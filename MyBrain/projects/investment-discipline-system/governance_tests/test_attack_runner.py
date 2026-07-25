from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPLAY_MODULE_PATH = PROJECT_ROOT / "scripts" / "replay_design_freeze_attacks.py"
ATTACK_IDS = [
    "ATTACK-PIT-ORACLE-INVERSION",
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
    "ATTACK-CONDITIONAL-SELF-ATTESTATION",
]


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class AttackRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        source_repository = Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=PROJECT_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            ).stdout.strip()
        )
        cls.project_prefix = (
            PROJECT_ROOT.relative_to(source_repository).as_posix() + "/"
        )
        cls.repository = Path(cls.temp.name) / "repository"
        cls.root = cls.repository / cls.project_prefix
        shutil.copytree(
            PROJECT_ROOT,
            cls.root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                "*.pyc",
                ".ruff_cache",
                "FROZEN_BUNDLE_V1.json",
            ),
        )
        workflow = (
            cls.repository
            / ".github"
            / "workflows"
            / "investment-discipline-assurance.yml"
        )
        workflow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            source_repository
            / ".github"
            / "workflows"
            / "investment-discipline-assurance.yml",
            workflow,
        )
        cls.git("init", "--initial-branch=main")
        cls.git("config", "user.name", "Attack Runner Test")
        cls.git("config", "user.email", "attack-runner@example.invalid")
        cls.git(
            "remote",
            "add",
            "origin",
            "https://github.com/j-a-v-e-n/knowledge-vault.git",
        )
        cls.git("add", ".")
        cls.git("commit", "-m", "exact candidate fixture")
        cls.candidate = cls.git_text("rev-parse", "HEAD")
        cls.tree = cls.git_text("rev-parse", "HEAD^{tree}")
        cls.runner = cls.root / "scripts" / "run_design_freeze_attack.py"

        module_spec = importlib.util.spec_from_file_location(
            "ids_replay_design_freeze_attacks",
            REPLAY_MODULE_PATH,
        )
        if module_spec is None or module_spec.loader is None:
            raise RuntimeError("cannot load replay_design_freeze_attacks.py")
        cls.replay_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(cls.replay_module)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    @classmethod
    def git(cls, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=cls.repository,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"git {' '.join(args)} failed:\n{result.stdout}"
            )
        return result

    @classmethod
    def git_text(cls, *args: str) -> str:
        return cls.git(*args).stdout.strip()

    def run_attack(
        self, attack_id: str
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        completed = subprocess.run(
            [
                sys.executable,
                str(self.runner),
                "--candidate-commit",
                self.candidate,
                "--attack-id",
                attack_id,
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        try:
            receipt = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"runner did not emit one JSON receipt: {exc}\n{completed.stdout}")
        return completed, receipt

    def test_actual_process_baseline_and_target_exits_are_separate(self) -> None:
        completed, receipt = self.run_attack("ATTACK-PIT-ORACLE-INVERSION")
        self.assertEqual(receipt["project_prefix"], self.project_prefix)
        self.assertTrue(receipt["project_prefix"])
        self.assertEqual(receipt["candidate_commit"], self.candidate)
        self.assertEqual(receipt["candidate_tree"], self.tree)
        self.assertEqual(receipt["baseline"]["exit_code"], 0)
        self.assertIn(
            "governance verification: PASS (candidate)",
            receipt["baseline"]["stdout"],
        )
        self.assertNotEqual(receipt["target"]["exit_code"], 0)
        self.assertIn(
            receipt["expected_rejection_substring"],
            receipt["target"]["stdout"],
        )
        self.assertEqual(receipt["result"], "rejected")
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(receipt["runner_exit_code"], completed.returncode)
        self.assertNotIn("command", receipt)
        self.assertEqual(
            receipt["baseline"]["argv"],
            ["PYTHON", "scripts/verify_governance.py", "--allow-candidate"],
        )

    def test_replay_rejects_forged_declared_or_target_exit(self) -> None:
        completed, receipt = self.run_attack("ATTACK-PIT-ORACLE-INVERSION")
        self.assertEqual(completed.returncode, 0, completed.stdout)
        validate = self.replay_module.valid_receipt

        forged_wrapper = copy.deepcopy(receipt)
        forged_wrapper["runner_exit_code"] = 73
        self.assertFalse(
            validate(
                forged_wrapper,
                attack_id="ATTACK-PIT-ORACLE-INVERSION",
                candidate_commit=self.candidate,
                candidate_tree=self.tree,
                actual_process_exit=completed.returncode,
            )
        )

        forged_target = copy.deepcopy(receipt)
        forged_target["target"]["exit_code"] = 0
        forged_target["execution_fingerprint"] = hashlib.sha256(
            self.replay_module.canonical_json(
                self.replay_module.fingerprint_payload(forged_target)
            )
        ).hexdigest()
        self.assertFalse(
            validate(
                forged_target,
                attack_id="ATTACK-PIT-ORACLE-INVERSION",
                candidate_commit=self.candidate,
                candidate_tree=self.tree,
                actual_process_exit=completed.returncode,
            )
        )

    def test_post_candidate_restricted_novelty_spec_is_executed(self) -> None:
        spec_path = self.root / "review-probe.json"
        spec = {
            "schema_version": 1,
            "probe_id": "PROBE-POST-CANDIDATE-PIT-TEST",
            "target_path": "governance/ACCEPTANCE_CASES_V1.json",
            "json_pointer": (
                "/cases/@id=CASE-PIT-LATE-RETRIEVAL/expected/accepted"
            ),
            "operation": "replace",
            "expected_before_sha256": canonical_hash(False),
            "replacement": True,
            "expected_rejection_substring": (
                "CASE-PIT-LATE-RETRIEVAL freeze-critical semantics differ"
            ),
            "rationale": "exercise the post-candidate restricted mutation path",
        }
        spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        self.assertNotEqual(
            subprocess.run(
                [
                    "git",
                    "cat-file",
                    "-e",
                    (
                        f"{self.candidate}:{self.project_prefix}"
                        "review-probe.json"
                    ),
                ],
                cwd=self.root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            ).returncode,
            0,
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(self.runner),
                "--candidate-commit",
                self.candidate,
                "--novelty-spec",
                str(spec_path),
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        receipt = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(receipt["mode"], "novelty")
        self.assertEqual(receipt["probe_id"], spec["probe_id"])
        self.assertEqual(receipt["baseline"]["exit_code"], 0)
        self.assertNotEqual(receipt["target"]["exit_code"], 0)
        self.assertEqual(receipt["result"], "rejected")

    def test_full_canonical_replay_exposes_all_actual_target_exits(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(self.root / "scripts" / "replay_design_freeze_attacks.py"),
                "--candidate-commit",
                self.candidate,
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["required_attack_ids"], ATTACK_IDS)
        for result in payload["results"]:
            self.assertEqual(result["actual_runner_process_exit"], 0)
            self.assertEqual(result["declared_runner_exit_code"], 0)
            self.assertEqual(result["baseline_verifier_exit"], 0)
            self.assertNotEqual(result["target_verifier_exit"], 0)
            self.assertEqual(result["result"], "rejected")

    def test_full_replay_fails_closed_on_null_runner_sections(self) -> None:
        original_runner = self.runner.read_bytes()
        malformed_runner = """#!/usr/bin/env python3
import json
import sys

print(json.dumps({"baseline": None, "target": None}))
sys.exit(1)
"""
        try:
            self.runner.write_text(malformed_runner, encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(
                        self.root
                        / "scripts"
                        / "replay_design_freeze_attacks.py"
                    ),
                    "--candidate-commit",
                    self.candidate,
                ],
                cwd=self.root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
        finally:
            self.runner.write_bytes(original_runner)
        self.assertEqual(completed.returncode, 1, completed.stdout)
        self.assertNotIn("Traceback", completed.stdout)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(len(payload["results"]), len(ATTACK_IDS))
        for result in payload["results"]:
            self.assertIsNone(result["baseline_verifier_exit"])
            self.assertIsNone(result["target_verifier_exit"])
            self.assertEqual(result["result"], "escaped_or_runner_error")


if __name__ == "__main__":
    unittest.main()
