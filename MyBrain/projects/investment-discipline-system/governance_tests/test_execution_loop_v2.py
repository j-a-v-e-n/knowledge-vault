from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

from scripts import derive_project_state as state
from scripts import verify_execution_loop_v2 as execution
from scripts import verify_work_packets as work_packets


SOURCE_ROOT = Path(__file__).resolve().parents[1]
POLICY_RELATIVE = Path("governance/EXECUTION_LOOP_POLICY_V2.json")
PACKET_DIRECTORY = Path(".work_packets/packets")
EXEMPT_PACKET_ID = "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def blocker(root_cause_id: str, status_after: str) -> dict[str, Any]:
    value = {
        "root_cause_id": root_cause_id,
        "failure_ids": [],
        "root_cause": root_cause_id.replace("-", " ").title(),
        "status_after": status_after,
    }
    value["fingerprint_sha256"] = execution.canonical_sha256(
        {
            "root_cause_id": value["root_cause_id"],
            "failure_ids": value["failure_ids"],
            "root_cause": value["root_cause"],
        }
    )
    return value


def empty_failure_delta() -> dict[str, list[Any]]:
    return {"before": [], "after": [], "resolved": [], "introduced": []}


def empty_evidence_delta() -> dict[str, list[Any]]:
    return {"before": [], "after": [], "added": [], "removed": []}


def unknown_cost() -> dict[str, Any]:
    return {
        "wall_time_source": "timestamps",
        "token_usage": {
            "availability": "unknown",
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "measurement_source": None,
        },
    }


def no_process_observation(mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "argv": None,
        "exit_code": None,
        "stdout_sha256": None,
        "stderr_sha256": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "capture_authority": (
            "tool_observed_baseline"
            if mode == "baseline"
            else "self_reported_no_process"
        ),
    }


def rehash_attempts(ledger: dict[str, Any]) -> None:
    previous: dict[str, Any] | None = None
    for attempt in ledger["attempts"]:
        attempt["previous_attempt_sha256"] = (
            None
            if previous is None
            else execution.canonical_sha256(previous)
        )
        without_record = {
            key: value
            for key, value in attempt.items()
            if key != "record_sha256"
        }
        attempt["record_sha256"] = execution.canonical_sha256(without_record)
        previous = attempt


class ExecutionLoopV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.copy_fixture()
        self.build_ledgers()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def copy_one(self, relative: str) -> None:
        source = SOURCE_ROOT / relative
        target = self.root / relative
        if not source.exists():
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)

    def copy_fixture(self) -> None:
        packet_sources = sorted(
            (SOURCE_ROOT / PACKET_DIRECTORY).glob("*.packet.json")
        )
        for packet_source in packet_sources:
            relative = packet_source.relative_to(SOURCE_ROOT).as_posix()
            self.copy_one(relative)

        paths = {
            POLICY_RELATIVE.as_posix(),
            "governance/WORK_PACKET_POLICY_V2.json",
            "governance/EXECUTION_LOOP_POLICY_V1.json",
            "scripts/verify_execution_loop.py",
            ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json",
            "STATUS.md",
            "TASK_BOARD.md",
            "LOOP_RUN_LOG.md",
        }
        for packet_source in packet_sources:
            packet = json.loads(packet_source.read_text(encoding="utf-8"))
            for claim in packet["bounded_write_paths"]:
                if not claim["path"].endswith(".attempts.v2.json"):
                    paths.add(claim["path"])
            paths.update(packet["read_dependencies"])
            for field in ("checkpoint_path", "acceptance_receipt_path"):
                if packet.get(field):
                    paths.add(packet[field])
        for exemption in execution.EXPECTED_EXEMPTIONS:
            paths.add(exemption["checkpoint_path"])
            paths.add(exemption["acceptance_path"])
        for relative in sorted(paths):
            self.copy_one(relative)

    def packet_path(self, packet_id: str) -> Path:
        return self.root / PACKET_DIRECTORY / f"{packet_id}.packet.json"

    def ledger_path(self, packet_id: str) -> Path:
        return self.root / execution.ledger_path_for(packet_id)

    def build_ledgers(self) -> None:
        resolved_root = self.root.resolve()
        packet_paths = sorted(
            (self.root / PACKET_DIRECTORY).glob("*.packet.json")
        )
        packets = {
            packet["packet_id"]: packet
            for path in packet_paths
            for packet in [json.loads(path.read_text(encoding="utf-8"))]
            if packet["schema_version"] == "work-packet-instance/v2"
        }
        live_ids = set(packets)
        for packet_id, packet in sorted(packets.items()):
            if packet_id == EXEMPT_PACKET_ID:
                continue
            excluded, claims = execution.current_claim_snapshots(
                resolved_root,
                packet,
                live_ids,
                [],
            )
            pending = packet["state"] == "pending"
            attempt = {
                "schema_version": "execution-attempt/v2",
                "attempt_kind": (
                    "baseline_observation" if pending else "execution_attempt"
                ),
                "sequence": 1,
                "retry_index": None if pending else 0,
                "started_at": "2026-07-26T00:00:00.000Z",
                "ended_at": "2026-07-26T00:00:00.000Z",
                "wall_time_ms": 0,
                "blocker": blocker(
                    (
                        "WAITING-FOR-PREREQUISITE"
                        if pending
                        else "ACTIVE-WORK-OBSERVATION"
                    ),
                    "waiting" if pending else "open",
                ),
                "failure_delta": empty_failure_delta(),
                "evidence_delta": empty_evidence_delta(),
                "controlled_snapshot": {
                    "algorithm": execution.EXPECTED_CURRENT_SNAPSHOT[
                        "algorithm"
                    ],
                    "excluded_paths": excluded,
                    "claims": claims,
                    "claims_sha256": execution.canonical_sha256(claims),
                },
                "process_observation": no_process_observation(
                    "baseline" if pending else "passive"
                ),
                "cost_observation": unknown_cost(),
                "declared_progress": False,
                "previous_attempt_sha256": None,
                "record_sha256": "",
            }
            ledger = {
                "schema_version": "execution-attempt-ledger/v2",
                "packet_id": packet_id,
                "packet_path": (
                    PACKET_DIRECTORY / f"{packet_id}.packet.json"
                ).as_posix(),
                "packet_contract_sha256": (
                    work_packets.packet_contract_sha256(packet)
                ),
                "reported_state": packet["state"],
                "cost_accounting_claim": "partial",
                "initial_state": {
                    "failure_ids": [],
                    "evidence": [],
                },
                "terminal_completion": None,
                "attempts": [attempt],
            }
            rehash_attempts(ledger)
            write_json(self.ledger_path(packet_id), ledger)

    def receipt(self) -> dict[str, Any]:
        return execution.verify(self.root, POLICY_RELATIVE)

    def assert_valid(self) -> dict[str, Any]:
        receipt = self.receipt()
        self.assertEqual("valid", receipt["verification_status"], receipt)
        self.assertEqual("current", receipt["execution_freshness_status"])
        self.assertEqual([], receipt["errors"])
        return receipt

    def assert_invalid(self, text: str) -> dict[str, Any]:
        receipt = self.receipt()
        self.assertEqual("invalid", receipt["verification_status"], receipt)
        self.assertTrue(
            any(text in error for error in receipt["errors"]),
            receipt["errors"],
        )
        return receipt

    def mutate_ledger(
        self,
        packet_id: str,
        mutator: Callable[[dict[str, Any]], None],
        *,
        rehash: bool,
    ) -> None:
        path = self.ledger_path(packet_id)
        ledger = json.loads(path.read_text(encoding="utf-8"))
        mutator(ledger)
        if rehash:
            rehash_attempts(ledger)
        write_json(path, ledger)

    def append_execution_attempt(
        self,
        packet_id: str,
        *,
        status_after: str = "open",
        root_cause_id: str = "ACTIVE-WORK-OBSERVATION",
        failure_before: list[str] | None = None,
        failure_after: list[str] | None = None,
        added_evidence: list[dict[str, Any]] | None = None,
    ) -> None:
        packet = json.loads(
            self.packet_path(packet_id).read_text(encoding="utf-8")
        )
        live_ids = {
            json.loads(path.read_text(encoding="utf-8"))["packet_id"]
            for path in (self.root / PACKET_DIRECTORY).glob("*.packet.json")
            if json.loads(path.read_text(encoding="utf-8")).get(
                "schema_version"
            )
            == "work-packet-instance/v2"
        }
        excluded, claims = execution.current_claim_snapshots(
            self.root.resolve(),
            packet,
            live_ids,
            [],
        )

        def mutate(ledger: dict[str, Any]) -> None:
            previous = ledger["attempts"][-1]
            previous_failures = previous["failure_delta"]["after"]
            previous_evidence = previous["evidence_delta"]["after"]
            before_failures = sorted(
                previous_failures if failure_before is None else failure_before
            )
            after_failures = sorted(
                before_failures if failure_after is None else failure_after
            )
            before_evidence = sorted(
                previous_evidence,
                key=execution.evidence_identity,
            )
            additions = sorted(
                added_evidence or [],
                key=execution.evidence_identity,
            )
            after_evidence = sorted(
                [*before_evidence, *additions],
                key=execution.evidence_identity,
            )
            sequence = len(ledger["attempts"]) + 1
            timestamp = f"2026-07-26T00:00:{sequence:02d}.000Z"
            attempt = {
                "schema_version": "execution-attempt/v2",
                "attempt_kind": "execution_attempt",
                "sequence": sequence,
                "retry_index": sum(
                    item["attempt_kind"] == "execution_attempt"
                    for item in ledger["attempts"]
                ),
                "started_at": timestamp,
                "ended_at": timestamp,
                "wall_time_ms": 0,
                "blocker": blocker(root_cause_id, status_after),
                "failure_delta": {
                    "before": before_failures,
                    "after": after_failures,
                    "resolved": sorted(
                        set(before_failures) - set(after_failures)
                    ),
                    "introduced": sorted(
                        set(after_failures) - set(before_failures)
                    ),
                },
                "evidence_delta": {
                    "before": before_evidence,
                    "after": after_evidence,
                    "added": additions,
                    "removed": [],
                },
                "controlled_snapshot": {
                    "algorithm": execution.EXPECTED_CURRENT_SNAPSHOT[
                        "algorithm"
                    ],
                    "excluded_paths": excluded,
                    "claims": claims,
                    "claims_sha256": execution.canonical_sha256(claims),
                },
                "process_observation": no_process_observation("passive"),
                "cost_observation": unknown_cost(),
                "declared_progress": bool(
                    additions
                    or set(before_failures) - set(after_failures)
                ),
                "previous_attempt_sha256": None,
                "record_sha256": "",
            }
            ledger["attempts"].append(attempt)

        self.mutate_ledger(packet_id, mutate, rehash=True)

    def evidence_reference(
        self,
        relative: str,
        *,
        supports: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "path": relative,
            "sha256": hashlib.sha256(
                (self.root / relative).read_bytes()
            ).hexdigest(),
            "kind": "other",
            "supports_failure_ids": sorted(supports or []),
        }

    def test_generated_fixture_is_current(self) -> None:
        receipt = self.assert_valid()
        self.assertEqual(7, receipt["tracked_packet_count"])
        self.assertEqual(6, receipt["verified_ledger_count"])
        self.assertEqual(1, receipt["exempt_packet_count"])

    def test_pending_packet_requires_baseline_ledger(self) -> None:
        self.ledger_path("WP-CI-LINT-BASELINE").unlink()
        self.assert_invalid("V2 ledger file set differs")

    def test_pending_controlled_content_change_requires_new_observation(self) -> None:
        path = self.root / "governance/RUFF_CI_CONFIG_V1.toml"
        path.write_text(
            path.read_text(encoding="utf-8") + "\n# stale mutation\n",
            encoding="utf-8",
        )
        self.assert_invalid("latest controlled snapshot is stale")

    def test_active_controlled_policy_change_requires_new_observation(self) -> None:
        path = self.root / "governance/PROJECT_STATE_VIEW_POLICY_V1.json"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nstale\n",
            encoding="utf-8",
        )
        self.assert_invalid("latest controlled snapshot is stale")

    def test_generated_views_are_excluded_to_break_state_ledger_recursion(
        self,
    ) -> None:
        path = self.root / "STATUS.md"
        path.write_text(
            path.read_text(encoding="utf-8") + "\nderived view mutation\n",
            encoding="utf-8",
        )
        self.assert_valid()

    def test_packet_contract_change_invalidates_ledger_binding(self) -> None:
        path = self.packet_path("WP-METHOD-INTEGRATION")
        packet = json.loads(path.read_text(encoding="utf-8"))
        packet["retry_budget"] += 1
        write_json(path, packet)
        self.assert_invalid("packet or schema binding differs")

    def test_weakening_same_blocker_threshold_is_rejected(self) -> None:
        path = self.root / POLICY_RELATIVE
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["stopping_rules"][
            "same_blocker_consecutive_no_progress_threshold"
        ] = 4
        write_json(path, policy)
        self.assert_invalid("policy.stopping_rules")

    def test_record_hash_tampering_is_rejected(self) -> None:
        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            lambda ledger: ledger["attempts"][0].__setitem__(
                "record_sha256",
                "0" * 64,
            ),
            rehash=False,
        )
        self.assert_invalid("record hash differs")

    def test_duplicate_json_key_is_rejected(self) -> None:
        path = self.ledger_path("WP-CI-LINT-BASELINE")
        raw = path.read_text(encoding="utf-8")
        path.write_text(
            raw.replace(
                '{\n  "attempts"',
                '{\n  "schema_version": "execution-attempt-ledger/v2",'
                '\n  "attempts"',
                1,
            ),
            encoding="utf-8",
        )
        self.assert_invalid("duplicate JSON key")

    def test_nonfinite_json_is_rejected(self) -> None:
        path = self.ledger_path("WP-CI-LINT-BASELINE")
        raw = path.read_text(encoding="utf-8")
        path.write_text(
            raw.replace('"reported_state": "pending"', '"reported_state": NaN'),
            encoding="utf-8",
        )
        self.assert_invalid("non-standard JSON constant")

    def test_extra_v2_ledger_is_rejected(self) -> None:
        write_json(
            self.root / ".work_packets/attempts/WP-EXTRA.attempts.v2.json",
            {},
        )
        self.assert_invalid("extra=['.work_packets/attempts/WP-EXTRA")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_nested_tree_symlink_is_rejected(self) -> None:
        tree = self.root / "research/evidence/r10"
        target = self.root / "STATUS.md"
        os.symlink(target, tree / "forbidden-symlink")
        self.assert_invalid("nested write symlink")

    def test_baseline_cannot_claim_progress(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            ledger["attempts"][0]["declared_progress"] = True

        self.mutate_ledger("WP-CI-LINT-BASELINE", mutate, rehash=True)
        self.assert_invalid("declared_progress differs")

    def test_controlled_claims_hash_tampering_is_rejected(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            ledger["attempts"][0]["controlled_snapshot"][
                "claims_sha256"
            ] = "0" * 64

        self.mutate_ledger("WP-CI-LINT-BASELINE", mutate, rehash=True)
        self.assert_invalid("controlled claims hash differs")

    def test_reported_state_must_match_packet(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            ledger["reported_state"] = "active"

        self.mutate_ledger("WP-CI-LINT-BASELINE", mutate, rehash=True)
        self.assert_invalid("packet or schema binding differs")

    def test_legacy_history_hash_is_enforced(self) -> None:
        path = (
            self.root
            / ".work_packets/attempts/WP-METHOD-INTEGRATION.attempts.json"
        )
        path.write_text(
            path.read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )
        self.assert_invalid("legacy artifact")

    def test_pre_v2_exemption_receipt_is_exactly_bound(self) -> None:
        path = (
            self.root
            / ".work_packets/receipts/"
            "WP-CONTRACT-SUPERSESSION-CLOSURE-POLICY.acceptance.json"
        )
        receipt = json.loads(path.read_text(encoding="utf-8"))
        receipt["checks"][0]["actual_exit_code"] = 1
        write_json(path, receipt)
        self.assert_invalid("acceptance: digest differs")

    def test_unknown_cost_forces_partial_claim(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            ledger["cost_accounting_claim"] = "measured"

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid("cost accounting claim differs")

    def test_three_identical_no_progress_attempts_require_blocked(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            first = ledger["attempts"][0]
            for sequence in (2, 3):
                item = json.loads(json.dumps(first))
                item["sequence"] = sequence
                item["retry_index"] = sequence - 1
                ledger["attempts"].append(item)

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid("three identical no-progress blockers")

    def test_rotating_blocker_labels_cannot_reset_no_progress_limit(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            first = ledger["attempts"][0]
            for sequence in (2, 3):
                item = json.loads(json.dumps(first))
                item["sequence"] = sequence
                item["retry_index"] = sequence - 1
                item["blocker"] = blocker(
                    f"ROTATED-BLOCKER-{sequence}",
                    "open",
                )
                ledger["attempts"].append(item)

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid(
            "three consecutive no-progress attempts require blocked"
        )

    def test_pending_baseline_cannot_be_followed_by_execution_attempt(self) -> None:
        self.append_execution_attempt("WP-CI-LINT-BASELINE")
        self.assert_invalid(
            "pending ledger must contain exactly one baseline observation"
        )

    def test_failure_state_must_be_continuous_across_attempts(self) -> None:
        evidence = self.evidence_reference(
            "governance/EXECUTION_LOOP_POLICY_V2.json",
            supports=["FAKE-01"],
        )
        self.append_execution_attempt(
            "WP-METHOD-RUNTIME-FOUNDATION",
            failure_before=["FAKE-01"],
            failure_after=[],
            added_evidence=[evidence],
        )
        self.assert_invalid(
            "failure state is not continuous with prior attempt"
        )

    def test_evidence_state_must_be_continuous_across_attempts(self) -> None:
        evidence = self.evidence_reference(
            "governance/EXECUTION_LOOP_POLICY_V2.json"
        )
        self.append_execution_attempt(
            "WP-METHOD-RUNTIME-FOUNDATION",
            added_evidence=[evidence],
        )
        self.append_execution_attempt("WP-METHOD-RUNTIME-FOUNDATION")

        def mutate(ledger: dict[str, Any]) -> None:
            latest = ledger["attempts"][-1]
            latest["evidence_delta"]["before"] = []
            latest["evidence_delta"]["added"] = latest["evidence_delta"]["after"]

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid(
            "evidence state is not continuous with prior attempt"
        )

    def test_forced_stop_prefix_cannot_be_erased_by_fourth_progress(self) -> None:
        packet_id = "WP-METHOD-RUNTIME-FOUNDATION"
        self.append_execution_attempt(
            packet_id,
            root_cause_id="ROTATED-BLOCKER-TWO",
        )
        self.append_execution_attempt(
            packet_id,
            root_cause_id="ROTATED-BLOCKER-THREE",
        )
        evidence = self.evidence_reference(
            "governance/EXECUTION_LOOP_POLICY_V2.json"
        )
        self.append_execution_attempt(
            packet_id,
            status_after="resolved",
            root_cause_id="FOURTH-ATTEMPT-PROGRESS",
            added_evidence=[evidence],
        )
        self.assert_invalid("forced stop is absorbing")

    def test_retry_budget_cannot_end_resolved_without_acceptance(self) -> None:
        packet_id = "WP-METHOD-RUNTIME-FOUNDATION"
        self.append_execution_attempt(packet_id)
        evidence = self.evidence_reference(
            "governance/EXECUTION_LOOP_POLICY_V2.json"
        )
        self.append_execution_attempt(
            packet_id,
            status_after="resolved",
            added_evidence=[evidence],
        )
        self.assert_invalid("exhausted retry budget must remain blocked")

    def test_blocker_fingerprint_is_recomputed(self) -> None:
        def mutate(ledger: dict[str, Any]) -> None:
            ledger["attempts"][0]["blocker"]["root_cause"] = "renamed"

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid("fingerprint differs")

    def test_packet_file_cannot_be_progress_evidence(self) -> None:
        packet_id = "WP-METHOD-RUNTIME-FOUNDATION"

        def mutate(ledger: dict[str, Any]) -> None:
            attempt = ledger["attempts"][0]
            relative = (
                ".work_packets/packets/"
                "WP-METHOD-RUNTIME-FOUNDATION.packet.json"
            )
            reference = {
                "path": relative,
                "sha256": hashlib.sha256(
                    (self.root / relative).read_bytes()
                ).hexdigest(),
                "kind": "other",
                "supports_failure_ids": [],
            }
            attempt["evidence_delta"]["after"] = [reference]
            attempt["evidence_delta"]["added"] = [reference]
            attempt["declared_progress"] = True

        self.mutate_ledger(packet_id, mutate, rehash=True)
        self.assert_invalid("packet and ledger files cannot be evidence")

    def test_unrelated_file_cannot_be_progress_evidence(self) -> None:
        unrelated = self.root / "unrelated-proof.txt"
        unrelated.write_text("not controlled\n", encoding="utf-8")

        def mutate(ledger: dict[str, Any]) -> None:
            attempt = ledger["attempts"][0]
            reference = {
                "path": "unrelated-proof.txt",
                "sha256": hashlib.sha256(unrelated.read_bytes()).hexdigest(),
                "kind": "other",
                "supports_failure_ids": [],
            }
            attempt["evidence_delta"]["after"] = [reference]
            attempt["evidence_delta"]["added"] = [reference]
            attempt["declared_progress"] = True

        self.mutate_ledger(
            "WP-METHOD-RUNTIME-FOUNDATION",
            mutate,
            rehash=True,
        )
        self.assert_invalid("progress evidence is outside controlled writes")

    def test_attempt_ledger_claim_is_rejected_as_runtime_sidecar(self) -> None:
        path = self.packet_path("WP-METHOD-INTEGRATION")
        packet = json.loads(path.read_text(encoding="utf-8"))
        packet["bounded_write_paths"].append(
            {
                "path": ".work_packets/attempts/NOT-A-PACKET.attempts.v2.json",
                "kind": "file",
            }
        )
        write_json(path, packet)
        self.assert_invalid("derived runtime sidecars")

    def test_state_derivation_fails_closed_when_v2_ledger_is_missing(self) -> None:
        self.assert_valid()
        self.ledger_path("WP-CI-LINT-BASELINE").unlink()
        with self.assertRaisesRegex(
            state.ProjectStateError,
            "execution-freshness verifier failed",
        ):
            state.derive_projection(self.root)

    def test_valid_ledger_tail_change_makes_generated_views_stale(self) -> None:
        state.refresh_project_state(self.root)
        state.check_project_state(self.root)

        def mutate(ledger: dict[str, Any]) -> None:
            attempt = ledger["attempts"][0]
            attempt["started_at"] = "2026-07-26T00:00:01.000Z"
            attempt["ended_at"] = "2026-07-26T00:00:01.000Z"

        self.mutate_ledger(
            "WP-CI-LINT-BASELINE",
            mutate,
            rehash=True,
        )
        self.assert_valid()
        with self.assertRaisesRegex(
            state.ProjectStateError,
            "project state views are stale",
        ):
            state.check_project_state(self.root)

    def test_self_reported_complete_cannot_advance_state_projection(self) -> None:
        path = self.packet_path("WP-METHOD-RUNTIME-FOUNDATION")
        packet = json.loads(path.read_text(encoding="utf-8"))
        packet["state"] = "complete"
        write_json(path, packet)
        with self.assertRaisesRegex(
            state.ProjectStateError,
            "work-packet verifier failed",
        ):
            state.derive_projection(self.root)


if __name__ == "__main__":
    unittest.main()
