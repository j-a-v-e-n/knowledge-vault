"""04b_methodC_pilot.py — Method C pilot on subject 01 TYPE01.

调 run_subject_methodC(), 报告:
  - MAE / n_nan / n_fallback
  - λ 分布 (min/max/median/std)  — 看 LLM 给的 λ 是否退化成固定值
  - 前 5 个非 cold-start 窗 (i=10..14) 的 (HR_est, HR_truth, λ, reasoning)
  - 写 results/methodC_pilot_subj01.json
"""

import json
import time
from pathlib import Path

import numpy as np

from method_c_llm import run_subject_methodC


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "methodC_pilot_subj01.json"


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


SUBJ_ID = "01"
TYPE_ID = "01"
N = 10
MAX_JUMP_BPM = 15
ENERGY_THRESHOLD = 0.5

print("=" * 70)
print(f"Method C pilot — subj{SUBJ_ID} TYPE{TYPE_ID}")
print(f"params: N={N}  max_jump_bpm={MAX_JUMP_BPM}  "
      f"energy_threshold={ENERGY_THRESHOLD}")
print(f"model: deepseek-v4-flash  temperature=0.3  thinking=disabled")
print("=" * 70)

t0 = time.perf_counter()
result = run_subject_methodC(
    SUBJ_ID, type_id=TYPE_ID, N=N,
    max_jump_bpm=MAX_JUMP_BPM,
    energy_threshold=ENERGY_THRESHOLD,
)
t1 = time.perf_counter()
elapsed = t1 - t0

# ---- Summary ----
print()
print(f"MAE:        {result['mae']:.3f} BPM")
print(f"n_windows:  {result['n_windows']}")
print(f"n_nan:      {result['n_nan']}")
print(f"n_fallback: {result['n_fallback']}")
print(f"elapsed:    {elapsed:.2f} s  "
      f"({elapsed / max(result['n_windows'] - N, 1):.2f}s per LLM-call window)")

# ---- λ distribution (排除 None / NaN) ----
lam_arr = np.array([
    float(l) for l in result["lambdas_used"]
    if l is not None and not (isinstance(l, float) and np.isnan(l))
])
print()
print(f"λ distribution (n={len(lam_arr)} non-null windows):")
if len(lam_arr) > 0:
    print(f"  min:    {lam_arr.min():.3f}")
    print(f"  max:    {lam_arr.max():.3f}")
    print(f"  median: {float(np.median(lam_arr)):.3f}")
    print(f"  std:    {lam_arr.std():.3f}")
    # 看是否退化成固定 1.0
    n_eq_1 = int(np.sum(lam_arr == 1.0))
    n_non_cold = result["n_windows"] - N
    print(f"  λ == 1.0 exact count:  {n_eq_1} / {len(lam_arr)}  "
          f"(cold start contributes {N})")
else:
    print("  (no valid λ values)")

# ---- 前 5 个非 cold-start 窗 (i=10..14) ----
print()
print("First 5 non-cold-start windows (i=10..14):")
print(f"  {'i':>3}  {'HR_est':>8}  {'HR_truth':>9}  {'λ':>6}  {'fb':>3}  reasoning")
print(f"  {'-'*3}  {'-'*8}  {'-'*9}  {'-'*6}  {'-'*3}  {'-'*60}")
for i in range(N, min(N + 5, len(result["hr_estimates"]))):
    hr_e = result["hr_estimates"][i]
    hr_t = result["hr_truths"][i]
    lam = result["lambdas_used"][i]
    resp = result["llm_responses"][i] if i < len(result["llm_responses"]) else {}
    fb = "Y" if resp.get("fallback_used") else "N"
    reason = resp.get("reasoning", "")
    # Truncate long reasoning for table layout
    reason_short = reason if len(reason) <= 80 else reason[:77] + "..."
    hr_e_str = f"{hr_e:>8.2f}" if not (isinstance(hr_e, float) and np.isnan(hr_e)) else "     NaN"
    lam_str = f"{lam:>6.3f}" if lam is not None and not (isinstance(lam, float) and np.isnan(lam)) else "   N/A"
    print(f"  {i:>3}  {hr_e_str}  {hr_t:>9.2f}  {lam_str}  {fb:>3}  {reason_short}")

# ---- Write JSON ----
output = {
    "subject_id": SUBJ_ID,
    "type_id": TYPE_ID,
    "method": "LLM_lambda_DeepSeek_v4_flash",
    "params": {
        "N": N,
        "max_jump_bpm": MAX_JUMP_BPM,
        "energy_threshold": ENERGY_THRESHOLD,
        "model": "deepseek-v4-flash",
        "temperature": 0.3,
        "max_tokens": 200,
        "thinking_disabled": True,
    },
    "elapsed_sec": elapsed,
    **result,
}
output_safe = make_json_safe(output)
with open(RESULTS_PATH, "w") as f:
    json.dump(output_safe, f, indent=2)

print()
print("=" * 70)
print(f"results: {RESULTS_PATH}")
print("=" * 70)
