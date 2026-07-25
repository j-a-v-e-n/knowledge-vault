from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import run_project_method_acceptance
from scripts.freeze_governance import MACHINE_CHECK_SPECS


class ProjectMethodAcceptanceRunnerTests(unittest.TestCase):
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
