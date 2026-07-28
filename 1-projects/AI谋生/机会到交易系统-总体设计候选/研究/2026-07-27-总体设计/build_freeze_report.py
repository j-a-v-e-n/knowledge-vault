#!/usr/bin/env python3
"""Build the exact external freeze report consumed by the governance Gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from verify_candidate_manifest import (  # noqa: E402
    ManifestError,
    sha256_file,
    validate_manifest,
)


CANDIDATE_VERIFIER_PATH = "研究/2026-07-27-总体设计/verify_candidate_manifest.py"
FREEZE_REPORT_KEYS = {
    "schema_version",
    "candidate_id",
    "parent_candidate_manifest_sha256",
    "verifier_path",
    "verifier_sha256",
    "mode",
    "result",
    "candidate_inventory_digest_sha256",
    "post_closure_root_states",
}
POST_CLOSURE_ROOT_NAMES = {
    "机会到交易系统-闭合记录",
    "机会到交易系统-shadow-mvp",
}


class FreezeReportError(ValueError):
    pass


def canonical_text(document: dict[str, Any]) -> str:
    if set(document) != FREEZE_REPORT_KEYS:
        raise FreezeReportError("freeze report does not match the frozen exact key set")
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def build_freeze_report(candidate_manifest_path: Path) -> dict[str, Any]:
    candidate_manifest_path = candidate_manifest_path.resolve()
    result = validate_manifest(candidate_manifest_path, phase="freeze")
    candidate_root = candidate_manifest_path.parent
    verifier = candidate_root / CANDIDATE_VERIFIER_PATH
    if verifier.is_symlink() or not verifier.is_file():
        raise FreezeReportError("candidate verifier is missing or symlinked")
    root_states = [
        {"root_id": row["root_id"], "state": row["state"]}
        for row in result["post_closure_roots"]
    ]
    expected_states = [
        {"root_id": "closure-governance", "state": "ABSENT"},
        {"root_id": "shadow-mvp", "state": "ABSENT"},
    ]
    if root_states != expected_states:
        raise FreezeReportError("freeze does not prove both post-closure roots absent")
    document = {
        "schema_version": "otts.candidate-freeze-report/1",
        "candidate_id": result["candidate_id"],
        "parent_candidate_manifest_sha256": result["manifest_sha256"],
        "verifier_path": CANDIDATE_VERIFIER_PATH,
        "verifier_sha256": sha256_file(verifier),
        "mode": "freeze",
        "result": "PASS",
        "candidate_inventory_digest_sha256": result[
            "candidate_inventory_digest_sha256"
        ],
        "post_closure_root_states": root_states,
    }
    canonical_text(document)
    return document


def write_freeze_report(
    candidate_manifest_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    candidate_manifest_path = candidate_manifest_path.resolve()
    candidate_root = candidate_manifest_path.parent
    output_path = output_path.resolve()
    try:
        output_path.relative_to(candidate_root)
    except ValueError:
        pass
    else:
        raise FreezeReportError("freeze report must remain outside candidate inventory")
    candidate_parent = candidate_root.parent
    for root_name in POST_CLOSURE_ROOT_NAMES:
        forbidden_root = (candidate_parent / root_name).resolve()
        try:
            output_path.relative_to(forbidden_root)
        except ValueError:
            continue
        raise FreezeReportError(
            f"freeze report must not create post-closure root before review: {root_name}"
        )

    document = build_freeze_report(candidate_manifest_path)
    text = canonical_text(document)
    if output_path.exists():
        try:
            existing = output_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise FreezeReportError(f"cannot inspect existing output: {exc}") from exc
        if existing != text:
            raise FreezeReportError(
                "refusing to overwrite a different existing freeze report"
            )
        return document
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        document = write_freeze_report(args.candidate_manifest, args.output)
    except (FreezeReportError, ManifestError, OSError, UnicodeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            {
                "valid": True,
                "candidate_id": document["candidate_id"],
                "freeze_report_path": str(args.output.resolve()),
                "freeze_report_sha256": sha256_file(args.output.resolve()),
                "external_action_authority": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
