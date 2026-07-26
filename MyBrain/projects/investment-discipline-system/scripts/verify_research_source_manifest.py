#!/usr/bin/env python3
"""Verify the replayable R10 research-source manifest and report coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path("research/evidence/r10/SOURCE_MANIFEST.json")
TOP_LEVEL_FIELDS = {
    "schema_version",
    "manifest_id",
    "created_at_utc",
    "scope",
    "report_paths",
    "authority_rules",
    "sources",
    "local_sources",
    "excluded_mutable_field_sources",
}
AUTHORITY_RULE_FIELDS = {
    "fixed_snapshot",
    "mutable_snapshot",
    "field_probe_only",
    "local_artifact",
}
SOURCE_FIELDS = {
    "source_ids",
    "canonical_title",
    "canonical_version_locator",
    "revision_state",
    "snapshot_status",
    "snapshot_artifacts",
    "authority",
}
SOURCE_TIME_FIELDS = {"retrieved_at_utc", "retrieval_observation_ended_at_utc"}
SOURCE_OPTIONAL_FIELDS = SOURCE_TIME_FIELDS | {"retrieval_limit"}
ARTIFACT_REQUIRED_FIELDS = {"path", "byte_count", "sha256"}
ARTIFACT_OPTIONAL_FIELDS = {"retrieved_at_utc", "validation", "claim_boundary"}
LOCAL_SOURCE_FIELDS = {"local_source_id", "path", "sha256", "scope"}
EXCLUDED_FIELDS = {"source_ids", "reason"}
SOURCE_ID_RE = re.compile(r"^[MF]-[SP][0-9]{2}$")
LOCAL_SOURCE_ID_RE = re.compile(r"^LOCAL-[A-Z0-9][A-Z0-9-]{1,95}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_UTC_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
)
REPORT_SOURCE_ID_RE = re.compile(r"\b[MF]-[SP][0-9]{2}\b")


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite a prior key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {token!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError("top-level value must be an object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_regular_file(
    root: Path,
    value: Any,
    field: str,
    errors: list[str],
) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field}: path must be a nonempty string")
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{field}: path must remain project-relative")
        return None
    candidate = root / relative
    cursor = root
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            errors.append(f"{field}: symlinks are forbidden")
            return None
    try:
        resolved_root = root.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"{field}: path cannot be resolved: {exc}")
        return None
    if resolved != resolved_root and resolved_root not in resolved.parents:
        errors.append(f"{field}: path escapes the project")
        return None
    if not resolved.is_file():
        errors.append(f"{field}: path must be a regular file")
        return None
    return resolved


def validate_timestamp(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or RFC3339_UTC_RE.fullmatch(value) is None:
        errors.append(f"{field}: timestamp must use YYYY-MM-DDTHH:MM:SSZ")


def validate_artifact(
    artifact: Any,
    *,
    root: Path,
    field: str,
    seen_paths: set[str],
    errors: list[str],
) -> bool:
    if not isinstance(artifact, dict):
        errors.append(f"{field}: artifact must be an object")
        return False
    fields = set(artifact)
    if not ARTIFACT_REQUIRED_FIELDS <= fields or not fields <= (
        ARTIFACT_REQUIRED_FIELDS | ARTIFACT_OPTIONAL_FIELDS
    ):
        errors.append(f"{field}: artifact fields are not exact")
        return False
    path_value = artifact["path"]
    if path_value in seen_paths:
        errors.append(f"{field}: duplicate artifact path {path_value!r}")
    elif isinstance(path_value, str):
        seen_paths.add(path_value)
    path = resolve_regular_file(root, path_value, f"{field}.path", errors)
    byte_count = artifact["byte_count"]
    digest = artifact["sha256"]
    valid = True
    if type(byte_count) is not int or byte_count < 0:
        errors.append(f"{field}.byte_count: must be a nonnegative integer")
        valid = False
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        errors.append(f"{field}.sha256: invalid SHA-256")
        valid = False
    if "retrieved_at_utc" in artifact:
        validate_timestamp(
            artifact["retrieved_at_utc"],
            f"{field}.retrieved_at_utc",
            errors,
        )
    for optional in ("validation", "claim_boundary"):
        if optional in artifact and not nonempty_string(artifact[optional]):
            errors.append(f"{field}.{optional}: must be nonempty")
    if path is not None and valid:
        observed_size = path.stat().st_size
        if observed_size != byte_count:
            errors.append(
                f"{field}.byte_count mismatch: expected {byte_count}, "
                f"observed {observed_size}"
            )
        observed_digest = sha256(path)
        if observed_digest != digest:
            errors.append(
                f"{field}.sha256 mismatch: expected {digest}, "
                f"observed {observed_digest}"
            )
        if path.suffix.lower() == ".pdf" and not path.read_bytes().startswith(b"%PDF-"):
            errors.append(f"{field}: .pdf snapshot lacks PDF file magic")
    return path is not None and valid


def verify_manifest(
    manifest: dict[str, Any],
    *,
    project_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        root = project_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return {
            "verification_status": "invalid",
            "manifest_id": manifest.get("manifest_id"),
            "source_id_count": 0,
            "snapshot_artifact_count": 0,
            "local_source_count": 0,
            "covered_report_source_ids": [],
            "errors": [f"project root cannot be resolved: {exc}"],
            "claim_boundary": (
                "Valid means only that declared local bytes, hashes, and report "
                "source-ID coverage are internally consistent."
            ),
        }

    if set(manifest) != TOP_LEVEL_FIELDS:
        errors.append("manifest top-level fields are not exact")
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if manifest.get("manifest_id") != (
        "AI-PROJECT-METHOD-FAILURE-R10-SOURCE-MANIFEST"
    ):
        errors.append("unexpected manifest_id")
    validate_timestamp(
        manifest.get("created_at_utc"),
        "created_at_utc",
        errors,
    )
    if not nonempty_string(manifest.get("scope")):
        errors.append("scope must be nonempty")
    rules = manifest.get("authority_rules")
    if not isinstance(rules, dict) or set(rules) != AUTHORITY_RULE_FIELDS:
        errors.append("authority_rules fields are not exact")
    elif any(not nonempty_string(value) for value in rules.values()):
        errors.append("authority_rules values must be nonempty")

    source_ids: set[str] = set()
    snapshot_paths: set[str] = set()
    snapshot_artifact_count = 0
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a nonempty list")
        sources = []
    for source_index, source in enumerate(sources):
        field = f"sources[{source_index}]"
        if not isinstance(source, dict):
            errors.append(f"{field}: source must be an object")
            continue
        time_fields = set(source) & SOURCE_TIME_FIELDS
        if (
            set(source) - SOURCE_OPTIONAL_FIELDS != SOURCE_FIELDS
            or len(time_fields) != 1
            or not set(source) <= (SOURCE_FIELDS | SOURCE_OPTIONAL_FIELDS)
        ):
            errors.append(f"{field}: source fields are not exact")
            continue
        source_id_values = source["source_ids"]
        if not isinstance(source_id_values, list) or not source_id_values:
            errors.append(f"{field}.source_ids: must be nonempty")
            source_id_values = []
        local_ids: set[str] = set()
        for source_id in source_id_values:
            if not isinstance(source_id, str) or SOURCE_ID_RE.fullmatch(source_id) is None:
                errors.append(f"{field}.source_ids: invalid source id {source_id!r}")
                continue
            if source_id in local_ids or source_id in source_ids:
                errors.append(f"{field}.source_ids: duplicate source id {source_id}")
                continue
            local_ids.add(source_id)
            source_ids.add(source_id)
        for name in (
            "canonical_title",
            "canonical_version_locator",
            "revision_state",
            "snapshot_status",
            "authority",
        ):
            if not nonempty_string(source[name]):
                errors.append(f"{field}.{name}: must be nonempty")
        if (
            not isinstance(source["canonical_version_locator"], str)
            or not source["canonical_version_locator"].startswith("https://")
        ):
            errors.append(f"{field}.canonical_version_locator: must use https")
        time_field = next(iter(time_fields))
        validate_timestamp(source[time_field], f"{field}.{time_field}", errors)
        if "retrieval_limit" in source and not nonempty_string(
            source["retrieval_limit"]
        ):
            errors.append(f"{field}.retrieval_limit: must be nonempty")
        artifacts = source["snapshot_artifacts"]
        if not isinstance(artifacts, list):
            errors.append(f"{field}.snapshot_artifacts: must be a list")
            artifacts = []
        retained = str(source["snapshot_status"]).startswith("retained")
        if retained != bool(artifacts):
            errors.append(
                f"{field}: retained snapshot status and artifact presence differ"
            )
        for artifact_index, artifact in enumerate(artifacts):
            validate_artifact(
                artifact,
                root=root,
                field=f"{field}.snapshot_artifacts[{artifact_index}]",
                seen_paths=snapshot_paths,
                errors=errors,
            )
            snapshot_artifact_count += 1

    local_source_count = 0
    local_ids: set[str] = set()
    local_paths: set[str] = set()
    local_sources = manifest.get("local_sources")
    if not isinstance(local_sources, list) or not local_sources:
        errors.append("local_sources must be a nonempty list")
        local_sources = []
    for index, source in enumerate(local_sources):
        field = f"local_sources[{index}]"
        if not isinstance(source, dict) or set(source) != LOCAL_SOURCE_FIELDS:
            errors.append(f"{field}: fields are not exact")
            continue
        local_id = source["local_source_id"]
        if (
            not isinstance(local_id, str)
            or LOCAL_SOURCE_ID_RE.fullmatch(local_id) is None
            or local_id in local_ids
        ):
            errors.append(f"{field}.local_source_id: invalid or duplicated")
        else:
            local_ids.add(local_id)
        path_value = source["path"]
        if path_value in local_paths:
            errors.append(f"{field}.path: duplicate local source path")
        elif isinstance(path_value, str):
            local_paths.add(path_value)
        path = resolve_regular_file(root, path_value, f"{field}.path", errors)
        digest = source["sha256"]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            errors.append(f"{field}.sha256: invalid SHA-256")
        elif path is not None and sha256(path) != digest:
            errors.append(f"{field}.sha256 mismatch")
        if not nonempty_string(source["scope"]):
            errors.append(f"{field}.scope: must be nonempty")
        local_source_count += 1

    excluded = manifest.get("excluded_mutable_field_sources")
    excluded_ids: set[str] = set()
    if not isinstance(excluded, dict) or set(excluded) != EXCLUDED_FIELDS:
        errors.append("excluded_mutable_field_sources fields are not exact")
    else:
        values = excluded["source_ids"]
        if not isinstance(values, list) or not values:
            errors.append("excluded source_ids must be a nonempty list")
        else:
            for source_id in values:
                if (
                    not isinstance(source_id, str)
                    or SOURCE_ID_RE.fullmatch(source_id) is None
                    or source_id in excluded_ids
                    or source_id in source_ids
                ):
                    errors.append(
                        f"excluded source id {source_id!r} is invalid, duplicated, "
                        "or also snapshotted"
                    )
                else:
                    excluded_ids.add(source_id)
        if not nonempty_string(excluded["reason"]):
            errors.append("excluded source reason must be nonempty")

    report_paths = manifest.get("report_paths")
    observed_report_ids: set[str] = set()
    seen_report_paths: set[str] = set()
    if not isinstance(report_paths, list) or not report_paths:
        errors.append("report_paths must be a nonempty list")
        report_paths = []
    for index, path_value in enumerate(report_paths):
        field = f"report_paths[{index}]"
        if path_value in seen_report_paths:
            errors.append(f"{field}: duplicate report path")
        elif isinstance(path_value, str):
            seen_report_paths.add(path_value)
        path = resolve_regular_file(root, path_value, field, errors)
        if path is not None:
            observed_report_ids.update(
                REPORT_SOURCE_ID_RE.findall(path.read_text(encoding="utf-8"))
            )
    covered_ids = source_ids | excluded_ids
    missing_ids = sorted(observed_report_ids - covered_ids)
    if missing_ids:
        errors.append(f"report source IDs are absent from manifest: {missing_ids}")

    return {
        "verification_status": "valid" if not errors else "invalid",
        "manifest_id": manifest.get("manifest_id"),
        "source_id_count": len(source_ids),
        "snapshot_artifact_count": snapshot_artifact_count,
        "local_source_count": local_source_count,
        "covered_report_source_ids": sorted(observed_report_ids),
        "errors": sorted(set(errors)),
        "claim_boundary": (
            "Valid means only that declared local bytes, hashes, and report "
            "source-ID coverage are internally consistent. It does not prove "
            "claim entailment, source truth, external freshness, method "
            "sufficiency, design freeze, or product completion."
        ),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        root = args.project_root.resolve(strict=True)
        manifest_path = (
            args.manifest
            if args.manifest.is_absolute()
            else root / args.manifest
        )
        manifest = load_json(manifest_path)
        receipt = verify_manifest(manifest, project_root=root)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        receipt = {
            "verification_status": "invalid",
            "manifest_id": None,
            "source_id_count": 0,
            "snapshot_artifact_count": 0,
            "local_source_count": 0,
            "covered_report_source_ids": [],
            "errors": [f"manifest cannot be loaded: {exc}"],
            "claim_boundary": (
                "Valid means only that declared local bytes, hashes, and report "
                "source-ID coverage are internally consistent."
            ),
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
        print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["verification_status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
