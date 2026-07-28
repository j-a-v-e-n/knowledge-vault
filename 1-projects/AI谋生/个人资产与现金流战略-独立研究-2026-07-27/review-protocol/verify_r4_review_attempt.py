#!/usr/bin/env python3
"""Deterministically verify an append-only R4 review attempt.

This verifier reads local JSON artifacts only.  It does not call a model or a
network service, mutate project state, or grant authority.  A successful
verification says only that the supplied checkpoints obey this receipt
protocol and bind the same bytes and identities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RAW_BYTES = "RAW_BYTES"
RAW_SERIALIZATION = "UTF8_JSON_INDENT_2_TRAILING_LF"
EXTRACTED_SERIALIZATION = "UTF8_JSON_SORT_KEYS_TRUE_COMPACT_TRAILING_LF"
REQUEST_SCHEMA = "R4_REVIEW_ATTEMPT_REQUEST_V1"
BLIND_SCHEMA = "R4_BLIND_ARTIFACT_V1"
CONFORMANCE_SCHEMA = "R4_CONFORMANCE_RECEIPT_V1"
ADVERSARIAL_SCHEMA = "R4_ADVERSARIAL_RECEIPT_V1"
SUCCESSOR_SCHEMA = "R4_REVIEW_SUCCESSOR_V1"
STAGE_ORDER = [
    "BLIND_GENERATION",
    "CONFORMANCE_REVIEW",
    "ADVERSARIAL_REVIEW",
    "SUCCESSOR",
]
PASS_RULE = (
    "CANDIDATE_AND_CONFORMANCE_PASS_AND_ADVERSARIAL_PASS_"
    "WITH_ZERO_CRITICAL_AND_ZERO_MAJOR"
)
REQUIRED_SUCCESSOR_FIELDS = [
    "predecessor_state_sha256",
    "state_id",
    "status",
    "claim_ceiling",
    "review_outcome",
    "permissions",
    "primary_action",
    "next_action",
    "workflow_activation",
]
STATUS_MAPPING = {
    "PASS": "R4_REVIEW_PASS_BLOCKED_OWNER_CONSTRAINT",
    "FAIL": "R4_REVIEW_FAIL",
}
STATE_ID_MAPPING = {
    "PASS": "PORTFOLIO-BLUEPRINT-R4-REVIEWED-PASS",
    "FAIL": "PORTFOLIO-BLUEPRINT-R4-REVIEWED-FAIL",
}
CLAIM_CEILING_MAPPING = {
    "PASS": "R4_REVIEW_PASS_ONLY_NO_BUSINESS_WORKFLOW_ACTIVATION_OR_MODEL_PORTABILITY_CLAIM",
    "FAIL": "R4_REVIEW_FAIL_NO_BUSINESS_WORKFLOW_ACTIVATION_OR_MODEL_PORTABILITY_CLAIM",
}
ACTION_MAPPING = {
    "PASS": {
        "id": "PB-ACT-OWNER-CONSTRAINT",
        "effect_class": "USER_INPUT",
        "owner": "JAVEN",
    },
    "FAIL": {
        "id": "PB-ACT-R4-FAIL-BACKTRACK-ASSESSMENT",
        "effect_class": "READ_ONLY",
        "owner": "PRIMARY_AGENT",
    },
}
PASS_OWNER_CONSTRAINT_ACTION = ACTION_MAPPING["PASS"]
MUTABLE_PREDECESSOR_FIELDS = [
    "as_of",
    "state_id",
    "status",
    "claim_ceiling",
    "primary_action",
    "blockers",
]
DESIGN_CLOSURE_BLOCKING_MAPPING = {
    "PASS": [],
    "FAIL": ["R4_REVIEW_FAIL_REQUIRES_PB060_C_BACKTRACK_ASSESSMENT"],
}
REVIEWER_PERMISSIONS = {
    "read_bound_local_artifacts": True,
    "run_required_local_commands": True,
    "modify_project_files": False,
    "external_actions": False,
    "grant_authority": False,
}
_RFC3339 = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)

EXIT_VALID = 0
EXIT_VALID_SUCCESSOR_FAIL = 2
EXIT_MISSING_CHECKPOINT = 3
EXIT_IDENTITY_MISMATCH = 4
EXIT_INVALID_RECEIPT = 5
EXIT_INVALID_REQUEST = 6

_HEX = set("0123456789abcdef")


class ProtocolError(Exception):
    """A classified, fail-closed protocol error."""

    def __init__(self, classification: str, message: str):
        super().__init__(message)
        self.classification = classification


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def raw_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=False, indent=2) + "\n"
    ).encode("utf-8")


def canonical_extracted_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_protocol_json(path: Path, kind: str) -> tuple[dict[str, Any], bytes]:
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise ProtocolError("MISSING_CHECKPOINT", f"missing {kind}: {path}") from exc
    try:
        text = data.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ProtocolError("INVALID_RECEIPT", f"invalid {kind} JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_RECEIPT", f"{kind} must be a JSON object")
    if data != raw_json_bytes(value):
        raise ProtocolError(
            "INVALID_RECEIPT",
            f"{kind} is not serialized as {RAW_SERIALIZATION}",
        )
    return value, data


def _require_exact_keys(value: Any, expected: set[str], where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be an object")
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        raise ProtocolError(
            "INVALID_RECEIPT",
            f"{where} keys mismatch; missing={missing}, extra={extra}",
        )
    return value


def _require_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be a non-empty string")
    return value


def _require_sha256(value: Any, where: str) -> str:
    digest = _require_string(value, where)
    if len(digest) != 64 or any(char not in _HEX for char in digest):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be lowercase SHA-256")
    return digest


def artifact_ref(path: Path, serialization: str = RAW_BYTES) -> dict[str, Any]:
    if serialization not in {RAW_BYTES, RAW_SERIALIZATION}:
        raise ValueError(f"unsupported artifact serialization: {serialization}")
    resolved = path.resolve()
    data = resolved.read_bytes()
    if serialization == RAW_SERIALIZATION:
        _read_protocol_json(resolved, "protocol artifact reference")
    return {
        "path": str(resolved),
        "sha256": sha256_bytes(data),
        "byte_length": len(data),
        "serialization": serialization,
    }


def protocol_artifact_ref(path: Path) -> dict[str, Any]:
    return artifact_ref(path, RAW_SERIALIZATION)


def _validate_artifact_ref(value: Any, where: str) -> dict[str, Any]:
    ref = _require_exact_keys(
        value, {"path", "sha256", "byte_length", "serialization"}, where
    )
    raw_path = _require_string(ref["path"], f"{where}.path")
    path = Path(raw_path)
    if not path.is_absolute() or raw_path != str(path.resolve()):
        raise ProtocolError(
            "IDENTITY_MISMATCH", f"{where}.path must be an exact resolved absolute path"
        )
    _require_sha256(ref["sha256"], f"{where}.sha256")
    if isinstance(ref["byte_length"], bool) or not isinstance(ref["byte_length"], int):
        raise ProtocolError("INVALID_RECEIPT", f"{where}.byte_length must be an integer")
    if ref["byte_length"] < 0:
        raise ProtocolError(
            "INVALID_RECEIPT", f"{where}.byte_length must be non-negative"
        )
    if ref["serialization"] not in {RAW_BYTES, RAW_SERIALIZATION}:
        raise ProtocolError(
            "INVALID_RECEIPT",
            f"{where}.serialization is not a closed-enum value",
        )
    return ref


def _match_artifact_ref(
    value: Any,
    actual_path: Path,
    where: str,
    expected_serialization: str | None = None,
) -> None:
    ref = _validate_artifact_ref(value, where)
    if expected_serialization is not None and ref["serialization"] != expected_serialization:
        raise ProtocolError(
            "INVALID_RECEIPT",
            f"{where}.serialization must be {expected_serialization}",
        )
    try:
        actual = artifact_ref(actual_path, ref["serialization"])
    except FileNotFoundError as exc:
        raise ProtocolError(
            "MISSING_CHECKPOINT", f"{where} target is missing: {actual_path}"
        ) from exc
    if ref != actual:
        raise ProtocolError(
            "IDENTITY_MISMATCH",
            f"{where} does not bind the exact path, hash, length, and serialization",
        )


def _validate_findings(value: Any, where: str) -> dict[str, list[Any]]:
    findings = _require_exact_keys(value, {"Critical", "Major", "Minor"}, where)
    for severity in ("Critical", "Major", "Minor"):
        items = findings[severity]
        if not isinstance(items, list):
            raise ProtocolError(
                "INVALID_RECEIPT", f"{where}.{severity} must be an array"
            )
        for index, item in enumerate(items):
            finding = _require_exact_keys(
                item, {"id", "summary"}, f"{where}.{severity}[{index}]"
            )
            _require_string(finding["id"], f"{where}.{severity}[{index}].id")
            _require_string(
                finding["summary"], f"{where}.{severity}[{index}].summary"
            )
    return findings


def _zero_blocking(findings: dict[str, list[Any]]) -> bool:
    return not findings["Critical"] and not findings["Major"]


def _validate_string_array(value: Any, where: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be a non-empty string array")
    if any(not isinstance(item, str) or not item for item in value):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must not contain duplicates")
    return value


def _validate_named_refs(value: Any, where: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be an array")
    roles: set[str] = set()
    for index, item in enumerate(value):
        entry = _require_exact_keys(item, {"role", "artifact"}, f"{where}[{index}]")
        role = _require_string(entry["role"], f"{where}[{index}].role")
        if role in roles:
            raise ProtocolError("INVALID_RECEIPT", f"duplicate {where} role: {role}")
        roles.add(role)
        ref = _validate_artifact_ref(entry["artifact"], f"{where}[{index}].artifact")
        _match_artifact_ref(ref, Path(ref["path"]), f"{where}[{index}].artifact")
    return value


def _validate_successor_contract(value: Any) -> dict[str, Any]:
    contract = _require_exact_keys(
        value,
        {
            "required_portfolio_state_fields",
            "status_mapping",
            "mutable_predecessor_fields",
            "state_id_mapping",
            "claim_ceiling_mapping",
            "action_mapping",
            "design_closure_blocking_mapping",
            "blocked_workflow_activation_value",
        },
        "request.successor_contract",
    )
    if contract["required_portfolio_state_fields"] != REQUIRED_SUCCESSOR_FIELDS:
        raise ProtocolError(
            "INVALID_RECEIPT", "successor required state fields are not exact"
        )
    if contract["status_mapping"] != STATUS_MAPPING:
        raise ProtocolError("INVALID_RECEIPT", "successor status mapping is not exact")
    if contract["mutable_predecessor_fields"] != MUTABLE_PREDECESSOR_FIELDS:
        raise ProtocolError("INVALID_RECEIPT", "successor mutable fields are not exact")
    if contract["state_id_mapping"] != STATE_ID_MAPPING:
        raise ProtocolError("INVALID_RECEIPT", "successor state_id mapping is not exact")
    if contract["claim_ceiling_mapping"] != CLAIM_CEILING_MAPPING:
        raise ProtocolError("INVALID_RECEIPT", "successor claim ceiling mapping is not exact")
    if contract["action_mapping"] != ACTION_MAPPING:
        raise ProtocolError("INVALID_RECEIPT", "successor action mapping is not exact")
    if contract["design_closure_blocking_mapping"] != DESIGN_CLOSURE_BLOCKING_MAPPING:
        raise ProtocolError(
            "INVALID_RECEIPT", "successor design closure blocker mapping is not exact"
        )
    if contract["blocked_workflow_activation_value"] != "BLOCKED":
        raise ProtocolError(
            "INVALID_RECEIPT", "blocked workflow activation value must be BLOCKED"
        )
    return contract


def _validate_request(path: Path) -> tuple[dict[str, Any], bytes]:
    request, data = _read_protocol_json(path, "request")
    try:
        request = _require_exact_keys(
            request,
            {
                "schema_version",
                "attempt_id",
                "serialization",
                "extracted_serialization",
                "stage_order",
                "pass_rule",
                "exact_identity",
                "protocol_artifacts",
                "historical_evidence",
                "review_scope",
                "required_commands",
                "reviewer_identities",
                "reviewer_permissions",
                "validator",
                "successor_contract",
            },
            "request",
        )
        if request["schema_version"] != REQUEST_SCHEMA:
            raise ProtocolError("INVALID_RECEIPT", "unsupported request schema_version")
        _require_string(request["attempt_id"], "request.attempt_id")
        if request["serialization"] != RAW_SERIALIZATION:
            raise ProtocolError(
                "INVALID_RECEIPT",
                f"request.serialization must be {RAW_SERIALIZATION}",
            )
        if request["extracted_serialization"] != EXTRACTED_SERIALIZATION:
            raise ProtocolError(
                "INVALID_RECEIPT",
                f"request.extracted_serialization must be {EXTRACTED_SERIALIZATION}",
            )
        if request["stage_order"] != STAGE_ORDER:
            raise ProtocolError("INVALID_RECEIPT", "request.stage_order is not exact")
        if request["pass_rule"] != PASS_RULE:
            raise ProtocolError("INVALID_RECEIPT", "request.pass_rule is not exact")

        identities = _require_exact_keys(
            request["exact_identity"],
            {
                "blueprint",
                "state",
                "applicable_instructions",
                "blind_request",
                "task_class",
                "input_bundle",
            },
            "request.exact_identity",
        )
        for name, ref in identities.items():
            validated = _validate_artifact_ref(ref, f"request.exact_identity.{name}")
            _match_artifact_ref(
                validated,
                Path(validated["path"]),
                f"request.exact_identity.{name}",
            )

        _validate_named_refs(request["protocol_artifacts"], "request.protocol_artifacts")
        _validate_named_refs(request["historical_evidence"], "request.historical_evidence")
        _validate_string_array(request["review_scope"], "request.review_scope")
        _validate_string_array(request["required_commands"], "request.required_commands")

        reviewers = _require_exact_keys(
            request["reviewer_identities"],
            {"blind", "conformance", "adversarial"},
            "request.reviewer_identities",
        )
        for role, identity in reviewers.items():
            _require_string(identity, f"request.reviewer_identities.{role}")
        if len(set(reviewers.values())) != 3:
            raise ProtocolError(
                "INVALID_RECEIPT", "all reviewer identities must be distinct"
            )

        permissions = _require_exact_keys(
            request["reviewer_permissions"],
            set(REVIEWER_PERMISSIONS),
            "request.reviewer_permissions",
        )
        if permissions != REVIEWER_PERMISSIONS:
            raise ProtocolError("INVALID_RECEIPT", "reviewer permissions are not exact")

        validator = _require_exact_keys(
            request["validator"], {"command", "pass_result"}, "request.validator"
        )
        _require_string(validator["command"], "request.validator.command")
        pass_result = _require_exact_keys(
            validator["pass_result"],
            {"exit_code", "classification"},
            "request.validator.pass_result",
        )
        if pass_result["exit_code"] != 0:
            raise ProtocolError(
                "INVALID_RECEIPT", "request validator PASS exit_code must be 0"
            )
        _require_string(
            pass_result["classification"],
            "request.validator.pass_result.classification",
        )
        if validator["command"] not in request["required_commands"]:
            raise ProtocolError(
                "INVALID_RECEIPT", "validator command is absent from required_commands"
            )
        _validate_successor_contract(request["successor_contract"])
    except ProtocolError as exc:
        if exc.classification == "IDENTITY_MISMATCH":
            raise
        raise ProtocolError("INVALID_REQUEST", str(exc)) from exc
    return request, data


def _bound_identity(request: dict[str, Any], request_data: bytes) -> dict[str, str]:
    exact = request["exact_identity"]
    return {
        "blueprint_sha256": exact["blueprint"]["sha256"],
        "state_sha256": exact["state"]["sha256"],
        "applicable_instructions_sha256": exact["applicable_instructions"]["sha256"],
        "request_sha256": sha256_bytes(request_data),
        "blind_request_sha256": exact["blind_request"]["sha256"],
        "task_class_sha256": exact["task_class"]["sha256"],
        "input_bundle_sha256": exact["input_bundle"]["sha256"],
    }


def _match_bound_identity(
    value: Any, expected: dict[str, str], where: str
) -> None:
    bound = _require_exact_keys(value, set(expected), where)
    for key, digest in bound.items():
        _require_sha256(digest, f"{where}.{key}")
    if bound != expected:
        raise ProtocolError("IDENTITY_MISMATCH", f"{where} drifted from request")


def _validate_blind(
    path: Path, request: dict[str, Any], request_data: bytes
) -> tuple[dict[str, Any], bytes, str, Any]:
    blind, data = _read_protocol_json(path, "blind artifact")
    blind = _require_exact_keys(
        blind,
        {
            "schema_version",
            "attempt_id",
            "role",
            "reviewer_task_identity",
            "verdict",
            "candidate_output",
            "refusal_output",
            "attestation",
        },
        "blind",
    )
    if blind["schema_version"] != BLIND_SCHEMA or blind["role"] != "BLIND_GENERATOR":
        raise ProtocolError("INVALID_RECEIPT", "invalid blind schema or role")
    if blind["attempt_id"] != request["attempt_id"]:
        raise ProtocolError("IDENTITY_MISMATCH", "blind attempt_id mismatch")
    if blind["reviewer_task_identity"] != request["reviewer_identities"]["blind"]:
        raise ProtocolError("IDENTITY_MISMATCH", "blind reviewer identity mismatch")
    verdict = blind["verdict"]
    if verdict not in {"CANDIDATE_RECOVERY", "REFUSAL"}:
        raise ProtocolError("INVALID_RECEIPT", "blind verdict is not closed-enum")
    payload_key = "candidate_output" if verdict == "CANDIDATE_RECOVERY" else "refusal_output"
    payload = blind[payload_key]
    inactive_key = "refusal_output" if verdict == "CANDIDATE_RECOVERY" else "candidate_output"
    if blind[inactive_key] is not None:
        raise ProtocolError("INVALID_RECEIPT", f"blind.{inactive_key} must be null")
    if not isinstance(payload, dict):
        raise ProtocolError("INVALID_RECEIPT", f"blind.{payload_key} must be an object")
    if verdict == "REFUSAL":
        refusal = _require_exact_keys(
            payload,
            {"task_class_id", "qualification_status", "reason"},
            "blind.refusal_output",
        )
        if refusal["task_class_id"] != "TASK_PROJECT_RECOVERY_READ_ONLY":
            raise ProtocolError("INVALID_RECEIPT", "refusal task_class_id is not exact")
        if refusal["qualification_status"] != "REFUSED":
            raise ProtocolError("INVALID_RECEIPT", "refusal qualification_status is not exact")
        _require_string(refusal["reason"], "blind.refusal_output.reason")

    attestation = _require_exact_keys(
        blind["attestation"],
        {
            "bound_identity",
            "commands_used",
            "forbidden_content_opened_or_hashed",
            "file_modifications",
            "external_actions",
            "findings",
        },
        "blind.attestation",
    )
    _match_bound_identity(
        attestation["bound_identity"],
        _bound_identity(request, request_data),
        "blind.attestation.bound_identity",
    )
    if not isinstance(attestation["commands_used"], list) or any(
        not isinstance(command, str) or not command
        for command in attestation["commands_used"]
    ):
        raise ProtocolError(
            "INVALID_RECEIPT", "blind.attestation.commands_used must be strings"
        )
    for field in ("file_modifications", "external_actions"):
        if attestation[field] is not False:
            raise ProtocolError(
                "INVALID_RECEIPT", f"blind.attestation.{field} must be false"
            )
    forbidden = attestation["forbidden_content_opened_or_hashed"]
    if not isinstance(forbidden, bool):
        raise ProtocolError(
            "INVALID_RECEIPT",
            "blind.attestation.forbidden_content_opened_or_hashed must be boolean",
        )
    if verdict == "CANDIDATE_RECOVERY" and forbidden:
        raise ProtocolError(
            "INVALID_RECEIPT", "candidate blind artifact reports forbidden access"
        )
    if verdict == "REFUSAL":
        reason_is_tainted = payload["reason"].startswith("FAIL_TAINTED")
        if forbidden != reason_is_tainted:
            raise ProtocolError(
                "INVALID_RECEIPT",
                "tainted refusal requires both forbidden=true and FAIL_TAINTED reason",
            )
    _validate_findings(attestation["findings"], "blind.attestation.findings")
    return blind, data, payload_key, payload


def _validate_conformance(
    path: Path,
    request: dict[str, Any],
    request_data: bytes,
    blind_path: Path,
    blind: dict[str, Any],
    payload_key: str,
    payload: Any,
) -> tuple[dict[str, Any], bytes, dict[str, list[Any]]]:
    receipt, data = _read_protocol_json(path, "conformance receipt")
    receipt = _require_exact_keys(
        receipt,
        {
            "schema_version",
            "attempt_id",
            "role",
            "reviewer_task_identity",
            "blind_artifact",
            "extracted_payload",
            "bound_identity",
            "validator",
            "verdict",
            "findings",
        },
        "conformance",
    )
    if (
        receipt["schema_version"] != CONFORMANCE_SCHEMA
        or receipt["role"] != "CONFORMANCE_REVIEWER"
    ):
        raise ProtocolError("INVALID_RECEIPT", "invalid conformance schema or role")
    if receipt["attempt_id"] != request["attempt_id"]:
        raise ProtocolError("IDENTITY_MISMATCH", "conformance attempt_id mismatch")
    if receipt["reviewer_task_identity"] != request["reviewer_identities"]["conformance"]:
        raise ProtocolError("IDENTITY_MISMATCH", "conformance reviewer identity mismatch")
    _match_artifact_ref(
        receipt["blind_artifact"],
        blind_path,
        "conformance.blind_artifact",
        RAW_SERIALIZATION,
    )
    extracted = _require_exact_keys(
        receipt["extracted_payload"],
        {"kind", "sha256", "serialization"},
        "conformance.extracted_payload",
    )
    if extracted["kind"] != payload_key:
        raise ProtocolError("IDENTITY_MISMATCH", "extracted payload kind mismatch")
    if extracted["serialization"] != EXTRACTED_SERIALIZATION:
        raise ProtocolError(
            "INVALID_RECEIPT",
            f"extracted serialization must be {EXTRACTED_SERIALIZATION}",
        )
    _require_sha256(extracted["sha256"], "conformance.extracted_payload.sha256")
    if extracted["sha256"] != sha256_bytes(canonical_extracted_bytes(payload)):
        raise ProtocolError("IDENTITY_MISMATCH", "extracted payload hash mismatch")
    _match_bound_identity(
        receipt["bound_identity"],
        _bound_identity(request, request_data),
        "conformance.bound_identity",
    )
    validator = _require_exact_keys(
        receipt["validator"], {"command", "result"}, "conformance.validator"
    )
    if validator["command"] != request["validator"]["command"]:
        raise ProtocolError("IDENTITY_MISMATCH", "validator command mismatch")
    result = _require_exact_keys(
        validator["result"],
        {"exit_code", "classification"},
        "conformance.validator.result",
    )
    if isinstance(result["exit_code"], bool) or not isinstance(result["exit_code"], int):
        raise ProtocolError("INVALID_RECEIPT", "validator exit_code must be an integer")
    _require_string(result["classification"], "validator result classification")
    verdict = receipt["verdict"]
    if verdict not in {"PASS", "FAIL"}:
        raise ProtocolError("INVALID_RECEIPT", "conformance verdict is not closed-enum")
    findings = _validate_findings(receipt["findings"], "conformance.findings")
    pass_result = request["validator"]["pass_result"]
    if verdict == "PASS":
        if blind["verdict"] != "CANDIDATE_RECOVERY":
            raise ProtocolError("INVALID_RECEIPT", "a refusal cannot receive conformance PASS")
        if result != pass_result:
            raise ProtocolError("INVALID_RECEIPT", "conformance PASS contradicts validator result")
        if not _zero_blocking(findings):
            raise ProtocolError("INVALID_RECEIPT", "conformance PASS has Critical or Major")
    else:
        if result == pass_result:
            raise ProtocolError("INVALID_RECEIPT", "conformance FAIL contradicts validator result")
        if _zero_blocking(findings):
            raise ProtocolError("INVALID_RECEIPT", "conformance FAIL needs Critical or Major")
    return receipt, data, findings


def _validate_adversarial(
    path: Path,
    request: dict[str, Any],
    request_data: bytes,
    blind_path: Path,
    conformance_path: Path,
) -> tuple[dict[str, Any], bytes, dict[str, list[Any]]]:
    receipt, data = _read_protocol_json(path, "adversarial receipt")
    receipt = _require_exact_keys(
        receipt,
        {
            "schema_version",
            "attempt_id",
            "role",
            "reviewer_task_identity",
            "blind_artifact",
            "conformance_receipt",
            "bound_identity",
            "verdict",
            "findings",
        },
        "adversarial",
    )
    if (
        receipt["schema_version"] != ADVERSARIAL_SCHEMA
        or receipt["role"] != "ADVERSARIAL_REVIEWER"
    ):
        raise ProtocolError("INVALID_RECEIPT", "invalid adversarial schema or role")
    if receipt["attempt_id"] != request["attempt_id"]:
        raise ProtocolError("IDENTITY_MISMATCH", "adversarial attempt_id mismatch")
    if receipt["reviewer_task_identity"] != request["reviewer_identities"]["adversarial"]:
        raise ProtocolError("IDENTITY_MISMATCH", "adversarial reviewer identity mismatch")
    _match_artifact_ref(
        receipt["blind_artifact"],
        blind_path,
        "adversarial.blind_artifact",
        RAW_SERIALIZATION,
    )
    _match_artifact_ref(
        receipt["conformance_receipt"],
        conformance_path,
        "adversarial.conformance_receipt",
        RAW_SERIALIZATION,
    )
    _match_bound_identity(
        receipt["bound_identity"],
        _bound_identity(request, request_data),
        "adversarial.bound_identity",
    )
    verdict = receipt["verdict"]
    if verdict not in {"PASS", "FAIL"}:
        raise ProtocolError("INVALID_RECEIPT", "adversarial verdict is not closed-enum")
    findings = _validate_findings(receipt["findings"], "adversarial.findings")
    if verdict == "PASS" and not _zero_blocking(findings):
        raise ProtocolError("INVALID_RECEIPT", "adversarial PASS has Critical or Major")
    if verdict == "FAIL" and _zero_blocking(findings):
        raise ProtocolError("INVALID_RECEIPT", "adversarial FAIL needs Critical or Major")
    return receipt, data, findings


def _expected_successor_state(
    blind: dict[str, Any],
    conformance: dict[str, Any] | None,
    adversarial: dict[str, Any] | None,
    conformance_findings: dict[str, list[Any]] | None,
    adversarial_findings: dict[str, list[Any]] | None,
) -> tuple[str, dict[str, Any]]:
    if blind["verdict"] == "REFUSAL":
        if conformance is not None or adversarial is not None:
            raise ProtocolError(
                "INVALID_RECEIPT", "refusal must skip conformance and adversarial"
            )
        reason = blind["refusal_output"]["reason"]
        return "FAIL", {
            "active": True,
            "stage": "BLIND_GENERATION",
            "reason": "BLIND_TAINTED" if reason.startswith("FAIL_TAINTED") else "BLIND_REFUSAL",
        }
    if conformance is None or conformance_findings is None:
        raise ProtocolError("MISSING_CHECKPOINT", "candidate path needs conformance receipt")
    if conformance["verdict"] == "FAIL":
        if adversarial is not None:
            raise ProtocolError(
                "INVALID_RECEIPT", "conformance FAIL must skip adversarial"
            )
        return "FAIL", {
            "active": True,
            "stage": "CONFORMANCE_REVIEW",
            "reason": "CONFORMANCE_FAIL",
        }
    if not _zero_blocking(conformance_findings):
        raise ProtocolError("INVALID_RECEIPT", "conformance signatory has blocking findings")
    if adversarial is None or adversarial_findings is None:
        raise ProtocolError("MISSING_CHECKPOINT", "candidate PASS path needs adversarial receipt")
    overall = "PASS" if adversarial["verdict"] == "PASS" else "FAIL"
    if overall == "PASS" and not _zero_blocking(adversarial_findings):
        raise ProtocolError("INVALID_RECEIPT", "adversarial signatory has blocking findings")
    return overall, {"active": False, "stage": None, "reason": None}


def _load_bound_state(request: dict[str, Any]) -> dict[str, Any]:
    ref = request["exact_identity"]["state"]
    path = Path(ref["path"])
    if ref["serialization"] == RAW_SERIALIZATION:
        state, _ = _read_protocol_json(path, "bound predecessor state")
        return state
    try:
        value = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_json_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ProtocolError(
            "INVALID_REQUEST", f"bound predecessor state is invalid JSON: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_REQUEST", "bound predecessor state must be an object")
    return value


def _validate_no_workflow_activation(value: Any, where: str = "portfolio_state_successor") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_where = f"{where}.{key}"
            if key in {"workflow_activation", "portfolio_activation"}:
                allowed = child is False or child is None or child in (
                    "BLOCKED",
                    "NOT_ACTIVATED",
                ) if isinstance(child, (str, bool)) or child is None else False
                if not allowed:
                    raise ProtocolError(
                        "INVALID_RECEIPT", f"{child_where} activates a workflow"
                    )
            elif key.endswith("_allowed_now") and child is not False:
                raise ProtocolError(
                    "INVALID_RECEIPT", f"{child_where} must remain false"
                )
            _validate_no_workflow_activation(child, child_where)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _validate_no_workflow_activation(child, f"{where}[{index}]")


def _parse_rfc3339(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not _RFC3339.fullmatch(value):
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be strict RFC3339")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProtocolError("INVALID_RECEIPT", f"{where} must be strict RFC3339") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProtocolError("INVALID_RECEIPT", f"{where} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _validate_portfolio_state_successor(
    state: Any,
    predecessor: dict[str, Any],
    request: dict[str, Any],
    blind_path: Path,
    conformance_path: Path | None,
    adversarial_path: Path | None,
    overall: str,
    short_circuit: dict[str, Any],
    top_artifacts: dict[str, Any],
) -> str:
    if not isinstance(state, dict):
        raise ProtocolError("INVALID_RECEIPT", "portfolio_state_successor must be an object")
    contract = request["successor_contract"]
    missing = [field for field in contract["required_portfolio_state_fields"] if field not in state]
    if missing:
        raise ProtocolError(
            "INVALID_RECEIPT", f"portfolio_state_successor missing fields: {missing}"
        )
    expected_state_keys = set(predecessor) | {
        "predecessor_state_sha256",
        "review_outcome",
        "next_action",
        "workflow_activation",
    }
    if set(state) != expected_state_keys:
        raise ProtocolError(
            "INVALID_RECEIPT", "portfolio_state_successor top-level keys are not exact"
        )
    predecessor_sha = request["exact_identity"]["state"]["sha256"]
    if state["predecessor_state_sha256"] != predecessor_sha:
        raise ProtocolError("IDENTITY_MISMATCH", "successor predecessor_state_sha256 mismatch")
    if state["state_id"] != contract["state_id_mapping"][overall]:
        raise ProtocolError("INVALID_RECEIPT", "portfolio successor state_id mismatch")
    if state["claim_ceiling"] != contract["claim_ceiling_mapping"][overall]:
        raise ProtocolError("INVALID_RECEIPT", "portfolio successor claim_ceiling mismatch")
    expected_status = contract["status_mapping"][overall]
    if state["status"] != expected_status:
        raise ProtocolError("INVALID_RECEIPT", "portfolio successor status mismatch")

    predecessor_as_of = _parse_rfc3339(predecessor.get("as_of"), "predecessor.as_of")
    successor_as_of = _parse_rfc3339(state["as_of"], "portfolio_state_successor.as_of")
    if successor_as_of < predecessor_as_of:
        raise ProtocolError("INVALID_RECEIPT", "portfolio successor as_of precedes predecessor")

    predecessor_permissions = predecessor.get("permissions")
    permissions = state["permissions"]
    if not isinstance(predecessor_permissions, dict) or not isinstance(permissions, dict):
        raise ProtocolError("INVALID_RECEIPT", "predecessor and successor permissions must be objects")
    if set(permissions) != set(predecessor_permissions):
        raise ProtocolError("INVALID_RECEIPT", "successor permission keys must remain exact")
    for name, old_value in predecessor_permissions.items():
        new_value = permissions[name]
        if not isinstance(old_value, bool) or not isinstance(new_value, bool):
            raise ProtocolError("INVALID_RECEIPT", f"permission {name} must be boolean")
        if old_value is False and new_value is not False:
            raise ProtocolError("INVALID_RECEIPT", f"permission expansion: {name}")

    mutable_fields = set(contract["mutable_predecessor_fields"])
    for field, predecessor_value in predecessor.items():
        if field not in mutable_fields and state[field] != predecessor_value:
            raise ProtocolError(
                "INVALID_RECEIPT", f"immutable predecessor field changed: {field}"
            )

    predecessor_blockers = predecessor.get("blockers")
    successor_blockers = state["blockers"]
    if not isinstance(predecessor_blockers, dict) or not isinstance(successor_blockers, dict):
        raise ProtocolError("INVALID_RECEIPT", "predecessor and successor blockers must be objects")
    if set(successor_blockers) != set(predecessor_blockers):
        raise ProtocolError("INVALID_RECEIPT", "successor blocker keys must remain exact")
    if "design_closure_blocking" not in predecessor_blockers:
        raise ProtocolError("INVALID_RECEIPT", "predecessor blockers lack design_closure_blocking")
    for name, predecessor_value in predecessor_blockers.items():
        if name == "design_closure_blocking":
            if successor_blockers[name] != contract["design_closure_blocking_mapping"][overall]:
                raise ProtocolError(
                    "INVALID_RECEIPT", "successor design_closure_blocking mismatch"
                )
        elif successor_blockers[name] != predecessor_value:
            raise ProtocolError(
                "INVALID_RECEIPT", f"immutable predecessor blocker changed: {name}"
            )

    outcome = _require_exact_keys(
        state["review_outcome"],
        {"attempt_id", "overall_verdict", "short_circuit", "artifacts"},
        "portfolio_state_successor.review_outcome",
    )
    if outcome["attempt_id"] != request["attempt_id"]:
        raise ProtocolError("IDENTITY_MISMATCH", "embedded review outcome attempt mismatch")
    if outcome["overall_verdict"] != overall or outcome["short_circuit"] != short_circuit:
        raise ProtocolError("INVALID_RECEIPT", "embedded review outcome is not derived")
    embedded_artifacts = _require_exact_keys(
        outcome["artifacts"],
        {"blind", "conformance", "adversarial"},
        "portfolio_state_successor.review_outcome.artifacts",
    )
    if embedded_artifacts != top_artifacts:
        raise ProtocolError("IDENTITY_MISMATCH", "embedded artifact refs differ from outcome refs")
    _match_artifact_ref(
        embedded_artifacts["blind"], blind_path, "embedded artifacts blind", RAW_SERIALIZATION
    )
    if conformance_path is None:
        if embedded_artifacts["conformance"] is not None:
            raise ProtocolError("IDENTITY_MISMATCH", "embedded conformance must be null")
    else:
        _match_artifact_ref(
            embedded_artifacts["conformance"],
            conformance_path,
            "embedded artifacts conformance",
            RAW_SERIALIZATION,
        )
    if adversarial_path is None:
        if embedded_artifacts["adversarial"] is not None:
            raise ProtocolError("IDENTITY_MISMATCH", "embedded adversarial must be null")
    else:
        _match_artifact_ref(
            embedded_artifacts["adversarial"],
            adversarial_path,
            "embedded artifacts adversarial",
            RAW_SERIALIZATION,
        )

    if state["workflow_activation"] != contract["blocked_workflow_activation_value"]:
        raise ProtocolError("INVALID_RECEIPT", "workflow activation must remain blocked")
    _validate_no_workflow_activation(state)
    required_action = contract["action_mapping"][overall]
    for field in ("primary_action", "next_action"):
        if state[field] != required_action:
            raise ProtocolError(
                "INVALID_RECEIPT", f"portfolio successor {field} action mismatch"
            )

    return sha256_bytes(raw_json_bytes(state))


def _validate_successor(
    path: Path,
    request: dict[str, Any],
    request_data: bytes,
    blind_path: Path,
    conformance_path: Path | None,
    adversarial_path: Path | None,
    expected_overall: str,
    expected_short_circuit: dict[str, Any],
) -> tuple[dict[str, Any], bytes, str]:
    successor, data = _read_protocol_json(path, "successor")
    successor = _require_exact_keys(
        successor,
        {
            "schema_version",
            "attempt_id",
            "role",
            "artifacts",
            "bound_identity",
            "short_circuit",
            "overall_verdict",
            "portfolio_state_successor",
        },
        "successor",
    )
    if successor["schema_version"] != SUCCESSOR_SCHEMA or successor["role"] != "SUCCESSOR":
        raise ProtocolError("INVALID_RECEIPT", "invalid successor schema or role")
    if successor["attempt_id"] != request["attempt_id"]:
        raise ProtocolError("IDENTITY_MISMATCH", "successor attempt_id mismatch")
    artifacts = _require_exact_keys(
        successor["artifacts"],
        {"blind", "conformance", "adversarial"},
        "successor.artifacts",
    )
    _match_artifact_ref(
        artifacts["blind"], blind_path, "successor.artifacts.blind", RAW_SERIALIZATION
    )
    if conformance_path is None:
        if artifacts["conformance"] is not None:
            raise ProtocolError("IDENTITY_MISMATCH", "successor conformance must be null")
    else:
        if artifacts["conformance"] is None:
            raise ProtocolError("MISSING_CHECKPOINT", "successor omits conformance binding")
        _match_artifact_ref(
            artifacts["conformance"],
            conformance_path,
            "successor.artifacts.conformance",
            RAW_SERIALIZATION,
        )
    if adversarial_path is None:
        if artifacts["adversarial"] is not None:
            raise ProtocolError(
                "IDENTITY_MISMATCH", "successor must bind absent adversarial as null"
            )
    else:
        if artifacts["adversarial"] is None:
            raise ProtocolError("MISSING_CHECKPOINT", "successor omits adversarial binding")
        _match_artifact_ref(
            artifacts["adversarial"],
            adversarial_path,
            "successor.artifacts.adversarial",
            RAW_SERIALIZATION,
        )
    _match_bound_identity(
        successor["bound_identity"],
        _bound_identity(request, request_data),
        "successor.bound_identity",
    )
    short_circuit = _require_exact_keys(
        successor["short_circuit"],
        {"active", "stage", "reason"},
        "successor.short_circuit",
    )
    if short_circuit != expected_short_circuit:
        raise ProtocolError("INVALID_RECEIPT", "successor short_circuit is not derived")
    if successor["overall_verdict"] != expected_overall:
        raise ProtocolError("INVALID_RECEIPT", "successor overall_verdict is not derived")
    state_sha = _validate_portfolio_state_successor(
        successor["portfolio_state_successor"],
        _load_bound_state(request),
        request,
        blind_path,
        conformance_path,
        adversarial_path,
        expected_overall,
        expected_short_circuit,
        artifacts,
    )
    return successor, data, state_sha


def verify_attempt(
    request_path: Path,
    blind_path: Path,
    conformance_path: Path | None,
    adversarial_path: Path | None = None,
    successor_path: Path | None = None,
) -> tuple[int, dict[str, Any]]:
    try:
        request, request_data = _validate_request(request_path.resolve())
        blind, _, payload_key, payload = _validate_blind(
            blind_path.resolve(), request, request_data
        )
        conformance = None
        conformance_findings = None
        if blind["verdict"] == "REFUSAL":
            if conformance_path is not None or adversarial_path is not None:
                raise ProtocolError(
                    "INVALID_RECEIPT", "blind refusal must short-circuit later checkpoints"
                )
        else:
            if conformance_path is not None:
                conformance_path = conformance_path.resolve()
                conformance, _, conformance_findings = _validate_conformance(
                    conformance_path,
                    request,
                    request_data,
                    blind_path.resolve(),
                    blind,
                    payload_key,
                    payload,
                )

        adversarial = None
        adversarial_findings = None
        if adversarial_path is not None:
            if conformance_path is None:
                raise ProtocolError(
                    "MISSING_CHECKPOINT", "adversarial checkpoint lacks conformance"
                )
            adversarial_path = adversarial_path.resolve()
            adversarial, _, adversarial_findings = _validate_adversarial(
                adversarial_path,
                request,
                request_data,
                blind_path.resolve(),
                conformance_path,
            )

        if successor_path is None:
            if conformance is not None and conformance["verdict"] == "FAIL" and adversarial is not None:
                raise ProtocolError(
                    "INVALID_RECEIPT", "conformance FAIL cannot have adversarial checkpoint"
                )
            if blind["verdict"] == "REFUSAL" or conformance is None:
                stage = "BLIND_GENERATION"
            else:
                stage = "ADVERSARIAL_REVIEW" if adversarial is not None else "CONFORMANCE_REVIEW"
            return EXIT_VALID, {
                "classification": "VALID_CHECKPOINT",
                "attempt_id": request["attempt_id"],
                "last_verified_stage": stage,
                "authority_granted": False,
            }

        expected_overall, expected_short_circuit = _expected_successor_state(
            blind,
            conformance,
            adversarial,
            conformance_findings,
            adversarial_findings,
        )
        _, _, portfolio_state_successor_sha256 = _validate_successor(
            successor_path.resolve(),
            request,
            request_data,
            blind_path.resolve(),
            conformance_path,
            adversarial_path,
            expected_overall,
            expected_short_circuit,
        )
        classification = (
            "VALID_SUCCESSOR_PASS" if expected_overall == "PASS" else "VALID_SUCCESSOR_FAIL"
        )
        exit_code = EXIT_VALID if expected_overall == "PASS" else EXIT_VALID_SUCCESSOR_FAIL
        return exit_code, {
            "classification": classification,
            "attempt_id": request["attempt_id"],
            "overall_verdict": expected_overall,
            "portfolio_state_successor_sha256": portfolio_state_successor_sha256,
            "authority_granted": False,
        }
    except ProtocolError as exc:
        exit_codes = {
            "MISSING_CHECKPOINT": EXIT_MISSING_CHECKPOINT,
            "IDENTITY_MISMATCH": EXIT_IDENTITY_MISMATCH,
            "INVALID_RECEIPT": EXIT_INVALID_RECEIPT,
            "INVALID_REQUEST": EXIT_INVALID_REQUEST,
        }
        return exit_codes[exc.classification], {
            "classification": exc.classification,
            "error": str(exc),
            "authority_granted": False,
        }
    except (OSError, TypeError, KeyError) as exc:
        return EXIT_INVALID_RECEIPT, {
            "classification": "INVALID_RECEIPT",
            "error": f"unhandled invalid artifact: {exc}",
            "authority_granted": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--blind", type=Path, required=True)
    parser.add_argument("--conformance", type=Path)
    parser.add_argument("--adversarial", type=Path)
    parser.add_argument("--successor", type=Path)
    args = parser.parse_args()
    code, result = verify_attempt(
        args.request,
        args.blind,
        args.conformance,
        args.adversarial,
        args.successor,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
