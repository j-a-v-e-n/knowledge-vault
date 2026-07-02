"""IEEE SPC 2015 dataset loader.

数据集结构(基于 Zhang 2015 TROIKA paper):
- 12 subjects 在跑步机上跑步,速度 6/8/12/15 km/h
- 每个 subject: 2-channel wrist PPG, 3-axis wrist accel, 1-lead chest ECG (ground truth HR)
- Sample rate: 125 Hz
- 每个 .mat 文件含一个 6×N 矩阵 (rows: ECG, PPG1, PPG2, accelX, accelY, accelZ)

Public: Zenodo / PhysioNet 镜像。Cite: Zhang et al. (2015) IEEE TBME.

Usage:
    >>> ds = IEEESPC2015Dataset("data/")
    >>> windows = ds.windows_for_subject(1)
    >>> # windows: list of dict, 每个含 ppg / accel / ecg / hr_truth
"""

from __future__ import annotations

import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

try:
    import mat73  # type: ignore

    HAS_MAT73 = True
except ImportError:
    HAS_MAT73 = False

try:
    from scipy.io import loadmat  # type: ignore

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


FS = 125  # Hz, sample rate
WINDOW_SEC = 8.0
SHIFT_SEC = 2.0
WINDOW_LEN = int(WINDOW_SEC * FS)  # 1000 samples
SHIFT_LEN = int(SHIFT_SEC * FS)  # 250 samples


@dataclass
class Window:
    """一个 8 秒窗口的所有数据。"""

    subject_id: int
    window_idx: int
    ppg: np.ndarray  # (2, 1000) — 2-channel wrist PPG
    accel: np.ndarray  # (3, 1000) — 3-axis accel
    ecg: np.ndarray  # (1000,) — chest ECG ground truth
    hr_truth: float  # BPM, 来自 ECG R-peak detection


_KNOWN_KEYS = ("sig", "BPM0", "BVP_Data", "data")


def _load_mat(path: Path) -> np.ndarray:
    """加载一个 .mat 文件,返回主 array (signal 文件 = (6, N), BPMtrace = (n, 1))."""
    if HAS_MAT73:
        try:
            data = mat73.loadmat(str(path))
            for key in _KNOWN_KEYS:
                if key in data:
                    return np.asarray(data[key])
        except Exception:
            pass
    if HAS_SCIPY:
        data = loadmat(str(path))
        for key in _KNOWN_KEYS:
            if key in data:
                return np.asarray(data[key])
    raise RuntimeError(
        f"Cannot load {path}. Install mat73 (`pip install mat73`) or scipy."
    )


def _hr_from_ecg(ecg: np.ndarray, fs: int = FS) -> float:
    """从 ECG 段计算 ground-truth HR (BPM)。

    简单 R-peak 检测 — 对 IEEE SPC 2015 chest ECG 通常足够。
    """
    from scipy.signal import find_peaks

    # 标准化
    ecg = (ecg - np.mean(ecg)) / (np.std(ecg) + 1e-8)
    # find_peaks: 距离 > 0.4s (max 150 BPM), height > 1
    peaks, _ = find_peaks(ecg, distance=int(0.4 * fs), height=1.0)
    if len(peaks) < 2:
        return float("nan")
    intervals = np.diff(peaks) / fs  # seconds
    return float(60.0 / np.mean(intervals))


class IEEESPC2015Dataset:
    """IEEE Signal Processing Cup 2015 dataset wrapper.

    实际数据集结构 (来自 https://github.com/AlessandraGalli/PPG DATABASE.zip):

        data/
          DATABASE/
            Training_data/
              DATA_01_TYPE01.mat       — sig (6, N) float64
              DATA_01_TYPE01_BPMtrace.mat — BPM0 (n_windows, 1) ground-truth
              DATA_02_TYPE02.mat
              DATA_02_TYPE02_BPMtrace.mat
              ...
              DATA_12_TYPE02.mat
              DATA_12_TYPE02_BPMtrace.mat
            Competition_data/        ← 10 个 TEST subjects + True ground-truth (10 subjects)

    我们用 12 个 Training subjects 做 LOSO (proposal §4)。
    BPMtrace 是官方 ground-truth — 每 2 秒一个 BPM 值 (8s window, 2s shift, 跟我们 windowing 完全一致)。
    """

    def __init__(self, data_dir: str | Path = "data/"):
        self.data_dir = Path(data_dir)
        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"{self.data_dir} 不存在。先下数据 (见 README §2)。"
            )
        # 优先 DATABASE/Training_data 子结构,fallback 到平铺
        self._training_dir = self.data_dir / "DATABASE" / "Training_data"
        if not self._training_dir.exists():
            self._training_dir = self.data_dir

    @property
    def subject_files(self) -> list[Path]:
        """返回 12 个 training subject signal .mat 文件 (排除 BPMtrace)。"""
        all_mat = sorted(self._training_dir.glob("DATA_*_TYPE*.mat"))
        sig_files = [f for f in all_mat if "BPMtrace" not in f.name]
        if not sig_files:
            raise FileNotFoundError(
                f"{self._training_dir} 下没有 DATA_*_TYPE*.mat 文件。检查 DATABASE.zip 是否解压"
            )
        return sig_files

    @property
    def bpmtrace_files(self) -> list[Path]:
        """返回对应的 12 个 BPMtrace ground-truth 文件,跟 subject_files 顺序一一对应。"""
        return [f.with_name(f.stem + "_BPMtrace.mat") for f in self.subject_files]

    @property
    def n_subjects(self) -> int:
        return len(self.subject_files)

    def load_subject(self, subject_id: int) -> dict[str, np.ndarray]:
        """加载第 subject_id 个 subject (1-indexed) 的信号 + BPM ground-truth.

        Returns:
            dict 含
              'ecg' (N,) — chest ECG (用于 sanity check, 不再做 truth)
              'ppg' (2, N) — 2-channel wrist PPG (绿光)
              'accel' (3, N) — 3-axis wrist accelerometer
              'bpm0' (n_windows,) — 官方 ground-truth, 每个对应一个 8s/2s window
        """
        if subject_id < 1 or subject_id > self.n_subjects:
            raise ValueError(f"subject_id {subject_id} 超范围 [1, {self.n_subjects}]")
        sig_path = self.subject_files[subject_id - 1]
        bpm_path = self.bpmtrace_files[subject_id - 1]

        sig = _load_mat(sig_path)  # (6, N)
        if sig.shape[0] != 6:
            sig = sig.T

        bpm0 = _load_mat(bpm_path).flatten()  # (n_windows,)

        return {
            "ecg": sig[0],
            "ppg": sig[1:3],
            "accel": sig[3:6],
            "bpm0": bpm0,
        }

    def windows_for_subject(self, subject_id: int) -> list[Window]:
        """切分一个 subject 的信号为 8 秒窗口,2 秒 shift。

        ground-truth HR 从官方 BPMtrace 直接读 (BPM0[k] 对应第 k 个 8s window)。
        """
        signals = self.load_subject(subject_id)
        n_samples = signals["ecg"].shape[0]
        bpm0 = signals["bpm0"]
        windows: list[Window] = []

        for w_idx, start in enumerate(range(0, n_samples - WINDOW_LEN + 1, SHIFT_LEN)):
            if w_idx >= len(bpm0):
                break  # BPM0 长度兜底 — 信号末尾不一定有对应 truth
            end = start + WINDOW_LEN
            ecg_w = signals["ecg"][start:end]
            ppg_w = signals["ppg"][:, start:end]
            accel_w = signals["accel"][:, start:end]
            hr_truth = float(bpm0[w_idx])
            if np.isnan(hr_truth) or hr_truth <= 0:
                continue
            windows.append(
                Window(
                    subject_id=subject_id,
                    window_idx=w_idx,
                    ppg=ppg_w,
                    accel=accel_w,
                    ecg=ecg_w,
                    hr_truth=hr_truth,
                )
            )
        return windows

    def all_windows(self) -> Iterator[Window]:
        """所有 subject 所有窗口的迭代器。"""
        for s_id in range(1, self.n_subjects + 1):
            yield from self.windows_for_subject(s_id)


def loso_folds(n_subjects: int) -> list[tuple[list[int], int]]:
    """Leave-One-Subject-Out folds.

    Returns:
        list of (train_subjects, test_subject), 1-indexed
    """
    return [
        (list(set(range(1, n_subjects + 1)) - {test}), test)
        for test in range(1, n_subjects + 1)
    ]


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Smoke-test IEEE SPC 2015 dataset loader")
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--subject", type=int, default=1)
    args = p.parse_args()

    ds = IEEESPC2015Dataset(args.data_dir)
    print(f"Found {ds.n_subjects} subjects in {ds.data_dir}")
    print(f"Files: {[f.name for f in ds.subject_files]}")

    print(f"\n=== Subject {args.subject} ===")
    sig = ds.load_subject(args.subject)
    print(f"  ECG shape: {sig['ecg'].shape}")
    print(f"  PPG shape: {sig['ppg'].shape}")
    print(f"  Accel shape: {sig['accel'].shape}")

    windows = ds.windows_for_subject(args.subject)
    print(f"\n  {len(windows)} windows extracted")
    if windows:
        w = windows[0]
        print(f"  First window HR: {w.hr_truth:.1f} BPM")
        hr_range = [w.hr_truth for w in windows]
        print(f"  HR range: {min(hr_range):.0f}–{max(hr_range):.0f} BPM")
