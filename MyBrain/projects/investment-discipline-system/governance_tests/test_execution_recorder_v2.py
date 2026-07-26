from __future__ import annotations

import copy
import hashlib
import inspect
import json
import shutil
import subprocess
import sys
import tempfile
import time
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
SECOND_ID = "WP-RECORDER-SECOND"
EXEMPT_ID = "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY"
TARGET_OUTPUT = "src/recorder-target.txt"
SUCCESSOR_OUTPUT = "src/recorder-successor.txt"
SECOND_OUTPUT = "src/recorder-second.txt"
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
            "bounded_write_paths": [{"path": TARGET_OUTPUT, "kind": "file"}],
            "read_dependencies": ["governance_tests/test_contract_supersession.py"],
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
                            "path": ("governance_tests/test_contract_supersession.py"),
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
            "bounded_write_paths": [{"path": SUCCESSOR_OUTPUT, "kind": "file"}],
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
                    "inputs": [{"packet_id": TARGET_ID, "path": TARGET_OUTPUT}],
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
        live_packet_ids = {
            path.name.removesuffix(".packet.json")
            for path in (self.root / PACKET_DIRECTORY).glob("*.packet.json")
        }
        errors: list[str] = []
        excluded, claims = execution.current_claim_snapshots(
            self.root.resolve(),
            packet,
            live_packet_ids,
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
            {key: value for key, value in attempt.items() if key != "record_sha256"}
        )
        return {
            "schema_version": "execution-attempt-ledger/v2",
            "packet_id": packet["packet_id"],
            "packet_path": self.packet_path(packet["packet_id"]),
            "packet_contract_sha256": work_packets.packet_contract_sha256(packet),
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
                        "freeze_state_authority": ("governance/FROZEN_BUNDLE_V1.json")
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
        crash_before_journal_after_staged: bool = False,
        crash_after_outcome: bool = False,
        crash_after_core_commit: bool = False,
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
            crash_before_journal_after_staged=(crash_before_journal_after_staged),
            crash_after_outcome=crash_after_outcome,
            crash_after_core_commit=crash_after_core_commit,
        )

    def record_resolved(self) -> dict[str, Any]:
        return self.append_passive(status_after="resolved")

    def finalize_with_consistent_clock(self) -> dict[str, Any]:
        self.record_resolved()
        with mock.patch.object(
            recorder,
            "utc_datetime_milliseconds",
            side_effect=[
                datetime(2030, 7, 25, 1, 0, 0, tzinfo=UTC),
                datetime(2030, 7, 25, 1, 0, 0, 125000, tzinfo=UTC),
            ],
        ):
            return recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
            )

    def git(self, *argv: str) -> str:
        completed = subprocess.run(
            ["git", *argv],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(
            0,
            completed.returncode,
            (completed.stdout, completed.stderr),
        )
        return completed.stdout.strip()

    def prepare_seal_authority(
        self,
        packet_id: str = TARGET_ID,
    ) -> tuple[str, str]:
        probe = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if probe.returncode != 0:
            self.git("init", "-q")
            self.git("config", "user.name", "Recorder Test")
            self.git("config", "user.email", "recorder@example.invalid")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", f"candidate {packet_id}")
        candidate_commit = self.git("rev-parse", "HEAD")
        candidate_tree = self.git("rev-parse", "HEAD^{tree}")
        candidate_terminal = self.ledger(packet_id)["terminal_completion"]
        review = {
            "schema_version": "work-packet-independent-review/v2",
            "packet_id": packet_id,
            "candidate_commit": candidate_commit,
            "candidate_tree": candidate_tree,
            "candidate_terminal_canonical_sha256": (
                execution.canonical_sha256(candidate_terminal)
            ),
            "reviewer_mode": "independent_read_only",
            "verdict": "accepted",
            "findings": [],
            "limitations": [
                "Fixture review validates binding mechanics, not reviewer identity."
            ],
        }
        review_path = f".work_packets/reviews/{packet_id}.review.v2.json"
        self.write_json(review_path, review)
        self.git("add", review_path)
        self.git("commit", "-q", "-m", f"review {packet_id}")
        review_commit = self.git("rev-parse", "HEAD")
        self.git(
            "tag",
            f"ids-reviewed/{packet_id}",
            review_commit,
        )
        return candidate_commit, review_commit

    def seal_candidate(
        self,
        packet_id: str = TARGET_ID,
    ) -> tuple[str, str, dict[str, Any]]:
        candidate_commit, review_commit = self.prepare_seal_authority(packet_id)
        result = recorder.seal_packet(
            self.root,
            packet_id,
            self.tail(packet_id),
            candidate_commit,
            review_commit,
        )
        return candidate_commit, review_commit, result

    def test_wrong_expected_tail_cas_changes_no_project_file(self) -> None:
        before = self.project_files()
        with self.assertRaisesRegex(recorder.RecorderError, "expected-tail CAS"):
            self.append_passive(expected_tail="0" * 64)
        self.assertEqual(before, self.project_files())

    def test_invalid_transition_input_changes_no_file_or_operation(self) -> None:
        before = self.project_files()
        with self.assertRaisesRegex(
            recorder.RecorderError,
            "failure_after must contain unique valid failure identifiers",
        ):
            recorder.append_passive(
                self.root,
                TARGET_ID,
                self.tail(),
                ["bad failure"],
                "open",
                "bad",
                "Invalid caller data",
            )
        self.assertEqual(before, self.project_files())
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()

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
        operation_id = recorder.pending_operation_paths(self.root)[0].name
        receipt = self.assert_execution_invalid(
            "interrupted transaction requiring recovery"
        )
        self.assertEqual("invalid", receipt["execution_freshness_status"])
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "execution-freshness verifier failed",
        ):
            project_state.derive_projection(self.root)

        self.assertEqual(
            [transaction_id],
            [path.name for path in recorder.pending_transaction_paths(self.root)],
        )
        recovered = recorder.recover_operations(self.root)
        self.assertEqual([operation_id], recovered)
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
        self.assertEqual([], recorder.recover_operations(self.root))
        self.assertEqual(rolled_forward, self.project_files())

    def test_prejournal_staging_is_discarded_then_operation_rolls_forward(
        self,
    ) -> None:
        before = copy.deepcopy(self.ledger()["attempts"])
        with self.assertRaises(recorder.SimulatedRecorderCrash):
            self.append_passive(
                crash_before_journal_after_staged=True,
            )
        transaction = recorder.pending_transaction_paths(self.root)[0]
        self.assertTrue((transaction / "prepare.json").is_file())
        self.assertFalse((transaction / "journal.json").exists())
        operation_id = recorder.pending_operation_paths(self.root)[0].name
        self.assertEqual(before, self.ledger()["attempts"])
        self.assert_execution_invalid("interrupted transaction requiring recovery")

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        self.assertEqual(len(before) + 1, len(self.ledger()["attempts"]))
        self.assertEqual([], recorder.pending_transaction_paths(self.root))
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()
        project_state.check_project_state(self.root)

    def test_empty_prelaunch_operation_is_recoverable_and_never_executes(
        self,
    ) -> None:
        operation_id = "a" * 32
        directory = (
            self.root
            / execution.EXPECTED_RECORDER["operation_directory"]
            / operation_id
        )
        directory.mkdir(parents=True)
        self.assert_execution_invalid("interrupted operation requiring recovery")
        before = self.project_files()
        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        self.assertFalse(directory.exists())
        self.assertEqual(
            {
                path: content
                for path, content in before.items()
                if not path.startswith(
                    execution.EXPECTED_RECORDER["operation_directory"]
                )
            },
            {
                path: content
                for path, content in self.project_files().items()
                if not path.startswith(
                    execution.EXPECTED_RECORDER["operation_directory"]
                )
            },
        )
        self.assert_execution_current()

    def test_durable_outcome_recovers_instead_of_disappearing(self) -> None:
        before = copy.deepcopy(self.ledger()["attempts"])
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            self.append_passive(crash_after_outcome=True)
        operation_id = str(raised.exception)
        self.assertEqual(before, self.ledger()["attempts"])
        self.assert_execution_invalid("interrupted operation requiring recovery")

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        after = self.ledger()["attempts"]
        self.assertEqual(before, after[:-1])
        self.assertEqual("passive", after[-1]["process_observation"]["mode"])
        self.assert_execution_current()

    def test_post_outcome_change_cannot_be_attributed_to_finished_run(
        self,
    ) -> None:
        recorder.append_passive(
            self.root,
            TARGET_ID,
            self.tail(),
            ["REC-01"],
            "open",
            "RECORDER-PRIOR-FAILURE",
            "Create one unresolved failure",
        )
        command = [sys.executable, "-c", "raise SystemExit(0)"]
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                command,
                [],
                "resolved",
                "RECORDER-REQUESTED-RESOLUTION",
                "The child itself changes no controlled bytes",
                10,
                crash_after_outcome=True,
            )
        operation_id = str(raised.exception)
        self.write_text(TARGET_OUTPUT, "changed-after-durable-outcome\n")

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            ["REC-01", "RECORDER-905"],
            latest["failure_delta"]["after"],
        )
        self.assertEqual([], latest["failure_delta"]["resolved"])
        self.assertEqual("blocked", latest["blocker"]["status_after"])
        self.assertEqual(
            "RECORDER-POST-OUTCOME-DIVERGENCE",
            latest["blocker"]["root_cause_id"],
        )
        self.assertEqual(0, latest["process_observation"]["exit_code"])
        self.assert_execution_current()

    def test_sigkill_after_durable_child_outcome_recovers_exact_result(
        self,
    ) -> None:
        barrier = Path(self._temporary.name) / "outcome-durable"
        expected_tail = self.tail()
        child_stdout = b"durable-child-out\n"
        worker = (
            "import signal, sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, {str(SOURCE_ROOT)!r})\n"
            "from scripts import record_execution_attempt_v2 as recorder\n"
            "root = Path(sys.argv[1])\n"
            "barrier = Path(sys.argv[2])\n"
            "def hook(phase, operation_id):\n"
            "    if phase == 'outcome':\n"
            "        barrier.write_text(operation_id)\n"
            "        signal.pause()\n"
            "recorder.run_and_append("
            "root, sys.argv[3], sys.argv[4], "
            f"[sys.executable, '-c', {('import os; os.write(1, ' + repr(child_stdout) + ')')!r}], "
            "None, 'open', 'RECORDER-SIGKILL', "
            "'Persist child outcome before forced termination', 10, "
            "_lifecycle_hook=hook)"
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                worker,
                str(self.root),
                str(barrier),
                TARGET_ID,
                expected_tail,
            ],
            cwd=SOURCE_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 15
        while not barrier.exists() and process.poll() is None:
            if time.monotonic() >= deadline:
                process.kill()
                stdout, stderr = process.communicate()
                self.fail((stdout, stderr))
            time.sleep(0.01)
        self.assertTrue(barrier.exists())
        operation_id = barrier.read_text()
        process.kill()
        process.communicate(timeout=10)
        self.assertNotEqual(0, process.returncode)
        operation = recorder.validate_operation(
            self.root
            / execution.EXPECTED_RECORDER["operation_directory"]
            / operation_id
        )
        self.assertEqual("outcome_recorded", operation["phase"])
        self.assert_execution_invalid("interrupted operation requiring recovery")

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        observed = self.ledger()["attempts"][-1]["process_observation"]
        self.assertEqual(0, observed["exit_code"])
        self.assertEqual(
            hashlib.sha256(child_stdout).hexdigest(),
            observed["stdout_sha256"],
        )
        self.assertEqual(len(child_stdout), observed["stdout_bytes"])
        self.assert_execution_current()

    def test_sigkill_while_child_runs_terminates_group_before_recovery(
        self,
    ) -> None:
        barrier = Path(self._temporary.name) / "child-running"
        expected_tail = self.tail()
        child = (
            "import pathlib, sys, time; "
            "time.sleep(30); "
            "pathlib.Path(sys.argv[1]).write_text('late-child-write\\n')"
        )
        worker = (
            "import signal, sys\n"
            "from pathlib import Path\n"
            f"sys.path.insert(0, {str(SOURCE_ROOT)!r})\n"
            "from scripts import record_execution_attempt_v2 as recorder\n"
            "root = Path(sys.argv[1])\n"
            "barrier = Path(sys.argv[2])\n"
            "def hook(phase, operation_id):\n"
            "    if phase == 'process_started':\n"
            "        barrier.write_text(operation_id)\n"
            "        signal.pause()\n"
            "recorder.run_and_append("
            "root, sys.argv[3], sys.argv[4], "
            f"[sys.executable, '-c', {child!r}, str(root / {TARGET_OUTPUT!r})], "
            "None, 'open', 'RECORDER-LIVE-CHILD', "
            "'Recorder owns the still-running child group', 60, "
            "_lifecycle_hook=hook)"
        )
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                worker,
                str(self.root),
                str(barrier),
                TARGET_ID,
                expected_tail,
            ],
            cwd=SOURCE_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        deadline = time.monotonic() + 15
        while not barrier.exists() and process.poll() is None:
            if time.monotonic() >= deadline:
                process.kill()
                stdout, stderr = process.communicate()
                self.fail((stdout, stderr))
            time.sleep(0.01)
        operation_id = barrier.read_text()
        process.kill()
        process.communicate(timeout=10)

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        time.sleep(0.1)
        self.assertEqual(
            "target-v1\n",
            (self.root / TARGET_OUTPUT).read_text(encoding="utf-8"),
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual("indeterminate", latest["process_observation"]["mode"])
        self.assertEqual(["RECORDER-902"], latest["failure_delta"]["after"])
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()

    def test_postcore_crash_keeps_operation_until_views_are_refreshed(
        self,
    ) -> None:
        before_views = {
            relative: (self.root / relative).read_bytes() for relative in VIEW_PATHS
        }
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            self.append_passive(crash_after_core_commit=True)
        operation_id = str(raised.exception)
        self.assertEqual(2, len(self.ledger()["attempts"]))
        self.assertEqual(
            before_views,
            {relative: (self.root / relative).read_bytes() for relative in VIEW_PATHS},
        )
        self.assert_execution_invalid("interrupted operation requiring recovery")

        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        self.assert_execution_current()
        project_state.check_project_state(self.root)
        self.assertNotEqual(
            before_views,
            {relative: (self.root / relative).read_bytes() for relative in VIEW_PATHS},
        )

    def test_missing_run_outcome_recovers_as_explicit_block(self) -> None:
        command = [sys.executable, "-c", "raise SystemExit(0)"]
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                command,
                None,
                "resolved",
                "RECORDER-RUN-INTENT",
                "Durable run intent",
                10,
                crash_after_intent=True,
            )
        operation_id = str(raised.exception)
        self.assert_execution_invalid("interrupted operation requiring recovery")
        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            "indeterminate",
            latest["process_observation"]["mode"],
        )
        self.assertEqual("blocked", latest["blocker"]["status_after"])
        self.assertEqual(["RECORDER-902"], latest["failure_delta"]["after"])
        self.assertEqual(
            "blocked",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assert_execution_current()

    def test_missing_run_outcome_preserves_every_prior_failure(self) -> None:
        recorder.append_passive(
            self.root,
            TARGET_ID,
            self.tail(),
            ["REC-01"],
            "open",
            "RECORDER-PRIOR-FAILURE",
            "Create one unresolved failure",
        )
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                [sys.executable, "-c", "raise SystemExit(0)"],
                [],
                "resolved",
                "RECORDER-RUN-INTENT",
                "Requested resolution is not yet observed",
                10,
                crash_after_intent=True,
            )
        self.assertEqual(
            [str(raised.exception)],
            recorder.recover_operations(self.root),
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            ["REC-01", "RECORDER-902"],
            latest["failure_delta"]["after"],
        )
        self.assertEqual([], latest["failure_delta"]["resolved"])
        self.assert_execution_current()

    def test_nonzero_run_cannot_be_discarded_by_requested_resolution(
        self,
    ) -> None:
        result = recorder.run_and_append(
            self.root,
            TARGET_ID,
            self.tail(),
            [sys.executable, "-c", "raise SystemExit(7)"],
            None,
            "resolved",
            "RECORDER-NONZERO",
            "Caller requested resolution",
            10,
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(7, result["process_exit_code"])
        self.assertEqual("open", latest["blocker"]["status_after"])
        self.assertEqual(["RECORDER-901"], latest["failure_delta"]["after"])
        self.assert_execution_current()

    def test_nonzero_run_preserves_every_prior_failure(self) -> None:
        recorder.append_passive(
            self.root,
            TARGET_ID,
            self.tail(),
            ["REC-01"],
            "open",
            "RECORDER-PRIOR-FAILURE",
            "Create one unresolved failure",
        )
        recorder.run_and_append(
            self.root,
            TARGET_ID,
            self.tail(),
            [sys.executable, "-c", "raise SystemExit(7)"],
            [],
            "resolved",
            "RECORDER-NONZERO",
            "Caller requested resolution",
            10,
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            ["REC-01", "RECORDER-901"],
            latest["failure_delta"]["after"],
        )
        self.assertEqual([], latest["failure_delta"]["resolved"])
        self.assertEqual("open", latest["blocker"]["status_after"])
        self.assert_execution_current()

    def test_run_output_capture_has_a_hard_limit(self) -> None:
        with mock.patch.object(
            recorder,
            "MAX_CAPTURED_OUTPUT_BYTES_PER_STREAM",
            32,
        ):
            recorder.run_and_append(
                self.root,
                TARGET_ID,
                self.tail(),
                [sys.executable, "-c", "import os; os.write(1, b'x' * 1000)"],
                [],
                "resolved",
                "RECORDER-OUTPUT-LIMIT",
                "Bound child output capture",
                10,
            )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            recorder.OUTPUT_LIMIT_EXIT_CODE,
            latest["process_observation"]["exit_code"],
        )
        self.assertEqual(32, latest["process_observation"]["stdout_bytes"])
        self.assertEqual(["RECORDER-901"], latest["failure_delta"]["after"])
        self.assert_execution_current()

    def test_unsupported_resolution_is_recorded_before_any_invalid_commit(
        self,
    ) -> None:
        recorder.append_passive(
            self.root,
            TARGET_ID,
            self.tail(),
            ["REC-01"],
            "open",
            "RECORDER-PRIOR-FAILURE",
            "Create one unresolved failure",
        )
        recorder.run_and_append(
            self.root,
            TARGET_ID,
            self.tail(),
            [sys.executable, "-c", "raise SystemExit(0)"],
            [],
            "resolved",
            "RECORDER-UNSUPPORTED",
            "No controlled byte changed",
            10,
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            ["REC-01", "RECORDER-906"],
            latest["failure_delta"]["after"],
        )
        self.assertEqual([], latest["failure_delta"]["resolved"])
        self.assertEqual(
            "RECORDER-UNSUPPORTED-RESOLUTION",
            latest["blocker"]["root_cause_id"],
        )
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()

    def test_finalize_outcome_recovers_without_rerunning_observed_check(
        self,
    ) -> None:
        self.record_resolved()
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
                crash_after_check_outcome=1,
            )
        operation_id = str(raised.exception)
        operation = recorder.validate_operation(
            recorder.pending_operation_paths(self.root)[0]
        )
        self.assertEqual(1, operation["outcome"]["next_check_index"])
        self.assertEqual(1, len(operation["outcome"]["checks"]))
        self.assert_execution_invalid("interrupted operation requiring recovery")

        with mock.patch.object(
            recorder,
            "subprocess",
            wraps=recorder.subprocess,
        ) as process_module:
            self.assertEqual(
                [operation_id],
                recorder.recover_operations(self.root),
            )
        self.assertEqual(0, process_module.run.call_count)
        self.assertEqual(
            "candidate_complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assert_execution_current()

    def test_git_review_seal_is_required_before_successor_activation(
        self,
    ) -> None:
        self.finalize_with_consistent_clock()
        self.assertEqual(
            "candidate_complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assertEqual(
            "pending",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )

        candidate_commit, review_commit, result = self.seal_candidate()
        self.assertEqual("sealed_complete", result["status"])
        self.assertEqual(candidate_commit, result["candidate_commit"])
        self.assertEqual(review_commit, result["review_commit"])
        self.assertEqual(
            "complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assertEqual(
            "active",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )
        terminal = self.ledger()["terminal_completion"]
        self.assertEqual(
            "git_review_sealed_candidate",
            terminal["authority_kind"],
        )
        self.assertEqual(
            f"refs/tags/ids-reviewed/{TARGET_ID}",
            terminal["completion_seal"]["anchor_ref"],
        )
        self.assert_execution_current()
        project_state.check_project_state(self.root)

    def test_seal_reads_candidate_from_real_parent_repository_prefix(
        self,
    ) -> None:
        self.finalize_with_consistent_clock()
        repository_root = self.root.parent
        subprocess.run(
            ["git", "init", "-q", str(repository_root)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.git("config", "user.name", "Recorder Test")
        self.git("config", "user.email", "recorder@example.invalid")

        candidate_commit, review_commit, result = self.seal_candidate()
        prefix = self.git("rev-parse", "--show-prefix")
        self.assertTrue(prefix.endswith("project/"), prefix)
        self.assertEqual("sealed_complete", result["status"])
        self.assertEqual(candidate_commit, result["candidate_commit"])
        self.assertEqual(review_commit, result["review_commit"])
        self.assert_execution_current()

    def test_seal_rejects_index_bytes_not_seen_by_acceptance(self) -> None:
        self.finalize_with_consistent_clock()
        self.git("init", "-q")
        self.git("config", "user.name", "Recorder Test")
        self.git("config", "user.email", "recorder@example.invalid")
        self.git("add", "-A")
        accepted_bytes = (self.root / TARGET_OUTPUT).read_bytes()
        self.write_text(TARGET_OUTPUT, "candidate-index-only-bytes\n")
        self.git("add", TARGET_OUTPUT)
        (self.root / TARGET_OUTPUT).write_bytes(accepted_bytes)
        self.git("commit", "-q", "-m", "candidate with divergent index")
        candidate_commit = self.git("rev-parse", "HEAD")
        candidate_tree = self.git("rev-parse", "HEAD^{tree}")
        terminal = self.ledger()["terminal_completion"]
        review = {
            "schema_version": "work-packet-independent-review/v2",
            "packet_id": TARGET_ID,
            "candidate_commit": candidate_commit,
            "candidate_tree": candidate_tree,
            "candidate_terminal_canonical_sha256": (
                execution.canonical_sha256(terminal)
            ),
            "reviewer_mode": "independent_read_only",
            "verdict": "accepted",
            "findings": [],
            "limitations": ["Fixture exercises candidate content binding."],
        }
        review_path = f".work_packets/reviews/{TARGET_ID}.review.v2.json"
        self.write_json(review_path, review)
        self.git("add", review_path)
        self.git("commit", "-q", "-m", "review divergent candidate")
        review_commit = self.git("rev-parse", "HEAD")
        self.git("tag", f"ids-reviewed/{TARGET_ID}", review_commit)

        with self.assertRaisesRegex(
            recorder.RecorderError,
            "candidate Git controlled claims differ",
        ):
            recorder.seal_packet(
                self.root,
                TARGET_ID,
                self.tail(),
                candidate_commit,
                review_commit,
            )
        self.assertEqual(
            "candidate_complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()

    def test_interrupted_seal_recovers_before_retiring_operation(
        self,
    ) -> None:
        self.finalize_with_consistent_clock()
        candidate_commit, review_commit = self.prepare_seal_authority()
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.seal_packet(
                self.root,
                TARGET_ID,
                self.tail(),
                candidate_commit,
                review_commit,
                crash_after_core_commit=True,
            )
        operation_id = str(raised.exception)
        self.assertEqual(
            "complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assert_execution_invalid("interrupted operation requiring recovery")
        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()
        project_state.check_project_state(self.root)

    def test_coherent_terminal_and_receipt_rewrite_fails_git_anchor(
        self,
    ) -> None:
        self.finalize_with_consistent_clock()
        self.seal_candidate()
        execution_relative = f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
        receipt = self.read_json(execution_relative)
        receipt["checks"][0]["stdout_sha256"] = "0" * 64
        self.write_json(execution_relative, receipt)
        ledger = self.ledger()
        terminal = ledger["terminal_completion"]
        rewritten_digest = execution.canonical_sha256(receipt)
        terminal["execution_receipt_canonical_sha256"] = rewritten_digest
        terminal["completion_seal"]["candidate_execution_receipt_canonical_sha256"] = (
            rewritten_digest
        )
        self.write_json(self.ledger_relative(TARGET_ID), ledger)

        invalid = self.execution_receipt()
        forged_receipt = copy.deepcopy(invalid)
        forged_receipt["verification_status"] = "valid"
        forged_receipt["execution_freshness_status"] = "current"
        forged_receipt["verified_ledger_count"] = (
            forged_receipt["tracked_packet_count"]
            - forged_receipt["exempt_packet_count"]
        )
        forged_receipt["errors"] = []
        work_receipt = self.work_receipt()

        def forged_observer(
            _root: Path,
            _policy: dict[str, Any],
        ) -> dict[str, Any]:
            return {
                "work_packets": {
                    "status": work_receipt["status"],
                    "policy_id": work_receipt["policy_id"],
                    "receipt_sha256": project_state.canonical_sha256(work_receipt),
                    "completion_verified_count": work_receipt[
                        "completion_verified_count"
                    ],
                    "superseded_receipt_verified_count": work_receipt[
                        "superseded_receipt_verified_count"
                    ],
                    "dag_edges": work_receipt["dag_edges"],
                    "root_packet_ids": work_receipt["root_packet_ids"],
                    "sink_packet_ids": work_receipt["sink_packet_ids"],
                },
                "execution_freshness": {
                    "verification_status": "valid",
                    "execution_freshness_status": "current",
                    "policy_id": forged_receipt["policy_id"],
                    "receipt_sha256": project_state.canonical_sha256(forged_receipt),
                    "tracked_packet_count": forged_receipt["tracked_packet_count"],
                    "verified_ledger_count": forged_receipt["verified_ledger_count"],
                    "exempt_packet_count": forged_receipt["exempt_packet_count"],
                    "authority_basis": forged_receipt["authority_basis"],
                },
            }

        project_state.refresh_project_state(
            self.root,
            runtime_authority_observer=forged_observer,
        )
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "execution-freshness verifier failed",
        ):
            project_state.check_project_state(self.root)
        self.assertEqual("invalid", invalid["verification_status"], invalid)
        self.assertTrue(
            any(
                "candidate_execution_receipt digest differs" in error
                or "candidate ledger differs from sealed transition" in error
                for error in invalid["errors"]
            ),
            invalid["errors"],
        )

    def test_fanin_predecessor_completes_before_join_activation(
        self,
    ) -> None:
        target = self.read_json(self.packet_path(TARGET_ID))
        target["activates"] = [SECOND_ID, SUCCESSOR_ID]
        second = {
            "schema_version": "work-packet-instance/v2",
            "packet_id": SECOND_ID,
            "goal_id": target["goal_id"],
            "state": "pending",
            "owner": "recorder-fixture",
            "reviewer": "recorder-test",
            "bounded_write_paths": [{"path": SECOND_OUTPUT, "kind": "file"}],
            "read_dependencies": [TARGET_OUTPUT],
            "acceptance_checks": [
                {
                    "check_id": "CHECK-RECORDER-SECOND",
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
            "activates": [SUCCESSOR_ID],
            "integration_invariants": [
                {
                    "invariant_id": "INV-RECORDER-SECOND-INPUT",
                    "inputs": [{"packet_id": TARGET_ID, "path": TARGET_OUTPUT}],
                    "probe_check_ids": ["CHECK-RECORDER-SECOND"],
                }
            ],
            "routing": {
                "phase_id": "design_freeze",
                "action_id": "ACT-RECORDER-SECOND",
                "route_order": 15,
                "addresses_finding_ids": ["F-RECORDER"],
                "summary": "Complete the second fan-in branch",
            },
        }
        successor = self.read_json(self.packet_path(SUCCESSOR_ID))
        successor["depends_on"] = [TARGET_ID, SECOND_ID]
        successor["read_dependencies"] = [TARGET_OUTPUT, SECOND_OUTPUT]
        successor["integration_invariants"][0]["inputs"] = [
            {"packet_id": TARGET_ID, "path": TARGET_OUTPUT},
            {"packet_id": SECOND_ID, "path": SECOND_OUTPUT},
        ]
        register = self.read_json("governance/AI_PROJECT_RESEARCH_REGISTER_V1.json")
        required_actions = register["challenge"]["rounds"][0]["findings"][0][
            "required_action_ids"
        ]
        required_actions.append("ACT-RECORDER-SECOND")
        required_actions.sort()
        self.write_text(SECOND_OUTPUT, "second-v1\n")
        self.write_json(self.packet_path(TARGET_ID), target)
        self.write_json(self.packet_path(SECOND_ID), second)
        self.write_json(self.packet_path(SUCCESSOR_ID), successor)
        self.write_json(
            "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json",
            register,
        )
        for packet in (target, second, successor):
            self.write_json(
                self.ledger_relative(packet["packet_id"]),
                self.baseline_ledger(packet),
            )
        self.assertEqual("pass", self.work_receipt()["status"])
        self.assert_execution_current()
        project_state.refresh_project_state(self.root)

        self.record_resolved()
        recorder.finalize_packet(self.root, TARGET_ID, self.tail())
        self.seal_candidate(TARGET_ID)
        self.assertEqual(
            "complete",
            self.read_json(self.packet_path(TARGET_ID))["state"],
        )
        self.assertEqual(
            "active",
            self.read_json(self.packet_path(SECOND_ID))["state"],
        )
        self.assertEqual(
            "pending",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )
        self.assert_execution_current()

        recorder.append_passive(
            self.root,
            SECOND_ID,
            self.tail(SECOND_ID),
            None,
            "resolved",
            "RECORDER-SECOND-RESOLVED",
            "Second fan-in branch is ready",
        )
        recorder.finalize_packet(
            self.root,
            SECOND_ID,
            self.tail(SECOND_ID),
        )
        self.seal_candidate(SECOND_ID)
        self.assertEqual(
            "complete",
            self.read_json(self.packet_path(SECOND_ID))["state"],
        )
        self.assertEqual(
            "active",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )
        self.assert_execution_current()
        project_state.check_project_state(self.root)

    def test_finalize_prepared_check_without_outcome_blocks_explicitly(
        self,
    ) -> None:
        self.record_resolved()
        with self.assertRaises(recorder.SimulatedOperationCrash) as raised:
            recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
                crash_after_check_prepare=1,
            )
        operation_id = str(raised.exception)
        self.assertEqual(
            [operation_id],
            recorder.recover_operations(self.root),
        )
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(
            "indeterminate",
            latest["process_observation"]["mode"],
        )
        self.assertEqual(["RECORDER-902"], latest["failure_delta"]["after"])
        self.assertEqual("blocked", latest["blocker"]["status_after"])
        self.assertIsNone(self.ledger()["terminal_completion"])
        self.assert_execution_current()

    def test_acceptance_check_mutation_is_recorded_and_never_completes(
        self,
    ) -> None:
        packet = self.read_json(self.packet_path(TARGET_ID))
        packet["acceptance_checks"][0]["argv"] = [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                f"Path({TARGET_OUTPUT!r}).write_text('mutated\\n')"
            ),
        ]
        self.write_json(self.packet_path(TARGET_ID), packet)
        ledger = self.ledger()
        ledger["packet_contract_sha256"] = work_packets.packet_contract_sha256(packet)
        self.write_json(self.ledger_relative(TARGET_ID), ledger)
        self.assert_execution_current()
        self.record_resolved()

        result = recorder.finalize_packet(
            self.root,
            TARGET_ID,
            self.tail(),
        )
        self.assertEqual("recorded", result["status"])
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(["RECORDER-903"], latest["failure_delta"]["after"])
        self.assertEqual("blocked", latest["blocker"]["status_after"])
        self.assertIsNone(self.ledger()["terminal_completion"])
        self.assertFalse(
            (
                self.root / f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
            ).exists()
        )
        self.assert_execution_current()

    def test_acceptance_timeout_is_bounded_and_durably_failed(self) -> None:
        packet = self.read_json(self.packet_path(TARGET_ID))
        packet["acceptance_checks"][0]["argv"] = [
            sys.executable,
            "-c",
            "import time; time.sleep(30)",
        ]
        self.write_json(self.packet_path(TARGET_ID), packet)
        ledger = self.ledger()
        ledger["packet_contract_sha256"] = work_packets.packet_contract_sha256(packet)
        self.write_json(self.ledger_relative(TARGET_ID), ledger)
        self.assert_execution_current()
        self.record_resolved()

        with mock.patch.object(
            recorder,
            "ACCEPTANCE_CHECK_TIMEOUT_SECONDS",
            0.05,
        ):
            result = recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
            )

        self.assertEqual("recorded", result["status"])
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(["RECORDER-904"], latest["failure_delta"]["after"])
        self.assertEqual(124, latest["process_observation"]["exit_code"])
        self.assertEqual("blocked", latest["blocker"]["status_after"])
        self.assertEqual([], recorder.pending_operation_paths(self.root))
        self.assert_execution_current()

    def test_acceptance_time_cannot_precede_resolved_attempt(self) -> None:
        self.record_resolved()
        latest_ended = self.ledger()["attempts"][-1]["ended_at"]
        rollback = datetime(2026, 7, 24, tzinfo=UTC)
        with mock.patch.object(
            recorder,
            "utc_datetime_milliseconds",
            side_effect=[rollback, rollback],
        ):
            recorder.finalize_packet(
                self.root,
                TARGET_ID,
                self.tail(),
            )
        execution_relative = f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
        receipt = self.read_json(execution_relative)
        self.assertEqual(latest_ended, receipt["checks"][0]["started_at"])
        self.assertEqual(latest_ended, receipt["checks"][0]["ended_at"])

        receipt["checks"][0]["started_at"] = "2026-07-24T00:00:00.000Z"
        receipt["checks"][0]["ended_at"] = "2026-07-24T00:00:00.000Z"
        receipt["checks"][0]["wall_time_ms"] = 0
        self.write_json(execution_relative, receipt)
        ledger = self.ledger()
        ledger["terminal_completion"]["execution_receipt_canonical_sha256"] = (
            execution.canonical_sha256(receipt)
        )
        self.write_json(self.ledger_relative(TARGET_ID), ledger)
        self.assert_execution_invalid("started_at precedes the prior execution event")

    def test_cross_attempt_clock_rollback_is_clamped_and_detected(
        self,
    ) -> None:
        prior_ended = self.ledger()["attempts"][-1]["ended_at"]
        with mock.patch.object(
            recorder,
            "utc_datetime_milliseconds",
            return_value=datetime(2026, 7, 24, tzinfo=UTC),
        ):
            self.append_passive()
        latest = self.ledger()["attempts"][-1]
        self.assertEqual(prior_ended, latest["started_at"])
        self.assertEqual(prior_ended, latest["ended_at"])

        ledger = self.ledger()
        latest = ledger["attempts"][-1]
        latest["started_at"] = "2026-07-24T23:59:59.000Z"
        latest["ended_at"] = "2026-07-24T23:59:59.000Z"
        latest["wall_time_ms"] = 0
        latest["record_sha256"] = execution.canonical_sha256(
            {key: value for key, value in latest.items() if key != "record_sha256"}
        )
        self.write_json(self.ledger_relative(TARGET_ID), ledger)
        self.assert_execution_invalid("started_at precedes the prior attempt ended_at")

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

    def test_recorder_can_replace_stale_latest_evidence_observation(
        self,
    ) -> None:
        self.write_text(TARGET_OUTPUT, "target-v2\n")
        self.append_passive()
        first = self.ledger()["attempts"][-1]
        self.assertEqual(
            [TARGET_OUTPUT],
            [item["path"] for item in first["evidence_delta"]["after"]],
        )
        self.write_text(TARGET_OUTPUT, "target-v3\n")
        self.assert_execution_invalid("evidence hash differs from current file")

        self.append_passive()
        second = self.ledger()["attempts"][-1]
        self.assertEqual(
            hashlib.sha256(b"target-v3\n").hexdigest(),
            second["evidence_delta"]["after"][0]["sha256"],
        )
        self.assert_execution_current()

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
                    datetime(2030, 7, 25, 3, 0, 0, tzinfo=UTC),
                    datetime(2030, 7, 25, 3, 0, 0, 125000, tzinfo=UTC),
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
            "checks": [{"check_id": check["check_id"], "actual_exit_code": 0}],
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
                    "started_at": "2030-07-25T03:00:00.000Z",
                    "ended_at": "2030-07-25T03:00:00.125Z",
                    "wall_time_ms": 125,
                    "stdout_sha256": hashlib.sha256(FINALIZE_STDOUT).hexdigest(),
                    "stderr_sha256": hashlib.sha256(FINALIZE_STDERR).hexdigest(),
                    "stdout_bytes": len(FINALIZE_STDOUT),
                    "stderr_bytes": len(FINALIZE_STDERR),
                }
            ],
        }
        self.assertEqual(
            expected_checkpoint,
            self.read_json(f".work_packets/receipts/{TARGET_ID}.checkpoint.json"),
        )
        self.assertEqual(
            expected_acceptance,
            self.read_json(f".work_packets/receipts/{TARGET_ID}.acceptance.json"),
        )
        self.assertEqual(
            expected_execution,
            self.read_json(f".work_packets/receipts/{TARGET_ID}.execution.v2.json"),
        )

        target_after = self.read_json(self.packet_path(TARGET_ID))
        self.assertEqual("candidate_complete", target_after["state"])
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
            "controlled_claims_sha256": latest["controlled_snapshot"]["claims_sha256"],
            "checkpoint_path": (f".work_packets/receipts/{TARGET_ID}.checkpoint.json"),
            "checkpoint_canonical_sha256": execution.canonical_sha256(
                expected_checkpoint
            ),
            "acceptance_path": (f".work_packets/receipts/{TARGET_ID}.acceptance.json"),
            "acceptance_canonical_sha256": execution.canonical_sha256(
                expected_acceptance
            ),
            "execution_receipt_path": (
                f".work_packets/receipts/{TARGET_ID}.execution.v2.json"
            ),
            "execution_receipt_canonical_sha256": execution.canonical_sha256(
                expected_execution
            ),
            "completion_seal": None,
        }
        self.assertEqual(
            "candidate_complete",
            target_ledger["reported_state"],
        )
        self.assertEqual(expected_terminal, target_ledger["terminal_completion"])
        self.assertEqual(
            "pending",
            self.read_json(self.packet_path(SUCCESSOR_ID))["state"],
        )
        self.assertEqual(
            "pending",
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
