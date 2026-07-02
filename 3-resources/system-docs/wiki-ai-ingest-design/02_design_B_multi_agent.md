---
title: "Design B — Multi-agent Sophisticated 派"
date: 2026-05-12
agent: Plan (Opus)
agent_id: ad6209fb1680a8938
philosophy: RLHF-style adversarial / 3-angle research / 物理隔离 self-confirmation bias
cost_per_day: $1.30
new_files: 8-10
build_time: ~2 weeks
---

# Design B: Multi-agent Sophisticated Daily Wiki/AI Ingestion

## Core philosophy

**Quality through adversarial redundancy.** 不是"一个 agent 把活干完", 是**"多个 agent 从不同 angle 攻同一个 item, 让冲突显式化, 再用 judge gate 收敛"**. AI 行业每天都有新 paper / startup / release——如果 ingest 系统**一个 angle 看完就落 vault**, 今天那 3 条 quality lesson (二手 source / 数字零容忍 / 真实性 > 一切) 就会**被违反**, 因为 single-pass agent 看不见自己的 blind spot.

**比 ai-watch 高一个 quality tier**: ai-watch 是 broadcast (600 字早报), 本系统是 **wiki ingestion** (永久 vault asset, 跟 Garg_2025_DopFone 同级). Wiki 进得去就得跟 ECE284 paper 一样精度. **生产级 cost ($1.50/day) 买的是这个 tier 跳跃**.

**关键 mental model**: 这是 Anthropic 自己 RLHF data pipeline 的形态——**多个 labeler 独立给 label, judge model 收敛分歧, reject 低 agreement item**.

## Architecture

```
PHASE 0: HARVEST → harvest_agent (Haiku)
  scan 30+ sources, ≥ 50 candidate items
  → raw/web-research/YYYY-MM-DD/candidates.jsonl

PHASE 1: TRIAGE & DEDUP → triage_agent (Haiku, 1 instance)
  + Grep vault 找已有 page + 跟 7 天 ai-watch report 去重
  + 分类: paper / release / startup / opinion
  → 保留 top 8-12 items

PHASE 2: PARALLEL DEEP RESEARCH (per item × 3 angles)
  对每个 item 并行 spawn 3 researchers (Haiku):
  - Angle A: Primary source (paper PDF / release note)
  - Angle B: Vault relation (跟 Javen 已有 wiki 联系)
  - Angle C: Reception (业界反应 HN/X/blogs/竞品 paper)
  → 三份独立 research note (verbatim quotes)

PHASE 3: CONFLICT RESOLUTION → arbiter_agent (Sonnet, per item)
  读 3 份 research note, 检查 numerical claims 一致性
  标 ⚠️ 当 3 份有 contradiction
  → reconciled-fact-sheet.md

PHASE 4: SYNTHESIS DRAFT → synth_agent (Sonnet, per item)
  只输入 facts.md (不 read 三份原 note!)
  显式标每个数字的 source line
  → draft.md

PHASE 5: ADVERSARIAL DOUBLE REVIEW (gate)
  并行 spawn 2 reviewers (Sonnet):
  - Reviewer A: 事实 audit (每个数字 trace 回 primary PDF)
  - Reviewer B: vault consistency (跟现有 page 一致 / 链接对)
  → decision_agent (Sonnet):
    - 任一 🔴 → reject, 退回 Phase 4 重写 (max 2 次)
    - 全 🟢/🟡 → approve
    - 2 次 reject → 写到 approvals.md

PHASE 6: COMMIT & INDEX → commit_agent (Haiku)
  Write approved drafts → wiki/AI/ or notes/
  Update INDEX.md, log.md, gaps.md
  git commit (revertable), 写 daily-digest, append cost_tracker
```

## 为什么 multi-agent (锚 Anthropic 三准则)

| 准则 | 本系统命中点 |
|---|---|
| **High parallelism** | Phase 2 同 item 3 angle 并行 × 8-12 items ≈ 24-36 并行 |
| **Long context** | 每个 item primary source (paper PDF 30 页) + reception + vault 7 天历史 — 单 agent 装不下 |
| **Multi-tool complex** | WebSearch + WebFetch + Glob/Grep + Bash(re-compute) + git commit — 跨 6 类工具 |

**最关键 ROI**: **角色混淆的 cost**. 一个 agent 既研究又写又审, Phase 5 reviewer 找不到自己写的 bug (writer bias). **双 reviewer + 独立 arbiter 模拟 Anthropic RLHF pipeline 的 cross-labeler agreement**, 切断 self-confirmation bias.

## Per-phase agent setup

| Phase | Agent | Model | Cost | 并行度 |
|---|---|---|---|---|
| 0 Harvest | harvest_agent | Haiku 4.5 | $0.08 | 1 |
| 1 Triage | triage_agent | Haiku 4.5 | $0.05 | 1 |
| 2A Primary | researcher (A) | Haiku 4.5 | $0.04 × 10 | up to 10 |
| 2B Vault | researcher (B) | Haiku 4.5 | $0.03 × 10 | up to 10 |
| 2C Reception | researcher (C) | Haiku 4.5 | $0.04 × 10 | up to 10 |
| 3 Arbiter | arbiter_agent | Sonnet 4.5 | $0.06 × 10 | up to 10 |
| 4 Synthesis | synth_agent | Sonnet 4.5 | $0.08 × 10 | up to 10 |
| 5A Fact | reviewer (A) | Sonnet 4.5 | $0.07 × 10 | up to 10 |
| 5B Consistency | reviewer (B) | Sonnet 4.5 | $0.05 × 10 | up to 10 |
| 5D Decision | decision_agent | Sonnet 4.5 | $0.04 × 10 | up to 10 |
| 6 Commit | commit_agent | Haiku 4.5 | $0.05 | 1 |

**Total**: ~$1.30/day

## Quality gates (今天 3 lessons 落地)

| Lesson | Phase | 怎么 enforce |
|---|---|---|
| **二手 source 不可信** | Phase 2A researcher 红线 + Phase 5A reviewer 重新 fetch PDF cross-check | Researcher A 被禁止读 vault secondary; 必须 WebFetch / Read PDF |
| **数字零容忍** | Phase 4 synth + Phase 5A reviewer Bash 重算 | 每个数字标 `(source-file.md L42)`; 看到 "55% improvement" 跑 Bash 确认 |
| **真实性 > 一切** | Phase 3 arbiter + Phase 5A reviewer 双 gate | 检测 ranking labels — 必须 verify against full table |

**Lesson 加在所有 prompt 共同 preamble (DRY)**:
```
# 今日红线
1. 二手 source = vault summary / source 页 / 自己之前总结 → 不可信. Paper PDF 是 ground truth
2. 数字逐字 = paper 写 72.33% 就 72.33%, 不许 round
3. 真实性 > 任何 design 简洁 / 视觉 / 一致性考量
```

## Conflict resolution (3 researcher 矛盾)

**Source tier 排序**: paper PDF / official release > 厂商 blog > arXiv reply > HN comment > X thread.

**不消解, 显式标 ⚠️**: facts.md 必须包含 `### ⚠️ Disputed claims` section.

**Hard deadlock**: 整 item 标 `confidence: low` + 写 debate 页 (不污染高 confidence wiki).

## Failure modes

10 种 + auto handle, 包括:
1. Phase 2A WebFetch 拿到 paywall — Reviewer A flag → 降级 confidence: medium
2. Phase 2C reception 抓 SEO 农场 — domain allow-list (HN/X/官方 blog/arXiv)
3. Phase 3 arbiter 自相矛盾 — 整 item 标 low + push approvals.md
4. Phase 4 synth 编 paper 没说的 claim — 🔴 reject → 退回重写 (max 2 次)
5. 整日 cost 超 $1.50 — abort 剩余 items
6. Vault git conflict — Stash 自动 commit 到 branch `daemon/YYYY-MM-DD`
7. Researcher A 把 vault source 页当 primary — 引用路径含 `notes/` 或 `wiki/` 自身 → auto reject

## Stretch goals (v2)

1. Weekly synthesis pass (周日跑) — Opus 找 cross-item pattern
2. LLM-as-judge calibration — Opus 重审 Sonnet decision
3. Active learning loop — Javen approve/reject 写 feedback.jsonl 调 prompt
4. Citation graph build — 出 "下一篇该 ingest 谁" recommendation
5. cost_tracker 联动出月度 ROI report

## 跟 5-phase capability research 对比 (explicit)

| 维度 | 5-phase 典型 | Design B |
|---|---|---|
| 角色独立性 | researcher 兼 writer / reviewer | researcher × 3 angles 互不通气, writer 不读 raw research, reviewer × 2 互不通气 |
| 真实性 gate | review 1 次过 | Phase 3 arbiter + Phase 5 双 reviewer + decision_agent 三层 gate |
| 数字 audit | reviewer 看一遍 | Reviewer A 强制 Bash 重算 + 强制 re-fetch primary PDF |
| 冲突 surface | 矛盾被消解或忽略 | Phase 3 arbiter 显式 `⚠️ Disputed`, 不消解 |
| Per-item 深度 | 一份 research note | 3 个 angle 独立 note (3×) |
| Failure recovery | 失败 = 整 pipeline 重跑 | per-item 独立 retry + cost cap + git branch fallback |
| Anthropic 三准则 fit | 中等并行 | 24-36 并行 task, 6 工具类 |
| Wiki-quality compatibility | broadcast 级 | source/concept 页同级精度 |

**最 explicit 优势**: 今天 5/11 PPT 12 个 attribution 错的根因——"Claude 把自己之前总结当原材料"——5-phase 单线没法防 (researcher = writer 时, writer 本能 prefer 自己已组织过的内容). **Design B Phase 4 synth 被 prompt 强制只读 Phase 3 facts.md, 拿不到原 research note**, 物理上切断了"读自己 summary 当 primary"的可能性. **Architectural fix 不是 prompt-level fix**.
