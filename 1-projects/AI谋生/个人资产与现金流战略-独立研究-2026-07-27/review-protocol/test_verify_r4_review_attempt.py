from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from verify_r4_review_attempt import (
    ADVERSARIAL_SCHEMA,
    ACTION_MAPPING,
    BLIND_SCHEMA,
    CLAIM_CEILING_MAPPING,
    CONFORMANCE_SCHEMA,
    DESIGN_CLOSURE_BLOCKING_MAPPING,
    EXIT_IDENTITY_MISMATCH,
    EXIT_INVALID_RECEIPT,
    EXIT_MISSING_CHECKPOINT,
    EXIT_VALID,
    EXIT_VALID_SUCCESSOR_FAIL,
    EXTRACTED_SERIALIZATION,
    MUTABLE_PREDECESSOR_FIELDS,
    PASS_RULE,
    RAW_BYTES,
    RAW_SERIALIZATION,
    REQUEST_SCHEMA,
    REQUIRED_SUCCESSOR_FIELDS,
    REVIEWER_PERMISSIONS,
    STAGE_ORDER,
    STATE_ID_MAPPING,
    STATUS_MAPPING,
    SUCCESSOR_SCHEMA,
    artifact_ref,
    canonical_extracted_bytes,
    protocol_artifact_ref,
    raw_json_bytes,
    sha256_bytes,
    verify_attempt,
)


def empty_findings() -> dict[str, list[dict[str, str]]]:
    return {"Critical": [], "Major": [], "Minor": []}


def major_finding(finding_id: str = "M-1") -> dict[str, list[dict[str, str]]]:
    return {
        "Critical": [],
        "Major": [{"id": finding_id, "summary": "blocking test finding"}],
        "Minor": [],
    }


class AttemptFixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.blueprint = self.write_text("blueprint.md", "blueprint\n")
        self.instructions = self.write_text("AGENTS.md", "instructions\n")
        self.predecessor = {
            "schema_version": "PORTFOLIO_STATE_V1",
            "as_of": "2026-07-28T02:43:08-07:00",
            "state_id": "STATE-R4",
            "status": "R4_INDEPENDENT_REVIEW_READY",
            "claim_ceiling": "DESIGN_CANDIDATE_ONLY",
            "permissions": {
                "read_local_project": True,
                "write_workflow_candidates": False,
                "contact_real_people": False,
            },
            "primary_action": {
                "id": "PB-ACT-R4-BLIND-GENERATION",
                "effect_class": "READ_ONLY",
                "owner": "FRESH_BLIND_GENERATOR",
            },
            "objective": "Keep the portfolio governance safe and recoverable.",
            "blockers": {
                "review_admission_blocking": [],
                "design_closure_blocking": ["R4_REVIEW_PENDING"],
                "workflow_activation_blocking": ["OWNER_CONSTRAINT_REQUIRED"],
            },
            "workflow_observations": {
                "opportunity": {
                    "portfolio_activation": "BLOCKED",
                    "workflow_gates": {"local_shadow_allowed_now": False},
                }
            },
        }
        self.state = self.write_json("state.json", self.predecessor)
        self.blind_request = self.write_json(
            "blind-request.json", {"request": "blind instructions"}
        )
        self.task_class = self.write_json(
            "task-class.json", {"task_class_id": "TASK_PROJECT_RECOVERY_READ_ONLY"}
        )
        self.input_bundle = self.write_json(
            "input-bundle.json", {"input_bundle_id": "BUNDLE-R4"}
        )
        self.protocol_source = self.write_text("protocol-source.py", "# local verifier\n")
        self.historical = self.write_text("historical.md", "historical evidence\n")
        self.request_path = self.root / "request.json"
        self.blind_path = self.root / "blind.json"
        self.conformance_path = self.root / "conformance.json"
        self.adversarial_path = self.root / "adversarial.json"
        self.successor_path = self.root / "successor.json"
        self.request = self.make_request()
        self.write(self.request_path, self.request)

    def write_text(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, name: str, value: object) -> Path:
        path = self.root / name
        self.write(path, value)
        return path

    @staticmethod
    def write(path: Path, value: object) -> None:
        path.write_bytes(raw_json_bytes(value))

    def make_request(self) -> dict[str, object]:
        validator_command = "python3 -B validate_recovery_output.py"
        return {
            "schema_version": REQUEST_SCHEMA,
            "attempt_id": "ATTEMPT-R4-001",
            "serialization": RAW_SERIALIZATION,
            "extracted_serialization": EXTRACTED_SERIALIZATION,
            "stage_order": STAGE_ORDER,
            "pass_rule": PASS_RULE,
            "exact_identity": {
                "blueprint": artifact_ref(self.blueprint),
                "state": artifact_ref(self.state),
                "applicable_instructions": artifact_ref(self.instructions),
                "blind_request": artifact_ref(self.blind_request),
                "task_class": artifact_ref(self.task_class),
                "input_bundle": artifact_ref(self.input_bundle),
            },
            "protocol_artifacts": [
                {"role": "LOCAL_VERIFIER", "artifact": artifact_ref(self.protocol_source)}
            ],
            "historical_evidence": [
                {"role": "PRIOR_REVIEW", "artifact": artifact_ref(self.historical)}
            ],
            "review_scope": ["exact identity", "successor safety"],
            "required_commands": [validator_command, "shasum -a 256 bound artifacts"],
            "reviewer_identities": {
                "blind": "/root/blind-r4",
                "conformance": "/root/conformance-r4",
                "adversarial": "/root/adversarial-r4",
            },
            "reviewer_permissions": copy.deepcopy(REVIEWER_PERMISSIONS),
            "validator": {
                "command": validator_command,
                "pass_result": {
                    "exit_code": 0,
                    "classification": "EVAL_QUALIFIED_CANDIDATE_OUTPUT",
                },
            },
            "successor_contract": {
                "required_portfolio_state_fields": REQUIRED_SUCCESSOR_FIELDS,
                "status_mapping": STATUS_MAPPING,
                "mutable_predecessor_fields": MUTABLE_PREDECESSOR_FIELDS,
                "state_id_mapping": STATE_ID_MAPPING,
                "claim_ceiling_mapping": CLAIM_CEILING_MAPPING,
                "action_mapping": ACTION_MAPPING,
                "design_closure_blocking_mapping": DESIGN_CLOSURE_BLOCKING_MAPPING,
                "blocked_workflow_activation_value": "BLOCKED",
            },
        }

    def bound_identity(self) -> dict[str, str]:
        exact = self.request["exact_identity"]
        return {
            "blueprint_sha256": exact["blueprint"]["sha256"],
            "state_sha256": exact["state"]["sha256"],
            "applicable_instructions_sha256": exact["applicable_instructions"]["sha256"],
            "request_sha256": sha256_bytes(self.request_path.read_bytes()),
            "blind_request_sha256": exact["blind_request"]["sha256"],
            "task_class_sha256": exact["task_class"]["sha256"],
            "input_bundle_sha256": exact["input_bundle"]["sha256"],
        }

    def make_blind(
        self,
        verdict: str = "CANDIDATE_RECOVERY",
        tainted: bool = False,
    ) -> dict[str, object]:
        candidate = {
            "task_class_id": "TASK_PROJECT_RECOVERY_READ_ONLY",
            "input_bundle_id": "BUNDLE-R4",
            "projection": {"state_id": "STATE-R4", "note": "恢复"},
        }
        refusal = {
            "task_class_id": "TASK_PROJECT_RECOVERY_READ_ONLY",
            "qualification_status": "REFUSED",
            "reason": (
                "FAIL_TAINTED: forbidden content was accessed"
                if tainted
                else "The bound evidence cannot support a candidate."
            ),
        }
        return {
            "schema_version": BLIND_SCHEMA,
            "attempt_id": self.request["attempt_id"],
            "role": "BLIND_GENERATOR",
            "reviewer_task_identity": self.request["reviewer_identities"]["blind"],
            "verdict": verdict,
            "candidate_output": candidate if verdict == "CANDIDATE_RECOVERY" else None,
            "refusal_output": refusal if verdict == "REFUSAL" else None,
            "attestation": {
                "bound_identity": self.bound_identity(),
                "commands_used": ["read bound inputs"],
                "forbidden_content_opened_or_hashed": tainted,
                "file_modifications": False,
                "external_actions": False,
                "findings": empty_findings(),
            },
        }

    def make_conformance(
        self,
        blind: dict[str, object],
        verdict: str = "PASS",
        findings: dict[str, list[dict[str, str]]] | None = None,
    ) -> dict[str, object]:
        if findings is None:
            findings = empty_findings() if verdict == "PASS" else major_finding()
        validator_result = (
            copy.deepcopy(self.request["validator"]["pass_result"])
            if verdict == "PASS"
            else {"exit_code": 4, "classification": "WRONG_STATE_PROJECTION"}
        )
        return {
            "schema_version": CONFORMANCE_SCHEMA,
            "attempt_id": self.request["attempt_id"],
            "role": "CONFORMANCE_REVIEWER",
            "reviewer_task_identity": self.request["reviewer_identities"]["conformance"],
            "blind_artifact": protocol_artifact_ref(self.blind_path),
            "extracted_payload": {
                "kind": "candidate_output",
                "sha256": sha256_bytes(
                    canonical_extracted_bytes(blind["candidate_output"])
                ),
                "serialization": EXTRACTED_SERIALIZATION,
            },
            "bound_identity": self.bound_identity(),
            "validator": {
                "command": self.request["validator"]["command"],
                "result": validator_result,
            },
            "verdict": verdict,
            "findings": findings,
        }

    def make_adversarial(
        self,
        verdict: str = "PASS",
        findings: dict[str, list[dict[str, str]]] | None = None,
    ) -> dict[str, object]:
        if findings is None:
            findings = empty_findings() if verdict == "PASS" else major_finding("A-M-1")
        return {
            "schema_version": ADVERSARIAL_SCHEMA,
            "attempt_id": self.request["attempt_id"],
            "role": "ADVERSARIAL_REVIEWER",
            "reviewer_task_identity": self.request["reviewer_identities"]["adversarial"],
            "blind_artifact": protocol_artifact_ref(self.blind_path),
            "conformance_receipt": protocol_artifact_ref(self.conformance_path),
            "bound_identity": self.bound_identity(),
            "verdict": verdict,
            "findings": findings,
        }

    def artifact_chain(self, include_conformance: bool, include_adversarial: bool) -> dict[str, object]:
        return {
            "blind": protocol_artifact_ref(self.blind_path),
            "conformance": (
                protocol_artifact_ref(self.conformance_path) if include_conformance else None
            ),
            "adversarial": (
                protocol_artifact_ref(self.adversarial_path) if include_adversarial else None
            ),
        }

    def make_portfolio_successor(
        self,
        overall: str,
        short_circuit: dict[str, object],
        artifacts: dict[str, object],
    ) -> dict[str, object]:
        state = copy.deepcopy(self.predecessor)
        state.update(
            {
                "predecessor_state_sha256": self.request["exact_identity"]["state"]["sha256"],
                "as_of": "2026-07-28T03:00:00-07:00",
                "state_id": STATE_ID_MAPPING[overall],
                "status": STATUS_MAPPING[overall],
                "claim_ceiling": CLAIM_CEILING_MAPPING[overall],
                "review_outcome": {
                    "attempt_id": self.request["attempt_id"],
                    "overall_verdict": overall,
                    "short_circuit": short_circuit,
                    "artifacts": copy.deepcopy(artifacts),
                },
                "permissions": copy.deepcopy(self.predecessor["permissions"]),
                "workflow_activation": "BLOCKED",
                "blockers": {
                    **copy.deepcopy(self.predecessor["blockers"]),
                    "design_closure_blocking": copy.deepcopy(
                        DESIGN_CLOSURE_BLOCKING_MAPPING[overall]
                    ),
                },
            }
        )
        action = copy.deepcopy(ACTION_MAPPING[overall])
        state["primary_action"] = copy.deepcopy(action)
        state["next_action"] = copy.deepcopy(action)
        return state

    def make_successor(
        self,
        overall: str,
        short_circuit: dict[str, object],
        include_conformance: bool,
        include_adversarial: bool,
    ) -> dict[str, object]:
        artifacts = self.artifact_chain(include_conformance, include_adversarial)
        return {
            "schema_version": SUCCESSOR_SCHEMA,
            "attempt_id": self.request["attempt_id"],
            "role": "SUCCESSOR",
            "artifacts": artifacts,
            "bound_identity": self.bound_identity(),
            "short_circuit": short_circuit,
            "overall_verdict": overall,
            "portfolio_state_successor": self.make_portfolio_successor(
                overall, short_circuit, artifacts
            ),
        }

    def materialize_pass(self) -> None:
        blind = self.make_blind()
        self.write(self.blind_path, blind)
        self.write(self.conformance_path, self.make_conformance(blind))
        self.write(self.adversarial_path, self.make_adversarial())
        self.write(
            self.successor_path,
            self.make_successor(
                "PASS",
                {"active": False, "stage": None, "reason": None},
                True,
                True,
            ),
        )


class R4AttemptVerifierTests(unittest.TestCase):
    def fixture(self, directory: str) -> AttemptFixture:
        return AttemptFixture(Path(directory))

    def test_generic_and_protocol_serializations_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            blind = fixture.make_blind()
            fixture.write(fixture.blind_path, blind)
            self.assertEqual(artifact_ref(fixture.blueprint)["serialization"], RAW_BYTES)
            self.assertEqual(
                protocol_artifact_ref(fixture.blind_path)["serialization"],
                RAW_SERIALIZATION,
            )

    def test_complete_pass_and_commit_bytes_have_returned_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
            successor_state = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )["portfolio_state_successor"]
            committed = Path(directory) / "committed-state.json"
            committed.write_bytes(raw_json_bytes(successor_state))
            committed_hash = sha256_bytes(committed.read_bytes())
        self.assertEqual(code, EXIT_VALID)
        self.assertEqual(result["classification"], "VALID_SUCCESSOR_PASS")
        self.assertEqual(result["portfolio_state_successor_sha256"], committed_hash)

    def test_blind_refusal_true_short_circuit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind("REFUSAL"))
            short = {"active": True, "stage": "BLIND_GENERATION", "reason": "BLIND_REFUSAL"}
            fixture.write(
                fixture.successor_path,
                fixture.make_successor("FAIL", short, False, False),
            )
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                None,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_VALID_SUCCESSOR_FAIL)
        self.assertEqual(result["classification"], "VALID_SUCCESSOR_FAIL")

    def test_tainted_refusal_derives_blind_tainted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind("REFUSAL", tainted=True))
            short = {"active": True, "stage": "BLIND_GENERATION", "reason": "BLIND_TAINTED"}
            fixture.write(
                fixture.successor_path,
                fixture.make_successor("FAIL", short, False, False),
            )
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                None,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_VALID_SUCCESSOR_FAIL)
        self.assertEqual(result["overall_verdict"], "FAIL")

    def test_conformance_fail_short_circuit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            blind = fixture.make_blind()
            fixture.write(fixture.blind_path, blind)
            fixture.write(fixture.conformance_path, fixture.make_conformance(blind, "FAIL"))
            short = {
                "active": True,
                "stage": "CONFORMANCE_REVIEW",
                "reason": "CONFORMANCE_FAIL",
            }
            fixture.write(
                fixture.successor_path,
                fixture.make_successor("FAIL", short, True, False),
            )
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_VALID_SUCCESSOR_FAIL)
        self.assertEqual(result["overall_verdict"], "FAIL")

    def test_candidate_blind_only_is_valid_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind())
            code, result = verify_attempt(fixture.request_path, fixture.blind_path, None)
        self.assertEqual(code, EXIT_VALID)
        self.assertEqual(result["classification"], "VALID_CHECKPOINT")
        self.assertEqual(result["last_verified_stage"], "BLIND_GENERATION")
        self.assertFalse(result["authority_granted"])

    def test_blind_refusal_without_successor_is_valid_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind("REFUSAL"))
            code, result = verify_attempt(fixture.request_path, fixture.blind_path, None)
        self.assertEqual(code, EXIT_VALID)
        self.assertEqual(result["classification"], "VALID_CHECKPOINT")
        self.assertEqual(result["last_verified_stage"], "BLIND_GENERATION")
        self.assertFalse(result["authority_granted"])

    def test_candidate_successor_missing_conformance_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind())
            short = {
                "active": True,
                "stage": "CONFORMANCE_REVIEW",
                "reason": "CONFORMANCE_FAIL",
            }
            fixture.write(
                fixture.successor_path,
                fixture.make_successor("FAIL", short, False, False),
            )
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                None,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_MISSING_CHECKPOINT)
        self.assertEqual(result["classification"], "MISSING_CHECKPOINT")

    def test_candidate_pass_missing_adversarial_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            blind = fixture.make_blind()
            fixture.write(fixture.blind_path, blind)
            fixture.write(fixture.conformance_path, fixture.make_conformance(blind))
            short = {"active": False, "stage": None, "reason": None}
            fixture.write(
                fixture.successor_path,
                fixture.make_successor("FAIL", short, True, False),
            )
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_MISSING_CHECKPOINT)
        self.assertEqual(result["classification"], "MISSING_CHECKPOINT")

    def test_request_bound_historical_evidence_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind())
            fixture.historical.write_text("drifted historical evidence\n", encoding="utf-8")
            code, result = verify_attempt(
                fixture.request_path, fixture.blind_path, None
            )
        self.assertEqual(code, EXIT_IDENTITY_MISMATCH)
        self.assertEqual(result["classification"], "IDENTITY_MISMATCH")

    def test_blind_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            blind = fixture.make_blind()
            blind["candidate_output"]["projection"]["state_id"] = "DRIFTED"
            fixture.write(fixture.blind_path, blind)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
            )
        self.assertEqual(code, EXIT_IDENTITY_MISMATCH)
        self.assertEqual(result["classification"], "IDENTITY_MISMATCH")

    def test_wrong_bound_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            blind = fixture.make_blind()
            fixture.write(fixture.blind_path, blind)
            conformance = fixture.make_conformance(blind)
            conformance["bound_identity"]["state_sha256"] = "0" * 64
            fixture.write(fixture.conformance_path, conformance)
            code, result = verify_attempt(
                fixture.request_path, fixture.blind_path, fixture.conformance_path
            )
        self.assertEqual(code, EXIT_IDENTITY_MISMATCH)
        self.assertEqual(result["classification"], "IDENTITY_MISMATCH")

    def test_pass_with_major_is_invalid_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            blind = fixture.make_blind()
            fixture.write(fixture.blind_path, blind)
            fixture.write(
                fixture.conformance_path,
                fixture.make_conformance(blind, "PASS", major_finding("PASS-MAJOR")),
            )
            code, result = verify_attempt(
                fixture.request_path, fixture.blind_path, fixture.conformance_path
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertEqual(result["classification"], "INVALID_RECEIPT")

    def test_successor_wrong_derived_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            successor = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )
            successor["overall_verdict"] = "FAIL"
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertIn("overall_verdict", result["error"])

    def test_byte_length_and_protocol_serialization_mismatch(self) -> None:
        for field, value, expected_code in (
            ("byte_length", 1, EXIT_IDENTITY_MISMATCH),
            ("serialization", RAW_BYTES, EXIT_INVALID_RECEIPT),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                blind = fixture.make_blind()
                fixture.write(fixture.blind_path, blind)
                conformance = fixture.make_conformance(blind)
                conformance["blind_artifact"][field] = value
                fixture.write(fixture.conformance_path, conformance)
                code, _ = verify_attempt(
                    fixture.request_path, fixture.blind_path, fixture.conformance_path
                )
            self.assertEqual(code, expected_code)

    def test_permission_expansion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            successor = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )
            successor["portfolio_state_successor"]["permissions"][
                "write_workflow_candidates"
            ] = True
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertIn("permission expansion", result["error"])

    def test_objective_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            successor = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )
            successor["portfolio_state_successor"]["objective"] = "Mutated objective"
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertIn("immutable predecessor field changed: objective", result["error"])

    def test_wrong_blockers_are_rejected(self) -> None:
        mutations = (
            ("design_closure_blocking", ["WRONG_DESIGN_BLOCKER"]),
            ("workflow_activation_blocking", ["MUTATED_WORKFLOW_BLOCKER"]),
        )
        for blocker, value in mutations:
            with self.subTest(blocker=blocker), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                fixture.materialize_pass()
                successor = fixture.make_successor(
                    "PASS", {"active": False, "stage": None, "reason": None}, True, True
                )
                successor["portfolio_state_successor"]["blockers"][blocker] = value
                fixture.write(fixture.successor_path, successor)
                code, result = verify_attempt(
                    fixture.request_path,
                    fixture.blind_path,
                    fixture.conformance_path,
                    fixture.adversarial_path,
                    fixture.successor_path,
                )
            self.assertEqual(code, EXIT_INVALID_RECEIPT)
            self.assertTrue(
                "blocker" in result["error"] or "blocking" in result["error"]
            )

    def test_wrong_primary_or_next_action_is_rejected(self) -> None:
        for field in ("primary_action", "next_action"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                fixture.materialize_pass()
                successor = fixture.make_successor(
                    "PASS", {"active": False, "stage": None, "reason": None}, True, True
                )
                successor["portfolio_state_successor"][field]["owner"] = "WORKFLOW_AGENT"
                fixture.write(fixture.successor_path, successor)
                code, result = verify_attempt(
                    fixture.request_path,
                    fixture.blind_path,
                    fixture.conformance_path,
                    fixture.adversarial_path,
                    fixture.successor_path,
                )
            self.assertEqual(code, EXIT_INVALID_RECEIPT)
            self.assertIn("action mismatch", result["error"])

    def test_invalid_or_earlier_as_of_is_rejected(self) -> None:
        for value, expected_error in (
            ("2026-07-28 03:00:00", "strict RFC3339"),
            ("2026-07-28T01:00:00-07:00", "precedes predecessor"),
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                fixture.materialize_pass()
                successor = fixture.make_successor(
                    "PASS", {"active": False, "stage": None, "reason": None}, True, True
                )
                successor["portfolio_state_successor"]["as_of"] = value
                fixture.write(fixture.successor_path, successor)
                code, result = verify_attempt(
                    fixture.request_path,
                    fixture.blind_path,
                    fixture.conformance_path,
                    fixture.adversarial_path,
                    fixture.successor_path,
                )
            self.assertEqual(code, EXIT_INVALID_RECEIPT)
            self.assertIn(expected_error, result["error"])

    def test_state_id_and_claim_ceiling_mappings_are_rejected(self) -> None:
        for field in ("state_id", "claim_ceiling"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                fixture = self.fixture(directory)
                fixture.materialize_pass()
                successor = fixture.make_successor(
                    "PASS", {"active": False, "stage": None, "reason": None}, True, True
                )
                successor["portfolio_state_successor"][field] = "WRONG"
                fixture.write(fixture.successor_path, successor)
                code, result = verify_attempt(
                    fixture.request_path,
                    fixture.blind_path,
                    fixture.conformance_path,
                    fixture.adversarial_path,
                    fixture.successor_path,
                )
            self.assertEqual(code, EXIT_INVALID_RECEIPT)
            self.assertIn(f"{field} mismatch", result["error"])

    def test_status_mapping_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            successor = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )
            successor["portfolio_state_successor"]["status"] = "R4_REVIEW_FAIL"
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertIn("status mismatch", result["error"])

    def test_predecessor_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.materialize_pass()
            successor = fixture.make_successor(
                "PASS", {"active": False, "stage": None, "reason": None}, True, True
            )
            successor["portfolio_state_successor"]["predecessor_state_sha256"] = "0" * 64
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                fixture.conformance_path,
                fixture.adversarial_path,
                fixture.successor_path,
            )
        self.assertEqual(code, EXIT_IDENTITY_MISMATCH)
        self.assertIn("predecessor_state_sha256", result["error"])

    def test_fail_state_cannot_activate_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            fixture = self.fixture(directory)
            fixture.write(fixture.blind_path, fixture.make_blind("REFUSAL"))
            short = {"active": True, "stage": "BLIND_GENERATION", "reason": "BLIND_REFUSAL"}
            successor = fixture.make_successor("FAIL", short, False, False)
            successor["portfolio_state_successor"]["workflow_activation"] = "ACTIVE"
            fixture.write(fixture.successor_path, successor)
            code, result = verify_attempt(
                fixture.request_path,
                fixture.blind_path,
                None,
                successor_path=fixture.successor_path,
            )
        self.assertEqual(code, EXIT_INVALID_RECEIPT)
        self.assertIn("workflow activation", result["error"])


if __name__ == "__main__":
    unittest.main()
