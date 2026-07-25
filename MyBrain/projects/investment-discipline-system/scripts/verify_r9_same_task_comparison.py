#!/usr/bin/env python3
"""Verify that R9 remains a fail-closed, not-yet-executed preregistration.

A successful invocation proves only that the prelaunch control is intact and
that identifiable R9 execution material is absent. It does not run, pass, or
complete the method comparison, and it never authorizes generation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, NoReturn


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
PREREGISTRATION_RELATIVE = Path(
    "research/SAME_TASK_METHOD_COMPARISON_PREREGISTRATION_R9_2026-07-25.json"
)
CONTROL_ID = "R9-PRELAUNCH-FAIL-CLOSED-CONTROL-V1"

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "round_id",
    "status",
    "created_at_utc",
    "contains_execution_results",
    "prelaunch_readiness",
    "purpose",
    "predecessor_problem",
    "decision_scope",
    "estimand_and_contrast",
    "preregistration_freeze",
    "primary_design",
    "common_task",
    "frozen_corpus",
    "common_output_contract",
    "method_wrappers",
    "prompt_assembly",
    "package_and_tree_manifest",
    "execution_binding_contract",
    "resource_budget",
    "prelaunch_capability_preflight",
    "receipt_acceptance_contract",
    "judge_package_fit_preflight",
    "order_randomization_and_leakage_control",
    "blinding_and_review",
    "reviewer_locator_schema",
    "deterministic_pre_review_checks",
    "reference_anchors_for_judges",
    "evaluation_rubric",
    "continuous_outcomes_and_sensitivity",
    "cost_and_maintenance_accounting",
    "hash_and_locator_protocol",
    "additional_wrapper_admission_rule",
    "experiment_integrity_predicates",
    "stopping_and_failure_protocol",
    "result_reporting_requirements",
    "forbidden_actions_during_r9",
}

EXPECTED_READINESS_KEYS = {
    "state",
    "runtime_binding_present",
    "allocation_present",
    "capability_preflight_receipt_present",
    "judge_package_fit_receipts_present",
    "generation_authorized",
    "current_blocker",
    "resolution_rule",
}
EXPECTED_PAIR_IDS = [
    "R9-PAIR-01",
    "R9-PAIR-02",
    "R9-PAIR-03",
    "R9-PAIR-04",
]
EXPECTED_ARMS = [
    "common_contract_only",
    "common_contract_plus_minimum_core",
]
EXPECTED_SOURCE_IDS = [
    "R9-SRC-CRSP",
    "R9-SRC-NYSE",
    "R9-SRC-FACTSET",
    "R9-SRC-DB",
]
EXPECTED_SLICE_IDS = [f"R9-C{index:02d}" for index in range(1, 12)]
EXPECTED_CORPUS_ROOT = (
    "379ea29e5f981e6c014ba244c4970a66bd3c9f5ece8b4ac003db658015a2a4d1"
)
EXPECTED_TOTAL_SLICE_BYTES = 16512

EXPECTED_COMPONENT_HASHES = {
    "common_task": "1ebd4775fbfaf573eb125edd9694a4519d9e2e0113d7365441fa3d1476b39f87",
    "common_output_contract": (
        "187dfbc94c7aac7fd5a716663758d57f544edf134575022d3bda0dbc5da86f63"
    ),
    "wrapper.common_contract_only.model_visible": (
        "aa3a4ce3b9d27fdce20d421ede2cfddf82c951f78aee8f260450eb21332f7e25"
    ),
    "wrapper.common_contract_plus_minimum_core.model_visible": (
        "e4ec03ef668f2e8df8e31b88f9b97ab561d9e74a1a63a80609d7e59c4d7b9684"
    ),
    "frozen_corpus": (
        "26e5b2ad560eb657e3a3c5213a754cb5e49566791fab627f3ee21b6f180d0e1c"
    ),
    "package_and_tree_manifest": (
        "e98b1a5114894466f9c6bc2335fca6b3798de5882aae605ddb9aa8485cdb31cf"
    ),
    "execution_binding_contract": (
        "9bc85a5be7a2c037407709c936a1327653a6cbe279dc1c5bf9e216d141a83d2e"
    ),
    "resource_budget": (
        "02139a261cfaf450097699e54dba0a45a648ee8e4aa84c40307b7bb1c0eea304"
    ),
    "prelaunch_capability_preflight": (
        "c20a84173e03902e92eeb9d7f10894e3e65abd2853f1d9b90315fcd390dae56e"
    ),
    "receipt_acceptance_contract": (
        "3d3ef78971d15419ed1c400421443bb22d3ee5b613fc9344f10dc09ef81be2a8"
    ),
    "judge_package_fit_preflight": (
        "b91c0e9ee2e4efc73d3e4c08a404340aea521e71ff84a18f3cfa35c9a1829830"
    ),
    "evaluation_rubric": (
        "8da216adfe0f65cff054fbbc6b43eb5f59581eb59426abc16fbb05e650228c07"
    ),
    "reference_anchors_for_judges": (
        "94b63aaf3690a59b50ec982a302dd5b14c44b719b63d5a830e68ffe7995a58bf"
    ),
}

EXPECTED_SCHEMA_IDS = {
    "package_and_tree_manifest.tree_manifest_payload_schema.schema_id": (
        "R9-COMPLETE-TREE-MANIFEST-PAYLOAD-V2"
    ),
    "execution_binding_contract.schema_id": "R9-RUNTIME-BINDING-PAYLOAD-V2",
    "prelaunch_capability_preflight.schema_id": ("R9-CAPABILITY-PREFLIGHT-RECEIPT-V2"),
    "receipt_acceptance_contract.contract_id": ("R9-RESOURCE-AND-ATTEMPT-RECEIPT-V2"),
    "judge_package_fit_preflight.schema_id": (
        "R9-JUDGE-PACKAGE-FIT-PREFLIGHT-RECEIPT-V2"
    ),
    "hash_and_locator_protocol.generic_digest_sidecar_schema.schema_id": (
        "R9-ARTIFACT-DIGEST-SIDECAR-V2"
    ),
    "hash_and_locator_protocol.allocation_payload_schema.schema_id": (
        "R9-SEALED-ALLOCATION-PAYLOAD-V2"
    ),
    "hash_and_locator_protocol.input_manifest_schema.schema_id": (
        "R9-RUN-INPUT-MANIFEST-PAYLOAD-V2"
    ),
    "hash_and_locator_protocol.generation_output_receipt_schema.schema_id": (
        "R9-GENERATION-OUTPUT-RECEIPT-PAYLOAD-V2"
    ),
    "hash_and_locator_protocol.blind_review_package_schema.schema_id": (
        "R9-BLIND-REVIEW-PACKAGE-PAYLOAD-V2"
    ),
    "hash_and_locator_protocol.review_output_schema.schema_id": (
        "R9-BLIND-REVIEW-OUTPUT-PAYLOAD-V2"
    ),
    "hash_and_locator_protocol.final_result_schema.schema_id": (
        "R9-METHOD-COMPARISON-RESULT-PAYLOAD-V2"
    ),
}

EXPECTED_USAGE_FIELDS = [
    "pair_id",
    "request_slot_id",
    "blind_artifact_id",
    "full_request_raw_sha256",
    "provider_request_id_or_null",
    "provider_usage_payload_locator",
    "provider_usage_payload_raw_sha256",
    "input_tokens",
    "output_tokens",
    "total_accounted_tokens",
    "cached_input_tokens_or_null",
    "reasoning_tokens_or_null",
    "token_field_mapping_version",
    "usage_capture_status",
]
EXPECTED_TIMING_FIELDS = [
    "pair_id",
    "request_slot_id",
    "process_started_monotonic",
    "request_attempt_started_monotonic",
    "request_bytes_committed_monotonic_or_null",
    "first_response_byte_monotonic_or_null",
    "terminal_event_monotonic",
    "end_to_end_wall_milliseconds",
    "queue_or_transport_milliseconds_or_null",
    "provider_reported_generation_milliseconds_or_null",
    "clock_id",
    "recorder_version",
    "timing_capture_status",
]
EXPECTED_ATTEMPT_FIELDS = [
    "pair_id",
    "request_slot_id",
    "client_automatic_retry_limit",
    "fallback_enabled",
    "attempt_count",
    "retry_count",
    "attempt_event_log_locator",
    "attempt_event_log_raw_sha256",
    "terminal_class",
]
EXPECTED_CAPABILITY_RECEIPT_FIELDS = [
    "preflight_id",
    "created_at_utc",
    "harness_control_tree_manifest_payload_raw_sha256",
    "runtime_binding_payload_raw_sha256",
    "sandbox_profile_raw_sha256",
    "process_image_or_runtime_locator",
    "probe_case_ids",
    "per_probe_expected_result",
    "per_probe_observed_result",
    "per_probe_evidence_locator",
    "request_serialization_without_tools_raw_sha256",
    "automatic_retry_fault_probe_receipt_locator",
    "all_required_capabilities_passed",
    "preimage_excluded_fields",
]
EXPECTED_JUDGE_FIT_FIELDS = [
    "preflight_id",
    "created_at_utc",
    "judge_requested_configuration_raw_sha256",
    "reviewer_package_template_tree_manifest_payload_raw_sha256s",
    "tokenizer_name_version_and_raw_sha256_or_immutable_locator",
    "declared_judge_context_limit_tokens",
    "fixed_review_input_tokens",
    "generation_artifact_reserved_tokens",
    "artifact_envelope_overhead_tokens",
    "transport_framing_tokens",
    "judge_output_reserved_tokens",
    "worst_case_total_tokens",
    "fits_declared_context",
    "fits_judge_budget",
    "preimage_excluded_fields",
]
EXPECTED_TREE_MANIFEST_FIELDS = [
    "tree_id",
    "tree_role",
    "root_locator",
    "created_at_utc",
    "entry_count",
    "entries",
    "preimage_excluded_fields",
]
EXPECTED_TREE_ENTRY_FIELDS = [
    "relative_path",
    "entry_type",
    "mode_octal",
    "byte_count_or_null",
    "raw_sha256_or_null",
]
EXPECTED_SIDECAR_FIELDS = [
    "sidecar_schema_id",
    "target_role",
    "target_locator",
    "target_byte_count",
    "target_raw_sha256",
    "hash_algorithm",
    "created_at_utc",
    "preimage_excluded_fields",
]

READINESS_BLOCKER = (
    "本预注册只冻结方法，不包含 external independent stateless process harness、runtime "
    "binding、complete tree manifests、digest sidecars 或 capability/package-fit receipts；"
    "本项目父 task/thread 的 native subagent 明确不合格，因此现在不得启动 generation。"
)
READINESS_RESOLUTION = (
    "只能在任何输出前由符合本文件的外部隔离 harness 生成并冻结全部 required receipts 后"
    "把独立运行状态标为 ready；若能力 false、unknown 或平台无法提供，则保持 "
    "blocked_before_generation，并在 result payload 中记录 outcome = bounded_incomplete，"
    "不得回填本字段或降低标准。"
)
FAILED_PREFLIGHT_RULE = (
    "任何启动前 capability、tree completeness、configuration equality、receipt acceptance "
    "或 judge package-fit 门不能满足时，operational_state = blocked_before_generation，最终 "
    "outcome = bounded_incomplete；不得减少 replicate、改用父线程 native subagent、放宽隔离、"
    "缩小 reviewer package、换模型、改预算或降低标准。"
)
CAPABILITY_FAILURE_DISPOSITION = (
    "任一 probe false、unknown、不可执行或 receipt 不可恢复时，不启动任何 generation request，"
    "记录 operational_state = blocked_before_generation，并令最终 outcome = bounded_incomplete；"
    "不得使用本项目父线程 native subagent 或降低边界作为 fallback。"
)
JUDGE_FIT_FAILURE_DISPOSITION = (
    "任一 reviewer 的 package-fit preflight 失败或 unknown 时，启动前 "
    "blocked_before_generation 且最终 bounded_incomplete；不得删 artifact、摘要 artifact、"
    "拆成多轮 reviewer turns、减少 replicate、增大运行时 context 或改 judge。"
)
PRELAUNCH_STOP = (
    "任一 mandatory preflight、complete-tree、observable requested configuration、receipt "
    "acceptance 或 judge package-fit gate false/unknown 时，在任何 generation request 前停止；"
    "operational_state = blocked_before_generation，outcome = bounded_incomplete。"
)
NO_SAMPLE_SIZE_DOWNGRADE = (
    "必须获得四个预注册 pair 的一次且仅一次 request receipt；平台若不能支持八个隔离生成请求"
    "和两份完整 reviewer package，则启动前 blocked_before_generation 并最终 "
    "bounded_incomplete，不得改成一个 pair、删 pair、补 pair 或 best-of-n。"
)
NO_RETRY_RULE = (
    "不对生成或评审做 retry、continue、补 prompt、修复 JSON、替换模型、替换 pair、拆 reviewer "
    "package 或 best-of-n 选择；SDK 与 transport 自动 retry 必须在 preflight 中证明为零。"
)
ATTEMPT_ACCEPTANCE_RULE = (
    "client_automatic_retry_limit = 0、fallback_enabled = false、attempt_count = 1、"
    "retry_count = 0，且 event log 只含一个 network submission。attempt 是否被 provider 接受"
    "不改变 service-error disposition。"
)
EXPECTED_OUTCOME_FUNCTION = [
    "若任一 bounded_incomplete_when 条件为 true，则 outcome = bounded_incomplete",
    "否则若全部 machine_readable_adopt_predicates 为 true，则 outcome = adopt",
    "否则 outcome = reject",
]
NATIVE_SUBAGENT_SURFACE = "本项目父 Codex task/thread 的 native subagent"
NATIVE_SUBAGENT_FORBIDDEN_ACTION = "使用本项目父 task/thread 的 native subagent、fork 或继承上下文作为任何 generation arm"

R9_OUTPUT_SCHEMA_IDS = frozenset({*EXPECTED_SCHEMA_IDS.values(), "R9-ANSWER-V1"})
R9_PATH_MARKER = re.compile(r"(?:^|[/_.-])r9(?:[/_.-]|$)", re.IGNORECASE)
ALLOWED_R9_RESEARCH_FILES = {
    PREREGISTRATION_RELATIVE.relative_to("research").as_posix(),
    "COMPONENT_AUTHORITY_BOUNDARY_PREREGISTRATION_R9B_2026-07-25.json",
}
TEXT_LIKE_SUFFIXES = {
    ".json",
    ".jsonl",
    ".md",
    ".raw",
    ".txt",
    ".yaml",
    ".yml",
}
MISSING = object()


class StrictJsonError(ValueError):
    """Raised when a preregistration is not duplicate-free strict JSON."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJsonError(f"duplicate object key: {key}")
        result[key] = value
    return result


def reject_nonfinite_constant(value: str) -> NoReturn:
    raise StrictJsonError(f"non-finite JSON number: {value}")


def reject_float(value: str) -> NoReturn:
    raise StrictJsonError(f"floating JSON number is forbidden: {value}")


def parse_integer(value: str) -> int:
    if value == "-0":
        raise StrictJsonError("negative zero is forbidden")
    return int(value)


def reject_surrogates(value: Any, path: str = "$") -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise StrictJsonError(f"unpaired Unicode surrogate at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            reject_surrogates(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            reject_surrogates(key, f"{path}.<key>")
            reject_surrogates(item, f"{path}.{key}")


def load_preregistration(
    path: Path, errors: list[str]
) -> tuple[dict[str, Any] | None, bytes]:
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        errors.append(
            f"missing R9 preregistration: {PREREGISTRATION_RELATIVE.as_posix()}"
        )
        return None, b""
    except OSError as exc:
        errors.append(f"cannot read R9 preregistration: {exc}")
        return None, b""
    try:
        text = raw.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite_constant,
            parse_float=reject_float,
            parse_int=parse_integer,
        )
        reject_surrogates(value)
    except (UnicodeDecodeError, json.JSONDecodeError, StrictJsonError) as exc:
        errors.append(f"invalid strict JSON in R9 preregistration: {exc}")
        return None, raw
    if not isinstance(value, dict):
        errors.append("R9 preregistration top level must be an object")
        return None, raw
    return value, raw


def strict_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            strict_equal(left, right) for left, right in zip(actual, expected)
        )
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            strict_equal(actual[key], expected[key]) for key in expected
        )
    return bool(actual == expected)


def get_path(document: dict[str, Any], dotted: str) -> Any:
    current: Any = document
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current


def expect_equal(
    document: dict[str, Any], dotted: str, expected: Any, errors: list[str]
) -> None:
    actual = get_path(document, dotted)
    if actual is MISSING:
        errors.append(f"missing required R9 field: {dotted}")
    elif not strict_equal(actual, expected):
        errors.append(
            f"R9 field differs: {dotted}; expected={expected!r}, observed={actual!r}"
        )


def require_exact_keys(
    value: Any, expected: set[str], label: str, errors: list[str]
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    actual = set(value)
    if actual != expected:
        errors.append(
            f"{label} fields differ: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def walk_values(value: Any, path: str = "$") -> list[tuple[str, str | None, Any]]:
    observations: list[tuple[str, str | None, Any]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            observations.append((child, key, item))
            observations.extend(walk_values(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            observations.extend(walk_values(item, f"{path}[{index}]"))
    return observations


def validate_no_self_reference(
    document: dict[str, Any], raw_digest: str, errors: list[str]
) -> None:
    forbidden_state_keys = {
        "outcome",
        "operational_state",
        "wrapper_adoption",
        "experiment_passed",
        "method_comparison_completed",
    }
    for path, key, value in walk_values(document):
        if key is not None and (
            key.casefold().endswith("raw_sha256")
            or key.casefold() in forbidden_state_keys
        ):
            if key.casefold().endswith("raw_sha256"):
                errors.append(
                    "self-referential preregistration raw sha256 field is forbidden: "
                    f"{path}"
                )
            else:
                errors.append(
                    "R9 preregistration must not contain an executed-result state "
                    f"field: {path}"
                )
        if isinstance(value, str) and value == raw_digest:
            errors.append(
                f"R9 preregistration embeds its own current raw sha256 at {path}"
            )


def validate_core_contract(document: dict[str, Any], errors: list[str]) -> None:
    require_exact_keys(document, EXPECTED_TOP_LEVEL_KEYS, "R9 preregistration", errors)
    expect_equal(document, "schema_version", 2, errors)
    expect_equal(document, "round_id", "SAME-TASK-METHOD-COMPARISON-R9", errors)
    expect_equal(document, "status", "preregistered_not_executed", errors)
    expect_equal(document, "contains_execution_results", False, errors)

    readiness = get_path(document, "prelaunch_readiness")
    require_exact_keys(readiness, EXPECTED_READINESS_KEYS, "R9 readiness", errors)
    expect_equal(
        document,
        "prelaunch_readiness.state",
        "not_evaluated_blocked_until_required_receipts_exist",
        errors,
    )
    for field in (
        "runtime_binding_present",
        "allocation_present",
        "capability_preflight_receipt_present",
        "judge_package_fit_receipts_present",
        "generation_authorized",
    ):
        expect_equal(document, f"prelaunch_readiness.{field}", False, errors)
    expect_equal(
        document, "prelaunch_readiness.current_blocker", READINESS_BLOCKER, errors
    )
    expect_equal(
        document, "prelaunch_readiness.resolution_rule", READINESS_RESOLUTION, errors
    )

    expect_equal(
        document,
        "preregistration_freeze.failed_preflight_rule",
        FAILED_PREFLIGHT_RULE,
        errors,
    )
    expect_equal(
        document,
        "prelaunch_capability_preflight.failure_disposition",
        CAPABILITY_FAILURE_DISPOSITION,
        errors,
    )
    expect_equal(
        document,
        "judge_package_fit_preflight.failure_disposition",
        JUDGE_FIT_FAILURE_DISPOSITION,
        errors,
    )
    expect_equal(
        document,
        "stopping_and_failure_protocol.prelaunch_stop",
        PRELAUNCH_STOP,
        errors,
    )
    expect_equal(
        document,
        "additional_wrapper_admission_rule.outcome_function",
        EXPECTED_OUTCOME_FUNCTION,
        errors,
    )


def validate_design_and_no_downgrade(
    document: dict[str, Any], errors: list[str]
) -> None:
    expect_equal(document, "primary_design.paired_replicate_count", 4, errors)
    expect_equal(document, "primary_design.replicates_per_arm", 4, errors)
    expect_equal(
        document, "primary_design.planned_generation_artifact_count", 8, errors
    )
    expect_equal(document, "primary_design.pair_ids", EXPECTED_PAIR_IDS, errors)
    expect_equal(document, "primary_design.arms", EXPECTED_ARMS, errors)
    expect_equal(
        document,
        "primary_design.no_sample_size_downgrade",
        NO_SAMPLE_SIZE_DOWNGRADE,
        errors,
    )
    expect_equal(
        document,
        "stopping_and_failure_protocol.no_retry_rule",
        NO_RETRY_RULE,
        errors,
    )

    zero_budget_fields = (
        "resource_budget.generation_per_request.maximum_tool_calls",
        "resource_budget.generation_per_request.maximum_network_calls",
        "resource_budget.generation_per_request.maximum_retries",
        "resource_budget.generation_per_request.maximum_manual_interventions_after_launch",
        "resource_budget.judge_per_context.maximum_tool_calls",
        "resource_budget.judge_per_context.maximum_network_calls",
        "resource_budget.judge_per_context.maximum_retries",
    )
    for dotted in zero_budget_fields:
        expect_equal(document, dotted, 0, errors)
    expect_equal(
        document, "resource_budget.judge_per_context.judge_context_count", 2, errors
    )
    expect_equal(
        document,
        "resource_budget.judge_per_context.artifact_count_per_judge",
        8,
        errors,
    )
    expect_equal(
        document, "resource_budget.maximum_experiment_accounted_tokens", 320000, errors
    )

    expect_equal(
        document,
        "prelaunch_capability_preflight.required_generator_harness",
        "external_independent_stateless_one_shot_process_per_request",
        errors,
    )
    prohibited_surfaces = get_path(
        document, "prelaunch_capability_preflight.prohibited_generation_surfaces"
    )
    if not isinstance(prohibited_surfaces, list):
        errors.append("native subagent prohibition list is missing")
    elif NATIVE_SUBAGENT_SURFACE not in prohibited_surfaces:
        errors.append("parent-task native subagent is no longer explicitly unqualified")
    forbidden_actions = get_path(document, "forbidden_actions_during_r9")
    if not isinstance(forbidden_actions, list):
        errors.append("R9 forbidden action list is missing")
    elif NATIVE_SUBAGENT_FORBIDDEN_ACTION not in forbidden_actions:
        errors.append("parent-task native subagent prohibition differs")


def validate_required_contracts(document: dict[str, Any], errors: list[str]) -> None:
    for dotted, expected in EXPECTED_SCHEMA_IDS.items():
        expect_equal(document, dotted, expected, errors)

    expect_equal(
        document,
        "prelaunch_capability_preflight.receipt_required_fields",
        EXPECTED_CAPABILITY_RECEIPT_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "judge_package_fit_preflight.required_fields",
        EXPECTED_JUDGE_FIT_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.tree_manifest_payload_schema.required_fields",
        EXPECTED_TREE_MANIFEST_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.tree_manifest_payload_schema.entry_required_fields",
        EXPECTED_TREE_ENTRY_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "hash_and_locator_protocol.generic_digest_sidecar_schema.required_fields",
        EXPECTED_SIDECAR_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.automatic_capture_only",
        True,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.manual_or_model_self_report_is_unacceptable",
        True,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.usage_receipt.required_fields",
        EXPECTED_USAGE_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.timing_receipt.required_fields",
        EXPECTED_TIMING_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.retry_and_attempt_receipt.required_fields",
        EXPECTED_ATTEMPT_FIELDS,
        errors,
    )
    expect_equal(
        document,
        "receipt_acceptance_contract.retry_and_attempt_receipt.acceptance_rule",
        ATTEMPT_ACCEPTANCE_RULE,
        errors,
    )


def expected_generator_paths() -> list[str]:
    return [
        "common/system_message.txt",
        "common/common_task.canonical.json",
        "common/common_output_contract.canonical.json",
        "method/wrapper.canonical.json",
        "corpus/neutral_index.canonical.json",
        *(f"corpus/slices/{slice_id}.txt" for slice_id in EXPECTED_SLICE_IDS),
    ]


def expected_reviewer_common_paths() -> list[str]:
    return [
        "common/common_task.canonical.json",
        "common/common_output_contract.canonical.json",
        "corpus/neutral_index.canonical.json",
        *(f"corpus/slices/{slice_id}.txt" for slice_id in EXPECTED_SLICE_IDS),
        "review/evaluation_rubric.canonical.json",
        "review/reference_anchors.canonical.json",
        "review/system_message.txt",
        "review/scoring_instructions.txt",
    ]


def validate_package_counts(document: dict[str, Any], errors: list[str]) -> None:
    expect_equal(
        document,
        "frozen_corpus.replicate_package_rule.generator_package_instance_count",
        8,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.generator_visible_package.package_instance_count",
        8,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.generator_visible_package.exact_regular_file_paths",
        expected_generator_paths(),
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.generator_visible_package.exact_regular_file_count",
        16,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.reviewer_package_tree.reviewer_package_count",
        2,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.reviewer_package_tree.common_regular_file_paths",
        expected_reviewer_common_paths(),
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.reviewer_package_tree.common_regular_file_count",
        18,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.reviewer_package_tree.artifact_regular_file_count",
        16,
        errors,
    )
    expect_equal(
        document,
        "package_and_tree_manifest.reviewer_package_tree.total_regular_file_count",
        34,
        errors,
    )


def validate_component_hashes(
    document: dict[str, Any], errors: list[str]
) -> dict[str, str]:
    values: dict[str, Any] = {}
    for name in (
        "common_task",
        "common_output_contract",
        "frozen_corpus",
        "package_and_tree_manifest",
        "execution_binding_contract",
        "resource_budget",
        "prelaunch_capability_preflight",
        "receipt_acceptance_contract",
        "judge_package_fit_preflight",
        "evaluation_rubric",
        "reference_anchors_for_judges",
    ):
        value = get_path(document, name)
        if value is MISSING:
            errors.append(f"missing component for canonical hash: {name}")
        else:
            values[name] = value

    for arm in EXPECTED_ARMS:
        instructions = get_path(document, f"method_wrappers.{arm}.instructions")
        if not isinstance(instructions, str):
            errors.append(f"missing model-visible wrapper instructions: {arm}")
        else:
            values[f"wrapper.{arm}.model_visible"] = {"instructions": instructions}

    observed: dict[str, str] = {}
    for name, value in values.items():
        digest = sha256_bytes(canonical_json_bytes(value))
        observed[name] = digest
        expected = EXPECTED_COMPONENT_HASHES[name]
        if digest != expected:
            errors.append(
                f"canonical component sha256 mismatch: {name}; "
                f"expected={expected}, observed={digest}"
            )
    return observed


def safe_source_path(root: Path, relative: Any, errors: list[str]) -> Path | None:
    if not isinstance(relative, str):
        errors.append(f"frozen corpus source path is not a string: {relative!r}")
        return None
    pure = PurePosixPath(relative)
    required_prefix = ("research", "evidence", "r8", "RS-03", "extracted")
    if (
        not relative
        or "\\" in relative
        or pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.parts[: len(required_prefix)] != required_prefix
        or pure.suffix != ".txt"
    ):
        errors.append(f"unsafe frozen corpus source path: {relative!r}")
        return None
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"frozen corpus source path uses symlink: {relative}")
            return None
    try:
        resolved = current.resolve(strict=True)
    except FileNotFoundError:
        errors.append(f"missing frozen corpus source: {relative}")
        return None
    try:
        resolved.relative_to(root)
    except ValueError:
        errors.append(f"frozen corpus source escapes project root: {relative}")
        return None
    if not resolved.is_file():
        errors.append(f"frozen corpus source is not a regular file: {relative}")
        return None
    return resolved


def lf_lines(raw: bytes) -> list[bytes]:
    parts = raw.split(b"\n")
    lines = [part + b"\n" for part in parts[:-1]]
    if parts[-1]:
        lines.append(parts[-1])
    return lines


def validate_corpus(
    root: Path, document: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    sources = get_path(document, "frozen_corpus.sources")
    if not isinstance(sources, list):
        errors.append("frozen corpus sources must be an array")
        return {
            "source_count": 0,
            "slice_count": 0,
            "total_exposed_slice_bytes": 0,
            "manifest_root_sha256": None,
        }

    source_ids: list[Any] = []
    slice_ids: list[Any] = []
    actual_slice_hashes: dict[str, str] = {}
    actual_total = 0
    for source_index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"frozen corpus source[{source_index}] must be an object")
            continue
        source_ids.append(source.get("source_id"))
        path = safe_source_path(root, source.get("source_document_path"), errors)
        if path is None:
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"cannot read frozen corpus source {path}: {exc}")
            continue
        relative = source.get("source_document_path")
        if b"\r" in raw:
            errors.append(f"frozen corpus source is not LF-only: {relative}")
        actual_source_hash = sha256_bytes(raw)
        declared_source_hash = source.get("source_document_sha256")
        if not is_sha256(declared_source_hash):
            errors.append(f"invalid source_document_sha256: {relative}")
        elif declared_source_hash != actual_source_hash:
            errors.append(
                f"source document sha256 mismatch: {relative}; "
                f"expected={declared_source_hash}, observed={actual_source_hash}"
            )
        lines = lf_lines(raw)
        slices = source.get("slices")
        if not isinstance(slices, list):
            errors.append(f"frozen corpus slices missing for source: {relative}")
            continue
        for slice_index, slice_entry in enumerate(slices):
            if not isinstance(slice_entry, dict):
                errors.append(
                    f"frozen corpus slice[{source_index}][{slice_index}] must be an object"
                )
                continue
            slice_id = slice_entry.get("slice_id")
            slice_ids.append(slice_id)
            start = slice_entry.get("start_line")
            end = slice_entry.get("end_line")
            if (
                not isinstance(slice_id, str)
                or type(start) is not int
                or type(end) is not int
                or start < 1
                or end < start
                or end > len(lines)
            ):
                errors.append(
                    f"invalid line range for frozen corpus slice: {slice_id!r}"
                )
                continue
            exposed = b"".join(lines[start - 1 : end])
            byte_count = len(exposed)
            digest = sha256_bytes(exposed)
            actual_total += byte_count
            if slice_id in actual_slice_hashes:
                errors.append(f"duplicate frozen corpus slice_id: {slice_id}")
            else:
                actual_slice_hashes[slice_id] = digest
            if slice_entry.get("byte_count") != byte_count:
                errors.append(
                    f"slice byte count mismatch: {slice_id}; "
                    f"expected={slice_entry.get('byte_count')!r}, observed={byte_count}"
                )
            declared_digest = slice_entry.get("slice_sha256")
            if not is_sha256(declared_digest):
                errors.append(f"invalid slice_sha256: {slice_id}")
            elif declared_digest != digest:
                errors.append(
                    f"slice sha256 mismatch: {slice_id}; "
                    f"expected={declared_digest}, observed={digest}"
                )

    if source_ids != EXPECTED_SOURCE_IDS:
        errors.append(
            f"frozen corpus source identities/order differ: observed={source_ids!r}"
        )
    if slice_ids != EXPECTED_SLICE_IDS:
        errors.append(
            f"frozen corpus slice identities/order differ: observed={slice_ids!r}"
        )
    if len(set(str(item) for item in slice_ids)) != len(slice_ids):
        errors.append("frozen corpus slice identities are not unique")

    declared_total = get_path(document, "frozen_corpus.total_exposed_slice_bytes")
    if declared_total != EXPECTED_TOTAL_SLICE_BYTES:
        errors.append(
            "declared frozen corpus total byte count differs: "
            f"expected={EXPECTED_TOTAL_SLICE_BYTES}, observed={declared_total!r}"
        )
    if actual_total != EXPECTED_TOTAL_SLICE_BYTES:
        errors.append(
            "recomputed frozen corpus total byte count differs: "
            f"expected={EXPECTED_TOTAL_SLICE_BYTES}, observed={actual_total}"
        )

    preimage = bytearray(b"r9-corpus-manifest-v1\n")
    for slice_id in sorted(actual_slice_hashes, key=lambda item: item.encode("ascii")):
        preimage.extend(
            f"{slice_id}\t{actual_slice_hashes[slice_id]}\n".encode("ascii")
        )
    manifest_root = sha256_bytes(bytes(preimage))
    declared_root = get_path(document, "frozen_corpus.manifest_root_sha256")
    if declared_root != EXPECTED_CORPUS_ROOT:
        errors.append(
            "declared frozen corpus manifest root differs: "
            f"expected={EXPECTED_CORPUS_ROOT}, observed={declared_root!r}"
        )
    if manifest_root != EXPECTED_CORPUS_ROOT:
        errors.append(
            "recomputed frozen corpus manifest root differs: "
            f"expected={EXPECTED_CORPUS_ROOT}, observed={manifest_root}"
        )
    return {
        "source_count": len(source_ids),
        "slice_count": len(slice_ids),
        "total_exposed_slice_bytes": actual_total,
        "manifest_root_sha256": manifest_root,
    }


def scan_for_r9_execution_material(root: Path, errors: list[str]) -> dict[str, Any]:
    research_root = root / "research"
    suspicious: dict[str, set[str]] = {}
    if research_root.is_symlink():
        errors.append("research directory must not be a symlink")
        return {"files_scanned": 0, "unexpected_material": []}
    if not research_root.is_dir():
        errors.append("missing research directory")
        return {"files_scanned": 0, "unexpected_material": []}

    files_scanned = 0
    for path in sorted(research_root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(research_root).as_posix()
        if path.is_symlink():
            if (
                R9_PATH_MARKER.search(relative)
                and relative not in ALLOWED_R9_RESEARCH_FILES
            ):
                suspicious.setdefault(relative, set()).add("R9-specific symlink path")
            continue
        if not path.is_file():
            continue
        files_scanned += 1
        if (
            R9_PATH_MARKER.search(relative)
            and relative not in ALLOWED_R9_RESEARCH_FILES
        ):
            suspicious.setdefault(relative, set()).add("unexpected R9-specific path")
        if relative == PREREGISTRATION_RELATIVE.relative_to("research").as_posix():
            continue
        if path.suffix.casefold() not in TEXT_LIKE_SUFFIXES:
            continue
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"cannot scan research file {relative}: {exc}")
            continue
        for schema_id in R9_OUTPUT_SCHEMA_IDS:
            if schema_id.encode("ascii") in raw:
                suspicious.setdefault(relative, set()).add(
                    f"contains R9 execution schema {schema_id}"
                )

    for relative in sorted(suspicious):
        errors.append(
            "unexpected R9 generation/review/result/receipt/sidecar material "
            f"under research: {relative} ({'; '.join(sorted(suspicious[relative]))})"
        )
    return {
        "files_scanned": files_scanned,
        "unexpected_material": [
            {"path": relative, "reasons": sorted(suspicious[relative])}
            for relative in sorted(suspicious)
        ],
    }


def verify(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    preregistration_path = root / PREREGISTRATION_RELATIVE
    if preregistration_path.is_symlink():
        errors.append("R9 preregistration must not be a symlink")
        document: dict[str, Any] | None = None
        raw = b""
    else:
        document, raw = load_preregistration(preregistration_path, errors)
    raw_digest = sha256_bytes(raw) if raw else None

    component_hashes: dict[str, str] = {}
    corpus = {
        "source_count": 0,
        "slice_count": 0,
        "total_exposed_slice_bytes": 0,
        "manifest_root_sha256": None,
    }
    declared_generation_authorized: Any = None
    declared_status: Any = None
    declared_contains_results: Any = None
    if document is not None:
        declared_generation_authorized = get_path(
            document, "prelaunch_readiness.generation_authorized"
        )
        declared_status = document.get("status")
        declared_contains_results = document.get("contains_execution_results")
        validate_no_self_reference(document, raw_digest or "", errors)
        validate_core_contract(document, errors)
        validate_design_and_no_downgrade(document, errors)
        validate_required_contracts(document, errors)
        validate_package_counts(document, errors)
        component_hashes = validate_component_hashes(document, errors)
        corpus = validate_corpus(root, document, errors)

    output_scan = scan_for_r9_execution_material(root, errors)
    control_effective = not errors
    return {
        "schema_version": 1,
        "control_id": CONTROL_ID,
        "status": "pass" if control_effective else "fail",
        "status_semantics": "prelaunch_control_verification_only",
        "control_effective": control_effective,
        "experiment_state": "blocked_before_generation",
        "required_outcome_if_recorded": "bounded_incomplete",
        "wrapper_adoption": "not_adopted",
        "generation_authorized": False,
        "method_comparison_completed": False,
        "experiment_passed": False,
        "preregistration": {
            "path": PREREGISTRATION_RELATIVE.as_posix(),
            "observed_raw_sha256": raw_digest,
            "declared_status": declared_status,
            "declared_contains_execution_results": declared_contains_results,
            "declared_generation_authorized": declared_generation_authorized,
        },
        "readiness_evidence": {
            "required_artifacts_present": 0,
            "missing": [
                "runtime_binding",
                "sealed_allocation",
                "capability_preflight_receipt",
                "judge_package_fit_receipts",
                "required_digest_sidecars",
            ],
        },
        "planned_design": {
            "paired_replicates": 4,
            "generation_artifacts": 8,
            "generation_attempts_per_artifact": 1,
            "automatic_retries": 0,
        },
        "corpus": corpus,
        "canonical_component_sha256": component_hashes,
        "research_output_scan": output_scan,
        "claim_boundary": [
            "proves only that the frozen R9 prelaunch control is intact",
            "does not execute or complete the method comparison",
            "does not establish either wrapper's quality or superiority",
            "does not authorize generation or adopt a wrapper",
        ],
        "errors": errors,
    }


def internal_error_receipt(exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "control_id": CONTROL_ID,
        "status": "fail",
        "status_semantics": "prelaunch_control_verification_only",
        "control_effective": False,
        "experiment_state": "blocked_before_generation",
        "required_outcome_if_recorded": "bounded_incomplete",
        "wrapper_adoption": "not_adopted",
        "generation_authorized": False,
        "method_comparison_completed": False,
        "experiment_passed": False,
        "errors": [f"R9 verifier internal error: {type(exc).__name__}: {exc}"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="project root (defaults to IDS_PROJECT_ROOT or this script's parent)",
    )
    parser.add_argument("--json", action="store_true", help="emit one JSON receipt")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise NotADirectoryError(root)
        receipt = verify(root)
    except Exception as exc:  # fail closed on verifier defects and I/O races
        receipt = internal_error_receipt(exc)

    if args.json:
        print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    elif receipt["status"] == "pass":
        print("R9 prelaunch control verification: PASS")
        print(
            "experiment remains blocked_before_generation; "
            "required disposition is bounded_incomplete; wrapper not adopted"
        )
    else:
        print("R9 prelaunch control verification: FAIL (generation remains blocked)")
        for error in receipt["errors"]:
            print(f"- {error}")
    return 0 if receipt["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
