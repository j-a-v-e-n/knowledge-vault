#!/usr/bin/env python3
"""Aggregate, fail-closed gate for closure governance and shadow artifacts."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True

from verify_candidate_manifest import (  # noqa: E402
    ManifestError,
    SHA256_RE,
    reject_duplicate_keys,
    require_exact_keys,
    require_string,
    sha256_file,
    validate_manifest,
)
from run_shadow_acceptance import (  # noqa: E402
    CapabilityError,
    DOMAIN_REJECTION_CODES,
    REQUIRED_ACCEPTANCE_REJECTION_CODES,
    Snapshot,
    candidate_manifest_typed_id,
    canonical_load_snapshot,
    load_policy_snapshot,
    read_once_member,
    read_once_regular,
    sha256_json,
    validate_acceptance_case,
    validate_shadow_acceptance,
)


CANDIDATE_VERIFIER_PATH = "研究/2026-07-27-总体设计/verify_candidate_manifest.py"
ACTION_ENVELOPE_PATH = "研究/2026-07-27-总体设计/READ_ONLY_SHADOW_ACTION_ENVELOPE.md"
CAPABILITY_POLICY_PATH = "研究/2026-07-27-总体设计/SHADOW_CAPABILITY_POLICY.json"
SHADOW_ACCEPTANCE_RUNNER_PATH = "研究/2026-07-27-总体设计/run_shadow_acceptance.py"
GOVERNANCE_FILENAMES = {
    "FREEZE_VERIFICATION_REPORT.json",
    "FINAL_INDEPENDENT_REVIEW_RECEIPT.json",
    "RESEARCH_CLOSURE_DECISION.json",
}
FILE_REF_KEYS = {"path", "sha256"}
GOVERNANCE_MANIFEST_KEYS = {
    "schema_version",
    "artifact_kind",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "freeze_report",
    "independent_review_receipt",
    "closure_decision",
}
FREEZE_REPORT_KEYS = {
    "schema_version",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "verifier_path",
    "verifier_sha256",
    "mode",
    "result",
    "candidate_inventory_digest_sha256",
    "post_closure_root_states",
}
ROOT_STATE_KEYS = {"root_id", "state"}
REVIEW_RECEIPT_KEYS = {
    "schema_version",
    "receipt_id",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "freeze_report_sha256",
    "verifier_sha256",
    "reviewer_id",
    "independence_assertion",
    "review_scope",
    "verdict",
    "unresolved_critical",
    "unresolved_major",
    "residual_limits",
    "action_envelope_path",
    "action_envelope_sha256",
    "external_action_authority",
}
CLOSURE_DECISION_KEYS = {
    "schema_version",
    "decision_id",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "freeze_report_sha256",
    "independent_review_receipt_sha256",
    "decision",
    "authorized_root_id",
    "authorized_root_path",
    "authorized_envelope_id",
    "authorized_envelope_sha256",
    "authority_scope",
    "issuer_id",
    "unresolved_conditions",
    "external_action_authority",
}
SHADOW_MANIFEST_KEYS = {
    "schema_version",
    "artifact_id",
    "artifact_kind",
    "status",
    "scope",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "parent_candidate_typed_id",
    "governance_manifest_sha256",
    "independent_review_receipt_sha256",
    "closure_decision_sha256",
    "action_envelope_path",
    "action_envelope_sha256",
    "capability_policy_path",
    "capability_policy_sha256",
    "program",
    "acceptance_cases",
    "snapshot_ledger",
    "sbom",
    "capability_report",
    "acceptance_test_report",
    "external_action_authority",
    "entries",
}
SHADOW_ENTRY_KEYS = {
    "path",
    "sha256",
    "role",
    "authority_status",
    "depends_on",
}
SHADOW_ROLES = {
    "ir-program",
    "ir-test-program",
    "fixture",
    "documentation",
    "snapshot-ledger",
    "sbom",
    "capability-report",
    "acceptance-report",
}
SHADOW_STATUS = "SHADOW_IMPLEMENTATION_CANDIDATE"
SHADOW_SCOPE = "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY"
SHADOW_REVIEW_FILENAMES = {"SHADOW_INDEPENDENT_REVIEW_RECEIPT.json"}
SHADOW_REVIEW_MANIFEST_KEYS = {
    "schema_version",
    "artifact_kind",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "shadow_manifest",
    "independent_review_receipt",
}
SHADOW_REVIEW_RECEIPT_KEYS = {
    "schema_version",
    "receipt_id",
    "reviewer_id",
    "independence_assertion",
    "review_scope",
    "verdict",
    "unresolved_critical",
    "unresolved_major",
    "residual_limits",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "parent_candidate_typed_id",
    "governance_manifest_sha256",
    "closure_decision_sha256",
    "shadow_manifest_sha256",
    "capability_policy_sha256",
    "sbom_sha256",
    "capability_report_sha256",
    "acceptance_test_report_sha256",
    "acceptance_runner_sha256",
    "program_sha256",
    "snapshot_ledger_sha256",
    "node_graph_digest_sha256",
    "runtime_tcb_digest_sha256",
    "loaded_module_file_closure_digest_sha256",
    "acceptance_output_set_digest_sha256",
    "domain_rejection_code_set_sha256",
    "sandbox_support_status",
    "artifact_external_action_capability_absent",
    "exact_opened_unlinked_snapshot_execution",
    "staged_target_controlled_pathname_reopen_count",
    "same_uid_concurrent_mutation_resistance_proven",
    "memory_boundary",
    "aggregate_deadline_enforced",
    "aggregate_wall_timeout_seconds",
    "host_level_universal_noninterference_proven",
    "domain_semantic_gate_accepted",
    "rejection_protocol_bound",
    "natural_language_speech_act_inference_proven",
    "semantic_truth_of_human_labels_proven",
    "real_world_temporal_order_proven",
    "actual_lane_generation_isolation_proven",
    "local_domain_gate_shadow_candidate_accepted",
    "capability_authority",
    "runtime_authority",
    "deployment_authority",
    "freeze_authority",
    "external_action_authority",
}


def canonical_document_snapshot(
    path: Path,
    label: str,
    max_bytes: int = 2 * 1024 * 1024,
) -> tuple[dict[str, Any], Snapshot]:
    try:
        snapshot = read_once_regular(path, label, max_bytes)
        document = canonical_load_snapshot(snapshot, label)
    except CapabilityError as exc:
        raise ManifestError(f"{label}: cannot read canonical JSON: {exc}") from exc
    return document, snapshot


def canonical_document(path: Path, label: str) -> dict[str, Any]:
    return canonical_document_snapshot(path, label)[0]


def document_from_snapshot(snapshot: Snapshot, label: str) -> dict[str, Any]:
    try:
        return canonical_load_snapshot(snapshot, label)
    except CapabilityError as exc:
        raise ManifestError(f"{label}: cannot parse canonical snapshot: {exc}") from exc


def member_snapshot(
    root: Path,
    relative: str,
    label: str,
    max_bytes: int = 2 * 1024 * 1024,
) -> Snapshot:
    try:
        observed_relative, snapshot = read_once_member(
            root,
            relative,
            label,
            max_bytes,
        )
    except CapabilityError as exc:
        raise ManifestError(f"{label}: cannot snapshot artifact member: {exc}") from exc
    if observed_relative != relative:
        raise ManifestError(f"{label}: normalized path drift")
    return snapshot


def require_same_snapshot(
    observed: Snapshot,
    expected: Snapshot,
    label: str,
) -> None:
    """Reject ordinary concurrent drift of an already accepted opened object.

    This is a before/after stability check, not a claim of resistance to a
    hostile process running under the same uid that can race and restore bytes.
    """
    if (
        observed.sha256 != expected.sha256
        or observed.data != expected.data
        or observed.stat_identity != expected.stat_identity
    ):
        raise ManifestError(f"{label}: snapshot changed during aggregate validation")


def require_regular_snapshot_current(
    path: Path,
    expected: Snapshot,
    label: str,
    max_bytes: int = 2 * 1024 * 1024,
) -> None:
    try:
        observed = read_once_regular(path, label, max_bytes)
    except CapabilityError as exc:
        raise ManifestError(f"{label}: cannot re-snapshot artifact: {exc}") from exc
    require_same_snapshot(observed, expected, label)


def require_member_snapshot_current(
    root: Path,
    relative: str,
    expected: Snapshot,
    label: str,
    max_bytes: int = 2 * 1024 * 1024,
) -> None:
    observed = member_snapshot(root, relative, label, max_bytes)
    require_same_snapshot(observed, expected, label)


def require_sha(value: Any, label: str) -> str:
    digest = require_string(value, label)
    if not SHA256_RE.fullmatch(digest):
        raise ManifestError(f"{label}: expected lowercase SHA-256")
    return digest


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ManifestError(f"{label}: expected string list")
    if len(value) != len(set(value)):
        raise ManifestError(f"{label}: duplicate value")
    return value


def require_empty_list(value: Any, label: str) -> None:
    if value != []:
        raise ManifestError(f"{label}: must be an empty list")


def normalized_relative(raw_path: Any, label: str) -> str:
    relative = require_string(raw_path, label)
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ManifestError(f"{label}: path must be normalized and relative")
    return relative


def resolve_regular(root: Path, raw_path: Any, label: str) -> tuple[str, Path]:
    relative = normalized_relative(raw_path, label)
    pure = PurePosixPath(relative)
    cursor = root
    for part in pure.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ManifestError(f"{label}: symlink path component is forbidden")
    resolved = cursor.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ManifestError(f"{label}: path escapes artifact root") from exc
    try:
        file_stat = resolved.stat()
    except OSError as exc:
        raise ManifestError(f"{label}: missing file: {relative}") from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise ManifestError(f"{label}: expected regular file: {relative}")
    if file_stat.st_nlink != 1:
        raise ManifestError(f"{label}: hardlinked file is forbidden: {relative}")
    return relative, resolved


def exact_inventory(root: Path, manifest_path: Path) -> set[str]:
    files: set[str] = set()
    directories: set[str] = set()
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in list(directory_names):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ManifestError(f"symlink directory in artifact root: {relative}")
            mode = path.stat().st_mode
            if not stat.S_ISDIR(mode):
                raise ManifestError(f"non-directory node in directory list: {relative}")
            directories.add(relative)
        for name in file_names:
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ManifestError(f"symlink file in artifact root: {relative}")
            file_stat = path.stat()
            if not stat.S_ISREG(file_stat.st_mode):
                raise ManifestError(f"special file in artifact root: {relative}")
            if file_stat.st_nlink != 1:
                raise ManifestError(f"hardlinked file in artifact root: {relative}")
            if path.resolve() != manifest_path.resolve():
                files.add(relative)
    expected_directories: set[str] = set()
    for relative in files | {manifest_path.relative_to(root).as_posix()}:
        parent = PurePosixPath(relative).parent
        while str(parent) not in {"", "."}:
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    extra_directories = sorted(directories - expected_directories)
    if extra_directories:
        raise ManifestError(f"unlisted artifact directories: {extra_directories}")
    return files


def candidate_entry_hash(candidate_document: dict[str, Any], path: str) -> str:
    matches = [entry for entry in candidate_document["entries"] if entry["path"] == path]
    if len(matches) != 1:
        raise ManifestError(f"candidate active entry does not resolve uniquely: {path}")
    return matches[0]["sha256"]


def declared_root(
    candidate_document: dict[str, Any],
    root_id: str,
) -> dict[str, Any]:
    matches = [
        item
        for item in candidate_document["post_closure_artifact_roots"]
        if item["root_id"] == root_id
    ]
    if len(matches) != 1:
        raise ManifestError(f"candidate root declaration does not resolve: {root_id}")
    return matches[0]


def validate_file_ref(
    raw: Any,
    *,
    expected_path: str,
    expected_hash: str,
    label: str,
) -> None:
    if not isinstance(raw, dict):
        raise ManifestError(f"{label}: expected object")
    require_exact_keys(raw, FILE_REF_KEYS, label)
    if raw["path"] != expected_path:
        raise ManifestError(f"{label}.path mismatch")
    if require_sha(raw["sha256"], f"{label}.sha256") != expected_hash:
        raise ManifestError(f"{label}.sha256 mismatch")


def validate_governance_chain(
    *,
    candidate_manifest_path: Path,
    candidate_document: dict[str, Any],
    candidate_result: dict[str, Any],
    governance_manifest_path: Path,
    expected_decision_sha256: str,
) -> dict[str, Any]:
    candidate_root = candidate_manifest_path.parent
    candidate_parent = candidate_root.parent
    declaration = declared_root(candidate_document, "closure-governance")
    expected_root = candidate_parent / declaration["path_from_candidate_parent"]
    expected_manifest = expected_root / declaration["required_manifest"]
    if governance_manifest_path.resolve() != expected_manifest.resolve():
        raise ManifestError("governance manifest path does not match candidate declaration")
    if expected_root.is_symlink() or not expected_root.is_dir():
        raise ManifestError("governance root is missing, non-directory, or symlinked")

    inventory = exact_inventory(expected_root, governance_manifest_path)
    if inventory != GOVERNANCE_FILENAMES:
        raise ManifestError(
            f"governance inventory mismatch; expected={sorted(GOVERNANCE_FILENAMES)}; "
            f"actual={sorted(inventory)}"
        )

    governance, governance_snapshot = canonical_document_snapshot(
        governance_manifest_path,
        "governance_manifest",
    )
    require_exact_keys(governance, GOVERNANCE_MANIFEST_KEYS, "governance_manifest")
    if governance["schema_version"] != "otts.post-closure-governance-manifest/1":
        raise ManifestError("governance manifest schema_version mismatch")
    if governance["artifact_kind"] != "CLOSURE_GOVERNANCE":
        raise ManifestError("governance artifact_kind mismatch")

    candidate_id = candidate_document["candidate_id"]
    candidate_hash = candidate_result["manifest_sha256"]
    if governance["candidate_id"] != candidate_id:
        raise ManifestError("governance candidate_id mismatch")
    if require_sha(
        governance["parent_candidate_manifest_sha256"],
        "governance.parent_candidate_manifest_sha256",
    ) != candidate_hash:
        raise ManifestError("governance parent candidate hash mismatch")

    freeze_name = "FREEZE_VERIFICATION_REPORT.json"
    review_name = "FINAL_INDEPENDENT_REVIEW_RECEIPT.json"
    decision_name = "RESEARCH_CLOSURE_DECISION.json"
    freeze_snapshot = member_snapshot(expected_root, freeze_name, "freeze_report")
    review_snapshot = member_snapshot(
        expected_root,
        review_name,
        "independent_review_receipt",
    )
    decision_snapshot = member_snapshot(
        expected_root,
        decision_name,
        "closure_decision",
    )
    freeze_hash = freeze_snapshot.sha256
    review_hash = review_snapshot.sha256
    decision_hash = decision_snapshot.sha256
    validate_file_ref(
        governance["freeze_report"],
        expected_path=freeze_name,
        expected_hash=freeze_hash,
        label="governance.freeze_report",
    )
    validate_file_ref(
        governance["independent_review_receipt"],
        expected_path=review_name,
        expected_hash=review_hash,
        label="governance.independent_review_receipt",
    )
    validate_file_ref(
        governance["closure_decision"],
        expected_path=decision_name,
        expected_hash=decision_hash,
        label="governance.closure_decision",
    )
    if decision_hash != expected_decision_sha256:
        raise ManifestError("closure decision does not match external expected hash")

    verifier_hash = candidate_entry_hash(candidate_document, CANDIDATE_VERIFIER_PATH)
    envelope_hash = candidate_entry_hash(candidate_document, ACTION_ENVELOPE_PATH)

    freeze = document_from_snapshot(freeze_snapshot, "freeze_report")
    require_exact_keys(freeze, FREEZE_REPORT_KEYS, "freeze_report")
    if freeze["schema_version"] != "otts.candidate-freeze-report/1":
        raise ManifestError("freeze report schema_version mismatch")
    if freeze["candidate_id"] != candidate_id:
        raise ManifestError("freeze report candidate_id mismatch")
    if require_sha(
        freeze["parent_candidate_manifest_sha256"],
        "freeze.parent_candidate_manifest_sha256",
    ) != candidate_hash:
        raise ManifestError("freeze report parent candidate hash mismatch")
    if freeze["verifier_path"] != CANDIDATE_VERIFIER_PATH:
        raise ManifestError("freeze report verifier_path mismatch")
    if require_sha(freeze["verifier_sha256"], "freeze.verifier_sha256") != verifier_hash:
        raise ManifestError("freeze report verifier hash mismatch")
    if freeze["mode"] != "freeze" or freeze["result"] != "PASS":
        raise ManifestError("freeze report is not a freeze PASS")
    if require_sha(
        freeze["candidate_inventory_digest_sha256"],
        "freeze.candidate_inventory_digest_sha256",
    ) != candidate_result["candidate_inventory_digest_sha256"]:
        raise ManifestError("freeze report inventory digest mismatch")
    expected_root_states = [
        {"root_id": "closure-governance", "state": "ABSENT"},
        {"root_id": "shadow-mvp", "state": "ABSENT"},
        {"root_id": "shadow-review", "state": "ABSENT"},
    ]
    states = freeze["post_closure_root_states"]
    if not isinstance(states, list):
        raise ManifestError("freeze post_closure_root_states must be a list")
    for index, state_row in enumerate(states):
        if not isinstance(state_row, dict):
            raise ManifestError(f"freeze root state {index}: expected object")
        require_exact_keys(state_row, ROOT_STATE_KEYS, f"freeze root state {index}")
    if states != expected_root_states:
        raise ManifestError("freeze root states do not prove all roots absent")

    review = document_from_snapshot(
        review_snapshot,
        "independent_review_receipt",
    )
    require_exact_keys(review, REVIEW_RECEIPT_KEYS, "independent_review_receipt")
    if review["schema_version"] != "otts.final-independent-review-receipt/1":
        raise ManifestError("review receipt schema_version mismatch")
    if review["candidate_id"] != candidate_id:
        raise ManifestError("review receipt candidate_id mismatch")
    if require_sha(
        review["parent_candidate_manifest_sha256"],
        "review.parent_candidate_manifest_sha256",
    ) != candidate_hash:
        raise ManifestError("review receipt parent candidate hash mismatch")
    if require_sha(review["freeze_report_sha256"], "review.freeze_report_sha256") != freeze_hash:
        raise ManifestError("review receipt freeze hash mismatch")
    if require_sha(review["verifier_sha256"], "review.verifier_sha256") != verifier_hash:
        raise ManifestError("review receipt verifier hash mismatch")
    require_string(review["receipt_id"], "review.receipt_id")
    require_string(review["reviewer_id"], "review.reviewer_id")
    require_string(review["independence_assertion"], "review.independence_assertion")
    if (
        review["review_scope"]
        != "FULL_CANDIDATE_MANIFEST_AND_ALL_ACTIVE_HISTORICAL_DEPENDENCIES"
    ):
        raise ManifestError("review scope is incomplete")
    if review["verdict"] != "PASS":
        raise ManifestError("review verdict is not PASS")
    require_empty_list(review["unresolved_critical"], "review.unresolved_critical")
    require_empty_list(review["unresolved_major"], "review.unresolved_major")
    require_string_list(review["residual_limits"], "review.residual_limits")
    if review["external_action_authority"] is not False:
        raise ManifestError("review receipt must deny external action authority")
    if review["action_envelope_path"] != ACTION_ENVELOPE_PATH:
        raise ManifestError("review action envelope path mismatch")
    if require_sha(
        review["action_envelope_sha256"],
        "review.action_envelope_sha256",
    ) != envelope_hash:
        raise ManifestError("review action envelope hash mismatch")

    decision = document_from_snapshot(decision_snapshot, "closure_decision")
    require_exact_keys(decision, CLOSURE_DECISION_KEYS, "closure_decision")
    if decision["schema_version"] != "otts.research-closure-decision/1":
        raise ManifestError("closure decision schema_version mismatch")
    require_string(decision["decision_id"], "decision.decision_id")
    require_string(decision["issuer_id"], "decision.issuer_id")
    if decision["candidate_id"] != candidate_id:
        raise ManifestError("closure decision candidate_id mismatch")
    if require_sha(
        decision["parent_candidate_manifest_sha256"],
        "decision.parent_candidate_manifest_sha256",
    ) != candidate_hash:
        raise ManifestError("closure decision parent candidate hash mismatch")
    if require_sha(
        decision["freeze_report_sha256"],
        "decision.freeze_report_sha256",
    ) != freeze_hash:
        raise ManifestError("closure decision freeze hash mismatch")
    if require_sha(
        decision["independent_review_receipt_sha256"],
        "decision.independent_review_receipt_sha256",
    ) != review_hash:
        raise ManifestError("closure decision review receipt hash mismatch")
    shadow_declaration = declared_root(candidate_document, "shadow-mvp")
    if decision["decision"] != "CONDITIONALLY_READY":
        raise ManifestError("closure decision is not CONDITIONALLY_READY")
    if decision["authorized_root_id"] != "shadow-mvp":
        raise ManifestError("closure decision authorized_root_id mismatch")
    if decision["authorized_root_path"] != shadow_declaration["path_from_candidate_parent"]:
        raise ManifestError("closure decision authorized_root_path mismatch")
    if decision["authorized_envelope_id"] != "RO-SHADOW-ENVELOPE-1.0":
        raise ManifestError("closure decision envelope ID mismatch")
    if require_sha(
        decision["authorized_envelope_sha256"],
        "decision.authorized_envelope_sha256",
    ) != envelope_hash:
        raise ManifestError("closure decision envelope hash mismatch")
    if (
        decision["authority_scope"]
        != "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY"
    ):
        raise ManifestError("closure decision authority_scope mismatch")
    require_empty_list(
        decision["unresolved_conditions"],
        "decision.unresolved_conditions",
    )
    if decision["external_action_authority"] is not False:
        raise ManifestError("closure decision must deny external action authority")

    if exact_inventory(expected_root, governance_manifest_path) != inventory:
        raise ManifestError("governance inventory changed during snapshot validation")
    require_regular_snapshot_current(
        governance_manifest_path,
        governance_snapshot,
        "governance_manifest final stability",
    )
    for relative, snapshot, label in (
        (freeze_name, freeze_snapshot, "freeze_report final stability"),
        (review_name, review_snapshot, "independent_review_receipt final stability"),
        (decision_name, decision_snapshot, "closure_decision final stability"),
    ):
        require_member_snapshot_current(expected_root, relative, snapshot, label)

    return {
        "candidate_hash": candidate_hash,
        "candidate_id": candidate_id,
        "closure_decision_hash": decision_hash,
        "envelope_hash": envelope_hash,
        "freeze_report_hash": freeze_hash,
        "governance_manifest_hash": governance_snapshot.sha256,
        "review_receipt_hash": review_hash,
    }


def validate_shadow(
    *,
    candidate_manifest_path: Path,
    candidate_document: dict[str, Any],
    governance_chain: dict[str, Any],
    shadow_manifest_path: Path,
) -> dict[str, Any]:
    candidate_root = candidate_manifest_path.parent
    candidate_parent = candidate_root.parent
    declaration = declared_root(candidate_document, "shadow-mvp")
    shadow_root = candidate_parent / declaration["path_from_candidate_parent"]
    expected_manifest = shadow_root / declaration["required_manifest"]
    if shadow_manifest_path.resolve() != expected_manifest.resolve():
        raise ManifestError("shadow manifest path does not match candidate declaration")
    if shadow_root.is_symlink() or not shadow_root.is_dir():
        raise ManifestError("shadow root is missing, non-directory, or symlinked")

    shadow, shadow_manifest_snapshot = canonical_document_snapshot(
        shadow_manifest_path,
        "shadow_manifest",
    )
    require_exact_keys(shadow, SHADOW_MANIFEST_KEYS, "shadow_manifest")
    if shadow["schema_version"] != "otts.shadow-artifact-manifest/3":
        raise ManifestError("shadow manifest schema_version mismatch")
    if shadow["artifact_kind"] != "READ_ONLY_SHADOW_MVP":
        raise ManifestError("shadow artifact_kind mismatch")
    require_string(shadow["artifact_id"], "shadow.artifact_id")
    if shadow["status"] != SHADOW_STATUS:
        raise ManifestError("shadow status exceeds or differs from candidate scope")
    if shadow["scope"] != SHADOW_SCOPE:
        raise ManifestError("shadow scope exceeds or differs from allowed envelope")
    if shadow["external_action_authority"] is not False:
        raise ManifestError("shadow manifest must deny external action authority")
    if shadow["candidate_id"] != governance_chain["candidate_id"]:
        raise ManifestError("shadow candidate_id mismatch")
    parent_candidate_manifest_sha256 = require_sha(
        shadow["parent_candidate_manifest_sha256"],
        "shadow.parent_candidate_manifest_sha256",
    )
    if parent_candidate_manifest_sha256 != governance_chain["candidate_hash"]:
        raise ManifestError("shadow parent candidate hash mismatch")
    expected_parent_candidate_typed_id = candidate_manifest_typed_id(
        parent_candidate_manifest_sha256
    )
    if shadow["parent_candidate_typed_id"] != expected_parent_candidate_typed_id:
        raise ManifestError("shadow parent candidate typed ID mismatch")
    if require_sha(
        shadow["governance_manifest_sha256"],
        "shadow.governance_manifest_sha256",
    ) != governance_chain["governance_manifest_hash"]:
        raise ManifestError("shadow governance manifest hash mismatch")
    if require_sha(
        shadow["independent_review_receipt_sha256"],
        "shadow.independent_review_receipt_sha256",
    ) != governance_chain["review_receipt_hash"]:
        raise ManifestError("shadow review receipt hash mismatch")
    if require_sha(
        shadow["closure_decision_sha256"],
        "shadow.closure_decision_sha256",
    ) != governance_chain["closure_decision_hash"]:
        raise ManifestError("shadow closure decision hash mismatch")
    if shadow["action_envelope_path"] != ACTION_ENVELOPE_PATH:
        raise ManifestError("shadow action envelope path mismatch")
    if require_sha(
        shadow["action_envelope_sha256"],
        "shadow.action_envelope_sha256",
    ) != governance_chain["envelope_hash"]:
        raise ManifestError("shadow action envelope hash mismatch")
    policy_hash = candidate_entry_hash(candidate_document, CAPABILITY_POLICY_PATH)
    if shadow["capability_policy_path"] != CAPABILITY_POLICY_PATH:
        raise ManifestError("shadow capability policy path mismatch")
    if require_sha(
        shadow["capability_policy_sha256"],
        "shadow.capability_policy_sha256",
    ) != policy_hash:
        raise ManifestError("shadow capability policy hash mismatch")
    policy_path = candidate_root / CAPABILITY_POLICY_PATH
    try:
        policy_snapshot = read_once_regular(
            policy_path,
            "candidate capability policy",
            524288,
        )
        if policy_snapshot.sha256 != policy_hash:
            raise CapabilityError("candidate capability policy changed from manifest")
        policy = load_policy_snapshot(policy_snapshot)
    except CapabilityError as exc:
        raise ManifestError(f"shadow capability policy failed: {exc}") from exc
    limits = policy["limits"]
    normalized_relative(shadow["program"], "shadow.program")
    cases = shadow["acceptance_cases"]
    if (
        not isinstance(cases, list)
        or not cases
        or len(cases) > limits["max_acceptance_cases"]
    ):
        raise ManifestError(
            "shadow acceptance_cases must be non-empty and within fixed limit"
        )
    case_ids: set[str] = set()
    expected_pass_count = 0
    expected_rejection_codes: set[str] = set()
    for index, case in enumerate(cases):
        label = f"shadow.acceptance_cases[{index}]"
        try:
            validate_acceptance_case(case, label)
        except CapabilityError as exc:
            raise ManifestError(f"{label}: invalid acceptance contract: {exc}") from exc
        case_id = require_string(case["case_id"], f"{label}.case_id")
        if case_id in case_ids:
            raise ManifestError(f"{label}: duplicate case_id")
        case_ids.add(case_id)
        normalized_relative(case["fixture_path"], f"{label}.fixture_path")
        if case["expected_outcome"] == "PASS":
            expected_pass_count += 1
        else:
            expected_rejection_codes.add(case["expected_rejection_code"])
    if expected_pass_count < 1:
        raise ManifestError("shadow acceptance suite requires at least one PASS case")
    missing_rejection_coverage = sorted(
        REQUIRED_ACCEPTANCE_REJECTION_CODES - expected_rejection_codes
    )
    if missing_rejection_coverage:
        raise ManifestError(
            "shadow acceptance suite missing required domain rejection coverage: "
            f"{missing_rejection_coverage}"
        )
    for ref_name in (
        "snapshot_ledger",
        "sbom",
        "capability_report",
        "acceptance_test_report",
    ):
        ref = shadow[ref_name]
        if not isinstance(ref, dict):
            raise ManifestError(f"shadow.{ref_name}: expected object")
        require_exact_keys(ref, FILE_REF_KEYS, f"shadow.{ref_name}")
        normalized_relative(ref["path"], f"shadow.{ref_name}.path")
        require_sha(ref["sha256"], f"shadow.{ref_name}.sha256")

    entries = shadow["entries"]
    if (
        not isinstance(entries, list)
        or not entries
        or len(entries) > limits["max_manifest_entries"]
    ):
        raise ManifestError("shadow entries must be non-empty and within fixed limit")
    paths: set[str] = set()
    dependencies: dict[str, list[str]] = {}
    roles: dict[str, str] = {}
    entry_snapshots: dict[str, Snapshot] = {}
    total_input_bytes = 0
    shadow_manifest_relative = shadow_manifest_path.relative_to(shadow_root).as_posix()
    for index, raw in enumerate(entries):
        label = f"shadow.entries[{index}]"
        if not isinstance(raw, dict):
            raise ManifestError(f"{label}: expected object")
        require_exact_keys(raw, SHADOW_ENTRY_KEYS, label)
        relative = normalized_relative(raw["path"], f"{label}.path")
        if relative in paths:
            raise ManifestError(f"{label}: duplicate path")
        if relative == shadow_manifest_relative:
            raise ManifestError("shadow manifest must not include itself")
        expected_hash = require_sha(raw["sha256"], f"{label}.sha256")
        role = raw["role"]
        if role not in SHADOW_ROLES:
            raise ManifestError(f"{label}: unknown role")
        max_entry_bytes = (
            limits["max_artifact_bytes"]
            if role in {"ir-program", "ir-test-program"}
            else limits["max_fixture_bytes"]
            if role == "fixture"
            else limits["max_report_bytes"]
        )
        snapshot = member_snapshot(
            shadow_root,
            relative,
            f"{label}.path",
            max_entry_bytes,
        )
        if snapshot.sha256 != expected_hash:
            raise ManifestError(f"{label}: hash mismatch")
        total_input_bytes += len(snapshot.data)
        if total_input_bytes > limits["max_total_input_bytes"]:
            raise ManifestError("shadow entry snapshots exceed fixed total input bytes")
        if raw["authority_status"] != "NO_EXTERNAL_AUTHORITY":
            raise ManifestError(f"{label}: authority_status must deny external authority")
        dependencies[relative] = require_string_list(
            raw["depends_on"], f"{label}.depends_on"
        )
        roles[relative] = role
        entry_snapshots[relative] = snapshot
        paths.add(relative)

    if roles.get(shadow["program"]) != "ir-program":
        raise ManifestError("shadow program must resolve to an ir-program entry")
    for case in cases:
        if roles.get(case["fixture_path"]) != "fixture":
            raise ManifestError("shadow acceptance fixture must resolve to a fixture entry")
    for ref_name, expected_role in (
        ("snapshot_ledger", "snapshot-ledger"),
        ("sbom", "sbom"),
        ("capability_report", "capability-report"),
        ("acceptance_test_report", "acceptance-report"),
    ):
        if roles.get(shadow[ref_name]["path"]) != expected_role:
            raise ManifestError(f"shadow {ref_name} must resolve to role {expected_role}")

    for owner, owner_dependencies in dependencies.items():
        unknown = sorted(set(owner_dependencies) - paths)
        if unknown:
            raise ManifestError(f"{owner}: unknown dependencies: {unknown}")

    visit_state: dict[str, int] = {}

    def visit(path: str, stack: list[str]) -> None:
        state = visit_state.get(path, 0)
        if state == 2:
            return
        if state == 1:
            start = stack.index(path)
            cycle = stack[start:] + [path]
            raise ManifestError(f"shadow dependency cycle: {' -> '.join(cycle)}")
        visit_state[path] = 1
        for dependency in dependencies[path]:
            visit(dependency, stack + [path])
        visit_state[path] = 2

    for path in sorted(paths):
        visit(path, [])

    inventory = exact_inventory(shadow_root, shadow_manifest_path)
    if inventory != paths:
        raise ManifestError(
            f"shadow inventory mismatch; listed={sorted(paths)}; actual={sorted(inventory)}"
        )

    try:
        runner_path = candidate_root / SHADOW_ACCEPTANCE_RUNNER_PATH
        runner_snapshot = read_once_regular(
            runner_path,
            "candidate shadow runner",
            2 * 1024 * 1024,
        )
        if runner_snapshot.sha256 != candidate_entry_hash(
            candidate_document,
            SHADOW_ACCEPTANCE_RUNNER_PATH,
        ):
            raise CapabilityError("candidate shadow runner changed from manifest")
        acceptance = validate_shadow_acceptance(
            shadow_root=shadow_root,
            shadow=shadow,
            policy_path=policy_path,
            runner_path=runner_path,
            entry_snapshots=entry_snapshots,
            policy_snapshot=policy_snapshot,
            runner_snapshot=runner_snapshot,
        )
    except CapabilityError as exc:
        raise ManifestError(f"shadow capability/runtime acceptance failed: {exc}") from exc

    if acceptance["local_deterministic_domain_gate_acceptance_pass"] is not True:
        raise ManifestError("shadow acceptance did not pass the closed domain Gate")
    if acceptance["pass_case_count"] < 1:
        raise ManifestError("shadow domain Gate has no accepted neighboring valid case")
    if acceptance["reject_case_count"] < len(REQUIRED_ACCEPTANCE_REJECTION_CODES):
        raise ManifestError("shadow domain Gate rejection coverage count is incomplete")
    if acceptance["domain_rejection_code_set_sha256"] != sha256_json(
        sorted(DOMAIN_REJECTION_CODES)
    ):
        raise ManifestError("shadow domain rejection code set binding mismatch")
    if (
        acceptance["parent_candidate_typed_id"]
        != expected_parent_candidate_typed_id
    ):
        raise ManifestError("shadow acceptance parent candidate typed ID mismatch")
    if acceptance["exact_opened_unlinked_snapshot_execution"] is not True:
        raise ManifestError("shadow acceptance did not use opened-and-unlinked snapshots")
    reopen_count = acceptance["staged_target_controlled_pathname_reopen_count"]
    if (
        not isinstance(reopen_count, int)
        or isinstance(reopen_count, bool)
        or reopen_count != 0
    ):
        raise ManifestError("shadow acceptance reopened target-controlled pathname")
    if acceptance["same_uid_concurrent_mutation_resistance_proven"] is not False:
        raise ManifestError("shadow acceptance must preserve same-uid race non-claim")
    if acceptance["host_level_universal_noninterference_proven"] is not False:
        raise ManifestError("shadow acceptance must preserve host noninterference non-claim")
    for nonclaim in (
        "natural_language_speech_act_inference_proven",
        "semantic_truth_of_human_labels_proven",
        "real_world_temporal_order_proven",
        "actual_lane_generation_isolation_proven",
    ):
        if acceptance[nonclaim] is not False:
            raise ManifestError(f"shadow acceptance must preserve {nonclaim}=false")
    if acceptance["memory_boundary"] != (
        "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED"
    ):
        raise ManifestError("shadow acceptance memory boundary mismatch")
    if acceptance["aggregate_deadline_enforced"] is not True:
        raise ManifestError("shadow acceptance did not enforce aggregate deadline")
    if acceptance["aggregate_wall_timeout_seconds"] != limits[
        "aggregate_wall_timeout_seconds"
    ]:
        raise ManifestError("shadow acceptance aggregate timeout mismatch")
    for authority_key in (
        "runtime_authority",
        "deployment_authority",
        "freeze_authority",
        "external_action_authority",
    ):
        if acceptance[authority_key] is not False:
            raise ManifestError(f"shadow acceptance must keep {authority_key}=false")

    if exact_inventory(shadow_root, shadow_manifest_path) != inventory:
        raise ManifestError("shadow inventory changed during snapshot acceptance")
    require_regular_snapshot_current(
        shadow_manifest_path,
        shadow_manifest_snapshot,
        "shadow_manifest final stability",
    )
    for relative, snapshot in sorted(entry_snapshots.items()):
        require_member_snapshot_current(
            shadow_root,
            relative,
            snapshot,
            f"shadow entry {relative} final stability",
        )
    require_regular_snapshot_current(
        policy_path,
        policy_snapshot,
        "candidate capability policy final stability",
        524288,
    )
    require_regular_snapshot_current(
        runner_path,
        runner_snapshot,
        "candidate shadow runner final stability",
    )

    return {
        "shadow_document": shadow,
        "shadow_manifest_sha256": shadow_manifest_snapshot.sha256,
        "shadow_mechanical_acceptance": acceptance,
    }


def validate_shadow_review(
    *,
    candidate_manifest_path: Path,
    candidate_document: dict[str, Any],
    governance_chain: dict[str, Any],
    shadow_result: dict[str, Any],
    shadow_review_manifest_path: Path,
    expected_shadow_review_receipt_sha256: str,
) -> dict[str, Any]:
    expected_receipt_hash = require_sha(
        expected_shadow_review_receipt_sha256,
        "expected_shadow_review_receipt_sha256",
    )
    candidate_parent = candidate_manifest_path.parent.parent
    declaration = declared_root(candidate_document, "shadow-review")
    review_root = candidate_parent / declaration["path_from_candidate_parent"]
    expected_manifest = review_root / declaration["required_manifest"]
    if shadow_review_manifest_path.resolve() != expected_manifest.resolve():
        raise ManifestError("shadow review manifest path does not match candidate declaration")
    if review_root.is_symlink() or not review_root.is_dir():
        raise ManifestError("shadow review root is missing, non-directory, or symlinked")
    inventory = exact_inventory(review_root, shadow_review_manifest_path)
    if inventory != SHADOW_REVIEW_FILENAMES:
        raise ManifestError(
            "shadow review inventory mismatch; "
            f"expected={sorted(SHADOW_REVIEW_FILENAMES)}; actual={sorted(inventory)}"
        )

    review_manifest, review_manifest_snapshot = canonical_document_snapshot(
        shadow_review_manifest_path,
        "shadow_review_manifest",
    )
    require_exact_keys(
        review_manifest,
        SHADOW_REVIEW_MANIFEST_KEYS,
        "shadow_review_manifest",
    )
    if review_manifest["schema_version"] != "otts.shadow-review-manifest/2":
        raise ManifestError("shadow review manifest schema mismatch")
    if review_manifest["artifact_kind"] != "SHADOW_INDEPENDENT_REVIEW":
        raise ManifestError("shadow review artifact_kind mismatch")
    if review_manifest["candidate_id"] != governance_chain["candidate_id"]:
        raise ManifestError("shadow review candidate_id mismatch")
    if require_sha(
        review_manifest["parent_candidate_manifest_sha256"],
        "shadow_review.parent_candidate_manifest_sha256",
    ) != governance_chain["candidate_hash"]:
        raise ManifestError("shadow review parent candidate hash mismatch")

    receipt_name = "SHADOW_INDEPENDENT_REVIEW_RECEIPT.json"
    receipt_snapshot = member_snapshot(
        review_root,
        receipt_name,
        "shadow_independent_review_receipt",
    )
    receipt_hash = receipt_snapshot.sha256
    if receipt_hash != expected_receipt_hash:
        raise ManifestError("shadow review receipt does not match caller expected exact hash")
    shadow_path_label = "机会到交易系统-shadow-mvp/SHADOW_ARTIFACT_MANIFEST.json"
    validate_file_ref(
        review_manifest["shadow_manifest"],
        expected_path=shadow_path_label,
        expected_hash=shadow_result["shadow_manifest_sha256"],
        label="shadow_review.shadow_manifest",
    )
    validate_file_ref(
        review_manifest["independent_review_receipt"],
        expected_path=receipt_name,
        expected_hash=receipt_hash,
        label="shadow_review.independent_review_receipt",
    )

    receipt = document_from_snapshot(
        receipt_snapshot,
        "shadow_independent_review_receipt",
    )
    require_exact_keys(
        receipt,
        SHADOW_REVIEW_RECEIPT_KEYS,
        "shadow_independent_review_receipt",
    )
    if receipt["schema_version"] != "otts.shadow-independent-review-receipt/2":
        raise ManifestError("shadow review receipt schema mismatch")
    require_string(receipt["receipt_id"], "shadow_review.receipt_id")
    require_string(receipt["reviewer_id"], "shadow_review.reviewer_id")
    require_string(
        receipt["independence_assertion"],
        "shadow_review.independence_assertion",
    )
    if (
        receipt["review_scope"]
        != "EXACT_CLOSED_DOMAIN_GATE_SHADOW_MANIFEST_POLICY_SNAPSHOT_RUNTIME_AND_OUTCOMES"
    ):
        raise ManifestError("shadow independent review scope is incomplete")
    if receipt["verdict"] != "PASS":
        raise ManifestError("shadow independent review verdict is not PASS")
    require_empty_list(receipt["unresolved_critical"], "shadow_review.unresolved_critical")
    require_empty_list(receipt["unresolved_major"], "shadow_review.unresolved_major")
    require_string_list(receipt["residual_limits"], "shadow_review.residual_limits")
    if receipt["candidate_id"] != governance_chain["candidate_id"]:
        raise ManifestError("shadow receipt candidate_id mismatch")
    if receipt["parent_candidate_typed_id"] != shadow_result[
        "shadow_mechanical_acceptance"
    ]["parent_candidate_typed_id"]:
        raise ManifestError("shadow receipt parent candidate typed ID mismatch")
    expected_hashes = {
        "parent_candidate_manifest_sha256": governance_chain["candidate_hash"],
        "governance_manifest_sha256": governance_chain["governance_manifest_hash"],
        "closure_decision_sha256": governance_chain["closure_decision_hash"],
        "shadow_manifest_sha256": shadow_result["shadow_manifest_sha256"],
        "capability_policy_sha256": shadow_result["shadow_mechanical_acceptance"][
            "policy_sha256"
        ],
        "sbom_sha256": shadow_result["shadow_mechanical_acceptance"]["sbom_sha256"],
        "capability_report_sha256": shadow_result["shadow_mechanical_acceptance"][
            "capability_report_sha256"
        ],
        "acceptance_test_report_sha256": shadow_result[
            "shadow_mechanical_acceptance"
        ]["acceptance_test_report_sha256"],
        "acceptance_runner_sha256": shadow_result["shadow_mechanical_acceptance"][
            "runner_sha256"
        ],
        "program_sha256": shadow_result["shadow_mechanical_acceptance"][
            "program_sha256"
        ],
        "snapshot_ledger_sha256": shadow_result["shadow_mechanical_acceptance"][
            "snapshot_ledger_sha256"
        ],
        "node_graph_digest_sha256": shadow_result["shadow_mechanical_acceptance"][
            "node_graph_digest_sha256"
        ],
        "runtime_tcb_digest_sha256": shadow_result["shadow_mechanical_acceptance"][
            "runtime_tcb_digest_sha256"
        ],
        "loaded_module_file_closure_digest_sha256": shadow_result[
            "shadow_mechanical_acceptance"
        ]["loaded_module_file_closure_digest_sha256"],
        "acceptance_output_set_digest_sha256": shadow_result[
            "shadow_mechanical_acceptance"
        ]["acceptance_output_set_digest_sha256"],
        "domain_rejection_code_set_sha256": shadow_result[
            "shadow_mechanical_acceptance"
        ]["domain_rejection_code_set_sha256"],
    }
    for key, expected in expected_hashes.items():
        if require_sha(receipt[key], f"shadow_review.{key}") != expected:
            raise ManifestError(f"shadow review receipt {key} mismatch")
    if (
        receipt["sandbox_support_status"]
        != "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH"
    ):
        raise ManifestError("shadow review sandbox support status mismatch")
    if receipt["artifact_external_action_capability_absent"] is not True:
        raise ManifestError("shadow review does not accept the closed IR capability result")
    if receipt["domain_semantic_gate_accepted"] is not True:
        raise ManifestError("shadow review does not accept the closed domain Gate")
    if receipt["rejection_protocol_bound"] is not True:
        raise ManifestError("shadow review does not bind PASS/REJECT outcomes")
    if receipt["exact_opened_unlinked_snapshot_execution"] is not True:
        raise ManifestError("shadow review did not accept opened-and-unlinked execution")
    receipt_reopen_count = receipt["staged_target_controlled_pathname_reopen_count"]
    if (
        not isinstance(receipt_reopen_count, int)
        or isinstance(receipt_reopen_count, bool)
        or receipt_reopen_count != 0
    ):
        raise ManifestError("shadow review permits a target-controlled pathname reopen")
    if receipt["same_uid_concurrent_mutation_resistance_proven"] is not False:
        raise ManifestError("shadow review must preserve the same-uid race non-claim")
    if receipt["memory_boundary"] != shadow_result["shadow_mechanical_acceptance"][
        "memory_boundary"
    ]:
        raise ManifestError("shadow review memory boundary mismatch")
    if receipt["aggregate_deadline_enforced"] is not True:
        raise ManifestError("shadow review did not bind the aggregate deadline")
    if receipt["aggregate_wall_timeout_seconds"] != shadow_result[
        "shadow_mechanical_acceptance"
    ]["aggregate_wall_timeout_seconds"]:
        raise ManifestError("shadow review aggregate timeout mismatch")
    if receipt["host_level_universal_noninterference_proven"] is not False:
        raise ManifestError("shadow review must preserve the host noninterference non-claim")
    for nonclaim in (
        "natural_language_speech_act_inference_proven",
        "semantic_truth_of_human_labels_proven",
        "real_world_temporal_order_proven",
        "actual_lane_generation_isolation_proven",
    ):
        if receipt[nonclaim] is not False:
            raise ManifestError(f"shadow review must preserve {nonclaim}=false")
    if receipt["local_domain_gate_shadow_candidate_accepted"] is not True:
        raise ManifestError("shadow review does not accept the limited domain Gate candidate")
    for key in (
        "capability_authority",
        "runtime_authority",
        "deployment_authority",
        "freeze_authority",
        "external_action_authority",
    ):
        if receipt[key] is not False:
            raise ManifestError(f"shadow review receipt must keep {key}=false")

    if exact_inventory(review_root, shadow_review_manifest_path) != inventory:
        raise ManifestError("shadow review inventory changed during snapshot validation")
    require_regular_snapshot_current(
        shadow_review_manifest_path,
        review_manifest_snapshot,
        "shadow_review_manifest final stability",
    )
    require_member_snapshot_current(
        review_root,
        receipt_name,
        receipt_snapshot,
        "shadow_independent_review_receipt final stability",
    )

    return {
        "shadow_review_manifest_sha256": review_manifest_snapshot.sha256,
        "shadow_review_receipt_sha256": receipt_hash,
        "local_shadow_candidate_accepted": True,
        "domain_semantic_gate_accepted": True,
        "rejection_protocol_bound": True,
        "exact_opened_unlinked_snapshot_execution": True,
        "staged_target_controlled_pathname_reopen_count": 0,
        "same_uid_concurrent_mutation_resistance_proven": False,
        "memory_boundary": shadow_result["shadow_mechanical_acceptance"][
            "memory_boundary"
        ],
        "aggregate_deadline_enforced": True,
        "aggregate_wall_timeout_seconds": shadow_result[
            "shadow_mechanical_acceptance"
        ]["aggregate_wall_timeout_seconds"],
        "host_level_universal_noninterference_proven": False,
        "natural_language_speech_act_inference_proven": False,
        "semantic_truth_of_human_labels_proven": False,
        "real_world_temporal_order_proven": False,
        "actual_lane_generation_isolation_proven": False,
        "capability_authority": False,
        "runtime_authority": False,
        "deployment_authority": False,
        "freeze_authority": False,
        "external_action_authority": False,
    }


def validate_aggregate(
    *,
    candidate_manifest_path: Path,
    governance_manifest_path: Path,
    expected_decision_sha256: str,
    shadow_manifest_path: Path | None,
    shadow_review_manifest_path: Path | None = None,
    expected_shadow_review_receipt_sha256: str | None = None,
) -> dict[str, Any]:
    expected_decision_sha256 = require_sha(
        expected_decision_sha256,
        "expected_closure_decision_sha256",
    )
    candidate_result = validate_manifest(
        candidate_manifest_path,
        phase="post-closure",
    )
    candidate_manifest_path = candidate_manifest_path.resolve()
    candidate_document, candidate_snapshot = canonical_document_snapshot(
        candidate_manifest_path,
        "candidate_manifest",
    )
    if candidate_snapshot.sha256 != candidate_result["manifest_sha256"]:
        raise ManifestError("candidate manifest changed between phase and aggregate snapshots")
    governance_chain = validate_governance_chain(
        candidate_manifest_path=candidate_manifest_path,
        candidate_document=candidate_document,
        candidate_result=candidate_result,
        governance_manifest_path=governance_manifest_path.resolve(),
        expected_decision_sha256=expected_decision_sha256,
    )

    candidate_parent = candidate_manifest_path.parent.parent
    shadow_declaration = declared_root(candidate_document, "shadow-mvp")
    shadow_root = candidate_parent / shadow_declaration["path_from_candidate_parent"]
    shadow_review_declaration = declared_root(candidate_document, "shadow-review")
    shadow_review_root = candidate_parent / shadow_review_declaration[
        "path_from_candidate_parent"
    ]
    if shadow_root.exists():
        if shadow_manifest_path is None:
            raise ManifestError("present shadow root requires explicit --shadow-manifest")
        internal_shadow_result = validate_shadow(
            candidate_manifest_path=candidate_manifest_path,
            candidate_document=candidate_document,
            governance_chain=governance_chain,
            shadow_manifest_path=shadow_manifest_path.resolve(),
        )
        if shadow_review_root.exists():
            if (
                shadow_review_manifest_path is None
                or expected_shadow_review_receipt_sha256 is None
            ):
                raise ManifestError(
                    "present shadow review root requires explicit review manifest and "
                    "caller expected receipt hash"
                )
            review_result = validate_shadow_review(
                candidate_manifest_path=candidate_manifest_path,
                candidate_document=candidate_document,
                governance_chain=governance_chain,
                shadow_result=internal_shadow_result,
                shadow_review_manifest_path=shadow_review_manifest_path.resolve(),
                expected_shadow_review_receipt_sha256=(
                    expected_shadow_review_receipt_sha256
                ),
            )
            shadow_result = {
                "shadow_manifest_sha256": internal_shadow_result[
                    "shadow_manifest_sha256"
                ],
                "shadow_state": (
                    "PRESENT_ACCEPTED_LOCAL_DOMAIN_GATE_SHADOW_CANDIDATE"
                ),
                "shadow_manifest_hash_bound": True,
                "domain_gate_mechanical_acceptance_observed": True,
                "shadow_generation_valid": True,
                "local_shadow_candidate_accepted": True,
                "host_level_universal_noninterference_proven": False,
                "natural_language_speech_act_inference_proven": False,
                "semantic_truth_of_human_labels_proven": False,
                "real_world_temporal_order_proven": False,
                "actual_lane_generation_isolation_proven": False,
                "capability_authority": False,
                "runtime_authority": False,
                "deployment_authority": False,
                "freeze_authority": False,
                "external_action_authority": False,
                **review_result,
            }
        else:
            if (
                shadow_review_manifest_path is not None
                or expected_shadow_review_receipt_sha256 is not None
            ):
                raise ManifestError(
                    "shadow review arguments supplied but declared review root is absent"
                )
            shadow_result = {
                "shadow_manifest_sha256": internal_shadow_result[
                    "shadow_manifest_sha256"
                ],
                "shadow_state": "PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED",
                "shadow_manifest_hash_bound": True,
                "domain_gate_mechanical_acceptance_observed": True,
                "domain_semantic_gate_accepted": False,
                "rejection_protocol_bound": False,
                "shadow_generation_valid": False,
                "local_shadow_candidate_accepted": False,
                "host_level_universal_noninterference_proven": False,
                "natural_language_speech_act_inference_proven": False,
                "semantic_truth_of_human_labels_proven": False,
                "real_world_temporal_order_proven": False,
                "actual_lane_generation_isolation_proven": False,
                "capability_authority": False,
                "runtime_authority": False,
                "deployment_authority": False,
                "freeze_authority": False,
                "external_action_authority": False,
            }
    else:
        if shadow_manifest_path is not None:
            raise ManifestError("--shadow-manifest supplied but declared shadow root is absent")
        if shadow_review_root.exists():
            raise ManifestError("shadow review root cannot exist without shadow root")
        if (
            shadow_review_manifest_path is not None
            or expected_shadow_review_receipt_sha256 is not None
        ):
            raise ManifestError("shadow review arguments supplied but shadow root is absent")
        shadow_result = {
            "shadow_generation_valid": False,
            "shadow_state": "ABSENT_AUTHORIZED",
            "shadow_manifest_hash_bound": False,
            "domain_gate_mechanical_acceptance_observed": False,
            "domain_semantic_gate_accepted": False,
            "rejection_protocol_bound": False,
            "local_shadow_candidate_accepted": False,
            "host_level_universal_noninterference_proven": False,
            "natural_language_speech_act_inference_proven": False,
            "semantic_truth_of_human_labels_proven": False,
            "real_world_temporal_order_proven": False,
            "actual_lane_generation_isolation_proven": False,
            "capability_authority": False,
            "runtime_authority": False,
            "deployment_authority": False,
            "freeze_authority": False,
            "external_action_authority": False,
        }

    final_candidate_result = validate_manifest(
        candidate_manifest_path,
        phase="post-closure",
    )
    for key in (
        "candidate_id",
        "manifest_sha256",
        "active_files",
        "historical_files",
        "candidate_inventory_digest_sha256",
    ):
        if final_candidate_result[key] != candidate_result[key]:
            raise ManifestError(
                f"candidate changed during aggregate validation: {key}"
            )
    require_regular_snapshot_current(
        candidate_manifest_path,
        candidate_snapshot,
        "candidate_manifest final stability",
    )

    return {
        "candidate_id": candidate_result["candidate_id"],
        "candidate_manifest_sha256": governance_chain["candidate_hash"],
        "candidate_snapshot_valid": True,
        "closure_chain_valid": True,
        "closure_decision_sha256": governance_chain["closure_decision_hash"],
        "external_action_authority": False,
        "governance_manifest_sha256": governance_chain["governance_manifest_hash"],
        "governance_root_valid": True,
        **shadow_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_manifest", type=Path)
    parser.add_argument("--governance-manifest", type=Path, required=True)
    parser.add_argument(
        "--expected-closure-decision-sha256",
        required=True,
    )
    parser.add_argument("--shadow-manifest", type=Path)
    parser.add_argument("--shadow-review-manifest", type=Path)
    parser.add_argument("--expected-shadow-review-receipt-sha256")
    args = parser.parse_args()
    try:
        result = validate_aggregate(
            candidate_manifest_path=args.candidate_manifest,
            governance_manifest_path=args.governance_manifest,
            expected_decision_sha256=args.expected_closure_decision_sha256,
            shadow_manifest_path=args.shadow_manifest,
            shadow_review_manifest_path=args.shadow_review_manifest,
            expected_shadow_review_receipt_sha256=(
                args.expected_shadow_review_receipt_sha256
            ),
        )
    except ManifestError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"valid": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
