from __future__ import annotations

import contextlib
import io
import subprocess
import unittest
from unittest import mock

from scripts import run_assurance_ci


class AssuranceRunnerTests(unittest.TestCase):
    def test_success_emits_started_and_completed_progress(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["fixture-check"],
            returncode=0,
            stdout='{"status":"pass"}\n',
        )
        progress = io.StringIO()
        with (
            mock.patch.object(
                run_assurance_ci.subprocess,
                "run",
                return_value=completed,
            ),
            contextlib.redirect_stderr(progress),
        ):
            receipt = run_assurance_ci.execute_check(
                "CHECK-FIXTURE",
                ["fixture-check"],
                parse_json=True,
                timeout_seconds=7,
            )

        self.assertEqual(receipt["result"], "pass")
        self.assertEqual(receipt["actual_process_exit"], 0)
        self.assertFalse(receipt["timed_out"])
        self.assertEqual(receipt["timeout_seconds"], 7)
        self.assertIn('"phase": "started"', progress.getvalue())
        self.assertIn('"phase": "completed"', progress.getvalue())

    def test_timeout_fails_closed_and_preserves_partial_output(self) -> None:
        progress = io.StringIO()
        timeout = subprocess.TimeoutExpired(
            cmd=["fixture-check"],
            timeout=3,
            output="partial diagnostic",
        )
        with (
            mock.patch.object(
                run_assurance_ci.subprocess,
                "run",
                side_effect=timeout,
            ),
            contextlib.redirect_stderr(progress),
        ):
            receipt = run_assurance_ci.execute_check(
                "CHECK-TIMEOUT",
                ["fixture-check"],
                timeout_seconds=3,
            )

        self.assertEqual(receipt["result"], "fail")
        self.assertEqual(receipt["actual_process_exit"], 124)
        self.assertTrue(receipt["timed_out"])
        self.assertIn("partial diagnostic", receipt["stdout_tail"])
        self.assertIn("timed out after 3 seconds", receipt["stdout_tail"])
        self.assertIn("CHECK-TIMEOUT failure output tail", progress.getvalue())


if __name__ == "__main__":
    unittest.main()
