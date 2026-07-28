# 旧 CLI 与餐馆 Pilot：新设计差距审计

状态：`GAP-AUDIT-COMPLETE / LEGACY-REUSE-NOT-AUTHORIZED`

本审计只判断旧 `schema 0.1` 是否可以作为当前总体设计的实现起点。结论是：旧 runtime、测试与 Pilot 只能作为历史反例和迁移 fixture，不能作为新设计实现或验收证据。当前代码没有发送、发布、部署或收付款执行器；主要风险是它会生成可能被下游误读为“已验证、已授权或可交付”的状态与 Harness 工件。

## Critical

### `LG-01` 候选级 commitment 会过早解锁 delivery Harness

- 事件只绑定 `opportunity_ref`，没有绑定 counterparty、offer version、协议、订单或 probe：`src/opportunity_os.py:440`。
- `required_input_shared`、`agreement_signed` 和 `deposit_received` 被压成候选级 `commitment`：`src/opportunity_os.py:90`。
- `make_harness()` 只检查候选级市场阶段，不检查同一 exact offer 的 `DeliveryFeasibilityDecision`：`src/opportunity_os.py:723`。
- 旧测试明确把 deposit 当成生成 delivery Harness 的充分条件：`tests/test_opportunity_os.py:180`。

这允许 offer A/客户 A 的事件解锁同一候选下 offer B/probe B 的交付工件；退款、争议或报价变化也不会自动撤销历史最高阶段。新设计要求正式承诺与生产 Harness 前先通过 exact-offer `DeliveryFeasibilityGate`。

### `LG-02` “外部证据”只是调用者自填标签

- validator 只检查 `evidence_origin` 字符串；`evidence_locator` 只需非空，没有原件 hash、外部对象 ID、主体身份或回执验证：`src/opportunity_os.py:440`。
- “不能自证”的旧测试只证明 `system_log` 标签会被拒绝；同一 JSON 改标 `external_party` 即可通过：`tests/test_opportunity_os.py:165`。
- `offer_presented` 可由 `system_log` 推进为 `exposed`，也可被设为 probe 的成功事件：`src/opportunity_os.py:90`、`src/opportunity_os.py:413`。

因此旧系统能把自己记录的发送动作误写成实验成功，不能满足原始回执、环境终态、身份绑定与独立验收要求。

### `LG-03` 旧授权字段能够制造伪授权工件

- `scoped_authorization` 只要求任意非空 `authorization_ref`：`src/opportunity_os.py:422`。
- `human_approval_each` 与 `scoped_authorization` 被直接映射成 Harness permission 字符串：`src/opportunity_os.py:694`、`src/opportunity_os.py:796`。

旧系统没有 canonical `ActionEnvelope`、确定性 `PolicyDecision`、资源原子占用、readiness/Grant、exact-hash token、提交时重验或 `ExecutionReceipt`。这些字符串不得迁移成当前权限。

### `LG-04` 证据可原地修改，旧 Harness 不失效

- 旧测试直接修改既有 observation，并把旧、新 Harness 同时继续存在当作通过：`tests/test_opportunity_os.py:207`。
- Harness digest 只含 opportunity、probe 及其直接 principle/observation refs，不含事件、状态版本、政策、权利、Gate、批准或 assurance 闭包：`src/opportunity_os.py:762`。
- 同名 manifest/task contract 存在时直接返回，不重算和验证当前文件：`src/opportunity_os.py:815`。

这与来源、污染、oracle、权利或闭包变化必须让下游 `STALE/INVALID` 的新设计冲突。

### `LG-05` 没有机器级 legacy/BLOCKED 启动门

- CLI 仍可打印无范围的 `VALID` 或生成 Harness：`src/opportunity_os.py:899`。
- 旧 README 仍保留可复制的 `make-harness` 命令：`README.md:34`。

文首历史警告能降低人工误读，但不是 fail-closed control。研究状态未闭合时，旧 runtime 不得成为当前入口。

## Major

| ID | 缺口 | 旧实现 | 新设计要求 |
|---|---|---|---|
| `LG-06` | 双通道只验证有两个引用 | `src/opportunity_os.py:349`、`:574` | SamplingPlan/Acquisition lineage、隔离 workspace、sealed outputs、canary 与 contamination propagation |
| `LG-07` | 候选级单向阶段覆盖并存真相且不降级 | `src/opportunity_os.py:600` | 按 counterparty/offer/order/window 的正交状态、Blocker、staleness 与只读复合视图 |
| `LG-08` | `VALID` 语义过宽 | 空 workspace 可 valid；Pilot Run Log 写 `Workspace validation: VALID` | 只能声明精确 schema/范围的验证结果，不能暗示需求、权利、Gate 或研究闭合 |
| `LG-09` | Pilot 的 exact-input 声明缺反证依赖 | `RUN_LOG.md:5`、manifest `:5` | 完整输入闭包、负证据、原件 hash 与失效传播 |
| `LG-10` | Pilot 来源与预览没有可迁移权利链 | observation 只有漂移 URL；preview 使用品牌和公开网页素材 | SamplingPlan、原始快照、RightsRecord、AssetBOM 与 right-to-sell Gate |
| `LG-11` | 历史正文仍含已废弃路径 | `DESIGN.md:120`、`STATE.md:29` | 只把它们作为明确 legacy 输入，不允许 current runtime/search 读取为当前状态 |

## 只能在重验证后复用的部分

- 记录不得自写 `validated/status/score` 的不变量；
- Observation 与 interpretation 分离、principle 不反向引用市场结论的意图；
- typed reference 与重复 ID 的低层检查思路；
- 原子临时文件替换和 content digest 的思路，但实现必须升级为规范化完整闭包、append-only、恢复与失效传播；
- Pilot 中的 `Unknown`、`does not establish`、真实性警告和反证，可作 adversarial fixture，不可作需求事实；
- 市场证据与生产状态分开的意图，但不能保留旧 candidate-wide monotonic enums。

## 旧测试当前基线及其正确解释

在当前工作区执行：

```bash
python3 -m unittest discover -s '1-projects/AI谋生/机会到交易系统/tests' -v
```

输出为 `Ran 9 tests` 与 `OK`。这只证明旧实现仍符合它自己的 `schema 0.1` 断言；其中通过的 `test_delivery_harness_is_blocked_without_commitment` 正是把 deposit 当作 delivery Harness 解锁条件的旧规则。因此旧测试全绿是迁移基线，不是新设计正确、研究闭合或可以继续 Pilot 的证据。

## 最小只读 shadow MVP 迁移边界

### 先切断旧授权面

- `schema 0.1` 只允许显式 legacy import/quarantine；
- 停用 `make-harness`、`external_action_policy` 和 `derive_opportunity_status` 作为当前接口；
- 新 CLI 不输出无范围的 `VALID`、`commitment`、`paid` 或可执行 permission；
- shadow runtime 根本不加载外联、发布、部署、支付、账户或客户写入工具。

### 首批重写对象

| 旧对象 | shadow MVP 替代 |
|---|---|
| `observation` | `ObservationSamplingPlan + AcquisitionRecord + EvidenceNode + ObservationRecord + RightsRecord` |
| `principle` | `FirstPrinciplesMemo + SealedLaneOutput` |
| 两个 refs | 独立 lane workspace/manifest、canary、发布回执与 `ContaminationEvent` |
| `opportunity` | 含竞争解释、双向证据、scope 和最脆弱假设的 `NeedHypothesis` |
| `probe` | 只生成未执行的 `ExperimentSpec` 草案，绑定 family/cohort、判据与停止条件 |
| `event/status` | shadow 阶段不生成商业状态；用 exact-hash `EvalSpec/EvalRun` 记录模型、人工基线、oracle 与成本 |
| `make_harness` | 明确 deferred；外部验证与 exact-offer gates 通过前不存在生产 Harness 路径 |

### 最小验收终态

一次 shadow run 最多产出：可追溯 observations、两条 sealed lane outputs、带竞争解释的 `NeedHypothesis`、未执行的下一实验草案和绑定原件的 `EvalRun`。任一承重输入变化必须使派生物失效；旧 Pilot 或任何评测结果都不存在通往 Harness 或外部动作的代码路径。

只有在研究闭合与 exact-hash 最终审查通过、并且 sibling governance root 的 post-closure manifest 机械闭合后，才可在预声明且与旧项目不重叠的 `机会到交易系统-shadow-mvp/` sibling root 按 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 开始首版实现。本审计不授权复用旧 runtime；旧对象只能作为显式 `LEGACY_UNQUALIFIED` fixture 被新 validator 拒绝或隔离。
