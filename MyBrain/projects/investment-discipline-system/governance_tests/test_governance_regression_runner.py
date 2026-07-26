from __future__ import annotations

import copy
import tempfile
import time
import unittest
import uuid
from pathlib import Path

from scripts import run_governance_regression


class GovernanceRegressionRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.package = f"fixture_tests_{uuid.uuid4().hex}"
        self.package_root = self.root / self.package
        self.package_root.mkdir()
        self.heavy_module = f"{self.package}.test_heavy"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_test(self, filename: str, source: str) -> Path:
        path = self.package_root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    def write_fast_pass(self) -> None:
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n",
        )

    def run_fixture(
        self,
        *,
        heavy_timeout: float = 10,
        total_timeout: float = 30,
    ) -> dict:
        return run_governance_regression.run_regression(
            project_root=self.root,
            test_package=self.package,
            heavy_module=self.heavy_module,
            max_heavy_workers=2,
            non_heavy_timeout_seconds=10,
            heavy_selector_timeout_seconds=heavy_timeout,
            total_timeout_seconds=total_timeout,
        )

    def valid_worker_receipt(self, test_ids: list[str]) -> dict:
        return {
            "schema_version": 1,
            "runner_id": run_governance_regression.WORKER_RUNNER_ID,
            "runner_sha256": "a" * 64,
            "status": "pass",
            "request_kind": "selector",
            "requested_names": test_ids,
            "loaded_test_ids": test_ids,
            "started_test_ids": test_ids,
            "successful_test_ids": test_ids,
            "tests_run": len(test_ids),
            "failures": [],
            "errors": [],
            "skipped_test_ids": [],
            "expected_failure_test_ids": [],
            "unexpected_success_test_ids": [],
            "source_fingerprint_before": "b" * 64,
            "source_fingerprint_after": "b" * 64,
            "exact_execution": True,
            "captured_output_sha256": "c" * 64,
            "captured_output_bytes": 0,
        }

    def validate_fixture_receipt(
        self,
        receipt: dict,
        expected_ids: list[str],
    ) -> bool:
        return run_governance_regression.validate_worker_receipt(
            receipt,
            expected_test_ids=expected_ids,
            request_kind="selector",
            requested_names=expected_ids,
            worker_sha256="a" * 64,
            source_fingerprint="b" * 64,
        )

    def test_namespace_package_and_recursive_test_pattern_are_complete(self) -> None:
        self.assertFalse((self.package_root / "__init__.py").exists())
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_one(self): self.assertTrue(True)\n"
            "    def test_two(self): self.assertEqual(2, 2)\n",
        )
        self.write_test(
            "nested/test_child.py",
            "import unittest\n"
            "class Child(unittest.TestCase):\n"
            "    def test_nested(self): self.assertTrue(True)\n",
        )
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_one(self): self.assertTrue(True)\n"
            "    def test_two(self): self.assertEqual(2, 2)\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "pass", payload)
        self.assertTrue(payload["coverage_complete"])
        self.assertEqual(len(payload["discovered_test_ids"]), 5)
        self.assertEqual(
            payload["discovered_test_ids"],
            sorted(payload["discovered_test_ids"]),
        )
        self.assertCountEqual(
            payload["discovered_test_ids"],
            payload["loaded_test_ids"],
        )
        self.assertCountEqual(
            payload["discovered_test_ids"],
            payload["started_test_ids"],
        )
        self.assertCountEqual(
            payload["discovered_test_ids"],
            payload["successful_test_ids"],
        )
        self.assertEqual(len(payload["heavy_workers"]), 2)
        self.assertEqual(payload["active_process_count_after"], 0)
        self.assertTrue(payload["all_temporary_roots_removed"])

    def test_test_stdout_is_captured_without_corrupting_worker_json(self) -> None:
        self.write_test(
            "test_fast.py",
            "import sys\n"
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_noisy(self):\n"
            "        print('python stdout noise')\n"
            "        print('python stderr noise', file=sys.stderr)\n"
            "        self.assertTrue(True)\n",
        )
        self.write_test(
            "test_heavy.py",
            "import os\n"
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_fd_noise(self):\n"
            "        os.write(1, b'fd stdout noise\\n')\n"
            "        os.write(2, b'fd stderr noise\\n')\n"
            "        self.assertTrue(True)\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "pass", payload)
        receipts = [
            payload["non_heavy_worker"]["worker_receipt"],
            *[
                worker["worker_receipt"]
                for worker in payload["heavy_workers"]
            ],
        ]
        self.assertTrue(
            all(receipt["captured_output_bytes"] > 0 for receipt in receipts)
        )

    def test_duplicate_substitution_cannot_fake_exact_execution(self) -> None:
        expected = ["fixture.Case.test_a", "fixture.Case.test_b"]
        receipt = self.valid_worker_receipt(expected)
        receipt["loaded_test_ids"] = [expected[0], expected[0]]
        receipt["started_test_ids"] = [expected[0], expected[0]]
        receipt["successful_test_ids"] = [expected[0], expected[0]]
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))

    def test_missing_selector_cannot_fake_exact_execution(self) -> None:
        expected = ["fixture.Case.test_a", "fixture.Case.test_b"]
        receipt = self.valid_worker_receipt(expected)
        receipt["loaded_test_ids"] = expected[:1]
        receipt["started_test_ids"] = expected[:1]
        receipt["successful_test_ids"] = expected[:1]
        receipt["tests_run"] = 1
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))

    def test_malformed_worker_receipt_fails_closed_without_exception(self) -> None:
        expected = ["fixture.Case.test_a"]
        receipt = self.valid_worker_receipt(expected)
        receipt["loaded_test_ids"] = None
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))
        with self.assertRaisesRegex(
            run_governance_regression.DuplicateKeyError,
            "duplicate JSON key",
        ):
            run_governance_regression.strict_json_object('{"a":1,"a":2}')

    def test_failing_heavy_selector_fails_the_whole_run(self) -> None:
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_failure(self): self.fail('fixture failure')\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["heavy_workers"][0]["result"], "fail")
        self.assertEqual(
            payload["heavy_workers"][0]["actual_process_exit"],
            1,
        )

    def test_skip_is_not_treated_as_execution_success(self) -> None:
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    @unittest.skip('fixture skip')\n"
            "    def test_skip(self): pass\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        receipt = payload["heavy_workers"][0]["worker_receipt"]
        self.assertEqual(len(receipt["skipped_test_ids"]), 1)

    def test_expected_failure_is_not_treated_as_execution_success(self) -> None:
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    @unittest.expectedFailure\n"
            "    def test_expected(self): self.fail('expected fixture failure')\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        receipt = payload["heavy_workers"][0]["worker_receipt"]
        self.assertEqual(len(receipt["expected_failure_test_ids"]), 1)

    def test_source_mutation_during_test_fails_closed(self) -> None:
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import pathlib\n"
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_mutate(self):\n"
            "        path = pathlib.Path(__file__)\n"
            "        path.write_text(path.read_text() + '\\n# mutation\\n')\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        receipt = payload["heavy_workers"][0]["worker_receipt"]
        self.assertNotEqual(
            receipt["source_fingerprint_before"],
            receipt["source_fingerprint_after"],
        )

    def test_timed_out_selector_kills_grandchild_and_removes_temp_root(
        self,
    ) -> None:
        marker = self.root / "grandchild-survived.txt"
        child = (
            "import time\n"
            "from pathlib import Path\n"
            "time.sleep(0.7)\n"
            f"Path({str(marker)!r}).write_text('survived')\n"
        )
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import subprocess\n"
            "import sys\n"
            "import time\n"
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_slow(self):\n"
            f"        subprocess.Popen([sys.executable, '-c', {child!r}])\n"
            "        time.sleep(5)\n",
        )
        payload = self.run_fixture(heavy_timeout=0.1)
        worker = payload["heavy_workers"][0]
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(worker["timed_out"])
        self.assertEqual(worker["actual_process_exit"], 124)
        self.assertTrue(worker["temporary_root_removed"])
        time.sleep(1)
        self.assertFalse(marker.exists())

    def test_loader_error_fails_before_execution(self) -> None:
        self.write_fast_pass()
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n",
        )
        self.write_test("test_broken.py", "this is not valid python !!!\n")
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        self.assertIn("test discovery raised SyntaxError", payload["inventory_error"])

    def test_missing_heavy_module_fails_before_execution(self) -> None:
        self.write_fast_pass()
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        self.assertIn("must exist exactly once", payload["inventory_error"])

    def test_worker_receipt_rejects_non_boolean_exact_execution(self) -> None:
        expected = ["fixture.Case.test_a"]
        receipt = copy.deepcopy(self.valid_worker_receipt(expected))
        receipt["exact_execution"] = 1
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))

    def test_worker_receipt_rejects_invalid_captured_output_metadata(self) -> None:
        expected = ["fixture.Case.test_a"]
        receipt = copy.deepcopy(self.valid_worker_receipt(expected))
        receipt["captured_output_sha256"] = "not-a-digest"
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))
        receipt = copy.deepcopy(self.valid_worker_receipt(expected))
        receipt["captured_output_bytes"] = True
        self.assertFalse(self.validate_fixture_receipt(receipt, expected))


if __name__ == "__main__":
    unittest.main()
