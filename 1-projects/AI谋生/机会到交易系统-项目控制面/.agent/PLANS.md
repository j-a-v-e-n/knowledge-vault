# ExecPlan 标准

长期或跨会话工作必须使用一个自包含的 living ExecPlan。新模型应能只靠控制面和该计划继续，不依赖旧聊天。

## 必需内容

每份 active ExecPlan 都必须包含：

- Purpose：这段工作会产生什么用户可观察结果，为什么服务北极星。
- Scope / Non-scope：这次做什么、不做什么。
- Current facts：exact candidate、状态、关键证据和权限。
- Progress：带日期的完成、进行中和待办；每个停止点更新。
- Surprises & Discoveries：计划外事实、反例、工具限制及其证据。
- Decision Log：引用 DECISIONS.jsonl；记录新决定与原因。
- Milestones：每个里程碑应独立可验证，并说明完成后 STATE 如何变化。
- Concrete steps：cwd、命令或文件、预期输出与写入所有者。
- Validation：行为结果、正反例、独立审查和不代表什么。
- Stall / Backtrack：预算、无进展判据、最近可回溯分叉和替代路线。
- Idempotence / Recovery：中断后读取什么、什么可以安全重跑、什么不可重复。
- Interfaces：输入输出、工具合同、模型 adapter 与权限。
- Outcomes & Retrospective：完成时写实际结果、剩余未知与下一现实步骤。

## 写法规则

- 计划描述行为，不只描述要改哪些文件。
- 一个时刻只有一个最小工作单元标为 IN_PROGRESS。
- 每个里程碑先给验收，再执行。
- 计划可以随新证据修订，但必须保留为什么修订。
- 计划不自授予权限，不自签发候选 PASS，不覆盖失败历史。
- 任何新增复杂度必须通过 RUNBOOK.md 的 Complexity Gate。
- 到达 stall 条件必须回到 DECISIONS.jsonl，不能把计划延长当成进展。

## 计划生命周期

- active：唯一当前计划；STATE.json 精确引用。
- completed：行为验收完成并写 Outcomes 后移动。
- abandoned：因证据回溯而停止；保留失败原因和替代计划引用。

移动计划是状态变化，必须同步更新 STATE.json 并重新运行 verifier。

