from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREEZER = PROJECT_ROOT / "scripts" / "freeze_governance.py"
GIT_VERIFIER = PROJECT_ROOT / "scripts" / "verify_git_state.py"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"


class FreezeGitRemoteCounterexampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp.name)
        self.root = self.temp_root / "project"
        self.remote = self.temp_root / "remote.git"
        shutil.copytree(
            PROJECT_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        self.run_git(
            self.temp_root,
            "init",
            "--bare",
            "--initial-branch=main",
            str(self.remote),
        )
        self.run_git(self.root, "init", "--initial-branch=main")
        self.run_git(self.root, "config", "user.name", "Governance Test")
        self.run_git(self.root, "config", "user.email", "governance@example.invalid")
        self.run_git(self.root, "add", ".")
        self.run_git(self.root, "commit", "-m", "candidate fixture")
        self.run_git(self.root, "remote", "add", "origin", str(self.remote))
        self.run_git(self.root, "push", "--set-upstream", "origin", "main")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_command(
        self,
        cwd: Path,
        *command: str,
        env: dict[str, str] | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        if check and result.returncode != 0:
            self.fail(
                f"command failed ({result.returncode}): {' '.join(command)}\n"
                f"{result.stdout}"
            )
        return result

    def run_git(
        self, cwd: Path, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return self.run_command(cwd, "git", *args, check=check)

    def git_text(self, cwd: Path, *args: str) -> str:
        return self.run_git(cwd, *args).stdout.strip()

    def run_project_script(
        self, script: Path, *args: str
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        return self.run_command(
            self.root,
            sys.executable,
            str(script),
            *args,
            env=env,
            check=False,
        )

    def read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict) -> None:
        (self.root / relative).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def commit_and_push(self, message: str) -> str:
        self.run_git(self.root, "add", "-A")
        self.run_git(self.root, "commit", "-m", message)
        self.run_git(self.root, "push", "origin", "main")
        return self.git_text(self.root, "rev-parse", "HEAD")

    def prepare_completed_freeze(
        self, *, incomplete_relative: str | None = None
    ) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        frozen_files = contract["change_control"]["frozen_files"]
        for relative in frozen_files:
            if Path(relative).suffix.lower() != ".json":
                continue
            document = self.read_json(relative)
            if relative == RESEARCH_RELATIVE:
                document["status"] = "adopted_with_explicit_limits"
                challenge = document["challenge"]
                challenge["status"] = "completed"
                final_round = challenge["rounds"][-1]
                final_round["result"] = "passed_freeze"
                final_round["new_architecture_changing_classes"] = []
                final_round["critical_findings"] = []
                final_round["major_findings"] = []
                final_round["open_critical_count"] = 0
                final_round["open_major_count"] = 0
                document["stop_rule"]["met"] = True
            elif relative == incomplete_relative:
                document["status"] = "candidate_for_freeze"
            else:
                document["status"] = "frozen"
            self.write_json(relative, document)

    def assert_bundle_absent(self) -> None:
        self.assertFalse((self.root / BUNDLE_RELATIVE).exists())

    def test_git_verifier_reads_missing_normative_from_contract_boundary(self) -> None:
        relative = "governance/ACCEPTANCE_CASES_V1.json"
        (self.root / relative).unlink()
        baseline = self.commit_and_push("remove contract-listed normative file")

        result = self.run_project_script(
            GIT_VERIFIER, "--expected-commit", baseline
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"normative file is not tracked: {relative}", result.stdout)
        self.assertIn(f"normative file is absent from HEAD: {relative}", result.stdout)

    def test_git_verifier_requires_existing_bundle_in_head(self) -> None:
        bundle = self.root / BUNDLE_RELATIVE
        bundle.write_text("{}\n", encoding="utf-8")
        self.run_git(self.root, "add", BUNDLE_RELATIVE)

        result = self.run_project_script(GIT_VERIFIER)

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            f"frozen bundle is absent from HEAD: {BUNDLE_RELATIVE}", result.stdout
        )

    def test_freeze_runs_candidate_governance_verifier_first(self) -> None:
        missing = "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
        (self.root / missing).unlink()
        baseline = self.commit_and_push("remove candidate governance input")

        result = self.run_project_script(
            FREEZER, "--baseline-commit", baseline
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("candidate governance verification failed", result.stdout)
        self.assertIn(f"missing JSON: {missing}", result.stdout)
        self.assert_bundle_absent()

    def test_freeze_rejects_incomplete_dynamic_json_status(self) -> None:
        incomplete = "governance/ACCEPTANCE_CASES_V1.json"
        self.prepare_completed_freeze(incomplete_relative=incomplete)
        baseline = self.commit_and_push("leave one normative JSON incomplete")

        result = self.run_project_script(
            FREEZER, "--baseline-commit", baseline
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"{incomplete} status must be frozen", result.stdout)
        self.assert_bundle_absent()

    def test_freeze_rejects_dirty_exact_baseline(self) -> None:
        self.prepare_completed_freeze()
        baseline = self.commit_and_push("complete freeze prerequisites")
        with (self.root / "README.md").open("a", encoding="utf-8") as handle:
            handle.write("\ndirty counterexample\n")

        result = self.run_project_script(
            FREEZER, "--baseline-commit", baseline
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("project worktree is not clean", result.stdout)
        self.assertIn("README.md", result.stdout)
        self.assert_bundle_absent()

    def test_direct_remote_mismatch_defeats_stale_local_upstream(self) -> None:
        self.prepare_completed_freeze()
        baseline = self.commit_and_push("complete freeze prerequisites")
        attacker = self.temp_root / "remote-writer"
        self.run_git(self.temp_root, "clone", str(self.remote), str(attacker))
        self.run_git(attacker, "config", "user.name", "Remote Writer")
        self.run_git(attacker, "config", "user.email", "remote@example.invalid")
        (attacker / "remote-only.txt").write_text(
            "advance the actual remote without fetching locally\n",
            encoding="utf-8",
        )
        self.run_git(attacker, "add", "remote-only.txt")
        self.run_git(attacker, "commit", "-m", "advance actual remote")
        self.run_git(attacker, "push", "origin", "main")

        local_upstream = self.git_text(self.root, "rev-parse", "@{upstream}")
        actual_remote = self.git_text(
            self.root, "ls-remote", "--heads", "origin", "refs/heads/main"
        ).split()[0]
        self.assertEqual(local_upstream, baseline)
        self.assertNotEqual(actual_remote, baseline)

        local_only = self.run_project_script(
            GIT_VERIFIER,
            "--require-origin",
            "--expected-commit",
            baseline,
        )
        self.assertEqual(local_only.returncode, 0, local_only.stdout)

        result = self.run_project_script(
            FREEZER, "--baseline-commit", baseline
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("direct remote commit verification failed", result.stdout)
        self.assertIn("remote_commit_mismatch", result.stdout)
        self.assert_bundle_absent()


if __name__ == "__main__":
    unittest.main()
