"""04_rf_loso.py — Method B Random Forest LOSO over 11 subjects.

ECE 284 LLM-PPG project / Method B Step B.
- 调 rf_baseline.run_loso()  (内部已 print 每个 subject MAE)
- 输出 results/rf_loso.json  (跟 troika_loso.json 同 schema + method/n_features/model_params)
- numpy scalar / np.nan → Python 原生 / None
- 最后打印 overall MAE + 总耗时
"""

import json
import time
from pathlib import Path

import numpy as np

from rf_baseline import run_loso


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)
RESULTS_PATH = RESULTS_DIR / "rf_loso.json"


def to_json_safe_scalar(x):
    """单个 scalar → JSON-safe."""
    if isinstance(x, float):
        return None if np.isnan(x) else x
    if isinstance(x, np.floating):
        v = float(x)
        return None if np.isnan(v) else v
    if isinstance(x, np.integer):
        return int(x)
    return x


def make_json_safe(obj):
    """Recursively convert numpy scalars / np.nan inside dict/list."""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_safe(x) for x in obj]
    return to_json_safe_scalar(obj)


print("=" * 70)
print("Method B — Random Forest LOSO  (n_estimators=100, random_state=42)")
print("=" * 70)

t_start = time.perf_counter()
result = run_loso()
t_end = time.perf_counter()
total_sec = t_end - t_start

result_safe = make_json_safe(result)

with open(RESULTS_PATH, "w") as f:
    json.dump(result_safe, f, indent=2)

print()
print("=" * 70)
print(f"overall MAE (mean across {result['n_subjects']} subjects): "
      f"{result['overall_mae']:.3f} BPM")
print(f"total time: {total_sec:.2f} s")
print(f"results: {RESULTS_PATH}")
print("=" * 70)
