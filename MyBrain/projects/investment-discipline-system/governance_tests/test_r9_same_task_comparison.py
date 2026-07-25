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


SOURCE_ROOT = Path(__file__).resolve().parents[1]
VERIFIER_RELATIVE = Path("scripts/verify_r9_same_task_comparison.py")
PREREGISTRATION_RELATIVE = Path(
    "research/SAME_TASK_METHOD_COMPARISON_PREREGISTRATION_R9_2026-07-25.json"
)
SOURCE_DOCUMENTS = (
    Path(
        "research/evidence/r8/RS-03/extracted/"
        "CRSP_Market_Indexes_Methodology_Guide_July_2026.txt"
    ),
    Path(
        "research/evidence/r8/RS-03/extracted/"
        "NYSE_CorporateActions_Client_Specification_v3.2a.txt"
    ),
    Path(
        "research/evidence/r8/RS-03/extracted/"
        "FactSet_Accurately_Backtesting_Point_in_Time.txt"
    ),
    Path(
        "research/evidence/r8/RS-03/extracted/"
        "Deutsche_Bank_Seven_Sins_of_Quantitative_Investing.txt"
    ),
)
NATIVE_SUBAGENT_SURFACE = "本项目父 Codex task/thread 的 native subagent"


class R9SameTaskPrelaunchControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name) / "isolated-project"
        for relative in (
            VERIFIER_RELATIVE,
            PREREGISTRATION_RELATIVE,
            *SOURCE_DOCUMENTS,
        ):
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_ROOT / relative, destination)
        self.verifier = self.root / VERIFIER_RELATIVE

    def tearDown(self) -> None:
        self._temporary.cleanup()

    def run_verifier(
        self,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            [
                sys.executable,
                str(self.verifier),
                "--root",
                str(self.root),
                "--json",
            ],
            cwd=self.root,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(
                "R9 verifier did not emit one machine JSON receipt: "
                f"{exc}\nstdout={completed.stdout}\nstderr={completed.stderr}"
            ) from exc
        self.assertIsInstance(payload, dict)
        return completed, payload

    def read_preregistration(self) -> dict[str, Any]:
        value = json.loads(
            (self.root / PREREGISTRATION_RELATIVE).read_text(encoding="utf-8")
        )
        self.assertIsInstance(value, dict)
        return value

    def write_preregistration(self, value: dict[str, Any]) -> None:
        (self.root / PREREGISTRATION_RELATIVE).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def assert_rejected(self, expected_error: str) -> dict[str, Any]:
        completed, payload = self.run_verifier()
        self.assertEqual(1, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual("fail", payload.get("status"), payload)
        self.assertFalse(payload.get("control_effective"), payload)
        self.assertEqual(
            "blocked_before_generation", payload.get("experiment_state"), payload
        )
        self.assertEqual("not_adopted", payload.get("wrapper_adoption"), payload)
        self.assertFalse(payload.get("generation_authorized"), payload)
        self.assertFalse(payload.get("method_comparison_completed"), payload)
        self.assertFalse(payload.get("experiment_passed"), payload)
        self.assertTrue(
            any(expected_error in error for error in payload.get("errors", [])),
            payload,
        )
        return payload

    def test_current_boundary_passes_only_as_an_effective_block(self) -> None:
        completed, payload = self.run_verifier()
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(
            "prelaunch_control_verification_only", payload["status_semantics"]
        )
        self.assertTrue(payload["control_effective"])
        self.assertEqual("blocked_before_generation", payload["experiment_state"])
        self.assertEqual("bounded_incomplete", payload["required_outcome_if_recorded"])
        self.assertEqual("not_adopted", payload["wrapper_adoption"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["method_comparison_completed"])
        self.assertFalse(payload["experiment_passed"])
        self.assertEqual(
            {
                "paired_replicates": 4,
                "generation_artifacts": 8,
                "generation_attempts_per_artifact": 1,
                "automatic_retries": 0,
            },
            payload["planned_design"],
        )
        self.assertEqual(4, payload["corpus"]["source_count"])
        self.assertEqual(11, payload["corpus"]["slice_count"])
        self.assertEqual(16512, payload["corpus"]["total_exposed_slice_bytes"])
        self.assertEqual([], payload["research_output_scan"]["unexpected_material"])

    def test_duplicate_key_is_rejected_as_non_strict_json(self) -> None:
        path = self.root / PREREGISTRATION_RELATIVE
        source = path.read_text(encoding="utf-8")
        path.write_text(
            source.replace(
                '"schema_version": 2,',
                '"schema_version": 2,\n  "schema_version": 2,',
                1,
            ),
            encoding="utf-8",
        )
        self.assert_rejected("duplicate object key: schema_version")

    def test_missing_receipts_cannot_be_relabelled_as_generation_authorized(
        self,
    ) -> None:
        document = self.read_preregistration()
        document["prelaunch_readiness"]["generation_authorized"] = True
        self.write_preregistration(document)
        self.assert_rejected("prelaunch_readiness.generation_authorized")

    def test_contains_execution_results_cannot_be_true(self) -> None:
        document = self.read_preregistration()
        document["contains_execution_results"] = True
        self.write_preregistration(document)
        self.assert_rejected("contains_execution_results")

    def test_identifiable_fake_generation_output_is_rejected(self) -> None:
        output = self.root / "research/r9-generation-output.json"
        output.write_text(
            json.dumps(
                {
                    "schema_id": "R9-GENERATION-OUTPUT-RECEIPT-PAYLOAD-V2",
                    "terminal_class": "completed",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.assert_rejected("unexpected R9 generation/review/result/receipt/sidecar")

    def test_parent_task_native_subagent_cannot_be_made_eligible(self) -> None:
        document = self.read_preregistration()
        preflight = document["prelaunch_capability_preflight"]
        preflight["required_generator_harness"] = "parent_task_native_subagent"
        preflight["prohibited_generation_surfaces"].remove(NATIVE_SUBAGENT_SURFACE)
        self.write_preregistration(document)
        payload = self.assert_rejected("required_generator_harness")
        self.assertTrue(
            any(
                "native subagent" in error and "unqualified" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_pair_or_artifact_count_cannot_be_reduced(self) -> None:
        document = self.read_preregistration()
        design = document["primary_design"]
        design["paired_replicate_count"] = 3
        design["replicates_per_arm"] = 3
        design["planned_generation_artifact_count"] = 6
        design["pair_ids"].pop()
        self.write_preregistration(document)
        payload = self.assert_rejected("paired_replicate_count")
        self.assertTrue(
            any(
                "planned_generation_artifact_count" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_automatic_retry_cannot_be_enabled(self) -> None:
        document = self.read_preregistration()
        document["resource_budget"]["generation_per_request"]["maximum_retries"] = 1
        self.write_preregistration(document)
        self.assert_rejected("resource_budget.generation_per_request.maximum_retries")

    def test_no_retry_rule_cannot_be_softened(self) -> None:
        document = self.read_preregistration()
        document["stopping_and_failure_protocol"]["no_retry_rule"] = (
            "retry once after service errors"
        )
        self.write_preregistration(document)
        self.assert_rejected("stopping_and_failure_protocol.no_retry_rule")

    def test_usage_receipt_contract_cannot_be_removed(self) -> None:
        document = self.read_preregistration()
        del document["receipt_acceptance_contract"]["usage_receipt"]
        self.write_preregistration(document)
        self.assert_rejected(
            "receipt_acceptance_contract.usage_receipt.required_fields"
        )

    def test_timing_receipt_contract_cannot_be_removed(self) -> None:
        document = self.read_preregistration()
        del document["receipt_acceptance_contract"]["timing_receipt"]
        self.write_preregistration(document)
        self.assert_rejected(
            "receipt_acceptance_contract.timing_receipt.required_fields"
        )

    def test_tree_sidecar_and_judge_fit_contracts_cannot_be_removed(self) -> None:
        document = self.read_preregistration()
        del document["package_and_tree_manifest"]["tree_manifest_payload_schema"]
        del document["hash_and_locator_protocol"]["generic_digest_sidecar_schema"]
        del document["judge_package_fit_preflight"]["required_fields"]
        self.write_preregistration(document)
        payload = self.assert_rejected("tree_manifest_payload_schema.schema_id")
        self.assertTrue(
            any(
                "generic_digest_sidecar_schema.schema_id" in error
                for error in payload["errors"]
            ),
            payload,
        )
        self.assertTrue(
            any(
                "judge_package_fit_preflight.required_fields" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_preregistration_cannot_embed_a_self_raw_sha_field(self) -> None:
        path = self.root / PREREGISTRATION_RELATIVE
        raw_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        document = self.read_preregistration()
        document["preregistration_raw_sha256"] = raw_digest
        self.write_preregistration(document)
        self.assert_rejected("self-referential preregistration raw sha256 field")

    def test_frozen_corpus_slice_tampering_is_rejected(self) -> None:
        path = self.root / SOURCE_DOCUMENTS[0]
        lines = path.read_bytes().splitlines(keepends=True)
        self.assertGreaterEqual(len(lines), 2469)
        lines[2468] = b"X" + lines[2468][1:]
        path.write_bytes(b"".join(lines))
        payload = self.assert_rejected("slice sha256 mismatch: R9-C01")
        self.assertTrue(
            any(
                "source document sha256 mismatch" in error
                for error in payload["errors"]
            ),
            payload,
        )

    def test_blocked_state_cannot_be_changed_to_pass_or_adopt(self) -> None:
        document = self.read_preregistration()
        document["prelaunch_readiness"]["state"] = "pass"
        document["additional_wrapper_admission_rule"]["outcome_function"][0] = (
            "若 preflight 未通过，则 outcome = adopt"
        )
        self.write_preregistration(document)
        payload = self.assert_rejected("prelaunch_readiness.state")
        self.assertTrue(
            any("outcome_function" in error for error in payload["errors"]), payload
        )

    def test_generator_package_count_cannot_be_forged(self) -> None:
        document = self.read_preregistration()
        package = document["package_and_tree_manifest"]["generator_visible_package"]
        package["exact_regular_file_count"] = 15
        package["exact_regular_file_paths"].pop()
        self.write_preregistration(document)
        payload = self.assert_rejected("exact_regular_file_paths")
        self.assertTrue(
            any("exact_regular_file_count" in error for error in payload["errors"]),
            payload,
        )


if __name__ == "__main__":
    unittest.main()
