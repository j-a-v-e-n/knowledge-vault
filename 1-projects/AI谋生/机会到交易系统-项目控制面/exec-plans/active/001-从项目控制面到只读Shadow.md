# ExecPlan 001：从项目控制面到最小只读 Shadow

本计划是 living document。执行期间持续更新 Progress、Surprises、Decision Log 和验证结果。

## Purpose

让一个没有旧聊天上下文、可更换的 AI 能准确恢复整个项目，并把 C8 从无限设计分支收缩成有限安全里程碑；通过 fresh review 后进入本地只读 Shadow，第一次用实际输入检验需求识别链。

用户可观察结果不是“多一套文档”，而是：

- 重启或换模型后不会丢失最终目标、权限、当前失败和下一步；
- 卡住时能沿决策链回到上游分叉，而不是无限重试；
- C8 只修阻断当前 Shadow 的真实问题；
- 设计阶段有明确出口，后续进展由 Shadow 结果而非治理文件计量。

## Scope

本计划包含：

- 项目级控制面的构建与恢复盲测；
- C8 attempt 1 findings 的风险分类、最小修复、回归和 fresh independent review；
- 通过后生成当前 Envelope 允许的最小本地 synthetic/read-only Shadow；
- Shadow 结果回写，并决定进入现实实验设计、简化或回溯。

本计划不包含真人联系、公开发布、部署、账号、支付、收款、合同、交付承诺或真实市场结论。

## Current facts

- 项目北极星记录于 PROJECT_CHARTER.md。
- 当前商业证据等级是 NO_REAL_OPPORTUNITY_VALIDATED。
- exact C8 candidate 位于 ../机会到交易系统-C8/机会到交易系统-总体设计候选。
- C8 review attempt 1 是 FAIL / NO-GO，报告记录 Critical 3、Major 3、Minor 0。
- 七个被审关键对象的 exact SHA-256 记录在 STATE.json，当前 bytes_in_remediation 为 false。
- C8 canonical JSON 仍标识 C7 历史对象，不是 living C8 状态。
- 当前没有 C8 post-closure roots。
- 当前禁止所有外部行动。

## Progress

- [x] 2026-07-28：完成官方工程资料、实证研究和反例调研。
- [x] 2026-07-28：完成现有战略根、C8 与旧 runtime 的只读项目 Harness gap audit。
- [x] 2026-07-28：确认 C8 修复在项目控制面验收前暂停，候选关键字节未改变。
- [x] 2026-07-28：控制面初版通过窄机械检查；上下文隔离恢复代理可读出目标与状态。
- [x] 2026-07-28：对抗审查判 NO-GO，复现 authority/gate 混淆、自由文本动作、缺失 Shadow 状态、candidate 空绑定、回溯图弱校验、gold 泄露与 bytecode 副作用。
- [ ] IN_PROGRESS：做一次有限修订；把授权与质量 Gate 分离，闭合结构化 action/state/backtrack/snapshot，并移除 gold。
- [ ] PENDING：在稳定 snapshot 上运行无 gold 恢复测试与 fresh 对抗审查。
- [ ] PENDING：通过后 STATE 切到 C8_MINIMUM_REMEDIATION；这只打开 workflow gate，不创造新 authority。
- [ ] PENDING：把 attempt 1 findings 分成当前必须修与明确 nonclaim；由 Complexity Gate 审查。
- [ ] PENDING：每次只修一个 failure class，立即运行相关攻击测试与完整回归并 checkpoint。
- [ ] PENDING：由未参与修改的 reviewer 对 exact successor bytes 做 fresh review。
- [ ] PENDING：只有 fresh review 和预声明测试均通过后，按现有 Envelope 进入最小本地只读 Shadow。
- [ ] PENDING：用 Shadow 的 false positive、false negative、拒绝原因和恢复结果决定下一分支。

## Surprises & Discoveries

- C8 内部已有未来 ProjectHarnessSpec，但那是为单个客户项目生成的交付 Harness，不是维持整个长期项目方向的项目执行 Harness。
- C8 README 与 review report 都说 blocked，但 canonical FINAL_CANDIDATE_MANIFEST.json 仍是 C7 frozen-pending 对象；immutable candidate 不能兼任 living state。
- 现有设计包含恢复、幂等与 Eval 概念，却没有当前可运行的 State Bundle、唯一 active step 或模型接管测试。
- C8 的领域反例确实降低“把网络表达误当需求”的风险；但 raw-byte、receipt 和 root closure 的继续扩张不自动降低商业未知。
- 用户提出迷宫回溯：同一路径卡住时，应回到最近决策分叉重验假设；这成为控制面的核心机制。
- 用户要求 Harness 固定、模型可替换；因此模型记忆不能承担项目状态。
- 首次盲测在读取期间遇到文件并发变化并正确拒绝旧结果；说明 snapshot 稳定性必须成为 verifier 输出。
- 对抗审查发现控制面把 adapter 资格、workflow gate 与真实 authority 混在一起；按第一性原理回退为“用户/runtime 授权，文件只记录，Gate 只排序”。
- 当前恢复 Eval 将 gold 放在同一可读文件，因此可读性 PASS 不能冒充无泄题接管证明。

## Decision Log

- D000：北极星是现实需求、交付、交易和学习，不是文档闭合。
- D010：第一性原理与现实观察先分 lane，再形成可证伪假设。
- D020：C8 Gate 缩到阻止已复现误判和越权的必要范围。
- D030：先建立模型可替换、可恢复、可回溯的项目控制面。当前 active。
- D040：控制面通过后，最小修 C8，fresh review 后立即进入 bounded Shadow。尚待激活。

决定的完整 basis、falsifiers 与回溯指针见 DECISIONS.jsonl。

## Milestone A：项目控制面可恢复

### Acceptance

- verify_control_plane.py 返回 valid，并验证 required files、STATE 引用、候选 exact hashes、review FAIL、历史 C7 manifest、权限和决策图。
- 一个未继承旧聊天的上下文隔离代理只得到不含 gold 的 task prompt 与控制面根路径，仍能从权威文件准确恢复：
  - 最终目标与当前商业证据等级；
  - 当前 candidate、attempt 1 状态和为何不能 freeze；
  - 唯一下一安全动作与禁止动作；
  - 当前 decision node、回溯点和 stall 触发；
  - 模型替换需要通过什么接管测试；
  - 为什么文件齐全不等于商业进展。
- 任何关键项错误、自授予权限或读取聊天依赖都判失败。

### State transition

通过后：

- lifecycle_state → C8_MINIMUM_REMEDIATION；
- current_decision_node → D040；
- workflow_gates.control_plane_accepted → true；
- workflow_gates.c8_candidate_edit_allowed_now → true；
- local authority 不变化；model portability 仍保持 cross-provider unverified；
- workflow_gates.local_shadow_allowed_now 仍保持 false，直到 C8 fresh review 通过。

## Milestone B：C8 最小必要修复

### Before editing

对 attempt 1 每个 finding 填写：

- 会改变哪个领域晋级、权限或当前 Shadow 可信度；
- 是否有可复现攻击；
- 最简单修复；
- 对应回归；
- 若暂不修，exact nonclaim 与为什么不阻断当前阶段。

### Execution order

优先修能造成 false accept、越权或 stale/exact-object 混淆的问题。完整性工作只有在能改变当前 Shadow 判定或 fresh review 阻断时进入。

每个 failure class：

1. 先保留最小失败复现。
2. 只修改该类必要代码和 fixture。
3. 运行定向测试。
4. 运行受影响的完整回归。
5. 更新 exact hashes 与 Progress。
6. 若相同 failure signature 重现且无新证据，触发 stall，不继续堆补丁。

### Acceptance

- 所有进入当前范围的 attempt 1 Critical/Major 有可复现攻击、修复和回归。
- 被延后的项目有明确 nonclaim，且 fresh reviewer 同意它不阻断本地只读 Shadow。
- 没有扩大外部权限、没有伪造 C8 manifest/freeze/root。
- fresh reviewer 未参与 bytes 编写，并对 exact bytes 给出当前阶段所需 verdict。

### Backtrack

若在计划预算内不能把 C8 缩成可审查的最小 Shadow Gate，回到 D020，比较“局部能力声明的更窄 baseline”与“继续完整候选闭合”，不得自动产生 C9。

## Milestone C：本地只读 Shadow

### Preconditions

- Milestone A 与 B 都通过；
- exact C8 前置 Gate 真实闭合；
- STATE 的 workflow_gates.local_shadow_allowed_now 明确打开；
- 真人联系、发布、部署、账号与资金权限仍为 false。

### Observable outcome

在预声明 fixture 上，系统能把 Observation、Interpretation、Opportunity Hypothesis 和 REJECT 分开；已知污染、rights、lane、lineage、stale 与 malformed 反例不被冒充为 Validated Need。

结果只能说明本地流程对这些 fixture 的行为，不能说明真实需求、购买意愿或盈利。

### Backtrack

- false accept 集中于领域语义：回到 D020 的 Gate 范围。
- 输入接口或工具导致丢证据：回到 Tool/Interface 层。
- 输出正确但无法影响下一现实实验：回到 Plan/Problem 层，简化 Harness。

## Concrete steps

当前工作目录：

    1-projects/AI谋生/机会到交易系统-项目控制面

控制面校验：

    python3 -B verify_control_plane.py
    python3 -B -m unittest -v test_verify_control_plane.py

C8 的具体命令在 Milestone A 通过且完成风险分类后再从 exact candidate 读取，不在本计划提前猜测或授权。

## Validation and nonclaims

机械检查证明引用和不变量一致；恢复盲测证明控制面在一次上下文重置中可被另一个代理理解；两者都不能证明真实市场需求。C8 tests 与 fresh review 也只覆盖声明的领域与完整性范围。商业晋级必须依靠未来现实证据。

## Idempotence and recovery

- 使用 python3 -B 时，控制面 verifier 与 unit tests 不写 bytecode，可安全重跑；发现 __pycache__ 或 pyc 即视为工具合同污染。
- 研究、FAIL 报告和 decision history 追加保留，不覆盖。
- C8 编辑前重新计算 STATE 中 exact hashes；不一致则 STALE_STATE。
- 中断后从 README → verifier → STATE → 本计划恢复。
- 不重复任何未来外部动作；当前这些动作全部禁止。

## Interfaces and ownership

- root agent：维护 Charter、State、active plan、最终集成与用户沟通。
- bounded subagents：只读研究、反证、恢复盲测和 fresh review；未授权时不写共享文件。
- candidate writer：Milestone A 之后才指定，独占所改 C8 文件。
- fresh reviewer：不参与相应 successor bytes 编写。
- 模型更换：遵守 MODEL_ADAPTER_CONTRACT.md，不改变验收与权限。

## Outcomes & Retrospective

尚未完成。Milestone A 通过后记录控制面是否真的让独立代理无歧义恢复、发现了哪些缺口、删掉或保留了哪些机制；Shadow 后记录它是否减少现实实验成本，而不是只记录测试数量。
