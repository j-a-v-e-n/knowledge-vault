#!/usr/bin/env python3
"""Verify that the project candidate is tracked, clean, and present on its upstream."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
CONTRACT = PROJECT_ROOT / "governance" / "ACCEPTANCE_CONTRACT_V1.json"
FROZEN_BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FROZEN_BUNDLE = PROJECT_ROOT / FROZEN_BUNDLE_RELATIVE


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def output(result: subprocess.CompletedProcess[str], label: str, errors: list[str]) -> str:
    if result.returncode != 0:
        errors.append(f"{label}: {result.stderr.strip() or 'git command failed'}")
        return ""
    return result.stdout.strip()


def load_frozen_files(errors: list[str]) -> list[str]:
    try:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append("governance acceptance contract is missing")
        return []
    except json.JSONDecodeError as exc:
        errors.append(
            "governance acceptance contract is invalid JSON: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
        return []
    if not isinstance(contract, dict):
        errors.append("governance acceptance contract must be a JSON object")
        return []
    change_control = contract.get("change_control")
    frozen_files = (
        change_control.get("frozen_files") if isinstance(change_control, dict) else None
    )
    if not isinstance(frozen_files, list) or not frozen_files:
        errors.append(
            "contract change_control.frozen_files must be a nonempty string list"
        )
        return []

    safe_files: list[str] = []
    seen: set[str] = set()
    for index, relative in enumerate(frozen_files):
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
        ):
            errors.append(f"contract frozen_files[{index}] has an unsafe path")
            continue
        if relative in seen:
            errors.append(f"contract frozen_files contains duplicate path: {relative}")
            continue
        seen.add(relative)
        safe_files.append(relative)
    return safe_files


def verify_versioned_file(
    relative: str,
    *,
    label: str,
    project_prefix: str,
    errors: list[str],
) -> None:
    repo_relative = f"{project_prefix}{relative}"
    tracked = git("ls-files", "--error-unmatch", "--", f":(top){repo_relative}")
    if tracked.returncode != 0:
        errors.append(f"{label} is not tracked: {relative}")
    at_head = git("cat-file", "-e", f"HEAD:{repo_relative}")
    if at_head.returncode != 0:
        errors.append(f"{label} is absent from HEAD: {relative}")


def verify(require_origin: bool, expected_commit: str | None) -> tuple[list[str], dict[str, str]]:
    errors: list[str] = []
    frozen_files = load_frozen_files(errors)
    repo_root_text = output(git("rev-parse", "--show-toplevel"), "repo root", errors)
    head = output(git("rev-parse", "HEAD"), "HEAD", errors)
    tree = output(git("rev-parse", "HEAD^{tree}"), "HEAD tree", errors)
    prefix = output(git("rev-parse", "--show-prefix"), "project prefix", errors)
    if expected_commit and head != expected_commit:
        errors.append(f"HEAD differs from expected commit: expected {expected_commit}, got {head}")

    status = output(
        git(
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            ".",
        ),
        "project status",
        errors,
    )
    if status:
        errors.append(f"project worktree is not clean:\n{status}")

    diff_check = git("diff", "--check", "--", ".")
    if diff_check.returncode != 0:
        errors.append(f"git diff --check failed:\n{diff_check.stdout}{diff_check.stderr}")

    for relative in frozen_files:
        verify_versioned_file(
            relative,
            label="normative file",
            project_prefix=prefix,
            errors=errors,
        )
    if FROZEN_BUNDLE.exists():
        verify_versioned_file(
            FROZEN_BUNDLE_RELATIVE,
            label="frozen bundle",
            project_prefix=prefix,
            errors=errors,
        )

    upstream = ""
    if require_origin:
        upstream = output(
            git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
            "upstream",
            errors,
        )
        upstream_head = (
            output(git("rev-parse", "@{upstream}"), "upstream HEAD", errors)
            if upstream
            else ""
        )
        if head and upstream_head and head != upstream_head:
            errors.append(
                f"HEAD is not pushed to upstream {upstream}: local={head}, upstream={upstream_head}"
            )
        remote_url = output(git("remote", "get-url", "origin"), "origin URL", errors)
        if not remote_url:
            errors.append("origin remote has no URL")

    facts = {
        "repo_root": repo_root_text,
        "project_prefix": prefix,
        "head": head,
        "tree": tree,
        "upstream": upstream,
    }
    return errors, facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-origin", action="store_true")
    parser.add_argument("--expected-commit")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, facts = verify(args.require_origin, args.expected_commit)
    if args.json:
        print(json.dumps({"status": "fail" if errors else "pass", "facts": facts, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        print("git state verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "git state verification: PASS "
            f"(head={facts['head']}, tree={facts['tree']}, upstream={facts['upstream'] or 'not-required'})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
