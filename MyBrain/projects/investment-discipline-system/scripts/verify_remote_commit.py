#!/usr/bin/env python3
"""Verify a contract-declared Git remote and, for bundle D, a fresh clone."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
CONTRACT_RELATIVE = "governance/ACCEPTANCE_CONTRACT_V1.json"
CONTRACT = PROJECT_ROOT / CONTRACT_RELATIVE
BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
BUNDLE = PROJECT_ROOT / BUNDLE_RELATIVE
INNER_CONTEXT_ENV = "IDS_FROZEN_REMOTE_INNER_CONTEXT_V1"
INNER_CONTEXT_MODE = "fresh_clone_governance_v1"
TRUSTED_REMOTE_FIELDS = {
    "name",
    "fetch_url",
    "branch",
    "project_prefix",
}
INNER_CONTEXT_FIELDS = {
    "schema_version",
    "mode",
    "nonce",
    "commit",
    "remote_name",
    "fetch_url",
    "branch",
    "project_prefix",
    "repo_root",
    "project_root",
    "receipt_path",
}
FULL_SHA1 = re.compile(r"[0-9a-f]{40}")
FULL_SHA256 = re.compile(r"[0-9a-f]{64}")


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite an earlier object key."""


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate object key: {key}")
        value[key] = item
    return value


def parse_json_bytes(payload: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"{label} is not UTF-8: {exc}") from None
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        raise RuntimeError(f"{label} is invalid JSON: {exc}") from None
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must be a JSON object")
    return value


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
            f"git {' '.join(args)} failed: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def validate_trusted_remote(
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

    name = values["name"]
    if (
        not name
        or name.startswith("-")
        or name.endswith("/")
        or ".." in name
        or "@{" in name
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", name) is None
    ):
        errors.append(f"trusted_git_remote.name is invalid: {name!r}")
    fetch_url = values["fetch_url"]
    if (
        not fetch_url
        or fetch_url.startswith("-")
        or "\n" in fetch_url
        or "\r" in fetch_url
    ):
        errors.append(
            "trusted_git_remote.fetch_url must be one safe nonempty line"
        )
    branch = values["branch"]
    branch_check = git(PROJECT_ROOT, "check-ref-format", "--branch", branch)
    if not branch or branch_check.returncode != 0:
        errors.append(f"trusted_git_remote.branch is invalid: {branch!r}")
    prefix = values["project_prefix"]
    prefix_path = Path(prefix)
    if (
        prefix.startswith("/")
        or "\\" in prefix
        or (prefix and not prefix.endswith("/"))
        or ".." in prefix_path.parts
        or "." in prefix_path.parts
    ):
        errors.append(
            f"trusted_git_remote.project_prefix is invalid: {prefix!r}"
        )
    return values


def load_contract_at_head(
    head: str,
    project_prefix: str,
    errors: list[str],
) -> dict[str, object]:
    repo_relative = f"{project_prefix}{CONTRACT_RELATIVE}"
    result = git_bytes(PROJECT_ROOT, "show", f"{head}:{repo_relative}")
    if result.returncode != 0:
        errors.append("acceptance_contract_absent_from_HEAD")
        return {}
    if CONTRACT.is_symlink() or not CONTRACT.is_file():
        errors.append("acceptance_contract_missing_from_worktree")
        return {}
    working_bytes = CONTRACT.read_bytes()
    if working_bytes != result.stdout:
        errors.append("acceptance_contract_worktree_differs_from_HEAD")
        return {}
    try:
        return parse_json_bytes(result.stdout, "acceptance contract at HEAD")
    except RuntimeError as exc:
        errors.append(str(exc))
        return {}


def requested_identity(
    requested_remote: str | None,
    requested_branch: str | None,
    trusted: dict[str, str],
    errors: list[str],
) -> tuple[str, str]:
    remote = requested_remote or trusted.get("name", "")
    branch = requested_branch or trusted.get("branch", "")
    if trusted:
        if remote != trusted["name"]:
            errors.append(
                "--remote must match contract trusted remote "
                f"{trusted['name']!r}: got {remote!r}"
            )
        if branch != trusted["branch"]:
            errors.append(
                "--branch must match contract trusted branch "
                f"{trusted['branch']!r}: got {branch!r}"
            )
    return remote, branch


def configured_fetch_urls(remote: str, errors: list[str]) -> list[str]:
    result = git(PROJECT_ROOT, "remote", "get-url", "--all", remote)
    if result.returncode != 0:
        errors.append(
            f"trusted remote {remote!r} has no readable fetch URL: "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
        return []
    return result.stdout.splitlines()


def verify_local_git_identity(
    trusted: dict[str, str],
    actual_prefix: str,
    *,
    inner_clone: bool,
    expected_commit: str,
    errors: list[str],
    facts: dict[str, object],
) -> None:
    if not trusted:
        return
    expected_prefix = trusted["project_prefix"]
    if actual_prefix != expected_prefix:
        errors.append(
            "project_prefix_mismatch: "
            f"expected {expected_prefix!r}, got {actual_prefix!r}"
        )

    urls = configured_fetch_urls(trusted["name"], errors)
    facts["configured_fetch_urls"] = urls
    if urls and urls != [trusted["fetch_url"]]:
        errors.append(
            "trusted_remote_fetch_url_mismatch: "
            f"expected {[trusted['fetch_url']]!r}, got {urls!r}"
        )

    expected_upstream = f"{trusted['name']}/{trusted['branch']}"
    if inner_clone:
        detached = git(PROJECT_ROOT, "symbolic-ref", "-q", "--short", "HEAD")
        if detached.returncode == 0:
            errors.append(
                "fresh_clone_HEAD_must_be_detached: "
                f"got {detached.stdout.strip()!r}"
            )
        clone_ref = f"refs/remotes/{trusted['name']}/{trusted['branch']}"
        clone_ref_result = git(PROJECT_ROOT, "rev-parse", clone_ref)
        clone_ref_commit = (
            clone_ref_result.stdout.strip()
            if clone_ref_result.returncode == 0
            else ""
        )
        facts["clone_remote_tracking_ref"] = {
            "ref": clone_ref,
            "commit": clone_ref_commit,
        }
        if clone_ref_commit != expected_commit:
            errors.append(
                "fresh_clone_remote_tracking_ref_mismatch: "
                f"expected {expected_commit}, got {clone_ref_commit or '<missing>'}"
            )
        return

    branch_result = git(PROJECT_ROOT, "symbolic-ref", "--short", "HEAD")
    current_branch = (
        branch_result.stdout.strip() if branch_result.returncode == 0 else ""
    )
    if not current_branch:
        errors.append("current_branch_is_detached_or_unreadable")
    elif current_branch != trusted["branch"]:
        errors.append(
            "current_branch_mismatch: "
            f"expected {trusted['branch']!r}, got {current_branch!r}"
        )
    upstream_result = git(
        PROJECT_ROOT,
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
    if not upstream:
        errors.append(
            "current_upstream_missing_or_unreadable: "
            f"{upstream_result.stderr.strip() or upstream_result.stdout.strip()}"
        )
    elif upstream != expected_upstream:
        errors.append(
            "current_upstream_mismatch: "
            f"expected {expected_upstream!r}, got {upstream!r}"
        )
    facts["current_branch"] = current_branch
    facts["upstream"] = upstream


def observe_remote(
    expected_commit: str,
    trusted: dict[str, str],
    errors: list[str],
) -> dict[str, str]:
    ref = f"refs/heads/{trusted['branch']}"
    observed = git(
        PROJECT_ROOT,
        "ls-remote",
        "--heads",
        trusted["fetch_url"],
        ref,
    )
    if observed.returncode != 0:
        errors.append(
            "direct_remote_observation_failed: "
            f"{observed.stderr.strip() or observed.stdout.strip()}"
        )
        remote_commit = ""
    else:
        matching_lines = []
        for line in observed.stdout.splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[1] == ref:
                matching_lines.append(fields)
        remote_commit = (
            matching_lines[0][0] if len(matching_lines) == 1 else ""
        )
        if remote_commit != expected_commit:
            errors.append(
                "remote_commit_mismatch: "
                f"expected {expected_commit}, got {remote_commit or '<missing>'}"
            )
    return {
        "remote": trusted["name"],
        "fetch_url": trusted["fetch_url"],
        "ref": ref,
        "commit": remote_commit,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "observation_kind": "non_atomic_ls_remote",
    }


def verify_bundle_at_head(
    head: str,
    project_prefix: str,
    errors: list[str],
    facts: dict[str, object],
) -> bytes | None:
    repo_relative = f"{project_prefix}{BUNDLE_RELATIVE}"
    facts["project_prefix"] = project_prefix
    facts["bundle_path"] = BUNDLE_RELATIVE

    tracked = git(
        PROJECT_ROOT,
        "ls-files",
        "--error-unmatch",
        "--",
        f":(top,literal){repo_relative}",
    )
    if tracked.returncode != 0:
        errors.append("frozen_bundle_not_tracked")

    at_head = git(PROJECT_ROOT, "cat-file", "-e", f"{head}:{repo_relative}")
    if at_head.returncode != 0:
        errors.append("frozen_bundle_absent_from_HEAD")
        return None
    if BUNDLE.is_symlink() or not BUNDLE.is_file():
        errors.append("frozen_bundle_missing_from_worktree")
        return None

    head_bytes = git_bytes(PROJECT_ROOT, "show", f"{head}:{repo_relative}")
    if head_bytes.returncode != 0:
        errors.append("frozen_bundle_HEAD_blob_unreadable")
        return None
    working_bytes = BUNDLE.read_bytes()
    if working_bytes != head_bytes.stdout:
        errors.append("frozen_bundle_worktree_differs_from_HEAD")

    tree = git_bytes(
        PROJECT_ROOT,
        "ls-tree",
        "--full-name",
        "-z",
        head,
        "--",
        f":(top,literal){repo_relative}",
    )
    records = [record for record in tree.stdout.split(b"\0") if record]
    if tree.returncode != 0 or len(records) != 1 or b"\t" not in records[0]:
        errors.append("frozen_bundle_HEAD_entry_is_not_blob")
        return head_bytes.stdout
    metadata, observed_path = records[0].split(b"\t", 1)
    fields = metadata.decode("ascii", "replace").split()
    if (
        len(fields) != 3
        or fields[1] != "blob"
        or observed_path.decode("utf-8", "replace") != repo_relative
    ):
        errors.append("frozen_bundle_HEAD_entry_is_not_blob")
        return head_bytes.stdout
    facts.update(
        {
            "bundle_git_mode": fields[0],
            "bundle_git_type": fields[1],
            "bundle_git_blob": fields[2],
            "bundle_sha256": hashlib.sha256(head_bytes.stdout).hexdigest(),
        }
    )
    return head_bytes.stdout


def verify_bundle_commit_shape(
    head: str,
    project_prefix: str,
    bundle_bytes: bytes | None,
    errors: list[str],
    facts: dict[str, object],
) -> None:
    if bundle_bytes is None:
        return
    try:
        bundle = parse_json_bytes(bundle_bytes, "frozen bundle at HEAD")
    except RuntimeError as exc:
        errors.append(str(exc))
        return
    baseline = bundle.get("baseline_commit")
    if not isinstance(baseline, str) or FULL_SHA1.fullmatch(baseline) is None:
        errors.append("frozen_bundle_baseline_commit_invalid")
        return
    parents = git(PROJECT_ROOT, "rev-list", "--parents", "-n", "1", head)
    parent_fields = parents.stdout.split() if parents.returncode == 0 else []
    if len(parent_fields) != 2 or parent_fields[0] != head:
        errors.append("bundle_commit_D_must_have_exactly_one_parent")
        return
    parent = parent_fields[1]
    facts["bundle_baseline_commit"] = baseline
    facts["bundle_commit_parent"] = parent
    if parent != baseline:
        errors.append(
            "bundle_commit_D_parent_mismatch: "
            f"expected {baseline}, got {parent}"
        )

    repo_relative = f"{project_prefix}{BUNDLE_RELATIVE}"
    baseline_bundle = git(
        PROJECT_ROOT,
        "cat-file",
        "-e",
        f"{baseline}:{repo_relative}",
    )
    if baseline_bundle.returncode == 0:
        errors.append("frozen_bundle_already_existed_at_baseline")
    changed = git_bytes(
        PROJECT_ROOT,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "-z",
        head,
    )
    if changed.returncode != 0:
        errors.append(
            "bundle_commit_D_diff_unreadable: "
            f"{changed.stderr.decode('utf-8', 'replace').strip()}"
        )
        return
    changed_paths = [
        item.decode("utf-8", "replace")
        for item in changed.stdout.split(b"\0")
        if item
    ]
    facts["bundle_commit_changed_paths"] = changed_paths
    if changed_paths != [repo_relative]:
        errors.append(
            "bundle_commit_D_must_only_add_frozen_bundle: "
            f"expected {[repo_relative]!r}, got {changed_paths!r}"
        )


def load_inner_context(raw: str, errors: list[str]) -> dict[str, object]:
    try:
        context = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"inner_clone_context_invalid_JSON: {exc}")
        return {}
    if not isinstance(context, dict) or set(context) != INNER_CONTEXT_FIELDS:
        errors.append("inner_clone_context_fields_differ")
        return {}
    if context.get("schema_version") != 1:
        errors.append("inner_clone_context_schema_differs")
    if context.get("mode") != INNER_CONTEXT_MODE:
        errors.append("inner_clone_context_mode_differs")
    if (
        not isinstance(context.get("nonce"), str)
        or FULL_SHA256.fullmatch(str(context.get("nonce"))) is None
    ):
        errors.append("inner_clone_context_nonce_invalid")
    if (
        not isinstance(context.get("commit"), str)
        or FULL_SHA1.fullmatch(str(context.get("commit"))) is None
    ):
        errors.append("inner_clone_context_commit_invalid")
    for field in (
        "remote_name",
        "fetch_url",
        "branch",
        "project_prefix",
        "repo_root",
        "project_root",
        "receipt_path",
    ):
        if not isinstance(context.get(field), str):
            errors.append(f"inner_clone_context_{field}_invalid")
    return context


def write_inner_receipt(
    context: dict[str, object],
    facts: dict[str, object],
    errors: list[str],
) -> None:
    receipt_path = Path(str(context["receipt_path"]))
    expected_parent = Path(str(context["repo_root"])).parent.resolve()
    if (
        not receipt_path.is_absolute()
        or receipt_path.parent.resolve() != expected_parent
        or receipt_path.exists()
    ):
        errors.append("inner_clone_receipt_path_invalid_or_used")
        return
    try:
        parent_mode = stat.S_IMODE(receipt_path.parent.stat().st_mode)
    except OSError as exc:
        errors.append(f"inner_clone_receipt_parent_unreadable: {exc}")
        return
    if parent_mode & 0o077:
        errors.append("inner_clone_receipt_parent_is_not_private")
        return

    receipt = {
        "schema_version": 1,
        "verification_scope": "inner_clone",
        "nonce": context["nonce"],
        "commit": context["commit"],
        "remote_name": context["remote_name"],
        "fetch_url": context["fetch_url"],
        "branch": context["branch"],
        "project_prefix": context["project_prefix"],
        "head_tree": facts.get("head_tree"),
        "bundle_sha256": facts.get("bundle_sha256"),
    }
    payload = (json.dumps(receipt, sort_keys=True) + "\n").encode("utf-8")
    try:
        descriptor = os.open(
            receipt_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        errors.append(f"inner_clone_receipt_write_failed: {exc}")


def verify_inner_clone(
    args: argparse.Namespace,
    raw_context: str,
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    facts: dict[str, object] = {
        "mode": "frozen_bundle_inner_clone",
        "verification_scope": "inner_clone",
        "full_remote_verification": False,
    }
    context = load_inner_context(raw_context, errors)
    if not context:
        return errors, facts
    if not args.verify_frozen_bundle:
        errors.append("inner_clone_mode_requires_--verify-frozen-bundle")
    if args.fresh_clone:
        errors.append("inner_clone_mode_cannot_request_another_fresh_clone")
    if args.commit != context["commit"]:
        errors.append(
            "inner_clone_requested_commit_mismatch: "
            f"expected {context['commit']}, got {args.commit}"
        )
    if args.remote != context["remote_name"]:
        errors.append(
            "inner_clone_requested_remote_mismatch: "
            f"expected {context['remote_name']!r}, got {args.remote!r}"
        )
    if args.branch is not None and args.branch != context["branch"]:
        errors.append(
            "inner_clone_requested_branch_mismatch: "
            f"expected {context['branch']!r}, got {args.branch!r}"
        )

    try:
        head = checked(PROJECT_ROOT, "rev-parse", "HEAD")
        head_tree = checked(PROJECT_ROOT, "rev-parse", "HEAD^{tree}")
        prefix = checked(PROJECT_ROOT, "rev-parse", "--show-prefix")
        repo_root = Path(checked(PROJECT_ROOT, "rev-parse", "--show-toplevel")).resolve()
        facts.update(
            {
                "requested_commit": args.commit,
                "expected_remote_commit": context["commit"],
                "head": head,
                "head_tree": head_tree,
                "branch": context["branch"],
                "project_prefix": prefix,
            }
        )
        if head != context["commit"]:
            errors.append(
                "inner_clone_HEAD_mismatch: "
                f"expected {context['commit']}, got {head}"
            )
        if PROJECT_ROOT != Path(str(context["project_root"])).resolve():
            errors.append("inner_clone_project_root_mismatch")
        if repo_root != Path(str(context["repo_root"])).resolve():
            errors.append("inner_clone_repo_root_mismatch")
        expected_script = PROJECT_ROOT / "scripts" / "verify_remote_commit.py"
        if Path(__file__).resolve() != expected_script.resolve():
            errors.append("inner_clone_verifier_is_not_from_cloned_project")

        contract = load_contract_at_head(head, prefix, errors)
        trusted = validate_trusted_remote(contract, errors) if contract else {}
        expected_trusted = {
            "name": context["remote_name"],
            "fetch_url": context["fetch_url"],
            "branch": context["branch"],
            "project_prefix": context["project_prefix"],
        }
        if trusted and trusted != expected_trusted:
            errors.append(
                "inner_clone_contract_remote_identity_mismatch: "
                f"expected {expected_trusted!r}, got {trusted!r}"
            )
        facts["trusted_git_remote"] = trusted
        bundle_bytes = verify_bundle_at_head(head, prefix, errors, facts)
        verify_bundle_commit_shape(head, prefix, bundle_bytes, errors, facts)
        verify_local_git_identity(
            trusted,
            prefix,
            inner_clone=True,
            expected_commit=head,
            errors=errors,
            facts=facts,
        )
        facts["remote_observation"] = {
            "remote": trusted.get("name", ""),
            "fetch_url": trusted.get("fetch_url", ""),
            "ref": (
                f"refs/remotes/{trusted.get('name', '')}/"
                f"{trusted.get('branch', '')}"
            ),
            "commit": facts.get("clone_remote_tracking_ref", {}).get(
                "commit", ""
            ),
            "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "observation_kind": "fresh_clone_remote_tracking_ref",
        }
        if not errors:
            write_inner_receipt(context, facts, errors)
    except RuntimeError as exc:
        errors.append(str(exc))
    return errors, facts


def expected_inner_receipt(
    context: dict[str, object],
    cloned_tree: str,
    bundle_sha256: str,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "verification_scope": "inner_clone",
        "nonce": context["nonce"],
        "commit": context["commit"],
        "remote_name": context["remote_name"],
        "fetch_url": context["fetch_url"],
        "branch": context["branch"],
        "project_prefix": context["project_prefix"],
        "head_tree": cloned_tree,
        "bundle_sha256": bundle_sha256,
    }


def verify_fresh_clone(
    commit: str,
    trusted: dict[str, str],
    *,
    verify_frozen_governance: bool,
    facts: dict[str, object],
    errors: list[str],
) -> None:
    with tempfile.TemporaryDirectory(prefix="ids-remote-verify-") as temp:
        temp_root = Path(temp).resolve()
        clone_root = temp_root / "repo"
        clone = git(
            temp_root,
            "clone",
            "--no-checkout",
            "--single-branch",
            "--branch",
            trusted["branch"],
            "--no-tags",
            "--no-local",
            "--origin",
            trusted["name"],
            trusted["fetch_url"],
            str(clone_root),
        )
        if clone.returncode != 0:
            errors.append(
                f"fresh_clone_failed: {clone.stderr.strip() or clone.stdout.strip()}"
            )
            return
        cloned_url_result = git(
            clone_root,
            "remote",
            "get-url",
            "--all",
            trusted["name"],
        )
        cloned_urls = (
            cloned_url_result.stdout.splitlines()
            if cloned_url_result.returncode == 0
            else []
        )
        if cloned_urls != [trusted["fetch_url"]]:
            errors.append(
                "fresh_clone_fetch_url_mismatch: "
                f"expected {[trusted['fetch_url']]!r}, got {cloned_urls!r}"
            )
            return
        cloned_ref = f"refs/remotes/{trusted['name']}/{trusted['branch']}"
        cloned_ref_commit = checked(clone_root, "rev-parse", cloned_ref)
        if cloned_ref_commit != commit:
            errors.append(
                "fresh_clone_remote_ref_mismatch: "
                f"expected {commit}, got {cloned_ref_commit}"
            )
            return
        cloned_commit = checked(clone_root, "rev-parse", f"{commit}^{{commit}}")
        cloned_tree = checked(clone_root, "rev-parse", f"{commit}^{{tree}}")
        if cloned_commit != commit:
            errors.append("fresh_clone_commit_mismatch")
            return
        checkout = git(clone_root, "checkout", "--detach", commit)
        if checkout.returncode != 0:
            errors.append(
                "fresh_clone_exact_checkout_failed: "
                f"{checkout.stderr.strip() or checkout.stdout.strip()}"
            )
            return
        clone_project = (
            clone_root / trusted["project_prefix"]
            if trusted["project_prefix"]
            else clone_root
        ).resolve()
        if not clone_project.is_dir():
            errors.append(
                "fresh_clone_project_prefix_missing: "
                f"{trusted['project_prefix']!r}"
            )
            return
        cloned_prefix = checked(clone_project, "rev-parse", "--show-prefix")
        if cloned_prefix != trusted["project_prefix"]:
            errors.append(
                "fresh_clone_project_prefix_mismatch: "
                f"expected {trusted['project_prefix']!r}, got {cloned_prefix!r}"
            )
            return

        facts.update(
            {
                "fresh_clone": True,
                "cloned_commit": cloned_commit,
                "cloned_tree": cloned_tree,
                "cloned_remote_tracking_ref": {
                    "ref": cloned_ref,
                    "commit": cloned_ref_commit,
                },
            }
        )
        if verify_frozen_governance:
            verifier = clone_project / "scripts" / "verify_governance.py"
            if verifier.is_symlink() or not verifier.is_file():
                errors.append("fresh_clone_governance_verifier_missing")
                return
            receipt_path = temp_root / "inner-receipt.json"
            context: dict[str, object] = {
                "schema_version": 1,
                "mode": INNER_CONTEXT_MODE,
                "nonce": secrets.token_hex(32),
                "commit": commit,
                "remote_name": trusted["name"],
                "fetch_url": trusted["fetch_url"],
                "branch": trusted["branch"],
                "project_prefix": trusted["project_prefix"],
                "repo_root": str(clone_root),
                "project_root": str(clone_project),
                "receipt_path": str(receipt_path),
            }
            env = os.environ.copy()
            env["IDS_PROJECT_ROOT"] = str(clone_project)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env[INNER_CONTEXT_ENV] = json.dumps(
                context,
                sort_keys=True,
                separators=(",", ":"),
            )
            governance = subprocess.run(
                [sys.executable, str(verifier)],
                cwd=clone_project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                check=False,
            )
            facts["clone_governance"] = {
                "exit_code": governance.returncode,
                "stdout_sha256": hashlib.sha256(
                    governance.stdout.encode("utf-8")
                ).hexdigest(),
                "verification_scope": "inner_clone",
            }
            if governance.returncode != 0:
                errors.append(
                    "fresh_clone_governance_failed: "
                    f"{governance.stdout.strip() or '<no verifier output>'}"
                )
                return
            if not receipt_path.is_file():
                errors.append("fresh_clone_inner_receipt_missing")
                return
            try:
                receipt = parse_json_bytes(
                    receipt_path.read_bytes(),
                    "fresh-clone inner receipt",
                )
            except (OSError, RuntimeError) as exc:
                errors.append(f"fresh_clone_inner_receipt_invalid: {exc}")
                return
            expected_receipt = expected_inner_receipt(
                context,
                cloned_tree,
                str(facts.get("bundle_sha256", "")),
            )
            if receipt != expected_receipt:
                errors.append(
                    "fresh_clone_inner_receipt_binding_mismatch: "
                    f"expected {expected_receipt!r}, got {receipt!r}"
                )
                return
            facts["clone_governance"]["inner_receipt"] = {
                key: value
                for key, value in receipt.items()
                if key != "nonce"
            }

        clone_status = checked(
            clone_project,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            ".",
        )
        if clone_status:
            errors.append(
                "fresh_clone_verification_dirtied_project:\n"
                f"{clone_status}"
            )
            return

        post_observation = observe_remote(commit, trusted, errors)
        facts["post_clone_remote_observation"] = post_observation


def verify_outer(
    args: argparse.Namespace,
) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    attempted_scope = (
        "full_outer"
        if args.verify_frozen_bundle
        else ("fresh_clone_commit" if args.fresh_clone else "direct_remote_observation")
    )
    facts: dict[str, object] = {
        "mode": (
            "frozen_bundle_commit"
            if args.verify_frozen_bundle
            else "remote_commit"
        ),
        "verification_scope": f"{attempted_scope}_required",
        "full_remote_verification": False,
        "toctou_semantics": (
            "Remote reads, clone, checkout, and verification are non-atomic; "
            "success binds the recorded observations but cannot eliminate TOCTOU."
        ),
    }
    try:
        head = checked(PROJECT_ROOT, "rev-parse", "HEAD")
        head_tree = checked(PROJECT_ROOT, "rev-parse", "HEAD^{tree}")
        prefix = checked(PROJECT_ROOT, "rev-parse", "--show-prefix")
        contract = load_contract_at_head(head, prefix, errors)
        trusted = validate_trusted_remote(contract, errors) if contract else {}
        remote, branch = requested_identity(
            args.remote,
            args.branch,
            trusted,
            errors,
        )
        expected_commit = head if args.verify_frozen_bundle else args.commit
        assert expected_commit is not None
        facts.update(
            {
                "requested_commit": args.commit,
                "expected_remote_commit": expected_commit,
                "head": head,
                "head_tree": head_tree,
                "branch": branch,
                "project_prefix": prefix,
                "trusted_git_remote": trusted,
            }
        )
        if args.verify_frozen_bundle:
            if args.commit is not None and args.commit != head:
                errors.append(
                    "HEAD differs from requested commit: "
                    f"expected {args.commit}, got {head}"
                )
            bundle_bytes = verify_bundle_at_head(
                head,
                prefix,
                errors,
                facts,
            )
            verify_bundle_commit_shape(
                head,
                prefix,
                bundle_bytes,
                errors,
                facts,
            )
        verify_local_git_identity(
            trusted,
            prefix,
            inner_clone=False,
            expected_commit=expected_commit,
            errors=errors,
            facts=facts,
        )
        if remote and trusted and remote != trusted["name"]:
            errors.append("requested remote identity was not contract-authorized")
        if branch and trusted and branch != trusted["branch"]:
            errors.append("requested branch identity was not contract-authorized")

        if not errors and trusted:
            observation = observe_remote(expected_commit, trusted, errors)
            facts["remote_observation"] = observation
        if not errors and trusted and (
            args.verify_frozen_bundle or args.fresh_clone
        ):
            verify_fresh_clone(
                expected_commit,
                trusted,
                verify_frozen_governance=args.verify_frozen_bundle,
                facts=facts,
                errors=errors,
            )
        if not errors:
            facts["verification_scope"] = attempted_scope
            facts["full_remote_verification"] = (
                attempted_scope == "full_outer"
            )
    except RuntimeError as exc:
        errors.append(str(exc))
    return errors, facts


def emit(
    args: argparse.Namespace,
    errors: list[str],
    facts: dict[str, object],
) -> int:
    payload = {
        "schema_version": 1,
        "status": "fail" if errors else "pass",
        "verification_scope": facts.get("verification_scope"),
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
            f"scope={facts['verification_scope']})"
        )
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit")
    parser.add_argument("--remote")
    parser.add_argument("--branch")
    parser.add_argument(
        "--fresh-clone",
        action="store_true",
        help=(
            "Fresh-clone a generic commit. Frozen-bundle verification always "
            "fresh-clones even when this flag is omitted."
        ),
    )
    parser.add_argument("--verify-frozen-bundle", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.commit is not None and FULL_SHA1.fullmatch(args.commit) is None:
        print("--commit must be a full 40-character commit", file=sys.stderr)
        return 2
    if not args.verify_frozen_bundle and args.commit is None:
        print(
            "--commit is required unless --verify-frozen-bundle is used",
            file=sys.stderr,
        )
        return 2

    raw_inner_context = os.environ.get(INNER_CONTEXT_ENV)
    if raw_inner_context is not None:
        errors, facts = verify_inner_clone(args, raw_inner_context)
    else:
        errors, facts = verify_outer(args)
    return emit(args, errors, facts)


if __name__ == "__main__":
    sys.exit(main())
