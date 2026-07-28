#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True

from verify_run2_crosswalk import (  # noqa: E402
    CrosswalkError,
    SEMANTICALLY_REJECTED_DIRECT_IDENTITIES,
    canonical_jsonl,
    final_rows,
    parse_direct_mappings,
    validate_crosswalk,
)


ROOT = Path(__file__).resolve().parent
CANONICAL = ROOT / "RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl"


class Run2CrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows, cls.counts = final_rows(ROOT)

    def write_rows(self, directory: Path, rows: list[dict]) -> Path:
        path = directory / "crosswalk.jsonl"
        path.write_text(canonical_jsonl(rows), encoding="utf-8")
        return path

    def test_canonical_crosswalk_is_exhaustive_and_exact(self) -> None:
        result = validate_crosswalk(ROOT, CANONICAL)
        self.assertTrue(result["valid"])
        self.assertEqual(self.counts, {key: result[key] for key in self.counts})

    def test_missing_final_ce_in_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_rows(Path(temporary), self.rows[1:])
            with self.assertRaisesRegex(CrosswalkError, "missing="):
                validate_crosswalk(ROOT, path)

    def test_duplicate_identity_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_rows(Path(temporary), [self.rows[0], *self.rows])
            with self.assertRaisesRegex(CrosswalkError, "duplicates="):
                validate_crosswalk(ROOT, path)

    def test_claim_tamper_fails(self) -> None:
        changed = json.loads(json.dumps(self.rows, ensure_ascii=False))
        changed[0]["lead_claim"] += " tampered"
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_rows(Path(temporary), changed)
            with self.assertRaisesRegex(CrosswalkError, "differs from reconstructed"):
                validate_crosswalk(ROOT, path)

    def test_final_k_tamper_fails(self) -> None:
        changed = json.loads(json.dumps(self.rows, ensure_ascii=False))
        s2_index = next(index for index, row in enumerate(changed) if row["stage"] == "S2")
        changed[s2_index]["final_k"] = ["K13"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_rows(Path(temporary), changed)
            with self.assertRaisesRegex(CrosswalkError, "differs from reconstructed"):
                validate_crosswalk(ROOT, path)

    def test_unused_row_cannot_self_promote(self) -> None:
        changed = json.loads(json.dumps(self.rows, ensure_ascii=False))
        unused_index = next(
            index
            for index, row in enumerate(changed)
            if row["mapping_state"] == "NO_DIRECT_LOAD_BEARING_USE"
        )
        changed[unused_index]["mapping_state"] = "DIRECT_LOAD_BEARING_MAPPING"
        changed[unused_index]["claim_ids"] = ["SS-99"]
        with tempfile.TemporaryDirectory() as temporary:
            path = self.write_rows(Path(temporary), changed)
            with self.assertRaisesRegex(CrosswalkError, "differs from reconstructed"):
                validate_crosswalk(ROOT, path)

    def test_semantically_rejected_identities_remain_non_direct(self) -> None:
        by_identity = {row["identity"]: row for row in self.rows}
        for identity in sorted(SEMANTICALLY_REJECTED_DIRECT_IDENTITIES):
            with self.subTest(identity=identity):
                row = by_identity[identity]
                self.assertEqual(row["mapping_state"], "NO_DIRECT_LOAD_BEARING_USE")
                self.assertEqual(row["claim_ids"], [])
                self.assertEqual(row["dd_ids"], [])

    def test_rejected_identity_cannot_be_reintroduced_by_count_change(self) -> None:
        mappings = parse_direct_mappings(ROOT / "RUN2_CLAIM_EVIDENCE_CROSSWALK.md")
        mappings["S2-K03/R16/turn163academia15"] = {
            "rq_ids": ["RQ1"],
            "claim_ids": ["SS-01"],
            "dd_ids": ["DD-05"],
            "residual_unknown": "synthetic re-promotion",
        }
        with patch("verify_run2_crosswalk.parse_direct_mappings", return_value=mappings):
            with self.assertRaisesRegex(CrosswalkError, "semantically rejected identities"):
                final_rows(ROOT)

    def test_r05_cannot_regain_ss01_bridge(self) -> None:
        mappings = parse_direct_mappings(ROOT / "RUN2_CLAIM_EVIDENCE_CROSSWALK.md")
        mappings["S2-K06/R05/turn166search3"]["claim_ids"].append("SS-01")
        with patch("verify_run2_crosswalk.parse_direct_mappings", return_value=mappings):
            with self.assertRaisesRegex(CrosswalkError, "semantically rejected claim bridge"):
                final_rows(ROOT)

    def test_r05_retains_only_narrow_tf04_bridge(self) -> None:
        row = next(
            row
            for row in self.rows
            if row["identity"] == "S2-K06/R05/turn166search3"
        )
        self.assertEqual(row["mapping_state"], "DIRECT_LOAD_BEARING_MAPPING")
        self.assertEqual(row["rq_ids"], ["RQ5"])
        self.assertEqual(row["claim_ids"], ["TF-04"])
        self.assertEqual(row["dd_ids"], ["DD-05"])

    def test_noncanonical_serialization_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "crosswalk.jsonl"
            path.write_text(
                "\n".join(json.dumps(row, ensure_ascii=False) for row in self.rows) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(CrosswalkError, "not in canonical JSONL form"):
                validate_crosswalk(ROOT, path)


if __name__ == "__main__":
    unittest.main()
