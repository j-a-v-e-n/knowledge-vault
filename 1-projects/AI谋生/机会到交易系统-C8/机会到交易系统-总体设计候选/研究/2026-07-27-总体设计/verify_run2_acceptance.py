#!/usr/bin/env python3
"""Verify the exact independent acceptance of the Run2 final-status object.

This is a candidate-specific successor verifier.  The independent receipt is
kept byte-for-byte unchanged and therefore still names the original C7 review
root.  For C8, this verifier separately requires every local relocated copy to
match the exact independently accepted hash.  It never rewrites the receipt or
pretends the reviewer inspected the successor path.  It also re-runs exhaustive
crosswalk reconstruction and rejects any authority claim beyond category-
codebook saturation within the frozen protocol.  It cannot cryptographically
prove reviewer identity or independence; that residual limit remains explicit
in the receipt and must be reviewed again at the successor manifest-bound final
Gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from verify_run2_crosswalk import CrosswalkError, validate_crosswalk  # noqa: E402


ROOT = Path(__file__).resolve().parent
ORIGINAL_REVIEW_ROOT = (
    ROOT.parents[3]
    / "机会到交易系统-总体设计候选"
    / "研究/2026-07-27-总体设计"
)
DEFAULT_RECEIPT = ROOT / "ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json"
SCHEMA_VERSION = "otts.run2-final-status-independent-acceptance/1"
EXECUTION_ID = "SSP-1.0-RUN-20260727T154803-0700"
RECEIPT_ID = "otts-run2-final-status-independent-acceptance-5b27030ff9c13a61"
REVIEWER_ID = "fresh-c2-final-review-remediation-2"
ACCEPTED_STATUS = "SATURATED-WITHIN-PROTOCOL"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


TOP_LEVEL_KEYS = {
    "schema_version",
    "receipt_id",
    "reviewer_id",
    "independence_assertion",
    "review_scope",
    "execution_id",
    "protocol",
    "final_status",
    "human_crosswalk",
    "exhaustive_crosswalk",
    "verifier",
    "test",
    "s1_joint",
    "s2_joint",
    "s2_receipt",
    "decision",
    "accepted_status",
    "unresolved_critical",
    "unresolved_major",
    "residual_limits",
    "external_action_authority",
    "candidate_closure_authority",
    "implementation_authority",
    "shadow_operation_authority",
}
BINDING_KEYS = {"path", "sha256"}
EXECUTED_BINDING_KEYS = {"path", "sha256", "result"}


EXPECTED_BINDINGS = {
    "protocol": (
        "SEARCH_SATURATION_PROTOCOL.md",
        "911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1",
    ),
    "final_status": (
        "ssp-run2/FINAL_RUN_STATUS.md",
        "5b27030ff9c13a6196ffb81a0e828de3e69ac0ee176651d3fa35fab088e1a6c3",
    ),
    "human_crosswalk": (
        "RUN2_CLAIM_EVIDENCE_CROSSWALK.md",
        "8c71e9b5e5b5069259e820db8e1eae490aa21822094ef2e519d815c209ba8a0a",
    ),
    "exhaustive_crosswalk": (
        "RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl",
        "b31b67b255a6f2b797e261199c5ff8196001963e21011b07396e837ab8b0273b",
    ),
    "verifier": (
        "verify_run2_crosswalk.py",
        "1c1dafd1f7abfa9ae1ab6c918ccf1b7089c68d9c755c53663fe5a9d823a43ae0",
    ),
    "test": (
        "test_run2_crosswalk.py",
        "0b58f975d46d9a17f91881f4362623fdc36716031c603f935a5abfd82e50c99d",
    ),
    "s1_joint": (
        "ssp-run2/S1_JOINT_ADJUDICATION.md",
        "c8fb7bef800bc0a23370629fa8dfd4e19c802dea65d303f3e67eff690d00880f",
    ),
    "s2_joint": (
        "ssp-run2/S2_JOINT_ADJUDICATION.md",
        "c6b2f73f41f1669f1d4a096ebede551353f84024d6d281df091feab4a79907d3",
    ),
    "s2_receipt": (
        "ssp-run2/S2_INDEPENDENT_ACCEPTANCE_RECEIPT.md",
        "f10b6f36810bfd5ae441d6286ddb923f379dad4447d37bcecda9485b3a33bbf1",
    ),
}
EXPECTED_EXECUTION_RESULTS = {"verifier": "valid", "test": "OK"}
EXPECTED_INDEPENDENCE_ASSERTION = (
    "I did not author or modify remediation attempt 2. Review was read-only. "
    "I reviewed earlier rejected bytes, so this was not blind, but I remained "
    "independent of authorship and remediation. No receipt, root, or other file "
    "was created by the reviewer."
)
EXPECTED_REVIEW_SCOPE = (
    "Exact remediation-attempt-2 Run2 bytes only: SSP, S1/S2 raw manifests, "
    "lead/independent ledgers, S1/S2 joint adjudications, S2 independent receipt, "
    "all 23 direct semantic bridges, all 272 exhaustive JSONL rows, verifier/tests, "
    "and FINAL_RUN_STATUS. Excludes source truth, open-world exhaustiveness, "
    "candidate or design closure, implementation, shadow operation, Pilot, "
    "profitability, and external action authority."
)
EXPECTED_CROSSWALK_COUNTS = {
    "s1_final_ce_in": 131,
    "s2_final_ce_in": 141,
    "total_final_ce_in": 272,
    "s1_direct_mappings": 18,
    "s2_direct_mappings": 5,
    "total_direct_mappings": 23,
    "total_no_direct_load_bearing_use": 249,
}
EXPECTED_RESIDUAL_LIMITS = [
    (
        "Acceptance establishes saturation only within the frozen SSP "
        "category/codebook scope; it does not establish factual truth, open-world "
        "exhaustiveness, business validation, or overall C4/design closure."
    ),
    (
        "Reviewer identity, role independence, and chronology remain local "
        "attestations rather than cryptographic signatures or trusted timestamps."
    ),
    (
        "The supplied verifier reconstructs sealed identities and frozen rejection "
        "sets, but it cannot decide source meaning by itself; the read-only reviewer "
        "independently re-audited all current direct semantic bridges."
    ),
    (
        "S1 final K is a disclosed routing union, not individually adjudicated "
        "evidence weighting and not authority for stronger claims."
    ),
    (
        "Reviewer identity, independence, chronology, and this lead-materialized "
        "receipt remain local attestations rather than cryptographic signatures or "
        "trusted timestamps."
    ),
    (
        "Any byte change invalidates this acceptance; this exact receipt must be "
        "bound by the successor candidate before the accepted status becomes effective."
    ),
]


class AcceptanceError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AcceptanceError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AcceptanceError(f"{label}: expected object")
    actual = set(value)
    if actual != expected:
        raise AcceptanceError(
            f"{label}: key mismatch; missing={sorted(expected - actual)}; "
            f"extra={sorted(actual - expected)}"
        )
    return value


def require_regular_single_link(path: Path, label: str) -> None:
    if path.is_symlink():
        raise AcceptanceError(f"{label}: symlink is forbidden")
    try:
        path_stat = path.stat()
    except OSError as exc:
        raise AcceptanceError(f"{label}: cannot stat file: {exc}") from exc
    if not stat.S_ISREG(path_stat.st_mode):
        raise AcceptanceError(f"{label}: expected regular file")
    if path_stat.st_nlink != 1:
        raise AcceptanceError(f"{label}: hardlinked file is forbidden")


def validate_binding(document: dict[str, Any], key: str) -> None:
    expected_relative, expected_hash = EXPECTED_BINDINGS[key]
    expected_keys = EXECUTED_BINDING_KEYS if key in EXPECTED_EXECUTION_RESULTS else BINDING_KEYS
    binding = require_exact_keys(document[key], expected_keys, key)
    reviewed_path = (ORIGINAL_REVIEW_ROOT / expected_relative).resolve()
    if binding["path"] != str(reviewed_path):
        raise AcceptanceError(
            f"{key}.path: exact reviewed path mismatch; "
            f"expected={reviewed_path}; actual={binding['path']!r}"
        )
    if not isinstance(binding["sha256"], str) or not SHA256_RE.fullmatch(
        binding["sha256"]
    ):
        raise AcceptanceError(f"{key}.sha256: expected lowercase SHA-256")
    if binding["sha256"] != expected_hash:
        raise AcceptanceError(
            f"{key}.sha256: receipt does not bind the independently accepted hash"
        )
    relocated_path = (ROOT / expected_relative).resolve()
    require_regular_single_link(relocated_path, f"{key} relocated snapshot")
    actual_hash = sha256_file(relocated_path)
    if actual_hash != expected_hash:
        raise AcceptanceError(
            f"{key}: relocated artifact hash mismatch against accepted bytes; "
            f"expected={expected_hash}; actual={actual_hash}"
        )
    if key in EXPECTED_EXECUTION_RESULTS:
        expected_result = EXPECTED_EXECUTION_RESULTS[key]
        if binding["result"] != expected_result:
            raise AcceptanceError(
                f"{key}.result must equal independently reported {expected_result!r}"
            )


def load_receipt(receipt_path: Path) -> tuple[dict[str, Any], str]:
    require_regular_single_link(receipt_path, "receipt")
    try:
        text = receipt_path.read_text(encoding="utf-8")
        document = json.loads(text, object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AcceptanceError(f"cannot read receipt: {exc}") from exc
    document = require_exact_keys(document, TOP_LEVEL_KEYS, "receipt")
    canonical = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    if text != canonical:
        raise AcceptanceError("receipt is not in canonical serialized form")
    return document, text


def validate_acceptance(receipt_path: Path = DEFAULT_RECEIPT) -> dict[str, Any]:
    document, receipt_text = load_receipt(receipt_path)
    exact_scalars = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "reviewer_id": REVIEWER_ID,
        "independence_assertion": EXPECTED_INDEPENDENCE_ASSERTION,
        "review_scope": EXPECTED_REVIEW_SCOPE,
        "execution_id": EXECUTION_ID,
        "decision": "ACCEPT",
        "accepted_status": ACCEPTED_STATUS,
    }
    for key, expected in exact_scalars.items():
        if document[key] != expected:
            raise AcceptanceError(f"receipt.{key} does not match the accepted object")

    for key in (
        "external_action_authority",
        "candidate_closure_authority",
        "implementation_authority",
        "shadow_operation_authority",
    ):
        if document[key] is not False:
            raise AcceptanceError(f"receipt.{key} must be false")
    for key in ("unresolved_critical", "unresolved_major"):
        if document[key] != []:
            raise AcceptanceError(f"receipt.{key} must be an empty list")
    if document["residual_limits"] != EXPECTED_RESIDUAL_LIMITS:
        raise AcceptanceError("receipt.residual_limits changed or is incomplete")

    for key in EXPECTED_BINDINGS:
        validate_binding(document, key)

    final_status_text = (ROOT / EXPECTED_BINDINGS["final_status"][0]).read_text(
        encoding="utf-8"
    )
    required_status_markers = (
        f"- 执行 ID：`{EXECUTION_ID}`",
        f"- lead 提议状态：`{ACCEPTED_STATUS}`",
        "- 当前生效状态：`INCOMPLETE-PENDING-EXACT-FINAL-STATUS-INDEPENDENT-ACCEPTANCE`",
        "它不替代 successor candidate、closure predicate matrix 与 manifest-bound final independent review。",
    )
    for marker in required_status_markers:
        if marker not in final_status_text:
            raise AcceptanceError(f"final status missing required bounded marker: {marker}")

    try:
        crosswalk = validate_crosswalk(
            ROOT,
            ROOT / EXPECTED_BINDINGS["exhaustive_crosswalk"][0],
        )
    except (OSError, UnicodeError, CrosswalkError) as exc:
        raise AcceptanceError(f"exhaustive crosswalk validation failed: {exc}") from exc
    if crosswalk.get("valid") is not True:
        raise AcceptanceError("exhaustive crosswalk verifier did not return valid=true")
    if crosswalk.get("external_action_authority") is not False:
        raise AcceptanceError("crosswalk unexpectedly grants external action authority")
    for key, expected in EXPECTED_CROSSWALK_COUNTS.items():
        if crosswalk.get(key) != expected:
            raise AcceptanceError(
                f"crosswalk.{key} does not match independently accepted count"
            )

    return {
        "valid": True,
        "receipt_id": document["receipt_id"],
        "receipt_sha256": hashlib.sha256(receipt_text.encode("utf-8")).hexdigest(),
        "reviewer_id": document["reviewer_id"],
        "execution_id": document["execution_id"],
        "accepted_status": document["accepted_status"],
        "final_status_sha256": document["final_status"]["sha256"],
        "crosswalk_sha256": crosswalk["crosswalk_sha256"],
        "reviewed_original_root": str(ORIGINAL_REVIEW_ROOT.resolve()),
        "relocated_snapshot_root": str(ROOT.resolve()),
        "relocated_snapshot_exact_bytes": True,
        "review_scope_rewritten_for_successor": False,
        "unresolved_critical": [],
        "unresolved_major": [],
        "candidate_closure_authority": False,
        "implementation_authority": False,
        "shadow_operation_authority": False,
        "external_action_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    try:
        result = validate_acceptance(args.receipt)
    except (AcceptanceError, OSError, UnicodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
