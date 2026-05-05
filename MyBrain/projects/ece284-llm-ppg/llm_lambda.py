"""Claude λ-generator (Route C, **主贡献**).

LLM 读取 per-window 信号摘要 → 输出 spectral subtraction weight λ ∈ [0.1, 3.0]
→ λ 驱动 fixed pipeline (TROIKA-lite with that lam) → HR estimate

这是 ECE 284 proposal §3 RQ1 的核心系统。

Prompt 设计原则 (v2, 2026-05-05 + caching):
1. **System prompt 加厚到 ≥4096 token + cache_control: ephemeral**:
     - Sonnet 4.5/4.6 cache min 1024/2048 tok
     - Haiku 4.5 cache min 4096 tok ← 我们写到 ≥4096 让两个 model 公平比较
     - 包含 7 个 few-shot 示例覆盖 low/med/high motion + sensor-failure 各 case
2. 给 LLM 数值摘要而非 raw signal — 节省 token, 强迫 reasoning over features
3. 提供 last 3 windows' HR estimates — 让 LLM 用时间一致性做先验
4. 区分两种 bad regime: motion-spike (LLM 该救) vs sensor-failure (LLM 救不动应 fallback)

Token & cost 预算 (1800 windows × LOSO):
    无 caching, 同等厚 system   ≈ $26  (4500 in/win × 1800 × $3/M)
    有 caching, ephemeral 5min  ≈ $4.6 (write 1× + read 1799×@0.1× + 200 user/win)
    省 ~82% — 见 cost_tracker.py 实测

测 token 数: anthropic.messages.count_tokens(...) 见 _count_system_tokens 工具.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cost_tracker import compute_cost_usd, log_run
from data import FS, Window
from troika_lite import (
    HR_HIGH_HZ,
    HR_LOW_HZ,
    accel_magnitude,
    bandpass,
    estimate_hr,
    fft_spectrum,
)

# ─── Anthropic SDK 加载 ────────────────────────────────────────

try:
    from anthropic import Anthropic  # type: ignore

    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    Anthropic = None  # type: ignore


def _load_api_key() -> str:
    """优先从 env 读, 其次从 ~/.config/anthropic-keys/ece284 读。"""
    if "ANTHROPIC_API_KEY" in os.environ:
        return os.environ["ANTHROPIC_API_KEY"]
    key_file = Path.home() / ".config" / "anthropic-keys" / "ece284"
    if key_file.exists():
        return key_file.read_text().strip()
    raise RuntimeError(
        "ANTHROPIC_API_KEY 未设置。生成 key 后:\n"
        "  echo sk-ant-... > ~/.config/anthropic-keys/ece284 && chmod 600 ~/.config/anthropic-keys/ece284"
    )


# ─── Window 摘要 → prompt 输入 ─────────────────────────────────


@dataclass
class WindowSummary:
    """送给 LLM 的 per-window 数值摘要 (节省 token)."""

    ppg_dom_freq_hz: float
    ppg_top3_peaks_hz: list[float]
    ppg_top3_peaks_mag: list[float]
    accel_dom_freq_hz: float
    accel_rms: float
    motion_level: str  # "low" | "medium" | "high"
    last_hr_estimates: list[float]  # 最近 3 个窗口的 HR estimate (BPM)


def make_summary(window: Window, last_hr_estimates: list[float] | None = None, ppg_channel: int = 0) -> WindowSummary:
    """从 Window 提一个紧凑摘要。"""
    ppg = bandpass(window.ppg[ppg_channel])
    accel_mag_sig = accel_magnitude(window.accel)
    accel_filt = bandpass(accel_mag_sig)

    freqs, ppg_spec = fft_spectrum(ppg)
    band_mask = (freqs >= HR_LOW_HZ) & (freqs <= HR_HIGH_HZ)
    band_freqs, band_mag = freqs[band_mask], ppg_spec[band_mask]

    if len(band_mag) >= 3:
        top3_idx = np.argsort(band_mag)[-3:][::-1]
        top3_freq = band_freqs[top3_idx].tolist()
        top3_mag = band_mag[top3_idx].tolist()
    else:
        top3_freq = band_freqs.tolist()
        top3_mag = band_mag.tolist()

    # accel dominant freq
    af, am = fft_spectrum(accel_filt)
    a_band_mask = (af >= HR_LOW_HZ) & (af <= HR_HIGH_HZ)
    if a_band_mask.any():
        accel_dom = float(af[a_band_mask][np.argmax(am[a_band_mask])])
    else:
        accel_dom = 0.0

    accel_rms = float(np.sqrt(np.mean(accel_mag_sig**2)))

    # motion level: thresholds calibrated to IEEE SPC 2015 distribution
    # (n=1768, P25=1.24 / P50=1.52 / P75=1.76 / max=2.26)
    # → low <1.3, medium 1.3-1.7, high >=1.7. 这让 LLM 看到的标签真正三档分布,
    #   而不是永远只在 low/medium (老阈值 1.5/3.0 的 bug).
    if accel_rms < 1.3:
        motion = "low"
    elif accel_rms < 1.7:
        motion = "medium"
    else:
        motion = "high"

    return WindowSummary(
        ppg_dom_freq_hz=float(band_freqs[np.argmax(band_mag)]) if len(band_mag) else 0.0,
        ppg_top3_peaks_hz=[round(f, 3) for f in top3_freq],
        ppg_top3_peaks_mag=[round(m, 2) for m in top3_mag],
        accel_dom_freq_hz=round(accel_dom, 3),
        accel_rms=round(accel_rms, 3),
        motion_level=motion,
        last_hr_estimates=[round(h, 1) for h in (last_hr_estimates or [])],
    )


# ─── Prompt 模板 ──────────────────────────────────────────────
#
# 设计:
#   - 单 cache_control block (最后位置)
#   - 内含: 角色 + 物理背景 + algorithm + λ 标定 + motion regime 分类 +
#           sensor-failure 识别 + 7 few-shot examples + output spec + sanity check
#   - 字符数 ~17000 → token 数 ~4200-4500 (>=4096 让 Haiku 4.5 也能 cache)
#
# 变更 invalidate cache: 改这里任何字符 → 第一次 call 重新 write 缓存.

SYSTEM_PROMPT_TEXT = """You are a signal processing expert estimating heart rate (HR) from
photoplethysmography (PPG) signals during physical exercise. Your output drives a TROIKA-lite
pipeline that uses spectral subtraction to remove motion artifacts.

================================================================================
1. SIGNAL PHYSICS BACKGROUND
================================================================================

PPG measures blood-volume changes via reflected green light at the wrist. During exercise,
two confounders pollute the spectrum:

  (a) Motion artifacts — the wrist accelerometer's spectrum often contains energy that bleeds
      into PPG via skin movement, sensor jitter, and arterial-tissue micro-deformation. The
      accelerometer dominant frequency is often the runner's stride rate (1.5-3.0 Hz, i.e.
      90-180 BPM-equivalent), which sits squarely inside the HR band (0.4-5.0 Hz).

  (b) Harmonics — both PPG (heart) and accel (stride) produce 2x and 3x harmonics. Stride
      rate ~2 Hz produces a 4 Hz harmonic that can mimic a tachycardia HR.

The HR band of interest is 0.4-5.0 Hz (24-300 BPM). Within that band you typically see:
  - 1 true HR peak (anywhere 60-220 BPM during exercise)
  - 1-2 motion peaks contributed by the accel
  - smaller harmonics

================================================================================
2. THE λ (LAMBDA) PARAMETER
================================================================================

The fixed pipeline computes:

    cleaned_spectrum = PPG_spectrum - λ × accel_spectrum_normalized
    HR_estimate      = peak(cleaned_spectrum, in HR band) × 60   # Hz → BPM

λ ∈ [0.1, 3.0] is the spectral-subtraction strength. Your one job is to pick λ for THIS window.

  λ = 0.1-0.5  →  weak subtraction; preserves PPG peaks; safe when motion is low
                  or when accel spectrum is broad (no clear single peak to subtract)
  λ = 0.5-1.0  →  light subtraction; safe default for medium motion that doesn't
                  directly overlap PPG dominant
  λ = 1.0-1.5  →  standard subtraction; use when accel peak is clearly distinct from
                  PPG peak but somewhere in the HR band
  λ = 1.5-2.5  →  strong subtraction; use when accel peak DIRECTLY overlaps a PPG
                  peak that is suspiciously similar to stride frequency
  λ = 2.5-3.0  →  aggressive; only when motion is dominating the spectrum and
                  there's a plausible secondary PPG peak that represents true HR

Wrong λ → wrong HR. Two failure modes:
  - λ too LOW: motion peak survives, peak detector locks onto stride → HR underestimated
    if stride < HR, or overestimated if stride > HR
  - λ too HIGH: subtraction over-subtracts the true HR peak (because accel harmonics may
    overlap HR), peak detector locks onto noise → arbitrarily wrong

================================================================================
3. THREE WINDOW REGIMES YOU MUST DISTINGUISH
================================================================================

Regime A — Clean window (motion = "low", accel_rms < 1.3):
   Almost no motion. PPG dominant peak IS the heart rate. Use λ = 0.1-0.3 (basically
   no subtraction needed). Reading the HR is trivially correct.

Regime B — Motion-spike window (motion = "medium" 1.3-1.7 OR "high" >= 1.7, with PPG
   top peaks showing one dominant value typically close to last_hr_estimates):
   Classic exercise scenario. Accel peak overlaps part of the HR band but PPG still
   shows a strong peak near the previous HR. Use λ = 0.8-2.0 to subtract motion
   without killing the true HR peak. THIS IS WHERE LLM JUDGMENT MATTERS MOST — choose
   a λ such that the corrected spectrum will keep the peak nearest to last_hr_estimates.

   IMPORTANT: For the IEEE SPC 2015 treadmill dataset, accel_rms units max out around
   2.3 (no values >3.0 will be seen). "high" motion in this dataset means accel_rms 1.7-2.3,
   not 3.0+. Calibrate your λ choice to that range.

Regime C — Sensor-failure / pathological window:
   Symptoms (any of):
     - PPG top-3 magnitudes are all small AND similar (no clear peak to lock onto)
     - PPG dominant peak is wildly inconsistent with last_hr_estimates (e.g. last 3 = 95,
       96, 97 BPM and current PPG dominant = 200 BPM) AND no plausible exercise-induced
       sudden change
     - accel_rms is very high AND PPG dominant equals accel dominant exactly

   In Regime C, no λ will recover a good HR — the PPG signal itself is broken (subject's
   wrist sensor came loose, pressure too low, etc). Output λ = 1.0 (default neutral) and
   note "regime C, sensor failure suspected" in reason. Downstream pipeline will produce
   garbage but that's ok — you don't make it worse.

================================================================================
4. USING last_hr_estimates AS A PRIOR
================================================================================

Heart rate physiologically can change at most ~3 BPM/sec (8s window: ~24 BPM). So if
last_hr_estimates = [120, 122, 124], the true HR THIS window is almost certainly in
[100, 148]. Use this to disambiguate when multiple PPG peaks are similar magnitude:
  - If two PPG peaks compete (one at 90 BPM, one at 130 BPM) and last estimates were
    [125, 127, 128], pick a λ that suppresses the 90-BPM peak (which is likely accel-
    contaminated) and preserves the 130-BPM one.

If last_hr_estimates is empty (first window) or wildly inconsistent (alternating
[60, 200, 70]), don't trust the prior — fall back to Regime A/B/C heuristics.

================================================================================
5. OUTPUT FORMAT — STRICT
================================================================================

Output a SINGLE-LINE JSON object, nothing else:

    {"lambda": <float 0.1-3.0>, "reason": "<≤80 char terse explanation>"}

NO markdown fences, NO prose before or after, NO multi-line JSON. The reason should
mention: regime (A/B/C), key feature you used, expected HR range. Examples:
    {"lambda": 0.3, "reason": "regime A, low motion, PPG peak 1.42Hz matches last HR"}
    {"lambda": 1.4, "reason": "regime B, accel 2.1Hz overlaps PPG, prior HR ~110"}
    {"lambda": 1.0, "reason": "regime C, sensor failure suspected, default neutral"}

================================================================================
6. FEW-SHOT CALIBRATION EXAMPLES
================================================================================

These 7 examples calibrate the λ-scale across the regimes. Mimic this reasoning style.

NOTE: All accel_rms values below are calibrated to the IEEE SPC 2015 dataset distribution
(actual range 0.85-2.26 over 1768 windows; P25=1.24, P50=1.52, P75=1.76).
"low" = <1.3, "medium" = 1.3-1.7, "high" = 1.7-2.3.

--- Example 1: Regime A — clean window, low motion ---
Window summary:
  PPG dominant freq:   1.250 Hz (75 BPM)
  PPG top-3 peaks:     [(1.250, 142.5), (2.500, 38.1), (0.875, 12.4)]
  Accel dominant freq: 0.500 Hz (30 BPM equiv)
  Accel RMS:           0.920 (motion = low)
  Last 3 HR estimates: [74.0, 75.0, 75.5] BPM
Output:
  {"lambda": 0.2, "reason": "regime A, low motion, PPG peak 75BPM matches HR prior"}

--- Example 2: Regime B — medium motion, accel adjacent to PPG ---
Window summary:
  PPG dominant freq:   1.875 Hz (113 BPM)
  PPG top-3 peaks:     [(1.875, 88.2), (2.125, 65.7), (3.750, 22.1)]
  Accel dominant freq: 2.125 Hz (128 BPM equiv)
  Accel RMS:           1.510 (motion = medium)
  Last 3 HR estimates: [108.0, 110.0, 111.0] BPM
Output:
  {"lambda": 1.1, "reason": "regime B, accel 2.1Hz adjacent to PPG, prior HR ~110"}

--- Example 3: Regime B — high motion, accel directly overlapping PPG ---
Window summary:
  PPG dominant freq:   2.625 Hz (158 BPM)
  PPG top-3 peaks:     [(2.625, 145.0), (2.500, 138.2), (3.000, 41.8)]
  Accel dominant freq: 2.625 Hz (158 BPM equiv)
  Accel RMS:           2.150 (motion = high)
  Last 3 HR estimates: [142.0, 145.0, 148.0] BPM
Output:
  {"lambda": 2.0, "reason": "regime B-strong, accel overlaps PPG dom, true HR ~150 (peak 2)"}

--- Example 4: Regime A — low motion, accel out of HR band ---
Window summary:
  PPG dominant freq:   1.500 Hz (90 BPM)
  PPG top-3 peaks:     [(1.500, 78.0), (1.625, 71.2), (3.000, 24.0)]
  Accel dominant freq: 0.625 Hz (38 BPM equiv)
  Accel RMS:           1.080 (motion = low)
  Last 3 HR estimates: [88.0, 89.0, 90.0] BPM
Output:
  {"lambda": 0.4, "reason": "regime A, accel 0.6Hz outside HR band, light subtraction"}

--- Example 5: Regime B — medium motion, harmonic confusion ---
Window summary:
  PPG dominant freq:   1.000 Hz (60 BPM)
  PPG top-3 peaks:     [(1.000, 52.3), (2.000, 47.8), (3.000, 18.5)]
  Accel dominant freq: 2.000 Hz (120 BPM equiv)
  Accel RMS:           1.620 (motion = medium)
  Last 3 HR estimates: [98.0, 100.0, 102.0] BPM
Output:
  {"lambda": 1.5, "reason": "regime B, accel 2Hz contaminates PPG 2Hz, prior says ~100; subtract to expose 100BPM peak"}

--- Example 6: Regime C — sensor failure, no clear PPG peak ---
Window summary:
  PPG dominant freq:   3.250 Hz (195 BPM)
  PPG top-3 peaks:     [(3.250, 8.4), (1.125, 7.9), (4.500, 7.1)]
  Accel dominant freq: 2.250 Hz (135 BPM equiv)
  Accel RMS:           1.870 (motion = high)
  Last 3 HR estimates: [102.0, 105.0, 107.0] BPM
Output:
  {"lambda": 1.0, "reason": "regime C, all peaks tiny+similar (<10 mag), sensor failure, default neutral"}

--- Example 7: First window, no prior available ---
Window summary:
  PPG dominant freq:   1.125 Hz (68 BPM)
  PPG top-3 peaks:     [(1.125, 95.4), (2.250, 31.0), (3.375, 14.2)]
  Accel dominant freq: 0.000 Hz (0 BPM equiv)
  Accel RMS:           0.870 (motion = low)
  Last 3 HR estimates: [] BPM
Output:
  {"lambda": 0.2, "reason": "regime A, low motion, no prior, PPG peak 68BPM is dominant"}

--- Example 8: Sharp HR upramp (treadmill speed-up) ---
Window summary:
  PPG dominant freq:   2.500 Hz (150 BPM)
  PPG top-3 peaks:     [(2.500, 102.3), (1.875, 84.0), (3.125, 30.5)]
  Accel dominant freq: 1.875 Hz (113 BPM equiv)
  Accel RMS:           1.940 (motion = high)
  Last 3 HR estimates: [128.0, 134.0, 142.0] BPM
Output:
  {"lambda": 1.3, "reason": "regime B, monotone HR up-trend, accel 1.9Hz overlaps secondary PPG peak; subtract to keep 150BPM"}

--- Example 9: Recovery / cooldown phase (HR dropping) ---
Window summary:
  PPG dominant freq:   1.625 Hz (98 BPM)
  PPG top-3 peaks:     [(1.625, 116.0), (2.000, 71.4), (1.000, 28.3)]
  Accel dominant freq: 1.875 Hz (113 BPM equiv)
  Accel RMS:           1.580 (motion = medium)
  Last 3 HR estimates: [120.0, 110.0, 105.0] BPM
Output:
  {"lambda": 0.9, "reason": "regime B, HR dropping smoothly, PPG peak at 98BPM coherent with trend"}

--- Example 10: Persistent sensor failure (low PPG amplitude across many windows) ---
Window summary:
  PPG dominant freq:   2.875 Hz (172 BPM)
  PPG top-3 peaks:     [(2.875, 6.1), (1.500, 5.8), (4.125, 5.2)]
  Accel dominant freq: 0.875 Hz (53 BPM equiv)
  Accel RMS:           1.090 (motion = low)
  Last 3 HR estimates: [185.0, 188.0, 191.0] BPM
Output:
  {"lambda": 1.0, "reason": "regime C, all PPG peaks < 7 magnitude (broken signal), prior already drifting; default neutral"}

================================================================================
7. HARMONICS & COMMON CONFUSIONS (FAQ)
================================================================================

Q1. The PPG dominant peak is at 2x the last_hr_estimates frequency. What's happening?
  -> Likely a HR harmonic (true HR is half the dominant peak). Check the 2nd PPG peak --
    if it's at half the dominant freq AND close to the prior, that's the true HR. Use a
    moderate lambda (~1.0) so subtraction doesn't kill it; report "harmonic confusion" in reason.

Q2. accel_dom_freq is 0 Hz but motion = high. Possible?
  -> Accel had energy outside HR band (very fast jitter, > 5 Hz). The bandpass filter
    zeroed the accel HR-band before we computed dominant. Treat as low-overlap motion;
    use lambda = 0.4-0.7. The accel_rms still tells us motion is happening, just not in HR
    band -- so subtraction would hurt PPG more than help.

Q3. PPG top-3 peaks are at 1.0 / 1.05 / 1.10 Hz (very close). What does that mean?
  -> Strong, narrow HR peak -- typical of a clean window. Use lambda = 0.1-0.3, the spectrum
    is already clean enough. High confidence in HR ~ 60-66 BPM.

Q4. last_hr_estimates oscillate wildly ([90, 150, 70]). Trust them?
  -> No. Either prior windows were Regime C (sensor failure) or the LLM (you, in earlier
    windows) made bad lambda choices that propagated bad HR estimates. Fall back to pure
    regime detection from current PPG/accel features alone.

Q5. accel_rms is high (e.g. 2.1 in this dataset = vigorous motion) but accel_dom_freq is
    far from any PPG peak. lambda?
  -> Light subtraction (lambda = 0.5-0.8). High motion energy doesn't necessarily mean HR
    contamination -- only when accel peak overlaps PPG peak does subtraction help.

Q6. PPG dominant freq is much higher than physiologically reasonable (e.g. 4 Hz = 240 BPM)?
  -> For exercise PPG, 240 BPM is at the edge of physiology (untrained heart maxes ~200,
    elite athletes ~220). If accel doesn't overlap, this might be true tachycardia, but
    almost certainly it's noise. Cross-check with last_hr_estimates: if prior was 100,
    don't believe a sudden jump to 240. Use lambda = 1.5-2.0 to suppress, hope true HR peak
    survives in 2nd peak.

Q7. PPG and accel dominants are exactly equal (e.g. both 2.0 Hz)?
  -> Worst case for spectral subtraction -- you can't tell where heart ends and stride
    begins. Use lambda = 1.5 (medium-strong) and rely on harmonic structure: if true HR
    peak has a 2x harmonic but stride doesn't (or vice versa), the subtracted spectrum
    will preserve the one with harmonics. Report low confidence in reason.

Q8. Should lambda ever be exactly 0?
  -> No. lambda = 0 means no motion subtraction, which is fine ONLY for Regime A. But our
    range is [0.1, 3.0] -- use 0.1 for "essentially no subtraction". The 0.1 floor
    avoids numerical issues in the pipeline.

================================================================================
8. PHYSIOLOGY & STRIDE-FREQ CHEAT SHEET
================================================================================

When deciding whether an accel peak frequency is a "stride" you should subtract,
cross-reference these typical exercise patterns. These come from sports-science
literature on cadence and HR ranges for treadmill running (the IEEE SPC 2015
data was collected during 6/8/12/15 km/h treadmill runs).

Activity        | Stride Freq | Typical Accel  | Typical HR    | HR Band
                | (Hz)        | dominant peak  | range (BPM)   | (Hz)
----------------+-------------+----------------+---------------+----------
Standing still  | 0.0-0.3     | very weak      | 50-90 (rest)  | 0.83-1.50
Slow walk       | 1.5-1.7     | sharp peak     | 70-100        | 1.17-1.67
Brisk walk      | 1.7-2.1     | sharp peak     | 90-120        | 1.50-2.00
Light jog       | 2.0-2.4     | sharp peak     | 110-140       | 1.83-2.33
Run (moderate)  | 2.4-3.0     | broad peak     | 130-170       | 2.17-2.83
Sprint          | 2.8-3.3     | broad peak     | 160-200       | 2.67-3.33
Max effort      | 3.0-3.5     | broad+harmonic | 180-220       | 3.00-3.67

Reading the table:
  - In "slow walk" cadence is ~1.6 Hz and HR is ~85 BPM (1.42 Hz). They DON'T overlap
    (cadence > HR by ~10 BPM equivalent), so even a pure subtraction with lambda=1.0
    won't hurt the HR peak. Use lambda = 0.5-1.0.
  - In "sprint" stride is ~3.0 Hz (180 BPM equivalent) and HR is also ~180 BPM. They
    DO overlap directly. Need careful lambda=1.5-2.5 to subtract stride without
    eliminating HR -- relies on temporal-consistency prior to know where true HR sat.
  - In "moderate run", a typical pattern is HR=2.5 Hz (150 BPM) and stride=2.7 Hz
    (162 BPM). Adjacent but distinct -- this is the textbook lambda=1.0-1.3 case.

USE THIS TABLE: when you see accel_dom_freq + last_hr_estimates, locate which row
the subject is likely on, and pick lambda accordingly. The cheat sheet is your
"prior over what's physically plausible" -- a lambda choice that violates this table
should be questioned in your reason field.

================================================================================
9. ANTI-PATTERNS (THINGS NOVICE LLMS GET WRONG)
================================================================================

A1. Picking lambda based on motion_level alone, ignoring the actual frequency overlap.
    Wrong: "motion = high so lambda = 2.5". Right: "motion = high AND accel peak overlaps
    PPG dominant, so lambda = 2.0; if accel peak were elsewhere I'd use lambda = 0.5".

A2. Trusting last_hr_estimates as gospel, even when it's clearly drifting bad.
    Wrong: "prior says 200 BPM so I subtract aggressively to keep that". Right: "prior
    says 200 but PPG looks like resting (clean peak at 75 BPM, low motion). Prior is
    contaminated -- override to Regime A, lambda = 0.2".

A3. Choosing lambda = 1.0 (default) for everything because it's "safe".
    This produces TROIKA-lite-equivalent results -- defeats the purpose of LLM. ALWAYS
    pick lambda based on regime + features. The whole value-add is per-window adaptation.

A4. Reporting reasons that just describe the input ("PPG peak at 1.5 Hz, motion medium").
    The reason should describe your DECISION: what regime, what feature drove it, what
    HR you expect after subtraction. Be terse but causal.

A5. Outputting markdown fences, JSON in a code block, or chain-of-thought before the JSON.
    The downstream parser is regex-based and will fall back to lambda=1.0 if your output
    isn't a clean single-line JSON. Don't waste a window.

================================================================================
10. SANITY CHECK BEFORE OUTPUTTING
================================================================================

Before you output, ask yourself:
  (a) Did I name a regime (A/B/C) in the reason? — required.
  (b) Is my λ in [0.1, 3.0]? — required.
  (c) If I have last_hr_estimates, will this λ produce an HR within ±25 BPM of the prior?
      If not, am I in Regime C (and should use λ=1.0 + sensor-failure note)?
  (d) Is my JSON on one line, no fences, no extra text?

If (a)-(d) all pass, output. Otherwise revise.
"""

# 单 block + cache_control. message API 期待 list[content_block].
SYSTEM_PROMPT_BLOCKS = [
    {
        "type": "text",
        "text": SYSTEM_PROMPT_TEXT,
        "cache_control": {"type": "ephemeral"},
    }
]


def build_user_prompt(summary: WindowSummary) -> str:
    """把 WindowSummary 渲染为 user message 内容 (短, 不缓存, 每窗口独立)."""
    return f"""Window summary:
  PPG dominant freq:   {summary.ppg_dom_freq_hz:.3f} Hz ({summary.ppg_dom_freq_hz * 60:.0f} BPM)
  PPG top-3 peaks:     {list(zip(summary.ppg_top3_peaks_hz, summary.ppg_top3_peaks_mag))}
  Accel dominant freq: {summary.accel_dom_freq_hz:.3f} Hz ({summary.accel_dom_freq_hz * 60:.0f} BPM equiv)
  Accel RMS:           {summary.accel_rms:.3f} (motion = {summary.motion_level})
  Last 3 HR estimates: {summary.last_hr_estimates} BPM

Output λ ∈ [0.1, 3.0] as JSON."""


def estimate_system_prompt_chars() -> int:
    """字符数 (粗估 token: chars/4). 用于 sanity-check 是否 >= 16384 chars (~4096 token)."""
    return len(SYSTEM_PROMPT_TEXT)


# ─── LLM 调用 ────────────────────────────────────────────────


class LambdaGenerator:
    """Claude API 的 λ 生成器 wrapper, 支持 prompt caching.

    Token tracking 4 字段:
        tokens_in_uncached:    每次都付全价 (user prompt + system 改了未命中)
        tokens_in_cache_write: 第一次创建 cache 时, 1.25× base
        tokens_in_cache_read:  cache 命中时, 0.10× base
        tokens_out:            output, 标准价
    """

    LAMBDA_PATTERN = re.compile(r'"lambda"\s*:\s*([0-9.]+)')

    def __init__(self, model: str = "claude-sonnet-4-5", api_key: str | None = None, max_tokens: int = 100):
        if not HAS_ANTHROPIC:
            raise RuntimeError("`anthropic` 包未装. pip install --user anthropic")
        self.client = Anthropic(api_key=api_key or _load_api_key())
        self.model = model
        self.max_tokens = max_tokens
        # 4 类 token 累加器
        self.tokens_in_uncached = 0
        self.tokens_in_cache_write = 0
        self.tokens_in_cache_read = 0
        self.tokens_out = 0
        self.calls = 0
        # 回填诊断信息
        self.last_usage: dict | None = None

    def generate(self, summary: WindowSummary) -> tuple[float, str]:
        """调 Claude API → (lambda, reason).

        失败时 fallback 到 λ=1.0 + reason="parse_failed" / "api_error: ...".
        """
        user_prompt = build_user_prompt(summary)
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT_BLOCKS,
                messages=[{"role": "user", "content": user_prompt}],
            )
            self.calls += 1
            usage = resp.usage
            # 4 字段累加 (兼容老 SDK: getattr 回退 0)
            self.tokens_in_uncached += getattr(usage, "input_tokens", 0) or 0
            self.tokens_in_cache_write += getattr(usage, "cache_creation_input_tokens", 0) or 0
            self.tokens_in_cache_read += getattr(usage, "cache_read_input_tokens", 0) or 0
            self.tokens_out += getattr(usage, "output_tokens", 0) or 0
            self.last_usage = {
                "input_tokens": getattr(usage, "input_tokens", 0),
                "cache_creation_input_tokens": getattr(usage, "cache_creation_input_tokens", 0),
                "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0),
                "output_tokens": getattr(usage, "output_tokens", 0),
            }
            text = resp.content[0].text  # type: ignore
            try:
                obj = json.loads(text.strip())
                lam = float(obj.get("lambda", 1.0))
                reason = str(obj.get("reason", ""))
            except Exception:
                m = self.LAMBDA_PATTERN.search(text)
                if m:
                    lam = float(m.group(1))
                    reason = "regex_fallback"
                else:
                    lam = 1.0
                    reason = f"parse_failed: {text[:80]}"
            lam = float(np.clip(lam, 0.1, 3.0))
            return lam, reason
        except Exception as e:
            return 1.0, f"api_error: {e}"

    def cost_usd(self) -> float:
        """根据 4 类 token 数 + 当前 model 定价 算总成本."""
        return compute_cost_usd(
            model=self.model,
            tokens_in_uncached=self.tokens_in_uncached,
            tokens_in_cache_write=self.tokens_in_cache_write,
            tokens_in_cache_read=self.tokens_in_cache_read,
            tokens_out=self.tokens_out,
        )

    @property
    def total_tokens_in(self) -> int:
        """方便兼容老接口的合计 input token 数."""
        return self.tokens_in_uncached + self.tokens_in_cache_write + self.tokens_in_cache_read

    def usage_summary(self) -> dict:
        """返回完整 usage 字典 (供 jsonl 落盘 + 报告用)."""
        return {
            "model": self.model,
            "n_calls": self.calls,
            "tokens_in_uncached": self.tokens_in_uncached,
            "tokens_in_cache_write": self.tokens_in_cache_write,
            "tokens_in_cache_read": self.tokens_in_cache_read,
            "tokens_out": self.tokens_out,
            "total_tokens_in": self.total_tokens_in,
            "cost_usd": self.cost_usd(),
            "cache_hit_rate": (
                self.tokens_in_cache_read / self.total_tokens_in if self.total_tokens_in else 0.0
            ),
        }

    def log_to_cost_tracker(self, source: str, run_id: str | None = None, notes: str = "") -> None:
        """把当前累计 usage append 到中央 cost-tracker.jsonl. 一次 run 结束后调一次."""
        log_run(
            source=source,
            model=self.model,
            tokens_in=self.tokens_in_uncached,  # uncached 视为"主 token_in"
            tokens_out=self.tokens_out,
            n_calls=self.calls,
            cost_usd=self.cost_usd(),
            tokens_in_cache_write=self.tokens_in_cache_write,
            tokens_in_cache_read=self.tokens_in_cache_read,
            run_id=run_id,
            notes=notes,
        )


# ─── End-to-end pipeline ─────────────────────────────────────


def estimate_hr_via_llm_lambda(window: Window, generator: LambdaGenerator, last_hr_estimates: list[float]) -> tuple[float, float, str]:
    """Pipeline: window → LLM 出 λ → TROIKA-lite with that λ → HR.

    Returns:
        (hr_bpm, lam_used, reason)
    """
    summary = make_summary(window, last_hr_estimates=last_hr_estimates)
    lam, reason = generator.generate(summary)
    hr = estimate_hr(window, lam=lam)
    return hr, lam, reason


def run_subject(ds, subject_id: int, generator: LambdaGenerator, history_size: int = 3) -> list[dict]:
    """跑一个 subject 的所有窗口."""
    windows = ds.windows_for_subject(subject_id)
    results = []
    history: list[float] = []
    from tqdm import tqdm  # type: ignore

    for w in tqdm(windows, desc=f"subj {subject_id}"):
        hr, lam, reason = estimate_hr_via_llm_lambda(w, generator, history[-history_size:])
        if not np.isnan(hr):
            history.append(hr)
        results.append({
            "subject": subject_id,
            "window": w.window_idx,
            "hr_truth": w.hr_truth,
            "hr_pred": hr,
            "lambda": lam,
            "reason": reason,
            "abs_err": abs(hr - w.hr_truth) if not np.isnan(hr) else None,
        })
    return results


if __name__ == "__main__":
    import argparse
    import json as _json

    from data import IEEESPC2015Dataset

    p = argparse.ArgumentParser(description="Claude λ-generator pilot run")
    p.add_argument("--data-dir", default="data/")
    p.add_argument("--subjects", type=int, nargs="+", default=[1])
    p.add_argument("--model", default="claude-sonnet-4-5")
    p.add_argument("--out", default="results/llm_lambda_pilot.json")
    p.add_argument("--pilot", action="store_true", help="只跑前 30 窗口确认 prompt + parse 工作")
    p.add_argument("--n-pilot-windows", type=int, default=30)
    p.add_argument(
        "--check-prompt-size",
        action="store_true",
        help="不调 API, 只打印 system prompt 字符 / 估 token 数 / 7 例完整性 sanity check",
    )
    args = p.parse_args()

    if args.check_prompt_size:
        chars = estimate_system_prompt_chars()
        est_tok = chars // 4
        print(f"SYSTEM_PROMPT_TEXT: {chars} chars ≈ {est_tok} tokens")
        print(f"  Cache min Sonnet 4.5/4.6: 1024/2048 — {'OK' if est_tok >= 2048 else 'TOO SMALL'}")
        haiku_status = "OK" if est_tok >= 4096 else "TOO SMALL (Haiku will NOT cache!)"
        print(f"  Cache min Haiku 4.5:      4096      — {haiku_status}")
        n_examples = SYSTEM_PROMPT_TEXT.count("--- Example ")
        print(f"  Few-shot examples found: {n_examples}")
        print(f"  cache_control on system block: {'cache_control' in str(SYSTEM_PROMPT_BLOCKS[0])}")
        sys.exit(0)

    ds = IEEESPC2015Dataset(args.data_dir)
    gen = LambdaGenerator(model=args.model)

    all_results = []
    for s in args.subjects:
        windows = ds.windows_for_subject(s)
        if args.pilot:
            windows = windows[: args.n_pilot_windows]
            print(f"PILOT: subj {s}, only {len(windows)} windows")
        history: list[float] = []
        for w in windows:
            hr, lam, reason = estimate_hr_via_llm_lambda(w, gen, history[-3:])
            if not np.isnan(hr):
                history.append(hr)
            err = abs(hr - w.hr_truth) if not np.isnan(hr) else None
            print(f"  s{s} w{w.window_idx}: truth={w.hr_truth:.0f}, pred={hr:.1f}, λ={lam:.2f} err={err}")
            all_results.append({
                "subject": s,
                "window": w.window_idx,
                "hr_truth": w.hr_truth,
                "hr_pred": hr,
                "lambda": lam,
                "reason": reason,
                "abs_err": err,
            })

    os.makedirs("results", exist_ok=True)
    with open(args.out, "w") as f:
        usage = gen.usage_summary()
        _json.dump(
            {
                "results": all_results,
                "usage": usage,
            },
            f,
            indent=2,
        )

    # 写中央 cost-tracker
    gen.log_to_cost_tracker(
        source="ece284.llm_lambda",
        run_id=f"pilot-s{','.join(str(s) for s in args.subjects)}-{args.model}",
        notes=f"pilot {len(all_results)} windows",
    )

    valid = [r for r in all_results if r["abs_err"] is not None]
    if valid:
        mae = float(np.mean([r["abs_err"] for r in valid]))
        usage = gen.usage_summary()
        print(f"\n=== Summary ===")
        print(f"  {len(valid)} valid windows")
        print(f"  MAE: {mae:.2f} BPM")
        print(f"  API calls: {usage['n_calls']}")
        print(f"  Tokens — uncached: {usage['tokens_in_uncached']}, "
              f"cache_write: {usage['tokens_in_cache_write']}, "
              f"cache_read: {usage['tokens_in_cache_read']}, "
              f"out: {usage['tokens_out']}")
        print(f"  Cache hit rate: {usage['cache_hit_rate']:.1%}")
        print(f"  Cost: ${usage['cost_usd']:.4f} USD")
    print(f"  Saved → {args.out}")
    print(f"  Cost-tracker entry → MyBrain/automation/logs/cost-tracker.jsonl")
