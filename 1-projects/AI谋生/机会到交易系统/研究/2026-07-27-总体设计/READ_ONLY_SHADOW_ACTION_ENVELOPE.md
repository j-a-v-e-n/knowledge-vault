# 只读 Shadow MVP：实现权限边界

- Envelope ID：`RO-SHADOW-ENVELOPE-1.0`
- 状态：`CANDIDATE-C3-PENDING-FINAL-INDEPENDENT-REVIEW`
- 适用阶段：总体设计研究闭合后的第一阶段实现
- 默认决定：任何未明确列入“允许”的能力均为 `DENY`

## 目的

本边界只允许把通过 exact-hash 终审的总体设计转成一个可测试的本地 shadow runtime。它用于验证记录、隔离、哈希闭包、失效传播和评测语义，不用于发现或经营一个真实生意，也不构成任何市场、需求、价格、商机、交付能力或盈利结论。

## 生效条件

只有下列条件同时成立，本边界才允许开始实现：

- `RESEARCH_CLOSURE_DECISION` 对其绑定的 exact candidate manifest 得出仅限本边界的 `CONDITIONALLY_READY`；
- independent final review 对同一 manifest exact hash 明确 `PASS`，且不存在未决的 critical 或 major 项；
- governance 工件已写入候选目录的精确 sibling root `机会到交易系统-闭合记录/`，其中 canonical `GOVERNANCE_ARTIFACT_MANIFEST.json` 绑定同一候选、freeze report、review receipt 与 closure decision；aggregate Gate 还收到与 decision 字节一致的外部 expected hash，并通过候选内冻结的 post-closure verifier；
- 当前实现从候选目录的另一个精确 sibling root `机会到交易系统-shadow-mvp/` 开始，不把旧 `schema 0.1`、旧餐馆 Pilot、旧状态或旧 Harness 当作当前对象；
- runtime 的能力清单不包含本文件禁止的工具、连接器或执行器；
- 输入 fixture 满足下述来源与数据条件。

缺少任一条件时必须 fail closed；“用户最终想赚钱”“设计看起来合理”“旧测试通过”或 Agent 自述完成都不能替代这些条件。

## 允许的实现范围

允许在候选目录的父目录内新建且只新建预声明的隔离实现 root `机会到交易系统-shadow-mvp/`，实现并测试：

- closed-schema 记录对象与规范化序列化；
- append-only、content-addressed 的本地证据与派生物存储；
- `ObservationSamplingPlan`、`AcquisitionRecord`、`EvidenceNode`、`ObservationRecord` 与 `RightsRecord`；
- 彼此隔离的 `FirstPrinciplesMemo`、现实观察 lane、`SealedLaneOutput`、canary 与 `ContaminationEvent`；
- 带竞争解释、支持证据、反对证据、适用范围和最脆弱假设的 `NeedHypothesis`；
- 只作为未执行草案的 `ExperimentSpec`；
- 绑定模型、Harness、fixture、oracle、人工基线与成本记录的 `EvalSpec/EvalRun`；
- assurance dependency closure、staleness/invalidity propagation、恢复与机械验证；
- synthetic、tamper、cross-lane、contamination、rights、legacy-quarantine 和 zero-side-effect 测试。

首版验收测试的运行数据只能写入系统临时目录；`机会到交易系统-shadow-mvp/` 本身只保存进入其 canonical manifest 的实现、fixture、测试与说明。若未来要在项目内持久化 run 数据，必须先定义独立的 append-only run root 与逐次 run manifest，不能把可变运行输出混入已接受的实现候选。测试不得读取或修改项目范围外的用户数据。

## 设计快照与后闭合工件的阶段隔离

- `机会到交易系统/` 是不可变的 candidate inventory root；final review 只接受它的 exact manifest hash。
- candidate manifest 预声明 `机会到交易系统-闭合记录/` 与 `机会到交易系统-shadow-mvp/` 两个精确 sibling roots；不允许 glob、任意 ignore path、symlink 或第三个未声明 root。
- `freeze` 验证模式要求两个 sibling roots 都不存在，防止在终审前藏入 governance 或实现文件。
- final review PASS 后，先建立 governance root；其中 freeze report 证明终审时两个 sibling roots 都不存在，review receipt 绑定 exact candidate、freeze report、verifier 与本 Envelope，closure decision 再绑定 exact candidate、freeze report、exact receipt、exact shadow root 与本 Envelope，root manifest 完整绑定全部 governance 文件。
- 只有 aggregate Gate 在外部 expected decision hash 下验证 governance root 后，才可建立 shadow root；`SHADOW_ARTIFACT_MANIFEST.json` 必须绑定 exact candidate manifest、governance manifest、review receipt、closure decision 与本 Envelope，并完整列出自己的全部文件和依赖。
- frozen candidate 的任一字节变化使 RC-26、receipt、decision 和所有 downstream roots 失效；governance 变化使 shadow root 失效；shadow 实现变化只使该实现候选及其 EvalRun 失效，不反向改写已经发生的设计审查事实。

## 允许的输入

初始实现只允许：

- 项目内人工编写的合成 fixture；
- 为测试确定性失效路径而构造的 adversarial fixture；
- 明确标记为 `LEGACY_UNQUALIFIED` 的旧记录副本，仅用于证明其被拒绝或隔离；
- 已有明确授权、已本地化、无账号访问且经 `SamplingPlan + AcquisitionRecord + RightsRecord` 记录的只读 fixture；此类输入不是首版完成的必要条件。

不允许 runtime 自己从互联网、浏览器、邮箱、社交平台、云盘、账户、API 或第三方系统取回数据。公开可读不自动满足输入授权。

## 允许的输出

runtime 最多可以生成：

- 可追溯的本地 observation/evidence/rights 记录；
- 两条已封存 lane 输出及污染状态；
- `NeedHypothesis` 候选；
- 明确标记为 `UNEXECUTED` 的下一实验草案；
- 不产生现实动作的 `EvalRun` 与机械验证报告；
- `STALE / INVALID / LEGACY_UNQUALIFIED / BLOCKED` 等 fail-closed 状态。

这些输出都不是需求成立、买方存在、渠道可用、价格可接受、交易发生、可交付、客户价值实现、单位经济成立或可持续收入的证据。

## 明确禁止的能力

shadow runtime 不得装载、调用、生成可执行权限或提供间接路径来完成：

- 网络请求、实时抓取、浏览器操作或登录态读取；
- 邮件、短信、私信、评论、表单、电话、广告或任何对外触达；
- 发布、托管、部署、域名、商店、CRM、日历或第三方状态写入；
- 读取、保存、请求或使用账号、Cookie、token、API key、密码、身份凭据或支付信息；
- 报价、谈判、承诺、签约、开票、付款、收款、退款、转账或银行动作；
- 真实客户数据、敏感个人数据或未获授权资产的读取、变换或输出；
- 生成 production `ProjectHarness`、delivery permission、Action token 或可被下游解释为现实授权的工件；
- 从旧 Pilot、旧 commitment/deposit、帖子热度、内部评分或 shadow Eval 自动晋级任何商业状态。

测试、模拟、dry-run 或“只生成草稿”的命名不能让上述能力进入 runtime；首版实现中这些依赖必须不存在，而不是存在但声称暂时不调用。

## 确定性安全不变量

- 未知字段、未知记录类型、缺失父节点、错误 typed ID、hash 不匹配或未声明依赖一律拒绝；
- SamplingPlan 必须在对应采集结果可见前冻结；假设条件化样本不能满足独立 discovery 谓词；
- 两条 lane 在封存前不得读取对方输出，canary 命中会产生污染事件并使依赖派生物失效；
- 原始记录 append-only；纠正使用新事件，不得原地改写历史；
- 任一父证据、权利、污染、oracle、模型、Harness 或 closure 变化都会使受影响派生物进入 `STALE` 或 `INVALID`；
- Eval 通过只形成待独立审查的能力候选，不能产生 Grant、现实动作或商业状态；
- 旧 `schema 0.1` 输入只能得到 `LEGACY_UNQUALIFIED`，不能被无损升级或自动迁移；
- runtime 和测试必须能机械证明没有被注册的外部副作用 capability。
- candidate、governance 与 shadow 三个 inventory 必须分别闭合；通过改变路径、把文件移入未扫描目录或使用 symlink 绕过 inventory 一律拒绝。
- 三个 inventory 都拒绝 hardlink 与 FIFO/socket/device 等 special node；shadow manifest 的状态和 scope 是闭集，只能为 `SHADOW_IMPLEMENTATION_CANDIDATE / LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY`，并必须逐字声明 `external_action_authority=false`。
- verifier 只核验证据链，不创造审查独立性或 closure authority；只从可写 governance root 读取一个自称 `CONDITIONALLY_READY` 的文件不够，必须同时匹配调用者提供的 exact decision hash，且即使通过也没有外部行动权限。
- phase verifier 的 synthetic 回归必须覆盖正向闭合和 fail-closed 路径；测试只能在系统临时目录创建模拟 sibling roots，不得在候选冻结前创建真实 governance/shadow root。

## 完成定义

首版实现完成只表示：对允许的本地 fixture，系统能够形成可复算的记录闭包、隔离两条 lane、生成带竞争解释的假设与未执行实验草案、运行绑定输入的评测，并在篡改、污染、权利变化或 legacy 输入出现时 fail closed。

它不表示系统已经找到机会、接触客户、完成交易、能够赚钱或可以扩大自治。

## 升级规则

任何真实网络采集、具体 Pilot 选择、外部实验、联系人、发布、报价、账户、付款、收款、部署、客户数据或 production Harness 都超出本边界。升级必须以新的 exact action scope、来源/权利/身份/合规/伦理记录、能力评测、确定性 Gate、独立审查和用户授权为前提，不能修改本文件或在 post-closure sibling root 中新增文件后追认已经发生的动作。
