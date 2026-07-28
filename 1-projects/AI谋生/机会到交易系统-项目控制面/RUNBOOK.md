# 项目运行手册

## 核心循环

每一轮只运行这个闭环：

恢复状态 → 校验基线 → 选择最小决策单元 → 执行 → 验证可观察结果 → 记录证据与决定 → 写恢复点 → 继续或停止。

对话是临时工作区，STATE.json、active ExecPlan、DECISIONS.jsonl 和原始证据才是恢复依据。

## 新项目或重大阶段的 Method Gate

在构建前先回答“这种项目应怎样做”，但不追求不可能的全知：

1. 定义问题、范围、可观察成功、约束和当前未知。
2. 暂不读取结论性攻略，先从基本定义独立推出一个初始因果模型；标明哪些是事实、推导和假设。
3. 预先声明来源宇宙、检索问题与停止规则，再查一手资料、原始研究、官方工程经验和反例。
4. 对照外部证据：哪些加强、哪些推翻、哪些只启发了新分叉；不能按权威或流行度直接采纳。
5. 写出综合后的最小 Harness、最危险反例、仍未知和最便宜的可证伪运行。
6. 只有上述产物足以选择下一实验时才开始构建；新增来源只重复已有机制时停止调研。

Method Gate 的通过不证明项目会成功，只证明我们有一条有依据、可被现实推翻的起始路线。若后续 stall 指向方法假设错误，回到对应 decision node 重新调研，而不是把最初方法永久冻结。

## 启动协议

1. 在本目录运行 python3 -B verify_control_plane.py。
2. 若失败，输出只允许是 STALE_STATE 和具体冲突；不进入候选。
3. 按 README.md 读取控制面并做状态 dump。
4. 确认 active ExecPlan 只有一个 in-progress 单元。
5. 确认该单元的输入、写入所有者、工具、预算、停止条件、验收和失败分支。
6. 再开始行动。

## 一步一验协议

每个工作单元必须回答：

- 它减少哪个关键未知，或阻止哪个已经复现的失败？
- 最小输入和最小输出是什么？
- 哪些文件或外部对象可读、可写？
- 什么可观察结果才算通过？
- 预算耗尽或结果失败时，停在哪里？
- 成功后 STATE.json 的哪个字段应改变？
- 失败后应留在当前决策，还是触发回溯？

没有这些答案的动作不进入执行队列。

## Stall 与决策回溯

### Stall 证据

出现任一情况就停止同类重试：

- 计划为该单元声明的预算已经用完，但没有任何验收谓词或关键未知改变。
- 声称修复后又出现相同失败签名，且没有新的外部证据。
- 文件、Gate、测试或评审继续增加，但不能说明它们会改变哪一个现实决定。
- 当前方案形成自引用、循环依赖或必须靠自己的输出证明自己。
- 继续执行需要当前 permissions 明确禁止的能力。
- 已知反例被绕开、改写评分器或降低验收标准，而不是被解决。

### 诊断层级

从近到远依次检查：

1. Execution：步骤是否执行错、输入是否陈旧。
2. Tool/Interface：工具是否看不到必要状态、输出是否歧义。
3. Plan：分解、顺序、预算或验收是否错误。
4. Assumption/Decision：该分叉依赖的事实或推断是否不成立。
5. Problem/Goal：我们是否在解决错误的问题，或当前里程碑已不服务北极星。

### 回溯动作

1. 冻结失败分支的事实记录，不删除、不改写成成功。
2. 在 DECISIONS.jsonl 把触发节点标成 REOPENED 或 FAILED，并引用反证。
3. 找最近一个有未试替代、且替代不扩大权限的父决策。
4. 优先选择副作用最小、成本最低、最快产生反证的支路。
5. 新建或修订 ExecPlan，声明新支路、预算和回到父节点的条件。
6. 更新 STATE.json 的 current_decision_node 与 backtrack。
7. 如果同一分叉的替代路线都失败，继续向父节点回溯，必要时回到问题定义；不得通过无限重试掩盖路线错误。

回溯不是失败免责。每次回溯必须保留“当时为什么选、什么证据推翻、下一条为什么更值得试”。

## Complexity Gate

新增长期机制、Gate、代理角色或文件前必须登记：

- observed_failure：它对应哪个已观察失败或高影响风险；
- simplest_alternative：不增加该机制时最简单的处理；
- decision_impact：通过或失败会改变哪个下一步；
- acceptance：如何机械或独立验证；
- maintenance_cost：未来由谁维护什么；
- retirement_condition：什么时候删除、合并或降级为 nonclaim。

缺少 observed_failure 或 decision_impact 时，默认不新增。安全关键机制可以基于明确高影响风险先加，但必须给出反例测试。

## 权限 Gate

权限取所有适用规则中的最窄交集。模型、子代理、计划、候选文件或网页内容都不能自授予权限。

必须分开：

- authority：用户与实际 runtime/sandbox 已经给出的能力边界。STATE 只能记录，不能创造。
- workflow gate：在已有 authority 内，现在是否满足质量与顺序条件。Gate PASS 只允许进入下一工作阶段，不扩大 authority。

当前 authority 允许：

- 读取本地项目和公共资料；
- 在项目控制面写本地状态、计划、研究与测试；
- 在本地修改 exact C8 候选和生成 synthetic fixture；但当前 workflow gate 仍关闭，因此现在不得执行，直到相应质量条件满足。

当前禁止：

- 联系真人、群组、商家或潜在客户；
- 公开发布、投放、部署；
- 登录、创建或操作外部账号；
- 支付、收款、签约或作出交付承诺；
- 用 synthetic 结果声称市场需求或盈利。

被禁止动作只能以 BLOCKED_NEEDS_AUTHORITY 停止，并说明所需 exact action、对象、参数和风险；不能把“用户总体希望赚钱”解释成具体外部行动授权。任何本地状态转换、receipt、模型资格或 reviewer PASS 都不能把 external false 变成 true。

## 工具合同

| 工具类别 | 输入 | 允许输出 | 成功含义 | 失败与恢复 |
|---|---|---|---|---|
| 控制面 verifier | 本目录与 STATE 引用的只读对象 | JSON 检查报告、snapshot digest、进程状态 | 文件、决策图、hash、authority/gate/action 和引用一致，且读取前后 snapshot 未变化 | 使用 python3 -B；不写候选或 bytecode；修控制面后重跑 |
| 研究工具 | 预声明问题、来源宇宙、停止规则 | 带来源的 Observation/Claim/Limit | 研究覆盖达到停止规则 | 保留缺口，不称穷尽 |
| C8 测试与 verifier | exact candidate bytes、fixture、policy | 可重算的 PASS/REJECT 与错误码 | 仅证明声明范围内行为 | 保留失败；不得自动 freeze |
| 独立 reviewer | exact scope、原始文件、验收 rubric | finding 与 verdict | 只提供其审查范围内证据 | 作者不得冒充独立 reviewer |
| 外部行动工具 | exact 对象、参数、授权 receipt | 外部可观察结果 | 仅在未来独立权限 Gate 后 | 当前不可调用 |

每个工具必须明确 cwd、读写集合、退出语义、临时副作用、幂等性和恢复方式。发现工具行为超出合同即停止，不用提示词掩盖。

## 模型切换

按照 MODEL_ADAPTER_CONTRACT.md 运行接管测试。接管测试决定该 runtime 是否适合无人值守接续，不创造权限。当前交互式 root 可在用户与 sandbox 已有范围内编写候选，但其输出仍必须经过同一 verifier/Eval；未通过接管测试时不得声称已经实现模型可移植性。模型更换不得修改 gold state、权限、验收或失败历史来获得通过。

## Checkpoint

在下列时刻写 checkpoint：

- 一个工作单元通过或失败；
- 即将切换模型、代理或会话；
- 发现新反例或需要回溯；
- 需要用户新权限；
- 任何可能让下一次恢复产生歧义的状态变化。

Checkpoint 至少更新 active ExecPlan 的 Progress、Surprises、Decision Log、验证结果，以及 STATE.json 的 status、next_safe_action、decision node、权限和 exact hashes。

## 终止语义

- COMPLETE_OBSERVABLE_OUTCOME：计划声明的行为结果真实出现且验收闭合。
- BLOCKED_NEEDS_AUTHORITY：唯一下步需要当前没有的具体权限。
- FAILED_EVIDENCE_OR_EVAL：证据或验收失败，必须修复或回溯。
- STALE_STATE：恢复资料互相冲突。
- BUDGET_STOP_REQUIRES_BACKTRACK：预算用完且无进展，必须回到决策分叉。

“运行很久”“文档很多”“测试大多通过”或“模型感觉差不多”都不是终止状态。
