from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_RELATIVE = Path("scripts/verify_frozen_tests.py")
MANIFEST_RELATIVE = Path("governance/FROZEN_TEST_MANIFEST_V1.json")
PROJECT_METHOD_RELATIVE = Path("governance_tests/test_project_method.py")
ASSURANCE_RUNNER_RELATIVE = Path("governance_tests/test_assurance_runner.py")
RUN_ASSURANCE_RELATIVE = Path("scripts/run_assurance_ci.py")
PROJECT_METHOD_CLASS = "ProjectMethodPolicyTests"
PROJECT_METHOD_TEST = "test_frozen_test_baseline_bypass_is_rejected"
ASSURANCE_RUNNER_CLASS = "AssuranceRunnerTests"
ASSURANCE_RUNNER_TEST = "test_timeout_fails_closed_and_preserves_partial_output"
MUTABLE_FILES = (
    MANIFEST_RELATIVE,
    PROJECT_METHOD_RELATIVE,
    ASSURANCE_RUNNER_RELATIVE,
    RUN_ASSURANCE_RELATIVE,
)


class FrozenTestIntegrityMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls._temporary.name) / "isolated-project"
        shutil.copytree(
            SOURCE_ROOT,
            cls.root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                "*.pyc",
                ".ruff_cache",
                ".DS_Store",
            ),
        )
        git_init = subprocess.run(
            ["git", "init", "--quiet", str(cls.root)],
            check=False,
            capture_output=True,
            text=True,
        )
        if git_init.returncode != 0:
            raise AssertionError(
                "cannot initialize isolated Git fixture:\n"
                f"{git_init.stdout}{git_init.stderr}"
            )
        cls.verifier = cls.root / VERIFIER_RELATIVE
        cls.original_bytes = {
            relative: (cls.root / relative).read_bytes() for relative in MUTABLE_FILES
        }
        cls.baseline_result, cls.baseline_payload = cls.run_verifier()
        if cls.baseline_result.returncode != 0:
            raise AssertionError(
                "unmodified isolated frozen-test baseline must pass before "
                f"mutations:\n{cls.baseline_result.stdout}"
            )
        if cls.baseline_payload.get("status") != "pass":
            raise AssertionError(cls.baseline_payload)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()
        super().tearDownClass()

    def setUp(self) -> None:
        for relative, content in self.original_bytes.items():
            (self.root / relative).write_bytes(content)

    def tearDown(self) -> None:
        for relative, content in self.original_bytes.items():
            (self.root / relative).write_bytes(content)

    @classmethod
    def run_verifier(
        cls,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                str(cls.verifier),
                "--root",
                str(cls.root),
                "--json",
            ],
            cwd=cls.root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                "frozen-test verifier did not emit one JSON receipt: "
                f"{exc}\nstdout={completed.stdout}\nstderr={completed.stderr}"
            ) from exc
        if not isinstance(payload, dict):
            raise AssertionError(f"verifier receipt is not an object: {payload!r}")
        return completed, payload

    def read_json(self, relative: Path) -> dict[str, Any]:
        value = json.loads((self.root / relative).read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def write_json(self, relative: Path, value: dict[str, Any]) -> None:
        (self.root / relative).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def assert_static_rejection(self, expected_error: str) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(1, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual("fail", payload.get("status"), payload)
        self.assertEqual(
            "not_run",
            payload.get("baseline", {}).get("status"),
            payload,
        )
        self.assertTrue(
            any(expected_error in error for error in payload.get("errors", [])),
            payload,
        )
        return payload

    def assert_baseline_rejection(self, expected_error: str) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(1, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual("fail", payload.get("status"), payload)
        self.assertEqual("fail", payload.get("baseline", {}).get("status"), payload)
        self.assertTrue(
            any(expected_error in error for error in payload.get("errors", [])),
            payload,
        )
        return payload

    def method_node(
        self,
        relative: Path,
        class_name: str,
        test_name: str,
    ) -> ast.FunctionDef:
        source = (self.root / relative).read_text(encoding="utf-8")
        module = ast.parse(source, filename=relative.as_posix(), type_comments=True)
        classes = [
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ]
        self.assertEqual(1, len(classes))
        methods = [
            node
            for node in classes[0].body
            if isinstance(node, ast.FunctionDef) and node.name == test_name
        ]
        self.assertEqual(1, len(methods))
        return methods[0]

    def delete_method(
        self,
        relative: Path,
        class_name: str,
        test_name: str,
    ) -> None:
        path = self.root / relative
        method = self.method_node(relative, class_name, test_name)
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        del lines[method.lineno - 1 : method.end_lineno]
        path.write_text("".join(lines), encoding="utf-8")

    def insert_method_decorator(self, decorator: str) -> None:
        path = self.root / PROJECT_METHOD_RELATIVE
        method = self.method_node(
            PROJECT_METHOD_RELATIVE,
            PROJECT_METHOD_CLASS,
            PROJECT_METHOD_TEST,
        )
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        indent = " " * method.col_offset
        lines.insert(method.lineno - 1, f"{indent}@{decorator}\n")
        path.write_text("".join(lines), encoding="utf-8")

    def replace_once(self, relative: Path, old: str, new: str) -> None:
        path = self.root / relative
        source = path.read_text(encoding="utf-8")
        self.assertEqual(1, source.count(old), old)
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

    def test_unmodified_isolated_baseline_executes_every_selector(self) -> None:
        manifest = self.read_json(MANIFEST_RELATIVE)
        expected_selector_count = len(manifest["tests"])
        self.assertGreater(expected_selector_count, 0)
        self.assertEqual(
            0, self.baseline_result.returncode, self.baseline_result.stdout
        )
        self.assertEqual("pass", self.baseline_payload["status"])
        self.assertEqual(
            expected_selector_count,
            self.baseline_payload["selectors_checked"],
        )
        baseline = self.baseline_payload["baseline"]
        self.assertEqual("pass", baseline["status"])
        self.assertEqual(expected_selector_count, baseline["tests_run"])
        for field in (
            "failures",
            "errors",
            "skipped",
            "expected_failures",
            "unexpected_successes",
        ):
            self.assertEqual(0, baseline[field], field)
        self.assertEqual(
            [1] * expected_selector_count,
            [item["count"] for item in baseline["loaded_counts"]],
        )

    def test_duplicate_manifest_key_is_rejected_as_non_strict_json(self) -> None:
        path = self.root / MANIFEST_RELATIVE
        source = path.read_text(encoding="utf-8")
        path.write_text(
            source.replace(
                '"schema_version": 1,',
                '"schema_version": 1,\n  "schema_version": 1,',
                1,
            ),
            encoding="utf-8",
        )
        self.assert_static_rejection("duplicate object key: schema_version")

    def test_real_baseline_execution_rejects_broken_transitive_behavior(self) -> None:
        self.replace_once(
            RUN_ASSURANCE_RELATIVE,
            '        "timed_out": timed_out,\n'
            '        "actual_process_exit": process_exit,\n'
            '        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),\n',
            '        "timed_out": timed_out,\n'
            '        "actual_process_exit": 0,\n'
            '        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),\n',
        )
        payload = self.assert_baseline_rejection(
            "frozen-test baseline failures differs"
        )
        expected_selector_count = len(self.read_json(MANIFEST_RELATIVE)["tests"])
        self.assertEqual(
            expected_selector_count,
            payload["baseline"]["tests_run"],
        )
        self.assertEqual(1, payload["baseline"]["failures"])

    def test_manifest_cannot_drop_selector_and_lower_claimed_test_count(self) -> None:
        manifest = self.read_json(MANIFEST_RELATIVE)
        manifest["tests"].pop()
        manifest["baseline"]["expected"]["tests_run"] = len(manifest["tests"])
        self.write_json(MANIFEST_RELATIVE, manifest)
        payload = self.assert_static_rejection(
            "frozen-test selector identities or order differ"
        )
        self.assertTrue(
            any(
                "frozen-test baseline tests_run differs" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_deleted_frozen_method_is_rejected(self) -> None:
        self.delete_method(
            PROJECT_METHOD_RELATIVE,
            PROJECT_METHOD_CLASS,
            PROJECT_METHOD_TEST,
        )
        self.assert_static_rejection(
            "missing, renamed, or duplicate exact frozen-test method"
        )

    def test_renamed_frozen_method_is_rejected(self) -> None:
        self.replace_once(
            PROJECT_METHOD_RELATIVE,
            f"def {PROJECT_METHOD_TEST}(self)",
            f"def {PROJECT_METHOD_TEST}_renamed(self)",
        )
        self.assert_static_rejection(
            "missing, renamed, or duplicate exact frozen-test method"
        )

    def test_unittest_skip_decorator_is_rejected(self) -> None:
        self.insert_method_decorator('unittest.skip("mutation")')
        self.assert_static_rejection(
            "forbidden test-disable mechanism on frozen-test method"
        )

    def test_unittest_expected_failure_decorator_is_rejected(self) -> None:
        self.insert_method_decorator("unittest.expectedFailure")
        self.assert_static_rejection(
            "forbidden test-disable mechanism on frozen-test method"
        )

    def test_pytest_xfail_decorator_is_rejected_without_trusting_pytest(self) -> None:
        self.insert_method_decorator('pytest.mark.xfail(reason="mutation")')
        payload = self.assert_static_rejection(
            "forbidden test-disable mechanism on frozen-test method"
        )
        self.assertTrue(
            any("pytest.mark.xfail" in error for error in payload["errors"]),
            payload,
        )

    def test_assertion_deletion_is_rejected(self) -> None:
        self.replace_once(
            ASSURANCE_RUNNER_RELATIVE,
            '            self.assertEqual(receipt["result"], "fail")\n'
            '            self.assertEqual(receipt["actual_process_exit"], 124)\n',
            '            self.assertEqual(receipt["actual_process_exit"], 124)\n',
        )
        self.assert_static_rejection("assertion count mismatch for frozen-test method")

    def test_assertion_weakening_is_rejected(self) -> None:
        self.replace_once(
            ASSURANCE_RUNNER_RELATIVE,
            'self.assertEqual(receipt["actual_process_exit"], 124)',
            'self.assertNotEqual(receipt["actual_process_exit"], 0)',
        )
        self.assert_static_rejection(
            "assertion AST sha256 mismatch for frozen-test method"
        )

    def test_failed_assertion_replaced_by_always_pass_is_rejected(self) -> None:
        self.replace_once(
            ASSURANCE_RUNNER_RELATIVE,
            'self.assertEqual(receipt["actual_process_exit"], 124)',
            "self.assertTrue(True)",
        )
        payload = self.assert_static_rejection(
            "literal or structural always-pass assertion"
        )
        self.assertTrue(
            any(
                "assertion AST sha256 mismatch" in error for error in payload["errors"]
            ),
            payload,
        )


if __name__ == "__main__":
    unittest.main()
