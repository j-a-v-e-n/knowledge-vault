"""
01_load_and_plot.py — IEEE SPC 2015 Subject 01 TYPE01 数据加载 + 可视化

ECE 284 LLM-PPG project / setup Step 4 (2026-05-20).
功能: 下载 subject 01 TYPE01 的 .mat 文件 → 读 PPG/ECG/accel → 画两张图。
**不含任何 baseline 算法** (TROIKA / RF / LLM 都不在这里)。

Dataset source: Udacity nd320-c4 mirror of IEEE SPC 2015 (Zhang 2015 TROIKA paper).
"""

from pathlib import Path
import urllib.request

import numpy as np
import scipy.io
import matplotlib.pyplot as plt


# ===================================================================
# 路径配置 — script_dir / data / figs 都在 vault 内 code/ 目录下
# ===================================================================
SCRIPT_DIR = Path(__file__).parent           # .../ece284-llm-ppg/code/
DATA_DIR = SCRIPT_DIR / "data"               # .../code/data/
FIGS_DIR = SCRIPT_DIR / "figs"               # .../code/figs/

# mkdir -p (无害, exist_ok)
DATA_DIR.mkdir(exist_ok=True)
FIGS_DIR.mkdir(exist_ok=True)


# ===================================================================
# 数据集常量 (Zhang 2015 TROIKA / IEEE SPC 2015)
# ===================================================================
FS = 125                                # PPG/ECG/accel 采样率 Hz
WINDOW_SEC = 8                          # 滑窗长度 8 秒 (TROIKA paper 标准)
SHIFT_SEC = 2                           # 滑窗步长 2 秒
WINDOW_SAMPLES = FS * WINDOW_SEC        # 1000 samples / window
SHIFT_SAMPLES = FS * SHIFT_SEC          # 250 samples / shift

# BPM0[i] 对应 sig 的 sample range [i*SHIFT_SAMPLES, i*SHIFT_SAMPLES + WINDOW_SAMPLES)
# 时间 range  [2i, 2i+8) 秒, 窗口中心 = 2i+4 秒


# ===================================================================
# 数据下载源 (Udacity nd320-c4 mirror)
# ===================================================================
DATA_URL_BASE = (
    "https://github.com/udacity/nd320-c4-wearable-data-project-starter"
    "/raw/master/part_1/datasets/troika/training_data/"
)
DATA_FILE = "DATA_01_TYPE01.mat"        # 6×N 信号矩阵
REF_FILE = "REF_01_TYPE01.mat"          # W×1 ECG-derived HR ground truth


def download_if_missing(filename: str) -> Path:
    """Idempotent 下载: 文件在 code/data/ 已存在则 skip, 否则 GitHub fetch."""
    local_path = DATA_DIR / filename
    if local_path.exists():
        size_kb = local_path.stat().st_size / 1024
        print(f"[skip] {filename} already at {local_path} ({size_kb:.1f} KB)")
        return local_path
    url = DATA_URL_BASE + filename
    print(f"[download] {url}")
    print(f"          → {local_path}")
    urllib.request.urlretrieve(url, local_path)
    size_kb = local_path.stat().st_size / 1024
    print(f"[done]    {size_kb:.1f} KB written")
    return local_path


# ===================================================================
# Step 1: 下载两个 .mat 文件 (如未下过)
# ===================================================================
print("=" * 62)
print("Step 1: 下载 / verify 数据文件")
print("=" * 62)
data_path = download_if_missing(DATA_FILE)
ref_path = download_if_missing(REF_FILE)


# ===================================================================
# Step 2: 读 .mat 文件
# ===================================================================
print()
print("=" * 62)
print("Step 2: 读 .mat 文件")
print("=" * 62)

# DATA_01_TYPE01.mat 含 'sig' (6, N):
#   row 0 = ECG
#   row 1 = PPG ch1 (绿光)
#   row 2 = PPG ch2 (绿光, 另一通道)
#   row 3 = accelerometer X
#   row 4 = accelerometer Y
#   row 5 = accelerometer Z
data_mat = scipy.io.loadmat(data_path)
sig = data_mat["sig"]                                            # (6, N)

# 分通道引用 (不复制内存, 是 view)
ecg = sig[0, :]                                                  # (N,)
ppg_ch1 = sig[1, :]                                              # (N,)
ppg_ch2 = sig[2, :]                                              # (N,)
accel_xyz = sig[3:6, :]                                          # (3, N)

# 信号总长度统计
n_samples = sig.shape[1]
duration_sec = n_samples / FS
duration_min = duration_sec / 60.0

print(f"sig shape:        {sig.shape}  (6 channels × N samples)")
print(f"采样点数 N:       {n_samples}")
print(f"总时长:           {duration_sec:.2f} 秒  ({duration_min:.2f} 分钟)")

# REF_01_TYPE01.mat 含 'BPM0' (W, 1) ECG-derived HR ground truth
ref_mat = scipy.io.loadmat(ref_path)
bpm0 = ref_mat["BPM0"]                                           # (W, 1)
bpm0_flat = bpm0.flatten()                                       # (W,) 简化后续运算
n_windows = bpm0_flat.shape[0]

print(f"BPM0 shape:       {bpm0.shape}")
print(f"窗口数 W:         {n_windows}")
print(f"HR range:         min={bpm0_flat.min():.1f}  "
      f"max={bpm0_flat.max():.1f}  mean={bpm0_flat.mean():.1f}  BPM")

# 一致性 sanity check (不报错只 print):
# 窗口最后采样 idx = (W-1)*250 + 1000
expected_last_sample = (n_windows - 1) * SHIFT_SAMPLES + WINDOW_SAMPLES
print(f"窗口覆盖 samples: [0, {expected_last_sample})  "
      f"vs N={n_samples}  "
      f"({'match' if expected_last_sample <= n_samples else 'over!'})")


# ===================================================================
# Step 3: Figure 1 — PPG ch1 时域波形
# ===================================================================
print()
print("=" * 62)
print("Step 3: 画图")
print("=" * 62)

# 横轴: sample index → 秒
time_axis = np.arange(n_samples) / FS                            # (N,)

fig1, ax1 = plt.subplots(figsize=(14, 4))
ax1.plot(time_axis, ppg_ch1, linewidth=0.6, color="#1a3a6b")
ax1.set_xlabel("Time (seconds)")
ax1.set_ylabel("PPG ch1 amplitude")
ax1.set_title("Subject 01 TYPE01 — PPG channel 1 time-domain waveform")
ax1.set_xlim(0, duration_sec)
ax1.grid(True, alpha=0.3)
fig1.tight_layout()

fig1_path = FIGS_DIR / "subj01_type01_ppg_ch1.png"
fig1.savefig(fig1_path, dpi=120)
plt.close(fig1)
print(f"saved Fig 1:  {fig1_path}")


# ===================================================================
# Step 4: Figure 2 — ECG-derived HR (BPM0) 时间序列
# ===================================================================

# 每个窗口中心时间 = 2i + 4 秒 (window 在 [2i, 2i+8) 秒, 中点 2i+4)
window_centers_sec = 2 * np.arange(n_windows) + 4                # (W,)

fig2, ax2 = plt.subplots(figsize=(14, 4))
ax2.plot(window_centers_sec, bpm0_flat,
         marker="o", linewidth=1.0, markersize=3, color="#cc4c54")
ax2.set_xlabel("Window center time (seconds)")
ax2.set_ylabel("Heart Rate (BPM)")
ax2.set_title("Subject 01 TYPE01 — ECG-derived HR ground truth (BPM0)")
ax2.set_xlim(0, duration_sec)
ax2.grid(True, alpha=0.3)
fig2.tight_layout()

fig2_path = FIGS_DIR / "subj01_type01_hr_ground_truth.png"
fig2.savefig(fig2_path, dpi=120)
plt.close(fig2)
print(f"saved Fig 2:  {fig2_path}")


# ===================================================================
# Done
# ===================================================================
print()
print("=" * 62)
print("Done")
print("=" * 62)
print(f"Data dir:    {DATA_DIR}")
print(f"Figs dir:    {FIGS_DIR}")
print(f"Figure 1:    {fig1_path.name}")
print(f"Figure 2:    {fig2_path.name}")
