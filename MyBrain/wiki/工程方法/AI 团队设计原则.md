---
title: AI 团队设计原则
type: synthesis
tags: [AI, agent, multi-agent, 团队管理, 系统设计, 方法论]
sources:
  - https://www.anthropic.com/research/building-effective-agents
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://cognition.ai/blog/dont-build-multi-agents
  - https://arxiv.org/abs/2503.13657
  - https://arxiv.org/abs/2304.03442
  - https://arxiv.org/abs/2307.07924
  - Javen 2026-04-28 提出的两条 axiom
created: 2026-04-28
updated: 2026-04-28
confidence: medium
priority: active
---

# AI 团队设计原则

> 设计 vault 内任何"由多个 Claude 协作"的系统前先翻这页。基于 Javen 提出的两条 axiom + 业内已验证 framework + 真实事故经验提炼。

---

## 起点：两条 Axiom（Javen 2026-04-28 提出）

**Axiom 1（AI = 员工）**：不同 AI 模型像不同员工——能力 / 工资 / 性格各不同。设计系统时**像 hiring manager 一样按 JD 匹配员工**，而不是默认派给"那个最贵最强的"。

**Axiom 2（团队管理是通用学问）**：管理学已成熟 100+ 年。**AI 团队应当 inherit 通用智慧**（DACI、Conway's Law、two-pizza 等），而不是从头发明。但要识别哪些原则 AI 不需要（如心理安全、ego 管理）。

这两条是 vault 所有 AI 系统设计的**第一性原理**。后面所有具体规则都从这两条派生。

---

## 反直觉的核心立场：默认 single-agent

业内最重要的两个声音都在说同一件事：

> **Anthropic（Building Effective Agents, 2024-12）**："Start with simple prompts... add multi-step agentic systems only when simpler solutions fall short."

> **Cognition / Devin 团队（Don't Build Multi-Agents, 2025）**：单 agent + Context Engineering 比 multi-agent 更可靠；多 agent 像传话游戏导致 context 丢失。

**为什么**（数据说话）：
- Multi-agent 烧 **15×** tokens of single chat（[Anthropic 实测](https://www.anthropic.com/engineering/multi-agent-research-system)）
- 无结构 multi-agent 错误放大 **17.2×**（每 agent 输入是上 agent 输出，错误级联）
- 79% 的 multi-agent 失败来自**角色定义模糊 + 协调失败**，不是模型能力不够

**结论**：**默认 single-agent + Context Engineering**。Multi-agent 只在以下三条**全部**满足时才上：

1. 任务高度可并行（多个独立子任务）
2. 信息总量超过单 agent 的 context window
3. 需要多个复杂工具的不同领域专长

⚠️ **不要用 multi-agent 的场景**（Anthropic 自己说的）：
- Coding（依赖太重，不并行）
- 需要共享上下文的任务（split 后丢信息）
- 简单查询（杀鸡用牛刀，10× 成本无收益）

---

## Anthropic 5 个 building blocks（按复杂度递增）

设计任何 agent 系统前，**先看这条简单到复杂的阶梯**——能用第 1 条就别用第 5 条：

| # | Pattern | 用法 |
|---|---------|------|
| 1 | **Prompt Chaining** | 顺序分解，每步一个 prompt（最简单）|
| 2 | **Routing** | 分类后分流到不同处理路径 |
| 3 | **Parallelization** | sectioning（并行做不同部分）/ voting（多次跑同任务取共识）|
| 4 | **Orchestrator-Workers** | 主控动态委派 subagent |
| 5 | **Evaluator-Optimizer** | 生成 + 反馈循环，迭代改进 |

**Javen 当前 vault 的位置**：
- 看板系统 = ① Prompt Chaining（按看板任务顺序处理）
- daemon dawn-shift = ④ Orchestrator-Workers（雏形：主 prompt 派 subagent 做 ingest）
- 还没用 ② / ③ / ⑤——大概率不需要，除非系统真的 scale 到那个复杂度

---

## 模型员工档案（2026-04 当前 SOTA）

| 模型 | $/1M (in/out) | Context | 专长 | 性格 |
|------|--------------|---------|------|------|
| **Claude Opus 4.7** | $5/$25 | 1M | 复杂推理、长任务、agent 编排 | 谨慎，工具调用稳 |
| **Claude Sonnet 4.6** | $3/$15 | 1M | 编码 SOTA（SWE-bench 79.6%）、性价比之王 | 默认主力 |
| **Claude Haiku 4.5** | $1/$5 | 200K | fast triage、分类 | 快速回答 |
| **GPT-5** | $0.625/$5 | 400K | 性价比通用 | 主力 |
| **Gemini 2.5 Pro** | $1/$10 | 1M+ | 多模态、长 context、视频/PDF | 谷歌生态 |
| **Gemini 2.5 Flash** | $0.15/$0.60 | 1M | 极致性价比 fast triage | 大量分类用 |
| **DeepSeek V3.2** | $0.14/$0.28 | 128K | 中文、编码、便宜 | 预算王 |
| **DeepSeek R1** | 低价 | - | 推理链、数学 | OSS 可自托管 |

### 任务-模型 Matching Matrix

| 任务 | 推荐模型 | 理由 |
|------|---------|------|
| 编码 / refactor | **Sonnet 4.6** | SWE-bench 接近 Opus，便宜 5× |
| 复杂推理 / 编排 | **Opus 4.7** (lead) + **Sonnet** (worker) | Anthropic 实测此配置比纯 Opus 单 agent 高 90.2% |
| Triage / 路由 / 分类 | **Haiku 4.5** 或 **Gemini Flash** | sub $1，fast |
| 长 PDF / 多模态 | **Gemini 2.5 Pro** | 1M context + native multimodal |
| 数学 / 推理链 | **DeepSeek R1** 或 **GPT-5** | 推理强 + 便宜 |
| 中文 + 预算紧 | **DeepSeek V3.2** | $0.14/M |

**API 网关推荐**：个人 vault 项目用 **OpenRouter**（一个 key 通 200+ 模型，零配置）。系统稳定后再考虑 LiteLLM 自托管做 fallback 链。

---

## 团队管理学 → AI 系统的映射

| 经典原则 | AI 系统对应 |
|---------|-----------|
| **Conway's Law** | 系统反映组织通讯结构。**Inverse Conway**：先设计想要的 agent 架构，再倒推 vault 文件结构 |
| **Two-Pizza Rule**（Amazon）| AI 团队甜区 = **3-5 个 subagent**，再多协调成本爆炸 |
| **DACI**（Driver/Approver/Contributor/Informed）| 比 RACI 更适合 AI——动态委派友好。Javen=Approver，orchestrator=Driver，subagents=Contributor，日志=Informed |
| **Spotify Squads/Chapters/Guilds** | Squads=临时任务团队（一次 ingest），Chapters=技能维度（vault 的 `.claude/skills/` 就是 Chapters） |
| **Tuckman Forming-Storming-Norming** | AI 团队**没 Storming/Norming**（无 ego），但有"prompt 调试期"对应 Forming——新 agent 需 2-3 轮 dry run |
| **Lencioni 5 Dysfunctions** | AI **不需担心**信任 / 怕冲突 / 缺承诺；**仍需担心**：责任不清（谁该终止 loop）、结果忽视（没 eval）|

---

## 已知反 pattern（10 条警示）

1. **错误放大**：无结构 multi-agent 错误放大 17.2×
2. **Token 爆炸**（真实事故）：Claude Code subagent 跑 npm install 300+ 次 / 4.6 小时 / 27M tokens；LangGraph agent 2847 次迭代 $400+ 做 $5 任务
3. **无终止条件**：循环对话因缺退出条件、模糊 prompt、记忆截断重启
4. **不必要 multi-agent 化**：单 agent 能做的别 over-engineer
5. **一致性偏差**：同 base model 的 agents 同时盲——需异构模型才能真正 debate
6. **角色定义模糊**：每 subagent 必须有 objective + output format + tool list + boundaries
7. **Coding 类用 multi-agent**：Anthropic 自己说不适合
8. **共享 context 任务用 multi-agent**：信息分裂后丢
9. **不必要 debate**：简单查询用 debate 10× 成本
10. **没 eval 就上 multi-agent**：没 metric 你不知道是否真比 single 好

---

## 给 Javen vault 系统的 10 条 actionable 原则

按对**当前 vault 系统的实际价值**排序：

1. **默认 single-agent + Context Engineering**。Multi-agent 只在 Anthropic 三准则全部满足时启动。
2. **Lead=Opus, Workers=Sonnet** 是被 Anthropic 实测验证的配置。Javen 的 vault ingest 编排可直接复用。
3. **AI Two-Pizza = 3-5 subagent**。看板任务并行度先卡 5。
4. **DACI 比 RACI 适合 AI**。Javen 永远是 Approver，决策权留人手里。
5. **每个 subagent 必装三件套**：hard iteration cap (≤10) + token budget (硬上限) + 显式终止条件。这是反 $400 烧钱事故的最低成本保险——daemon 已经做了（max-budget-usd + max-turns + perl alarm）。
6. **只读 subagent 安全，写操作 single-threaded**。Javen 的 ingest 让多个 worker 各自 search/render PDF（只读），最后合并写 wiki/ 由单 agent 串行做。
7. **Skills = Chapters，Tasks = Squads**。vault 已有的 `.claude/skills/` 是横向能力库，看板任务是纵向交付单元——这个对应非常优雅，继续做。
8. **Reflexion > Self-refine**。编译完一篇 source 后让**第二个 agent**（异构模型更好，如 GPT-5）critique，比同模型自评有效。
9. **OpenRouter 起步，等系统稳定再迁 LiteLLM**。个人项目别一开始就上自托管 proxy。
10. **Evaluation first**。在搭 multi-agent 前先定义"怎么算成功"。vault 的 lint skill 是雏形 eval，可扩展成 benchmark。

---

## 🚦 决策流程图（设计新 agent 系统时跑一遍）

```
新需求来了 → 单 agent + 好 prompt 能解吗？
                ├─ 能 → 就做单 agent。结束。
                └─ 不能 → 是哪种"不能"？
                          ├─ 任务能并行 (parallel-able) → ③ Parallelization
                          ├─ 信息超 context → ④ Orchestrator-Workers
                          ├─ 输出质量需迭代 → ⑤ Evaluator-Optimizer
                          ├─ 流程要分类分流 → ② Routing
                          └─ 单纯长流程 → ① Prompt Chaining

任何复杂方案上线前必须先做：
  ✅ 列每个 agent 的 objective + output format + tool list + boundaries
  ✅ 设计 hard iteration cap + token budget + 终止条件
  ✅ 定义"怎么算成功"的 eval metric
  ✅ 跑一次 dry-run 看 token 消耗 vs 单 agent 对比
```

---

## ⚠️ 矛盾与未解决问题

- **Anthropic 内部立场略有矛盾**：一边说"先简单"，一边宣传 multi-agent research system 比单 Opus 高 90.2%。**调和方式**：multi-agent 在**特定任务类型上**确实更好（research / 高度并行），但**作为默认范式**还是 single agent。
- **Cognition 立场 9 个月内从"don't"软化到"only readonly OK"**——业内对 multi-agent 的认知仍在演化。本文档**应每 6 个月 review**一次。

---

## 🔗 关联

- [[2026-04-27_AI任务面板自动化系统]] — 思瑶视频，触发本文档思考的最初源头
- [[经验教训]] — debug 方法论，跟本文都是 vault 的"元规则"
- [[task-board]] — 看板系统就是 Orchestrator-Workers pattern 的具体实现

## 📎 来源

外部来源（22 个，按重要性排）：

**Anthropic 官方（最权威）**：
- [Building Effective Agents (2024-12)](https://www.anthropic.com/research/building-effective-agents)
- [How we built our multi-agent research system (2025-06)](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)

**counter-narrative（同等重要！）**：
- [Cognition — Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- [Cognition — Multi-Agents: What's Actually Working](https://cognition.ai/blog/multi-agents-working)

**学术**：
- [Why Multi-Agent LLM Systems Fail (arXiv 2503.13657)](https://arxiv.org/html/2503.13657v1)
- [Generative Agents (Park 2023)](https://arxiv.org/abs/2304.03442)
- [ChatDev (2023)](https://arxiv.org/abs/2307.07924)
- [Reflexion 框架](https://www.promptingguide.ai/techniques/reflexion)

**业内框架对比**：
- [LangGraph vs CrewAI vs AutoGen — DataCamp](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)
- [LiteLLM vs OpenRouter](https://www.truefoundry.com/blog/litellm-vs-openrouter)

**模型定价（截至 2026-04）**：
- [Anthropic Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Claude API Pricing — BenchLM](https://benchlm.ai/blog/posts/claude-api-pricing)
- [OpenAI / Gemini / DeepSeek pricing](https://www.tldl.io/resources/)

**Javen 个人洞察**（本文档的 axiom 起点）：
- 2026-04-28 主对话：AI=员工 + 团队管理是通用学问

---

> **使用建议**：每次设计新 agent / 改动 daemon prompt / 加新 skill 之前，**先翻这页确认设计落到哪条原则上**。如果落不到任何一条，要么需求被过度复杂化（退回简单方案），要么本文档需要更新（加新原则）。
