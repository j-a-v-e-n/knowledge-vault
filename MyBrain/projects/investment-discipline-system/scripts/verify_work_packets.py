#!/usr/bin/env python3
"""Fail-closed ORG-01/ORG-03 work-packet and path-ownership verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_RELATIVE = Path("governance/WORK_PACKET_POLICY_V1.json")

POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "linked_failure_ids",
    "packet_discovery",
    "packet_schema",
    "path_rules",
    "ownership",
    "completion",
    "semantic_integration",
    "platform_and_process_limitations",
}
PACKET_FIELDS = (
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
)
PACKET_CONTRACT_FIELDS = (
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
)
STATE_VALUES = (
    "pending",
    "active",
    "blocked",
    "candidate_complete",
    "complete",
)
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@-]{0,127}$")
PACKET_ID_RE = re.compile(r"^WP-[A-Z0-9][A-Z0-9._-]{0,63}$")
GOAL_ID_RE = re.compile(r"^[A-Z][A-Z0-9._-]{1,63}$")
CHECK_ID_RE = re.compile(r"^CHECK-[A-Z0-9][A-Z0-9._-]{0,63}$")
INVARIANT_ID_RE = re.compile(r"^INV-[A-Z0-9][A-Z0-9._-]{0,63}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
INVALID = object()


class DuplicateKeyError(ValueError):
    """Raised when a JSON object attempts to overwrite a prior key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json_value(path: Path, errors: list[str], label: str) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: invalid or unreadable JSON: {exc}")
        return INVALID


def load_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any] | None:
    value = load_json_value(path, errors, label)
    if value is INVALID:
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


def packet_contract_sha256(packet: dict[str, Any]) -> str:
    return canonical_sha256({field: packet[field] for field in PACKET_CONTRACT_FIELDS})


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
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        errors.append(f"{label}: fields differ; missing={missing}, extra={extra}")
        return False
    return True


def is_int(value: Any) -> bool:
    return type(value) is int


def is_nonempty_string(value: Any, maximum: int = 256) -> bool:
    return (
        isinstance(value, str)
        and value == value.strip()
        and 0 < len(value) <= maximum
    )


def validate_unique_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    maximum_items: int | None = None,
    allow_empty: bool = True,
) -> list[str] | None:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or not all(is_nonempty_string(item) for item in value)
    ):
        errors.append(f"{label}: must be a list of non-empty strings")
        return None
    if maximum_items is not None and len(value) > maximum_items:
        errors.append(f"{label}: exceeds maximum item count {maximum_items}")
    if len(value) != len(set(value)):
        errors.append(f"{label}: duplicate entries are forbidden")
    return value


def validate_policy(policy: dict[str, Any], errors: list[str]) -> bool:
    start = len(errors)
    if not exact_keys(policy, POLICY_FIELDS, "policy", errors):
        return False
    if policy["schema_version"] != "work-packet-policy/v1":
        errors.append("policy: unsupported schema_version")
    if policy["policy_id"] != "ORG-01-ORG-03-WORK-PACKET-V1":
        errors.append("policy: unexpected policy_id")
    if policy["linked_failure_ids"] != ["ORG-01", "ORG-03"]:
        errors.append("policy: linked_failure_ids must be ORG-01 and ORG-03")

    discovery = policy["packet_discovery"]
    if exact_keys(
        discovery,
        {"filename_suffix", "recursive", "reject_unexpected_entries"},
        "policy.packet_discovery",
        errors,
    ):
        if discovery["filename_suffix"] != ".packet.json":
            errors.append("policy.packet_discovery: unsupported filename_suffix")
        if discovery["recursive"] is not False:
            errors.append("policy.packet_discovery: recursive discovery must be false")
        if discovery["reject_unexpected_entries"] is not True:
            errors.append(
                "policy.packet_discovery: unexpected entries must be rejected"
            )

    schema = policy["packet_schema"]
    if exact_keys(
        schema,
        {"instance_schema_version", "required_fields", "state_values"},
        "policy.packet_schema",
        errors,
    ):
        if schema["instance_schema_version"] != "work-packet-instance/v1":
            errors.append("policy.packet_schema: unsupported instance schema")
        if schema["required_fields"] != list(PACKET_FIELDS):
            errors.append("policy.packet_schema: required_fields differ")
        if schema["state_values"] != list(STATE_VALUES):
            errors.append("policy.packet_schema: state_values differ")

    paths = policy["path_rules"]
    path_fields = {
        "format",
        "forbidden_glob_characters",
        "minimum_tree_depth",
        "maximum_write_claims_per_packet",
        "maximum_read_dependencies_per_packet",
        "read_dependencies_must_exist",
        "nested_write_symlinks_allowed",
    }
    if exact_keys(paths, path_fields, "policy.path_rules", errors):
        if paths["format"] != "normalized_posix_relative":
            errors.append("policy.path_rules: unsupported path format")
        forbidden = validate_unique_string_list(
            paths["forbidden_glob_characters"],
            "policy.path_rules.forbidden_glob_characters",
            errors,
            allow_empty=False,
        )
        if forbidden is not None and set(forbidden) != set("*?[]{}"):
            errors.append("policy.path_rules: forbidden glob characters differ")
        if not is_int(paths["minimum_tree_depth"]) or paths["minimum_tree_depth"] < 2:
            errors.append("policy.path_rules: minimum_tree_depth must be at least 2")
        for field, upper in (
            ("maximum_write_claims_per_packet", 1024),
            ("maximum_read_dependencies_per_packet", 4096),
        ):
            item = paths[field]
            if not is_int(item) or not 1 <= item <= upper:
                errors.append(f"policy.path_rules: invalid {field}")
        if paths["read_dependencies_must_exist"] is not True:
            errors.append("policy.path_rules: read dependencies must exist")
        if paths["nested_write_symlinks_allowed"] is not False:
            errors.append("policy.path_rules: nested write symlinks must be rejected")

    ownership = policy["ownership"]
    if exact_keys(
        ownership,
        {
            "ownership_states",
            "conflict_relation",
            "read_dependencies_confer_write_ownership",
            "completed_packets_retain_write_ownership",
        },
        "policy.ownership",
        errors,
    ):
        if ownership["ownership_states"] != [
            "active",
            "blocked",
            "candidate_complete",
        ]:
            errors.append("policy.ownership: ownership_states differ")
        if ownership["conflict_relation"] != "canonical_equal_or_ancestor":
            errors.append("policy.ownership: unsupported conflict relation")
        if ownership["read_dependencies_confer_write_ownership"] is not False:
            errors.append("policy.ownership: read dependencies cannot own paths")
        if ownership["completed_packets_retain_write_ownership"] is not False:
            errors.append("policy.ownership: completed packets cannot retain ownership")

    completion = policy["completion"]
    completion_fields = {
        "checkpoint_required_states",
        "acceptance_required_states",
        "receipt_directory",
        "checkpoint_schema_version",
        "acceptance_schema_version",
        "checkpoint_filename_suffix",
        "acceptance_filename_suffix",
    }
    if exact_keys(completion, completion_fields, "policy.completion", errors):
        if completion["checkpoint_required_states"] != [
            "candidate_complete",
            "complete",
        ]:
            errors.append("policy.completion: checkpoint_required_states differ")
        if completion["acceptance_required_states"] != ["complete"]:
            errors.append("policy.completion: acceptance_required_states differ")
        if completion["receipt_directory"] != ".work_packets/receipts":
            errors.append("policy.completion: receipt_directory differs")
        if completion["checkpoint_schema_version"] != "work-packet-checkpoint/v1":
            errors.append("policy.completion: checkpoint schema differs")
        if completion["acceptance_schema_version"] != "work-packet-acceptance/v1":
            errors.append("policy.completion: acceptance schema differs")
        if completion["checkpoint_filename_suffix"] != ".checkpoint.json":
            errors.append("policy.completion: checkpoint suffix differs")
        if completion["acceptance_filename_suffix"] != ".acceptance.json":
            errors.append("policy.completion: acceptance suffix differs")

    semantic = policy["semantic_integration"]
    if exact_keys(
        semantic,
        {"probe_states", "supported_probes", "minimum_inputs_per_probe"},
        "policy.semantic_integration",
        errors,
    ):
        if semantic["probe_states"] != [
            "active",
            "blocked",
            "candidate_complete",
            "complete",
        ]:
            errors.append("policy.semantic_integration: probe_states differ")
        if semantic["supported_probes"] != ["json_integer_sum_lte"]:
            errors.append("policy.semantic_integration: supported_probes differ")
        minimum = semantic["minimum_inputs_per_probe"]
        if not is_int(minimum) or minimum < 2:
            errors.append(
                "policy.semantic_integration: minimum inputs must be at least 2"
            )

    limitations = validate_unique_string_list(
        policy["platform_and_process_limitations"],
        "policy.platform_and_process_limitations",
        errors,
        allow_empty=False,
    )
    if limitations is not None and len(limitations) < 5:
        errors.append("policy: platform/process limitations are incomplete")
    return len(errors) == start


@dataclass(frozen=True)
class ResolvedProjectPath:
    lexical: str
    canonical: str
    candidate: Path
    resolved: Path


@dataclass(frozen=True)
class WriteClaim:
    path: ResolvedProjectPath
    kind: str


@dataclass(frozen=True)
class SemanticInput:
    path: ResolvedProjectPath
    pointer: str


@dataclass(frozen=True)
class SemanticInvariant:
    invariant_id: str
    probe: str
    inputs: tuple[SemanticInput, ...]
    maximum: int
    definition: dict[str, Any]


@dataclass
class PacketRecord:
    source: Path
    raw: dict[str, Any]
    packet_id: str
    state: str
    writes: list[WriteClaim]
    reads: list[ResolvedProjectPath]
    acceptance_checks: list[dict[str, Any]]
    checkpoint: ResolvedProjectPath | None
    acceptance_receipt: ResolvedProjectPath | None
    invariants: list[SemanticInvariant]
    contract_sha256: str


def normalize_posix_relative(
    raw: Any,
    label: str,
    errors: list[str],
    forbidden_glob_characters: list[str],
) -> str | None:
    if not is_nonempty_string(raw, maximum=1024):
        errors.append(f"{label}: path must be a non-empty trimmed string")
        return None
    assert isinstance(raw, str)
    if "\x00" in raw or "\\" in raw:
        errors.append(f"{label}: path must use POSIX separators and contain no NUL")
        return None
    if raw.startswith("/") or PurePosixPath(raw).is_absolute():
        errors.append(f"{label}: absolute paths are forbidden")
        return None
    components = raw.split("/")
    if raw in {".", "~"} or components[0] == "~":
        errors.append(f"{label}: repository root or home aliases are forbidden")
        return None
    if any(component in {"", ".", ".."} for component in components):
        errors.append(f"{label}: traversal or non-normalized components are forbidden")
        return None
    if any(character in raw for character in forbidden_glob_characters):
        errors.append(f"{label}: unresolved glob syntax is forbidden")
        return None
    normalized = posixpath.normpath(raw)
    if normalized != raw or normalized in {".", ".."} or normalized.startswith("../"):
        errors.append(f"{label}: path is not normalized POSIX relative form")
        return None
    return normalized


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_project_path(
    project_root: Path,
    normalized: str,
    label: str,
    errors: list[str],
    *,
    must_exist: bool,
) -> ResolvedProjectPath | None:
    candidate = project_root.joinpath(*PurePosixPath(normalized).parts)
    if candidate.is_symlink() and not candidate.exists():
        errors.append(f"{label}: broken symlink is forbidden")
        return None
    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, RuntimeError) as exc:
        errors.append(f"{label}: canonical resolution failed: {exc}")
        return None
    if resolved == project_root or not is_within(resolved, project_root):
        errors.append(f"{label}: symlink/canonical path escapes project root")
        return None
    if must_exist and not candidate.exists():
        errors.append(f"{label}: required path does not exist")
        return None
    canonical = resolved.relative_to(project_root).as_posix()
    return ResolvedProjectPath(normalized, canonical, candidate, resolved)


def path_parts(value: str) -> tuple[str, ...]:
    return PurePosixPath(value).parts


def path_relation(left: str, right: str) -> str | None:
    left_parts = path_parts(left)
    right_parts = path_parts(right)
    if left_parts == right_parts:
        return "equal"
    if len(left_parts) < len(right_parts) and right_parts[: len(left_parts)] == left_parts:
        return "left_parent"
    if len(right_parts) < len(left_parts) and left_parts[: len(right_parts)] == right_parts:
        return "right_parent"
    return None


def validate_no_nested_write_symlinks(
    directory: Path,
    label: str,
    errors: list[str],
) -> None:
    def onerror(exc: OSError) -> None:
        errors.append(f"{label}: directory traversal failed: {exc}")

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
            for name in directories + filenames:
                child = current_path / name
                if child.is_symlink():
                    relative = child.relative_to(directory).as_posix()
                    errors.append(
                        f"{label}: nested write symlink is forbidden: {relative}"
                    )
    except OSError as exc:
        errors.append(f"{label}: directory traversal failed: {exc}")


def validate_write_claims(
    value: Any,
    packet_id: str,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> list[WriteClaim] | None:
    path_policy = policy["path_rules"]
    if not isinstance(value, list) or not value:
        errors.append(f"packet {packet_id}: bounded_write_paths must be non-empty")
        return None
    maximum = path_policy["maximum_write_claims_per_packet"]
    if len(value) > maximum:
        errors.append(
            f"packet {packet_id}: bounded_write_paths exceeds maximum {maximum}"
        )
    claims: list[WriteClaim] = []
    for index, item in enumerate(value):
        label = f"packet {packet_id} bounded_write_paths[{index}]"
        if not exact_keys(item, {"path", "kind"}, label, errors):
            continue
        kind = item["kind"]
        if kind not in {"file", "tree"}:
            errors.append(f"{label}: kind must be file or tree")
            continue
        normalized = normalize_posix_relative(
            item["path"],
            f"{label}.path",
            errors,
            path_policy["forbidden_glob_characters"],
        )
        if normalized is None:
            continue
        resolved = resolve_project_path(
            project_root,
            normalized,
            f"{label}.path",
            errors,
            must_exist=False,
        )
        if resolved is None:
            continue
        if kind == "tree":
            minimum = path_policy["minimum_tree_depth"]
            lexical_depth = len(path_parts(resolved.lexical))
            canonical_depth = len(path_parts(resolved.canonical))
            if lexical_depth < minimum or canonical_depth < minimum:
                errors.append(
                    f"{label}: broad tree scope is forbidden; "
                    f"minimum depth is {minimum}"
                )
            if resolved.candidate.exists() and not resolved.resolved.is_dir():
                errors.append(f"{label}: tree claim resolves to a non-directory")
            elif resolved.resolved.is_dir():
                validate_no_nested_write_symlinks(
                    resolved.resolved,
                    label,
                    errors,
                )
        elif resolved.candidate.exists() and not resolved.resolved.is_file():
            errors.append(f"{label}: file claim resolves to a non-file")
        claims.append(WriteClaim(resolved, kind))

    for left_index, left in enumerate(claims):
        for right in claims[left_index + 1 :]:
            relation = path_relation(left.path.canonical, right.path.canonical)
            if relation is not None:
                errors.append(
                    f"packet {packet_id}: duplicate or parent/child write claims "
                    f"are forbidden: {left.path.lexical!r} and {right.path.lexical!r}"
                )
    return claims


def validate_read_dependencies(
    value: Any,
    packet_id: str,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> list[ResolvedProjectPath] | None:
    path_policy = policy["path_rules"]
    raw_paths = validate_unique_string_list(
        value,
        f"packet {packet_id} read_dependencies",
        errors,
        maximum_items=path_policy["maximum_read_dependencies_per_packet"],
    )
    if raw_paths is None:
        return None
    reads: list[ResolvedProjectPath] = []
    canonical_seen: set[str] = set()
    for index, raw in enumerate(raw_paths):
        label = f"packet {packet_id} read_dependencies[{index}]"
        normalized = normalize_posix_relative(
            raw,
            label,
            errors,
            path_policy["forbidden_glob_characters"],
        )
        if normalized is None:
            continue
        resolved = resolve_project_path(
            project_root,
            normalized,
            label,
            errors,
            must_exist=path_policy["read_dependencies_must_exist"],
        )
        if resolved is None:
            continue
        if resolved.canonical in canonical_seen:
            errors.append(f"{label}: duplicate canonical read dependency")
        canonical_seen.add(resolved.canonical)
        reads.append(resolved)
    return reads


def validate_acceptance_checks(
    value: Any,
    packet_id: str,
    errors: list[str],
) -> list[dict[str, Any]] | None:
    if not isinstance(value, list) or not value:
        errors.append(f"packet {packet_id}: acceptance_checks must be non-empty")
        return None
    checks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        label = f"packet {packet_id} acceptance_checks[{index}]"
        if not exact_keys(
            item,
            {"check_id", "kind", "argv", "expected_exit_code"},
            label,
            errors,
        ):
            continue
        check_id = item["check_id"]
        if not isinstance(check_id, str) or CHECK_ID_RE.fullmatch(check_id) is None:
            errors.append(f"{label}: invalid check_id")
        elif check_id in seen:
            errors.append(f"{label}: duplicate check_id")
        else:
            seen.add(check_id)
        if item["kind"] != "process_exit":
            errors.append(f"{label}: only process_exit checks are supported")
        argv = item["argv"]
        if (
            not isinstance(argv, list)
            or not argv
            or len(argv) > 64
            or not all(is_nonempty_string(argument, maximum=1024) for argument in argv)
        ):
            errors.append(f"{label}: argv must be a bounded non-empty string list")
        expected = item["expected_exit_code"]
        if not is_int(expected) or not 0 <= expected <= 255:
            errors.append(f"{label}: expected_exit_code must be in [0, 255]")
        checks.append(item)
    return checks


def decode_json_pointer(pointer: Any, label: str, errors: list[str]) -> list[str] | None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        errors.append(f"{label}: JSON pointer must start with '/'")
        return None
    decoded: list[str] = []
    for raw_token in pointer[1:].split("/"):
        index = 0
        token = ""
        while index < len(raw_token):
            if raw_token[index] != "~":
                token += raw_token[index]
                index += 1
                continue
            if index + 1 >= len(raw_token) or raw_token[index + 1] not in {"0", "1"}:
                errors.append(f"{label}: invalid JSON pointer escape")
                return None
            token += "~" if raw_token[index + 1] == "0" else "/"
            index += 2
        decoded.append(token)
    return decoded


def validate_semantic_invariants(
    value: Any,
    packet_id: str,
    state: str,
    writes: list[WriteClaim],
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> list[SemanticInvariant] | None:
    if not isinstance(value, list):
        errors.append(f"packet {packet_id}: semantic_invariants must be a list")
        return None
    semantic_policy = policy["semantic_integration"]
    path_policy = policy["path_rules"]
    invariants: list[SemanticInvariant] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value):
        label = f"packet {packet_id} semantic_invariants[{index}]"
        if not exact_keys(
            item,
            {"invariant_id", "probe", "inputs", "maximum"},
            label,
            errors,
        ):
            continue
        invariant_id = item["invariant_id"]
        if (
            not isinstance(invariant_id, str)
            or INVARIANT_ID_RE.fullmatch(invariant_id) is None
        ):
            errors.append(f"{label}: invalid invariant_id")
            continue
        if invariant_id in seen_ids:
            errors.append(f"{label}: duplicate invariant_id")
            continue
        seen_ids.add(invariant_id)
        probe = item["probe"]
        if probe not in semantic_policy["supported_probes"]:
            errors.append(f"{label}: unsupported semantic probe")
            continue
        maximum = item["maximum"]
        if not is_int(maximum):
            errors.append(f"{label}: maximum must be an integer")
            continue
        raw_inputs = item["inputs"]
        minimum = semantic_policy["minimum_inputs_per_probe"]
        if not isinstance(raw_inputs, list) or len(raw_inputs) < minimum:
            errors.append(f"{label}: requires at least {minimum} inputs")
            continue
        inputs: list[SemanticInput] = []
        selectors: set[tuple[str, str]] = set()
        for input_index, raw_input in enumerate(raw_inputs):
            input_label = f"{label}.inputs[{input_index}]"
            if not exact_keys(raw_input, {"path", "pointer"}, input_label, errors):
                continue
            normalized = normalize_posix_relative(
                raw_input["path"],
                f"{input_label}.path",
                errors,
                path_policy["forbidden_glob_characters"],
            )
            pointer_tokens = decode_json_pointer(
                raw_input["pointer"],
                f"{input_label}.pointer",
                errors,
            )
            if normalized is None or pointer_tokens is None:
                continue
            resolved = resolve_project_path(
                project_root,
                normalized,
                f"{input_label}.path",
                errors,
                must_exist=state in semantic_policy["probe_states"],
            )
            if resolved is None:
                continue
            selector = (resolved.canonical, raw_input["pointer"])
            if selector in selectors:
                errors.append(f"{input_label}: duplicate canonical selector")
            selectors.add(selector)
            inputs.append(SemanticInput(resolved, raw_input["pointer"]))
        if inputs and not any(
            path_relation(input_item.path.canonical, write.path.canonical) is not None
            for input_item in inputs
            for write in writes
        ):
            errors.append(
                f"{label}: invariant is not bound to any owned write path"
            )
        definition = {
            "invariant_id": invariant_id,
            "probe": probe,
            "inputs": sorted(
                (
                    {"path": input_item.path.canonical, "pointer": input_item.pointer}
                    for input_item in inputs
                ),
                key=lambda entry: (entry["path"], entry["pointer"]),
            ),
            "maximum": maximum,
        }
        invariants.append(
            SemanticInvariant(
                invariant_id,
                probe,
                tuple(inputs),
                maximum,
                definition,
            )
        )
    return invariants


def validate_receipt_reference(
    raw: Any,
    packet_id: str,
    receipt_kind: str,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> ResolvedProjectPath | None:
    if raw is None:
        return None
    completion = policy["completion"]
    path_policy = policy["path_rules"]
    normalized = normalize_posix_relative(
        raw,
        f"packet {packet_id} {receipt_kind}_path",
        errors,
        path_policy["forbidden_glob_characters"],
    )
    if normalized is None:
        return None
    suffix = completion[f"{receipt_kind}_filename_suffix"]
    expected = f"{completion['receipt_directory']}/{packet_id}{suffix}"
    if normalized != expected:
        errors.append(
            f"packet {packet_id}: {receipt_kind}_path must be {expected!r}"
        )
    return resolve_project_path(
        project_root,
        normalized,
        f"packet {packet_id} {receipt_kind}_path",
        errors,
        must_exist=False,
    )


def validate_packet(
    packet: dict[str, Any],
    source: Path,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> PacketRecord | None:
    start = len(errors)
    label = f"packet file {source.name}"
    if not exact_keys(packet, set(PACKET_FIELDS), label, errors):
        return None
    if packet["schema_version"] != policy["packet_schema"]["instance_schema_version"]:
        errors.append(f"{label}: unsupported schema_version")
    packet_id = packet["packet_id"]
    if not isinstance(packet_id, str) or PACKET_ID_RE.fullmatch(packet_id) is None:
        errors.append(f"{label}: invalid packet_id")
        packet_id = source.name
    goal_id = packet["goal_id"]
    if not isinstance(goal_id, str) or GOAL_ID_RE.fullmatch(goal_id) is None:
        errors.append(f"packet {packet_id}: invalid goal_id")
    state = packet["state"]
    if state not in policy["packet_schema"]["state_values"]:
        errors.append(f"packet {packet_id}: invalid state")
        state = "invalid"
    for field in ("owner", "reviewer"):
        value = packet[field]
        if not isinstance(value, str) or TOKEN_RE.fullmatch(value) is None:
            errors.append(f"packet {packet_id}: invalid {field}")
    if packet["owner"] == packet["reviewer"]:
        errors.append(f"packet {packet_id}: owner and reviewer must differ")
    retry_budget = packet["retry_budget"]
    if not is_int(retry_budget) or not 0 <= retry_budget <= 100:
        errors.append(f"packet {packet_id}: retry_budget must be in [0, 100]")
    validate_unique_string_list(
        packet["external_side_effects"],
        f"packet {packet_id} external_side_effects",
        errors,
        maximum_items=32,
    )

    writes = validate_write_claims(
        packet["bounded_write_paths"],
        packet_id,
        project_root,
        policy,
        errors,
    )
    reads = validate_read_dependencies(
        packet["read_dependencies"],
        packet_id,
        project_root,
        policy,
        errors,
    )
    checks = validate_acceptance_checks(
        packet["acceptance_checks"],
        packet_id,
        errors,
    )
    checkpoint = validate_receipt_reference(
        packet["checkpoint_path"],
        packet_id,
        "checkpoint",
        project_root,
        policy,
        errors,
    )
    acceptance = validate_receipt_reference(
        packet["acceptance_receipt_path"],
        packet_id,
        "acceptance",
        project_root,
        policy,
        errors,
    )
    if writes is None:
        writes = []
    invariants = validate_semantic_invariants(
        packet["semantic_invariants"],
        packet_id,
        state,
        writes,
        project_root,
        policy,
        errors,
    )
    if len(errors) != start:
        return None
    assert reads is not None
    assert checks is not None
    assert invariants is not None
    return PacketRecord(
        source=source,
        raw=packet,
        packet_id=packet_id,
        state=state,
        writes=writes,
        reads=reads,
        acceptance_checks=checks,
        checkpoint=checkpoint,
        acceptance_receipt=acceptance,
        invariants=invariants,
        contract_sha256=packet_contract_sha256(packet),
    )


def tree_content_sha256(directory: Path, label: str, errors: list[str]) -> str | None:
    records: list[dict[str, str]] = []

    def onerror(exc: OSError) -> None:
        errors.append(f"{label}: snapshot traversal failed: {exc}")

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
                    errors.append(
                        f"{label}: nested write symlink is forbidden: {relative}"
                    )
                else:
                    records.append({"path": relative, "type": "directory"})
            for name in filenames:
                child = current_path / name
                relative = child.relative_to(directory).as_posix()
                if child.is_symlink():
                    errors.append(
                        f"{label}: nested write symlink is forbidden: {relative}"
                    )
                elif child.is_file():
                    records.append(
                        {
                            "path": relative,
                            "type": "file",
                            "sha256": hashlib.sha256(child.read_bytes()).hexdigest(),
                        }
                    )
                else:
                    errors.append(
                        f"{label}: unsupported special filesystem entry: {relative}"
                    )
    except OSError as exc:
        errors.append(f"{label}: snapshot traversal failed: {exc}")
        return None
    return canonical_sha256(records)


def snapshot_write_claim(
    project_root: Path,
    claim: WriteClaim,
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    current = resolve_project_path(
        project_root,
        claim.path.lexical,
        label,
        errors,
        must_exist=False,
    )
    if current is None:
        return None
    if current.canonical != claim.path.canonical:
        errors.append(f"{label}: canonical target changed since packet validation")
        return None
    if not current.candidate.exists():
        return {
            "path": claim.path.lexical,
            "kind": claim.kind,
            "state": "absent",
            "content_sha256": None,
        }
    if claim.kind == "file":
        if not current.resolved.is_file():
            errors.append(f"{label}: file claim no longer resolves to a file")
            return None
        try:
            digest = hashlib.sha256(current.candidate.read_bytes()).hexdigest()
        except OSError as exc:
            errors.append(f"{label}: file snapshot failed: {exc}")
            return None
        return {
            "path": claim.path.lexical,
            "kind": claim.kind,
            "state": "file",
            "content_sha256": digest,
        }
    if not current.resolved.is_dir():
        errors.append(f"{label}: tree claim no longer resolves to a directory")
        return None
    digest = tree_content_sha256(current.resolved, label, errors)
    if digest is None:
        return None
    return {
        "path": claim.path.lexical,
        "kind": claim.kind,
        "state": "tree",
        "content_sha256": digest,
    }


def verify_checkpoint_receipt(
    record: PacketRecord,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if record.checkpoint is None:
        return None
    label = f"packet {record.packet_id} checkpoint receipt"
    start = len(errors)
    receipt = load_json_object(record.checkpoint.candidate, errors, label)
    if receipt is None:
        return None
    expected_fields = {
        "schema_version",
        "packet_id",
        "packet_contract_sha256",
        "sequence",
        "snapshots",
    }
    if not exact_keys(receipt, expected_fields, label, errors):
        return None
    completion = policy["completion"]
    if receipt["schema_version"] != completion["checkpoint_schema_version"]:
        errors.append(f"{label}: schema_version differs")
    if receipt["packet_id"] != record.packet_id:
        errors.append(f"{label}: packet_id differs")
    if receipt["packet_contract_sha256"] != record.contract_sha256:
        errors.append(f"{label}: packet contract digest differs")
    if not is_int(receipt["sequence"]) or receipt["sequence"] < 1:
        errors.append(f"{label}: sequence must be a positive integer")
    expected_snapshots: list[dict[str, Any]] = []
    for index, claim in enumerate(record.writes):
        snapshot = snapshot_write_claim(
            project_root,
            claim,
            f"{label} snapshots[{index}]",
            errors,
        )
        if snapshot is not None:
            expected_snapshots.append(snapshot)
    if receipt["snapshots"] != expected_snapshots:
        errors.append(f"{label}: snapshots differ from current owned write set")
    if len(errors) != start:
        return None
    return receipt


def verify_acceptance_receipt(
    record: PacketRecord,
    checkpoint: dict[str, Any] | None,
    policy: dict[str, Any],
    errors: list[str],
) -> bool:
    if record.acceptance_receipt is None:
        return False
    label = f"packet {record.packet_id} acceptance receipt"
    start = len(errors)
    receipt = load_json_object(record.acceptance_receipt.candidate, errors, label)
    if receipt is None:
        return False
    expected_fields = {
        "schema_version",
        "packet_id",
        "packet_contract_sha256",
        "checkpoint_receipt_sha256",
        "checks",
    }
    if not exact_keys(receipt, expected_fields, label, errors):
        return False
    completion = policy["completion"]
    if receipt["schema_version"] != completion["acceptance_schema_version"]:
        errors.append(f"{label}: schema_version differs")
    if receipt["packet_id"] != record.packet_id:
        errors.append(f"{label}: packet_id differs")
    if receipt["packet_contract_sha256"] != record.contract_sha256:
        errors.append(f"{label}: packet contract digest differs")
    if checkpoint is None:
        errors.append(f"{label}: valid checkpoint receipt is required first")
    elif receipt["checkpoint_receipt_sha256"] != canonical_sha256(checkpoint):
        errors.append(f"{label}: checkpoint receipt digest differs")

    raw_checks = receipt["checks"]
    if not isinstance(raw_checks, list):
        errors.append(f"{label}: checks must be a list")
    elif len(raw_checks) != len(record.acceptance_checks):
        errors.append(f"{label}: check count differs")
    else:
        for index, (actual, declared) in enumerate(
            zip(raw_checks, record.acceptance_checks, strict=True)
        ):
            check_label = f"{label} checks[{index}]"
            if not exact_keys(
                actual,
                {"check_id", "actual_exit_code"},
                check_label,
                errors,
            ):
                continue
            if actual["check_id"] != declared["check_id"]:
                errors.append(f"{check_label}: check_id differs")
            exit_code = actual["actual_exit_code"]
            if not is_int(exit_code) or not 0 <= exit_code <= 255:
                errors.append(f"{check_label}: invalid actual_exit_code")
            elif exit_code != declared["expected_exit_code"]:
                errors.append(
                    f"{check_label}: actual exit {exit_code} does not equal "
                    f"expected {declared['expected_exit_code']}"
                )
    return len(errors) == start


def extract_pointer(
    document: Any,
    pointer: str,
    label: str,
    errors: list[str],
) -> Any:
    tokens = decode_json_pointer(pointer, label, errors)
    if tokens is None:
        return INVALID
    current = document
    for token in tokens:
        if isinstance(current, dict):
            if token not in current:
                errors.append(f"{label}: object key {token!r} is missing")
                return INVALID
            current = current[token]
        elif isinstance(current, list):
            if re.fullmatch(r"0|[1-9][0-9]*", token) is None:
                errors.append(f"{label}: invalid array index {token!r}")
                return INVALID
            index = int(token)
            if index >= len(current):
                errors.append(f"{label}: array index {index} is out of range")
                return INVALID
            current = current[index]
        else:
            errors.append(f"{label}: pointer traverses a scalar value")
            return INVALID
    return current


def run_semantic_probes(
    records: list[PacketRecord],
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> int:
    probe_states = set(policy["semantic_integration"]["probe_states"])
    declarations: dict[str, SemanticInvariant] = {}
    for record in records:
        if record.state not in probe_states:
            continue
        for invariant in record.invariants:
            existing = declarations.get(invariant.invariant_id)
            if existing is None:
                declarations[invariant.invariant_id] = invariant
            elif existing.definition != invariant.definition:
                errors.append(
                    f"semantic invariant {invariant.invariant_id}: "
                    "active declarations differ"
                )

    for invariant_id in sorted(declarations):
        invariant = declarations[invariant_id]
        values: list[int] = []
        for index, input_item in enumerate(invariant.inputs):
            label = f"semantic invariant {invariant_id} input[{index}]"
            current = resolve_project_path(
                project_root,
                input_item.path.lexical,
                label,
                errors,
                must_exist=True,
            )
            if current is None:
                continue
            if current.canonical != input_item.path.canonical:
                errors.append(f"{label}: canonical target changed during verification")
                continue
            if not current.resolved.is_file():
                errors.append(f"{label}: semantic input must resolve to a file")
                continue
            document = load_json_value(current.candidate, errors, label)
            if document is INVALID:
                continue
            value = extract_pointer(
                document,
                input_item.pointer,
                f"{label} pointer {input_item.pointer}",
                errors,
            )
            if value is INVALID:
                continue
            if not is_int(value):
                errors.append(f"{label}: selected value must be an integer")
                continue
            values.append(value)
        if len(values) == len(invariant.inputs):
            total = sum(values)
            if total > invariant.maximum:
                errors.append(
                    f"semantic invariant {invariant_id} failed: "
                    f"sum {total} exceeds maximum {invariant.maximum}"
                )
    return len(declarations)


def discover_packet_files(
    packet_directory: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> list[Path]:
    suffix = policy["packet_discovery"]["filename_suffix"]
    try:
        entries = sorted(packet_directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        errors.append(f"packet directory: cannot enumerate: {exc}")
        return []
    packet_files: list[Path] = []
    for entry in entries:
        if entry.is_symlink():
            errors.append(f"packet directory: symlink entry is forbidden: {entry.name}")
        elif entry.is_file() and entry.name.endswith(suffix):
            packet_files.append(entry)
        else:
            errors.append(f"packet directory: unexpected entry: {entry.name}")
    if not packet_files:
        errors.append("packet directory: at least one packet instance is required")
    return packet_files


def verify(
    project_root_argument: Path,
    policy_argument: Path,
    packet_directory_argument: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    try:
        project_root = project_root_argument.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        return {
            "status": "fail",
            "policy_id": None,
            "packet_count": 0,
            "active_packet_count": 0,
            "ownership_claim_count": 0,
            "ownership_conflict_count": 0,
            "semantic_probe_count": 0,
            "completion_verified_count": 0,
            "errors": [f"project root: cannot resolve: {exc}"],
            "platform_and_process_limitations": [],
        }
    if not project_root.is_dir():
        errors.append("project root: must be a directory")

    policy_path = (
        policy_argument
        if policy_argument.is_absolute()
        else project_root / policy_argument
    )
    packet_directory = (
        packet_directory_argument
        if packet_directory_argument.is_absolute()
        else project_root / packet_directory_argument
    )
    try:
        policy_path = policy_path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"policy: cannot resolve: {exc}")
    try:
        packet_directory = packet_directory.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        errors.append(f"packet directory: cannot resolve: {exc}")

    if errors:
        return {
            "status": "fail",
            "policy_id": None,
            "packet_count": 0,
            "active_packet_count": 0,
            "ownership_claim_count": 0,
            "ownership_conflict_count": 0,
            "semantic_probe_count": 0,
            "completion_verified_count": 0,
            "errors": sorted(set(errors)),
            "platform_and_process_limitations": [],
        }
    assert isinstance(policy_path, Path)
    assert isinstance(packet_directory, Path)
    if not is_within(policy_path, project_root):
        errors.append("policy: canonical path escapes project root")
    if not is_within(packet_directory, project_root):
        errors.append("packet directory: canonical path escapes project root")
    if not policy_path.is_file():
        errors.append("policy: must resolve to a file")
    if not packet_directory.is_dir():
        errors.append("packet directory: must resolve to a directory")

    policy = load_json_object(policy_path, errors, "policy")
    limitations: list[str] = []
    if policy is not None:
        raw_limitations = policy.get("platform_and_process_limitations")
        if isinstance(raw_limitations, list) and all(
            isinstance(item, str) for item in raw_limitations
        ):
            limitations = raw_limitations
    if policy is None or not validate_policy(policy, errors):
        return {
            "status": "fail",
            "policy_id": policy.get("policy_id") if policy else None,
            "packet_count": 0,
            "active_packet_count": 0,
            "ownership_claim_count": 0,
            "ownership_conflict_count": 0,
            "semantic_probe_count": 0,
            "completion_verified_count": 0,
            "errors": sorted(set(errors)),
            "platform_and_process_limitations": limitations,
        }

    packet_files = discover_packet_files(packet_directory, policy, errors)
    records: list[PacketRecord] = []
    seen_packet_ids: dict[str, str] = {}
    for packet_file in packet_files:
        packet = load_json_object(packet_file, errors, f"packet file {packet_file.name}")
        if packet is None:
            continue
        record = validate_packet(packet, packet_file, project_root, policy, errors)
        if record is None:
            continue
        prior = seen_packet_ids.get(record.packet_id)
        if prior is not None:
            errors.append(
                f"duplicate packet_id {record.packet_id!r}: {prior} and "
                f"{packet_file.name}"
            )
        else:
            seen_packet_ids[record.packet_id] = packet_file.name
        records.append(record)

    ownership_states = set(policy["ownership"]["ownership_states"])
    active_records = [record for record in records if record.state in ownership_states]
    all_claims = [
        (record, claim)
        for record in records
        for claim in record.writes
    ]
    active_claims = [
        (record, claim)
        for record in active_records
        for claim in record.writes
    ]
    ownership_conflicts = 0
    for left_index, (left_record, left_claim) in enumerate(active_claims):
        for right_record, right_claim in active_claims[left_index + 1 :]:
            relation = path_relation(
                left_claim.path.canonical,
                right_claim.path.canonical,
            )
            if relation is None:
                continue
            ownership_conflicts += 1
            conflict_kind = (
                "duplicate ownership" if relation == "equal" else "parent/child overlap"
            )
            errors.append(
                f"active packets {left_record.packet_id} and "
                f"{right_record.packet_id}: {conflict_kind} between "
                f"{left_claim.path.lexical!r} and {right_claim.path.lexical!r}"
            )

    receipt_paths: list[tuple[PacketRecord, str, ResolvedProjectPath]] = []
    for record in records:
        if record.checkpoint is not None:
            receipt_paths.append((record, "checkpoint", record.checkpoint))
        if record.acceptance_receipt is not None:
            receipt_paths.append((record, "acceptance", record.acceptance_receipt))
    for left_index, (left_record, left_kind, left_path) in enumerate(receipt_paths):
        for right_record, right_kind, right_path in receipt_paths[left_index + 1 :]:
            if path_relation(left_path.canonical, right_path.canonical) is not None:
                errors.append(
                    f"receipt path collision: {left_record.packet_id} {left_kind} "
                    f"and {right_record.packet_id} {right_kind}"
                )
        for owner_record, claim in all_claims:
            if path_relation(left_path.canonical, claim.path.canonical) is not None:
                errors.append(
                    f"packet {left_record.packet_id} {left_kind} receipt overlaps "
                    f"declared write set of {owner_record.packet_id}"
                )

    semantic_probe_count = run_semantic_probes(
        records,
        project_root,
        policy,
        errors,
    )

    completion_verified_count = 0
    completion_policy = policy["completion"]
    for record in records:
        checkpoint_required = (
            record.state in completion_policy["checkpoint_required_states"]
        )
        acceptance_required = (
            record.state in completion_policy["acceptance_required_states"]
        )
        if checkpoint_required and record.checkpoint is None:
            errors.append(
                f"packet {record.packet_id}: checkpoint receipt is required "
                f"before state {record.state}"
            )
        if acceptance_required and record.acceptance_receipt is None:
            errors.append(
                f"packet {record.packet_id}: acceptance receipt is required "
                f"before state {record.state}"
            )
        checkpoint_receipt = None
        if record.checkpoint is not None:
            checkpoint_receipt = verify_checkpoint_receipt(
                record,
                project_root,
                policy,
                errors,
            )
        acceptance_valid = False
        if record.acceptance_receipt is not None:
            acceptance_valid = verify_acceptance_receipt(
                record,
                checkpoint_receipt,
                policy,
                errors,
            )
        if (
            record.state == "complete"
            and checkpoint_receipt is not None
            and acceptance_valid
        ):
            completion_verified_count += 1

    unique_errors = sorted(set(errors))
    return {
        "status": "pass" if not unique_errors else "fail",
        "policy_id": policy["policy_id"],
        "packet_count": len(packet_files),
        "active_packet_count": len(active_records),
        "ownership_claim_count": len(active_claims),
        "ownership_conflict_count": ownership_conflicts,
        "semantic_probe_count": semantic_probe_count,
        "completion_verified_count": completion_verified_count,
        "errors": unique_errors,
        "platform_and_process_limitations": limitations,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=SCRIPT_PROJECT_ROOT,
        help="Project root containing all packet-controlled paths.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_RELATIVE,
        help="Policy JSON path, relative to project root unless absolute.",
    )
    parser.add_argument(
        "--packet-dir",
        type=Path,
        required=True,
        help="Dedicated packet-instance directory inside the project root.",
    )
    parser.add_argument("--json", action="store_true", help="Emit one JSON result.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = verify(args.project_root, args.policy, args.packet_dir)
    except Exception as exc:  # pragma: no cover - final fail-closed boundary
        result = {
            "status": "fail",
            "policy_id": None,
            "packet_count": 0,
            "active_packet_count": 0,
            "ownership_claim_count": 0,
            "ownership_conflict_count": 0,
            "semantic_probe_count": 0,
            "completion_verified_count": 0,
            "errors": [
                f"internal verifier error: {type(exc).__name__}: {exc}"
            ],
            "platform_and_process_limitations": [],
        }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    elif result["status"] == "pass":
        print(
            "work-packet verification: PASS "
            f"({result['packet_count']} packets, "
            f"{result['semantic_probe_count']} semantic probes)"
        )
        for limitation in result["platform_and_process_limitations"]:
            print(f"LIMITATION: {limitation}")
    else:
        print("work-packet verification: FAIL")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
