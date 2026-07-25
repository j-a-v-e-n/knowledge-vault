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


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
SCRIPT_DIR = Path(__file__).resolve().parent
GOVERNANCE = PROJECT_ROOT / "governance"
CONTRACT = GOVERNANCE / "ACCEPTANCE_CONTRACT_V1.json"
RESEARCH = GOVERNANCE / "AI_PROJECT_RESEARCH_REGISTER_V1.json"
BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"
CANDIDATE_VERIFIER = SCRIPT_DIR / "verify_governance.py"
REMOTE_VERIFIER = SCRIPT_DIR / "verify_remote_commit.py"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"


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
        raise SystemExit(
            f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout.decode("utf-8").strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run_python(
    script: Path, *args: str
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["IDS_PROJECT_ROOT"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        check=False,
    )


def require_candidate_governance() -> None:
    result = run_python(CANDIDATE_VERIFIER, "--allow-candidate")
    if result.returncode != 0:
        detail = result.stdout.strip() or "candidate verifier produced no output"
        raise SystemExit(f"candidate governance verification failed:\n{detail}")


def load_json_object(path: Path, relative: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing frozen JSON: {relative}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"invalid frozen JSON {relative}:{exc.lineno}:{exc.colno}: {exc.msg}"
        ) from None
    if not isinstance(value, dict):
        raise SystemExit(f"frozen JSON must contain an object: {relative}")
    return value


def frozen_file_paths(contract: dict) -> list[str]:
    change_control = contract.get("change_control")
    frozen_files = (
        change_control.get("frozen_files") if isinstance(change_control, dict) else None
    )
    if not isinstance(frozen_files, list) or not frozen_files:
        raise SystemExit(
            "contract change_control.frozen_files must be a nonempty string list"
        )
    safe_files: list[str] = []
    seen: set[str] = set()
    for index, relative in enumerate(frozen_files):
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            raise SystemExit(f"contract frozen_files[{index}] has an unsafe path")
        if relative in seen:
            raise SystemExit(f"contract frozen_files contains duplicate path: {relative}")
        seen.add(relative)
        safe_files.append(relative)
    return safe_files


def require_frozen_statuses(
    frozen_files: list[str],
) -> tuple[dict, dict]:
    documents: dict[str, dict] = {}
    for relative in frozen_files:
        if Path(relative).suffix.lower() != ".json":
            continue
        document = load_json_object(PROJECT_ROOT / relative, relative)
        documents[relative] = document
        if relative == RESEARCH_RELATIVE:
            if document.get("status") != "adopted_with_explicit_limits":
                raise SystemExit(
                    "research register must be adopted_with_explicit_limits"
                )
        elif document.get("status") != "frozen":
            raise SystemExit(f"{relative} status must be frozen")

    contract_relative = "governance/ACCEPTANCE_CONTRACT_V1.json"
    contract = documents.get(contract_relative)
    if contract is None:
        raise SystemExit("acceptance contract must be included in frozen_files")
    research = documents.get(RESEARCH_RELATIVE)
    if research is None:
        raise SystemExit("research register must be included in frozen_files")
    challenge = research.get("challenge")
    if not isinstance(challenge, dict) or challenge.get("status") != "completed":
        raise SystemExit("research challenge is not completed")
    stop_rule = research.get("stop_rule")
    if not isinstance(stop_rule, dict) or stop_rule.get("met") is not True:
        raise SystemExit("research stop rule is not met")
    return contract, research


def require_clean_exact_baseline(baseline: str) -> None:
    head = git_text("rev-parse", "HEAD")
    if head != baseline:
        raise SystemExit(
            f"baseline must equal current clean HEAD: HEAD={head}, requested={baseline}"
        )
    project_status = git_text(
        "status", "--porcelain=v1", "--untracked-files=all", "--", "."
    )
    if project_status:
        raise SystemExit(f"project worktree is not clean:\n{project_status}")


def require_direct_remote(
    baseline: str, remote: str, branch: str | None
) -> dict[str, object]:
    command = ["--commit", baseline, "--remote", remote, "--json"]
    if branch:
        command.extend(["--branch", branch])
    result = run_python(REMOTE_VERIFIER, *command)
    detail = result.stdout.strip()
    try:
        payload = json.loads(detail)
    except json.JSONDecodeError:
        payload = {}
    if result.returncode != 0:
        raise SystemExit(
            "direct remote commit verification failed:\n"
            f"{detail or 'remote verifier produced no output'}"
        )
    if not isinstance(payload, dict) or payload.get("status") != "pass":
        raise SystemExit("direct remote verifier returned an invalid success result")
    facts = payload.get("facts")
    if not isinstance(facts, dict) or facts.get("remote_commit") != baseline:
        raise SystemExit("direct remote verifier did not bind the requested baseline")
    return facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-commit", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch")
    args = parser.parse_args()
    baseline = args.baseline_commit
    if not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise SystemExit("--baseline-commit must be a full 40-character commit")

    require_candidate_governance()
    if BUNDLE.exists():
        raise SystemExit(f"refusing to overwrite existing {BUNDLE.name}")

    candidate_contract = load_json_object(
        CONTRACT, "governance/ACCEPTANCE_CONTRACT_V1.json"
    )
    frozen_files = frozen_file_paths(candidate_contract)
    contract, research = require_frozen_statuses(frozen_files)
    del research

    require_clean_exact_baseline(baseline)
    remote_facts = require_direct_remote(baseline, args.remote, args.branch)
    require_clean_exact_baseline(baseline)

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
        "upstream_ref_at_creation": remote_facts.get("ref"),
        "remote_at_creation": remote_facts.get("remote"),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "creation_rule": "two-stage: candidate governance validated and normative baseline directly observed on the remote before this bundle; bundle itself must be committed and pushed next",
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
