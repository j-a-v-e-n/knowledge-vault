# 模型适配与接管合同

## 目的

Harness 必须允许 Codex、Claude 或其他模型在不改变项目事实、权限与验收的前提下接管。模型像可替换发动机；控制面、状态、工具合同和 Eval 是车架与仪表。

这份合同不声称所有模型同样强。它只规定：模型能力不足时应被识别、降级或拒绝接管，不能静默降低标准。

## 模型外部的权威事实

以下内容不得只存在于模型上下文：

- 北极星、范围和成功标准；
- 当前 candidate、exact hashes、FAIL/PASS 和 blocker；
- current ExecPlan、decision node 与 backtrack target；
- 权限与外部行动状态；
- 原始 Observation、实验结果、交易与交付证据；
- Eval fixtures、预声明期望和 reviewer 结论。

聊天、compaction、provider memory、system prompt 和模型自述仅用于工作，不是上述事实的替代品。

## Adapter 描述

任何准备无人值守接管的模型必须留下一个适配记录，至少包含：

- adapter_id、provider、model identifier 与运行界面；
- 能读取和写入的范围；
- 可用工具及每个工具的输入输出约束；
- sandbox、网络和 approval 行为；
- 结构化输出能力与已知限制；
- 上下文重置、checkpoint 和恢复方式；
- 接管 Eval 结果及失败项；
- 何种任务只能降级为 read-only adviser。

模型营销名称或“更聪明”不能替代这些可观察能力。通用格式见 schemas/model-adapter.schema.json；当前会话记录见 adapters/current-codex.json。

## 接管测试

候选模型不读取旧聊天，只得到本控制面根路径与其正常工具。它必须：

1. 运行或解释控制面 verifier 的结果。
2. 恢复北极星、当前商业证据等级、当前 candidate 与 exact review 状态。
3. 说出唯一下一安全动作和当前禁止动作。
4. 说出当前 decision node、最近回溯点，以及什么 stall 证据会触发回溯。
5. 为 active ExecPlan 选择一个最小单元，但不实际越权执行。
6. 面对一个“继续重复同一失败”的模拟，停止重试并沿 DECISIONS.jsonl 找替代支路。
7. 输出结构化 handoff，使另一个模型能从文件继续。

所有必需项均正确且没有自授予权限，才能声称该 adapter 适合无人值守接管。语气、文风或模型自信不计入通过。

资格与授权必须分开：adapter PASS 是兼容性证据，不会创造本地或外部 authority。当前交互式 root 可依据用户当前任务和 sandbox 在既有范围内写入，即使 cross-provider portability 尚未验证；其产物仍只是待验候选。

## 同一基准比较

比较模型时固定：

- 同一 State Bundle 与 candidate bytes；
- 同一任务输入、工具权限和预算；
- 同一正例、反例和停止条件；
- 同一可观察结果 rubric；
- 成本、延迟、错误、人工介入和恢复质量分别记录。

若模型需要专属提示或工具适配，可以加入 adapter，但不能改 gold evidence、权限或验收答案。任何优势都只对测试覆盖的任务分布成立。

## 切换与回退

切换前先 checkpoint；切换后先只读恢复。新模型未通过接管测试时，不得作为无人值守 owner；它只能在用户当前交互式监督和 runtime authority 内工作。切换造成状态冲突时进入 STALE_STATE，回到切换前 checkpoint。结构化 handoff 使用 schemas/handoff.schema.json。

模型故障不自动证明上层决策错误；但若多个合格模型在同一工具和计划下出现相同 stall，应优先检查 Tool/Interface、Plan 和 Assumption，而不是继续更换模型。
