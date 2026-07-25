#!/usr/bin/env python3
"""Reject silent weakening of a frozen acceptance contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SEVERITY = {"minor": 1, "major": 2, "critical": 3}


def by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items}


def verify(old: dict, new: dict) -> list[str]:
    errors: list[str] = []
    old_requirements = by_id(old.get("requirements", []))
    new_requirements = by_id(new.get("requirements", []))
    for req_id, old_req in old_requirements.items():
        new_req = new_requirements.get(req_id)
        if new_req is None:
            errors.append(f"removed requirement: {req_id}")
            continue
        if SEVERITY.get(new_req.get("severity"), 0) < SEVERITY.get(
            old_req.get("severity"), 0
        ):
            errors.append(f"lowered requirement severity: {req_id}")
        if new_req.get("statement") != old_req.get("statement"):
            errors.append(f"changed frozen requirement statement: {req_id}")
        for field in ("source_values", "hazards", "verification"):
            if not set(old_req.get(field, [])).issubset(set(new_req.get(field, []))):
                errors.append(f"weakened {field} for requirement: {req_id}")

    if new.get("scope") != old.get("scope"):
        errors.append("changed frozen scope")
    if new.get("non_goals") != old.get("non_goals"):
        errors.append("changed frozen non_goals")

    old_conditionals = by_id(old.get("conditional_gates", []))
    new_conditionals = by_id(new.get("conditional_gates", []))
    for gate_id, old_gate in old_conditionals.items():
        if new_conditionals.get(gate_id) != old_gate:
            errors.append(f"changed frozen conditional gate: {gate_id}")
    old_required = set(old_requirements)
    for gate_id, gate in new_conditionals.items():
        if gate_id in old_conditionals:
            continue
        moved = set(gate.get("applies_to_requirements", [])) & old_required
        if moved:
            errors.append(
                f"new conditional gate {gate_id} applies to frozen requirements: "
                f"{sorted(moved)}"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old_contract", type=Path)
    parser.add_argument("new_contract", type=Path)
    args = parser.parse_args()
    old = json.loads(args.old_contract.read_text(encoding="utf-8"))
    new = json.loads(args.new_contract.read_text(encoding="utf-8"))
    errors = verify(old, new)
    if errors:
        print("contract supersession verification: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("contract supersession verification: PASS (no frozen requirement weakened)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
