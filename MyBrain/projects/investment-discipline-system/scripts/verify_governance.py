#!/usr/bin/env python3
"""Verify the frozen intent, acceptance contract, and traceability baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
GOVERNANCE = PROJECT_ROOT / "governance"
USER_INTENT = GOVERNANCE / "USER_INTENT_V1.json"
CONTRACT = GOVERNANCE / "ACCEPTANCE_CONTRACT_V1.json"
TRACEABILITY = GOVERNANCE / "TRACEABILITY_V1.json"
RESEARCH_REGISTER = GOVERNANCE / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
SOURCE_EXCERPTS = GOVERNANCE / "USER_SOURCE_EXCERPTS_V1.json"
VERIFICATION_SPECS = GOVERNANCE / "VERIFICATION_SPECS_V1.json"
ASSURANCE_SUBJECTS = GOVERNANCE / "ASSURANCE_SUBJECTS_V1.json"
BLUEPRINT = PROJECT_ROOT / "PRODUCT_ASSURANCE_BLUEPRINT_V2.md"
FROZEN_BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"


class DuplicateKeyError(ValueError):
    """Raised when JSON silently attempts to overwrite an earlier key."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate object key: {key}")
        value[key] = item
    return value


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except FileNotFoundError:
        errors.append(f"missing JSON: {path.relative_to(PROJECT_ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(
            f"invalid JSON {path.relative_to(PROJECT_ROOT)}:{exc.lineno}:{exc.colno}: {exc.msg}"
        )
        return {}
    except DuplicateKeyError as exc:
        errors.append(f"invalid JSON {path.relative_to(PROJECT_ROOT)}: {exc}")
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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run_git(args: list[str], errors: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        errors.append(
            f"git {' '.join(args)} failed ({result.returncode}): {result.stderr.strip()}"
        )
        return ""
    return result.stdout.strip()


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


def verify_source_excerpts(
    excerpts_doc: dict[str, Any], value_ids: set[str], errors: list[str]
) -> None:
    excerpts = excerpts_doc.get("excerpts")
    excerpt_ids = unique_ids(excerpts, "source excerpts", errors)
    del excerpt_ids
    covered_values: set[str] = set()
    if not isinstance(excerpts, list):
        return
    for index, excerpt in enumerate(excerpts):
        if not isinstance(excerpt, dict):
            continue
        excerpt_id = excerpt.get("id", f"source excerpts[{index}]")
        text = excerpt.get("excerpt")
        expected_hash = excerpt.get("excerpt_sha256")
        if not isinstance(text, str) or not text:
            errors.append(f"{excerpt_id} has no excerpt text")
            continue
        if expected_hash != sha256_text(text):
            errors.append(f"{excerpt_id} excerpt_sha256 mismatch")

        mapped_values = excerpt.get("value_ids", [])
        intent_targets = excerpt.get("intent_targets", [])
        if not isinstance(mapped_values, list) or not all(
            isinstance(item, str) for item in mapped_values
        ):
            errors.append(f"{excerpt_id} value_ids must be a string list")
            mapped_values = []
        unknown_values = set(mapped_values) - value_ids
        if unknown_values:
            errors.append(
                f"{excerpt_id} references unknown user values: {sorted(unknown_values)}"
            )
        covered_values.update(mapped_values)
        if not mapped_values and not intent_targets:
            errors.append(f"{excerpt_id} has no value_ids or intent_targets")

        source_type = excerpt.get("source_type")
        if source_type in {"tracked_project_charter", "tracked_decision_log"}:
            relative = excerpt.get("source_path")
            start = excerpt.get("line_start")
            end = excerpt.get("line_end")
            if (
                not isinstance(relative, str)
                or not isinstance(start, int)
                or not isinstance(end, int)
                or start < 1
                or end < start
            ):
                errors.append(f"{excerpt_id} has invalid tracked source locator")
                continue
            source_path = PROJECT_ROOT / relative
            if not source_path.is_file():
                errors.append(f"{excerpt_id} tracked source missing: {relative}")
                continue
            lines = source_path.read_text(encoding="utf-8").splitlines()
            if end > len(lines):
                errors.append(f"{excerpt_id} tracked source line range is out of bounds")
                continue
            actual = "\n".join(lines[start - 1 : end])
            if actual != text:
                errors.append(
                    f"{excerpt_id} tracked excerpt differs from {relative}:{start}-{end}"
                )
        elif source_type == "codex_user_message_excerpt":
            if not isinstance(excerpt.get("source_locator"), str):
                errors.append(f"{excerpt_id} lacks a Codex source_locator")
        else:
            errors.append(f"{excerpt_id} has unsupported source_type: {source_type!r}")

    if covered_values != value_ids:
        errors.append(
            "user source excerpt coverage differs: "
            f"missing={sorted(value_ids - covered_values)}, "
            f"extra={sorted(covered_values - value_ids)}"
        )


def verify_verification_specs(
    specs_doc: dict[str, Any],
    verification_ids: set[str],
    requirements: Any,
    errors: list[str],
) -> None:
    executor_ids = unique_ids(specs_doc.get("executors"), "verification executors", errors)
    input_ids = unique_ids(specs_doc.get("input_profiles"), "input profiles", errors)
    oracle_ids = unique_ids(specs_doc.get("oracles"), "oracles", errors)
    fixture_ids = unique_ids(
        specs_doc.get("negative_fixture_sets"), "negative fixture sets", errors
    )
    specs = specs_doc.get("specs")
    spec_ids = unique_ids(specs, "verification specs", errors)
    if spec_ids != verification_ids:
        errors.append(
            "verification spec coverage differs: "
            f"missing={sorted(verification_ids - spec_ids)}, "
            f"extra={sorted(spec_ids - verification_ids)}"
        )

    expected_requirements: dict[str, set[str]] = {
        verification_id: set() for verification_id in verification_ids
    }
    if isinstance(requirements, list):
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            req_id = requirement.get("id")
            for verification_id in requirement.get("verification", []):
                if verification_id in expected_requirements and isinstance(req_id, str):
                    expected_requirements[verification_id].add(req_id)

    evidence_paths: set[str] = set()
    selectors: set[str] = set()
    if isinstance(specs, list):
        for spec in specs:
            if not isinstance(spec, dict):
                continue
            spec_id = spec.get("id", "<unknown>")
            if spec.get("executor_id") not in executor_ids:
                errors.append(f"{spec_id} references unknown executor")
            if spec.get("input_profile_id") not in input_ids:
                errors.append(f"{spec_id} references unknown input profile")
            if spec.get("oracle_id") not in oracle_ids:
                errors.append(f"{spec_id} references unknown oracle")
            negative_sets = spec.get("negative_fixture_set_ids")
            if not isinstance(negative_sets, list) or not negative_sets:
                errors.append(f"{spec_id} has no negative fixture set")
            else:
                unknown = set(negative_sets) - fixture_ids
                if unknown:
                    errors.append(
                        f"{spec_id} references unknown negative fixtures: {sorted(unknown)}"
                    )
            path = spec.get("evidence_path")
            if not isinstance(path, str) or not path.startswith("evidence/verification/"):
                errors.append(f"{spec_id} has invalid evidence_path")
            elif path in evidence_paths:
                errors.append(f"duplicate verification evidence path: {path}")
            else:
                evidence_paths.add(path)
            selector = spec.get("test_selector")
            if not isinstance(selector, str) or not selector:
                errors.append(f"{spec_id} has no test_selector")
            elif selector in selectors:
                errors.append(f"duplicate verification test_selector: {selector}")
            else:
                selectors.add(selector)
            required_for = spec.get("required_for")
            if not isinstance(required_for, list) or "product_release" not in required_for:
                errors.append(f"{spec_id} is not required for product_release")
            actual_requirements = spec.get("requirement_ids")
            if not isinstance(actual_requirements, list):
                errors.append(f"{spec_id} has no requirement_ids")
            elif set(actual_requirements) != expected_requirements.get(spec_id, set()):
                errors.append(
                    f"{spec_id} reverse requirement binding differs: "
                    f"expected={sorted(expected_requirements.get(spec_id, set()))}, "
                    f"actual={sorted(set(actual_requirements))}"
                )

    result_schema = specs_doc.get("result_schema")
    required_result_fields = {
        "verification_id",
        "candidate_commit",
        "candidate_tree",
        "frozen_bundle_sha256",
        "run_id",
        "executor_id",
        "subject_id",
        "status",
        "input_hashes",
        "raw_result_hashes",
        "oracle_id",
        "oracle_observations",
        "negative_cases",
        "finding_ids",
    }
    if not isinstance(result_schema, dict):
        errors.append("verification result_schema must be an object")
    else:
        actual_fields = result_schema.get("required")
        if not isinstance(actual_fields, list) or not required_result_fields.issubset(
            set(actual_fields)
        ):
            errors.append("verification result_schema is missing release-binding fields")


def verify_assurance_subjects(
    subjects_doc: dict[str, Any], research: dict[str, Any], errors: list[str]
) -> None:
    subjects = subjects_doc.get("subjects")
    subject_ids = unique_ids(subjects, "assurance subjects", errors)
    builders: set[str] = set()
    human_owners: set[str] = set()
    if isinstance(subjects, list):
        for subject in subjects:
            if not isinstance(subject, dict):
                continue
            subject_id = subject.get("id")
            role = subject.get("role")
            if role == "builder":
                builders.add(subject_id)
                if subject.get("can_approve_release") is not False:
                    errors.append(f"{subject_id} builder may approve release")
            if role == "human_owner":
                human_owners.add(subject_id)
            if role == "design_reviewer":
                if subject.get("participated_in_candidate_construction") is not False:
                    errors.append(f"{subject_id} design reviewer is not independent")
                if subject.get("write_access_used") is not False:
                    errors.append(f"{subject_id} design reviewer used write access")
    if not builders:
        errors.append("assurance subjects has no builder")
    if not human_owners:
        errors.append("assurance subjects has no human owner")

    challenge = research.get("challenge")
    if isinstance(challenge, dict):
        for challenge_round in challenge.get("rounds", []):
            if not isinstance(challenge_round, dict):
                continue
            unknown = set(challenge_round.get("reviewer_subjects", [])) - subject_ids
            if unknown:
                errors.append(
                    "research challenge references unknown reviewer subjects: "
                    f"{sorted(unknown)}"
                )

    constraints = subjects_doc.get("future_role_constraints")
    if not isinstance(constraints, dict):
        errors.append("assurance future_role_constraints must be an object")
    else:
        for role in ("acceptance_reviewer", "user_proxy", "independence_probe"):
            if role not in constraints:
                errors.append(f"assurance role constraint missing: {role}")


def verify_conditionals(
    conditional_gates: Any, requirement_ids: set[str], errors: list[str]
) -> None:
    if not isinstance(conditional_gates, list):
        return
    required_fields = {
        "applies_to_requirements",
        "severity",
        "prerequisite_probe",
        "allowed_states",
        "when_prerequisite_absent",
        "when_prerequisite_present",
        "mandatory_gate_when_ready",
        "evidence_path",
        "release_mapping",
        "must_not_be_claimed",
    }
    for gate in conditional_gates:
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("id", "<unknown>")
        missing = required_fields - set(gate)
        if missing:
            errors.append(f"{gate_id} missing conditional fields: {sorted(missing)}")
        applies = gate.get("applies_to_requirements")
        if not isinstance(applies, list) or not applies:
            errors.append(f"{gate_id} has no applies_to_requirements")
        else:
            unknown = set(applies) - requirement_ids
            if unknown:
                errors.append(
                    f"{gate_id} references unknown requirements: {sorted(unknown)}"
                )
        states = gate.get("allowed_states")
        if not isinstance(states, list) or not states:
            errors.append(f"{gate_id} has no allowed_states")
        else:
            for transition_field in (
                "when_prerequisite_absent",
                "when_prerequisite_present",
            ):
                transition = gate.get(transition_field)
                if (
                    isinstance(transition, str)
                    and "_then_" not in transition
                    and transition not in states
                ):
                    errors.append(
                        f"{gate_id} {transition_field} is outside allowed_states"
                    )
        evidence_path = gate.get("evidence_path")
        if not isinstance(evidence_path, str) or not evidence_path.startswith(
            "evidence/conditional/"
        ):
            errors.append(f"{gate_id} has invalid conditional evidence_path")


def verify_bundle(
    bundle: dict[str, Any], contract: dict[str, Any], errors: list[str]
) -> None:
    baseline_commit = bundle.get("baseline_commit")
    baseline_tree = bundle.get("baseline_tree")
    if not isinstance(baseline_commit, str) or not re.fullmatch(
        r"[0-9a-f]{40}", baseline_commit
    ):
        errors.append("frozen bundle baseline_commit must be a full SHA-1")
        baseline_commit = ""
    if not isinstance(baseline_tree, str) or not re.fullmatch(
        r"[0-9a-f]{40}", baseline_tree
    ):
        errors.append("frozen bundle baseline_tree must be a full SHA-1")
        baseline_tree = ""
    if baseline_commit and baseline_tree:
        actual_tree = run_git(["rev-parse", f"{baseline_commit}^{{tree}}"], errors)
        if actual_tree and actual_tree != baseline_tree:
            errors.append(
                f"frozen baseline tree mismatch: expected {baseline_tree}, got {actual_tree}"
            )

    entries = bundle.get("files")
    if not isinstance(entries, list):
        errors.append("frozen bundle files must be a list")
        return
    change_control = contract.get("change_control")
    frozen_files = (
        change_control.get("frozen_files") if isinstance(change_control, dict) else None
    )
    if not isinstance(frozen_files, list) or not all(
        isinstance(item, str) for item in frozen_files
    ):
        errors.append("contract change_control.frozen_files must be a string list")
        expected_paths: set[str] = set()
    else:
        expected_paths = set(frozen_files)
    repo_prefix = run_git(["rev-parse", "--show-prefix"], errors)
    actual_paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"frozen bundle files[{index}] must be object")
            continue
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        expected_blob = entry.get("git_blob")
        if (
            not isinstance(relative, str)
            or not isinstance(expected_hash, str)
            or not isinstance(expected_blob, str)
        ):
            errors.append(
                f"frozen bundle files[{index}] needs path, sha256 and git_blob"
            )
            continue
        if relative in actual_paths:
            errors.append(f"duplicate frozen bundle path: {relative}")
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
        if baseline_commit:
            repo_relative = f"{repo_prefix}{relative}"
            baseline_bytes = subprocess.run(
                ["git", "show", f"{baseline_commit}:{repo_relative}"],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if baseline_bytes.returncode != 0:
                errors.append(f"frozen file is absent from baseline commit: {relative}")
            else:
                baseline_hash = hashlib.sha256(baseline_bytes.stdout).hexdigest()
                if baseline_hash != expected_hash:
                    errors.append(
                        f"baseline content hash mismatch for {relative}: "
                        f"expected {expected_hash}, got {baseline_hash}"
                    )
            tree_line = run_git(
                ["ls-tree", baseline_commit, "--", repo_relative], errors
            )
            fields = tree_line.split()
            actual_blob = fields[2] if len(fields) >= 3 else ""
            if actual_blob != expected_blob:
                errors.append(
                    f"baseline git blob mismatch for {relative}: "
                    f"expected {expected_blob}, got {actual_blob or '<missing>'}"
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
    source_excerpts = load_json(SOURCE_EXCERPTS, errors)
    verification_specs = load_json(VERIFICATION_SPECS, errors)
    assurance_subjects = load_json(ASSURANCE_SUBJECTS, errors)

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
    for label, document in (
        ("user intent", intent),
        ("source excerpts", source_excerpts),
        ("verification specs", verification_specs),
        ("traceability", trace),
        ("assurance subjects", assurance_subjects),
    ):
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
    verify_source_excerpts(source_excerpts, value_ids, errors)
    source_evidence = intent.get("source_evidence")
    if (
        not isinstance(source_evidence, dict)
        or source_evidence.get("path")
        != "governance/USER_SOURCE_EXCERPTS_V1.json"
    ):
        errors.append("user intent does not bind USER_SOURCE_EXCERPTS_V1.json")
    requirements = contract.get("requirements")
    requirement_ids = unique_ids(requirements, "requirements", errors)
    verification_ids = unique_ids(
        contract.get("verification_catalog"), "verification_catalog", errors
    )
    unique_ids(contract.get("gates"), "gates", errors)
    unique_ids(contract.get("conditional_gates"), "conditional_gates", errors)
    verify_verification_specs(
        verification_specs, verification_ids, requirements, errors
    )
    verify_assurance_subjects(assurance_subjects, research, errors)
    verify_conditionals(contract.get("conditional_gates"), requirement_ids, errors)
    expected_frozen_files = {
        "governance/USER_SOURCE_EXCERPTS_V1.json",
        "governance/USER_INTENT_V1.json",
        "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json",
        "governance/ACCEPTANCE_CONTRACT_V1.json",
        "governance/VERIFICATION_SPECS_V1.json",
        "governance/TRACEABILITY_V1.json",
        "governance/ASSURANCE_SUBJECTS_V1.json",
        "PRODUCT_ASSURANCE_BLUEPRINT_V2.md",
    }
    change_control = contract.get("change_control")
    frozen_files = (
        change_control.get("frozen_files") if isinstance(change_control, dict) else None
    )
    if not isinstance(frozen_files, list) or set(frozen_files) != expected_frozen_files:
        errors.append(
            "normative frozen file boundary differs: "
            f"expected={sorted(expected_frozen_files)}, "
            f"actual={sorted(frozen_files) if isinstance(frozen_files, list) else frozen_files}"
        )
    if not BLUEPRINT.is_file():
        errors.append("normative PRODUCT_ASSURANCE_BLUEPRINT_V2.md is missing")

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
            verify_bundle(bundle, contract, errors)

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
