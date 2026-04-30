"""端到端 entry point — 一个命令跑全部 / 部分实验。

Daemon 凌晨调用:
    python run_all.py --scope committed   # TROIKA + RF + λ on full LOSO
    python run_all.py --scope all          # + ReAct (Week 9+)
    python run_all.py --scope pilot        # 快速 sanity check, ~5 min

每次跑都把结果写到 results/<system>_<ts>.json + 汇总到 results/summary.json。
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np

from data import IEEESPC2015Dataset, loso_folds


def _now() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def run_troika_lite(ds, lam: float = 1.0) -> dict:
    """跑 TROIKA-lite on all subjects (no training, just per-subject pass).

    Returns dict ready for evaluate.write_summary.
    """
    from troika_lite import estimate_hr

    print("\n=== System: TROIKA-lite ===")
    truths, preds, accel_rms_list, motions = [], [], [], []
    per_subj_mae = []
    for s in range(1, ds.n_subjects + 1):
        ws = ds.windows_for_subject(s)
        errs = []
        for w in ws:
            est = estimate_hr(w, lam=lam)
            if not np.isnan(est):
                truths.append(w.hr_truth)
                preds.append(est)
                a = float(np.sqrt(np.mean(np.sum(w.accel**2, axis=0))))
                accel_rms_list.append(a)
                errs.append(abs(est - w.hr_truth))
        if errs:
            per_subj_mae.append(float(np.mean(errs)))
            print(f"  subj {s}: MAE = {per_subj_mae[-1]:.2f} BPM ({len(errs)} windows)")

    overall = float(np.mean(per_subj_mae)) if per_subj_mae else float("nan")
    print(f"  Overall MAE: {overall:.2f} BPM")
    return {
        "overall_mae": overall,
        "per_subject_mae": per_subj_mae,
        "n_windows": len(truths),
        "cost_per_call_usd": 0.0,
        "latency_ms": "fast (FFT only)",
    }


def run_rf(ds) -> dict:
    """跑 RF baseline LOSO."""
    from rf_baseline import loso_evaluate

    print("\n=== System: Random Forest LOSO ===")
    res = loso_evaluate(ds, verbose=True)
    return {
        "overall_mae": res["overall_mae"],
        "per_subject_mae": res["per_subject_mae"],
        "n_windows": len(res["all_predictions"]),
        "cost_per_call_usd": 0.0,
        "latency_ms": "fast (sklearn predict)",
    }


def run_llm_lambda(ds, model: str, subjects: list[int], pilot_only: bool = False) -> dict:
    """跑 Claude λ-generator on selected subjects."""
    from llm_lambda import LambdaGenerator, run_subject

    print(f"\n=== System: Claude λ-generator ({model}) ===")
    gen = LambdaGenerator(model=model)
    all_results = []
    for s in subjects:
        rs = run_subject(ds, s, gen)
        if pilot_only:
            rs = rs[:30]
        all_results.extend(rs)
        valid = [r for r in rs if r.get("abs_err") is not None]
        if valid:
            mae = float(np.mean([r["abs_err"] for r in valid]))
            print(f"  subj {s}: MAE = {mae:.2f} BPM ({len(valid)} valid)")

    valid = [r for r in all_results if r.get("abs_err") is not None]
    overall = float(np.mean([r["abs_err"] for r in valid])) if valid else float("nan")
    return {
        "overall_mae": overall,
        "n_windows": len(valid),
        "tokens_in": gen.tokens_in,
        "tokens_out": gen.tokens_out,
        "n_calls": gen.calls,
        "cost_total_usd": gen.cost_usd(),
        "cost_per_call_usd": gen.cost_usd() / max(gen.calls, 1),
        "results": all_results,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--scope", choices=["pilot", "committed", "all"], default="committed")
    p.add_argument("--model", default="claude-sonnet-4-5")
    p.add_argument("--out-prefix", default=None)
    args = p.parse_args()

    out_prefix = args.out_prefix or f"run_{_now()}"
    Path("results").mkdir(exist_ok=True)
    out_dir = Path("results") / out_prefix
    out_dir.mkdir(exist_ok=True)

    ds = IEEESPC2015Dataset(args.data_dir)
    print(f"Dataset: {ds.n_subjects} subjects in {ds.data_dir}")

    systems_results = {}

    if args.scope in ("pilot", "committed", "all"):
        systems_results["TROIKA-lite (λ=1.0)"] = run_troika_lite(ds, lam=1.0)
        with open(out_dir / "troika.json", "w") as f:
            json.dump(systems_results["TROIKA-lite (λ=1.0)"], f, indent=2)

    if args.scope in ("committed", "all"):
        systems_results["Random Forest"] = run_rf(ds)
        with open(out_dir / "rf.json", "w") as f:
            json.dump(systems_results["Random Forest"], f, indent=2)

    if args.scope == "pilot":
        # Pilot: 1 subject, 30 windows, ~30 API calls, ~$0.05
        systems_results["Claude λ-gen (pilot)"] = run_llm_lambda(
            ds, args.model, subjects=[1], pilot_only=True
        )
    elif args.scope in ("committed", "all"):
        # Full: all 12 subjects, ~1800 calls, ~$5
        systems_results["Claude λ-gen"] = run_llm_lambda(
            ds, args.model, subjects=list(range(1, ds.n_subjects + 1))
        )
        with open(out_dir / "llm_lambda.json", "w") as f:
            # 大文件,results 单独存
            r = systems_results["Claude λ-gen"].copy()
            results_full = r.pop("results", [])
            json.dump(r, f, indent=2)
            with open(out_dir / "llm_lambda_per_window.json", "w") as f2:
                json.dump(results_full, f2, indent=2)

    if args.scope == "all":
        print("\n=== System: Claude ReAct (Week 9 stretch — 当前 STUB) ===")
        # Week 9 推进时填这里
        systems_results["Claude ReAct"] = {"status": "stub — Week 9"}

    # 汇总
    from evaluate import write_summary

    write_summary(systems_results, out_path=str(out_dir / "summary.json"))


if __name__ == "__main__":
    main()
