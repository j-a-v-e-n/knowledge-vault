#!/usr/bin/env python3
"""Validate one read-only project-recovery output against an exact bundle.

This runner is deterministic.  It does not call a model, identify a provider, or
grant any permission.  Exit codes distinguish qualification, refusal, stale
inputs, wrong output, and an invalid contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import SchemaError
except ImportError:  # pragma: no cover - exercised only in a missing runtime
    Draft202012Validator = None
    SchemaError = Exception


EXIT_QUALIFIED = 0
EXIT_REFUSED = 2
EXIT_STALE_INPUT = 3
EXIT_WRONG_OUTPUT = 4
EXIT_INVALID_CONTRACT = 5

MUTATION_DESCRIPTOR_TYPE = "OUTPUT_MUTATION_DESCRIPTOR"
MUTATION_EXECUTION_MODE = "MATERIALIZE_DESCRIPTOR_THEN_VALIDATE_OUTPUT"
_RFC3339_TIMESTAMP = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve(base: Path, raw_path: str) -> Path:
    return (base / raw_path).resolve()


def entry_by_role(entries: list[dict[str, Any]], role: str) -> dict[str, Any]:
    matches = [entry for entry in entries if entry.get("role") == role]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {role} entry, found {len(matches)}")
    return matches[0]


def validate_mutation_descriptor(
    descriptor: Any,
    expected_metadata: dict[str, Any] | None = None,
) -> list[str]:
    """Mechanically validate a mutation descriptor and its bound metadata."""

    if not isinstance(descriptor, dict):
        return ["mutation descriptor must be an object"]

    errors: list[str] = []
    required = {
        "fixture_type",
        "base_output",
        "json_pointer",
        "replacement",
        "expected_exit_code",
        "expected_classification",
    }
    missing = sorted(required - set(descriptor))
    if missing:
        errors.append(f"mutation descriptor missing fields: {missing}")
    extra = sorted(set(descriptor) - required)
    if extra:
        errors.append(f"mutation descriptor has unexpected fields: {extra}")

    if descriptor.get("fixture_type") != MUTATION_DESCRIPTOR_TYPE:
        errors.append(f"fixture_type must be {MUTATION_DESCRIPTOR_TYPE}")
    base_output = descriptor.get("base_output")
    if not isinstance(base_output, str) or not base_output:
        errors.append("base_output must be a non-empty string")
    json_pointer = descriptor.get("json_pointer")
    if not isinstance(json_pointer, str) or not json_pointer.startswith("/"):
        errors.append("json_pointer must be a non-root JSON pointer")
    elif re.search(r"~(?:[^01]|$)", json_pointer):
        errors.append("json_pointer contains an invalid escape")
    expected_exit_code = descriptor.get("expected_exit_code")
    if isinstance(expected_exit_code, bool) or not isinstance(expected_exit_code, int):
        errors.append("expected_exit_code must be an integer")
    if not isinstance(descriptor.get("expected_classification"), str):
        errors.append("expected_classification must be a string")

    if expected_metadata is not None:
        if expected_metadata.get("execution_mode") != MUTATION_EXECUTION_MODE:
            errors.append(
                f"mutation fixture execution_mode must be {MUTATION_EXECUTION_MODE}"
            )
        for field in ("expected_exit_code", "expected_classification"):
            if descriptor.get(field) != expected_metadata.get(field):
                errors.append(
                    f"descriptor {field}={descriptor.get(field)!r} does not match "
                    f"fixture metadata {expected_metadata.get(field)!r}"
                )
    return errors


def materialize_mutation_descriptor(
    descriptor_path: Path,
    destination: Path,
) -> dict[str, Any]:
    """Materialize one descriptor into a candidate output without validating it as output."""

    descriptor = load_json(descriptor_path)
    descriptor_errors = validate_mutation_descriptor(descriptor)
    if descriptor_errors:
        raise ValueError("; ".join(descriptor_errors))

    fixture_directory = descriptor_path.parent.resolve()
    base_output_path = (fixture_directory / descriptor["base_output"]).resolve()
    if base_output_path.parent != fixture_directory:
        raise ValueError("base_output must remain within the descriptor directory")
    output = load_json(base_output_path)

    parts = [
        part.replace("~1", "/").replace("~0", "~")
        for part in descriptor["json_pointer"][1:].split("/")
    ]
    target = output
    for part in parts[:-1]:
        if isinstance(target, list):
            if not part.isdigit() or (len(part) > 1 and part.startswith("0")):
                raise ValueError(f"invalid array index in json_pointer: {part!r}")
            target = target[int(part)]
        elif isinstance(target, dict):
            target = target[part]
        else:
            raise ValueError(f"json_pointer traverses a scalar at {part!r}")

    final = parts[-1]
    if isinstance(target, list):
        if not final.isdigit() or (len(final) > 1 and final.startswith("0")):
            raise ValueError(f"invalid array index in json_pointer: {final!r}")
        target[int(final)] = descriptor["replacement"]
    elif isinstance(target, dict):
        if final not in target:
            raise ValueError(f"json_pointer target does not exist: {final!r}")
        target[final] = descriptor["replacement"]
    else:
        raise ValueError("json_pointer target parent is a scalar")

    destination.write_text(json.dumps(output), encoding="utf-8")
    return descriptor


def derive_projection(state: dict[str, Any]) -> dict[str, Any]:
    """Mechanically derive every decision-relevant recovery field from state."""

    opportunity = state["workflow_observations"]["opportunity"]
    investment = state["workflow_observations"]["investment"]
    decision = state["current_decision"]
    primary = state["primary_action"]
    portability = state["model_portability"]
    owner_actions = [
        action["id"]
        for action in state["queued_after_primary"]
        if action["id"] == "PB-ACT-OWNER-CONSTRAINT"
    ]
    if len(owner_actions) != 1:
        raise ValueError("state must contain exactly one PB-ACT-OWNER-CONSTRAINT")
    outcome_candidate_actions = [
        action
        for action in state["queued_after_primary"]
        if action["id"] == "PB-ACT-RECORD-R4-OUTCOME-CANDIDATE"
    ]
    if len(outcome_candidate_actions) != 1:
        raise ValueError(
            "state must contain exactly one PB-ACT-RECORD-R4-OUTCOME-CANDIDATE"
        )
    outcome_candidate = outcome_candidate_actions[0]
    commit_successor_actions = [
        action
        for action in state["queued_after_primary"]
        if action["id"] == "PB-ACT-COMMIT-R4-SUCCESSOR"
    ]
    if len(commit_successor_actions) != 1:
        raise ValueError(
            "state must contain exactly one PB-ACT-COMMIT-R4-SUCCESSOR"
        )
    commit_successor = commit_successor_actions[0]

    return {
        "objective_id": state["objective_id"],
        "objective": state["objective"],
        "objective_conflict_policy": state["objective_conflict_policy"],
        "state_id": state["state_id"],
        "state_status": state["status"],
        "claim_ceiling": state["claim_ceiling"],
        "primary_action": {
            "id": primary["id"],
            "effect_class": primary["effect_class"],
            "owner": primary["owner"],
            "write_set": primary["write_set"],
        },
        "primary_write_action": state["primary_write_action"],
        "background_read_only_ready_set": state["background_read_only_ready_set"],
        "global_prohibitions": sorted(
            key for key, value in state["permissions"].items() if value is False
        ),
        "authority_boundary": {
            "candidate_bound_live_workflow_pointers": state["blueprint_candidate"][
                "candidate_bound_live_workflow_pointers"
            ],
            "cross_task_write_rule": state["authority_contract"]["cross_task_write_rule"],
            "observation_staleness_rule": state["authority_contract"][
                "observation_staleness_rule"
            ],
        },
        "evidence_timeline": {
            "state_as_of": state["as_of"],
            "opportunity_observed_at": opportunity["observed_at"],
            "opportunity_supplemental_c8_observed_at": opportunity[
                "supplemental_c8_observed_at"
            ],
            "opportunity_coordination_receipt_recorded_at": opportunity[
                "coordination_receipt_recorded_at"
            ],
            "investment_observed_at": investment["observed_at"],
            "latest_bound_observation_at": state["temporal_invariants"][
                "latest_bound_observation_at"
            ],
        },
        "workflow_status": {
            "opportunity": {
                "scope": opportunity["scope"],
                "reported_lifecycle": opportunity["reported_lifecycle"],
                "reported_current_decision": opportunity["reported_current_decision"],
                "reported_backtrack": opportunity["reported_backtrack"],
                "reported_next_action_id": opportunity["reported_next_action_id"],
                "observed_state_sha256": opportunity["observed_state_sha256"],
                "observed_control_plane_snapshot_sha256": opportunity[
                    "observed_control_plane_snapshot_sha256"
                ],
                "candidate_dependency": opportunity["candidate_dependency"],
                "coordination_status": opportunity["coordination_status"],
                "portfolio_activation": opportunity["portfolio_activation"],
                "future_local_route_decision": opportunity["future_local_route_decision"],
                "workflow_gates": opportunity["workflow_gates"],
            },
            "investment": {
                "scope": investment["scope"],
                "reported_phase": investment["reported_phase"],
                "reported_state": investment["reported_state"],
                "reported_next_action_id": investment["reported_next_action_id"],
                "observed_state_sha256": investment["observed_state_sha256"],
                "candidate_dependency": investment["candidate_dependency"],
                "portfolio_activation": investment["portfolio_activation"],
                "claim_ceiling": investment["claim_ceiling"],
            },
        },
        "current_decision": {
            "id": decision["id"],
            "parent_id": decision["parent_id"],
            "backtrack_to": decision["backtrack_to"],
            "adjacent_branch_ids": [branch["id"] for branch in decision["adjacent_branches"]],
        },
        "blockers": state["blockers"],
        "review_receipt_transition": {
            "attempt_id": state["review_output_contract"]["attempt_id"],
            "artifact_serialization": state["review_output_contract"][
                "artifact_serialization"
            ],
            "extracted_object_canonicalization": state["review_output_contract"][
                "extracted_object_canonicalization"
            ],
            "checkpoint_order": state["review_output_contract"]["checkpoint_order"],
            "receipt_binding_requirements": state["review_output_contract"][
                "receipt_binding_requirements"
            ],
            "short_circuit_rule": state["review_output_contract"][
                "short_circuit_rule"
            ],
            "verbatim_receipt_paths": state["review_output_contract"][
                "verbatim_receipt_paths"
            ],
            "mutation_rule": state["review_output_contract"]["mutation_rule"],
            "state_transition_rule": state["review_output_contract"][
                "state_transition_rule"
            ],
            "record_outcome_candidate_action": {
                "id": outcome_candidate["id"],
                "effect_class": outcome_candidate["effect_class"],
                "ready": outcome_candidate["ready"],
                "blocked_by": outcome_candidate["blocked_by"],
                "owner": outcome_candidate["owner"],
                "precondition": outcome_candidate["precondition"],
                "write_set": outcome_candidate["write_set"],
                "transition": outcome_candidate["transition"],
            },
            "commit_successor_action": {
                "id": commit_successor["id"],
                "effect_class": commit_successor["effect_class"],
                "ready": commit_successor["ready"],
                "blocked_by": commit_successor["blocked_by"],
                "owner": commit_successor["owner"],
                "precondition": commit_successor["precondition"],
                "write_set": commit_successor["write_set"],
                "transition": commit_successor["transition"],
            },
        },
        "model_portability": {
            "status": portability["status"],
            "first_task_class": portability["first_task_class"],
            "task_class_status": portability["task_class_status"],
            "active_model_qualification": portability["active_model_qualification"],
            "second_provider_qualification": portability["second_provider_qualification"],
        },
        "next_owner_constraint_action_id": owner_actions[0],
    }


def validate_state_timeline(
    state: dict[str, Any],
    opportunity_observation: dict[str, Any],
    c8_observation: dict[str, Any],
    investment_observation: dict[str, Any],
) -> list[str]:
    """Check that state time and projected observation times agree exactly."""

    errors: list[str] = []
    try:
        opportunity = state["workflow_observations"]["opportunity"]
        investment = state["workflow_observations"]["investment"]
        invariant = state["temporal_invariants"]
        state_as_of_gte = invariant["state_as_of_gte_all_bound_observations"]
        timestamp_fields = {
            "state.as_of": state["as_of"],
            "state.opportunity.observed_at": opportunity["observed_at"],
            "state.opportunity.supplemental_c8_observed_at": opportunity[
                "supplemental_c8_observed_at"
            ],
            "state.opportunity.coordination_receipt_recorded_at": opportunity[
                "coordination_receipt_recorded_at"
            ],
            "state.investment.observed_at": investment["observed_at"],
            "observation.opportunity.recorded_at": opportunity_observation[
                "recorded_at"
            ],
            "observation.c8.recorded_at": c8_observation["recorded_at"],
            "observation.opportunity.coordination_receipt.recorded_at": opportunity_observation[
                "coordination"
            ]["post_publication_isolation_receipt"]["recorded_at"],
            "observation.investment.recorded_at": investment_observation["recorded_at"],
            "state.temporal_invariants.latest_bound_observation_at": invariant[
                "latest_bound_observation_at"
            ],
        }
    except (KeyError, TypeError) as exc:
        return [f"invalid timeline structure: {exc}"]

    expected_pairs = [
        (
            "opportunity.observed_at",
            opportunity["observed_at"],
            opportunity_observation["recorded_at"],
        ),
        (
            "opportunity.supplemental_c8_observed_at",
            opportunity["supplemental_c8_observed_at"],
            c8_observation["recorded_at"],
        ),
        (
            "investment.observed_at",
            investment["observed_at"],
            investment_observation["recorded_at"],
        ),
        (
            "opportunity.coordination_receipt_recorded_at",
            opportunity["coordination_receipt_recorded_at"],
            opportunity_observation["coordination"][
                "post_publication_isolation_receipt"
            ]["recorded_at"],
        ),
    ]
    for field, projected, source in expected_pairs:
        if projected != source:
            errors.append(f"{field}={projected!r} does not match source recorded_at={source!r}")

    def parse_rfc3339(value: Any) -> datetime:
        if not isinstance(value, str) or _RFC3339_TIMESTAMP.fullmatch(value) is None:
            raise ValueError(
                "timestamp must use RFC3339 T separator and end with Z or explicit "
                f"timezone offset: {value!r}"
            )
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError(f"timestamp must include timezone offset: {value!r}")
        return parsed

    parsed_fields: dict[str, datetime] = {}
    for field, value in timestamp_fields.items():
        try:
            parsed_fields[field] = parse_rfc3339(value)
        except (TypeError, ValueError) as exc:
            errors.append(f"invalid RFC3339 timestamp at {field}: {exc}")
    if len(parsed_fields) != len(timestamp_fields):
        return errors

    state_as_of = parsed_fields["state.as_of"]
    observation_times = [
        parsed_fields["state.opportunity.observed_at"],
        parsed_fields["state.opportunity.supplemental_c8_observed_at"],
        parsed_fields["state.opportunity.coordination_receipt_recorded_at"],
        parsed_fields["state.investment.observed_at"],
    ]
    latest = max(observation_times)
    if state_as_of < latest:
        errors.append(
            f"state as_of {state['as_of']} precedes latest observation "
            f"{latest.isoformat()}"
        )
    if state_as_of_gte is not True:
        errors.append("state_as_of_gte_all_bound_observations must be true")
    if (
        parsed_fields["state.temporal_invariants.latest_bound_observation_at"]
        != latest
    ):
        errors.append(
            "latest_bound_observation_at does not equal the maximum bound observation time"
        )
    return errors


def validate_contract(manifest_path: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return None, {"classification": "INVALID_CONTRACT", "error": str(exc)}

    required = {
        "schema_version",
        "task_class_id",
        "input_bundle_id",
        "claim_status",
        "input_bundle",
        "contract_artifacts",
        "fixtures",
        "gold_projection",
        "oracle",
    }
    missing = sorted(required - set(manifest))
    if missing:
        return None, {"classification": "INVALID_CONTRACT", "missing": missing}
    if manifest["task_class_id"] != "TASK_PROJECT_RECOVERY_READ_ONLY":
        return None, {
            "classification": "INVALID_CONTRACT",
            "error": "unexpected task_class_id",
        }
    if manifest["claim_status"] != "EXECUTABLE_EVAL_NOT_YET_MODEL_RUN":
        return None, {
            "classification": "INVALID_CONTRACT",
            "error": "claim_status must remain EXECUTABLE_EVAL_NOT_YET_MODEL_RUN",
        }

    base = manifest_path.parent
    groups: list[tuple[str, Any]] = [
        ("input_bundle", manifest["input_bundle"]),
        ("contract_artifacts", manifest["contract_artifacts"]),
        ("fixtures", manifest["fixtures"]),
        ("gold_projection", [manifest["gold_projection"]]),
    ]
    mismatches: list[dict[str, str]] = []
    for group_name, entries in groups:
        if not isinstance(entries, list):
            return None, {
                "classification": "INVALID_CONTRACT",
                "error": f"{group_name} must be a list",
            }
        for entry in entries:
            try:
                target = resolve(base, entry["path"])
                expected = entry["sha256"]
            except (KeyError, TypeError) as exc:
                return None, {
                    "classification": "INVALID_CONTRACT",
                    "error": f"bad {group_name} entry: {exc}",
                }
            if not target.is_file():
                mismatches.append({"path": str(target), "expected": expected, "actual": "MISSING"})
                continue
            actual = sha256_file(target)
            if actual != expected:
                mismatches.append({"path": str(target), "expected": expected, "actual": actual})

    if mismatches:
        return None, {"classification": "STALE_INPUT_BUNDLE", "mismatches": mismatches}

    for entry in manifest["fixtures"]:
        if entry.get("role", "").endswith("_MUTATION_FIXTURE"):
            try:
                descriptor = load_json(resolve(base, entry["path"]))
            except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
                return None, {
                    "classification": "INVALID_CONTRACT",
                    "error": f"invalid mutation descriptor fixture: {exc}",
                }
            descriptor_errors = validate_mutation_descriptor(descriptor, entry)
            if descriptor_errors:
                return None, {
                    "classification": "INVALID_CONTRACT",
                    "error": "mutation descriptor contract failed",
                    "descriptor_errors": descriptor_errors,
                }

    try:
        state_entry = entry_by_role(manifest["input_bundle"], "PORTFOLIO_STATE")
        schema_entry = entry_by_role(manifest["contract_artifacts"], "OUTPUT_SCHEMA")
        state = load_json(resolve(base, state_entry["path"]))
        schema = load_json(resolve(base, schema_entry["path"]))
        gold = load_json(resolve(base, manifest["gold_projection"]["path"]))
        derived = derive_projection(state)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return None, {"classification": "INVALID_CONTRACT", "error": str(exc)}

    try:
        opportunity_observation = load_json(
            resolve(
                base,
                entry_by_role(manifest["input_bundle"], "OPPORTUNITY_CONTROL_PLANE_OBSERVATION")[
                    "path"
                ],
            )
        )
        c8_observation = load_json(
            resolve(
                base,
                entry_by_role(manifest["input_bundle"], "OPPORTUNITY_C8_READ_ONLY_OBSERVATION")[
                    "path"
                ],
            )
        )
        investment_observation = load_json(
            resolve(
                base,
                entry_by_role(manifest["input_bundle"], "INVESTMENT_WORKFLOW_OBSERVATION")[
                    "path"
                ],
            )
        )
        temporal_errors = validate_state_timeline(
            state,
            opportunity_observation,
            c8_observation,
            investment_observation,
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return None, {"classification": "INVALID_CONTRACT", "error": str(exc)}
    if temporal_errors:
        return None, {
            "classification": "INVALID_CONTRACT",
            "error": "state timeline invariant failed",
            "temporal_errors": temporal_errors,
        }

    if gold != derived:
        return None, {
            "classification": "INVALID_CONTRACT",
            "error": "gold projection is not the mechanical projection of the bound state",
            "expected_from_state": derived,
            "actual_gold": gold,
        }
    if Draft202012Validator is None:
        return None, {
            "classification": "INVALID_CONTRACT",
            "error": "jsonschema dependency is unavailable",
        }
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        return None, {"classification": "INVALID_CONTRACT", "error": str(exc)}

    manifest["_resolved_schema"] = schema
    manifest["_derived_gold"] = derived
    return manifest, {"classification": "CONTRACT_VALID"}


def validate_output(manifest_path: Path, output_path: Path) -> tuple[int, dict[str, Any]]:
    manifest, contract_result = validate_contract(manifest_path)
    if manifest is None:
        code = (
            EXIT_STALE_INPUT
            if contract_result["classification"] == "STALE_INPUT_BUNDLE"
            else EXIT_INVALID_CONTRACT
        )
        return code, contract_result

    try:
        output = load_json(output_path)
    except (OSError, json.JSONDecodeError) as exc:
        return EXIT_WRONG_OUTPUT, {"classification": "SCHEMA_INVALID", "error": str(exc)}

    errors = sorted(
        Draft202012Validator(manifest["_resolved_schema"]).iter_errors(output),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        return EXIT_WRONG_OUTPUT, {
            "classification": "SCHEMA_INVALID",
            "errors": [
                {
                    "path": "/" + "/".join(str(item) for item in error.absolute_path),
                    "message": error.message,
                }
                for error in errors
            ],
        }

    if output.get("qualification_status") == "REFUSED":
        return EXIT_REFUSED, {
            "classification": "NOT_QUALIFIED_REFUSAL",
            "task_class_id": manifest["task_class_id"],
            "reason": output["reason"],
        }

    if output["task_class_id"] != manifest["task_class_id"]:
        return EXIT_WRONG_OUTPUT, {
            "classification": "WRONG_TASK_CLASS",
            "expected": manifest["task_class_id"],
            "actual": output["task_class_id"],
        }
    if output["input_bundle_id"] != manifest["input_bundle_id"]:
        return EXIT_WRONG_OUTPUT, {
            "classification": "WRONG_INPUT_BUNDLE",
            "expected": manifest["input_bundle_id"],
            "actual": output["input_bundle_id"],
        }
    if output["projection"] != manifest["_derived_gold"]:
        return EXIT_WRONG_OUTPUT, {
            "classification": "WRONG_STATE_PROJECTION",
            "expected": manifest["_derived_gold"],
            "actual": output["projection"],
        }

    return EXIT_QUALIFIED, {
        "classification": "EVAL_QUALIFIED_CANDIDATE_OUTPUT",
        "task_class_id": manifest["task_class_id"],
        "input_bundle_id": manifest["input_bundle_id"],
        "claim_ceiling": "READ_ONLY_PROJECT_RECOVERY_FOR_THIS_EXACT_BUNDLE_ONLY",
        "note": "This validator does not identify the provider/model/adapter or grant run, write, market, account, payment, contract, or investment authority.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    code, result = validate_output(args.manifest.resolve(), args.output.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
