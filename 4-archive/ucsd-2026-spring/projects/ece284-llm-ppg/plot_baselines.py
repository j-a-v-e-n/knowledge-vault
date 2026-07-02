"""画 TROIKA-lite vs RF baseline 的 per-subject MAE 对比 bar chart.

Midterm report (5/20) §4 / Final report §5 直接能引这张图.

Output: results/baselines_comparison.png + results/baselines_comparison.pdf
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load_results():
    """载入两个 baseline 的 LOSO 结果."""
    troika = json.loads(Path("results/troika_loso.json").read_text())
    rf = json.loads(Path("results/rf_loso.json").read_text())
    return troika, rf


def main():
    troika, rf = load_results()

    n_subj = 12
    subjects = list(range(1, n_subj + 1))
    troika_mae = troika["per_subject_mae"]
    rf_mae = rf["per_subject_mae"]
    troika_overall = troika["overall_mae"]
    rf_overall = rf["overall_mae"]

    # 双 subplot:
    #   左: per-subject bar chart (RF vs TROIKA)
    #   右: scatter MAE-vs-accel-rms 看 motion 影响 (用 RF predictions)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.6, 1]})

    # --- 左: per-subject bar ---
    ax = axes[0]
    width = 0.38
    x = np.arange(n_subj)
    b1 = ax.bar(x - width / 2, troika_mae, width, label=f"TROIKA-lite (overall {troika_overall:.2f})", color="#cc4c54")
    b2 = ax.bar(x + width / 2, rf_mae, width, label=f"Random Forest (overall {rf_overall:.2f})", color="#4c72b0")

    # overall lines
    ax.axhline(troika_overall, color="#cc4c54", linestyle="--", alpha=0.4, lw=1)
    ax.axhline(rf_overall, color="#4c72b0", linestyle="--", alpha=0.4, lw=1)
    # paper reference (TROIKA full M-FOCUSS = 2.34)
    ax.axhline(2.34, color="black", linestyle=":", alpha=0.6, lw=1)
    ax.text(n_subj - 0.5, 2.34 + 1.5, "TROIKA paper (full M-FOCUSS) = 2.34", fontsize=8, color="black", ha="right")

    # bar value labels
    for bars in (b1, b2):
        for rect in bars:
            h = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, h + 0.5, f"{h:.1f}",
                    ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([f"S{s}" for s in subjects])
    ax.set_xlabel("Subject (LOSO test fold)")
    ax.set_ylabel("MAE (BPM)")
    ax.set_title("Per-subject HR estimation MAE — IEEE SPC 2015 (LOSO)")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, max(max(troika_mae), max(rf_mae)) * 1.15)

    # --- 右: scatter MAE-vs-motion (RF predictions) ---
    ax = axes[1]
    rf_preds = rf.get("all_predictions", [])  # list of (truth, pred, accel_rms)
    if not rf_preds:
        # fallback: 不画 scatter, 只画文字说明
        ax.text(0.5, 0.5, "(no per-window predictions in rf_loso.json)\n→ rerun rf_baseline.py to enable scatter",
                ha="center", va="center", transform=ax.transAxes, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
    else:
        # 实际是 list of [truth, pred, accel_rms]
        truths = np.array([p[0] for p in rf_preds])
        preds = np.array([p[1] for p in rf_preds])
        accel_rms = np.array([p[2] for p in rf_preds])
        abs_err = np.abs(preds - truths)

        # 按 motion level 分箱 — IEEE SPC 2015 calibrated thresholds (与 llm_lambda 一致)
        # 实测 P25=1.24 / P50=1.52 / P75=1.76 / max=2.26
        low = accel_rms < 1.3
        med = (accel_rms >= 1.3) & (accel_rms < 1.7)
        hi = accel_rms >= 1.7

        bp = ax.boxplot(
            [abs_err[low], abs_err[med], abs_err[hi]],
            tick_labels=[f"low\n(n={low.sum()})", f"med\n(n={med.sum()})", f"high\n(n={hi.sum()})"],
            patch_artist=True,
            widths=0.55,
            showfliers=False,
        )
        for patch, color in zip(bp["boxes"], ["#5db35d", "#d9a73c", "#cc4c54"]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_ylabel("Per-window |error| (BPM)  RF baseline")
        ax.set_xlabel("Motion regime (accel_rms)")
        ax.set_title("Where motion hurts most")
        ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    out_png = Path("results/baselines_comparison.png")
    out_pdf = Path("results/baselines_comparison.pdf")
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    print(f"Saved → {out_png}")
    print(f"Saved → {out_pdf}")

    # 打印 quick stats 给报告 §4 用
    print(f"\n=== Quick stats for report §4 ===")
    print(f"TROIKA-lite overall MAE:   {troika_overall:.2f} BPM (best subj 4 = {min(troika_mae):.2f}, worst subj 10 = {max(troika_mae):.2f})")
    print(f"Random Forest overall MAE: {rf_overall:.2f} BPM (best subj {1+rf_mae.index(min(rf_mae))} = {min(rf_mae):.2f}, worst subj {1+rf_mae.index(max(rf_mae))} = {max(rf_mae):.2f})")
    print(f"RF improvement over TROIKA: {(troika_overall - rf_overall) / troika_overall * 100:.1f}%")
    print(f"Reference (TROIKA paper full M-FOCUSS): 2.34 BPM")


if __name__ == "__main__":
    main()
