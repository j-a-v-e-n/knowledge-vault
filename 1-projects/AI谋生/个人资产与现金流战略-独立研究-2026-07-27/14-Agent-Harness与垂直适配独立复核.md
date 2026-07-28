# Agent、Harness 与垂直适配：独立复核

状态：完成当前一手来源与访谈字幕复核。旧文档只用于定位访谈 URL，没有作为结论证据。

## 精确来源

- 访谈：[Jensen Huang: Why companies need open agent systems](https://www.youtube.com/watch?v=Yy3JH6dDugc)
- 配套发布：[LangChain and NVIDIA launch the NemoClaw Deep Agents Blueprint](https://www.langchain.com/blog/langchain-and-nvidia-launch-the-nemoclaw-deep-agents-blueprint)
- 技术案例：[Tuning the harness, not the model](https://www.langchain.com/blog/tuning-the-harness-not-the-model-a-nemotron-3-ultra-playbook)
- 本轮直接获取英文字幕的身份记录：[`evidence/jensen-open-agent-interview-caption-identity-2026-07-27.json`](./evidence/jensen-open-agent-interview-caption-identity-2026-07-27.json)

字幕是 YouTube 提供的英文文本轨，可能含转写误差；下文使用时间定位和释义，不把字幕当经编辑的逐字稿。

## 访谈实际支持什么

- `00:01:23–00:02:19`：基础模型是必要能力，但有用产品还需要信息 grounding、工具、记忆、安全措施和迭代循环。这个上下文不支持“模型无所谓”。
- `00:03:16–00:03:49`：访谈把领域问题、内部知识和使用反馈循环放在专用系统的中心。
- `00:04:18–00:05:40`：领域化不是纯模型或纯 Harness；讨论同时包括足够强的模型、领域信息、Harness，以及可能在 Harness 中做 post-training。
- `00:05:44–00:06:16`：不同模型需要不同 prompt 和工具配置；这直接反驳“搭好同一个架构后模型随便换”。
- `00:08:50–00:09:28`：黄仁勋同时预计前沿模型、厂商 Harness、memory、compaction、retrieval 和知识图谱继续快速改善。通用层会被供应商继续吸收。
- `00:09:30–00:11:16`：他描述的实践是先用前沿模型看清能力上限，再为供应链、芯片设计等特定任务接入专用工具、知识和团队持续改进，而不是先训练一个没有真实任务的垂直模型。
- `00:13:10–00:14:35`：Harness 可以把既有业务流程变成 Agent 系统；成功运行后仍可继续改信息、Harness 和模型权重。
- `00:15:09–00:17:03`：长期控制对象被描述为公司的专门知识和能力，而不是某个通用编码或写作技能。

## 它不能证明什么

- 不能证明任何个人或小公司做通用 Harness 都有市场；LangChain 与 NVIDIA 正在销售相关框架、模型、运行环境和算力，观点有直接商业利益。
- 不能证明访谈中的内部 benchmark 可外推到所有领域、模型、成本和风险条件。
- 不能证明企业内部数据天然成为资产；还需要合法权利、质量、可迁移性、反馈闭环和收益捕获。
- 不能证明 post-training 是领域化的默认第一步；配套技术案例反而明确写出 Harness 先解决脚手架问题，稳定不变的能力缺口才指向权重。
- 不能证明通用框架本身不会被 AWS、Microsoft、Google、OpenAI、NVIDIA 或 LangChain 继续产品化。
- 不能证明某个垂直有现实需求、付款者或可交付性。

## 更准确的系统模型

不应使用“固定赛车手技术 + 随便更换发动机”的单向比喻。更准确的研究单位是：

> **模型 × Harness × 工具与数据 × 任务环境 × Eval × 权限与责任**

这些因素互相作用。模型较弱时，Harness 无法凭空补出能力；Harness 不匹配时，强模型也会浪费能力；任务和 Eval 不真实时，两者都可能只是在优化演示。

## 垂直适配决策树

### 先定义现实任务与 Eval

先写外部结果、失败、风险、成本、允许动作和人工接管。没有稳定任务集和 held-out 检验，就没有证据区分是系统改善还是记住测试。

### 再修事实、接口和确定性控制

- 领域事实变化快：优先检索、数据库或工具。
- 数据脏、身份不明、权限不足：先修数据和权限，不调模型。
- 每次必须遵守：放在模型外的确定性代码和提交门。
- 工具调用、上下文位置、循环和恢复不匹配：调整 Harness 与 middleware。

### 然后比较现成模型

用更强或更适合任务的现成模型检查能力上限。如果换模型比维护复杂定制更可靠且全成本更低，接受供应商能力，不把自建层当信仰。

### 最后才考虑 post-training

只有残余失败在稳定任务、稳定 Harness、未见测试和环境变化下仍重复出现，并且有合法数据、可训练模型、回滚和持续使用规模时，才值得训练。安全权限、错误目标、脏数据、无需求和无付款不能靠 post-training 修复。

## 对 Javen 的结论

访谈确实支持你的核心直觉：模型之外的系统、领域知识、工具、反馈和流程很重要，而且很多现有模型已经足以进入有用的 Agent 系统。但它也同时推翻两个更强版本：不是所有模型都可互换，通用 Harness 也不会天然由个人长期独占。

因此值得长期培养的是**领域化可靠系统的构建与诊断能力**；值得尝试积累的是**真实工作流、授权数据、失败 Eval、集成权和结果关系**；不值得押注的是**某个框架语法或一个没有领域接入的通用 Agent 壳**。

