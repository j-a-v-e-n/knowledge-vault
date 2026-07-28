#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True

from verify_run2_acceptance import (  # noqa: E402
    AcceptanceError,
    DEFAULT_RECEIPT,
    EXPECTED_CROSSWALK_COUNTS,
    ORIGINAL_REVIEW_ROOT,
    ROOT,
    validate_acceptance,
)
from verify_run2_crosswalk import CrosswalkError  # noqa: E402


class Run2AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical = json.loads(DEFAULT_RECEIPT.read_text(encoding="utf-8"))

    def write_receipt(self, directory: Path, document: dict, *, canonical: bool = True) -> Path:
        path = directory / "receipt.json"
        if canonical:
            text = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
        else:
            text = json.dumps(document, ensure_ascii=False) + "\n"
        path.write_text(text, encoding="utf-8")
        return path

    def changed(self) -> dict:
        return json.loads(json.dumps(self.canonical, ensure_ascii=False))

    def test_canonical_exact_acceptance_passes(self) -> None:
        result = validate_acceptance(DEFAULT_RECEIPT)
        self.assertTrue(result["valid"])
        self.assertEqual(result["accepted_status"], "SATURATED-WITHIN-PROTOCOL")
        self.assertFalse(result["candidate_closure_authority"])
        self.assertFalse(result["implementation_authority"])
        self.assertFalse(result["shadow_operation_authority"])
        self.assertFalse(result["external_action_authority"])
        self.assertEqual(
            result["reviewed_original_root"], str(ORIGINAL_REVIEW_ROOT.resolve())
        )
        self.assertEqual(result["relocated_snapshot_root"], str(ROOT.resolve()))
        self.assertTrue(result["relocated_snapshot_exact_bytes"])
        self.assertFalse(result["review_scope_rewritten_for_successor"])

    def test_decision_tamper_fails(self) -> None:
        document = self.changed()
        document["decision"] = "REJECT"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "decision"):
                validate_acceptance(path)

    def test_accepted_status_tamper_fails(self) -> None:
        document = self.changed()
        document["accepted_status"] = "OPEN-WORLD-SATURATED"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "accepted_status"):
                validate_acceptance(path)

    def test_nonempty_major_fails(self) -> None:
        document = self.changed()
        document["unresolved_major"] = ["unresolved"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "unresolved_major"):
                validate_acceptance(path)

    def test_each_authority_escalation_fails(self) -> None:
        for key in (
            "external_action_authority",
            "candidate_closure_authority",
            "implementation_authority",
            "shadow_operation_authority",
        ):
            with self.subTest(key=key):
                document = self.changed()
                document[key] = True
                with tempfile.TemporaryDirectory() as temporary:
                    path = self.write_receipt(Path(temporary), document)
                    with self.assertRaisesRegex(AcceptanceError, key):
                        validate_acceptance(path)

    def test_final_status_binding_tamper_fails(self) -> None:
        document = self.changed()
        document["final_status"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "independently accepted hash"):
                validate_acceptance(path)

    def test_reviewed_path_tamper_fails(self) -> None:
        document = self.changed()
        document["protocol"]["path"] += ".other"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "exact reviewed path mismatch"):
                validate_acceptance(path)

    def test_successor_path_cannot_impersonate_original_reviewed_path(self) -> None:
        document = self.changed()
        document["protocol"]["path"] = str(
            (ROOT / "SEARCH_SATURATION_PROTOCOL.md").resolve()
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "exact reviewed path mismatch"):
                validate_acceptance(path)

    def test_independence_disclosure_tamper_fails(self) -> None:
        document = self.changed()
        document["independence_assertion"] = "blind"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "independence_assertion"):
                validate_acceptance(path)

    def test_residual_limit_removal_fails(self) -> None:
        document = self.changed()
        document["residual_limits"] = document["residual_limits"][:-1]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), document)
            with self.assertRaisesRegex(AcceptanceError, "residual_limits"):
                validate_acceptance(path)

    def test_missing_or_extra_key_fails(self) -> None:
        for mutation in ("missing", "extra"):
            with self.subTest(mutation=mutation):
                document = self.changed()
                if mutation == "missing":
                    del document["review_scope"]
                else:
                    document["self_approved"] = True
                with tempfile.TemporaryDirectory() as temporary:
                    path = self.write_receipt(Path(temporary), document)
                    with self.assertRaisesRegex(AcceptanceError, "key mismatch"):
                        validate_acceptance(path)

    def test_duplicate_json_key_fails(self) -> None:
        text = DEFAULT_RECEIPT.read_text(encoding="utf-8")
        duplicate = text.replace(
            '{\n  "schema_version":',
            '{\n  "schema_version": "duplicate",\n  "schema_version":',
            1,
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            path.write_text(duplicate, encoding="utf-8")
            with self.assertRaisesRegex(AcceptanceError, "duplicate JSON key"):
                validate_acceptance(path)

    def test_noncanonical_serialization_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_receipt(Path(temporary), self.changed(), canonical=False)
            with self.assertRaisesRegex(AcceptanceError, "not in canonical"):
                validate_acceptance(path)

    def test_hardlinked_receipt_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            path = self.write_receipt(directory, self.changed())
            os.link(path, directory / "second-link.json")
            with self.assertRaisesRegex(AcceptanceError, "hardlinked"):
                validate_acceptance(path)

    def test_artifact_byte_mismatch_fails(self) -> None:
        real_sha256 = __import__("verify_run2_acceptance").sha256_file

        def wrong_for_final_status(path: Path) -> str:
            if path.name == "FINAL_RUN_STATUS.md":
                return "0" * 64
            return real_sha256(path)

        with patch("verify_run2_acceptance.sha256_file", side_effect=wrong_for_final_status):
            with self.assertRaisesRegex(AcceptanceError, "relocated artifact hash mismatch"):
                validate_acceptance(DEFAULT_RECEIPT)

    def test_crosswalk_reconstruction_failure_propagates(self) -> None:
        with patch(
            "verify_run2_acceptance.validate_crosswalk",
            side_effect=CrosswalkError("synthetic reconstruction failure"),
        ):
            with self.assertRaisesRegex(AcceptanceError, "exhaustive crosswalk"):
                validate_acceptance(DEFAULT_RECEIPT)

    def test_crosswalk_accepted_count_drift_fails(self) -> None:
        synthetic = {
            "valid": True,
            "external_action_authority": False,
            "crosswalk_sha256": "0" * 64,
            **EXPECTED_CROSSWALK_COUNTS,
        }
        synthetic["total_direct_mappings"] += 1
        with patch("verify_run2_acceptance.validate_crosswalk", return_value=synthetic):
            with self.assertRaisesRegex(AcceptanceError, "independently accepted count"):
                validate_acceptance(DEFAULT_RECEIPT)


if __name__ == "__main__":
    unittest.main()
