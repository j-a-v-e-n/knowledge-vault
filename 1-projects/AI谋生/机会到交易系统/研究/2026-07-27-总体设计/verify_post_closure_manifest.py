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

from verify_candidate_manifest import (
    ManifestError,
    SHA256_RE,
    reject_duplicate_keys,
    require_exact_keys,
    require_string,
    sha256_file,
    validate_manifest,
)


CANDIDATE_VERIFIER_PATH = "研究/2026-07-27-总体设计/verify_candidate_manifest.py"
ACTION_ENVELOPE_PATH = "研究/2026-07-27-总体设计/READ_ONLY_SHADOW_ACTION_ENVELOPE.md"
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
    "governance_manifest_sha256",
    "independent_review_receipt_sha256",
    "closure_decision_sha256",
    "action_envelope_path",
    "action_envelope_sha256",
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
    "source",
    "test",
    "fixture",
    "documentation",
    "verification-script",
}
SHADOW_STATUS = "SHADOW_IMPLEMENTATION_CANDIDATE"
SHADOW_SCOPE = "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY"


def canonical_document(path: Path, label: str) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        document = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{label}: cannot read canonical JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ManifestError(f"{label}: root must be an object")
    canonical = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if text != canonical:
        raise ManifestError(f"{label}: JSON is not canonically serialized")
    return document


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

    governance = canonical_document(governance_manifest_path, "governance_manifest")
    require_exact_keys(governance, GOVERNANCE_MANIFEST_KEYS, "governance_manifest")
    if governance["schema_version"] != "otts.post-closure-governance-manifest/1":
        raise ManifestError("governance manifest schema_version mismatch")
    if governance["artifact_kind"] != "CLOSURE_GOVERNANCE":
        raise ManifestError("governance artifact_kind mismatch")

    candidate_id = candidate_document["candidate_id"]
    candidate_hash = sha256_file(candidate_manifest_path)
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
    freeze_path = expected_root / freeze_name
    review_path = expected_root / review_name
    decision_path = expected_root / decision_name
    freeze_hash = sha256_file(freeze_path)
    review_hash = sha256_file(review_path)
    decision_hash = sha256_file(decision_path)
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

    freeze = canonical_document(freeze_path, "freeze_report")
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
    ]
    states = freeze["post_closure_root_states"]
    if not isinstance(states, list):
        raise ManifestError("freeze post_closure_root_states must be a list")
    for index, state_row in enumerate(states):
        if not isinstance(state_row, dict):
            raise ManifestError(f"freeze root state {index}: expected object")
        require_exact_keys(state_row, ROOT_STATE_KEYS, f"freeze root state {index}")
    if states != expected_root_states:
        raise ManifestError("freeze root states do not prove both roots absent")

    review = canonical_document(review_path, "independent_review_receipt")
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
    if review["action_envelope_path"] != ACTION_ENVELOPE_PATH:
        raise ManifestError("review action envelope path mismatch")
    if require_sha(
        review["action_envelope_sha256"],
        "review.action_envelope_sha256",
    ) != envelope_hash:
        raise ManifestError("review action envelope hash mismatch")

    decision = canonical_document(decision_path, "closure_decision")
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

    return {
        "candidate_hash": candidate_hash,
        "candidate_id": candidate_id,
        "closure_decision_hash": decision_hash,
        "envelope_hash": envelope_hash,
        "freeze_report_hash": freeze_hash,
        "governance_manifest_hash": sha256_file(governance_manifest_path),
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

    shadow = canonical_document(shadow_manifest_path, "shadow_manifest")
    require_exact_keys(shadow, SHADOW_MANIFEST_KEYS, "shadow_manifest")
    if shadow["schema_version"] != "otts.shadow-artifact-manifest/1":
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
    if require_sha(
        shadow["parent_candidate_manifest_sha256"],
        "shadow.parent_candidate_manifest_sha256",
    ) != governance_chain["candidate_hash"]:
        raise ManifestError("shadow parent candidate hash mismatch")
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

    entries = shadow["entries"]
    if not isinstance(entries, list) or not entries:
        raise ManifestError("shadow entries must be a non-empty list")
    paths: set[str] = set()
    dependencies: dict[str, list[str]] = {}
    for index, raw in enumerate(entries):
        label = f"shadow.entries[{index}]"
        if not isinstance(raw, dict):
            raise ManifestError(f"{label}: expected object")
        require_exact_keys(raw, SHADOW_ENTRY_KEYS, label)
        relative, resolved = resolve_regular(shadow_root, raw["path"], f"{label}.path")
        if relative in paths:
            raise ManifestError(f"{label}: duplicate path")
        if resolved == shadow_manifest_path.resolve():
            raise ManifestError("shadow manifest must not include itself")
        expected_hash = require_sha(raw["sha256"], f"{label}.sha256")
        if sha256_file(resolved) != expected_hash:
            raise ManifestError(f"{label}: hash mismatch")
        if raw["role"] not in SHADOW_ROLES:
            raise ManifestError(f"{label}: unknown role")
        if raw["authority_status"] != "NO_EXTERNAL_AUTHORITY":
            raise ManifestError(f"{label}: authority_status must deny external authority")
        dependencies[relative] = require_string_list(
            raw["depends_on"], f"{label}.depends_on"
        )
        paths.add(relative)

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

    return {
        "shadow_generation_valid": True,
        "shadow_manifest_sha256": sha256_file(shadow_manifest_path),
        "shadow_state": "PRESENT_VALID",
    }


def validate_aggregate(
    *,
    candidate_manifest_path: Path,
    governance_manifest_path: Path,
    expected_decision_sha256: str,
    shadow_manifest_path: Path | None,
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
    candidate_document = canonical_document(
        candidate_manifest_path,
        "candidate_manifest",
    )
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
    if shadow_root.exists():
        if shadow_manifest_path is None:
            raise ManifestError("present shadow root requires explicit --shadow-manifest")
        shadow_result = validate_shadow(
            candidate_manifest_path=candidate_manifest_path,
            candidate_document=candidate_document,
            governance_chain=governance_chain,
            shadow_manifest_path=shadow_manifest_path.resolve(),
        )
    else:
        if shadow_manifest_path is not None:
            raise ManifestError("--shadow-manifest supplied but declared shadow root is absent")
        shadow_result = {
            "shadow_generation_valid": False,
            "shadow_state": "ABSENT_AUTHORIZED",
        }

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
    args = parser.parse_args()
    try:
        result = validate_aggregate(
            candidate_manifest_path=args.candidate_manifest,
            governance_manifest_path=args.governance_manifest,
            expected_decision_sha256=args.expected_closure_decision_sha256,
            shadow_manifest_path=args.shadow_manifest,
        )
    except ManifestError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"valid": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
