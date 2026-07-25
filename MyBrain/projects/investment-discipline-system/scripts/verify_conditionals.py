#!/usr/bin/env python3
"""Verify conditional gates from independently resolved, replay-resistant evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pwd
import re
import sqlite3
import stat
import subprocess
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).expanduser().resolve()
CONTRACT_RELATIVE = "governance/ACCEPTANCE_CONTRACT_V1.json"
CONTRACT = PROJECT_ROOT / CONTRACT_RELATIVE
FROZEN_BUNDLE_RELATIVE = "governance/FROZEN_BUNDLE_V1.json"
FROZEN_BUNDLE = PROJECT_ROOT / FROZEN_BUNDLE_RELATIVE
VERIFIER_RELATIVE = "scripts/verify_conditionals.py"
SHA1_RE = re.compile(r"[0-9a-f]{40}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SQL_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
EVIDENCE_REQUIRED_V2 = (
    "schema_version",
    "condition_id",
    "gate_id",
    "gate_stage",
    "state",
    "candidate_commit",
    "candidate_tree",
    "frozen_bundle_path",
    "frozen_bundle_sha256",
    "run_id",
    "producer_id",
    "executor_ids",
    "acceptance_case_ids",
    "observation",
    "run_receipt",
    "raw_result_path",
    "raw_result_sha256",
    "completed_at",
)
OBSERVATION_REQUIRED_V2 = (
    "authority",
    "condition_id",
    "source_event_seq",
    "source_event_hash",
    "source_state_hash",
    "source_anchor_hash",
    "observed_at",
)
RUN_RECEIPT_REQUIRED_V1 = (
    "authority",
    "run_event_seq",
    "run_event_hash",
    "run_anchor_hash",
    "run_id",
    "condition_id",
    "gate_id",
    "gate_stage",
    "state",
    "source_event_seq",
    "source_event_hash",
    "source_state_hash",
    "source_anchor_hash",
    "raw_result_path",
    "raw_result_sha256",
    "completed_at",
)
RAW_RESULT_REQUIRED_V1 = (
    "schema_version",
    "condition_id",
    "gate_id",
    "gate_stage",
    "state",
    "candidate_commit",
    "candidate_tree",
    "frozen_bundle_path",
    "frozen_bundle_sha256",
    "run_id",
    "producer_id",
    "executor_ids",
    "acceptance_case_ids",
    "observation",
    "started_at",
    "completed_at",
    "status",
    "actual_cases_run",
    "case_results",
)
CASE_RESULT_REQUIRED_V1 = (
    "case_id",
    "status",
    "input_hashes",
    "raw_result_hashes",
)
RUNTIME_EVENT_PRODUCER_ID = "PRODUCER-RUNTIME-CONDITION-OBSERVER-V1"
RAW_RESULT_PREFIX = "evidence/conditional/raw/"
ARTIFACT_PREFIX = "evidence/conditional/artifacts/"
MAX_EVIDENCE_AGE_SECONDS = 86400
APPEND_ONLY_TRIGGER_SPECS = (
    {
        "name": "events_no_update",
        "table": "events",
        "operation": "update",
    },
    {
        "name": "events_no_delete",
        "table": "events",
        "operation": "delete",
    },
    {
        "name": "condition_observations_no_update",
        "table": "condition_observations",
        "operation": "update",
    },
    {
        "name": "condition_observations_no_delete",
        "table": "condition_observations",
        "operation": "delete",
    },
    {
        "name": "conditional_gate_runs_no_update",
        "table": "conditional_gate_runs",
        "operation": "update",
    },
    {
        "name": "conditional_gate_runs_no_delete",
        "table": "conditional_gate_runs",
        "operation": "delete",
    },
)
ANCHOR_REQUIRED_V1 = (
    "schema_version",
    "sequence",
    "event_hash",
    "anchored_at",
    "previous_anchor_hash",
    "anchor_hash",
)
ANCHOR_SCHEMA_V1 = {
    "schema_version": 1,
    "format": "canonical_jsonl",
    "required": list(ANCHOR_REQUIRED_V1),
    "genesis_previous_anchor_hash": "0" * 64,
    "hash_algorithm": "sha256_canonical_json_v1",
    "tail_must_equal_main_event_chain": True,
}
RUNTIME_AUTHORITY_POLICY_V1 = {
    "production_config_path": (
        "~/Library/Application Support/InvestmentDisciplineSystem/"
        "runtime-authority.json"
    ),
    "config_schema_version": 1,
    "runtime_database_relative_path": "runtime.sqlite3",
    "anchor_relative_path": "anchors.jsonl",
    "fixture_override_env": "IDS_RUNTIME_AUTHORITY_CONFIG",
    "fixture_mode_env": "IDS_CONDITIONAL_FIXTURE_MODE",
    "fixture_release_allowed": False,
    "cli_runtime_db_role": "expected_value_only",
    "production_root_mode_max": "0700",
    "production_file_mode_max": "0600",
    "production_owner": "current_uid",
    "production_forbidden_roots": [
        "project_root",
        "~/Library/CloudStorage",
        "~/Library/Mobile Documents",
        "~/Dropbox",
        "~/Google Drive",
        "~/OneDrive",
    ],
    "production_anchor_trust": (
        "fail_closed_until_pinned_external_signature_verifier"
    ),
    "fixture_anchor_trust": "hash_chain_test_only",
    "fixture_permission_exempt": True,
}
RUNTIME_EVENT_CHAIN_SCHEMA_V1 = {
    "schema_version": 1,
    "event_table": "events",
    "event_domain": "main_application",
    "observation_table": "condition_observations",
    "gate_run_table": "conditional_gate_runs",
    "event_columns": [
        "sequence",
        "event_type",
        "producer_id",
        "occurred_at",
        "payload_json",
        "prev_hash",
        "event_hash",
    ],
    "event_column_types": {
        "sequence": "INTEGER",
        "event_type": "TEXT",
        "producer_id": "TEXT",
        "occurred_at": "TEXT",
        "payload_json": "TEXT",
        "prev_hash": "TEXT",
        "event_hash": "TEXT",
    },
    "event_primary_key": ["sequence"],
    "observation_columns": [
        "source_event_seq",
        "condition_id",
        "stage",
        "ready",
        "source_event_hash",
        "source_state_hash",
        "source_anchor_hash",
        "observed_at",
        "producer_id",
    ],
    "observation_column_types": {
        "source_event_seq": "INTEGER",
        "condition_id": "TEXT",
        "stage": "TEXT",
        "ready": "INTEGER",
        "source_event_hash": "TEXT",
        "source_state_hash": "TEXT",
        "source_anchor_hash": "TEXT",
        "observed_at": "TEXT",
        "producer_id": "TEXT",
    },
    "observation_primary_key": ["source_event_seq"],
    "gate_run_columns": [
        "run_event_seq",
        "run_id",
        "condition_id",
        "gate_id",
        "gate_stage",
        "state",
        "source_event_seq",
        "source_event_hash",
        "source_state_hash",
        "source_anchor_hash",
        "raw_result_path",
        "raw_result_sha256",
        "completed_at",
        "producer_id",
        "run_event_hash",
        "run_anchor_hash",
    ],
    "gate_run_column_types": {
        "run_event_seq": "INTEGER",
        "run_id": "TEXT",
        "condition_id": "TEXT",
        "gate_id": "TEXT",
        "gate_stage": "TEXT",
        "state": "TEXT",
        "source_event_seq": "INTEGER",
        "source_event_hash": "TEXT",
        "source_state_hash": "TEXT",
        "source_anchor_hash": "TEXT",
        "raw_result_path": "TEXT",
        "raw_result_sha256": "TEXT",
        "completed_at": "TEXT",
        "producer_id": "TEXT",
        "run_event_hash": "TEXT",
        "run_anchor_hash": "TEXT",
    },
    "gate_run_primary_key": ["run_event_seq"],
    "gate_run_unique": ["run_id"],
    "append_only_triggers": list(APPEND_ONLY_TRIGGER_SPECS),
    "event_types": ["condition_observation", "conditional_gate_run"],
    "genesis_prev_hash": "0" * 64,
    "payload_required_by_type": {
        "condition_observation": [
            "condition_id",
            "stage",
            "ready",
            "observed_at",
            "producer_id",
            "candidate_commit",
            "candidate_tree",
            "frozen_bundle_path",
            "frozen_bundle_sha256",
        ],
        "conditional_gate_run": [
            "run_id",
            "condition_id",
            "gate_id",
            "gate_stage",
            "state",
            "source_event_seq",
            "source_event_hash",
            "source_state_hash",
            "source_anchor_hash",
            "raw_result_path",
            "raw_result_sha256",
            "completed_at",
            "producer_id",
            "executor_ids",
            "acceptance_case_ids",
            "candidate_commit",
            "candidate_tree",
            "frozen_bundle_path",
            "frozen_bundle_sha256",
        ],
    },
    "event_hash_algorithm": "sha256_canonical_json_v1",
    "event_hash_fields": [
        "sequence",
        "event_type",
        "producer_id",
        "occurred_at",
        "payload",
        "prev_hash",
    ],
    "source_state_hash_algorithm": "sha256_canonical_json_v1",
    "source_state_hash_fields": [
        "through_sequence",
        "through_event_hash",
        "condition_states",
    ],
    "canonical_json": {
        "sort_keys": True,
        "ensure_ascii": False,
        "allow_nan": False,
        "separators": [",", ":"],
    },
    "anchor_schema": ANCHOR_SCHEMA_V1,
}
CONDITIONAL_BINDING_RULE_V2 = (
    "Git HEAD and the fixed frozen-bundle file are authoritative; CLI, raw "
    "results, evidence and --runtime-db are expected values only. Runtime "
    "readiness requires the fixed private runtime authority, a contract-authorized "
    "producer, the recomputed append-only main event chain and its external "
    "anchor; fixture authority cannot satisfy human or longitudinal release. "
    "Every gate run must append one unique run_id receipt to that anchored main "
    "event chain, binding the latest prerequisite observation and raw-result hash; "
    "overwriting current evidence cannot erase or replace the receipt. Passing "
    "evidence requires that fresh receipt, exact case-set equality and recomputable "
    "per-case input/raw hashes."
)
CONDITIONAL_EVIDENCE_SCHEMA_V2 = {
    "schema_version": 2,
    "required": list(EVIDENCE_REQUIRED_V2),
    "additional_fields_allowed": False,
    "state_enum": ["passed", "failed", "inconclusive"],
    "identity_authority": {
        "candidate_commit": "project_root_git_head",
        "candidate_tree": "project_root_git_head_tree",
        "frozen_bundle_path": FROZEN_BUNDLE_RELATIVE,
        "frozen_bundle_sha256": "sha256_file_bytes",
        "cli_and_evidence_role": "expected_values_only",
    },
    "observation_schema": {
        "required": list(OBSERVATION_REQUIRED_V2),
        "additional_fields_allowed": False,
        "runtime_event_seq_minimum": 1,
        "environment_presence_event_seq": 0,
    },
    "run_receipt_schema": {
        "required": list(RUN_RECEIPT_REQUIRED_V1),
        "additional_fields_allowed": False,
        "authority": "runtime_sqlite_gate_run_receipt",
        "runtime_event_seq_minimum": 1,
    },
    "raw_result_schema": {
        "schema_version": 1,
        "required": list(RAW_RESULT_REQUIRED_V1),
        "additional_fields_allowed": False,
        "required_status": "pass",
    },
    "case_result_schema": {
        "required": list(CASE_RESULT_REQUIRED_V1),
        "additional_fields_allowed": False,
        "required_status": "pass",
        "hash_algorithm": "sha256",
    },
    "runtime_authority": RUNTIME_AUTHORITY_POLICY_V1,
    "runtime_event_chain_schema": RUNTIME_EVENT_CHAIN_SCHEMA_V1,
    "binding_rule": CONDITIONAL_BINDING_RULE_V2,
}
GATE_CATALOG_POLICY_V2 = {
    "GATE-TIINGO-LIVE-PROBE": {
        "executor_ids": ["EX-CONDITIONAL"],
        "evidence_producer_id": "EX-CONDITIONAL",
        "producer_authority_source": "frozen_conditional_gate_catalog",
        "caller_producer_override_allowed": False,
        "raw_result_path_prefix": RAW_RESULT_PREFIX,
        "artifact_path_prefix": ARTIFACT_PREFIX,
        "max_evidence_age_seconds": MAX_EVIDENCE_AGE_SECONDS,
    },
    "GATE-LONGITUDINAL-EVALUATION": {
        "executor_ids": ["EX-CONDITIONAL"],
        "evidence_producer_id": "EX-CONDITIONAL",
        "producer_authority_source": "frozen_conditional_gate_catalog",
        "caller_producer_override_allowed": False,
        "raw_result_path_prefix": RAW_RESULT_PREFIX,
        "artifact_path_prefix": ARTIFACT_PREFIX,
        "max_evidence_age_seconds": MAX_EVIDENCE_AGE_SECONDS,
    },
    "GATE-JAVEN-FIELD-USE": {
        "executor_ids": ["EX-CONDITIONAL", "EX-HUMAN"],
        "evidence_producer_id": "EX-CONDITIONAL",
        "producer_authority_source": "frozen_conditional_gate_catalog",
        "caller_producer_override_allowed": False,
        "raw_result_path_prefix": RAW_RESULT_PREFIX,
        "artifact_path_prefix": ARTIFACT_PREFIX,
        "max_evidence_age_seconds": MAX_EVIDENCE_AGE_SECONDS,
    },
}
MANDATORY_GATE_BY_CONDITION_V2 = {
    "COND-TIINGO-LIVE-PROBE": "GATE-TIINGO-LIVE-PROBE",
    "COND-LONGITUDINAL-EDGE": "GATE-LONGITUDINAL-EVALUATION",
    "COND-JAVEN-FIELD-USE": "GATE-JAVEN-FIELD-USE",
}
REQUIRED_CASES_V2 = {
    ("COND-TIINGO-LIVE-PROBE", "live_probe"): {
        "CASE-TIINGO-CREDENTIAL-PRESENT-PENDING"
    },
    ("COND-LONGITUDINAL-EDGE", "future_window"): {
        "CASE-FAMILY-RENAME",
        "CASE-CONTAMINATION-UNKNOWN",
        "CASE-BENCHMARK-TOTAL-RETURN",
    },
    ("COND-JAVEN-FIELD-USE", "human_onboarding"): {
        "CASE-HUMAN-REAL-JOURNEY",
        "CASE-FIELD-USE-FIXTURE-REJECTED",
        "CASE-BACKUP-UNENCRYPTED-STATUS",
    },
    ("COND-JAVEN-FIELD-USE", "longitudinal"): {
        "CASE-FIELD-USE-FAIL-REOPENS"
    },
}


@dataclass(frozen=True)
class AuthoritativeBindings:
    candidate_commit: str | None
    candidate_tree: str | None
    frozen_bundle_path: str
    frozen_bundle_sha256: str | None
    errors: tuple[str, ...]

    def public_record(self) -> dict[str, Any]:
        return {
            "candidate_commit": self.candidate_commit,
            "candidate_tree": self.candidate_tree,
            "frozen_bundle_path": self.frozen_bundle_path,
            "frozen_bundle_sha256": self.frozen_bundle_sha256,
            "identity_source": {
                "candidate_commit": "project_root_git_head",
                "candidate_tree": "project_root_git_head_tree",
                "frozen_bundle_path": "fixed_project_relative_path",
                "frozen_bundle_sha256": "sha256_file_bytes",
            },
        }


@dataclass(frozen=True)
class RuntimeAuthority:
    mode: str
    config_source: str
    runtime_db_path: Path | None
    anchor_path: Path | None
    permission_policy: str
    anchor_trust: str
    errors: tuple[str, ...]

    def public_record(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "config_source": self.config_source,
            "database_locator": RUNTIME_AUTHORITY_POLICY_V1[
                "runtime_database_relative_path"
            ],
            "anchor_locator": RUNTIME_AUTHORITY_POLICY_V1[
                "anchor_relative_path"
            ],
            "cli_runtime_db_role": "expected_value_only",
            "fixture_release_allowed": False,
            "permission_policy": self.permission_policy,
            "anchor_trust": self.anchor_trust,
            "status": "fail" if self.errors else "pass",
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class RuntimeLedger:
    available: bool
    observations_by_condition: dict[str, dict[str, Any]]
    gate_runs_by_id: dict[str, dict[str, Any]]
    errors: tuple[str, ...]


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lexical_absolute(path: Path, *, relative_root: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = relative_root / expanded
    absolute = Path(os.path.abspath(os.fspath(expanded)))
    for system_alias in (Path("/var"), Path("/tmp"), Path("/etc")):
        try:
            remainder = absolute.relative_to(system_alias)
        except ValueError:
            continue
        canonical_prefix = Path(os.path.realpath(system_alias))
        return canonical_prefix / remainder
    return absolute


def reject_symlink_components(
    path: Path, *, label: str, errors: list[str]
) -> None:
    absolute = lexical_absolute(path, relative_root=PROJECT_ROOT)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if os.path.lexists(current) and current.is_symlink():
            errors.append(f"{label}_path_uses_symlink:{current.name}")


def path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def current_account_home(errors: list[str]) -> Path | None:
    try:
        account = pwd.getpwuid(os.getuid())
    except KeyError:
        errors.append("runtime_current_uid_account_missing")
        return None
    home = Path(account.pw_dir)
    if not home.is_absolute():
        errors.append("runtime_current_uid_home_not_absolute")
        return None
    return lexical_absolute(home, relative_root=PROJECT_ROOT)


def fixed_production_config_path(
    account_home: Path | None, errors: list[str]
) -> Path | None:
    configured = RUNTIME_AUTHORITY_POLICY_V1["production_config_path"]
    if account_home is None:
        return None
    if not isinstance(configured, str) or not configured.startswith("~/"):
        errors.append("runtime_production_config_policy_invalid")
        return None
    return lexical_absolute(
        account_home / configured[2:], relative_root=PROJECT_ROOT
    )


def validate_owned_private_path(
    path: Path,
    *,
    label: str,
    expected_kind: str,
    maximum_mode: int,
    errors: list[str],
) -> None:
    try:
        metadata = path.lstat()
    except OSError:
        errors.append(f"{label}_missing")
        return
    if expected_kind == "directory":
        kind_matches = stat.S_ISDIR(metadata.st_mode)
    else:
        kind_matches = stat.S_ISREG(metadata.st_mode)
    if not kind_matches:
        errors.append(f"{label}_type_invalid")
    if metadata.st_uid != os.getuid():
        errors.append(f"{label}_owner_not_current_uid")
    actual_mode = stat.S_IMODE(metadata.st_mode)
    if actual_mode & ~maximum_mode:
        errors.append(
            f"{label}_permissions_too_broad:"
            f"{actual_mode:04o}>{maximum_mode:04o}"
        )


def validate_production_runtime_boundary(
    *,
    runtime_root: Path,
    config_path: Path,
    runtime_db_path: Path,
    anchor_path: Path,
    account_home: Path,
    project_root: Path = PROJECT_ROOT,
) -> list[str]:
    errors: list[str] = []
    canonical_root = runtime_root.resolve(strict=False)
    forbidden_roots = (
        ("project_root", project_root.resolve(strict=False)),
        (
            "cloud_storage",
            (account_home / "Library" / "CloudStorage").resolve(strict=False),
        ),
        (
            "mobile_documents",
            (account_home / "Library" / "Mobile Documents").resolve(
                strict=False
            ),
        ),
        ("dropbox", (account_home / "Dropbox").resolve(strict=False)),
        (
            "google_drive",
            (account_home / "Google Drive").resolve(strict=False),
        ),
        ("onedrive", (account_home / "OneDrive").resolve(strict=False)),
    )
    for label, forbidden_root in forbidden_roots:
        if path_is_within(canonical_root, forbidden_root):
            errors.append(f"production_runtime_root_forbidden:{label}")

    validate_owned_private_path(
        runtime_root,
        label="production_runtime_root",
        expected_kind="directory",
        maximum_mode=0o700,
        errors=errors,
    )
    for label, path in (
        ("production_runtime_config", config_path),
        ("production_runtime_db", runtime_db_path),
        ("production_runtime_anchor", anchor_path),
    ):
        validate_owned_private_path(
            path,
            label=label,
            expected_kind="file",
            maximum_mode=0o600,
            errors=errors,
        )
    return errors


def resolve_runtime_authority(
    expected_runtime_db: str | None,
) -> RuntimeAuthority:
    errors: list[str] = []
    account_home = current_account_home(errors)
    production_config = fixed_production_config_path(account_home, errors)
    fixture_mode = os.environ.get(
        RUNTIME_AUTHORITY_POLICY_V1["fixture_mode_env"]
    ) == "1"
    override = os.environ.get(
        RUNTIME_AUTHORITY_POLICY_V1["fixture_override_env"]
    )
    if override is not None and not fixture_mode:
        errors.append("runtime_fixture_override_without_fixture_mode")
        config_path = production_config
        mode = "production"
        config_source = "fixed_private_runtime_root"
    elif override is not None:
        config_path = Path(override)
        mode = "fixture"
        config_source = "explicit_fixture_override"
    else:
        config_path = production_config
        mode = "production"
        config_source = "fixed_private_runtime_root"
    if config_path is None:
        return RuntimeAuthority(
            mode=mode,
            config_source=config_source,
            runtime_db_path=None,
            anchor_path=None,
            permission_policy=(
                "fixture_exempt" if mode == "fixture" else "production_enforced"
            ),
            anchor_trust=(
                RUNTIME_AUTHORITY_POLICY_V1["fixture_anchor_trust"]
                if mode == "fixture"
                else RUNTIME_AUTHORITY_POLICY_V1["production_anchor_trust"]
            ),
            errors=tuple(errors),
        )
    config_path = lexical_absolute(config_path, relative_root=PROJECT_ROOT)
    if mode == "production":
        reject_symlink_components(
            config_path, label="runtime_authority_config", errors=errors
        )
    elif config_path.is_symlink():
        errors.append("runtime_authority_config_path_uses_symlink")

    expected_config = {
        "schema_version": RUNTIME_AUTHORITY_POLICY_V1[
            "config_schema_version"
        ],
        "mode": mode,
        "runtime_database_relative_path": RUNTIME_AUTHORITY_POLICY_V1[
            "runtime_database_relative_path"
        ],
        "anchor_relative_path": RUNTIME_AUTHORITY_POLICY_V1[
            "anchor_relative_path"
        ],
    }
    config, _, config_errors = read_json_object(
        config_path, label="runtime_authority_config", required=True
    )
    errors.extend(config_errors)
    if config is not None and config != expected_config:
        errors.append("runtime_authority_config_schema_differs")

    runtime_root = config_path.parent
    runtime_db_raw = runtime_root / RUNTIME_AUTHORITY_POLICY_V1[
        "runtime_database_relative_path"
    ]
    anchor_raw = runtime_root / RUNTIME_AUTHORITY_POLICY_V1[
        "anchor_relative_path"
    ]
    if mode == "production":
        reject_symlink_components(
            runtime_db_raw, label="authoritative_runtime_db", errors=errors
        )
        reject_symlink_components(
            anchor_raw, label="authoritative_runtime_anchor", errors=errors
        )
    else:
        if runtime_db_raw.is_symlink():
            errors.append("authoritative_runtime_db_path_uses_symlink")
        if anchor_raw.is_symlink():
            errors.append("authoritative_runtime_anchor_path_uses_symlink")
    runtime_db = runtime_db_raw.resolve(strict=False)
    anchor_path = anchor_raw.resolve(strict=False)
    try:
        runtime_db.relative_to(runtime_root.resolve(strict=False))
        anchor_path.relative_to(runtime_root.resolve(strict=False))
    except ValueError:
        errors.append("runtime_authority_path_escapes_private_root")

    if mode == "production":
        if account_home is None:
            errors.append("production_runtime_account_home_unavailable")
        else:
            errors.extend(
                validate_production_runtime_boundary(
                    runtime_root=runtime_root,
                    config_path=config_path,
                    runtime_db_path=runtime_db,
                    anchor_path=anchor_path,
                    account_home=account_home,
                )
            )
        errors.append("production_trusted_anchor_binding_not_configured")

    if expected_runtime_db is not None:
        expected_raw = lexical_absolute(
            Path(expected_runtime_db), relative_root=PROJECT_ROOT
        )
        if mode == "production":
            reject_symlink_components(
                expected_raw, label="expected_runtime_db", errors=errors
            )
        elif expected_raw.is_symlink():
            errors.append("expected_runtime_db_path_uses_symlink")
        if expected_raw.resolve(strict=False) != runtime_db:
            errors.append("expected_runtime_db_mismatch")

    return RuntimeAuthority(
        mode=mode,
        config_source=config_source,
        runtime_db_path=runtime_db,
        anchor_path=anchor_path,
        permission_policy=(
            "fixture_exempt" if mode == "fixture" else "production_enforced"
        ),
        anchor_trust=(
            RUNTIME_AUTHORITY_POLICY_V1["fixture_anchor_trust"]
            if mode == "fixture"
            else RUNTIME_AUTHORITY_POLICY_V1["production_anchor_trust"]
        ),
        errors=tuple(errors),
    )


def git(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_text(args: tuple[str, ...], label: str, errors: list[str]) -> str:
    result = git(*args)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        errors.append(f"authoritative_{label}_resolution_failed:{detail or 'git_failed'}")
        return ""
    return result.stdout.decode("utf-8", errors="strict").strip()


def safe_project_path(
    relative: Any,
    *,
    label: str,
    errors: list[str],
    required_prefix: str | None = None,
) -> Path | None:
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        errors.append(f"{label}_path_invalid")
        return None
    if required_prefix is not None and not relative.startswith(required_prefix):
        errors.append(f"{label}_path_outside_allowed_prefix")
        return None
    candidate = PROJECT_ROOT / relative
    try:
        candidate.resolve(strict=False).relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        errors.append(f"{label}_path_escapes_project")
        return None
    cursor = PROJECT_ROOT
    for part in Path(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            errors.append(f"{label}_path_uses_symlink")
            return None
    return candidate


def read_json_object(
    path: Path,
    *,
    label: str,
    required: bool,
) -> tuple[dict[str, Any] | None, bool, list[str]]:
    if not path.is_file():
        return None, False, [f"{label}_missing"] if required else []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, True, [f"{label}_invalid_json:{exc}"]
    if not isinstance(value, dict):
        return None, True, [f"{label}_must_be_object"]
    return value, True, []


def resolve_authoritative_bindings(
    *,
    expected_commit: str | None,
    expected_tree: str | None,
    expected_bundle_path: str | None,
    expected_bundle_sha256: str | None,
) -> AuthoritativeBindings:
    errors: list[str] = []
    candidate_commit = git_text(("rev-parse", "HEAD"), "candidate_commit", errors)
    candidate_tree = git_text(
        ("rev-parse", "HEAD^{tree}"), "candidate_tree", errors
    )
    project_prefix = git_text(("rev-parse", "--show-prefix"), "project_prefix", errors)
    if candidate_commit and not SHA1_RE.fullmatch(candidate_commit):
        errors.append("authoritative_candidate_commit_invalid")
        candidate_commit = ""
    if candidate_tree and not SHA1_RE.fullmatch(candidate_tree):
        errors.append("authoritative_candidate_tree_invalid")
        candidate_tree = ""

    for relative in (VERIFIER_RELATIVE, CONTRACT_RELATIVE):
        path = PROJECT_ROOT / relative
        try:
            working_bytes = path.read_bytes()
        except OSError as exc:
            errors.append(f"authoritative_head_bound_file_unreadable:{relative}:{exc}")
            continue
        head_result = git("show", f"HEAD:{project_prefix}{relative}")
        if head_result.returncode != 0:
            errors.append(f"authoritative_head_bound_file_missing:{relative}")
        elif head_result.stdout != working_bytes:
            errors.append(f"authoritative_head_bound_file_differs:{relative}")

    bundle_sha256: str | None = None
    bundle_path = safe_project_path(
        FROZEN_BUNDLE_RELATIVE,
        label="authoritative_frozen_bundle",
        errors=errors,
    )
    if bundle_path is None or not bundle_path.is_file():
        errors.append("authoritative_frozen_bundle_missing")
    else:
        try:
            bundle_bytes = bundle_path.read_bytes()
        except OSError as exc:
            errors.append(f"authoritative_frozen_bundle_unreadable:{exc}")
        else:
            bundle_sha256 = sha256_bytes(bundle_bytes)
            try:
                bundle_value = json.loads(bundle_bytes)
            except (UnicodeError, json.JSONDecodeError) as exc:
                errors.append(f"authoritative_frozen_bundle_invalid_json:{exc}")
            else:
                if not isinstance(bundle_value, dict):
                    errors.append("authoritative_frozen_bundle_must_be_object")
                elif (
                    bundle_value.get("schema_version") != 1
                    or bundle_value.get("status") != "frozen"
                ):
                    errors.append("authoritative_frozen_bundle_not_frozen")
            head_bundle = git(
                "show", f"HEAD:{project_prefix}{FROZEN_BUNDLE_RELATIVE}"
            )
            if head_bundle.returncode != 0:
                errors.append("authoritative_frozen_bundle_absent_from_head")
            elif head_bundle.stdout != bundle_bytes:
                errors.append("authoritative_frozen_bundle_differs_from_head")

    actual_values = (
        ("candidate_commit", candidate_commit or None, expected_commit),
        ("candidate_tree", candidate_tree or None, expected_tree),
        (
            "frozen_bundle_path",
            FROZEN_BUNDLE_RELATIVE,
            expected_bundle_path,
        ),
        ("frozen_bundle_sha256", bundle_sha256, expected_bundle_sha256),
    )
    for label, actual, expected in actual_values:
        if expected is not None and expected != actual:
            errors.append(f"expected_{label}_mismatch")

    return AuthoritativeBindings(
        candidate_commit=candidate_commit or None,
        candidate_tree=candidate_tree or None,
        frozen_bundle_path=FROZEN_BUNDLE_RELATIVE,
        frozen_bundle_sha256=bundle_sha256,
        errors=tuple(errors),
    )


def exact_fields(
    value: dict[str, Any],
    required: Any,
    *,
    label: str,
    errors: list[str],
) -> None:
    if not isinstance(required, list) or not all(
        isinstance(field, str) and field for field in required
    ):
        errors.append(f"{label}_contract_schema_invalid")
        return
    required_set = set(required)
    if len(required_set) != len(required):
        errors.append(f"{label}_contract_schema_duplicate_fields")
        return
    missing = required_set - set(value)
    extra = set(value) - required_set
    if missing:
        errors.append(f"{label}_missing_fields:{','.join(sorted(missing))}")
    if extra:
        errors.append(f"{label}_unexpected_fields:{','.join(sorted(extra))}")


def validate_contract_machine_schema(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = contract.get("conditional_evidence_schema")
    if schema != CONDITIONAL_EVIDENCE_SCHEMA_V2:
        errors.append("conditional_evidence_machine_schema_differs")

    catalog = contract.get("conditional_gate_catalog")
    catalog_by_id = {
        item.get("id"): item
        for item in catalog
        if isinstance(catalog, list) and isinstance(item, dict)
    } if isinstance(catalog, list) else {}
    for gate_id, expected_policy in GATE_CATALOG_POLICY_V2.items():
        entry = catalog_by_id.get(gate_id)
        if not isinstance(entry, dict) or any(
            entry.get(field) != expected
            for field, expected in expected_policy.items()
        ):
            errors.append(f"conditional_gate_catalog_policy_differs:{gate_id}")

    gates = contract.get("conditional_gates")
    gates_by_id = {
        item.get("id"): item
        for item in gates
        if isinstance(gates, list) and isinstance(item, dict)
    } if isinstance(gates, list) else {}
    for (condition_id, stage), expected_cases in REQUIRED_CASES_V2.items():
        gate = gates_by_id.get(condition_id)
        actual_cases = (
            gate.get("required_acceptance_case_ids_by_stage", {}).get(stage)
            if isinstance(gate, dict)
            else None
        )
        if (
            not isinstance(actual_cases, list)
            or len(actual_cases) != len(set(actual_cases))
            or set(actual_cases) != expected_cases
        ):
            errors.append(
                f"conditional_required_case_policy_differs:{condition_id}:{stage}"
            )
    for condition_id in (
        "COND-LONGITUDINAL-EDGE",
        "COND-JAVEN-FIELD-USE",
    ):
        gate = gates_by_id.get(condition_id)
        probe = gate.get("prerequisite_probe") if isinstance(gate, dict) else None
        expected_probe_values = {
            "authority": "runtime_sqlite_event_chain",
            "table": "condition_observations",
            "event_table": RUNTIME_EVENT_CHAIN_SCHEMA_V1["event_table"],
            "producer_id": RUNTIME_EVENT_PRODUCER_ID,
            "producer_authority_source": "frozen_conditional_contract",
            "caller_producer_override_allowed": False,
        }
        if not isinstance(probe, dict) or any(
            probe.get(field) != expected
            for field, expected in expected_probe_values.items()
        ):
            errors.append(
                f"conditional_runtime_probe_policy_differs:{condition_id}"
            )
    tiingo = gates_by_id.get("COND-TIINGO-LIVE-PROBE")
    tiingo_probe = (
        tiingo.get("prerequisite_probe") if isinstance(tiingo, dict) else None
    )
    if (
        not isinstance(tiingo_probe, dict)
        or tiingo_probe.get("presence_semantics") != "environment_key_exists"
        or tiingo_probe.get("secret_value_read_allowed") is not False
    ):
        errors.append("conditional_tiingo_secret_probe_policy_differs")
    return errors


def parse_utc_timestamp(
    value: Any, *, label: str, errors: list[str]
) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label}_invalid")
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label}_invalid")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() != dt.timedelta(0):
        errors.append(f"{label}_must_be_utc")
        return None
    return parsed.astimezone(dt.timezone.utc)


def validate_sqlite_table_schema(
    connection: sqlite3.Connection,
    *,
    table: Any,
    columns: Any,
    column_types: Any,
    primary_key: Any,
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(table, str) or not SQL_IDENTIFIER_RE.fullmatch(table):
        errors.append(f"{label}_table_name_invalid")
        return False
    if (
        not isinstance(columns, list)
        or not columns
        or not all(
            isinstance(column, str) and SQL_IDENTIFIER_RE.fullmatch(column)
            for column in columns
        )
        or not isinstance(column_types, dict)
        or set(column_types) != set(columns)
        or not isinstance(primary_key, list)
    ):
        errors.append(f"{label}_table_contract_invalid")
        return False
    info = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
    if not info:
        errors.append(f"{label}_table_missing")
        return False
    actual_columns = [row[1] for row in info]
    if actual_columns != columns:
        errors.append(f"{label}_columns_invalid")
        return False
    actual_primary = [
        name
        for _, name, _, _, _, pk_order in sorted(
            info, key=lambda row: row[5] if row[5] else len(info) + row[0]
        )
        if pk_order
    ]
    if actual_primary != primary_key:
        errors.append(f"{label}_primary_key_invalid")
    for _, name, declared_type, not_null, _, pk_order in info:
        expected_type = column_types.get(name)
        if (
            not isinstance(expected_type, str)
            or declared_type.upper() != expected_type.upper()
        ):
            errors.append(f"{label}_column_type_invalid:{name}")
        if not pk_order and not not_null:
            errors.append(f"{label}_column_nullable:{name}")
    return True


def validate_sqlite_unique_constraint(
    connection: sqlite3.Connection,
    *,
    table: Any,
    columns: Any,
    label: str,
    errors: list[str],
) -> None:
    if (
        not isinstance(table, str)
        or not SQL_IDENTIFIER_RE.fullmatch(table)
        or not isinstance(columns, list)
        or not columns
        or not all(
            isinstance(column, str) and SQL_IDENTIFIER_RE.fullmatch(column)
            for column in columns
        )
    ):
        errors.append(f"{label}_unique_contract_invalid")
        return
    expected = tuple(columns)
    matches = 0
    for row in connection.execute(f'PRAGMA index_list("{table}")').fetchall():
        if len(row) < 5:
            continue
        _, index_name, unique, _, partial = row[:5]
        if not unique or partial or not isinstance(index_name, str):
            continue
        quoted_index_name = index_name.replace('"', '""')
        index_columns = tuple(
            info[2]
            for info in connection.execute(
                f'PRAGMA index_info("{quoted_index_name}")'
            ).fetchall()
        )
        if index_columns == expected:
            matches += 1
    if matches != 1:
        errors.append(f"{label}_unique_constraint_invalid")


def normalize_trigger_sql(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value.strip().lower())
    normalized = re.sub(r"\s*([(),;])\s*", r"\1", normalized)
    return normalized.removesuffix(";")


def expected_trigger_sql(spec: dict[str, str]) -> str:
    return normalize_trigger_sql(
        f"CREATE TRIGGER {spec['name']} BEFORE {spec['operation'].upper()} "
        f"ON {spec['table']} BEGIN "
        "SELECT RAISE(ABORT, 'append_only'); END"
    )


def validate_append_only_triggers(
    connection: sqlite3.Connection,
    errors: list[str],
) -> None:
    for spec in APPEND_ONLY_TRIGGER_SPECS:
        name = spec["name"]
        row = connection.execute(
            "SELECT tbl_name, sql FROM sqlite_master "
            "WHERE type = 'trigger' AND name = ?",
            (name,),
        ).fetchone()
        if row is None or not isinstance(row[1], str):
            errors.append(f"runtime_append_only_trigger_missing:{name}")
            continue
        if (
            row[0] != spec["table"]
            or normalize_trigger_sql(row[1]) != expected_trigger_sql(spec)
        ):
            errors.append(f"runtime_append_only_trigger_invalid:{name}")


def probe_append_only_statement(
    connection: sqlite3.Connection,
    *,
    statement: str,
    label: str,
    errors: list[str],
) -> None:
    connection.execute("SAVEPOINT append_only_probe")
    try:
        try:
            connection.execute(statement)
        except sqlite3.DatabaseError as exc:
            if str(exc) != "append_only":
                errors.append(f"{label}_unexpected_rejection:{exc}")
        else:
            errors.append(f"{label}_not_blocked")
    finally:
        connection.execute("ROLLBACK TO append_only_probe")
        connection.execute("RELEASE append_only_probe")


def validate_append_only_behavior(
    source: sqlite3.Connection,
    *,
    event_table: str,
    observation_table: str,
    gate_run_table: str,
    errors: list[str],
) -> None:
    probe = sqlite3.connect(":memory:")
    try:
        source.backup(probe)
        probe.execute("PRAGMA foreign_keys = ON")
        event_row = probe.execute(
            f'SELECT MIN(sequence) FROM "{event_table}"'
        ).fetchone()
        observation_row = probe.execute(
            f'SELECT MIN(source_event_seq) FROM "{observation_table}"'
        ).fetchone()
        gate_run_row = probe.execute(
            f'SELECT MIN(run_event_seq) FROM "{gate_run_table}"'
        ).fetchone()
        if event_row is None or event_row[0] is None:
            errors.append("runtime_append_only_event_probe_has_no_row")
            return
        event_seq = int(event_row[0])
        if observation_row is None or observation_row[0] is None:
            try:
                probe.execute(
                    f'INSERT INTO "{observation_table}" '
                    "(source_event_seq, condition_id, stage, ready, "
                    "source_event_hash, source_state_hash, source_anchor_hash, "
                    "observed_at, producer_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        event_seq,
                        "COND-JAVEN-FIELD-USE",
                        "human_onboarding_ready",
                        1,
                        "0" * 64,
                        "0" * 64,
                        "0" * 64,
                        "2000-01-01T00:00:00Z",
                        RUNTIME_EVENT_PRODUCER_ID,
                    ),
                )
                observation_seq = event_seq
            except sqlite3.DatabaseError as exc:
                errors.append(
                    f"runtime_append_only_observation_probe_setup_failed:{exc}"
                )
                observation_seq = None
        else:
            observation_seq = int(observation_row[0])
        if gate_run_row is None or gate_run_row[0] is None:
            try:
                probe.execute(
                    f'INSERT INTO "{gate_run_table}" '
                    "(run_event_seq, run_id, condition_id, gate_id, gate_stage, "
                    "state, source_event_seq, source_event_hash, source_state_hash, "
                    "source_anchor_hash, raw_result_path, raw_result_sha256, "
                    "completed_at, producer_id, run_event_hash, run_anchor_hash) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        event_seq,
                        "00000000-0000-4000-8000-000000000000",
                        "COND-JAVEN-FIELD-USE",
                        "GATE-JAVEN-FIELD-USE",
                        "human_onboarding",
                        "passed",
                        event_seq,
                        "0" * 64,
                        "0" * 64,
                        "0" * 64,
                        (
                            "evidence/conditional/raw/"
                            "00000000-0000-4000-8000-000000000000.json"
                        ),
                        "0" * 64,
                        "2000-01-01T00:00:00Z",
                        "EX-CONDITIONAL",
                        "0" * 64,
                        "0" * 64,
                    ),
                )
                gate_run_seq = event_seq
            except sqlite3.DatabaseError as exc:
                errors.append(
                    f"runtime_append_only_gate_run_probe_setup_failed:{exc}"
                )
                gate_run_seq = None
        else:
            gate_run_seq = int(gate_run_row[0])
        probe_append_only_statement(
            probe,
            statement=(
                f'UPDATE "{event_table}" SET event_type = event_type '
                f"WHERE sequence = {event_seq}"
            ),
            label="runtime_append_only_event_update",
            errors=errors,
        )
        probe_append_only_statement(
            probe,
            statement=(
                f'DELETE FROM "{event_table}" WHERE sequence = {event_seq}'
            ),
            label="runtime_append_only_event_delete",
            errors=errors,
        )
        if observation_seq is not None:
            probe_append_only_statement(
                probe,
                statement=(
                    f'UPDATE "{observation_table}" SET stage = stage '
                    f"WHERE source_event_seq = {observation_seq}"
                ),
                label="runtime_append_only_observation_update",
                errors=errors,
            )
            probe_append_only_statement(
                probe,
                statement=(
                    f'DELETE FROM "{observation_table}" '
                    f"WHERE source_event_seq = {observation_seq}"
                ),
                label="runtime_append_only_observation_delete",
                errors=errors,
            )
        if gate_run_seq is not None:
            probe_append_only_statement(
                probe,
                statement=(
                    f'UPDATE "{gate_run_table}" SET state = state '
                    f"WHERE run_event_seq = {gate_run_seq}"
                ),
                label="runtime_append_only_gate_run_update",
                errors=errors,
            )
            probe_append_only_statement(
                probe,
                statement=(
                    f'DELETE FROM "{gate_run_table}" '
                    f"WHERE run_event_seq = {gate_run_seq}"
                ),
                label="runtime_append_only_gate_run_delete",
                errors=errors,
            )
    finally:
        probe.close()


def validate_anchor_chain(
    anchor_path: Path | None,
    events: dict[int, dict[str, Any]],
    errors: list[str],
) -> dict[int, str]:
    if anchor_path is None or not anchor_path.is_file():
        errors.append("authoritative_runtime_anchor_missing")
        return {}
    try:
        raw = anchor_path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"authoritative_runtime_anchor_unreadable:{exc}")
        return {}
    if not raw.endswith(b"\n"):
        errors.append("authoritative_runtime_anchor_not_newline_terminated")
    lines = text.splitlines()
    if not lines or any(not line for line in lines):
        errors.append("authoritative_runtime_anchor_empty_or_blank")
        return {}
    anchor_hashes: dict[int, str] = {}
    expected_previous = ANCHOR_SCHEMA_V1["genesis_previous_anchor_hash"]
    for expected_sequence, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            errors.append(
                f"authoritative_runtime_anchor_invalid_json:{expected_sequence}"
            )
            continue
        if not isinstance(record, dict) or set(record) != set(ANCHOR_REQUIRED_V1):
            errors.append(
                f"authoritative_runtime_anchor_fields_invalid:{expected_sequence}"
            )
            continue
        try:
            if canonical_json(record) != line:
                errors.append(
                    f"authoritative_runtime_anchor_not_canonical:{expected_sequence}"
                )
        except (TypeError, ValueError):
            errors.append(
                f"authoritative_runtime_anchor_not_canonical:{expected_sequence}"
            )
        sequence = record.get("sequence")
        event = events.get(sequence) if type(sequence) is int else None
        if sequence != expected_sequence or event is None:
            errors.append(
                f"authoritative_runtime_anchor_sequence_invalid:{expected_sequence}"
            )
        if record.get("schema_version") != ANCHOR_SCHEMA_V1["schema_version"]:
            errors.append(
                f"authoritative_runtime_anchor_schema_invalid:{expected_sequence}"
            )
        if (
            not isinstance(record.get("event_hash"), str)
            or not SHA256_RE.fullmatch(record["event_hash"])
            or event is None
            or record["event_hash"] != event.get("event_hash")
        ):
            errors.append(
                f"authoritative_runtime_anchor_event_hash_invalid:{expected_sequence}"
            )
        if record.get("previous_anchor_hash") != expected_previous:
            errors.append(
                f"authoritative_runtime_anchor_prev_hash_invalid:{expected_sequence}"
            )
        anchored_at_errors: list[str] = []
        anchored_at = parse_utc_timestamp(
            record.get("anchored_at"),
            label=f"authoritative_runtime_anchor_time:{expected_sequence}",
            errors=anchored_at_errors,
        )
        errors.extend(anchored_at_errors)
        event_time_errors: list[str] = []
        event_time = (
            parse_utc_timestamp(
                event.get("occurred_at"),
                label=f"authoritative_runtime_event_time:{expected_sequence}",
                errors=event_time_errors,
            )
            if event is not None
            else None
        )
        errors.extend(event_time_errors)
        if (
            anchored_at is not None
            and event_time is not None
            and anchored_at < event_time
        ):
            errors.append(
                f"authoritative_runtime_anchor_predates_event:{expected_sequence}"
            )
        material = {
            "schema_version": record.get("schema_version"),
            "sequence": sequence,
            "event_hash": record.get("event_hash"),
            "anchored_at": record.get("anchored_at"),
            "previous_anchor_hash": record.get("previous_anchor_hash"),
        }
        try:
            computed_hash = sha256_bytes(
                canonical_json(material).encode("utf-8")
            )
        except (TypeError, ValueError):
            errors.append(
                f"authoritative_runtime_anchor_hash_material_invalid:"
                f"{expected_sequence}"
            )
            computed_hash = ""
        anchor_hash = record.get("anchor_hash")
        if (
            not isinstance(anchor_hash, str)
            or not SHA256_RE.fullmatch(anchor_hash)
            or anchor_hash != computed_hash
        ):
            errors.append(
                f"authoritative_runtime_anchor_hash_invalid:{expected_sequence}"
            )
        else:
            anchor_hashes[expected_sequence] = anchor_hash
            expected_previous = anchor_hash
    if events:
        tail_sequence = max(events)
        tail_event_hash = events[tail_sequence].get("event_hash")
        try:
            last_record = json.loads(lines[-1]) if lines else {}
        except json.JSONDecodeError:
            last_record = {}
        if (
            not isinstance(last_record, dict)
            or last_record.get("sequence") != tail_sequence
            or last_record.get("event_hash") != tail_event_hash
        ):
            errors.append("authoritative_runtime_anchor_tail_mismatch")
    return anchor_hashes


def load_runtime_ledger(runtime_authority: RuntimeAuthority) -> RuntimeLedger:
    authority = "runtime_sqlite_event_chain"
    runtime_db = runtime_authority.runtime_db_path
    errors: list[str] = list(runtime_authority.errors)
    if runtime_db is None or not runtime_db.is_file():
        return RuntimeLedger(False, {}, {}, tuple(errors))

    schema = RUNTIME_EVENT_CHAIN_SCHEMA_V1
    event_table = schema["event_table"]
    observation_table = schema["observation_table"]
    gate_run_table = schema["gate_run_table"]
    try:
        connection = sqlite3.connect(f"file:{runtime_db}?mode=ro", uri=True)
        try:
            connection.execute("PRAGMA query_only = ON")
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if integrity != ("ok",):
                errors.append("authoritative_runtime_integrity_check_failed")
            event_schema_ok = validate_sqlite_table_schema(
                connection,
                table=event_table,
                columns=schema.get("event_columns"),
                column_types=schema.get("event_column_types"),
                primary_key=schema.get("event_primary_key"),
                label="runtime_event",
                errors=errors,
            )
            observation_schema_ok = validate_sqlite_table_schema(
                connection,
                table=observation_table,
                columns=schema.get("observation_columns"),
                column_types=schema.get("observation_column_types"),
                primary_key=schema.get("observation_primary_key"),
                label="runtime_observation",
                errors=errors,
            )
            gate_run_schema_ok = validate_sqlite_table_schema(
                connection,
                table=gate_run_table,
                columns=schema.get("gate_run_columns"),
                column_types=schema.get("gate_run_column_types"),
                primary_key=schema.get("gate_run_primary_key"),
                label="runtime_gate_run",
                errors=errors,
            )
            if gate_run_schema_ok:
                validate_sqlite_unique_constraint(
                    connection,
                    table=gate_run_table,
                    columns=schema.get("gate_run_unique"),
                    label="runtime_gate_run",
                    errors=errors,
                )
            validate_append_only_triggers(connection, errors)
            if not (
                event_schema_ok
                and observation_schema_ok
                and gate_run_schema_ok
            ):
                return RuntimeLedger(True, {}, {}, tuple(errors))

            observation_foreign_keys = connection.execute(
                f'PRAGMA foreign_key_list("{observation_table}")'
            ).fetchall()
            if not any(
                row[2] == event_table
                and row[3] == "source_event_seq"
                and row[4] == "sequence"
                for row in observation_foreign_keys
            ):
                errors.append("runtime_observation_event_foreign_key_missing")
            gate_run_foreign_keys = connection.execute(
                f'PRAGMA foreign_key_list("{gate_run_table}")'
            ).fetchall()
            if not any(
                row[2] == event_table
                and row[3] == "run_event_seq"
                and row[4] == "sequence"
                for row in gate_run_foreign_keys
            ):
                errors.append("runtime_gate_run_event_foreign_key_missing")

            event_rows = connection.execute(
                f'SELECT sequence, event_type, producer_id, occurred_at, '
                f'payload_json, prev_hash, event_hash FROM "{event_table}" '
                "ORDER BY sequence"
            ).fetchall()
            observation_rows = connection.execute(
                f'SELECT source_event_seq, condition_id, stage, ready, '
                f'source_event_hash, source_state_hash, source_anchor_hash, '
                f'observed_at, producer_id '
                f'FROM "{observation_table}" ORDER BY source_event_seq'
            ).fetchall()
            gate_run_rows = connection.execute(
                f'SELECT run_event_seq, run_id, condition_id, gate_id, '
                f'gate_stage, state, source_event_seq, source_event_hash, '
                f'source_state_hash, source_anchor_hash, raw_result_path, '
                f'raw_result_sha256, completed_at, producer_id, run_event_hash, '
                f'run_anchor_hash FROM "{gate_run_table}" ORDER BY run_event_seq'
            ).fetchall()
            validate_append_only_behavior(
                connection,
                event_table=event_table,
                observation_table=observation_table,
                gate_run_table=gate_run_table,
                errors=errors,
            )
        finally:
            connection.close()
    except sqlite3.Error as exc:
        errors.append(f"authoritative_runtime_probe_failed:{exc}")
        return RuntimeLedger(True, {}, {}, tuple(errors))

    genesis = schema.get("genesis_prev_hash")
    payload_required_by_type = schema.get("payload_required_by_type")
    event_types = schema.get("event_types")
    if not isinstance(genesis, str) or not SHA256_RE.fullmatch(genesis):
        errors.append("runtime_genesis_hash_contract_invalid")
        genesis = ""
    if (
        not isinstance(payload_required_by_type, dict)
        or not isinstance(event_types, list)
        or set(payload_required_by_type) != set(event_types)
        or not all(
            isinstance(fields, list)
            and fields
            and all(isinstance(field, str) and field for field in fields)
            for fields in payload_required_by_type.values()
        )
    ):
        errors.append("runtime_payload_contract_invalid")
        payload_required_by_type = {}

    runtime_condition_ids = {
        "COND-LONGITUDINAL-EDGE",
        "COND-JAVEN-FIELD-USE",
    }
    state: dict[str, dict[str, Any]] = {}
    latest_observation_sequence: dict[str, int] = {}
    events: dict[int, dict[str, Any]] = {}
    expected_prev = genesis
    condition_event_count = 0
    gate_run_event_count = 0
    seen_gate_run_ids: set[str] = set()
    for index, row in enumerate(event_rows, start=1):
        (
            sequence,
            event_type,
            producer_id,
            occurred_at,
            payload_json,
            prev_hash,
            event_hash,
        ) = row
        if type(sequence) is not int or sequence != index:
            errors.append("runtime_event_sequence_invalid")
            continue
        if not isinstance(payload_json, str):
            errors.append(f"runtime_event_payload_invalid:{sequence}")
            continue
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError:
            errors.append(f"runtime_event_payload_invalid_json:{sequence}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"runtime_event_payload_not_object:{sequence}")
            continue
        try:
            if canonical_json(payload) != payload_json:
                errors.append(f"runtime_event_payload_not_canonical:{sequence}")
        except (TypeError, ValueError):
            errors.append(f"runtime_event_payload_not_canonical:{sequence}")
        occurred_time = parse_utc_timestamp(
            occurred_at,
            label=f"runtime_event_occurred_at:{sequence}",
            errors=errors,
        )
        if prev_hash != expected_prev:
            errors.append(f"runtime_event_prev_hash_invalid:{sequence}")
        envelope = {
            "sequence": sequence,
            "event_type": event_type,
            "producer_id": producer_id,
            "occurred_at": occurred_at,
            "payload": payload,
            "prev_hash": prev_hash,
        }
        try:
            computed_event_hash = sha256_bytes(
                canonical_json(envelope).encode("utf-8")
            )
        except (TypeError, ValueError):
            errors.append(f"runtime_event_hash_material_invalid:{sequence}")
            computed_event_hash = ""
        if (
            not isinstance(event_hash, str)
            or not SHA256_RE.fullmatch(event_hash)
            or event_hash != computed_event_hash
        ):
            errors.append(f"runtime_event_hash_invalid:{sequence}")
        expected_prev = event_hash if isinstance(event_hash, str) else ""

        source_state_hash: str | None = None
        is_condition_event = event_type == "condition_observation"
        is_gate_run_event = event_type == "conditional_gate_run"
        latest_source_sequence: int | None = None
        if is_condition_event:
            condition_event_count += 1
            required_fields = payload_required_by_type.get(event_type, [])
            if set(payload) != set(required_fields):
                errors.append(f"runtime_event_payload_fields_invalid:{sequence}")
            condition_id = payload.get("condition_id")
            if (
                not isinstance(condition_id, str)
                or condition_id not in runtime_condition_ids
            ):
                errors.append(f"runtime_event_condition_unknown:{sequence}")
            if (
                producer_id != RUNTIME_EVENT_PRODUCER_ID
                or payload.get("producer_id") != RUNTIME_EVENT_PRODUCER_ID
            ):
                errors.append(f"runtime_event_producer_not_authorized:{sequence}")
            if (
                not isinstance(payload.get("stage"), str)
                or not payload.get("stage")
                or type(payload.get("ready")) is not bool
                or payload.get("observed_at") != occurred_at
            ):
                errors.append(
                    f"runtime_event_observation_payload_invalid:{sequence}"
                )
            for field, pattern in (
                ("candidate_commit", SHA1_RE),
                ("candidate_tree", SHA1_RE),
                ("frozen_bundle_sha256", SHA256_RE),
            ):
                value = payload.get(field)
                if not isinstance(value, str) or not pattern.fullmatch(value):
                    errors.append(f"runtime_event_{field}_invalid:{sequence}")
            if payload.get("frozen_bundle_path") != FROZEN_BUNDLE_RELATIVE:
                errors.append(
                    f"runtime_event_frozen_bundle_path_invalid:{sequence}"
                )
            if isinstance(condition_id, str):
                state[condition_id] = payload
                latest_observation_sequence[condition_id] = sequence
            state_material = {
                "through_sequence": sequence,
                "through_event_hash": event_hash,
                "condition_states": [state[key] for key in sorted(state)],
            }
            try:
                source_state_hash = sha256_bytes(
                    canonical_json(state_material).encode("utf-8")
                )
            except (TypeError, ValueError):
                errors.append(
                    f"runtime_event_state_hash_material_invalid:{sequence}"
                )
                source_state_hash = None
        elif is_gate_run_event:
            gate_run_event_count += 1
            required_fields = payload_required_by_type.get(event_type, [])
            if set(payload) != set(required_fields):
                errors.append(
                    f"runtime_gate_run_payload_fields_invalid:{sequence}"
                )
            condition_id = payload.get("condition_id")
            gate_id = payload.get("gate_id")
            expected_gate_id = (
                MANDATORY_GATE_BY_CONDITION_V2.get(condition_id)
                if isinstance(condition_id, str)
                else None
            )
            catalog_policy = (
                GATE_CATALOG_POLICY_V2.get(gate_id, {})
                if isinstance(gate_id, str)
                else {}
            )
            if expected_gate_id is None or gate_id != expected_gate_id:
                errors.append(f"runtime_gate_run_gate_binding_invalid:{sequence}")
            expected_producer = catalog_policy.get("evidence_producer_id")
            if (
                not isinstance(expected_producer, str)
                or producer_id != expected_producer
                or payload.get("producer_id") != expected_producer
            ):
                errors.append(
                    f"runtime_gate_run_producer_not_authorized:{sequence}"
                )
            exact_string_set(
                payload.get("executor_ids"),
                set(catalog_policy.get("executor_ids", [])),
                label=f"runtime_gate_run_executor_binding:{sequence}",
                errors=errors,
            )
            gate_stage = payload.get("gate_stage")
            required_cases = set(
                REQUIRED_CASES_V2.get((condition_id, gate_stage), set())
                if isinstance(condition_id, str)
                and isinstance(gate_stage, str)
                else set()
            )
            if not required_cases:
                errors.append(
                    f"runtime_gate_run_required_case_set_empty:{sequence}"
                )
            exact_string_set(
                payload.get("acceptance_case_ids"),
                required_cases,
                label=f"runtime_gate_run_case_binding:{sequence}",
                errors=errors,
            )
            if (
                not isinstance(payload.get("state"), str)
                or payload.get("state")
                not in {"passed", "failed", "inconclusive"}
            ):
                errors.append(f"runtime_gate_run_state_invalid:{sequence}")

            run_id = payload.get("run_id")
            try:
                parsed_run_id = (
                    uuid.UUID(run_id) if isinstance(run_id, str) else None
                )
            except ValueError:
                parsed_run_id = None
            if (
                parsed_run_id is None
                or parsed_run_id.version != 4
                or str(parsed_run_id) != run_id
            ):
                errors.append(f"runtime_gate_run_id_invalid:{sequence}")
            elif run_id in seen_gate_run_ids:
                errors.append(f"runtime_gate_run_id_duplicate:{run_id}")
            else:
                seen_gate_run_ids.add(run_id)

            for field, pattern in (
                ("candidate_commit", SHA1_RE),
                ("candidate_tree", SHA1_RE),
                ("frozen_bundle_sha256", SHA256_RE),
                ("source_event_hash", SHA256_RE),
                ("source_state_hash", SHA256_RE),
                ("source_anchor_hash", SHA256_RE),
                ("raw_result_sha256", SHA256_RE),
            ):
                value = payload.get(field)
                if not isinstance(value, str) or not pattern.fullmatch(value):
                    errors.append(
                        f"runtime_gate_run_{field}_invalid:{sequence}"
                    )
            if payload.get("frozen_bundle_path") != FROZEN_BUNDLE_RELATIVE:
                errors.append(
                    f"runtime_gate_run_frozen_bundle_path_invalid:{sequence}"
                )
            expected_raw_path = (
                f"{catalog_policy.get('raw_result_path_prefix')}{run_id}.json"
                if isinstance(run_id, str)
                and isinstance(
                    catalog_policy.get("raw_result_path_prefix"), str
                )
                else None
            )
            if payload.get("raw_result_path") != expected_raw_path:
                errors.append(
                    f"runtime_gate_run_raw_path_invalid:{sequence}"
                )
            completed_time = parse_utc_timestamp(
                payload.get("completed_at"),
                label=f"runtime_gate_run_completed_at:{sequence}",
                errors=errors,
            )
            if payload.get("completed_at") != occurred_at:
                errors.append(
                    f"runtime_gate_run_completed_at_mismatch:{sequence}"
                )
            if (
                completed_time is not None
                and occurred_time is not None
                and completed_time != occurred_time
            ):
                errors.append(
                    f"runtime_gate_run_time_binding_invalid:{sequence}"
                )

            source_event_seq = payload.get("source_event_seq")
            if condition_id == "COND-TIINGO-LIVE-PROBE":
                if (
                    source_event_seq != 0
                    or payload.get("source_event_hash")
                    != payload.get("source_state_hash")
                    or payload.get("source_event_hash")
                    != payload.get("source_anchor_hash")
                ):
                    errors.append(
                        f"runtime_gate_run_environment_source_invalid:{sequence}"
                    )
            else:
                latest_source_sequence = (
                    latest_observation_sequence.get(condition_id)
                    if isinstance(condition_id, str)
                    else None
                )
                if (
                    type(source_event_seq) is not int
                    or source_event_seq < 1
                    or source_event_seq >= sequence
                    or latest_source_sequence is None
                    or source_event_seq != latest_source_sequence
                ):
                    errors.append(
                        f"runtime_gate_run_not_latest_observation:{sequence}"
                    )
        elif not isinstance(producer_id, str) or not producer_id:
            errors.append(f"runtime_main_event_producer_invalid:{sequence}")

        events[sequence] = {
            "payload": payload,
            "event_hash": event_hash,
            "source_state_hash": source_state_hash,
            "producer_id": producer_id,
            "occurred_at": occurred_at,
            "occurred_time": occurred_time,
            "is_condition_event": is_condition_event,
            "is_gate_run_event": is_gate_run_event,
            "latest_source_sequence": latest_source_sequence,
        }

    if condition_event_count != len(observation_rows):
        errors.append("runtime_event_observation_cardinality_mismatch")
    if gate_run_event_count != len(gate_run_rows):
        errors.append("runtime_event_gate_run_cardinality_mismatch")
    anchor_hashes = validate_anchor_chain(
        runtime_authority.anchor_path, events, errors
    )

    observations_by_condition: dict[str, dict[str, Any]] = {}
    seen_observation_sequences: set[int] = set()
    for row in observation_rows:
        (
            source_event_seq,
            condition_id,
            stage,
            ready_value,
            source_event_hash,
            source_state_hash,
            source_anchor_hash,
            observed_at,
            producer_id,
        ) = row
        if (
            type(source_event_seq) is not int
            or source_event_seq in seen_observation_sequences
        ):
            errors.append("runtime_observation_event_reference_invalid")
            continue
        seen_observation_sequences.add(source_event_seq)
        event = events.get(source_event_seq)
        if event is None or not event.get("is_condition_event"):
            errors.append(
                f"runtime_observation_event_reference_missing:{source_event_seq}"
            )
            continue
        payload = event["payload"]
        if type(ready_value) is not int or ready_value not in {0, 1}:
            errors.append(f"runtime_observation_ready_invalid:{source_event_seq}")
            ready = False
        else:
            ready = bool(ready_value)
        expected_projection = (
            payload.get("condition_id"),
            payload.get("stage"),
            payload.get("ready"),
            event["event_hash"],
            event["source_state_hash"],
            anchor_hashes.get(source_event_seq),
            payload.get("observed_at"),
            event["producer_id"],
        )
        actual_projection = (
            condition_id,
            stage,
            ready,
            source_event_hash,
            source_state_hash,
            source_anchor_hash,
            observed_at,
            producer_id,
        )
        if actual_projection != expected_projection:
            errors.append(f"runtime_observation_projection_invalid:{source_event_seq}")
        observation = {
            "authority": authority,
            "condition_id": condition_id,
            "source_event_seq": source_event_seq,
            "source_event_hash": source_event_hash,
            "source_state_hash": source_state_hash,
            "source_anchor_hash": source_anchor_hash,
            "observed_at": observed_at,
            "producer_id": producer_id,
            "stage": stage,
            "ready": ready,
            "_event_payload": payload,
        }
        if isinstance(condition_id, str):
            observations_by_condition[condition_id] = observation
        else:
            errors.append(
                f"runtime_observation_condition_id_invalid:{source_event_seq}"
            )

    gate_runs_by_id: dict[str, dict[str, Any]] = {}
    for sequence, event in events.items():
        if not event.get("is_gate_run_event"):
            continue
        payload = event["payload"]
        source_event_seq = payload.get("source_event_seq")
        if (
            type(source_event_seq) is int
            and source_event_seq > 0
        ):
            source_event = events.get(source_event_seq)
            expected_source = (
                source_event.get("event_hash") if source_event else None,
                source_event.get("source_state_hash") if source_event else None,
                anchor_hashes.get(source_event_seq),
            )
            actual_source = (
                payload.get("source_event_hash"),
                payload.get("source_state_hash"),
                payload.get("source_anchor_hash"),
            )
            if (
                source_event is None
                or not source_event.get("is_condition_event")
                or source_event["payload"].get("condition_id")
                != payload.get("condition_id")
                or actual_source != expected_source
            ):
                errors.append(
                    f"runtime_gate_run_source_binding_invalid:{sequence}"
                )
            elif any(
                source_event["payload"].get(field) != payload.get(field)
                for field in (
                    "candidate_commit",
                    "candidate_tree",
                    "frozen_bundle_path",
                    "frozen_bundle_sha256",
                )
            ):
                errors.append(
                    f"runtime_gate_run_source_candidate_mismatch:{sequence}"
                )
            if (
                source_event is not None
                and source_event.get("occurred_time") is not None
                and event.get("occurred_time") is not None
                and event["occurred_time"] < source_event["occurred_time"]
            ):
                errors.append(
                    f"runtime_gate_run_predates_observation:{sequence}"
                )
        run_id = payload.get("run_id")
        receipt = {
            "authority": "runtime_sqlite_gate_run_receipt",
            "run_event_seq": sequence,
            "run_event_hash": event.get("event_hash"),
            "run_anchor_hash": anchor_hashes.get(sequence),
            "run_id": run_id,
            "condition_id": payload.get("condition_id"),
            "gate_id": payload.get("gate_id"),
            "gate_stage": payload.get("gate_stage"),
            "state": payload.get("state"),
            "source_event_seq": payload.get("source_event_seq"),
            "source_event_hash": payload.get("source_event_hash"),
            "source_state_hash": payload.get("source_state_hash"),
            "source_anchor_hash": payload.get("source_anchor_hash"),
            "raw_result_path": payload.get("raw_result_path"),
            "raw_result_sha256": payload.get("raw_result_sha256"),
            "completed_at": payload.get("completed_at"),
        }
        if isinstance(run_id, str) and run_id not in gate_runs_by_id:
            gate_runs_by_id[run_id] = {
                "receipt": receipt,
                "payload": payload,
            }

    seen_gate_run_sequences: set[int] = set()
    seen_projected_run_ids: set[str] = set()
    for row in gate_run_rows:
        (
            run_event_seq,
            run_id,
            condition_id,
            gate_id,
            gate_stage,
            state_value,
            source_event_seq,
            source_event_hash,
            source_state_hash,
            source_anchor_hash,
            raw_result_path,
            raw_result_sha256,
            completed_at,
            producer_id,
            run_event_hash,
            run_anchor_hash,
        ) = row
        if (
            type(run_event_seq) is not int
            or run_event_seq in seen_gate_run_sequences
        ):
            errors.append("runtime_gate_run_event_reference_invalid")
            continue
        seen_gate_run_sequences.add(run_event_seq)
        if not isinstance(run_id, str) or run_id in seen_projected_run_ids:
            errors.append(f"runtime_gate_run_projection_duplicate_run_id:{run_id}")
        else:
            seen_projected_run_ids.add(run_id)
        event = events.get(run_event_seq)
        if event is None or not event.get("is_gate_run_event"):
            errors.append(
                f"runtime_gate_run_event_reference_missing:{run_event_seq}"
            )
            continue
        payload = event["payload"]
        expected_projection = (
            payload.get("run_id"),
            payload.get("condition_id"),
            payload.get("gate_id"),
            payload.get("gate_stage"),
            payload.get("state"),
            payload.get("source_event_seq"),
            payload.get("source_event_hash"),
            payload.get("source_state_hash"),
            payload.get("source_anchor_hash"),
            payload.get("raw_result_path"),
            payload.get("raw_result_sha256"),
            payload.get("completed_at"),
            payload.get("producer_id"),
            event.get("event_hash"),
            anchor_hashes.get(run_event_seq),
        )
        actual_projection = (
            run_id,
            condition_id,
            gate_id,
            gate_stage,
            state_value,
            source_event_seq,
            source_event_hash,
            source_state_hash,
            source_anchor_hash,
            raw_result_path,
            raw_result_sha256,
            completed_at,
            producer_id,
            run_event_hash,
            run_anchor_hash,
        )
        if actual_projection != expected_projection:
            errors.append(
                f"runtime_gate_run_projection_invalid:{run_event_seq}"
            )

    return RuntimeLedger(
        True,
        observations_by_condition,
        gate_runs_by_id,
        tuple(errors),
    )


def runtime_observation(
    gate: dict[str, Any],
    ledger: RuntimeLedger,
    bindings: AuthoritativeBindings,
) -> tuple[bool, str | None, dict[str, Any], list[str]]:
    authority = "runtime_sqlite_event_chain"
    errors = list(ledger.errors)
    if not ledger.available:
        return False, None, {"source": "runtime_database_absent"}, errors
    latest = ledger.observations_by_condition.get(gate.get("id"))
    if latest is None:
        return False, None, {"source": authority}, errors
    event_payload = latest.get("_event_payload", {})
    for field, expected in (
        ("candidate_commit", bindings.candidate_commit),
        ("candidate_tree", bindings.candidate_tree),
        ("frozen_bundle_path", bindings.frozen_bundle_path),
        ("frozen_bundle_sha256", bindings.frozen_bundle_sha256),
    ):
        if expected is None or event_payload.get(field) != expected:
            errors.append(f"runtime_observation_{field}_mismatch")
    ready_when = gate.get("prerequisite_probe", {}).get("ready_when", {})
    stage = latest.get("stage")
    stage_matches = (
        stage == ready_when.get("stage")
        if "stage" in ready_when
        else isinstance(stage, str)
        and stage in set(ready_when.get("stage_in", []))
    )
    ready = (
        not errors
        and latest.get("ready") is ready_when.get("ready")
        and stage_matches
    )
    public = {
        key: value
        for key, value in latest.items()
        if not key.startswith("_")
    }
    public["source"] = authority
    return ready, stage, public, errors


def deterministic_presence_observation(
    gate: dict[str, Any],
    *,
    present: bool,
    bindings: AuthoritativeBindings,
) -> dict[str, Any]:
    material = {
        "authority": "process_environment_presence",
        "condition_id": gate.get("id"),
        "present": present,
        "candidate_commit": bindings.candidate_commit,
        "candidate_tree": bindings.candidate_tree,
        "frozen_bundle_path": bindings.frozen_bundle_path,
        "frozen_bundle_sha256": bindings.frozen_bundle_sha256,
    }
    fingerprint = sha256_bytes(canonical_json(material).encode("utf-8"))
    return {
        "authority": "process_environment_presence",
        "condition_id": gate.get("id"),
        "source_event_seq": 0,
        "source_event_hash": fingerprint,
        "source_state_hash": fingerprint,
        "source_anchor_hash": fingerprint,
        "observed_at": None,
    }


def observe_prerequisite(
    gate: dict[str, Any],
    contract: dict[str, Any],
    runtime_ledger: RuntimeLedger,
    bindings: AuthoritativeBindings,
) -> tuple[bool, str | None, dict[str, Any], list[str]]:
    authority = gate.get("prerequisite_probe", {}).get("authority")
    if authority == "process_environment_presence":
        present = "TIINGO_API_TOKEN" in os.environ
        observation = deterministic_presence_observation(
            gate, present=present, bindings=bindings
        )
        observation.update(
            {
                "source": authority,
                "present": present,
                "secret_value_read": False,
            }
        )
        return present, "live_probe" if present else None, observation, []
    if authority == "frozen_contract_scope":
        forbidden_scope = "真实资金、live broker、实盘凭据或自动下单"
        satisfied = forbidden_scope in set(contract.get("non_goals", []))
        return satisfied, "scope" if satisfied else None, {
            "source": authority,
            "forbidden_scope_present": satisfied,
        }, []
    if authority == "runtime_sqlite_event_chain":
        return runtime_observation(gate, runtime_ledger, bindings)
    return False, None, {"source": authority}, [
        "unknown_prerequisite_authority"
    ]


def required_stage(gate_id: str, observed_stage: str | None) -> str | None:
    if gate_id == "COND-TIINGO-LIVE-PROBE":
        return "live_probe"
    if gate_id == "COND-LONGITUDINAL-EDGE":
        return "future_window"
    if gate_id == "COND-JAVEN-FIELD-USE":
        return {
            "human_onboarding_ready": "human_onboarding",
            "longitudinal_window_ready": "longitudinal",
        }.get(observed_stage)
    return observed_stage


def expected_observation_binding(
    observation: dict[str, Any],
) -> dict[str, Any] | None:
    if any(field not in observation for field in OBSERVATION_REQUIRED_V2):
        return None
    return {
        field: observation[field] for field in OBSERVATION_REQUIRED_V2
    }


def exact_string_set(
    actual: Any,
    expected: set[str],
    *,
    label: str,
    errors: list[str],
) -> None:
    if (
        not isinstance(actual, list)
        or not all(isinstance(item, str) and item for item in actual)
        or len(actual) != len(set(actual))
        or set(actual) != expected
    ):
        errors.append(f"{label}_mismatch")


def validate_binding_fields(
    record: dict[str, Any],
    bindings: AuthoritativeBindings,
    *,
    label: str,
    errors: list[str],
) -> None:
    expected = {
        "candidate_commit": bindings.candidate_commit,
        "candidate_tree": bindings.candidate_tree,
        "frozen_bundle_path": bindings.frozen_bundle_path,
        "frozen_bundle_sha256": bindings.frozen_bundle_sha256,
    }
    patterns = {
        "candidate_commit": SHA1_RE,
        "candidate_tree": SHA1_RE,
        "frozen_bundle_sha256": SHA256_RE,
    }
    for field, expected_value in expected.items():
        actual = record.get(field)
        pattern = patterns.get(field)
        if pattern is not None and (
            not isinstance(actual, str) or not pattern.fullmatch(actual)
        ):
            errors.append(f"{label}_{field}_invalid")
        if expected_value is None or actual != expected_value:
            errors.append(f"{label}_{field}_mismatch")


def validate_hash_map(
    value: Any,
    *,
    label: str,
    artifact_prefix: Any,
    errors: list[str],
) -> None:
    if (
        not isinstance(value, dict)
        or not value
        or not isinstance(artifact_prefix, str)
        or not artifact_prefix
    ):
        errors.append(f"{label}_invalid")
        return
    for relative, expected_hash in value.items():
        path = safe_project_path(
            relative,
            label=label,
            errors=errors,
            required_prefix=artifact_prefix,
        )
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(
            expected_hash
        ):
            errors.append(f"{label}_sha256_invalid")
            continue
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"{label}_artifact_missing")
        elif sha256_file(path) != expected_hash:
            errors.append(f"{label}_artifact_hash_mismatch")


def run_id_replayed(
    run_id: str,
    *,
    current_evidence_path: str,
    conditional_gates: list[dict[str, Any]],
) -> bool:
    for other_gate in conditional_gates:
        relative = other_gate.get("evidence_path")
        if not isinstance(relative, str) or relative == current_evidence_path:
            continue
        other_errors: list[str] = []
        path = safe_project_path(
            relative, label="other_gate_evidence", errors=other_errors
        )
        if path is None or not path.is_file():
            continue
        try:
            other = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if isinstance(other, dict) and other.get("run_id") == run_id:
            return True
    return False


def validate_gate_evidence(
    gate: dict[str, Any],
    all_conditional_gates: list[dict[str, Any]],
    gate_catalog: dict[str, dict[str, Any]],
    evidence_schema: dict[str, Any],
    evidence: dict[str, Any],
    stage: str | None,
    observation: dict[str, Any],
    bindings: AuthoritativeBindings,
    runtime_ledger: RuntimeLedger,
    now: dt.datetime,
) -> list[str]:
    errors: list[str] = []
    evidence_schema = CONDITIONAL_EVIDENCE_SCHEMA_V2
    exact_fields(
        evidence,
        list(EVIDENCE_REQUIRED_V2),
        label="gate_evidence",
        errors=errors,
    )
    if "prerequisite_ready" in evidence:
        errors.append("gate_evidence_must_not_report_prerequisite_readiness")
    if evidence.get("schema_version") != evidence_schema.get("schema_version"):
        errors.append("gate_evidence_schema_version_mismatch")

    mandatory_gate = MANDATORY_GATE_BY_CONDITION_V2.get(gate.get("id"))
    catalog_entry = gate_catalog.get(mandatory_gate, {})
    catalog_policy = GATE_CATALOG_POLICY_V2.get(mandatory_gate, {})
    expected_stage = required_stage(gate.get("id", ""), stage)
    if evidence.get("condition_id") != gate.get("id"):
        errors.append("condition_id_mismatch")
    if evidence.get("gate_id") != mandatory_gate:
        errors.append("gate_id_mismatch")
    if evidence.get("gate_stage") != expected_stage:
        errors.append("gate_stage_mismatch")
    evidence_state = evidence.get("state")
    if (
        not isinstance(evidence_state, str)
        or evidence_state not in set(evidence_schema.get("state_enum", []))
    ):
        errors.append("state_not_allowed")
    validate_binding_fields(
        evidence, bindings, label="gate_evidence", errors=errors
    )

    expected_producer = catalog_policy.get("evidence_producer_id")
    if (
        not isinstance(expected_producer, str)
        or catalog_policy.get("producer_authority_source")
        != "frozen_conditional_gate_catalog"
        or catalog_policy.get("caller_producer_override_allowed") is not False
        or any(
            catalog_entry.get(field) != expected
            for field, expected in catalog_policy.items()
        )
    ):
        errors.append("gate_producer_authority_contract_invalid")
    if evidence.get("producer_id") != expected_producer:
        errors.append("gate_evidence_producer_not_authorized")

    expected_executors = set(catalog_policy.get("executor_ids", []))
    exact_string_set(
        evidence.get("executor_ids"),
        expected_executors,
        label="gate_executor_binding",
        errors=errors,
    )
    required_cases = set(
        REQUIRED_CASES_V2.get((gate.get("id"), expected_stage or ""), set())
    )
    if not required_cases:
        errors.append("gate_required_case_set_empty")
    exact_string_set(
        evidence.get("acceptance_case_ids"),
        required_cases,
        label="gate_acceptance_case_binding",
        errors=errors,
    )

    run_id = evidence.get("run_id")
    try:
        parsed_run_id = uuid.UUID(run_id) if isinstance(run_id, str) else None
    except ValueError:
        parsed_run_id = None
    if (
        parsed_run_id is None
        or parsed_run_id.version != 4
        or str(parsed_run_id) != run_id
    ):
        errors.append("gate_run_id_invalid")
    elif run_id_replayed(
        run_id,
        current_evidence_path=gate.get("evidence_path", ""),
        conditional_gates=all_conditional_gates,
    ):
        errors.append("gate_run_id_replayed")

    observation_schema = evidence_schema.get("observation_schema", {})
    evidence_observation = evidence.get("observation")
    expected_observation = expected_observation_binding(observation)
    if not isinstance(evidence_observation, dict):
        errors.append("gate_observation_binding_invalid")
    else:
        exact_fields(
            evidence_observation,
            observation_schema.get("required"),
            label="gate_observation",
            errors=errors,
        )
        if expected_observation is None or evidence_observation != expected_observation:
            errors.append("gate_observation_binding_mismatch")

    receipt_schema = evidence_schema.get("run_receipt_schema", {})
    evidence_receipt = evidence.get("run_receipt")
    if not isinstance(evidence_receipt, dict):
        errors.append("gate_run_receipt_invalid")
    else:
        exact_fields(
            evidence_receipt,
            receipt_schema.get("required"),
            label="gate_run_receipt",
            errors=errors,
        )
        if evidence_receipt.get("authority") != receipt_schema.get("authority"):
            errors.append("gate_run_receipt_authority_invalid")
        run_event_seq = evidence_receipt.get("run_event_seq")
        if (
            type(run_event_seq) is not int
            or run_event_seq
            < receipt_schema.get("runtime_event_seq_minimum", 1)
        ):
            errors.append("gate_run_receipt_event_seq_invalid")
        for field in (
            "run_event_hash",
            "run_anchor_hash",
            "source_event_hash",
            "source_state_hash",
            "source_anchor_hash",
            "raw_result_sha256",
        ):
            value = evidence_receipt.get(field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                errors.append(f"gate_run_receipt_{field}_invalid")

        expected_receipt_bindings = {
            "run_id": evidence.get("run_id"),
            "condition_id": evidence.get("condition_id"),
            "gate_id": evidence.get("gate_id"),
            "gate_stage": evidence.get("gate_stage"),
            "state": evidence.get("state"),
            "raw_result_path": evidence.get("raw_result_path"),
            "raw_result_sha256": evidence.get("raw_result_sha256"),
            "completed_at": evidence.get("completed_at"),
        }
        if isinstance(evidence_observation, dict):
            for field in (
                "source_event_seq",
                "source_event_hash",
                "source_state_hash",
                "source_anchor_hash",
            ):
                expected_receipt_bindings[field] = evidence_observation.get(
                    field
                )
        for field, expected_value in expected_receipt_bindings.items():
            if evidence_receipt.get(field) != expected_value:
                errors.append(f"gate_run_receipt_{field}_mismatch")

    anchored_gate_run = (
        runtime_ledger.gate_runs_by_id.get(run_id)
        if isinstance(run_id, str)
        else None
    )
    if anchored_gate_run is None:
        errors.append("gate_run_receipt_missing_or_unanchored")
    else:
        anchored_receipt = anchored_gate_run.get("receipt")
        anchored_payload = anchored_gate_run.get("payload")
        if (
            not isinstance(anchored_receipt, dict)
            or not isinstance(anchored_receipt.get("run_anchor_hash"), str)
            or not SHA256_RE.fullmatch(
                anchored_receipt.get("run_anchor_hash", "")
            )
        ):
            errors.append("gate_run_receipt_unanchored")
        if (
            not isinstance(evidence_receipt, dict)
            or evidence_receipt != anchored_receipt
        ):
            errors.append("gate_run_receipt_mismatch")

        expected_run_payload: dict[str, Any] = {}
        source_fields = {
            "source_event_seq",
            "source_event_hash",
            "source_state_hash",
            "source_anchor_hash",
        }
        for field in RUNTIME_EVENT_CHAIN_SCHEMA_V1[
            "payload_required_by_type"
        ]["conditional_gate_run"]:
            if field in source_fields:
                expected_run_payload[field] = (
                    evidence_observation.get(field)
                    if isinstance(evidence_observation, dict)
                    else None
                )
            else:
                expected_run_payload[field] = evidence.get(field)
        if (
            not isinstance(anchored_payload, dict)
            or anchored_payload != expected_run_payload
        ):
            errors.append("gate_run_receipt_evidence_mismatch")
            if isinstance(anchored_payload, dict):
                for field, expected_value in expected_run_payload.items():
                    if anchored_payload.get(field) != expected_value:
                        errors.append(
                            f"gate_run_receipt_payload_mismatch:{field}"
                        )

        latest_source = expected_observation_binding(observation)
        if isinstance(anchored_receipt, dict) and isinstance(
            latest_source, dict
        ):
            if any(
                anchored_receipt.get(field) != latest_source.get(field)
                for field in source_fields
            ):
                errors.append(
                    "gate_run_receipt_replayed_against_latest_observation"
                )

    evidence_completed = parse_utc_timestamp(
        evidence.get("completed_at"),
        label="gate_evidence_completed_at",
        errors=errors,
    )
    max_age = MAX_EVIDENCE_AGE_SECONDS
    if type(max_age) is not int or max_age <= 0:
        errors.append("gate_freshness_contract_invalid")
    elif evidence_completed is not None:
        if evidence_completed > now:
            errors.append("gate_evidence_completed_at_future")
        elif (now - evidence_completed).total_seconds() > max_age:
            errors.append("gate_evidence_stale")

    raw_relative = evidence.get("raw_result_path")
    raw_hash = evidence.get("raw_result_sha256")
    expected_raw_relative = (
        f"{RAW_RESULT_PREFIX}{run_id}.json"
        if isinstance(run_id, str)
        else None
    )
    if raw_relative != expected_raw_relative:
        errors.append("raw_result_path_run_binding_mismatch")
    raw_path = safe_project_path(
        raw_relative,
        label="raw_result",
        errors=errors,
        required_prefix=RAW_RESULT_PREFIX,
    )
    raw: dict[str, Any] | None = None
    if not isinstance(raw_hash, str) or not SHA256_RE.fullmatch(raw_hash):
        errors.append("raw_result_sha256_invalid")
    if raw_path is None or not raw_path.is_file():
        errors.append("raw_result_missing")
    else:
        actual_raw_hash = sha256_file(raw_path)
        if actual_raw_hash != raw_hash:
            errors.append("raw_result_hash_mismatch")
        raw_value, _, raw_load_errors = read_json_object(
            raw_path, label="raw_result", required=True
        )
        errors.extend(raw_load_errors)
        raw = raw_value
    if raw is None:
        return errors

    raw_schema = CONDITIONAL_EVIDENCE_SCHEMA_V2["raw_result_schema"]
    exact_fields(
        raw,
        raw_schema.get("required"),
        label="raw_result",
        errors=errors,
    )
    if raw.get("schema_version") != raw_schema.get("schema_version"):
        errors.append("raw_result_schema_version_mismatch")
    for field in (
        "condition_id",
        "gate_id",
        "gate_stage",
        "state",
        "run_id",
        "producer_id",
        "executor_ids",
        "acceptance_case_ids",
        "observation",
    ):
        if raw.get(field) != evidence.get(field):
            errors.append(f"raw_result_{field}_mismatch")
    validate_binding_fields(raw, bindings, label="raw_result", errors=errors)
    if raw.get("status") != raw_schema.get("required_status"):
        errors.append("raw_result_status_not_pass")

    exact_string_set(
        raw.get("acceptance_case_ids"),
        required_cases,
        label="raw_result_acceptance_case_binding",
        errors=errors,
    )
    actual_cases_run = raw.get("actual_cases_run")
    if (
        type(actual_cases_run) is not int
        or actual_cases_run <= 0
        or actual_cases_run != len(required_cases)
    ):
        errors.append("raw_result_actual_cases_run_mismatch")

    case_results = raw.get("case_results")
    if not isinstance(case_results, list):
        errors.append("raw_result_case_results_invalid")
    else:
        case_ids = [
            item.get("case_id")
            for item in case_results
            if isinstance(item, dict)
        ]
        if (
            len(case_results) != len(required_cases)
            or len(case_ids) != len(case_results)
            or not all(
                isinstance(case_id, str) and case_id
                for case_id in case_ids
            )
            or len(case_ids) != len(set(case_ids))
            or set(case_ids) != required_cases
        ):
            errors.append("raw_result_case_set_mismatch")
        case_schema = evidence_schema.get("case_result_schema", {})
        for index, case_result in enumerate(case_results):
            if not isinstance(case_result, dict):
                errors.append(f"raw_result_case_invalid:{index}")
                continue
            exact_fields(
                case_result,
                list(CASE_RESULT_REQUIRED_V1),
                label=f"raw_result_case:{index}",
                errors=errors,
            )
            if case_result.get("status") != case_schema.get("required_status"):
                errors.append(
                    f"raw_result_case_status_not_pass:{case_result.get('case_id', index)}"
                )
            validate_hash_map(
                case_result.get("input_hashes"),
                label=f"raw_result_case_input_hashes:{index}",
                artifact_prefix=ARTIFACT_PREFIX,
                errors=errors,
            )
            validate_hash_map(
                case_result.get("raw_result_hashes"),
                label=f"raw_result_case_raw_hashes:{index}",
                artifact_prefix=ARTIFACT_PREFIX,
                errors=errors,
            )

    raw_started = parse_utc_timestamp(
        raw.get("started_at"),
        label="raw_result_started_at",
        errors=errors,
    )
    raw_completed = parse_utc_timestamp(
        raw.get("completed_at"),
        label="raw_result_completed_at",
        errors=errors,
    )
    if (
        raw_started is not None
        and raw_completed is not None
        and raw_started > raw_completed
    ):
        errors.append("raw_result_time_order_invalid")
    if (
        raw_completed is not None
        and evidence_completed is not None
        and raw_completed > evidence_completed
    ):
        errors.append("gate_evidence_predates_raw_result")
    observed_at = (
        expected_observation.get("observed_at")
        if isinstance(expected_observation, dict)
        else None
    )
    if observed_at is not None:
        observed_time = parse_utc_timestamp(
            observed_at,
            label="gate_observation_observed_at",
            errors=errors,
        )
        if (
            observed_time is not None
            and raw_started is not None
            and raw_started < observed_time
        ):
            errors.append("raw_result_predates_observation")
    if type(max_age) is int and max_age > 0 and raw_completed is not None:
        if raw_completed > now:
            errors.append("raw_result_completed_at_future")
        elif (now - raw_completed).total_seconds() > max_age:
            errors.append("raw_result_stale")
    return errors


def release_effect(
    gate: dict[str, Any], effective_state: str, target_verdict: str
) -> str | None:
    mapping = gate.get("release_mapping", {})
    state_rule = mapping.get(effective_state)
    if isinstance(state_rule, dict):
        effect = state_rule.get(target_verdict)
        return effect if isinstance(effect, str) else None
    return None


def evaluate(
    gate: dict[str, Any],
    all_conditional_gates: list[dict[str, Any]],
    contract: dict[str, Any],
    gate_catalog: dict[str, dict[str, Any]],
    runtime_authority: RuntimeAuthority,
    runtime_ledger: RuntimeLedger,
    target_verdict: str,
    bindings: AuthoritativeBindings,
    common_errors: list[str],
    now: dt.datetime,
) -> dict[str, Any]:
    gate_id = gate["id"]
    evidence_path_errors: list[str] = []
    evidence_path = safe_project_path(
        gate.get("evidence_path"),
        label="gate_evidence",
        errors=evidence_path_errors,
    )
    evidence: dict[str, Any] | None = None
    evidence_present = False
    evidence_load_errors: list[str] = []
    if evidence_path is not None:
        evidence, evidence_present, evidence_load_errors = read_json_object(
            evidence_path, label="gate_evidence", required=False
        )
    ready, stage, prerequisite_observation, prerequisite_errors = (
        observe_prerequisite(
            gate, contract, runtime_ledger, bindings
        )
    )
    errors = evidence_path_errors + evidence_load_errors + prerequisite_errors
    if (
        (ready or evidence_present)
        and gate.get("mandatory_gate_when_ready") is not None
        and gate.get("prerequisite_probe", {}).get("authority")
        != "runtime_sqlite_event_chain"
    ):
        errors.extend(runtime_ledger.errors)
    if ready or evidence_present:
        errors = list(common_errors) + errors
    allowed_states = set(gate["allowed_states"])
    transitions = gate["transition_table"]

    if not ready:
        effective_state = transitions["not_ready"]
        if evidence_present:
            errors.append(
                "gate_evidence_present_without_authoritative_prerequisite"
            )
            if (
                evidence is not None
                and gate.get("mandatory_gate_when_ready") is not None
                and stage is not None
            ):
                errors.extend(
                    validate_gate_evidence(
                        gate,
                        all_conditional_gates,
                        gate_catalog,
                        contract["conditional_evidence_schema"],
                        evidence,
                        stage,
                        prerequisite_observation,
                        bindings,
                        runtime_ledger,
                        now,
                    )
                )
    else:
        mandatory_gate = gate["mandatory_gate_when_ready"]
        if mandatory_gate is None:
            effective_state = transitions["ready_without_valid_gate_evidence"]
        elif evidence is None:
            errors.append("prerequisite_ready_but_evidence_missing")
            effective_state = transitions["ready_without_valid_gate_evidence"]
        else:
            validation_errors = validate_gate_evidence(
                gate,
                all_conditional_gates,
                gate_catalog,
                contract["conditional_evidence_schema"],
                evidence,
                stage,
                prerequisite_observation,
                bindings,
                runtime_ledger,
                now,
            )
            errors.extend(validation_errors)
            state = evidence.get("state")
            effective_state = (
                {
                    "passed": transitions.get("gate_pass"),
                    "failed": transitions.get("gate_fail"),
                    "inconclusive": transitions.get("gate_inconclusive"),
                }.get(state, transitions["ready_without_valid_gate_evidence"])
                if isinstance(state, str)
                else transitions["ready_without_valid_gate_evidence"]
            )
            if validation_errors:
                effective_state = transitions["ready_without_valid_gate_evidence"]

    if effective_state not in allowed_states:
        errors.append("effective_state_not_allowed")

    if runtime_authority.mode == "fixture" and target_verdict in {
        "human_onboarding_verified",
        "longitudinal_personal_validation",
    }:
        errors.append("fixture_runtime_cannot_satisfy_release")

    if gate_id == "COND-JAVEN-FIELD-USE" and target_verdict in {
        "human_onboarding_verified",
        "longitudinal_personal_validation",
    }:
        target_rule = gate["release_mapping"][target_verdict]
        if (
            stage != target_rule["required_probe_stage"]
            or effective_state != target_rule["required_state"]
            or not evidence
            or evidence.get("gate_stage") != target_rule["required_gate_stage"]
        ):
            errors.append("target_verdict_requirements_not_met")

    return {
        "condition_id": gate_id,
        "prerequisite_ready": ready,
        "prerequisite_stage": stage,
        "prerequisite_observation": prerequisite_observation,
        "evidence_path": gate["evidence_path"],
        "effective_state": effective_state,
        "target_release_effect": release_effect(
            gate, effective_state, target_verdict
        ),
        "must_not_be_claimed": gate["must_not_be_claimed"],
        "status": "fail" if errors else "pass",
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", help="evaluate one conditional gate id")
    parser.add_argument("--runtime-db")
    parser.add_argument(
        "--target-verdict",
        choices=[
            "core_release_candidate",
            "human_onboarding_verified",
            "longitudinal_personal_validation",
        ],
        default="core_release_candidate",
    )
    parser.add_argument(
        "--candidate-commit",
        help="expected value only; actual value is resolved from PROJECT_ROOT Git HEAD",
    )
    parser.add_argument(
        "--candidate-tree",
        help="expected value only; actual value is resolved from PROJECT_ROOT Git HEAD",
    )
    parser.add_argument(
        "--frozen-bundle-path",
        help="expected value only; actual path is fixed by the verifier",
    )
    parser.add_argument(
        "--frozen-bundle-sha256",
        help="expected value only; actual hash is recomputed from the fixed bundle",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        contract_value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"conditional contract cannot be loaded: {exc}", file=sys.stderr)
        return 2
    if not isinstance(contract_value, dict):
        print("conditional contract must be a JSON object", file=sys.stderr)
        return 2
    contract: dict[str, Any] = contract_value
    gates = contract.get("conditional_gates", [])
    if not isinstance(gates, list):
        print("conditional gate catalog is invalid", file=sys.stderr)
        return 2
    selected = [
        gate
        for gate in gates
        if isinstance(gate, dict)
        and (not args.gate or gate.get("id") == args.gate)
    ]
    if args.gate and not selected:
        print(f"unknown conditional gate: {args.gate}", file=sys.stderr)
        return 2

    bindings = resolve_authoritative_bindings(
        expected_commit=args.candidate_commit,
        expected_tree=args.candidate_tree,
        expected_bundle_path=args.frozen_bundle_path,
        expected_bundle_sha256=args.frozen_bundle_sha256,
    )
    common_errors = list(bindings.errors) + validate_contract_machine_schema(
        contract
    )
    runtime_authority = resolve_runtime_authority(args.runtime_db)
    runtime_ledger = load_runtime_ledger(runtime_authority)
    gate_catalog = {
        gate["id"]: gate
        for gate in contract.get("conditional_gate_catalog", [])
        if isinstance(gate, dict) and isinstance(gate.get("id"), str)
    }
    now = dt.datetime.now(dt.timezone.utc)
    results = [
        evaluate(
            gate,
            gates,
            contract,
            gate_catalog,
            runtime_authority,
            runtime_ledger,
            args.target_verdict,
            bindings,
            common_errors,
            now,
        )
        for gate in selected
    ]
    failed = [result for result in results if result["status"] == "fail"]
    blocking_effects = {
        "blocked",
        "design_reopened",
    }
    unresolved_states = {
        "not_run_missing_user_credential",
        "not_yet_observable",
        "inconclusive",
    }
    if failed or any(
        result.get("target_release_effect") in blocking_effects
        for result in results
    ):
        aggregate_verdict = "blocked"
    elif args.target_verdict != "core_release_candidate":
        aggregate_verdict = args.target_verdict
    elif any(
        result["effective_state"] in unresolved_states for result in results
    ):
        aggregate_verdict = "core_pass_with_unproven_conditions"
    else:
        aggregate_verdict = "all_selected_conditions_passed"
    payload = {
        "schema_version": 2,
        "status": "fail" if failed else "pass",
        "aggregate_verdict": aggregate_verdict,
        "authoritative_bindings": bindings.public_record(),
        "runtime_authority": runtime_authority.public_record(),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"conditional verification: {payload['status'].upper()} "
            f"(aggregate={aggregate_verdict})"
        )
        for result in results:
            print(
                f"- {result['condition_id']}: {result['effective_state']} "
                f"(prerequisite_ready={result['prerequisite_ready']})"
            )
            for error in result["errors"]:
                print(f"  error: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
