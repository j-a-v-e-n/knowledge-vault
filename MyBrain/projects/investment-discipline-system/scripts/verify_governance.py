#!/usr/bin/env python3
"""Verify the frozen intent, acceptance contract, and traceability baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = PROJECT_ROOT / "governance"
USER_INTENT = GOVERNANCE / "USER_INTENT_V1.json"
CONTRACT = GOVERNANCE / "ACCEPTANCE_CONTRACT_V1.json"
TRACEABILITY = GOVERNANCE / "TRACEABILITY_V1.json"
RESEARCH_REGISTER = GOVERNANCE / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
FROZEN_BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON: {path.relative_to(PROJECT_ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(
            f"invalid JSON {path.relative_to(PROJECT_ROOT)}:{exc.lineno}:{exc.colno}: {exc.msg}"
        )
        return {}
    if not isinstance(value, dict):
        errors.append(f"top-level JSON must be object: {path.relative_to(PROJECT_ROOT)}")
        return {}
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def unique_ids(
    items: Any, label: str, errors: list[str], *, key: str = "id"
) -> set[str]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return set()
    seen: set[str] = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get(key), str):
            errors.append(f"{label}[{index}] missing string {key}")
            continue
        item_id = item[key]
        if item_id in seen:
            errors.append(f"duplicate {label} id: {item_id}")
        seen.add(item_id)
    return seen


def collect_design_ids() -> set[str]:
    paths = [
        PROJECT_ROOT / "research" / "AI_PROJECT_FAILURE_TAXONOMY_2026-07-25.md",
        PROJECT_ROOT / "PRODUCT_ASSURANCE_BLUEPRINT_V2.md",
    ]
    result: set[str] = set()
    pattern = re.compile(r"\b(?:GOV|RES|CTX|ORG|IMP|VER|SEC|OPS|HUM|ECO|H)-\d{2}\b")
    for path in paths:
        if path.exists():
            result.update(pattern.findall(path.read_text(encoding="utf-8")))
    return result


def verify_bundle(bundle: dict[str, Any], errors: list[str]) -> None:
    entries = bundle.get("files")
    if not isinstance(entries, list):
        errors.append("frozen bundle files must be a list")
        return
    expected_paths = {
        "governance/USER_INTENT_V1.json",
        "governance/ACCEPTANCE_CONTRACT_V1.json",
        "governance/TRACEABILITY_V1.json",
    }
    actual_paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"frozen bundle files[{index}] must be object")
            continue
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected_hash, str):
            errors.append(f"frozen bundle files[{index}] needs path and sha256")
            continue
        actual_paths.add(relative)
        path = PROJECT_ROOT / relative
        if not path.is_file():
            errors.append(f"frozen file missing: {relative}")
            continue
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            errors.append(
                f"frozen hash mismatch: {relative}: expected {expected_hash}, got {actual_hash}"
            )
    if actual_paths != expected_paths:
        errors.append(
            "frozen bundle paths differ: "
            f"missing={sorted(expected_paths - actual_paths)}, "
            f"extra={sorted(actual_paths - expected_paths)}"
        )


def verify(allow_candidate: bool) -> list[str]:
    errors: list[str] = []
    intent = load_json(USER_INTENT, errors)
    contract = load_json(CONTRACT, errors)
    trace = load_json(TRACEABILITY, errors)
    research = load_json(RESEARCH_REGISTER, errors)

    if errors:
        return errors

    expected_status = "candidate_under_challenge" if allow_candidate else "frozen"
    allowed_contract_statuses = {expected_status}
    if allow_candidate:
        allowed_contract_statuses.add("frozen")
    if contract.get("status") not in allowed_contract_statuses:
        errors.append(
            f"contract status must be one of {sorted(allowed_contract_statuses)}, "
            f"got {contract.get('status')!r}"
        )

    expected_baseline_status = "candidate_for_freeze" if allow_candidate else "frozen"
    allowed_baseline_statuses = {expected_baseline_status}
    if allow_candidate:
        allowed_baseline_statuses.add("frozen")
    for label, document in (("user intent", intent), ("traceability", trace)):
        if document.get("status") not in allowed_baseline_statuses:
            errors.append(
                f"{label} status must be one of {sorted(allowed_baseline_statuses)}, "
                f"got {document.get('status')!r}"
            )

    if not allow_candidate:
        if research.get("status") != "adopted_with_explicit_limits":
            errors.append("research register is not adopted_with_explicit_limits")
        challenge = research.get("challenge")
        if not isinstance(challenge, dict) or challenge.get("status") != "completed":
            errors.append("research independent challenge is not completed")
        stop_rule = research.get("stop_rule")
        if not isinstance(stop_rule, dict) or stop_rule.get("met") is not True:
            errors.append("research stop rule is not met")

    value_ids = unique_ids(intent.get("core_values"), "core_values", errors)
    requirements = contract.get("requirements")
    requirement_ids = unique_ids(requirements, "requirements", errors)
    verification_ids = unique_ids(
        contract.get("verification_catalog"), "verification_catalog", errors
    )
    unique_ids(contract.get("gates"), "gates", errors)
    unique_ids(contract.get("conditional_gates"), "conditional_gates", errors)

    design_ids = collect_design_ids()
    if isinstance(requirements, list):
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            req_id = requirement.get("id", "<unknown>")
            source_values = requirement.get("source_values")
            if not isinstance(source_values, list) or not source_values:
                errors.append(f"{req_id} has no source_values")
            else:
                unknown_values = {
                    value for value in source_values if value not in value_ids
                }
                if unknown_values:
                    errors.append(
                        f"{req_id} references unknown user values: {sorted(unknown_values)}"
                    )
            hazards = requirement.get("hazards")
            if not isinstance(hazards, list) or not hazards:
                errors.append(f"{req_id} has no hazards")
            else:
                unknown_hazards = {
                    hazard for hazard in hazards if hazard not in design_ids
                }
                if unknown_hazards:
                    errors.append(
                        f"{req_id} references unknown hazards: {sorted(unknown_hazards)}"
                    )
            verification = requirement.get("verification")
            if not isinstance(verification, list) or not verification:
                errors.append(f"{req_id} has no verification")
            else:
                unknown_verification = {
                    item for item in verification if item not in verification_ids
                }
                if unknown_verification:
                    errors.append(
                        f"{req_id} references unknown verification: "
                        f"{sorted(unknown_verification)}"
                    )
            if requirement.get("severity") not in {"critical", "major", "minor"}:
                errors.append(f"{req_id} has invalid severity")

    controls = trace.get("controls")
    control_ids = unique_ids(controls, "controls", errors)
    links = trace.get("links")
    linked_requirements: set[str] = set()
    linked_controls: set[str] = set()
    if not isinstance(links, list):
        errors.append("traceability links must be a list")
    else:
        for index, link in enumerate(links):
            if not isinstance(link, dict):
                errors.append(f"links[{index}] must be object")
                continue
            req_id = link.get("requirement_id")
            control_list = link.get("control_ids")
            if not isinstance(req_id, str):
                errors.append(f"links[{index}] missing requirement_id")
                continue
            if req_id in linked_requirements:
                errors.append(f"duplicate trace link for requirement: {req_id}")
            linked_requirements.add(req_id)
            if not isinstance(control_list, list) or not control_list:
                errors.append(f"{req_id} has no linked controls")
                continue
            linked_controls.update(control_list)

    if linked_requirements != requirement_ids:
        errors.append(
            "traceability requirement coverage differs: "
            f"missing={sorted(requirement_ids - linked_requirements)}, "
            f"extra={sorted(linked_requirements - requirement_ids)}"
        )
    unknown_controls = linked_controls - control_ids
    if unknown_controls:
        errors.append(f"traceability references unknown controls: {sorted(unknown_controls)}")
    unused_controls = control_ids - linked_controls
    if unused_controls:
        errors.append(f"traceability has unused controls: {sorted(unused_controls)}")

    if isinstance(controls, list):
        for control in controls:
            if not isinstance(control, dict):
                continue
            control_id = control.get("id", "<unknown>")
            targets = control.get("implementation_targets")
            if not isinstance(targets, list) or not targets:
                errors.append(f"{control_id} has no implementation targets")
            design_ref = control.get("design_ref")
            if not isinstance(design_ref, str) or "#" not in design_ref:
                errors.append(f"{control_id} has invalid design_ref")

    if not allow_candidate:
        bundle = load_json(FROZEN_BUNDLE, errors)
        if bundle:
            verify_bundle(bundle, errors)
        for relative in contract.get("required_artifacts", []):
            if not isinstance(relative, str):
                errors.append("required_artifacts entries must be strings")
                continue
            if not (PROJECT_ROOT / relative).exists():
                errors.append(f"required artifact missing: {relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-candidate",
        action="store_true",
        help="Validate the pre-freeze candidate without requiring a frozen bundle.",
    )
    args = parser.parse_args()
    errors = verify(args.allow_candidate)
    if errors:
        print("governance verification: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "governance verification: PASS "
        f"({'candidate' if args.allow_candidate else 'frozen'})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
