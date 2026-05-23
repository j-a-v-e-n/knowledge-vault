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

# ---- HR tracking tunables (调参 round-by-round) ----
COLD_START_N = 10                       # 前 N 个窗口不用 tracking, 全频段最大值
ENERGY_THRESHOLD = 0.5                  # tracking peak 能量 / global max 比值 < 此阈值 → fallback
MAX_JUMP_BPM = 20                       # tracking band 半宽 (BPM)


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
def estimate_hr_one_window(ppg_window, accel_xyz_window, fs=125, lam=1.0,
                            prev_hr=None, max_jump_bpm=15,
                            cold_start_active=False, energy_threshold=0.5):
    """Estimate HR for one window via PPG-vs-accel spectral subtraction.

    Args:
        ppg_window:        (W,)  PPG ch1, length 1000 expected (8 s @ 125 Hz)
        accel_xyz_window:  (3,W) accel X/Y/Z over same window
        fs:                sampling rate Hz
        lam:               subtraction weight (cleaned = ppg - lam * coef * accel)
        prev_hr:           previous window HR estimate (BPM) for tracking, or None
        max_jump_bpm:      max allowed |HR - prev_hr| (BPM) within tracking band
        cold_start_active: True → 强制忽略 prev_hr, 用全频段最大值 (前 N 窗冷启动)
        energy_threshold:  tracking peak 能量 < threshold * global max 时 fallback
                           到全频段最大值 (self-correction)

    Returns:
        (hr_bpm or np.nan, debug_dict)
        debug_dict keys: ppg_filt, accel_mag_filt, freqs,
                         ppg_power, accel_power, cleaned_power, coef, peak_freq,
                         prev_hr_used, tracking_band_low_hz, tracking_band_high_hz,
                         tracking_fallback_used, cold_start_active,
                         energy_threshold_used.
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

    # cold_start_active=True → 视作没有 prev_hr (强制 cold start)
    has_prev = (
        (not cold_start_active)
        and (prev_hr is not None)
        and (not np.isnan(prev_hr))
    )
    if has_prev:
        tracking_band_low_hz = float((prev_hr - max_jump_bpm) / 60.0)
        tracking_band_high_hz = float((prev_hr + max_jump_bpm) / 60.0)
    else:
        tracking_band_low_hz = None
        tracking_band_high_hz = None

    debug_dict = {
        "ppg_filt": ppg_filt,
        "accel_mag_filt": accel_mag_filt,
        "freqs": freqs,
        "ppg_power": ppg_power,
        "accel_power": accel_power,
        "cleaned_power": cleaned_power,
        "coef": coef,
        "peak_freq": None,
        "prev_hr_used": prev_hr,
        "tracking_band_low_hz": tracking_band_low_hz,
        "tracking_band_high_hz": tracking_band_high_hz,
        "tracking_fallback_used": False,
        "cold_start_active": bool(cold_start_active),
        "energy_threshold_used": float(energy_threshold),
    }

    hr_band_mask = (freqs >= HR_BAND_LOW) & (freqs <= HR_BAND_HIGH)
    cleaned_band = cleaned_power[hr_band_mask]
    freqs_band = freqs[hr_band_mask]

    peaks, _ = find_peaks(cleaned_band)
    if len(peaks) == 0:
        return np.nan, debug_dict

    # 全频段最大 peak (always computed; used for cold start, fallback, self-correction)
    global_best_idx = peaks[int(np.argmax(cleaned_band[peaks]))]
    global_best_energy = float(cleaned_band[global_best_idx])

    # ---- Peak selection: HR tracking from prev_hr (if available) ----
    if not has_prev:
        # Cold start / 上一窗 NaN → 全频段最大值
        best_peak_idx = global_best_idx
    else:
        peak_freqs_hz = freqs_band[peaks]
        in_band = (
            (peak_freqs_hz >= tracking_band_low_hz)
            & (peak_freqs_hz <= tracking_band_high_hz)
        )
        valid_peaks = peaks[in_band]
        if len(valid_peaks) > 0:
            tracking_best_idx = valid_peaks[
                int(np.argmax(cleaned_band[valid_peaks]))
            ]
            tracking_best_energy = float(cleaned_band[tracking_best_idx])
            # Self-correction: tracking peak 能量太弱 → fallback 到全频段最大值
            if tracking_best_energy < energy_threshold * global_best_energy:
                best_peak_idx = global_best_idx
                debug_dict["tracking_fallback_used"] = True
            else:
                best_peak_idx = tracking_best_idx
        else:
            # tracking band 内无 peak → fallback 全频段最大值
            best_peak_idx = global_best_idx
            debug_dict["tracking_fallback_used"] = True

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
    prev_hr = None                       # HR tracking 状态，初始 None (cold start)
    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            hr_estimates.append(np.nan)
            continue                     # 越界 → 不更新 prev_hr
        cold_start_active = (i < COLD_START_N)
        hr, _ = estimate_hr_one_window(
            sig[1, start:end],          # PPG ch1
            sig[3:6, start:end],        # accel XYZ
            fs=FS,
            lam=lam,                    # 显式传 lam, 不依赖默认值
            prev_hr=prev_hr,            # HR tracking from prev window
            max_jump_bpm=MAX_JUMP_BPM,  # tracking band 半宽
            cold_start_active=cold_start_active,
            energy_threshold=ENERGY_THRESHOLD,
        )
        hr_estimates.append(hr)
        if not np.isnan(hr):
            prev_hr = hr                # 仅在有效估计时更新
        # hr 为 NaN 时 prev_hr 保持上次值, 让下一窗仍用更早的 prev_hr 约束

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
