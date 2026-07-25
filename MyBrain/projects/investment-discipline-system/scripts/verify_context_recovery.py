#!/usr/bin/env python3
"""Verify the frozen, deterministic CTX-02 context-recovery mechanism."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("IDS_PROJECT_ROOT", Path(__file__).resolve().parents[1])
).resolve()
DEFAULT_SPEC_PATH = (
    PROJECT_ROOT / "governance" / "CONTEXT_RECOVERY_SPEC_V1.json"
)

MECHANISM_ID = "CTX-02-CONTEXT-RECOVERY-DESIGN-FREEZE-V1"
FAILURE_ID = "CTX-02"
FIXTURE_ID = "CTX02-FIXTURE-001"
EXPECTED_FIXTURE_SHA256 = (
    "22f7eadd618ceb154d2ed5b99dec1c0e785c1f672c5de3fb6db2a6dfaba50cc2"
)
CURRENT_REQUEST_ID = "REQ-CTX02-CURRENT"
CURRENT_TARGET_ID = "TARGET-CTX02-DESIGN-FREEZE"
STALE_REQUEST_ID = "REQ-CTX02-STALE-LABEL-CHECK"
STALE_TARGET_ID = "TARGET-CTX02-LABEL-CHECK-ONLY"
SENTINEL_ID = "CTX02-CURRENT-TARGET-V1"

REQUIRED_PROBE_IDS = [
    "start",
    "middle",
    "end",
    "post_compaction",
    "empty_context_restart",
    "stale_request_regression",
]

STATE_FILE_MARKERS = {
    "PROJECT_CHARTER.md": [
        "# 项目章程｜投研纪律系统",
        "## 项目目标",
        "## 当前范围",
        "## 当前非目标",
        "## 成功标准",
    ],
    "STATUS.md": [
        "# 当前状态｜投研纪律系统",
        "## 当前裁决",
        "## 已有且仍然有效",
        "## 进行中",
        "## 当前下一步",
        "## 主要残余风险",
    ],
    "TASK_BOARD.md": [
        "# 工作板｜投研纪律系统",
        "## 进行中",
        "## 已排队",
        "## 条件性任务",
        "## 已完成且证据仍有效",
        "## 工作规则",
    ],
    "DECISIONS.md": [
        "# 决定日志｜投研纪律系统",
        "## 已确认的工作决定",
        "### 当前只服务个人",
        "### AI 负责分析与建议，人保留最终决策",
        "### Obsidian 作为长期项目记忆",
        "## 待确认决定",
    ],
    "AI_COLLABORATION_METHOD.md": [
        "# AI 协作开发方法",
        "## 基本原则",
        "## 有边界的自主循环",
        "## 工作循环",
        "### 恢复状态",
        "## 上下文管理",
        "## 完成判定",
        "## 本方法的待验证部分",
    ],
}

CLAIM_BOUNDARY = {
    "proof_scope": (
        "A deterministic standard-library oracle reads the required state-packet "
        "file bytes, checks frozen ordered section markers, replays six bounded "
        "recovery probes, and compares the derived observations with an explicit "
        "frozen receipt."
    ),
    "does_not_prove": [
        "real LLM recall",
        "unknown-position statistical coverage",
        "production incident rate",
        "model- or harness-independent behavior",
    ],
    "residual_limitation": (
        "This design freeze proves only the specified byte checks and deterministic "
        "fixture behavior. Retrieval by a real model, arbitrary context lengths "
        "and positions, compaction implementations, and future harness revisions "
        "require separately pinned empirical runs."
    ),
}

EXPECTED_SENTINEL = {
    "sentinel_id": SENTINEL_ID,
    "request_id": CURRENT_REQUEST_ID,
    "target_id": CURRENT_TARGET_ID,
    "request_revision": 2,
    "supersedes": STALE_REQUEST_ID,
    "instruction": "verify context recovery from bytes and deterministic probes",
}

EXPECTED_CURRENT_REQUEST = {
    "request_id": CURRENT_REQUEST_ID,
    "target_id": CURRENT_TARGET_ID,
    "request_revision": 2,
    "state": "current",
    "supersedes": STALE_REQUEST_ID,
}

EXPECTED_STALE_REQUEST = {
    "request_id": STALE_REQUEST_ID,
    "target_id": STALE_TARGET_ID,
    "request_revision": 1,
    "state": "superseded",
    "superseded_by": CURRENT_REQUEST_ID,
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object repeats a key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def add_error(
    errors: list[dict[str, str]],
    oracle_id: str,
    message: str,
    probe_id: str | None = None,
) -> None:
    error = {"oracle_id": oracle_id, "message": message}
    if probe_id is not None:
        error["probe_id"] = probe_id
    errors.append(error)


def read_strict_json(
    path: Path, errors: list[dict[str, str]]
) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        add_error(
            errors,
            "CTX02-SPEC-READ",
            f"specification is unreadable: {exc}",
        )
        return {}, b""
    try:
        text = raw.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        add_error(
            errors,
            "CTX02-SPEC-STRICT-JSON",
            f"specification is not strict JSON: {exc}",
        )
        return {}, raw
    if not isinstance(value, dict):
        add_error(
            errors,
            "CTX02-SPEC-SCHEMA",
            "specification top-level value must be an object",
        )
        return {}, raw
    return value, raw


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def expected_state_contract() -> dict[str, Any]:
    return {
        "encoding": "utf-8",
        "nonempty_rule": "at_least_one_non_whitespace_byte",
        "marker_rule": "each_literal_utf8_marker_occurs_once_in_declared_order",
        "required_files": [
            {"path": path, "ordered_markers": markers}
            for path, markers in STATE_FILE_MARKERS.items()
        ],
    }


def expected_probe_contract() -> dict[str, Any]:
    return {
        "fixture_id": FIXTURE_ID,
        "required_probe_ids": REQUIRED_PROBE_IDS,
        "sentinel_id": SENTINEL_ID,
        "current_request_id": CURRENT_REQUEST_ID,
        "current_target_id": CURRENT_TARGET_ID,
        "stale_request_id": STALE_REQUEST_ID,
        "stale_target_id": STALE_TARGET_ID,
        "selection_rule": (
            "select_the_unique_current_request_whose_supersession_links_reject_"
            "the_stale_request"
        ),
    }


def verify_spec_contract(
    spec: dict[str, Any], errors: list[dict[str, str]]
) -> None:
    expected_keys = {
        "schema_version",
        "mechanism_id",
        "failure_id",
        "claim_boundary",
        "state_packet_contract",
        "probe_contract",
        "probe_fixture",
        "expected_probe_receipt",
    }
    if set(spec) != expected_keys:
        add_error(
            errors,
            "CTX02-SPEC-SCHEMA",
            "specification top-level keys differ from the frozen schema",
        )
    if spec.get("schema_version") != 1:
        add_error(
            errors,
            "CTX02-SPEC-SCHEMA",
            "schema_version must be 1",
        )
    if spec.get("mechanism_id") != MECHANISM_ID:
        add_error(
            errors,
            "CTX02-SPEC-IDENTITY",
            "mechanism_id differs",
        )
    if spec.get("failure_id") != FAILURE_ID:
        add_error(
            errors,
            "CTX02-SPEC-IDENTITY",
            "failure_id differs",
        )
    if spec.get("claim_boundary") != CLAIM_BOUNDARY:
        add_error(
            errors,
            "CTX02-CLAIM-BOUNDARY",
            "proof scope or residual limitation differs",
        )
    if spec.get("state_packet_contract") != expected_state_contract():
        add_error(
            errors,
            "CTX02-STATE-CONTRACT",
            "state-packet byte and marker contract differs",
        )
    if spec.get("probe_contract") != expected_probe_contract():
        add_error(
            errors,
            "CTX02-PROBE-CONTRACT",
            "probe contract differs",
        )


def verify_state_packet(
    project_root: Path, errors: list[dict[str, str]]
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for relative, markers in STATE_FILE_MARKERS.items():
        path = project_root / relative
        try:
            raw = path.read_bytes()
        except OSError as exc:
            add_error(
                errors,
                "CTX02-STATE-MISSING",
                f"{relative} is missing or unreadable: {exc}",
            )
            observations.append(
                {
                    "path": relative,
                    "byte_count": 0,
                    "sha256": None,
                    "marker_offsets": [],
                }
            )
            continue

        observation: dict[str, Any] = {
            "path": relative,
            "byte_count": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "marker_offsets": [],
        }
        observations.append(observation)

        if not raw.strip():
            add_error(
                errors,
                "CTX02-STATE-NONEMPTY",
                f"{relative} contains no non-whitespace bytes",
            )
            continue
        try:
            raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            add_error(
                errors,
                "CTX02-STATE-UTF8",
                f"{relative} is not valid UTF-8: {exc}",
            )
            continue

        offsets: list[int] = []
        marker_problem = False
        for marker in markers:
            marker_bytes = marker.encode("utf-8")
            count = raw.count(marker_bytes)
            if count == 0:
                add_error(
                    errors,
                    "CTX02-STATE-MARKER-MISSING",
                    f"{relative} is missing marker {marker!r}",
                )
                marker_problem = True
                continue
            if count != 1:
                add_error(
                    errors,
                    "CTX02-STATE-MARKER-DUPLICATE",
                    f"{relative} marker {marker!r} occurs {count} times",
                )
                marker_problem = True
                continue
            offsets.append(raw.index(marker_bytes))
        observation["marker_offsets"] = offsets
        if not marker_problem and offsets != sorted(offsets):
            add_error(
                errors,
                "CTX02-STATE-MARKER-ORDER",
                f"{relative} markers are not in the frozen section order",
            )
    return observations


def validate_fixture_identity(
    fixture: Any, errors: list[dict[str, str]]
) -> dict[str, Any]:
    if not isinstance(fixture, dict):
        add_error(
            errors,
            "CTX02-FIXTURE-SCHEMA",
            "probe_fixture must be an object",
        )
        return {}
    if set(fixture) != {
        "fixture_id",
        "current_request",
        "stale_request",
        "probes",
    }:
        add_error(
            errors,
            "CTX02-FIXTURE-SCHEMA",
            "probe_fixture keys differ",
        )
    if fixture.get("fixture_id") != FIXTURE_ID:
        add_error(
            errors,
            "CTX02-FIXTURE-IDENTITY",
            "fixture_id differs",
        )

    current = fixture.get("current_request")
    if isinstance(current, dict) and current.get("target_id") == STALE_TARGET_ID:
        add_error(
            errors,
            "CTX02-CURRENT-TARGET-STALE",
            "the declared current request points at the superseded target",
        )
    if current != EXPECTED_CURRENT_REQUEST:
        add_error(
            errors,
            "CTX02-CURRENT-REQUEST-CONTRACT",
            "current request differs from the frozen current request",
        )
    if fixture.get("stale_request") != EXPECTED_STALE_REQUEST:
        add_error(
            errors,
            "CTX02-STALE-REQUEST-CONTRACT",
            "stale request differs from the frozen superseded request",
        )

    probes = fixture.get("probes")
    if not isinstance(probes, list):
        add_error(
            errors,
            "CTX02-PROBE-SET",
            "fixture probes must be a list",
        )
        return fixture
    probe_ids = [
        probe.get("probe_id") if isinstance(probe, dict) else None
        for probe in probes
    ]
    if probe_ids != REQUIRED_PROBE_IDS or len(probe_ids) != len(set(probe_ids)):
        add_error(
            errors,
            "CTX02-PROBE-SET",
            "fixture must contain each required probe once in frozen order",
        )
    return fixture


def position_observation(
    probe: dict[str, Any],
    probe_id: str,
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    segments = probe.get("context_segments")
    if probe.get("probe_type") != "position" or not isinstance(segments, list):
        add_error(
            errors,
            f"CTX02-PROBE-{probe_id.upper()}-SCHEMA",
            "position probe schema differs",
            probe_id,
        )
        return None
    sentinels = [
        (index, segment)
        for index, segment in enumerate(segments)
        if isinstance(segment, dict) and segment.get("kind") == "sentinel"
    ]
    if not sentinels:
        add_error(
            errors,
            f"CTX02-PROBE-{probe_id.upper()}-SENTINEL-MISSING",
            "position probe has no sentinel segment",
            probe_id,
        )
        return None
    if len(sentinels) != 1:
        add_error(
            errors,
            f"CTX02-PROBE-{probe_id.upper()}-SENTINEL-COUNT",
            "position probe must have exactly one sentinel segment",
            probe_id,
        )
        return None

    index, segment = sentinels[0]
    if probe_id == "start":
        correct_position = index == 0
    elif probe_id == "middle":
        correct_position = len(segments) >= 5 and index * 2 == len(segments) - 1
    else:
        correct_position = bool(segments) and index == len(segments) - 1
    if not correct_position:
        add_error(
            errors,
            f"CTX02-PROBE-{probe_id.upper()}-SENTINEL-POSITION",
            f"sentinel is not at the required {probe_id} position",
            probe_id,
        )

    payload = segment.get("payload")
    if payload != EXPECTED_SENTINEL:
        oracle_id = f"CTX02-PROBE-{probe_id.upper()}-SENTINEL-CONTRADICTED"
        add_error(
            errors,
            oracle_id,
            "sentinel payload contradicts the frozen current request",
            probe_id,
        )
    if not isinstance(payload, dict):
        return None
    return {
        "probe_id": probe_id,
        "recovery_source": "context_segments",
        "sentinel_index": index,
        "segment_count": len(segments),
        "recovered_request_id": payload.get("request_id"),
        "recovered_target_id": payload.get("target_id"),
    }


def post_compaction_observation(
    probe: dict[str, Any], errors: list[dict[str, str]]
) -> dict[str, Any] | None:
    probe_id = "post_compaction"
    segments = probe.get("context_segments")
    if probe.get("probe_type") != probe_id or not isinstance(segments, list):
        add_error(
            errors,
            "CTX02-PROBE-COMPACTION-SCHEMA",
            "post-compaction probe schema differs",
            probe_id,
        )
        return None
    receipts = [
        segment
        for segment in segments
        if isinstance(segment, dict)
        and segment.get("kind") == "compaction_receipt"
    ]
    if len(receipts) != 1:
        add_error(
            errors,
            "CTX02-PROBE-COMPACTION-RECOVERY-MISSING",
            "post-compaction input must contain one recovery receipt",
            probe_id,
        )
        return None
    receipt = receipts[0]
    sentinel = receipt.get("recovered_sentinel")
    if sentinel != EXPECTED_SENTINEL:
        add_error(
            errors,
            "CTX02-PROBE-COMPACTION-SENTINEL-CONTRADICTED",
            "post-compaction receipt does not recover the frozen sentinel",
            probe_id,
        )
    if (
        probe.get("pre_compaction_target_id") != CURRENT_TARGET_ID
        or probe.get("compacted_history_omits_stale_request_body") is not True
        or receipt.get("compaction_id") != "COMPACT-CTX02-001"
        or receipt.get("input_probe_ids") != ["start", "middle", "end"]
    ):
        add_error(
            errors,
            "CTX02-PROBE-COMPACTION-LINEAGE",
            "post-compaction lineage differs",
            probe_id,
        )
    if not isinstance(sentinel, dict):
        return None
    return {
        "probe_id": probe_id,
        "recovery_source": "compaction_receipt",
        "context_was_empty": len(segments) == 0,
        "recovered_request_id": sentinel.get("request_id"),
        "recovered_target_id": sentinel.get("target_id"),
        "stale_request_disposition": "not_in_compacted_input",
    }


def restart_observation(
    probe: dict[str, Any],
    state_observations: list[dict[str, Any]],
    errors: list[dict[str, str]],
) -> dict[str, Any] | None:
    probe_id = "empty_context_restart"
    if probe.get("probe_type") != probe_id:
        add_error(
            errors,
            "CTX02-PROBE-RESTART-SCHEMA",
            "restart probe type differs",
            probe_id,
        )
        return None
    segments = probe.get("context_segments")
    if segments != []:
        add_error(
            errors,
            "CTX02-PROBE-RESTART-NOT-EMPTY",
            "restart probe must begin with an empty context",
            probe_id,
        )
    packet = probe.get("restart_packet")
    if not isinstance(packet, dict):
        add_error(
            errors,
            "CTX02-PROBE-RESTART-RECOVERY-MISSING",
            "empty-context restart has no persistent recovery packet",
            probe_id,
        )
        return None
    expected_files = list(STATE_FILE_MARKERS)
    if (
        packet.get("startup_mode") != "empty_context"
        or packet.get("loaded_files") != expected_files
    ):
        add_error(
            errors,
            "CTX02-PROBE-RESTART-PACKET",
            "restart packet does not load the frozen required-state file set",
            probe_id,
        )
    if any(
        observation.get("byte_count", 0) == 0
        or not observation.get("marker_offsets")
        for observation in state_observations
    ):
        add_error(
            errors,
            "CTX02-PROBE-RESTART-STATE-INVALID",
            "restart recovery cannot proceed from an invalid state packet",
            probe_id,
        )
    sentinel = packet.get("recovery_sentinel")
    if sentinel != EXPECTED_SENTINEL:
        add_error(
            errors,
            "CTX02-PROBE-RESTART-SENTINEL-CONTRADICTED",
            "restart packet does not recover the frozen sentinel",
            probe_id,
        )
    if not isinstance(sentinel, dict):
        return None
    return {
        "probe_id": probe_id,
        "recovery_source": "required_state_packet",
        "context_was_empty": segments == [],
        "recovered_request_id": sentinel.get("request_id"),
        "recovered_target_id": sentinel.get("target_id"),
    }


def stale_request_observation(
    probe: dict[str, Any], errors: list[dict[str, str]]
) -> dict[str, Any] | None:
    probe_id = "stale_request_regression"
    segments = probe.get("context_segments")
    if probe.get("probe_type") != probe_id or not isinstance(segments, list):
        add_error(
            errors,
            "CTX02-PROBE-STALE-SCHEMA",
            "stale-request probe schema differs",
            probe_id,
        )
        return None
    records: dict[str, dict[str, Any]] = {}
    for segment in segments:
        if not isinstance(segment, dict) or segment.get("kind") != "request":
            continue
        payload = segment.get("payload")
        if not isinstance(payload, dict) or not isinstance(
            payload.get("request_id"), str
        ):
            add_error(
                errors,
                "CTX02-PROBE-STALE-REQUEST-SCHEMA",
                "stale-request probe contains an invalid request record",
                probe_id,
            )
            continue
        request_id = payload["request_id"]
        if request_id in records:
            add_error(
                errors,
                "CTX02-PROBE-STALE-DUPLICATE-REQUEST",
                f"request {request_id!r} occurs more than once",
                probe_id,
            )
        records[request_id] = payload

    current_candidates = [
        record
        for record in records.values()
        if record.get("state") == "current"
        and "superseded_by" not in record
    ]
    if len(current_candidates) != 1:
        add_error(
            errors,
            "CTX02-PROBE-STALE-CURRENT-SELECTION",
            "supersession graph must select exactly one current request",
            probe_id,
        )
        return None
    selected = current_candidates[0]
    stale = records.get(STALE_REQUEST_ID)
    if (
        selected.get("request_id") != CURRENT_REQUEST_ID
        or selected.get("target_id") != CURRENT_TARGET_ID
    ):
        add_error(
            errors,
            "CTX02-PROBE-STALE-TARGET-SELECTED",
            "stale-request regression selected the wrong target",
            probe_id,
        )
    if (
        stale != EXPECTED_STALE_REQUEST
        or selected != EXPECTED_CURRENT_REQUEST
        or selected.get("supersedes") != STALE_REQUEST_ID
        or not isinstance(stale, dict)
        or stale.get("superseded_by") != CURRENT_REQUEST_ID
    ):
        add_error(
            errors,
            "CTX02-PROBE-STALE-SUPERSESSION",
            "current and stale request supersession links are inconsistent",
            probe_id,
        )
    return {
        "probe_id": probe_id,
        "recovery_source": "request_supersession",
        "selected_request_id": selected.get("request_id"),
        "selected_target_id": selected.get("target_id"),
        "stale_request_disposition": (
            "rejected_superseded"
            if isinstance(stale, dict)
            and stale.get("state") == "superseded"
            and stale.get("superseded_by") == selected.get("request_id")
            else "not_rejected"
        ),
    }


def derive_probe_receipt(
    fixture: dict[str, Any],
    state_observations: list[dict[str, Any]],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    fixture_hash = hashlib.sha256(canonical_json_bytes(fixture)).hexdigest()
    if fixture_hash != EXPECTED_FIXTURE_SHA256:
        add_error(
            errors,
            "CTX02-FIXTURE-DIGEST",
            "probe fixture bytes differ from the frozen canonical fixture",
        )

    probes = fixture.get("probes")
    probe_map = (
        {
            probe["probe_id"]: probe
            for probe in probes
            if isinstance(probe, dict)
            and isinstance(probe.get("probe_id"), str)
        }
        if isinstance(probes, list)
        else {}
    )
    observations: list[dict[str, Any]] = []
    for probe_id in ("start", "middle", "end"):
        probe = probe_map.get(probe_id)
        if not isinstance(probe, dict):
            add_error(
                errors,
                f"CTX02-PROBE-{probe_id.upper()}-MISSING",
                "required position probe is missing",
                probe_id,
            )
            continue
        observation = position_observation(probe, probe_id, errors)
        if observation is not None:
            observations.append(observation)

    compaction_probe = probe_map.get("post_compaction")
    if isinstance(compaction_probe, dict):
        observation = post_compaction_observation(compaction_probe, errors)
        if observation is not None:
            observations.append(observation)
    else:
        add_error(
            errors,
            "CTX02-PROBE-COMPACTION-MISSING",
            "post-compaction probe is missing",
            "post_compaction",
        )

    restart_probe = probe_map.get("empty_context_restart")
    if isinstance(restart_probe, dict):
        observation = restart_observation(
            restart_probe, state_observations, errors
        )
        if observation is not None:
            observations.append(observation)
    else:
        add_error(
            errors,
            "CTX02-PROBE-RESTART-MISSING",
            "empty-context restart probe is missing",
            "empty_context_restart",
        )

    stale_probe = probe_map.get("stale_request_regression")
    if isinstance(stale_probe, dict):
        observation = stale_request_observation(stale_probe, errors)
        if observation is not None:
            observations.append(observation)
    else:
        add_error(
            errors,
            "CTX02-PROBE-STALE-MISSING",
            "stale-request regression probe is missing",
            "stale_request_regression",
        )

    return {
        "fixture_id": fixture.get("fixture_id"),
        "fixture_sha256": fixture_hash,
        "observations": observations,
    }


def expected_receipt() -> dict[str, Any]:
    return {
        "fixture_id": FIXTURE_ID,
        "fixture_sha256": EXPECTED_FIXTURE_SHA256,
        "observations": [
            {
                "probe_id": "start",
                "recovery_source": "context_segments",
                "sentinel_index": 0,
                "segment_count": 5,
                "recovered_request_id": CURRENT_REQUEST_ID,
                "recovered_target_id": CURRENT_TARGET_ID,
            },
            {
                "probe_id": "middle",
                "recovery_source": "context_segments",
                "sentinel_index": 2,
                "segment_count": 5,
                "recovered_request_id": CURRENT_REQUEST_ID,
                "recovered_target_id": CURRENT_TARGET_ID,
            },
            {
                "probe_id": "end",
                "recovery_source": "context_segments",
                "sentinel_index": 4,
                "segment_count": 5,
                "recovered_request_id": CURRENT_REQUEST_ID,
                "recovered_target_id": CURRENT_TARGET_ID,
            },
            {
                "probe_id": "post_compaction",
                "recovery_source": "compaction_receipt",
                "context_was_empty": False,
                "recovered_request_id": CURRENT_REQUEST_ID,
                "recovered_target_id": CURRENT_TARGET_ID,
                "stale_request_disposition": "not_in_compacted_input",
            },
            {
                "probe_id": "empty_context_restart",
                "recovery_source": "required_state_packet",
                "context_was_empty": True,
                "recovered_request_id": CURRENT_REQUEST_ID,
                "recovered_target_id": CURRENT_TARGET_ID,
            },
            {
                "probe_id": "stale_request_regression",
                "recovery_source": "request_supersession",
                "selected_request_id": CURRENT_REQUEST_ID,
                "selected_target_id": CURRENT_TARGET_ID,
                "stale_request_disposition": "rejected_superseded",
            },
        ],
    }


def verify(
    project_root: Path, spec_path: Path
) -> tuple[dict[str, Any], int]:
    errors: list[dict[str, str]] = []
    spec, spec_raw = read_strict_json(spec_path, errors)
    state_observations = verify_state_packet(project_root, errors)

    derived_receipt: dict[str, Any] = {
        "fixture_id": None,
        "fixture_sha256": None,
        "observations": [],
    }
    if spec:
        verify_spec_contract(spec, errors)
        fixture = validate_fixture_identity(spec.get("probe_fixture"), errors)
        if fixture:
            derived_receipt = derive_probe_receipt(
                fixture, state_observations, errors
            )
        frozen_receipt = spec.get("expected_probe_receipt")
        if frozen_receipt != expected_receipt():
            add_error(
                errors,
                "CTX02-RECEIPT-CONTRACT",
                "explicit expected probe receipt differs from the frozen oracle",
            )
        if derived_receipt != frozen_receipt:
            add_error(
                errors,
                "CTX02-RECEIPT-MISMATCH",
                "derived probe observations do not match the explicit receipt",
            )

    status = "pass" if not errors else "fail"
    payload = {
        "schema_version": 1,
        "mechanism_id": MECHANISM_ID,
        "failure_id": FAILURE_ID,
        "status": status,
        "derived_from": {
            "spec_path": "governance/CONTEXT_RECOVERY_SPEC_V1.json",
            "spec_byte_count": len(spec_raw),
            "spec_sha256": (
                hashlib.sha256(spec_raw).hexdigest() if spec_raw else None
            ),
            "state_packet_files": state_observations,
        },
        "probe_receipt": derived_receipt,
        "claim_boundary": CLAIM_BOUNDARY,
        "errors": errors,
    }
    return payload, 0 if status == "pass" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=PROJECT_ROOT,
        help="project root containing the required state packet",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=None,
        help="context-recovery specification path",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable receipt",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    project_root = args.root.resolve()
    spec_path = (
        args.spec.resolve()
        if args.spec is not None
        else project_root / "governance" / "CONTEXT_RECOVERY_SPEC_V1.json"
    )
    payload, exit_code = verify(project_root, spec_path)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif exit_code == 0:
        print(
            "PASS: CTX-02 state bytes and all deterministic recovery probes match"
        )
    else:
        for error in payload["errors"]:
            print(
                f"FAIL [{error['oracle_id']}]: {error['message']}",
                file=sys.stderr,
            )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
