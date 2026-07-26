#!/usr/bin/env python3
"""Append and finalize V2 execution records with locking, CAS, and recovery."""

from __future__ import annotations

import argparse
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
from typing import Any, Iterator


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
EXECUTION_RECEIPT_SCHEMA = "execution-finalization-receipt/v2"
TRANSACTION_ID_RE = re.compile(r"[0-9a-f]{32}")
_LOCAL_LOCKS_GUARD = threading.Lock()
_LOCAL_LOCKS: dict[str, threading.RLock] = {}
_HELD_LOCK_DEPTH = threading.local()


class RecorderError(RuntimeError):
    """Raised when a recorder operation cannot preserve its invariants."""


class SimulatedRecorderCrash(RuntimeError):
    """Test-only interruption after a bounded number of replacements."""


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


def pending_transaction_paths(root: Path) -> list[Path]:
    directory = transaction_root(root)
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise RecorderError("transaction directory must be a real directory")
    return sorted(directory.iterdir(), key=lambda item: item.name)


def require_no_pending_transactions(root: Path) -> None:
    pending = pending_transaction_paths(root)
    if pending:
        raise RecorderError(
            "interrupted transaction requires recovery before new writes: "
            + ", ".join(path.name for path in pending)
        )


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
        transaction_relative = execution.EXPECTED_RECORDER[
            "transaction_directory"
        ]
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
) -> str:
    with packet_lock(root, "__GLOBAL-TRANSACTION__"):
        return _apply_transaction_locked(
            root,
            packet_id,
            replacements,
            crash_after_replacements=crash_after_replacements,
        )


def _apply_transaction_locked(
    root: Path,
    packet_id: str,
    replacements: dict[str, bytes],
    *,
    crash_after_replacements: int | None = None,
) -> str:
    require_no_pending_transactions(root)
    if not replacements:
        raise RecorderError("transaction replacements are empty")
    transaction_id = uuid.uuid4().hex
    directory = transaction_root(root) / transaction_id
    directory.mkdir(parents=True, exist_ok=False)
    fsync_directory(directory.parent)
    records: list[dict[str, Any]] = []
    journal_path = directory / "journal.json"
    journal_written = False
    try:
        for index, (relative, content) in enumerate(sorted(replacements.items())):
            target = normalized_relative(relative, "transaction target")
            transaction_relative = execution.EXPECTED_RECORDER[
                "transaction_directory"
            ]
            if (
                target == transaction_relative
                or target.startswith(f"{transaction_relative}/")
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
        atomic_write(
            journal_path,
            canonical_bytes(
                journal_document(transaction_id, packet_id, records, 0)
            ),
        )
        journal_written = True
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
        journal = validate_journal(root, directory)
        journal_path = directory / "journal.json"
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
    if recovered:
        project_state.refresh_project_state(root)
    return recovered


def runtime_preflight(
    root: Path,
    *,
    allow_stale_packet_id: str | None = None,
) -> dict[str, Any]:
    receipt = execution.verify(
        root,
        POLICY_RELATIVE,
        allow_stale_packet_id=allow_stale_packet_id,
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
            "execution preflight failed: "
            + "; ".join(receipt.get("errors", []))
        )
    return receipt


def post_write_verify(root: Path) -> dict[str, Any]:
    receipt = execution.verify(root, POLICY_RELATIVE)
    if (
        receipt.get("verification_status") != "valid"
        or receipt.get("execution_freshness_status") != "current"
    ):
        raise RecorderError(
            "post-write execution verification failed: "
            + "; ".join(receipt.get("errors", []))
        )
    project_state.refresh_project_state(root)
    project_state.check_project_state(root)
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
                raise RecorderError(
                    f"changed tree {relative} contains a special entry"
                )
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
        item
        for item in after_claims
        if before_map.get(item["path"]) != item
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
            item["path"] == changed
            or item["path"].startswith(f"{changed}/")
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
            >= execution.EXPECTED_STOPPING[
                "consecutive_no_progress_threshold"
            ]
            or same
            >= execution.EXPECTED_STOPPING[
                "same_blocker_consecutive_no_progress_threshold"
            ]
        ):
            return True
    return False


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
) -> dict[str, Any]:
    with packet_lock(root, packet_id):
        require_no_pending_transactions(root)
        runtime_preflight(root, allow_stale_packet_id=packet_id)
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
            {
                key: value
                for key, value in attempt.items()
                if key != "record_sha256"
            }
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
            replacements[
                packet_path(root, packet_id).relative_to(root).as_posix()
            ] = canonical_bytes(packet)
        transaction_id = apply_transaction(
            root,
            packet_id,
            replacements,
            crash_after_replacements=crash_after_replacements,
        )
        receipt = post_write_verify(root)
        return {
            "status": "recorded",
            "packet_id": packet_id,
            "transaction_id": transaction_id,
            "latest_record_sha256": ledger["attempts"][-1]["record_sha256"],
            "process_exit_code": process_observation["exit_code"],
            "execution_verification": receipt["verification_status"],
            "execution_freshness": receipt["execution_freshness_status"],
        }


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
) -> dict[str, Any]:
    if not command or any(not item for item in command):
        raise RecorderError("run mode requires a non-empty argv")
    with packet_lock(root, packet_id):
        require_no_pending_transactions(root)
        runtime_preflight(root)
        ledger = strict_load(ledger_path(root, packet_id), f"ledger {packet_id}")
        require_tail(tail_sha256(ledger), expected_tail)
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
        return append_observation(
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
        )


def receipt_value(root: Path, relative: str, label: str) -> dict[str, Any]:
    path = project_file(root, relative, label)
    return strict_load(path, label)


def finalize_packet(
    root: Path,
    packet_id: str,
    expected_tail: str,
    *,
    crash_after_replacements: int | None = None,
) -> dict[str, Any]:
    with packet_lock(root, packet_id):
        require_no_pending_transactions(root)
        runtime_preflight(root)
        packets = load_packets(root)
        packet = packets.get(packet_id)
        if packet is None or packet.get("state") != "active":
            raise RecorderError("finalize requires one active packet")
        ledger = strict_load(ledger_path(root, packet_id), f"ledger {packet_id}")
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
                "finalize requires a latest resolved execution attempt with "
                "no remaining failures"
            )

        check_observations: list[dict[str, Any]] = []
        for check in packet["acceptance_checks"]:
            started = utc_datetime_milliseconds()
            started_at = format_utc_milliseconds(started)
            completed = subprocess.run(
                check["argv"],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            ended_at, wall_time_ms = observed_interval(started)
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
            check_observations.append(observation)
        failed = [
            item
            for item in check_observations
            if item["actual_exit_code"] != item["expected_exit_code"]
        ]
        if failed:
            raise RecorderError(
                "acceptance checks failed: "
                + ", ".join(item["check_id"] for item in failed)
            )

        contract_digest = work_packets.packet_contract_sha256(packet)
        checkpoint_relative = (
            f".work_packets/receipts/{packet_id}.checkpoint.json"
        )
        acceptance_relative = (
            f".work_packets/receipts/{packet_id}.acceptance.json"
        )
        execution_relative = (
            f".work_packets/receipts/{packet_id}.execution.v2.json"
        )
        packet["checkpoint_path"] = checkpoint_relative
        packet["acceptance_receipt_path"] = acceptance_relative
        packet["state"] = "complete"
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
        ledger["reported_state"] = "complete"
        ledger["terminal_completion"] = {
            "authority_kind": "self_reported_local_candidate",
            "packet_contract_sha256": contract_digest,
            "latest_record_sha256": latest["record_sha256"],
            "controlled_claims_sha256": latest["controlled_snapshot"][
                "claims_sha256"
            ],
            "checkpoint_path": checkpoint_relative,
            "checkpoint_canonical_sha256": execution.canonical_sha256(
                checkpoint
            ),
            "acceptance_path": acceptance_relative,
            "acceptance_canonical_sha256": execution.canonical_sha256(
                acceptance
            ),
            "execution_receipt_path": execution_relative,
            "execution_receipt_canonical_sha256": execution.canonical_sha256(
                execution_receipt
            ),
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
        complete_after = {
            item_id
            for item_id, item in packets.items()
            if item.get("state") == "complete"
        } | {packet_id}
        for successor_id in sorted(packet["activates"]):
            successor = packets[successor_id]
            if successor.get("state") != "pending":
                raise RecorderError(
                    f"activated successor {successor_id} is not pending"
                )
            if not set(successor["depends_on"]).issubset(complete_after):
                raise RecorderError(
                    f"activated successor {successor_id} has incomplete dependencies"
                )
            successor["state"] = "active"
            successor_ledger = strict_load(
                ledger_path(root, successor_id),
                f"ledger {successor_id}",
            )
            if (
                successor_ledger.get("reported_state") != "pending"
                or len(successor_ledger.get("attempts", [])) != 1
                or successor_ledger["attempts"][0]["attempt_kind"]
                != "baseline_observation"
            ):
                raise RecorderError(
                    f"activated successor {successor_id} lacks one pending baseline"
                )
            successor_ledger["reported_state"] = "active"
            replacements[
                packet_path(root, successor_id).relative_to(root).as_posix()
            ] = canonical_bytes(successor)
            replacements[
                execution.ledger_path_for(successor_id)
            ] = canonical_bytes(successor_ledger)

        transaction_id = apply_transaction(
            root,
            packet_id,
            replacements,
            crash_after_replacements=crash_after_replacements,
        )
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
        execution_receipt_result = post_write_verify(root)
        return {
            "status": "finalized_local_candidate",
            "packet_id": packet_id,
            "transaction_id": transaction_id,
            "latest_record_sha256": latest["record_sha256"],
            "execution_receipt_sha256": execution.canonical_sha256(
                execution_receipt
            ),
            "work_packet_verification": work_receipt["status"],
            "execution_verification": execution_receipt_result[
                "verification_status"
            ],
            "execution_freshness": execution_receipt_result[
                "execution_freshness_status"
            ],
        }


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
            recovered = recover_transactions(root)
            result = {"status": "recovered", "transaction_ids": recovered}
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
        else:
            result = finalize_packet(
                root,
                args.packet_id,
                args.expected_tail,
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
