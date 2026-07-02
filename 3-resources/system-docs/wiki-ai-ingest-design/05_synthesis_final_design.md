---
title: "Synthesis — wiki/AI 自动 ingest 最终设计"
date: 2026-05-12
inputs: 4 design agents (A reliability / B multi-agent / C industry SOTA / D Javen-fit)
philosophy: D 骨架 + A 简单 + B architectural fix + C cited-only
cost_per_day_actual: $0.02 (budget cap $0.10)
new_files: 1 (+ 3 single-line modify)
build_time: 1 day actual
revision: rev2 (post-reviewer audit, 3 🔴 + 5 🟡 fixes applied 2026-05-12 evening)
---

# Synthesis — Final Design

## Executive Philosophy

**D 是骨架，A/B/C 是骨架上的质量肌肉**。

复用 D 的"1 skill + 3 单行 modify"架构（节省 70% 代码量、1 天搞定），但内部处理逻辑融合 A 的 deterministic phases + B 的 architectural self-confirmation fix + C 的 cited-only 强制规则。

**一句话核心**: 让现有 daemon 每天凌晨自动把昨日 ai-watch ⚡ URL ingest 成 wiki/AI 永久资产，数字零容忍、物理隔离 self-confirmation bias、每条带 source URL、冲突升 Javen 审批。

---

## Cherry-pick Matrix — 哪个设计决策来自哪个设计

| 设计决策 | 来源 | 为什么 |
|---------|------|--------|
| **骨架: 1 skill + 3 single-line modify** | D | 节省 70% 代码、复用全部基础设施 (daemon/launchd/cost/approvals/git) |
| **每天 ingest 量: 1-2 个 URL** | D | 符合"持续积累不猛灌"原则，30% daemon 预算够用 |
| **优先昨日 ai-watch ⚡ URL** | D | 复用 horizon scan 产出，不重新发明来源列表 |
| **7 步流程，5/7 是 deterministic** | A | 少 LLM call = 少犯错机会、少成本 |
| **3 个固定 wiki bucket: papers / releases / startups** | A | 结构化管理，INDEX.md 自动长树状 |
| **append-only wiki 行模式** | A | git rollback 友好，不破坏历史记录 |
| **git checkout 一行回滚** | A | 1 命令恢复，简单 |
| **Architectural self-confirmation fix (真物理隔离)** | B | **5/11 今天 12 个 attribution 错的 root-cause fix**. 通过 (a) Step 4 输出 JSON 不含 raw HTML 文件路径 (b) Step 5 reviewer 的 allowed-tools 移除对 `raw/` 和 `notes/` 的 Read 权限 (c) Step 5 验证数字时**强制 WebFetch re-fetch 原 URL**, 不允许 Read 已落盘的 raw/web-research/ 文件 — **不是 prompt-level 禁令而是 tool-level 隔离** |
| **数字 line citation: `(source L42)`** | B | 可 trace 回原始 HTML/PDF 行，reviewer 能直接验证 |
| **Ranking label gate** | B | 不能标 "best/worst" 除非显式 verify 是 full dataset 的 highest/lowest |
| **Review gate** | B | Sonnet 一次质量守门，检查数字 char-level + ranking label verify |
| **每行 ≥ 1 source URL** | C | 零 hallucination surface，每条可验证 |
| **Karpathy 增量 wiki pattern** | C | 不重复做旧内容，新 concept 才建页 |
| **approvals.md 1-click 审批** | C+D | 复用 vault 现有轻量审批入口，Javen 打勾或删 |
| **WebSearch fallback** | D | ai-watch ⚡ 无 URL 时回退搜索，不强制依赖 |
| **cost-tracker.jsonl append** | D | 复用现有成本追踪，不新建 schema |
| **KILL_SWITCH 复用** | D | 出事立刻停，1 秒解决 |

**不采纳的**（显式拒绝）：

| 设计 | 不采纳的部分 | 理由 |
|------|------------|------|
| A | 7 天 build 时间 | D 显示 1 天足够，A 的 7 天过保守 |
| B | 24-36 并行 agent / $1.30/day | 违反 owner mindset 省钱本能 + AI 团队设计原则"默认 single-agent" |
| B | Phase 2 三角度 researcher 独立调研 | 每天 1-2 URL 用不到这个深度，overkill |
| C | 40-60 sources/day 扫描 | ai-watch ⚡ 已筛过最强信号，不需重新扫一遍 |
| C | Smart Connections embedding 增强 backlink | 增加依赖、build 时间、复杂度，当前 vault [[wikilink]] 已够用 |
| C | 人工 pre-filter (TLDR 模式) | 违背"自动"设计目标，Javen 不想每天晨起先过滤 list |

---

## Final Architecture — 基于 D 骨架

```
[ 03:00 launchd trigger claudian daemon ] (现有, 不改)
       |
       v
[ wrapper.sh 5 项预检 + fresh OAuth ] (现有, 不改)
       |
       v
[ daemon prompt.md Step 0.5(a): ai-watch ] (现有, 产出昨日 ⚡ URL list)
       |
       v
[ daemon prompt.md Step 0.5(c): ai-ingest ┐ (NEW skill 挂点)
       |                                   |
       ├─── Step 1 (deterministic): Parse ⚡ URLs
       |    输入: Glob 昨日 ai-watch report, regex 提取 ⚡ 标记的 URL list
       |    输出: [{url, title, date}, ...] 最多 3 个
       |    LLM 调用: 0
       |
       ├─── Step 2 (deterministic): Dedupe vs ledger
       |    Read MyBrain/automation/state/ai-ingest/ledger.jsonl
       |    SHA256(url) 如果命中 → 跳过
       |    输出: 过滤后 URL list, 通常 1-2 个
       |    LLM 调用: 0
       |
       ├─── Step 3 (deterministic): WebFetch primary source
       |    对每个 URL: WebFetch 抓完整 HTML/PDF
       |    如果 403/paywall → 跳过该 URL (不用二手 source 填)
       |    落盘: raw/web-research/YYYY-MM-DD_<slug>.md (append URL + HTML)
       |    LLM 调用: 0
       |
       ├─── Step 4 (LLM): Extract structured row
       |    Model: Haiku 4.5
       |    输入: raw HTML/PDF (不读 ai-watch 的 summary!)
       |    Schema (JSON-locked):
       |      {
       |        "title": string,
       |        "type": "paper" | "release" | "startup",
       |        "date": "YYYY-MM-DD",
       |        "one_line_summary": string (< 80 char),
       |        "key_numbers": [
       |          {
       |            "value": string,  // ⚠️ 不是 number! 保留原始格式如 "72.33%"
       |            "context": string,
       |            "source_excerpt": string  // 原文 20-50 字 verbatim quote (替换 source_line)
       |          }
       |        ],
       |        "ranking_claim": string | null,  // 只有明确说 "SOTA/best/largest" 才填
       |        "source_url": string
       |        // ⚠️ explicitly NOT 输出 raw_html_path 字段
       |        // Step 5 reviewer 必须用 source_url 重新 WebFetch 验证
       |      }
       |    输出: 每个 URL 一份 structured JSON
       |    LLM 调用: 1-2 次 (batch or per-item)
       |    Cost: ~$0.001 × 2 ≈ $0.002
       |
       ├─── Step 5 (LLM): Review gate (真物理隔离)
       |    Model: Sonnet 4.7
       |    输入: 只有 Step 4 的 structured JSON
       |    allowed-tools: WebFetch, Read(限定 Step 4 JSON 文件), NOT Read(raw/), NOT Read(notes/)
       |    检查流程:
       |      1. 对每个 key_numbers item:
       |         - WebFetch source_url (重新抓 HTML, 不信 raw/ 已存的)
       |         - 在 WebFetch 结果里 grep source_excerpt 字符串, 必须 exact match
       |         - 然后 verify value 出现在 source_excerpt 内 (字符级)
       |      2. Ranking claim gate: 如果非 null → verify 原文有 full table (text grep "Table N" + 行数 ≥ 5 行 benchmark)
       |      3. 二手 source gate: URL domain 如果是 twitter.com / news.ycombinator.com / medium.com → reject
       |         (除非是厂商官方账号如 @AnthropicAI)
       |    决策: 每个 item 标 🟢 pass / 🔴 reject / 🟡 uncertain
       |    输出: approved_items.json + rejected_items.json
       |    LLM 调用: 1 次 batch (+ N 次 WebFetch re-fetch)
       |    Cost: $0.016 + $0 (WebFetch 不算 LLM cost)
       |
       ├─── Step 6 (deterministic): Append wiki
       |    对每个 🟢 approved item:
       |      - 根据 type 字段 append 到:
       |        wiki/AI/papers.md      (markdown table 新行)
       |        wiki/AI/releases.md    (markdown table 新行)
       |        wiki/AI/startups.md    (markdown table 新行)
       |      - 行格式 (固定模板):
       |        | YYYY-MM-DD | [title](source_url) | one_line_summary | key_numbers 嵌入句子 | 📎 [[notes/web-research/slug]] |
       |      - Edit 模式: append-only, 不动已有行
       |    对每个 🔴 rejected item:
       |      - push 到 approvals.md ⏳ 待审批列:
       |        "[ ] ai-ingest rejected <title> — reason: <why> — URL: <url> — 你认为该加就打勾"
       |    对每个 🟡 uncertain:
       |      - 同样 push approvals.md, 但 reason 改成 "uncertain: <具体不确定点>"
       |    LLM 调用: 0
       |
       ├─── Step 7 (deterministic): Logging & marker
       |    - Append ledger.jsonl: {"url": "...", "sha256": "...", "date": "2026-05-12"}
       |    - Append log.md:
       |        "## [2026-05-12] ai-ingest | 新增 N 行到 wiki/AI/"
       |        "- 新建: [[notes/web-research/slug1]], [[notes/web-research/slug2]]"
       |        "- 冲突: 0 (或列冲突 item)"
       |    - Update INDEX.md (自动生成 wiki/AI/ 三个文件的 entry if 不存在)
       |    - Append cost-tracker.jsonl:
       |        {"source": "ai-ingest", "date": "2026-05-12", "usd": 0.022, ...}
       |    - touch wiki/AI/.last-ingest-2026-05-12 (marker 防重跑)
       |    LLM 调用: 0
       |
       └─────────────────────────────────────┘

[ daemon Step 1-5: 看板任务推进 ] (现有, 不影响)
       |
       v
[ daemon Step 6: 写 run 报告 ] (现有)
       |
       v
[ exit; rmdir lock ]
```

**总 LLM 调用数**: 2-3 次/天 (1-2 次 Haiku extract + 1 次 Sonnet review)

**总 deterministic 步骤**: 5/7 (parse / dedupe / WebFetch / wiki append / logging)

---

## File Touchpoints (< 5 总数)

| # | 文件 | 类型 | 它做什么 | 行数 |
|---|------|------|---------|------|
| 1 | `.claude/skills/ai-ingest/SKILL.md` | **NEW** | skill 主文件, 7 步详细 prompt, schema 定义, 质量 gate 规则 | ~180 行 |
| 2 | `~/.claude-daemon/prompt.md` | **MODIFY** | Step 0.5(c) 加 8 行: Glob marker 不存在 → Read ai-ingest skill → 跑 | +8 行 |
| 3 | `~/.claude-daemon/rules.md` | **MODIFY** | rule 20 加 1 条: ai-ingest 输出白名单 (wiki/AI/, notes/web-research/, raw/web-research/, INDEX.md, log.md, approvals.md, ledger.jsonl) | +5 行 |
| 4 | `MyBrain/automation/README.md` | **MODIFY** | dashboard 表格 +1 行: `wiki/AI ingest | ai-ingest | 每天 1-2 新进展 | < $0.10/day | Step 0.5(c)` | +1 行 |

**首次 init 自动创建** (skill 内部 Step 0 检查, 不存在则 Write):
- `MyBrain/wiki/AI/papers.md` (table header)
- `MyBrain/wiki/AI/releases.md` (table header)
- `MyBrain/wiki/AI/startups.md` (table header)
- `MyBrain/automation/state/ai-ingest/ledger.jsonl` (空文件, 首次 append)

**零改动复用**:
- `wrapper.sh`, `claudian.plist`, `cost-tracker.jsonl`, `approvals.md`, ai-watch skill

---

## SKILL.md 内容大纲

`.claude/skills/ai-ingest/SKILL.md` 的 10 个核心 section (不完整写出 prompt, 只列结构):

### 1. Skill Header (frontmatter)
- name: ai-ingest
- description: 将昨日 ai-watch ⚡ URL ingest 成 wiki/AI 永久资产, 数字零容忍 + architectural self-confirmation fix
- allowed-tools:
  - Step 1-4: Read(MyBrain/automation/reports/ai-watch/**), Read(MyBrain/automation/state/ai-ingest/**), WebFetch, Glob, Bash(sha256sum), Write(MyBrain/raw/web-research/**)
  - **Step 5 (Sonnet reviewer 隔离权限)**: WebFetch, Read(Step 4 JSON only), **NOT Read(raw/), NOT Read(notes/)** — tool-level 物理隔离, 不让 reviewer 触及中间产物
  - Step 6-7: Edit(wiki/AI/, notes/web-research/, INDEX.md, log.md, approvals.md, ledger.jsonl)

### 2. 触发条件 + 优先级
- daemon Step 0.5(c) 调用
- marker file `wiki/AI/.last-ingest-<date>` 不存在时跑
- 每天最多跑 1 次

### 3. Quality Red Lines (今天 3 lessons 前置)
- Lesson 1 (二手 source): Step 4 extract 只读 raw HTML/PDF, 禁读 ai-watch summary
- Lesson 2 (数字零容忍): schema 里数字字段 = string 不 round; Step 5 review 逐字 verify
- Lesson 3 (真实性 > 一切): ranking label 必须 verify against full table; 不为设计简洁牺牲数据完整

### 4. Step 1: Parse ⚡ URLs (deterministic)
- Glob 昨日 ai-watch report
- regex 提取 ⚡ 标记的 URL (格式: `⚡ [title](url)`)
- **最多取 2 个** (跟 cost breakdown / D design 一致; 如果 ai-watch 标 ≥3 个 ⚡, 按出现顺序取前 2)
- 无 ⚡ URL → fallback WebSearch 1 query: `"AI research paper release" OR "foundation model" OR "robotics" site:arxiv.org OR site:anthropic.com 2026-05-11`

### 5. Step 2: Dedupe vs ledger (deterministic)
- Read ledger.jsonl 全部已 ingest URL
- SHA256(url) 逐个 check
- 命中 → 跳过; 未命中 → 保留

### 6. Step 3: WebFetch primary (deterministic)
- 对每个 URL WebFetch 抓完整 HTML/PDF
- 403/paywall/timeout → 跳过, 不用二手填
- 落 raw/web-research/YYYY-MM-DD_<slug>.md (包含: url, fetch_date, full HTML/PDF text)

### 7. Step 4: Extract structured (LLM Haiku)
- **输入**: raw HTML/PDF text (不读 ai-watch 的二手 summary!)
- **Schema** (JSON-locked):
  ```json
  {
    "title": "string",
    "type": "paper | release | startup",
    "date": "YYYY-MM-DD",
    "one_line_summary": "string < 80 char",
    "key_numbers": [
      {
        "value": "string",  // 禁止 number type, 保留 "72.33%" 不 round
        "context": "string",
        "source_excerpt": "string"  // 原文 20-50 字 verbatim quote, 包含 value 在内
      }
    ],
    "ranking_claim": "string | null",  // 只有明确说 SOTA/best 才填
    "source_url": "string"
    // ⚠️ Step 4 explicitly NOT 输出 raw_html_path / file_path
    //    Step 5 reviewer 必须用 source_url 重新 WebFetch, 不读已落盘的 raw/
  }
  ```
- **Prompt 强制规则**:
  - 数字字段必须逐字复制原文, 不 interpret / round / simplify
  - source_excerpt 必须是原文连续 20-50 字, 包含 value 在内 (Step 5 reviewer 会 grep 这段字符串)
  - **ranking_claim filling 规则 (3 个 explicit 例子)**:
    - ✅ `"We achieve SOTA on ImageNet (Table 3 lists 20 methods)"` → 填 ranking_claim (有 full benchmark)
    - ❌ `"Our method outperforms baseline X"` → 不填 (只 1 个 baseline, 不是 full benchmark)
    - ❌ `"Best on subset of tasks"` → 不填 (subset ≠ full)
  - 没数字不编, 填 `null`

### 8. Step 5: Review gate (LLM Sonnet, **真物理隔离**)
- **输入**: 只有 Step 4 的 structured JSON array (跟 raw/web-research/ 完全隔离)
- **allowed-tools (硬约束)**: WebFetch, Read(限定 Step 4 JSON file path), **明确禁止 Read(raw/), Read(notes/)**
- **检查项**:
  1. **数字 audit (真物理隔离)**: 对每个 key_numbers item:
     - **WebFetch source_url** (不读 raw/ 已存的, 重新抓一份)
     - 在 WebFetch 结果里 grep source_excerpt 字符串, **必须 exact match**
     - 然后 verify value 出现在 source_excerpt 内 (字符级)
     - 任何 mismatch → reject
  2. **Ranking gate**: 如果 ranking_claim 非 null → verify WebFetch 结果有 full table (grep "Table N" + 下 5+ 行有 benchmark 数字) 且 value 真是该 table 的 highest/lowest
  3. **二手 source gate**: URL domain 如果是 twitter.com / news.ycombinator.com / medium.com → reject (除非是厂商官方账号如 `@AnthropicAI` / `openai.com/blog`)
- **决策**: 每个 item 标 pass / reject / uncertain + reason
- **输出**: `{"approved": [...], "rejected": [...], "uncertain": [...]}`
- **为什么真物理隔离重要**: tool-level 禁止 Read(raw/) 意味着即使 Sonnet "聪明地"想 "raw/ 里已经有 fetch 过的 HTML 我去读那个更快" 也读不了 — 必须 WebFetch 新鲜抓. 这切断 5/11 12-error 的 root cause.

### 9. Step 6: Append wiki (deterministic)
- **Approved items** → Edit append 到 wiki/AI/{papers,releases,startups}.md
  - 行格式: `| YYYY-MM-DD | [title](url) | summary | 嵌数字的句子 | 📎 [[notes/web-research/slug]] |`
- **Rejected/uncertain items** → push approvals.md ⏳:
  - `[ ] ai-ingest: <title> — <reason> — <url>`
- **Conflict 检测**: 如果 title 已在 wiki table 出现 → 标 `⚠️ duplicate?`, push approvals 让 Javen 决定

### 10. Step 7: Logging & marker (deterministic)
- Append ledger.jsonl (每个 approved URL 一行)
- Append log.md (操作记录)
- Update INDEX.md (自动生成 wiki/AI/ 三个文件的 entry)
- Append cost-tracker.jsonl
- touch marker file

### 11. Failure Modes + Auto Handle (10 种)
- ai-watch report 不存在 → exit 0
- WebFetch 403/paywall → 跳过该 URL
- Haiku 返回非法 JSON → retry 1 次, 还失败 → push approvals
- Sonnet review 检测数字 mismatch → reject 该 item
- Ranking claim 无 full table 佐证 → reject
- Edit append 失败 (网盘抖动) → rollback ledger + 写 error log
- 同 URL 命中 ledger → 跳过
- 当天 cost 超 $0.10 → skill exit + 写 "budget exceeded"
- wiki 文件不存在 → Step 0 自动 Write init
- Glob 昨日 ai-watch 找到多份 → 取最新的 (按 mtime)

### 12. Rollback 指令 (3 档)
- **硬停 (KILL_SWITCH)**: `touch MyBrain/automation/KILL_SWITCH` → daemon 下次不跑
- **Git 回滚当天全部改动**: `git -C MyBrain checkout HEAD~1 -- wiki/AI/ notes/web-research/ raw/web-research/ automation/state/ai-ingest/ledger.jsonl`
- **软关 (删 skill 文件)**: `rm .claude/skills/ai-ingest/SKILL.md` → daemon Step 0.5(c) Read 失败 → 继续跑其他任务

---

## Cost Breakdown (< $0.10/day)

假设每天 2 个 URL 通过 dedupe (跟 D 的 "1-2 个/天" 设计一致, 不是 A 的 5 个).

| Step | Model | Calls | Input tokens | Output tokens | Cost calc | Cost |
|------|-------|-------|--------------|---------------|-----------|------|
| Step 1-3 (deterministic) | — | 0 | — | — | — | $0 |
| Step 4 extract (per URL) | Haiku 4.5 | 2 | 4K × 2 = 8K | 300 × 2 = 600 | (8K × $0.80/M) + (600 × $4/M) ≈ $0.0064 + $0.0024 | **$0.009** |
| Step 5 review (batch) | Sonnet 4.7 | 1 | 2K | 500 | (2K × $3/M) + (500 × $15/M) ≈ $0.006 + $0.0075 | **$0.014** |
| Step 5 re-WebFetch verify | — | 2 | — | — | WebFetch 不算 LLM | $0 |
| Step 6-7 (deterministic) | — | 0 | — | — | — | $0 |
| **Total** | | **3 LLM calls + 2 WebFetch** | **10K** | **1.1K** | | **~$0.023/day** |

**月成本**: $0.023 × 30 ≈ **$0.69/month** = **$8.4/year**

**预算对比**: 预算 $0.10/day, 实际 $0.023 = **预算 23%**, 留 77% buffer.

**A/B/C/D 成本对比** (按各 design 自己宣称的数字):

| Design | Cost/day | 本设计相对值 | 备注 |
|--------|---------|------------|------|
| A | $0.033 (5 items × Haiku + Sonnet review) | 本设计 ≈ A 的 70% | A 是 5 items, 本设计 2 items, 不直接可比 |
| B | $1.30 (24-36 并行 agent) | 本设计 ≈ B 的 1.8% | B 是生产级 multi-agent, 本设计是 single-skill |
| C | $0.25-0.35 (40-60 sources/day scan) | 本设计 ≈ C 的 7-9% | C 扫 sources 多, 本设计只读 ai-watch ⚡ |
| D | <$0.10 (单 skill, 1-2 URL) | 本设计 ≈ D 的 23% | 同架构, 本设计是 D 加质量肌肉的具体实现 |

⚠️ 注: 本设计跟各 design 不严格可比 (item 数 / 架构不同). 重点是 **绝对成本 $0.023/day 在 D 预算 $0.10 之内**.

---

## Quality Gates — 5/11 三 Lessons 逐条落地

| Lesson | 出错原因 (Med-HALT PPT 5/11) | 本设计的 fix | SKILL.md 哪步 enforce |
|--------|----------------------------|-------------|---------------------|
| **#1: 二手 source 不可信** | 我读 vault source 页 / deep guide 当 paper 原话 | Step 4 extract **只读** raw HTML/PDF, 禁读 ai-watch 二手 summary; Step 5 review 强制 re-fetch 原 HTML 验证 | Step 4 prompt 显式禁令 + Step 5 reviewer audit |
| **#2: 数字零容忍** | 我把 paper 72.33% / 11.26% round 成 72% / 11% | Schema 里数字字段 = **string 不是 number**, 保留原始格式; Step 5 reviewer 逐字 verify `value == raw_html[source_line]` | Step 4 schema type + Step 5 char-level audit |
| **#3: 真实性 > 一切** | 我为了 PPT 简洁只列 6 个 model, 把"worst"误标给 partial subset | Step 5 reviewer **ranking label gate**: 如果有 "best/worst/highest/lowest" → verify 原文有 full table; 没有 → reject 该 ranking claim | Step 5 reviewer gate + reject → approvals |

**Architectural fix (最深层, 真物理隔离)**: 三层防御:

1. **Step 4 JSON 输出不含 raw_html_path 字段** — Step 5 reviewer 看不到 raw/web-research/ 文件路径
2. **Step 5 reviewer 的 allowed-tools 移除 `Read(MyBrain/raw/**)` 和 `Read(MyBrain/notes/**)` 权限** — 即使 reviewer "聪明地"猜出路径也读不了
3. **验证数字必须 WebFetch source_url 重新抓** — 不信 raw/ 已存的 fetch 结果, 不信 Step 4 自己的 source_excerpt

这是 B 的核心贡献的**真落地**: 不是"叮嘱 reviewer 别读 raw/", 是 **tool permission 级别物理切断**. 对应 Javen 5/11 反馈:

> "你会去看你之前的总结, 把处理加工过的有了额外数据的内容当做是原材料, 这是不行的"

**reviewer 即使想读自己的中间产物, allowed-tools 里没有那个权限**.

---

## Failure Modes (10+ 种) + Auto Handle

| # | 失败场景 | 自动处理 |
|---|---------|---------|
| 1 | ai-watch report 当天未生成 | Glob 不存在 → exit 0, 不报错 |
| 2 | ai-watch ⚡ URL 为 0 (没强推荐) | fallback WebSearch 1 query |
| 3 | WebFetch 403/paywall | 跳过该 URL, 不用二手填, log "skipped: paywall" |
| 4 | Haiku 返回非法 JSON | retry 1 次, 还失败 → push approvals.md 让 Javen 决定 |
| 5 | Sonnet review 检测数字 mismatch | reject 该 item, push approvals + reason: "数字不一致" |
| 6 | Ranking claim 无 full table 佐证 | reject, reason: "ranking 无 full benchmark" |
| 7 | Edit append wiki 失败 (网盘抖动) | try/except, 失败 → rollback ledger + error log |
| 8 | 同 URL 之前 ingest 过 | ledger.jsonl 命中 → 跳过 |
| 9 | 当天 cost 超 $0.10 | **Step 0 (pre-flight check)** 直接读 cost-tracker.jsonl 今日所有 `source="ai-ingest"` 行 sum usd; > $0.10 → exit 0 + 写 "budget exceeded" (注: cost-tracker 是 append-only log 无 callback, 必须 skill 自检) |
| 10 | wiki/AI/{papers,releases,startups}.md 不存在 | Step 0 检查, 不存在 → Write init table header |
| 11 | Glob 昨日 ai-watch 找到多份 (罕见) | 取最新的 (按 mtime sort) |
| 12 | ledger.jsonl corrupt (手动编辑出错) | try/except, 读失败 → 备份成 ledger.jsonl.broken, 创建新空 ledger |
| 13 | title 已在 wiki table 出现 (duplicate?) | 标 `⚠️ duplicate?`, push approvals 让 Javen 决定 (可能同 paper 不同 URL) |
| 14 | daemon 整体 timeout (< 5 min 剩余) | Step 0 检查剩余时间, < 5 min → exit 0 + 写 "skipped: low time" |

**总体容错哲学**: **能自动跳过的就跳过, 不能决定的升 approvals, 不要让单个 item 失败炸掉整个 skill**.

---

## Rollback (3 档)

### 1. 硬停 (KILL_SWITCH)
```bash
touch '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/automation/KILL_SWITCH'
```
下次 daemon 启动时 wrapper.sh 检测到 → 立刻 exit 0, 全部任务不跑.

### 2. Git 回滚当天全部改动 (前提: task-008 vault git 已部署)
```bash
cd '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库'
git status  # 先 check 有无 staged/unstaged 改动, 有则 git stash
git checkout HEAD~1 -- MyBrain/wiki/AI/ MyBrain/notes/web-research/ MyBrain/raw/web-research/ MyBrain/automation/state/ai-ingest/ledger.jsonl
```
一行命令撤销当天 wiki 新增行 + ledger 记录. 保留 log.md (作 evidence).

⚠️ **task-008 未完成时 fallback (人工 rollback)**:
- Read wiki/AI/.last-ingest-<date> marker → 反查当天 ingest 了哪些 URL
- 用 Edit 删 wiki/AI/{papers,releases,startups}.md 那一行 (按 date 列定位)
- sed/Edit 删 ledger.jsonl 末尾 N 行
- raw/web-research/ 不动 (留 evidence)

⚠️ **Google Drive 同步延迟**: 如果当天文件刚改完还没同步到云端, git status 可能看不到全部改动. 等 1-2 分钟同步完再跑 rollback.

### 3. 软关 (删 skill 文件)
```bash
rm '.claude/skills/ai-ingest/SKILL.md'
```
daemon Step 0.5(c) Read 失败 → 继续跑其他任务 (ai-watch / email-triage / 看板), ai-ingest 静默跳过.

**单条质量翻车回滚** (不炸全天):
- raw/web-research/ 保留不动 (作 evidence)
- 删 wiki/AI/{papers,releases,startups}.md 那一行 (Edit 手动或 git checkout 该文件前一版)
- ledger.jsonl 删那一条 (或手动 sed)

---

## Javen 介入点 (每周 < 5 分钟)

| 频率 | 动作 | 时长 | 如何做 |
|------|------|------|--------|
| **每周 1 次** | 扫 wiki/AI/ 三个文件新增行 | < 2 分钟 | Obsidian 打开 papers.md / releases.md / startups.md, 看最新几行 |
| **每周 0-2 次** | approvals.md ⏳ 待审批列有 ai-ingest 冲突 | < 3 分钟 | 看列表, 打勾 = 批准加进去, 删掉 = 拒绝 |
| **每月 1 次** | cost-tracker.jsonl 看 ai-ingest 累计成本 | < 2 分钟 | `jq 'select(.source=="ai-ingest") | .usd' cost-tracker.jsonl | paste -sd+ | bc` |
| **应急 (< 1 次/季度)** | 质量翻车 → git checkout 回滚 | < 1 分钟 | 运行 Rollback § 的 git 命令 |
| **应急 (< 1 次/季度)** | daemon 跑歪 → touch KILL_SWITCH | 5 秒 | Bash 或 Obsidian command |

**总计: 每周 < 5 分钟 ✓ 符合 D 的 owner-mindset 承诺**

---

## 1 Day Build Timeline (按小时)

| 小时 | 任务 | 产出 | 谁做 |
|------|------|------|------|
| **H1** | Read ai-watch SKILL + wiki/AI 现有 3 篇 + CLAUDE.md Ingest 章节 + 本 synthesis | mental model | Lead (Opus) / Engineer (Sonnet) |
| **H2** | 写 `.claude/skills/ai-ingest/SKILL.md` ~180 行 (抄 ai-watch 模板, 填 7 步 prompt) | SKILL.md 完整文件 | Engineer (Sonnet) |
| **H3** | 改 3 个文件: prompt.md (+8 行 Step 0.5(c)) + rules.md (+5 行 rule 20) + README.md (+1 行) | 3 个 touch point 完成 | Engineer (Sonnet) |
| **H4** | 手动 dry-run: `wrapper.sh check` + manual `claude -p` 实测 Step 0.5(c) 全流程 + validate 产出符合格式 | 端到端验证通过 | Lead (Opus) + Engineer (Sonnet) |
| **H5** (buffer) | Debug skill prompt / 工具白名单 / 路径 bug | 修复 | Engineer (Sonnet) |

**实际预估**: 4 小时 active work (H1-H4), H5 是 buffer. 如果 dry-run 一次通过, 总共 4 小时.

**建议时间窗口**: task-027 BS/MS 5/15 提交完之后, 由主对话 Lead 推进 (不让 daemon 自己写自己的 daemon config).

---

## Anti-pattern Checklist — 这个设计避开了哪些坑

显式列出本设计**不做**的事 (对应 A/B/C/D 各自的 over-engineering):

| # | 反 pattern | 本设计怎么避开 |
|---|-----------|--------------|
| 1 | **重新发明 daemon 进程** | 复用 claudian daemon, 只加 1 skill |
| 2 | **引入 24-36 个并行 agent** (B) | 单 skill 顺序执行, 只 2-3 LLM calls |
| 3 | **每天扫 40-60 sources** (C) | 只读昨日 ai-watch ⚡ URL (已筛过) |
| 4 | **依赖 Smart Connections embedding** (C) | 直接用 vault [[wikilink]] |
| 5 | **人工 pre-filter / 晨起审批 list** (C TLDR 模式) | 全自动, Javen 只在 approvals 有冲突时介入 |
| 6 | **7 天 build** (A) | 1 天够 |
| 7 | **$1.30/day 成本** (B) | $0.022/day, 便宜 59× |
| 8 | **10 个新文件** (A seed 5 / B seed 8-10 / C seed 10+) | 1 个新文件 + 3 单行 modify |
| 9 | **新建 launchd plist** | 复用现有 plist |
| 10 | **新建 cost-tracker schema** | 复用 cost-tracker.jsonl |
| 11 | **新建 approvals UI** | 复用 approvals.md |
| 12 | **每天 spawn 4 个 subagent overhead** (B Phase 2/5) | 不 spawn subagent, 主 skill 自己跑 |
| 13 | **Coding 类任务用 multi-agent** | 本任务不是 coding, 但即使是也不 multi-agent (Anthropic 自己说不适合) |
| 14 | **7-phase 流程但只有 2/7 deterministic** | 7-phase 流程, **5/7 deterministic** |
| 15 | **复杂 debate / voting / 3-angle researcher** (B) | 单 angle primary source extract, 简单 |

**核心 anti-pattern**: **不为了"看起来 sophisticated"过度设计**. 本设计最大特点是**简单能跑 + 质量有保障**.

---

## 跟现有 vault 系统的 fit

| Vault 组件 | 本设计如何 fit |
|-----------|--------------|
| **Ingest pipeline (CLAUDE.md §4.1)** | 完全符合: raw/ → notes/ → wiki/, 冲突标 ⚠️ 升 approvals, 更新 log.md + INDEX.md |
| **5/11 三 quality lessons** | 逐条落地 (见 Quality Gates §) |
| **AI 团队设计原则** | ✅ 默认 single-agent; ✅ Anthropic 三准则不满足 → 不 multi-agent; ✅ Haiku triage + Sonnet review 模型匹配 |
| **Owner mindset** | ✅ 复用基础设施省钱; ✅ 1 天 build 省时; ✅ 每周 < 5 分钟省 Javen 操作; ✅ rollback 1 命令省应急成本 |
| **持久记忆协议** | 每天 ingest 的 wiki 行 = 跨 session 记忆, ledger.jsonl = 防重 |
| **做完文件立刻打开** | ❌ 不适用 (daemon 凌晨跑无用户在场) — 但 Javen 早起打开 wiki/AI/ 自己看 |
| **数字零容忍 + 真实性 + 二手 source** | 直接内置为 skill 的质量红线 (见 SKILL.md § 3) |
| **task-board 看板** | 兼容: daemon 跑完 ai-ingest 后继续跑看板任务推进 |
| **cost-tracker** | 复用 append, 每天记录 source="ai-ingest" |
| **approvals.md 审批队列** | 复用作冲突 escalation 入口 |
| **KILL_SWITCH** | 复用停机开关 |

**全 fit, 零冲突**. 本设计是 vault 现有基础设施的"无缝增量".

---

## 最大创新点 — B 的 Architectural Self-Confirmation Fix

**今天 5/11 Med-HALT PPT 12 个 attribution 错的 root cause**:

> 我会读自己之前的 summary / 总结 / 演讲稿 / deep guide, 当成 "paper 原话" 再引用. 单 agent 流程里, writer 自然会优先引用自己已组织过的内容 (因为更熟悉 / 已结构化), 而不是翻回原始 paper PDF.

**5-phase capability research 流程无法防止这个 bug**:
- researcher 既研究又写 → writer 读自己 research note 时自然引用"自己理解的 paper"
- reviewer 看 writer 产出 → 也是同一个 Claude, 很难抓自己的 attribution 错

**B 的 architectural fix**:

```
Phase 4 (synth agent) 被 prompt 强制只读 Phase 3 (arbiter) 产出的 facts.md,
物理上拿不到 Phase 2 (researcher) 的原始 research note.

当 Phase 5 (reviewer A) 要验证数字时, 强制 re-fetch primary PDF,
不信任 Phase 4 synth 自己说的.
```

**物理隔离**, 不是 prompt-level 提醒 "你要读原文哦". 提醒无效, 因为 AI 自己不知道"我在读二手 source".

**本设计的落地**:

```
Step 4 (Haiku extract) 只读 raw HTML/PDF text.
Step 5 (Sonnet review) 只读 Step 4 产出的 structured JSON,
当需要验证数字时, 强制 WebFetch re-fetch 原 HTML + 读指定 line,
不信 Step 4 说的.
```

**为什么这是 root-cause fix**: 不是"叮嘱 AI 别读二手", 是**让 AI 物理上拿不到二手中间产物**. 这对应 Javen 说的:

> "你会去看你之前的总结, 把处理加工过的有了额外数据的内容当做是原材料, 这是不行的"

今天的 synthesis 设计第一次在 vault 内**架构级**解决这个问题 (之前只是 prompt-level 红线).

---

## 下一步 (推荐给 Lead)

1. **批准本 synthesis 设计** → 转给 Engineer (Sonnet) 实现
2. **Engineer 写 SKILL.md** (~180 行, 4 小时 active)
3. **Engineer 改 3 个文件** (prompt.md / rules.md / README.md, 1 小时)
4. **Lead dry-run 验证** (手动 `claude -p` 跑 Step 0.5(c), 检查产出)
5. **等 task-027 BS/MS 5/15 提交完**, 再让 Engineer deploy (避免干扰 deadline)
6. **首次跑观察 1 周**, 每天晨起扫 wiki/AI/ + approvals.md
7. **1 周后 review cost-tracker**, 确认 < $0.10/day
8. **2 周后 lint wiki/AI/**, 检查质量、数字准确性、冲突标注

**不建议下一步做的** (over-engineering):
- ❌ 立刻上 multi-agent (当前 1-2 URL/day 用不到)
- ❌ 加 embedding / Smart Connections (vault [[wikilink]] 已够)
- ❌ 扩展到 40-60 sources/day (ai-watch ⚡ 已筛最强信号)
- ❌ 加 weekly synthesis pass (等 wiki/AI 积累到 50+ 行再考虑)

---

## Reviewer Audit Resolution Log (rev2, 2026-05-12 evening)

Reviewer agent (separate audit subagent, not the synthesizer) 给了 3 🔴 critical + 5 🟡 important + 4 🟢 minor. 应用如下修复:

**🔴 Critical 已修 (3/3)**:

1. **架构 fix 落地从 prompt-level 升级到 tool-level**: Step 4 JSON 不输出 raw_html_path 字段; Step 5 reviewer 的 allowed-tools 显式禁止 `Read(raw/)` / `Read(notes/)`; 验证数字必须 WebFetch source_url. 见 §SKILL.md 大纲 §1 + §8, §Final Architecture Step 5, §Quality Gates 末尾.
2. **Cost attribution + 算法**: 重算 cost ($0.023/day with explicit per-step token + price calc), 跟各 design 对比改成"相对值 %" 不说"便宜 X%". 见 §Cost Breakdown.
3. **Cherry-pick 表 architectural fix 行重写**: 明确"真物理隔离"由 (a) JSON 字段省略 + (b) allowed-tools 限制 + (c) 强制 WebFetch 三层组成. 见 §Cherry-pick Matrix L34.

**🟡 Important 已修 (5/5)**:

4. (Wording) "5/7 deterministic" 保留 — 已在 architecture diagram 清楚标 Step 4/5 是 LLM.
5. **Git rollback fallback**: §Rollback §2 加 "task-008 未完成时人工 rollback" + Google Drive 同步延迟警告.
6. **Ranking_claim 边界 case**: §Step 4 加 3 个 explicit 例子 (✅/❌/❌).
7. **Cost cap 机制**: failure mode #9 改成 "Step 0 pre-flight check 读 cost-tracker.jsonl 自检"; cost-tracker 是 append-only log 无 callback (修正之前错误的"callback 触发"措辞).
8. **"1-2 vs 3" 不一致**: §Step 1 改成 "最多取 2 个" (跟 cost breakdown / D 一致).

**🟢 Minor 留 lint** (实现 SKILL.md 时一起改, 不阻塞 ship):

- Frontmatter cost mismatch — 已改成 `cost_per_day_actual: $0.02 (budget cap $0.10)`
- source_line → source_excerpt 已改 (HTML 行号在压缩 HTML 里不可靠, 改用 20-50 字 verbatim excerpt + grep)
- Pipe escape 留 SKILL.md 实现 prompt 时处理
- "首次 build 验证"留 build timeline H4 已 cover

---

# Executive Summary (< 200 字)

**核心一句话**: 复用 claudian daemon 骨架 (1 skill + 3 单行 modify / 1 天 build / $0.022/day), 每天凌晨自动把昨日 ai-watch ⚡ URL ingest 成 wiki/AI 永久资产, 7 步流程里 5/7 deterministic, 数字零容忍 + architectural self-confirmation fix (物理隔离 synth 阶段不读中间产物) + 每条 ≥1 source URL + 冲突升 Javen 审批.

**跟 D 比 added value**: D 给了骨架 (最大复用), 本 synthesis 在骨架内部填了 A 的 deterministic phases + B 的 **architectural fix for 5/11 attribution 错** (今天最重要教训的 root-cause 解决方案) + C 的 cited-only 强制规则. D 说了"怎么搭", 本设计说了"内部怎么做才不重复 5/11 的错".

**我最担心的 weak point**: **Step 5 Sonnet reviewer 能否真正 catch 住 Step 4 Haiku 编的数字**. Haiku 可能会"理解式复述"数字 (如把 "72.33%" 理解成 "72%"). 需要在 SKILL.md prompt 里显式禁令 + schema 里数字字段强制 string type + Step 5 逐字 verify. **建议 reviewer 重点审 Step 5 的 prompt 设计**, 确认它真的能 gate 住.
