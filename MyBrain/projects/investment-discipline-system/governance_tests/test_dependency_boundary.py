from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_dependency_boundary import verify_dependency_boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "governance" / "DEPENDENCY_BOUNDARY_V1.json"


class DependencyBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in (
            "governance",
            "prototype",
            "scripts",
            "governance_tests",
            "research/evidence/r8/RS-04/probe",
            ".github/workflows",
        ):
            (self.root / relative).mkdir(parents=True)
        self.write("prototype/main.py", "import json\nfrom scripts.tool import VALUE\n")
        self.write("scripts/tool.py", "import argparse\nVALUE = 1\n")
        self.write("governance_tests/test_placeholder.py", "import unittest\n")
        self.write("research/evidence/r8/RS-04/probe/check.py", "import csv\n")
        self.write(
            ".github/workflows/assurance.yml",
            """name: fixture
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
      - run: python -m pip install --disable-pip-version-check ruff==0.15.17
""",
        )
        self.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, relative: str, text: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def write_manifest(self) -> None:
        self.write(
            "governance/DEPENDENCY_BOUNDARY_V1.json",
            json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
        )

    def report(self) -> dict:
        return verify_dependency_boundary(
            self.root,
            repository_root=self.root,
        )

    def assert_rejected(self, oracle_id: str) -> None:
        report = self.report()
        self.assertEqual("fail", report["status"], report)
        self.assertIn(
            oracle_id, {item["oracle_id"] for item in report["errors"]}, report
        )

    def test_benign_fixture_derives_empty_runtime_and_governance_sets(self) -> None:
        report = self.report()
        self.assertEqual("pass", report["status"], report)
        self.assertEqual([], report["observed"]["runtime_third_party_dependencies"])
        self.assertEqual([], report["observed"]["governance_third_party_dependencies"])
        self.assertEqual(["ruff"], report["observed"]["ci_tool_dependencies"])
        self.assertEqual(1, len(report["observed"]["external_actions"]))

    def test_current_repository_passes_and_runtime_observation_is_empty(self) -> None:
        report = verify_dependency_boundary(PROJECT_ROOT)
        self.assertEqual("pass", report["status"], report)
        self.assertEqual([], report["observed"]["runtime_third_party_dependencies"])
        self.assertEqual([], report["observed"]["governance_third_party_dependencies"])

    def test_direct_requests_import_is_rejected(self) -> None:
        self.write("prototype/http_client.py", "import requests as http\n")
        self.assert_rejected("DEP-RUNTIME-NON-STDLIB")
        self.assert_rejected("DEP-UNREGISTERED-DEPENDENCY")

    def test_importlib_alias_dynamic_requests_import_is_rejected(self) -> None:
        self.write(
            "scripts/plugin.py",
            "import importlib as loader\nplugin = loader.import_module('requests')\n",
        )
        self.assert_rejected("DEP-UNREGISTERED-DEPENDENCY")

    def test_from_importlib_alias_dynamic_import_is_rejected(self) -> None:
        self.write(
            "scripts/plugin.py",
            "from importlib import import_module as load\nplugin = load('requests')\n",
        )
        self.assert_rejected("DEP-UNREGISTERED-DEPENDENCY")

    def test_nonliteral_dynamic_import_is_rejected(self) -> None:
        self.write(
            "scripts/plugin.py",
            "import importlib\nname = 'json'\nplugin = importlib.import_module(name)\n",
        )
        self.assert_rejected("DEP-DYNAMIC-IMPORT-NONLITERAL")

    def test_floating_pip_in_aliased_subprocess_is_rejected(self) -> None:
        self.write(
            "scripts/installer.py",
            "import subprocess as process\n"
            "import sys\n"
            "process.run([sys.executable, '-m', 'pip', 'install', 'requests'], check=True)\n",
        )
        self.assert_rejected("DEP-FLOATING-INSTALL")

    def test_floating_pip_in_shell_command_is_rejected(self) -> None:
        self.write(
            "scripts/installer.py",
            "import os\nos.system('python -m pip install requests')\n",
        )
        self.assert_rejected("DEP-FLOATING-INSTALL")

    def test_unregistered_exact_install_is_rejected(self) -> None:
        self.write(
            "scripts/installer.py",
            "import subprocess\nsubprocess.run(['pip', 'install', 'requests==2.32.4'])\n",
        )
        self.assert_rejected("DEP-UNREGISTERED-DEPENDENCY")

    def test_unknown_telemetry_is_rejected(self) -> None:
        self.manifest["third_party_dependencies"][0]["permissions_or_telemetry"][
            "status"
        ] = "unknown"
        self.write_manifest()
        self.assert_rejected("DEP-TELEMETRY-UNKNOWN")

    def test_unpinned_external_action_is_rejected(self) -> None:
        self.write(
            ".github/workflows/assurance.yml",
            """name: fixture
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python -m pip install ruff==0.15.17
""",
        )
        self.assert_rejected("DEP-ACTION-UNPINNED")

    def test_missing_license_is_rejected(self) -> None:
        del self.manifest["third_party_dependencies"][0]["license"]
        self.write_manifest()
        self.assert_rejected("DEP-MANIFEST-SCHEMA")

    def test_missing_removal_plan_is_rejected(self) -> None:
        del self.manifest["third_party_dependencies"][0]["removal_plan"]
        self.write_manifest()
        self.assert_rejected("DEP-MANIFEST-SCHEMA")

    def test_missing_hash_is_rejected(self) -> None:
        del self.manifest["third_party_dependencies"][0]["sha256_or_lock_hash"]
        self.write_manifest()
        self.assert_rejected("DEP-MANIFEST-SCHEMA")

    def test_invalid_hash_value_is_rejected(self) -> None:
        self.manifest["third_party_dependencies"][0]["sha256_or_lock_hash"]["value"] = (
            "not-a-sha256"
        )
        self.write_manifest()
        self.assert_rejected("DEP-MANIFEST-HASH")

    def test_requirements_dependency_is_derived_and_must_be_registered(self) -> None:
        self.write("requirements.txt", "requests==2.32.4\n")
        self.assert_rejected("DEP-UNREGISTERED-DEPENDENCY")

    def test_floating_pyproject_dependency_is_rejected(self) -> None:
        self.write(
            "pyproject.toml",
            "[project]\nname = 'fixture'\nversion = '1.0.0'\ndependencies = ['requests>=2']\n",
        )
        self.assert_rejected("DEP-CONFIG-FLOATING")

    def test_new_undeclared_python_root_is_rejected(self) -> None:
        self.write("src/new_runtime.py", "import json\n")
        self.assert_rejected("DEP-UNDECLARED-PYTHON-ROOT")

    def test_duplicate_manifest_key_is_rejected(self) -> None:
        path = self.root / "governance" / "DEPENDENCY_BOUNDARY_V1.json"
        encoded = path.read_text(encoding="utf-8")
        encoded = encoded.replace(
            '"schema_version": 1,',
            '"schema_version": 1,\n  "schema_version": 1,',
            1,
        )
        path.write_text(encoded, encoding="utf-8")
        self.assert_rejected("DEP-MANIFEST-STRICT-JSON")


if __name__ == "__main__":
    unittest.main()
