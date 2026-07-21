from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol, Sequence


Signal = Literal["buy", "sell", "hold"]


@dataclass(frozen=True)
class PricePoint:
    date: str
    close: Decimal


class Strategy(Protocol):
    def signal(self, history: Sequence[PricePoint]) -> Signal:
        ...


@dataclass(frozen=True)
class MovingAverageStrategy:
    lookback: int

    def signal(self, history: Sequence[PricePoint]) -> Signal:
        if self.lookback <= 0:
            raise ValueError("lookback must be positive")
        if len(history) < self.lookback:
            return "hold"
        window = history[-self.lookback :]
        average = sum(point.close for point in window) / Decimal(self.lookback)
        return "buy" if history[-1].close > average else "sell"


@dataclass(frozen=True)
class Trade:
    entry_date: str
    exit_date: str
    entry_price: Decimal
    exit_price: Decimal
    net_return: Decimal


@dataclass(frozen=True)
class PhaseResult:
    name: str
    start_date: str
    end_date: str
    strategy_return: Decimal
    benchmark_return: Decimal
    trades: tuple[Trade, ...]
    decision_dates: tuple[str, ...]
    visible_through_dates: tuple[str, ...]

    @property
    def no_future_information(self) -> bool:
        return all(
            decision_date == visible_date
            for decision_date, visible_date in zip(
                self.decision_dates,
                self.visible_through_dates,
            )
        )


@dataclass(frozen=True)
class BacktestConfig:
    development_start: str
    development_end: str
    holdout_start: str
    holdout_end: str
    transaction_cost_rate: Decimal


@dataclass(frozen=True)
class SplitResult:
    development: PhaseResult
    holdout: PhaseResult
    transaction_cost_rate: Decimal


def _validate_prices(prices: Sequence[PricePoint]) -> None:
    if not prices:
        raise ValueError("price series is empty")
    previous_date = ""
    for point in prices:
        if point.date <= previous_date:
            raise ValueError("price dates must be strictly increasing")
        if point.close <= 0:
            raise ValueError("prices must be positive")
        previous_date = point.date


def _phase_points(
    prices: Sequence[PricePoint],
    start_date: str,
    end_date: str,
) -> list[PricePoint]:
    selected = [point for point in prices if start_date <= point.date <= end_date]
    if len(selected) < 2:
        raise ValueError("a phase needs at least two observations")
    return selected


def _trade_return(
    entry_price: Decimal,
    exit_price: Decimal,
    transaction_cost_rate: Decimal,
) -> Decimal:
    if transaction_cost_rate < 0 or transaction_cost_rate >= 1:
        raise ValueError("transaction cost rate must be between zero and one")
    return (
        (exit_price / entry_price)
        * (Decimal("1") - transaction_cost_rate)
        * (Decimal("1") - transaction_cost_rate)
        - Decimal("1")
    )


def run_phase(
    prices: Sequence[PricePoint],
    benchmark: Sequence[PricePoint],
    strategy: Strategy,
    name: str,
    start_date: str,
    end_date: str,
    transaction_cost_rate: Decimal,
) -> PhaseResult:
    _validate_prices(prices)
    _validate_prices(benchmark)
    phase = _phase_points(prices, start_date, end_date)
    benchmark_phase = _phase_points(benchmark, start_date, end_date)
    benchmark_by_date = {point.date: point for point in benchmark_phase}
    if [point.date for point in phase] != list(benchmark_by_date):
        raise ValueError("price and benchmark dates must match within a phase")

    open_entry: PricePoint | None = None
    trades: list[Trade] = []
    decision_dates: list[str] = []
    visible_through_dates: list[str] = []

    for index, current in enumerate(phase[:-1]):
        history = tuple(point for point in prices if point.date <= current.date)
        if not history or history[-1].date != current.date:
            raise ValueError("strategy history is not bounded by the decision date")
        signal = strategy.signal(history)
        decision_dates.append(current.date)
        visible_through_dates.append(history[-1].date)
        next_point = phase[index + 1]

        if open_entry is None and signal == "buy":
            open_entry = next_point
        elif open_entry is not None and signal == "sell":
            trades.append(
                Trade(
                    entry_date=open_entry.date,
                    exit_date=next_point.date,
                    entry_price=open_entry.close,
                    exit_price=next_point.close,
                    net_return=_trade_return(
                        open_entry.close,
                        next_point.close,
                        transaction_cost_rate,
                    ),
                )
            )
            open_entry = None

    if open_entry is not None:
        final_point = phase[-1]
        trades.append(
            Trade(
                entry_date=open_entry.date,
                exit_date=final_point.date,
                entry_price=open_entry.close,
                exit_price=final_point.close,
                net_return=_trade_return(
                    open_entry.close,
                    final_point.close,
                    transaction_cost_rate,
                ),
            )
        )

    strategy_multiplier = Decimal("1")
    for trade in trades:
        strategy_multiplier *= Decimal("1") + trade.net_return
    strategy_return = strategy_multiplier - Decimal("1")
    benchmark_return = benchmark_phase[-1].close / benchmark_phase[0].close - Decimal("1")
    return PhaseResult(
        name=name,
        start_date=phase[0].date,
        end_date=phase[-1].date,
        strategy_return=strategy_return,
        benchmark_return=benchmark_return,
        trades=tuple(trades),
        decision_dates=tuple(decision_dates),
        visible_through_dates=tuple(visible_through_dates),
    )


def evaluate_split(
    prices: Sequence[PricePoint],
    benchmark: Sequence[PricePoint],
    strategy: Strategy,
    config: BacktestConfig,
) -> SplitResult:
    if config.development_end >= config.holdout_start:
        raise ValueError("development and holdout phases must not overlap")
    development = run_phase(
        prices,
        benchmark,
        strategy,
        "development",
        config.development_start,
        config.development_end,
        config.transaction_cost_rate,
    )
    holdout = run_phase(
        prices,
        benchmark,
        strategy,
        "holdout",
        config.holdout_start,
        config.holdout_end,
        config.transaction_cost_rate,
    )
    return SplitResult(
        development=development,
        holdout=holdout,
        transaction_cost_rate=config.transaction_cost_rate,
    )

