# RS-04 独立逐-claim entailment review

## 1. 审查身份、输入与独立性边界

- `topic_id`: `RS-04`
- `round_id`: `RESEARCH-REFRESH-R8`
- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_mode`: `platform_observable_separate_thread_review`
- `review_input`: `audits/research_r8/RS-04_RAW_REPORT.md`
- `expected_review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `review_input_integrity`: `pass_exact_match`
- `network_or_new_search`: `not_performed`
- `live_surface_or_connector_access`: `not_performed`
- `offline_probe_reexecution`: `not_performed`
- `author_report_or_claims_modified`: `no`
- `other_evidence_governance_or_code_modified`: `no`

本审查只读取本地保存的报告、R8 预注册文件、manifest、固定 snapshot bytes、discovery freeze 与离线 probe artifacts。搜索摘要和作者的 `author_entailment` 只用于理解被审查对象，不作为独立 source-to-claim 证明。

本审查仅是 **platform-observable separate-thread review**：平台可观察到上述 reviewer locator 与作者线程分离，并可观察到本审查绑定的 raw-report SHA-256。它不证明组织隔离、安全隔离、操作系统或进程隔离、不同模型/训练数据/工具链、抗串通性或密码学 reviewer identity。locator 与内容 hash 不能消除同源模型和共同盲点。

## 2. Fail-closed 闸门与预注册 verdict 边界

| 检查 | 预期值 | 只读重算值 | 结果 |
|---|---|---|---|
| `RS-04_RAW_REPORT.md` SHA-256 | `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c` | `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c` | `match`; fail-closed 未触发 |
| R8 preregistration SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | `match` |
| discovery freeze SHA-256 | `8231d40bfc47c618ead5d272ed5283f46d906c5b1a283a3911ab4e241205bec4` | `8231d40bfc47c618ead5d272ed5283f46d906c5b1a283a3911ab4e241205bec4` | `match` |

R8 preregistration 要求每条 independent review record 均含：

- `reviewer_locator`
- `review_input_sha256`
- `claim_id`
- `verdict`
- `reason`
- `checked_source_ranges`
- `overclaim_or_missing_counterevidence`

可用于 design closure 的逐 claim verdict 只有：

- `entailed`
- `contested_non_decision_changing`

预注册同时规定 `author_only_closure = false` 与 `reviewer_must_not_write_claims_under_review = true`。因此，本 reviewer 可以指出缺失的 decisive claim，却不能替作者补写该 claim；缺失 claim 没有 independent verdict，必须阻塞 closure。

## 3. Snapshot 与 probe byte integrity

下列 SHA-256 与 byte count 均由本 reviewer 对实际保存 bytes 只读重算，并与 manifest 或 raw report 对照：

| artifact | byte count | SHA-256 | 对照 |
|---|---:|---|---|
| `snapshots/MANIFEST.json` | `10935` | `8073cb65dd8bb6f98b3bb3a87875335c29a8b204a16941c648c30d17a6b96f01` | 与 raw report `match` |
| `R8-RS04-SNAP-FINRLX` tar | `245760` | `1d950a3563d189bb75b423f3000c5e0df0faa1a876d7525049b2750dc42391fd` | 与 manifest `match` |
| `R8-RS04-SNAP-ML4T` tar | `798720` | `71639a2719b276ee13306f05482e51144d8724ab04870269017405a913e4e274` | 与 manifest `match` |
| `R8-RS04-SNAP-AITRADER-76` | `7235` | `3ec5e5e1609e113029cbf5860d5c3f26f46999f793f5a3d2d3646ced9ff14eaf` | 与 manifest `match` |
| `R8-RS04-SNAP-NAUTILUS-4564` | `8175` | `075db22c33e20b6762d13954ac0045650cc53d6f2741927ce042a0318c2633cb` | 与 manifest `match` |
| `R8-RS04-SNAP-NAUTILUS-4470` | `7346` | `34fa610ba8a0f6244fbacdecfe869d6ba29c1257019786530fab1b540c494e10` | 与 manifest `match` |
| `probe/FIXED_INPUT.json` | — | `ff1fbcf608f23e450d09fde9ad54bb7bf0eb9195022ef74da1027649c48d782b` | 与 raw report/receipt `match` |
| `probe/run_differential_accounting.py` | — | `91fcc6cac312d1236be8e5fd6ac5f1ec892b9ade019310f1942f95d1e0e05523` | 与 raw report/receipt `match` |
| `probe/R8-RS04-P1_RECEIPT.json` | `6466` | `da337f9a4af2071ea112b4ea389a0109a3e7b5dfd880f69e499c489afb99cdd1` | 与 raw report `match` |

ML4T tar 内被 probe 执行的 `tests/oracle/engine.py` member SHA-256 只读重算为 `3a663f95d233956185c7d83822d042ad790a2846380f09dc8d89456c8c7d950d`，与 fixed input 和 receipt 一致。

## 4. Decisive claim set 与 inventory 完整性

Raw report 列出的 final atomic claims 是：

- `R8-RS04-C01`
- `R8-RS04-C02`
- `R8-RS04-C03`
- `R8-RS04-C04`
- `R8-RS04-C05`

但 R8 preregistration 的 RS-04 `r7_decisions_under_review` 明确包含四个复用边界：`ExternalResearchAdapter`、`ExternalComponentManifest`、`DifferentialOracle` 与 `LedgerProjection`。现有 claim/delta 映射如下：

| preregistered subject | raw-report coverage | inventory verdict |
|---|---|---|
| 不以被审查整包替换权威核心 | `C01`, `C03`, `DLT-03` | covered |
| `DifferentialOracle` | `C02`, `DLT-01` | covered |
| `ExternalResearchAdapter` | `C04` | covered，但 input/live/LLM reachability gate 仍不够显式 |
| `ExternalComponentManifest` | `C05`, `DLT-02` | covered，但 LLM/network/transitive mutable-state 字段仍不够显式 |
| `LedgerProjection` | 仅在 raw report 第 `17` 行继承性点名；无 atomic claim、source ranges、counterevidence 或 executable mapping | **missing decisive subject; closure blocker** |
| 不引入 live connector、LLM authority 或 external mutable ledger | 分散出现在 authority boundary、`C01/C04/C05` 与 `DLT-02` 的宽泛禁止语句中 | **没有形成完整、可测试的显式 claim/gate 集合** |

因此，本 review 可以完整裁决作者实际提交的 `C01–C05`，但不能把“现有五条均获允许 verdict”改写为“预注册 decisive claim inventory 完整”。

## 5. 逐 claim verdict 摘要

| claim_id | verdict | design effect |
|---|---|---|
| `R8-RS04-C01` | `entailed` | 固定 revision 不得按现状替换 Paper V1 authoritative core；未来 adapter admission 仍可 defer |
| `R8-RS04-C02` | `contested_non_decision_changing` | review-only/no-winner/no-causality-certificate 边界成立；本轮只观察到 agreement，未观察 divergence |
| `R8-RS04-C03` | `contested_non_decision_changing` | 正面 bytes 推翻 blanket package rejection；whole-package isolation/admission 与净维护收益仍未证明 |
| `R8-RS04-C04` | `contested_non_decision_changing` | target weights 可作 candidate output；独立 mandatory lineage 是项目设计综合，不是该接口 bytes 的唯一直接结论 |
| `R8-RS04-C05` | `entailed` | 固定 issue reports 足以否定“成熟度自动消除 failure surface”；只作 counterexample/gate，不作发生率或 root-cause 证明 |

`C01–C05` 的 verdict 均位于预注册允许集合内。Topic closure 仍被 Section 4 的 claim-inventory 缺口阻塞。

## 6. 完整逐 claim 审查记录

### `R8-RS04-C01`

- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `claim_id`: `R8-RS04-C01`
- `verdict`: `entailed`
- `reason`: 固定 FinRL-X bytes 直接显示 weight-centric interface、backtest layer、walk-forward helper 与 Alpaca paper/live surface。`trade_executor.py` 同时把 risk check 设为 configurable，在 order submission 后才写本地 JSON log，并在 price retrieval 失败时返回默认价格 `100.0`。`requirements.txt` 还包含 `yfinance`、`requests`、`alpaca-py` 与 `openai`。这些 observed surfaces 与预注册的“外部组件不得进入 risk gate、execution 或 authoritative ledger write path”不兼容；在没有隔离 adapter、完整 lineage 与 admission evidence 时，固定 revision 不能按现状替换 Paper V1 authoritative core。该结论只针对当前保存 evidence、固定 revision 与 Paper V1 authority boundary。
- `checked_source_ranges`:
  - `R8-RS04-SNAP-FINRLX`, SHA-256 `1d950a3563d189bb75b423f3000c5e0df0faa1a876d7525049b2750dc42391fd`, `README.md:38-44,117,208,263`。
  - 同一 snapshot，`src/trading/trade_executor.py:39-48,131-146,280-316,318-351,394-426`。
  - 同一 snapshot，`src/backtest/backtest_engine.py:124-242,290-341`。
  - 同一 snapshot，`src/strategies/adaptive_rotation/walk_forward.py:182-367,451-475`。
  - 同一 snapshot，`requirements.txt:17-24,30-48` 与 `LICENSE` entire file。
  - R8 preregistration JSON，RS-04 `r7_decisions_under_review`。
- `overclaim_or_missing_counterevidence`: Selected tar 是 decisive blobs archive，不是 full-repository archive，因此它不能独立证明整个 fixed tree 没有 tests，也不能支持对 FinRL-X 普遍质量的否定。`cannot replace` 必须解释为“当前 evidence 下不得 as-is 获得 authoritative-core admission”，而不是“该项目永远不能被隔离、修改或复用”。Raw report 已实质保留这一限制；未发现会改变 rejection/defer decision 的遗漏反证。

### `R8-RS04-C02`

- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `claim_id`: `R8-RS04-C02`
- `verdict`: `contested_non_decision_changing`
- `reason`: 保存的 differential test code 确实按字段比较 SUT 与 reference oracle；离线 receipt 绑定 fixed input、archive/member hashes、named semantics、逐字段 tolerance，并明确记录 `causality_claimed=false`、`routing=review_only` 与 `winner_selected=false`。Receipt limitations 直接说明 agreement 不能建立 correctness，且不覆盖 prefix causality。争议是本轮固定 probe 的唯一 observation 为 `agreement_within_tolerance`，没有实际观察到 implementation/semantic divergence；raw report 所依赖的两项 D2 preprint 没有保存 PDF exact bytes，不能在本审查中承担独立 entailment。因而“可构造能暴露 mismatch 的 comparison instrument”成立，“本轮 probe 已暴露 risk”不成立。这个收窄不改变 DifferentialOracle 只能 review-only、不能旁路 causality/lineage gate 的决定。
- `checked_source_ranges`:
  - `R8-RS04-SNAP-ML4T`, SHA-256 `71639a2719b276ee13306f05482e51144d8724ab04870269017405a913e4e274`, `tests/test_oracle_differential.py:1-134`。
  - 同一 snapshot，作者声明范围 `tests/oracle/engine.py:1-220`；为核对输出计算完整性，另检查 `221-270`。
  - 同一 snapshot，`validation/METHODOLOGY.md:1-90,229-309`。
  - `probe/R8-RS04-P1_RECEIPT.json`, SHA-256 `da337f9a4af2071ea112b4ea389a0109a3e7b5dfd880f69e499c489afb99cdd1`, JSON fields `comparison`, `component`, `fixed_input`, `limitations`, `outcome`, `runtime`。
  - `probe/run_differential_accounting.py`, SHA-256 `91fcc6cac312d1236be8e5fd6ac5f1ec892b9ade019310f1942f95d1e0e05523`, lines `46-79`, `82-155`, `158-243`，只作 receipt/boundary 静态交叉核对。
- `overclaim_or_missing_counterevidence`: D2 preprint exact bytes 缺失是明确的 evidence gap。另有 source-range 精度问题：`tests/oracle/engine.py:1-220` 漏掉实际 PnL/result construction 的 `221-270`；`validation/METHODOLOGY.md:229 onward as applicable` 不是精确终点。ML4T methodology 自身在 `72-76` 把多 engine convergence 推到 correctness，正好说明 maintainer confidence 不能替代本项目的 same-bug negative control。以上都是 non-decision-changing contestation：应修正 range 与措辞，但保留 review-only/no-winner/no-causality-certificate contract。

### `R8-RS04-C03`

- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `claim_id`: `R8-RS04-C03`
- `verdict`: `contested_non_decision_changing`
- `reason`: 固定 ML4T bytes 确实包含 named execution semantics、explicit limitations、differential tests、cross-engine contract test 与 dependency lock；这足以推翻“packaged open-source engine 只能提供营销描述”以及“原子复用必然等于复制函数”的 blanket proposition。争议在于 snapshot 是 selected decisive blobs，不是完整 package archive；cross-engine contract 依赖 optional comparison dependencies，并在环境变量未设置时 skip；本轮 probe 只执行一个 in-tree reference-oracle member，不是 package SUT，也不是 whole-package subprocess admission trial。因此，bytes 支持“whole package 可以进入候选评估”，不支持“whole package 已证明可隔离、可接入或有净维护收益”。Raw claim 的 `defer to pinned admission test` 与 `no authority transfer` 使该争议不改变决定。
- `checked_source_ranges`:
  - `R8-RS04-SNAP-ML4T`, SHA-256 `71639a2719b276ee13306f05482e51144d8724ab04870269017405a913e4e274`, `README.md:21,262-347`。
  - 同一 snapshot，`LIMITATIONS.md:1-210`。
  - 同一 snapshot，`tests/contracts/test_cross_engine_contracts.py:1-114`。
  - 同一 snapshot，`uv.lock` entire member；仅验证固定 dependency lock 存在，不把 lock 存在解释为依赖安全或可维护性通过。
  - `R8-RS04-SNAP-FINRLX` 的 declared selected architecture ranges。
  - `probe/R8-RS04-P1_RECEIPT.json:component,limitations,outcome`。
- `overclaim_or_missing_counterevidence`: 没有 whole-package execution receipt、adapter reachability negative test、dependency installation receipt、package SUT differential result或 net-maintenance evidence。`tests/contracts/test_cross_engine_contracts.py:100-114` 还显示这些 integration tests 可能因缺 dependency 或缺 `ML4T_COMPARISON_INPROC=1` 而 skip。应把 claim 固定为 “eligible for quarantined admission evaluation”，不得写成已 admitted；该收窄不反转反对 blanket rejection 的决定。

### `R8-RS04-C04`

- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `claim_id`: `R8-RS04-C04`
- `verdict`: `contested_non_decision_changing`
- `reason`: 固定 bytes 直接证明 target-weight 是 strategy 与 downstream execution 之间的接口；`StrategyResult` 只要求 `strategy_name`、`weights` 与 optional unconstrained `metadata`，而 trade executor 将 weights 转为 orders、可选执行 risk check、下单后再记录 JSON。它没有定义 Paper V1 所需的 source、decision-time、human-decision、gate-decision 与 requested→actual execution lineage。由此可以支持“weights 只能作为 candidate output，不能单独获得 authority”。争议是“这些 lineage 必须作为独立 mandatory records”属于结合 Paper V1 invariant 的保守设计综合；source bytes 没有证明 optional `metadata` 绝不可能承载其中部分字段，也没有证明独立记录是唯一实现方式。该争议不改变 candidate-only 与 no-authority decision。
- `checked_source_ranges`:
  - `R8-RS04-SNAP-FINRLX`, SHA-256 `1d950a3563d189bb75b423f3000c5e0df0faa1a876d7525049b2750dc42391fd`, `README.md:38-44`。
  - 同一 snapshot，`src/strategies/base_strategy.py:1-27`。
  - 同一 snapshot，`src/trading/trade_executor.py:131-146,394-426`。
  - R8 preregistration JSON，RS-04 authority/lineage decisions under review。
- `overclaim_or_missing_counterevidence`: Manifest 的 `selected_blob_ids` 包含 `src/strategies/base_strategy.py`，但 `source_range_used` 没有列出该文件；raw claim 又只写文件名、没有精确行范围。这是 traceability defect，但 bytes 已固定且文件只有被检查的 `1-27`。下游应把 mandatory lineage 明确标为 project contract，并补齐 manifest range；不得声称 FinRL-X bytes 自身证明了唯一记录拓扑。

### `R8-RS04-C05`

- `reviewer_locator`: `codex_subagent:019f9a32-3cdf-7d22-be0c-53baf28394fa`
- `review_input_sha256`: `f44ee87f2036dc5baae16792e65f6f617858cf5cfd11cd15050a9f2c228f822c`
- `claim_id`: `R8-RS04-C05`
- `verdict`: `entailed`
- `reason`: 三个 exact issue responses 分别保存了 post-decision retrieval、strategy-scope/instrument-scope mismatch 与 connectivity-loss/order-incarnation/reconciliation failure 的具体 user reports；FinRL-X fixed code 同时保存 configurable risk check、live Alpaca call、default-price fallback 与 order-before-log surface。它们足以否定“maintainer architecture/test/maturity claim 自动消除独立 failure counterexample”的推断，并支持 manifest 显式记录 optional bypass、observed default、live-surface reachability 与 requested→actual lineage。Claim 已把 issue bytes 限制为 counterexample 而非 incidence 或 maintainer-confirmed root cause，因此没有越过保存证据。
- `checked_source_ranges`:
  - `R8-RS04-SNAP-AITRADER-76`, SHA-256 `3ec5e5e1609e113029cbf5860d5c3f26f46999f793f5a3d2d3646ced9ff14eaf`, JSON fields `number,state,title,created_at,updated_at,closed_at,author_association,comments,body`。
  - `R8-RS04-SNAP-NAUTILUS-4564`, SHA-256 `075db22c33e20b6762d13954ac0045650cc53d6f2741927ce042a0318c2633cb`, JSON fields `number,state,title,created_at,updated_at,closed_at,author_association,comments,body`。
  - `R8-RS04-SNAP-NAUTILUS-4470`, SHA-256 `34fa610ba8a0f6244fbacdecfe869d6ba29c1257019786530fab1b540c494e10`, JSON fields `number,state,title,created_at,updated_at,closed_at,author_association,comments,body`。
  - `R8-RS04-SNAP-FINRLX`, `src/trading/trade_executor.py:39-48,131-146,280-316,318-351,394-426`。
- `overclaim_or_missing_counterevidence`: Separate comments endpoints 未保存；AI-Trader `closed` 不证明 fix，Nautilus `open` 不证明 maintainer confirmation、current exploitability 或 root cause。Issue bodies 是 reporter-authored evidence；本 reviewer 没有复现 live incident。Raw claim 已保留这些限制。还应补充：manifest 中的 `actual default` 和 `reachability` 必须由 observed/static+runtime evidence 支持，不能只复制 issue 或 README 文本。

## 7. 重点边界挑战

| boundary | reviewer finding |
|---|---|
| 不替换整套系统 | `C01` 支持 fixed revision 不得 as-is 替换 authoritative core；`C03` 只开放 quarantined admission evaluation，不转移 decision、risk、execution 或 ledger authority。 |
| `ExternalResearchAdapter` | Candidate-only output 边界成立；但 raw report 没有把“input 只能是 hash-verified fixed snapshot”“禁止 network/live connector/LLM invocation 获得 authority”“禁止任何 ledger write”全部落为显式 schema 与 negative reachability tests。 |
| `ExternalComponentManifest` | tracked tests、observed defaults、optional bypass、live/broker/credential reachability 与 revision freshness 已提出；但 exact FinRL-X requirements 含 `openai`、`yfinance`、`requests` 与 `alpaca-py`，所以 manifest 还必须显式枚举 direct/transitive network、LLM、mutable state/store 与 write side effects，不能把它们隐藏在宽泛的 “live surface” 或 “any authority” 中。 |
| `DifferentialOracle` | 本轮 probe 的 `review_only` 界定正确：fixed hashes、named semantics、per-field tolerance、`causality_claimed=false`、`winner_selected=false`。Static adapter bytes 未导入 broker/network/subprocess/LLM package，只读取 hash-verified local tar member并输出 receipt。该结论只覆盖此 probe，不是 package SUT、whole-package isolation 或 runtime sandbox attestation。 |
| `LedgerProjection` | **未被审查对象化。** Raw report 没有 atomic claim、source ranges、counterevidence、one-way/read-only/rebuildable contract、reverse-write rejection 或 executable test/gate。Reviewer 不能替作者补写，因此 closure 必须阻塞。 |
| no live connector / no LLM authority / no external mutable ledger | 当前离线 probe 没有这些能力；未来 architecture 只有宽泛禁止，没有完整可执行 proof obligation。尤其 `LedgerProjection` 缺失使“外部 mutable ledger 永不反向覆盖 authoritative event chain”没有 R8 claim-level 证据。 |

## 8. 反证遗漏与 source-range 缺口

### Closure-changing omissions

- `LedgerProjection` 是 preregistered subject，却没有 author claim 或 executable mapping；这是 claim-inventory blocker。
- LLM invocation、network/data connector 与 external mutable state/store 只被宽泛包含在 authority/live 禁止中，没有独立 manifest fields、adapter reachability negative tests 与 ledger reverse-write rejection；这使 no-authority boundary 不能被确定性验证。

### Non-decision-changing limitations

- `C02` 引用的两项 D2 preprint 没有保存 PDF exact bytes；本 review 不据此确认其 empirical result。
- 本轮 differential probe 只有一个 synthetic long SAME_BAR case且结果为 agreement；不覆盖 short、partial fill、corporate action、event ordering、prefix causality 或 package SUT。
- ML4T 的 validation 数字与 correctness 语言是 maintainer claims；没有本轮 observed full test receipt，cross-engine contract 可因 dependency/env 条件而 skip。
- FinRL-X tar 只保存 selected decisive blobs，不能证明 full tree 中不存在 tests。
- 三个 issue 的 comments endpoints 未保存，不能裁决 maintainer response、fix、root cause 或 incidence。
- S2 没有 corporate-action-specific issue；该 bounded coverage gap 仍应保留。
- `C02/C04` 存在不精确或未进入 manifest 的 source range，需在 author revision 中修正。

## 9. 总 verdict

- `listed_claims_C01_through_C05`: `all_allowed_for_design_closure`
- `decisive_claim_inventory_complete`: `false`
- `independent_claim_entailment_predicate`: `blocked_incomplete_claim_inventory`
- `offline_differential_probe_boundary`: `correctly_scoped_as_review_only`
- `current_RS-04_topic_status_recommendation`: `bounded_incomplete`
- `automatic_authority_transfer`: `forbidden`

现有 `C01–C05` 没有 `not_entailed` 或 `decision_changing_contestation`；三个 contestation 都只收窄证据强度，并保留更保守的 decision effect。但预注册的 `LedgerProjection` subject 没有 claim 可供 review，且 no-LLM/no-external-mutable-ledger 仍缺可执行 mapping，所以 raw report 第 `412` 行“唯一 false predicate 是 independent review”不能成立。本文件不能单独把 predicate `5` 从 `false` 改成 `true`。

本 verdict 只裁决 RS-04 design-research evidence 的逐 claim 蕴含与覆盖边界。它不证明 implementation、adapter sandbox、package admission、machine provenance、post-candidate semantic review、Javen 最终决定或 final release 已完成。

## 10. Topic closure predicate 更新建议

| preregistered predicate | 建议状态 | 本 reviewer 的依据与剩余 blocker |
|---|---|---|
| 预注册 commit、文件 hash、祖先关系和检索时间通过 | `partial_pass_pending_final_integration_commit` | Raw report、preregistration 与 discovery freeze hashes 已只读重算匹配；包含本 review 的 final integration commit 尚未存在，后续必须重跑 ancestor check，不能预写为 pass。 |
| 五个 query_id 均有且仅有一次执行或明确工具失败 receipt | 保持作者 `pass`，本 review 不重开 | 本 reviewer 没有联网、新搜索或重放 search accounting。 |
| 全部可见结果有逐结果筛选记录且归属唯一 query_id | 保持作者 `pass`，本 review 不重开 | 本轮只审查保存 bytes 与 claim entailment，不把 snapshot review 冒充 query-completeness 重验。 |
| required snapshot classes 均有保存字节与哈希 | `pass` | Manifest-declared tar/issue bytes 的 byte count 与 SHA-256 全部重算匹配；probe hashes 也匹配。 |
| 每个决定性 claim 通过独立逐 claim蕴含复核 | **保持 `false` / blocked** | 作者列出的 `C01–C05` 已完成 allowed-verdict review，但 preregistered `LedgerProjection` decisive subject 没有 author claim，inventory 不完整。 |
| 矛盾与反证已保留且有决定影响 | `partial` | Package positive evidence、agreement、issue counterexamples 与 bounded gaps 已保留；LedgerProjection/no-LLM/no-mutable-ledger 分支尚无 claim-level counterevidence record。 |
| 稳定性 passing rule 满足 | `conditional` | 若 remediation 仅把已冻结 R7 authority boundary显式化，且不形成新 high-impact architecture/decision delta，可保留原 stability pass并说明理由；若新增 high-impact delta，则 S3 之后没有 later reserved query，按固定预算必须保持 `bounded_incomplete`，并在新预注册 round 重开。 |
| architecture / decision delta 落到 executable contract、test、gate、defer 或 rejection | **`false` / blocked** | `DifferentialOracle` 与 `ExternalComponentManifest` 有 mapping；`ExternalResearchAdapter` mapping 不完整；`LedgerProjection` 没有 mapping；LLM/network/mutable-store reachability 也没有显式 negative gate。 |
| 残余风险和重开触发器明确 | `partial` | 原 residual gaps 仍有效；还需加入 transitive dependency 新增 network/LLM capability、adapter output 获得 authority、projection 出现 reverse ingestion/write、external mutable store 与 authoritative ledger 分歧等触发器。 |

## 11. 解除 blocker 所需的作者侧工作

由于 `reviewer_must_not_write_claims_under_review = true`，以下工作必须由作者或后续构造者完成，而不是由本 reviewer 代写：

- 为 `LedgerProjection` 增加 atomic claim、exact source ranges、limitations、counterevidence 与 decision effect，并明确 one-way downstream/read-only、可从 authoritative ledger 重建、禁止 reverse overwrite。
- 把 `ExternalResearchAdapter` 的 fixed-snapshot-only input、candidate-only output、no network/live connector、no LLM authority、no execution 与 no ledger write 变成可执行 contract 和 negative reachability tests。
- 把 `ExternalComponentManifest` 扩展为显式枚举 direct/transitive network、broker、credential、LLM、mutable state/store 与 write side effects，并区分 declared、statically reachable、runtime observed 与 blocked。
- 修正 `C02` 的 exact source ranges，并在需要保留 preprint empirical wording时保存其 exact bytes；否则把 claim 收窄到本地保存 test/probe 实际支持的范围。
- 把 `src/strategies/base_strategy.py:1-27` 补入 FINRL-X manifest 的 `source_range_used`。
- 由另一个与作者分离的 reviewer 对修订后的新增/变更 claims 重新做 per-claim review；本文件不得被当作尚未存在的 claim verdict。
- 若上述修订构成新的 high-impact architecture/decision delta，则不要在 R8 固定预算内伪装 stability；应保持 `bounded_incomplete` 并进入新的预注册 round。
