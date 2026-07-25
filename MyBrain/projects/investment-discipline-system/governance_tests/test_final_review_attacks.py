from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = PROJECT_ROOT / "scripts" / "verify_governance.py"


class FinalReviewAttackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        temp_root = Path(self.temp.name)
        source_repo = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(
            source_repo.returncode,
            0,
            "canonical attack source must belong to a Git repository:\n"
            f"{source_repo.stdout}",
        )
        source_prefix = subprocess.run(
            ["git", "rev-parse", "--show-prefix"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(
            source_prefix.returncode,
            0,
            "canonical attack source must have a resolvable project prefix:\n"
            f"{source_prefix.stdout}",
        )
        repo_root = temp_root / "repository"
        clone = subprocess.run(
            [
                "git",
                "clone",
                "--shared",
                "--no-checkout",
                source_repo.stdout.strip(),
                str(repo_root),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(
            clone.returncode,
            0,
            "canonical attack fixture must retain candidate Git objects:\n"
            f"{clone.stdout}",
        )
        source_origin = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if source_origin.returncode == 0:
            restore_origin = subprocess.run(
                [
                    "git",
                    "remote",
                    "set-url",
                    "origin",
                    source_origin.stdout.strip(),
                ],
                cwd=repo_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(
                restore_origin.returncode,
                0,
                "canonical attack fixture must preserve the source origin:\n"
                f"{restore_origin.stdout}",
            )
        self.root = repo_root / source_prefix.stdout.strip()
        self.root.mkdir(parents=True, exist_ok=True)
        for directory in (
            "governance",
            "research",
            "audits",
            "scripts",
            "governance_tests",
        ):
            shutil.copytree(
                PROJECT_ROOT / directory,
                self.root / directory,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                dirs_exist_ok=True,
            )
        for relative in (
            "PRODUCT_ASSURANCE_BLUEPRINT_V2.md",
            "PROJECT_CHARTER.md",
            "DECISIONS.md",
            "README.md",
            "STATUS.md",
        ):
            shutil.copy2(PROJECT_ROOT / relative, self.root / relative)
        baseline = self.run_verifier()
        self.assertEqual(
            baseline.returncode,
            0,
            "canonical attack fixture must pass before an isolated mutation:\n"
            f"{baseline.stdout}",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict) -> None:
        (self.root / relative).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        return subprocess.run(
            [os.sys.executable, str(VERIFIER), "--allow-candidate"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def assert_rejected(self, expected_error: str) -> None:
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_error, result.stdout)

    def test_pit_oracle_inversion_is_rejected(self) -> None:
        relative = "governance/ACCEPTANCE_CASES_V1.json"
        cases = self.read_json(relative)
        case = next(
            item
            for item in cases["cases"]
            if item["id"] == "CASE-PIT-LATE-RETRIEVAL"
        )
        case["expected"]["accepted"] = True
        self.write_json(relative, cases)

        self.assert_rejected(
            "CASE-PIT-LATE-RETRIEVAL freeze-critical semantics differ"
        )

    def test_same_bar_causality_smuggle_is_rejected(self) -> None:
        relative = "governance/MARKET_SIMULATION_POLICY_V1.json"
        policy = self.read_json(relative)
        policy["calendar_and_causality"]["same_bar_fill"] = (
            "allowed by default whenever the backtest requests it"
        )
        self.write_json(relative, policy)

        self.assert_rejected("market calendar and causality semantics differ")

    def test_split_accounting_smuggle_is_rejected(self) -> None:
        relative = "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
        money = self.read_json(relative)
        split = next(
            item
            for item in money["corporate_action_matrix"]
            if item["id"] == "ACTION-SPLIT"
        )
        split["semantics"]["quantity_rule"] = "leave_quantity_unchanged"
        self.write_json(relative, money)

        self.assert_rejected("ACTION-SPLIT corporate action semantics differ")

    def test_conditional_self_attestation_is_rejected(self) -> None:
        selectors = [
            (
                "governance_tests.test_verify_conditionals.ConditionalGateTests."
                "test_round3_original_self_attestation_counterexample_is_rejected"
            ),
            (
                "governance_tests.test_verify_conditionals.ConditionalGateTests."
                "test_same_gate_run_id_reuse_after_overwrite_is_rejected"
            ),
        ]
        result = subprocess.run(
            [sys.executable, "-m", "unittest", *selectors, "-v"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_conditional_schema_self_weakening_is_rejected(self) -> None:
        relative = "governance/ACCEPTANCE_CONTRACT_V1.json"
        contract = self.read_json(relative)
        contract["conditional_evidence_schema"]["raw_result_schema"][
            "required"
        ].remove("actual_cases_run")
        self.write_json(relative, contract)

        self.assert_rejected("conditional evidence schema differs")

    def test_final_review_schema_self_weakening_is_rejected(self) -> None:
        relative = "governance/ASSURANCE_SUBJECTS_V1.json"
        assurance = self.read_json(relative)
        assurance["final_review_evidence_schema"][
            "required_attack_selectors"
        ].pop()
        self.write_json(relative, assurance)

        self.assert_rejected("assurance final review evidence schema differs")


if __name__ == "__main__":
    unittest.main()
