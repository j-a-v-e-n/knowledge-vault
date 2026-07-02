"""rf_baseline.py — Method B: Random Forest baseline for PPG HR estimation.

11-D hand-crafted spectral feature vector → RandomForestRegressor → HR (BPM).
LOSO over the 11 available IEEE SPC 2015 subjects (subject 09 missing on the
Udacity mirror).

API:
  - extract_features(ppg_window, accel_xyz_window, fs=125)
      → 1D np.ndarray of length 11 (float64)
  - extract_subject_features(subj_id, type_id)
      → (X (W,11), y (W,))   越界窗口跳过
  - run_loso()
      → dict (same schema as 04_rf_loso.py writes to JSON)

Features (in fixed order):
  PPG side (4):
    0  ppg_dom_freq          # 0.4-5 Hz 频段内最强峰频率 Hz
    1  ppg_dom_power         # 该峰能量
    2  ppg_band_energy       # 0.4-5 Hz 内 PSD 总和
    3  ppg_peak_to_band_ratio = ppg_dom_power / ppg_band_energy
  Accel side (5):
    4  accel_dom_freq
    5  accel_dom_power
    6  accel_band_energy
    7  accel_total_magnitude # mean(accel_mag), motion intensity proxy
    8  accel_variance        # var(accel_mag)
  Cross (2):
    9  ppg_accel_peak_ratio  = ppg_dom_power / (accel_dom_power + 1e-6)
    10 freq_diff             = |ppg_dom_freq - accel_dom_freq|

找不到 peak 时 dom_freq / dom_power 设为 0.0 (不 NaN, 避免影响 RF).
"""

import numpy as np
from scipy.signal import butter, filtfilt, periodogram, find_peaks
from sklearn.ensemble import RandomForestRegressor

from data import load_subject


# ===================================================================
# 常量 (跟 troika_lite.py 对齐)
# ===================================================================
FS = 125
WINDOW_SAMPLES = 1000
SHIFT_SAMPLES = 250
HR_BAND_LOW = 0.4
HR_BAND_HIGH = 5.0
NFFT = 4096

N_FEATURES = 11
FEATURE_NAMES = [
    "ppg_dom_freq", "ppg_dom_power", "ppg_band_energy",
    "ppg_peak_to_band_ratio",
    "accel_dom_freq", "accel_dom_power", "accel_band_energy",
    "accel_total_magnitude", "accel_variance",
    "ppg_accel_peak_ratio", "freq_diff",
]

# RF 超参 (固定, 不调)
RF_N_ESTIMATORS = 100
RF_RANDOM_STATE = 42

# LOSO subject 池 (跟 03_troika_loso.py 完全一致)
SUBJECT_TYPES = [
    ("01", "01"), ("02", "02"), ("03", "02"), ("04", "01"),
    ("05", "02"), ("06", "02"), ("07", "02"), ("08", "02"),
    ("10", "02"), ("11", "02"), ("12", "02"),
]
MISSING_SUBJECTS = ["09"]


# ===================================================================
# Helpers
# ===================================================================
def _bandpass(signal, fs):
    """4th-order Butterworth bandpass 0.4-5 Hz, zero-phase filtfilt."""
    nyq = fs / 2.0
    b, a = butter(4, [HR_BAND_LOW / nyq, HR_BAND_HIGH / nyq], btype="band")
    return filtfilt(b, a, signal)


def _hr_band_peak(power, freqs):
    """Find dominant peak in HR band [0.4, 5] Hz.

    Returns (dom_freq, dom_power, band_energy).
    No peak → (0.0, 0.0, band_energy).
    """
    band_mask = (freqs >= HR_BAND_LOW) & (freqs <= HR_BAND_HIGH)
    power_band = power[band_mask]
    freqs_band = freqs[band_mask]
    band_energy = float(np.sum(power_band))

    peaks, _ = find_peaks(power_band)
    if len(peaks) == 0:
        return 0.0, 0.0, band_energy

    best_idx = peaks[int(np.argmax(power_band[peaks]))]
    return float(freqs_band[best_idx]), float(power_band[best_idx]), band_energy


# ===================================================================
# 1. Feature extraction (single window)
# ===================================================================
def extract_features(ppg_window, accel_xyz_window, fs=125):
    """Extract 11-D feature vector from one 8-sec window.

    Args:
        ppg_window:        (N,)   PPG ch1
        accel_xyz_window:  (3,N)  accel X/Y/Z
        fs:                sample rate Hz

    Returns:
        np.ndarray shape (11,), float64.
    """
    # ---- PPG side ----
    ppg_filt = _bandpass(ppg_window, fs)
    freqs, ppg_power = periodogram(ppg_filt, fs=fs, nfft=NFFT)
    ppg_dom_freq, ppg_dom_power, ppg_band_energy = _hr_band_peak(ppg_power, freqs)
    if ppg_band_energy > 1e-12:
        ppg_peak_to_band_ratio = ppg_dom_power / ppg_band_energy
    else:
        ppg_peak_to_band_ratio = 0.0

    # ---- Accel side ----
    accel_mag = np.sqrt(np.sum(accel_xyz_window ** 2, axis=0))
    accel_total_magnitude = float(np.mean(accel_mag))
    accel_variance = float(np.var(accel_mag))

    accel_filt = _bandpass(accel_mag, fs)
    _, accel_power = periodogram(accel_filt, fs=fs, nfft=NFFT)
    accel_dom_freq, accel_dom_power, accel_band_energy = _hr_band_peak(
        accel_power, freqs
    )

    # ---- Cross ----
    ppg_accel_peak_ratio = ppg_dom_power / (accel_dom_power + 1e-6)
    freq_diff = abs(ppg_dom_freq - accel_dom_freq)

    return np.array([
        ppg_dom_freq, ppg_dom_power, ppg_band_energy, ppg_peak_to_band_ratio,
        accel_dom_freq, accel_dom_power, accel_band_energy,
        accel_total_magnitude, accel_variance,
        ppg_accel_peak_ratio, freq_diff,
    ], dtype=np.float64)


# ===================================================================
# 2. Subject-level feature extraction
# ===================================================================
def extract_subject_features(subj_id, type_id):
    """Walk all windows of one subject; return (X, y) of valid windows only.

    越界窗口 (i*250 + 1000 > sig.shape[1]) 跳过, 不进 X/y.
    Returns:
        X:  (W_valid, 11) float64
        y:  (W_valid,)    float64  ground-truth BPM
    """
    sig, bpm0 = load_subject(subj_id, type_id)
    W = len(bpm0)

    X_list, y_list = [], []
    n_skipped = 0
    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            n_skipped += 1
            continue
        feats = extract_features(sig[1, start:end], sig[3:6, start:end], fs=FS)
        X_list.append(feats)
        y_list.append(float(bpm0[i]))

    if X_list:
        X = np.array(X_list, dtype=np.float64)
        y = np.array(y_list, dtype=np.float64)
    else:
        X = np.empty((0, N_FEATURES), dtype=np.float64)
        y = np.empty((0,), dtype=np.float64)

    if n_skipped > 0:
        print(f"  [info] subj{subj_id}_type{type_id}: skipped {n_skipped} "
              f"out-of-range windows")
    return X, y


# ===================================================================
# 3. LOSO driver
# ===================================================================
def run_loso():
    """LOSO over SUBJECT_TYPES. Returns a dict for direct JSON dump.

    Schema:
      {
        "overall_mae": float,
        "n_subjects": 11,
        "missing_subjects": ["09"],
        "method": "RandomForest",
        "n_features": 11,
        "model_params": {"n_estimators": 100, "random_state": 42},
        "per_subject": {
          "subj01_type01": {mae, type_id, hr_estimates, hr_truths, n_windows},
          ...
        }
      }
    """
    # ---- Pre-extract features for all subjects (avoid 11x re-extract in loop) ----
    print("[step 1/2] extracting features for all 11 subjects ...")
    all_feats = {}
    for subj_id, type_id in SUBJECT_TYPES:
        X, y = extract_subject_features(subj_id, type_id)
        all_feats[(subj_id, type_id)] = (X, y)
        print(f"  subj{subj_id}_type{type_id}: X.shape={X.shape}  y.shape={y.shape}")

    # ---- LOSO loop ----
    print()
    print("[step 2/2] LOSO train+predict ...")
    per_subject = {}
    per_subject_mae = []

    for held_out_idx, (subj_id, type_id) in enumerate(SUBJECT_TYPES):
        train_pairs = (
            SUBJECT_TYPES[:held_out_idx] + SUBJECT_TYPES[held_out_idx + 1:]
        )
        train_X = np.concatenate([all_feats[p][0] for p in train_pairs], axis=0)
        train_y = np.concatenate([all_feats[p][1] for p in train_pairs], axis=0)

        model = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            random_state=RF_RANDOM_STATE,
            n_jobs=-1,
        )
        model.fit(train_X, train_y)

        test_X, test_y = all_feats[(subj_id, type_id)]
        predictions = model.predict(test_X)

        mae = float(np.nanmean(np.abs(predictions - test_y)))

        key = f"subj{subj_id}_type{type_id}"
        per_subject[key] = {
            "mae": mae,
            "type_id": type_id,
            "hr_estimates": predictions.tolist(),
            "hr_truths": test_y.tolist(),
            "n_windows": int(test_X.shape[0]),
        }
        per_subject_mae.append(mae)
        print(f"  {key}: MAE={mae:.3f} BPM, n_windows={test_X.shape[0]}")

    overall_mae = float(np.mean(per_subject_mae))

    return {
        "overall_mae": overall_mae,
        "n_subjects": len(SUBJECT_TYPES),
        "missing_subjects": MISSING_SUBJECTS,
        "method": "RandomForest",
        "n_features": N_FEATURES,
        "model_params": {
            "n_estimators": RF_N_ESTIMATORS,
            "random_state": RF_RANDOM_STATE,
        },
        "per_subject": per_subject,
    }
