---
title: "Design A — Reliability-first 简单优先派"
date: 2026-05-12
agent: Plan (Opus)
agent_id: a64dbdb35e4e2129e
philosophy: 简单 / 5/7 deterministic / 不会跑歪
cost_per_day: $0.033
new_files: 5
build_time: 7 days
---

# Design A: Reliability-first Daily Wiki/AI Auto-Ingestion

## Core philosophy 一句话

ai-watch 已经做了"扫描 + 写早报"; 我只在它之上加一个 deterministic "diff → curate → append" 步骤, 把当天有沉淀价值的 item 用 fixed template 追加到 wiki 三个固定文件里, 100% append-only, fail-safe, 每天 < 5 LLM calls.

不重建 ingest pipeline. 不发明新 source list. 不引入 multi-agent. 只做 wiki 的"沉淀层" — 把 ai-watch 的 ephemeral 早报转成 wiki 的 cumulative knowledge.

## Architecture

```
[ 03:00 daemon ]
       |
       v
[ ai-watch SKILL ] ────► writes MyBrain/automation/reports/ai-watch/<date>.md   (已有, 不改)
       |
       v  (新增, daemon prompt.md 里加 1 行调用)
[ ai-ingest SKILL ]  ◄── 这个 design 的全部
       |
       ├─ 1. parse 今天的 ai-watch report (deterministic regex, 不调 LLM)
       ├─ 2. dedupe vs ledger.jsonl (URL hash, 不调 LLM)
       ├─ 3. classify item → bucket  (1 LLM call, Haiku, batch)
       ├─ 4. fetch primary source for each kept item  (WebFetch, no LLM)
       ├─ 5. extract structured row  (1 LLM call per item, Haiku, schema-locked)
       ├─ 6. reviewer pass — 数字 / 二手 / ranking gate  (1 LLM call, Sonnet, gate-only)
       └─ 7. append-only Edit 到 3 个 wiki 文件 + 写 ledger + cost log
       |
       v
[ MyBrain/wiki/AI/ ]
   ├─ papers.md       (论文; cumulative table)
   ├─ releases.md     (model / product release; cumulative table)
   └─ startups.md     (融资 / 产品 / team move; cumulative table)
```

总 phase 数 = 7, 但 **5/7 是 deterministic 无 LLM**. 真正的"AI 决策点"只有 3 个 LLM call (classify / extract / review).

## Multi-agent or single-agent?

**单 agent (single skill, 直接调 Haiku + Sonnet 各一次).**

为什么不上 multi-agent:
1. ROI 测算: 当前 ai-watch report 一天 ~15-25 item, dedupe + classify 后平均 3-5 个真正 ingest. 3 个 item 用 4 个 subagent 来回 orchestrate, overhead > 实际工作
2. Predictability 优先: 多 agent = 多 prompt = 多自由度 = 输出更随机
3. Cost ceiling: $0.30/day 预算下多 agent 直接超支
4. 现有 4 个 subagent 是为复杂调研任务设计, 本任务"小而高频"不是 sweet spot

唯一例外: review gate 用 Sonnet (不是 Haiku), 因为它是质量守门员, 但它就是一次 call, 不和别的 agent 来回.

## Cost breakdown / day

假设每天 5 个 item 通过 dedupe.

| Step | Model | Calls | Cost |
|---|---|---|---|
| Classify (batch 全部 ~20 item 一次) | Haiku 3.5 | 1 | $0.003 |
| Extract structured row (per item) | Haiku 3.5 | 5 | $0.014 |
| Review gate (batch 5 row 一次) | Sonnet 4.7 | 1 | $0.016 |
| WebFetch (primary source, 不算 LLM) | — | 5 | $0 |
| **Total** | | **7 LLM call** | **~$0.033/day** |

预算 $0.30, 实际 ~$0.033 = **预算 11%**. 留 89% buffer.

## 复用 vs 新建文件清单

**复用 (不动)**:
- `~/.claude-daemon/wrapper.sh`, `prompt.md` — 只在 prompt.md 加 1 行 "after ai-watch, run /ai-ingest"
- `.claude/skills/ai-watch/SKILL.md` — 不改
- `MyBrain/projects/ece284-llm-ppg/cost_tracker.py` — 直接 import 记 cost
- `MyBrain/automation/queue/approvals.md` — 不确定的 item 丢这里等 Javen 批
- git — 回滚机制

**新建 (5 个文件, 全部 < 100 行)**:
1. `.claude/skills/ai-ingest/SKILL.md` — skill 主文件, ~80 行 prompt
2. `.claude/skills/ai-ingest/schema.json` — 锁定 extract 输出 schema (~30 行)
3. `MyBrain/wiki/AI/papers.md` — table header + 空 body (首次 init)
4. `MyBrain/wiki/AI/releases.md` — 同上
5. `MyBrain/wiki/AI/startups.md` — 同上

**新建 state 文件 (auto-create on first run)**:
- `MyBrain/automation/state/ai-ingest/ledger.jsonl` — URL hash + ingest date
- `MyBrain/automation/state/ai-ingest/<date>.log` — 当天 run log

## Failure modes + 自动 handle

1. **ai-watch report 当天没生成 (上游 fail)** → ai-ingest 检测到文件不存在直接 exit 0
2. **WebFetch 拿不到 primary source** → 该 item 跳过, 不用二手 source 填
3. **LLM 返回的 JSON 不符合 schema** → 单 item retry 1 次, 还失败就跳过 + 写入 approvals.md
4. **数字 mismatch** → 该 item 拒收, 进 approvals.md
5. **Ranking label 出现但 source 不是 full data** → review gate 直接 reject
6. **Edit append 时 wiki 文件不存在** → skill 在 step 0 检查, 不存在则 abort
7. **同一 URL 之前 ingest 过** → ledger.jsonl 命中, dedupe 跳过
8. **当天 cost 超 $0.10** → cost_tracker.py callback 触发, skill 直接 exit
9. **Edit 写入失败 (网盘抖动)** → try/except, 全部 batch 失败则回滚 ledger
10. **网盘同步未完成** → wrapper.sh 已有 retry

**Rollback**: `git -C MyBrain checkout HEAD~1 -- wiki/AI/ automation/state/ai-ingest/ledger.jsonl` — 一行命令.

## Quality gate 设计 (今天 3 lessons 落地)

**Lesson 1 (二手 source 不可信)**:
- Extract step 强制 input = WebFetch 拿到的 primary source HTML/PDF, 不允许直接读 ai-watch report 的 summary
- ai-watch report 只用来"发现" URL list

**Lesson 2 (数字零容忍)**:
- schema.json 里所有数字字段类型 = `string` (不是 number), 强制保留原始格式
- Review gate prompt 显式: "字符级一致才 pass"

**Lesson 3 (真实性 > ranking)**:
- Schema 里 explicit 字段 `ranking_claim: string | null`
- 只有当 source 本身明确说 "best/SOTA/largest" 并附 full benchmark 才能填值

## 故意没做的 (trade-off)

1. 没做 embedding-based 语义 dedupe (只用 URL hash)
2. 没做 cross-day debate / theme aggregation (wiki 只是 "append daily new row")
3. 没做 dynamic topic discovery (3 个 bucket hardcode)
4. 没做 social media (Twitter / HN, 都是二手)
5. 没做 PDF 全文 ingest, 只 ingest abstract / TL;DR
6. 没做 auto-tag / auto-link
7. 没做 reviewer agent 模板 (review 直接 inline 在 SKILL.md prompt)

## 1 周 build timeline

| Day | 内容 |
|---|---|
| Day 1 | 创建 3 个空 wiki 文件 + skill 骨架 + state 目录 + smoke test |
| Day 2 | Deterministic 层 — URL extract + ledger dedupe + WebFetch + 失败跳过 |
| Day 3 | LLM 层 — Haiku classify + extract prompt + cost_tracker 集成 |
| Day 4 | Review gate — Sonnet prompt + reject → approvals.md 路径 |
| Day 5 | Wiki append 层 — 静态 template + 原子化 commit |
| Day 6 | Hook 进 daemon prompt.md + dry-run 一天 |
| Day 7 | Live + 监控 + runbook (rollback / 关闭 / 调试 命令) |

Total: 7 天, < 100 行 config + ~150 行 prompt.
