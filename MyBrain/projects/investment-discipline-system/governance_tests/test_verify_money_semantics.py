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


class MoneyGovernanceMutationTests(unittest.TestCase):
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

    def read_money(self) -> dict:
        return json.loads(
            (
                self.root
                / "governance"
                / "MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
            ).read_text(encoding="utf-8")
        )

    def write_money(self, value: dict) -> None:
        (
            self.root
            / "governance"
            / "MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json"
        ).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def assert_rejected(self, needle: str) -> None:
        env = os.environ.copy()
        env["IDS_PROJECT_ROOT"] = str(self.root)
        result = subprocess.run(
            ["python3", str(VERIFIER), "--allow-candidate"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(needle, result.stdout)

    def test_forward_or_unknown_symbol_is_rejected(self) -> None:
        money = self.read_money()
        booking = next(
            item for item in money["booking_rules"] if item["id"] == "MONEY-BOOK-BUY"
        )
        booking["calculation_steps"][0]["args"] = ["cash_after"]
        self.write_money(money)
        self.assert_rejected("references unknown expression symbol: 'cash_after'")

    def test_wrong_operator_arity_is_rejected(self) -> None:
        money = self.read_money()
        booking = next(
            item for item in money["booking_rules"] if item["id"] == "MONEY-BOOK-SELL"
        )
        negate = booking["calculation_steps"][1]["args"][0]["args"][2]
        negate["args"].append("cash_before")
        self.write_money(money)
        self.assert_rejected("operator negate requires arity 1, got 2")

    def test_free_text_predicate_is_rejected(self) -> None:
        money = self.read_money()
        booking = next(
            item for item in money["booking_rules"] if item["id"] == "MONEY-NAV"
        )
        invariant = next(
            item
            for item in booking["invariants"]
            if item["id"] == "INV-NAV-NO-SILENT-ZERO"
        )
        invariant.pop("predicate_id")
        invariant["predicate"] = "looks_safe"
        self.write_money(money)
        self.assert_rejected("INV-NAV-NO-SILENT-ZERO predicate binding differs")


if __name__ == "__main__":
    unittest.main()
