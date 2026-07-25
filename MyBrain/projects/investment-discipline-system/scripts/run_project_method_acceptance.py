#!/usr/bin/env python3
"""Execute candidate-bound project-method mechanisms and write closure evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()
).resolve()
POLICY_PATH = PROJECT_ROOT / "governance" / "PROJECT_METHOD_POLICY_V1.json"
FAILURE_REGISTRY = PROJECT_ROOT / "governance" / "FAILURE_CLASSES_V1.json"
DEFAULT_OUTPUT = (
    PROJECT_ROOT / "evidence" / "verification" / "V-PROJECT-METHOD.json"
)
DEFAULT_TIMEOUT_SECONDS = 300


FAILURE_CASES: list[dict[str, Any]] = [
    {
        "failure_id": "GOV-04",
        "case_id": "CASE-METHOD-CRITERION-WEAKENING",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_criterion_weakening_is_rejected",
                "governance_tests.test_contract_supersession",
                "-v",
            ]
        ],
        "limitations": [
            "The executable successor fixtures cover declared frozen fields and catalogs, but no finite comparison can recognize every semantically equivalent weakening outside that declared contract."
        ],
    },
    {
        "failure_id": "GOV-07",
        "case_id": "CASE-METHOD-CONDITIONAL-BYPASS",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_conditional_bypass_is_rejected",
                "-v",
            ]
        ],
        "limitations": [
            "The mutation does not exhaust every semantically equivalent requirement split, selector rewrite, or oracle weakening."
        ],
    },
    {
        "failure_id": "CTX-02",
        "case_id": "CASE-METHOD-MIDDLE-SENTINEL",
        "commands": [
            ["PYTHON", "scripts/verify_context_recovery.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_context_recovery",
                "-v",
            ],
        ],
        "limitations": [
            "Deterministic state-byte and recovery probes do not prove arbitrary-model recall or every production compaction behavior."
        ],
    },
    {
        "failure_id": "ORG-01",
        "case_id": "CASE-METHOD-BROAD-WRITE-SCOPE",
        "commands": [
            [
                "PYTHON",
                "scripts/verify_work_packets.py",
                "--packet-dir",
                ".work_packets/packets",
                "--json",
            ],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_work_packets.WorkPacketVerifierTests.test_broad_top_level_tree_scope_is_rejected",
                "governance_tests.test_work_packets.WorkPacketVerifierTests.test_bound_checkpoint_and_acceptance_receipts_allow_completion",
                "-v",
            ],
        ],
        "limitations": [
            "Path ownership is cooperative and point-in-time; it is not an operating-system write sandbox."
        ],
    },
    {
        "failure_id": "ORG-03",
        "case_id": "CASE-METHOD-PARALLEL-COLLISION",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_work_packets.WorkPacketVerifierTests.test_direct_duplicate_ownership_is_rejected",
                "governance_tests.test_work_packets.WorkPacketVerifierTests.test_parent_child_ownership_overlap_is_rejected",
                "governance_tests.test_work_packets.WorkPacketVerifierTests.test_disjoint_text_changes_can_fail_joint_semantic_invariant",
                "-v",
            ]
        ],
        "limitations": [
            "Only declared supported semantic invariants are evaluated; omitted cross-component invariants remain outside this mechanism."
        ],
    },
    {
        "failure_id": "ORG-04",
        "case_id": "CASE-METHOD-REPEATED-BLOCKER",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_repeated_blocker_threshold_weakening_is_rejected",
                "-v",
            ],
            ["PYTHON", "scripts/verify_execution_loop.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_execution_loop",
                "-v",
            ],
        ],
        "limitations": [
            "The append-oriented ledger persists stable root-cause identifiers and derives the three-strike stop, but dishonest semantic splitting of one blocker still requires independent review."
        ],
    },
    {
        "failure_id": "ORG-05",
        "case_id": "CASE-METHOD-HARNESS-NO-BASELINE",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_harness_without_same_task_ablation_is_rejected",
                "-v",
            ],
            ["PYTHON", "scripts/verify_r9_same_task_comparison.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_r9_same_task_comparison",
                "-v",
            ],
        ],
        "limitations": [
            "The current control proves the optional wrapper is not adopted while the preregistered experiment is blocked before generation; it does not estimate either wrapper's quality."
        ],
    },
    {
        "failure_id": "ORG-06",
        "case_id": "CASE-METHOD-REVIEWER-WRITES-CANDIDATE",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_reviewer_candidate_write_access_is_rejected",
                "-v",
            ]
        ],
        "limitations": [
            "Hash and write-scope receipts can detect observed candidate writes but cannot prove organizational or security isolation."
        ],
    },
    {
        "failure_id": "IMP-04",
        "case_id": "CASE-METHOD-FLOATING-DEPENDENCY",
        "commands": [
            ["PYTHON", "scripts/verify_dependency_boundary.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_floating_dependency_is_rejected",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_dependency_boundary_binding_is_rejected_when_redirected",
                "governance_tests.test_assurance_metadata.AssuranceMetadataMutationTests.test_rejects_unpinned_action_reference",
                "governance_tests.test_dependency_boundary",
                "-v",
            ]
        ],
        "limitations": [
            "The static boundary binds declared imports, supported installer/config syntax, the local exact-version artifact hash, binary-only no-dependency CI flags, and external Action revisions; it does not prove the GitHub runner, Python or pip bootstrap, upstream binary safety, vulnerabilities, or every runtime-generated process argument."
        ],
    },
    {
        "failure_id": "VER-07",
        "case_id": "CASE-METHOD-FROZEN-TEST-DELETED",
        "commands": [
            ["PYTHON", "scripts/verify_frozen_tests.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_frozen_tests",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_regression_test_universe_narrowing_is_rejected",
                "-v",
            ],
        ],
        "limitations": [
            "The manifest protects only listed tests, while the regression-universe policy separately fixes recursive test*.py discovery and exact test identities; neither establishes that an original oracle is semantically correct."
        ],
    },
    {
        "failure_id": "SEC-06",
        "case_id": "CASE-METHOD-TELEMETRY-UNKNOWN",
        "commands": [
            ["PYTHON", "scripts/verify_dependency_boundary.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_unknown_telemetry_warning_is_rejected",
                "governance_tests.test_dependency_boundary.DependencyBoundaryTests.test_unknown_telemetry_is_rejected",
                "-v",
            ]
        ],
        "limitations": [
            "The repository configuration fails closed on unknown declared telemetry, but static source inspection does not prove absence of indirect dependency telemetry, operating-system behavior, or unobserved network activity."
        ],
    },
    {
        "failure_id": "OPS-08",
        "case_id": "CASE-METHOD-INCIDENT-NO-REGRESSION",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_attack_runner",
                "-v",
            ]
        ],
        "timeout_seconds": 1200,
        "limitations": [
            "Regression coverage addresses the recorded oracle incident; future incidents may expose a different root cause."
        ],
    },
    {
        "failure_id": "HUM-05",
        "case_id": "CASE-METHOD-EXPLANATION-OMITS-UNKNOWN",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_explanation_without_unknowns_is_rejected",
                "-v",
            ]
        ],
        "conditional_gate_id": "COND-JAVEN-FIELD-USE",
        "limitations": [
            "Fixture text cannot prove that the real nontechnical user understood the system during onboarding and longitudinal use."
        ],
    },
    {
        "failure_id": "ECO-01",
        "case_id": "CASE-METHOD-BUDGET-RELABELLED-SUCCESS",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_budget_exhaustion_relabelled_success_is_rejected",
                "-v",
            ],
            [
                "PYTHON",
                "scripts/verify_work_packets.py",
                "--packet-dir",
                ".work_packets/packets",
                "--json",
            ],
            ["PYTHON", "scripts/verify_execution_loop.py", "--json"],
        ],
        "limitations": [
            "Wall time, attempts, retries, and no-progress are recorded; token telemetry remains explicitly unknown where the platform supplies no receipt, so aggregate cost accounting remains partial rather than measured."
        ],
    },
    {
        "failure_id": "ECO-02",
        "case_id": "CASE-METHOD-LIVE-SCOPE-SMUGGLE",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_live_scope_smuggling_is_rejected",
                "-v",
            ],
            ["PYTHON", "scripts/verify_no_live_scope.py", "--json"],
        ],
        "limitations": [
            "The declared implementation roots and active work packets are scanned at one point in time; this is not operating-system network isolation and must be extended when product entry points are added."
        ],
    },
    {
        "failure_id": "ECO-03",
        "case_id": "CASE-METHOD-COMPONENT-NO-REMOVAL",
        "commands": [
            ["PYTHON", "scripts/verify_component_registry.py", "--json"],
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_component_registry.ComponentRegistryTests.test_invalid_removal_or_migration_evidence_is_rejected",
                "governance_tests.test_component_registry.ComponentRegistryTests.test_removal_dry_run_reports_blocker_without_deleting",
                "-v",
            ],
        ],
        "conditional_gate_id": "COND-LONGITUDINAL-EDGE",
        "limitations": [
            "The current inventory and removal dry-run do not prove maintenance cost across multiple real periods."
        ],
    },
    {
        "failure_id": "ECO-04",
        "case_id": "CASE-METHOD-RENAME-REWRITE",
        "commands": [
            [
                "PYTHON",
                "-m",
                "unittest",
                "governance_tests.test_project_method.ProjectMethodPolicyTests.test_terminology_only_rewrite_is_rejected",
                "-v",
            ],
            ["PYTHON", "scripts/verify_migration_drill.py", "--json"],
        ],
        "limitations": [
            "The executable drill proves one representative work-packet migration and exact rollback, not every future database schema, concurrent writer, or filesystem crash model."
        ],
    },
]


class DuplicateKeyError(ValueError):
    """Raised when a JSON object attempts to overwrite an earlier key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=lambda constant: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {constant!r}")
        ),
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one JSON object")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_text(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stdout.strip() or '<no output>'}"
        )
    return completed.stdout.strip()


def normalize_command(command: list[str]) -> list[str]:
    return [sys.executable if item == "PYTHON" else item for item in command]


def display_command(command: list[str]) -> list[str]:
    return ["PYTHON" if item == sys.executable else item for item in command]


def execute(command: list[str], *, timeout_seconds: int) -> dict[str, Any]:
    argv = normalize_command(command)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        completed = subprocess.run(
            argv,
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=environment,
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        timed_out = False
    except FileNotFoundError as exc:
        exit_code = 127
        stdout = str(exc)
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        captured = exc.stdout or ""
        if isinstance(captured, bytes):
            captured = captured.decode("utf-8", "replace")
        stdout = captured
        timed_out = True
    completed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    return {
        "argv": display_command(argv),
        "started_at": started_at,
        "completed_at": completed_at,
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stdout_tail": stdout[-4000:],
    }


def project_is_clean_before_evidence(output: Path) -> tuple[bool, list[str]]:
    output_relative: str | None = None
    try:
        output_relative = output.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        pass
    command = [
        "git",
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        ".",
    ]
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        return False, [completed.stdout.strip() or "git status failed"]
    dirty = []
    for line in completed.stdout.splitlines():
        path = line[3:] if len(line) > 3 else line
        if output_relative is not None and path == output_relative:
            continue
        dirty.append(line)
    return not dirty, dirty


def write_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        help=(
            "Write the closure receipt outside the candidate worktree, verify it, "
            "and remove it before returning."
        ),
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run the independent closure-evidence verifier after writing the receipt.",
    )
    args = parser.parse_args()
    if args.ephemeral and args.output is not None:
        parser.error("--ephemeral and --output are mutually exclusive")
    temporary_output: tempfile.TemporaryDirectory[str] | None = None
    if args.ephemeral:
        temporary_output = tempfile.TemporaryDirectory(
            prefix="ids-project-method-"
        )
        output = Path(temporary_output.name) / "V-PROJECT-METHOD.json"
    elif args.output is None:
        output = DEFAULT_OUTPUT
    else:
        output = (
            args.output
            if args.output.is_absolute()
            else PROJECT_ROOT / args.output
        )

    preconditions: list[str] = []
    try:
        policy = load_json(POLICY_PATH)
        registry = load_json(FAILURE_REGISTRY)
        candidate_commit = git_text("rev-parse", "HEAD")
        candidate_tree = git_text("rev-parse", "HEAD^{tree}")
        project_prefix = git_text("rev-parse", "--show-prefix")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(
            json.dumps(
                {"status": "fail", "errors": [str(exc)]},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        if temporary_output is not None:
            temporary_output.cleanup()
        return 1

    clean, dirty = project_is_clean_before_evidence(output)
    if not clean:
        preconditions.append(
            "candidate worktree was not clean before evidence generation: "
            + "; ".join(dirty)
        )
    if policy.get("status") not in {"candidate_for_freeze", "frozen"}:
        preconditions.append("project method policy status is not freeze-eligible")

    registry_entries = registry.get("failure_classes")
    if not isinstance(registry_entries, list):
        preconditions.append("failure registry entries are missing")
        registry_by_id: dict[str, dict[str, Any]] = {}
    else:
        registry_by_id = {
            entry.get("id"): entry
            for entry in registry_entries
            if isinstance(entry, dict) and isinstance(entry.get("id"), str)
        }

    failure_results: list[dict[str, Any]] = []
    for plan in FAILURE_CASES:
        timeout_seconds = int(
            plan.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
        )
        executions = [
            execute(command, timeout_seconds=timeout_seconds)
            for command in plan["commands"]
        ]
        commands_passed = all(
            execution["exit_code"] == 0 and not execution["timed_out"]
            for execution in executions
        )
        registry_entry = registry_by_id.get(plan["failure_id"], {})
        registry_status = registry_entry.get("status")
        conditional_gate = plan.get("conditional_gate_id")
        if commands_passed and registry_status == "covered":
            outcome = "mechanism_verified"
            applied_gate = None
        elif (
            commands_passed
            and registry_status == "partially_covered"
            and isinstance(conditional_gate, str)
        ):
            outcome = "conditionally_deferred"
            applied_gate = conditional_gate
        else:
            outcome = "blocked"
            applied_gate = None
        raw_result = {
            "registry_status": registry_status,
            "commands_passed": commands_passed,
            "executions": executions,
        }
        failure_results.append(
            {
                "failure_id": plan["failure_id"],
                "case_id": plan["case_id"],
                "outcome": outcome,
                "selector_observation": (
                    f"{len(executions)} frozen command(s) executed; "
                    f"commands_passed={str(commands_passed).lower()}; "
                    f"registry_status={registry_status!r}"
                ),
                "oracle_observations": [
                    (
                        "Every required process exited zero without timeout."
                        if commands_passed
                        else "At least one required process failed, was absent, or timed out."
                    ),
                    (
                        "Closure outcome was derived from both process observations "
                        "and the candidate failure-registry status."
                    ),
                ],
                "raw_result": raw_result,
                "raw_result_sha256": sha256_bytes(canonical_bytes(raw_result)),
                "residual_limitations": list(plan["limitations"]),
                "conditional_gate_id": applied_gate,
            }
        )

    all_outcomes_eligible = all(
        result["outcome"] in {"mechanism_verified", "conditionally_deferred"}
        for result in failure_results
    )
    status = "pass" if not preconditions and all_outcomes_eligible else "fail"
    evidence = {
        "schema_version": 1,
        "verification_id": "V-PROJECT-METHOD",
        "executor_id": "ids-project-method-acceptance-v1",
        "status": status,
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "project_prefix": project_prefix,
        "policy_sha256": sha256_bytes(POLICY_PATH.read_bytes()),
        "failure_registry_sha256": sha256_bytes(FAILURE_REGISTRY.read_bytes()),
        "failure_results": failure_results,
        "limitations": [
            "A passing receipt proves only the listed deterministic mechanisms against the exact clean candidate and declared conditionals.",
            "Separate-context review remains platform-observable rather than organizationally or cryptographically independent.",
            "Open-world unknowns, real-user comprehension, and longitudinal maintenance remain governed by their explicit conditional gates.",
            *preconditions,
        ],
    }
    write_atomic(output, evidence)
    summary = {
        "status": status,
        "verification_id": evidence["verification_id"],
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "evidence_path": (
            "ephemeral://V-PROJECT-METHOD.json"
            if args.ephemeral
            else (
                output.relative_to(PROJECT_ROOT).as_posix()
                if output.is_relative_to(PROJECT_ROOT)
                else str(output)
            )
        ),
        "evidence_sha256": sha256_bytes(output.read_bytes()),
        "eligible_count": sum(
            result["outcome"] in {"mechanism_verified", "conditionally_deferred"}
            for result in failure_results
        ),
        "blocked_failure_ids": [
            result["failure_id"]
            for result in failure_results
            if result["outcome"] == "blocked"
        ],
        "precondition_errors": preconditions,
    }
    if args.verify:
        verification = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "verify_project_method.py"),
                "--json",
                "--require-closure",
                "--evidence",
                str(output),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            verification_payload = json.loads(verification.stdout)
        except json.JSONDecodeError:
            verification_payload = {
                "status": "fail",
                "errors": [verification.stdout.strip() or "<no verifier output>"],
            }
        if args.ephemeral and isinstance(verification_payload, dict):
            verification_payload["closure_evidence_path"] = (
                "ephemeral://V-PROJECT-METHOD.json"
            )
        summary["closure_verification"] = verification_payload
        if (
            verification.returncode != 0
            or verification_payload.get("status") != "pass"
        ):
            summary["status"] = "fail"
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return_code = 0 if summary["status"] == "pass" else 1
    if temporary_output is not None:
        temporary_output.cleanup()
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
