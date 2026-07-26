# 项目治理与产品现实独立挑战 R10｜2026-07-25

状态：`blocked-freeze`

裁决：**不得冻结设计，也不得把治理绿灯表述为产品完成。**

本轮是 Codex 平台可观察的多路径只读挑战。不同审查路径分别检查了项目状态新鲜度、AI 项目方法的自我验收风险和现有投研原型的产品现实。它们降低了单一路径漏检风险，但不构成密码学身份、组织独立性、安全隔离或模型分布独立性证明。

## 审查对象与候选绑定

- branch：`codex/investment-assurance-r7`
- candidate commit：`aa0a5966e114d6d7c87aa14fe2c27253f9f89f26`
- candidate tree：`36935032f40b3519960cf7e79ea611bc8f031bbf`
- candidate observation：审查启动时项目工作树 clean，branch 与远端同名分支对齐。

本报告只裁决上述候选。审查过程中产生的任何修复均属于后续候选，不能借用本报告获得通过；后续候选必须重新接受候选绑定审查。

## 可成立的有限结论

- 当前仓库存在一套会拒绝多类弱化、能运行大量反例的候选治理系统。
- 当前仓库仍主要是旧可运行原型与候选治理层，不是已交付的长期可用产品。
- 治理机制的存在与运行，不等于研究充分、设计冻结、产品完成或真实个人使用有效。
- 当前冻结必须保持阻断。

## 阻断发现

### `R10-CRIT-STATE-FRESHNESS`｜状态入口可陈旧而恢复检查仍通过

`STATUS.md`、`TASK_BOARD.md` 与 `LOOP_RUN_LOG.md` 仍描述较早轮次；现有 context recovery 只检查文件非空、固定标题、字节哈希和合成位置探针，没有从机器事实推导当前阶段、最新阻断审查与唯一下一步。长上下文遗忘风险因此被转移到一组可能陈旧的外部文件，而没有被关闭。

要求：

- 建立由验收状态、结构化审查记录和可路由工作包共同推导的 canonical state projection。
- 三个可见入口必须包含同源生成块，并由 CI 逐字节检查。
- 可见入口继续排除在 ground-truth 自引用哈希之外；推导规则、输入和校验器进入冻结边界。

### `R10-CRIT-CIRCULAR-COVERAGE`｜候选可用自己的覆盖标签升级机器结论

`run_project_method_acceptance.py` 在命令成功后仍读取候选可编辑的 failure registry：只有候选把状态写成 `covered`，机器才输出 `mechanism_verified`。这使语义覆盖结论同时成为输入和输出。实际远端运行中，所有声明命令均成功，但 16 个 failure 仅因 registry 为 `partially_covered` 或 `gap` 被标为 blocked；反向把标签改成 `covered` 又可升级结论，构成循环自证。

要求：

- 机器回执只能陈述声明命令是否执行成功，以及是否保留精确授权的外部条件。
- failure-registry 状态只能作为候选元数据，不能升级、降级或决定机器 outcome。
- “完整覆盖、方法充分、设计冻结或产品完成”必须由候选绑定只读语义审查或明确的人类残余风险决定，不能由该回执声明。

### `R10-CRIT-REGRESSION-BUDGET`｜完整回归尚无成功证据

候选前一轮完整回归在总预算耗尽时停止。它证明了进程组清理、输入指纹稳定和部分重型反例成功，但没有执行完完整测试宇宙。`aa0a596` 已扩大本地与远端预算，但审查时仍没有该候选的完整成功回执。

要求：

- 在稳定候选上执行完整发现集合，并证明 discovered、planned、loaded、started 与 successful selector multiset 精确一致。
- 任何超时、跳过、加载错误、失败、expected failure、unexpected success 或回执缺失均保持阻断。

### `R10-MAJOR-WORK-GRAPH`｜工作包有所有权规则，但没有可执行依赖图

现有工作包能检查写路径所有权和部分语义探针，却没有机器可验证的 `depends_on`、阻断传播、唯一 ready set 和 finding-to-action 路由。多个工作包同时存在时，系统不能从机器事实唯一推出下一步；`semantic_probe_count=0` 仍可通过。

要求：

- 把依赖边、finding 路由、阶段、稳定排序和 terminal-state 规则加入工作包合同。
- 拒绝未知依赖、自依赖、环、依赖未完成却 active、阻断未传播、重复 ready order 和开放 finding 无可路由 action。

### `R10-MAJOR-LOOP-FRESHNESS`｜执行循环台账未记录当前候选推进

执行台账只有一个较早 attempt，仍可长期保持 `active`。它没有证明最新治理修改已进入新的 attempt，也没有把最新观察绑定到当前受控工作范围。因此“有台账”不能证明循环记录仍对应当前工作。

要求：

- 最新 attempt 或独立的 current-state observation 必须绑定当前受控路径的确定性内容快照。
- 受控内容改变而未产生新记录时必须失败。
- 不把当前 HEAD 写回受版本控制文件，避免同提交自引用；运行时 HEAD/tree 只进入临时回执。

### `R10-MAJOR-RESEARCH-STATUS`｜回执有效与研究充分使用同一个通用绿灯词

`verify_research_sufficiency.py` 在 `derived_pre_review_eligible=false`、`derived_research_state=bounded_incomplete` 时仍输出通用 `status=pass`。其本意是“回执内部有效”，但 status-only 消费者可能把它误解为“研究已充分”。

要求：

- 分离 `verification_status` 与 `research_claim_status`。
- 不为仍然 bounded-incomplete 的研究输出可被通用消费者误读的 `status=pass`。

### `R10-MAJOR-LIVING-REVIEW`｜更新触发器仍是文本，不是运行机制

研究记录为五个主题写了 reopen triggers，但没有校准更新节奏、触发器观察、差异检索回执和旧结论失效传播。它表达了意图，尚不能保证长期保持最新。

要求：

- 为有时效性的来源和决策记录 `as_of`、复核窗口、事件触发器、上次检查、下次到期和差异结果。
- 到期或命中触发器必须使相关 claim 与下游决策进入 stale/reopened，而不是继续沿用旧绿灯。

### `R10-CRIT-PRODUCT-REALITY`｜当前仍没有可交付产品层

仓库没有正式的 `src/`、`tests/`、`acceptance/`、本地运行数据库、操作恢复层和非技术工作台。旧 `prototype/` 能演示部分纪律内核；候选治理能约束设计，但两者不能替代完整产品。

要求：

- 在设计冻结之后依次建立正式本地运行骨架、纪律内核、数据与研究交换、预注册评估、最小工作台、备份恢复与真实人工 onboarding。
- 产品完成必须由真实纸面运行、恢复演练、独立验收和用户使用证据证明，不能由治理回归代替。

## 当前修复不得声称的内容

- 修复一个 verifier 不等于关闭对应 failure class。
- 更新状态文档不等于状态新鲜；必须由机器事实派生并校验。
- 增加 `depends_on` 字段不等于有依赖图；必须执行拓扑与传播 oracle。
- 增加 living-review 文字不等于能长期更新；必须有到期与重开回执。
- 完整治理回归通过不等于投研产品完成。

## 重审前置

1. 关闭机器回执的循环覆盖主张。
2. 建立 canonical state projection 和 executable work graph。
3. 使执行循环台账对当前受控内容保持新鲜。
4. 分离研究回执有效性和研究充分性主张。
5. 把 living review 从文本触发器升级为可观察、可到期、可重开的机制。
6. 在稳定、干净候选上完成全量本地回归与远端机器回执。
7. 用新的精确 commit/tree 重新进行只读语义挑战。

在上述条件完成前，正确状态是：`design_freeze = blocked`，`product_complete = false`。
