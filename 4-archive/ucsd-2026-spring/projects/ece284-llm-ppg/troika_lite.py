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


def evaluate_subject(ds, subject_id: int, lam: float = 1.0) -> dict:
    """跑一个 subject 的全部窗口, 返回 stats + per-window predictions."""
    windows = ds.windows_for_subject(subject_id)
    truths, preds, accel_rms_list = [], [], []
    for w in windows:
        est = estimate_hr(w, lam=lam)
        accel_rms = float(np.sqrt(np.mean(accel_magnitude(w.accel) ** 2)))
        truths.append(float(w.hr_truth))
        preds.append(float(est) if not np.isnan(est) else None)
        accel_rms_list.append(accel_rms)
    valid_errs = [
        abs(p - t) for p, t in zip(preds, truths) if p is not None
    ]
    return {
        "subject": subject_id,
        "n_windows": len(windows),
        "n_valid": len(valid_errs),
        "mae": float(np.mean(valid_errs)) if valid_errs else float("nan"),
        "median": float(np.median(valid_errs)) if valid_errs else float("nan"),
        "p90": float(np.percentile(valid_errs, 90)) if valid_errs else float("nan"),
        "max": float(np.max(valid_errs)) if valid_errs else float("nan"),
        "predictions": [
            {"truth": t, "pred": p, "accel_rms": a}
            for t, p, a in zip(truths, preds, accel_rms_list)
        ],
    }


if __name__ == "__main__":
    import argparse
    import json
    import os

    from data import IEEESPC2015Dataset

    p = argparse.ArgumentParser(description="TROIKA-lite sanity check / LOSO dump")
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--subject", type=int, default=1)
    p.add_argument("--lam", type=float, default=1.0)
    p.add_argument("--loso", action="store_true", help="跑全 12 subjects 并 dump JSON")
    p.add_argument("--out", default="results/troika_loso.json")
    args = p.parse_args()

    ds = IEEESPC2015Dataset(args.data_dir)

    if args.loso:
        per_subject = []
        for s in range(1, ds.n_subjects + 1):
            stats = evaluate_subject(ds, s, lam=args.lam)
            per_subject.append(stats)
            print(
                f"  Subject {s:>2}: n={stats['n_valid']:>3} valid / {stats['n_windows']:>3} total | "
                f"MAE={stats['mae']:>6.2f} | median={stats['median']:>5.2f} | p90={stats['p90']:>6.2f} BPM"
            )

        per_subject_mae = [s["mae"] for s in per_subject]
        overall_mae = float(np.mean(per_subject_mae))
        print(f"\n  Overall LOSO-style MAE (avg over {ds.n_subjects} subjects): {overall_mae:.2f} BPM")
        print(f"  Best:  subj {1 + int(np.argmin(per_subject_mae))} ({min(per_subject_mae):.2f})")
        print(f"  Worst: subj {1 + int(np.argmax(per_subject_mae))} ({max(per_subject_mae):.2f})")
        print(f"  Reference: TROIKA paper reports 2.34 BPM MAE (full M-FOCUSS).")

        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(
                {
                    "system": "troika_lite",
                    "lambda": args.lam,
                    "n_subjects": ds.n_subjects,
                    "overall_mae": overall_mae,
                    "per_subject_mae": per_subject_mae,
                    "per_subject": per_subject,
                },
                f,
                indent=2,
            )
        print(f"\n  Saved → {args.out}")
    else:
        stats = evaluate_subject(ds, args.subject, lam=args.lam)
        print(f"Subject {args.subject}: {stats['n_valid']} valid windows")
        print(f"  MAE: {stats['mae']:.2f} BPM")
        print(f"  Median: {stats['median']:.2f} BPM")
        print(f"  P90:    {stats['p90']:.2f} BPM")
        print(f"  Max:    {stats['max']:.2f} BPM")
        print(f"\n  Reference: TROIKA paper reports 2.34 BPM MAE on this dataset.")
        print(f"  (Our simplified version omits M-FOCUSS — expect higher MAE.)")
