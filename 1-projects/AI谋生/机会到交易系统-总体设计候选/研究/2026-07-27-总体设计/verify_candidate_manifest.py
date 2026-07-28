#!/usr/bin/env python3
"""Fail-closed verifier for the research candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True

from verify_run2_acceptance import (  # noqa: E402
    AcceptanceError,
    validate_acceptance,
)


TOP_LEVEL_KEYS = {
    "schema_version",
    "candidate_id",
    "status",
    "scope",
    "candidate_inventory_root",
    "post_closure_artifact_roots",
    "entries",
    "historical_exclusions",
}
ENTRY_KEYS = {
    "path",
    "sha256",
    "role",
    "authority_status",
    "depends_on",
}
HISTORICAL_KEYS = ENTRY_KEYS | {"exclusion_reason"}
POST_CLOSURE_ROOT_KEYS = {
    "root_id",
    "path_from_candidate_parent",
    "artifact_kind",
    "required_manifest",
    "freeze_required_state",
    "post_closure_required_state",
    "activation_gate",
    "governed_by_path",
    "governed_by_sha256",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PHASES = {"freeze", "post-closure"}
POST_CLOSURE_ROOT_POLICIES = {
    "closure-governance": {
        "path_from_candidate_parent": "机会到交易系统-闭合记录",
        "artifact_kind": "CLOSURE_GOVERNANCE",
        "required_manifest": "GOVERNANCE_ARTIFACT_MANIFEST.json",
        "freeze_required_state": "MUST_BE_ABSENT",
        "post_closure_required_state": "MUST_BE_PRESENT",
        "activation_gate": "EXACT_CANDIDATE_REVIEW_PASS",
    },
    "shadow-mvp": {
        "path_from_candidate_parent": "机会到交易系统-shadow-mvp",
        "artifact_kind": "READ_ONLY_SHADOW_MVP",
        "required_manifest": "SHADOW_ARTIFACT_MANIFEST.json",
        "freeze_required_state": "MUST_BE_ABSENT",
        "post_closure_required_state": "MAY_BE_ABSENT_OR_VALID",
        "activation_gate": "EXACT_CLOSURE_DECISION",
    },
    "shadow-review": {
        "path_from_candidate_parent": "机会到交易系统-shadow-review",
        "artifact_kind": "SHADOW_INDEPENDENT_REVIEW",
        "required_manifest": "SHADOW_REVIEW_MANIFEST.json",
        "freeze_required_state": "MUST_BE_ABSENT",
        "post_closure_required_state": "MAY_BE_ABSENT_OR_VALID",
        "activation_gate": (
            "EXACT_DECLARATIVE_SHADOW_SNAPSHOT_AND_CALLER_BOUND_REVIEW"
        ),
    },
}
REAL_CANDIDATE_ROOT_NAME = "机会到交易系统-总体设计候选"
REAL_CANDIDATE_ID = "OTTS-DESIGN-20260727-C6"
REAL_CANDIDATE_ROOT = Path(__file__).resolve().parents[2]
RUN2_ACCEPTANCE_PATH = (
    "研究/2026-07-27-总体设计/ssp-run2/"
    "FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json"
)
RUN2_ACCEPTANCE_VERIFIER_PATH = (
    "研究/2026-07-27-总体设计/verify_run2_acceptance.py"
)
RUN2_ACCEPTANCE_TEST_PATH = "研究/2026-07-27-总体设计/test_run2_acceptance.py"
REQUIRED_RUN2_ACCEPTANCE_PATHS = {
    RUN2_ACCEPTANCE_PATH,
    RUN2_ACCEPTANCE_VERIFIER_PATH,
    RUN2_ACCEPTANCE_TEST_PATH,
}


class ManifestError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManifestError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ManifestError(f"{label}: key mismatch; missing={missing}; extra={extra}")


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{label}: expected non-empty string")
    return value


def resolve_member(base: Path, relative_text: Any, label: str) -> tuple[str, Path]:
    relative = require_string(relative_text, label)
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise ManifestError(f"{label}: path must be normalized and relative: {relative!r}")
    unresolved = base / Path(*pure.parts)
    if unresolved.is_symlink():
        raise ManifestError(f"{label}: symlinks are not allowed: {relative!r}")
    resolved = unresolved.resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise ManifestError(f"{label}: path escapes manifest directory: {relative!r}") from exc
    return relative, resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_post_closure_root(
    raw: Any,
    *,
    candidate_parent: Path,
    candidate_root_name: str,
    label: str,
    phase: str,
) -> dict[str, str | bool]:
    if not isinstance(raw, dict):
        raise ManifestError(f"{label}: expected object")
    require_exact_keys(raw, POST_CLOSURE_ROOT_KEYS, label)
    root_id = require_string(raw["root_id"], f"{label}.root_id")
    root_name = require_string(
        raw["path_from_candidate_parent"],
        f"{label}.path_from_candidate_parent",
    )
    root_pure = PurePosixPath(root_name)
    if root_pure.parts != (root_name,) or root_name in {".", ".."}:
        raise ManifestError(
            f"{label}.path_from_candidate_parent: expected one normalized sibling name"
        )
    if root_name == candidate_root_name:
        raise ManifestError(f"{label}: post-closure root overlaps candidate root")
    artifact_kind = require_string(raw["artifact_kind"], f"{label}.artifact_kind")
    required_manifest = require_string(
        raw["required_manifest"], f"{label}.required_manifest"
    )
    manifest_pure = PurePosixPath(required_manifest)
    if manifest_pure.parts != (required_manifest,) or required_manifest in {".", ".."}:
        raise ManifestError(f"{label}.required_manifest: expected one normalized filename")
    freeze_required_state = require_string(
        raw["freeze_required_state"], f"{label}.freeze_required_state"
    )
    post_closure_required_state = require_string(
        raw["post_closure_required_state"],
        f"{label}.post_closure_required_state",
    )
    activation_gate = require_string(raw["activation_gate"], f"{label}.activation_gate")
    governed_by_path = require_string(
        raw["governed_by_path"], f"{label}.governed_by_path"
    )
    governed_by_sha256 = require_string(
        raw["governed_by_sha256"], f"{label}.governed_by_sha256"
    )
    if not SHA256_RE.fullmatch(governed_by_sha256):
        raise ManifestError(f"{label}.governed_by_sha256: expected lowercase SHA-256")

    policy = POST_CLOSURE_ROOT_POLICIES.get(root_id)
    if policy is None:
        raise ManifestError(f"{label}.root_id: unknown root policy")
    declared_policy = {
        "path_from_candidate_parent": root_name,
        "artifact_kind": artifact_kind,
        "required_manifest": required_manifest,
        "freeze_required_state": freeze_required_state,
        "post_closure_required_state": post_closure_required_state,
        "activation_gate": activation_gate,
    }
    if declared_policy != policy:
        raise ManifestError(f"{label}: declaration does not match frozen root policy")

    root_path = candidate_parent / root_name
    if root_path.is_symlink():
        raise ManifestError(f"{label}: post-closure root must not be a symlink")
    exists = root_path.exists()
    if phase == "freeze" and freeze_required_state == "MUST_BE_ABSENT" and exists:
        raise ManifestError(
            f"{label}: post-closure root must be absent during candidate freeze: {root_name}"
        )
    if (
        phase == "post-closure"
        and post_closure_required_state == "MUST_BE_PRESENT"
        and not exists
    ):
        raise ManifestError(f"{label}: required post-closure root is absent: {root_name}")
    if phase == "post-closure" and exists:
        if not root_path.is_dir():
            raise ManifestError(f"{label}: post-closure root is not a directory")
        root_manifest = root_path / required_manifest
        if root_manifest.is_symlink() or not root_manifest.is_file():
            raise ManifestError(
                f"{label}: present root lacks regular required manifest: "
                f"{root_name}/{required_manifest}"
            )
    return {
        "root_id": root_id,
        "root_name": root_name,
        "artifact_kind": artifact_kind,
        "required_manifest": required_manifest,
        "activation_gate": activation_gate,
        "governed_by_path": governed_by_path,
        "governed_by_sha256": governed_by_sha256,
        "present": exists,
    }


def validate_entry(
    raw: Any,
    *,
    base: Path,
    label: str,
    historical: bool,
) -> tuple[str, list[str]]:
    if not isinstance(raw, dict):
        raise ManifestError(f"{label}: expected object")
    require_exact_keys(raw, HISTORICAL_KEYS if historical else ENTRY_KEYS, label)
    relative, resolved = resolve_member(base, raw["path"], f"{label}.path")
    expected_hash = require_string(raw["sha256"], f"{label}.sha256")
    if not SHA256_RE.fullmatch(expected_hash):
        raise ManifestError(f"{label}.sha256: expected lowercase SHA-256")
    require_string(raw["role"], f"{label}.role")
    require_string(raw["authority_status"], f"{label}.authority_status")
    if historical:
        require_string(raw["exclusion_reason"], f"{label}.exclusion_reason")
    dependencies = raw["depends_on"]
    if not isinstance(dependencies, list) or any(
        not isinstance(item, str) or not item for item in dependencies
    ):
        raise ManifestError(f"{label}.depends_on: expected string list")
    if len(dependencies) != len(set(dependencies)):
        raise ManifestError(f"{label}.depends_on: duplicate dependency")
    if not resolved.is_file():
        raise ManifestError(f"{label}: missing file: {relative}")
    actual_hash = sha256_file(resolved)
    if actual_hash != expected_hash:
        raise ManifestError(
            f"{label}: hash mismatch for {relative}; "
            f"expected={expected_hash}; actual={actual_hash}"
        )
    return relative, dependencies


def validate_manifest(manifest_path: Path, *, phase: str = "freeze") -> dict[str, Any]:
    if phase not in PHASES:
        raise ManifestError(f"unknown verification phase: {phase!r}")
    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
        document = json.loads(manifest_text, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read canonical JSON manifest: {exc}") from exc
    if not isinstance(document, dict):
        raise ManifestError("manifest root must be an object")
    require_exact_keys(document, TOP_LEVEL_KEYS, "manifest")
    canonical_text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if manifest_text != canonical_text:
        raise ManifestError("manifest is valid JSON but not in canonical serialized form")
    if document["schema_version"] != "1.1":
        raise ManifestError("manifest.schema_version must equal '1.1'")
    require_string(document["candidate_id"], "manifest.candidate_id")
    require_string(document["status"], "manifest.status")
    require_string(document["scope"], "manifest.scope")
    if document["candidate_inventory_root"] != ".":
        raise ManifestError("manifest.candidate_inventory_root must equal '.'")
    entries = document["entries"]
    exclusions = document["historical_exclusions"]
    post_closure_roots = document["post_closure_artifact_roots"]
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest.entries must be a non-empty list")
    if not isinstance(exclusions, list):
        raise ManifestError("manifest.historical_exclusions must be a list")
    if not isinstance(post_closure_roots, list) or not post_closure_roots:
        raise ManifestError("manifest.post_closure_artifact_roots must be non-empty")

    base = manifest_path.resolve().parent
    candidate_parent = base.parent
    manifest_name = manifest_path.name
    root_declarations = [
        validate_post_closure_root(
            raw,
            candidate_parent=candidate_parent,
            candidate_root_name=base.name,
            label=f"post_closure_artifact_roots[{index}]",
            phase=phase,
        )
        for index, raw in enumerate(post_closure_roots)
    ]
    root_ids = [str(item["root_id"]) for item in root_declarations]
    root_names = [str(item["root_name"]) for item in root_declarations]
    if len(root_ids) != len(set(root_ids)):
        raise ManifestError("duplicate post-closure root_id")
    if set(root_ids) != set(POST_CLOSURE_ROOT_POLICIES):
        raise ManifestError("post-closure root declarations do not match policy set")
    if len(root_names) != len(set(root_names)):
        raise ManifestError("duplicate post-closure sibling path")
    dependencies_by_path: dict[str, list[str]] = {}
    hashes_by_path: dict[str, str] = {}
    active_paths: set[str] = set()
    historical_paths: set[str] = set()

    for index, raw in enumerate(entries):
        path, dependencies = validate_entry(
            raw,
            base=base,
            label=f"entries[{index}]",
            historical=False,
        )
        if path in active_paths:
            raise ManifestError(f"duplicate active path: {path}")
        if path == manifest_name:
            raise ManifestError("manifest must not include itself")
        active_paths.add(path)
        dependencies_by_path[path] = dependencies
        hashes_by_path[path] = raw["sha256"]

    for index, raw in enumerate(exclusions):
        path, dependencies = validate_entry(
            raw,
            base=base,
            label=f"historical_exclusions[{index}]",
            historical=True,
        )
        if path in historical_paths or path in active_paths:
            raise ManifestError(f"duplicate or active/historical overlap: {path}")
        if path == manifest_name:
            raise ManifestError("manifest must not include itself")
        historical_paths.add(path)
        dependencies_by_path[path] = dependencies
        hashes_by_path[path] = raw["sha256"]

    known_paths = active_paths | historical_paths
    run2_acceptance_result: dict[str, Any] | None = None
    if base.name == REAL_CANDIDATE_ROOT_NAME:
        if base != REAL_CANDIDATE_ROOT:
            raise ManifestError(
                "real candidate root name is present at a path other than the "
                "candidate-specific verifier root"
            )
        if document["candidate_id"] != REAL_CANDIDATE_ID:
            raise ManifestError(
                f"manifest.candidate_id must equal {REAL_CANDIDATE_ID!r} for this root"
            )
        missing_acceptance = sorted(REQUIRED_RUN2_ACCEPTANCE_PATHS - active_paths)
        if missing_acceptance:
            raise ManifestError(
                f"real candidate omits required Run2 acceptance artifacts: {missing_acceptance}"
            )
        try:
            run2_acceptance_result = validate_acceptance(base / RUN2_ACCEPTANCE_PATH)
        except (AcceptanceError, OSError, UnicodeError) as exc:
            raise ManifestError(f"Run2 exact acceptance is invalid: {exc}") from exc

    for root in root_declarations:
        governed_by_path = str(root["governed_by_path"])
        governed_by_sha256 = str(root["governed_by_sha256"])
        if governed_by_path not in active_paths:
            raise ManifestError(
                f"post-closure root {root['root_id']}: governed_by_path is not active"
            )
        if hashes_by_path[governed_by_path] != governed_by_sha256:
            raise ManifestError(
                f"post-closure root {root['root_id']}: governed_by_sha256 mismatch"
            )
    for owner, dependencies in dependencies_by_path.items():
        for dependency in dependencies:
            if dependency not in known_paths:
                raise ManifestError(f"{owner}: unknown dependency: {dependency}")

    visit_state: dict[str, int] = {}

    def visit(path: str, stack: list[str]) -> None:
        state = visit_state.get(path, 0)
        if state == 2:
            return
        if state == 1:
            cycle_start = stack.index(path)
            cycle = stack[cycle_start:] + [path]
            raise ManifestError(f"dependency cycle: {' -> '.join(cycle)}")
        visit_state[path] = 1
        for dependency in dependencies_by_path[path]:
            visit(dependency, stack + [path])
        visit_state[path] = 2

    for path in sorted(known_paths):
        visit(path, [])

    inventory_paths: set[str] = set()
    inventory_directories: set[str] = set()
    for current, directory_names, file_names in os.walk(base, followlinks=False):
        current_path = Path(current)
        for name in list(directory_names):
            candidate = current_path / name
            relative = candidate.relative_to(base).as_posix()
            if candidate.is_symlink():
                raise ManifestError(f"symlink directory in candidate inventory: {relative}")
            if not stat.S_ISDIR(candidate.stat().st_mode):
                raise ManifestError(f"special directory node in candidate: {relative}")
            inventory_directories.add(relative)
        for name in file_names:
            candidate = current_path / name
            relative = candidate.relative_to(base).as_posix()
            if candidate.is_symlink():
                raise ManifestError(f"symlink file in candidate inventory: {relative}")
            candidate_stat = candidate.stat()
            if not stat.S_ISREG(candidate_stat.st_mode):
                raise ManifestError(f"special file in candidate inventory: {relative}")
            if candidate_stat.st_nlink != 1:
                raise ManifestError(f"hardlinked file in candidate inventory: {relative}")
            if candidate.resolve() == manifest_path.resolve():
                continue
            inventory_paths.add(relative)
    unlisted = sorted(inventory_paths - known_paths)
    if unlisted:
        raise ManifestError(f"unlisted project files: {unlisted}")
    listed_but_absent = sorted(known_paths - inventory_paths)
    if listed_but_absent:
        raise ManifestError(f"listed files absent from project inventory: {listed_but_absent}")
    expected_directories: set[str] = set()
    for relative in known_paths | {manifest_name}:
        parent = PurePosixPath(relative).parent
        while str(parent) not in {"", "."}:
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    extra_directories = sorted(inventory_directories - expected_directories)
    if extra_directories:
        raise ManifestError(f"unlisted candidate directories: {extra_directories}")

    inventory_identity = [
        {
            "authority_status": raw["authority_status"],
            "category": "active",
            "path": raw["path"],
            "role": raw["role"],
            "sha256": raw["sha256"],
        }
        for raw in entries
    ] + [
        {
            "authority_status": raw["authority_status"],
            "category": "historical",
            "exclusion_reason": raw["exclusion_reason"],
            "path": raw["path"],
            "role": raw["role"],
            "sha256": raw["sha256"],
        }
        for raw in exclusions
    ]
    inventory_identity.sort(key=lambda item: (item["category"], item["path"]))
    inventory_digest = hashlib.sha256(
        json.dumps(
            inventory_identity,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    result = {
        "candidate_id": document["candidate_id"],
        "manifest_sha256": sha256_file(manifest_path),
        "active_files": len(active_paths),
        "historical_files": len(historical_paths),
        "candidate_inventory_digest_sha256": inventory_digest,
        "verification_phase": phase,
        "post_closure_roots": [
            {
                "root_id": item["root_id"],
                "path_from_candidate_parent": item["root_name"],
                "present": item["present"],
                "state": "PRESENT" if item["present"] else "ABSENT",
            }
            for item in root_declarations
        ],
        "status": document["status"],
        "scope": document["scope"],
    }
    if run2_acceptance_result is not None:
        result["run2_final_status_acceptance"] = {
            "valid": True,
            "receipt_sha256": run2_acceptance_result["receipt_sha256"],
            "accepted_status": run2_acceptance_result["accepted_status"],
            "candidate_closure_authority": False,
            "implementation_authority": False,
            "shadow_operation_authority": False,
            "external_action_authority": False,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--phase", choices=sorted(PHASES), default="freeze")
    args = parser.parse_args()
    try:
        result = validate_manifest(args.manifest, phase=args.phase)
    except ManifestError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"valid": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
