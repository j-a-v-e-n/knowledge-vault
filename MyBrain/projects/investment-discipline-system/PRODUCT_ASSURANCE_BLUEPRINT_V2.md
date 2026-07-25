# 产品保障蓝图 V2｜个人投研纪律工作台

状态：`candidate-design`  
设计依据：项目章程、既有系统独立审计、AI 项目失效地图、数据/纸面边界研究、相邻系统复用审查。  
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

## 权威数据模型

### 项目与运行

- `schema_migrations`：不可跳跃的数据库版本。
- `system_settings`：非秘密、可导出的本地设置。
- `runs`：不可变 run manifest；包含代码、配置、数据、模型/Prompt、政策和账户快照哈希。
- `artifacts`：内容寻址的原始和规范化产物。
- `findings`：审查问题、严重度、状态、证据和关闭记录。

### 研究

- `hypotheses`：不可原位覆盖的假设版本、宇宙、信号、失效条件、评估计划。
- `sources`：来源身份、URL/文件、取得时间、类型和上游簇。
- `evidence_items`：事实/推断/假设/未知、支持或挑战关系、as-of 时间。
- `recommendations`：模型、Prompt、输入包、证据、反证、置信、未知、行动范围和期限。
- `decisions`：只能由 human actor 创建，绑定所见建议/证据哈希、理由、偏离、情绪、premortem 和复盘日期。

### 纪律与账户

- `risk_policies`：不可变版本、创建时间、生效时间、前版本和确认记录。
- `order_intents`：绑定 decision、account、symbol、side、quantity、price model 和 canonical hash。
- `risk_evaluations`：逐规则结果、权威状态快照哈希、批准 token、一次性消费状态。
- `orders`：paper-only 生命周期。
- `fills`：部分/完整成交、费用和模型说明。
- `accounts`、`positions`、`cash_entries`：可从事件重放并与物化状态对账。
- `reviews`：到期、结果、基准、过程偏差和下一研究节点。
- `performance_snapshots`：AI 建议轨、人工决定轨和基准轨。

### 审计

- `events`：严格递增 sequence、run_id、actor、event_type、occurred_at、recorded_at、payload、previous_hash、event_hash。
- UPDATE/DELETE trigger：对事件、已生效政策、冻结假设、决定和 fill 直接拒绝。
- `anchor_outbox`：数据库提交后待写入外部尾锚的 sequence/hash。
- 外部 `anchors.jsonl`：追加、flush、备份；数据库尾部短于可信锚时验收失败。

本地拥有全部文件权限的人理论上可以同时重写数据库、锚和 Git 历史。因此产品只承诺“在设定威胁模型下具备篡改发现能力”，不宣称绝对不可篡改。

## 状态机

### 假设

```text
draft → frozen → development_tested → holdout_ready
      → holdout_consumed → supported | contested | rejected
```

- `validated` 不是普通 update 可写状态。
- 只有预注册计划、冻结数据/代码、独立留出结果、反证和明确裁决齐备，才可进入 `supported`。
- 新策略或参数修改必须创建新版本，不能继承旧留出的独立性。

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

- 首个政策由 Javen 完整确认后建立。
- 修订的最早生效时间由当前 active policy 的 amendment cooldown 决定。
- AI actor、import actor 和 web API 不能创建 human acknowledgment。

### Paper 订单

```text
intent_created
  → risk_rejected
  → approved → submitted_local → partially_filled → filled
                              ↘ cancelled
                              ↘ unknown → reconciling → terminal
```

本地 MVP 不伪造网络 ACK；`unknown/reconciling` 通过故障适配器验证未来外部协议边界。

## 风险规则

具体参数不能由设计者替 Javen 猜测。首次使用必须由 Javen 设置；在此之前系统处于 `policy_missing/read_only`。

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
- security stable ID 与当期 ticker。
- exact request 和 coverage。
- raw payload 和 SHA-256。
- normalized rows 和 SHA-256。
- retrieved_at、observed_at、available_at。
- point-in-time 证明类型。
- revision lineage 与 parent snapshot。
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
来源、feed 和 universe 与 manifest 一致
```

当前版本下载的数据只能用于当前之后的真实纸面决定或明确标为“事后研究”的分析，不能回填成过去的决策快照。

## 回测与诚实评估

### 预注册

运行前冻结：

- 假设和经济/行为机制。
- 宇宙及其 as-of 证明。
- 策略版本和参数范围。
- 开发、验证、留出和未来纸面区间。
- benchmark、成本、滑点/价差压力情景。
- 主指标、失败标准和允许的试验次数。

### 防止未来信息

- 策略接口每次只获得该决策时点可见的 prefix。
- 运行 prefix-causality metamorphic test：追加未来数据后，过去每个信号必须逐值不变。
- 决策 bar 与可交易 bar 的时序显式分开。
- 数据缺失不通过日期交集静默删除；必须报告 coverage。

### 结果

保存完整权益序列、现金、持仓、交易、换手、成本、回撤、波动、基准和全部尝试，而不是只保存摘要赢家。

首期不计算自己无法可靠校准的“策略有效概率”。留出通过只能成为继续纸面前推的证据；不能直接升级为真实资金。

## 三轨评估

每个可执行建议在同一市场时间和成本假设下产生：

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
- 政策修改和频繁决定带有冷却，不提供运行时 override。
- 收益图默认使用长区间和基准；不使用红绿闪烁、排行榜、连胜、彩带或 top movers。
- 拦截解释规则和修复条件，但不提供绕过按钮。

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

### 私人运行备份

`backup` 生成不可变目录：

- SQLite 一致性快照。
- anchors。
- artifact manifest。
- 配置和 schema 版本。
- 每个文件 SHA-256。
- 创建时间和应用 commit。

`verify-backup` 重算哈希、打开数据库、验证事件链和外部锚。`restore` 只写入不存在的目标，并在独立目录运行 smoke/对账。

### 完成前恢复演练

1. 从 GitHub 的明确 commit 克隆到新的临时目录。
2. 不依赖工作目录的 ignored 文件运行核心测试和空库/fixture E2E。
3. 从独立私人备份恢复运行数据库。
4. 验证事件链、锚、账户重放、三轨结果和 UI smoke。
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

其报告进入 `evidence/reviews/` 且不可由构造者覆盖。没有 open critical/major 只是必要条件，仍需机械测试、恢复和真实用户旅程共同通过。

## 实现顺序

```text
冻结意图 / 需求 / 验收合同
  → 把旧审计反例变成失败测试
  → SQLite 事件与事务内核
  → 风险批准—执行完整绑定
  → 可恢复 PaperAccount 与外部锚
  → 数据快照 / PIT / 修订
  → 假设 / 证据 / 建议 / 人工决定
  → 回测预注册与 prefix-causality
  → 三轨复盘与行为摩擦
  → 本地工作台
  → Tiingo 离线契约 + 公开 demo 探针
  → 备份 / 独立恢复 / UI 真实旅程
  → 独立红队与用户立场检察官
```

正式数据账户试用和外部 Paper 认证不是本地构造的伪前提。没有 token 时，它们作为条件性门明确保持未证明；这不会被写成绿灯，也不会允许进入真实资金。

