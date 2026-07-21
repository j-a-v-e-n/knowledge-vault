from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path

from prototype.backtest import BacktestConfig, MovingAverageStrategy, PricePoint, evaluate_split
from prototype.contracts import DataSnapshot, MarketRecord
from prototype.discipline_system import (
    AppendOnlyLedger,
    Decision,
    Evidence,
    EvidencePacket,
    PaperOrder,
    PaperReview,
    Recommendation,
    RiskRules,
    record_paper_review,
)
from prototype.paper import PaperAccount, PaperOrderRequest
from prototype.research_run import record_backtest_run
from prototype.run_real_data_case import (
    DECISION_TARGET,
    HOLDING_OBSERVATIONS,
    LOOKBACK_OBSERVATIONS,
    RAW,
    SOURCE_URLS,
    first_on_or_after,
    load_series,
    sha256_file,
    timestamp,
    validate_required_dates,
)
from prototype.workflow import run_gated_paper_workflow


ROOT = Path(__file__).parent
RUN = ROOT / "data" / "runs" / "real_data_unified_v2"
CALCULATION_VERSION = "real-data-unified-v2"
ROUND_TRIP_COST = Decimal("0.001")


def _manifest() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(RAW / f"{name}.csv"),
            "url": SOURCE_URLS[name],
            "sha256": sha256_file(RAW / f"{name}.csv"),
        }
        for name in ("NASDAQCOM", "SP500")
    }


def _manifest_hash(manifest: dict[str, dict[str, str]]) -> str:
    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _raw_files_hash() -> str:
    digest = hashlib.sha256()
    for name in ("NASDAQCOM", "SP500"):
        with (RAW / f"{name}.csv").open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _snapshot_records(
    instrument: dict[str, Decimal],
    benchmark: dict[str, Decimal],
    dates: tuple[str, ...],
) -> tuple[MarketRecord, ...]:
    return tuple(
        record
        for date_value in dates
        for record in (
            MarketRecord(
                symbol="NASDAQCOM",
                field="close",
                value=instrument[date_value],
                observed_at=timestamp(date_value),
                available_at=timestamp(date_value),
            ),
            MarketRecord(
                symbol="SP500",
                field="close",
                value=benchmark[date_value],
                observed_at=timestamp(date_value),
                available_at=timestamp(date_value),
            ),
        )
    )


def run_case() -> dict[str, object]:
    RUN.mkdir(parents=True, exist_ok=True)
    result_path = RUN / "run_result.json"
    ledger_path = RUN / "ledger.jsonl"
    manifest = _manifest()
    snapshot_id = f"fred-manifest-{_manifest_hash(manifest)}"
    raw_payload_hash = _raw_files_hash()
    if result_path.exists():
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        if (
            previous.get("calculation_version") == CALCULATION_VERSION
            and previous.get("source_files") == manifest
        ):
            valid, errors = AppendOnlyLedger(ledger_path).verify()
            if not valid:
                raise RuntimeError(f"saved unified ledger is invalid: {errors}")
            return previous
        raise RuntimeError("saved source snapshot or calculation version changed; use a new run directory")

    instrument = load_series(RAW / "NASDAQCOM.csv", "NASDAQCOM")
    benchmark = load_series(RAW / "SP500.csv", "SP500")
    common_dates = tuple(sorted(set(instrument).intersection(benchmark)))
    prices = [PricePoint(date_value, instrument[date_value]) for date_value in common_dates]
    benchmark_points = [PricePoint(date_value, benchmark[date_value]) for date_value in common_dates]

    backtest = evaluate_split(
        prices,
        benchmark_points,
        MovingAverageStrategy(lookback=20),
        BacktestConfig(
            development_start="2016-07-18",
            development_end="2020-12-31",
            holdout_start="2021-01-04",
            holdout_end="2025-12-31",
            transaction_cost_rate=ROUND_TRIP_COST,
        ),
    )

    decision_index = first_on_or_after(list(common_dates), DECISION_TARGET)
    if decision_index < LOOKBACK_OBSERVATIONS:
        raise ValueError("not enough pre-decision observations for the lookback")
    entry_index = decision_index + 1
    exit_index = entry_index + HOLDING_OBSERVATIONS
    if exit_index >= len(common_dates):
        raise ValueError("not enough post-entry observations for the holding window")
    selected_dates = tuple(common_dates[decision_index - LOOKBACK_OBSERVATIONS : exit_index + 1])
    validate_required_dates(list(selected_dates), benchmark, "SP500")

    decision_date = common_dates[decision_index]
    entry_date = common_dates[entry_index]
    exit_date = common_dates[exit_index]
    decision_time = timestamp(decision_date)
    data_snapshot = DataSnapshot(
        snapshot_id=snapshot_id,
        source="FRED saved CSV manifest",
        source_version=CALCULATION_VERSION,
        retrieved_at="2026-02-04T09:00:00+00:00",
        raw_payload_sha256=raw_payload_hash,
        records=_snapshot_records(instrument, benchmark, (decision_date,)),
    )
    snapshot_errors = data_snapshot.validate_for_decision(decision_time)
    if snapshot_errors:
        raise RuntimeError(f"data snapshot failed the decision-time audit: {snapshot_errors}")

    packet = EvidencePacket(
        idea_id="real-data-unified-fred-case",
        as_of=decision_time,
        evidence=(
            Evidence(
                source="NASDAQCOM FRED CSV",
                source_type="saved source data file",
                observed_at=decision_time,
                claim_kind="fact",
                statement="The saved source file contains the decision-date observation.",
                url=SOURCE_URLS["NASDAQCOM"],
            ),
            Evidence(
                source="SP500 FRED CSV",
                source_type="saved source data file",
                observed_at=decision_time,
                claim_kind="fact",
                statement="The saved source file contains the benchmark observation.",
                url=SOURCE_URLS["SP500"],
            ),
        ),
        invalidation_conditions=(
            "The source manifest changes or cannot be reproduced.",
            "The case is interpreted as evidence of a durable investment edge.",
        ),
        version=CALCULATION_VERSION,
    )
    recommendation = Recommendation(
        action="buy",
        thesis="This case only tests that a saved real-source input can flow into a paper record.",
        conditions=("Paper execution only.", "Do not treat an index as a directly tradable security."),
        invalidation_conditions=packet.invalidation_conditions,
        uncertainty="The price-index source and illustrative cost do not establish an investment edge.",
        version=CALCULATION_VERSION,
    )
    decision = Decision(
        status="accept",
        rationale="Accept the real-source case for pipeline verification only.",
        decided_at=decision_time,
        chosen_action="buy",
        emotion_note="Calm; this is a paper-only pipeline test.",
        deviated_from_recommendation=False,
    )
    paper_order = PaperOrder(
        order_id="real-data-unified-paper-order",
        idea_id=packet.idea_id,
        action="buy",
        allocation_fraction=0.1,
        submitted_at=timestamp(entry_date),
    )
    initial_cash = instrument[entry_date] * Decimal("10")
    account = PaperAccount(initial_cash)
    request = PaperOrderRequest(
        order_id=paper_order.order_id,
        symbol="NASDAQCOM",
        side="buy",
        quantity=Decimal("1"),
        reference_price=instrument[entry_date],
        submitted_at=paper_order.submitted_at,
    )

    ledger = AppendOnlyLedger(ledger_path)
    ledger.append(
        "research_run_started",
        {
            "run_id": "real-data-unified-fred-v1",
            "calculation_version": CALCULATION_VERSION,
            "source_files": manifest,
            "data_snapshot": snapshot_id,
        },
        "2026-02-04T09:00:00+00:00",
    )
    record_backtest_run(
        backtest,
        run_id="real-data-unified-fred-v1",
        strategy_version="moving-average-lookback-20",
        data_snapshot=snapshot_id,
        occurred_at="2026-02-04T09:01:00+00:00",
        ledger=ledger,
    )
    workflow = run_gated_paper_workflow(
        packet,
        recommendation,
        decision,
        paper_order,
        request,
        RiskRules(
            max_allocation_fraction=0.2,
            max_orders_per_window=1,
            version=CALCULATION_VERSION,
        ),
        (),
        account,
        ledger,
    )
    if not workflow.gate.allowed or workflow.fill is None:
        raise RuntimeError(f"real-source paper workflow failed: {workflow}")

    allocation = Decimal("0.1")
    system_return = account.mark_to_market({"NASDAQCOM": instrument[exit_date]}) / initial_cash - Decimal("1")
    benchmark_asset_return = benchmark[exit_date] / benchmark[entry_date] - Decimal("1")
    review = PaperReview(
        idea_id=packet.idea_id,
        reviewed_at=timestamp(exit_date),
        system_return=str(system_return),
        benchmark_return=str(allocation * benchmark_asset_return),
        executed_as_planned=True,
        observations=(
            "The benchmark is a FRED price index and does not include dividends.",
            "The local paper account does not represent a real broker.",
            "The result is a source-and-ledger integration artifact, not a strategy evaluation.",
        ),
        benchmark_series="SP500 price index with matched allocation assumption",
        source_snapshot=snapshot_id,
    )
    record_paper_review(review, ledger)
    ledger.append(
        "research_run_completed",
        {
            "run_id": "real-data-unified-fred-v1",
            "data_snapshot_valid": not snapshot_errors,
            "paper_gate_allowed": workflow.gate.allowed,
            "paper_execution_status": workflow.execution.status if workflow.execution else None,
            "review_recorded": True,
        },
        review.reviewed_at,
    )
    valid, errors = ledger.verify()
    if not valid:
        raise RuntimeError(f"real-source unified ledger verification failed: {errors}")

    result = {
        "calculation_version": CALCULATION_VERSION,
        "source_files": manifest,
        "data_snapshot": {
            "snapshot_id": snapshot_id,
            "raw_payload_sha256": raw_payload_hash,
            "decision_time_valid": not snapshot_errors,
            "errors": list(snapshot_errors),
            "selected_window_start": selected_dates[0],
            "selected_window_end": selected_dates[-1],
        },
        "ledger": {
            "path": str(ledger_path),
            "valid": valid,
            "errors": list(errors),
            "event_types": [record["event_type"] for record in ledger.records()],
        },
        "paper": {
            "gate_allowed": workflow.gate.allowed,
            "execution_status": workflow.execution.status if workflow.execution else None,
            "reviewed_at": review.reviewed_at,
        },
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = """# 真实来源统一研究运行

## 目的

用已保存并哈希的 FRED CSV，把真实来源快照、历史检验、纸面工作流、追加式账本和基准复盘放进同一条运行链。这是管线验证，不是投资建议或策略有效性证明。

## 已验证

- 来源文件清单和哈希进入研究运行起点。
- 数据快照区分观察时间、可见时间和获取时间，并通过决策时点审计。
- 历史检验结果写入同一账本，并保留开发/留出与无未来信息审计。
- 纸面建议、人工决定、风险闸门、纸面成交和复盘写入同一账本。
- 运行结果、来源快照和账本校验结果可重载；来源或计算版本改变时不覆盖旧结果。

## 重要边界

FRED 序列是价格指数，不是正式总回报基准；纸面账户是本地模型，不是券商；当前运行没有真实资金、真实订单或外部执行权限。

## 可复核命令

    python3 -m prototype.run_real_data_unified

运行产物位于本目录下的 run_result.json、ledger.jsonl 和 run_report.md。
"""
    (RUN / "run_report.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    result = run_case()
    print(json.dumps(result["ledger"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
