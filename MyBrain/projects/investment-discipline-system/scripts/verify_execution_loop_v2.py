#!/usr/bin/env python3
"""Verify current work-packet execution observations without self-reference."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import verify_work_packets as work_packets


DEFAULT_POLICY = Path("governance/EXECUTION_LOOP_POLICY_V2.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PACKET_ID_RE = re.compile(r"^WP-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
FAILURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{2,4}$")
ROOT_CAUSE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){1,15}$")
TIMESTAMP_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$"
)
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
REVIEW_REF_RE = re.compile(r"^refs/tags/ids-reviewed/WP-[A-Z0-9]+(?:-[A-Z0-9]+)*$")

POLICY_FIELDS = {
    "schema_version",
    "status",
    "policy_id",
    "linked_failure_ids",
    "work_packets",
    "ledger_schema",
    "current_snapshot",
    "progress_derivation",
    "baseline_observation",
    "stopping_rules",
    "completion_semantics",
    "recorder_runtime",
    "cost_accounting",
    "legacy_v1_history",
    "completed_before_v2_exemptions",
    "platform_and_process_limitations",
}
LEDGER_FIELDS = {
    "schema_version",
    "packet_id",
    "packet_path",
    "packet_contract_sha256",
    "reported_state",
    "cost_accounting_claim",
    "initial_state",
    "terminal_completion",
    "attempts",
}
INITIAL_STATE_FIELDS = {"failure_ids", "evidence"}
TERMINAL_COMPLETION_FIELDS = {
    "authority_kind",
    "packet_contract_sha256",
    "latest_record_sha256",
    "controlled_claims_sha256",
    "checkpoint_path",
    "checkpoint_canonical_sha256",
    "acceptance_path",
    "acceptance_canonical_sha256",
    "execution_receipt_path",
    "execution_receipt_canonical_sha256",
    "completion_seal",
}
COMPLETION_SEAL_FIELDS = {
    "schema_version",
    "candidate_commit",
    "candidate_tree",
    "candidate_packet_canonical_sha256",
    "candidate_ledger_canonical_sha256",
    "candidate_checkpoint_canonical_sha256",
    "candidate_acceptance_canonical_sha256",
    "candidate_execution_receipt_canonical_sha256",
    "review_commit",
    "review_tree",
    "review_path",
    "review_canonical_sha256",
    "anchor_ref",
    "anchor_commit",
    "anchor_authority",
}
INDEPENDENT_REVIEW_FIELDS = {
    "schema_version",
    "packet_id",
    "candidate_commit",
    "candidate_tree",
    "candidate_terminal_canonical_sha256",
    "reviewer_mode",
    "verdict",
    "findings",
    "limitations",
}
ATTEMPT_FIELDS = {
    "schema_version",
    "attempt_kind",
    "sequence",
    "retry_index",
    "started_at",
    "ended_at",
    "wall_time_ms",
    "blocker",
    "failure_delta",
    "evidence_delta",
    "controlled_snapshot",
    "process_observation",
    "cost_observation",
    "declared_progress",
    "previous_attempt_sha256",
    "record_sha256",
}
BLOCKER_FIELDS = {
    "root_cause_id",
    "failure_ids",
    "root_cause",
    "status_after",
    "fingerprint_sha256",
}
FAILURE_DELTA_FIELDS = {"before", "after", "resolved", "introduced"}
EVIDENCE_DELTA_FIELDS = {"before", "after", "added", "removed"}
EVIDENCE_FIELDS = {"path", "sha256", "kind", "supports_failure_ids"}
SNAPSHOT_FIELDS = {
    "algorithm",
    "excluded_paths",
    "claims",
    "claims_sha256",
}
PROCESS_OBSERVATION_FIELDS = {
    "mode",
    "argv",
    "exit_code",
    "stdout_sha256",
    "stderr_sha256",
    "stdout_bytes",
    "stderr_bytes",
    "capture_authority",
}
EXECUTION_RECEIPT_FIELDS = {
    "schema_version",
    "packet_id",
    "packet_contract_sha256",
    "checks",
}
EXECUTION_CHECK_FIELDS = {
    "check_id",
    "argv",
    "expected_exit_code",
    "actual_exit_code",
    "started_at",
    "ended_at",
    "wall_time_ms",
    "stdout_sha256",
    "stderr_sha256",
    "stdout_bytes",
    "stderr_bytes",
}
CLAIM_FIELDS = {"path", "kind", "state", "content_sha256"}
COST_FIELDS = {"wall_time_source", "token_usage"}
TOKEN_FIELDS = {
    "availability",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "measurement_source",
}
V2_CONTRACT_FIELDS = (
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
    "depends_on",
    "activates",
    "integration_invariants",
    "routing",
)

EXPECTED_WORK_PACKETS = {
    "policy_path": "governance/WORK_PACKET_POLICY_V2.json",
    "packet_directory": ".work_packets/packets",
    "packet_filename_suffix": ".packet.json",
    "live_schema_version": "work-packet-instance/v2",
    "historical_schema_versions": ["work-packet-instance/v1"],
    "ledger_required_states": [
        "pending",
        "active",
        "blocked",
        "candidate_complete",
        "complete",
    ],
    "historical_state": "superseded",
    "ledger_claim_rule": ("derived_runtime_sidecar_must_not_be_in_bounded_write_paths"),
}
EXPECTED_LEDGER_SCHEMA = {
    "directory": ".work_packets/attempts",
    "filename_template": "{packet_id}.attempts.v2.json",
    "ledger_schema_version": "execution-attempt-ledger/v2",
    "ledger_required_fields": [
        "schema_version",
        "packet_id",
        "packet_path",
        "packet_contract_sha256",
        "reported_state",
        "cost_accounting_claim",
        "initial_state",
        "terminal_completion",
        "attempts",
    ],
    "initial_state_required_fields": [
        "failure_ids",
        "evidence",
    ],
    "terminal_completion_required_fields": [
        "authority_kind",
        "packet_contract_sha256",
        "latest_record_sha256",
        "controlled_claims_sha256",
        "checkpoint_path",
        "checkpoint_canonical_sha256",
        "acceptance_path",
        "acceptance_canonical_sha256",
        "execution_receipt_path",
        "execution_receipt_canonical_sha256",
        "completion_seal",
    ],
    "attempt_schema_version": "execution-attempt/v2",
    "attempt_required_fields": [
        "schema_version",
        "attempt_kind",
        "sequence",
        "retry_index",
        "started_at",
        "ended_at",
        "wall_time_ms",
        "blocker",
        "failure_delta",
        "evidence_delta",
        "controlled_snapshot",
        "process_observation",
        "cost_observation",
        "declared_progress",
        "previous_attempt_sha256",
        "record_sha256",
    ],
    "attempt_kind_values": ["baseline_observation", "execution_attempt"],
    "blocker_required_fields": [
        "root_cause_id",
        "failure_ids",
        "root_cause",
        "status_after",
        "fingerprint_sha256",
    ],
    "failure_delta_required_fields": [
        "before",
        "after",
        "resolved",
        "introduced",
    ],
    "evidence_delta_required_fields": [
        "before",
        "after",
        "added",
        "removed",
    ],
    "evidence_reference_required_fields": [
        "path",
        "sha256",
        "kind",
        "supports_failure_ids",
    ],
    "controlled_snapshot_required_fields": [
        "algorithm",
        "excluded_paths",
        "claims",
        "claims_sha256",
    ],
    "process_observation_required_fields": [
        "mode",
        "argv",
        "exit_code",
        "stdout_sha256",
        "stderr_sha256",
        "stdout_bytes",
        "stderr_bytes",
        "capture_authority",
    ],
    "process_observation_modes": [
        "baseline",
        "passive",
        "run",
        "indeterminate",
    ],
    "claim_snapshot_required_fields": [
        "path",
        "kind",
        "state",
        "content_sha256",
    ],
    "cost_observation_required_fields": ["wall_time_source", "token_usage"],
    "token_usage_required_fields": [
        "availability",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "measurement_source",
    ],
    "first_sequence": 1,
    "first_execution_retry_index": 0,
    "timestamp_format": "RFC3339_UTC_Z_MILLISECONDS",
    "record_hash_rule": "canonical_sha256_of_attempt_without_record_sha256",
}
EXPECTED_CURRENT_SNAPSHOT = {
    "algorithm": "canonical_sha256_of_sorted_claim_snapshots_v1",
    "source": "packet.bounded_write_paths",
    "excluded_claim_rule": (
        "runtime_ledgers_and_generated_views_must_not_be_bounded_write_claims"
    ),
    "excluded_generated_view_paths": [
        "STATUS.md",
        "TASK_BOARD.md",
        "LOOP_RUN_LOG.md",
    ],
    "file_hash": "raw_sha256",
    "tree_hash": "canonical_sha256_of_sorted_relative_entry_records",
    "absent_state": "explicit_null_digest",
    "latest_attempt_must_equal_current_claims": True,
    "pending_requires_baseline_observation": True,
    "packet_ledger_and_generated_view_files_cannot_count_as_progress_evidence": True,
}
EXPECTED_PROGRESS = {
    "declared_progress_must_equal_derived": True,
    "failure_delta_must_be_set_difference": True,
    "evidence_delta_must_be_set_difference": True,
    "latest_evidence_after_must_match_current_regular_files": True,
    "progress_requires": "verified_evidence_addition_or_failure_resolution",
    "resolved_failure_requires_added_supporting_evidence": True,
    "progress_evidence_must_be_controlled_write_claim": True,
    "first_attempt_before_state_source": "ledger.initial_state",
    "cross_attempt_failure_state_continuity": True,
    "cross_attempt_evidence_state_continuity": True,
    "introduced_resolved_and_support_ids_must_be_closed": True,
    "allowed_evidence_kinds": ["policy", "implementation", "test", "other"],
}
EXPECTED_BASELINE = {
    "only_first_attempt": True,
    "allowed_reported_states": ["pending", "active"],
    "retry_index": None,
    "declared_progress": False,
    "failure_and_evidence_deltas_must_be_empty": True,
    "blocker_status_after": "waiting",
    "pending_ledger_exact_attempt_count": 1,
    "pending_ledger_only_attempt_kind": "baseline_observation",
}
EXPECTED_STOPPING = {
    "same_blocker_consecutive_no_progress_threshold": 3,
    "same_blocker_threshold_outcome": "blocked",
    "consecutive_no_progress_threshold": 3,
    "consecutive_no_progress_threshold_outcome": "blocked",
    "retry_budget_source": "packet.retry_budget",
    "retry_budget_meaning": "maximum_execution_attempt_count",
    "execution_attempt_retry_indices_contiguous_from_zero": True,
    "retry_index_at_or_above_budget_outcome": "invalid",
    "budget_exhausted_without_verified_acceptance_outcome": "blocked",
    "every_historical_prefix_is_evaluated": True,
    "first_forced_stop_is_absorbing": True,
    "blocked_continuation_requires": "successor_packet",
}
EXPECTED_COMPLETION = {
    "local_receipts_are": (
        "self_reported_candidate_evidence_not_authenticated_execution"
    ),
    "candidate_complete_and_complete_require_latest_execution_status": ("resolved"),
    "terminal_completion_required_states": [
        "candidate_complete",
        "complete",
    ],
    "candidate_terminal_authority_kind": "self_reported_local_candidate",
    "sealed_terminal_authority_kind": "git_review_sealed_candidate",
    "terminal_record_must_bind_latest_attempt_snapshot_contract_and_receipts": True,
    "execution_receipt_schema_version": "execution-finalization-receipt/v2",
    "execution_receipt_required_fields": [
        "schema_version",
        "packet_id",
        "packet_contract_sha256",
        "checks",
    ],
    "execution_check_required_fields": [
        "check_id",
        "argv",
        "expected_exit_code",
        "actual_exit_code",
        "started_at",
        "ended_at",
        "wall_time_ms",
        "stdout_sha256",
        "stderr_sha256",
        "stdout_bytes",
        "stderr_bytes",
    ],
    "execution_receipt_checks_must_exactly_match_packet_acceptance_checks": True,
    "execution_check_timestamps_and_output_digests_required": True,
    "terminal_completion_is_append_absorbing": True,
    "candidate_complete_does_not_activate_successors": True,
    "complete_requires_content_addressed_candidate_and_independent_review_ref": True,
    "review_sidecar_directory": ".work_packets/reviews",
    "review_schema_version": "work-packet-independent-review/v2",
    "seal_schema_version": "execution-completion-seal/v2",
    "seal_anchor_ref_template": "refs/tags/ids-reviewed/{packet_id}",
    "controlled_change_after_complete_requires": (
        "successor_packet_supersession_in_v2"
    ),
    "authenticated_completion_authority": (
        "git_content_addressed_candidate_plus_independent_read_only_review_ref"
    ),
    "design_freeze_or_product_completion_may_not_be_inferred": True,
}
EXPECTED_RECORDER = {
    "script_path": "scripts/record_execution_attempt_v2.py",
    "transaction_directory": ".work_packets/runtime-transactions",
    "operation_directory": ".work_packets/runtime-operations",
    "lock_directory_scope": "system_temp_by_project_packet_and_global_transaction",
    "per_packet_lock": True,
    "global_transaction_lock": True,
    "global_operation_lock": True,
    "expected_tail_compare_and_swap": True,
    "existing_attempt_records_are_immutable": True,
    "before_after_snapshots_are_tool_observed": True,
    "run_mode_captures_process_exit_and_output_digest": True,
    "passive_mode_is_self_reported": True,
    "operation_intent_is_durable_before_process_launch": True,
    "process_outcome_is_durable_before_ledger_commit": True,
    "process_outcome_and_controlled_snapshot_share_one_durable_envelope": True,
    "post_outcome_snapshot_divergence_preserves_prior_failures_and_blocks": True,
    "missing_process_outcome_recovers_as_explicit_indeterminate_block": True,
    "failed_or_indeterminate_process_preserves_prior_failures": True,
    "caller_transition_is_validated_before_durable_operation": True,
    "proposed_attempt_chain_is_validated_before_commit_plan": True,
    "acceptance_check_timeout_seconds": 7200,
    "max_captured_output_bytes_per_stream": 16777216,
    "output_limit_exit_code": 125,
    "ledger_write": "atomic_replace_after_fsync",
    "interrupted_multi_file_transition": (
        "discard_verified_precommit_prepare_or_roll_forward_durable_commit_journal"
    ),
    "operation_remains_pending_through_view_refresh": True,
    "ordinary_verifier_rejects_pending_operations": True,
    "post_write_verifier_required": True,
}
EXPECTED_COST = {
    "wall_time_source": "started_at_and_ended_at",
    "attempt_timestamps_nondecreasing": True,
    "token_availability_values": ["measured", "unknown"],
    "unknown_tokens_require_null_counts_and_source": True,
    "measured_tokens_require_nonnegative_counts_sum_and_source": True,
    "ledger_claim_values": ["measured", "partial"],
    "any_unknown_token_observation_forces_partial": True,
}
EXPECTED_LEGACY = {
    "authority": "historical_bytes_only_not_current_execution_authority",
    "artifacts": [
        {
            "path": "governance/EXECUTION_LOOP_POLICY_V1.json",
            "sha256": "bab2e798cf44534bd2168c6ce9d11f2f8e4e5935b321a73575dd72fc9d52c75f",
        },
        {
            "path": "scripts/verify_execution_loop.py",
            "sha256": "7e45eac95733369a34cb68c209c3bef47ea726d9d0ba478231103308f248fbe2",
        },
        {
            "path": ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json",
            "sha256": "038dc1e4338a1e759d50279de2c923febfa4d64fcf96607229c8b5d8f5773b75",
        },
    ],
}
EXPECTED_EXEMPTIONS = [
    {
        "packet_id": "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY",
        "packet_path": (
            ".work_packets/packets/WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY.packet.json"
        ),
        "packet_schema_version": "work-packet-instance/v2",
        "packet_state": "complete",
        "packet_contract_sha256": (
            "1f98863e7ab1fee7a511dc712c2ceb5e7bdea8ba20b8ab0e4f7f0ce0344a7b76"
        ),
        "checkpoint_path": (
            ".work_packets/receipts/"
            "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY.checkpoint.json"
        ),
        "checkpoint_canonical_sha256": (
            "699582eaedcbff2d712a9636c1808f5ce1ab6d613decd60f21257fb48d63a8f8"
        ),
        "acceptance_path": (
            ".work_packets/receipts/"
            "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY.acceptance.json"
        ),
        "acceptance_canonical_sha256": (
            "c918091a5bcf3a0e657948590ced6a2d0531e8b3983fcc51c93fd94e98e14145"
        ),
        "reason": (
            "Completed and receipt-bound before the V2 execution-ledger "
            "runtime was activated."
        ),
    }
]
EXPECTED_LIMITATIONS = [
    "Content snapshots and ledger hashes are tamper-evident consistency checks, not proof of who wrote the bytes or when the work actually occurred.",
    "The verifier does not execute work-packet acceptance commands and does not treat a hand-written actual_exit_code as authenticated process evidence.",
    "A dishonest author can split one semantic blocker into different root-cause identifiers; candidate-bound independent review remains required.",
    "Filesystem checks are point-in-time and cannot eliminate time-of-check/time-of-use, mount replacement, hard-link alias, or every case-folding race.",
    "Tree hashing rejects observed symlinks and special entries but does not provide operating-system sandboxing or distributed locking.",
    "A pending baseline proves only the current bytes were observed; it does not prove the work was authorized, unstarted, or produced after the prerequisite state.",
    "The formal recorder prevents cooperative concurrent writers from overwriting one another, but a process with arbitrary filesystem access can still bypass it and rewrite local history; immutable Git candidates and independent review remain required.",
    "A process outcome and its durable controlled snapshot establish one observed interval boundary, not semantic causality between the command and every changed byte.",
    "Recorder process-group recovery controls descendants that remain in the owned process group; a deliberately detached descendant can escape that boundary and requires operating-system sandboxing.",
    "Captured stdout and stderr are each bounded; exit 125 means the configured evidence-capture limit was exceeded and the retained digest covers only the bounded captured prefix.",
    "A local Git review tag raises the cost and visibility of coherent rewrites but is not an authenticated identity or protected remote ref; hostile-author resistance requires pushing the tag to a protected remote and verifying that external ref.",
    "A V2 blocked or completed packet cannot resume in place; continued work requires a named successor packet so the prior terminal chain remains visible.",
    "Legacy V1 artifacts are hash-retained history only and cannot be used to assert current V2 freshness.",
    "Current execution freshness does not prove research sufficiency, design freeze, product completion, or investment effectiveness.",
]


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite a prior key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )


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


def exact_keys(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[str],
) -> bool:
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


def is_int(value: Any) -> bool:
    return type(value) is int


def unique_strings(
    value: Any,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> list[str] | None:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        errors.append(f"{label}: must be a unique string list")
        return None
    return value


def normalized_relative(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip():
        errors.append(f"{label}: must be a non-empty normalized relative path")
        return None
    if "\\" in value or any(character in value for character in "*?[]{}"):
        errors.append(f"{label}: backslashes and glob syntax are forbidden")
        return None
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or value in {".", "..", "~"}
        or any(part in {"", ".", "..", "~"} for part in path.parts)
        or posixpath.normpath(value) != value
    ):
        errors.append(f"{label}: path is not normalized project-relative")
        return None
    return value


def resolve_path(
    root: Path,
    relative: Any,
    label: str,
    errors: list[str],
    *,
    must_exist: bool,
) -> Path | None:
    normalized = normalized_relative(relative, label, errors)
    if normalized is None:
        return None
    candidate = root.joinpath(*PurePosixPath(normalized).parts)
    cursor = root
    try:
        for part in PurePosixPath(normalized).parts:
            cursor = cursor / part
            if cursor.exists() and cursor.is_symlink():
                errors.append(f"{label}: symlink components are forbidden")
                return None
        resolved_parent = candidate.parent.resolve(strict=True)
        if root != resolved_parent and root not in resolved_parent.parents:
            errors.append(f"{label}: canonical parent escapes project root")
            return None
        if must_exist:
            resolved = candidate.resolve(strict=True)
            if root != resolved and root not in resolved.parents:
                errors.append(f"{label}: canonical path escapes project root")
                return None
            if candidate.is_symlink():
                errors.append(f"{label}: symlink leaf is forbidden")
                return None
    except (OSError, RuntimeError) as exc:
        errors.append(f"{label}: cannot resolve safely: {exc}")
        return None
    if must_exist and not candidate.exists():
        errors.append(f"{label}: required path is absent")
        return None
    return candidate


def validate_policy(policy: Any, errors: list[str]) -> bool:
    if not exact_keys(policy, POLICY_FIELDS, "policy", errors):
        return False
    expected_scalars = {
        "schema_version": "execution-loop-policy/v2",
        "status": "candidate_for_freeze",
        "policy_id": "ids-execution-loop-v2",
        "linked_failure_ids": ["ECO-01", "ORG-04"],
        "work_packets": EXPECTED_WORK_PACKETS,
        "ledger_schema": EXPECTED_LEDGER_SCHEMA,
        "current_snapshot": EXPECTED_CURRENT_SNAPSHOT,
        "progress_derivation": EXPECTED_PROGRESS,
        "baseline_observation": EXPECTED_BASELINE,
        "stopping_rules": EXPECTED_STOPPING,
        "completion_semantics": EXPECTED_COMPLETION,
        "recorder_runtime": EXPECTED_RECORDER,
        "cost_accounting": EXPECTED_COST,
        "legacy_v1_history": EXPECTED_LEGACY,
        "completed_before_v2_exemptions": EXPECTED_EXEMPTIONS,
        "platform_and_process_limitations": EXPECTED_LIMITATIONS,
    }
    for field, expected in expected_scalars.items():
        if policy.get(field) != expected:
            errors.append(f"policy.{field}: differs from executable contract")
    return not errors


def ledger_path_for(packet_id: str) -> str:
    return f".work_packets/attempts/{packet_id}.attempts.v2.json"


def is_v2_ledger_path(value: str, live_packet_ids: set[str]) -> bool:
    return value in {ledger_path_for(packet_id) for packet_id in live_packet_ids}


def tree_sha256(directory: Path, label: str, errors: list[str]) -> str | None:
    start = len(errors)
    records: list[dict[str, str]] = []

    def onerror(exc: OSError) -> None:
        errors.append(f"{label}: tree traversal failed: {exc}")

    try:
        for current, directories, filenames in os.walk(
            directory,
            topdown=True,
            followlinks=False,
            onerror=onerror,
        ):
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
                        {
                            "path": relative,
                            "type": "file",
                            "sha256": raw_sha256(child),
                        }
                    )
                else:
                    errors.append(
                        f"{label}: special filesystem entry is forbidden: {relative}"
                    )
    except OSError as exc:
        errors.append(f"{label}: tree traversal failed: {exc}")
        return None
    if len(errors) != start:
        return None
    return canonical_sha256(records)


def current_claim_snapshots(
    root: Path,
    packet: dict[str, Any],
    live_packet_ids: set[str],
    errors: list[str],
) -> tuple[list[str], list[dict[str, Any]]]:
    excluded: list[str] = []
    claims: list[dict[str, Any]] = []
    raw_claims = packet.get("bounded_write_paths")
    if not isinstance(raw_claims, list):
        errors.append(f"packet {packet.get('packet_id')}: write claims must be a list")
        return excluded, claims
    for index, claim in enumerate(raw_claims):
        label = f"packet {packet.get('packet_id')} write[{index}]"
        if not exact_keys(claim, {"path", "kind"}, label, errors):
            continue
        relative = normalized_relative(claim["path"], f"{label}.path", errors)
        kind = claim["kind"]
        if kind not in {"file", "tree"}:
            errors.append(f"{label}.kind: unsupported claim kind")
            continue
        if relative is None:
            continue
        if relative in set(EXPECTED_CURRENT_SNAPSHOT["excluded_generated_view_paths"]):
            errors.append(
                f"{label}: generated project-state views are runtime sidecars "
                "and cannot be bounded product write claims"
            )
            continue
        if relative.startswith(".work_packets/attempts/"):
            errors.append(
                f"{label}: execution ledgers are derived runtime sidecars and "
                "cannot be bounded product write claims"
            )
            continue
        candidate = resolve_path(
            root,
            relative,
            f"{label}.path",
            errors,
            must_exist=False,
        )
        if candidate is None:
            continue
        if not candidate.exists():
            snapshot = {
                "path": relative,
                "kind": kind,
                "state": "absent",
                "content_sha256": None,
            }
        elif kind == "file":
            if not candidate.is_file() or candidate.is_symlink():
                errors.append(f"{label}: file claim is not a regular file")
                continue
            snapshot = {
                "path": relative,
                "kind": kind,
                "state": "file",
                "content_sha256": raw_sha256(candidate),
            }
        else:
            if not candidate.is_dir() or candidate.is_symlink():
                errors.append(f"{label}: tree claim is not a regular directory")
                continue
            digest = tree_sha256(candidate, label, errors)
            if digest is None:
                continue
            snapshot = {
                "path": relative,
                "kind": kind,
                "state": "tree",
                "content_sha256": digest,
            }
        claims.append(snapshot)
    excluded.sort()
    claims.sort(key=lambda item: (item["path"], item["kind"]))
    return excluded, claims


def validate_claim_snapshot(
    value: Any,
    label: str,
    errors: list[str],
) -> bool:
    if not exact_keys(value, CLAIM_FIELDS, label, errors):
        return False
    state = value["state"]
    digest = value["content_sha256"]
    valid = (
        isinstance(value["path"], str)
        and value["kind"] in {"file", "tree"}
        and state in {"absent", "file", "tree"}
        and (
            (state == "absent" and digest is None)
            or (
                state != "absent"
                and isinstance(digest, str)
                and SHA256_RE.fullmatch(digest) is not None
            )
        )
    )
    if not valid:
        errors.append(f"{label}: invalid claim snapshot")
    return valid


def evidence_identity(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        item["path"],
        item["sha256"],
        item["kind"],
        tuple(item["supports_failure_ids"]),
    )


def validate_evidence_list(
    value: Any,
    label: str,
    root: Path,
    packet_path: str,
    live_packet_ids: set[str],
    controlled_claims: list[dict[str, Any]],
    allowed_kinds: set[str],
    errors: list[str],
    *,
    require_current: bool,
) -> list[dict[str, Any]] | None:
    if not isinstance(value, list):
        errors.append(f"{label}: must be a list")
        return None
    identities: set[tuple[Any, ...]] = set()
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        if not exact_keys(item, EVIDENCE_FIELDS, item_label, errors):
            continue
        path = normalized_relative(item["path"], f"{item_label}.path", errors)
        digest = item["sha256"]
        kind = item["kind"]
        support = unique_strings(
            item["supports_failure_ids"],
            f"{item_label}.supports_failure_ids",
            errors,
        )
        if support is not None and any(
            FAILURE_ID_RE.fullmatch(failure_id) is None for failure_id in support
        ):
            errors.append(f"{item_label}: invalid supported failure_id")
        if (
            path is None
            or not isinstance(digest, str)
            or SHA256_RE.fullmatch(digest) is None
            or kind not in allowed_kinds
        ):
            errors.append(f"{item_label}: invalid evidence reference")
            continue
        if path == packet_path or is_v2_ledger_path(path, live_packet_ids):
            errors.append(f"{item_label}: packet and ledger files cannot be evidence")
        if not any(
            path == claim["path"]
            or (claim["kind"] == "tree" and path.startswith(f"{claim['path']}/"))
            for claim in controlled_claims
        ):
            errors.append(
                f"{item_label}: progress evidence is outside controlled writes"
            )
        if require_current:
            candidate = resolve_path(
                root,
                path,
                f"{item_label}.path",
                errors,
                must_exist=True,
            )
            if candidate is not None:
                if not candidate.is_file() or candidate.is_symlink():
                    errors.append(f"{item_label}: evidence must be a regular file")
                elif raw_sha256(candidate) != digest:
                    errors.append(
                        f"{item_label}: evidence hash differs from current file"
                    )
        identity = evidence_identity(item)
        if identity in identities:
            errors.append(f"{item_label}: duplicate evidence reference")
        identities.add(identity)
        result.append(item)
    if result != sorted(result, key=evidence_identity):
        errors.append(f"{label}: evidence references must be sorted")
    return result


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or TIMESTAMP_RE.fullmatch(value) is None:
        errors.append(f"{label}: invalid UTC millisecond timestamp")
        return None
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        errors.append(f"{label}: invalid timestamp value")
        return None
    return parsed.replace(tzinfo=UTC)


def validate_cost(
    value: Any,
    label: str,
    errors: list[str],
) -> bool:
    if not exact_keys(value, COST_FIELDS, label, errors):
        return False
    if value["wall_time_source"] != "timestamps":
        errors.append(f"{label}: wall_time_source differs")
    token = value["token_usage"]
    if not exact_keys(token, TOKEN_FIELDS, f"{label}.token_usage", errors):
        return False
    availability = token["availability"]
    if availability == "unknown":
        if any(
            token[field] is not None
            for field in (
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "measurement_source",
            )
        ):
            errors.append(f"{label}: unknown token usage requires null details")
    elif availability == "measured":
        counts = [
            token["input_tokens"],
            token["output_tokens"],
            token["total_tokens"],
        ]
        if (
            any(not is_int(count) or count < 0 for count in counts)
            or counts[0] + counts[1] != counts[2]
            or not isinstance(token["measurement_source"], str)
            or not token["measurement_source"]
        ):
            errors.append(f"{label}: measured token usage is invalid")
    else:
        errors.append(f"{label}: unsupported token availability")
    return availability == "unknown"


def validate_process_observation(
    value: Any,
    kind: Any,
    label: str,
    errors: list[str],
) -> None:
    if not exact_keys(
        value,
        PROCESS_OBSERVATION_FIELDS,
        f"{label}.process_observation",
        errors,
    ):
        return
    mode = value["mode"]
    if mode not in {"baseline", "passive", "run", "indeterminate"}:
        errors.append(f"{label}.process_observation: unsupported mode")
        return
    if kind == "baseline_observation" and mode != "baseline":
        errors.append(
            f"{label}.process_observation: baseline attempt requires baseline mode"
        )
    if kind == "execution_attempt" and mode == "baseline":
        errors.append(
            f"{label}.process_observation: execution attempt cannot use baseline mode"
        )
    if mode in {"baseline", "passive"}:
        expected_authority = (
            "tool_observed_baseline"
            if mode == "baseline"
            else "self_reported_no_process"
        )
        if value["capture_authority"] != expected_authority or any(
            value[field] is not None
            for field in (
                "argv",
                "exit_code",
                "stdout_sha256",
                "stderr_sha256",
                "stdout_bytes",
                "stderr_bytes",
            )
        ):
            errors.append(f"{label}.process_observation: {mode} semantics differ")
        return
    if mode == "indeterminate":
        if (
            value["capture_authority"] != "durable_intent_without_recoverable_outcome"
            or not isinstance(value["argv"], list)
            or not value["argv"]
            or any(not isinstance(item, str) or not item for item in value["argv"])
            or any(
                value[field] is not None
                for field in (
                    "exit_code",
                    "stdout_sha256",
                    "stderr_sha256",
                    "stdout_bytes",
                    "stderr_bytes",
                )
            )
        ):
            errors.append(
                f"{label}.process_observation: indeterminate semantics differ"
            )
        return
    argv = value["argv"]
    if (
        value["capture_authority"] != "recorder_executed_process"
        or not isinstance(argv, list)
        or not argv
        or any(not isinstance(item, str) or not item for item in argv)
        or not is_int(value["exit_code"])
        or any(
            not isinstance(value[field], str)
            or SHA256_RE.fullmatch(value[field]) is None
            for field in ("stdout_sha256", "stderr_sha256")
        )
        or any(
            not is_int(value[field]) or value[field] < 0
            for field in ("stdout_bytes", "stderr_bytes")
        )
    ):
        errors.append(f"{label}.process_observation: run semantics differ")


def validate_execution_receipt(
    value: Any,
    packet: dict[str, Any],
    contract_digest: str,
    not_before: datetime | None,
    label: str,
    errors: list[str],
) -> None:
    if not exact_keys(value, EXECUTION_RECEIPT_FIELDS, label, errors):
        return
    if (
        value["schema_version"] != "execution-finalization-receipt/v2"
        or value["packet_id"] != packet["packet_id"]
        or value["packet_contract_sha256"] != contract_digest
    ):
        errors.append(f"{label}: packet or schema binding differs")
    observations = value["checks"]
    declared_checks = packet["acceptance_checks"]
    if not isinstance(observations, list):
        errors.append(f"{label}.checks: must be a list")
        return
    if len(observations) != len(declared_checks):
        errors.append(f"{label}.checks: count differs from packet")
        return
    prior_ended = not_before
    for index, (observation, declared) in enumerate(
        zip(observations, declared_checks, strict=True)
    ):
        check_label = f"{label}.checks[{index}]"
        if not exact_keys(
            observation,
            EXECUTION_CHECK_FIELDS,
            check_label,
            errors,
        ):
            continue
        if (
            observation["check_id"] != declared["check_id"]
            or observation["argv"] != declared["argv"]
            or observation["expected_exit_code"] != declared["expected_exit_code"]
            or observation["actual_exit_code"] != declared["expected_exit_code"]
        ):
            errors.append(
                f"{check_label}: declaration or successful exit binding differs"
            )
        started = parse_timestamp(
            observation["started_at"],
            f"{check_label}.started_at",
            errors,
        )
        ended = parse_timestamp(
            observation["ended_at"],
            f"{check_label}.ended_at",
            errors,
        )
        wall_time_ms = observation["wall_time_ms"]
        if started is not None and ended is not None:
            expected_wall = int((ended - started).total_seconds() * 1000)
            if (
                ended < started
                or not is_int(wall_time_ms)
                or wall_time_ms != expected_wall
            ):
                errors.append(f"{check_label}: wall_time_ms differs from timestamps")
            if prior_ended is not None and started < prior_ended:
                errors.append(
                    f"{check_label}: started_at precedes the prior execution event"
                )
            prior_ended = ended
        if any(
            not isinstance(observation[field], str)
            or SHA256_RE.fullmatch(observation[field]) is None
            for field in ("stdout_sha256", "stderr_sha256")
        ):
            errors.append(f"{check_label}: output digest differs")
        if any(
            not is_int(observation[field]) or observation[field] < 0
            for field in ("stdout_bytes", "stderr_bytes")
        ):
            errors.append(f"{check_label}: output byte count differs")


def git_output(
    root: Path,
    argv: list[str],
    label: str,
    errors: list[str],
) -> bytes | None:
    try:
        completed = subprocess.run(
            ["git", *argv],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=15,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"{label}: Git observation failed: {exc}")
        return None
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        errors.append(f"{label}: Git observation failed: {detail}")
        return None
    return completed.stdout


def git_project_prefix(
    root: Path,
    label: str,
    errors: list[str],
) -> str | None:
    payload = git_output(
        root,
        ["rev-parse", "--show-prefix"],
        label,
        errors,
    )
    if payload is None:
        return None
    try:
        raw_prefix = payload.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        errors.append(f"{label}: Git project prefix is invalid: {exc}")
        return None
    if raw_prefix.startswith("/"):
        errors.append(f"{label}: Git project prefix is unsafe")
        return None
    prefix = raw_prefix[:-1] if raw_prefix.endswith("/") else raw_prefix
    if "\\" in prefix or any(part in {"", ".", ".."} for part in prefix.split("/")):
        if prefix:
            errors.append(f"{label}: Git project prefix is unsafe")
            return None
    return prefix


def git_json(
    root: Path,
    commit: str,
    relative: str,
    label: str,
    errors: list[str],
) -> Any | None:
    if GIT_OBJECT_RE.fullmatch(commit) is None:
        errors.append(f"{label}: invalid Git commit")
        return None
    normalized = normalized_relative(relative, f"{label}.path", errors)
    if normalized is None:
        return None
    prefix = git_project_prefix(
        root,
        f"{label}.project_prefix",
        errors,
    )
    if prefix is None:
        return None
    object_path = f"{prefix}/{normalized}" if prefix else normalized
    payload = git_output(
        root,
        ["show", f"{commit}:{object_path}"],
        label,
        errors,
    )
    if payload is None:
        return None
    try:
        return json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: committed JSON is invalid: {exc}")
        return None


def git_object_id(
    root: Path,
    revision: str,
    label: str,
    errors: list[str],
) -> str | None:
    payload = git_output(
        root,
        ["rev-parse", "--verify", revision],
        label,
        errors,
    )
    if payload is None:
        return None
    value = payload.decode("ascii", errors="replace").strip()
    if GIT_OBJECT_RE.fullmatch(value) is None:
        errors.append(f"{label}: Git object id is invalid")
        return None
    return value


def git_tree_entries(
    root: Path,
    commit: str,
    relative: str,
    *,
    recursive: bool,
    label: str,
    errors: list[str],
) -> tuple[str, list[dict[str, str]]] | None:
    normalized = normalized_relative(relative, f"{label}.path", errors)
    prefix = git_project_prefix(root, f"{label}.project_prefix", errors)
    if normalized is None or prefix is None:
        return None
    object_path = f"{prefix}/{normalized}" if prefix else normalized
    argv = ["ls-tree", "--full-tree", "-z"]
    if recursive:
        argv.extend(["-r", "-t"])
    argv.extend([commit, "--", f":(top){object_path}"])
    payload = git_output(root, argv, label, errors)
    if payload is None:
        return None
    entries: list[dict[str, str]] = []
    for raw_entry in payload.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
            mode, kind, object_id = metadata.decode("ascii").split(" ", 2)
            path = raw_path.decode("utf-8")
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{label}: malformed Git tree entry: {exc}")
            return None
        entries.append(
            {
                "mode": mode,
                "kind": kind,
                "object_id": object_id,
                "path": path,
            }
        )
    return object_path, entries


def git_blob_bytes(
    root: Path,
    object_id: str,
    label: str,
    errors: list[str],
) -> bytes | None:
    if GIT_OBJECT_RE.fullmatch(object_id) is None:
        errors.append(f"{label}: Git blob object id is invalid")
        return None
    return git_output(root, ["cat-file", "blob", object_id], label, errors)


def git_claim_snapshots(
    root: Path,
    commit: str,
    packet: dict[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for index, claim in enumerate(packet.get("bounded_write_paths", [])):
        relative = claim.get("path")
        kind = claim.get("kind")
        label = f"candidate claim[{index}]"
        observed = git_tree_entries(
            root,
            commit,
            relative,
            recursive=(kind == "tree"),
            label=label,
            errors=errors,
        )
        if observed is None:
            continue
        object_path, entries = observed
        relevant = [
            item
            for item in entries
            if item["path"] == object_path or item["path"].startswith(f"{object_path}/")
        ]
        top = [item for item in relevant if item["path"] == object_path]
        if not top:
            snapshots.append(
                {
                    "path": relative,
                    "kind": kind,
                    "state": "absent",
                    "content_sha256": None,
                }
            )
            continue
        if len(top) != 1:
            errors.append(f"{label}: candidate path has multiple top entries")
            continue
        top_entry = top[0]
        if kind == "file":
            if top_entry["kind"] != "blob" or top_entry["mode"] not in {
                "100644",
                "100755",
            }:
                errors.append(f"{label}: candidate file is not a regular Git blob")
                continue
            content = git_blob_bytes(
                root,
                top_entry["object_id"],
                f"{label}.blob",
                errors,
            )
            if content is None:
                continue
            snapshots.append(
                {
                    "path": relative,
                    "kind": kind,
                    "state": "file",
                    "content_sha256": hashlib.sha256(content).hexdigest(),
                }
            )
            continue
        if kind != "tree" or (
            top_entry["kind"] != "tree" or top_entry["mode"] != "040000"
        ):
            errors.append(f"{label}: candidate tree is not a Git tree")
            continue
        records: list[dict[str, str]] = []
        valid_tree = True
        for item in relevant:
            if item["path"] == object_path:
                continue
            child = item["path"][len(object_path) + 1 :]
            if item["kind"] == "tree" and item["mode"] == "040000":
                records.append({"path": child, "type": "directory"})
                continue
            if item["kind"] != "blob" or item["mode"] not in {
                "100644",
                "100755",
            }:
                errors.append(
                    f"{label}: candidate tree contains a symlink, "
                    "submodule, or special entry"
                )
                valid_tree = False
                break
            content = git_blob_bytes(
                root,
                item["object_id"],
                f"{label}.{child}",
                errors,
            )
            if content is None:
                valid_tree = False
                break
            records.append(
                {
                    "path": child,
                    "type": "file",
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
        if valid_tree:
            snapshots.append(
                {
                    "path": relative,
                    "kind": kind,
                    "state": "tree",
                    "content_sha256": canonical_sha256(records),
                }
            )
    return sorted(snapshots, key=lambda item: (item["path"], item["kind"]))


def validate_completion_seal(
    seal: Any,
    terminal: dict[str, Any],
    ledger: dict[str, Any],
    packet: dict[str, Any],
    root: Path,
    errors: list[str],
) -> None:
    packet_id = packet["packet_id"]
    label = f"ledger {packet_id}.terminal_completion.completion_seal"
    if not exact_keys(seal, COMPLETION_SEAL_FIELDS, label, errors):
        return
    candidate_commit = seal["candidate_commit"]
    review_commit = seal["review_commit"]
    if (
        seal["schema_version"] != "execution-completion-seal/v2"
        or not isinstance(candidate_commit, str)
        or GIT_OBJECT_RE.fullmatch(candidate_commit) is None
        or not isinstance(review_commit, str)
        or GIT_OBJECT_RE.fullmatch(review_commit) is None
        or candidate_commit == review_commit
        or not isinstance(seal["candidate_tree"], str)
        or GIT_OBJECT_RE.fullmatch(seal["candidate_tree"]) is None
        or not isinstance(seal["review_tree"], str)
        or GIT_OBJECT_RE.fullmatch(seal["review_tree"]) is None
        or any(
            not isinstance(seal[field], str) or SHA256_RE.fullmatch(seal[field]) is None
            for field in (
                "candidate_packet_canonical_sha256",
                "candidate_ledger_canonical_sha256",
                "candidate_checkpoint_canonical_sha256",
                "candidate_acceptance_canonical_sha256",
                "candidate_execution_receipt_canonical_sha256",
                "review_canonical_sha256",
            )
        )
        or seal["anchor_ref"] != f"refs/tags/ids-reviewed/{packet_id}"
        or REVIEW_REF_RE.fullmatch(seal["anchor_ref"]) is None
        or seal["anchor_commit"] != review_commit
        or seal["anchor_authority"]
        != "local_git_ref_content_addressed_not_authenticated_remote"
    ):
        errors.append(f"{label}: identity or schema binding differs")
        return

    candidate_tree = git_object_id(
        root,
        f"{candidate_commit}^{{tree}}",
        f"{label}.candidate_tree",
        errors,
    )
    review_tree = git_object_id(
        root,
        f"{review_commit}^{{tree}}",
        f"{label}.review_tree",
        errors,
    )
    anchor_commit = git_object_id(
        root,
        seal["anchor_ref"],
        f"{label}.anchor_ref",
        errors,
    )
    if candidate_tree is not None and candidate_tree != seal["candidate_tree"]:
        errors.append(f"{label}: candidate tree differs")
    if review_tree is not None and review_tree != seal["review_tree"]:
        errors.append(f"{label}: review tree differs")
    if anchor_commit is not None and anchor_commit != review_commit:
        errors.append(f"{label}: review anchor ref moved")
    ancestor = git_output(
        root,
        ["merge-base", "--is-ancestor", candidate_commit, review_commit],
        f"{label}.candidate_ancestry",
        errors,
    )
    if ancestor is None:
        return

    packet_relative = f".work_packets/packets/{packet_id}.packet.json"
    ledger_relative = ledger_path_for(packet_id)
    candidate_packet = git_json(
        root,
        candidate_commit,
        packet_relative,
        f"{label}.candidate_packet",
        errors,
    )
    candidate_ledger = git_json(
        root,
        candidate_commit,
        ledger_relative,
        f"{label}.candidate_ledger",
        errors,
    )
    if isinstance(candidate_packet, dict) and isinstance(candidate_ledger, dict):
        candidate_claims = git_claim_snapshots(
            root,
            candidate_commit,
            candidate_packet,
            errors,
        )
        candidate_attempts = candidate_ledger.get("attempts")
        candidate_latest = (
            candidate_attempts[-1]
            if isinstance(candidate_attempts, list) and candidate_attempts
            else None
        )
        candidate_snapshot = (
            candidate_latest.get("controlled_snapshot")
            if isinstance(candidate_latest, dict)
            else None
        )
        if (
            not isinstance(candidate_snapshot, dict)
            or candidate_claims != candidate_snapshot.get("claims")
            or canonical_sha256(candidate_claims)
            != candidate_snapshot.get("claims_sha256")
        ):
            errors.append(
                f"{label}: candidate Git controlled claims differ from "
                "the accepted snapshot"
            )
    receipt_specs = (
        (
            terminal["checkpoint_path"],
            "candidate_checkpoint_canonical_sha256",
            "candidate_checkpoint",
        ),
        (
            terminal["acceptance_path"],
            "candidate_acceptance_canonical_sha256",
            "candidate_acceptance",
        ),
        (
            terminal["execution_receipt_path"],
            "candidate_execution_receipt_canonical_sha256",
            "candidate_execution_receipt",
        ),
    )
    candidate_receipts: dict[str, Any] = {}
    for relative, digest_field, receipt_label in receipt_specs:
        value = git_json(
            root,
            candidate_commit,
            relative,
            f"{label}.{receipt_label}",
            errors,
        )
        candidate_receipts[receipt_label] = value
        if value is not None and canonical_sha256(value) != seal[digest_field]:
            errors.append(f"{label}: {receipt_label} digest differs")
    if candidate_packet is not None:
        expected_packet = dict(packet)
        expected_packet["state"] = "candidate_complete"
        if candidate_packet != expected_packet:
            errors.append(f"{label}: candidate packet differs from sealed transition")
        if (
            canonical_sha256(candidate_packet)
            != seal["candidate_packet_canonical_sha256"]
        ):
            errors.append(f"{label}: candidate packet digest differs")
    if isinstance(candidate_ledger, dict):
        expected_terminal = dict(terminal)
        expected_terminal["authority_kind"] = "self_reported_local_candidate"
        expected_terminal["completion_seal"] = None
        expected_ledger = dict(ledger)
        expected_ledger["reported_state"] = "candidate_complete"
        expected_ledger["terminal_completion"] = expected_terminal
        if candidate_ledger != expected_ledger:
            errors.append(f"{label}: candidate ledger differs from sealed transition")
        if (
            canonical_sha256(candidate_ledger)
            != seal["candidate_ledger_canonical_sha256"]
        ):
            errors.append(f"{label}: candidate ledger digest differs")

    review_path = f".work_packets/reviews/{packet_id}.review.v2.json"
    if seal["review_path"] != review_path:
        errors.append(f"{label}: review path differs")
        return
    current_review_path = resolve_path(
        root,
        review_path,
        f"{label}.review",
        errors,
        must_exist=True,
    )
    current_review: Any | None = None
    if current_review_path is not None:
        try:
            current_review = load_json(current_review_path)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateKeyError,
            ValueError,
        ) as exc:
            errors.append(f"{label}: review JSON is invalid: {exc}")
    committed_review = git_json(
        root,
        review_commit,
        review_path,
        f"{label}.committed_review",
        errors,
    )
    if current_review is not None:
        if canonical_sha256(current_review) != seal["review_canonical_sha256"]:
            errors.append(f"{label}: current review digest differs")
        if current_review != committed_review:
            errors.append(f"{label}: current review differs from anchored commit")
        if exact_keys(
            current_review,
            INDEPENDENT_REVIEW_FIELDS,
            f"{label}.review",
            errors,
        ):
            expected_candidate_terminal = None
            if isinstance(candidate_ledger, dict):
                expected_candidate_terminal = candidate_ledger.get(
                    "terminal_completion"
                )
            if (
                current_review["schema_version"] != "work-packet-independent-review/v2"
                or current_review["packet_id"] != packet_id
                or current_review["candidate_commit"] != candidate_commit
                or current_review["candidate_tree"] != seal["candidate_tree"]
                or current_review["reviewer_mode"] != "independent_read_only"
                or current_review["verdict"] != "accepted"
                or current_review["findings"] != []
                or not isinstance(current_review["limitations"], list)
                or any(
                    not isinstance(item, str) or not item
                    for item in current_review["limitations"]
                )
                or current_review["candidate_terminal_canonical_sha256"]
                != canonical_sha256(expected_candidate_terminal)
            ):
                errors.append(f"{label}: independent review binding differs")


def validate_terminal_completion(
    ledger: dict[str, Any],
    packet: dict[str, Any],
    latest: dict[str, Any],
    root: Path,
    errors: list[str],
) -> None:
    packet_id = packet["packet_id"]
    terminal_states = {"candidate_complete", "complete"}
    terminal = ledger["terminal_completion"]
    if ledger["reported_state"] not in terminal_states:
        if terminal is not None:
            errors.append(
                f"ledger {packet_id}: nonterminal state requires null terminal_completion"
            )
        return
    if not exact_keys(
        terminal,
        TERMINAL_COMPLETION_FIELDS,
        f"ledger {packet_id}.terminal_completion",
        errors,
    ):
        return
    snapshot = latest.get("controlled_snapshot")
    if not isinstance(snapshot, dict):
        errors.append(f"ledger {packet_id}: terminal latest snapshot is invalid")
        return
    contract_digest = work_packets.packet_contract_sha256(packet)
    expected_authority = (
        "self_reported_local_candidate"
        if ledger["reported_state"] == "candidate_complete"
        else "git_review_sealed_candidate"
    )
    if (
        terminal["authority_kind"] != expected_authority
        or terminal["packet_contract_sha256"] != contract_digest
        or terminal["latest_record_sha256"] != latest.get("record_sha256")
        or terminal["controlled_claims_sha256"] != snapshot.get("claims_sha256")
    ):
        errors.append(f"ledger {packet_id}: terminal record binding differs")
    if ledger["reported_state"] == "candidate_complete":
        if terminal["completion_seal"] is not None:
            errors.append(
                f"ledger {packet_id}: candidate completion must remain unsealed"
            )
    else:
        validate_completion_seal(
            terminal["completion_seal"],
            terminal,
            ledger,
            packet,
            root,
            errors,
        )
    receipt_fields = (
        (
            "checkpoint",
            "checkpoint_path",
            "checkpoint_canonical_sha256",
        ),
        (
            "acceptance",
            "acceptance_receipt_path",
            "acceptance_canonical_sha256",
        ),
    )
    for label, packet_field, digest_field in receipt_fields:
        expected_path = packet.get(packet_field)
        terminal_path = terminal[
            "checkpoint_path" if label == "checkpoint" else "acceptance_path"
        ]
        if terminal_path != expected_path:
            errors.append(
                f"ledger {packet_id}: terminal {label} path differs from packet"
            )
            continue
        path = resolve_path(
            root,
            terminal_path,
            f"ledger {packet_id} terminal {label}",
            errors,
            must_exist=True,
        )
        if path is None:
            continue
        try:
            value = load_json(path)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateKeyError,
            ValueError,
        ) as exc:
            errors.append(f"ledger {packet_id} terminal {label}: invalid JSON: {exc}")
            continue
        if canonical_sha256(value) != terminal[digest_field]:
            errors.append(f"ledger {packet_id}: terminal {label} digest differs")
    expected_execution_path = f".work_packets/receipts/{packet_id}.execution.v2.json"
    if terminal["execution_receipt_path"] != expected_execution_path:
        errors.append(f"ledger {packet_id}: terminal execution receipt path differs")
    else:
        execution_path = resolve_path(
            root,
            expected_execution_path,
            f"ledger {packet_id} terminal execution receipt",
            errors,
            must_exist=True,
        )
        if execution_path is not None:
            try:
                execution_value = load_json(execution_path)
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                DuplicateKeyError,
                ValueError,
            ) as exc:
                errors.append(
                    f"ledger {packet_id} terminal execution receipt: "
                    f"invalid JSON: {exc}"
                )
            else:
                if (
                    canonical_sha256(execution_value)
                    != terminal["execution_receipt_canonical_sha256"]
                ):
                    errors.append(
                        f"ledger {packet_id}: terminal execution receipt digest differs"
                    )
                validate_execution_receipt(
                    execution_value,
                    packet,
                    contract_digest,
                    parse_timestamp(
                        latest.get("ended_at"),
                        f"ledger {packet_id} terminal latest ended_at",
                        errors,
                    ),
                    f"ledger {packet_id} terminal execution receipt",
                    errors,
                )


def validate_attempts(
    ledger: dict[str, Any],
    packet: dict[str, Any],
    packet_path: str,
    current_excluded: list[str],
    current_claims: list[dict[str, Any]],
    root: Path,
    live_packet_ids: set[str],
    policy: dict[str, Any],
    errors: list[str],
    *,
    allow_latest_snapshot_stale: bool = False,
) -> None:
    attempts = ledger["attempts"]
    packet_id = packet["packet_id"]
    if not isinstance(attempts, list) or not attempts:
        errors.append(f"ledger {packet_id}: attempts must be a non-empty list")
        return
    initial = ledger["initial_state"]
    initial_failures: list[str] | None = None
    initial_evidence: list[dict[str, Any]] | None = None
    if exact_keys(
        initial,
        INITIAL_STATE_FIELDS,
        f"ledger {packet_id}.initial_state",
        errors,
    ):
        initial_failures = unique_strings(
            initial["failure_ids"],
            f"ledger {packet_id}.initial_state.failure_ids",
            errors,
        )
        initial_evidence = validate_evidence_list(
            initial["evidence"],
            f"ledger {packet_id}.initial_state.evidence",
            root,
            packet_path,
            live_packet_ids,
            current_claims,
            set(policy["progress_derivation"]["allowed_evidence_kinds"]),
            errors,
            require_current=False,
        )
        if initial_failures is not None and initial_failures != sorted(
            initial_failures
        ):
            errors.append(
                f"ledger {packet_id}.initial_state.failure_ids: must be sorted"
            )
        if initial_failures is not None and initial_evidence is not None:
            supported = {
                failure_id
                for item in initial_evidence
                for failure_id in item["supports_failure_ids"]
            }
            if not supported.issubset(set(initial_failures)):
                errors.append(
                    f"ledger {packet_id}.initial_state: evidence references "
                    "unknown failure ids"
                )
    expected_failure_before = initial_failures
    expected_evidence_before = initial_evidence
    execution_retry = 0
    prior: dict[str, Any] | None = None
    prior_ended: datetime | None = None
    unknown_cost_seen = False
    validated_attempts: list[dict[str, Any]] = []
    for index, attempt in enumerate(attempts):
        label = f"ledger {packet_id} attempts[{index}]"
        if not exact_keys(attempt, ATTEMPT_FIELDS, label, errors):
            continue
        if attempt["schema_version"] != "execution-attempt/v2":
            errors.append(f"{label}: schema_version differs")
        if attempt["sequence"] != index + 1:
            errors.append(f"{label}: sequence is not contiguous from one")
        kind = attempt["attempt_kind"]
        if kind not in {"baseline_observation", "execution_attempt"}:
            errors.append(f"{label}: invalid attempt_kind")
        if kind == "baseline_observation":
            if index != 0:
                errors.append(f"{label}: baseline observation is only allowed first")
            if attempt["retry_index"] is not None:
                errors.append(f"{label}: baseline retry_index must be null")
        else:
            if attempt["retry_index"] != execution_retry:
                errors.append(f"{label}: execution retry_index is not contiguous")
            execution_retry += 1

        started = parse_timestamp(attempt["started_at"], f"{label}.started_at", errors)
        ended = parse_timestamp(attempt["ended_at"], f"{label}.ended_at", errors)
        wall = attempt["wall_time_ms"]
        if started is not None and ended is not None:
            expected_wall = int((ended - started).total_seconds() * 1000)
            if ended < started or not is_int(wall) or wall != expected_wall:
                errors.append(f"{label}: wall_time_ms differs from timestamps")
            if prior_ended is not None and started < prior_ended:
                errors.append(
                    f"{label}: started_at precedes the prior attempt ended_at"
                )
            prior_ended = ended

        blocker = attempt["blocker"]
        if exact_keys(blocker, BLOCKER_FIELDS, f"{label}.blocker", errors):
            failure_ids = unique_strings(
                blocker["failure_ids"],
                f"{label}.blocker.failure_ids",
                errors,
            )
            if (
                not isinstance(blocker["root_cause_id"], str)
                or ROOT_CAUSE_ID_RE.fullmatch(blocker["root_cause_id"]) is None
                or not isinstance(blocker["root_cause"], str)
                or not blocker["root_cause"]
                or blocker["status_after"]
                not in {"waiting", "open", "resolved", "blocked"}
                or failure_ids is None
                or any(
                    FAILURE_ID_RE.fullmatch(failure_id) is None
                    for failure_id in failure_ids
                )
            ):
                errors.append(f"{label}.blocker: invalid blocker")
            expected_fingerprint = canonical_sha256(
                {
                    "root_cause_id": blocker["root_cause_id"],
                    "failure_ids": blocker["failure_ids"],
                    "root_cause": blocker["root_cause"],
                }
            )
            if blocker["fingerprint_sha256"] != expected_fingerprint:
                errors.append(f"{label}.blocker: fingerprint differs")

        failure_delta = attempt["failure_delta"]
        failure_lists: dict[str, list[str] | None] = {}
        if exact_keys(
            failure_delta,
            FAILURE_DELTA_FIELDS,
            f"{label}.failure_delta",
            errors,
        ):
            for field in ("before", "after", "resolved", "introduced"):
                failure_lists[field] = unique_strings(
                    failure_delta[field],
                    f"{label}.failure_delta.{field}",
                    errors,
                )
            if all(value is not None for value in failure_lists.values()):
                for field in ("before", "after", "resolved", "introduced"):
                    if failure_delta[field] != sorted(failure_delta[field]):
                        errors.append(f"{label}.failure_delta.{field}: must be sorted")
                before = set(failure_lists["before"] or [])
                after = set(failure_lists["after"] or [])
                if failure_delta["resolved"] != sorted(before - after):
                    errors.append(f"{label}: resolved failure delta differs")
                if failure_delta["introduced"] != sorted(after - before):
                    errors.append(f"{label}: introduced failure delta differs")
                if (
                    expected_failure_before is not None
                    and failure_delta["before"] != expected_failure_before
                ):
                    errors.append(
                        f"{label}: failure state is not continuous with prior attempt"
                    )
                expected_failure_before = failure_delta["after"]

        evidence_delta = attempt["evidence_delta"]
        evidence_lists: dict[str, list[dict[str, Any]] | None] = {}
        if exact_keys(
            evidence_delta,
            EVIDENCE_DELTA_FIELDS,
            f"{label}.evidence_delta",
            errors,
        ):
            for field in ("before", "after", "added", "removed"):
                evidence_lists[field] = validate_evidence_list(
                    evidence_delta[field],
                    f"{label}.evidence_delta.{field}",
                    root,
                    packet_path,
                    live_packet_ids,
                    current_claims,
                    set(policy["progress_derivation"]["allowed_evidence_kinds"]),
                    errors,
                    require_current=(
                        index == len(attempts) - 1
                        and field == "after"
                        and not allow_latest_snapshot_stale
                    ),
                )
            if all(value is not None for value in evidence_lists.values()):
                before_items = evidence_lists["before"] or []
                after_items = evidence_lists["after"] or []
                before = {evidence_identity(item) for item in before_items}
                after = {evidence_identity(item) for item in after_items}
                added = {
                    evidence_identity(item) for item in (evidence_lists["added"] or [])
                }
                removed = {
                    evidence_identity(item)
                    for item in (evidence_lists["removed"] or [])
                }
                if added != after - before:
                    errors.append(f"{label}: added evidence delta differs")
                if removed != before - after:
                    errors.append(f"{label}: removed evidence delta differs")
                if (
                    expected_evidence_before is not None
                    and before_items != expected_evidence_before
                ):
                    errors.append(
                        f"{label}: evidence state is not continuous with prior attempt"
                    )
                expected_evidence_before = after_items

        known_failure_ids = set(failure_delta.get("before", [])) | set(
            failure_delta.get("after", [])
        )
        referenced_failure_ids = set(blocker.get("failure_ids", []))
        for item in evidence_delta.get("after", []):
            if isinstance(item, dict):
                referenced_failure_ids.update(item.get("supports_failure_ids", []))
        if not referenced_failure_ids.issubset(known_failure_ids):
            errors.append(
                f"{label}: blocker or evidence references unknown failure ids"
            )

        snapshot = attempt["controlled_snapshot"]
        if exact_keys(
            snapshot, SNAPSHOT_FIELDS, f"{label}.controlled_snapshot", errors
        ):
            if snapshot["algorithm"] != policy["current_snapshot"]["algorithm"]:
                errors.append(f"{label}: controlled snapshot algorithm differs")
            excluded = unique_strings(
                snapshot["excluded_paths"],
                f"{label}.controlled_snapshot.excluded_paths",
                errors,
            )
            raw_claims = snapshot["claims"]
            if not isinstance(raw_claims, list):
                errors.append(f"{label}.controlled_snapshot.claims: must be a list")
            else:
                for claim_index, claim in enumerate(raw_claims):
                    validate_claim_snapshot(
                        claim,
                        f"{label}.controlled_snapshot.claims[{claim_index}]",
                        errors,
                    )
                if raw_claims != sorted(
                    raw_claims,
                    key=lambda item: (
                        item.get("path", ""),
                        item.get("kind", ""),
                    ),
                ):
                    errors.append(f"{label}: controlled claims are not sorted")
                if snapshot["claims_sha256"] != canonical_sha256(raw_claims):
                    errors.append(f"{label}: controlled claims hash differs")
            if excluded != current_excluded:
                errors.append(f"{label}: excluded ledger paths differ")

        validate_process_observation(
            attempt["process_observation"],
            kind,
            label,
            errors,
        )
        unknown_cost_seen = (
            validate_cost(
                attempt["cost_observation"],
                f"{label}.cost_observation",
                errors,
            )
            or unknown_cost_seen
        )

        resolved = (
            set(failure_delta.get("resolved", []))
            if isinstance(failure_delta, dict)
            else set()
        )
        added_evidence = (
            evidence_delta.get("added", [])
            if isinstance(evidence_delta, dict)
            and isinstance(evidence_delta.get("added"), list)
            else []
        )
        derived_progress = bool(resolved or added_evidence)
        if attempt["declared_progress"] is not derived_progress:
            errors.append(f"{label}: declared_progress differs from derived progress")
        if resolved:
            supported = {
                failure_id
                for item in added_evidence
                if isinstance(item, dict)
                for failure_id in item.get("supports_failure_ids", [])
            }
            if not resolved.issubset(supported):
                errors.append(
                    f"{label}: resolved failures lack newly added supporting evidence"
                )
        if kind == "baseline_observation":
            unchanged_failure = (
                failure_delta.get("before") == failure_delta.get("after")
                and failure_delta.get("resolved") == []
                and failure_delta.get("introduced") == []
            )
            unchanged_evidence = (
                evidence_delta.get("before") == evidence_delta.get("after")
                and evidence_delta.get("added") == []
                and evidence_delta.get("removed") == []
            )
            if (
                not unchanged_failure
                or not unchanged_evidence
                or attempt["declared_progress"] is not False
                or blocker.get("status_after") != "waiting"
            ):
                errors.append(f"{label}: baseline observation semantics differ")

        expected_previous = None if prior is None else canonical_sha256(prior)
        if attempt["previous_attempt_sha256"] != expected_previous:
            errors.append(f"{label}: previous attempt hash differs")
        without_record = {
            key: value for key, value in attempt.items() if key != "record_sha256"
        }
        if attempt["record_sha256"] != canonical_sha256(without_record):
            errors.append(f"{label}: record hash differs")
        prior = attempt
        validated_attempts.append(attempt)

    if not validated_attempts:
        return
    latest = validated_attempts[-1]
    latest_snapshot = latest.get("controlled_snapshot")
    if isinstance(latest_snapshot, dict) and not allow_latest_snapshot_stale:
        if latest_snapshot.get("claims") != current_claims:
            errors.append(f"ledger {packet_id}: latest controlled snapshot is stale")
    if ledger["reported_state"] == "pending":
        if (
            len(validated_attempts) != 1
            or validated_attempts[0].get("attempt_kind") != "baseline_observation"
        ):
            errors.append(
                f"ledger {packet_id}: pending ledger must contain exactly one "
                "baseline observation"
            )
    elif (
        len(validated_attempts) == 1
        and validated_attempts[0].get("attempt_kind") == "baseline_observation"
        and ledger["reported_state"] not in {"pending", "active"}
    ):
        errors.append(
            f"ledger {packet_id}: baseline-only ledger is allowed only while "
            "pending or newly active"
        )
    execution_attempts = [
        attempt
        for attempt in validated_attempts
        if attempt.get("attempt_kind") == "execution_attempt"
    ]
    if execution_attempts:
        retry_budget = packet["retry_budget"]
        blocked_indices = [
            index
            for index, attempt in enumerate(execution_attempts)
            if attempt["blocker"]["status_after"] == "blocked"
        ]
        if blocked_indices and blocked_indices != [len(execution_attempts) - 1]:
            errors.append(
                f"ledger {packet_id}: a blocked transition is absorbing and "
                "must be the final execution attempt"
            )
        if ledger["reported_state"] == "blocked":
            if execution_attempts[-1]["blocker"]["status_after"] != "blocked":
                errors.append(
                    f"ledger {packet_id}: blocked packet requires a final "
                    "blocked transition"
                )
        elif blocked_indices:
            errors.append(
                f"ledger {packet_id}: blocked transition requires blocked packet state"
            )
        if len(execution_attempts) > retry_budget:
            errors.append(f"ledger {packet_id}: retry budget exceeded")
        terminal_states = {"candidate_complete", "complete"}
        if len(execution_attempts) == retry_budget and (
            ledger["reported_state"] not in terminal_states
            and (
                ledger["reported_state"] != "blocked"
                or execution_attempts[-1]["blocker"]["status_after"] != "blocked"
            )
        ):
            errors.append(
                f"ledger {packet_id}: exhausted retry budget must remain blocked"
            )
        consecutive_no_progress = 0
        same_blocker_no_progress = 0
        previous_fingerprint: str | None = None
        forced_stop_index: int | None = None
        forced_stop_reason: str | None = None
        for index, attempt in enumerate(execution_attempts):
            if attempt["declared_progress"] is True:
                consecutive_no_progress = 0
                same_blocker_no_progress = 0
                previous_fingerprint = None
                continue
            consecutive_no_progress += 1
            fingerprint = attempt["blocker"]["fingerprint_sha256"]
            if fingerprint == previous_fingerprint:
                same_blocker_no_progress += 1
            else:
                same_blocker_no_progress = 1
                previous_fingerprint = fingerprint
            if (
                same_blocker_no_progress
                >= policy["stopping_rules"][
                    "same_blocker_consecutive_no_progress_threshold"
                ]
            ):
                forced_stop_index = index
                forced_stop_reason = "three identical no-progress blockers"
                break
            if (
                consecutive_no_progress
                >= policy["stopping_rules"]["consecutive_no_progress_threshold"]
            ):
                forced_stop_index = index
                forced_stop_reason = (
                    "three consecutive no-progress attempts require blocked"
                )
                break
        if forced_stop_index is not None:
            stopped = execution_attempts[forced_stop_index]
            if (
                forced_stop_index != len(execution_attempts) - 1
                or ledger["reported_state"] != "blocked"
                or stopped["blocker"]["status_after"] != "blocked"
            ):
                errors.append(
                    f"ledger {packet_id}: {forced_stop_reason}; forced stop "
                    "is absorbing and must be the final blocked attempt"
                )
    if ledger["reported_state"] in {"candidate_complete", "complete"}:
        if (
            not execution_attempts
            or execution_attempts[-1]["blocker"]["status_after"] != "resolved"
        ):
            errors.append(
                f"ledger {packet_id}: candidate_complete and complete require "
                "a latest resolved execution attempt"
            )
    validate_terminal_completion(
        ledger,
        packet,
        latest,
        root,
        errors,
    )
    expected_claim = "partial" if unknown_cost_seen else "measured"
    if ledger["cost_accounting_claim"] != expected_claim:
        errors.append(f"ledger {packet_id}: cost accounting claim differs")


def verify_legacy_and_exemptions(
    root: Path,
    packets: dict[str, dict[str, Any]],
    packet_paths: dict[str, str],
    policy: dict[str, Any],
    errors: list[str],
) -> set[str]:
    for artifact in policy["legacy_v1_history"]["artifacts"]:
        path = resolve_path(
            root,
            artifact["path"],
            f"legacy artifact {artifact['path']}",
            errors,
            must_exist=True,
        )
        if path is not None and (
            not path.is_file()
            or path.is_symlink()
            or raw_sha256(path) != artifact["sha256"]
        ):
            errors.append(f"legacy artifact {artifact['path']}: hash differs")

    exempt_ids: set[str] = set()
    for exemption in policy["completed_before_v2_exemptions"]:
        packet_id = exemption["packet_id"]
        packet = packets.get(packet_id)
        if packet is None:
            errors.append(f"execution exemption {packet_id}: packet is missing")
            continue
        exempt_ids.add(packet_id)
        if (
            packet_paths.get(packet_id) != exemption["packet_path"]
            or packet.get("schema_version") != exemption["packet_schema_version"]
            or packet.get("state") != exemption["packet_state"]
            or work_packets.packet_contract_sha256(packet)
            != exemption["packet_contract_sha256"]
        ):
            errors.append(f"execution exemption {packet_id}: packet binding differs")
        for kind in ("checkpoint", "acceptance"):
            path_value = exemption[f"{kind}_path"]
            path = resolve_path(
                root,
                path_value,
                f"execution exemption {packet_id} {kind}",
                errors,
                must_exist=True,
            )
            if path is None:
                continue
            try:
                value = load_json(path)
            except (
                OSError,
                UnicodeDecodeError,
                json.JSONDecodeError,
                DuplicateKeyError,
                ValueError,
            ) as exc:
                errors.append(
                    f"execution exemption {packet_id} {kind}: invalid JSON: {exc}"
                )
                continue
            if canonical_sha256(value) != exemption[f"{kind}_canonical_sha256"]:
                errors.append(f"execution exemption {packet_id} {kind}: digest differs")
    return exempt_ids


def verify(
    project_root: Path,
    policy_path: Path = DEFAULT_POLICY,
    *,
    allow_stale_packet_id: str | None = None,
    allow_pending_operation_id: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        root = project_root.resolve(strict=True)
    except OSError as exc:
        return {
            "verification_status": "invalid",
            "execution_freshness_status": "invalid",
            "policy_id": None,
            "tracked_packet_count": 0,
            "verified_ledger_count": 0,
            "exempt_packet_count": 0,
            "authority_basis": [],
            "errors": [f"project root cannot be resolved: {exc}"],
            "claim_boundary": "No execution-freshness claim was established.",
        }
    policy_candidate = policy_path if policy_path.is_absolute() else root / policy_path
    try:
        policy = load_json(policy_candidate)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        policy = {}
        errors.append(f"policy cannot be loaded strictly: {exc}")
    if not errors:
        validate_policy(policy, errors)
    if errors:
        return {
            "verification_status": "invalid",
            "execution_freshness_status": "invalid",
            "policy_id": policy.get("policy_id") if isinstance(policy, dict) else None,
            "tracked_packet_count": 0,
            "verified_ledger_count": 0,
            "exempt_packet_count": 0,
            "authority_basis": [],
            "errors": sorted(set(errors)),
            "claim_boundary": "No execution-freshness claim was established.",
        }

    transaction_directory = root / policy["recorder_runtime"]["transaction_directory"]
    if transaction_directory.exists():
        if transaction_directory.is_symlink() or not transaction_directory.is_dir():
            errors.append(
                "execution recorder transaction path must be a real directory"
            )
        else:
            pending_transactions = sorted(
                entry.name for entry in transaction_directory.iterdir()
            )
            if pending_transactions:
                errors.append(
                    "execution recorder has an interrupted transaction requiring "
                    f"recovery: {pending_transactions}"
                )

    operation_directory = root / policy["recorder_runtime"]["operation_directory"]
    if operation_directory.exists():
        if operation_directory.is_symlink() or not operation_directory.is_dir():
            errors.append("execution recorder operation path must be a real directory")
        else:
            pending_operations = sorted(
                entry.name for entry in operation_directory.iterdir()
            )
            if allow_pending_operation_id is not None:
                if re.fullmatch(
                    r"[0-9a-f]{32}", allow_pending_operation_id
                ) is None or pending_operations != [allow_pending_operation_id]:
                    errors.append(
                        "recorder operation exception must name the sole "
                        "pending operation"
                    )
                else:
                    pending_operations = []
            if pending_operations:
                errors.append(
                    "execution recorder has an interrupted operation requiring "
                    f"recovery: {pending_operations}"
                )
    elif allow_pending_operation_id is not None:
        errors.append("recorder operation exception names no pending operation")

    packet_dir = root / policy["work_packets"]["packet_directory"]
    work_policy = root / policy["work_packets"]["policy_path"]
    work_receipt = work_packets.verify(root, work_policy, packet_dir)
    if work_receipt.get("status") != "pass":
        errors.append(
            "V2 work-packet verification failed: "
            + "; ".join(work_receipt.get("errors", []))
        )

    packets: dict[str, dict[str, Any]] = {}
    packet_paths: dict[str, str] = {}
    try:
        packet_files = sorted(packet_dir.glob("*.packet.json"))
    except OSError as exc:
        packet_files = []
        errors.append(f"packet directory cannot be enumerated: {exc}")
    for packet_file in packet_files:
        try:
            packet = load_json(packet_file)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateKeyError,
            ValueError,
        ) as exc:
            errors.append(f"packet {packet_file.name}: invalid JSON: {exc}")
            continue
        if not isinstance(packet, dict):
            errors.append(f"packet {packet_file.name}: must be an object")
            continue
        packet_id = packet.get("packet_id")
        if not isinstance(packet_id, str) or PACKET_ID_RE.fullmatch(packet_id) is None:
            errors.append(f"packet {packet_file.name}: invalid packet_id")
            continue
        packets[packet_id] = packet
        packet_paths[packet_id] = packet_file.relative_to(root).as_posix()

    live_v2 = {
        packet_id: packet
        for packet_id, packet in packets.items()
        if packet.get("schema_version") == "work-packet-instance/v2"
        and packet.get("state") in set(policy["work_packets"]["ledger_required_states"])
    }
    live_packet_ids = set(live_v2)
    if (
        allow_stale_packet_id is not None
        and allow_stale_packet_id not in live_packet_ids
    ):
        errors.append("recorder stale exception does not name one live V2 packet")
    exempt_ids = verify_legacy_and_exemptions(
        root,
        packets,
        packet_paths,
        policy,
        errors,
    )
    unexpected_exemptions = exempt_ids - live_packet_ids
    if unexpected_exemptions:
        errors.append(
            f"execution exemptions are not live V2 packets: "
            f"{sorted(unexpected_exemptions)}"
        )

    expected_ledger_paths = {
        ledger_path_for(packet_id) for packet_id in live_packet_ids - exempt_ids
    }
    actual_v2_paths: set[str] = set()
    ledger_dir = root / policy["ledger_schema"]["directory"]
    try:
        for entry in ledger_dir.iterdir():
            relative = entry.relative_to(root).as_posix()
            if entry.name.endswith(".attempts.v2.json"):
                actual_v2_paths.add(relative)
    except OSError as exc:
        errors.append(f"V2 ledger directory cannot be enumerated: {exc}")
    if actual_v2_paths != expected_ledger_paths:
        errors.append(
            "V2 ledger file set differs; "
            f"missing={sorted(expected_ledger_paths - actual_v2_paths)}, "
            f"extra={sorted(actual_v2_paths - expected_ledger_paths)}"
        )

    verified_ledger_count = 0
    authority_basis: list[dict[str, Any]] = []
    for packet_id in sorted(exempt_ids):
        exemption = next(
            item
            for item in policy["completed_before_v2_exemptions"]
            if item["packet_id"] == packet_id
        )
        authority_basis.append(
            {
                "packet_id": packet_id,
                "packet_path": packet_paths.get(packet_id),
                "packet_contract_sha256": exemption["packet_contract_sha256"],
                "reported_state": exemption["packet_state"],
                "ledger_path": None,
                "ledger_canonical_sha256": None,
                "latest_record_sha256": None,
                "latest_claims_sha256": None,
                "pre_v2_exemption": True,
            }
        )
    for packet_id in sorted(live_packet_ids - exempt_ids):
        packet = live_v2[packet_id]
        ledger_relative = ledger_path_for(packet_id)
        claims = packet.get("bounded_write_paths")
        if isinstance(claims, list) and any(
            isinstance(claim, dict)
            and claim.get("path", "").startswith(".work_packets/attempts/")
            for claim in claims
        ):
            errors.append(
                f"packet {packet_id}: V2 ledger runtime sidecars must not be "
                "bounded product write claims"
            )
        ledger_path = resolve_path(
            root,
            ledger_relative,
            f"ledger {packet_id}",
            errors,
            must_exist=True,
        )
        if ledger_path is None:
            continue
        if not ledger_path.is_file() or ledger_path.is_symlink():
            errors.append(f"ledger {packet_id}: must be a regular file")
            continue
        try:
            ledger = load_json(ledger_path)
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateKeyError,
            ValueError,
        ) as exc:
            errors.append(f"ledger {packet_id}: invalid JSON: {exc}")
            continue
        if not exact_keys(ledger, LEDGER_FIELDS, f"ledger {packet_id}", errors):
            continue
        contract_digest = work_packets.packet_contract_sha256(packet)
        if (
            ledger["schema_version"] != "execution-attempt-ledger/v2"
            or ledger["packet_id"] != packet_id
            or ledger["packet_path"] != packet_paths[packet_id]
            or ledger["packet_contract_sha256"] != contract_digest
            or ledger["reported_state"] != packet["state"]
            or ledger["cost_accounting_claim"] not in {"measured", "partial"}
        ):
            errors.append(f"ledger {packet_id}: packet or schema binding differs")
        current_excluded, current_claims = current_claim_snapshots(
            root,
            packet,
            live_packet_ids,
            errors,
        )
        before = len(errors)
        validate_attempts(
            ledger,
            packet,
            packet_paths[packet_id],
            current_excluded,
            current_claims,
            root,
            live_packet_ids,
            policy,
            errors,
            allow_latest_snapshot_stale=(packet_id == allow_stale_packet_id),
        )
        latest_attempt = (
            ledger["attempts"][-1]
            if isinstance(ledger["attempts"], list) and ledger["attempts"]
            else {}
        )
        latest_snapshot = (
            latest_attempt.get("controlled_snapshot", {})
            if isinstance(latest_attempt, dict)
            else {}
        )
        authority_basis.append(
            {
                "packet_id": packet_id,
                "packet_path": packet_paths[packet_id],
                "packet_contract_sha256": contract_digest,
                "reported_state": packet["state"],
                "ledger_path": ledger_relative,
                "ledger_canonical_sha256": canonical_sha256(ledger),
                "latest_record_sha256": latest_attempt.get("record_sha256"),
                "latest_claims_sha256": latest_snapshot.get("claims_sha256"),
                "pre_v2_exemption": False,
            }
        )
        if len(errors) == before:
            verified_ledger_count += 1

    unique_errors = sorted(set(errors))
    return {
        "verification_status": "valid" if not unique_errors else "invalid",
        "execution_freshness_status": (
            (
                "stale_authorized_for_recorder"
                if allow_stale_packet_id is not None
                else "current"
            )
            if not unique_errors
            else "invalid"
        ),
        "policy_id": policy["policy_id"],
        "tracked_packet_count": len(live_v2),
        "verified_ledger_count": verified_ledger_count,
        "exempt_packet_count": len(exempt_ids),
        "authority_basis": sorted(
            authority_basis,
            key=lambda item: item["packet_id"],
        ),
        "errors": unique_errors,
        "claim_boundary": (
            "Recorder preflight validates every contract and history while "
            "allowing exactly one named active packet's latest controlled "
            "snapshot to be stale so a new observation can be appended."
            if allow_stale_packet_id is not None
            else (
                "Current means every non-exempt live V2 packet has a "
                "contract-bound latest observation matching its controlled "
                "bytes. It does not authenticate execution, establish "
                "semantic adequacy, freeze the design, prove product "
                "completion, or prove investment effectiveness."
            )
        ),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        receipt = verify(args.project_root, args.policy)
    except Exception as exc:  # pragma: no cover - final fail-closed boundary
        receipt = {
            "verification_status": "invalid",
            "execution_freshness_status": "invalid",
            "policy_id": None,
            "tracked_packet_count": 0,
            "verified_ledger_count": 0,
            "exempt_packet_count": 0,
            "authority_basis": [],
            "errors": [f"internal verifier error: {type(exc).__name__}: {exc}"],
            "claim_boundary": "No execution-freshness claim was established.",
        }
    if args.json:
        print(
            json.dumps(
                receipt,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    else:
        print(
            f"execution freshness {receipt['execution_freshness_status']}: "
            f"{receipt['verified_ledger_count']} ledgers"
        )
        for error in receipt["errors"]:
            print(f"- {error}")
    return 0 if receipt["verification_status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
