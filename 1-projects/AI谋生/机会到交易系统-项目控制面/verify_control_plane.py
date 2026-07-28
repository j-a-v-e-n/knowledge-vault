#!/usr/bin/env python3
"""Read-only consistency verifier for the project control plane."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FILES = {
    "README.md",
    "AGENTS.md",
    "PROJECT_CHARTER.md",
    "STATE.json",
    "DECISIONS.jsonl",
    "RUNBOOK.md",
    "MODEL_ADAPTER_CONTRACT.md",
    ".agent/PLANS.md",
    "research/2026-07-28-AI项目Harness调研.md",
    "evals/RECOVERY_DRILL.md",
    "schemas/model-adapter.schema.json",
    "schemas/handoff.schema.json",
    "adapters/current-codex.json",
    "verify_control_plane.py",
    "test_verify_control_plane.py",
}

PLAN_HEADINGS = {
    "## Purpose",
    "## Scope",
    "## Current facts",
    "## Progress",
    "## Surprises & Discoveries",
    "## Decision Log",
    "## Concrete steps",
    "## Validation and nonclaims",
    "## Idempotence and recovery",
    "## Interfaces and ownership",
    "## Outcomes & Retrospective",
}

EXPECTED_HASH_KEYS = {
    "SHADOW_CAPABILITY_POLICY.json",
    "run_shadow_acceptance.py",
    "test_shadow_acceptance.py",
    "verify_post_closure_manifest.py",
    "test_phase_manifests.py",
    "verify_run2_acceptance.py",
    "test_run2_acceptance.py",
}

LOCAL_AUTHORITY_KEYS = {
    "read_local_project",
    "read_public_sources",
    "write_project_control_plane",
    "modify_c8_candidate",
    "generate_local_synthetic_fixture",
}

EXTERNAL_AUTHORITY_KEYS = {
    "contact_real_people",
    "publish_publicly",
    "deploy",
    "access_or_create_accounts",
    "pay_or_receive_money",
    "sign_contracts",
    "make_delivery_commitments",
}

WORKFLOW_GATE_KEYS = {
    "control_plane_accepted",
    "c8_candidate_edit_allowed_now",
    "c8_fresh_review_pass",
    "local_shadow_allowed_now",
    "reality_experiment_proposal_allowed_now",
}

DECISION_STATUSES = {
    "ACTIVE_ROOT",
    "ACTIVE",
    "REOPENED",
    "ACTIVE_REMEDIATION",
    "PENDING",
    "FAILED",
    "SUPERSEDED",
}

ALTERNATIVE_STATES = {
    "SELECTED",
    "UNTRIED",
    "REJECTED",
    "REJECTED_CONSTRAINT",
    "FAILED",
    "SUPERSEDED",
}

TERMINAL_STATES = {
    "COMPLETE_OBSERVABLE_OUTCOME",
    "BLOCKED_NEEDS_AUTHORITY",
    "FAILED_EVIDENCE_OR_EVAL",
    "STALE_STATE",
    "BUDGET_STOP_REQUIRES_BACKTRACK",
}

LIFECYCLE_POLICIES: dict[str, dict[str, Any]] = {
    "CONTROL_PLANE_REMEDIATION": {
        "action": "RUN_CONTROL_PLANE_VALIDATION",
        "decision": "D030",
        "required_gates": set(),
        "gate_values": {
            "control_plane_accepted": False,
            "c8_candidate_edit_allowed_now": False,
            "c8_fresh_review_pass": False,
            "local_shadow_allowed_now": False,
            "reality_experiment_proposal_allowed_now": False,
        },
        "next": "C8_MINIMUM_REMEDIATION",
    },
    "C8_MINIMUM_REMEDIATION": {
        "action": "MODIFY_C8_CANDIDATE",
        "decision": "D040",
        "required_gates": {"control_plane_accepted", "c8_candidate_edit_allowed_now"},
        "gate_values": {
            "control_plane_accepted": True,
            "c8_candidate_edit_allowed_now": True,
            "c8_fresh_review_pass": False,
            "local_shadow_allowed_now": False,
            "reality_experiment_proposal_allowed_now": False,
        },
        "next": "C8_FRESH_REVIEW",
    },
    "C8_FRESH_REVIEW": {
        "action": "RUN_C8_FRESH_REVIEW",
        "decision": "D040",
        "required_gates": {"control_plane_accepted"},
        "gate_values": {
            "control_plane_accepted": True,
            "c8_candidate_edit_allowed_now": False,
            "c8_fresh_review_pass": False,
            "local_shadow_allowed_now": False,
            "reality_experiment_proposal_allowed_now": False,
        },
        "next": "LOCAL_READ_ONLY_SHADOW",
    },
    "LOCAL_READ_ONLY_SHADOW": {
        "action": "RUN_LOCAL_READ_ONLY_SHADOW",
        "decision": "D040",
        "required_gates": {
            "control_plane_accepted",
            "c8_fresh_review_pass",
            "local_shadow_allowed_now",
        },
        "gate_values": {
            "control_plane_accepted": True,
            "c8_candidate_edit_allowed_now": False,
            "c8_fresh_review_pass": True,
            "local_shadow_allowed_now": True,
            "reality_experiment_proposal_allowed_now": False,
        },
        "next": "SHADOW_COMPLETE_AWAITING_REALITY_GATE",
    },
    "SHADOW_COMPLETE_AWAITING_REALITY_GATE": {
        "action": "PREPARE_REALITY_EXPERIMENT_PROPOSAL",
        "decision": "D040",
        "required_gates": {
            "control_plane_accepted",
            "c8_fresh_review_pass",
            "reality_experiment_proposal_allowed_now",
        },
        "gate_values": {
            "control_plane_accepted": True,
            "c8_candidate_edit_allowed_now": False,
            "c8_fresh_review_pass": True,
            "local_shadow_allowed_now": False,
            "reality_experiment_proposal_allowed_now": True,
        },
        "next": "BLOCKED_NEEDS_AUTHORITY",
    },
}

ACTION_LOCAL_AUTHORITIES = {
    "RUN_CONTROL_PLANE_VALIDATION": {"read_local_project"},
    "MODIFY_C8_CANDIDATE": {"read_local_project", "modify_c8_candidate"},
    "RUN_C8_FRESH_REVIEW": {"read_local_project"},
    "RUN_LOCAL_READ_ONLY_SHADOW": {
        "read_local_project",
        "generate_local_synthetic_fixture",
    },
    "PREPARE_REALITY_EXPERIMENT_PROPOSAL": {
        "read_local_project",
        "write_project_control_plane",
    },
}

GOLD_LEAK_MARKERS = {
    "CONTROL_PLANE_REMEDIATION",
    "NO_REAL_OPPORTUNITY_VALIDATED",
    "PRE-FREEZE-REVIEW-ATTEMPT-1-FAIL",
    "OTTS-DESIGN-20260727-C7",
    "D030",
    "D020",
}


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def collect_snapshot(root: Path) -> tuple[str, list[dict[str, str]], list[str]]:
    entries: list[dict[str, str]] = []
    transients: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            transients.append(relative)
        entries.append({"path": relative, "sha256": sha256_file(path)})
    return sha256_bytes(canonical_json(entries)), entries, transients


def load_decisions(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            record = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number}: decision must be an object")
        records.append(record)
    return records


def ancestor_chain(by_id: dict[str, dict[str, Any]], decision_id: str) -> list[str]:
    chain: list[str] = []
    seen: set[str] = set()
    cursor: str | None = decision_id
    while cursor is not None:
        if cursor in seen:
            raise ValueError(f"parent cycle detected at {decision_id}")
        seen.add(cursor)
        chain.append(cursor)
        record = by_id.get(cursor)
        if record is None:
            break
        parent = record.get("parent_id")
        cursor = parent if isinstance(parent, str) else None
    return chain


def validate_decision_graph(
    records: list[dict[str, Any]],
    current_id: str,
    nearest_backtrack_id: str,
) -> list[str]:
    errors: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}

    for record in records:
        decision_id = record.get("id")
        if not isinstance(decision_id, str) or not decision_id:
            errors.append("decision missing non-empty string id")
            continue
        if decision_id in by_id:
            errors.append(f"duplicate decision id: {decision_id}")
            continue
        by_id[decision_id] = record

    for decision_id, record in by_id.items():
        parent_id = record.get("parent_id")
        backtrack_to = record.get("backtrack_to")
        if parent_id is not None and parent_id not in by_id:
            errors.append(f"{decision_id} has missing parent_id {parent_id}")
        if backtrack_to is not None and backtrack_to not in by_id:
            errors.append(f"{decision_id} has missing backtrack_to {backtrack_to}")
        if record.get("status") not in DECISION_STATUSES:
            errors.append(f"{decision_id} has invalid status")
        for key in ("question", "selected_alternative_id"):
            if not isinstance(record.get(key), str) or not record[key]:
                errors.append(f"{decision_id} missing non-empty {key}")
        for key in ("basis", "falsifiers"):
            value = record.get(key)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item for item in value
            ):
                errors.append(f"{decision_id} {key} must be a non-empty string list")
        if not isinstance(record.get("attempts"), list):
            errors.append(f"{decision_id} attempts must be a list")

        alternatives = record.get("alternatives")
        if not isinstance(alternatives, list) or not alternatives:
            errors.append(f"{decision_id} alternatives must be non-empty")
            continue
        alternative_ids: set[str] = set()
        selected_ids: list[str] = []
        for alternative in alternatives:
            if not isinstance(alternative, dict):
                errors.append(f"{decision_id} alternative must be an object")
                continue
            alternative_id = alternative.get("id")
            if not isinstance(alternative_id, str) or not alternative_id:
                errors.append(f"{decision_id} alternative missing id")
                continue
            if alternative_id in alternative_ids:
                errors.append(f"{decision_id} duplicate alternative {alternative_id}")
            alternative_ids.add(alternative_id)
            if alternative.get("state") not in ALTERNATIVE_STATES:
                errors.append(f"{decision_id} alternative {alternative_id} invalid state")
            if alternative.get("state") == "SELECTED":
                selected_ids.append(alternative_id)
            if not isinstance(alternative.get("description"), str) or not alternative[
                "description"
            ]:
                errors.append(f"{decision_id} alternative {alternative_id} missing description")
        if selected_ids != [record.get("selected_alternative_id")]:
            errors.append(f"{decision_id} selected alternative is not uniquely bound")

    for decision_id, record in by_id.items():
        try:
            chain = ancestor_chain(by_id, decision_id)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        own_backtrack = record.get("backtrack_to")
        if own_backtrack is not None and own_backtrack not in chain[1:]:
            errors.append(f"{decision_id} backtrack_to is not a strict ancestor")

    if current_id not in by_id:
        errors.append(f"current decision missing: {current_id}")
        return errors
    if nearest_backtrack_id not in by_id:
        errors.append(f"nearest backtrack decision missing: {nearest_backtrack_id}")
        return errors
    try:
        current_chain = ancestor_chain(by_id, current_id)
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    if nearest_backtrack_id not in current_chain[1:]:
        errors.append("nearest backtrack decision is not an ancestor of current")
    else:
        alternatives = by_id[nearest_backtrack_id].get("alternatives", [])
        if not any(
            isinstance(item, dict) and item.get("state") == "UNTRIED"
            for item in alternatives
        ):
            errors.append("nearest backtrack decision has no UNTRIED alternative")
    return errors


def validate_authority_and_action(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    authority = state.get("authority")
    if not isinstance(authority, dict):
        return ["authority must be an object"]
    if authority.get("authority_source") != "USER_INSTRUCTION_AND_RUNTIME_ENFORCEMENT_ONLY":
        errors.append("authority source must remain user/runtime only")
    if authority.get("state_file_can_expand_authority") is not False:
        errors.append("state_file_can_expand_authority must be false")
    if authority.get("quality_gate_can_expand_authority") is not False:
        errors.append("quality_gate_can_expand_authority must be false")

    local = authority.get("local")
    external = authority.get("external")
    if not isinstance(local, dict) or set(local) != LOCAL_AUTHORITY_KEYS:
        errors.append("local authority keys are not exact")
        local = {}
    if not isinstance(external, dict) or set(external) != EXTERNAL_AUTHORITY_KEYS:
        errors.append("external authority keys are not exact")
        external = {}
    for key in LOCAL_AUTHORITY_KEYS:
        if local.get(key) is not True:
            errors.append(f"declared local authority must be true: {key}")
    for key in EXTERNAL_AUTHORITY_KEYS:
        if external.get(key) is not False:
            errors.append(f"external authority must remain false: {key}")

    gates = state.get("workflow_gates")
    if not isinstance(gates, dict) or set(gates) != WORKFLOW_GATE_KEYS:
        errors.append("workflow gate keys are not exact")
        gates = {}

    lifecycle = state.get("lifecycle_state")
    policy = LIFECYCLE_POLICIES.get(lifecycle)
    if policy is None:
        errors.append(f"unsupported lifecycle_state: {lifecycle}")
        return errors
    if state.get("current_decision_node") != policy["decision"]:
        errors.append("lifecycle state does not match current decision")
    for key, expected in policy["gate_values"].items():
        if gates.get(key) is not expected:
            errors.append(f"workflow gate {key} conflicts with lifecycle state")

    action = state.get("next_safe_action")
    if not isinstance(action, dict):
        return errors + ["next_safe_action must be an object"]
    required_action_keys = {
        "action_id",
        "kind",
        "actor_role",
        "target",
        "required_local_authorities",
        "required_workflow_gates",
        "external_action",
        "expected_observable_result",
        "on_success_transition",
        "on_failure_transition",
    }
    if set(action) != required_action_keys:
        errors.append("next_safe_action keys are not exact")
    kind = action.get("kind")
    if kind != policy["action"]:
        errors.append("next action kind conflicts with lifecycle state")
    expected_authorities = ACTION_LOCAL_AUTHORITIES.get(kind)
    declared_authorities = action.get("required_local_authorities")
    if not isinstance(declared_authorities, list) or set(declared_authorities) != (
        expected_authorities or set()
    ):
        errors.append("next action local authority requirements are not exact")
    else:
        for key in declared_authorities:
            if local.get(key) is not True:
                errors.append(f"next action lacks local authority: {key}")
    declared_gates = action.get("required_workflow_gates")
    if not isinstance(declared_gates, list) or set(declared_gates) != policy[
        "required_gates"
    ]:
        errors.append("next action workflow requirements are not exact")
    else:
        for key in declared_gates:
            if gates.get(key) is not True:
                errors.append(f"next action lacks workflow gate: {key}")
    if action.get("external_action") is not False:
        errors.append("all currently supported actions must be local-only")
    if action.get("on_success_transition") != policy["next"]:
        errors.append("next action success transition conflicts with lifecycle table")
    for key in ("action_id", "actor_role", "target", "expected_observable_result"):
        if not isinstance(action.get(key), str) or not action[key]:
            errors.append(f"next action missing non-empty {key}")
    return errors


def validate_candidate(root: Path, state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    info = state.get("current_candidate")
    if not isinstance(info, dict):
        return ["current_candidate must be an object"]
    expected_candidate = (
        root.parent / "机会到交易系统-C8" / "机会到交易系统-总体设计候选"
    ).resolve()
    expected_review = (
        expected_candidate
        / "研究"
        / "2026-07-27-总体设计"
        / "C8_DOMAIN_GATE_REVIEW_REPORT.md"
    )
    expected_historical = expected_candidate / "FINAL_CANDIDATE_MANIFEST.json"

    if info.get("candidate_label") != "C8":
        errors.append("candidate_label must be C8")
    candidate_relative = info.get("candidate_path")
    if not isinstance(candidate_relative, str):
        return errors + ["candidate_path must be a string"]
    candidate_path = (root / candidate_relative).resolve()
    if candidate_path != expected_candidate:
        errors.append("candidate_path is not the fixed C8 sibling")
    if not candidate_path.is_dir():
        return errors + ["fixed C8 candidate path is missing"]

    review_relative = info.get("review_report")
    if not isinstance(review_relative, str) or (root / review_relative).resolve() != expected_review:
        errors.append("review_report is not the fixed C8 report")
    elif not expected_review.is_file():
        errors.append("fixed C8 review report is missing")
    else:
        review_text = expected_review.read_text(encoding="utf-8")
        for marker in (
            "PRE-FREEZE-REVIEW-ATTEMPT-1-FAIL",
            "FAIL / NO-GO",
            "Critical 3 / Major 3 / Minor 0",
            "FRESH-REVIEW-PENDING",
        ):
            if marker not in review_text:
                errors.append(f"review report missing marker: {marker}")

    hashes = info.get("candidate_hashes")
    if not isinstance(hashes, dict) or set(hashes) != EXPECTED_HASH_KEYS:
        errors.append("candidate_hashes must bind the exact non-empty key set")
    else:
        research_dir = candidate_path / "研究" / "2026-07-27-总体设计"
        for filename in sorted(EXPECTED_HASH_KEYS):
            file_path = research_dir / filename
            if not file_path.is_file():
                errors.append(f"candidate hash target missing: {filename}")
            elif sha256_file(file_path) != hashes[filename]:
                errors.append(f"candidate hash mismatch: {filename}")

    historical = info.get("historical_manifest_detected")
    if not isinstance(historical, dict):
        errors.append("historical_manifest_detected must be an object")
    else:
        historical_relative = historical.get("path")
        if (
            not isinstance(historical_relative, str)
            or (root / historical_relative).resolve() != expected_historical
        ):
            errors.append("historical manifest path is not fixed")
        elif not expected_historical.is_file():
            errors.append("historical C7 manifest is missing")
        else:
            manifest = load_json(expected_historical)
            if manifest.get("candidate_id") != historical.get("candidate_id"):
                errors.append("historical candidate_id drift")
            if manifest.get("status") != historical.get("status"):
                errors.append("historical status drift")
            if manifest.get("candidate_id") != "OTTS-DESIGN-20260727-C7":
                errors.append("canonical historical manifest is no longer C7")

    root_names = {
        "机会到交易系统-闭合记录",
        "机会到交易系统-shadow-mvp",
        "机会到交易系统-shadow-review",
    }
    actual_roots_present = any((candidate_path.parent / name).exists() for name in root_names)
    if info.get("post_closure_roots_present") is not actual_roots_present:
        errors.append("post_closure_roots_present does not match filesystem")

    pre_shadow_states = {
        "CONTROL_PLANE_REMEDIATION",
        "C8_MINIMUM_REMEDIATION",
        "C8_FRESH_REVIEW",
    }
    if state.get("lifecycle_state") in pre_shadow_states:
        if info.get("status") != "PRE-FREEZE-REVIEW-ATTEMPT-1-FAIL":
            errors.append("pre-shadow candidate status must retain attempt-1 FAIL")
        if info.get("review_verdict") != "FAIL_NO_GO":
            errors.append("pre-shadow review verdict must remain FAIL_NO_GO")
        if info.get("fresh_review_pending") is not True:
            errors.append("pre-shadow fresh_review_pending must be true")
        if actual_roots_present:
            errors.append("post-closure roots must be absent before Shadow")
    return errors


def validate_eval_task(root: Path) -> list[str]:
    text = (root / "evals" / "RECOVERY_DRILL.md").read_text(encoding="utf-8")
    errors = [f"recovery task leaks gold marker: {marker}" for marker in GOLD_LEAK_MARKERS if marker in text]
    if re.search(r"\b[0-9a-f]{64}\b", text):
        errors.append("recovery task leaks an exact SHA-256")
    return errors


def validate_adapter(root: Path, state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    portability = state.get("model_portability")
    if not isinstance(portability, dict):
        return ["model_portability must be an object"]
    if portability.get("claim_status") != "CONTRACT_DESIGNED_CROSS_PROVIDER_UNVERIFIED":
        errors.append("portability claim must remain cross-provider unverified")
    if portability.get("qualification_is_authority") is not False:
        errors.append("qualification_is_authority must be false")
    adapter_relative = portability.get("adapter_record")
    if not isinstance(adapter_relative, str):
        return errors + ["adapter_record must be a string"]
    try:
        adapter_path = resolve_inside(root, adapter_relative)
    except ValueError as exc:
        return errors + [str(exc)]
    if not adapter_path.is_file():
        return errors + ["adapter record missing"]
    adapter = load_json(adapter_path)
    qualification = adapter.get("qualification", {})
    if qualification.get("authority_effect") != "NONE":
        errors.append("adapter qualification must have no authority effect")
    if qualification.get("cross_provider_portability_verified") is not False:
        errors.append("cross-provider portability is not yet verified")
    if qualification.get("unattended_handoff") is not False:
        errors.append("current adapter is not qualified for unattended handoff")
    if portability.get("unattended_handoff_qualified") is not False:
        errors.append("STATE must not claim unattended handoff qualification")
    for schema_path in (
        root / "schemas" / "model-adapter.schema.json",
        root / "schemas" / "handoff.schema.json",
    ):
        try:
            load_json(schema_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"invalid schema document {schema_path.name}: {exc}")
    return errors


def resolve_inside(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes control-plane root: {relative}") from exc
    return candidate


def validate_control_plane(root: Path) -> dict[str, Any]:
    root = root.resolve()
    snapshot_start, entries_start, transients_start = collect_snapshot(root)
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def record(name: str, local_errors: list[str]) -> None:
        checks.append({"name": name, "ok": not local_errors})
        errors.extend(f"{name}: {item}" for item in local_errors)

    present_files = {entry["path"] for entry in entries_start}
    record(
        "required_files",
        [f"missing {relative}" for relative in sorted(REQUIRED_FILES - present_files)],
    )
    record(
        "transient_artifacts",
        [f"forbidden bytecode artifact: {path}" for path in transients_start],
    )
    if REQUIRED_FILES - present_files:
        return {
            "valid": False,
            "snapshot_sha256": snapshot_start,
            "snapshot_stable": True,
            "checks": checks,
            "errors": errors,
        }

    try:
        state = load_json(root / "STATE.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        record("state_json", [str(exc)])
        return {
            "valid": False,
            "snapshot_sha256": snapshot_start,
            "snapshot_stable": True,
            "checks": checks,
            "errors": errors,
        }
    record("state_json", [])

    state_errors: list[str] = []
    if state.get("schema_version") != "1.1":
        state_errors.append("unexpected schema_version")
    if state.get("project_id") != "OPPORTUNITY_TO_TRANSACTION_SYSTEM":
        state_errors.append("unexpected project_id")
    if state.get("commercial_progress", {}).get("transaction_evidence_present") is not False:
        state_errors.append("transaction evidence must currently be false")
    if state.get("commercial_progress", {}).get("repeatability_evidence_present") is not False:
        state_errors.append("repeatability evidence must currently be false")
    if set(state.get("allowed_lifecycle_states", [])) != set(LIFECYCLE_POLICIES):
        state_errors.append("allowed_lifecycle_states do not match closed transition table")
    if set(state.get("terminal_states", [])) != TERMINAL_STATES:
        state_errors.append("terminal_states do not match fail-closed set")
    work_unit = state.get("current_work_unit")
    if not isinstance(work_unit, dict):
        state_errors.append("current_work_unit must be an object")
    else:
        if work_unit.get("status") not in {"IN_PROGRESS", "PENDING", "COMPLETE", "FAILED"}:
            state_errors.append("current_work_unit status is invalid")
        if work_unit.get("budget_state") not in {
            "NORMAL",
            "FINAL_REMEDIATION_BEFORE_BACKTRACK",
            "EXHAUSTED",
        }:
            state_errors.append("current_work_unit budget_state is invalid")
        for key in (
            "work_unit_id",
            "acceptance_change_required",
            "stop_without_retry_if",
        ):
            if not isinstance(work_unit.get(key), str) or not work_unit[key]:
                state_errors.append(f"current_work_unit missing {key}")
    record("state_invariants", state_errors)

    plan_errors: list[str] = []
    plan_relative = state.get("current_exec_plan")
    if not isinstance(plan_relative, str):
        plan_errors.append("current_exec_plan must be a string")
    else:
        try:
            plan_path = resolve_inside(root, plan_relative)
        except ValueError as exc:
            plan_errors.append(str(exc))
        else:
            if not plan_path.is_file():
                plan_errors.append("current ExecPlan is missing")
            elif plan_path.parent != (root / "exec-plans" / "active").resolve():
                plan_errors.append("current ExecPlan is not under active")
            else:
                plan_text = plan_path.read_text(encoding="utf-8")
                for heading in sorted(PLAN_HEADINGS):
                    if heading not in plan_text:
                        plan_errors.append(f"current ExecPlan missing heading: {heading}")
    active_plans = list((root / "exec-plans" / "active").glob("*.md"))
    if len(active_plans) != 1:
        plan_errors.append(f"expected exactly one active ExecPlan, found {len(active_plans)}")
    record("active_exec_plan", plan_errors)

    try:
        decisions = load_decisions(root / "DECISIONS.jsonl")
        decision_errors = validate_decision_graph(
            decisions,
            str(state.get("current_decision_node", "")),
            str(state.get("backtrack", {}).get("nearest_reopenable_decision", "")),
        )
    except (OSError, ValueError) as exc:
        decision_errors = [str(exc)]
    record("decision_graph", decision_errors)
    record("authority_gate_action", validate_authority_and_action(state))
    record("candidate_exact_state", validate_candidate(root, state))
    record("recovery_task_no_gold", validate_eval_task(root))
    record("model_adapter", validate_adapter(root, state))

    separation_errors: list[str] = []
    candidate_relative = state.get("current_candidate", {}).get("candidate_path")
    if isinstance(candidate_relative, str):
        candidate_path = (root / candidate_relative).resolve()
        try:
            root.relative_to(candidate_path)
            separation_errors.append("control plane must not be inside candidate")
        except ValueError:
            pass
        try:
            candidate_path.relative_to(root)
            separation_errors.append("candidate must not be inside control plane")
        except ValueError:
            pass
    record("control_plane_candidate_separation", separation_errors)

    snapshot_end, entries_end, transients_end = collect_snapshot(root)
    snapshot_errors: list[str] = []
    if snapshot_end != snapshot_start or entries_end != entries_start:
        snapshot_errors.append("control-plane snapshot changed during verification")
    if transients_end != transients_start:
        snapshot_errors.append("transient artifact set changed during verification")
    record("snapshot_stability", snapshot_errors)

    return {
        "valid": not errors,
        "snapshot_sha256": snapshot_start,
        "snapshot_stable": not snapshot_errors,
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    result = validate_control_plane(Path(__file__).resolve().parent)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

