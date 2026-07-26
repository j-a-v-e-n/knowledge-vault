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

V1_POLICY_FIELDS = {
    "schema_version",
    "policy_id",
    "linked_failure_ids",
    "packet_discovery",
    "packet_schema",
    "path_rules",
    "ownership",
    "completion",
    "supersession",
    "semantic_integration",
    "platform_and_process_limitations",
}
V2_POLICY_FIELDS = V1_POLICY_FIELDS | {
    "dag",
    "activation",
    "parallel_conflicts",
    "integration_probes",
    "checkpoint_prerequisites",
    "routing",
}
V1_PACKET_FIELDS = (
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
V2_PACKET_FIELDS = V1_PACKET_FIELDS + (
    "depends_on",
    "activates",
    "integration_invariants",
    "routing",
)
V1_PACKET_CONTRACT_FIELDS = (
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
V2_PACKET_CONTRACT_FIELDS = V1_PACKET_CONTRACT_FIELDS + (
    "depends_on",
    "activates",
    "integration_invariants",
    "routing",
)
STATE_VALUES = (
    "pending",
    "active",
    "blocked",
    "candidate_complete",
    "complete",
    "superseded",
)
SUPERSESSION_FIELD = "superseded_by"
TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@-]{0,127}$")
PACKET_ID_RE = re.compile(r"^WP-[A-Z0-9][A-Z0-9._-]{0,63}$")
GOAL_ID_RE = re.compile(r"^[A-Z][A-Z0-9._-]{1,63}$")
CHECK_ID_RE = re.compile(r"^CHECK-[A-Z0-9][A-Z0-9._-]{0,63}$")
INVARIANT_ID_RE = re.compile(r"^INV-[A-Z0-9][A-Z0-9._-]{0,63}$")
ACTION_ID_RE = re.compile(r"^ACT-[A-Z0-9][A-Z0-9._-]{0,63}$")
FINDING_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._-]{1,127}$")
PHASE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
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
    fields = (
        V2_PACKET_CONTRACT_FIELDS
        if packet.get("schema_version") == "work-packet-instance/v2"
        else V1_PACKET_CONTRACT_FIELDS
    )
    return canonical_sha256({field: packet[field] for field in fields})


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


def validate_v1_policy(policy: dict[str, Any], errors: list[str]) -> bool:
    start = len(errors)
    if not exact_keys(policy, V1_POLICY_FIELDS, "policy", errors):
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
        if schema["required_fields"] != list(V1_PACKET_FIELDS):
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
            "superseded",
        ]:
            errors.append("policy.completion: checkpoint_required_states differ")
        if completion["acceptance_required_states"] != [
            "complete",
            "superseded",
        ]:
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

    supersession = policy["supersession"]
    expected_supersession = {
        "state": "superseded",
        "successor_field": SUPERSESSION_FIELD,
        "successor_allowed_states": [
            "active",
            "blocked",
            "candidate_complete",
            "complete",
        ],
        "successor_must_exist": True,
        "successor_must_share_goal": True,
        "successor_must_reclaim_exact_write_set": True,
        "historical_receipts_remain_required": True,
        "historical_snapshot_rule": (
            "validate_receipt_schema_and_original_claim_identity_without_"
            "comparing_later_file_bytes"
        ),
    }
    if supersession != expected_supersession:
        errors.append("policy.supersession differs")

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


def validate_v2_policy(policy: dict[str, Any], errors: list[str]) -> bool:
    start = len(errors)
    if not exact_keys(policy, V2_POLICY_FIELDS, "policy", errors):
        return False
    if policy["schema_version"] != "work-packet-policy/v2":
        errors.append("policy: unsupported schema_version")
    if policy["policy_id"] != "ORG-01-ORG-03-WORK-PACKET-V2":
        errors.append("policy: unexpected policy_id")

    schema = policy["packet_schema"]
    if exact_keys(
        schema,
        {
            "instance_schema_version",
            "historical_superseded_instance_schema_versions",
            "required_fields",
            "state_values",
        },
        "policy.packet_schema",
        errors,
    ):
        if schema["instance_schema_version"] != "work-packet-instance/v2":
            errors.append("policy.packet_schema: unsupported instance schema")
        if schema["historical_superseded_instance_schema_versions"] != [
            "work-packet-instance/v1"
        ]:
            errors.append(
                "policy.packet_schema: historical instance schemas differ"
            )
        if schema["required_fields"] != list(V2_PACKET_FIELDS):
            errors.append("policy.packet_schema: required_fields differ")
        if schema["state_values"] != list(STATE_VALUES):
            errors.append("policy.packet_schema: state_values differ")

    path_policy = policy["path_rules"]
    if exact_keys(
        path_policy,
        {
            "format",
            "forbidden_glob_characters",
            "minimum_tree_depth",
            "maximum_write_claims_per_packet",
            "maximum_read_dependencies_per_packet",
            "read_dependencies_must_exist",
            "read_dependencies_must_be_files",
            "nested_write_symlinks_allowed",
        },
        "policy.path_rules",
        errors,
    ) and path_policy["read_dependencies_must_be_files"] is not True:
        errors.append("policy.path_rules: read dependencies must be files")

    completion = policy["completion"]
    if exact_keys(
        completion,
        {
            "checkpoint_required_states",
            "acceptance_required_states",
            "receipt_directory",
            "checkpoint_schema_version",
            "acceptance_schema_version",
            "historical_checkpoint_schema_version",
            "historical_acceptance_schema_version",
            "checkpoint_filename_suffix",
            "acceptance_filename_suffix",
        },
        "policy.completion",
        errors,
    ):
        if completion["checkpoint_schema_version"] != "work-packet-checkpoint/v2":
            errors.append("policy.completion: checkpoint schema differs")
        if completion["acceptance_schema_version"] != "work-packet-acceptance/v2":
            errors.append("policy.completion: acceptance schema differs")
        if (
            completion["historical_checkpoint_schema_version"]
            != "work-packet-checkpoint/v1"
        ):
            errors.append("policy.completion: historical checkpoint schema differs")
        if (
            completion["historical_acceptance_schema_version"]
            != "work-packet-acceptance/v1"
        ):
            errors.append("policy.completion: historical acceptance schema differs")

    expected_dag = {
        "live_states": [
            "pending",
            "active",
            "blocked",
            "candidate_complete",
            "complete",
        ],
        "dependency_field": "depends_on",
        "activation_field": "activates",
        "require_exact_bidirectional_edges": True,
        "require_acyclic": True,
        "unique_root_per_goal": True,
        "unique_sink_per_goal": True,
        "require_root_to_sink_coverage": True,
    }
    if policy["dag"] != expected_dag:
        errors.append("policy.dag differs")
    expected_activation = {
        "verified_complete_state": "complete",
        "unverified_prerequisite_allowed_state": "pending",
        "stale_pending_error": "stale_pending_activation",
        "blocked_propagation": "strict_descendants_only",
    }
    if policy["activation"] != expected_activation:
        errors.append("policy.activation differs")
    expected_parallel = {
        "scope": "all_live_incomparable_packets",
        "path_relation": "canonical_equal_or_ancestor",
        "reject_write_write": True,
        "reject_read_write": True,
        "reject_identical_external_side_effects": True,
    }
    if policy["parallel_conflicts"] != expected_parallel:
        errors.append("policy.parallel_conflicts differs")
    expected_integration = {
        "join_minimum_dependencies": 2,
        "minimum_inputs_per_invariant": 1,
        "multi_node_goal_minimum_probe_declarations": 1,
        "probe_receipt_required_states": ["candidate_complete", "complete"],
        "input_packet_must_be_direct_dependency": True,
        "input_path_must_be_owned_by_input_packet": True,
        "input_path_must_be_join_read_dependency": True,
        "probe_check_must_belong_to_join": True,
    }
    if policy["integration_probes"] != expected_integration:
        errors.append("policy.integration_probes differs")
    expected_prerequisites = {
        "field": "prerequisite_receipts",
        "binding": (
            "exact_direct_dependency_contract_checkpoint_and_acceptance_sha256"
        ),
        "required_for_v2_checkpoints": True,
    }
    if policy["checkpoint_prerequisites"] != expected_prerequisites:
        errors.append("policy.checkpoint_prerequisites differs")
    expected_routing = {
        "required_fields": [
            "phase_id",
            "action_id",
            "route_order",
            "addresses_finding_ids",
            "summary",
        ],
        "phase_id_rule": "lowercase_identifier",
        "action_id_rule": "globally_unique_ACT_identifier",
        "route_order_rule": "globally_unique_positive_integer",
        "addresses_finding_ids_rule": "unique_identifiers_may_be_empty",
        "claim_boundary": (
            "routing orders work and binds optional finding addresses; it does "
            "not prove that a route resolves a finding"
        ),
    }
    if policy["routing"] != expected_routing:
        errors.append("policy.routing differs")

    v1_projection = {field: policy[field] for field in V1_POLICY_FIELDS}
    v1_projection["schema_version"] = "work-packet-policy/v1"
    v1_projection["policy_id"] = "ORG-01-ORG-03-WORK-PACKET-V1"
    v1_projection["packet_schema"] = {
        "instance_schema_version": "work-packet-instance/v1",
        "required_fields": list(V1_PACKET_FIELDS),
        "state_values": list(STATE_VALUES),
    }
    v1_projection["path_rules"] = {
        key: value
        for key, value in (
            path_policy.items() if isinstance(path_policy, dict) else ()
        )
        if key != "read_dependencies_must_be_files"
    }
    v1_projection["completion"] = {
        key: value
        for key, value in (
            completion.items() if isinstance(completion, dict) else ()
        )
        if key
        not in {
            "historical_checkpoint_schema_version",
            "historical_acceptance_schema_version",
        }
    }
    if isinstance(completion, dict):
        v1_projection["completion"]["checkpoint_schema_version"] = (
            "work-packet-checkpoint/v1"
        )
        v1_projection["completion"]["acceptance_schema_version"] = (
            "work-packet-acceptance/v1"
        )
    validate_v1_policy(v1_projection, errors)
    return len(errors) == start


def validate_policy(policy: dict[str, Any], errors: list[str]) -> bool:
    schema_version = policy.get("schema_version")
    if schema_version == "work-packet-policy/v1":
        return validate_v1_policy(policy, errors)
    if schema_version == "work-packet-policy/v2":
        return validate_v2_policy(policy, errors)
    errors.append("policy: unsupported schema_version")
    return False


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


@dataclass(frozen=True)
class IntegrationInput:
    packet_id: str
    path: ResolvedProjectPath


@dataclass(frozen=True)
class IntegrationInvariant:
    invariant_id: str
    inputs: tuple[IntegrationInput, ...]
    probe_check_ids: tuple[str, ...]


@dataclass
class PacketRecord:
    source: Path
    raw: dict[str, Any]
    schema_version: str
    packet_id: str
    goal_id: str
    state: str
    superseded_by: str | None
    writes: list[WriteClaim]
    reads: list[ResolvedProjectPath]
    acceptance_checks: list[dict[str, Any]]
    checkpoint: ResolvedProjectPath | None
    acceptance_receipt: ResolvedProjectPath | None
    invariants: list[SemanticInvariant]
    depends_on: list[str]
    activates: list[str]
    integration_invariants: list[IntegrationInvariant]
    routing: dict[str, Any] | None
    external_side_effects: list[str]
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
        if (
            path_policy.get("read_dependencies_must_be_files") is True
            and not resolved.resolved.is_file()
        ):
            errors.append(f"{label}: read dependency must resolve to a file")
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


def validate_packet_id_list(
    value: Any,
    packet_id: str,
    field: str,
    errors: list[str],
) -> list[str] | None:
    packet_ids = validate_unique_string_list(
        value,
        f"packet {packet_id} {field}",
        errors,
        maximum_items=1024,
    )
    if packet_ids is None:
        return None
    for index, item in enumerate(packet_ids):
        if PACKET_ID_RE.fullmatch(item) is None:
            errors.append(f"packet {packet_id} {field}[{index}]: invalid packet_id")
    return packet_ids


def validate_integration_invariants(
    value: Any,
    packet_id: str,
    acceptance_checks: list[dict[str, Any]],
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> list[IntegrationInvariant] | None:
    if not isinstance(value, list):
        errors.append(f"packet {packet_id}: integration_invariants must be a list")
        return None
    path_policy = policy["path_rules"]
    integration_policy = policy["integration_probes"]
    declared_checks = {
        check["check_id"]: check
        for check in acceptance_checks
        if isinstance(check.get("check_id"), str)
    }
    invariants: list[IntegrationInvariant] = []
    invariant_ids: set[str] = set()
    bound_probe_ids: set[str] = set()
    for index, item in enumerate(value):
        label = f"packet {packet_id} integration_invariants[{index}]"
        if not exact_keys(
            item,
            {"invariant_id", "inputs", "probe_check_ids"},
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
        if invariant_id in invariant_ids:
            errors.append(f"{label}: duplicate invariant_id")
            continue
        invariant_ids.add(invariant_id)

        raw_inputs = item["inputs"]
        minimum = integration_policy["minimum_inputs_per_invariant"]
        if not isinstance(raw_inputs, list) or len(raw_inputs) < minimum:
            errors.append(f"{label}: requires at least {minimum} inputs")
            continue
        inputs: list[IntegrationInput] = []
        input_selectors: set[tuple[str, str]] = set()
        for input_index, raw_input in enumerate(raw_inputs):
            input_label = f"{label}.inputs[{input_index}]"
            if not exact_keys(raw_input, {"packet_id", "path"}, input_label, errors):
                continue
            input_packet_id = raw_input["packet_id"]
            if (
                not isinstance(input_packet_id, str)
                or PACKET_ID_RE.fullmatch(input_packet_id) is None
            ):
                errors.append(f"{input_label}: invalid packet_id")
                continue
            normalized = normalize_posix_relative(
                raw_input["path"],
                f"{input_label}.path",
                errors,
                path_policy["forbidden_glob_characters"],
            )
            if normalized is None:
                continue
            resolved = resolve_project_path(
                project_root,
                normalized,
                f"{input_label}.path",
                errors,
                must_exist=True,
            )
            if resolved is None:
                continue
            if not resolved.resolved.is_file():
                errors.append(f"{input_label}.path: integration input must be a file")
                continue
            selector = (input_packet_id, resolved.canonical)
            if selector in input_selectors:
                errors.append(f"{input_label}: duplicate integration input")
            input_selectors.add(selector)
            inputs.append(IntegrationInput(input_packet_id, resolved))

        probe_ids = validate_unique_string_list(
            item["probe_check_ids"],
            f"{label}.probe_check_ids",
            errors,
            allow_empty=False,
        )
        if probe_ids is None:
            continue
        for probe_index, probe_id in enumerate(probe_ids):
            probe_label = f"{label}.probe_check_ids[{probe_index}]"
            if CHECK_ID_RE.fullmatch(probe_id) is None:
                errors.append(f"{probe_label}: invalid check_id")
            declared_check = declared_checks.get(probe_id)
            if declared_check is None:
                errors.append(
                    f"{probe_label}: probe check_id is not declared by join packet"
                )
            elif declared_check.get("expected_exit_code") != 0:
                errors.append(
                    f"{probe_label}: integration probe check must expect exit 0"
                )
            if probe_id in bound_probe_ids:
                errors.append(
                    f"{probe_label}: probe check_id is bound more than once"
                )
            bound_probe_ids.add(probe_id)
        invariants.append(
            IntegrationInvariant(
                invariant_id,
                tuple(inputs),
                tuple(probe_ids),
            )
        )
    return invariants


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
    if not isinstance(packet, dict):
        errors.append(f"{label}: must be an object")
        return None
    policy_is_v2 = policy["schema_version"] == "work-packet-policy/v2"
    schema_version = packet.get("schema_version")
    state_value = packet.get("state")
    if policy_is_v2 and schema_version == "work-packet-instance/v2":
        required_fields = set(V2_PACKET_FIELDS)
    elif policy_is_v2 and schema_version == "work-packet-instance/v1":
        required_fields = set(V1_PACKET_FIELDS)
        if state_value != "superseded":
            errors.append(
                f"{label}: live V1 packet is forbidden under V2 policy"
            )
    else:
        required_fields = set(V1_PACKET_FIELDS)
    allowed_fields = required_fields | {SUPERSESSION_FIELD}
    actual_fields = set(packet)
    if (
        not required_fields.issubset(actual_fields)
        or not actual_fields.issubset(allowed_fields)
    ):
        errors.append(
            f"{label}: fields differ; "
            f"missing={sorted(required_fields - actual_fields)}, "
            f"extra={sorted(actual_fields - allowed_fields)}"
        )
        return None
    if policy_is_v2:
        supported_schema = schema_version in {
            "work-packet-instance/v1",
            "work-packet-instance/v2",
        }
    else:
        supported_schema = (
            schema_version
            == policy["packet_schema"]["instance_schema_version"]
        )
    if not supported_schema:
        errors.append(f"{label}: unsupported schema_version")
    packet_id = packet["packet_id"]
    if not isinstance(packet_id, str) or PACKET_ID_RE.fullmatch(packet_id) is None:
        errors.append(f"{label}: invalid packet_id")
        packet_id = source.name
    goal_id = packet["goal_id"]
    if not isinstance(goal_id, str) or GOAL_ID_RE.fullmatch(goal_id) is None:
        errors.append(f"packet {packet_id}: invalid goal_id")
        goal_id = f"INVALID-{packet_id}"
    state = packet["state"]
    if state not in policy["packet_schema"]["state_values"]:
        errors.append(f"packet {packet_id}: invalid state")
        state = "invalid"
    superseded_by = packet.get(SUPERSESSION_FIELD)
    if state == "superseded":
        if (
            not isinstance(superseded_by, str)
            or PACKET_ID_RE.fullmatch(superseded_by) is None
            or superseded_by == packet_id
        ):
            errors.append(
                f"packet {packet_id}: invalid {SUPERSESSION_FIELD}"
            )
            superseded_by = None
    elif SUPERSESSION_FIELD in packet:
        errors.append(
            f"packet {packet_id}: {SUPERSESSION_FIELD} is only allowed "
            "for superseded packets"
        )
        superseded_by = None
    for field in ("owner", "reviewer"):
        value = packet[field]
        if not isinstance(value, str) or TOKEN_RE.fullmatch(value) is None:
            errors.append(f"packet {packet_id}: invalid {field}")
    if packet["owner"] == packet["reviewer"]:
        errors.append(f"packet {packet_id}: owner and reviewer must differ")
    retry_budget = packet["retry_budget"]
    if not is_int(retry_budget) or not 0 <= retry_budget <= 100:
        errors.append(f"packet {packet_id}: retry_budget must be in [0, 100]")
    external_side_effects = validate_unique_string_list(
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
    depends_on: list[str] = []
    activates: list[str] = []
    integration_invariants: list[IntegrationInvariant] = []
    routing: dict[str, Any] | None = None
    if schema_version == "work-packet-instance/v2":
        raw_depends_on = validate_packet_id_list(
            packet["depends_on"],
            packet_id,
            "depends_on",
            errors,
        )
        raw_activates = validate_packet_id_list(
            packet["activates"],
            packet_id,
            "activates",
            errors,
        )
        if checks is None:
            checks_for_integration: list[dict[str, Any]] = []
        else:
            checks_for_integration = checks
        raw_integrations = validate_integration_invariants(
            packet["integration_invariants"],
            packet_id,
            checks_for_integration,
            project_root,
            policy,
            errors,
        )
        if raw_depends_on is not None:
            depends_on = raw_depends_on
        if raw_activates is not None:
            activates = raw_activates
        if raw_integrations is not None:
            integration_invariants = raw_integrations
        routing_value = packet["routing"]
        routing_fields = set(policy["routing"]["required_fields"])
        if exact_keys(
            routing_value,
            routing_fields,
            f"packet {packet_id} routing",
            errors,
        ):
            phase_id = routing_value["phase_id"]
            action_id = routing_value["action_id"]
            route_order = routing_value["route_order"]
            summary = routing_value["summary"]
            addresses = validate_unique_string_list(
                routing_value["addresses_finding_ids"],
                f"packet {packet_id} routing addresses_finding_ids",
                errors,
                maximum_items=64,
            )
            if (
                not isinstance(phase_id, str)
                or PHASE_ID_RE.fullmatch(phase_id) is None
            ):
                errors.append(f"packet {packet_id}: invalid routing phase_id")
            if (
                not isinstance(action_id, str)
                or ACTION_ID_RE.fullmatch(action_id) is None
            ):
                errors.append(f"packet {packet_id}: invalid routing action_id")
            if not is_int(route_order) or route_order < 1:
                errors.append(
                    f"packet {packet_id}: routing route_order must be positive"
                )
            if not is_nonempty_string(summary, maximum=512):
                errors.append(f"packet {packet_id}: invalid routing summary")
            if addresses is not None and any(
                FINDING_ID_RE.fullmatch(finding_id) is None
                for finding_id in addresses
            ):
                errors.append(
                    f"packet {packet_id}: invalid routing finding identifier"
                )
            if len(errors) == start:
                routing = routing_value
    if len(errors) != start:
        return None
    assert reads is not None
    assert checks is not None
    assert invariants is not None
    assert external_side_effects is not None
    assert isinstance(schema_version, str)
    return PacketRecord(
        source=source,
        raw=packet,
        schema_version=schema_version,
        packet_id=packet_id,
        goal_id=goal_id,
        state=state,
        superseded_by=superseded_by,
        writes=writes,
        reads=reads,
        acceptance_checks=checks,
        checkpoint=checkpoint,
        acceptance_receipt=acceptance,
        invariants=invariants,
        depends_on=depends_on,
        activates=activates,
        integration_invariants=integration_invariants,
        routing=routing,
        external_side_effects=external_side_effects,
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


def verify_historical_snapshots(
    record: PacketRecord,
    snapshots: Any,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(snapshots, list) or len(snapshots) != len(record.writes):
        errors.append(f"{label}: historical snapshot count differs")
        return
    for index, (snapshot, claim) in enumerate(
        zip(snapshots, record.writes, strict=True)
    ):
        item_label = f"{label} snapshots[{index}]"
        if not exact_keys(
            snapshot,
            {"path", "kind", "state", "content_sha256"},
            item_label,
            errors,
        ):
            continue
        state = snapshot["state"]
        digest = snapshot["content_sha256"]
        if (
            snapshot["path"] != claim.path.lexical
            or snapshot["kind"] != claim.kind
            or state not in {"absent", "file", "tree"}
            or (state == "absent" and digest is not None)
            or (
                state != "absent"
                and (
                    not isinstance(digest, str)
                    or SHA256_RE.fullmatch(digest) is None
                )
            )
        ):
            errors.append(f"{item_label}: historical claim identity differs")


def expected_receipt_schema_version(
    record: PacketRecord,
    policy: dict[str, Any],
    receipt_kind: str,
) -> str:
    completion = policy["completion"]
    if (
        policy["schema_version"] == "work-packet-policy/v2"
        and record.schema_version == "work-packet-instance/v1"
    ):
        return completion[f"historical_{receipt_kind}_schema_version"]
    return completion[f"{receipt_kind}_schema_version"]


def validate_prerequisite_receipt_entries(
    value: Any,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(value, list):
        errors.append(f"{label}: prerequisite_receipts must be a list")
        return
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_label = f"{label} prerequisite_receipts[{index}]"
        if not exact_keys(
            item,
            {
                "packet_id",
                "packet_contract_sha256",
                "checkpoint_receipt_sha256",
                "acceptance_receipt_sha256",
            },
            item_label,
            errors,
        ):
            continue
        packet_id = item["packet_id"]
        if not isinstance(packet_id, str) or PACKET_ID_RE.fullmatch(packet_id) is None:
            errors.append(f"{item_label}: invalid packet_id")
        elif packet_id in seen:
            errors.append(f"{item_label}: duplicate prerequisite packet_id")
        else:
            seen.add(packet_id)
        for field in (
            "packet_contract_sha256",
            "checkpoint_receipt_sha256",
            "acceptance_receipt_sha256",
        ):
            digest = item[field]
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                errors.append(f"{item_label}: invalid {field}")


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
    if record.schema_version == "work-packet-instance/v2":
        expected_fields.add("prerequisite_receipts")
    if not exact_keys(receipt, expected_fields, label, errors):
        return None
    expected_schema = expected_receipt_schema_version(
        record,
        policy,
        "checkpoint",
    )
    if receipt["schema_version"] != expected_schema:
        errors.append(f"{label}: schema_version differs")
    if receipt["packet_id"] != record.packet_id:
        errors.append(f"{label}: packet_id differs")
    if receipt["packet_contract_sha256"] != record.contract_sha256:
        errors.append(f"{label}: packet contract digest differs")
    if not is_int(receipt["sequence"]) or receipt["sequence"] < 1:
        errors.append(f"{label}: sequence must be a positive integer")
    if record.schema_version == "work-packet-instance/v2":
        validate_prerequisite_receipt_entries(receipt["prerequisite_receipts"], label, errors)
    if record.state == "superseded":
        verify_historical_snapshots(
            record,
            receipt["snapshots"],
            label,
            errors,
        )
    else:
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
            errors.append(
                f"{label}: snapshots differ from current owned write set"
            )
    if len(errors) != start:
        return None
    return receipt


def verify_acceptance_receipt(
    record: PacketRecord,
    checkpoint: dict[str, Any] | None,
    policy: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    if record.acceptance_receipt is None:
        return None
    label = f"packet {record.packet_id} acceptance receipt"
    start = len(errors)
    receipt = load_json_object(record.acceptance_receipt.candidate, errors, label)
    if receipt is None:
        return None
    expected_fields = {
        "schema_version",
        "packet_id",
        "packet_contract_sha256",
        "checkpoint_receipt_sha256",
        "checks",
    }
    if not exact_keys(receipt, expected_fields, label, errors):
        return None
    expected_schema = expected_receipt_schema_version(
        record,
        policy,
        "acceptance",
    )
    if receipt["schema_version"] != expected_schema:
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
    if len(errors) != start:
        return None
    return receipt


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


@dataclass
class DagAnalysis:
    live_records: list[PacketRecord]
    edges: list[tuple[str, str]]
    root_packet_ids: list[str]
    sink_packet_ids: list[str]
    topological_packet_ids: list[str]
    descendants: dict[str, set[str]]
    blocked_by: dict[str, list[str]]


def analyze_v2_dag(
    records: list[PacketRecord],
    policy: dict[str, Any],
    errors: list[str],
) -> DagAnalysis:
    live_states = set(policy["dag"]["live_states"])
    live_records = [record for record in records if record.state in live_states]
    route_orders: dict[int, str] = {}
    action_ids: dict[str, str] = {}
    for record in live_records:
        if record.routing is None:
            errors.append(f"packet {record.packet_id}: live V2 routing is missing")
            continue
        route_order = record.routing["route_order"]
        action_id = record.routing["action_id"]
        prior_order = route_orders.get(route_order)
        if prior_order is not None:
            errors.append(
                f"routing route_order {route_order}: packets "
                f"{prior_order} and {record.packet_id} conflict"
            )
        else:
            route_orders[route_order] = record.packet_id
        prior_action = action_ids.get(action_id)
        if prior_action is not None:
            errors.append(
                f"routing action_id {action_id!r}: packets "
                f"{prior_action} and {record.packet_id} conflict"
            )
        else:
            action_ids[action_id] = record.packet_id
    records_by_id = {record.packet_id: record for record in records}
    live_by_id = {record.packet_id: record for record in live_records}
    dependency_edges: set[tuple[str, str]] = set()
    activation_edges: set[tuple[str, str]] = set()

    def validate_endpoint(
        source: PacketRecord,
        target_id: str,
        field: str,
    ) -> PacketRecord | None:
        if target_id == source.packet_id:
            errors.append(
                f"packet {source.packet_id}: self {field} reference is forbidden"
            )
            return None
        target = records_by_id.get(target_id)
        if target is None:
            errors.append(
                f"packet {source.packet_id}: {field} packet {target_id!r} is missing"
            )
            return None
        if target.state == "superseded":
            errors.append(
                f"packet {source.packet_id}: {field} packet {target_id!r} "
                "is superseded"
            )
            return None
        if target.goal_id != source.goal_id:
            errors.append(
                f"packet {source.packet_id}: {field} packet {target_id!r} "
                "belongs to a different goal"
            )
            return None
        if target.packet_id not in live_by_id:
            errors.append(
                f"packet {source.packet_id}: {field} packet {target_id!r} is not live"
            )
            return None
        return target

    for record in live_records:
        for dependency_id in record.depends_on:
            dependency = validate_endpoint(record, dependency_id, "depends_on")
            if dependency is not None:
                dependency_edges.add((dependency.packet_id, record.packet_id))
        for activated_id in record.activates:
            activated = validate_endpoint(record, activated_id, "activates")
            if activated is not None:
                activation_edges.add((record.packet_id, activated.packet_id))

    for source_id, target_id in sorted(dependency_edges - activation_edges):
        errors.append(
            f"DAG edge {source_id} -> {target_id}: depends_on is not matched "
            "by activates"
        )
    for source_id, target_id in sorted(activation_edges - dependency_edges):
        errors.append(
            f"DAG edge {source_id} -> {target_id}: activates is not matched "
            "by depends_on"
        )
    edges = sorted(dependency_edges & activation_edges)
    adjacency = {packet_id: set() for packet_id in live_by_id}
    reverse = {packet_id: set() for packet_id in live_by_id}
    for source_id, target_id in edges:
        adjacency[source_id].add(target_id)
        reverse[target_id].add(source_id)

    indegree = {packet_id: len(reverse[packet_id]) for packet_id in live_by_id}
    ready = sorted(packet_id for packet_id, degree in indegree.items() if degree == 0)
    topological: list[str] = []
    while ready:
        packet_id = ready.pop(0)
        topological.append(packet_id)
        for target_id in sorted(adjacency[packet_id]):
            indegree[target_id] -= 1
            if indegree[target_id] == 0:
                ready.append(target_id)
                ready.sort()
    cyclic = sorted(set(live_by_id) - set(topological))
    if cyclic:
        errors.append(f"DAG cycle detected among live packets: {cyclic}")
        topological.extend(cyclic)

    roots: list[str] = []
    sinks: list[str] = []
    records_by_goal: dict[str, list[PacketRecord]] = {}
    for record in live_records:
        records_by_goal.setdefault(record.goal_id, []).append(record)
    for goal_id, goal_records in sorted(records_by_goal.items()):
        goal_ids = {record.packet_id for record in goal_records}
        goal_roots = sorted(
            packet_id for packet_id in goal_ids if not reverse[packet_id]
        )
        goal_sinks = sorted(
            packet_id for packet_id in goal_ids if not adjacency[packet_id]
        )
        roots.extend(goal_roots)
        sinks.extend(goal_sinks)
        if len(goal_roots) != 1:
            errors.append(
                f"goal {goal_id}: expected exactly one live root; found {goal_roots}"
            )
        if len(goal_sinks) != 1:
            errors.append(
                f"goal {goal_id}: expected exactly one live sink; found {goal_sinks}"
            )

    descendants: dict[str, set[str]] = {}
    for packet_id in live_by_id:
        visited: set[str] = set()
        pending = list(adjacency[packet_id])
        while pending:
            descendant_id = pending.pop()
            if descendant_id in visited:
                continue
            visited.add(descendant_id)
            pending.extend(adjacency[descendant_id] - visited)
        visited.discard(packet_id)
        descendants[packet_id] = visited

    for goal_id, goal_records in sorted(records_by_goal.items()):
        goal_ids = {record.packet_id for record in goal_records}
        goal_roots = [packet_id for packet_id in goal_ids if not reverse[packet_id]]
        goal_sinks = [packet_id for packet_id in goal_ids if not adjacency[packet_id]]
        if len(goal_roots) == 1:
            unreachable = sorted(
                goal_ids - descendants[goal_roots[0]] - {goal_roots[0]}
            )
            if unreachable:
                errors.append(
                    f"goal {goal_id}: live packets are not reachable from root "
                    f"{goal_roots[0]}: {unreachable}"
                )
        if len(goal_sinks) == 1:
            cannot_reach_sink = sorted(
                packet_id
                for packet_id in goal_ids
                if packet_id != goal_sinks[0]
                and goal_sinks[0] not in descendants[packet_id]
            )
            if cannot_reach_sink:
                errors.append(
                    f"goal {goal_id}: live packets cannot reach sink "
                    f"{goal_sinks[0]}: {cannot_reach_sink}"
                )

    blocked_by_sets: dict[str, set[str]] = {}
    for record in live_records:
        if record.state != "blocked":
            continue
        for descendant_id in descendants[record.packet_id]:
            blocked_by_sets.setdefault(descendant_id, set()).add(record.packet_id)
    blocked_by = {
        packet_id: sorted(blockers)
        for packet_id, blockers in sorted(blocked_by_sets.items())
    }
    return DagAnalysis(
        live_records=live_records,
        edges=edges,
        root_packet_ids=sorted(roots),
        sink_packet_ids=sorted(sinks),
        topological_packet_ids=topological,
        descendants=descendants,
        blocked_by=blocked_by,
    )


def validate_v2_parallel_conflicts(
    analysis: DagAnalysis,
    errors: list[str],
) -> None:
    live_records = sorted(analysis.live_records, key=lambda record: record.packet_id)
    for left_index, left in enumerate(live_records):
        for right in live_records[left_index + 1 :]:
            if (
                right.packet_id in analysis.descendants[left.packet_id]
                or left.packet_id in analysis.descendants[right.packet_id]
            ):
                continue
            for left_claim in left.writes:
                for right_claim in right.writes:
                    if path_relation(
                        left_claim.path.canonical,
                        right_claim.path.canonical,
                    ) is not None:
                        errors.append(
                            f"parallel packets {left.packet_id} and "
                            f"{right.packet_id}: write/write conflict between "
                            f"{left_claim.path.lexical!r} and "
                            f"{right_claim.path.lexical!r}"
                        )
            for reader, writer in ((left, right), (right, left)):
                for read in reader.reads:
                    for write in writer.writes:
                        if path_relation(read.canonical, write.path.canonical) is not None:
                            errors.append(
                                f"parallel packets {left.packet_id} and "
                                f"{right.packet_id}: read/write conflict; "
                                f"{reader.packet_id} reads {read.lexical!r} while "
                                f"{writer.packet_id} writes {write.path.lexical!r}"
                            )
            shared_effects = sorted(
                set(left.external_side_effects)
                & set(right.external_side_effects)
            )
            for effect in shared_effects:
                errors.append(
                    f"parallel packets {left.packet_id} and {right.packet_id}: "
                    f"identical external side effect conflict {effect!r}"
                )


def write_claim_owns_file(claim: WriteClaim, canonical_path: str) -> bool:
    relation = path_relation(claim.path.canonical, canonical_path)
    if claim.kind == "file":
        return relation == "equal"
    return relation in {"equal", "left_parent"}


def validate_v2_integration_invariants(
    analysis: DagAnalysis,
    errors: list[str],
) -> int:
    live_by_id = {record.packet_id: record for record in analysis.live_records}
    declarations_by_goal: dict[str, int] = {}
    records_by_goal: dict[str, int] = {}
    declared_count = 0
    for record in analysis.live_records:
        records_by_goal[record.goal_id] = records_by_goal.get(record.goal_id, 0) + 1
        dependency_ids = set(record.depends_on)
        covered_dependencies: set[str] = set()
        read_paths = {read.canonical for read in record.reads}
        if len(dependency_ids) >= 2 and not record.integration_invariants:
            errors.append(
                f"join packet {record.packet_id}: integration_invariant is required"
            )
        for invariant in record.integration_invariants:
            probe_count = len(invariant.probe_check_ids)
            declared_count += probe_count
            declarations_by_goal[record.goal_id] = (
                declarations_by_goal.get(record.goal_id, 0) + probe_count
            )
            for input_item in invariant.inputs:
                if input_item.packet_id not in dependency_ids:
                    errors.append(
                        f"packet {record.packet_id} integration invariant "
                        f"{invariant.invariant_id}: input packet "
                        f"{input_item.packet_id} is not a direct dependency"
                    )
                    continue
                covered_dependencies.add(input_item.packet_id)
                owner = live_by_id.get(input_item.packet_id)
                if owner is None or not any(
                    write_claim_owns_file(claim, input_item.path.canonical)
                    for claim in owner.writes
                ):
                    errors.append(
                        f"packet {record.packet_id} integration invariant "
                        f"{invariant.invariant_id}: input path "
                        f"{input_item.path.lexical!r} is not owned by packet "
                        f"{input_item.packet_id}"
                    )
                if input_item.path.canonical not in read_paths:
                    errors.append(
                        f"packet {record.packet_id} integration invariant "
                        f"{invariant.invariant_id}: input path "
                        f"{input_item.path.lexical!r} is not in join "
                        "read_dependencies"
                    )
        if len(dependency_ids) >= 2:
            omitted = sorted(dependency_ids - covered_dependencies)
            if omitted:
                errors.append(
                    f"join packet {record.packet_id}: integration inputs omit "
                    f"direct branches {omitted}"
                )
    for goal_id, record_count in sorted(records_by_goal.items()):
        if record_count > 1 and declarations_by_goal.get(goal_id, 0) == 0:
            errors.append(
                f"goal {goal_id}: multi-node goal declares zero integration probes"
            )
    return declared_count


def expected_prerequisite_receipts(
    record: PacketRecord,
    records_by_id: dict[str, PacketRecord],
    checkpoints: dict[str, dict[str, Any]],
    acceptances: dict[str, dict[str, Any]],
    eligible_dependency_ids: set[str],
    eligibility_label: str,
    errors: list[str],
) -> list[dict[str, str]] | None:
    expected: list[dict[str, str]] = []
    valid = True
    for dependency_id in sorted(record.depends_on):
        dependency = records_by_id.get(dependency_id)
        checkpoint = checkpoints.get(dependency_id)
        acceptance = acceptances.get(dependency_id)
        if (
            dependency is None
            or dependency_id not in eligible_dependency_ids
            or checkpoint is None
            or acceptance is None
        ):
            errors.append(
                f"packet {record.packet_id} checkpoint receipt: prerequisite "
                f"{dependency_id} is not {eligibility_label} with valid receipts"
            )
            valid = False
            continue
        expected.append(
            {
                "packet_id": dependency_id,
                "packet_contract_sha256": dependency.contract_sha256,
                "checkpoint_receipt_sha256": canonical_sha256(checkpoint),
                "acceptance_receipt_sha256": canonical_sha256(acceptance),
            }
        )
    return expected if valid else None


def verify_v2_receipts(
    records: list[PacketRecord],
    analysis: DagAnalysis,
    project_root: Path,
    policy: dict[str, Any],
    errors: list[str],
) -> tuple[int, int, set[str], set[str], int]:
    completion = policy["completion"]
    checkpoints: dict[str, dict[str, Any]] = {}
    acceptances: dict[str, dict[str, Any]] = {}
    for record in records:
        checkpoint_required = record.state in completion["checkpoint_required_states"]
        acceptance_required = record.state in completion["acceptance_required_states"]
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
        checkpoint = None
        if record.checkpoint is not None:
            checkpoint = verify_checkpoint_receipt(
                record,
                project_root,
                policy,
                errors,
            )
            if checkpoint is not None:
                checkpoints[record.packet_id] = checkpoint
        if record.acceptance_receipt is not None:
            acceptance = verify_acceptance_receipt(
                record,
                checkpoint,
                policy,
                errors,
            )
            if acceptance is not None:
                acceptances[record.packet_id] = acceptance

    records_by_id = {record.packet_id: record for record in records}
    live_by_id = {record.packet_id: record for record in analysis.live_records}
    verified_complete: set[str] = set()
    receipt_chain_valid: set[str] = set()
    completion_verified_count = 0
    for packet_id in analysis.topological_packet_ids:
        record = live_by_id[packet_id]
        checkpoint = checkpoints.get(packet_id)
        acceptance = acceptances.get(packet_id)
        prerequisite_valid = True
        if checkpoint is not None:
            expected = expected_prerequisite_receipts(
                record,
                records_by_id,
                checkpoints,
                acceptances,
                verified_complete,
                "verified_complete",
                errors,
            )
            if expected is None:
                prerequisite_valid = False
            elif checkpoint["prerequisite_receipts"] != expected:
                errors.append(
                    f"packet {packet_id} checkpoint receipt: "
                    "prerequisite_receipts do not exactly bind direct dependencies"
                )
                prerequisite_valid = False
        if checkpoint is not None and acceptance is not None and prerequisite_valid:
            receipt_chain_valid.add(packet_id)
        if record.state == "complete" and packet_id in receipt_chain_valid:
            verified_complete.add(packet_id)
            completion_verified_count += 1

    superseded_receipt_verified_count = 0
    retained_receipt_ids = set(checkpoints) & set(acceptances)
    for record in records:
        if (
            record.state != "superseded"
            or record.packet_id not in retained_receipt_ids
        ):
            continue
        historical_binding_valid = True
        if record.schema_version == "work-packet-instance/v2":
            checkpoint = checkpoints[record.packet_id]
            expected = expected_prerequisite_receipts(
                record,
                records_by_id,
                checkpoints,
                acceptances,
                retained_receipt_ids,
                "retained",
                errors,
            )
            if expected is None:
                historical_binding_valid = False
            elif checkpoint["prerequisite_receipts"] != expected:
                errors.append(
                    f"packet {record.packet_id} checkpoint receipt: historical "
                    "prerequisite_receipts do not exactly bind direct dependencies"
                )
                historical_binding_valid = False
        if historical_binding_valid:
            superseded_receipt_verified_count += 1
    integration_probe_verified_count = 0
    required_probe_states = set(
        policy["integration_probes"]["probe_receipt_required_states"]
    )
    for record in analysis.live_records:
        for invariant in record.integration_invariants:
            for probe_id in invariant.probe_check_ids:
                if record.packet_id in receipt_chain_valid:
                    integration_probe_verified_count += 1
                elif record.state in required_probe_states:
                    errors.append(
                        f"packet {record.packet_id} integration probe {probe_id}: "
                        "not verified by a valid successful acceptance receipt"
                    )
    return (
        completion_verified_count,
        superseded_receipt_verified_count,
        verified_complete,
        receipt_chain_valid,
        integration_probe_verified_count,
    )


def validate_v2_activation_states(
    analysis: DagAnalysis,
    verified_complete: set[str],
    errors: list[str],
) -> list[str]:
    activatable: list[str] = []
    for record in analysis.live_records:
        dependencies_complete = all(
            dependency_id in verified_complete
            for dependency_id in record.depends_on
        )
        if dependencies_complete and record.state == "pending":
            activatable.append(record.packet_id)
            errors.append(
                f"packet {record.packet_id}: stale_pending_activation; "
                "all dependencies are verified_complete"
            )
        elif not dependencies_complete and record.state != "pending":
            incomplete = sorted(
                dependency_id
                for dependency_id in record.depends_on
                if dependency_id not in verified_complete
            )
            errors.append(
                f"packet {record.packet_id}: upstream packets {incomplete} are not "
                "verified_complete; downstream state must remain pending"
            )
    return sorted(activatable)


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
            "superseded_receipt_verified_count": 0,
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
            "superseded_receipt_verified_count": 0,
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
        invalid_policy_result = {
            "status": "fail",
            "policy_id": policy.get("policy_id") if policy else None,
            "packet_count": 0,
            "active_packet_count": 0,
            "ownership_claim_count": 0,
            "ownership_conflict_count": 0,
            "semantic_probe_count": 0,
            "completion_verified_count": 0,
            "superseded_receipt_verified_count": 0,
            "errors": sorted(set(errors)),
            "platform_and_process_limitations": limitations,
        }
        if policy and policy.get("schema_version") == "work-packet-policy/v2":
            invalid_policy_result.update(
                {
                    "dag_edges": [],
                    "root_packet_ids": [],
                    "sink_packet_ids": [],
                    "activatable_packet_ids": [],
                    "blocked_by": {},
                    "integration_probe_declared_count": 0,
                    "integration_probe_verified_count": 0,
                }
            )
        return invalid_policy_result

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

    records_by_id = {record.packet_id: record for record in records}
    allowed_successor_states = set(
        policy["supersession"]["successor_allowed_states"]
    )
    for record in records:
        if record.state != "superseded":
            continue
        successor = (
            records_by_id.get(record.superseded_by)
            if record.superseded_by is not None
            else None
        )
        if successor is None:
            errors.append(
                f"packet {record.packet_id}: superseding packet is missing"
            )
            continue
        if successor.state not in allowed_successor_states:
            errors.append(
                f"packet {record.packet_id}: superseding packet state is invalid"
            )
        if successor.raw["goal_id"] != record.raw["goal_id"]:
            errors.append(
                f"packet {record.packet_id}: superseding packet goal differs"
            )
        historical_writes = {
            (claim.path.lexical, claim.kind) for claim in record.writes
        }
        successor_writes = {
            (claim.path.lexical, claim.kind) for claim in successor.writes
        }
        if successor_writes != historical_writes:
            errors.append(
                f"packet {record.packet_id}: superseding packet write set differs"
            )

    is_v2 = policy["schema_version"] == "work-packet-policy/v2"
    dag_analysis: DagAnalysis | None = None
    integration_probe_declared_count = 0
    if is_v2:
        dag_analysis = analyze_v2_dag(records, policy, errors)
        validate_v2_parallel_conflicts(dag_analysis, errors)
        integration_probe_declared_count = validate_v2_integration_invariants(
            dag_analysis,
            errors,
        )

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

    integration_probe_verified_count = 0
    activatable_packet_ids: list[str] = []
    if is_v2:
        assert dag_analysis is not None
        (
            completion_verified_count,
            superseded_receipt_verified_count,
            verified_complete,
            _receipt_chain_valid,
            integration_probe_verified_count,
        ) = verify_v2_receipts(
            records,
            dag_analysis,
            project_root,
            policy,
            errors,
        )
        activatable_packet_ids = validate_v2_activation_states(
            dag_analysis,
            verified_complete,
            errors,
        )
    else:
        completion_verified_count = 0
        superseded_receipt_verified_count = 0
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
            acceptance_valid = None
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
            if (
                record.state == "superseded"
                and checkpoint_receipt is not None
                and acceptance_valid
            ):
                superseded_receipt_verified_count += 1

    unique_errors = sorted(set(errors))
    result = {
        "status": "pass" if not unique_errors else "fail",
        "policy_id": policy["policy_id"],
        "packet_count": len(packet_files),
        "active_packet_count": len(active_records),
        "ownership_claim_count": len(active_claims),
        "ownership_conflict_count": ownership_conflicts,
        "semantic_probe_count": semantic_probe_count,
        "completion_verified_count": completion_verified_count,
        "superseded_receipt_verified_count": (
            superseded_receipt_verified_count
        ),
        "errors": unique_errors,
        "platform_and_process_limitations": limitations,
    }
    if is_v2:
        assert dag_analysis is not None
        result.update(
            {
                "dag_edges": [list(edge) for edge in dag_analysis.edges],
                "root_packet_ids": dag_analysis.root_packet_ids,
                "sink_packet_ids": dag_analysis.sink_packet_ids,
                "activatable_packet_ids": activatable_packet_ids,
                "blocked_by": dag_analysis.blocked_by,
                "integration_probe_declared_count": (
                    integration_probe_declared_count
                ),
                "integration_probe_verified_count": (
                    integration_probe_verified_count
                ),
            }
        )
    return result


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
            "superseded_receipt_verified_count": 0,
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
