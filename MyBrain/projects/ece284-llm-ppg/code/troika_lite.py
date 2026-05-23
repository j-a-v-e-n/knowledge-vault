"""troika_lite.py — TROIKA-lite HR estimation (bandpass + spectral subtraction).

ECE 284 LLM-PPG project. Core API:
  - bandpass_filter(signal, lowcut, highcut, fs, order)
      4-th order Butterworth bandpass, zero-phase filtfilt.
  - estimate_hr_one_window(ppg_window, accel_xyz_window, fs, lam)
      Single 8-sec window → (hr_bpm or np.nan, debug_dict).
  - run_subject(subj_id, type_id, lam)
      Loop run on full subject → dict(mae, hr_estimates, hr_truths, n_windows, n_nan).

Pipeline (single window):
  1) PPG bandpass 0.4-5 Hz Butterworth filtfilt
  2) Accel magnitude = sqrt(X²+Y²+Z²) → same bandpass
  3) PSD via scipy.signal.periodogram (nfft=4096)
  4) Spectral subtraction: cleaned = max(ppg_power - lam * accel_power, 0)
  5) Peak in HR band [0.4, 5] Hz via find_peaks; take max-amplitude peak
  6) HR = peak_freq * 60
"""

import numpy as np
from scipy.signal import butter, filtfilt, periodogram, find_peaks

from data import load_subject


# ===================================================================
# 数据集常量 (Zhang 2015 TROIKA / IEEE SPC 2015)
# ===================================================================
FS = 125                                # 采样率 Hz
WINDOW_SAMPLES = 1000                   # 8 s 窗 = 1000 samples
SHIFT_SAMPLES = 250                     # 2 s 步长 = 250 samples
HR_BAND_LOW = 0.4                       # HR 频段下界 Hz (= 24 BPM)
HR_BAND_HIGH = 5.0                      # HR 频段上界 Hz (= 300 BPM)
NFFT = 4096                             # periodogram zero-padding


# ===================================================================
# 1. Bandpass filter
# ===================================================================
def bandpass_filter(signal, lowcut=0.4, highcut=5.0, fs=125, order=4):
    """4th-order Butterworth bandpass, zero-phase filtfilt."""
    nyq = fs / 2.0
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return filtfilt(b, a, signal)


# ===================================================================
# 2. Single-window HR estimate
# ===================================================================
def estimate_hr_one_window(ppg_window, accel_xyz_window, fs=125, lam=1.0):
    """Estimate HR for one window via PPG-vs-accel spectral subtraction.

    Args:
        ppg_window:       (W,)  PPG ch1, length 1000 expected (8 s @ 125 Hz)
        accel_xyz_window: (3,W) accel X/Y/Z over same window
        fs:               sampling rate Hz
        lam:              subtraction weight (cleaned = ppg - lam * accel)

    Returns:
        (hr_bpm or np.nan, debug_dict)
        debug_dict keys: ppg_filt, accel_mag_filt, freqs,
                         ppg_power, accel_power, cleaned_power, peak_freq.
    """
    # --- 1. PPG bandpass ---
    ppg_filt = bandpass_filter(
        ppg_window, lowcut=HR_BAND_LOW, highcut=HR_BAND_HIGH, fs=fs
    )

    # --- 2. Accel magnitude + bandpass ---
    accel_mag = np.sqrt(np.sum(accel_xyz_window ** 2, axis=0))
    accel_mag_filt = bandpass_filter(
        accel_mag, lowcut=HR_BAND_LOW, highcut=HR_BAND_HIGH, fs=fs
    )

    # --- 3. PSD (periodogram, nfft=4096) ---
    freqs, ppg_power = periodogram(ppg_filt, fs=fs, nfft=NFFT)
    _, accel_power = periodogram(accel_mag_filt, fs=fs, nfft=NFFT)

    # --- 4. Spectral subtraction + 5. Peak detection in HR band ---
    # HR 频段内 regression-based normalization
    # coef 表示 "在 HR 频段内, PPG 频谱里 accel 能解释的耦合系数"
    hr_band_mask_local = (freqs >= HR_BAND_LOW) & (freqs <= HR_BAND_HIGH)
    ppg_hr = ppg_power[hr_band_mask_local]
    accel_hr = accel_power[hr_band_mask_local]

    accel_hr_sq_sum = float(np.sum(accel_hr ** 2))
    if accel_hr_sq_sum < 1e-12:
        # accel 在 HR 频段内几乎没能量 (静息窗口) → 无需 subtraction
        coef = 0.0
    else:
        coef = float(np.sum(accel_hr * ppg_hr) / accel_hr_sq_sum)

    cleaned_power = np.maximum(ppg_power - lam * coef * accel_power, 0.0)

    debug_dict = {
        "ppg_filt": ppg_filt,
        "accel_mag_filt": accel_mag_filt,
        "freqs": freqs,
        "ppg_power": ppg_power,
        "accel_power": accel_power,
        "cleaned_power": cleaned_power,
        "coef": coef,
        "peak_freq": None,
    }

    hr_band_mask = (freqs >= HR_BAND_LOW) & (freqs <= HR_BAND_HIGH)
    cleaned_band = cleaned_power[hr_band_mask]
    freqs_band = freqs[hr_band_mask]

    peaks, _ = find_peaks(cleaned_band)
    if len(peaks) == 0:
        return np.nan, debug_dict

    best_peak_idx = peaks[int(np.argmax(cleaned_band[peaks]))]
    peak_freq = float(freqs_band[best_peak_idx])
    debug_dict["peak_freq"] = peak_freq

    hr_bpm = peak_freq * 60.0
    return hr_bpm, debug_dict


# ===================================================================
# 3. Single-subject driver
# ===================================================================
def run_subject(subj_id, type_id="01", lam=1.0):
    """Run TROIKA-lite over all windows of one subject.

    Returns:
        dict(mae, hr_estimates, hr_truths, n_windows, n_nan)
    """
    sig, bpm0 = load_subject(subj_id, type_id)
    W = len(bpm0)

    hr_estimates = []
    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            hr_estimates.append(np.nan)
            continue
        hr, _ = estimate_hr_one_window(
            sig[1, start:end],          # PPG ch1
            sig[3:6, start:end],        # accel XYZ
            fs=FS,
            lam=lam,                    # 显式传 lam, 不依赖默认值
        )
        hr_estimates.append(hr)

    hr_truths = bpm0[:W].tolist()       # 与 hr_estimates index 对齐
    hr_est_arr = np.array(hr_estimates, dtype=float)
    hr_truth_arr = np.array(hr_truths, dtype=float)

    mae = float(np.nanmean(np.abs(hr_est_arr - hr_truth_arr)))
    n_nan = int(sum(1 for h in hr_estimates if np.isnan(h)))   # 越界 + 找不到 peak

    return {
        "mae": mae,
        "hr_estimates": hr_estimates,
        "hr_truths": hr_truths,
        "n_windows": int(W),
        "n_nan": n_nan,
    }
