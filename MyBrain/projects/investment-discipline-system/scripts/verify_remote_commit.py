#!/usr/bin/env python3
"""Observe the actual remote ref and optionally prove recovery in a fresh clone."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def checked(cwd: Path, *args: str) -> str:
    result = git(cwd, *args)
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch")
    parser.add_argument("--fresh-clone", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        print("--commit must be a full 40-character commit", file=sys.stderr)
        return 2
    errors: list[str] = []
    facts: dict[str, str | bool] = {"requested_commit": args.commit}
    try:
        upstream = checked(
            PROJECT_ROOT,
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        )
        branch = args.branch or upstream.removeprefix(f"{args.remote}/")
        ref = f"refs/heads/{branch}"
        observed = checked(PROJECT_ROOT, "ls-remote", "--heads", args.remote, ref)
        fields = observed.split()
        remote_commit = fields[0] if len(fields) >= 2 and fields[1] == ref else ""
        facts.update({"remote": args.remote, "branch": branch, "ref": ref, "remote_commit": remote_commit})
        if remote_commit != args.commit:
            errors.append(
                f"remote_commit_mismatch: expected {args.commit}, got {remote_commit or '<missing>'}"
            )

        if args.fresh_clone and not errors:
            remote_url = checked(PROJECT_ROOT, "remote", "get-url", args.remote)
            with tempfile.TemporaryDirectory(prefix="ids-remote-verify-") as temp:
                clone_root = Path(temp) / "repo"
                clone = git(
                    Path(temp),
                    "clone",
                    "--no-checkout",
                    "--origin",
                    args.remote,
                    remote_url,
                    str(clone_root),
                )
                if clone.returncode != 0:
                    errors.append(
                        f"fresh_clone_failed: {clone.stderr.strip() or clone.stdout.strip()}"
                    )
                else:
                    cloned_commit = checked(clone_root, "rev-parse", args.commit)
                    cloned_tree = checked(clone_root, "rev-parse", f"{args.commit}^{{tree}}")
                    facts.update(
                        {
                            "fresh_clone": True,
                            "cloned_commit": cloned_commit,
                            "cloned_tree": cloned_tree,
                        }
                    )
                    if cloned_commit != args.commit:
                        errors.append("fresh_clone_commit_mismatch")
    except RuntimeError as exc:
        errors.append(str(exc))

    payload = {"schema_version": 1, "status": "fail" if errors else "pass", "facts": facts, "errors": errors}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif errors:
        print("remote commit verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "remote commit verification: PASS "
            f"({facts.get('ref')}={facts.get('remote_commit')}, fresh_clone={facts.get('fresh_clone', False)})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
