#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

from verify_run2_crosswalk import (  # noqa: E402
    CrosswalkError,
    canonical_jsonl,
    final_rows,
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
