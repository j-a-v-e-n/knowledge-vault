---
title: "综合：AI 浪潮下中国留学生（Javen）的工具选型与岗位选择"
type: synthesis
tags: [AI, 求职, 工具栈, Javen, 决策框架, 留学生, 实习]
created: 2026-05-11
updated: 2026-05-11
confidence: medium
priority: active
---

# 综合：AI 浪潮下中国留学生（Javen）的工具选型与岗位选择

> 这是把 [[综合_2026年AI工具栈的三重转变]] 的产业级判断**应用到 Javen 的具体处境**——美国 UCSD ECE 硕士 / 2026 summer 找实习 / 中国留学生 / 已投 Anduril / 对 AI 狂热。给一个**当下可执行的 strategic 决策框架**。

---

## 一、Javen 当前 baseline（事实清单）

**学业**：
- UCSD ECE 硕士，2025 入学
- 2026 Spring 课程：COGS117 (cognitive development) / ECE284 (digital health) / ECE175B (deep generative models) / PHIL28
- 主项目：ECE284 LLM-PPG 项目 + ECE175B ADG diffusion 项目

**求职**：
- 已投 Anduril × 2（EE Intern + SWE Frontier Systems Intern, 2026-04-28）
- Qualcomm Embedded / QGOV 状态混乱（窗口可能关闭）
- 目标 summer 2026 intern

**AI 资产**：
- vault 系统（CLAUDE.md + 4 sub-agent + 任务看板 + Memory Commit Protocol）
- 在用 Claude Code Pro + claude.ai
- AI 狂热者，但承认"很多不懂"

**约束**：
- 中国留学生 → 涉及 H1B / visa
- MacBook 用户（具体配置未知）
- 时间紧（要 balance 课程 + 实习准备 + AI 学习）

---

## 二、工具栈选型 (Owner Mindset 推荐)

### 2.1 主战场（保留 / 强化）

```
Claude Code Pro ($20/mo)
+ Claude.ai web ($20/mo Pro)
+ vault 系统 (Personal AI Workspace)
+ 4 sub-agent + skills + hooks
```

**为什么不换**：
- 你已经在最优位置（业内主流 + 生态最完整）
- vault 系统跟 Claude Code 深度耦合，换工具会破坏全部 metadata
- 学习曲线已 amortize

**强化方向**（这周做）：
1. Audit `.claude/settings.local.json` 的 permissions 配置 — 见 [[2026-05-11_Claude_Code_permissions提前授权]]
2. 试 Sub-agents 并行（你 vault CLAUDE.md 已经定义了 4 个 agent，但很多任务还在主对话独干）
3. 试 Routines — 把现有部分 launchd daemon 任务用 Routines 替代

### 2.2 副工具（添加）

```
Ollama (free)                           ← 本地推理
  ├ deepseek-coder:6.7b
  ├ llama3:8b
  └ qwen2.5-coder:7b

DeepSeek API (pay-as-you-go, $0.14-$3.48 per M tokens)
  └ 用于批量低 stake 任务
```

**为什么加**：
- Ollama 30 分钟装好，免费，离线能跑
- DeepSeek API 跑批量任务（vault inbox 整理 / 抖音字幕分析）省 Claude 钱
- **学习投资**：体验本地推理生态，未来面试可以聊

**适用场景**：
- vault 批量编译（你的 douyin-favorites 这种）
- 离线工作（飞机 / 火车）
- 不敏感的代码 utility 任务（命名 / docstring）

### 2.3 不必折腾 (delete from to-do list)

- **Cursor** — 跟 Claude Code 高度重叠，切换成本 > 价值
- **Cline** — 开源 alt 但缺高级 feature，学习用可看 source code
- **Devin** — $500+/月 + 自主度 mismatch
- **ds4 (Antirez)** — build 难度太高，等更易用 wrapper
- **SEQUENCE OS¹** — 不存在的产品，don't chase

### 2.4 Watch list (12 月内再 evaluate)

- **Cursor Background Agent** — 如果 catch up 到 Claude Code 自主度水平
- **OpenAI Codex CLI** — 如果 GPT-5 显著好于 Claude Opus
- **CodeBanana / Copilot Workspace** — 当你进入团队工作场景

---

## 三、求职策略 (B + C 双线并行)

### 3.1 总策略：B 主投 + C 保底，A 不押

| Path | 内容 | 风险 | 应届可行性 | Javen 行动 |
|---|---|---|---|---|
| **A. 直接走 FDE** | Anthropic / OpenAI FDE intern | 极高 | 5% | 投但不押 |
| **B. AI Application Engineer** | 大厂 AI 工程实习 | 中 | 30% | **主投** |
| **C. 传统 ECE 路径** | Anduril / Apple / Tesla ECE | 低 | 60% | **保底** |

### 3.2 Path C — Anduril 类传统 ECE 实习（已在执行）

**保留 + 优化**：
- 继续 monitor Anduril 投递状态（已投 2 个，等回复）
- 加投：Apple / Tesla / Lockheed Martin / Northrop Grumman / Raytheon
- Application material 已就绪，**rinse and repeat**

**Owner mindset**：这是 floor——offer 落袋让你睡得着，再去试 stretch goals

### 3.3 Path B — AI Application Engineer 实习（主投）

**目标公司**（按 likelihood + 薪资）：

**Tier 1 (Stretch)**：
- **Anthropic** — Applied AI Intern (如果有)
- **OpenAI** — Solutions Engineer Intern
- **Cohere** — AI Application Intern

**Tier 2 (Likely)**：
- **Google AI** — AI Engineer Intern
- **Microsoft Azure AI** — AI Solutions Intern
- **Amazon AWS Bedrock** — AI Solutions Intern
- **NVIDIA** — AI Application Intern

**Tier 3 (Fallback)**：
- **Hugging Face** — Open Source Engineer Intern
- **Together AI** / **Modal** / **Replicate** — AI 平台 startup
- **Scale AI** — AI Solutions Intern

**Action items 本周**：
1. 上 Anthropic Careers 看 FDE / Applied AI 岗位描述 — 抄要求清单
2. Update resume 加 "Personal AI Workspace System" portfolio item
3. 准备一个 "vault 系统" 的 demo video / writeup（让 recruiter 一眼看懂你 AI 能力）

### 3.4 Path A — FDE Direct (long shot)

**为什么试**：万一中了就 unicorn
**为什么不押**：应届 < 5% 成功率

**资源投入**：5% time
- 投：Anthropic FDE / OpenAI Forward Deployed Engineer (即便 full-time 也试)
- 当作 stretch experiment，**不要因为这个 delay 主战场 (B + C)**

---

## 四、Portfolio 升级 (用 vault 作为差异化武器)

### 4.1 把 vault 从 "hobby" 升级到 "engineering case study"

**旧 framing**:
"I built an Obsidian vault for knowledge management with Claude Code."

**新 framing**（给 AI 公司的 recruiter / interviewer）:
> "I designed and implemented a Personal AI Workspace System (~70 markdown files, 50+ structured concepts) demonstrating production-level AI engineering patterns:
> - **Vault-based persistent memory** (replacing unreliable Auto Memory)
> - **4 specialized sub-agents** with explicit tool boundaries (researcher/engineer/writer/reviewer)
> - **Memory Commit Protocol** ensuring cross-session knowledge persistence
> - **Constitutional governance** via CLAUDE.md (safety rules, raw/archive protection)
> - **Task board system** (shared state for human + AI collaboration)
> - **Automated daily reports** (email triage / AI trend / task check via launchd daemon)
>
> This system directly implements key design patterns of enterprise AI deployment: agent role specialization, context alignment, governance frameworks, and human-in-the-loop verification."

### 4.2 简历 bullet point candidates

**给 SWE / AI Engineer 角度**：
- "Architected a 70-page knowledge graph (Obsidian + Claude Code) implementing multi-agent orchestration with 4 specialized sub-agents and constitutional governance, demonstrating production-grade patterns for AI system design."

**给 Solutions Engineer / FDE 角度**：
- "Built a personal AI workspace serving as case study in enterprise AI deployment challenges: memory persistence, agent role boundaries, context alignment, governance via written constitution—anticipating real client implementation patterns."

**给 ML / Research 角度**：
- "Compiled and synthesized 30+ research papers (cognitive science, medical AI, LLM evaluation) using vault knowledge graph with structured frontmatter, internal wikilinks, and visual figure rendering pipeline."

### 4.3 Demo materials 准备

需要做（这个月内）：
1. **5 分钟 vault 系统 demo 视频** — 录屏说明：（a）你怎么用它学习；（b）4 sub-agent 怎么分工；（c）Memory Commit Protocol 怎么保证 cross-session 一致性
2. **GitHub README** — vault 系统的 architecture overview + 关键设计决策
3. **个人博客一篇文章** —《Building a Personal AI Workspace: Engineering Notes》记录设计哲学

---

## 五、学习投入 priority (这学期 + 暑假)

### 5.1 P0 (必须 by 暑假)

1. **RAG 框架实战** — LangChain 或 LlamaIndex
   - 做一个 ECE284 paper chatbot（RAG 14 篇 ECE284 reading + 引用对应论文 page）
   - 部署到 HuggingFace Spaces / Vercel
2. **Agent 框架** — AutoGen 或 CrewAI
   - 把你 vault 4 sub-agent 抽象成 reusable AutoGen / CrewAI 模式
3. **Evaluation 工程** — 怎么测 AI 应用对不对
   - DeepEval / Ragas / 自己写 eval pipeline

### 5.2 P1 (强烈推荐)

1. **MCP (Model Context Protocol) 深度** — 你已经在用 Gmail / Drive MCP，扩展到 GitHub / Notion MCP
2. **vector store** — Pinecone / Weaviate / Qdrant 选一个深入
3. **DSPy / 自动 prompt 优化** — 这是 prompt engineering 的 next-gen

### 5.3 P2 (Nice to have)

1. **Fine-tuning** — PEFT / LoRA (用 HuggingFace TRL)
2. **本地推理** — Ollama 装好就行（不必深入 llama.cpp）
3. **Multi-modal** — vision + audio 一起处理（FLUX / Whisper / GPT-4o）

### 5.4 Don't waste time

- ❌ 训前沿模型 (commoditize 了)
- ❌ Pure prompt engineering（吸纳进 AI Engineer）
- ❌ Web 开发深入（除非你想做 product founder）
- ❌ Web3 / NFT / metaverse（dead trend）

---

## 六、12 个月 timeline

### 现在 (5/11 - 6/30) — 春季学期收尾

- 5/12 ECE284 Med-HALT 演讲 ✓ ([[Pal_2023_MedHALT_演讲稿]])
- ECE284 + ECE175B 项目最终交付
- 投递 Path B Tier 1-2 公司 (Anthropic / Google AI / NVIDIA Intern)
- vault demo 视频 + GitHub README 准备

### 7-9 月 (Summer 2026) — 实习

- 主目标：拿到 Path B (AI Application) 或 Path C (Anduril 等) 实习
- 实习期间：积累 LLM 应用层 production 经验 + 拿 return offer
- 副项目：vault 系统继续 evolve（multi-model / 本地 / multimodal）

### 10-12 月 (Fall 2026) — 秋季学期

- 用实习经验找 full-time（如果 return offer 不理想）
- 投 Path A (FDE)（实习经验加身比应届有 leverage）
- 把 vault 系统 open source / 写 paper

### 1-5/2027 — 毕业前

- 拿 full-time offer
- 决定美国留下 vs 回国（见 [[AI agent 时代的团队与岗位]] §4.5）

---

## 七、关键风险 + 缓解

### 风险 1: AI 路径过于发散，主战场 (ECE 项目 / 课程) 受影响

**缓解**：
- AI 学习 < 30% time / 主战场 > 70%
- 不要因为 vault 玩得开心而 delay 课程作业
- 实习目标设置：先保 Anduril 类 floor，stretch 试 AI 公司

### 风险 2: 中国留学生 visa 卡 FDE 路径

**缓解**：
- FDE 类岗位通常高薪 + 不可替代 → H1B sponsor 概率高于普通 SWE
- 但仍然有 risk —— 保 Path C ECE 路径作 backup
- 长期：考虑 O1 / EB1 等更高 tier visa

### 风险 3: AI 工具栈快速变化 (你学的可能 6 月过时)

**缓解**：
- 学**概念** + **设计 pattern**（如 RAG / Agent / Eval），不是具体工具
- LangChain 过时可能 LlamaIndex 接班——你学的是"如何接 LLM 到外部数据"这个 pattern
- 关注 first principles，不押单一工具

### 风险 4: 主战场 (Anduril 类) 拒了 + AI 路径也没结果

**缓解**：
- 投递面铺更广（Path B Tier 2-3 都投）
- 准备校内 research opportunity 作为 floor backup
- 实在不行 gap year 续命

---

## 八、关键 metric (你这学期结束应该有的)

| Metric | Target | 状态 |
|---|---|---|
| 课程 GPA | ≥ 3.6 | 待跟踪 |
| ECE284 项目 final | Done + 高质量 | 在做 |
| ECE175B 项目 final | Done + 高质量 | 在做 |
| 投递公司数 | ≥ 15 | 2 (Anduril) → 需大幅扩 |
| 拿到的 OA / interview | ≥ 3 | 0 → 等待 |
| **AI portfolio 项目** | 至少 1 个 end-to-end LLM 应用 | 0 → **必须做** |
| **vault demo materials** | Video + README + Blog | 0 → **必须做** |
| 拿到的 offer | ≥ 1 | 0 → 待努力 |

---

## ⚠️ 这份 synthesis 的 limitation

- **基于当前已知信息**：你可能有未告诉我的约束（家庭因素 / 经济考虑 / 长期 vision），可能改变 ranking
- **AI 行业 6 月内可能再变**：本框架基于 2026-05 数据，半年后需要 refresh
- **依赖 Owner Mindset 的 judgment**：我作为 AI 不能替你决策——以上是"如果我是 Javen 我会怎么做"，不是"你必须这样"

## 🔗 关联

- [[综合_2026年AI工具栈的三重转变]] — 产业级判断的来源
- [[AI 编码工具生态全景]] — 工具选型详细
- [[本地大模型推理]] — 本地化路径详细
- [[AI agent 时代的团队与岗位]] — 岗位选择详细
- [[2026-05-11_AI落地咨询师岗位预测]] — 关键岗位 trend
- `MyBrain/career/applications.md` — 投递追踪（应该按上面 Tier 1-3 扩列表）
- `MyBrain/career/resume-master.md` — 简历升级（加 vault portfolio item）
- `MyBrain/automation/queue/task-board.md` — 任务看板（应该 reflect 这个 timeline）

---

**这份 framework 的 actionable 一句话总结**：

**Anduril 类 floor 投到底；同时把 vault 系统包装成 portfolio + 学 RAG/Agent 框架 + 投 Anthropic / Google AI Intern。两条腿走路，半年后无论哪个中都不慌。**
