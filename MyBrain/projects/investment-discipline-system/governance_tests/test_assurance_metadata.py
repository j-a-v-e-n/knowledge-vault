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
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_PREFIX = Path("MyBrain/projects/investment-discipline-system")
WORKFLOW_PATH = Path(".github/workflows/investment-discipline-assurance.yml")
TRUST_MODEL = Path("governance/ASSURANCE_TRUST_MODEL_V1.json")
GROUND_TRUTH = Path("governance/GROUND_TRUTH_MANIFEST_V1.json")
FAILURE_REGISTRY = Path("governance/FAILURE_CLASSES_V1.json")
DECISION_AUTHORITY = Path("governance/DECISION_AUTHORITY_V1.json")
RESEARCH_REGISTER = Path("governance/AI_PROJECT_RESEARCH_REGISTER_V1.json")
PRIVATE_DATA_POLICY = Path("governance/PRIVATE_DATA_POLICY_V1.json")
REMOTE_URL = "git@github.com:j-a-v-e-n/knowledge-vault.git"


def source_repository_root() -> Path:
    result = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
    )
    return Path(result.stdout.strip()).resolve(strict=True)


SOURCE_REPOSITORY_ROOT = source_repository_root()


class AssuranceMetadataMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_temp = tempfile.TemporaryDirectory()
        cls.fixture_repository = Path(cls.fixture_temp.name) / "fixture-repository"
        cls.fixture_project = cls.fixture_repository / PROJECT_PREFIX
        cls.fixture_project.parent.mkdir(parents=True)
        shutil.copytree(
            PROJECT_ROOT,
            cls.fixture_project,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        fixture_workflow = cls.fixture_repository / WORKFLOW_PATH
        fixture_workflow.parent.mkdir(parents=True)
        shutil.copy2(SOURCE_REPOSITORY_ROOT / WORKFLOW_PATH, fixture_workflow)
        subprocess.run(
            ["git", "init", "--quiet", str(cls.fixture_repository)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(cls.fixture_repository),
                "remote",
                "add",
                "origin",
                REMOTE_URL,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        cls.normalize_manifest_hashes(
            project=cls.fixture_project,
            repository=cls.fixture_repository,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture_temp.cleanup()

    @staticmethod
    def normalize_manifest_hashes(*, project: Path, repository: Path) -> None:
        manifest_path = project / GROUND_TRUTH
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for artifact in manifest["artifacts"]:
            base = repository if artifact.get("scope", "project") == "repository" else project
            artifact_path = base / artifact["path"]
            artifact["sha256"] = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repository = Path(self.temp.name) / "test-repository"
        shutil.copytree(self.fixture_repository, self.repository)
        self.project = self.repository / PROJECT_PREFIX
        self.verifier = self.project / "scripts" / "verify_assurance_metadata.py"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def read_document(self, relative: Path) -> dict[str, Any]:
        value = json.loads((self.project / relative).read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def write_document(self, relative: Path, value: dict[str, Any]) -> None:
        (self.project / relative).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def refresh_manifest_entries(self, *relative_paths: Path) -> None:
        manifest = self.read_document(GROUND_TRUTH)
        requested = {path.as_posix() for path in relative_paths}
        refreshed: set[str] = set()
        for artifact in manifest["artifacts"]:
            relative = artifact["path"]
            if relative not in requested:
                continue
            base = (
                self.repository
                if artifact.get("scope", "project") == "repository"
                else self.project
            )
            artifact["sha256"] = hashlib.sha256(
                (base / relative).read_bytes()
            ).hexdigest()
            refreshed.add(relative)
        self.assertEqual(refreshed, requested)
        self.write_document(GROUND_TRUTH, manifest)

    def run_verifier(
        self,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, str(self.verifier), "--json"],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=environment,
            timeout=30,
            check=False,
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"verifier did not emit JSON: {exc}: {result.stdout!r}")
        self.assertIsInstance(payload, dict)
        return result, payload

    def assert_rejected(self, expected_error: str) -> None:
        result, payload = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(payload.get("status"), "fail", payload)
        self.assertGreater(payload.get("error_count", 0), 0, payload)
        combined_errors = "\n".join(payload.get("errors", []))
        self.assertIn(expected_error, combined_errors, payload)

    def test_benign_copied_project_passes(self) -> None:
        result, payload = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            payload,
            {"error_count": 0, "errors": [], "status": "pass"},
        )

    def test_rejects_duplicate_json_key(self) -> None:
        trust_path = self.project / TRUST_MODEL
        trust = self.read_document(TRUST_MODEL)
        status_line = f'  "status": {json.dumps(trust["status"])},\n'
        original = trust_path.read_text(encoding="utf-8")
        self.assertEqual(original.count(status_line), 1)
        trust_path.write_text(
            original.replace(status_line, status_line + status_line, 1),
            encoding="utf-8",
        )
        self.assert_rejected("duplicate JSON key")

    def test_rejects_stale_artifact_hash(self) -> None:
        artifact = self.project / PRIVATE_DATA_POLICY
        artifact.write_bytes(artifact.read_bytes() + b"\n")
        self.assert_rejected(
            "stale artifact hash for governance/PRIVATE_DATA_POLICY_V1.json"
        )

    def test_rejects_missing_research_primary_artifact(self) -> None:
        research = self.read_document(RESEARCH_REGISTER)
        missing_path = research["primary_artifacts"][0]["path"]
        manifest = self.read_document(GROUND_TRUTH)
        manifest["artifacts"] = [
            artifact
            for artifact in manifest["artifacts"]
            if artifact["path"] != missing_path
        ]
        self.write_document(GROUND_TRUTH, manifest)
        self.assert_rejected(f"missing research primary artifact {missing_path}")

    def test_rejects_unknown_failure_reference(self) -> None:
        registry = self.read_document(FAILURE_REGISTRY)
        registry["failure_classes"][0]["requirement_ids"].append("REQ-UNKNOWN")
        self.write_document(FAILURE_REGISTRY, registry)
        self.refresh_manifest_entries(FAILURE_REGISTRY)
        self.assert_rejected("unknown requirement_ids references ['REQ-UNKNOWN']")

    def test_rejects_forged_human_excerpt_with_self_consistent_hash(self) -> None:
        authority = self.read_document(DECISION_AUTHORITY)
        decision = next(
            item for item in authority["decisions"] if item["id"] == "DA-001"
        )
        source = decision["sources"][0]
        source["excerpt"] = "forged human confirmation"
        source["excerpt_sha256"] = hashlib.sha256(
            source["excerpt"].encode("utf-8")
        ).hexdigest()
        self.write_document(DECISION_AUTHORITY, authority)
        self.refresh_manifest_entries(DECISION_AUTHORITY)
        self.assert_rejected("excerpt does not equal the current source line range")

    def test_rejects_trust_workflow_hash_mutation(self) -> None:
        trust = self.read_document(TRUST_MODEL)
        machine = trust["trust_roots"]["github_actions_machine_execution"]
        machine["workflow_sha256"] = "0" * 64
        self.write_document(TRUST_MODEL, trust)
        self.refresh_manifest_entries(TRUST_MODEL)
        self.assert_rejected("workflow hash is stale")

    def test_rejects_forged_broader_workflow_permissions(self) -> None:
        workflow = self.repository / WORKFLOW_PATH
        workflow_text = workflow.read_text(encoding="utf-8")
        self.assertEqual(workflow_text.count("  contents: read\n"), 1)
        workflow.write_text(
            workflow_text.replace("  contents: read\n", "  contents: write\n", 1),
            encoding="utf-8",
        )
        trust = self.read_document(TRUST_MODEL)
        machine = trust["trust_roots"]["github_actions_machine_execution"]
        machine["workflow_sha256"] = hashlib.sha256(workflow.read_bytes()).hexdigest()
        machine["required_permissions"]["contents"] = "write"
        self.write_document(TRUST_MODEL, trust)
        self.refresh_manifest_entries(TRUST_MODEL, WORKFLOW_PATH)
        self.assert_rejected("permissions differ from the least-privilege contract")


if __name__ == "__main__":
    unittest.main()
