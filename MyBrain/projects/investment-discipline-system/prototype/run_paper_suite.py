from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
import json
from pathlib import Path

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
from prototype.workflow import WorkflowResult, run_gated_paper_workflow


ROOT = Path(__file__).parent
RUN = ROOT / "data" / "runs" / "paper_suite_v3"
CALCULATION_VERSION = "paper-suite-v3"
INITIAL_CASH = Decimal("1000")


def scenario_snapshot() -> dict[str, object]:
    return {
        "initial_cash": str(INITIAL_CASH),
        "cases": [
            {
                "case_id": "accepted-buy",
                "recommendation": "buy",
                "decision": "accept-buy",
                "allocation_fraction": "0.1",
                "quantity": "2",
                "reference_price": "100",
            },
            {
                "case_id": "risk-rejected-over-cap",
                "recommendation": "buy",
                "decision": "accept-buy",
                "allocation_fraction": "0.4",
                "max_allocation_fraction": "0.2",
                "quantity": "1",
                "reference_price": "100",
            },
            {
                "case_id": "human-modified-sell",
                "recommendation": "buy",
                "decision": "modify-to-sell",
                "allocation_fraction": "0.1",
                "quantity": "1",
                "reference_price": "105",
            },
            {
                "case_id": "execution-rejected-insufficient-position",
                "recommendation": "sell",
                "decision": "accept-sell",
                "allocation_fraction": "0.1",
                "quantity": "2",
                "reference_price": "105",
            },
        ],
        "review_mark": {"DEMO": "105"},
        "benchmark_reference": {"entry": "100", "review": "105"},
    }


def _timestamp(hour: int, minute: int) -> str:
    return f"2026-02-03T{hour:02d}:{minute:02d}:00+00:00"


def _packet(case_id: str) -> EvidencePacket:
    return EvidencePacket(
        idea_id=case_id,
        as_of=_timestamp(9, 0),
        evidence=(
            Evidence(
                source="paper-suite-fixture",
                source_type="controlled local fixture",
                observed_at=_timestamp(8, 55),
                claim_kind="assumption",
                statement="This case exists to exercise a workflow branch; it is not market evidence.",
            ),
        ),
        invalidation_conditions=("The controlled fixture is no longer reproducible.",),
        version="paper-suite-v3",
    )


def _recommendation(action: str = "buy") -> Recommendation:
    return Recommendation(
        action=action,  # type: ignore[arg-type]
        thesis="Controlled fixture for checking the paper workflow path.",
        conditions=("Paper execution only.",),
        invalidation_conditions=("The controlled fixture is no longer reproducible.",),
        uncertainty="This case says nothing about investment performance.",
        version="paper-suite-v1",
    )


def _decision(
    case_id: str,
    chosen_action: str,
    status: str = "accept",
    recommendation_action: str = "buy",
) -> Decision:
    deviated = chosen_action != recommendation_action
    return Decision(
        status=status,  # type: ignore[arg-type]
        rationale=f"Controlled decision for {case_id}.",
        decided_at=_timestamp(9, 30),
        chosen_action=chosen_action,  # type: ignore[arg-type]
        emotion_note="Calm; this is a paper-only workflow fixture.",
        deviated_from_recommendation=deviated,
    )


def _run_case(
    *,
    case_id: str,
    recommendation: Recommendation,
    decision: Decision,
    allocation_fraction: float,
    quantity: str,
    reference_price: str,
    max_allocation_fraction: float,
    symbol: str,
    prior_orders: tuple[PaperOrder, ...],
    account: PaperAccount,
    ledger: AppendOnlyLedger,
) -> tuple[PaperOrder, WorkflowResult]:
    order = PaperOrder(
        order_id=f"{case_id}-order",
        idea_id=case_id,
        action=decision.chosen_action,  # type: ignore[arg-type]
        allocation_fraction=allocation_fraction,
        submitted_at=_timestamp(9, 31),
    )
    request = PaperOrderRequest(
        order_id=order.order_id,
        symbol=symbol,
        side=order.action,
        quantity=Decimal(quantity),
        reference_price=Decimal(reference_price),
        submitted_at=order.submitted_at,
    )
    result = run_gated_paper_workflow(
        _packet(case_id),
        recommendation,
        decision,
        order,
        request,
        RiskRules(
            max_allocation_fraction=max_allocation_fraction,
            max_orders_per_window=10,
            version="paper-suite-v3",
        ),
        prior_orders,
        account,
        ledger,
    )
    return order, result


def _outcome(case_id: str, order: PaperOrder, result: WorkflowResult, account: PaperAccount) -> dict[str, object]:
    return {
        "case_id": case_id,
        "order_id": order.order_id,
        "gate_allowed": result.gate.allowed,
        "gate_reasons": list(result.gate.reasons),
        "fill_recorded": result.fill is not None,
        "execution_error": result.execution_error,
        "cash_after": str(account.cash),
    }


def run_suite() -> dict[str, object]:
    RUN.mkdir(parents=True, exist_ok=True)
    result_path = RUN / "suite_result.json"
    ledger_path = RUN / "ledger.jsonl"
    snapshot = scenario_snapshot()
    if result_path.exists():
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        if (
            previous.get("calculation_version") == CALCULATION_VERSION
            and previous.get("scenario_snapshot") == snapshot
        ):
            valid, errors = AppendOnlyLedger(ledger_path).verify()
            if not valid:
                raise RuntimeError(f"saved paper suite ledger is invalid: {errors}")
            return previous
        raise RuntimeError("saved paper suite scenario changed; use a new run directory")

    ledger = AppendOnlyLedger(ledger_path)
    account = PaperAccount(INITIAL_CASH)
    accepted_orders: list[PaperOrder] = []
    outcomes: list[dict[str, object]] = []

    order, result = _run_case(
        case_id="accepted-buy",
        recommendation=_recommendation("buy"),
        decision=_decision("accepted-buy", "buy"),
        allocation_fraction=0.1,
        quantity="2",
        reference_price="100",
        max_allocation_fraction=0.2,
        symbol="DEMO",
        prior_orders=tuple(accepted_orders),
        account=account,
        ledger=ledger,
    )
    outcomes.append(_outcome("accepted-buy", order, result, account))
    if result.gate.allowed:
        accepted_orders.append(order)

    order, result = _run_case(
        case_id="risk-rejected-over-cap",
        recommendation=_recommendation("buy"),
        decision=_decision("risk-rejected-over-cap", "buy"),
        allocation_fraction=0.4,
        quantity="1",
        reference_price="100",
        max_allocation_fraction=0.2,
        symbol="DEMO",
        prior_orders=tuple(accepted_orders),
        account=account,
        ledger=ledger,
    )
    outcomes.append(_outcome("risk-rejected-over-cap", order, result, account))

    order, result = _run_case(
        case_id="human-modified-sell",
        recommendation=_recommendation("buy"),
        decision=_decision("human-modified-sell", "sell", status="modify"),
        allocation_fraction=0.1,
        quantity="1",
        reference_price="105",
        max_allocation_fraction=0.2,
        symbol="DEMO",
        prior_orders=tuple(accepted_orders),
        account=account,
        ledger=ledger,
    )
    outcomes.append(_outcome("human-modified-sell", order, result, account))
    if result.gate.allowed:
        accepted_orders.append(order)

    order, result = _run_case(
        case_id="execution-rejected-insufficient-position",
        recommendation=_recommendation("sell"),
        decision=_decision(
            "execution-rejected-insufficient-position",
            "sell",
            recommendation_action="sell",
        ),
        allocation_fraction=0.1,
        quantity="2",
        reference_price="105",
        max_allocation_fraction=0.2,
        symbol="DEMO",
        prior_orders=tuple(accepted_orders),
        account=account,
        ledger=ledger,
    )
    outcomes.append(_outcome("execution-rejected-insufficient-position", order, result, account))

    review_value = account.mark_to_market({"DEMO": Decimal("105")})
    review = PaperReview(
        idea_id="paper-suite-review",
        reviewed_at=_timestamp(16, 0),
        system_return=str(review_value / INITIAL_CASH - Decimal("1")),
        benchmark_return=str(Decimal("105") / Decimal("100") - Decimal("1")),
        executed_as_planned=False,
        observations=(
            "The suite contains both a risk rejection and an execution failure.",
            "The human changed the recommendation and the deviation is recorded.",
            "All results are controlled fixtures and not evidence of a market edge.",
        ),
        benchmark_series="synthetic controlled reference",
        source_snapshot="scenario_snapshot in suite_result.json",
    )
    record_paper_review(review, ledger)
    ledger_valid, ledger_errors = ledger.verify()
    if not ledger_valid:
        raise RuntimeError(f"paper suite ledger verification failed: {ledger_errors}")

    result = {
        "calculation_version": CALCULATION_VERSION,
        "scenario_snapshot": snapshot,
        "case_outcomes": outcomes,
        "ending_account": {
            "cash": str(account.cash),
            "positions": [asdict(position) for position in account.positions],
            "fills": [asdict(fill) for fill in account.fills],
        },
        "review": asdict(review),
        "ledger": {
            "path": str(ledger_path),
            "valid": ledger_valid,
            "errors": list(ledger_errors),
            "event_types": [record["event_type"] for record in ledger.records()],
        },
    }
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    report = """# 连续纸面运行套件

## 目的

这是本地原型的分支覆盖验证，不是投资策略验证，也不是收益承诺。

## 覆盖的流程分支

- 合法买入：风险闸门通过，纸面账户产生成交。
- 风险拦截：超过预先设定的配置上限，账户状态不变。
- 人工偏离：人工把系统建议改成卖出；偏离被记录，且仍经过同一风险闸门。
- 执行失败：闸门通过，但纸面账户因持仓不足拒绝执行；失败被单独留痕，不伪装成成交。
- 复盘：最终账户状态与一个明确标记的基准参考并列记录。

## 结论

流程已经能把“建议—人工决定—风险闸门—纸面执行—失败/成交—复盘”串在同一条追加式账本中。这里使用的是受控本地夹具，不能说明任何市场优势。

## 可复核命令

    python3 -m prototype.run_paper_suite

结果与账本保存在本目录下的 suite_result.json 与 ledger.jsonl；源代码版本和场景快照改变时，不覆盖旧运行结果。
"""
    (RUN / "suite_report.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    result = run_suite()
    print(json.dumps({"ledger": result["ledger"], "case_outcomes": result["case_outcomes"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
