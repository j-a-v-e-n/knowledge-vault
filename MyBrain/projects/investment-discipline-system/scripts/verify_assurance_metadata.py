#!/usr/bin/env python3
"""Fail-closed verification for design-freeze assurance metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
PROJECT_DOCUMENT_STATUSES = {"candidate_for_freeze", "frozen"}
WORKFLOW_PATH = ".github/workflows/investment-discipline-assurance.yml"
EXPECTED_WORKFLOW_PERMISSIONS = {
    "contents": "read",
    "id-token": "write",
    "attestations": "write",
    "artifact-metadata": "write",
}
FAILURE_REFERENCE_FIELDS = (
    "requirement_ids",
    "control_ids",
    "verification_ids",
    "acceptance_case_ids",
)
AUTHORITY_STATUS_PAIRS = {
    "human_delegated_reversible": {
        "conditional_candidate_not_human_confirmed",
        "delegated_candidate_v1_not_human_confirmed",
    },
    "human_explicit": {"confirmed_active"},
    "human_only_required": {"unset_human_only_blocking"},
    "technical_derived": {
        "claim_blocked_no_threshold",
        "derived_candidate_v1_not_human_confirmed",
    },
}
EXPECTED_RELEASE_REQUIREMENTS = [
    "local frozen runner replay passes against the exact reviewed candidate",
    (
        "GitHub-issued workflow provenance for the assurance manifest is "
        "observed and verifies against exact repository/workflow/source "
        "commit and policy"
    ),
    "post-candidate Codex semantic review covers the full ground-truth manifest",
    "at least one post-candidate novelty probe is actually executed and rejected",
    "no open critical, major, or minor final-review finding remains",
]
EXPECTED_ANTI_OVERCLAIM_ALLOWED = {
    "content snapshot anchor",
    "GitHub-issued workflow provenance",
    "platform-observable separate-thread review",
    "personal paper-scope assurance",
}
EXPECTED_ANTI_OVERCLAIM_FORBIDDEN = {
    "independent executor",
    "security-isolated reviewer",
    "cryptographically independent reviewer",
    "organizationally independent audit",
    "tamper-proof against the machine owner",
    "safe for live trading",
}
EXPECTED_CLAIM_BOUNDARIES = {
    "ASSURANCE-CLAIM-CONTENT": {
        "level": "content_snapshot_anchor",
        "does_not_prove": {
            "文件中的主体、命令或结果字段真实",
            "Git author 或 committer 字段对应真实身份",
            "作者与审查者组织独立",
        },
    },
    "ASSURANCE-CLAIM-MACHINE": {
        "level": "github_issued_workflow_provenance",
        "does_not_prove": {
            "workflow 可控制的 predicate 字段均为真实陈述",
            "manifest 声称的命令与结果仅因 attestation 而真实",
            "测试 oracle 或设计语义正确",
            "GitHub 平台、仓库 owner 与所有构造主体不串谋",
        },
    },
    "ASSURANCE-CLAIM-SEMANTIC": {
        "level": "platform_observable_separate_thread_review",
        "does_not_prove": {
            "子代理线程构成安全意义上的上下文隔离",
            "审查者人类身份的密码学证明",
            "组织级职责分离",
            "仓库内 locator 字符串本身不可伪造",
        },
    },
}
EXPECTED_NOT_COVERED = {
    "同一 OS 管理员或恶意软件重写全部本地状态",
    "仓库 owner、GitHub、OpenAI 平台、主代理和全部子代理共同串谋",
    "组织级独立审计或受监管职责分离",
    "审查者人类身份的密码学证明",
    "真实资金系统所需的券商、密钥、权限和合规边界",
}
DELEGATED_CONFIRMATION_PHRASES = (
    "Javen 已确认",
    "Javen明确确认",
    "Javen 明确确认",
    "human confirmed",
    "human-confirmed",
    "confirmed_active",
)


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


class VerificationSetupError(RuntimeError):
    """Raised when verifier roots cannot be derived safely."""


@dataclass(frozen=True)
class Roots:
    project: Path
    repository: Path
    project_prefix: str


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(
    path: Path,
    *,
    label: str,
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        errors.append(f"{label}: cannot read {path}: {exc}")
        return None
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError, ValueError) as exc:
        errors.append(f"{label}: invalid JSON: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: top-level JSON value must be an object")
        return None
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def exact_integer(value: Any) -> bool:
    return type(value) is int


def validate_hash(value: Any, *, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or HASH_PATTERN.fullmatch(value) is None:
        errors.append(f"{label}: expected a lowercase SHA-256 hex digest")
        return None
    return value


def string_list(
    value: Any,
    *,
    label: str,
    errors: list[str],
    allow_empty: bool,
) -> list[str] | None:
    if not isinstance(value, list):
        errors.append(f"{label}: expected a list")
        return None
    if not allow_empty and not value:
        errors.append(f"{label}: list must not be empty")
        return None
    if not all(nonempty_string(item) for item in value):
        errors.append(f"{label}: every item must be a nonempty string")
        return None
    if len(value) != len(set(value)):
        errors.append(f"{label}: duplicate values are forbidden")
        return None
    return value


def safe_relative_path(
    value: Any,
    *,
    label: str,
    errors: list[str],
) -> PurePosixPath | None:
    if (
        not isinstance(value, str)
        or not value
        or value.startswith("~")
        or "\\" in value
        or any(ord(character) < 32 for character in value)
    ):
        errors.append(f"{label}: unsafe relative path {value!r}")
        return None
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or "." in relative.parts
        or ".." in relative.parts
        or ":" in relative.parts[0]
        or relative.as_posix() != value
    ):
        errors.append(f"{label}: unsafe relative path {value!r}")
        return None
    return relative


def resolve_regular_file(
    base: Path,
    relative_value: Any,
    *,
    label: str,
    errors: list[str],
) -> Path | None:
    relative = safe_relative_path(relative_value, label=label, errors=errors)
    if relative is None:
        return None
    candidate = base.joinpath(*relative.parts)
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        errors.append(f"{label}: missing or unreadable file {relative.as_posix()!r}: {exc}")
        return None
    try:
        resolved.relative_to(base)
    except ValueError:
        errors.append(f"{label}: resolved path escapes its declared scope")
        return None
    if resolved != candidate or not resolved.is_file():
        errors.append(f"{label}: path must name a regular non-symlink file")
        return None
    return resolved


def run_git(
    arguments: list[str],
    *,
    cwd: Path,
    label: str,
) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *arguments],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as exc:
        raise VerificationSetupError(f"{label}: cannot execute Git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stdout.strip() or "<no Git output>"
        raise VerificationSetupError(f"{label}: Git failed: {detail}")
    lines = result.stdout.splitlines()
    if not lines or any(not line for line in lines):
        raise VerificationSetupError(f"{label}: Git returned an empty value")
    return lines


def discover_roots() -> Roots:
    try:
        script_path = Path(__file__).resolve(strict=True)
    except OSError as exc:
        raise VerificationSetupError(f"cannot resolve verifier path: {exc}") from exc
    if (
        script_path.name != "verify_assurance_metadata.py"
        or script_path.parent.name != "scripts"
    ):
        raise VerificationSetupError("verifier is not in the expected project scripts directory")
    project = script_path.parent.parent
    if not (project / "governance").is_dir():
        raise VerificationSetupError("derived project root has no governance directory")
    root_lines = run_git(
        ["rev-parse", "--show-toplevel"],
        cwd=project,
        label="repository root discovery",
    )
    if len(root_lines) != 1:
        raise VerificationSetupError("repository root discovery returned multiple lines")
    raw_root = Path(root_lines[0])
    if not raw_root.is_absolute():
        raise VerificationSetupError("Git repository root is not absolute")
    try:
        repository = raw_root.resolve(strict=True)
    except OSError as exc:
        raise VerificationSetupError(f"cannot resolve Git repository root: {exc}") from exc
    if not repository.is_dir():
        raise VerificationSetupError("Git repository root is not a directory")
    try:
        relative_project = project.relative_to(repository)
    except ValueError as exc:
        raise VerificationSetupError(
            "derived project root is outside the Git repository root"
        ) from exc
    if relative_project == Path("."):
        raise VerificationSetupError("project root must be a non-root repository subtree")
    project_prefix = relative_project.as_posix() + "/"
    return Roots(
        project=project,
        repository=repository,
        project_prefix=project_prefix,
    )


def verify_document_header(
    document: dict[str, Any],
    *,
    label: str,
    errors: list[str],
) -> None:
    if not exact_integer(document.get("schema_version")) or document.get(
        "schema_version"
    ) != 1:
        errors.append(f"{label}: schema_version must be integer 1")
    if document.get("status") not in PROJECT_DOCUMENT_STATUSES:
        errors.append(
            f"{label}: status must be one of {sorted(PROJECT_DOCUMENT_STATUSES)}"
        )


def github_repository_from_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(
        r"(?:git@github\.com:|https://github\.com/)"
        r"(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\.git",
        value,
    )
    return match.group("repository") if match else None


def parse_workflow_permissions(path: Path, errors: list[str]) -> dict[str, str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"trust workflow: cannot read UTF-8 workflow: {exc}")
        return None
    lines = text.splitlines()
    permission_headers: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = re.fullmatch(r"([ \t]*)permissions\s*:\s*(?:#.*)?", line)
        if match:
            permission_headers.append((index, match.group(1)))
    if len(permission_headers) != 1 or permission_headers[0][1]:
        errors.append(
            "trust workflow: exactly one repository-root permissions block is required"
        )
        return None
    start = permission_headers[0][0] + 1
    permissions: dict[str, str] = {}
    for line in lines[start:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")):
            break
        match = re.fullmatch(
            r"  ([a-z][a-z0-9-]*): (read|write|none)(?:\s+#.*)?",
            line,
        )
        if match is None:
            errors.append(
                "trust workflow: permissions block uses unsupported or ambiguous YAML"
            )
            return None
        key, value = match.groups()
        if key in permissions:
            errors.append(f"trust workflow: duplicate permission key {key!r}")
            return None
        permissions[key] = value
    if not permissions:
        errors.append("trust workflow: permissions block must not be empty")
        return None
    return permissions


def verify_trust_model(
    trust: dict[str, Any],
    contract: dict[str, Any],
    research: dict[str, Any],
    roots: Roots,
    errors: list[str],
) -> None:
    verify_document_header(trust, label="assurance trust model", errors=errors)
    if trust.get("model_id") != "ids-personal-paper-assurance-v1":
        errors.append("assurance trust model: model_id differs")

    source = trust.get("source_research")
    if not isinstance(source, dict):
        errors.append("assurance trust model: source_research must be an object")
    else:
        source_path = resolve_regular_file(
            roots.project,
            source.get("path"),
            label="assurance trust model source research",
            errors=errors,
        )
        expected_hash = validate_hash(
            source.get("sha256"),
            label="assurance trust model source research hash",
            errors=errors,
        )
        if (
            source_path is not None
            and expected_hash is not None
            and sha256_file(source_path) != expected_hash
        ):
            errors.append("assurance trust model: source research hash is stale")
        primary_artifacts = research.get("primary_artifacts")
        matching = (
            [
                item
                for item in primary_artifacts
                if isinstance(item, dict) and item.get("path") == source.get("path")
            ]
            if isinstance(primary_artifacts, list)
            else []
        )
        if (
            len(matching) != 1
            or matching[0].get("sha256") != source.get("sha256")
        ):
            errors.append(
                "assurance trust model: source research is not exactly bound "
                "to the research register"
            )

    change_control = contract.get("change_control")
    trusted_remote = (
        change_control.get("trusted_git_remote")
        if isinstance(change_control, dict)
        else None
    )
    if not isinstance(trusted_remote, dict):
        errors.append("acceptance contract: trusted_git_remote must be an object")
        return
    required_remote_keys = {"name", "fetch_url", "branch", "project_prefix"}
    if set(trusted_remote) != required_remote_keys:
        errors.append("acceptance contract: trusted_git_remote fields differ")
    remote_name = trusted_remote.get("name")
    fetch_url = trusted_remote.get("fetch_url")
    branch = trusted_remote.get("branch")
    project_prefix = trusted_remote.get("project_prefix")
    if (
        not isinstance(remote_name, str)
        or re.fullmatch(r"[A-Za-z0-9._-]+", remote_name) is None
        or not nonempty_string(fetch_url)
        or not isinstance(branch, str)
        or re.fullmatch(r"[A-Za-z0-9._/-]+", branch) is None
        or branch.startswith("-")
        or ".." in PurePosixPath(branch).parts
        or not isinstance(project_prefix, str)
        or not project_prefix.endswith("/")
    ):
        errors.append("acceptance contract: trusted Git remote values are unsafe")
        return
    safe_relative_path(
        project_prefix[:-1],
        label="acceptance contract project prefix",
        errors=errors,
    )
    if project_prefix != roots.project_prefix:
        errors.append(
            "acceptance contract: project prefix does not match the derived roots"
        )

    trust_roots = trust.get("trust_roots")
    git_content = (
        trust_roots.get("git_content") if isinstance(trust_roots, dict) else None
    )
    machine = (
        trust_roots.get("github_actions_machine_execution")
        if isinstance(trust_roots, dict)
        else None
    )
    codex = (
        trust_roots.get("codex_semantic_review")
        if isinstance(trust_roots, dict)
        else None
    )
    if not isinstance(git_content, dict):
        errors.append("assurance trust model: git_content trust root is missing")
        return
    expected_git_binding = {
        "remote_name": remote_name,
        "fetch_url": fetch_url,
        "branch": branch,
        "project_prefix": project_prefix,
    }
    for field, expected in expected_git_binding.items():
        if git_content.get(field) != expected:
            errors.append(
                f"assurance trust model: git_content {field} differs "
                "from the acceptance contract"
            )
    repository_name = github_repository_from_url(fetch_url)
    if repository_name is None or git_content.get("repository") != repository_name:
        errors.append(
            "assurance trust model: repository identity does not match fetch_url"
        )
    try:
        observed_urls = run_git(
            ["remote", "get-url", "--all", remote_name],
            cwd=roots.repository,
            label="trusted Git remote observation",
        )
    except VerificationSetupError as exc:
        errors.append(str(exc))
    else:
        if observed_urls != [fetch_url]:
            errors.append(
                "assurance trust model: configured Git fetch URL differs "
                "from the acceptance contract"
            )

    repository_frozen_files = (
        change_control.get("repository_frozen_files")
        if isinstance(change_control, dict)
        else None
    )
    if repository_frozen_files != [WORKFLOW_PATH]:
        errors.append("acceptance contract: repository workflow boundary differs")
    if not isinstance(machine, dict):
        errors.append("assurance trust model: machine-execution trust root is missing")
    else:
        if machine.get("repository") != repository_name:
            errors.append("assurance trust model: machine repository differs")
        if machine.get("workflow_path") != WORKFLOW_PATH:
            errors.append("assurance trust model: workflow path differs")
        workflow = resolve_regular_file(
            roots.repository,
            machine.get("workflow_path"),
            label="assurance trust workflow",
            errors=errors,
        )
        expected_workflow_hash = validate_hash(
            machine.get("workflow_sha256"),
            label="assurance trust workflow hash",
            errors=errors,
        )
        if (
            workflow is not None
            and expected_workflow_hash is not None
            and sha256_file(workflow) != expected_workflow_hash
        ):
            errors.append("assurance trust model: workflow hash is stale")
        required_permissions = machine.get("required_permissions")
        if required_permissions != EXPECTED_WORKFLOW_PERMISSIONS:
            errors.append(
                "assurance trust model: required permissions differ from "
                "the least-privilege contract"
            )
        if workflow is not None:
            observed_permissions = parse_workflow_permissions(workflow, errors)
            if (
                observed_permissions is not None
                and observed_permissions != EXPECTED_WORKFLOW_PERMISSIONS
            ):
                errors.append(
                    "assurance trust model: root workflow permissions differ "
                    "from the least-privilege contract"
                )

    if (
        not isinstance(codex, dict)
        or codex.get("forbidden_claim")
        != "security_isolated_or_cryptographically_independent_reviewer"
    ):
        errors.append(
            "assurance trust model: Codex semantic-review non-overclaim "
            "boundary differs"
        )

    claims = trust.get("claims")
    claim_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(claims, list):
        errors.append("assurance trust model: claims must be a list")
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"assurance trust model: claims[{index}] is not an object")
                continue
            claim_id = claim.get("id")
            if not nonempty_string(claim_id):
                errors.append(f"assurance trust model: claims[{index}] has no id")
                continue
            if claim_id in claim_by_id:
                errors.append(f"assurance trust model: duplicate claim id {claim_id!r}")
                continue
            claim_by_id[claim_id] = claim
            string_list(
                claim.get("proves"),
                label=f"assurance trust model claim {claim_id} proves",
                errors=errors,
                allow_empty=False,
            )
            string_list(
                claim.get("does_not_prove"),
                label=f"assurance trust model claim {claim_id} does_not_prove",
                errors=errors,
                allow_empty=False,
            )
    if set(claim_by_id) != set(EXPECTED_CLAIM_BOUNDARIES):
        errors.append("assurance trust model: claim set differs")
    for claim_id, expected in EXPECTED_CLAIM_BOUNDARIES.items():
        claim = claim_by_id.get(claim_id)
        if claim is None:
            continue
        if claim.get("level") != expected["level"]:
            errors.append(f"assurance trust model: {claim_id} level differs")
        boundaries = claim.get("does_not_prove")
        if not isinstance(boundaries, list) or set(boundaries) != expected[
            "does_not_prove"
        ]:
            errors.append(
                f"assurance trust model: {claim_id} non-overclaim boundary differs"
            )

    bounded = trust.get("bounded_threat_model")
    if not isinstance(bounded, dict):
        errors.append("assurance trust model: bounded_threat_model is missing")
    else:
        string_list(
            bounded.get("covered"),
            label="assurance trust model covered threats",
            errors=errors,
            allow_empty=False,
        )
        not_covered = string_list(
            bounded.get("not_covered"),
            label="assurance trust model non-covered threats",
            errors=errors,
            allow_empty=False,
        )
        if not_covered is not None and not EXPECTED_NOT_COVERED.issubset(
            set(not_covered)
        ):
            errors.append(
                "assurance trust model: explicit non-covered threat boundary differs"
            )

    vocabulary = trust.get("anti_overclaim_vocabulary")
    if not isinstance(vocabulary, dict):
        errors.append("assurance trust model: anti_overclaim_vocabulary is missing")
    else:
        allowed = string_list(
            vocabulary.get("allowed"),
            label="assurance trust model allowed vocabulary",
            errors=errors,
            allow_empty=False,
        )
        forbidden = string_list(
            vocabulary.get("forbidden_without_new_evidence"),
            label="assurance trust model forbidden vocabulary",
            errors=errors,
            allow_empty=False,
        )
        if allowed is not None and set(allowed) != EXPECTED_ANTI_OVERCLAIM_ALLOWED:
            errors.append("assurance trust model: allowed vocabulary differs")
        if forbidden is not None and set(
            forbidden
        ) != EXPECTED_ANTI_OVERCLAIM_FORBIDDEN:
            errors.append("assurance trust model: forbidden vocabulary differs")

    release_rule = trust.get("release_rule")
    if not isinstance(release_rule, dict):
        errors.append("assurance trust model: release_rule is missing")
    else:
        if release_rule.get("type") != "conjunction":
            errors.append("assurance trust model: release rule must be conjunctive")
        if release_rule.get("required") != EXPECTED_RELEASE_REQUIREMENTS:
            errors.append("assurance trust model: conjunctive release terms differ")
        if release_rule.get("single_source_is_sufficient") is not False:
            errors.append(
                "assurance trust model: a single assurance source must not be sufficient"
            )
        if release_rule.get("unknown_or_missing") != "blocked_freeze":
            errors.append(
                "assurance trust model: unknown or missing assurance must block freeze"
            )


def collect_ids(
    value: Any,
    *,
    label: str,
    errors: list[str],
) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"{label}: expected a list")
        return set()
    identifiers: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not nonempty_string(item.get("id")):
            errors.append(f"{label}[{index}]: expected an object with a nonempty id")
            continue
        identifier = item["id"]
        if identifier in identifiers:
            errors.append(f"{label}: duplicate id {identifier!r}")
        identifiers.add(identifier)
    return identifiers


def verify_ground_truth(
    manifest: dict[str, Any],
    research: dict[str, Any],
    trust: dict[str, Any],
    contract: dict[str, Any],
    roots: Roots,
    errors: list[str],
) -> None:
    verify_document_header(manifest, label="ground-truth manifest", errors=errors)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("ground-truth manifest: artifacts must be a nonempty list")
        return
    change_control = contract.get("change_control")
    repository_paths = (
        change_control.get("repository_frozen_files")
        if isinstance(change_control, dict)
        else None
    )
    allowed_repository_paths = (
        set(repository_paths)
        if isinstance(repository_paths, list)
        and all(isinstance(item, str) for item in repository_paths)
        else set()
    )
    observed_repository_paths: set[str] = set()
    artifact_by_path: dict[str, dict[str, Any]] = {}
    sort_keys: list[tuple[int, str]] = []
    scope_rank = {"project": 0, "repository": 1}
    for index, artifact in enumerate(artifacts):
        label = f"ground-truth artifact[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{label}: expected an object")
            continue
        relative = artifact.get("path")
        parsed_relative = safe_relative_path(
            relative,
            label=f"{label} path",
            errors=errors,
        )
        scope = artifact.get("scope", "project")
        if scope not in scope_rank:
            errors.append(f"{label}: scope must be project or repository")
            continue
        if not isinstance(relative, str) or parsed_relative is None:
            continue
        if relative in artifact_by_path:
            errors.append(f"ground-truth manifest: duplicate artifact path {relative!r}")
        else:
            artifact_by_path[relative] = artifact
        sort_keys.append((scope_rank[scope], relative))
        if artifact.get("required") is not True:
            errors.append(f"{label}: required must be true")
        if not nonempty_string(artifact.get("role")):
            errors.append(f"{label}: role must be a nonempty string")
        expected_hash = validate_hash(
            artifact.get("sha256"),
            label=f"{label} hash",
            errors=errors,
        )
        if (
            scope == "project"
            and relative == "governance/GROUND_TRUTH_MANIFEST_V1.json"
        ):
            errors.append("ground-truth manifest: recursive self-reference is forbidden")
        if scope == "repository":
            observed_repository_paths.add(relative)
            if relative not in allowed_repository_paths:
                errors.append(
                    f"{label}: repository-scope path is outside the acceptance contract"
                )
        path = resolve_regular_file(
            roots.repository if scope == "repository" else roots.project,
            relative,
            label=label,
            errors=errors,
        )
        if (
            path is not None
            and expected_hash is not None
            and sha256_file(path) != expected_hash
        ):
            errors.append(f"ground-truth manifest: stale artifact hash for {relative}")
    if sort_keys != sorted(sort_keys):
        errors.append(
            "ground-truth manifest: artifact paths are not lexicographically "
            "sorted within scope"
        )
    if observed_repository_paths != allowed_repository_paths:
        errors.append(
            "ground-truth manifest: repository-scope coverage differs "
            "from the acceptance contract"
        )
    workflow_artifact = artifact_by_path.get(WORKFLOW_PATH)
    machine = (
        trust.get("trust_roots", {}).get("github_actions_machine_execution")
        if isinstance(trust.get("trust_roots"), dict)
        else None
    )
    if (
        not isinstance(workflow_artifact, dict)
        or workflow_artifact.get("scope") != "repository"
        or workflow_artifact.get("required") is not True
    ):
        errors.append(
            "ground-truth manifest: required repository assurance workflow is missing"
        )
    elif (
        not isinstance(machine, dict)
        or workflow_artifact.get("sha256") != machine.get("workflow_sha256")
    ):
        errors.append(
            "ground-truth manifest: workflow hash differs from the trust model"
        )

    primary_artifacts = research.get("primary_artifacts")
    if not isinstance(primary_artifacts, list) or not primary_artifacts:
        errors.append("research register: primary_artifacts must be a nonempty list")
        return
    primary_ids: set[str] = set()
    primary_paths: set[str] = set()
    for index, primary in enumerate(primary_artifacts):
        label = f"research primary_artifact[{index}]"
        if not isinstance(primary, dict):
            errors.append(f"{label}: expected an object")
            continue
        primary_id = primary.get("id")
        relative = primary.get("path")
        expected_hash = validate_hash(
            primary.get("sha256"),
            label=f"{label} hash",
            errors=errors,
        )
        if not nonempty_string(primary_id):
            errors.append(f"{label}: id must be a nonempty string")
        elif primary_id in primary_ids:
            errors.append(f"research register: duplicate primary artifact id {primary_id!r}")
        else:
            primary_ids.add(primary_id)
        parsed = safe_relative_path(
            relative,
            label=f"{label} path",
            errors=errors,
        )
        if isinstance(relative, str) and parsed is not None:
            if relative in primary_paths:
                errors.append(
                    f"research register: duplicate primary artifact path {relative!r}"
                )
            primary_paths.add(relative)
            declared = artifact_by_path.get(relative)
            if declared is None:
                errors.append(
                    f"ground-truth manifest: missing research primary artifact {relative}"
                )
            elif declared.get("scope", "project") != "project":
                errors.append(
                    f"ground-truth manifest: research primary artifact {relative} "
                    "must use project scope"
                )
            elif expected_hash is not None and declared.get("sha256") != expected_hash:
                errors.append(
                    f"ground-truth manifest: research primary artifact hash "
                    f"differs for {relative}"
                )


def verify_failure_registry(
    registry: dict[str, Any],
    contract: dict[str, Any],
    traceability: dict[str, Any],
    verification_specs: dict[str, Any],
    acceptance_cases: dict[str, Any],
    roots: Roots,
    errors: list[str],
) -> None:
    verify_document_header(registry, label="failure registry", errors=errors)
    taxonomy_relative = registry.get("source_taxonomy_path")
    taxonomy = resolve_regular_file(
        roots.project,
        taxonomy_relative,
        label="failure registry source taxonomy",
        errors=errors,
    )
    expected_source_hash = registry.get("source_taxonomy_hash")
    observed_source_hash = sha256_file(taxonomy) if taxonomy is not None else None
    if (
        not isinstance(expected_source_hash, str)
        or not expected_source_hash.startswith("sha256:")
        or HASH_PATTERN.fullmatch(expected_source_hash.removeprefix("sha256:")) is None
    ):
        errors.append("failure registry: source taxonomy hash format differs")
    elif observed_source_hash != expected_source_hash.removeprefix("sha256:"):
        errors.append("failure registry: source taxonomy hash is stale")

    requirement_ids = collect_ids(
        contract.get("requirements"),
        label="acceptance contract requirements",
        errors=errors,
    )
    control_ids = collect_ids(
        traceability.get("controls"),
        label="traceability controls",
        errors=errors,
    )
    contract_verification_ids = collect_ids(
        contract.get("verification_catalog"),
        label="acceptance contract verification catalog",
        errors=errors,
    )
    spec_verification_ids = collect_ids(
        verification_specs.get("specs"),
        label="verification specs",
        errors=errors,
    )
    if contract_verification_ids != spec_verification_ids:
        errors.append(
            "verification references: acceptance catalog and specs differ"
        )
    verification_ids = contract_verification_ids & spec_verification_ids
    case_ids = collect_ids(
        acceptance_cases.get("cases"),
        label="acceptance cases",
        errors=errors,
    )
    allowed_references = {
        "requirement_ids": requirement_ids,
        "control_ids": control_ids,
        "verification_ids": verification_ids,
        "acceptance_case_ids": case_ids,
    }

    failure_classes = registry.get("failure_classes")
    if not isinstance(failure_classes, list) or not failure_classes:
        errors.append("failure registry: failure_classes must be a nonempty list")
        return
    primary_ids: set[str] = set()
    aliases: set[str] = set()
    parsed_items: list[dict[str, Any]] = []
    domain_counts: dict[str, dict[str, Any]] = {}
    expected_open_gaps: list[dict[str, Any]] = []
    covered_count = 0
    gap_count = 0
    alias_count = 0

    for index, item in enumerate(failure_classes):
        label = f"failure class[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}: expected an object")
            continue
        failure_id = item.get("id")
        if not nonempty_string(failure_id):
            errors.append(f"{label}: id must be a nonempty string")
            continue
        if failure_id in primary_ids:
            errors.append(f"failure registry: duplicate failure id {failure_id!r}")
        primary_ids.add(failure_id)
        parsed_items.append(item)

    for item in parsed_items:
        failure_id = item["id"]
        label = f"failure class {failure_id}"
        item_aliases = string_list(
            item.get("aliases"),
            label=f"{label} aliases",
            errors=errors,
            allow_empty=True,
        )
        if item_aliases is not None:
            alias_count += len(item_aliases)
            for alias in item_aliases:
                if alias in aliases or alias in primary_ids:
                    errors.append(
                        f"failure registry: duplicate or colliding alias {alias!r}"
                    )
                aliases.add(alias)
        status = item.get("status")
        if status not in {"covered", "gap"}:
            errors.append(f"{label}: status must be covered or gap")
        domain = item.get("domain")
        if not nonempty_string(domain):
            errors.append(f"{label}: domain must be a nonempty string")
            domain = "<invalid>"
        counts = domain_counts.setdefault(
            domain,
            {"domain": domain, "total": 0, "covered": 0, "gaps": 0},
        )
        counts["total"] += 1
        if status == "covered":
            covered_count += 1
            counts["covered"] += 1
        elif status == "gap":
            gap_count += 1
            counts["gaps"] += 1
        if item.get("source_path") != taxonomy_relative:
            errors.append(f"{label}: source_path differs from source taxonomy")
        if not nonempty_string(item.get("residual_risk")):
            errors.append(f"{label}: residual_risk must be nonempty")

        missing_dimensions: list[str] = []
        for reference_field in FAILURE_REFERENCE_FIELDS:
            references = string_list(
                item.get(reference_field),
                label=f"{label} {reference_field}",
                errors=errors,
                allow_empty=True,
            )
            if not references:
                missing_dimensions.append(reference_field)
                continue
            unknown = sorted(set(references) - allowed_references[reference_field])
            if unknown:
                errors.append(
                    f"{label}: unknown {reference_field} references {unknown}"
                )
        open_gaps = string_list(
            item.get("open_gaps"),
            label=f"{label} open_gaps",
            errors=errors,
            allow_empty=True,
        )
        if status == "covered":
            if missing_dimensions:
                errors.append(
                    f"{label}: covered status has missing dimensions "
                    f"{missing_dimensions}"
                )
            if open_gaps != []:
                errors.append(f"{label}: covered status must have no open gaps")
        elif status == "gap":
            if not missing_dimensions:
                errors.append(f"{label}: gap status has no missing dimensions")
            if open_gaps is None or len(open_gaps) != 1:
                errors.append(
                    f"{label}: gap status requires exactly one explicit gap reason"
                )
            else:
                expected_open_gaps.append(
                    {
                        "id": failure_id,
                        "domain": domain,
                        "missing": missing_dimensions,
                        "reason": open_gaps[0],
                    }
                )

    if aliases & primary_ids:
        errors.append("failure registry: aliases collide with primary failure IDs")
    expected_summary = {
        "total_failure_classes": len(failure_classes),
        "covered_failure_classes": covered_count,
        "gap_failure_classes": gap_count,
        "alias_count": alias_count,
        "domains": list(domain_counts.values()),
        "open_gap_ids": [item["id"] for item in expected_open_gaps],
    }
    if registry.get("coverage_summary") != expected_summary:
        errors.append("failure registry: coverage_summary does not recompute exactly")
    if registry.get("open_gaps") != expected_open_gaps:
        errors.append("failure registry: top-level open_gaps do not recompute exactly")


def verify_decision_authority(
    document: dict[str, Any],
    roots: Roots,
    errors: list[str],
) -> None:
    verify_document_header(document, label="decision authority", errors=errors)
    authority_model = document.get("authority_model")
    allowed_authorities = (
        authority_model.get("allowed")
        if isinstance(authority_model, dict)
        else None
    )
    if (
        not isinstance(allowed_authorities, list)
        or set(allowed_authorities) != set(AUTHORITY_STATUS_PAIRS)
        or len(allowed_authorities) != len(set(AUTHORITY_STATUS_PAIRS))
    ):
        errors.append("decision authority: allowed authority set differs")
    expected_non_confirmation_rule = (
        "只有 authority=human_explicit 且 source excerpt 可重算时，才允许把该项描述为 "
        "Javen 已确认；其他 authority 一律保留其候选、条件性或未设置状态。"
    )
    if (
        not isinstance(authority_model, dict)
        or authority_model.get("non_confirmation_rule")
        != expected_non_confirmation_rule
    ):
        errors.append("decision authority: non-confirmation rule differs")
    status_model = document.get("status_model")
    known_statuses = set().union(*AUTHORITY_STATUS_PAIRS.values())
    if not isinstance(status_model, dict) or set(status_model) != known_statuses:
        errors.append("decision authority: status model differs")
    elif not all(nonempty_string(value) for value in status_model.values()):
        errors.append("decision authority: status descriptions must be nonempty")

    decisions = document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        errors.append("decision authority: decisions must be a nonempty list")
        return
    decision_ids: set[str] = set()
    source_line_cache: dict[Path, list[str]] = {}
    for index, decision in enumerate(decisions):
        label = f"decision[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{label}: expected an object")
            continue
        decision_id = decision.get("id")
        if not nonempty_string(decision_id):
            errors.append(f"{label}: id must be a nonempty string")
            continue
        label = f"decision {decision_id}"
        if decision_id in decision_ids:
            errors.append(f"decision authority: duplicate decision id {decision_id!r}")
        decision_ids.add(decision_id)
        for field in ("topic", "decision", "rationale"):
            if not nonempty_string(decision.get(field)):
                errors.append(f"{label}: {field} must be nonempty")
        authority = decision.get("authority")
        status = decision.get("status")
        allowed_statuses = AUTHORITY_STATUS_PAIRS.get(authority)
        if allowed_statuses is None or status not in allowed_statuses:
            errors.append(
                f"{label}: authority/status pairing is not allowed "
                f"({authority!r}, {status!r})"
            )

        sources = decision.get("sources")
        if not isinstance(sources, list):
            errors.append(f"{label}: sources must be a list")
            sources = []
        if authority == "human_explicit" and not sources:
            errors.append(f"{label}: human_explicit requires source evidence")
        if not sources:
            errors.append(f"{label}: decision provenance must not be empty")
        for source_index, source in enumerate(sources):
            source_label = f"{label} source[{source_index}]"
            if not isinstance(source, dict):
                errors.append(f"{source_label}: expected an object")
                continue
            source_path = resolve_regular_file(
                roots.project,
                source.get("path"),
                label=f"{source_label} path",
                errors=errors,
            )
            line_start = source.get("line_start")
            line_end = source.get("line_end")
            if (
                not exact_integer(line_start)
                or not exact_integer(line_end)
                or line_start < 1
                or line_end < line_start
            ):
                errors.append(f"{source_label}: invalid one-based line range")
                continue
            excerpt = source.get("excerpt")
            excerpt_hash = validate_hash(
                source.get("excerpt_sha256"),
                label=f"{source_label} excerpt hash",
                errors=errors,
            )
            if not isinstance(excerpt, str):
                errors.append(f"{source_label}: excerpt must be a string")
                continue
            if source_path is not None:
                if source_path not in source_line_cache:
                    try:
                        source_line_cache[source_path] = source_path.read_text(
                            encoding="utf-8"
                        ).splitlines()
                    except (OSError, UnicodeDecodeError) as exc:
                        errors.append(f"{source_label}: cannot read source lines: {exc}")
                        source_line_cache[source_path] = []
                lines = source_line_cache[source_path]
                if line_end > len(lines):
                    errors.append(f"{source_label}: line range exceeds current source")
                else:
                    observed_excerpt = "\n".join(lines[line_start - 1 : line_end])
                    if excerpt != observed_excerpt:
                        errors.append(
                            f"{source_label}: excerpt does not equal the current "
                            "source line range"
                        )
            observed_excerpt_hash = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
            if excerpt_hash is not None and excerpt_hash != observed_excerpt_hash:
                errors.append(f"{source_label}: excerpt hash does not match excerpt")
            if "context" in source and not nonempty_string(source.get("context")):
                errors.append(f"{source_label}: context must be nonempty when present")

        reversibility = decision.get("reversibility")
        if not isinstance(reversibility, dict) or not reversibility:
            errors.append(f"{label}: reversibility must be a nonempty object")
            reversibility = {}
        if not nonempty_string(reversibility.get("class")):
            errors.append(f"{label}: reversibility class must be nonempty")
        if not nonempty_string(reversibility.get("notes")):
            errors.append(f"{label}: reversibility notes must be nonempty")
        if type(reversibility.get("human_confirmation_required")) is not bool:
            errors.append(
                f"{label}: reversibility human_confirmation_required must be boolean"
            )
        reopen_triggers = string_list(
            decision.get("reopen_trigger"),
            label=f"{label} reopen_trigger",
            errors=errors,
            allow_empty=False,
        )
        if reopen_triggers is None:
            reopen_triggers = []

        if authority == "human_only_required":
            if status != "unset_human_only_blocking":
                errors.append(f"{label}: human-only decision must remain blocking")
            if reversibility.get("human_confirmation_required") is not True:
                errors.append(
                    f"{label}: human-only decision must require human confirmation"
                )
        if authority == "human_delegated_reversible":
            if (
                not isinstance(status, str)
                or not status.endswith("_not_human_confirmed")
            ):
                errors.append(
                    f"{label}: delegated choice claims human confirmation by status"
                )
            if reversibility.get("human_confirmation_required") is not False:
                errors.append(
                    f"{label}: delegated V1 choice must remain reversibly delegated"
                )
            delegated_text = "\n".join(
                str(value)
                for value in (
                    decision.get("decision", ""),
                    decision.get("rationale", ""),
                    reversibility.get("notes", ""),
                )
            ).lower()
            if any(
                phrase.lower() in delegated_text
                for phrase in DELEGATED_CONFIRMATION_PHRASES
            ):
                errors.append(
                    f"{label}: delegated choice contains a human-confirmation claim"
                )


def verify_all() -> list[str]:
    errors: list[str] = []
    try:
        roots = discover_roots()
    except VerificationSetupError as exc:
        return [f"verifier setup: {exc}"]

    document_paths = {
        "trust": "governance/ASSURANCE_TRUST_MODEL_V1.json",
        "manifest": "governance/GROUND_TRUTH_MANIFEST_V1.json",
        "failures": "governance/FAILURE_CLASSES_V1.json",
        "authority": "governance/DECISION_AUTHORITY_V1.json",
        "contract": "governance/ACCEPTANCE_CONTRACT_V1.json",
        "research": "governance/AI_PROJECT_RESEARCH_REGISTER_V1.json",
        "traceability": "governance/TRACEABILITY_V1.json",
        "cases": "governance/ACCEPTANCE_CASES_V1.json",
        "verification": "governance/VERIFICATION_SPECS_V1.json",
    }
    documents: dict[str, dict[str, Any]] = {}
    for key, relative in document_paths.items():
        document = load_json(
            roots.project / relative,
            label=relative,
            errors=errors,
        )
        if document is not None:
            documents[key] = document
    if errors:
        return errors

    verify_trust_model(
        documents["trust"],
        documents["contract"],
        documents["research"],
        roots,
        errors,
    )
    verify_ground_truth(
        documents["manifest"],
        documents["research"],
        documents["trust"],
        documents["contract"],
        roots,
        errors,
    )
    verify_failure_registry(
        documents["failures"],
        documents["contract"],
        documents["traceability"],
        documents["verification"],
        documents["cases"],
        roots,
        errors,
    )
    verify_decision_authority(documents["authority"], roots, errors)
    return errors


def output_result(errors: Iterable[str], *, as_json: bool) -> int:
    error_list = list(errors)
    status = "fail" if error_list else "pass"
    if as_json:
        print(
            json.dumps(
                {
                    "status": status,
                    "error_count": len(error_list),
                    "errors": error_list,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
    elif error_list:
        print("assurance metadata: FAIL")
        for error in error_list:
            print(f"- {error}")
    else:
        print("assurance metadata: PASS")
    return 1 if error_list else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify assurance metadata and all current source bindings."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit one machine-readable JSON result.",
    )
    args = parser.parse_args()
    try:
        errors = verify_all()
    except Exception as exc:  # pragma: no cover - last-resort fail-closed boundary
        errors = [f"internal verifier failure: {type(exc).__name__}: {exc}"]
    return output_result(errors, as_json=args.json)


if __name__ == "__main__":
    sys.exit(main())
