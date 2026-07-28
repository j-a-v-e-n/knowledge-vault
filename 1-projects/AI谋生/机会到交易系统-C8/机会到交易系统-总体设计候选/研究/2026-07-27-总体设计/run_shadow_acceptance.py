#!/usr/bin/env python3
"""Closed declarative-IR acceptance runner for local shadow evaluation.

Target-controlled artifacts are canonical JSON data, never Python or another
executable format.  The fixed runner interprets an exact tagged-union schema.
The macOS sandbox is required defense in depth for a local PASS, but is
deprecated/unsupported and is not evidence of universal host noninterference.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import grp
import hashlib
import json
import os
import re
import resource
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Optional, Sequence

sys.dont_write_bytecode = True

SANDBOX_EXEC = Path("/usr/bin/sandbox-exec")
TRUSTED_PYTHON = Path(
    "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/"
    "Python3.framework/Versions/3.9/Resources/"
    "Python.app/Contents/MacOS/Python"
)
TRUSTED_PYTHON_HOME = Path(
    "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/"
    "Python3.framework/Versions/3.9"
)
TRUSTED_RUNTIME_ANCHOR = Path("/Applications/Xcode.app")
SANDBOX_PROFILE_TEMPLATE = """(version 1)
(deny default)
(deny network*)
(deny process-fork)

(allow process-exec (literal {runtime}))

(allow file-read* file-test-existence file-map-executable
  (subpath {python_home})
  (subpath {output_dir})
  (subpath \"/System\")
  (subpath \"/Library/Apple\")
  (subpath \"/usr/lib\")
  (subpath \"/usr/share\")
  (literal \"/\")
  (literal \"/Applications\")
  (literal \"/Applications/Xcode.app\")
  (literal \"/Applications/Xcode.app/Contents\")
  (literal \"/Applications/Xcode.app/Contents/Developer\")
  (literal \"/Applications/Xcode.app/Contents/Developer/Library\")
  (literal \"/Applications/Xcode.app/Contents/Developer/Library/Frameworks\")
  (literal \"/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework\")
  (literal \"/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions\")
  (literal \"/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9\")
  (literal \"/private\")
  (literal \"/private/tmp\")
  (literal {probe_root})
  (literal \"/dev/null\")
  (literal \"/dev/random\")
  (literal \"/dev/urandom\")
  (literal \"/private/etc/localtime\"))

(allow file-write* (subpath {output_dir}))
(allow sysctl-read)
"""
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
TYPED_ID_RE = re.compile(
    r"^(CandidateManifest|OpportunityRecord|ObservationSamplingPlan|"
    r"SamplingPlanFreezeReceipt|AcquisitionRecord|RightsRecord|"
    r"SealedLaneOutput|Lane|LaneEpoch|Canary|ObservationClaim|"
    r"ContaminationEvent|NeedHypothesis|ExperimentSpec|EvalSpec):"
    r"[a-z0-9][a-z0-9._-]{0,63}$"
)
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".app", ".bat", ".bin", ".class", ".com", ".command", ".dll",
    ".dylib", ".exe", ".jar", ".o", ".ps1", ".pyd", ".py", ".pyc",
    ".sh", ".so", ".wasm", ".whl",
}

POLICY_KEYS = {
    "schema_version", "policy_id", "language_scope", "artifact_suffixes",
    "fixture_suffixes", "document_suffixes", "forbidden_artifact_suffixes",
    "opcodes", "domain_gate", "limits", "sandbox", "capabilities",
    "external_action_authority",
}
DOMAIN_GATE_KEYS = {
    "gate_id", "input_schema", "normalized_output_schema", "opcode",
    "rejection_codes", "required_acceptance_rejection_codes",
}
LIMIT_KEYS = {
    "max_artifact_bytes", "max_fixture_bytes", "max_report_bytes",
    "max_manifest_entries", "max_total_input_bytes", "max_acceptance_cases",
    "max_json_depth", "max_json_values", "max_string_bytes",
    "max_integer_abs", "max_nodes", "max_build_object_entries", "max_steps",
    "max_structural_value_bytes_total", "max_output_bytes",
    "max_output_files", "max_output_total_bytes", "max_stdout_bytes",
    "max_cas_files", "max_cas_total_bytes", "max_stderr_bytes",
    "wall_timeout_seconds", "aggregate_wall_timeout_seconds", "cpu_seconds",
    "max_open_files", "max_processes",
    "max_file_bytes",
}
FIXED_LIMITS = {
    "max_artifact_bytes": 262144,
    "max_fixture_bytes": 262144,
    "max_report_bytes": 524288,
    "max_manifest_entries": 256,
    "max_total_input_bytes": 4194304,
    "max_acceptance_cases": 32,
    "max_json_depth": 32,
    "max_json_values": 4096,
    "max_string_bytes": 16384,
    "max_integer_abs": 9007199254740991,
    "max_nodes": 256,
    "max_build_object_entries": 256,
    "max_steps": 512,
    "max_structural_value_bytes_total": 8388608,
    "max_output_bytes": 262144,
    "max_output_files": 64,
    "max_output_total_bytes": 1048576,
    "max_cas_files": 64,
    "max_cas_total_bytes": 1048576,
    "max_stdout_bytes": 65536,
    "max_stderr_bytes": 65536,
    "wall_timeout_seconds": 8,
    "aggregate_wall_timeout_seconds": 60,
    "cpu_seconds": 3,
    "max_open_files": 64,
    "max_processes": 2000,
    "max_file_bytes": 1048576,
}
SANDBOX_KEYS = {
    "implementation", "profile_model", "support_status", "required_probes",
    "failure_mode",
}
CAPABILITY_KEYS = {
    "arbitrary_artifact_code_execution", "connectors",
    "credential_or_environment_secret_access", "dynamic_dispatch_from_data",
    "external_action_authority", "filesystem_path_or_uri_from_data",
    "legacy_root_read", "module_loading_from_artifact",
    "native_or_compiled_artifact", "network", "non_temporary_write",
    "project_external_read", "subprocess",
}
PROGRAM_KEYS = {
    "schema_version", "program_id", "gate_id", "input_type", "output_type",
    "nodes", "result_ref",
}
NODE_KEYS = {
    "INPUT": {"id", "op"},
    "VALIDATE_OPPORTUNITY_RECORD": {"id", "op", "source"},
    "CAS_PUT": {"id", "op", "source"},
    "CAS_GET": {"id", "op", "digest_ref"},
}
PASS_CASE_KEYS = {
    "case_id", "fixture_path", "expected_outcome", "expected_result_sha256",
}
REJECT_CASE_KEYS = {
    "case_id", "fixture_path", "expected_outcome", "expected_rejection_code",
}
FILE_REF_KEYS = {"path", "sha256"}

DOMAIN_REJECTION_CODES = frozenset({
    "ACQUISITION_AFTER_FREEZE_REQUIRED",
    "AUTHORITY_ESCALATION_FORBIDDEN",
    "CANARY_ID_COLLISION",
    "CONTAMINATION_DETECTED",
    "CROSS_LANE_CANARY_DETECTED",
    "DOMAIN_RECORD_INVALID",
    "DOMAIN_RECORD_STALE",
    "DOMAIN_SCHEMA_KEY_MISMATCH",
    "DOMAIN_SCHEMA_MISMATCH",
    "DOMAIN_TYPE_MISMATCH",
    "EVAL_EXECUTION_FORBIDDEN",
    "EXPERIMENT_AUTHORIZATION_REQUIRED",
    "EXPERIMENT_EXECUTION_FORBIDDEN",
    "FIRST_PRINCIPLES_CONTENT_CLASSIFICATION_INVALID",
    "FIRST_PRINCIPLES_NOT_PRESEALED",
    "LANE_ID_COLLISION",
    "LEGACY_SCHEMA_QUARANTINED",
    "OBSERVATION_EVIDENCE_CLASSIFICATION_INVALID",
    "OBSERVATION_NOT_PRESEALED",
    "OBSERVATION_SOURCE_BINDING_MISMATCH",
    "PARENT_BINDING_MISMATCH",
    "PARENT_DANGLING",
    "PARENT_HASH_MISMATCH",
    "PARENT_INVALID",
    "PARENT_STALE",
    "RIGHTS_ACCOUNT_ACCESS_FORBIDDEN",
    "RIGHTS_EXTERNAL_RETRIEVAL_FORBIDDEN",
    "RIGHTS_NOT_AUTHORIZED",
    "RIGHTS_PERSONAL_DATA_FORBIDDEN",
    "SAMPLING_PLAN_NOT_FROZEN",
    "SIGNAL_EXTRACTION_UNCERTAINTY_MISSING",
    "SIGNAL_TAXONOMY_INCONSISTENT",
    "TYPED_ID_COLLISION",
    "TYPED_ID_INVALID",
    "TYPED_ID_TYPE_MISMATCH",
})
REQUIRED_ACCEPTANCE_REJECTION_CODES = frozenset({
    "CONTAMINATION_DETECTED",
    "CROSS_LANE_CANARY_DETECTED",
    "EXPERIMENT_EXECUTION_FORBIDDEN",
    "FIRST_PRINCIPLES_NOT_PRESEALED",
    "LEGACY_SCHEMA_QUARANTINED",
    "OBSERVATION_NOT_PRESEALED",
    "RIGHTS_NOT_AUTHORIZED",
    "SAMPLING_PLAN_NOT_FROZEN",
    "SIGNAL_TAXONOMY_INCONSISTENT",
})


class CapabilityError(ValueError):
    pass


class DomainRejection(ValueError):
    def __init__(self, code: str):
        if code not in DOMAIN_REJECTION_CODES:
            raise CapabilityError("internal domain rejection code is outside closed set")
        super().__init__(code)
        self.code = code
        self.steps = 0


@dataclass(frozen=True)
class Snapshot:
    data: bytes
    sha256: str
    stat_identity: tuple[int, int, int, int, int, int, int, int, int]
    source: str


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CapabilityError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def canonical_text(document: Any) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_snapshot_integrity(snapshot: Snapshot, label: str, max_bytes: int) -> None:
    if not isinstance(snapshot, Snapshot) or len(snapshot.stat_identity) != 9:
        raise CapabilityError(f"{label}: invalid snapshot object")
    if len(snapshot.data) > max_bytes or snapshot.stat_identity[6] != len(snapshot.data):
        raise CapabilityError(f"{label}: snapshot length/stat binding mismatch")
    if snapshot.sha256 != sha256_bytes(snapshot.data):
        raise CapabilityError(f"{label}: snapshot hash/bytes binding mismatch")
    if not stat.S_ISREG(snapshot.stat_identity[2]):
        raise CapabilityError(f"{label}: snapshot is not regular-file identity")


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def canonical_document_sha256(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def json_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise CapabilityError(f"unsupported result type {type(value).__name__}")


def _identity(value: os.stat_result) -> tuple[int, int, int, int, int, int, int, int, int]:
    return (
        value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
        value.st_uid, value.st_gid,
        value.st_size, value.st_mtime_ns, value.st_ctime_ns,
    )


def _directory_identity(path: Path) -> tuple[int, int, int, int, int]:
    value = path.lstat()
    return value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid


def _snapshot_open_fd(
    fd: int, label: str, max_bytes: int, source: str,
    allowed_nlinks: tuple[int, ...] = (1,),
) -> Snapshot:
    os.lseek(fd, 0, os.SEEK_SET)
    before = os.fstat(fd)
    if not stat.S_ISREG(before.st_mode):
        raise CapabilityError(f"{label}: expected regular file")
    if before.st_nlink not in allowed_nlinks:
        raise CapabilityError(f"{label}: hardlinked/unexpected link count {before.st_nlink}")
    if before.st_size < 0 or before.st_size > max_bytes:
        raise CapabilityError(f"{label}: file exceeds {max_bytes} bytes")
    blocks: list[bytes] = []
    total = 0
    while True:
        block = os.read(fd, min(65536, max_bytes + 1 - total))
        if not block:
            break
        blocks.append(block)
        total += len(block)
        if total > max_bytes:
            raise CapabilityError(f"{label}: file exceeds {max_bytes} bytes")
    after = os.fstat(fd)
    data = b"".join(blocks)
    if _identity(before) != _identity(after) or len(data) != before.st_size:
        raise CapabilityError(f"{label}: opened object mutated during read")
    return Snapshot(data, sha256_bytes(data), _identity(after), source)


def read_once_regular(path: Path, label: str, max_bytes: int) -> Snapshot:
    """Read one O_NOFOLLOW opened regular object; hash exactly those bytes."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise CapabilityError(f"{label}: cannot open without following links: {exc}") from exc
    try:
        return _snapshot_open_fd(fd, label, max_bytes, str(path))
    finally:
        os.close(fd)


def _normalized_parts(raw: Any, label: str) -> tuple[str, tuple[str, ...]]:
    if not isinstance(raw, str) or not raw:
        raise CapabilityError(f"{label}: expected non-empty relative path")
    pure = PurePosixPath(raw)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise CapabilityError(f"{label}: expected normalized relative path")
    return raw, pure.parts


def read_once_member(root: Path, raw: Any, label: str, max_bytes: int) -> tuple[str, Snapshot]:
    relative, parts = _normalized_parts(raw, label)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) |
        getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    file_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    opened: list[int] = []
    try:
        current = os.open(root, directory_flags)
        opened.append(current)
        for part in parts[:-1]:
            current = os.open(part, directory_flags, dir_fd=current)
            opened.append(current)
        fd = os.open(parts[-1], file_flags, dir_fd=current)
        opened.append(fd)
        return relative, _snapshot_open_fd(fd, label, max_bytes, f"{root}/{relative}")
    except OSError as exc:
        raise CapabilityError(f"{label}: unsafe or missing member: {exc}") from exc
    finally:
        for fd in reversed(opened):
            os.close(fd)


def _json_from_bytes(data: bytes, label: str) -> Any:
    try:
        text = data.decode("utf-8")
        return json.loads(
            text, object_pairs_hook=reject_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                CapabilityError(f"{label}: non-finite number {value} forbidden")
            ),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CapabilityError(f"{label}: invalid UTF-8 JSON: {exc}") from exc


def canonical_load_value_snapshot(snapshot: Snapshot, label: str) -> Any:
    document = _json_from_bytes(snapshot.data, label)
    if snapshot.data != canonical_text(document).encode("utf-8"):
        raise CapabilityError(f"{label}: JSON is not canonically serialized")
    return document


def canonical_load_snapshot(snapshot: Snapshot, label: str) -> dict[str, Any]:
    document = canonical_load_value_snapshot(snapshot, label)
    if not isinstance(document, dict):
        raise CapabilityError(f"{label}: root must be an object")
    return document


def canonical_load(path: Path, label: str, max_bytes: int = 524288) -> dict[str, Any]:
    return canonical_load_snapshot(read_once_regular(path, label, max_bytes), label)


def require_exact_keys(value: Any, keys: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise CapabilityError(f"{label}: expected object")
    if set(value) != keys:
        raise CapabilityError(
            f"{label}: key mismatch; missing={sorted(keys - set(value))}; "
            f"extra={sorted(set(value) - keys)}"
        )


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise CapabilityError(f"{label}: expected lowercase SHA-256")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if (
        not isinstance(value, list) or
        any(not isinstance(item, str) or not item for item in value) or
        len(value) != len(set(value))
    ):
        raise CapabilityError(f"{label}: expected unique non-empty string list")
    return value


def _check_json_limits(value: Any, limits: Mapping[str, int], label: str) -> None:
    count = 0
    stack: list[tuple[Any, int]] = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        count += 1
        if count > limits["max_json_values"]:
            raise CapabilityError(f"{label}: JSON value count limit exceeded")
        if depth > limits["max_json_depth"]:
            raise CapabilityError(f"{label}: JSON depth limit exceeded")
        if isinstance(current, str):
            if len(current.encode("utf-8")) > limits["max_string_bytes"]:
                raise CapabilityError(f"{label}: string byte limit exceeded")
        elif isinstance(current, bool) or current is None:
            pass
        elif isinstance(current, int):
            if abs(current) > limits["max_integer_abs"]:
                raise CapabilityError(f"{label}: integer magnitude limit exceeded")
        elif isinstance(current, float):
            raise CapabilityError(f"{label}: floating-point values are forbidden")
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in reversed(current))
        elif isinstance(current, dict):
            for key, item in reversed(list(current.items())):
                if not isinstance(key, str):
                    raise CapabilityError(f"{label}: object key must be string")
                stack.append((key, depth + 1))
                stack.append((item, depth + 1))
        else:
            raise CapabilityError(f"{label}: unsupported JSON type {type(current).__name__}")


def load_policy_snapshot(snapshot: Snapshot) -> dict[str, Any]:
    _require_snapshot_integrity(snapshot, "capability_policy", 524288)
    policy = canonical_load_snapshot(snapshot, "capability_policy")
    require_exact_keys(policy, POLICY_KEYS, "capability_policy")
    if policy["schema_version"] != "otts.shadow-capability-policy/4":
        raise CapabilityError("capability policy schema mismatch")
    if policy["policy_id"] != "OTTS-SHADOW-OPPORTUNITY-SEMANTIC-GATE-CLOSED-1":
        raise CapabilityError("capability policy ID mismatch")
    if (
        policy["language_scope"]
        != "CANONICAL_JSON_CLOSED_OPPORTUNITY_SEMANTIC_GATE_ONLY"
    ):
        raise CapabilityError("capability policy must require the closed domain Gate")
    require_exact_keys(policy["domain_gate"], DOMAIN_GATE_KEYS, "policy.domain_gate")
    expected_domain_gate = {
        "gate_id": "OTTS-OPPORTUNITY-SEMANTIC-GATE-1",
        "input_schema": "otts.opportunity-record/1",
        "normalized_output_schema": "otts.normalized-opportunity-record/1",
        "opcode": "VALIDATE_OPPORTUNITY_RECORD",
        "rejection_codes": sorted(DOMAIN_REJECTION_CODES),
        "required_acceptance_rejection_codes": sorted(
            REQUIRED_ACCEPTANCE_REJECTION_CODES
        ),
    }
    if policy["domain_gate"] != expected_domain_gate:
        raise CapabilityError("policy domain Gate contract differs from runner closed contract")
    require_exact_keys(policy["limits"], LIMIT_KEYS, "policy.limits")
    for key, value in policy["limits"].items():
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise CapabilityError(f"policy.limits.{key}: expected positive integer")
    if policy["limits"] != FIXED_LIMITS:
        raise CapabilityError("policy limits must equal runner-coded fixed ceilings")
    require_exact_keys(policy["sandbox"], SANDBOX_KEYS, "policy.sandbox")
    require_exact_keys(policy["capabilities"], CAPABILITY_KEYS, "policy.capabilities")
    if any(value is not False for value in policy["capabilities"].values()):
        raise CapabilityError("every artifact capability must be false")
    if policy["external_action_authority"] is not False:
        raise CapabilityError("policy must deny external action authority")
    for key in (
        "artifact_suffixes", "fixture_suffixes", "document_suffixes",
        "forbidden_artifact_suffixes", "opcodes",
    ):
        _string_list(policy[key], f"policy.{key}")
    _string_list(policy["sandbox"]["required_probes"], "policy.sandbox.required_probes")
    if set(policy["opcodes"]) != set(NODE_KEYS):
        raise CapabilityError("policy opcode set differs from runner closed set")
    if set(policy["forbidden_artifact_suffixes"]) != FORBIDDEN_ARTIFACT_SUFFIXES:
        raise CapabilityError("policy forbidden artifact suffix set mismatch")
    if policy["sandbox"] != {
        "implementation": "/usr/bin/sandbox-exec",
        "profile_model": "DENY_DEFAULT_OPENED_UNLINKED_INPUT_FDS_PRIVATE_TEMP_WRITE",
        "support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
        "required_probes": [
            "CHILD_PROCESS_DENIED", "EXTERNAL_READ_DENIED",
            "EXTERNAL_WRITE_DENIED", "NETWORK_LOOPBACK_BIND_DENIED",
        ],
        "failure_mode": "FAIL_CLOSED_NO_PASS",
    }:
        raise CapabilityError("sandbox policy constants mismatch")
    return policy


def load_policy(policy_path: Path) -> dict[str, Any]:
    snapshot = read_once_regular(policy_path, "capability_policy", 524288)
    return load_policy_snapshot(snapshot)


def _node_refs(node: dict[str, Any]) -> list[str]:
    op = node["op"]
    if op in {"VALIDATE_OPPORTUNITY_RECORD", "CAS_PUT"}:
        return [node["source"]]
    if op == "CAS_GET":
        return [node["digest_ref"]]
    return []


def validate_program(program: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(program, PROGRAM_KEYS, "program")
    if program["schema_version"] != "otts.shadow-declarative-ir/2":
        raise CapabilityError("program schema mismatch")
    if not isinstance(program["program_id"], str) or not IDENTIFIER_RE.fullmatch(program["program_id"]):
        raise CapabilityError("program.program_id invalid")
    if program["gate_id"] != "OTTS-OPPORTUNITY-SEMANTIC-GATE-1":
        raise CapabilityError("program.gate_id mismatch")
    if (
        program["input_type"] != "OPPORTUNITY_RECORD"
        or program["output_type"] != "NORMALIZED_OPPORTUNITY_RECORD"
    ):
        raise CapabilityError("program input/output types must bind the domain Gate")
    nodes = program["nodes"]
    if not isinstance(nodes, list) or not nodes or len(nodes) > policy["limits"]["max_nodes"]:
        raise CapabilityError("program.nodes count invalid or over limit")
    by_id: dict[str, dict[str, Any]] = {}
    input_count = 0
    for index, node in enumerate(nodes):
        label = f"program.nodes[{index}]"
        if not isinstance(node, dict):
            raise CapabilityError(f"{label}: expected object")
        op = node.get("op")
        if op not in NODE_KEYS:
            raise CapabilityError(f"{label}: unknown opcode {op!r}")
        require_exact_keys(node, NODE_KEYS[op], label)
        node_id = node["id"]
        if not isinstance(node_id, str) or not IDENTIFIER_RE.fullmatch(node_id):
            raise CapabilityError(f"{label}.id invalid")
        if node_id in by_id:
            raise CapabilityError(f"{label}: duplicate node id")
        by_id[node_id] = node
        if op == "INPUT":
            input_count += 1
        for ref in _node_refs(node):
            if not isinstance(ref, str) or not IDENTIFIER_RE.fullmatch(ref):
                raise CapabilityError(f"{label}: invalid reference")
    if input_count != 1:
        raise CapabilityError("program must contain exactly one INPUT node")
    result_ref = program["result_ref"]
    if not isinstance(result_ref, str) or result_ref not in by_id:
        raise CapabilityError("program.result_ref is unknown")
    for node in nodes:
        unknown = sorted(set(_node_refs(node)) - set(by_id))
        if unknown:
            raise CapabilityError(f"node {node['id']}: unknown refs {unknown}")
    visiting: set[str] = set()
    reached: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in reached:
            return
        if node_id in visiting:
            raise CapabilityError(f"program node cycle at {node_id}")
        visiting.add(node_id)
        for ref in _node_refs(by_id[node_id]):
            visit(ref)
        visiting.remove(node_id)
        reached.add(node_id)

    visit(result_ref)
    unreachable = sorted(set(by_id) - reached)
    if unreachable:
        raise CapabilityError(f"program has unreachable nodes: {unreachable}")
    inputs = [node for node in nodes if node["op"] == "INPUT"]
    validators = [
        node for node in nodes if node["op"] == "VALIDATE_OPPORTUNITY_RECORD"
    ]
    cas_puts = [node for node in nodes if node["op"] == "CAS_PUT"]
    cas_gets = [node for node in nodes if node["op"] == "CAS_GET"]
    if len(validators) != 1 or validators[0]["source"] != inputs[0]["id"]:
        raise CapabilityError("program must validate the sole INPUT exactly once")
    validator_id = validators[0]["id"]
    if result_ref == validator_id:
        if len(nodes) != 2 or cas_puts or cas_gets:
            raise CapabilityError("direct domain Gate program must contain exactly two nodes")
    else:
        if len(nodes) != 4 or len(cas_puts) != 1 or len(cas_gets) != 1:
            raise CapabilityError("domain Gate may only add one exact CAS round trip")
        if cas_puts[0]["source"] != validator_id:
            raise CapabilityError("CAS_PUT must consume the normalized domain record")
        if cas_gets[0]["digest_ref"] != cas_puts[0]["id"]:
            raise CapabilityError("CAS_GET must consume the Gate CAS digest")
        if result_ref != cas_gets[0]["id"]:
            raise CapabilityError("program result must be the normalized CAS round trip")
    return {
        "node_graph_digest_sha256": sha256_json(
            {"nodes": nodes, "result_ref": result_ref}
        ),
        "node_count": len(nodes),
    }


OPPORTUNITY_RECORD_KEYS = {
    "schema_version", "record_type", "record_id", "record_state",
    "parent_context", "sampling_plan", "sampling_freeze_receipt",
    "acquisition_record", "rights_record", "first_principles_lane",
    "observation_lane", "contamination_event", "need_hypothesis",
    "experiment_spec", "eval_spec", "authority",
}
PARENT_CONTEXT_KEYS = {"candidate_id", "candidate_sha256", "state"}
PARENT_BINDING_KEYS = {"parent_id", "parent_sha256", "required_state"}
COMMON_RECORD_KEYS = {
    "schema_version", "record_type", "record_id", "state", "parent_bindings",
}
SAMPLING_PLAN_KEYS = COMMON_RECORD_KEYS | {
    "sampling_purpose", "frozen_before_observation", "plan_sequence",
    "source_universe", "selection_rule", "inclusion_rule", "exclusion_rule",
    "negative_sample_rule", "stopping_rule",
}
SAMPLING_FREEZE_KEYS = COMMON_RECORD_KEYS | {
    "status", "sequence", "plan_sha256",
}
ACQUISITION_KEYS = COMMON_RECORD_KEYS | {
    "sequence", "mode", "observed_after_sampling_freeze",
    "account_or_login_used", "external_retrieval_performed",
}
RIGHTS_KEYS = COMMON_RECORD_KEYS | {
    "status", "contains_personal_data", "account_or_login_used",
    "external_retrieval_performed",
}
FIRST_PRINCIPLES_LANE_KEYS = COMMON_RECORD_KEYS | {
    "lane_id", "lane_epoch_id", "lane_role", "seal_sequence",
    "sealed_before_observation", "canary_id", "canary_token",
    "contamination_detected", "content_classification", "principles",
    "assumptions",
}
OBSERVATION_LANE_KEYS = COMMON_RECORD_KEYS | {
    "lane_id", "lane_epoch_id", "lane_role", "seal_sequence",
    "sealed_before_cross_lane_merge", "canary_id", "canary_token",
    "contamination_detected", "source_kind", "source_payload",
    "source_payload_sha256", "evidence_classification", "observations",
    "signal_taxonomy",
}
OBSERVATION_CLAIM_KEYS = {
    "claim_id", "source_start", "source_end", "source_text", "span_sha256",
    "evidence_class",
}
SIGNAL_TAXONOMY_KEYS = {
    "schema_version", "primary_class", "explicit_request_status",
    "behavior_observation_status", "extraction_basis",
    "extraction_uncertainty", "natural_language_inference_performed",
    "source_payload_sha256", "source_span_ids",
}
CONTAMINATION_EVENT_KEYS = COMMON_RECORD_KEYS | {
    "status", "detected", "detected_canary_ids", "assessment_sequence",
}
NEED_HYPOTHESIS_KEYS = COMMON_RECORD_KEYS | {
    "status", "merge_sequence", "candidate_buyer_class", "job_to_be_done",
    "statement", "competing_explanations", "applicability_scope",
    "weakest_assumption", "supporting_observation_claim_ids",
}
EXPERIMENT_SPEC_KEYS = COMMON_RECORD_KEYS | {
    "status", "requires_new_explicit_authorization", "draft_method",
    "success_signal", "failure_signal", "forbidden_capabilities",
    "external_action_authority",
}
EVAL_SPEC_KEYS = COMMON_RECORD_KEYS | {
    "status", "fixture_type", "oracle_kind", "model_binding_sha256",
    "harness_binding_sha256", "human_baseline", "cost_record",
    "external_action_authority",
}
AUTHORITY_KEYS = {
    "market_authority", "customer_authority", "demand_proof",
    "pricing_authority", "payment_authority", "deployment_authority",
    "external_action_authority",
}


def _domain_object(value: Any, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    if set(value) != keys:
        raise DomainRejection("DOMAIN_SCHEMA_KEY_MISMATCH")
    return value


def _domain_string(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    return value


def _domain_positive_int(value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    return value


def _domain_string_list(
    value: Any, *, allow_empty: bool = False,
) -> list[str]:
    if (
        not isinstance(value, list)
        or (not allow_empty and not value)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    return value


def _domain_typed_id_syntax(value: Any, expected_type: str) -> str:
    if not isinstance(value, str) or not TYPED_ID_RE.fullmatch(value):
        raise DomainRejection("TYPED_ID_INVALID")
    if value.split(":", 1)[0] != expected_type:
        raise DomainRejection("TYPED_ID_TYPE_MISMATCH")
    return value


def _domain_register_id(
    value: Any, expected_type: str, seen: set[str],
) -> str:
    typed_id = _domain_typed_id_syntax(value, expected_type)
    if typed_id in seen:
        raise DomainRejection("TYPED_ID_COLLISION")
    seen.add(typed_id)
    return typed_id


def _domain_require_state(value: Any, *, root: bool = False) -> None:
    if value == "CURRENT":
        return
    if value == "STALE":
        raise DomainRejection("DOMAIN_RECORD_STALE" if root else "PARENT_STALE")
    if value == "INVALID":
        raise DomainRejection("DOMAIN_RECORD_INVALID" if root else "PARENT_INVALID")
    raise DomainRejection("DOMAIN_RECORD_INVALID")


def _domain_common_record(
    value: Any, *, keys: set[str], schema: str, record_type: str,
    seen: set[str],
) -> dict[str, Any]:
    record = _domain_object(value, keys)
    if record["schema_version"] != schema or record["record_type"] != record_type:
        raise DomainRejection("DOMAIN_SCHEMA_MISMATCH")
    _domain_register_id(record["record_id"], record_type, seen)
    _domain_require_state(record["state"])
    if not isinstance(record["parent_bindings"], list):
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    return record


def _domain_contains_scalar(value: Any, target: str) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if current == target:
            return True
        if isinstance(current, dict):
            stack.extend(current.keys())
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _domain_validate_parent_bindings(
    child: dict[str, Any], expected_parents: list[dict[str, Any]],
    all_records: Mapping[str, dict[str, Any]],
) -> None:
    bindings = child["parent_bindings"]
    expected_ids = [parent["record_id"] for parent in expected_parents]
    if len(bindings) != len(expected_ids):
        raise DomainRejection("PARENT_BINDING_MISMATCH")
    actual_ids: list[str] = []
    for binding in bindings:
        row = _domain_object(binding, PARENT_BINDING_KEYS)
        parent_id = _domain_string(row["parent_id"])
        if parent_id not in all_records:
            raise DomainRejection("PARENT_DANGLING")
        actual_ids.append(parent_id)
        if row["required_state"] != "CURRENT":
            raise DomainRejection("PARENT_BINDING_MISMATCH")
        parent = all_records[parent_id]
        _domain_require_state(parent["state"])
        if (
            not isinstance(row["parent_sha256"], str)
            or not SHA256_RE.fullmatch(row["parent_sha256"])
            or row["parent_sha256"] != sha256_json(parent)
        ):
            raise DomainRejection("PARENT_HASH_MISMATCH")
    if actual_ids != expected_ids or len(actual_ids) != len(set(actual_ids)):
        raise DomainRejection("PARENT_BINDING_MISMATCH")


def validate_opportunity_record(
    value: Any, expected_parent_candidate_sha256: Optional[str] = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    schema_version = value.get("schema_version")
    if schema_version in {"0.1", "otts.opportunity-record/0.1"}:
        raise DomainRejection("LEGACY_SCHEMA_QUARANTINED")
    record = _domain_object(value, OPPORTUNITY_RECORD_KEYS)
    if (
        record["schema_version"] != "otts.opportunity-record/1"
        or record["record_type"] != "OpportunityRecord"
    ):
        raise DomainRejection("DOMAIN_SCHEMA_MISMATCH")
    seen_ids: set[str] = set()
    _domain_register_id(record["record_id"], "OpportunityRecord", seen_ids)
    _domain_require_state(record["record_state"], root=True)

    parent_context = _domain_object(record["parent_context"], PARENT_CONTEXT_KEYS)
    _domain_register_id(parent_context["candidate_id"], "CandidateManifest", seen_ids)
    candidate_sha256 = parent_context["candidate_sha256"]
    if not isinstance(candidate_sha256, str) or not SHA256_RE.fullmatch(candidate_sha256):
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    _domain_require_state(parent_context["state"])
    if (
        expected_parent_candidate_sha256 is not None
        and candidate_sha256 != expected_parent_candidate_sha256
    ):
        raise DomainRejection("PARENT_HASH_MISMATCH")

    sampling_plan = _domain_common_record(
        record["sampling_plan"], keys=SAMPLING_PLAN_KEYS,
        schema="otts.observation-sampling-plan/1",
        record_type="ObservationSamplingPlan", seen=seen_ids,
    )
    sampling_freeze = _domain_common_record(
        record["sampling_freeze_receipt"], keys=SAMPLING_FREEZE_KEYS,
        schema="otts.sampling-plan-freeze-receipt/1",
        record_type="SamplingPlanFreezeReceipt", seen=seen_ids,
    )
    acquisition = _domain_common_record(
        record["acquisition_record"], keys=ACQUISITION_KEYS,
        schema="otts.acquisition-record/1", record_type="AcquisitionRecord",
        seen=seen_ids,
    )
    rights = _domain_common_record(
        record["rights_record"], keys=RIGHTS_KEYS,
        schema="otts.rights-record/1", record_type="RightsRecord",
        seen=seen_ids,
    )
    first_lane = _domain_common_record(
        record["first_principles_lane"], keys=FIRST_PRINCIPLES_LANE_KEYS,
        schema="otts.sealed-lane-output/1", record_type="SealedLaneOutput",
        seen=seen_ids,
    )
    observation_lane = _domain_common_record(
        record["observation_lane"], keys=OBSERVATION_LANE_KEYS,
        schema="otts.sealed-lane-output/1", record_type="SealedLaneOutput",
        seen=seen_ids,
    )
    contamination = _domain_common_record(
        record["contamination_event"], keys=CONTAMINATION_EVENT_KEYS,
        schema="otts.contamination-event/1", record_type="ContaminationEvent",
        seen=seen_ids,
    )
    hypothesis = _domain_common_record(
        record["need_hypothesis"], keys=NEED_HYPOTHESIS_KEYS,
        schema="otts.need-hypothesis/1", record_type="NeedHypothesis",
        seen=seen_ids,
    )
    experiment = _domain_common_record(
        record["experiment_spec"], keys=EXPERIMENT_SPEC_KEYS,
        schema="otts.experiment-spec/1", record_type="ExperimentSpec",
        seen=seen_ids,
    )
    eval_spec = _domain_common_record(
        record["eval_spec"], keys=EVAL_SPEC_KEYS,
        schema="otts.eval-spec/1", record_type="EvalSpec", seen=seen_ids,
    )

    if sampling_plan["sampling_purpose"] not in {
        "DISCOVERY_UNCONDITIONED", "HYPOTHESIS_CONDITIONED", "CONFIRMATORY",
    }:
        raise DomainRejection("DOMAIN_RECORD_INVALID")
    for key in (
        "source_universe", "selection_rule", "inclusion_rule", "exclusion_rule",
        "negative_sample_rule", "stopping_rule",
    ):
        _domain_string(sampling_plan[key])
    plan_sequence = _domain_positive_int(sampling_plan["plan_sequence"])
    if sampling_plan["frozen_before_observation"] is not True:
        raise DomainRejection("SAMPLING_PLAN_NOT_FROZEN")
    freeze_sequence = _domain_positive_int(sampling_freeze["sequence"])
    if (
        sampling_freeze["status"] != "FROZEN"
        or sampling_freeze["plan_sha256"] != sha256_json(sampling_plan)
        or freeze_sequence <= plan_sequence
    ):
        raise DomainRejection("SAMPLING_PLAN_NOT_FROZEN")
    acquisition_sequence = _domain_positive_int(acquisition["sequence"])
    if (
        acquisition["mode"] != "SYNTHETIC_LOCAL_FIXTURE"
        or acquisition["observed_after_sampling_freeze"] is not True
        or acquisition_sequence <= freeze_sequence
    ):
        raise DomainRejection("ACQUISITION_AFTER_FREEZE_REQUIRED")
    if acquisition["account_or_login_used"] is not False:
        raise DomainRejection("RIGHTS_ACCOUNT_ACCESS_FORBIDDEN")
    if acquisition["external_retrieval_performed"] is not False:
        raise DomainRejection("RIGHTS_EXTERNAL_RETRIEVAL_FORBIDDEN")

    if rights["status"] != "SYNTHETIC_AUTHORIZED":
        raise DomainRejection("RIGHTS_NOT_AUTHORIZED")
    if rights["contains_personal_data"] is not False:
        raise DomainRejection("RIGHTS_PERSONAL_DATA_FORBIDDEN")
    if rights["account_or_login_used"] is not False:
        raise DomainRejection("RIGHTS_ACCOUNT_ACCESS_FORBIDDEN")
    if rights["external_retrieval_performed"] is not False:
        raise DomainRejection("RIGHTS_EXTERNAL_RETRIEVAL_FORBIDDEN")

    if first_lane["lane_role"] != "FIRST_PRINCIPLES":
        raise DomainRejection("DOMAIN_RECORD_INVALID")
    if first_lane["sealed_before_observation"] is not True:
        raise DomainRejection("FIRST_PRINCIPLES_NOT_PRESEALED")
    if (
        first_lane["content_classification"]
        != "GENERAL_PRINCIPLES_ONLY_HUMAN_ASSERTED_UNVERIFIED"
    ):
        raise DomainRejection("FIRST_PRINCIPLES_CONTENT_CLASSIFICATION_INVALID")
    _domain_string_list(first_lane["principles"])
    _domain_string_list(first_lane["assumptions"])
    if observation_lane["lane_role"] != "OBSERVATION":
        raise DomainRejection("DOMAIN_RECORD_INVALID")
    if observation_lane["sealed_before_cross_lane_merge"] is not True:
        raise DomainRejection("OBSERVATION_NOT_PRESEALED")
    if observation_lane["source_kind"] != "SYNTHETIC_CONSTRUCTED_TEXT":
        raise DomainRejection("OBSERVATION_EVIDENCE_CLASSIFICATION_INVALID")
    if (
        observation_lane["evidence_classification"]
        != "DIRECT_SOURCE_SPANS_ONLY_SEMANTICS_UNVERIFIED"
    ):
        raise DomainRejection("OBSERVATION_EVIDENCE_CLASSIFICATION_INVALID")

    first_lane_id = _domain_typed_id_syntax(first_lane["lane_id"], "Lane")
    observation_lane_id = _domain_typed_id_syntax(
        observation_lane["lane_id"], "Lane"
    )
    if first_lane_id == observation_lane_id:
        raise DomainRejection("LANE_ID_COLLISION")
    _domain_register_id(first_lane_id, "Lane", seen_ids)
    _domain_register_id(observation_lane_id, "Lane", seen_ids)
    first_epoch = _domain_typed_id_syntax(first_lane["lane_epoch_id"], "LaneEpoch")
    observation_epoch = _domain_typed_id_syntax(
        observation_lane["lane_epoch_id"], "LaneEpoch"
    )
    if first_epoch != observation_epoch:
        raise DomainRejection("DOMAIN_RECORD_INVALID")
    first_canary_id = _domain_typed_id_syntax(first_lane["canary_id"], "Canary")
    observation_canary_id = _domain_typed_id_syntax(
        observation_lane["canary_id"], "Canary"
    )
    first_canary_token = _domain_string(first_lane["canary_token"])
    observation_canary_token = _domain_string(observation_lane["canary_token"])
    if (
        first_canary_id == observation_canary_id
        or first_canary_token == observation_canary_token
    ):
        raise DomainRejection("CANARY_ID_COLLISION")
    _domain_register_id(first_canary_id, "Canary", seen_ids)
    _domain_register_id(observation_canary_id, "Canary", seen_ids)
    if (
        _domain_contains_scalar(observation_lane, first_canary_id)
        or _domain_contains_scalar(observation_lane, first_canary_token)
        or _domain_contains_scalar(first_lane, observation_canary_id)
        or _domain_contains_scalar(first_lane, observation_canary_token)
    ):
        raise DomainRejection("CROSS_LANE_CANARY_DETECTED")

    source_payload = _domain_string(observation_lane["source_payload"])
    source_payload_sha256 = sha256_bytes(source_payload.encode("utf-8"))
    if observation_lane["source_payload_sha256"] != source_payload_sha256:
        raise DomainRejection("OBSERVATION_SOURCE_BINDING_MISMATCH")
    observations = observation_lane["observations"]
    if not isinstance(observations, list) or not observations:
        raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    observation_claim_ids: list[str] = []
    for claim in observations:
        row = _domain_object(claim, OBSERVATION_CLAIM_KEYS)
        claim_id = _domain_register_id(row["claim_id"], "ObservationClaim", seen_ids)
        start = row["source_start"]
        end = row["source_end"]
        if (
            not isinstance(start, int) or isinstance(start, bool)
            or not isinstance(end, int) or isinstance(end, bool)
            or start < 0 or end <= start or end > len(source_payload)
        ):
            raise DomainRejection("OBSERVATION_SOURCE_BINDING_MISMATCH")
        source_text = source_payload[start:end]
        if (
            row["evidence_class"] != "DIRECT_SOURCE_SPAN"
            or row["source_text"] != source_text
            or row["span_sha256"] != sha256_bytes(source_text.encode("utf-8"))
        ):
            raise DomainRejection("OBSERVATION_SOURCE_BINDING_MISMATCH")
        observation_claim_ids.append(claim_id)

    taxonomy = _domain_object(
        observation_lane["signal_taxonomy"], SIGNAL_TAXONOMY_KEYS
    )
    if taxonomy["schema_version"] != "otts.structured-signal-taxonomy/1":
        raise DomainRejection("DOMAIN_SCHEMA_MISMATCH")
    if (
        taxonomy["extraction_basis"] != "SOURCE_SPAN_BOUND_HUMAN_LABEL"
        or taxonomy["extraction_uncertainty"] != "UNVERIFIED_SEMANTIC_LABEL"
        or taxonomy["natural_language_inference_performed"] is not False
    ):
        raise DomainRejection("SIGNAL_EXTRACTION_UNCERTAINTY_MISSING")
    if (
        taxonomy["source_payload_sha256"] != source_payload_sha256
        or _domain_string_list(taxonomy["source_span_ids"]) != observation_claim_ids
    ):
        raise DomainRejection("OBSERVATION_SOURCE_BINDING_MISMATCH")
    primary_class = taxonomy["primary_class"]
    request_classes = {
        "EXPLICIT_HELP_REQUEST", "EXPLICIT_PRICE_INQUIRY",
        "EXPLICIT_PROCUREMENT_REQUEST",
    }
    non_request_classes = {
        "EXPLICIT_COMPLAINT", "BEHAVIORAL_TRACE",
        "WORKAROUND_OR_SELF_BUILT_ARTIFACT", "SOLUTION_EVOKED_RESPONSE",
        "NO_DIRECT_SIGNAL",
    }
    if primary_class in request_classes:
        expected_request_status = "HUMAN_ASSERTED_UNVERIFIED"
    elif primary_class in non_request_classes:
        expected_request_status = "NOT_ESTABLISHED"
    else:
        raise DomainRejection("SIGNAL_TAXONOMY_INCONSISTENT")
    if (
        taxonomy["explicit_request_status"] != expected_request_status
        or taxonomy["behavior_observation_status"]
        != "SYNTHETIC_NOT_REAL_WORLD"
    ):
        raise DomainRejection("SIGNAL_TAXONOMY_INCONSISTENT")

    if (
        first_lane["contamination_detected"] is not False
        or observation_lane["contamination_detected"] is not False
        or contamination["detected"] is not False
        or contamination["status"] != "CLEAR"
    ):
        raise DomainRejection("CONTAMINATION_DETECTED")
    detected_canaries = _domain_string_list(
        contamination["detected_canary_ids"], allow_empty=True
    )
    if detected_canaries:
        raise DomainRejection("CROSS_LANE_CANARY_DETECTED")

    first_seal_sequence = _domain_positive_int(first_lane["seal_sequence"])
    observation_seal_sequence = _domain_positive_int(
        observation_lane["seal_sequence"]
    )
    assessment_sequence = _domain_positive_int(contamination["assessment_sequence"])
    merge_sequence = _domain_positive_int(hypothesis["merge_sequence"])
    if first_seal_sequence >= merge_sequence:
        raise DomainRejection("FIRST_PRINCIPLES_NOT_PRESEALED")
    if observation_seal_sequence >= merge_sequence:
        raise DomainRejection("OBSERVATION_NOT_PRESEALED")
    if assessment_sequence >= merge_sequence:
        raise DomainRejection("CONTAMINATION_DETECTED")

    if hypothesis["status"] != "HYPOTHESIS_NOT_DEMAND_PROOF":
        raise DomainRejection("AUTHORITY_ESCALATION_FORBIDDEN")
    for key in (
        "candidate_buyer_class", "job_to_be_done", "statement",
        "applicability_scope", "weakest_assumption",
    ):
        _domain_string(hypothesis[key])
    _domain_string_list(hypothesis["competing_explanations"])
    if (
        _domain_string_list(hypothesis["supporting_observation_claim_ids"])
        != observation_claim_ids
    ):
        raise DomainRejection("PARENT_BINDING_MISMATCH")

    if experiment["status"] != "UNEXECUTED":
        raise DomainRejection("EXPERIMENT_EXECUTION_FORBIDDEN")
    if experiment["requires_new_explicit_authorization"] is not True:
        raise DomainRejection("EXPERIMENT_AUTHORIZATION_REQUIRED")
    if experiment["external_action_authority"] is not False:
        raise DomainRejection("AUTHORITY_ESCALATION_FORBIDDEN")
    for key in ("draft_method", "success_signal", "failure_signal"):
        _domain_string(experiment[key])
    if _domain_string_list(experiment["forbidden_capabilities"]) != [
        "ACCOUNT_ACCESS", "CONTACT", "DEPLOYMENT", "EXTERNAL_RETRIEVAL",
        "PAYMENT", "PRICING",
    ]:
        raise DomainRejection("AUTHORITY_ESCALATION_FORBIDDEN")

    if eval_spec["status"] != "NOT_RUN":
        raise DomainRejection("EVAL_EXECUTION_FORBIDDEN")
    if (
        eval_spec["fixture_type"] != "SYNTHETIC"
        or eval_spec["oracle_kind"]
        != "EXACT_RESULT_HASH_OR_STABLE_REJECTION_CODE"
        or eval_spec["external_action_authority"] is not False
    ):
        raise DomainRejection("AUTHORITY_ESCALATION_FORBIDDEN")
    for key in ("model_binding_sha256", "harness_binding_sha256"):
        if not isinstance(eval_spec[key], str) or not SHA256_RE.fullmatch(eval_spec[key]):
            raise DomainRejection("DOMAIN_TYPE_MISMATCH")
    _domain_string(eval_spec["human_baseline"])
    _domain_string(eval_spec["cost_record"])

    authority = _domain_object(record["authority"], AUTHORITY_KEYS)
    if any(value is not False for value in authority.values()):
        raise DomainRejection("AUTHORITY_ESCALATION_FORBIDDEN")

    all_records = {
        item["record_id"]: item for item in (
            sampling_plan, sampling_freeze, acquisition, rights, first_lane,
            observation_lane, contamination, hypothesis, experiment, eval_spec,
        )
    }
    _domain_validate_parent_bindings(sampling_plan, [], all_records)
    _domain_validate_parent_bindings(sampling_freeze, [sampling_plan], all_records)
    _domain_validate_parent_bindings(
        acquisition, [sampling_plan, sampling_freeze], all_records
    )
    _domain_validate_parent_bindings(rights, [acquisition], all_records)
    _domain_validate_parent_bindings(
        first_lane, [sampling_plan, sampling_freeze], all_records
    )
    _domain_validate_parent_bindings(
        observation_lane, [acquisition, rights], all_records
    )
    _domain_validate_parent_bindings(
        contamination, [first_lane, observation_lane], all_records
    )
    _domain_validate_parent_bindings(
        hypothesis, [rights, first_lane, observation_lane, contamination],
        all_records,
    )
    _domain_validate_parent_bindings(
        experiment, [rights, hypothesis], all_records
    )
    _domain_validate_parent_bindings(
        eval_spec, [experiment, hypothesis], all_records
    )

    normalized_record = json.loads(canonical_bytes(record).decode("utf-8"))
    return {
        "schema_version": "otts.normalized-opportunity-record/1",
        "gate_id": "OTTS-OPPORTUNITY-SEMANTIC-GATE-1",
        "source_record_sha256": sha256_json(record),
        "derived_record_status": "CURRENT",
        "record": normalized_record,
        "semantic_boundary": {
            "structured_contract_valid": True,
            "natural_language_speech_act_inferred": False,
            "semantic_truth_of_human_labels_proven": False,
            "demand_proven": False,
            "market_validated": False,
            "customer_exists_proven": False,
            "price_validated": False,
            "revenue_proven": False,
        },
        "authority": {
            "capability_authority": False,
            "runtime_authority": False,
            "deployment_authority": False,
            "freeze_authority": False,
            "external_action_authority": False,
        },
    }


def _cas_path(cas_root: Path, digest: str) -> Path:
    require_sha(digest, "CAS digest")
    return cas_root / digest[:2] / digest[2:]


def _cas_usage(cas_root: Path, limits: Mapping[str, int]) -> tuple[int, int]:
    if not cas_root.exists():
        return 0, 0
    count = 0
    total = 0
    for current, directories, files in os.walk(cas_root, followlinks=False):
        current_path = Path(current)
        for name in directories:
            value = (current_path / name).lstat()
            if not stat.S_ISDIR(value.st_mode) or stat.S_ISLNK(value.st_mode):
                raise CapabilityError("CAS contains invalid directory")
        for name in files:
            value = (current_path / name).lstat()
            if not stat.S_ISREG(value.st_mode) or value.st_nlink != 1:
                raise CapabilityError("CAS contains invalid object")
            count += 1
            total += value.st_size
    if count > limits["max_cas_files"] or total > limits["max_cas_total_bytes"]:
        raise CapabilityError("CAS existing usage exceeds fixed quota")
    return count, total


def cas_put_bytes(cas_root: Path, data: bytes, limits: Mapping[str, int]) -> str:
    if len(data) > limits["max_output_bytes"]:
        raise CapabilityError("CAS object exceeds output byte limit")
    digest = sha256_bytes(data)
    count, total = _cas_usage(cas_root, limits)
    target = _cas_path(cas_root, digest)
    target_exists = target.exists()
    if not target_exists and (
        count + 1 > limits["max_cas_files"] or
        total + len(data) > limits["max_cas_total_bytes"]
    ):
        raise CapabilityError("CAS put would exceed fixed file or total-byte quota")
    parent = cas_root / digest[:2]
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(target, flags, 0o400)
    except FileExistsError:
        existing = read_once_regular(target, "existing CAS object", limits["max_output_bytes"])
        if existing.sha256 != digest or existing.data != data:
            raise CapabilityError("CAS existing object is corrupt")
        return digest
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise CapabilityError("CAS short write")
            view = view[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    stored = read_once_regular(target, "new CAS object", limits["max_output_bytes"])
    if stored.sha256 != digest or stored.data != data:
        raise CapabilityError("CAS write verification failed")
    return digest


def cas_get_bytes(cas_root: Path, digest: str, limits: Mapping[str, int]) -> bytes:
    snapshot = read_once_regular(_cas_path(cas_root, digest), "CAS object", limits["max_output_bytes"])
    if snapshot.sha256 != digest:
        raise CapabilityError("CAS object digest mismatch")
    return snapshot.data


def evaluate_program(
    program: dict[str, Any], fixture: Any, policy: dict[str, Any], cas_root: Path,
    expected_parent_candidate_sha256: Optional[str] = None,
) -> tuple[Any, int]:
    validate_program(program, policy)
    _check_json_limits(fixture, policy["limits"], "fixture")
    by_id = {node["id"]: node for node in program["nodes"]}
    values: dict[str, Any] = {}
    steps = 0
    structural_value_bytes = 0

    def evaluate(node_id: str) -> Any:
        nonlocal steps, structural_value_bytes
        if node_id in values:
            return values[node_id]
        steps += 1
        if steps > policy["limits"]["max_steps"]:
            raise CapabilityError("program step limit exceeded")
        node = by_id[node_id]
        op = node["op"]
        try:
            if op == "INPUT":
                value = fixture
            elif op == "VALIDATE_OPPORTUNITY_RECORD":
                value = validate_opportunity_record(
                    evaluate(node["source"]), expected_parent_candidate_sha256
                )
            elif op == "CAS_PUT":
                value = cas_put_bytes(
                    cas_root, canonical_bytes(evaluate(node["source"])),
                    policy["limits"],
                )
            elif op == "CAS_GET":
                digest = evaluate(node["digest_ref"])
                if not isinstance(digest, str):
                    raise CapabilityError("CAS_GET digest_ref must evaluate to string")
                data = cas_get_bytes(cas_root, digest, policy["limits"])
                value = _json_from_bytes(data, "CAS object")
                if canonical_bytes(value) != data:
                    raise CapabilityError("CAS object is not canonical compact JSON")
            else:  # Exact validation makes this unreachable; no data-driven dispatch.
                raise CapabilityError("validated opcode invariant violated")
        except DomainRejection as exc:
            exc.steps = steps
            raise
        _check_json_limits(value, policy["limits"], f"node {node_id} output")
        value_size = len(canonical_bytes(value))
        if value_size > policy["limits"]["max_output_bytes"]:
            raise CapabilityError(f"node {node_id} output byte limit exceeded")
        structural_value_bytes += value_size
        if structural_value_bytes > policy["limits"]["max_structural_value_bytes_total"]:
            raise CapabilityError("program structural value byte total exceeded")
        values[node_id] = value
        return value

    result = evaluate(program["result_ref"])
    return result, steps


def _snapshot_ledger(snapshots: Mapping[str, Snapshot]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "sha256": snapshot.sha256,
            "stat_identity": list(snapshot.stat_identity),
        }
        for path, snapshot in sorted(snapshots.items())
    ]


def build_snapshot_ledger(
    *, entries: Mapping[str, tuple[dict[str, Any], Snapshot]],
    policy_snapshot: Snapshot, runner_snapshot: Snapshot,
) -> dict[str, Any]:
    operational = []
    for path, (entry, snapshot) in sorted(entries.items()):
        if entry.get("role") not in {"ir-program", "ir-test-program", "fixture"}:
            continue
        operational.append({
            "path": path,
            "role": entry["role"],
            "byte_length": len(snapshot.data),
            "original_snapshot_sha256": snapshot.sha256,
            "staged_sha256": snapshot.sha256,
        })
    return {
        "schema_version": "otts.shadow-snapshot-ledger/2",
        "operational_artifacts": operational,
        "policy": {
            "byte_length": len(policy_snapshot.data),
            "sha256": policy_snapshot.sha256,
        },
        "runner": {
            "byte_length": len(runner_snapshot.data),
            "sha256": runner_snapshot.sha256,
        },
        "derived_reports_excluded_to_avoid_digest_cycle": True,
        "execution_transport": "RUNNER_OPENED_VERIFIED_UNLINKED_READ_ONLY_FDS",
        "same_uid_concurrent_mutation_resistance_proven": False,
        "external_action_authority": False,
    }


def _trusted_binary_snapshot(path: Path, label: str) -> Snapshot:
    """Snapshot a system TCB file; unlike artifact input, system hardlinks are allowed."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise CapabilityError(f"{label}: cannot open trusted runtime: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 128 * 1024 * 1024:
            raise CapabilityError(f"{label}: trusted runtime object invalid")
        blocks: list[bytes] = []
        while True:
            block = os.read(fd, 1024 * 1024)
            if not block:
                break
            blocks.append(block)
        after = os.fstat(fd)
        data = b"".join(blocks)
        if _identity(before) != _identity(after) or len(data) != before.st_size:
            raise CapabilityError(f"{label}: trusted runtime mutated during read")
        return Snapshot(data, sha256_bytes(data), _identity(after), str(path))
    finally:
        os.close(fd)


def _runtime_security_chain() -> list[dict[str, Any]]:
    anchor = TRUSTED_RUNTIME_ANCHOR
    targets = (TRUSTED_PYTHON_HOME, TRUSTED_PYTHON)
    rows: dict[str, dict[str, Any]] = {}
    for target in targets:
        try:
            relative = target.relative_to(anchor)
        except ValueError as exc:
            raise CapabilityError("trusted runtime target escapes Xcode trust anchor") from exc
        cursor = anchor
        for part in (Path("."), *relative.parts):
            if part != Path("."):
                cursor /= str(part)
            if str(cursor) in rows:
                continue
            try:
                value = cursor.lstat()
            except OSError as exc:
                raise CapabilityError(f"trusted runtime chain missing: {cursor}") from exc
            if stat.S_ISLNK(value.st_mode):
                raise CapabilityError(f"trusted runtime chain symlink forbidden: {cursor}")
            if value.st_uid != 0 or stat.S_IMODE(value.st_mode) & 0o022:
                raise CapabilityError(
                    f"trusted runtime chain must be root-owned and non-group/other-writable: {cursor}"
                )
            rows[str(cursor)] = {
                "path": str(cursor), "uid": value.st_uid, "gid": value.st_gid,
                "mode": format(stat.S_IMODE(value.st_mode), "04o"),
                "device": value.st_dev, "inode": value.st_ino,
                "node_type": "directory" if stat.S_ISDIR(value.st_mode) else "regular-file",
            }
    if not stat.S_ISREG(TRUSTED_PYTHON.lstat().st_mode):
        raise CapabilityError("trusted Python runtime is not regular file")
    return [rows[key] for key in sorted(rows)]


def _applications_ancestor_residual() -> dict[str, Any]:
    path = Path("/Applications")
    value = path.lstat()
    groups = sorted(set(os.getgroups()) | {os.getgid()})
    try:
        group_name = grp.getgrgid(value.st_gid).gr_name
    except KeyError:
        group_name = "UNKNOWN"
    return {
        "path": str(path), "uid": value.st_uid, "gid": value.st_gid,
        "group_name": group_name,
        "mode": format(stat.S_IMODE(value.st_mode), "04o"),
        "group_writable": bool(stat.S_IMODE(value.st_mode) & 0o020),
        "current_uid": os.getuid(), "current_groups": groups,
        "current_process_is_member_of_parent_group": value.st_gid in groups,
        "threat_model_status": "EXCLUDED_HOSTILE_SAME_UID_OR_ADMIN_RACE_AND_RESTORE",
    }


def runtime_tcb_document(runner_snapshot: Snapshot) -> dict[str, Any]:
    security_chain = _runtime_security_chain()
    python_snapshot = _trusted_binary_snapshot(TRUSTED_PYTHON, "trusted Python")
    sandbox_snapshot = _trusted_binary_snapshot(SANDBOX_EXEC, "sandbox-exec")
    host = os.uname()
    return {
        "schema_version": "otts.shadow-runtime-tcb/2",
        "runner_sha256": runner_snapshot.sha256,
        "python_runtime": {
            "path": str(TRUSTED_PYTHON), "sha256": python_snapshot.sha256,
            "home": str(TRUSTED_PYTHON_HOME),
            "anchor": str(TRUSTED_RUNTIME_ANCHOR),
            "anchor_to_runtime_security_chain": security_chain,
            "anchor_to_runtime_security_digest_sha256": sha256_json(security_chain),
        },
        "applications_parent_ancestor_residual": _applications_ancestor_residual(),
        "sandbox_exec": {
            "path": str(SANDBOX_EXEC), "sha256": sandbox_snapshot.sha256,
            "support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
        },
        "profile_template_sha256": sha256_bytes(SANDBOX_PROFILE_TEMPLATE.encode("utf-8")),
        "host": {
            "sysname": host.sysname, "release": host.release,
            "version": host.version, "machine": host.machine,
            "validator_process_python_version": sys.version,
            "validator_process_python_implementation_cache_tag": sys.implementation.cache_tag,
        },
        "loaded_python_module_file_closure": "BOUND_AFTER_WORKER_EXECUTION",
        "full_dynamic_library_and_host_runtime_closure_proven": False,
        "same_uid_concurrent_mutation_resistance_proven": False,
        "external_action_authority": False,
    }


def _entry_map(
    shadow_root: Path,
    shadow: dict[str, Any],
    policy: dict[str, Any],
    entry_snapshots: Optional[Mapping[str, Snapshot]],
) -> dict[str, tuple[dict[str, Any], Snapshot]]:
    entries = shadow.get("entries")
    if (
        not isinstance(entries, list) or not entries or
        len(entries) > policy["limits"]["max_manifest_entries"]
    ):
        raise CapabilityError("shadow entries must be non-empty and within fixed limit")
    result: dict[str, tuple[dict[str, Any], Snapshot]] = {}
    limits = policy["limits"]
    total_input_bytes = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise CapabilityError(f"entries[{index}]: expected object")
        relative, _ = _normalized_parts(entry.get("path"), f"entries[{index}].path")
        if relative in result:
            raise CapabilityError(f"entries[{index}]: duplicate path")
        role = entry.get("role")
        max_bytes = (
            limits["max_artifact_bytes"] if role in {"ir-program", "ir-test-program"}
            else limits["max_fixture_bytes"] if role == "fixture"
            else limits["max_report_bytes"]
        )
        if entry_snapshots is None:
            _, snapshot = read_once_member(
                shadow_root, relative, f"entries[{index}].path", max_bytes
            )
        else:
            snapshot = entry_snapshots.get(relative)  # type: ignore[assignment]
            if not isinstance(snapshot, Snapshot):
                raise CapabilityError(f"entries[{index}]: missing supplied snapshot")
            _require_snapshot_integrity(snapshot, f"entries[{index}]", max_bytes)
        expected = require_sha(entry.get("sha256"), f"entries[{index}].sha256")
        if snapshot.sha256 != expected:
            raise CapabilityError(f"entries[{index}]: snapshot hash mismatch")
        total_input_bytes += len(snapshot.data)
        if total_input_bytes > limits["max_total_input_bytes"]:
            raise CapabilityError("manifest entry snapshots exceed fixed total input bytes")
        if stat.S_IMODE(snapshot.stat_identity[2]) & 0o111:
            raise CapabilityError(f"{relative}: executable mode bits are forbidden")
        suffix = PurePosixPath(relative).suffix.lower()
        if suffix in FORBIDDEN_ARTIFACT_SUFFIXES:
            raise CapabilityError(f"{relative}: executable/native suffix is forbidden")
        if role in {"ir-program", "ir-test-program"} and suffix not in set(policy["artifact_suffixes"]):
            raise CapabilityError(f"{relative}: artifact must use canonical JSON suffix")
        if role == "fixture" and suffix not in set(policy["fixture_suffixes"]):
            raise CapabilityError(f"{relative}: fixture suffix is not allowed")
        if role not in {"ir-program", "ir-test-program", "fixture"} and suffix not in set(policy["document_suffixes"]):
            raise CapabilityError(f"{relative}: document/report suffix is not allowed")
        result[relative] = (entry, snapshot)
    if entry_snapshots is not None and set(entry_snapshots) != set(result):
        raise CapabilityError("supplied entry snapshot set differs from manifest entries")
    return result


def build_static_reports(
    *, shadow_root: Path, shadow: dict[str, Any], policy_path: Path,
    entry_snapshots: Optional[Mapping[str, Snapshot]] = None,
    policy_snapshot: Optional[Snapshot] = None,
    runner_path: Optional[Path] = None,
    runner_snapshot: Optional[Snapshot] = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, tuple[dict[str, Any], Snapshot]]]:
    policy_snapshot = policy_snapshot or read_once_regular(
        policy_path, "capability_policy", 524288
    )
    policy = load_policy_snapshot(policy_snapshot)
    runner_path = runner_path or Path(__file__)
    runner_snapshot = runner_snapshot or read_once_regular(
        runner_path, "acceptance runner", 2 * 1024 * 1024
    )
    _require_snapshot_integrity(runner_snapshot, "acceptance runner", 2 * 1024 * 1024)
    if shadow.get("capability_policy_sha256") != policy_snapshot.sha256:
        raise CapabilityError("shadow capability policy hash mismatch")
    entries = _entry_map(shadow_root, shadow, policy, entry_snapshots)
    programs: list[dict[str, Any]] = []
    for relative, (entry, snapshot) in sorted(entries.items()):
        if entry.get("role") in {"ir-program", "ir-test-program"}:
            program = canonical_load_snapshot(snapshot, relative)
            graph = validate_program(program, policy)
            programs.append({
                "path": relative,
                "sha256": snapshot.sha256,
                "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
                "node_count": graph["node_count"],
            })
        elif entry.get("role") == "fixture":
            fixture = canonical_load_value_snapshot(snapshot, relative)
            _check_json_limits(fixture, policy["limits"], relative)
    if not programs:
        raise CapabilityError("shadow has no declarative IR program")
    snapshot_ledger = build_snapshot_ledger(
        entries=entries, policy_snapshot=policy_snapshot,
        runner_snapshot=runner_snapshot,
    )
    tcb = runtime_tcb_document(runner_snapshot)
    rejection_code_set_sha256 = sha256_json(sorted(DOMAIN_REJECTION_CODES))
    sbom = {
        "schema_version": "otts.shadow-declarative-sbom/2",
        "language_scope": "CANONICAL_JSON_CLOSED_OPPORTUNITY_SEMANTIC_GATE_ONLY",
        "programs": programs,
        "artifact_executable_or_native_dependency_count": 0,
        "trusted_runtime": "FIXED_RUNNER_AND_CPYTHON_OUTSIDE_ARTIFACT_SBOM",
        "external_action_authority": False,
    }
    capability_report = {
        "schema_version": "otts.shadow-capability-report/4",
        "policy_id": policy["policy_id"],
        "policy_sha256": policy_snapshot.sha256,
        "analysis_scope": "EXACT_SNAPSHOT_CLOSED_DOMAIN_GATE_SCHEMA_GRAPH_AND_REJECTION_CODE_SET",
        "programs": programs,
        "sbom_sha256": sha256_json(sbom),
        "snapshot_ledger_sha256": canonical_document_sha256(snapshot_ledger),
        "runtime_tcb_base_digest_sha256": sha256_json(tcb),
        "domain_gate_id": policy["domain_gate"]["gate_id"],
        "domain_gate_opcode": policy["domain_gate"]["opcode"],
        "domain_rejection_code_set_sha256": rejection_code_set_sha256,
        "required_acceptance_rejection_codes": sorted(
            REQUIRED_ACCEPTANCE_REJECTION_CODES
        ),
        "language_level_artifact_executable_constructs": "ABSENT_BY_EXACT_SCHEMA",
        "os_sandbox_observed_enforcement": "NOT_OBSERVED_STATIC_PHASE",
        "exact_opened_unlinked_snapshot_execution": "NOT_EXECUTED_STATIC_PHASE",
        "same_uid_concurrent_mutation_resistance_proven": False,
        "host_level_universal_noninterference_proven": False,
        "sandbox_inherited_fd_boundary": "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_BOUNDED_UNLINKED_STDIO_FDS; POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED",
        "sandbox_same_runtime_reexec_residual": "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; CLOSED_DOMAIN_IR_HAS_NO_EXEC_OPCODE",
        "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ONLY",
        "result": "CLOSED_OPPORTUNITY_SEMANTIC_GATE_LANGUAGE_VALID",
        "runtime_authority": False,
        "deployment_authority": False,
        "freeze_authority": False,
        "external_action_authority": False,
    }
    return sbom, capability_report, entries


def _stage_bytes(path: Path, data: bytes, mode: int = 0o400) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, mode)
    try:
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise CapabilityError("staging short write")
            view = view[written:]
        os.fsync(fd)
        os.fchmod(fd, mode)
    finally:
        os.close(fd)


def _verify_private_directories(directories: Sequence[Path]) -> None:
    owner = os.getuid()
    for path in directories:
        value = path.lstat()
        if (
            not stat.S_ISDIR(value.st_mode) or stat.S_ISLNK(value.st_mode) or
            value.st_uid != owner or stat.S_IMODE(value.st_mode) != 0o700
        ):
            raise CapabilityError(f"private staging directory invariant failed: {path}")


def _open_verified_unlinked_bytes(
    directory: Path, name: str, data: bytes, label: str,
) -> int:
    path = directory / name
    _stage_bytes(path, data, 0o400)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        snapshot = _snapshot_open_fd(fd, label, len(data), str(path))
        if snapshot.data != data or snapshot.sha256 != sha256_bytes(data):
            raise CapabilityError(f"{label}: staged bytes differ from opened snapshot")
        value = os.fstat(fd)
        if value.st_uid != os.getuid() or stat.S_IMODE(value.st_mode) != 0o400:
            raise CapabilityError(f"{label}: staged owner/mode invariant failed")
        path.unlink()
        after_unlink = os.fstat(fd)
        stable_before = (
            value.st_dev, value.st_ino, value.st_mode, value.st_uid, value.st_gid
        )
        stable_after = (
            after_unlink.st_dev, after_unlink.st_ino, after_unlink.st_mode,
            after_unlink.st_uid, after_unlink.st_gid,
        )
        if after_unlink.st_nlink != 0 or stable_before != stable_after:
            raise CapabilityError(f"{label}: unlink identity invariant failed")
        os.lseek(fd, 0, os.SEEK_SET)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _verify_unlinked_read_fd(fd: int, expected: Snapshot, label: str) -> None:
    actual = _snapshot_open_fd(
        fd, label, len(expected.data), f"opened-fd:{fd}", allowed_nlinks=(0,)
    )
    if actual.data != expected.data or actual.sha256 != expected.sha256:
        raise CapabilityError(f"{label}: opened unlinked bytes mismatch")
    value = os.fstat(fd)
    if value.st_uid != os.getuid() or stat.S_IMODE(value.st_mode) != 0o400:
        raise CapabilityError(f"{label}: opened unlinked owner/mode mismatch")


def _close_fds(fds: Sequence[int]) -> None:
    for fd in fds:
        try:
            os.close(fd)
        except OSError:
            pass


def _sbpl_literal(path: Path) -> str:
    if not path.is_absolute() or "\x00" in str(path) or "\n" in str(path) or "\r" in str(path):
        raise CapabilityError("sandbox profile path must be validated absolute path")
    return json.dumps(str(path), ensure_ascii=True)


def _sandbox_profile(*, output_dir: Path, probe_root: Path, runtime: Path) -> str:
    if output_dir.parent != probe_root:
        raise CapabilityError("sandbox output must be direct child of runner-private root")
    python_home = TRUSTED_PYTHON_HOME
    return SANDBOX_PROFILE_TEMPLATE.format(
        runtime=_sbpl_literal(runtime), python_home=_sbpl_literal(python_home),
        output_dir=_sbpl_literal(output_dir), probe_root=_sbpl_literal(probe_root),
    )


def _limit_process(limits: Mapping[str, int]) -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"], limits["cpu_seconds"]))
    resource.setrlimit(resource.RLIMIT_FSIZE, (limits["max_file_bytes"], limits["max_file_bytes"]))
    resource.setrlimit(resource.RLIMIT_NOFILE, (limits["max_open_files"], limits["max_open_files"]))
    if hasattr(resource, "RLIMIT_NPROC"):
        resource.setrlimit(resource.RLIMIT_NPROC, (limits["max_processes"], limits["max_processes"]))


def _open_unlinked_capture(root: Path, label: str) -> int:
    fd, raw_path = tempfile.mkstemp(prefix=f"{label}-", dir=root)
    path = Path(raw_path)
    os.fchmod(fd, 0o600)
    path.unlink()
    value = os.fstat(fd)
    if value.st_nlink != 0 or value.st_uid != os.getuid() or stat.S_IMODE(value.st_mode) != 0o600:
        os.close(fd)
        raise CapabilityError(f"{label}: capture FD invariant failed")
    return fd


def _read_capture(fd: int, label: str, max_bytes: int) -> bytes:
    snapshot = _snapshot_open_fd(
        fd, label, max_bytes, f"capture-fd:{fd}", allowed_nlinks=(0,)
    )
    return snapshot.data


def _invoke_sandbox(
    *, arguments: Sequence[str], profile: str, cwd: Path, runner_fd: int,
    inherited_fds: Sequence[int], limits: Mapping[str, int], timeout: int,
) -> tuple[int, bytes, bytes]:
    if not SANDBOX_EXEC.is_file() or not os.access(SANDBOX_EXEC, os.X_OK):
        raise CapabilityError("required /usr/bin/sandbox-exec is unavailable")
    if not TRUSTED_PYTHON.is_file() or not os.access(TRUSTED_PYTHON, os.X_OK):
        raise CapabilityError("fixed trusted Python runtime is unavailable")
    clean_env = {
        "HOME": str(cwd), "LC_ALL": "C", "LANG": "C",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
        "TMPDIR": str(cwd),
    }
    all_input_fds = tuple(dict.fromkeys((runner_fd, *inherited_fds)))
    before_identities = {fd: _identity(os.fstat(fd)) for fd in all_input_fds}
    for fd in all_input_fds:
        os.lseek(fd, 0, os.SEEK_SET)
    stdout_fd = _open_unlinked_capture(cwd, "stdout")
    stderr_fd = _open_unlinked_capture(cwd, "stderr")
    try:
        try:
            process = subprocess.Popen(
                [str(SANDBOX_EXEC), "-p", profile, str(TRUSTED_PYTHON), "-I", "-B", "-", *arguments],
                cwd=cwd, env=clean_env, stdin=runner_fd,
                stdout=stdout_fd, stderr=stderr_fd, close_fds=True,
                pass_fds=tuple(inherited_fds),
                start_new_session=True, preexec_fn=lambda: _limit_process(limits),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise CapabilityError(f"sandbox worker launch failed: {exc}") from exc
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            raise CapabilityError("sandbox worker wall timeout; process group killed") from exc
        for fd, before in before_identities.items():
            if _identity(os.fstat(fd)) != before:
                raise CapabilityError(f"opened input FD identity changed during sandbox run: {fd}")
        stdout = _read_capture(stdout_fd, "worker stdout", limits["max_stdout_bytes"])
        stderr = _read_capture(stderr_fd, "worker stderr", limits["max_stderr_bytes"])
        return returncode, stdout, stderr
    finally:
        _close_fds((stdout_fd, stderr_fd))


def _decode_worker_response(returncode: int, stdout: bytes, stderr: bytes, label: str) -> dict[str, Any]:
    if len(stdout.splitlines()) != 1:
        raise CapabilityError(
            f"{label}: expected exactly one bounded response line; "
            f"returncode={returncode}; stderr={stderr.decode('utf-8', 'replace')[:512]}"
        )
    try:
        response = json.loads(stdout.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CapabilityError(f"{label}: invalid worker response") from exc
    if returncode != 0 or not isinstance(response, dict) or response.get("ok") is not True:
        error = response.get("error") if isinstance(response, dict) else None
        raise CapabilityError(
            f"{label}: fail closed; returncode={returncode}; error={error}; "
            f"stderr={stderr.decode('utf-8', 'replace')[:512]}"
        )
    return response


def _validate_domain_worker_response(value: Any) -> dict[str, Any]:
    require_exact_keys(value, {
        "ok", "outcome", "result_sha256", "result_type",
        "result_byte_length", "rejection_code", "steps",
        "output_inventory_digest_sha256", "runtime_observation",
    }, "domain worker response")
    if value["ok"] is not True:
        raise CapabilityError("domain worker response did not complete safely")
    if (
        not isinstance(value["steps"], int)
        or isinstance(value["steps"], bool)
        or value["steps"] <= 0
    ):
        raise CapabilityError("domain worker response steps invalid")
    require_sha(
        value["output_inventory_digest_sha256"],
        "domain worker output inventory digest",
    )
    if value["outcome"] == "PASS":
        require_sha(value["result_sha256"], "domain worker result hash")
        if value["result_type"] != "object":
            raise CapabilityError("domain worker PASS must return normalized object")
        if (
            not isinstance(value["result_byte_length"], int)
            or isinstance(value["result_byte_length"], bool)
            or value["result_byte_length"] <= 0
        ):
            raise CapabilityError("domain worker PASS result length invalid")
        if value["rejection_code"] is not None:
            raise CapabilityError("domain worker PASS cannot include rejection code")
    elif value["outcome"] == "REJECT":
        if (
            value["result_sha256"] is not None
            or value["result_type"] is not None
            or value["result_byte_length"] is not None
        ):
            raise CapabilityError("domain worker REJECT cannot include a result")
        if value["rejection_code"] not in DOMAIN_REJECTION_CODES:
            raise CapabilityError("domain worker rejection code outside closed set")
    else:
        raise CapabilityError("domain worker outcome outside PASS/REJECT closed set")
    return value


def _validate_runtime_observation(value: Any) -> dict[str, Any]:
    keys = {
        "python_version", "python_implementation_cache_tag", "python_executable",
        "python_prefix", "loaded_module_files",
        "loaded_module_file_closure_digest_sha256", "closure_scope",
        "full_dynamic_library_and_host_runtime_closure_proven",
    }
    require_exact_keys(value, keys, "worker.runtime_observation")
    if value["python_executable"] != str(TRUSTED_PYTHON):
        raise CapabilityError("worker Python executable identity mismatch")
    if value["python_prefix"] != str(TRUSTED_PYTHON_HOME):
        raise CapabilityError("worker Python home identity mismatch")
    if value["python_implementation_cache_tag"] != "cpython-39":
        raise CapabilityError("worker Python implementation/cache tag mismatch")
    if not isinstance(value["python_version"], str) or not value["python_version"]:
        raise CapabilityError("worker Python version missing")
    if value["closure_scope"] != "ACTUALLY_LOADED_PYTHON_MODULE_FILES_AT_RESPONSE_MEASUREMENT":
        raise CapabilityError("worker loaded module closure scope mismatch")
    if value["full_dynamic_library_and_host_runtime_closure_proven"] is not False:
        raise CapabilityError("worker must not claim full dynamic/host closure")
    rows = value["loaded_module_files"]
    if not isinstance(rows, list) or not rows:
        raise CapabilityError("worker loaded module file closure must be non-empty")
    checked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        require_exact_keys(
            row, {"path", "sha256", "byte_length", "modules"},
            f"worker.runtime_observation.loaded_module_files[{index}]",
        )
        path_text = row["path"]
        if not isinstance(path_text, str) or path_text in seen:
            raise CapabilityError("worker loaded module path invalid or duplicate")
        seen.add(path_text)
        path = Path(path_text)
        try:
            path.relative_to(TRUSTED_PYTHON_HOME)
        except ValueError as exc:
            raise CapabilityError("worker loaded module path outside trusted home") from exc
        snapshot = _trusted_binary_snapshot(path, "worker-observed Python module")
        if row["sha256"] != snapshot.sha256 or row["byte_length"] != len(snapshot.data):
            raise CapabilityError("worker loaded module file hash/length mismatch")
        modules = row["modules"]
        if (
            not isinstance(modules, list) or not modules or
            any(not isinstance(name, str) or not name for name in modules) or
            modules != sorted(set(modules))
        ):
            raise CapabilityError("worker loaded module name set invalid")
        checked.append(row)
    if rows != sorted(rows, key=lambda item: item["path"]):
        raise CapabilityError("worker loaded module file closure is not sorted")
    digest = require_sha(
        value["loaded_module_file_closure_digest_sha256"],
        "worker loaded module file closure digest",
    )
    if digest != sha256_json(checked):
        raise CapabilityError("worker loaded module file closure digest mismatch")
    return value


def _run_required_probes(
    *, runner_fd: int, profile: str, root: Path,
    denied_read: Path, denied_write: Path, limits: Mapping[str, int],
    aggregate_deadline: float,
) -> dict[str, str]:
    probes = {
        "EXTERNAL_READ_DENIED": ("external-read", denied_read),
        "EXTERNAL_WRITE_DENIED": ("external-write", denied_write),
        "NETWORK_LOOPBACK_BIND_DENIED": ("network-socket", denied_read),
        "CHILD_PROCESS_DENIED": ("child-process", denied_read),
    }
    observed: dict[str, str] = {}
    for expected, (mode, target) in probes.items():
        remaining = aggregate_deadline - time.monotonic()
        if remaining <= 0:
            raise CapabilityError("aggregate acceptance wall timeout exceeded")
        returncode, stdout, stderr = _invoke_sandbox(
            arguments=["--trusted-probe", mode, "--probe-target", str(target)],
            profile=profile, cwd=root, runner_fd=runner_fd,
            inherited_fds=(), limits=limits,
            timeout=min(limits["wall_timeout_seconds"], remaining),
        )
        response = _decode_worker_response(returncode, stdout, stderr, f"probe {mode}")
        if response != {"denied": True, "ok": True, "probe": mode}:
            raise CapabilityError(f"probe {mode}: required denial was not observed")
        observed[expected] = "OBSERVED_DENIED"
    return observed


def _output_inventory(root: Path, limits: Mapping[str, int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total = 0
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directories:
            item = current_path / name
            value = item.lstat()
            if not stat.S_ISDIR(value.st_mode) or stat.S_ISLNK(value.st_mode):
                raise CapabilityError("runtime output contains invalid directory")
        for name in files:
            path = current_path / name
            snapshot = read_once_regular(path, "runtime output", limits["max_file_bytes"])
            total += len(snapshot.data)
            rows.append({
                "path": path.relative_to(root).as_posix(),
                "sha256": snapshot.sha256,
                "bytes": len(snapshot.data),
            })
            if len(rows) > limits["max_output_files"] or total > limits["max_output_total_bytes"]:
                raise CapabilityError("runtime output inventory quota exceeded")
    return sorted(rows, key=lambda row: row["path"])


def run_case(
    *, shadow_root: Path, program_path: Optional[Path] = None,
    fixture_path: Optional[Path] = None,
    program_snapshot: Optional[Snapshot] = None,
    fixture_snapshot: Optional[Snapshot] = None,
    policy_path: Optional[Path] = None,
    policy_snapshot: Optional[Snapshot] = None,
    runner_path: Optional[Path] = None,
    runner_snapshot: Optional[Snapshot] = None,
    aggregate_deadline: Optional[float] = None,
    expected_parent_candidate_sha256: Optional[str] = None,
) -> dict[str, Any]:
    """Evaluate exact opened-and-unlinked bytes through the fixed sandboxed runner.

    No artifact pathname is ever executed.
    """
    del shadow_root
    runner_path = runner_path or Path(__file__)
    runner_snapshot = runner_snapshot or read_once_regular(
        runner_path, "acceptance runner", 2 * 1024 * 1024
    )
    _require_snapshot_integrity(runner_snapshot, "acceptance runner", 2 * 1024 * 1024)
    if program_snapshot is None:
        if program_path is None:
            raise CapabilityError("run_case requires program snapshot or program_path")
        program_snapshot = read_once_regular(program_path, "program", 524288)
    _require_snapshot_integrity(program_snapshot, "program", FIXED_LIMITS["max_artifact_bytes"])
    if fixture_snapshot is None:
        if fixture_path is None:
            raise CapabilityError("run_case requires fixture snapshot or fixture_path")
        fixture_snapshot = read_once_regular(fixture_path, "fixture", 524288)
    _require_snapshot_integrity(fixture_snapshot, "fixture", FIXED_LIMITS["max_fixture_bytes"])
    if policy_snapshot is None:
        policy_path = policy_path or Path(__file__).with_name("SHADOW_CAPABILITY_POLICY.json")
        policy_snapshot = read_once_regular(policy_path, "capability_policy", 524288)
    policy = load_policy_snapshot(policy_snapshot)
    if expected_parent_candidate_sha256 is not None:
        require_sha(
            expected_parent_candidate_sha256,
            "expected parent candidate manifest hash",
        )
    if aggregate_deadline is None:
        aggregate_deadline = (
            time.monotonic() + policy["limits"]["aggregate_wall_timeout_seconds"]
        )
    if time.monotonic() > aggregate_deadline:
        raise CapabilityError("aggregate acceptance wall timeout exceeded")
    program = canonical_load_snapshot(program_snapshot, "program")
    fixture = canonical_load_value_snapshot(fixture_snapshot, "fixture")
    graph = validate_program(program, policy)
    _check_json_limits(fixture, policy["limits"], "fixture")
    runtime_tcb_before = runtime_tcb_document(runner_snapshot)

    with tempfile.TemporaryDirectory(prefix="otts-declarative-shadow-") as temporary:
        root = Path(temporary).resolve()
        os.chmod(root, 0o700)
        staged = root / "staged"
        output = root / "output"
        denied = root / "denied"
        for directory in (staged, output, denied):
            directory.mkdir(mode=0o700)
        denied_read = denied / "secret.txt"
        denied_write = denied / "forbidden.txt"
        _stage_bytes(denied_read, b"sandbox probe secret\n")
        _verify_private_directories([root, staged, output, denied])
        directory_identities = {
            str(path): _directory_identity(path) for path in (root, staged, output, denied)
        }
        opened_fds: list[int] = []
        runner_fd = _open_verified_unlinked_bytes(
            staged, "runner.py", runner_snapshot.data, "staged runner"
        )
        opened_fds.append(runner_fd)
        program_fd = _open_verified_unlinked_bytes(
            staged, "program.json", program_snapshot.data, "staged program"
        )
        opened_fds.append(program_fd)
        fixture_fd = _open_verified_unlinked_bytes(
            staged, "fixture.json", fixture_snapshot.data, "staged fixture"
        )
        opened_fds.append(fixture_fd)
        policy_fd = _open_verified_unlinked_bytes(
            staged, "policy.json", policy_snapshot.data, "staged policy"
        )
        opened_fds.append(policy_fd)
        request = {
            "expected_parent_candidate_sha256": expected_parent_candidate_sha256,
            "fixture_fd": fixture_fd,
            "fixture_sha256": fixture_snapshot.sha256,
            "output_root": str(output),
            "policy_fd": policy_fd,
            "policy_sha256": policy_snapshot.sha256,
            "program_fd": program_fd,
            "program_sha256": program_snapshot.sha256,
        }
        request_bytes = canonical_text(request).encode("utf-8")
        request_fd = _open_verified_unlinked_bytes(
            staged, "request.json", request_bytes, "staged request"
        )
        opened_fds.append(request_fd)
        profile = _sandbox_profile(
            output_dir=output, probe_root=root, runtime=TRUSTED_PYTHON
        )
        try:
            for fd, snapshot, label in (
                (runner_fd, runner_snapshot, "runner FD"),
                (program_fd, program_snapshot, "program FD"),
                (fixture_fd, fixture_snapshot, "fixture FD"),
                (policy_fd, policy_snapshot, "policy FD"),
            ):
                _verify_unlinked_read_fd(fd, snapshot, label)
            observed = _run_required_probes(
                runner_fd=runner_fd, profile=profile, root=root,
                denied_read=denied_read, denied_write=denied_write,
                limits=policy["limits"], aggregate_deadline=aggregate_deadline,
            )
            remaining = aggregate_deadline - time.monotonic()
            if remaining <= 0:
                raise CapabilityError("aggregate acceptance wall timeout exceeded")
            returncode, stdout, stderr = _invoke_sandbox(
                arguments=["--worker-fd", str(request_fd)],
                profile=profile, cwd=root, runner_fd=runner_fd,
                inherited_fds=(request_fd, program_fd, fixture_fd, policy_fd),
                limits=policy["limits"],
                timeout=min(policy["limits"]["wall_timeout_seconds"], remaining),
            )
            response = _decode_worker_response(
                returncode, stdout, stderr, "domain Gate worker"
            )
            response = _validate_domain_worker_response(response)
            response["runtime_observation"] = _validate_runtime_observation(
                response.get("runtime_observation")
            )
            inventory = _output_inventory(output, policy["limits"])
            if response.get("output_inventory_digest_sha256") != sha256_json(inventory):
                raise CapabilityError("worker output inventory binding mismatch")
            for path_text, before in directory_identities.items():
                if _directory_identity(Path(path_text)) != before:
                    raise CapabilityError(
                        f"runner-private directory identity changed during execution: {path_text}"
                    )
            if runtime_tcb_document(runner_snapshot) != runtime_tcb_before:
                raise CapabilityError("runtime TCB identity changed during execution")
            return {
                **response,
                "program_sha256": program_snapshot.sha256,
                "fixture_sha256": fixture_snapshot.sha256,
                "runner_sha256": runner_snapshot.sha256,
                "policy_sha256": policy_snapshot.sha256,
                "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
                "sandbox_observed_enforcement": observed,
                "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
                "exact_opened_unlinked_snapshot_execution": True,
                "staged_target_controlled_pathname_reopen_count": 0,
                "same_uid_concurrent_mutation_resistance_proven": False,
                "host_level_universal_noninterference_proven": False,
                "sandbox_inherited_fd_boundary": "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_BOUNDED_UNLINKED_STDIO_FDS; POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED",
                "sandbox_same_runtime_reexec_residual": "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; CLOSED_DOMAIN_IR_HAS_NO_EXEC_OPCODE",
                "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED",
            }
        finally:
            _close_fds(opened_fds)


def _file_ref(shadow: dict[str, Any], key: str) -> dict[str, str]:
    value = shadow.get(key)
    require_exact_keys(value, FILE_REF_KEYS, f"shadow.{key}")
    require_sha(value["sha256"], f"shadow.{key}.sha256")
    _normalized_parts(value["path"], f"shadow.{key}.path")
    return value


def validate_acceptance_case(case: Any, label: str) -> dict[str, Any]:
    if not isinstance(case, dict):
        raise CapabilityError(f"{label}: expected object")
    outcome = case.get("expected_outcome")
    if outcome == "PASS":
        require_exact_keys(case, PASS_CASE_KEYS, label)
        require_sha(case["expected_result_sha256"], f"{label}.expected_result_sha256")
    elif outcome == "REJECT":
        require_exact_keys(case, REJECT_CASE_KEYS, label)
        if case["expected_rejection_code"] not in DOMAIN_REJECTION_CODES:
            raise CapabilityError(f"{label}.expected_rejection_code outside closed set")
    else:
        raise CapabilityError(f"{label}.expected_outcome must be PASS or REJECT")
    case_id = case["case_id"]
    if not isinstance(case_id, str) or not IDENTIFIER_RE.fullmatch(case_id):
        raise CapabilityError(f"{label}.case_id invalid")
    _normalized_parts(case["fixture_path"], f"{label}.fixture_path")
    return case


def _validate_supplied_report(
    *, shadow: dict[str, Any], key: str, expected: dict[str, Any],
    entries: Mapping[str, tuple[dict[str, Any], Snapshot]],
) -> Snapshot:
    ref = _file_ref(shadow, key)
    if ref["path"] not in entries:
        raise CapabilityError(f"shadow.{key}: report is not a manifest entry")
    snapshot = entries[ref["path"]][1]
    if snapshot.sha256 != ref["sha256"]:
        raise CapabilityError(f"shadow.{key}: hash mismatch")
    supplied = canonical_load_snapshot(snapshot, key)
    if supplied != expected:
        raise CapabilityError(f"{key}: supplied report differs from deterministic reconstruction")
    return snapshot


def validate_shadow_acceptance(
    *, shadow_root: Path, shadow: dict[str, Any], policy_path: Path,
    runner_path: Optional[Path] = None,
    entry_snapshots: Optional[Mapping[str, Snapshot]] = None,
    policy_snapshot: Optional[Snapshot] = None,
    runner_snapshot: Optional[Snapshot] = None,
) -> dict[str, Any]:
    aggregate_started = time.monotonic()
    policy_snapshot = policy_snapshot or read_once_regular(
        policy_path, "capability_policy", 524288
    )
    runner_path = runner_path or Path(__file__)
    runner_snapshot = runner_snapshot or read_once_regular(
        runner_path, "acceptance runner", 2 * 1024 * 1024
    )
    policy = load_policy_snapshot(policy_snapshot)
    aggregate_deadline = (
        aggregate_started + policy["limits"]["aggregate_wall_timeout_seconds"]
    )

    def require_aggregate_time() -> None:
        if time.monotonic() > aggregate_deadline:
            raise CapabilityError("aggregate acceptance wall timeout exceeded")

    require_aggregate_time()
    sbom, capability_report, entries = build_static_reports(
        shadow_root=shadow_root, shadow=shadow, policy_path=policy_path,
        entry_snapshots=entry_snapshots, policy_snapshot=policy_snapshot,
        runner_path=runner_path, runner_snapshot=runner_snapshot,
    )
    snapshot_ledger = build_snapshot_ledger(
        entries=entries, policy_snapshot=policy_snapshot,
        runner_snapshot=runner_snapshot,
    )
    snapshot_ledger_snapshot = _validate_supplied_report(
        shadow=shadow, key="snapshot_ledger", expected=snapshot_ledger,
        entries=entries,
    )
    if entries[shadow["snapshot_ledger"]["path"]][0].get("role") != "snapshot-ledger":
        raise CapabilityError("shadow snapshot_ledger must resolve to snapshot-ledger role")
    snapshot_ledger_sha256 = snapshot_ledger_snapshot.sha256
    tcb = runtime_tcb_document(runner_snapshot)
    sbom_snapshot = _validate_supplied_report(
        shadow=shadow, key="sbom", expected=sbom, entries=entries
    )
    capability_report["sbom_sha256"] = sbom_snapshot.sha256
    capability_snapshot = _validate_supplied_report(
        shadow=shadow, key="capability_report", expected=capability_report,
        entries=entries,
    )
    program_relative, _ = _normalized_parts(shadow.get("program"), "shadow.program")
    if program_relative not in entries or entries[program_relative][0].get("role") != "ir-program":
        raise CapabilityError("program must resolve to a manifest-bound ir-program entry")
    program_snapshot = entries[program_relative][1]
    program = canonical_load_snapshot(program_snapshot, "manifest program")
    graph = validate_program(program, policy)
    cases = shadow.get("acceptance_cases")
    if (
        not isinstance(cases, list) or not cases or
        len(cases) > policy["limits"]["max_acceptance_cases"]
    ):
        raise CapabilityError("shadow.acceptance_cases must be non-empty and within fixed limit")
    parent_candidate_sha256 = require_sha(
        shadow.get("parent_candidate_manifest_sha256"),
        "shadow.parent_candidate_manifest_sha256",
    )
    case_ids: set[str] = set()
    prepared_cases: list[tuple[dict[str, Any], str, Snapshot]] = []
    expected_rejection_codes: set[str] = set()
    expected_pass_count = 0
    for index, case in enumerate(cases):
        label = f"acceptance_cases[{index}]"
        validated_case = validate_acceptance_case(case, label)
        case_id = validated_case["case_id"]
        if case_id in case_ids:
            raise CapabilityError(f"{label}.case_id invalid or duplicate")
        case_ids.add(case_id)
        fixture_relative, _ = _normalized_parts(
            validated_case["fixture_path"], f"{label}.fixture_path"
        )
        if (
            fixture_relative not in entries
            or entries[fixture_relative][0].get("role") != "fixture"
        ):
            raise CapabilityError("acceptance fixture must be a manifest-bound fixture entry")
        if validated_case["expected_outcome"] == "PASS":
            expected_pass_count += 1
        else:
            expected_rejection_codes.add(
                validated_case["expected_rejection_code"]
            )
        prepared_cases.append(
            (validated_case, fixture_relative, entries[fixture_relative][1])
        )
    if expected_pass_count < 1:
        raise CapabilityError("acceptance suite must contain at least one PASS case")
    missing_rejection_coverage = sorted(
        REQUIRED_ACCEPTANCE_REJECTION_CODES - expected_rejection_codes
    )
    if missing_rejection_coverage:
        raise CapabilityError(
            "acceptance suite missing required domain rejection coverage: "
            f"{missing_rejection_coverage}"
        )

    case_results: list[dict[str, Any]] = []
    observed_binding: Optional[dict[str, str]] = None
    runtime_observation_binding: Optional[dict[str, Any]] = None
    actual_pass_count = 0
    actual_reject_count = 0
    for case, fixture_relative, fixture_snapshot in prepared_cases:
        require_aggregate_time()
        case_id = case["case_id"]
        response = run_case(
            shadow_root=shadow_root, program_snapshot=program_snapshot,
            fixture_snapshot=fixture_snapshot, policy_snapshot=policy_snapshot,
            runner_snapshot=runner_snapshot,
            aggregate_deadline=aggregate_deadline,
            expected_parent_candidate_sha256=parent_candidate_sha256,
        )
        require_aggregate_time()
        expected_outcome = case["expected_outcome"]
        actual_outcome = response["outcome"]
        if actual_outcome != expected_outcome:
            raise CapabilityError(
                f"acceptance case {case_id}: outcome mismatch; "
                f"expected={expected_outcome}; actual={actual_outcome}; "
                f"actual_rejection_code={response['rejection_code']}"
            )
        if expected_outcome == "PASS":
            expected_result_sha256 = case["expected_result_sha256"]
            if response["result_sha256"] != expected_result_sha256:
                raise CapabilityError(
                    f"acceptance case {case_id}: result hash mismatch; "
                    f"expected={expected_result_sha256}; "
                    f"actual={response['result_sha256']}"
                )
            expected_rejection_code: Optional[str] = None
            actual_pass_count += 1
        else:
            expected_result_sha256 = None
            expected_rejection_code = case["expected_rejection_code"]
            if response["rejection_code"] != expected_rejection_code:
                raise CapabilityError(
                    f"acceptance case {case_id}: rejection code mismatch; "
                    f"expected={expected_rejection_code}; "
                    f"actual={response['rejection_code']}"
                )
            actual_reject_count += 1
        if observed_binding is None:
            observed_binding = response["sandbox_observed_enforcement"]
        elif observed_binding != response["sandbox_observed_enforcement"]:
            raise CapabilityError("sandbox observation differs across cases")
        if runtime_observation_binding is None:
            runtime_observation_binding = response["runtime_observation"]
        elif runtime_observation_binding != response["runtime_observation"]:
            raise CapabilityError("loaded Python module closure differs across cases")
        case_results.append({
            "case_id": case_id,
            "fixture_path": fixture_relative,
            "fixture_sha256": fixture_snapshot.sha256,
            "expected_outcome": expected_outcome,
            "actual_outcome": actual_outcome,
            "expected_result_sha256": expected_result_sha256,
            "actual_result_sha256": response["result_sha256"],
            "expected_rejection_code": expected_rejection_code,
            "actual_rejection_code": response["rejection_code"],
            "result_type": response["result_type"],
            "result_byte_length": response["result_byte_length"],
            "steps": response["steps"],
            "output_inventory_digest_sha256": response["output_inventory_digest_sha256"],
            "loaded_module_file_closure_digest_sha256": response["runtime_observation"][
                "loaded_module_file_closure_digest_sha256"
            ],
        })
    if runtime_observation_binding is None:
        raise CapabilityError("runtime observation missing")
    tcb["loaded_python_module_file_closure"] = runtime_observation_binding
    runtime_tcb_digest_sha256 = sha256_json(tcb)
    acceptance_output_set_digest_sha256 = sha256_json(case_results)
    test_report = {
        "schema_version": "otts.shadow-acceptance-test-report/4",
        "result": "LOCAL_DETERMINISTIC_DOMAIN_GATE_ACCEPTANCE_PASS",
        "runner_sha256": runner_snapshot.sha256,
        "policy_sha256": policy_snapshot.sha256,
        "parent_candidate_manifest_sha256": parent_candidate_sha256,
        "sbom_sha256": sbom_snapshot.sha256,
        "capability_report_sha256": capability_snapshot.sha256,
        "program_sha256": program_snapshot.sha256,
        "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
        "snapshot_ledger_sha256": snapshot_ledger_sha256,
        "runtime_tcb_digest_sha256": runtime_tcb_digest_sha256,
        "loaded_module_file_closure_digest_sha256": runtime_observation_binding[
            "loaded_module_file_closure_digest_sha256"
        ],
        "acceptance_output_set_digest_sha256": acceptance_output_set_digest_sha256,
        "domain_gate_id": policy["domain_gate"]["gate_id"],
        "domain_rejection_code_set_sha256": sha256_json(
            sorted(DOMAIN_REJECTION_CODES)
        ),
        "required_acceptance_rejection_codes": sorted(
            REQUIRED_ACCEPTANCE_REJECTION_CODES
        ),
        "pass_case_count": actual_pass_count,
        "reject_case_count": actual_reject_count,
        "program": program_relative,
        "cases": case_results,
        "language_level_artifact_executable_constructs": "ABSENT_BY_EXACT_SCHEMA",
        "os_sandbox_observed_enforcement": observed_binding,
        "sandbox_support_status": "DEPRECATED_UNSUPPORTED_DEFENSE_IN_DEPTH",
        "exact_opened_unlinked_snapshot_execution": True,
        "staged_target_controlled_pathname_reopen_count": 0,
        "same_uid_concurrent_mutation_resistance_proven": False,
        "host_level_universal_noninterference_proven": False,
        "sandbox_inherited_fd_boundary": "PARENT_CONFIGURED_ONLY_RUNNER_OPENED_UNLINKED_READ_FDS_AND_BOUNDED_UNLINKED_STDIO_FDS; POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED",
        "sandbox_same_runtime_reexec_residual": "EXACT_RUNTIME_PROCESS_EXEC_IS_ALLOWED_FOR_INITIAL_LAUNCH; CLOSED_DOMAIN_IR_HAS_NO_EXEC_OPCODE",
        "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED",
        "natural_language_speech_act_inference_proven": False,
        "semantic_truth_of_human_labels_proven": False,
        "aggregate_deadline_enforced": True,
        "aggregate_wall_timeout_seconds": policy["limits"]["aggregate_wall_timeout_seconds"],
        "runtime_authority": False,
        "deployment_authority": False,
        "freeze_authority": False,
        "external_action_authority": False,
    }
    report_snapshot = _validate_supplied_report(
        shadow=shadow, key="acceptance_test_report", expected=test_report,
        entries=entries,
    )
    require_aggregate_time()
    snapshots = {path: snapshot for path, (_, snapshot) in entries.items()}
    return {
        "sbom_sha256": sbom_snapshot.sha256,
        "capability_report_sha256": capability_snapshot.sha256,
        "acceptance_test_report_sha256": report_snapshot.sha256,
        "runner_sha256": runner_snapshot.sha256,
        "policy_sha256": policy_snapshot.sha256,
        "parent_candidate_manifest_sha256": parent_candidate_sha256,
        "program_sha256": program_snapshot.sha256,
        "node_graph_digest_sha256": graph["node_graph_digest_sha256"],
        "snapshot_ledger_document": snapshot_ledger,
        "snapshot_ledger_sha256": snapshot_ledger_sha256,
        "runtime_tcb_document": tcb,
        "runtime_tcb_digest_sha256": runtime_tcb_digest_sha256,
        "loaded_module_file_closure_digest_sha256": runtime_observation_binding[
            "loaded_module_file_closure_digest_sha256"
        ],
        "acceptance_output_set_digest_sha256": acceptance_output_set_digest_sha256,
        "domain_rejection_code_set_sha256": sha256_json(
            sorted(DOMAIN_REJECTION_CODES)
        ),
        "snapshot_ledger": _snapshot_ledger(snapshots),
        "case_count": len(case_results),
        "pass_case_count": actual_pass_count,
        "reject_case_count": actual_reject_count,
        "local_deterministic_domain_gate_acceptance_pass": True,
        "exact_opened_unlinked_snapshot_execution": True,
        "staged_target_controlled_pathname_reopen_count": 0,
        "same_uid_concurrent_mutation_resistance_proven": False,
        "memory_boundary": "NO_HOST_RSS_LIMIT_ON_DARWIN; FIXED_STRUCTURAL_IR_BYTE_BOUNDS_ENFORCED",
        "aggregate_deadline_enforced": True,
        "aggregate_wall_timeout_seconds": policy["limits"]["aggregate_wall_timeout_seconds"],
        "host_level_universal_noninterference_proven": False,
        "natural_language_speech_act_inference_proven": False,
        "semantic_truth_of_human_labels_proven": False,
        "runtime_authority": False,
        "deployment_authority": False,
        "freeze_authority": False,
        "external_action_authority": False,
    }


def _snapshot_inherited_fd(fd: Any, label: str, max_bytes: int) -> Snapshot:
    if not isinstance(fd, int) or isinstance(fd, bool) or fd < 3:
        raise CapabilityError(f"{label}: expected inherited non-stdio FD")
    access_mode = fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE
    if access_mode != os.O_RDONLY:
        raise CapabilityError(f"{label}: inherited FD must be read-only")
    return _snapshot_open_fd(
        fd, label, max_bytes, f"inherited-fd:{fd}", allowed_nlinks=(0,)
    )


def _loaded_python_module_file_closure() -> dict[str, Any]:
    files: dict[str, set[str]] = {}
    for module_name, module in sorted(list(sys.modules.items())):
        raw = getattr(module, "__file__", None)
        if not isinstance(raw, str) or not raw or raw.startswith("<"):
            continue
        path = Path(raw).resolve()
        try:
            path.relative_to(TRUSTED_PYTHON_HOME)
        except ValueError as exc:
            raise CapabilityError(
                f"loaded Python module file outside trusted home: {module_name}"
            ) from exc
        files.setdefault(str(path), set()).add(module_name)
    rows = []
    for path_text, module_names in sorted(files.items()):
        snapshot = _trusted_binary_snapshot(Path(path_text), "loaded Python module file")
        rows.append({
            "path": path_text, "sha256": snapshot.sha256,
            "byte_length": len(snapshot.data), "modules": sorted(module_names),
        })
    return {
        "python_version": sys.version,
        "python_implementation_cache_tag": sys.implementation.cache_tag,
        "python_executable": sys.executable,
        "python_prefix": sys.prefix,
        "loaded_module_files": rows,
        "loaded_module_file_closure_digest_sha256": sha256_json(rows),
        "closure_scope": "ACTUALLY_LOADED_PYTHON_MODULE_FILES_AT_RESPONSE_MEASUREMENT",
        "full_dynamic_library_and_host_runtime_closure_proven": False,
    }


def _worker(request_fd: int) -> int:
    try:
        request_snapshot = _snapshot_inherited_fd(request_fd, "worker request", 65536)
        request = canonical_load_snapshot(request_snapshot, "worker request")
        require_exact_keys(request, {
            "expected_parent_candidate_sha256", "fixture_fd", "fixture_sha256",
            "output_root", "policy_fd", "policy_sha256", "program_fd",
            "program_sha256",
        }, "worker request")
        expected_parent_candidate_sha256 = request[
            "expected_parent_candidate_sha256"
        ]
        if expected_parent_candidate_sha256 is not None:
            require_sha(
                expected_parent_candidate_sha256,
                "worker expected parent candidate manifest hash",
            )
        inherited = [request["policy_fd"], request["program_fd"], request["fixture_fd"]]
        if len(set(inherited + [request_fd])) != 4:
            raise CapabilityError("worker inherited FDs must be distinct")
        policy_snapshot = _snapshot_inherited_fd(
            request["policy_fd"], "staged policy", FIXED_LIMITS["max_report_bytes"]
        )
        program_snapshot = _snapshot_inherited_fd(
            request["program_fd"], "staged program", FIXED_LIMITS["max_artifact_bytes"]
        )
        fixture_snapshot = _snapshot_inherited_fd(
            request["fixture_fd"], "staged fixture", FIXED_LIMITS["max_fixture_bytes"]
        )
        for name, snapshot in (
            ("policy", policy_snapshot), ("program", program_snapshot),
            ("fixture", fixture_snapshot),
        ):
            if snapshot.sha256 != require_sha(request[f"{name}_sha256"], f"request.{name}_sha256"):
                raise CapabilityError(f"staged {name} hash mismatch")
        policy = load_policy_snapshot(policy_snapshot)
        program = canonical_load_snapshot(program_snapshot, "staged program")
        fixture = canonical_load_value_snapshot(fixture_snapshot, "staged fixture")
        output_root = Path(request["output_root"])
        output_value = output_root.lstat()
        if (
            not output_root.is_absolute() or not stat.S_ISDIR(output_value.st_mode) or
            stat.S_ISLNK(output_value.st_mode) or output_value.st_uid != os.getuid() or
            stat.S_IMODE(output_value.st_mode) != 0o700
        ):
            raise CapabilityError("worker output root invariant failed")
        cas_root = output_root / "cas"
        cas_root.mkdir(mode=0o700)
        try:
            result, steps = evaluate_program(
                program, fixture, policy, cas_root,
                expected_parent_candidate_sha256,
            )
            result_bytes = canonical_bytes(result)
            outcome = "PASS"
            result_sha256: Optional[str] = sha256_bytes(result_bytes)
            result_type: Optional[str] = json_type_name(result)
            result_byte_length: Optional[int] = len(result_bytes)
            rejection_code: Optional[str] = None
        except DomainRejection as rejection:
            outcome = "REJECT"
            steps = rejection.steps
            result_sha256 = None
            result_type = None
            result_byte_length = None
            rejection_code = rejection.code
        inventory = _output_inventory(output_root, policy["limits"])
        runtime_observation = _loaded_python_module_file_closure()
        response = {
            "ok": True,
            "outcome": outcome,
            "result_sha256": result_sha256,
            "result_type": result_type,
            "result_byte_length": result_byte_length,
            "rejection_code": rejection_code,
            "steps": steps,
            "output_inventory_digest_sha256": sha256_json(inventory),
            "runtime_observation": runtime_observation,
        }
    except BaseException as exc:
        response = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(response, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return 0 if response["ok"] else 1


def _trusted_probe(mode: str, target: Path) -> int:
    try:
        if mode == "external-read":
            target.read_bytes()
        elif mode == "external-write":
            target.write_bytes(b"forbidden")
        elif mode == "network-socket":
            handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                handle.bind(("127.0.0.1", 0))
            finally:
                handle.close()
        elif mode == "child-process":
            child_pid = os.posix_spawn(
                str(TRUSTED_PYTHON),
                [str(TRUSTED_PYTHON), "-I", "-B", "-c", "pass"],
                {"LC_ALL": "C", "PYTHONDONTWRITEBYTECODE": "1"},
            )
            os.waitpid(child_pid, 0)
        else:
            raise CapabilityError("unknown trusted probe")
    except OSError as exc:
        if exc.errno in {errno.EPERM, errno.EACCES}:
            response = {"denied": True, "ok": True, "probe": mode}
            print(json.dumps(response, separators=(",", ":"), sort_keys=True))
            return 0
        response = {
            "denied": False, "error": f"unexpected errno {exc.errno}",
            "ok": False, "probe": mode,
        }
        print(json.dumps(response, separators=(",", ":"), sort_keys=True))
        return 1
    response = {"denied": False, "ok": False, "probe": mode}
    print(json.dumps(response, separators=(",", ":"), sort_keys=True))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-fd", type=int)
    parser.add_argument(
        "--trusted-probe",
        choices=["external-read", "external-write", "network-socket", "child-process"],
    )
    parser.add_argument("--probe-target", type=Path)
    args = parser.parse_args()
    if args.worker_fd is not None and args.trusted_probe is None and args.probe_target is None:
        return _worker(args.worker_fd)
    if args.worker_fd is None and args.trusted_probe is not None and args.probe_target is not None:
        return _trusted_probe(args.trusted_probe, args.probe_target)
    parser.error("exactly one trusted worker mode is required")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
