#!/usr/bin/env python3
"""Run every governance test with bounded parallelism for remote-heavy cases."""

from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PACKAGE = "governance_tests"
HEAVY_MODULE = "governance_tests.test_freeze_git_remote"
MAX_HEAVY_WORKERS = 4
NON_HEAVY_TIMEOUT_SECONDS = 900
HEAVY_SELECTOR_TIMEOUT_SECONDS = 600
RUNNER_ID = "ids-governance-regression-v1"
RAN_PATTERN = re.compile(r"^Ran (?P<count>[0-9]+) tests? in ", re.MULTILINE)
_ACTIVE_PROCESSES: set[subprocess.Popen[str]] = set()
_ACTIVE_PROCESSES_LOCK = threading.Lock()


class InventoryError(RuntimeError):
    """Raised when the test inventory cannot be proved complete and unique."""


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def flatten_suite(suite: unittest.TestSuite) -> list[str]:
    selectors: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            selectors.extend(flatten_suite(item))
        else:
            selectors.append(item.id())
    return selectors


def module_names(project_root: Path, test_package: str) -> list[str]:
    package_path = project_root / Path(*test_package.split("."))
    if (
        not package_path.is_dir()
        or package_path.is_symlink()
        or not (package_path / "__init__.py").is_file()
    ):
        raise InventoryError("governance test package is missing or unsafe")
    names: list[str] = []
    for path in sorted(package_path.glob("test_*.py")):
        if path.is_symlink() or not path.is_file():
            raise InventoryError(f"test module is not a regular file: {path.name}")
        names.append(f"{test_package}.{path.stem}")
    if not names or len(names) != len(set(names)):
        raise InventoryError("governance test modules are empty or duplicated")
    return names


def load_selectors(
    names: list[str],
    *,
    project_root: Path,
) -> list[str]:
    root_text = str(project_root)
    inserted = not sys.path or sys.path[0] != root_text
    if inserted:
        sys.path.insert(0, root_text)
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromNames(names)
        if loader.errors:
            raise InventoryError(
                "test discovery errors: " + " | ".join(loader.errors)
            )
        selectors = flatten_suite(suite)
    finally:
        if inserted and sys.path and sys.path[0] == root_text:
            sys.path.pop(0)
    if not selectors or len(selectors) != len(set(selectors)):
        raise InventoryError("discovered test selectors are empty or duplicated")
    return selectors


def discover_inventory(
    *,
    project_root: Path,
    test_package: str,
    heavy_module: str,
) -> dict[str, Any]:
    modules = module_names(project_root, test_package)
    if modules.count(heavy_module) != 1:
        raise InventoryError("heavy governance module must exist exactly once")
    selectors = load_selectors(modules, project_root=project_root)
    heavy_selectors = sorted(
        selector
        for selector in selectors
        if selector.startswith(f"{heavy_module}.")
    )
    non_heavy_selectors = sorted(set(selectors) - set(heavy_selectors))
    non_heavy_modules = [name for name in modules if name != heavy_module]
    if not heavy_selectors or not non_heavy_selectors or not non_heavy_modules:
        raise InventoryError("governance test partition is empty")
    if len(non_heavy_selectors) + len(heavy_selectors) != len(selectors):
        raise InventoryError("governance test partition does not cover inventory")
    return {
        "modules": modules,
        "selectors": sorted(selectors),
        "non_heavy_modules": non_heavy_modules,
        "non_heavy_selectors": non_heavy_selectors,
        "heavy_selectors": heavy_selectors,
    }


def normalized_argv(argv: list[str]) -> list[str]:
    return ["PYTHON" if item == sys.executable else item for item in argv]


def terminate_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                return
        else:
            process.kill()
        process.wait()


def terminate_active_processes(
    _signum: int | None = None,
    _frame: object | None = None,
) -> None:
    with _ACTIVE_PROCESSES_LOCK:
        active = list(_ACTIVE_PROCESSES)
    for process in active:
        terminate_process(process)


def run_process(
    argv: list[str],
    *,
    cwd: Path,
    timeout_seconds: float,
    expected_test_count: int,
    label: str,
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    environment["TZ"] = "UTC"
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=(os.name == "posix"),
    )
    with _ACTIVE_PROCESSES_LOCK:
        _ACTIVE_PROCESSES.add(process)
    timed_out = False
    try:
        try:
            output, _ = process.communicate(timeout=timeout_seconds)
            process_exit = process.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_process(process)
            output, _ = process.communicate()
            process_exit = 124
    finally:
        with _ACTIVE_PROCESSES_LOCK:
            _ACTIVE_PROCESSES.discard(process)
    elapsed = time.monotonic() - started
    counts = [int(match.group("count")) for match in RAN_PATTERN.finditer(output)]
    observed_test_count = counts[0] if len(counts) == 1 else None
    clean_ok = len(re.findall(r"^OK$", output, re.MULTILINE)) == 1
    passed = (
        not timed_out
        and process_exit == 0
        and observed_test_count == expected_test_count
        and clean_ok
        and "FAILED (" not in output
    )
    return {
        "label": label,
        "argv": normalized_argv(argv),
        "expected_test_count": expected_test_count,
        "observed_test_count": observed_test_count,
        "actual_process_exit": process_exit,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_sha256": sha256_text(output),
        "stdout_tail": output[-4000:],
        "result": "pass" if passed else "fail",
    }


def run_regression(
    *,
    project_root: Path = PROJECT_ROOT,
    test_package: str = TEST_PACKAGE,
    heavy_module: str = HEAVY_MODULE,
    max_heavy_workers: int = MAX_HEAVY_WORKERS,
    non_heavy_timeout_seconds: float = NON_HEAVY_TIMEOUT_SECONDS,
    heavy_selector_timeout_seconds: float = HEAVY_SELECTOR_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    try:
        inventory = discover_inventory(
            project_root=project_root,
            test_package=test_package,
            heavy_module=heavy_module,
        )
    except InventoryError as exc:
        return {
            "schema_version": 1,
            "runner_id": RUNNER_ID,
            "status": "fail",
            "inventory_error": str(exc),
        }
    worker_count = min(max_heavy_workers, len(inventory["heavy_selectors"]))
    if worker_count < 1:
        return {
            "schema_version": 1,
            "runner_id": RUNNER_ID,
            "status": "fail",
            "inventory_error": "heavy worker count must be positive",
        }

    non_heavy = run_process(
        [
            sys.executable,
            "-m",
            "unittest",
            "-v",
            *inventory["non_heavy_modules"],
        ],
        cwd=project_root,
        timeout_seconds=non_heavy_timeout_seconds,
        expected_test_count=len(inventory["non_heavy_selectors"]),
        label="non_heavy_governance_modules",
    )
    heavy_results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="governance-regression",
    ) as executor:
        futures = {
            selector: executor.submit(
                run_process,
                [sys.executable, "-m", "unittest", "-v", selector],
                cwd=project_root,
                timeout_seconds=heavy_selector_timeout_seconds,
                expected_test_count=1,
                label=selector,
            )
            for selector in inventory["heavy_selectors"]
        }
        for selector in inventory["heavy_selectors"]:
            heavy_results.append(futures[selector].result())

    expected_total = len(inventory["selectors"])
    observed_counts = [
        non_heavy["observed_test_count"],
        *(result["observed_test_count"] for result in heavy_results),
    ]
    observed_total = (
        sum(observed_counts)
        if all(isinstance(value, int) for value in observed_counts)
        else None
    )
    all_passed = non_heavy["result"] == "pass" and all(
        result["result"] == "pass" for result in heavy_results
    )
    coverage_complete = (
        len(heavy_results) == len(inventory["heavy_selectors"])
        and len({item["label"] for item in heavy_results})
        == len(inventory["heavy_selectors"])
        and observed_total == expected_total
    )
    inventory_digest = hashlib.sha256(
        canonical_json(inventory["selectors"])
    ).hexdigest()
    return {
        "schema_version": 1,
        "runner_id": RUNNER_ID,
        "status": "pass" if all_passed and coverage_complete else "fail",
        "worker_count": worker_count,
        "inventory": {
            "module_count": len(inventory["modules"]),
            "expected_test_count": expected_total,
            "non_heavy_test_count": len(inventory["non_heavy_selectors"]),
            "heavy_test_count": len(inventory["heavy_selectors"]),
            "selector_inventory_sha256": inventory_digest,
            "heavy_selectors": inventory["heavy_selectors"],
        },
        "non_heavy_result": non_heavy,
        "heavy_results": heavy_results,
        "observed_test_count": observed_total,
        "coverage_complete": coverage_complete,
    }


def main() -> int:
    if os.name == "posix":
        signal.signal(signal.SIGTERM, terminate_active_processes)
        signal.signal(signal.SIGINT, terminate_active_processes)
    payload = run_regression()
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
