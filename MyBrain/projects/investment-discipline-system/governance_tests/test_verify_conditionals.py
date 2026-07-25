from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = PROJECT_ROOT / "scripts" / "verify_conditionals.py"


class ConditionalGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "governance").mkdir()
        shutil.copy2(
            PROJECT_ROOT / "governance" / "ACCEPTANCE_CONTRACT_V1.json",
            self.root / "governance" / "ACCEPTANCE_CONTRACT_V1.json",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_gate(
        self, gate_id: str, *, token: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        if token is None:
            env.pop("TIINGO_API_TOKEN", None)
        else:
            env["TIINGO_API_TOKEN"] = token
        return subprocess.run(
            ["python3", str(VERIFIER), "--gate", gate_id, "--json"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_missing_tiingo_token_is_unproved_not_failed(self) -> None:
        result = self.run_gate("COND-TIINGO-LIVE-PROBE")
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(
            payload["aggregate_verdict"], "core_pass_with_unproven_conditions"
        )
        self.assertEqual(
            payload["results"][0]["effective_state"],
            "not_run_missing_user_credential",
        )

    def test_present_token_without_evidence_is_blocked_and_not_leaked(self) -> None:
        secret = "test-token-must-not-appear"
        result = self.run_gate("COND-TIINGO-LIVE-PROBE", token=secret)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertNotIn(secret, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["aggregate_verdict"], "blocked")
        self.assertEqual(payload["results"][0]["effective_state"], "mandatory_pending")
        self.assertIn(
            "prerequisite_ready_but_evidence_missing",
            payload["results"][0]["errors"],
        )

    def test_unknown_gate_is_usage_error(self) -> None:
        result = self.run_gate("COND-NOT-REAL")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("unknown conditional gate", result.stdout)


if __name__ == "__main__":
    unittest.main()
