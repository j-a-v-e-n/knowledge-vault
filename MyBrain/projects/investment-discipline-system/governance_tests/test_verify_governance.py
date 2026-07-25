from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = PROJECT_ROOT / "scripts" / "verify_governance.py"


class GovernanceVerifierMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(PROJECT_ROOT / "governance", self.root / "governance")
        shutil.copytree(PROJECT_ROOT / "research", self.root / "research")
        for relative in (
            "PRODUCT_ASSURANCE_BLUEPRINT_V2.md",
            "PROJECT_CHARTER.md",
            "DECISIONS.md",
        ):
            shutil.copy2(PROJECT_ROOT / relative, self.root / relative)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_verifier(self, *, frozen: bool = False) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        command = ["python3", str(VERIFIER)]
        if not frozen:
            command.append("--allow-candidate")
        return subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
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

    def assert_rejected(self, needle: str) -> None:
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(needle, result.stdout)

    def test_unmodified_candidate_passes(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_duplicate_json_key_is_rejected(self) -> None:
        path = self.root / "governance" / "ACCEPTANCE_CONTRACT_V1.json"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                '"schema_version": 1,',
                '"schema_version": 1,\n  "schema_version": 1,',
                1,
            ),
            encoding="utf-8",
        )
        self.assert_rejected("duplicate object key")

    def test_changed_source_excerpt_is_rejected(self) -> None:
        source = self.read_json("governance/USER_SOURCE_EXCERPTS_V1.json")
        source["excerpts"][0]["excerpt"] += "被修改"
        self.write_json("governance/USER_SOURCE_EXCERPTS_V1.json", source)
        self.assert_rejected("excerpt_sha256 mismatch")

    def test_missing_user_value_source_is_rejected(self) -> None:
        source = self.read_json("governance/USER_SOURCE_EXCERPTS_V1.json")
        for excerpt in source["excerpts"]:
            excerpt["value_ids"] = [
                value for value in excerpt.get("value_ids", []) if value != "UV-12"
            ]
        self.write_json("governance/USER_SOURCE_EXCERPTS_V1.json", source)
        self.assert_rejected("user source excerpt coverage differs")

    def test_missing_verification_spec_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        specs["specs"].pop()
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("verification spec coverage differs")

    def test_wrong_reverse_requirement_binding_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        specs["specs"][0]["requirement_ids"] = []
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("reverse requirement binding differs")

    def test_reviewer_who_constructed_candidate_is_rejected(self) -> None:
        subjects = self.read_json("governance/ASSURANCE_SUBJECTS_V1.json")
        reviewer = next(
            item for item in subjects["subjects"] if item["role"] == "design_reviewer"
        )
        reviewer["participated_in_candidate_construction"] = True
        self.write_json("governance/ASSURANCE_SUBJECTS_V1.json", subjects)
        self.assert_rejected("design reviewer is not independent")

    def test_unknown_conditional_requirement_is_rejected(self) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        contract["conditional_gates"][0]["applies_to_requirements"].append(
            "REQ-NOT-REAL"
        )
        self.write_json("governance/ACCEPTANCE_CONTRACT_V1.json", contract)
        self.assert_rejected("references unknown requirements")

    def test_normative_file_removed_from_freeze_boundary_is_rejected(self) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        contract["change_control"]["frozen_files"].remove(
            "PRODUCT_ASSURANCE_BLUEPRINT_V2.md"
        )
        self.write_json("governance/ACCEPTANCE_CONTRACT_V1.json", contract)
        self.assert_rejected("normative frozen file boundary differs")

    def test_frozen_mode_rejects_open_research(self) -> None:
        result = self.run_verifier(frozen=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("research independent challenge is not completed", result.stdout)
        self.assertIn("research stop rule is not met", result.stdout)


if __name__ == "__main__":
    unittest.main()
