#!/usr/bin/env python3
"""Run the complete governance unittest universe with bounded parallelism."""

from __future__ import annotations

import collections
import concurrent.futures
import fnmatch
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_PACKAGE = "governance_tests"
HEAVY_MODULE = "governance_tests.test_freeze_git_remote"
WORKER_SCRIPT = PROJECT_ROOT / "scripts" / "run_unittest_receipt.py"
MAX_HEAVY_WORKERS = 2
NON_HEAVY_TIMEOUT_SECONDS = 900
HEAVY_SELECTOR_TIMEOUT_SECONDS = 600
TOTAL_TIMEOUT_SECONDS = 1320
RUNNER_ID = "ids-governance-regression-v2"
WORKER_RUNNER_ID = "ids-unittest-receipt-v1"
_ACTIVE_PROCESSES: set[subprocess.Popen[str]] = set()
_ACTIVE_PROCESSES_LOCK = threading.Lock()
_SHUTDOWN_EVENT = threading.Event()


class InventoryError(RuntimeError):
    """Raised when the test inventory cannot be proved complete and unique."""


class DuplicateKeyError(ValueError):
    """Raised when a worker receipt contains duplicate JSON keys."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def strict_json_object(raw: str) -> dict[str, Any]:
    value = json.loads(
        raw,
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("worker receipt must be a JSON object")
    return value


def safe_dotted_name(value: str) -> bool:
    return bool(value) and all(
        part
        and part.isidentifier()
        and not part.startswith("_")
        for part in value.split(".")
    )


def strict_package_root(project_root: Path, test_package: str) -> Path:
    if not safe_dotted_name(test_package):
        raise InventoryError("test package name is unsafe")
    package_root = project_root.joinpath(*test_package.split("."))
    try:
        resolved = package_root.resolve(strict=True)
    except OSError as exc:
        raise InventoryError(f"test package cannot be resolved: {exc}") from exc
    if resolved != package_root or not resolved.is_dir() or resolved.is_symlink():
        raise InventoryError("test package must be one regular directory")
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
                raise InventoryError(
                    f"test source directory symlink is forbidden: {candidate}"
                )
            if name == "__pycache__":
                directory_names.remove(name)
        for filename in filenames:
            if not fnmatch.fnmatchcase(filename, "test*.py"):
                continue
            path = directory_path / filename
            if path.is_symlink() or not path.is_file():
                raise InventoryError(
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
        raise InventoryError("governance test source inventory is empty")
    return inventory


def test_source_fingerprint(
    project_root: Path,
    test_package: str,
) -> str:
    return sha256_bytes(
        canonical_json(test_source_inventory(project_root, test_package))
    )


def module_names(
    project_root: Path,
    test_package: str,
) -> list[str]:
    package_root = strict_package_root(project_root, test_package)
    modules: list[str] = []
    for item in test_source_inventory(project_root, test_package):
        relative = (
            project_root / item["path"]
        ).relative_to(package_root).with_suffix("")
        modules.append(
            ".".join([test_package, *relative.parts])
        )
    if len(modules) != len(set(modules)):
        raise InventoryError("governance test modules are duplicated")
    return modules


def flatten_suite(suite: unittest.TestSuite) -> list[str]:
    selectors: list[str] = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            selectors.extend(flatten_suite(item))
        else:
            selectors.append(item.id())
    return selectors


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
        try:
            suite = loader.loadTestsFromNames(names)
        except Exception as exc:
            raise InventoryError(
                f"test discovery raised {type(exc).__name__}: {exc}"
            ) from exc
        if loader.errors:
            raise InventoryError(
                "test discovery errors: " + " | ".join(loader.errors)
            )
        selectors = flatten_suite(suite)
    finally:
        if inserted and sys.path and sys.path[0] == root_text:
            sys.path.pop(0)
    counts = collections.Counter(selectors)
    if not selectors or any(count != 1 for count in counts.values()):
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
    selectors = sorted(load_selectors(modules, project_root=project_root))
    heavy_selectors = [
        selector
        for selector in selectors
        if selector.startswith(f"{heavy_module}.")
    ]
    non_heavy_selectors = [
        selector
        for selector in selectors
        if not selector.startswith(f"{heavy_module}.")
    ]
    non_heavy_modules = [name for name in modules if name != heavy_module]
    planned = [*non_heavy_selectors, *heavy_selectors]
    if (
        not heavy_selectors
        or not non_heavy_selectors
        or not non_heavy_modules
        or collections.Counter(planned) != collections.Counter(selectors)
    ):
        raise InventoryError("governance test partition is incomplete")
    return {
        "modules": modules,
        "selectors": selectors,
        "non_heavy_modules": non_heavy_modules,
        "non_heavy_selectors": non_heavy_selectors,
        "heavy_selectors": heavy_selectors,
    }


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


def terminate_active_processes() -> None:
    with _ACTIVE_PROCESSES_LOCK:
        active = list(_ACTIVE_PROCESSES)
    for process in active:
        terminate_process(process)


def signal_shutdown(signum: int, _frame: object | None) -> None:
    _SHUTDOWN_EVENT.set()
    terminate_active_processes()
    raise SystemExit(128 + signum)


WORKER_RECEIPT_FIELDS = {
    "schema_version",
    "runner_id",
    "runner_sha256",
    "status",
    "request_kind",
    "requested_names",
    "loaded_test_ids",
    "started_test_ids",
    "successful_test_ids",
    "tests_run",
    "failures",
    "errors",
    "skipped_test_ids",
    "expected_failure_test_ids",
    "unexpected_success_test_ids",
    "source_fingerprint_before",
    "source_fingerprint_after",
    "exact_execution",
}


def validate_worker_receipt(
    receipt: Any,
    *,
    expected_test_ids: list[str],
    request_kind: str,
    requested_names: list[str],
    worker_sha256: str,
    source_fingerprint: str,
) -> bool:
    if not isinstance(receipt, dict) or set(receipt) != WORKER_RECEIPT_FIELDS:
        return False
    list_fields = (
        "requested_names",
        "loaded_test_ids",
        "started_test_ids",
        "successful_test_ids",
        "failures",
        "errors",
        "skipped_test_ids",
        "expected_failure_test_ids",
        "unexpected_success_test_ids",
    )
    if any(not isinstance(receipt.get(field), list) for field in list_fields):
        return False
    string_list_fields = (
        "requested_names",
        "loaded_test_ids",
        "started_test_ids",
        "successful_test_ids",
        "skipped_test_ids",
        "expected_failure_test_ids",
        "unexpected_success_test_ids",
    )
    if any(
        any(not isinstance(item, str) or not item for item in receipt[field])
        for field in string_list_fields
    ):
        return False
    if (
        any(not isinstance(item, str) or not item for item in expected_test_ids)
        or any(not isinstance(item, str) or not item for item in requested_names)
    ):
        return False
    expected = collections.Counter(expected_test_ids)
    loaded = collections.Counter(receipt["loaded_test_ids"])
    started = collections.Counter(receipt["started_test_ids"])
    successful = collections.Counter(receipt["successful_test_ids"])
    return (
        type(receipt.get("schema_version")) is int
        and receipt.get("schema_version") == 1
        and receipt.get("runner_id") == WORKER_RUNNER_ID
        and receipt.get("runner_sha256") == worker_sha256
        and receipt.get("status") == "pass"
        and receipt.get("request_kind") == request_kind
        and receipt.get("requested_names") == requested_names
        and expected == loaded == started == successful
        and all(count == 1 for count in expected.values())
        and type(receipt.get("tests_run")) is int
        and receipt.get("tests_run") == len(expected_test_ids)
        and receipt.get("failures") == []
        and receipt.get("errors") == []
        and receipt.get("skipped_test_ids") == []
        and receipt.get("expected_failure_test_ids") == []
        and receipt.get("unexpected_success_test_ids") == []
        and receipt.get("source_fingerprint_before") == source_fingerprint
        and receipt.get("source_fingerprint_after") == source_fingerprint
        and receipt.get("exact_execution") is True
    )


def run_worker(
    *,
    project_root: Path,
    test_package: str,
    request_kind: str,
    requested_names: list[str],
    expected_test_ids: list[str],
    timeout_seconds: float,
    deadline: float,
    worker_sha256: str,
    source_fingerprint: str,
) -> dict[str, Any]:
    remaining = deadline - time.monotonic()
    effective_timeout = min(timeout_seconds, max(remaining, 0.0))
    temporary_root = Path(
        tempfile.mkdtemp(prefix="ids-governance-regression-")
    )
    option = "--module" if request_kind == "module" else "--selector"
    argv = [
        sys.executable,
        str(WORKER_SCRIPT),
        "--project-root",
        str(project_root),
        "--test-package",
        test_package,
    ]
    for name in requested_names:
        argv.extend([option, name])
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    environment["TZ"] = "UTC"
    environment["TMPDIR"] = str(temporary_root)
    timed_out = effective_timeout <= 0 or _SHUTDOWN_EVENT.is_set()
    output = ""
    process_exit = 124 if timed_out else None
    receipt: dict[str, Any] | None = None
    receipt_valid = False
    cleanup_succeeded = False
    process: subprocess.Popen[str] | None = None
    try:
        if not timed_out and not _SHUTDOWN_EVENT.is_set():
            process = subprocess.Popen(
                argv,
                cwd=project_root,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=(os.name == "posix"),
            )
            with _ACTIVE_PROCESSES_LOCK:
                _ACTIVE_PROCESSES.add(process)
            try:
                output, _ = process.communicate(timeout=effective_timeout)
                process_exit = process.returncode
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_process(process)
                output, _ = process.communicate()
                process_exit = 124
            finally:
                with _ACTIVE_PROCESSES_LOCK:
                    _ACTIVE_PROCESSES.discard(process)
        try:
            receipt = strict_json_object(output)
        except (
            DuplicateKeyError,
            json.JSONDecodeError,
            ValueError,
        ):
            receipt = None
        receipt_valid = validate_worker_receipt(
            receipt,
            expected_test_ids=expected_test_ids,
            request_kind=request_kind,
            requested_names=requested_names,
            worker_sha256=worker_sha256,
            source_fingerprint=source_fingerprint,
        )
    finally:
        if process is not None and process.poll() is None:
            terminate_process(process)
        try:
            shutil.rmtree(temporary_root)
            cleanup_succeeded = not temporary_root.exists()
        except OSError:
            cleanup_succeeded = False
    passed = (
        not timed_out
        and process_exit == 0
        and receipt_valid
        and cleanup_succeeded
    )
    return {
        "request_kind": request_kind,
        "requested_names": requested_names,
        "expected_test_ids": expected_test_ids,
        "actual_process_exit": process_exit,
        "timed_out": timed_out,
        "timeout_seconds": timeout_seconds,
        "effective_timeout_seconds": round(effective_timeout, 3),
        "stdout_sha256": sha256_bytes(output.encode("utf-8")),
        "worker_receipt": receipt,
        "temporary_root_removed": cleanup_succeeded,
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
    total_timeout_seconds: float = TOTAL_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    _SHUTDOWN_EVENT.clear()
    runner_sha256 = sha256_bytes(Path(__file__).read_bytes())
    worker_sha256 = sha256_bytes(WORKER_SCRIPT.read_bytes())
    try:
        inventory = discover_inventory(
            project_root=project_root,
            test_package=test_package,
            heavy_module=heavy_module,
        )
        source_before = test_source_fingerprint(
            project_root,
            test_package,
        )
    except (InventoryError, OSError) as exc:
        return {
            "schema_version": 2,
            "runner_id": RUNNER_ID,
            "runner_sha256": runner_sha256,
            "status": "fail",
            "inventory_error": f"{type(exc).__name__}: {exc}",
        }
    worker_count = min(max_heavy_workers, len(inventory["heavy_selectors"]))
    if worker_count < 1:
        return {
            "schema_version": 2,
            "runner_id": RUNNER_ID,
            "runner_sha256": runner_sha256,
            "status": "fail",
            "inventory_error": "heavy worker count must be positive",
        }
    deadline = time.monotonic() + total_timeout_seconds
    non_heavy = run_worker(
        project_root=project_root,
        test_package=test_package,
        request_kind="module",
        requested_names=inventory["non_heavy_modules"],
        expected_test_ids=inventory["non_heavy_selectors"],
        timeout_seconds=non_heavy_timeout_seconds,
        deadline=deadline,
        worker_sha256=worker_sha256,
        source_fingerprint=source_before,
    )
    heavy_results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=worker_count,
        thread_name_prefix="governance-regression",
    ) as executor:
        futures = {
            selector: executor.submit(
                run_worker,
                project_root=project_root,
                test_package=test_package,
                request_kind="selector",
                requested_names=[selector],
                expected_test_ids=[selector],
                timeout_seconds=heavy_selector_timeout_seconds,
                deadline=deadline,
                worker_sha256=worker_sha256,
                source_fingerprint=source_before,
            )
            for selector in inventory["heavy_selectors"]
        }
        for selector in inventory["heavy_selectors"]:
            heavy_results.append(futures[selector].result())
    terminate_active_processes()
    try:
        source_after = test_source_fingerprint(project_root, test_package)
    except (InventoryError, OSError):
        source_after = None

    workers = [non_heavy, *heavy_results]
    worker_receipts = [
        item.get("worker_receipt")
        for item in workers
        if isinstance(item.get("worker_receipt"), dict)
    ]
    loaded = [
        selector
        for receipt in worker_receipts
        for selector in receipt.get("loaded_test_ids", [])
    ]
    started = [
        selector
        for receipt in worker_receipts
        for selector in receipt.get("started_test_ids", [])
    ]
    successful = [
        selector
        for receipt in worker_receipts
        for selector in receipt.get("successful_test_ids", [])
    ]
    discovered = inventory["selectors"]
    planned = [
        *inventory["non_heavy_selectors"],
        *inventory["heavy_selectors"],
    ]
    counters_match = (
        collections.Counter(discovered)
        == collections.Counter(planned)
        == collections.Counter(loaded)
        == collections.Counter(started)
        == collections.Counter(successful)
        and all(
            count == 1
            for count in collections.Counter(discovered).values()
        )
    )
    coverage_complete = (
        counters_match
        and all(item["result"] == "pass" for item in workers)
        and source_before == source_after
        and len(_ACTIVE_PROCESSES) == 0
        and all(item["temporary_root_removed"] for item in workers)
        and time.monotonic() <= deadline
    )
    return {
        "schema_version": 2,
        "runner_id": RUNNER_ID,
        "runner_sha256": runner_sha256,
        "worker_runner_id": WORKER_RUNNER_ID,
        "worker_runner_sha256": worker_sha256,
        "status": "pass" if coverage_complete else "fail",
        "worker_count": worker_count,
        "total_timeout_seconds": total_timeout_seconds,
        "source_fingerprint_before": source_before,
        "source_fingerprint_after": source_after,
        "selector_inventory_sha256": sha256_bytes(
            canonical_json(discovered)
        ),
        "discovered_test_ids": discovered,
        "planned_test_ids": planned,
        "loaded_test_ids": loaded,
        "started_test_ids": started,
        "successful_test_ids": successful,
        "non_heavy_worker": non_heavy,
        "heavy_workers": heavy_results,
        "coverage_complete": coverage_complete,
        "active_process_count_after": len(_ACTIVE_PROCESSES),
        "all_temporary_roots_removed": all(
            item["temporary_root_removed"] for item in workers
        ),
    }


def main() -> int:
    if os.name == "posix":
        signal.signal(signal.SIGTERM, signal_shutdown)
        signal.signal(signal.SIGINT, signal_shutdown)
    payload = run_regression()
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
