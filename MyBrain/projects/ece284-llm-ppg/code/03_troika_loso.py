"""03_troika_loso.py — TROIKA-lite over 11 available subjects on Udacity mirror.

ECE 284 LLM-PPG project / Step C.

Udacity 镜像里 subject × type 文件不完整:
  - subject 01 / 04 → TYPE01
  - subject 02 / 03 / 05 / 06 / 07 / 08 / 10 / 11 / 12 → TYPE02
  - subject 09 → 完全缺失，跳过
所以 LOSO 实际跑 11 个 (subj_id, type_id) 组合.

输出 results/troika_loso.json:
  {
    "overall_mae": float,
    "n_subjects": 11,
    "missing_subjects": ["09"],
    "per_subject": {
      "subjXX_typeXX": {mae, type_id, hr_estimates, hr_truths, n_windows, n_nan},
      ...
    }
  }

np.nan → None 序列化为 JSON null. numpy scalar → 原生 Python float / int.
"""

import json
import time
from pathlib import Path

import numpy as np

from troika_lite import (
    COLD_START_N,
    ENERGY_THRESHOLD,
    MAX_JUMP_BPM,
    run_subject,
)


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "troika_loso.json"


# subject 09 缺失; 其他 subject 按实际可用 type_id 分配
SUBJECT_TYPES = [
    ("01", "01"),
    ("02", "02"),
    ("03", "02"),
    ("04", "01"),
    ("05", "02"),
    ("06", "02"),
    ("07", "02"),
    ("08", "02"),
    ("10", "02"),
    ("11", "02"),
    ("12", "02"),
]
MISSING_SUBJECTS = ["09"]
LAM = 1.0

# 显式 override module-level tracking params 以保持跟 method C / RF-λ / Oracle 一致
# (method C / 05 / 07 都用 J=15, 这里之前用 module default J=20 → 破坏 controlled comparison)
MAX_JUMP_BPM_EXPLICIT = 15
ENERGY_THRESHOLD_EXPLICIT = 0.5
COLD_START_N_EXPLICIT = 10


def to_json_safe(x):
    """numpy scalar / np.nan → native Python (float/int) / None."""
    if isinstance(x, float):
        return None if np.isnan(x) else x
    if isinstance(x, np.floating):
        v = float(x)
        return None if np.isnan(v) else v
    if isinstance(x, np.integer):
        return int(x)
    return x


print("=" * 70)
print("TROIKA-lite LOSO — 11 subjects (Udacity mirror, type per availability)")
print(f"params (EXPLICIT, override module defaults to align with method C / RF-λ / Oracle):")
print(f"  COLD_START_N={COLD_START_N_EXPLICIT}  "
      f"ENERGY_THRESHOLD={ENERGY_THRESHOLD_EXPLICIT}  "
      f"MAX_JUMP_BPM={MAX_JUMP_BPM_EXPLICIT}  lam={LAM}")
print(f"  (module defaults were: N={COLD_START_N} T={ENERGY_THRESHOLD} J={MAX_JUMP_BPM})")
print(f"missing_subjects: {MISSING_SUBJECTS}")
print("=" * 70)

t_start = time.perf_counter()
per_subject = {}
per_subject_mae = []

for subj, type_id in SUBJECT_TYPES:
    t0 = time.perf_counter()
    res = run_subject(
        subj, type_id=type_id, lam=LAM,
        max_jump_bpm=MAX_JUMP_BPM_EXPLICIT,
        energy_threshold=ENERGY_THRESHOLD_EXPLICIT,
        cold_start_n=COLD_START_N_EXPLICIT,
    )
    t1 = time.perf_counter()

    key = f"subj{subj}_type{type_id}"
    print(f"{key}: MAE={res['mae']:.3f} BPM, n_nan={res['n_nan']}  "
          f"({t1 - t0:.2f}s, n_windows={res['n_windows']})")

    hr_estimates_safe = [to_json_safe(x) for x in res["hr_estimates"]]
    hr_truths_safe = [to_json_safe(x) for x in res["hr_truths"]]

    per_subject[key] = {
        "mae": float(res["mae"]),
        "type_id": type_id,
        "hr_estimates": hr_estimates_safe,
        "hr_truths": hr_truths_safe,
        "n_windows": int(res["n_windows"]),
        "n_nan": int(res["n_nan"]),
    }
    per_subject_mae.append(float(res["mae"]))

t_end = time.perf_counter()
total_sec = t_end - t_start

overall_mae = float(np.mean(per_subject_mae))

result_dict = {
    "overall_mae": overall_mae,
    "n_subjects": len(SUBJECT_TYPES),
    "missing_subjects": MISSING_SUBJECTS,
    "method": "TROIKA_lite",
    "params": {
        "N": COLD_START_N_EXPLICIT,
        "max_jump_bpm": MAX_JUMP_BPM_EXPLICIT,
        "energy_threshold": ENERGY_THRESHOLD_EXPLICIT,
        "lam": LAM,
    },
    "per_subject": per_subject,
}

with open(RESULTS_PATH, "w") as f:
    json.dump(result_dict, f, indent=2)

print()
print("=" * 70)
print(f"overall MAE (mean across {len(SUBJECT_TYPES)} subjects): "
      f"{overall_mae:.3f} BPM")
print(f"total time: {total_sec:.2f} s")
print(f"results: {RESULTS_PATH}")
print("=" * 70)
