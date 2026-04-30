"""TROIKA-lite: 信号处理 baseline (Route A).

简化版 TROIKA (Zhang 2015):
1. Bandpass filter PPG 到 0.4–5 Hz (心率频段)
2. FFT PPG + accel
3. Spectral subtraction: 用 accel spectrum 减去 PPG spectrum 中的 motion 峰
4. Peak detection: 剩余 spectrum 最大峰 → HR

省略原版的 M-FOCUSS (sparse optimization) — 用标准 FFT + 频谱减法替代。
λ 是 spectral subtraction 的权重 (默认 1.0,LLM 版本会动态生成)。
"""

from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt

from data import FS, Window

HR_LOW_HZ = 0.4  # 24 BPM
HR_HIGH_HZ = 5.0  # 300 BPM


def bandpass(signal: np.ndarray, fs: int = FS, low: float = HR_LOW_HZ, high: float = HR_HIGH_HZ, order: int = 4) -> np.ndarray:
    """4-order Butterworth bandpass."""
    nyq = fs / 2
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, signal)


def fft_spectrum(signal: np.ndarray, fs: int = FS) -> tuple[np.ndarray, np.ndarray]:
    """单边 FFT spectrum.

    Returns:
        (freqs, magnitude) — freqs in Hz, magnitude 取 abs
    """
    n = len(signal)
    fft = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1 / fs)
    mag = np.abs(fft)
    return freqs, mag


def accel_magnitude(accel: np.ndarray) -> np.ndarray:
    """3-axis accel → 1D magnitude. accel: (3, N)"""
    return np.sqrt(np.sum(accel**2, axis=0))


def spectral_subtraction(ppg_mag: np.ndarray, accel_mag: np.ndarray, lam: float = 1.0) -> np.ndarray:
    """用 accel spectrum 减去 PPG spectrum 的 motion 部分。

    Args:
        ppg_mag: PPG single-side magnitude spectrum
        accel_mag: 同长度的 accel magnitude spectrum
        lam: subtraction 权重 (LLM 版本会动态生成)

    Returns:
        cleaned spectrum, 已 clip 到 ≥ 0
    """
    # normalize accel mag 到 PPG mag 量级
    if np.max(accel_mag) > 0:
        accel_norm = accel_mag * (np.max(ppg_mag) / np.max(accel_mag))
    else:
        accel_norm = accel_mag
    cleaned = ppg_mag - lam * accel_norm
    return np.maximum(cleaned, 0)


def peak_to_hr(freqs: np.ndarray, mag: np.ndarray, hr_low: float = HR_LOW_HZ, hr_high: float = HR_HIGH_HZ) -> float:
    """spectrum 最大峰 → HR (BPM)。"""
    band_mask = (freqs >= hr_low) & (freqs <= hr_high)
    if not band_mask.any():
        return float("nan")
    band_freqs = freqs[band_mask]
    band_mag = mag[band_mask]
    peak_freq = band_freqs[np.argmax(band_mag)]
    return float(peak_freq * 60)  # Hz → BPM


def estimate_hr(window: Window, lam: float = 1.0, ppg_channel: int = 0) -> float:
    """对一个窗口跑完整 TROIKA-lite pipeline。

    Args:
        window: Window 实例
        lam: spectral subtraction 权重 (default 1.0)
        ppg_channel: 用 PPG 的哪一通道 (0 或 1)

    Returns:
        estimated HR in BPM
    """
    ppg = window.ppg[ppg_channel]
    accel_mag_t = accel_magnitude(window.accel)

    # 1. Bandpass
    ppg_filt = bandpass(ppg)
    accel_filt = bandpass(accel_mag_t)

    # 2. FFT
    freqs, ppg_spec = fft_spectrum(ppg_filt)
    _, accel_spec = fft_spectrum(accel_filt)

    # 3. Spectral subtraction
    cleaned = spectral_subtraction(ppg_spec, accel_spec, lam=lam)

    # 4. Peak → HR
    return peak_to_hr(freqs, cleaned)


# ─── Oracle λ 搜索 (供 §4.3 评估 LLM-vs-oracle 用) ───

def oracle_lambda(window: Window, lam_grid: np.ndarray | None = None) -> tuple[float, float]:
    """对单个窗口在 grid 上搜最优 λ (使 |estimated HR - truth| 最小)。

    Returns:
        (best_lambda, best_error_bpm)
    """
    if lam_grid is None:
        lam_grid = np.linspace(0.1, 3.0, 30)
    best_lam, best_err = 1.0, float("inf")
    for lam in lam_grid:
        est = estimate_hr(window, lam=lam)
        if np.isnan(est):
            continue
        err = abs(est - window.hr_truth)
        if err < best_err:
            best_err = err
            best_lam = float(lam)
    return best_lam, best_err


if __name__ == "__main__":
    import argparse

    from data import IEEESPC2015Dataset

    p = argparse.ArgumentParser(description="TROIKA-lite sanity check")
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--subject", type=int, default=1)
    p.add_argument("--lam", type=float, default=1.0)
    args = p.parse_args()

    ds = IEEESPC2015Dataset(args.data_dir)
    windows = ds.windows_for_subject(args.subject)

    errors = []
    for w in windows:
        est = estimate_hr(w, lam=args.lam)
        if not np.isnan(est):
            errors.append(abs(est - w.hr_truth))
    errors = np.array(errors)
    print(f"Subject {args.subject}: {len(errors)} valid windows")
    print(f"  MAE: {np.mean(errors):.2f} BPM")
    print(f"  Median: {np.median(errors):.2f} BPM")
    print(f"  P90:    {np.percentile(errors, 90):.2f} BPM")
    print(f"  Max:    {np.max(errors):.2f} BPM")
    print(f"\n  Reference: TROIKA paper reports 2.34 BPM MAE on this dataset.")
    print(f"  (Our simplified version omits M-FOCUSS — expect higher MAE.)")
