#!/usr/bin/env python3
"""Create the non-circular second-stage governance frozen bundle."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
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
GROUND_TRUTH_RELATIVE = "governance/GROUND_TRUTH_MANIFEST_V1.json"
IMPLEMENTATION_TARGETS_RELATIVE = "governance/IMPLEMENTATION_TARGETS_V1.json"
RESEARCH_SUFFICIENCY_RELATIVE = "governance/RESEARCH_SUFFICIENCY_V1.json"
ATTACK_RUNNER = SCRIPT_DIR / "run_design_freeze_attack.py"
FINAL_ARTIFACT_ID = re.compile(r"ARTIFACT-CHALLENGE-FINAL-R[0-9]+")
TRUSTED_REMOTE_FIELDS = {
    "name",
    "fetch_url",
    "branch",
    "project_prefix",
}
CANONICAL_ATTACK_IDS = (
    "ATTACK-PIT-ORACLE-INVERSION",
    "ATTACK-SAME-BAR-CAUSALITY-SMUGGLE",
    "ATTACK-SPLIT-ACCOUNTING-SMUGGLE",
    "ATTACK-CONDITIONAL-SELF-ATTESTATION",
)
RUNNER_ID = "ids-design-freeze-attack-runner-v1"
RUNNER_FINGERPRINT_FIELDS = (
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


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


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


def runner_fingerprint(receipt: dict) -> str:
    payload = {
        key: receipt.get(key)
        for key in RUNNER_FINGERPRINT_FIELDS
    }
    return sha256_bytes(canonical_json_bytes(payload))


def parse_runner_receipt(
    completed: subprocess.CompletedProcess[str],
    *,
    candidate_commit: str,
    candidate_tree: str,
    project_prefix: str,
    mode: str,
    probe_id: str,
    label: str,
) -> tuple[dict, bytes]:
    raw = completed.stdout.encode("utf-8")
    receipt = parse_json_object(raw, label)
    baseline = receipt.get("baseline")
    target = receipt.get("target")
    expected = {
        "schema_version": 2,
        "runner_id": RUNNER_ID,
        "runner_sha256": sha256_bytes(ATTACK_RUNNER.read_bytes()),
        "candidate_commit": candidate_commit,
        "candidate_tree": candidate_tree,
        "project_prefix": project_prefix,
        "mode": mode,
        "probe_id": probe_id,
        "result": "rejected",
        "runner_exit_code": 0,
    }
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise SystemExit(f"{label} {key} does not bind the candidate")
    if completed.returncode != receipt["runner_exit_code"]:
        raise SystemExit(f"{label} process/declared exit binding differs")
    for phase, record, expected_zero in (
        ("baseline", baseline, True),
        ("target", target, False),
    ):
        if not isinstance(record, dict) or set(record) != {
            "argv",
            "exit_code",
            "stdout",
            "stdout_sha256",
        }:
            raise SystemExit(f"{label} {phase} execution record differs")
        stdout = record.get("stdout")
        exit_code = record.get("exit_code")
        if (
            record.get("argv")
            != ["PYTHON", "scripts/verify_governance.py", "--allow-candidate"]
            or type(exit_code) is not int
            or not isinstance(stdout, str)
            or record.get("stdout_sha256")
            != sha256_bytes(stdout.encode("utf-8"))
            or (expected_zero and exit_code != 0)
            or (not expected_zero and exit_code == 0)
        ):
            raise SystemExit(f"{label} {phase} actual execution binding differs")
    expected_signal = receipt.get("expected_rejection_substring")
    if (
        not isinstance(expected_signal, str)
        or not expected_signal
        or expected_signal not in target["stdout"]
    ):
        raise SystemExit(f"{label} target rejection signal differs")
    fingerprint = receipt.get("execution_fingerprint")
    if (
        not isinstance(fingerprint, str)
        or re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None
        or fingerprint != runner_fingerprint(receipt)
    ):
        raise SystemExit(f"{label} execution fingerprint differs")
    return receipt, raw


def execute_runner(
    *,
    candidate_commit: str,
    candidate_tree: str,
    project_prefix: str,
    mode: str,
    probe_id: str,
    novelty_spec: Path | None = None,
    label: str,
) -> tuple[dict, bytes]:
    arguments = ["--candidate-commit", candidate_commit]
    if mode == "canonical":
        arguments.extend(["--attack-id", probe_id])
    elif mode == "novelty" and novelty_spec is not None:
        arguments.extend(["--novelty-spec", str(novelty_spec)])
    else:
        raise SystemExit(f"{label} has no executable mutation")
    completed = run_python(ATTACK_RUNNER, *arguments)
    return parse_runner_receipt(
        completed,
        candidate_commit=candidate_commit,
        candidate_tree=candidate_tree,
        project_prefix=project_prefix,
        mode=mode,
        probe_id=probe_id,
        label=label,
    )


def require_candidate_governance(reviewed_commit: str) -> None:
    candidate_tree = require_commit(reviewed_commit, "reviewed candidate commit")
    project_prefix = git_text("rev-parse", "--show-prefix")
    try:
        execute_runner(
            candidate_commit=reviewed_commit,
            candidate_tree=candidate_tree,
            project_prefix=project_prefix,
            mode="canonical",
            probe_id=CANONICAL_ATTACK_IDS[0],
            label="candidate governance probe",
        )
    except SystemExit as exc:
        raise SystemExit(
            f"candidate governance verification failed:\n{exc}"
        ) from None


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


def commit_tree_entry(commit: str, prefix: str, relative: str) -> dict[str, str]:
    repo_relative = f"{prefix}{relative}"
    result = git_bytes(
        "ls-tree",
        "--full-name",
        "-z",
        commit,
        "--",
        f":(top,literal){repo_relative}",
    )
    if result.returncode != 0 or not result.stdout:
        raise SystemExit(f"cannot resolve Git tree entry for {commit}:{relative}")
    records = [item for item in result.stdout.split(b"\0") if item]
    if len(records) != 1 or b"\t" not in records[0]:
        raise SystemExit(f"ambiguous Git tree entry for {commit}:{relative}")
    metadata, observed_path = records[0].split(b"\t", 1)
    fields = metadata.decode("ascii").split()
    if len(fields) != 3 or observed_path.decode("utf-8") != repo_relative:
        raise SystemExit(f"invalid Git tree entry for {commit}:{relative}")
    mode, tree_type, object_id = fields
    kind = git_text("cat-file", "-t", object_id)
    if tree_type != "blob" or kind != "blob":
        raise SystemExit(
            f"frozen file is not a Git blob: {relative} "
            f"(tree_type={tree_type}, object_kind={kind})"
        )
    return {
        "mode": mode,
        "tree_type": tree_type,
        "object_id": object_id,
        "object_kind": kind,
    }


def parse_raw_diff(
    reviewed_commit: str,
    baseline: str,
) -> dict[str, dict[str, str]]:
    result = git_bytes(
        "diff",
        "--raw",
        "--no-renames",
        "-z",
        reviewed_commit,
        baseline,
        "--",
        ".",
    )
    if result.returncode != 0:
        raise SystemExit("cannot enumerate raw reviewed-candidate closure delta")
    tokens = [item for item in result.stdout.split(b"\0") if item]
    entries: dict[str, dict[str, str]] = {}
    index = 0
    while index < len(tokens):
        header = tokens[index]
        index += 1
        if b"\t" in header:
            metadata, path_bytes = header.split(b"\t", 1)
        else:
            metadata = header
            if index >= len(tokens):
                raise SystemExit("raw closure delta has a pathless entry")
            path_bytes = tokens[index]
            index += 1
        fields = metadata.decode("ascii").removeprefix(":").split()
        if len(fields) != 5:
            raise SystemExit("raw closure delta entry has invalid metadata")
        old_mode, new_mode, old_object, new_object, status = fields
        if status not in {"A", "D", "M", "T"}:
            raise SystemExit(f"raw closure delta has unsupported status: {status}")
        path = path_bytes.decode("utf-8")
        if path in entries:
            raise SystemExit(f"raw closure delta repeats path: {path}")
        entries[path] = {
            "status": status,
            "old_mode": old_mode,
            "new_mode": new_mode,
            "old_object": old_object,
            "new_object": new_object,
        }
    return entries


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


def commit_repo_file_bytes(commit: str, repo_relative: str) -> bytes:
    result = git_bytes("show", f"{commit}:{repo_relative}")
    if result.returncode != 0:
        raise SystemExit(f"{repo_relative} is absent from commit {commit}")
    return result.stdout


def require_sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise SystemExit(f"{label} sha256 is invalid")
    return value


def require_added_artifact(
    *,
    reviewed_commit: str,
    baseline: str,
    prefix: str,
    relative_value: object,
    expected_hash_value: object,
    label: str,
) -> dict[str, str]:
    relative = require_safe_relative(relative_value, label)
    expected_hash = require_sha256(expected_hash_value, label)
    if commit_has_file(reviewed_commit, prefix, relative):
        raise SystemExit(f"{label} existed in the reviewed candidate")
    entry = commit_tree_entry(baseline, prefix, relative)
    if (
        entry["mode"] != "100644"
        or entry["tree_type"] != "blob"
        or entry["object_kind"] != "blob"
    ):
        raise SystemExit(f"{label} must be a non-executable regular Git blob")
    payload = commit_file_bytes(baseline, prefix, relative)
    if sha256_bytes(payload) != expected_hash:
        raise SystemExit(f"{label} sha256 differs from baseline bytes")
    return {
        "path": relative,
        "sha256": expected_hash,
        "git_mode": entry["mode"],
        "git_type": entry["tree_type"],
        "git_object_kind": entry["object_kind"],
        "git_blob": entry["object_id"],
    }


def load_production_verifier():
    spec = importlib.util.spec_from_file_location(
        "ids_freeze_schema_v2_verifier",
        CANDIDATE_VERIFIER,
    )
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load production governance verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_schema_v2_review(
    evidence: dict,
    *,
    final_round: dict,
    reviewed_commit: str,
    reviewed_tree: str,
    frozen_files: list[str],
    implementation_targets: dict,
) -> None:
    round_id = final_round.get("id")
    reviewers = final_round.get("reviewer_subjects")
    if not isinstance(round_id, str) or not round_id:
        raise SystemExit("final review round id is missing")
    verifier = load_production_verifier()
    errors: list[str] = []
    verifier.verify_final_review_evidence(
        evidence,
        round_id=round_id,
        reviewers=reviewers,
        candidate_commit=reviewed_commit,
        candidate_tree=reviewed_tree,
        frozen_files=frozen_files,
        implementation_targets=implementation_targets,
        errors=errors,
    )
    if errors:
        raise SystemExit(
            "final review schema v2 verification failed:\n- "
            + "\n- ".join(errors)
        )


def require_candidate_ground_truth(
    *,
    reviewed_commit: str,
    baseline: str,
    prefix: str,
    reviewed_document: dict,
    baseline_document: dict,
) -> dict[str, str]:
    if (
        reviewed_document.get("status") != "candidate_for_freeze"
        or baseline_document.get("status") != "frozen"
    ):
        raise SystemExit("ground-truth lifecycle transition differs")
    candidate_body = copy.deepcopy(reviewed_document)
    baseline_body = copy.deepcopy(baseline_document)
    candidate_body.pop("status", None)
    baseline_body.pop("status", None)
    if candidate_body != baseline_body:
        raise SystemExit(
            "ground-truth closure may change only its lifecycle status"
        )
    artifacts = reviewed_document.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise SystemExit("candidate ground-truth artifacts must be nonempty")
    observed: set[tuple[str, str]] = set()
    for index, artifact in enumerate(artifacts):
        label = f"candidate ground-truth artifacts[{index}]"
        if not isinstance(artifact, dict):
            raise SystemExit(f"{label} must be an object")
        relative = require_safe_relative(artifact.get("path"), label)
        scope = artifact.get("scope", "project")
        identity = (str(scope), relative)
        if scope not in {"project", "repository"} or identity in observed:
            raise SystemExit(f"{label} scope/path is invalid or duplicate")
        observed.add(identity)
        expected_hash = require_sha256(artifact.get("sha256"), label)
        payload = (
            commit_file_bytes(reviewed_commit, prefix, relative)
            if scope == "project"
            else commit_repo_file_bytes(reviewed_commit, relative)
        )
        if sha256_bytes(payload) != expected_hash:
            raise SystemExit(
                f"candidate ground-truth hash differs for {scope}:{relative}"
            )
    candidate_bytes = commit_file_bytes(
        reviewed_commit,
        prefix,
        GROUND_TRUTH_RELATIVE,
    )
    baseline_bytes = commit_file_bytes(
        baseline,
        prefix,
        GROUND_TRUTH_RELATIVE,
    )
    return {
        "candidate_sha256": sha256_bytes(candidate_bytes),
        "baseline_sha256": sha256_bytes(baseline_bytes),
    }


def github_repository_from_url(fetch_url: str) -> str | None:
    match = re.fullmatch(
        r"(?:git@github\.com:|https://github\.com/)"
        r"(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\.git",
        fetch_url,
    )
    return match.group("repository") if match else None


def require_machine_and_attestation(
    *,
    machine_manifest: dict,
    attestation: dict,
    machine_path: str,
    machine_hash: str,
    reviewed_commit: str,
    reviewed_tree: str,
    trusted: dict[str, str],
) -> None:
    repository = github_repository_from_url(trusted["fetch_url"])
    if repository is None:
        repository = machine_manifest.get("repository")
    machine_expected = {
        "schema_version": 1,
        "manifest_id": "ids-github-machine-assurance-v1",
        "status": "pass",
        "assurance_level": "github_issued_workflow_provenance",
        "semantic_approval": False,
        "repository": repository,
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "project_prefix": trusted["project_prefix"],
        "workflow_sha": reviewed_commit,
        "github_sha_matches_candidate": True,
        "runner_environment": "github-hosted",
    }
    for key, expected in machine_expected.items():
        if machine_manifest.get(key) != expected:
            raise SystemExit(f"machine-assurance manifest {key} differs")
    workflow_ref = machine_manifest.get("workflow_ref")
    expected_workflow_suffix = (
        "/.github/workflows/investment-discipline-assurance.yml"
        f"@refs/heads/{trusted['branch']}"
    )
    if (
        not isinstance(workflow_ref, str)
        or not workflow_ref.endswith(expected_workflow_suffix)
    ):
        raise SystemExit("machine-assurance manifest workflow_ref differs")
    required_check_ids = machine_manifest.get("required_check_ids")
    checks = machine_manifest.get("checks")
    if (
        not isinstance(required_check_ids, list)
        or not required_check_ids
        or not all(isinstance(item, str) and item for item in required_check_ids)
        or len(required_check_ids) != len(set(required_check_ids))
        or not isinstance(checks, list)
    ):
        raise SystemExit("machine-assurance manifest check catalog differs")
    check_by_id: dict[str, dict] = {}
    for check in checks:
        check_id = check.get("check_id") if isinstance(check, dict) else None
        if (
            not isinstance(check_id, str)
            or check_id in check_by_id
            or check.get("result") != "pass"
            or (
                "actual_process_exit" in check
                and check.get("actual_process_exit") != 0
            )
        ):
            raise SystemExit("machine-assurance manifest check result differs")
        check_by_id[check_id] = check
    if set(check_by_id) != set(required_check_ids):
        raise SystemExit("machine-assurance manifest required checks differ")

    attestation_expected = {
        "schema_version": 1,
        "status": "pass",
        "fixture_only": False,
        "repository": repository,
        "workflow_path": (
            ".github/workflows/investment-discipline-assurance.yml"
        ),
        "source_ref": f"refs/heads/{trusted['branch']}",
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "project_prefix": trusted["project_prefix"],
        "subject": {
            "path": machine_path,
            "sha256": machine_hash,
        },
    }
    for key, expected in attestation_expected.items():
        if attestation.get(key) != expected:
            raise SystemExit(f"machine-attestation verification {key} differs")
    if (
        not isinstance(attestation.get("verification_id"), str)
        or not attestation["verification_id"]
        or attestation.get("policy_checks")
        != {
            "repository_matches": True,
            "workflow_matches": True,
            "source_commit_matches": True,
            "source_ref_matches": True,
            "hosted_runner_required": True,
            "subject_digest_matches": True,
        }
    ):
        raise SystemExit("machine-attestation verification policy binding differs")


def require_review_closure(
    reviewed_commit: str,
    baseline: str,
    frozen_files: list[str],
    trusted: dict[str, str] | None = None,
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
    reviewed_entries: dict[str, dict[str, str]] = {}
    baseline_entries: dict[str, dict[str, str]] = {}
    for relative in frozen_files:
        before_entry = commit_tree_entry(reviewed_commit, prefix, relative)
        after_entry = commit_tree_entry(baseline, prefix, relative)
        reviewed_entries[relative] = before_entry
        baseline_entries[relative] = after_entry
        for field in ("mode", "tree_type", "object_kind"):
            if before_entry[field] != after_entry[field]:
                raise SystemExit(
                    f"closure changed Git mode/type for frozen file: {relative} "
                    f"({field}: {before_entry[field]} -> {after_entry[field]})"
                )
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
    evidence_entry = commit_tree_entry(baseline, prefix, evidence_path)
    if evidence_entry["mode"] != "100644":
        raise SystemExit("final review evidence must be a non-executable regular blob")
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
        "open_minor_count": 0,
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
    finding_ids = evidence.get("finding_ids")
    findings = evidence.get("findings")
    if (
        not isinstance(finding_ids, list)
        or not all(isinstance(item, str) and item for item in finding_ids)
        or len(finding_ids) != len(set(finding_ids))
        or not isinstance(findings, list)
        or not all(isinstance(item, dict) for item in findings)
    ):
        raise SystemExit("final review findings are not machine-verifiable")
    observed_finding_ids: list[str] = []
    open_counts = {"critical": 0, "major": 0, "minor": 0}
    for finding in findings:
        finding_id = finding.get("id")
        severity = finding.get("severity")
        status = finding.get("status")
        if (
            not isinstance(finding_id, str)
            or not finding_id
            or finding_id in observed_finding_ids
            or not isinstance(severity, str)
            or not isinstance(status, str)
        ):
            raise SystemExit("final review finding identity is invalid or duplicate")
        observed_finding_ids.append(finding_id)
        if status == "open":
            if severity not in open_counts:
                raise SystemExit(
                    f"final review finding has unsupported open severity: {finding_id}"
                )
            open_counts[severity] += 1
    if finding_ids != observed_finding_ids:
        raise SystemExit("final review finding_ids do not exactly match findings")
    for severity, count in open_counts.items():
        if evidence.get(f"open_{severity}_count") != count:
            raise SystemExit(
                f"final review open_{severity}_count does not match findings"
            )

    commands_run = evidence.get("commands_run")
    if (
        not isinstance(commands_run, list)
        or not commands_run
        or not all(isinstance(item, str) and item.strip() for item in commands_run)
        or len(commands_run) != len(set(commands_run))
    ):
        raise SystemExit("final review commands_run must be nonempty unique strings")
    for field in ("what_would_falsify_pass", "limitations"):
        values = evidence.get(field)
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(item, str) and item for item in values)
        ):
            raise SystemExit(f"final review {field} must be nonempty strings")

    attacks = evidence.get("independent_attacks")
    if not isinstance(attacks, list) or len(attacks) < 3:
        raise SystemExit("final review requires at least three independent attacks")
    attack_ids: set[str] = set()
    replay_selectors: set[str] = set()
    raw_result_paths: set[str] = set()
    for attack in attacks:
        if not isinstance(attack, dict):
            raise SystemExit("final review independent attack must be an object")
        attack_id = attack.get("attack_id")
        mutation = attack.get("mutation")
        replay_selector = attack.get("replay_selector")
        if (
            not isinstance(attack_id, str)
            or not attack_id
            or attack_id in attack_ids
        ):
            raise SystemExit("final review independent attack_id is invalid or duplicate")
        attack_ids.add(attack_id)
        if (
            not isinstance(mutation, str)
            or not mutation
            or not isinstance(attack.get("expected"), str)
            or not attack["expected"]
            or not isinstance(attack.get("observed"), str)
            or not attack["observed"]
            or attack.get("mutation_sha256")
            != sha256_bytes(mutation.encode("utf-8"))
            or attack.get("result") != "rejected"
        ):
            raise SystemExit(f"final review attack is not a bound rejection: {attack_id}")
        if (
            not isinstance(replay_selector, str)
            or not replay_selector
            or replay_selector in replay_selectors
        ):
            raise SystemExit(
                f"final review attack replay_selector is invalid or duplicate: "
                f"{attack_id}"
            )
        replay_selectors.add(replay_selector)
        raw_path = require_safe_relative(
            attack.get("raw_result_path"),
            f"final review attack {attack_id} raw result",
        )
        raw_hash = attack.get("raw_result_sha256")
        if (
            raw_path == evidence_path
            or raw_path in raw_result_paths
            or not isinstance(raw_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", raw_hash)
        ):
            raise SystemExit(f"final review attack raw result is invalid: {attack_id}")
        raw_result_paths.add(raw_path)
        if commit_has_file(reviewed_commit, prefix, raw_path):
            raise SystemExit(
                f"final review attack raw result existed in candidate: {attack_id}"
            )
        raw_entry = commit_tree_entry(baseline, prefix, raw_path)
        if raw_entry["mode"] != "100644":
            raise SystemExit(
                f"final review attack raw result must be regular blob: {attack_id}"
            )
        raw_bytes = commit_file_bytes(baseline, prefix, raw_path)
        if sha256_bytes(raw_bytes) != raw_hash:
            raise SystemExit(
                f"final review attack raw result hash differs: {attack_id}"
            )
        raw_result = parse_json_object(raw_bytes, raw_path)
        expected_raw = {
            "attack_id": attack_id,
            "candidate_commit": reviewed_commit,
            "candidate_tree": reviewed_tree,
            "result": "rejected",
            "mutation_sha256": attack.get("mutation_sha256"),
            "replay_selector": replay_selector,
            "expected": attack.get("expected"),
            "observed": attack.get("observed"),
        }
        for key, expected in expected_raw.items():
            if raw_result.get(key) != expected:
                raise SystemExit(
                    f"final review attack raw result {key} differs: {attack_id}"
                )
        if (
            type(raw_result.get("exit_code")) is not int
            or raw_result["exit_code"] == 0
        ):
            raise SystemExit(
                f"final review attack raw result exit_code is not rejecting: {attack_id}"
            )
        raw_command = raw_result.get("command")
        stdout_hash = raw_result.get("stdout_sha256")
        if (
            not isinstance(raw_command, str)
            or not raw_command
            or raw_command not in commands_run
            or not isinstance(stdout_hash, str)
            or not re.fullmatch(r"[0-9a-f]{64}", stdout_hash)
        ):
            raise SystemExit(
                f"final review attack raw command/stdout binding is invalid: "
                f"{attack_id}"
            )
        if "stdout" in raw_result and (
            not isinstance(raw_result["stdout"], str)
            or sha256_bytes(raw_result["stdout"].encode("utf-8")) != stdout_hash
        ):
            raise SystemExit(
                f"final review attack raw stdout hash differs: {attack_id}"
            )

    round_expected = {
        "candidate_commit": reviewed_commit,
        "candidate_tree": reviewed_tree,
        "reviewer_subjects": [subject_id],
        "result": "passed_freeze",
        "evidence_path": evidence_path,
        "evidence_sha256": evidence_hash,
        "open_critical_count": 0,
        "open_major_count": 0,
        "open_minor_count": 0,
        "finding_ids": [],
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

    raw_entries = parse_raw_diff(reviewed_commit, baseline)
    repo_paths = set(raw_entries)
    expected_paths = {
        f"{prefix}{relative}"
        for relative in frozen_files
        if Path(relative).suffix.lower() == ".json"
    }
    expected_paths.add(f"{prefix}{evidence_path}")
    expected_paths.update(f"{prefix}{path}" for path in raw_result_paths)
    if repo_paths != expected_paths:
        raise SystemExit(
            "closure changed paths outside the allowed metadata set: "
            f"missing={sorted(expected_paths - repo_paths)}, "
            f"extra={sorted(repo_paths - expected_paths)}"
        )
    evidence_repo_path = f"{prefix}{evidence_path}"
    for repo_path, raw_entry in raw_entries.items():
        if repo_path == evidence_repo_path or repo_path in {
            f"{prefix}{path}" for path in raw_result_paths
        }:
            if (
                raw_entry["status"] != "A"
                or raw_entry["old_mode"] != "000000"
                or raw_entry["new_mode"] != "100644"
            ):
                raise SystemExit(
                    "final review evidence/raw-result Git delta is not a clean add"
                )
            continue
        relative = repo_path.removeprefix(prefix)
        if raw_entry["status"] != "M":
            raise SystemExit(
                f"closure used non-modify Git delta for frozen file: {relative}"
            )
        before_entry = reviewed_entries[relative]
        after_entry = baseline_entries[relative]
        if (
            raw_entry["old_mode"] != before_entry["mode"]
            or raw_entry["new_mode"] != after_entry["mode"]
            or raw_entry["old_mode"] != raw_entry["new_mode"]
        ):
            raise SystemExit(
                f"closure raw delta changed Git mode/type for frozen file: {relative}"
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


def trusted_git_remote(contract: dict) -> dict[str, str]:
    change_control = contract.get("change_control")
    trusted = (
        change_control.get("trusted_git_remote")
        if isinstance(change_control, dict)
        else None
    )
    if not isinstance(trusted, dict) or set(trusted) != TRUSTED_REMOTE_FIELDS:
        raise SystemExit(
            "contract change_control.trusted_git_remote must contain exactly "
            "name, fetch_url, branch, project_prefix"
        )
    values: dict[str, str] = {}
    for field in sorted(TRUSTED_REMOTE_FIELDS):
        value = trusted.get(field)
        if not isinstance(value, str):
            raise SystemExit(f"trusted_git_remote.{field} must be a string")
        values[field] = value
    name = values["name"]
    if (
        not name
        or name.startswith("-")
        or name.endswith("/")
        or ".." in name
        or "@{" in name
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", name) is None
    ):
        raise SystemExit(f"trusted_git_remote.name is invalid: {name!r}")
    fetch_url = values["fetch_url"]
    if (
        not fetch_url
        or fetch_url.startswith("-")
        or "\n" in fetch_url
        or "\r" in fetch_url
    ):
        raise SystemExit(
            "trusted_git_remote.fetch_url must be one safe nonempty line"
        )
    branch = values["branch"]
    branch_check = git_bytes("check-ref-format", "--branch", branch)
    if not branch or branch_check.returncode != 0:
        raise SystemExit(f"trusted_git_remote.branch is invalid: {branch!r}")
    prefix = values["project_prefix"]
    if (
        prefix.startswith("/")
        or "\\" in prefix
        or (prefix and not prefix.endswith("/"))
        or ".." in Path(prefix).parts
        or "." in Path(prefix).parts
    ):
        raise SystemExit(
            f"trusted_git_remote.project_prefix is invalid: {prefix!r}"
        )
    return values


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
    baseline: str,
    trusted: dict[str, str],
) -> dict[str, str]:
    command = [
        "--commit",
        baseline,
        "--remote",
        trusted["name"],
        "--branch",
        trusted["branch"],
        "--json",
    ]
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
    observation = facts.get("remote_observation") if isinstance(facts, dict) else None
    if (
        payload.get("verification_scope") != "direct_remote_observation"
        or not isinstance(facts, dict)
        or facts.get("verification_scope") != "direct_remote_observation"
        or facts.get("full_remote_verification") is not False
        or facts.get("trusted_git_remote") != trusted
        or facts.get("project_prefix") != trusted["project_prefix"]
        or facts.get("current_branch") != trusted["branch"]
        or facts.get("upstream")
        != f"{trusted['name']}/{trusted['branch']}"
        or facts.get("configured_fetch_urls") != [trusted["fetch_url"]]
        or not isinstance(observation, dict)
        or observation.get("remote") != trusted["name"]
        or observation.get("fetch_url") != trusted["fetch_url"]
        or observation.get("commit") != baseline
        or observation.get("ref") != f"refs/heads/{trusted['branch']}"
        or observation.get("observation_kind") != "non_atomic_ls_remote"
        or not isinstance(observation.get("observed_at"), str)
        or not observation["observed_at"]
    ):
        raise SystemExit("direct remote verifier did not bind the requested baseline")
    return observation


def require_design_freeze_attack_replay(
    baseline: str,
    baseline_tree: str,
) -> dict[str, object]:
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    env = os.environ.copy()
    env["IDS_PROJECT_ROOT"] = str(PROJECT_ROOT)
    results: list[dict[str, object]] = []
    outputs: dict[str, bytes] = {}
    transcript = bytearray()
    for attack_id, selector in CANONICAL_ATTACK_SELECTORS.items():
        command = [sys.executable, "-m", "unittest", selector, "-v"]
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )
        output = completed.stdout
        outputs[attack_id] = output
        result_name = (
            "rejected" if completed.returncode == 0 else "escaped_or_error"
        )
        results.append(
            {
                "attack_id": attack_id,
                "selector": selector,
                "exit_code": completed.returncode,
                "output_sha256": sha256_bytes(output),
                "result": result_name,
            }
        )
        header = json.dumps(
            {
                "attack_id": attack_id,
                "selector": selector,
                "exit_code": completed.returncode,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        transcript.extend(len(header).to_bytes(8, "big"))
        transcript.extend(header)
        transcript.extend(len(output).to_bytes(8, "big"))
        transcript.extend(output)

    passed = all(
        item["result"] == "rejected" and item["exit_code"] == 0
        for item in results
    )
    payload = {
        "schema_version": 1,
        "status": "pass" if passed else "fail",
        "candidate_commit": baseline,
        "candidate_tree": baseline_tree,
        "required_attack_ids": list(CANONICAL_ATTACK_SELECTORS),
        "started_at": started_at,
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": results,
        "stdout_sha256": sha256_bytes(bytes(transcript)),
    }
    if not passed:
        failed_details = []
        for item in results:
            if item["exit_code"] == 0:
                continue
            attack_id = str(item["attack_id"])
            output = outputs[attack_id].decode("utf-8", "replace").strip()
            failed_details.append(
                f"{attack_id} exit={item['exit_code']}:\n"
                f"{output or '<no output>'}"
            )
        raise SystemExit(
            "design-freeze canonical attack replay failed:\n"
            + "\n".join(failed_details)
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-commit", required=True)
    parser.add_argument("--reviewed-candidate-commit", required=True)
    parser.add_argument("--remote")
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
    trusted = trusted_git_remote(contract)
    if args.remote is not None and args.remote != trusted["name"]:
        raise SystemExit(
            "--remote must match contract trusted remote "
            f"{trusted['name']!r}: got {args.remote!r}"
        )
    if args.branch is not None and args.branch != trusted["branch"]:
        raise SystemExit(
            "--branch must match contract trusted branch "
            f"{trusted['branch']!r}: got {args.branch!r}"
        )

    require_clean_exact_baseline(baseline)
    prefix = git_text("rev-parse", "--show-prefix")
    if prefix != trusted["project_prefix"]:
        raise SystemExit(
            "project prefix does not match contract: "
            f"expected {trusted['project_prefix']!r}, got {prefix!r}"
        )
    observation_before = require_direct_remote(baseline, trusted)
    closure_facts = require_review_closure(
        reviewed_commit,
        baseline,
        frozen_files,
    )
    attack_replay = require_design_freeze_attack_replay(
        baseline,
        closure_facts["baseline_tree"],
    )
    require_clean_exact_baseline(baseline)

    entries: list[dict[str, str]] = []
    for relative in frozen_files:
        repo_relative = f"{prefix}{relative}"
        content = git_bytes("show", f"{baseline}:{repo_relative}")
        if content.returncode != 0:
            raise SystemExit(f"frozen file is not tracked at baseline: {relative}")
        current = (PROJECT_ROOT / relative).read_bytes()
        if current != content.stdout:
            raise SystemExit(f"working file differs from baseline: {relative}")
        tree_entry = commit_tree_entry(baseline, prefix, relative)
        entries.append(
            {
                "path": relative,
                "sha256": sha256_bytes(current),
                "git_mode": tree_entry["mode"],
                "git_type": tree_entry["tree_type"],
                "git_object_kind": tree_entry["object_kind"],
                "git_blob": tree_entry["object_id"],
            }
        )
    require_clean_exact_baseline(baseline)
    observation_after = require_direct_remote(baseline, trusted)
    require_clean_exact_baseline(baseline)

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
        "design_freeze_attack_replay": attack_replay,
        "trusted_git_remote": trusted,
        "baseline_remote_observations": [
            {
                "phase": "before_baseline_verification",
                **observation_before,
            },
            {
                "phase": "after_baseline_verification",
                **observation_after,
            },
        ],
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "creation_rule": (
            "non-circular two-stage: an independent review binds candidate C; "
            "baseline B may add only structurally verified review-closure metadata, "
            "must be clean and directly observed on the contract-declared trusted "
            "remote before and after baseline verification; observations are "
            "non-atomic and this bundle must then be committed, pushed, and "
            "independently verified"
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
