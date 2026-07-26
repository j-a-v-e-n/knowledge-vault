#!/usr/bin/env python3
"""Append and finalize V2 execution records with locking, CAS, and recovery."""

from __future__ import annotations

import argparse
import copy
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import derive_project_state as project_state
from scripts import verify_execution_loop_v2 as execution
from scripts import verify_work_packets as work_packets


POLICY_RELATIVE = Path("governance/EXECUTION_LOOP_POLICY_V2.json")
PACKET_DIRECTORY = Path(".work_packets/packets")
NONE_TAIL = "NONE"
JOURNAL_SCHEMA = "execution-recorder-transaction/v2"
PREPARE_SCHEMA = "execution-recorder-transaction-prepare/v2"
OPERATION_SCHEMA = "execution-recorder-operation/v2"
OPERATION_PREPARE_SCHEMA = "execution-recorder-operation-prepare/v2"
EXECUTION_RECEIPT_SCHEMA = "execution-finalization-receipt/v2"
TRANSACTION_ID_RE = re.compile(r"[0-9a-f]{32}")
OPERATION_ID_RE = re.compile(r"[0-9a-f]{32}")
_LOCAL_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.RLock] = {}
_HELD_LOCK_DEPTH = threading.local()


class RecorderError(RuntimeError):
    """Raised when a recorder operation cannot preserve its invariants."""


class SimulatedRecorderCrash(RuntimeError):
    """Test-only interruption after a bounded number of replacements."""


class SimulatedOperationCrash(RuntimeError):
    """Test-only interruption at one durable operation lifecycle boundary."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def raw_sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_datetime_milliseconds() -> datetime:
    value = datetime.now(UTC)
    return value.replace(microsecond=(value.microsecond // 1000) * 1000)


def format_utc_milliseconds(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def parse_utc_milliseconds(value: str) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except (TypeError, ValueError) as exc:
        raise RecorderError(f"invalid prior attempt timestamp: {value!r}") from exc
    return parsed.replace(tzinfo=UTC)


def observed_interval(started: datetime) -> tuple[str, int]:
    ended = utc_datetime_milliseconds()
    if ended < started:
        ended = started
    wall_time_ms = int((ended - started).total_seconds() * 1000)
    return format_utc_milliseconds(ended), wall_time_ms


def strict_load(path: Path, label: str) -> dict[str, Any]:
    try:
        value = execution.load_json(path)
    except Exception as exc:
        raise RecorderError(f"{label}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise RecorderError(f"{label}: must be a JSON object")
    return value


def normalized_relative(value: str, label: str) -> str:
    errors: list[str] = []
    relative = execution.normalized_relative(value, label, errors)
    if relative is None or errors:
        raise RecorderError("; ".join(errors) or f"{label}: invalid path")
    return relative


def project_file(root: Path, relative: str, label: str) -> Path:
    errors: list[str] = []
    path = execution.resolve_path(
        root,
        relative,
        label,
        errors,
        must_exist=False,
    )
    if path is None or errors:
        raise RecorderError("; ".join(errors) or f"{label}: invalid path")
    return path


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.recorder-",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def packet_path(root: Path, packet_id: str) -> Path:
    if execution.PACKET_ID_RE.fullmatch(packet_id) is None:
        raise RecorderError("packet_id is invalid")
    return root / PACKET_DIRECTORY / f"{packet_id}.packet.json"


def load_packets(root: Path) -> dict[str, dict[str, Any]]:
    packets: dict[str, dict[str, Any]] = {}
    for path in sorted((root / PACKET_DIRECTORY).glob("*.packet.json")):
        packet = strict_load(path, f"packet {path.name}")
        packet_id = packet.get("packet_id")
        if not isinstance(packet_id, str) or packet_id in packets:
            raise RecorderError(f"packet {path.name}: invalid or duplicate packet_id")
        packets[packet_id] = packet
    return packets


def ledger_path(root: Path, packet_id: str) -> Path:
    return root / execution.ledger_path_for(packet_id)


def tail_sha256(ledger: dict[str, Any] | None) -> str | None:
    if ledger is None:
        return None
    attempts = ledger.get("attempts")
    if not isinstance(attempts, list) or not attempts:
        raise RecorderError("ledger has no attempt tail")
    tail = attempts[-1].get("record_sha256")
    if not isinstance(tail, str):
        raise RecorderError("ledger attempt tail is invalid")
    return tail


def require_tail(actual: str | None, expected: str) -> None:
    expected_value = None if expected == NONE_TAIL else expected
    if expected_value != actual:
        raise RecorderError(
            f"expected-tail CAS failed: expected={expected!r}, actual={actual!r}"
        )


def transaction_root(root: Path) -> Path:
    return root / execution.EXPECTED_RECORDER["transaction_directory"]


def operation_root(root: Path) -> Path:
    return root / execution.EXPECTED_RECORDER["operation_directory"]


def pending_transaction_paths(root: Path) -> list[Path]:
    directory = transaction_root(root)
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise RecorderError("transaction directory must be a real directory")
    return sorted(directory.iterdir(), key=lambda item: item.name)


def pending_operation_paths(root: Path) -> list[Path]:
    directory = operation_root(root)
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise RecorderError("operation directory must be a real directory")
    return sorted(directory.iterdir(), key=lambda item: item.name)


def require_no_pending_transactions(root: Path) -> None:
    pending = pending_transaction_paths(root)
    if pending:
        raise RecorderError(
            "interrupted transaction requires recovery before new writes: "
            + ", ".join(path.name for path in pending)
        )


def require_no_pending_operations(root: Path) -> None:
    pending = pending_operation_paths(root)
    if pending:
        raise RecorderError(
            "interrupted operation requires recovery before new work: "
            + ", ".join(path.name for path in pending)
        )


def operation_document(
    operation_id: str,
    packet_id: str,
    kind: str,
    expected_tail: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": OPERATION_SCHEMA,
        "operation_id": operation_id,
        "packet_id": packet_id,
        "kind": kind,
        "phase": "prepared",
        "expected_tail": expected_tail,
        "request": request,
        "outcome": None,
        "commit_plan": None,
    }


def operation_prepare_document(
    operation_id: str,
    packet_id: str,
    kind: str,
) -> dict[str, Any]:
    return {
        "schema_version": OPERATION_PREPARE_SCHEMA,
        "operation_id": operation_id,
        "packet_id": packet_id,
        "kind": kind,
        "phase": "prelaunch_identity",
    }


def validate_operation(directory: Path) -> dict[str, Any]:
    if directory.is_symlink() or not directory.is_dir():
        raise RecorderError(f"operation {directory.name}: invalid directory")
    prepare = strict_load(
        directory / "prepare.json",
        "operation prepare",
    )
    if (
        set(prepare)
        != {
            "schema_version",
            "operation_id",
            "packet_id",
            "kind",
            "phase",
        }
        or prepare["schema_version"] != OPERATION_PREPARE_SCHEMA
        or prepare["operation_id"] != directory.name
        or prepare["phase"] != "prelaunch_identity"
    ):
        raise RecorderError("operation prepare identity differs")
    operation = strict_load(directory / "operation.json", "operation")
    expected_fields = {
        "schema_version",
        "operation_id",
        "packet_id",
        "kind",
        "phase",
        "expected_tail",
        "request",
        "outcome",
        "commit_plan",
    }
    if set(operation) != expected_fields:
        raise RecorderError("operation schema fields differ")
    if (
        operation["schema_version"] != OPERATION_SCHEMA
        or operation["operation_id"] != directory.name
        or OPERATION_ID_RE.fullmatch(directory.name) is None
        or not isinstance(operation["packet_id"], str)
        or execution.PACKET_ID_RE.fullmatch(operation["packet_id"]) is None
        or operation["kind"] not in {"append", "run", "finalize", "seal"}
        or prepare["packet_id"] != operation["packet_id"]
        or prepare["kind"] != operation["kind"]
        or operation["phase"]
        not in {
            "prepared",
            "check_prepared",
            "outcome_recorded",
            "commit_preparing",
            "commit_planned",
            "core_committed",
        }
        or not isinstance(operation["expected_tail"], str)
        or (
            operation["expected_tail"] != NONE_TAIL
            and execution.SHA256_RE.fullmatch(operation["expected_tail"]) is None
        )
        or not isinstance(operation["request"], dict)
        or (
            operation["outcome"] is not None
            and not isinstance(operation["outcome"], dict)
        )
        or (
            operation["commit_plan"] is not None
            and not isinstance(operation["commit_plan"], list)
        )
    ):
        raise RecorderError("operation identity or lifecycle differs")
    allowed_entries = {"prepare.json", "operation.json", "planned"}
    unexpected = {entry.name for entry in directory.iterdir()} - allowed_entries
    if unexpected:
        raise RecorderError(
            f"operation {directory.name}: unexpected entries {sorted(unexpected)}"
        )
    plan = operation["commit_plan"]
    if plan is not None:
        if not plan or operation["phase"] not in {
            "commit_planned",
            "core_committed",
        }:
            raise RecorderError("operation commit plan phase differs")
        for index, item in enumerate(plan):
            if (
                not isinstance(item, dict)
                or set(item)
                != {
                    "target",
                    "staged",
                    "before_sha256",
                    "desired_sha256",
                }
                or (
                    item["before_sha256"] is not None
                    and (
                        not isinstance(item["before_sha256"], str)
                        or execution.SHA256_RE.fullmatch(item["before_sha256"]) is None
                    )
                )
                or not isinstance(item["desired_sha256"], str)
                or execution.SHA256_RE.fullmatch(item["desired_sha256"]) is None
            ):
                raise RecorderError("operation commit plan schema differs")
            target = normalized_relative(
                item["target"],
                f"operation commit target {index}",
            )
            staged = normalized_relative(
                item["staged"],
                f"operation staged payload {index}",
            )
            if (
                target != item["target"]
                or staged != item["staged"]
                or staged != f"planned/{index:04d}.bin"
            ):
                raise RecorderError("operation commit paths differ")
            staged_path = directory / staged
            if (
                staged_path.is_symlink()
                or not staged_path.is_file()
                or raw_sha256(staged_path.read_bytes()) != item["desired_sha256"]
            ):
                raise RecorderError("operation staged payload differs")
    elif operation["phase"] in {"commit_planned", "core_committed"}:
        raise RecorderError("operation commit phase lacks a plan")
    return operation


def create_operation(
    root: Path,
    packet_id: str,
    kind: str,
    expected_tail: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    require_no_pending_operations(root)
    operation_id = uuid.uuid4().hex
    runtime_root = operation_root(root)
    if not runtime_root.exists():
        runtime_root.mkdir(parents=True, exist_ok=False)
        fsync_directory(runtime_root.parent)
    directory = runtime_root / operation_id
    directory.mkdir(exist_ok=False)
    fsync_directory(runtime_root)
    atomic_write(
        directory / "prepare.json",
        canonical_bytes(operation_prepare_document(operation_id, packet_id, kind)),
    )
    operation = operation_document(
        operation_id,
        packet_id,
        kind,
        expected_tail,
        request,
    )
    atomic_write(directory / "operation.json", canonical_bytes(operation))
    return operation


def write_operation(root: Path, operation: dict[str, Any]) -> None:
    operation_id = operation["operation_id"]
    if OPERATION_ID_RE.fullmatch(operation_id) is None:
        raise RecorderError("operation_id is invalid")
    directory = operation_root(root) / operation_id
    atomic_write(directory / "operation.json", canonical_bytes(operation))
    validate_operation(directory)


def set_operation_outcome(
    root: Path,
    operation: dict[str, Any],
    outcome: dict[str, Any],
) -> None:
    if operation["phase"] not in {"prepared", "outcome_recorded"}:
        raise RecorderError("operation cannot record an outcome in this phase")
    operation["outcome"] = outcome
    operation["phase"] = "outcome_recorded"
    write_operation(root, operation)


def plan_operation_commit(
    root: Path,
    operation: dict[str, Any],
    replacements: dict[str, bytes],
) -> None:
    if operation["phase"] != "outcome_recorded":
        raise RecorderError("operation outcome must be durable before commit")
    if not replacements:
        raise RecorderError("operation commit replacements are empty")
    directory = operation_root(root) / operation["operation_id"]
    planned = directory / "planned"
    if planned.exists():
        shutil.rmtree(planned)
        fsync_directory(directory)
    operation["phase"] = "commit_preparing"
    operation["commit_plan"] = None
    write_operation(root, operation)
    planned.mkdir(parents=True, exist_ok=False)
    fsync_directory(directory)
    plan: list[dict[str, Any]] = []
    try:
        for index, (relative, content) in enumerate(sorted(replacements.items())):
            target_relative = normalized_relative(
                relative,
                "operation commit target",
            )
            target = project_file(
                root,
                target_relative,
                "operation commit target",
            )
            before_sha256 = (
                raw_sha256(target.read_bytes())
                if target.exists() and target.is_file() and not target.is_symlink()
                else None
            )
            if target.exists() and (target.is_symlink() or not target.is_file()):
                raise RecorderError(
                    f"operation target {target_relative} is not a real file"
                )
            staged_relative = f"planned/{index:04d}.bin"
            atomic_write(directory / staged_relative, content)
            plan.append(
                {
                    "target": target_relative,
                    "staged": staged_relative,
                    "before_sha256": before_sha256,
                    "desired_sha256": raw_sha256(content),
                }
            )
    except Exception:
        shutil.rmtree(planned)
        fsync_directory(directory)
        operation["phase"] = "outcome_recorded"
        operation["commit_plan"] = None
        write_operation(root, operation)
        raise
    operation["commit_plan"] = plan
    operation["phase"] = "commit_planned"
    write_operation(root, operation)


def planned_replacements(
    root: Path,
    operation: dict[str, Any],
) -> dict[str, bytes]:
    directory = operation_root(root) / operation["operation_id"]
    validated = validate_operation(directory)
    plan = validated["commit_plan"]
    if not isinstance(plan, list):
        raise RecorderError("operation has no durable commit plan")
    return {item["target"]: (directory / item["staged"]).read_bytes() for item in plan}


def operation_commit_state(
    root: Path,
    operation: dict[str, Any],
) -> str:
    plan = operation["commit_plan"]
    if not isinstance(plan, list):
        raise RecorderError("operation has no commit plan")
    states: list[str] = []
    for item in plan:
        target = project_file(root, item["target"], "operation target")
        actual = (
            raw_sha256(target.read_bytes())
            if target.exists() and target.is_file() and not target.is_symlink()
            else None
        )
        if actual == item["desired_sha256"]:
            states.append("desired")
        elif actual == item["before_sha256"]:
            states.append("before")
        else:
            states.append("diverged")
    if states and all(state == "desired" for state in states):
        return "committed"
    if states and all(state == "before" for state in states):
        return "uncommitted"
    return "diverged"


def commit_planned_operation(
    root: Path,
    operation: dict[str, Any],
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
) -> str | None:
    if operation["phase"] not in {"commit_planned", "core_committed"}:
        raise RecorderError("operation has no commit ready for recovery")
    state = operation_commit_state(root, operation)
    transaction_id: str | None = None
    if state == "uncommitted":
        transaction_id = apply_transaction(
            root,
            operation["packet_id"],
            planned_replacements(root, operation),
            crash_after_replacements=crash_after_replacements,
            crash_before_journal_after_staged=(crash_before_journal_after_staged),
        )
    elif state != "committed":
        raise RecorderError(
            "operation targets diverged from both before and planned states"
        )
    operation["phase"] = "core_committed"
    write_operation(root, operation)
    return transaction_id


def remove_operation(root: Path, operation_id: str) -> None:
    if OPERATION_ID_RE.fullmatch(operation_id) is None:
        raise RecorderError("operation_id is invalid")
    directory = operation_root(root) / operation_id
    validate_operation(directory)
    shutil.rmtree(directory)
    fsync_directory(directory.parent)


def lock_path(root: Path, packet_id: str) -> Path:
    identity = hashlib.sha256(
        f"{root.resolve()}::{packet_id}".encode("utf-8")
    ).hexdigest()
    directory = Path(tempfile.gettempdir()) / "ids-execution-v2-locks"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{identity}.lock"


@contextlib.contextmanager
def packet_lock(root: Path, packet_id: str) -> Iterator[None]:
    path = lock_path(root, packet_id)
    identity = str(path)
    with _LOCAL_LOCKS_GUARD:
        local_lock = _LOCAL_LOCKS.setdefault(identity, threading.RLock())
    with local_lock:
        depths = getattr(_HELD_LOCK_DEPTH, "values", None)
        if depths is None:
            depths = {}
            _HELD_LOCK_DEPTH.values = depths
        depth = depths.get(identity, 0)
        if depth:
            depths[identity] = depth + 1
            try:
                yield
            finally:
                depths[identity] -= 1
            return
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            depths[identity] = 1
            yield
        finally:
            depths.pop(identity, None)
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)


def journal_document(
    transaction_id: str,
    packet_id: str,
    replacements: list[dict[str, Any]],
    next_index: int,
) -> dict[str, Any]:
    return {
        "schema_version": JOURNAL_SCHEMA,
        "transaction_id": transaction_id,
        "packet_id": packet_id,
        "next_index": next_index,
        "replacements": replacements,
    }


def prepare_document(transaction_id: str, packet_id: str) -> dict[str, Any]:
    return {
        "schema_version": PREPARE_SCHEMA,
        "transaction_id": transaction_id,
        "packet_id": packet_id,
        "phase": "staging_before_commit_journal",
    }


def validate_prepare(directory: Path) -> dict[str, Any]:
    prepare = strict_load(directory / "prepare.json", "transaction prepare")
    if (
        set(prepare) != {"schema_version", "transaction_id", "packet_id", "phase"}
        or prepare["schema_version"] != PREPARE_SCHEMA
        or prepare["transaction_id"] != directory.name
        or TRANSACTION_ID_RE.fullmatch(directory.name) is None
        or not isinstance(prepare["packet_id"], str)
        or execution.PACKET_ID_RE.fullmatch(prepare["packet_id"]) is None
        or prepare["phase"] != "staging_before_commit_journal"
    ):
        raise RecorderError("transaction prepare identity differs")
    return prepare


def validate_journal(root: Path, directory: Path) -> dict[str, Any]:
    if directory.is_symlink() or not directory.is_dir():
        raise RecorderError(f"transaction {directory.name}: invalid directory")
    journal = strict_load(directory / "journal.json", "transaction journal")
    expected_fields = {
        "schema_version",
        "transaction_id",
        "packet_id",
        "next_index",
        "replacements",
    }
    if set(journal) != expected_fields or journal["schema_version"] != JOURNAL_SCHEMA:
        raise RecorderError("transaction journal schema differs")
    if (
        journal["transaction_id"] != directory.name
        or TRANSACTION_ID_RE.fullmatch(directory.name) is None
        or not isinstance(journal["packet_id"], str)
        or execution.PACKET_ID_RE.fullmatch(journal["packet_id"]) is None
    ):
        raise RecorderError("transaction journal identity differs")
    replacements = journal["replacements"]
    next_index = journal["next_index"]
    if (
        not isinstance(replacements, list)
        or not replacements
        or type(next_index) is not int
        or not 0 <= next_index <= len(replacements)
    ):
        raise RecorderError("transaction journal sequence is invalid")
    for index, item in enumerate(replacements):
        if (
            not isinstance(item, dict)
            or set(item) != {"target", "staged", "sha256"}
            or not isinstance(item["sha256"], str)
        ):
            raise RecorderError("transaction replacement schema differs")
        target = normalized_relative(item["target"], "transaction target")
        staged = normalized_relative(item["staged"], "transaction staged path")
        transaction_relative = execution.EXPECTED_RECORDER["transaction_directory"]
        if (
            target != item["target"]
            or staged != item["staged"]
            or staged != f"staged/{index:04d}.bin"
            or target == transaction_relative
            or target.startswith(f"{transaction_relative}/")
        ):
            raise RecorderError("transaction paths are not canonical")
        staged_path = directory / staged
        if (
            staged_path.is_symlink()
            or not staged_path.is_file()
            or raw_sha256(staged_path.read_bytes()) != item["sha256"]
        ):
            raise RecorderError(
                f"transaction staged content {index} is missing or changed"
            )
        project_file(root, target, f"transaction target {index}")
    return journal


def apply_transaction(
    root: Path,
    packet_id: str,
    replacements: dict[str, bytes],
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
) -> str:
    with packet_lock(root, "__GLOBAL-TRANSACTION__"):
        return _apply_transaction_locked(
            root,
            packet_id,
            replacements,
            crash_after_replacements=crash_after_replacements,
            crash_before_journal_after_staged=(crash_before_journal_after_staged),
        )


def _apply_transaction_locked(
    root: Path,
    packet_id: str,
    replacements: dict[str, bytes],
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
) -> str:
    require_no_pending_transactions(root)
    if not replacements:
        raise RecorderError("transaction replacements are empty")
    transaction_id = uuid.uuid4().hex
    runtime_root = transaction_root(root)
    if not runtime_root.exists():
        runtime_root.mkdir(parents=True, exist_ok=False)
        fsync_directory(runtime_root.parent)
    directory = runtime_root / transaction_id
    directory.mkdir(exist_ok=False)
    fsync_directory(runtime_root)
    atomic_write(
        directory / "prepare.json",
        canonical_bytes(prepare_document(transaction_id, packet_id)),
    )
    records: list[dict[str, Any]] = []
    journal_path = directory / "journal.json"
    journal_written = False
    try:
        for index, (relative, content) in enumerate(sorted(replacements.items())):
            target = normalized_relative(relative, "transaction target")
            transaction_relative = execution.EXPECTED_RECORDER["transaction_directory"]
            if target == transaction_relative or target.startswith(
                f"{transaction_relative}/"
            ):
                raise RecorderError(
                    "transaction cannot replace its own runtime journal"
                )
            staged_relative = f"staged/{index:04d}.bin"
            staged = directory / staged_relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(staged, content)
            records.append(
                {
                    "target": target,
                    "staged": staged_relative,
                    "sha256": raw_sha256(content),
                }
            )
        if crash_before_journal_after_staged:
            raise SimulatedRecorderCrash(transaction_id)
        atomic_write(
            journal_path,
            canonical_bytes(journal_document(transaction_id, packet_id, records, 0)),
        )
        journal_written = True
    except SimulatedRecorderCrash:
        raise
    except Exception:
        if not journal_written:
            shutil.rmtree(directory)
            fsync_directory(directory.parent)
        raise
    for index, record in enumerate(records):
        content = (directory / record["staged"]).read_bytes()
        atomic_write(
            project_file(root, record["target"], "transaction target"),
            content,
        )
        atomic_write(
            journal_path,
            canonical_bytes(
                journal_document(
                    transaction_id,
                    packet_id,
                    records,
                    index + 1,
                )
            ),
        )
        if (
            crash_after_replacements is not None
            and index + 1 == crash_after_replacements
        ):
            raise SimulatedRecorderCrash(transaction_id)
    shutil.rmtree(directory)
    fsync_directory(directory.parent)
    return transaction_id


def recover_transactions(root: Path) -> list[str]:
    with packet_lock(root, "__GLOBAL-TRANSACTION__"):
        return _recover_transactions_locked(root)


def _recover_transactions_locked(root: Path) -> list[str]:
    recovered: list[str] = []
    for directory in pending_transaction_paths(root):
        journal_path = directory / "journal.json"
        if not journal_path.exists():
            if TRANSACTION_ID_RE.fullmatch(directory.name) is None:
                raise RecorderError(
                    f"orphan transaction {directory.name}: invalid identity"
                )
            prepare_path = directory / "prepare.json"
            if not prepare_path.exists():
                entries = list(directory.iterdir())
                if any(
                    entry.is_symlink()
                    or entry.is_dir()
                    or not entry.name.startswith(".prepare.json.recorder-")
                    for entry in entries
                ):
                    raise RecorderError(
                        f"orphan transaction {directory.name}: "
                        "unexpected pre-prepare entries"
                    )
            else:
                validate_prepare(directory)
                allowed_top_level = {"prepare.json", "staged"}
                if {entry.name for entry in directory.iterdir()} - allowed_top_level:
                    raise RecorderError(
                        f"orphan transaction {directory.name}: "
                        "unexpected pre-journal entries"
                    )
                staged = directory / "staged"
                if staged.exists():
                    if staged.is_symlink() or not staged.is_dir():
                        raise RecorderError(
                            f"orphan transaction {directory.name}: invalid staging"
                        )
                    for entry in staged.iterdir():
                        if (
                            entry.is_symlink()
                            or not entry.is_file()
                            or re.fullmatch(r"[0-9]{4}\.bin", entry.name) is None
                        ):
                            raise RecorderError(
                                f"orphan transaction {directory.name}: "
                                "invalid staged payload"
                            )
            recovered.append(directory.name)
            shutil.rmtree(directory)
            fsync_directory(directory.parent)
            continue
        journal = validate_journal(root, directory)
        records = journal["replacements"]
        for index in range(journal["next_index"], len(records)):
            record = records[index]
            atomic_write(
                project_file(root, record["target"], "recovery target"),
                (directory / record["staged"]).read_bytes(),
            )
            journal["next_index"] = index + 1
            atomic_write(journal_path, canonical_bytes(journal))
        recovered.append(journal["transaction_id"])
        shutil.rmtree(directory)
        fsync_directory(directory.parent)
    if recovered and not pending_operation_paths(root):
        project_state.refresh_project_state(root)
    return recovered


def discard_incomplete_commit_preparation(
    root: Path,
    operation: dict[str, Any],
) -> None:
    if operation["phase"] != "commit_preparing":
        return
    directory = operation_root(root) / operation["operation_id"]
    planned = directory / "planned"
    if planned.exists():
        if planned.is_symlink() or not planned.is_dir():
            raise RecorderError("incomplete operation staging is invalid")
        shutil.rmtree(planned)
        fsync_directory(directory)
    operation["phase"] = "outcome_recorded"
    operation["commit_plan"] = None
    write_operation(root, operation)


def recover_append_or_run_operation(
    root: Path,
    operation: dict[str, Any],
) -> None:
    request = operation["request"]
    required = {
        "failure_after",
        "status_after",
        "root_cause_id",
        "root_cause",
    }
    if not required.issubset(request):
        raise RecorderError("recoverable append request fields differ")
    if operation["phase"] == "prepared":
        timestamp = format_utc_milliseconds(utc_datetime_milliseconds())
        if operation["kind"] == "append":
            outcome = {
                "process_observation": no_process_observation("passive"),
                "started_at": timestamp,
                "ended_at": timestamp,
                "wall_time_ms": 0,
            }
        else:
            command = request.get("command")
            if (
                not isinstance(command, list)
                or not command
                or any(not isinstance(item, str) or not item for item in command)
            ):
                raise RecorderError("recoverable run argv differs")
            ledger = strict_load(
                ledger_path(root, operation["packet_id"]),
                f"ledger {operation['packet_id']}",
            )
            prior_failures = ledger["attempts"][-1]["failure_delta"]["after"]
            requested_failures = request["failure_after"]
            effective_failures = (
                prior_failures if requested_failures is None else requested_failures
            )
            request["failure_after"] = sorted(
                set(effective_failures) | {"RECORDER-902"}
            )
            request["status_after"] = "blocked"
            request["root_cause_id"] = "RECORDER-INDETERMINATE-OUTCOME"
            request["root_cause"] = (
                "A durable process intent existed, but no recoverable child "
                "outcome was persisted; the packet is blocked rather than "
                "silently treating the process as absent or successful."
            )
            outcome = {
                "process_observation": (indeterminate_process_observation(command)),
                "started_at": timestamp,
                "ended_at": timestamp,
                "wall_time_ms": 0,
            }
        set_operation_outcome(root, operation, outcome)
    discard_incomplete_commit_preparation(root, operation)
    if operation["phase"] in {"commit_planned", "core_committed"}:
        commit_planned_operation(root, operation)
        finish_committed_operation(root, operation)
        return
    if operation["phase"] != "outcome_recorded":
        raise RecorderError("append/run operation recovery phase differs")
    outcome = operation["outcome"]
    if not isinstance(outcome, dict):
        raise RecorderError("append/run operation outcome is missing")
    _append_observation_core(
        root,
        operation["packet_id"],
        operation["expected_tail"],
        request["failure_after"],
        request["status_after"],
        request["root_cause_id"],
        request["root_cause"],
        outcome["process_observation"],
        outcome["started_at"],
        outcome["ended_at"],
        outcome["wall_time_ms"],
        operation,
    )


def recover_operations(root: Path) -> list[str]:
    recovered_transactions = recover_transactions(root)
    del recovered_transactions
    recovered: list[str] = []
    with packet_lock(root, "__GLOBAL-OPERATION__"):
        for directory in pending_operation_paths(root):
            operation_path = directory / "operation.json"
            if not operation_path.exists():
                if (
                    directory.is_symlink()
                    or not directory.is_dir()
                    or OPERATION_ID_RE.fullmatch(directory.name) is None
                ):
                    raise RecorderError(
                        f"prelaunch operation {directory.name}: invalid directory"
                    )
                entries = list(directory.iterdir())
                if any(
                    entry.is_symlink()
                    or entry.is_dir()
                    or (
                        entry.name != "prepare.json"
                        and not entry.name.startswith(".prepare.json.recorder-")
                        and not entry.name.startswith(".operation.json.recorder-")
                    )
                    for entry in entries
                ):
                    raise RecorderError(
                        f"prelaunch operation {directory.name}: "
                        "unexpected durable entries"
                    )
                if (directory / "prepare.json").exists():
                    prepare = strict_load(
                        directory / "prepare.json",
                        "prelaunch operation prepare",
                    )
                    if (
                        prepare.get("schema_version") != OPERATION_PREPARE_SCHEMA
                        or prepare.get("operation_id") != directory.name
                        or prepare.get("phase") != "prelaunch_identity"
                    ):
                        raise RecorderError(
                            f"prelaunch operation {directory.name}: "
                            "prepare identity differs"
                        )
                recovered.append(directory.name)
                shutil.rmtree(directory)
                fsync_directory(directory.parent)
                continue
            operation = validate_operation(directory)
            with packet_lock(root, operation["packet_id"]):
                if operation["kind"] in {"append", "run"}:
                    recover_append_or_run_operation(root, operation)
                elif operation["kind"] == "finalize":
                    resume_finalize_operation(root, operation)
                else:
                    resume_seal_operation(root, operation)
            recovered.append(operation["operation_id"])
    return recovered


def runtime_preflight(
    root: Path,
    *,
    allow_stale_packet_id: str | None = None,
    allow_operation_id: str | None = None,
) -> dict[str, Any]:
    receipt = execution.verify(
        root,
        POLICY_RELATIVE,
        allow_stale_packet_id=allow_stale_packet_id,
        allow_pending_operation_id=allow_operation_id,
    )
    expected_freshness = (
        "stale_authorized_for_recorder"
        if allow_stale_packet_id is not None
        else "current"
    )
    if (
        receipt.get("verification_status") != "valid"
        or receipt.get("execution_freshness_status") != expected_freshness
    ):
        raise RecorderError(
            "execution preflight failed: " + "; ".join(receipt.get("errors", []))
        )
    return receipt


def operation_runtime_observer(
    operation_id: str,
) -> project_state.RuntimeAuthorityObserver:
    def observe(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
        configured = policy["sources"]["runtime_authorities"]
        work_config = configured["work_packets"]
        execution_config = configured["execution_freshness"]
        work_receipt = work_packets.verify(
            root,
            root / work_config["policy_path"],
            root / work_config["packet_directory"],
        )
        execution_receipt = execution.verify(
            root,
            Path(execution_config["policy_path"]),
            allow_pending_operation_id=operation_id,
        )
        observation = {
            "work_packets": {
                "status": work_receipt["status"],
                "policy_id": work_receipt["policy_id"],
                "receipt_sha256": project_state.canonical_sha256(work_receipt),
                "completion_verified_count": work_receipt["completion_verified_count"],
                "superseded_receipt_verified_count": work_receipt[
                    "superseded_receipt_verified_count"
                ],
                "dag_edges": work_receipt["dag_edges"],
                "root_packet_ids": work_receipt["root_packet_ids"],
                "sink_packet_ids": work_receipt["sink_packet_ids"],
            },
            "execution_freshness": {
                "verification_status": execution_receipt["verification_status"],
                "execution_freshness_status": execution_receipt[
                    "execution_freshness_status"
                ],
                "policy_id": execution_receipt["policy_id"],
                "receipt_sha256": project_state.canonical_sha256(execution_receipt),
                "tracked_packet_count": execution_receipt["tracked_packet_count"],
                "verified_ledger_count": execution_receipt["verified_ledger_count"],
                "exempt_packet_count": execution_receipt["exempt_packet_count"],
                "authority_basis": execution_receipt["authority_basis"],
            },
        }
        return project_state.validate_runtime_authority_observation(
            observation,
            policy,
        )

    return observe


def post_write_verify(
    root: Path,
    *,
    allow_operation_id: str | None = None,
) -> dict[str, Any]:
    receipt = execution.verify(
        root,
        POLICY_RELATIVE,
        allow_pending_operation_id=allow_operation_id,
    )
    if (
        receipt.get("verification_status") != "valid"
        or receipt.get("execution_freshness_status") != "current"
    ):
        raise RecorderError(
            "post-write execution verification failed: "
            + "; ".join(receipt.get("errors", []))
        )
    observer = (
        None
        if allow_operation_id is None
        else operation_runtime_observer(allow_operation_id)
    )
    project_state.refresh_project_state(
        root,
        runtime_authority_observer=observer,
    )
    project_state.check_project_state(
        root,
        runtime_authority_observer=observer,
    )
    return receipt


def claim_snapshots(
    root: Path,
    packet: dict[str, Any],
    packets: dict[str, dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    errors: list[str] = []
    excluded, claims = execution.current_claim_snapshots(
        root,
        packet,
        {
            packet_id
            for packet_id, item in packets.items()
            if item.get("schema_version") == "work-packet-instance/v2"
            and item.get("state")
            in set(execution.EXPECTED_WORK_PACKETS["ledger_required_states"])
        },
        errors,
    )
    if errors:
        raise RecorderError("; ".join(errors))
    return excluded, claims


def no_process_observation(mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "argv": None,
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "capture_authority": (
            "tool_observed_baseline"
            if mode == "baseline"
            else "self_reported_no_process"
        ),
    }


def indeterminate_process_observation(command: list[str]) -> dict[str, Any]:
    if not command or any(not isinstance(item, str) or not item for item in command):
        raise RecorderError("indeterminate process intent requires a non-empty argv")
    return {
        "mode": "indeterminate",
        "argv": command,
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "capture_authority": "durable_intent_without_recoverable_outcome",
    }


def unknown_cost() -> dict[str, Any]:
    return {
        "wall_time_source": "timestamps",
        "token_usage": {
            "availability": "unknown",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "measurement_source": None,
        },
    }


def blocker(
    root_cause_id: str,
    root_cause: str,
    failure_ids: list[str],
    status_after: str,
) -> dict[str, Any]:
    value = {
        "root_cause_id": root_cause_id,
        "failure_ids": sorted(failure_ids),
        "root_cause": root_cause,
        "status_after": status_after,
    }
    value["fingerprint_sha256"] = execution.canonical_sha256(
        {
            "root_cause_id": value["root_cause_id"],
            "failure_ids": value["failure_ids"],
            "root_cause": value["root_cause"],
        }
    )
    return value


def evidence_kind(relative: str) -> str:
    if relative.startswith(("governance_tests/", "tests/", "acceptance/")):
        return "test"
    if relative.startswith("governance/"):
        return "policy"
    if relative.startswith(("scripts/", "src/", "prototype/")):
        return "implementation"
    return "other"


def regular_files_in_tree(root: Path, relative: str) -> list[str]:
    directory = project_file(root, relative, "changed tree")
    if not directory.is_dir() or directory.is_symlink():
        raise RecorderError(f"changed tree {relative} is not a real directory")
    result: list[str] = []
    for current, directories, filenames in os.walk(
        directory,
        topdown=True,
        followlinks=False,
    ):
        directories.sort()
        filenames.sort()
        current_path = Path(current)
        for name in directories:
            if (current_path / name).is_symlink():
                raise RecorderError(f"changed tree {relative} contains a symlink")
        for name in filenames:
            path = current_path / name
            if path.is_symlink() or not path.is_file():
                raise RecorderError(f"changed tree {relative} contains a special entry")
            result.append(path.relative_to(root).as_posix())
    return sorted(result)


def derive_evidence_after(
    root: Path,
    prior_evidence: list[dict[str, Any]],
    before_claims: list[dict[str, Any]],
    after_claims: list[dict[str, Any]],
    resolved_failure_ids: list[str],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    before_map = {item["path"]: item for item in before_claims}
    changed_claims = [
        item for item in after_claims if before_map.get(item["path"]) != item
    ]
    changed_files: set[str] = set()
    changed_roots: list[str] = []
    for claim in changed_claims:
        changed_roots.append(claim["path"])
        if claim["state"] == "file":
            changed_files.add(claim["path"])
        elif claim["state"] == "tree":
            changed_files.update(regular_files_in_tree(root, claim["path"]))
    retained = [
        item
        for item in prior_evidence
        if not any(
            item["path"] == changed or item["path"].startswith(f"{changed}/")
            for changed in changed_roots
        )
    ]
    additions = [
        {
            "path": relative,
            "sha256": hashlib.sha256(
                project_file(root, relative, "evidence file").read_bytes()
            ).hexdigest(),
            "kind": evidence_kind(relative),
            "supports_failure_ids": sorted(resolved_failure_ids),
        }
        for relative in sorted(changed_files)
    ]
    after = sorted(
        [*retained, *additions],
        key=execution.evidence_identity,
    )
    before = sorted(prior_evidence, key=execution.evidence_identity)
    before_identities = {execution.evidence_identity(item) for item in before}
    after_identities = {execution.evidence_identity(item) for item in after}
    added = [
        item
        for item in after
        if execution.evidence_identity(item) not in before_identities
    ]
    removed = [
        item
        for item in before
        if execution.evidence_identity(item) not in after_identities
    ]
    return after, added, removed


def forced_block_required(attempts: list[dict[str, Any]], retry_budget: int) -> bool:
    execution_attempts = [
        item for item in attempts if item["attempt_kind"] == "execution_attempt"
    ]
    if len(execution_attempts) >= retry_budget:
        return True
    consecutive = 0
    same = 0
    prior_fingerprint: str | None = None
    for attempt in execution_attempts:
        if attempt["declared_progress"]:
            consecutive = 0
            same = 0
            prior_fingerprint = None
            continue
        consecutive += 1
        fingerprint = attempt["blocker"]["fingerprint_sha256"]
        if fingerprint == prior_fingerprint:
            same += 1
        else:
            same = 1
            prior_fingerprint = fingerprint
        if (
            consecutive
            >= execution.EXPECTED_STOPPING["consecutive_no_progress_threshold"]
            or same
            >= execution.EXPECTED_STOPPING[
                "same_blocker_consecutive_no_progress_threshold"
            ]
        ):
            return True
    return False


def _append_observation_core(
    root: Path,
    packet_id: str,
    expected_tail: str,
    failure_after: list[str] | None,
    status_after: str,
    root_cause_id: str,
    root_cause: str,
    process_observation: dict[str, Any],
    started_at: str,
    ended_at: str,
    wall_time_ms: int,
    operation: dict[str, Any],
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    with packet_lock(root, packet_id):
        require_no_pending_transactions(root)
        runtime_preflight(
            root,
            allow_stale_packet_id=packet_id,
            allow_operation_id=operation["operation_id"],
        )
        packets = load_packets(root)
        packet = packets.get(packet_id)
        if packet is None or packet.get("state") != "active":
            raise RecorderError("append requires one active packet")
        ledger_file = ledger_path(root, packet_id)
        ledger = strict_load(ledger_file, f"ledger {packet_id}")
        require_tail(tail_sha256(ledger), expected_tail)
        if ledger.get("terminal_completion") is not None:
            raise RecorderError("terminal ledger cannot be appended")
        previous = ledger["attempts"][-1]
        previous_ended = parse_utc_milliseconds(previous["ended_at"])
        started_value = parse_utc_milliseconds(started_at)
        ended_value = parse_utc_milliseconds(ended_at)
        if started_value < previous_ended:
            started_value = previous_ended
        if ended_value < started_value:
            ended_value = started_value
        started_at = format_utc_milliseconds(started_value)
        ended_at = format_utc_milliseconds(ended_value)
        wall_time_ms = int((ended_value - started_value).total_seconds() * 1000)
        before_failures = sorted(previous["failure_delta"]["after"])
        after_failures = sorted(
            before_failures if failure_after is None else set(failure_after)
        )
        resolved = sorted(set(before_failures) - set(after_failures))
        introduced = sorted(set(after_failures) - set(before_failures))
        excluded, after_claims = claim_snapshots(root, packet, packets)
        before_claims = previous["controlled_snapshot"]["claims"]
        before_evidence = sorted(
            previous["evidence_delta"]["after"],
            key=execution.evidence_identity,
        )
        after_evidence, added, removed = derive_evidence_after(
            root,
            before_evidence,
            before_claims,
            after_claims,
            resolved,
        )
        if status_after == "resolved" and after_failures:
            raise RecorderError("resolved status requires an empty failure set")
        if (
            process_observation["mode"] == "run"
            and status_after == "resolved"
            and process_observation["exit_code"] != 0
        ):
            raise RecorderError(
                "a nonzero recorder-observed process cannot resolve the attempt"
            )
        if status_after == "blocked":
            packet["state"] = "blocked"
        sequence = len(ledger["attempts"]) + 1
        attempt = {
            "schema_version": "execution-attempt/v2",
            "attempt_kind": "execution_attempt",
            "sequence": sequence,
            "retry_index": sum(
                item["attempt_kind"] == "execution_attempt"
                for item in ledger["attempts"]
            ),
            "started_at": started_at,
            "ended_at": ended_at,
            "wall_time_ms": wall_time_ms,
            "blocker": blocker(
                root_cause_id,
                root_cause,
                after_failures,
                status_after,
            ),
            "failure_delta": {
                "before": before_failures,
                "after": after_failures,
                "resolved": resolved,
                "introduced": introduced,
            },
            "evidence_delta": {
                "before": before_evidence,
                "after": after_evidence,
                "added": added,
                "removed": removed,
            },
            "controlled_snapshot": {
                "algorithm": execution.EXPECTED_CURRENT_SNAPSHOT["algorithm"],
                "excluded_paths": excluded,
                "claims": after_claims,
                "claims_sha256": execution.canonical_sha256(after_claims),
            },
            "process_observation": process_observation,
            "cost_observation": unknown_cost(),
            "declared_progress": bool(resolved or added),
            "previous_attempt_sha256": None,
            "record_sha256": "",
        }
        attempt["previous_attempt_sha256"] = execution.canonical_sha256(previous)
        attempt["record_sha256"] = execution.canonical_sha256(
            {key: value for key, value in attempt.items() if key != "record_sha256"}
        )
        ledger["attempts"].append(attempt)
        ledger["reported_state"] = packet["state"]
        if forced_block_required(ledger["attempts"], packet["retry_budget"]):
            if status_after != "blocked" or packet["state"] != "blocked":
                raise RecorderError(
                    "this attempt reaches a stopping threshold and must be "
                    "recorded as the final blocked transition"
                )
        replacements = {
            execution.ledger_path_for(packet_id): canonical_bytes(ledger),
        }
        if packet["state"] == "blocked":
            replacements[packet_path(root, packet_id).relative_to(root).as_posix()] = (
                canonical_bytes(packet)
            )
        plan_operation_commit(root, operation, replacements)
        transaction_id = commit_planned_operation(
            root,
            operation,
            crash_after_replacements=crash_after_replacements,
            crash_before_journal_after_staged=(crash_before_journal_after_staged),
        )
        if crash_after_core_commit:
            raise SimulatedOperationCrash(operation["operation_id"])
        receipt = finish_committed_operation(root, operation)
        return {
            "status": "recorded",
            "packet_id": packet_id,
            "transaction_id": transaction_id,
            "latest_record_sha256": ledger["attempts"][-1]["record_sha256"],
            "process_exit_code": process_observation["exit_code"],
            "execution_verification": receipt["verification_status"],
            "execution_freshness": receipt["execution_freshness_status"],
        }


def finish_committed_operation(
    root: Path,
    operation: dict[str, Any],
) -> dict[str, Any]:
    if operation["phase"] != "core_committed":
        raise RecorderError("operation core is not committed")
    operation_id = operation["operation_id"]
    receipt = post_write_verify(
        root,
        allow_operation_id=operation_id,
    )
    remove_operation(root, operation_id)
    ordinary = execution.verify(root, POLICY_RELATIVE)
    if (
        ordinary.get("verification_status") != "valid"
        or ordinary.get("execution_freshness_status") != "current"
    ):
        raise RecorderError(
            "ordinary verification failed after operation retirement: "
            + "; ".join(ordinary.get("errors", []))
        )
    project_state.check_project_state(root)
    if receipt != ordinary:
        raise RecorderError("operation-aware and ordinary verification receipts differ")
    return ordinary


def append_observation(
    root: Path,
    packet_id: str,
    expected_tail: str,
    failure_after: list[str] | None,
    status_after: str,
    root_cause_id: str,
    root_cause: str,
    process_observation: dict[str, Any],
    started_at: str,
    ended_at: str,
    wall_time_ms: int,
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
    crash_after_outcome: bool = False,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    with packet_lock(root, "__GLOBAL-OPERATION__"):
        with packet_lock(root, packet_id):
            require_no_pending_transactions(root)
            require_no_pending_operations(root)
            runtime_preflight(root, allow_stale_packet_id=packet_id)
            ledger = strict_load(
                ledger_path(root, packet_id),
                f"ledger {packet_id}",
            )
            require_tail(tail_sha256(ledger), expected_tail)
            packets = load_packets(root)
            packet = packets.get(packet_id)
            if packet is None or packet.get("state") != "active":
                raise RecorderError("append requires one active packet")
            if ledger.get("terminal_completion") is not None:
                raise RecorderError("terminal ledger cannot be appended")
            request = {
                "failure_after": failure_after,
                "status_after": status_after,
                "root_cause_id": root_cause_id,
                "root_cause": root_cause,
            }
            operation = create_operation(
                root,
                packet_id,
                "append",
                expected_tail,
                request,
            )
            set_operation_outcome(
                root,
                operation,
                {
                    "process_observation": process_observation,
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "wall_time_ms": wall_time_ms,
                },
            )
            if crash_after_outcome:
                raise SimulatedOperationCrash(operation["operation_id"])
            return _append_observation_core(
                root,
                packet_id,
                expected_tail,
                failure_after,
                status_after,
                root_cause_id,
                root_cause,
                process_observation,
                started_at,
                ended_at,
                wall_time_ms,
                operation,
                crash_after_replacements=crash_after_replacements,
                crash_before_journal_after_staged=(crash_before_journal_after_staged),
                crash_after_core_commit=crash_after_core_commit,
            )


def append_passive(
    root: Path,
    packet_id: str,
    expected_tail: str,
    failure_after: list[str] | None,
    status_after: str,
    root_cause_id: str,
    root_cause: str,
    *,
    crash_after_replacements: int | None = None,
    crash_before_journal_after_staged: bool = False,
    crash_after_outcome: bool = False,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    timestamp = format_utc_milliseconds(utc_datetime_milliseconds())
    return append_observation(
        root,
        packet_id,
        expected_tail,
        failure_after,
        status_after,
        root_cause_id,
        root_cause,
        no_process_observation("passive"),
        timestamp,
        timestamp,
        0,
        crash_after_replacements=crash_after_replacements,
        crash_before_journal_after_staged=(crash_before_journal_after_staged),
        crash_after_outcome=crash_after_outcome,
        crash_after_core_commit=crash_after_core_commit,
    )


def run_and_append(
    root: Path,
    packet_id: str,
    expected_tail: str,
    command: list[str],
    failure_after: list[str] | None,
    status_after: str,
    root_cause_id: str,
    root_cause: str,
    timeout_seconds: float,
    *,
    crash_after_intent: bool = False,
    crash_after_outcome: bool = False,
    crash_after_core_commit: bool = False,
    _lifecycle_hook: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    if not command or any(not item for item in command):
        raise RecorderError("run mode requires a non-empty argv")
    with packet_lock(root, "__GLOBAL-OPERATION__"):
        with packet_lock(root, packet_id):
            require_no_pending_transactions(root)
            require_no_pending_operations(root)
            runtime_preflight(root)
            ledger = strict_load(
                ledger_path(root, packet_id),
                f"ledger {packet_id}",
            )
            require_tail(tail_sha256(ledger), expected_tail)
            packets = load_packets(root)
            packet = packets.get(packet_id)
            if packet is None or packet.get("state") != "active":
                raise RecorderError("run requires one active packet")
            if ledger.get("terminal_completion") is not None:
                raise RecorderError("terminal ledger cannot be appended")
            request = {
                "failure_after": failure_after,
                "status_after": status_after,
                "root_cause_id": root_cause_id,
                "root_cause": root_cause,
                "command": command,
                "timeout_seconds": timeout_seconds,
                "requested_status_after": status_after,
            }
            operation = create_operation(
                root,
                packet_id,
                "run",
                expected_tail,
                request,
            )
            if crash_after_intent:
                raise SimulatedOperationCrash(operation["operation_id"])
            if _lifecycle_hook is not None:
                _lifecycle_hook("intent", operation["operation_id"])
            started = utc_datetime_milliseconds()
            started_at = format_utc_milliseconds(started)
            try:
                completed = subprocess.run(
                    command,
                    cwd=root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                stdout = exc.stdout or b""
                stderr = exc.stderr or b""
                process_observation = {
                    "mode": "run",
                    "argv": command,
                    "exit_code": 124,
                    "stdout_sha256": raw_sha256(stdout),
                    "stderr_sha256": raw_sha256(stderr),
                    "stdout_bytes": len(stdout),
                    "stderr_bytes": len(stderr),
                    "capture_authority": "recorder_executed_process",
                }
            else:
                process_observation = {
                    "mode": "run",
                    "argv": command,
                    "exit_code": completed.returncode,
                    "stdout_sha256": raw_sha256(completed.stdout),
                    "stderr_sha256": raw_sha256(completed.stderr),
                    "stdout_bytes": len(completed.stdout),
                    "stderr_bytes": len(completed.stderr),
                    "capture_authority": "recorder_executed_process",
                }
            ended_at, wall_time_ms = observed_interval(started)
            if process_observation["exit_code"] != 0 and status_after == "resolved":
                prior_failures = ledger["attempts"][-1]["failure_delta"]["after"]
                effective_failures = (
                    prior_failures if failure_after is None else failure_after
                )
                failure_after = sorted(set(effective_failures) | {"RECORDER-901"})
                status_after = "open"
                operation["request"]["failure_after"] = failure_after
                operation["request"]["status_after"] = status_after
                operation["request"]["root_cause"] = (
                    root_cause + "; recorder-observed process exited nonzero, so "
                    "resolution was rejected"
                )
                root_cause = operation["request"]["root_cause"]
            set_operation_outcome(
                root,
                operation,
                {
                    "process_observation": process_observation,
                    "started_at": started_at,
                    "ended_at": ended_at,
                    "wall_time_ms": wall_time_ms,
                },
            )
            if _lifecycle_hook is not None:
                _lifecycle_hook("outcome", operation["operation_id"])
            if crash_after_outcome:
                raise SimulatedOperationCrash(operation["operation_id"])
            return _append_observation_core(
                root,
                packet_id,
                expected_tail,
                failure_after,
                status_after,
                root_cause_id,
                root_cause,
                process_observation,
                started_at,
                ended_at,
                wall_time_ms,
                operation,
                crash_after_core_commit=crash_after_core_commit,
            )


def receipt_value(root: Path, relative: str, label: str) -> dict[str, Any]:
    path = project_file(root, relative, label)
    return strict_load(path, label)


def record_finalize_failure(
    root: Path,
    operation: dict[str, Any],
    observation: dict[str, Any],
    failure_id: str,
    root_cause_id: str,
    root_cause: str,
) -> dict[str, Any]:
    process_observation = {
        field: observation[field]
        for field in (
            "mode",
            "argv",
            "exit_code",
            "stdout_sha256",
            "stderr_sha256",
            "stdout_bytes",
            "stderr_bytes",
            "capture_authority",
        )
    }
    started_at = observation.get(
        "started_at",
        format_utc_milliseconds(utc_datetime_milliseconds()),
    )
    ended_at = observation.get("ended_at", started_at)
    wall_time_ms = observation.get("wall_time_ms", 0)
    request = operation["request"]
    request["failure_record"] = {
        "failure_id": failure_id,
        "root_cause_id": root_cause_id,
        "root_cause": root_cause,
        "observation": observation,
    }
    write_operation(root, operation)
    return _append_observation_core(
        root,
        operation["packet_id"],
        operation["expected_tail"],
        [failure_id],
        "blocked",
        root_cause_id,
        root_cause,
        process_observation,
        started_at,
        ended_at,
        wall_time_ms,
        operation,
    )


def finalize_failure_process_observation(
    observation: dict[str, Any],
) -> dict[str, Any]:
    return {
        "mode": "run",
        "argv": observation["argv"],
        "exit_code": observation["actual_exit_code"],
        "stdout_sha256": observation["stdout_sha256"],
        "stderr_sha256": observation["stderr_sha256"],
        "stdout_bytes": observation["stdout_bytes"],
        "stderr_bytes": observation["stderr_bytes"],
        "capture_authority": "recorder_executed_process",
        "started_at": observation["started_at"],
        "ended_at": observation["ended_at"],
        "wall_time_ms": observation["wall_time_ms"],
    }


def commit_finalize_candidate(
    root: Path,
    operation: dict[str, Any],
    packets: dict[str, dict[str, Any]],
    packet: dict[str, Any],
    ledger: dict[str, Any],
    check_observations: list[dict[str, Any]],
    *,
    crash_after_replacements: int | None = None,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    packet_id = packet["packet_id"]
    latest = ledger["attempts"][-1]
    if (
        latest["controlled_snapshot"]["claims"]
        != claim_snapshots(
            root,
            packet,
            packets,
        )[1]
    ):
        observation = {
            "mode": "indeterminate",
            "argv": packet["acceptance_checks"][-1]["argv"],
            "exit_code": None,
            "stdout_sha256": None,
            "stderr_sha256": None,
            "stdout_bytes": None,
            "stderr_bytes": None,
            "capture_authority": "durable_intent_without_recoverable_outcome",
            "started_at": format_utc_milliseconds(utc_datetime_milliseconds()),
            "ended_at": format_utc_milliseconds(utc_datetime_milliseconds()),
            "wall_time_ms": 0,
        }
        return record_finalize_failure(
            root,
            operation,
            observation,
            "RECORDER-903",
            "RECORDER-ACCEPTANCE-MUTATION",
            "Controlled claims differ from the latest resolved observation; "
            "candidate completion was rejected.",
        )

    contract_digest = work_packets.packet_contract_sha256(packet)
    checkpoint_relative = f".work_packets/receipts/{packet_id}.checkpoint.json"
    acceptance_relative = f".work_packets/receipts/{packet_id}.acceptance.json"
    execution_relative = f".work_packets/receipts/{packet_id}.execution.v2.json"
    packet["checkpoint_path"] = checkpoint_relative
    packet["acceptance_receipt_path"] = acceptance_relative
    packet["state"] = "candidate_complete"
    if work_packets.packet_contract_sha256(packet) != contract_digest:
        raise RecorderError("completion transition changed packet contract")
    _, snapshots = claim_snapshots(root, packet, packets)
    prerequisites: list[dict[str, Any]] = []
    for dependency_id in sorted(packet["depends_on"]):
        dependency = packets[dependency_id]
        checkpoint_value = receipt_value(
            root,
            dependency["checkpoint_path"],
            f"dependency {dependency_id} checkpoint",
        )
        acceptance_value = receipt_value(
            root,
            dependency["acceptance_receipt_path"],
            f"dependency {dependency_id} acceptance",
        )
        prerequisites.append(
            {
                "packet_id": dependency_id,
                "packet_contract_sha256": (
                    work_packets.packet_contract_sha256(dependency)
                ),
                "checkpoint_receipt_sha256": execution.canonical_sha256(
                    checkpoint_value
                ),
                "acceptance_receipt_sha256": execution.canonical_sha256(
                    acceptance_value
                ),
            }
        )
    checkpoint = {
        "schema_version": "work-packet-checkpoint/v2",
        "packet_id": packet_id,
        "packet_contract_sha256": contract_digest,
        "sequence": len(ledger["attempts"]) + 1,
        "snapshots": snapshots,
        "prerequisite_receipts": prerequisites,
    }
    acceptance = {
        "schema_version": "work-packet-acceptance/v2",
        "packet_id": packet_id,
        "packet_contract_sha256": contract_digest,
        "checkpoint_receipt_sha256": execution.canonical_sha256(checkpoint),
        "checks": [
            {
                "check_id": item["check_id"],
                "actual_exit_code": item["actual_exit_code"],
            }
            for item in check_observations
        ],
    }
    execution_receipt = {
        "schema_version": EXECUTION_RECEIPT_SCHEMA,
        "packet_id": packet_id,
        "packet_contract_sha256": contract_digest,
        "checks": check_observations,
    }
    ledger["reported_state"] = "candidate_complete"
    ledger["terminal_completion"] = {
        "authority_kind": "self_reported_local_candidate",
        "packet_contract_sha256": contract_digest,
        "latest_record_sha256": latest["record_sha256"],
        "controlled_claims_sha256": latest["controlled_snapshot"]["claims_sha256"],
        "checkpoint_path": checkpoint_relative,
        "checkpoint_canonical_sha256": execution.canonical_sha256(checkpoint),
        "acceptance_path": acceptance_relative,
        "acceptance_canonical_sha256": execution.canonical_sha256(acceptance),
        "execution_receipt_path": execution_relative,
        "execution_receipt_canonical_sha256": execution.canonical_sha256(
            execution_receipt
        ),
        "completion_seal": None,
    }
    replacements: dict[str, bytes] = {
        packet_path(root, packet_id).relative_to(root).as_posix(): (
            canonical_bytes(packet)
        ),
        execution.ledger_path_for(packet_id): canonical_bytes(ledger),
        checkpoint_relative: canonical_bytes(checkpoint),
        acceptance_relative: canonical_bytes(acceptance),
        execution_relative: canonical_bytes(execution_receipt),
    }
    plan_operation_commit(root, operation, replacements)
    transaction_id = commit_planned_operation(
        root,
        operation,
        crash_after_replacements=crash_after_replacements,
    )
    if crash_after_core_commit:
        raise SimulatedOperationCrash(operation["operation_id"])
    work_receipt = work_packets.verify(
        root,
        root / "governance/WORK_PACKET_POLICY_V2.json",
        root / PACKET_DIRECTORY,
    )
    if work_receipt.get("status") != "pass":
        raise RecorderError(
            "post-finalize work-packet verification failed: "
            + "; ".join(work_receipt.get("errors", []))
        )
    execution_receipt_result = finish_committed_operation(root, operation)
    return {
        "status": "finalized_local_candidate",
        "packet_id": packet_id,
        "transaction_id": transaction_id,
        "latest_record_sha256": latest["record_sha256"],
        "execution_receipt_sha256": execution.canonical_sha256(execution_receipt),
        "work_packet_verification": work_receipt["status"],
        "execution_verification": execution_receipt_result["verification_status"],
        "execution_freshness": execution_receipt_result["execution_freshness_status"],
    }


def resume_finalize_operation(
    root: Path,
    operation: dict[str, Any],
    *,
    crash_after_replacements: int | None = None,
    crash_after_check_prepare: int | None = None,
    crash_after_check_outcome: int | None = None,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    if operation["phase"] in {"commit_planned", "core_committed"}:
        transaction_id = commit_planned_operation(root, operation)
        receipt = finish_committed_operation(root, operation)
        return {
            "status": "recovered_finalization",
            "packet_id": operation["packet_id"],
            "transaction_id": transaction_id,
            "execution_verification": receipt["verification_status"],
            "execution_freshness": receipt["execution_freshness_status"],
        }
    discard_incomplete_commit_preparation(root, operation)
    packet_id = operation["packet_id"]
    packets = load_packets(root)
    packet = packets.get(packet_id)
    if packet is None or packet.get("state") != "active":
        raise RecorderError("finalize recovery requires one active packet")
    ledger = strict_load(ledger_path(root, packet_id), f"ledger {packet_id}")
    require_tail(tail_sha256(ledger), operation["expected_tail"])
    latest = ledger["attempts"][-1]
    if (
        latest["attempt_kind"] != "execution_attempt"
        or latest["blocker"]["status_after"] != "resolved"
        or latest["failure_delta"]["after"] != []
    ):
        raise RecorderError(
            "finalize requires a latest resolved execution attempt with "
            "no remaining failures"
        )
    if operation["phase"] == "prepared":
        set_operation_outcome(
            root,
            operation,
            {
                "next_check_index": 0,
                "checks": [],
                "current_check": None,
            },
        )
    outcome = operation["outcome"]
    if not isinstance(outcome, dict):
        raise RecorderError("finalize operation outcome is missing")
    if operation["phase"] == "check_prepared":
        current = outcome.get("current_check")
        if not isinstance(current, dict):
            raise RecorderError("prepared acceptance check is missing")
        now = utc_datetime_milliseconds()
        started = parse_utc_milliseconds(current["started_at"])
        if now < started:
            now = started
        observation = {
            **indeterminate_process_observation(current["argv"]),
            "started_at": current["started_at"],
            "ended_at": format_utc_milliseconds(now),
            "wall_time_ms": int((now - started).total_seconds() * 1000),
        }
        outcome["current_check"] = None
        operation["phase"] = "outcome_recorded"
        write_operation(root, operation)
        return record_finalize_failure(
            root,
            operation,
            observation,
            "RECORDER-902",
            "RECORDER-INDETERMINATE-OUTCOME",
            "An acceptance-check intent was durable, but its child outcome "
            "was not; finalization is blocked rather than inferred.",
        )

    checks = packet["acceptance_checks"]
    while outcome["next_check_index"] < len(checks):
        index = outcome["next_check_index"]
        check = checks[index]
        _, claims_before = claim_snapshots(root, packet, packets)
        started = utc_datetime_milliseconds()
        started_at = format_utc_milliseconds(started)
        outcome["current_check"] = {
            "index": index,
            "check_id": check["check_id"],
            "argv": check["argv"],
            "started_at": started_at,
            "claims_before_sha256": execution.canonical_sha256(claims_before),
        }
        operation["phase"] = "check_prepared"
        write_operation(root, operation)
        if crash_after_check_prepare == index + 1:
            raise SimulatedOperationCrash(operation["operation_id"])
        completed = subprocess.run(
            check["argv"],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        ended_at, wall_time_ms = observed_interval(started)
        _, claims_after = claim_snapshots(root, packet, packets)
        observation = {
            "check_id": check["check_id"],
            "argv": check["argv"],
            "expected_exit_code": check["expected_exit_code"],
            "actual_exit_code": completed.returncode,
            "started_at": started_at,
            "ended_at": ended_at,
            "wall_time_ms": wall_time_ms,
            "stdout_sha256": raw_sha256(completed.stdout),
            "stderr_sha256": raw_sha256(completed.stderr),
            "stdout_bytes": len(completed.stdout),
            "stderr_bytes": len(completed.stderr),
        }
        envelope = {
            "observation": observation,
            "claims_before_sha256": execution.canonical_sha256(claims_before),
            "claims_after_sha256": execution.canonical_sha256(claims_after),
            "claims_unchanged": claims_after == claims_before,
        }
        outcome["checks"].append(envelope)
        outcome["next_check_index"] = index + 1
        outcome["current_check"] = None
        operation["phase"] = "outcome_recorded"
        write_operation(root, operation)
        if crash_after_check_outcome == index + 1:
            raise SimulatedOperationCrash(operation["operation_id"])
        failure_process = finalize_failure_process_observation(observation)
        if not envelope["claims_unchanged"]:
            return record_finalize_failure(
                root,
                operation,
                failure_process,
                "RECORDER-903",
                "RECORDER-ACCEPTANCE-MUTATION",
                f"Acceptance check {check['check_id']} changed controlled "
                "bytes; completion was rejected.",
            )
        if observation["actual_exit_code"] != observation["expected_exit_code"]:
            return record_finalize_failure(
                root,
                operation,
                failure_process,
                "RECORDER-904",
                "RECORDER-ACCEPTANCE-FAILED",
                f"Acceptance check {check['check_id']} returned an unexpected "
                "exit code; completion was rejected.",
            )
    check_observations = [item["observation"] for item in outcome["checks"]]
    return commit_finalize_candidate(
        root,
        operation,
        packets,
        packet,
        ledger,
        check_observations,
        crash_after_replacements=crash_after_replacements,
        crash_after_core_commit=crash_after_core_commit,
    )


def finalize_packet(
    root: Path,
    packet_id: str,
    expected_tail: str,
    *,
    crash_after_replacements: int | None = None,
    crash_after_check_prepare: int | None = None,
    crash_after_check_outcome: int | None = None,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    with packet_lock(root, "__GLOBAL-OPERATION__"):
        with packet_lock(root, packet_id):
            require_no_pending_transactions(root)
            require_no_pending_operations(root)
            runtime_preflight(root)
            packets = load_packets(root)
            packet = packets.get(packet_id)
            if packet is None or packet.get("state") != "active":
                raise RecorderError("finalize requires one active packet")
            ledger = strict_load(
                ledger_path(root, packet_id),
                f"ledger {packet_id}",
            )
            require_tail(tail_sha256(ledger), expected_tail)
            if ledger.get("terminal_completion") is not None:
                raise RecorderError("packet is already terminal")
            latest = ledger["attempts"][-1]
            if (
                latest["attempt_kind"] != "execution_attempt"
                or latest["blocker"]["status_after"] != "resolved"
                or latest["failure_delta"]["after"] != []
            ):
                raise RecorderError(
                    "finalize requires a latest resolved execution attempt "
                    "with no remaining failures"
                )
            operation = create_operation(
                root,
                packet_id,
                "finalize",
                expected_tail,
                {},
            )
            return resume_finalize_operation(
                root,
                operation,
                crash_after_replacements=crash_after_replacements,
                crash_after_check_prepare=crash_after_check_prepare,
                crash_after_check_outcome=crash_after_check_outcome,
                crash_after_core_commit=crash_after_core_commit,
            )


def require_git_value(
    value: str | None,
    errors: list[str],
) -> str:
    if value is None or errors:
        raise RecorderError("; ".join(errors) or "Git authority is missing")
    return value


def build_completion_seal(
    root: Path,
    packet: dict[str, Any],
    ledger: dict[str, Any],
    candidate_commit: str,
    review_commit: str,
) -> dict[str, Any]:
    packet_id = packet["packet_id"]
    if (
        execution.GIT_OBJECT_RE.fullmatch(candidate_commit) is None
        or execution.GIT_OBJECT_RE.fullmatch(review_commit) is None
        or candidate_commit == review_commit
    ):
        raise RecorderError("candidate and review commits are invalid")
    errors: list[str] = []
    candidate_tree = require_git_value(
        execution.git_object_id(
            root,
            f"{candidate_commit}^{{tree}}",
            "candidate commit tree",
            errors,
        ),
        errors,
    )
    review_tree = require_git_value(
        execution.git_object_id(
            root,
            f"{review_commit}^{{tree}}",
            "review commit tree",
            errors,
        ),
        errors,
    )
    anchor_ref = f"refs/tags/ids-reviewed/{packet_id}"
    anchor_commit = require_git_value(
        execution.git_object_id(
            root,
            anchor_ref,
            "independent review anchor ref",
            errors,
        ),
        errors,
    )
    if anchor_commit != review_commit:
        raise RecorderError("independent review anchor ref differs")
    if (
        execution.git_output(
            root,
            ["merge-base", "--is-ancestor", candidate_commit, review_commit],
            "candidate/review ancestry",
            errors,
        )
        is None
    ):
        raise RecorderError("; ".join(errors))

    packet_relative = f".work_packets/packets/{packet_id}.packet.json"
    ledger_relative = execution.ledger_path_for(packet_id)
    candidate_packet = execution.git_json(
        root,
        candidate_commit,
        packet_relative,
        "candidate packet",
        errors,
    )
    candidate_ledger = execution.git_json(
        root,
        candidate_commit,
        ledger_relative,
        "candidate ledger",
        errors,
    )
    terminal = ledger["terminal_completion"]
    receipt_specs = {
        "checkpoint": terminal["checkpoint_path"],
        "acceptance": terminal["acceptance_path"],
        "execution": terminal["execution_receipt_path"],
    }
    candidate_receipts = {
        name: execution.git_json(
            root,
            candidate_commit,
            relative,
            f"candidate {name} receipt",
            errors,
        )
        for name, relative in receipt_specs.items()
    }
    if errors:
        raise RecorderError("; ".join(errors))
    if candidate_packet != packet or candidate_ledger != ledger:
        raise RecorderError(
            "candidate commit does not exactly contain the current candidate "
            "packet and execution ledger"
        )
    for name, relative in receipt_specs.items():
        current = strict_load(root / relative, f"current {name} receipt")
        if candidate_receipts[name] != current:
            raise RecorderError(
                f"candidate commit {name} receipt differs from current bytes"
            )

    review_path = f".work_packets/reviews/{packet_id}.review.v2.json"
    current_review = strict_load(root / review_path, "independent review")
    committed_review = execution.git_json(
        root,
        review_commit,
        review_path,
        "committed independent review",
        errors,
    )
    if errors:
        raise RecorderError("; ".join(errors))
    if current_review != committed_review:
        raise RecorderError(
            "independent review sidecar differs from its anchored commit"
        )
    if (
        set(current_review) != execution.INDEPENDENT_REVIEW_FIELDS
        or current_review["schema_version"] != "work-packet-independent-review/v2"
        or current_review["packet_id"] != packet_id
        or current_review["candidate_commit"] != candidate_commit
        or current_review["candidate_tree"] != candidate_tree
        or current_review["candidate_terminal_canonical_sha256"]
        != execution.canonical_sha256(terminal)
        or current_review["reviewer_mode"] != "independent_read_only"
        or current_review["verdict"] != "accepted"
        or current_review["findings"] != []
        or not isinstance(current_review["limitations"], list)
        or any(
            not isinstance(item, str) or not item
            for item in current_review["limitations"]
        )
    ):
        raise RecorderError("independent review does not accept this candidate")
    return {
        "schema_version": "execution-completion-seal/v2",
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "candidate_packet_canonical_sha256": execution.canonical_sha256(
            candidate_packet
        ),
        "candidate_ledger_canonical_sha256": execution.canonical_sha256(
            candidate_ledger
        ),
        "candidate_checkpoint_canonical_sha256": (
            execution.canonical_sha256(candidate_receipts["checkpoint"])
        ),
        "candidate_acceptance_canonical_sha256": (
            execution.canonical_sha256(candidate_receipts["acceptance"])
        ),
        "candidate_execution_receipt_canonical_sha256": (
            execution.canonical_sha256(candidate_receipts["execution"])
        ),
        "review_commit": review_commit,
        "review_tree": review_tree,
        "review_path": review_path,
        "review_canonical_sha256": execution.canonical_sha256(current_review),
        "anchor_ref": anchor_ref,
        "anchor_commit": review_commit,
        "anchor_authority": (
            "local_git_ref_content_addressed_not_authenticated_remote"
        ),
    }


def seal_replacements(
    root: Path,
    packet_id: str,
    seal: dict[str, Any],
) -> tuple[dict[str, bytes], dict[str, Any], dict[str, Any]]:
    packets = load_packets(root)
    packet = packets.get(packet_id)
    if packet is None or packet.get("state") != "candidate_complete":
        raise RecorderError("seal requires one candidate_complete packet")
    ledger = strict_load(ledger_path(root, packet_id), f"ledger {packet_id}")
    if (
        ledger.get("reported_state") != "candidate_complete"
        or not isinstance(ledger.get("terminal_completion"), dict)
        or ledger["terminal_completion"].get("completion_seal") is not None
    ):
        raise RecorderError("seal requires one unsealed candidate ledger")
    packet = copy.deepcopy(packet)
    ledger = copy.deepcopy(ledger)
    contract_digest = work_packets.packet_contract_sha256(packet)
    packet["state"] = "complete"
    if work_packets.packet_contract_sha256(packet) != contract_digest:
        raise RecorderError("seal transition changed packet contract")
    ledger["reported_state"] = "complete"
    ledger["terminal_completion"]["authority_kind"] = "git_review_sealed_candidate"
    ledger["terminal_completion"]["completion_seal"] = seal
    errors: list[str] = []
    execution.validate_completion_seal(
        seal,
        ledger["terminal_completion"],
        ledger,
        packet,
        root,
        errors,
    )
    if errors:
        raise RecorderError("completion seal validation failed: " + "; ".join(errors))
    replacements: dict[str, bytes] = {
        packet_path(root, packet_id).relative_to(root).as_posix(): (
            canonical_bytes(packet)
        ),
        execution.ledger_path_for(packet_id): canonical_bytes(ledger),
    }
    complete_after = {
        item_id for item_id, item in packets.items() if item.get("state") == "complete"
    } | {packet_id}
    for successor_id in sorted(packet["activates"]):
        successor = packets[successor_id]
        dependencies_complete = set(successor["depends_on"]).issubset(complete_after)
        if not dependencies_complete:
            if successor.get("state") != "pending":
                raise RecorderError(
                    f"not-yet-activatable successor {successor_id} must remain pending"
                )
            continue
        if successor.get("state") != "pending":
            raise RecorderError(f"activated successor {successor_id} is not pending")
        successor = copy.deepcopy(successor)
        successor["state"] = "active"
        successor_ledger = strict_load(
            ledger_path(root, successor_id),
            f"ledger {successor_id}",
        )
        if (
            successor_ledger.get("reported_state") != "pending"
            or len(successor_ledger.get("attempts", [])) != 1
            or successor_ledger["attempts"][0]["attempt_kind"] != "baseline_observation"
        ):
            raise RecorderError(
                f"activated successor {successor_id} lacks one pending baseline"
            )
        successor_ledger["reported_state"] = "active"
        replacements[packet_path(root, successor_id).relative_to(root).as_posix()] = (
            canonical_bytes(successor)
        )
        replacements[execution.ledger_path_for(successor_id)] = canonical_bytes(
            successor_ledger
        )
    return replacements, packet, ledger


def resume_seal_operation(
    root: Path,
    operation: dict[str, Any],
    *,
    crash_after_replacements: int | None = None,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    if operation["phase"] in {"commit_planned", "core_committed"}:
        transaction_id = commit_planned_operation(root, operation)
        receipt = finish_committed_operation(root, operation)
        return {
            "status": "recovered_seal",
            "packet_id": operation["packet_id"],
            "transaction_id": transaction_id,
            "execution_verification": receipt["verification_status"],
            "execution_freshness": receipt["execution_freshness_status"],
        }
    discard_incomplete_commit_preparation(root, operation)
    packet_id = operation["packet_id"]
    packet = strict_load(packet_path(root, packet_id), f"packet {packet_id}")
    ledger = strict_load(ledger_path(root, packet_id), f"ledger {packet_id}")
    require_tail(tail_sha256(ledger), operation["expected_tail"])
    if operation["phase"] == "prepared":
        request = operation["request"]
        seal = build_completion_seal(
            root,
            packet,
            ledger,
            request["candidate_commit"],
            request["review_commit"],
        )
        set_operation_outcome(root, operation, {"seal": seal})
    outcome = operation["outcome"]
    if (
        operation["phase"] != "outcome_recorded"
        or not isinstance(outcome, dict)
        or not isinstance(outcome.get("seal"), dict)
    ):
        raise RecorderError("seal operation outcome differs")
    replacements, sealed_packet, sealed_ledger = seal_replacements(
        root,
        packet_id,
        outcome["seal"],
    )
    del sealed_packet, sealed_ledger
    plan_operation_commit(root, operation, replacements)
    transaction_id = commit_planned_operation(
        root,
        operation,
        crash_after_replacements=crash_after_replacements,
    )
    if crash_after_core_commit:
        raise SimulatedOperationCrash(operation["operation_id"])
    work_receipt = work_packets.verify(
        root,
        root / "governance/WORK_PACKET_POLICY_V2.json",
        root / PACKET_DIRECTORY,
    )
    if work_receipt.get("status") != "pass":
        raise RecorderError(
            "post-seal work-packet verification failed: "
            + "; ".join(work_receipt.get("errors", []))
        )
    receipt = finish_committed_operation(root, operation)
    return {
        "status": "sealed_complete",
        "packet_id": packet_id,
        "transaction_id": transaction_id,
        "candidate_commit": outcome["seal"]["candidate_commit"],
        "review_commit": outcome["seal"]["review_commit"],
        "execution_verification": receipt["verification_status"],
        "execution_freshness": receipt["execution_freshness_status"],
    }


def seal_packet(
    root: Path,
    packet_id: str,
    expected_tail: str,
    candidate_commit: str,
    review_commit: str,
    *,
    crash_after_replacements: int | None = None,
    crash_after_core_commit: bool = False,
) -> dict[str, Any]:
    with packet_lock(root, "__GLOBAL-OPERATION__"):
        with packet_lock(root, packet_id):
            require_no_pending_transactions(root)
            require_no_pending_operations(root)
            runtime_preflight(root)
            packet = strict_load(
                packet_path(root, packet_id),
                f"packet {packet_id}",
            )
            ledger = strict_load(
                ledger_path(root, packet_id),
                f"ledger {packet_id}",
            )
            require_tail(tail_sha256(ledger), expected_tail)
            if (
                packet.get("state") != "candidate_complete"
                or ledger.get("reported_state") != "candidate_complete"
            ):
                raise RecorderError("seal requires candidate_complete state")
            build_completion_seal(
                root,
                packet,
                ledger,
                candidate_commit,
                review_commit,
            )
            operation = create_operation(
                root,
                packet_id,
                "seal",
                expected_tail,
                {
                    "candidate_commit": candidate_commit,
                    "review_commit": review_commit,
                },
            )
            return resume_seal_operation(
                root,
                operation,
                crash_after_replacements=crash_after_replacements,
                crash_after_core_commit=crash_after_core_commit,
            )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    tail = subparsers.add_parser("tail")
    tail.add_argument("--packet-id", required=True)

    recover = subparsers.add_parser("recover")
    recover.add_argument("--verify", action="store_true")

    for name in ("append", "run"):
        command = subparsers.add_parser(name)
        command.add_argument("--packet-id", required=True)
        command.add_argument("--expected-tail", required=True)
        command.add_argument("--failure-after", action="append")
        command.add_argument(
            "--status-after",
            choices=("open", "resolved", "blocked"),
            required=True,
        )
        command.add_argument("--root-cause-id", required=True)
        command.add_argument("--root-cause", required=True)
        if name == "run":
            command.add_argument("--timeout-seconds", type=float, default=1200)
            command.add_argument("argv", nargs=argparse.REMAINDER)

    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--packet-id", required=True)
    finalize.add_argument("--expected-tail", required=True)
    seal = subparsers.add_parser("seal")
    seal.add_argument("--packet-id", required=True)
    seal.add_argument("--expected-tail", required=True)
    seal.add_argument("--candidate-commit", required=True)
    seal.add_argument("--review-commit", required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        root = args.project_root.resolve(strict=True)
        if args.command_name == "tail":
            ledger = strict_load(
                ledger_path(root, args.packet_id),
                f"ledger {args.packet_id}",
            )
            result = {
                "packet_id": args.packet_id,
                "latest_record_sha256": tail_sha256(ledger),
            }
        elif args.command_name == "recover":
            recovered = recover_operations(root)
            result = {"status": "recovered", "operation_ids": recovered}
            if args.verify:
                result["verification"] = post_write_verify(root)
        elif args.command_name == "append":
            result = append_passive(
                root,
                args.packet_id,
                args.expected_tail,
                args.failure_after,
                args.status_after,
                args.root_cause_id,
                args.root_cause,
            )
        elif args.command_name == "run":
            command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
            result = run_and_append(
                root,
                args.packet_id,
                args.expected_tail,
                command,
                args.failure_after,
                args.status_after,
                args.root_cause_id,
                args.root_cause,
                args.timeout_seconds,
            )
        elif args.command_name == "finalize":
            result = finalize_packet(
                root,
                args.packet_id,
                args.expected_tail,
            )
        else:
            result = seal_packet(
                root,
                args.packet_id,
                args.expected_tail,
                args.candidate_commit,
                args.review_commit,
            )
    except (RecorderError, OSError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "fail", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
