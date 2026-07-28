from __future__ import annotations

import copy
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
    MUTATION_EXECUTION_MODE,
    derive_projection,
    load_json,
    materialize_mutation_descriptor,
    sha256_file,
    validate_contract,
    validate_mutation_descriptor,
    validate_output,
    validate_state_timeline,
)


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "task-class.json"
STALE_MANIFEST = ROOT / "stale-task-class.json"
STATE = ROOT / "../../17-总体蓝图活动状态.json"
OPPORTUNITY_OBSERVATION = ROOT / "../../evidence/opportunity-control-plane-observation-2026-07-28.json"
C8_OBSERVATION = ROOT / "../../evidence/opportunity-c8-read-only-observation-2026-07-28.json"
INVESTMENT_OBSERVATION = ROOT / "../../evidence/investment-workflow-observation-2026-07-28.json"


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

    def test_stale_manifest_has_one_real_blueprint_hash_mismatch(self) -> None:
        code, result = validate_output(
            STALE_MANIFEST,
            ROOT / "fixtures/valid-output.json",
        )
        blueprint = (ROOT / "../../16-总体蓝图闭合合同与状态审计.md").resolve()
        self.assertEqual(code, EXIT_STALE_INPUT)
        self.assertEqual(result["classification"], "STALE_INPUT_BUNDLE")
        self.assertEqual(
            result["mismatches"],
            [
                {
                    "path": str(blueprint),
                    "expected": "0000000000000000000000000000000000000000000000000000000000000000",
                    "actual": sha256_file(blueprint),
                }
            ],
        )
        self.assertNotEqual(result["mismatches"][0]["actual"], "MISSING")

    def test_schema_valid_but_wrong_projection_is_rejected(self) -> None:
        code, result = validate_output(MANIFEST, ROOT / "fixtures/wrong-output.json")
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "WRONG_STATE_PROJECTION")

    def test_wrong_tiebreak_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "wrong-tiebreak.json"
            descriptor = materialize_mutation_descriptor(
                ROOT / "fixtures/wrong-tiebreak-output.json", candidate
            )
            self.assertEqual(descriptor["fixture_type"], "OUTPUT_MUTATION_DESCRIPTOR")
            self.assertEqual(descriptor["expected_exit_code"], EXIT_WRONG_OUTPUT)
            self.assertEqual(
                descriptor["expected_classification"], "WRONG_STATE_PROJECTION"
            )
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, descriptor["expected_exit_code"])
        self.assertEqual(result["classification"], descriptor["expected_classification"])

    def test_wrong_successor_rule_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "wrong-successor.json"
            descriptor = materialize_mutation_descriptor(
                ROOT / "fixtures/wrong-successor-output.json", candidate
            )
            self.assertEqual(descriptor["fixture_type"], "OUTPUT_MUTATION_DESCRIPTOR")
            self.assertEqual(descriptor["expected_exit_code"], EXIT_WRONG_OUTPUT)
            self.assertEqual(
                descriptor["expected_classification"], "WRONG_STATE_PROJECTION"
            )
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, descriptor["expected_exit_code"])
        self.assertEqual(result["classification"], descriptor["expected_classification"])

    def test_mutation_descriptor_metadata_mismatch_is_rejected(self) -> None:
        manifest = load_json(MANIFEST)
        entry = next(
            fixture
            for fixture in manifest["fixtures"]
            if fixture["role"] == "WRONG_TIEBREAK_MUTATION_FIXTURE"
        )
        descriptor = load_json(ROOT / entry["path"])
        entry["execution_mode"] = MUTATION_EXECUTION_MODE
        descriptor["expected_classification"] = "SCHEMA_INVALID"
        errors = validate_mutation_descriptor(descriptor, entry)
        self.assertEqual(
            errors,
            [
                "descriptor expected_classification='SCHEMA_INVALID' does not match "
                "fixture metadata 'WRONG_STATE_PROJECTION'"
            ],
        )

    def test_mutation_fixture_execution_mode_is_required_and_exact(self) -> None:
        manifest = load_json(MANIFEST)
        entry = next(
            fixture
            for fixture in manifest["fixtures"]
            if fixture["role"] == "WRONG_TIEBREAK_MUTATION_FIXTURE"
        )
        descriptor = load_json(ROOT / entry["path"])

        missing = copy.deepcopy(entry)
        missing.pop("execution_mode", None)
        self.assertEqual(
            validate_mutation_descriptor(descriptor, missing),
            [
                "mutation fixture execution_mode must be "
                "MATERIALIZE_DESCRIPTOR_THEN_VALIDATE_OUTPUT"
            ],
        )

        wrong = copy.deepcopy(entry)
        wrong["execution_mode"] = "VALIDATE_DESCRIPTOR_AS_OUTPUT"
        self.assertEqual(
            validate_mutation_descriptor(descriptor, wrong),
            [
                "mutation fixture execution_mode must be "
                "MATERIALIZE_DESCRIPTOR_THEN_VALIDATE_OUTPUT"
            ],
        )

    def test_wrong_outcome_precondition_is_rejected(self) -> None:
        output = load_json(ROOT / "fixtures/valid-output.json")
        output["projection"]["review_receipt_transition"][
            "record_outcome_candidate_action"
        ]["precondition"] = "WRONG_PRECONDITION"
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "wrong-precondition.json"
            candidate.write_text(json.dumps(output), encoding="utf-8")
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "WRONG_STATE_PROJECTION")

    def test_missing_tiebreak_policy_is_schema_invalid(self) -> None:
        output = load_json(ROOT / "fixtures/valid-output.json")
        del output["projection"]["objective_conflict_policy"]
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "missing-tiebreak.json"
            candidate.write_text(json.dumps(output), encoding="utf-8")
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "SCHEMA_INVALID")

    def test_extra_field_is_schema_invalid(self) -> None:
        output = load_json(ROOT / "fixtures/valid-output.json")
        output["self_approval"] = True
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = Path(temp_dir) / "extra-field.json"
            candidate.write_text(json.dumps(output), encoding="utf-8")
            code, result = validate_output(MANIFEST, candidate)
        self.assertEqual(code, EXIT_WRONG_OUTPUT)
        self.assertEqual(result["classification"], "SCHEMA_INVALID")

    def test_review_transition_projects_binding_protocol_and_split_actions(self) -> None:
        state = load_json(STATE)
        transition = derive_projection(state)["review_receipt_transition"]
        contract = state["review_output_contract"]
        for field in (
            "attempt_id",
            "artifact_serialization",
            "extracted_object_canonicalization",
            "checkpoint_order",
            "receipt_binding_requirements",
            "short_circuit_rule",
            "verbatim_receipt_paths",
            "mutation_rule",
            "state_transition_rule",
        ):
            with self.subTest(contract_field=field):
                self.assertEqual(transition[field], contract[field])

        action_fields = (
            "id",
            "effect_class",
            "ready",
            "blocked_by",
            "owner",
            "precondition",
            "write_set",
            "transition",
        )
        for output_field, action_id in (
            (
                "record_outcome_candidate_action",
                "PB-ACT-RECORD-R4-OUTCOME-CANDIDATE",
            ),
            ("commit_successor_action", "PB-ACT-COMMIT-R4-SUCCESSOR"),
        ):
            source = next(
                action
                for action in state["queued_after_primary"]
                if action["id"] == action_id
            )
            with self.subTest(action_id=action_id):
                self.assertEqual(
                    transition[output_field],
                    {field: source[field] for field in action_fields},
                )

    def test_duplicate_or_missing_split_outcome_actions_invalidate_projection(
        self,
    ) -> None:
        state = load_json(STATE)
        for action_id in (
            "PB-ACT-RECORD-R4-OUTCOME-CANDIDATE",
            "PB-ACT-COMMIT-R4-SUCCESSOR",
        ):
            without = copy.deepcopy(state)
            without["queued_after_primary"] = [
                action
                for action in without["queued_after_primary"]
                if action["id"] != action_id
            ]
            with self.subTest(action_id=action_id, mutation="missing"):
                with self.assertRaisesRegex(ValueError, f"exactly one {action_id}"):
                    derive_projection(without)

            duplicated = copy.deepcopy(state)
            action = next(
                item
                for item in duplicated["queued_after_primary"]
                if item["id"] == action_id
            )
            duplicated["queued_after_primary"].append(copy.deepcopy(action))
            with self.subTest(action_id=action_id, mutation="duplicate"):
                with self.assertRaisesRegex(ValueError, f"exactly one {action_id}"):
                    derive_projection(duplicated)

    def test_current_timeline_matches_sources(self) -> None:
        errors = validate_state_timeline(
            load_json(STATE),
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertEqual(errors, [])

    def test_observation_after_state_is_rejected(self) -> None:
        state = load_json(STATE)
        state["as_of"] = "2026-07-28T02:24:38-07:00"
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(any("precedes latest observation" in error for error in errors))

    def test_projected_observation_time_must_match_source(self) -> None:
        state = load_json(STATE)
        state["workflow_observations"]["opportunity"]["supplemental_c8_observed_at"] = (
            "2026-07-28T02:28:56-07:00"
        )
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(any("does not match source recorded_at" in error for error in errors))

    def test_coordination_receipt_time_must_match_source_and_latest(self) -> None:
        state = load_json(STATE)
        state["workflow_observations"]["opportunity"][
            "coordination_receipt_recorded_at"
        ] = "2026-07-28T03:19:00-07:00"
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(
            any(
                "opportunity.coordination_receipt_recorded_at" in error
                and "does not match source recorded_at" in error
                for error in errors
            ),
            errors,
        )

    def test_naive_timestamp_is_rejected(self) -> None:
        state = load_json(STATE)
        state["as_of"] = "2026-07-28T02:43:08"
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(any("timezone offset" in error for error in errors))

    def test_space_separator_timestamp_is_rejected(self) -> None:
        state = load_json(STATE)
        state["as_of"] = "2026-07-28 02:43:08-07:00"
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(
            any("invalid RFC3339 timestamp at state.as_of" in error for error in errors)
        )

    def test_malformed_latest_bound_timestamp_returns_errors(self) -> None:
        state = load_json(STATE)
        state["temporal_invariants"]["latest_bound_observation_at"] = "not-a-time"
        errors = validate_state_timeline(
            state,
            load_json(OPPORTUNITY_OBSERVATION),
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(
            any("latest_bound_observation_at" in error for error in errors), errors
        )

    def test_malformed_observation_timestamp_returns_errors(self) -> None:
        opportunity_observation = load_json(OPPORTUNITY_OBSERVATION)
        opportunity_observation["recorded_at"] = "not-a-time"
        errors = validate_state_timeline(
            load_json(STATE),
            opportunity_observation,
            load_json(C8_OBSERVATION),
            load_json(INVESTMENT_OBSERVATION),
        )
        self.assertTrue(
            any(
                "invalid RFC3339 timestamp at observation.opportunity.recorded_at"
                in error
                for error in errors
            ),
            errors,
        )

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
