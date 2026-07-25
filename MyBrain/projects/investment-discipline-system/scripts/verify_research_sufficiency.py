#!/usr/bin/env python3
"""Recompute research pre-review eligibility from the frozen receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECEIPT = PROJECT_ROOT / "governance" / "RESEARCH_SUFFICIENCY_V1.json"
TOPIC_IDS = {"RS-01", "RS-02", "RS-03", "RS-04", "RS-05"}
PRE_REVIEW_RULE_IDS = {
    "DR-01",
    "DR-02",
    "DR-03",
    "DR-04",
    "DR-05",
    "DR-06",
    "DR-07",
    "DR-08",
    "DR-09",
    "DR-10",
    "DR-12",
    "DR-13",
}
ALLOWED_REVISION_STATES = {
    "content_hash_verified_current",
    "fixed_commit_verified",
    "revision_graph_checked_current",
}
ALLOWED_ENTAILMENT = {"entailed", "contested_non_decision_changing"}
ALLOWED_REVIEW_STATES = {
    "deterministic_receipt",
    "explicit_human_receipt",
    "independent_review_receipt",
}
ALLOWED_DELTA_STATES = {"accepted", "deferred", "rejected"}
ALLOWED_GAP_STATES = {
    "pre_review_blocking",
    "final_closure_gate",
    "product_release_conditional",
    "human_onboarding_conditional",
    "longitudinal_conditional",
    "resolved",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rule_result(
    rule_id: str,
    *,
    failed_topic_ids: list[str] | None = None,
    failed_gap_ids: list[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": rule_id,
        "result": (
            "fail" if failed_topic_ids or failed_gap_ids else "pass"
        ),
    }
    if failed_topic_ids:
        result["failed_topic_ids"] = sorted(failed_topic_ids)
    if failed_gap_ids:
        result["failed_gap_ids"] = sorted(failed_gap_ids)
    return result


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def safe_relative(value: Any) -> str | None:
    if (
        not isinstance(value, str)
        or not value
        or Path(value).is_absolute()
        or ".." in Path(value).parts
    ):
        return None
    return value


def preregistration_bytes(commit: str, relative: str) -> bytes | None:
    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if root_result.returncode != 0:
        return None
    repository_root = Path(
        root_result.stdout.decode("utf-8", "replace").strip()
    ).resolve()
    try:
        project_prefix = PROJECT_ROOT.relative_to(repository_root)
    except ValueError:
        return None
    repository_relative = (project_prefix / relative).as_posix()
    commit_result = subprocess.run(
        ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if (
        commit_result.returncode != 0
        or commit_result.stdout.decode("ascii", "replace").strip() != commit
    ):
        return None
    ancestor_result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if ancestor_result.returncode != 0:
        return None
    file_result = subprocess.run(
        ["git", "show", f"{commit}:{repository_relative}"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return file_result.stdout if file_result.returncode == 0 else None


def evaluate(document: dict[str, Any]) -> dict[str, Any]:
    topics = document.get("topics")
    gaps = document.get("open_gaps")
    if not isinstance(topics, list):
        topics = []
    if not isinstance(gaps, list):
        gaps = []
    topic_by_id = {
        item.get("id"): item
        for item in topics
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    results: list[dict[str, Any]] = []

    observed_topic_ids = set(topic_by_id)
    dr01_failed = (
        sorted(TOPIC_IDS ^ observed_topic_ids)
        if observed_topic_ids != TOPIC_IDS
        else []
    )
    results.append(rule_result("DR-01", failed_topic_ids=dr01_failed))

    failed: list[str] = []
    for topic_id, topic in topic_by_id.items():
        registration = topic.get("preregistration")
        commit = (
            registration.get("git_commit")
            if isinstance(registration, dict)
            else None
        )
        artifact_path = (
            safe_relative(registration.get("artifact_path"))
            if isinstance(registration, dict)
            else None
        )
        artifact_hash = (
            registration.get("artifact_sha256")
            if isinstance(registration, dict)
            else None
        )
        proof = (
            registration.get("timing_proof")
            if isinstance(registration, dict)
            else None
        )
        artifact_bytes = (
            preregistration_bytes(commit, artifact_path)
            if isinstance(commit, str) and artifact_path is not None
            else None
        )
        try:
            preregistration = (
                json.loads(artifact_bytes)
                if artifact_bytes is not None
                else None
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            preregistration = None
        preregistered_topic_ids = {
            item.get("topic_id")
            for item in (
                preregistration.get("questions", [])
                if isinstance(preregistration, dict)
                else []
            )
            if isinstance(item, dict)
        }
        if (
            not isinstance(registration, dict)
            or registration.get("timing_state") != "verified_before_search"
            or not isinstance(commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", commit) is None
            or artifact_path is None
            or not isinstance(artifact_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", artifact_hash) is None
            or artifact_bytes is None
            or hashlib.sha256(artifact_bytes).hexdigest() != artifact_hash
            or not isinstance(preregistration, dict)
            or preregistration.get("status")
            != "preregistered_before_counted_search"
            or preregistered_topic_ids != TOPIC_IDS
            or not isinstance(proof, dict)
            or proof.get("executor_platform") != "Codex App subagents"
            or not isinstance(proof.get("agent_or_thread_locators"), list)
            or not proof["agent_or_thread_locators"]
            or not all(
                nonempty(locator)
                for locator in proof["agent_or_thread_locators"]
            )
            or not nonempty(proof.get("observable_limitation"))
        ):
            failed.append(topic_id)
    results.append(rule_result("DR-02", failed_topic_ids=failed))

    failed = []
    preregistration_documents: dict[str, dict[str, Any]] = {}
    for topic_id, topic in topic_by_id.items():
        registration = topic.get("preregistration")
        if isinstance(registration, dict):
            commit = registration.get("git_commit")
            relative = safe_relative(registration.get("artifact_path"))
            if isinstance(commit, str) and relative is not None:
                payload = preregistration_bytes(commit, relative)
                try:
                    parsed = json.loads(payload) if payload is not None else None
                except (UnicodeDecodeError, json.JSONDecodeError):
                    parsed = None
                if isinstance(parsed, dict):
                    preregistration_documents[topic_id] = parsed
        protocol = topic.get("search_protocol")
        budget = protocol.get("budget") if isinstance(protocol, dict) else None
        executions = (
            protocol.get("search_executions")
            if isinstance(protocol, dict)
            else None
        )
        if not isinstance(budget, dict):
            failed.append(topic_id)
            continue
        query_limit = budget.get("planned_query_limit")
        round_limit = budget.get("planned_supplemental_round_limit")
        consumed_queries = budget.get("consumed_query_count")
        consumed_rounds = budget.get("consumed_supplemental_round_count")
        preregistration = preregistration_documents.get(topic_id, {})
        prereg_budget = preregistration.get("budget")
        execution_ids = [
            item.get("id")
            for item in executions
            if isinstance(item, dict)
        ] if isinstance(executions, list) else []
        execution_shape_valid = (
            isinstance(executions, list)
            and bool(executions)
            and len(execution_ids) == len(set(execution_ids))
            and all(
                isinstance(item, dict)
                and nonempty(item.get("id"))
                and nonempty(item.get("retrieved_at"))
                and nonempty(item.get("channel"))
                and nonempty(item.get("exact_query"))
                and nonempty(item.get("executor_locator"))
                and type(item.get("result_count")) is int
                and item["result_count"] >= 0
                and isinstance(item.get("result_source_ids"), list)
                for item in executions
            )
        )
        if (
            budget.get("registration_state") != "frozen_before_search"
            or budget.get("consumption_receipt_state") != "complete"
            or type(query_limit) is not int
            or query_limit < 1
            or type(round_limit) is not int
            or round_limit < 1
            or type(consumed_queries) is not int
            or not 0 <= consumed_queries <= query_limit
            or type(consumed_rounds) is not int
            or not 0 <= consumed_rounds <= round_limit
            or not isinstance(prereg_budget, dict)
            or query_limit != prereg_budget.get("per_topic_query_limit")
            or round_limit != prereg_budget.get("supplemental_round_limit")
            or not execution_shape_valid
            or consumed_queries != len(executions)
        ):
            failed.append(topic_id)
    results.append(rule_result("DR-03", failed_topic_ids=failed))

    failed = []
    source_by_topic: dict[str, dict[str, dict[str, Any]]] = {}
    for topic_id, topic in topic_by_id.items():
        protocol = topic.get("search_protocol")
        outcomes = topic.get("source_outcomes")
        if (
            not isinstance(protocol, dict)
            or protocol.get("result_set_state") != "frozen_complete"
            or not isinstance(outcomes, list)
            or not outcomes
        ):
            failed.append(topic_id)
            continue
        source_map: dict[str, dict[str, Any]] = {}
        topic_failed = False
        for source in outcomes:
            if not isinstance(source, dict):
                topic_failed = True
                continue
            source_id = source.get("id")
            decision = source.get("screening_decision")
            reason = source.get("screening_reason")
            required_strings = (
                "retrieved_at",
                "channel",
                "exact_query_or_locator",
                "locator",
                "observed_result",
                "source_class",
                "revision_state",
                "evidence_fingerprint",
            )
            query_ids = source.get("query_ids")
            if (
                not isinstance(source_id, str)
                or source_id in source_map
                or decision
                not in {
                    "included",
                    "included_limited",
                    "excluded_from_claim_support",
                }
                or not nonempty(reason)
                or any(not nonempty(source.get(key)) for key in required_strings)
                or not isinstance(source.get("cluster_ids"), list)
                or not isinstance(query_ids, list)
                or not query_ids
            ):
                topic_failed = True
                continue
            source_map[source_id] = source
        executions = protocol.get("search_executions")
        execution_map = {
            item.get("id"): item
            for item in executions
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        } if isinstance(executions, list) else {}
        declared_result_ids: list[str] = []
        for execution in execution_map.values():
            result_source_ids = execution.get("result_source_ids")
            if not isinstance(result_source_ids, list):
                topic_failed = True
                continue
            declared_result_ids.extend(result_source_ids)
            if execution.get("result_count") != len(result_source_ids):
                topic_failed = True
        if (
            len(declared_result_ids) != len(set(declared_result_ids))
            or set(declared_result_ids) != set(source_map)
        ):
            topic_failed = True
        for source in source_map.values():
            query_ids = source.get("query_ids")
            if (
                not isinstance(query_ids, list)
                or not set(query_ids).issubset(execution_map)
            ):
                topic_failed = True
        source_by_topic[topic_id] = source_map
        if topic_failed:
            failed.append(topic_id)
    results.append(rule_result("DR-04", failed_topic_ids=failed))

    failed = []
    cluster_by_topic: dict[str, dict[str, dict[str, Any]]] = {}
    for topic_id, topic in topic_by_id.items():
        protocol = topic.get("search_protocol")
        required_classes = (
            set(protocol.get("required_source_classes", []))
            if isinstance(protocol, dict)
            else set()
        )
        source_map = source_by_topic.get(topic_id, {})
        observed_classes = {
            source.get("source_class")
            for source in source_map.values()
            if source.get("screening_decision")
            in {"included", "included_limited"}
        }
        clusters = topic.get("evidence_clusters")
        cluster_map: dict[str, dict[str, Any]] = {}
        topic_failed = not required_classes.issubset(observed_classes)
        if not isinstance(clusters, list) or not clusters:
            topic_failed = True
            clusters = []
        for cluster in clusters:
            if not isinstance(cluster, dict):
                topic_failed = True
                continue
            cluster_id = cluster.get("id")
            members = cluster.get("member_source_ids")
            roots = cluster.get("upstream_roots")
            if (
                not isinstance(cluster_id, str)
                or cluster_id in cluster_map
                or not isinstance(members, list)
                or not members
                or not set(members).issubset(source_map)
                or not isinstance(roots, list)
                or not roots
                or not all(nonempty(root) for root in roots)
                or cluster.get("revision_check_state")
                not in ALLOWED_REVISION_STATES
            ):
                topic_failed = True
                continue
            cluster_map[cluster_id] = cluster
        cluster_by_topic[topic_id] = cluster_map
        for source in source_map.values():
            if source.get("screening_decision") not in {
                "included",
                "included_limited",
            }:
                continue
            cluster_ids = source.get("cluster_ids")
            if (
                not isinstance(cluster_ids, list)
                or not cluster_ids
                or not set(cluster_ids).issubset(cluster_map)
            ):
                topic_failed = True
        if topic_failed:
            failed.append(topic_id)
    results.append(rule_result("DR-05", failed_topic_ids=failed))

    failed = []
    for topic_id, topic in topic_by_id.items():
        claims = topic.get("claims")
        cluster_ids = set(cluster_by_topic.get(topic_id, {}))
        topic_failed = not isinstance(claims, list) or not claims
        if not isinstance(claims, list):
            claims = []
        for claim in claims:
            if not isinstance(claim, dict) or claim.get("impact") != "high":
                topic_failed = True
                continue
            evidence_ids = claim.get("evidence_cluster_ids")
            if (
                claim.get("entailment_status") not in ALLOWED_ENTAILMENT
                or claim.get("review_state") not in ALLOWED_REVIEW_STATES
                or not isinstance(evidence_ids, list)
                or not evidence_ids
                or not set(evidence_ids).issubset(cluster_ids)
                or not nonempty(claim.get("source_range_or_receipt"))
                or not nonempty(claim.get("limitations"))
                or not nonempty(claim.get("decision_effect"))
            ):
                topic_failed = True
        if topic_failed:
            failed.append(topic_id)
    results.append(rule_result("DR-06", failed_topic_ids=failed))

    failed = []
    for topic_id, topic in topic_by_id.items():
        rounds = topic.get("supplemental_rounds")
        if not isinstance(rounds, list) or not rounds:
            failed.append(topic_id)
            continue
        last_delta_index = -1
        for index, round_item in enumerate(rounds):
            if not isinstance(round_item, dict):
                continue
            if round_item.get("architecture_delta_ids") or round_item.get(
                "decision_delta_ids"
            ):
                last_delta_index = index
        stable_after = [
            item
            for item in rounds[last_delta_index + 1 :]
            if isinstance(item, dict)
            and item.get("result") == "completed_stable"
            and not item.get("architecture_delta_ids")
            and not item.get("decision_delta_ids")
            and not item.get("new_high_impact_node_ids")
        ]
        if not stable_after:
            failed.append(topic_id)
    results.append(rule_result("DR-07", failed_topic_ids=failed))

    failed = []
    for topic_id, topic in topic_by_id.items():
        contradictions = topic.get("unresolved_contradictions")
        if not isinstance(contradictions, list):
            failed.append(topic_id)
            continue
        if any(
            isinstance(item, dict)
            and item.get("state") == "open"
            and item.get("decision_effect")
            in {"architecture_changing", "decision_changing"}
            for item in contradictions
        ):
            failed.append(topic_id)
    results.append(rule_result("DR-08", failed_topic_ids=failed))

    failed = []
    for topic_id, topic in topic_by_id.items():
        deltas = topic.get("deltas")
        if not isinstance(deltas, dict):
            failed.append(topic_id)
            continue
        topic_failed = False
        for kind in ("architecture", "decisions"):
            entries = deltas.get(kind)
            if not isinstance(entries, list):
                topic_failed = True
                continue
            for delta in entries:
                if (
                    not isinstance(delta, dict)
                    or any(
                        not nonempty(delta.get(field))
                        for field in (
                            "id",
                            "source_locator",
                            "authority",
                            "status",
                            "rationale",
                            "disposition",
                        )
                    )
                    or delta.get("status") not in ALLOWED_DELTA_STATES
                    or delta.get("disposition") not in ALLOWED_DELTA_STATES
                ):
                    topic_failed = True
        if topic_failed:
            failed.append(topic_id)
    results.append(rule_result("DR-09", failed_topic_ids=failed))

    failed = []
    claim_ids_by_topic = {
        topic_id: {
            claim.get("id")
            for claim in topic.get("claims", [])
            if isinstance(claim, dict)
        }
        for topic_id, topic in topic_by_id.items()
    }
    for topic_id, topic in topic_by_id.items():
        triggers = topic.get("reopen_triggers")
        topic_failed = not isinstance(triggers, list) or not triggers
        if not isinstance(triggers, list):
            triggers = []
        for trigger in triggers:
            affected = (
                trigger.get("affected_claim_ids")
                if isinstance(trigger, dict)
                else None
            )
            if (
                not isinstance(trigger, dict)
                or not nonempty(trigger.get("condition"))
                or not nonempty(trigger.get("action"))
                or not isinstance(affected, list)
                or not affected
                or not set(affected).issubset(claim_ids_by_topic[topic_id])
            ):
                topic_failed = True
        if topic_failed:
            failed.append(topic_id)
    results.append(rule_result("DR-10", failed_topic_ids=failed))

    failed_gap_ids: list[str] = []
    seen_gap_ids: set[str] = set()
    for gap in gaps:
        if not isinstance(gap, dict):
            failed_gap_ids.append("<invalid>")
            continue
        gap_id = gap.get("id")
        state = gap.get("state")
        if (
            not isinstance(gap_id, str)
            or gap_id in seen_gap_ids
            or state not in ALLOWED_GAP_STATES
        ):
            failed_gap_ids.append(str(gap_id))
            continue
        seen_gap_ids.add(gap_id)
        if state == "pre_review_blocking":
            failed_gap_ids.append(gap_id)
    results.append(rule_result("DR-12", failed_gap_ids=failed_gap_ids))

    input_failures: list[str] = []
    rules = document.get("derivation_rules")
    snapshot = rules.get("input_snapshot") if isinstance(rules, dict) else None
    if not isinstance(snapshot, list) or not snapshot:
        input_failures.append("<missing-input-snapshot>")
    else:
        for item in snapshot:
            if not isinstance(item, dict):
                input_failures.append("<invalid-input>")
                continue
            relative = item.get("path")
            expected = item.get("sha256")
            if (
                not isinstance(relative, str)
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
                or not isinstance(expected, str)
                or re.fullmatch(r"[0-9a-f]{64}", expected) is None
            ):
                input_failures.append(str(relative))
                continue
            path = PROJECT_ROOT / relative
            if not path.is_file() or sha256(path) != expected:
                input_failures.append(relative)
    results.append(rule_result("DR-13", failed_topic_ids=input_failures))

    passed = all(
        item["result"] == "pass"
        for item in results
        if item["id"] in PRE_REVIEW_RULE_IDS
    )
    return {
        "derived_pre_review_eligible": passed,
        "derived_research_state": (
            "candidate_pre_review_eligible" if passed else "bounded_incomplete"
        ),
        "evaluated_input_sha256_state": (
            "matched"
            if next(item for item in results if item["id"] == "DR-13")[
                "result"
            ]
            == "pass"
            else "mismatch"
        ),
        "rule_results": results,
    }


def verify_document(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if document.get("schema_version") != 2:
        errors.append("research sufficiency schema_version differs")
    if document.get("status") not in {"candidate_for_freeze", "frozen"}:
        errors.append("research sufficiency lifecycle status differs")
    rules = document.get("derivation_rules")
    if not isinstance(rules, dict):
        errors.append("research sufficiency derivation_rules must be an object")
        return errors
    predicate_ids = {
        item.get("id")
        for item in rules.get("predicates", [])
        if isinstance(item, dict)
    }
    if predicate_ids != PRE_REVIEW_RULE_IDS | {"DR-11"}:
        errors.append("research sufficiency predicate IDs differ")
    expression = rules.get("pre_review_closure_expression")
    if (
        not isinstance(expression, dict)
        or expression.get("operator") != "all"
        or set(expression.get("predicate_ids", [])) != PRE_REVIEW_RULE_IDS
    ):
        errors.append("research pre-review closure expression differs")
    evaluation = evaluate(document)
    if (
        document.get("derived_pre_review_eligible")
        != evaluation["derived_pre_review_eligible"]
    ):
        errors.append("derived_pre_review_eligible was not recomputed")
    if document.get("derived_research_state") != evaluation[
        "derived_research_state"
    ]:
        errors.append("derived_research_state was not recomputed")
    if rules.get("current_evaluation") != {
        "derived_research_state": evaluation["derived_research_state"],
        "evaluated_input_sha256_state": evaluation[
            "evaluated_input_sha256_state"
        ],
        "rule_results": evaluation["rule_results"],
    }:
        errors.append("research sufficiency current_evaluation differs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        document = json.loads(RECEIPT.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        errors = [f"cannot load research sufficiency receipt: {exc}"]
        document = {}
    else:
        errors = verify_document(document)
    evaluation = evaluate(document)
    if args.json:
        print(
            json.dumps(
                {
                    "status": "fail" if errors else "pass",
                    "errors": errors,
                    **evaluation,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    elif errors:
        print("research sufficiency verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "research sufficiency verification: PASS "
            f"({evaluation['derived_research_state']})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
