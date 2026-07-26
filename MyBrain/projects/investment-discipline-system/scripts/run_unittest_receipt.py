#!/usr/bin/env python3
"""Run an explicit unittest slice and emit one machine-checkable JSON receipt."""

from __future__ import annotations

import argparse
import collections
import fnmatch
import hashlib
import json
import os
import sys
import tempfile
import traceback
import unittest
from pathlib import Path
from typing import Any


RUNNER_ID = "ids-unittest-receipt-v1"


class ReceiptError(RuntimeError):
    """Raised when the requested test scope cannot be loaded safely."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def strict_package_root(project_root: Path, test_package: str) -> Path:
    if (
        not test_package
        or any(
            not part
            or not all(character.isalnum() or character == "_" for character in part)
            for part in test_package.split(".")
        )
    ):
        raise ReceiptError("test package name is unsafe")
    package_root = project_root.joinpath(*test_package.split("."))
    try:
        resolved = package_root.resolve(strict=True)
    except OSError as exc:
        raise ReceiptError(f"test package cannot be resolved: {exc}") from exc
    if resolved != package_root or not resolved.is_dir() or resolved.is_symlink():
        raise ReceiptError("test package must be one regular directory")
    return resolved


def test_source_inventory(
    project_root: Path,
    test_package: str,
) -> list[dict[str, str]]:
    package_root = strict_package_root(project_root, test_package)
    inventory: list[dict[str, str]] = []
    for directory, directory_names, filenames in os.walk(
        package_root,
        followlinks=False,
    ):
        directory_path = Path(directory)
        for name in list(directory_names):
            candidate = directory_path / name
            if candidate.is_symlink():
                raise ReceiptError(
                    f"test source directory symlink is forbidden: {candidate}"
                )
            if name == "__pycache__":
                directory_names.remove(name)
        for filename in filenames:
            if not fnmatch.fnmatchcase(filename, "test*.py"):
                continue
            path = directory_path / filename
            if path.is_symlink() or not path.is_file():
                raise ReceiptError(
                    f"test source must be one regular file: {path}"
                )
            relative = path.relative_to(project_root).as_posix()
            inventory.append(
                {
                    "path": relative,
                    "sha256": sha256_bytes(path.read_bytes()),
                }
            )
    inventory.sort(key=lambda item: item["path"])
    if not inventory:
        raise ReceiptError("test source inventory is empty")
    return inventory


def test_source_fingerprint(
    project_root: Path,
    test_package: str,
) -> str:
    return sha256_bytes(
        canonical_json(test_source_inventory(project_root, test_package))
    )


def flatten_suite(suite: unittest.TestSuite) -> list[str]:
    selectors: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            selectors.extend(flatten_suite(item))
        else:
            selectors.append(item.id())
    return selectors


def load_suite(
    names: list[str],
    *,
    project_root: Path,
) -> tuple[unittest.TestSuite, list[str]]:
    root_text = str(project_root)
    inserted = not sys.path or sys.path[0] != root_text
    if inserted:
        sys.path.insert(0, root_text)
    try:
        loader = unittest.TestLoader()
        try:
            suite = loader.loadTestsFromNames(names)
        except Exception as exc:
            raise ReceiptError(
                f"test loader raised {type(exc).__name__}: {exc}"
            ) from exc
        if loader.errors:
            raise ReceiptError(
                "test loader errors: " + " | ".join(loader.errors)
            )
        selectors = flatten_suite(suite)
    finally:
        if inserted and sys.path and sys.path[0] == root_text:
            sys.path.pop(0)
    if not selectors:
        raise ReceiptError("loaded test selector inventory is empty")
    selector_counts = collections.Counter(selectors)
    if any(count != 1 for count in selector_counts.values()):
        raise ReceiptError("loaded test selectors are duplicated")
    return suite, selectors


def diagnostic(test: unittest.case.TestCase, error: tuple) -> dict[str, str]:
    rendered = "".join(traceback.format_exception(*error))
    return {
        "test_id": test.id(),
        "traceback_sha256": sha256_bytes(rendered.encode("utf-8")),
        "traceback_tail": rendered[-4000:],
    }


class RecordingResult(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.started_test_ids: list[str] = []
        self.successful_test_ids: list[str] = []
        self.failure_diagnostics: list[dict[str, str]] = []
        self.error_diagnostics: list[dict[str, str]] = []
        self.skipped_test_ids: list[str] = []
        self.expected_failure_test_ids: list[str] = []
        self.unexpected_success_test_ids: list[str] = []

    def startTest(self, test: unittest.case.TestCase) -> None:
        self.started_test_ids.append(test.id())
        super().startTest(test)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        self.successful_test_ids.append(test.id())
        super().addSuccess(test)

    def addFailure(self, test: unittest.case.TestCase, err: tuple) -> None:
        self.failure_diagnostics.append(diagnostic(test, err))
        super().addFailure(test, err)

    def addError(self, test: unittest.case.TestCase, err: tuple) -> None:
        self.error_diagnostics.append(diagnostic(test, err))
        super().addError(test, err)

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        self.skipped_test_ids.append(test.id())
        super().addSkip(test, reason)

    def addExpectedFailure(
        self,
        test: unittest.case.TestCase,
        err: tuple,
    ) -> None:
        self.expected_failure_test_ids.append(test.id())
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:
        self.unexpected_success_test_ids.append(test.id())
        super().addUnexpectedSuccess(test)


def run_with_captured_process_output(
    suite: unittest.TestSuite,
    result: RecordingResult,
) -> bytes:
    """Run tests while keeping worker stdout as one unambiguous JSON object."""
    sys.stdout.flush()
    sys.stderr.flush()
    saved_stdout = os.dup(1)
    saved_stderr = os.dup(2)
    try:
        with tempfile.TemporaryFile(mode="w+b") as capture:
            os.dup2(capture.fileno(), 1)
            os.dup2(capture.fileno(), 2)
            try:
                suite.run(result)
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
                os.dup2(saved_stdout, 1)
                os.dup2(saved_stderr, 2)
            capture.seek(0)
            return capture.read()
    finally:
        os.close(saved_stdout)
        os.close(saved_stderr)


def execute(
    *,
    project_root: Path,
    test_package: str,
    names: list[str],
    request_kind: str,
) -> dict[str, Any]:
    source_before = test_source_fingerprint(project_root, test_package)
    suite, loaded = load_suite(names, project_root=project_root)
    result = RecordingResult()
    captured_output = run_with_captured_process_output(suite, result)
    source_after = test_source_fingerprint(project_root, test_package)
    loaded_counts = collections.Counter(loaded)
    started_counts = collections.Counter(result.started_test_ids)
    successful_counts = collections.Counter(result.successful_test_ids)
    exact_execution = (
        loaded_counts == started_counts == successful_counts
        and all(count == 1 for count in loaded_counts.values())
    )
    passed = (
        exact_execution
        and result.testsRun == len(loaded)
        and not result.failure_diagnostics
        and not result.error_diagnostics
        and not result.skipped_test_ids
        and not result.expected_failure_test_ids
        and not result.unexpected_success_test_ids
        and source_before == source_after
    )
    return {
        "schema_version": 1,
        "runner_id": RUNNER_ID,
        "runner_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "status": "pass" if passed else "fail",
        "request_kind": request_kind,
        "requested_names": names,
        "loaded_test_ids": loaded,
        "started_test_ids": result.started_test_ids,
        "successful_test_ids": result.successful_test_ids,
        "tests_run": result.testsRun,
        "failures": result.failure_diagnostics,
        "errors": result.error_diagnostics,
        "skipped_test_ids": result.skipped_test_ids,
        "expected_failure_test_ids": result.expected_failure_test_ids,
        "unexpected_success_test_ids": result.unexpected_success_test_ids,
        "source_fingerprint_before": source_before,
        "source_fingerprint_after": source_after,
        "exact_execution": exact_execution,
        "captured_output_sha256": sha256_bytes(captured_output),
        "captured_output_bytes": len(captured_output),
    }


def failure_receipt(message: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "runner_id": RUNNER_ID,
        "runner_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "status": "fail",
        "setup_error": message,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--test-package", required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--module", action="append")
    group.add_argument("--selector", action="append")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        project_root = args.project_root.resolve(strict=True)
        if not project_root.is_dir():
            raise ReceiptError("project root must be a directory")
        names = args.module if args.module is not None else args.selector
        request_kind = "module" if args.module is not None else "selector"
        payload = execute(
            project_root=project_root,
            test_package=args.test_package,
            names=names,
            request_kind=request_kind,
        )
    except (
        OSError,
        ReceiptError,
        RuntimeError,
        ValueError,
    ) as exc:
        payload = failure_receipt(f"{type(exc).__name__}: {exc}")
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
