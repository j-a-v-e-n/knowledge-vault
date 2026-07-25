#!/usr/bin/env python3
"""Evaluate conditional-gate state without converting missing prerequisites to green claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
CONTRACT = PROJECT_ROOT / "governance" / "ACCEPTANCE_CONTRACT_V1.json"


def load_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"conditional evidence must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def runtime_observation(
    gate: dict[str, Any], runtime_db: Path | None
) -> tuple[bool, str | None, dict[str, Any], list[str]]:
    if runtime_db is None or not runtime_db.is_file():
        return False, None, {"source": "runtime_database_absent"}, []
    errors: list[str] = []
    row: tuple[Any, ...] | None = None
    try:
        connection = sqlite3.connect(f"file:{runtime_db}?mode=ro", uri=True)
        try:
            row = connection.execute(
                "SELECT condition_id, stage, ready, source_event_seq, "
                "source_state_hash, observed_at "
                "FROM condition_observations WHERE condition_id = ? "
                "ORDER BY source_event_seq DESC LIMIT 1",
                (gate["id"],),
            ).fetchone()
        finally:
            connection.close()
    except sqlite3.Error as exc:
        return (
            False,
            None,
            {"source": "runtime_sqlite_event_chain"},
            [f"authoritative_runtime_probe_failed:{exc}"],
        )
    if row is None:
        return False, None, {"source": "runtime_sqlite_event_chain"}, []
    observation = {
        "condition_id": row[0],
        "stage": row[1],
        "ready": bool(row[2]),
        "source_event_seq": row[3],
        "source_state_hash": row[4],
        "observed_at": row[5],
        "source": "runtime_sqlite_event_chain",
    }
    if (
        observation["condition_id"] != gate["id"]
        or not isinstance(observation["stage"], str)
        or not isinstance(observation["source_event_seq"], int)
        or observation["source_event_seq"] < 1
        or not isinstance(observation["source_state_hash"], str)
        or not re.fullmatch(r"[0-9a-f]{64}", observation["source_state_hash"])
        or not isinstance(observation["observed_at"], str)
        or not observation["observed_at"]
    ):
        errors.append("authoritative_runtime_observation_invalid")
    ready_when = gate["prerequisite_probe"]["ready_when"]
    stage = observation["stage"]
    stage_matches = (
        stage == ready_when.get("stage")
        if "stage" in ready_when
        else stage in set(ready_when.get("stage_in", []))
    )
    ready = (
        not errors
        and observation["ready"] is ready_when.get("ready")
        and stage_matches
    )
    return ready, stage, observation, errors


def observe_prerequisite(
    gate: dict[str, Any],
    contract: dict[str, Any],
    runtime_db: Path | None,
) -> tuple[bool, str | None, dict[str, Any], list[str]]:
    authority = gate["prerequisite_probe"]["authority"]
    if authority == "process_environment_presence":
        present = bool(os.environ.get("TIINGO_API_TOKEN"))
        return present, "live_probe" if present else None, {
            "source": authority,
            "present": present,
            "secret_value_read": False,
        }, []
    if authority == "frozen_contract_scope":
        forbidden_scope = "真实资金、live broker、实盘凭据或自动下单"
        satisfied = forbidden_scope in set(contract.get("non_goals", []))
        return satisfied, "scope" if satisfied else None, {
            "source": authority,
            "forbidden_scope_present": satisfied,
        }, []
    if authority == "runtime_sqlite_event_chain":
        return runtime_observation(gate, runtime_db)
    return False, None, {"source": authority}, ["unknown_prerequisite_authority"]


def required_stage(gate_id: str, observed_stage: str | None) -> str | None:
    if gate_id == "COND-TIINGO-LIVE-PROBE":
        return "live_probe"
    if gate_id == "COND-LONGITUDINAL-EDGE":
        return "future_window"
    if gate_id == "COND-JAVEN-FIELD-USE":
        return {
            "human_onboarding_ready": "human_onboarding",
            "longitudinal_window_ready": "longitudinal",
        }.get(observed_stage)
    return observed_stage


def validate_gate_evidence(
    gate: dict[str, Any],
    gate_catalog: dict[str, dict[str, Any]],
    evidence_schema: dict[str, Any],
    evidence: dict[str, Any],
    stage: str | None,
    candidate_commit: str | None,
    candidate_tree: str | None,
    frozen_bundle_sha256: str | None,
) -> list[str]:
    errors: list[str] = []
    required = set(evidence_schema.get("required", []))
    missing = required - set(evidence)
    if missing:
        errors.append(f"gate_evidence_missing_fields:{','.join(sorted(missing))}")
        return errors
    if "prerequisite_ready" in evidence:
        errors.append("gate_evidence_must_not_report_prerequisite_readiness")
    mandatory_gate = gate["mandatory_gate_when_ready"]
    catalog_entry = gate_catalog.get(mandatory_gate, {})
    if evidence.get("condition_id") != gate["id"]:
        errors.append("condition_id_mismatch")
    if evidence.get("gate_id") != mandatory_gate:
        errors.append("gate_id_mismatch")
    if evidence.get("state") not in set(evidence_schema.get("state_enum", [])):
        errors.append("state_not_allowed")
    expected_stage = required_stage(gate["id"], stage)
    if evidence.get("gate_stage") != expected_stage:
        errors.append("gate_stage_mismatch")
    for field, expected, pattern in (
        ("candidate_commit", candidate_commit, r"[0-9a-f]{40}"),
        ("candidate_tree", candidate_tree, r"[0-9a-f]{40}"),
        ("frozen_bundle_sha256", frozen_bundle_sha256, r"[0-9a-f]{64}"),
    ):
        actual = evidence.get(field)
        if not isinstance(actual, str) or not re.fullmatch(pattern, actual):
            errors.append(f"{field}_invalid")
        elif expected is not None and actual != expected:
            errors.append(f"{field}_mismatch")
    executors = evidence.get("executor_ids")
    if (
        not isinstance(executors, list)
        or set(executors) != set(catalog_entry.get("executor_ids", []))
    ):
        errors.append("gate_executor_binding_mismatch")
    required_cases = set(
        gate.get("required_acceptance_case_ids_by_stage", {}).get(
            expected_stage or "", []
        )
    )
    evidence_cases = evidence.get("acceptance_case_ids")
    if (
        not isinstance(evidence_cases, list)
        or not required_cases.issubset(set(evidence_cases))
    ):
        errors.append("gate_acceptance_case_binding_mismatch")
    raw_relative = evidence.get("raw_result_path")
    raw_hash = evidence.get("raw_result_sha256")
    if (
        not isinstance(raw_relative, str)
        or Path(raw_relative).is_absolute()
        or ".." in Path(raw_relative).parts
    ):
        errors.append("raw_result_path_invalid")
    else:
        raw_path = PROJECT_ROOT / raw_relative
        if not raw_path.is_file():
            errors.append("raw_result_missing")
        elif not isinstance(raw_hash, str) or sha256_file(raw_path) != raw_hash:
            errors.append("raw_result_hash_mismatch")
    return errors


def evaluate(
    gate: dict[str, Any],
    contract: dict[str, Any],
    gate_catalog: dict[str, dict[str, Any]],
    runtime_db: Path | None,
    target_verdict: str,
    candidate_commit: str | None,
    candidate_tree: str | None,
    frozen_bundle_sha256: str | None,
) -> dict[str, Any]:
    gate_id = gate["id"]
    evidence_path = PROJECT_ROOT / gate["evidence_path"]
    evidence = load_optional(evidence_path)
    ready, stage, prerequisite_observation, errors = observe_prerequisite(
        gate, contract, runtime_db
    )
    allowed_states = set(gate["allowed_states"])
    transitions = gate["transition_table"]

    if not ready:
        effective_state = transitions["not_ready"]
        if evidence is not None:
            errors.append("gate_evidence_present_without_authoritative_prerequisite")
    else:
        mandatory_gate = gate["mandatory_gate_when_ready"]
        if mandatory_gate is None:
            effective_state = transitions["ready_without_valid_gate_evidence"]
        elif evidence is None:
            errors.append("prerequisite_ready_but_evidence_missing")
            effective_state = transitions["ready_without_valid_gate_evidence"]
        else:
            errors.extend(
                validate_gate_evidence(
                    gate,
                    gate_catalog,
                    contract["conditional_evidence_schema"],
                    evidence,
                    stage,
                    candidate_commit,
                    candidate_tree,
                    frozen_bundle_sha256,
                )
            )
            state = evidence.get("state")
            effective_state = {
                "passed": transitions.get("gate_pass"),
                "failed": transitions.get("gate_fail"),
                "inconclusive": transitions.get("gate_inconclusive"),
            }.get(state, transitions["ready_without_valid_gate_evidence"])
            if errors:
                effective_state = transitions["ready_without_valid_gate_evidence"]

    if effective_state not in allowed_states:
        errors.append("effective_state_not_allowed")

    if gate_id == "COND-JAVEN-FIELD-USE" and target_verdict in {
        "human_onboarding_verified",
        "longitudinal_personal_validation",
    }:
        target_rule = gate["release_mapping"][target_verdict]
        if (
            stage != target_rule["required_probe_stage"]
            or effective_state != target_rule["required_state"]
            or not evidence
            or evidence.get("gate_stage") != target_rule["required_gate_stage"]
        ):
            errors.append("target_verdict_requirements_not_met")

    return {
        "condition_id": gate_id,
        "prerequisite_ready": ready,
        "prerequisite_stage": stage,
        "prerequisite_observation": prerequisite_observation,
        "evidence_path": gate["evidence_path"],
        "effective_state": effective_state,
        "must_not_be_claimed": gate["must_not_be_claimed"],
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", help="evaluate one conditional gate id")
    parser.add_argument("--runtime-db")
    parser.add_argument(
        "--target-verdict",
        choices=[
            "core_release_candidate",
            "human_onboarding_verified",
            "longitudinal_personal_validation",
        ],
        default="core_release_candidate",
    )
    parser.add_argument("--candidate-commit")
    parser.add_argument("--candidate-tree")
    parser.add_argument("--frozen-bundle-sha256")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gates = contract.get("conditional_gates", [])
    selected = [gate for gate in gates if not args.gate or gate.get("id") == args.gate]
    if args.gate and not selected:
        print(f"unknown conditional gate: {args.gate}", file=sys.stderr)
        return 2
    runtime_value = args.runtime_db or os.environ.get("IDS_RUNTIME_DB")
    runtime_db = Path(runtime_value).expanduser().resolve() if runtime_value else None
    gate_catalog = {
        gate["id"]: gate
        for gate in contract.get("conditional_gate_catalog", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    results = [
        evaluate(
            gate,
            contract,
            gate_catalog,
            runtime_db,
            args.target_verdict,
            args.candidate_commit,
            args.candidate_tree,
            args.frozen_bundle_sha256,
        )
        for gate in selected
    ]
    failed = [result for result in results if result["status"] == "fail"]
    unresolved_states = {
        "not_run_missing_user_credential",
        "not_yet_observable",
        "inconclusive",
    }
    aggregate_verdict = (
        "blocked"
        if failed
        else (
            args.target_verdict
            if args.target_verdict != "core_release_candidate"
            else (
                "core_pass_with_unproven_conditions"
                if any(
                    result["effective_state"] in unresolved_states for result in results
                )
                else "all_selected_conditions_passed"
            )
        )
    )
    payload = {
        "schema_version": 1,
        "status": "fail" if failed else "pass",
        "aggregate_verdict": aggregate_verdict,
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"conditional verification: {payload['status'].upper()} "
            f"(aggregate={aggregate_verdict})"
        )
        for result in results:
            print(
                f"- {result['condition_id']}: {result['effective_state']} "
                f"(prerequisite_ready={result['prerequisite_ready']})"
            )
            for error in result["errors"]:
                print(f"  error: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
