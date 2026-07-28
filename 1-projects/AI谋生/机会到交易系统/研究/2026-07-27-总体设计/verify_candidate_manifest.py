#!/usr/bin/env python3
"""Fail-closed verifier for the research candidate manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


TOP_LEVEL_KEYS = {
    "schema_version",
    "candidate_id",
    "status",
    "scope",
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
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


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


def validate_manifest(manifest_path: Path) -> dict[str, Any]:
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
    if document["schema_version"] != "1.0":
        raise ManifestError("manifest.schema_version must equal '1.0'")
    require_string(document["candidate_id"], "manifest.candidate_id")
    require_string(document["status"], "manifest.status")
    require_string(document["scope"], "manifest.scope")
    entries = document["entries"]
    exclusions = document["historical_exclusions"]
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest.entries must be a non-empty list")
    if not isinstance(exclusions, list):
        raise ManifestError("manifest.historical_exclusions must be a list")

    base = manifest_path.resolve().parent
    manifest_name = manifest_path.name
    dependencies_by_path: dict[str, list[str]] = {}
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

    known_paths = active_paths | historical_paths
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
    for candidate in base.rglob("*"):
        if candidate.is_symlink():
            raise ManifestError(
                f"unlisted or listed symlink in inventory: "
                f"{candidate.relative_to(base).as_posix()}"
            )
        if not candidate.is_file() or candidate.resolve() == manifest_path.resolve():
            continue
        inventory_paths.add(candidate.relative_to(base).as_posix())
    unlisted = sorted(inventory_paths - known_paths)
    if unlisted:
        raise ManifestError(f"unlisted project files: {unlisted}")
    listed_but_absent = sorted(known_paths - inventory_paths)
    if listed_but_absent:
        raise ManifestError(f"listed files absent from project inventory: {listed_but_absent}")

    return {
        "candidate_id": document["candidate_id"],
        "manifest_sha256": sha256_file(manifest_path),
        "active_files": len(active_paths),
        "historical_files": len(historical_paths),
        "status": document["status"],
        "scope": document["scope"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        result = validate_manifest(args.manifest)
    except ManifestError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"valid": True, **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
