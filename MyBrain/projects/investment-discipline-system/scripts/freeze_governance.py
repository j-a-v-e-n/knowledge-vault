#!/usr/bin/env python3
"""Create the non-circular second-stage governance frozen bundle."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE = PROJECT_ROOT / "governance"
CONTRACT = GOVERNANCE / "ACCEPTANCE_CONTRACT_V1.json"
RESEARCH = GOVERNANCE / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"


def git_bytes(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_text(*args: str) -> str:
    result = git_bytes(*args)
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout.decode("utf-8").strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def require_frozen_statuses(contract: dict, research: dict) -> None:
    if contract.get("status") != "frozen":
        raise RuntimeError("contract status must be frozen before baseline commit")
    if research.get("status") != "adopted_with_explicit_limits":
        raise RuntimeError("research register must be adopted_with_explicit_limits")
    if research.get("challenge", {}).get("status") != "completed":
        raise RuntimeError("research challenge is not completed")
    if research.get("stop_rule", {}).get("met") is not True:
        raise RuntimeError("research stop rule is not met")
    for relative in (
        "governance/USER_SOURCE_EXCERPTS_V1.json",
        "governance/USER_INTENT_V1.json",
        "governance/VERIFICATION_SPECS_V1.json",
        "governance/TRACEABILITY_V1.json",
        "governance/ASSURANCE_SUBJECTS_V1.json",
    ):
        document = json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))
        if document.get("status") != "frozen":
            raise RuntimeError(f"{relative} status must be frozen")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-commit", required=True)
    args = parser.parse_args()
    baseline = args.baseline_commit
    if not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise SystemExit("--baseline-commit must be a full 40-character commit")
    if BUNDLE.exists():
        raise SystemExit(f"refusing to overwrite existing {BUNDLE.name}")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    research = json.loads(RESEARCH.read_text(encoding="utf-8"))
    require_frozen_statuses(contract, research)
    frozen_files = contract.get("change_control", {}).get("frozen_files")
    if not isinstance(frozen_files, list) or not frozen_files:
        raise SystemExit("contract has no frozen_files")

    head = git_text("rev-parse", "HEAD")
    if head != baseline:
        raise SystemExit(f"baseline must equal current clean HEAD: HEAD={head}, requested={baseline}")
    project_status = git_text(
        "status", "--porcelain=v1", "--untracked-files=all", "--", "."
    )
    if project_status:
        raise SystemExit(f"project worktree is not clean:\n{project_status}")
    upstream = git_text("rev-parse", "@{upstream}")
    if upstream != baseline:
        raise SystemExit(
            f"baseline is not the current pushed upstream commit: upstream={upstream}"
        )

    prefix = git_text("rev-parse", "--show-prefix")
    entries: list[dict[str, str]] = []
    for relative in frozen_files:
        repo_relative = f"{prefix}{relative}"
        content = git_bytes("show", f"{baseline}:{repo_relative}")
        if content.returncode != 0:
            raise SystemExit(f"frozen file is not tracked at baseline: {relative}")
        current = (PROJECT_ROOT / relative).read_bytes()
        if current != content.stdout:
            raise SystemExit(f"working file differs from baseline: {relative}")
        tree_line = git_text("ls-tree", baseline, "--", repo_relative)
        fields = tree_line.split()
        if len(fields) < 3:
            raise SystemExit(f"cannot resolve git blob for {relative}")
        entries.append(
            {
                "path": relative,
                "sha256": sha256_bytes(current),
                "git_blob": fields[2],
            }
        )

    bundle = {
        "schema_version": 1,
        "status": "frozen",
        "contract_id": contract.get("contract_id"),
        "baseline_commit": baseline,
        "baseline_tree": git_text("rev-parse", f"{baseline}^{{tree}}"),
        "upstream_ref_at_creation": git_text(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
        ),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "creation_rule": "two-stage: normative baseline committed and pushed before this bundle; bundle itself must be committed and pushed next",
        "files": entries,
    }
    payload = (json.dumps(bundle, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor = os.open(BUNDLE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    print(
        f"created {BUNDLE.relative_to(PROJECT_ROOT)} for baseline "
        f"{baseline}; commit and push the bundle before claiming frozen"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
