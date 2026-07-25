from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_work_packets.py"
SOURCE_POLICY = SOURCE_ROOT / "governance" / "WORK_PACKET_POLICY_V1.json"
CONTRACT_FIELDS = (
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


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class WorkPacketVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.base = Path(self._temporary.name)
        self.root = self.base / "project"
        self.outside = self.base / "outside"
        self.packet_directory = self.root / "packets"
        self.receipt_directory = self.root / ".work_packets" / "receipts"
        self.policy_path = self.root / "governance" / "WORK_PACKET_POLICY_V1.json"
        for directory in (
            self.packet_directory,
            self.receipt_directory,
            self.policy_path.parent,
            self.root / "src" / "feature",
            self.root / "shared",
            self.root / "limits",
            self.outside,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_POLICY, self.policy_path)
        self.write_text("src/feature/a.json", '{"value": 1}\n')
        self.write_text("src/feature/b.json", '{"value": 2}\n')
        self.write_text("shared/input.json", '{"source": "fixture"}\n')

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

    def packet(
        self,
        packet_id: str,
        write_path: str,
        *,
        kind: str = "file",
        state: str = "active",
        reads: list[str] | None = None,
        invariants: list[dict[str, Any]] | None = None,
        checkpoint_path: str | None = None,
        acceptance_receipt_path: str | None = None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "work-packet-instance/v1",
            "packet_id": packet_id,
            "goal_id": "GOAL-ORG",
            "state": state,
            "owner": f"owner-{packet_id.lower()}",
            "reviewer": f"reviewer-{packet_id.lower()}",
            "bounded_write_paths": [{"path": write_path, "kind": kind}],
            "read_dependencies": [] if reads is None else reads,
            "acceptance_checks": [
                {
                    "check_id": "CHECK-FOCUSED",
                    "kind": "process_exit",
                    "argv": ["python3", "-m", "unittest", "focused"],
                    "expected_exit_code": 0,
                }
            ],
            "checkpoint_path": checkpoint_path,
            "acceptance_receipt_path": acceptance_receipt_path,
            "retry_budget": 2,
            "external_side_effects": [],
            "semantic_invariants": [] if invariants is None else invariants,
        }

    def write_packet(self, packet: dict[str, Any]) -> Path:
        filename = f"{packet['packet_id']}.packet.json"
        return self.write_json(f"packets/{filename}", packet)

    def run_verifier(self) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        completed = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--project-root",
                str(self.root),
                "--policy",
                "governance/WORK_PACKET_POLICY_V1.json",
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

    def test_benign_disjoint_packets_allow_shared_read_dependencies(self) -> None:
        self.write_packet(
            self.packet(
                "WP-A",
                "src/feature/a.json",
                reads=["shared/input.json", "src/feature/b.json"],
            )
        )
        self.write_packet(
            self.packet(
                "WP-B",
                "src/feature/b.json",
                reads=["shared/input.json", "src/feature/a.json"],
            )
        )

        payload = self.assert_passes()
        self.assertEqual(2, payload["active_packet_count"])
        self.assertEqual(2, payload["ownership_claim_count"])
        self.assertEqual(0, payload["ownership_conflict_count"])
        self.assertEqual(5, len(payload["platform_and_process_limitations"]))

    def test_direct_duplicate_ownership_is_rejected(self) -> None:
        self.write_packet(self.packet("WP-A", "src/feature/a.json"))
        self.write_packet(self.packet("WP-B", "src/feature/a.json"))

        payload = self.assert_rejected("duplicate ownership")
        self.assertEqual(1, payload["ownership_conflict_count"])

    def test_parent_child_ownership_overlap_is_rejected(self) -> None:
        self.write_packet(self.packet("WP-A", "src/feature", kind="tree"))
        self.write_packet(self.packet("WP-B", "src/feature/b.json"))

        payload = self.assert_rejected("parent/child overlap")
        self.assertEqual(1, payload["ownership_conflict_count"])

    def test_symlink_canonical_escape_is_rejected(self) -> None:
        outside_file = self.outside / "outside.json"
        outside_file.write_text('{"outside": true}\n', encoding="utf-8")
        escape = self.root / "src" / "feature" / "escape.json"
        try:
            os.symlink(outside_file, escape)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.write_packet(self.packet("WP-A", "src/feature/escape.json"))

        self.assert_rejected("symlink/canonical path escapes project root")

    def test_broad_top_level_tree_scope_is_rejected(self) -> None:
        self.write_packet(self.packet("WP-A", "src", kind="tree"))

        self.assert_rejected("broad tree scope is forbidden")

    def test_complete_state_without_receipts_is_rejected(self) -> None:
        self.write_packet(
            self.packet(
                "WP-A",
                "src/feature/a.json",
                state="complete",
            )
        )

        payload = self.assert_rejected("checkpoint receipt is required")
        self.assertTrue(
            any(
                "acceptance receipt is required" in error
                for error in payload["errors"]
            ),
            payload["errors"],
        )
        self.assertEqual(0, payload["completion_verified_count"])

    def test_bound_checkpoint_and_acceptance_receipts_allow_completion(self) -> None:
        checkpoint_relative = ".work_packets/receipts/WP-A.checkpoint.json"
        acceptance_relative = ".work_packets/receipts/WP-A.acceptance.json"
        packet = self.packet(
            "WP-A",
            "src/feature/a.json",
            state="complete",
            checkpoint_path=checkpoint_relative,
            acceptance_receipt_path=acceptance_relative,
        )
        contract_digest = canonical_sha256(
            {field: packet[field] for field in CONTRACT_FIELDS}
        )
        file_digest = hashlib.sha256(
            (self.root / "src" / "feature" / "a.json").read_bytes()
        ).hexdigest()
        checkpoint = {
            "schema_version": "work-packet-checkpoint/v1",
            "packet_id": "WP-A",
            "packet_contract_sha256": contract_digest,
            "sequence": 1,
            "snapshots": [
                {
                    "path": "src/feature/a.json",
                    "kind": "file",
                    "state": "file",
                    "content_sha256": file_digest,
                }
            ],
        }
        acceptance = {
            "schema_version": "work-packet-acceptance/v1",
            "packet_id": "WP-A",
            "packet_contract_sha256": contract_digest,
            "checkpoint_receipt_sha256": canonical_sha256(checkpoint),
            "checks": [
                {
                    "check_id": "CHECK-FOCUSED",
                    "actual_exit_code": 0,
                }
            ],
        }
        self.write_packet(packet)
        self.write_json(checkpoint_relative, checkpoint)
        self.write_json(acceptance_relative, acceptance)

        payload = self.assert_passes()
        self.assertEqual(1, payload["completion_verified_count"])

    def test_disjoint_text_changes_can_fail_joint_semantic_invariant(self) -> None:
        invariant = {
            "invariant_id": "INV-ALLOCATION-CAP",
            "probe": "json_integer_sum_lte",
            "inputs": [
                {"path": "limits/alpha.json", "pointer": "/allocation"},
                {"path": "limits/beta.json", "pointer": "/allocation"},
            ],
            "maximum": 100,
        }
        self.write_packet(
            self.packet(
                "WP-A",
                "limits/alpha.json",
                reads=["limits/beta.json"],
                invariants=[invariant],
            )
        )
        self.write_packet(
            self.packet(
                "WP-B",
                "limits/beta.json",
                reads=["limits/alpha.json"],
                invariants=[invariant],
            )
        )

        self.write_text("limits/alpha.json", '{"allocation": 60}\n')
        self.write_text("limits/beta.json", '{"allocation": 0}\n')
        self.assert_passes()

        self.write_text("limits/alpha.json", '{"allocation": 0}\n')
        self.write_text("limits/beta.json", '{"allocation": 60}\n')
        self.assert_passes()

        self.write_text("limits/alpha.json", '{"allocation": 60}\n')
        self.write_text("limits/beta.json", '{"allocation": 60}\n')
        payload = self.assert_rejected(
            "sum 120 exceeds maximum 100"
        )
        self.assertEqual(0, payload["ownership_conflict_count"])
        self.assertEqual(1, payload["semantic_probe_count"])

    def test_root_traversal_glob_and_non_normalized_paths_are_rejected(self) -> None:
        cases = (
            (".", "repository root or home aliases are forbidden"),
            ("../outside/outside.json", "traversal"),
            ("src/*.json", "unresolved glob syntax"),
            ("src//feature/a.json", "non-normalized components"),
        )
        packet_path = self.packet_directory / "WP-A.packet.json"
        for path, expected in cases:
            with self.subTest(path=path):
                packet = self.packet("WP-A", path)
                packet_path.write_text(
                    json.dumps(packet, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                self.assert_rejected(expected)

    def test_packet_schema_rejects_unknown_fields(self) -> None:
        packet = self.packet("WP-A", "src/feature/a.json")
        packet["declared_safe"] = True
        self.write_packet(packet)

        self.assert_rejected("fields differ")

    def test_duplicate_json_keys_are_rejected(self) -> None:
        packet = self.packet("WP-A", "src/feature/a.json")
        encoded = json.dumps(packet, ensure_ascii=False)
        encoded = encoded.replace(
            '"packet_id": "WP-A"',
            '"packet_id": "WP-A", "packet_id": "WP-B"',
            1,
        )
        (self.packet_directory / "WP-A.packet.json").write_text(
            encoded + "\n",
            encoding="utf-8",
        )

        self.assert_rejected("duplicate JSON key 'packet_id'")


if __name__ == "__main__":
    unittest.main()
