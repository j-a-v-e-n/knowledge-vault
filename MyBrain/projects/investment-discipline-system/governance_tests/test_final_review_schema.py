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
WORKFLOW_RELATIVE = ".github/workflows/investment-discipline-assurance.yml"
GROUND_TRUTH_RELATIVE = "governance/GROUND_TRUTH_MANIFEST_V1.json"
CONTRACT_RELATIVE = "governance/ACCEPTANCE_CONTRACT_V1.json"
TARGETS_RELATIVE = "governance/IMPLEMENTATION_TARGETS_V1.json"
EVIDENCE_RELATIVE = "audits/FINAL_REVIEW_SCHEMA_V2_FIXTURE.json"
REVIEW_OUTPUT_RELATIVE = "audits/final_review_fixture/review-output.md"
MACHINE_MANIFEST_RELATIVE = (
    "evidence/ci/final-review-schema-machine-manifest.json"
)
ATTESTATION_RELATIVE = (
    "evidence/ci/final-review-schema-attestation-verification.json"
)
POSTDATED_SPEC_RELATIVE = (
    "audits/final_review_probes/PROBE-SCHEMA-V2-POSTDATED.json"
)
PREDATED_SPEC_RELATIVE = (
    "audits/final_review_probes/PROBE-SCHEMA-V2-PREDATED.json"
)
POSTDATED_RECEIPT_RELATIVE = (
    "audits/final_review_attacks/novelty-postdated.json"
)
PREDATED_RECEIPT_RELATIVE = (
    "audits/final_review_attacks/novelty-predated.json"
)
SUBJECT_ID = "SUBJECT-DESIGN-REVIEW-SCHEMA-V2-FIXTURE"
ROUND_ID = "CHALLENGE-FINAL-SCHEMA-V2-FIXTURE"
EXPECTED_ORIGIN = "git@github.com:j-a-v-e-n/knowledge-vault.git"
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


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_verifier(project_root: Path) -> ModuleType:
    verifier_path = project_root / "scripts" / "verify_governance.py"
    module_name = f"_final_review_fixture_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, verifier_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load verifier: {verifier_path}")
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


class FinalReviewSchemaV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.class_temp = tempfile.TemporaryDirectory()
        try:
            cls.build_replayable_fixture(Path(cls.class_temp.name))
        except Exception:
            cls.class_temp.cleanup()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.class_temp.cleanup()
        super().tearDownClass()

    @classmethod
    def checked_run(
        cls,
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(
                f"{' '.join(argv)} failed ({completed.returncode}):\n"
                f"{completed.stdout}"
            )
        return completed

    @classmethod
    def git_text(cls, cwd: Path, *args: str) -> str:
        return cls.checked_run(["git", *args], cwd=cwd).stdout.strip()

    @classmethod
    def fixture_env(cls, project_root: Path) -> dict[str, str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(project_root)
        return env

    @classmethod
    def novelty_spec(
        cls,
        *,
        project_root: Path,
        probe_id: str,
    ) -> dict[str, Any]:
        private_policy = read_json(
            project_root / "governance" / "PRIVATE_DATA_POLICY_V1.json"
        )
        current_mode = private_policy["runtime_storage"]["file_mode"]
        return {
            "schema_version": 1,
            "probe_id": probe_id,
            "target_path": "governance/PRIVATE_DATA_POLICY_V1.json",
            "json_pointer": "/runtime_storage/file_mode",
            "operation": "replace",
            "expected_before_sha256": digest_value(current_mode),
            "replacement": "0644",
            "expected_rejection_substring": (
                "private runtime storage boundary differs"
            ),
            "rationale": (
                "A permissive private-state file mode must remain blocked by "
                "the frozen privacy boundary."
            ),
        }

    @classmethod
    def build_replayable_fixture(cls, temp_root: Path) -> None:
        source_repository = Path(
            cls.git_text(PROJECT_ROOT, "rev-parse", "--show-toplevel")
        ).resolve()
        cls.project_prefix = (
            PROJECT_ROOT.relative_to(source_repository).as_posix() + "/"
        )
        cls.base_repository = temp_root / "base-repository"
        cls.base_root = cls.base_repository / cls.project_prefix
        shutil.copytree(
            PROJECT_ROOT,
            cls.base_root,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                "*.pyc",
                ".ruff_cache",
            ),
        )
        source_workflow = source_repository / WORKFLOW_RELATIVE
        copied_workflow = cls.base_repository / WORKFLOW_RELATIVE
        copied_workflow.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_workflow, copied_workflow)

        cls.checked_run(
            ["git", "init", "--initial-branch=main"],
            cwd=cls.base_repository,
        )
        cls.checked_run(
            ["git", "config", "user.name", "Final Review Schema Test"],
            cwd=cls.base_repository,
        )
        cls.checked_run(
            [
                "git",
                "config",
                "user.email",
                "final-review-schema@example.invalid",
            ],
            cwd=cls.base_repository,
        )
        cls.checked_run(
            ["git", "remote", "add", "origin", EXPECTED_ORIGIN],
            cwd=cls.base_repository,
        )

        write_json(
            cls.base_root / PREDATED_SPEC_RELATIVE,
            cls.novelty_spec(
                project_root=cls.base_root,
                probe_id="PROBE-SCHEMA-V2-PREDATED",
            ),
        )
        cls.checked_run(
            [
                sys.executable,
                str(
                    cls.base_root
                    / "scripts"
                    / "refresh_ground_truth_manifest.py"
                ),
            ],
            cwd=cls.base_root,
        )
        cls.checked_run(["git", "add", "."], cwd=cls.base_repository)
        cls.checked_run(
            ["git", "commit", "-m", "schema v2 candidate fixture"],
            cwd=cls.base_repository,
        )
        cls.candidate_commit = cls.git_text(
            cls.base_repository, "rev-parse", "HEAD"
        )
        cls.candidate_tree = cls.git_text(
            cls.base_repository,
            "rev-parse",
            f"{cls.candidate_commit}^{{tree}}",
        )

        baseline = cls.checked_run(
            [
                sys.executable,
                str(cls.base_root / "scripts" / "verify_governance.py"),
                "--allow-candidate",
            ],
            cwd=cls.base_root,
            env=cls.fixture_env(cls.base_root),
        )
        if "governance verification: PASS (candidate)" not in baseline.stdout:
            raise AssertionError(
                "candidate baseline did not report the expected pass:\n"
                f"{baseline.stdout}"
            )

        write_json(
            cls.base_root / POSTDATED_SPEC_RELATIVE,
            cls.novelty_spec(
                project_root=cls.base_root,
                probe_id="PROBE-SCHEMA-V2-POSTDATED",
            ),
        )
        verifier = load_verifier(cls.base_root)
        reviewed_files = cls.collect_reviewed_files(verifier)

        canonical_attacks: list[dict[str, str]] = []
        canonical_receipts: list[dict[str, Any]] = []
        for index, attack_id in enumerate(ATTACK_IDS, 1):
            receipt_relative = (
                "audits/final_review_attacks/"
                f"canonical-{index:02d}-{attack_id.lower()}.json"
            )
            receipt = cls.run_attack(
                extra_args=["--attack-id", attack_id],
                receipt_relative=receipt_relative,
            )
            canonical_receipts.append(receipt)
            canonical_attacks.append(
                {
                    "attack_id": attack_id,
                    "runner_receipt_path": receipt_relative,
                    "runner_receipt_sha256": sha256_file(
                        cls.base_root / receipt_relative
                    ),
                }
            )

        postdated_receipt = cls.run_attack(
            extra_args=[
                "--novelty-spec",
                str(cls.base_root / POSTDATED_SPEC_RELATIVE),
            ],
            receipt_relative=POSTDATED_RECEIPT_RELATIVE,
        )
        cls.run_attack(
            extra_args=[
                "--novelty-spec",
                str(cls.base_root / PREDATED_SPEC_RELATIVE),
            ],
            receipt_relative=PREDATED_RECEIPT_RELATIVE,
        )

        review_output = (
            "# Schema V2 fixture review output\n\n"
            f"Candidate commit: {cls.candidate_commit}\n\n"
            f"Candidate tree: {cls.candidate_tree}\n\n"
            "Every canonical attack and the post-candidate novelty probe was "
            "executed by the frozen production runner and rejected.\n"
        )
        review_output_path = cls.base_root / REVIEW_OUTPUT_RELATIVE
        review_output_path.parent.mkdir(parents=True, exist_ok=True)
        review_output_path.write_text(review_output, encoding="utf-8")

        machine_manifest = {
            "schema_version": 1,
            "manifest_id": "ids-github-machine-assurance-v1",
            "status": "pass",
            "assurance_level": "github_issued_workflow_provenance",
            "semantic_approval": False,
            "repository": "j-a-v-e-n/knowledge-vault",
            "candidate_commit": cls.candidate_commit,
            "candidate_tree": cls.candidate_tree,
            "project_prefix": cls.project_prefix,
            "fixture_scope": "isolated_schema_v2_test",
            "required_check_ids": [
                "CHECK-CANONICAL-ATTACK-REPLAY",
                "CHECK-CANDIDATE-GOVERNANCE",
            ],
            "checks": [
                {
                    "check_id": "CHECK-CANDIDATE-GOVERNANCE",
                    "result": "pass",
                    "stdout_sha256": hashlib.sha256(
                        baseline.stdout.encode("utf-8")
                    ).hexdigest(),
                },
                {
                    "check_id": "CHECK-CANONICAL-ATTACK-REPLAY",
                    "result": "pass",
                    "execution_fingerprints": [
                        receipt["execution_fingerprint"]
                        for receipt in canonical_receipts
                    ],
                },
            ],
            "limitations": [
                "This file is a local schema fixture, not a GitHub-issued attestation.",
                "The production verifier separately requires external provenance.",
            ],
        }
        write_json(
            cls.base_root / MACHINE_MANIFEST_RELATIVE,
            machine_manifest,
        )
        machine_manifest_hash = sha256_file(
            cls.base_root / MACHINE_MANIFEST_RELATIVE
        )
        attestation_verification = {
            "schema_version": 1,
            "verification_id": (
                "ids-github-attestation-verification-fixture-v1"
            ),
            "status": "pass",
            "fixture_only": True,
            "repository": "j-a-v-e-n/knowledge-vault",
            "workflow_path": WORKFLOW_RELATIVE,
            "candidate_commit": cls.candidate_commit,
            "subject": {
                "path": MACHINE_MANIFEST_RELATIVE,
                "sha256": machine_manifest_hash,
            },
            "policy_checks": {
                "repository_matches": True,
                "workflow_matches": True,
                "source_commit_matches": True,
                "hosted_runner_required": True,
            },
            "limitations": [
                "No external GitHub signature is asserted by this unit fixture."
            ],
        }
        write_json(
            cls.base_root / ATTESTATION_RELATIVE,
            attestation_verification,
        )

        review_input = (
            "Review the exact candidate against the complete ground-truth "
            "manifest. Replay every canonical attack and design at least one "
            "candidate-postdated novelty probe. Pass only with no open finding."
        )
        commands_run = [
            (
                "PYTHON scripts/run_design_freeze_attack.py "
                f"--candidate-commit {cls.candidate_commit} "
                f"--attack-id {attack_id}"
            )
            for attack_id in ATTACK_IDS
        ]
        commands_run.append(
            (
                "PYTHON scripts/run_design_freeze_attack.py "
                f"--candidate-commit {cls.candidate_commit} "
                f"--novelty-spec {POSTDATED_SPEC_RELATIVE}"
            )
        )
        evidence = {
            "schema_version": 2,
            "subject_id": SUBJECT_ID,
            "review_locator": "fixture:platform-observable-separate-thread",
            "assurance_level": (
                "platform_observable_separate_thread_review"
            ),
            "review_input": review_input,
            "review_input_sha256": hashlib.sha256(
                review_input.encode("utf-8")
            ).hexdigest(),
            "review_output_path": REVIEW_OUTPUT_RELATIVE,
            "review_output_sha256": sha256_file(review_output_path),
            "candidate_commit": cls.candidate_commit,
            "candidate_tree": cls.candidate_tree,
            "ground_truth_manifest_path": GROUND_TRUTH_RELATIVE,
            "ground_truth_manifest_sha256": sha256_file(
                cls.base_root / GROUND_TRUTH_RELATIVE
            ),
            "machine_assurance_manifest_path": MACHINE_MANIFEST_RELATIVE,
            "machine_assurance_manifest_sha256": machine_manifest_hash,
            "machine_attestation_verification_path": ATTESTATION_RELATIVE,
            "machine_attestation_verification_sha256": sha256_file(
                cls.base_root / ATTESTATION_RELATIVE
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
                    "probe_id": "PROBE-SCHEMA-V2-POSTDATED",
                    "spec_path": POSTDATED_SPEC_RELATIVE,
                    "spec_sha256": sha256_file(
                        cls.base_root / POSTDATED_SPEC_RELATIVE
                    ),
                    "runner_receipt_path": POSTDATED_RECEIPT_RELATIVE,
                    "runner_receipt_sha256": sha256_file(
                        cls.base_root / POSTDATED_RECEIPT_RELATIVE
                    ),
                }
            ],
            "findings": [],
            "finding_ids": [],
            "what_would_falsify_pass": [
                "A production-runner replay escapes or produces a different fingerprint."
            ],
            "limitations": [
                "The isolated fixture proves schema behavior, not external identity."
            ],
        }
        if (
            postdated_receipt.get("probe_id")
            != evidence["novelty_probes"][0]["probe_id"]
        ):
            raise AssertionError("postdated novelty receipt binding differs")
        write_json(cls.base_root / EVIDENCE_RELATIVE, evidence)

        postdated_candidate_path = (
            f"{cls.candidate_commit}:{cls.project_prefix}"
            f"{POSTDATED_SPEC_RELATIVE}"
        )
        postdated_probe = subprocess.run(
            ["git", "cat-file", "-e", postdated_candidate_path],
            cwd=cls.base_repository,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if postdated_probe.returncode == 0:
            raise AssertionError(
                "postdated novelty spec unexpectedly exists in the candidate"
            )
        predating_candidate_path = (
            f"{cls.candidate_commit}:{cls.project_prefix}"
            f"{PREDATED_SPEC_RELATIVE}"
        )
        cls.checked_run(
            ["git", "cat-file", "-e", predating_candidate_path],
            cwd=cls.base_repository,
        )

        cls.checked_run(["git", "add", "."], cwd=cls.base_repository)
        cls.checked_run(
            ["git", "commit", "-m", "schema v2 review fixture"],
            cwd=cls.base_repository,
        )

    @classmethod
    def run_attack(
        cls,
        *,
        extra_args: list[str],
        receipt_relative: str,
    ) -> dict[str, Any]:
        completed = cls.checked_run(
            [
                sys.executable,
                str(
                    cls.base_root
                    / "scripts"
                    / "run_design_freeze_attack.py"
                ),
                "--candidate-commit",
                cls.candidate_commit,
                *extra_args,
            ],
            cwd=cls.base_root,
            env=cls.fixture_env(cls.base_root),
        )
        try:
            receipt = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                f"attack runner did not emit JSON:\n{completed.stdout}"
            ) from exc
        if (
            not isinstance(receipt, dict)
            or receipt.get("candidate_commit") != cls.candidate_commit
            or receipt.get("candidate_tree") != cls.candidate_tree
            or receipt.get("result") != "rejected"
            or receipt.get("runner_exit_code") != completed.returncode
            or receipt.get("baseline", {}).get("exit_code") != 0
            or receipt.get("target", {}).get("exit_code") == 0
        ):
            raise AssertionError(
                "attack runner did not produce a rejected actual-execution "
                f"receipt:\n{completed.stdout}"
            )
        receipt_path = cls.base_root / receipt_relative
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(completed.stdout, encoding="utf-8")
        return receipt

    @classmethod
    def collect_reviewed_files(cls, verifier: ModuleType) -> list[str]:
        required = set(verifier.FINAL_REVIEW_REQUIRED_SCOPE)
        ground_truth = read_json(cls.base_root / GROUND_TRUTH_RELATIVE)
        for artifact in ground_truth["artifacts"]:
            if artifact.get("required") is not True:
                continue
            relative = artifact["path"]
            if artifact.get("scope", "project") == "repository":
                required.add(f"{verifier.REPOSITORY_SCOPE_PREFIX}{relative}")
            else:
                required.add(relative)

        contract = read_json(cls.base_root / CONTRACT_RELATIVE)
        required.update(contract["change_control"]["frozen_files"])
        targets = read_json(cls.base_root / TARGETS_RELATIVE)
        for target in targets["targets"]:
            if target.get("required_by") != "design_freeze":
                continue
            relative = target["path"]
            if target["kind"] == "file":
                required.add(relative)
                continue
            listing = cls.git_text(
                cls.base_repository,
                "ls-tree",
                "-r",
                "--full-tree",
                "--name-only",
                cls.candidate_commit,
                "--",
                (
                    f":(top,literal){cls.project_prefix}"
                    f"{relative}"
                ),
            )
            required.update(
                item.removeprefix(cls.project_prefix)
                for item in listing.splitlines()
                if item.startswith(cls.project_prefix)
            )
        return sorted(required)

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name) / "repository"
        self.checked_run(
            [
                "git",
                "clone",
                "--quiet",
                str(self.base_repository),
                str(self.repository),
            ],
            cwd=Path(self.temp.name),
        )
        self.checked_run(
            ["git", "remote", "set-url", "origin", EXPECTED_ORIGIN],
            cwd=self.repository,
        )
        self.root = self.repository / self.project_prefix
        self.verifier = load_verifier(self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evidence(self) -> dict[str, Any]:
        return read_json(self.root / EVIDENCE_RELATIVE)

    def verify_errors(
        self,
        evidence: dict[str, Any] | None = None,
    ) -> list[str]:
        contract = read_json(self.root / CONTRACT_RELATIVE)
        targets = read_json(self.root / TARGETS_RELATIVE)
        errors: list[str] = []
        previous_root = os.environ.get("IDS_PROJECT_ROOT")
        os.environ["IDS_PROJECT_ROOT"] = str(self.root)
        try:
            self.verifier.verify_final_review_evidence(
                evidence if evidence is not None else self.evidence(),
                round_id=ROUND_ID,
                reviewers=[SUBJECT_ID],
                candidate_commit=self.candidate_commit,
                candidate_tree=self.candidate_tree,
                frozen_files=contract["change_control"]["frozen_files"],
                implementation_targets=targets,
                errors=errors,
            )
        finally:
            if previous_root is None:
                os.environ.pop("IDS_PROJECT_ROOT", None)
            else:
                os.environ["IDS_PROJECT_ROOT"] = previous_root
        return errors

    def assert_rejected(
        self,
        evidence: dict[str, Any],
        *expected_errors: str,
    ) -> None:
        errors = self.verify_errors(evidence)
        self.assertTrue(errors, "mutated evidence unexpectedly passed")
        rendered = "\n".join(errors)
        for expected in expected_errors:
            self.assertIn(expected, rendered)

    def rewrite_receipt(
        self,
        evidence: dict[str, Any],
        *,
        attack_index: int,
        mutation,
    ) -> None:
        binding = evidence["canonical_attacks"][attack_index]
        receipt_path = self.root / binding["runner_receipt_path"]
        receipt = read_json(receipt_path)
        mutation(receipt)
        payload = {
            key: receipt.get(key)
            for key in FINGERPRINT_FIELDS
        }
        receipt["execution_fingerprint"] = hashlib.sha256(
            canonical_json(payload)
        ).hexdigest()
        write_json(receipt_path, receipt)
        binding["runner_receipt_sha256"] = sha256_file(receipt_path)

    def test_complete_schema_v2_review_fixture_passes(self) -> None:
        self.assertEqual(self.verify_errors(), [])

    def test_cross_candidate_runner_receipt_is_rejected(self) -> None:
        evidence = self.evidence()
        self.rewrite_receipt(
            evidence,
            attack_index=0,
            mutation=lambda receipt: receipt.update(
                {"candidate_commit": "0" * 40}
            ),
        )
        self.assert_rejected(
            evidence,
            "canonical_attacks[0] runner receipt candidate_commit differs",
            "canonical_attacks[0] actual runner replay differs",
        )

    def test_cross_candidate_machine_manifest_is_rejected(self) -> None:
        evidence = self.evidence()
        manifest_path = self.root / MACHINE_MANIFEST_RELATIVE
        manifest = read_json(manifest_path)
        manifest["candidate_commit"] = "0" * 40
        write_json(manifest_path, manifest)
        evidence["machine_assurance_manifest_sha256"] = sha256_file(
            manifest_path
        )
        self.assert_rejected(
            evidence,
            "machine-assurance manifest candidate_commit differs",
        )

    def test_escaped_attack_receipt_is_rejected(self) -> None:
        evidence = self.evidence()

        def escape(receipt: dict[str, Any]) -> None:
            receipt["target"]["exit_code"] = 0
            receipt["result"] = "escaped_or_wrong_failure"
            receipt["runner_exit_code"] = 1

        self.rewrite_receipt(
            evidence,
            attack_index=0,
            mutation=escape,
        )
        self.assert_rejected(
            evidence,
            "canonical_attacks[0] runner receipt result differs",
            "canonical_attacks[0] target actual execution binding differs",
            "canonical_attacks[0] actual runner replay differs",
        )

    def test_post_receipt_novelty_mutation_is_rejected(self) -> None:
        evidence = self.evidence()
        spec_path = self.root / POSTDATED_SPEC_RELATIVE
        spec = read_json(spec_path)
        spec["replacement"] = "0640"
        write_json(spec_path, spec)
        evidence["novelty_probes"][0]["spec_sha256"] = sha256_file(spec_path)
        self.assert_rejected(
            evidence,
            "novelty_probes[0] receipt/spec semantic hash differs",
            "novelty_probes[0] actual runner replay differs",
        )

    def test_raw_runner_receipt_hash_tamper_is_rejected(self) -> None:
        evidence = self.evidence()
        evidence["canonical_attacks"][0]["runner_receipt_sha256"] = "0" * 64
        self.assert_rejected(
            evidence,
            "canonical_attacks[0] runner receipt sha256 mismatch",
        )

    def test_missing_novelty_probe_is_rejected(self) -> None:
        evidence = self.evidence()
        evidence["novelty_probes"] = []
        self.assert_rejected(
            evidence,
            "passing review requires at least one novelty probe",
        )

    def test_candidate_predated_novelty_probe_is_rejected(self) -> None:
        evidence = self.evidence()
        evidence["novelty_probes"] = [
            {
                "probe_id": "PROBE-SCHEMA-V2-PREDATED",
                "spec_path": PREDATED_SPEC_RELATIVE,
                "spec_sha256": sha256_file(
                    self.root / PREDATED_SPEC_RELATIVE
                ),
                "runner_receipt_path": PREDATED_RECEIPT_RELATIVE,
                "runner_receipt_sha256": sha256_file(
                    self.root / PREDATED_RECEIPT_RELATIVE
                ),
            }
        ]
        self.assert_rejected(
            evidence,
            "novelty_probes[0] novelty spec existed in the reviewed candidate",
        )

    def test_wrong_assurance_level_is_rejected(self) -> None:
        evidence = self.evidence()
        evidence["assurance_level"] = "content_snapshot_anchor"
        self.assert_rejected(
            evidence,
            "passing review evidence assurance_level differs",
        )

    def test_bound_artifact_hash_tampering_is_rejected(self) -> None:
        evidence = self.evidence()
        evidence["review_input_sha256"] = "0" * 64
        evidence["review_output_sha256"] = "0" * 64
        evidence["ground_truth_manifest_sha256"] = "0" * 64
        evidence["machine_attestation_verification_sha256"] = "0" * 64
        self.assert_rejected(
            evidence,
            "passing review provenance is incomplete",
            "review output sha256 mismatch",
            "ground-truth manifest sha256 mismatch",
            "machine-attestation verification sha256 mismatch",
        )


if __name__ == "__main__":
    unittest.main()
