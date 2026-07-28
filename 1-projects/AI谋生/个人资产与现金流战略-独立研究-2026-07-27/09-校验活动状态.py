#!/usr/bin/env python3
"""Fail-closed checks for the active portfolio state.

This validator checks structure, local evidence identity, and authorization
boundaries. It does not prove demand, payment, delivery, profit, investment
performance, review quality, or runtime correctness.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parent
STATE_PATH = RESEARCH_ROOT / "08-活动状态.json"
LEGACY_OPPORTUNITY_ROOT = (RESEARCH_ROOT.parent / "机会到交易系统").resolve()
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
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
    "private_account_or_credential_use",
    "nonpublic_third_party_data_use",
    "new_external_integration",
    "live_or_shadow_investment_execution",
    "investment_risk_rule_change",
}
REQUIRED_FALSE_EXPERIMENT_AUTHORITY = {
    "external_contact_authorized",
    "quote_authorized",
    "account_access_authorized",
    "submission_authorized",
    "payment_action_authorized",
    "delivery_harness_authorized",
}
REQUIRED_FALSE_EXPERIMENT_RESULTS = {
    "externally_validated_demand",
    "willingness_to_pay",
    "delivery_feasible",
    "profitable",
    "repeatable",
    "asset_candidate",
}
REQUIRED_CA_MISSING_BINDINGS = {
    "sender_account",
    "observation_cutoff_at",
    "pre_send_source_refresh",
    "exact_user_authorization",
}
EXPECTED_INVESTMENT_IDENTITY = {
    "commit": "fed7d6694dc1b47490848b83e3ff0b56e04a3f39",
    "tree": "2da5f0af186345da05738f971cb8afbdb6dac8db",
    "parent": "d8c108f81f84f4c5be99fe09902ace161bda5745",
}


def nonempty_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate_not_future(value: object, *, errors: list[str], label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: missing timestamp")
        return
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: invalid RFC 3339 timestamp")
        return
    if parsed.tzinfo is None:
        errors.append(f"{label}: timestamp must include an offset")
        return
    if parsed.astimezone(timezone.utc) > datetime.now(timezone.utc):
        errors.append(f"{label}: timestamp is in the future")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def confined_file(
    raw_path: object,
    *,
    base: Path,
    errors: list[str],
    label: str,
    allowed_root: Path = RESEARCH_ROOT,
) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{label}: missing path")
        return None
    candidate = Path(raw_path)
    try:
        resolved = (candidate if candidate.is_absolute() else base / candidate).resolve(
            strict=True
        )
    except (OSError, RuntimeError):
        errors.append(f"{label}: path does not resolve")
        return None
    if resolved != allowed_root and allowed_root not in resolved.parents:
        errors.append(f"{label}: path escapes its allowed evidence root")
        return None
    if not resolved.is_file():
        errors.append(f"{label}: path is not a regular file")
        return None
    return resolved


def verify_bound_file(
    binding: object,
    *,
    base: Path,
    errors: list[str],
    label: str,
    allowed_root: Path = RESEARCH_ROOT,
) -> Path | None:
    if not isinstance(binding, dict):
        errors.append(f"{label}: binding must be an object")
        return None
    path = confined_file(
        binding.get("path"),
        base=base,
        errors=errors,
        label=label,
        allowed_root=allowed_root,
    )
    expected = binding.get("sha256")
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        errors.append(f"{label}: sha256 must be an exact lowercase digest")
        return path
    if path is not None and sha256_file(path) != expected:
        errors.append(f"{label}: sha256 mismatch")
    return path


def load_json(path: Path, *, errors: list[str], label: str) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        errors.append(f"{label}: unreadable or invalid JSON")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: JSON root must be an object")
        return None
    return value


def validate_experiment(stream: dict, errors: list[str]) -> dict | None:
    prefix = "opportunity experiment:"
    current = stream.get("current_experiment")
    if not isinstance(current, dict):
        errors.append(f"{prefix} current_experiment must be an object")
        return None
    spec_binding = {
        "path": current.get("spec_path"),
        "sha256": current.get("spec_sha256"),
    }
    spec_path = verify_bound_file(
        spec_binding, base=RESEARCH_ROOT, errors=errors, label=f"{prefix} spec"
    )
    if spec_path is None:
        return None
    experiment = load_json(spec_path, errors=errors, label=f"{prefix} spec")
    if experiment is None:
        return None

    if experiment.get("experiment_id") != current.get("experiment_id"):
        errors.append(f"{prefix} experiment_id mismatch")
    validate_not_future(
        experiment.get("captured_at"), errors=errors, label=f"{prefix} captured_at"
    )
    validate_not_future(
        experiment.get("internal_review_recorded_at"),
        errors=errors,
        label=f"{prefix} internal_review_recorded_at",
    )
    try:
        captured_at = datetime.fromisoformat(experiment["captured_at"])
        reviewed_at = datetime.fromisoformat(experiment["internal_review_recorded_at"])
        if reviewed_at < captured_at:
            errors.append(f"{prefix} internal review predates candidate capture")
    except (KeyError, TypeError, ValueError):
        pass
    if experiment.get("status") != "blocked_before_external_action":
        errors.append(f"{prefix} experiment must remain blocked before external action")
    if current.get("external_action_status") != "blocked":
        errors.append(f"{prefix} external action status must remain blocked")
    if current.get("external_contact_authorized") is not False:
        errors.append(f"{prefix} state must keep external_contact_authorized=false")

    authority = experiment.get("authority")
    if not isinstance(authority, dict):
        errors.append(f"{prefix} authority must be an object")
    else:
        if authority.get("internal_research_authorized") is not True:
            errors.append(f"{prefix} internal research authority is not explicit")
        for key in sorted(REQUIRED_FALSE_EXPERIMENT_AUTHORITY):
            if authority.get(key) is not False:
                errors.append(f"{prefix} authority {key} must be false")

    sender = experiment.get("sender_binding")
    if not isinstance(sender, dict):
        errors.append(f"{prefix} sender_binding must be an object")
    elif sender.get("sending_account") is not None or sender.get(
        "sending_account_status"
    ) != "unbound":
        errors.append(f"{prefix} sending account must remain unbound")
    if experiment.get("observation_cutoff_at") is not None:
        errors.append(f"{prefix} observation cutoff must remain unbound")

    bound_inputs = experiment.get("bound_inputs")
    if not isinstance(bound_inputs, list) or not bound_inputs:
        errors.append(f"{prefix} bound_inputs must be a non-empty list")
    else:
        seen_paths: set[Path] = set()
        for index, binding in enumerate(bound_inputs):
            bound_path = verify_bound_file(
                binding,
                base=spec_path.parent,
                errors=errors,
                label=f"{prefix} bound_inputs[{index}]",
            )
            if bound_path is not None:
                if bound_path in seen_paths:
                    errors.append(f"{prefix} duplicate bound input path")
                seen_paths.add(bound_path)

    results = experiment.get("result_claims")
    if not isinstance(results, dict):
        errors.append(f"{prefix} result_claims must be an object")
    else:
        if not REQUIRED_FALSE_EXPERIMENT_RESULTS.issubset(results):
            errors.append(f"{prefix} required result claims are missing")
        for key, value in results.items():
            if value is not False:
                errors.append(f"{prefix} result claim {key} must be false")
        if current.get("result_claims") != results:
            errors.append(f"{prefix} state result_claims do not match bound experiment")

    external_gate = [
        gate
        for gate in experiment.get("gate_results", [])
        if isinstance(gate, dict) and gate.get("gate") == "external_action"
    ]
    if len(external_gate) != 1 or external_gate[0].get("result") != "blocked":
        errors.append(f"{prefix} external_action gate must be uniquely blocked")
    return experiment


def validate_review_receipts(stream: dict, errors: list[str]) -> None:
    prefix = "opportunity independent reviews:"
    reviews = stream.get("independent_reviews")
    required_keys = {
        "legacy_runtime_tombstone",
        "ca012650_internal_candidate",
    }
    if not isinstance(reviews, dict) or set(reviews) != required_keys:
        errors.append(f"{prefix} exact review receipt set is missing or changed")
        return

    loaded: dict[str, tuple[Path, dict]] = {}
    for key in sorted(required_keys):
        state_binding = reviews.get(key)
        receipt_path = verify_bound_file(
            state_binding,
            base=RESEARCH_ROOT,
            errors=errors,
            label=f"{prefix} {key}",
        )
        if not isinstance(state_binding, dict) or state_binding.get("verdict") != "PASS":
            errors.append(f"{prefix} {key} state verdict must be PASS")
        if receipt_path is None:
            continue
        receipt = load_json(
            receipt_path, errors=errors, label=f"{prefix} {key} receipt"
        )
        if receipt is None:
            continue
        loaded[key] = (receipt_path, receipt)
        if receipt.get("verdict") != "PASS":
            errors.append(f"{prefix} {key} receipt verdict must be PASS")
        if receipt.get("reviewer_role") != "independent_read_only_subagent":
            errors.append(f"{prefix} {key} reviewer role changed")
        if receipt.get("reviewer_modified_candidate") is not False:
            errors.append(f"{prefix} {key} reviewer must not modify candidate")
        validate_not_future(
            receipt.get("recorded_at"),
            errors=errors,
            label=f"{prefix} {key} recorded_at",
        )

    ca_pair = loaded.get("ca012650_internal_candidate")
    if ca_pair is not None:
        ca_path, ca_receipt = ca_pair
        ca_bindings = ca_receipt.get("candidate_bindings")
        expected_ca_paths = {
            (RESEARCH_ROOT / "03-否决门与反方审查.md").resolve(),
            (RESEARCH_ROOT / "07-自主运行协议.md").resolve(),
            (RESEARCH_ROOT / "10-现实候选预筛与首个反证实验.md").resolve(),
            (RESEARCH_ROOT / "11-内部诊断页-CA012650.md").resolve(),
            (RESEARCH_ROOT / "12-首个反证实验与对外动作候选.md").resolve(),
            (RESEARCH_ROOT / "evidence/cec-building-benchmarking-prescreen-2026-07-27.json").resolve(),
            (RESEARCH_ROOT / "evidence/experiment-ca012650-internal-2026-07-27.json").resolve(),
        }
        observed_ca_paths: set[Path] = set()
        if not isinstance(ca_bindings, list):
            errors.append(f"{prefix} CA receipt candidate_bindings must be a list")
        else:
            for index, binding in enumerate(ca_bindings):
                bound_path = verify_bound_file(
                    binding,
                    base=ca_path.parent,
                    errors=errors,
                    label=f"{prefix} CA candidate[{index}]",
                )
                if bound_path is not None:
                    observed_ca_paths.add(bound_path)
        if observed_ca_paths != expected_ca_paths:
            errors.append(f"{prefix} CA receipt does not bind the exact review candidate")
        if ca_receipt.get("external_action_status") != "BLOCKED_NOT_AUTHORIZED":
            errors.append(f"{prefix} CA receipt external action must remain blocked")
        expected_missing = {
            "sending_account",
            "observation_cutoff_at",
            "pre_send_source_refresh",
            "exact_one_message_user_authorization",
        }
        if set(ca_receipt.get("missing_external_bindings", [])) != expected_missing:
            errors.append(f"{prefix} CA receipt missing external bindings changed")

    legacy_pair = loaded.get("legacy_runtime_tombstone")
    if legacy_pair is not None:
        legacy_path, legacy_receipt = legacy_pair
        raw_root = legacy_receipt.get("candidate_root")
        try:
            resolved_root = (legacy_path.parent / raw_root).resolve(strict=True)
        except (OSError, RuntimeError, TypeError):
            resolved_root = None
            errors.append(f"{prefix} legacy candidate root does not resolve")
        if resolved_root != LEGACY_OPPORTUNITY_ROOT:
            errors.append(f"{prefix} legacy candidate root changed")
        legacy_bindings = legacy_receipt.get("candidate_bindings")
        expected_legacy_paths = {
            (LEGACY_OPPORTUNITY_ROOT / "src/opportunity_os.py").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "tests/test_opportunity_os.py").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "README.md").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "LEGACY_STATUS.md").resolve(),
            (LEGACY_OPPORTUNITY_ROOT / "LEGACY_CODE_GAP_AUDIT.md").resolve(),
        }
        observed_legacy_paths: set[Path] = set()
        if not isinstance(legacy_bindings, list):
            errors.append(f"{prefix} legacy receipt candidate_bindings must be a list")
        else:
            for index, binding in enumerate(legacy_bindings):
                bound_path = verify_bound_file(
                    binding,
                    base=LEGACY_OPPORTUNITY_ROOT,
                    errors=errors,
                    label=f"{prefix} legacy candidate[{index}]",
                    allowed_root=LEGACY_OPPORTUNITY_ROOT,
                )
                if bound_path is not None:
                    observed_legacy_paths.add(bound_path)
        if observed_legacy_paths != expected_legacy_paths:
            errors.append(f"{prefix} legacy receipt does not bind the exact tombstone candidate")


def validate_investment_audit(stream: dict, errors: list[str]) -> None:
    prefix = "investment audit:"
    binding = stream.get("candidate_audit")
    audit_path = verify_bound_file(
        binding, base=RESEARCH_ROOT, errors=errors, label=f"{prefix} evidence"
    )
    if audit_path is None:
        return
    audit = load_json(audit_path, errors=errors, label=f"{prefix} evidence")
    if audit is None:
        return
    identity = audit.get("candidate_identity")
    if not isinstance(identity, dict) or any(
        identity.get(key) != value for key, value in EXPECTED_INVESTMENT_IDENTITY.items()
    ):
        errors.append(f"{prefix} exact commit/tree/parent identity mismatch")
    if audit.get("overall_acceptance") != "blocked_internal":
        errors.append(f"{prefix} overall acceptance must remain blocked_internal")
    claims = audit.get("result_claims")
    if not isinstance(claims, dict) or not claims or any(
        value is not False for value in claims.values()
    ):
        errors.append(f"{prefix} all result claims must be explicit false")

    checks = {
        item.get("check"): item
        for item in audit.get("observed_checks", [])
        if isinstance(item, dict) and isinstance(item.get("check"), str)
    }
    full_suite = checks.get("full_governance_suite", {})
    if full_suite.get("verbatim_summary") != [
        "Ran 532 tests in 1319.315s",
        "FAILED (failures=40, errors=2)",
    ] or full_suite.get("acceptance") != "fail":
        errors.append(f"{prefix} full governance failure evidence changed")
    no_live = checks.get("targeted_no_live_suite", {})
    if no_live.get("verbatim_summary") != [
        "Ran 18 tests in 7.518s",
        "OK",
    ] or no_live.get("acceptance") != "pass_with_narrow_claim_boundary":
        errors.append(f"{prefix} targeted no-live evidence changed")


def validate_approval_queue(
    approval_queue: object,
    *,
    approval_actions: set[str],
    experiment: dict | None,
    errors: list[str],
) -> None:
    if not isinstance(approval_queue, list):
        errors.append("approval_queue must be a list")
        return
    if len(approval_queue) != 1:
        errors.append("approval_queue must contain only the exact CA012650 blocked entry")
    ca_entries = []
    for index, item in enumerate(approval_queue):
        prefix = f"approval_queue[{index}]:"
        if not isinstance(item, dict):
            errors.append(f"{prefix} entry must be an object")
            continue
        if item.get("id") == "approval-ca012650-one-message-verification":
            ca_entries.append(item)
        if item.get("external_effect") is True and item.get("action") not in approval_actions:
            errors.append(f"{prefix} external action is outside explicit approval envelope")
        missing = item.get("missing_bindings")
        if not isinstance(missing, list):
            errors.append(f"{prefix} missing_bindings must be a list")
            continue
        declared_missing = set(missing)
        observed_unbound: set[str] = set()
        if "sender_account" in item and item.get("sender_account") is None:
            observed_unbound.add("sender_account")
        if "observation_cutoff_at" in item and item.get("observation_cutoff_at") is None:
            observed_unbound.add("observation_cutoff_at")
        if "pre_send_source_refresh" in item:
            refresh = item.get("pre_send_source_refresh")
            if not isinstance(refresh, dict) or refresh.get("status") != "completed":
                observed_unbound.add("pre_send_source_refresh")
        if "exact_user_authorization" in item and item.get(
            "exact_user_authorization"
        ) is not True:
            observed_unbound.add("exact_user_authorization")
        if not observed_unbound.issubset(declared_missing):
            errors.append(f"{prefix} observed unbound fields are missing from missing_bindings")
        if declared_missing or observed_unbound:
            if not isinstance(item.get("status"), str) or not item["status"].startswith(
                "blocked"
            ):
                errors.append(f"{prefix} missing binding requires blocked status")
            for flag in ("authorized", "ready", "executable"):
                if item.get(flag) is not False:
                    errors.append(f"{prefix} missing binding requires {flag}=false")

    if len(ca_entries) != 1:
        errors.append("approval_queue must contain exactly one CA012650 blocked entry")
        return
    item = ca_entries[0]
    prefix = "CA012650 approval:"
    if set(item.get("missing_bindings", [])) != REQUIRED_CA_MISSING_BINDINGS:
        errors.append(f"{prefix} exact missing bindings changed")
    if item.get("action") != "external_contact" or item.get("external_effect") is not True:
        errors.append(f"{prefix} action must be an explicit external contact")
    if any(item.get(flag) is not False for flag in ("authorized", "ready", "executable")):
        errors.append(f"{prefix} blocked entry cannot be authorized, ready, or executable")
    if item.get("sender_account") is not None:
        errors.append(f"{prefix} sender account must remain unbound")
    if item.get("observation_cutoff_at") is not None:
        errors.append(f"{prefix} observation cutoff must remain unbound")
    refresh = item.get("pre_send_source_refresh")
    if not isinstance(refresh, dict) or refresh.get("status") == "completed":
        errors.append(f"{prefix} pre-send source refresh must remain incomplete")
    if item.get("exact_user_authorization") is not False:
        errors.append(f"{prefix} exact user authorization must remain false")
    verify_bound_file(
        item.get("message_binding"),
        base=RESEARCH_ROOT,
        errors=errors,
        label=f"{prefix} message",
    )
    if experiment is not None:
        if item.get("experiment_id") != experiment.get("experiment_id"):
            errors.append(f"{prefix} experiment_id mismatch")
        target = experiment.get("exact_target", {})
        if item.get("exact_channel") != target.get("allowed_future_channel"):
            errors.append(f"{prefix} channel differs from bound experiment")


def validate(state: dict) -> list[str]:
    errors: list[str] = []
    validate_not_future(state.get("as_of"), errors=errors, label="active state as_of")
    envelope = state.get("authority_envelope", {})
    declared_autonomous_scopes = envelope.get("autonomous_scopes")
    if not isinstance(declared_autonomous_scopes, list) or set(
        declared_autonomous_scopes
    ) != AUTONOMOUS_SCOPES or len(declared_autonomous_scopes) != len(
        AUTONOMOUS_SCOPES
    ):
        errors.append("authority envelope autonomous scopes changed or were expanded")
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
    stream_by_id: dict[str, dict] = {}
    for stream in workstreams:
        if not isinstance(stream, dict):
            errors.append("workstream entry must be an object")
            continue
        stream_id = stream.get("id")
        prefix = f"workstream {stream_id or '<missing>'}:"
        if not isinstance(stream_id, str) or not stream_id.strip():
            errors.append(f"{prefix} missing id")
        elif stream_id in seen_ids:
            errors.append(f"{prefix} duplicate id")
        else:
            seen_ids.add(stream_id)
            stream_by_id[stream_id] = stream

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
                if not isinstance(fact, dict):
                    errors.append(f"{fact_prefix} must be an object")
                    continue
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

    strategy = stream_by_id.get("long_term_capability_strategy")
    if strategy is None:
        errors.append("missing long_term_capability_strategy workstream")
    else:
        if strategy.get("status") != "active_internal":
            errors.append("long-term capability strategy must remain active_internal")
        artifacts = strategy.get("strategy_artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != 4:
            errors.append("long-term capability strategy must bind its exact artifacts")
        else:
            for index, binding in enumerate(artifacts):
                verify_bound_file(
                    binding,
                    base=RESEARCH_ROOT,
                    errors=errors,
                    label=f"long-term strategy artifact[{index}]",
                )

    opportunity = stream_by_id.get("opportunity_to_transaction")
    experiment = None
    if opportunity is None:
        errors.append("missing opportunity_to_transaction workstream")
    else:
        if opportunity.get("status") != "blocked_external":
            errors.append("opportunity workstream must remain blocked_external")
        validate_review_receipts(opportunity, errors)
        experiment = validate_experiment(opportunity, errors)

    investment = stream_by_id.get("investment_discipline")
    if investment is None:
        errors.append("missing investment_discipline workstream")
    else:
        if investment.get("status") != "blocked_internal":
            errors.append("investment workstream must remain blocked_internal")
        expected_safety = {
            "paper_only": True,
            "human_final": True,
            "live_trading": False,
            "broker_integration": False,
        }
        if investment.get("safety_boundary") != expected_safety:
            errors.append("investment safety boundary changed or is incomplete")
        validate_investment_audit(investment, errors)

    validate_approval_queue(
        state.get("approval_queue"),
        approval_actions=approval_actions,
        experiment=experiment,
        errors=errors,
    )
    return errors


def main() -> int:
    state = load_json(STATE_PATH, errors=[], label="active state")
    if state is None:
        print("ERROR: active state is unreadable or invalid JSON")
        return 1
    errors = validate(state)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: active state, local evidence bindings, and authorization boundaries validate")
    print("NOTE: this does not validate demand, payment, delivery, profit, investment performance, or runtime acceptance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
