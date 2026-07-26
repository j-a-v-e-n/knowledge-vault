from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from copy import deepcopy
from datetime import date
from pathlib import Path

from scripts.verify_research_living_review import evaluate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = (
    PROJECT_ROOT / "governance" / "RESEARCH_LIVING_REVIEW_POLICY_V1.json"
)
STATE_PATH = (
    PROJECT_ROOT / "governance" / "RESEARCH_LIVING_REVIEW_STATE_V1.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ResearchLivingReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self.state = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    def test_real_candidate_is_explicitly_pending_independent_review(self) -> None:
        receipt = evaluate(
            self.policy,
            self.state,
            project_root=PROJECT_ROOT,
            as_of=date(2026, 7, 26),
        )
        self.assertEqual(receipt["verification_status"], "valid")
        self.assertEqual(
            receipt["living_review_status"],
            "blocked_pending_independent_review",
        )
        self.assertNotIn("status", receipt)

    def test_hash_mismatch_is_invalid_not_stale(self) -> None:
        state = deepcopy(self.state)
        state["latest_refresh"]["artifacts"][0]["sha256"] = "0" * 64
        receipt = evaluate(
            self.policy,
            state,
            project_root=PROJECT_ROOT,
            as_of=date(2026, 7, 26),
        )
        self.assertEqual(receipt["verification_status"], "invalid")
        self.assertEqual(receipt["living_review_status"], "invalid")

    def test_review_expiry_is_derived_from_explicit_as_of(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research = root / "research"
            audits = root / "audits"
            research.mkdir()
            audits.mkdir()
            first = research / "method.md"
            second = research / "failure.md"
            receipt_path = audits / "review.md"
            first.write_text("method", encoding="utf-8")
            second.write_text("failure", encoding="utf-8")
            receipt_path.write_text("independent review", encoding="utf-8")
            state = deepcopy(self.state)
            artifacts = [
                {"path": "research/method.md", "sha256": digest(first)},
                {"path": "research/failure.md", "sha256": digest(second)},
            ]
            state["latest_refresh"]["artifacts"] = artifacts
            state["latest_accepted_independent_review"] = {
                "review_id": "REVIEW-1",
                "completed_on": "2026-07-26",
                "candidate_bound": True,
                "reviewer_read_only": True,
                "reviewed_artifacts": artifacts,
                "receipt_path": "audits/review.md",
                "receipt_sha256": digest(receipt_path),
                "open_critical_count": 0,
                "open_major_count": 0,
            }
            current = evaluate(
                self.policy,
                state,
                project_root=root,
                as_of=date(2026, 8, 25),
            )
            stale = evaluate(
                self.policy,
                state,
                project_root=root,
                as_of=date(2026, 8, 26),
            )
            self.assertEqual(current["living_review_status"], "current")
            self.assertEqual(current["next_due"], "2026-08-25")
            self.assertEqual(stale["living_review_status"], "stale_due_to_time")

    def test_open_event_precedes_time_and_blocks_current_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research = root / "research"
            audits = root / "audits"
            evidence = root / "evidence"
            research.mkdir()
            audits.mkdir()
            evidence.mkdir()
            first = research / "method.md"
            second = research / "failure.md"
            review_path = audits / "review.md"
            event_path = evidence / "runtime-change.md"
            first.write_text("method", encoding="utf-8")
            second.write_text("failure", encoding="utf-8")
            review_path.write_text("independent review", encoding="utf-8")
            event_path.write_text("runtime changed", encoding="utf-8")
            artifacts = [
                {"path": "research/method.md", "sha256": digest(first)},
                {"path": "research/failure.md", "sha256": digest(second)},
            ]
            state = deepcopy(self.state)
            state["latest_refresh"]["artifacts"] = artifacts
            state["latest_accepted_independent_review"] = {
                "review_id": "REVIEW-1",
                "completed_on": "2026-07-26",
                "candidate_bound": True,
                "reviewer_read_only": True,
                "reviewed_artifacts": artifacts,
                "receipt_path": "audits/review.md",
                "receipt_sha256": digest(review_path),
                "open_critical_count": 0,
                "open_major_count": 0,
            }
            state["event_log"] = [
                {
                    "event_id": "EVENT-1",
                    "trigger_id": "LR-EVENT-MODEL-OR-RUNTIME",
                    "observed_on": "2026-07-27",
                    "state": "open",
                    "evidence_path": "evidence/runtime-change.md",
                    "evidence_sha256": digest(event_path),
                    "resolution_receipt_path": None,
                    "resolution_receipt_sha256": None,
                }
            ]
            receipt = evaluate(
                self.policy,
                state,
                project_root=root,
                as_of=date(2026, 7, 27),
            )
            self.assertEqual(receipt["verification_status"], "valid")
            self.assertEqual(
                receipt["living_review_status"],
                "stale_due_to_event",
            )
            self.assertEqual(receipt["open_event_ids"], ["EVENT-1"])

    def test_future_dated_review_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research = root / "research"
            audits = root / "audits"
            research.mkdir()
            audits.mkdir()
            first = research / "method.md"
            second = research / "failure.md"
            receipt_path = audits / "review.md"
            first.write_text("method", encoding="utf-8")
            second.write_text("failure", encoding="utf-8")
            receipt_path.write_text("independent review", encoding="utf-8")
            artifacts = [
                {"path": "research/method.md", "sha256": digest(first)},
                {"path": "research/failure.md", "sha256": digest(second)},
            ]
            state = deepcopy(self.state)
            state["latest_refresh"]["artifacts"] = artifacts
            state["latest_accepted_independent_review"] = {
                "review_id": "REVIEW-FUTURE",
                "completed_on": "2026-07-27",
                "candidate_bound": True,
                "reviewer_read_only": True,
                "reviewed_artifacts": artifacts,
                "receipt_path": "audits/review.md",
                "receipt_sha256": digest(receipt_path),
                "open_critical_count": 0,
                "open_major_count": 0,
            }
            receipt = evaluate(
                self.policy,
                state,
                project_root=root,
                as_of=date(2026, 7, 26),
            )
            self.assertEqual(receipt["verification_status"], "invalid")
            self.assertEqual(receipt["living_review_status"], "invalid")

    def test_resolved_event_requires_a_hashed_resolution_receipt(self) -> None:
        state = deepcopy(self.state)
        state["event_log"] = [
            {
                "event_id": "EVENT-1",
                "trigger_id": "LR-EVENT-SOURCE-REVISION",
                "observed_on": "2026-07-26",
                "state": "resolved",
                "evidence_path": state["latest_refresh"]["artifacts"][0]["path"],
                "evidence_sha256": state["latest_refresh"]["artifacts"][0][
                    "sha256"
                ],
                "resolution_receipt_path": None,
                "resolution_receipt_sha256": None,
            }
        ]
        receipt = evaluate(
            self.policy,
            state,
            project_root=PROJECT_ROOT,
            as_of=date(2026, 7, 26),
        )
        self.assertEqual(receipt["verification_status"], "invalid")
        self.assertEqual(receipt["living_review_status"], "invalid")


if __name__ == "__main__":
    unittest.main()
