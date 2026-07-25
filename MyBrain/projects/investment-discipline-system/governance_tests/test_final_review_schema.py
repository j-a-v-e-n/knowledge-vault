from __future__ import annotations

import copy
import hashlib
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
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
ASSURANCE_RELATIVE = "governance/ASSURANCE_SUBJECTS_V1.json"
EVIDENCE_RELATIVE = "audits/FINAL_REVIEW_SCHEMA_FIXTURE.json"
SUBJECT_ID = "SUBJECT-DESIGN-REVIEW-SCHEMA-FIXTURE"
ATTACK_SELECTORS = {
    "ATTACK-PIT-ORACLE-INVERSION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_pit_oracle_inversion_is_rejected"
    ),
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_same_bar_causality_smuggle_is_rejected"
    ),
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_split_accounting_smuggle_is_rejected"
    ),
    "ATTACK-CONDITIONAL-SELF-ATTESTATION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_conditional_self_attestation_is_rejected"
    ),
}
REQUIRED_REVIEW_SCOPE = {
    "scripts/verify_governance.py",
    "scripts/verify_conditionals.py",
    "scripts/freeze_governance.py",
    "scripts/verify_git_state.py",
    "scripts/verify_remote_commit.py",
    "scripts/replay_design_freeze_attacks.py",
    "governance_tests/test_final_review_attacks.py",
    "governance_tests/test_verify_conditionals.py",
    "governance_tests/test_freeze_git_remote.py",
}


def digest_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class FinalReviewSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        shutil.copytree(
            PROJECT_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        self.run_git("init", "--initial-branch=main")
        self.run_git("config", "user.name", "Final Review Schema Test")
        self.run_git(
            "config", "user.email", "final-review-schema@example.invalid"
        )
        self.run_git("add", ".")
        self.run_git("commit", "-m", "candidate fixture")
        self.candidate_commit = self.git_text("rev-parse", "HEAD")
        self.candidate_tree = self.git_text(
            "rev-parse", f"{self.candidate_commit}^{{tree}}"
        )
        self.install_passing_review()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            self.fail(f"git {' '.join(args)} failed:\n{result.stdout}")
        return result

    def git_text(self, *args: str) -> str:
        return self.run_git(*args).stdout.strip()

    def read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        return subprocess.run(
            [sys.executable, str(VERIFIER), "--allow-candidate"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def evidence_hash(self) -> str:
        return hashlib.sha256((self.root / EVIDENCE_RELATIVE).read_bytes()).hexdigest()

    def synchronize_evidence_bindings(self) -> None:
        evidence_hash = self.evidence_hash()
        research = self.read_json(RESEARCH_RELATIVE)
        final_round = research["challenge"]["rounds"][-1]
        final_round["evidence_sha256"] = evidence_hash
        artifact = research["primary_artifacts"][-1]
        artifact["sha256"] = evidence_hash
        self.write_json(RESEARCH_RELATIVE, research)

        assurance = self.read_json(ASSURANCE_RELATIVE)
        assurance["subjects"][-1]["evidence_sha256"] = evidence_hash
        self.write_json(ASSURANCE_RELATIVE, assurance)

    def install_passing_review(self) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        reviewed_files = sorted(
            set(contract["change_control"]["frozen_files"]) | REQUIRED_REVIEW_SCOPE
        )
        attacks: list[dict] = []
        for index, (attack_id, selector) in enumerate(ATTACK_SELECTORS.items(), 1):
            mutation = f"canonical isolated mutation {index}: {attack_id}"
            expected = "the target verifier rejects the isolated mutation"
            observed = "target exit code was nonzero and named the violated invariant"
            raw_relative = f"audits/final_review_attacks/{index:02d}.json"
            raw = {
                "schema_version": 1,
                "attack_id": attack_id,
                "candidate_commit": self.candidate_commit,
                "candidate_tree": self.candidate_tree,
                "mutation_sha256": digest_text(mutation),
                "replay_selector": selector,
                "command": f"python3 -m unittest {selector}",
                "exit_code": 1,
                "stdout": observed,
                "stdout_sha256": digest_text(observed),
                "expected": expected,
                "observed": observed,
                "result": "rejected",
            }
            self.write_json(raw_relative, raw)
            attacks.append(
                {
                    "attack_id": attack_id,
                    "mutation": mutation,
                    "mutation_sha256": digest_text(mutation),
                    "expected": expected,
                    "observed": observed,
                    "result": "rejected",
                    "replay_selector": selector,
                    "raw_result_path": raw_relative,
                    "raw_result_sha256": hashlib.sha256(
                        (self.root / raw_relative).read_bytes()
                    ).hexdigest(),
                }
            )

        review_input = (
            "Review the exact candidate and try the canonical independent attacks. "
            "Pass only when every attack is rejected and all findings are reconciled."
        )
        evidence = {
            "schema_version": 1,
            "subject_id": SUBJECT_ID,
            "review_locator": "test-fixture:strict-final-review-schema",
            "review_input": review_input,
            "review_input_sha256": digest_text(review_input),
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "verdict": "passed_freeze",
            "open_critical_count": 0,
            "open_major_count": 0,
            "open_minor_count": 0,
            "new_architecture_changing_classes": [],
            "participated_in_candidate_construction": False,
            "write_access_used": False,
            "reviewed_files": reviewed_files,
            "commands_run": [
                f"python3 -m unittest {selector}"
                for selector in ATTACK_SELECTORS.values()
            ],
            "independent_attacks": attacks,
            "findings": [],
            "finding_ids": [],
            "what_would_falsify_pass": [
                "one canonical attack escapes its target verifier"
            ],
            "limitations": [
                "local process ownership cannot prove cryptographic human identity"
            ],
        }
        self.write_json(EVIDENCE_RELATIVE, evidence)
        evidence_hash = self.evidence_hash()

        research = self.read_json(RESEARCH_RELATIVE)
        research["status"] = "adopted_with_explicit_limits"
        research["challenge"]["status"] = "completed"
        research["challenge"]["rounds"].append(
            {
                "id": "CHALLENGE-FINAL-SCHEMA-FIXTURE",
                "candidate_commit": self.candidate_commit,
                "candidate_tree": self.candidate_tree,
                "reviewer_subjects": [SUBJECT_ID],
                "result": "passed_freeze",
                "evidence_path": EVIDENCE_RELATIVE,
                "evidence_sha256": evidence_hash,
                "new_architecture_changing_classes": [],
                "critical_findings": [],
                "major_findings": [],
                "open_critical_count": 0,
                "open_major_count": 0,
                "open_minor_count": 0,
                "finding_ids": [],
                "disposition": "strict machine-readable review evidence passed",
            }
        )
        research["stop_rule"]["met"] = True
        research["primary_artifacts"].append(
            {
                "id": "ARTIFACT-CHALLENGE-FINAL-R99",
                "path": EVIDENCE_RELATIVE,
                "sha256": evidence_hash,
                "role": "independent_final_challenge",
            }
        )
        self.write_json(RESEARCH_RELATIVE, research)

        assurance = self.read_json(ASSURANCE_RELATIVE)
        assurance["subjects"].append(
            {
                "id": SUBJECT_ID,
                "role": "design_reviewer",
                "locator": evidence["review_locator"],
                "candidate_commit": self.candidate_commit,
                "candidate_tree": self.candidate_tree,
                "write_access_used": False,
                "participated_in_candidate_construction": False,
                "verdict": "passed_freeze",
                "evidence_path": EVIDENCE_RELATIVE,
                "evidence_sha256": evidence_hash,
            }
        )
        self.write_json(ASSURANCE_RELATIVE, assurance)

    def mutate_evidence(self, mutation) -> None:
        evidence = self.read_json(EVIDENCE_RELATIVE)
        mutation(evidence)
        self.write_json(EVIDENCE_RELATIVE, evidence)
        self.synchronize_evidence_bindings()

    def assert_rejected(self, expected_error: str) -> None:
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_error, result.stdout)

    def test_complete_strict_review_evidence_passes(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_canonical_attack_is_rejected(self) -> None:
        self.mutate_evidence(lambda evidence: evidence["independent_attacks"].pop())
        self.assert_rejected("passing review attack coverage differs")

    def test_escaped_attack_is_rejected(self) -> None:
        def mutate(evidence: dict) -> None:
            evidence["independent_attacks"][0]["result"] = "escaped"

        self.mutate_evidence(mutate)
        self.assert_rejected("did not produce a rejected attack")

    def test_raw_result_hash_mismatch_is_rejected(self) -> None:
        self.mutate_evidence(
            lambda evidence: evidence["independent_attacks"][0].update(
                {"raw_result_sha256": "0" * 64}
            )
        )
        self.assert_rejected("raw result sha256 mismatch")

    def test_cross_candidate_raw_result_is_rejected(self) -> None:
        evidence = self.read_json(EVIDENCE_RELATIVE)
        raw_relative = evidence["independent_attacks"][0]["raw_result_path"]
        raw = self.read_json(raw_relative)
        raw["candidate_commit"] = "0" * 40
        self.write_json(raw_relative, raw)
        evidence["independent_attacks"][0]["raw_result_sha256"] = hashlib.sha256(
            (self.root / raw_relative).read_bytes()
        ).hexdigest()
        self.write_json(EVIDENCE_RELATIVE, evidence)
        self.synchronize_evidence_bindings()
        self.assert_rejected("raw result candidate_commit differs")

    def test_finding_count_mismatch_is_rejected(self) -> None:
        self.mutate_evidence(
            lambda evidence: evidence.update({"open_minor_count": 1})
        )
        self.assert_rejected("evidence open_minor_count differs")

    def test_open_minor_finding_cannot_be_called_passing(self) -> None:
        evidence = self.read_json(EVIDENCE_RELATIVE)
        evidence["open_minor_count"] = 1
        evidence["finding_ids"] = ["FINAL-MINOR-001"]
        evidence["findings"] = [
            {
                "id": "FINAL-MINOR-001",
                "severity": "minor",
                "status": "open",
                "title": "A real open limitation remains",
                "evidence": "The final review has not closed this observation.",
            }
        ]
        self.write_json(EVIDENCE_RELATIVE, evidence)
        self.synchronize_evidence_bindings()
        research = self.read_json(RESEARCH_RELATIVE)
        final_round = research["challenge"]["rounds"][-1]
        final_round["open_minor_count"] = 1
        final_round["finding_ids"] = ["FINAL-MINOR-001"]
        self.write_json(RESEARCH_RELATIVE, research)

        self.assert_rejected("passed with open review findings")

    def test_omitted_verifier_scope_is_rejected(self) -> None:
        def mutate(evidence: dict) -> None:
            evidence["reviewed_files"].remove("scripts/verify_conditionals.py")

        self.mutate_evidence(mutate)
        self.assert_rejected("passing review omitted required files")


if __name__ == "__main__":
    unittest.main()
