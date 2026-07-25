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
REMOTE_VERIFIER = PROJECT_ROOT / "scripts" / "verify_remote_commit.py"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
ASSURANCE_RELATIVE = "governance/ASSURANCE_SUBJECTS_V1.json"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FINAL_EVIDENCE_RELATIVE = "audits/FINAL_REVIEW_EVIDENCE_R3.json"
FINAL_REVIEW_SUBJECT = "SUBJECT-DESIGN-REVIEW-FINAL-R3"
CANONICAL_ATTACK_SELECTORS = {
    "ATTACK-PIT-ORACLE-INVERSION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_pit_oracle_inversion_is_rejected"
    ),
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_same_bar_causality_smuggle_is_rejected"
    ),
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_split_accounting_smuggle_is_rejected"
    ),
    "ATTACK-CONDITIONAL-SELF-ATTESTATION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_conditional_self_attestation_is_rejected"
    ),
}


class FreezeGitRemoteCounterexampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp.name)
        self.repo_root = self.temp_root / "project"
        self.root = self.repo_root
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
        self.run_git(self.repo_root, "init", "--initial-branch=main")
        self.run_git(self.repo_root, "config", "user.name", "Governance Test")
        self.run_git(
            self.repo_root,
            "config",
            "user.email",
            "governance@example.invalid",
        )
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
        attack_specs = [
            {
                "attack_id": "ATTACK-PIT-ORACLE-INVERSION",
                "mutation": (
                    "Invert the point-in-time late-retrieval oracle to accept "
                    "future information."
                ),
                "expected": "The freeze-critical PIT oracle mutation is rejected.",
                "observed": (
                    "The verifier rejected CASE-PIT-LATE-RETRIEVAL semantic drift."
                ),
                "replay_selector": CANONICAL_ATTACK_SELECTORS[
                    "ATTACK-PIT-ORACLE-INVERSION"
                ],
            },
            {
                "attack_id": "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
                "mutation": (
                    "Allow same-bar fills by default and thereby smuggle future "
                    "bar information into execution."
                ),
                "expected": "The same-bar causality mutation is rejected.",
                "observed": (
                    "The verifier rejected market calendar and causality drift."
                ),
                "replay_selector": CANONICAL_ATTACK_SELECTORS[
                    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE"
                ],
            },
            {
                "attack_id": "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
                "mutation": (
                    "Leave position quantity unchanged when applying a stock split."
                ),
                "expected": "The split-accounting mutation is rejected.",
                "observed": (
                    "The verifier rejected ACTION-SPLIT accounting drift."
                ),
                "replay_selector": CANONICAL_ATTACK_SELECTORS[
                    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE"
                ],
            },
            {
                "attack_id": "ATTACK-CONDITIONAL-SELF-ATTESTATION",
                "mutation": (
                    "Let the candidate self-attest a conditional gate without "
                    "independent release evidence."
                ),
                "expected": "The conditional self-attestation is rejected.",
                "observed": (
                    "The verifier rejected candidate-authored conditional evidence."
                ),
                "replay_selector": CANONICAL_ATTACK_SELECTORS[
                    "ATTACK-CONDITIONAL-SELF-ATTESTATION"
                ],
            },
        ]
        independent_attacks = []
        commands_run = []
        for index, attack in enumerate(attack_specs, start=1):
            mutation_hash = hashlib.sha256(
                attack["mutation"].encode("utf-8")
            ).hexdigest()
            raw_relative = f"audits/FINAL_REVIEW_ATTACK_R3_{index}.json"
            replay_command = (
                f"python3 -m unittest {attack['replay_selector']}"
            )
            raw_command = (
                f"IDS_ATTACK_FIXTURE={attack['attack_id']} "
                "python3 scripts/verify_governance.py --allow-candidate"
            )
            stdout = attack["observed"]
            raw_result = {
                "schema_version": 1,
                "attack_id": attack["attack_id"],
                "candidate_commit": reviewed_commit,
                "candidate_tree": reviewed_tree,
                "result": "rejected",
                "exit_code": 1,
                "mutation_sha256": mutation_hash,
                "replay_selector": attack["replay_selector"],
                "expected": attack["expected"],
                "observed": attack["observed"],
                "command": raw_command,
                "stdout": stdout,
                "stdout_sha256": hashlib.sha256(
                    stdout.encode("utf-8")
                ).hexdigest(),
            }
            self.write_json(raw_relative, raw_result)
            raw_hash = hashlib.sha256(
                (self.root / raw_relative).read_bytes()
            ).hexdigest()
            independent_attacks.append(
                {
                    **attack,
                    "result": "rejected",
                    "mutation_sha256": mutation_hash,
                    "raw_result_path": raw_relative,
                    "raw_result_sha256": raw_hash,
                }
            )
            commands_run.extend([replay_command, raw_command])

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
            "open_minor_count": 0,
            "new_architecture_changing_classes": [],
            "participated_in_candidate_construction": False,
            "write_access_used": False,
            "reviewed_files": list(
                dict.fromkeys(
                    [
                        *frozen_files,
                        "scripts/verify_governance.py",
                        "scripts/verify_conditionals.py",
                        "scripts/replay_design_freeze_attacks.py",
                        "scripts/freeze_governance.py",
                        "scripts/verify_git_state.py",
                        "scripts/verify_remote_commit.py",
                        "governance_tests/test_final_review_attacks.py",
                        "governance_tests/test_verify_conditionals.py",
                        "governance_tests/test_freeze_git_remote.py",
                    ]
                )
            ),
            "finding_ids": [],
            "findings": [],
            "commands_run": commands_run,
            "independent_attacks": independent_attacks,
            "what_would_falsify_pass": [
                "Any replay selector accepts its corresponding mutation.",
                "Any reviewed frozen file differs semantically from the candidate.",
            ],
            "limitations": [
                "The fixture proves governance rejection behavior, not production "
                "investment correctness."
            ],
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
                        "open_minor_count": 0,
                        "finding_ids": [],
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

    def test_closure_rejects_chmod_smuggle(self) -> None:
        reviewed = self.prepare_completed_freeze()
        relative = "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
        os.chmod(self.root / relative, 0o755)
        baseline = self.commit_and_push("smuggle executable mode into closure")
        tree_entry = self.git_text(
            self.root,
            "ls-tree",
            "--full-name",
            baseline,
            "--",
            f":(top,literal){relative}",
        )
        self.assertTrue(tree_entry.startswith("100755 "), tree_entry)

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
            "--branch",
            "main",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            f"closure changed Git mode/type for frozen file: {relative}",
            result.stdout,
        )
        self.assert_bundle_absent()

    def test_closure_rejects_rename_smuggle(self) -> None:
        reviewed = self.prepare_completed_freeze()
        original = "governance_tests/test_research_evidence_governance.py"
        renamed = "audits/TEST_PACKAGE_RENAMED_DURING_CLOSURE.py"
        self.run_git(self.root, "mv", original, renamed)
        baseline = self.commit_and_push("smuggle rename into closure")

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
            "--branch",
            "main",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "closure changed paths outside the allowed metadata set",
            result.stdout,
        )
        self.assertIn(original, result.stdout)
        self.assertIn(renamed, result.stdout)
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
        replay = bundle["design_freeze_attack_replay"]
        self.assertEqual(replay["schema_version"], 1)
        self.assertEqual(replay["status"], "pass")
        self.assertEqual(replay["candidate_commit"], baseline)
        self.assertEqual(
            replay["candidate_tree"],
            self.git_text(self.root, "rev-parse", f"{baseline}^{{tree}}"),
        )
        self.assertEqual(
            set(replay["required_attack_ids"]),
            set(CANONICAL_ATTACK_SELECTORS),
        )
        self.assertEqual(len(replay["required_attack_ids"]), 4)
        replay_results = {
            item["attack_id"]: item for item in replay["results"]
        }
        self.assertEqual(set(replay_results), set(CANONICAL_ATTACK_SELECTORS))
        self.assertEqual(len(replay["results"]), 4)
        for attack_id, selector in CANONICAL_ATTACK_SELECTORS.items():
            attack_result = replay_results[attack_id]
            self.assertEqual(attack_result["selector"], selector)
            self.assertEqual(attack_result["result"], "rejected")
            self.assertEqual(attack_result["exit_code"], 0)
            self.assertEqual(len(attack_result["output_sha256"]), 64)
        self.assertEqual(len(replay["stdout_sha256"]), 64)
        observations = bundle["baseline_remote_observations"]
        self.assertEqual(
            [item["phase"] for item in observations],
            [
                "before_baseline_verification",
                "after_baseline_verification",
            ],
        )
        for observation in observations:
            self.assertEqual(observation["remote"], "origin")
            self.assertEqual(observation["ref"], "refs/heads/main")
            self.assertEqual(observation["commit"], baseline)
            self.assertTrue(observation["observed_at"])
        self.assertNotIn("remote_at_creation", bundle)
        self.assertNotIn("upstream_ref_at_creation", bundle)

        frozen_commit = self.commit_and_push("commit frozen bundle")
        post_verification = self.run_project_script(
            REMOTE_VERIFIER,
            "--verify-frozen-bundle",
            "--remote",
            "origin",
            "--branch",
            "main",
            "--json",
        )
        self.assertEqual(
            post_verification.returncode,
            0,
            post_verification.stdout,
        )
        post_payload = json.loads(post_verification.stdout)
        self.assertEqual(post_payload["status"], "pass")
        post_facts = post_payload["facts"]
        self.assertEqual(post_facts["head"], frozen_commit)
        self.assertEqual(
            post_facts["project_prefix"],
            "",
        )
        self.assertEqual(post_facts["bundle_path"], BUNDLE_RELATIVE)
        self.assertEqual(
            post_facts["bundle_sha256"],
            hashlib.sha256(
                (self.root / BUNDLE_RELATIVE).read_bytes()
            ).hexdigest(),
        )
        self.assertEqual(
            post_facts["remote_observation"],
            {
                "remote": "origin",
                "ref": "refs/heads/main",
                "commit": frozen_commit,
                "observed_at": post_facts["remote_observation"]["observed_at"],
            },
        )

    def test_post_bundle_verifier_rejects_uncommitted_bundle(self) -> None:
        reviewed = self.prepare_completed_freeze()
        baseline = self.commit_and_push("valid review closure")
        freeze = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
            "--branch",
            "main",
        )
        self.assertEqual(freeze.returncode, 0, freeze.stdout)

        result = self.run_project_script(
            REMOTE_VERIFIER,
            "--verify-frozen-bundle",
            "--remote",
            "origin",
            "--branch",
            "main",
            "--json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("frozen_bundle_not_tracked", payload["errors"])
        self.assertIn("frozen_bundle_absent_from_HEAD", payload["errors"])

    def test_post_bundle_verifier_supports_nested_project_prefix(self) -> None:
        nested_repo = self.temp_root / "nested-repository"
        nested_project = nested_repo / "workspace" / "project"
        nested_bundle = nested_project / BUNDLE_RELATIVE
        nested_bundle.parent.mkdir(parents=True)
        nested_bundle.write_text('{"status": "fixture"}\n', encoding="utf-8")
        nested_remote = self.temp_root / "nested-remote.git"
        self.run_git(
            self.temp_root,
            "init",
            "--bare",
            "--initial-branch=main",
            str(nested_remote),
        )
        self.run_git(nested_repo, "init", "--initial-branch=main")
        self.run_git(nested_repo, "config", "user.name", "Governance Test")
        self.run_git(
            nested_repo,
            "config",
            "user.email",
            "governance@example.invalid",
        )
        self.run_git(nested_project, "add", ".")
        self.run_git(nested_project, "commit", "-m", "nested bundle fixture")
        self.run_git(
            nested_project,
            "remote",
            "add",
            "origin",
            str(nested_remote),
        )
        self.run_git(
            nested_project,
            "push",
            "--set-upstream",
            "origin",
            "main",
        )
        head = self.git_text(nested_project, "rev-parse", "HEAD")
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(nested_project)

        result = self.run_command(
            nested_project,
            sys.executable,
            str(REMOTE_VERIFIER),
            "--verify-frozen-bundle",
            "--remote",
            "origin",
            "--branch",
            "main",
            "--json",
            env=env,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(
            payload["facts"]["project_prefix"],
            "workspace/project/",
        )
        self.assertEqual(
            payload["facts"]["remote_observation"]["commit"],
            head,
        )

    def test_freeze_rejects_complete_forged_attack_replay_payload(self) -> None:
        replay_runner = self.root / "scripts" / "replay_design_freeze_attacks.py"
        replay_runner.write_text(
            "#!/usr/bin/env python3\n"
            "import json\n"
            "import subprocess\n"
            "def git(*args):\n"
            "    return subprocess.check_output(['git', *args], text=True).strip()\n"
            f"selectors = {CANONICAL_ATTACK_SELECTORS!r}\n"
            "results = [\n"
            "    {\n"
            "        'attack_id': attack_id,\n"
            "        'selector': selector,\n"
            "        'exit_code': 0,\n"
            "        'output_sha256': '0' * 64,\n"
            "        'result': 'rejected',\n"
            "    }\n"
            "    for attack_id, selector in selectors.items()\n"
            "]\n"
            "print(json.dumps({\n"
            "    'schema_version': 1,\n"
            "    'status': 'pass',\n"
            "    'candidate_commit': git('rev-parse', 'HEAD'),\n"
            "    'candidate_tree': git('rev-parse', 'HEAD^{tree}'),\n"
            "    'required_attack_ids': list(selectors),\n"
            "    'started_at': 'fixture-start',\n"
            "    'completed_at': 'fixture-end',\n"
            "    'results': results,\n"
            "    'stdout_sha256': '0' * 64,\n"
            "}))\n",
            encoding="utf-8",
        )
        attack_tests = (
            self.root / "governance_tests" / "test_final_review_attacks.py"
        )
        with attack_tests.open("a", encoding="utf-8") as handle:
            handle.write(
                "\nraise RuntimeError("
                "'canonical attack tests were replaced by a forged runner')\n"
            )
        baseline = self.commit_and_push("candidate with forged replay runner")
        baseline_tree = self.git_text(
            self.root,
            "rev-parse",
            f"{baseline}^{{tree}}",
        )
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        forged = self.run_command(
            self.root,
            sys.executable,
            str(replay_runner),
            env=env,
            check=False,
        )
        self.assertEqual(forged.returncode, 0, forged.stdout)
        forged_payload = json.loads(forged.stdout)
        self.assertEqual(forged_payload["status"], "pass")
        self.assertEqual(len(forged_payload["results"]), 4)
        self.assertTrue(
            all(
                item["result"] == "rejected" and item["exit_code"] == 0
                for item in forged_payload["results"]
            )
        )
        env["IDS_FREEZER_PATH"] = str(FREEZER)
        env["IDS_BASELINE_COMMIT"] = baseline
        env["IDS_BASELINE_TREE"] = baseline_tree
        probe = self.run_command(
            self.root,
            sys.executable,
            "-c",
            (
                "import importlib.util, os\n"
                "spec = importlib.util.spec_from_file_location("
                "'freeze_probe', os.environ['IDS_FREEZER_PATH'])\n"
                "module = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(module)\n"
                "module.require_design_freeze_attack_replay(\n"
                "    os.environ['IDS_BASELINE_COMMIT'],\n"
                "    os.environ['IDS_BASELINE_TREE'],\n"
                ")\n"
            ),
            env=env,
            check=False,
        )

        self.assertNotEqual(probe.returncode, 0, probe.stdout)
        self.assertIn(
            "design-freeze canonical attack replay failed",
            probe.stdout,
        )
        self.assertIn("canonical attack tests were replaced", probe.stdout)
        self.assert_bundle_absent()

    def test_git_verifier_rejects_other_upstream_even_when_origin_matches(self) -> None:
        other = self.temp_root / "other.git"
        self.run_git(
            self.temp_root,
            "init",
            "--bare",
            "--initial-branch=main",
            str(other),
        )
        self.run_git(self.root, "remote", "add", "other", str(other))
        self.run_git(self.root, "push", "--set-upstream", "other", "main")
        head = self.git_text(self.root, "rev-parse", "HEAD")

        result = self.run_project_script(
            GIT_VERIFIER,
            "--require-origin",
            "--expected-commit",
            head,
            "--branch",
            "main",
            "--json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn(
            "upstream is not trusted origin/main: got other/main",
            payload["errors"],
        )
        self.assertEqual(
            payload["facts"]["remote_observation"]["commit"],
            head,
        )
        untrusted_remote = self.run_project_script(
            REMOTE_VERIFIER,
            "--commit",
            head,
            "--remote",
            "other",
            "--branch",
            "main",
        )
        self.assertNotEqual(
            untrusted_remote.returncode,
            0,
            untrusted_remote.stdout,
        )
        self.assertIn(
            "--remote must be trusted remote 'origin'",
            untrusted_remote.stdout,
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
            "--branch",
            "main",
        )
        self.assertNotEqual(local_only.returncode, 0, local_only.stdout)
        self.assertIn("direct origin commit mismatch", local_only.stdout)

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
