"""λ-generator system architecture diagram for ECE 284 update report.

不画代码截图 (syllabus rule). 画 boxes-and-arrows pipeline diagram with
token-cost annotation showing where caching helps.

Output: results/architecture.{png,pdf}
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def main():
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(-0.2, 6.4)
    ax.axis("off")

    # ─── Box style helpers ──────────────────────────────────
    def box(x, y, w, h, label, color, sub=None, fontsize=9):
        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.04,rounding_size=0.10",
            linewidth=1.3, edgecolor="black", facecolor=color, alpha=0.92,
        )
        ax.add_patch(rect)
        if sub is None:
            ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                    fontsize=fontsize, weight="bold")
        else:
            ax.text(x + w / 2, y + h * 0.62, label, ha="center", va="center",
                    fontsize=fontsize, weight="bold")
            ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
                    fontsize=fontsize - 1, style="italic", color="#333")

    def arrow(x1, y1, x2, y2, label=None, label_y_offset=0.18, color="black"):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle="-|>", mutation_scale=14, lw=1.4, color=color,
        ))
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + label_y_offset
            ax.text(mx, my, label, ha="center", va="center", fontsize=8.0,
                    color="#222")

    # ─── Row 1: Inputs ──────────────────────────────────────
    box(0.15, 4.10, 1.95, 0.95, "PPG window\n(8 sec, 125 Hz)",
        color="#e8f1fb", sub="2-ch wrist sensor")
    box(0.15, 2.95, 1.95, 0.95, "Accelerometer\n(3-axis, 8 sec)",
        color="#e8f1fb", sub="motion ground truth")

    # ─── Feature extractor ─────────────────────────────────
    box(2.55, 3.15, 1.85, 1.70, "Feature\nExtraction",
        color="#fff4d4",
        sub="FFT + bandpass\n+ peak detect")

    arrow(2.10, 4.55, 2.55, 4.40)
    arrow(2.10, 3.40, 2.55, 3.55)

    # ─── 6-field summary ───────────────────────────────────
    summary_text = (
        "WindowSummary (6 fields)\n"
        "ppg_dom_freq_hz, ppg_top3_peaks_hz/mag\n"
        "accel_dom_freq_hz, accel_rms\n"
        "motion_level, last_3_HR_estimates"
    )
    box(4.85, 3.30, 2.85, 1.45, summary_text, color="#fff4d4", fontsize=8.0)
    arrow(4.40, 4.00, 4.85, 4.00)

    # ─── Claude (highlighted box) ──────────────────────────
    box(8.10, 3.70, 2.70, 1.05,
        "Claude Sonnet 4.5",
        color="#ffd9d2",
        sub="Anthropic Messages API\nprompt caching ephemeral")

    arrow(7.70, 4.20, 8.10, 4.20, label="user prompt", label_y_offset=0.20)

    # cached system prompt callout (above Claude)
    box(8.10, 5.10, 2.70, 0.45,
        "Cached system prompt (5,898 tok, hit rate 94%)",
        color="#cfe7d6", fontsize=8.0)
    ax.add_patch(FancyArrowPatch(
        (9.45, 5.10), (9.45, 4.75),
        arrowstyle="-|>", mutation_scale=12, lw=1.2, color="#1a6b1a",
        linestyle="--",
    ))

    # ─── λ output ──────────────────────────────────────────
    arrow(9.45, 3.70, 9.45, 3.10, label="λ ∈ [0.1, 3.0] + reason",
          label_y_offset=0.15)
    box(8.10, 1.95, 2.70, 1.05, "JSON parse + clip",
        color="#fff4d4",
        sub='{"lambda": 1.2, "reason": "..."}')

    # ─── λ → fixed pipeline ────────────────────────────────
    arrow(8.10, 2.45, 7.20, 2.45, label="λ", label_y_offset=0.18)
    box(4.30, 1.95, 2.85, 1.05,
        "Fixed TROIKA-lite pipeline",
        color="#e8d8f5",
        sub="cleaned = PPG − λ × accel_spec")

    # ─── HR output ─────────────────────────────────────────
    arrow(4.30, 2.45, 3.45, 2.45, label="cleaned\nspectrum", label_y_offset=0.30)
    box(0.50, 1.95, 2.95, 1.05, "HR estimate (BPM)",
        color="#cfe7d6",
        sub="peak detect → freq × 60")

    # ─── History feedback loop ─────────────────────────────
    # arrow from HR back to summary (dashed)
    ax.add_patch(FancyArrowPatch(
        (1.00, 1.95), (1.00, 1.40),
        arrowstyle="-|>", mutation_scale=11, lw=1.0, color="#666",
        linestyle="--",
    ))
    ax.add_patch(FancyArrowPatch(
        (1.00, 1.40), (5.30, 1.40),
        arrowstyle="-", mutation_scale=11, lw=1.0, color="#666",
        linestyle="--",
    ))
    ax.add_patch(FancyArrowPatch(
        (5.30, 1.40), (5.30, 3.30),
        arrowstyle="-|>", mutation_scale=11, lw=1.0, color="#666",
        linestyle="--",
    ))
    ax.text(3.10, 1.20, "last 3 HR estimates (temporal prior)",
            ha="center", va="center", fontsize=7.5, color="#666",
            style="italic")

    # ─── Cost annotation ───────────────────────────────────
    ax.text(5.5, -0.05,
            "30-window pilot (subj 1, Sonnet 4.5):  MAE 7.90 BPM  •  "
            "cost \\$0.110  •  94.1% cache hit rate  •  full 1800-window LOSO projection ≈ \\$6.6",
            ha="center", va="center", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#f5f5f5",
                      edgecolor="#999", linewidth=0.8))

    # ─── Legend (top-left) ─────────────────────────────────
    legend_handles = [
        mpatches.Patch(color="#e8f1fb", label="Sensor inputs"),
        mpatches.Patch(color="#fff4d4", label="Deterministic preprocessing"),
        mpatches.Patch(color="#ffd9d2", label="LLM (this is the contribution)"),
        mpatches.Patch(color="#e8d8f5", label="Fixed pipeline (driven by λ)"),
        mpatches.Patch(color="#cfe7d6", label="Output / cached"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              bbox_to_anchor=(0.01, 1.005), fontsize=7.6,
              frameon=True, edgecolor="#bbb", ncol=1)

    fig.tight_layout()

    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    fig.savefig(out_dir / "architecture.png", dpi=170, bbox_inches="tight")
    fig.savefig(out_dir / "architecture.pdf", bbox_inches="tight")
    print(f"Saved → {out_dir / 'architecture.png'}")
    print(f"Saved → {out_dir / 'architecture.pdf'}")


if __name__ == "__main__":
    main()
