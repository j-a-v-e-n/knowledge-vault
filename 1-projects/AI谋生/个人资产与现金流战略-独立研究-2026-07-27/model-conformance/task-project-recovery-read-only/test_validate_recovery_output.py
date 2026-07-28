from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_recovery_output import (
    EXIT_INVALID_CONTRACT,
    EXIT_QUALIFIED,
    EXIT_REFUSED,
    EXIT_STALE_INPUT,
    EXIT_WRONG_OUTPUT,
    load_json,
    validate_contract,
    validate_output,
)


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "task-class.json"


class RecoveryOutputContractTests(unittest.TestCase):
    def test_bound_contract_and_mechanical_gold_are_valid(self) -> None:
        manifest, result = validate_contract(MANIFEST)
        self.assertIsNotNone(manifest)
        self.assertEqual(result["classification"], "CONTRACT_VALID")
        self.assertEqual(manifest["claim_status"], "EXECUTABLE_EVAL_NOT_YET_MODEL_RUN")

    def test_normal_fixture_qualifies_only_candidate_output(self) -> None:
        code, result = validate_output(MANIFEST, ROOT / "fixtures/valid-output.json")
        self.assertEqual(code, EXIT_QUALIFIED)
        self.assertEqual(result["classification"], "EVAL_QUALIFIED_CANDIDATE_OUTPUT")
        self.assertIn("does not identify", result["note"])

    def test_refusal_is_explicit_nonqualification(self) -> None:
        code, result = validate_output(MANIFEST, ROOT / "fixtures/refusal-output.json")
        self.assertEqual(code, EXIT_REFUSED)
        self.assertEqual(result["classification"], "NOT_QUALIFIED_REFUSAL")

    def test_stale_manifest_fails_before_output_acceptance(self) -> None:
        code, result = validate_output(
            ROOT / "fixtures/stale-task-class.json",
            ROOT / "fixtures/valid-output.json",
        )
        self.assertEqual(code, EXIT_STALE_INPUT)
        self.assertEqual(result["classification"], "STALE_INPUT_BUNDLE")
        self.assertTrue(result["mismatches"])

    def test_schema_valid_but_wrong_projection_is_rejected(self) -> None:
        code, result = validate_output(MANIFEST, ROOT / "fixtures/wrong-output.json")
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "WRONG_STATE_PROJECTION")

    def test_extra_field_is_schema_invalid(self) -> None:
        output = load_json(ROOT / "fixtures/valid-output.json")
        output["self_approval"] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "extra-field.json"
            candidate.write_text(json.dumps(output), encoding="utf-8")
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "SCHEMA_INVALID")

    def test_manifest_cannot_upgrade_claim_status(self) -> None:
        manifest = load_json(MANIFEST)
        manifest["claim_status"] = "MODEL_QUALIFIED"
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "upgraded-manifest.json"
            candidate.write_text(json.dumps(manifest), encoding="utf-8")
            loaded, result = validate_contract(candidate)
        self.assertIsNone(loaded)
        self.assertEqual(result["classification"], "INVALID_CONTRACT")
        self.assertEqual(EXIT_INVALID_CONTRACT, 5)


if __name__ == "__main__":
    unittest.main()
