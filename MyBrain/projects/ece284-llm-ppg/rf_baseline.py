"""Random Forest baseline (Route B).

Per-window 4 频域特征 → sklearn RandomForestRegressor → HR (BPM)。

特征:
1. PPG 主频率 (dominant freq in HR band)
2. PPG 心率频段总能量 (spectral energy 0.4-5 Hz)
3. PPG 最高峰 / 第二高峰比 (peak-to-second-peak ratio)
4. Accel magnitude RMS

按 proposal §4 的 evaluation axes 跑 LOSO。
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestRegressor

from data import FS, Window, loso_folds
from troika_lite import HR_HIGH_HZ, HR_LOW_HZ, accel_magnitude, bandpass, fft_spectrum


def extract_features(window: Window, ppg_channel: int = 0) -> np.ndarray:
    """从一个窗口提 4 维特征。"""
    ppg = bandpass(window.ppg[ppg_channel])
    accel_mag_sig = accel_magnitude(window.accel)

    freqs, ppg_spec = fft_spectrum(ppg)
    band_mask = (freqs >= HR_LOW_HZ) & (freqs <= HR_HIGH_HZ)
    band_freqs = freqs[band_mask]
    band_mag = ppg_spec[band_mask]

    # 1. dominant frequency in HR band (Hz)
    if len(band_mag) > 0:
        dom_freq = float(band_freqs[np.argmax(band_mag)])
    else:
        dom_freq = 0.0

    # 2. spectral energy in HR band
    energy = float(np.sum(band_mag**2))

    # 3. peak-to-second-peak ratio
    sorted_mag = np.sort(band_mag)[::-1]
    if len(sorted_mag) >= 2 and sorted_mag[1] > 1e-8:
        ratio = float(sorted_mag[0] / sorted_mag[1])
    else:
        ratio = 1.0

    # 4. accel magnitude RMS
    accel_rms = float(np.sqrt(np.mean(accel_mag_sig**2)))

    return np.array([dom_freq, energy, ratio, accel_rms], dtype=np.float64)


def featurize_windows(windows: list[Window]) -> tuple[np.ndarray, np.ndarray]:
    """整批窗口 → (X (n,4), y (n,))"""
    X = np.stack([extract_features(w) for w in windows])
    y = np.array([w.hr_truth for w in windows])
    return X, y


def train_rf(X_train: np.ndarray, y_train: np.ndarray, n_estimators: int = 200, seed: int = 42) -> RandomForestRegressor:
    """训一个 RF。"""
    rf = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=None,
        min_samples_leaf=2,
        random_state=seed,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)
    return rf


def loso_evaluate(ds, verbose: bool = True) -> dict:
    """LOSO 评估。

    Returns:
        dict: {"per_subject_mae": [...], "all_predictions": [(truth, pred, accel_rms), ...]}
    """
    n_subj = ds.n_subjects
    folds = loso_folds(n_subj)
    per_subject_mae = []
    all_preds = []

    # 预先把所有 subject 的窗口 + 特征算好,避免重复
    cache: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    for s in range(1, n_subj + 1):
        windows = ds.windows_for_subject(s)
        X, y = featurize_windows(windows)
        cache[s] = (X, y)
        if verbose:
            print(f"  Subject {s}: {len(windows)} windows cached")

    for train_subj, test_subj in folds:
        X_tr = np.vstack([cache[s][0] for s in train_subj])
        y_tr = np.concatenate([cache[s][1] for s in train_subj])
        X_te, y_te = cache[test_subj]
        rf = train_rf(X_tr, y_tr)
        y_pred = rf.predict(X_te)
        mae = float(np.mean(np.abs(y_pred - y_te)))
        per_subject_mae.append(mae)
        for truth, pred, x in zip(y_te, y_pred, X_te):
            all_preds.append((float(truth), float(pred), float(x[3])))  # x[3] = accel RMS
        if verbose:
            print(f"  Test subj {test_subj}: MAE = {mae:.2f} BPM")

    overall_mae = float(np.mean(per_subject_mae))
    if verbose:
        print(f"\n  Overall LOSO MAE: {overall_mae:.2f} BPM (avg over {n_subj} subjects)")
    return {
        "per_subject_mae": per_subject_mae,
        "overall_mae": overall_mae,
        "all_predictions": all_preds,
    }


if __name__ == "__main__":
    import argparse
    import json

    from data import IEEESPC2015Dataset

    p = argparse.ArgumentParser(description="RF baseline LOSO")
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--out", default="results/rf_loso.json")
    args = p.parse_args()

    ds = IEEESPC2015Dataset(args.data_dir)
    print(f"Found {ds.n_subjects} subjects")
    print("\n=== Phase 1: Featurize all subjects ===")
    print("\n=== Phase 2: LOSO evaluation ===")
    res = loso_evaluate(ds)

    # 保存结果
    import os

    os.makedirs("results", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(
            {
                "per_subject_mae": res["per_subject_mae"],
                "overall_mae": res["overall_mae"],
            },
            f,
            indent=2,
        )
    print(f"\nResults saved to {args.out}")
