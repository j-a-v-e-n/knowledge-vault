---
name: email-triage
description: 扫描 Javen 的 Gmail 收件箱（jacao@ucsd.edu），识别招聘 / OA / 面试 / 学校重要 / 其他高优先级邮件，写一份每日早报到 MyBrain/system/email-triage/。当用户说"扫一下邮箱"、"今天有啥邮件"，或 daemon 凌晨任务里包含此 skill 时调用。**默认只读**——不自动回信、不自动 label、不创建 draft（除非任务卡里明确放行）。
allowed-tools: Read, Write, Glob, Bash(date*), mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__list_labels, mcp__claude_ai_Gmail__list_drafts
---

# Email Triage — 每日邮箱筛选早报

每天早上扫 Javen 的 Gmail，挑出**他真正需要花时间处理的几封**，把 100 封无关邮件压缩成一页报告。

## 输出位置

`MyBrain/system/email-triage/YYYY-MM-DD.md`

**先 Glob 一下**：今天文件已经存在 → 不重写，跳过本次。每天最多一份。

## 触发的优先级 → 类别 → 行动建议

| 信号 | 类别 | Javen 应做的 |
|---|---|---|
| Recruiter / Hiring 联系 | 🔴 招聘 | 24h 内回 |
| OA 邀请 (HackerRank / CodeSignal / Karat / Codility) | 🔴 OA | 看 deadline，48-72h 完成 |
| 面试时间确认 / reschedule | 🔴 面试 | 立刻确认时间 |
| 拒信 | 🟡 拒信 | 知道一下，归档 |
| UCSD 课程公告（教授 / TA） | 🟡 学校 | 浏览，看是否有 deadline 调整 |
| 助学金 / financial aid | 🟡 学校 | 看是否需 action |
| **Anduril / Brain Corp / 已投递公司**任何信件 | 🔴 招聘（重点）| 立即看 |
| GitHub / LinkedIn 通知 | ⚪ 跳过详情 | 一句话归类即可 |
| 营销 / 订阅 / Newsletter | ⚪ 跳过详情 | 不进报告 |

## 扫描流程

### 1. 拿过去 24 小时的所有 thread

用 `mcp__claude_ai_Gmail__search_threads` 跑：

```
query: newer_than:1d
```

如果结果太多（>30 thread），改用：

```
query: newer_than:1d -category:promotions -category:social
```

进一步筛掉营销 + 社交噪音。

### 2. 对每个 thread 用 `get_thread` 拿 subject + 最新一封 body 摘要

**注意：** 不要把所有 thread 都 get_thread——这会浪费 token。先看 subject + sender 决定要不要展开。**只 get_thread 那些 subject/sender 看着像招聘 / OA / 面试 / 学校 / 已投递公司的**。

### 3. 分类 + 排序

按上表的优先级分组：
- **🔴 立即处理（top 1-3）**：当天必须回
- **🟡 当天看一下（3-5 条）**：不紧急但应知道
- **⚪ 已归类（计数）**：不展开，只报"N 封 GitHub / N 封 LinkedIn / N 封订阅"

### 4. 写报告

## 报告模板

```markdown
---
date: 2026-04-29
type: email-triage
threads_scanned: N
threads_surfaced: M
---

# Email Triage · 2026-04-29

> 过去 24h 收到 N 封，挑出 M 封要你看。其余 (N-M) 封是噪音/订阅，不展开。

---

## 🔴 立即处理（24h 内回）

### [发件人] — [简短主题]
- **来自**: full sender (e.g., `Anduril Recruiting <hr@anduril.com>`)
- **时间**: 2026-04-29 09:23
- **要点**: 1-2 句说邮件内容
- **建议**: 一句话行动建议（"24h 内简短确认 + 给 availability"）
- **Gmail 链接**: 给 thread ID 或 search shortcut，方便跳转

（如果 0 条，写"无紧急邮件"）

---

## 🟡 当天看一下

### [简短列表，每条 1-3 行]
- **[发件人]**: [主题] — [一句话要点 + 是否需要 action]

（最多 5 条，超过的归到 ⚪）

---

## ⚪ 已归类（不展开）

- N 封 GitHub 通知（PR / issue / star）
- N 封 LinkedIn 推送
- N 封课程相关 Canvas / Piazza（无紧急）
- N 封订阅 / newsletter
- N 封其他

---

*生成于 YYYY-MM-DD HH:MM by Claude (skill: email-triage)*
```

## 关键检查点

### "已投递公司"特别 surface

Javen 的 `MyBrain/career/applications.md` 里有他已投出的公司清单。
**先 Read 那份文件**，提取所有 "投出"状态的公司名 + recruiter 邮箱（如果有）。

发件人若匹配这份清单 → **强制 surface 到 🔴**，哪怕邮件内容看起来是自动回信。理由：可能藏着 OA 链接、面试邀请、reject 反馈。

### Recruiter / OA 关键词

subject 或 body 里出现以下关键词 → 自动归 🔴：

- "online assessment", "OA", "coding challenge", "HackerRank link"
- "interview", "schedule a call", "next round"
- "offer", "extend an offer"
- "internship", "position you applied"
- 公司 + "recruiter" / "recruiting" / "talent"

### 拒信识别

subject 包含 "regret", "unable to move forward", "other candidates", "after careful consideration" → 归 🟡 拒信，**不 surface 内容**，只列：

```
- ❌ [公司名]: 已拒
```

让 Javen 看一眼即可，不浪费 attention 上面。

## 边界情况

- **过去 24h 0 邮件**：写"过去 24h 无新邮件 — 全清"，结束
- **Gmail MCP 调用失败**：写"Gmail MCP 不可用：[error]"，**不要重试**，结束
- **某 thread get_thread 失败**（隐私 / 已删）：跳过那条，继续
- **某邮件 body 太长**（>3000 字）：取前 200 + 后 100 字，标"[middle truncated]"

## 不做的事

- **不创建 draft / 不自动回信 / 不 label / 不 archive**：这是 read-only triage skill
- **不修改 applications.md**：这个 skill 只读邮箱、读 applications.md，不写 applications.md
- **不在报告里 paraphrase 完整邮件正文**：用要点 + 行动建议，不要复述
- **不抓 promotions / social 类**：search 时已经过滤掉了，不再 surface
- **不替 Javen 决定回不回**：报"建议 X"，决定他做
- **不抓超过 24 小时**：每天看一份，重叠会重复 surface 同一封

## 升级路径（未来可能开启，**当前不开启**）

如果 Javen 后续明确说要：
- 自动 label 招聘邮件 → 加 `mcp__claude_ai_Gmail__label_thread` 到 allowed-tools
- 自动起草礼貌回信草稿 → 加 `mcp__claude_ai_Gmail__create_draft`，但**永远 draft 不发送**
- 自动 archive 营销邮件 → 加 `mcp__claude_ai_Gmail__unlabel_thread` (从 INBOX 移走)

升级时改本文件 frontmatter 的 `allowed-tools` 字段，并在 daemon 的 wrapper.sh 里同步加白名单。
