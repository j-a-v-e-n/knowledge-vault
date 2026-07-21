from __future__ import annotations

import csv
from datetime import datetime, time
from decimal import Decimal
import hashlib
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
    record_paper_workflow,
)


ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
RUN = ROOT / "data" / "runs" / "real_data_case_v2"
CALCULATION_VERSION = "paper-case-v2"
DECISION_TARGET = "2024-01-02"
LOOKBACK_OBSERVATIONS = 20
HOLDING_OBSERVATIONS = 20
ROUND_TRIP_COST = Decimal("0.001")

SOURCE_URLS = {
    "NASDAQCOM": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=NASDAQCOM",
    "SP500": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500",
}


def load_series(path: Path, column: str) -> dict[str, Decimal]:
    values: dict[str, Decimal] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            value = row[column]
            if value not in ("", "."):
                values[row["observation_date"]] = Decimal(value)
    return values


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def timestamp(date_value: str) -> str:
    return datetime.combine(
        datetime.fromisoformat(date_value).date(),
        time(23, 59),
    ).isoformat(timespec="minutes") + "+00:00"


def first_on_or_after(dates: list[str], target: str) -> int:
    for index, date_value in enumerate(dates):
        if date_value >= target:
            return index
    raise ValueError(f"no observation on or after {target}")


def validate_required_dates(
    required_dates: list[str],
    series: dict[str, Decimal],
    series_name: str,
) -> None:
    missing = [date_value for date_value in required_dates if date_value not in series]
    if missing:
        raise ValueError(f"{series_name} has missing observations in the required window: {missing}")


def reusable_result_or_none(
    result_path: Path,
    calculation_version: str,
    source_files: dict[str, dict[str, str]],
) -> dict[str, object] | None:
    if not result_path.exists():
        return None
    previous = json.loads(result_path.read_text(encoding="utf-8"))
    current_hashes = {name: value["sha256"] for name, value in source_files.items()}
    previous_sources = previous.get("source_files", {})
    previous_hashes = {name: value.get("sha256") for name, value in previous_sources.items()}
    if previous.get("calculation_version") == calculation_version and previous_hashes == current_hashes:
        return previous
    raise RuntimeError(
        "saved source snapshot or calculation version changed; use a new run directory instead of overwriting"
    )


def calculate_case() -> dict[str, object]:
    instrument = load_series(RAW / "NASDAQCOM.csv", "NASDAQCOM")
    benchmark = load_series(RAW / "SP500.csv", "SP500")
    instrument_dates = sorted(instrument)
    decision_index = first_on_or_after(instrument_dates, DECISION_TARGET)
    if decision_index < LOOKBACK_OBSERVATIONS:
        raise ValueError("not enough pre-decision observations for the lookback")
    entry_index = decision_index + 1
    exit_index = entry_index + HOLDING_OBSERVATIONS
    if exit_index >= len(instrument_dates):
        raise ValueError("not enough post-entry observations for the holding window")

    selected_dates = instrument_dates[decision_index - LOOKBACK_OBSERVATIONS : exit_index + 1]
    validate_required_dates(selected_dates, benchmark, "SP500")
    decision_date = instrument_dates[decision_index]
    entry_date = instrument_dates[entry_index]
    exit_date = instrument_dates[exit_index]
    prior_values = [instrument[date] for date in instrument_dates[decision_index - LOOKBACK_OBSERVATIONS : decision_index]]
    decision_value = instrument[decision_date]
    trailing_mean = sum(prior_values, Decimal("0")) / Decimal(len(prior_values))
    action = "buy" if decision_value > trailing_mean else "no_trade"
    if action != "buy":
        raise ValueError("the fixed demonstration date did not produce the expected paper signal")

    packet = EvidencePacket(
        idea_id="fred-index-trend-demo",
        as_of=timestamp(decision_date),
        evidence=(
            Evidence(
                source="NASDAQCOM FRED CSV",
                source_type="source data file",
                observed_at=timestamp(decision_date),
                claim_kind="fact",
                statement="The source file contains the decision-date closing observation.",
                url=SOURCE_URLS["NASDAQCOM"],
            ),
            Evidence(
                source="SP500 FRED CSV",
                source_type="source data file",
                observed_at=timestamp(decision_date),
                claim_kind="fact",
                statement="The source file contains the benchmark observation series.",
                url=SOURCE_URLS["SP500"],
            ),
        ),
        invalidation_conditions=(
            "The source observation is revised or cannot be reproduced from the saved file.",
            "The trend condition is no longer true at a future review.",
        ),
    )
    recommendation = Recommendation(
        action="buy",
        thesis="For this pipeline demonstration only, the decision-date index close is above its trailing lookback mean.",
        conditions=("Use paper execution only.", "Do not treat the index as a directly tradable security."),
        invalidation_conditions=packet.invalidation_conditions,
        uncertainty="This is a mechanical pipeline example, not evidence of a durable investment edge.",
    )
    decision = Decision(
        status="accept",
        rationale="Accept the mechanical signal for paper-record testing only.",
        decided_at=timestamp(decision_date),
        chosen_action="buy",
        emotion_note="Calm; this is a paper-only pipeline test.",
        deviated_from_recommendation=False,
    )
    order = PaperOrder(
        order_id="fred-index-trend-demo-order",
        idea_id=packet.idea_id,
        action="buy",
        allocation_fraction=0.1,
        submitted_at=timestamp(entry_date),
    )
    rules = RiskRules(max_allocation_fraction=0.2, max_orders_per_window=1)

    source_files = {
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
    }
    RUN.mkdir(parents=True, exist_ok=True)
    result_path = RUN / "case_result.json"
    reusable = reusable_result_or_none(result_path, CALCULATION_VERSION, source_files)
    if reusable is not None:
        return reusable
    ledger = AppendOnlyLedger(RUN / "ledger.jsonl")
    gate = record_paper_workflow(packet, recommendation, decision, order, rules, (), ledger)
    if not gate.allowed:
        raise RuntimeError(f"paper gate rejected the demonstration case: {gate.reasons}")

    instrument_gross = instrument[exit_date] / instrument[entry_date] - Decimal("1")
    instrument_net = instrument_gross - ROUND_TRIP_COST
    benchmark_return = benchmark[exit_date] / benchmark[entry_date] - Decimal("1")
    relative_difference = instrument_net - benchmark_return
    review = PaperReview(
        idea_id=packet.idea_id,
        reviewed_at=timestamp(exit_date),
        system_return=str(instrument_net),
        benchmark_return=str(benchmark_return),
        executed_as_planned=True,
        observations=(
            "The result uses price-index observations, not a total-return series.",
            "The cost assumption is illustrative and has not been calibrated.",
            "The case is a pipeline verification artifact, not a strategy evaluation.",
        ),
        benchmark_series="SP500",
        source_snapshot="FRED CSV files hashed in case_result.json",
    )
    record_paper_review(review, ledger)
    valid, errors = ledger.verify()
    if not valid:
        raise RuntimeError(f"ledger verification failed: {errors}")

    result = {
        "calculation_version": CALCULATION_VERSION,
        "case_id": packet.idea_id,
        "source_files": source_files,
        "data_quality": {
            "required_window_start": selected_dates[0],
            "required_window_end": selected_dates[-1],
            "missing_instrument_observations": [],
            "missing_benchmark_observations": [],
        },
        "decision": {
            "date": decision_date,
            "instrument": "NASDAQCOM",
            "instrument_close": str(decision_value),
            "trailing_lookback_mean": str(trailing_mean),
            "action": action,
        },
        "paper_execution": {
            "entry_date": entry_date,
            "entry_close": str(instrument[entry_date]),
            "exit_date": exit_date,
            "exit_close": str(instrument[exit_date]),
            "allocation_fraction_assumption": str(order.allocation_fraction),
            "gate_allowed": gate.allowed,
            "gate_reasons": list(gate.reasons),
        },
        "benchmark": {
            "series": "SP500",
            "entry_close": str(benchmark[entry_date]),
            "exit_close": str(benchmark[exit_date]),
        },
        "derived_review": {
            "round_trip_cost_assumption": str(ROUND_TRIP_COST),
            "instrument_net_return": str(instrument_net),
            "benchmark_price_return": str(benchmark_return),
            "relative_difference": str(relative_difference),
            "ledger_valid": valid,
            "ledger_errors": list(errors),
        },
    }
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = f"""# 真实来源纸面案例

## 目的

这是第一个纵切片的管线验证，不是投资建议，也不是策略有效性的证明。

## 来源

- NASDAQCOM：FRED 日收盘 CSV，来源文件已保存并计算 SHA-256。
- SP500：FRED 日收盘 CSV，作为并列基准，来源文件已保存并计算 SHA-256。

FRED 的这两个序列是价格指数；本案例不把它们描述为包含分红的总回报。

## 案例过程

- 决策日期：{decision_date}
- 纸面进入日期：{entry_date}
- 纸面复盘日期：{exit_date}
- 研究规则：决策日收盘值高于此前固定观察窗口的均值时，生成纸面买入建议。
- 人工决策：接受，但仅用于纸面记录。
- 风险闸门：通过；真实券商和真实资金均未接入。

## 证据与复盘

来源观察值、来源文件哈希、风险闸门结果、纸面事件链和派生复盘字段保存在 case_result.json 与 ledger.jsonl。

派生收益字段由程序从来源文件计算，不被当作来源事实；成本参数是未校准的演示假设。该案例不能证明策略存在优势。

## 可复核命令

    python3 -m prototype.run_real_data_case
"""
    (RUN / "case_report.md").write_text(report, encoding="utf-8")
    return result


def main() -> None:
    result = calculate_case()
    print(json.dumps(result["derived_review"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
