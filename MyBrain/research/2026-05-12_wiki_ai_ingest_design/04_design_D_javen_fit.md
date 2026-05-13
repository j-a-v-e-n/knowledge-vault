---
title: "Design D — Javen-fit / 最大复用派"
date: 2026-05-12
agent: Plan (Opus)
agent_id: ac5732b1a52cb8c1c
philosophy: 100% 复用现有 daemon / 1 个新文件 / 1 天搞定
cost_per_day: "<$0.10"
new_files: 1 (+ 3 单行级 modifications)
build_time: 1 day (4 hours actual)
key_insight: 现有 ~/.claude-daemon 已稳定 14+ 天, 加 wiki/AI ingest 不是新建 daemon 是新建 skill
---

# Design D · Javen-fit / 最大复用派

## 1. Inventory 结果

| 现有基础设施 | 位置 | 状态 | 复用价值 |
|---|---|---|---|
| **Claudian dawn-shift daemon** | `~/.claude-daemon/{wrapper.sh,prompt.md,rules.md}` | 每天 03:00 跑、稳定 14+ 天、有 OAuth + fresh session + lock + kill-switch + AC-power 预检 | **核心载体** |
| **launchd plist** | `~/Library/LaunchAgents/com.javen.claudian.plist` | 03:00 触发, AC-power gating | **直接复用** |
| **ai-watch skill** | `.claude/skills/ai-watch/SKILL.md` | WebSearch + WebFetch + 70/30 模板 + 每日 Glob | **抄结构** |
| **email-triage skill** | `.claude/skills/email-triage/SKILL.md` | 已部署、prompt.md Step 0.5(b) | **抄模式** |
| **daemon prompt.md Step 0.5** | `~/.claude-daemon/prompt.md` 第 20-34 行 | 已有"每日第一次跑 → Glob 今日报告 → 不存在则跑 skill"机制 | **直接加 0.5(c)** |
| **cost-tracker.jsonl** | `MyBrain/automation/logs/cost-tracker.jsonl` | JSONL append 格式, tokens/cache/usd 字段齐 | **直接 append** |
| **approvals.md** | `MyBrain/automation/queue/approvals.md` | 打勾批准, 删除拒绝 | **复用作 wiki/AI 草稿审批入口** |
| **subagent 团队** | `.claude/agents/{researcher,engineer,writer,reviewer}.md` | 已可调度 | **复用 researcher** 做 fact-check (可选) |
| **wiki/AI/ 现状** | 3 篇 concept 页 | 框架已立 | **直接 append** |
| **raw/web-research/** | 已有约定 | ai-watch 报告本身就是潜在原料 | **复用 ai-watch 历史报告**作 ingest 候选源 |

## 2. 复用决策表

| 现有组件 | 复用方式 | 节省 |
|---|---|---|
| `wrapper.sh` | **零改动** — 工具白名单已含 Read/Write/WebFetch/WebSearch | -300 行 daemon 框架 |
| `claudian.plist` | **零改动** — 03:00 触发已含本任务 | -50 行 plist |
| `prompt.md` Step 0.5 机制 | **+8 行** Step 0.5(c) | -150 行新调度 |
| `rules.md` | **+1 条 rule 20** 限定输出范围 | -50 行权限管理 |
| `ai-watch` skill 模板 | 抄 frontmatter / Glob / 输出位置 / 长度约束 | -100 行模板 |
| `approvals.md` 打勾审批 | 复用作冲突 escalation | -80 行新 UI |
| `cost-tracker.jsonl` | 直接 append `{"source":"ai-ingest", ...}` | -40 行新 schema |
| `researcher.md` subagent | 可选 spawn 做 fact-check (default 不 spawn) | 复用 |
| ai-watch 历史报告 | 优先扫**昨日 ai-watch ⚡ 标记 URL** | 复用 horizon scan 产出 |

**新代码占比**: 约 200 行新 markdown, 其余 **70%+ 都是复用**.

## 3. 新增组件 (< 5 个)

**新增 = 1 个文件 + 3 处微改 = 4 个 touch point**:

| # | 文件 | 类型 | 它做什么 | 为什么不能 extend |
|---|---|---|---|---|
| 1 | `.claude/skills/ai-ingest/SKILL.md` | **NEW** | 每天 ingest 1-2 个 AI 进展, 按 vault ingest pipeline 写 source 页 + concept 页 + INDEX + log.md; 冲突 → approvals.md | 是新 skill, 跟 ai-watch / email-triage 边界清晰 |
| 2 | `~/.claude-daemon/prompt.md` | **MODIFY** (+8 行) | 加 Step 0.5(c): Glob `wiki/AI/.last-ingest-<date>` 不存在 → Read skill → 跑 → 写 marker | daemon 调度入口 |
| 3 | `~/.claude-daemon/rules.md` | **MODIFY** (+1 条 rule 20) | 限定 ai-ingest 输出白名单 (wiki/AI/, notes/web-research/, raw/web-research/, INDEX.md, log.md, approvals.md) | daemon 安全护栏 |
| 4 | `MyBrain/automation/README.md` | **MODIFY** (+1 行) | dashboard 表格 +1 行 `wiki/AI ingest` | dashboard 是 Javen 入口 |

**explicitly NOT 新增**:
- ❌ 不新建 daemon 进程
- ❌ 不新建 plist
- ❌ 不新建 cost-tracker schema
- ❌ 不新建 approvals.md UI
- ❌ 不新建 launchd job

## 4. Daemon 执行流程

凌晨 03:00 单次完整 ingest (在 claudian 现有 30 分钟预算内, 估计本任务占 5-7 分钟):

```
[launchd 03:00] (现有)
  ↓
[wrapper.sh 5 项预检] (现有: kill-switch / vault / AC / claude bin / lock)
  ↓
[fresh session UUID + OAuth] (现有)
  ↓
[claude -p 跑 FULL_PROMPT, Sonnet fallback] (现有)
  ↓
[Step 0: approvals.md 扫打勾] (现有)
  ↓
[Step 0.5(a): ai-watch skill] (现有)
  ↓
[Step 0.5(b): email-triage skill] (现有)
  ↓
[Step 0.5(c): ai-ingest skill ─ NEW ┐
   • Glob `wiki/AI/.last-ingest-<date>` 存在 → skip
   • Read `.claude/skills/ai-ingest/SKILL.md`
   • 选源 (优先级):
     (1) 昨日 ai-watch 报告 ⚡ 标记 URL (复用 horizon scan)
     (2) 若无 → WebSearch 1 query
   • WebFetch top 1-2 URL
   • 落 raw/web-research/YYYY-MM-DD_<slug>.md
   • 按 vault CLAUDE.md ingest 规则:
     - source 页 → notes/web-research/<slug>.md
     - 普适 concept → wiki/AI/<concept>.md
     - 冲突 → approvals.md ⏳ 待 Javen 决定
   • Append log.md + 更新 INDEX.md
   • touch wiki/AI/.last-ingest-<date> marker
   • Append cost-tracker.jsonl
                                  ┘
  ↓
[Step 1-5: 看板任务推进] (现有)
  ↓
[Step 6: 写 daemon-run 报告] (现有)
  ↓
[exit; rmdir lock]
```

**关键设计选择 (owner mindset)**:
- **优先复用昨日 ai-watch ⚡ URL** — horizon scan 已 surface 出每天最值得 ingest 的 1-2 条
- **Sonnet (不 Haiku)** — prompt cache 已能压住 ai-watch ≈ $0.05/天; ingest 任务要写 wiki concept, 质量优先于 0.5 美分差
- **冲突 = 升 approvals 不擅自合并** — 符合 vault "不擅自批准"原则

## 5. Javen 介入点

| 频率 | 动作 | 时长 |
|---|---|---|
| **每周 1 次** | 扫 `wiki/AI/.last-ingest-*` 看新加 concept | < 2 分钟 |
| **每周 0-2 次** | approvals.md 看 ⏳ 待审批列里 ai-ingest 冲突, 打勾或删 | < 3 分钟 |
| **每月 1 次** | jq 看 cost-tracker.jsonl ai-ingest 累计 | < 2 分钟 |
| **应急 (< 1 次/季度)** | daemon 跑歪 → touch KILL_SWITCH | 5 秒 |

**总计: 每周 < 5 分钟 ✓ 达标**

## 6. 应急 rollback

**1 命令立刻停** (KILL_SWITCH):
```
touch '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/automation/KILL_SWITCH'
```

**1 命令清掉本 daemon 加的所有 wiki/AI/ 内容** (git 部署后):
```
git checkout -- MyBrain/wiki/AI/ MyBrain/notes/web-research/ MyBrain/raw/web-research/
```

**软 rollback**:
- 删 `.claude/skills/ai-ingest/SKILL.md` → daemon Step 0.5(c) Read 失败 → 继续跑其他任务, 不爆
- 或 prompt.md 注释 Step 0.5(c) → 1 行改回

**单条质量翻车回滚**:
- 每天 ingest 先落 raw/web-research/ (不可修改) → 再衍生
- 翻车 concept 页 → 直接删 + log.md 加"撤销", raw/ 留作 evidence

## 7. 1 天构建计划 (实际预估 4 小时)

| 小时 | 动作 | 产出 |
|---|---|---|
| **H1** | 读 ai-watch SKILL + wiki/AI 3 篇 concept + CLAUDE.md Ingest 章节 | mental model |
| **H2** | 写 `.claude/skills/ai-ingest/SKILL.md` (~150 行, 抄 ai-watch 模板) | skill 文件 |
| **H3** | 改 prompt.md (+8 行 Step 0.5(c)) + rules.md (+5 行 rule 20) + README dashboard (+1 行) | 调度 hook + 护栏 |
| **H4** | 手动 dry-run: `wrapper.sh check` + manual claude -p 实测 0.5(c) 全流程 + validate 产出 | 端到端验证 |
| **H5** (备用) | debug + 修 skill prompt / 工具白名单 / 路径 bug | 修复 |
| **H6-8** | buffer | — |

**实际操作**: 建议在 task-027 BS/MS 5/15 提交完之后由主对话推进 (不让 daemon 自己写自己).

## 8. 风险 & 假设

| 假设 | 失败时怎么办 |
|---|---|
| claudian daemon 03:00 还在稳定跑 | dashboard 已监控; daemon 挂 → 本设计跟着挂, 不增风险 |
| ai-watch 持续每天产出 ⚡ URL | 回退 WebSearch fallback (skill 已设计) |
| 30 分钟 daemon 总预算够多塞 skill | 现 ai-watch ≈ 3 min, email-triage ≈ 4 min, ingest 估 5-7 min, 剩 15 min; 爆 timeout → "剩余时间 <5 min 则 skip" |
| Sonnet $2 budget 够 | 日均 < $0.5, +$0.1 远低于 cap |
| Javen 不希望 wiki/AI 被自动塞满 | approvals.md 当护栏; skill 设硬约束"每天最多 1 新 concept + 2 update" |
| 某天质量翻车 | 6.1 / 6.2 / 6.3 三档 rollback |
| Google Drive 同步延迟 | wrapper.sh 预检已 check CLAUDE.md 可达 |

## 差异化定位

A 估 5 新文件 / B 估 8-10 / C 估中等 (seed 10 wiki + scripts). **D 只 1 个新文件** + 3 处单行级微改, daemon / launchd / cost / 审批 / token / lock / kill-switch / fresh session 基础设施 **100% 复用**. 1 天搞定, 每周 Javen 介入 < 5 分钟, 每天成本 < $0.10.

## Critical Files

- `.claude/skills/ai-ingest/SKILL.md` (NEW — 唯一新增, ~150 行)
- `~/.claude-daemon/prompt.md` (MODIFY — Step 0.5(c) +8 行)
- `~/.claude-daemon/rules.md` (MODIFY — rule 20 +5 行)
- `.claude/skills/ai-watch/SKILL.md` (REFERENCE — 模板抄它)
- `MyBrain/CLAUDE.md` (REFERENCE — ingest pipeline 规范源)
