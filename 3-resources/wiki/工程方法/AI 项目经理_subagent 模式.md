---
title: AI 项目经理 — Subagent 模式（模式 B）
type: synthesis
tags: [AI, agent, multi-agent, subagent, Claude Code, 系统设计]
sources:
  - https://docs.claude.com/en/docs/agents/sdk/subagents
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - Javen 2026-04-30 主对话决策"代替我的人力,让 AI 成为团队"
created: 2026-04-30
updated: 2026-04-30
confidence: medium
priority: active
---

# AI 项目经理 — Subagent 模式（模式 B）

> Claude Code 当项目经理,4 个 subagent 当员工。这是 [[AI 团队设计原则]] 第 5 building block (Orchestrator-Workers) 的具体落地。
>
> 本笔记是 [[task-board#task-019]] 的设计文档。

---

## 起点：Javen 的两条 Axiom 落地

[[AI 团队设计原则]] 起点是 Javen 提的两条:

> **Axiom 1**: AI = 员工——不同模型像不同岗位的员工
> **Axiom 2**: 团队管理是通用学问——AI 团队应 inherit 管理学

**Subagent 模式是这两条 axiom 在 Claude Code 里的最直接落地**:

| Axiom | 在 Claude Code 里 |
|---|---|
| 不同模型 = 不同员工 | `model: claude-haiku-4-5` (researcher 便宜) vs `model: claude-sonnet-4-5` (engineer 专业) |
| DACI 框架 | Javen=Approver / Main Claude=Driver / Subagents=Contributor / vault logs=Informed |
| Two-Pizza (3-5 人) | 现在 4 人(researcher / engineer / writer / reviewer) |
| Conway's Law | `.claude/agents/` 目录结构反映你想要的团队结构 |

---

## 三种"加员工"模式对比（[[超级个体_工具与杠杆]] 引用）

| 模式 | 实现 | 改动量 | 节省 | 决策时机 |
|---|---|---|---|---|
| **A. 模型路由** | `claude-code-router` proxy | 30-60 min | ~50× daemon | task-013, 5/5 后 |
| **B. Subagent + 多模型** ⭐ | `.claude/agents/<role>.md` | 已搭, ~1h | ~3-10× per task | **task-019, 现在** |
| **C. Multi-agent platform** | LangGraph/CrewAI 自写 | 数十小时 | 不一定 | 暂不做(Anthropic 三准则不全) |

**为什么模式 B 是当前甜区**:
- 不需要外部基础设施(纯 Claude Code 原生)
- 模型分层已经给 ~3× 价差(Haiku $1 vs Sonnet $3 per M tok)
- 跟 task-013 router 兼容——router 装好后只改 model 字段一行
- 直接服务两个 ECE project 的实际工作流

---

## 4 个员工的"岗位说明书"

### Researcher(调研员, Haiku $1/M tok)
- **职责**: 读 PDF / 笔记 / 网页 → 出摘要 + 引文
- **典型任务**: "读 [[Zhang_2015_TROIKA]] 出 200 字 lay summary + 5 条 key findings"
- **tools**: Read, Glob, Grep, WebFetch, WebSearch
- **不干**: 写代码 / 写报告 / 主观评价
- **iteration cap**: 5 次 WebFetch / 25 次工具调用

### Engineer(工程师, Sonnet $3/M tok)
- **职责**: 写代码 / 改代码 / 跑实验脚本
- **典型任务**: "在 troika_lite.py 加 vectorized_estimate_hr 支持批量,验证 sanity"
- **tools**: Read, Write, Edit, Bash, Glob, Grep
- **不干**: 调研 / 写报告 / 审稿
- **iteration cap**: 30 次工具调用

### Writer(写手, Sonnet $3/M tok)
- **职责**: 写论文 / 报告 / 文档 / vault 笔记
- **典型任务**: "写 ECE284 update report §3 Methodology, 2 页 ACM Large 风格"
- **tools**: Read, Write, Edit, Glob, Grep
- **不干**: 写代码 / 调研外部
- **iteration cap**: 20 次工具调用

### Reviewer(审稿员, Sonnet $3/M tok, 只读)
- **职责**: 审代码 / 审稿 / 找事实错——不动文件
- **典型任务**: "审 engineer 刚写的 train.py, 重点 OOM fix 是否引入新 bug"
- **tools**: Read, Glob, Grep, Bash(只读)
- **不干**: 修复 / 写新内容
- **iteration cap**: 25 次工具调用

---

## 关键设计决策(为什么这样)

### 为什么 4 个员工不是 5 / 6?

按 [[AI 团队设计原则]] **AI Two-Pizza = 3-5 subagent**。4 是甜区:覆盖 90% workflow + 协调成本可控。

加第 5 个( **planner** 拆 epic 任务?**evaluator** 跑 metric?)的话,目前还没看到稳定的真实需求。等 1 周后总结 [[lessons]] 再决定。

### 为什么 researcher 用 Haiku, 其他用 Sonnet?

**调研活 80% 是阅读理解 + 摘要**——Haiku 4.5 在这类任务上跟 Sonnet 几乎没差距,但便宜 3×。

**编码 / 写作 / 审稿涉及主观判断和复杂推理**——Sonnet 不能省。

(等 task-013 router 装好后, researcher 可以进一步降到 DeepSeek $0.14/M tok 或 Gemini Flash $0.15/M tok, 再省 7×。)

### 为什么 reviewer 是只读?

按 [[AI 团队设计原则]] 第 6 条:**只读 subagent 安全, 写操作 single-threaded**。

reviewer 不动文件 = 即使它误判,也不会"改坏代码"。Lead 拿着 review 报告自己决定派 engineer / writer 修。这避免了"二级误差放大"。

### 为什么不让 subagent 互通?

按 [[AI 团队设计原则]] 反 pattern 第 8 条:**共享 context 任务用 multi-agent 信息会分裂丢**。

Lead(主 Claude)是唯一中枢。所有 subagent 输出回流到 lead,由 lead 决定下一步。**像公司一样,经理是 information hub**。

### 为什么不用 Opus?

[[AI 团队设计原则]] Anthropic 实测显示 Opus(lead) + Sonnet(worker) 比纯 Opus 单 agent 高 90.2%。但**只有 lead 用 Opus 才有意义**——你已经在用 Sonnet 当 lead,先验证模式 B 跑通,再考虑要不要把 lead 升级到 Opus。

---

## 跟 task-013 (router) 的衔接

**Router 不是 subagent 模式的前置依赖,而是 cost 优化扩展**。

```
现在(模式 B 单独): 全部走 Anthropic
  Lead Sonnet ($3/M)
  └── researcher Haiku ($1/M)        ← 已经省 3×
  └── engineer Sonnet ($3/M)
  └── writer Sonnet ($3/M)
  └── reviewer Sonnet ($3/M)

router 装好后(模式 A + B 组合): 路由到便宜模型
  Lead Sonnet ($3/M, 不变)
  └── researcher → DeepSeek-V3.2 ($0.14/M)   ← 省 21×
  └── engineer → DeepSeek-V3.2 ($0.14/M)      ← 省 21× (但要测 quality)
  └── writer → DeepSeek-V3.2 ($0.14/M)
  └── reviewer → Sonnet ($3/M, 不变 — 审稿质量优先)
```

迁移成本:**改 3 个 markdown 的 `model:` 字段**, 1 分钟。

---

## 落到两个 ECE project 的具体场景

### ECE 175B (ADG diffusion)

```
场景 1 (本周): 主对话写完代码骨架, 但训练前要再 refine 一遍
  Lead: 把 train.py + adg.py 派 reviewer 审 → 发现 bug → 派 engineer 修 → 派 reviewer 验
  → 最终给 Javen "代码 ready, 可上 Colab"

场景 2 (5/13 midterm 前): 写 midterm report
  Lead 拆 4 子任务并行:
    - researcher: 读 proposal.pdf + 5 个 lecture notes 出 §1-2 motivation 草稿
    - engineer: 跑训练 logs + 出 loss curve PNG
    - writer: 用上述 input 写 §3-5
    - reviewer: 对比 proposal §3-5 找漂移
  Lead 整合 → Javen 审 → 提交
```

### ECE 284 (LLM-PPG)

```
场景 1 (本周): TROIKA-lite + RF baseline 实测
  Lead: 派 engineer 跑 troika_lite.py + rf_baseline.py LOSO
        → 派 writer 把 results/*.json 摘成一段进度更新
        → 写到 task-board task-018 子任务 + ECE284 README
  Javen 早起看一眼即可

场景 2 (5/20 update report): 写 6% update report
  跟 ECE175B 场景 2 一样的并行模式
```

### 看板推进(daemon 凌晨)

daemon 03:00 启动后, 主 Claude(lead) 看到 owner=@claude 的子任务, **现在可以把 subtask 派给具体 subagent**, 不用自己什么都干。

例如 task-018 子任务 c (跑 TROIKA-lite sanity check):
- 之前 daemon: 主 Claude 自己跑
- 现在 daemon: 主 Claude → 派 engineer 跑 → engineer 输出结果 → 主 Claude 写到看板

总成本: $0.01 (engineer Sonnet 跑 ~3000 tok)。比 lead 自己跑省 30%(因为 lead 不用 reasoning 跑代码这么细的事)。

---

## ⚠️ 已知风险 / 矛盾

按 [[AI 团队设计原则]] 反 pattern 列表:

1. **错误放大**: 如果 researcher 摘错事实, writer 用错事实, reviewer 没看出来 → 报告里有错。**缓解**: reviewer 必须对比 ground truth 不只看 writer 输出
2. **Token 爆炸**: subagent 内置 iteration cap 是缓解 #1 (researcher 25 / engineer 30 / writer 20 / reviewer 25 工具调用 / 单任务)。但累积 4 个 subagent 同时跑可能 60-100 工具调用——主 Claude 派活时**不并行 ≥ 3 个**
3. **角色定义模糊**: researcher 和 reviewer 都"读资料"——边界是 researcher 出**新摘要**, reviewer 跟 ground truth **对比找错**。markdown 里强制写明
4. **未必比 single-agent 强**: 部署后 1 周必须 `lessons.md` 总结哪些 task 用 subagent 后变好 / 变坏。**没 metric 的话回退**

---

## ✅ 部署清单 (task-019 子任务对照)

- [x] researcher.md
- [x] engineer.md
- [x] writer.md
- [x] reviewer.md
- [x] `.claude/agents/README.md`
- [x] 这份 wiki 设计文档
- [ ] smoke test (本 session 末)
- [ ] (5/5 后) router 装好换 model 字段
- [ ] (5/8 左右) 1 周复盘到 lessons.md

---

## 🔗 关联

- [[AI 团队设计原则]] — 总纲, subagent 模式由其推导
- [[超级个体_工具与杠杆]] — 三种"加员工"模式对比的起点
- [[claude-code-router-setup.md]] — 模式 A (router), 跟模式 B 互补
- [[task-board]] task-019 — 本系统的部署任务
- [[task-board]] task-017 / task-018 — 模式 B 直接服务的两个 project

## 📎 来源

- Javen 2026-04-30 主对话: "代替我的人力,让 AI 成为团队"
- [Anthropic Subagents docs](https://docs.claude.com/en/docs/agents/sdk/subagents)
- [Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system) — Opus + Sonnet workers 配置实测 +90.2%
- 已 deployed 的 4 个 subagent markdown: `/.claude/agents/{researcher,engineer,writer,reviewer}.md`
