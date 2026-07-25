#!/usr/bin/env python3
"""Verify project Git state and directly observe the trusted origin branch."""

from __future__ import annotations

import argparse
import datetime as dt
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
TRUSTED_REMOTE = "origin"


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


def trusted_branch(
    requested_branch: str | None,
    errors: list[str],
) -> tuple[str, str]:
    branch = requested_branch or output(
        git("symbolic-ref", "--short", "HEAD"),
        "current branch",
        errors,
    )
    if branch:
        valid = git("check-ref-format", "--branch", branch)
        if valid.returncode != 0:
            errors.append(f"trusted branch is invalid: {branch!r}")
    upstream = output(
        git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
        "upstream",
        errors,
    )
    expected_upstream = f"{TRUSTED_REMOTE}/{branch}" if branch else ""
    if upstream and expected_upstream and upstream != expected_upstream:
        errors.append(
            f"upstream is not trusted {expected_upstream}: got {upstream}"
        )
    return branch, upstream


def observe_origin(
    head: str,
    branch: str,
    errors: list[str],
) -> dict[str, str]:
    ref = f"refs/heads/{branch}"
    result = git("ls-remote", "--heads", TRUSTED_REMOTE, ref)
    if result.returncode != 0:
        errors.append(
            "direct origin observation failed: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
        remote_commit = ""
    else:
        matches = []
        for line in result.stdout.splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[1] == ref:
                matches.append(fields)
        remote_commit = matches[0][0] if len(matches) == 1 else ""
        if remote_commit != head:
            errors.append(
                "direct origin commit mismatch: "
                f"expected {head}, got {remote_commit or '<missing>'}"
            )
    return {
        "remote": TRUSTED_REMOTE,
        "ref": ref,
        "commit": remote_commit,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def verify(
    require_origin: bool,
    expected_commit: str | None,
    remote: str = TRUSTED_REMOTE,
    branch: str | None = None,
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    frozen_files = load_frozen_files(errors)
    repo_root_text = output(git("rev-parse", "--show-toplevel"), "repo root", errors)
    head = output(git("rev-parse", "HEAD"), "HEAD", errors)
    tree = output(git("rev-parse", "HEAD^{tree}"), "HEAD tree", errors)
    prefix = output(git("rev-parse", "--show-prefix"), "project prefix", errors)
    if expected_commit and (
        len(expected_commit) != 40
        or any(character not in "0123456789abcdef" for character in expected_commit)
    ):
        errors.append("expected commit must be a full lowercase Git object id")
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
    trusted_branch_name = ""
    remote_observation: dict[str, str] = {}
    if require_origin:
        if remote != TRUSTED_REMOTE:
            errors.append(
                f"remote is not trusted {TRUSTED_REMOTE!r}: got {remote!r}"
            )
        trusted_branch_name, upstream = trusted_branch(branch, errors)
        remote_url = output(
            git("remote", "get-url", TRUSTED_REMOTE),
            "origin URL",
            errors,
        )
        if not remote_url:
            errors.append("origin remote has no URL")
        if head and trusted_branch_name and remote_url:
            remote_observation = observe_origin(
                head,
                trusted_branch_name,
                errors,
            )

    facts = {
        "repo_root": repo_root_text,
        "project_prefix": prefix,
        "head": head,
        "tree": tree,
        "upstream": upstream,
        "trusted_remote": TRUSTED_REMOTE if require_origin else "",
        "trusted_branch": trusted_branch_name,
        "remote_observation": remote_observation,
    }
    return errors, facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-origin", action="store_true")
    parser.add_argument("--expected-commit")
    parser.add_argument("--remote", default=TRUSTED_REMOTE)
    parser.add_argument("--branch")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, facts = verify(
        args.require_origin,
        args.expected_commit,
        args.remote,
        args.branch,
    )
    if args.json:
        print(json.dumps({"status": "fail" if errors else "pass", "facts": facts, "errors": errors}, ensure_ascii=False, indent=2))
    elif errors:
        print("git state verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "git state verification: PASS "
            f"(head={facts['head']}, tree={facts['tree']}, "
            f"origin_ref={facts['remote_observation'].get('ref', 'not-required')})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
