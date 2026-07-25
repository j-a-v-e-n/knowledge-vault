from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = SOURCE_ROOT / "scripts" / "verify_context_recovery.py"
SPEC_RELATIVE = Path("governance") / "CONTEXT_RECOVERY_SPEC_V1.json"
STATE_FILES = [
    "PROJECT_CHARTER.md",
    "STATUS.md",
    "TASK_BOARD.md",
    "DECISIONS.md",
    "AI_COLLABORATION_METHOD.md",
]
PROBE_IDS = [
    "start",
    "middle",
    "end",
    "post_compaction",
    "empty_context_restart",
    "stale_request_regression",
]


class ContextRecoveryDesignFreezeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "governance").mkdir()
        shutil.copy2(SOURCE_ROOT / SPEC_RELATIVE, self.root / SPEC_RELATIVE)
        for relative in STATE_FILES:
            shutil.copy2(SOURCE_ROOT / relative, self.root / relative)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def spec_path(self) -> Path:
        return self.root / SPEC_RELATIVE

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--root",
                str(self.root),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def load_spec(self) -> dict[str, Any]:
        return json.loads(self.spec_path.read_text(encoding="utf-8"))

    def write_spec(self, spec: dict[str, Any]) -> None:
        self.spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def probe(self, spec: dict[str, Any], probe_id: str) -> dict[str, Any]:
        for probe in spec["probe_fixture"]["probes"]:
            if probe["probe_id"] == probe_id:
                return probe
        self.fail(f"missing test fixture probe {probe_id}")

    def assert_oracle(
        self,
        result: subprocess.CompletedProcess[str],
        oracle_id: str,
    ) -> dict[str, Any]:
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("fail", payload["status"])
        oracle_ids = [error["oracle_id"] for error in payload["errors"]]
        self.assertIn(oracle_id, oracle_ids, payload["errors"])
        return payload

    def assert_spec_mutation_rejected(
        self,
        mutation: Callable[[dict[str, Any]], None],
        oracle_id: str,
    ) -> dict[str, Any]:
        baseline = self.run_verifier()
        self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)
        spec = self.load_spec()
        mutation(spec)
        self.write_spec(spec)
        return self.assert_oracle(self.run_verifier(), oracle_id)

    def test_benign_fixture_exercises_every_required_recovery(self) -> None:
        result = self.run_verifier()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["errors"])
        observations = payload["probe_receipt"]["observations"]
        self.assertEqual(
            PROBE_IDS,
            [observation["probe_id"] for observation in observations],
        )
        state_files = payload["derived_from"]["state_packet_files"]
        self.assertEqual(
            STATE_FILES,
            [observation["path"] for observation in state_files],
        )
        for observation in state_files:
            self.assertGreater(observation["byte_count"], 0)
            self.assertTrue(observation["sha256"])
            self.assertTrue(observation["marker_offsets"])
        boundary = payload["claim_boundary"]
        self.assertIn("real LLM recall", boundary["does_not_prove"])
        self.assertIn(
            "unknown-position statistical coverage",
            boundary["does_not_prove"],
        )

    def test_removed_middle_sentinel_hits_missing_sentinel_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            middle = self.probe(spec, "middle")
            middle["context_segments"] = [
                segment
                for segment in middle["context_segments"]
                if segment["kind"] != "sentinel"
            ]

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-PROBE-MIDDLE-SENTINEL-MISSING",
        )

    def test_moved_middle_sentinel_hits_position_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            segments = self.probe(spec, "middle")["context_segments"]
            sentinel = segments.pop(2)
            segments.append(sentinel)

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-PROBE-MIDDLE-SENTINEL-POSITION",
        )

    def test_contradicted_middle_sentinel_hits_content_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            middle = self.probe(spec, "middle")
            sentinel = next(
                segment
                for segment in middle["context_segments"]
                if segment["kind"] == "sentinel"
            )
            sentinel["payload"]["target_id"] = (
                "TARGET-CTX02-LABEL-CHECK-ONLY"
            )

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-PROBE-MIDDLE-SENTINEL-CONTRADICTED",
        )

    def test_empty_required_state_file_hits_byte_oracle(self) -> None:
        baseline = self.run_verifier()
        self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)
        (self.root / "STATUS.md").write_bytes(b"")
        self.assert_oracle(
            self.run_verifier(),
            "CTX02-STATE-NONEMPTY",
        )

    def test_stale_current_target_hits_current_target_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            spec["probe_fixture"]["current_request"]["target_id"] = (
                "TARGET-CTX02-LABEL-CHECK-ONLY"
            )

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-CURRENT-TARGET-STALE",
        )

    def test_omitted_restart_recovery_hits_restart_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            self.probe(spec, "empty_context_restart").pop("restart_packet")

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-PROBE-RESTART-RECOVERY-MISSING",
        )

    def test_omitted_post_compaction_recovery_hits_compaction_oracle(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            self.probe(spec, "post_compaction")["context_segments"] = []

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-PROBE-COMPACTION-RECOVERY-MISSING",
        )

    def test_receipt_claim_cannot_override_derived_observation(self) -> None:
        def mutate(spec: dict[str, Any]) -> None:
            observation = next(
                item
                for item in spec["expected_probe_receipt"]["observations"]
                if item["probe_id"] == "stale_request_regression"
            )
            observation["selected_target_id"] = (
                "TARGET-CTX02-LABEL-CHECK-ONLY"
            )

        self.assert_spec_mutation_rejected(
            mutate,
            "CTX02-RECEIPT-CONTRACT",
        )

    def test_duplicate_json_key_is_rejected_fail_closed(self) -> None:
        baseline = self.run_verifier()
        self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)
        text = self.spec_path.read_text(encoding="utf-8")
        text = text.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 1,',
            1,
        )
        self.spec_path.write_text(text, encoding="utf-8")
        self.assert_oracle(
            self.run_verifier(),
            "CTX02-SPEC-STRICT-JSON",
        )


if __name__ == "__main__":
    unittest.main()
