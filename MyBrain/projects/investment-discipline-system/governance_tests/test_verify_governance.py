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
        shutil.copytree(PROJECT_ROOT / "audits", self.root / "audits")
        shutil.copytree(PROJECT_ROOT / "scripts", self.root / "scripts")
        shutil.copytree(PROJECT_ROOT / "governance_tests", self.root / "governance_tests")
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

    def test_wrong_reverse_acceptance_case_binding_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        specs["specs"][0]["acceptance_case_ids"] = []
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("has no exact acceptance_case_ids")

    def test_free_text_always_pass_oracle_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        oracle_id = specs["oracles"][0]["id"]
        specs["oracles"][0] = {"id": oracle_id, "rule": "always pass"}
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("oracle definition is not structurally enforceable")

    def test_missing_assertion_catalog_item_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        specs["assertion_catalog"] = [
            assertion
            for assertion in specs["assertion_catalog"]
            if assertion["id"] != "aggregate_verdict_matches"
        ]
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected(
            "O-CONDITIONAL-STATE references undefined assertions: "
            "['aggregate_verdict_matches']"
        )

    def test_unknown_assertion_evaluator_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        assertion = next(
            item
            for item in specs["assertion_catalog"]
            if item["id"] == "aggregate_verdict_matches"
        )
        assertion["evaluator_id"] = "EVAL-NOT-REAL"
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected(
            "aggregate_verdict_matches references unknown assertion evaluator"
        )

    def test_empty_acceptance_case_set_is_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        specs["negative_fixture_sets"][0]["case_ids"] = []
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("has no acceptance cases")

    def test_unbound_free_text_case_names_are_rejected(self) -> None:
        specs = self.read_json("governance/VERIFICATION_SPECS_V1.json")
        fixture_set = specs["negative_fixture_sets"][0]
        fixture_set["cases"] = ["sounds_bad"]
        self.write_json("governance/VERIFICATION_SPECS_V1.json", specs)
        self.assert_rejected("uses unbound free-text cases")

    def test_unknown_acceptance_case_requirement_is_rejected(self) -> None:
        cases = self.read_json("governance/ACCEPTANCE_CASES_V1.json")
        cases["cases"][0]["requirement_ids"].append("REQ-NOT-REAL")
        self.write_json("governance/ACCEPTANCE_CASES_V1.json", cases)
        self.assert_rejected("references unknown requirement_ids")

    def test_missing_operation_catalog_item_is_rejected(self) -> None:
        cases = self.read_json("governance/ACCEPTANCE_CASES_V1.json")
        cases["operation_catalog"] = [
            operation
            for operation in cases["operation_catalog"]
            if operation["id"] != "OP-GOV-OPEN-RESEARCH"
        ]
        self.write_json("governance/ACCEPTANCE_CASES_V1.json", cases)
        self.assert_rejected(
            "CASE-GOV-OPEN-RESEARCH references unknown operation_id"
        )

    def test_invalid_operation_selector_is_rejected(self) -> None:
        cases = self.read_json("governance/ACCEPTANCE_CASES_V1.json")
        operation = next(
            item
            for item in cases["operation_catalog"]
            if item["id"] == "OP-GOV-OPEN-RESEARCH"
        )
        operation["selector"] = "governance"
        self.write_json("governance/ACCEPTANCE_CASES_V1.json", cases)
        self.assert_rejected("OP-GOV-OPEN-RESEARCH has no parseable selector")

    def test_missing_design_freeze_target_is_rejected(self) -> None:
        (self.root / "scripts" / "verify_conditionals.py").unlink()
        self.assert_rejected("required design_freeze implementation target missing")

    def test_undeclared_trace_target_is_rejected(self) -> None:
        targets = self.read_json("governance/IMPLEMENTATION_TARGETS_V1.json")
        targets["targets"] = [
            target
            for target in targets["targets"]
            if target["path"] != "scripts/verify_conditionals.py"
        ]
        self.write_json("governance/IMPLEMENTATION_TARGETS_V1.json", targets)
        self.assert_rejected("implementation target coverage differs")

    def test_missing_required_reference_case_is_rejected(self) -> None:
        money = self.read_json("governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json")
        money["required_reference_cases"].append("CASE-NOT-REAL")
        self.write_json(
            "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json", money
        )
        self.assert_rejected("references unknown acceptance cases")

    def test_money_semantics_mutation_is_rejected(self) -> None:
        money = self.read_json("governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json")
        money["decimal_context"]["float_input_allowed"] = True
        self.write_json(
            "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json", money
        )
        self.assert_rejected("money decimal_context differs")

    def test_missing_money_calculation_step_is_rejected(self) -> None:
        money = self.read_json("governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json")
        booking = next(
            item for item in money["booking_rules"] if item["id"] == "MONEY-BOOK-BUY"
        )
        booking["calculation_steps"] = [
            step
            for step in booking["calculation_steps"]
            if step["id"] != "BUY-NOTIONAL"
        ]
        self.write_json(
            "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json", money
        )
        self.assert_rejected("MONEY-BOOK-BUY calculation step ids differ")

    def test_unknown_money_expression_operator_is_rejected(self) -> None:
        money = self.read_json("governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json")
        booking = next(
            item for item in money["booking_rules"] if item["id"] == "MONEY-BOOK-BUY"
        )
        step = next(
            item
            for item in booking["calculation_steps"]
            if item["id"] == "BUY-NOTIONAL"
        )
        step["op"] = "divide"
        self.write_json(
            "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json", money
        )
        self.assert_rejected(
            "MONEY-BOOK-BUY.BUY-NOTIONAL uses unknown expression operator: 'divide'"
        )

    def test_missing_corporate_action_case_binding_is_rejected(self) -> None:
        money = self.read_json("governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json")
        action = next(
            item
            for item in money["corporate_action_matrix"]
            if item["id"] == "ACTION-SPINOFF"
        )
        action["acceptance_case_ids"].remove("CASE-CORP-ACTION-UNKNOWN")
        self.write_json(
            "governance/MONEY_AND_CORPORATE_ACTIONS_SPEC_V1.json", money
        )
        self.assert_rejected("ACTION-SPINOFF has no acceptance_case_ids")

    def test_market_family_rename_reset_is_rejected(self) -> None:
        market = self.read_json("governance/MARKET_SIMULATION_POLICY_V1.json")
        market["experiment_lineage"]["rename_does_not_reset"] = False
        self.write_json("governance/MARKET_SIMULATION_POLICY_V1.json", market)
        self.assert_rejected("market experiment lineage or claim boundary differs")

    def test_missing_market_clause_id_is_rejected(self) -> None:
        market = self.read_json("governance/MARKET_SIMULATION_POLICY_V1.json")
        market["benchmark_policy"]["required_fields"] = [
            clause
            for clause in market["benchmark_policy"]["required_fields"]
            if clause["id"] != "BENCHMARK-CASH"
        ]
        self.write_json("governance/MARKET_SIMULATION_POLICY_V1.json", market)
        self.assert_rejected(
            "market benchmark fields clause ids differ: "
            "missing=['BENCHMARK-CASH']"
        )

    def test_ai_can_set_urgency_mutation_is_rejected(self) -> None:
        field = self.read_json("governance/FIELD_USE_PROTOCOL_V1.json")
        field["urgency_state_machine"]["rule"] = "AI/import can set it"
        self.write_json("governance/FIELD_USE_PROTOCOL_V1.json", field)
        self.assert_rejected("field-use anti-rubber-stamp boundary differs")

    def test_missing_field_clause_id_is_rejected(self) -> None:
        field = self.read_json("governance/FIELD_USE_PROTOCOL_V1.json")
        field["longitudinal_protocol"]["minimum_structure"] = [
            clause
            for clause in field["longitudinal_protocol"]["minimum_structure"]
            if clause["id"] != "FIELD-NATURAL-LONG-GAP"
        ]
        self.write_json("governance/FIELD_USE_PROTOCOL_V1.json", field)
        self.assert_rejected(
            "field-use minimum structure clause ids differ: "
            "missing=['FIELD-NATURAL-LONG-GAP']"
        )

    def test_private_backup_overwrite_mutation_is_rejected(self) -> None:
        private = self.read_json("governance/PRIVATE_DATA_POLICY_V1.json")
        private["backup_storage"]["immutability"] = "overwrite the latest backup"
        self.write_json("governance/PRIVATE_DATA_POLICY_V1.json", private)
        self.assert_rejected("private backup lifecycle boundary differs")

    def test_missing_private_backup_manifest_clause_id_is_rejected(self) -> None:
        private = self.read_json("governance/PRIVATE_DATA_POLICY_V1.json")
        private["backup_storage"]["manifest"] = [
            clause
            for clause in private["backup_storage"]["manifest"]
            if clause["id"] != "BACKUP-MANIFEST-CREATED-AT"
        ]
        self.write_json("governance/PRIVATE_DATA_POLICY_V1.json", private)
        self.assert_rejected(
            "private backup manifest clauses clause ids differ: "
            "missing=['BACKUP-MANIFEST-CREATED-AT']"
        )

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

    def test_missing_conditional_gate_executor_is_rejected(self) -> None:
        contract = self.read_json("governance/ACCEPTANCE_CONTRACT_V1.json")
        contract["conditional_gate_catalog"] = [
            item
            for item in contract["conditional_gate_catalog"]
            if item["id"] != "GATE-TIINGO-LIVE-PROBE"
        ]
        self.write_json("governance/ACCEPTANCE_CONTRACT_V1.json", contract)
        self.assert_rejected("conditional gate executor is missing")

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
