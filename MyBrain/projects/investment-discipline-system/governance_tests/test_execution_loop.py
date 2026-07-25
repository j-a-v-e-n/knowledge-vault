from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_execution_loop.py"
SOURCE_POLICY = SOURCE_ROOT / "governance" / "EXECUTION_LOOP_POLICY_V1.json"
PACKET_RELATIVE = ".work_packets/packets/WP-METHOD-INTEGRATION.packet.json"
LEDGER_RELATIVE = ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json"
POLICY_RELATIVE = "governance/EXECUTION_LOOP_POLICY_V1.json"
LINKED_FAILURES = ["ECO-01", "ORG-04"]
CONTRACT_FIELDS = [
    "schema_version",
    "packet_id",
    "goal_id",
    "owner",
    "reviewer",
    "bounded_write_paths",
    "read_dependencies",
    "acceptance_checks",
    "retry_budget",
    "external_side_effects",
    "semantic_invariants",
]


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


class ExecutionLoopVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "project"
        for relative in (
            "governance",
            ".work_packets/packets",
            ".work_packets/attempts",
            ".work_packets/receipts",
            "src",
            "evidence",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_POLICY, self.root / POLICY_RELATIVE)
        self.write_text("src/output.txt", "candidate output\n")
        self.packet = self.make_packet()
        self.ledger: dict[str, Any] = {}
        self.prepare_active_fixture()

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def write_text(self, relative: str, content: str) -> Path:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def write_json(self, relative: str, value: Any) -> Path:
        return self.write_text(
            relative,
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        )

    def make_packet(self, *, retry_budget: int = 3, state: str = "active") -> dict[str, Any]:
        return {
            "schema_version": "work-packet-instance/v1",
            "packet_id": "WP-METHOD-INTEGRATION",
            "goal_id": "METHOD-GOVERNANCE-CLOSURE",
            "state": state,
            "owner": "main-agent",
            "reviewer": "independent-reviewer",
            "bounded_write_paths": [{"path": "src/output.txt", "kind": "file"}],
            "read_dependencies": [],
            "acceptance_checks": [
                {
                    "check_id": "CHECK-FOCUSED",
                    "kind": "process_exit",
                    "argv": ["python3", "-m", "unittest", "focused"],
                    "expected_exit_code": 0,
                }
            ],
            "checkpoint_path": None,
            "acceptance_receipt_path": None,
            "retry_budget": retry_budget,
            "external_side_effects": [],
            "semantic_invariants": [],
        }

    def contract_digest(self) -> str:
        return canonical_sha256(
            {field: self.packet[field] for field in CONTRACT_FIELDS}
        )

    def evidence_reference(
        self,
        relative: str,
        *,
        kind: str = "implementation",
    ) -> dict[str, Any]:
        return {
            "path": relative,
            "sha256": hashlib.sha256((self.root / relative).read_bytes()).hexdigest(),
            "kind": kind,
            "supports_failure_ids": LINKED_FAILURES,
        }

    def blocker(self, *, status: str) -> dict[str, Any]:
        value = {
            "root_cause_id": "EXECUTION-LOOP-CONTROL-GAP",
            "failure_ids": LINKED_FAILURES,
            "root_cause": (
                "The packet lacks an enforced attempt ledger and derived stop state."
            ),
            "status_after": status,
        }
        return {
            **value,
            "fingerprint_sha256": canonical_sha256(
                {
                    "root_cause_id": value["root_cause_id"],
                    "failure_ids": value["failure_ids"],
                }
            ),
        }

    def make_attempt(
        self,
        sequence: int,
        *,
        before_failures: list[str],
        after_failures: list[str],
        before_evidence: list[dict[str, Any]],
        after_evidence: list[dict[str, Any]],
        previous_sha: str | None,
        token_usage: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        before_map = {canonical_json_bytes(item): item for item in before_evidence}
        after_map = {canonical_json_bytes(item): item for item in after_evidence}
        added = [after_map[key] for key in sorted(after_map.keys() - before_map.keys())]
        removed = [before_map[key] for key in sorted(before_map.keys() - after_map.keys())]
        added.sort(key=lambda item: item["path"])
        removed.sort(key=lambda item: item["path"])
        resolved = sorted(set(before_failures) - set(after_failures))
        introduced = sorted(set(after_failures) - set(before_failures))
        started = datetime(2026, 7, 25, 18, 0, tzinfo=UTC) + timedelta(
            seconds=(sequence - 1) * 2
        )
        ended = started + timedelta(seconds=1)
        status = "resolved" if not after_failures else "open"
        if token_usage is None:
            token_usage = {
                "availability": "unknown",
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "measurement_source": None,
            }
        attempt = {
            "schema_version": "execution-attempt/v1",
            "sequence": sequence,
            "retry_index": sequence - 1,
            "started_at": started.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "ended_at": ended.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "wall_time_ms": 1000,
            "blocker": self.blocker(status=status),
            "failure_delta": {
                "before": before_failures,
                "after": after_failures,
                "resolved": resolved,
                "introduced": introduced,
            },
            "evidence_delta": {
                "before": before_evidence,
                "after": after_evidence,
                "added": added,
                "removed": removed,
            },
            "cost_observation": {
                "wall_time_source": "timestamps",
                "token_usage": token_usage,
            },
            "declared_progress": bool(added or resolved),
            "previous_attempt_sha256": previous_sha,
        }
        attempt["record_sha256"] = canonical_sha256(attempt)
        return attempt

    def make_ledger(
        self,
        attempts: list[dict[str, Any]],
        *,
        reported_state: str,
        cost_claim: str = "partial",
    ) -> dict[str, Any]:
        return {
            "schema_version": "execution-attempt-ledger/v1",
            "packet_id": "WP-METHOD-INTEGRATION",
            "packet_path": PACKET_RELATIVE,
            "packet_contract_sha256": self.contract_digest(),
            "reported_state": reported_state,
            "cost_accounting_claim": cost_claim,
            "attempts": attempts,
        }

    def rehash_attempts(self) -> None:
        previous: str | None = None
        for attempt in self.ledger["attempts"]:
            attempt["previous_attempt_sha256"] = previous
            attempt["record_sha256"] = canonical_sha256(
                {key: value for key, value in attempt.items() if key != "record_sha256"}
            )
            previous = attempt["record_sha256"]

    def persist(self) -> None:
        self.write_json(PACKET_RELATIVE, self.packet)
        self.write_json(LEDGER_RELATIVE, self.ledger)

    def prepare_active_fixture(self) -> None:
        self.write_text("evidence/mechanism.txt", "verified mechanism bytes\n")
        reference = self.evidence_reference("evidence/mechanism.txt")
        attempt = self.make_attempt(
            1,
            before_failures=LINKED_FAILURES,
            after_failures=LINKED_FAILURES,
            before_evidence=[],
            after_evidence=[reference],
            previous_sha=None,
        )
        self.packet = self.make_packet()
        self.ledger = self.make_ledger([attempt], reported_state="active")
        self.persist()

    def prepare_no_progress_attempts(self, count: int) -> None:
        attempts: list[dict[str, Any]] = []
        previous_sha: str | None = None
        for sequence in range(1, count + 1):
            attempt = self.make_attempt(
                sequence,
                before_failures=LINKED_FAILURES,
                after_failures=LINKED_FAILURES,
                before_evidence=[],
                after_evidence=[],
                previous_sha=previous_sha,
            )
            attempts.append(attempt)
            previous_sha = attempt["record_sha256"]
        self.packet = self.make_packet()
        self.ledger = self.make_ledger(attempts, reported_state="active")
        self.persist()

    def prepare_budget_exhausted_success_claim(self) -> None:
        self.packet = self.make_packet(retry_budget=1, state="complete")
        attempts: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        previous_sha: str | None = None
        for sequence in (1, 2):
            path = f"evidence/progress-{sequence}.txt"
            self.write_text(path, f"progress {sequence}\n")
            new_evidence = sorted(
                evidence + [self.evidence_reference(path)], key=lambda item: item["path"]
            )
            attempt = self.make_attempt(
                sequence,
                before_failures=LINKED_FAILURES,
                after_failures=LINKED_FAILURES,
                before_evidence=evidence,
                after_evidence=new_evidence,
                previous_sha=previous_sha,
            )
            attempts.append(attempt)
            evidence = new_evidence
            previous_sha = attempt["record_sha256"]
        self.ledger = self.make_ledger(attempts, reported_state="complete")
        self.persist()

    def prepare_complete_fixture(
        self,
        *,
        attempt_count: int,
        retry_budget: int,
        actual_exit_code: int = 0,
    ) -> None:
        self.packet = self.make_packet(retry_budget=retry_budget, state="complete")
        checkpoint_relative = (
            ".work_packets/receipts/WP-METHOD-INTEGRATION.checkpoint.json"
        )
        acceptance_relative = (
            ".work_packets/receipts/WP-METHOD-INTEGRATION.acceptance.json"
        )
        self.packet["checkpoint_path"] = checkpoint_relative
        self.packet["acceptance_receipt_path"] = acceptance_relative
        contract = self.contract_digest()
        checkpoint = {
            "schema_version": "work-packet-checkpoint/v1",
            "packet_id": "WP-METHOD-INTEGRATION",
            "packet_contract_sha256": contract,
            "sequence": attempt_count,
            "snapshots": [
                {
                    "path": "src/output.txt",
                    "kind": "file",
                    "state": "file",
                    "content_sha256": hashlib.sha256(
                        (self.root / "src/output.txt").read_bytes()
                    ).hexdigest(),
                }
            ],
        }
        acceptance = {
            "schema_version": "work-packet-acceptance/v1",
            "packet_id": "WP-METHOD-INTEGRATION",
            "packet_contract_sha256": contract,
            "checkpoint_receipt_sha256": canonical_sha256(checkpoint),
            "checks": [
                {
                    "check_id": "CHECK-FOCUSED",
                    "actual_exit_code": actual_exit_code,
                }
            ],
        }
        self.write_json(checkpoint_relative, checkpoint)
        self.write_json(acceptance_relative, acceptance)

        attempts: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        previous_sha: str | None = None
        for sequence in range(1, attempt_count + 1):
            path = f"evidence/step-{sequence}.txt"
            self.write_text(path, f"step {sequence}\n")
            additions = [self.evidence_reference(path)]
            if sequence == attempt_count:
                additions.extend(
                    [
                        self.evidence_reference(
                            checkpoint_relative, kind="checkpoint_receipt"
                        ),
                        self.evidence_reference(
                            acceptance_relative, kind="acceptance_receipt"
                        ),
                    ]
                )
            new_evidence = sorted(evidence + additions, key=lambda item: item["path"])
            after_failures = [] if sequence == attempt_count else LINKED_FAILURES
            attempt = self.make_attempt(
                sequence,
                before_failures=LINKED_FAILURES,
                after_failures=after_failures,
                before_evidence=evidence,
                after_evidence=new_evidence,
                previous_sha=previous_sha,
            )
            attempts.append(attempt)
            evidence = new_evidence
            previous_sha = attempt["record_sha256"]
        self.ledger = self.make_ledger(attempts, reported_state="complete")
        self.persist()

    def run_verifier(self) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--project-root",
                str(self.root),
                "--policy",
                POLICY_RELATIVE,
                "--packet",
                PACKET_RELATIVE,
                "--ledger",
                LEDGER_RELATIVE,
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"verifier did not emit one JSON object: {exc}\n"
                f"stdout={completed.stdout}\nstderr={completed.stderr}"
            )
        return completed, payload

    def assert_passes(self) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(0, completed.returncode, payload)
        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual([], payload["errors"])
        return payload

    def assert_rejected(self, expected_error: str) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(1, completed.returncode, payload)
        self.assertEqual("fail", payload["status"], payload)
        self.assertTrue(
            any(expected_error in error for error in payload["errors"]),
            payload["errors"],
        )
        return payload

    def test_current_active_attempt_is_derived_and_unknown_cost_stays_partial(self) -> None:
        payload = self.assert_passes()
        self.assertEqual("active", payload["derived_state"])
        self.assertEqual(1, payload["attempt_count"])
        self.assertEqual(1, payload["progress_attempt_count"])
        self.assertEqual("partial", payload["cost_accounting"])
        self.assertFalse(payload["acceptance_verified"])

    def test_forged_progress_claim_is_rejected_after_hash_chain_is_repaired(self) -> None:
        attempt = self.ledger["attempts"][0]
        attempt["evidence_delta"] = {
            "before": [],
            "after": [],
            "added": [],
            "removed": [],
        }
        self.rehash_attempts()
        self.persist()

        self.assert_rejected("declared_progress: differs from derived progress False")

    def test_missing_sequence_is_rejected_even_with_rehashed_records(self) -> None:
        self.prepare_no_progress_attempts(2)
        self.ledger["attempts"][1]["sequence"] = 3
        self.rehash_attempts()
        self.persist()

        self.assert_rejected("sequence: must be contiguous and equal 2")

    def test_reordered_time_interval_is_rejected(self) -> None:
        self.prepare_no_progress_attempts(2)
        second = self.ledger["attempts"][1]
        second["started_at"] = "2026-07-25T18:00:00.500Z"
        second["ended_at"] = "2026-07-25T18:00:01.500Z"
        self.rehash_attempts()
        self.persist()

        self.assert_rejected("attempts overlap or are reordered")

    def test_three_same_blocker_no_progress_attempts_cannot_remain_active(self) -> None:
        self.prepare_no_progress_attempts(3)

        payload = self.assert_rejected("active differs from derived blocked")
        self.assertEqual("blocked", payload["derived_state"])
        self.assertEqual(3, payload["consecutive_same_blocker_no_progress"])

    def test_attempt_after_mandatory_same_blocker_stop_is_rejected(self) -> None:
        self.prepare_no_progress_attempts(4)

        self.assert_rejected("attempt continued after mandatory block at sequence 3")

    def test_budget_exhaustion_without_receipts_cannot_be_called_complete(self) -> None:
        self.prepare_budget_exhausted_success_claim()

        payload = self.assert_rejected(
            "budget or no-progress exhaustion cannot be relabelled complete"
        )
        self.assertEqual("blocked", payload["derived_state"])

    def test_retry_above_budget_cannot_complete_even_with_valid_receipts(self) -> None:
        self.prepare_complete_fixture(attempt_count=3, retry_budget=1)

        payload = self.assert_rejected("exceeds packet retry_budget 1")
        self.assertEqual("blocked", payload["derived_state"])

    def test_unknown_token_cost_cannot_be_claimed_measured(self) -> None:
        self.ledger["cost_accounting_claim"] = "measured"
        self.persist()

        self.assert_rejected("cost_accounting_claim: differs from derived partial")

    def test_unknown_token_observation_cannot_contain_fake_measurement(self) -> None:
        token = self.ledger["attempts"][0]["cost_observation"]["token_usage"]
        token["total_tokens"] = 100
        token["measurement_source"] = "estimated"
        self.rehash_attempts()
        self.persist()

        self.assert_rejected("unknown telemetry requires null counts and source")

    def test_measured_token_cost_requires_consistent_counts_and_source(self) -> None:
        token = self.ledger["attempts"][0]["cost_observation"]["token_usage"]
        token.update(
            {
                "availability": "measured",
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "measurement_source": "fixture-platform-usage-receipt",
            }
        )
        self.ledger["cost_accounting_claim"] = "measured"
        self.rehash_attempts()
        self.persist()

        payload = self.assert_passes()
        self.assertEqual("measured", payload["cost_accounting"])

    def test_receipt_contract_hash_decoupling_is_rejected(self) -> None:
        self.prepare_complete_fixture(attempt_count=1, retry_budget=2)
        acceptance_path = self.root / ".work_packets/receipts/WP-METHOD-INTEGRATION.acceptance.json"
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
        acceptance["packet_contract_sha256"] = "0" * 64
        self.write_json(
            ".work_packets/receipts/WP-METHOD-INTEGRATION.acceptance.json",
            acceptance,
        )
        receipt_reference = next(
            item
            for item in self.ledger["attempts"][-1]["evidence_delta"]["after"]
            if item["kind"] == "acceptance_receipt"
        )
        receipt_reference["sha256"] = hashlib.sha256(acceptance_path.read_bytes()).hexdigest()
        added_reference = next(
            item
            for item in self.ledger["attempts"][-1]["evidence_delta"]["added"]
            if item["kind"] == "acceptance_receipt"
        )
        added_reference["sha256"] = receipt_reference["sha256"]
        self.rehash_attempts()
        self.persist()

        self.assert_rejected("acceptance receipt: packet contract digest differs")

    def test_failed_acceptance_exit_code_cannot_complete(self) -> None:
        self.prepare_complete_fixture(
            attempt_count=1,
            retry_budget=2,
            actual_exit_code=1,
        )

        self.assert_rejected("actual exit 1 does not equal expected 0")

    def test_valid_bound_acceptance_within_budget_can_derive_complete(self) -> None:
        self.prepare_complete_fixture(attempt_count=2, retry_budget=2)

        payload = self.assert_passes()
        self.assertEqual("complete", payload["derived_state"])
        self.assertTrue(payload["acceptance_verified"])
        self.assertEqual(1, payload["highest_retry_index"])

    def test_duplicate_json_key_is_rejected(self) -> None:
        encoded = json.dumps(self.ledger, ensure_ascii=False)
        encoded = encoded.replace(
            '"reported_state": "active"',
            '"reported_state": "active", "reported_state": "complete"',
            1,
        )
        self.write_text(LEDGER_RELATIVE, encoded + "\n")

        self.assert_rejected("duplicate JSON key 'reported_state'")

    def test_packet_contract_change_invalidates_ledger_binding(self) -> None:
        self.packet["acceptance_checks"][0]["argv"].append("--changed")
        self.write_json(PACKET_RELATIVE, self.packet)

        self.assert_rejected(
            "ledger.packet_contract_sha256: differs from current packet contract"
        )

    def test_no_progress_threshold_cannot_be_weakened_in_policy(self) -> None:
        policy_path = self.root / POLICY_RELATIVE
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["stopping_rules"][
            "same_blocker_consecutive_no_progress_threshold"
        ] = 4
        self.write_json(POLICY_RELATIVE, policy)

        self.assert_rejected("policy.stopping_rules: frozen value differs")

    def test_attempt_content_change_without_rehash_is_rejected(self) -> None:
        self.ledger["attempts"][0]["blocker"]["root_cause"] = "Rewritten after the fact."
        self.persist()

        self.assert_rejected("record_sha256: differs from canonical attempt")


if __name__ == "__main__":
    unittest.main()
