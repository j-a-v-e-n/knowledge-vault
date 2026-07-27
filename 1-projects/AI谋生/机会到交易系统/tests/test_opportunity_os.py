from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from opportunity_os import (  # noqa: E402
    RECORD_DIRECTORIES,
    derive_opportunity_status,
    init_workspace,
    make_harness,
    validate_record,
    validate_workspace,
)


CREATED_AT = "2026-07-27T12:00:00Z"


def write_record(workspace: Path, record: dict) -> Path:
    directory = workspace / RECORD_DIRECTORIES[record["record_type"]]
    path = directory / f"{record['id']}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def principle() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "principle",
        "id": "principle-visible-value",
        "created_at": CREATED_AT,
        "premises": [
            "A buyer cannot evaluate an outcome they cannot understand.",
            "A concrete preview can reduce uncertainty about a proposed outcome.",
        ],
        "derivation": [
            "If uncertainty blocks evaluation, a tailored preview may make the value gap visible."
        ],
        "prediction": "Some buyers will take a next step only after seeing a concrete preview.",
        "falsifier": "Comparable buyers understand the preview but consistently decline any next step.",
    }


def observation() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "observation",
        "id": "observation-public-artifact",
        "created_at": CREATED_AT,
        "source": {"kind": "public_webpage", "locator": "https://example.invalid/source"},
        "captured_at": CREATED_AT,
        "actor_context": "Publicly visible business artifact; decision-maker identity is unknown.",
        "verbatim_or_observable": ["The public artifact does not show the proposed feature."],
        "known_context": ["The artifact was publicly accessible at capture time."],
        "unknown_context": ["Whether the owner wants the feature or has a budget."],
        "visibility": "latent_indicator",
    }


def opportunity() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "opportunity",
        "id": "opportunity-tailored-preview",
        "created_at": CREATED_AT,
        "buyer": "The decision-maker responsible for the public business artifact",
        "situation": "Potential customers evaluate the business through the artifact",
        "value_gap": "The artifact may not communicate a desired outcome clearly",
        "value_hypothesis": "A tailored preview could make an improved outcome concrete",
        "why_might_pay": "The buyer may value a clearer path from visitor attention to action",
        "observation_refs": ["observation-public-artifact"],
        "principle_refs": ["principle-visible-value"],
        "alternatives": ["Keep the current artifact", "Use a self-service tool"],
        "uncertainties": ["Whether the buyer perceives a problem", "Whether timing is suitable"],
        "disconfirming_signals": ["The buyer explicitly prefers the current artifact"],
    }


def probe() -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "probe",
        "id": "probe-tailored-preview",
        "created_at": CREATED_AT,
        "opportunity_ref": "opportunity-tailored-preview",
        "claim_tested": "The target will request a next step after seeing a tailored preview.",
        "offer": "A bounded, tailored improvement with explicit scope and price to be defined before contact.",
        "artifact": "A local, non-published value preview",
        "target": "One named decision-maker selected from public evidence",
        "success_event_kinds": ["next_step_requested", "meeting_scheduled"],
        "failure_or_stop_events": ["declined", "no_response"],
        "effort_boundary": "Stop at the owner-approved effort boundary recorded before the run.",
        "external_action_policy": "draft_only",
    }


def event(event_id: str, kind: str, origin: str) -> dict:
    return {
        "schema_version": "0.1",
        "record_type": "event",
        "id": event_id,
        "created_at": CREATED_AT,
        "opportunity_ref": "opportunity-tailored-preview",
        "event_kind": kind,
        "occurred_at": CREATED_AT,
        "evidence_locator": f"local-evidence://{event_id}",
        "evidence_origin": origin,
        "actor": "Recorded actor",
        "notes": "Event fixture for deterministic state derivation.",
    }


class OpportunityOSTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name) / "workspace"
        init_workspace(self.workspace)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add_foundation(self) -> None:
        write_record(self.workspace, principle())
        write_record(self.workspace, observation())
        write_record(self.workspace, opportunity())
        write_record(self.workspace, probe())

    def test_empty_workspace_is_valid(self) -> None:
        _, issues = validate_workspace(self.workspace)
        self.assertEqual([], issues)

    def test_observation_cannot_smuggle_in_inference(self) -> None:
        record = observation()
        record["inference"] = "The owner will pay."
        issues = validate_record(record)
        self.assertTrue(any("interpretation fields" in issue.message for issue in issues))

    def test_opportunity_requires_both_channels_to_exist(self) -> None:
        write_record(self.workspace, opportunity())
        _, issues = validate_workspace(self.workspace)
        messages = [issue.message for issue in issues]
        self.assertIn("unknown observation_ref 'observation-public-artifact'", messages)
        self.assertIn("unknown principle_ref 'principle-visible-value'", messages)

    def test_market_and_fulfillment_stages_are_derived_separately(self) -> None:
        self.add_foundation()
        write_record(self.workspace, event("event-offer", "offer_presented", "system_log"))
        write_record(self.workspace, event("event-declined", "declined", "external_party"))
        write_record(self.workspace, event("event-prototype", "prototype_created", "system_log"))

        index, issues = validate_workspace(self.workspace)
        self.assertEqual([], issues)
        status = derive_opportunity_status("opportunity-tailored-preview", index)
        self.assertEqual("exposed", status["market_stage"])
        self.assertEqual("prototype", status["fulfillment_stage"])
        self.assertEqual(["declined"], status["issue_events"])

    def test_external_interest_cannot_be_self_certified(self) -> None:
        self.add_foundation()
        write_record(self.workspace, event("event-meeting", "meeting_scheduled", "system_log"))
        _, issues = validate_workspace(self.workspace)
        self.assertTrue(any("must originate from the external party" in issue.message for issue in issues))

    def test_payment_event_advances_market_stage_only(self) -> None:
        self.add_foundation()
        write_record(self.workspace, event("event-payment", "payment_received", "payment_provider"))
        index, issues = validate_workspace(self.workspace)
        self.assertEqual([], issues)
        status = derive_opportunity_status("opportunity-tailored-preview", index)
        self.assertEqual("paid", status["market_stage"])
        self.assertEqual("not_started", status["fulfillment_stage"])

    def test_delivery_harness_is_blocked_without_commitment(self) -> None:
        self.add_foundation()
        probe_manifest = make_harness(
            self.workspace,
            "opportunity-tailored-preview",
            "probe-tailored-preview",
            "probe",
        )
        self.assertTrue(probe_manifest.is_file())

        with self.assertRaisesRegex(ValueError, "blocked until external evidence reaches commitment"):
            make_harness(
                self.workspace,
                "opportunity-tailored-preview",
                "probe-tailored-preview",
                "delivery",
            )

        write_record(self.workspace, event("event-deposit", "deposit_received", "payment_provider"))
        delivery_manifest = make_harness(
            self.workspace,
            "opportunity-tailored-preview",
            "probe-tailored-preview",
            "delivery",
        )
        self.assertTrue(delivery_manifest.is_file())

    def test_harness_identity_changes_when_source_record_changes(self) -> None:
        self.add_foundation()
        first_manifest = make_harness(
            self.workspace,
            "opportunity-tailored-preview",
            "probe-tailored-preview",
            "probe",
        )

        observation_path = self.workspace / "observations" / "observation-public-artifact.json"
        record = json.loads(observation_path.read_text(encoding="utf-8"))
        record["unknown_context"].append("Whether another provider is already changing it.")
        observation_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        second_manifest = make_harness(
            self.workspace,
            "opportunity-tailored-preview",
            "probe-tailored-preview",
            "probe",
        )
        self.assertNotEqual(first_manifest.name, second_manifest.name)
        self.assertTrue(first_manifest.is_file())
        self.assertTrue(second_manifest.is_file())

    def test_records_cannot_set_their_own_validation_status(self) -> None:
        record = opportunity()
        record["validated"] = True
        issues = validate_record(record)
        self.assertTrue(any("derived validation fields are forbidden" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
