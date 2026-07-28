#!/usr/bin/env python3
"""Negative and positive tests for candidate/post-closure phase separation."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True

from verify_candidate_manifest import (
    REAL_CANDIDATE_ID,
    REAL_CANDIDATE_ROOT_NAME,
    REQUIRED_RUN2_ACCEPTANCE_PATHS,
    ManifestError,
    sha256_file,
    validate_manifest,
)
from verify_post_closure_manifest import (
    ACTION_ENVELOPE_PATH,
    CANDIDATE_VERIFIER_PATH,
    validate_aggregate,
)
from verify_run2_acceptance import AcceptanceError


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, document: dict) -> None:
    write_text(path, json.dumps(document, ensure_ascii=False, indent=2) + "\n")


class PhaseManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otts-phase-test-")
        self.parent = Path(self.temporary.name)
        self.candidate = self.parent / "candidate"
        self.candidate.mkdir()
        self.envelope = self.candidate / ACTION_ENVELOPE_PATH
        self.verifier_fixture = self.candidate / CANDIDATE_VERIFIER_PATH
        write_text(self.envelope, "synthetic envelope\n")
        write_text(self.verifier_fixture, "synthetic verifier identity\n")
        self.envelope_hash = sha256_file(self.envelope)
        self.verifier_hash = sha256_file(self.verifier_fixture)
        self.candidate_manifest = self.candidate / "FINAL_CANDIDATE_MANIFEST.json"
        candidate_document = {
            "schema_version": "1.1",
            "candidate_id": "SYNTHETIC-C2",
            "status": "SYNTHETIC-TEST-ONLY",
            "scope": "Synthetic verifier test only; no authority.",
            "candidate_inventory_root": ".",
            "post_closure_artifact_roots": [
                {
                    "root_id": "closure-governance",
                    "path_from_candidate_parent": "机会到交易系统-闭合记录",
                    "artifact_kind": "CLOSURE_GOVERNANCE",
                    "required_manifest": "GOVERNANCE_ARTIFACT_MANIFEST.json",
                    "freeze_required_state": "MUST_BE_ABSENT",
                    "post_closure_required_state": "MUST_BE_PRESENT",
                    "activation_gate": "EXACT_CANDIDATE_REVIEW_PASS",
                    "governed_by_path": ACTION_ENVELOPE_PATH,
                    "governed_by_sha256": self.envelope_hash,
                },
                {
                    "root_id": "shadow-mvp",
                    "path_from_candidate_parent": "机会到交易系统-shadow-mvp",
                    "artifact_kind": "READ_ONLY_SHADOW_MVP",
                    "required_manifest": "SHADOW_ARTIFACT_MANIFEST.json",
                    "freeze_required_state": "MUST_BE_ABSENT",
                    "post_closure_required_state": "MAY_BE_ABSENT_OR_VALID",
                    "activation_gate": "EXACT_CLOSURE_DECISION",
                    "governed_by_path": ACTION_ENVELOPE_PATH,
                    "governed_by_sha256": self.envelope_hash,
                },
            ],
            "entries": [
                {
                    "path": ACTION_ENVELOPE_PATH,
                    "sha256": self.envelope_hash,
                    "role": "synthetic-envelope",
                    "authority_status": "synthetic-no-authority",
                    "depends_on": [],
                },
                {
                    "path": CANDIDATE_VERIFIER_PATH,
                    "sha256": self.verifier_hash,
                    "role": "synthetic-verifier-identity",
                    "authority_status": "synthetic-no-authority",
                    "depends_on": [],
                },
            ],
            "historical_exclusions": [],
        }
        write_json(self.candidate_manifest, candidate_document)
        self.freeze_result = validate_manifest(self.candidate_manifest, phase="freeze")
        self.candidate_hash = sha256_file(self.candidate_manifest)
        self.governance_root = self.parent / "机会到交易系统-闭合记录"
        self.shadow_root = self.parent / "机会到交易系统-shadow-mvp"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _create_governance(self) -> dict[str, Path | str]:
        self.governance_root.mkdir()
        freeze_path = self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        review_path = self.governance_root / "FINAL_INDEPENDENT_REVIEW_RECEIPT.json"
        decision_path = self.governance_root / "RESEARCH_CLOSURE_DECISION.json"
        governance_path = self.governance_root / "GOVERNANCE_ARTIFACT_MANIFEST.json"

        freeze = {
            "schema_version": "otts.candidate-freeze-report/1",
            "candidate_id": "SYNTHETIC-C2",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "verifier_path": CANDIDATE_VERIFIER_PATH,
            "verifier_sha256": self.verifier_hash,
            "mode": "freeze",
            "result": "PASS",
            "candidate_inventory_digest_sha256": self.freeze_result[
                "candidate_inventory_digest_sha256"
            ],
            "post_closure_root_states": [
                {"root_id": "closure-governance", "state": "ABSENT"},
                {"root_id": "shadow-mvp", "state": "ABSENT"},
            ],
        }
        write_json(freeze_path, freeze)
        freeze_hash = sha256_file(freeze_path)

        review = {
            "schema_version": "otts.final-independent-review-receipt/1",
            "receipt_id": "SYNTHETIC-REVIEW",
            "candidate_id": "SYNTHETIC-C2",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "freeze_report_sha256": freeze_hash,
            "verifier_sha256": self.verifier_hash,
            "reviewer_id": "synthetic-independent-reviewer",
            "independence_assertion": "Synthetic test assertion; no real authority.",
            "review_scope": (
                "FULL_CANDIDATE_MANIFEST_AND_ALL_ACTIVE_HISTORICAL_DEPENDENCIES"
            ),
            "verdict": "PASS",
            "unresolved_critical": [],
            "unresolved_major": [],
            "residual_limits": ["Synthetic fixture only."],
            "action_envelope_path": ACTION_ENVELOPE_PATH,
            "action_envelope_sha256": self.envelope_hash,
        }
        write_json(review_path, review)
        review_hash = sha256_file(review_path)

        decision = {
            "schema_version": "otts.research-closure-decision/1",
            "decision_id": "SYNTHETIC-DECISION",
            "candidate_id": "SYNTHETIC-C2",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "freeze_report_sha256": freeze_hash,
            "independent_review_receipt_sha256": review_hash,
            "decision": "CONDITIONALLY_READY",
            "authorized_root_id": "shadow-mvp",
            "authorized_root_path": "机会到交易系统-shadow-mvp",
            "authorized_envelope_id": "RO-SHADOW-ENVELOPE-1.0",
            "authorized_envelope_sha256": self.envelope_hash,
            "authority_scope": "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY",
            "issuer_id": "synthetic-closure-gate",
            "unresolved_conditions": [],
            "external_action_authority": False,
        }
        write_json(decision_path, decision)
        decision_hash = sha256_file(decision_path)

        governance = {
            "schema_version": "otts.post-closure-governance-manifest/1",
            "artifact_kind": "CLOSURE_GOVERNANCE",
            "candidate_id": "SYNTHETIC-C2",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "freeze_report": {
                "path": freeze_path.name,
                "sha256": freeze_hash,
            },
            "independent_review_receipt": {
                "path": review_path.name,
                "sha256": review_hash,
            },
            "closure_decision": {
                "path": decision_path.name,
                "sha256": decision_hash,
            },
        }
        write_json(governance_path, governance)
        return {
            "decision_hash": decision_hash,
            "decision_path": decision_path,
            "governance_path": governance_path,
            "review_path": review_path,
        }

    def _validate(self, bundle: dict[str, Path | str], shadow: Path | None = None) -> dict:
        return validate_aggregate(
            candidate_manifest_path=self.candidate_manifest,
            governance_manifest_path=Path(bundle["governance_path"]),
            expected_decision_sha256=str(bundle["decision_hash"]),
            shadow_manifest_path=shadow,
        )

    def test_freeze_requires_both_sibling_roots_absent(self) -> None:
        self.governance_root.mkdir()
        with self.assertRaisesRegex(ManifestError, "must be absent"):
            validate_manifest(self.candidate_manifest, phase="freeze")

    def test_post_closure_requires_governance_root(self) -> None:
        with self.assertRaisesRegex(ManifestError, "required post-closure root is absent"):
            validate_manifest(self.candidate_manifest, phase="post-closure")

    def test_candidate_unlisted_file_fails(self) -> None:
        write_text(self.candidate / "UNLISTED.txt", "must fail\n")
        with self.assertRaisesRegex(ManifestError, "unlisted project files"):
            validate_manifest(self.candidate_manifest, phase="freeze")

    def test_candidate_special_file_fails(self) -> None:
        os.mkfifo(self.candidate / "UNLISTED.fifo")
        with self.assertRaisesRegex(ManifestError, "special file"):
            validate_manifest(self.candidate_manifest, phase="freeze")

    def test_candidate_hardlink_fails(self) -> None:
        os.link(self.envelope, self.candidate / "HARDLINK.md")
        with self.assertRaisesRegex(ManifestError, "hardlinked file"):
            validate_manifest(self.candidate_manifest, phase="freeze")

    def test_unknown_activation_gate_fails(self) -> None:
        candidate = canonical_load(self.candidate_manifest)
        candidate["post_closure_artifact_roots"][0]["activation_gate"] = "OPAQUE"
        write_json(self.candidate_manifest, candidate)
        with self.assertRaisesRegex(ManifestError, "frozen root policy"):
            validate_manifest(self.candidate_manifest, phase="freeze")

    def _candidate_specific_manifest(self, *, omit: str | None = None) -> tuple[Path, Path]:
        root = self.parent / REAL_CANDIDATE_ROOT_NAME
        root.mkdir()
        envelope = root / ACTION_ENVELOPE_PATH
        verifier = root / CANDIDATE_VERIFIER_PATH
        write_text(envelope, "candidate-specific synthetic envelope\n")
        write_text(verifier, "candidate-specific synthetic verifier\n")
        paths = {ACTION_ENVELOPE_PATH, CANDIDATE_VERIFIER_PATH}
        for relative in REQUIRED_RUN2_ACCEPTANCE_PATHS:
            if relative != omit:
                write_text(root / relative, f"synthetic {relative}\n")
                paths.add(relative)
        envelope_hash = sha256_file(envelope)
        document = canonical_load(self.candidate_manifest)
        document["candidate_id"] = REAL_CANDIDATE_ID
        document["post_closure_artifact_roots"][0]["governed_by_sha256"] = envelope_hash
        document["post_closure_artifact_roots"][1]["governed_by_sha256"] = envelope_hash
        document["entries"] = [
            {
                "path": relative,
                "sha256": sha256_file(root / relative),
                "role": "candidate-specific synthetic fixture",
                "authority_status": "SYNTHETIC_NO_AUTHORITY",
                "depends_on": [],
            }
            for relative in sorted(paths)
        ]
        manifest = root / "FINAL_CANDIDATE_MANIFEST.json"
        write_json(manifest, document)
        return root, manifest

    def test_real_candidate_requires_all_run2_acceptance_artifacts(self) -> None:
        omitted = sorted(REQUIRED_RUN2_ACCEPTANCE_PATHS)[0]
        root, manifest = self._candidate_specific_manifest(omit=omitted)
        with patch("verify_candidate_manifest.REAL_CANDIDATE_ROOT", root.resolve()):
            with self.assertRaisesRegex(ManifestError, "omits required Run2 acceptance"):
                validate_manifest(manifest, phase="freeze")

    def test_real_candidate_rejects_invalid_run2_acceptance(self) -> None:
        root, manifest = self._candidate_specific_manifest()
        with (
            patch("verify_candidate_manifest.REAL_CANDIDATE_ROOT", root.resolve()),
            patch(
                "verify_candidate_manifest.validate_acceptance",
                side_effect=AcceptanceError("synthetic receipt tamper"),
            ),
        ):
            with self.assertRaisesRegex(ManifestError, "Run2 exact acceptance is invalid"):
                validate_manifest(manifest, phase="freeze")

    def test_valid_governance_with_absent_shadow_is_not_implementation_valid(self) -> None:
        bundle = self._create_governance()
        result = self._validate(bundle)
        self.assertTrue(result["candidate_snapshot_valid"])
        self.assertTrue(result["closure_chain_valid"])
        self.assertEqual(result["shadow_state"], "ABSENT_AUTHORIZED")
        self.assertFalse(result["shadow_generation_valid"])
        self.assertFalse(result["external_action_authority"])

    def test_external_decision_hash_mismatch_fails(self) -> None:
        bundle = self._create_governance()
        with self.assertRaisesRegex(ManifestError, "external expected hash"):
            validate_aggregate(
                candidate_manifest_path=self.candidate_manifest,
                governance_manifest_path=Path(bundle["governance_path"]),
                expected_decision_sha256="0" * 64,
                shadow_manifest_path=None,
            )

    def test_governance_extra_file_fails(self) -> None:
        bundle = self._create_governance()
        write_text(self.governance_root / "UNLISTED.txt", "must fail\n")
        with self.assertRaisesRegex(ManifestError, "governance inventory mismatch"):
            self._validate(bundle)

    def test_governance_symlink_fails(self) -> None:
        bundle = self._create_governance()
        (self.governance_root / "LINK").symlink_to(
            self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        )
        with self.assertRaisesRegex(ManifestError, "symlink"):
            self._validate(bundle)

    def test_governance_hardlink_fails(self) -> None:
        bundle = self._create_governance()
        os.link(
            self.governance_root / "FREEZE_VERIFICATION_REPORT.json",
            self.governance_root / "HARDLINK.json",
        )
        with self.assertRaisesRegex(ManifestError, "hardlinked"):
            self._validate(bundle)

    def test_unresolved_major_fails_even_if_manifest_rehashed(self) -> None:
        bundle = self._create_governance()
        review_path = Path(bundle["review_path"])
        review = canonical_load(review_path)
        review["unresolved_major"] = ["synthetic-major"]
        write_json(review_path, review)
        self._rehash_governance_after_review_change(bundle)
        with self.assertRaisesRegex(ManifestError, "unresolved_major"):
            self._validate(bundle)

    def _rehash_governance_after_review_change(
        self,
        bundle: dict[str, Path | str],
    ) -> None:
        review_path = Path(bundle["review_path"])
        decision_path = Path(bundle["decision_path"])
        governance_path = Path(bundle["governance_path"])
        review_hash = sha256_file(review_path)
        decision = canonical_load(decision_path)
        decision["independent_review_receipt_sha256"] = review_hash
        write_json(decision_path, decision)
        decision_hash = sha256_file(decision_path)
        governance = canonical_load(governance_path)
        governance["independent_review_receipt"]["sha256"] = review_hash
        governance["closure_decision"]["sha256"] = decision_hash
        write_json(governance_path, governance)
        bundle["decision_hash"] = decision_hash

    def test_wrong_decision_scope_fails_even_with_matching_external_hash(self) -> None:
        bundle = self._create_governance()
        decision_path = Path(bundle["decision_path"])
        governance_path = Path(bundle["governance_path"])
        decision = canonical_load(decision_path)
        decision["authority_scope"] = "BROADER_THAN_ENVELOPE"
        write_json(decision_path, decision)
        decision_hash = sha256_file(decision_path)
        governance = canonical_load(governance_path)
        governance["closure_decision"]["sha256"] = decision_hash
        write_json(governance_path, governance)
        bundle["decision_hash"] = decision_hash
        with self.assertRaisesRegex(ManifestError, "authority_scope"):
            self._validate(bundle)

    def test_present_shadow_requires_explicit_shadow_manifest_argument(self) -> None:
        bundle = self._create_governance()
        self.shadow_root.mkdir()
        write_json(self.shadow_root / "SHADOW_ARTIFACT_MANIFEST.json", {})
        with self.assertRaisesRegex(ManifestError, "requires explicit"):
            self._validate(bundle)

    def _create_shadow(
        self,
        bundle: dict[str, Path | str],
    ) -> tuple[Path, Path]:
        self.shadow_root.mkdir()
        readme = self.shadow_root / "README.md"
        write_text(readme, "synthetic shadow\n")
        shadow_manifest = self.shadow_root / "SHADOW_ARTIFACT_MANIFEST.json"
        shadow = {
            "schema_version": "otts.shadow-artifact-manifest/1",
            "artifact_id": "SYNTHETIC-SHADOW",
            "artifact_kind": "READ_ONLY_SHADOW_MVP",
            "status": "SHADOW_IMPLEMENTATION_CANDIDATE",
            "scope": "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY",
            "candidate_id": "SYNTHETIC-C2",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "governance_manifest_sha256": sha256_file(Path(bundle["governance_path"])),
            "independent_review_receipt_sha256": sha256_file(Path(bundle["review_path"])),
            "closure_decision_sha256": str(bundle["decision_hash"]),
            "action_envelope_path": ACTION_ENVELOPE_PATH,
            "action_envelope_sha256": self.envelope_hash,
            "external_action_authority": False,
            "entries": [
                {
                    "path": "README.md",
                    "sha256": sha256_file(readme),
                    "role": "documentation",
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [],
                }
            ],
        }
        write_json(shadow_manifest, shadow)
        return shadow_manifest, readme

    def test_shadow_status_overclaim_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        shadow["status"] = "PRODUCTION_AUTHORIZED"
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "status exceeds"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_external_authority_claim_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        shadow["external_action_authority"] = True
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "deny external"):
            self._validate(bundle, shadow_manifest)

    def test_valid_shadow_then_tamper_fails_without_changing_candidate_hash(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, readme = self._create_shadow(bundle)
        result = self._validate(bundle, shadow_manifest)
        self.assertTrue(result["shadow_generation_valid"])
        frozen_candidate_hash = sha256_file(self.candidate_manifest)
        write_text(readme, "tampered shadow\n")
        with self.assertRaisesRegex(ManifestError, "hash mismatch"):
            self._validate(bundle, shadow_manifest)
        self.assertEqual(sha256_file(self.candidate_manifest), frozen_candidate_hash)


def canonical_load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
