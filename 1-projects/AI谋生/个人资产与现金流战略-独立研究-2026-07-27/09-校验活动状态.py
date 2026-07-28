#!/usr/bin/env python3
"""Fail-closed checks for the active portfolio state.

This checks structure and authorization boundaries.  It does not prove that a
business, demand, return, review, or runtime is valid.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


STATE_PATH = Path(__file__).with_name("08-活动状态.json")
ALLOWED_STATUSES = {
    "active_internal",
    "blocked_internal",
    "blocked_external",
    "stopped",
    "observation_only",
}
ALLOWED_CLAIM_CLASSES = {"observed", "inferred", "unknown", "externally_validated"}
AUTONOMOUS_SCOPES = {
    "public_read_only_research",
    "workspace_read",
    "local_reversible_edit",
    "local_test",
    "paper_simulation",
    "unpublished_draft",
    "independent_review",
}
REQUIRED_APPROVAL_ACTIONS = {
    "external_contact",
    "public_publish_or_deploy",
    "spend_or_purchase",
    "receive_or_refund_payment",
    "contract_or_legal_commitment",
    "live_or_shadow_investment_execution",
    "investment_risk_rule_change",
}


def nonempty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate(state: dict) -> list[str]:
    errors: list[str] = []
    envelope = state.get("authority_envelope", {})
    approval_actions = set(envelope.get("explicit_approval_required", []))
    if not REQUIRED_APPROVAL_ACTIONS.issubset(approval_actions):
        errors.append("authority envelope is missing required approval actions")

    hard = envelope.get("hard_boundaries", {})
    expected_hard = {
        "investment_paper_only": True,
        "investment_human_final": True,
        "broker_connection_allowed": False,
        "live_order_allowed": False,
    }
    if hard != expected_hard:
        errors.append("investment hard boundaries changed or are incomplete")

    workstreams = state.get("workstreams")
    if not isinstance(workstreams, list) or not workstreams:
        return errors + ["workstreams must be a non-empty list"]

    seen_ids: set[str] = set()
    for stream in workstreams:
        stream_id = stream.get("id")
        prefix = f"workstream {stream_id or '<missing>'}:"
        if not isinstance(stream_id, str) or not stream_id.strip():
            errors.append(f"{prefix} missing id")
        elif stream_id in seen_ids:
            errors.append(f"{prefix} duplicate id")
        else:
            seen_ids.add(stream_id)

        if stream.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{prefix} invalid status")
        if not nonempty_list(stream.get("unknowns")):
            errors.append(f"{prefix} unknowns must be explicit and non-empty")
        if not nonempty_list(stream.get("stop_conditions")):
            errors.append(f"{prefix} stop_conditions must be explicit and non-empty")

        facts = stream.get("observed_facts")
        if not isinstance(facts, list) or not facts:
            errors.append(f"{prefix} observed_facts must be non-empty")
        else:
            for index, fact in enumerate(facts):
                fact_prefix = f"{prefix} fact {index}:"
                if fact.get("claim_class") not in ALLOWED_CLAIM_CLASSES:
                    errors.append(f"{fact_prefix} invalid claim_class")
                if not isinstance(fact.get("claim"), str) or not fact["claim"].strip():
                    errors.append(f"{fact_prefix} missing claim")
                if not isinstance(fact.get("evidence_locator"), str) or not fact[
                    "evidence_locator"
                ].strip():
                    errors.append(f"{fact_prefix} missing evidence_locator")

        action = stream.get("next_action", {})
        if action.get("scope") not in AUTONOMOUS_SCOPES:
            errors.append(f"{prefix} next action is outside autonomous scopes")
        if action.get("external_effect") is not False:
            errors.append(f"{prefix} next action must have external_effect=false")
        if action.get("destructive") is not False:
            errors.append(f"{prefix} next action must have destructive=false")

        if stream_id == "investment_discipline":
            safety = stream.get("safety_boundary", {})
            expected_safety = {
                "paper_only": True,
                "human_final": True,
                "live_trading": False,
                "broker_integration": False,
            }
            if safety != expected_safety:
                errors.append(f"{prefix} safety boundary changed or is incomplete")

    approval_queue = state.get("approval_queue")
    if not isinstance(approval_queue, list):
        errors.append("approval_queue must be a list")
    return errors


def main() -> int:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    errors = validate(state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: active state is structurally complete and stays inside the authorization envelope")
    print("NOTE: this does not validate demand, revenue, investment performance, or review acceptance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
