#!/usr/bin/env python3
"""Directly observe trusted origin and verify an optional frozen-bundle commit."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
TRUSTED_REMOTE = "origin"
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
BUNDLE = PROJECT_ROOT / BUNDLE_RELATIVE


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_bytes(cwd: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
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


def resolve_branch(remote: str, requested_branch: str | None) -> str:
    if remote != TRUSTED_REMOTE:
        raise RuntimeError(
            f"untrusted remote {remote!r}; trusted remote is {TRUSTED_REMOTE!r}"
        )
    if requested_branch:
        branch = requested_branch
    else:
        upstream = checked(
            PROJECT_ROOT,
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{upstream}",
        )
        remote_prefix = f"{TRUSTED_REMOTE}/"
        if not upstream.startswith(remote_prefix):
            raise RuntimeError(
                f"upstream {upstream!r} is not on trusted remote "
                f"{TRUSTED_REMOTE!r}; pass --branch explicitly"
            )
        branch = upstream[len(remote_prefix) :]
    valid = git(PROJECT_ROOT, "check-ref-format", "--branch", branch)
    if valid.returncode != 0:
        raise RuntimeError(f"invalid remote branch: {branch!r}")
    return branch


def observe_remote(
    expected_commit: str,
    remote: str,
    branch: str,
    errors: list[str],
) -> dict[str, str]:
    ref = f"refs/heads/{branch}"
    observed = checked(PROJECT_ROOT, "ls-remote", "--heads", remote, ref)
    matching_lines = []
    for line in observed.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[1] == ref:
            matching_lines.append(fields)
    remote_commit = matching_lines[0][0] if len(matching_lines) == 1 else ""
    observation = {
        "remote": remote,
        "ref": ref,
        "commit": remote_commit,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    if remote_commit != expected_commit:
        errors.append(
            "remote_commit_mismatch: "
            f"expected {expected_commit}, got {remote_commit or '<missing>'}"
        )
    return observation


def verify_bundle_at_head(
    head: str,
    errors: list[str],
    facts: dict[str, object],
) -> None:
    prefix = checked(PROJECT_ROOT, "rev-parse", "--show-prefix")
    repo_relative = f"{prefix}{BUNDLE_RELATIVE}"
    facts["project_prefix"] = prefix
    facts["bundle_path"] = BUNDLE_RELATIVE

    tracked = git(
        PROJECT_ROOT,
        "ls-files",
        "--error-unmatch",
        "--",
        f":(top){repo_relative}",
    )
    if tracked.returncode != 0:
        errors.append("frozen_bundle_not_tracked")

    at_head = git(PROJECT_ROOT, "cat-file", "-e", f"{head}:{repo_relative}")
    if at_head.returncode != 0:
        errors.append("frozen_bundle_absent_from_HEAD")
        return
    if BUNDLE.is_symlink() or not BUNDLE.is_file():
        errors.append("frozen_bundle_missing_from_worktree")
        return

    head_bytes = git_bytes(PROJECT_ROOT, "show", f"{head}:{repo_relative}")
    if head_bytes.returncode != 0:
        errors.append("frozen_bundle_HEAD_blob_unreadable")
        return
    working_bytes = BUNDLE.read_bytes()
    if working_bytes != head_bytes.stdout:
        errors.append("frozen_bundle_worktree_differs_from_HEAD")

    tree = checked(
        PROJECT_ROOT,
        "ls-tree",
        "--full-name",
        "-z",
        head,
        "--",
        f":(top,literal){repo_relative}",
    )
    records = [record for record in tree.split("\0") if record]
    if len(records) != 1 or "\t" not in records[0]:
        errors.append("frozen_bundle_HEAD_entry_is_not_blob")
        return
    metadata, observed_path = records[0].split("\t", 1)
    fields = metadata.split()
    if (
        len(fields) != 3
        or fields[1] != "blob"
        or observed_path != repo_relative
    ):
        errors.append("frozen_bundle_HEAD_entry_is_not_blob")
        return
    facts.update(
        {
            "bundle_git_mode": fields[0],
            "bundle_git_type": fields[1],
            "bundle_git_blob": fields[2],
            "bundle_sha256": hashlib.sha256(head_bytes.stdout).hexdigest(),
        }
    )


def verify_fresh_clone(
    commit: str,
    remote: str,
    facts: dict[str, object],
    errors: list[str],
) -> None:
    remote_url = checked(PROJECT_ROOT, "remote", "get-url", remote)
    with tempfile.TemporaryDirectory(prefix="ids-remote-verify-") as temp:
        clone_root = Path(temp) / "repo"
        clone = git(
            Path(temp),
            "clone",
            "--no-checkout",
            "--origin",
            remote,
            remote_url,
            str(clone_root),
        )
        if clone.returncode != 0:
            errors.append(
                f"fresh_clone_failed: {clone.stderr.strip() or clone.stdout.strip()}"
            )
            return
        cloned_commit = checked(clone_root, "rev-parse", f"{commit}^{{commit}}")
        cloned_tree = checked(clone_root, "rev-parse", f"{commit}^{{tree}}")
        facts.update(
            {
                "fresh_clone": True,
                "cloned_commit": cloned_commit,
                "cloned_tree": cloned_tree,
            }
        )
        if cloned_commit != commit:
            errors.append("fresh_clone_commit_mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit")
    parser.add_argument("--remote", default=TRUSTED_REMOTE)
    parser.add_argument("--branch")
    parser.add_argument("--fresh-clone", action="store_true")
    parser.add_argument("--verify-frozen-bundle", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.remote != TRUSTED_REMOTE:
        print(
            f"--remote must be trusted remote {TRUSTED_REMOTE!r}",
            file=sys.stderr,
        )
        return 2
    if args.commit is not None and not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        print("--commit must be a full 40-character commit", file=sys.stderr)
        return 2
    if not args.verify_frozen_bundle and args.commit is None:
        print("--commit is required unless --verify-frozen-bundle is used", file=sys.stderr)
        return 2

    errors: list[str] = []
    facts: dict[str, object] = {
        "mode": (
            "frozen_bundle_commit"
            if args.verify_frozen_bundle
            else "remote_commit"
        )
    }
    try:
        head = checked(PROJECT_ROOT, "rev-parse", "HEAD")
        expected_commit = head if args.verify_frozen_bundle else args.commit
        assert expected_commit is not None
        facts.update(
            {
                "requested_commit": args.commit,
                "expected_remote_commit": expected_commit,
                "head": head,
                "head_tree": checked(PROJECT_ROOT, "rev-parse", "HEAD^{tree}"),
            }
        )
        if args.verify_frozen_bundle:
            if args.commit is not None and args.commit != head:
                errors.append(
                    f"HEAD differs from requested commit: expected {args.commit}, got {head}"
                )
            verify_bundle_at_head(head, errors, facts)
        branch = resolve_branch(args.remote, args.branch)
        facts["branch"] = branch
        observation = observe_remote(
            expected_commit,
            args.remote,
            branch,
            errors,
        )
        facts["remote_observation"] = observation
        if args.fresh_clone and not errors:
            verify_fresh_clone(expected_commit, args.remote, facts, errors)
    except RuntimeError as exc:
        errors.append(str(exc))

    payload = {
        "schema_version": 1,
        "status": "fail" if errors else "pass",
        "facts": facts,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif errors:
        print("remote commit verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        observation = facts.get("remote_observation", {})
        print(
            "remote commit verification: PASS "
            f"({observation.get('ref')}={observation.get('commit')}, "
            f"mode={facts['mode']})"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
