#!/usr/bin/env python3
"""Execute and verify the isolated ECO-04 migration/rollback/exit drill."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
DEFAULT_SPEC_PATH = PROJECT_ROOT / "governance" / "MIGRATION_DRILL_SPEC_V1.json"

MECHANISM_ID = "ECO-04-WORK-PACKET-MIGRATION-DRILL-V1"
FAILURE_ID = "ECO-04"
REQUIREMENT_ID = "REQ-METHOD-001"
CASE_ID = "CASE-METHOD-RENAME-REWRITE"
SOURCE_VERSION = "work-packet-instance/v1"
TARGET_VERSION = "work-packet-instance/v2-drill"
EXPECTED_SPEC_SHA256 = (
    "118115fe49f91070a9d7efc634c67186552736b2f3e08ac7f0f236f81841d83a"
)

FAULT_MODES = (
    "none",
    "semantic_loss",
    "skip_backup",
    "partial_write_on_failure",
    "rollback_drift",
    "source_version_mismatch",
    "non_idempotent_repeat",
)

SOURCE_KEYS = {
    "schema_version",
    "packet_id",
    "goal_id",
    "state",
    "owner",
    "reviewer",
    "bounded_write_paths",
    "read_dependencies",
    "acceptance_checks",
    "checkpoint_path",
    "acceptance_receipt_path",
    "retry_budget",
    "external_side_effects",
    "semantic_invariants",
}
TARGET_KEYS = {
    "schema_version",
    "identity",
    "lifecycle",
    "authority",
    "scope",
    "verification",
    "migration",
}
STATE_VALUES = {
    "pending",
    "active",
    "blocked",
    "candidate_complete",
    "complete",
}
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")

CLAIM_BOUNDARY = {
    "allowed_claim": (
        "This verifier executed one isolated work-packet v1 to v2-drill "
        "migration with a no-write dry run, exact backup, a pre-replace "
        "failure, semantic comparison, explicit incompatibility, deterministic "
        "replay, idempotent repeat, exact rollback, and guarded writes."
    ),
    "forbidden_claim": (
        "This fixture does not prove every future schema, production database "
        "migration, concurrent writer protocol, filesystem crash model, or "
        "long-term exit cost."
    ),
}


class DuplicateKeyError(ValueError):
    """Raised when strict JSON encounters the same key twice."""


class DrillFailure(RuntimeError):
    """A fail-closed migration-drill failure with a stable oracle identifier."""

    def __init__(self, oracle_id: str, message: str) -> None:
        super().__init__(message)
        self.oracle_id = oracle_id
        self.message = message


class InjectedPreReplaceFailure(RuntimeError):
    """Expected interruption after candidate fsync and before replacement."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def parse_strict_json_bytes(raw: bytes, label: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        raise DrillFailure(
            "ECO04-STRICT-JSON", f"{label} is not strict JSON: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise DrillFailure(
            "ECO04-STRICT-JSON", f"{label} top-level value must be an object"
        )
    return value


def read_strict_json(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise DrillFailure("ECO04-READ", f"cannot read {label}: {exc}") from exc
    return parse_strict_json_bytes(raw, label), raw


def add_error(
    errors: list[dict[str, str]], oracle_id: str, message: str
) -> None:
    candidate = {"oracle_id": oracle_id, "message": message}
    if candidate not in errors:
        errors.append(candidate)


def exact_keys(
    value: Any, expected: set[str], label: str, messages: list[str]
) -> bool:
    if not isinstance(value, dict):
        messages.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        messages.append(
            f"{label} keys differ: missing={sorted(expected - actual)!r} "
            f"extra={sorted(actual - expected)!r}"
        )
        return False
    return True


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_plain_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_source_record(record: Any) -> list[str]:
    messages: list[str] = []
    if not exact_keys(record, SOURCE_KEYS, "source record", messages):
        return messages
    if record["schema_version"] != SOURCE_VERSION:
        messages.append(
            f"source schema_version must be {SOURCE_VERSION!r}, got "
            f"{record['schema_version']!r}"
        )
    for field_name in ("packet_id", "goal_id", "owner", "reviewer"):
        if not is_nonempty_string(record[field_name]):
            messages.append(f"source {field_name} must be a non-empty string")
    if record["state"] not in STATE_VALUES:
        messages.append("source state is unsupported")
    if (
        not is_plain_int(record["retry_budget"])
        or record["retry_budget"] < 0
    ):
        messages.append("source retry_budget must be a non-negative integer")

    writes = record["bounded_write_paths"]
    if not isinstance(writes, list) or not writes:
        messages.append("source bounded_write_paths must be a non-empty list")
    else:
        seen_paths: set[str] = set()
        for index, claim in enumerate(writes):
            label = f"source bounded_write_paths[{index}]"
            if not exact_keys(claim, {"path", "kind"}, label, messages):
                continue
            path = claim["path"]
            if not is_nonempty_string(path) or Path(path).is_absolute():
                messages.append(f"{label}.path must be a relative non-empty path")
            elif path in seen_paths:
                messages.append(f"{label}.path is duplicated")
            else:
                seen_paths.add(path)
            if claim["kind"] not in {"file", "directory"}:
                messages.append(f"{label}.kind is unsupported")

    for field_name in (
        "read_dependencies",
        "external_side_effects",
        "semantic_invariants",
    ):
        if not isinstance(record[field_name], list):
            messages.append(f"source {field_name} must be a list")
    if isinstance(record["read_dependencies"], list) and not all(
        is_nonempty_string(item) for item in record["read_dependencies"]
    ):
        messages.append("source read_dependencies entries must be non-empty strings")
    if isinstance(record["external_side_effects"], list) and not all(
        is_nonempty_string(item) for item in record["external_side_effects"]
    ):
        messages.append(
            "source external_side_effects entries must be non-empty strings"
        )

    checks = record["acceptance_checks"]
    if not isinstance(checks, list) or not checks:
        messages.append("source acceptance_checks must be a non-empty list")
    else:
        for index, check in enumerate(checks):
            label = f"source acceptance_checks[{index}]"
            if not exact_keys(
                check,
                {"check_id", "kind", "argv", "expected_exit_code"},
                label,
                messages,
            ):
                continue
            if not is_nonempty_string(check["check_id"]):
                messages.append(f"{label}.check_id must be non-empty")
            if check["kind"] != "process_exit":
                messages.append(f"{label}.kind must be process_exit")
            if not isinstance(check["argv"], list) or not check["argv"] or not all(
                is_nonempty_string(item) for item in check["argv"]
            ):
                messages.append(f"{label}.argv must be a non-empty string list")
            if not is_plain_int(check["expected_exit_code"]):
                messages.append(f"{label}.expected_exit_code must be an integer")

    for field_name in ("checkpoint_path", "acceptance_receipt_path"):
        value = record[field_name]
        if value is not None and not is_nonempty_string(value):
            messages.append(f"source {field_name} must be null or non-empty string")
    return messages


def validate_target_record(
    record: Any, expected_source_sha256: str | None = None
) -> list[str]:
    messages: list[str] = []
    if not exact_keys(record, TARGET_KEYS, "target record", messages):
        return messages
    if record["schema_version"] != TARGET_VERSION:
        messages.append("target schema_version is wrong")
    nested_contracts = {
        "identity": {"packet_id", "goal_id"},
        "lifecycle": {"state", "retry_budget"},
        "authority": {"owner", "reviewer"},
        "scope": {
            "bounded_write_paths",
            "read_dependencies",
            "external_side_effects",
        },
        "verification": {
            "acceptance_checks",
            "checkpoint_path",
            "acceptance_receipt_path",
            "semantic_invariants",
        },
        "migration": {
            "source_version",
            "target_version",
            "compatibility",
            "source_sha256",
        },
    }
    for field_name, keys in nested_contracts.items():
        exact_keys(record[field_name], keys, f"target {field_name}", messages)
    if messages:
        return messages
    if record["migration"]["source_version"] != SOURCE_VERSION:
        messages.append("target migration.source_version is wrong")
    if record["migration"]["target_version"] != TARGET_VERSION:
        messages.append("target migration.target_version is wrong")
    if record["migration"]["compatibility"] != "explicit_break":
        messages.append("target compatibility must be explicit_break")
    source_hash = record["migration"]["source_sha256"]
    if not isinstance(source_hash, str) or HEX_SHA256.fullmatch(source_hash) is None:
        messages.append("target migration.source_sha256 is not SHA-256")
    elif expected_source_sha256 is not None and source_hash != expected_source_sha256:
        messages.append("target migration.source_sha256 differs from exact source bytes")
    reconstructed = {
        "schema_version": record["migration"]["source_version"],
        "packet_id": record["identity"]["packet_id"],
        "goal_id": record["identity"]["goal_id"],
        "state": record["lifecycle"]["state"],
        "owner": record["authority"]["owner"],
        "reviewer": record["authority"]["reviewer"],
        "bounded_write_paths": record["scope"]["bounded_write_paths"],
        "read_dependencies": record["scope"]["read_dependencies"],
        "acceptance_checks": record["verification"]["acceptance_checks"],
        "checkpoint_path": record["verification"]["checkpoint_path"],
        "acceptance_receipt_path": record["verification"][
            "acceptance_receipt_path"
        ],
        "retry_budget": record["lifecycle"]["retry_budget"],
        "external_side_effects": record["scope"]["external_side_effects"],
        "semantic_invariants": record["verification"]["semantic_invariants"],
    }
    source_messages = validate_source_record(reconstructed)
    messages.extend(f"reconstructed {message}" for message in source_messages)
    return messages


def source_reader_accepts(record: Any) -> bool:
    return not validate_source_record(record)


def target_reader_accepts(record: Any, source_sha256: str | None = None) -> bool:
    return not validate_target_record(record, source_sha256)


def json_pointer(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise DrillFailure(
            "ECO04-SPEC-CONTRACT", f"invalid JSON pointer {pointer!r}"
        )
    current = value
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdecimal():
            index = int(token)
            if index >= len(current):
                raise DrillFailure(
                    "ECO04-SEMANTIC-INVARIANT",
                    f"pointer {pointer!r} list index is out of range",
                )
            current = current[index]
        else:
            raise DrillFailure(
                "ECO04-SEMANTIC-INVARIANT",
                f"pointer {pointer!r} does not resolve",
            )
    return current


def semantic_observations(
    source: dict[str, Any],
    target: dict[str, Any],
    invariants: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for invariant in invariants:
        source_value = json_pointer(source, invariant["source_pointer"])
        target_value = json_pointer(target, invariant["target_pointer"])
        equal = source_value == target_value
        observations.append(
            {
                "invariant_id": invariant["invariant_id"],
                "comparison": invariant["comparison"],
                "preserved": equal,
                "source_value_sha256": sha256_bytes(
                    canonical_json_bytes(source_value)
                ),
                "target_value_sha256": sha256_bytes(
                    canonical_json_bytes(target_value)
                ),
            }
        )
    return observations


def transform_source(
    source: dict[str, Any], source_raw: bytes, semantic_loss: bool = False
) -> dict[str, Any]:
    target = {
        "schema_version": TARGET_VERSION,
        "identity": {
            "packet_id": copy.deepcopy(source["packet_id"]),
            "goal_id": copy.deepcopy(source["goal_id"]),
        },
        "lifecycle": {
            "state": copy.deepcopy(source["state"]),
            "retry_budget": copy.deepcopy(source["retry_budget"]),
        },
        "authority": {
            "owner": copy.deepcopy(source["owner"]),
            "reviewer": copy.deepcopy(source["reviewer"]),
        },
        "scope": {
            "bounded_write_paths": copy.deepcopy(source["bounded_write_paths"]),
            "read_dependencies": copy.deepcopy(source["read_dependencies"]),
            "external_side_effects": copy.deepcopy(
                source["external_side_effects"]
            ),
        },
        "verification": {
            "acceptance_checks": copy.deepcopy(source["acceptance_checks"]),
            "checkpoint_path": copy.deepcopy(source["checkpoint_path"]),
            "acceptance_receipt_path": copy.deepcopy(
                source["acceptance_receipt_path"]
            ),
            "semantic_invariants": copy.deepcopy(source["semantic_invariants"]),
        },
        "migration": {
            "source_version": SOURCE_VERSION,
            "target_version": TARGET_VERSION,
            "compatibility": "explicit_break",
            "source_sha256": sha256_bytes(source_raw),
        },
    }
    if semantic_loss:
        # A plausible rename-only bug: both role labels survive, but the
        # independent reviewer authority is silently replaced by the owner.
        target["authority"]["reviewer"] = source["owner"]
    return target


def validate_spec(spec: dict[str, Any], raw: bytes) -> list[str]:
    messages: list[str] = []
    if sha256_bytes(raw) != EXPECTED_SPEC_SHA256:
        messages.append("spec bytes differ from the frozen migration-drill spec")
    expected_top_keys = {
        "schema_version",
        "mechanism_id",
        "failure_id",
        "requirement_id",
        "case_id",
        "record_family",
        "source_version",
        "target_version",
        "source_fixture",
        "migration_contract",
        "semantic_invariants",
        "compatibility_contract",
        "backup_contract",
        "failure_atomicity_contract",
        "rollback_contract",
        "repeat_run_contract",
        "project_isolation_contract",
        "exit_plan",
        "claim_boundary",
    }
    exact_keys(spec, expected_top_keys, "migration drill spec", messages)
    expected_scalars = {
        "schema_version": "migration-drill-spec/v1",
        "mechanism_id": MECHANISM_ID,
        "failure_id": FAILURE_ID,
        "requirement_id": REQUIREMENT_ID,
        "case_id": CASE_ID,
        "record_family": "work_packet",
        "source_version": SOURCE_VERSION,
        "target_version": TARGET_VERSION,
    }
    for field_name, expected in expected_scalars.items():
        if spec.get(field_name) != expected:
            messages.append(f"spec {field_name} differs from the frozen contract")
    source_fixture = spec.get("source_fixture")
    messages.extend(validate_source_record(source_fixture))
    invariants = spec.get("semantic_invariants")
    if not isinstance(invariants, list) or len(invariants) != 14:
        messages.append("spec must declare exactly fourteen semantic invariants")
    else:
        seen_ids: set[str] = set()
        seen_pairs: set[tuple[str, str]] = set()
        for index, invariant in enumerate(invariants):
            label = f"semantic_invariants[{index}]"
            if not exact_keys(
                invariant,
                {
                    "invariant_id",
                    "source_pointer",
                    "target_pointer",
                    "comparison",
                },
                label,
                messages,
            ):
                continue
            invariant_id = invariant["invariant_id"]
            if not is_nonempty_string(invariant_id) or invariant_id in seen_ids:
                messages.append(f"{label}.invariant_id is invalid or duplicated")
            else:
                seen_ids.add(invariant_id)
            pair = (invariant["source_pointer"], invariant["target_pointer"])
            if pair in seen_pairs:
                messages.append(f"{label} duplicates a semantic mapping")
            else:
                seen_pairs.add(pair)
            if invariant["comparison"] != "deep_equal":
                messages.append(f"{label}.comparison must be deep_equal")
    compatibility = spec.get("compatibility_contract")
    if not isinstance(compatibility, dict) or compatibility.get("mode") != (
        "explicit_break"
    ):
        messages.append("compatibility contract must declare explicit_break")
    isolation = spec.get("project_isolation_contract")
    if not isinstance(isolation, dict) or not isinstance(
        isolation.get("protected_project_paths"), list
    ):
        messages.append("project isolation protected paths are missing")
    return messages


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@dataclass
class MutationAudit:
    sandbox_root: Path
    events: list[dict[str, Any]] = field(default_factory=list)
    sequence: int = 0

    def guarded(self, path: Path) -> Path:
        resolved = path.resolve(strict=False)
        if not is_within(resolved, self.sandbox_root):
            raise DrillFailure(
                "ECO04-PROJECT-ISOLATION",
                f"refused mutation outside sandbox: {resolved}",
            )
        return resolved

    def record(self, operation: str, path: Path) -> None:
        self.sequence += 1
        relative = self.guarded(path).relative_to(self.sandbox_root).as_posix()
        self.events.append(
            {"sequence": self.sequence, "operation": operation, "path": relative}
        )

    def ensure_directory(self, path: Path) -> None:
        resolved = self.guarded(path)
        missing: list[Path] = []
        cursor = resolved
        while cursor != self.sandbox_root and not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        resolved.mkdir(parents=True, exist_ok=True)
        for created in reversed(missing):
            self.record("mkdir", created)

    def write_new(self, path: Path, raw: bytes, operation: str) -> None:
        resolved = self.guarded(path)
        self.ensure_directory(resolved.parent)
        try:
            with resolved.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError as exc:
            raise DrillFailure(
                "ECO04-NO-OVERWRITE", f"refused to overwrite {resolved.name}"
            ) from exc
        fsync_directory(resolved.parent)
        self.record(operation, resolved)

    def replace_bytes(
        self,
        path: Path,
        raw: bytes,
        operation: str,
        inject_before_replace: bool = False,
    ) -> None:
        resolved = self.guarded(path)
        candidate = resolved.with_name(resolved.name + ".migration-candidate")
        self.write_new(candidate, raw, operation + "_candidate_fsync")
        if inject_before_replace:
            candidate.unlink()
            fsync_directory(candidate.parent)
            self.record(operation + "_candidate_removed", candidate)
            raise InjectedPreReplaceFailure(
                "injected after candidate fsync and before replace"
            )
        os.replace(candidate, resolved)
        fsync_directory(resolved.parent)
        self.record(operation + "_replace", resolved)

    def broken_partial_write(self, path: Path, raw: bytes) -> None:
        resolved = self.guarded(path)
        with resolved.open("wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        fsync_directory(resolved.parent)
        self.record("broken_partial_write", resolved)


def snapshot_paths(project_root: Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for relative in relative_paths:
        if not is_nonempty_string(relative) or Path(relative).is_absolute():
            raise DrillFailure(
                "ECO04-SPEC-CONTRACT",
                f"protected project path is not relative: {relative!r}",
            )
        path = project_root / relative
        if path.is_symlink() or not path.is_file():
            raise DrillFailure(
                "ECO04-PROJECT-SENTINEL",
                f"protected project path is not an exact regular file: {relative}",
            )
        raw = path.read_bytes()
        manifest.append(
            {
                "path": relative,
                "kind": "regular_file",
                "size": len(raw),
                "sha256": sha256_bytes(raw),
            }
        )
    return manifest


def sandbox_manifest(root: Path) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            manifest.append(
                {"path": relative, "kind": "symlink", "target": os.readlink(path)}
            )
        elif path.is_file():
            raw = path.read_bytes()
            manifest.append(
                {
                    "path": relative,
                    "kind": "regular_file",
                    "size": len(raw),
                    "sha256": sha256_bytes(raw),
                }
            )
        elif path.is_dir():
            manifest.append({"path": relative, "kind": "directory"})
    return manifest


def project_tree_manifest(
    project_root: Path, excluded_components: set[str]
) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    try:
        paths = sorted(project_root.rglob("*"))
    except OSError as exc:
        raise DrillFailure(
            "ECO04-PROJECT-MANIFEST",
            f"cannot enumerate project tree: {exc}",
        ) from exc
    for path in paths:
        relative_path = path.relative_to(project_root)
        if any(part in excluded_components for part in relative_path.parts):
            continue
        relative = relative_path.as_posix()
        try:
            if path.is_symlink():
                manifest.append(
                    {
                        "path": relative,
                        "kind": "symlink",
                        "target": os.readlink(path),
                    }
                )
            elif path.is_file():
                raw = path.read_bytes()
                manifest.append(
                    {
                        "path": relative,
                        "kind": "regular_file",
                        "size": len(raw),
                        "sha256": sha256_bytes(raw),
                    }
                )
            elif path.is_dir():
                manifest.append({"path": relative, "kind": "directory"})
            else:
                raise DrillFailure(
                    "ECO04-PROJECT-MANIFEST",
                    f"unsupported project-tree entry type: {relative}",
                )
        except OSError as exc:
            raise DrillFailure(
                "ECO04-PROJECT-MANIFEST",
                f"cannot inspect project-tree entry {relative}: {exc}",
            ) from exc
    return manifest


def verify_backup(
    backup_path: Path, sidecar_path: Path, source_raw: bytes
) -> dict[str, Any]:
    if (
        backup_path.is_symlink()
        or sidecar_path.is_symlink()
        or not backup_path.is_file()
        or not sidecar_path.is_file()
    ):
        raise DrillFailure(
            "ECO04-BACKUP-REQUIRED", "exact backup and hash sidecar are required"
        )
    backup_raw = backup_path.read_bytes()
    expected_hash = sha256_bytes(source_raw)
    try:
        sidecar = sidecar_path.read_text(encoding="ascii", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise DrillFailure(
            "ECO04-BACKUP-HASH", f"backup hash sidecar is unreadable: {exc}"
        ) from exc
    if backup_raw != source_raw:
        raise DrillFailure(
            "ECO04-BACKUP-BYTES", "backup bytes differ from exact source bytes"
        )
    if sidecar != expected_hash + "\n":
        raise DrillFailure(
            "ECO04-BACKUP-HASH", "backup hash sidecar does not bind source bytes"
        )
    return {
        "created": True,
        "exact_bytes": True,
        "sha256": expected_hash,
        "sidecar_verified": True,
    }


def create_backup(
    audit: MutationAudit,
    source_raw: bytes,
    backup_path: Path,
    sidecar_path: Path,
) -> dict[str, Any]:
    source_hash = sha256_bytes(source_raw)
    audit.write_new(backup_path, source_raw, "backup_exact_source")
    audit.write_new(
        sidecar_path,
        (source_hash + "\n").encode("ascii"),
        "backup_hash_sidecar",
    )
    return verify_backup(backup_path, sidecar_path, source_raw)


def transactional_migrate(
    audit: MutationAudit,
    record_path: Path,
    backup_path: Path,
    sidecar_path: Path,
    invariants: list[dict[str, Any]],
    *,
    semantic_loss: bool = False,
    inject_before_replace: bool = False,
) -> tuple[str, bytes, list[dict[str, Any]]]:
    current, current_raw = read_strict_json(record_path, "active record")
    version = current.get("schema_version")
    if version == TARGET_VERSION:
        target_messages = validate_target_record(
            current, current.get("migration", {}).get("source_sha256")
        )
        if target_messages:
            raise DrillFailure(
                "ECO04-TARGET-SCHEMA",
                "; ".join(target_messages),
            )
        return "already_at_target", current_raw, []
    if version != SOURCE_VERSION:
        raise DrillFailure(
            "ECO04-SOURCE-VERSION",
            f"expected {SOURCE_VERSION!r}, got {version!r}; no write performed",
        )
    source_messages = validate_source_record(current)
    if source_messages:
        raise DrillFailure("ECO04-SOURCE-SCHEMA", "; ".join(source_messages))
    verify_backup(backup_path, sidecar_path, current_raw)
    target = transform_source(current, current_raw, semantic_loss=semantic_loss)
    target_messages = validate_target_record(target, sha256_bytes(current_raw))
    if target_messages:
        raise DrillFailure("ECO04-TARGET-SCHEMA", "; ".join(target_messages))
    observations = semantic_observations(current, target, invariants)
    if not all(item["preserved"] for item in observations):
        failed = [
            item["invariant_id"]
            for item in observations
            if not item["preserved"]
        ]
        raise DrillFailure(
            "ECO04-SEMANTIC-INVARIANT",
            f"migration lost semantics for {failed!r}; no target commit allowed",
        )
    target_raw = canonical_json_bytes(target)
    audit.replace_bytes(
        record_path,
        target_raw,
        "migration",
        inject_before_replace=inject_before_replace,
    )
    return "migrated", target_raw, observations


def transactional_rollback(
    audit: MutationAudit,
    record_path: Path,
    backup_path: Path,
    sidecar_path: Path,
    source_raw: bytes,
    *,
    rollback_drift: bool = False,
) -> bytes:
    verify_backup(backup_path, sidecar_path, source_raw)
    restore_raw = backup_path.read_bytes()
    if rollback_drift:
        restore_record = parse_strict_json_bytes(restore_raw, "backup")
        restore_raw = pretty_json_bytes(restore_record)
    audit.replace_bytes(record_path, restore_raw, "rollback")
    return record_path.read_bytes()


def compatibility_observation(
    source: dict[str, Any], target: dict[str, Any], source_hash: str
) -> dict[str, Any]:
    return {
        "mode": "explicit_break",
        "source_reader_accepts_source": source_reader_accepts(source),
        "source_reader_accepts_target": source_reader_accepts(target),
        "target_reader_accepts_source": target_reader_accepts(source, source_hash),
        "target_reader_accepts_target": target_reader_accepts(target, source_hash),
        "break_is_explicit_and_enforced": (
            source_reader_accepts(source)
            and not source_reader_accepts(target)
            and not target_reader_accepts(source, source_hash)
            and target_reader_accepts(target, source_hash)
        ),
    }


def execute_drill(
    project_root: Path,
    spec: dict[str, Any],
    fault_mode: str,
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    protected_paths = spec["project_isolation_contract"][
        "protected_project_paths"
    ]
    excluded_components = set(
        spec["project_isolation_contract"]["excluded_path_components"]
    )
    before_project = snapshot_paths(project_root, protected_paths)
    before_project_tree = project_tree_manifest(project_root, excluded_components)
    observation: dict[str, Any] = {
        "source_version": SOURCE_VERSION,
        "target_version": TARGET_VERSION,
        "source_sha256": None,
        "target_sha256": None,
        "backup": {
            "created": False,
            "exact_bytes": False,
            "sha256": None,
            "sidecar_verified": False,
            "precedes_first_replace": False,
        },
        "dry_run": {"executed": False, "no_write": False},
        "failure_injection": {
            "stage": "after_candidate_fsync_before_replace",
            "executed": False,
            "source_preserved": False,
            "candidate_removed": False,
        },
        "semantic_invariants": [],
        "compatibility": {},
        "migration": {"status": "not_run"},
        "repeat_run": {
            "status": "not_run",
            "bytes_unchanged": False,
            "sha256_unchanged": False,
        },
        "rollback": {
            "status": "not_run",
            "exact_bytes": False,
            "exact_sha256": False,
            "source_reader_accepts": False,
        },
        "determinism": {
            "pure_transform_equal": False,
            "second_migration_equal": False,
        },
        "exit": {"restored_source_exact": False},
        "project_isolation": {
            "sandbox_outside_project": False,
            "all_audited_mutations_under_sandbox": False,
            "real_project_write_count": None,
            "protected_manifest_before": before_project,
            "protected_manifest_after": [],
            "protected_manifest_unchanged": False,
            "full_tree_manifest_before_sha256": sha256_bytes(
                canonical_json_bytes(before_project_tree)
            ),
            "full_tree_manifest_after_sha256": None,
            "full_tree_manifest_unchanged": False,
            "audited_mutations": [],
        },
    }

    try:
        with tempfile.TemporaryDirectory(
            prefix="ids-eco04-migration-drill-"
        ) as temporary_name:
            sandbox = Path(temporary_name).resolve()
            outside = not is_within(sandbox, project_root) and not is_within(
                project_root, sandbox
            )
            observation["project_isolation"]["sandbox_outside_project"] = outside
            if not outside:
                raise DrillFailure(
                    "ECO04-PROJECT-ISOLATION",
                    "temporary drill directory overlaps the project root",
                )
            audit = MutationAudit(sandbox)
            record_path = sandbox / "state" / "current.packet.json"
            backup_path = sandbox / spec["backup_contract"]["backup_path"]
            sidecar_path = sandbox / spec["backup_contract"]["hash_sidecar_path"]

            source_fixture = copy.deepcopy(spec["source_fixture"])
            if fault_mode == "source_version_mismatch":
                source_fixture["schema_version"] = "work-packet-instance/v0"
            source_raw = canonical_json_bytes(source_fixture)
            audit.write_new(record_path, source_raw, "initialize_source_fixture")
            observation["source_sha256"] = sha256_bytes(source_raw)

            if source_fixture.get("schema_version") != SOURCE_VERSION:
                raise DrillFailure(
                    "ECO04-SOURCE-VERSION",
                    f"expected {SOURCE_VERSION!r}, got "
                    f"{source_fixture.get('schema_version')!r}; no migration allowed",
                )
            source_messages = validate_source_record(source_fixture)
            if source_messages:
                raise DrillFailure(
                    "ECO04-SOURCE-SCHEMA", "; ".join(source_messages)
                )

            dry_before = sandbox_manifest(sandbox)
            dry_target = transform_source(
                source_fixture,
                source_raw,
                semantic_loss=fault_mode == "semantic_loss",
            )
            dry_observations = semantic_observations(
                source_fixture, dry_target, spec["semantic_invariants"]
            )
            dry_after = sandbox_manifest(sandbox)
            observation["dry_run"] = {
                "executed": True,
                "no_write": dry_before == dry_after,
            }
            observation["semantic_invariants"] = dry_observations
            if dry_before != dry_after:
                raise DrillFailure(
                    "ECO04-DRY-RUN-WRITE", "dry run changed sandbox bytes"
                )
            if not all(item["preserved"] for item in dry_observations):
                failed = [
                    item["invariant_id"]
                    for item in dry_observations
                    if not item["preserved"]
                ]
                raise DrillFailure(
                    "ECO04-SEMANTIC-INVARIANT",
                    f"rename-only transform lost semantics for {failed!r}",
                )
            target_messages = validate_target_record(
                dry_target, sha256_bytes(source_raw)
            )
            if target_messages:
                raise DrillFailure(
                    "ECO04-TARGET-SCHEMA", "; ".join(target_messages)
                )
            deterministic_peer = transform_source(source_fixture, source_raw)
            observation["determinism"]["pure_transform_equal"] = (
                canonical_json_bytes(dry_target)
                == canonical_json_bytes(deterministic_peer)
            )
            if not observation["determinism"]["pure_transform_equal"]:
                raise DrillFailure(
                    "ECO04-DETERMINISM", "pure transforms produced different bytes"
                )

            if fault_mode != "skip_backup":
                observation["backup"] = create_backup(
                    audit, source_raw, backup_path, sidecar_path
                )

            observation["failure_injection"]["executed"] = True
            if fault_mode == "partial_write_on_failure":
                try:
                    audit.broken_partial_write(
                        record_path,
                        b'{"schema_version":"work-packet-instance/v2-drill"',
                    )
                    raise InjectedPreReplaceFailure(
                        "broken migration failed after a partial direct write"
                    )
                except InjectedPreReplaceFailure:
                    pass
            else:
                try:
                    transactional_migrate(
                        audit,
                        record_path,
                        backup_path,
                        sidecar_path,
                        spec["semantic_invariants"],
                        inject_before_replace=True,
                    )
                    raise DrillFailure(
                        "ECO04-FAILURE-INJECTION",
                        "pre-replace failure injection did not interrupt migration",
                    )
                except InjectedPreReplaceFailure:
                    pass

            failure_raw = record_path.read_bytes()
            candidate_path = record_path.with_name(
                record_path.name + ".migration-candidate"
            )
            observation["failure_injection"]["source_preserved"] = (
                failure_raw == source_raw
            )
            observation["failure_injection"]["candidate_removed"] = (
                not candidate_path.exists() and not candidate_path.is_symlink()
            )
            if failure_raw != source_raw:
                raise DrillFailure(
                    "ECO04-FAILURE-ATOMICITY",
                    "failed migration changed active source bytes",
                )
            if candidate_path.exists() or candidate_path.is_symlink():
                raise DrillFailure(
                    "ECO04-FAILURE-CLEANUP",
                    "failed migration left a candidate file behind",
                )

            backup_sequences = [
                event["sequence"]
                for event in audit.events
                if event["operation"] == "backup_exact_source"
            ]
            replace_candidate_sequences = [
                event["sequence"]
                for event in audit.events
                if event["operation"] == "migration_candidate_fsync"
            ]
            precedes = bool(backup_sequences and replace_candidate_sequences) and (
                min(backup_sequences) < min(replace_candidate_sequences)
            )
            observation["backup"]["precedes_first_replace"] = precedes
            if not precedes:
                raise DrillFailure(
                    "ECO04-BACKUP-ORDER",
                    "verified backup did not precede the first migration candidate",
                )

            migration_status, target_raw, semantic_results = transactional_migrate(
                audit,
                record_path,
                backup_path,
                sidecar_path,
                spec["semantic_invariants"],
            )
            observation["migration"] = {"status": migration_status}
            observation["target_sha256"] = sha256_bytes(target_raw)
            observation["semantic_invariants"] = semantic_results
            target_record = parse_strict_json_bytes(target_raw, "migrated target")
            observation["compatibility"] = compatibility_observation(
                source_fixture, target_record, sha256_bytes(source_raw)
            )
            if not observation["compatibility"]["break_is_explicit_and_enforced"]:
                raise DrillFailure(
                    "ECO04-COMPATIBILITY",
                    "reader behavior does not enforce the declared explicit break",
                )

            first_target_raw = record_path.read_bytes()
            if fault_mode == "non_idempotent_repeat":
                repeated_record = parse_strict_json_bytes(
                    first_target_raw, "first target"
                )
                audit.replace_bytes(
                    record_path,
                    pretty_json_bytes(repeated_record),
                    "broken_repeat_migration",
                )
                repeat_status = "rewritten_target"
            else:
                repeat_status, _, _ = transactional_migrate(
                    audit,
                    record_path,
                    backup_path,
                    sidecar_path,
                    spec["semantic_invariants"],
                )
            repeated_raw = record_path.read_bytes()
            repeat_bytes_equal = repeated_raw == first_target_raw
            repeat_hash_equal = sha256_bytes(repeated_raw) == sha256_bytes(
                first_target_raw
            )
            observation["repeat_run"] = {
                "status": repeat_status,
                "bytes_unchanged": repeat_bytes_equal,
                "sha256_unchanged": repeat_hash_equal,
            }
            if (
                repeat_status != "already_at_target"
                or not repeat_bytes_equal
                or not repeat_hash_equal
            ):
                raise DrillFailure(
                    "ECO04-REPEAT-IDEMPOTENCY",
                    "repeated migration was not a validated byte-preserving no-op",
                )

            restored_raw = transactional_rollback(
                audit,
                record_path,
                backup_path,
                sidecar_path,
                source_raw,
                rollback_drift=fault_mode == "rollback_drift",
            )
            restored_record = parse_strict_json_bytes(restored_raw, "restored source")
            rollback_exact_bytes = restored_raw == source_raw
            rollback_exact_hash = sha256_bytes(restored_raw) == sha256_bytes(
                source_raw
            )
            rollback_reader_accepts = source_reader_accepts(restored_record)
            observation["rollback"] = {
                "status": "restored",
                "exact_bytes": rollback_exact_bytes,
                "exact_sha256": rollback_exact_hash,
                "source_reader_accepts": rollback_reader_accepts,
            }
            if not rollback_exact_bytes or not rollback_exact_hash:
                raise DrillFailure(
                    "ECO04-ROLLBACK-BYTES",
                    "rollback did not restore exact source bytes and SHA-256",
                )
            if not rollback_reader_accepts:
                raise DrillFailure(
                    "ECO04-ROLLBACK-READER",
                    "source reader rejected the rolled-back record",
                )

            second_status, second_target_raw, _ = transactional_migrate(
                audit,
                record_path,
                backup_path,
                sidecar_path,
                spec["semantic_invariants"],
            )
            second_equal = (
                second_status == "migrated" and second_target_raw == first_target_raw
            )
            observation["determinism"]["second_migration_equal"] = second_equal
            if not second_equal:
                raise DrillFailure(
                    "ECO04-DETERMINISM",
                    "migration after rollback did not reproduce exact target bytes",
                )

            final_source_raw = transactional_rollback(
                audit,
                record_path,
                backup_path,
                sidecar_path,
                source_raw,
            )
            final_exact = final_source_raw == source_raw
            observation["exit"]["restored_source_exact"] = final_exact
            if not final_exact:
                raise DrillFailure(
                    "ECO04-EXIT-RESTORE",
                    "exit drill did not end at exact source state",
                )

            observation["project_isolation"]["audited_mutations"] = audit.events
            all_under_sandbox = all(
                is_within(sandbox / event["path"], sandbox)
                for event in audit.events
            )
            observation["project_isolation"][
                "all_audited_mutations_under_sandbox"
            ] = all_under_sandbox
            real_project_write_count = sum(
                1
                for event in audit.events
                if is_within(sandbox / event["path"], project_root)
            )
            observation["project_isolation"][
                "real_project_write_count"
            ] = real_project_write_count
            if not all_under_sandbox:
                raise DrillFailure(
                    "ECO04-PROJECT-ISOLATION",
                    "mutation audit contains an out-of-sandbox path",
                )
            if real_project_write_count != 0:
                raise DrillFailure(
                    "ECO04-PROJECT-ISOLATION",
                    "mutation audit contains a real-project write",
                )
    except DrillFailure as exc:
        add_error(errors, exc.oracle_id, exc.message)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        add_error(
            errors,
            "ECO04-UNEXPECTED-FAIL-CLOSED",
            f"drill aborted without a success claim: {type(exc).__name__}: {exc}",
        )

    try:
        after_project = snapshot_paths(project_root, protected_paths)
    except DrillFailure as exc:
        add_error(errors, exc.oracle_id, exc.message)
        after_project = []
    unchanged = before_project == after_project
    observation["project_isolation"]["protected_manifest_after"] = after_project
    observation["project_isolation"]["protected_manifest_unchanged"] = unchanged
    if not unchanged:
        add_error(
            errors,
            "ECO04-PROJECT-ISOLATION",
            "protected real-project bytes changed during the isolated drill",
        )
    try:
        after_project_tree = project_tree_manifest(
            project_root, excluded_components
        )
    except DrillFailure as exc:
        add_error(errors, exc.oracle_id, exc.message)
        after_project_tree = []
    before_tree_hash = sha256_bytes(canonical_json_bytes(before_project_tree))
    after_tree_hash = sha256_bytes(canonical_json_bytes(after_project_tree))
    full_tree_unchanged = before_project_tree == after_project_tree
    observation["project_isolation"][
        "full_tree_manifest_before_sha256"
    ] = before_tree_hash
    observation["project_isolation"][
        "full_tree_manifest_after_sha256"
    ] = after_tree_hash
    observation["project_isolation"][
        "full_tree_manifest_unchanged"
    ] = full_tree_unchanged
    if not full_tree_unchanged:
        add_error(
            errors,
            "ECO04-PROJECT-ISOLATION",
            "the real project tree changed during the isolated drill",
        )
    return observation


def verify(
    project_root: Path, spec_path: Path, fault_mode: str = "none"
) -> tuple[dict[str, Any], int]:
    errors: list[dict[str, str]] = []
    spec: dict[str, Any] = {}
    spec_raw = b""
    try:
        spec, spec_raw = read_strict_json(spec_path, "migration drill spec")
    except DrillFailure as exc:
        add_error(errors, exc.oracle_id, exc.message)

    if spec:
        for message in validate_spec(spec, spec_raw):
            add_error(errors, "ECO04-SPEC-CONTRACT", message)

    drill: dict[str, Any] = {"status": "not_executed"}
    if spec and not errors:
        try:
            drill = execute_drill(project_root, spec, fault_mode, errors)
        except DrillFailure as exc:
            add_error(errors, exc.oracle_id, exc.message)
            drill = {"status": "aborted_fail_closed"}
        except (OSError, ValueError, TypeError, KeyError) as exc:
            add_error(
                errors,
                "ECO04-UNEXPECTED-FAIL-CLOSED",
                f"drill setup aborted without a success claim: "
                f"{type(exc).__name__}: {exc}",
            )
            drill = {"status": "aborted_fail_closed"}

    status = "pass" if not errors else "fail"
    payload = {
        "schema_version": 1,
        "mechanism_id": MECHANISM_ID,
        "failure_id": FAILURE_ID,
        "requirement_id": REQUIREMENT_ID,
        "case_id": CASE_ID,
        "status": status,
        "fault_mode": fault_mode,
        "derived_from": {
            "spec_path": "governance/MIGRATION_DRILL_SPEC_V1.json",
            "spec_byte_count": len(spec_raw),
            "spec_sha256": sha256_bytes(spec_raw) if spec_raw else None,
        },
        "drill": drill,
        "claim_boundary": CLAIM_BOUNDARY,
        "errors": errors,
    }
    return payload, 0 if status == "pass" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="project root containing the frozen migration drill spec",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=None,
        help="explicit migration drill spec path (defaults under --root)",
    )
    parser.add_argument(
        "--fault-mode",
        choices=FAULT_MODES,
        default="none",
        help="test-only fault injected inside the isolated temporary drill",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit the full machine JSON receipt"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    project_root = args.root.resolve()
    spec_path = (
        args.spec.resolve()
        if args.spec is not None
        else project_root / "governance" / "MIGRATION_DRILL_SPEC_V1.json"
    )
    payload, exit_code = verify(project_root, spec_path, args.fault_mode)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif exit_code == 0:
        print(
            "PASS: ECO-04 migration, failure atomicity, repeat, rollback, "
            "determinism, and project isolation drill completed"
        )
    else:
        for error in payload["errors"]:
            print(
                f"FAIL [{error['oracle_id']}]: {error['message']}",
                file=sys.stderr,
            )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
