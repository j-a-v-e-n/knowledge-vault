from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "08-活动状态.json"
VALIDATOR_PATH = ROOT / "09-校验活动状态.py"

SPEC = importlib.util.spec_from_file_location("active_state_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ActiveStateValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = VALIDATOR.loads_json_strict(STATE_PATH.read_text(encoding="utf-8"))
        assert isinstance(self.state, dict)
        self.now = datetime.fromisoformat(self.state["as_of"]) + timedelta(hours=1)

    def errors_for(self, state: dict, *, now: datetime | None = None) -> list[str]:
        return VALIDATOR.validate(state, now=now or self.now)

    def assert_detected(self, state: dict, needle: str, *, now: datetime | None = None) -> None:
        errors = self.errors_for(state, now=now)
        self.assertTrue(
            any(needle in error for error in errors),
            msg=f"expected {needle!r}; errors were: {errors}",
        )

    def ca_r2_bindings(self) -> list[dict[str, str]]:
        receipt_parent = ROOT / "evidence"
        return [
            {
                "path": os.path.relpath(path, start=receipt_parent),
                "sha256": VALIDATOR.sha256_file(path),
            }
            for path in sorted(VALIDATOR.ca_r2_candidate_paths())
        ]

    def ca_r2_receipt(self) -> dict:
        return {
            "schema_version": VALIDATOR.EXPECTED_CA_R2_SCHEMA_VERSION,
            "review_id": VALIDATOR.EXPECTED_CA_R2_REVIEW_ID,
            "recorded_at": "2026-07-27T21:54:10-07:00",
            "reviewer_agent_identity": VALIDATOR.EXPECTED_CA_R2_REVIEWER_IDENTITY,
            "reviewer_role": "independent_read_only_subagent",
            "reviewer_modified_candidate": False,
            "verdict": "PASS",
            "severity_counts": copy.deepcopy(
                VALIDATOR.EXPECTED_CA_R2_SEVERITY_COUNTS
            ),
            "candidate_bindings": self.ca_r2_bindings(),
            "reviewed_properties": sorted(
                VALIDATOR.EXPECTED_CA_R2_REVIEWED_PROPERTIES
            ),
            "external_action_status": "BLOCKED_NOT_AUTHORIZED",
            "missing_external_bindings": sorted(
                VALIDATOR.EXPECTED_CA_R2_MISSING_EXTERNAL_BINDINGS
            ),
            "claim_boundary": VALIDATOR.EXPECTED_CA_R2_CLAIM_BOUNDARY,
        }

    def sender_profile_record(self) -> dict:
        path = ROOT / VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
        record = VALIDATOR.loads_json_strict(path.read_text(encoding="utf-8"))
        assert isinstance(record, dict)
        return record

    def successor_candidate_bindings(self) -> list[dict[str, str]]:
        receipt_parent = ROOT / "evidence"
        return [
            {
                "path": os.path.relpath(path, start=receipt_parent),
                "sha256": VALIDATOR.sha256_file(path),
            }
            for path in sorted(VALIDATOR.ca_precontact_successor_candidate_paths())
        ]

    def successor_review(self) -> dict:
        return {
            "schema_version": (
                VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_SCHEMA_VERSION
            ),
            "review_id": VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_REVIEW_ID,
            "recorded_at": "2026-07-28T00:05:00-07:00",
            "reviewer_agent_identity": (
                VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_REVIEWER_IDENTITY
            ),
            "reviewer_role": "independent_read_only_subagent",
            "reviewer_modified_candidate": False,
            "verdict": "PASS",
            "severity_counts": copy.deepcopy(
                VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_SEVERITY_COUNTS
            ),
            "candidate_bindings": self.successor_candidate_bindings(),
            "reviewed_properties": sorted(
                VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_REVIEWED_PROPERTIES
            ),
            "external_action_status": "REJECTED_PRECONTACT_TERMINAL_NO_AUTHORITY",
            "missing_external_bindings": sorted(
                VALIDATOR.REQUIRED_CA_MISSING_BINDINGS
            ),
            "claim_boundary": (
                VALIDATOR.EXPECTED_CA_PRECONTACT_SUCCESSOR_CLAIM_BOUNDARY
            ),
        }

    def rejected_state(self, review: dict | None = None) -> dict:
        review = copy.deepcopy(review or self.successor_review())
        precursor_path = (
            ROOT
            / VALIDATOR.EXPECTED_CA_PRETRANSITION_STATE_SNAPSHOT_BINDING["path"]
        )
        state = VALIDATOR.loads_json_strict(
            precursor_path.read_text(encoding="utf-8")
        )
        assert isinstance(state, dict)
        state["as_of"] = "2026-07-28T00:10:00-07:00"
        state["freshness_policy"]["refresh_due_at"] = "2026-07-31T00:10:00-07:00"
        opportunity = next(
            stream
            for stream in state["workstreams"]
            if stream["id"] == "opportunity_to_transaction"
        )
        review_raw = json.dumps(
            review, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        opportunity["independent_reviews"]["ca012650_internal_candidate"] = {
            "path": VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
                "ca012650_internal_candidate"
            ],
            "sha256": hashlib.sha256(review_raw).hexdigest(),
            "verdict": "PASS",
        }
        opportunity["status"] = "active_internal"
        opportunity["observed_facts"] = [
            copy.deepcopy(VALIDATOR.EXPECTED_OPPORTUNITY_FIRST_FACT),
            copy.deepcopy(
                VALIDATOR.EXPECTED_OPPORTUNITY_REVIEW_FACTS[
                    "passed_precontact_rejection_successor"
                ]
            ),
            {
                "claim_class": "observed",
                "claim": VALIDATOR.EXPECTED_OPPORTUNITY_STAGE_FACT_CLAIMS[
                    "rejected_precontact"
                ],
                "evidence_locator": (
                    VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING[
                        "path"
                    ]
                ),
            },
        ]
        opportunity["unknowns"] = copy.deepcopy(
            VALIDATOR.EXPECTED_OPPORTUNITY_UNKNOWNS
        )
        opportunity["next_action"] = copy.deepcopy(
            VALIDATOR.EXPECTED_OPPORTUNITY_ACTIONS["rejected_precontact"]
        )
        opportunity["stop_conditions"] = copy.deepcopy(
            VALIDATOR.EXPECTED_OPPORTUNITY_STOP_CONDITIONS
        )
        current = opportunity["current_experiment"]
        current["internal_review_result"] = "FAIL_PRECONTACT_RECIPIENT_VALUE"
        current["internal_review_scope"] = (
            VALIDATOR.EXPECTED_CA_INTERNAL_REVIEW_SCOPES[
                "passed_precontact_rejection_successor"
            ]
        )
        current["external_action_status"] = "rejected_precontact"
        current["external_contact_authorized"] = False
        current["result_claims"] = {
            key: False for key in VALIDATOR.REQUIRED_FALSE_EXPERIMENT_RESULTS
        }
        approval = state["approval_queue"][0]
        approval.update(
            {
                "status": "rejected_precontact",
                "authorized": False,
                "ready": False,
                "executable": False,
                "authorization_consumed": False,
                "sender_account": None,
                "observation_cutoff_at": None,
                "pre_send_source_refresh": {
                    "status": "not_completed",
                    "completed_at": None,
                    "cec_status_record": None,
                    "organization_channel_record": None,
                },
                "exact_user_authorization": False,
                "missing_bindings": sorted(
                    VALIDATOR.REQUIRED_CA_MISSING_BINDINGS
                ),
                "lifecycle": {
                    "stage": "rejected_precontact",
                    "previous_stage": "blocked_missing_bindings",
                    "precontact_rejection_receipt": copy.deepcopy(
                        VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING
                    ),
                    "readiness_receipt": None,
                    "authorization_receipt": None,
                    "execution_receipt": None,
                    "observation_receipt": None,
                    "closure_receipt": None,
                },
                "claim_boundary": (
                    VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_APPROVAL_CLAIM_BOUNDARY
                ),
            }
        )
        approval.pop("sender_profile_record", None)
        return state

    def errors_for_rejected_fixture(
        self,
        state: dict,
        *,
        review: dict | None = None,
        now: datetime | None = None,
    ) -> list[str]:
        """Exercise the full state path with an in-memory exact future receipt.

        Mutable 08 and the review itself are intentionally excluded from the r3
        candidate to avoid a hash cycle.  Until the independent reviewer writes
        the real receipt, this harness substitutes only that one absent file;
        every candidate binding and all historical evidence are still validated
        by production code against real bytes.
        """

        review = copy.deepcopy(review or self.successor_review())
        review_path = ROOT / VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
            "ca012650_internal_candidate"
        ]
        review_raw = json.dumps(
            review, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        review_sha = hashlib.sha256(review_raw).hexdigest()
        original_verify = VALIDATOR.verify_bound_file
        original_load = VALIDATOR.load_json
        original_locator = VALIDATOR.validate_evidence_locator

        def verify_override(binding: object, **kwargs: object) -> Path | None:
            label = str(kwargs.get("label", ""))
            if label == (
                "opportunity independent reviews: "
                "ca012650_internal_candidate"
            ):
                errors = kwargs["errors"]
                assert isinstance(errors, list)
                if not isinstance(binding, dict) or binding.get("path") != (
                    VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
                        "ca012650_internal_candidate"
                    ]
                ):
                    errors.append(f"{label}: synthetic review path changed")
                elif binding.get("sha256") != review_sha:
                    errors.append(f"{label}: sha256 mismatch")
                return review_path
            return original_verify(binding, **kwargs)

        def load_override(path: Path, **kwargs: object) -> dict | None:
            if path == review_path:
                return copy.deepcopy(review)
            return original_load(path, **kwargs)

        def locator_override(locator: object, **kwargs: object) -> None:
            if locator == VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
                "ca012650_internal_candidate"
            ]:
                return
            original_locator(locator, **kwargs)

        with mock.patch.object(
            VALIDATOR, "verify_bound_file", side_effect=verify_override
        ), mock.patch.object(
            VALIDATOR, "load_json", side_effect=load_override
        ), mock.patch.object(
            VALIDATOR, "validate_evidence_locator", side_effect=locator_override
        ):
            return VALIDATOR.validate(
                state,
                now=now or datetime.fromisoformat("2026-07-28T00:11:00-07:00"),
            )

    def assert_rejected_detected(
        self, state: dict, needle: str, *, review: dict | None = None
    ) -> None:
        errors = self.errors_for_rejected_fixture(state, review=review)
        self.assertTrue(
            any(needle in error for error in errors),
            msg=f"expected {needle!r}; errors were: {errors}",
        )

    def test_live_state_is_exact_successor_or_fails_closed_as_predecessor(self) -> None:
        errors = self.errors_for(self.state)
        current_review = next(
            stream
            for stream in self.state["workstreams"]
            if stream["id"] == "opportunity_to_transaction"
        )["independent_reviews"]["ca012650_internal_candidate"]
        if current_review.get("path") == VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
            "ca012650_internal_candidate"
        ]:
            self.assertEqual([], errors)
        else:
            self.assertTrue(
                any(
                    "historical r2 cannot review successor bytes" in error
                    for error in errors
                ),
                errors,
            )

    def test_exact_synthetic_successor_and_rejected_state_pass(self) -> None:
        review = self.successor_review()
        state = self.rejected_state(review)
        self.assertEqual([], self.errors_for_rejected_fixture(state, review=review))

    def test_predecessor_snapshot_cannot_pass_as_current_successor(self) -> None:
        path = ROOT / VALIDATOR.EXPECTED_CA_PRETRANSITION_STATE_SNAPSHOT_BINDING[
            "path"
        ]
        precursor = VALIDATOR.loads_json_strict(path.read_text(encoding="utf-8"))
        assert isinstance(precursor, dict)
        errors = VALIDATOR.validate(
            precursor,
            now=datetime.fromisoformat("2026-07-27T22:15:56-07:00"),
        )
        self.assertTrue(
            any("historical r2 cannot review successor bytes" in error for error in errors),
            errors,
        )

    def test_closed_schema_rejects_unknown_and_missing_fields(self) -> None:
        with self.subTest("unknown top-level"):
            state = copy.deepcopy(self.state)
            state["surprise"] = True
            self.assert_detected(state, "unknown fields")
        with self.subTest("missing approval field"):
            state = copy.deepcopy(self.state)
            del state["approval_queue"][0]["claim_boundary"]
            self.assert_detected(state, "missing fields")

    def test_authority_default_allow_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        state["authority_envelope"]["default"] = "allow"
        self.assert_detected(state, "default must deny")

    def test_truth_policy_authority_changes_are_detected(self) -> None:
        mutations = (
            ("old_documents_are_authority", True, "old_documents_are_authority"),
            ("ai_summary_is_evidence", True, "ai_summary_is_evidence"),
        )
        for key, value, needle in mutations:
            with self.subTest(key=key):
                state = copy.deepcopy(self.state)
                state["truth_policy"][key] = value
                self.assert_detected(state, needle)
        state = copy.deepcopy(self.state)
        state["truth_policy"]["required_claim_classes"].append("observed")
        self.assert_detected(state, "duplicates are forbidden")

    def test_target_and_channel_source_substitution_are_detected(self) -> None:
        with self.subTest("target"):
            state = copy.deepcopy(self.state)
            state["approval_queue"][0]["exact_target"]["public_building_id"] = (
                "Building #REPLACED"
            )
            self.assert_detected(state, "exact target changed")
        with self.subTest("channel source"):
            state = copy.deepcopy(self.state)
            state["approval_queue"][0]["channel_source"] = (
                "https://example.invalid/replacement"
            )
            self.assert_detected(state, "channel source changed")
        with self.subTest("channel"):
            state = copy.deepcopy(self.state)
            state["approval_queue"][0]["exact_channel"] = "replacement@example.invalid"
            self.assert_detected(state, "exact channel changed")

    def test_sender_profile_observation_is_exact_content_addressed_read_only_input(
        self,
    ) -> None:
        errors: list[str] = []
        observed_at = VALIDATOR.validate_sender_profile_observation(
            copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING),
            snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
            errors=errors,
        )
        self.assertEqual([], errors)
        self.assertEqual(
            datetime.fromisoformat("2026-07-27T23:20:26-07:00"), observed_at
        )

        attacks = {
            "account": (
                "account_email",
                "another@example.com",
                "authenticated account differs",
            ),
            "operation": (
                "connector_operation",
                "gmail_send_message",
                "connector operation",
            ),
            "read-only type confusion": (
                "read_only",
                1,
                "JSON boolean true",
            ),
            "draft type confusion": (
                "draft_created",
                0,
                "JSON boolean false",
            ),
            "sent": ("message_sent", True, "JSON boolean false"),
            "proposed use": (
                "proposed_use",
                "authorized_sender",
                "proposed use changed",
            ),
            "claim expansion": (
                "claim_boundary",
                "This observation authorizes sending.",
                "claim boundary differs",
            ),
            "naive observed_at": (
                "observed_at",
                "2026-07-27T23:20:26",
                "timestamp must include an offset",
            ),
            "future observed_at": (
                "observed_at",
                "2026-07-27T23:21:01-07:00",
                "timestamp is in the future",
            ),
        }
        with tempfile.TemporaryDirectory(
            prefix="validator-sender-observation-", dir="/private/tmp"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            evidence_dir = temp_root / "evidence"
            evidence_dir.mkdir()
            record_path = evidence_dir / Path(
                VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
            ).name
            for label, (key, value, needle) in attacks.items():
                with self.subTest(label=label):
                    record = self.sender_profile_record()
                    record[key] = value
                    record_path.write_text(json.dumps(record), encoding="utf-8")
                    binding = {
                        "path": f"evidence/{record_path.name}",
                        "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
                    }
                    attack_errors: list[str] = []
                    with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root), mock.patch.object(
                        VALIDATOR,
                        "EXPECTED_CA_SENDER_PROFILE_BINDING",
                        binding,
                    ):
                        VALIDATOR.validate_sender_profile_observation(
                            binding,
                            snapshot_at=datetime.fromisoformat(
                                "2026-07-27T23:21:00-07:00"
                            ),
                            errors=attack_errors,
                        )
                    self.assertTrue(
                        any(needle in error for error in attack_errors), attack_errors
                    )

            record = self.sender_profile_record()
            record["unexpected_authority"] = True
            record_path.write_text(json.dumps(record), encoding="utf-8")
            binding = {
                "path": f"evidence/{record_path.name}",
                "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
            }
            schema_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root), mock.patch.object(
                VALIDATOR, "EXPECTED_CA_SENDER_PROFILE_BINDING", binding
            ):
                VALIDATOR.validate_sender_profile_observation(
                    binding,
                    snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                    errors=schema_errors,
                )
            self.assertTrue(any("unknown fields" in error for error in schema_errors))

            record = self.sender_profile_record()
            record["observed_at"] = "2026-07-28T06:20:26+00:00"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            binding = {
                "path": f"evidence/{record_path.name}",
                "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
            }
            offset_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root), mock.patch.object(
                VALIDATOR, "EXPECTED_CA_SENDER_PROFILE_BINDING", binding
            ):
                offset_observed_at = VALIDATOR.validate_sender_profile_observation(
                    binding,
                    snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                    errors=offset_errors,
                )
            self.assertEqual([], offset_errors)
            self.assertEqual(
                datetime.fromisoformat("2026-07-27T23:20:26-07:00"),
                offset_observed_at,
            )

    def test_sender_profile_freshness_uses_real_now_and_execution_boundary(
        self,
    ) -> None:
        observed_at = datetime.fromisoformat("2026-07-27T23:20:26-07:00")
        readiness_at = observed_at + timedelta(minutes=1)
        lifecycle = {
            "readiness_recorded_at": readiness_at,
            "authorized_at": None,
            "executed_at": None,
        }
        boundary_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="request_ready",
            validation_now=observed_at
            + timedelta(hours=VALIDATOR.SENDER_PROFILE_MAX_AGE_HOURS),
            lifecycle_times=lifecycle,
            errors=boundary_errors,
        )
        self.assertEqual([], boundary_errors)

        expired_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="request_ready",
            validation_now=observed_at
            + timedelta(
                hours=VALIDATOR.SENDER_PROFILE_MAX_AGE_HOURS, seconds=1
            ),
            lifecycle_times=lifecycle,
            errors=expired_errors,
        )
        self.assertTrue(
            any("older than the pre-send window" in error for error in expired_errors),
            expired_errors,
        )

        refreshed_snapshot_at = observed_at + timedelta(days=7)
        observation_errors: list[str] = []
        still_old_observed_at = VALIDATOR.validate_sender_profile_observation(
            copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING),
            snapshot_at=refreshed_snapshot_at,
            errors=observation_errors,
        )
        self.assertEqual([], observation_errors)
        refreshed_state_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            still_old_observed_at,
            stage="request_ready",
            validation_now=refreshed_snapshot_at,
            lifecycle_times=lifecycle,
            errors=refreshed_state_errors,
        )
        self.assertTrue(
            any(
                "older than the pre-send window" in error
                for error in refreshed_state_errors
            ),
            refreshed_state_errors,
        )

        future_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="request_ready",
            validation_now=observed_at - timedelta(seconds=1),
            lifecycle_times=lifecycle,
            errors=future_errors,
        )
        self.assertTrue(any("observation is in the future" in error for error in future_errors))

        offset_boundary_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="request_ready",
            validation_now=datetime.fromisoformat("2026-07-29T06:20:26+00:00"),
            lifecycle_times=lifecycle,
            errors=offset_boundary_errors,
        )
        self.assertEqual([], offset_boundary_errors)

        execution_boundary = observed_at + timedelta(
            hours=VALIDATOR.SENDER_PROFILE_MAX_AGE_HOURS
        )
        execution_lifecycle = {
            "readiness_recorded_at": readiness_at,
            "authorized_at": readiness_at + timedelta(minutes=1),
            "executed_at": execution_boundary,
        }
        execution_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="executed_once",
            validation_now=execution_boundary + timedelta(days=30),
            lifecycle_times=execution_lifecycle,
            errors=execution_errors,
        )
        self.assertEqual([], execution_errors)
        execution_lifecycle["executed_at"] = execution_boundary + timedelta(seconds=1)
        late_execution_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="executed_once",
            validation_now=execution_boundary + timedelta(days=30),
            lifecycle_times=execution_lifecycle,
            errors=late_execution_errors,
        )
        self.assertTrue(
            any(
                "execution occurred after the sender profile window" in error
                for error in late_execution_errors
            ),
            late_execution_errors,
        )

        execution_lifecycle["executed_at"] = execution_boundary
        execution_lifecycle["readiness_recorded_at"] = observed_at - timedelta(seconds=1)
        chronology_errors: list[str] = []
        VALIDATOR.validate_sender_profile_window(
            observed_at,
            stage="executed_once",
            validation_now=execution_boundary,
            lifecycle_times=execution_lifecycle,
            errors=chronology_errors,
        )
        self.assertTrue(
            any("readiness_recorded_at predates" in error for error in chronology_errors),
            chronology_errors,
        )

    def test_sender_profile_hash_and_parse_use_one_immutable_byte_read(self) -> None:
        evidence_path = ROOT / VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
        exact_bytes = evidence_path.read_bytes()
        second_read_attack = exact_bytes.replace(
            b'"account_email": "jacao@ucsd.edu"',
            b'"account_email": "another@example.com"',
        )
        read_count = 0

        def adversarial_read_bytes(path: Path) -> bytes:
            nonlocal read_count
            read_count += 1
            return exact_bytes if read_count == 1 else second_read_attack

        errors: list[str] = []
        with mock.patch.object(Path, "read_bytes", new=adversarial_read_bytes):
            observed_at = VALIDATOR.validate_sender_profile_observation(
                copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING),
                snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                errors=errors,
            )
        self.assertEqual(1, read_count)
        self.assertEqual([], errors)
        self.assertEqual(
            datetime.fromisoformat("2026-07-27T23:20:26-07:00"), observed_at
        )

    def test_static_sender_profile_never_makes_send_stage_executable(self) -> None:
        readiness_errors: list[str] = []
        VALIDATOR.validate_sender_execution_boundary(
            "request_ready", errors=readiness_errors
        )
        self.assertEqual([], readiness_errors)

        for stage in (
            "authorized_once",
            "executed_once",
            "observing",
            "closed",
        ):
            with self.subTest(stage=stage):
                errors: list[str] = []
                VALIDATOR.validate_sender_execution_boundary(stage, errors=errors)
                self.assertTrue(
                    any(
                        "static profile observation supports readiness only" in error
                        and "same-session get_profile" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_sender_profile_path_hash_content_and_duplicate_attacks_are_detected(
        self,
    ) -> None:
        with self.subTest("binding path"):
            binding = copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING)
            binding["path"] = "evidence/another-sender-profile.json"
            errors: list[str] = []
            VALIDATOR.validate_sender_profile_observation(
                binding, snapshot_at=self.now, errors=errors
            )
            self.assertTrue(
                any("exact content-addressed binding changed" in error for error in errors),
                errors,
            )
        with self.subTest("binding hash"):
            binding = copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING)
            binding["sha256"] = "0" * 64
            errors = []
            VALIDATOR.validate_sender_profile_observation(
                binding, snapshot_at=self.now, errors=errors
            )
            self.assertTrue(any("sha256 mismatch" in error for error in errors), errors)

        with tempfile.TemporaryDirectory(
            prefix="validator-sender-bytes-", dir="/private/tmp"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            evidence_dir = temp_root / "evidence"
            evidence_dir.mkdir()
            record_path = evidence_dir / Path(
                VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
            ).name
            raw = (ROOT / VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]).read_text(
                encoding="utf-8"
            )
            record_path.write_text(
                raw.replace('"account_email": "jacao@ucsd.edu"', '"account_email": "another@example.com"'),
                encoding="utf-8",
            )
            content_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root):
                VALIDATOR.validate_sender_profile_observation(
                    copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING),
                    snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                    errors=content_errors,
                )
            self.assertTrue(any("sha256 mismatch" in error for error in content_errors))

            duplicate_raw = raw.replace(
                '"account_email": "jacao@ucsd.edu"',
                (
                    '"account_email": "another@example.com",\n'
                    '  "account_email": "jacao@ucsd.edu"'
                ),
            )
            record_path.write_text(duplicate_raw, encoding="utf-8")
            duplicate_binding = {
                "path": f"evidence/{record_path.name}",
                "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
            }
            duplicate_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root), mock.patch.object(
                VALIDATOR,
                "EXPECTED_CA_SENDER_PROFILE_BINDING",
                duplicate_binding,
            ):
                VALIDATOR.validate_sender_profile_observation(
                    duplicate_binding,
                    snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                    errors=duplicate_errors,
                )
            self.assertTrue(
                any("duplicate JSON key rejected" in error for error in duplicate_errors),
                duplicate_errors,
            )

        with tempfile.TemporaryDirectory(
            prefix="validator-sender-symlink-", dir="/private/tmp"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            evidence_dir = temp_root / "evidence"
            evidence_dir.mkdir()
            target = evidence_dir / "real-profile.json"
            target.write_bytes(
                (ROOT / VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]).read_bytes()
            )
            link = evidence_dir / Path(
                VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
            ).name
            link.symlink_to(target)
            symlink_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root):
                VALIDATOR.validate_sender_profile_observation(
                    copy.deepcopy(VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING),
                    snapshot_at=datetime.fromisoformat("2026-07-27T23:21:00-07:00"),
                    errors=symlink_errors,
                )
            self.assertTrue(any("symlink" in error for error in symlink_errors))

    def test_mutating_state_and_readiness_receipt_sender_together_still_fails(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="validator-readiness-sender-", dir="/private/tmp"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            evidence_dir = temp_root / "evidence"
            evidence_dir.mkdir()
            profile_path = evidence_dir / Path(
                VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]
            ).name
            profile_path.write_bytes(
                (ROOT / VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING["path"]).read_bytes()
            )
            profile_binding = copy.deepcopy(
                VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING
            )
            message_binding = copy.deepcopy(
                self.state["approval_queue"][0]["message_binding"]
            )
            source_binding = {"path": "evidence/source.json", "sha256": "1" * 64}
            item = {
                "sender_account": VALIDATOR.EXPECTED_CA_SENDER_ACCOUNT,
                "sender_profile_record": profile_binding,
                "observation_cutoff_at": "2026-08-03T23:30:00-07:00",
                "message_binding": message_binding,
                "pre_send_source_refresh": {
                    "cec_status_record": source_binding,
                    "organization_channel_record": source_binding,
                },
            }
            receipt = {
                "schema_version": "1.0",
                "receipt_type": "readiness",
                "approval_id": VALIDATOR.EXPECTED_CA_APPROVAL_ID,
                "experiment_id": VALIDATOR.EXPECTED_CA_EXPERIMENT_ID,
                "from_stage": "blocked_missing_bindings",
                "to_stage": "request_ready",
                "recorded_at": "2026-07-27T23:21:00-07:00",
                "exact_target": copy.deepcopy(VALIDATOR.EXPECTED_CA_TARGET),
                "exact_channel": VALIDATOR.EXPECTED_CA_CHANNEL,
                "channel_source": VALIDATOR.EXPECTED_CA_CHANNEL_SOURCE,
                "message_binding": message_binding,
                "stage_payload": {
                    "sender_account": VALIDATOR.EXPECTED_CA_SENDER_ACCOUNT,
                    "sender_profile_record": profile_binding,
                    "observation_cutoff_at": item["observation_cutoff_at"],
                    "cec_status_record": source_binding,
                    "organization_channel_record": source_binding,
                },
            }
            receipt_path = evidence_dir / "readiness.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            binding = {
                "path": "evidence/readiness.json",
                "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
            }
            valid_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root):
                VALIDATOR.validate_stage_receipt(
                    binding,
                    receipt_field="readiness_receipt",
                    item=item,
                    now=datetime.fromisoformat("2026-07-27T23:22:00-07:00"),
                    errors=valid_errors,
                )
            self.assertEqual([], valid_errors)

            item["sender_account"] = "another@example.com"
            receipt["stage_payload"]["sender_account"] = "another@example.com"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            binding["sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            attack_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root):
                VALIDATOR.validate_stage_receipt(
                    binding,
                    receipt_field="readiness_receipt",
                    item=item,
                    now=datetime.fromisoformat("2026-07-27T23:22:00-07:00"),
                    errors=attack_errors,
                )
            self.assertTrue(
                any(
                    "sender account differs from authenticated profile" in error
                    for error in attack_errors
                ),
                attack_errors,
            )

            forged_profile = self.sender_profile_record()
            forged_profile["account_email"] = "another@example.com"
            profile_path.write_text(json.dumps(forged_profile), encoding="utf-8")
            forged_profile_binding = {
                "path": profile_binding["path"],
                "sha256": hashlib.sha256(profile_path.read_bytes()).hexdigest(),
            }
            item["sender_profile_record"] = forged_profile_binding
            receipt["stage_payload"]["sender_profile_record"] = forged_profile_binding
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            binding["sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            triple_attack_errors: list[str] = []
            with mock.patch.object(VALIDATOR, "RESEARCH_ROOT", temp_root):
                VALIDATOR.validate_stage_receipt(
                    binding,
                    receipt_field="readiness_receipt",
                    item=item,
                    now=datetime.fromisoformat("2026-07-27T23:22:00-07:00"),
                    errors=triple_attack_errors,
                )
            self.assertTrue(
                any(
                    "exact content-addressed binding changed" in error
                    for error in triple_attack_errors
                ),
                triple_attack_errors,
            )
            self.assertTrue(
                any(
                    "authenticated account differs from the exact sender" in error
                    for error in triple_attack_errors
                ),
                triple_attack_errors,
            )

    def test_duplicate_sender_profile_binding_is_rejected_in_state_and_receipt_json(
        self,
    ) -> None:
        binding_json = json.dumps(
            VALIDATOR.EXPECTED_CA_SENDER_PROFILE_BINDING, separators=(",", ":")
        )
        raw_cases = {
            "state": (
                '{"approval_queue":[{"sender_profile_record":'
                + binding_json
                + ',"sender_profile_record":'
                + binding_json
                + "}]}"
            ),
            "readiness receipt": (
                '{"stage_payload":{"sender_profile_record":'
                + binding_json
                + ',"sender_profile_record":'
                + binding_json
                + "}}"
            ),
        }
        with tempfile.TemporaryDirectory(
            prefix="validator-duplicate-sender-binding-", dir="/private/tmp"
        ) as temp_dir:
            for label, raw in raw_cases.items():
                with self.subTest(label=label):
                    path = Path(temp_dir) / f"{label.replace(' ', '-')}.json"
                    path.write_text(raw, encoding="utf-8")
                    errors: list[str] = []
                    loaded = VALIDATOR.load_json(
                        path, errors=errors, label=f"duplicate {label}"
                    )
                    self.assertIsNone(loaded)
                    self.assertTrue(
                        any("duplicate JSON key rejected" in error for error in errors),
                        errors,
                    )

    def test_stale_as_of_fails_closed_but_injected_fresh_now_passes(self) -> None:
        due = datetime.fromisoformat(self.state["freshness_policy"]["refresh_due_at"])
        self.assert_detected(
            copy.deepcopy(self.state),
            "active state is stale",
            now=due + timedelta(seconds=1),
        )
        fresh_errors = self.errors_for(self.state, now=self.now)
        self.assertFalse(
            any("active state is stale" in error for error in fresh_errors),
            fresh_errors,
        )

    def test_nonexistent_semicolon_evidence_locator_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        fact = state["workstreams"][0]["observed_facts"][0]
        fact["evidence_locator"] += "; evidence/does-not-exist.json"
        self.assert_detected(state, "locator does not resolve")

    def test_symlink_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="validator-symlink-") as temp_dir:
            root = Path(temp_dir)
            target = root / "target.txt"
            target.write_text("evidence", encoding="utf-8")
            link = root / "link.txt"
            link.symlink_to(target)
            errors: list[str] = []
            resolved = VALIDATOR.confined_file(
                "link.txt",
                base=root,
                allowed_root=root,
                errors=errors,
                label="symlink-test",
            )
            self.assertIsNone(resolved)
            self.assertTrue(any("symlink" in error for error in errors), errors)

    def test_evidence_locator_traversal_is_rejected(self) -> None:
        state = copy.deepcopy(self.state)
        state["workstreams"][0]["observed_facts"][0]["evidence_locator"] = (
            "../README.md"
        )
        self.assert_detected(state, "confined relative path")

    def test_request_ready_refresh_recomputes_bound_raw_content(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="validator-refresh-", dir="/private/tmp"
        ) as temp_dir:
            root = Path(temp_dir)
            raw = root / "evidence/raw"
            raw.mkdir(parents=True)
            csv_path = raw / "fresh-cec.csv"
            csv_path.write_text(
                '"Building ID",Street,City,"Gross Floor Area","Reporting Year","Compliance Status"\n'
                '"Building #CA012650","800 bay marina drive","national city",64888,2026,"in compliance"\n',
                encoding="utf-8",
            )
            csv_binding = {
                "path": "evidence/raw/fresh-cec.csv",
                "sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            }
            record = {
                "schema_version": "ca012650-cec-status-refresh/1",
                "captured_at": self.state["as_of"],
                "source_url": (
                    "https://touchstone-content.s3.us-east-1.amazonaws.com/governments/"
                    "CoveredBuildingsExport.csv"
                ),
                "source_content_binding": csv_binding,
                "exact_target": {
                    "public_building_id": "Building #CA012650",
                    "public_record_location": "Best Western Plus Marina Gateway Hotel",
                    "public_address": "800 Bay Marina Drive, National City",
                },
                "observed_reporting_year": "2026",
                "observed_compliance_status": "not submitted",
                "claim_boundary": VALIDATOR.EXPECTED_CA_REFRESH_CLAIM_BOUNDARIES[
                    "CEC status/address"
                ],
            }
            record_path = root / "cec-record.json"
            record_path.write_text(json.dumps(record), encoding="utf-8")
            binding = {
                "path": record_path.name,
                "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
            }
            errors: list[str] = []
            VALIDATOR.validate_refresh_record(
                binding,
                record_type="CEC status/address",
                completed_at=datetime.fromisoformat(self.state["as_of"]),
                stage="request_ready",
                validation_now=self.now,
                snapshot_at=datetime.fromisoformat(self.state["as_of"]),
                errors=errors,
                base=root,
                allowed_root=root,
            )
            self.assertTrue(
                any("differs from bound raw CSV" in error for error in errors), errors
            )

            record["claim_boundary"] = (
                "External contact, quoting, payment, and delivery are authorized now."
            )
            record_path.write_text(json.dumps(record), encoding="utf-8")
            binding["sha256"] = hashlib.sha256(record_path.read_bytes()).hexdigest()
            boundary_errors: list[str] = []
            VALIDATOR.validate_refresh_record(
                binding,
                record_type="CEC status/address",
                completed_at=datetime.fromisoformat(self.state["as_of"]),
                stage="request_ready",
                validation_now=self.now,
                snapshot_at=datetime.fromisoformat(self.state["as_of"]),
                errors=boundary_errors,
                base=root,
                allowed_root=root,
            )
            self.assertTrue(
                any("claim boundary differs" in error for error in boundary_errors),
                boundary_errors,
            )

    def test_pre_send_refresh_age_uses_validation_now(self) -> None:
        refresh = {
            "status": "completed",
            "completed_at": self.state["as_of"],
            "cec_status_record": None,
            "organization_channel_record": None,
        }
        errors: list[str] = []
        snapshot_at = datetime.fromisoformat(self.state["as_of"])
        VALIDATOR.validate_source_refresh(
            refresh,
            stage="request_ready",
            validation_now=snapshot_at
            + timedelta(hours=VALIDATOR.PRE_SEND_REFRESH_MAX_AGE_HOURS, seconds=1),
            snapshot_at=snapshot_at,
            errors=errors,
        )
        self.assertTrue(
            any("older than the pre-send freshness window" in error for error in errors),
            errors,
        )
        boundary_errors: list[str] = []
        VALIDATOR.validate_source_refresh(
            refresh,
            stage="request_ready",
            validation_now=snapshot_at
            + timedelta(hours=VALIDATOR.PRE_SEND_REFRESH_MAX_AGE_HOURS),
            snapshot_at=snapshot_at,
            errors=boundary_errors,
        )
        self.assertFalse(
            any(
                "older than the pre-send freshness window" in error
                for error in boundary_errors
            ),
            boundary_errors,
        )

    def test_post_execution_must_be_inside_refresh_window(self) -> None:
        refresh_at = datetime.fromisoformat(self.state["as_of"])
        errors: list[str] = []
        VALIDATOR.validate_execution_refresh_window(
            executed_at=refresh_at
            + timedelta(hours=VALIDATOR.PRE_SEND_REFRESH_MAX_AGE_HOURS, seconds=1),
            refresh_timestamps=[refresh_at],
            errors=errors,
        )
        self.assertTrue(
            any("after at least one source freshness window" in error for error in errors),
            errors,
        )
        boundary_errors: list[str] = []
        VALIDATOR.validate_execution_refresh_window(
            executed_at=refresh_at
            + timedelta(hours=VALIDATOR.PRE_SEND_REFRESH_MAX_AGE_HOURS),
            refresh_timestamps=[refresh_at],
            errors=boundary_errors,
        )
        self.assertEqual([], boundary_errors)

    def test_one_stale_source_cannot_hide_behind_newer_refresh(self) -> None:
        start = datetime.fromisoformat(self.state["as_of"])
        errors: list[str] = []
        VALIDATOR.validate_execution_refresh_window(
            executed_at=start + timedelta(hours=46),
            refresh_timestamps=[
                start,
                start + timedelta(hours=23),
                start + timedelta(hours=23),
            ],
            errors=errors,
        )
        self.assertTrue(
            any("at least one source freshness window" in error for error in errors),
            errors,
        )

    def test_ca_r2_candidate_set_rejects_omission_and_hash_drift(self) -> None:
        bindings = self.ca_r2_bindings()
        with self.subTest("validator omitted"):
            errors: list[str] = []
            VALIDATOR.validate_ca_r2_candidate_bindings(
                [
                    binding
                    for binding in bindings
                    if binding["path"] != "../09-校验活动状态.py"
                ],
                receipt_parent=ROOT / "evidence",
                errors=errors,
            )
            self.assertTrue(
                any("exact unique closed review candidate" in error for error in errors),
                errors,
            )
        with self.subTest("sender profile observation omitted"):
            errors = []
            VALIDATOR.validate_ca_r2_candidate_bindings(
                [
                    binding
                    for binding in bindings
                    if binding["path"]
                    != "gmail-sender-profile-observation-2026-07-27T2320.json"
                ],
                receipt_parent=ROOT / "evidence",
                errors=errors,
            )
            self.assertTrue(
                any("exact unique closed review candidate" in error for error in errors),
                errors,
            )
        with self.subTest("latest historical FAIL omitted"):
            errors = []
            VALIDATOR.validate_ca_r2_candidate_bindings(
                [
                    binding
                    for binding in bindings
                    if binding["path"]
                    != "review-ca012650-detached-gate-2026-07-27-attempt-2.json"
                ],
                receipt_parent=ROOT / "evidence",
                errors=errors,
            )
            self.assertTrue(
                any("exact unique closed review candidate" in error for error in errors),
                errors,
            )
        with self.subTest("validator hash drift"):
            drifted = copy.deepcopy(bindings)
            validator_binding = next(
                binding
                for binding in drifted
                if binding["path"] == "../09-校验活动状态.py"
            )
            validator_binding["sha256"] = "0" * 64
            errors = []
            VALIDATOR.validate_ca_r2_candidate_bindings(
                drifted,
                receipt_parent=ROOT / "evidence",
                errors=errors,
            )
            self.assertTrue(any("sha256 mismatch" in error for error in errors), errors)

    def test_ca_r2_receipt_contract_binds_identity_schema_and_predecessors(self) -> None:
        receipt_path = ROOT / "evidence/review-ca012650-durable-candidate-2026-07-27-r2.json"
        now = datetime.fromisoformat("2026-07-27T22:00:00-07:00")
        valid = self.ca_r2_receipt()
        errors: list[str] = []
        VALIDATOR.validate_ca_r2_receipt_contract(
            valid,
            receipt_path=receipt_path,
            now=now,
            errors=errors,
        )
        self.assertEqual([], errors)

        with self.subTest("reviewer substitution"):
            changed = copy.deepcopy(valid)
            changed["reviewer_agent_identity"] = "/root/another_agent"
            errors = []
            VALIDATOR.validate_ca_r2_receipt_contract(
                changed, receipt_path=receipt_path, now=now, errors=errors
            )
            self.assertTrue(
                any("reviewer_agent_identity changed" in error for error in errors),
                errors,
            )
        with self.subTest("unknown root field"):
            changed = copy.deepcopy(valid)
            changed["self_asserted_quality"] = "PASS"
            errors = []
            VALIDATOR.validate_ca_r2_receipt_contract(
                changed, receipt_path=receipt_path, now=now, errors=errors
            )
            self.assertTrue(any("unknown fields" in error for error in errors), errors)
        with self.subTest("not later than predecessor"):
            changed = copy.deepcopy(valid)
            changed["recorded_at"] = "2026-07-27T21:54:09-07:00"
            errors = []
            VALIDATOR.validate_ca_r2_receipt_contract(
                changed, receipt_path=receipt_path, now=now, errors=errors
            )
            self.assertTrue(
                any("later than every historical FAIL" in error for error in errors),
                errors,
            )

    def test_precontact_successor_contract_is_exact_and_chronological(self) -> None:
        review = self.successor_review()
        review_path = ROOT / VALIDATOR.EXPECTED_REVIEW_STATE_PATHS[
            "ca012650_internal_candidate"
        ]
        now = datetime.fromisoformat("2026-07-28T00:06:00-07:00")
        errors: list[str] = []
        recorded_at = VALIDATOR.validate_ca_precontact_successor_receipt_contract(
            review, receipt_path=review_path, now=now, errors=errors
        )
        self.assertEqual([], errors)
        self.assertEqual(
            datetime.fromisoformat("2026-07-28T00:05:00-07:00"), recorded_at
        )

        scalar_attacks = {
            "schema": (
                "schema_version",
                "old-schema",
                "schema_version changed",
            ),
            "review identity": (
                "review_id",
                "review-reused-r2",
                "review_id changed",
            ),
            "reviewer": (
                "reviewer_agent_identity",
                "/root/not-independent",
                "reviewer_agent_identity changed",
            ),
            "candidate modified": (
                "reviewer_modified_candidate",
                True,
                "reviewer_modified_candidate changed",
            ),
            "verdict": ("verdict", "FAIL", "verdict changed"),
            "external status": (
                "external_action_status",
                "AUTHORIZED",
                "external_action_status changed",
            ),
            "claim expansion": (
                "claim_boundary",
                "Sending and market claims are authorized.",
                "claim_boundary changed",
            ),
        }
        for label, (key, value, needle) in scalar_attacks.items():
            with self.subTest(label=label):
                changed = copy.deepcopy(review)
                changed[key] = value
                attack_errors: list[str] = []
                VALIDATOR.validate_ca_precontact_successor_receipt_contract(
                    changed, receipt_path=review_path, now=now, errors=attack_errors
                )
                self.assertTrue(
                    any(needle in error for error in attack_errors), attack_errors
                )

        with self.subTest("review predates sender remediation"):
            changed = copy.deepcopy(review)
            changed["recorded_at"] = "2026-07-27T23:56:49-07:00"
            errors = []
            VALIDATOR.validate_ca_precontact_successor_receipt_contract(
                changed, receipt_path=review_path, now=now, errors=errors
            )
            self.assertTrue(
                any("later than sender-remediation predecessor" in error for error in errors),
                errors,
            )

    def test_precontact_successor_candidate_set_rejects_omission_substitution_and_paths(
        self,
    ) -> None:
        receipt_parent = ROOT / "evidence"
        bindings = self.successor_candidate_bindings()
        attacks: dict[str, tuple[list[dict[str, str]], str]] = {}

        omitted = copy.deepcopy(bindings)
        omitted.pop()
        attacks["omission"] = (omitted, "exact unique closed successor candidate")

        duplicated = copy.deepcopy(bindings)
        duplicated.append(copy.deepcopy(duplicated[0]))
        attacks["duplicate"] = (duplicated, "duplicate")

        wrong_hash = copy.deepcopy(bindings)
        next(
            binding
            for binding in wrong_hash
            if binding["path"]
            == "review-ca012650-recipient-value-2026-07-27-r1.json"
        )["sha256"] = "0" * 64
        attacks["recipient hash"] = (wrong_hash, "sha256 mismatch")

        snapshot_drift = copy.deepcopy(bindings)
        next(
            binding
            for binding in snapshot_drift
            if binding["path"] == "precursor-sender-stage-09-3ac3937a.snapshot"
        )["sha256"] = "1" * 64
        attacks["sender snapshot drift"] = (snapshot_drift, "sha256 mismatch")

        traversal = copy.deepcopy(bindings)
        traversal[0]["path"] = "../../outside.json"
        attacks["path traversal"] = (traversal, "path traversal")

        for label, (candidate, needle) in attacks.items():
            with self.subTest(label=label):
                errors: list[str] = []
                VALIDATOR.validate_ca_precontact_successor_candidate_bindings(
                    candidate, receipt_parent=receipt_parent, errors=errors
                )
                self.assertTrue(any(needle in error for error in errors), errors)

    def test_recipient_fail_cannot_be_upgraded_or_misrepresented(self) -> None:
        source = ROOT / VALIDATOR.EXPECTED_CA_RECIPIENT_VALUE_REVIEW_BINDING["path"]
        original = VALIDATOR.loads_json_strict(source.read_text(encoding="utf-8"))
        assert isinstance(original, dict)
        attacks = {
            "verdict": ("verdict", "PASS", "verdict changed"),
            "independence": (
                "independent_review",
                True,
                "independent_review changed",
            ),
            "counterevidence": (
                "claim_boundary",
                "This proves there is no demand.",
                "claim_boundary changed",
            ),
        }
        with tempfile.TemporaryDirectory(
            prefix="validator-recipient-fail-", dir="/private/tmp"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            evidence = temp_root / "evidence"
            evidence.mkdir()
            (temp_root / "12-首个反证实验与对外动作候选.md").write_bytes(
                (ROOT / "12-首个反证实验与对外动作候选.md").read_bytes()
            )
            snapshot_binding = copy.deepcopy(
                VALIDATOR.EXPECTED_CA_PRETRANSITION_STATE_SNAPSHOT_BINDING
            )
            snapshot_path = temp_root / snapshot_binding["path"]
            snapshot_path.write_bytes((ROOT / snapshot_binding["path"]).read_bytes())
            review_path = evidence / source.name
            for label, (key, value, needle) in attacks.items():
                with self.subTest(label=label):
                    changed = copy.deepcopy(original)
                    changed[key] = value
                    review_path.write_text(
                        json.dumps(changed, ensure_ascii=False), encoding="utf-8"
                    )
                    binding = {
                        "path": f"evidence/{source.name}",
                        "sha256": hashlib.sha256(review_path.read_bytes()).hexdigest(),
                    }
                    errors: list[str] = []
                    with mock.patch.object(
                        VALIDATOR, "RESEARCH_ROOT", temp_root
                    ), mock.patch.object(
                        VALIDATOR,
                        "EXPECTED_CA_RECIPIENT_VALUE_REVIEW_BINDING",
                        binding,
                    ):
                        VALIDATOR.validate_ca_recipient_value_review(
                            binding,
                            now=datetime.fromisoformat("2026-07-27T23:31:00-07:00"),
                            errors=errors,
                        )
                    self.assertTrue(any(needle in error for error in errors), errors)

    def test_rejection_receipt_closes_every_external_and_market_interpretation(
        self,
    ) -> None:
        receipt_path = ROOT / VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING[
            "path"
        ]
        original = VALIDATOR.loads_json_strict(receipt_path.read_text(encoding="utf-8"))
        assert isinstance(original, dict)

        def errors_for_receipt(receipt: dict) -> list[str]:
            errors: list[str] = []
            original_loader = VALIDATOR.load_exact_bound_json

            def loader_override(binding: object, **kwargs: object) -> tuple[Path | None, dict | None]:
                if str(kwargs.get("label", "")).startswith(
                    "CA012650 approval precontact_rejection_receipt:"
                ):
                    return receipt_path, copy.deepcopy(receipt)
                return original_loader(binding, **kwargs)

            with mock.patch.object(
                VALIDATOR, "load_exact_bound_json", side_effect=loader_override
            ):
                VALIDATOR.validate_precontact_rejection_receipt(
                    copy.deepcopy(
                        VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING
                    ),
                    item=None,
                    now=datetime.fromisoformat("2026-07-27T23:44:00-07:00"),
                    errors=errors,
                    validate_stage_item=False,
                )
            return errors

        boolean_attacks = {
            "request authorization": "request_send_authorization",
            "external draft": "external_draft_authorized",
            "external contact": "external_contact_authorized",
            "message sent": "message_sent",
            "follow-up": "follow_up_sent",
            "recipient response": "recipient_or_market_response_observed",
            "market counterevidence": "market_counterevidence_claimed",
        }
        for label, key in boolean_attacks.items():
            with self.subTest(label=label):
                changed = copy.deepcopy(original)
                changed["stage_payload"][key] = True
                errors = errors_for_receipt(changed)
                self.assertTrue(
                    any(f"{key} must be the JSON boolean false" in error for error in errors),
                    errors,
                )

        with self.subTest("wrong transition"):
            changed = copy.deepcopy(original)
            changed["to_stage"] = "request_ready"
            self.assertTrue(
                any("to_stage" in error for error in errors_for_receipt(changed))
            )
        with self.subTest("recipient review binding"):
            changed = copy.deepcopy(original)
            changed["stage_payload"]["recipient_value_review_record"]["sha256"] = "0" * 64
            self.assertTrue(
                any("recipient-value review binding changed" in error for error in errors_for_receipt(changed))
            )
        with self.subTest("snapshot binding"):
            changed = copy.deepcopy(original)
            changed["stage_payload"]["pretransition_state_snapshot"]["sha256"] = "0" * 64
            self.assertTrue(
                any("pretransition snapshot binding changed" in error for error in errors_for_receipt(changed))
            )
        with self.subTest("chronology"):
            changed = copy.deepcopy(original)
            changed["recorded_at"] = "2026-07-27T23:30:13-07:00"
            self.assertTrue(
                any("later than recipient-value review" in error for error in errors_for_receipt(changed))
            )

    def test_rejected_state_is_terminal_unbound_and_result_closed(self) -> None:
        opportunity_index = next(
            index
            for index, stream in enumerate(self.rejected_state()["workstreams"])
            if stream["id"] == "opportunity_to_transaction"
        )

        mutations = {
            "revive request ready": (
                lambda state: (
                    state["approval_queue"][0].__setitem__("status", "request_ready"),
                    state["approval_queue"][0]["lifecycle"].__setitem__(
                        "stage", "request_ready"
                    ),
                ),
                "terminal rejected_precontact",
            ),
            "same identity revert": (
                lambda state: (
                    state["approval_queue"][0].__setitem__(
                        "status", "blocked_missing_bindings"
                    ),
                    state["approval_queue"][0]["lifecycle"].__setitem__(
                        "stage", "blocked_missing_bindings"
                    ),
                    state["approval_queue"][0]["lifecycle"].__setitem__(
                        "previous_stage", None
                    ),
                ),
                "terminal rejected_precontact",
            ),
            "ready": (
                lambda state: state["approval_queue"][0].__setitem__("ready", True),
                "flags do not match",
            ),
            "executable": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "executable", True
                ),
                "flags do not match",
            ),
            "authorized": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "authorized", True
                ),
                "flags do not match",
            ),
            "authorization consumed": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "authorization_consumed", True
                ),
                "flags do not match",
            ),
            "exact user authorization": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "exact_user_authorization", True
                ),
                "exact user authorization must be false",
            ),
            "sender populated": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "sender_account", "jacao@ucsd.edu"
                ),
                "sender account must be null",
            ),
            "cutoff populated": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "observation_cutoff_at", "2026-08-03T23:30:00-07:00"
                ),
                "observation cutoff must be null",
            ),
            "refresh populated": (
                lambda state: state["approval_queue"][0][
                    "pre_send_source_refresh"
                ].update({"status": "completed", "completed_at": state["as_of"]}),
                "blocked stage must keep refresh wholly incomplete",
            ),
            "missing binding removed": (
                lambda state: state["approval_queue"][0]["missing_bindings"].pop(),
                "exact missing bindings changed",
            ),
            "readiness receipt present": (
                lambda state: state["approval_queue"][0]["lifecycle"].__setitem__(
                    "readiness_receipt",
                    copy.deepcopy(
                        VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING
                    ),
                ),
                "non-required receipt readiness_receipt must be null",
            ),
            "result demand": (
                lambda state: state["workstreams"][opportunity_index][
                    "current_experiment"
                ]["result_claims"].__setitem__("externally_validated_demand", True),
                "result claims must remain false",
            ),
            "asset claim": (
                lambda state: state["workstreams"][opportunity_index][
                    "current_experiment"
                ]["result_claims"].__setitem__("asset_candidate", True),
                "result claims must remain false",
            ),
            "unknown deleted": (
                lambda state: state["workstreams"][opportunity_index][
                    "unknowns"
                ].pop(),
                "unknowns differ from the exact closed value",
            ),
            "counterevidence prose": (
                lambda state: state["workstreams"][opportunity_index][
                    "observed_facts"
                ][2].__setitem__(
                    "claim", "The recipient rejected us and market demand is absent."
                ),
                "observed_facts differ from exact stage rendering",
            ),
            "Gmail draft field": (
                lambda state: state["approval_queue"][0].__setitem__(
                    "gmail_draft_created", True
                ),
                "unknown fields",
            ),
        }
        for label, (mutate, needle) in mutations.items():
            with self.subTest(label=label):
                state = self.rejected_state()
                mutate(state)
                self.assert_rejected_detected(state, needle)

        for result_name in sorted(VALIDATOR.REQUIRED_FALSE_EXPERIMENT_RESULTS):
            with self.subTest(result_claim=result_name):
                state = self.rejected_state()
                state["workstreams"][opportunity_index]["current_experiment"][
                    "result_claims"
                ][result_name] = True
                self.assert_rejected_detected(
                    state, "result claims must remain false"
                )

        for receipt_name in (
            "readiness_receipt",
            "authorization_receipt",
            "execution_receipt",
            "observation_receipt",
            "closure_receipt",
        ):
            with self.subTest(non_required_receipt=receipt_name):
                state = self.rejected_state()
                state["approval_queue"][0]["lifecycle"][receipt_name] = copy.deepcopy(
                    VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING
                )
                self.assert_rejected_detected(
                    state, f"non-required receipt {receipt_name} must be null"
                )

        for flag_name in (
            "authorized",
            "ready",
            "executable",
            "authorization_consumed",
        ):
            with self.subTest(boolean_type_confusion=flag_name):
                state = self.rejected_state()
                state["approval_queue"][0][flag_name] = 1
                self.assert_rejected_detected(state, "flags do not match")

    def test_rejected_identity_target_channel_message_and_receipt_are_immutable(self) -> None:
        mutations = {
            "target": (
                lambda approval: approval["exact_target"].__setitem__(
                    "public_building_id", "Building #OTHER"
                ),
                "exact target changed",
            ),
            "channel": (
                lambda approval: approval.__setitem__(
                    "exact_channel", "other@example.com"
                ),
                "exact channel changed",
            ),
            "message": (
                lambda approval: approval["message_binding"].__setitem__(
                    "sha256", "0" * 64
                ),
                "sha256 mismatch",
            ),
            "receipt missing": (
                lambda approval: approval["lifecycle"].__setitem__(
                    "precontact_rejection_receipt", None
                ),
                "requires precontact_rejection_receipt",
            ),
            "receipt hash": (
                lambda approval: approval["lifecycle"][
                    "precontact_rejection_receipt"
                ].__setitem__("sha256", "0" * 64),
                "exact content-addressed binding changed",
            ),
        }
        for label, (mutate, needle) in mutations.items():
            with self.subTest(label=label):
                state = self.rejected_state()
                mutate(state["approval_queue"][0])
                self.assert_rejected_detected(state, needle)

    def test_authority_and_result_prose_are_exact_closed_values(self) -> None:
        opportunity_index = next(
            index
            for index, stream in enumerate(self.state["workstreams"])
            if stream["id"] == "opportunity_to_transaction"
        )
        mutations = (
            (
                "opportunity positive fact",
                lambda state: state["workstreams"][opportunity_index][
                    "observed_facts"
                ][0].update(
                    {
                        "claim_class": "externally_validated",
                        "claim": (
                            "The target paid; demand and willingness to pay are proven."
                        ),
                    }
                ),
                "opportunity semantic closure",
            ),
            (
                "opportunity action",
                lambda state: state["workstreams"][opportunity_index]["next_action"].__setitem__(
                    "description",
                    "Send now, quote, collect payment, and begin delivery.",
                ),
                "opportunity semantic closure",
            ),
            (
                "opportunity unknown",
                lambda state: state["workstreams"][opportunity_index]["unknowns"].__setitem__(
                    0, "Demand and payment are already proven."
                ),
                "opportunity semantic closure",
            ),
            (
                "opportunity stop condition",
                lambda state: state["workstreams"][opportunity_index][
                    "stop_conditions"
                ].__setitem__(0, "Never stop; all external actions are authorized."),
                "opportunity semantic closure",
            ),
            (
                "review scope",
                lambda state: state["workstreams"][opportunity_index][
                    "current_experiment"
                ].__setitem__(
                    "internal_review_scope",
                    "Independent PASS authorizes external contact, quoting, and payment.",
                ),
                "internal review scope differs",
            ),
            (
                "approval boundary",
                lambda state: state["approval_queue"][0].__setitem__(
                    "claim_boundary",
                    "Contact, quoting, payment, and delivery are authorized now.",
                ),
                "claim boundary differs from exact lifecycle stage",
            ),
            (
                "investment action",
                lambda state: next(
                    stream
                    for stream in state["workstreams"]
                    if stream["id"] == "investment_discipline"
                )["next_action"].__setitem__(
                    "description", "Connect a broker and start live trading now."
                ),
                "investment_discipline semantic closure",
            ),
        )
        for label, mutate, needle in mutations:
            with self.subTest(label):
                state = self.rejected_state()
                mutate(state)
                self.assert_rejected_detected(state, needle)

    def test_raw_json_duplicate_keys_are_rejected_recursively(self) -> None:
        state_raw = STATE_PATH.read_text(encoding="utf-8")
        duplicated_state = state_raw.replace(
            '"default": "deny_high_impact_or_external_actions"',
            (
                '"default": "allow",\n'
                '    "default": "deny_high_impact_or_external_actions"'
            ),
            1,
        )
        self.assertNotEqual(state_raw, duplicated_state)

        receipt_raw = json.dumps(self.ca_r2_receipt(), ensure_ascii=False, indent=2)
        duplicate_receipts = {
            "verdict": receipt_raw.replace(
                '"verdict": "PASS"',
                '"verdict": "FAIL",\n  "verdict": "PASS"',
                1,
            ),
            "reviewer identity": receipt_raw.replace(
                '"reviewer_agent_identity": "/root/ca_gate_fix_map"',
                (
                    '"reviewer_agent_identity": "/root/not-independent",\n'
                    '  "reviewer_agent_identity": "/root/ca_gate_fix_map"'
                ),
                1,
            ),
            "external action status": receipt_raw.replace(
                '"external_action_status": "BLOCKED_NOT_AUTHORIZED"',
                (
                    '"external_action_status": "AUTHORIZED",\n'
                    '  "external_action_status": "BLOCKED_NOT_AUTHORIZED"'
                ),
                1,
            ),
        }
        successor_raw = json.dumps(
            self.successor_review(), ensure_ascii=False, indent=2
        )
        duplicate_successor = successor_raw.replace(
            '"verdict": "PASS"',
            '"verdict": "FAIL",\n  "verdict": "PASS"',
            1,
        )
        rejection_raw = (
            ROOT
            / VALIDATOR.EXPECTED_CA_PRECONTACT_REJECTION_RECEIPT_BINDING["path"]
        ).read_text(encoding="utf-8")
        duplicate_rejection = rejection_raw.replace(
            '"message_sent": false',
            '"message_sent": true,\n    "message_sent": false',
            1,
        )
        raw_cases = {
            "nested state authority": duplicated_state,
            **duplicate_receipts,
            "successor duplicate verdict": duplicate_successor,
            "rejection duplicate external action": duplicate_rejection,
        }
        with tempfile.TemporaryDirectory(
            prefix="validator-duplicate-json-", dir="/private/tmp"
        ) as temp_dir:
            for label, raw in raw_cases.items():
                with self.subTest(label):
                    path = Path(temp_dir) / f"{label.replace(' ', '-')}.json"
                    path.write_text(raw, encoding="utf-8")
                    errors: list[str] = []
                    loaded = VALIDATOR.load_json(
                        path, errors=errors, label=f"duplicate {label}"
                    )
                    self.assertIsNone(loaded)
                    self.assertTrue(
                        any("duplicate JSON key rejected" in error for error in errors),
                        errors,
                    )

    def test_duplicate_strategy_artifact_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        artifacts = state["workstreams"][0]["strategy_artifacts"]
        artifacts[1] = copy.deepcopy(artifacts[0])
        self.assert_detected(state, "duplicate")

    def test_extra_approval_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        extra = copy.deepcopy(state["approval_queue"][0])
        extra["id"] = "unexpected-extra-approval"
        state["approval_queue"].append(extra)
        self.assert_detected(state, "only the exact CA012650 entry")

    def test_scope_expansion_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        state["authority_envelope"]["autonomous_scopes"].append(
            "external_contact_without_approval"
        )
        self.assert_detected(state, "exact required set changed")

    def test_hash_tampering_is_detected(self) -> None:
        state = copy.deepcopy(self.state)
        state["workstreams"][0]["strategy_artifacts"][0]["sha256"] = "0" * 64
        self.assert_detected(state, "sha256 mismatch")

    def test_illegal_lifecycle_transition_is_detected(self) -> None:
        state = self.rejected_state()
        approval = state["approval_queue"][0]
        approval["status"] = "authorized_once"
        approval["lifecycle"]["stage"] = "authorized_once"
        approval["lifecycle"]["previous_stage"] = "blocked_missing_bindings"
        self.assert_rejected_detected(state, "illegal or skipped transition")
        self.assert_rejected_detected(state, "requires readiness_receipt")


if __name__ == "__main__":
    unittest.main()
