#!/usr/bin/env python3
"""Local, evidence-first opportunity-to-transaction workspace.

The program deliberately does not discover opportunities by itself. It provides
the deterministic record boundaries and state derivation needed to stop an AI
interpretation from silently becoming a market-validation claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "0.1"
WORKSPACE_VERSION = "0.1"

RECORD_DIRECTORIES = {
    "principle": "principles",
    "observation": "observations",
    "opportunity": "opportunities",
    "probe": "probes",
    "event": "events",
}

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

FORBIDDEN_DERIVED_FIELDS = {
    "status",
    "market_stage",
    "fulfillment_stage",
    "validated",
    "is_validated",
    "confidence_score",
    "demand_score",
}

OBSERVATION_FORBIDDEN_FIELDS = {
    "inference",
    "target_market",
    "solution",
    "budget",
    "willingness_to_pay",
    "why_might_pay",
}

PRINCIPLE_FORBIDDEN_FIELDS = {
    "observation_refs",
    "target_market",
    "buyer",
    "solution",
    "budget",
}

VISIBILITY_VALUES = {"explicit", "latent_indicator"}
EXTERNAL_ACTION_POLICIES = {
    "draft_only",
    "human_approval_each",
    "scoped_authorization",
}

EVENT_KINDS = {
    "offer_presented",
    "next_step_requested",
    "meeting_scheduled",
    "required_input_shared",
    "agreement_signed",
    "deposit_received",
    "payment_received",
    "repeat_payment_received",
    "declined",
    "no_response",
    "prototype_created",
    "delivery_sent",
    "delivery_accepted",
    "refund_requested",
    "refund_issued",
    "dispute_opened",
}

POSITIVE_MARKET_EVENT_TO_STAGE = {
    "offer_presented": "exposed",
    "next_step_requested": "interest",
    "meeting_scheduled": "interest",
    "required_input_shared": "commitment",
    "agreement_signed": "commitment",
    "deposit_received": "commitment",
    "payment_received": "paid",
    "repeat_payment_received": "repeat_paid",
}

MARKET_STAGES = [
    "hypothesis",
    "exposed",
    "interest",
    "commitment",
    "paid",
    "repeat_paid",
]

FULFILLMENT_EVENT_TO_STAGE = {
    "prototype_created": "prototype",
    "delivery_sent": "delivered",
    "delivery_accepted": "accepted",
}

FULFILLMENT_STAGES = ["not_started", "prototype", "delivered", "accepted"]

ISSUE_EVENT_KINDS = {
    "declined",
    "no_response",
    "refund_requested",
    "refund_issued",
    "dispute_opened",
}

EVIDENCE_ORIGINS = {
    "external_party",
    "payment_provider",
    "delivery_system",
    "owner_attestation",
    "system_log",
}

EXTERNAL_PARTY_ONLY_EVENTS = {
    "next_step_requested",
    "meeting_scheduled",
    "required_input_shared",
    "agreement_signed",
    "declined",
    "delivery_accepted",
    "refund_requested",
}

PAYMENT_EVENTS = {
    "deposit_received",
    "payment_received",
    "repeat_payment_received",
    "refund_issued",
}


@dataclass(frozen=True)
class ValidationIssue:
    location: str
    message: str

    def render(self) -> str:
        return f"{self.location}: {self.message}"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso8601(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_nonempty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(is_nonempty_string(item) for item in value)
    )


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def require_fields(
    record: dict[str, Any],
    fields: Iterable[str],
    location: str,
) -> list[ValidationIssue]:
    return [
        ValidationIssue(location, f"missing required field '{field}'")
        for field in fields
        if field not in record
    ]


def validate_common(record: Any, location: str) -> list[ValidationIssue]:
    if not isinstance(record, dict):
        return [ValidationIssue(location, "record must be a JSON object")]

    issues = require_fields(
        record,
        ("schema_version", "record_type", "id", "created_at"),
        location,
    )
    if issues:
        return issues

    if record["schema_version"] != SCHEMA_VERSION:
        issues.append(
            ValidationIssue(
                location,
                f"schema_version must be '{SCHEMA_VERSION}'",
            )
        )

    record_type = record["record_type"]
    if record_type not in RECORD_DIRECTORIES:
        issues.append(ValidationIssue(location, f"unknown record_type '{record_type}'"))

    record_id = record["id"]
    if not is_nonempty_string(record_id) or not ID_PATTERN.fullmatch(record_id):
        issues.append(
            ValidationIssue(
                location,
                "id must use lowercase letters, digits, dots, underscores, or hyphens",
            )
        )

    if not parse_iso8601(record["created_at"]):
        issues.append(ValidationIssue(location, "created_at must be ISO-8601"))

    forbidden = sorted(FORBIDDEN_DERIVED_FIELDS.intersection(record))
    if forbidden:
        issues.append(
            ValidationIssue(
                location,
                "derived validation fields are forbidden: " + ", ".join(forbidden),
            )
        )
    return issues


def validate_principle(record: dict[str, Any], location: str) -> list[ValidationIssue]:
    issues = require_fields(
        record,
        ("premises", "derivation", "prediction", "falsifier"),
        location,
    )
    forbidden = sorted(PRINCIPLE_FORBIDDEN_FIELDS.intersection(record))
    if forbidden:
        issues.append(
            ValidationIssue(
                location,
                "principle must remain independent of market observations: "
                + ", ".join(forbidden),
            )
        )
    for field in ("premises", "derivation"):
        if field in record and not is_nonempty_string_list(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string list"))
    for field in ("prediction", "falsifier"):
        if field in record and not is_nonempty_string(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string"))
    return issues


def validate_observation(record: dict[str, Any], location: str) -> list[ValidationIssue]:
    issues = require_fields(
        record,
        (
            "source",
            "captured_at",
            "actor_context",
            "verbatim_or_observable",
            "known_context",
            "unknown_context",
            "visibility",
        ),
        location,
    )
    forbidden = sorted(OBSERVATION_FORBIDDEN_FIELDS.intersection(record))
    if forbidden:
        issues.append(
            ValidationIssue(
                location,
                "observation contains interpretation fields: " + ", ".join(forbidden),
            )
        )

    source = record.get("source")
    if not isinstance(source, dict):
        issues.append(ValidationIssue(location, "source must be an object"))
    else:
        for field in ("kind", "locator"):
            if not is_nonempty_string(source.get(field)):
                issues.append(ValidationIssue(location, f"source.{field} must be non-empty"))

    if "captured_at" in record and not parse_iso8601(record["captured_at"]):
        issues.append(ValidationIssue(location, "captured_at must be ISO-8601"))
    if "actor_context" in record and not is_nonempty_string(record["actor_context"]):
        issues.append(ValidationIssue(location, "actor_context must be non-empty"))
    if "verbatim_or_observable" in record and not is_nonempty_string_list(
        record["verbatim_or_observable"]
    ):
        issues.append(
            ValidationIssue(location, "verbatim_or_observable must be a non-empty string list")
        )
    for field in ("known_context", "unknown_context"):
        if field in record and not (
            isinstance(record[field], list)
            and all(is_nonempty_string(item) for item in record[field])
        ):
            issues.append(ValidationIssue(location, f"{field} must be a string list"))
    if "visibility" in record and record["visibility"] not in VISIBILITY_VALUES:
        issues.append(
            ValidationIssue(
                location,
                "visibility must be 'explicit' or 'latent_indicator'",
            )
        )
    return issues


def validate_opportunity(record: dict[str, Any], location: str) -> list[ValidationIssue]:
    required = (
        "buyer",
        "situation",
        "value_gap",
        "value_hypothesis",
        "why_might_pay",
        "observation_refs",
        "principle_refs",
        "alternatives",
        "uncertainties",
        "disconfirming_signals",
    )
    issues = require_fields(record, required, location)
    for field in ("buyer", "situation", "value_gap", "value_hypothesis", "why_might_pay"):
        if field in record and not is_nonempty_string(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string"))
    for field in (
        "observation_refs",
        "principle_refs",
        "alternatives",
        "uncertainties",
        "disconfirming_signals",
    ):
        if field in record and not is_nonempty_string_list(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string list"))
    return issues


def validate_probe(record: dict[str, Any], location: str) -> list[ValidationIssue]:
    required = (
        "opportunity_ref",
        "claim_tested",
        "offer",
        "artifact",
        "target",
        "success_event_kinds",
        "failure_or_stop_events",
        "effort_boundary",
        "external_action_policy",
    )
    issues = require_fields(record, required, location)
    for field in (
        "opportunity_ref",
        "claim_tested",
        "offer",
        "artifact",
        "target",
        "effort_boundary",
    ):
        if field in record and not is_nonempty_string(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string"))

    for field in ("success_event_kinds", "failure_or_stop_events"):
        values = record.get(field)
        if values is not None and not is_nonempty_string_list(values):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string list"))
        elif values is not None:
            unknown = sorted(set(values).difference(EVENT_KINDS))
            if unknown:
                issues.append(
                    ValidationIssue(location, f"{field} contains unknown events: {', '.join(unknown)}")
                )

    success_events = set(record.get("success_event_kinds", []))
    if success_events and not success_events.intersection(POSITIVE_MARKET_EVENT_TO_STAGE):
        issues.append(
            ValidationIssue(
                location,
                "success_event_kinds must contain at least one externally observable market event",
            )
        )

    policy = record.get("external_action_policy")
    if policy is not None and policy not in EXTERNAL_ACTION_POLICIES:
        issues.append(
            ValidationIssue(
                location,
                "external_action_policy must be draft_only, human_approval_each, or scoped_authorization",
            )
        )
    if policy == "scoped_authorization" and not is_nonempty_string(record.get("authorization_ref")):
        issues.append(
            ValidationIssue(
                location,
                "scoped_authorization requires authorization_ref",
            )
        )
    return issues


def validate_event(record: dict[str, Any], location: str) -> list[ValidationIssue]:
    required = (
        "opportunity_ref",
        "event_kind",
        "occurred_at",
        "evidence_locator",
        "evidence_origin",
        "actor",
        "notes",
    )
    issues = require_fields(record, required, location)

    event_kind = record.get("event_kind")
    if event_kind is not None and event_kind not in EVENT_KINDS:
        issues.append(ValidationIssue(location, f"unknown event_kind '{event_kind}'"))
    if "occurred_at" in record and not parse_iso8601(record["occurred_at"]):
        issues.append(ValidationIssue(location, "occurred_at must be ISO-8601"))
    for field in ("opportunity_ref", "evidence_locator", "actor", "notes"):
        if field in record and not is_nonempty_string(record[field]):
            issues.append(ValidationIssue(location, f"{field} must be a non-empty string"))

    origin = record.get("evidence_origin")
    if origin is not None and origin not in EVIDENCE_ORIGINS:
        issues.append(ValidationIssue(location, f"unknown evidence_origin '{origin}'"))
    if event_kind in EXTERNAL_PARTY_ONLY_EVENTS and origin != "external_party":
        issues.append(
            ValidationIssue(
                location,
                f"{event_kind} must originate from the external party",
            )
        )
    if event_kind in PAYMENT_EVENTS and origin not in {"payment_provider", "owner_attestation"}:
        issues.append(
            ValidationIssue(
                location,
                f"{event_kind} requires payment-provider evidence or owner attestation",
            )
        )
    return issues


TYPE_VALIDATORS = {
    "principle": validate_principle,
    "observation": validate_observation,
    "opportunity": validate_opportunity,
    "probe": validate_probe,
    "event": validate_event,
}


def validate_record(record: Any, location: str = "record") -> list[ValidationIssue]:
    issues = validate_common(record, location)
    if not isinstance(record, dict):
        return issues
    record_type = record.get("record_type")
    validator = TYPE_VALIDATORS.get(record_type)
    if validator is not None:
        issues.extend(validator(record, location))
    return issues


def load_workspace_records(
    workspace: Path,
) -> tuple[list[tuple[Path, dict[str, Any]]], list[ValidationIssue]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    issues: list[ValidationIssue] = []
    for record_type, directory_name in RECORD_DIRECTORIES.items():
        directory = workspace / directory_name
        if not directory.is_dir():
            issues.append(ValidationIssue(str(directory), "record directory is missing"))
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                value = read_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                issues.append(ValidationIssue(str(path), f"cannot read JSON: {exc}"))
                continue
            if not isinstance(value, dict):
                issues.append(ValidationIssue(str(path), "record must be a JSON object"))
                continue
            if value.get("record_type") != record_type:
                issues.append(
                    ValidationIssue(
                        str(path),
                        f"record_type must match directory type '{record_type}'",
                    )
                )
            records.append((path, value))
    return records, issues


def validate_workspace(
    workspace: Path,
) -> tuple[dict[str, dict[str, Any]], list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    manifest_path = workspace / "workspace.json"
    if not manifest_path.is_file():
        issues.append(ValidationIssue(str(manifest_path), "workspace manifest is missing"))
    else:
        try:
            manifest = read_json(manifest_path)
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(ValidationIssue(str(manifest_path), f"cannot read JSON: {exc}"))
        else:
            if not isinstance(manifest, dict) or manifest.get("workspace_version") != WORKSPACE_VERSION:
                issues.append(
                    ValidationIssue(
                        str(manifest_path),
                        f"workspace_version must be '{WORKSPACE_VERSION}'",
                    )
                )

    records, load_issues = load_workspace_records(workspace)
    issues.extend(load_issues)

    index: dict[str, dict[str, Any]] = {}
    locations: dict[str, str] = {}
    for path, record in records:
        location = str(path)
        issues.extend(validate_record(record, location))
        record_id = record.get("id")
        if not is_nonempty_string(record_id):
            continue
        if record_id in index:
            issues.append(
                ValidationIssue(
                    location,
                    f"duplicate id also used by {locations[record_id]}",
                )
            )
        else:
            index[record_id] = record
            locations[record_id] = location

    for path, record in records:
        location = str(path)
        record_type = record.get("record_type")
        if record_type == "opportunity":
            for ref in record.get("observation_refs", []):
                target = index.get(ref)
                if target is None or target.get("record_type") != "observation":
                    issues.append(ValidationIssue(location, f"unknown observation_ref '{ref}'"))
            for ref in record.get("principle_refs", []):
                target = index.get(ref)
                if target is None or target.get("record_type") != "principle":
                    issues.append(ValidationIssue(location, f"unknown principle_ref '{ref}'"))
        elif record_type == "probe":
            ref = record.get("opportunity_ref")
            target = index.get(ref)
            if target is None or target.get("record_type") != "opportunity":
                issues.append(ValidationIssue(location, f"unknown opportunity_ref '{ref}'"))
        elif record_type == "event":
            ref = record.get("opportunity_ref")
            target = index.get(ref)
            if target is None or target.get("record_type") != "opportunity":
                issues.append(ValidationIssue(location, f"unknown opportunity_ref '{ref}'"))

    return index, issues


def derive_opportunity_status(
    opportunity_id: str,
    index: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    market_stage = "hypothesis"
    fulfillment_stage = "not_started"
    event_kinds: list[str] = []
    issue_events: list[str] = []

    for record in index.values():
        if record.get("record_type") != "event" or record.get("opportunity_ref") != opportunity_id:
            continue
        event_kind = record["event_kind"]
        event_kinds.append(event_kind)
        if event_kind in POSITIVE_MARKET_EVENT_TO_STAGE:
            candidate = POSITIVE_MARKET_EVENT_TO_STAGE[event_kind]
            if MARKET_STAGES.index(candidate) > MARKET_STAGES.index(market_stage):
                market_stage = candidate
        if event_kind in FULFILLMENT_EVENT_TO_STAGE:
            candidate = FULFILLMENT_EVENT_TO_STAGE[event_kind]
            if FULFILLMENT_STAGES.index(candidate) > FULFILLMENT_STAGES.index(fulfillment_stage):
                fulfillment_stage = candidate
        if event_kind in ISSUE_EVENT_KINDS:
            issue_events.append(event_kind)

    return {
        "opportunity_id": opportunity_id,
        "market_stage": market_stage,
        "fulfillment_stage": fulfillment_stage,
        "event_kinds": sorted(event_kinds),
        "issue_events": sorted(issue_events),
    }


def init_workspace(workspace: Path) -> None:
    if workspace.exists() and any(workspace.iterdir()):
        raise ValueError(f"workspace is not empty: {workspace}")
    workspace.mkdir(parents=True, exist_ok=True)
    for directory_name in RECORD_DIRECTORIES.values():
        (workspace / directory_name).mkdir(exist_ok=True)
    (workspace / "harnesses").mkdir(exist_ok=True)
    atomic_write_json(
        workspace / "workspace.json",
        {
            "workspace_version": WORKSPACE_VERSION,
            "created_at": utc_now(),
            "goal": "发现真实价值缺口，提供有效解决方案，并以真实交易完成验证。",
            "external_actions_default": "not_authorized",
        },
    )


def add_record(workspace: Path, source_path: Path) -> Path:
    index, issues = validate_workspace(workspace)
    if issues:
        raise ValueError("workspace is invalid:\n" + "\n".join(issue.render() for issue in issues))
    try:
        record = read_json(source_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read record: {exc}") from exc

    record_issues = validate_record(record, str(source_path))
    if record_issues:
        raise ValueError("\n".join(issue.render() for issue in record_issues))

    record_id = record["id"]
    if record_id in index:
        raise ValueError(f"record id already exists: {record_id}")

    record_type = record["record_type"]
    destination = workspace / RECORD_DIRECTORIES[record_type] / f"{record_id}.json"
    atomic_write_json(destination, record)

    _, final_issues = validate_workspace(workspace)
    if final_issues:
        destination.unlink(missing_ok=True)
        raise ValueError("record would invalidate workspace:\n" + "\n".join(
            issue.render() for issue in final_issues
        ))
    return destination


def status_report(workspace: Path) -> list[dict[str, Any]]:
    index, issues = validate_workspace(workspace)
    if issues:
        raise ValueError("workspace is invalid:\n" + "\n".join(issue.render() for issue in issues))
    opportunities = sorted(
        record_id
        for record_id, record in index.items()
        if record.get("record_type") == "opportunity"
    )
    return [derive_opportunity_status(record_id, index) for record_id in opportunities]


def external_permission_for_probe(probe: dict[str, Any]) -> str:
    return {
        "draft_only": "not_authorized",
        "human_approval_each": "per_action_approval",
        "scoped_authorization": "scoped_authorization",
    }[probe["external_action_policy"]]


def make_harness(
    workspace: Path,
    opportunity_id: str,
    probe_id: str,
    mode: str,
) -> Path:
    index, issues = validate_workspace(workspace)
    if issues:
        raise ValueError("workspace is invalid:\n" + "\n".join(issue.render() for issue in issues))

    opportunity = index.get(opportunity_id)
    if opportunity is None or opportunity.get("record_type") != "opportunity":
        raise ValueError(f"unknown opportunity: {opportunity_id}")
    probe = index.get(probe_id)
    if probe is None or probe.get("record_type") != "probe":
        raise ValueError(f"unknown probe: {probe_id}")
    if probe["opportunity_ref"] != opportunity_id:
        raise ValueError("probe does not belong to the requested opportunity")
    if mode not in {"probe", "delivery"}:
        raise ValueError("mode must be 'probe' or 'delivery'")

    status = derive_opportunity_status(opportunity_id, index)
    if mode == "delivery" and MARKET_STAGES.index(status["market_stage"]) < MARKET_STAGES.index(
        "commitment"
    ):
        raise ValueError(
            "delivery harness is blocked until external evidence reaches commitment; "
            f"current market stage is {status['market_stage']}"
        )

    if mode == "probe":
        objective = probe["claim_tested"]
        outputs = [probe["artifact"], "evidence-ready Offer draft", "run log"]
        evaluation = {
            "success_event_kinds": probe["success_event_kinds"],
            "failure_or_stop_events": probe["failure_or_stop_events"],
            "claim_rule": "Only recorded external events can update market stage.",
        }
        stop_conditions = [
            probe["effort_boundary"],
            "Stop before any external action not allowed by the probe policy.",
            "Stop if the artifact would require invented facts about the target.",
        ]
    else:
        objective = (
            f"Deliver the agreed outcome for {opportunity['buyer']} in "
            f"{opportunity['situation']}: {opportunity['value_hypothesis']}"
        )
        outputs = ["agreed deliverable", "acceptance evidence", "delivery run log"]
        evaluation = {
            "required_delivery_events": ["delivery_sent", "delivery_accepted"],
            "market_status_at_generation": status["market_stage"],
            "claim_rule": "Delivery does not imply satisfaction or repeat demand.",
        }
        stop_conditions = [
            "Stop when requested work exceeds the recorded Offer or agreement.",
            "Stop before spending, signing, refunding, or changing payment accounts.",
            "Stop when acceptance criteria are missing or contradictory.",
        ]

    input_record_ids = sorted(
        set(
            [opportunity_id, probe_id]
            + opportunity["principle_refs"]
            + opportunity["observation_refs"]
        )
    )
    input_payload = [index[record_id] for record_id in input_record_ids]
    input_digest = hashlib.sha256(
        json.dumps(
            input_payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    manifest = {
        "harness_version": "0.1",
        "generated_at": utc_now(),
        "input_digest_sha256": input_digest,
        "input_record_ids": input_record_ids,
        "mode": mode,
        "opportunity_ref": opportunity_id,
        "probe_ref": probe_id,
        "objective": objective,
        "inputs": {
            "principle_refs": opportunity["principle_refs"],
            "observation_refs": opportunity["observation_refs"],
            "buyer": opportunity["buyer"],
            "situation": opportunity["situation"],
            "offer": probe["offer"],
            "target": probe["target"],
        },
        "permissions": {
            "read_public_information": True,
            "create_local_artifacts": True,
            "external_communication": external_permission_for_probe(probe),
            "financial_actions": "not_authorized",
            "contractual_commitments": "not_authorized",
        },
        "constraints": [
            "Preserve source wording and provenance.",
            "Label AI interpretation as hypothesis.",
            "Do not infer budget, authority, urgency, payment, or satisfaction without evidence.",
            "Record counterevidence and negative outcomes.",
            "Do not broaden the target or Offer without a new probe record.",
        ],
        "evaluation": evaluation,
        "stop_conditions": stop_conditions,
        "outputs": outputs,
    }

    destination_directory = workspace / "harnesses" / opportunity_id
    identity = input_digest[:12]
    destination = destination_directory / f"{mode}-{identity}-manifest.json"
    readme_path = destination_directory / f"{mode}-{identity}-TASK_CONTRACT.md"
    if destination.exists() and readme_path.exists():
        return destination
    if destination.exists() or readme_path.exists():
        raise ValueError("partial harness output exists; inspect it before continuing")

    atomic_write_json(destination, manifest)
    markdown = render_harness_markdown(manifest)
    atomic_write_text(readme_path, markdown)
    return destination


def render_harness_markdown(manifest: dict[str, Any]) -> str:
    permissions = manifest["permissions"]
    lines = [
        f"# {manifest['mode'].title()} Task Contract",
        "",
        f"- Opportunity: `{manifest['opportunity_ref']}`",
        f"- Probe: `{manifest['probe_ref']}`",
        f"- Generated: `{manifest['generated_at']}`",
        f"- Input digest: `{manifest['input_digest_sha256']}`",
        "",
        "## Objective",
        "",
        manifest["objective"],
        "",
        "## Permissions",
        "",
    ]
    for name, value in permissions.items():
        lines.append(f"- {name}: `{value}`")
    lines.extend(["", "## Constraints", ""])
    lines.extend(f"- {item}" for item in manifest["constraints"])
    lines.extend(["", "## Stop conditions", ""])
    lines.extend(f"- {item}" for item in manifest["stop_conditions"])
    lines.extend(["", "## Required outputs", ""])
    lines.extend(f"- {item}" for item in manifest["outputs"])
    lines.extend(
        [
            "",
            "## Completion rule",
            "",
            "Completion may be claimed only from the evaluation events in the manifest and their evidence locators.",
            "",
        ]
    )
    return "\n".join(lines)


def print_issues(issues: list[ValidationIssue]) -> None:
    for issue in issues:
        print(f"ERROR {issue.render()}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create an empty workspace")
    init_parser.add_argument("workspace", type=Path)

    validate_parser = subparsers.add_parser("validate", help="validate all records")
    validate_parser.add_argument("workspace", type=Path)

    add_parser = subparsers.add_parser("add", help="add one validated JSON record")
    add_parser.add_argument("workspace", type=Path)
    add_parser.add_argument("record", type=Path)

    status_parser = subparsers.add_parser("status", help="derive market and fulfillment status")
    status_parser.add_argument("workspace", type=Path)
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    harness_parser = subparsers.add_parser("make-harness", help="generate a probe or delivery harness")
    harness_parser.add_argument("workspace", type=Path)
    harness_parser.add_argument("--opportunity", required=True)
    harness_parser.add_argument("--probe", required=True)
    harness_parser.add_argument("--mode", choices=("probe", "delivery"), required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            init_workspace(args.workspace)
            print(args.workspace)
        elif args.command == "validate":
            _, issues = validate_workspace(args.workspace)
            if issues:
                print_issues(issues)
                return 1
            print("VALID")
        elif args.command == "add":
            print(add_record(args.workspace, args.record))
        elif args.command == "status":
            report = status_report(args.workspace)
            if args.as_json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            elif not report:
                print("No opportunities recorded.")
            else:
                for item in report:
                    print(
                        f"{item['opportunity_id']}: market={item['market_stage']} "
                        f"fulfillment={item['fulfillment_stage']} "
                        f"issues={','.join(item['issue_events']) or '-'}"
                    )
        elif args.command == "make-harness":
            print(
                make_harness(
                    args.workspace,
                    args.opportunity,
                    args.probe,
                    args.mode,
                )
            )
    except (OSError, ValueError, json.JSONDecodeError, shutil.Error) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
