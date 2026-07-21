from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from prototype.backtest import BacktestConfig, MovingAverageStrategy, PricePoint, evaluate_split


ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
RUN = ROOT / "data" / "runs" / "backtest_v1"
SOURCE_URLS = {
    "NASDAQCOM": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM",
    "SP500": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500",
}


def load_series(path: Path, column: str) -> dict[str, Decimal]:
    values: dict[str, Decimal] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row[column] not in ("", "."):
                values[row["observation_date"]] = Decimal(row[column])
    return values


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def phase_dict(phase: object) -> dict[str, object]:
    return {
        "name": phase.name,
        "start_date": phase.start_date,
        "end_date": phase.end_date,
        "strategy_return": str(phase.strategy_return),
        "benchmark_return": str(phase.benchmark_return),
        "relative_difference": str(phase.strategy_return - phase.benchmark_return),
        "trade_count": len(phase.trades),
        "no_future_information": phase.no_future_information,
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


def main() -> None:
    instrument = load_series(RAW / "NASDAQCOM.csv", "NASDAQCOM")
    benchmark = load_series(RAW / "SP500.csv", "SP500")
    dates = sorted(set(instrument).intersection(benchmark))
    prices = [PricePoint(date, instrument[date]) for date in dates]
    benchmark_points = [PricePoint(date, benchmark[date]) for date in dates]

    config = BacktestConfig(
        development_start="2016-07-18",
        development_end="2020-12-31",
        holdout_start="2021-01-04",
        holdout_end="2025-12-31",
        transaction_cost_rate=Decimal("0.001"),
    )
    result = evaluate_split(
        prices,
        benchmark_points,
        MovingAverageStrategy(lookback=20),
        config,
    )
    if not result.development.no_future_information or not result.holdout.no_future_information:
        raise RuntimeError("backtest failed the no-future-information audit")

    RUN.mkdir(parents=True, exist_ok=True)
    output = {
        "case_id": "fred-index-moving-average-v1",
        "instrument": "NASDAQCOM",
        "benchmark": "SP500",
        "source_files": {
            "NASDAQCOM": {
                "path": str(RAW / "NASDAQCOM.csv"),
                "url": SOURCE_URLS["NASDAQCOM"],
                "sha256": sha256_file(RAW / "NASDAQCOM.csv"),
            },
            "SP500": {
                "path": str(RAW / "SP500.csv"),
                "url": SOURCE_URLS["SP500"],
                "sha256": sha256_file(RAW / "SP500.csv"),
            },
        },
        "strategy": {
            "type": "moving_average_baseline",
            "lookback": 20,
            "transaction_cost_rate": str(config.transaction_cost_rate),
            "execution": "next common close",
        },
        "development": phase_dict(result.development),
        "holdout": phase_dict(result.holdout),
        "interpretation": [
            "This is a validation artifact for the backtest engine.",
            "The parameters were not optimized against the holdout phase.",
            "The price-index benchmark does not include dividends.",
            "The result is not evidence of a durable investment edge.",
        ],
    }
    (RUN / "backtest_result.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = """# 历史检验引擎真实来源案例

本案例使用本地保存的 FRED 日收盘序列，运行一个固定的移动平均基准规则。它的目的，是验证交易成本、开发区间、留出区间、基准和无未来信息审计，而不是寻找或宣称策略优势。

结果文件：prototype/data/runs/backtest_v1/backtest_result.json

案例明确记录了：

- 来源文件和哈希。
- 固定参数和下一共同收盘执行约定。
- 开发区间与留出区间。
- 每个阶段的系统结果、基准结果、交易记录和无未来信息检查。
- 价格指数不含分红，以及参数未对留出区间优化的限制。

运行命令：

    python3 -m prototype.run_real_data_backtest
"""
    (RUN / "backtest_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"development": phase_dict(result.development), "holdout": phase_dict(result.holdout)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

