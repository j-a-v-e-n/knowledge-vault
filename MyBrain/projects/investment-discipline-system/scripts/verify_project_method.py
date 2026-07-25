#!/usr/bin/env python3
"""Fail-closed verification for the reusable project-work method kernel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
POLICY_PATH = PROJECT_ROOT / "governance" / "PROJECT_METHOD_POLICY_V1.json"
FAILURE_REGISTRY = PROJECT_ROOT / "governance" / "FAILURE_CLASSES_V1.json"
DEFAULT_CLOSURE_EVIDENCE = (
    PROJECT_ROOT / "evidence" / "verification" / "V-PROJECT-METHOD.json"
)
ALLOWED_FAILURE_STATUSES = {"covered", "partially_covered", "gap"}
CONDITIONALLY_DEFERRED_FAILURES = {
    "HUM-05": "COND-JAVEN-FIELD-USE",
    "ECO-03": "COND-LONGITUDINAL-EDGE",
}

EXPECTED_TOP_LEVEL = {
    "schema_version",
    "status",
    "policy_id",
    "scope",
    "authority",
    "required_state_packet",
    "work_packet_contract",
    "execution_state_machine",
    "completion_change_control",
    "review_boundary",
    "harness_admission",
    "supply_chain",
    "frozen_test_integrity",
    "incident_learning",
    "nontechnical_explanation",
    "scope_and_budget",
    "maintainability_and_migration",
    "failure_coverage",
}
EXPECTED_STATE_FILES = [
    "PROJECT_CHARTER.md",
    "STATUS.md",
    "TASK_BOARD.md",
    "DECISIONS.md",
    "AI_COLLABORATION_METHOD.md",
]
EXPECTED_DUMP_FIELDS = [
    "available",
    "current_stage",
    "currently_usable",
    "target_for_this_run",
    "known_blockers",
    "authorities_and_prohibitions",
]
EXPECTED_POSITION_PROBES = [
    "start",
    "middle",
    "end",
    "post_compaction",
    "empty_context_restart",
    "stale_request_regression",
]
EXPECTED_PACKET_FIELDS = [
    "packet_id",
    "goal_id",
    "bounded_write_paths",
    "read_dependencies",
    "acceptance_checks",
    "checkpoint_path",
    "retry_budget",
    "owner",
    "reviewer",
    "external_side_effects",
]
EXPECTED_FAILURE_CASES = {
    "GOV-04": (
        "PM-01-MONOTONIC-COMPLETION",
        "CASE-METHOD-CRITERION-WEAKENING",
    ),
    "GOV-07": (
        "PM-01-MONOTONIC-COMPLETION",
        "CASE-METHOD-CONDITIONAL-BYPASS",
    ),
    "CTX-02": ("PM-02-CONTEXT-RECOVERY", "CASE-METHOD-MIDDLE-SENTINEL"),
    "ORG-01": ("PM-03-BOUNDED-WORK", "CASE-METHOD-BROAD-WRITE-SCOPE"),
    "ORG-03": (
        "PM-04-DISJOINT-WRITES",
        "CASE-METHOD-PARALLEL-COLLISION",
    ),
    "ORG-04": (
        "PM-05-NO-PROGRESS-STOP",
        "CASE-METHOD-REPEATED-BLOCKER",
    ),
    "ORG-05": (
        "PM-06-HARNESS-ABLATION",
        "CASE-METHOD-HARNESS-NO-BASELINE",
    ),
    "ORG-06": (
        "PM-07-REVIEWER-READONLY",
        "CASE-METHOD-REVIEWER-WRITES-CANDIDATE",
    ),
    "IMP-04": ("PM-08-SUPPLY-CHAIN", "CASE-METHOD-FLOATING-DEPENDENCY"),
    "VER-07": ("PM-09-FROZEN-TESTS", "CASE-METHOD-FROZEN-TEST-DELETED"),
    "SEC-06": ("PM-08-SUPPLY-CHAIN", "CASE-METHOD-TELEMETRY-UNKNOWN"),
    "OPS-08": (
        "PM-10-INCIDENT-PREVENTION",
        "CASE-METHOD-INCIDENT-NO-REGRESSION",
    ),
    "HUM-05": (
        "PM-11-NONTECH-EXPLANATION",
        "CASE-METHOD-EXPLANATION-OMITS-UNKNOWN",
    ),
    "ECO-01": (
        "PM-12-SCOPE-AND-BUDGET",
        "CASE-METHOD-BUDGET-RELABELLED-SUCCESS",
    ),
    "ECO-02": (
        "PM-12-SCOPE-AND-BUDGET",
        "CASE-METHOD-LIVE-SCOPE-SMUGGLE",
    ),
    "ECO-03": (
        "PM-13-MAINTAINABILITY",
        "CASE-METHOD-COMPONENT-NO-REMOVAL",
    ),
    "ECO-04": ("PM-14-MIGRATION-EXIT", "CASE-METHOD-RENAME-REWRITE"),
}


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite a prior key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label}: invalid or unreadable JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label}: top-level value must be an object")
        return {}
    return value


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def exact_string_list(
    value: Any,
    expected: list[str],
    label: str,
    errors: list[str],
) -> None:
    if value != expected:
        errors.append(f"{label} differs")


def exact_set(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    if (
        not isinstance(value, list)
        or not all(nonempty(item) for item in value)
        or len(value) != len(set(value))
        or set(value) != expected
    ):
        errors.append(f"{label} differs")


def verify_authority(policy: dict[str, Any], errors: list[str]) -> None:
    expected = {
        "builder_may_submit_candidate": True,
        "builder_may_lower_frozen_completion_criteria": False,
        "reviewer_may_modify_candidate": False,
        "human_reserved_changes": [
            "goal",
            "scope",
            "privacy boundary",
            "live-money boundary",
            "completion-risk acceptance",
        ],
    }
    if policy.get("authority") != expected:
        errors.append("project method authority boundary differs")


def verify_state_and_packets(policy: dict[str, Any], errors: list[str]) -> None:
    state = policy.get("required_state_packet")
    if not isinstance(state, dict):
        errors.append("required state packet is missing")
    else:
        exact_string_list(
            state.get("files"),
            EXPECTED_STATE_FILES,
            "required state packet files",
            errors,
        )
        exact_string_list(
            state.get("start_dump_fields"),
            EXPECTED_DUMP_FIELDS,
            "state dump fields",
            errors,
        )
        exact_string_list(
            state.get("position_probes"),
            EXPECTED_POSITION_PROBES,
            "context position probes",
            errors,
        )
        if state.get("missing_required_item_outcome") != "blocked_state_recovery":
            errors.append("missing state packet must block recovery")
        for relative in EXPECTED_STATE_FILES:
            if not (PROJECT_ROOT / relative).is_file():
                errors.append(f"required state packet file is missing: {relative}")

    packet = policy.get("work_packet_contract")
    if not isinstance(packet, dict):
        errors.append("work packet contract is missing")
        return
    exact_string_list(
        packet.get("required_fields"),
        EXPECTED_PACKET_FIELDS,
        "work packet required fields",
        errors,
    )
    exact_set(
        packet.get("forbidden_write_scopes"),
        {"/", "~", "repository_root_recursive", "unresolved_glob", "undeclared_path"},
        "forbidden work-packet write scopes",
        errors,
    )
    if packet.get("parallel_write_rule") != (
        "active packets must have disjoint bounded_write_paths; collision blocks "
        "both packets until ownership is resolved"
    ):
        errors.append("parallel write ownership rule differs")
    if packet.get("partial_state_rule") != (
        "a packet cannot be complete without its checkpoint and acceptance receipts"
    ):
        errors.append("partial work state rule differs")


def verify_execution(policy: dict[str, Any], errors: list[str]) -> None:
    machine = policy.get("execution_state_machine")
    if not isinstance(machine, dict):
        errors.append("project execution state machine is missing")
        return
    exact_set(
        machine.get("states"),
        {
            "pending",
            "active",
            "verification_failed",
            "blocked",
            "candidate_complete",
            "accepted",
            "superseded",
        },
        "project execution states",
        errors,
    )
    if type(machine.get("max_consecutive_same_blocker_turns")) is not int or (
        machine.get("max_consecutive_same_blocker_turns") != 3
    ):
        errors.append("same-blocker stop threshold differs")
    if machine.get("same_blocker_limit_outcome") != "blocked":
        errors.append("same-blocker threshold must produce blocked")
    if machine.get("budget_exhaustion_outcome") != "bounded_incomplete":
        errors.append("budget exhaustion must produce bounded_incomplete")
    exact_set(
        machine.get("forbidden_transitions"),
        {
            "verification_failed->accepted",
            "blocked->accepted",
            "superseded->accepted",
        },
        "forbidden execution transitions",
        errors,
    )
    exact_set(
        machine.get("accepted_requires"),
        {
            "all acceptance checks pass",
            "all required evidence paths exist and match",
            "reviewer did not modify candidate",
            "no open critical or major finding",
            "human-reserved decisions remain human",
        },
        "accepted-state requirements",
        errors,
    )


def verify_completion_and_review(policy: dict[str, Any], errors: list[str]) -> None:
    control = policy.get("completion_change_control")
    required_phrases = {
        "monotonic_rule": ("deletion", "weakening", "post-hoc"),
        "human_exception": ("explicit human decision", "cannot rewrite"),
        "conditional_gate_rule": ("cannot weaken", "failure outcome"),
        "terminology_rule": ("does not authorize a rewrite",),
    }
    if not isinstance(control, dict) or set(control) != set(required_phrases):
        errors.append("completion change-control schema differs")
    else:
        for field, phrases in required_phrases.items():
            value = control.get(field)
            if not nonempty(value) or any(phrase not in value for phrase in phrases):
                errors.append(f"completion change-control {field} differs")

    review = policy.get("review_boundary")
    if not isinstance(review, dict):
        errors.append("review boundary is missing")
        return
    if review.get("reviewer_candidate_write_paths") != []:
        errors.append("reviewer candidate write paths must be empty")
    exact_set(
        review.get("reviewer_append_only_output_prefixes"),
        {"audits/", "evidence/reviews/"},
        "reviewer append-only output prefixes",
        errors,
    )
    if review.get("candidate_change_after_review") != "invalidates_review_binding":
        errors.append("candidate change must invalidate review")
    if review.get("same_model_or_role_name_counts_as_independent") is not False:
        errors.append("role names or same-model repetition cannot imply independence")
    exact_set(
        review.get("high_impact_review_requires"),
        {
            "candidate-bound read-only review",
            "different evidence path",
            "deterministic oracle or explicit human decision",
        },
        "high-impact review requirements",
        errors,
    )


def verify_harness_and_supply_chain(
    policy: dict[str, Any], errors: list[str]
) -> None:
    harness = policy.get("harness_admission")
    if not isinstance(harness, dict):
        errors.append("harness admission policy is missing")
    else:
        if harness.get("default") != "not_adopted":
            errors.append("optional harness default must be not_adopted")
        exact_set(
            harness.get("required_same_task_fields"),
            {
                "baseline_artifact",
                "target_artifact",
                "objective_oracle",
                "quality_delta",
                "time_cost",
                "maintenance_cost",
                "failure_delta",
                "reversibility",
                "exit_plan",
            },
            "harness same-task ablation fields",
            errors,
        )
        if harness.get("missing_ablation_outcome") != "not_adopted":
            errors.append("missing harness ablation must reject adoption")
        if harness.get("framework_name_or_popularity_is_evidence") is not False:
            errors.append("framework names or popularity cannot count as evidence")

    supply = policy.get("supply_chain")
    if not isinstance(supply, dict):
        errors.append("supply-chain policy is missing")
        return
    if supply.get("core_runtime_policy") != (
        "python_standard_library_only_until_a_dependency_manifest_is_accepted"
    ):
        errors.append("core runtime dependency boundary differs")
    for field, expected in (
        ("boundary_manifest", "governance/DEPENDENCY_BOUNDARY_V1.json"),
        ("boundary_verifier", "scripts/verify_dependency_boundary.py"),
        ("boundary_tests", "governance_tests/test_dependency_boundary.py"),
    ):
        if supply.get(field) != expected:
            errors.append(f"supply-chain {field} binding differs")
    exact_set(
        supply.get("dependency_manifest_required_fields"),
        {
            "name",
            "version_or_commit",
            "sha256_or_lock_hash",
            "canonical_source",
            "license",
            "necessity",
            "permissions_or_telemetry",
            "removal_plan",
        },
        "dependency manifest fields",
        errors,
    )
    for field, expected in (
        ("floating_versions_allowed", False),
        ("external_actions_require_full_commit_sha", True),
        ("install_before_review_allowed", False),
    ):
        if supply.get(field) is not expected:
            errors.append(f"supply-chain {field} differs")
    if supply.get("telemetry_unknown_outcome") != "blocked":
        errors.append("unknown dependency telemetry must block")


def verify_tests_incidents_and_explanations(
    policy: dict[str, Any], errors: list[str]
) -> None:
    integrity = policy.get("frozen_test_integrity")
    if not isinstance(integrity, dict):
        errors.append("frozen test integrity policy is missing")
    else:
        exact_set(
            integrity.get("required_suite_roots"),
            {"governance_tests/", "tests/", "acceptance/"},
            "required frozen test roots",
            errors,
        )
        if integrity.get("deletion_skip_or_xfail_outcome") != "blocked":
            errors.append("deleting or skipping a frozen test must block")
        if integrity.get("baseline_must_pass_before_mutation") is not True:
            errors.append("mutation tests must first prove a passing baseline")
        if integrity.get("mutation_must_trigger_target_rejection") is not True:
            errors.append("mutation must trigger its target rejection")
        if integrity.get("test_or_oracle_change_requires_new_candidate_review") is not True:
            errors.append("test or oracle changes must require a new review")

    incidents = policy.get("incident_learning")
    required_incident_fields = {
        "incident_id",
        "observed_failure",
        "proximate_cause",
        "root_control_failure",
        "preventive_control",
        "regression_test",
        "owner",
        "reopen_trigger",
    }
    if not isinstance(incidents, dict):
        errors.append("incident-learning policy is missing")
    else:
        exact_set(
            incidents.get("required_fields"),
            required_incident_fields,
            "incident record fields",
            errors,
        )
        records = incidents.get("records")
        if not isinstance(records, list) or not records:
            errors.append("at least one incident-learning record is required")
        else:
            seen: set[str] = set()
            for index, record in enumerate(records):
                if (
                    not isinstance(record, dict)
                    or set(record) != required_incident_fields
                    or any(not nonempty(value) for value in record.values())
                ):
                    errors.append(f"incident record[{index}] is incomplete")
                    continue
                if record["incident_id"] in seen:
                    errors.append("incident IDs must be unique")
                seen.add(record["incident_id"])
                regression = PROJECT_ROOT / record["regression_test"]
                if not regression.is_file():
                    errors.append(
                        f"incident regression test is missing: {record['regression_test']}"
                    )

    explanation = policy.get("nontechnical_explanation")
    if not isinstance(explanation, dict):
        errors.append("nontechnical explanation policy is missing")
    else:
        exact_set(
            explanation.get("required_fields"),
            {
                "what_happened",
                "why_it_matters",
                "what_is_blocked",
                "what_the_user_can_do",
                "what_remains_unknown",
            },
            "nontechnical explanation fields",
            errors,
        )
        exact_set(
            explanation.get("must_distinguish"),
            {"proved", "not_proved", "rejected", "conditional", "human_decision"},
            "nontechnical explanation states",
            errors,
        )
        if explanation.get("fixture_only_cannot_prove_comprehension") is not True:
            errors.append("fixture text cannot prove real user comprehension")
        if explanation.get("real_user_comprehension_is") != (
            "human_onboarding_and_longitudinal_conditional"
        ):
            errors.append("real user comprehension stage differs")


def verify_scope_and_maintenance(
    policy: dict[str, Any], errors: list[str]
) -> None:
    scope = policy.get("scope_and_budget")
    if not isinstance(scope, dict):
        errors.append("scope and budget policy is missing")
    else:
        exact_set(
            scope.get("current_allowed"),
            {
                "single user",
                "local first",
                "paper only",
                "AI research and advice",
                "human final investment decision",
            },
            "allowed project scope",
            errors,
        )
        exact_set(
            scope.get("current_forbidden"),
            {
                "live broker execution",
                "real funds",
                "multi-user service",
                "commercial release",
                "unrelated private-data access",
            },
            "forbidden project scope",
            errors,
        )
        for field in (
            "every_packet_requires_finite_retry_budget",
            "budget_exhaustion_cannot_be_relabelled_success",
            "scope_expansion_requires_human_decision",
        ):
            if scope.get(field) is not True:
                errors.append(f"scope and budget {field} must be true")

    maintenance = policy.get("maintainability_and_migration")
    if not isinstance(maintenance, dict):
        errors.append("maintainability and migration policy is missing")
        return
    exact_set(
        maintenance.get("new_component_required_fields"),
        {
            "owner",
            "contract",
            "tests",
            "observability",
            "failure_mode",
            "dependency_cost",
            "removal_path",
        },
        "new component maintainability fields",
        errors,
    )
    if maintenance.get("rename_only_rewrite_allowed") is not False:
        errors.append("terminology-only rewrites must be forbidden")
    exact_set(
        maintenance.get("migration_required_fields"),
        {
            "source_version",
            "target_version",
            "dry_run",
            "backup",
            "rollback",
            "post_migration_invariants",
            "compatibility_or_explicit_break",
        },
        "migration safety fields",
        errors,
    )
    if maintenance.get("missing_exit_plan_outcome") != "not_adopted":
        errors.append("components without an exit plan must not be adopted")


def verify_failure_coverage(policy: dict[str, Any], errors: list[str]) -> None:
    registry = load_json(FAILURE_REGISTRY, errors, "failure registry")
    registry_classes = registry.get("failure_classes")
    if not isinstance(registry_classes, list):
        errors.append("failure registry failure_classes must be a list")
        return
    class_by_id = {
        item.get("id"): item
        for item in registry_classes
        if isinstance(item, dict) and nonempty(item.get("id"))
    }
    noncovered_ids: list[str] = []
    status_counts = {
        "covered": 0,
        "partially_covered": 0,
        "gap": 0,
    }
    domain_counts: dict[str, dict[str, Any]] = {}
    alias_count = 0
    for index, item in enumerate(registry_classes):
        if not isinstance(item, dict):
            errors.append(f"failure registry failure_classes[{index}] is not an object")
            continue
        failure_id = item.get("id")
        domain = item.get("domain")
        status = item.get("status")
        open_gaps = item.get("open_gaps")
        aliases = item.get("aliases")
        if not nonempty(failure_id) or not nonempty(domain):
            errors.append(
                f"failure registry failure_classes[{index}] lacks id or domain"
            )
            continue
        if status not in ALLOWED_FAILURE_STATUSES:
            errors.append(f"failure registry {failure_id} status is invalid")
            continue
        if (
            not isinstance(open_gaps, list)
            or not all(nonempty(value) for value in open_gaps)
            or len(open_gaps) != len(set(open_gaps))
        ):
            errors.append(f"failure registry {failure_id} open_gaps is invalid")
            continue
        if status == "covered" and open_gaps:
            errors.append(
                f"failure registry {failure_id} cannot be covered with open gaps"
            )
        if status != "covered" and not open_gaps:
            errors.append(
                f"failure registry {failure_id} must name its remaining gaps"
            )
        if status != "covered":
            noncovered_ids.append(failure_id)
        status_counts[status] += 1
        if not isinstance(aliases, list) or not all(
            nonempty(value) for value in aliases
        ):
            errors.append(f"failure registry {failure_id} aliases is invalid")
        else:
            alias_count += len(aliases)
        domain_record = domain_counts.setdefault(
            domain,
            {
                "domain": domain,
                "total": 0,
                "covered": 0,
                "partially_covered": 0,
                "gaps": 0,
            },
        )
        domain_record["total"] += 1
        if status == "gap":
            domain_record["gaps"] += 1
        else:
            domain_record[status] += 1

    for failure_id, (_, case_id) in EXPECTED_FAILURE_CASES.items():
        item = class_by_id.get(failure_id)
        if not isinstance(item, dict):
            errors.append(f"project-method failure class is missing: {failure_id}")
            continue
        required_bindings = (
            ("requirement_ids", "REQ-METHOD-001"),
            ("control_ids", "CTRL-PROJECT-METHOD"),
            ("verification_ids", "V-PROJECT-METHOD"),
            ("acceptance_case_ids", case_id),
        )
        for field, expected_id in required_bindings:
            values = item.get(field)
            if not isinstance(values, list) or expected_id not in values:
                errors.append(
                    f"project-method failure class {failure_id} lacks "
                    f"{field} binding {expected_id}"
                )

    if registry.get("open_gaps") != noncovered_ids:
        errors.append(
            "failure registry open_gaps must be derived from non-covered entries"
        )
    summary = registry.get("coverage_summary")
    expected_summary = {
        "total_failure_classes": len(registry_classes),
        "covered_failure_classes": status_counts["covered"],
        "partially_covered_failure_classes": status_counts[
            "partially_covered"
        ],
        "gap_failure_classes": status_counts["gap"],
        "alias_count": alias_count,
        "domains": list(domain_counts.values()),
        "open_gap_ids": noncovered_ids,
    }
    if summary != expected_summary:
        errors.append(
            "failure registry coverage summary must be derived from entries"
        )

    coverage = policy.get("failure_coverage")
    if not isinstance(coverage, list):
        errors.append("project-method failure coverage must be a list")
        return
    observed: dict[str, tuple[str, str]] = {}
    case_ids: set[str] = set()
    for index, item in enumerate(coverage):
        if (
            not isinstance(item, dict)
            or set(item) != {"failure_id", "invariant_id", "case_id"}
        ):
            errors.append(f"project-method failure_coverage[{index}] differs")
            continue
        failure_id = item.get("failure_id")
        invariant_id = item.get("invariant_id")
        case_id = item.get("case_id")
        if (
            not nonempty(failure_id)
            or not nonempty(invariant_id)
            or not nonempty(case_id)
            or re.fullmatch(r"PM-[0-9]{2}-[A-Z0-9-]+", invariant_id) is None
            or re.fullmatch(r"CASE-METHOD-[A-Z0-9-]+", case_id) is None
        ):
            errors.append(f"project-method failure_coverage[{index}] has invalid IDs")
            continue
        if failure_id in observed:
            errors.append(f"duplicate project-method failure coverage: {failure_id}")
        if case_id in case_ids:
            errors.append(f"duplicate project-method case ID: {case_id}")
        observed[failure_id] = (invariant_id, case_id)
        case_ids.add(case_id)
    if observed != EXPECTED_FAILURE_CASES:
        errors.append("project-method failure-to-case mapping differs")


def verify() -> list[str]:
    errors: list[str] = []
    policy = load_json(POLICY_PATH, errors, "project method policy")
    if not policy:
        return errors
    if set(policy) != EXPECTED_TOP_LEVEL:
        errors.append("project method top-level schema differs")
    if type(policy.get("schema_version")) is not int or (
        policy.get("schema_version") != 1
    ):
        errors.append("project method schema_version must be integer 1")
    if policy.get("status") not in {"candidate_for_freeze", "frozen"}:
        errors.append("project method status differs")
    if policy.get("policy_id") != "ids-ai-project-method-v1":
        errors.append("project method policy_id differs")
    if not nonempty(policy.get("scope")):
        errors.append("project method scope is missing")

    verify_authority(policy, errors)
    verify_state_and_packets(policy, errors)
    verify_execution(policy, errors)
    verify_completion_and_review(policy, errors)
    verify_harness_and_supply_chain(policy, errors)
    verify_tests_incidents_and_explanations(policy, errors)
    verify_scope_and_maintenance(policy, errors)
    verify_failure_coverage(policy, errors)
    return errors


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: "
            f"{completed.stdout.strip() or '<no output>'}"
        )
    return completed.stdout.strip()


def git_blob_sha256(commit: str, repository_relative: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{repository_relative}"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git show {commit}:{repository_relative} failed: "
            f"{completed.stderr.decode('utf-8', 'replace').strip() or '<no output>'}"
        )
    return hashlib.sha256(completed.stdout).hexdigest()


def verify_closure_evidence(path: Path) -> list[str]:
    errors: list[str] = []
    receipt = load_json(path, errors, "project method closure evidence")
    if not receipt:
        return errors
    registry = load_json(FAILURE_REGISTRY, errors, "failure registry")
    registry_classes = registry.get("failure_classes")
    registry_by_id = (
        {
            item.get("id"): item
            for item in registry_classes
            if isinstance(item, dict) and nonempty(item.get("id"))
        }
        if isinstance(registry_classes, list)
        else {}
    )
    expected_top_level = {
        "schema_version",
        "verification_id",
        "executor_id",
        "status",
        "candidate_commit",
        "candidate_tree",
        "project_prefix",
        "policy_sha256",
        "failure_registry_sha256",
        "failure_results",
        "limitations",
    }
    if set(receipt) != expected_top_level:
        errors.append("project method closure evidence top-level schema differs")
        return errors
    if receipt.get("schema_version") != 1:
        errors.append("project method closure evidence schema_version differs")
    if receipt.get("verification_id") != "V-PROJECT-METHOD":
        errors.append("project method closure evidence verification_id differs")
    if receipt.get("executor_id") != "ids-project-method-acceptance-v1":
        errors.append("project method closure evidence executor_id differs")
    if receipt.get("status") != "pass":
        errors.append("project method closure evidence status is not pass")
    try:
        candidate_commit = git_text("rev-parse", "HEAD")
        candidate_tree = git_text("rev-parse", "HEAD^{tree}")
        project_prefix = git_text("rev-parse", "--show-prefix")
    except RuntimeError as exc:
        errors.append(str(exc))
        return errors
    if receipt.get("candidate_commit") != candidate_commit:
        errors.append("project method closure evidence candidate commit differs")
    if receipt.get("candidate_tree") != candidate_tree:
        errors.append("project method closure evidence candidate tree differs")
    if receipt.get("project_prefix") != project_prefix:
        errors.append("project method closure evidence project prefix differs")
    for field, source in (
        ("policy_sha256", POLICY_PATH),
        ("failure_registry_sha256", FAILURE_REGISTRY),
    ):
        value = receipt.get(field)
        if (
            not isinstance(value, str)
            or re.fullmatch(r"[0-9a-f]{64}", value) is None
            or value != sha256_file(source)
        ):
            errors.append(f"project method closure evidence {field} differs")
    for relative, source in (
        ("governance/PROJECT_METHOD_POLICY_V1.json", POLICY_PATH),
        ("governance/FAILURE_CLASSES_V1.json", FAILURE_REGISTRY),
    ):
        try:
            committed_hash = git_blob_sha256(
                candidate_commit,
                f"{project_prefix}{relative}",
            )
        except RuntimeError as exc:
            errors.append(str(exc))
            continue
        if committed_hash != sha256_file(source):
            errors.append(
                "project method closure evidence source differs from candidate "
                f"commit: {relative}"
            )

    results = receipt.get("failure_results")
    if not isinstance(results, list):
        errors.append("project method closure evidence failure_results must be a list")
        return errors
    by_id: dict[str, dict[str, Any]] = {}
    expected_result_fields = {
        "failure_id",
        "case_id",
        "outcome",
        "selector_observation",
        "oracle_observations",
        "raw_result",
        "raw_result_sha256",
        "residual_limitations",
        "conditional_gate_id",
    }
    for index, result in enumerate(results):
        if not isinstance(result, dict) or set(result) != expected_result_fields:
            errors.append(
                f"project method closure evidence failure_results[{index}] differs"
            )
            continue
        failure_id = result.get("failure_id")
        if failure_id in by_id:
            errors.append(
                f"project method closure evidence duplicates {failure_id}"
            )
            continue
        by_id[failure_id] = result
        expected_case = EXPECTED_FAILURE_CASES.get(failure_id, (None, None))[1]
        if result.get("case_id") != expected_case:
            errors.append(
                f"project method closure evidence {failure_id} case_id differs"
            )
        outcome = result.get("outcome")
        if outcome not in {"mechanism_verified", "conditionally_deferred"}:
            errors.append(
                f"project method closure evidence {failure_id} outcome blocks closure"
            )
        conditional_gate = result.get("conditional_gate_id")
        registry_entry = registry_by_id.get(failure_id)
        registry_status = (
            registry_entry.get("status")
            if isinstance(registry_entry, dict)
            else None
        )
        if outcome == "conditionally_deferred":
            if (
                CONDITIONALLY_DEFERRED_FAILURES.get(failure_id)
                != conditional_gate
                or registry_status != "partially_covered"
            ):
                errors.append(
                    "project method closure evidence has an unauthorized "
                    f"conditional deferral for {failure_id}"
                )
        elif outcome == "mechanism_verified":
            if registry_status != "covered":
                errors.append(
                    "project method closure evidence cannot mark a non-covered "
                    f"registry entry verified: {failure_id}"
                )
            if conditional_gate is not None:
                errors.append(
                    f"project method closure evidence {failure_id} has a stray "
                    "conditional gate"
                )
        elif conditional_gate is not None:
            errors.append(
                f"project method closure evidence {failure_id} has a stray "
                "conditional gate"
            )
        if not nonempty(result.get("selector_observation")):
            errors.append(
                f"project method closure evidence {failure_id} lacks selector "
                "observation"
            )
        observations = result.get("oracle_observations")
        if (
            not isinstance(observations, list)
            or not observations
            or not all(nonempty(value) for value in observations)
        ):
            errors.append(
                f"project method closure evidence {failure_id} lacks oracle "
                "observations"
            )
        limitations = result.get("residual_limitations")
        if (
            not isinstance(limitations, list)
            or not limitations
            or not all(nonempty(value) for value in limitations)
        ):
            errors.append(
                f"project method closure evidence {failure_id} lacks residual "
                "limitations"
            )
        raw_result = result.get("raw_result")
        raw_hash = result.get("raw_result_sha256")
        if (
            not isinstance(raw_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", raw_hash) is None
            or raw_hash
            != hashlib.sha256(
                json.dumps(
                    raw_result,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
        ):
            errors.append(
                f"project method closure evidence {failure_id} raw-result hash "
                "differs"
            )
    if set(by_id) != set(EXPECTED_FAILURE_CASES):
        errors.append(
            "project method closure evidence failure result set differs"
        )
    limitations = receipt.get("limitations")
    if (
        not isinstance(limitations, list)
        or not limitations
        or not all(nonempty(value) for value in limitations)
    ):
        errors.append("project method closure evidence limitations are missing")
    return errors


def output(
    errors: Iterable[str],
    as_json: bool,
    *,
    closure_errors: Iterable[str] = (),
    require_closure: bool = False,
    closure_evidence: Path | None = None,
) -> int:
    values = list(errors)
    closure_values = list(closure_errors)
    failed = bool(values or (require_closure and closure_values))
    payload = {
        "status": "fail" if failed else "pass",
        "error_count": len(values) + (len(closure_values) if require_closure else 0),
        "errors": values + (closure_values if require_closure else []),
    }
    if require_closure:
        payload["closure_status"] = (
            "eligible" if not closure_values else "blocked"
        )
        payload["closure_error_count"] = len(closure_values)
        payload["closure_evidence_path"] = (
            str(closure_evidence) if closure_evidence is not None else None
        )
        payload["closure_evidence_sha256"] = (
            sha256_file(closure_evidence)
            if closure_evidence is not None and closure_evidence.is_file()
            else None
        )
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif failed:
        print("project method verification: FAIL")
        for error in payload["errors"]:
            print(f"- {error}")
    else:
        print("project method verification: PASS")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-closure", action="store_true")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=DEFAULT_CLOSURE_EVIDENCE,
    )
    args = parser.parse_args()
    closure_errors = (
        verify_closure_evidence(args.evidence)
        if args.require_closure
        else []
    )
    return output(
        verify(),
        args.json,
        closure_errors=closure_errors,
        require_closure=args.require_closure,
        closure_evidence=args.evidence if args.require_closure else None,
    )


if __name__ == "__main__":
    sys.exit(main())
