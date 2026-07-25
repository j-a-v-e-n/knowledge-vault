#!/usr/bin/env python3
"""Execute the fixed machine-assurance suite and emit an attestable manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()
).resolve()
PROJECT_PREFIX = subprocess.run(
    ["git", "rev-parse", "--show-prefix"],
    cwd=PROJECT_ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=True,
).stdout.strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_text(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPOSITORY_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(
            f"git {' '.join(args)} failed: "
            f"{completed.stdout.strip() or '<no output>'}"
        )
    return completed.stdout.strip()


def normalize_argv(argv: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in argv:
        if value == sys.executable:
            normalized.append("PYTHON")
        elif value.startswith(str(PROJECT_ROOT)):
            normalized.append(
                str(Path(value).relative_to(PROJECT_ROOT))
            )
        else:
            normalized.append(value)
    return normalized


def execute_check(
    check_id: str,
    argv: list[str],
    *,
    cwd: Path = PROJECT_ROOT,
    parse_json: bool = False,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    print(
        json.dumps(
            {
                "check_id": check_id,
                "phase": "started",
                "timeout_seconds": timeout_seconds,
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )
    timed_out = False
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout_seconds,
        )
        process_exit = completed.returncode
        stdout = completed.stdout
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        process_exit = 124
        captured = exc.stdout or ""
        if isinstance(captured, bytes):
            captured = captured.decode("utf-8", errors="replace")
        stdout = (
            captured
            + f"\nassurance check timed out after {timeout_seconds} seconds\n"
        )
    record: dict[str, Any] = {
        "check_id": check_id,
        "argv": normalize_argv(argv),
        "cwd": (
            "PROJECT_ROOT" if cwd == PROJECT_ROOT else "REPOSITORY_ROOT"
        ),
        "timeout_seconds": timeout_seconds,
        "timed_out": timed_out,
        "actual_process_exit": process_exit,
        "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
        "stdout_tail": stdout[-4000:],
        "result": "pass" if process_exit == 0 else "fail",
    }
    if parse_json:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            parsed = None
            record["result"] = "fail"
        record["structured_result"] = parsed
        if (
            not isinstance(parsed, dict)
            or parsed.get("status") != "pass"
        ):
            record["result"] = "fail"
    print(
        json.dumps(
            {
                "actual_process_exit": process_exit,
                "check_id": check_id,
                "phase": "completed",
                "result": record["result"],
                "timed_out": timed_out,
            },
            sort_keys=True,
        ),
        file=sys.stderr,
        flush=True,
    )
    if record["result"] != "pass":
        print(
            f"{check_id} failure output tail:\n{record['stdout_tail']}",
            file=sys.stderr,
            flush=True,
        )
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "evidence" / "ci" / "assurance-manifest.json",
    )
    args = parser.parse_args()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    commit = git_text("rev-parse", "HEAD")
    tree = git_text("rev-parse", "HEAD^{tree}")
    github_sha = os.environ.get("GITHUB_SHA")
    identity_valid = github_sha is None or github_sha == commit

    checks = [
        execute_check(
            "CHECK-ASSURANCE-METADATA",
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "verify_assurance_metadata.py"
                ),
                "--json",
            ],
            parse_json=True,
        ),
        execute_check(
            "CHECK-PROJECT-METHOD",
            [
                sys.executable,
                str(
                    PROJECT_ROOT
                    / "scripts"
                    / "run_project_method_acceptance.py"
                ),
                "--json",
                "--verify",
                "--ephemeral",
            ],
            parse_json=True,
            timeout_seconds=1800,
        ),
        execute_check(
            "CHECK-CANDIDATE-GOVERNANCE",
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "verify_governance.py"),
                "--allow-candidate",
            ],
        ),
        execute_check(
            "CHECK-CANONICAL-ATTACK-REPLAY",
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "replay_design_freeze_attacks.py"),
                "--candidate-commit",
                commit,
            ],
            parse_json=True,
            timeout_seconds=600,
        ),
        execute_check(
            "CHECK-GOVERNANCE-REGRESSION",
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "governance_tests",
                "-v",
            ],
            timeout_seconds=1200,
        ),
        execute_check(
            "CHECK-COMPILEALL",
            [sys.executable, "-m", "compileall", "-q", "."],
        ),
        execute_check(
            "CHECK-RUFF",
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--config",
                "governance/RUFF_CI_CONFIG_V1.toml",
                ".",
            ],
        ),
        execute_check(
            "CHECK-GIT-DIFF",
            ["git", "diff", "--check", commit],
            cwd=REPOSITORY_ROOT,
        ),
    ]
    required_check_ids = [
        "CHECK-ASSURANCE-METADATA",
        "CHECK-PROJECT-METHOD",
        "CHECK-CANDIDATE-GOVERNANCE",
        "CHECK-CANONICAL-ATTACK-REPLAY",
        "CHECK-GOVERNANCE-REGRESSION",
        "CHECK-COMPILEALL",
        "CHECK-RUFF",
        "CHECK-GIT-DIFF",
    ]
    passed = identity_valid and all(
        check["result"] == "pass" for check in checks
    )
    manifest = {
        "schema_version": 1,
        "manifest_id": "ids-github-machine-assurance-v1",
        "status": "pass" if passed else "fail",
        "assurance_level": "github_issued_workflow_provenance",
        "semantic_approval": False,
        "repository": os.environ.get(
            "GITHUB_REPOSITORY", "j-a-v-e-n/knowledge-vault"
        ),
        "workflow": os.environ.get(
            "GITHUB_WORKFLOW",
            "Investment Discipline Machine Assurance",
        ),
        "workflow_ref": os.environ.get("GITHUB_WORKFLOW_REF"),
        "workflow_sha": github_sha,
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "event_name": os.environ.get("GITHUB_EVENT_NAME"),
        "runner_environment": os.environ.get("RUNNER_ENVIRONMENT"),
        "candidate_commit": commit,
        "candidate_tree": tree,
        "project_prefix": PROJECT_PREFIX,
        "github_sha_matches_candidate": identity_valid,
        "required_check_ids": required_check_ids,
        "started_at": started_at,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "checks": checks,
        "limitations": [
            "The attestation proves workflow provenance and artifact integrity, not semantic correctness.",
            "Semantic release approval requires a separate post-candidate Codex review and novelty probe.",
        ],
    }
    output = args.output
    if not output.is_absolute():
        output = (PROJECT_ROOT / output).resolve()
    try:
        output.relative_to(PROJECT_ROOT)
    except ValueError:
        raise SystemExit("--output must stay inside the project root") from None
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "candidate_commit": commit,
                "candidate_tree": tree,
                "manifest_path": str(output.relative_to(PROJECT_ROOT)),
                "manifest_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            },
            sort_keys=True,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
