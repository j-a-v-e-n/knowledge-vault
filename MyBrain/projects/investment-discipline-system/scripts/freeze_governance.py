#!/usr/bin/env python3
"""Create the non-circular second-stage governance frozen bundle."""

from __future__ import annotations

import argparse
import copy
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
BUNDLE = GOVERNANCE / "FROZEN_BUNDLE_V1.json"
CANDIDATE_VERIFIER = SCRIPT_DIR / "verify_governance.py"
REMOTE_VERIFIER = SCRIPT_DIR / "verify_remote_commit.py"
CONTRACT_RELATIVE = "governance/ACCEPTANCE_CONTRACT_V1.json"
RESEARCH_RELATIVE = "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json"
ASSURANCE_RELATIVE = "governance/ASSURANCE_SUBJECTS_V1.json"
FINAL_ARTIFACT_ID = re.compile(r"ARTIFACT-CHALLENGE-FINAL-R[0-9]+")


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite an earlier object key."""


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate object key: {key}")
        value[key] = item
    return value


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


def run_python(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
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


def parse_json_object(payload: bytes, label: str) -> dict:
    try:
        value = json.loads(
            payload.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except UnicodeDecodeError as exc:
        raise SystemExit(f"invalid UTF-8 JSON {label}: {exc}") from None
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        raise SystemExit(
            f"invalid JSON {label}: {exc}"
        ) from None
    if not isinstance(value, dict):
        raise SystemExit(f"JSON must contain an object: {label}")
    return value


def load_json_object(path: Path, relative: str) -> dict:
    try:
        payload = path.read_bytes()
    except FileNotFoundError:
        raise SystemExit(f"missing frozen JSON: {relative}") from None
    return parse_json_object(payload, relative)


def require_commit(commit: str, label: str) -> str:
    result = git_bytes("rev-parse", "--verify", f"{commit}^{{commit}}")
    if result.returncode != 0:
        raise SystemExit(f"{label} does not resolve to a commit: {commit}")
    resolved = result.stdout.decode("utf-8").strip()
    if resolved != commit:
        raise SystemExit(f"{label} is not the exact requested commit: {commit}")
    return git_text("rev-parse", f"{commit}^{{tree}}")


def commit_file_bytes(commit: str, prefix: str, relative: str) -> bytes:
    result = git_bytes("show", f"{commit}:{prefix}{relative}")
    if result.returncode != 0:
        raise SystemExit(f"{relative} is absent from commit {commit}")
    return result.stdout


def commit_has_file(commit: str, prefix: str, relative: str) -> bool:
    return (
        git_bytes("cat-file", "-e", f"{commit}:{prefix}{relative}").returncode == 0
    )


def require_safe_relative(relative: object, label: str) -> str:
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise SystemExit(f"{label} has an unsafe path")
    return relative


def require_prefix_append(
    before: object, after: object, label: str
) -> tuple[list, object]:
    if not isinstance(before, list) or not isinstance(after, list):
        raise SystemExit(f"{label} must be lists")
    if len(after) != len(before) + 1 or after[:-1] != before:
        raise SystemExit(f"{label} must preserve the old prefix and append exactly one item")
    return before, after[-1]


def require_review_closure(
    reviewed_commit: str,
    baseline: str,
    frozen_files: list[str],
) -> dict[str, str]:
    reviewed_tree = require_commit(reviewed_commit, "reviewed candidate commit")
    baseline_tree = require_commit(baseline, "baseline commit")
    ancestor = git_bytes("merge-base", "--is-ancestor", reviewed_commit, baseline)
    if ancestor.returncode == 1:
        raise SystemExit("reviewed candidate commit is not an ancestor of baseline")
    if ancestor.returncode != 0:
        raise SystemExit("cannot prove reviewed candidate ancestry")

    prefix = git_text("rev-parse", "--show-prefix")
    reviewed_docs: dict[str, dict] = {}
    baseline_docs: dict[str, dict] = {}
    for relative in frozen_files:
        before = commit_file_bytes(reviewed_commit, prefix, relative)
        after = commit_file_bytes(baseline, prefix, relative)
        if Path(relative).suffix.lower() != ".json":
            if before != after:
                raise SystemExit(
                    f"closure changed non-JSON normative content: {relative}"
                )
            continue
        reviewed_docs[relative] = parse_json_object(
            before, f"{reviewed_commit}:{relative}"
        )
        baseline_docs[relative] = parse_json_object(
            after, f"{baseline}:{relative}"
        )

    for relative in frozen_files:
        if Path(relative).suffix.lower() != ".json" or relative in {
            RESEARCH_RELATIVE,
            ASSURANCE_RELATIVE,
        }:
            continue
        before = reviewed_docs[relative]
        after = baseline_docs[relative]
        expected_candidate_status = (
            "candidate_under_challenge"
            if relative == CONTRACT_RELATIVE
            else "candidate_for_freeze"
        )
        if before.get("status") != expected_candidate_status:
            raise SystemExit(
                f"reviewed candidate status is not eligible for closure: {relative}"
            )
        if after.get("status") != "frozen":
            raise SystemExit(f"baseline status is not frozen: {relative}")
        before_body = copy.deepcopy(before)
        after_body = copy.deepcopy(after)
        before_body.pop("status", None)
        after_body.pop("status", None)
        if before_body != after_body:
            raise SystemExit(f"closure changed non-status content: {relative}")

    research_before = reviewed_docs.get(RESEARCH_RELATIVE)
    research_after = baseline_docs.get(RESEARCH_RELATIVE)
    assurance_before = reviewed_docs.get(ASSURANCE_RELATIVE)
    assurance_after = baseline_docs.get(ASSURANCE_RELATIVE)
    if not all(
        isinstance(item, dict)
        for item in (
            research_before,
            research_after,
            assurance_before,
            assurance_after,
        )
    ):
        raise SystemExit("research and assurance must be JSON objects in frozen_files")

    if (
        research_before.get("status") != "under_independent_challenge"
        or research_after.get("status") != "adopted_with_explicit_limits"
    ):
        raise SystemExit("research status transition is not an allowed closure")
    challenge_before = research_before.get("challenge")
    challenge_after = research_after.get("challenge")
    stop_before = research_before.get("stop_rule")
    stop_after = research_after.get("stop_rule")
    if not all(
        isinstance(item, dict)
        for item in (challenge_before, challenge_after, stop_before, stop_after)
    ):
        raise SystemExit("research challenge and stop_rule must be objects")
    if (
        challenge_before.get("status") != "in_progress"
        or challenge_after.get("status") != "completed"
        or stop_before.get("met") is not False
        or stop_after.get("met") is not True
    ):
        raise SystemExit("research challenge/stop_rule transition is not allowed")

    _, final_round = require_prefix_append(
        challenge_before.get("rounds"),
        challenge_after.get("rounds"),
        "research challenge rounds",
    )
    _, final_artifact = require_prefix_append(
        research_before.get("primary_artifacts"),
        research_after.get("primary_artifacts"),
        "research primary_artifacts",
    )
    if not isinstance(final_round, dict) or not isinstance(final_artifact, dict):
        raise SystemExit("final review round and artifact must be objects")

    expected_research = copy.deepcopy(research_before)
    expected_research["status"] = "adopted_with_explicit_limits"
    expected_research["challenge"]["status"] = "completed"
    expected_research["challenge"]["rounds"].append(copy.deepcopy(final_round))
    expected_research["stop_rule"]["met"] = True
    expected_research["primary_artifacts"].append(copy.deepcopy(final_artifact))
    if expected_research != research_after:
        raise SystemExit("research closure changed fields outside the allowed metadata")

    evidence_path = require_safe_relative(
        final_round.get("evidence_path"), "final review evidence"
    )
    evidence_hash = final_round.get("evidence_sha256")
    if not isinstance(evidence_hash, str) or not re.fullmatch(
        r"[0-9a-f]{64}", evidence_hash
    ):
        raise SystemExit("final review evidence_sha256 is invalid")
    if commit_has_file(reviewed_commit, prefix, evidence_path):
        raise SystemExit("final review evidence already existed in reviewed candidate")
    evidence_bytes = commit_file_bytes(baseline, prefix, evidence_path)
    if sha256_bytes(evidence_bytes) != evidence_hash:
        raise SystemExit("final review evidence hash differs from baseline bytes")
    evidence = parse_json_object(evidence_bytes, evidence_path)
    review_input = evidence.get("review_input")
    if (
        not isinstance(review_input, str)
        or not review_input
        or evidence.get("review_input_sha256")
        != sha256_bytes(review_input.encode("utf-8"))
    ):
        raise SystemExit("final review input/hash binding is invalid")
    reviewed_scope = evidence.get("reviewed_files")
    if (
        not isinstance(reviewed_scope, list)
        or not all(isinstance(item, str) for item in reviewed_scope)
        or len(reviewed_scope) != len(set(reviewed_scope))
        or set(frozen_files) - set(reviewed_scope)
    ):
        raise SystemExit("final review evidence does not cover all frozen_files")

    subject_id = evidence.get("subject_id")
    evidence_expected = {
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "verdict": "passed_freeze",
        "open_critical_count": 0,
        "open_major_count": 0,
        "new_architecture_changing_classes": [],
        "participated_in_candidate_construction": False,
        "write_access_used": False,
    }
    for key, expected in evidence_expected.items():
        if evidence.get(key) != expected:
            raise SystemExit(f"final review evidence {key} does not bind candidate")
    if (
        evidence.get("schema_version") != 1
        or not isinstance(subject_id, str)
        or not subject_id
        or not isinstance(evidence.get("review_locator"), str)
        or not evidence.get("review_locator")
    ):
        raise SystemExit("final review evidence identity/provenance is incomplete")

    round_expected = {
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "reviewer_subjects": [subject_id],
        "result": "passed_freeze",
        "evidence_path": evidence_path,
        "evidence_sha256": evidence_hash,
        "open_critical_count": 0,
        "open_major_count": 0,
        "new_architecture_changing_classes": [],
    }
    for key, expected in round_expected.items():
        if final_round.get(key) != expected:
            raise SystemExit(f"final review round {key} does not match evidence")

    if (
        not isinstance(final_artifact.get("id"), str)
        or FINAL_ARTIFACT_ID.fullmatch(final_artifact["id"]) is None
        or final_artifact.get("role") != "independent_final_challenge"
        or final_artifact.get("path") != evidence_path
        or final_artifact.get("sha256") != evidence_hash
    ):
        raise SystemExit("final research artifact does not match final review evidence")

    if (
        assurance_before.get("status") != "candidate_for_freeze"
        or assurance_after.get("status") != "frozen"
    ):
        raise SystemExit("assurance status transition is not an allowed closure")
    _, final_subject = require_prefix_append(
        assurance_before.get("subjects"),
        assurance_after.get("subjects"),
        "assurance subjects",
    )
    if not isinstance(final_subject, dict):
        raise SystemExit("final reviewer subject must be an object")
    expected_assurance = copy.deepcopy(assurance_before)
    expected_assurance["status"] = "frozen"
    expected_assurance["subjects"].append(copy.deepcopy(final_subject))
    if expected_assurance != assurance_after:
        raise SystemExit("assurance closure changed fields outside the allowed metadata")
    subject_expected = {
        "id": subject_id,
        "role": "design_reviewer",
        "locator": evidence.get("review_locator"),
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "write_access_used": False,
        "participated_in_candidate_construction": False,
        "verdict": "passed_freeze",
        "evidence_path": evidence_path,
        "evidence_sha256": evidence_hash,
    }
    for key, expected in subject_expected.items():
        if final_subject.get(key) != expected:
            raise SystemExit(f"final reviewer subject {key} does not match evidence")

    diff = git_bytes(
        "diff", "--name-only", "-z", reviewed_commit, baseline, "--", "."
    )
    if diff.returncode != 0:
        raise SystemExit("cannot enumerate reviewed-candidate closure paths")
    repo_paths = {
        item.decode("utf-8")
        for item in diff.stdout.split(b"\0")
        if item
    }
    expected_paths = {
        f"{prefix}{relative}"
        for relative in frozen_files
        if Path(relative).suffix.lower() == ".json"
    }
    expected_paths.add(f"{prefix}{evidence_path}")
    if repo_paths != expected_paths:
        raise SystemExit(
            "closure changed paths outside the allowed metadata set: "
            f"missing={sorted(expected_paths - repo_paths)}, "
            f"extra={sorted(repo_paths - expected_paths)}"
        )

    return {
        "reviewed_candidate_tree": reviewed_tree,
        "baseline_tree": baseline_tree,
        "review_subject_id": subject_id,
        "review_evidence_path": evidence_path,
        "review_evidence_sha256": evidence_hash,
    }


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


def require_frozen_statuses(frozen_files: list[str]) -> dict:
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
    return contract


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
    parser.add_argument("--reviewed-candidate-commit", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--branch")
    args = parser.parse_args()
    baseline = args.baseline_commit
    reviewed_commit = args.reviewed_candidate_commit
    if not re.fullmatch(r"[0-9a-f]{40}", baseline):
        raise SystemExit("--baseline-commit must be a full 40-character commit")
    if not re.fullmatch(r"[0-9a-f]{40}", reviewed_commit):
        raise SystemExit(
            "--reviewed-candidate-commit must be a full 40-character commit"
        )

    require_candidate_governance()
    if BUNDLE.exists():
        raise SystemExit(f"refusing to overwrite existing {BUNDLE.name}")

    candidate_contract = load_json_object(
        CONTRACT, "governance/ACCEPTANCE_CONTRACT_V1.json"
    )
    frozen_files = frozen_file_paths(candidate_contract)
    contract = require_frozen_statuses(frozen_files)

    require_clean_exact_baseline(baseline)
    closure_facts = require_review_closure(
        reviewed_commit,
        baseline,
        frozen_files,
    )
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
        "reviewed_candidate_commit": reviewed_commit,
        "reviewed_candidate_tree": closure_facts["reviewed_candidate_tree"],
        "baseline_commit": baseline,
        "baseline_tree": closure_facts["baseline_tree"],
        "final_review_subject_id": closure_facts["review_subject_id"],
        "final_review_evidence_path": closure_facts["review_evidence_path"],
        "final_review_evidence_sha256": closure_facts["review_evidence_sha256"],
        "upstream_ref_at_creation": remote_facts.get("ref"),
        "remote_at_creation": remote_facts.get("remote"),
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "creation_rule": (
            "non-circular two-stage: an independent review binds candidate C; "
            "baseline B may add only structurally verified review-closure metadata, "
            "must be clean and directly observed on the remote; this bundle must "
            "then be committed and pushed"
        ),
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
