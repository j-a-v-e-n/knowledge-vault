"""4 个评估轴 (proposal §4):

1. MAE (BPM), overall + stratified by HR bands
2. Per-motion-level MAE (low/medium/high accel quartiles)
3. λ-appropriateness (parametric only): LLM λ vs oracle λ* on 100-window subset
4. Token cost & latency

跑完所有系统后,这个脚本汇总成单一 results/summary.json + 几张图。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np


def mae(truths: list[float], preds: list[float]) -> float:
    """Mean Absolute Error in BPM."""
    arr = np.abs(np.array(truths) - np.array(preds))
    arr = arr[~np.isnan(arr)]
    return float(np.mean(arr)) if len(arr) else float("nan")


def stratified_mae(truths: list[float], preds: list[float], strat_values: list[float], n_bins: int = 4) -> dict:
    """按 strat_values 分位数分箱后报每箱 MAE."""
    truths = np.array(truths)
    preds = np.array(preds)
    strat = np.array(strat_values)
    quantiles = np.quantile(strat, np.linspace(0, 1, n_bins + 1))
    out = {}
    for i in range(n_bins):
        lo, hi = quantiles[i], quantiles[i + 1]
        mask = (strat >= lo) & (strat <= hi)
        out[f"bin_{i + 1}_({lo:.2f}-{hi:.2f})"] = mae(truths[mask].tolist(), preds[mask].tolist())
    return out


def lambda_appropriateness(
    pilot_results: list[dict],
    windows_subset: list,
    grid: np.ndarray | None = None,
) -> dict:
    """对一个 100 窗口 subset, 比较 LLM 的 λ 跟 grid-search 最优 λ*.

    Args:
        pilot_results: llm_lambda.py 的 results, 含 ('lambda', 'subject', 'window')
        windows_subset: data.Window 列表 (匹配 pilot_results 顺序)

    Returns:
        {"correlation": float, "mae_penalty_bpm": float, ...}
    """
    from troika_lite import oracle_lambda  # 延迟 import 防循环

    llm_lambdas = []
    oracle_lambdas = []
    llm_errs = []
    oracle_errs = []

    if grid is None:
        grid = np.linspace(0.1, 3.0, 30)

    for r, w in zip(pilot_results, windows_subset):
        if r.get("lambda") is None or r.get("hr_pred") is None:
            continue
        llm_lam = float(r["lambda"])
        ora_lam, ora_err = oracle_lambda(w, lam_grid=grid)
        llm_err = float(r.get("abs_err") or 0.0)
        llm_lambdas.append(llm_lam)
        oracle_lambdas.append(ora_lam)
        llm_errs.append(llm_err)
        oracle_errs.append(ora_err)

    if len(llm_lambdas) < 5:
        return {"error": "too few valid samples"}

    corr = float(np.corrcoef(llm_lambdas, oracle_lambdas)[0, 1])
    penalty = float(np.mean(llm_errs) - np.mean(oracle_errs))
    return {
        "correlation": corr,
        "mae_penalty_bpm": penalty,
        "n_windows": len(llm_lambdas),
        "llm_lambdas_mean": float(np.mean(llm_lambdas)),
        "oracle_lambdas_mean": float(np.mean(oracle_lambdas)),
    }


def write_summary(systems_results: dict, out_path: str = "results/summary.json"):
    """统一汇总各 system 的 metric, 写到 results/summary.json + 打印一个对比表."""
    os.makedirs("results", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(systems_results, f, indent=2)
    print(f"\n=== 系统对比 (Final report Table 1) ===")
    print(f"{'System':<25} {'Overall MAE':<12} {'Cost/Call':<12} {'Latency':<10}")
    print("-" * 60)
    for name, r in systems_results.items():
        mae_v = r.get("overall_mae", "—")
        cost_v = r.get("cost_per_call_usd", "—")
        lat = r.get("latency_ms", "—")
        if isinstance(mae_v, float):
            mae_v = f"{mae_v:.2f}"
        if isinstance(cost_v, float):
            cost_v = f"${cost_v:.4f}"
        print(f"{name:<25} {mae_v:<12} {cost_v:<12} {lat:<10}")
    print(f"\nFull JSON: {out_path}")


if __name__ == "__main__":
    print("evaluate.py — 主要从 run_all.py 调用. 直接跑可读已有 results/*.json")
    res_dir = Path("results")
    if not res_dir.exists():
        print("  results/ 还没东西. 先跑 troika_lite.py / rf_baseline.py / llm_lambda.py")
    else:
        for f in sorted(res_dir.glob("*.json")):
            print(f"  - {f.name}")
