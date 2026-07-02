"""04c_methodC_loso.py — Method C LOSO over 11 subjects.

ECE 284 LLM-PPG project / Method C Step LOSO.

- 跑 11 subject 串行 (跟 Method A / B 同 SUBJECT_TYPES)
- 每 subject 调 run_subject_methodC(N=10, max_jump_bpm=15, energy_threshold=0.5)
- 每 subject 打印 "subjXX_typeXX: MAE=YY BPM, n_fallback=Z, lambda_median=W"
- 跑完打印 overall MAE + 总耗时 + 总 fallback 数
- 输出 results/methodC_loso.json

中断 / 异常处理:
- 任一 subject 抛异常 → 不重试整 subject, 打印 "PARTIAL" 状态 + 写 results/methodC_loso_partial.json
- LLM call 内部 fallback 不算异常 (call_llm 已 handle, 自动用 λ=1.0)
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

from method_c_llm import run_subject_methodC


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "methodC_loso.json"
PARTIAL_PATH = RESULTS_DIR / "methodC_loso_partial.json"


# ===================================================================
# Config (跟 method A / B 一致, 不要中途调)
# ===================================================================
SUBJECT_TYPES = [
    ("01", "01"), ("02", "02"), ("03", "02"), ("04", "01"),
    ("05", "02"), ("06", "02"), ("07", "02"), ("08", "02"),
    ("10", "02"), ("11", "02"), ("12", "02"),
]
MISSING_SUBJECTS = ["09"]

N = 10
MAX_JUMP_BPM = 15
ENERGY_THRESHOLD = 0.5


# ===================================================================
# JSON-safe helpers
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


def lambda_subset_stats(lambdas_used, llm_responses, N_cold):
    """Compute λ stats on (i >= N_cold) ∧ (not None / NaN) ∧ (not fallback)."""
    vals = []
    for i, lam in enumerate(lambdas_used):
        if i < N_cold:
            continue
        if lam is None:
            continue
        if isinstance(lam, float) and np.isnan(lam):
            continue
        resp = llm_responses[i] if i < len(llm_responses) else {}
        if resp and resp.get("fallback_used") is True:
            continue
        vals.append(float(lam))
    if not vals:
        return {"min": None, "max": None, "median": None,
                "mean": None, "std": None, "n": 0}
    arr = np.array(vals)
    return {
        "min": float(arr.min()),
        "max": float(arr.max()),
        "median": float(np.median(arr)),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "n": int(len(vals)),
    }


# ===================================================================
# Main
# ===================================================================
print("=" * 70)
print(f"Method C LOSO — {len(SUBJECT_TYPES)} subjects "
      f"(deepseek-v4-flash, thinking=disabled)")
print(f"params: N={N}  max_jump_bpm={MAX_JUMP_BPM}  "
      f"energy_threshold={ENERGY_THRESHOLD}  temperature=0.3")
print(f"missing_subjects: {MISSING_SUBJECTS}")
print("=" * 70)

t_start = time.perf_counter()
per_subject = {}
per_subject_mae = []
total_n_fallback = 0
current_pair = None
failed_key = None
failure_message = None

try:
    for subj_id, type_id in SUBJECT_TYPES:
        current_pair = (subj_id, type_id)
        key = f"subj{subj_id}_type{type_id}"

        t0 = time.perf_counter()
        result = run_subject_methodC(
            subj_id, type_id=type_id,
            N=N,
            max_jump_bpm=MAX_JUMP_BPM,
            energy_threshold=ENERGY_THRESHOLD,
        )
        t1 = time.perf_counter()

        lam_stats = lambda_subset_stats(
            result["lambdas_used"], result["llm_responses"], N
        )
        median_str = (f"{lam_stats['median']:.3f}"
                      if lam_stats["median"] is not None else "N/A")

        print(f"{key}: MAE={result['mae']:.3f} BPM, "
              f"n_fallback={result['n_fallback']}, "
              f"lambda_median={median_str}  "
              f"({t1 - t0:.1f}s, n_windows={result['n_windows']})")

        per_subject[key] = {
            "mae": float(result["mae"]),
            "type_id": type_id,
            "hr_estimates": result["hr_estimates"],
            "hr_truths": result["hr_truths"],
            "lambdas_used": result["lambdas_used"],
            "n_windows": int(result["n_windows"]),
            "n_nan": int(result["n_nan"]),
            "n_fallback": int(result["n_fallback"]),
            "lambda_stats": lam_stats,
            "llm_reasonings": [
                ((r or {}).get("reasoning", "")) for r in result["llm_responses"]
            ],
        }
        per_subject_mae.append(float(result["mae"]))
        total_n_fallback += int(result["n_fallback"])

except KeyboardInterrupt:
    failed_key = (f"subj{current_pair[0]}_type{current_pair[1]}"
                  if current_pair else "before_loop")
    failure_message = "KeyboardInterrupt"
    print()
    print("!" * 70)
    print(f"[INTERRUPT] at {failed_key}; completed "
          f"{len(per_subject)}/{len(SUBJECT_TYPES)} subjects")
    print("!" * 70)
except Exception as e:
    failed_key = (f"subj{current_pair[0]}_type{current_pair[1]}"
                  if current_pair else "before_loop")
    failure_message = f"{type(e).__name__}: {e}"
    print()
    print("!" * 70)
    print(f"[ERROR] {failed_key}: {failure_message}")
    print(f"completed {len(per_subject)}/{len(SUBJECT_TYPES)} subjects before failure")
    print("!" * 70)

t_end = time.perf_counter()
total_sec = t_end - t_start

overall_mae = (float(np.mean(per_subject_mae))
               if per_subject_mae else None)

result_dict = {
    "overall_mae": overall_mae,
    "n_subjects": len(SUBJECT_TYPES),
    "n_completed_subjects": len(per_subject),
    "missing_subjects": MISSING_SUBJECTS,
    "method": "MethodC_DeepSeek",
    "model": "deepseek-v4-flash",
    "params": {
        "N": N,
        "max_jump_bpm": MAX_JUMP_BPM,
        "energy_threshold": ENERGY_THRESHOLD,
        "thinking": "disabled",
        "temperature": 0.3,
    },
    "total_n_fallback": total_n_fallback,
    "total_time_sec": total_sec,
    "per_subject": per_subject,
}

if failed_key is not None:
    result_dict["status"] = "partial"
    result_dict["failed_subject"] = failed_key
    result_dict["failure_message"] = failure_message
    write_path = PARTIAL_PATH
else:
    result_dict["status"] = "complete"
    write_path = RESULTS_PATH

safe = make_json_safe(result_dict)
with open(write_path, "w") as f:
    json.dump(safe, f, indent=2)

print()
print("=" * 70)
if failed_key is None:
    print(f"overall MAE ({len(SUBJECT_TYPES)} subjects): "
          f"{overall_mae:.3f} BPM")
else:
    print(f"PARTIAL: completed {len(per_subject)}/{len(SUBJECT_TYPES)} subjects")
    if overall_mae is not None:
        print(f"partial-overall MAE (over {len(per_subject)} completed): "
              f"{overall_mae:.3f} BPM")
print(f"total fallback count: {total_n_fallback}")
print(f"total time: {total_sec:.1f} s ({total_sec/60:.1f} min)")
print(f"results: {write_path}")
print("=" * 70)

if failed_key is not None:
    sys.exit(1)
