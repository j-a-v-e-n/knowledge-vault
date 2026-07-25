# RESEARCH-REFRESH-R8 / RS-04 RAW REPORT

- topic_id: `RS-04`
- question: 现有开源投研组件应以哪些原子模式、只读差分 oracle 或下游投影被复用，哪些整包边界必须继续排除？
- author-side final revision: `r8-rs04-author-v1`
- final topic status: `bounded_incomplete`
- status reason: 五次预注册查询、完整逐结果筛选、required snapshot classes、non-search probe、反证保留、delta freeze 与稳定性规则均完成；但预注册要求“每个决定性 claim 通过与作者分离的逐 claim 蕴含复核”，而本任务明确禁止独立 entailment review，因此该 predicate 为 false，不能写成 design closure。
- authority boundary: 本报告只研究 Paper V1 的组件复用边界；没有接入 live surface、broker 或凭据，没有安装大而未审依赖，没有把任何外部结果写入风险闸门、执行或权威 ledger，也没有替 Javen 作最终决定。

## 1. 当前状态与本轮目标

### 已有且本轮继承

R7 的待复核决定是：

1. 不以任何被审查整包替换权威核心；
2. 采用 `ExternalResearchAdapter`、`ExternalComponentManifest`、`DifferentialOracle` 和 `LedgerProjection` 边界；
3. 外部组件不得进入风险闸门、执行或权威 ledger 写路径；
4. requested 与 actual source 全链以及 prefix causality 继续作为硬门。

R7 明确遗留三个与本题直接相关的缺口：FinRL-X 未核查、没有固定 snapshot 的 differential probe、最后 architecture delta 后没有稳定性查询。本轮目标仅是按 R8 预注册关闭这些缺口，不重复 R7 的广泛发现，也不把 classic FinRL 结论外推到 FinRL-X。

### 本轮完成定义

- 精确执行 `D1`、`D2`、`S1`、`S2`、`S3`，每个 query 单独一次搜索调用；
- D1/D2 后、S1 前冻结 atomic claims 与 architecture/decision deltas；
- 保存 required snapshot classes 的 exact bytes、SHA-256 与 manifest；
- 对一个固定 snapshot 通过隔离 adapter 执行一次 differential accounting；
- 主动寻找能推翻“整包一律排除”与“原子复用等于复制小段代码”的正面反证；
- 逐 predicate 判定并保留未闭合项。

## 2. 时间边界证明

### 2.1 预注册身份

| Field | Observed value |
|---|---|
| preregistration path | `research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json` |
| preregistration commit | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` |
| author timestamp | `2026-07-25T09:13:44-07:00` |
| committer timestamp | `2026-07-25T09:13:44-07:00` |
| required UTC boundary | `2026-07-25T16:13:44Z` |
| preregistration SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` |
| observed SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` |
| exact-byte diff against commit | exit `0` |
| prereg commit ancestor of `origin/codex/investment-assurance-r7` at initial verification | exit `0` |

### 2.2 对报告写作时全部 later commits 的祖先检查

以下 commit 均位于预注册 commit 之后；逐个运行 `git merge-base --is-ancestor 7824a63… <commit>`，均返回 exit `0`。

| Later commit | Commit timestamp | Subject | Ancestor exit |
|---|---|---|---:|
| `216dde18eefb6e6e26ce3d3082252cc128c6bcd3` | `2026-07-25T09:18:09-07:00` | `vault backup: 2026-07-25 09:18:09` | `0` |
| `1ebc3f3592953cb4fe52821cd551a70921b657fb` | `2026-07-25T09:23:17-07:00` | `vault backup: 2026-07-25 09:23:17` | `0` |
| `9a930cee9915510e01880b96b6f1f2d7be476bd0` | `2026-07-25T09:28:40-07:00` | `vault backup: 2026-07-25 09:28:39` | `0` |
| `98bdf382cf34c7cc3ca5f6e889983e51c60e1695` | `2026-07-25T09:33:58-07:00` | `vault backup: 2026-07-25 09:33:58` | `0` |
| `c768ea481507a16a605cd7bdc05a83a7f8b5d8db` | `2026-07-25T09:38:36-07:00` | `vault backup: 2026-07-25 09:38:36` | `0` |
| `3a0a44285b960d172e240a87567ce62dd90a0cb1` | `2026-07-25T09:43:02-07:00` | `vault backup: 2026-07-25 09:43:02` | `0` |
| `a06f96efc3fb50ef89f5910e5eba4e8871a1d0b8` | `2026-07-25T09:46:58-07:00` | `vault backup: 2026-07-25 09:46:58` | `0` |

本代理的 RS-04 证据在交付时仍是 working-tree artifacts，不声称存在一个尚未创建的“RS-04 evidence commit”。若后续提交这些 artifacts，提交者仍须对那个 commit 重跑 ancestor check。

### 2.3 检索时间顺序

所有 counted retrieval 均晚于 `2026-07-25T16:13:44Z`，顺序与预注册一致：

| Order | query_id | Retrieval-start UTC | Relation to freeze |
|---:|---|---|---|
| 1 | `R8-RS04-D1` | `2026-07-25T16:17:26Z` | discovery |
| 2 | `R8-RS04-D2` | `2026-07-25T16:19:20Z` | discovery |
| — | discovery freeze | `2026-07-25T16:24:39Z` | before any stability query |
| 3 | `R8-RS04-S1` | `2026-07-25T16:25:53Z` | stability |
| 4 | `R8-RS04-S2` | `2026-07-25T16:27:37Z` | stability |
| 5 | `R8-RS04-S3` | `2026-07-25T16:29:18Z` | stability |

## 3. Query accounting

每个 query_id 都只对应一次单独的 `search_query` 调用；没有批量、改写、追加或第六次查询。搜索摘要只用于 discovery/screening，不冒充内容快照。

Screening schema normalization：预注册字段 `retrieved_at_utc` 映射为 receipt 顶部的 `retrieval_start_utc`；它与 `query_id` 都是该 receipt 内每一结果行继承的常量。表内逐行保存 `result_rank_or_backend_order`、locator、title、class、cluster、decision、reason 与 revision/supersession state。这样每个结果都有预注册要求的全部字段，同时不重复写相同的 query/time。

| query_id | Exact query | Calls | Visible results | Backend truncation observed | Receipt SHA-256 |
|---|---|---:|---:|---|---|
| `R8-RS04-D1` | `FinRL-X GitHub production trading framework license tests paper trading` | `1` | `32` | `false` | `163d4f02536370e2fe9d22bbdda2fd7a919870f4c299b0f8ae370c948636a014` |
| `R8-RS04-D2` | `open source backtesting engine differential testing lookahead bias independent review` | `1` | `15` | `false` | `613dddf55504fbecc45d1ab935e19ea4377d13462d1c198cbae398b7bb59f5fd` |
| `R8-RS04-S1` | `counterexample open source trading engine reliable point in time event driven regression tests` | `1` | `21` | `false` | `5516928b385bff82dc1fd9d6a66daa724c99b1dd64e31976dd44dce4b3c9723c` |
| `R8-RS04-S2` | `site:github.com open source backtest lookahead bug corporate action issue` | `1` | `18` | `false` | `dd017c7a5980a225626fa0ee5a128710895ba5b83628743898ac452df8bc1697` |
| `R8-RS04-S3` | `site:reddit.com open source backtesting engine lookahead data quality maintenance` | `1` | `24` | `false` | `a33a18e80efe84550471bd8ab3397b49a9df3c6ea3d9b2a604324e196cb1c5e9` |

完整可见结果集、原顺序、纳排、`source_class`、`upstream_cluster_id` 和 `revision_or_supersession_state` 原样收录在本报告附录 A；独立 receipt 同时保存在 `research/evidence/r8/RS-04/queries/`。

## 4. D1/D2 discovery 结果与冻结

Discovery freeze 保存于：

- `research/evidence/r8/RS-04/freezes/DISCOVERY_FREEZE_AFTER_D2.md`
- freeze UTC: `2026-07-25T16:24:39Z`
- freeze SHA-256: `8231d40bfc47c618ead5d272ed5283f46d906c5b1a283a3911ab4e241205bec4`
- freeze revision: `discovery-v1`
- freeze 边界：author freeze only，不是 independent entailment review。

### 4.1 FinRL-X 与 classic FinRL 分离

D1 的 canonical current candidate 是 [AI4Finance-Foundation/FinRL-Trading](https://github.com/AI4Finance-Foundation/FinRL-Trading)，固定到 `e65d6f0483ead7d2ef4a5fc940cdf960392a25c1`，commit timestamp 为 `2026-05-02T23:12:36+08:00`。classic [FinRL](https://github.com/AI4Finance-Foundation/FinRL) 被保留为 separate lineage / boundary-only result；本报告没有把 classic FinRL 的教育定位、旧依赖、测试或正确性结论外推到 FinRL-X。

固定 FinRL-X tree 提供真实的正面反证：Apache-2.0、共同 target-weight flow、backtest layer、walk-forward helpers，以及 paper/live Alpaca execution 位于同一 modular repository。它说明“开源整包必然没有可复用架构”是错误命题。

但同一固定 revision 也与 Paper V1 authority boundary 冲突：

- README 的 no-lookahead 声明在该 revision 没有 tracked test path / test module 对应，尽管 dependency metadata 声明 pytest packages；
- risk check 是 configurable；
- trading path 包含 Alpaca、broker credentials 与 live order surface；
- price-fetch failure path 可使用默认价格 `100.0`；
- order submission 发生在本地 JSON execution log 之前；
- target-weight interface 本身不携带本项目所需的 requested→actual source、decision-time、human-decision、risk-gate 与 authoritative event-ledger lineage。

因此，FinRL-X 的正面架构存在与“不适合作为 Paper V1 权威核心”可以同时为真。结论针对固定 revision 与当前 Paper V1，不是对 FinRL-X 整体质量的普遍否定。

### 4.2 Differential oracle 的价值与边界

D2 的 [Implementation Risk in Portfolio Backtesting](https://arxiv.org/abs/2603.20319) 直接比较多个开源 engine，支持“固定策略意图仍会因 execution/accounting semantics 不同而分歧”；其可见结果同时保留了反方向证据：特定 zero-cost regime 出现 agreement，因此不能把“所有 engine 必然分歧”当作规则。

D2 的 [Look-Ahead-Freedom as Temporal Non-Interference](https://arxiv.org/abs/2607.04958) 报告 planted leaks 可被 differential/tiling detector 漏掉，直接反对“两个实现相同就证明无未来信息”。

这两项都只按其 inspected preprint scope 使用。它们没有在本轮被当成 peer-reviewed final truth，也没有替代本项目的 prefix-causality 和 temporal/source-lineage gates。

### 4.3 对“整包排除 / 原子复用”的反证

`ml4t/backtest@459abd81f2f30dc70cf38a40da7591af3da2d02a` 是本轮最直接的 positive counterexample：固定 tree 保存 MIT license、explicit limitations、contract/regression tests、零 package import 的 in-tree reference oracle、cross-engine adapters、validation methodology 与 dependency lock。它反驳“开源 engine 只能提供营销描述”。

D2 还保留 RaptorBT 与 hftbacktest；S1 继续保留 NautilusTrader、LEAN、Penrose、OpenTRMS 与 Barter。它们共同反驳两个过宽命题：

1. “所有 open-source trading packages 都不可靠，所以整个 repository 都不能运行”；
2. “原子复用只允许复制某个函数或代码片段”。

R8 的更窄边界是：可以把 pinned whole package 当作 quarantined、read-only、non-authoritative subprocess oracle；是否接入取决于 admission evidence、surface isolation 与净维护成本。仍然拒绝把任何被检查 package 提升为 decision、risk gate、execution 或 authoritative ledger authority。

## 5. Required content snapshots

Manifest：

- path: `research/evidence/r8/RS-04/snapshots/MANIFEST.json`
- generated UTC: `2026-07-25T16:34:28Z`
- SHA-256: `8073cb65dd8bb6f98b3bb3a87875335c29a8b204a16941c648c30d17a6b96f01`
- JSON parse validation: pass。

| Required class | source_id | Fixed locator | Exact local bytes | Byte count | SHA-256 | Status |
|---|---|---|---|---:|---|---|
| one pinned current candidate repository | `R8-RS04-SNAP-FINRLX` | `AI4Finance-Foundation/FinRL-Trading@e65d6f0483ead7d2ef4a5fc940cdf960392a25c1` | `snapshots/FINRLX_e65d6f0483ead7d2ef4a5fc940cdf960392a25c1_decisive_source.tar` | `245760` | `1d950a3563d189bb75b423f3000c5e0df0faa1a876d7525049b2750dc42391fd` | satisfied |
| one maintainer test or architecture source | `R8-RS04-SNAP-ML4T` | `ml4t/backtest@459abd81f2f30dc70cf38a40da7591af3da2d02a` | `snapshots/ML4T_BACKTEST_459abd81f2f30dc70cf38a40da7591af3da2d02a_tests_architecture.tar` | `798720` | `71639a2719b276ee13306f05482e51144d8724ab04870269017405a913e4e274` | satisfied |
| one independent issue, security report, or user counterexample | `R8-RS04-SNAP-AITRADER-76` | `HKUDS/AI-Trader#76` | `snapshots/AITRADER_issue_76_response.json` | `7235` | `3ec5e5e1609e113029cbf5860d5c3f26f46999f793f5a3d2d3646ced9ff14eaf` | satisfied |
| same required independent class; additional fixed counterexample | `R8-RS04-SNAP-NAUTILUS-4564` | `nautechsystems/nautilus_trader#4564` | `snapshots/NAUTILUS_issue_4564_response.json` | `8175` | `075db22c33e20b6762d13954ac0045650cc53d6f2741927ce042a0318c2633cb` | satisfied |
| same required independent class; additional fixed counterexample | `R8-RS04-SNAP-NAUTILUS-4470` | `nautechsystems/nautilus_trader#4470` | `snapshots/NAUTILUS_issue_4470_response.json` | `7346` | `34fa610ba8a0f6244fbacdecfe869d6ba29c1257019786530fab1b540c494e10` | satisfied |

对应 GitHub API transport headers 也保存 exact bytes；manifest 记录 byte count、SHA-256、ETag、Last-Modified 与 GitHub API version。AI-Trader issue 的 comments endpoint 没有保存，因此 closed state 不被当作 fix proof；两个 Nautilus issue 的 separate comments 也没有保存，因此不裁决 maintainer response 或 proposed fix。

两个 tar 都是固定 commit 的 selected decisive blobs，不冒充 full-repository archive。manifest 中保存了 tree、blob IDs、source ranges、license/quotation boundary，并通过 `git hash-object` 抽查 exact payload。

## 6. Required non-search probe

### 6.1 固定对象与隔离边界

| Artifact | SHA-256 |
|---|---|
| `probe/FIXED_INPUT.json` | `ff1fbcf608f23e450d09fde9ad54bb7bf0eb9195022ef74da1027649c48d782b` |
| `probe/run_differential_accounting.py` | `91fcc6cac312d1236be8e5fd6ac5f1ec892b9ade019310f1942f95d1e0e05523` |
| `probe/R8-RS04-P1_RECEIPT.json` | `da337f9a4af2071ea112b4ea389a0109a3e7b5dfd880f69e499c489afb99cdd1` |

执行时间：`2026-07-25T16:40:34.246724Z`。

执行命令：`python3 -I probe/run_differential_accounting.py`。

adapter 只从 SHA-verified ML4T tar 读取并执行 SHA-verified `tests/oracle/engine.py`；没有 import `ml4t` package，没有第三方 dependency，没有 broker、credential、HTTP、socket、subprocess 或 live-surface code。独立侧使用 Decimal accounting，不共享 external oracle implementation。

### 6.2 Observation

固定 case 是一个 `SAME_BAR` long round trip，receipt 对 entry/exit fill、gross PnL、fees、net PnL、returns、slippage costs、total PnL 与 final cash 做逐字段比较。receipt 的最终 observation 是：

```json
{
  "all_fields_within_declared_tolerance": true,
  "causality_claimed": false,
  "classification": "agreement_within_tolerance",
  "routing": "review_only",
  "winner_selected": false
}
```

绝对容差为 `0.000000001`。完整 external value、independent value 与 absolute difference 收录在附录 B 和 exact JSON receipt。

### 6.3 Probe interpretation

本次 observation 只说明该固定 long round-trip accounting profile 在声明容差内一致。它不覆盖 short、partial fill、corporate action、event ordering 或 prefix causality；external side 运行的是 repository reference oracle，不是 package SUT；两个实现也可能共享同一个错误 semantic assumption。因此：

- agreement 不关闭 correctness 或 causality gate；
- disagreement 若出现也只进入 review，不自动选赢家；
- 本次没有连接 live surface、broker 或 credential，也没有安装依赖。

## 7. Final atomic claims（author-side only）

以下 claims 已从 discovery freeze 的 `discovery-v1` 整理为 `r8-rs04-author-v1`。`author_entailment` 是作者自己的 source-to-claim 判断，不是 independent verdict。

### R8-RS04-C01

- claim_id: `R8-RS04-C01`
- topic_id: `RS-04`
- claim_text: 在固定 commit `e65d6f0483ead7d2ef4a5fc940cdf960392a25c1`，FinRL-X 提供真实的 modular target-weight、backtest 与 paper/live architecture；但当前保存的 repository evidence 不足且边界不兼容，不能替换 Paper V1 authoritative core。
- impact: `high`
- evidence_cluster_ids: `FINRLX-UPSTREAM`, `FINRLX-PAPER`
- source_snapshot_ids: `R8-RS04-SNAP-FINRLX`
- source_ranges: `README.md:38-44,117,208,263`; `src/trading/trade_executor.py:45,131-146,280-316,318-351,398-426`; `src/backtest/backtest_engine.py:124-242,290-340`; `src/strategies/adaptive_rotation/walk_forward.py:182-367,451-475`; `LICENSE`; `requirements.txt`
- author_entailment: `partially_entailed`——positive architecture 与 incompatible surfaces 由固定代码/README 支持；“不能替代本项目 authority”包含 project-fit inference。
- limitations: 没有执行 FinRL-X live path；D1 没找到固定、独立的 FinRL-X correctness review；没有把 classic FinRL 结论投射到 FinRL-X。
- decision_effect: `rejection` from authoritative core；`defer` future isolated research-adapter admission。

### R8-RS04-C02

- claim_id: `R8-RS04-C02`
- topic_id: `RS-04`
- claim_text: fixed-snapshot differential accounting 可暴露 implementation/semantic risk，但 agreement 不是 correctness、prefix causality 或 temporal-lineage certificate。
- impact: `high`
- evidence_cluster_ids: `IMPLEMENTATION-RISK-STUDY`, `TEMPORAL-NONINTERFERENCE`, `ML4T-BACKTEST-UPSTREAM`, `R8-RS04-PROBE-P1`
- source_snapshot_ids: `R8-RS04-SNAP-ML4T`, `R8-RS04-PROBE-P1`
- source_ranges: `tests/test_oracle_differential.py:1-134`; `tests/oracle/engine.py:1-220`; `validation/METHODOLOGY.md:1-90,229 onward as applicable`; `probe/R8-RS04-P1_RECEIPT.json:comparison,outcome,limitations`
- author_entailment: `entailed_with_scope_limits`——probe 证明可执行的逐字段 comparison receipt；D2 sources 和 probe limitations共同否定“agreement 等于 causality proof”。
- limitations: D2 两项是 inspected preprints；本轮没有保存其 PDF exact bytes；probe 仅一个 synthetic long case，且 external side 是 in-repo reference oracle。
- decision_effect: `contract` strengthening for `DifferentialOracle`；agreement 不能旁路 prefix gate，disagreement 必须 review-only。

### R8-RS04-C03

- claim_id: `R8-RS04-C03`
- topic_id: `RS-04`
- claim_text: 具有明确 semantics、tests、limitations、fixed revision 与可隔离入口的 open-source engine，可以 whole-package 形式被评估为 quarantined non-authoritative oracle；“原子复用”不应被解释为必须复制代码或拒绝每个 packaged executable。
- impact: `major`
- evidence_cluster_ids: `ML4T-BACKTEST-UPSTREAM`, `RAPTORBT-UPSTREAM`, `HFTBACKTEST-UPSTREAM`, `NAUTILUS-UPSTREAM`, `LEAN-UPSTREAM`, `PENROSE-UPSTREAM`, `OPENTRMS-UPSTREAM`, `BARTER-UPSTREAM`
- source_snapshot_ids: `R8-RS04-SNAP-ML4T`, `R8-RS04-SNAP-FINRLX`
- source_ranges: `ML4T README.md:21,262-347`; `LIMITATIONS.md:1-210`; `tests/contracts/test_cross_engine_contracts.py`; `uv.lock`; FinRL-X selected architecture ranges in `R8-RS04-SNAP-FINRLX`
- author_entailment: `decision_fit_candidate`——positive candidates 足以推翻 blanket rejection，但不等于任一 candidate 已通过本项目 admission。
- limitations: 除 ML4T/FinRL-X 外，S1 positive candidates 没有全部在本轮固定 revision 或做同题 local trial；没有证明 net maintenance benefit。
- decision_effect: `defer` to pinned admission test；允许 quarantined read-only subprocess，禁止 authority transfer。

### R8-RS04-C04

- claim_id: `R8-RS04-C04`
- topic_id: `RS-04`
- claim_text: target-weight interface 是可复用的 atomic strategy-output pattern，但只有在 source、temporal、human-decision、gate 与 actual-execution lineage 作为独立 mandatory records 保存时，才可进入 Paper V1 candidate flow；weight 本身不能承载 authority。
- impact: `major`
- evidence_cluster_ids: `FINRLX-UPSTREAM`
- source_snapshot_ids: `R8-RS04-SNAP-FINRLX`
- source_ranges: `README.md:38-44`; `src/strategies/base_strategy.py`; `src/trading/trade_executor.py:131-146,398-426`
- author_entailment: `decision_fit_candidate`——interface observation 来自固定 tree；mandatory lineage 是它与 Paper V1 invariant 的 project-fit inference。
- limitations: 不主张 target weights 本质不安全，也不主张 FinRL-X 无法在其自身目标下工作。
- decision_effect: `contract` on `ExternalResearchAdapter`；weights 只能作为 candidate output。

### R8-RS04-C05

- claim_id: `R8-RS04-C05`
- topic_id: `RS-04`
- claim_text: maintainer architecture/test claims 不能消除 live/order/retrieval surface 的独立 failure counterexample；manifest 必须明确 optional bypass、actual default、live-surface reachability 与 requested→actual lineage，而不能用 repository maturity 代替这些 gates。
- impact: `major`
- evidence_cluster_ids: `AITRADER-ISSUE-76`, `NAUTILUS-ISSUE-4564`, `NAUTILUS-ISSUE-4470`, `FINRLX-UPSTREAM`
- source_snapshot_ids: `R8-RS04-SNAP-AITRADER-76`, `R8-RS04-SNAP-NAUTILUS-4564`, `R8-RS04-SNAP-NAUTILUS-4470`, `R8-RS04-SNAP-FINRLX`
- source_ranges: issue JSON fields `number,state,title,created_at,updated_at,closed_at,author_association,comments,body`; FinRL-X `src/trading/trade_executor.py:45,131-146,280-316,318-351,398-426`
- author_entailment: `entailed_as_counterexample_not_incidence`——exact issue bytes证明这些固定 reports 存在并给出 reproduction；不把 user report 当作 universal defect rate 或 maintainer-confirmed root cause。
- limitations: AI-Trader issue comments 未保存，closed 不证明已修；Nautilus issue comments 未保存，不裁决 proposed fix；live incident 内容没有在本轮独立复现。
- decision_effect: `gate` and `reopen trigger` for `ExternalComponentManifest`；不是自动 package rejection。

## 8. 独立 entailment review 边界

本报告没有执行、伪装或代替 independent claim-by-claim entailment review：

- 没有创建 reviewer identity；
- 没有为任何 claim 填写 `reviewer_locator`、`review_input_sha256`、`verdict`、`checked_source_ranges` 或 `overclaim_or_missing_counterevidence`；
- 没有把 author freeze、probe agreement、issue state 或另一个 maintainer test 当作 independent reviewer verdict。

这正是最终状态必须为 `bounded_incomplete` 的决定性原因。

## 9. 反证与矛盾保留

### 9.1 反对 blanket package rejection 的证据

- FinRL-X 在一个 repository 内提供 modular target-weight、backtest、walk-forward 与 paper/live flow；
- ML4T 固定 tree 提供 tests、explicit limitations、reference oracle、cross-engine contracts 与 lock；
- S1 的 NautilusTrader、LEAN、Penrose、OpenTRMS、Barter 以及 D2 的 RaptorBT、hftbacktest 保留为 positive candidate / locator；
- 本轮 fixed ML4T oracle probe 在声明 accounting profile 下 `agreement_within_tolerance`。

决定影响：删除“所有 package 都不可靠”这个 straw proposition；保留“任何 package 不得自动成为 Paper V1 authority”这个更窄边界。

### 9.2 反对“差分必然找到错误”的证据

- D2 implementation-risk result 在其特定 zero-cost regime 报告 agreement；
- 本轮 probe 也得到 agreement；
- temporal-non-interference result 与本轮 probe limitation 都说明 same-bug / same-assumption agreement 仍可能发生。

决定影响：差分是 review instrument，不是 correctness certificate。

### 9.3 反对“成熟 repository 等于 boundary safe”的证据

- AI-Trader 固定 issue 保存了 backtest retrieval 返回 post-decision news 的 reproduction；
- Nautilus 固定 issues 保存了 strategy scope / instrument scope mismatch，以及 connectivity loss 后 order-incarnation/reconciliation failure reports；
- FinRL-X 固定 tree 同时包含 live broker/credential surface、configurable risk check 与 fabricated default-price path。

决定影响：测试数量、production-grade 声明、same-code-path 或 repository maturity 不能替代本项目自己的 adapter isolation、lineage、reconciliation 与 prefix gates。

### 9.4 未找到的反证

S2 exact query 的可见结果中没有 corporate-action-specific bug。该空缺被保留为 bounded coverage gap；没有改写 query，也没有追加第六次搜索。

## 10. Frozen architecture / decision delta

Discovery deltas 在 `2026-07-25T16:24:39Z` 冻结。S1–S3 没有改变 revision。

### R8-RS04-DLT-01 — high-impact `DifferentialOracle` contract

每个 comparison receipt 必须绑定：

- fixed input snapshot hash 与 ordered rows；
- component repository/commit、dependency lock、command、environment 与 adapter hash；
- named execution/accounting semantics；
- per-field expected/actual 与 tolerance；
- divergence class、适用时的 implementation-uncertainty interval，以及最终 decision conclusion 是否改变；
- agreement 不满足 prefix-causality 或 temporal-lineage gate；
- 每个 disagreement 强制进入 human/reviewer routing，禁止 automatic winner。

Executable mapping：

- contract: 增加上述 receipt schema；
- test: fixed-snapshot per-field differential fixture，加 semantic-profile mismatch 与 planted same-bug negative control；
- gate: 缺字段、输入未固定、adapter hash 不匹配、agreement 被用作 causality proof，均拒绝；
- review: divergence 只进入 review；
- rejection: 不允许外部 engine result 直接覆盖本地权威结果。

### R8-RS04-DLT-02 — major `ExternalComponentManifest` admission delta

Manifest 必须增加：

- tracked-test inventory 与 observed test command/receipt，和 dependency declaration 分开；
- declared behavior 与 observed defaults；
- optional bypass、fail-open 与 fabricated-default paths；
- live/broker/credential surfaces 是否存在，以及 adapter 中不可达的证据；
- documented limitations 与 revision freshness。

Executable mapping：

- contract: manifest schema；
- test: adapter reachability negative tests、default/failure-path fixtures、test-command receipt；
- gate: 只有 declared dependency 而没有 tracked/observed test 不算通过；live surface 可达即拒绝；
- defer: dependency/runtime 或维护成本未证明净收益时不接入；
- rejection: 任何 authority、execution 或 ledger-write capability。

### R8-RS04-DLT-03 — clarification, not reversal

- 继续拒绝任何 package 作为 authoritative-core replacement；
- 允许 pinned whole package 在 admission 后作为 quarantined read-only oracle，不需要复制其 internals；
- package surface 或 dependency cost 不成比例时，仍优先自行实现小型 architecture pattern。

该 clarification 是对“atomic reuse”的精确定义，不是 authority decision reversal。

## 11. Stability

最后一个 discovery-stage high-impact delta 是 `R8-RS04-DLT-01`。预注册 passing rule 要求它之后至少一个 reserved stability query 不产生新 high-impact failure class、decision reversal 或 open critical/major contradiction。

| Stability query | New high-impact failure class | Decision reversal | Open critical/major contradiction | Revision effect |
|---|---|---|---|---|
| `R8-RS04-S1` | none | none | none | positive candidate expansion only；no delta |
| `R8-RS04-S2` | none | none | none | strengthens existing lineage/prefix/manifest gates；no delta |
| `R8-RS04-S3` | none | none | none | wording/test refinement only；no delta |

S3 是最后一次预留查询，`last-query high-impact delta=false`。因此 RS-04 的 stability passing rule 为 `pass`；没有添加第六次查询。

## 12. Residual gaps 与 reopen triggers

### Residual gaps

1. 决定性 claims 没有独立逐 claim entailment review；这是 closure-blocking gap。
2. D2 两项 preprint 没有保存 PDF exact bytes，也没有在本轮完成独立复核。
3. FinRL-X 没有 observed maintainer test run；固定 revision 没有 tracked test path，本轮也没有执行 live path。
4. probe 只覆盖一个 synthetic long round trip；不覆盖 short、partial fills、corporate actions、event ordering、prefix causality 或 package SUT。
5. S2 没有返回 corporate-action-specific issue。
6. AI-Trader 与 Nautilus issue comments endpoints 没有保存；issue body 只作为 fixed counterexample，不裁决修复或 root cause。
7. S1 positive candidates 没有全部固定 revision、保存 dependency locks 或通过同任务 admission trial。
8. 没有法律意见级 license review，也没有 longitudinal maintenance-cost evidence。

### Reopen triggers

- FinRL-X、ML4T、Nautilus 或拟接入 candidate 出现新 release、license change、重大 security/correctness issue；
- admission test 暴露本轮分类之外的 live reachability、semantic mismatch、fabricated default、dependency 或 maintenance failure；
- fixed-snapshot differential 发生 decision-changing divergence，或同一 conclusion 对 semantic profile / adapter revision 不稳定；
- paper reconciliation、recovery drill 或 prefix-causality test 与当前 frozen assumptions 冲突；
- 新证据证明某个 package 能在不转移 authority 的情况下显著降低实现/维护风险，或证明 quarantined whole-package oracle 仍无法被可靠隔离；
- 完成与作者分离的逐 claim review，并发现 overclaim、missing counterevidence 或 source-range mismatch。

## 13. Topic closure predicates

| # | Predicate | Status | Evidence / reason |
|---:|---|---|---|
| 1 | 预注册 commit、文件 hash、祖先关系和检索时间通过 | `pass` | commit/hash exact match；当前可见 later commits ancestor exit 均为 `0`；五次 retrieval 均晚于 `2026-07-25T16:13:44Z` |
| 2 | 五个 query_id 均有且仅有一次执行或明确工具失败 receipt | `pass` | D1、D2、S1、S2、S3 各 `1` 次；无改写、批量或第六次 query |
| 3 | 全部可见结果有逐结果筛选记录且归属唯一 query_id | `pass` | 附录 A 与五个独立 receipts 保存原顺序及全部 required screening fields；无 backend truncation warning |
| 4 | required snapshot classes 均有保存字节与哈希 | `pass` | pinned current candidate、maintainer tests/architecture、independent issue 均为 satisfied；manifest JSON valid |
| 5 | 每个决定性 claim 通过独立逐 claim 蕴含复核 | `false` | 任务明确禁止独立 entailment review；本报告只有 author-side entailment |
| 6 | 矛盾与反证已保留且有决定影响 | `pass` | positive package evidence、differential agreement、fixed failure issues 与 no-corporate-action-result gap 均保留 |
| 7 | 稳定性 passing rule 满足 | `pass` | DLT-01 后 S1、S2、S3 均无 high-impact delta；最后查询无 delta |
| 8 | architecture / decision delta 落到 executable contract、test、gate、defer 或 rejection | `pass` | DLT-01、DLT-02、DLT-03 分别给出 contract/test/gate/review/defer/rejection mapping |
| 9 | 残余风险和重开触发器明确 | `pass` | 见第 12 节 |

## 14. Final status

`RS-04 = bounded_incomplete`。

这是 predicate-driven 状态，不是对研究质量的模糊保留：固定查询预算已经用完，stability 已通过，required bytes 与 probe 已完成；唯一明确为 false 的 closure predicate 是 independent claim entailment review。根据预注册，任一 predicate false 即不能进入 design closure。本报告也不暗示 implementation、machine provenance、post-candidate semantic review、Javen final decision 或 final release 已完成。

## Appendix A — 五次查询的完整可见结果与逐结果筛选

以下内容逐字嵌入五个独立 query receipts；rank 顺序就是 backend 可见顺序。每个结果从 receipt header 继承 query_id 与 retrieval UTC，并逐行保留 locator、title、class、cluster、纳排理由与 revision/supersession state。

<details>
<summary>D1 complete receipt</summary>

# R8-RS04-D1 query receipt

- query_id: `R8-RS04-D1`
- exact_query: `FinRL-X GitHub production trading framework license tests paper trading`
- retrieval_start_utc: `2026-07-25T16:17:26Z`
- search_tool_calls_for_query_id: `1`
- call_shape: one `search_query` entry; `response_length=long`
- visible_result_count: `32`
- backend_truncation_observed: `false` (the tool emitted no truncation warning or continuation cursor)
- accounting_note: Result order below is the exact visible backend order. Search snippets are discovery aids only and are not treated as content snapshots.

## Complete visible-result screening

| rank | url_or_fixed_locator | title | source_class | upstream_cluster_id | screening_decision | screening_reason | revision_or_supersession_state |
|---:|---|---|---|---|---|---|---|
| 1 | https://github.com/AI4Finance-Foundation/FinRL-Trading | GitHub - AI4Finance-Foundation/FinRL-Trading: FinRL-X: An AI-Native Modular Infrastructure for Quantitative Trading · GitHub | open_source_primary | FINRLX-UPSTREAM | include | Canonical FinRL-X candidate repository; decisive for current code, license, tests, and live/paper surface after pinning. | Mutable branch result; exact commit pending non-search pin. |
| 2 | https://arxiv.org/abs/2603.21330 | FinRL-X: An AI-Native Modular Infrastructure for Quantitative Trading | primary_preprint | FINRLX-PAPER | include | Primary architecture paper for the named FinRL-X system. | Versioned arXiv record; exact version pending snapshot. |
| 3 | https://github.com/AI4Finance-Foundation/FinRL-Trading/releases | Releases · AI4Finance-Foundation/FinRL-Trading · GitHub | maintainer_release_page | FINRLX-UPSTREAM | include | Maintainer release locator and paper/live architecture description; same upstream as repository, not independent support. | Mutable release index; release/tag identity pending pin. |
| 4 | https://doi.org/10.1007/978-981-92-2014-4_23 | FinRL-X: An AI-Native Modular Infrastructure for Quantitative Trading \| Springer Nature Link | peer_reviewed_primary | FINRLX-PAPER | include | Published conference-paper record; same authors and mechanism lineage as the preprint. | Fixed DOI; first-online date visible as 2026-07-14. |
| 5 | https://github.com/AI4Finance-Foundation/FinRL | GitHub - AI4Finance-Foundation/FinRL: FinRL®: Financial Reinforcement Learning. 🔥 · GitHub | open_source_primary_adjacent | FINRL-CLASSIC | include_boundary_only | Confirms classic FinRL is a distinct/superseded educational-research codebase and points to FinRL-X; no classic-FinRL finding will be projected onto FinRL-X. | Mutable classic-repo branch; separate product lineage. |
| 6 | https://t.co/KoRicm8OCz | GitHub - AI4Finance-Foundation/FinRL: FinRL®: Financial Reinforcement Learning. 🔥 · GitHub | redirect_mirror | FINRL-CLASSIC | exclude_duplicate | Redirect duplicates rank 5 and adds no independent evidence. | Mutable redirect to classic repo. |
| 7 | https://huggingface.co/papers/2603.21330 | Paper page - FinRL-X: An AI-Native Modular Infrastructure for Quantitative Trading | secondary_paper_index | FINRLX-PAPER | exclude_duplicate | Mirrors/indexes the same FinRL-X paper; canonical arXiv/DOI preferred. | Mutable index of fixed paper identity. |
| 8 | https://gitrepotrend.com/repo/AI4Finance-Foundation/FinRL | AI4Finance-Foundation/FinRL — 15.7k Stars \| GitRepoTrend | third_party_repo_index | FINRL-CLASSIC | exclude_duplicate | Third-party mirror/index of classic FinRL, not FinRL-X and not authoritative for code or license. | Mutable mirror; separate classic project. |
| 9 | https://github.com/ai4finance-foundation/finrl-meta | GitHub - AI4Finance-Foundation/FinRL-Meta: FinRL­®-Meta: Dynamic datasets and market environments for FinRL. · GitHub | open_source_primary_adjacent | FINRL-META | exclude_out_of_scope | Adjacent dataset/environment repository, not the FinRL-X candidate under review. | Mutable separate repository. |
| 10 | https://arxiv.org/abs/2011.09607 | FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading in Quantitative Finance | primary_preprint_adjacent | FINRL-CLASSIC-PAPER | exclude_out_of_scope | Classic FinRL paper; cannot establish FinRL-X behavior. | Versioned older paper; superseded for FinRL-X architecture. |
| 11 | https://gitextract.com/AI4Finance-Foundation/FinRL | Full Code of AI4Finance-Foundation/FinRL for AI - Complete Repository Source \| GitExtract | third_party_code_mirror | FINRL-CLASSIC | exclude_duplicate | Unpinned third-party extraction of classic FinRL. | Mutable mirror; separate classic project. |
| 12 | https://ai4finance.org/research/finrl-open-source.html | FinRL-X: An AI-Native Modular Infrastructure for Quantitative Trading | maintainer_project_page | FINRLX-UPSTREAM | include_supporting | Maintainer description and canonical repository locator; same upstream and therefore not independent. | Mutable live page; current retrieval only. |
| 13 | https://finrl.ai/ | Home - FinRL | maintainer_product_page | FINRL-ECOSYSTEM | exclude_marketing | Broad ecosystem/product page; insufficiently revisioned and not needed once repository and paper are pinned. | Mutable live page. |
| 14 | https://ai4finance.org/research | Research \| AI4Finance Foundation | maintainer_research_index | FINRLX-UPSTREAM | include_locator_only | Maintainer index corroborates publication and repository identity, but adds no independent mechanism evidence. | Mutable live index. |
| 15 | https://arxiv.org/abs/2111.09395 | FinRL: Deep Reinforcement Learning Framework to Automate Trading in Quantitative Finance | primary_preprint_adjacent | FINRL-CLASSIC-PAPER | exclude_out_of_scope | Classic FinRL paper, not FinRL-X. | Versioned older paper; separate architecture. |
| 16 | https://openfin.engineering.columbia.edu/sites/default/files/content/publications/3490354.3494366.pdf | FinRL: Deep Reinforcement Learning Framework to Automate | primary_paper_copy_adjacent | FINRL-CLASSIC-PAPER | exclude_out_of_scope | Classic FinRL publication copy, not FinRL-X. | Fixed PDF of older classic framework. |
| 17 | https://finrl.readthedocs.io/_/downloads/en/latest/pdf/ | FinRL Documentation | maintainer_documentation_adjacent | FINRL-CLASSIC-DOCS | exclude_out_of_scope | Documentation for classic FinRL; not evidence about FinRL-X internals. | Mutable `latest` documentation. |
| 18 | https://finrl.readthedocs.io/_/downloads/en/stable/pdf/ | FinRL Documentation | maintainer_documentation_adjacent | FINRL-CLASSIC-DOCS | exclude_out_of_scope | Stable classic-FinRL documentation; distinct from FinRL-X. | Mutable `stable` alias; older separate project. |
| 19 | https://arxiv.org/abs/2511.12599 | FINRS: A Risk-Sensitive Trading Framework for Real Financial Markets | primary_preprint_adjacent | FINRS | exclude_out_of_scope | Different framework; does not answer FinRL-X license/tests/paper-trading question. | Versioned paper; unrelated candidate. |
| 20 | https://riunet.upv.es/server/api/core/bitstreams/768e61a6-70bc-4db6-be43-9dd80c9677cc/content | On the exploration of Deep Reinforcement Learning in Stock Trading through the framework FinRL | academic_secondary_adjacent | FINRL-CLASSIC-USAGE | exclude_out_of_scope | Evaluation/use of classic FinRL rather than current FinRL-X. | Fixed repository bitstream; separate classic framework. |
| 21 | https://www.reddit.com/r/SideProject/comments/1sbj2nt/i_opensourced_my_statistical_arbitrage_engine/ | I open-sourced my statistical arbitrage engine – finds cointegrated trading pairs, backtests mean-reversion strategies, paper trades. Built with Python/FastAPI + React. Would love feedback | practitioner_project_report | HEDGEVISION-USER | exclude_out_of_scope | Unrelated self-authored project; no evidence about FinRL-X and no pinned independent review. | Mutable user thread, 2026-era; self-report. |
| 22 | https://www.reddit.com/r/algotrading/comments/e030rm | I'm creating an open-source trading framework. Looking for feedback/suggestions | practitioner_counterexample | USER-FRAMEWORK-LOSS | include_counterexample_only | User reports a framework moving from live gains to losses; useful only as a failure hypothesis against treating production/live claims as reliability proof. | Mutable user thread; old and not FinRL-X-specific. |
| 23 | https://www.reddit.com/r/algotrading/comments/1l0l4ei | Are there any open source reinforcement learning spot-environments to test agents? | practitioner_question | FINRL-CLASSIC-USAGE | exclude_weak | Question merely points to “FinRL GitHub”; no fixed implementation or observed result. | Mutable user thread; ambiguous classic/FinRL-X reference. |
| 24 | https://www.reddit.com/r/IndiaAlgoTrading/comments/1u062qe/removed/ | [Removed] | practitioner_counterexample_unrecoverable | USER-PARTIAL-FILL | include_counterexample_only | Visible snippet reports a rare partial-fill/cancel-modify drift and reconciliation lesson; content is removed, so it cannot bear a decisive claim or satisfy saved-bytes snapshot class. | Removed/mutable thread; snippet-only and non-decisive. |
| 25 | https://www.reddit.com/r/IndiaAlgoTrading/comments/1uv8grj/built_an_opensource_papertrading_broker_for/ | Built an open-source paper-trading broker for NSE/BSE (Python) — realistic fees, T+1, order book. Looking for feedback. | practitioner_counterexample | USER-PAPER-DATA-QUALITY | include_counterexample_only | Visible discussion identifies survivorship and corporate-action risks in a paper engine’s fallback data; usable only as a failure/reopen hypothesis. | Mutable user thread; independent of FinRL-X but not authoritative incidence evidence. |
| 26 | https://www.reddit.com/r/opensource/comments/112vhhh | I made an open-source tool to build, test, and deploy algotrading strategies! | practitioner_project_report | HFT-EXT-USER | exclude_out_of_scope | Self-promotion for another tool; no FinRL-X evidence. | Mutable old thread. |
| 27 | https://www.reddit.com/r/MachineLearning/comments/li5ybp | [P] FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading in Quantitative Finance | practitioner_paper_discussion | FINRL-CLASSIC-PAPER | exclude_duplicate | Discussion of classic FinRL paper; canonical paper is available and distinct from FinRL-X. | Mutable old discussion; classic framework. |
| 28 | https://www.reddit.com/r/algotrading/comments/1tfy0um/sanity_check_papertrading_silver_system_with/ | Sanity check: paper-trading silver system with deterministic risk engine, free data collectors, and later LLM agents | practitioner_design_thread | USER-SILVER-SYSTEM | exclude_out_of_scope | Unrelated proposed system; no FinRL-X implementation evidence. | Mutable user thread; design request rather than fixed result. |
| 29 | https://www.reddit.com/r/reinforcementlearning/comments/tsv55f | [R] Reinforcement learning in Finance project | practitioner_paper_discussion | FINRL-CLASSIC-PAPER | exclude_duplicate | Repeats classic FinRL capability claims and does not inspect FinRL-X. | Mutable old thread; classic framework. |
| 30 | https://www.reddit.com/r/MachineLearning/comments/tsv4sv | [R] Reinforcement Learning in Finance research | practitioner_paper_discussion | FINRL-CLASSIC-PAPER | exclude_duplicate | Cross-community repetition of classic FinRL claims; same upstream paper/repository. | Mutable old thread; classic framework. |
| 31 | https://www.reddit.com/r/Python/comments/112viv7 | I made an open-source tool to build, test, and deploy algotrading strategies! | practitioner_project_report | HFT-EXT-USER | exclude_duplicate | Crosspost of rank 26 for a different tool. | Mutable old crosspost. |
| 32 | https://www.reddit.com/r/algotrading/comments/1u6w3ra/removed/ | [Removed] | practitioner_counterexample_unrecoverable | USER-BACKTEST-SELECTION | include_counterexample_only | Visible snippet raises out-of-sample selection and walk-forward concerns; removed content cannot support a decisive claim or saved snapshot. | Removed/mutable thread; snippet-only. |

## D1 accounting

- Included for direct FinRL-X examination: ranks `1`, `2`, `3`, `4`, `12`, `14`.
- Included only to enforce the classic-FinRL/FinRL-X non-projection boundary: rank `5`.
- Included only as practitioner failure hypotheses/counterexamples: ranks `22`, `24`, `25`, `32`.
- All other ranks were screened out as duplicate, adjacent, marketing-only, weak, or out of scope.
- Same-upstream rule: ranks `1`, `3`, `12`, and `14` are one maintainer cluster; ranks `2` and `4` are one author/paper cluster. They are not counted as independent confirmations.

</details>

<details>
<summary>D2 complete receipt</summary>

# R8-RS04-D2 query receipt

- query_id: `R8-RS04-D2`
- exact_query: `open source backtesting engine differential testing lookahead bias independent review`
- retrieval_start_utc: `2026-07-25T16:19:20Z`
- search_tool_calls_for_query_id: `1`
- call_shape: one `search_query` entry; `response_length=long`
- visible_result_count: `15`
- backend_truncation_observed: `false` (the tool emitted no truncation warning or continuation cursor)
- accounting_note: Result order below is the exact visible backend order. Search snippets are discovery aids only and are not treated as content snapshots.

## Complete visible-result screening

| rank | url_or_fixed_locator | title | source_class | upstream_cluster_id | screening_decision | screening_reason | revision_or_supersession_state |
|---:|---|---|---|---|---|---|---|
| 1 | https://arxiv.org/abs/2603.20319 | Implementation Risk in Portfolio Backtesting: A Previously Unquantified Source of Error | primary_empirical_preprint | IMPLEMENTATION-RISK-STUDY | include_decisive | Direct differential study across open-source engines; reports agreement boundaries, cost-driven divergence, and source-code defects. It directly tests the value and limits of a differential oracle. | Versioned arXiv record dated 2026-03-19; exact version/artifact pending snapshot. |
| 2 | https://arxiv.org/abs/2607.04958 | Look-Ahead-Freedom as Temporal Non-Interference: A Verifiable Correctness Property for Backtesting and Agentic Trading Pipelines | primary_formal_preprint | TEMPORAL-NONINTERFERENCE | include_decisive | Directly formalizes temporal non-interference and reports planted leaks missed by differential/tiling detectors; potential counterevidence to treating differential agreement as causality proof. | Versioned arXiv record dated 2026-07-06; exact version/artifact pending snapshot. |
| 3 | https://en.wikipedia.org/wiki/QuantConnect | QuantConnect | secondary_encyclopedic | LEAN-UPSTREAM-BACKGROUND | exclude_secondary | General background and unverified deployment counts; canonical LEAN repository/tests are preferable. | Mutable secondary page. |
| 4 | https://en.wikipedia.org/wiki/Purged_cross-validation | Purged cross-validation | secondary_encyclopedic | PURGED-CV-BACKGROUND | exclude_secondary | Method background, but not engine differential testing or a primary source. | Mutable secondary page. |
| 5 | https://www.alphabench.in/raptorbt | RaptorBT: Rust Backtesting Engine for AI Agents · alphabench | maintainer_product_documentation | RAPTORBT-UPSTREAM | include_positive_candidate | Claims a small deterministic MIT engine and exposes an architecture/test surface; useful as a candidate counterexample to blanket whole-package rejection, subject to pinned repo inspection. | Mutable live product/docs page; code revision not visible in result. |
| 6 | https://foresight.trading/ | Foresight — native-code backtester for Pine Script | vendor_product_documentation | FORESIGHT-UPSTREAM | exclude_not_open_fixed | Public beta/vendor page with parity claims but no fixed open-source revision in the visible result; cannot satisfy the open-source candidate requirement. | Mutable beta product page. |
| 7 | https://arxiv.org/abs/2601.13770 | Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance | primary_benchmark_preprint_adjacent | LOOKAHEADBENCH | exclude_adjacent | Focuses LLM temporal knowledge rather than backtesting-engine accounting/causality semantics. | Versioned arXiv paper dated 2026-01-20. |
| 8 | https://www.avogrowth.com/case-studies/backtesting-engine | Apex Backtesting Engine: Eliminating Look-Ahead Bias at 425M Rows \| Avo Case Studies | vendor_case_study | APEX-CASE-STUDY | include_hypothesis_only | Reports event/ingestion-time failures and a backtest/live gap, but is a vendor case study without fixed source or independent reproduction. It can generate failure probes only. | Mutable marketing/case-study page; no pinned code/data. |
| 9 | https://ml4trading.io/docs/backtest/ | ML4T Backtest | maintainer_test_architecture | ML4T-BACKTEST-UPSTREAM | include_decisive_candidate | Maintainer documentation exposes explicit execution profiles and claimed differential validation against VectorBT, Backtrader, Zipline, and LEAN; suitable for pinned tests/architecture inspection. | Mutable live docs; exact repository commit pending non-search pin. |
| 10 | https://www.manifoldbt.com/ | Manifold-BT, Python Backtesting Library with Rust Core | vendor_product_documentation | MANIFOLDBT-UPSTREAM | exclude_marketing | Self-authored product comparisons and performance claims with no fixed open-source revision in the result. | Mutable product page. |
| 11 | https://www.foxalgo.io/ | FoxAlgo — Independent Strategy & Indicator Research | commercial_research_marketing | FOXALGO | exclude_unverifiable | Claims independent audits but decisive reports are paywalled and no reproducible engine snapshot is exposed. | Mutable commercial page. |
| 12 | https://shreyanshsharma.me/projects/algorithmic-backtesting-engine/ | A Modular Backtesting Engine for Algorithmic Trading — Shreyansh Kumar Sharma | maintainer_project_page | NCBACKTESTER-UPSTREAM | exclude_weak | Self-description of another engine; no independent review or pinned test evidence in the result. | Mutable personal project page. |
| 13 | https://git.hubp.de/sahmed0/backtesting-quant-engine | GitHub - sahmed0/backtesting-quant-engine: Work in Progress · GitHub | repository_proxy_mirror | SAHMED-BACKTEST | exclude_proxy_wip | Proxy/mirror result explicitly marked work in progress; canonical GitHub locator and fixed revision absent. | Mutable proxy of WIP repository. |
| 14 | https://pypi.org/project/nullius/0.1.0/ | nullius · PyPI | versioned_package_maintainer | NULLIUS-UPSTREAM | include_atomic_pattern | Versioned falsify-first package advertises prefix-invariance and negative controls; useful as an atomic test-pattern candidate, not as an authoritative engine. | Fixed package page `0.1.0`; source/artifact inspection pending. |
| 15 | https://github.com/nkaz001/hftbacktest | GitHub - nkaz001/hftbacktest: Free, open source, a high frequency trading and market making backtesting and trading bot, which accounts for limit orders, queue positions, and latencies, utilizing full tick data for trades and order books(Level-2 and Level-3), with real-world crypto trading examples for Binance and Bybit · GitHub | open_source_primary | HFTBACKTEST-UPSTREAM | include_positive_candidate | Canonical open-source event-driven engine candidate with detailed order/latency semantics; potential counterexample to blanket whole-package rejection, subject to scope and pinned tests. | Mutable branch result; exact commit pending non-search pin. |

## D2 accounting

- Decisive discovery candidates: ranks `1`, `2`, and `9`.
- Positive candidates actively retained against blanket whole-package exclusion: ranks `5` and `15`.
- Atomic test-pattern candidate: rank `14`.
- Failure-hypothesis-only source: rank `8`.
- Same-upstream caution: the implementation-risk paper and ML4T engine may share authors/code lineage; they must not be counted as independent of each other until authorship and repository provenance are checked.

</details>

<details>
<summary>S1 complete receipt</summary>

# R8-RS04-S1 query receipt

- query_id: `R8-RS04-S1`
- exact_query: `counterexample open source trading engine reliable point in time event driven regression tests`
- retrieval_start_utc: `2026-07-25T16:25:53Z`
- search_tool_calls_for_query_id: `1`
- call_shape: one `search_query` entry; `response_length=long`
- visible_result_count: `21`
- backend_truncation_observed: `false` (the tool emitted no truncation warning or continuation cursor)
- accounting_note: Result order below is the exact visible backend order. Search snippets are discovery aids only and are not treated as content snapshots.

## Complete visible-result screening

| rank | url_or_fixed_locator | title | source_class | upstream_cluster_id | screening_decision | screening_reason | revision_or_supersession_state |
|---:|---|---|---|---|---|---|---|
| 1 | https://nautilustrader.io/ | NautilusTrader: open-source algorithmic trading platform | maintainer_architecture_and_test_page | NAUTILUS-UPSTREAM | include_positive_counterevidence | Direct positive counterexample: deterministic event core, replay, same research/live model, and multiple test classes. Must be pinned before bearing a claim; still includes live execution. | Mutable live page advertising v1.230.0; repository revision pending non-search pin if selected. |
| 2 | https://pypi.org/project/ml4t-backtest/ | ml4t-backtest · PyPI | package_registry_maintainer | ML4T-BACKTEST-UPSTREAM | include_supporting_duplicate | Current package locator supports the already frozen positive candidate; same maintainer/code lineage, not independent stability evidence. | Mutable current PyPI index; package versions are separately immutable. |
| 3 | https://www.quantconnect.com/ | Open Source Algorithmic Trading Platform. - QuantConnect.com | maintainer_product_page | LEAN-UPSTREAM | include_positive_counterevidence | Maintainer claims PIT data and a large regression surface; canonical pinned LEAN source/tests remain preferable and were already an R7 positive pattern. | Mutable product/cloud page; claims span open engine and hosted service. |
| 4 | https://github.com/lefeverela/nautilus_trader_test | GitHub - lefeverela/nautilus_trader_test: A high-performance algorithmic trading platform and event-driven backtester · GitHub | fork_or_mirror_repository | NAUTILUS-MIRROR | exclude_duplicate | Noncanonical fork/mirror; canonical Nautilus source is rank 1’s target. | Mutable noncanonical repository. |
| 5 | https://www.quantconnect.com/splash | Open Source Algorithmic Trading Platform. - QuantConnect.com | maintainer_product_page_duplicate | LEAN-UPSTREAM | exclude_duplicate | Duplicate landing route for rank 3. | Mutable product page. |
| 6 | https://penrose.systems/ | Penrose - Quant Research Platform | maintainer_research_tool_page | PENROSE-UPSTREAM | include_positive_counterevidence | No-live, falsification-first, sandboxed generated code, fixed referee/human approval, and Apache-2.0 claims directly challenge an over-broad package exclusion; repository must be pinned and inspected. | Mutable live page; exact repository commit pending non-search pin. |
| 7 | https://opentrms.com/ | OpenTRMS — Open Source Trading & Risk Management System | maintainer_product_architecture_page | OPENTRMS-UPSTREAM | include_positive_counterevidence | Event-sourced audit, database write restrictions, replay, scoped agents, and human approval challenge blanket rejection of packaged trading controls; needs pinned source/tests and is adjacent to rather than identical with Paper V1. | Mutable live page; repository revision not visible in result. |
| 8 | https://pypi.org/project/ml4t-backtest/0.1.0b14/ | ml4t-backtest · PyPI | versioned_package_maintainer | ML4T-BACKTEST-UPSTREAM | exclude_superseded | Fixed older beta package from the already examined upstream. | Immutable version `0.1.0b14`, superseded by later repository state. |
| 9 | https://kiploks.com/ | Kiploks - Trading Bot Strategy Robustness, Walk-Forward Testing & Open Source Engine | maintainer_product_page | KIPLOKS-UPSTREAM | include_locator_only | Falsification/robustness claims are relevant, but the result does not expose a pinned repository, exact gate, or independent reproduction. | Mutable product page; open-source revision not fixed. |
| 10 | https://github.com/barter-rs/barter-rs | GitHub - barter-rs/barter-rs: Open-source Rust framework for building event-driven live-trading & backtesting systems · GitHub | open_source_primary | BARTER-UPSTREAM | include_positive_counterevidence | Canonical modular Rust engine with mock/live components and claimed tests; positive package counterexample, but live surface and dependency/runtime scope remain outside current Paper V1 authority. | Mutable branch result; exact commit pending pin if selected. |
| 11 | https://git.hubp.de/nautechsystems/nautilus_trader | GitHub - nautechsystems/nautilus_trader: Production-grade Rust-native trading engine with deterministic event-driven architecture · GitHub | repository_proxy_mirror | NAUTILUS-UPSTREAM | exclude_proxy_duplicate | Proxy of canonical Nautilus repository; canonical GitHub commit is required. | Mutable proxy. |
| 12 | https://pypi.org/project/ml4t-backtest/0.1.0b10/ | ml4t-backtest · PyPI | versioned_package_maintainer | ML4T-BACKTEST-UPSTREAM | exclude_superseded | Older beta from the same examined upstream. | Immutable version `0.1.0b10`, superseded by later beta/repository state. |
| 13 | https://arxiv.org/abs/1509.08248 | Correctness of Backtest Engines | primary_preprint | BACKTEST-CORRECTNESS-PAPER | include_supporting | Directly relevant correctness framing; old paper does not establish current candidate reliability but may support test design. | Versioned arXiv paper, 2015-era. |
| 14 | https://arxiv.org/abs/2102.01499 | Event-Driven LSTM For Forex Price Prediction | primary_preprint_adjacent | EVENT-LSTM | exclude_out_of_scope | “Event-driven” refers to modeling/features, not a regression-tested trading-engine architecture. | Versioned paper. |
| 15 | https://arxiv.org/abs/2107.00856 | A Practical Guide to Counterfactual Estimators for Causal Inference with Time-Series Cross-Sectional Data | primary_preprint_adjacent | CAUSAL-TSCS | exclude_out_of_scope | Statistical counterfactual estimation, not trading-engine event/PIT correctness. | Versioned paper. |
| 16 | https://arxiv.org/abs/2206.13237 | The DEBS 2022 Grand Challenge: Detecting Trading Trends in Financial Tick Data | primary_challenge_paper_adjacent | DEBS-CHALLENGE | exclude_out_of_scope | Event-processing benchmark, not portfolio accounting, PIT, or regression reliability. | Versioned paper. |
| 17 | https://www.usenix.org/event/atc10/tech/full_papers/usenixatc10_proceedings.pdf | conference proceedings 2010 USENIX Annual Technic | proceedings_pdf_adjacent | USENIX-2010 | exclude_out_of_scope | Broad proceedings with a search-snippet mention of Marketcetera; no direct current candidate result. | Fixed proceedings PDF; unrelated scope. |
| 18 | https://catalogimages.wiley.com/images/db/pdf/9781118460146.excerpt.pdf | untitled | book_excerpt_secondary | EVENT-DRIVEN-BOOK | exclude_secondary | General explanation of event-driven backtest/live parity; not an open-source regression receipt. | Fixed excerpt, old secondary source. |
| 19 | https://static.usenix.org/events/atc10/tech/full_papers/usenixatc10_proceedings.pdf | conference proceedings 2010 USENIX Annual Technic | proceedings_pdf_mirror | USENIX-2010 | exclude_duplicate | Mirror of rank 17. | Fixed duplicate PDF. |
| 20 | https://wiredspace.wits.ac.za/server/api/core/bitstreams/912439c9-4f70-407b-8524-9daf5eae73c8/content | University of the Witwatersrand | academic_repository_bitstream_adjacent | WITS-MATCHING-ENGINE | exclude_out_of_scope | Student/research matching-engine work; not current portfolio-backtest package evidence. | Fixed repository bitstream. |
| 21 | https://pure.au.dk/ws/files/136779731/Christoffer_Quist_Adamsen_thesis.pdf | Automated Testing Techniques for | academic_thesis_adjacent | EVENT-TESTING-THESIS | exclude_out_of_scope | Generic automated testing of event-driven applications; not trading-engine-specific evidence. | Fixed thesis PDF. |

## S1 delta assessment

- New high-impact failure class: `none`.
- Decision reversal: `none`.
- Open critical/major contradiction: `none` at screening stage.
- Supporting positive counterevidence: Nautilus, LEAN, Penrose, OpenTRMS, and Barter demonstrate that whole repositories can contain serious architecture/test mechanisms. This rejects the straw proposition “all open-source trading packages are unreliable.”
- Effect on frozen decision: no package is promoted into the authoritative core. Penrose/OpenTRMS/Barter are new candidate names but fit the already frozen `pinned + quarantined + read-only/non-authoritative + admission-gated` category; candidate-set expansion alone is not an architecture delta.

</details>

<details>
<summary>S2 complete receipt</summary>

# R8-RS04-S2 query receipt

- query_id: `R8-RS04-S2`
- exact_query: `site:github.com open source backtest lookahead bug corporate action issue`
- retrieval_start_utc: `2026-07-25T16:27:37Z`
- search_tool_calls_for_query_id: `1`
- call_shape: one `search_query` entry; `response_length=long`
- visible_result_count: `18`
- backend_truncation_observed: `false` (the tool emitted no truncation warning or continuation cursor)
- accounting_note: Result order below is the exact visible backend order. Search snippets are discovery aids only and are not treated as content snapshots.

## Complete visible-result screening

| rank | url_or_fixed_locator | title | source_class | upstream_cluster_id | screening_decision | screening_reason | revision_or_supersession_state |
|---:|---|---|---|---|---|---|---|
| 1 | https://github.com/microsoft/qlib/issues/1930 | Backtest results stay the same regardless of model used · Issue #1930 · microsoft/qlib | implementation_issue_user_report | QLIB-ISSUE-1930 | include_counterexample | A user reports invariant backtest outputs across model changes; useful as a metamorphic failure hypothesis, but issue resolution/cause must be inspected before attributing an engine defect. | Closed issue opened 2025-05-23; mutable comments. |
| 2 | https://github.com/freqtrade/freqtrade/issues/10294 | why does backtesting not work as live mode does? · Issue #10294 · freqtrade/freqtrade | implementation_issue_user_maintainer_dialogue | FREQTRADE-ISSUE-10294 | include_decisive_counterexample | Directly records whole-dataframe backtest/live divergence, detector limits, same-candle execution ambiguity, and the maintenance/performance cost of iterative prefix execution. | Closed issue opened 2024-06-08; mutable comments. |
| 3 | https://github.com/Limex-com/ziplime | GitHub - Limex-com/ziplime: ZipLime - Reinventing the Classic Backtesting Experience of Zipline · GitHub | open_source_primary_self_description | ZIPLIME-UPSTREAM | exclude_not_issue | Repository marketing result rather than a fixed bug/corporate-action issue; no independent counterexample in the visible result. | Mutable repository fork. |
| 4 | https://github.com/HKUDS/AI-Trader/issues/76 | [Bug] Future Information Leakage (Lookahead Bias) in `get_information` Tool During Backtesting · Issue #76 · HKUDS/AI-Trader | implementation_issue_user_reproduction | AITRADER-ISSUE-76 | include_decisive_counterexample | Detailed user reproduction shows post-decision news entering an agent backtest and affecting an action; directly supports temporal lineage/prefix tests for retrieval tools. | Closed issue opened 2025-11-03; mutable comments; fix status requires issue activity inspection. |
| 5 | https://github.com/microsoft/qlib/issues/855 | backtest · Issue #855 · microsoft/qlib · GitHub | implementation_issue_question | QLIB-ISSUE-855 | exclude_weak | Generic help request with no visible mechanism, reproduction conclusion, or counterexample. | Closed old issue. |
| 6 | https://github.com/nautechsystems/nautilus_trader/issues | Issues · nautechsystems/nautilus_trader · GitHub | issue_index | NAUTILUS-ISSUES | include_counterexample_locator | Current visible issue index includes a backtest reporting losses with zero orders/positions and a lifecycle panic, counterbalancing broad reliability claims; individual issue must be fixed by number. | Mutable issue index; visible open issues include `#4055` and `#4054`. |
| 7 | https://github.com/microsoft/qlib/issues/1623 | examples\nested_decision_execution\workflow.py not work · Issue #1623 · microsoft/qlib | implementation_issue_user_reproduction | QLIB-ISSUE-1623 | include_counterexample | Open calendar/data-availability boundary failure in nested decision execution; supports explicit calendar revision and availability fixtures. | Open issue opened 2023-08-15; mutable. |
| 8 | https://github.com/freqtrade/freqtrade/issues/10380 | Lookahead analysis get_open_trades misjudgment · Issue #10380 · freqtrade/freqtrade | implementation_issue_detector_false_positive | FREQTRADE-ISSUE-10380 | include_counterexample | Maintainer explains an apparent lookahead finding can arise from changed test-period/scenario selection; detector output requires interpretation and cannot be an oracle alone. | Closed issue opened 2024-06-28; mutable comments. |
| 9 | https://github.com/freqtrade/freqtrade/issues/9240 | Concerning lookahead-analysis · Issue #9240 · freqtrade/freqtrade | implementation_issue_user_error | FREQTRADE-ISSUE-9240 | include_supporting | Explicit future shift is correctly identified; supports a planted-positive control but is not an engine bug. | Closed issue opened 2023-09-29. |
| 10 | https://github.com/freqtrade/freqtrade/issues/4276 | availability of trade profit while generating sell signals · Issue #4276 · freqtrade/freqtrade | implementation_issue_maintainer_design_tradeoff | FREQTRADE-ISSUE-4276 | include_decisive_counterexample | Maintainer states whole-range vectorized indicators are retained for speed/hyperopt and users must avoid lookahead; demonstrates that package architecture may knowingly delegate causality safety to strategy authors. | Closed issue from 2021; mutable comments. |
| 11 | https://github.com/freqtrade/freqtrade/issues/11642 | lookahead-analysis: Not clear how to avoid the bias · Issue #11642 · freqtrade/freqtrade | implementation_issue_detector_boundary | FREQTRADE-ISSUE-11642 | include_counterexample | Discussion distinguishes no-lookahead from severe recursive/startup-history error; one green detector does not close other temporal correctness classes. | Mutable issue opened 2025-era. |
| 12 | https://github.com/nkaz001/hftbacktest | GitHub - nkaz001/hftbacktest: Free, open source, a high frequency trading and market making backtesting and trading bot, which accounts for limit orders, queue positions, and latencies, utilizing full tick data for trades and order books(Level-2 and Level-3), with real-world crypto trading examples for Binance and Bybit · GitHub | open_source_primary | HFTBACKTEST-UPSTREAM | exclude_duplicate | Positive candidate already located and pinned during discovery; not a bug issue. | Pinned separately at `5f3ec40…`; result itself is mutable. |
| 13 | https://github.com/fraunhoferhhi/vvenc/wiki/data/vvenc-v1.3.1-v1.pdf | VVC™ is a trademark of Media Coding Industry Forum. | unrelated_pdf | VVENC | exclude_out_of_scope | Video-codec lookahead option, unrelated to trading/backtesting. | Fixed PDF. |
| 14 | https://enterprise.github.com/downloads/en/enterprise-datasheet.pdf | Whether they are 10 person startups or teams of thousands, development teams of all sizes use GitHub | unrelated_vendor_pdf | GITHUB-ENTERPRISE | exclude_out_of_scope | Generic issue-tracking datasheet. | Fixed PDF. |
| 15 | https://raw.github.com/covarep/covarep/master/documentation/Covarep.pdf | Covarep A Cooperative Voice Analysis Repository fo | unrelated_repository_pdf | COVAREP | exclude_out_of_scope | Voice-analysis reimplementation discussion, not trading. | Mutable branch raw PDF. |
| 16 | https://github.com/internetarchive/heritrix3/wiki/attachments/5441/560.pdf | An Introduction to Heritrix | unrelated_repository_pdf | HERITRIX | exclude_out_of_scope | Web-crawler architecture, not trading. | Fixed wiki attachment. |
| 17 | https://github.com/user-attachments/files/18486561/202407.amd-application.en-redacted.pdf | Thomas Debesse | unrelated_attachment | AMD-APPLICATION | exclude_out_of_scope | Employment/application document, unrelated. | Fixed GitHub attachment. |
| 18 | https://github.com/SJLEE411/Sum23-SFT221-NEE-4/files/12256640/project-student-2023.v2.pdf | SFT221 – Project | unrelated_attachment | SFT221 | exclude_out_of_scope | Generic student software-testing document. | Fixed GitHub attachment. |

## S2 delta assessment

- New high-impact failure class: `none`.
- Decision reversal: `none`.
- Open critical/major contradiction: `none`.
- Stability effect: second consecutive post-freeze query with no high-impact delta.
- Important supporting failure channels:
  - full-frame/vectorized execution can leave lookahead prevention to strategy authors;
  - a detector can yield both interpretation-dependent positives and silence on other temporal errors;
  - unstructured retrieval can introduce post-decision information even when price bars are correctly sliced;
  - a mature engine’s issue tracker can contain accounting/lifecycle failures despite extensive test claims.
- Corporate-action-specific visible result: `none`. The exact S2 query did not return a corporate-action bug; this remains a bounded coverage gap and no replacement query is permitted.
- Effect on frozen decision: these results strengthen `prefix causality + complete temporal/source lineage + independent invariants`; they do not add a new architecture category beyond `R8-RS04-DLT-01/02`.

</details>

<details>
<summary>S3 complete receipt</summary>

# R8-RS04-S3 query receipt

- query_id: `R8-RS04-S3`
- exact_query: `site:reddit.com open source backtesting engine lookahead data quality maintenance`
- retrieval_start_utc: `2026-07-25T16:29:18Z`
- search_tool_calls_for_query_id: `1`
- call_shape: one `search_query` entry; `response_length=long`
- visible_result_count: `24`
- backend_truncation_observed: `false` (the tool emitted no truncation warning or continuation cursor)
- accounting_note: Result order below is the exact visible backend order. Practitioner material is used only for failure hypotheses, burden, counterexamples, and reopen triggers.

## Complete visible-result screening

| rank | url_or_fixed_locator | title | source_class | upstream_cluster_id | screening_decision | screening_reason | revision_or_supersession_state |
|---:|---|---|---|---|---|---|---|
| 1 | https://www.reddit.com/r/quantfinance/comments/1syfqzk/built_an_opensource_cli_to_automate_backtest/ | Built an open-source CLI to automate backtest setup & lookahead checks (looking for feedback on the validation logic) | practitioner_builder_report | FINNYAI-USER | include_failure_hypothesis | Builder relies on AST scanning and asks how to handle edge cases/LLM hallucinations; supports planted behavioral probes over static scanner trust. | Mutable thread published 2026-era; self-report. |
| 2 | https://www.reddit.com/r/TorontoStarts/comments/1rcikct/stop_overbuilding_your_trading_startup_an/ | Stop overbuilding your trading startup: an open-source stack that actually ships | practitioner_advice | STARTUP-STACK-USER | include_burden_support | Supports reuse for early research while identifying data quality, execution, and risk as boundaries; advice is not evidence of package correctness. | Mutable thread; broad self-authored advice. |
| 3 | https://www.reddit.com/r/Zig/comments/1jysq4g | I just open sourced a Backtesting engine written in Zig | practitioner_builder_report | ZACK-USER | include_positive_locator_only | Small bar-by-bar next-open engine is a positive package example, but it is a learning project with only a basic strategy in the visible report. | Mutable thread; self-report from 2025. |
| 4 | https://www.reddit.com/r/algotrading/comments/1t4h8ms/backtesting_in_2026/ | Backtesting in 2026 | practitioner_landscape_opinion | USER-BACKTEST-2026 | include_burden_support | Identifies data hygiene, roll handling, PIT, survivorship, maintenance, and engine/data fit as practical selection costs; not incidence evidence. | Mutable 2026 thread. |
| 5 | https://www.reddit.com/r/quant/comments/16jgnj3 | Open source backtesting engine | practitioner_discussion | USER-ENGINE-CHOICE | include_counterevidence | Contains both mature-engine reuse recommendations and build-it-yourself skepticism; preserves the real burden tradeoff rather than selecting a universal answer. | Mutable 2023 thread with later comments. |
| 6 | https://www.reddit.com/r/AlgofyTrading/comments/1tmljli/how_does_your_backtesting_framework_look_for_algo/ | How does your backtesting framework look for algo trading? Looking for best practices and stack advice. | practitioner_question | USER-STACK-QUESTION | exclude_weak | Question lists desired controls but offers no observed result or answer in the visible set. | Mutable 2026 thread. |
| 7 | https://www.reddit.com/r/algotrading/comments/1tiqq1x/any_genuinely_free_backtesting_tools/ | Any genuinely free backtesting tools? | practitioner_discussion | USER-FREE-TOOLS | include_burden_support | Discussion emphasizes identical live/backtest data shape and names different tools by task; useful for integration burden/reopen hypotheses only. | Mutable 2026 thread. |
| 8 | https://www.reddit.com/r/algotrading/comments/1sgijsr/opensourced_a_systematic_strategy_research/ | Open-sourced a systematic strategy research pipeline to reduce backtest false positives - looking for critique | practitioner_failure_report | USER-ADAPTIVE-SELECTION-LEAK | include_decisive_failure_hypothesis | User reports a validation-split leak caused by adaptive selection of what to test next rather than feature calculation; supports preregistering comparator/candidate/profile selection before oracle outputs. | Mutable 2026 thread; self-report without fixed reproduction. |
| 9 | https://www.reddit.com/r/algotrading/comments/1t1fkrk/do_you_guys_use_proprietary_quick_iteration/ | Do you guys use proprietary "quick iteration" software or an existing products? | practitioner_failure_and_workflow_report | USER-HYBRID-ENGINE | include_decisive_failure_hypothesis | Reports an accounting “magic money” error and a common hybrid workflow: off-the-shelf triage, custom semantics when fills/fees/partials matter. Directly tests the reuse boundary without proving prevalence. | Mutable 2026 thread. |
| 10 | https://www.reddit.com/r/algorithmictrading/comments/1tld7wi/backtesting/ | Backtesting | practitioner_discussion | USER-BACKTESTING-GENERAL | include_supporting | Includes same-code-path and cross-engine-disagreement concerns; useful as probe ideas, not mechanism authority. | Mutable 2026 thread. |
| 11 | https://www.reddit.com/r/IndiaAlgoTrading/comments/1u1v2ey/does_anyone_have_any_good_suggestions_for/ | Does anyone have any good suggestions for open-source trading frameworks which have Stocks/options backtesting, paper/live trading capabilities | practitioner_discussion | USER-OPTIONS-DATA | include_burden_support | Separates framework capability from the harder historical-options data pipeline; supports provider/data boundary rather than a package correctness claim. | Mutable 2026 thread. |
| 12 | https://www.reddit.com/r/algotrading/comments/1u6w3ra/removed/ | [Removed] | practitioner_counterexample_unrecoverable | USER-AI-SELF-AUDIT | include_counterexample_only | Visible replies challenge an AI-produced “no lookahead/no roll bug” conclusion and optimistic fills; removed source cannot satisfy saved-snapshot or decisive-claim requirements. | Removed/mutable thread; snippet-only. |
| 13 | https://no.reddit.com/r/ClaudeCode/comments/1t0xrad/gpt55_vs_gpt54_vs_opus_47_on_56_real_coding_tasks/ | GPT-5.5 vs GPT-5.4 vs Opus 4.7 on 56 real coding tasks from 2 open source repos:ClaudeCode | unrelated_practitioner_benchmark | CODING-MODEL-BENCH | exclude_out_of_scope | Coding-model benchmark, not backtesting. | Mutable translated Reddit route. |
| 14 | https://fr.reddit.com/r/programare/comments/1ucjotx/am_construit_%C3%AEn_5_luni_un_orchestrator_ai/?sort=top | Am construit în 5 luni un orchestrator AI open-source care rulează totul local și vreau să vi-l arăt : programare | unrelated_practitioner_project | AI-ORCHESTRATOR | exclude_out_of_scope | Generic AI orchestrator. | Mutable translated Reddit route. |
| 15 | https://ns.reddit.com/user/marcioPG/ | marcioPG (u/marcioPG) - Reddit | unrelated_user_profile | REDDIT-USER-MARCIOPG | exclude_out_of_scope | User profile with generic testing text. | Mutable user profile. |
| 16 | https://fr.reddit.com/r/Healthyhooha/comments/1cq8adc/skin_tag_removal/ | Skin tag removal? : Healthyhooha | unrelated | HEALTH | exclude_out_of_scope | Unrelated health thread. | Mutable translated Reddit route. |
| 17 | https://se.reddit.com/r/realestateinvesting/comments/1qqo1ej/the_dishwasher_premium/ | The dishwasher premium : r/realestateinvesting | unrelated | REALESTATE | exclude_out_of_scope | Unrelated real-estate data-quality discussion. | Mutable translated Reddit route. |
| 18 | https://fr.reddit.com/r/haskell/comments/1av4g1g/what_do_you_use_haskell_for/ | What do you use Haskell for? : haskell | unrelated_programming_discussion | HASKELL | exclude_out_of_scope | General language/backend discussion. | Mutable translated Reddit route. |
| 19 | https://ns.reddit.com/r/SimplyPlural/comments/1t9rasa/regarding_sp_alternatives/ | Regarding SP Alternatives : r/SimplyPlural | unrelated | SIMPLYPLURAL | exclude_out_of_scope | Unrelated app/export discussion. | Mutable Reddit route. |
| 20 | https://fr.reddit.com/r/algotrading/comments/1e40bak/to_people_currently_running_a_live_strategy_whats/ | To people currently running a live strategy - what's your next move? : algotrading | practitioner_adjacent | USER-LIVE-STRATEGY | exclude_adjacent | Longitudinal strategy/paper experience, but no fixed engine correctness or maintenance counterexample in the visible snippet. | Mutable 2024 thread. |
| 21 | https://ns.reddit.com/r/RealSolarSystem/comments/1gondpo/mechjeb_wont_autostage_stages_with_engines/ | Mechjeb won't autostage stages with engines : r/RealSolarSystem | unrelated | GAME-MECHJEB | exclude_out_of_scope | Game/rocket staging. | Mutable Reddit route. |
| 22 | https://fr.reddit.com/r/procurement/comments/1ub3uap/how_reliable_is_historical_customsbill_of_lading/?sort=old | How reliable is historical customs/Bill of Lading data for auditing a supplier's true capacity? : procurement | unrelated | PROCUREMENT | exclude_out_of_scope | Non-financial historical-data reliability. | Mutable translated Reddit route. |
| 23 | https://ns.reddit.com/r/bmwz3/comments/1k6bfqw/hey_friends_i_need_help_with_my_z3/ | Hey friends I need help with my z3 : r/bmwz3 | unrelated | AUTOMOTIVE | exclude_out_of_scope | Vehicle maintenance. | Mutable Reddit route. |
| 24 | https://fr.reddit.com/user/justinnealey | revu pour justinnealey | unrelated_user_profile | REDDIT-USER-JUSTINNEALEY | exclude_out_of_scope | User-profile snippet, not a fixed backtesting thread. | Mutable user profile. |

## S3 delta and stability assessment

- New high-impact failure class: `none`.
- Decision reversal: `none`.
- Open critical/major contradiction: `none`.
- Last-query high-impact delta: `false`.
- The adaptive-selection/holdout anecdote at rank 8 is an explicit test case under the already frozen project-wide preregistration and single-use holdout rules. Adding it as a reopen trigger is a wording/test refinement, not a new architecture category.
- The accounting error and hybrid workflow at rank 9 support the frozen boundary: use mature tools for isolated triage/oracles, but keep authority in project-specific semantics and invariants.
- Practitioner reports do not establish incidence, universal capability, or candidate correctness.
- Stability result: `pass`. After the discovery-stage high-impact delta `R8-RS04-DLT-01`, S1, S2, and S3 each yielded no new high-impact failure class, decision reversal, or open critical/major contradiction. Because S3 produced no high-impact delta, the “last stability query adds delta” failure condition did not trigger.

</details>

## Appendix B — Probe receipt exact JSON

```json
{
  "adapter": {
    "boundary": [
      "loads one hash-verified member from one hash-verified pinned tar archive",
      "does not import the ml4t package",
      "uses no third-party dependency",
      "contains no broker, credential, HTTP, socket, subprocess, or live-surface code",
      "independent Decimal accounting shares no implementation with the external oracle"
    ],
    "path": "probe/run_differential_accounting.py",
    "sha256": "91fcc6cac312d1236be8e5fd6ac5f1ec892b9ade019310f1942f95d1e0e05523"
  },
  "command": "python3 -I probe/run_differential_accounting.py",
  "comparison": [
    {
      "absolute_difference": "0.0000",
      "absolute_tolerance": "0.000000001",
      "external_value": "100.2",
      "field": "entry_fill",
      "independent_value": "100.2000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.0000",
      "absolute_tolerance": "0.000000001",
      "external_value": "109.78",
      "field": "exit_fill",
      "independent_value": "109.7800",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000000002",
      "absolute_tolerance": "0.000000001",
      "external_value": "95.79999999999998",
      "field": "gross_pnl",
      "independent_value": "95.80000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000",
      "absolute_tolerance": "0.000000001",
      "external_value": "2.0998",
      "field": "fees",
      "independent_value": "2.09980000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000000002",
      "absolute_tolerance": "0.000000001",
      "external_value": "93.70019999999998",
      "field": "net_pnl",
      "independent_value": "93.70020000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000000000001051896207585",
      "absolute_tolerance": "0.000000001",
      "external_value": "0.09560878243512973",
      "field": "pnl_percent",
      "independent_value": "0.09560878243512974051896207585",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000000000001077844311377",
      "absolute_tolerance": "0.000000001",
      "external_value": "0.0935131736526946",
      "field": "net_return",
      "independent_value": "0.09351317365269461077844311377",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.0000000000000284",
      "absolute_tolerance": "0.000000001",
      "external_value": "2.0000000000000284",
      "field": "entry_slippage_cost",
      "independent_value": "2.00000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.0000000000000114",
      "absolute_tolerance": "0.000000001",
      "external_value": "2.1999999999999886",
      "field": "exit_slippage_cost",
      "independent_value": "2.20000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000000002",
      "absolute_tolerance": "0.000000001",
      "external_value": "93.70019999999998",
      "field": "total_pnl",
      "independent_value": "93.70020000",
      "within_tolerance": true
    },
    {
      "absolute_difference": "0.00000000",
      "absolute_tolerance": "0.000000001",
      "external_value": "100093.7002",
      "field": "final_cash",
      "independent_value": "100093.70020000",
      "within_tolerance": true
    }
  ],
  "component": {
    "archive_path": "snapshots/ML4T_BACKTEST_459abd81f2f30dc70cf38a40da7591af3da2d02a_tests_architecture.tar",
    "archive_sha256": "71639a2719b276ee13306f05482e51144d8724ab04870269017405a913e4e274",
    "commit": "459abd81f2f30dc70cf38a40da7591af3da2d02a",
    "member": "ml4t-backtest-459abd81f2f30dc70cf38a40da7591af3da2d02a/tests/oracle/engine.py",
    "member_sha256": "3a663f95d233956185c7d83822d042ad790a2846380f09dc8d89456c8c7d950d",
    "name": "ml4t-backtest reference oracle",
    "repository": "https://github.com/ml4t/backtest"
  },
  "executed_utc": "2026-07-25T16:40:34.246724Z",
  "external_observation": {
    "entry_fill": 100.2,
    "entry_slippage_cost": 2.0000000000000284,
    "exit_fill": 109.78,
    "exit_slippage_cost": 2.1999999999999886,
    "fees": 2.0998,
    "final_cash": 100093.7002,
    "gross_pnl": 95.79999999999998,
    "net_pnl": 93.70019999999998,
    "net_return": 0.0935131736526946,
    "pnl_percent": 0.09560878243512973,
    "total_pnl": 93.70019999999998
  },
  "fixed_input": {
    "case_id": "R8-RS04-fixed-long-same-bar-cost-accounting",
    "path": "probe/FIXED_INPUT.json",
    "semantics": {
      "absolute_tolerance": 1e-09,
      "commission": "fill_price multiplied by quantity multiplied by commission_rate, charged on entry and exit",
      "entry_fill": "signal bar close multiplied by (1 + slippage_rate)",
      "exit_fill": "signal bar close multiplied by (1 - slippage_rate)",
      "fill_timing": "SAME_BAR",
      "final_cash": "initial_cash + net_pnl",
      "gross_pnl": "(exit_fill - entry_fill) multiplied by quantity",
      "net_pnl": "gross_pnl - entry_commission - exit_commission",
      "position": "one long round trip"
    },
    "sha256": "ff1fbcf608f23e450d09fde9ad54bb7bf0eb9195022ef74da1027649c48d782b"
  },
  "independent_observation": {
    "entry_fill": "100.2000",
    "entry_slippage_cost": "2.00000",
    "exit_fill": "109.7800",
    "exit_slippage_cost": "2.20000",
    "fees": "2.09980000",
    "final_cash": "100093.70020000",
    "gross_pnl": "95.80000",
    "net_pnl": "93.70020000",
    "net_return": "0.09351317365269461077844311377",
    "pnl_percent": "0.09560878243512974051896207585",
    "total_pnl": "93.70020000"
  },
  "limitations": [
    "One synthetic long round trip is not coverage of shorts, partial fills, corporate actions, event ordering, or prefix causality.",
    "Agreement cannot establish correctness because both implementations may share the same semantic assumption.",
    "The external observation executes only the repository's reference oracle, not the package system under test.",
    "No live surface, broker, credential, network call, or dependency installation was used."
  ],
  "outcome": {
    "all_fields_within_declared_tolerance": true,
    "causality_claimed": false,
    "classification": "agreement_within_tolerance",
    "routing": "review_only",
    "winner_selected": false
  },
  "probe_id": "R8-RS04-P1",
  "runtime": {
    "implementation": "CPython",
    "isolated_mode": true,
    "python": "3.14.0"
  },
  "schema_version": 1
}
```
