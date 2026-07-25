#!/usr/bin/env python3
"""Fail-closed ORG-04/ECO-01 execution-attempt ledger verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = Path("governance/EXECUTION_LOOP_POLICY_V1.json")
DEFAULT_PACKET = Path(
    ".work_packets/packets/WP-METHOD-INTEGRATION.packet.json"
)
DEFAULT_LEDGER = Path(
    ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json"
)

POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "linked_failure_ids",
    "bound_work_packet",
    "ledger_schema",
    "progress_derivation",
    "stopping_rules",
    "completion_rules",
    "cost_accounting",
    "platform_and_process_limitations",
}
PACKET_FIELDS = {
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
PACKET_CONTRACT_FIELDS = [
    "schema_version",
    "packet_id",
    "goal_id",
    "owner",
    "reviewer",
    "bounded_write_paths",
    "read_dependencies",
    "acceptance_checks",
    "retry_budget",
    "external_side_effects",
    "semantic_invariants",
]
LEDGER_FIELD_LIST = [
    "schema_version",
    "packet_id",
    "packet_path",
    "packet_contract_sha256",
    "reported_state",
    "cost_accounting_claim",
    "attempts",
]
LEDGER_FIELDS = set(LEDGER_FIELD_LIST)
ATTEMPT_FIELD_LIST = [
    "schema_version",
    "sequence",
    "retry_index",
    "started_at",
    "ended_at",
    "wall_time_ms",
    "blocker",
    "failure_delta",
    "evidence_delta",
    "cost_observation",
    "declared_progress",
    "previous_attempt_sha256",
    "record_sha256",
]
ATTEMPT_FIELDS = set(ATTEMPT_FIELD_LIST)
BLOCKER_FIELD_LIST = [
    "root_cause_id",
    "failure_ids",
    "root_cause",
    "status_after",
    "fingerprint_sha256",
]
BLOCKER_FIELDS = set(BLOCKER_FIELD_LIST)
FAILURE_DELTA_FIELD_LIST = ["before", "after", "resolved", "introduced"]
FAILURE_DELTA_FIELDS = set(FAILURE_DELTA_FIELD_LIST)
EVIDENCE_DELTA_FIELD_LIST = ["before", "after", "added", "removed"]
EVIDENCE_DELTA_FIELDS = set(EVIDENCE_DELTA_FIELD_LIST)
EVIDENCE_REFERENCE_FIELD_LIST = [
    "path",
    "sha256",
    "kind",
    "supports_failure_ids",
]
EVIDENCE_REFERENCE_FIELDS = set(EVIDENCE_REFERENCE_FIELD_LIST)
COST_OBSERVATION_FIELD_LIST = ["wall_time_source", "token_usage"]
COST_OBSERVATION_FIELDS = set(COST_OBSERVATION_FIELD_LIST)
TOKEN_USAGE_FIELD_LIST = [
    "availability",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "measurement_source",
]
TOKEN_USAGE_FIELDS = set(TOKEN_USAGE_FIELD_LIST)
PACKET_STATES = {"pending", "active", "blocked", "candidate_complete", "complete"}
EVIDENCE_KINDS = {
    "policy",
    "implementation",
    "test",
    "checkpoint_receipt",
    "acceptance_receipt",
    "other",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FAILURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{2,4}$")
ROOT_CAUSE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){1,15}$")
TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$"
)

EXPECTED_BOUND_PACKET = {
    "packet_id": "WP-METHOD-INTEGRATION",
    "packet_path": ".work_packets/packets/WP-METHOD-INTEGRATION.packet.json",
    "attempts_path": ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json",
    "packet_schema_version": "work-packet-instance/v1",
    "packet_contract_fields": PACKET_CONTRACT_FIELDS,
}
EXPECTED_LEDGER_SCHEMA = {
    "ledger_schema_version": "execution-attempt-ledger/v1",
    "ledger_required_fields": LEDGER_FIELD_LIST,
    "attempt_schema_version": "execution-attempt/v1",
    "attempt_required_fields": ATTEMPT_FIELD_LIST,
    "blocker_required_fields": BLOCKER_FIELD_LIST,
    "failure_delta_required_fields": FAILURE_DELTA_FIELD_LIST,
    "evidence_delta_required_fields": EVIDENCE_DELTA_FIELD_LIST,
    "evidence_reference_required_fields": EVIDENCE_REFERENCE_FIELD_LIST,
    "cost_observation_required_fields": COST_OBSERVATION_FIELD_LIST,
    "token_usage_required_fields": TOKEN_USAGE_FIELD_LIST,
    "first_sequence": 1,
    "first_retry_index": 0,
    "timestamp_format": "RFC3339_UTC_Z_MILLISECONDS",
    "record_hash_rule": "canonical_sha256_of_attempt_without_record_sha256",
}
EXPECTED_PROGRESS = {
    "declared_progress_must_equal_derived": True,
    "failure_delta_must_be_set_difference": True,
    "evidence_delta_must_be_set_difference": True,
    "evidence_after_must_match_current_regular_files": True,
    "progress_requires": "verified_evidence_addition_or_failure_resolution",
    "resolved_failure_requires_added_supporting_evidence": True,
    "ledger_and_packet_files_cannot_count_as_progress_evidence": True,
}
EXPECTED_STOPPING = {
    "same_blocker_consecutive_no_progress_threshold": 3,
    "same_blocker_threshold_outcome": "blocked",
    "retry_budget_source": "packet.retry_budget",
    "first_attempt_is_retry_index_zero": True,
    "retry_index_above_budget_outcome": "invalid",
    "budget_exhausted_without_verified_acceptance_outcome": "blocked",
}
EXPECTED_COMPLETION = {
    "candidate_complete_requires_current_checkpoint_receipt": True,
    "complete_requires_current_checkpoint_and_acceptance_receipts": True,
    "receipt_directory": ".work_packets/receipts",
    "checkpoint_schema_version": "work-packet-checkpoint/v1",
    "acceptance_schema_version": "work-packet-acceptance/v1",
    "all_actual_exit_codes_must_equal_expected": True,
    "final_attempt_must_add_required_receipt": True,
    "acceptance_without_budget_overrun_can_derive_complete": True,
}
EXPECTED_COST = {
    "wall_time_source": "started_at_and_ended_at",
    "token_availability_values": ["measured", "unknown"],
    "unknown_tokens_require_null_counts_and_source": True,
    "measured_tokens_require_nonnegative_counts_sum_and_source": True,
    "ledger_claim_values": ["measured", "partial"],
    "any_unknown_token_observation_forces_partial": True,
}
EXPECTED_LIMITATIONS = [
    "Current-file hashes prove that cited evidence bytes exist now; they do not by themselves prove semantic adequacy or the historical time at which those bytes were created.",
    "The local JSON ledger is tamper-evident through hashes and ordering but not physically append-only; durable Git and remote history are separate assurance layers.",
    "When the execution platform exposes no token telemetry, token cost remains explicitly unknown and aggregate accounting remains partial.",
    "Acceptance receipts bind declared checks and recorded exit codes, but this verifier does not re-execute, authenticate, or sandbox the recorded commands.",
    "A stable root-cause identifier reduces wording-based retry evasion, but independent review is still needed to detect dishonest splitting of one semantic blocker into multiple identifiers.",
]


class DuplicateKeyError(ValueError):
    """Raised when a JSON object attempts to overwrite an earlier key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any] | None:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: invalid or unreadable JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: top-level value must be an object")
        return None
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_int(value: Any) -> bool:
    return type(value) is int


def nonempty_string(value: Any, maximum: int = 1024) -> bool:
    return (
        isinstance(value, str)
        and value == value.strip()
        and 0 < len(value) <= maximum
    )


def exact_keys(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return False
    actual = set(value)
    if actual != expected:
        errors.append(
            f"{label}: fields differ; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
        return False
    return True


def normalize_relative_path(value: Any, label: str, errors: list[str]) -> str | None:
    if not nonempty_string(value, maximum=512):
        errors.append(f"{label}: must be a bounded non-empty string")
        return None
    assert isinstance(value, str)
    if "\\" in value or any(character in value for character in "*?[]{}"):
        errors.append(f"{label}: backslashes and unresolved glob syntax are forbidden")
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or value in {".", "..", "~"}:
        errors.append(f"{label}: must be a project-relative path")
        return None
    if any(part in {"", ".", "..", "~"} for part in path.parts):
        errors.append(f"{label}: traversal and non-normalized components are forbidden")
        return None
    if posixpath.normpath(value) != value:
        errors.append(f"{label}: path must already be normalized")
        return None
    return value


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_regular_file(
    project_root: Path,
    relative: str,
    label: str,
    errors: list[str],
) -> Path | None:
    normalized = normalize_relative_path(relative, label, errors)
    if normalized is None:
        return None
    candidate = project_root.joinpath(*PurePosixPath(normalized).parts)
    cursor = project_root
    try:
        for part in PurePosixPath(normalized).parts:
            cursor = cursor / part
            if cursor.exists() and cursor.is_symlink():
                errors.append(f"{label}: symlink path components are forbidden")
                return None
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"{label}: cannot resolve regular file: {exc}")
        return None
    if not is_within(resolved, project_root):
        errors.append(f"{label}: canonical path escapes project root")
        return None
    if not resolved.is_file() or candidate.is_symlink():
        errors.append(f"{label}: must resolve to a non-symlink regular file")
        return None
    return candidate


def resolve_cli_file(
    project_root: Path,
    argument: Path,
    label: str,
    errors: list[str],
) -> Path | None:
    candidate = argument if argument.is_absolute() else project_root / argument
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"{label}: cannot resolve: {exc}")
        return None
    if not is_within(resolved, project_root):
        errors.append(f"{label}: canonical path escapes project root")
        return None
    if candidate.is_symlink() or not resolved.is_file():
        errors.append(f"{label}: must be a non-symlink regular file")
        return None
    return candidate


def validate_policy(policy: dict[str, Any], errors: list[str]) -> bool:
    if not exact_keys(policy, POLICY_FIELDS, "policy", errors):
        return False
    comparisons = (
        ("schema_version", "execution-loop-policy/v1"),
        ("policy_id", "ORG-04-ECO-01-EXECUTION-LOOP-V1"),
        ("linked_failure_ids", ["ORG-04", "ECO-01"]),
        ("bound_work_packet", EXPECTED_BOUND_PACKET),
        ("ledger_schema", EXPECTED_LEDGER_SCHEMA),
        ("progress_derivation", EXPECTED_PROGRESS),
        ("stopping_rules", EXPECTED_STOPPING),
        ("completion_rules", EXPECTED_COMPLETION),
        ("cost_accounting", EXPECTED_COST),
        ("platform_and_process_limitations", EXPECTED_LIMITATIONS),
    )
    for field, expected in comparisons:
        if policy[field] != expected:
            errors.append(f"policy.{field}: frozen value differs")
    return not errors


def validate_string_id_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    allowed: set[str] | None = None,
    allow_empty: bool = True,
) -> list[str] | None:
    if not isinstance(value, list) or (not allow_empty and not value):
        errors.append(f"{label}: must be a {'non-empty ' if not allow_empty else ''}list")
        return None
    if not all(isinstance(item, str) and FAILURE_ID_RE.fullmatch(item) for item in value):
        errors.append(f"{label}: contains an invalid failure id")
        return None
    if value != sorted(set(value)):
        errors.append(f"{label}: must be unique and lexicographically sorted")
    if allowed is not None and not set(value).issubset(allowed):
        errors.append(f"{label}: contains failure ids outside the bound policy")
    return value


def validate_acceptance_checks(value: Any, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        errors.append("packet.acceptance_checks: must be a non-empty list")
        return []
    checks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, check in enumerate(value):
        label = f"packet.acceptance_checks[{index}]"
        if not exact_keys(
            check,
            {"check_id", "kind", "argv", "expected_exit_code"},
            label,
            errors,
        ):
            continue
        check_id = check["check_id"]
        if not nonempty_string(check_id, maximum=128) or check_id in seen:
            errors.append(f"{label}: check_id must be unique and non-empty")
        else:
            seen.add(check_id)
        if check["kind"] != "process_exit":
            errors.append(f"{label}: only process_exit is supported")
        argv = check["argv"]
        if (
            not isinstance(argv, list)
            or not argv
            or not all(nonempty_string(item) for item in argv)
        ):
            errors.append(f"{label}: argv must be a non-empty string list")
        expected = check["expected_exit_code"]
        if not is_int(expected) or not 0 <= expected <= 255:
            errors.append(f"{label}: expected_exit_code must be in [0, 255]")
        checks.append(check)
    return checks


def validate_packet(
    packet: dict[str, Any],
    policy: dict[str, Any],
    errors: list[str],
) -> tuple[str | None, int | None, list[dict[str, Any]], str | None]:
    if not exact_keys(packet, PACKET_FIELDS, "packet", errors):
        return None, None, [], None
    bound = policy["bound_work_packet"]
    if packet["schema_version"] != bound["packet_schema_version"]:
        errors.append("packet.schema_version: differs from bound schema")
    if packet["packet_id"] != bound["packet_id"]:
        errors.append("packet.packet_id: differs from bound packet")
    state = packet["state"]
    if state not in PACKET_STATES:
        errors.append("packet.state: unsupported state")
        state = None
    retry_budget = packet["retry_budget"]
    if not is_int(retry_budget) or not 0 <= retry_budget <= 100:
        errors.append("packet.retry_budget: must be an integer in [0, 100]")
        retry_budget = None
    checks = validate_acceptance_checks(packet["acceptance_checks"], errors)
    writes = packet["bounded_write_paths"]
    if not isinstance(writes, list) or not writes:
        errors.append("packet.bounded_write_paths: must be a non-empty list")
    else:
        for index, claim in enumerate(writes):
            label = f"packet.bounded_write_paths[{index}]"
            if not exact_keys(claim, {"path", "kind"}, label, errors):
                continue
            normalize_relative_path(claim["path"], f"{label}.path", errors)
            if claim["kind"] not in {"file", "tree"}:
                errors.append(f"{label}.kind: must be file or tree")
    try:
        contract = {field: packet[field] for field in PACKET_CONTRACT_FIELDS}
        contract_digest = canonical_sha256(contract)
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f"packet contract: cannot hash: {exc}")
        contract_digest = None
    return state, retry_budget, checks, contract_digest


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or TIMESTAMP_RE.fullmatch(value) is None:
        errors.append(f"{label}: must use RFC3339 UTC with millisecond precision")
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC)
    except ValueError as exc:
        errors.append(f"{label}: invalid timestamp: {exc}")
        return None


def evidence_identity(reference: dict[str, Any]) -> bytes:
    return canonical_json_bytes(reference)


def validate_evidence_references(
    value: Any,
    label: str,
    project_root: Path,
    allowed_failures: set[str],
    errors: list[str],
    *,
    require_current: bool,
) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        errors.append(f"{label}: must be a list")
        return None
    references: list[dict[str, Any]] = []
    prior_path = ""
    seen_paths: set[str] = set()
    for index, reference in enumerate(value):
        item_label = f"{label}[{index}]"
        if not exact_keys(reference, EVIDENCE_REFERENCE_FIELDS, item_label, errors):
            continue
        relative = normalize_relative_path(reference["path"], f"{item_label}.path", errors)
        if relative is not None:
            if relative in seen_paths:
                errors.append(f"{item_label}.path: duplicate evidence path")
            if prior_path and relative <= prior_path:
                errors.append(f"{label}: evidence paths must be strictly sorted")
            prior_path = relative
            seen_paths.add(relative)
        digest = reference["sha256"]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            errors.append(f"{item_label}.sha256: invalid digest")
        if reference["kind"] not in EVIDENCE_KINDS:
            errors.append(f"{item_label}.kind: unsupported evidence kind")
        validate_string_id_list(
            reference["supports_failure_ids"],
            f"{item_label}.supports_failure_ids",
            errors,
            allowed=allowed_failures,
            allow_empty=False,
        )
        if require_current and relative is not None:
            current = resolve_regular_file(project_root, relative, item_label, errors)
            if current is not None:
                try:
                    actual = raw_sha256(current)
                except OSError as exc:
                    errors.append(f"{item_label}: cannot hash evidence: {exc}")
                else:
                    if actual != digest:
                        errors.append(f"{item_label}: sha256 differs from current file")
        references.append(reference)
    return references


def validate_failure_delta(
    value: Any,
    label: str,
    allowed_failures: set[str],
    previous_after: list[str] | None,
    errors: list[str],
) -> tuple[list[str], list[str], list[str]] | None:
    if not exact_keys(value, FAILURE_DELTA_FIELDS, label, errors):
        return None
    lists: dict[str, list[str]] = {}
    for field in ("before", "after", "resolved", "introduced"):
        parsed = validate_string_id_list(
            value[field],
            f"{label}.{field}",
            errors,
            allowed=allowed_failures,
        )
        lists[field] = [] if parsed is None else parsed
    before = lists["before"]
    after = lists["after"]
    if previous_after is None:
        if before != sorted(allowed_failures):
            errors.append(f"{label}.before: first attempt must anchor all linked failures")
    elif before != previous_after:
        errors.append(f"{label}.before: does not continue prior failure state")
    expected_resolved = sorted(set(before) - set(after))
    expected_introduced = sorted(set(after) - set(before))
    if lists["resolved"] != expected_resolved:
        errors.append(f"{label}.resolved: differs from derived set difference")
    if lists["introduced"] != expected_introduced:
        errors.append(f"{label}.introduced: differs from derived set difference")
    return after, expected_resolved, expected_introduced


def validate_evidence_delta(
    value: Any,
    label: str,
    project_root: Path,
    allowed_failures: set[str],
    previous_after: list[dict[str, Any]] | None,
    errors: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]] | None:
    if not exact_keys(value, EVIDENCE_DELTA_FIELDS, label, errors):
        return None
    before = validate_evidence_references(
        value["before"],
        f"{label}.before",
        project_root,
        allowed_failures,
        errors,
        require_current=False,
    )
    after = validate_evidence_references(
        value["after"],
        f"{label}.after",
        project_root,
        allowed_failures,
        errors,
        require_current=True,
    )
    added = validate_evidence_references(
        value["added"],
        f"{label}.added",
        project_root,
        allowed_failures,
        errors,
        require_current=True,
    )
    removed = validate_evidence_references(
        value["removed"],
        f"{label}.removed",
        project_root,
        allowed_failures,
        errors,
        require_current=False,
    )
    if any(item is None for item in (before, after, added, removed)):
        return None
    assert before is not None and after is not None and added is not None and removed is not None
    if previous_after is None:
        if before:
            errors.append(f"{label}.before: first attempt must start with no evidence")
    elif before != previous_after:
        errors.append(f"{label}.before: does not continue prior evidence state")
    before_map = {evidence_identity(item): item for item in before}
    after_map = {evidence_identity(item): item for item in after}
    expected_added = [after_map[key] for key in sorted(after_map.keys() - before_map.keys())]
    expected_removed = [before_map[key] for key in sorted(before_map.keys() - after_map.keys())]
    expected_added.sort(key=lambda item: item["path"])
    expected_removed.sort(key=lambda item: item["path"])
    if added != expected_added:
        errors.append(f"{label}.added: differs from derived evidence set difference")
    if removed != expected_removed:
        errors.append(f"{label}.removed: differs from derived evidence set difference")
    return after, expected_added, expected_removed


def validate_cost_observation(
    value: Any,
    label: str,
    errors: list[str],
) -> str | None:
    if not exact_keys(value, COST_OBSERVATION_FIELDS, label, errors):
        return None
    if value["wall_time_source"] != "timestamps":
        errors.append(f"{label}.wall_time_source: must be timestamps")
    token = value["token_usage"]
    if not exact_keys(token, TOKEN_USAGE_FIELDS, f"{label}.token_usage", errors):
        return None
    availability = token["availability"]
    counts = (token["input_tokens"], token["output_tokens"], token["total_tokens"])
    source = token["measurement_source"]
    if availability == "unknown":
        if counts != (None, None, None) or source is not None:
            errors.append(
                f"{label}.token_usage: unknown telemetry requires null counts and source"
            )
    elif availability == "measured":
        if not all(is_int(item) and item >= 0 for item in counts):
            errors.append(
                f"{label}.token_usage: measured telemetry requires nonnegative integer counts"
            )
        elif counts[0] + counts[1] != counts[2]:
            errors.append(f"{label}.token_usage: total must equal input plus output")
        if not nonempty_string(source, maximum=256) or source == "unknown":
            errors.append(f"{label}.token_usage: measured telemetry requires a source")
    else:
        errors.append(f"{label}.token_usage: availability must be measured or unknown")
        return None
    return availability


def blocker_fingerprint(blocker: dict[str, Any]) -> str:
    return canonical_sha256(
        {
            "root_cause_id": blocker["root_cause_id"],
            "failure_ids": blocker["failure_ids"],
        }
    )


def validate_blocker(
    value: Any,
    label: str,
    allowed_failures: set[str],
    after_failures: list[str],
    resolved_failures: list[str],
    errors: list[str],
) -> tuple[str | None, str | None]:
    if not exact_keys(value, BLOCKER_FIELDS, label, errors):
        return None, None
    root_cause_id = value["root_cause_id"]
    if not isinstance(root_cause_id, str) or ROOT_CAUSE_ID_RE.fullmatch(root_cause_id) is None:
        errors.append(f"{label}.root_cause_id: invalid stable identifier")
    failures = validate_string_id_list(
        value["failure_ids"],
        f"{label}.failure_ids",
        errors,
        allowed=allowed_failures,
        allow_empty=False,
    )
    if not nonempty_string(value["root_cause"], maximum=1000):
        errors.append(f"{label}.root_cause: must be a bounded non-empty explanation")
    status = value["status_after"]
    if status not in {"open", "resolved"}:
        errors.append(f"{label}.status_after: must be open or resolved")
        status = None
    expected_fingerprint = blocker_fingerprint(value)
    if value["fingerprint_sha256"] != expected_fingerprint:
        errors.append(f"{label}.fingerprint_sha256: differs from derived identity")
    if failures is not None and status == "open" and not set(failures).intersection(after_failures):
        errors.append(f"{label}: open blocker must retain at least one linked failure")
    if (
        failures is not None
        and status == "resolved"
        and not set(failures).issubset(resolved_failures)
    ):
        errors.append(f"{label}: resolved blocker must be derived from failure_delta.resolved")
    return expected_fingerprint, status


def tree_content_sha256(directory: Path, label: str, errors: list[str]) -> str | None:
    records: list[dict[str, str]] = []
    try:
        for current, directories, filenames in os.walk(directory, topdown=True, followlinks=False):
            directories.sort()
            filenames.sort()
            current_path = Path(current)
            for name in directories:
                child = current_path / name
                relative = child.relative_to(directory).as_posix()
                if child.is_symlink():
                    errors.append(f"{label}: nested symlink is forbidden: {relative}")
                else:
                    records.append({"path": relative, "type": "directory"})
            for name in filenames:
                child = current_path / name
                relative = child.relative_to(directory).as_posix()
                if child.is_symlink():
                    errors.append(f"{label}: nested symlink is forbidden: {relative}")
                elif child.is_file():
                    records.append(
                        {"path": relative, "type": "file", "sha256": raw_sha256(child)}
                    )
                else:
                    errors.append(f"{label}: unsupported filesystem entry: {relative}")
    except OSError as exc:
        errors.append(f"{label}: tree traversal failed: {exc}")
        return None
    return canonical_sha256(records)


def current_write_snapshots(
    packet: dict[str, Any], project_root: Path, errors: list[str]
) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    writes = packet.get("bounded_write_paths")
    if not isinstance(writes, list):
        return snapshots
    for index, claim in enumerate(writes):
        label = f"checkpoint snapshot[{index}]"
        if not isinstance(claim, dict) or set(claim) != {"path", "kind"}:
            continue
        relative = normalize_relative_path(claim["path"], f"{label}.path", errors)
        if relative is None:
            continue
        candidate = project_root.joinpath(*PurePosixPath(relative).parts)
        if not candidate.exists():
            snapshots.append(
                {"path": relative, "kind": claim["kind"], "state": "absent", "content_sha256": None}
            )
            continue
        current = (
            resolve_regular_file(project_root, relative, label, errors)
            if claim["kind"] == "file"
            else None
        )
        if claim["kind"] == "file":
            if current is not None:
                snapshots.append(
                    {
                        "path": relative,
                        "kind": "file",
                        "state": "file",
                        "content_sha256": raw_sha256(current),
                    }
                )
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            errors.append(f"{label}: cannot resolve tree: {exc}")
            continue
        if candidate.is_symlink() or not is_within(resolved, project_root) or not resolved.is_dir():
            errors.append(f"{label}: tree must be a project-local non-symlink directory")
            continue
        digest = tree_content_sha256(resolved, label, errors)
        if digest is not None:
            snapshots.append(
                {"path": relative, "kind": "tree", "state": "tree", "content_sha256": digest}
            )
    return snapshots


def verify_checkpoint(
    packet: dict[str, Any],
    contract_digest: str,
    project_root: Path,
    errors: list[str],
) -> tuple[dict[str, Any] | None, Path | None]:
    relative = packet.get("checkpoint_path")
    if relative is None:
        return None, None
    expected = f".work_packets/receipts/{packet['packet_id']}.checkpoint.json"
    if relative != expected:
        errors.append(f"checkpoint receipt path must be {expected!r}")
        return None, None
    path = resolve_regular_file(project_root, relative, "checkpoint receipt", errors)
    if path is None:
        return None, None
    start = len(errors)
    receipt = load_json_object(path, errors, "checkpoint receipt")
    if receipt is None or not exact_keys(
        receipt,
        {"schema_version", "packet_id", "packet_contract_sha256", "sequence", "snapshots"},
        "checkpoint receipt",
        errors,
    ):
        return None, path
    if receipt["schema_version"] != "work-packet-checkpoint/v1":
        errors.append("checkpoint receipt: schema_version differs")
    if receipt["packet_id"] != packet["packet_id"]:
        errors.append("checkpoint receipt: packet_id differs")
    if receipt["packet_contract_sha256"] != contract_digest:
        errors.append("checkpoint receipt: packet contract digest differs")
    if not is_int(receipt["sequence"]) or receipt["sequence"] < 1:
        errors.append("checkpoint receipt: sequence must be a positive integer")
    if receipt["snapshots"] != current_write_snapshots(packet, project_root, errors):
        errors.append("checkpoint receipt: snapshots differ from current write set")
    if len(errors) != start:
        return None, path
    return receipt, path


def verify_acceptance(
    packet: dict[str, Any],
    checks: list[dict[str, Any]],
    contract_digest: str,
    checkpoint: dict[str, Any] | None,
    project_root: Path,
    errors: list[str],
) -> tuple[bool, Path | None]:
    relative = packet.get("acceptance_receipt_path")
    if relative is None:
        return False, None
    expected = f".work_packets/receipts/{packet['packet_id']}.acceptance.json"
    if relative != expected:
        errors.append(f"acceptance receipt path must be {expected!r}")
        return False, None
    path = resolve_regular_file(project_root, relative, "acceptance receipt", errors)
    if path is None:
        return False, None
    receipt = load_json_object(path, errors, "acceptance receipt")
    if receipt is None or not exact_keys(
        receipt,
        {
            "schema_version",
            "packet_id",
            "packet_contract_sha256",
            "checkpoint_receipt_sha256",
            "checks",
        },
        "acceptance receipt",
        errors,
    ):
        return False, path
    start = len(errors)
    if receipt["schema_version"] != "work-packet-acceptance/v1":
        errors.append("acceptance receipt: schema_version differs")
    if receipt["packet_id"] != packet["packet_id"]:
        errors.append("acceptance receipt: packet_id differs")
    if receipt["packet_contract_sha256"] != contract_digest:
        errors.append("acceptance receipt: packet contract digest differs")
    if checkpoint is None:
        errors.append("acceptance receipt: a valid current checkpoint is required")
    elif receipt["checkpoint_receipt_sha256"] != canonical_sha256(checkpoint):
        errors.append("acceptance receipt: checkpoint digest differs")
    actual_checks = receipt["checks"]
    if not isinstance(actual_checks, list) or len(actual_checks) != len(checks):
        errors.append("acceptance receipt: check count differs")
    else:
        for index, (actual, declared) in enumerate(zip(actual_checks, checks, strict=True)):
            label = f"acceptance receipt.checks[{index}]"
            if not exact_keys(actual, {"check_id", "actual_exit_code"}, label, errors):
                continue
            if actual["check_id"] != declared["check_id"]:
                errors.append(f"{label}: check_id differs")
            exit_code = actual["actual_exit_code"]
            if not is_int(exit_code) or not 0 <= exit_code <= 255:
                errors.append(f"{label}: invalid actual_exit_code")
            elif exit_code != declared["expected_exit_code"]:
                errors.append(
                    f"{label}: actual exit {exit_code} does not equal expected "
                    f"{declared['expected_exit_code']}"
                )
    return len(errors) == start, path


def receipt_added(
    added: list[dict[str, Any]], path: Path | None, project_root: Path, kind: str
) -> bool:
    if path is None:
        return False
    relative = path.relative_to(project_root).as_posix()
    digest = raw_sha256(path)
    return any(
        item["path"] == relative and item["sha256"] == digest and item["kind"] == kind
        for item in added
    )


def validate_attempts(
    attempts: Any,
    project_root: Path,
    policy: dict[str, Any],
    packet_path: str,
    ledger_path: str,
    retry_budget: int,
    errors: list[str],
) -> dict[str, Any]:
    if not isinstance(attempts, list):
        errors.append("ledger.attempts: must be a list")
        attempts = []
    allowed_failures = set(policy["linked_failure_ids"])
    previous_failure_after: list[str] | None = None
    previous_evidence_after: list[dict[str, Any]] | None = None
    previous_ended: datetime | None = None
    previous_record_sha: str | None = None
    token_availabilities: list[str] = []
    progress_flags: list[bool] = []
    blocker_fingerprints: list[str | None] = []
    blocker_statuses: list[str | None] = []
    added_by_attempt: list[list[dict[str, Any]]] = []
    forced_block_sequence: int | None = None
    consecutive_count = 0
    consecutive_fingerprint: str | None = None

    for index, attempt in enumerate(attempts):
        label = f"ledger.attempts[{index}]"
        start_error_count = len(errors)
        if not exact_keys(attempt, ATTEMPT_FIELDS, label, errors):
            progress_flags.append(False)
            blocker_fingerprints.append(None)
            blocker_statuses.append(None)
            added_by_attempt.append([])
            continue
        sequence = attempt["sequence"]
        retry_index = attempt["retry_index"]
        if not is_int(sequence) or sequence != index + 1:
            errors.append(f"{label}.sequence: must be contiguous and equal {index + 1}")
        if not is_int(retry_index) or retry_index != index:
            errors.append(f"{label}.retry_index: must be contiguous and equal {index}")
        if is_int(retry_index) and retry_index > retry_budget:
            errors.append(f"{label}.retry_index: exceeds packet retry_budget {retry_budget}")
        started = parse_timestamp(attempt["started_at"], f"{label}.started_at", errors)
        ended = parse_timestamp(attempt["ended_at"], f"{label}.ended_at", errors)
        wall_time = attempt["wall_time_ms"]
        if not is_int(wall_time) or wall_time < 0:
            errors.append(f"{label}.wall_time_ms: must be a nonnegative integer")
        if started is not None and ended is not None:
            if ended < started:
                errors.append(f"{label}: ended_at precedes started_at")
            else:
                derived_wall_time = int((ended - started).total_seconds() * 1000)
                if wall_time != derived_wall_time:
                    errors.append(f"{label}.wall_time_ms: differs from timestamp delta")
            if previous_ended is not None and started < previous_ended:
                errors.append(f"{label}.started_at: attempts overlap or are reordered")
            previous_ended = ended

        failure_result = validate_failure_delta(
            attempt["failure_delta"],
            f"{label}.failure_delta",
            allowed_failures,
            previous_failure_after,
            errors,
        )
        if failure_result is None:
            after_failures: list[str] = []
            resolved_failures: list[str] = []
        else:
            after_failures, resolved_failures, _ = failure_result
            previous_failure_after = after_failures
        evidence_result = validate_evidence_delta(
            attempt["evidence_delta"],
            f"{label}.evidence_delta",
            project_root,
            allowed_failures,
            previous_evidence_after,
            errors,
        )
        if evidence_result is None:
            after_evidence: list[dict[str, Any]] = []
            added_evidence: list[dict[str, Any]] = []
        else:
            after_evidence, added_evidence, _ = evidence_result
            previous_evidence_after = after_evidence
        added_by_attempt.append(added_evidence)

        fingerprint, blocker_status = validate_blocker(
            attempt["blocker"],
            f"{label}.blocker",
            allowed_failures,
            after_failures,
            resolved_failures,
            errors,
        )
        blocker_fingerprints.append(fingerprint)
        blocker_statuses.append(blocker_status)

        forbidden_progress_paths = {packet_path, ledger_path}
        verified_added = [
            item for item in added_evidence if item["path"] not in forbidden_progress_paths
        ]
        for failure_id in resolved_failures:
            if not any(failure_id in item["supports_failure_ids"] for item in verified_added):
                errors.append(
                    f"{label}.failure_delta.resolved: {failure_id} lacks added supporting evidence"
                )
        derived_progress = bool(verified_added or resolved_failures)
        declared_progress = attempt["declared_progress"]
        if type(declared_progress) is not bool:
            errors.append(f"{label}.declared_progress: must be boolean")
        elif declared_progress != derived_progress:
            errors.append(
                f"{label}.declared_progress: differs from derived progress {derived_progress}"
            )
        progress_flags.append(derived_progress)

        availability = validate_cost_observation(
            attempt["cost_observation"], f"{label}.cost_observation", errors
        )
        if availability is not None:
            token_availabilities.append(availability)

        expected_previous = None if index == 0 else previous_record_sha
        if attempt["previous_attempt_sha256"] != expected_previous:
            errors.append(f"{label}.previous_attempt_sha256: chain link differs")
        record_sha = attempt["record_sha256"]
        if not isinstance(record_sha, str) or SHA256_RE.fullmatch(record_sha) is None:
            errors.append(f"{label}.record_sha256: invalid digest")
            previous_record_sha = None
        else:
            expected_record = canonical_sha256(
                {key: value for key, value in attempt.items() if key != "record_sha256"}
            )
            if record_sha != expected_record:
                errors.append(f"{label}.record_sha256: differs from canonical attempt")
            previous_record_sha = record_sha

        if forced_block_sequence is not None:
            errors.append(
                f"{label}: attempt continued after mandatory block at sequence {forced_block_sequence}"
            )
        if blocker_status == "open" and not derived_progress and fingerprint is not None:
            if fingerprint == consecutive_fingerprint:
                consecutive_count += 1
            else:
                consecutive_fingerprint = fingerprint
                consecutive_count = 1
        else:
            consecutive_fingerprint = None
            consecutive_count = 0
        if consecutive_count >= 3 and forced_block_sequence is None:
            forced_block_sequence = index + 1

        if len(errors) > start_error_count and failure_result is None:
            previous_failure_after = None
        if len(errors) > start_error_count and evidence_result is None:
            previous_evidence_after = None

    highest_retry_index = len(attempts) - 1 if attempts else None
    return {
        "attempt_count": len(attempts),
        "highest_retry_index": highest_retry_index,
        "progress_attempt_count": sum(progress_flags),
        "token_availabilities": token_availabilities,
        "forced_block_sequence": forced_block_sequence,
        "consecutive_same_blocker_no_progress": consecutive_count,
        "added_by_attempt": added_by_attempt,
        "final_failure_ids": previous_failure_after,
        "final_blocker_status": blocker_statuses[-1] if blocker_statuses else None,
    }


def verify(
    project_root_argument: Path,
    policy_argument: Path,
    packet_argument: Path,
    ledger_argument: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        project_root = project_root_argument.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return failure_result([f"project root: cannot resolve: {exc}"])
    if not project_root.is_dir():
        return failure_result(["project root: must be a directory"])

    policy_path = resolve_cli_file(project_root, policy_argument, "policy", errors)
    packet_path = resolve_cli_file(project_root, packet_argument, "packet", errors)
    ledger_path = resolve_cli_file(project_root, ledger_argument, "ledger", errors)
    if policy_path is None or packet_path is None or ledger_path is None:
        return failure_result(errors)
    policy = load_json_object(policy_path, errors, "policy")
    packet = load_json_object(packet_path, errors, "packet")
    ledger = load_json_object(ledger_path, errors, "ledger")
    if policy is None or packet is None or ledger is None:
        return failure_result(errors)
    if not validate_policy(policy, errors):
        return failure_result(errors, policy=policy)

    bound = policy["bound_work_packet"]
    actual_packet_relative = packet_path.relative_to(project_root).as_posix()
    actual_ledger_relative = ledger_path.relative_to(project_root).as_posix()
    if actual_packet_relative != bound["packet_path"]:
        errors.append("packet: CLI path differs from frozen bound packet path")
    if actual_ledger_relative != bound["attempts_path"]:
        errors.append("ledger: CLI path differs from frozen attempts path")

    packet_state, retry_budget, checks, contract_digest = validate_packet(packet, policy, errors)
    if not exact_keys(ledger, LEDGER_FIELDS, "ledger", errors):
        return failure_result(errors, policy=policy)
    if ledger["schema_version"] != "execution-attempt-ledger/v1":
        errors.append("ledger.schema_version: unsupported schema")
    if ledger["packet_id"] != bound["packet_id"] or ledger["packet_id"] != packet.get("packet_id"):
        errors.append("ledger.packet_id: differs from bound packet")
    if ledger["packet_path"] != bound["packet_path"]:
        errors.append("ledger.packet_path: differs from frozen packet path")
    if contract_digest is None or ledger["packet_contract_sha256"] != contract_digest:
        errors.append("ledger.packet_contract_sha256: differs from current packet contract")
    reported_state = ledger["reported_state"]
    if reported_state not in PACKET_STATES:
        errors.append("ledger.reported_state: unsupported state")
    if packet_state is not None and reported_state != packet_state:
        errors.append("ledger.reported_state: differs from packet.state")
    if ledger["cost_accounting_claim"] not in {"measured", "partial"}:
        errors.append("ledger.cost_accounting_claim: must be measured or partial")

    if retry_budget is None:
        retry_budget = 0
    attempt_result = validate_attempts(
        ledger["attempts"],
        project_root,
        policy,
        bound["packet_path"],
        bound["attempts_path"],
        retry_budget,
        errors,
    )

    checkpoint: dict[str, Any] | None = None
    checkpoint_path: Path | None = None
    acceptance_verified = False
    acceptance_path: Path | None = None
    if contract_digest is not None:
        checkpoint, checkpoint_path = verify_checkpoint(
            packet, contract_digest, project_root, errors
        )
        acceptance_verified, acceptance_path = verify_acceptance(
            packet, checks, contract_digest, checkpoint, project_root, errors
        )

    if checkpoint is not None and checkpoint["sequence"] != attempt_result["attempt_count"]:
        errors.append("checkpoint receipt: sequence must equal the final attempt sequence")

    added_by_attempt = attempt_result["added_by_attempt"]
    final_added = added_by_attempt[-1] if added_by_attempt else []
    checkpoint_added = receipt_added(
        final_added, checkpoint_path, project_root, "checkpoint_receipt"
    )
    acceptance_added = receipt_added(
        final_added, acceptance_path, project_root, "acceptance_receipt"
    )
    if packet_state == "candidate_complete" and (checkpoint is None or not checkpoint_added):
        errors.append(
            "candidate_complete requires a valid current checkpoint receipt added by the final attempt"
        )
    if packet_state == "complete":
        if checkpoint is None or not acceptance_verified:
            errors.append("complete requires valid current checkpoint and acceptance receipts")
        if not checkpoint_added or not acceptance_added:
            errors.append("complete requires the final attempt to add both bound receipts")

    failure_closure_verified = (
        attempt_result["final_failure_ids"] == []
        and attempt_result["final_blocker_status"] == "resolved"
    )
    if packet_state == "complete" and not failure_closure_verified:
        errors.append("complete requires all linked failures and the final blocker to be resolved")
    verified_completion = (
        acceptance_verified
        and checkpoint_added
        and acceptance_added
        and failure_closure_verified
    )

    availability = attempt_result["token_availabilities"]
    derived_cost_claim = (
        "measured"
        if attempt_result["attempt_count"] > 0
        and len(availability) == attempt_result["attempt_count"]
        and all(item == "measured" for item in availability)
        else "partial"
    )
    if ledger["cost_accounting_claim"] != derived_cost_claim:
        errors.append(
            f"ledger.cost_accounting_claim: differs from derived {derived_cost_claim}"
        )

    attempt_count = attempt_result["attempt_count"]
    highest_retry = attempt_result["highest_retry_index"]
    budget_overrun = highest_retry is not None and highest_retry > retry_budget
    forced_block = attempt_result["forced_block_sequence"] is not None
    budget_exhausted = (
        highest_retry is not None
        and highest_retry >= retry_budget
        and not verified_completion
    )
    if budget_overrun or forced_block or budget_exhausted:
        derived_state = "blocked"
    elif verified_completion:
        derived_state = "complete"
    elif checkpoint is not None:
        derived_state = "candidate_complete"
    elif attempt_count == 0:
        derived_state = "pending"
    else:
        derived_state = "active"

    if reported_state in PACKET_STATES and reported_state != derived_state:
        errors.append(
            f"ledger.reported_state: {reported_state} differs from derived {derived_state}"
        )
    if packet_state == "complete" and (budget_overrun or forced_block or budget_exhausted):
        errors.append("budget or no-progress exhaustion cannot be relabelled complete")

    unique_errors = sorted(set(errors))
    return {
        "status": "pass" if not unique_errors else "fail",
        "policy_id": policy["policy_id"],
        "packet_id": packet.get("packet_id"),
        "packet_contract_sha256": contract_digest,
        "attempt_count": attempt_count,
        "highest_retry_index": highest_retry,
        "retry_budget": retry_budget,
        "reported_packet_state": packet_state,
        "derived_state": derived_state,
        "progress_attempt_count": attempt_result["progress_attempt_count"],
        "consecutive_same_blocker_no_progress": attempt_result[
            "consecutive_same_blocker_no_progress"
        ],
        "cost_accounting": derived_cost_claim,
        "acceptance_verified": acceptance_verified,
        "errors": unique_errors,
        "platform_and_process_limitations": policy["platform_and_process_limitations"],
    }


def failure_result(
    errors: list[str], policy: dict[str, Any] | None = None
) -> dict[str, Any]:
    limitations = []
    policy_id = None
    if isinstance(policy, dict):
        policy_id = policy.get("policy_id")
        raw = policy.get("platform_and_process_limitations")
        if isinstance(raw, list) and all(isinstance(item, str) for item in raw):
            limitations = raw
    return {
        "status": "fail",
        "policy_id": policy_id,
        "packet_id": None,
        "packet_contract_sha256": None,
        "attempt_count": 0,
        "highest_retry_index": None,
        "retry_budget": None,
        "reported_packet_state": None,
        "derived_state": "invalid",
        "progress_attempt_count": 0,
        "consecutive_same_blocker_no_progress": 0,
        "cost_accounting": "partial",
        "acceptance_verified": False,
        "errors": sorted(set(errors)),
        "platform_and_process_limitations": limitations,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=SCRIPT_PROJECT_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--json", action="store_true", help="Emit one JSON result.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = verify(args.project_root, args.policy, args.packet, args.ledger)
    except Exception as exc:  # pragma: no cover - final fail-closed boundary
        result = failure_result(
            [f"internal verifier error: {type(exc).__name__}: {exc}"]
        )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["status"] == "pass":
        print(
            "execution-loop verification passed: "
            f"state={result['derived_state']}, attempts={result['attempt_count']}, "
            f"cost={result['cost_accounting']}"
        )
    else:
        print("execution-loop verification failed", file=sys.stderr)
        for error in result["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
