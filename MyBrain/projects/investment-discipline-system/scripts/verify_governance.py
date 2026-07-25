#!/usr/bin/env python3
"""Verify the frozen intent, acceptance contract, and traceability baseline."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
ASSURANCE_TRUST_MODEL = GOVERNANCE / "ASSURANCE_TRUST_MODEL_V1.json"
GROUND_TRUTH_MANIFEST = GOVERNANCE / "GROUND_TRUTH_MANIFEST_V1.json"
RESEARCH_SUFFICIENCY = GOVERNANCE / "RESEARCH_SUFFICIENCY_V1.json"
FAILURE_CLASSES = GOVERNANCE / "FAILURE_CLASSES_V1.json"
DECISION_AUTHORITY = GOVERNANCE / "DECISION_AUTHORITY_V1.json"
PROJECT_METHOD_POLICY = GOVERNANCE / "PROJECT_METHOD_POLICY_V1.json"
BLUEPRINT = PROJECT_ROOT / "PRODUCT_ASSURANCE_BLUEPRINT_V2.md"
FROZEN_BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"
ATTACK_RUNNER = PROJECT_ROOT / "scripts" / "run_design_freeze_attack.py"
REPLAY_ATTACKS = PROJECT_ROOT / "scripts" / "replay_design_freeze_attacks.py"
ASSURANCE_WORKFLOW_REPO_PATH = (
    ".github/workflows/investment-discipline-assurance.yml"
)
REPOSITORY_SCOPE_PREFIX = "@repo/"
INNER_REMOTE_CONTEXT_ENV = "IDS_FROZEN_REMOTE_INNER_CONTEXT_V1"
EXPECTED_TRUSTED_GIT_REMOTE = {
    "name": "origin",
    "fetch_url": "git@github.com:j-a-v-e-n/knowledge-vault.git",
    "branch": "main",
    "project_prefix": "MyBrain/projects/investment-discipline-system/",
}

PHASES = {"design_freeze", "product_release", "human_onboarding", "longitudinal"}
FINAL_REVIEW_ATTACK_IDS = [
    "ATTACK-PIT-ORACLE-INVERSION",
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
    "ATTACK-CONDITIONAL-SELF-ATTESTATION",
]
FINAL_REVIEW_REQUIRED_SCOPE = {
    "PROJECT_CHARTER.md",
    "DECISIONS.md",
    "AI_COLLABORATION_METHOD.md",
    "EVIDENCE_GOVERNED_AI_SYSTEM.md",
    "scripts/verify_governance.py",
    "scripts/verify_conditionals.py",
    "scripts/freeze_governance.py",
    "scripts/verify_git_state.py",
    "scripts/verify_remote_commit.py",
    "scripts/run_design_freeze_attack.py",
    "scripts/replay_design_freeze_attacks.py",
    "scripts/run_assurance_ci.py",
    "scripts/refresh_ground_truth_manifest.py",
    "scripts/verify_assurance_metadata.py",
    "scripts/verify_project_method.py",
    "scripts/verify_research_sufficiency.py",
    "scripts/verify_contract_supersession.py",
    "README.md",
    "STATUS.md",
    "governance_tests/test_final_review_attacks.py",
    "governance_tests/test_final_review_schema.py",
    "governance_tests/test_attack_runner.py",
    "governance_tests/test_assurance_metadata.py",
    "governance_tests/test_project_method.py",
    "governance_tests/test_research_sufficiency.py",
    "governance_tests/test_research_evidence_governance.py",
    "governance_tests/test_verify_conditionals.py",
    "governance_tests/test_freeze_git_remote.py",
    "governance_tests/test_verify_governance.py",
    "governance_tests/test_verify_money_semantics.py",
    f"{REPOSITORY_SCOPE_PREFIX}{ASSURANCE_WORKFLOW_REPO_PATH}",
}
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
    "governance/PROJECT_METHOD_POLICY_V1.json",
    "governance/IMPLEMENTATION_TARGETS_V1.json",
    "governance/VERIFICATION_SPECS_V1.json",
    "governance/TRACEABILITY_V1.json",
    "governance/ASSURANCE_SUBJECTS_V1.json",
    "governance/ASSURANCE_TRUST_MODEL_V1.json",
    "governance/GROUND_TRUTH_MANIFEST_V1.json",
    "governance/RESEARCH_SUFFICIENCY_V1.json",
    "governance/FAILURE_CLASSES_V1.json",
    "governance/DECISION_AUTHORITY_V1.json",
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


def nonempty_unique_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and bool(item) for item in value)
        and len(value) == len(set(value))
    )


def safe_relative_file(value: Any, *, prefix: str | None = None) -> Path | None:
    if (
        not isinstance(value, str)
        or not value
        or Path(value).is_absolute()
        or ".." in Path(value).parts
        or (prefix is not None and not value.startswith(prefix))
    ):
        return None
    path = PROJECT_ROOT / value
    return path if path.is_file() else None


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


def review_reference_repo_path(
    reference: str,
    *,
    project_prefix: str,
) -> str | None:
    if reference.startswith(REPOSITORY_SCOPE_PREFIX):
        relative = reference.removeprefix(REPOSITORY_SCOPE_PREFIX)
    else:
        relative = f"{project_prefix}{reference}"
    if (
        not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
        or "\\" in relative
    ):
        return None
    return relative


def verify_bound_project_file(
    evidence: dict[str, Any],
    *,
    path_field: str,
    hash_field: str,
    required_path: str | None,
    prefix: str | None,
    label: str,
    errors: list[str],
) -> Path | None:
    relative = evidence.get(path_field)
    expected_hash = evidence.get(hash_field)
    path = safe_relative_file(relative, prefix=prefix)
    if (
        path is None
        or (required_path is not None and relative != required_path)
        or not isinstance(expected_hash, str)
        or re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None
    ):
        errors.append(f"{label} binding is invalid")
        return None
    if sha256(path) != expected_hash:
        errors.append(f"{label} sha256 mismatch")
        return None
    return path


def runner_receipt_fingerprint_payload(
    receipt: dict[str, Any],
) -> dict[str, Any]:
    keys = (
        "runner_id",
        "runner_sha256",
        "candidate_commit",
        "candidate_tree",
        "project_prefix",
        "mode",
        "probe_id",
        "mutation_spec_sha256",
        "mutation_observation",
        "baseline",
        "target",
        "expected_rejection_substring",
        "result",
        "runner_exit_code",
    )
    return {key: receipt.get(key) for key in keys}


def verify_runner_receipt_shape(
    receipt: dict[str, Any],
    *,
    candidate_commit: Any,
    candidate_tree: Any,
    mode: str,
    probe_id: str,
    label: str,
    errors: list[str],
) -> None:
    required_fields = {
        "schema_version",
        "runner_id",
        "runner_sha256",
        "candidate_commit",
        "candidate_tree",
        "project_prefix",
        "mode",
        "probe_id",
        "mutation_spec_sha256",
        "mutation_observation",
        "baseline",
        "target",
        "expected_rejection_substring",
        "result",
        "runner_exit_code",
        "started_at",
        "completed_at",
        "execution_fingerprint",
    }
    if set(receipt) != required_fields:
        errors.append(f"{label} runner receipt fields differ")
    project_prefix = run_git(["rev-parse", "--show-prefix"], errors)
    expected = {
        "schema_version": 2,
        "runner_id": "ids-design-freeze-attack-runner-v1",
        "runner_sha256": sha256(ATTACK_RUNNER),
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "project_prefix": project_prefix,
        "mode": mode,
        "probe_id": probe_id,
        "result": "rejected",
        "runner_exit_code": 0,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            errors.append(f"{label} runner receipt {key} differs")
    for phase, expected_zero in (("baseline", True), ("target", False)):
        record = receipt.get(phase)
        if not isinstance(record, dict) or set(record) != {
            "argv",
            "exit_code",
            "stdout",
            "stdout_sha256",
        }:
            errors.append(f"{label} {phase} execution record differs")
            continue
        stdout = record.get("stdout")
        exit_code = record.get("exit_code")
        if (
            record.get("argv")
            != ["PYTHON", "scripts/verify_governance.py", "--allow-candidate"]
            or type(exit_code) is not int
            or not isinstance(stdout, str)
            or record.get("stdout_sha256") != sha256_text(stdout)
            or (expected_zero and exit_code != 0)
            or (not expected_zero and exit_code == 0)
        ):
            errors.append(f"{label} {phase} actual execution binding differs")
    expected_signal = receipt.get("expected_rejection_substring")
    target = receipt.get("target")
    if (
        not isinstance(expected_signal, str)
        or not expected_signal
        or not isinstance(target, dict)
        or not isinstance(target.get("stdout"), str)
        or expected_signal not in target["stdout"]
    ):
        errors.append(f"{label} target rejection signal differs")
    fingerprint = receipt.get("execution_fingerprint")
    if (
        not isinstance(fingerprint, str)
        or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
        or fingerprint
        != hashlib.sha256(
            json.dumps(
                runner_receipt_fingerprint_payload(receipt),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
    ):
        errors.append(f"{label} execution fingerprint differs")


def reexecute_runner_receipt(
    *,
    candidate_commit: str,
    attack_id: str | None,
    novelty_spec: Path | None,
    expected_fingerprint: Any,
    label: str,
    errors: list[str],
) -> None:
    argv = [
        sys.executable,
        str(ATTACK_RUNNER),
        "--candidate-commit",
        candidate_commit,
    ]
    if attack_id is not None:
        argv.extend(["--attack-id", attack_id])
    elif novelty_spec is not None:
        argv.extend(["--novelty-spec", str(novelty_spec)])
    else:
        errors.append(f"{label} has no executable mutation")
        return
    completed = subprocess.run(
        argv,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        actual = json.loads(completed.stdout)
    except json.JSONDecodeError:
        actual = None
    if (
        completed.returncode != 0
        or not isinstance(actual, dict)
        or actual.get("runner_exit_code") != completed.returncode
        or actual.get("result") != "rejected"
        or actual.get("execution_fingerprint") != expected_fingerprint
    ):
        errors.append(
            f"{label} actual runner replay differs: "
            f"process_exit={completed.returncode}, "
            f"output={completed.stdout[-1000:]!r}"
        )


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
    case_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(cases, list):
        return case_ids
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            continue
        case_id = case.get("id", f"acceptance cases[{index}]")
        if isinstance(case_id, str):
            case_by_id[case_id] = case
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
    freeze_critical_case_semantics = {
        "CASE-PIT-LATE-RETRIEVAL": {
            "preconditions": {
                "decision_at": "2024-01-02T21:00:00Z",
                "system_recorded_at": "2026-01-02T21:00:00Z",
                "verifiable_vintage": False,
            },
            "operation": {
                "action": "admit snapshot to historical decision/backtest"
            },
            "expected": {
                "accepted": False,
                "reason": "snapshot_recorded_after_decision_without_vintage",
            },
        },
        "CASE-PIT-LENGTH-MISMATCH": {
            "preconditions": {
                "visible_dates_count": 0,
                "strategy_dates_count": 1,
            },
            "operation": {"action": "validate temporal coverage"},
            "expected": {
                "accepted": False,
                "reason": "date_domain_mismatch",
            },
        },
        "CASE-CALENDAR-MISSING-SESSION": {
            "preconditions": {
                "exchange_calendar_sessions": 3,
                "strategy_rows": 2,
                "benchmark_rows": 3,
            },
            "operation": {"action": "run backtest using row intersection"},
            "expected": {
                "run_status": "rejected",
                "coverage_missing_sessions": 1,
            },
        },
        "CASE-BENCHMARK-TOTAL-RETURN": {
            "preconditions": {
                "benchmark_start_price": "100.00",
                "benchmark_end_price": "100.00",
                "cash_dividend": "2.00",
                "shares": "1.00000000",
            },
            "operation": {"action": "compute benchmark ending value"},
            "expected": {
                "ending_value": "102.00",
                "price_only_value_is_invalid": "100.00",
            },
        },
        "CASE-DECISION-NEXT-BAR": {
            "preconditions": {
                "signal_basis": "session_T_close",
                "fill_attempt": "session_T_close",
            },
            "operation": {"action": "validate fill timing"},
            "expected": {
                "accepted": False,
                "earliest_default_fill": "next eligible session open",
            },
        },
        "CASE-DATA-SILENT-FALLBACK": {
            "preconditions": {
                "approved_feed": "tiingo_raw_eod",
                "observed_feed": "unapproved_fallback",
            },
            "operation": {
                "action": (
                    "admit snapshot to a run without an explicit "
                    "feed-change record"
                )
            },
            "expected": {
                "accepted": False,
                "reason": "unapproved_data_source_change",
                "observed_feed_recorded": True,
            },
        },
        "CASE-CORP-ACTION-ADJUSTED-MISMATCH": {
            "preconditions": {
                "local_raw_plus_actions_value": "102.00",
                "provider_adjusted_value": "100.00",
            },
            "operation": {"action": "reconcile adjusted series"},
            "expected": {
                "provider_adjusted_used_as_authority": False,
                "mismatch_recorded": True,
                "run_status": "incomplete",
            },
        },
    }
    for case_id, expected_semantics in freeze_critical_case_semantics.items():
        case = case_by_id.get(case_id)
        if case is None or any(
            case.get(field) != expected
            for field, expected in expected_semantics.items()
        ):
            errors.append(f"{case_id} freeze-critical semantics differ")
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
    node: Any,
    operator_specs: dict[str, Any],
    quantum_symbols: set[str],
    allowed_symbols: set[str],
    label: str,
    errors: list[str],
) -> None:
    if isinstance(node, str):
        if re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", node):
            return
        if node not in allowed_symbols:
            errors.append(f"{label} references unknown expression symbol: {node!r}")
        return
    if not isinstance(node, dict):
        errors.append(f"{label} expression node must be string or object")
        return
    extra_keys = set(node) - {"op", "args", "quantum"}
    if extra_keys:
        errors.append(f"{label} expression has unsupported keys: {sorted(extra_keys)}")
    operator = node.get("op")
    arguments = node.get("args")
    operator_spec = operator_specs.get(operator)
    if not isinstance(operator_spec, dict):
        errors.append(f"{label} uses unknown expression operator: {operator!r}")
    if not isinstance(arguments, list) or not arguments:
        errors.append(f"{label} expression has no args")
        return
    if isinstance(operator_spec, dict):
        exact_arity = operator_spec.get("arity")
        minimum_arity = operator_spec.get("minimum_arity")
        if isinstance(exact_arity, int) and len(arguments) != exact_arity:
            errors.append(
                f"{label} operator {operator} requires arity {exact_arity}, "
                f"got {len(arguments)}"
            )
        if isinstance(minimum_arity, int) and len(arguments) < minimum_arity:
            errors.append(
                f"{label} operator {operator} requires minimum arity "
                f"{minimum_arity}, got {len(arguments)}"
            )
        requires_quantum = operator_spec.get("requires_quantum") is True
        quantum = node.get("quantum")
        if requires_quantum and quantum not in quantum_symbols:
            errors.append(f"{label} operator {operator} lacks a valid quantum")
        if not requires_quantum and "quantum" in node:
            errors.append(f"{label} operator {operator} must not declare quantum")
    for index, argument in enumerate(arguments):
        verify_expression(
            argument,
            operator_specs,
            quantum_symbols,
            allowed_symbols,
            f"{label}.args[{index}]",
            errors,
        )


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
    expected_operator_specs = {
        "add": {"minimum_arity": 2},
        "subtract": {"minimum_arity": 2},
        "multiply": {"arity": 2},
        "sum": {"minimum_arity": 1},
        "negate": {"arity": 1},
        "quantize": {"arity": 1, "requires_quantum": True},
        "map_quantized_multiply": {"arity": 2, "requires_quantum": True},
    }
    operator_specs = (
        expression_language.get("operators", {})
        if isinstance(expression_language, dict)
        else {}
    )
    quantum_symbols = (
        set(expression_language.get("quantum_symbols", []))
        if isinstance(expression_language, dict)
        else set()
    )
    if (
        not isinstance(expression_language, dict)
        or expression_language.get("numeric_type")
        != "Decimal_from_canonical_base10_string"
        or operator_specs != expected_operator_specs
        or quantum_symbols != {"price", "quantity", "money", "fee", "ratio"}
    ):
        errors.append("money expression language differs")
    evaluator_ids = unique_ids(
        money.get("invariant_evaluators"), "money invariant evaluators", errors
    )
    expected_evaluators = {
        "EVAL-DECIMAL-EQUALITY": "typed_decimal_exact_equality",
        "EVAL-DECIMAL-GTE": "typed_decimal_greater_than_or_equal",
        "EVAL-SET-EQUALITY-OR-INCOMPLETE": "set_equality_else_explicit_incomplete_state",
        "EVAL-STATE-PREDICATE": "named_state_predicate",
    }
    actual_evaluators = {
        item.get("id"): item.get("kind")
        for item in money.get("invariant_evaluators", [])
        if isinstance(item, dict)
    }
    if actual_evaluators != expected_evaluators:
        errors.append("money invariant evaluator catalog differs")
    predicates = money.get("predicate_catalog")
    predicate_ids = unique_ids(predicates, "money predicate catalog", errors)
    predicate_by_id: dict[str, dict[str, Any]] = {}
    if predicate_ids != {"PRED-NAV-NO-SILENT-ZERO"}:
        errors.append("money predicate catalog ids differ")
    if isinstance(predicates, list):
        for predicate in predicates:
            if not isinstance(predicate, dict):
                continue
            predicate_id = predicate.get("id", "<unknown>")
            predicate_by_id[predicate_id] = predicate
            if predicate.get("evaluator_id") != "EVAL-STATE-PREDICATE":
                errors.append(f"{predicate_id} predicate evaluator differs")
            if (
                not isinstance(predicate.get("selector"), str)
                or not re.fullmatch(
                    r"[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+",
                    predicate.get("selector", ""),
                )
            ):
                errors.append(f"{predicate_id} predicate selector is not parseable")
            required_inputs = predicate.get("required_inputs")
            if (
                not isinstance(required_inputs, list)
                or not required_inputs
                or not all(isinstance(item, str) for item in required_inputs)
                or len(required_inputs) != len(set(required_inputs))
            ):
                errors.append(f"{predicate_id} predicate required_inputs differ")
            if predicate.get("expected") is not True:
                errors.append(f"{predicate_id} predicate expected value differs")
    booking_rules = money.get("booking_rules")
    booking_ids = unique_ids(booking_rules, "money booking rules", errors)
    if booking_ids != {"MONEY-BOOK-BUY", "MONEY-BOOK-SELL", "MONEY-NAV"}:
        errors.append("money booking rule ids differ")
    expected_step_ids = {
        "MONEY-BOOK-BUY": {
            "BUY-NOTIONAL",
            "BUY-CASH-AFTER",
            "BUY-POSITION-AFTER",
            "BUY-CASH-DELTA",
            "BUY-QUANTITY-DELTA",
        },
        "MONEY-BOOK-SELL": {
            "SELL-NOTIONAL",
            "SELL-CASH-AFTER",
            "SELL-POSITION-AFTER",
            "SELL-CASH-DELTA",
            "SELL-QUANTITY-DELTA",
        },
        "MONEY-NAV": {"NAV-POSITION-VALUE", "NAV-TOTAL"},
    }
    expected_invariant_ids = {
        "MONEY-BOOK-BUY": {
            "INV-BUY-CASH-CONSERVATION",
            "INV-BUY-QUANTITY-CONSERVATION",
        },
        "MONEY-BOOK-SELL": {
            "INV-SELL-CASH-CONSERVATION",
            "INV-SELL-QUANTITY-CONSERVATION",
            "INV-NO-SHORT-POSITION",
        },
        "MONEY-NAV": {
            "INV-NAV-MARK-COVERAGE",
            "INV-NAV-NO-SILENT-ZERO",
        },
    }
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
            inputs = booking.get("inputs")
            if (
                not isinstance(inputs, list)
                or not inputs
                or not all(
                    isinstance(item, str)
                    and re.fullmatch(r"[a-z][a-z0-9_]*", item)
                    for item in inputs
                )
                or len(inputs) != len(set(inputs))
            ):
                errors.append(f"{booking_id} has invalid inputs")
                input_symbols: set[str] = set()
            else:
                input_symbols = set(inputs)
            steps = booking.get("calculation_steps")
            step_ids = unique_ids(steps, f"{booking_id} calculation steps", errors)
            if step_ids != expected_step_ids.get(booking_id, set()):
                errors.append(f"{booking_id} calculation step ids differ")
            if isinstance(steps, list):
                outputs: set[str] = set()
                for step in steps:
                    if not isinstance(step, dict):
                        continue
                    output = step.get("output")
                    if not isinstance(output, str) or output in outputs:
                        errors.append(f"{booking_id} has invalid or duplicate output")
                    verify_expression(
                        {
                            key: step[key]
                            for key in ("op", "args", "quantum")
                            if key in step
                        },
                        operator_specs if isinstance(operator_specs, dict) else {},
                        quantum_symbols,
                        input_symbols | outputs,
                        f"{booking_id}.{step.get('id')}",
                        errors,
                    )
                    if isinstance(output, str) and output not in outputs:
                        outputs.add(output)
            invariants = booking.get("invariants")
            invariant_ids = unique_ids(invariants, f"{booking_id} invariants", errors)
            if invariant_ids != expected_invariant_ids.get(booking_id, set()):
                errors.append(f"{booking_id} invariant ids differ")
            if isinstance(invariants, list):
                for invariant in invariants:
                    if not isinstance(invariant, dict):
                        continue
                    evaluator_id = invariant.get("evaluator_id")
                    if evaluator_id not in evaluator_ids:
                        errors.append(
                            f"{invariant.get('id', '<unknown>')} uses unknown evaluator"
                        )
                    if evaluator_id == "EVAL-STATE-PREDICATE":
                        predicate_id = invariant.get("predicate_id")
                        predicate = predicate_by_id.get(predicate_id)
                        if predicate is None or "predicate" in invariant:
                            errors.append(
                                f"{invariant.get('id', '<unknown>')} predicate binding differs"
                            )
                        elif not set(predicate.get("required_inputs", [])).issubset(
                            input_symbols
                        ):
                            errors.append(
                                f"{invariant.get('id', '<unknown>')} predicate inputs "
                                "are absent from booking inputs"
                            )
                    else:
                        if not {"left", "right"}.issubset(invariant):
                            errors.append(
                                f"{invariant.get('id', '<unknown>')} lacks invariant operands"
                            )
                        for expression_key in ("left", "right"):
                            if expression_key not in invariant:
                                continue
                            verify_expression(
                                invariant[expression_key],
                                operator_specs
                                if isinstance(operator_specs, dict)
                                else {},
                                quantum_symbols,
                                input_symbols | outputs,
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
    expected_action_modes = {
        "ACTION-SPLIT": "automatic",
        "ACTION-REVERSE-SPLIT": (
            "automatic_with_cash_in_lieu_pending_if_fraction_disallowed"
        ),
        "ACTION-CASH-DIVIDEND": "automatic",
        "ACTION-TICKER-NAME-CHANGE": "automatic_identity_alias",
        "ACTION-CASH-MERGER": "pending_manual",
        "ACTION-STOCK-MERGER": "pending_manual",
        "ACTION-SPINOFF": "pending_manual",
        "ACTION-CASH-IN-LIEU": "pending_manual",
        "ACTION-DELISTING-BANKRUPTCY": "pending_manual",
        "ACTION-CORRECTION-REVERSAL": "compensating_event_only",
    }
    expected_action_semantics = {
        "ACTION-SPLIT": {
            "terminal_state": "applied",
            "quantity_rule": "multiply_ratio_then_quantize_quantity",
            "per_share_cost_rule": "divide_ratio_then_quantize_price",
            "total_cost_rule": "conserve_subject_only_to_declared_quantization",
            "cash_rule": "unchanged",
            "replay_rule": "idempotency_key_applies_once",
        },
        "ACTION-REVERSE-SPLIT": {
            "terminal_state": "applied_or_action_pending_manual",
            "quantity_rule": "multiply_ratio_then_quantize_quantity",
            "per_share_cost_rule": "divide_ratio_then_quantize_price",
            "total_cost_rule": "conserve_subject_only_to_declared_quantization",
            "fraction_rule": "unresolved_cash_in_lieu_freezes_affected_security",
            "replay_rule": "idempotency_key_applies_once",
        },
        "ACTION-CASH-DIVIDEND": {
            "terminal_state": "applied",
            "cash_rule": (
                "add_eligible_quantity_times_cash_per_share_quantized_money"
            ),
            "quantity_rule": "unchanged",
            "date_rule": "ex_date_and_pay_date_are_distinct",
            "replay_rule": "idempotency_key_applies_once",
        },
        "ACTION-TICKER-NAME-CHANGE": {
            "terminal_state": "applied",
            "stable_security_id_rule": "unchanged",
            "old_symbol_rule": "close_validity_interval",
            "new_symbol_rule": "open_validity_interval",
            "replay_rule": "idempotency_key_applies_once",
        },
        "ACTION-CASH-MERGER": {
            "terminal_state": "action_pending_manual",
            "automatic_transform_rule": "forbidden",
            "cash_rule": "no_guessed_amount",
            "affected_security_rule": "frozen",
            "nav_rule": "incomplete",
            "risk_rule": "new_approval_blocked",
        },
        "ACTION-STOCK-MERGER": {
            "terminal_state": "action_pending_manual",
            "automatic_transform_rule": "forbidden",
            "quantity_rule": "no_guessed_quantity",
            "cost_rule": "no_guessed_basis",
            "affected_security_rule": "frozen",
            "nav_rule": "incomplete",
            "risk_rule": "new_approval_blocked",
        },
        "ACTION-SPINOFF": {
            "terminal_state": "action_pending_manual",
            "automatic_transform_rule": "forbidden",
            "quantity_rule": "no_guessed_quantity",
            "cost_rule": "no_guessed_basis_allocation",
            "affected_security_rule": "frozen",
            "nav_rule": "incomplete",
            "risk_rule": "new_approval_blocked",
        },
        "ACTION-CASH-IN-LIEU": {
            "terminal_state": "action_pending_manual",
            "automatic_transform_rule": "forbidden",
            "cash_rule": "no_guessed_amount",
            "reconciliation_rule": "open",
            "affected_security_rule": "frozen",
            "nav_rule": "incomplete",
        },
        "ACTION-DELISTING-BANKRUPTCY": {
            "terminal_state": "action_pending_manual",
            "automatic_transform_rule": "forbidden",
            "mark_rule": "never_silently_zero",
            "resolution_rule": (
                "explicit_evidence_and_compensating_event_required"
            ),
            "nav_rule": "incomplete",
            "risk_rule": "new_approval_blocked",
        },
        "ACTION-CORRECTION-REVERSAL": {
            "terminal_state": "corrected_by_compensation",
            "original_event_rule": "immutable",
            "revision_rule": "linked_revision_required",
            "account_rule": "append_compensating_event",
            "replay_rule": "rebuild_from_original_plus_compensation",
        },
    }
    verify_bound_items(
        actions,
        "money corporate actions",
        expected_action_ids,
        "v1_mode",
        requirement_ids,
        verification_ids,
        case_ids,
        errors,
    )
    if isinstance(actions, list):
        for action in actions:
            if not isinstance(action, dict):
                continue
            action_id = action.get("id", "<unknown>")
            if action.get("v1_mode") != expected_action_modes.get(action_id):
                errors.append(f"{action_id} corporate action mode differs")
            if action.get("semantics") != expected_action_semantics.get(action_id):
                errors.append(f"{action_id} corporate action semantics differ")
            if "effect" in action:
                errors.append(f"{action_id} uses free-text corporate action effect")
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
    expected_calendar = {
        "calendar": (
            "explicit exchange session table with timezone; "
            "data-row intersection is never a calendar"
        ),
        "decision_bar_rule": (
            "a close-derived signal at session T is available only after that close"
        ),
        "earliest_default_fill": (
            "next eligible session T+1 using the preregistered fill-price model"
        ),
        "same_bar_fill": (
            "forbidden unless the signal was provably available before the chosen "
            "executable price and the alternate timing was preregistered"
        ),
        "missing_session_rule": (
            "report coverage and fail the run when required strategy/benchmark "
            "sessions differ; never hide via zip or intersection"
        ),
    }
    if calendar != expected_calendar:
        errors.append("market calendar and causality semantics differ")
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
                evidence_path = subject.get("evidence_path")
                if evidence_path is not None:
                    if (
                        not isinstance(evidence_path, str)
                        or Path(evidence_path).is_absolute()
                        or ".." in Path(evidence_path).parts
                        or not (PROJECT_ROOT / evidence_path).is_file()
                    ):
                        errors.append(
                            f"{subject_id} design reviewer evidence path is invalid"
                        )
                    else:
                        evidence_hash = subject.get("evidence_sha256")
                        if (
                            not isinstance(evidence_hash, str)
                            or not re.fullmatch(r"[0-9a-f]{64}", evidence_hash)
                            or sha256(PROJECT_ROOT / evidence_path) != evidence_hash
                        ):
                            errors.append(
                                f"{subject_id} design reviewer evidence sha256 mismatch"
                            )
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
    expected_final_review_schema = {
        "schema_version": 2,
        "additional_fields_allowed": False,
        "required": [
            "schema_version",
            "subject_id",
            "review_locator",
            "assurance_level",
            "review_input",
            "review_input_sha256",
            "review_output_path",
            "review_output_sha256",
            "candidate_commit",
            "candidate_tree",
            "ground_truth_manifest_path",
            "ground_truth_manifest_sha256",
            "machine_assurance_manifest_path",
            "machine_assurance_manifest_sha256",
            "machine_attestation_verification_path",
            "machine_attestation_verification_sha256",
            "verdict",
            "open_critical_count",
            "open_major_count",
            "open_minor_count",
            "new_architecture_changing_classes",
            "participated_in_candidate_construction",
            "write_access_used",
            "reviewed_files",
            "commands_run",
            "canonical_attacks",
            "novelty_probes",
            "findings",
            "finding_ids",
            "what_would_falsify_pass",
            "limitations",
        ],
        "required_canonical_attacks": [
            {"attack_id": attack_id}
            for attack_id in FINAL_REVIEW_ATTACK_IDS
        ],
        "canonical_attack_required": [
            "attack_id",
            "runner_receipt_path",
            "runner_receipt_sha256",
        ],
        "novelty_probe_required": [
            "probe_id",
            "spec_path",
            "spec_sha256",
            "runner_receipt_path",
            "runner_receipt_sha256",
        ],
        "runner_receipt_required": [
            "schema_version",
            "runner_id",
            "runner_sha256",
            "candidate_commit",
            "candidate_tree",
            "project_prefix",
            "mode",
            "probe_id",
            "mutation_spec_sha256",
            "mutation_observation",
            "baseline",
            "target",
            "expected_rejection_substring",
            "result",
            "runner_exit_code",
            "started_at",
            "completed_at",
            "execution_fingerprint",
        ],
        "passing_rule": (
            "候选 commit/tree、平台可观察审查输入输出、完整 ground truth、GitHub 签名机器 manifest、"
            "finding 计数、四个 canonical attack 和至少一个候选固定后新增 novelty probe 必须一致；"
            "冻结 runner 会重新执行每项 mutation，并同时核对实际 runner process exit、"
            "未变异 baseline exit=0、mutated target exit!=0、目标错误信号和 receipt fingerprint。"
            "任意 command 字符串或内部自洽哈希不能单独成为执行证据；任一遗漏、escaped、"
            "跨候选复用、open finding 或缺失外部 provenance 都保持 blocked_freeze。"
        ),
    }
    if subjects_doc.get("final_review_evidence_schema") != (
        expected_final_review_schema
    ):
        errors.append("assurance final review evidence schema differs")


def verify_final_review_evidence(
    evidence: dict[str, Any],
    *,
    round_id: str,
    reviewers: Any,
    candidate_commit: Any,
    candidate_tree: Any,
    frozen_files: Any,
    implementation_targets: Any,
    errors: list[str],
) -> None:
    required_fields = {
        "schema_version",
        "subject_id",
        "review_locator",
        "assurance_level",
        "review_input",
        "review_input_sha256",
        "review_output_path",
        "review_output_sha256",
        "candidate_commit",
        "candidate_tree",
        "ground_truth_manifest_path",
        "ground_truth_manifest_sha256",
        "machine_assurance_manifest_path",
        "machine_assurance_manifest_sha256",
        "machine_attestation_verification_path",
        "machine_attestation_verification_sha256",
        "verdict",
        "open_critical_count",
        "open_major_count",
        "open_minor_count",
        "new_architecture_changing_classes",
        "participated_in_candidate_construction",
        "write_access_used",
        "reviewed_files",
        "commands_run",
        "canonical_attacks",
        "novelty_probes",
        "findings",
        "finding_ids",
        "what_would_falsify_pass",
        "limitations",
    }
    missing = required_fields - set(evidence)
    if missing:
        errors.append(
            f"{round_id} passing review evidence missing fields: {sorted(missing)}"
        )
    unexpected = set(evidence) - required_fields
    if unexpected:
        errors.append(
            f"{round_id} passing review evidence has unexpected fields: "
            f"{sorted(unexpected)}"
        )
    if evidence.get("schema_version") != 2:
        errors.append(f"{round_id} passing review evidence schema differs")
    reviewer_set = set(reviewers) if isinstance(reviewers, list) else set()
    if evidence.get("subject_id") not in reviewer_set:
        errors.append(f"{round_id} passing review evidence subject differs")
    review_input = evidence.get("review_input")
    if (
        not isinstance(evidence.get("review_locator"), str)
        or not evidence.get("review_locator")
        or not isinstance(review_input, str)
        or not review_input
        or evidence.get("review_input_sha256") != sha256_text(review_input)
    ):
        errors.append(f"{round_id} passing review provenance is incomplete")
    verify_bound_project_file(
        evidence,
        path_field="review_output_path",
        hash_field="review_output_sha256",
        required_path=None,
        prefix="audits/",
        label=f"{round_id} review output",
        errors=errors,
    )
    ground_truth_path = verify_bound_project_file(
        evidence,
        path_field="ground_truth_manifest_path",
        hash_field="ground_truth_manifest_sha256",
        required_path="governance/GROUND_TRUTH_MANIFEST_V1.json",
        prefix="governance/",
        label=f"{round_id} ground-truth manifest",
        errors=errors,
    )
    machine_manifest_path = verify_bound_project_file(
        evidence,
        path_field="machine_assurance_manifest_path",
        hash_field="machine_assurance_manifest_sha256",
        required_path=None,
        prefix="evidence/ci/",
        label=f"{round_id} machine-assurance manifest",
        errors=errors,
    )
    verify_bound_project_file(
        evidence,
        path_field="machine_attestation_verification_path",
        hash_field="machine_attestation_verification_sha256",
        required_path=None,
        prefix="evidence/ci/",
        label=f"{round_id} machine-attestation verification",
        errors=errors,
    )
    if machine_manifest_path is not None:
        machine_manifest = load_json(machine_manifest_path, errors)
        expected_machine_binding = {
            "schema_version": 1,
            "manifest_id": "ids-github-machine-assurance-v1",
            "status": "pass",
            "assurance_level": "github_issued_workflow_provenance",
            "semantic_approval": False,
            "repository": "j-a-v-e-n/knowledge-vault",
            "candidate_commit": candidate_commit,
            "candidate_tree": candidate_tree,
        }
        for key, expected in expected_machine_binding.items():
            if machine_manifest.get(key) != expected:
                errors.append(
                    f"{round_id} machine-assurance manifest {key} differs"
                )

    expected_evidence = {
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "assurance_level": "platform_observable_separate_thread_review",
        "verdict": "passed_freeze",
        "new_architecture_changing_classes": [],
        "participated_in_candidate_construction": False,
        "write_access_used": False,
    }
    for key, expected in expected_evidence.items():
        if evidence.get(key) != expected:
            errors.append(f"{round_id} passing review evidence {key} differs")

    reviewed_files = evidence.get("reviewed_files")
    if not nonempty_unique_strings(reviewed_files):
        errors.append(f"{round_id} passing review evidence reviewed_files differs")
    else:
        required_scope = set(FINAL_REVIEW_REQUIRED_SCOPE)
        if ground_truth_path is not None:
            ground_truth = load_json(ground_truth_path, errors)
            artifacts = ground_truth.get("artifacts")
            if not isinstance(artifacts, list) or not artifacts:
                errors.append(
                    f"{round_id} ground-truth manifest artifacts must be nonempty"
                )
            else:
                for index, artifact in enumerate(artifacts):
                    if not isinstance(artifact, dict):
                        errors.append(
                            f"{round_id} ground-truth artifacts[{index}] is invalid"
                        )
                        continue
                    if artifact.get("required") is not True:
                        continue
                    relative = artifact.get("path")
                    scope = artifact.get("scope", "project")
                    if not isinstance(relative, str) or not relative:
                        errors.append(
                            f"{round_id} ground-truth artifacts[{index}] path differs"
                        )
                        continue
                    required_scope.add(
                        f"{REPOSITORY_SCOPE_PREFIX}{relative}"
                        if scope == "repository"
                        else relative
                    )
        if isinstance(frozen_files, list):
            required_scope.update(
                item for item in frozen_files if isinstance(item, str)
            )
        targets = (
            implementation_targets.get("targets")
            if isinstance(implementation_targets, dict)
            else None
        )
        if isinstance(targets, list):
            project_prefix = run_git(["rev-parse", "--show-prefix"], errors)
            candidate_is_resolvable = isinstance(
                candidate_commit, str
            ) and bool(re.fullmatch(r"[0-9a-f]{40}", candidate_commit))
            for target in targets:
                if (
                    not isinstance(target, dict)
                    or target.get("required_by") != "design_freeze"
                ):
                    continue
                relative = target.get("path")
                kind = target.get("kind")
                if not isinstance(relative, str) or not relative:
                    continue
                if kind == "file":
                    required_scope.add(relative)
                    continue
                if kind != "directory" or not candidate_is_resolvable:
                    continue
                listing = run_git(
                    [
                        "ls-tree",
                        "-r",
                        "--full-tree",
                        "--name-only",
                        candidate_commit,
                        "--",
                        f":(top,literal){project_prefix}{relative}",
                    ],
                    errors,
                )
                prefix_length = len(project_prefix)
                directory_files = {
                    item[prefix_length:]
                    for item in listing.splitlines()
                    if item.startswith(project_prefix)
                    and item[prefix_length:].startswith(relative)
                }
                if not directory_files:
                    errors.append(
                        f"{round_id} passing review design-freeze directory "
                        f"is empty in candidate: {relative}"
                    )
                required_scope.update(directory_files)
        omitted = required_scope - set(reviewed_files)
        if omitted:
            errors.append(
                f"{round_id} passing review omitted required files: "
                f"{sorted(omitted)}"
            )
        project_prefix = run_git(["rev-parse", "--show-prefix"], errors)
        can_resolve_reviewed_files = isinstance(
            candidate_commit, str
        ) and bool(re.fullmatch(r"[0-9a-f]{40}", candidate_commit))
        for relative in reviewed_files:
            repo_relative = review_reference_repo_path(
                relative,
                project_prefix=project_prefix,
            )
            if repo_relative is None:
                errors.append(
                    f"{round_id} passing review has unsafe reviewed file: {relative}"
                )
                continue
            if not can_resolve_reviewed_files:
                continue
            tree_entry = run_git(
                [
                    "ls-tree",
                    "--full-tree",
                    candidate_commit,
                    "--",
                    f":(top,literal){repo_relative}",
                ],
                errors,
            )
            fields = tree_entry.split()
            if len(fields) < 3 or fields[1] != "blob":
                errors.append(
                    f"{round_id} passing review file is absent from candidate: "
                    f"{relative}"
                )

    commands_run = evidence.get("commands_run")
    if not nonempty_unique_strings(commands_run):
        errors.append(
            f"{round_id} passing review commands_run must be nonempty and unique"
        )
        commands: set[str] = set()
    else:
        commands = set(commands_run)
    required_commands = {
        (
            "PYTHON scripts/run_design_freeze_attack.py "
            f"--candidate-commit {candidate_commit} --attack-id {attack_id}"
        )
        for attack_id in FINAL_REVIEW_ATTACK_IDS
    }
    if not required_commands.issubset(commands):
        errors.append(
            f"{round_id} passing review omitted canonical replay commands: "
            f"{sorted(required_commands - commands)}"
        )

    for field in ("what_would_falsify_pass", "limitations"):
        if not nonempty_unique_strings(evidence.get(field)):
            errors.append(
                f"{round_id} passing review {field} must be nonempty and unique"
            )

    findings = evidence.get("findings")
    finding_ids = evidence.get("finding_ids")
    if (
        not isinstance(finding_ids, list)
        or not all(isinstance(item, str) and item for item in finding_ids)
        or len(finding_ids) != len(set(finding_ids))
    ):
        errors.append(f"{round_id} passing review finding_ids differs")
        declared_finding_ids: set[str] = set()
    else:
        declared_finding_ids = set(finding_ids)
    observed_finding_ids: set[str] = set()
    open_counts = {"critical": 0, "major": 0, "minor": 0}
    if not isinstance(findings, list):
        errors.append(f"{round_id} passing review findings must be a list")
    else:
        for index, finding in enumerate(findings):
            label = f"{round_id} passing review findings[{index}]"
            if not isinstance(finding, dict):
                errors.append(f"{label} must be an object")
                continue
            finding_id = finding.get("id")
            severity = finding.get("severity")
            status = finding.get("status")
            if (
                not isinstance(finding_id, str)
                or not finding_id
                or finding_id in observed_finding_ids
            ):
                errors.append(f"{label} id is invalid or duplicate")
            else:
                observed_finding_ids.add(finding_id)
            if severity not in open_counts:
                errors.append(f"{label} severity differs")
            if status not in {"open", "resolved"}:
                errors.append(f"{label} status differs")
            if not isinstance(finding.get("title"), str) or not finding.get("title"):
                errors.append(f"{label} title is missing")
            if not isinstance(finding.get("evidence"), str) or not finding.get(
                "evidence"
            ):
                errors.append(f"{label} evidence is missing")
            if severity in open_counts and status == "open":
                open_counts[severity] += 1
    if declared_finding_ids != observed_finding_ids:
        errors.append(f"{round_id} passing review finding_ids/findings differ")
    for severity in ("critical", "major", "minor"):
        field = f"open_{severity}_count"
        if evidence.get(field) != open_counts[severity]:
            errors.append(f"{round_id} passing review evidence {field} differs")
    if any(open_counts.values()):
        errors.append(f"{round_id} passed with open review findings")

    project_prefix = run_git(["rev-parse", "--show-prefix"], errors)
    canonical_attacks = evidence.get("canonical_attacks")
    attack_ids: set[str] = set()
    receipt_paths: set[str] = set()
    if not isinstance(canonical_attacks, list):
        errors.append(f"{round_id} passing review canonical_attacks must be a list")
    else:
        for index, attack in enumerate(canonical_attacks):
            label = f"{round_id} canonical_attacks[{index}]"
            if not isinstance(attack, dict) or set(attack) != {
                "attack_id",
                "runner_receipt_path",
                "runner_receipt_sha256",
            }:
                errors.append(f"{label} fields differ")
                continue
            attack_id = attack.get("attack_id")
            if (
                not isinstance(attack_id, str)
                or attack_id in attack_ids
                or attack_id not in FINAL_REVIEW_ATTACK_IDS
            ):
                errors.append(f"{label} attack_id is invalid or duplicate")
                continue
            attack_ids.add(attack_id)
            receipt_relative = attack.get("runner_receipt_path")
            receipt_path = safe_relative_file(
                receipt_relative,
                prefix="audits/final_review_attacks/",
            )
            receipt_hash = attack.get("runner_receipt_sha256")
            if (
                receipt_path is None
                or receipt_relative in receipt_paths
                or not isinstance(receipt_hash, str)
                or re.fullmatch(r"[0-9a-f]{64}", receipt_hash) is None
            ):
                errors.append(f"{label} runner receipt binding is invalid")
                continue
            receipt_paths.add(receipt_relative)
            if sha256(receipt_path) != receipt_hash:
                errors.append(f"{label} runner receipt sha256 mismatch")
                continue
            receipt = load_json(receipt_path, errors)
            verify_runner_receipt_shape(
                receipt,
                candidate_commit=candidate_commit,
                candidate_tree=candidate_tree,
                mode="canonical",
                probe_id=attack_id,
                label=label,
                errors=errors,
            )
            if isinstance(candidate_commit, str):
                reexecute_runner_receipt(
                    candidate_commit=candidate_commit,
                    attack_id=attack_id,
                    novelty_spec=None,
                    expected_fingerprint=receipt.get("execution_fingerprint"),
                    label=label,
                    errors=errors,
                )

    required_attack_ids = set(FINAL_REVIEW_ATTACK_IDS)
    if attack_ids != required_attack_ids:
        errors.append(
            f"{round_id} passing review attack coverage differs: "
            f"missing={sorted(required_attack_ids - attack_ids)}, "
            f"extra={sorted(attack_ids - required_attack_ids)}"
        )

    novelty_probes = evidence.get("novelty_probes")
    probe_ids: set[str] = set()
    if not isinstance(novelty_probes, list) or not novelty_probes:
        errors.append(
            f"{round_id} passing review requires at least one novelty probe"
        )
    else:
        for index, probe in enumerate(novelty_probes):
            label = f"{round_id} novelty_probes[{index}]"
            if not isinstance(probe, dict) or set(probe) != {
                "probe_id",
                "spec_path",
                "spec_sha256",
                "runner_receipt_path",
                "runner_receipt_sha256",
            }:
                errors.append(f"{label} fields differ")
                continue
            probe_id = probe.get("probe_id")
            if (
                not isinstance(probe_id, str)
                or re.fullmatch(r"PROBE-[A-Z0-9][A-Z0-9-]{2,80}", probe_id)
                is None
                or probe_id in probe_ids
            ):
                errors.append(f"{label} probe_id is invalid or duplicate")
                continue
            probe_ids.add(probe_id)
            spec_relative = probe.get("spec_path")
            spec_path = safe_relative_file(
                spec_relative,
                prefix="audits/final_review_probes/",
            )
            spec_hash = probe.get("spec_sha256")
            if (
                spec_path is None
                or not isinstance(spec_hash, str)
                or re.fullmatch(r"[0-9a-f]{64}", spec_hash) is None
                or sha256(spec_path) != spec_hash
            ):
                errors.append(f"{label} novelty spec binding differs")
                continue
            spec = load_json(spec_path, errors)
            canonical_spec_hash = hashlib.sha256(
                json.dumps(
                    spec,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if spec.get("probe_id") != probe_id:
                errors.append(f"{label} novelty spec probe_id differs")
            if isinstance(candidate_commit, str):
                candidate_spec = subprocess.run(
                    [
                        "git",
                        "cat-file",
                        "-e",
                        f"{candidate_commit}:{project_prefix}{spec_relative}",
                    ],
                    cwd=PROJECT_ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if candidate_spec.returncode == 0:
                    errors.append(
                        f"{label} novelty spec existed in the reviewed candidate"
                    )

            receipt_relative = probe.get("runner_receipt_path")
            receipt_path = safe_relative_file(
                receipt_relative,
                prefix="audits/final_review_attacks/",
            )
            receipt_hash = probe.get("runner_receipt_sha256")
            if (
                receipt_path is None
                or receipt_relative in receipt_paths
                or not isinstance(receipt_hash, str)
                or re.fullmatch(r"[0-9a-f]{64}", receipt_hash) is None
                or sha256(receipt_path) != receipt_hash
            ):
                errors.append(f"{label} runner receipt binding differs")
                continue
            receipt_paths.add(receipt_relative)
            receipt = load_json(receipt_path, errors)
            verify_runner_receipt_shape(
                receipt,
                candidate_commit=candidate_commit,
                candidate_tree=candidate_tree,
                mode="novelty",
                probe_id=probe_id,
                label=label,
                errors=errors,
            )
            if receipt.get("mutation_spec_sha256") != canonical_spec_hash:
                errors.append(f"{label} receipt/spec semantic hash differs")
            if isinstance(candidate_commit, str):
                reexecute_runner_receipt(
                    candidate_commit=candidate_commit,
                    attack_id=None,
                    novelty_spec=spec_path,
                    expected_fingerprint=receipt.get("execution_fingerprint"),
                    label=label,
                    errors=errors,
                )


def verify_research_register(
    research: dict[str, Any],
    research_sufficiency: dict[str, Any],
    contract: dict[str, Any],
    implementation_targets: dict[str, Any],
    allow_candidate: bool,
    errors: list[str],
) -> None:
    expected_source_classes = {
        "official_vendor_engineering",
        "standards_and_public_handbooks",
        "peer_reviewed_or_preprint_research",
        "benchmarks_and_reproducible_experiments",
        "open_source_code_and_issue_trackers",
        "ordinary_user_experience",
        "critical_and_negative_cases",
        "current_project_adversarial_experiments",
    }
    if set(research.get("required_source_classes", [])) != expected_source_classes:
        errors.append("research source class boundary differs")

    coverage = research.get("coverage")
    coverage_ids = unique_ids(coverage, "research coverage", errors)
    expected_coverage_ids = {f"RC-{index:02d}" for index in range(1, 23)}
    if coverage_ids != expected_coverage_ids:
        errors.append(
            "research coverage ids differ: "
            f"missing={sorted(expected_coverage_ids - coverage_ids)}, "
            f"extra={sorted(coverage_ids - expected_coverage_ids)}"
        )
    if isinstance(coverage, list):
        for item in coverage:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id", "<unknown>")
            if item.get("impact") != "high":
                errors.append(f"{item_id} research impact differs")
            if item.get("status") not in {"supported", "contested"}:
                errors.append(f"{item_id} research status differs")

    search_log = research.get("search_log")
    if not isinstance(search_log, list) or not search_log:
        errors.append("research search_log must be nonempty")
    else:
        for index, item in enumerate(search_log):
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("date"), str)
                or not isinstance(item.get("channel"), str)
                or not isinstance(item.get("query"), str)
                or not item.get("query")
            ):
                errors.append(f"research search_log[{index}] is incomplete")

    artifacts = research.get("primary_artifacts")
    artifact_ids = unique_ids(artifacts, "research primary artifacts", errors)
    core_artifact_ids = {
        "ARTIFACT-AI-FAILURE-TAXONOMY",
        "ARTIFACT-AI-METHOD-REFRESH",
        "ARTIFACT-EXISTING-SYSTEM-AUDIT",
        "ARTIFACT-VIBE-TRADING-REVIEW",
        "ARTIFACT-DATA-PAPER-BOUNDARY",
        "ARTIFACT-CHALLENGE-R2",
        "ARTIFACT-CHALLENGE-R2B",
        "ARTIFACT-CHALLENGE-R3",
        "ARTIFACT-CHALLENGE-R3B",
        "ARTIFACT-CHALLENGE-R4",
        "ARTIFACT-ASSURANCE-PROVENANCE-REFRESH",
        "ARTIFACT-CHALLENGE-R6",
        "ARTIFACT-PRODUCT-ASSURANCE-BLUEPRINT",
    }
    missing_core_artifacts = core_artifact_ids - artifact_ids
    if missing_core_artifacts:
        errors.append(
            "research primary artifact ids differ: "
            f"missing={sorted(missing_core_artifacts)}, "
            "extra=[]"
        )
    artifact_paths: set[str] = set()
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                continue
            artifact_id = artifact.get("id", "<unknown>")
            if not isinstance(artifact_id, str) or not re.fullmatch(
                r"ARTIFACT-[A-Z0-9-]+", artifact_id
            ):
                errors.append(f"{artifact_id} research artifact id is invalid")
            relative = artifact.get("path")
            expected_hash = artifact.get("sha256")
            if (
                not isinstance(relative, str)
                or Path(relative).is_absolute()
                or ".." in Path(relative).parts
            ):
                errors.append(f"{artifact_id} research artifact has unsafe path")
                continue
            if relative in artifact_paths:
                errors.append(f"duplicate research primary artifact path: {relative}")
            artifact_paths.add(relative)
            path = PROJECT_ROOT / relative
            if not path.is_file():
                errors.append(f"research primary artifact is missing: {relative}")
            elif (
                not isinstance(expected_hash, str)
                or not re.fullmatch(r"[0-9a-f]{64}", expected_hash)
                or sha256(path) != expected_hash
            ):
                errors.append(f"{artifact_id} research artifact sha256 mismatch")
            if not allow_candidate and path.is_file():
                repo_prefix = run_git(["rev-parse", "--show-prefix"], errors)
                repo_relative = f"{repo_prefix}{relative}"
                tracked = subprocess.run(
                    [
                        "git",
                        "ls-files",
                        "--error-unmatch",
                        "--",
                        f":(top){repo_relative}",
                    ],
                    cwd=PROJECT_ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                at_head = subprocess.run(
                    ["git", "cat-file", "-e", f"HEAD:{repo_relative}"],
                    cwd=PROJECT_ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if tracked.returncode != 0 or at_head.returncode != 0:
                    errors.append(
                        f"{artifact_id} frozen research artifact is not tracked in HEAD"
                    )
            role = artifact.get("role")
            if not isinstance(role, str) or not role:
                errors.append(f"{artifact_id} research artifact role is missing")
            final_id = bool(
                isinstance(artifact_id, str)
                and re.fullmatch(
                    r"ARTIFACT-CHALLENGE-FINAL-R[0-9]+", artifact_id
                )
            )
            final_role = role == "independent_final_challenge"
            if final_id or final_role:
                errors.append(
                    f"{artifact_id} post-candidate final review evidence must not "
                    "be a candidate primary artifact"
                )

    challenge = research.get("challenge")
    if not isinstance(challenge, dict):
        errors.append("research challenge must be an object")
        return
    challenge_status = challenge.get("status")
    if challenge_status not in {"in_progress", "completed"}:
        errors.append("research challenge status differs")
    rounds = challenge.get("rounds")
    round_ids = unique_ids(rounds, "research challenge rounds", errors)
    del round_ids
    if not isinstance(rounds, list) or not rounds:
        errors.append("research challenge rounds must be nonempty")
        return
    for challenge_round in rounds:
        if not isinstance(challenge_round, dict):
            continue
        round_id = challenge_round.get("id", "<unknown>")
        reviewers = challenge_round.get("reviewer_subjects")
        if (
            not isinstance(reviewers, list)
            or not reviewers
            or not all(isinstance(item, str) for item in reviewers)
        ):
            errors.append(f"{round_id} has no reviewer subjects")
        result = challenge_round.get("result")
        if result not in {"blocked_freeze", "passed_freeze"}:
            errors.append(f"{round_id} challenge result differs")
        for key in ("candidate_commit", "candidate_tree"):
            value = challenge_round.get(key)
            if value is not None and (
                not isinstance(value, str)
                or not re.fullmatch(r"[0-9a-f]{40}", value)
            ):
                errors.append(f"{round_id} {key} is not a full Git object id")
        evidence_path = challenge_round.get("evidence_path")
        if evidence_path is not None:
            if (
                not isinstance(evidence_path, str)
                or Path(evidence_path).is_absolute()
                or ".." in Path(evidence_path).parts
                or not (PROJECT_ROOT / evidence_path).is_file()
            ):
                errors.append(f"{round_id} challenge evidence path is invalid")
            else:
                evidence_sha256 = challenge_round.get("evidence_sha256")
                if (
                    not isinstance(evidence_sha256, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", evidence_sha256)
                    or sha256(PROJECT_ROOT / evidence_path) != evidence_sha256
                ):
                    errors.append(f"{round_id} challenge evidence sha256 mismatch")
        new_classes = challenge_round.get("new_architecture_changing_classes")
        if not isinstance(new_classes, list) or not all(
            isinstance(item, str) for item in new_classes
        ):
            errors.append(f"{round_id} new architecture class list differs")
        if result == "passed_freeze":
            candidate_commit = challenge_round.get("candidate_commit")
            candidate_tree = challenge_round.get("candidate_tree")
            if not isinstance(candidate_commit, str) or not re.fullmatch(
                r"[0-9a-f]{40}", candidate_commit
            ):
                errors.append(f"{round_id} passing round lacks candidate_commit")
            if not isinstance(candidate_tree, str) or not re.fullmatch(
                r"[0-9a-f]{40}", candidate_tree
            ):
                errors.append(f"{round_id} passing round lacks candidate_tree")
            if new_classes:
                errors.append(f"{round_id} passed while adding architecture classes")
            if challenge_round.get("open_critical_count") != 0:
                errors.append(f"{round_id} passed with open critical findings")
            if challenge_round.get("open_major_count") != 0:
                errors.append(f"{round_id} passed with open major findings")
            if not isinstance(evidence_path, str) or not evidence_path.endswith(".json"):
                errors.append(
                    f"{round_id} passing review evidence must be machine-readable JSON"
                )
            elif (PROJECT_ROOT / evidence_path).is_file():
                evidence = load_json(PROJECT_ROOT / evidence_path, errors)
                frozen_files = contract.get("change_control", {}).get("frozen_files")
                verify_final_review_evidence(
                    evidence,
                    round_id=round_id,
                    reviewers=reviewers,
                    candidate_commit=candidate_commit,
                    candidate_tree=candidate_tree,
                    frozen_files=frozen_files,
                    implementation_targets=implementation_targets,
                    errors=errors,
                )
                if (
                    challenge_round.get("open_minor_count")
                    != evidence.get("open_minor_count")
                ):
                    errors.append(
                        f"{round_id} passing review round open_minor_count differs"
                    )
                if challenge_round.get("finding_ids") != evidence.get("finding_ids"):
                    errors.append(
                        f"{round_id} passing review round finding_ids differs"
                    )
                resolved_tree = run_git(
                    ["rev-parse", f"{candidate_commit}^{{tree}}"], errors
                )
                if resolved_tree and resolved_tree != candidate_tree:
                    errors.append(
                        f"{round_id} passing review candidate tree differs"
                    )

    stop_rule = research.get("stop_rule")
    expected_stop_rule = {
        "method": "derived_not_declared",
        "receipt_path": "governance/RESEARCH_SUFFICIENCY_V1.json",
        "derived_field": "derived_pre_review_eligible",
        "required": (
            "RESEARCH_SUFFICIENCY_V1 的冻结 derivation_rules 必须从检索预算、纳入/排除、来源簇、"
            "claim entailment、矛盾、补充轮和 architecture/decision delta 推导 pre-review eligibility；"
            "最终关闭还必须与外部签名机器执行、候选固定后的独立语义挑战、novelty probe "
            "和零未关闭 finding 共同成立。任何自由布尔值均不构成停止证据。"
        ),
    }
    if stop_rule != expected_stop_rule:
        errors.append("research stop rule is not derived from sufficiency receipt")
    pre_review_eligible = (
        research_sufficiency.get("derived_pre_review_eligible") is True
    )
    last_result = rounds[-1].get("result") if isinstance(rounds[-1], dict) else None
    if challenge_status == "completed":
        if not pre_review_eligible or last_result != "passed_freeze":
            errors.append(
                "completed research challenge lacks derived eligibility or a passing final round"
            )
    if not allow_candidate and (
        challenge_status != "completed"
        or not pre_review_eligible
        or last_result != "passed_freeze"
    ):
        errors.append("frozen research has no valid completed challenge")
    if last_result == "passed_freeze" and isinstance(rounds[-1], dict):
        final_round = rounds[-1]
        if final_round.get("evidence_path") in artifact_paths:
            errors.append(
                "passing final challenge evidence is circularly registered as a "
                "candidate primary artifact"
            )


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
    expected_conditional_evidence_schema = {
        "schema_version": 2,
        "required": [
            "schema_version",
            "condition_id",
            "gate_id",
            "gate_stage",
            "state",
            "candidate_commit",
            "candidate_tree",
            "frozen_bundle_path",
            "frozen_bundle_sha256",
            "run_id",
            "producer_id",
            "executor_ids",
            "acceptance_case_ids",
            "observation",
            "run_receipt",
            "raw_result_path",
            "raw_result_sha256",
            "completed_at",
        ],
        "additional_fields_allowed": False,
        "state_enum": ["passed", "failed", "inconclusive"],
        "identity_authority": {
            "candidate_commit": "project_root_git_head",
            "candidate_tree": "project_root_git_head_tree",
            "frozen_bundle_path": "governance/FROZEN_BUNDLE_V1.json",
            "frozen_bundle_sha256": "sha256_file_bytes",
            "cli_and_evidence_role": "expected_values_only",
        },
        "observation_schema": {
            "required": [
                "authority",
                "condition_id",
                "source_event_seq",
                "source_event_hash",
                "source_state_hash",
                "source_anchor_hash",
                "observed_at",
            ],
            "additional_fields_allowed": False,
            "runtime_event_seq_minimum": 1,
            "environment_presence_event_seq": 0,
        },
        "run_receipt_schema": {
            "required": [
                "authority",
                "run_event_seq",
                "run_event_hash",
                "run_anchor_hash",
                "run_id",
                "condition_id",
                "gate_id",
                "gate_stage",
                "state",
                "source_event_seq",
                "source_event_hash",
                "source_state_hash",
                "source_anchor_hash",
                "raw_result_path",
                "raw_result_sha256",
                "completed_at",
            ],
            "additional_fields_allowed": False,
            "authority": "runtime_sqlite_gate_run_receipt",
            "runtime_event_seq_minimum": 1,
        },
        "raw_result_schema": {
            "schema_version": 1,
            "required": [
                "schema_version",
                "condition_id",
                "gate_id",
                "gate_stage",
                "state",
                "candidate_commit",
                "candidate_tree",
                "frozen_bundle_path",
                "frozen_bundle_sha256",
                "run_id",
                "producer_id",
                "executor_ids",
                "acceptance_case_ids",
                "observation",
                "started_at",
                "completed_at",
                "status",
                "actual_cases_run",
                "case_results",
            ],
            "additional_fields_allowed": False,
            "required_status": "pass",
        },
        "case_result_schema": {
            "required": [
                "case_id",
                "status",
                "input_hashes",
                "raw_result_hashes",
            ],
            "additional_fields_allowed": False,
            "required_status": "pass",
            "hash_algorithm": "sha256",
        },
        "runtime_authority": {
            "production_config_path": (
                "~/Library/Application Support/InvestmentDisciplineSystem/"
                "runtime-authority.json"
            ),
            "config_schema_version": 1,
            "runtime_database_relative_path": "runtime.sqlite3",
            "anchor_relative_path": "anchors.jsonl",
            "fixture_override_env": "IDS_RUNTIME_AUTHORITY_CONFIG",
            "fixture_mode_env": "IDS_CONDITIONAL_FIXTURE_MODE",
            "fixture_release_allowed": False,
            "cli_runtime_db_role": "expected_value_only",
            "production_root_mode_max": "0700",
            "production_file_mode_max": "0600",
            "production_owner": "current_uid",
            "production_forbidden_roots": [
                "project_root",
                "~/Library/CloudStorage",
                "~/Library/Mobile Documents",
                "~/Dropbox",
                "~/Google Drive",
                "~/OneDrive",
            ],
            "production_anchor_trust": (
                "fail_closed_until_pinned_external_signature_verifier"
            ),
            "fixture_anchor_trust": "hash_chain_test_only",
            "fixture_permission_exempt": True,
        },
        "runtime_event_chain_schema": {
            "schema_version": 1,
            "event_table": "events",
            "event_domain": "main_application",
            "observation_table": "condition_observations",
            "gate_run_table": "conditional_gate_runs",
            "event_columns": [
                "sequence",
                "event_type",
                "producer_id",
                "occurred_at",
                "payload_json",
                "prev_hash",
                "event_hash",
            ],
            "event_column_types": {
                "sequence": "INTEGER",
                "event_type": "TEXT",
                "producer_id": "TEXT",
                "occurred_at": "TEXT",
                "payload_json": "TEXT",
                "prev_hash": "TEXT",
                "event_hash": "TEXT",
            },
            "event_primary_key": ["sequence"],
            "observation_columns": [
                "source_event_seq",
                "condition_id",
                "stage",
                "ready",
                "source_event_hash",
                "source_state_hash",
                "source_anchor_hash",
                "observed_at",
                "producer_id",
            ],
            "observation_column_types": {
                "source_event_seq": "INTEGER",
                "condition_id": "TEXT",
                "stage": "TEXT",
                "ready": "INTEGER",
                "source_event_hash": "TEXT",
                "source_state_hash": "TEXT",
                "source_anchor_hash": "TEXT",
                "observed_at": "TEXT",
                "producer_id": "TEXT",
            },
            "observation_primary_key": ["source_event_seq"],
            "gate_run_columns": [
                "run_event_seq",
                "run_id",
                "condition_id",
                "gate_id",
                "gate_stage",
                "state",
                "source_event_seq",
                "source_event_hash",
                "source_state_hash",
                "source_anchor_hash",
                "raw_result_path",
                "raw_result_sha256",
                "completed_at",
                "producer_id",
                "run_event_hash",
                "run_anchor_hash",
            ],
            "gate_run_column_types": {
                "run_event_seq": "INTEGER",
                "run_id": "TEXT",
                "condition_id": "TEXT",
                "gate_id": "TEXT",
                "gate_stage": "TEXT",
                "state": "TEXT",
                "source_event_seq": "INTEGER",
                "source_event_hash": "TEXT",
                "source_state_hash": "TEXT",
                "source_anchor_hash": "TEXT",
                "raw_result_path": "TEXT",
                "raw_result_sha256": "TEXT",
                "completed_at": "TEXT",
                "producer_id": "TEXT",
                "run_event_hash": "TEXT",
                "run_anchor_hash": "TEXT",
            },
            "gate_run_primary_key": ["run_event_seq"],
            "gate_run_unique": ["run_id"],
            "append_only_triggers": [
                {
                    "name": "events_no_update",
                    "table": "events",
                    "operation": "update",
                },
                {
                    "name": "events_no_delete",
                    "table": "events",
                    "operation": "delete",
                },
                {
                    "name": "condition_observations_no_update",
                    "table": "condition_observations",
                    "operation": "update",
                },
                {
                    "name": "condition_observations_no_delete",
                    "table": "condition_observations",
                    "operation": "delete",
                },
                {
                    "name": "conditional_gate_runs_no_update",
                    "table": "conditional_gate_runs",
                    "operation": "update",
                },
                {
                    "name": "conditional_gate_runs_no_delete",
                    "table": "conditional_gate_runs",
                    "operation": "delete",
                },
            ],
            "event_types": [
                "condition_observation",
                "conditional_gate_run",
            ],
            "genesis_prev_hash": "0" * 64,
            "payload_required_by_type": {
                "condition_observation": [
                    "condition_id",
                    "stage",
                    "ready",
                    "observed_at",
                    "producer_id",
                    "candidate_commit",
                    "candidate_tree",
                    "frozen_bundle_path",
                    "frozen_bundle_sha256",
                ],
                "conditional_gate_run": [
                    "run_id",
                    "condition_id",
                    "gate_id",
                    "gate_stage",
                    "state",
                    "source_event_seq",
                    "source_event_hash",
                    "source_state_hash",
                    "source_anchor_hash",
                    "raw_result_path",
                    "raw_result_sha256",
                    "completed_at",
                    "producer_id",
                    "executor_ids",
                    "acceptance_case_ids",
                    "candidate_commit",
                    "candidate_tree",
                    "frozen_bundle_path",
                    "frozen_bundle_sha256",
                ],
            },
            "event_hash_algorithm": "sha256_canonical_json_v1",
            "event_hash_fields": [
                "sequence",
                "event_type",
                "producer_id",
                "occurred_at",
                "payload",
                "prev_hash",
            ],
            "source_state_hash_algorithm": "sha256_canonical_json_v1",
            "source_state_hash_fields": [
                "through_sequence",
                "through_event_hash",
                "condition_states",
            ],
            "canonical_json": {
                "sort_keys": True,
                "ensure_ascii": False,
                "allow_nan": False,
                "separators": [",", ":"],
            },
            "anchor_schema": {
                "schema_version": 1,
                "format": "canonical_jsonl",
                "required": [
                    "schema_version",
                    "sequence",
                    "event_hash",
                    "anchored_at",
                    "previous_anchor_hash",
                    "anchor_hash",
                ],
                "genesis_previous_anchor_hash": "0" * 64,
                "hash_algorithm": "sha256_canonical_json_v1",
                "tail_must_equal_main_event_chain": True,
            },
        },
        "binding_rule": (
            "Git HEAD and the fixed frozen-bundle file are authoritative; CLI, raw "
            "results, evidence and --runtime-db are expected values only. Runtime "
            "readiness requires the fixed private runtime authority, a "
            "contract-authorized producer, the recomputed append-only main event "
            "chain and its external anchor; fixture authority cannot satisfy human "
            "or longitudinal release. Every gate run must append one unique run_id "
            "receipt to that anchored main event chain, binding the latest "
            "prerequisite observation and raw-result hash; overwriting current "
            "evidence cannot erase or replace the receipt. Passing evidence requires "
            "that fresh receipt, exact case-set equality and recomputable per-case "
            "input/raw hashes."
        ),
    }
    if evidence_schema != expected_conditional_evidence_schema:
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
                    or probe.get("event_table") != "events"
                    or probe.get("producer_id")
                    != "PRODUCER-RUNTIME-CONDITION-OBSERVER-V1"
                    or probe.get("producer_authority_source")
                    != "frozen_conditional_contract"
                    or probe.get("caller_producer_override_allowed") is not False
                    or not isinstance(required_observations, list)
                    or set(required_observations) != {
                        "condition_id",
                        "stage",
                        "ready",
                        "source_event_seq",
                        "source_event_hash",
                        "source_state_hash",
                        "source_anchor_hash",
                        "observed_at",
                        "producer_id",
                    }
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


def verify_design_freeze_attack_replay_payload(
    payload: Any,
    *,
    expected_commit: str,
    expected_tree: str,
    label: str,
    require_stdout_hash: bool,
    errors: list[str],
) -> None:
    if not isinstance(payload, dict):
        errors.append(f"{label} must be an object")
        return
    expected_attack_ids = FINAL_REVIEW_ATTACK_IDS
    if (
        payload.get("schema_version") != 2
        or payload.get("status") != "pass"
        or payload.get("candidate_commit") != expected_commit
        or payload.get("candidate_tree") != expected_tree
        or payload.get("runner_id") != "ids-design-freeze-attack-runner-v1"
        or payload.get("runner_sha256") != sha256(ATTACK_RUNNER)
        or payload.get("required_attack_ids") != expected_attack_ids
        or not isinstance(payload.get("started_at"), str)
        or not payload.get("started_at")
        or not isinstance(payload.get("completed_at"), str)
        or not payload.get("completed_at")
    ):
        errors.append(f"{label} identity or coverage differs")
    del require_stdout_hash
    results = payload.get("results")
    if not isinstance(results, list) or len(results) != len(expected_attack_ids):
        errors.append(f"{label} result set differs")
        return
    observed_ids: set[str] = set()
    for index, result in enumerate(results):
        if not isinstance(result, dict):
            errors.append(f"{label} results[{index}] must be an object")
            continue
        attack_id = result.get("attack_id")
        if (
            not isinstance(attack_id, str)
            or attack_id in observed_ids
            or attack_id not in FINAL_REVIEW_ATTACK_IDS
            or result.get("actual_runner_process_exit") != 0
            or result.get("declared_runner_exit_code") != 0
            or result.get("baseline_verifier_exit") != 0
            or type(result.get("target_verifier_exit")) is not int
            or result.get("target_verifier_exit") == 0
            or result.get("result") != "rejected"
            or any(
                not isinstance(result.get(field), str)
                or re.fullmatch(r"[0-9a-f]{64}", result.get(field, "")) is None
                for field in (
                    "baseline_stdout_sha256",
                    "target_stdout_sha256",
                    "execution_fingerprint",
                    "receipt_sha256",
                )
            )
        ):
            errors.append(f"{label} results[{index}] differs")
        if isinstance(attack_id, str):
            observed_ids.add(attack_id)
    if observed_ids != set(expected_attack_ids):
        errors.append(f"{label} attack IDs differ")


def run_canonical_design_freeze_attacks(
    *, candidate_commit: str, label: str, errors: list[str]
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPLAY_ATTACKS),
            "--candidate-commit",
            candidate_commit,
        ],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = None
    if result.returncode != 0 or not isinstance(payload, dict):
        errors.append(
            f"{label} escaped or errored: "
            f"{result.stdout.strip() or '<no replay output>'}"
        )
        return
    expected_tree = run_git(
        ["rev-parse", f"{candidate_commit}^{{tree}}"], errors
    )
    verify_design_freeze_attack_replay_payload(
        payload,
        expected_commit=candidate_commit,
        expected_tree=expected_tree,
        label=label,
        require_stdout_hash=False,
        errors=errors,
    )


def verify_bundle(
    bundle: dict[str, Any],
    contract: dict[str, Any],
    research: dict[str, Any],
    assurance_subjects: dict[str, Any],
    errors: list[str],
) -> None:
    if bundle.get("schema_version") != 1 or bundle.get("status") != "frozen":
        errors.append("frozen bundle schema or status differs")
    if bundle.get("contract_id") != contract.get("contract_id"):
        errors.append("frozen bundle contract_id differs")
    reviewed_commit = bundle.get("reviewed_candidate_commit")
    reviewed_tree = bundle.get("reviewed_candidate_tree")
    baseline_commit = bundle.get("baseline_commit")
    baseline_tree = bundle.get("baseline_tree")
    for label, value in (
        ("reviewed_candidate_commit", reviewed_commit),
        ("reviewed_candidate_tree", reviewed_tree),
    ):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
            errors.append(f"frozen bundle {label} must be a full SHA-1")
            if label == "reviewed_candidate_commit":
                reviewed_commit = ""
            else:
                reviewed_tree = ""
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
    if reviewed_commit and reviewed_tree:
        actual_reviewed_tree = run_git(
            ["rev-parse", f"{reviewed_commit}^{{tree}}"], errors
        )
        if actual_reviewed_tree and actual_reviewed_tree != reviewed_tree:
            errors.append(
                "frozen reviewed candidate tree mismatch: "
                f"expected {reviewed_tree}, got {actual_reviewed_tree}"
            )
    if reviewed_commit and baseline_commit:
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", reviewed_commit, baseline_commit],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if ancestry.returncode != 0:
            errors.append(
                "frozen bundle cannot prove reviewed candidate is an ancestor "
                "of the baseline"
            )

    if reviewed_commit and reviewed_tree:
        verify_design_freeze_attack_replay_payload(
            bundle.get("design_freeze_attack_replay"),
            expected_commit=reviewed_commit,
            expected_tree=reviewed_tree,
            label="frozen bundle design-freeze attack replay",
            require_stdout_hash=True,
            errors=errors,
        )

    evidence_path = bundle.get("final_review_evidence_path")
    evidence_hash = bundle.get("final_review_evidence_sha256")
    review_subject_id = bundle.get("final_review_subject_id")
    if (
        not isinstance(evidence_path, str)
        or Path(evidence_path).is_absolute()
        or ".." in Path(evidence_path).parts
        or not isinstance(evidence_hash, str)
        or not re.fullmatch(r"[0-9a-f]{64}", evidence_hash)
        or not isinstance(review_subject_id, str)
        or not review_subject_id
    ):
        errors.append("frozen bundle final review binding is invalid")
    else:
        evidence_file = PROJECT_ROOT / evidence_path
        if not evidence_file.is_file() or sha256(evidence_file) != evidence_hash:
            errors.append("frozen bundle final review evidence hash differs")
        if baseline_commit:
            repo_prefix_for_evidence = run_git(
                ["rev-parse", "--show-prefix"], errors
            )
            baseline_evidence = subprocess.run(
                [
                    "git",
                    "show",
                    f"{baseline_commit}:{repo_prefix_for_evidence}{evidence_path}",
                ],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if (
                baseline_evidence.returncode != 0
                or hashlib.sha256(baseline_evidence.stdout).hexdigest()
                != evidence_hash
            ):
                errors.append(
                    "frozen bundle final review evidence is absent or differs "
                    "at baseline"
                )
        challenge_rounds = research.get("challenge", {}).get("rounds")
        final_round = (
            challenge_rounds[-1]
            if isinstance(challenge_rounds, list)
            and challenge_rounds
            and isinstance(challenge_rounds[-1], dict)
            else {}
        )
        expected_round_binding = {
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "reviewer_subjects": [review_subject_id],
            "result": "passed_freeze",
            "evidence_path": evidence_path,
            "evidence_sha256": evidence_hash,
            "open_critical_count": 0,
            "open_major_count": 0,
            "new_architecture_changing_classes": [],
        }
        for key, expected in expected_round_binding.items():
            if final_round.get(key) != expected:
                errors.append(f"frozen bundle final review round {key} differs")
        matching_subjects = [
            subject
            for subject in assurance_subjects.get("subjects", [])
            if isinstance(subject, dict) and subject.get("id") == review_subject_id
        ]
        if len(matching_subjects) != 1:
            errors.append("frozen bundle final review subject is missing or duplicated")
        else:
            subject = matching_subjects[0]
            expected_subject_binding = {
                "role": "design_reviewer",
                "candidate_commit": reviewed_commit,
                "candidate_tree": reviewed_tree,
                "write_access_used": False,
                "participated_in_candidate_construction": False,
                "verdict": "passed_freeze",
                "evidence_path": evidence_path,
                "evidence_sha256": evidence_hash,
            }
            for key, expected in expected_subject_binding.items():
                if subject.get(key) != expected:
                    errors.append(
                        f"frozen bundle final review subject {key} differs"
                    )
    observations = bundle.get("baseline_remote_observations")
    expected_phases = {
        "before_baseline_verification",
        "after_baseline_verification",
    }
    observed_phases: set[str] = set()
    observed_refs: set[str] = set()
    if not isinstance(observations, list) or len(observations) != 2:
        errors.append("frozen bundle baseline remote observations differ")
    else:
        for index, observation in enumerate(observations):
            if not isinstance(observation, dict):
                errors.append(
                    f"frozen bundle baseline remote observation[{index}] is invalid"
                )
                continue
            phase = observation.get("phase")
            if not isinstance(phase, str) or phase in observed_phases:
                errors.append(
                    f"frozen bundle baseline remote observation[{index}] phase differs"
                )
            else:
                observed_phases.add(phase)
            ref = observation.get("ref")
            if (
                observation.get("remote") != "origin"
                or observation.get("commit") != baseline_commit
                or not isinstance(ref, str)
                or not ref.startswith("refs/heads/")
                or not isinstance(observation.get("observed_at"), str)
                or not observation.get("observed_at")
            ):
                errors.append(
                    f"frozen bundle baseline remote observation[{index}] binding differs"
                )
            else:
                observed_refs.add(ref)
        if observed_phases != expected_phases:
            errors.append("frozen bundle baseline remote observation phases differ")
        if len(observed_refs) != 1:
            errors.append("frozen bundle baseline remote refs differ")
    if not isinstance(bundle.get("created_at"), str) or not bundle.get("created_at"):
        errors.append("frozen bundle created_at is missing")
    creation_rule = bundle.get("creation_rule")
    if (
        not isinstance(creation_rule, str)
        or not creation_rule
        or "non-atomic" not in creation_rule
        or "committed, pushed" not in creation_rule
    ):
        errors.append("frozen bundle creation_rule overstates its provenance")

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
    if reviewed_commit and baseline_commit and isinstance(frozen_files, list):
        freezer_path = PROJECT_ROOT / "scripts" / "freeze_governance.py"
        try:
            module_spec = importlib.util.spec_from_file_location(
                "ids_freeze_governance_verifier", freezer_path
            )
            if module_spec is None or module_spec.loader is None:
                raise RuntimeError("cannot load freeze_governance")
            freezer_module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(freezer_module)
            closure_facts = freezer_module.require_review_closure(
                reviewed_commit, baseline_commit, frozen_files
            )
            if (
                closure_facts.get("reviewed_candidate_tree") != reviewed_tree
                or closure_facts.get("baseline_tree") != baseline_tree
                or closure_facts.get("review_subject_id") != review_subject_id
                or closure_facts.get("review_evidence_path") != evidence_path
                or closure_facts.get("review_evidence_sha256") != evidence_hash
            ):
                errors.append("frozen bundle closure facts differ")
        except (OSError, RuntimeError, SystemExit) as exc:
            errors.append(f"frozen bundle review closure verification failed: {exc}")
    repo_prefix = run_git(["rev-parse", "--show-prefix"], errors)
    actual_paths: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"frozen bundle files[{index}] must be object")
            continue
        relative = entry.get("path")
        expected_hash = entry.get("sha256")
        expected_blob = entry.get("git_blob")
        expected_mode = entry.get("git_mode")
        expected_type = entry.get("git_type")
        expected_object_kind = entry.get("git_object_kind")
        if (
            not isinstance(relative, str)
            or not isinstance(expected_hash, str)
            or not isinstance(expected_blob, str)
            or not isinstance(expected_mode, str)
            or not isinstance(expected_type, str)
            or not isinstance(expected_object_kind, str)
        ):
            errors.append(
                f"frozen bundle files[{index}] lacks content and Git identity fields"
            )
            continue
        if (
            expected_mode != "100644"
            or expected_type != "blob"
            or expected_object_kind != "blob"
        ):
            errors.append(f"frozen bundle Git mode/type differs for {relative}")
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
                [
                    "ls-tree",
                    "--full-tree",
                    baseline_commit,
                    "--",
                    f":(top,literal){repo_relative}",
                ],
                errors,
            )
            fields = tree_line.split()
            actual_mode = fields[0] if len(fields) >= 3 else ""
            actual_type = fields[1] if len(fields) >= 3 else ""
            actual_blob = fields[2] if len(fields) >= 3 else ""
            if actual_mode != expected_mode or actual_type != expected_type:
                errors.append(
                    f"baseline Git mode/type mismatch for {relative}: "
                    f"expected {expected_mode}/{expected_type}, "
                    f"got {actual_mode or '<missing>'}/{actual_type or '<missing>'}"
                )
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

    head = run_git(["rev-parse", "HEAD"], errors)
    if baseline_commit and head:
        ancestry = subprocess.run(
            ["git", "merge-base", "--is-ancestor", baseline_commit, head],
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if ancestry.returncode != 0:
            errors.append("frozen bundle baseline is not an ancestor of HEAD")
        current_tree = run_git(["rev-parse", "HEAD^{tree}"], errors)
        if current_tree:
            run_canonical_design_freeze_attacks(
                candidate_commit=reviewed_commit,
                label="current design-freeze attack replay",
                errors=errors,
            )
        remote_verifier = PROJECT_ROOT / "scripts" / "verify_remote_commit.py"
        trusted_remote = contract.get("change_control", {}).get(
            "trusted_git_remote", {}
        )
        trusted_remote_name = (
            trusted_remote.get("name")
            if isinstance(trusted_remote, dict)
            else None
        )
        result = subprocess.run(
            [
                sys.executable,
                str(remote_verifier),
                "--verify-frozen-bundle",
                "--commit",
                head,
                "--remote",
                trusted_remote_name
                if isinstance(trusted_remote_name, str)
                else "",
                "--json",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            remote_payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            remote_payload = {}
        remote_facts = (
            remote_payload.get("facts")
            if isinstance(remote_payload, dict)
            and isinstance(remote_payload.get("facts"), dict)
            else {}
        )
        inner_clone_context = os.environ.get(INNER_REMOTE_CONTEXT_ENV) is not None
        expected_scope = "inner_clone" if inner_clone_context else "full_outer"
        scope_matches = (
            remote_payload.get("verification_scope") == expected_scope
            and remote_facts.get("verification_scope") == expected_scope
        )
        if inner_clone_context:
            remote_completion_matches = (
                remote_facts.get("mode") == "frozen_bundle_inner_clone"
                and remote_facts.get("full_remote_verification") is False
            )
        else:
            clone_governance = remote_facts.get("clone_governance")
            remote_observation = remote_facts.get("remote_observation")
            post_clone_observation = remote_facts.get(
                "post_clone_remote_observation"
            )
            expected_remote_observation = {
                "remote": EXPECTED_TRUSTED_GIT_REMOTE["name"],
                "fetch_url": EXPECTED_TRUSTED_GIT_REMOTE["fetch_url"],
                "ref": (
                    "refs/heads/"
                    f"{EXPECTED_TRUSTED_GIT_REMOTE['branch']}"
                ),
                "commit": head,
            }
            remote_completion_matches = (
                remote_facts.get("mode") == "frozen_bundle_commit"
                and remote_facts.get("full_remote_verification") is True
                and remote_facts.get("fresh_clone") is True
                and remote_facts.get("cloned_commit") == head
                and remote_facts.get("cloned_tree") == current_tree
                and remote_facts.get("current_branch")
                == EXPECTED_TRUSTED_GIT_REMOTE["branch"]
                and remote_facts.get("upstream")
                == (
                    f"{EXPECTED_TRUSTED_GIT_REMOTE['name']}/"
                    f"{EXPECTED_TRUSTED_GIT_REMOTE['branch']}"
                )
                and remote_facts.get("configured_fetch_urls")
                == [EXPECTED_TRUSTED_GIT_REMOTE["fetch_url"]]
                and isinstance(remote_observation, dict)
                and all(
                    remote_observation.get(key) == value
                    for key, value in expected_remote_observation.items()
                )
                and isinstance(post_clone_observation, dict)
                and all(
                    post_clone_observation.get(key) == value
                    for key, value in expected_remote_observation.items()
                )
                and isinstance(clone_governance, dict)
                and clone_governance.get("exit_code") == 0
                and clone_governance.get("verification_scope") == "inner_clone"
                and isinstance(clone_governance.get("inner_receipt"), dict)
            )
        if (
            result.returncode != 0
            or remote_payload.get("status") != "pass"
            or not scope_matches
            or not remote_completion_matches
            or remote_facts.get("head") != head
            or remote_facts.get("head_tree") != current_tree
            or remote_facts.get("trusted_git_remote")
            != EXPECTED_TRUSTED_GIT_REMOTE
            or remote_facts.get("project_prefix")
            != EXPECTED_TRUSTED_GIT_REMOTE["project_prefix"]
            or remote_facts.get("bundle_sha256") != sha256(FROZEN_BUNDLE)
            or remote_facts.get("bundle_git_mode") != "100644"
            or remote_facts.get("bundle_git_type") != "blob"
        ):
            errors.append(
                "frozen bundle is not the tracked HEAD blob on trusted origin: "
                f"{result.stdout.strip() or '<no verifier output>'}"
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
    assurance_trust_model = load_json(ASSURANCE_TRUST_MODEL, errors)
    ground_truth_manifest = load_json(GROUND_TRUTH_MANIFEST, errors)
    research_sufficiency = load_json(RESEARCH_SUFFICIENCY, errors)
    failure_classes = load_json(FAILURE_CLASSES, errors)
    decision_authority = load_json(DECISION_AUTHORITY, errors)
    project_method_policy = load_json(PROJECT_METHOD_POLICY, errors)

    if errors:
        return errors

    research_sufficiency_verifier = (
        PROJECT_ROOT / "scripts" / "verify_research_sufficiency.py"
    )
    if not research_sufficiency_verifier.is_file():
        errors.append("research sufficiency verifier is missing")
    else:
        research_result = subprocess.run(
            [sys.executable, str(research_sufficiency_verifier), "--json"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            research_payload = json.loads(research_result.stdout)
        except json.JSONDecodeError:
            research_payload = {}
        if (
            research_result.returncode != 0
            or research_payload.get("status") != "pass"
        ):
            detail = research_payload.get("errors")
            if not isinstance(detail, list):
                detail = [research_result.stdout.strip() or "<no verifier output>"]
            errors.append(
                "research sufficiency executable verification failed: "
                + "; ".join(str(item) for item in detail)
            )

    assurance_metadata_verifier = (
        PROJECT_ROOT / "scripts" / "verify_assurance_metadata.py"
    )
    if not assurance_metadata_verifier.is_file():
        errors.append("assurance metadata verifier is missing")
    else:
        assurance_result = subprocess.run(
            [sys.executable, str(assurance_metadata_verifier), "--json"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            assurance_payload = json.loads(assurance_result.stdout)
        except json.JSONDecodeError:
            assurance_payload = {}
        if (
            assurance_result.returncode != 0
            or assurance_payload.get("status") != "pass"
        ):
            detail = assurance_payload.get("errors")
            if not isinstance(detail, list):
                detail = [assurance_result.stdout.strip() or "<no verifier output>"]
            errors.append(
                "assurance metadata executable verification failed: "
                + "; ".join(str(item) for item in detail)
            )

    project_method_verifier = (
        PROJECT_ROOT / "scripts" / "verify_project_method.py"
    )
    if not project_method_verifier.is_file():
        errors.append("project method verifier is missing")
    else:
        project_method_result = subprocess.run(
            [sys.executable, str(project_method_verifier), "--json"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            project_method_payload = json.loads(project_method_result.stdout)
        except json.JSONDecodeError:
            project_method_payload = {}
        if (
            project_method_result.returncode != 0
            or project_method_payload.get("status") != "pass"
        ):
            detail = project_method_payload.get("errors")
            if not isinstance(detail, list):
                detail = [
                    project_method_result.stdout.strip() or "<no verifier output>"
                ]
            errors.append(
                "project method executable verification failed: "
                + "; ".join(str(item) for item in detail)
            )

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
        ("assurance trust model", assurance_trust_model),
        ("ground truth manifest", ground_truth_manifest),
        ("research sufficiency", research_sufficiency),
        ("failure classes", failure_classes),
        ("decision authority", decision_authority),
        ("project method policy", project_method_policy),
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
        if research_sufficiency.get("derived_pre_review_eligible") is not True:
            errors.append("research sufficiency is not derived pre-review eligible")

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
    verify_research_register(
        research,
        research_sufficiency,
        contract,
        implementation_targets,
        allow_candidate,
        errors,
    )
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
    repository_frozen_files = (
        change_control.get("repository_frozen_files")
        if isinstance(change_control, dict)
        else None
    )
    if repository_frozen_files != [ASSURANCE_WORKFLOW_REPO_PATH]:
        errors.append("repository frozen file boundary differs")
    repository_root_text = run_git(["rev-parse", "--show-toplevel"], errors)
    if repository_root_text:
        workflow_path = Path(repository_root_text) / ASSURANCE_WORKFLOW_REPO_PATH
        machine_root = assurance_trust_model.get(
            "trust_roots", {}
        ).get("github_actions_machine_execution", {})
        expected_workflow_hash = (
            machine_root.get("workflow_sha256")
            if isinstance(machine_root, dict)
            else None
        )
        if (
            not workflow_path.is_file()
            or not isinstance(expected_workflow_hash, str)
            or sha256(workflow_path) != expected_workflow_hash
        ):
            errors.append("assurance workflow content binding differs")
    trusted_remote = (
        change_control.get("trusted_git_remote")
        if isinstance(change_control, dict)
        else None
    )
    expected_remote_fields = {
        "name",
        "fetch_url",
        "branch",
        "project_prefix",
    }
    if (
        not isinstance(trusted_remote, dict)
        or set(trusted_remote) != expected_remote_fields
        or trusted_remote != EXPECTED_TRUSTED_GIT_REMOTE
        or not isinstance(trusted_remote.get("fetch_url"), str)
        or not trusted_remote.get("fetch_url")
        or trusted_remote.get("fetch_url", "").startswith("-")
        or not isinstance(trusted_remote.get("branch"), str)
        or re.fullmatch(
            r"[A-Za-z0-9._/-]+", trusted_remote.get("branch", "")
        )
        is None
        or not isinstance(trusted_remote.get("project_prefix"), str)
        or not trusted_remote.get("project_prefix", "").endswith("/")
        or ".." in Path(trusted_remote.get("project_prefix", "")).parts
    ):
        errors.append("trusted Git remote policy differs")
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
            verify_bundle(
                bundle,
                contract,
                research,
                assurance_subjects,
                errors,
            )

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
    if args.allow_candidate:
        verification_scope = "candidate"
    elif os.environ.get(INNER_REMOTE_CONTEXT_ENV) is not None:
        verification_scope = "frozen-inner-clone"
    else:
        verification_scope = "frozen-full-outer"
    print(
        "governance verification: PASS "
        f"({verification_scope})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
