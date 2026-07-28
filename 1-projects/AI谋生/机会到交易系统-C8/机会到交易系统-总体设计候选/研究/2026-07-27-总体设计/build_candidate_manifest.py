#!/usr/bin/env python3
"""Build the canonical C8 candidate manifest from an explicit closed inventory.

The builder is intentionally not a discovery tool.  Every admissible path,
role, authority status and dependency is declared below.  An unexpected file,
missing file, non-regular node or hardlink stops generation instead of being
silently added to the candidate.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True

from verify_candidate_manifest import (  # noqa: E402
    EXPECTED_CANDIDATE_SCOPE,
    EXPECTED_CANDIDATE_STATUS,
    REAL_CANDIDATE_ID,
)


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = "研究/2026-07-27-总体设计"
MANIFEST_PATH = ROOT / "FINAL_CANDIDATE_MANIFEST.json"
ENVELOPE = f"{RESEARCH}/READ_ONLY_SHADOW_ACTION_ENVELOPE.md"


class BuildError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def spec(
    role: str,
    authority_status: str,
    *depends_on: str,
) -> dict[str, Any]:
    return {
        "role": role,
        "authority_status": authority_status,
        "depends_on": list(depends_on),
    }


P = f"{RESEARCH}/SEARCH_SATURATION_PROTOCOL.md"
RP = f"{RESEARCH}/RESEARCH_PROTOCOL.md"
CLAIMS = f"{RESEARCH}/02-主张与证据地图.md"
DESIGN = f"{RESEARCH}/03-机会到交易系统-总体设计.md"
LOG = f"{RESEARCH}/04-来源与检索日志.md"
S1_LEAD = f"{RESEARCH}/ssp-run2/lead-screening/S1.md"
S1_INDEPENDENT = f"{RESEARCH}/ssp-run2/independent-screening/S1.md"
S1_JOINT = f"{RESEARCH}/ssp-run2/S1_JOINT_ADJUDICATION.md"
S2_LEAD = f"{RESEARCH}/ssp-run2/lead-screening/S2.md"
S2_INDEPENDENT = f"{RESEARCH}/ssp-run2/independent-screening/S2.md"
S2_JOINT = f"{RESEARCH}/ssp-run2/S2_JOINT_ADJUDICATION.md"
S2_RECEIPT = f"{RESEARCH}/ssp-run2/S2_INDEPENDENT_ACCEPTANCE_RECEIPT.md"
HUMAN_CROSSWALK = f"{RESEARCH}/RUN2_CLAIM_EVIDENCE_CROSSWALK.md"
JSONL_CROSSWALK = f"{RESEARCH}/RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl"
CROSSWALK_VERIFIER = f"{RESEARCH}/verify_run2_crosswalk.py"
CROSSWALK_TEST = f"{RESEARCH}/test_run2_crosswalk.py"
FINAL_STATUS = f"{RESEARCH}/ssp-run2/FINAL_RUN_STATUS.md"
FINAL_STATUS_RECEIPT = (
    f"{RESEARCH}/ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json"
)
ACCEPTANCE_VERIFIER = f"{RESEARCH}/verify_run2_acceptance.py"
ACCEPTANCE_TEST = f"{RESEARCH}/test_run2_acceptance.py"
EXECUTION = f"{RESEARCH}/ssp-run2/EXECUTION_MANIFEST.md"
S1_RAW_MANIFEST = f"{RESEARCH}/ssp-run2/S1_RAW_MANIFEST.md"
S2_RAW_MANIFEST = f"{RESEARCH}/ssp-run2/S2_RAW_MANIFEST.md"
MATRIX = f"{RESEARCH}/RESEARCH_CLOSURE_PREDICATE_MATRIX.md"
CANDIDATE_VERIFIER = f"{RESEARCH}/verify_candidate_manifest.py"
POST_VERIFIER = f"{RESEARCH}/verify_post_closure_manifest.py"
PHASE_TEST = f"{RESEARCH}/test_phase_manifests.py"
BUILDER = f"{RESEARCH}/build_candidate_manifest.py"
FREEZE_BUILDER = f"{RESEARCH}/build_freeze_report.py"
CAPABILITY_POLICY = f"{RESEARCH}/SHADOW_CAPABILITY_POLICY.json"
SHADOW_ACCEPTANCE_RUNNER = f"{RESEARCH}/run_shadow_acceptance.py"
SHADOW_ACCEPTANCE_TEST = f"{RESEARCH}/test_shadow_acceptance.py"
SANDBOX_PROBE_REPORT = f"{RESEARCH}/C6_SANDBOX_PROBE_REPORT.md"
C7_SHADOW_FAILURE = f"{RESEARCH}/C7_SHADOW_FAILURE_RECORD.md"
C8_DOMAIN_GATE_REPORT = f"{RESEARCH}/C8_DOMAIN_GATE_REVIEW_REPORT.md"


SPECS: dict[str, dict[str, Any]] = {
    "LEGACY_STATUS.md": spec(
        "external legacy authority quarantine",
        "LEGACY_UNQUALIFIED_NO_REUSE_AUTHORITY",
    ),
    "LEGACY_CODE_GAP_AUDIT.md": spec(
        "external legacy implementation gap audit",
        "DIAGNOSTIC_ONLY_NO_REUSE_AUTHORITY",
        "LEGACY_STATUS.md",
    ),
    "EXTERNAL_LEGACY_QUARANTINE.md": spec(
        "boundary record for mutable external predecessor root",
        "BOUNDARY_EVIDENCE_ONLY",
        "LEGACY_STATUS.md",
        "LEGACY_CODE_GAP_AUDIT.md",
    ),
    f"{RESEARCH}/01-黄仁勋访谈核查.md": spec(
        "seed interview identity and scope check",
        "SEED_ONLY_NOT_THEORETICAL_FOUNDATION",
    ),
    P: spec(
        "pre-registered search saturation protocol",
        "FROZEN_PROTOCOL_EVIDENCE_ONLY",
    ),
    RP: spec(
        "research closure protocol",
        "CLOSURE_RULES_NO_SELF_APPROVAL",
        P,
        C7_SHADOW_FAILURE,
        f"{RESEARCH}/FINAL_REVIEW_HISTORY.md",
    ),
    f"{RESEARCH}/FINAL_REVIEW_HISTORY.md": spec(
        "immutable predecessor rejection and remediation history",
        "HISTORY_ONLY_NO_SUCCESSOR_APPROVAL",
        C7_SHADOW_FAILURE,
    ),
    C7_SHADOW_FAILURE: spec(
        "exact C7 post-closure shadow rejection and successor repair boundary",
        "HISTORY_ONLY_NO_SUCCESSOR_APPROVAL",
    ),
    f"{RESEARCH}/verify_run2_crosswalk.py": spec(
        "independent reconstruction verifier for every final CE-IN row",
        "MECHANICAL_VALIDATION_ONLY",
        S1_LEAD,
        S1_INDEPENDENT,
        S1_JOINT,
        S2_LEAD,
        S2_INDEPENDENT,
        S2_JOINT,
        HUMAN_CROSSWALK,
    ),
    f"{RESEARCH}/test_run2_crosswalk.py": spec(
        "negative and positive regression tests for exhaustive crosswalk",
        "MECHANICAL_TEST_ONLY",
        CROSSWALK_VERIFIER,
        JSONL_CROSSWALK,
    ),
    ACCEPTANCE_VERIFIER: spec(
        "exact-hash Run2 final-status acceptance receipt verifier",
        "MECHANICAL_VALIDATION_ONLY",
        FINAL_STATUS_RECEIPT,
        CROSSWALK_VERIFIER,
        JSONL_CROSSWALK,
    ),
    ACCEPTANCE_TEST: spec(
        "negative and positive regression tests for Run2 acceptance",
        "MECHANICAL_TEST_ONLY",
        ACCEPTANCE_VERIFIER,
        FINAL_STATUS_RECEIPT,
    ),
    CANDIDATE_VERIFIER: spec(
        "closed candidate inventory and phase verifier",
        "MECHANICAL_VALIDATION_ONLY",
        ACCEPTANCE_VERIFIER,
        ENVELOPE,
    ),
    CAPABILITY_POLICY: spec(
        "closed declarative shadow IR and capability policy",
        "LANGUAGE_AND_RUNTIME_POLICY_NO_EXTERNAL_AUTHORITY",
        ENVELOPE,
        SANDBOX_PROBE_REPORT,
    ),
    SANDBOX_PROBE_REPORT: spec(
        "host-specific sandbox probe evidence and non-claims",
        "LOCAL_PROBE_EVIDENCE_ONLY_NO_PORTABLE_ATTESTATION",
        ENVELOPE,
    ),
    SHADOW_ACCEPTANCE_RUNNER: spec(
        "exact-snapshot declarative shadow interpreter and acceptance runner",
        "MECHANICAL_LOCAL_EVALUATION_ONLY",
        CAPABILITY_POLICY,
        SANDBOX_PROBE_REPORT,
        ENVELOPE,
    ),
    SHADOW_ACCEPTANCE_TEST: spec(
        "adversarial tests for declarative shadow capability and runtime boundary",
        "MECHANICAL_TEST_ONLY",
        SHADOW_ACCEPTANCE_RUNNER,
        CAPABILITY_POLICY,
        SANDBOX_PROBE_REPORT,
    ),
    POST_VERIFIER: spec(
        "post-closure governance and shadow aggregate verifier",
        "MECHANICAL_VALIDATION_ONLY",
        CANDIDATE_VERIFIER,
        CAPABILITY_POLICY,
        SHADOW_ACCEPTANCE_RUNNER,
        ENVELOPE,
    ),
    PHASE_TEST: spec(
        "phase-boundary fail-closed regression tests",
        "MECHANICAL_TEST_ONLY",
        CANDIDATE_VERIFIER,
        POST_VERIFIER,
        SHADOW_ACCEPTANCE_TEST,
        FREEZE_BUILDER,
        ENVELOPE,
    ),
    FREEZE_BUILDER: spec(
        "exact-schema external freeze report builder",
        "MECHANICAL_GENERATION_ONLY",
        CANDIDATE_VERIFIER,
    ),
    C8_DOMAIN_GATE_REPORT: spec(
        "exact-byte C8 domain Gate code and interface review report",
        "REVIEW_EVIDENCE_ONLY_NO_SELF_APPROVAL",
        C7_SHADOW_FAILURE,
        CAPABILITY_POLICY,
        SHADOW_ACCEPTANCE_RUNNER,
        SHADOW_ACCEPTANCE_TEST,
        POST_VERIFIER,
        PHASE_TEST,
        ACCEPTANCE_VERIFIER,
        ACCEPTANCE_TEST,
    ),
    BUILDER: spec(
        "explicit closed-inventory canonical manifest builder",
        "MECHANICAL_GENERATION_ONLY",
        CANDIDATE_VERIFIER,
    ),
}


RAW_FILES: dict[str, list[str]] = {"S1": [], "S2": []}
for stage in ("S1", "S2"):
    for number in range(1, 14):
        path = f"{RESEARCH}/ssp-run2/raw-search/{stage}-K{number:02d}.md"
        RAW_FILES[stage].append(path)
        SPECS[path] = spec(
            f"{stage} frozen raw search response",
            "RAW_RESEARCH_INPUT_NO_EXTERNAL_AUTHORITY",
            P,
        )


SPECS.update(
    {
        EXECUTION: spec(
            "Run2 execution identity and ordering record",
            "RUN_IDENTITY_EVIDENCE_ONLY",
            P,
        ),
        S1_RAW_MANIFEST: spec(
            "S1 raw response identity manifest",
            "RAW_INVENTORY_EVIDENCE_ONLY",
            P,
            EXECUTION,
            *RAW_FILES["S1"],
        ),
        S2_RAW_MANIFEST: spec(
            "S2 raw response identity manifest",
            "RAW_INVENTORY_EVIDENCE_ONLY",
            P,
            EXECUTION,
            *RAW_FILES["S2"],
        ),
        S1_LEAD: spec(
            "sealed S1 lead screening ledger",
            "SCREENING_EVIDENCE_ONLY",
            P,
            EXECUTION,
            S1_RAW_MANIFEST,
        ),
        S1_INDEPENDENT: spec(
            "sealed S1 independent screening ledger",
            "SCREENING_EVIDENCE_ONLY",
            P,
            EXECUTION,
            S1_RAW_MANIFEST,
        ),
        S1_JOINT: spec(
            "S1 joint adjudication",
            "ROUND_ADJUDICATION_ONLY",
            P,
            S1_RAW_MANIFEST,
            S1_LEAD,
            S1_INDEPENDENT,
        ),
        S2_LEAD: spec(
            "sealed S2 lead screening ledger",
            "SCREENING_EVIDENCE_ONLY",
            P,
            EXECUTION,
            S2_RAW_MANIFEST,
            S1_JOINT,
        ),
        S2_INDEPENDENT: spec(
            "sealed S2 independent screening ledger",
            "SCREENING_EVIDENCE_ONLY",
            P,
            EXECUTION,
            S2_RAW_MANIFEST,
            S1_JOINT,
        ),
        S2_JOINT: spec(
            "S2 joint adjudication",
            "ROUND_ADJUDICATION_ONLY",
            P,
            S2_RAW_MANIFEST,
            S2_LEAD,
            S2_INDEPENDENT,
        ),
        S2_RECEIPT: spec(
            "independent exact-byte acceptance of S2 joint only",
            "S2_ROUND_ACCEPTANCE_ONLY",
            S2_JOINT,
        ),
        CLAIMS: spec(
            "typed Claim RQ DD evidence and unknown map",
            "DESIGN_EVIDENCE_ONLY",
            RP,
            S1_JOINT,
            S2_JOINT,
            S2_RECEIPT,
            C7_SHADOW_FAILURE,
        ),
        HUMAN_CROSSWALK: spec(
            "human-readable direct-use CE to Claim RQ DD crosswalk",
            "SYNTHESIS_MAP_NO_EXTERNAL_AUTHORITY",
            CLAIMS,
            S1_JOINT,
            S2_JOINT,
            S2_RECEIPT,
        ),
        JSONL_CROSSWALK: spec(
            "canonical exhaustive final CE-IN crosswalk",
            "EXHAUSTIVE_LEDGER_NO_EXTERNAL_AUTHORITY",
            HUMAN_CROSSWALK,
            S1_LEAD,
            S1_INDEPENDENT,
            S1_JOINT,
            S2_LEAD,
            S2_INDEPENDENT,
            S2_JOINT,
        ),
        FINAL_STATUS: spec(
            "lead Run2 final-status object",
            "RUN2_CATEGORY_SATURATION_PROPOSAL_ONLY",
            P,
            EXECUTION,
            S1_RAW_MANIFEST,
            S1_LEAD,
            S1_INDEPENDENT,
            S1_JOINT,
            S2_RAW_MANIFEST,
            S2_LEAD,
            S2_INDEPENDENT,
            S2_JOINT,
            S2_RECEIPT,
            HUMAN_CROSSWALK,
            JSONL_CROSSWALK,
            CROSSWALK_VERIFIER,
            CROSSWALK_TEST,
        ),
        FINAL_STATUS_RECEIPT: spec(
            "independent exact-hash acceptance of Run2 final status",
            "RUN2_CATEGORY_SATURATION_ACCEPTANCE_ONLY",
            P,
            FINAL_STATUS,
            HUMAN_CROSSWALK,
            JSONL_CROSSWALK,
            CROSSWALK_VERIFIER,
            CROSSWALK_TEST,
            S1_JOINT,
            S2_JOINT,
            S2_RECEIPT,
        ),
        LOG: spec(
            "source universe retrieval log and residual gaps",
            "RESEARCH_TRACE_ONLY",
            RP,
            FINAL_STATUS_RECEIPT,
            C7_SHADOW_FAILURE,
        ),
        DESIGN: spec(
            "opportunity-to-transaction system design",
            "DESIGN_SPECIFICATION_NO_IMPLEMENTATION_AUTHORITY",
            RP,
            CLAIMS,
            LOG,
            f"{RESEARCH}/01-黄仁勋访谈核查.md",
            C7_SHADOW_FAILURE,
        ),
        ENVELOPE: spec(
            "conditional read-only zero-side-effect shadow action envelope",
            "CONDITIONAL_SCOPE_NO_CURRENT_IMPLEMENTATION_AUTHORITY",
            RP,
            DESIGN,
            FINAL_STATUS_RECEIPT,
            C7_SHADOW_FAILURE,
        ),
        MATRIX: spec(
            "research closure predicate matrix",
            "LEAD_CANDIDATE_JUDGMENT_NO_SELF_APPROVAL",
            RP,
            CLAIMS,
            DESIGN,
            LOG,
            FINAL_STATUS,
            FINAL_STATUS_RECEIPT,
            CROSSWALK_VERIFIER,
            CROSSWALK_TEST,
            ACCEPTANCE_VERIFIER,
            ACCEPTANCE_TEST,
            ENVELOPE,
            C7_SHADOW_FAILURE,
            "EXTERNAL_LEGACY_QUARANTINE.md",
            f"{RESEARCH}/FINAL_REVIEW_HISTORY.md",
            CANDIDATE_VERIFIER,
            POST_VERIFIER,
            PHASE_TEST,
            BUILDER,
            FREEZE_BUILDER,
            CAPABILITY_POLICY,
            SHADOW_ACCEPTANCE_RUNNER,
            SHADOW_ACCEPTANCE_TEST,
            SANDBOX_PROBE_REPORT,
            C8_DOMAIN_GATE_REPORT,
        ),
        "FINAL_CANDIDATE_MANIFEST.md": spec(
            "human-readable final candidate freeze and review instructions",
            "REVIEW_ROUTING_ONLY_NO_SELF_APPROVAL",
            MATRIX,
            ENVELOPE,
            BUILDER,
            CANDIDATE_VERIFIER,
            POST_VERIFIER,
            PHASE_TEST,
            FREEZE_BUILDER,
            CAPABILITY_POLICY,
            SHADOW_ACCEPTANCE_RUNNER,
            SHADOW_ACCEPTANCE_TEST,
            SANDBOX_PROBE_REPORT,
            ACCEPTANCE_VERIFIER,
            ACCEPTANCE_TEST,
        ),
        "README.md": spec(
            "candidate root entrypoint and authority warning",
            "ENTRYPOINT_ONLY_NO_EXTERNAL_AUTHORITY",
            "FINAL_CANDIDATE_MANIFEST.md",
            DESIGN,
            "EXTERNAL_LEGACY_QUARANTINE.md",
        ),
    }
)


def inventory() -> set[str]:
    paths: set[str] = set()
    directories: set[str] = set()
    for current, directory_names, file_names in os.walk(ROOT, followlinks=False):
        current_path = Path(current)
        for name in list(directory_names):
            candidate = current_path / name
            relative = candidate.relative_to(ROOT).as_posix()
            if candidate.is_symlink():
                raise BuildError(f"symlink directory is forbidden: {relative}")
            candidate_stat = candidate.stat()
            if not stat.S_ISDIR(candidate_stat.st_mode):
                raise BuildError(f"special directory node is forbidden: {relative}")
            directories.add(relative)
        for name in file_names:
            candidate = current_path / name
            relative = candidate.relative_to(ROOT).as_posix()
            if candidate.is_symlink():
                raise BuildError(f"symlink file is forbidden: {relative}")
            candidate_stat = candidate.stat()
            if not stat.S_ISREG(candidate_stat.st_mode):
                raise BuildError(f"special file is forbidden: {relative}")
            if candidate_stat.st_nlink != 1:
                raise BuildError(f"hardlinked file is forbidden: {relative}")
            if candidate.resolve() == MANIFEST_PATH.resolve():
                continue
            paths.add(relative)

    expected_directories: set[str] = set()
    for relative in {*SPECS, MANIFEST_PATH.name}:
        parent = PurePosixPath(relative).parent
        while str(parent) not in {"", "."}:
            expected_directories.add(parent.as_posix())
            parent = parent.parent
    extras = sorted(directories - expected_directories)
    if extras:
        raise BuildError(f"unexpected directories: {extras}")
    return paths


def validate_dependency_graph() -> None:
    expected = set(SPECS)
    for owner, item in SPECS.items():
        dependencies = item["depends_on"]
        if len(dependencies) != len(set(dependencies)):
            raise BuildError(f"duplicate dependency for {owner}")
        for dependency in dependencies:
            if dependency not in expected:
                raise BuildError(f"{owner}: unknown dependency {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(path: str, stack: list[str]) -> None:
        if path in visited:
            return
        if path in visiting:
            start = stack.index(path)
            raise BuildError(f"dependency cycle: {' -> '.join(stack[start:] + [path])}")
        visiting.add(path)
        for dependency in SPECS[path]["depends_on"]:
            visit(dependency, stack + [path])
        visiting.remove(path)
        visited.add(path)

    for path in sorted(expected):
        visit(path, [])


def build() -> dict[str, Any]:
    validate_dependency_graph()
    actual = inventory()
    expected = set(SPECS)
    if actual != expected:
        raise BuildError(
            "closed inventory mismatch; "
            f"missing={sorted(expected - actual)}; unexpected={sorted(actual - expected)}"
        )
    envelope_hash = sha256_file(ROOT / ENVELOPE)
    entries = []
    for relative in sorted(expected):
        item = SPECS[relative]
        entries.append(
            {
                "path": relative,
                "sha256": sha256_file(ROOT / relative),
                "role": item["role"],
                "authority_status": item["authority_status"],
                "depends_on": item["depends_on"],
            }
        )
    return {
        "schema_version": "1.1",
        "candidate_id": REAL_CANDIDATE_ID,
        "status": EXPECTED_CANDIDATE_STATUS,
        "scope": EXPECTED_CANDIDATE_SCOPE,
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
                "governed_by_path": ENVELOPE,
                "governed_by_sha256": envelope_hash,
            },
            {
                "root_id": "shadow-mvp",
                "path_from_candidate_parent": "机会到交易系统-shadow-mvp",
                "artifact_kind": "READ_ONLY_SHADOW_MVP",
                "required_manifest": "SHADOW_ARTIFACT_MANIFEST.json",
                "freeze_required_state": "MUST_BE_ABSENT",
                "post_closure_required_state": "MAY_BE_ABSENT_OR_VALID",
                "activation_gate": "EXACT_CLOSURE_DECISION",
                "governed_by_path": ENVELOPE,
                "governed_by_sha256": envelope_hash,
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
                "governed_by_path": ENVELOPE,
                "governed_by_sha256": envelope_hash,
            },
        ],
        "entries": entries,
        "historical_exclusions": [],
    }


def main() -> int:
    try:
        document = build()
        MANIFEST_PATH.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (BuildError, OSError, UnicodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "candidate_id": document["candidate_id"],
                "entry_count": len(document["entries"]),
                "manifest_path": str(MANIFEST_PATH),
                "manifest_sha256": sha256_file(MANIFEST_PATH),
                "external_action_authority": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
