#!/usr/bin/env python3
"""Negative and positive tests for candidate/post-closure phase separation."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode = True

from build_freeze_report import (  # noqa: E402
    FREEZE_REPORT_KEYS as BUILDER_FREEZE_REPORT_KEYS,
    FreezeReportError,
    build_freeze_report,
    write_freeze_report,
)
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
    CAPABILITY_POLICY_PATH,
    CANDIDATE_VERIFIER_PATH,
    FREEZE_REPORT_KEYS as GATE_FREEZE_REPORT_KEYS,
    SHADOW_ACCEPTANCE_RUNNER_PATH,
    validate_aggregate,
)
import run_shadow_acceptance as rsa
from verify_run2_acceptance import AcceptanceError


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, document: dict) -> None:
    write_text(path, json.dumps(document, ensure_ascii=False, indent=2) + "\n")


def byte_inventory_snapshot(root: Path) -> tuple[set[str], dict[str, str], str]:
    file_hashes = {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    inventory_digest = hashlib.sha256(
        json.dumps(
            file_hashes,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    return set(file_hashes), file_hashes, inventory_digest


class PhaseManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="otts-phase-test-")
        self.parent = Path(self.temporary.name)
        self.candidate = self.parent / "candidate"
        self.candidate.mkdir()
        self.envelope = self.candidate / ACTION_ENVELOPE_PATH
        self.verifier_fixture = self.candidate / CANDIDATE_VERIFIER_PATH
        self.policy_fixture = self.candidate / CAPABILITY_POLICY_PATH
        self.runner_fixture = self.candidate / SHADOW_ACCEPTANCE_RUNNER_PATH
        write_text(self.envelope, "synthetic envelope\n")
        write_text(self.verifier_fixture, "synthetic verifier identity\n")
        source_root = Path(__file__).resolve().parent
        write_text(
            self.policy_fixture,
            (source_root / "SHADOW_CAPABILITY_POLICY.json").read_text(encoding="utf-8"),
        )
        write_text(
            self.runner_fixture,
            (source_root / "run_shadow_acceptance.py").read_text(encoding="utf-8"),
        )
        self.envelope_hash = sha256_file(self.envelope)
        self.verifier_hash = sha256_file(self.verifier_fixture)
        self.candidate_manifest = self.candidate / "FINAL_CANDIDATE_MANIFEST.json"
        candidate_document = {
            "schema_version": "1.1",
            "candidate_id": "SYNTHETIC-C6",
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
                {
                    "root_id": "shadow-review",
                    "path_from_candidate_parent": "机会到交易系统-shadow-review",
                    "artifact_kind": "SHADOW_INDEPENDENT_REVIEW",
                    "required_manifest": "SHADOW_REVIEW_MANIFEST.json",
                    "freeze_required_state": "MUST_BE_ABSENT",
                    "post_closure_required_state": "MAY_BE_ABSENT_OR_VALID",
                    "activation_gate": (
                        "EXACT_DECLARATIVE_SHADOW_SNAPSHOT_AND_CALLER_BOUND_REVIEW"
                    ),
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
                {
                    "path": CAPABILITY_POLICY_PATH,
                    "sha256": sha256_file(self.policy_fixture),
                    "role": "synthetic-capability-policy",
                    "authority_status": "synthetic-no-authority",
                    "depends_on": [],
                },
                {
                    "path": SHADOW_ACCEPTANCE_RUNNER_PATH,
                    "sha256": sha256_file(self.runner_fixture),
                    "role": "synthetic-acceptance-runner",
                    "authority_status": "synthetic-no-authority",
                    "depends_on": [CAPABILITY_POLICY_PATH],
                },
            ],
            "historical_exclusions": [],
        }
        write_json(self.candidate_manifest, candidate_document)
        self.freeze_result = validate_manifest(self.candidate_manifest, phase="freeze")
        self.candidate_hash = sha256_file(self.candidate_manifest)
        self.governance_root = self.parent / "机会到交易系统-闭合记录"
        self.shadow_root = self.parent / "机会到交易系统-shadow-mvp"
        self.shadow_review_root = self.parent / "机会到交易系统-shadow-review"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _create_governance(self) -> dict[str, Path | str]:
        freeze = build_freeze_report(self.candidate_manifest)
        self.governance_root.mkdir()
        freeze_path = self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        review_path = self.governance_root / "FINAL_INDEPENDENT_REVIEW_RECEIPT.json"
        decision_path = self.governance_root / "RESEARCH_CLOSURE_DECISION.json"
        governance_path = self.governance_root / "GOVERNANCE_ARTIFACT_MANIFEST.json"

        write_json(freeze_path, freeze)
        freeze_hash = sha256_file(freeze_path)

        review = {
            "schema_version": "otts.final-independent-review-receipt/1",
            "receipt_id": "SYNTHETIC-REVIEW",
            "candidate_id": "SYNTHETIC-C6",
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
            "external_action_authority": False,
        }
        write_json(review_path, review)
        review_hash = sha256_file(review_path)

        decision = {
            "schema_version": "otts.research-closure-decision/1",
            "decision_id": "SYNTHETIC-DECISION",
            "candidate_id": "SYNTHETIC-C6",
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
            "candidate_id": "SYNTHETIC-C6",
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

    def _validate(
        self,
        bundle: dict[str, Path | str],
        shadow: Path | None = None,
        shadow_review: Path | None = None,
        expected_shadow_review_receipt_sha256: str | None = None,
        case_side_effect=None,
    ) -> dict:
        def validate() -> dict:
            return validate_aggregate(
                candidate_manifest_path=self.candidate_manifest,
                governance_manifest_path=Path(bundle["governance_path"]),
                expected_decision_sha256=str(bundle["decision_hash"]),
                shadow_manifest_path=shadow,
                shadow_review_manifest_path=shadow_review,
                expected_shadow_review_receipt_sha256=(
                    expected_shadow_review_receipt_sha256
                ),
            )

        if shadow is None:
            return validate()
        patch_arguments = (
            {"side_effect": case_side_effect}
            if case_side_effect is not None
            else {"return_value": self.shadow_case_response}
        )
        with patch("run_shadow_acceptance.run_case", **patch_arguments):
            return validate()

    def test_freeze_requires_all_three_sibling_roots_absent(self) -> None:
        for root in (
            self.governance_root,
            self.shadow_root,
            self.shadow_review_root,
        ):
            with self.subTest(root=root.name):
                root.mkdir()
                with self.assertRaisesRegex(ManifestError, "must be absent"):
                    validate_manifest(self.candidate_manifest, phase="freeze")
                root.rmdir()

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
        for root_declaration in document["post_closure_artifact_roots"]:
            root_declaration["governed_by_sha256"] = envelope_hash
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

    def test_freeze_report_builder_matches_aggregate_exact_schema(self) -> None:
        self.assertEqual(BUILDER_FREEZE_REPORT_KEYS, GATE_FREEZE_REPORT_KEYS)
        report = build_freeze_report(self.candidate_manifest)
        self.assertEqual(set(report), GATE_FREEZE_REPORT_KEYS)
        self.assertEqual(report["verifier_path"], CANDIDATE_VERIFIER_PATH)
        self.assertEqual(
            report["post_closure_root_states"],
            [
                {"root_id": "closure-governance", "state": "ABSENT"},
                {"root_id": "shadow-mvp", "state": "ABSENT"},
                {"root_id": "shadow-review", "state": "ABSENT"},
            ],
        )

    def test_post_closure_cli_without_dash_b_does_not_write_bytecode(self) -> None:
        source_root = Path(__file__).resolve().parent
        candidate_root = source_root.parents[1]
        local_import_sources = (
            "verify_post_closure_manifest.py",
            "verify_candidate_manifest.py",
            "verify_run2_acceptance.py",
            "verify_run2_crosswalk.py",
            "run_shadow_acceptance.py",
        )
        governance = self._create_governance()
        before_paths, before_hashes, before_digest = byte_inventory_snapshot(
            candidate_root
        )

        with tempfile.TemporaryDirectory(prefix="otts-post-cli-bytecode-") as raw:
            isolated = Path(raw)
            for name in local_import_sources:
                shutil.copyfile(source_root / name, isolated / name)

            child_env = os.environ.copy()
            child_env.pop("PYTHONDONTWRITEBYTECODE", None)
            child_env.pop("PYTHONPYCACHEPREFIX", None)

            help_result = subprocess.run(
                [sys.executable, "verify_post_closure_manifest.py", "--help"],
                cwd=isolated,
                env=child_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                help_result.returncode,
                0,
                msg=f"stdout={help_result.stdout!r}\nstderr={help_result.stderr!r}",
            )

            aggregate_arguments = [
                "verify_post_closure_manifest.py",
                str(self.candidate_manifest),
                "--governance-manifest",
                str(governance["governance_path"]),
                "--expected-closure-decision-sha256",
                str(governance["decision_hash"]),
            ]
            aggregate_results: dict[str, dict] = {}
            for label, command in (
                ("without_dash_b", [sys.executable, *aggregate_arguments]),
                ("with_dash_b", [sys.executable, "-B", *aggregate_arguments]),
            ):
                completed = subprocess.run(
                    command,
                    cwd=isolated,
                    env=child_env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    msg=(
                        f"{label}: stdout={completed.stdout!r}\n"
                        f"stderr={completed.stderr!r}"
                    ),
                )
                aggregate_results[label] = json.loads(completed.stdout)

            self.assertEqual(
                aggregate_results["without_dash_b"],
                aggregate_results["with_dash_b"],
            )
            aggregate = aggregate_results["without_dash_b"]
            self.assertTrue(aggregate["valid"])
            self.assertTrue(aggregate["closure_chain_valid"])
            self.assertEqual(aggregate["shadow_state"], "ABSENT_AUTHORIZED")
            self.assertFalse(aggregate["shadow_generation_valid"])
            self.assertFalse(aggregate["external_action_authority"])

            bytecode_artifacts = sorted(
                path.relative_to(isolated).as_posix()
                for path in isolated.rglob("*")
                if path.name == "__pycache__" or path.suffix == ".pyc"
            )
            self.assertEqual(bytecode_artifacts, [])

        after_paths, after_hashes, after_digest = byte_inventory_snapshot(candidate_root)
        self.assertEqual(after_paths, before_paths)
        self.assertEqual(after_hashes, before_hashes)
        self.assertEqual(after_digest, before_digest)

    def test_freeze_report_writer_rejects_candidate_and_post_closure_roots(self) -> None:
        forbidden = (
            self.candidate / "report.json",
            self.parent / "机会到交易系统-闭合记录/FREEZE_VERIFICATION_REPORT.json",
            self.parent / "机会到交易系统-shadow-mvp/FREEZE_VERIFICATION_REPORT.json",
            self.parent / "机会到交易系统-shadow-review/FREEZE_VERIFICATION_REPORT.json",
        )
        for output in forbidden:
            with self.subTest(output=output):
                with self.assertRaises(FreezeReportError):
                    write_freeze_report(self.candidate_manifest, output)
                self.assertFalse(output.exists())

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

    def test_review_receipt_external_authority_fails_even_if_rehashed(self) -> None:
        bundle = self._create_governance()
        review_path = Path(bundle["review_path"])
        review = canonical_load(review_path)
        review["external_action_authority"] = True
        write_json(review_path, review)
        self._rehash_governance_after_review_change(bundle)
        with self.assertRaisesRegex(ManifestError, "deny external action authority"):
            self._validate(bundle)

    def test_freeze_report_extra_key_fails_even_if_chain_rehashed(self) -> None:
        bundle = self._create_governance()
        freeze_path = self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        freeze = canonical_load(freeze_path)
        freeze["active_files"] = 2
        write_json(freeze_path, freeze)
        self._rehash_governance_after_freeze_change(bundle)
        with self.assertRaisesRegex(ManifestError, "freeze_report: key mismatch"):
            self._validate(bundle)

    def test_freeze_report_absolute_verifier_path_fails_when_rehashed(self) -> None:
        bundle = self._create_governance()
        freeze_path = self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        freeze = canonical_load(freeze_path)
        freeze["verifier_path"] = str(self.verifier_fixture.resolve())
        write_json(freeze_path, freeze)
        self._rehash_governance_after_freeze_change(bundle)
        with self.assertRaisesRegex(ManifestError, "verifier_path mismatch"):
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

    def _rehash_governance_after_freeze_change(
        self,
        bundle: dict[str, Path | str],
    ) -> None:
        freeze_path = self.governance_root / "FREEZE_VERIFICATION_REPORT.json"
        review_path = Path(bundle["review_path"])
        decision_path = Path(bundle["decision_path"])
        governance_path = Path(bundle["governance_path"])
        freeze_hash = sha256_file(freeze_path)
        review = canonical_load(review_path)
        review["freeze_report_sha256"] = freeze_hash
        write_json(review_path, review)
        review_hash = sha256_file(review_path)
        decision = canonical_load(decision_path)
        decision["freeze_report_sha256"] = freeze_hash
        decision["independent_review_receipt_sha256"] = review_hash
        write_json(decision_path, decision)
        decision_hash = sha256_file(decision_path)
        governance = canonical_load(governance_path)
        governance["freeze_report"]["sha256"] = freeze_hash
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
        program_path = self.shadow_root / "program.json"
        fixture = self.shadow_root / "fixtures" / "case.json"
        program = {
            "schema_version": "otts.shadow-declarative-ir/1",
            "program_id": "SYNTHETIC-SAFE-IR",
            "input_type": "JSON",
            "output_type": "JSON",
            "nodes": [
                {"id": "input", "op": "INPUT"},
                {
                    "id": "value",
                    "op": "JSON_POINTER",
                    "source": "input",
                    "pointer": "/value",
                },
                {
                    "id": "result",
                    "op": "BUILD_OBJECT",
                    "entries": [{"key": "value", "ref": "value"}],
                },
            ],
            "result_ref": "result",
        }
        fixture_document = {"value": "synthetic fixture"}
        result_document = {"value": "synthetic fixture"}
        write_json(program_path, program)
        write_json(fixture, fixture_document)
        expected_result_hash = rsa.sha256_bytes(rsa.canonical_bytes(result_document))
        result_bytes = rsa.canonical_bytes(result_document)
        policy_snapshot = rsa.read_once_regular(
            self.policy_fixture, "synthetic policy", 524288
        )
        runner_snapshot = rsa.read_once_regular(
            self.runner_fixture, "synthetic runner", 2 * 1024 * 1024
        )
        policy = rsa.load_policy_snapshot(policy_snapshot)
        graph = rsa.validate_program(program, policy)
        synthetic_module_path = (
            rsa.TRUSTED_PYTHON_HOME / "lib/python3.9/hashlib.py"
        )
        synthetic_module_rows = [
            {
                "path": str(synthetic_module_path),
                "sha256": sha256_file(synthetic_module_path),
                "byte_length": synthetic_module_path.stat().st_size,
                "modules": ["hashlib"],
            }
        ]
        synthetic_runtime_observation = {
            "python_version": "synthetic-phase-fixture",
            "python_implementation_cache_tag": "cpython-39",
            "python_executable": str(rsa.TRUSTED_PYTHON),
            "python_prefix": str(rsa.TRUSTED_PYTHON_HOME),
            "loaded_module_files": synthetic_module_rows,
            "loaded_module_file_closure_digest_sha256": rsa.sha256_json(
                synthetic_module_rows
            ),
            "closure_scope": (
                "ACTUALLY_LOADED_PYTHON_MODULE_FILES_AT_RESPONSE_MEASUREMENT"
            ),
            "full_dynamic_library_and_host_runtime_closure_proven": False,
        }
        self.shadow_case_response = {
            "result_sha256": expected_result_hash,
            "result_type": rsa.json_type_name(result_document),
            "result_byte_length": len(result_bytes),
            "output_inventory_digest_sha256": rsa.sha256_json([]),
            "sandbox_observed_enforcement": {
                "CHILD_PROCESS_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_READ_DENIED": "OBSERVED_DENIED",
                "EXTERNAL_WRITE_DENIED": "OBSERVED_DENIED",
                "NETWORK_LOOPBACK_BIND_DENIED": "OBSERVED_DENIED",
            },
            "runtime_observation": synthetic_runtime_observation,
        }
        shadow_manifest = self.shadow_root / "SHADOW_ARTIFACT_MANIFEST.json"
        shadow = {
            "schema_version": "otts.shadow-artifact-manifest/2",
            "artifact_id": "SYNTHETIC-SHADOW",
            "artifact_kind": "READ_ONLY_SHADOW_MVP",
            "status": "SHADOW_IMPLEMENTATION_CANDIDATE",
            "scope": "LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY",
            "candidate_id": "SYNTHETIC-C6",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "governance_manifest_sha256": sha256_file(Path(bundle["governance_path"])),
            "independent_review_receipt_sha256": sha256_file(Path(bundle["review_path"])),
            "closure_decision_sha256": str(bundle["decision_hash"]),
            "action_envelope_path": ACTION_ENVELOPE_PATH,
            "action_envelope_sha256": self.envelope_hash,
            "capability_policy_path": CAPABILITY_POLICY_PATH,
            "capability_policy_sha256": sha256_file(self.policy_fixture),
            "program": program_path.name,
            "acceptance_cases": [
                {
                    "case_id": "SAFE-1",
                    "fixture_path": "fixtures/case.json",
                    "expected_result_sha256": expected_result_hash,
                }
            ],
            "snapshot_ledger": {
                "path": "SNAPSHOT_LEDGER.json",
                "sha256": "0" * 64,
            },
            "sbom": {"path": "SBOM.json", "sha256": "0" * 64},
            "capability_report": {
                "path": "CAPABILITY_REPORT.json",
                "sha256": "0" * 64,
            },
            "acceptance_test_report": {
                "path": "ACCEPTANCE_TEST_REPORT.json",
                "sha256": "0" * 64,
            },
            "external_action_authority": False,
            "entries": [
                {
                    "path": program_path.name,
                    "sha256": sha256_file(program_path),
                    "role": "ir-program",
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [],
                },
                {
                    "path": "fixtures/case.json",
                    "sha256": sha256_file(fixture),
                    "role": "fixture",
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [],
                }
            ],
        }
        sbom, capability, initial_entries = rsa.build_static_reports(
            shadow_root=self.shadow_root,
            shadow=shadow,
            policy_path=self.policy_fixture,
            policy_snapshot=policy_snapshot,
            runner_path=self.runner_fixture,
            runner_snapshot=runner_snapshot,
        )
        snapshot_ledger = rsa.build_snapshot_ledger(
            entries=initial_entries,
            policy_snapshot=policy_snapshot,
            runner_snapshot=runner_snapshot,
        )
        snapshot_ledger_path = self.shadow_root / "SNAPSHOT_LEDGER.json"
        write_json(snapshot_ledger_path, snapshot_ledger)
        shadow["entries"].append(
            {
                "path": snapshot_ledger_path.name,
                "sha256": sha256_file(snapshot_ledger_path),
                "role": "snapshot-ledger",
                "authority_status": "NO_EXTERNAL_AUTHORITY",
                "depends_on": [program_path.name, fixture.relative_to(self.shadow_root).as_posix()],
            }
        )
        shadow["snapshot_ledger"]["sha256"] = sha256_file(snapshot_ledger_path)
        sbom_path = self.shadow_root / "SBOM.json"
        write_json(sbom_path, sbom)
        capability["sbom_sha256"] = sha256_file(sbom_path)
        capability_path = self.shadow_root / "CAPABILITY_REPORT.json"
        write_json(capability_path, capability)
        case_results = [
            {
                "case_id": "SAFE-1",
                "fixture_path": fixture.relative_to(self.shadow_root).as_posix(),
                "fixture_sha256": sha256_file(fixture),
                "expected_result_sha256": expected_result_hash,
                "actual_result_sha256": expected_result_hash,
                "result_type": self.shadow_case_response["result_type"],
                "result_byte_length": self.shadow_case_response["result_byte_length"],
                "output_inventory_digest_sha256": self.shadow_case_response[
                    "output_inventory_digest_sha256"
                ],
                "loaded_module_file_closure_digest_sha256": (
                    synthetic_runtime_observation[
                        "loaded_module_file_closure_digest_sha256"
                    ]
                ),
            }
        ]
        runtime_tcb = rsa.runtime_tcb_document(runner_snapshot)
        runtime_tcb["loaded_python_module_file_closure"] = (
            synthetic_runtime_observation
        )
        test_report = {
            "schema_version": "otts.shadow-acceptance-test-report/3",
            "result": "LOCAL_DETERMINISTIC_DECLARATIVE_EVALUATION_PASS",
            "runner_sha256": sha256_file(self.runner_fixture),
            "policy_sha256": sha256_file(self.policy_fixture),
            "sbom_sha256": sha256_file(sbom_path),
            "capability_report_sha256": sha256_file(capability_path),
            "program_sha256": sha256_file(program_path),
            "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
            "snapshot_ledger_sha256": sha256_file(snapshot_ledger_path),
            "runtime_tcb_digest_sha256": rsa.sha256_json(runtime_tcb),
            "loaded_module_file_closure_digest_sha256": (
                synthetic_runtime_observation[
                    "loaded_module_file_closure_digest_sha256"
                ]
            ),
            "acceptance_output_set_digest_sha256": rsa.sha256_json(case_results),
            "program": program_path.name,
            "cases": case_results,
            "language_level_artifact_executable_constructs": "ABSENT_BY_EXACT_SCHEMA",
            "os_sandbox_observed_enforcement": self.shadow_case_response[
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
                "CLOSED_IR_HAS_NO_EXEC_OPCODE"
            ),
            "memory_boundary": (
                "NO_HOST_RSS_LIMIT_ON_DARWIN; "
                "FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED"
            ),
            "aggregate_deadline_enforced": True,
            "aggregate_wall_timeout_seconds": policy["limits"][
                "aggregate_wall_timeout_seconds"
            ],
            "runtime_authority": False,
            "deployment_authority": False,
            "freeze_authority": False,
            "external_action_authority": False,
        }
        test_report_path = self.shadow_root / "ACCEPTANCE_TEST_REPORT.json"
        write_json(test_report_path, test_report)
        for path, role in (
            (sbom_path, "sbom"),
            (capability_path, "capability-report"),
            (test_report_path, "acceptance-report"),
        ):
            shadow["entries"].append(
                {
                    "path": path.name,
                    "sha256": sha256_file(path),
                    "role": role,
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [program_path.name],
                }
            )
        shadow["sbom"]["sha256"] = sha256_file(sbom_path)
        shadow["capability_report"]["sha256"] = sha256_file(capability_path)
        shadow["acceptance_test_report"]["sha256"] = sha256_file(test_report_path)
        write_json(shadow_manifest, shadow)
        return shadow_manifest, program_path

    def test_shadow_status_overclaim_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        shadow["status"] = "PRODUCTION_AUTHORIZED"
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "status exceeds"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_acceptance_case_count_fixed_limit_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        fixed_limit = rsa.FIXED_LIMITS["max_acceptance_cases"]
        template = shadow["acceptance_cases"][0]
        shadow["acceptance_cases"] = [
            {
                **template,
                "case_id": f"SAFE-{index}",
            }
            for index in range(fixed_limit + 1)
        ]
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "within fixed limit"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_manifest_entry_count_fixed_limit_fails_before_reads(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        while len(shadow["entries"]) <= rsa.FIXED_LIMITS["max_manifest_entries"]:
            index = len(shadow["entries"])
            shadow["entries"].append(
                {
                    "path": f"not-materialized-{index}.txt",
                    "sha256": "0" * 64,
                    "role": "documentation",
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [],
                }
            )
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "within fixed limit"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_total_input_bytes_fixed_limit_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        payload = "x" * 500000
        for index in range(9):
            path = self.shadow_root / f"large-report-{index}.txt"
            write_text(path, payload)
            shadow["entries"].append(
                {
                    "path": path.name,
                    "sha256": sha256_file(path),
                    "role": "documentation",
                    "authority_status": "NO_EXTERNAL_AUTHORITY",
                    "depends_on": [],
                }
            )
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "fixed total input bytes"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_external_authority_claim_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        shadow["external_action_authority"] = True
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "deny external"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_tampered_snapshot_ledger_fails_even_if_rehashed(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        ledger_path = self.shadow_root / shadow["snapshot_ledger"]["path"]
        ledger = canonical_load(ledger_path)
        ledger["external_action_authority"] = True
        write_json(ledger_path, ledger)
        forged_hash = sha256_file(ledger_path)
        shadow["snapshot_ledger"]["sha256"] = forged_hash
        for entry in shadow["entries"]:
            if entry["path"] == ledger_path.name:
                entry["sha256"] = forged_hash
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(
            ManifestError, "supplied report differs from deterministic reconstruction"
        ):
            self._validate(bundle, shadow_manifest)

    def test_shadow_tampered_acceptance_digest_fails_even_if_rehashed(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        report_path = self.shadow_root / shadow["acceptance_test_report"]["path"]
        report = canonical_load(report_path)
        report["runtime_tcb_digest_sha256"] = "f" * 64
        write_json(report_path, report)
        forged_hash = sha256_file(report_path)
        shadow["acceptance_test_report"]["sha256"] = forged_hash
        for entry in shadow["entries"]:
            if entry["path"] == report_path.name:
                entry["sha256"] = forged_hash
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(
            ManifestError, "supplied report differs from deterministic reconstruction"
        ):
            self._validate(bundle, shadow_manifest)

    def test_shadow_entry_drift_during_acceptance_fails_final_snapshot_check(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, program_path = self._create_shadow(bundle)

        def mutate_after_snapshot(**_kwargs):
            write_text(program_path, "same-name replacement after snapshot\n")
            return self.shadow_case_response

        with self.assertRaisesRegex(ManifestError, "snapshot changed"):
            self._validate(
                bundle,
                shadow_manifest,
                case_side_effect=mutate_after_snapshot,
            )

    def test_candidate_drift_during_acceptance_fails_final_candidate_check(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)

        def mutate_candidate_after_snapshot(**_kwargs):
            write_text(self.envelope, "candidate drift after governance snapshot\n")
            return self.shadow_case_response

        with self.assertRaisesRegex(ManifestError, "hash mismatch"):
            self._validate(
                bundle,
                shadow_manifest,
                case_side_effect=mutate_candidate_after_snapshot,
            )

    def test_shadow_executable_program_suffix_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, program_path = self._create_shadow(bundle)
        executable_path = program_path.with_suffix(".py")
        program_path.rename(executable_path)
        shadow = canonical_load(shadow_manifest)
        old_name = program_path.name
        shadow["program"] = executable_path.name
        for entry in shadow["entries"]:
            if entry["path"] == old_name:
                entry["path"] = executable_path.name
            entry["depends_on"] = [
                executable_path.name if dependency == old_name else dependency
                for dependency in entry["depends_on"]
            ]
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "executable/native suffix"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_executable_program_mode_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, program_path = self._create_shadow(bundle)
        os.chmod(program_path, 0o755)
        with self.assertRaisesRegex(ManifestError, "executable mode bits"):
            self._validate(bundle, shadow_manifest)

    def _create_shadow_review(
        self,
        bundle: dict[str, Path | str],
        shadow_manifest: Path,
    ) -> tuple[Path, Path, str]:
        self.shadow_review_root.mkdir()
        shadow = canonical_load(shadow_manifest)
        acceptance_report = canonical_load(
            self.shadow_root / shadow["acceptance_test_report"]["path"]
        )
        receipt_path = (
            self.shadow_review_root / "SHADOW_INDEPENDENT_REVIEW_RECEIPT.json"
        )
        receipt = {
            "schema_version": "otts.shadow-independent-review-receipt/1",
            "receipt_id": "SYNTHETIC-SHADOW-REVIEW",
            "reviewer_id": "synthetic-independent-shadow-reviewer",
            "independence_assertion": "Synthetic independent test fixture only.",
            "review_scope": (
                "EXACT_DECLARATIVE_SHADOW_MANIFEST_POLICY_SNAPSHOT_RUNTIME_AND_OUTPUTS"
            ),
            "verdict": "PASS",
            "unresolved_critical": [],
            "unresolved_major": [],
            "residual_limits": [
                "Synthetic fixture; trusted runtime is outside the artifact SBOM."
            ],
            "candidate_id": "SYNTHETIC-C6",
            "parent_candidate_manifest_sha256": self.candidate_hash,
            "governance_manifest_sha256": sha256_file(Path(bundle["governance_path"])),
            "closure_decision_sha256": str(bundle["decision_hash"]),
            "shadow_manifest_sha256": sha256_file(shadow_manifest),
            "capability_policy_sha256": sha256_file(self.policy_fixture),
            "sbom_sha256": shadow["sbom"]["sha256"],
            "capability_report_sha256": shadow["capability_report"]["sha256"],
            "acceptance_test_report_sha256": shadow["acceptance_test_report"][
                "sha256"
            ],
            "acceptance_runner_sha256": sha256_file(self.runner_fixture),
            "program_sha256": acceptance_report["program_sha256"],
            "snapshot_ledger_sha256": shadow["snapshot_ledger"]["sha256"],
            "node_graph_digest_sha256": acceptance_report[
                "node_graph_digest_sha256"
            ],
            "runtime_tcb_digest_sha256": acceptance_report[
                "runtime_tcb_digest_sha256"
            ],
            "loaded_module_file_closure_digest_sha256": acceptance_report[
                "loaded_module_file_closure_digest_sha256"
            ],
            "acceptance_output_set_digest_sha256": acceptance_report[
                "acceptance_output_set_digest_sha256"
            ],
            "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
            "artifact_external_action_capability_absent": True,
            "exact_opened_unlinked_snapshot_execution": True,
            "staged_target_controlled_pathname_reopen_count": 0,
            "same_uid_concurrent_mutation_resistance_proven": False,
            "memory_boundary": acceptance_report["memory_boundary"],
            "aggregate_deadline_enforced": True,
            "aggregate_wall_timeout_seconds": acceptance_report[
                "aggregate_wall_timeout_seconds"
            ],
            "host_level_universal_noninterference_proven": False,
            "local_declarative_shadow_candidate_accepted": True,
            "capability_authority": False,
            "runtime_authority": False,
            "deployment_authority": False,
            "freeze_authority": False,
            "external_action_authority": False,
        }
        write_json(receipt_path, receipt)
        receipt_hash = sha256_file(receipt_path)
        review_manifest = self.shadow_review_root / "SHADOW_REVIEW_MANIFEST.json"
        write_json(
            review_manifest,
            {
                "schema_version": "otts.shadow-review-manifest/1",
                "artifact_kind": "SHADOW_INDEPENDENT_REVIEW",
                "candidate_id": "SYNTHETIC-C6",
                "parent_candidate_manifest_sha256": self.candidate_hash,
                "shadow_manifest": {
                    "path": (
                        "机会到交易系统-shadow-mvp/SHADOW_ARTIFACT_MANIFEST.json"
                    ),
                    "sha256": sha256_file(shadow_manifest),
                },
                "independent_review_receipt": {
                    "path": receipt_path.name,
                    "sha256": receipt_hash,
                },
            },
        )
        return review_manifest, receipt_path, receipt_hash

    def test_valid_shadow_is_unreviewed_and_all_authorities_false(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, source = self._create_shadow(bundle)
        result = self._validate(bundle, shadow_manifest)
        self.assertEqual(
            result["shadow_state"], "PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED"
        )
        self.assertFalse(result["shadow_generation_valid"])
        self.assertFalse(result["local_shadow_candidate_accepted"])
        self.assertFalse(result["capability_authority"])
        self.assertFalse(result["runtime_authority"])
        self.assertFalse(result["external_action_authority"])
        frozen_candidate_hash = sha256_file(self.candidate_manifest)
        write_text(source, "tampered shadow\n")
        with self.assertRaisesRegex(ManifestError, "hash mismatch"):
            self._validate(bundle, shadow_manifest)
        self.assertEqual(sha256_file(self.candidate_manifest), frozen_candidate_hash)

    def test_exact_independent_shadow_review_allows_only_limited_candidate_state(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        review_manifest, _, receipt_hash = self._create_shadow_review(
            bundle, shadow_manifest
        )
        result = self._validate(
            bundle,
            shadow_manifest,
            review_manifest,
            receipt_hash,
        )
        self.assertEqual(
            result["shadow_state"],
            "PRESENT_ACCEPTED_LOCAL_DECLARATIVE_SHADOW_CANDIDATE",
        )
        self.assertTrue(result["local_shadow_candidate_accepted"])
        self.assertFalse(result["capability_authority"])
        self.assertFalse(result["runtime_authority"])
        self.assertFalse(result["external_action_authority"])

    def test_shadow_review_hash_mismatch_and_forged_pass_fail_closed(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        review_manifest, receipt_path, receipt_hash = self._create_shadow_review(
            bundle, shadow_manifest
        )
        with self.assertRaisesRegex(ManifestError, "caller expected exact hash"):
            self._validate(bundle, shadow_manifest, review_manifest, "0" * 64)

        receipt = canonical_load(receipt_path)
        receipt["runtime_authority"] = True
        write_json(receipt_path, receipt)
        forged_hash = sha256_file(receipt_path)
        review = canonical_load(review_manifest)
        review["independent_review_receipt"]["sha256"] = forged_hash
        write_json(review_manifest, review)
        with self.assertRaisesRegex(ManifestError, "runtime_authority=false"):
            self._validate(bundle, shadow_manifest, review_manifest, forged_hash)
        self.assertNotEqual(receipt_hash, forged_hash)

    def test_shadow_review_tampered_ledger_digest_fails_even_if_rehashed(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        review_manifest, receipt_path, receipt_hash = self._create_shadow_review(
            bundle, shadow_manifest
        )
        receipt = canonical_load(receipt_path)
        receipt["snapshot_ledger_sha256"] = "f" * 64
        write_json(receipt_path, receipt)
        forged_hash = sha256_file(receipt_path)
        review = canonical_load(review_manifest)
        review["independent_review_receipt"]["sha256"] = forged_hash
        write_json(review_manifest, review)
        with self.assertRaisesRegex(
            ManifestError, "receipt snapshot_ledger_sha256 mismatch"
        ):
            self._validate(bundle, shadow_manifest, review_manifest, forged_hash)
        self.assertNotEqual(receipt_hash, forged_hash)

    def test_shadow_review_cannot_claim_same_uid_race_resistance(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        review_manifest, receipt_path, receipt_hash = self._create_shadow_review(
            bundle, shadow_manifest
        )
        receipt = canonical_load(receipt_path)
        receipt["same_uid_concurrent_mutation_resistance_proven"] = True
        write_json(receipt_path, receipt)
        forged_hash = sha256_file(receipt_path)
        review = canonical_load(review_manifest)
        review["independent_review_receipt"]["sha256"] = forged_hash
        write_json(review_manifest, review)
        with self.assertRaisesRegex(ManifestError, "same-uid race non-claim"):
            self._validate(bundle, shadow_manifest, review_manifest, forged_hash)
        self.assertNotEqual(receipt_hash, forged_hash)

    def test_shadow_review_reopen_count_rejects_json_boolean_false(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        review_manifest, receipt_path, receipt_hash = self._create_shadow_review(
            bundle, shadow_manifest
        )
        receipt = canonical_load(receipt_path)
        receipt["staged_target_controlled_pathname_reopen_count"] = False
        write_json(receipt_path, receipt)
        forged_hash = sha256_file(receipt_path)
        review = canonical_load(review_manifest)
        review["independent_review_receipt"]["sha256"] = forged_hash
        write_json(review_manifest, review)
        with self.assertRaisesRegex(ManifestError, "pathname reopen"):
            self._validate(bundle, shadow_manifest, review_manifest, forged_hash)
        self.assertNotEqual(receipt_hash, forged_hash)

    def test_present_shadow_review_root_without_receipt_or_expected_hash_fails(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        self.shadow_review_root.mkdir()
        write_json(self.shadow_review_root / "SHADOW_REVIEW_MANIFEST.json", {})
        with self.assertRaisesRegex(ManifestError, "requires explicit review"):
            self._validate(bundle, shadow_manifest)

    def test_shadow_cannot_self_fill_accepted_status(self) -> None:
        bundle = self._create_governance()
        shadow_manifest, _ = self._create_shadow(bundle)
        shadow = canonical_load(shadow_manifest)
        shadow["local_shadow_candidate_accepted"] = True
        write_json(shadow_manifest, shadow)
        with self.assertRaisesRegex(ManifestError, "key mismatch"):
            self._validate(bundle, shadow_manifest)


def canonical_load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
