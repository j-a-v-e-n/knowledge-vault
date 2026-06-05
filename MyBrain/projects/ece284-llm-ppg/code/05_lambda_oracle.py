"""05_lambda_oracle.py — Oracle λ* per-window analysis WITH tracking.

Oracle v2: 跟 method A / C 完全相同的 tracking + cold start + self-correction,
唯一区别是非 cold-start 窗用 oracle (扫 grid 选误差最小 λ) 而不是 LLM / fixed.

修复 v1 的两个问题:
  1) v1 关了 tracking → 比 method C 还差 5 个 subject, 不是有效上限.
     现在 v2 保留 tracking, 严格 ≥ method C (因为 oracle 知道 truth, 同一架构).
  2) v1 tie 选 grid 第一个 (0.1) → λ* 分布偏向 0.1, 不真实.
     现在 v2 tie 时选 |λ - 1.0| 最小, 反映 "需要偏离 1.0 多少" 这个语义.

Params (跟 method A/C LOSO 一致): N=10, max_jump_bpm=15, energy_threshold=0.5.

Cold-start window (i<N): λ=1.0, 直接调 estimate_hr_one_window(cold_start_active=True),
不扫 grid (跟 method C 一致).

Non-cold-start window: 扫 λ ∈ np.arange(0.1, 3.01, 0.1), 每个 λ 调
estimate_hr_one_window(...) 拿 HR. 选 error 最小, tie → |λ - 1.0| 最小.

prev_hr 用选中 λ 的 HR 更新 (序列依赖).
"""

import json
import time
from pathlib import Path

import numpy as np

from data import load_subject
from troika_lite import (
    FS,
    WINDOW_SAMPLES,
    SHIFT_SAMPLES,
    estimate_hr_one_window,
)


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "lambda_oracle_loso.json"


LAMBDA_GRID = np.round(np.arange(0.1, 3.01, 0.1), 2)
TIE_EPS = 1e-9

# Method A/C LOSO 参数 (固定, 不调)
N_COLD_START = 10
MAX_JUMP_BPM = 15
ENERGY_THRESHOLD = 0.5

SUBJECT_TYPES = [
    ("01", "01"), ("02", "02"), ("03", "02"), ("04", "01"),
    ("05", "02"), ("06", "02"), ("07", "02"), ("08", "02"),
    ("10", "02"), ("11", "02"), ("12", "02"),
]
MISSING_SUBJECTS = ["09"]


# ===================================================================
# Per-window oracle (non-cold-start, tracking on)
# ===================================================================
def oracle_one_window_with_tracking(ppg_window, accel_xyz_window, hr_truth,
                                     prev_hr, max_jump_bpm, energy_threshold):
    """扫 λ grid; tracking ON; pick (smallest err, then closest λ to 1.0).

    Returns (best_lam, best_hr). NaN if no λ produces a valid HR.
    """
    best_err = np.inf
    best_lam = np.nan
    best_hr = np.nan

    for lam in LAMBDA_GRID:
        lam_f = float(lam)
        hr, _ = estimate_hr_one_window(
            ppg_window, accel_xyz_window, fs=FS, lam=lam_f,
            prev_hr=prev_hr,
            max_jump_bpm=max_jump_bpm,
            cold_start_active=False,
            energy_threshold=energy_threshold,
        )
        if np.isnan(hr):
            continue
        err = abs(hr - hr_truth)

        if err < best_err - TIE_EPS:
            # 严格更优
            best_err = err
            best_lam = lam_f
            best_hr = hr
        elif abs(err - best_err) < TIE_EPS:
            # tie → 比 |λ - 1.0|
            if np.isnan(best_lam) or abs(lam_f - 1.0) < abs(best_lam - 1.0):
                best_lam = lam_f
                best_hr = hr

    if np.isnan(best_lam):
        return np.nan, np.nan
    return best_lam, best_hr


# ===================================================================
# Subject-level driver
# ===================================================================
def oracle_run_subject(subj_id, type_id, N=10, max_jump_bpm=15,
                       energy_threshold=0.5):
    sig, bpm0 = load_subject(subj_id, type_id)
    W = len(bpm0)

    oracle_lambdas = []
    hr_estimates = []
    prev_hr = None

    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            oracle_lambdas.append(np.nan)
            hr_estimates.append(np.nan)
            continue                              # 越界 → 不更新 prev_hr

        if i < N:
            # Cold start: λ=1.0, cold_start_active=True (跟 method A/C 一致)
            hr, _ = estimate_hr_one_window(
                sig[1, start:end], sig[3:6, start:end],
                fs=FS, lam=1.0,
                prev_hr=prev_hr,
                max_jump_bpm=max_jump_bpm,
                cold_start_active=True,
                energy_threshold=energy_threshold,
            )
            lam = 1.0
        else:
            hr_truth = float(bpm0[i])
            lam, hr = oracle_one_window_with_tracking(
                sig[1, start:end], sig[3:6, start:end],
                hr_truth, prev_hr, max_jump_bpm, energy_threshold,
            )

        oracle_lambdas.append(lam)
        hr_estimates.append(hr)

        # 用选中 λ 的 HR 更新 prev_hr (序列依赖)
        if not np.isnan(hr):
            prev_hr = hr

    hr_truths = bpm0[:W].tolist()
    hr_est_arr = np.array(hr_estimates, dtype=float)
    hr_truth_arr = np.array(hr_truths, dtype=float)

    mae = float(np.nanmean(np.abs(hr_est_arr - hr_truth_arr)))
    n_nan = int(sum(1 for h in hr_estimates if np.isnan(h)))

    return {
        "mae": mae,
        "oracle_lambdas": oracle_lambdas,
        "hr_estimates": hr_estimates,
        "hr_truths": hr_truths,
        "n_windows": int(W),
        "n_nan": n_nan,
    }


# ===================================================================
# JSON helpers
# ===================================================================
def to_json_safe_scalar(x):
    if isinstance(x, float):
        return None if np.isnan(x) else x
    if isinstance(x, np.floating):
        v = float(x)
        return None if np.isnan(v) else v
    if isinstance(x, np.integer):
        return int(x)
    return x


def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    if isinstance(obj, tuple):
        return [make_json_safe(x) for x in obj]
    return to_json_safe_scalar(obj)


def lambda_stats_of(values):
    """Stats over non-None / non-NaN λs."""
    vals = np.array([float(x) for x in values if x is not None
                     and not (isinstance(x, float) and np.isnan(x))])
    if len(vals) == 0:
        return {"min": None, "max": None, "median": None,
                "mean": None, "std": None, "n": 0}
    return {
        "min": float(vals.min()),
        "max": float(vals.max()),
        "median": float(np.median(vals)),
        "mean": float(vals.mean()),
        "std": float(vals.std()),
        "n": int(len(vals)),
    }


# ===================================================================
# Main
# ===================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(f"Oracle λ* LOSO v2 — {len(SUBJECT_TYPES)} subjects, "
          f"tracking ON (N={N_COLD_START}, J={MAX_JUMP_BPM}, T={ENERGY_THRESHOLD})")
    print(f"λ grid: {[float(x) for x in LAMBDA_GRID]}  "
          f"({len(LAMBDA_GRID)} values)")
    print(f"tie-break: closest λ to 1.0 (eps={TIE_EPS})")
    print("=" * 70)

    t_start = time.perf_counter()
    per_subject = {}
    per_subject_mae = []
    all_oracle_lambdas_noncold = []      # 全局 stats 排除 cold-start

    for subj_id, type_id in SUBJECT_TYPES:
        t0 = time.perf_counter()
        result = oracle_run_subject(
            subj_id, type_id,
            N=N_COLD_START,
            max_jump_bpm=MAX_JUMP_BPM,
            energy_threshold=ENERGY_THRESHOLD,
        )
        t1 = time.perf_counter()

        # Stats 仅在 i >= N (非 cold-start) 的窗上
        post_cold = result["oracle_lambdas"][N_COLD_START:]
        ls = lambda_stats_of(post_cold)
        med_str = f"{ls['median']:.2f}" if ls["median"] is not None else "N/A"

        key = f"subj{subj_id}_type{type_id}"
        print(f"{key}: MAE={result['mae']:.3f} BPM, n_nan={result['n_nan']}, "
              f"λ*_median(post-cold)={med_str}  "
              f"({t1 - t0:.2f}s, n_windows={result['n_windows']})")

        per_subject[key] = {
            "mae": float(result["mae"]),
            "type_id": type_id,
            "oracle_lambdas": result["oracle_lambdas"],
            "hr_estimates": result["hr_estimates"],
            "hr_truths": result["hr_truths"],
            "n_windows": int(result["n_windows"]),
            "n_nan": int(result["n_nan"]),
            "oracle_lambda_stats": ls,        # post-cold-start only
        }
        per_subject_mae.append(float(result["mae"]))
        for lam in post_cold:
            if lam is not None and not (isinstance(lam, float) and np.isnan(lam)):
                all_oracle_lambdas_noncold.append(float(lam))

    t_end = time.perf_counter()
    total_sec = t_end - t_start

    overall_mae = float(np.mean(per_subject_mae))
    global_stats = lambda_stats_of(all_oracle_lambdas_noncold)

    output = {
        "overall_mae": overall_mae,
        "n_subjects": len(SUBJECT_TYPES),
        "missing_subjects": MISSING_SUBJECTS,
        "method": "OracleLambda_withTracking",
        "lambda_grid": [float(x) for x in LAMBDA_GRID],
        "tie_break_rule": "closest_to_1.0",
        "params": {
            "N": N_COLD_START,
            "max_jump_bpm": MAX_JUMP_BPM,
            "energy_threshold": ENERGY_THRESHOLD,
        },
        "overall_lambda_stats": global_stats,    # post-cold-start aggregated
        "total_time_sec": total_sec,
        "per_subject": per_subject,
    }
    safe = make_json_safe(output)
    with open(RESULTS_PATH, "w") as f:
        json.dump(safe, f, indent=2)

    print()
    print(f"Global oracle λ* distribution (post-cold-start, n={global_stats['n']}):")
    print(f"  min:    {global_stats['min']:.3f}")
    print(f"  max:    {global_stats['max']:.3f}")
    print(f"  median: {global_stats['median']:.3f}")
    print(f"  mean:   {global_stats['mean']:.3f}")
    print(f"  std:    {global_stats['std']:.3f}")

    print()
    print("=" * 70)
    print(f"overall oracle MAE ({len(SUBJECT_TYPES)} subjects): {overall_mae:.3f} BPM")
    print(f"total time: {total_sec:.2f} s")
    print(f"results: {RESULTS_PATH}")
    print("=" * 70)
