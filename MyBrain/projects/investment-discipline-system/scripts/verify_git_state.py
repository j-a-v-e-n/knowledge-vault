#!/usr/bin/env python3
"""Verify project Git state against the contract-declared trusted remote."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
CONTRACT_RELATIVE = "governance/ACCEPTANCE_CONTRACT_V1.json"
CONTRACT = PROJECT_ROOT / CONTRACT_RELATIVE
FROZEN_BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FROZEN_BUNDLE = PROJECT_ROOT / FROZEN_BUNDLE_RELATIVE
TRUSTED_REMOTE_FIELDS = {
    "name",
    "fetch_url",
    "branch",
    "project_prefix",
}


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_bytes(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def output(
    result: subprocess.CompletedProcess[str],
    label: str,
    errors: list[str],
) -> str:
    if result.returncode != 0:
        errors.append(
            f"{label}: {result.stderr.strip() or result.stdout.strip() or 'git command failed'}"
        )
        return ""
    return result.stdout.strip()


def load_contract(
    head: str,
    project_prefix: str,
    errors: list[str],
) -> dict[str, object]:
    try:
        working_bytes = CONTRACT.read_bytes()
    except FileNotFoundError:
        errors.append("governance acceptance contract is missing")
        return {}
    if CONTRACT.is_symlink():
        errors.append("governance acceptance contract must not be a symlink")
        return {}
    repo_relative = f"{project_prefix}{CONTRACT_RELATIVE}"
    at_head = git_bytes("show", f"{head}:{repo_relative}")
    if at_head.returncode != 0:
        errors.append("governance acceptance contract is absent from HEAD")
        return {}
    if working_bytes != at_head.stdout:
        errors.append("governance acceptance contract differs from HEAD")
        return {}
    try:
        contract = json.loads(working_bytes.decode("utf-8"))
    except UnicodeDecodeError as exc:
        errors.append(f"governance acceptance contract is not UTF-8: {exc}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(
            "governance acceptance contract is invalid JSON: "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
        return {}
    if not isinstance(contract, dict):
        errors.append("governance acceptance contract must be a JSON object")
        return {}
    return contract


def load_frozen_files(
    contract: dict[str, object],
    errors: list[str],
) -> list[str]:
    change_control = contract.get("change_control")
    frozen_files = (
        change_control.get("frozen_files")
        if isinstance(change_control, dict)
        else None
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
            or "\\" in relative
            or ".." in Path(relative).parts
        ):
            errors.append(f"contract frozen_files[{index}] has an unsafe path")
            continue
        if relative in seen:
            errors.append(
                f"contract frozen_files contains duplicate path: {relative}"
            )
            continue
        seen.add(relative)
        safe_files.append(relative)
    return safe_files


def load_trusted_remote(
    contract: dict[str, object],
    errors: list[str],
) -> dict[str, str]:
    change_control = contract.get("change_control")
    trusted = (
        change_control.get("trusted_git_remote")
        if isinstance(change_control, dict)
        else None
    )
    if not isinstance(trusted, dict) or set(trusted) != TRUSTED_REMOTE_FIELDS:
        errors.append(
            "contract change_control.trusted_git_remote must contain exactly "
            "name, fetch_url, branch, project_prefix"
        )
        return {}
    values: dict[str, str] = {}
    for field in sorted(TRUSTED_REMOTE_FIELDS):
        value = trusted.get(field)
        if not isinstance(value, str):
            errors.append(f"trusted_git_remote.{field} must be a string")
        else:
            values[field] = value
    if len(values) != len(TRUSTED_REMOTE_FIELDS):
        return {}
    if (
        not values["name"]
        or values["name"].startswith("-")
        or values["name"].endswith("/")
        or ".." in values["name"]
        or "@{" in values["name"]
        or re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._/-]*",
            values["name"],
        )
        is None
    ):
        errors.append(
            f"trusted_git_remote.name is invalid: {values['name']!r}"
        )
    if (
        not values["fetch_url"]
        or values["fetch_url"].startswith("-")
        or "\n" in values["fetch_url"]
        or "\r" in values["fetch_url"]
    ):
        errors.append(
            "trusted_git_remote.fetch_url must be one safe nonempty line"
        )
    branch_check = git(
        "check-ref-format",
        "--branch",
        values["branch"],
    )
    if not values["branch"] or branch_check.returncode != 0:
        errors.append(
            f"trusted_git_remote.branch is invalid: {values['branch']!r}"
        )
    prefix = values["project_prefix"]
    if (
        prefix.startswith("/")
        or "\\" in prefix
        or (prefix and not prefix.endswith("/"))
        or ".." in Path(prefix).parts
        or "." in Path(prefix).parts
    ):
        errors.append(
            f"trusted_git_remote.project_prefix is invalid: {prefix!r}"
        )
    return values


def verify_versioned_file(
    relative: str,
    *,
    label: str,
    project_prefix: str,
    errors: list[str],
) -> None:
    repo_relative = f"{project_prefix}{relative}"
    tracked = git(
        "ls-files",
        "--error-unmatch",
        "--",
        f":(top,literal){repo_relative}",
    )
    if tracked.returncode != 0:
        errors.append(f"{label} is not tracked: {relative}")
    at_head = git("cat-file", "-e", f"HEAD:{repo_relative}")
    if at_head.returncode != 0:
        errors.append(f"{label} is absent from HEAD: {relative}")


def verify_trusted_local_identity(
    trusted: dict[str, str],
    requested_remote: str | None,
    requested_branch: str | None,
    errors: list[str],
) -> tuple[str, str, list[str], bool]:
    if not trusted:
        return "", "", [], False
    if requested_remote is not None and requested_remote != trusted["name"]:
        errors.append(
            "remote does not match contract trusted remote "
            f"{trusted['name']!r}: got {requested_remote!r}"
        )
    if requested_branch is not None and requested_branch != trusted["branch"]:
        errors.append(
            "branch does not match contract trusted branch "
            f"{trusted['branch']!r}: got {requested_branch!r}"
        )
    branch_result = git("symbolic-ref", "--short", "HEAD")
    current_branch = (
        branch_result.stdout.strip() if branch_result.returncode == 0 else ""
    )
    if not current_branch:
        errors.append("current branch is detached or unreadable")
    elif current_branch != trusted["branch"]:
        errors.append(
            "current branch does not match contract: "
            f"expected {trusted['branch']!r}, got {current_branch!r}"
        )

    upstream_result = git(
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    upstream = (
        upstream_result.stdout.strip()
        if upstream_result.returncode == 0
        else ""
    )
    expected_upstream = f"{trusted['name']}/{trusted['branch']}"
    if not upstream:
        errors.append(
            "current upstream is missing or unreadable: "
            f"{upstream_result.stderr.strip() or upstream_result.stdout.strip()}"
        )
    elif upstream != expected_upstream:
        errors.append(
            "current upstream does not match contract: "
            f"expected {expected_upstream!r}, got {upstream!r}"
        )

    url_result = git(
        "remote",
        "get-url",
        "--all",
        trusted["name"],
    )
    urls = (
        url_result.stdout.splitlines()
        if url_result.returncode == 0
        else []
    )
    url_matches = urls == [trusted["fetch_url"]]
    if not url_matches:
        errors.append(
            "trusted remote fetch URL does not match contract: "
            f"expected {[trusted['fetch_url']]!r}, got {urls!r}"
        )
    return current_branch, upstream, urls, url_matches


def observe_trusted_remote(
    head: str,
    trusted: dict[str, str],
    errors: list[str],
) -> dict[str, str]:
    ref = f"refs/heads/{trusted['branch']}"
    result = git(
        "ls-remote",
        "--heads",
        trusted["fetch_url"],
        ref,
    )
    if result.returncode != 0:
        errors.append(
            "direct trusted remote observation failed: "
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
                "direct trusted remote commit mismatch: "
                f"expected {head}, got {remote_commit or '<missing>'}"
            )
    return {
        "remote": trusted["name"],
        "fetch_url": trusted["fetch_url"],
        "ref": ref,
        "commit": remote_commit,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "observation_kind": "non_atomic_ls_remote",
    }


def verify(
    require_origin: bool,
    expected_commit: str | None,
    remote: str | None = None,
    branch: str | None = None,
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    repo_root_text = output(
        git("rev-parse", "--show-toplevel"),
        "repo root",
        errors,
    )
    head = output(git("rev-parse", "HEAD"), "HEAD", errors)
    tree = output(git("rev-parse", "HEAD^{tree}"), "HEAD tree", errors)
    prefix = output(
        git("rev-parse", "--show-prefix"),
        "project prefix",
        errors,
    )
    contract = load_contract(head, prefix, errors) if head else {}
    frozen_files = load_frozen_files(contract, errors) if contract else []
    trusted = load_trusted_remote(contract, errors) if contract else {}

    if expected_commit and (
        len(expected_commit) != 40
        or any(
            character not in "0123456789abcdef"
            for character in expected_commit
        )
    ):
        errors.append("expected commit must be a full lowercase Git object id")
    if expected_commit and head != expected_commit:
        errors.append(
            f"HEAD differs from expected commit: expected {expected_commit}, got {head}"
        )

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
        errors.append(
            f"git diff --check failed:\n{diff_check.stdout}{diff_check.stderr}"
        )

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

    current_branch = ""
    upstream = ""
    configured_urls: list[str] = []
    remote_observation: dict[str, str] = {}
    if trusted and prefix != trusted["project_prefix"]:
        errors.append(
            "project prefix does not match contract: "
            f"expected {trusted['project_prefix']!r}, got {prefix!r}"
        )
    if require_origin:
        (
            current_branch,
            upstream,
            configured_urls,
            url_matches,
        ) = verify_trusted_local_identity(
            trusted,
            remote,
            branch,
            errors,
        )
        if head and trusted and url_matches:
            remote_observation = observe_trusted_remote(
                head,
                trusted,
                errors,
            )

    facts = {
        "repo_root": repo_root_text,
        "project_prefix": prefix,
        "head": head,
        "tree": tree,
        "current_branch": current_branch,
        "upstream": upstream,
        "trusted_git_remote": trusted,
        "trusted_remote": trusted.get("name", "") if require_origin else "",
        "trusted_branch": trusted.get("branch", "") if require_origin else "",
        "configured_fetch_urls": configured_urls,
        "remote_observation": remote_observation,
        "toctou_semantics": (
            "The direct remote observation is non-atomic and cannot eliminate "
            "changes before or after the recorded read."
        ),
    }
    return errors, facts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-origin",
        action="store_true",
        help=(
            "Require the remote identity declared by trusted_git_remote. "
            "The option name is retained for the frozen contract command."
        ),
    )
    parser.add_argument("--expected-commit")
    parser.add_argument("--remote")
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
        print(
            json.dumps(
                {
                    "status": "fail" if errors else "pass",
                    "facts": facts,
                    "errors": errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    elif errors:
        print("git state verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "git state verification: PASS "
            f"(head={facts['head']}, tree={facts['tree']}, "
            f"trusted_ref={facts['remote_observation'].get('ref', 'not-required')})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
