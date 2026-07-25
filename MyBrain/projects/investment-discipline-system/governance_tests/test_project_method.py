from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_project_method.py"


class ProjectMethodPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        (self.root / "governance").mkdir()
        (self.root / "governance_tests").mkdir()

        for relative in (
            "governance/PROJECT_METHOD_POLICY_V1.json",
            "governance/FAILURE_CLASSES_V1.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_ROOT / relative, target)

        for relative in (
            "PROJECT_CHARTER.md",
            "STATUS.md",
            "TASK_BOARD.md",
            "DECISIONS.md",
            "AI_COLLABORATION_METHOD.md",
            "governance_tests/test_attack_runner.py",
            "governance_tests/test_project_method_acceptance_runner.py",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n", encoding="utf-8")

        self.git("init")
        self.git("config", "user.name", "Project Method Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("add", ".")
        self.git("commit", "-m", "fixture baseline")

    def tearDown(self) -> None:
        self._temporary.cleanup()

    @property
    def policy_path(self) -> Path:
        return self.root / "governance" / "PROJECT_METHOD_POLICY_V1.json"

    @property
    def registry_path(self) -> Path:
        return self.root / "governance" / "FAILURE_CLASSES_V1.json"

    def run_verifier(
        self, *extra_arguments: str
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["IDS_PROJECT_ROOT"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--json", *extra_arguments],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def git(self, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            completed.returncode,
            completed.stdout + completed.stderr,
        )
        return completed.stdout.strip()

    def load_policy(self) -> dict[str, Any]:
        return json.loads(self.policy_path.read_text(encoding="utf-8"))

    def write_policy(self, policy: dict[str, Any]) -> None:
        self.policy_path.write_text(
            json.dumps(policy, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def load_registry(self) -> dict[str, Any]:
        return json.loads(self.registry_path.read_text(encoding="utf-8"))

    def write_registry(self, registry: dict[str, Any]) -> None:
        self.registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def canonical_hash(value: Any) -> str:
        return hashlib.sha256(
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

    def make_eligible_closure_evidence(self) -> Path:
        registry = self.load_registry()
        conditional_ids = {"HUM-05", "ECO-03"}
        status_counts = {
            "covered": 0,
            "partially_covered": 0,
            "gap": 0,
        }
        domain_counts: dict[str, dict[str, Any]] = {}
        alias_count = 0
        noncovered_ids: list[str] = []
        method_ids = {
            item["failure_id"]
            for item in self.load_policy()["failure_coverage"]
        }
        for item in registry["failure_classes"]:
            if item["id"] in method_ids:
                if item["id"] in conditional_ids:
                    item["status"] = "partially_covered"
                    item["open_gaps"] = ["fixture conditional remains open"]
                else:
                    item["status"] = "covered"
                    item["open_gaps"] = []
            status = item["status"]
            status_counts[status] += 1
            alias_count += len(item["aliases"])
            if status != "covered":
                noncovered_ids.append(item["id"])
            domain = item["domain"]
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
        registry["open_gaps"] = noncovered_ids
        registry["coverage_summary"] = {
            "total_failure_classes": len(registry["failure_classes"]),
            "covered_failure_classes": status_counts["covered"],
            "partially_covered_failure_classes": status_counts[
                "partially_covered"
            ],
            "gap_failure_classes": status_counts["gap"],
            "alias_count": alias_count,
            "domains": list(domain_counts.values()),
            "open_gap_ids": noncovered_ids,
        }
        self.write_registry(registry)
        self.git("add", "governance/FAILURE_CLASSES_V1.json")
        self.git("commit", "-m", "eligible registry fixture")

        gates = {
            "HUM-05": "COND-JAVEN-FIELD-USE",
            "ECO-03": "COND-LONGITUDINAL-EDGE",
        }
        failure_results = []
        for binding in self.load_policy()["failure_coverage"]:
            failure_id = binding["failure_id"]
            raw_result = {
                "commands_passed": True,
                "registry_status": (
                    "partially_covered"
                    if failure_id in gates
                    else "covered"
                ),
            }
            failure_results.append(
                {
                    "failure_id": failure_id,
                    "case_id": binding["case_id"],
                    "outcome": (
                        "conditionally_deferred"
                        if failure_id in gates
                        else "mechanism_verified"
                    ),
                    "selector_observation": "fixture selector executed",
                    "oracle_observations": ["fixture oracle passed"],
                    "raw_result": raw_result,
                    "raw_result_sha256": self.canonical_hash(raw_result),
                    "residual_limitations": ["fixture limitation"],
                    "conditional_gate_id": gates.get(failure_id),
                }
            )
        evidence = {
            "schema_version": 1,
            "verification_id": "V-PROJECT-METHOD",
            "executor_id": "ids-project-method-acceptance-v1",
            "status": "pass",
            "candidate_commit": self.git("rev-parse", "HEAD"),
            "candidate_tree": self.git("rev-parse", "HEAD^{tree}"),
            "project_prefix": "",
            "policy_sha256": hashlib.sha256(
                self.policy_path.read_bytes()
            ).hexdigest(),
            "failure_registry_sha256": hashlib.sha256(
                self.registry_path.read_bytes()
            ).hexdigest(),
            "failure_results": failure_results,
            "limitations": ["fixture-only closure evidence"],
        }
        path = self.root / "closure.json"
        path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def mutate_evidence(
        self,
        path: Path,
        mutation: Callable[[dict[str, Any]], None],
    ) -> None:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        mutation(evidence)
        path.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def assert_rejected(
        self,
        mutation: Callable[[dict[str, Any]], None],
        expected_error: str,
    ) -> None:
        baseline = self.run_verifier()
        self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)

        policy = self.load_policy()
        mutation(policy)
        self.write_policy(policy)
        result = self.run_verifier()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertTrue(
            any(expected_error in error for error in payload["errors"]),
            payload["errors"],
        )

    def test_benign_policy_passes(self) -> None:
        result = self.run_verifier()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("pass", json.loads(result.stdout)["status"])

    def test_static_policy_pass_does_not_imply_closure(self) -> None:
        result = self.run_verifier("--require-closure")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("fail", payload["status"])
        self.assertEqual("blocked", payload["closure_status"])
        self.assertTrue(
            any(
                "project method closure evidence" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_candidate_bound_eligible_closure_passes(self) -> None:
        evidence = self.make_eligible_closure_evidence()
        result = self.run_verifier(
            "--require-closure",
            "--evidence",
            str(evidence),
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("eligible", json.loads(result.stdout)["closure_status"])

    def test_partial_registry_entry_cannot_be_forged_as_verified(self) -> None:
        evidence = self.make_eligible_closure_evidence()

        def mutate(payload: dict[str, Any]) -> None:
            target = next(
                item
                for item in payload["failure_results"]
                if item["failure_id"] == "HUM-05"
            )
            target["outcome"] = "mechanism_verified"
            target["conditional_gate_id"] = None

        self.mutate_evidence(evidence, mutate)
        result = self.run_verifier(
            "--require-closure",
            "--evidence",
            str(evidence),
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue(
            any(
                "cannot mark a non-covered registry entry verified: HUM-05"
                in error
                for error in json.loads(result.stdout)["errors"]
            ),
            result.stdout,
        )

    def test_wrong_conditional_gate_is_rejected(self) -> None:
        evidence = self.make_eligible_closure_evidence()

        def mutate(payload: dict[str, Any]) -> None:
            target = next(
                item
                for item in payload["failure_results"]
                if item["failure_id"] == "ECO-03"
            )
            target["conditional_gate_id"] = "COND-WRONG"

        self.mutate_evidence(evidence, mutate)
        result = self.run_verifier(
            "--require-closure",
            "--evidence",
            str(evidence),
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue(
            any(
                "unauthorized conditional deferral for ECO-03" in error
                for error in json.loads(result.stdout)["errors"]
            ),
            result.stdout,
        )

    def test_closure_evidence_must_bind_current_candidate(self) -> None:
        evidence = self.make_eligible_closure_evidence()
        self.mutate_evidence(
            evidence,
            lambda payload: payload.__setitem__(
                "candidate_commit",
                "0" * 40,
            ),
        )
        result = self.run_verifier(
            "--require-closure",
            "--evidence",
            str(evidence),
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue(
            any(
                "candidate commit differs" in error
                for error in json.loads(result.stdout)["errors"]
            ),
            result.stdout,
        )

    def test_worktree_source_drift_from_candidate_is_rejected(self) -> None:
        evidence = self.make_eligible_closure_evidence()
        self.policy_path.write_text(
            self.policy_path.read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )

        def mutate(payload: dict[str, Any]) -> None:
            payload["policy_sha256"] = hashlib.sha256(
                self.policy_path.read_bytes()
            ).hexdigest()

        self.mutate_evidence(evidence, mutate)
        result = self.run_verifier(
            "--require-closure",
            "--evidence",
            str(evidence),
        )
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertTrue(
            any(
                (
                    "source differs from candidate commit: "
                    "governance/PROJECT_METHOD_POLICY_V1.json"
                )
                in error
                for error in json.loads(result.stdout)["errors"]
            ),
            result.stdout,
        )

    def test_registry_summary_must_be_derived_from_entries(self) -> None:
        registry = self.load_registry()
        target = next(
            item
            for item in registry["failure_classes"]
            if item["id"] == "GOV-04"
        )
        target["status"] = "covered"
        target["open_gaps"] = []
        self.write_registry(registry)
        result = self.run_verifier()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(
                "coverage summary must be derived from entries" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_noncovered_registry_entry_requires_gap_reason(self) -> None:
        registry = self.load_registry()
        target = next(
            item
            for item in registry["failure_classes"]
            if item["id"] == "GOV-04"
        )
        target["open_gaps"] = []
        self.write_registry(registry)
        result = self.run_verifier()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any(
                "GOV-04 must name its remaining gaps" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_criterion_weakening_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["completion_change_control"]["monotonic_rule"] = (
                "a superseding contract may preserve a frozen criterion"
            )

        self.assert_rejected(mutate, "completion change-control monotonic_rule differs")

    def test_conditional_bypass_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["completion_change_control"]["conditional_gate_rule"] = (
                "a conditional gate may defer a named external prerequisite"
            )

        self.assert_rejected(
            mutate,
            "completion change-control conditional_gate_rule differs",
        )

    def test_missing_middle_context_probe_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["required_state_packet"]["position_probes"].remove("middle")

        self.assert_rejected(mutate, "context position probes differs")

    def test_broad_write_scope_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["work_packet_contract"]["forbidden_write_scopes"].remove("/")

        self.assert_rejected(mutate, "forbidden work-packet write scopes differs")

    def test_parallel_write_collision_bypass_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["work_packet_contract"]["parallel_write_rule"] = (
                "active packets may share write paths"
            )

        self.assert_rejected(mutate, "parallel write ownership rule differs")

    def test_repeated_blocker_threshold_weakening_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["execution_state_machine"][
                "max_consecutive_same_blocker_turns"
            ] = 4

        self.assert_rejected(mutate, "same-blocker stop threshold differs")

    def test_harness_without_same_task_ablation_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["harness_admission"]["missing_ablation_outcome"] = "adopted"

        self.assert_rejected(
            mutate,
            "missing harness ablation must reject adoption",
        )

    def test_reviewer_candidate_write_access_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["review_boundary"]["reviewer_candidate_write_paths"] = ["src/"]

        self.assert_rejected(
            mutate,
            "reviewer candidate write paths must be empty",
        )

    def test_floating_dependency_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["supply_chain"]["floating_versions_allowed"] = True

        self.assert_rejected(
            mutate,
            "supply-chain floating_versions_allowed differs",
        )

    def test_dependency_boundary_binding_is_rejected_when_redirected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["supply_chain"]["boundary_verifier"] = (
                "scripts/unreviewed_dependency_check.py"
            )

        self.assert_rejected(
            mutate,
            "supply-chain boundary_verifier binding differs",
        )

    def test_frozen_test_baseline_bypass_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["frozen_test_integrity"][
                "baseline_must_pass_before_mutation"
            ] = False

        self.assert_rejected(
            mutate,
            "mutation tests must first prove a passing baseline",
        )

    def test_regression_test_universe_narrowing_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            universe = policy["frozen_test_integrity"][
                "complete_regression_universe"
            ]
            universe["recursive"] = False
            universe["source_pattern"] = "test_*.py"

        self.assert_rejected(
            mutate,
            "complete governance regression universe differs",
        )

    def test_unknown_telemetry_warning_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["supply_chain"]["telemetry_unknown_outcome"] = "warn"

        self.assert_rejected(mutate, "unknown dependency telemetry must block")

    def test_incident_without_regression_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["incident_learning"]["records"][0]["regression_test"] = (
                "governance_tests/missing_regression.py"
            )

        self.assert_rejected(
            mutate,
            "incident regression test is missing",
        )

    def test_explanation_without_unknowns_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["nontechnical_explanation"]["required_fields"].remove(
                "what_remains_unknown"
            )

        self.assert_rejected(mutate, "nontechnical explanation fields differs")

    def test_budget_exhaustion_relabelled_success_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["scope_and_budget"][
                "budget_exhaustion_cannot_be_relabelled_success"
            ] = False

        self.assert_rejected(
            mutate,
            (
                "scope and budget "
                "budget_exhaustion_cannot_be_relabelled_success must be true"
            ),
        )

    def test_live_scope_smuggling_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["scope_and_budget"]["current_forbidden"].remove(
                "live broker execution"
            )

        self.assert_rejected(mutate, "forbidden project scope differs")

    def test_component_without_removal_path_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["maintainability_and_migration"][
                "new_component_required_fields"
            ].remove("removal_path")

        self.assert_rejected(
            mutate,
            "new component maintainability fields differs",
        )

    def test_terminology_only_rewrite_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["maintainability_and_migration"][
                "rename_only_rewrite_allowed"
            ] = True

        self.assert_rejected(
            mutate,
            "terminology-only rewrites must be forbidden",
        )


if __name__ == "__main__":
    unittest.main()
