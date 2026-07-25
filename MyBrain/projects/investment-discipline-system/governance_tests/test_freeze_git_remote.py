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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREEZER = PROJECT_ROOT / "scripts" / "freeze_governance.py"
GIT_VERIFIER = PROJECT_ROOT / "scripts" / "verify_git_state.py"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
ASSURANCE_RELATIVE = "governance/ASSURANCE_SUBJECTS_V1.json"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FINAL_EVIDENCE_RELATIVE = "audits/FINAL_REVIEW_EVIDENCE_R3.json"
FINAL_REVIEW_SUBJECT = "SUBJECT-DESIGN-REVIEW-FINAL-R3"


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
        self.initial_candidate = self.git_text(self.root, "rev-parse", "HEAD")

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
    ) -> str:
        reviewed_commit = self.git_text(self.root, "rev-parse", "HEAD")
        reviewed_tree = self.git_text(
            self.root, "rev-parse", f"{reviewed_commit}^{{tree}}"
        )
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        frozen_files = contract["change_control"]["frozen_files"]
        review_input = (
            "Independently review the exact candidate commit and tree against every "
            "contract frozen file. Pass only with no open critical or major finding "
            "and no new architecture-changing class."
        )
        evidence = {
            "schema_version": 1,
            "subject_id": FINAL_REVIEW_SUBJECT,
            "review_locator": "test-fixture:independent-final-review-r3",
            "review_input": review_input,
            "review_input_sha256": hashlib.sha256(
                review_input.encode("utf-8")
            ).hexdigest(),
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "verdict": "passed_freeze",
            "open_critical_count": 0,
            "open_major_count": 0,
            "new_architecture_changing_classes": [],
            "participated_in_candidate_construction": False,
            "write_access_used": False,
            "reviewed_files": list(frozen_files),
            "finding_ids": [],
        }
        self.write_json(FINAL_EVIDENCE_RELATIVE, evidence)
        evidence_hash = hashlib.sha256(
            (self.root / FINAL_EVIDENCE_RELATIVE).read_bytes()
        ).hexdigest()

        assurance = self.read_json(ASSURANCE_RELATIVE)
        assurance["subjects"].append(
            {
                "id": FINAL_REVIEW_SUBJECT,
                "role": "design_reviewer",
                "locator": evidence["review_locator"],
                "candidate_commit": reviewed_commit,
                "candidate_tree": reviewed_tree,
                "write_access_used": False,
                "participated_in_candidate_construction": False,
                "verdict": "passed_freeze",
                "evidence_path": FINAL_EVIDENCE_RELATIVE,
                "evidence_sha256": evidence_hash,
            }
        )
        self.write_json(ASSURANCE_RELATIVE, assurance)

        for relative in frozen_files:
            if Path(relative).suffix.lower() != ".json":
                continue
            document = self.read_json(relative)
            if relative == RESEARCH_RELATIVE:
                document["status"] = "adopted_with_explicit_limits"
                challenge = document["challenge"]
                challenge["status"] = "completed"
                challenge["rounds"].append(
                    {
                        "id": "CHALLENGE-FINAL-R3",
                        "candidate_commit": reviewed_commit,
                        "candidate_tree": reviewed_tree,
                        "reviewer_subjects": [FINAL_REVIEW_SUBJECT],
                        "result": "passed_freeze",
                        "evidence_path": FINAL_EVIDENCE_RELATIVE,
                        "evidence_sha256": evidence_hash,
                        "new_architecture_changing_classes": [],
                        "critical_findings": [],
                        "major_findings": [],
                        "open_critical_count": 0,
                        "open_major_count": 0,
                        "disposition": "machine-readable final review closed the candidate",
                    }
                )
                document["stop_rule"]["met"] = True
                document["primary_artifacts"].append(
                    {
                        "id": "ARTIFACT-CHALLENGE-FINAL-R3",
                        "path": FINAL_EVIDENCE_RELATIVE,
                        "sha256": evidence_hash,
                        "role": "independent_final_challenge",
                    }
                )
            elif relative == incomplete_relative:
                document["status"] = "candidate_for_freeze"
            else:
                document["status"] = "frozen"
            self.write_json(relative, document)
        return reviewed_commit

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
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            self.initial_candidate,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("candidate governance verification failed", result.stdout)
        self.assertIn(f"missing JSON: {missing}", result.stdout)
        self.assert_bundle_absent()

    def test_freeze_rejects_incomplete_dynamic_json_status(self) -> None:
        incomplete = "governance/ACCEPTANCE_CASES_V1.json"
        reviewed = self.prepare_completed_freeze(incomplete_relative=incomplete)
        baseline = self.commit_and_push("leave one normative JSON incomplete")

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"{incomplete} status must be frozen", result.stdout)
        self.assert_bundle_absent()

    def test_freeze_rejects_dirty_exact_baseline(self) -> None:
        reviewed = self.prepare_completed_freeze()
        baseline = self.commit_and_push("complete freeze prerequisites")
        with (self.root / "README.md").open("a", encoding="utf-8") as handle:
            handle.write("\ndirty counterexample\n")

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("project worktree is not clean", result.stdout)
        self.assertIn("README.md", result.stdout)
        self.assert_bundle_absent()

    def test_closure_rejects_smuggled_money_semantics_change(self) -> None:
        reviewed = self.prepare_completed_freeze()
        relative = "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
        money = self.read_json(relative)
        money["scope"] += " Closure may also silently reinterpret booked cash."
        self.write_json(relative, money)
        baseline = self.commit_and_push("smuggle money semantics into closure")

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(f"closure changed non-status content: {relative}", result.stdout)
        self.assert_bundle_absent()

    def test_valid_non_circular_closure_creates_bound_bundle(self) -> None:
        reviewed = self.prepare_completed_freeze()
        baseline = self.commit_and_push("valid review closure")

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        bundle = self.read_json(BUNDLE_RELATIVE)
        self.assertEqual(bundle["reviewed_candidate_commit"], reviewed)
        self.assertEqual(
            bundle["reviewed_candidate_tree"],
            self.git_text(self.root, "rev-parse", f"{reviewed}^{{tree}}"),
        )
        self.assertEqual(bundle["baseline_commit"], baseline)
        self.assertEqual(
            bundle["baseline_tree"],
            self.git_text(self.root, "rev-parse", f"{baseline}^{{tree}}"),
        )
        self.assertEqual(bundle["final_review_subject_id"], FINAL_REVIEW_SUBJECT)
        self.assertEqual(
            bundle["final_review_evidence_path"], FINAL_EVIDENCE_RELATIVE
        )
        self.assertEqual(
            bundle["final_review_evidence_sha256"],
            hashlib.sha256(
                (self.root / FINAL_EVIDENCE_RELATIVE).read_bytes()
            ).hexdigest(),
        )

    def test_direct_remote_mismatch_defeats_stale_local_upstream(self) -> None:
        reviewed = self.prepare_completed_freeze()
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
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("direct remote commit verification failed", result.stdout)
        self.assertIn("remote_commit_mismatch", result.stdout)
        self.assert_bundle_absent()


if __name__ == "__main__":
    unittest.main()
