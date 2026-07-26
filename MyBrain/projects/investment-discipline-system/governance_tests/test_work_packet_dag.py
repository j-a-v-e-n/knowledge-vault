from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_work_packets.py"
SOURCE_POLICY = SOURCE_ROOT / "governance" / "WORK_PACKET_POLICY_V2.json"
V1_CONTRACT_FIELDS = (
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
)
V2_CONTRACT_FIELDS = V1_CONTRACT_FIELDS + (
    "depends_on",
    "activates",
    "integration_invariants",
    "routing",
)


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class WorkPacketDagVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "project"
        self.packet_directory = self.root / "packets"
        self.receipt_directory = self.root / ".work_packets" / "receipts"
        self.policy_path = self.root / "governance" / "WORK_PACKET_POLICY_V2.json"
        for directory in (
            self.packet_directory,
            self.receipt_directory,
            self.policy_path.parent,
            self.root / "src" / "branches",
            self.root / "src" / "join",
            self.root / "shared",
        ):
            directory.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_POLICY, self.policy_path)
        for relative, value in (
            ("src/root.json", 1),
            ("src/branches/a.json", 2),
            ("src/branches/b.json", 3),
            ("src/branches/shared.json", 4),
            ("src/join/result.json", 5),
            ("shared/input.json", 6),
        ):
            self.write_text(relative, json.dumps({"value": value}) + "\n")
        self.receipts: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}

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

    def checks(self) -> list[dict[str, Any]]:
        return [
            {
                "check_id": "CHECK-FOCUSED",
                "kind": "process_exit",
                "argv": ["python3", "-m", "unittest", "focused"],
                "expected_exit_code": 0,
            },
            {
                "check_id": "CHECK-INTEGRATION",
                "kind": "process_exit",
                "argv": ["python3", "-m", "unittest", "integration"],
                "expected_exit_code": 0,
            },
        ]

    def integration(
        self,
        *inputs: tuple[str, str],
        probe_id: str = "CHECK-INTEGRATION",
    ) -> list[dict[str, Any]]:
        return [
            {
                "invariant_id": "INV-INTEGRATION",
                "inputs": [
                    {"packet_id": packet_id, "path": path}
                    for packet_id, path in inputs
                ],
                "probe_check_ids": [probe_id],
            }
        ]

    def packet(
        self,
        packet_id: str,
        write_path: str,
        *,
        state: str = "active",
        goal_id: str = "GOAL-ORG",
        depends_on: list[str] | None = None,
        activates: list[str] | None = None,
        reads: list[str] | None = None,
        integration_invariants: list[dict[str, Any]] | None = None,
        external_side_effects: list[str] | None = None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "work-packet-instance/v2",
            "packet_id": packet_id,
            "goal_id": goal_id,
            "state": state,
            "owner": f"owner-{packet_id.lower()}",
            "reviewer": f"reviewer-{packet_id.lower()}",
            "bounded_write_paths": [{"path": write_path, "kind": "file"}],
            "read_dependencies": [] if reads is None else reads,
            "acceptance_checks": self.checks(),
            "checkpoint_path": None,
            "acceptance_receipt_path": None,
            "retry_budget": 2,
            "external_side_effects": (
                [] if external_side_effects is None else external_side_effects
            ),
            "semantic_invariants": [],
            "depends_on": [] if depends_on is None else depends_on,
            "activates": [] if activates is None else activates,
            "integration_invariants": (
                [] if integration_invariants is None else integration_invariants
            ),
            "routing": {
                "phase_id": "design_freeze",
                "action_id": f"ACT-{packet_id.removeprefix('WP-')}",
                "route_order": (
                    int(hashlib.sha256(packet_id.encode()).hexdigest()[:8], 16)
                    + 1
                ),
                "addresses_finding_ids": [],
                "summary": f"Execute {packet_id}",
            },
        }

    def v1_packet(
        self,
        packet_id: str,
        write_path: str,
        *,
        state: str,
    ) -> dict[str, Any]:
        packet = self.packet(packet_id, write_path, state=state)
        for field in (
            "depends_on",
            "activates",
            "integration_invariants",
            "routing",
        ):
            del packet[field]
        packet["schema_version"] = "work-packet-instance/v1"
        return packet

    def write_packet(self, packet: dict[str, Any]) -> Path:
        return self.write_json(
            f"packets/{packet['packet_id']}.packet.json",
            packet,
        )

    def add_receipts(
        self,
        packet: dict[str, Any],
        *,
        include_acceptance: bool = True,
    ) -> None:
        packet_id = packet["packet_id"]
        checkpoint_relative = (
            f".work_packets/receipts/{packet_id}.checkpoint.json"
        )
        acceptance_relative = (
            f".work_packets/receipts/{packet_id}.acceptance.json"
        )
        packet["checkpoint_path"] = checkpoint_relative
        packet["acceptance_receipt_path"] = (
            acceptance_relative if include_acceptance else None
        )
        fields = (
            V2_CONTRACT_FIELDS
            if packet["schema_version"] == "work-packet-instance/v2"
            else V1_CONTRACT_FIELDS
        )
        contract_digest = canonical_sha256(
            {field: packet[field] for field in fields}
        )
        snapshots = []
        for claim in packet["bounded_write_paths"]:
            snapshots.append(
                {
                    "path": claim["path"],
                    "kind": claim["kind"],
                    "state": "file",
                    "content_sha256": hashlib.sha256(
                        (self.root / claim["path"]).read_bytes()
                    ).hexdigest(),
                }
            )
        if packet["schema_version"] == "work-packet-instance/v2":
            prerequisite_receipts = []
            for dependency_id in sorted(packet["depends_on"]):
                dependency_checkpoint, dependency_acceptance = self.receipts[
                    dependency_id
                ]
                dependency_packet = json.loads(
                    (
                        self.packet_directory
                        / f"{dependency_id}.packet.json"
                    ).read_text(encoding="utf-8")
                )
                prerequisite_receipts.append(
                    {
                        "packet_id": dependency_id,
                        "packet_contract_sha256": canonical_sha256(
                            {
                                field: dependency_packet[field]
                                for field in V2_CONTRACT_FIELDS
                            }
                        ),
                        "checkpoint_receipt_sha256": canonical_sha256(
                            dependency_checkpoint
                        ),
                        "acceptance_receipt_sha256": canonical_sha256(
                            dependency_acceptance
                        ),
                    }
                )
            checkpoint = {
                "schema_version": "work-packet-checkpoint/v2",
                "packet_id": packet_id,
                "packet_contract_sha256": contract_digest,
                "sequence": 1,
                "snapshots": snapshots,
                "prerequisite_receipts": prerequisite_receipts,
            }
            acceptance_schema = "work-packet-acceptance/v2"
        else:
            checkpoint = {
                "schema_version": "work-packet-checkpoint/v1",
                "packet_id": packet_id,
                "packet_contract_sha256": contract_digest,
                "sequence": 1,
                "snapshots": snapshots,
            }
            acceptance_schema = "work-packet-acceptance/v1"
        acceptance = {
            "schema_version": acceptance_schema,
            "packet_id": packet_id,
            "packet_contract_sha256": contract_digest,
            "checkpoint_receipt_sha256": canonical_sha256(checkpoint),
            "checks": [
                {
                    "check_id": check["check_id"],
                    "actual_exit_code": check["expected_exit_code"],
                }
                for check in packet["acceptance_checks"]
            ],
        }
        self.write_packet(packet)
        self.write_json(checkpoint_relative, checkpoint)
        if include_acceptance:
            self.write_json(acceptance_relative, acceptance)
            self.receipts[packet_id] = (checkpoint, acceptance)

    def run_verifier(self) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        completed = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--project-root",
                str(self.root),
                "--policy",
                "governance/WORK_PACKET_POLICY_V2.json",
                "--packet-dir",
                "packets",
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(
                f"verifier did not emit one JSON result: {exc}\n"
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

    def write_parallel_graph(
        self,
        *,
        a_path: str = "src/branches/a.json",
        b_path: str = "src/branches/b.json",
        a_state: str = "active",
        b_state: str = "active",
        join_state: str = "pending",
        a_reads: list[str] | None = None,
        b_reads: list[str] | None = None,
        a_effects: list[str] | None = None,
        b_effects: list[str] | None = None,
        join_integration: list[dict[str, Any]] | None = None,
        join_reads: list[str] | None = None,
    ) -> dict[str, dict[str, Any]]:
        if join_integration is None:
            join_integration = self.integration(
                ("WP-A", a_path),
                ("WP-B", b_path),
            )
        if join_reads is None:
            join_reads = list(dict.fromkeys((a_path, b_path)))
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=["WP-A", "WP-B"],
        )
        branch_a = self.packet(
            "WP-A",
            a_path,
            state=a_state,
            depends_on=["WP-ROOT"],
            activates=["WP-JOIN"],
            reads=a_reads,
            external_side_effects=a_effects,
        )
        branch_b = self.packet(
            "WP-B",
            b_path,
            state=b_state,
            depends_on=["WP-ROOT"],
            activates=["WP-JOIN"],
            reads=b_reads,
            external_side_effects=b_effects,
        )
        join = self.packet(
            "WP-JOIN",
            "src/join/result.json",
            state=join_state,
            depends_on=["WP-A", "WP-B"],
            reads=join_reads,
            integration_invariants=join_integration,
        )
        self.add_receipts(root)
        for packet in (branch_a, branch_b, join):
            self.write_packet(packet)
        return {
            "root": root,
            "a": branch_a,
            "b": branch_b,
            "join": join,
        }

    def test_healthy_root_parallel_branches_join_with_bound_probe(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=["WP-A", "WP-B"],
        )
        branch_a = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="complete",
            depends_on=["WP-ROOT"],
            activates=["WP-JOIN"],
        )
        branch_b = self.packet(
            "WP-B",
            "src/branches/b.json",
            state="complete",
            depends_on=["WP-ROOT"],
            activates=["WP-JOIN"],
        )
        join = self.packet(
            "WP-JOIN",
            "src/join/result.json",
            state="complete",
            depends_on=["WP-A", "WP-B"],
            reads=["src/branches/a.json", "src/branches/b.json"],
            integration_invariants=self.integration(
                ("WP-A", "src/branches/a.json"),
                ("WP-B", "src/branches/b.json"),
            ),
        )
        for packet in (root, branch_a, branch_b, join):
            self.add_receipts(packet)

        payload = self.assert_passes()
        self.assertEqual(
            [
                ["WP-A", "WP-JOIN"],
                ["WP-B", "WP-JOIN"],
                ["WP-ROOT", "WP-A"],
                ["WP-ROOT", "WP-B"],
            ],
            payload["dag_edges"],
        )
        self.assertEqual(["WP-ROOT"], payload["root_packet_ids"])
        self.assertEqual(["WP-JOIN"], payload["sink_packet_ids"])
        self.assertEqual([], payload["activatable_packet_ids"])
        self.assertEqual({}, payload["blocked_by"])
        self.assertEqual(1, payload["integration_probe_declared_count"])
        self.assertEqual(1, payload["integration_probe_verified_count"])
        self.assertEqual(4, payload["completion_verified_count"])

    def test_missing_dependency_is_rejected(self) -> None:
        self.write_packet(
            self.packet(
                "WP-A",
                "src/branches/a.json",
                state="pending",
                depends_on=["WP-MISSING"],
            )
        )
        self.assert_rejected("depends_on packet 'WP-MISSING' is missing")

    def test_self_dependency_is_rejected(self) -> None:
        self.write_packet(
            self.packet(
                "WP-A",
                "src/branches/a.json",
                state="pending",
                depends_on=["WP-A"],
                activates=["WP-A"],
            )
        )
        self.assert_rejected("self depends_on reference is forbidden")

    def test_duplicate_dependency_is_rejected(self) -> None:
        packet = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="pending",
            depends_on=["WP-ROOT", "WP-ROOT"],
        )
        self.write_packet(packet)
        self.assert_rejected("depends_on: duplicate entries are forbidden")

    def test_empty_finding_addresses_are_valid_for_support_packets(self) -> None:
        packet = self.packet("WP-A", "src/branches/a.json")
        self.assertEqual([], packet["routing"]["addresses_finding_ids"])
        self.write_packet(packet)
        self.assert_passes()

    def test_route_order_is_globally_unique_across_live_goals(self) -> None:
        left = self.packet(
            "WP-A",
            "src/branches/a.json",
            goal_id="GOAL-A",
        )
        right = self.packet(
            "WP-B",
            "src/branches/b.json",
            goal_id="GOAL-B",
        )
        right["routing"]["route_order"] = left["routing"]["route_order"]
        self.write_packet(left)
        self.write_packet(right)
        self.assert_rejected("routing route_order")

    def test_action_id_is_globally_unique_across_live_goals(self) -> None:
        left = self.packet(
            "WP-A",
            "src/branches/a.json",
            goal_id="GOAL-A",
        )
        right = self.packet(
            "WP-B",
            "src/branches/b.json",
            goal_id="GOAL-B",
        )
        right["routing"]["action_id"] = left["routing"]["action_id"]
        self.write_packet(left)
        self.write_packet(right)
        self.assert_rejected("routing action_id")

    def test_malformed_routing_finding_identifier_is_rejected(self) -> None:
        packet = self.packet("WP-A", "src/branches/a.json")
        packet["routing"]["addresses_finding_ids"] = ["bad finding id"]
        self.write_packet(packet)
        self.assert_rejected("invalid routing finding identifier")

    def test_routing_requires_the_exact_declared_fields(self) -> None:
        packet = self.packet("WP-A", "src/branches/a.json")
        packet["routing"].pop("summary")
        self.write_packet(packet)
        self.assert_rejected("routing: fields differ; missing=['summary']")

    def test_cycle_is_rejected_by_kahn(self) -> None:
        packet_a = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="pending",
            depends_on=["WP-B"],
            activates=["WP-B"],
            reads=["src/branches/b.json"],
            integration_invariants=self.integration(
                ("WP-B", "src/branches/b.json")
            ),
        )
        packet_b = self.packet(
            "WP-B",
            "src/branches/b.json",
            state="pending",
            depends_on=["WP-A"],
            activates=["WP-A"],
            reads=["src/branches/a.json"],
            integration_invariants=self.integration(
                ("WP-A", "src/branches/a.json")
            ),
        )
        self.write_packet(packet_a)
        self.write_packet(packet_b)
        self.assert_rejected("DAG cycle detected")

    def test_one_sided_activates_tampering_is_rejected(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=[],
        )
        child = self.packet(
            "WP-A",
            "src/branches/a.json",
            depends_on=["WP-ROOT"],
            reads=["src/root.json"],
            integration_invariants=self.integration(("WP-ROOT", "src/root.json")),
        )
        self.add_receipts(root)
        self.write_packet(child)
        self.assert_rejected("depends_on is not matched by activates")

    def test_cross_goal_dependency_is_rejected(self) -> None:
        first = self.packet(
            "WP-A",
            "src/branches/a.json",
            goal_id="GOAL-A",
            activates=["WP-B"],
        )
        second = self.packet(
            "WP-B",
            "src/branches/b.json",
            state="pending",
            goal_id="GOAL-B",
            depends_on=["WP-A"],
        )
        self.write_packet(first)
        self.write_packet(second)
        self.assert_rejected("belongs to a different goal")

    def test_dependency_on_superseded_history_is_rejected(self) -> None:
        historical = self.v1_packet(
            "WP-OLD",
            "src/branches/a.json",
            state="complete",
        )
        self.add_receipts(historical)
        historical["state"] = "superseded"
        historical["superseded_by"] = "WP-NEW"
        self.write_packet(historical)
        self.write_packet(
            self.packet(
                "WP-NEW",
                "src/branches/a.json",
                state="active",
            )
        )
        self.write_packet(
            self.packet(
                "WP-DOWN",
                "src/branches/b.json",
                state="pending",
                depends_on=["WP-OLD"],
            )
        )
        self.assert_rejected("depends_on packet 'WP-OLD' is superseded")

    def test_upstream_not_verified_complete_keeps_downstream_pending(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="active",
            activates=["WP-A"],
        )
        child = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="active",
            depends_on=["WP-ROOT"],
            reads=["src/root.json"],
            integration_invariants=self.integration(("WP-ROOT", "src/root.json")),
        )
        self.write_packet(root)
        self.write_packet(child)
        self.assert_rejected("downstream state must remain pending")

    def test_stale_pending_activation_is_rejected_and_reported(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=["WP-A"],
        )
        child = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="pending",
            depends_on=["WP-ROOT"],
            reads=["src/root.json"],
            integration_invariants=self.integration(("WP-ROOT", "src/root.json")),
        )
        self.add_receipts(root)
        self.write_packet(child)
        payload = self.assert_rejected("stale_pending_activation")
        self.assertEqual(["WP-A"], payload["activatable_packet_ids"])

    def test_blocked_propagation_reaches_descendants_not_siblings(self) -> None:
        self.write_parallel_graph(a_state="blocked", b_state="active")
        payload = self.assert_passes()
        self.assertEqual({"WP-JOIN": ["WP-A"]}, payload["blocked_by"])
        self.assertNotIn("WP-B", payload["blocked_by"])

    def test_parallel_write_write_conflict_is_rejected(self) -> None:
        self.write_parallel_graph(
            a_path="src/branches/shared.json",
            b_path="src/branches/shared.json",
        )
        self.assert_rejected("write/write conflict")

    def test_parallel_read_write_conflict_is_rejected(self) -> None:
        self.write_parallel_graph(a_reads=["src/branches/b.json"])
        self.assert_rejected("read/write conflict")

    def test_parallel_external_side_effect_conflict_is_rejected(self) -> None:
        self.write_parallel_graph(
            a_effects=["publish:artifact"],
            b_effects=["publish:artifact"],
        )
        self.assert_rejected("identical external side effect conflict")

    def test_join_without_invariant_is_rejected(self) -> None:
        self.write_parallel_graph(join_integration=[])
        self.assert_rejected("integration_invariant is required")

    def test_join_invariant_must_cover_every_direct_branch(self) -> None:
        invariant = self.integration(("WP-A", "src/branches/a.json"))
        self.write_parallel_graph(
            join_integration=invariant,
            join_reads=["src/branches/a.json"],
        )
        self.assert_rejected("integration inputs omit direct branches ['WP-B']")

    def test_join_input_path_must_be_owned_by_named_packet(self) -> None:
        invariant = self.integration(
            ("WP-A", "src/branches/b.json"),
            ("WP-B", "src/branches/b.json"),
        )
        self.write_parallel_graph(
            join_integration=invariant,
            join_reads=["src/branches/b.json"],
        )
        self.assert_rejected("is not owned by packet WP-A")

    def test_join_input_path_must_be_a_read_dependency(self) -> None:
        self.write_parallel_graph(join_reads=["src/branches/a.json"])
        self.assert_rejected("is not in join read_dependencies")

    def test_probe_id_must_reference_join_acceptance_check(self) -> None:
        invariant = self.integration(
            ("WP-A", "src/branches/a.json"),
            ("WP-B", "src/branches/b.json"),
            probe_id="CHECK-MISSING",
        )
        self.write_parallel_graph(join_integration=invariant)
        self.assert_rejected("probe check_id is not declared by join packet")

    def test_integration_probe_must_expect_success_exit(self) -> None:
        packets = self.write_parallel_graph()
        for check in packets["join"]["acceptance_checks"]:
            if check["check_id"] == "CHECK-INTEGRATION":
                check["expected_exit_code"] = 1
        self.write_packet(packets["join"])
        self.assert_rejected("integration probe check must expect exit 0")

    def test_multi_node_goal_with_zero_probe_declarations_is_rejected(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=["WP-A"],
        )
        child = self.packet(
            "WP-A",
            "src/branches/a.json",
            depends_on=["WP-ROOT"],
        )
        self.add_receipts(root)
        self.write_packet(child)
        self.assert_rejected("multi-node goal declares zero integration probes")

    def test_candidate_join_probe_requires_successful_bound_receipt(self) -> None:
        packets = self.write_parallel_graph(
            a_state="complete",
            b_state="complete",
            join_state="candidate_complete",
        )
        self.add_receipts(packets["a"])
        self.add_receipts(packets["b"])
        self.add_receipts(packets["join"], include_acceptance=False)
        self.assert_rejected("not verified by a valid successful acceptance receipt")

    def test_checkpoint_prerequisite_binding_is_exact(self) -> None:
        root = self.packet(
            "WP-ROOT",
            "src/root.json",
            state="complete",
            activates=["WP-A"],
        )
        child = self.packet(
            "WP-A",
            "src/branches/a.json",
            state="complete",
            depends_on=["WP-ROOT"],
            reads=["src/root.json"],
            integration_invariants=self.integration(("WP-ROOT", "src/root.json")),
        )
        self.add_receipts(root)
        self.add_receipts(child)
        checkpoint_path = ".work_packets/receipts/WP-A.checkpoint.json"
        acceptance_path = ".work_packets/receipts/WP-A.acceptance.json"
        checkpoint = json.loads(
            (self.root / checkpoint_path).read_text(encoding="utf-8")
        )
        checkpoint["prerequisite_receipts"][0][
            "packet_contract_sha256"
        ] = "0" * 64
        acceptance = json.loads(
            (self.root / acceptance_path).read_text(encoding="utf-8")
        )
        acceptance["checkpoint_receipt_sha256"] = canonical_sha256(checkpoint)
        self.write_json(checkpoint_path, checkpoint)
        self.write_json(acceptance_path, acceptance)
        self.assert_rejected(
            "prerequisite_receipts do not exactly bind direct dependencies"
        )

    def test_live_v1_packet_is_rejected_under_v2_policy(self) -> None:
        self.write_packet(
            self.v1_packet(
                "WP-A",
                "src/branches/a.json",
                state="active",
            )
        )
        self.assert_rejected("live V1 packet is forbidden under V2 policy")

    def test_superseded_v1_history_is_retained_under_v2_policy(self) -> None:
        historical = self.v1_packet(
            "WP-OLD",
            "src/branches/a.json",
            state="complete",
        )
        self.add_receipts(historical)
        historical["state"] = "superseded"
        historical["superseded_by"] = "WP-NEW"
        self.write_packet(historical)
        successor = self.packet(
            "WP-NEW",
            "src/branches/a.json",
            state="active",
        )
        self.write_packet(successor)

        payload = self.assert_passes()
        self.assertEqual(1, payload["superseded_receipt_verified_count"])
        self.assertEqual(["WP-NEW"], payload["root_packet_ids"])


if __name__ == "__main__":
    unittest.main()
