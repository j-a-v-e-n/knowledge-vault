"""Mock test: 验证 prompt caching 4 字段 token tracking + cost 算法.

不需要 ANTHROPIC_API_KEY. 用 unittest.mock 替换 Anthropic client, 模拟
两次调用:
  Call 1 (cache write): cache_creation_input_tokens 大, cache_read 0
  Call 2 (cache read):  cache_creation_input_tokens 0, cache_read 大

确认:
  1. LambdaGenerator 4 字段累加器对
  2. cost_usd() 用 1.25× / 0.10× / 1× 三档定价对
  3. usage_summary() 输出 cache_hit_rate
  4. log_to_cost_tracker() 写 jsonl 含 tokens_in_cache_write / read 字段
  5. caching 前后总成本对比 (vs 同等厚 system 不 cache)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# 确保我们能 import 当前目录
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cost_tracker
from cost_tracker import compute_cost_usd
from llm_lambda import (
    SYSTEM_PROMPT_BLOCKS,
    SYSTEM_PROMPT_TEXT,
    LambdaGenerator,
    WindowSummary,
    build_user_prompt,
    estimate_system_prompt_chars,
)


def make_mock_response(
    input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    cache_read_input_tokens: int = 0,
    output_tokens: int = 0,
    text: str = '{"lambda": 1.2, "reason": "regime B mock"}',
):
    """造一个 Anthropic SDK style response object."""
    resp = MagicMock()
    resp.usage.input_tokens = input_tokens
    resp.usage.cache_creation_input_tokens = cache_creation_input_tokens
    resp.usage.cache_read_input_tokens = cache_read_input_tokens
    resp.usage.output_tokens = output_tokens
    resp.content = [MagicMock(text=text)]
    return resp


def test_system_prompt_meets_haiku_cache_min():
    """SYSTEM_PROMPT_TEXT 应当 >= 4096 token 估算 (chars / 4)."""
    chars = estimate_system_prompt_chars()
    est_tok = chars // 4
    assert est_tok >= 4096, f"system prompt {est_tok} tok < Haiku 4096 cache min"
    n_examples = SYSTEM_PROMPT_TEXT.count("--- Example ")
    assert n_examples >= 7, f"need >=7 few-shot examples, got {n_examples}"
    assert "cache_control" in str(SYSTEM_PROMPT_BLOCKS[0])
    print(f"[OK] system prompt: {chars} chars / ~{est_tok} tok / {n_examples} few-shot examples")


def test_4field_token_tracking_and_cache_hit_rate():
    """模拟 1 次 cache_write + 9 次 cache_read 调用. 验证累加器 + hit rate 对."""
    summary = WindowSummary(
        ppg_dom_freq_hz=1.5, ppg_top3_peaks_hz=[1.5, 2.0, 3.0],
        ppg_top3_peaks_mag=[100.0, 50.0, 20.0],
        accel_dom_freq_hz=2.0, accel_rms=2.5, motion_level="medium",
        last_hr_estimates=[100.0, 102.0, 105.0],
    )

    with patch("llm_lambda.Anthropic") as mock_anthropic:
        # mock client: 第 1 次 cache write, 后 9 次 cache read
        mock_client = MagicMock()
        responses = [
            make_mock_response(
                input_tokens=180,                 # user prompt (uncached)
                cache_creation_input_tokens=4500, # 写缓存
                cache_read_input_tokens=0,
                output_tokens=42,
            ),
        ] + [
            make_mock_response(
                input_tokens=180,                 # user prompt (uncached)
                cache_creation_input_tokens=0,
                cache_read_input_tokens=4500,     # 命中缓存
                output_tokens=42,
            )
            for _ in range(9)
        ]
        mock_client.messages.create.side_effect = responses
        mock_anthropic.return_value = mock_client

        # 绕过 _load_api_key
        gen = LambdaGenerator(model="claude-sonnet-4-5", api_key="sk-ant-fake")
        for _ in range(10):
            lam, reason = gen.generate(summary)

    usage = gen.usage_summary()
    print(f"\n[Test 2] 4-field token tracking after 10 calls (1 write + 9 reads):")
    print(f"  uncached:    {usage['tokens_in_uncached']}     (expect 1800 = 10 × 180)")
    print(f"  cache_write: {usage['tokens_in_cache_write']}  (expect 4500)")
    print(f"  cache_read:  {usage['tokens_in_cache_read']}   (expect 40500 = 9 × 4500)")
    print(f"  out:         {usage['tokens_out']}            (expect 420 = 10 × 42)")
    print(f"  hit rate:    {usage['cache_hit_rate']:.1%}    (expect ~85.7%)")

    assert usage["tokens_in_uncached"] == 1800
    assert usage["tokens_in_cache_write"] == 4500
    assert usage["tokens_in_cache_read"] == 40500
    assert usage["tokens_out"] == 420
    # hit rate = 40500 / (1800 + 4500 + 40500) = 40500 / 46800 = 0.8654
    assert 0.86 < usage["cache_hit_rate"] < 0.87

    # cost 算法验证: Sonnet 4.5 = $3 in / $15 out
    expected_cost = (
        1800 / 1_000_000 * 3.0
        + 4500 / 1_000_000 * 3.0 * 1.25      # cache_write
        + 40500 / 1_000_000 * 3.0 * 0.10     # cache_read
        + 420 / 1_000_000 * 15.0
    )
    assert abs(usage["cost_usd"] - expected_cost) < 1e-6, f"cost mismatch: {usage['cost_usd']} vs {expected_cost}"
    print(f"  cost_usd:    ${usage['cost_usd']:.6f}  (expect ${expected_cost:.6f})  [OK]")


def test_cost_tracker_log_run():
    """验证 log_run 写出 jsonl 含所有必要字段."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        cost_tracker.log_run(
            source="test.mock",
            model="claude-sonnet-4-5",
            tokens_in=1800,
            tokens_out=420,
            n_calls=10,
            cost_usd=0.0234,
            log_path=tmp_path,
            tokens_in_cache_write=4500,
            tokens_in_cache_read=40500,
            run_id="mock-pilot-test",
            notes="cache hit rate 85.7%",
        )
        with tmp_path.open() as f:
            line = f.readline().strip()
            entry = json.loads(line)
        print(f"\n[Test 3] cost-tracker.jsonl entry:")
        print(f"  {json.dumps(entry, indent=2)}")
        assert entry["source"] == "test.mock"
        assert entry["model"] == "claude-sonnet-4-5"
        assert entry["tokens_in_cache_write"] == 4500
        assert entry["tokens_in_cache_read"] == 40500
        assert entry["run_id"] == "mock-pilot-test"
        assert entry["notes"] == "cache hit rate 85.7%"
        assert "ts" in entry
        print(f"  [OK] all 4 token fields written, ts present, source/model/run_id correct")
    finally:
        tmp_path.unlink(missing_ok=True)


def test_caching_savings_vs_no_cache():
    """对比 1800 windows × LOSO: cache vs no-cache 同等 system 厚度.

    打印实际省钱比例 → 跟 Javen 任务卡里 73% 数字对比.
    """
    n_windows = 1800
    system_tok = 4500       # 我们的厚 system + few-shot
    user_per_window = 180   # short user prompt
    output_per_window = 50  # JSON output

    # 无 caching: 每次都付全 system + user 价
    no_cache_cost = compute_cost_usd(
        model="claude-sonnet-4-5",
        tokens_in_uncached=(system_tok + user_per_window) * n_windows,
        tokens_out=output_per_window * n_windows,
    )

    # 有 caching: 1 次 write + (N-1) 次 read, user prompt 仍 uncached
    cache_cost = compute_cost_usd(
        model="claude-sonnet-4-5",
        tokens_in_uncached=user_per_window * n_windows,
        tokens_in_cache_write=system_tok,
        tokens_in_cache_read=system_tok * (n_windows - 1),
        tokens_out=output_per_window * n_windows,
    )

    saving_pct = (1 - cache_cost / no_cache_cost) * 100
    print(f"\n[Test 4] 1800-window LOSO cost projection (Sonnet 4.5, 4500-tok system):")
    print(f"  No caching:  ${no_cache_cost:.2f}")
    print(f"  Caching:     ${cache_cost:.2f}")
    print(f"  Saving:      {saving_pct:.1f}%")

    # 同 system 厚 + cache 应该省 >= 75%
    assert saving_pct >= 75.0, f"caching should save >=75%, got {saving_pct:.1f}%"

    # 同 baseline: 假设无 caching 但用薄 system (现 200 tok)
    thin_system_cost = compute_cost_usd(
        model="claude-sonnet-4-5",
        tokens_in_uncached=(200 + user_per_window) * n_windows,
        tokens_out=output_per_window * n_windows,
    )
    print(f"\n  vs THIN system no-cache baseline (200-tok system):")
    print(f"    Thin no-cache:   ${thin_system_cost:.2f}")
    print(f"    Thick + cache:   ${cache_cost:.2f}  (delta ${cache_cost - thin_system_cost:+.2f})")
    print(f"    For ~${cache_cost - thin_system_cost:.2f} extra per LOSO run, we get 22× richer prompt + few-shot calibration")
    return {
        "no_cache_cost": no_cache_cost,
        "cache_cost": cache_cost,
        "saving_pct": saving_pct,
        "thin_no_cache_cost": thin_system_cost,
    }


def test_haiku_pricing_correct():
    """Haiku 4.5 base $1/$5 per Mtok. 验证定价表."""
    cost = compute_cost_usd(
        model="claude-haiku-4-5",
        tokens_in_uncached=1_000_000,
        tokens_out=1_000_000,
    )
    expected = 1.0 + 5.0
    assert abs(cost - expected) < 1e-6, f"Haiku cost wrong: {cost} vs {expected}"
    print(f"\n[Test 5] Haiku 4.5 pricing: ${cost:.2f} per 1M in + 1M out (expect $6.00)  [OK]")


if __name__ == "__main__":
    print("=" * 70)
    print("MOCK TEST: prompt caching wiring (no ANTHROPIC_API_KEY needed)")
    print("=" * 70)

    test_system_prompt_meets_haiku_cache_min()
    test_4field_token_tracking_and_cache_hit_rate()
    test_cost_tracker_log_run()
    proj = test_caching_savings_vs_no_cache()
    test_haiku_pricing_correct()

    print("\n" + "=" * 70)
    print("ALL 5 TESTS PASSED")
    print("=" * 70)
    print("\n下一步: 等 ANTHROPIC_API_KEY 后跑")
    print("  python3 llm_lambda.py --subjects 1 --pilot --n-pilot-windows 30 --model claude-sonnet-4-5")
    print(f"\n实际成本预期 (1800-window LOSO, Sonnet 4.5):")
    print(f"  No cache: ${proj['no_cache_cost']:.2f}")
    print(f"  Cache:    ${proj['cache_cost']:.2f}  (save {proj['saving_pct']:.0f}%)")
