from __future__ import annotations

import copy
import hashlib
import inspect
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest import mock

from scripts import derive_project_state as project_state
from scripts import record_execution_attempt_v2 as recorder
from scripts import verify_execution_loop_v2 as execution
from scripts import verify_work_packets as work_packets


SOURCE_ROOT = Path(__file__).resolve().parents[1]
RECORDER_SCRIPT = SOURCE_ROOT / "scripts" / "record_execution_attempt_v2.py"
EXECUTION_POLICY = Path("governance/EXECUTION_LOOP_POLICY_V2.json")
WORK_PACKET_POLICY = Path("governance/WORK_PACKET_POLICY_V2.json")
PROJECT_STATE_POLICY = Path("governance/PROJECT_STATE_VIEW_POLICY_V1.json")
PACKET_DIRECTORY = Path(".work_packets/packets")
TARGET_ID = "WP-METHOD-RUNTIME-FOUNDATION"
SUCCESSOR_ID = "WP-RECORDER-SUCCESSOR"
EXEMPT_ID = "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY"
TARGET_OUTPUT = "src/recorder-target.txt"
SUCCESSOR_OUTPUT = "src/recorder-successor.txt"
VIEW_PATHS = ("STATUS.md", "TASK_BOARD.md", "LOOP_RUN_LOG.md")
FINALIZE_STDOUT = b"acceptance-out\n"
FINALIZE_STDERR = b"acceptance-err\n"


class ExecutionRecorderV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "project"
        self.root.mkdir()
        self.root = self.root.resolve()
        self._build_fixture()

        work_receipt = self.work_receipt()
        self.assertEqual("pass", work_receipt["status"], work_receipt)
        execution_receipt = self.execution_receipt()
        self.assertEqual(
            "valid",
            execution_receipt["verification_status"],
            execution_receipt,
        )
        self.assertEqual(
            "current",
            execution_receipt["execution_freshness_status"],
            execution_receipt,
        )
        project_state.refresh_project_state(self.root)
        project_state.check_project_state(self.root)

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def write_bytes(self, relative: str, content: bytes) -> Path:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def write_text(self, relative: str, content: str) -> Path:
        return self.write_bytes(relative, content.encode("utf-8"))

    def write_json(self, relative: str, value: Any) -> Path:
        return self.write_bytes(relative, recorder.canonical_bytes(value))

    def read_json(self, relative: str) -> dict[str, Any]:
        value = json.loads((self.root / relative).read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def copy_source(self, relative: str) -> None:
        source = SOURCE_ROOT / relative
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    def packet_path(self, packet_id: str) -> str:
        return f".work_packets/packets/{packet_id}.packet.json"

    def ledger_relative(self, packet_id: str) -> str:
        return execution.ledger_path_for(packet_id)

    def ledger(self, packet_id: str = TARGET_ID) -> dict[str, Any]:
        return self.read_json(self.ledger_relative(packet_id))

    def tail(self, packet_id: str = TARGET_ID) -> str:
        value = recorder.tail_sha256(self.ledger(packet_id))
        self.assertIsInstance(value, str)
        return value

    def project_files(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in sorted(self.root.rglob("*"))
            if path.is_file()
        }

    def work_receipt(self) -> dict[str, Any]:
        return work_packets.verify(
            self.root,
            self.root / WORK_PACKET_POLICY,
            self.root / PACKET_DIRECTORY,
        )

    def execution_receipt(self) -> dict[str, Any]:
        return execution.verify(self.root, EXECUTION_POLICY)

    def assert_execution_current(self) -> dict[str, Any]:
        receipt = self.execution_receipt()
        self.assertEqual("valid", receipt["verification_status"], receipt)
        self.assertEqual(
            "current",
            receipt["execution_freshness_status"],
            receipt,
        )
        self.assertEqual([], receipt["errors"], receipt)
        return receipt

    def assert_execution_invalid(self, expected: str) -> dict[str, Any]:
        receipt = self.execution_receipt()
        self.assertEqual("invalid", receipt["verification_status"], receipt)
        self.assertTrue(
            any(expected in error for error in receipt["errors"]),
            receipt["errors"],
        )
        return receipt

    def target_packet(self) -> dict[str, Any]:
        check_id = "CHECK-RECORDER-TARGET"
        return {
            "schema_version": "work-packet-instance/v2",
            "packet_id": TARGET_ID,
            "goal_id": "METHOD-GOVERNANCE-CLOSURE",
            "state": "active",
            "owner": "recorder-fixture",
            "reviewer": "recorder-test",
            "bounded_write_paths": [
                {"path": TARGET_OUTPUT, "kind": "file"}
            ],
            "read_dependencies": [
                "governance_tests/test_contract_supersession.py"
            ],
            "acceptance_checks": [
                {
                    "check_id": check_id,
                    "kind": "process_exit",
                    "argv": [
                        sys.executable,
                        "-c",
                        (
                            "import os; "
                            f"os.write(1, {FINALIZE_STDOUT!r}); "
                            f"os.write(2, {FINALIZE_STDERR!r})"
                        ),
                    ],
                    "expected_exit_code": 0,
                }
            ],
            "checkpoint_path": None,
            "acceptance_receipt_path": None,
            "retry_budget": 8,
            "external_side_effects": [],
            "semantic_invariants": [],
            "depends_on": [EXEMPT_ID],
            "activates": [SUCCESSOR_ID],
            "integration_invariants": [
                {
                    "invariant_id": "INV-RECORDER-TARGET-PREREQUISITE",
                    "inputs": [
                        {
                            "packet_id": EXEMPT_ID,
                            "path": (
                                "governance_tests/"
                                "test_contract_supersession.py"
                            ),
                        }
                    ],
                    "probe_check_ids": [check_id],
                }
            ],
            "routing": {
                "phase_id": "design_freeze",
                "action_id": "ACT-METHOD-RUNTIME-FOUNDATION",
                "route_order": 10,
                "addresses_finding_ids": ["F-RECORDER"],
                "summary": "Exercise the V2 execution recorder",
            },
        }

    def successor_packet(self) -> dict[str, Any]:
        check_id = "CHECK-RECORDER-SUCCESSOR"
        return {
            "schema_version": "work-packet-instance/v2",
            "packet_id": SUCCESSOR_ID,
            "goal_id": "METHOD-GOVERNANCE-CLOSURE",
            "state": "pending",
            "owner": "recorder-fixture",
            "reviewer": "recorder-test",
            "bounded_write_paths": [
                {"path": SUCCESSOR_OUTPUT, "kind": "file"}
            ],
            "read_dependencies": [TARGET_OUTPUT],
            "acceptance_checks": [
                {
                    "check_id": check_id,
                    "kind": "process_exit",
                    "argv": [sys.executable, "-c", "raise SystemExit(0)"],
                    "expected_exit_code": 0,
                }
            ],
            "checkpoint_path": None,
            "acceptance_receipt_path": None,
            "retry_budget": 8,
            "external_side_effects": [],
            "semantic_invariants": [],
            "depends_on": [TARGET_ID],
            "activates": [],
            "integration_invariants": [
                {
                    "invariant_id": "INV-RECORDER-SUCCESSOR-INPUT",
                    "inputs": [
                        {"packet_id": TARGET_ID, "path": TARGET_OUTPUT}
                    ],
                    "probe_check_ids": [check_id],
                }
            ],
            "routing": {
                "phase_id": "design_freeze",
                "action_id": "ACT-RECORDER-SUCCESSOR",
                "route_order": 20,
                "addresses_finding_ids": ["F-RECORDER"],
                "summary": "Continue after recorder finalization",
            },
        }

    def baseline_ledger(self, packet: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        excluded, claims = execution.current_claim_snapshots(
            self.root.resolve(),
            packet,
            {EXEMPT_ID, TARGET_ID, SUCCESSOR_ID},
            errors,
        )
        self.assertEqual([], errors)
        blocker = {
            "root_cause_id": "RECORDER-BASELINE",
            "failure_ids": [],
            "root_cause": "Initial recorder fixture observation",
            "status_after": "waiting",
        }
        blocker["fingerprint_sha256"] = execution.canonical_sha256(
            {
                "root_cause_id": blocker["root_cause_id"],
                "failure_ids": blocker["failure_ids"],
                "root_cause": blocker["root_cause"],
            }
        )
        attempt = {
            "schema_version": "execution-attempt/v2",
            "attempt_kind": "baseline_observation",
            "sequence": 1,
            "retry_index": None,
            "started_at": "2026-07-25T00:00:00.000Z",
            "ended_at": "2026-07-25T00:00:00.000Z",
            "wall_time_ms": 0,
            "blocker": blocker,
            "failure_delta": {
                "before": [],
                "after": [],
                "resolved": [],
                "introduced": [],
            },
            "evidence_delta": {
                "before": [],
                "after": [],
                "added": [],
                "removed": [],
            },
            "controlled_snapshot": {
                "algorithm": execution.EXPECTED_CURRENT_SNAPSHOT["algorithm"],
                "excluded_paths": excluded,
                "claims": claims,
                "claims_sha256": execution.canonical_sha256(claims),
            },
            "process_observation": recorder.no_process_observation("baseline"),
            "cost_observation": recorder.unknown_cost(),
            "declared_progress": False,
            "previous_attempt_sha256": None,
            "record_sha256": "",
        }
        attempt["record_sha256"] = execution.canonical_sha256(
            {
                key: value
                for key, value in attempt.items()
                if key != "record_sha256"
            }
        )
        return {
            "schema_version": "execution-attempt-ledger/v2",
            "packet_id": packet["packet_id"],
            "packet_path": self.packet_path(packet["packet_id"]),
            "packet_contract_sha256": work_packets.packet_contract_sha256(
                packet
            ),
            "reported_state": packet["state"],
            "cost_accounting_claim": "partial",
            "initial_state": {"failure_ids": [], "evidence": []},
            "terminal_completion": None,
            "attempts": [attempt],
        }

    def _build_fixture(self) -> None:
        for relative in (
            EXECUTION_POLICY.as_posix(),
            WORK_PACKET_POLICY.as_posix(),
            PROJECT_STATE_POLICY.as_posix(),
            "governance/EXECUTION_LOOP_POLICY_V1.json",
            "scripts/verify_execution_loop.py",
            ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json",
            self.packet_path(EXEMPT_ID),
            f".work_packets/receipts/{EXEMPT_ID}.checkpoint.json",
            f".work_packets/receipts/{EXEMPT_ID}.acceptance.json",
            "governance_tests/test_contract_supersession.py",
            "scripts/verify_contract_supersession.py",
            "governance/PROJECT_METHOD_POLICY_V1.json",
            "governance/WORK_PACKET_POLICY_V1.json",
        ):
            self.copy_source(relative)

        self.write_json(
            "governance/ACCEPTANCE_CONTRACT_V1.json",
            {
                "schema_version": 1,
                "contract_id": "recorder-fixture-v1",
                "status": "candidate_under_challenge",
                "change_control": {
                    "closure_mutation_policy": {
                        "freeze_state_authority": (
                            "governance/FROZEN_BUNDLE_V1.json"
                        )
                    }
                },
            },
        )
        self.write_json(
            "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json",
            {
                "challenge": {
                    "rounds": [
                        {
                            "id": "CHALLENGE-10",
                            "review_sequence": 10,
                            "candidate_commit": "a" * 40,
                            "candidate_tree": "b" * 40,
                            "result": "blocked_freeze",
                            "evidence_path": "audits/recorder-fixture.md",
                            "evidence_sha256": "c" * 64,
                            "findings": [
                                {
                                    "finding_id": "F-RECORDER",
                                    "severity": "critical",
                                    "state": "open",
                                    "required_action_ids": [
                                        "ACT-METHOD-RUNTIME-FOUNDATION",
                                        "ACT-RECORDER-SUCCESSOR",
                                    ],
                                }
                            ],
                        }
                    ]
                }
            },
        )
        self.write_text(TARGET_OUTPUT, "target-v1\n")
        self.write_text(SUCCESSOR_OUTPUT, "successor-v1\n")

        target = self.target_packet()
        successor = self.successor_packet()
        self.write_json(self.packet_path(TARGET_ID), target)
        self.write_json(self.packet_path(SUCCESSOR_ID), successor)
        self.write_json(self.ledger_relative(TARGET_ID), self.baseline_ledger(target))
        self.write_json(
            self.ledger_relative(SUCCESSOR_ID),
            self.baseline_ledger(successor),
        )
        for view in VIEW_PATHS:
            self.write_text(
                view,
                (
                    f"# fixture {view}\n"
                    "<!-- PROJECT_STATE_VIEW:START -->\n"
                    "{}\n"
                    "<!-- PROJECT_STATE_VIEW:END -->\n"
                ),
            )

    def append_passive(
        self,
        *,
        status_after: str = "open",
        failure_after: list[str] | None = None,
        expected_tail: str | None = None,
        crash_after_replacements: int | None = None,
    ) -> dict[str, Any]:
        return recorder.append_passive(
            self.root,
            TARGET_ID,
            self.tail() if expected_tail is None else expected_tail,
            failure_after,
            status_after,
            "RECORDER-OBSERVATION",
            "Recorder fixture observation",
            crash_after_replacements=crash_after_replacements,
        )

    def record_resolved(self) -> dict[str, Any]:
        return self.append_passive(status_after="resolved")

    def finalize_with_consistent_clock(self) -> dict[str, Any]:
        self.record_resolved()
        with mock.patch.object(
            recorder,
            "utc_datetime_milliseconds",
            side_effect=[
                datetime(2026, 7, 25, 1, 0, 0, tzinfo=UTC),
                datetime(2026, 7, 25, 1, 0, 0, 125000, tzinfo=UTC),
            ],
        ):
            return recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
            )

    def test_wrong_expected_tail_cas_changes_no_project_file(self) -> None:
        before = self.project_files()
        with self.assertRaisesRegex(recorder.RecorderError, "expected-tail CAS"):
            self.append_passive(expected_tail="0" * 64)
        self.assertEqual(before, self.project_files())

    def test_two_concurrent_recorders_with_same_tail_have_one_winner(self) -> None:
        expected_tail = self.tail()
        barrier = Path(self._temporary.name) / "recorder-barrier"
        worker = (
            "import os, pathlib, sys, time; "
            "barrier = pathlib.Path(sys.argv[1]); "
            "worker_id = sys.argv[2]; "
            "barrier.mkdir(parents=True, exist_ok=True); "
            "(barrier / worker_id).write_text('ready'); "
            "deadline = time.monotonic() + 10; "
            "\nwhile len(list(barrier.iterdir())) < 2:\n"
            "    if time.monotonic() >= deadline: raise SystemExit(98)\n"
            "    time.sleep(0.005)\n"
            "os.execv(sys.executable, [sys.executable, *sys.argv[3:]])"
        )
        recorder_args = [
            str(RECORDER_SCRIPT),
            "--project-root",
            str(self.root),
            "append",
            "--packet-id",
            TARGET_ID,
            "--expected-tail",
            expected_tail,
            "--status-after",
            "open",
            "--root-cause-id",
            "RECORDER-CONCURRENT",
            "--root-cause",
            "Concurrent recorder fixture",
        ]
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    "-c",
                    worker,
                    str(barrier),
                    str(index),
                    *recorder_args,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(2)
        ]
        completed = [
            (process.returncode, stdout, stderr)
            for process in processes
            for stdout, stderr in [process.communicate(timeout=30)]
        ]
        return_codes = sorted(item[0] for item in completed)
        self.assertEqual([0, 1], return_codes, completed)
        payloads = [json.loads(item[1]) for item in completed]
        winner = next(payload for payload in payloads if payload["status"] != "fail")
        loser = next(payload for payload in payloads if payload["status"] == "fail")
        self.assertEqual("recorded", winner["status"])
        self.assertIn("expected-tail CAS failed", loser["error"])
        self.assertEqual(2, len(self.ledger()["attempts"]))
        self.assert_execution_current()

    def test_run_observation_is_from_real_child_not_caller_claims(self) -> None:
        real_stdout = b"real-out\x00\n"
        real_stderr = b"real-err\xff\n"
        command = [
            sys.executable,
            "-c",
            (
                "import os, sys; "
                f"os.write(1, {real_stdout!r}); "
                f"os.write(2, {real_stderr!r}); "
                "raise SystemExit(7)"
            ),
            "--exit-code=0",
            f"--stdout-sha256={'0' * 64}",
            "--stdout-bytes=999999",
        ]
        self.assertNotIn(
            "process_observation",
            inspect.signature(recorder.run_and_append).parameters,
        )
        with (
            mock.patch.object(
                recorder,
                "utc_datetime_milliseconds",
                side_effect=[
                    datetime(2026, 7, 25, 2, 0, 0, tzinfo=UTC),
                    datetime(2026, 7, 25, 2, 0, 0, 125000, tzinfo=UTC),
                ],
            ),
        ):
            result = recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                command,
                None,
                "open",
                "RECORDER-REAL-PROCESS",
                "Capture only the real child process",
                10,
            )
        observation = self.ledger()["attempts"][-1]["process_observation"]
        self.assertEqual(7, result["process_exit_code"])
        self.assertEqual(
            {
                "mode": "run",
                "argv": command,
                "exit_code": 7,
                "stdout_sha256": hashlib.sha256(real_stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(real_stderr).hexdigest(),
                "stdout_bytes": len(real_stdout),
                "stderr_bytes": len(real_stderr),
                "capture_authority": "recorder_executed_process",
            },
            observation,
        )
        self.assert_execution_current()

    def test_pending_packet_cannot_append(self) -> None:
        before = self.project_files()
        with self.assertRaisesRegex(
            recorder.RecorderError,
            "append requires one active packet",
        ):
            recorder.append_passive(
                self.root,
                SUCCESSOR_ID,
                self.tail(SUCCESSOR_ID),
                None,
                "open",
                "RECORDER-PENDING-REJECTED",
                "A pending packet cannot execute",
            )
        self.assertEqual(before, self.project_files())

    def test_interrupted_transaction_fails_closed_and_recovers_roll_forward(
        self,
    ) -> None:
        before_attempts = copy.deepcopy(self.ledger()["attempts"])
        with self.assertRaises(recorder.SimulatedRecorderCrash) as raised:
            self.append_passive(
                status_after="blocked",
                failure_after=["REC-01"],
                crash_after_replacements=1,
            )
        transaction_id = str(raised.exception)
        receipt = self.assert_execution_invalid(
            "interrupted transaction requiring recovery"
        )
        self.assertEqual("invalid", receipt["execution_freshness_status"])
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "execution-freshness verifier failed",
        ):
            project_state.derive_projection(self.root)

        recovered = recorder.recover_transactions(self.root)
        self.assertEqual([transaction_id], recovered)
        ledger = self.ledger()
        self.assertEqual(before_attempts, ledger["attempts"][:-1])
        self.assertEqual(2, len(ledger["attempts"]))
        self.assertEqual("blocked", ledger["reported_state"])
        self.assertEqual(
            "blocked",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assert_execution_current()
        project_state.check_project_state(self.root)

        rolled_forward = self.project_files()
        self.assertEqual([], recorder.recover_transactions(self.root))
        self.assertEqual(rolled_forward, self.project_files())

    def test_append_preserves_every_existing_attempt_record(self) -> None:
        before = copy.deepcopy(self.ledger()["attempts"])
        before_bytes = [recorder.canonical_bytes(item) for item in before]
        self.append_passive()
        after = self.ledger()["attempts"]
        self.assertEqual(before, after[: len(before)])
        self.assertEqual(
            before_bytes,
            [recorder.canonical_bytes(item) for item in after[: len(before)]],
        )
        self.assertEqual(len(before) + 1, len(after))

    def test_successful_write_refreshes_execution_and_all_state_views(self) -> None:
        result = self.append_passive()
        self.assertEqual("valid", result["execution_verification"])
        self.assertEqual("current", result["execution_freshness"])
        self.assert_execution_current()
        projection = project_state.check_project_state(self.root)
        policy = self.read_json(PROJECT_STATE_POLICY.as_posix())
        for view in VIEW_PATHS:
            with self.subTest(view=view):
                self.assertEqual(
                    project_state.render_canonical_view(
                        projection,
                        policy,
                        view,
                    ),
                    (self.root / view).read_bytes(),
                )

    def test_terminal_completion_rejects_append_and_detects_all_rewrites(
        self,
    ) -> None:
        self.finalize_with_consistent_clock()
        terminal_tail = self.tail()
        before = self.project_files()
        with self.assertRaisesRegex(
            recorder.RecorderError,
            "append requires one active packet|terminal ledger cannot be appended",
        ):
            self.append_passive(expected_tail=terminal_tail)
        self.assertEqual(before, self.project_files())

        controlled = self.root / TARGET_OUTPUT
        controlled_before = controlled.read_bytes()
        controlled.write_bytes(controlled_before + b"tamper\n")
        self.assert_execution_invalid("latest controlled snapshot is stale")
        controlled.write_bytes(controlled_before)
        self.assert_execution_current()

        receipt_paths = (
            f".work_packets/receipts/{TARGET_ID}.checkpoint.json",
            f".work_packets/receipts/{TARGET_ID}.acceptance.json",
            f".work_packets/receipts/{TARGET_ID}.execution.v2.json",
        )
        for relative in receipt_paths:
            with self.subTest(receipt=relative):
                path = self.root / relative
                original = path.read_bytes()
                value = json.loads(original)
                value["packet_contract_sha256"] = "0" * 64
                path.write_bytes(recorder.canonical_bytes(value))
                receipt = self.execution_receipt()
                self.assertEqual(
                    "invalid",
                    receipt["verification_status"],
                    receipt,
                )
                self.assertTrue(
                    any("digest differs" in error for error in receipt["errors"]),
                    receipt["errors"],
                )
                path.write_bytes(original)
                self.assert_execution_current()

    def test_finalize_is_one_transaction_with_exact_receipts_and_successor(
        self,
    ) -> None:
        self.record_resolved()
        ledger_before = self.ledger()
        latest = copy.deepcopy(ledger_before["attempts"][-1])
        target_before = self.read_json(self.packet_path(TARGET_ID))
        contract_digest = work_packets.packet_contract_sha256(target_before)
        check = target_before["acceptance_checks"][0]

        with (
            mock.patch.object(
                recorder,
                "utc_datetime_milliseconds",
                side_effect=[
                    datetime(2026, 7, 25, 3, 0, 0, tzinfo=UTC),
                    datetime(2026, 7, 25, 3, 0, 0, 125000, tzinfo=UTC),
                ],
            ),
            mock.patch.object(
                recorder,
                "apply_transaction",
                wraps=recorder.apply_transaction,
            ) as transaction,
        ):
            result = recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
            )

        self.assertEqual(1, transaction.call_count)
        replacements = transaction.call_args.args[2]
        expected_replacements = {
            self.packet_path(TARGET_ID),
            self.ledger_relative(TARGET_ID),
            f".work_packets/receipts/{TARGET_ID}.checkpoint.json",
            f".work_packets/receipts/{TARGET_ID}.acceptance.json",
            f".work_packets/receipts/{TARGET_ID}.execution.v2.json",
            self.packet_path(SUCCESSOR_ID),
            self.ledger_relative(SUCCESSOR_ID),
        }
        self.assertEqual(expected_replacements, set(replacements))

        dependency_checkpoint = self.read_json(
            f".work_packets/receipts/{EXEMPT_ID}.checkpoint.json"
        )
        dependency_acceptance = self.read_json(
            f".work_packets/receipts/{EXEMPT_ID}.acceptance.json"
        )
        expected_checkpoint = {
            "schema_version": "work-packet-checkpoint/v2",
            "packet_id": TARGET_ID,
            "packet_contract_sha256": contract_digest,
            "sequence": len(ledger_before["attempts"]) + 1,
            "snapshots": latest["controlled_snapshot"]["claims"],
            "prerequisite_receipts": [
                {
                    "packet_id": EXEMPT_ID,
                    "packet_contract_sha256": (
                        work_packets.packet_contract_sha256(
                            self.read_json(self.packet_path(EXEMPT_ID))
                        )
                    ),
                    "checkpoint_receipt_sha256": execution.canonical_sha256(
                        dependency_checkpoint
                    ),
                    "acceptance_receipt_sha256": execution.canonical_sha256(
                        dependency_acceptance
                    ),
                }
            ],
        }
        expected_acceptance = {
            "schema_version": "work-packet-acceptance/v2",
            "packet_id": TARGET_ID,
            "packet_contract_sha256": contract_digest,
            "checkpoint_receipt_sha256": execution.canonical_sha256(
                expected_checkpoint
            ),
            "checks": [
                {"check_id": check["check_id"], "actual_exit_code": 0}
            ],
        }
        expected_execution = {
            "schema_version": "execution-finalization-receipt/v2",
            "packet_id": TARGET_ID,
            "packet_contract_sha256": contract_digest,
            "checks": [
                {
                    "check_id": check["check_id"],
                    "argv": check["argv"],
                    "expected_exit_code": 0,
                    "actual_exit_code": 0,
                    "started_at": "2026-07-25T03:00:00.000Z",
                    "ended_at": "2026-07-25T03:00:00.125Z",
                    "wall_time_ms": 125,
                    "stdout_sha256": hashlib.sha256(
                        FINALIZE_STDOUT
                    ).hexdigest(),
                    "stderr_sha256": hashlib.sha256(
                        FINALIZE_STDERR
                    ).hexdigest(),
                    "stdout_bytes": len(FINALIZE_STDOUT),
                    "stderr_bytes": len(FINALIZE_STDERR),
                }
            ],
        }
        self.assertEqual(
            expected_checkpoint,
            self.read_json(
                f".work_packets/receipts/{TARGET_ID}.checkpoint.json"
            ),
        )
        self.assertEqual(
            expected_acceptance,
            self.read_json(
                f".work_packets/receipts/{TARGET_ID}.acceptance.json"
            ),
        )
        self.assertEqual(
            expected_execution,
            self.read_json(
                f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
            ),
        )

        target_after = self.read_json(self.packet_path(TARGET_ID))
        self.assertEqual("complete", target_after["state"])
        self.assertEqual(
            f".work_packets/receipts/{TARGET_ID}.checkpoint.json",
            target_after["checkpoint_path"],
        )
        self.assertEqual(
            f".work_packets/receipts/{TARGET_ID}.acceptance.json",
            target_after["acceptance_receipt_path"],
        )
        self.assertEqual(
            contract_digest,
            work_packets.packet_contract_sha256(target_after),
        )
        target_ledger = self.ledger()
        expected_terminal = {
            "authority_kind": "self_reported_local_candidate",
            "packet_contract_sha256": contract_digest,
            "latest_record_sha256": latest["record_sha256"],
            "controlled_claims_sha256": latest["controlled_snapshot"][
                "claims_sha256"
            ],
            "checkpoint_path": (
                f".work_packets/receipts/{TARGET_ID}.checkpoint.json"
            ),
            "checkpoint_canonical_sha256": execution.canonical_sha256(
                expected_checkpoint
            ),
            "acceptance_path": (
                f".work_packets/receipts/{TARGET_ID}.acceptance.json"
            ),
            "acceptance_canonical_sha256": execution.canonical_sha256(
                expected_acceptance
            ),
            "execution_receipt_path": (
                f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
            ),
            "execution_receipt_canonical_sha256": execution.canonical_sha256(
                expected_execution
            ),
        }
        self.assertEqual("complete", target_ledger["reported_state"])
        self.assertEqual(expected_terminal, target_ledger["terminal_completion"])
        self.assertEqual(
            "active",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )
        self.assertEqual(
            "active",
            self.ledger(SUCCESSOR_ID)["reported_state"],
        )
        self.assertEqual(
            execution.canonical_sha256(expected_execution),
            result["execution_receipt_sha256"],
        )
        self.assertEqual("pass", self.work_receipt()["status"])
        self.assert_execution_current()
        project_state.check_project_state(self.root)

    def test_wall_time_is_exactly_the_rfc3339_timestamp_delta(self) -> None:
        command = [sys.executable, "-c", "raise SystemExit(0)"]
        with (
            mock.patch.object(
                recorder,
                "utc_datetime_milliseconds",
                side_effect=[
                    datetime(2026, 7, 25, 4, 0, 0, tzinfo=UTC),
                    datetime(2026, 7, 25, 4, 0, 0, 250000, tzinfo=UTC),
                ],
            ),
        ):
            recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                command,
                None,
                "open",
                "RECORDER-CLOCK-CONSISTENCY",
                "Timestamp duration is the wall-time authority",
                10,
            )
        attempt = self.ledger()["attempts"][-1]
        timestamp_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
        self.assertRegex(attempt["started_at"], timestamp_pattern)
        self.assertRegex(attempt["ended_at"], timestamp_pattern)
        started = datetime.strptime(
            attempt["started_at"],
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ).replace(tzinfo=UTC)
        ended = datetime.strptime(
            attempt["ended_at"],
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ).replace(tzinfo=UTC)
        self.assertEqual(
            int((ended - started).total_seconds() * 1000),
            attempt["wall_time_ms"],
        )
        self.assert_execution_current()


if __name__ == "__main__":
    unittest.main()
