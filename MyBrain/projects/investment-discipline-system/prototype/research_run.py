from __future__ import annotations

from prototype.backtest import PhaseResult, SplitResult
from prototype.discipline_system import AppendOnlyLedger


def _phase_payload(phase: PhaseResult) -> dict[str, object]:
    return {
        "name": phase.name,
        "start_date": phase.start_date,
        "end_date": phase.end_date,
        "strategy_return": str(phase.strategy_return),
        "benchmark_return": str(phase.benchmark_return),
        "relative_difference": str(phase.strategy_return - phase.benchmark_return),
        "no_future_information": phase.no_future_information,
        "decision_dates": list(phase.decision_dates),
        "visible_through_dates": list(phase.visible_through_dates),
        "trades": [
            {
                "entry_date": trade.entry_date,
                "exit_date": trade.exit_date,
                "entry_price": str(trade.entry_price),
                "exit_price": str(trade.exit_price),
                "net_return": str(trade.net_return),
            }
            for trade in phase.trades
        ],
    }


def record_backtest_run(
    result: SplitResult,
    *,
    run_id: str,
    strategy_version: str,
    data_snapshot: str,
    occurred_at: str,
    ledger: AppendOnlyLedger,
) -> str:
    if not result.development.no_future_information or not result.holdout.no_future_information:
        raise ValueError("cannot record a backtest that failed the no-future-information audit")
    return ledger.append(
        "backtest_run",
        {
            "run_id": run_id,
            "strategy_version": strategy_version,
            "data_snapshot": data_snapshot,
            "transaction_cost_rate": str(result.transaction_cost_rate),
            "development": _phase_payload(result.development),
            "holdout": _phase_payload(result.holdout),
        },
        occurred_at,
    )
