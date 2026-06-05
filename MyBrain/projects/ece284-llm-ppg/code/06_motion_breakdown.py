"""06_motion_breakdown.py — Per-motion-level MAE breakdown for methods A / B / C.

Pure data re-organization: no re-runs, no LLM calls, no model retraining.

Steps:
  1) Recompute accel magnitude variance per window for each (subject, window)
     across 11 subjects (matches Method C's accel_intensity feature:
     accel_mag = sqrt(X²+Y²+Z²), intensity = var(accel_mag), no bandpass).
  2) Global tertile thresholds (33.33% / 66.67% percentiles) over all
     non-out-of-range windows → low / med / high motion groups.
  3) Align (subject, window_index) across A / B / C:
     - Method A / C: hr_estimates length = full bpm0 length (NaN for OOR)
     - Method B: hr_estimates length = valid windows only (OOR skipped)
       → map B's dense index back to original window index via per-subject
       "valid mask" recomputed from data shape.
  4) Take intersection of windows where ALL three methods have a valid
     (non-None / non-NaN) estimate.
  5) For each (method, motion_group), MAE = mean(|est - truth|) over
     intersection-restricted set.

Output: results/motion_breakdown.json
"""

import json
from pathlib import Path

import numpy as np

from data import load_subject
from troika_lite import FS, WINDOW_SAMPLES, SHIFT_SAMPLES


SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
OUT_PATH = RESULTS_DIR / "motion_breakdown.json"


SUBJECT_TYPES = [
    ("01", "01"), ("02", "02"), ("03", "02"), ("04", "01"),
    ("05", "02"), ("06", "02"), ("07", "02"), ("08", "02"),
    ("10", "02"), ("11", "02"), ("12", "02"),
]


# ===================================================================
# Step 1: per-window accel variance
# ===================================================================
def compute_accel_variance_per_window(subj_id, type_id):
    """Returns list of (accel_var, is_valid) length = W (bpm0 length).
    OOR window → (NaN, False).
    """
    sig, bpm0 = load_subject(subj_id, type_id)
    W = len(bpm0)
    out = []
    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            out.append((np.nan, False))
        else:
            accel_mag = np.sqrt(np.sum(sig[3:6, start:end] ** 2, axis=0))
            out.append((float(np.var(accel_mag)), True))
    return out


print("=" * 70)
print("Step 1: compute accel magnitude variance per (subject, window)")
print("=" * 70)

per_subj_motion = {}    # subj_key → list[(accel_var, is_valid)]
for subj, ty in SUBJECT_TYPES:
    key = f"subj{subj}_type{ty}"
    per_subj_motion[key] = compute_accel_variance_per_window(subj, ty)
    n_valid = sum(1 for _, v in per_subj_motion[key] if v)
    print(f"  {key}: {len(per_subj_motion[key])} windows, {n_valid} valid")


# ===================================================================
# Step 2: global tertile thresholds
# ===================================================================
all_vars = []
for key, items in per_subj_motion.items():
    for v, valid in items:
        if valid:
            all_vars.append(v)

arr = np.array(all_vars)
low_max = float(np.percentile(arr, 100.0 / 3.0))
med_max = float(np.percentile(arr, 200.0 / 3.0))

print()
print(f"Step 2: global tertile thresholds over {len(arr)} non-OOR windows")
print(f"  variance min/max:   {arr.min():.4f} / {arr.max():.4f}")
print(f"  low_max  (33.33%):  {low_max:.4f}")
print(f"  med_max  (66.67%):  {med_max:.4f}")


def classify(v):
    if v <= low_max:
        return "low"
    if v <= med_max:
        return "med"
    return "high"


# (subj_key, window_idx) → motion_group
window_motion = {}
n_per_group = {"low": 0, "med": 0, "high": 0}
for key, items in per_subj_motion.items():
    for i, (v, valid) in enumerate(items):
        if valid:
            g = classify(v)
            window_motion[(key, i)] = g
            n_per_group[g] += 1

print()
print(f"  windows per group:  low={n_per_group['low']}, "
      f"med={n_per_group['med']}, high={n_per_group['high']}")


# ===================================================================
# Step 3: load JSONs + build per-subject (orig_idx → est) maps
# ===================================================================
print()
print("Step 3: load A/B/C JSONs + build orig-index estimate maps")
A_data = json.load(open(RESULTS_DIR / "troika_loso.json"))
B_data = json.load(open(RESULTS_DIR / "rf_loso.json"))
C_data = json.load(open(RESULTS_DIR / "methodC_loso.json"))


def build_estimate_map(method_data, b_mode=False):
    """subj_key → {orig_window_idx → estimate (or None)}.

    A/C: hr_estimates is dense over orig indices.
    B  : hr_estimates only covers valid windows; map B's j → orig i
         via per_subj_motion's valid mask.
    """
    out = {}
    for subj_key, sd in method_data["per_subject"].items():
        ests = sd["hr_estimates"]
        if b_mode:
            valid_indices = [i for i, (v, valid) in enumerate(per_subj_motion[subj_key])
                             if valid]
            # B's dense list ests[j] ↔ original index valid_indices[j]
            if len(ests) != len(valid_indices):
                raise RuntimeError(
                    f"length mismatch for {subj_key}: B has {len(ests)} ests "
                    f"but {len(valid_indices)} valid windows recomputed"
                )
            out[subj_key] = {valid_indices[j]: ests[j] for j in range(len(ests))}
        else:
            out[subj_key] = {i: ests[i] for i in range(len(ests))}
    return out


A_est = build_estimate_map(A_data, b_mode=False)
B_est = build_estimate_map(B_data, b_mode=True)
C_est = build_estimate_map(C_data, b_mode=False)


# Ground truth from method A (full bpm0 dense, identical across methods)
A_truth = {}
for subj_key, sd in A_data["per_subject"].items():
    truths = sd["hr_truths"]
    A_truth[subj_key] = {i: truths[i] for i in range(len(truths))}


# ===================================================================
# Step 4: intersection of valid windows across all 3 methods
# ===================================================================
def get_valid_float(d, key1, key2):
    """Lookup; return None if missing / None / NaN."""
    v = d.get(key1, {}).get(key2)
    if v is None:
        return None
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    if np.isnan(v):
        return None
    return v


intersection = set()
for (subj_key, idx), grp in window_motion.items():
    a = get_valid_float(A_est, subj_key, idx)
    b = get_valid_float(B_est, subj_key, idx)
    c = get_valid_float(C_est, subj_key, idx)
    t = get_valid_float(A_truth, subj_key, idx)
    if None in (a, b, c, t):
        continue
    intersection.add((subj_key, idx))

print()
print(f"Step 4: intersection where A∩B∩C∩truth all valid: "
      f"{len(intersection)} windows (out of {len(window_motion)})")


# ===================================================================
# Step 5: MAE per (method × motion_group), over intersection
# ===================================================================
errors = {
    "A": {"low": [], "med": [], "high": []},
    "B": {"low": [], "med": [], "high": []},
    "C": {"low": [], "med": [], "high": []},
}
for (subj_key, idx) in intersection:
    grp = window_motion[(subj_key, idx)]
    t = A_truth[subj_key][idx]
    a = A_est[subj_key][idx]
    b = B_est[subj_key][idx]
    c = C_est[subj_key][idx]
    errors["A"][grp].append(abs(float(a) - float(t)))
    errors["B"][grp].append(abs(float(b) - float(t)))
    errors["C"][grp].append(abs(float(c) - float(t)))


mae_table = {}
for m in ("A", "B", "C"):
    mae_table[m] = {}
    for g in ("low", "med", "high"):
        vals = errors[m][g]
        mae_table[m][g] = float(np.mean(vals)) if vals else None


print()
print("Step 5: MAE table (method × motion_group, over intersection)")
print(f"            {'low':>10s}  {'med':>10s}  {'high':>10s}")
for m in ("A", "B", "C"):
    row = mae_table[m]
    print(f"  Method {m}  "
          f"{row['low']:>10.3f}  {row['med']:>10.3f}  {row['high']:>10.3f}")


# ===================================================================
# Step 6: write JSON
# ===================================================================
output = {
    "motion_intensity_definition": "var(sqrt(X^2+Y^2+Z^2)) per window, no bandpass; matches Method C accel_intensity feature",
    "motion_tertile_thresholds": {
        "low_max": low_max,
        "med_max": med_max,
    },
    "n_windows_per_group": {
        "low": int(n_per_group["low"]),
        "med": int(n_per_group["med"]),
        "high": int(n_per_group["high"]),
    },
    "n_windows_in_intersection": len(intersection),
    "n_windows_per_group_in_intersection": {
        g: int(sum(1 for k in intersection if window_motion[k] == g))
        for g in ("low", "med", "high")
    },
    "mae_by_method_and_motion": mae_table,
    "subjects_used": [f"subj{s}_type{t}" for s, t in SUBJECT_TYPES],
}
with open(OUT_PATH, "w") as f:
    json.dump(output, f, indent=2)

print()
print("=" * 70)
print(f"results: {OUT_PATH}")
print("=" * 70)
