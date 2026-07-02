"""method_c_llm.py — Method C: LLM (DeepSeek-v4-flash) as per-window λ generator.

Pipeline diff vs Method A:
  - 完全沿用 Method A 的 bandpass + FFT + coupling_coef + spectral subtraction
    + tracking + self-correction 流程.
  - 唯一区别: λ 不是固定 1.0; DeepSeek 每窗看 (PPG top peaks, accel top peaks,
    motion intensity, coupling coef, recent HR/λ) 返回 λ ∈ [0.1, 3.0].

Cold start (前 N 个窗口):
  - 不调 LLM, λ=1.0
  - cold start 的 λ=1.0 也加入 recent_lambdas history, 保持 state 一致

LLM 调用:
  - openai SDK, base_url=https://api.deepseek.com, model=deepseek-v4-flash
  - response_format = {"type": "json_object"}
  - temperature=0.3, max_tokens=200
  - **thinking 显式禁用**: extra_body={"thinking": {"type": "disabled"}}
  - Retry 最多 2 次 (3 次 total attempts) for API error / timeout
  - Fallback chain:
      JSON parse fail / 缺 key → λ=1.0, reasoning='parse_fail', fallback_used=True
      All retries exhausted → λ=1.0, reasoning='api_fail', fallback_used=True
      λ 不在 [0.1, 3.0] → clamp (静默, 不算 fallback)
"""

import json
import os
import time
from collections import deque
from pathlib import Path

import numpy as np
from scipy.signal import periodogram, find_peaks

from dotenv import load_dotenv
from openai import OpenAI

from data import load_subject
from troika_lite import (
    FS,
    WINDOW_SAMPLES,
    SHIFT_SAMPLES,
    HR_BAND_LOW,
    HR_BAND_HIGH,
    NFFT,
    bandpass_filter,
    compute_coupling_coef,
    estimate_hr_one_window,
)


# ===================================================================
# .env 加载 (脚本所在目录的 .env, 不依赖 cwd)
# ===================================================================
load_dotenv(dotenv_path=Path(__file__).parent / ".env")


# ===================================================================
# DeepSeek API config
# ===================================================================
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"
TEMPERATURE = 0.3
MAX_TOKENS = 200

LAM_MIN = 0.1
LAM_MAX = 3.0
LAM_FALLBACK = 1.0

RECENT_HISTORY_LEN = 3


# ===================================================================
# System prompt (verbatim per spec)
# ===================================================================
SYSTEM_PROMPT = """You are a signal processing assistant for PPG heart rate estimation.

Given features from one 8-second window of a wrist PPG sensor, you decide the optimal lambda for spectral subtraction.

Pipeline context:
- A bandpass-filtered PPG window and accelerometer window are FFT'd.
- A coupling coefficient (least squares regression of PPG vs accel power in HR band) is computed.
- Spectral subtraction: cleaned_psd = max(ppg_psd - lambda * coupling_coef * accel_psd, 0)
- Then the strongest peak in [0.4, 5.0] Hz is taken as heart rate.

Lambda meaning:
- lambda = 0: no motion removal (accel ignored)
- lambda = 1: subtract estimated motion (default; assumes coupling_coef captures it exactly)
- lambda > 1: aggressively over-subtract (when motion in PPG is stronger than accel suggests)
- lambda < 1: gently under-subtract (when accel exaggerates the motion in PPG)

Your reasoning should:
- Identify motion presence (high accel_intensity, accel peak strength)
- Compare PPG top peaks vs accel top peaks for overlap
- Use recent HR history to verify HR continuity
- Decide if lambda should be larger (motion is dominant in PPG), smaller (motion seems minor), or near 1

Output strict JSON only (no other text). Both keys are required:
{
  "reasoning": "1-2 sentence reasoning",
  "lambda": <float in [0.1, 3.0]>
}"""


# ===================================================================
# Feature extraction
# ===================================================================
def _top3_peaks(power, freqs):
    """Top-3 peaks in HR band, sorted by power desc.

    Returns list of (freq_hz, power) tuples, length ≤ 3.
    No peaks → empty list.
    """
    band_mask = (freqs >= HR_BAND_LOW) & (freqs <= HR_BAND_HIGH)
    power_band = power[band_mask]
    freqs_band = freqs[band_mask]

    peaks, _ = find_peaks(power_band)
    if len(peaks) == 0:
        return []

    sorted_idx = np.argsort(power_band[peaks])[::-1]
    top = peaks[sorted_idx[:3]]
    return [(float(freqs_band[i]), float(power_band[i])) for i in top]


def extract_window_features(ppg_window, accel_xyz_window, prev_hrs,
                             prev_lambdas, fs=125):
    """Extract feature dict for LLM.

    Returns dict:
      ppg_top3_peaks:   list[(freq, power)]
      accel_top3_peaks: list[(freq, power)]
      accel_intensity:  float  (var of raw accel magnitude)
      coupling_coef:    float  (from troika_lite.compute_coupling_coef)
      recent_hrs:       list (up to 3 floats or None)
      recent_lambdas:   list (up to 3 floats)
    """
    # PPG bandpass + PSD
    ppg_filt = bandpass_filter(
        ppg_window, lowcut=HR_BAND_LOW, highcut=HR_BAND_HIGH, fs=fs
    )
    freqs, ppg_power = periodogram(ppg_filt, fs=fs, nfft=NFFT)

    # Accel magnitude + bandpass + PSD
    accel_mag = np.sqrt(np.sum(accel_xyz_window ** 2, axis=0))
    accel_intensity = float(np.var(accel_mag))
    accel_mag_filt = bandpass_filter(
        accel_mag, lowcut=HR_BAND_LOW, highcut=HR_BAND_HIGH, fs=fs
    )
    _, accel_power = periodogram(accel_mag_filt, fs=fs, nfft=NFFT)

    # Coupling coef (reuse from troika_lite, 不重写)
    coef = compute_coupling_coef(ppg_power, accel_power, freqs)

    return {
        "ppg_top3_peaks": _top3_peaks(ppg_power, freqs),
        "accel_top3_peaks": _top3_peaks(accel_power, freqs),
        "accel_intensity": accel_intensity,
        "coupling_coef": coef,
        "recent_hrs": list(prev_hrs),
        "recent_lambdas": list(prev_lambdas),
    }


# ===================================================================
# Build prompt
# ===================================================================
def _fmt_peaks(peaks):
    """[(1.8, 5300), ...] → '[(1.80, 5300.0), ...]'  or '[]' if empty."""
    if not peaks:
        return "[]"
    return "[" + ", ".join(f"({p[0]:.2f}, {p[1]:.1f})" for p in peaks) + "]"


def _fmt_history(values, formatter):
    """List with possible None → string '[N/A, 1.0, 2.0]'."""
    if not values:
        return "[]"
    return "[" + ", ".join(
        "N/A" if v is None else formatter(v)
        for v in values
    ) + "]"


def build_prompt(features):
    """Build (system_prompt, user_prompt) tuple from feature dict."""
    ppg_str = _fmt_peaks(features["ppg_top3_peaks"])
    accel_str = _fmt_peaks(features["accel_top3_peaks"])
    hrs_str = _fmt_history(features["recent_hrs"], lambda v: f"{v:.0f}")
    lams_str = _fmt_history(features["recent_lambdas"], lambda v: f"{v:.2f}")

    user_prompt = (
        "Window features:\n"
        "\n"
        f"PPG top-3 peaks (Hz, power): {ppg_str}\n"
        f"Accel top-3 peaks (Hz, power): {accel_str}\n"
        f"Accel intensity (variance): {features['accel_intensity']:.4f}\n"
        f"Coupling coefficient: {features['coupling_coef']:.1f}\n"
        "\n"
        f"Recent HR estimates (last 3 windows, oldest to newest): {hrs_str}\n"
        f"Recent lambda values (last 3 windows): {lams_str}\n"
        "\n"
        "What lambda do you recommend?"
    )
    return SYSTEM_PROMPT, user_prompt


# ===================================================================
# Call LLM
# ===================================================================
_client = None


def _get_client():
    """Lazy-init OpenAI client. Raises if DEEPSEEK_API_KEY missing or placeholder."""
    global _client
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key or api_key == "__USER_WILL_FILL_THIS__":
            raise RuntimeError(
                "DEEPSEEK_API_KEY missing or still placeholder. "
                "请先编辑 code/.env 填入真实 key."
            )
        _client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    return _client


def call_llm(system_prompt, user_prompt, retries=2):
    """Call DeepSeek API. Returns {lambda, reasoning, fallback_used}.

    Args:
        system_prompt: str
        user_prompt:   str
        retries:       max retry count on API error / timeout (default 2 → 3 total attempts)

    Fallback chain:
      - API error / timeout → retry, 用完仍失败 → λ=1.0, reasoning='api_fail', fallback_used=True
      - JSON parse fail OR 缺 'lambda'/'reasoning' key → λ=1.0, reasoning='parse_fail', fallback_used=True
      - λ 不在 [0.1, 3.0] → silently clamp (不算 fallback)
    """
    client = _get_client()

    for attempt in range(retries + 1):       # retries=2 → 3 attempts total
        # ---- API call ----
        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"},
                extra_body={"thinking": {"type": "disabled"}},
            )
        except Exception as e:
            if attempt < retries:
                time.sleep(1.0)
                continue
            return {
                "lambda": LAM_FALLBACK,
                "reasoning": f"api_fail: {type(e).__name__}",
                "fallback_used": True,
            }

        # ---- Parse JSON (no retry on parse fail; spec requires immediate fallback) ----
        content = response.choices[0].message.content or ""
        try:
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                raise ValueError("response not a dict")
            if "lambda" not in parsed or "reasoning" not in parsed:
                raise KeyError("missing 'lambda' or 'reasoning'")
            lam_raw = float(parsed["lambda"])
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            return {
                "lambda": LAM_FALLBACK,
                "reasoning": "parse_fail",
                "fallback_used": True,
            }

        # ---- Clamp λ silently ----
        lam = max(LAM_MIN, min(LAM_MAX, lam_raw))

        return {
            "lambda": lam,
            "reasoning": str(parsed["reasoning"]),
            "fallback_used": False,
        }

    # 不应到达 (循环已 return)
    return {
        "lambda": LAM_FALLBACK,
        "reasoning": "api_fail",
        "fallback_used": True,
    }


# ===================================================================
# Single-window driver (LLM-driven λ + method A pipeline)
# ===================================================================
def estimate_hr_one_window_with_llm(ppg_window, accel_xyz_window, prev_hr,
                                     prev_hrs_list, prev_lambdas,
                                     fs=125, max_jump_bpm=15,
                                     cold_start_active=False,
                                     energy_threshold=0.5):
    """Single-window HR estimation with LLM-driven λ.

    Returns:
        (hr_bpm, lambda_used, llm_resp_dict, debug_dict)
    """
    # a) Cold start → λ=1.0, 不调 LLM
    if cold_start_active:
        lam = 1.0
        llm_resp = {
            "lambda": 1.0,
            "reasoning": "cold_start",
            "fallback_used": False,
        }
    else:
        # b) extract features → build_prompt → call_llm
        features = extract_window_features(
            ppg_window, accel_xyz_window,
            prev_hrs_list, prev_lambdas, fs=fs,
        )
        sys_p, usr_p = build_prompt(features)
        llm_resp = call_llm(sys_p, usr_p, retries=2)
        lam = llm_resp["lambda"]

    # c+d) 用拿到的 λ 跑 method A spectral subtraction + tracking + self-correction
    hr, debug = estimate_hr_one_window(
        ppg_window, accel_xyz_window, fs=fs, lam=lam,
        prev_hr=prev_hr,
        max_jump_bpm=max_jump_bpm,
        cold_start_active=cold_start_active,
        energy_threshold=energy_threshold,
    )
    return hr, lam, llm_resp, debug


# ===================================================================
# Subject-level driver
# ===================================================================
def run_subject_methodC(subj_id, type_id, N=10, max_jump_bpm=15,
                         energy_threshold=0.5):
    """Run Method C over all windows of one subject.

    Returns dict:
      mae, hr_estimates, hr_truths, lambdas_used, llm_responses,
      n_windows, n_nan, n_fallback
    """
    sig, bpm0 = load_subject(subj_id, type_id)
    W = len(bpm0)

    hr_estimates = []
    lambdas_used = []
    llm_responses = []

    prev_hr = None
    recent_hrs = deque(maxlen=RECENT_HISTORY_LEN)
    recent_lambdas = deque(maxlen=RECENT_HISTORY_LEN)

    for i in range(W):
        start = i * SHIFT_SAMPLES
        end = start + WINDOW_SAMPLES
        if end > sig.shape[1]:
            # 越界 → 占位, 不更新 history
            hr_estimates.append(np.nan)
            lambdas_used.append(np.nan)
            llm_responses.append({
                "lambda": None,
                "reasoning": "out_of_range",
                "fallback_used": False,
            })
            continue

        cold_start_active = (i < N)
        hr, lam, llm_resp, _ = estimate_hr_one_window_with_llm(
            sig[1, start:end],
            sig[3:6, start:end],
            prev_hr=prev_hr,
            prev_hrs_list=list(recent_hrs),
            prev_lambdas=list(recent_lambdas),
            fs=FS,
            max_jump_bpm=max_jump_bpm,
            cold_start_active=cold_start_active,
            energy_threshold=energy_threshold,
        )

        hr_estimates.append(hr)
        lambdas_used.append(lam)
        llm_responses.append(llm_resp)

        # 更新 tracking 状态
        if not np.isnan(hr):
            prev_hr = hr

        # 关键: cold start 期间 λ=1.0 也加入 recent_lambdas, 保持 history 一致
        recent_hrs.append(hr if not np.isnan(hr) else None)
        recent_lambdas.append(lam)

    hr_truths = bpm0[:W].tolist()
    hr_est_arr = np.array(hr_estimates, dtype=float)
    hr_truth_arr = np.array(hr_truths, dtype=float)

    mae = float(np.nanmean(np.abs(hr_est_arr - hr_truth_arr)))
    n_nan = int(sum(1 for h in hr_estimates if np.isnan(h)))
    n_fallback = int(sum(
        1 for r in llm_responses if r.get("fallback_used") is True
    ))

    return {
        "mae": mae,
        "hr_estimates": hr_estimates,
        "hr_truths": hr_truths,
        "lambdas_used": lambdas_used,
        "llm_responses": llm_responses,
        "n_windows": int(W),
        "n_nan": n_nan,
        "n_fallback": n_fallback,
    }
