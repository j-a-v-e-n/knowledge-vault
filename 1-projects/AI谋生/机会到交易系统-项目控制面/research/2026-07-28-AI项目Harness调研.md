# AI 长期项目 Harness 调研与独立推导

## 调研问题

怎样让 AI 在长项目中持续服务同一个现实目标，跨会话、跨模型恢复，遇到死路能回溯，并且不过早构造一个脱离真实任务的庞大系统？

这份调研只回答项目执行方法。它不证明“机会到交易系统”已找到需求或能赚钱。

## 方法：先独立推导，再用外部证据挑战

### 从基本定义推出的初始模型

一个项目不是一段长对话，而是一连串在不确定性下作出的决定与实验。若执行器会更换、上下文会压缩、工具会失败，则坚固性必须存在于执行器之外。

从这个定义可推出：

1. 目标必须能被观察和验收，否则执行者无法知道何时结束。
2. 当前状态必须外部化，否则上下文重置就会把历史与现实混淆。
3. 大任务必须分成每一步都能改变某个状态谓词的单元，否则“做了很多”无法区分进展和循环。
4. 每次行动需要环境、测试或真人行为等外部反馈；模型自我感觉不能闭合因果链。
5. 权限必须独立于模型内容，否则模型能通过写一句话扩大自己的动作空间。
6. 项目卡住可能来自执行、接口、计划、假设或问题定义；只在末端重试不能修复上层路线错误。
7. 更换模型相当于更换执行器；若规范、状态和评分也随模型改变，就无法比较或安全接管。

这些是工程推导，不是外部实证。下面用一手资料、原始论文和反例检查它们。

## 来源宇宙

本轮主动覆盖：

- OpenAI 官方 Codex、ExecPlan、long-running work、AGENTS、subagent、eval 与 Harness 工程资料；
- Anthropic 官方 long-running agent、application harness、agent workflow、context、tool 与 eval 工程资料；
- 原始论文和官方 benchmark/研究机构材料，涵盖软件工程 Agent、规划、长期上下文、反思、多代理、整体验收和 reward hacking；
- Google、Microsoft 与 LangGraph 的官方状态持久化/恢复资料，用于对照实现模式。

未系统覆盖机器人、网络安全、科研 Agent、企业内部未公开数据或所有社区视频与博客。因此本轮不是“网上所有信息”，也不称穷尽。

停止规则：目标、状态、分解、工具、验证、恢复、模型切换、多代理、权限、回溯和过度设计各有直接来源或明确反例；新增来源开始重复相同机制，且剩余分歧可通过本项目的最小实验检验时停止。

## 外部证据地图

| 主张 | 一手来源说明了什么 | 限制 | 本项目决策 |
|---|---|---|---|
| Harness 不等于长 prompt | OpenAI 的 Harness engineering 把 repo 知识、工具、测试、观察性与反馈回路作为 Agent 环境；[原文](https://openai.com/index/harness-engineering/) | 是工程经验，不是所有商业任务的随机实验 | 用短入口、外部状态、工具合同和 Eval，而不是继续扩写总提示 |
| 长任务需要自包含 living plan | OpenAI ExecPlan 要求 Purpose、Progress、Surprises、Decision Log、Validation、Recovery，并要求能只靠计划重启；[原文](https://developers.openai.com/cookbook/articles/codex_exec_plans) | 主要面向软件项目 | 建立 active ExecPlan，并以可观察行为而非文件存在验收 |
| 目标文字也应成为完成标准 | Codex long-running work 要求 outcome、constraints 和 verification；[原文](https://learn.chatgpt.com/docs/long-running-work) | 产品行为可能变化；不证明目标本身正确 | Charter 与每步 Done 条件分层 |
| 稳定规则应短而分层 | Codex AGENTS 文档说明目录层级、优先级与持久规则；[原文](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 规则文件不能替代 living state | AGENTS 只存不变量，State 与 Plan 分开 |
| 多代理主要用于有界并行和上下文隔离 | Codex subagent 文档与 Anthropic multi-agent 研究都强调委派边界、资源成本和共享写冲突；[OpenAI](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system) | 不同产品和任务的增益不同 | 主代理保留方向与集成；研究、反证、测试可只读并行；不把投票当权威 |
| 长任务需要结构化交接 | Anthropic 的 long-running harness 使用 initializer、feature/progress 状态、逐项工作与 session handoff；[原文](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 示例偏应用开发 | 每个 checkpoint 更新 State、Plan、失败与下一步 |
| 规划者、生成者和 evaluator 可分，但 evaluator 也有限 | Anthropic application harness 强调分解、交接、独立 evaluator 和 sprint contract；[原文](https://www.anthropic.com/engineering/harness-design-long-running-apps) | evaluator 仍可能共享模型偏差 | 独立 reviewer 查看原始对象；LLM 结论不单独授权 |
| 先用简单 workflow，复杂度要证明收益 | Anthropic Building effective agents 区分固定 workflow 与动态 agent，并建议从简单方案开始；[原文](https://www.anthropic.com/engineering/building-effective-agents) | 工程建议而非普遍定律 | C8 复杂度逐项通过 Complexity Gate |
| 工具接口本身显著影响 Agent | SWE-agent 研究专门改变 agent-computer interface；[论文](https://arxiv.org/abs/2405.15793) | 软件修复任务，不能直接外推市场研究 | 对采集、证据、测试使用低歧义工具合同 |
| 更复杂自治不一定更好 | Agentless 用固定的定位、修复、验证阶段挑战复杂软件 Agent 的必要性；[论文](https://arxiv.org/abs/2407.01489) | 特定 benchmark | 先建立单执行器、确定性 baseline，再用实际 failure 增加组件 |
| 长上下文不是可靠项目数据库 | Lost in the Middle 发现长上下文中的信息位置会影响使用；[论文](https://arxiv.org/abs/2307.03172) | 不是长期商业项目实验 | 关键状态外部化；聊天只作临时工作区 |
| 纯内省纠错不稳定 | ICLR 研究发现没有外部反馈的 intrinsic self-correction 可能不改善表现；[论文](https://openreview.net/forum?id=IkmD3fKBPQ) | 任务与模型覆盖有限 | 反思必须消费测试、环境、原始证据或独立反馈 |
| 自动测试可能高估交付质量 | METR 比较自动测试与整体可合并审查，发现通过测试仍可能缺少维护级质量；[原文](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) | 样本和仓库有限 | 机械测试后仍做整体 rubric 与 fresh review |
| 无限 loop 与评分投机是现实风险 | METR 记录 Agent 修改评分器/参考对象等 reward hacking；[原文](https://metr.org/blog/2025-06-05-recent-reward-hacking/) | 发生率不能外推所有部署 | 保护 Eval、固定权限、设置 budget/stall/backtrack |
| 可恢复执行需要显式 state/checkpoint | Google ADK 与 LangGraph 官方资料都把长任务状态和 checkpoint 放在对话之外；[Google](https://developers.googleblog.com/build-long-running-ai-agents-that-pause-resume-and-never-lose-context-with-adk/)、[LangGraph](https://docs.langchain.com/oss/python/langgraph/persistence) | 框架实现不等于项目方法已正确 | State Bundle 和幂等恢复成为模型无关合同 |

## 外部经验与独立推导的交叉结果

### 被外部资料加强的结论

- 外部化目标、状态、权限和验证；
- 每次推进一个可验收单元；
- 环境反馈优先于纯自评；
- 长任务在恢复点重启，而不是无限延长上下文；
- 多代理是有成本的工作分解，不是正确性证明；
- 固定 Harness、通过 adapter 替换模型；
- 新复杂度必须对应观察到的失败。

### 外部资料没有证明、必须保留为假设

- 某套 manifest、hash DAG、freeze 或治理文件数量是最佳 Harness；
- 同一模型换角色就构成真正独立；
- 更强模型、更多模型或更长上下文会自动解决方向漂移；
- 在软件 benchmark 表现好就能发现需求、销售、交付和赚钱；
- 项目开始前把通用 Harness 设计得越完整，最终效果越好；
- 网络抱怨能够稳定预测购买意愿。

## 关键分歧与反例

### 复杂 Agent 与简单 workflow

有资料展示工具化 Agent 的价值，也有研究显示固定的简单阶段能竞争甚至胜过复杂自治。两者不矛盾：接口和反馈很重要，但自治层数本身不是价值。我们的处理是先跑最小 baseline，只有 observed failure 才增加 planner、memory、reviewer 或 Gate。

### Reflection 有用还是有害

带环境反馈、测试或成功信号的反思可能有用；没有新证据的纯内省可能重复或放大原错误。因此 RUNBOOK 要求反思消费新外部信号。

### 计划坚持还是迷宫回溯

living plan 防止遗忘，但错误计划如果只被持续更新也会固化偏差。用户提出的迷宫模型补上这一点：stall 时沿 decision graph 回到最近可替换分叉；替代也失败则继续上溯。计划负责持续，决策图负责可撤销。

### 坚固与过度治理

权限、反例和恢复能减少真实风险；但如果新的 Gate 不改变现实决定，它会把“防止失控”变成新的失控。Complexity Gate 要求每项机制绑定 observed failure、decision impact、acceptance 和 retirement。

## 综合设计

本项目采用最小、模型无关的控制面：

- Charter：北极星、现实成功、范围与未知；
- State Bundle：当前 exact reality、权限、下一步和恢复点；
- Living ExecPlan：当前里程碑与一步一验；
- Decision graph：选择、依据、反证、替代与回溯；
- Runbook / Tool contracts：执行、stall、权限、复杂度和恢复；
- Model adapter：接管测试，不让模型改标准；
- Eval：机械一致性 + 无聊天恢复盲测 + 领域反例 + 整体审查。

它先在当前 C8 这个真实低风险任务上运行。只有盲测或 C8/Shadow 暴露具体失败，才增加组件。

## 仍需现实验证

- 独立模型能否仅靠控制面无歧义接管；
- 回溯规则会不会过早放弃困难但正确的路线；
- Complexity Gate 能否实质减少治理自循环；
- C8 最小 Gate 是否足以运行有意义的 read-only Shadow；
- Shadow 的输出是否真正降低第一次现实需求实验的成本。

这些成为后续 Eval，而不是在研究文档里宣布答案。

