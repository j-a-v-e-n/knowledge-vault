from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

from scripts.verify_contract_supersession import load_contract, verify


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = PROJECT_ROOT / "governance" / "ACCEPTANCE_CONTRACT_V1.json"


class ContractSupersessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.old = load_contract(CONTRACT_PATH)

    def successor(self) -> dict[str, Any]:
        candidate = copy.deepcopy(self.old)
        candidate["schema_version"] = self.old["schema_version"] + 1
        candidate["contract_id"] = f"{self.old['contract_id']}-successor-fixture"
        return candidate

    def assert_rejected(
        self,
        mutation: Callable[[dict[str, Any]], None],
        expected: str,
    ) -> None:
        candidate = self.successor()
        mutation(candidate)
        errors = verify(self.old, candidate)
        self.assertTrue(
            any(expected in error for error in errors),
            errors,
        )

    def test_unchanged_normative_successor_passes(self) -> None:
        self.assertEqual([], verify(self.old, self.successor()))

    def test_removed_requirement_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["requirements"].pop(0),
            "removed requirement",
        )

    def test_lowered_severity_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["requirements"][0].__setitem__(
                "severity",
                "minor",
            ),
            "lowered requirement severity",
        )

    def test_changed_statement_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["requirements"][0].__setitem__(
                "statement",
                "weakened",
            ),
            "changed frozen requirement statement",
        )

    def test_removed_verification_binding_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["requirements"][0]["verification"].pop(),
            "weakened verification",
        )

    def test_removed_required_artifact_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["required_artifacts"].pop(),
            "weakened required_artifacts",
        )

    def test_scope_change_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["scope"].append("live execution"),
            "changed frozen normative field: scope",
        )

    def test_human_authority_change_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["authority"]["human_reserved"].clear(),
            "changed frozen normative field: authority",
        )

    def test_old_requirement_cannot_move_under_new_conditional(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["conditional_gates"].append(
                {
                    "id": "COND-FIXTURE-BYPASS",
                    "applies_to_requirements": [
                        self.old["requirements"][0]["id"]
                    ],
                }
            )

        self.assert_rejected(
            mutate,
            "applies to frozen requirements",
        )

    def test_changed_frozen_verification_entry_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["verification_catalog"][0].__setitem__(
                "description",
                "weakened",
            ),
            "changed frozen verification_catalog entry",
        )

    def test_removed_frozen_file_is_rejected(self) -> None:
        self.assert_rejected(
            lambda value: value["change_control"]["frozen_files"].pop(),
            "weakened change_control.frozen_files",
        )

    def test_duplicate_json_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(
                '{"schema_version":1,"schema_version":2}\n',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_contract(path)

    def test_nonfinite_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "nan.json"
            path.write_text('{"value":NaN}\n', encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError,
                "non-standard JSON constant",
            ):
                load_contract(path)

    def test_fixture_round_trip_is_strict_json(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "successor.json"
            path.write_text(
                json.dumps(self.successor(), ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self.assertEqual([], verify(self.old, load_contract(path)))


if __name__ == "__main__":
    unittest.main()
