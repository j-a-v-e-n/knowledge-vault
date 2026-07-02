"""λ-generator pilot vs baselines on Subject 1 first 30 windows.

3 systems plotted on same window range:
  TROIKA-lite  (results/troika_loso.json)
  Random Forest (results/rf_loso.json)
  LLM λ-generator Sonnet 4.5 (results/llm_lambda_pilot_s1_sonnet.json)

Output: results/pilot_subj1_comparison.{png,pdf}
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_subj1_first_30():
    """从 3 个 JSON 抽 subject 1 前 30 windows 的 (truth, pred) for each system."""
    troika_data = json.loads(Path("results/troika_loso.json").read_text())
    # per_subject 是 list, subject 1 = index 0; predictions 列表里前 30 个
    troika_subj1 = troika_data["per_subject"][0]["predictions"][:30]
    troika_truth = [p["truth"] for p in troika_subj1]
    troika_pred = [p["pred"] for p in troika_subj1]

    rf_data = json.loads(Path("results/rf_loso.json").read_text())
    # all_predictions 顺序是 LOSO 折跑出来; fold 1 = subject 1 在 test, 它的 predictions
    # 应该排在最前 (fold 顺序: test_subj=1, test_subj=2, ...).
    # 验证: subject 1 应该有 148 windows, 前 148 应该都是 subject 1.
    # 我们要 subject 1 前 30 windows.
    rf_all = rf_data["all_predictions"]
    rf_subj1 = rf_all[:30]
    rf_truth = [p[0] for p in rf_subj1]
    rf_pred = [p[1] for p in rf_subj1]

    llm_data = json.loads(Path("results/llm_lambda_pilot_s1_sonnet.json").read_text())
    llm_results = llm_data["results"][:30]
    llm_truth = [r["hr_truth"] for r in llm_results]
    llm_pred = [r["hr_pred"] for r in llm_results]
    llm_lam = [r["lambda"] for r in llm_results]

    # sanity: truth should match across 3 systems on same windows
    assert all(abs(t1 - t2) < 0.5 for t1, t2 in zip(troika_truth, llm_truth)), \
        f"truth mismatch troika vs llm: {troika_truth[:5]} vs {llm_truth[:5]}"

    return {
        "windows": list(range(30)),
        "truth": llm_truth,
        "troika": troika_pred,
        "rf": rf_pred,
        "llm": llm_pred,
        "lam": llm_lam,
    }


def main():
    d = load_subj1_first_30()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.5, 5.4),
                                    gridspec_kw={"height_ratios": [3, 1]},
                                    sharex=True)

    # ─── Top: HR estimates over time ──────────────────────
    w = d["windows"]
    ax1.plot(w, d["truth"], "k-", lw=2.4, label="Ground truth (ECG-derived)",
             marker="o", markersize=4, alpha=0.85)
    ax1.plot(w, d["troika"], color="#cc4c54", lw=1.4, marker="s",
             markersize=4, alpha=0.75, label="TROIKA-lite (signal proc.)")
    ax1.plot(w, d["rf"], color="#4c72b0", lw=1.4, marker="^",
             markersize=4, alpha=0.75, label="Random Forest (4 features)")
    ax1.plot(w, d["llm"], color="#d96e1d", lw=1.6, marker="D",
             markersize=4.5, alpha=0.92, label="LLM λ-generator (Sonnet 4.5, cached)")

    # mark outlier windows w16 / w28
    for w_idx, color in [(16, "#d96e1d"), (28, "#d96e1d")]:
        ax1.axvline(w_idx, color="gray", linestyle=":", linewidth=0.7, alpha=0.6)

    ax1.set_ylabel("Heart rate (BPM)")
    ax1.set_title("Subject 1 — first 30 windows: HR estimate vs ground truth (8 s windows, 2 s shift)")
    ax1.legend(loc="upper left", fontsize=9, ncol=2, framealpha=0.94)
    ax1.grid(alpha=0.3)
    ax1.set_ylim(40, 165)

    # MAE annotation in upper-right
    troika_mae = float(np.mean([abs(t - p) for t, p in zip(d["truth"], d["troika"])]))
    rf_mae = float(np.mean([abs(t - p) for t, p in zip(d["truth"], d["rf"])]))
    llm_mae = float(np.mean([abs(t - p) for t, p in zip(d["truth"], d["llm"])]))
    mae_text = (
        f"30-window MAE:\n"
        f"  TROIKA-lite:  {troika_mae:>5.2f} BPM\n"
        f"  Random Forest:{rf_mae:>5.2f} BPM\n"
        f"  LLM λ-gen:    {llm_mae:>5.2f} BPM"
    )
    ax1.text(0.99, 0.97, mae_text, transform=ax1.transAxes,
             ha="right", va="top", fontsize=8.5, family="monospace",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#fafafa",
                       edgecolor="#999", linewidth=0.8))

    # ─── Bottom: λ choice over time ───────────────────────
    ax2.plot(w, d["lam"], color="#d96e1d", lw=1.4, marker="D", markersize=4)
    ax2.axhline(1.0, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax2.set_ylabel("λ chosen")
    ax2.set_xlabel("Window index (0–29 of Subject 1)")
    ax2.grid(alpha=0.3)
    ax2.set_ylim(0, 2.6)

    # annotate outliers
    for w_idx, color in [(16, "#d96e1d"), (28, "#d96e1d")]:
        ax2.axvline(w_idx, color="gray", linestyle=":", linewidth=0.7, alpha=0.6)
        ax1.annotate(f"w{w_idx}", xy=(w_idx, d["llm"][w_idx]),
                     xytext=(w_idx + 0.5, d["llm"][w_idx] + 12 if d["llm"][w_idx] < 80 else d["llm"][w_idx] - 18),
                     fontsize=7.5, color="#d96e1d",
                     arrowprops=dict(arrowstyle="->", color="#d96e1d", lw=0.6))

    fig.tight_layout()

    out_dir = Path("results")
    fig.savefig(out_dir / "pilot_subj1_comparison.png", dpi=170, bbox_inches="tight")
    fig.savefig(out_dir / "pilot_subj1_comparison.pdf", bbox_inches="tight")
    print(f"Saved → {out_dir / 'pilot_subj1_comparison.png'}")
    print(f"Saved → {out_dir / 'pilot_subj1_comparison.pdf'}")

    print(f"\n=== 30-window MAE on Subject 1 ===")
    print(f"  TROIKA-lite:  {troika_mae:.2f} BPM")
    print(f"  Random Forest:{rf_mae:.2f} BPM")
    print(f"  LLM λ-gen:    {llm_mae:.2f} BPM")
    print(f"  → LLM vs TROIKA: {(troika_mae - llm_mae) / troika_mae * 100:+.1f}%")
    print(f"  → LLM vs RF:     {(rf_mae - llm_mae) / rf_mae * 100:+.1f}%")


if __name__ == "__main__":
    main()
