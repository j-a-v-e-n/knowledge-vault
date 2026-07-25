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


class ResearchEvidenceMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ("governance", "research", "audits", "scripts"):
            shutil.copytree(PROJECT_ROOT / directory, self.root / directory)
        for relative in (
            "PRODUCT_ASSURANCE_BLUEPRINT_V2.md",
            "PROJECT_CHARTER.md",
            "DECISIONS.md",
            "README.md",
            "STATUS.md",
        ):
            shutil.copy2(PROJECT_ROOT / relative, self.root / relative)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_verifier(self) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        return subprocess.run(
            ["python3", str(VERIFIER), "--allow-candidate"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def read_research(self) -> dict:
        return json.loads(
            (
                self.root
                / "governance"
                / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
            ).read_text(encoding="utf-8")
        )

    def write_research(self, value: dict) -> None:
        (
            self.root
            / "governance"
            / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
        ).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_replacing_review_report_breaks_content_binding(self) -> None:
        path = self.root / "audits" / "DESIGN_FREEZE_STRUCTURAL_REVIEW_2026-07-25.md"
        path.write_text("replacement report\n", encoding="utf-8")
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("design reviewer evidence sha256 mismatch", result.stdout)
        self.assertIn("research artifact sha256 mismatch", result.stdout)
        self.assertIn("challenge evidence sha256 mismatch", result.stdout)

    def test_blocked_markdown_cannot_be_relabelled_as_passing_review(self) -> None:
        research = self.read_research()
        final_round = research["challenge"]["rounds"][-1]
        final_round["result"] = "passed_freeze"
        final_round["new_architecture_changing_classes"] = []
        final_round["open_critical_count"] = 0
        final_round["open_major_count"] = 0
        self.write_research(research)
        result = self.run_verifier()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "passing review evidence must be machine-readable JSON", result.stdout
        )


if __name__ == "__main__":
    unittest.main()
