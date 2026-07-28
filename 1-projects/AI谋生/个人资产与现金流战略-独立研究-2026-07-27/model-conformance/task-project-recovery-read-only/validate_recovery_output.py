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

    return {
        "objective_id": state["objective_id"],
        "objective": state["objective"],
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
        "workflow_status": {
            "opportunity": {
                "scope": opportunity["scope"],
                "reported_lifecycle": opportunity["reported_lifecycle"],
                "reported_current_decision": opportunity["reported_current_decision"],
                "reported_backtrack": opportunity["reported_backtrack"],
                "reported_next_action_id": opportunity["reported_next_action_id"],
                "observed_state_sha256": opportunity["observed_state_sha256"],
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
        "review_receipt_paths": state["review_output_contract"]["verbatim_receipt_paths"],
        "model_portability": {
            "status": portability["status"],
            "first_task_class": portability["first_task_class"],
            "task_class_status": portability["task_class_status"],
            "active_model_qualification": portability["active_model_qualification"],
            "second_provider_qualification": portability["second_provider_qualification"],
        },
        "next_owner_constraint_action_id": owner_actions[0],
    }


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

    try:
        state_entry = entry_by_role(manifest["input_bundle"], "PORTFOLIO_STATE")
        schema_entry = entry_by_role(manifest["contract_artifacts"], "OUTPUT_SCHEMA")
        state = load_json(resolve(base, state_entry["path"]))
        schema = load_json(resolve(base, schema_entry["path"]))
        gold = load_json(resolve(base, manifest["gold_projection"]["path"]))
        derived = derive_projection(state)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return None, {"classification": "INVALID_CONTRACT", "error": str(exc)}

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
