from __future__ import annotations

import json
import inspect
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_project_method_acceptance, verify_governance
from scripts.freeze_governance import MACHINE_CHECK_SPECS


class ProjectMethodAcceptanceRunnerTests(unittest.TestCase):
    def test_governance_aggregator_uses_only_v2_current_runtime_authorities(
        self,
    ) -> None:
        self.assertEqual(
            "WORK_PACKET_POLICY_V2.json",
            verify_governance.WORK_PACKET_POLICY.name,
        )
        self.assertEqual(
            "EXECUTION_LOOP_POLICY_V2.json",
            verify_governance.EXECUTION_LOOP_POLICY.name,
        )
        source = inspect.getsource(verify_governance.verify)
        self.assertIn("verify_execution_loop_v2.py", source)
        self.assertNotIn('"verify_execution_loop.py"', source)

    def test_current_method_cases_do_not_invoke_v1_runtime_authorities(
        self,
    ) -> None:
        commands = [
            command
            for case in run_project_method_acceptance.FAILURE_CASES
            for command in case["commands"]
        ]
        self.assertNotIn(
            ["PYTHON", "scripts/verify_execution_loop.py", "--json"],
            commands,
        )
        current_work_commands = [
            command
            for command in commands
            if "scripts/verify_work_packets.py" in command
        ]
        self.assertTrue(current_work_commands)
        for command in current_work_commands:
            self.assertIn("--policy", command)
            self.assertIn("governance/WORK_PACKET_POLICY_V2.json", command)
        self.assertIn(
            ["PYTHON", "scripts/verify_execution_loop_v2.py", "--json"],
            commands,
        )

    def test_machine_outcome_ignores_registry_metadata(self) -> None:
        self.assertEqual(
            ("checks_passed", None),
            run_project_method_acceptance.derive_outcome(True, None),
        )

    def test_failed_command_blocks_machine_outcome(self) -> None:
        self.assertEqual(
            ("blocked", None),
            run_project_method_acceptance.derive_outcome(False, None),
        )

    def test_authorized_external_conditional_remains_explicit(self) -> None:
        self.assertEqual(
            ("conditionally_deferred", "COND-FIXTURE"),
            run_project_method_acceptance.derive_outcome(
                True,
                "COND-FIXTURE",
            ),
        )

    def test_machine_check_requires_ephemeral_receipt(self) -> None:
        self.assertEqual(
            MACHINE_CHECK_SPECS["CHECK-PROJECT-METHOD"]["argv"],
            [
                "PYTHON",
                "scripts/run_project_method_acceptance.py",
                "--json",
                "--verify",
                "--ephemeral",
            ],
        )

    def test_external_receipt_does_not_dirty_candidate(self) -> None:
        with (
            tempfile.TemporaryDirectory() as repository_directory,
            tempfile.TemporaryDirectory() as evidence_directory,
        ):
            repository = Path(repository_directory)
            evidence = Path(evidence_directory) / "V-PROJECT-METHOD.json"
            (repository / "tracked.txt").write_text(
                "candidate\n",
                encoding="utf-8",
            )
            for command in (
                ["git", "init"],
                ["git", "config", "user.name", "Acceptance Fixture"],
                ["git", "config", "user.email", "fixture@example.invalid"],
                ["git", "add", "."],
                ["git", "commit", "-m", "candidate"],
            ):
                completed = subprocess.run(
                    command,
                    cwd=repository,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    0,
                    completed.returncode,
                    completed.stdout + completed.stderr,
                )

            with mock.patch.object(
                run_project_method_acceptance,
                "PROJECT_ROOT",
                repository,
            ):
                run_project_method_acceptance.write_atomic(
                    evidence,
                    {"status": "fixture"},
                )
                clean, dirty = (
                    run_project_method_acceptance.project_is_clean_before_evidence(
                        evidence
                    )
                )

            self.assertTrue(clean, dirty)
            self.assertEqual([], dirty)
            self.assertEqual(
                {"status": "fixture"},
                json.loads(evidence.read_text(encoding="utf-8")),
            )
            status = subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                cwd=repository,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, status.returncode, status.stderr)
            self.assertEqual("", status.stdout)


if __name__ == "__main__":
    unittest.main()
