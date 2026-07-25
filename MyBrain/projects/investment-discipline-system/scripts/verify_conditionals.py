#!/usr/bin/env python3
"""Evaluate conditional-gate state without converting missing prerequisites to green claims."""

from __future__ import annotations

import argparse
import json
import os
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


def observed_prerequisite(gate_id: str, evidence: dict[str, Any] | None) -> bool:
    if gate_id == "COND-TIINGO-LIVE-PROBE":
        return bool(os.environ.get("TIINGO_API_TOKEN"))
    if gate_id == "COND-EXTERNAL-PAPER":
        return False
    return bool(evidence and evidence.get("prerequisite_ready") is True)


def evaluate(gate: dict[str, Any]) -> dict[str, Any]:
    gate_id = gate["id"]
    evidence_path = PROJECT_ROOT / gate["evidence_path"]
    evidence = load_optional(evidence_path)
    ready = observed_prerequisite(gate_id, evidence)
    allowed_states = set(gate["allowed_states"])
    errors: list[str] = []

    if evidence is not None and evidence.get("condition_id") != gate_id:
        errors.append("condition_id_mismatch")
    state = evidence.get("state") if evidence else None
    if state is not None and state not in allowed_states:
        errors.append("state_not_allowed")

    if not ready:
        expected = gate["when_prerequisite_absent"]
        if state is not None and state != expected:
            errors.append("state_conflicts_with_absent_prerequisite")
        effective_state = state or expected
    else:
        if evidence is None:
            errors.append("prerequisite_ready_but_evidence_missing")
            effective_state = "mandatory_pending"
        elif state in {None, "mandatory_pending"}:
            errors.append("prerequisite_ready_but_mandatory_gate_pending")
            effective_state = "mandatory_pending"
        else:
            effective_state = state

    if gate_id == "COND-EXTERNAL-PAPER" and effective_state != "out_of_scope":
        errors.append("external_paper_must_remain_out_of_scope")

    return {
        "condition_id": gate_id,
        "prerequisite_ready": ready,
        "evidence_path": gate["evidence_path"],
        "effective_state": effective_state,
        "must_not_be_claimed": gate["must_not_be_claimed"],
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", help="evaluate one conditional gate id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gates = contract.get("conditional_gates", [])
    selected = [gate for gate in gates if not args.gate or gate.get("id") == args.gate]
    if args.gate and not selected:
        print(f"unknown conditional gate: {args.gate}", file=sys.stderr)
        return 2
    results = [evaluate(gate) for gate in selected]
    failed = [result for result in results if result["status"] == "fail"]
    unresolved_states = {
        "not_run_missing_user_credential",
        "not_yet_observable",
        "out_of_scope",
        "inconclusive",
    }
    aggregate_verdict = (
        "blocked"
        if failed
        else (
            "core_pass_with_unproven_conditions"
            if any(result["effective_state"] in unresolved_states for result in results)
            else "all_selected_conditions_passed"
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
