"""Claude ReAct orchestrator (Route D, **stretch goal** for RQ2).

按 proposal §4: LLM dynamically chooses tool call sequence per window.
Tool library 跟 λ-generator 共享 (bandpass_filter, compute_fft, compute_accel_magnitude,
find_peaks, spectral_subtract).

**这是 Week 9 任务。Week 7-8 主线 (TROIKA + RF + λ) 跑完才动。**

用 Anthropic 的 tool_use API:
- 5 个 tool 定义, 每个对应 troika_lite.py 里的一个函数
- LLM 一个 window 里可以多次调用工具, 最后返回 final HR estimate
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np

# 为 daemon / Javen 早起接续:
# - 主对话 (我) 此次只放 stub. Week 8 跑完主线 RQ1 后, 由主对话或 daemon
#   在 task-018 子任务 h 启动时把这个 stub 填实.
# - 工具定义参考 anthropic.com/api/tool-use docs

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "bandpass_filter",
        "description": "Apply a Butterworth bandpass filter to a 1D signal. Default 0.4-5 Hz HR band.",
        "input_schema": {
            "type": "object",
            "properties": {
                "signal_id": {"type": "string", "description": "ID of signal to filter (e.g., 'ppg_ch0')"},
                "low_hz": {"type": "number", "default": 0.4},
                "high_hz": {"type": "number", "default": 5.0},
            },
            "required": ["signal_id"],
        },
    },
    {
        "name": "compute_fft",
        "description": "Compute single-sided FFT magnitude spectrum.",
        "input_schema": {
            "type": "object",
            "properties": {"signal_id": {"type": "string"}},
            "required": ["signal_id"],
        },
    },
    {
        "name": "compute_accel_magnitude",
        "description": "Compute 3-axis accelerometer magnitude.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "find_peaks",
        "description": "Find peaks in a spectrum, return top-K by magnitude.",
        "input_schema": {
            "type": "object",
            "properties": {
                "spectrum_id": {"type": "string"},
                "k": {"type": "integer", "default": 3},
            },
            "required": ["spectrum_id"],
        },
    },
    {
        "name": "spectral_subtract",
        "description": "Subtract weighted accel spectrum from PPG spectrum (cleaned = ppg - λ × accel).",
        "input_schema": {
            "type": "object",
            "properties": {
                "ppg_spectrum_id": {"type": "string"},
                "accel_spectrum_id": {"type": "string"},
                "lambda": {"type": "number"},
            },
            "required": ["ppg_spectrum_id", "accel_spectrum_id", "lambda"],
        },
    },
    {
        "name": "report_hr",
        "description": "Final tool: report estimated HR in BPM.",
        "input_schema": {
            "type": "object",
            "properties": {"hr_bpm": {"type": "number"}},
            "required": ["hr_bpm"],
        },
    },
]


SYSTEM_PROMPT_REACT = """You are a signal processing agent estimating heart rate from \
a noisy PPG window during exercise. You have access to 6 tools. Use them in any order to \
clean the signal and find HR. End by calling report_hr with your final estimate."""


def run_react_window(window, client) -> dict:
    """跑单个窗口的 ReAct loop. STUB — Week 9 填实."""
    raise NotImplementedError(
        "ReAct agent is Week 9 stretch goal. 主线 RQ1 跑完后启动 task-018 子任务 h."
    )


if __name__ == "__main__":
    print("react_agent.py — stretch goal, Week 9 启动")
    print(f"  Tool library defined: {len(TOOL_DEFINITIONS)} tools")
    print("  Status: STUB — implement after Week 8 (主线 LOSO done)")
