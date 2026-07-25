#!/usr/bin/env python3
"""Reject silent weakening of a frozen acceptance contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SEVERITY = {"minor": 1, "major": 2, "critical": 3}
EXACT_NORMATIVE_FIELDS = (
    "release_target",
    "objective",
    "scope",
    "non_goals",
    "authority",
    "allowed_write_paths",
    "manual_or_tool_evidence",
    "conditional_evidence_schema",
    "release_verdicts",
    "failure_policy",
    "loop_budget",
)
EXACT_ID_CATALOGS = (
    "verification_catalog",
    "gates",
    "conditional_gate_catalog",
)


class DuplicateKeyError(ValueError):
    """Raised when JSON attempts to overwrite a prior key."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_contract(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return value


def indexed(
    items: Any,
    label: str,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"{label}[{index}] lacks a string id")
            continue
        item_id = item["id"]
        if item_id in result:
            errors.append(f"{label} duplicates id: {item_id}")
            continue
        result[item_id] = item
    return result


def string_set(
    value: Any,
    label: str,
    errors: list[str],
) -> set[str]:
    if (
        not isinstance(value, list)
        or not all(isinstance(item, str) and item for item in value)
        or len(value) != len(set(value))
    ):
        errors.append(f"{label} must be a unique non-empty string list")
        return set()
    return set(value)


def require_superset(
    old_value: Any,
    new_value: Any,
    label: str,
    errors: list[str],
) -> None:
    old_set = string_set(old_value, f"old {label}", errors)
    new_set = string_set(new_value, f"new {label}", errors)
    removed = sorted(old_set - new_set)
    if removed:
        errors.append(f"weakened {label}; removed={removed}")


def verify_requirements(
    old: dict[str, Any],
    new: dict[str, Any],
    errors: list[str],
) -> None:
    old_requirements = indexed(old.get("requirements"), "old requirements", errors)
    new_requirements = indexed(new.get("requirements"), "new requirements", errors)
    for requirement_id, old_requirement in old_requirements.items():
        new_requirement = new_requirements.get(requirement_id)
        if new_requirement is None:
            errors.append(f"removed requirement: {requirement_id}")
            continue
        old_severity = old_requirement.get("severity")
        new_severity = new_requirement.get("severity")
        if old_severity not in SEVERITY or new_severity not in SEVERITY:
            errors.append(f"invalid requirement severity: {requirement_id}")
        elif SEVERITY[new_severity] < SEVERITY[old_severity]:
            errors.append(f"lowered requirement severity: {requirement_id}")
        if new_requirement.get("statement") != old_requirement.get("statement"):
            errors.append(
                f"changed frozen requirement statement: {requirement_id}"
            )
        for field in ("source_values", "hazards", "verification"):
            require_superset(
                old_requirement.get(field),
                new_requirement.get(field),
                f"{field} for requirement {requirement_id}",
                errors,
            )


def verify_exact_catalog(
    old: dict[str, Any],
    new: dict[str, Any],
    field: str,
    errors: list[str],
) -> None:
    old_items = indexed(old.get(field), f"old {field}", errors)
    new_items = indexed(new.get(field), f"new {field}", errors)
    for item_id, old_item in old_items.items():
        new_item = new_items.get(item_id)
        if new_item is None:
            errors.append(f"removed {field} entry: {item_id}")
        elif new_item != old_item:
            errors.append(f"changed frozen {field} entry: {item_id}")


def verify_conditionals(
    old: dict[str, Any],
    new: dict[str, Any],
    errors: list[str],
) -> None:
    old_requirements = set(
        indexed(old.get("requirements"), "old requirements", errors)
    )
    old_gates = indexed(
        old.get("conditional_gates"),
        "old conditional_gates",
        errors,
    )
    new_gates = indexed(
        new.get("conditional_gates"),
        "new conditional_gates",
        errors,
    )
    for gate_id, old_gate in old_gates.items():
        if new_gates.get(gate_id) != old_gate:
            errors.append(f"changed frozen conditional gate: {gate_id}")
    for gate_id, gate in new_gates.items():
        if gate_id in old_gates:
            continue
        applies_to = string_set(
            gate.get("applies_to_requirements"),
            f"new conditional gate {gate_id} applies_to_requirements",
            errors,
        )
        moved = sorted(applies_to & old_requirements)
        if moved:
            errors.append(
                f"new conditional gate {gate_id} applies to frozen "
                f"requirements: {moved}"
            )


def verify_change_control(
    old: dict[str, Any],
    new: dict[str, Any],
    errors: list[str],
) -> None:
    old_control = old.get("change_control")
    new_control = new.get("change_control")
    expected_fields = {
        "before_freeze",
        "freeze_action",
        "trusted_git_remote",
        "frozen_files",
        "repository_frozen_files",
        "after_freeze",
        "closure_mutation_policy",
    }
    if (
        not isinstance(old_control, dict)
        or not isinstance(new_control, dict)
        or set(old_control) != expected_fields
        or set(new_control) != expected_fields
    ):
        errors.append("change_control schema differs")
        return
    for field in (
        "before_freeze",
        "freeze_action",
        "trusted_git_remote",
        "after_freeze",
        "closure_mutation_policy",
    ):
        if new_control[field] != old_control[field]:
            errors.append(f"changed frozen change_control.{field}")
    for field in ("frozen_files", "repository_frozen_files"):
        require_superset(
            old_control[field],
            new_control[field],
            f"change_control.{field}",
            errors,
        )


def verify(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    old_version = old.get("schema_version")
    new_version = new.get("schema_version")
    if (
        type(old_version) is not int
        or type(new_version) is not int
        or new_version <= old_version
    ):
        errors.append("successor schema_version must be a greater integer")
    if (
        not isinstance(old.get("contract_id"), str)
        or not isinstance(new.get("contract_id"), str)
        or old.get("contract_id") == new.get("contract_id")
    ):
        errors.append("successor contract_id must be a distinct string")
    for field in EXACT_NORMATIVE_FIELDS:
        if new.get(field) != old.get(field):
            errors.append(f"changed frozen normative field: {field}")
    require_superset(
        old.get("protected_paths"),
        new.get("protected_paths"),
        "protected_paths",
        errors,
    )
    require_superset(
        old.get("required_artifacts"),
        new.get("required_artifacts"),
        "required_artifacts",
        errors,
    )
    verify_requirements(old, new, errors)
    for field in EXACT_ID_CATALOGS:
        verify_exact_catalog(old, new, field, errors)
    verify_conditionals(old, new, errors)
    verify_change_control(old, new, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_contract", type=Path)
    parser.add_argument("new_contract", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        old = load_contract(args.old_contract)
        new = load_contract(args.new_contract)
        errors = verify(old, new)
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKeyError,
        ValueError,
    ) as exc:
        errors = [f"contract input is invalid: {exc}"]
    payload = {
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    elif errors:
        print("contract supersession verification: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            "contract supersession verification: PASS "
            "(no frozen requirement or control weakened)"
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
