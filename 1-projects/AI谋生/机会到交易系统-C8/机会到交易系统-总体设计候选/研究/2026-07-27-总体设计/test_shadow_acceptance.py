#!/usr/bin/env python3
"""Adversarial tests for the closed OpportunityRecord semantic Gate."""

from __future__ import annotations

import copy
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Callable, Optional
from unittest import mock

import run_shadow_acceptance as rsa


HERE = Path(__file__).resolve().parent
POLICY = HERE / "SHADOW_CAPABILITY_POLICY.json"
RUNNER = HERE / "run_shadow_acceptance.py"
PARENT_CANDIDATE_SHA256 = "c" * 64


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: object) -> None:
    write_bytes(path, rsa.canonical_text(value).encode("utf-8"))


def parent_bindings(*parents: dict) -> list[dict]:
    return [
        {
            "parent_id": parent["record_id"],
            "parent_sha256": rsa.sha256_json(parent),
            "required_state": "CURRENT",
        }
        for parent in parents
    ]


def common_record(
    schema: str, record_type: str, record_id: str, parents: tuple[dict, ...],
    **values,
) -> dict:
    record = {
        "schema_version": schema,
        "record_type": record_type,
        "record_id": record_id,
        "state": "CURRENT",
        "parent_bindings": parent_bindings(*parents),
    }
    record.update(values)
    return record


def make_valid_record(source_payload: Optional[str] = None) -> dict:
    source_payload = source_payload or (
        "Synthetic actor reports a repeated weekly formatting task."
    )
    sampling = common_record(
        "otts.observation-sampling-plan/1",
        "ObservationSamplingPlan",
        "ObservationSamplingPlan:plan-001",
        (),
        sampling_purpose="HYPOTHESIS_CONDITIONED",
        frozen_before_observation=True,
        plan_sequence=1,
        source_universe="SYNTHETIC_CONSTRUCTED_EXAMPLE_ONLY",
        selection_rule="One constructed record for contract testing.",
        inclusion_rule="Include the declared synthetic source only.",
        exclusion_rule="Exclude every real person, business, and account.",
        negative_sample_rule="Retain a no-demand counter-hypothesis.",
        stopping_rule="Stop after deterministic local Gate evaluation.",
    )
    freeze = common_record(
        "otts.sampling-plan-freeze-receipt/1",
        "SamplingPlanFreezeReceipt",
        "SamplingPlanFreezeReceipt:freeze-001",
        (sampling,),
        status="FROZEN",
        sequence=2,
        plan_sha256=rsa.sha256_json(sampling),
    )
    acquisition = common_record(
        "otts.acquisition-record/1",
        "AcquisitionRecord",
        "AcquisitionRecord:acquisition-001",
        (sampling, freeze),
        sequence=3,
        mode="SYNTHETIC_LOCAL_FIXTURE",
        observed_after_sampling_freeze=True,
        account_or_login_used=False,
        external_retrieval_performed=False,
    )
    rights = common_record(
        "otts.rights-record/1",
        "RightsRecord",
        "RightsRecord:rights-001",
        (acquisition,),
        status="SYNTHETIC_AUTHORIZED",
        contains_personal_data=False,
        account_or_login_used=False,
        external_retrieval_performed=False,
    )
    first_lane = common_record(
        "otts.sealed-lane-output/1",
        "SealedLaneOutput",
        "SealedLaneOutput:first-principles-001",
        (sampling, freeze),
        lane_id="Lane:first-principles-001",
        lane_epoch_id="LaneEpoch:epoch-001",
        lane_role="FIRST_PRINCIPLES",
        seal_sequence=4,
        sealed_before_observation=True,
        canary_id="Canary:first-principles-001",
        canary_token="FP_CANARY_TOKEN_001",
        contamination_detected=False,
        content_classification=(
            "GENERAL_PRINCIPLES_ONLY_HUMAN_ASSERTED_UNVERIFIED"
        ),
        principles=[
            "A complaint is evidence of friction, not demand proof.",
            "Voluntary costly action is stronger than a polite reaction.",
        ],
        assumptions=[
            "The synthetic friction may or may not change behavior."
        ],
    )
    claim_id = "ObservationClaim:claim-001"
    observation = common_record(
        "otts.sealed-lane-output/1",
        "SealedLaneOutput",
        "SealedLaneOutput:observation-001",
        (acquisition, rights),
        lane_id="Lane:observation-001",
        lane_epoch_id="LaneEpoch:epoch-001",
        lane_role="OBSERVATION",
        seal_sequence=5,
        sealed_before_cross_lane_merge=True,
        canary_id="Canary:observation-001",
        canary_token="OBS_CANARY_TOKEN_001",
        contamination_detected=False,
        source_kind="SYNTHETIC_CONSTRUCTED_TEXT",
        source_payload=source_payload,
        source_payload_sha256=rsa.sha256_bytes(source_payload.encode("utf-8")),
        evidence_classification="DIRECT_SOURCE_SPANS_ONLY_SEMANTICS_UNVERIFIED",
        observations=[
            {
                "claim_id": claim_id,
                "source_start": 0,
                "source_end": len(source_payload),
                "source_text": source_payload,
                "span_sha256": rsa.sha256_bytes(source_payload.encode("utf-8")),
                "evidence_class": "DIRECT_SOURCE_SPAN",
            }
        ],
        signal_taxonomy={
            "schema_version": "otts.structured-signal-taxonomy/1",
            "primary_class": "EXPLICIT_COMPLAINT",
            "explicit_request_status": "NOT_ESTABLISHED",
            "behavior_observation_status": "SYNTHETIC_NOT_REAL_WORLD",
            "extraction_basis": "SOURCE_SPAN_BOUND_HUMAN_LABEL",
            "extraction_uncertainty": "UNVERIFIED_SEMANTIC_LABEL",
            "natural_language_inference_performed": False,
            "source_payload_sha256": rsa.sha256_bytes(
                source_payload.encode("utf-8")
            ),
            "source_span_ids": [claim_id],
        },
    )
    contamination = common_record(
        "otts.contamination-event/1",
        "ContaminationEvent",
        "ContaminationEvent:assessment-001",
        (first_lane, observation),
        status="CLEAR",
        detected=False,
        detected_canary_ids=[],
        assessment_sequence=6,
    )
    hypothesis = common_record(
        "otts.need-hypothesis/1",
        "NeedHypothesis",
        "NeedHypothesis:hypothesis-001",
        (rights, first_lane, observation, contamination),
        status="HYPOTHESIS_NOT_DEMAND_PROOF",
        merge_sequence=7,
        candidate_buyer_class="Synthetic recurring-workflow owner.",
        job_to_be_done="Evaluate a bounded local transformation.",
        statement="Some such actors may value reduced repetitive work.",
        competing_explanations=[
            "The statement may be casual venting.",
            "The current workaround may already be sufficient.",
        ],
        applicability_scope="Synthetic contract fixture only.",
        weakest_assumption="The friction changes costly behavior.",
        supporting_observation_claim_ids=[claim_id],
    )
    experiment = common_record(
        "otts.experiment-spec/1",
        "ExperimentSpec",
        "ExperimentSpec:experiment-001",
        (rights, hypothesis),
        status="UNEXECUTED",
        requires_new_explicit_authorization=True,
        draft_method="Only after new authorization, define a bounded evaluation.",
        success_signal="A predeclared costly evaluation action.",
        failure_signal="No predeclared costly evaluation action.",
        forbidden_capabilities=[
            "ACCOUNT_ACCESS",
            "CONTACT",
            "DEPLOYMENT",
            "EXTERNAL_RETRIEVAL",
            "PAYMENT",
            "PRICING",
        ],
        external_action_authority=False,
    )
    eval_spec = common_record(
        "otts.eval-spec/1",
        "EvalSpec",
        "EvalSpec:eval-001",
        (experiment, hypothesis),
        status="NOT_RUN",
        fixture_type="SYNTHETIC",
        oracle_kind="EXACT_RESULT_HASH_OR_STABLE_REJECTION_CODE",
        model_binding_sha256="a" * 64,
        harness_binding_sha256="b" * 64,
        human_baseline="Manually validate the same synthetic structured record.",
        cost_record="No external spend; deterministic local evaluation only.",
        external_action_authority=False,
    )
    return {
        "schema_version": "otts.opportunity-record/1",
        "record_type": "OpportunityRecord",
        "record_id": "OpportunityRecord:synthetic-001",
        "record_state": "CURRENT",
        "parent_context": {
            "candidate_id": "CandidateManifest:synthetic-c8",
            "candidate_sha256": PARENT_CANDIDATE_SHA256,
            "state": "CURRENT",
        },
        "sampling_plan": sampling,
        "sampling_freeze_receipt": freeze,
        "acquisition_record": acquisition,
        "rights_record": rights,
        "first_principles_lane": first_lane,
        "observation_lane": observation,
        "contamination_event": contamination,
        "need_hypothesis": hypothesis,
        "experiment_spec": experiment,
        "eval_spec": eval_spec,
        "authority": {
            "market_authority": False,
            "customer_authority": False,
            "demand_proof": False,
            "pricing_authority": False,
            "payment_authority": False,
            "deployment_authority": False,
            "external_action_authority": False,
        },
    }


def make_program(*, cas_roundtrip: bool = True) -> dict:
    nodes = [
        {"id": "input", "op": "INPUT"},
        {
            "id": "validated",
            "op": "VALIDATE_OPPORTUNITY_RECORD",
            "source": "input",
        },
    ]
    result_ref = "validated"
    if cas_roundtrip:
        nodes.extend([
            {"id": "stored", "op": "CAS_PUT", "source": "validated"},
            {"id": "restored", "op": "CAS_GET", "digest_ref": "stored"},
        ])
        result_ref = "restored"
    return {
        "schema_version": "otts.shadow-declarative-ir/2",
        "program_id": "OPPORTUNITY-GATE",
        "gate_id": "OTTS-OPPORTUNITY-SEMANTIC-GATE-1",
        "input_type": "OPPORTUNITY_RECORD",
        "output_type": "NORMALIZED_OPPORTUNITY_RECORD",
        "nodes": nodes,
        "result_ref": result_ref,
    }


def replace_observation_source_payload(record: dict, payload: str) -> None:
    observation = record["observation_lane"]
    payload_sha256 = rsa.sha256_bytes(payload.encode("utf-8"))
    observation["source_payload"] = payload
    observation["source_payload_sha256"] = payload_sha256
    claim = observation["observations"][0]
    claim["source_end"] = len(payload)
    claim["source_text"] = payload
    claim["span_sha256"] = payload_sha256
    observation["signal_taxonomy"]["source_payload_sha256"] = payload_sha256


def required_semantic_cases() -> list[tuple[str, dict, str, Optional[str]]]:
    valid = make_valid_record()
    rows: list[tuple[str, dict, str, str | None]] = [
        ("PASS-VALID", valid, "PASS", None)
    ]
    mutations: list[tuple[str, str, Callable[[dict], None]]] = [
        (
            "REJECT-SAMPLING",
            "SAMPLING_PLAN_NOT_FROZEN",
            lambda value: value["sampling_plan"].update(
                {"frozen_before_observation": False}
            ),
        ),
        (
            "REJECT-FIRST-SEAL",
            "FIRST_PRINCIPLES_NOT_PRESEALED",
            lambda value: value["first_principles_lane"].update(
                {"sealed_before_observation": False}
            ),
        ),
        (
            "REJECT-OBS-SEAL",
            "OBSERVATION_NOT_PRESEALED",
            lambda value: value["observation_lane"].update(
                {"sealed_before_cross_lane_merge": False}
            ),
        ),
        (
            "REJECT-CONTAMINATION",
            "CONTAMINATION_DETECTED",
            lambda value: value["observation_lane"].update(
                {"contamination_detected": True}
            ),
        ),
        (
            "REJECT-RIGHTS",
            "RIGHTS_NOT_AUTHORIZED",
            lambda value: value["rights_record"].update({
                "status": "DENIED",
                "account_or_login_used": True,
                "external_retrieval_performed": True,
            }),
        ),
        (
            "REJECT-LEGACY",
            "LEGACY_SCHEMA_QUARANTINED",
            lambda value: value.update({"schema_version": "0.1"}),
        ),
        (
            "REJECT-EXPERIMENT",
            "EXPERIMENT_EXECUTION_FORBIDDEN",
            lambda value: value["experiment_spec"].update(
                {"status": "EXECUTED"}
            ),
        ),
        (
            "REJECT-CROSS-CANARY",
            "CROSS_LANE_CANARY_DETECTED",
            lambda value: replace_observation_source_payload(
                value,
                "Synthetic prefix "
                + value["first_principles_lane"]["canary_token"]
                + " synthetic suffix.",
            ),
        ),
        (
            "REJECT-SIGNAL",
            "SIGNAL_TAXONOMY_INCONSISTENT",
            lambda value: value["observation_lane"]["signal_taxonomy"].update({
                "explicit_request_status": "HUMAN_ASSERTED_UNVERIFIED"
            }),
        ),
    ]
    for case_id, code, mutation in mutations:
        record = copy.deepcopy(valid)
        mutation(record)
        rows.append((case_id, record, "REJECT", code))
    return rows


class ShadowAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otts-domain-gate-test-")
        self.root = Path(self.temporary.name) / "shadow"
        self.root.mkdir()
        self.program_path = self.root / "program.json"
        self.fixture_path = self.root / "fixture.json"
        self.program = make_program()
        self.fixture = make_valid_record()
        write_json(self.program_path, self.program)
        write_json(self.fixture_path, self.fixture)
        self.policy_snapshot = rsa.read_once_regular(POLICY, "policy", 524288)
        self.policy = rsa.load_policy_snapshot(self.policy_snapshot)
        self.runner_snapshot = rsa.read_once_regular(
            RUNNER, "runner", 2 * 1024 * 1024
        )
        self.valid_output = rsa.validate_opportunity_record(
            self.fixture, PARENT_CANDIDATE_SHA256
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def snapshot(self, path: Path, label: str = "test") -> rsa.Snapshot:
        return rsa.read_once_regular(path, label, 2 * 1024 * 1024)

    def runtime_observation(self) -> dict:
        module_path = rsa.TRUSTED_PYTHON_HOME / "lib/python3.9/json/__init__.py"
        module_snapshot = rsa._trusted_binary_snapshot(module_path, "test module")
        rows = [{
            "path": str(module_path),
            "sha256": module_snapshot.sha256,
            "byte_length": len(module_snapshot.data),
            "modules": ["json"],
        }]
        return {
            "python_version": "3.9.6 synthetic-test-binding",
            "python_implementation_cache_tag": "cpython-39",
            "python_executable": str(rsa.TRUSTED_PYTHON),
            "python_prefix": str(rsa.TRUSTED_PYTHON_HOME),
            "loaded_module_files": rows,
            "loaded_module_file_closure_digest_sha256": rsa.sha256_json(rows),
            "closure_scope": (
                "ACTUALLY_LOADED_PYTHON_MODULE_FILES_AT_RESPONSE_MEASUREMENT"
            ),
            "full_dynamic_library_and_host_runtime_closure_proven": False,
        }

    def worker_response(self, record: dict) -> dict:
        with tempfile.TemporaryDirectory(prefix="otts-local-domain-eval-") as temporary:
            output = Path(temporary) / "output"
            cas = output / "cas"
            cas.mkdir(parents=True)
            try:
                result, steps = rsa.evaluate_program(
                    self.program,
                    record,
                    self.policy,
                    cas,
                    PARENT_CANDIDATE_SHA256,
                )
                result_bytes = rsa.canonical_bytes(result)
                outcome = "PASS"
                result_sha256 = rsa.sha256_bytes(result_bytes)
                result_type = rsa.json_type_name(result)
                result_byte_length = len(result_bytes)
                rejection_code = None
            except rsa.DomainRejection as rejection:
                outcome = "REJECT"
                steps = rejection.steps
                result_sha256 = None
                result_type = None
                result_byte_length = None
                rejection_code = rejection.code
            inventory = rsa._output_inventory(output, self.policy["limits"])
        return {
            "ok": True,
            "outcome": outcome,
            "result_sha256": result_sha256,
            "result_type": result_type,
            "result_byte_length": result_byte_length,
            "rejection_code": rejection_code,
            "steps": steps,
            "output_inventory_digest_sha256": rsa.sha256_json(inventory),
            "runtime_observation": self.runtime_observation(),
        }

    def local_case_response(self, record: dict) -> dict:
        response = self.worker_response(record)
        response.update({
            "sandbox_observed_enforcement": {
                "CHILD_PROCESS_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_READ_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_WRITE_DENIED": "OBSERVED_DENIED",
                "NETWORK_LOOPBACK_BIND_DENIED": "OBSERVED_DENIED",
            },
            "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
            "exact_opened_unlinked_snapshot_execution": True,
            "staged_target_controlled_pathname_reopen_count": 0,
            "same_uid_concurrent_mutation_resistance_proven": False,
            "host_level_universal_noninterference_proven": False,
            "sandbox_inherited_fd_boundary": (
                "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_"
                "BOUNDED_UNLINKED_STDIO_FDS; "
                "POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED"
            ),
            "sandbox_same_runtime_reexec_residual": (
                "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; "
                "CLOSED_DOMAIN_IR_HAS_NO_EXEC_OPCODE"
            ),
            "memory_boundary": (
                "NO_HOST_RSS_LIMIT_ON_DARWIN; "
                "FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED"
            ),
        })
        return response

    def base_shadow(self) -> dict:
        return {
            "parent_candidate_manifest_sha256": PARENT_CANDIDATE_SHA256,
            "capability_policy_sha256": self.policy_snapshot.sha256,
            "program": "program.json",
            "acceptance_cases": [{
                "case_id": "PASS-VALID",
                "fixture_path": "fixture.json",
                "expected_outcome": "PASS",
                "expected_result_sha256": rsa.sha256_json(self.valid_output),
            }],
            "sbom": {"path": "SBOM.json", "sha256": "0" * 64},
            "capability_report": {
                "path": "CAPABILITY_REPORT.json", "sha256": "0" * 64
            },
            "acceptance_test_report": {
                "path": "ACCEPTANCE_TEST_REPORT.json", "sha256": "0" * 64
            },
            "snapshot_ledger": {
                "path": "SNAPSHOT_LEDGER.json", "sha256": "0" * 64
            },
            "entries": [
                {
                    "path": "program.json",
                    "sha256": self.snapshot(self.program_path).sha256,
                    "role": "ir-program",
                },
                {
                    "path": "fixture.json",
                    "sha256": self.snapshot(self.fixture_path).sha256,
                    "role": "fixture",
                },
            ],
        }

    def materialize_package(self) -> tuple[dict, list[dict]]:
        shadow = self.base_shadow()
        shadow["acceptance_cases"] = []
        shadow["entries"] = [{
            "path": "program.json",
            "sha256": self.snapshot(self.program_path).sha256,
            "role": "ir-program",
        }]
        records: list[dict] = []
        for case_id, record, outcome, rejection_code in required_semantic_cases():
            fixture_relative = f"fixtures/{case_id.lower()}.json"
            fixture_path = self.root / fixture_relative
            write_json(fixture_path, record)
            case = {
                "case_id": case_id,
                "fixture_path": fixture_relative,
                "expected_outcome": outcome,
            }
            if outcome == "PASS":
                normalized = rsa.validate_opportunity_record(
                    record, PARENT_CANDIDATE_SHA256
                )
                case["expected_result_sha256"] = rsa.sha256_json(normalized)
            else:
                case["expected_rejection_code"] = rejection_code
            shadow["acceptance_cases"].append(case)
            shadow["entries"].append({
                "path": fixture_relative,
                "sha256": self.snapshot(fixture_path).sha256,
                "role": "fixture",
            })
            records.append(record)

        sbom, capability, initial_entries = rsa.build_static_reports(
            shadow_root=self.root,
            shadow=shadow,
            policy_path=POLICY,
            policy_snapshot=self.policy_snapshot,
            runner_snapshot=self.runner_snapshot,
        )
        ledger = rsa.build_snapshot_ledger(
            entries=initial_entries,
            policy_snapshot=self.policy_snapshot,
            runner_snapshot=self.runner_snapshot,
        )
        ledger_path = self.root / "SNAPSHOT_LEDGER.json"
        write_json(ledger_path, ledger)
        shadow["entries"].append({
            "path": ledger_path.name,
            "sha256": self.snapshot(ledger_path).sha256,
            "role": "snapshot-ledger",
        })
        shadow["snapshot_ledger"]["sha256"] = self.snapshot(ledger_path).sha256
        sbom_path = self.root / "SBOM.json"
        write_json(sbom_path, sbom)
        capability["sbom_sha256"] = self.snapshot(sbom_path).sha256
        capability_path = self.root / "CAPABILITY_REPORT.json"
        write_json(capability_path, capability)
        for path, role in (
            (sbom_path, "sbom"),
            (capability_path, "capability-report"),
        ):
            shadow["entries"].append({
                "path": path.name,
                "sha256": self.snapshot(path).sha256,
                "role": role,
            })
        shadow["sbom"]["sha256"] = self.snapshot(sbom_path).sha256
        shadow["capability_report"]["sha256"] = self.snapshot(
            capability_path
        ).sha256

        responses = [self.local_case_response(record) for record in records]
        case_results = []
        for case, response in zip(shadow["acceptance_cases"], responses):
            fixture_path = self.root / case["fixture_path"]
            case_results.append({
                "case_id": case["case_id"],
                "fixture_path": case["fixture_path"],
                "fixture_sha256": self.snapshot(fixture_path).sha256,
                "expected_outcome": case["expected_outcome"],
                "actual_outcome": response["outcome"],
                "expected_result_sha256": case.get("expected_result_sha256"),
                "actual_result_sha256": response["result_sha256"],
                "expected_rejection_code": case.get("expected_rejection_code"),
                "actual_rejection_code": response["rejection_code"],
                "result_type": response["result_type"],
                "result_byte_length": response["result_byte_length"],
                "steps": response["steps"],
                "output_inventory_digest_sha256": response[
                    "output_inventory_digest_sha256"
                ],
                "loaded_module_file_closure_digest_sha256": response[
                    "runtime_observation"
                ]["loaded_module_file_closure_digest_sha256"],
            })
        runtime_observation = responses[0]["runtime_observation"]
        runtime_tcb = rsa.runtime_tcb_document(self.runner_snapshot)
        runtime_tcb["loaded_python_module_file_closure"] = runtime_observation
        graph = rsa.validate_program(self.program, self.policy)
        report = {
            "schema_version": "otts.shadow-acceptance-test-report/4",
            "result": "LOCAL_DETERMINISTIC_DOMAIN_GATE_ACCEPTANCE_PASS",
            "runner_sha256": self.runner_snapshot.sha256,
            "policy_sha256": self.policy_snapshot.sha256,
            "parent_candidate_manifest_sha256": PARENT_CANDIDATE_SHA256,
            "sbom_sha256": self.snapshot(sbom_path).sha256,
            "capability_report_sha256": self.snapshot(capability_path).sha256,
            "program_sha256": self.snapshot(self.program_path).sha256,
            "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
            "snapshot_ledger_sha256": self.snapshot(ledger_path).sha256,
            "runtime_tcb_digest_sha256": rsa.sha256_json(runtime_tcb),
            "loaded_module_file_closure_digest_sha256": runtime_observation[
                "loaded_module_file_closure_digest_sha256"
            ],
            "acceptance_output_set_digest_sha256": rsa.sha256_json(case_results),
            "domain_gate_id": "OTTS-OPPORTUNITY-SEMANTIC-GATE-1",
            "domain_rejection_code_set_sha256": rsa.sha256_json(
                sorted(rsa.DOMAIN_REJECTION_CODES)
            ),
            "required_acceptance_rejection_codes": sorted(
                rsa.REQUIRED_ACCEPTANCE_REJECTION_CODES
            ),
            "pass_case_count": 1,
            "reject_case_count": len(case_results) - 1,
            "program": "program.json",
            "cases": case_results,
            "language_level_artifact_executable_constructs": (
                "ABSENT_BY_EXACT_SCHEMA"
            ),
            "os_sandbox_observed_enforcement": responses[0][
                "sandbox_observed_enforcement"
            ],
            "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
            "exact_opened_unlinked_snapshot_execution": True,
            "staged_target_controlled_pathname_reopen_count": 0,
            "same_uid_concurrent_mutation_resistance_proven": False,
            "host_level_universal_noninterference_proven": False,
            "sandbox_inherited_fd_boundary": (
                "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_"
                "BOUNDED_UNLINKED_STDIO_FDS; "
                "POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED"
            ),
            "sandbox_same_runtime_reexec_residual": (
                "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; "
                "CLOSED_DOMAIN_IR_HAS_NO_EXEC_OPCODE"
            ),
            "memory_boundary": (
                "NO_HOST_RSS_LIMIT_ON_DARWIN; "
                "FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED"
            ),
            "natural_language_speech_act_inference_proven": False,
            "semantic_truth_of_human_labels_proven": False,
            "real_world_temporal_order_proven": False,
            "actual_lane_generation_isolation_proven": False,
            "aggregate_deadline_enforced": True,
            "aggregate_wall_timeout_seconds": self.policy["limits"][
                "aggregate_wall_timeout_seconds"
            ],
            "runtime_authority": False,
            "deployment_authority": False,
            "freeze_authority": False,
            "external_action_authority": False,
        }
        report_path = self.root / "ACCEPTANCE_TEST_REPORT.json"
        write_json(report_path, report)
        shadow["entries"].append({
            "path": report_path.name,
            "sha256": self.snapshot(report_path).sha256,
            "role": "acceptance-report",
        })
        shadow["acceptance_test_report"]["sha256"] = self.snapshot(
            report_path
        ).sha256
        return shadow, responses

    def assert_domain_reject(self, record: dict, code: str) -> None:
        with self.assertRaises(rsa.DomainRejection) as raised:
            rsa.validate_opportunity_record(record, PARENT_CANDIDATE_SHA256)
        self.assertEqual(raised.exception.code, code)

    def test_valid_gate_returns_normalized_record_and_preserves_nonclaims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, steps = rsa.evaluate_program(
                self.program,
                self.fixture,
                self.policy,
                Path(temporary),
                PARENT_CANDIDATE_SHA256,
            )
        self.assertEqual(steps, 4)
        self.assertEqual(result["schema_version"], "otts.normalized-opportunity-record/1")
        self.assertEqual(result["record"], self.fixture)
        self.assertFalse(result["semantic_boundary"]["natural_language_speech_act_inferred"])
        self.assertFalse(result["semantic_boundary"]["semantic_truth_of_human_labels_proven"])
        self.assertFalse(result["semantic_boundary"]["demand_proven"])
        self.assertTrue(
            result["semantic_boundary"][
                "target_controlled_synthetic_record_internal_consistency_only"
            ]
        )
        self.assertFalse(
            result["semantic_boundary"]["real_world_temporal_order_proven"]
        )
        self.assertFalse(
            result["semantic_boundary"]["actual_lane_generation_isolation_proven"]
        )
        self.assertTrue(all(value is False for value in result["authority"].values()))

    def test_c7_seven_reproduced_unsafe_variants_reject_with_stable_codes(self) -> None:
        valid = make_valid_record()
        self.assertEqual(
            rsa.validate_opportunity_record(valid, PARENT_CANDIDATE_SHA256)[
                "derived_record_status"
            ],
            "CURRENT",
        )
        for _, record, outcome, code in required_semantic_cases()[1:8]:
            with self.subTest(code=code):
                self.assertEqual(outcome, "REJECT")
                self.assert_domain_reject(record, str(code))

    def test_signal_taxonomy_and_source_bound_observation_rejections(self) -> None:
        valid = make_valid_record()
        complaint_as_request = copy.deepcopy(valid)
        complaint_as_request["observation_lane"]["signal_taxonomy"][
            "explicit_request_status"
        ] = "HUMAN_ASSERTED_UNVERIFIED"
        self.assert_domain_reject(
            complaint_as_request, "SIGNAL_TAXONOMY_INCONSISTENT"
        )
        missing_uncertainty = copy.deepcopy(valid)
        missing_uncertainty["observation_lane"]["signal_taxonomy"][
            "extraction_uncertainty"
        ] = "CERTAIN"
        self.assert_domain_reject(
            missing_uncertainty, "SIGNAL_EXTRACTION_UNCERTAINTY_MISSING"
        )
        invented_observation = copy.deepcopy(valid)
        invented_observation["observation_lane"]["observations"][0][
            "source_text"
        ] = "A mockup would be valuable."
        self.assert_domain_reject(
            invented_observation, "OBSERVATION_SOURCE_BINDING_MISMATCH"
        )
        solution_classification = copy.deepcopy(valid)
        solution_classification["first_principles_lane"][
            "content_classification"
        ] = "SOLUTION_CONTENT"
        self.assert_domain_reject(
            solution_classification,
            "FIRST_PRINCIPLES_CONTENT_CLASSIFICATION_INVALID",
        )

    def test_typed_id_parent_hash_and_staleness_fail_closed(self) -> None:
        valid = make_valid_record()
        variants = []
        collision = copy.deepcopy(valid)
        collision["observation_lane"]["record_id"] = collision[
            "first_principles_lane"
        ]["record_id"]
        variants.append((collision, "TYPED_ID_COLLISION"))
        wrong_type = copy.deepcopy(valid)
        wrong_type["rights_record"]["record_id"] = "AcquisitionRecord:rights-001"
        variants.append((wrong_type, "TYPED_ID_TYPE_MISMATCH"))
        dangling = copy.deepcopy(valid)
        dangling["rights_record"]["parent_bindings"][0][
            "parent_id"
        ] = "AcquisitionRecord:missing"
        variants.append((dangling, "PARENT_DANGLING"))
        bad_hash = copy.deepcopy(valid)
        bad_hash["rights_record"]["parent_bindings"][0]["parent_sha256"] = "f" * 64
        variants.append((bad_hash, "PARENT_HASH_MISMATCH"))
        stale = copy.deepcopy(valid)
        stale["sampling_plan"]["state"] = "STALE"
        variants.append((stale, "PARENT_STALE"))
        invalid = copy.deepcopy(valid)
        invalid["sampling_plan"]["state"] = "INVALID"
        variants.append((invalid, "PARENT_INVALID"))
        for record, code in variants:
            with self.subTest(code=code):
                self.assert_domain_reject(record, code)

    def test_lane_canary_rights_and_authority_variants_fail_closed(self) -> None:
        valid = make_valid_record()
        variants = []
        lane_collision = copy.deepcopy(valid)
        lane_collision["observation_lane"]["lane_id"] = lane_collision[
            "first_principles_lane"
        ]["lane_id"]
        variants.append((lane_collision, "LANE_ID_COLLISION"))
        canary_collision = copy.deepcopy(valid)
        canary_collision["observation_lane"]["canary_token"] = canary_collision[
            "first_principles_lane"
        ]["canary_token"]
        variants.append((canary_collision, "CANARY_ID_COLLISION"))
        embedded_canary = copy.deepcopy(valid)
        embedded_payload = (
            "Synthetic prefix "
            + embedded_canary["first_principles_lane"]["canary_token"]
            + " synthetic suffix."
        )
        replace_observation_source_payload(embedded_canary, embedded_payload)
        variants.append((embedded_canary, "CROSS_LANE_CANARY_DETECTED"))
        account = copy.deepcopy(valid)
        account["rights_record"]["account_or_login_used"] = True
        variants.append((account, "RIGHTS_ACCOUNT_ACCESS_FORBIDDEN"))
        retrieval = copy.deepcopy(valid)
        retrieval["rights_record"]["external_retrieval_performed"] = True
        variants.append((retrieval, "RIGHTS_EXTERNAL_RETRIEVAL_FORBIDDEN"))
        personal = copy.deepcopy(valid)
        personal["rights_record"]["contains_personal_data"] = True
        variants.append((personal, "RIGHTS_PERSONAL_DATA_FORBIDDEN"))
        authority = copy.deepcopy(valid)
        authority["authority"]["pricing_authority"] = True
        variants.append((authority, "AUTHORITY_ESCALATION_FORBIDDEN"))
        for record, code in variants:
            with self.subTest(code=code):
                self.assert_domain_reject(record, code)

    def test_experiment_eval_and_exact_schema_fail_closed(self) -> None:
        valid = make_valid_record()
        no_authorization = copy.deepcopy(valid)
        no_authorization["experiment_spec"][
            "requires_new_explicit_authorization"
        ] = False
        self.assert_domain_reject(
            no_authorization, "EXPERIMENT_AUTHORIZATION_REQUIRED"
        )
        eval_executed = copy.deepcopy(valid)
        eval_executed["eval_spec"]["status"] = "EXECUTED"
        self.assert_domain_reject(eval_executed, "EVAL_EXECUTION_FORBIDDEN")
        extra = copy.deepcopy(valid)
        extra["rights_record"]["unexpected"] = True
        self.assert_domain_reject(extra, "DOMAIN_SCHEMA_KEY_MISMATCH")
        missing = copy.deepcopy(valid)
        missing["rights_record"].pop("status")
        self.assert_domain_reject(missing, "DOMAIN_SCHEMA_KEY_MISMATCH")
        wrong_type = copy.deepcopy(valid)
        wrong_type["sampling_plan"] = []
        self.assert_domain_reject(wrong_type, "DOMAIN_TYPE_MISMATCH")
        unknown_schema = copy.deepcopy(valid)
        unknown_schema["schema_version"] = "otts.opportunity-record/2"
        self.assert_domain_reject(unknown_schema, "DOMAIN_SCHEMA_MISMATCH")

    def test_closed_program_shape_prevents_gate_bypass(self) -> None:
        direct = make_program(cas_roundtrip=False)
        self.assertEqual(rsa.validate_program(direct, self.policy)["node_count"], 2)
        variants = []
        unknown = copy.deepcopy(self.program)
        unknown["nodes"][1]["op"] = "PYTHON_CALLBACK"
        variants.append((unknown, "unknown opcode"))
        wrong_type = copy.deepcopy(self.program)
        wrong_type["input_type"] = "JSON"
        variants.append((wrong_type, "domain Gate"))
        bypass = copy.deepcopy(self.program)
        bypass["result_ref"] = "input"
        variants.append((bypass, "unreachable"))
        extra_key = copy.deepcopy(self.program)
        extra_key["nodes"][1]["params"] = {"callback": "eval"}
        variants.append((extra_key, "key mismatch"))
        bad_cas = copy.deepcopy(self.program)
        bad_cas["nodes"][2]["source"] = "input"
        variants.append((bad_cas, "unreachable"))
        for program, message in variants:
            with self.subTest(message=message), self.assertRaisesRegex(
                rsa.CapabilityError, message
            ):
                rsa.validate_program(program, self.policy)

    def test_worker_protocol_distinguishes_domain_reject_from_runtime_failure(self) -> None:
        pass_response = self.worker_response(make_valid_record())
        self.assertEqual(
            rsa._validate_domain_worker_response(pass_response)["outcome"], "PASS"
        )
        reject_record = required_semantic_cases()[1][1]
        reject_response = self.worker_response(reject_record)
        checked = rsa._validate_domain_worker_response(reject_response)
        self.assertEqual(checked["outcome"], "REJECT")
        self.assertEqual(checked["rejection_code"], "SAMPLING_PLAN_NOT_FROZEN")
        tampered = copy.deepcopy(reject_response)
        tampered["rejection_code"] = "UNREVIEWED_DYNAMIC_CODE"
        with self.assertRaisesRegex(rsa.CapabilityError, "outside closed set"):
            rsa._validate_domain_worker_response(tampered)
        with self.assertRaisesRegex(rsa.CapabilityError, "fail closed"):
            rsa._decode_worker_response(
                1,
                b'{"ok":false,"error":"unexpected runtime error"}\n',
                b"runtime failed",
                "worker",
            )

    def test_manifest_bound_pass_and_reject_report_is_exact(self) -> None:
        shadow, responses = self.materialize_package()
        with mock.patch.object(rsa, "run_case", side_effect=responses):
            accepted = rsa.validate_shadow_acceptance(
                shadow_root=self.root,
                shadow=shadow,
                policy_path=POLICY,
                runner_path=RUNNER,
                policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )
        self.assertTrue(accepted["local_deterministic_domain_gate_acceptance_pass"])
        self.assertEqual(accepted["pass_case_count"], 1)
        self.assertEqual(
            accepted["reject_case_count"],
            len(rsa.REQUIRED_ACCEPTANCE_REJECTION_CODES),
        )
        self.assertFalse(accepted["natural_language_speech_act_inference_proven"])
        self.assertFalse(accepted["semantic_truth_of_human_labels_proven"])
        for key in (
            "runtime_authority", "deployment_authority", "freeze_authority",
            "external_action_authority",
        ):
            self.assertFalse(accepted[key])

    def test_expected_outcome_hash_and_rejection_code_tamper_fail(self) -> None:
        shadow, responses = self.materialize_package()
        variants = []
        wrong_hash = copy.deepcopy(shadow)
        wrong_hash["acceptance_cases"][0]["expected_result_sha256"] = "f" * 64
        variants.append((wrong_hash, "result hash mismatch"))
        wrong_code = copy.deepcopy(shadow)
        first_code = wrong_code["acceptance_cases"][1]["expected_rejection_code"]
        second_code = wrong_code["acceptance_cases"][2]["expected_rejection_code"]
        wrong_code["acceptance_cases"][1]["expected_rejection_code"] = second_code
        wrong_code["acceptance_cases"][2]["expected_rejection_code"] = first_code
        variants.append((wrong_code, "rejection code mismatch"))
        wrong_outcome = copy.deepcopy(shadow)
        wrong_outcome["acceptance_cases"][1]["expected_outcome"] = "PASS"
        variants.append((wrong_outcome, "key mismatch"))
        extra = copy.deepcopy(shadow)
        extra["acceptance_cases"][1]["expected_result_sha256"] = "0" * 64
        variants.append((extra, "key mismatch"))
        for changed, message in variants:
            with self.subTest(message=message), mock.patch.object(
                rsa, "run_case", side_effect=list(responses)
            ), self.assertRaisesRegex(rsa.CapabilityError, message):
                rsa.validate_shadow_acceptance(
                    shadow_root=self.root,
                    shadow=changed,
                    policy_path=POLICY,
                    runner_path=RUNNER,
                    policy_snapshot=self.policy_snapshot,
                    runner_snapshot=self.runner_snapshot,
                )

    def test_required_rejection_coverage_cannot_be_omitted(self) -> None:
        shadow, responses = self.materialize_package()
        shadow["acceptance_cases"] = shadow["acceptance_cases"][:-1]
        with mock.patch.object(
            rsa, "run_case", side_effect=responses
        ), self.assertRaisesRegex(rsa.CapabilityError, "missing required"):
            rsa.validate_shadow_acceptance(
                shadow_root=self.root,
                shadow=shadow,
                policy_path=POLICY,
                runner_path=RUNNER,
                policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )

    def test_duplicate_json_and_program_keys_rejected(self) -> None:
        duplicate = b'{"schema_version":"x","schema_version":"y"}\n'
        identity = (
            1, 2, stat.S_IFREG | 0o600, 1, os.getuid(), os.getgid(),
            len(duplicate), 0, 0,
        )
        snapshot = rsa.Snapshot(
            duplicate, rsa.sha256_bytes(duplicate), identity, "memory"
        )
        with self.assertRaisesRegex(rsa.CapabilityError, "duplicate JSON key"):
            rsa.canonical_load_snapshot(snapshot, "duplicate")
        program = copy.deepcopy(self.program)
        program["extra"] = True
        with self.assertRaisesRegex(rsa.CapabilityError, "key mismatch"):
            rsa.validate_program(program, self.policy)

    def test_executable_suffixes_modes_and_file_kinds_rejected(self) -> None:
        for suffix in (".py", ".pyc", ".so", ".dylib", ".exe"):
            path = self.root / f"artifact{suffix}"
            write_bytes(path, b"x")
            shadow = self.base_shadow()
            shadow["entries"].append({
                "path": path.name,
                "sha256": self.snapshot(path).sha256,
                "role": "ir-test-program",
            })
            with self.subTest(suffix=suffix), self.assertRaisesRegex(
                rsa.CapabilityError, "suffix"
            ):
                rsa.build_static_reports(
                    shadow_root=self.root, shadow=shadow, policy_path=POLICY
                )
        symlink = self.root / "link.json"
        symlink.symlink_to(self.program_path)
        with self.assertRaises(rsa.CapabilityError):
            rsa.read_once_regular(symlink, "symlink", 1000)
        hardlink = self.root / "hard.json"
        os.link(self.program_path, hardlink)
        with self.assertRaisesRegex(rsa.CapabilityError, "hardlinked"):
            rsa.read_once_regular(hardlink, "hardlink", 10000)
        hardlink.unlink()
        os.chmod(self.fixture_path, 0o755)
        with self.assertRaisesRegex(rsa.CapabilityError, "executable mode"):
            rsa.build_static_reports(
                shadow_root=self.root,
                shadow=self.base_shadow(),
                policy_path=POLICY,
            )
        os.chmod(self.fixture_path, 0o644)

    def test_profile_is_exact_inline_template_without_broad_mach_rule(self) -> None:
        writable = self.root / "runtime"
        profile = rsa._sandbox_profile(
            output_dir=writable,
            probe_root=self.root,
            runtime=rsa.TRUSTED_PYTHON,
        )
        expected = rsa.SANDBOX_PROFILE_TEMPLATE.format(
            runtime=rsa._sbpl_literal(rsa.TRUSTED_PYTHON),
            python_home=rsa._sbpl_literal(rsa.TRUSTED_PYTHON_HOME),
            output_dir=rsa._sbpl_literal(writable),
            probe_root=rsa._sbpl_literal(self.root),
        )
        self.assertEqual(profile, expected)
        self.assertNotIn("mach-lookup", profile)
        self.assertNotIn("staged", profile)

    def test_opened_unlinked_fd_ignores_same_name_substitution(self) -> None:
        staged = self.root / "fd-stage"
        staged.mkdir(mode=0o700)
        original = b"trusted opened bytes\n"
        fd = rsa._open_verified_unlinked_bytes(
            staged, "request.json", original, "FD race test"
        )
        replacement = staged / "request.json"
        write_bytes(replacement, b"attacker replacement\n")
        try:
            snapshot = rsa._snapshot_open_fd(
                fd, "unlinked FD", 1024, "test-fd", allowed_nlinks=(0,)
            )
            self.assertEqual(snapshot.data, original)
            self.assertEqual(os.fstat(fd).st_nlink, 0)
        finally:
            os.close(fd)

    def test_xcode_runtime_tcb_and_residual_nonclaims_are_bound(self) -> None:
        tcb = rsa.runtime_tcb_document(self.runner_snapshot)
        runtime = tcb["python_runtime"]
        self.assertEqual(runtime["anchor"], "/Applications/Xcode.app")
        self.assertEqual(runtime["path"], str(rsa.TRUSTED_PYTHON))
        for row in runtime["anchor_to_runtime_security_chain"]:
            self.assertEqual(row["uid"], 0)
            self.assertEqual(int(row["mode"], 8) & 0o022, 0)
        self.assertFalse(tcb["same_uid_concurrent_mutation_resistance_proven"])
        self.assertFalse(tcb["full_dynamic_library_and_host_runtime_closure_proven"])

    def test_loaded_module_closure_tamper_is_rejected(self) -> None:
        observation = self.runtime_observation()
        self.assertEqual(rsa._validate_runtime_observation(observation), observation)
        tampered = copy.deepcopy(observation)
        tampered["loaded_module_files"][0]["sha256"] = "f" * 64
        with self.assertRaisesRegex(rsa.CapabilityError, "hash/length mismatch"):
            rsa._validate_runtime_observation(tampered)

    def test_policy_contract_and_fixed_ceilings_cannot_expand(self) -> None:
        self.assertEqual(
            self.policy["domain_gate"]["rejection_codes"],
            sorted(rsa.DOMAIN_REJECTION_CODES),
        )
        self.assertEqual(
            self.policy["domain_gate"]["required_acceptance_rejection_codes"],
            sorted(rsa.REQUIRED_ACCEPTANCE_REJECTION_CODES),
        )
        for mutation, message in (
            (lambda value: value["limits"].update({"max_nodes": 257}), "fixed ceilings"),
            (
                lambda value: value["domain_gate"]["rejection_codes"].append(
                    "DYNAMIC_REJECTION"
                ),
                "domain Gate contract",
            ),
        ):
            document = rsa.canonical_load_snapshot(self.policy_snapshot, "policy")
            mutation(document)
            data = rsa.canonical_text(document).encode("utf-8")
            identity = list(self.policy_snapshot.stat_identity)
            identity[6] = len(data)
            snapshot = rsa.Snapshot(
                data, rsa.sha256_bytes(data), tuple(identity), "memory"
            )
            with self.subTest(message=message), self.assertRaisesRegex(
                rsa.CapabilityError, message
            ):
                rsa.load_policy_snapshot(snapshot)

    def test_manifest_case_node_total_input_and_aggregate_caps(self) -> None:
        too_many = self.base_shadow()
        too_many["entries"] = [
            {
                "path": f"f-{index}.json",
                "sha256": self.policy_snapshot.sha256,
                "role": "fixture",
            }
            for index in range(self.policy["limits"]["max_manifest_entries"] + 1)
        ]
        with self.assertRaisesRegex(rsa.CapabilityError, "fixed limit"):
            rsa._entry_map(self.root, too_many, self.policy, {})

        oversized_program = copy.deepcopy(self.program)
        oversized_program["nodes"] = [
            {"id": f"n{index}", "op": "INPUT"}
            for index in range(self.policy["limits"]["max_nodes"] + 1)
        ]
        with self.assertRaisesRegex(rsa.CapabilityError, "count invalid"):
            rsa.validate_program(oversized_program, self.policy)

        shadow, responses = self.materialize_package()
        shadow["acceptance_cases"] = [
            copy.deepcopy(shadow["acceptance_cases"][0])
            for _ in range(self.policy["limits"]["max_acceptance_cases"] + 1)
        ]
        with mock.patch.object(
            rsa, "run_case", side_effect=responses
        ), self.assertRaisesRegex(rsa.CapabilityError, "fixed limit"):
            rsa.validate_shadow_acceptance(
                shadow_root=self.root,
                shadow=shadow,
                policy_path=POLICY,
                runner_path=RUNNER,
                policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )
        shadow, responses = self.materialize_package()
        with mock.patch.object(
            rsa.time, "monotonic", side_effect=[0, 61]
        ), self.assertRaisesRegex(rsa.CapabilityError, "aggregate acceptance wall timeout"):
            rsa.validate_shadow_acceptance(
                shadow_root=self.root,
                shadow=shadow,
                policy_path=POLICY,
                runner_path=RUNNER,
                policy_snapshot=self.policy_snapshot,
                runner_snapshot=self.runner_snapshot,
            )

    def test_path_uri_module_and_operator_strings_remain_inert_data(self) -> None:
        payload = (
            "/etc/passwd file:///etc/passwd subprocess eval CAS_GET "
            "PYTHON_CALLBACK"
        )
        record = make_valid_record(payload)
        result = rsa.validate_opportunity_record(record, PARENT_CANDIDATE_SHA256)
        self.assertEqual(result["record"]["observation_lane"]["source_payload"], payload)

    def test_read_once_detects_opened_object_mutation(self) -> None:
        before = os.stat(self.program_path)
        changed = mock.Mock(
            st_dev=before.st_dev,
            st_ino=before.st_ino,
            st_mode=before.st_mode,
            st_nlink=before.st_nlink,
            st_uid=before.st_uid,
            st_gid=before.st_gid,
            st_size=before.st_size + 1,
            st_mtime_ns=before.st_mtime_ns,
            st_ctime_ns=before.st_ctime_ns,
        )
        original_fstat = os.fstat
        calls = 0

        def fstat(fd: int):
            nonlocal calls
            calls += 1
            return original_fstat(fd) if calls == 1 else changed

        with mock.patch.object(
            rsa.os, "fstat", side_effect=fstat
        ), self.assertRaisesRegex(rsa.CapabilityError, "mutated"):
            rsa.read_once_regular(self.program_path, "mutating", 10000)

    def test_cas_roundtrip_corruption_exclusive_create_and_prewrite_quota(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = rsa.canonical_bytes({"safe": True})
            flags_seen = []
            original_open = rsa.os.open

            def tracked_open(path, flags, *args, **kwargs):
                if flags & os.O_CREAT:
                    flags_seen.append(flags)
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(rsa.os, "open", side_effect=tracked_open):
                digest = rsa.cas_put_bytes(root, data, self.policy["limits"])
            self.assertEqual(
                rsa.cas_get_bytes(root, digest, self.policy["limits"]), data
            )
            self.assertTrue(any(flags & os.O_EXCL for flags in flags_seen))
            target = root / digest[:2] / digest[2:]
            os.chmod(target, 0o600)
            target.write_bytes(b"corrupt")
            with self.assertRaisesRegex(rsa.CapabilityError, "digest mismatch"):
                rsa.cas_get_bytes(root, digest, self.policy["limits"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            limits = dict(self.policy["limits"])
            limits["max_cas_total_bytes"] = 1
            with self.assertRaisesRegex(rsa.CapabilityError, "would exceed"):
                rsa.cas_put_bytes(root, b"two bytes", limits)
            self.assertEqual(list(root.rglob("*")), [])

    def test_structural_step_output_and_inventory_limits(self) -> None:
        with self.assertRaisesRegex(rsa.CapabilityError, "exceeds"):
            rsa.read_once_regular(self.program_path, "tiny", 1)
        policy = copy.deepcopy(self.policy)
        policy["limits"]["max_steps"] = 3
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            rsa.CapabilityError, "step"
        ):
            rsa.evaluate_program(
                self.program, self.fixture, policy, Path(temporary),
                PARENT_CANDIDATE_SHA256,
            )
        policy = copy.deepcopy(self.policy)
        policy["limits"]["max_output_bytes"] = 4
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(
            rsa.CapabilityError, "output byte"
        ):
            rsa.evaluate_program(
                self.program, self.fixture, policy, Path(temporary),
                PARENT_CANDIDATE_SHA256,
            )
        output = self.root / "quota-output"
        output.mkdir()
        write_bytes(output / "one", b"123")
        write_bytes(output / "two", b"456")
        limits = dict(self.policy["limits"])
        limits["max_output_files"] = 1
        with self.assertRaisesRegex(rsa.CapabilityError, "inventory quota"):
            rsa._output_inventory(output, limits)

    def test_host_required_sandbox_denials_pass_and_domain_reject(self) -> None:
        if os.environ.get("OTTS_REQUIRE_HOST_SANDBOX") != "1":
            self.skipTest("set OTTS_REQUIRE_HOST_SANDBOX=1 for mandatory host integration")
        passed = rsa.run_case(
            shadow_root=self.root,
            program_path=self.program_path,
            fixture_path=self.fixture_path,
            policy_path=POLICY,
            runner_path=RUNNER,
            expected_parent_candidate_sha256=PARENT_CANDIDATE_SHA256,
        )
        self.assertEqual(passed["outcome"], "PASS")
        self.assertTrue(all(
            value == "OBSERVED_DENIED"
            for value in passed["sandbox_observed_enforcement"].values()
        ))
        reject_path = self.root / "reject.json"
        reject_record = required_semantic_cases()[1][1]
        write_json(reject_path, reject_record)
        rejected = rsa.run_case(
            shadow_root=self.root,
            program_path=self.program_path,
            fixture_path=reject_path,
            policy_path=POLICY,
            runner_path=RUNNER,
            expected_parent_candidate_sha256=PARENT_CANDIDATE_SHA256,
        )
        self.assertEqual(rejected["outcome"], "REJECT")
        self.assertEqual(rejected["rejection_code"], "SAMPLING_PLAN_NOT_FROZEN")
        self.assertFalse(rejected["same_uid_concurrent_mutation_resistance_proven"])

    def test_sandbox_runtime_error_is_never_converted_to_domain_reject(self) -> None:
        with mock.patch.object(
            rsa,
            "_run_required_probes",
            side_effect=rsa.CapabilityError("sandbox unavailable"),
        ), self.assertRaisesRegex(rsa.CapabilityError, "sandbox unavailable"):
            rsa.run_case(
                shadow_root=self.root,
                program_path=self.program_path,
                fixture_path=self.fixture_path,
                policy_path=POLICY,
                runner_path=RUNNER,
                expected_parent_candidate_sha256=PARENT_CANDIDATE_SHA256,
            )

    def test_bounded_output_and_wall_timeout_kill_process_group(self) -> None:
        large = self.root / "large.log"
        write_bytes(large, b"x" * 20)
        with self.assertRaisesRegex(rsa.CapabilityError, "exceeds"):
            rsa.read_once_regular(large, "bounded", 10)

        class FakeProcess:
            pid = 424242
            calls = 0

            def wait(self, timeout=None):
                self.calls += 1
                if self.calls == 1:
                    raise subprocess.TimeoutExpired("fake", timeout)
                return -9

        staged = self.root / "staged-timeout"
        staged.mkdir(mode=0o700)
        runner_fd = rsa._open_verified_unlinked_bytes(
            staged, "runner.py", self.runner_snapshot.data, "timeout runner"
        )
        try:
            with mock.patch.object(
                rsa.subprocess, "Popen", return_value=FakeProcess()
            ) as popen, mock.patch.object(rsa.os, "killpg") as killpg:
                with self.assertRaisesRegex(rsa.CapabilityError, "process group killed"):
                    rsa._invoke_sandbox(
                        arguments=[],
                        profile="(version 1)\n",
                        cwd=self.root,
                        runner_fd=runner_fd,
                        inherited_fds=(),
                        limits=self.policy["limits"],
                        timeout=1,
                    )
                killpg.assert_called_once_with(424242, rsa.signal.SIGKILL)
                argv = popen.call_args.args[0]
                self.assertIn("-p", argv)
                self.assertNotIn("-f", argv)
                self.assertEqual(popen.call_args.kwargs["stdin"], runner_fd)
        finally:
            os.close(runner_fd)

    def test_derived_report_tamper_and_hash_bindings_fail(self) -> None:
        shadow, responses = self.materialize_package()
        for key in (
            "snapshot_ledger", "sbom", "capability_report",
            "acceptance_test_report",
        ):
            with self.subTest(key=key):
                changed = copy.deepcopy(shadow)
                path = self.root / changed[key]["path"]
                original = path.read_bytes()
                document = json.loads(original)
                document["tampered"] = True
                write_json(path, document)
                digest = self.snapshot(path).sha256
                changed[key]["sha256"] = digest
                for entry in changed["entries"]:
                    if entry["path"] == path.name:
                        entry["sha256"] = digest
                with mock.patch.object(
                    rsa, "run_case", side_effect=list(responses)
                ), self.assertRaises(rsa.CapabilityError):
                    rsa.validate_shadow_acceptance(
                        shadow_root=self.root,
                        shadow=changed,
                        policy_path=POLICY,
                        runner_path=RUNNER,
                        policy_snapshot=self.policy_snapshot,
                        runner_snapshot=self.runner_snapshot,
                    )
                path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
