"""Claude λ-generator (Route C, **主贡献**).

LLM 读取 per-window 信号摘要 → 输出 spectral subtraction weight λ ∈ [0.1, 3.0]
→ λ 驱动 fixed pipeline (TROIKA-lite with that lam) → HR estimate

这是 ECE 284 proposal §3 RQ1 的核心系统。

Prompt 设计原则:
1. 给 LLM **数值摘要**而非 raw signal — 节省 token, 强迫 reasoning over features
2. 提供 last 3 windows' HR estimates — 让 LLM 用时间一致性做先验
3. Few-shot 用 oracle λ 标定一些代表性 case (hi/lo motion) — 校准 LLM 的 λ scale

Token 预算 (proposal §4):
- ~800 input + 50 output tokens / window
- 1800 windows × full LOSO ≈ 3M tokens, < $5 (Claude Sonnet)
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

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

    # motion level: simple heuristic 33/66 percentile splits
    if accel_rms < 1.5:
        motion = "low"
    elif accel_rms < 3.0:
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

SYSTEM_PROMPT = """You are a signal processing expert helping estimate heart rate (HR) \
from photoplethysmography (PPG) signals during exercise.

Your job: given a summary of one 8-second window, output a single number λ (lambda) \
in the range [0.1, 3.0]. This λ is the weight for spectral subtraction:

    cleaned_PPG_spectrum = PPG_spectrum - λ × accelerometer_spectrum

Then a peak detector finds the heart rate from the cleaned spectrum.

Guidelines:
- λ ≈ 0.5 if motion is mild or accel doesn't overlap with HR band → conservative subtraction
- λ ≈ 1.0–1.5 if motion is moderate and accel peak is near a PPG peak → standard subtraction
- λ ≈ 2.0–3.0 if motion is severe (high accel RMS) and accel peak overlaps PPG dominant → aggressive
- Use the last 3 HR estimates as a sanity check: if your λ would predict a wildly different HR, re-think

Output format: ONLY a JSON object on a single line, like:
    {"lambda": 1.2, "reason": "moderate motion, accel peak adjacent to second PPG peak"}

No prose, no markdown, no extra text."""


def build_user_prompt(summary: WindowSummary) -> str:
    """把 WindowSummary 渲染为 user message 内容."""
    return f"""Window summary:
  PPG dominant freq:   {summary.ppg_dom_freq_hz:.3f} Hz ({summary.ppg_dom_freq_hz * 60:.0f} BPM)
  PPG top-3 peaks:     {list(zip(summary.ppg_top3_peaks_hz, summary.ppg_top3_peaks_mag))}
  Accel dominant freq: {summary.accel_dom_freq_hz:.3f} Hz ({summary.accel_dom_freq_hz * 60:.0f} BPM equiv)
  Accel RMS:           {summary.accel_rms:.3f} (motion = {summary.motion_level})
  Last 3 HR estimates: {summary.last_hr_estimates} BPM

Output λ ∈ [0.1, 3.0] as JSON."""


# ─── LLM 调用 ────────────────────────────────────────────────


class LambdaGenerator:
    """Claude API 的 λ 生成器 wrapper."""

    LAMBDA_PATTERN = re.compile(r'"lambda"\s*:\s*([0-9.]+)')

    def __init__(self, model: str = "claude-sonnet-4-5", api_key: str | None = None, max_tokens: int = 100):
        if not HAS_ANTHROPIC:
            raise RuntimeError("`anthropic` 包未装. pip install --user anthropic")
        self.client = Anthropic(api_key=api_key or _load_api_key())
        self.model = model
        self.max_tokens = max_tokens
        self.tokens_in = 0
        self.tokens_out = 0
        self.calls = 0

    def generate(self, summary: WindowSummary) -> tuple[float, str]:
        """调 Claude API → (lambda, reason).

        失败时 fallback 到 λ=1.0 + reason="parse_failed".
        """
        user_prompt = build_user_prompt(summary)
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            self.calls += 1
            self.tokens_in += resp.usage.input_tokens
            self.tokens_out += resp.usage.output_tokens
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

    def cost_usd(self, in_per_mtok: float = 3.0, out_per_mtok: float = 15.0) -> float:
        """Sonnet pricing default. Haiku/Opus 调一下。"""
        return (self.tokens_in / 1_000_000 * in_per_mtok) + (self.tokens_out / 1_000_000 * out_per_mtok)


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
    args = p.parse_args()

    ds = IEEESPC2015Dataset(args.data_dir)
    gen = LambdaGenerator(model=args.model)

    all_results = []
    for s in args.subjects:
        windows = ds.windows_for_subject(s)
        if args.pilot:
            windows = windows[:30]
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
        _json.dump(
            {
                "results": all_results,
                "tokens_in": gen.tokens_in,
                "tokens_out": gen.tokens_out,
                "n_calls": gen.calls,
                "cost_usd": gen.cost_usd(),
            },
            f,
            indent=2,
        )
    valid = [r for r in all_results if r["abs_err"] is not None]
    if valid:
        mae = float(np.mean([r["abs_err"] for r in valid]))
        print(f"\n=== Summary ===")
        print(f"  {len(valid)} valid windows")
        print(f"  MAE: {mae:.2f} BPM")
        print(f"  API calls: {gen.calls}, tokens: {gen.tokens_in}+{gen.tokens_out}")
        print(f"  Cost: ${gen.cost_usd():.4f} USD")
    print(f"  Saved → {args.out}")
