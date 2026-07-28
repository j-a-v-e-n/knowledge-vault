# 机会到交易系统：架构反证与修订记录

状态：`ARCHITECTURE-CHALLENGE-PASS / RESEARCH-CLOSURE-PENDING`

本记录只回答：内部架构挑战是否发现了承重缺口，以及这些缺口是否已经进入可执行的记录、状态、Gate 和测试语义。它不是最终研究闭合审查，不授权选择行业、联系客户、发布、承诺、报价、收付款或部署。

## 本轮绑定的候选

| 文件 | SHA-256 |
|---|---|
| `02-主张与证据地图.md` | `6e84f9660f79764a0274209a31609d5e10e2643acb86cd5fbd04f878b40ed0d6` |
| `03-机会到交易系统-总体设计.md` | `dc87fa0a2c9b82f11ba2ab3de2a6570c2aec15635f50900767ff53e38c9e9cc7` |
| `RESEARCH_PROTOCOL.md` | `7660e1fce039d16cf2ed49cd612237f5bd239cb1155eb6f219b1b7c5bda82957` |

任一绑定文件变化都会使本记录只成为历史审查证据；变化后的候选必须重新计算 hash，并在最终候选 manifest 下接受新一轮精确身份审查。

## 第一轮商业系统反证

| ID | 发现的承重缺口 | 为什么会使系统产生虚假结论 | 进入设计的修订 |
|---|---|---|---|
| `AR-01` | 第一性通道与现实通道虽然输出隔离，但两边可能共享由既有假设挑选的输入 | 输出不互看不能消除平台、关键词、时间窗和过滤过程已经造成的确认偏差 | `DD-21`；`ObservationSamplingPlan`、`AcquisitionRecord`、query/filter ancestry、负样本、无条件 discovery 与独立 confirmatory 分离 |
| `AR-02` | 付款、留存和收入可能在客户没有真正得到承诺价值时持续 | 自动续费、遗忘、锁定和取消摩擦会把价值未实现伪装成需求已解决 | `DD-22`；逐主体/订单 `CustomerValueRealizationRecord/State/Gate`，与 payment、retention、收入耐久分离 |
| `AR-03` | 正式承诺之前缺少 exact-offer 的可交付性门 | Demo 能运行不证明真实输入、权限、依赖、容量和验收条件下能够履约 | `DD-23`；承诺前 `DeliveryFeasibilityGate`，未知时只允许范围受限、风险披露且可退款的探索合同 |
| `AR-04` | 单个实验预注册不能控制批量尝试后只挑幸运赢家 | winner's curse 和选择性汇报会让偶然命中升级成“已验证机会” | `DD-24`；`ExperimentFamily/DiscoveryCohort`、完整 sibling 账本、累计探索预算、序贯/多重比较和独立确认 |
| `AR-05` | 系统可能从非随机触达结果中学习错误的因果规则 | 文案、价格、Harness 和对象由同一政策选择时，结果差异可能来自对象与渠道差异 | `DD-25`；`DecisionExposureRecord`、eligible action set、选择政策/概率、处理前条件；没有可信识别只生成相关性假设 |
| `AR-06` | 渠道与成交证据没有显式绑定卖方身份、关系和信任来源 | 熟人、学校、真人创始人或旧账号信誉下成立的结果不能自动迁移给新品牌或无人 Agent | `DD-26`；`SellerIdentityAndTrustContext`、关系/引荐依赖簇与 portability test |
| `AR-07` | 未成熟 cohort 可能提前支持退款、留存、支持负担和利润结论 | 右删失会在尾部事件发生前系统性高估结果 | `DD-27`；统一 `OutcomeMaturityState`、风险窗、保守界限、迟到事件重算和下游降级 |
| `AR-08` | 候选可以通过换解释、换版本或继续增加实验无限续命 | 不删除负面结果仍不能阻止组合持续消耗现金、人工和机会成本 | `DD-28`；`CandidateInvestmentPolicy/PortfolioStopPolicy`、跨版本累计投入、kill、no-progress expiry 与受控 re-entry |
| `AR-09` | “可持续的小额收入”可能被误写成用户的谋生目标已经完成 | 收入流耐久性与收入是否足以满足用户期限、现金、人工、资本和风险目标不是同一命题 | `DD-29`；`OwnerObjectiveSpec`、`IncomeSufficiencyState/Gate`，与 `SustainableIncomeState` 分离 |

## 第二轮结构一致性反证

第一轮修订之后，挑战者不再只检查概念是否出现，而是检查它们是否进入了可执行语义。发现并修订：

| ID | 结构缺口 | 修订结果 |
|---|---|---|
| `AR-10` | 交付可行性只有描述，没有唯一、可哈希、可失效的 Gate 输出 | 增加 `DeliveryFeasibilityDecision`，绑定 exact offer、原件集合、逐项谓词、制定者、独立批准、有效期与 assurance 闭包 |
| `AR-11` | `LearningProposal` 没有强制绑定当时的动作暴露与识别条件 | 增加 `DecisionExposureRecord` ID/hash、eligible actions、选择政策、causal estimand、识别方法与禁止因果升级规则 |
| `AR-12` | 结果成熟度在不同段落可能出现不一致枚举 | 统一为 `PENDING / MATURED / RIGHT_CENSORED / LOST`，并写入迟到事件重算和状态降级 |
| `AR-13` | 组合停止策略可能只停留在候选字段而非一等政策对象 | 把 `PortfolioStopPolicy` 建成有 scope、规范化版本/hash、累计量来源、批准、有效期和迁移规则的一等对象 |
| `AR-14` | 新增状态可能没有进入候选复合视图，形成“记录存在但结论不用”的死字段 | `CandidateCompositeView` 明确消费 sampling lineage、卖方身份/信任、交付可行性、价值实现、结果成熟度、组合停止、经济与收入充分性状态 |
| `AR-15` | 不同动作和商业结论所需 Gate 未形成明确映射 | 增加不可取消订金、正式承诺、交付 Harness、交易预测、扩张、需求已解决和最终收入目标各自的 Gate 组合；一个门通过不能抵消另一个未知或阻断 |

## 反证后的判断

在本记录绑定的候选上，`AR-01`—`AR-15` 已经不只是写成原则，而是进入了设计决策、记录对象、状态、Gate、失效传播或验收场景。内部架构挑战在这些检查项上没有留下新的未处理承重缺口。

这不等于总体设计已经闭合，原因是：

- 冻结检索协议的 S2 双方初始编码与第二次共同裁决尚未完成；
- 搜索裁决可能要求修改类别、证据边界或设计；
- 完整候选 manifest 尚未冻结；
- 最终独立复核尚未对搜索闭合产物和完整候选的精确 SHA-256 进行审查；
- 所有商业效果、项目化阈值和现实外部有效性仍然未知，必须在后续只读影子验证与经授权实验中产生。

因此当前研究状态继续保持 `BLOCKED`。本轮 `PASS` 只表示：已经提出的架构反例在这个精确候选中获得了结构化修订，没有把内部设计审查误写成现实有效性证明。
