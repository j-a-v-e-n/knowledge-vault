# SSP Run2：Claim-Evidence Crosswalk

- 状态：`COMPLETE-FOR-CANDIDATE / FINAL-RESEARCH-REVIEW-PENDING`
- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- S1 joint SHA-256：`c8fb7bef800bc0a23370629fa8dfd4e19c802dea65d303f3e67eff690d00880f`
- S2 joint 已独立接受 SHA-256：`c6b2f73f41f1669f1d4a096ebede551353f84024d6d281df091feab4a79907d3`

本文件只把冻结运行中最终可进入 claim-evidence 的结果桥接到现有 RQ、Claim、设计决策与残余未知。它不把类别饱和改写成来源内容正确，也不把 CE-IN 改写成具体商机、需求、价格、交付能力或盈利事实。

S1 joint 只裁决为普通 `INCLUDE`，没有权威子型，所以下表写作 `INCLUDE/UNSUBTYPED`。S2 的 canonical final proposition 是 S2 joint 第 3 节定义的逐字 `FinalClaimRecord`；下表的“显示摘要”只用于索引，不替代该 literal tuple，也不得扩大其 `MethodLimitRecord`。

## S1 最终 CE-IN

| Identity | 显示摘要 | 严格范围 / CE | Claim / RQ 关系 | DD | 残余未知 |
|---|---|---|---|---|---|
| `S1/K02/R03/turn148search2` | 多种需求研究方法并行时，新 insight 可能来自新方法或 triangulation | 单公司探索案例；不估计方法相对效果；`INCLUDE/UNSUBTYPED` | `RQ2,RQ4`；case mechanism 支持 `SS-02,SS-03`，限制“单一方法能读取隐性需求” | `DD-02,DD-03,DD-06,DD-21` | 方法优劣、外部效度与跨情境重复性未知 |
| `S1/K04/R11/turn150search10` | hypothetical bias 常被报告，但 criterion-validity 证据更 mixed，且 hypothetical/actual designs 不可直接比较 | 限于综述覆盖的 health/social valuation contexts；不得给商业产品通用校正量；`INCLUDE/UNSUBTYPED` | `RQ3`；支持 `EF-06`；反对通用信号排序或固定校准量 | `DD-03,DD-06` | 具体产品、渠道、信号的预测效度与校准未知 |
| `S1/K05/R03/turn151search2` | fee-price fit、order frequency、质量、cancellation-refund 等与 delivery-app churn 相关 | 特定调查的选择性自报样本；相关而非因果；`INCLUDE/UNSUBTYPED` | `RQ3,RQ5`；支持 `EF-07`；限制“付款或使用等于价值实现” | `DD-05,DD-22,DD-27` | 因果驱动、总体适用性与长期价值实现未知 |
| `S1/K06/R03/turn152search2` | R&D complementary assets 与 sales/commercialization capability 影响 value proposition、delivery/capture | system-dynamics simulation 加单一企业情境；不是普遍因果事实；`INCLUDE/UNSUBTYPED` | `RQ1`；模型范围内支持 `TF-01,SS-01` | `DD-05` | 参数有效性、跨企业因果与实际价值捕获未知 |
| `S1/K06/R05/turn152search4` | formal/informal protection 组合随 business-model type 而异 | comparative case study；只生成框架，不证明收益因果或最优组合；`INCLUDE/UNSUBTYPED` | `RQ1,RQ8`；支持 `SS-01`；限制通用保护策略 | `DD-04,DD-05` | 各司法辖区、资产、合同及保护组合效果未知 |
| `S1/K07/R01/turn153search0` | Lean Startup 被描述为假设驱动实验法，但其直接促进组织学习的证据有限 | 限于可见综述；采用实验法不等于需求、付款或盈利；`INCLUDE/UNSUBTYPED` | `RQ9`；限制 `EF-16,SS-11`；只支持有纪律的测试 | `DD-06,DD-10` | 各行业中的学习与业务结果效应未知 |
| `S1/K07/R03/turn153search2` | Lean Startup 的适用行业、组织适配与采用驱动呈现情境异质性 | 不证明普遍绩效；`INCLUDE/UNSUBTYPED` | `RQ9`；限制 `EF-16,SS-11` 的普遍化 | `DD-06,DD-24` | 适用场景、选择偏差与业务结果未知 |
| `S1/K07/R09/turn153search8` | Lean Startup 与学习循环存在直接和提示性联系，但不能把关联升级为因果 | 限于综述覆盖研究；`INCLUDE/UNSUBTYPED` | `RQ9`；限制 `EF-16`；反对因果学习过度主张 | `DD-06,DD-10` | 因果效应、机制与外部效度未知 |
| `S1/K07/R11/turn153search10` | 软件创业者可能把 MVP 理解为产品版本和客户价值，而不是假设检验与学习 | 定性调查；仅覆盖其软件创业样本；`INCLUDE/UNSUBTYPED` | `RQ9`；限制 `EF-16`；支持冻结实验语义 | `DD-06` | 漂移的普遍性、原因和结果影响未知 |
| `S1/K08/R20/turn154search19` | GitHub Copilot field experiment 使用自然工作环境，异质任务使标准化测量困难 | 只支持该实验环境与测量边界；不纳入未显示效果量或普遍生产率；`INCLUDE/UNSUBTYPED` | `RQ6`；支持并限制 `SS-07,H-AI-04` | `DD-08,DD-10,DD-13` | 本系统精确任务的质量、总工时、返工与成本未知 |
| `S1/K09/R08/turn155search3` | Odysseys 以真实浏览会话构造 live-Internet 长时程、多站点任务并评分过程进度 | 只证明该 benchmark 的任务与评分设计；动态网站会漂移；`INCLUDE/UNSUBTYPED` | `RQ6,RQ7`；支持 `EF-10,H-AI-06` 的评测机制，不证明可靠性 | `DD-08,DD-10,DD-13` | 模型表现、复现性与生产迁移未知 |
| `S1/K09/R16/turn155search11` | EdgeBench 项目页描述以真实科研数据和跨模块任务评测超长时程环境学习 | 只证明项目页所述 benchmark 工件；不证明一般 Agent 可靠；`INCLUDE/UNSUBTYPED` | `RQ6,RQ7`；支持 `EF-09,EF-10` 的评测机制并限制外推 | `DD-08,DD-10,DD-13` | benchmark validity、结果、oracle 与生产可靠性未知 |
| `S1/K10/R15/turn156search15` | NIST NCCoE concept paper 把 strong authentication、least privilege 与 action intent 列为待解决标准问题 | 概念文件和标准化方向；不是生效标准或效果验证；`INCLUDE/UNSUBTYPED` | `RQ8`；支持 `SS-09`；限制“身份/授权已解决” | `DD-09,DD-20` | 最终标准、互操作与控制效果未知 |
| `S1/K10/R18/turn156search17` | CSA 文档把 authentication、authorization、session management 与 credentials 治理列为独立控制面 | 只承载组织文档所述机制；不证明跨平台互操作或攻击免疫；`INCLUDE/UNSUBTYPED` | `RQ8`；作为控制 taxonomy 支持 `SS-09` | `DD-09,DD-20` | 实现正确性、有效性及具体合规适用未知 |
| `S1/K10/R22/turn156search21` | IMF note 讨论 Agent 发起购物和付款时的授权、身份与 account-holder/legal-agent boundary | 政策/经济讨论；不确认具体产品、司法辖区或法律代理关系；`INCLUDE/UNSUBTYPED` | `RQ8`；支持 `SS-09`；反对“能付款即有权付款” | `DD-09,DD-20` | 真实支付产品、合同授权与司法辖区结论未知 |
| `S1/K11/R03/turn158search2` | 美国版权局发布说明 GenAI 输出与人类作者决定的关系，并未建议给纯 AI 输出新增保护 | 只承载该官方发布的美国政策立场；不替代法院裁决；`INCLUDE/UNSUBTYPED` | `RQ8`；在所述司法辖区支持 `SS-10` | `DD-04,DD-09,DD-12` | 具体作品作者性、其他权利与司法辖区未知 |
| `S1/K11/R22/turn158search21` | 单一发行人 SEC filing 披露 AI 输出不可版权、第三方 IP、隐私、合同与监管风险 | 只证明该发行人的风险披露；不证明法律结论或发生率；`INCLUDE/UNSUBTYPED` | `RQ8`；限定支持 `SS-10` 的风险边界，不是法律证明 | `DD-04,DD-09,DD-12` | 风险是否发生、责任与适用法律未知 |
| `S1/K12/R19/turn159search18` | 大学/监管提交材料把 AI 驱动 dark patterns 与隐私、民主和经济伤害联系起来 | 支持风险论证与治理诉求；不是总体实证估计；`INCLUDE/UNSUBTYPED` | `RQ5`；支持 `SS-05,SS-06` 的机制边界，不支持发生率 | `DD-12` | 发生率、因果强度、受影响群体与缓解效果未知 |

## S2 条件式最终 CE-IN

以下结果来自 independent 已接受的 S2 joint exact hash；它们仍只在各自行范围内进入研究候选，不能越过最终 manifest-bound research review。

| Identity | 显示摘要 | 严格范围 / CE | Claim / RQ 关系 | DD | 残余未知 |
|---|---|---|---|---|---|
| `S2/K03/R10/turn163search8` | Nicira 回顾中，客户兴趣没有自动转化为预算和组织采购能力 | 单一创业团队回顾、无对照；不估计普遍频率；`CE-IN/CASE-MECHANISM` | `RQ1`；案例范围内支持 `EF-01`；反对“兴趣等于采购就绪” | `DD-01,DD-16,DD-19` | 频率、因果与跨组织适用性未知 |
| `S2/K03/R16/turn163academia15` | 模型中 rival firms 可收购并整合 orthogonal-market startup | 只承载 rival firms、acquihire 与 talent allocation 的形式模型；不是客户获取或市场需求经验效应；`CE-IN/PRIMARY-METHOD` | `RQ1`；形式机制范围内支持 `SS-01`；不支持 buyer-reach effectiveness | `DD-05` | 模型条件的现实满足、方向与市场效应未知 |
| `S2/K05/R07/turn165search6` | IBM 文档称 Abandoned Products report 可用于发起 abandonment recovery campaigns | 只承载 IBM 文档内容与发布者自述；不证明 recovery 导致购买；`CE-IN/DOCUMENTATION` | `RQ3`；只限制 `EF-06`，不支持结果主张 | `DD-03,DD-06` | abandonment 原因、恢复因果效果与购买率未知 |
| `S2/K06/R05/turn166search3` | 可见模型以 quality-WTP 分布和简单购买规则研究 customer surplus/profit | 只承载模型、假设与条件；需全文核验；不作经验 WTP 或效果量外推；`CE-IN/PRIMARY-METHOD` | `RQ1,RQ5`；只在模型内支持 `TF-04,SS-01` | `DD-05` | 分布假设、经验 WTP、竞争反应与效果量未知 |
| `S2/K06/R06/turn166search4` | compositional-choice 理论说明相似价格、质量或功能不必然意味着实际 substitutes | 只承载形式理论及成立条件；不作普遍经验替代效应；`CE-IN/PRIMARY-METHOD` | `RQ1,RQ5`；条件性支持 `TF-04,SS-01` | `DD-05` | 承重价值成分、实际替代弹性与成立条件未知 |
| `S2/K07/R17/turn167academia16` | Bayesian truth-discovery 方法分别建模 source false-positive/false-negative quality | 只承载算法及所述 data-integration 数据集；不作开放世界需求发现准确率；`CE-IN/PRIMARY-METHOD` | `RQ3,RQ4`；支持 `SS-04` 下的候选来源质量机制，限制自动 truth inference | `DD-04,DD-10` | 敌对网页、商业需求与分布漂移上的准确率未知 |
| `S2/K09/R26/turn169search25` | 原论文提供 multi-agent failure benchmark/taxonomy，并讨论 verification、communication、uncertainty 与 memory/state | 只限论文 benchmark/taxonomy；不作开放世界生产可靠性、恢复或安全保证；普通 `INCLUDE`；`S2-K09/R03` 为 duplicate | `RQ6,RQ7`；支持 `EF-09,SS-08`；反对“多 Agent 必然更强” | `DD-08,DD-10,DD-13` | benchmark 迁移、生产失败率与控制净效果未知 |
| `S2/K10/R22/turn170search21` | Microsoft 文档描述 access control、data protection、auditability、admin consent、managed identity 与 least privilege | 只承载产品文档所述 controls/configuration；不证明实现正确或安全有效；`CE-IN/DOCUMENTATION` | `RQ8`；作为 documented mechanism 支持 `SS-09`，不支持 effectiveness | `DD-09,DD-20` | 配置执行、攻击抵抗、其他平台与法律适用未知 |

## S2 K04 强制 non-claim

| Query | 最终 CE | 可保留内容 | Claim / DD bridge | 禁止结论 | 残余未知 |
|---|---|---|---|---|---|
| `S2-K04` | 无 CE-IN；全部为 CE-OUT | interview、waitlist、LOI、deposit、paid pilot、pre-contract documentation/payment-readiness 仅作 discovery mechanism | 不支持新增 Claim；既有 `RQ3/EF-06` 与 `DD-03,DD-06` 的设计机制仍待验证 | 不得声称任一信号能预测真实购买/支付，也不得声称普遍排序、校准量、阈值、因果效应或跨市场有效性 | 每种信号在精确市场、样本、offer 与时间窗中的预测效度未知 |

## S1 oversight provisional：只桥接类别与设计

| Identity | 机制 | Joint disposition | 现有桥 | 证据权限 |
|---|---|---|---|---|
| `S1/K13/R24/turn160reddit23` | 无具体 action scope 的 approval 可能退化为 rubber stamp | `EXISTING-K13 / EXCLUDE:NO-METHOD` | `RQ8 / SS-09,SS-12 / H-OVERSIGHT-01 → DD-09,DD-14` | category-only；不支持发生率、因果或监督普遍失效 |
| `S1/K13/R27/turn160reddit26` | 监督者可能没有能力实际评估输出 | `EXISTING-K13 / EXCLUDE:NO-METHOD` | `RQ8 / SS-12 / H-OVERSIGHT-01 → DD-10,DD-14` | category-only；不补强承重经验主张 |
| `S1/K13/R34/turn160news37` | time pressure、approval fatigue 与 automation bias 可能削弱人审 | `EXISTING-K13`，harm cross-map `K12`；`EXCLUDE:SECONDARY-WHEN-PRIMARY-AVAILABLE` | `RQ8 / SS-12 / H-OVERSIGHT-01 → DD-14` | category-only；承重证据仍来自既有 primary/official sources |

## CE-OUT 处理规则

| 最终 CE class | Crosswalk 处理 |
|---|---|
| `OUT-OF-SCOPE` | 只保留 provenance；Claim、relation 与 DD support 均为 `NONE` |
| `NO-METHOD` | 可保留 K/category discovery；不得成为事实证据 |
| `SECONDARY-WHEN-PRIMARY-AVAILABLE` | 指向 canonical primary；自身 evidence count 为零 |
| `PROMOTIONAL-ONLY` | 只记录发布者自述线索；不得承担效果、成熟度或采用主张 |
| `DUPLICATE` | 必须填写 `canonical_ref`；不得重复计数或制造独立 corroboration |
| `INACCESSIBLE-FOR-VERIFICATION` | 不得承载 factual proposition；只保留检索轨迹 |
| `STALE-CURRENT-CLAIM` | 不得支持当前状态；若保留只能作为明确日期限定的历史材料 |
| `FABRICATED-OR-UNVERIFIABLE` | 隔离并禁止进入 Claim/DD support graph |

## 机械不变量

- S1 的全部最终 CE-IN identity 必须各出现一次；S2 的全部条件式最终 CE-IN identity 也必须各出现一次。
- 每个 duplicate 必须指向唯一 canonical result；不能形成 duplicate chain 或把 duplicate 当独立 corroboration。
- 任一 CE-OUT 若被标为 `relation=supports`，验证必须 fail closed。
- 本 crosswalk 与任一 joint、ledger 或 raw manifest 不一致时，以绑定的 sealed 原件为准，并使本文件进入 `INVALID`；不得静默修订原件。
