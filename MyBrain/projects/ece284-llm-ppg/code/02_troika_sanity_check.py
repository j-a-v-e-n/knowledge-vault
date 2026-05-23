"""02_troika_sanity_check.py — TROIKA-lite single-subject sanity check.

ECE 284 LLM-PPG project / Step B (2026-05-23).
- 跑 subject 01 TYPE01 全部窗口 → 打印 n_windows / n_nan / MAE
- 选 window index 50 (时间 100-108 s, 运动较强段) 画 3 张诊断图

不画完所有 subject, 不跑 LOSO; 那是 03_troika_loso.py 的事.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from data import load_subject
from troika_lite import (
    FS,
    WINDOW_SAMPLES,
    SHIFT_SAMPLES,
    HR_BAND_LOW,
    HR_BAND_HIGH,
    estimate_hr_one_window,
    run_subject,
)


SCRIPT_DIR = Path(__file__).parent
FIGS_DIR = SCRIPT_DIR / "figs"
FIGS_DIR.mkdir(exist_ok=True)


# ===================================================================
# Step 1: 跑 subject 01 全部窗口
# ===================================================================
SUBJ_ID = "01"
TYPE_ID = "01"
LAM = 1.0

print("=" * 62)
print(f"Step 1: run_subject({SUBJ_ID!r}, {TYPE_ID!r}, lam={LAM})")
print("=" * 62)

result = run_subject(SUBJ_ID, type_id=TYPE_ID, lam=LAM)

print()
print(f"subject ID:   {SUBJ_ID}  TYPE{TYPE_ID}")
print(f"n_windows:    {result['n_windows']}")
print(f"n_nan:        {result['n_nan']}")
print(f"MAE:          {result['mae']:.3f} BPM")


# ===================================================================
# Step 2: 选 window 50 (运动段) 拿 debug_dict
# ===================================================================
WINDOW_IDX = 50

print()
print("=" * 62)
print(f"Step 2: 诊断 window index {WINDOW_IDX} (时间 100-108 s)")
print("=" * 62)

# 重新 load 一次拿 sig + bpm0 (run_subject 内已经下载 cache, 这步无 IO 成本)
sig, bpm0 = load_subject(SUBJ_ID, TYPE_ID)

if WINDOW_IDX >= len(bpm0):
    raise ValueError(
        f"window index {WINDOW_IDX} out of range, bpm0 length={len(bpm0)}"
    )
assert WINDOW_IDX < len(bpm0), (
    f"window index {WINDOW_IDX} out of range, bpm0 length={len(bpm0)}"
)

start = WINDOW_IDX * SHIFT_SAMPLES
end = start + WINDOW_SAMPLES

ppg_window_raw = sig[1, start:end]                       # (1000,)
accel_window_raw = sig[3:6, start:end]                   # (3, 1000)
gt_hr = float(bpm0[WINDOW_IDX])
gt_freq_hz = gt_hr / 60.0

hr_est, debug = estimate_hr_one_window(
    ppg_window_raw, accel_window_raw, fs=FS, lam=LAM
)

print(f"window samples:    [{start}, {end})")
print(f"window time:       [{start/FS:.2f}, {end/FS:.2f}) s")
print(f"ground truth HR:   {gt_hr:.2f} BPM  ({gt_freq_hz:.4f} Hz)")
if np.isnan(hr_est):
    print("estimated HR:      NaN (no peak found)")
    est_label = "NaN"
else:
    print(f"estimated HR:      {hr_est:.2f} BPM  "
          f"({debug['peak_freq']:.4f} Hz)")
    est_label = f"{hr_est:.2f}"


# ===================================================================
# 诊断图通用 title 后缀
# ===================================================================
title_suffix = (
    f"subj {SUBJ_ID} TYPE{TYPE_ID} window {WINDOW_IDX}  "
    f"ground truth HR = {gt_hr:.2f} BPM  estimated HR = {est_label} BPM"
)


# ===================================================================
# Figure (a): bandpass diagnostic
# ===================================================================
time_axis = np.arange(WINDOW_SAMPLES) / FS + start / FS   # 绝对秒

fig_a, axes_a = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

axes_a[0].plot(time_axis, ppg_window_raw, color="#888888", linewidth=0.8)
axes_a[0].set_ylabel("Raw PPG ch1")
axes_a[0].set_title(f"PPG ch1 — raw vs bandpass-filtered\n{title_suffix}")
axes_a[0].grid(True, alpha=0.3)

axes_a[1].plot(time_axis, debug["ppg_filt"], color="#1a3a6b", linewidth=1.0)
axes_a[1].set_ylabel("Filtered PPG ch1\n(0.4-5 Hz Butter, filtfilt)")
axes_a[1].set_xlabel("Time (seconds)")
axes_a[1].grid(True, alpha=0.3)

fig_a.tight_layout()
fig_a_path = FIGS_DIR / "troika_diag_bandpass.png"
fig_a.savefig(fig_a_path, dpi=120)
plt.close(fig_a)
print(f"saved (a):  {fig_a_path}")


# ===================================================================
# Figure (b): FFT diagnostic (PPG + accel 频谱)
# ===================================================================
freqs = debug["freqs"]
ppg_power = debug["ppg_power"]
accel_power = debug["accel_power"]

# 限制到 0-10 Hz 显示
plot_mask = freqs <= 10.0
freqs_plot = freqs[plot_mask]
ppg_plot = ppg_power[plot_mask]
accel_plot = accel_power[plot_mask]

fig_b, axes_b = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

axes_b[0].plot(freqs_plot, ppg_plot, color="#1a3a6b", linewidth=1.0)
axes_b[0].axvspan(HR_BAND_LOW, HR_BAND_HIGH, alpha=0.15, color="#888888",
                  label=f"HR band [{HR_BAND_LOW}, {HR_BAND_HIGH}] Hz")
axes_b[0].set_ylabel("PPG PSD")
axes_b[0].set_title(f"PPG vs accel-magnitude PSD (periodogram, nfft=4096)\n"
                    f"{title_suffix}")
axes_b[0].legend(loc="upper right")
axes_b[0].grid(True, alpha=0.3)

axes_b[1].plot(freqs_plot, accel_plot, color="#cc4c54", linewidth=1.0)
axes_b[1].axvspan(HR_BAND_LOW, HR_BAND_HIGH, alpha=0.15, color="#888888",
                  label=f"HR band [{HR_BAND_LOW}, {HR_BAND_HIGH}] Hz")
axes_b[1].set_ylabel("Accel magnitude PSD")
axes_b[1].set_xlabel("Frequency (Hz)")
axes_b[1].set_xlim(0, 10)
axes_b[1].legend(loc="upper right")
axes_b[1].grid(True, alpha=0.3)

fig_b.tight_layout()
fig_b_path = FIGS_DIR / "troika_diag_fft.png"
fig_b.savefig(fig_b_path, dpi=120)
plt.close(fig_b)
print(f"saved (b):  {fig_b_path}")


# ===================================================================
# Figure (c): spectral subtraction (single overlay plot)
# ===================================================================
cleaned_power = debug["cleaned_power"]
cleaned_plot = cleaned_power[plot_mask]
coef = debug["coef"]
accel_scaled_plot = LAM * coef * accel_plot

fig_c, ax_c = plt.subplots(figsize=(10, 5))
ax_c.plot(freqs_plot, ppg_plot, color="#1a3a6b", linewidth=1.2,
          label="PPG PSD")
ax_c.plot(freqs_plot, accel_scaled_plot, color="#e08a2a", linewidth=1.2,
          label=f"accel PSD × λ × coef (λ={LAM}, coef={coef:.4f})")
ax_c.plot(freqs_plot, cleaned_plot, color="#2a9a3c", linewidth=1.5,
          label="cleaned = max(PPG − λ·coef·accel, 0)")

# HR band shading
ax_c.axvspan(HR_BAND_LOW, HR_BAND_HIGH, alpha=0.10, color="#888888",
             label=f"HR band [{HR_BAND_LOW}, {HR_BAND_HIGH}] Hz")

# Ground truth vertical line
ax_c.axvline(gt_freq_hz, color="black", linestyle="--", linewidth=1.2)
y_top = ax_c.get_ylim()[1]
ax_c.text(gt_freq_hz, y_top * 0.92,
          f"  Ground truth = {gt_hr:.2f} BPM",
          color="black", fontsize=9, ha="left", va="top")

# Estimated peak vertical line (only if a peak was found)
if not np.isnan(hr_est):
    peak_freq_hz = debug["peak_freq"]
    ax_c.axvline(peak_freq_hz, color="red", linestyle="--", linewidth=1.2)
    ax_c.text(peak_freq_hz, y_top * 0.78,
              f"  HR estimate = {hr_est:.2f} BPM",
              color="red", fontsize=9, ha="left", va="top")

# Coef annotation (top-left corner)
ax_c.text(0.02, 0.97, f"coef = {coef:.4f}",
          transform=ax_c.transAxes, fontsize=10, color="#333333",
          ha="left", va="top",
          bbox=dict(boxstyle="round,pad=0.3",
                    facecolor="white", edgecolor="#888888", alpha=0.85))

ax_c.set_xlabel("Frequency (Hz)")
ax_c.set_ylabel("Power")
ax_c.set_xlim(0, 10)
ax_c.set_title(f"Spectral subtraction (coef-normalized) — "
               f"PPG vs accel × λ × coef vs cleaned\n{title_suffix}")
ax_c.legend(loc="upper right", fontsize=8)
ax_c.grid(True, alpha=0.3)

fig_c.tight_layout()
fig_c_path = FIGS_DIR / "troika_diag_subtraction.png"
fig_c.savefig(fig_c_path, dpi=120)
plt.close(fig_c)
print(f"saved (c):  {fig_c_path}")


# ===================================================================
# Done
# ===================================================================
print()
print("=" * 62)
print("Sanity check done")
print("=" * 62)
print(f"subject:   {SUBJ_ID} TYPE{TYPE_ID}")
print(f"n_windows: {result['n_windows']}")
print(f"n_nan:     {result['n_nan']}")
print(f"MAE:       {result['mae']:.3f} BPM")
print(f"window {WINDOW_IDX}:  ground truth = {gt_hr:.2f} BPM, "
      f"estimated = {est_label} BPM")
print(f"figs:")
print(f"  (a) {fig_a_path}")
print(f"  (b) {fig_b_path}")
print(f"  (c) {fig_c_path}")
