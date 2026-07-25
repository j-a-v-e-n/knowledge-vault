#!/usr/bin/env python3
"""One-shot isolated adapter for the preregistered RS-04 non-search probe.

The adapter executes only the reviewed pure-Python oracle member from the
pinned source archive. It neither imports the ml4t package nor connects to a
live surface. Its comparison implementation uses Decimal and shares no code
with the external oracle.
"""

from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
import tarfile
import types
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


PROBE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = PROBE_DIR.parent
INPUT_PATH = PROBE_DIR / "FIXED_INPUT.json"
ARCHIVE_PATH = (
    EVIDENCE_DIR
    / "snapshots"
    / "ML4T_BACKTEST_459abd81f2f30dc70cf38a40da7591af3da2d02a_tests_architecture.tar"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def decimal_text(value: Decimal) -> str:
    return format(value, "f")


def load_external_oracle(case: dict) -> tuple[types.ModuleType, str]:
    expected_archive_hash = case["component"]["archive_sha256"]
    actual_archive_hash = sha256_path(ARCHIVE_PATH)
    if actual_archive_hash != expected_archive_hash:
        raise RuntimeError(
            f"archive hash mismatch: expected {expected_archive_hash}, got {actual_archive_hash}"
        )

    member_name = case["component"]["member"]
    with tarfile.open(ARCHIVE_PATH, mode="r:") as archive:
        member = archive.getmember(member_name)
        if not member.isfile():
            raise RuntimeError(f"oracle member is not a regular file: {member_name}")
        member_stream = archive.extractfile(member)
        if member_stream is None:
            raise RuntimeError(f"cannot read oracle member: {member_name}")
        source = member_stream.read()

    expected_member_hash = case["component"]["member_sha256"]
    actual_member_hash = sha256_bytes(source)
    if actual_member_hash != expected_member_hash:
        raise RuntimeError(
            f"member hash mismatch: expected {expected_member_hash}, got {actual_member_hash}"
        )

    module_name = "_rs04_pinned_external_oracle"
    module = types.ModuleType(module_name)
    module.__file__ = f"{ARCHIVE_PATH}!/{member_name}"
    sys.modules[module_name] = module
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    finally:
        sys.modules.pop(module_name, None)
    return module, actual_member_hash


def run_external(module: types.ModuleType, case: dict) -> dict[str, float]:
    bars = [module.OracleBar(**bar) for bar in case["bars"]]
    signals = [module.OracleSignal(**signal) for signal in case["signals"]]
    fill_rule = module.OracleFillRule(
        timing=module.FillTiming.SAME_BAR,
        commission_rate=case["commission_rate"],
        slippage_rate=case["slippage_rate"],
    )
    result = module.run_oracle(
        bars=bars,
        signals=signals,
        fill_rule=fill_rule,
        initial_cash=case["initial_cash"],
    )
    if len(result.trades) != 1:
        raise RuntimeError(f"expected one closed trade, got {len(result.trades)}")
    trade = result.trades[0]
    return {
        "entry_fill": trade.entry_price,
        "exit_fill": trade.exit_price,
        "gross_pnl": trade.gross_pnl,
        "fees": trade.fees,
        "net_pnl": trade.net_pnl,
        "pnl_percent": trade.pnl_percent,
        "net_return": trade.net_return,
        "entry_slippage_cost": trade.entry_slippage_cost,
        "exit_slippage_cost": trade.exit_slippage_cost,
        "total_pnl": result.total_pnl,
        "final_cash": result.final_cash,
    }


def run_independent(case: dict) -> dict[str, Decimal]:
    if (
        case["semantics"]["fill_timing"] != "SAME_BAR"
        or len(case["signals"]) != 2
        or case["signals"][0]["direction"] != "long"
        or case["signals"][0]["action"] != "entry"
        or case["signals"][1]["direction"] != "long"
        or case["signals"][1]["action"] != "exit"
        or case["signals"][0]["quantity"] != case["signals"][1]["quantity"]
    ):
        raise RuntimeError("fixed case is outside this adapter's declared accounting semantics")

    entry_signal, exit_signal = case["signals"]
    entry_base = case["bars"][entry_signal["bar_index"]]["close"]
    exit_base = case["bars"][exit_signal["bar_index"]]["close"]
    quantity = entry_signal["quantity"]
    commission_rate = case["commission_rate"]
    slippage_rate = case["slippage_rate"]
    initial_cash = case["initial_cash"]

    entry_fill = entry_base * (Decimal("1") + slippage_rate)
    exit_fill = exit_base * (Decimal("1") - slippage_rate)
    entry_commission = entry_fill * quantity * commission_rate
    exit_commission = exit_fill * quantity * commission_rate
    fees = entry_commission + exit_commission
    gross_pnl = (exit_fill - entry_fill) * quantity
    net_pnl = gross_pnl - fees
    notional = entry_fill * quantity

    return {
        "entry_fill": entry_fill,
        "exit_fill": exit_fill,
        "gross_pnl": gross_pnl,
        "fees": fees,
        "net_pnl": net_pnl,
        "pnl_percent": gross_pnl / notional,
        "net_return": net_pnl / notional,
        "entry_slippage_cost": abs(entry_fill - entry_base) * quantity,
        "exit_slippage_cost": abs(exit_fill - exit_base) * quantity,
        "total_pnl": net_pnl,
        "final_cash": initial_cash + net_pnl,
    }


def main() -> None:
    input_bytes = INPUT_PATH.read_bytes()
    case = json.loads(input_bytes, parse_float=Decimal)
    module, member_hash = load_external_oracle(case)

    external_case = json.loads(input_bytes)
    external = run_external(module, external_case)
    independent = run_independent(case)
    tolerance = case["semantics"]["absolute_tolerance"]

    comparisons = []
    for field in independent:
        external_decimal = Decimal(str(external[field]))
        difference = abs(external_decimal - independent[field])
        comparisons.append(
            {
                "field": field,
                "external_value": repr(external[field]),
                "independent_value": decimal_text(independent[field]),
                "absolute_difference": decimal_text(difference),
                "absolute_tolerance": decimal_text(tolerance),
                "within_tolerance": difference <= tolerance,
            }
        )

    all_within_tolerance = all(item["within_tolerance"] for item in comparisons)
    receipt = {
        "schema_version": 1,
        "probe_id": "R8-RS04-P1",
        "executed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "command": "python3 -I probe/run_differential_accounting.py",
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "isolated_mode": bool(sys.flags.isolated),
        },
        "component": {
            "name": external_case["component"]["name"],
            "repository": external_case["component"]["repository"],
            "commit": external_case["component"]["commit"],
            "archive_path": str(ARCHIVE_PATH.relative_to(EVIDENCE_DIR)),
            "archive_sha256": external_case["component"]["archive_sha256"],
            "member": external_case["component"]["member"],
            "member_sha256": member_hash,
        },
        "fixed_input": {
            "path": str(INPUT_PATH.relative_to(EVIDENCE_DIR)),
            "sha256": sha256_bytes(input_bytes),
            "case_id": external_case["case_id"],
            "semantics": external_case["semantics"],
        },
        "adapter": {
            "path": str(Path(__file__).resolve().relative_to(EVIDENCE_DIR)),
            "sha256": sha256_path(Path(__file__).resolve()),
            "boundary": [
                "loads one hash-verified member from one hash-verified pinned tar archive",
                "does not import the ml4t package",
                "uses no third-party dependency",
                "contains no broker, credential, HTTP, socket, subprocess, or live-surface code",
                "independent Decimal accounting shares no implementation with the external oracle",
            ],
        },
        "external_observation": external,
        "independent_observation": {
            key: decimal_text(value) for key, value in independent.items()
        },
        "comparison": comparisons,
        "outcome": {
            "all_fields_within_declared_tolerance": all_within_tolerance,
            "classification": (
                "agreement_within_tolerance"
                if all_within_tolerance
                else "accounting_divergence"
            ),
            "causality_claimed": False,
            "winner_selected": False,
            "routing": "review_only",
        },
        "limitations": [
            "One synthetic long round trip is not coverage of shorts, partial fills, corporate actions, event ordering, or prefix causality.",
            "Agreement cannot establish correctness because both implementations may share the same semantic assumption.",
            "The external observation executes only the repository's reference oracle, not the package system under test.",
            "No live surface, broker, credential, network call, or dependency installation was used.",
        ],
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
