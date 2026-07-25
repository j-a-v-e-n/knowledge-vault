# 产品保障蓝图 V2｜个人投研纪律工作台

状态：`candidate-design`  
设计依据：项目章程、既有系统独立审计、两轮设计冻结挑战、AI 项目失效地图、数据/纸面边界研究、相邻系统复用审查，以及候选 Money、市场模拟、真实使用和私人数据规范。

冻结条件：AI 项目方法研究通过独立挑战后，连同机器可读验收合同一起锁定。

## 产品结果

Javen 可以在一台本地 Mac 上完成以下真实流程：

1. 提出并预注册一个投资假设。
2. 保存带时间、来源和反证的证据。
3. 导出结构化研究包给 AI，导入 AI 的结构化建议。
4. 亲自接受、拒绝、延后或修改建议。
5. 由不可被订单请求绕过的确定性规则检查完整意图。
6. 只在本地 PaperAccount 中模拟订单生命周期。
7. 长期并列观察 AI 建议、人工决定与基准。
8. 从账本、备份、Obsidian 和 Git 恢复项目事实，不依赖聊天记忆。

产品不承诺策略有优势，不提供真实交易执行，不把 Paper P&L 当作可实现收益证明。

## 当前范围

### 包含

- 单用户、本地优先、只绑定 `127.0.0.1` 的工作台。
- 美国上市股票与 ETF 的研究记录；正式历史验证首期只允许人工冻结的小型宇宙。
- 日线数据支持周/月节奏。
- 结构化证据、AI 建议、人工决定、风险政策、PaperAccount、回测、复盘、审计和恢复。
- 本地 CSV/JSON 快照导入；Tiingo 只读适配器及离线契约测试。
- 本地数据和外部 Paper 之间的适配器边界与故障夹具。
- Calm UI：风险、未知、过程和到期复盘优先。

### 明确不包含

- 真实资金、live broker、实盘凭据、自动下单或自动复制外部账户状态。
- 动态全市场选股、历史指数成分回测或声称已解决所有生存者偏差。
- 高频、日内或以成交速度为优势的策略。
- 多用户、云部署、商业化、对外分享或移动端。
- 自动生成“买卖信号”作为产品价值中心。
- 用任何单个回测、Paper 账户或模型评分宣称能赚钱。

## 选择的实现边界

### 单一结构化事实源

SQLite 保存权威状态与事件。Markdown、JSON、Obsidian 页面和网页视图都从同一事实源导出，不能各自维护状态。

选择理由：

- 本地、可检查、无需外部服务。
- 支持事务、唯一约束、外键、触发器、备份和恢复。
- 可以让账户状态与审计事件在同一事务中提交。
- 当前规模不需要图数据库、工作流平台或云基础设施。

### 零运行时第三方依赖

核心使用 Python 标准库、SQLite、HTML/CSS/JavaScript。正式数据适配器使用标准库 HTTPS 客户端。

这不是“依赖越少越先进”，而是当前产品需要：

- 独立 Git 恢复后直接运行。
- 减少供应链、版本、许可证和遥测面。
- 让 AI 和人都能完整读取关键实现。

若以后确有可复现的性能、交互或协议缺口，再以对称试验引入依赖。

### 本地网页工作台

- 后端只监听 loopback。
- 写请求要求本地 mutation header 和同源 Host/Origin。
- 无 CORS、无远程登录、无 telemetry。
- UI 只显示数据库查询结果，不维护第二份业务状态。
- 视觉图由结构化节点/边生成；布局不是事实。

### AI 是离线研究协作者

系统不内置能自行提交订单的模型代理。AI 交互通过版本化 JSON 包：

```text
工作台导出 ResearchCase
  → Codex/其他 AI 调研并返回 RecommendationCandidate
  → schema、来源、时间和证据引用校验
  → 候选建议进入工作台
  → Javen 亲自提交 Decision
```

AI 可以写候选，不可以写 `human_decision`、`risk_approval`、`fill` 或风险政策生效记录。

`actor=human` 不能由请求体、导入包或普通 CLI 参数声明。高影响动作使用项目之外的本地人工确认能力建立短期、同源会话，由服务器赋予 actor；确认材料不进入 ResearchCase、Prompt、Git 或备份。直接 API、CLI、数据库、导入和回放路径都不能绕过这一能力。

这是一条协作威胁模型下的能力边界，不是“证明键盘前一定是某个人”的绝对身份认证：拥有同一 OS 用户全部权限且主动窃取确认材料的恶意进程仍可能突破。V1 必须如实陈述这个剩余风险，不能把 actor 字段测试写成“已证明真人在场”。

## 保障主张

| ID | 必须成立的主张 | 主要证据 |
| --- | --- | --- |
| A-01 | 目标没有在搭建中漂移 | 冻结意图、需求双向追踪、用户立场检察官 |
| A-02 | 决策只引用当时可知且未被事后覆盖的数据 | 原始快照、时间验证、修订并存、prefix-causality |
| A-03 | AI 建议可追溯且不会变成人工决定 | schema、角色权限、真实 UI 旅程 |
| A-04 | 风险闸门绑定完整执行请求并使用权威状态 | intent hash、事务审批、错配/伪造/并发测试 |
| A-05 | 风险规则不能被临场悄然放宽 | 不可变政策版本、延迟生效、变更事件 |
| A-06 | PaperAccount 可重启、重放、对账且不重复成交 | SQLite 事务、唯一键、状态重建、故障注入 |
| A-07 | 记录能发现局部改写、尾删、乱序和恢复缺失 | append-only trigger、hash chain、序号、外部尾锚、restore drill |
| A-08 | 历史检验不把数据挖掘包装成优势 | 预注册、试验谱系、留出封存、成本、基准、完整产物 |
| A-09 | 系统主动抑制情绪化操作 | premortem、情绪/紧迫度、冷却期、频率规则、calm UI |
| A-10 | AI、人工和基准能够长期并列复盘 | 三轨账户/快照、到期复盘、校准和过程指标 |
| A-11 | 项目和私人运行均可恢复 | Git/GitHub、带哈希数据备份、独立目录恢复 |
| A-12 | 本地产品不扩大隐私和实盘风险 | loopback、最小数据、secret scan、无 live connector |
| A-13 | 作者不能用自评批准完成 | 冻结合同、独立黑盒/故障测试、只读审查、未证明清单 |
| A-14 | 证据集合不会因同源转载、漏检反证或已更正/撤回来源而伪装成充分支持 | 检索 manifest、来源簇、revision graph、更正级联、决定性 claim 闸门 |
| A-15 | 历史比较在证券身份、市场日历、信号可用时点、公司行动、现金流和基准口径上有效 | as-of 宇宙、稳定证券 ID、显式日历、下一可交易 bar、总回报基准、独立参考序列 |
| A-16 | “有人操作过表格”不会被扩大成“人在冷静思考” | 可信人工会话、紧迫度状态机、确定性等待、随机反事实提示、长期使用协议和剩余威胁声明 |
| A-17 | 长期停用不会让旧批准、旧数据或旧语义自动恢复权威 | `resume_review_required`、批准失效、差异摘要、政策/许可/模型/Prompt/schema 重验 |
| A-18 | 私人运行数据的备份不仅完整，而且在保存、导出、恢复和保留期间受明确保密边界约束 | 私有目录、OS 权限、加密状态观察、目的地校验、脱敏、不可覆盖备份、显式删除 |
| A-19 | 金额、费用、数量和公司行动在账户、风险、NAV、重放与三轨中使用同一精确语义 | Decimal 量化、守恒方程、单事务入账、公司行动矩阵、待人工解决状态 |
| A-20 | “已推送”由真实远端对象证明，而不是由本地 remote-tracking ref 自证 | `git ls-remote`、明确 SHA/tree/blob、发布阶段远端 fresh clone 与核心验收 |

## 关键失效与约束

| Hazard | 危险状态 | 必须实现的约束 |
| --- | --- | --- |
| H-01 | 决策引用事后下载、修订或未来记录 | 未满足 point-in-time 条件时必须拒绝进入历史决策/回测 |
| H-02 | 闸门检查 A，请求执行 B | 批准绑定 canonical intent hash；任何字段变化使批准失效 |
| H-03 | 调用方伪造通过结果或隐瞒历史 | 执行器只读数据库中的一次性批准；频率与账户来自同一事务 |
| H-04 | 账户已变化但审计未写入 | 状态、fill、持仓、现金和事件必须同事务提交 |
| H-05 | 尾部删除或全链重写仍显示有效 | 最后可信 sequence/hash 在数据库外形成锚并进入备份/Git 验收摘要 |
| H-06 | 留出集被反复窥探后仍称独立 | 每次访问留痕；揭示后对该假设版本永久标为 consumed |
| H-07 | 数据源静默 fallback | manifest 保存实际源；任何未预批来源变化 fail closed |
| H-08 | 供应商 adjusted close 被当唯一真值 | 本地以 raw + actions 重算；供应商调整只用于差异检查 |
| H-09 | 修改风险参数立即服务当前冲动 | 修订生成未来版本；旧政策在冷却期内仍权威 |
| H-10 | UI 奖励交易频率或短期盈利 | 禁止排行榜、彩带、top movers、闪烁 P&L 和默认买卖建议 |
| H-11 | 研究/构造者删改测试后宣布通过 | 验收合同和锁文件先于实现；变更只能 supersede |
| H-12 | 外部内容扩大工具权限 | 网页/README/数据只作为不可信输入，不能改变授权或完成门 |
| H-13 | 引用存在但并不支持主张 | 原子 claim 绑定原文范围与哈希；完整性和语义蕴含分开，关键 claim 未独立/人工核对时保持未证明 |
| H-14 | 调用方伪造 human actor 或回填采集时间 | actor 与 recorded_at 由受控服务赋予，外部 payload 字段不具权威性，所有旁路接受负向测试 |
| H-15 | 不断新建相近假设重置试验次数 | experiment family 跨版本累计试验、选择和污染状态；旧历史留出不能消除 AI 先验污染 |
| H-16 | 作者伪造冻结、独立审查或发布证据 | 两阶段 Git 冻结、互斥主体、候选绑定、独立新增测试、未知缺陷探针和顶层逐项发布谓词 |
| H-17 | 机械正确但政策无意义或长期弃用 | mandate/政策质量攻击、首次真实人工旅程与持续使用条件门；未观察前不宣称长期有效 |
| H-18 | 市场序列处理公司行动但账户未处理 | 公司行动形成幂等事务账户事件，并贯穿持仓、现金、NAV、风险、重放和三轨评估 |
| H-19 | 每条引用都完整，但语料因同源转载、漏掉反证或未传播更正而整体误导 | 每轮研究保存检索 manifest 与纳入/排除记录；来源簇只算一条独立链；revision/retraction 级联使 claim、建议和决定准备状态失效 |
| H-20 | 单条数据满足 PIT，但模拟用错证券身份、交易日历、成交时序或价格型基准 | 冻结 as-of 宇宙与稳定 ID；显式交易所 session；收盘信号默认下一 eligible session 成交；缺日 fail closed；基准使用同日历、币种、现金流和总回报 |
| H-21 | 使用者或 AI 机械填完情绪表格，系统便把冲动操作认作冷静决定 | AI/import 不能填写权威紧迫度或反思；`urgent/panic` 由服务器时间触发不可覆盖等待并使旧批准失效；表格摩擦不被宣称为反思证明 |
| H-22 | 停用后旧批准、旧数据、旧政策或旧模型语义仍显示可继续 | 越过政策间隔或发现数据/政策/许可/模型/Prompt/schema 变化即进入 `resume_review_required`；旧批准失效、新订单只读，人工确认差异和重验后才能恢复 |
| H-23 | 备份哈希和恢复都通过，但私人数据库明文进入 Git/同步目录或泄露到日志/导出 | 私人数据策略约束默认目录、权限、symlink、OS 加密状态、目的地、分类和脱敏；V1 不自造加密；不覆盖旧备份且不由 AI 自动删除 |
| H-24 | 浮点、舍入或复杂公司行动在不同模块得到不同结果 | 只接收十进制字符串，统一 `ROUND_HALF_EVEN` 与量化；现金/持仓/费用/事件同事务；未知行动进入 `pending_manual`，更正只追加补偿事件 |
| H-25 | 本地 upstream 指向候选便被写成“远端可恢复” | 冻结时直接查询远端 ref；发布时从远端 fresh clone 确切 commit，重算 tree/blob 并在克隆副本运行核心验收 |

## 权威数据模型

### 项目与运行

- `schema_migrations`：不可跳跃的数据库版本。
- `system_settings`：非秘密、可导出的本地设置。
- `runs`：不可变 run manifest；包含代码、配置、数据、模型/Prompt、政策和账户快照哈希。
- `artifacts`：内容寻址的原始和规范化产物。
- `findings`：审查问题、严重度、状态、证据和关闭记录。

### 研究

- `hypotheses`：不可原位覆盖的假设版本、宇宙、信号、失效条件、评估计划。
- `experiment_families`：由经济机制、信号依赖图、决策节奏、宇宙族、数据变换、基准族和主指标形成不可重置的 root fingerprint；跨假设版本累计试验、选择、AI-origin contamination 和未来样本状态。
- `retrieval_manifests`：冻结研究问题、检索范围、查询、时间、返回集合、纳入/排除理由和结果哈希，使“检索过什么、没纳入什么”可复核。
- `source_snapshots`：URL/RSS/文件/人工来源的真实身份、原始内容、事件发生、published、available、recorded 时间、内容哈希和取得方式。
- `source_clusters`：把转载、聚合页和共同上游归为一条证据链；数量展示不能把同源副本算成独立支持。
- `source_revision_edges`：保存 correction、retraction、supersession 和普通更新关系；旧字节保持不可变，新 revision 触发依赖级联。
- `claims`：原子 fact/inference/hypothesis/unknown，绑定原文 byte range/hash、支持/挑战关系、验证者、状态、失效条件和依赖 revision。
- `recommendations`：模型、Prompt、输入包、证据、反证、置信、未知、行动范围和期限。
- `decisions`：只能由 human actor 创建，绑定所见建议/证据哈希、理由、偏离、情绪、premortem 和复盘日期。

### 市场身份与模拟

- `securities`：稳定 `security_id`，不把 ticker 当经济身份。
- `security_alias_intervals`：symbol/name 的 `valid_from/valid_to`；改名不新建资产历史。
- `universe_snapshots`：每个假设在测试前冻结 as-of 成分与纳入理由。
- `exchange_sessions`：带时区的显式交易所 session；数据行交集不能充当日历。
- `market_snapshots`、`corporate_actions`：原始价格与拆股/分红行动分开保存；供应商 adjusted 字段只作交叉检查。
- `benchmark_specs`：在测试前冻结基准、适用理由、币种、日历、总回报、成本、现金和覆盖口径。
- `simulation_runs`：保存信号可用时点、最早可成交 session、缺失覆盖、成本、现金流和独立参考序列差异。

### 纪律与账户

- `risk_policies`：不可变版本、创建时间、生效时间、前版本和确认记录。
- `order_intents`：绑定 decision、account、symbol、side、quantity、price model 和 canonical hash。
- `risk_evaluations`：逐规则结果、权威状态快照哈希、批准 token、一次性消费状态。
- `orders`：paper-only 生命周期。
- `fills`：部分/完整成交、费用和模型说明。
- `accounts`、`positions`、`cash_entries`：金额/数量/费用使用固定 Decimal 语义，可从事件重放并与物化状态对账。
- `account_corporate_actions`：拆股、现金分红、标的身份变化和待人工处理行动，按生效时间幂等进入账户事务。
- `behavior_checks`：由服务器记录紧迫度、随机反事实提示、最早可继续时间、回答哈希和旧批准失效；不把这些字段解释为已证明反思。
- `reviews`：到期、结果、基准、过程偏差和下一研究节点。
- `performance_snapshots`：AI 建议轨、人工决定轨和基准轨。

### 运行、恢复与保密

- `health_epochs`：最近成功健康检查、应用/数据/政策/许可/模型/Prompt/schema 指纹和停用边界。
- `resume_reviews`：进入 `resume_review_required` 的原因、失效批准、差异摘要、逐项重验和人工恢复记录。
- `backup_manifests`：内容分类、数据库/锚/产物哈希、schema、应用 commit、文件权限、OS 加密状态观察、创建时间和目标身份。

### 审计

- `events`：严格递增 sequence、run_id、actor、event_type、occurred_at、recorded_at、payload、previous_hash、event_hash。
- UPDATE/DELETE trigger：对事件、已生效政策、冻结假设、决定和 fill 直接拒绝。
- `anchor_outbox`：数据库提交后待写入外部尾锚的 sequence/hash。
- 外部 `anchors.jsonl`：追加、flush、备份；数据库尾部短于可信锚时验收失败。

本地拥有全部文件权限的人理论上可以同时重写数据库、锚和 Git 历史。因此产品只承诺“在设定威胁模型下具备篡改发现能力”，不宣称绝对不可篡改。

同理，本地 Markdown/JSON 也不能密码学证明两个 AI 审查者完全独立。保障系统要求记录 builder/reviewer/user-proxy 的主体、会话、输入哈希、候选 commit/tree、冻结包、原始结果和参与历史，并让独立者新增构造者事先未知的测试或变异；它提供可审计的认识论独立，不宣称抵御同一 OS 用户恶意串谋。

## 金额与公司行动语义

V1 只定义本地 USD、long-only PaperAccount，不把这些规则冒充券商会计、税务或实盘成交语义。

- 外部金额、价格、数量、费用和比率只接受 base-10 字符串直接解析为 Decimal；拒绝 float 输入。
- 统一使用 `ROUND_HALF_EVEN`：价格量化到 `0.000001`，数量到 `0.00000001`，金额与费用到 `0.01`，比率到 `0.00000001`。
- 买入、卖出和 NAV 使用冻结公式与守恒式；缺 mark、stale mark 或未解决公司行动产生 `incomplete`，不能静默按零。
- order/fill、费用、现金、持仓、公司行动、物化状态、审计事件和 anchor outbox 在一个 SQLite 事务中提交；任一注入失败必须完整回滚。
- 拆股、反向拆股、现金分红与 ticker/name change 按稳定身份和幂等键处理；cash merger、stock merger、spinoff、cash-in-lieu、delisting/bankruptcy 在 V1 进入 `pending_manual`，禁止猜测。
- correction/reversal 不删除原事件，只追加 linked revision 与 compensating event；受影响证券、NAV 置信和新风险批准在解决前 fail closed。

## 状态机

### 假设

```text
draft → frozen → development_tested → holdout_ready
      → holdout_consumed → supported | contested | rejected
```

- `validated` 不是普通 update 可写状态。
- 只有预注册计划、冻结数据/代码、独立留出结果、反证和明确裁决齐备，才可进入 `supported`。
- 新策略或参数修改必须创建新版本，不能继承旧留出的独立性。

### 来源修订与依赖主张

```text
source revision: observed → current → corrected | retracted | superseded
dependent claim: verified → invalidated_pending_review → reverified | withdrawn
recommendation: ready_for_human → blocked_by_evidence_revision
```

- 修订创建新快照和 revision edge，不覆盖原始字节。
- correction、retraction 或 material contradiction 必须沿依赖边传播；传播完成前，相关决定性 claim 和候选建议不得进入 ready 状态。
- 同源转载只改变可见副本数，不增加 independent support chain。

### 建议与人工决定

```text
candidate → schema_valid → ready_for_human
human: accept | reject | defer | modify | no_trade
```

任何决定都绑定候选建议哈希；修改形成新的 order intent，不改写 AI 原建议。

### 风险政策

```text
draft → acknowledged → scheduled → active → superseded
```

- 首个 mandate 与政策由 Javen 完整确认后进入 `scheduled`，至少冷静 `24h` 才能 active；冷静期内修改会重新计时。
- 修订的最早生效时间由当前 active policy 的 amendment cooldown 决定。
- AI actor、import actor 和 web API 不能创建 human acknowledgment。
- 人工确认必须来自服务器签发的本地短期能力；payload 中的 `actor=human` 永远不产生权限。

### 紧迫度与反敷衍

```text
calm(0h) | elevated(0h) | urgent(4h) | panic(24h)
```

- 紧迫度只能由 authenticated human UI 选择；AI、导入包和请求字段不能设置权威值。
- `urgent/panic` 以服务器时间创建不可覆盖 cooldown，并使此前批准失效。
- emotion 文本非空不构成通过。服务端在认证后随机选择反事实提示，记录 prompt ID、经过时间和回答哈希；这些只能证明完成了摩擦步骤，不能证明真实反思。

### Paper 订单

```text
intent_created
  → risk_rejected
  → approved → submitted_local → partially_filled → filled
                              ↘ cancelled
                              ↘ unknown → reconciling → terminal
```

本地 MVP 不伪造网络 ACK；`unknown/reconciling` 通过故障适配器验证未来外部协议边界。

### 停用与恢复

```text
operational → resume_review_required → revalidation_in_progress
            → operational | read_only_blocked
```

- 审批过期，或数据、政策、许可、模型、Prompt、schema 发生变化，或停用间隔越过预先政策边界时，必须进入 `resume_review_required`。
- 进入该状态即使旧批准失效，新订单保持只读；系统生成面向 Javen 的差异摘要，不以“进程成功启动”代表可继续。
- 恢复逐项重验数据新鲜度、政策、权限、许可、migration、模型/Prompt 和账户/账本一致性；需要人工确认的项未确认时不得回到 `operational`。

## 风险规则

具体参数不能由设计者替 Javen 猜测。首次使用必须由 Javen 设置 paper investment mandate、初始 PaperAccount 资金与风险政策；在此之前系统处于 `mandate_or_policy_missing/read_only`。

mandate 至少明确：研究/纸面目标、允许宇宙、最大可接受风险边界、禁止事项、复盘节奏和策略有效性不能如何声称。系统以极宽上限、相互矛盾、零冷却、缺少损失边界等对抗场景检查政策质量，但不替 Javen 选择具体风险偏好。

首期支持的确定性规则：

- 单笔订单相对当前 NAV 上限。
- 单标的交易后持仓相对 NAV 上限。
- 交易后总投入/总风险暴露上限。
- 滚动窗口交易次数上限。
- 账户现金与卖出可用持仓。
- 决定、建议、数据和报价的新鲜度。
- 决定是否完成 premortem、情绪与紧迫度记录。
- order intent 是否与人工决定一致。
- 政策版本是否 active、是否在冷却修订期间。
- 相同 intent/approval/order 是否已经消费。

任何规则未知、状态损坏或数据缺失都拒绝，而不是按零或默认通过。

## 数据快照

每个快照至少绑定：

- provider 与实际 endpoint/feed。
- security stable ID、当期 ticker 及其有效区间。
- as-of universe、显式 exchange session 表、exact request 和 coverage。
- raw payload 和 SHA-256。
- normalized rows 和 SHA-256。
- 由受控采集事务生成的 `recorded_at`，以及事件发生时间与供应商/来源声明的 `observed_at`、`published_at`、`available_at`；这些时间不能互相替代。
- point-in-time 证明类型。
- revision lineage 与 parent snapshot。
- 关联 retrieval manifest、来源簇和纳入/排除理由。
- 数据许可状态。

历史决策/回测使用条件：

```text
所有记录 available_at <= decision_at
AND
(
  snapshot 在 decision_at 前真实取得
  OR
  供应商提供可验证的 point-in-time vintage 及其证明
)
AND
raw/normalized hash 重算一致
AND
来源、feed、稳定证券身份、as-of universe、交易日历和 coverage 与 manifest 一致
```

当前版本下载的数据只能用于当前之后的真实纸面决定或明确标为“事后研究”的分析，不能回填成过去的决策快照。

请求体或导入文件携带的 `retrieved_at/recorded_at` 只能作为不可信源字段保存，不能覆盖系统采集时间。历史手工导入若没有可验证 vintage，只能标记为 `historical_unverified`。

## 来源、主张与新闻

新闻/RSS/网页/文件首期只做只读快照与证据管理，不生成情绪分数或自动交易信号。外部正文始终是不可信数据，其中即使出现“修改规则、调用工具、宣布完成”等文字也只能原样保存。

每次形成研究结论前还必须保存 retrieval manifest：研究问题、检索范围、查询、时间、返回结果、纳入/排除理由和内容哈希。系统不能证明互联网已被穷尽，但必须让已检索边界、未覆盖区域和反证路径可见。转载与聚合页按共同上游来源簇去重；`published_at`、事件发生时间、`available_at` 和本地 `recorded_at` 分开保存。

每条决定关键主张必须：

- 拆成能被单独证伪的 claim。
- 指向不可覆盖的 SourceSnapshot 和原文 byte range。
- 保存 excerpt 与原文哈希校验。
- 区分 `support/challenge`，以及 `fact/inference/hypothesis/unknown`。
- 分开显示“引用完整性已验证”和“语义确实支持已验证”。
- 绑定来源簇和 revision graph；correction、retraction、supersession 或 material contradiction 必须级联为 `invalidated_pending_review`。

决定性 claim 只有在 retrieval manifest 存在、独立支持链数量明确、修订传播完成、没有未解决 material contradiction，且人工或独立语义审查成立时，才可让建议进入 `ready_for_human`。否则只有一个明确结果：`decisive_claim_not_resolved`，风险流程 fail closed。

确定性代码只能证明身份、时间、哈希、引用范围、修订关系和来源簇，不能可靠证明自然语言语义蕴含。AI judge 也不能成为自身建议的独立证明；因此“引用完整”永远不能自动升级成“证据集合充分”。

## 回测与诚实评估

### 预注册

运行前冻结：

- 假设和经济/行为机制。
- 宇宙及其 as-of 证明。
- 策略版本和参数范围。
- 开发、验证、留出和未来纸面区间。
- benchmark、成本、滑点/价差压力情景。
- 主指标、失败标准和允许的试验次数。
- experiment family 的 root fingerprint、跨版本全局试验预算和 AI-origin contamination 状态；root 由经济机制、信号依赖图、决策节奏、宇宙族、数据变换、基准族和主指标共同决定，改名或换展示不能重置。

### 防止未来信息

- 策略接口每次只获得该决策时点可见的 prefix。
- 运行 prefix-causality metamorphic test：追加未来数据后，过去每个信号必须逐值不变。
- 决策 bar 与可交易 bar 的时序显式分开。
- 数据缺失不通过日期交集静默删除；必须报告 coverage。

### 模拟市场与基准有效性

- ticker 只是带有效区间的别名；每次假设在看到结果前冻结稳定证券 ID 与 as-of 宇宙。
- 显式 exchange session 表是唯一市场日历；策略、资产和 benchmark 缺失 required session 时拒绝运行，禁止用 `zip` 或日期交集隐藏。
- 依赖 session `T` 收盘的信号只能在该收盘后可知，默认最早在下一 eligible session `T+1` 按预注册价格模型成交；same-bar fill 默认禁止。
- 价格序列由 raw price 与 split/dividend action 重算；供应商 adjusted 字段只作差异检查。
- 策略收益来自账户现金、持仓、fill、费用和公司行动现金流；benchmark 必须用同币种、同起止 eligible session、同日历、明确现金/成本处理的 total-return 序列。
- golden fixture 与独立计算的参考序列逐值核对；benchmark suitability 在测试前记录，历史或 Paper 跑赢仍不能推出 live investability。

### 结果

保存完整权益序列、现金、持仓、交易、换手、成本、回撤、波动、基准和全部尝试，而不是只保存摘要赢家。

AI-origin 的污染状态缺乏证明时默认为 `unknown_contaminated`。参数、symbol、清洗或 benchmark 变化默认仍是同一 root descendant，除非独立裁决者在看结果前记录了新的经济机制。

首期记录全部试验、有效样本信息、依赖假设和不确定性，但不从历史数据输出“策略优势通过/失败”或自己无法可靠校准的“策略有效概率”。历史结果最多是 `historically_unpromising`、`historically_promising_but_unproved` 或 `contested`；决定性纵向状态只能等待预注册未来窗口关闭。留出通过只能成为继续纸面前推的证据，不能直接升级为真实资金。

模型可能在预训练或先前研究中见过历史结果，因此“AI 没打开本项目 holdout”不等于真正未见。无法证明隔离的历史留出只可作为受污染的辅助证据；决定性的优势判断必须依赖假设与实现冻结后产生的未来纸面样本。

## 三轨评估

每个可执行建议在同一市场日历、稳定证券身份、成交时序、Decimal 会计、公司行动、现金流和成本假设下产生：

1. `AI recommendation track`：AI 原始建议若机械执行的假想轨。
2. `Human decision track`：Javen 实际 Paper 决定轨。
3. `Benchmark track`：预先选定、同口径总回报基准。

复盘分开：

- 建议质量：方向、置信校准、失效条件和未知是否合理。
- 人工纪律：接受/修改/拒绝是否遵守预先规则。
- 执行质量：请求、成交、费用和计划的偏差。
- 市场结果：收益、回撤和基准差。

盈利不自动证明建议质量；亏损也不自动证明纪律错误。

## 行为设计

- 首页首先显示待复盘、风险规则、未知、数据新鲜度和系统健康。
- 创建决定前填写：为什么现在、如果错了会怎样、什么证据会改变观点、当前情绪和紧迫度。
- “等待/不交易/不知道”与买卖同等级。
- 首个 mandate/政策至少冷静 `24h`；`urgent` 新订单等待 `4h`，`panic` 等待 `24h`；政策修改和频繁决定也受 active policy 冷却，不提供运行时 override。
- AI/import 不能填写权威紧迫度或人工反思。随机反事实提示、经过时间和回答哈希用于增加可审计摩擦，但 UI 必须同时显示“这不证明已经冷静思考”的剩余风险。
- 收益图默认使用长区间和基准；不使用红绿闪烁、排行榜、连胜、彩带或 top movers。
- 拦截解释规则和修复条件，但不提供绕过按钮。
- 真实首次使用与长期行为验证分开：fixture、AI 填表、请求体 `actor=human` 或一次容易演示都不能成为个人采用证据；长期窗口开始前由 Javen 预注册负担、放弃、逾期复盘和纪律标准，失败直接进入 `design_reopened`。

## 工作台视图

1. **Today**：待决定、待复盘、阻塞、数据/账本/备份健康。
2. **Research**：假设、来源、证据、反证、未知和试验谱系。
3. **Decision**：AI 候选、人工选择、premortem、情绪、期限和完整 intent。
4. **Discipline**：active policy、未来修订、逐规则闸门、账户和对账。
5. **Evaluation**：AI/人工/基准三轨、过程指标和到期复盘。
6. **System**：目标、失效、证据、工作图，run manifest、事件链、锚、备份和审查发现。

## 恢复与版本

### Git/GitHub

跟踪：

- 章程、设计、合同、代码、测试、迁移、UI、fixture 和可公开验收摘要。

排除：

- token、私人账户、原始许可数据、运行数据库和可能含私人内容的完整 AI Prompt。

本地 `@{upstream}` 或 remote-tracking ref 只证明本地认知，不能证明远端真实存在候选。设计冻结必须对实际 origin 执行 `git ls-remote` 并匹配明确 branch/ref 与 baseline SHA；产品发布必须从远端 fresh clone 该确切 SHA，重算 commit/tree/blob 后再运行核心验收。远端不可达、ref 不匹配或克隆对象不同都 fail closed，不能沿用旧的“已推送”标签。

### 私人运行备份

默认私人运行根位于 `~/Library/Application Support/InvestmentDisciplineSystem`，必须位于项目、Git 和已知云同步根之外；目录为 `0700`、文件为 `0600`，路径中不允许 symlink 组件。

`backup` 只向已经验证的私人目的地生成新的不可变目录：

- SQLite 一致性快照。
- anchors。
- artifact manifest。
- 配置和 schema 版本。
- 每个文件 SHA-256。
- 内容分类、创建时间、应用 commit、权限和目的卷 OS 加密状态观察。

V1 不自造应用层加密，也不声称能恢复应用从未持有的 OS/FileVault 密钥。目的卷加密状态未知或未保护时，阻断 personal acceptance，除非 Javen 在项目文件之外明确接受该残余风险。日志和公开导出只允许 allowlist 字段，token、session secret 与人工确认材料在持久化前脱敏；完整私人导出要求 authenticated human action。

`verify-backup` 重算哈希、打开数据库、验证事件链、外部锚、权限和目的地边界。`restore` 只写入不存在的目标，并在独立私人目录运行 smoke/对账；已有备份永不覆盖。V1 不自动删除备份，删除是单独、明确且不委托 AI 的人工动作。

### 完成前恢复演练

1. 直接查询 origin 后，从 GitHub 的明确 commit fresh clone 到新的临时目录，并重算 commit/tree/blob。
2. 不依赖工作目录的 ignored 文件运行核心测试和空库/fixture E2E。
3. 从独立私人备份恢复运行数据库。
4. 验证事件链、锚、账户重放、Decimal/公司行动、三轨结果、私人权限和 UI smoke。
5. 保存命令、commit、manifest hash、退出状态和发现。

## AI 做项目的“用户立场检察官”

完成审查时，独立检察官只拿冻结意图、合同、候选代码和原始结果，不先看作者总结。它逐项检查：

- 哪个原始目标没有证据。
- 哪个测试会假绿。
- 哪个关键状态只在上下文。
- 哪个入口可绕过规则。
- 哪个失败/恢复/并发路径没测。
- 哪个高价值能力因容易而被提前停止。
- 哪个已知缺口阻止当前声明。
- 证据是否只是同一上游的重复副本；更正、撤回和未检索反证是否已经传播。
- PIT 通过后，证券身份、日历、成交时序、公司行动和总回报基准是否仍能制造错误比较。
- 人工字段是否可被 AI 或机械填表伪造；紧迫状态是否真正触发不可覆盖等待。
- 长期停用后，哪些批准、数据、政策、许可、模型、Prompt 和 schema 已经过期。
- 私人备份是否只证明完整，却泄露到 Git、同步目录、宽权限文件、日志或导出。
- “已推送”是否来自真实远端观察和 fresh clone，而不是本地 remote-tracking ref。

其报告进入 `evidence/reviews/` 且不可由构造者覆盖。没有 open critical/major 只是必要条件，仍需机械测试、恢复和真实用户旅程共同通过。

“独立”不是报告里的一句自我声明。每份审查证据必须绑定 reviewer 主体、参与历史、候选 commit/tree、冻结包、输入与原始运行哈希；reviewer 直接读取仓库和原始结果，并增加构造者事先未知的测试或缺陷变异。顶层发布谓词逐项重算这些关系，不信任某个 `verify_all.py` 的单独退出码。

## 四种裁决状态，不混为一谈

- `core_release_candidate`：冻结治理、全部 core cases、真实入口、事务/账户、证据更正、市场模拟、行为阻断、停用恢复、私人数据、独立审查、直接远端观察和 fresh-clone 恢复均有绑定当前候选的证据；不包含 Javen 采用或行为改善声明。
- `human_onboarding_verified`：前者基础上，Javen 通过 human-only 本地能力提交自己的 paper mandate 和风险参数，首个政策冷静期完成，并使用一份真实当前、非 fixture 市场快照完成一条含 support、challenge、unknown 和 no-trade 选项的研究—决定旅程；仍不包含长期声明。
- `longitudinal_personal_validation`：Javen 在看到结果前预注册真实使用窗口、最低真实案例、no-trade/defer、操作负担、逾期复盘、放弃定义、行为标准和失败动作；窗口关闭后全部 criteria 通过。
- `design_reopened`：field-use 在负担、放弃、恢复或纪律标准上失败，或发现新的高影响 workflow hazard；失败不能靠事后改窗口或门槛转换为通过。

顶层谓词按下列关系逐项重算，不接受单个脚本的总退出码代替：

```text
core_release_candidate =
  frozen intent/contract/architecture/research boundary
  AND research stop rule legitimately met
  AND exact requirement → control → case → oracle → raw evidence closure
  AND no open critical/major independent finding
  AND direct remote ref observation + exact-SHA fresh-clone recovery
  AND evidence-revision + market-simulation + Money/corporate-action
      + behavior + hiatus + private-data release predicates

human_onboarding_verified =
  core_release_candidate
  AND real authenticated non-fixture onboarding journey

longitudinal_personal_validation =
  human_onboarding_verified
  AND preregistered future field-use window closed
  AND every preregistered criterion passed
```

长期采用、情绪改善和投资优势必须等待各自预注册窗口与未来样本；不能为了得到“完成”而伪造时间。本蓝图仍是 `candidate-design`，第二轮挑战的 `blocked-freeze` 只产生待再次独立挑战的候选控制，不表示研究已经完成、规范已经冻结或任何上述裁决已经取得。

## 实现顺序

```text
冻结意图 / 需求 / 验收合同
  → 把旧审计反例变成失败测试
  → 检索 manifest / 来源簇 / revision propagation
  → SQLite 事件与事务内核
  → 风险批准—执行完整绑定
  → Decimal Money / 公司行动 / 可恢复 PaperAccount / 外部锚
  → 数据快照 / PIT / 稳定证券身份 / 市场日历
  → 假设 / 证据 / 建议 / 人工决定
  → 回测预注册 / root lineage / prefix-causality / total-return benchmark
  → 三轨复盘 / 紧迫度与反敷衍摩擦
  → hiatus/resume / 私人数据与备份生命周期
  → 本地工作台
  → Tiingo 离线契约 + 公开 demo 探针
  → 直接远端证明 / fresh clone / 私人备份恢复 / UI 真实旅程
  → 独立红队与用户立场检察官
```

正式数据账户试用和外部 Paper 认证不是本地构造的伪前提。没有 token 时，它们作为条件性门明确保持未证明；这不会被写成绿灯，也不会允许进入真实资金。
