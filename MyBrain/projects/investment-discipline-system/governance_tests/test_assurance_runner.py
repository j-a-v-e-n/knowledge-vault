from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

from scripts import run_assurance_ci


class AssuranceRunnerTests(unittest.TestCase):
    def test_success_emits_started_and_completed_progress(self) -> None:
        progress = io.StringIO()
        with contextlib.redirect_stderr(progress):
            receipt = run_assurance_ci.execute_check(
                "CHECK-FIXTURE",
                [
                    sys.executable,
                    "-c",
                    "import json; print(json.dumps({'status': 'pass'}))",
                ],
                parse_json=True,
                timeout_seconds=7,
            )

        self.assertEqual(receipt["result"], "pass")
        self.assertEqual(receipt["actual_process_exit"], 0)
        self.assertFalse(receipt["timed_out"])
        self.assertEqual(receipt["timeout_seconds"], 7)
        self.assertIn('"phase": "started"', progress.getvalue())
        self.assertIn('"phase": "completed"', progress.getvalue())

    def test_malformed_structured_output_fails_closed(self) -> None:
        progress = io.StringIO()
        with contextlib.redirect_stderr(progress):
            receipt = run_assurance_ci.execute_check(
                "CHECK-MALFORMED",
                [sys.executable, "-c", "print('not json')"],
                parse_json=True,
                timeout_seconds=7,
            )
        self.assertEqual(receipt["actual_process_exit"], 0)
        self.assertEqual(receipt["result"], "fail")
        self.assertIsNone(receipt["structured_result"])

    def test_timeout_fails_closed_and_preserves_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "grandchild-survived.txt"
            child = (
                "import time\n"
                "from pathlib import Path\n"
                "time.sleep(0.7)\n"
                f"Path({str(marker)!r}).write_text('survived')\n"
            )
            parent = (
                "import subprocess\n"
                "import sys\n"
                "import time\n"
                f"subprocess.Popen([sys.executable, '-c', {child!r}])\n"
                "print('partial diagnostic', flush=True)\n"
                "time.sleep(5)\n"
            )
            progress = io.StringIO()
            with contextlib.redirect_stderr(progress):
                receipt = run_assurance_ci.execute_check(
                    "CHECK-TIMEOUT",
                    [sys.executable, "-c", parent],
                    timeout_seconds=0.1,
                )

            self.assertEqual(receipt["result"], "fail")
            self.assertEqual(receipt["actual_process_exit"], 124)
            self.assertTrue(receipt["timed_out"])
            self.assertIn("partial diagnostic", receipt["stdout_tail"])
            self.assertIn(
                "timed out after 0.1 seconds",
                receipt["stdout_tail"],
            )
            self.assertIn(
                "CHECK-TIMEOUT failure output tail",
                progress.getvalue(),
            )
            time.sleep(1)
            self.assertFalse(marker.exists())

    def test_spawn_error_fails_closed(self) -> None:
        receipt = run_assurance_ci.execute_check(
            "CHECK-NOT-FOUND",
            ["/definitely/not/a/real/executable"],
            timeout_seconds=1,
        )
        self.assertEqual(receipt["result"], "fail")
        self.assertEqual(receipt["actual_process_exit"], 125)
        self.assertFalse(receipt["timed_out"])
        self.assertIn("FileNotFoundError", receipt["stdout_tail"])

    def test_normalized_python_argv_is_stable(self) -> None:
        receipt = run_assurance_ci.execute_check(
            "CHECK-ARGV",
            [
                sys.executable,
                "-c",
                f"print({json.dumps('ok')})",
            ],
            timeout_seconds=7,
        )
        self.assertEqual(receipt["argv"][0], "PYTHON")


if __name__ == "__main__":
    unittest.main()
