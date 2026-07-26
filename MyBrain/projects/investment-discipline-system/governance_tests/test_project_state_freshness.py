from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from scripts import derive_project_state as project_state


SOURCE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_POLICY = SOURCE_ROOT / "governance" / "PROJECT_STATE_VIEW_POLICY_V1.json"
DERIVER = SOURCE_ROOT / "scripts" / "derive_project_state.py"
START_MARKER = b"<!-- PROJECT_STATE_VIEW:START -->"
END_MARKER = b"<!-- PROJECT_STATE_VIEW:END -->"
VIEW_PATHS = ("STATUS.md", "TASK_BOARD.md", "LOOP_RUN_LOG.md")


class ProjectStateFreshnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "project"
        (self.root / "governance").mkdir(parents=True)
        (self.root / ".work_packets" / "packets").mkdir(parents=True)
        self.write_bytes(
            "governance/PROJECT_STATE_VIEW_POLICY_V1.json",
            SOURCE_POLICY.read_bytes(),
        )
        self.write_json(
            "governance/ACCEPTANCE_CONTRACT_V1.json",
            {
                "schema_version": 1,
                "contract_id": "fixture-contract-v1",
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
                            "id": "CHALLENGE-05",
                            "result": "blocked_freeze",
                            "major_findings": ["legacy text only"],
                        },
                        {
                            "id": "CHALLENGE-08",
                            "review_sequence": 8,
                            "result": "blocked_freeze",
                            "major_findings": ["legacy text only"],
                        },
                        self.review(
                            10,
                            [self.finding("F-STATE", ["ACT-ROOT"])],
                        ),
                    ]
                }
            },
        )
        self.write_packet(
            self.packet(
                "WP-ROOT",
                "ACT-ROOT",
                10,
                ["F-STATE"],
                summary="Repair canonical project-state freshness",
            )
        )
        for view in VIEW_PATHS:
            self.write_bytes(view, self.legacy_view_bytes(view))
        self.real_runtime_observer = project_state.observe_runtime_authorities
        self.runtime_patcher = mock.patch.object(
            project_state,
            "observe_runtime_authorities",
            side_effect=self.synthetic_runtime_authorities,
        )
        self.runtime_patcher.start()

    def tearDown(self) -> None:
        self.runtime_patcher.stop()
        self._temporary.cleanup()

    def write_bytes(self, relative: str, content: bytes) -> Path:
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def write_json(self, relative: str, value: Any) -> Path:
        return self.write_bytes(
            relative,
            (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode(),
        )

    def read_json(self, relative: str) -> dict[str, Any]:
        value = json.loads((self.root / relative).read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def finding(
        self,
        finding_id: str,
        required_action_ids: list[str],
        *,
        severity: str = "critical",
        state: str = "open",
    ) -> dict[str, Any]:
        return {
            "finding_id": finding_id,
            "severity": severity,
            "state": state,
            "required_action_ids": required_action_ids,
        }

    def review(
        self,
        sequence: int,
        findings: list[dict[str, Any]],
        *,
        result: str = "blocked_freeze",
    ) -> dict[str, Any]:
        hex_digit = format(sequence % 16, "x")
        evidence_digit = format((sequence + 1) % 16, "x")
        return {
            "id": f"CHALLENGE-{sequence}",
            "review_sequence": sequence,
            "candidate_commit": hex_digit * 40,
            "candidate_tree": format((sequence + 2) % 16, "x") * 40,
            "result": result,
            "evidence_path": f"audits/review-r{sequence}.md",
            "evidence_sha256": evidence_digit * 64,
            "findings": findings,
        }

    def packet(
        self,
        packet_id: str,
        action_id: str,
        route_order: int,
        finding_ids: list[str],
        *,
        state: str = "active",
        depends_on: list[str] | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "work-packet-instance/v2",
            "packet_id": packet_id,
            "state": state,
            "depends_on": [] if depends_on is None else depends_on,
            "routing": {
                "phase_id": "design_freeze",
                "action_id": action_id,
                "route_order": route_order,
                "addresses_finding_ids": finding_ids,
                "summary": summary or f"Execute {action_id}",
            },
            "owner": "fixture-builder",
        }

    def write_packet(self, packet: dict[str, Any]) -> Path:
        return self.write_json(
            f".work_packets/packets/{packet['packet_id']}.packet.json",
            packet,
        )

    def update_packet(self, packet_id: str, **updates: Any) -> dict[str, Any]:
        relative = f".work_packets/packets/{packet_id}.packet.json"
        packet = self.read_json(relative)
        packet.update(updates)
        self.write_json(relative, packet)
        return packet

    def register(self) -> dict[str, Any]:
        return self.read_json("governance/AI_PROJECT_RESEARCH_REGISTER_V1.json")

    def write_register(self, register: dict[str, Any]) -> None:
        self.write_json("governance/AI_PROJECT_RESEARCH_REGISTER_V1.json", register)

    def current_findings(self) -> list[dict[str, Any]]:
        rounds = self.register()["challenge"]["rounds"]
        return copy.deepcopy(rounds[-1]["findings"])

    def append_review(self, review: dict[str, Any]) -> None:
        register = self.register()
        register["challenge"]["rounds"].append(review)
        self.write_register(register)

    def synthetic_runtime_authorities(
        self,
        project_root: Path,
        _policy: dict[str, Any],
    ) -> dict[str, Any]:
        packet_records: list[dict[str, Any]] = []
        for path in sorted(
            (project_root / ".work_packets/packets").glob("*.packet.json")
        ):
            document = json.loads(path.read_text(encoding="utf-8"))
            packet_records.append(
                {
                    "path": path.relative_to(project_root).as_posix(),
                    "canonical_sha256": project_state.canonical_sha256(document),
                    "packet_id": document.get("packet_id"),
                    "state": document.get("state"),
                }
            )
        packet_digest = project_state.canonical_sha256(packet_records)
        complete_count = sum(
            record["state"] == "complete" for record in packet_records
        )
        authority_basis = [
            {
                "packet_id": record["packet_id"],
                "packet_path": record["path"],
                "packet_contract_sha256": record["canonical_sha256"],
                "reported_state": record["state"],
                "ledger_path": f"fixture://{record['packet_id']}",
                "ledger_canonical_sha256": record["canonical_sha256"],
                "latest_record_sha256": record["canonical_sha256"],
                "latest_claims_sha256": record["canonical_sha256"],
                "pre_v2_exemption": False,
            }
            for record in packet_records
        ]
        return {
            "work_packets": {
                "status": "pass",
                "policy_id": "fixture-work-packets",
                "receipt_sha256": packet_digest,
                "completion_verified_count": complete_count,
                "superseded_receipt_verified_count": 0,
                "dag_edges": [],
                "root_packet_ids": [],
                "sink_packet_ids": [],
            },
            "execution_freshness": {
                "verification_status": "valid",
                "execution_freshness_status": "current",
                "policy_id": "fixture-execution",
                "receipt_sha256": packet_digest,
                "tracked_packet_count": len(packet_records),
                "verified_ledger_count": len(packet_records),
                "exempt_packet_count": 0,
                "authority_basis": authority_basis,
            },
        }

    def legacy_view_bytes(self, view: str) -> bytes:
        return (
            f"# Existing title for {view}\r\n"
            f"outside-before:{view}\r\n"
        ).encode() + (
            START_MARKER
            + b"\nlegacy R5 phase/review/action with a copied digest\n"
            + END_MARKER
        ) + f"\r\noutside-after:{view}\r\n".encode()

    def derive(self, **observations: str) -> dict[str, Any]:
        return project_state.derive_projection(
            self.root,
            observed_head=observations.get("observed_head"),
            observed_tree=observations.get("observed_tree"),
            generated_at=observations.get("generated_at"),
        )

    def refresh(self) -> dict[str, Any]:
        return project_state.refresh_project_state(self.root)

    def assert_rejected(self, expected: str) -> None:
        with self.assertRaisesRegex(project_state.ProjectStateError, expected):
            self.derive()

    def test_nonempty_legacy_r5_blocks_are_not_a_green_freshness_signal(self) -> None:
        for view in VIEW_PATHS:
            data = (self.root / view).read_bytes()
            self.assertIn(b"Existing title", data)
            self.assertIn(b"legacy R5", data)
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "views are stale",
        ):
            project_state.check_project_state(self.root)

    def test_each_visible_component_tamper_is_rejected_byte_for_byte(self) -> None:
        projection = self.refresh()
        baselines = {
            view: (self.root / view).read_bytes()
            for view in VIEW_PATHS
        }
        digest = projection["basis"]["state_basis_sha256"]
        cases = (
            ("STATUS.md", b'"state": "blocked"', b'"state": "passed"'),
            ("TASK_BOARD.md", b'"review_sequence": 10', b'"review_sequence": 5'),
            ("LOOP_RUN_LOG.md", b'"action_id": "ACT-ROOT"', b'"action_id": "ACT-OLD"'),
            (
                "STATUS.md",
                f'"state_basis_sha256": "{digest}"'.encode(),
                b'"state_basis_sha256": "' + b"0" * 64 + b'"',
            ),
        )
        for view, needle, replacement in cases:
            with self.subTest(view=view, needle=needle):
                for path, baseline in baselines.items():
                    self.write_bytes(path, baseline)
                data = (self.root / view).read_bytes()
                self.assertIn(needle, data)
                self.write_bytes(view, data.replace(needle, replacement, 1))
                with self.assertRaisesRegex(
                    project_state.ProjectStateError,
                    "views are stale",
                ):
                    project_state.check_project_state(self.root)

    def test_new_later_blocked_review_requires_refresh(self) -> None:
        self.refresh()
        findings = self.current_findings()
        findings.append(self.finding("F-R11", ["ACT-R11"], severity="major"))
        self.append_review(self.review(11, findings))
        self.write_packet(self.packet("WP-R11", "ACT-R11", 20, ["F-R11"]))

        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "views are stale",
        ):
            project_state.check_project_state(self.root)

    def test_review_sequence_duplicate_is_rejected(self) -> None:
        duplicate = self.review(10, self.current_findings())
        duplicate["id"] = "CHALLENGE-10-DUPLICATE"
        self.append_review(duplicate)
        self.assert_rejected("duplicate value")

    def test_review_sequence_descending_is_rejected_even_below_projection_floor(self) -> None:
        self.append_review(
            {
                "id": "CHALLENGE-09-LATE",
                "review_sequence": 9,
                "result": "blocked_freeze",
            }
        )
        self.assert_rejected("strictly increasing")

    def test_projection_review_sequences_must_be_contiguous_from_ten(self) -> None:
        self.append_review(self.review(12, self.current_findings()))
        self.assert_rejected("contiguous from 10")

    def configure_two_action_graph(self) -> None:
        findings = [
            self.finding("F-STATE", ["ACT-ROOT", "ACT-REVIEW"]),
            self.finding("F-DAG", ["ACT-DAG"], severity="major"),
        ]
        register = self.register()
        register["challenge"]["rounds"][-1]["findings"] = findings
        self.write_register(register)
        self.write_packet(
            self.packet(
                "WP-DAG",
                "ACT-DAG",
                20,
                ["F-DAG"],
                state="pending",
                depends_on=["WP-ROOT"],
            )
        )
        self.write_packet(
            self.packet(
                "WP-REVIEW",
                "ACT-REVIEW",
                30,
                ["F-STATE"],
                state="pending",
                depends_on=["WP-ROOT"],
            )
        )

    def test_action_completion_makes_the_visible_next_action_stale(self) -> None:
        self.configure_two_action_graph()
        projection = self.refresh()
        self.assertEqual("WP-ROOT", projection["next_action"]["packet_id"])

        self.update_packet("WP-ROOT", state="complete")
        derived = self.derive()
        self.assertEqual("WP-DAG", derived["next_action"]["packet_id"])
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "views are stale",
        ):
            project_state.check_project_state(self.root)

    def test_dependency_change_makes_the_visible_basis_and_action_stale(self) -> None:
        findings = [
            self.finding("F-STATE", ["ACT-ROOT"]),
            self.finding("F-DAG", ["ACT-DAG"], severity="major"),
        ]
        register = self.register()
        register["challenge"]["rounds"][-1]["findings"] = findings
        self.write_register(register)
        self.write_packet(self.packet("WP-DAG", "ACT-DAG", 20, ["F-DAG"]))
        before = self.refresh()
        self.assertEqual("WP-ROOT", before["next_action"]["packet_id"])

        self.update_packet("WP-ROOT", depends_on=["WP-DAG"])
        after = self.derive()
        self.assertEqual("WP-DAG", after["next_action"]["packet_id"])
        self.assertNotEqual(
            before["basis"]["state_basis_sha256"],
            after["basis"]["state_basis_sha256"],
        )
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "views are stale",
        ):
            project_state.check_project_state(self.root)

    def test_packet_completion_cannot_close_an_open_finding(self) -> None:
        self.update_packet("WP-ROOT", state="complete")
        self.assert_rejected("open findings have no nonterminal packet")

    def test_only_a_later_review_can_close_a_finding(self) -> None:
        resolved = self.finding(
            "F-STATE",
            ["ACT-ROOT"],
            state="resolved",
        )
        replacement = self.finding(
            "F-R11",
            ["ACT-R11"],
            severity="major",
        )
        self.append_review(self.review(11, [resolved, replacement]))
        self.write_packet(self.packet("WP-R11", "ACT-R11", 20, ["F-R11"]))

        projection = self.derive()
        self.assertEqual(
            ["F-R11"],
            projection["latest_blocking_review"]["open_finding_ids"],
        )
        self.assertEqual("WP-R11", projection["next_action"]["packet_id"])

    def test_open_finding_without_packet_fails_closed(self) -> None:
        register = self.register()
        register["challenge"]["rounds"][-1]["findings"].append(
            self.finding("F-UNROUTED", ["ACT-MISSING"], severity="major")
        )
        self.write_register(register)
        self.assert_rejected("open findings have no nonterminal packet")

    def test_support_packet_without_finding_address_is_selected_from_target_closure(
        self,
    ) -> None:
        register = self.register()
        register["challenge"]["rounds"][-1]["findings"] = [
            self.finding("F-STATE", ["ACT-TARGET"])
        ]
        self.write_register(register)
        self.write_packet(
            self.packet(
                "WP-ROOT",
                "ACT-SUPPORT",
                10,
                [],
                summary="Build the prerequisite used by the finding target",
            )
        )
        self.write_packet(
            self.packet(
                "WP-TARGET",
                "ACT-TARGET",
                20,
                ["F-STATE"],
                state="pending",
                depends_on=["WP-ROOT"],
            )
        )

        before = self.derive()
        self.assertEqual("WP-ROOT", before["next_action"]["packet_id"])
        self.update_packet("WP-ROOT", state="complete")
        after = self.derive()
        self.assertEqual("WP-TARGET", after["next_action"]["packet_id"])

    def test_unaddressed_packet_outside_target_dependency_closure_is_not_selected(
        self,
    ) -> None:
        self.write_packet(
            self.packet("WP-UNRELATED", "ACT-UNRELATED", 1, [])
        )
        projection = self.derive()
        self.assertEqual("WP-ROOT", projection["next_action"]["packet_id"])

    def test_equal_route_order_is_rejected_as_global_ambiguity(self) -> None:
        register = self.register()
        finding = register["challenge"]["rounds"][-1]["findings"][0]
        finding["required_action_ids"].append("ACT-SECOND")
        self.write_register(register)
        self.write_packet(
            self.packet("WP-SECOND", "ACT-SECOND", 10, ["F-STATE"])
        )
        self.assert_rejected("route_order 10: ambiguous")

    def test_dependency_cycle_fails_closed(self) -> None:
        register = self.register()
        finding = register["challenge"]["rounds"][-1]["findings"][0]
        finding["required_action_ids"].append("ACT-SECOND")
        self.write_register(register)
        self.update_packet("WP-ROOT", depends_on=["WP-SECOND"])
        self.write_packet(
            self.packet(
                "WP-SECOND",
                "ACT-SECOND",
                20,
                ["F-STATE"],
                depends_on=["WP-ROOT"],
            )
        )
        self.assert_rejected("dependency cycle")

    def test_correct_digest_does_not_rescue_old_visible_words(self) -> None:
        projection = self.refresh()
        digest = projection["basis"]["state_basis_sha256"].encode()
        path = self.root / "STATUS.md"
        data = path.read_bytes()
        self.assertIn(digest, data)
        tampered = data.replace(
            b'"summary": "Repair canonical project-state freshness"',
            b'"summary": "Continue the obsolete R5 action"',
            1,
        )
        self.assertIn(digest, tampered)
        path.write_bytes(tampered)
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "views are stale",
        ):
            project_state.check_project_state(self.root)

    def test_projection_contains_no_head_tree_time_or_self_hash_fields(self) -> None:
        projection = self.derive(
            observed_head="a" * 40,
            observed_tree="b" * 40,
            generated_at="2099-01-01T00:00:00Z",
        )
        forbidden = {
            "head_commit",
            "head_tree",
            "observed_head",
            "observed_tree",
            "generated_at",
            "projection_sha256",
        }

        def keys(value: Any) -> set[str]:
            if isinstance(value, dict):
                result = set(value)
                for child in value.values():
                    result.update(keys(child))
                return result
            if isinstance(value, list):
                result: set[str] = set()
                for child in value:
                    result.update(keys(child))
                return result
            return set()

        self.assertEqual(set(), forbidden & keys(projection))

    def test_unrelated_observed_head_change_cannot_change_pure_fact_basis(self) -> None:
        left = self.derive(
            observed_head="a" * 40,
            observed_tree="b" * 40,
            generated_at="2026-01-01T00:00:00Z",
        )
        right = self.derive(
            observed_head="c" * 40,
            observed_tree="d" * 40,
            generated_at="2027-01-01T00:00:00Z",
        )
        self.assertEqual(left, right)
        self.assertEqual(
            left["basis"]["state_basis_sha256"],
            right["basis"]["state_basis_sha256"],
        )

    def test_refresh_preserves_all_outside_bytes_and_is_idempotent(self) -> None:
        before: dict[str, tuple[bytes, bytes]] = {}
        for view in VIEW_PATHS:
            data = (self.root / view).read_bytes()
            start = data.index(START_MARKER)
            end = data.index(END_MARKER) + len(END_MARKER)
            before[view] = (data[:start], data[end:])

        self.refresh()
        once = {view: (self.root / view).read_bytes() for view in VIEW_PATHS}
        for view, data in once.items():
            start = data.index(START_MARKER)
            end = data.index(END_MARKER) + len(END_MARKER)
            self.assertEqual(before[view][0], data[:start])
            self.assertEqual(before[view][1], data[end:])

        self.refresh()
        twice = {view: (self.root / view).read_bytes() for view in VIEW_PATHS}
        self.assertEqual(once, twice)

    def test_refresh_preflight_failure_does_not_partially_write_other_views(self) -> None:
        baselines = {
            view: (self.root / view).read_bytes()
            for view in VIEW_PATHS
        }
        broken = baselines["LOOP_RUN_LOG.md"].replace(END_MARKER, b"BROKEN-END")
        self.write_bytes("LOOP_RUN_LOG.md", broken)
        expected_untouched = {
            "STATUS.md": baselines["STATUS.md"],
            "TASK_BOARD.md": baselines["TASK_BOARD.md"],
        }
        with self.assertRaisesRegex(
            project_state.ProjectStateError,
            "markers must each occur once",
        ):
            self.refresh()
        for view, expected in expected_untouched.items():
            self.assertEqual(expected, (self.root / view).read_bytes())

    def test_derive_cli_emits_only_one_canonical_json_value(self) -> None:
        with mock.patch.object(
            project_state,
            "observe_runtime_authorities",
            self.real_runtime_observer,
        ):
            projection = project_state.derive_projection(SOURCE_ROOT)
        completed = subprocess.run(
            [
                sys.executable,
                str(DERIVER),
                "derive",
                "--project-root",
                str(SOURCE_ROOT),
            ],
            check=False,
            capture_output=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr.decode())
        self.assertEqual(b"", completed.stderr)
        self.assertEqual(
            project_state.canonical_json_bytes(projection) + b"\n",
            completed.stdout,
        )

    def test_cli_check_accepts_current_production_projection(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(DERIVER),
                "check",
                "--project-root",
                str(SOURCE_ROOT),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_missing_structured_r10_review_fails_closed_without_guessing(self) -> None:
        register = self.register()
        register["challenge"]["rounds"] = register["challenge"]["rounds"][:-1]
        self.write_register(register)
        self.assert_rejected("no complete projection review")

    def test_projection_review_without_findings_schema_fails_closed(self) -> None:
        register = self.register()
        register["challenge"]["rounds"][-1].pop("findings")
        self.write_register(register)
        self.assert_rejected("missing fields.*findings")

    def test_live_v1_packet_without_routing_fails_closed(self) -> None:
        packet = self.read_json(
            ".work_packets/packets/WP-ROOT.packet.json"
        )
        packet["schema_version"] = "work-packet-instance/v1"
        packet["superseded_by"] = "WP-SUCCESSOR"
        packet.pop("depends_on")
        packet.pop("routing")
        self.write_packet(packet)
        self.assert_rejected("only superseded state is allowed")

    def test_superseded_v1_packet_is_retained_but_excluded_from_live_routing(
        self,
    ) -> None:
        self.write_packet(
            {
                "schema_version": "work-packet-instance/v1",
                "packet_id": "WP-HISTORICAL",
                "state": "superseded",
                "superseded_by": "WP-ROOT",
            }
        )
        projection = self.derive()
        self.assertEqual("WP-ROOT", projection["next_action"]["packet_id"])
        historical_facts = [
            fact
            for fact in projection["basis"]["facts"]
            if fact["path"].endswith("WP-HISTORICAL.packet.json")
        ]
        self.assertEqual(1, len(historical_facts))

    def test_superseded_v1_packet_requires_a_live_v2_successor(self) -> None:
        self.write_packet(
            {
                "schema_version": "work-packet-instance/v1",
                "packet_id": "WP-HISTORICAL",
                "state": "superseded",
                "superseded_by": "WP-MISSING",
            }
        )
        self.assert_rejected("superseding live V2 packet.*is missing")

    def test_authority_file_existence_alone_never_completes_phase(self) -> None:
        self.write_json(
            "governance/FROZEN_BUNDLE_V1.json",
            {"unverified": True},
        )
        projection = self.derive()
        self.assertEqual("blocked", projection["phase"]["state"])
        self.assertIn(
            "GATE-DESIGN-FREEZE-AUTHORITY-VERIFICATION-UNSUPPORTED",
            projection["phase"]["blocking_gate_ids"],
        )


if __name__ == "__main__":
    unittest.main()
