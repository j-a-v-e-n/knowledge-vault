from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PREFIX = subprocess.run(
    ["git", "rev-parse", "--show-prefix"],
    cwd=PROJECT_ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
).stdout.strip()
REPOSITORY_ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()
)
SOURCE_HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    cwd=PROJECT_ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
).stdout.strip()


class ResearchSufficiencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name) / "repository"
        subprocess.run(
            ["git", "clone", "--shared", str(REPOSITORY_ROOT), str(self.repository)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        subprocess.run(
            ["git", "checkout", "--detach", SOURCE_HEAD],
            cwd=self.repository,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.project = self.repository / PROJECT_PREFIX
        self.receipt = (
            self.project / "governance" / "RESEARCH_SUFFICIENCY_V1.json"
        )
        self.verifier = (
            self.project / "scripts" / "verify_research_sufficiency.py"
        )
        shutil.copy2(
            PROJECT_ROOT / "scripts" / "verify_research_sufficiency.py",
            self.verifier,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def read_receipt(self) -> dict:
        return json.loads(self.receipt.read_text(encoding="utf-8"))

    def write_receipt(self, value: dict) -> None:
        self.receipt.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(self.verifier), "--json"],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def assert_rejected(self, expected: str) -> None:
        completed = self.run_verifier()
        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        self.assertIn(expected, completed.stdout)

    def test_current_bounded_incomplete_receipt_is_internally_valid(self) -> None:
        completed = self.run_verifier()
        self.assertEqual(completed.returncode, 0, completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["derived_pre_review_eligible"])
        self.assertEqual(payload["derived_research_state"], "bounded_incomplete")

    def test_free_boolean_cannot_approve_research(self) -> None:
        receipt = self.read_receipt()
        receipt["derived_closure_eligible"] = True
        self.write_receipt(receipt)
        self.assert_rejected("top-level fields differ")

    def test_declared_pre_review_result_must_equal_recomputed_result(self) -> None:
        receipt = self.read_receipt()
        receipt["derived_pre_review_eligible"] = True
        receipt["derived_research_state"] = "candidate_pre_review_eligible"
        self.write_receipt(receipt)
        self.assert_rejected("derived_pre_review_eligible was not recomputed")

    def test_final_challenge_cannot_be_smuggled_into_pre_review_expression(
        self,
    ) -> None:
        receipt = self.read_receipt()
        receipt["derivation_rules"]["pre_review_closure_expression"][
            "predicate_ids"
        ].append("DR-11")
        self.write_receipt(receipt)
        self.assert_rejected("pre-review closure expression differs")

    def test_gap_state_and_evaluation_cannot_disagree(self) -> None:
        receipt = self.read_receipt()
        receipt["open_gaps"][0]["state"] = "resolved"
        self.write_receipt(receipt)
        self.assert_rejected("current_evaluation differs")

    def test_predicate_description_cannot_silently_weaken(self) -> None:
        receipt = self.read_receipt()
        receipt["derivation_rules"]["predicates"][11][
            "test"
        ] = "trust_declared_boolean"
        self.write_receipt(receipt)
        self.assert_rejected("predicate test differs")


if __name__ == "__main__":
    unittest.main()
