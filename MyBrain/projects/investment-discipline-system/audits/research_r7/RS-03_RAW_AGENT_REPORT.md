## Research result: RESEARCH-REFRESH-R7 / RS-03

结论：可以冻结到“供应商中立契约强冻结、供应商能力条件冻结”。本地 Paper 核心、PIT 拒绝规则、许可状态机、公司行动会计边界和外部 Paper 观察器边界可无凭据冻结；Tiingo/Alpaca 的真实许可、覆盖、认证、成交与对账不能冻结为已通过。

本轮状态：`bounded_incomplete`。原因是 primary method/standard 原文未成功取得、网页未取得完整内容哈希，且查询预算耗尽后无法执行预注册要求的 post-delta 补充轮。没有索取或访问私人凭据，没有写文件。

预注册证明：

- Git commit：`3a1bbe4565006745fb3c458066e08a4640c31268`
- 预注册文件 SHA-256：`db7e630355719e62c4c9ccd5e50d038539327ef8de952a3bf47c9e4894f30d35`
- 首条 counted query：`2026-07-25T15:44:23Z`
- [预注册 JSON](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json>)

### Sources consulted

- [Tiingo EOD](https://www.tiingo.com/documentation/end-of-day) — raw/adjusted 字段、分红、拆分、晚间修订和 token 要求。
- [Tiingo Pricing](https://www.tiingo.com/pricing)、[Terms §7.3/§15.5](https://app.tiingo.com/tos/) — 个人内部使用、再分发及终止边界；未明确授予退订后保留权。
- [Alpaca Paper Trading](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading) — Paper 凭据、IEX 权限、模拟遗漏和成交假设。
- [EODHD Terms](https://eodhd.com/financial-apis/terms-conditions) — 退订后删除义务，作为许可反证。
- [QuantConnect Corporate Actions](https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/corporate-actions) — 拆分、分红、改名、退市的事件化实现。
- [LEAN FactorFile.cs](https://github.com/QuantConnect/Lean/blob/master/Common/Data/Auxiliary/FactorFile.cs)、[AuxiliaryDataEnumerator.cs](https://github.com/QuantConnect/Lean/blob/master/Engine/DataFeeds/Enumerators/AuxiliaryDataEnumerator.cs) — 日期化因子与按交易日生成辅助事件的源码。
- [CRSP Calculations](https://www.crsp.com/products/documentation/crsp-calculations) — Tiingo 指向的 primary method；本轮返回 `502`，重试仍不可读。
- SEC 与 ISO 20022 查询 — 均为零可见结果 receipt。

### Key findings

1. **可冻结的是契约，不是供应商验收** — `DataSnapshot/DataSource/ExecutionAdapter`、fail-closed 状态和本地权威账可直接冻结；provider capability 必须保持 `unknown/conditional`。

2. **正式数据必须是不可覆盖快照** — Tiingo 同时提供 raw/adjusted 数据并会接收晚间更正；因此决策快照、后续修订和供应商调整值必须分离。[Tiingo EOD](https://www.tiingo.com/documentation/end-of-day)

3. **PIT 不能由 `date` 字段证明** — Tiingo 的价格日期表示数据所属日期，分红日期为 ex-date；它们不等于发布时间、可见时间或实际获取时间。未发现公开、可核验的 Tiingo vintage/as-of universe 证明。

4. **许可必须是显式 gate** — Tiingo 公开材料支持个人内部使用并限制分享，但本轮材料未明确授予退订后永久缓存权；这不能被推断成允许。[Tiingo Terms](https://app.tiingo.com/tos/)

5. **公司行动必须贯穿市场序列和账户** — Tiingo EOD 明示的核心字段是现金分红与拆分因子；LEAN 则将拆分、分红、改名、退市分成事件。未知、复杂或未覆盖行动必须进入 `pending_manual`，不能静默忽略。

6. **外部 Paper 只能作协议观察器** — Alpaca Paper 使用独立 key/endpoint，Paper-only 数据限于 IEX，并明确遗漏市场冲击、队列、延迟滑点、监管费和分红；其账和收益不能覆盖本地账或证明 live 可实现性。[Alpaca Paper](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading)

7. **反证否定“有 API 即可长期归档”** — EODHD 允许订阅期内私人存储，却要求终止后删除；许可必须逐供应商、逐计划验证。[EODHD Terms](https://eodhd.com/financial-apis/terms-conditions)

### Exact query ledger（UTC）

同批查询共享准确的批次开始/完成时间。

| Query | Exact query | UTC |
|---|---|---|
| Q1 | `site:tiingo.com/documentation/end-of-day "splitFactor" "divCash" "adjClose" revisions` | `2026-07-25T15:44:23Z` → `15:44:38Z` |
| Q2 | `site:tiingo.com/about terms API data personal use cache retain subscription termination` | `2026-07-25T15:44:23Z` → `15:44:38Z` |
| Q3 | `site:docs.alpaca.markets "Paper Trading" "market impact" "queue position" dividends` | `2026-07-25T15:44:23Z` → `15:44:38Z` |
| Q4 | `site:sec.gov "EDGAR Application Programming Interfaces" "does not require any authentication" "acceptanceDateTime"` | `2026-07-25T15:44:23Z` → `15:44:38Z`; 零可见结果 |
| Q5 | `site:iso20022.org "CorporateActionNotification" status event identification dates` | `2026-07-25T15:44:44Z` → `15:44:57Z`; 零可见结果 |
| Q6 | `site:github.com/QuantConnect/Lean Split Dividend Delisting DataNormalizationMode Raw source` | `2026-07-25T15:44:44Z` → `15:44:57Z` |
| Q7 | `site:quantconnect.com/docs corporate actions splits dividends delistings factor files map files point in time` | `2026-07-25T15:44:44Z` → `15:44:57Z` |
| Q8 | `site:eodhd.com/financial-apis/terms-conditions subscription termination delete downloaded data` | `2026-07-25T15:44:44Z` → `15:44:57Z`; 预注册反证查询 |

### 完整可见结果集合与筛选

搜索工具合并同批结果，没有保留逐 query 归属；以下保留完整 batch-visible set，不事后猜测归属。

Cluster：`U-TIINGO`、`U-ALPACA`、`U-EODHD`、`U-QC-LEAN`。同一 cluster 不计独立证据。

#### Batch A：Q1–Q4

| RID | 可见结果 | Screening / cluster / revision |
|---|---|---|
| A01 | [Tiingo EOD](https://www.tiingo.com/documentation/end-of-day) | 纳入；provider doc；`U-TIINGO`；mutable，无 revision log |
| A02 | [About Tiingo API](https://www.tiingo.com/about) | 排除；营销性质量主张，与 A01 同源 |
| A03 | [Tiingo Pricing](https://www.tiingo.com/pricing) | 纳入许可上下文；`U-TIINGO`；mutable |
| A04 | [Tiingo Terms](https://app.tiingo.com/tos/) | 纳入；`U-TIINGO`；Version 1，last updated `February 18th, 2026` |
| A05 | [Tiingo Pricing mirror](https://app.tiingo.com/pricing/) | 排除重复；同 A03 上游 |
| A06 | [Tiingo Privacy](https://api.tiingo.com/privacy/) | 排除；个人数据政策，不回答市场数据保留许可 |
| A07 | [Tiingo Developer Program](https://www.tiingo.com/documentation/appendix/developers) | 背景纳入；token/开发者约束；同源 |
| A08 | [Alpaca Paper Trading](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading) | 反证纳入；`U-ALPACA`；version-pinned `v1.4.2`，页面称 updated `10 months ago` |
| A09 | [Tiingo homepage](https://www.tiingo.com/) | 排除；营销/重复 |
| A10 | [Presenting Tiingo API](https://www.tiingo.com/blog/presenting-tiingo-api/) | 排除；旧博客/营销 |
| A11 | [Tiingo News API](https://www.tiingo.com/products/news-api) | 排除；不同数据集 |
| A12 | [Tiingo homepage version URL](https://www.tiingo.com/?v=1.0.24) | 排除重复 |
| A13 | [Skill vs Luck PDF](https://blog.tiingo.com/wp-content/uploads/2016/02/Skill-vs-luck.pdf) | 排除；与 RS-03 无关 |

#### Batch B：Q5–Q8

| RID | 可见结果 | Screening / cluster / revision |
|---|---|---|
| B01 | [EODHD Terms](https://eodhd.com/financial-apis/terms-conditions) | 反证纳入；`U-EODHD`；无可见 last-revised，条款允许后续修改 |
| B02 | [QuantConnect Corporate Actions](https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/corporate-actions) | 纳入；maintainer docs；`U-QC-LEAN`；v2 route |
| B03 | [US Equity Security Master](https://www.quantconnect.com/docs/v2/writing-algorithms/datasets/quantconnect/us-equity-security-master) | 背景纳入；显示 Security Master 与底层价格许可分离 |
| B04 | [LEAN QCAlgorithm.cs](https://github.com/QuantConnect/Lean/blob/master/Algorithm/QCAlgorithm.cs) | 背景；源码但范围过宽；mutable `master` |
| B05 | [LEAN Releases](https://github.com/QuantConnect/Lean/releases) | 排除；release noise，不提供稳定 claim 范围 |
| B06 | [QuantConnect v1 Handling Data](https://www.quantconnect.com/docs/v1/algorithm-reference/handling-data) | 排除；被 v2 文档 supersede |
| B07 | [LEAN issue #2064](https://github.com/QuantConnect/Lean/issues/2064) | 历史反证纳入；raw/adjusted 行为缺陷；closed by `#2427` |
| B08 | [Event Handlers](https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/event-handlers) | 纳入；公司行动按可用时点进入事件流 |
| B09 | [Cloud US Equities](https://www.quantconnect.com/docs/v2/cloud-platform/datasets/quantconnect/us-equities) | 排除重复/hosted-product scope |
| B10 | [Factor-file forum question](https://www.quantconnect.com/forum/discussion/11251/transforming-data-into-lean-format-dividend-stock-split-capital-reduction-delisting/) | 排除；未解决用户问题，不作规范证据 |
| B11 | [Requesting Data](https://www.quantconnect.com/docs/v2/writing-algorithms/securities/asset-classes/us-equity/requesting-data) | 纳入；normalization 与历史公司行动语义 |
| B12 | [Historical US Equities](https://www.quantconnect.com/docs/v2/writing-algorithms/historical-data/asset-classes/us-equities) | 背景；同源补充 |
| B13 | [Writing Algorithms Python PDF](https://cdn.quantconnect.com/docs/i/Quantconnect-Writing-Algorithms-Python.pdf) | 排除；B02 的 PDF 重复 |
| B14 | [Cloud Platform Python PDF](https://cdn.quantconnect.com/docs/i/Quantconnect-Cloud-Platform-Python.pdf) | 排除；同源重复 |
| B15 | [Cloud Platform C# PDF](https://cdn.quantconnect.com/docs/i/Quantconnect-Cloud-Platform-CSharp.pdf) | 排除；同源重复 |
| B16 | [Local Platform C# PDF](https://cdn.quantconnect.com/docs/i/Quantconnect-Local-Platform-CSharp.pdf) | 排除；范围不直接回答 RS-03 |

#### Direct locator receipts

- `QuantConnect/Lean@master:Common/Data/Auxiliary/FactorFile.cs` — 纳入；blob `097161e5008c0aa697e6e26b67909cdcfbc0f309`。
- `QuantConnect/Lean@master:Engine/DataFeeds/Enumerators/AuxiliaryDataEnumerator.cs` — 纳入；blob `a23bcf83c055b1a6bbcf7156e8414cf0836e07ca`。
- `SplitEventProvider.cs`、`DividendEventProvider.cs`、`DelistingEventProvider.cs` 三个候选 locator — 均返回 `404`，不作为证据。
- CRSP primary-method URL — `502`，重试为 non-retryable safe-open failure。

### Atomic claims

| Claim | 精确范围、entailment 与限制 | Decision effect |
|---|---|---|
| `RS03-C01` | Tiingo EOD 需要 token；公开页支持 raw/adjusted、`divCash`、`splitFactor`，并说明晚间更正。范围：Tiingo EOD L96–102、L175–227。`entailed`；exact-text hashes `c5a9…71ed`、`ed57…a00`。限制：不证明真实覆盖或质量。 | 离线契约可冻结；Tiingo acceptance 不可绿灯。 |
| `RS03-C02` | Tiingo API 为个人内部使用，限制分享；审阅的公开条款没有明确授予终止后的本地保留权。范围：Pricing License、Terms §7.3/§15.5。`entailed_scope-limited`；hash `7ebf…f967`。 | `license_status=unknown`，必须有 account-specific retention gate。 |
| `RS03-C03` | 数据所属日期、ex-date 与数据可见/获取时间不是同一概念；公开 Tiingo 页未提供可核验 vintage/as-of universe 证明。`entailed` 仅限字段语义与更正；供应商 PIT 能力为 `not_entailed/unknown`。 | PIT eligibility 只能由预决策快照或可验证 vintage 证明满足。 |
| `RS03-C04` | Tiingo EOD 明示字段不足以证明完整公司行动覆盖；LEAN 公开实现按日期保存 factor rows，并在交易日生成辅助事件。范围：FactorFile L38–40、L93–100；AuxiliaryDataEnumerator L92–97、L108–113。blob 已固定，代码行 hash `1d4a…faf2`。 | 冻结 typed action matrix；复杂/未知行动 `pending_manual`。 |
| `RS03-C05` | Alpaca Paper 需注册与独立 key/endpoint；Paper-only 为 IEX，模拟遗漏多类现实因素，并存在特定成交假设。范围：L33–48、L78–102。`entailed`；hash `75be…1d0e`。限制：旧版路径，未实测当前账户。 | 仅作 observer；本地账权威，真实 adapter release 条件化。 |
| `RS03-C06` | EODHD 明确要求订阅终止后删除数据。范围：`DATA STORAGE AND DELETION`。`entailed`；hash `ac27…3f2`。限制：只约束 EODHD，不能外推 Tiingo。 | 证明许可不能从 API 能力或个人用途推断。 |
| `RS03-C07` | ISO 查询零结果；CRSP primary method 无法读取；网页只有 excerpt SHA，没有完整内容 SHA-256；没有独立语义 reviewer。 | RS-03 研究 stop rule 未满足，状态必须是 `bounded_incomplete`。 |

上述 SHA-256 是精确可见 excerpt 的哈希，不是网页完整内容哈希；两者不能混称。

### Verbatim quotes（≤5）

> “Most US Equity prices are available at 5:30 PM EST, however exchanges may send corrections until 8 PM EST.”  
> （[Tiingo EOD，L99](https://www.tiingo.com/documentation/end-of-day)）

> “All data via the API is for internal consumption only.”  
> （[Tiingo Terms，§7.3](https://app.tiingo.com/tos/)）

> “Paper trading account does NOT simulate dividends.”  
> （[Alpaca Paper，L95](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading)）

> “Upon termination or expiration of the subscription, the subscriber is required to delete all copies of the data in their possession within one (1) month.”  
> （[EODHD Terms，DATA STORAGE AND DELETION](https://eodhd.com/financial-apis/terms-conditions)）

> `public SortedList<DateTime, List<T>> SortedFactorFileData { get; set; }`  
> （[LEAN FactorFile.cs，L40](https://github.com/QuantConnect/Lean/blob/master/Common/Data/Auxiliary/FactorFile.cs)）

### ⚠️ 矛盾或不确定

- Alpaca 同页先称 Paper 与 live 端到端相同、仅不路由交易所，随后又列出市场冲击、延迟、队列、分红等遗漏；两段不能合并成“等同 live”。
- Tiingo 公开材料支持内部个人使用，但没有明确回答退订后保留；不能把“未见禁止”消解成“允许”。
- LEAN 展示成熟事件化实现，但历史 issue `#2064` 曾报告 raw normalization 错误；开源实现不能充当正确性标准。
- Tiingo 引用 CRSP 方法，但本轮没有取得 CRSP 原文；primary method coverage 未关闭。
- Alpaca 来源是 `v1.4.2` 路径，当前真实行为必须在授权后重新验证。

### Design delta

- **许可 gate 收紧**：从“上线前确认许可”改为机器状态 `unknown → allowed/restricted/expired/revoked`；绑定条款 URL、版本/日期、个人用途、缓存、分享、退订保留和重新确认触发器。
- **PIT 时间语义收紧**：显式分开 `event/effective/ex/published/available/retrieved/decision`；供应商 `date` 不得代替可用时间。
- **修订策略收紧**：加入 `source_declared_correction_window`、`revision_observed_at`、parent snapshot；更正只追加，不能改写决策输入。
- **公司行动矩阵收紧**：V1 仅自动处理已冻结且具金样本的拆分/现金分红；改名、退市、合并、分拆等需 Security Master 或 `pending_manual`。
- **外部 Paper manifest 扩展**：记录 `paper_base_url`、`feed_entitlement`、文档/模拟模型版本、已知遗漏和 reconciliation 差异；外部状态永不覆盖本地账。
- **LEAN 使用边界**：借鉴 factor/map/event 分层并制作独立 oracle，不把 mutable `master` 或 QuantConnect 数据许可带入核心。
- **没有新增供应商角色**：R7 强化了既有四角色拆分，主要 delta 是 acceptance contract 与证据状态，不是新增架构组件。

### Gap classification

| 分类 | Gap | 是否可延期 |
|---|---|---|
| **Design closure** | 取得可读 primary method/standard；保存完整内容哈希；独立 entailment review；执行 post-delta 补充轮；冻结公司行动与许可状态 schema | 不可作为 RS-03 “closed” 延期；可在本地核心继续前保持明确 blocked 状态 |
| **Product release conditional** | Tiingo 固定宇宙真实覆盖、修订/PIT、配额、故障、计划条款和退订保留；Alpaca 当前认证、Paper hostname、IEX 权限、ACK/部分成交/断线/对账 | 可延期；不得标记 provider accepted，不得影响本地 Paper 核心 |
| **Human onboarding** | 用户自行注册、接受条款、选择计划、在本机注入 token、确认固定宇宙/风险参数/许可用途 | 必须由 Javen 完成；AI 不索取、不读取、不保存凭据 |

### Suggested next step（lead 接续用）

用本摘要可冻结 provider-neutral contract 和 conditional gates；若要把 RS-03 从 `bounded_incomplete` 关闭，下一轮只补 primary method/standard 原文、完整内容哈希、独立 entailment review 和 post-delta stability query，不提前做 Tiingo/Alpaca 私人试用。

执行期间没有发出文件写入或 Git mutation；后台 `vault backup` 将 HEAD 从预注册提交推进到 `cd3728f82b93052854b04a2231fc22937c73aa2c`，这是并发状态变化，本轮未归因或覆盖。

<oai-mem-citation>
<citation_entries>
MEMORY.md:119-122|note=[used prior provider-neutral architecture and paper-first boundary for initial routing, then verified against the preregistered checkout]
</citation_entries>
<rollout_ids>
019f83f2-e416-7883-bc44-63190cd9e356
</rollout_ids>
</oai-mem-citation>
