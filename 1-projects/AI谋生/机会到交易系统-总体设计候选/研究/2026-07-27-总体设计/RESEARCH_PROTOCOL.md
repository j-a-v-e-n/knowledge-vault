# 机会到交易系统：研究协议

状态：`CANDIDATE-C4-PREFREEZE / RUN2-EXACT-ACCEPTED / BLOCKED`。C1 因 candidate inventory 与未来 shadow 目录相互失效而得到 `FAIL / MAJOR`，C2 因 candidate node-type、shadow 状态闭集和测试 bytecode 副作用得到 `FAIL / WITHDRAWN`，C3 因 Run2 crosswalk 漏项、final-status independent acceptance 缺失及可变旧根污染得到 `FAIL / MAJOR`；记录保存在 [`FINAL_REVIEW_HISTORY.md`](./FINAL_REVIEW_HISTORY.md)。C4 已完成完整 CE-IN crosswalk及同一 exact Run2 final-status 的明确独立接受；只有 successor manifest review、外部 closure decision 与 sibling governance root 继续全部闭合后，才可能改变总体 `BLOCKED`。

## 决策问题

在公开或获授权信息范围内，能否设计一套由 AI 主导、以真实外部行为为学习信号的通用系统，使它能够：

1. 发现他人的明示需求与隐性价值缺口；
2. 形成多个可证伪的商业机会假设；
3. 用最低必要成本获得比讨论热度更强的需求证据；
4. 为通过验证的机会设计专属 Harness 并完成数字化生产与交付；
5. 在明确权限内推进销售和交易；
6. 从拒绝、使用、付款、退款、复购和留存结果中改进。

## 当前不作为事实的核心假设

- AI 在某些具体环节可能提高最终质量或降低完整成本，从而可能扩大个人可盈利解决的问题范围。该假设必须按模块与纯人工/人机基线比较，不得从模型能力推出净利润。
- 网络碎片能帮助发现真实需求，包括未被直接表达的需求。
- 大部分在线环节最终可以由 AI 承担。
- 一套跨行业的通用工作流可以比临时人工判断更稳定地找到机会并完成交易。

这些都要接受支持检索、对抗检索和外部有效性检查。

## 研究问题

- `RQ1`：商业机会、价值、需求、有效需求和交易最小分别意味着什么？如何区分价值创造与竞争后的价值捕获？
- `RQ2`：明示需求、行为暴露的需求、隐性需求和方案唤醒的偏好如何区分？
- `RQ3`：投诉、搜索、评论、工作绕行、现有支出、回复、承诺、使用、付款和留存各能证明什么？
- `RQ4`：怎样发现在线信息中没有直接写出的价值缺口，同时避免投射与确认偏误？
- `RQ5`：哪些购买、信任、采用、满意和复购机制应进入系统，哪些理论不具备跨场景通用性？
- `RQ6`：当前 AI 在研究、分析、原型、生产、销售、交付和学习各环节的可靠能力边界是什么？
- `RQ7`：确定性流水线、单 Agent、专用 Agent 路由和多 Agent 系统的成本、可靠性与适用条件有何不同？
- `RQ8`：哪些动作可以默认自主，哪些必须由身份、授权、权利/IP、法律责任、伦理伤害或不可逆性触发人的批准？
- `RQ9`：怎样用有容量约束的实验组合验证总体系统，并最终连接完整成本后的可持续收入，而不先假定某个行业就是正确方向？

## 范围

### 优先覆盖

- 可通过互联网观察、触达或验证的需求；
- 可数字交付，或主要由数字工作完成的产品与服务；
- 消费者、小企业和知识工作场景的通用机制；
- 英文与中文可访问材料；
- 基础理论不设年代下限，当前 AI 能力优先使用最新官方与独立资料；
- 法律与监管仅用于总体架构风险，重点覆盖美国与欧盟公开资料。
- 权利研究只覆盖版权、开放许可、平台/模型条款、客户资产授权和 right-to-sell 的系统级门；不构成具体法律意见。

### 暂不声称覆盖

- 所有国家和地区的法律、税务、许可和平台规则；
- 医疗、金融、法律代理等高风险专业服务的完整落地设计；
- 线下物流、制造、库存和雇佣的完整自动化；
- 所有行业、语言、封闭社区和私有交易数据；
- 真实客户访谈、付款、退款、复购和留存结果。

## 来源宇宙

1. 同行评审论文、作者论文页、学术工作论文和系统综述；
2. 政府、监管机构、标准组织和官方统计；
3. AI 产品官方文档、系统卡、技术报告和公开评测说明；
4. 独立能力评测、安全研究和真实任务研究；
5. 具有方法与样本说明的平台一手数据和公开实验；
6. 创业者、买家和从业者的一手案例，仅作机制与假设来源；
7. 公开讨论、评论、搜索与网页观察，仅作需求线索，不作支付结论。

旧创新闭环、旧候选和餐馆 Pilot 不作为核心假设的支持证据。

## 证据使用规则

- 厂商发布可以证明其产品、设计与自报结果，不能单独证明普遍效果。
- 单一帖子可以证明该表达出现过，不能证明人群频率、严重性或预算。
- 态度与购买意向不能替代行为；行为也必须结合可替代解释。
- Benchmark 只能支持其任务、工具、样本和评分范围内的能力判断。
- AI 生成内容不成为其自身主张的独立证据。
- 来源网页数不等于独立证据数；转载、同一主体、同一数据集与营销传播必须建依赖图。
- “公开可读”不等于可抓取、模型处理、改编、商用或转让；权利不明不得销售。
- 客户被说服或付款不能抵消欺骗、暗黑模式、弱点利用或第三方伤害。
- 每条关键结论必须标注：事实、推断、设计选择或未知。

## 对抗性检索

每个关键主张都必须主动搜索：失败、无效、选择偏差、意向—行为差距、虚假需求、平台操纵、自动化脆弱性、长任务衰减、提示注入、越权、法律责任、客户反感和单位经济不成立。

## 研究闭合条件

检索类别饱和只按冻结的 [SEARCH_SATURATION_PROTOCOL.md](./SEARCH_SATURATION_PROTOCOL.md) 执行。协议文件本身保持冻结时的 `NOT_RUN`，动态执行状态位于 Run2 外部工件；Run2 已完成两轮执行、joint 与完整 crosswalk，[`FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json`](./ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json) 已对同一 [`FINAL_RUN_STATUS.md`](./ssp-run2/FINAL_RUN_STATUS.md) exact bytes 明确 `ACCEPT`。因此 `SATURATED-WITHIN-PROTOCOL` 现只关闭类别代码本谓词，不追认历史检索，不替代主张证据、架构审查、现实外部有效性或 C4 final review。

只有同时满足以下条件，状态才能从 `BLOCKED` 变为 `CONDITIONALLY_READY`：

- 每个研究问题都有主来源和适用范围；
- 核心主张同时有支持证据与反证/边界；
- 搜索与来源日志可复查；
- 主张—证据映射不存在循环引用；
- 每个 RQ 都有 `Claim → Evidence → Scope → Counterevidence → Design Decision → Residual unknown` 记录；
- 当前能力与未来设想分开；
- 竞争架构在同任务、预算和评分口径下比较任务成功、方差、端到端延迟、总成本、人工复核、权限面、状态一致性、失败恢复与攻击下表现；没有实测的值标记为未知，不得用形容词伪装数据；
- 外部动作权限和最小人工节点明确；
- 双通道有可验证隔离、sealed outputs、污染事件与新 epoch 规则；
- 观察进入双通道前有冻结的 SamplingPlan、query/filter ancestry、完整 AcquisitionRecord、未命中/负样本和停止规则；假设条件化样本不能冒充独立 discovery，独立结论要求分离的 discovery/confirmatory 样本；
- 生命周期与法律/权利/伦理等 blocker 正交；交易对手、报价、协议、订单、里程碑、发票、支付、退款、交付、验收、结果、关系与持续义务按实体建模，候选状态只是不可反向覆写的派生视图；
- 逐主体 BuyerValue、渠道资格、采购就绪和竞争后价值捕获都有独立记录、状态与 Gate；
- 渠道、报价与成交证据绑定 SellerIdentityAndTrustContext、关系/引荐依赖和 portability；不可取消订金或正式结果承诺前，exact offer 的 DeliveryFeasibilityGate 检查关键路径、输入/权限、依赖、容量、验收、失败与回退；
- CustomerValueRealizationState/Gate 与付款、留存和收入耐久分离，逐主体/订单记录实际结果、负担、不利结果、使用、归因、锁定/取消摩擦与自愿继续；
- ActionEnvelope、原子 ResourceReservation、部分执行/对账/补救状态机与能力/自治授权均绑定确切对象、状态、模型、Harness、工具、政策、任务分布、环境、时限、撤销与回执；
- 人工批准不以“点过确认”自证有效；监督就绪记录覆盖任务能力、独立性、利益冲突、原件可见、审查容量、有效期和校准，超载或条件失效时 fail closed，并有相对普通确认框的预注册评测；
- readiness 由冻结 qualification spec 和独立签发者确证；DecisionAuthority 与 IndependentAssessor 分离，Grant 有正式 exact-hash 签发链且不能自我续期或修改 oracle/Gate/权限根；GovernanceRootPolicy 的根权限不提供给受管 Agent，变更需要双重批准与失效传播；
- 权利 BOM、right-to-sell Gate 和 assurance 依赖图完整；来源、污染或 oracle 变化能让下游状态、Eval、Grant、token 与结论确定性失效；
- EconomicModelSpec 冻结单位/cohort/窗口/价格瀑布/容量与分配政策；现金、应收/应付、预付义务、储备、已赚收入和已实现单位经济分账，SustainableIncomeState 有正向条件与自动降级路径；
- ExperimentFamily/DiscoveryCohort 保留完整候选宇宙、选择历史、sibling 结果、累计探索预算、序贯/多重比较与独立确认；CandidateInvestmentPolicy/PortfolioStopPolicy 的累计 kill/re-entry 条件跨版本执行；
- DecisionExposureRecord 记录 eligible actions、选择政策/概率或理由、处理前身份/信任/关系条件和观察窗；没有随机或可信准实验识别时不发布因果学习规则；
- OutcomeMaturityState 处理 cohort age、右删失、退款/续费/质保/支持尾部和迟到事件重算；OwnerObjectiveSpec 与 IncomeSufficiencyState 将收入耐久与用户目标充分性分离；
- 残余未知点和变化监控条件明确；
- 冻结协议 Run2 `SSP-1.0-RUN-20260727T154803-0700` 下的两轮全部查询都被逐结果筛选，没有 `NEW-CRITICAL` 或 `UNRESOLVED`，完整 CE-IN crosswalk 通过机械复算，且 lead 与独立审查者对同一 exact final-status 对象形成明确一致意见；
- candidate inventory、governance 工件与 shadow implementation 使用不重叠的精确 roots：freeze 时后两者必须不存在，后闭合时各自由单独 canonical manifest 完整覆盖并绑定 exact parent，不能用 ignore glob、symlink、路径逃逸或逐文件重封把未来可变实现混入已审设计快照；
- 最终独立复核绑定完整候选 manifest 与每个文件的 SHA-256，没有发现会改变总体架构的未处理缺口。

上述条件的候选级判定、证据路径、exact hash、残余限制和最终审查待办统一记录在 [`RESEARCH_CLOSURE_PREDICATE_MATRIX.md`](./RESEARCH_CLOSURE_PREDICATE_MATRIX.md)。矩阵不能自行把状态改成 `CONDITIONALLY_READY`：其 final-review predicate 只有在 manifest 冻结后才能由独立审查满足；随后 freeze report、review receipt 与外部 `RESEARCH_CLOSURE_DECISION` 必须进入预声明的 `机会到交易系统-闭合记录/` sibling root，由该 root 的 `GOVERNANCE_ARTIFACT_MANIFEST.json` 绑定同一 candidate manifest、receipt 与 decision，并在调用者提供 decision exact hash 的条件下通过 [`verify_post_closure_manifest.py`](./verify_post_closure_manifest.py) aggregate Gate。该哈希锚只证明调用对象的精确身份，不自行证明签发者身份或审查独立性。

`CONDITIONALLY_READY` 只允许把通过 exact-hash 终审的设计作为**本地隔离、零外部副作用的只读 shadow MVP**及其验证方案的规格输入。这个实现只能出现在另一个预声明的 sibling root `机会到交易系统-shadow-mvp/`，其 manifest 必须绑定 exact candidate、governance manifest 与 closure decision；首版可变运行数据只进入系统临时目录。这个阶段的实现只能处理合成 fixture 或已有明确授权且已本地化的只读 fixture，只能产出可追溯观察、sealed-lane 输出、需求假设、未执行的实验草案与评测记录；不得装载或暴露浏览器写入、外联、发送、发布、部署、账户、凭据、签约、报价、付款、收款、客户数据写入或生产 Harness 执行器。它也不授权把某个行业、对象、需求、价格、商机或盈利判断写成已验证事实。任何真实网络采集、具体 Pilot、外部实验或商业动作都需要在其精确 SamplingPlan、权利、身份、合规、伦理、能力与 ActionEnvelope Gate 下另行取得权限。
