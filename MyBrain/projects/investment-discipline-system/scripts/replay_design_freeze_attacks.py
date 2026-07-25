#!/usr/bin/env python3
"""Replay the fixed adversarial probes required before design freeze."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
ATTACK_SELECTORS = {
    "ATTACK-PIT-ORACLE-INVERSION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_pit_oracle_inversion_is_rejected"
    ),
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_same_bar_causality_smuggle_is_rejected"
    ),
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_split_accounting_smuggle_is_rejected"
    ),
    "ATTACK-CONDITIONAL-SELF-ATTESTATION": (
        "governance_tests.test_final_review_attacks."
        "FinalReviewAttackTests.test_conditional_self_attestation_is_rejected"
    ),
}


def git_text(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "fail",
                    "error": f"git {' '.join(args)} failed",
                    "detail": result.stderr.strip(),
                },
                sort_keys=True,
            )
        )
    return result.stdout.strip()


def main() -> int:
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    candidate_commit = git_text("rev-parse", "HEAD")
    candidate_tree = git_text("rev-parse", "HEAD^{tree}")
    results: list[dict[str, object]] = []
    for attack_id, selector in ATTACK_SELECTORS.items():
        result = subprocess.run(
            [sys.executable, "-m", "unittest", selector, "-v"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        output = result.stdout
        results.append(
            {
                "attack_id": attack_id,
                "selector": selector,
                "exit_code": result.returncode,
                "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
                "result": "rejected" if result.returncode == 0 else "escaped_or_error",
            }
        )
    passed = all(item["result"] == "rejected" for item in results)
    payload = {
        "schema_version": 1,
        "status": "pass" if passed else "fail",
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "required_attack_ids": list(ATTACK_SELECTORS),
        "started_at": started_at,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": results,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
