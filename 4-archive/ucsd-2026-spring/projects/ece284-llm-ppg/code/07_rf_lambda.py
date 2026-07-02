"""07_rf_lambda.py — Method B-lambda: RF predicts λ instead of HR.

回答 "用 RF 预测 λ 能不能比 LLM 更好" — 答辩关键 baseline.

Pipeline:
  1. 训练: 对每个 held-out subject (LOSO), 用其他 10 subject 的
     (11 features, oracle λ*) 训练 RandomForestRegressor.
       - features 复用 rf_baseline.extract_features (跟 method B 完全一致)
       - 标签 = oracle λ*  (从 results/lambda_oracle_loso.json 读)
       - 仅训 i >= N 的非 cold-start 窗 (cold start 窗 oracle 强制 λ=1.0, 无意义)
       - RF params: n_estimators=100, random_state=42 (跟 method B 一致, 不调超参)
  2. 预测: held-out subject 每非-cold-start 窗 → RF 预测 λ → clamp [0.1, 3.0].
  3. Pipeline: 把预测的 λ 喂给 estimate_hr_one_window (跟 method A/C 同 tracking +
     cold start + self-correction, N=10/J=15/T=0.5).
       - cold start (i<N): λ=1.0, cold_start_active=True (不用 RF 预测)
       - 非 cold start:     λ=RF.predict, cold_start_active=False

控制对照: 跟 A/C 完全同 pipeline, 唯一变量是 λ 来源.
  - A: λ=1.0 固定
  - C: λ=LLM 输出
  - B-λ: λ=RF 预测
  - Oracle: λ=GT 反推 (理论上限)
"""

import json
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from data import load_subject
from troika_lite import (
    FS,
    WINDOW_SAMPLES,
    SHIFT_SAMPLES,
    estimate_hr_one_window,
)
from rf_baseline import extract_features, N_FEATURES


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
ORACLE_JSON_PATH = RESULTS_DIR / "lambda_oracle_loso.json"
OUT_PATH = RESULTS_DIR / "rf_lambda_loso.json"


SUBJECT_TYPES = [
    ("01", "01"), ("02", "02"), ("03", "02"), ("04", "01"),
    ("05", "02"), ("06", "02"), ("07", "02"), ("08", "02"),
    ("10", "02"), ("11", "02"), ("12", "02"),
]
MISSING_SUBJECTS = ["09"]

# Pipeline params (跟 A/C LOSO 一致)
N_COLD_START = 10
MAX_JUMP_BPM = 15
ENERGY_THRESHOLD = 0.5

# RF params (跟 method B 一致)
RF_N_ESTIMATORS = 100
RF_RANDOM_STATE = 42

LAM_MIN = 0.1
LAM_MAX = 3.0


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
# Step 1: 读 oracle λ + 预提取 11 subject 的 (features, oracle, valid_indices)
# ===================================================================
print("=" * 70)
print("Step 1: load oracle λ* + extract 11 features per (subj, window)")
print("=" * 70)

oracle_data = json.load(open(ORACLE_JSON_PATH))
all_features = {}        # subj_key → np.ndarray (W_valid, 11)
all_valid_orig_idx = {}  # subj_key → list[orig_window_idx]
all_oracle = {}          # subj_key → list[oracle λ over orig idx] (None for OOR)

for subj, ty in SUBJECT_TYPES:
    key = f"subj{subj}_type{ty}"
    sig, bpm0 = load_subject(subj, ty)
    W = len(bpm0)

    feats_list = []
    valid_idx = []
    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            continue
        f = extract_features(sig[1, start:end], sig[3:6, start:end], fs=FS)
        feats_list.append(f)
        valid_idx.append(i)
    all_features[key] = (np.array(feats_list, dtype=np.float64)
                         if feats_list else np.empty((0, N_FEATURES)))
    all_valid_orig_idx[key] = valid_idx
    all_oracle[key] = oracle_data["per_subject"][key]["oracle_lambdas"]

    print(f"  {key}: {len(valid_idx)} valid windows, "
          f"oracle λ list length {len(all_oracle[key])}")


# ===================================================================
# Step 2: LOSO — train RF on other 10 subj's (features, oracle λ*) → predict
#         → run method A pipeline with predicted λ
# ===================================================================
def build_train_set(train_keys):
    """Build (X, y) from non-cold-start, non-OOR windows of given subjects.

    y = oracle λ* per window.
    """
    X_list, y_list = [], []
    for key in train_keys:
        feats = all_features[key]
        valid_idx = all_valid_orig_idx[key]
        oracle_list = all_oracle[key]
        for j, orig_i in enumerate(valid_idx):
            if orig_i < N_COLD_START:
                continue                          # cold start, oracle forced 1.0
            ora = oracle_list[orig_i]
            if ora is None:
                continue
            if isinstance(ora, float) and np.isnan(ora):
                continue
            X_list.append(feats[j])
            y_list.append(float(ora))
    if not X_list:
        return np.empty((0, N_FEATURES)), np.empty((0,))
    return np.array(X_list, dtype=np.float64), np.array(y_list, dtype=np.float64)


print()
print("=" * 70)
print("Step 2: LOSO train+predict+pipeline")
print("=" * 70)

t_start = time.perf_counter()
per_subject = {}
per_subject_mae = []

for held_idx, (subj, ty) in enumerate(SUBJECT_TYPES):
    t0 = time.perf_counter()
    held_key = f"subj{subj}_type{ty}"
    train_keys = [f"subj{s}_type{t}" for s, t in SUBJECT_TYPES if (s, t) != (subj, ty)]

    # Train RF on other 10 subjects
    train_X, train_y = build_train_set(train_keys)
    rf = RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        random_state=RF_RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(train_X, train_y)

    # Predict on held-out subject's non-cold-start windows
    held_feats = all_features[held_key]
    held_valid = all_valid_orig_idx[held_key]
    test_X_list = []
    test_orig_indices = []
    for j, orig_i in enumerate(held_valid):
        if orig_i < N_COLD_START:
            continue
        test_X_list.append(held_feats[j])
        test_orig_indices.append(orig_i)
    if test_X_list:
        test_X = np.array(test_X_list, dtype=np.float64)
        preds = rf.predict(test_X)
        preds = np.clip(preds, LAM_MIN, LAM_MAX)
    else:
        preds = np.array([])
    pred_map = dict(zip(test_orig_indices, preds.tolist()))

    # Run method A pipeline with predicted λ
    sig, bpm0 = load_subject(subj, ty)
    W = len(bpm0)

    hr_estimates = []
    predicted_lambdas = []          # 长度 = W; OOR=NaN, cold start=1.0, else=RF pred
    prev_hr = None

    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            hr_estimates.append(np.nan)
            predicted_lambdas.append(np.nan)
            continue

        if i < N_COLD_START:
            lam = 1.0
            cold_start_active = True
        else:
            lam = float(pred_map[i])
            cold_start_active = False

        predicted_lambdas.append(lam)
        hr, _ = estimate_hr_one_window(
            sig[1, start:end],
            sig[3:6, start:end],
            fs=FS, lam=lam,
            prev_hr=prev_hr,
            max_jump_bpm=MAX_JUMP_BPM,
            cold_start_active=cold_start_active,
            energy_threshold=ENERGY_THRESHOLD,
        )
        hr_estimates.append(hr)
        if not np.isnan(hr):
            prev_hr = hr

    hr_truths = bpm0[:W].tolist()
    hr_est_arr = np.array(hr_estimates, dtype=float)
    hr_truth_arr = np.array(hr_truths, dtype=float)

    mae = float(np.nanmean(np.abs(hr_est_arr - hr_truth_arr)))
    n_nan = int(sum(1 for h in hr_estimates if np.isnan(h)))

    # λ stats only over actual RF predictions (i.e. exclude cold start forced 1.0)
    post_cold = predicted_lambdas[N_COLD_START:]
    lam_stats = lambda_stats_of(post_cold)

    t1 = time.perf_counter()
    med_str = f"{lam_stats['median']:.3f}" if lam_stats["median"] is not None else "N/A"
    print(f"{held_key}: MAE={mae:.3f} BPM, n_nan={n_nan}, "
          f"λ_median(post-cold)={med_str}  "
          f"(train n={len(train_y)}, test n={len(preds)}, {t1 - t0:.2f}s)")

    per_subject[held_key] = {
        "mae": mae,
        "type_id": ty,
        "hr_estimates": hr_estimates,
        "hr_truths": hr_truths,
        "predicted_lambdas": predicted_lambdas,
        "n_windows": int(W),
        "n_nan": n_nan,
        "lambda_stats": lam_stats,
    }
    per_subject_mae.append(mae)

t_end = time.perf_counter()
total_sec = t_end - t_start

overall_mae = float(np.mean(per_subject_mae))


# ===================================================================
# Step 3: global λ stats (post-cold-start aggregated)
# ===================================================================
all_post_cold_lams = []
for key, sd in per_subject.items():
    for lam in sd["predicted_lambdas"][N_COLD_START:]:
        if lam is not None and not (isinstance(lam, float) and np.isnan(lam)):
            all_post_cold_lams.append(float(lam))
global_stats = lambda_stats_of(all_post_cold_lams)


# ===================================================================
# Step 4: write JSON
# ===================================================================
output = {
    "overall_mae": overall_mae,
    "n_subjects": len(SUBJECT_TYPES),
    "missing_subjects": MISSING_SUBJECTS,
    "method": "RF_lambda",
    "label_source": "oracle_lambda_star",
    "oracle_source_file": str(ORACLE_JSON_PATH.name),
    "params": {
        "n_estimators": RF_N_ESTIMATORS,
        "random_state": RF_RANDOM_STATE,
        "N": N_COLD_START,
        "max_jump_bpm": MAX_JUMP_BPM,
        "energy_threshold": ENERGY_THRESHOLD,
    },
    "overall_lambda_stats": global_stats,
    "total_time_sec": total_sec,
    "per_subject": per_subject,
}
safe = make_json_safe(output)
with open(OUT_PATH, "w") as f:
    json.dump(safe, f, indent=2)

print()
print(f"Global RF-λ predicted distribution (post-cold-start, n={global_stats['n']}):")
print(f"  min:    {global_stats['min']:.3f}")
print(f"  max:    {global_stats['max']:.3f}")
print(f"  median: {global_stats['median']:.3f}")
print(f"  mean:   {global_stats['mean']:.3f}")
print(f"  std:    {global_stats['std']:.3f}")

print()
print("=" * 70)
print(f"overall RF-λ MAE ({len(SUBJECT_TYPES)} subjects): {overall_mae:.3f} BPM")
print(f"total time: {total_sec:.2f} s")
print(f"results: {OUT_PATH}")
print("=" * 70)
