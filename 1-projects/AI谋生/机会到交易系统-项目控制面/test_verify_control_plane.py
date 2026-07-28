#!/usr/bin/env python3

import copy
import json
import tempfile
import unittest
from pathlib import Path

from verify_control_plane import (
    LIFECYCLE_POLICIES,
    collect_snapshot,
    load_decisions,
    load_json,
    resolve_inside,
    validate_authority_and_action,
    validate_candidate,
    validate_control_plane,
    validate_decision_graph,
    validate_eval_task,
)


ROOT = Path(__file__).resolve().parent


class DecisionGraphTests(unittest.TestCase):
    def test_live_decision_graph_is_closed(self) -> None:
        records = load_decisions(ROOT / "DECISIONS.jsonl")
        self.assertEqual(validate_decision_graph(records, "D030", "D020"), [])

    def test_orphan_parent_is_rejected(self) -> None:
        records = load_decisions(ROOT / "DECISIONS.jsonl")
        changed = copy.deepcopy(records)
        changed[-1]["parent_id"] = "MISSING"
        errors = validate_decision_graph(changed, "D030", "D020")
        self.assertTrue(any("missing parent_id" in item for item in errors))

    def test_unrelated_backtrack_is_rejected(self) -> None:
        records = load_decisions(ROOT / "DECISIONS.jsonl")
        errors = validate_decision_graph(records, "D040", "D000")
        self.assertTrue(any("no UNTRIED alternative" in item for item in errors))

    def test_invalid_status_and_empty_basis_are_rejected(self) -> None:
        records = load_decisions(ROOT / "DECISIONS.jsonl")
        changed = copy.deepcopy(records)
        changed[3]["status"] = "WHATEVER"
        changed[3]["basis"] = []
        errors = validate_decision_graph(changed, "D030", "D020")
        self.assertTrue(any("invalid status" in item for item in errors))
        self.assertTrue(any("basis" in item for item in errors))


class AuthorityAndActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = load_json(ROOT / "STATE.json")

    def test_external_authority_true_is_rejected(self) -> None:
        changed = copy.deepcopy(self.state)
        changed["authority"]["external"]["contact_real_people"] = True
        errors = validate_authority_and_action(changed)
        self.assertTrue(any("contact_real_people" in item for item in errors))

    def test_free_text_external_action_cannot_pass(self) -> None:
        changed = copy.deepcopy(self.state)
        changed["next_safe_action"]["kind"] = "CONTACT_AND_COLLECT_MONEY"
        changed["next_safe_action"]["target"] = "real people"
        errors = validate_authority_and_action(changed)
        self.assertTrue(any("action kind" in item for item in errors))

    def test_pending_model_qualification_does_not_control_authority(self) -> None:
        self.assertFalse(self.state["model_portability"]["qualification_is_authority"])
        self.assertFalse(self.state["model_portability"]["unattended_handoff_qualified"])
        self.assertEqual(validate_authority_and_action(self.state), [])

    def test_transition_table_contains_shadow_and_reality_exit(self) -> None:
        self.assertIn("LOCAL_READ_ONLY_SHADOW", LIFECYCLE_POLICIES)
        self.assertIn("SHADOW_COMPLETE_AWAITING_REALITY_GATE", LIFECYCLE_POLICIES)
        self.assertEqual(
            LIFECYCLE_POLICIES["SHADOW_COMPLETE_AWAITING_REALITY_GATE"]["action"],
            "PREPARE_REALITY_EXPERIMENT_PROPOSAL",
        )


class CandidateTests(unittest.TestCase):
    def test_empty_hash_map_is_rejected(self) -> None:
        state = load_json(ROOT / "STATE.json")
        state["current_candidate"]["candidate_hashes"] = {}
        errors = validate_candidate(ROOT, state)
        self.assertTrue(any("exact non-empty key set" in item for item in errors))

    def test_false_root_presence_claim_is_rejected(self) -> None:
        state = load_json(ROOT / "STATE.json")
        state["current_candidate"]["post_closure_roots_present"] = True
        errors = validate_candidate(ROOT, state)
        self.assertTrue(any("does not match filesystem" in item for item in errors))


class EvalAndSnapshotTests(unittest.TestCase):
    def test_recovery_task_has_no_current_gold(self) -> None:
        self.assertEqual(validate_eval_task(ROOT), [])

    def test_snapshot_reports_transient_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "x.pyc").write_bytes(b"x")
            _, _, transients = collect_snapshot(root)
            self.assertEqual(transients, ["__pycache__/x.pyc"])

    def test_control_plane_path_escape_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            resolve_inside(ROOT, "../outside.md")


class LiveControlPlaneTests(unittest.TestCase):
    def test_live_control_plane_is_consistent(self) -> None:
        result = validate_control_plane(ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertTrue(result["snapshot_stable"])
        self.assertRegex(result["snapshot_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()

