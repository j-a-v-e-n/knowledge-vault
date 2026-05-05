"""中央 cost / token logger.

主对话 + daemon 凌晨任务都用这一个 entry-point 写 cost-tracker.jsonl。
跨源聚合后 Javen 一眼看清"今天 / 这周 / 这个月" Anthropic API 花了多少钱、哪个 source 烧得最多。

Usage:
    from cost_tracker import log_run

    log_run(
        source="ece284.llm_lambda",          # 谁调的
        model="claude-sonnet-4-5",           # 哪个 model
        tokens_in=350,                       # uncached 输入
        tokens_out=42,                       # 输出
        n_calls=1,                           # 这次 batch 调了几次
        cost_usd=0.0019,                     # 美刀
        # 可选额外字段
        tokens_in_cache_write=4112,
        tokens_in_cache_read=0,
        run_id="pilot-30win-sonnet",
        notes="prompt v1, cache miss (first call)",
    )

文件位置: MyBrain/automation/logs/cost-tracker.jsonl  (vault root 之外的脚本会找不到, 用绝对路径)

JSONL schema (每行一个 JSON object):
    {
      "ts": "2026-05-05T14:23:11-07:00",   # ISO 8601 with TZ
      "source": "ece284.llm_lambda",
      "model": "claude-sonnet-4-5",
      "tokens_in": 350,
      "tokens_out": 42,
      "n_calls": 1,
      "cost_usd": 0.0019,
      "tokens_in_cache_write": 4112,        # optional
      "tokens_in_cache_read": 0,            # optional
      "run_id": "pilot-30win-sonnet",       # optional
      "notes": "prompt v1...",              # optional
      ... (任意 extra kwargs)
    }
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# vault root 检测: 这个文件在 MyBrain/projects/ece284-llm-ppg/，往上数 3 层 = vault root
_VAULT_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_LOG_PATH = _VAULT_ROOT / "MyBrain" / "automation" / "logs" / "cost-tracker.jsonl"

# 允许 env override (e.g. daemon 想写到别处)
LOG_PATH = Path(os.environ.get("COST_TRACKER_LOG", str(_DEFAULT_LOG_PATH)))


# ─── Anthropic pricing 表 (per million tokens, 2026-05-05) ──────────────────
# 来源: https://platform.claude.com/docs/en/about-claude/pricing
# 4-tuple: (input_base, output, cache_write_5min_multiplier, cache_read_multiplier)
# cache_write_5min = base × 1.25, cache_read = base × 0.10
_PRICING_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    # base_input, base_output (cache 倍数硬编码 1.25 / 0.10)
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-opus-4-5": (15.0, 75.0),
    "claude-opus-4-7": (5.0, 25.0),
}

CACHE_WRITE_MULTIPLIER = 1.25  # 5-min ephemeral
CACHE_READ_MULTIPLIER = 0.10


def compute_cost_usd(
    model: str,
    tokens_in_uncached: int = 0,
    tokens_in_cache_write: int = 0,
    tokens_in_cache_read: int = 0,
    tokens_out: int = 0,
) -> float:
    """根据 4 类 token 数 + 当前定价表算总成本.

    未知 model 会 fallback 到 Sonnet 价格 + 打 warning.
    """
    if model not in _PRICING_USD_PER_MTOK:
        # warning to stderr, fallback Sonnet
        import sys

        print(f"[cost_tracker] WARN: unknown model {model!r}, fallback Sonnet pricing", file=sys.stderr)
        in_base, out_base = _PRICING_USD_PER_MTOK["claude-sonnet-4-5"]
    else:
        in_base, out_base = _PRICING_USD_PER_MTOK[model]

    cost = (
        tokens_in_uncached / 1_000_000 * in_base
        + tokens_in_cache_write / 1_000_000 * in_base * CACHE_WRITE_MULTIPLIER
        + tokens_in_cache_read / 1_000_000 * in_base * CACHE_READ_MULTIPLIER
        + tokens_out / 1_000_000 * out_base
    )
    return cost


def log_run(
    source: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    n_calls: int,
    cost_usd: float,
    log_path: str | Path | None = None,
    **extra: Any,
) -> Path:
    """append 一行 JSON 到 cost-tracker.jsonl.

    Args:
        source: 调用方标识, e.g. "ece284.llm_lambda" / "daemon.email_triage" / "ece175b.adg"
        model: model 名, e.g. "claude-sonnet-4-5"
        tokens_in: uncached 输入 token 数 (cached 部分用 extra kwargs 传)
        tokens_out: 输出 token 数
        n_calls: 这条 entry 涵盖几次 API 调用
        cost_usd: 总成本(美刀)
        log_path: optional override, 默认写 MyBrain/automation/logs/cost-tracker.jsonl
        **extra: 任意补充字段 (e.g. tokens_in_cache_write, run_id, notes)

    Returns:
        实际写入的文件路径
    """
    path = Path(log_path) if log_path else LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "source": source,
        "model": model,
        "tokens_in": int(tokens_in),
        "tokens_out": int(tokens_out),
        "n_calls": int(n_calls),
        "cost_usd": round(float(cost_usd), 6),
    }
    # 把任意 extra kwargs 也写进去 (cache token 字段 / run_id / notes / ...)
    for k, v in extra.items():
        if v is None:
            continue
        # 数字四舍五入,字符串/dict/list 直接写
        if isinstance(v, float):
            entry[k] = round(v, 6)
        else:
            entry[k] = v

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def summarize(log_path: str | Path | None = None, since_ts: str | None = None) -> dict:
    """读 cost-tracker.jsonl 汇总 by source / by model / total.

    Args:
        log_path: optional override
        since_ts: ISO timestamp, 只算 ts >= since 的 entry; None = 全部

    Returns:
        dict: {"total_cost_usd": ..., "by_source": {...}, "by_model": {...}, "n_entries": ...}
    """
    path = Path(log_path) if log_path else LOG_PATH
    if not path.exists():
        return {"total_cost_usd": 0.0, "by_source": {}, "by_model": {}, "n_entries": 0}

    by_source: dict[str, float] = {}
    by_model: dict[str, float] = {}
    total = 0.0
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if since_ts and e.get("ts", "") < since_ts:
                continue
            cost = float(e.get("cost_usd", 0.0))
            total += cost
            by_source[e.get("source", "?")] = by_source.get(e.get("source", "?"), 0.0) + cost
            by_model[e.get("model", "?")] = by_model.get(e.get("model", "?"), 0.0) + cost
            n += 1
    return {
        "total_cost_usd": round(total, 6),
        "by_source": {k: round(v, 6) for k, v in by_source.items()},
        "by_model": {k: round(v, 6) for k, v in by_model.items()},
        "n_entries": n,
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="cost_tracker.py CLI: write or summarize")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub_log = sub.add_parser("log", help="append a fake entry (smoke test)")
    sub_log.add_argument("--source", required=True)
    sub_log.add_argument("--model", default="claude-sonnet-4-5")
    sub_log.add_argument("--tokens-in", type=int, default=100)
    sub_log.add_argument("--tokens-out", type=int, default=20)
    sub_log.add_argument("--cost", type=float, default=0.0)
    sub_log.add_argument("--notes", default="")

    sub_sum = sub.add_parser("summary", help="print rollup of cost-tracker.jsonl")
    sub_sum.add_argument("--since", default=None, help="ISO ts, e.g. 2026-05-01")
    sub_sum.add_argument("--path", default=None)

    args = p.parse_args()

    if args.cmd == "log":
        out = log_run(
            source=args.source,
            model=args.model,
            tokens_in=args.tokens_in,
            tokens_out=args.tokens_out,
            n_calls=1,
            cost_usd=args.cost,
            notes=args.notes,
        )
        print(f"appended → {out}")
    elif args.cmd == "summary":
        s = summarize(log_path=args.path, since_ts=args.since)
        print(json.dumps(s, indent=2))
