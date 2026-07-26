from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.verify_research_source_manifest import verify_manifest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "research" / "evidence" / "r10" / "SOURCE_MANIFEST.json"
VERIFIER = PROJECT_ROOT / "scripts" / "verify_research_source_manifest.py"


class ResearchSourceManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def verify(self, manifest: dict) -> dict:
        return verify_manifest(manifest, project_root=PROJECT_ROOT)

    def test_real_manifest_binds_all_declared_bytes_and_report_ids(self) -> None:
        receipt = self.verify(self.manifest)
        self.assertEqual("valid", receipt["verification_status"], receipt)
        self.assertEqual([], receipt["errors"])
        self.assertNotIn("status", receipt)
        self.assertIn("F-S11", receipt["covered_report_source_ids"])
        self.assertIn("M-P06", receipt["covered_report_source_ids"])

    def test_snapshot_hash_mismatch_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][1]["snapshot_artifacts"][0]["sha256"] = "0" * 64
        receipt = self.verify(manifest)
        self.assertEqual("invalid", receipt["verification_status"])
        self.assertTrue(
            any("sha256 mismatch" in error for error in receipt["errors"]),
            receipt,
        )

    def test_snapshot_byte_count_mismatch_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][2]["snapshot_artifacts"][0]["byte_count"] += 1
        receipt = self.verify(manifest)
        self.assertEqual("invalid", receipt["verification_status"])
        self.assertTrue(
            any("byte_count mismatch" in error for error in receipt["errors"]),
            receipt,
        )

    def test_report_source_id_without_manifest_disposition_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["excluded_mutable_field_sources"]["source_ids"].remove("M-P06")
        receipt = self.verify(manifest)
        self.assertEqual("invalid", receipt["verification_status"])
        self.assertTrue(
            any("M-P06" in error for error in receipt["errors"]),
            receipt,
        )

    def test_retained_status_without_artifact_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][2]["snapshot_artifacts"] = []
        receipt = self.verify(manifest)
        self.assertEqual("invalid", receipt["verification_status"])
        self.assertTrue(
            any(
                "retained snapshot status and artifact presence differ" in error
                for error in receipt["errors"]
            ),
            receipt,
        )

    def test_duplicate_source_id_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["sources"][1]["source_ids"].append("M-S03")
        receipt = self.verify(manifest)
        self.assertEqual("invalid", receipt["verification_status"])
        self.assertTrue(
            any("duplicate source id M-S03" in error for error in receipt["errors"]),
            receipt,
        )

    def test_cli_emits_one_machine_receipt(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--project-root",
                str(PROJECT_ROOT),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("", completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("valid", payload["verification_status"], payload)
        self.assertEqual(1, completed.stdout.count("\n"))


if __name__ == "__main__":
    unittest.main()
