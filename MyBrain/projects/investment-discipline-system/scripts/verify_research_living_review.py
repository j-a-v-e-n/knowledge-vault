#!/usr/bin/env python3
"""Verify deterministic freshness and event reopening for research evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = (
    PROJECT_ROOT / "governance" / "RESEARCH_LIVING_REVIEW_POLICY_V1.json"
)
DEFAULT_STATE = (
    PROJECT_ROOT / "governance" / "RESEARCH_LIVING_REVIEW_STATE_V1.json"
)
EXPECTED_POLICY_FIELDS = {
    "accepted_independent_review_requires",
    "clock_contract",
    "derived_living_review_statuses",
    "event_triggers",
    "network_contract",
    "policy_id",
    "precedence",
    "scheduled_review",
    "schema_version",
    "scope",
    "stale_propagation",
    "status",
}
EXPECTED_STATE_FIELDS = {
    "event_log",
    "latest_accepted_independent_review",
    "latest_refresh",
    "policy_id",
    "research_subject",
    "schema_version",
}
EXPECTED_REVIEW_REQUIREMENTS = {
    "candidate_bound",
    "reviewer_read_only",
    "artifact_set_exact",
    "receipt_hash_matches",
    "no_open_critical_or_major_finding",
}
EXPECTED_STATUSES = [
    "current",
    "blocked_pending_independent_review",
    "stale_due_to_event",
    "stale_due_to_time",
    "invalid",
]
EXPECTED_PRECEDENCE = [
    "invalid",
    "blocked_pending_independent_review",
    "stale_due_to_event",
    "stale_due_to_time",
    "current",
]
SHA256_LENGTH = 64


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_iso_date(value: Any, field: str, errors: list[str]) -> date | None:
    if not isinstance(value, str):
        errors.append(f"{field} must be an ISO date string")
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        errors.append(f"{field} must use YYYY-MM-DD")
        return None
    if parsed.isoformat() != value:
        errors.append(f"{field} must use canonical YYYY-MM-DD")
        return None
    return parsed


def safe_path(root: Path, value: Any, field: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a nonempty relative path")
        return None
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{field} must stay inside the project")
        return None
    resolved_root = root.resolve()
    resolved = (resolved_root / relative).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        errors.append(f"{field} escapes the project")
        return None
    return resolved


def verify_artifact_set(
    root: Path,
    artifacts: Any,
    field: str,
    errors: list[str],
) -> list[tuple[str, str]]:
    if not isinstance(artifacts, list) or not artifacts:
        errors.append(f"{field} must be a nonempty list")
        return []
    observed: list[tuple[str, str]] = []
    seen: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"{field}[{index}]"
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
            errors.append(f"{prefix} must contain exactly path and sha256")
            continue
        path_value = artifact.get("path")
        hash_value = artifact.get("sha256")
        path = safe_path(root, path_value, f"{prefix}.path", errors)
        if not isinstance(hash_value, str) or len(hash_value) != SHA256_LENGTH:
            errors.append(f"{prefix}.sha256 must be a 64-character digest")
            continue
        if path_value in seen:
            errors.append(f"{prefix}.path is duplicated")
            continue
        seen.add(path_value)
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"{prefix}.path does not exist")
            continue
        observed_hash = sha256(path)
        if observed_hash != hash_value:
            errors.append(
                f"{prefix}.sha256 mismatch: expected {hash_value}, "
                f"observed {observed_hash}"
            )
            continue
        observed.append((path_value, hash_value))
    return sorted(observed)


def evaluate(
    policy: dict[str, Any],
    state: dict[str, Any],
    *,
    project_root: Path,
    as_of: date,
) -> dict[str, Any]:
    errors: list[str] = []

    if set(policy) != EXPECTED_POLICY_FIELDS:
        errors.append("policy top-level fields are not exact")
    if set(state) != EXPECTED_STATE_FIELDS:
        errors.append("state top-level fields are not exact")
    if policy.get("schema_version") != 1 or state.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if policy.get("status") != "candidate_for_freeze":
        errors.append("policy status must be candidate_for_freeze")
    policy_id = policy.get("policy_id")
    if policy_id != "ids-research-living-review-v1":
        errors.append("unexpected policy_id")
    if state.get("policy_id") != policy_id:
        errors.append("state policy_id does not match policy")

    clock = policy.get("clock_contract")
    if clock != {
        "input": "explicit_cli_as_of",
        "format": "YYYY-MM-DD",
        "timezone": "UTC",
        "implicit_wall_clock_allowed": False,
        "as_of_before_refresh_outcome": "invalid",
    }:
        errors.append("clock_contract semantics changed")

    schedule = policy.get("scheduled_review")
    maximum_age_days: int | None = None
    if not isinstance(schedule, dict):
        errors.append("scheduled_review must be an object")
    else:
        maximum_age_days = schedule.get("maximum_age_days")
        if not isinstance(maximum_age_days, int) or maximum_age_days <= 0:
            errors.append("maximum_age_days must be a positive integer")
            maximum_age_days = None
        if schedule.get("fresh_through_due_date_inclusive") is not True:
            errors.append("fresh-through-due-date semantics changed")
        if (
            schedule.get("next_due_derivation")
            != "latest_accepted_independent_review.completed_on + maximum_age_days"
        ):
            errors.append("next_due_derivation semantics changed")

    requirements = policy.get("accepted_independent_review_requires")
    if (
        not isinstance(requirements, list)
        or set(requirements) != EXPECTED_REVIEW_REQUIREMENTS
        or len(requirements) != len(EXPECTED_REVIEW_REQUIREMENTS)
    ):
        errors.append("independent-review requirements changed")
    if policy.get("derived_living_review_statuses") != EXPECTED_STATUSES:
        errors.append("living-review statuses changed")
    if policy.get("precedence") != EXPECTED_PRECEDENCE:
        errors.append("living-review precedence changed")

    network = policy.get("network_contract")
    if not isinstance(network, dict) or network.get("verifier_may_access_network") is not False:
        errors.append("network verifier boundary changed")

    trigger_items = policy.get("event_triggers")
    trigger_ids: set[str] = set()
    if not isinstance(trigger_items, list) or not trigger_items:
        errors.append("event_triggers must be a nonempty list")
    else:
        for index, item in enumerate(trigger_items):
            if not isinstance(item, dict) or set(item) != {"id", "description"}:
                errors.append(
                    f"event_triggers[{index}] must contain exactly id and description"
                )
                continue
            trigger_id = item.get("id")
            description = item.get("description")
            if (
                not isinstance(trigger_id, str)
                or not trigger_id.startswith("LR-EVENT-")
                or trigger_id in trigger_ids
            ):
                errors.append(f"event_triggers[{index}].id is invalid or duplicated")
            else:
                trigger_ids.add(trigger_id)
            if not isinstance(description, str) or not description.strip():
                errors.append(f"event_triggers[{index}].description is empty")

    refresh = state.get("latest_refresh")
    refresh_date: date | None = None
    refresh_artifacts: list[tuple[str, str]] = []
    if not isinstance(refresh, dict) or set(refresh) != {
        "refresh_id",
        "completed_on",
        "artifacts",
        "claim_status",
    }:
        errors.append("latest_refresh fields are not exact")
    else:
        if not isinstance(refresh.get("refresh_id"), str) or not refresh.get(
            "refresh_id"
        ):
            errors.append("latest_refresh.refresh_id must be nonempty")
        refresh_date = parse_iso_date(
            refresh.get("completed_on"),
            "latest_refresh.completed_on",
            errors,
        )
        if refresh.get("claim_status") != "bounded_incomplete":
            errors.append("latest_refresh.claim_status must be bounded_incomplete")
        refresh_artifacts = verify_artifact_set(
            project_root,
            refresh.get("artifacts"),
            "latest_refresh.artifacts",
            errors,
        )
    if refresh_date is not None and as_of < refresh_date:
        errors.append("as_of is before latest_refresh.completed_on")

    open_event_ids: list[str] = []
    event_log = state.get("event_log")
    seen_event_records: set[str] = set()
    if not isinstance(event_log, list):
        errors.append("event_log must be a list")
        event_log = []
    for index, event in enumerate(event_log):
        prefix = f"event_log[{index}]"
        if not isinstance(event, dict) or set(event) != {
            "event_id",
            "trigger_id",
            "observed_on",
            "state",
            "evidence_path",
            "evidence_sha256",
            "resolution_receipt_path",
            "resolution_receipt_sha256",
        }:
            errors.append(f"{prefix} fields are not exact")
            continue
        event_id = event.get("event_id")
        trigger_id = event.get("trigger_id")
        if (
            not isinstance(event_id, str)
            or not event_id
            or event_id in seen_event_records
        ):
            errors.append(f"{prefix}.event_id is invalid or duplicated")
        else:
            seen_event_records.add(event_id)
        if trigger_id not in trigger_ids:
            errors.append(f"{prefix}.trigger_id is not declared")
        observed_on = parse_iso_date(event.get("observed_on"), f"{prefix}.observed_on", errors)
        if observed_on is not None and observed_on > as_of:
            errors.append(f"{prefix}.observed_on is after as_of")
        evidence = verify_artifact_set(
            project_root,
            [
                {
                    "path": event.get("evidence_path"),
                    "sha256": event.get("evidence_sha256"),
                }
            ],
            f"{prefix}.evidence",
            errors,
        )
        if len(evidence) != 1:
            errors.append(f"{prefix} must have one valid evidence artifact")
        event_state = event.get("state")
        if event_state == "open":
            if (
                event.get("resolution_receipt_path") is not None
                or event.get("resolution_receipt_sha256") is not None
            ):
                errors.append(f"{prefix} open event cannot have a resolution receipt")
            if isinstance(event_id, str):
                open_event_ids.append(event_id)
        elif event_state == "resolved":
            resolution = verify_artifact_set(
                project_root,
                [
                    {
                        "path": event.get("resolution_receipt_path"),
                        "sha256": event.get("resolution_receipt_sha256"),
                    }
                ],
                f"{prefix}.resolution_receipt",
                errors,
            )
            if len(resolution) != 1:
                errors.append(f"{prefix} resolved event needs a valid receipt")
        else:
            errors.append(f"{prefix}.state must be open or resolved")

    review = state.get("latest_accepted_independent_review")
    next_due: date | None = None
    if review is not None:
        expected_review_fields = {
            "review_id",
            "completed_on",
            "candidate_bound",
            "reviewer_read_only",
            "reviewed_artifacts",
            "receipt_path",
            "receipt_sha256",
            "open_critical_count",
            "open_major_count",
        }
        if not isinstance(review, dict) or set(review) != expected_review_fields:
            errors.append("latest_accepted_independent_review fields are not exact")
        else:
            review_date = parse_iso_date(
                review.get("completed_on"),
                "latest_accepted_independent_review.completed_on",
                errors,
            )
            if review_date is not None and review_date > as_of:
                errors.append("independent review completed_on is after as_of")
            if (
                review_date is not None
                and refresh_date is not None
                and review_date < refresh_date
            ):
                errors.append("independent review predates latest refresh")
            if not isinstance(review.get("review_id"), str) or not review.get(
                "review_id"
            ):
                errors.append("independent review_id must be nonempty")
            if review.get("candidate_bound") is not True:
                errors.append("independent review must be candidate_bound")
            if review.get("reviewer_read_only") is not True:
                errors.append("independent reviewer must be read-only")
            reviewed_artifacts = review.get("reviewed_artifacts")
            if not isinstance(reviewed_artifacts, list):
                errors.append("reviewed_artifacts must be a list")
            else:
                normalized = sorted(
                    (item.get("path"), item.get("sha256"))
                    for item in reviewed_artifacts
                    if isinstance(item, dict)
                    and set(item) == {"path", "sha256"}
                    and isinstance(item.get("path"), str)
                    and isinstance(item.get("sha256"), str)
                )
                if len(normalized) != len(reviewed_artifacts):
                    errors.append("reviewed_artifacts entries are malformed")
                if normalized != refresh_artifacts:
                    errors.append("reviewed_artifacts do not exactly match refresh")
            receipt = verify_artifact_set(
                project_root,
                [
                    {
                        "path": review.get("receipt_path"),
                        "sha256": review.get("receipt_sha256"),
                    }
                ],
                "latest_accepted_independent_review.receipt",
                errors,
            )
            if len(receipt) != 1:
                errors.append("independent review receipt is invalid")
            for count_field in ("open_critical_count", "open_major_count"):
                count = review.get(count_field)
                if not isinstance(count, int) or isinstance(count, bool) or count != 0:
                    errors.append(f"{count_field} must equal integer zero")
            if review_date is not None and maximum_age_days is not None:
                next_due = review_date + timedelta(days=maximum_age_days)

    if errors:
        living_status = "invalid"
    elif review is None:
        living_status = "blocked_pending_independent_review"
    elif open_event_ids:
        living_status = "stale_due_to_event"
    elif next_due is not None and as_of > next_due:
        living_status = "stale_due_to_time"
    else:
        living_status = "current"

    return {
        "schema_version": 1,
        "verifier": "verify_research_living_review.py",
        "verification_status": "invalid" if errors else "valid",
        "living_review_status": living_status,
        "as_of": as_of.isoformat(),
        "latest_refresh_id": (
            refresh.get("refresh_id") if isinstance(refresh, dict) else None
        ),
        "tracked_artifact_count": len(refresh_artifacts),
        "next_due": next_due.isoformat() if next_due is not None else None,
        "open_event_ids": sorted(open_event_ids),
        "errors": errors,
        "claim_boundary": (
            "This receipt validates tracked bytes, review binding, explicit date "
            "arithmetic, and event state only. It does not perform network "
            "research, establish claim truth, or prove project completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--require-current", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    date_errors: list[str] = []
    as_of = parse_iso_date(args.as_of, "--as-of", date_errors)
    if as_of is None:
        receipt = {
            "schema_version": 1,
            "verifier": "verify_research_living_review.py",
            "verification_status": "invalid",
            "living_review_status": "invalid",
            "as_of": args.as_of,
            "latest_refresh_id": None,
            "tracked_artifact_count": 0,
            "next_due": None,
            "open_event_ids": [],
            "errors": date_errors,
            "claim_boundary": "The as-of date was invalid.",
        }
    else:
        try:
            policy = json.loads(args.policy.read_text(encoding="utf-8"))
            state = json.loads(args.state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            receipt = {
                "schema_version": 1,
                "verifier": "verify_research_living_review.py",
                "verification_status": "invalid",
                "living_review_status": "invalid",
                "as_of": as_of.isoformat(),
                "latest_refresh_id": None,
                "tracked_artifact_count": 0,
                "next_due": None,
                "open_event_ids": [],
                "errors": [str(exc)],
                "claim_boundary": "Policy or state could not be read.",
            }
        else:
            receipt = evaluate(
                policy,
                state,
                project_root=args.project_root,
                as_of=as_of,
            )

    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(
            "research living review "
            f"{receipt['verification_status']}: "
            f"{receipt['living_review_status']}"
        )
        for error in receipt["errors"]:
            print(f"- {error}")

    if receipt["verification_status"] != "valid":
        return 1
    if args.require_current and receipt["living_review_status"] != "current":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
