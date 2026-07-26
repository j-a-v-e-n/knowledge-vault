#!/usr/bin/env python3
"""Derive and maintain the canonical, non-self-referential project-state view."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


SCRIPT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_RELATIVE = Path("governance/PROJECT_STATE_VIEW_POLICY_V1.json")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@-]{0,127}$")
PACKET_ID_RE = re.compile(r"^WP-[A-Z0-9][A-Z0-9._-]{0,63}$")


class DuplicateKeyError(ValueError):
    """Raised when a JSON object attempts to overwrite a prior key."""


class ProjectStateError(RuntimeError):
    """Raised when canonical project state cannot be derived safely."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def canonical_json_bytes(value: Any) -> bytes:
    """Return the sole canonical JSON encoding used by facts and derive output."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ProjectStateError(f"{label}: invalid or unreadable JSON: {exc}") from exc


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProjectStateError(f"{label}: must be an object")
    return value


def require_exact_fields(
    value: Any,
    expected: set[str],
    label: str,
) -> dict[str, Any]:
    item = require_object(value, label)
    actual = set(item)
    if actual != expected:
        raise ProjectStateError(
            f"{label}: fields differ; "
            f"missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
    return item


def require_fields(
    value: Any,
    required: set[str],
    label: str,
) -> dict[str, Any]:
    item = require_object(value, label)
    missing = required - set(item)
    if missing:
        raise ProjectStateError(f"{label}: missing fields {sorted(missing)}")
    return item


def is_int(value: Any) -> bool:
    return type(value) is int


def require_identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or IDENTIFIER_RE.fullmatch(value) is None:
        raise ProjectStateError(f"{label}: invalid identifier")
    return value


def require_trimmed_string(value: Any, label: str, maximum: int = 1024) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or len(value) > maximum
    ):
        raise ProjectStateError(f"{label}: must be a bounded non-empty string")
    return value


def require_unique_string_list(
    value: Any,
    label: str,
    *,
    allow_empty: bool = True,
) -> list[str]:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or not all(isinstance(item, str) and item for item in value)
    ):
        raise ProjectStateError(f"{label}: must be a list of non-empty strings")
    if len(value) != len(set(value)):
        raise ProjectStateError(f"{label}: duplicate entries are forbidden")
    return value


def normalize_relative_path(raw: Any, label: str) -> str:
    value = require_trimmed_string(raw, label)
    if "\\" in value or "\x00" in value:
        raise ProjectStateError(f"{label}: must use POSIX separators and no NUL")
    candidate = PurePosixPath(value)
    components = value.split("/")
    if (
        candidate.is_absolute()
        or value in {".", "~"}
        or components[0] == "~"
        or any(component in {"", ".", ".."} for component in components)
    ):
        raise ProjectStateError(f"{label}: must be a normalized project-relative path")
    return value


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def resolve_project_path(
    project_root: Path,
    raw: Any,
    label: str,
    *,
    must_exist: bool,
) -> tuple[str, Path]:
    relative = normalize_relative_path(raw, label)
    candidate = project_root / relative
    try:
        resolved = candidate.resolve(strict=must_exist)
    except (OSError, RuntimeError) as exc:
        raise ProjectStateError(f"{label}: cannot resolve: {exc}") from exc
    if not is_within(resolved, project_root):
        raise ProjectStateError(f"{label}: canonical path escapes project root")
    return relative, candidate


def decode_json_pointer(pointer: str, label: str) -> list[str]:
    if pointer == "":
        return []
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ProjectStateError(f"{label}: JSON pointer must be empty or start with '/'")
    decoded: list[str] = []
    for raw_token in pointer[1:].split("/"):
        token = ""
        index = 0
        while index < len(raw_token):
            if raw_token[index] != "~":
                token += raw_token[index]
                index += 1
                continue
            if index + 1 >= len(raw_token) or raw_token[index + 1] not in {"0", "1"}:
                raise ProjectStateError(f"{label}: invalid JSON pointer escape")
            token += "~" if raw_token[index + 1] == "0" else "/"
            index += 2
        decoded.append(token)
    return decoded


def extract_json_pointer(document: Any, pointer: str, label: str) -> Any:
    value = document
    for token in decode_json_pointer(pointer, label):
        if isinstance(value, dict):
            if token not in value:
                raise ProjectStateError(f"{label}: missing object key {token!r}")
            value = value[token]
        elif isinstance(value, list):
            if token == "-" or not token.isdigit() or (token.startswith("0") and token != "0"):
                raise ProjectStateError(f"{label}: invalid array index {token!r}")
            index = int(token)
            if index >= len(value):
                raise ProjectStateError(f"{label}: array index out of range")
            value = value[index]
        else:
            raise ProjectStateError(f"{label}: pointer traverses a scalar")
    return value


@dataclass(frozen=True)
class CanonicalFact:
    path: str
    json_pointers: tuple[str, ...]
    canonical_sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "json_pointers": list(self.json_pointers),
            "canonical_sha256": self.canonical_sha256,
        }


class FactSet:
    """Collect selected facts without hashing generated views or Git observations."""

    def __init__(self) -> None:
        self._facts: dict[str, CanonicalFact] = {}

    def add_selected(self, path: str, document: Any, pointers: list[str]) -> None:
        if path in self._facts:
            raise ProjectStateError(f"basis: duplicate fact path {path!r}")
        if len(pointers) != len(set(pointers)):
            raise ProjectStateError(f"basis: duplicate JSON pointer for {path!r}")
        ordered = sorted(pointers)
        selected = [
            {
                "json_pointer": pointer,
                "value": extract_json_pointer(
                    document,
                    pointer,
                    f"basis fact {path} {pointer}",
                ),
            }
            for pointer in ordered
        ]
        self._facts[path] = CanonicalFact(
            path,
            tuple(ordered),
            canonical_sha256(selected),
        )

    def add_observation(self, path: str, value: Any) -> None:
        if path in self._facts:
            raise ProjectStateError(f"basis: duplicate fact path {path!r}")
        self._facts[path] = CanonicalFact(path, (), canonical_sha256(value))

    def public_facts(self) -> list[dict[str, Any]]:
        return [self._facts[path].as_dict() for path in sorted(self._facts)]


def validate_policy(policy: dict[str, Any]) -> None:
    require_exact_fields(
        policy,
        {
            "schema_version",
            "policy_id",
            "projection_schema_version",
            "sources",
            "review_source",
            "packet_routing",
            "phase_model",
            "rendering",
            "basis",
            "limitations",
        },
        "policy",
    )
    if policy["schema_version"] != "project-state-view-policy/v1":
        raise ProjectStateError("policy: unsupported schema_version")
    if policy["policy_id"] != "PROJECT-STATE-VIEW-V1":
        raise ProjectStateError("policy: unexpected policy_id")
    if policy["projection_schema_version"] != "project-state-view/v1":
        raise ProjectStateError("policy: unsupported projection schema")

    sources = require_exact_fields(
        policy["sources"],
        {"acceptance_contract", "review_register", "work_packets", "views"},
        "policy.sources",
    )
    contract = require_exact_fields(
        sources["acceptance_contract"],
        {"path", "json_pointers"},
        "policy.sources.acceptance_contract",
    )
    normalize_relative_path(contract["path"], "policy acceptance contract path")
    expected_contract_pointers = [
        "/schema_version",
        "/contract_id",
        "/status",
        "/change_control/closure_mutation_policy/freeze_state_authority",
    ]
    if contract["json_pointers"] != expected_contract_pointers:
        raise ProjectStateError("policy: acceptance contract pointers differ")
    reviews = require_exact_fields(
        sources["review_register"],
        {"path", "rounds_pointer"},
        "policy.sources.review_register",
    )
    normalize_relative_path(reviews["path"], "policy review register path")
    if reviews["rounds_pointer"] != "/challenge/rounds":
        raise ProjectStateError("policy: review rounds pointer differs")
    packets = require_exact_fields(
        sources["work_packets"],
        {"directory", "filename_suffix", "recursive"},
        "policy.sources.work_packets",
    )
    normalize_relative_path(packets["directory"], "policy packet directory")
    if packets["filename_suffix"] != ".packet.json" or packets["recursive"] is not False:
        raise ProjectStateError("policy: packet discovery rule differs")
    if sources["views"] != ["STATUS.md", "TASK_BOARD.md", "LOOP_RUN_LOG.md"]:
        raise ProjectStateError("policy: visible view set differs")
    for index, view in enumerate(sources["views"]):
        normalize_relative_path(view, f"policy view[{index}]")

    review = require_exact_fields(
        policy["review_source"],
        {
            "minimum_projection_sequence",
            "explicit_sequence_rule",
            "projection_sequence_rule",
            "round_required_fields",
            "finding_required_fields",
            "result_values",
            "finding_severity_values",
            "finding_state_values",
            "finding_snapshot_rule",
        },
        "policy.review_source",
    )
    if review["minimum_projection_sequence"] != 10:
        raise ProjectStateError("policy: minimum_projection_sequence must be 10")
    if review["explicit_sequence_rule"] != "strictly_increasing_unique":
        raise ProjectStateError("policy: explicit review sequence rule differs")
    if review["projection_sequence_rule"] != "contiguous_from_minimum":
        raise ProjectStateError("policy: projection review sequence rule differs")
    if review["round_required_fields"] != [
        "id",
        "review_sequence",
        "candidate_commit",
        "candidate_tree",
        "result",
        "evidence_path",
        "evidence_sha256",
        "findings",
    ]:
        raise ProjectStateError("policy: review fields differ")
    if review["finding_required_fields"] != [
        "finding_id",
        "severity",
        "state",
        "required_action_ids",
    ]:
        raise ProjectStateError("policy: finding fields differ")
    if review["result_values"] != ["blocked_freeze", "passed_freeze"]:
        raise ProjectStateError("policy: review result values differ")
    if review["finding_severity_values"] != ["critical", "major", "minor"]:
        raise ProjectStateError("policy: finding severity values differ")
    if review["finding_state_values"] != ["open", "resolved", "superseded"]:
        raise ProjectStateError("policy: finding state values differ")
    if review["finding_snapshot_rule"] != "complete_snapshot_each_projection_review":
        raise ProjectStateError("policy: finding snapshot rule differs")

    routing = require_exact_fields(
        policy["packet_routing"],
        {
            "instance_schema_version",
            "historical_superseded_instance_schema_versions",
            "historical_required_fields",
            "historical_behavior",
            "packet_required_fields",
            "routing_required_fields",
            "state_values",
            "terminal_states",
            "dependency_satisfied_states",
            "completion_verification",
            "route_order_rule",
            "addresses_finding_ids_rule",
            "direct_target_rule",
            "ready_rule",
        },
        "policy.packet_routing",
    )
    if routing["instance_schema_version"] != "work-packet-instance/v2":
        raise ProjectStateError("policy: packet V2 schema differs")
    if routing["historical_superseded_instance_schema_versions"] != [
        "work-packet-instance/v1"
    ]:
        raise ProjectStateError("policy: historical packet schemas differ")
    if routing["historical_required_fields"] != [
        "schema_version",
        "packet_id",
        "state",
        "superseded_by",
    ]:
        raise ProjectStateError("policy: historical packet fields differ")
    if routing["historical_behavior"] != (
        "accept_only_superseded_and_exclude_from_live_routing"
    ):
        raise ProjectStateError("policy: historical packet behavior differs")
    if routing["packet_required_fields"] != [
        "schema_version",
        "packet_id",
        "state",
        "depends_on",
        "routing",
    ]:
        raise ProjectStateError("policy: packet required fields differ")
    if routing["routing_required_fields"] != [
        "phase_id",
        "action_id",
        "route_order",
        "addresses_finding_ids",
        "summary",
    ]:
        raise ProjectStateError("policy: packet routing fields differ")
    expected_states = [
        "pending",
        "active",
        "blocked",
        "candidate_complete",
        "complete",
        "superseded",
    ]
    if routing["state_values"] != expected_states:
        raise ProjectStateError("policy: packet state values differ")
    if routing["terminal_states"] != ["complete", "superseded"]:
        raise ProjectStateError("policy: packet terminal states differ")
    if routing["dependency_satisfied_states"] != ["complete"]:
        raise ProjectStateError("policy: dependency completion states differ")
    if routing["completion_verification"] != "declared_complete_candidate_only":
        raise ProjectStateError("policy: unsupported packet completion verification")
    if routing["route_order_rule"] != "global_unique_positive_integer":
        raise ProjectStateError("policy: route order rule differs")
    if routing["addresses_finding_ids_rule"] != "unique_identifiers_may_be_empty":
        raise ProjectStateError("policy: finding address rule differs")
    if routing["direct_target_rule"] != (
        "nonterminal_current_phase_packet_addressing_finding_with_required_action"
    ):
        raise ProjectStateError("policy: direct target rule differs")
    if routing["ready_rule"] != (
        "minimum_route_order_ready_packet_in_dependency_closure_of_direct_targets"
    ):
        raise ProjectStateError("policy: ready rule differs")

    phase_model = require_exact_fields(
        policy["phase_model"],
        {"current_phase_id", "supported_phases", "unsupported_phase_behavior"},
        "policy.phase_model",
    )
    if phase_model["current_phase_id"] != "design_freeze":
        raise ProjectStateError("policy: unsupported current phase")
    if phase_model["unsupported_phase_behavior"] != "fail_closed":
        raise ProjectStateError("policy: unsupported phase behavior differs")
    phases = phase_model["supported_phases"]
    if not isinstance(phases, list) or len(phases) != 1:
        raise ProjectStateError("policy: exactly one V1 phase must be declared")
    phase = require_exact_fields(
        phases[0],
        {
            "phase_id",
            "completion_authority_path",
            "completion_verifier",
            "blocking_gate_ids",
        },
        "policy phase design_freeze",
    )
    if phase["phase_id"] != "design_freeze":
        raise ProjectStateError("policy: design_freeze phase declaration differs")
    if phase["completion_authority_path"] != "governance/FROZEN_BUNDLE_V1.json":
        raise ProjectStateError("policy: design-freeze authority path differs")
    verifier = require_exact_fields(
        phase["completion_verifier"],
        {"mode", "receipt_path", "receipt_schema_version"},
        "policy design-freeze verifier",
    )
    if verifier != {
        "mode": "unsupported",
        "receipt_path": None,
        "receipt_schema_version": None,
    }:
        raise ProjectStateError("policy: design-freeze verifier must fail closed")
    gates = require_exact_fields(
        phase["blocking_gate_ids"],
        {
            "open_findings",
            "authority_missing",
            "authority_verification_unsupported",
        },
        "policy design-freeze gates",
    )
    for name, value in gates.items():
        require_identifier(value, f"policy design-freeze gate {name}")

    rendering = require_exact_fields(
        policy["rendering"],
        {"start_marker", "end_marker", "language"},
        "policy.rendering",
    )
    if rendering != {
        "start_marker": "<!-- PROJECT_STATE_VIEW:START -->",
        "end_marker": "<!-- PROJECT_STATE_VIEW:END -->",
        "language": "json",
    }:
        raise ProjectStateError("policy: rendering contract differs")
    basis = require_exact_fields(
        policy["basis"],
        {"policy_json_pointers", "state_basis_rule", "excluded_inputs"},
        "policy.basis",
    )
    expected_policy_pointers = [
        "/schema_version",
        "/projection_schema_version",
        "/sources/acceptance_contract",
        "/sources/review_register",
        "/sources/work_packets",
        "/review_source",
        "/packet_routing",
        "/phase_model",
    ]
    if basis["policy_json_pointers"] != expected_policy_pointers:
        raise ProjectStateError("policy: basis policy pointers differ")
    if basis["state_basis_rule"] != "canonical_sha256_of_sorted_fact_descriptors":
        raise ProjectStateError("policy: state basis rule differs")
    expected_exclusions = [
        "head_commit",
        "head_tree",
        "observed_head",
        "observed_tree",
        "generated_at",
        "view_file_hashes",
        "projection_sha256",
    ]
    if basis["excluded_inputs"] != expected_exclusions:
        raise ProjectStateError("policy: basis exclusions differ")
    limitations = require_unique_string_list(
        policy["limitations"],
        "policy.limitations",
        allow_empty=False,
    )
    expected_limitations = [
        (
            "A V2 dependency packet whose state is complete is only a declarative "
            "completion candidate here; receipt verification must be integrated "
            "before this projection can call that dependency independently verified."
        ),
        (
            "The design-freeze authority verifier is intentionally unsupported in "
            "V1. A missing FROZEN_BUNDLE blocks, and file existence alone also "
            "remains blocked."
        ),
        (
            "Only design_freeze is supported. Any future phase requires an explicit "
            "policy schema update and a structured authority verifier; product "
            "completion is never inferred."
        ),
        (
            "Refresh preflights all three views and atomically replaces each "
            "individual file, but a local filesystem cannot provide one atomic "
            "transaction spanning all three files."
        ),
    ]
    if limitations != expected_limitations:
        raise ProjectStateError("policy: limitations differ")


@dataclass(frozen=True)
class Finding:
    finding_id: str
    severity: str
    state: str
    required_action_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewFold:
    latest_blocked: dict[str, Any]
    open_findings: dict[str, Finding]
    fact_pointers: tuple[str, ...]


def validate_review_round(
    raw: dict[str, Any],
    index: int,
    policy: dict[str, Any],
    prior_findings: dict[str, Finding],
) -> tuple[dict[str, Finding], list[str]]:
    review_policy = policy["review_source"]
    label = f"review round index {index}"
    require_fields(raw, set(review_policy["round_required_fields"]), label)
    review_id = require_identifier(raw["id"], f"{label}.id")
    sequence = raw["review_sequence"]
    if not is_int(sequence) or sequence < review_policy["minimum_projection_sequence"]:
        raise ProjectStateError(f"{label}.review_sequence: invalid projection sequence")
    for field in ("candidate_commit", "candidate_tree"):
        value = raw[field]
        if not isinstance(value, str) or GIT_OBJECT_RE.fullmatch(value) is None:
            raise ProjectStateError(f"{label}.{field}: invalid Git object id")
    if raw["result"] not in review_policy["result_values"]:
        raise ProjectStateError(f"{label}.result: unsupported value")
    normalize_relative_path(raw["evidence_path"], f"{label}.evidence_path")
    if not isinstance(raw["evidence_sha256"], str) or SHA256_RE.fullmatch(
        raw["evidence_sha256"]
    ) is None:
        raise ProjectStateError(f"{label}.evidence_sha256: invalid SHA-256")
    raw_findings = raw["findings"]
    if not isinstance(raw_findings, list):
        raise ProjectStateError(f"{label}.findings: must be a list")

    snapshot: dict[str, Finding] = {}
    for finding_index, raw_finding in enumerate(raw_findings):
        finding_label = f"{label}.findings[{finding_index}]"
        finding_item = require_exact_fields(
            raw_finding,
            set(review_policy["finding_required_fields"]),
            finding_label,
        )
        finding_id = require_identifier(
            finding_item["finding_id"],
            f"{finding_label}.finding_id",
        )
        if finding_id in snapshot:
            raise ProjectStateError(f"{label}: duplicate finding_id {finding_id!r}")
        severity = finding_item["severity"]
        state_value = finding_item["state"]
        if severity not in review_policy["finding_severity_values"]:
            raise ProjectStateError(f"{finding_label}.severity: unsupported value")
        if state_value not in review_policy["finding_state_values"]:
            raise ProjectStateError(f"{finding_label}.state: unsupported value")
        actions = tuple(
            require_unique_string_list(
                finding_item["required_action_ids"],
                f"{finding_label}.required_action_ids",
                allow_empty=False,
            )
        )
        for action_index, action_id in enumerate(actions):
            require_identifier(action_id, f"{finding_label}.required_action_ids[{action_index}]")
        prior = prior_findings.get(finding_id)
        if prior is None and state_value != "open":
            raise ProjectStateError(
                f"{finding_label}: a finding must first appear in open state"
            )
        if prior is not None:
            if severity != prior.severity or actions != prior.required_action_ids:
                raise ProjectStateError(
                    f"{finding_label}: severity or required actions changed"
                )
            if prior.state in {"resolved", "superseded"} and state_value != prior.state:
                raise ProjectStateError(f"{finding_label}: closed finding cannot reopen")
        snapshot[finding_id] = Finding(finding_id, severity, state_value, actions)

    missing_prior = sorted(set(prior_findings) - set(snapshot))
    if missing_prior:
        raise ProjectStateError(
            f"{label}: complete finding snapshot omitted {missing_prior}"
        )
    open_ids = sorted(
        finding_id for finding_id, finding in snapshot.items() if finding.state == "open"
    )
    if raw["result"] == "blocked_freeze" and not open_ids:
        raise ProjectStateError(f"{label}: blocked review must contain open findings")
    if raw["result"] == "passed_freeze" and open_ids:
        raise ProjectStateError(f"{label}: passed review cannot contain open findings")

    base = f"/challenge/rounds/{index}"
    pointers = [f"{base}/{field}" for field in review_policy["round_required_fields"]]
    _ = review_id
    return snapshot, pointers


def fold_reviews(register: dict[str, Any], policy: dict[str, Any]) -> ReviewFold:
    review_policy = policy["review_source"]
    rounds_pointer = policy["sources"]["review_register"]["rounds_pointer"]
    raw_rounds = extract_json_pointer(register, rounds_pointer, "review rounds")
    if not isinstance(raw_rounds, list):
        raise ProjectStateError("review rounds: must be a list")

    explicit_sequences: list[int] = []
    eligible: list[tuple[int, dict[str, Any]]] = []
    seen_sequences: set[int] = set()
    previous_sequence: int | None = None
    minimum = review_policy["minimum_projection_sequence"]
    for index, raw_round in enumerate(raw_rounds):
        round_item = require_object(raw_round, f"review round index {index}")
        if "review_sequence" not in round_item:
            continue
        sequence = round_item["review_sequence"]
        if not is_int(sequence) or sequence < 1:
            raise ProjectStateError(
                f"review round index {index}.review_sequence: must be a positive integer"
            )
        if sequence in seen_sequences:
            raise ProjectStateError(f"review_sequence {sequence}: duplicate value")
        if previous_sequence is not None and sequence <= previous_sequence:
            raise ProjectStateError(
                "explicit review_sequence values must be strictly increasing"
            )
        seen_sequences.add(sequence)
        previous_sequence = sequence
        explicit_sequences.append(sequence)
        if sequence >= minimum:
            eligible.append((index, round_item))

    _ = explicit_sequences
    if not eligible:
        raise ProjectStateError(
            f"review rounds: no complete projection review at sequence >= {minimum}"
        )
    actual_projection_sequences = [item[1]["review_sequence"] for item in eligible]
    expected_projection_sequences = list(
        range(minimum, minimum + len(actual_projection_sequences))
    )
    if actual_projection_sequences != expected_projection_sequences:
        raise ProjectStateError(
            "projection review_sequence values must be contiguous from "
            f"{minimum}; observed={actual_projection_sequences}"
        )

    findings: dict[str, Finding] = {}
    latest_blocked: dict[str, Any] | None = None
    fact_pointers: list[str] = []
    for index, raw_round in eligible:
        findings, pointers = validate_review_round(
            raw_round,
            index,
            policy,
            findings,
        )
        fact_pointers.extend(pointers)
        if raw_round["result"] == "blocked_freeze":
            latest_blocked = raw_round
    if latest_blocked is None:
        raise ProjectStateError("review rounds: no blocking review is available")
    open_findings = {
        finding_id: finding
        for finding_id, finding in findings.items()
        if finding.state == "open"
    }
    return ReviewFold(latest_blocked, open_findings, tuple(fact_pointers))


@dataclass(frozen=True)
class Packet:
    source_path: str
    packet_id: str
    state: str
    depends_on: tuple[str, ...]
    phase_id: str
    action_id: str
    route_order: int
    addresses_finding_ids: tuple[str, ...]
    summary: str


def discover_packets(
    project_root: Path,
    policy: dict[str, Any],
    facts: FactSet,
) -> dict[str, Packet]:
    source = policy["sources"]["work_packets"]
    directory_relative, directory = resolve_project_path(
        project_root,
        source["directory"],
        "packet directory",
        must_exist=True,
    )
    if directory.is_symlink() or not directory.is_dir():
        raise ProjectStateError("packet directory: must be a real directory")
    try:
        entries = sorted(directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        raise ProjectStateError(f"packet directory: cannot enumerate: {exc}") from exc
    suffix = source["filename_suffix"]
    packet_paths = [entry for entry in entries if entry.name.endswith(suffix)]
    if not packet_paths:
        raise ProjectStateError("packet directory: no packet files found")

    routing_policy = policy["packet_routing"]
    historical_schemas = set(
        routing_policy["historical_superseded_instance_schema_versions"]
    )
    supported_phases = {
        phase["phase_id"] for phase in policy["phase_model"]["supported_phases"]
    }
    records: dict[str, Packet] = {}
    seen_packet_ids: set[str] = set()
    historical_successors: dict[str, str] = {}
    route_orders: dict[int, str] = {}
    action_ids: dict[str, str] = {}
    for path in packet_paths:
        if path.is_symlink() or not path.is_file():
            raise ProjectStateError(f"packet file {path.name}: symlinks are forbidden")
        document = require_object(load_json(path, f"packet file {path.name}"), path.name)
        require_fields(
            document,
            {"schema_version", "packet_id", "state"},
            f"packet file {path.name}",
        )
        schema_version = document["schema_version"]
        packet_id = document["packet_id"]
        if not isinstance(packet_id, str) or PACKET_ID_RE.fullmatch(packet_id) is None:
            raise ProjectStateError(f"packet file {path.name}: invalid packet_id")
        expected_name = f"{packet_id}{suffix}"
        if path.name != expected_name:
            raise ProjectStateError(
                f"packet file {path.name}: filename must be {expected_name!r}"
            )
        if packet_id in seen_packet_ids:
            raise ProjectStateError(f"duplicate packet_id {packet_id!r}")
        seen_packet_ids.add(packet_id)
        relative = f"{directory_relative}/{path.name}"

        if schema_version in historical_schemas:
            require_fields(
                document,
                set(routing_policy["historical_required_fields"]),
                f"historical packet file {path.name}",
            )
            if document["state"] != "superseded":
                raise ProjectStateError(
                    f"historical packet {packet_id}: only superseded state is allowed"
                )
            successor = document["superseded_by"]
            if (
                not isinstance(successor, str)
                or PACKET_ID_RE.fullmatch(successor) is None
                or successor == packet_id
            ):
                raise ProjectStateError(
                    f"historical packet {packet_id}: invalid superseded_by"
                )
            historical_successors[packet_id] = successor
            facts.add_selected(
                relative,
                document,
                ["/schema_version", "/packet_id", "/state", "/superseded_by"],
            )
            continue
        if schema_version != routing_policy["instance_schema_version"]:
            raise ProjectStateError(
                f"packet file {path.name}: unsupported packet schema"
            )
        require_fields(
            document,
            set(routing_policy["packet_required_fields"]),
            f"packet file {path.name}",
        )
        state_value = document["state"]
        if state_value not in routing_policy["state_values"]:
            raise ProjectStateError(f"packet {packet_id}: unsupported state")
        dependencies = tuple(
            require_unique_string_list(
                document["depends_on"],
                f"packet {packet_id}.depends_on",
            )
        )
        for dependency in dependencies:
            if PACKET_ID_RE.fullmatch(dependency) is None:
                raise ProjectStateError(f"packet {packet_id}: invalid dependency id")
            if dependency == packet_id:
                raise ProjectStateError(f"packet {packet_id}: self dependency is forbidden")
        route = require_exact_fields(
            document["routing"],
            set(routing_policy["routing_required_fields"]),
            f"packet {packet_id}.routing",
        )
        phase_id = require_identifier(route["phase_id"], f"packet {packet_id}.phase_id")
        if phase_id not in supported_phases:
            raise ProjectStateError(f"packet {packet_id}: unsupported phase {phase_id!r}")
        action_id = require_identifier(route["action_id"], f"packet {packet_id}.action_id")
        if action_id in action_ids:
            raise ProjectStateError(
                f"action_id {action_id!r}: ambiguous packets "
                f"{action_ids[action_id]!r} and {packet_id!r}"
            )
        action_ids[action_id] = packet_id
        route_order = route["route_order"]
        if not is_int(route_order) or route_order < 1:
            raise ProjectStateError(f"packet {packet_id}: route_order must be positive")
        if route_order in route_orders:
            raise ProjectStateError(
                f"route_order {route_order}: ambiguous packets "
                f"{route_orders[route_order]!r} and {packet_id!r}"
            )
        route_orders[route_order] = packet_id
        addresses = tuple(
            require_unique_string_list(
                route["addresses_finding_ids"],
                f"packet {packet_id}.addresses_finding_ids",
                allow_empty=True,
            )
        )
        for finding_id in addresses:
            require_identifier(finding_id, f"packet {packet_id}.addresses_finding_ids")
        summary = require_trimmed_string(route["summary"], f"packet {packet_id}.summary")
        records[packet_id] = Packet(
            relative,
            packet_id,
            state_value,
            dependencies,
            phase_id,
            action_id,
            route_order,
            addresses,
            summary,
        )
        facts.add_selected(
            relative,
            document,
            [
                "/schema_version",
                "/packet_id",
                "/state",
                "/depends_on",
                "/routing/phase_id",
                "/routing/action_id",
                "/routing/route_order",
                "/routing/addresses_finding_ids",
                "/routing/summary",
            ],
        )
    for historical_id, successor in sorted(historical_successors.items()):
        if successor not in records:
            raise ProjectStateError(
                f"historical packet {historical_id}: superseding live V2 packet "
                f"{successor!r} is missing"
            )
    if not records:
        raise ProjectStateError("packet directory: no live V2 packet files found")
    return records


def validate_dependency_graph(packets: dict[str, Packet]) -> None:
    for packet in packets.values():
        for dependency in packet.depends_on:
            if dependency not in packets:
                raise ProjectStateError(
                    f"packet {packet.packet_id}: unknown dependency {dependency!r}"
                )

    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(packet_id: str) -> None:
        marker = state.get(packet_id, 0)
        if marker == 2:
            return
        if marker == 1:
            start = stack.index(packet_id)
            cycle = stack[start:] + [packet_id]
            raise ProjectStateError(f"packet dependency cycle: {' -> '.join(cycle)}")
        state[packet_id] = 1
        stack.append(packet_id)
        for dependency in sorted(packets[packet_id].depends_on):
            visit(dependency)
        stack.pop()
        state[packet_id] = 2

    for packet_id in sorted(packets):
        visit(packet_id)


def select_next_action(
    packets: dict[str, Packet],
    review_fold: ReviewFold,
    policy: dict[str, Any],
) -> Packet:
    validate_dependency_graph(packets)
    open_findings = review_fold.open_findings
    if not open_findings:
        raise ProjectStateError(
            "routing: no current open finding; passed-freeze transition is unsupported"
        )
    routing_policy = policy["packet_routing"]
    terminal_states = set(routing_policy["terminal_states"])
    satisfied_states = set(routing_policy["dependency_satisfied_states"])
    current_phase = policy["phase_model"]["current_phase_id"]

    matching_packets: dict[str, list[str]] = {finding_id: [] for finding_id in open_findings}
    for packet in packets.values():
        valid_open_addresses: list[str] = []
        for finding_id in packet.addresses_finding_ids:
            finding = open_findings.get(finding_id)
            if finding is None:
                continue
            if packet.action_id not in finding.required_action_ids:
                raise ProjectStateError(
                    f"packet {packet.packet_id}: action {packet.action_id!r} is not "
                    f"required by open finding {finding_id!r}"
                )
            valid_open_addresses.append(finding_id)
        nonterminal = packet.state not in terminal_states
        if packet.phase_id == current_phase and nonterminal:
            for finding_id in valid_open_addresses:
                matching_packets[finding_id].append(packet.packet_id)

    missing_routes = sorted(
        finding_id
        for finding_id, packet_ids in matching_packets.items()
        if not packet_ids
    )
    if missing_routes:
        raise ProjectStateError(
            f"routing: open findings have no nonterminal packet: {missing_routes}"
        )

    direct_target_ids = {
        packet_id
        for packet_ids in matching_packets.values()
        for packet_id in packet_ids
    }
    dependency_closure: set[str] = set()

    def include_dependencies(packet_id: str) -> None:
        if packet_id in dependency_closure:
            return
        dependency_closure.add(packet_id)
        for dependency_id in packets[packet_id].depends_on:
            include_dependencies(dependency_id)

    for target_id in sorted(direct_target_ids):
        include_dependencies(target_id)

    ready: list[Packet] = []
    for packet_id in sorted(dependency_closure):
        packet = packets[packet_id]
        nonterminal = packet.state not in terminal_states
        if nonterminal and packet.phase_id != current_phase:
            raise ProjectStateError(
                f"routing: dependency-frontier packet {packet.packet_id} belongs "
                f"to unsupported phase {packet.phase_id!r}"
            )
        dependencies_satisfied = all(
            packets[dependency].state in satisfied_states
            for dependency in packet.depends_on
        )
        if nonterminal and dependencies_satisfied:
            ready.append(packet)

    if not ready:
        raise ProjectStateError(
            "routing: no ready packet in dependency closure of open-finding targets"
        )
    ready.sort(key=lambda packet: (packet.route_order, packet.packet_id))
    if len(ready) > 1 and ready[0].route_order == ready[1].route_order:
        raise ProjectStateError("routing: minimum route_order is ambiguous")
    return ready[0]


def validate_projection(projection: dict[str, Any]) -> None:
    require_exact_fields(
        projection,
        {"schema_version", "phase", "latest_blocking_review", "next_action", "basis"},
        "projection",
    )
    if projection["schema_version"] != "project-state-view/v1":
        raise ProjectStateError("projection: unsupported schema_version")
    phase = require_exact_fields(
        projection["phase"],
        {"id", "state", "blocking_gate_ids"},
        "projection.phase",
    )
    if phase["id"] != "design_freeze" or phase["state"] != "blocked":
        raise ProjectStateError("projection.phase: V1 must remain blocked design_freeze")
    require_unique_string_list(
        phase["blocking_gate_ids"],
        "projection.phase.blocking_gate_ids",
        allow_empty=False,
    )
    review = require_exact_fields(
        projection["latest_blocking_review"],
        {
            "review_id",
            "review_sequence",
            "subject_candidate_commit",
            "evidence_path",
            "open_finding_ids",
        },
        "projection.latest_blocking_review",
    )
    require_identifier(review["review_id"], "projection review_id")
    if not is_int(review["review_sequence"]) or review["review_sequence"] < 10:
        raise ProjectStateError("projection review_sequence: invalid")
    if (
        not isinstance(review["subject_candidate_commit"], str)
        or GIT_OBJECT_RE.fullmatch(review["subject_candidate_commit"]) is None
    ):
        raise ProjectStateError("projection subject candidate commit: invalid")
    normalize_relative_path(review["evidence_path"], "projection evidence_path")
    require_unique_string_list(
        review["open_finding_ids"],
        "projection open_finding_ids",
        allow_empty=False,
    )
    action = require_exact_fields(
        projection["next_action"],
        {"action_id", "packet_id", "summary"},
        "projection.next_action",
    )
    require_identifier(action["action_id"], "projection action_id")
    if not isinstance(action["packet_id"], str) or PACKET_ID_RE.fullmatch(
        action["packet_id"]
    ) is None:
        raise ProjectStateError("projection packet_id: invalid")
    require_trimmed_string(action["summary"], "projection action summary")
    basis = require_exact_fields(
        projection["basis"],
        {"facts", "state_basis_sha256"},
        "projection.basis",
    )
    if not isinstance(basis["facts"], list) or not basis["facts"]:
        raise ProjectStateError("projection.basis.facts: must be non-empty")
    prior_path: str | None = None
    for index, raw_fact in enumerate(basis["facts"]):
        fact = require_exact_fields(
            raw_fact,
            {"path", "json_pointers", "canonical_sha256"},
            f"projection.basis.facts[{index}]",
        )
        fact_path = normalize_relative_path(fact["path"], f"projection fact[{index}].path")
        if prior_path is not None and fact_path <= prior_path:
            raise ProjectStateError("projection facts: paths must be sorted and unique")
        prior_path = fact_path
        pointers = require_unique_string_list(
            fact["json_pointers"],
            f"projection fact[{index}].json_pointers",
        )
        if pointers != sorted(pointers):
            raise ProjectStateError(
                f"projection fact[{index}]: JSON pointers must be sorted"
            )
        if not isinstance(fact["canonical_sha256"], str) or SHA256_RE.fullmatch(
            fact["canonical_sha256"]
        ) is None:
            raise ProjectStateError(f"projection fact[{index}]: invalid digest")
    if basis["state_basis_sha256"] != canonical_sha256(basis["facts"]):
        raise ProjectStateError("projection.basis: state_basis_sha256 differs")

    forbidden = {
        "head_commit",
        "head_tree",
        "observed_head",
        "observed_tree",
        "generated_at",
        "projection_sha256",
    }

    def reject_forbidden(value: Any) -> None:
        if isinstance(value, dict):
            overlap = forbidden & set(value)
            if overlap:
                raise ProjectStateError(
                    f"projection: forbidden self-referential fields {sorted(overlap)}"
                )
            for child in value.values():
                reject_forbidden(child)
        elif isinstance(value, list):
            for child in value:
                reject_forbidden(child)

    reject_forbidden(projection)


def derive_projection(
    project_root: Path,
    policy_path: Path | None = None,
    *,
    observed_head: str | None = None,
    observed_tree: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Derive project state; runtime Git/time observations are intentionally ignored."""

    del observed_head, observed_tree, generated_at
    try:
        root = project_root.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProjectStateError(f"project root: cannot resolve: {exc}") from exc
    if not root.is_dir():
        raise ProjectStateError("project root: must be a directory")
    raw_policy_path = DEFAULT_POLICY_RELATIVE if policy_path is None else policy_path
    if raw_policy_path.is_absolute():
        try:
            resolved_policy = raw_policy_path.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise ProjectStateError(f"policy: cannot resolve: {exc}") from exc
        if not is_within(resolved_policy, root):
            raise ProjectStateError("policy: must be inside project root")
        policy_relative = resolved_policy.relative_to(root).as_posix()
        policy_file = resolved_policy
    else:
        policy_relative, policy_file = resolve_project_path(
            root,
            raw_policy_path.as_posix(),
            "policy",
            must_exist=True,
        )
    if policy_file.is_symlink() or not policy_file.is_file():
        raise ProjectStateError("policy: must be a real file")
    policy = require_object(load_json(policy_file, "policy"), "policy")
    validate_policy(policy)

    facts = FactSet()
    facts.add_selected(
        policy_relative,
        policy,
        policy["basis"]["policy_json_pointers"],
    )

    contract_source = policy["sources"]["acceptance_contract"]
    contract_relative, contract_path = resolve_project_path(
        root,
        contract_source["path"],
        "acceptance contract",
        must_exist=True,
    )
    contract = require_object(load_json(contract_path, "acceptance contract"), "acceptance contract")
    contract_pointers = contract_source["json_pointers"]
    contract_values = [
        extract_json_pointer(contract, pointer, f"acceptance contract {pointer}")
        for pointer in contract_pointers
    ]
    if contract_values[0] != 1:
        raise ProjectStateError("acceptance contract: unsupported schema_version")
    require_identifier(contract_values[1], "acceptance contract contract_id")
    require_trimmed_string(contract_values[2], "acceptance contract status")
    phase_definition = policy["phase_model"]["supported_phases"][0]
    if contract_values[3] != phase_definition["completion_authority_path"]:
        raise ProjectStateError("acceptance contract: freeze authority binding differs")
    facts.add_selected(contract_relative, contract, contract_pointers)

    review_source = policy["sources"]["review_register"]
    register_relative, register_path = resolve_project_path(
        root,
        review_source["path"],
        "review register",
        must_exist=True,
    )
    register = require_object(load_json(register_path, "review register"), "review register")
    review_fold = fold_reviews(register, policy)
    facts.add_selected(register_relative, register, list(review_fold.fact_pointers))

    packets = discover_packets(root, policy, facts)
    next_packet = select_next_action(packets, review_fold, policy)

    authority_relative, authority_path = resolve_project_path(
        root,
        phase_definition["completion_authority_path"],
        "design-freeze authority",
        must_exist=False,
    )
    authority_exists = authority_path.exists()
    if authority_path.is_symlink():
        raise ProjectStateError("design-freeze authority: symlinks are forbidden")
    if authority_exists and not authority_path.is_file():
        raise ProjectStateError("design-freeze authority: must be a file")
    facts.add_observation(authority_relative, {"exists": authority_exists})

    gates = phase_definition["blocking_gate_ids"]
    blocking_gate_ids: list[str] = []
    if review_fold.open_findings:
        blocking_gate_ids.append(gates["open_findings"])
    if not authority_exists:
        blocking_gate_ids.append(gates["authority_missing"])
    else:
        blocking_gate_ids.append(gates["authority_verification_unsupported"])

    public_facts = facts.public_facts()
    latest = review_fold.latest_blocked
    projection = {
        "schema_version": policy["projection_schema_version"],
        "phase": {
            "id": policy["phase_model"]["current_phase_id"],
            "state": "blocked",
            "blocking_gate_ids": blocking_gate_ids,
        },
        "latest_blocking_review": {
            "review_id": latest["id"],
            "review_sequence": latest["review_sequence"],
            "subject_candidate_commit": latest["candidate_commit"],
            "evidence_path": latest["evidence_path"],
            "open_finding_ids": sorted(review_fold.open_findings),
        },
        "next_action": {
            "action_id": next_packet.action_id,
            "packet_id": next_packet.packet_id,
            "summary": next_packet.summary,
        },
        "basis": {
            "facts": public_facts,
            "state_basis_sha256": canonical_sha256(public_facts),
        },
    }
    validate_projection(projection)
    return projection


def derive_project_state(
    project_root: Path,
    policy_path: Path | None = None,
    **observations: str | None,
) -> dict[str, Any]:
    """Compatibility alias with an explicit name for callers and tests."""

    allowed = {"observed_head", "observed_tree", "generated_at"}
    unexpected = set(observations) - allowed
    if unexpected:
        raise TypeError(f"unexpected observations: {sorted(unexpected)}")
    return derive_projection(project_root, policy_path, **observations)


def render_generated_block(projection: dict[str, Any], policy: dict[str, Any]) -> bytes:
    validate_projection(projection)
    rendering = policy["rendering"]
    body = json.dumps(
        projection,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        indent=2,
    )
    return (
        f"{rendering['start_marker']}\n"
        f"```{rendering['language']}\n"
        f"{body}\n"
        "```\n"
        f"{rendering['end_marker']}"
    ).encode("utf-8")


def locate_generated_block(data: bytes, policy: dict[str, Any], label: str) -> tuple[int, int]:
    start_marker = policy["rendering"]["start_marker"].encode("ascii")
    end_marker = policy["rendering"]["end_marker"].encode("ascii")
    if data.count(start_marker) != 1 or data.count(end_marker) != 1:
        raise ProjectStateError(f"{label}: generated block markers must each occur once")
    start = data.index(start_marker)
    end_start = data.index(end_marker)
    end = end_start + len(end_marker)
    if start >= end_start:
        raise ProjectStateError(f"{label}: generated block markers are reversed")
    if start > 0 and data[start - 1 : start] not in {b"\n", b"\r"}:
        raise ProjectStateError(f"{label}: start marker must begin a line")
    if end < len(data) and data[end : end + 1] not in {b"\n", b"\r"}:
        raise ProjectStateError(f"{label}: end marker must end a line")
    return start, end


def load_policy_for_views(
    project_root: Path,
    policy_path: Path | None,
) -> tuple[Path, dict[str, Any]]:
    root = project_root.resolve(strict=True)
    raw_policy_path = DEFAULT_POLICY_RELATIVE if policy_path is None else policy_path
    path = raw_policy_path if raw_policy_path.is_absolute() else root / raw_policy_path
    resolved = path.resolve(strict=True)
    if not is_within(resolved, root):
        raise ProjectStateError("policy: must be inside project root")
    policy = require_object(load_json(resolved, "policy"), "policy")
    validate_policy(policy)
    return root, policy


def prepare_view_replacements(
    project_root: Path,
    policy: dict[str, Any],
    expected_block: bytes,
) -> tuple[list[str], list[tuple[Path, bytes]]]:
    stale: list[str] = []
    replacements: list[tuple[Path, bytes]] = []
    for raw_view in policy["sources"]["views"]:
        relative, view_path = resolve_project_path(
            project_root,
            raw_view,
            f"view {raw_view}",
            must_exist=True,
        )
        if view_path.is_symlink() or not view_path.is_file():
            raise ProjectStateError(f"view {relative}: must be a real file")
        try:
            data = view_path.read_bytes()
        except OSError as exc:
            raise ProjectStateError(f"view {relative}: cannot read: {exc}") from exc
        start, end = locate_generated_block(data, policy, f"view {relative}")
        if data[start:end] != expected_block:
            stale.append(relative)
            replacements.append((view_path, data[:start] + expected_block + data[end:]))
    return stale, replacements


def check_project_state(
    project_root: Path,
    policy_path: Path | None = None,
) -> dict[str, Any]:
    projection = derive_projection(project_root, policy_path)
    root, policy = load_policy_for_views(project_root, policy_path)
    expected = render_generated_block(projection, policy)
    stale, _ = prepare_view_replacements(root, policy, expected)
    if stale:
        raise ProjectStateError(f"project state views are stale: {stale}")
    return projection


def atomic_replace_bytes(path: Path, content: bytes) -> None:
    original_mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.project-state-",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, original_mode)
        os.replace(temporary, path)
        directory_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def refresh_project_state(
    project_root: Path,
    policy_path: Path | None = None,
) -> dict[str, Any]:
    projection = derive_projection(project_root, policy_path)
    root, policy = load_policy_for_views(project_root, policy_path)
    expected = render_generated_block(projection, policy)
    _, replacements = prepare_view_replacements(root, policy, expected)
    for path, content in replacements:
        atomic_replace_bytes(path, content)
    return projection


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("derive", "check", "refresh"))
    parser.add_argument(
        "--project-root",
        type=Path,
        default=SCRIPT_PROJECT_ROOT,
        help="Project root (defaults to the script's repository root).",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=DEFAULT_POLICY_RELATIVE,
        help="Project-relative policy path.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        if args.mode == "derive":
            projection = derive_projection(args.project_root, args.policy)
            sys.stdout.buffer.write(canonical_json_bytes(projection) + b"\n")
        elif args.mode == "check":
            check_project_state(args.project_root, args.policy)
            print("project state views are fresh")
        else:
            refresh_project_state(args.project_root, args.policy)
            print("project state views refreshed")
    except (ProjectStateError, OSError) as exc:
        print(f"project state derivation failed closed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
