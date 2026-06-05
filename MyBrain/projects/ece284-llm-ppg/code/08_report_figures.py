"""08_report_figures.py — Report figures + sensitivity analysis.

读 5 个 JSON, 不重跑 method:
  - results/troika_loso.json       (A)
  - results/rf_loso.json           (B)
  - results/methodC_loso.json      (C)
  - results/rf_lambda_loso.json    (RF-λ)
  - results/lambda_oracle_loso.json (Oracle)
  - results/motion_breakdown.json   (per-motion 3×3)

Outputs:
  figs/fig_overall_mae.png         — 5 method overall MAE
  figs/fig_per_subject_mae.png     — 11 subj × 4 method + Oracle marker
  figs/fig_motion_breakdown.png    — 3 motion × 3 method (A/B/C)
  figs/fig_lambda_headroom.png     — λ headroom 利用率 horizontal bar
  figs/fig_lambda_distribution.png — per-subject λ box (C / RF-λ / Oracle)

  results/sensitivity.json:
    - with/without subj10 per method
    - per-subject headroom utilization (LLM)
    - median vs mean MAE per method
"""

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
FIGS_DIR = SCRIPT_DIR / "figs"
FIGS_DIR.mkdir(exist_ok=True)


# ===================================================================
# Load all JSONs
# ===================================================================
A = json.load(open(RESULTS_DIR / "troika_loso.json"))
B = json.load(open(RESULTS_DIR / "rf_loso.json"))
C = json.load(open(RESULTS_DIR / "methodC_loso.json"))
RFL = json.load(open(RESULTS_DIR / "rf_lambda_loso.json"))
ORC = json.load(open(RESULTS_DIR / "lambda_oracle_loso.json"))
MOT = json.load(open(RESULTS_DIR / "motion_breakdown.json"))


SUBJECTS = [
    "subj01_type01", "subj02_type02", "subj03_type02", "subj04_type01",
    "subj05_type02", "subj06_type02", "subj07_type02", "subj08_type02",
    "subj10_type02", "subj11_type02", "subj12_type02",
]
SUBJ_LABELS = ["01", "02", "03", "04", "05", "06", "07", "08", "10", "11", "12"]
N_COLD = 10


# ===================================================================
# Per-subject MAE
# ===================================================================
mae_A   = [A["per_subject"][s]["mae"] for s in SUBJECTS]
mae_B   = [B["per_subject"][s]["mae"] for s in SUBJECTS]
mae_C   = [C["per_subject"][s]["mae"] for s in SUBJECTS]
mae_RFL = [RFL["per_subject"][s]["mae"] for s in SUBJECTS]
mae_ORC = [ORC["per_subject"][s]["mae"] for s in SUBJECTS]

overall_A   = float(np.mean(mae_A))
overall_B   = float(np.mean(mae_B))
overall_C   = float(np.mean(mae_C))
overall_RFL = float(np.mean(mae_RFL))
overall_ORC = float(np.mean(mae_ORC))


# ===================================================================
# Color palette
# ===================================================================
COLOR_A     = "#b9ccdf"   # λ-axis, lightest
COLOR_RFL   = "#6e93ba"   # λ-axis, medium
COLOR_C     = "#2a5e8c"   # λ-axis, darker
COLOR_ORC   = "#082a48"   # λ-axis, darkest (oracle floor)
COLOR_B     = "#e08a2a"   # paradigm-2 (orange)


# ===================================================================
# Figure 1: Overall MAE (5 methods)
# ===================================================================
fig, ax = plt.subplots(figsize=(9.5, 5))

labels = ["A\n(fixed λ=1.0)", "RF-λ\n(RF→λ)", "C\n(LLM-λ)",
          "Oracle λ*\n(uses GT)", "B\n(RF→HR)"]
vals = [overall_A, overall_RFL, overall_C, overall_ORC, overall_B]
colors = [COLOR_A, COLOR_RFL, COLOR_C, COLOR_ORC, COLOR_B]
positions = [0, 1, 2, 3, 4.4]      # offset B to visually separate

bars = ax.bar(positions, vals, color=colors, edgecolor="black", linewidth=0.7,
              width=0.7)
for p, v in zip(positions, vals):
    ax.text(p, v + 0.25, f"{v:.2f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold")

ax.set_xticks(positions)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("LOSO Overall MAE (BPM)", fontsize=11)
ax.set_title("Overall MAE across 11 subjects — lower is better", fontsize=12)
ax.set_ylim(0, max(vals) * 1.27)
ax.grid(axis="y", alpha=0.3)

ax.annotate("not deployable\n(uses GT)", xy=(3, overall_ORC),
            xytext=(3, overall_ORC + 1.5),
            ha="center", fontsize=8, color="#555", fontstyle="italic")
ax.annotate("different paradigm\n(no λ; RF→HR)", xy=(4.4, overall_B),
            xytext=(4.4, overall_B + 1.5),
            ha="center", fontsize=8, color="#555", fontstyle="italic")

ax.axvline(x=3.7, color="black", linestyle=":", alpha=0.4, linewidth=0.7)
ax.text(1.5, max(vals) * 1.20, "λ-axis comparison (same pipeline)",
        ha="center", fontsize=9, color="#333")
ax.text(4.4, max(vals) * 1.20, "paradigm\ncomparison",
        ha="center", fontsize=9, color="#333")

plt.tight_layout()
p1 = FIGS_DIR / "fig_overall_mae.png"
plt.savefig(p1, dpi=150, bbox_inches="tight")
plt.close()
print(f"[saved] {p1}")


# ===================================================================
# Figure 2: Per-subject MAE
# ===================================================================
fig, ax = plt.subplots(figsize=(13, 5.5))
x = np.arange(len(SUBJECTS))
w = 0.20

ax.bar(x - 1.5 * w, mae_A,   w, label="A (fixed λ=1.0)", color=COLOR_A,   edgecolor="black", linewidth=0.4)
ax.bar(x - 0.5 * w, mae_RFL, w, label="RF-λ",            color=COLOR_RFL, edgecolor="black", linewidth=0.4)
ax.bar(x + 0.5 * w, mae_C,   w, label="C (LLM-λ)",       color=COLOR_C,   edgecolor="black", linewidth=0.4)
ax.bar(x + 1.5 * w, mae_B,   w, label="B (RF→HR)",       color=COLOR_B,   edgecolor="black", linewidth=0.4)

# Oracle as red X marker (overlay reference)
ax.scatter(x, mae_ORC, marker="X", s=70, color="#c81e2c",
           edgecolor="black", linewidth=0.5, zorder=5, label="Oracle λ*")

# Highlight catastrophic subjects (subj02, subj10) and reversal subjects (subj06, subj07)
for idx, lbl in enumerate(SUBJ_LABELS):
    if lbl in ["02", "10"]:
        ax.axvspan(idx - 0.5, idx + 0.5, color="red", alpha=0.07, zorder=0)
    if lbl in ["06", "07"]:
        ax.axvspan(idx - 0.5, idx + 0.5, color="orange", alpha=0.09, zorder=0)

ax.set_xticks(x)
ax.set_xticklabels([f"subj{l}" for l in SUBJ_LABELS])
ax.set_ylabel("MAE (BPM)", fontsize=11)
ax.set_title("Per-subject MAE — red shade = catastrophic (architecture-bound), "
             "orange = LLM worse than fixed λ",
             fontsize=11)
ax.legend(loc="upper right", fontsize=9, ncol=2)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, max(max(mae_A), max(mae_B), max(mae_C), max(mae_RFL)) * 1.10)

plt.tight_layout()
p2 = FIGS_DIR / "fig_per_subject_mae.png"
plt.savefig(p2, dpi=150, bbox_inches="tight")
plt.close()
print(f"[saved] {p2}")


# ===================================================================
# Figure 3: Per-motion-level MAE (A/B/C)
# ===================================================================
fig, ax = plt.subplots(figsize=(8, 5.2))
groups = ["low", "med", "high"]
x = np.arange(len(groups))
w = 0.26

mae_motion = MOT["mae_by_method_and_motion"]
vals_A = [mae_motion["A"][g] for g in groups]
vals_C = [mae_motion["C"][g] for g in groups]
vals_B = [mae_motion["B"][g] for g in groups]
n_per = MOT["n_windows_per_group_in_intersection"]

bars_A = ax.bar(x - w, vals_A, w, label="A (fixed λ)",  color=COLOR_A, edgecolor="black", linewidth=0.4)
bars_C = ax.bar(x,     vals_C, w, label="C (LLM-λ)",    color=COLOR_C, edgecolor="black", linewidth=0.4)
bars_B = ax.bar(x + w, vals_B, w, label="B (RF→HR)",    color=COLOR_B, edgecolor="black", linewidth=0.4)

# Value labels on top
for bars, vals in [(bars_A, vals_A), (bars_C, vals_C), (bars_B, vals_B)]:
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3,
                f"{v:.2f}", ha="center", va="bottom", fontsize=8)

# Star the winner of each motion group
for i, g in enumerate(groups):
    triple = [(vals_A[i], x[i] - w, "A"),
              (vals_C[i], x[i], "C"),
              (vals_B[i], x[i] + w, "B")]
    triple.sort(key=lambda t: t[0])
    winner_v, winner_x, winner_name = triple[0]
    ax.scatter([winner_x], [winner_v - 1.2], marker="*", s=120,
               color="green", zorder=5)

ax.set_xticks(x)
ax.set_xticklabels([f"low\n(n={n_per['low']})",
                    f"med\n(n={n_per['med']})",
                    f"high\n(n={n_per['high']})"])
ax.set_xlabel("Motion intensity tertile (accel-variance global tertile)")
ax.set_ylabel("MAE (BPM)")
ax.set_title("Per-motion-level MAE — different paradigm wins each motion regime",
             fontsize=11)
ax.legend(loc="upper left", fontsize=9)
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, max(vals_A + vals_B + vals_C) * 1.18)
ax.text(0.99, 0.02, "★ = winner per group", transform=ax.transAxes,
        ha="right", fontsize=8, color="green", style="italic")

plt.tight_layout()
p3 = FIGS_DIR / "fig_motion_breakdown.png"
plt.savefig(p3, dpi=150, bbox_inches="tight")
plt.close()
print(f"[saved] {p3}")


# ===================================================================
# Figure 4: λ headroom utilization
# ===================================================================
fig, ax = plt.subplots(figsize=(10, 4.5))

methods = ["A (baseline, fixed λ=1.0)", "RF-λ (RF predicts λ)",
           "C (LLM-λ via DeepSeek)", "Oracle λ* (uses GT)"]
vals = [overall_A, overall_RFL, overall_C, overall_ORC]
colors = [COLOR_A, COLOR_RFL, COLOR_C, COLOR_ORC]
y_pos = np.arange(len(methods))

bars = ax.barh(y_pos, vals, color=colors, edgecolor="black",
               linewidth=0.5, height=0.65)

# Utilization %
util_RFL = (overall_A - overall_RFL) / (overall_A - overall_ORC) * 100
util_C   = (overall_A - overall_C)   / (overall_A - overall_ORC) * 100

annots = [
    f"  {overall_A:.2f}  ← baseline (0% captured)",
    f"  {overall_RFL:.2f}  ← captured {util_RFL:.1f}% of λ-headroom",
    f"  {overall_C:.2f}  ← captured {util_C:.1f}% of λ-headroom",
    f"  {overall_ORC:.2f}  ← architecture floor (100%, not deployable)",
]
for i, txt in enumerate(annots):
    ax.text(vals[i] + 0.15, i, txt, va="center", fontsize=9)

# Total headroom annotation
ax.axvline(overall_A, color="gray", linestyle=":", alpha=0.5, linewidth=0.7)
ax.axvline(overall_ORC, color="gray", linestyle=":", alpha=0.5, linewidth=0.7)
ax.annotate("", xy=(overall_ORC, -0.55), xytext=(overall_A, -0.55),
            arrowprops=dict(arrowstyle="<->", color="gray", lw=0.7))
ax.text((overall_A + overall_ORC) / 2, -0.80,
        f"Total λ-headroom = A − Oracle = {overall_A - overall_ORC:.2f} BPM",
        ha="center", color="#444", fontsize=9, fontstyle="italic")

ax.set_yticks(y_pos)
ax.set_yticklabels(methods, fontsize=10)
ax.set_xlabel("LOSO Overall MAE (BPM) — lower = better")
ax.set_title("λ-axis headroom: how much of the theoretical λ-improvement "
             "each method captures",
             fontsize=11)
ax.set_xlim(0, max(vals) * 1.45)
ax.invert_yaxis()
ax.grid(axis="x", alpha=0.3)
ax.set_ylim(len(methods) - 0.5, -1.1)

plt.tight_layout()
p4 = FIGS_DIR / "fig_lambda_headroom.png"
plt.savefig(p4, dpi=150, bbox_inches="tight")
plt.close()
print(f"[saved] {p4}")


# ===================================================================
# Figure 5: λ distributions per subject (LLM / RF-λ / Oracle)
# ===================================================================
def get_post_cold_lams(method_data, subj_key, list_field):
    sd = method_data["per_subject"][subj_key]
    lams = sd[list_field][N_COLD:]
    return [float(l) for l in lams
            if l is not None and not (isinstance(l, float) and np.isnan(l))]


llm_lams = [get_post_cold_lams(C, k, "lambdas_used")    for k in SUBJECTS]
rfl_lams = [get_post_cold_lams(RFL, k, "predicted_lambdas") for k in SUBJECTS]
orc_lams = [get_post_cold_lams(ORC, k, "oracle_lambdas")    for k in SUBJECTS]


fig, ax = plt.subplots(figsize=(14, 5.5))
n_subj = len(SUBJECTS)
positions = np.arange(n_subj)
w = 0.26

for lams_list, color, offset in [
    (llm_lams, COLOR_C,   -w),
    (rfl_lams, COLOR_RFL,  0),
    (orc_lams, "#888888",  w),
]:
    ax.boxplot(
        lams_list,
        positions=positions + offset,
        widths=w * 0.85,
        patch_artist=True,
        showfliers=True,
        boxprops=dict(facecolor=color, alpha=0.78, edgecolor="black", linewidth=0.5),
        whiskerprops=dict(color="black", linewidth=0.5),
        capprops=dict(color="black", linewidth=0.5),
        medianprops=dict(color="red", linewidth=1.0),
        flierprops=dict(marker=".", markersize=3, alpha=0.4),
    )

ax.axhline(1.0, color="red", linestyle="--", alpha=0.5, linewidth=0.8, zorder=0)
ax.text(n_subj - 0.4, 1.06, "λ=1.0 (baseline)",
        color="red", fontsize=8, alpha=0.7)

legend_handles = [
    Patch(facecolor=COLOR_C,   label="C (LLM-λ)"),
    Patch(facecolor=COLOR_RFL, label="RF-λ"),
    Patch(facecolor="#888888", label="Oracle λ*"),
]
ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

ax.set_xticks(positions)
ax.set_xticklabels([f"subj{l}" for l in SUBJ_LABELS])
ax.set_xlim(-0.5, n_subj - 0.5)
ax.set_ylim(0, 3.2)
ax.set_ylabel("λ value")
ax.set_title("Per-subject λ distributions (post-cold-start) — "
             "RF-λ collapses to ~1.0, LLM spreads, Oracle is the GT-derived target",
             fontsize=11)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
p5 = FIGS_DIR / "fig_lambda_distribution.png"
plt.savefig(p5, dpi=150, bbox_inches="tight")
plt.close()
print(f"[saved] {p5}")


# ===================================================================
# Sensitivity analysis
# ===================================================================
mae_dicts = {
    "A":      dict(zip(SUBJECTS, mae_A)),
    "B":      dict(zip(SUBJECTS, mae_B)),
    "C":      dict(zip(SUBJECTS, mae_C)),
    "RF-λ":   dict(zip(SUBJECTS, mae_RFL)),
    "Oracle": dict(zip(SUBJECTS, mae_ORC)),
}
without_subj10 = [s for s in SUBJECTS if s != "subj10_type02"]


# 1. with vs without subj10
sens_subj10 = {}
for m, d in mae_dicts.items():
    sens_subj10[m] = {
        "with_subj10": float(np.mean(list(d.values()))),
        "without_subj10": float(np.mean([d[s] for s in without_subj10])),
        "subj10_mae": float(d["subj10_type02"]),
        "delta": float(np.mean(list(d.values())) - np.mean([d[s] for s in without_subj10])),
    }


# 2. per-subject headroom utilization (for LLM-C, since C is the focus)
util_C_per_subj = {}
for s in SUBJECTS:
    a = mae_dicts["A"][s]
    c = mae_dicts["C"][s]
    o = mae_dicts["Oracle"][s]
    denom = a - o
    if abs(denom) < 1e-6:
        util_C_per_subj[s] = None
    else:
        util_C_per_subj[s] = float((a - c) / denom * 100)


# Bonus: same for RF-λ
util_RFL_per_subj = {}
for s in SUBJECTS:
    a = mae_dicts["A"][s]
    r = mae_dicts["RF-λ"][s]
    o = mae_dicts["Oracle"][s]
    denom = a - o
    if abs(denom) < 1e-6:
        util_RFL_per_subj[s] = None
    else:
        util_RFL_per_subj[s] = float((a - r) / denom * 100)


# 3. median vs mean MAE
median_vs_mean = {}
for m, d in mae_dicts.items():
    vals = list(d.values())
    median_vs_mean[m] = {
        "mean":   float(np.mean(vals)),
        "median": float(np.median(vals)),
        "mean_minus_median": float(np.mean(vals) - np.median(vals)),
    }


sensitivity = {
    "with_vs_without_subj10": sens_subj10,
    "per_subject_headroom_utilization_percent": {
        "C_vs_oracle":   util_C_per_subj,
        "RFL_vs_oracle": util_RFL_per_subj,
    },
    "median_vs_mean_mae": median_vs_mean,
}
sens_path = RESULTS_DIR / "sensitivity.json"
with open(sens_path, "w") as f:
    json.dump(sensitivity, f, indent=2)

print()
print("=" * 70)
print("Sensitivity analysis")
print("=" * 70)

# 1. with vs without subj10
print()
print("(1) with vs without subj10:")
print(f"  {'method':<8} | {'with':>8} | {'w/o subj10':>11} | {'delta':>8} | "
      f"{'subj10 MAE':>10}")
print(f"  {'-'*8} | {'-'*8} | {'-'*11} | {'-'*8} | {'-'*10}")
for m, d in sens_subj10.items():
    print(f"  {m:<8} | {d['with_subj10']:8.3f} | {d['without_subj10']:11.3f} | "
          f"{d['delta']:+8.3f} | {d['subj10_mae']:10.3f}")

# 2. per-subject util
print()
print("(2) per-subject headroom utilization (C vs Oracle):")
print(f"  {'subject':<14} | {'A':>7} | {'C':>7} | {'Oracle':>7} | "
      f"{'C util %':>9} | {'RF-λ util %':>11}")
print(f"  {'-'*14} | {'-'*7} | {'-'*7} | {'-'*7} | {'-'*9} | {'-'*11}")
for s in SUBJECTS:
    a = mae_dicts["A"][s]
    c = mae_dicts["C"][s]
    o = mae_dicts["Oracle"][s]
    uc = util_C_per_subj[s]
    ur = util_RFL_per_subj[s]
    uc_s = f"{uc:9.1f}" if uc is not None else "       N/A"
    ur_s = f"{ur:11.1f}" if ur is not None else "         N/A"
    print(f"  {s:<14} | {a:7.2f} | {c:7.2f} | {o:7.2f} | {uc_s} | {ur_s}")

# 3. median vs mean
print()
print("(3) median vs mean MAE per method:")
print(f"  {'method':<8} | {'mean':>8} | {'median':>8} | {'mean-median':>12}")
print(f"  {'-'*8} | {'-'*8} | {'-'*8} | {'-'*12}")
for m, d in median_vs_mean.items():
    print(f"  {m:<8} | {d['mean']:8.3f} | {d['median']:8.3f} | "
          f"{d['mean_minus_median']:+12.3f}")

print()
print(f"[saved] {sens_path}")
print()
print("=" * 70)
print("All figures + sensitivity done")
print("=" * 70)
print(f"  Figs:")
print(f"    {p1}")
print(f"    {p2}")
print(f"    {p3}")
print(f"    {p4}")
print(f"    {p5}")
print(f"  Sensitivity JSON: {sens_path}")
