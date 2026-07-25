#!/usr/bin/env python3
"""Replay every fixed design-freeze attack through the production runner."""

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
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
RUNNER = PROJECT_ROOT / "scripts" / "run_design_freeze_attack.py"
RUNNER_ID = "ids-design-freeze-attack-runner-v1"
ATTACK_IDS = [
    "ATTACK-PIT-ORACLE-INVERSION",
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
    "ATTACK-CONDITIONAL-SELF-ATTESTATION",
]


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "schema_version": 2,
                    "status": "fail",
                    "error": f"git {' '.join(args)} failed",
                    "detail": result.stdout.strip(),
                },
                sort_keys=True,
            )
        )
    return result.stdout.strip()


def fingerprint_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "runner_id",
        "runner_sha256",
        "candidate_commit",
        "candidate_tree",
        "project_prefix",
        "mode",
        "probe_id",
        "mutation_spec_sha256",
        "mutation_observation",
        "baseline",
        "target",
        "expected_rejection_substring",
        "result",
        "runner_exit_code",
    )
    return {key: receipt.get(key) for key in keys}


def valid_receipt(
    receipt: Any,
    *,
    attack_id: str,
    candidate_commit: str,
    candidate_tree: str,
    actual_process_exit: int,
) -> bool:
    if not isinstance(receipt, dict):
        return False
    baseline = receipt.get("baseline")
    target = receipt.get("target")
    fingerprint = receipt.get("execution_fingerprint")
    if (
        receipt.get("schema_version") != 2
        or receipt.get("runner_id") != RUNNER_ID
        or receipt.get("candidate_commit") != candidate_commit
        or receipt.get("candidate_tree") != candidate_tree
        or receipt.get("mode") != "canonical"
        or receipt.get("probe_id") != attack_id
        or receipt.get("result") != "rejected"
        or receipt.get("runner_exit_code") != 0
        or actual_process_exit != receipt.get("runner_exit_code")
        or not isinstance(baseline, dict)
        or baseline.get("exit_code") != 0
        or not isinstance(target, dict)
        or type(target.get("exit_code")) is not int
        or target.get("exit_code") == 0
        or not isinstance(fingerprint, str)
        or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
    ):
        return False
    return fingerprint == sha256_bytes(canonical_json(fingerprint_payload(receipt)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-commit")
    args = parser.parse_args()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    candidate_commit = args.candidate_commit or git_text("rev-parse", "HEAD")
    if re.fullmatch(r"[0-9a-f]{40}", candidate_commit) is None:
        raise SystemExit("--candidate-commit must be a full 40-character SHA-1")
    resolved = git_text("rev-parse", "--verify", f"{candidate_commit}^{{commit}}")
    if resolved != candidate_commit:
        raise SystemExit("candidate commit did not resolve exactly")
    candidate_tree = git_text("rev-parse", f"{candidate_commit}^{{tree}}")

    results: list[dict[str, Any]] = []
    for attack_id in ATTACK_IDS:
        completed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--candidate-commit",
                candidate_commit,
                "--attack-id",
                attack_id,
            ],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        raw = completed.stdout
        try:
            receipt = json.loads(raw)
        except json.JSONDecodeError:
            receipt = None
        passed = valid_receipt(
            receipt,
            attack_id=attack_id,
            candidate_commit=candidate_commit,
            candidate_tree=candidate_tree,
            actual_process_exit=completed.returncode,
        )
        raw_baseline = receipt.get("baseline") if isinstance(receipt, dict) else None
        raw_target = receipt.get("target") if isinstance(receipt, dict) else None
        baseline = raw_baseline if isinstance(raw_baseline, dict) else {}
        target = raw_target if isinstance(raw_target, dict) else {}
        results.append(
            {
                "attack_id": attack_id,
                "actual_runner_process_exit": completed.returncode,
                "declared_runner_exit_code": (
                    receipt.get("runner_exit_code")
                    if isinstance(receipt, dict)
                    else None
                ),
                "baseline_verifier_exit": baseline.get("exit_code"),
                "target_verifier_exit": target.get("exit_code"),
                "baseline_stdout_sha256": baseline.get("stdout_sha256"),
                "target_stdout_sha256": target.get("stdout_sha256"),
                "execution_fingerprint": (
                    receipt.get("execution_fingerprint")
                    if isinstance(receipt, dict)
                    else None
                ),
                "receipt_sha256": sha256_bytes(raw.encode("utf-8")),
                "result": "rejected" if passed else "escaped_or_runner_error",
            }
        )

    passed = all(item["result"] == "rejected" for item in results)
    payload = {
        "schema_version": 2,
        "status": "pass" if passed else "fail",
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "runner_id": RUNNER_ID,
        "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        "required_attack_ids": ATTACK_IDS,
        "started_at": started_at,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
