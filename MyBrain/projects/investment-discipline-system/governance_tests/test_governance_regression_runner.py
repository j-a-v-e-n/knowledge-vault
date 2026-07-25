from __future__ import annotations

import sys
import tempfile
import unittest
import uuid
from pathlib import Path

from scripts import run_governance_regression


class GovernanceRegressionRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.package = f"fixture_tests_{uuid.uuid4().hex}"
        package_root = self.root / self.package
        package_root.mkdir()
        (package_root / "__init__.py").write_text("", encoding="utf-8")
        self.heavy_module = f"{self.package}.test_heavy"

    def tearDown(self) -> None:
        prefix = f"{self.package}."
        for name in list(sys.modules):
            if name == self.package or name.startswith(prefix):
                sys.modules.pop(name, None)
        self.temp.cleanup()

    def write_test(self, filename: str, source: str) -> None:
        (self.root / self.package / filename).write_text(
            source,
            encoding="utf-8",
        )

    def run_fixture(
        self,
        *,
        heavy_timeout: float = 10,
    ) -> dict:
        return run_governance_regression.run_regression(
            project_root=self.root,
            test_package=self.package,
            heavy_module=self.heavy_module,
            max_heavy_workers=2,
            non_heavy_timeout_seconds=10,
            heavy_selector_timeout_seconds=heavy_timeout,
        )

    def test_every_discovered_selector_runs_exactly_once(self) -> None:
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_one(self): self.assertTrue(True)\n"
            "    def test_two(self): self.assertEqual(2, 2)\n",
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
        self.assertEqual(payload["inventory"]["expected_test_count"], 4)
        self.assertEqual(payload["observed_test_count"], 4)
        self.assertEqual(len(payload["heavy_results"]), 2)
        self.assertEqual(
            len({item["label"] for item in payload["heavy_results"]}),
            2,
        )

    def test_failing_heavy_selector_fails_the_whole_run(self) -> None:
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n",
        )
        self.write_test(
            "test_heavy.py",
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_failure(self): self.fail('expected fixture failure')\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["heavy_results"][0]["result"], "fail")
        self.assertEqual(
            payload["heavy_results"][0]["observed_test_count"],
            1,
        )

    def test_timed_out_selector_fails_closed(self) -> None:
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n",
        )
        self.write_test(
            "test_heavy.py",
            "import time\n"
            "import unittest\n"
            "class Heavy(unittest.TestCase):\n"
            "    def test_slow(self): time.sleep(2)\n",
        )
        payload = self.run_fixture(heavy_timeout=0.1)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(payload["heavy_results"][0]["timed_out"])
        self.assertEqual(
            payload["heavy_results"][0]["actual_process_exit"],
            124,
        )

    def test_missing_heavy_module_fails_before_execution(self) -> None:
        self.write_test(
            "test_fast.py",
            "import unittest\n"
            "class Fast(unittest.TestCase):\n"
            "    def test_ok(self): self.assertTrue(True)\n",
        )
        payload = self.run_fixture()
        self.assertEqual(payload["status"], "fail")
        self.assertIn("must exist exactly once", payload["inventory_error"])


if __name__ == "__main__":
    unittest.main()
