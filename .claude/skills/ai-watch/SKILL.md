---
name: ai-watch
description: 每日 AI 趋势扫描 + 写一份早报到 MyBrain/research/ai-watch/。设计原则 70% 启发好奇心（broad horizon、值得了解的有趣进展）/ 30% 落地建议（连到 Javen 的 ECE148 / 175A / 175B / 找实习场景，能实际用上的）。当用户说"AI 早报"、"今天 AI 圈有什么新东西"，或 daemon 凌晨任务里包含此 skill 时调用。
allowed-tools: Read, Write, WebSearch, WebFetch, Glob, Bash(date*), Bash(ls*)
---

# AI Watch v2 — 每日 AI 趋势早报

每天扫一遍最新 AI 进展，写一份**给 Javen 看的**早报。Javen 是 UCSD ECE 大三、ML/Robotics/Controls 方向、正在找 2026 暑期实习。

## 设计原则（不要忘）

- **70% 启发好奇心**：让他了解"AI 圈这周在发生什么有意思的事"，扩视野
  - 包括：新模型 release、新论文、新工具、新应用、技术争论、有意思的 demo
  - 不局限于他当前需求——他需要"知道 AI 圈是流动的"
- **30% 落地建议**：连到他的实际场景
  - "这个能怎么用在你 ECE148 final？"
  - "这跟你 175A 的 pattern recognition 内容相关，可以补充"
  - "这家公司在用这个 stack——你简历可以加 keyword X"
  - "这个开源项目能 fork 当作 portfolio"

## 输出位置

`MyBrain/research/ai-watch/YYYY-MM-DD.md`

**先 Glob 一下**：今天文件已经存在 → 不重写，跳过本次。每天最多一份。

## 信息源（**轮换扫**，不是每个都扫一遍）

每次随机选 3-4 个，避免每天都看一样的：

### Tier 1: 厂商官方（信号最强）
- https://www.anthropic.com/news
- https://openai.com/news/
- https://blog.google/technology/ai/ (Google AI)
- https://ai.meta.com/blog/
- https://huggingface.co/blog
- https://www.together.ai/blog

### Tier 2: 学术 / 社区
- https://huggingface.co/papers (每日热度论文)
- https://arxiv.org/list/cs.AI/recent (cs.AI 最新)
- https://arxiv.org/list/cs.RO/recent (cs.RO 最新, 跟 Javen ECE148 相关)
- https://arxiv.org/list/cs.LG/recent (cs.LG 最新, 跟 Javen 175A 相关)
- https://bair.berkeley.edu/blog/
- https://ai.googleblog.com/

### Tier 3: 工具 / 工程
- https://github.com/trending?since=daily&language=python
- https://news.ycombinator.com/

## 扫描流程

1. **WebSearch**: 用 1-2 个广撒网 query，比如：
   - `"Anthropic" OR "OpenAI" OR "DeepMind" announcement 2026 04`
   - `robotics foundation model release April 2026`
   - 注意：query 里**带具体年月**，避免拿到陈旧结果

2. **WebFetch top 3-5 URLs**：从搜出来的链里挑信号最强的（厂商官方 > arXiv > 社区博客 > 推文）

3. **筛选标准**：
   - ✅ 有实质内容（不是 PR 软文）
   - ✅ 跟 Javen 方向有交叉（ML / robotics / controls / embedded AI / coding agent）
   - ❌ 跳过：纯 hype 但没技术细节的帖子、纯营销公告
   - ❌ 跳过：跟 Javen 完全无关领域（如 generative art / AI 法律）

4. **写早报**：按下面模板

## 早报模板

```markdown
---
date: 2026-04-28
type: ai-watch
sources_count: 4
---

# AI Watch · 2026-04-28

> 今日扫了 N 个 source，挑出 M 项值得你知道的。
> ⚡ = 强建议看 / 🔍 = 知道一下 / 💡 = 有 Javen 的落地切入点

---

## 70% — Broad Horizon

### ⚡ [一句话标题，最值得看的那条]
- **What**: 1-2 句说这是什么
- **Why interesting**: 为什么值得知道（不是为什么对 Javen，而是为什么 AI 圈的人都该知道）
- **Source**: [WebFetch URL] (fetched YYYY-MM-DD)

### 🔍 [次重要的几条，每条 3-5 行]
（同样格式，2-3 条）

---

## 30% — Land Mode

### 💡 给 Javen 的落地切入点

把上面 70% 里跟 Javen 有连接的那几条挖深。每条要回答：

- **直接关联**: 这跟你 [ECE148 / 175A / 175B / 找实习] 有什么具体连接？
- **能怎么用**: 一句行动建议（"加进 final project demo 视频"、"跟教授提一下用这个 baseline"、"简历里加 keyword X"、"花 30 分钟跟一下 tutorial"）

> 如果 70% 里没有任何条目能连到 Javen，这一节写 "**今日无强落地切入点**——但保持 horizon scan，下次见"。**不强行造连接**，假大空。

---

## 📎 来源

- [URL 1] (Tier 1)
- [URL 2] (Tier 2)
- ...

---

*生成于 YYYY-MM-DD HH:MM by Claude (skill: ai-watch)*
```

## 长度约束

- 整份早报 ≤ 600 字（Javen 早起 5 分钟扫完）
- 70% 部分 3-5 条
- 30% 部分 1-2 条（连不上就说连不上，**不造**）

## 边界情况

- **WebSearch 拒绝 / 没结果**：写一行 "今日 search 失败：[具体原因]"，不要 fallback 编内容
- **所有 sources 都没新东西**（已经写过 / 跟昨天重复）：那就不写这份，记一句"今日无新进展，跳过"到 daemon-runs 即可
- **多个 source 互相矛盾**（罕见但可能）：在 70% 里标 ⚠️，列两边各自论点
- **不可达的 URL**（403 / 限流）：跳过那条，写下其他的

## 不做的事

- 不抓低质内容（SEO 农场、标题党、纯产品发布会无技术细节的）
- 不重复已经在 ai-watch 出现过的旧消息——先 Glob 一下过去 7 天文件，扫扫主标题
- 不在 30% 部分编"看似有用"的连接（比如 "这个 LLM 跟你 ECE148 有关因为都用到 Python"——这种空话不写）
- 不深度解析单篇论文（那是 ingest 的活，ai-watch 只做 surface scan）
- 不替 Javen 决定"该花时间学 X"——给信号、给切入点，决策权他的
