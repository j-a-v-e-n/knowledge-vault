from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FREEZER = PROJECT_ROOT / "scripts" / "freeze_governance.py"
GIT_VERIFIER = PROJECT_ROOT / "scripts" / "verify_git_state.py"
REMOTE_VERIFIER = PROJECT_ROOT / "scripts" / "verify_remote_commit.py"
GOVERNANCE_VERIFIER = PROJECT_ROOT / "scripts" / "verify_governance.py"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
ASSURANCE_RELATIVE = "governance/ASSURANCE_SUBJECTS_V1.json"
GROUND_TRUTH_RELATIVE = "governance/GROUND_TRUTH_MANIFEST_V1.json"
RESEARCH_SUFFICIENCY_RELATIVE = "governance/RESEARCH_SUFFICIENCY_V1.json"
TARGETS_RELATIVE = "governance/IMPLEMENTATION_TARGETS_V1.json"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FINAL_EVIDENCE_RELATIVE = "audits/FINAL_REVIEW_EVIDENCE_SCHEMA_V2.json"
REVIEW_OUTPUT_RELATIVE = "audits/final_review_fixture/review-output.md"
MACHINE_MANIFEST_RELATIVE = "evidence/ci/assurance-manifest.json"
ATTESTATION_RELATIVE = "evidence/ci/attestation-verification.json"
NOVELTY_SPEC_RELATIVE = (
    "audits/final_review_probes/PROBE-FREEZE-SCHEMA-V2-POSTDATED.json"
)
NOVELTY_RECEIPT_RELATIVE = (
    "audits/final_review_attacks/novelty-freeze-schema-v2.json"
)
FINAL_REVIEW_SUBJECT = "SUBJECT-DESIGN-REVIEW-FINAL-SCHEMA-V2"
TEST_PROJECT_PREFIX = "workspace/project/"
INNER_CONTEXT_ENV = "IDS_FROZEN_REMOTE_INNER_CONTEXT_V1"
WORKFLOW_RELATIVE = ".github/workflows/investment-discipline-assurance.yml"
FIXTURE_REPOSITORY = "fixture-owner/fixture-repository"
ATTACK_IDS = (
    "ATTACK-PIT-ORACLE-INVERSION",
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
    "ATTACK-CONDITIONAL-SELF-ATTESTATION",
)
FINGERPRINT_FIELDS = (
    "runner_id",
    "runner_sha256",
    "candidate_commit",
    "candidate_tree",
    "project_prefix",
    "mode",
    "probe_id",
    "mutation_spec_sha256",
    "mutation_observation",
    "baseline",
    "target",
    "expected_rejection_substring",
    "result",
    "runner_exit_code",
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path, prefix: str, *, project_root: Path) -> ModuleType:
    module_name = f"{prefix}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    previous_root = os.environ.get("IDS_PROJECT_ROOT")
    os.environ["IDS_PROJECT_ROOT"] = str(project_root)
    try:
        spec.loader.exec_module(module)
    finally:
        if previous_root is None:
            os.environ.pop("IDS_PROJECT_ROOT", None)
        else:
            os.environ["IDS_PROJECT_ROOT"] = previous_root
    return module


class FreezeGitRemoteCounterexampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp.name)
        self.repo_root = self.temp_root / "repository"
        self.root = self.repo_root / TEST_PROJECT_PREFIX
        self.remote = self.temp_root / "remote.git"
        shutil.copytree(
            PROJECT_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        source_repository = Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=PROJECT_ROOT,
                text=True,
            ).strip()
        )
        source_workflow = source_repository / WORKFLOW_RELATIVE
        fixture_workflow = self.repo_root / WORKFLOW_RELATIVE
        fixture_workflow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_workflow, fixture_workflow)
        self.run_git(
            self.temp_root,
            "init",
            "--bare",
            "--initial-branch=main",
            str(self.remote),
        )
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        contract["change_control"]["trusted_git_remote"] = {
            "name": "origin",
            "fetch_url": str(self.remote),
            "branch": "main",
            "project_prefix": TEST_PROJECT_PREFIX,
        }
        self.write_json("governance/ACCEPTANCE_CONTRACT_V1.json", contract)
        trust = self.read_json("governance/ASSURANCE_TRUST_MODEL_V1.json")
        git_content = trust["trust_roots"]["git_content"]
        git_content.update(
            {
                "repository": FIXTURE_REPOSITORY,
                "remote_name": "origin",
                "fetch_url": str(self.remote),
                "branch": "main",
                "project_prefix": TEST_PROJECT_PREFIX,
            }
        )
        machine_trust = trust["trust_roots"][
            "github_actions_machine_execution"
        ]
        machine_trust["repository"] = FIXTURE_REPOSITORY
        machine_trust["attested_artifact_path"] = (
            f"{TEST_PROJECT_PREFIX}{MACHINE_MANIFEST_RELATIVE}"
        )
        self.write_json("governance/ASSURANCE_TRUST_MODEL_V1.json", trust)
        verifier = self.root / "scripts" / "verify_governance.py"
        verifier_source = verifier.read_text(encoding="utf-8")
        production_policy = (
            "EXPECTED_TRUSTED_GIT_REMOTE = {\n"
            '    "name": "origin",\n'
            '    "fetch_url": "git@github.com:j-a-v-e-n/knowledge-vault.git",\n'
            '    "branch": "main",\n'
            '    "project_prefix": '
            '"MyBrain/projects/investment-discipline-system/",\n'
            "}"
        )
        fixture_policy = (
            "EXPECTED_TRUSTED_GIT_REMOTE = {\n"
            '    "name": "origin",\n'
            f'    "fetch_url": {str(self.remote)!r},\n'
            '    "branch": "main",\n'
            f'    "project_prefix": {TEST_PROJECT_PREFIX!r},\n'
            "}"
        )
        self.assertIn(production_policy, verifier_source)
        machine_repository_policy = (
            '            "repository": "j-a-v-e-n/knowledge-vault",'
        )
        self.assertIn(machine_repository_policy, verifier_source)
        verifier_source = verifier_source.replace(
            production_policy,
            fixture_policy,
            1,
        ).replace(
            machine_repository_policy,
            f'            "repository": {FIXTURE_REPOSITORY!r},',
            1,
        )
        verifier.write_text(
            verifier_source,
            encoding="utf-8",
        )
        assurance_verifier = (
            self.root / "scripts" / "verify_assurance_metadata.py"
        )
        assurance_source = assurance_verifier.read_text(encoding="utf-8")
        repository_parser = (
            "def github_repository_from_url(value: Any) -> str | None:\n"
            "    if not isinstance(value, str):\n"
        )
        fixture_repository_parser = (
            "def github_repository_from_url(value: Any) -> str | None:\n"
            f"    if value == {str(self.remote)!r}:\n"
            f"        return {FIXTURE_REPOSITORY!r}\n"
            "    if not isinstance(value, str):\n"
        )
        self.assertIn(repository_parser, assurance_source)
        assurance_verifier.write_text(
            assurance_source.replace(
                repository_parser,
                fixture_repository_parser,
                1,
            ),
            encoding="utf-8",
        )
        self.run_git(self.repo_root, "init", "--initial-branch=main")
        self.run_git(self.repo_root, "config", "user.name", "Governance Test")
        self.run_git(
            self.repo_root,
            "config",
            "user.email",
            "governance@example.invalid",
        )
        self.run_git(self.repo_root, "add", "-A")
        self.run_git(self.root, "commit", "-m", "fixture preregistration anchor")
        preregistration_commit = self.git_text(
            self.root,
            "rev-parse",
            "HEAD",
        )
        self.make_research_sufficiency_eligible(preregistration_commit)
        refresh = self.run_project_script(
            PROJECT_ROOT / "scripts" / "refresh_ground_truth_manifest.py"
        )
        self.assertEqual(refresh.returncode, 0, refresh.stdout)
        self.run_git(self.repo_root, "add", "-A")
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
        fixture_script = self.root / script.relative_to(PROJECT_ROOT)
        return self.run_command(
            self.root,
            sys.executable,
            str(fixture_script),
            *args,
            env=env,
            check=False,
        )

    def read_json(self, relative: str) -> dict:
        return json.loads((self.root / relative).read_text(encoding="utf-8"))

    def write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def make_research_sufficiency_eligible(
        self,
        preregistration_commit: str,
    ) -> None:
        preregistration_relative = (
            "research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json"
        )
        preregistration = self.read_json(preregistration_relative)
        preregistration_bytes = subprocess.check_output(
            [
                "git",
                "show",
                (
                    f"{preregistration_commit}:{TEST_PROJECT_PREFIX}"
                    f"{preregistration_relative}"
                ),
            ],
            cwd=self.root,
        )
        preregistration_hash = hashlib.sha256(
            preregistration_bytes
        ).hexdigest()
        receipt = self.read_json(RESEARCH_SUFFICIENCY_RELATIVE)
        required_by_topic = preregistration[
            "required_source_classes_by_topic"
        ]
        query_limit = preregistration["budget"]["per_topic_query_limit"]
        round_limit = preregistration["budget"]["supplemental_round_limit"]

        for topic in receipt["topics"]:
            topic_id = topic["id"]
            source_classes = required_by_topic[topic_id]
            query_id = f"{topic_id}-QUERY-FIXTURE"
            source_ids = [
                f"{topic_id}-SOURCE-{index:02d}"
                for index in range(1, len(source_classes) + 1)
            ]
            topic["preregistration"] = {
                "timing_state": "verified_before_search",
                "git_commit": preregistration_commit,
                "artifact_path": preregistration_relative,
                "artifact_sha256": preregistration_hash,
                "timing_proof": {
                    "executor_platform": "Codex App subagents",
                    "agent_or_thread_locators": [
                        f"fixture:{topic_id}:counted-search"
                    ],
                    "observable_limitation": (
                        "The unit fixture validates temporal binding mechanics, "
                        "not an external research judgment."
                    ),
                },
            }
            topic["search_protocol"] = {
                "budget": {
                    "registration_state": "frozen_before_search",
                    "consumption_receipt_state": "complete",
                    "planned_query_limit": query_limit,
                    "planned_supplemental_round_limit": round_limit,
                    "consumed_query_count": 1,
                    "consumed_supplemental_round_count": 1,
                },
                "required_source_classes": source_classes,
                "result_set_state": "frozen_complete",
                "search_executions": [
                    {
                        "id": query_id,
                        "retrieved_at": "2026-07-25T16:00:00Z",
                        "channel": "fixture-deterministic",
                        "exact_query": f"{topic_id} fixture evidence",
                        "executor_locator": f"fixture:{topic_id}:executor",
                        "result_count": len(source_ids),
                        "result_source_ids": source_ids,
                    }
                ],
            }
            topic["source_outcomes"] = []
            topic["evidence_clusters"] = []
            for index, (source_class, source_id) in enumerate(
                zip(source_classes, source_ids, strict=True),
                start=1,
            ):
                cluster_id = f"{topic_id}-CLUSTER-{index:02d}"
                topic["source_outcomes"].append(
                    {
                        "id": source_id,
                        "screening_decision": "included",
                        "screening_reason": (
                            "Deterministic fixture source exercises the "
                            "complete result-set contract."
                        ),
                        "retrieved_at": "2026-07-25T16:00:00Z",
                        "channel": "fixture-deterministic",
                        "exact_query_or_locator": f"{topic_id}:{source_class}",
                        "locator": f"fixture:{topic_id}:{source_class}",
                        "observed_result": (
                            "The fixture records one included source for the "
                            "required source class."
                        ),
                        "source_class": source_class,
                        "revision_state": "content_hash_verified_current",
                        "evidence_fingerprint": hashlib.sha256(
                            f"{topic_id}:{source_class}".encode("utf-8")
                        ).hexdigest(),
                        "cluster_ids": [cluster_id],
                        "query_ids": [query_id],
                    }
                )
                topic["evidence_clusters"].append(
                    {
                        "id": cluster_id,
                        "member_source_ids": [source_id],
                        "upstream_roots": [
                            f"fixture-root:{topic_id}:{source_class}"
                        ],
                        "revision_check_state": (
                            "content_hash_verified_current"
                        ),
                    }
                )
            claim_id = f"{topic_id}-CLAIM-FIXTURE"
            topic["claims"] = [
                {
                    "id": claim_id,
                    "impact": "high",
                    "entailment_status": "entailed",
                    "review_state": "deterministic_receipt",
                    "evidence_cluster_ids": [
                        item["id"] for item in topic["evidence_clusters"]
                    ],
                    "source_range_or_receipt": (
                        f"{RESEARCH_SUFFICIENCY_RELATIVE}#/{topic_id}"
                    ),
                    "limitations": (
                        "This synthetic claim exists only to exercise the "
                        "fail-closed sufficiency derivation."
                    ),
                    "decision_effect": (
                        "Allows the fixture candidate to enter final review."
                    ),
                }
            ]
            topic["supplemental_rounds"] = [
                {
                    "id": f"{topic_id}-ROUND-FIXTURE",
                    "round_type": "independent_challenge",
                    "result": "completed_stable",
                    "architecture_delta_ids": [],
                    "decision_delta_ids": [],
                    "new_high_impact_node_ids": [],
                }
            ]
            topic["unresolved_contradictions"] = []
            topic["deltas"] = {"architecture": [], "decisions": []}
            topic["reopen_triggers"] = [
                {
                    "id": f"{topic_id}-REOPEN-FIXTURE",
                    "condition": "A bound fixture input changes.",
                    "action": "Recompute the deterministic fixture receipt.",
                    "affected_claim_ids": [claim_id],
                }
            ]

        for gap in receipt["open_gaps"]:
            gap["state"] = "resolved"
        stable_input = "EVIDENCE_GOVERNED_AI_SYSTEM.md"
        receipt["derivation_rules"]["input_snapshot"] = [
            {
                "id": "INPUT-FIXTURE-STABLE",
                "path": stable_input,
                "sha256": sha256_file(self.root / stable_input),
            }
        ]

        research = self.read_json(RESEARCH_RELATIVE)
        for artifact in research["primary_artifacts"]:
            artifact["sha256"] = sha256_file(self.root / artifact["path"])
        self.write_json(RESEARCH_RELATIVE, research)

        verifier = load_module(
            self.root / "scripts" / "verify_research_sufficiency.py",
            "fixture_research_sufficiency",
            project_root=self.root,
        )
        evaluation = verifier.evaluate(receipt)
        self.assertTrue(evaluation["derived_pre_review_eligible"], evaluation)
        receipt["derived_pre_review_eligible"] = evaluation[
            "derived_pre_review_eligible"
        ]
        receipt["derived_research_state"] = evaluation[
            "derived_research_state"
        ]
        receipt["derivation_rules"]["current_evaluation"] = {
            "derived_research_state": evaluation["derived_research_state"],
            "evaluated_input_sha256_state": evaluation[
                "evaluated_input_sha256_state"
            ],
            "rule_results": evaluation["rule_results"],
        }
        self.write_json(RESEARCH_SUFFICIENCY_RELATIVE, receipt)
        verified = self.run_project_script(
            PROJECT_ROOT / "scripts" / "verify_research_sufficiency.py",
            "--json",
        )
        self.assertEqual(verified.returncode, 0, verified.stdout)

    def novelty_spec(self) -> dict[str, Any]:
        policy = self.read_json("governance/PRIVATE_DATA_POLICY_V1.json")
        current_mode = policy["runtime_storage"]["file_mode"]
        return {
            "schema_version": 1,
            "probe_id": "PROBE-FREEZE-SCHEMA-V2-POSTDATED",
            "target_path": "governance/PRIVATE_DATA_POLICY_V1.json",
            "json_pointer": "/runtime_storage/file_mode",
            "operation": "replace",
            "expected_before_sha256": digest_value(current_mode),
            "replacement": "0644",
            "expected_rejection_substring": (
                "private runtime storage boundary differs"
            ),
            "rationale": (
                "A permissive private-state mode must remain blocked by the "
                "candidate's frozen privacy boundary."
            ),
        }

    def run_attack(
        self,
        *,
        candidate_commit: str,
        candidate_tree: str,
        extra_args: list[str],
        receipt_relative: str,
    ) -> dict[str, Any]:
        completed = self.run_project_script(
            PROJECT_ROOT / "scripts" / "run_design_freeze_attack.py",
            "--candidate-commit",
            candidate_commit,
            *extra_args,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        receipt = json.loads(completed.stdout)
        self.assertEqual(receipt["schema_version"], 2)
        self.assertEqual(receipt["candidate_commit"], candidate_commit)
        self.assertEqual(receipt["candidate_tree"], candidate_tree)
        self.assertEqual(receipt["project_prefix"], TEST_PROJECT_PREFIX)
        self.assertEqual(receipt["result"], "rejected")
        self.assertEqual(receipt["runner_exit_code"], completed.returncode)
        self.assertEqual(receipt["baseline"]["exit_code"], 0)
        self.assertNotEqual(receipt["target"]["exit_code"], 0)
        receipt_path = self.root / receipt_relative
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(completed.stdout, encoding="utf-8")
        return receipt

    def collect_reviewed_files(
        self,
        *,
        candidate_commit: str,
    ) -> list[str]:
        verifier = load_module(
            self.root / "scripts" / "verify_governance.py",
            "fixture_governance",
            project_root=self.root,
        )
        required = set(verifier.FINAL_REVIEW_REQUIRED_SCOPE)
        ground_truth = self.read_json(GROUND_TRUTH_RELATIVE)
        for artifact in ground_truth["artifacts"]:
            if artifact.get("required") is not True:
                continue
            relative = artifact["path"]
            if artifact.get("scope", "project") == "repository":
                required.add(f"{verifier.REPOSITORY_SCOPE_PREFIX}{relative}")
            else:
                required.add(relative)
        contract = self.read_json(
            "governance/ACCEPTANCE_CONTRACT_V1.json"
        )
        required.update(contract["change_control"]["frozen_files"])
        targets = self.read_json(TARGETS_RELATIVE)
        for target in targets["targets"]:
            if target.get("required_by") != "design_freeze":
                continue
            relative = target["path"]
            if target["kind"] == "file":
                required.add(relative)
                continue
            listing = self.git_text(
                self.root,
                "ls-tree",
                "-r",
                "--full-tree",
                "--name-only",
                candidate_commit,
                "--",
                f":(top,literal){TEST_PROJECT_PREFIX}{relative}",
            )
            required.update(
                item.removeprefix(TEST_PROJECT_PREFIX)
                for item in listing.splitlines()
                if item.startswith(TEST_PROJECT_PREFIX)
            )
        return sorted(required)

    def commit_and_push(self, message: str) -> str:
        self.run_git(self.root, "add", "-A")
        self.run_git(self.root, "commit", "-m", message)
        self.run_git(self.root, "push", "origin", "main")
        return self.git_text(self.root, "rev-parse", "HEAD")

    def commit_without_push(self, message: str) -> str:
        self.run_git(self.root, "add", "-A")
        self.run_git(self.root, "commit", "-m", message)
        return self.git_text(self.root, "rev-parse", "HEAD")

    def create_frozen_bundle_file(self) -> tuple[str, str]:
        reviewed = self.prepare_completed_freeze()
        baseline = self.commit_and_push("valid review closure")
        freeze = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )
        self.assertEqual(freeze.returncode, 0, freeze.stdout)
        return reviewed, baseline

    def install_inner_clone_failure(self) -> None:
        verifier = self.root / "scripts" / "verify_governance.py"
        source = verifier.read_text(encoding="utf-8")
        marker = '\nif __name__ == "__main__":\n'
        self.assertIn(marker, source)
        source = source.replace(
            marker,
            (
                "\nif os.environ.get("
                f"{INNER_CONTEXT_ENV!r}"
                "):\n"
                "    print('fixture: fresh-clone governance verifier failed')\n"
                "    raise SystemExit(41)\n"
                f"{marker}"
            ),
            1,
        )
        verifier.write_text(source, encoding="utf-8")
        self.commit_and_push("candidate with failing inner clone verifier")

    def prepare_completed_freeze(
        self, *, incomplete_relative: str | None = None
    ) -> str:
        reviewed_commit = self.git_text(self.root, "rev-parse", "HEAD")
        reviewed_tree = self.git_text(
            self.root, "rev-parse", f"{reviewed_commit}^{{tree}}"
        )
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        frozen_files = contract["change_control"]["frozen_files"]
        self.write_json(NOVELTY_SPEC_RELATIVE, self.novelty_spec())
        canonical_attacks: list[dict[str, str]] = []
        canonical_receipts: list[dict[str, Any]] = []
        for index, attack_id in enumerate(ATTACK_IDS, start=1):
            receipt_relative = (
                "audits/final_review_attacks/"
                f"canonical-{index:02d}-{attack_id.lower()}.json"
            )
            receipt = self.run_attack(
                candidate_commit=reviewed_commit,
                candidate_tree=reviewed_tree,
                extra_args=["--attack-id", attack_id],
                receipt_relative=receipt_relative,
            )
            canonical_receipts.append(receipt)
            canonical_attacks.append(
                {
                    "attack_id": attack_id,
                    "runner_receipt_path": receipt_relative,
                    "runner_receipt_sha256": sha256_file(
                        self.root / receipt_relative
                    ),
                }
            )
        novelty_receipt = self.run_attack(
            candidate_commit=reviewed_commit,
            candidate_tree=reviewed_tree,
            extra_args=[
                "--novelty-spec",
                str(self.root / NOVELTY_SPEC_RELATIVE),
            ],
            receipt_relative=NOVELTY_RECEIPT_RELATIVE,
        )
        candidate_governance = self.run_project_script(
            GOVERNANCE_VERIFIER,
            "--allow-candidate",
        )
        self.assertEqual(
            candidate_governance.returncode,
            0,
            candidate_governance.stdout,
        )
        reviewed_files = self.collect_reviewed_files(
            candidate_commit=reviewed_commit
        )

        for relative in frozen_files:
            if Path(relative).suffix.lower() != ".json":
                continue
            document = self.read_json(relative)
            if relative == RESEARCH_RELATIVE:
                document["status"] = "adopted_with_explicit_limits"
            elif relative == incomplete_relative:
                document["status"] = "candidate_for_freeze"
            else:
                document["status"] = "frozen"
            self.write_json(relative, document)

        review_output = (
            "# Final schema-v2 fixture review\n\n"
            f"Candidate commit: {reviewed_commit}\n\n"
            f"Candidate tree: {reviewed_tree}\n\n"
            "The frozen production runner rejected every canonical mutation "
            "and the candidate-postdated novelty probe.\n"
        )
        review_output_path = self.root / REVIEW_OUTPUT_RELATIVE
        review_output_path.parent.mkdir(parents=True, exist_ok=True)
        review_output_path.write_text(review_output, encoding="utf-8")

        machine_replay = {
            "schema_version": 2,
            "status": "pass",
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "runner_id": "ids-design-freeze-attack-runner-v1",
            "runner_sha256": canonical_receipts[0]["runner_sha256"],
            "required_attack_ids": list(ATTACK_IDS),
            "started_at": "2026-07-25T16:10:00Z",
            "completed_at": "2026-07-25T16:11:00Z",
            "results": [
                {
                    "attack_id": receipt["probe_id"],
                    "actual_runner_process_exit": 0,
                    "declared_runner_exit_code": receipt[
                        "runner_exit_code"
                    ],
                    "baseline_verifier_exit": receipt["baseline"][
                        "exit_code"
                    ],
                    "target_verifier_exit": receipt["target"][
                        "exit_code"
                    ],
                    "baseline_stdout_sha256": receipt["baseline"][
                        "stdout_sha256"
                    ],
                    "target_stdout_sha256": receipt["target"][
                        "stdout_sha256"
                    ],
                    "execution_fingerprint": receipt[
                        "execution_fingerprint"
                    ],
                    "receipt_sha256": sha256_file(
                        self.root / binding["runner_receipt_path"]
                    ),
                    "result": "rejected",
                }
                for receipt, binding in zip(
                    canonical_receipts,
                    canonical_attacks,
                    strict=True,
                )
            ],
        }

        def machine_check(
            check_id: str,
            argv: list[str],
            *,
            cwd: str = "PROJECT_ROOT",
            stdout: str = "fixture check passed\n",
            structured_result: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            check: dict[str, Any] = {
                "check_id": check_id,
                "argv": argv,
                "cwd": cwd,
                "actual_process_exit": 0,
                "stdout_sha256": hashlib.sha256(
                    stdout.encode("utf-8")
                ).hexdigest(),
                "stdout_tail": stdout[-4000:],
                "result": "pass",
            }
            if structured_result is not None:
                check["structured_result"] = structured_result
            return check

        machine_check_ids = [
            "CHECK-ASSURANCE-METADATA",
            "CHECK-PROJECT-METHOD",
            "CHECK-CANDIDATE-GOVERNANCE",
            "CHECK-CANONICAL-ATTACK-REPLAY",
            "CHECK-GOVERNANCE-REGRESSION",
            "CHECK-COMPILEALL",
            "CHECK-RUFF",
            "CHECK-GIT-DIFF",
        ]
        machine_checks = [
            machine_check(
                "CHECK-ASSURANCE-METADATA",
                [
                    "PYTHON",
                    "scripts/verify_assurance_metadata.py",
                    "--json",
                ],
                structured_result={"status": "pass", "errors": []},
            ),
            machine_check(
                "CHECK-PROJECT-METHOD",
                ["PYTHON", "scripts/verify_project_method.py", "--json"],
                structured_result={"status": "pass", "errors": []},
            ),
            machine_check(
                "CHECK-CANDIDATE-GOVERNANCE",
                [
                    "PYTHON",
                    "scripts/verify_governance.py",
                    "--allow-candidate",
                ],
                stdout=candidate_governance.stdout,
            ),
            machine_check(
                "CHECK-CANONICAL-ATTACK-REPLAY",
                [
                    "PYTHON",
                    "scripts/replay_design_freeze_attacks.py",
                    "--candidate-commit",
                    reviewed_commit,
                ],
                stdout=json.dumps(machine_replay, sort_keys=True) + "\n",
                structured_result=machine_replay,
            ),
            machine_check(
                "CHECK-GOVERNANCE-REGRESSION",
                [
                    "PYTHON",
                    "-m",
                    "unittest",
                    "discover",
                    "-s",
                    "governance_tests",
                    "-v",
                ],
            ),
            machine_check(
                "CHECK-COMPILEALL",
                ["PYTHON", "-m", "compileall", "-q", "."],
            ),
            machine_check(
                "CHECK-RUFF",
                ["PYTHON", "-m", "ruff", "check", "."],
            ),
            machine_check(
                "CHECK-GIT-DIFF",
                ["git", "diff", "--check", reviewed_commit],
                cwd="REPOSITORY_ROOT",
            ),
        ]
        machine_manifest = {
            "schema_version": 1,
            "manifest_id": "ids-github-machine-assurance-v1",
            "status": "pass",
            "assurance_level": "github_issued_workflow_provenance",
            "semantic_approval": False,
            "repository": FIXTURE_REPOSITORY,
            "workflow": "Investment Discipline Machine Assurance",
            "workflow_ref": (
                f"{FIXTURE_REPOSITORY}/{WORKFLOW_RELATIVE}"
                "@refs/heads/main"
            ),
            "workflow_sha": reviewed_commit,
            "run_id": "fixture-run-1",
            "run_attempt": "1",
            "event_name": "workflow_dispatch",
            "github_sha_matches_candidate": True,
            "runner_environment": "github-hosted",
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "project_prefix": TEST_PROJECT_PREFIX,
            "required_check_ids": machine_check_ids,
            "started_at": "2026-07-25T16:00:00Z",
            "completed_at": "2026-07-25T16:12:00Z",
            "checks": machine_checks,
            "limitations": [
                "The local unit fixture models an externally verified manifest."
            ],
        }
        self.write_json(MACHINE_MANIFEST_RELATIVE, machine_manifest)
        machine_hash = sha256_file(self.root / MACHINE_MANIFEST_RELATIVE)
        self.write_json(
            ATTESTATION_RELATIVE,
            {
                "schema_version": 1,
                "verification_id": (
                    "ids-github-attestation-verification-v1"
                ),
                "status": "pass",
                "fixture_only": False,
                "repository": FIXTURE_REPOSITORY,
                "workflow_path": WORKFLOW_RELATIVE,
                "source_ref": "refs/heads/main",
                "candidate_commit": reviewed_commit,
                "candidate_tree": reviewed_tree,
                "project_prefix": TEST_PROJECT_PREFIX,
                "subject": {
                    "path": MACHINE_MANIFEST_RELATIVE,
                    "sha256": machine_hash,
                },
                "policy_checks": {
                    "repository_matches": True,
                    "workflow_matches": True,
                    "source_commit_matches": True,
                    "source_ref_matches": True,
                    "hosted_runner_required": True,
                    "subject_digest_matches": True,
                },
                "limitations": [
                    "The test exercises binding validation without claiming "
                    "that a local fixture is a GitHub-issued signature."
                ],
            },
        )
        review_input = (
            "Review the exact candidate commit and tree against the complete "
            "candidate ground-truth manifest. Replay every canonical attack "
            "and execute one candidate-postdated novelty probe. Pass only "
            "with no open finding or new architecture-changing class."
        )
        commands_run = [
            (
                "PYTHON scripts/run_design_freeze_attack.py "
                f"--candidate-commit {reviewed_commit} "
                f"--attack-id {attack_id}"
            )
            for attack_id in ATTACK_IDS
        ]
        commands_run.append(
            (
                "PYTHON scripts/run_design_freeze_attack.py "
                f"--candidate-commit {reviewed_commit} "
                f"--novelty-spec {NOVELTY_SPEC_RELATIVE}"
            )
        )
        evidence = {
            "schema_version": 2,
            "subject_id": FINAL_REVIEW_SUBJECT,
            "review_locator": (
                "fixture:platform-observable-separate-thread"
            ),
            "assurance_level": (
                "platform_observable_separate_thread_review"
            ),
            "review_input": review_input,
            "review_input_sha256": hashlib.sha256(
                review_input.encode("utf-8")
            ).hexdigest(),
            "review_output_path": REVIEW_OUTPUT_RELATIVE,
            "review_output_sha256": sha256_file(review_output_path),
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "ground_truth_manifest_path": GROUND_TRUTH_RELATIVE,
            "ground_truth_manifest_sha256": sha256_file(
                self.root / GROUND_TRUTH_RELATIVE
            ),
            "machine_assurance_manifest_path": MACHINE_MANIFEST_RELATIVE,
            "machine_assurance_manifest_sha256": machine_hash,
            "machine_attestation_verification_path": ATTESTATION_RELATIVE,
            "machine_attestation_verification_sha256": sha256_file(
                self.root / ATTESTATION_RELATIVE
            ),
            "verdict": "passed_freeze",
            "open_critical_count": 0,
            "open_major_count": 0,
            "open_minor_count": 0,
            "new_architecture_changing_classes": [],
            "participated_in_candidate_construction": False,
            "write_access_used": False,
            "reviewed_files": reviewed_files,
            "commands_run": commands_run,
            "canonical_attacks": canonical_attacks,
            "novelty_probes": [
                {
                    "probe_id": novelty_receipt["probe_id"],
                    "spec_path": NOVELTY_SPEC_RELATIVE,
                    "spec_sha256": sha256_file(
                        self.root / NOVELTY_SPEC_RELATIVE
                    ),
                    "runner_receipt_path": NOVELTY_RECEIPT_RELATIVE,
                    "runner_receipt_sha256": sha256_file(
                        self.root / NOVELTY_RECEIPT_RELATIVE
                    ),
                }
            ],
            "findings": [],
            "finding_ids": [],
            "what_would_falsify_pass": [
                "A production-runner replay produces a different fingerprint."
            ],
            "limitations": [
                "The fixture proves governance binding behavior, not "
                "production investment correctness."
            ],
        }
        self.write_json(FINAL_EVIDENCE_RELATIVE, evidence)
        evidence_hash = sha256_file(self.root / FINAL_EVIDENCE_RELATIVE)

        research = self.read_json(RESEARCH_RELATIVE)
        research["challenge"]["status"] = "completed"
        research["challenge"]["rounds"].append(
            {
                "id": "CHALLENGE-FINAL-SCHEMA-V2",
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
                "disposition": (
                    "Schema-v2 closure evidence directly closes the "
                    "post-candidate challenge."
                ),
            }
        )
        self.write_json(RESEARCH_RELATIVE, research)

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
        invalid_candidate = self.commit_and_push(
            "remove candidate governance input"
        )

        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            invalid_candidate,
            "--reviewed-candidate-commit",
            invalid_candidate,
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
            f":(top,literal){TEST_PROJECT_PREFIX}{relative}",
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
        self.assertEqual(bundle["final_review_schema_version"], 2)
        self.assertEqual(
            bundle["review_output_sha256"],
            sha256_file(self.root / REVIEW_OUTPUT_RELATIVE),
        )
        self.assertEqual(
            bundle["ground_truth_manifest_sha256"],
            sha256_file(self.root / GROUND_TRUTH_RELATIVE),
        )
        candidate_ground_truth = subprocess.check_output(
            [
                "git",
                "show",
                (
                    f"{reviewed}:{TEST_PROJECT_PREFIX}"
                    f"{GROUND_TRUTH_RELATIVE}"
                ),
            ],
            cwd=self.root,
        )
        self.assertEqual(
            bundle["reviewed_ground_truth_candidate_sha256"],
            hashlib.sha256(candidate_ground_truth).hexdigest(),
        )
        self.assertEqual(
            bundle["machine_assurance_manifest_sha256"],
            sha256_file(self.root / MACHINE_MANIFEST_RELATIVE),
        )
        self.assertEqual(
            bundle["machine_attestation_verification_sha256"],
            sha256_file(self.root / ATTESTATION_RELATIVE),
        )

        research = self.read_json(RESEARCH_RELATIVE)
        primary_paths = {
            artifact["path"] for artifact in research["primary_artifacts"]
        }
        self.assertNotIn(FINAL_EVIDENCE_RELATIVE, primary_paths)
        final_round = research["challenge"]["rounds"][-1]
        self.assertEqual(final_round["candidate_commit"], reviewed)
        self.assertEqual(
            final_round["candidate_tree"],
            bundle["reviewed_candidate_tree"],
        )
        self.assertEqual(
            final_round["evidence_path"],
            FINAL_EVIDENCE_RELATIVE,
        )
        self.assertEqual(
            final_round["evidence_sha256"],
            bundle["final_review_evidence_sha256"],
        )

        closure_artifacts = {
            item["path"]: item
            for item in bundle["review_closure_artifacts"]
        }
        expected_closure_paths = {
            FINAL_EVIDENCE_RELATIVE,
            REVIEW_OUTPUT_RELATIVE,
            MACHINE_MANIFEST_RELATIVE,
            ATTESTATION_RELATIVE,
            NOVELTY_SPEC_RELATIVE,
            NOVELTY_RECEIPT_RELATIVE,
            *[
                item["runner_receipt_path"]
                for item in bundle["canonical_attacks"]
            ],
        }
        self.assertEqual(set(closure_artifacts), expected_closure_paths)
        for relative, binding in closure_artifacts.items():
            self.assertEqual(binding["sha256"], sha256_file(self.root / relative))
            self.assertEqual(binding["git_mode"], "100644")
            self.assertEqual(binding["git_type"], "blob")
            self.assertEqual(binding["git_object_kind"], "blob")
            self.assertEqual(len(binding["git_blob"]), 40)

        replay = bundle["design_freeze_attack_replay"]
        self.assertEqual(replay["schema_version"], 2)
        self.assertEqual(replay["status"], "pass")
        self.assertEqual(replay["candidate_commit"], reviewed)
        self.assertEqual(
            replay["candidate_tree"],
            self.git_text(self.root, "rev-parse", f"{reviewed}^{{tree}}"),
        )
        self.assertEqual(replay["required_attack_ids"], list(ATTACK_IDS))
        self.assertEqual(len(replay["required_attack_ids"]), 4)
        replay_results = {
            item["attack_id"]: item for item in replay["results"]
        }
        self.assertEqual(set(replay_results), set(ATTACK_IDS))
        self.assertEqual(len(replay["results"]), 4)
        bound_fingerprints = {
            item["attack_id"]: self.read_json(
                item["runner_receipt_path"]
            )["execution_fingerprint"]
            for item in bundle["canonical_attacks"]
        }
        for attack_id in ATTACK_IDS:
            attack_result = replay_results[attack_id]
            self.assertEqual(attack_result["result"], "rejected")
            self.assertEqual(attack_result["actual_runner_process_exit"], 0)
            self.assertEqual(attack_result["declared_runner_exit_code"], 0)
            self.assertEqual(attack_result["baseline_verifier_exit"], 0)
            self.assertNotEqual(attack_result["target_verifier_exit"], 0)
            self.assertEqual(
                attack_result["execution_fingerprint"],
                bound_fingerprints[attack_id],
            )
            for field in (
                "baseline_stdout_sha256",
                "target_stdout_sha256",
                "execution_fingerprint",
                "receipt_sha256",
            ):
                self.assertEqual(len(attack_result[field]), 64)
        self.assertEqual(
            bundle["trusted_git_remote"],
            {
                "name": "origin",
                "fetch_url": str(self.remote),
                "branch": "main",
                "project_prefix": TEST_PROJECT_PREFIX,
            },
        )
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
            self.assertEqual(observation["fetch_url"], str(self.remote))
            self.assertEqual(observation["ref"], "refs/heads/main")
            self.assertEqual(observation["commit"], baseline)
            self.assertEqual(
                observation["observation_kind"],
                "non_atomic_ls_remote",
            )
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
        self.assertEqual(post_payload["verification_scope"], "full_outer")
        post_facts = post_payload["facts"]
        self.assertEqual(post_facts["verification_scope"], "full_outer")
        self.assertTrue(post_facts["full_remote_verification"])
        self.assertTrue(post_facts["fresh_clone"])
        self.assertEqual(
            post_facts["clone_governance"]["verification_scope"],
            "inner_clone",
        )
        self.assertEqual(
            post_facts["clone_governance"]["inner_receipt"][
                "verification_scope"
            ],
            "inner_clone",
        )
        self.assertEqual(post_facts["head"], frozen_commit)
        self.assertEqual(
            post_facts["project_prefix"],
            TEST_PROJECT_PREFIX,
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
                "fetch_url": str(self.remote),
                "ref": "refs/heads/main",
                "commit": frozen_commit,
                "observed_at": post_facts["remote_observation"]["observed_at"],
                "observation_kind": "non_atomic_ls_remote",
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

    def test_post_bundle_verifier_rejects_D_that_only_exists_locally(
        self,
    ) -> None:
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_without_push("local-only bundle commit D")

        result = self.run_project_script(
            REMOTE_VERIFIER,
            "--verify-frozen-bundle",
            "--commit",
            frozen_commit,
            "--json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(
            payload["verification_scope"],
            "full_outer_required",
        )
        self.assertIn("remote_commit_mismatch", "\n".join(payload["errors"]))
        self.assertNotIn("fresh_clone", payload["facts"])

    def test_post_bundle_verifier_supports_nested_project_prefix(self) -> None:
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_and_push("commit nested frozen bundle")

        result = self.run_project_script(
            REMOTE_VERIFIER,
            "--verify-frozen-bundle",
            "--remote",
            "origin",
            "--branch",
            "main",
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["verification_scope"], "full_outer")
        self.assertEqual(
            payload["facts"]["project_prefix"],
            TEST_PROJECT_PREFIX,
        )
        self.assertEqual(
            payload["facts"]["remote_observation"]["commit"],
            frozen_commit,
        )
        self.assertEqual(payload["facts"]["cloned_commit"], frozen_commit)

    def test_fresh_clone_governance_nonzero_rejects_bundle_D(self) -> None:
        self.install_inner_clone_failure()
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_and_push("bundle D with reviewed fail probe")

        result = self.run_project_script(
            REMOTE_VERIFIER,
            "--verify-frozen-bundle",
            "--commit",
            frozen_commit,
            "--json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertTrue(payload["facts"]["fresh_clone"])
        self.assertEqual(
            payload["facts"]["clone_governance"]["exit_code"],
            41,
        )
        self.assertIn(
            "fresh_clone_governance_failed",
            "\n".join(payload["errors"]),
        )
        self.assertIn(
            "fixture: fresh-clone governance verifier failed",
            "\n".join(payload["errors"]),
        )

    def test_bundle_parameter_combinations_cannot_skip_fresh_clone(
        self,
    ) -> None:
        self.install_inner_clone_failure()
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_and_push(
            "bundle D for clone-combination counterexample"
        )
        variants = [
            [],
            ["--commit", frozen_commit],
            [
                "--commit",
                frozen_commit,
                "--fresh-clone",
                "--remote",
                "origin",
                "--branch",
                "main",
            ],
        ]

        for extra in variants:
            with self.subTest(arguments=extra):
                result = self.run_project_script(
                    REMOTE_VERIFIER,
                    "--verify-frozen-bundle",
                    *extra,
                    "--json",
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)
                payload = json.loads(result.stdout)
                self.assertTrue(payload["facts"]["fresh_clone"])
                self.assertEqual(
                    payload["facts"]["clone_governance"]["exit_code"],
                    41,
                )
                self.assertIn(
                    "fresh_clone_governance_failed",
                    "\n".join(payload["errors"]),
                )

    def test_inner_clone_result_cannot_claim_full_outer_verification(
        self,
    ) -> None:
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_and_push(
            "bundle D for inner-scope counterexample"
        )
        context = {
            "schema_version": 1,
            "mode": "fresh_clone_governance_v1",
            "nonce": "1" * 64,
            "commit": frozen_commit,
            "remote_name": "origin",
            "fetch_url": str(self.remote),
            "branch": "main",
            "project_prefix": TEST_PROJECT_PREFIX,
            "repo_root": str(self.repo_root),
            "project_root": str(self.root),
            "receipt_path": str(self.temp_root / "forged-inner-receipt.json"),
        }
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        env[INNER_CONTEXT_ENV] = json.dumps(context, sort_keys=True)

        result = self.run_command(
            self.root,
            sys.executable,
            str(self.root / "scripts" / "verify_remote_commit.py"),
            "--verify-frozen-bundle",
            "--commit",
            frozen_commit,
            "--remote",
            "origin",
            "--json",
            env=env,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["verification_scope"], "inner_clone")
        self.assertEqual(
            payload["facts"]["verification_scope"],
            "inner_clone",
        )
        self.assertFalse(payload["facts"]["full_remote_verification"])
        self.assertIn(
            "fresh_clone_HEAD_must_be_detached",
            "\n".join(payload["errors"]),
        )

    def test_governance_normal_mode_rejects_forged_inner_scope(self) -> None:
        self.create_frozen_bundle_file()
        frozen_commit = self.commit_and_push(
            "bundle D for governance scope counterexample"
        )
        fake_remote = self.root / "scripts" / "verify_remote_commit.py"
        fake_remote.write_text(
            "#!/usr/bin/env python3\n"
            "import hashlib, json, subprocess\n"
            "from pathlib import Path\n"
            "head = subprocess.check_output("
            "['git', 'rev-parse', 'HEAD'], text=True).strip()\n"
            "bundle = Path('governance/FROZEN_BUNDLE_V1.json')\n"
            "facts = {\n"
            "  'mode': 'frozen_bundle_inner_clone',\n"
            "  'verification_scope': 'inner_clone',\n"
            "  'full_remote_verification': False,\n"
            "  'head': head,\n"
            "  'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),\n"
            "  'bundle_git_mode': '100644',\n"
            "  'bundle_git_type': 'blob',\n"
            "}\n"
            "print(json.dumps({"
            "'schema_version': 1, 'status': 'pass', "
            "'verification_scope': 'inner_clone', "
            "'facts': facts, 'errors': []}))\n",
            encoding="utf-8",
        )

        result = self.run_project_script(GOVERNANCE_VERIFIER)

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "frozen bundle is not the tracked HEAD blob on trusted origin",
            result.stdout,
        )
        self.assertIn(frozen_commit, result.stdout)

    def test_freeze_rejects_forged_schema_v2_runner_receipt(self) -> None:
        reviewed = self.prepare_completed_freeze()
        evidence = self.read_json(FINAL_EVIDENCE_RELATIVE)
        attack_binding = evidence["canonical_attacks"][0]
        receipt_relative = attack_binding["runner_receipt_path"]
        receipt = self.read_json(receipt_relative)
        forged_stdout = (
            f"{receipt['expected_rejection_substring']}\n"
            "fixture-forged-target-output"
        )
        receipt["target"]["stdout"] = forged_stdout
        receipt["target"]["stdout_sha256"] = hashlib.sha256(
            forged_stdout.encode("utf-8")
        ).hexdigest()
        receipt["execution_fingerprint"] = digest_value(
            {
                field: receipt.get(field)
                for field in FINGERPRINT_FIELDS
            }
        )
        self.write_json(receipt_relative, receipt)
        attack_binding["runner_receipt_sha256"] = sha256_file(
            self.root / receipt_relative
        )
        self.write_json(FINAL_EVIDENCE_RELATIVE, evidence)
        evidence_hash = sha256_file(self.root / FINAL_EVIDENCE_RELATIVE)

        research = self.read_json(RESEARCH_RELATIVE)
        research["challenge"]["rounds"][-1][
            "evidence_sha256"
        ] = evidence_hash
        self.write_json(RESEARCH_RELATIVE, research)
        assurance = self.read_json(ASSURANCE_RELATIVE)
        assurance["subjects"][-1]["evidence_sha256"] = evidence_hash
        self.write_json(ASSURANCE_RELATIVE, assurance)

        baseline = self.commit_and_push("closure with forged runner receipt")
        result = self.run_project_script(
            FREEZER,
            "--baseline-commit",
            baseline,
            "--reviewed-candidate-commit",
            reviewed,
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("actual runner replay differs", result.stdout)
        self.assert_bundle_absent()

    def test_origin_name_cannot_hide_changed_fetch_url(self) -> None:
        alternate = self.temp_root / "alternate.git"
        self.run_git(
            self.temp_root,
            "init",
            "--bare",
            "--initial-branch=main",
            str(alternate),
        )
        self.run_git(
            self.root,
            "remote",
            "add",
            "alternate",
            str(alternate),
        )
        self.run_git(self.root, "push", "alternate", "main")
        self.run_git(
            self.root,
            "remote",
            "set-url",
            "origin",
            str(alternate),
        )
        head = self.git_text(self.root, "rev-parse", "HEAD")

        git_result = self.run_project_script(
            GIT_VERIFIER,
            "--require-origin",
            "--expected-commit",
            head,
            "--json",
        )
        self.assertNotEqual(git_result.returncode, 0, git_result.stdout)
        git_payload = json.loads(git_result.stdout)
        self.assertIn(
            (
                "trusted remote fetch URL does not match contract: "
                f"expected {[str(self.remote)]!r}, got {[str(alternate)]!r}"
            ),
            git_payload["errors"],
        )

        remote_result = self.run_project_script(
            REMOTE_VERIFIER,
            "--commit",
            head,
            "--remote",
            "origin",
            "--json",
        )
        self.assertNotEqual(
            remote_result.returncode,
            0,
            remote_result.stdout,
        )
        remote_payload = json.loads(remote_result.stdout)
        self.assertIn(
            "trusted_remote_fetch_url_mismatch",
            "\n".join(remote_payload["errors"]),
        )
        self.assertNotIn("remote_observation", remote_payload["facts"])

    def test_contract_branch_must_match_branch_and_upstream(self) -> None:
        self.run_git(self.root, "switch", "-c", "other")
        self.run_git(
            self.root,
            "push",
            "--set-upstream",
            "origin",
            "other",
        )
        head = self.git_text(self.root, "rev-parse", "HEAD")

        git_result = self.run_project_script(
            GIT_VERIFIER,
            "--require-origin",
            "--expected-commit",
            head,
            "--json",
        )
        self.assertNotEqual(git_result.returncode, 0, git_result.stdout)
        git_errors = json.loads(git_result.stdout)["errors"]
        self.assertIn(
            (
                "current branch does not match contract: "
                "expected 'main', got 'other'"
            ),
            git_errors,
        )
        self.assertIn(
            (
                "current upstream does not match contract: "
                "expected 'origin/main', got 'origin/other'"
            ),
            git_errors,
        )

        remote_result = self.run_project_script(
            REMOTE_VERIFIER,
            "--commit",
            head,
            "--branch",
            "other",
            "--json",
        )
        self.assertNotEqual(
            remote_result.returncode,
            0,
            remote_result.stdout,
        )
        remote_errors = json.loads(remote_result.stdout)["errors"]
        self.assertIn(
            "--branch must match contract trusted branch 'main': got 'other'",
            remote_errors,
        )
        self.assertIn(
            "current_branch_mismatch: expected 'main', got 'other'",
            remote_errors,
        )
        self.assertIn(
            (
                "current_upstream_mismatch: expected 'origin/main', "
                "got 'origin/other'"
            ),
            remote_errors,
        )

    def test_contract_project_prefix_must_match_actual_prefix(self) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        contract["change_control"]["trusted_git_remote"][
            "project_prefix"
        ] = "wrong/project/"
        self.write_json("governance/ACCEPTANCE_CONTRACT_V1.json", contract)
        head = self.commit_and_push("contract with wrong project prefix")

        git_result = self.run_project_script(
            GIT_VERIFIER,
            "--require-origin",
            "--expected-commit",
            head,
            "--json",
        )
        self.assertNotEqual(git_result.returncode, 0, git_result.stdout)
        self.assertIn(
            (
                "project prefix does not match contract: "
                f"expected 'wrong/project/', got {TEST_PROJECT_PREFIX!r}"
            ),
            json.loads(git_result.stdout)["errors"],
        )

        remote_result = self.run_project_script(
            REMOTE_VERIFIER,
            "--commit",
            head,
            "--json",
        )
        self.assertNotEqual(
            remote_result.returncode,
            0,
            remote_result.stdout,
        )
        self.assertIn(
            (
                "project_prefix_mismatch: expected 'wrong/project/', "
                f"got {TEST_PROJECT_PREFIX!r}"
            ),
            json.loads(remote_result.stdout)["errors"],
        )
        self.assertNotIn(
            "remote_observation",
            json.loads(remote_result.stdout)["facts"],
        )

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
            (
                "current upstream does not match contract: "
                "expected 'origin/main', got 'other/main'"
            ),
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
            "--remote must match contract trusted remote 'origin': got 'other'",
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
        self.assertIn(
            "direct trusted remote commit mismatch",
            local_only.stdout,
        )

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
