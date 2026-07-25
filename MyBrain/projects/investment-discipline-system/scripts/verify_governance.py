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
ACCEPTANCE_CASES = GOVERNANCE / "ACCEPTANCE_CASES_V1.json"
MONEY_SPEC = GOVERNANCE / "MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
MARKET_POLICY = GOVERNANCE / "MARKET_SIMULATION_POLICY_V1.json"
FIELD_PROTOCOL = GOVERNANCE / "FIELD_USE_PROTOCOL_V1.json"
PRIVATE_DATA_POLICY = GOVERNANCE / "PRIVATE_DATA_POLICY_V1.json"
IMPLEMENTATION_TARGETS = GOVERNANCE / "IMPLEMENTATION_TARGETS_V1.json"
BLUEPRINT = PROJECT_ROOT / "PRODUCT_ASSURANCE_BLUEPRINT_V2.md"
FROZEN_BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"

PHASES = {"design_freeze", "product_release", "human_onboarding", "longitudinal"}
NORMATIVE_JSON_PATHS = (
    "governance/USER_SOURCE_EXCERPTS_V1.json",
    "governance/USER_INTENT_V1.json",
    "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json",
    "governance/ACCEPTANCE_CONTRACT_V1.json",
    "governance/ACCEPTANCE_CASES_V1.json",
    "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json",
    "governance/MARKET_SIMULATION_POLICY_V1.json",
    "governance/FIELD_USE_PROTOCOL_V1.json",
    "governance/PRIVATE_DATA_POLICY_V1.json",
    "governance/IMPLEMENTATION_TARGETS_V1.json",
    "governance/VERIFICATION_SPECS_V1.json",
    "governance/TRACEABILITY_V1.json",
    "governance/ASSURANCE_SUBJECTS_V1.json",
)


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


def verify_acceptance_cases(
    cases_doc: dict[str, Any],
    requirement_ids: set[str],
    verification_ids: set[str],
    errors: list[str],
) -> set[str]:
    schema = cases_doc.get("case_schema")
    required_fields = {
        "id",
        "operation_id",
        "phase",
        "requirement_ids",
        "verification_ids",
        "preconditions",
        "operation",
        "expected",
    }
    if not isinstance(schema, dict):
        errors.append("acceptance case_schema must be an object")
    else:
        declared = schema.get("required")
        if not isinstance(declared, list) or set(declared) != required_fields:
            errors.append("acceptance case_schema required fields differ")
        if set(schema.get("phase_enum", [])) != PHASES:
            errors.append("acceptance case_schema phases differ")

    cases = cases_doc.get("cases")
    case_ids = unique_ids(cases, "acceptance cases", errors)
    operations = cases_doc.get("operation_catalog")
    operation_ids = unique_ids(operations, "acceptance operation catalog", errors)
    operation_by_id: dict[str, dict[str, Any]] = {}
    operation_case_ids: set[str] = set()
    if isinstance(operations, list):
        for operation in operations:
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("id", "<unknown>")
            operation_by_id[operation_id] = operation
            case_id = operation.get("case_id")
            if not isinstance(case_id, str):
                errors.append(f"{operation_id} has no case_id")
            elif case_id in operation_case_ids:
                errors.append(f"duplicate operation case binding: {case_id}")
            else:
                operation_case_ids.add(case_id)
            if operation.get("kind") not in {"command", "domain_action"}:
                errors.append(f"{operation_id} has invalid operation kind")
            selector = operation.get("selector")
            if (
                not isinstance(selector, str)
                or not re.fullmatch(
                    r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", selector
                )
            ):
                errors.append(f"{operation_id} has no parseable selector")
            target = operation.get("implementation_target")
            if (
                not isinstance(target, str)
                or Path(target).is_absolute()
                or ".." in Path(target).parts
            ):
                errors.append(f"{operation_id} has invalid implementation target")
            if operation.get("required_by") not in PHASES:
                errors.append(f"{operation_id} has invalid required_by phase")
            expected_target = {
                "design_freeze": "governance_tests/",
                "product_release": "acceptance/",
                "human_onboarding": "src/investment_discipline/conditionals.py",
                "longitudinal": "src/investment_discipline/conditionals.py",
            }.get(operation.get("required_by"))
            if expected_target is not None and target != expected_target:
                errors.append(f"{operation_id} implementation stage target differs")
    if operation_case_ids != case_ids:
        errors.append(
            "acceptance operation case coverage differs: "
            f"missing={sorted(case_ids - operation_case_ids)}, "
            f"extra={sorted(operation_case_ids - case_ids)}"
        )
    covered_requirements: set[str] = set()
    if not isinstance(cases, list):
        return case_ids
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            continue
        case_id = case.get("id", f"acceptance cases[{index}]")
        missing = required_fields - set(case)
        if missing:
            errors.append(f"{case_id} missing acceptance fields: {sorted(missing)}")
        if case.get("phase") not in PHASES:
            errors.append(f"{case_id} has invalid phase")
        operation_id = case.get("operation_id")
        operation = operation_by_id.get(operation_id)
        if operation_id not in operation_ids or operation is None:
            errors.append(f"{case_id} references unknown operation_id")
        elif (
            operation.get("case_id") != case_id
            or operation.get("required_by") != case.get("phase")
        ):
            errors.append(f"{case_id} operation binding differs")
        for field, known_ids in (
            ("requirement_ids", requirement_ids),
            ("verification_ids", verification_ids),
        ):
            values = case.get(field)
            if (
                not isinstance(values, list)
                or not values
                or not all(isinstance(value, str) for value in values)
                or len(values) != len(set(values))
            ):
                errors.append(f"{case_id} {field} must be a nonempty unique string list")
                continue
            unknown = set(values) - known_ids
            if unknown:
                errors.append(f"{case_id} references unknown {field}: {sorted(unknown)}")
            if field == "requirement_ids":
                covered_requirements.update(value for value in values if value in known_ids)
        for field in ("preconditions", "operation", "expected"):
            value = case.get(field)
            if not isinstance(value, dict) or not value:
                errors.append(f"{case_id} {field} must be a nonempty object")
        expected = case.get("expected")
        if isinstance(expected, dict):
            serialized = json.dumps(expected, ensure_ascii=False).strip().lower()
            if expected in ({"status": "pass"}, {"result": "pass"}) or serialized in {
                '"pass"',
                '{"pass": true}',
            }:
                errors.append(f"{case_id} has a bare pass oracle")
            if any(term in serialized for term in ("does not crash", "looks correct")):
                errors.append(f"{case_id} has a non-observable oracle")
    if covered_requirements != requirement_ids:
        errors.append(
            "acceptance case requirement coverage differs: "
            f"missing={sorted(requirement_ids - covered_requirements)}, "
            f"extra={sorted(covered_requirements - requirement_ids)}"
        )
    return case_ids


def verify_verification_specs(
    specs_doc: dict[str, Any],
    verification_ids: set[str],
    requirements: Any,
    cases_doc: dict[str, Any],
    case_ids: set[str],
    errors: list[str],
) -> set[str]:
    executor_ids = unique_ids(specs_doc.get("executors"), "verification executors", errors)
    input_ids = unique_ids(specs_doc.get("input_profiles"), "input profiles", errors)
    assertion_evaluators = specs_doc.get("assertion_evaluators")
    assertion_evaluator_ids = unique_ids(
        assertion_evaluators, "assertion evaluators", errors
    )
    assertion_catalog = specs_doc.get("assertion_catalog")
    assertion_ids = unique_ids(assertion_catalog, "assertion catalog", errors)
    oracles = specs_doc.get("oracles")
    oracle_ids = unique_ids(oracles, "oracles", errors)
    fixture_sets = specs_doc.get("negative_fixture_sets")
    fixture_ids = unique_ids(fixture_sets, "negative fixture sets", errors)
    specs = specs_doc.get("specs")
    spec_ids = unique_ids(specs, "verification specs", errors)
    if set(specs_doc.get("phase_rules", {})) != PHASES:
        errors.append("verification phase rules differ")
    if spec_ids != verification_ids:
        errors.append(
            "verification spec coverage differs: "
            f"missing={sorted(verification_ids - spec_ids)}, "
            f"extra={sorted(spec_ids - verification_ids)}"
        )

    oracle_assertions: set[str] = set()
    if isinstance(oracles, list):
        for oracle in oracles:
            if not isinstance(oracle, dict):
                continue
            oracle_id = oracle.get("id", "<unknown>")
            assertions = oracle.get("assertions")
            if (
                not isinstance(assertions, list)
                or len(assertions) < 2
                or not all(isinstance(item, str) and item for item in assertions)
                or oracle.get("failure_is_nonzero") is not True
                or oracle.get("bare_pass_forbidden") is not True
                or "rule" in oracle
                or any("always pass" in item.lower() for item in assertions if isinstance(item, str))
            ):
                errors.append(
                    f"{oracle_id} oracle definition is not structurally enforceable"
                )
            else:
                oracle_assertions.update(assertions)
                unknown_assertions = set(assertions) - assertion_ids
                if unknown_assertions:
                    errors.append(
                        f"{oracle_id} references undefined assertions: "
                        f"{sorted(unknown_assertions)}"
                    )
    if oracle_assertions != assertion_ids:
        errors.append(
            "assertion catalog coverage differs: "
            f"unused={sorted(assertion_ids - oracle_assertions)}, "
            f"missing={sorted(oracle_assertions - assertion_ids)}"
        )
    if isinstance(assertion_evaluators, list):
        for evaluator in assertion_evaluators:
            if not isinstance(evaluator, dict):
                continue
            evaluator_id = evaluator.get("id", "<unknown>")
            if not isinstance(evaluator.get("kind"), str):
                errors.append(f"{evaluator_id} evaluator kind is missing")
            if (
                not isinstance(evaluator.get("selector"), str)
                or not re.fullmatch(
                    r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+",
                    evaluator.get("selector", ""),
                )
            ):
                errors.append(f"{evaluator_id} evaluator selector is not parseable")
            if evaluator.get("implementation_target") != "scripts/verify_release.py":
                errors.append(f"{evaluator_id} evaluator implementation target differs")
    if isinstance(assertion_catalog, list):
        for assertion in assertion_catalog:
            if not isinstance(assertion, dict):
                continue
            assertion_id = assertion.get("id", "<unknown>")
            if assertion.get("evaluator_id") not in assertion_evaluator_ids:
                errors.append(f"{assertion_id} references unknown assertion evaluator")
            observation_schema = assertion.get("observation_schema")
            if (
                not isinstance(observation_schema, dict)
                or set(observation_schema.get("required", []))
                != {
                    "assertion_id",
                    "observed",
                    "expected",
                    "raw_evidence_hash",
                }
                or observation_schema.get("bare_boolean_without_raw_evidence_allowed")
                is not False
            ):
                errors.append(f"{assertion_id} observation schema differs")
            if assertion.get("failure_outcome") != "verification_fail":
                errors.append(f"{assertion_id} failure outcome differs")

    referenced_cases: set[str] = set()
    fixture_cases_by_id: dict[str, set[str]] = {}
    if isinstance(fixture_sets, list):
        for fixture_set in fixture_sets:
            if not isinstance(fixture_set, dict):
                continue
            fixture_id = fixture_set.get("id", "<unknown>")
            cases = fixture_set.get("case_ids")
            if (
                not isinstance(cases, list)
                or not cases
                or not all(isinstance(item, str) for item in cases)
                or len(cases) != len(set(cases))
            ):
                errors.append(f"{fixture_id} has no acceptance cases")
                continue
            if "cases" in fixture_set:
                errors.append(f"{fixture_id} uses unbound free-text cases")
            unknown = set(cases) - case_ids
            if unknown:
                errors.append(
                    f"{fixture_id} references unknown acceptance cases: {sorted(unknown)}"
                )
            referenced_cases.update(item for item in cases if item in case_ids)
            fixture_cases_by_id[fixture_id] = {
                item for item in cases if item in case_ids
            }
    if referenced_cases != case_ids:
        errors.append(
            "negative fixture case coverage differs: "
            f"missing={sorted(case_ids - referenced_cases)}, "
            f"extra={sorted(referenced_cases - case_ids)}"
        )

    expected_requirements: dict[str, set[str]] = {
        verification_id: set() for verification_id in verification_ids
    }
    expected_cases: dict[str, set[str]] = {
        verification_id: set() for verification_id in verification_ids
    }
    for case in cases_doc.get("cases", []):
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            continue
        for verification_id in case.get("verification_ids", []):
            if verification_id in expected_cases:
                expected_cases[verification_id].add(case["id"])
    if isinstance(requirements, list):
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            req_id = requirement.get("id")
            verifications = requirement.get("verification", [])
            if not isinstance(verifications, list):
                continue
            for verification_id in verifications:
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
            actual_cases = spec.get("acceptance_case_ids")
            if (
                not isinstance(actual_cases, list)
                or not actual_cases
                or not all(isinstance(item, str) for item in actual_cases)
                or len(actual_cases) != len(set(actual_cases))
            ):
                errors.append(f"{spec_id} has no exact acceptance_case_ids")
            elif set(actual_cases) != expected_cases.get(spec_id, set()):
                errors.append(
                    f"{spec_id} reverse acceptance case binding differs: "
                    f"expected={sorted(expected_cases.get(spec_id, set()))}, "
                    f"actual={sorted(set(actual_cases))}"
                )
            elif isinstance(negative_sets, list):
                grouped_cases: set[str] = set()
                for fixture_id in negative_sets:
                    grouped_cases.update(fixture_cases_by_id.get(fixture_id, set()))
                missing_group_membership = set(actual_cases) - grouped_cases
                if missing_group_membership:
                    errors.append(
                        f"{spec_id} exact acceptance cases are absent from its fixture sets: "
                        f"{sorted(missing_group_membership)}"
                    )
            path = spec.get("evidence_path")
            if not isinstance(path, str) or not path.startswith("evidence/verification/"):
                errors.append(f"{spec_id} has invalid evidence_path")
            elif path in evidence_paths:
                errors.append(f"duplicate verification evidence path: {path}")
            else:
                evidence_paths.add(path)
            selector = spec.get("test_selector")
            if (
                not isinstance(selector, str)
                or not re.fullmatch(r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", selector)
            ):
                errors.append(f"{spec_id} has no parseable test_selector")
            elif selector in selectors:
                errors.append(f"duplicate verification test_selector: {selector}")
            else:
                selectors.add(selector)
            required_for = spec.get("required_for")
            if (
                not isinstance(required_for, list)
                or not required_for
                or not all(isinstance(item, str) for item in required_for)
                or len(required_for) != len(set(required_for))
                or not set(required_for).issubset(PHASES)
            ):
                errors.append(f"{spec_id} has invalid required_for phases")
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
        "started_at",
        "completed_at",
        "status",
        "input_hashes",
        "raw_result_hashes",
        "spec_sha256",
        "oracle_id",
        "oracle_observations",
        "acceptance_case_results",
        "selector_observation",
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
        if "not_run_preimplementation" not in set(result_schema.get("status_enum", [])):
            errors.append("verification result_schema lacks preimplementation state")
    return executor_ids


def verify_reference_cases(
    label: str,
    document: dict[str, Any],
    case_ids: set[str],
    errors: list[str],
) -> None:
    references = document.get("required_reference_cases")
    if (
        not isinstance(references, list)
        or not references
        or not all(isinstance(item, str) for item in references)
        or len(references) != len(set(references))
    ):
        errors.append(f"{label} required_reference_cases must be nonempty and unique")
        return
    unknown = set(references) - case_ids
    if unknown:
        errors.append(f"{label} references unknown acceptance cases: {sorted(unknown)}")


def verify_bound_items(
    items: Any,
    label: str,
    expected_ids: set[str],
    value_key: str,
    requirement_ids: set[str],
    verification_ids: set[str],
    case_ids: set[str],
    errors: list[str],
    *,
    shared_binding: dict[str, Any] | None = None,
) -> None:
    item_ids = unique_ids(items, label, errors)
    if item_ids != expected_ids:
        errors.append(
            f"{label} clause ids differ: "
            f"missing={sorted(expected_ids - item_ids)}, "
            f"extra={sorted(item_ids - expected_ids)}"
        )
    if not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        item_id = item.get("id", "<unknown>")
        if not isinstance(item.get(value_key), str) or not item.get(value_key):
            errors.append(f"{item_id} has no {value_key}")
        binding = shared_binding if shared_binding is not None else item
        for key, known in (
            ("requirement_ids", requirement_ids),
            ("verification_ids", verification_ids),
            ("acceptance_case_ids", case_ids),
        ):
            references = binding.get(key) if isinstance(binding, dict) else None
            if (
                not isinstance(references, list)
                or not references
                or not all(isinstance(reference, str) for reference in references)
            ):
                errors.append(f"{item_id} has no {key}")
                continue
            unknown = set(references) - known
            if unknown:
                errors.append(f"{item_id} references unknown {key}: {sorted(unknown)}")


def verify_expression(
    node: Any, allowed_operators: set[str], label: str, errors: list[str]
) -> None:
    if isinstance(node, str):
        return
    if not isinstance(node, dict):
        errors.append(f"{label} expression node must be string or object")
        return
    operator = node.get("op")
    arguments = node.get("args")
    if operator not in allowed_operators:
        errors.append(f"{label} uses unknown expression operator: {operator!r}")
    if not isinstance(arguments, list) or not arguments:
        errors.append(f"{label} expression has no args")
        return
    for index, argument in enumerate(arguments):
        verify_expression(argument, allowed_operators, f"{label}.args[{index}]", errors)


def verify_normative_policy_anchors(
    money: dict[str, Any],
    market: dict[str, Any],
    field: dict[str, Any],
    private: dict[str, Any],
    requirement_ids: set[str],
    verification_ids: set[str],
    case_ids: set[str],
    errors: list[str],
) -> None:
    decimal = money.get("decimal_context")
    if not isinstance(decimal, dict):
        errors.append("money decimal_context must be an object")
    else:
        expected_decimal = {
            "rounding": "ROUND_HALF_EVEN",
            "price_quantum": "0.000001",
            "quantity_quantum": "0.00000001",
            "money_quantum": "0.01",
            "fee_quantum": "0.01",
            "ratio_quantum": "0.00000001",
            "float_input_allowed": False,
            "canonical_input": "base-10 string parsed directly as Decimal",
        }
        if decimal != expected_decimal:
            errors.append("money decimal_context differs from the frozen V1 semantics")
    expression_language = money.get("expression_language")
    allowed_operators = (
        set(expression_language.get("operators", {}))
        if isinstance(expression_language, dict)
        else set()
    )
    if (
        not isinstance(expression_language, dict)
        or expression_language.get("numeric_type")
        != "Decimal_from_canonical_base10_string"
        or not {
            "add",
            "subtract",
            "multiply",
            "sum",
            "negate",
            "quantize",
            "map_quantized_multiply",
        }.issubset(allowed_operators)
    ):
        errors.append("money expression language differs")
    evaluator_ids = unique_ids(
        money.get("invariant_evaluators"), "money invariant evaluators", errors
    )
    booking_rules = money.get("booking_rules")
    booking_ids = unique_ids(booking_rules, "money booking rules", errors)
    if booking_ids != {"MONEY-BOOK-BUY", "MONEY-BOOK-SELL", "MONEY-NAV"}:
        errors.append("money booking rule ids differ")
    if isinstance(booking_rules, list):
        for booking in booking_rules:
            if not isinstance(booking, dict):
                continue
            booking_id = booking.get("id", "<unknown>")
            for key, known in (
                ("requirement_ids", requirement_ids),
                ("verification_ids", verification_ids),
                ("acceptance_case_ids", case_ids),
            ):
                references = booking.get(key)
                if (
                    not isinstance(references, list)
                    or not references
                    or set(references) - known
                ):
                    errors.append(f"{booking_id} has invalid {key}")
            steps = booking.get("calculation_steps")
            step_ids = unique_ids(steps, f"{booking_id} calculation steps", errors)
            if not step_ids:
                errors.append(f"{booking_id} has no calculation steps")
            if isinstance(steps, list):
                outputs: set[str] = set()
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    output = step.get("output")
                    if not isinstance(output, str) or output in outputs:
                        errors.append(f"{booking_id} has invalid or duplicate output")
                    else:
                        outputs.add(output)
                    verify_expression(
                        {"op": step.get("op"), "args": step.get("args")},
                        allowed_operators,
                        f"{booking_id}.{step.get('id')}",
                        errors,
                    )
            invariants = booking.get("invariants")
            invariant_ids = unique_ids(invariants, f"{booking_id} invariants", errors)
            if not invariant_ids:
                errors.append(f"{booking_id} has no structured invariants")
            if isinstance(invariants, list):
                for invariant in invariants:
                    if not isinstance(invariant, dict):
                        continue
                    if invariant.get("evaluator_id") not in evaluator_ids:
                        errors.append(
                            f"{invariant.get('id', '<unknown>')} uses unknown evaluator"
                        )
                    for expression_key in ("left", "right"):
                        if expression_key in invariant:
                            verify_expression(
                                invariant[expression_key],
                                allowed_operators,
                                f"{invariant.get('id')}.{expression_key}",
                                errors,
                            )

    actions = money.get("corporate_action_matrix")
    action_types = {
        item.get("type") for item in actions if isinstance(item, dict)
    } if isinstance(actions, list) else set()
    expected_actions = {
        "split",
        "reverse_split",
        "cash_dividend",
        "ticker_or_name_change",
        "cash_merger",
        "stock_merger",
        "spinoff",
        "cash_in_lieu",
        "delisting_or_bankruptcy",
        "correction_or_reversal",
    }
    if action_types != expected_actions:
        errors.append("money corporate action matrix differs")
    expected_action_ids = {
        "ACTION-SPLIT",
        "ACTION-REVERSE-SPLIT",
        "ACTION-CASH-DIVIDEND",
        "ACTION-TICKER-NAME-CHANGE",
        "ACTION-CASH-MERGER",
        "ACTION-STOCK-MERGER",
        "ACTION-SPINOFF",
        "ACTION-CASH-IN-LIEU",
        "ACTION-DELISTING-BANKRUPTCY",
        "ACTION-CORRECTION-REVERSAL",
    }
    verify_bound_items(
        actions,
        "money corporate actions",
        expected_action_ids,
        "effect",
        requirement_ids,
        verification_ids,
        case_ids,
        errors,
    )
    if money.get("corporate_action_idempotency_key_fields") != [
        "provider",
        "stable_security_id",
        "effective_at",
        "action_type",
        "revision_id",
    ]:
        errors.append("money corporate action idempotency key differs")
    if "one SQLite transaction" not in str(money.get("transaction_boundary", "")):
        errors.append("money transaction boundary is not atomic")

    calendar = market.get("calendar_and_causality")
    benchmark = market.get("benchmark_policy")
    lineage = market.get("experiment_lineage")
    if not isinstance(calendar, dict) or calendar.get("earliest_default_fill") != (
        "next eligible session T+1 using the preregistered fill-price model"
    ):
        errors.append("market default fill timing differs")
    benchmark_fields = benchmark.get("required_fields") if isinstance(benchmark, dict) else None
    verify_bound_items(
        benchmark_fields,
        "market benchmark fields",
        {
            "BENCHMARK-SECURITY",
            "BENCHMARK-SUITABILITY",
            "BENCHMARK-CURRENCY",
            "BENCHMARK-CALENDAR",
            "BENCHMARK-TOTAL-RETURN",
            "BENCHMARK-COST",
            "BENCHMARK-CASH",
        },
        "field",
        requirement_ids,
        verification_ids,
        case_ids,
        errors,
    )
    if not isinstance(benchmark, dict) or not any(
        isinstance(item, dict) and item.get("field") == "total-return method"
        for item in (benchmark_fields or [])
    ):
        errors.append("market benchmark lacks total-return semantics")
    lineage_fields = lineage.get("root_fingerprint_fields") if isinstance(lineage, dict) else None
    verify_bound_items(
        lineage_fields,
        "market root fingerprint fields",
        {
            "ROOT-ECONOMIC-MECHANISM",
            "ROOT-SIGNAL-GRAPH",
            "ROOT-DECISION-CADENCE",
            "ROOT-UNIVERSE-FAMILY",
            "ROOT-DATA-TRANSFORMS",
            "ROOT-BENCHMARK-FAMILY",
            "ROOT-PRIMARY-METRIC",
        },
        "field",
        requirement_ids,
        verification_ids,
        case_ids,
        errors,
    )
    if (
        not isinstance(lineage, dict)
        or lineage.get("rename_does_not_reset") is not True
        or lineage.get("ai_origin_contamination_default") != "unknown_contaminated"
        or "does not emit strategy-edge pass/fail" not in str(
            lineage.get("statistical_claim_rule", "")
        )
    ):
        errors.append("market experiment lineage or claim boundary differs")

    onboarding = field.get("human_onboarding")
    urgency = field.get("urgency_state_machine")
    longitudinal = field.get("longitudinal_protocol")
    if (
        not isinstance(onboarding, dict)
        or onboarding.get("requires_real_human_executor") is not True
        or onboarding.get("initial_policy_cooling", {}).get("minimum_hours") != 24
    ):
        errors.append("field-use human onboarding boundary differs")
    if isinstance(onboarding, dict):
        verify_bound_items(
            onboarding.get("required_inputs"),
            "field-use onboarding inputs",
            {
                "ONBOARD-HUMAN-CAPABILITY",
                "ONBOARD-PAPER-MANDATE",
                "ONBOARD-RISK-PARAMETERS",
                "ONBOARD-REAL-SNAPSHOT",
                "ONBOARD-REAL-RESEARCH",
                "ONBOARD-HUMAN-DECISION",
            },
            "field",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
        )
        verify_bound_items(
            onboarding.get("prohibited_substitutes"),
            "field-use prohibited substitutes",
            {
                "SUBSTITUTE-FIXTURE-JOURNEY",
                "SUBSTITUTE-AI-HUMAN-FIELDS",
                "SUBSTITUTE-ACTOR-LABEL",
                "SUBSTITUTE-BUILDER-SCREENSHOT",
            },
            "field",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
        )
    urgency_states = (
        {
            item.get("id"): item.get("new_order_delay_hours")
            for item in urgency.get("states", [])
            if isinstance(item, dict)
        }
        if isinstance(urgency, dict)
        else {}
    )
    if urgency_states != {"calm": 0, "elevated": 0, "urgent": 4, "panic": 24}:
        errors.append("field-use urgency state machine differs")
    if (
        not isinstance(urgency, dict)
        or "AI/import cannot set it" not in str(urgency.get("rule", ""))
        or "does not prove reflection" not in str(urgency.get("anti_rubber_stamp", ""))
    ):
        errors.append("field-use anti-rubber-stamp boundary differs")
    if (
        not isinstance(longitudinal, dict)
        or longitudinal.get("must_be_preregistered_by_human_before_window") is not True
        or "design_reopened" not in str(longitudinal.get("failure_rule", ""))
    ):
        errors.append("field-use longitudinal failure rule differs")
    if isinstance(longitudinal, dict):
        verify_bound_items(
            longitudinal.get("required_human_fields_without_defaults"),
            "field-use required human fields",
            {
                "FIELD-WINDOW-START",
                "FIELD-WINDOW-END",
                "FIELD-MIN-REAL-RESEARCH",
                "FIELD-MIN-NO-TRADE",
                "FIELD-MAX-ACTIVE-MINUTES",
                "FIELD-MAX-OVERDUE-RATE",
                "FIELD-ABANDONMENT",
                "FIELD-BEHAVIOR-SUCCESS",
                "FIELD-FAILURE-ACTION",
            },
            "field",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
            shared_binding=longitudinal.get("required_human_fields_binding"),
        )
        verify_bound_items(
            longitudinal.get("minimum_structure"),
            "field-use minimum structure",
            {
                "FIELD-ORDERED-WINDOW",
                "FIELD-POST-REGISTRATION-ONLY",
                "FIELD-NO-FIXTURE-COUNT",
                "FIELD-ALL-ATTEMPTS-COUNT",
                "FIELD-NATURAL-LONG-GAP",
            },
            "rule",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
            shared_binding=longitudinal.get("minimum_structure_binding"),
        )

    runtime = private.get("runtime_storage")
    backup = private.get("backup_storage")
    if (
        not isinstance(runtime, dict)
        or runtime.get("default")
        != "~/Library/Application Support/InvestmentDisciplineSystem"
        or runtime.get("directory_mode") != "0700"
        or runtime.get("file_mode") != "0600"
        or runtime.get("symlink_components_allowed") is not False
    ):
        errors.append("private runtime storage boundary differs")
    if isinstance(runtime, dict):
        verify_bound_items(
            runtime.get("must_be_outside"),
            "private runtime exclusion clauses",
            {
                "PRIVATE-OUTSIDE-GIT",
                "PRIVATE-OUTSIDE-PROJECT",
                "PRIVATE-OUTSIDE-SYNC",
            },
            "field",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
        )
    if (
        not isinstance(backup, dict)
        or backup.get("application_encryption") != "not_implemented_do_not_invent_crypto"
        or "never overwrites" not in str(backup.get("immutability", ""))
        or "no automatic deletion" not in str(backup.get("retention", ""))
    ):
        errors.append("private backup lifecycle boundary differs")
    if isinstance(backup, dict):
        verify_bound_items(
            backup.get("manifest"),
            "private backup manifest clauses",
            {
                "BACKUP-MANIFEST-CLASSIFICATION",
                "BACKUP-MANIFEST-DATABASE-HASH",
                "BACKUP-MANIFEST-ANCHOR-HASH",
                "BACKUP-MANIFEST-ARTIFACT-HASHES",
                "BACKUP-MANIFEST-SCHEMA",
                "BACKUP-MANIFEST-APP-COMMIT",
                "BACKUP-MANIFEST-PERMISSIONS",
                "BACKUP-MANIFEST-ENCRYPTION",
                "BACKUP-MANIFEST-CREATED-AT",
            },
            "field",
            requirement_ids,
            verification_ids,
            case_ids,
            errors,
            shared_binding=backup.get("manifest_clause_binding"),
        )


def verify_implementation_targets(
    targets_doc: dict[str, Any],
    trace_targets: set[str],
    allow_candidate: bool,
    errors: list[str],
) -> set[str]:
    targets = targets_doc.get("targets")
    if not isinstance(targets, list):
        errors.append("implementation targets must be a list")
        return set()
    seen: set[str] = set()
    declared: set[str] = set()
    for index, target in enumerate(targets):
        if not isinstance(target, dict):
            errors.append(f"implementation targets[{index}] must be object")
            continue
        relative = target.get("path")
        kind = target.get("kind")
        required_by = target.get("required_by")
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            errors.append(f"implementation targets[{index}] has unsafe path")
            continue
        if relative in seen:
            errors.append(f"duplicate implementation target: {relative}")
        seen.add(relative)
        declared.add(relative)
        if kind not in {"file", "directory"}:
            errors.append(f"{relative} has invalid target kind")
        if required_by not in {"design_freeze", "bundle_creation", "product_release"}:
            errors.append(f"{relative} has invalid required_by stage")
            continue
        path = PROJECT_ROOT / relative
        must_exist = required_by == "design_freeze" or (
            not allow_candidate and required_by == "bundle_creation"
        )
        if must_exist:
            exists = path.is_file() if kind == "file" else path.is_dir()
            if not exists:
                errors.append(f"required {required_by} implementation target missing: {relative}")
    if declared != trace_targets:
        errors.append(
            "implementation target coverage differs: "
            f"missing={sorted(trace_targets - declared)}, "
            f"extra={sorted(declared - trace_targets)}"
        )
    return declared


def markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        heading = match.group(1).strip().lower()
        heading = re.sub(r"[`*_{}\[\]()#+.!?\"'“”‘’：:，,。、/\\|]", "", heading)
        heading = re.sub(r"\s+", "-", heading)
        anchors.add(heading)
    return anchors


def verify_gate_catalogs(
    contract: dict[str, Any], executor_ids: set[str], errors: list[str]
) -> None:
    gates = contract.get("gates")
    conditional_catalog = contract.get("conditional_gate_catalog")
    gate_ids = unique_ids(gates, "gates", errors)
    conditional_catalog_ids = unique_ids(
        conditional_catalog, "conditional gate catalog", errors
    )
    for label, entries in (("gate", gates), ("conditional gate", conditional_catalog)):
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            entry_id = entry.get("id", "<unknown>")
            command = entry.get("command")
            executors = entry.get("executor_ids")
            if not isinstance(command, str) or not command:
                errors.append(f"{entry_id} {label} command is missing")
            if (
                not isinstance(executors, list)
                or not executors
                or set(executors) - executor_ids
            ):
                errors.append(f"{entry_id} {label} executor is missing")
    used_conditional_catalog: set[str] = set()
    for condition in contract.get("conditional_gates", []):
        if not isinstance(condition, dict):
            continue
        mandatory = condition.get("mandatory_gate_when_ready")
        if mandatory is not None:
            if mandatory not in conditional_catalog_ids:
                errors.append(
                    f"{condition.get('id', '<unknown>')} conditional gate executor is missing"
                )
            else:
                used_conditional_catalog.add(mandatory)
    if used_conditional_catalog != conditional_catalog_ids:
        errors.append(
            "conditional gate catalog coverage differs: "
            f"unused={sorted(conditional_catalog_ids - used_conditional_catalog)}"
        )
    if "GATE-09-GIT-STATE" not in gate_ids:
        errors.append("local git state gate is missing")


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
    contract: dict[str, Any],
    requirement_ids: set[str],
    case_ids: set[str],
    errors: list[str],
) -> None:
    conditional_gates = contract.get("conditional_gates")
    if not isinstance(conditional_gates, list):
        return
    evidence_schema = contract.get("conditional_evidence_schema")
    required_evidence_fields = {
        "schema_version",
        "condition_id",
        "gate_id",
        "gate_stage",
        "state",
        "candidate_commit",
        "candidate_tree",
        "frozen_bundle_sha256",
        "executor_ids",
        "acceptance_case_ids",
        "raw_result_path",
        "raw_result_sha256",
        "completed_at",
    }
    if (
        not isinstance(evidence_schema, dict)
        or set(evidence_schema.get("required", [])) != required_evidence_fields
        or set(evidence_schema.get("state_enum", []))
        != {"passed", "failed", "inconclusive"}
    ):
        errors.append("conditional evidence schema differs")
    required_fields = {
        "applies_to_requirements",
        "severity",
        "prerequisite_probe",
        "allowed_states",
        "transition_table",
        "mandatory_gate_when_ready",
        "evidence_path",
        "required_acceptance_case_ids_by_stage",
        "release_mapping",
        "must_not_be_claimed",
    }
    probe_ids: set[str] = set()
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
        if (
            not isinstance(states, list)
            or not states
            or not all(isinstance(state, str) for state in states)
            or len(states) != len(set(states))
        ):
            errors.append(f"{gate_id} has no allowed_states")
        else:
            transition_table = gate.get("transition_table")
            if not isinstance(transition_table, dict) or not transition_table:
                errors.append(f"{gate_id} transition_table must be a nonempty object")
            else:
                unknown_states = {
                    state
                    for state in transition_table.values()
                    if not isinstance(state, str) or state not in states
                }
                if unknown_states:
                    errors.append(
                        f"{gate_id} transition_table uses unknown states: "
                        f"{sorted(str(state) for state in unknown_states)}"
                    )
        probe = gate.get("prerequisite_probe")
        if not isinstance(probe, dict):
            errors.append(f"{gate_id} prerequisite_probe must be structured")
        else:
            probe_id = probe.get("id")
            authority = probe.get("authority")
            selector = probe.get("selector")
            if not isinstance(probe_id, str) or not probe_id:
                errors.append(f"{gate_id} prerequisite probe id is missing")
            elif probe_id in probe_ids:
                errors.append(f"duplicate prerequisite probe id: {probe_id}")
            else:
                probe_ids.add(probe_id)
            if authority not in {
                "process_environment_presence",
                "frozen_contract_scope",
                "runtime_sqlite_event_chain",
            }:
                errors.append(f"{gate_id} prerequisite authority is not independent")
            if (
                not isinstance(selector, str)
                or not re.fullmatch(
                    r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+", selector
                )
            ):
                errors.append(f"{gate_id} prerequisite selector is not parseable")
            if not isinstance(probe.get("ready_when"), dict):
                errors.append(f"{gate_id} prerequisite ready_when must be structured")
            if authority == "runtime_sqlite_event_chain":
                required_observations = probe.get("required_observation_fields")
                if (
                    probe.get("table") != "condition_observations"
                    or not isinstance(required_observations, list)
                    or not {
                        "condition_id",
                        "stage",
                        "ready",
                        "source_event_seq",
                        "source_state_hash",
                        "observed_at",
                    }.issubset(set(required_observations))
                ):
                    errors.append(
                        f"{gate_id} runtime prerequisite lacks authoritative observation binding"
                    )
            if "prerequisite_ready" in probe:
                errors.append(f"{gate_id} trusts self-reported prerequisite readiness")
        release_mapping = gate.get("release_mapping")
        if not isinstance(release_mapping, dict) or not release_mapping:
            errors.append(f"{gate_id} release_mapping must be structured")
        stage_cases = gate.get("required_acceptance_case_ids_by_stage")
        if not isinstance(stage_cases, dict) or not stage_cases:
            errors.append(f"{gate_id} has no stage acceptance cases")
        else:
            for stage, references in stage_cases.items():
                if (
                    not isinstance(stage, str)
                    or not isinstance(references, list)
                    or not references
                    or not all(isinstance(item, str) for item in references)
                ):
                    errors.append(f"{gate_id} has invalid stage acceptance cases")
                    continue
                unknown_cases = set(references) - case_ids
                if unknown_cases:
                    errors.append(
                        f"{gate_id} references unknown conditional cases: "
                        f"{sorted(unknown_cases)}"
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
    acceptance_cases = load_json(ACCEPTANCE_CASES, errors)
    money_spec = load_json(MONEY_SPEC, errors)
    market_policy = load_json(MARKET_POLICY, errors)
    field_protocol = load_json(FIELD_PROTOCOL, errors)
    private_data_policy = load_json(PRIVATE_DATA_POLICY, errors)
    implementation_targets = load_json(IMPLEMENTATION_TARGETS, errors)

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
        ("acceptance cases", acceptance_cases),
        ("money and corporate actions spec", money_spec),
        ("market simulation policy", market_policy),
        ("field use protocol", field_protocol),
        ("private data policy", private_data_policy),
        ("implementation targets", implementation_targets),
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
    unique_ids(contract.get("conditional_gates"), "conditional_gates", errors)
    case_ids = verify_acceptance_cases(
        acceptance_cases, requirement_ids, verification_ids, errors
    )
    executor_ids = verify_verification_specs(
        verification_specs,
        verification_ids,
        requirements,
        acceptance_cases,
        case_ids,
        errors,
    )
    verify_assurance_subjects(assurance_subjects, research, errors)
    verify_conditionals(contract, requirement_ids, case_ids, errors)
    verify_gate_catalogs(contract, executor_ids, errors)
    for label, document in (
        ("money spec", money_spec),
        ("market policy", market_policy),
        ("field use protocol", field_protocol),
        ("private data policy", private_data_policy),
    ):
        verify_reference_cases(label, document, case_ids, errors)
    verify_normative_policy_anchors(
        money_spec,
        market_policy,
        field_protocol,
        private_data_policy,
        requirement_ids,
        verification_ids,
        case_ids,
        errors,
    )
    expected_frozen_files = set(NORMATIVE_JSON_PATHS) | {
        "PRODUCT_ASSURANCE_BLUEPRINT_V2.md"
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

    trace_targets: set[str] = set()
    blueprint_anchors = markdown_anchors(BLUEPRINT) if BLUEPRINT.is_file() else set()
    if isinstance(controls, list):
        for control in controls:
            if not isinstance(control, dict):
                continue
            control_id = control.get("id", "<unknown>")
            targets = control.get("implementation_targets")
            if not isinstance(targets, list) or not targets:
                errors.append(f"{control_id} has no implementation targets")
            elif not all(isinstance(target, str) for target in targets):
                errors.append(f"{control_id} implementation targets must be strings")
            else:
                trace_targets.update(targets)
            design_ref = control.get("design_ref")
            if not isinstance(design_ref, str) or "#" not in design_ref:
                errors.append(f"{control_id} has invalid design_ref")
            else:
                design_path, anchor = design_ref.split("#", 1)
                if design_path != "PRODUCT_ASSURANCE_BLUEPRINT_V2.md":
                    errors.append(f"{control_id} design_ref uses an unknown document")
                elif anchor not in blueprint_anchors:
                    errors.append(
                        f"{control_id} design_ref anchor is missing: {anchor}"
                    )

    verify_implementation_targets(
        implementation_targets, trace_targets, allow_candidate, errors
    )

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
