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
VERIFIER = SOURCE_ROOT / "scripts" / "verify_migration_drill.py"
SPEC_RELATIVE = Path("governance") / "MIGRATION_DRILL_SPEC_V1.json"
PROTECTED_RELATIVES = [
    SPEC_RELATIVE,
    Path("governance") / "PROJECT_METHOD_POLICY_V1.json",
    Path("governance") / "WORK_PACKET_POLICY_V1.json",
]


class MigrationDrillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in PROTECTED_RELATIVES:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_ROOT / relative, destination)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def spec_path(self) -> Path:
        return self.root / SPEC_RELATIVE

    def run_verifier(
        self, fault_mode: str = "none"
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                str(VERIFIER),
                "--root",
                str(self.root),
                "--fault-mode",
                fault_mode,
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def payload(self, result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
        self.assertTrue(result.stdout, result.stderr)
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"verifier did not emit machine JSON: {exc}: {result.stdout!r}")
        self.assertIsInstance(value, dict)
        return value

    def assert_oracle(
        self,
        result: subprocess.CompletedProcess[str],
        oracle_id: str,
    ) -> dict[str, Any]:
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        payload = self.payload(result)
        self.assertEqual("fail", payload["status"])
        oracle_ids = [error["oracle_id"] for error in payload["errors"]]
        self.assertIn(oracle_id, oracle_ids, payload["errors"])
        return payload

    def protected_manifest(self) -> list[tuple[str, int, str]]:
        manifest: list[tuple[str, int, str]] = []
        for relative in PROTECTED_RELATIVES:
            raw = (self.root / relative).read_bytes()
            manifest.append(
                (
                    relative.as_posix(),
                    len(raw),
                    hashlib.sha256(raw).hexdigest(),
                )
            )
        return manifest

    def test_benign_drill_executes_migration_failure_repeat_rollback_and_exit(
        self,
    ) -> None:
        before = self.protected_manifest()
        result = self.run_verifier()
        after = self.protected_manifest()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = self.payload(result)
        self.assertEqual("pass", payload["status"])
        self.assertEqual([], payload["errors"])
        self.assertEqual(before, after)

        drill = payload["drill"]
        self.assertEqual("work-packet-instance/v1", drill["source_version"])
        self.assertEqual("work-packet-instance/v2-drill", drill["target_version"])
        self.assertTrue(drill["source_sha256"])
        self.assertTrue(drill["target_sha256"])
        self.assertNotEqual(drill["source_sha256"], drill["target_sha256"])

        self.assertEqual(
            {"executed": True, "no_write": True}, drill["dry_run"]
        )
        self.assertTrue(drill["backup"]["created"])
        self.assertTrue(drill["backup"]["exact_bytes"])
        self.assertTrue(drill["backup"]["sidecar_verified"])
        self.assertTrue(drill["backup"]["precedes_first_replace"])
        self.assertEqual(drill["source_sha256"], drill["backup"]["sha256"])

        failure = drill["failure_injection"]
        self.assertTrue(failure["executed"])
        self.assertTrue(failure["source_preserved"])
        self.assertTrue(failure["candidate_removed"])
        self.assertEqual(
            "after_candidate_fsync_before_replace", failure["stage"]
        )

        invariants = drill["semantic_invariants"]
        self.assertEqual(14, len(invariants))
        self.assertTrue(all(item["preserved"] for item in invariants))
        self.assertEqual(
            14, len({item["invariant_id"] for item in invariants})
        )
        reviewer = next(
            item
            for item in invariants
            if item["invariant_id"] == "ECO04-INV-REVIEWER-AUTHORITY"
        )
        self.assertEqual(
            reviewer["source_value_sha256"], reviewer["target_value_sha256"]
        )

        compatibility = drill["compatibility"]
        self.assertEqual("explicit_break", compatibility["mode"])
        self.assertTrue(compatibility["source_reader_accepts_source"])
        self.assertFalse(compatibility["source_reader_accepts_target"])
        self.assertFalse(compatibility["target_reader_accepts_source"])
        self.assertTrue(compatibility["target_reader_accepts_target"])
        self.assertTrue(compatibility["break_is_explicit_and_enforced"])

        self.assertEqual("migrated", drill["migration"]["status"])
        self.assertEqual("already_at_target", drill["repeat_run"]["status"])
        self.assertTrue(drill["repeat_run"]["bytes_unchanged"])
        self.assertTrue(drill["repeat_run"]["sha256_unchanged"])
        self.assertTrue(drill["rollback"]["exact_bytes"])
        self.assertTrue(drill["rollback"]["exact_sha256"])
        self.assertTrue(drill["rollback"]["source_reader_accepts"])
        self.assertTrue(drill["determinism"]["pure_transform_equal"])
        self.assertTrue(drill["determinism"]["second_migration_equal"])
        self.assertTrue(drill["exit"]["restored_source_exact"])

        isolation = drill["project_isolation"]
        self.assertTrue(isolation["sandbox_outside_project"])
        self.assertTrue(isolation["all_audited_mutations_under_sandbox"])
        self.assertEqual(0, isolation["real_project_write_count"])
        self.assertTrue(isolation["protected_manifest_unchanged"])
        self.assertTrue(isolation["full_tree_manifest_unchanged"])
        self.assertEqual(
            isolation["full_tree_manifest_before_sha256"],
            isolation["full_tree_manifest_after_sha256"],
        )
        self.assertEqual(
            isolation["protected_manifest_before"],
            isolation["protected_manifest_after"],
        )
        self.assertTrue(isolation["audited_mutations"])
        for event in isolation["audited_mutations"]:
            self.assertFalse(Path(event["path"]).is_absolute())
            self.assertNotIn("..", Path(event["path"]).parts)

    def test_terminology_rename_that_loses_reviewer_authority_is_rejected(
        self,
    ) -> None:
        payload = self.assert_oracle(
            self.run_verifier("semantic_loss"),
            "ECO04-SEMANTIC-INVARIANT",
        )
        observations = payload["drill"]["semantic_invariants"]
        failed = [
            item["invariant_id"]
            for item in observations
            if not item["preserved"]
        ]
        self.assertEqual(["ECO04-INV-REVIEWER-AUTHORITY"], failed)

    def test_migration_without_backup_is_rejected_before_replace(self) -> None:
        payload = self.assert_oracle(
            self.run_verifier("skip_backup"),
            "ECO04-BACKUP-REQUIRED",
        )
        self.assertFalse(payload["drill"]["backup"]["created"])
        self.assertFalse(
            payload["drill"]["failure_injection"]["source_preserved"]
        )

    def test_failure_after_partial_write_is_detected(self) -> None:
        payload = self.assert_oracle(
            self.run_verifier("partial_write_on_failure"),
            "ECO04-FAILURE-ATOMICITY",
        )
        self.assertTrue(payload["drill"]["failure_injection"]["executed"])
        self.assertFalse(
            payload["drill"]["failure_injection"]["source_preserved"]
        )

    def test_semantically_equal_but_byte_different_rollback_is_rejected(
        self,
    ) -> None:
        payload = self.assert_oracle(
            self.run_verifier("rollback_drift"),
            "ECO04-ROLLBACK-BYTES",
        )
        rollback = payload["drill"]["rollback"]
        self.assertEqual("restored", rollback["status"])
        self.assertFalse(rollback["exact_bytes"])
        self.assertFalse(rollback["exact_sha256"])
        self.assertTrue(rollback["source_reader_accepts"])

    def test_source_version_mismatch_aborts_without_migration(self) -> None:
        payload = self.assert_oracle(
            self.run_verifier("source_version_mismatch"),
            "ECO04-SOURCE-VERSION",
        )
        self.assertEqual("not_run", payload["drill"]["migration"]["status"])
        self.assertFalse(payload["drill"]["backup"]["created"])

    def test_non_idempotent_repeated_migration_is_rejected(self) -> None:
        payload = self.assert_oracle(
            self.run_verifier("non_idempotent_repeat"),
            "ECO04-REPEAT-IDEMPOTENCY",
        )
        repeat = payload["drill"]["repeat_run"]
        self.assertEqual("rewritten_target", repeat["status"])
        self.assertFalse(repeat["bytes_unchanged"])
        self.assertFalse(repeat["sha256_unchanged"])

    def test_duplicate_spec_key_is_rejected_as_strict_json(self) -> None:
        raw = self.spec_path.read_text(encoding="utf-8")
        self.spec_path.write_text(
            raw.replace(
                '"schema_version": "migration-drill-spec/v1",',
                '"schema_version": "migration-drill-spec/v1",\n'
                '  "schema_version": "migration-drill-spec/v1",',
                1,
            ),
            encoding="utf-8",
        )
        self.assert_oracle(self.run_verifier(), "ECO04-STRICT-JSON")

    def test_compatibility_claim_mutation_is_rejected_by_frozen_spec(self) -> None:
        spec = json.loads(self.spec_path.read_text(encoding="utf-8"))
        spec["compatibility_contract"]["mode"] = "compatible"
        self.spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.assert_oracle(self.run_verifier(), "ECO04-SPEC-CONTRACT")

    def test_missing_real_project_sentinel_fails_closed_with_machine_json(
        self,
    ) -> None:
        (self.root / "governance" / "WORK_PACKET_POLICY_V1.json").unlink()
        payload = self.assert_oracle(
            self.run_verifier(), "ECO04-PROJECT-SENTINEL"
        )
        self.assertEqual("aborted_fail_closed", payload["drill"]["status"])


if __name__ == "__main__":
    unittest.main()
