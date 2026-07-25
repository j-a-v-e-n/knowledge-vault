from __future__ import annotations

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
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._temporary.cleanup()

    @property
    def policy_path(self) -> Path:
        return self.root / "governance" / "PROJECT_METHOD_POLICY_V1.json"

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["IDS_PROJECT_ROOT"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--json"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def load_policy(self) -> dict[str, Any]:
        return json.loads(self.policy_path.read_text(encoding="utf-8"))

    def write_policy(self, policy: dict[str, Any]) -> None:
        self.policy_path.write_text(
            json.dumps(policy, ensure_ascii=False, indent=2) + "\n",
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

    def test_frozen_test_baseline_bypass_is_rejected(self) -> None:
        def mutate(policy: dict[str, Any]) -> None:
            policy["frozen_test_integrity"][
                "baseline_must_pass_before_mutation"
            ] = False

        self.assert_rejected(
            mutate,
            "mutation tests must first prove a passing baseline",
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
