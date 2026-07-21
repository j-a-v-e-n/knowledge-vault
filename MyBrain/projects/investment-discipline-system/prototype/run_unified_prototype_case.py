from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

from prototype.backtest import BacktestConfig, MovingAverageStrategy, PricePoint, evaluate_split
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
from prototype.workflow import run_gated_paper_workflow


ROOT = Path(__file__).parent
RUN = ROOT / "data" / "runs" / "unified_prototype_v1"
CALCULATION_VERSION = "unified-prototype-v1"


def _fixture_prices() -> tuple[list[PricePoint], list[PricePoint]]:
    dates = [f"2024-01-{day:02d}" for day in range(1, 13)]
    prices = [10, 11, 12, 13, 12, 11, 10, 11, 12, 14, 15, 16]
    benchmark = [10, 10, 11, 11, 12, 12, 12, 12, 13, 13, 14, 14]
    return (
        [PricePoint(date, Decimal(str(value))) for date, value in zip(dates, prices)],
        [PricePoint(date, Decimal(str(value))) for date, value in zip(dates, benchmark)],
    )


def _snapshot() -> dict[str, object]:
    return {
        "calculation_version": CALCULATION_VERSION,
        "data_snapshot": "controlled-fixture-v1",
        "strategy_version": "moving-average-lookback-fixture",
        "paper_reference_price": "100",
        "paper_review_price": "110",
    }


def run_case() -> dict[str, object]:
    RUN.mkdir(parents=True, exist_ok=True)
    result_path = RUN / "run_result.json"
    ledger_path = RUN / "ledger.jsonl"
    snapshot = _snapshot()
    if result_path.exists():
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        if previous.get("snapshot") == snapshot:
            valid, errors = AppendOnlyLedger(ledger_path).verify()
            if not valid:
                raise RuntimeError(f"saved unified ledger is invalid: {errors}")
            return previous
        raise RuntimeError("saved unified case changed; use a new run directory")

    prices, benchmark = _fixture_prices()
    split = evaluate_split(
        prices,
        benchmark,
        MovingAverageStrategy(lookback=2),
        BacktestConfig(
            development_start="2024-01-01",
            development_end="2024-01-06",
            holdout_start="2024-01-07",
            holdout_end="2024-01-12",
            transaction_cost_rate=Decimal("0.001"),
        ),
    )
    ledger = AppendOnlyLedger(ledger_path)
    ledger.append(
        "research_run_started",
        {"run_id": "unified-prototype-v1", "snapshot": snapshot},
        "2026-02-04T09:00:00+00:00",
    )
    record_backtest_run(
        split,
        run_id="unified-prototype-v1",
        strategy_version="moving-average-lookback-fixture",
        data_snapshot="controlled-fixture-v1",
        occurred_at="2026-02-04T09:01:00+00:00",
        ledger=ledger,
    )

    packet = EvidencePacket(
        idea_id="unified-paper-idea",
        as_of="2026-02-04T09:10:00+00:00",
        evidence=(
            Evidence(
                source="controlled-fixture",
                source_type="local test fixture",
                observed_at="2026-02-04T09:05:00+00:00",
                claim_kind="assumption",
                statement="The fixture is available for an end-to-end paper workflow test.",
            ),
        ),
        invalidation_conditions=("The controlled fixture is no longer reproducible.",),
        version="unified-prototype-v1",
    )
    recommendation = Recommendation(
        action="buy",
        thesis="Use the controlled fixture to connect backtest and paper review records.",
        conditions=("Paper execution only.",),
        invalidation_conditions=packet.invalidation_conditions,
        uncertainty="This is a plumbing test and not a market claim.",
        version="unified-prototype-v1",
    )
    decision = Decision(
        status="accept",
        rationale="Accept the controlled fixture for pipeline verification.",
        decided_at="2026-02-04T09:15:00+00:00",
        chosen_action="buy",
        emotion_note="Calm; this is a paper-only pipeline test.",
        deviated_from_recommendation=False,
    )
    paper_order = PaperOrder(
        order_id="unified-paper-order",
        idea_id=packet.idea_id,
        action="buy",
        allocation_fraction=0.1,
        submitted_at="2026-02-04T09:16:00+00:00",
    )
    account = PaperAccount(Decimal("1000"))
    workflow = run_gated_paper_workflow(
        packet,
        recommendation,
        decision,
        paper_order,
        PaperOrderRequest(
            order_id=paper_order.order_id,
            symbol="DEMO",
            side="buy",
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            submitted_at=paper_order.submitted_at,
        ),
        RiskRules(max_allocation_fraction=0.2, max_orders_per_window=1, version="unified-prototype-v1"),
        (),
        account,
        ledger,
    )
    if not workflow.gate.allowed or workflow.fill is None:
        raise RuntimeError(f"unified paper workflow failed: {workflow}")

    review = PaperReview(
        idea_id=packet.idea_id,
        reviewed_at="2026-02-04T16:00:00+00:00",
        system_return=str(account.mark_to_market({"DEMO": Decimal("110")}) / Decimal("1000") - Decimal("1")),
        benchmark_return="0.08",
        executed_as_planned=True,
        observations=(
            "The backtest event and paper workflow share one ledger.",
            "The benchmark value is a controlled fixture reference.",
            "The run is not evidence of an investment edge.",
        ),
        benchmark_series="controlled-fixture-benchmark",
        source_snapshot="controlled-fixture-v1",
    )
    record_paper_review(review, ledger)
    ledger.append(
        "research_run_completed",
        {
            "run_id": "unified-prototype-v1",
            "paper_gate_allowed": workflow.gate.allowed,
            "paper_execution_status": workflow.execution.status if workflow.execution else None,
            "review_recorded": True,
        },
        review.reviewed_at,
    )
    valid, errors = ledger.verify()
    if not valid:
        raise RuntimeError(f"unified ledger verification failed: {errors}")

    result = {
        "snapshot": snapshot,
        "ledger": {
            "path": str(ledger_path),
            "valid": valid,
            "errors": list(errors),
            "event_types": [record["event_type"] for record in ledger.records()],
        },
        "paper": {
            "gate_allowed": workflow.gate.allowed,
            "execution_status": workflow.execution.status if workflow.execution else None,
            "ending_cash": str(account.cash),
        },
        "review": {"idea_id": review.idea_id, "benchmark_series": review.benchmark_series},
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = """# 统一研究运行原型

## 目的

用受控本地夹具把历史检验、纸面执行、追加式账本和复盘放进同一条运行链。它验证的是模块连接，不是策略有效性。

## 运行链

研究运行开始 → 开发/留出历史检验 → 记录纸面证据、建议、人工决定和风险闸门 → 本地纸面成交 → 与基准并列复盘 → 研究运行完成。

## 当前结论

历史检验事件、纸面工作流事件和复盘事件已经可以写入同一条账本，并通过统一校验恢复。夹具仍然不是市场数据，纸面账户仍然不是券商。

## 可复核命令

    python3 -m prototype.run_unified_prototype_case

结果位于本目录下的 run_result.json，账本位于 ledger.jsonl。
"""
    (RUN / "run_report.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    result = run_case()
    print(json.dumps(result["ledger"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
