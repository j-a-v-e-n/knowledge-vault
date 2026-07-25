# RS-01 独立逐-claim entailment review

## 1. 审查身份、范围与独立性边界

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input`: `audits/research_r8/RS-01_RAW_REPORT.md`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- 审查对象：`RS01-CL-01` 至 `RS01-CL-06`，以及这些 claim 对 `RS01-DD-01` 至 `RS01-DD-04` 的支持边界。
- 证据边界：只读取本地保存的原始 snapshot bytes、`manifest.json`、R8 预注册文件和原始报告；没有联网，没有执行新搜索，也没有把搜索摘要或作者的 `author_entailment` 当作独立证据。
- 写入边界：本 reviewer 没有修改被审查 claims、`RS-01_RAW_REPORT.md`、`research/evidence`、governance、代码或其他文件。

本审查是 **platform-observable separate-thread review**：平台可观察到本 reviewer locator 与作者线程分离，并可观察到本审查绑定的输入 SHA-256。它**不是**组织隔离、安全隔离、操作系统或进程隔离、不同模型/训练数据/工具链保证，也不是密码学独立性保证。线程 locator 与内容 hash 只能证明可观察的线程分离和字节绑定，不能证明 reviewer 与作者不存在共同盲点。

## 2. Fail-closed 输入闸门与预注册合同

### 2.1 输入 hash

| 检查 | 预期值 | 只读重算值 | verdict |
|---|---|---|---|
| `RS-01_RAW_REPORT.md` SHA-256 | `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee` | `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee` | `match`; fail-closed 未触发 |

补充只读检查：

- 当前 R8 预注册文件 SHA-256：`613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`。
- commit `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` 内同一路径预注册字节 SHA-256：`613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`。
- 当前 raw report 与 commit `3a0a44285b960d172e240a87567ce62dd90a0cb1` 内 raw report 的 SHA-256 都是 `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`。
- `merge-base(7824a63afe923d5e38c0c6f06577a7d1adfb81d5, 3a0a44285b960d172e240a87567ce62dd90a0cb1)` 为 `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`。

### 2.2 `claim_protocol` 核对

预注册的 `independent_review_required_fields` 是：

- `reviewer_locator`
- `review_input_sha256`
- `claim_id`
- `verdict`
- `reason`
- `checked_source_ranges`
- `overclaim_or_missing_counterevidence`

预注册的 `allowed_independent_verdicts_for_design_closure` 只有：

- `entailed`
- `contested_non_decision_changing`

预注册同时规定：

- `author_only_closure = false`
- `reviewer_must_not_write_claims_under_review = true`

`not_entailed` 与 `decision_changing_contestation` 不在上述 design-closure 允许集合内；按本轮任务指令，若证据不成立或争议会改变决定，则必须使用其中相应失败 verdict，并阻塞 closure。本审查没有把失败 verdict 改写成 closure 允许值。

## 3. Snapshot byte integrity

下列 SHA-256 与 byte count 均由本 reviewer 对实际保存文件只读重算，并与 `research/evidence/r8/RS-01/manifest.json` 对照：

| source id | byte count | SHA-256 | manifest 对照 |
|---|---:|---|---|
| `RS01-SRC-01` | `382125` | `728bbac9ad5dae544d1a0549e0fe3f3812e00ad0f4e8c69a0dda2916f0efd26b` | `match` |
| `RS01-SRC-02` | `901478` | `f9123e33da838b45f9aef4787720fb7f58ac3f0535ed39cf77fcb96767c73406` | `match` |
| `RS01-SRC-03` | `73645` | `6aa2f048c23bc62663c14cf11bf13143d07e60e442055cf3282590fbd6850aa0` | `match` |
| `RS01-SRC-04` | `2019220` | `3b6a3b8032dcaea9187e5aea88854268c3cf3782ab83e968ea93e0e8b2129446` | `match` |
| `RS01-SRC-05` | `488268` | `90f65ea8fae259321341042124f2446f7deaa697953cb79eb3818a2fdb91c390` | `match` |
| `RS01-SRC-06` | `1545` | `4d4f907c245a1dd924f890beaef04c8f4efe726f3724247af2db105a95ff5841` | `match` |
| `RS01-SRC-06-CONTEXT` | `491` | `f2882f6570e93190e76e3d878e5729c714f15b1690aee139b9d0eb0240b0c6a4` | `match` |

控制文件只读重算：

- `manifest.json`: `12025` bytes；SHA-256 `2ef7bd6357f037b4fdf1b37b75684b479e624775f3427d34052cc633d19f19e6`。
- `RS01_RETRIEVAL_FAILURE_RECEIPTS.md`: `1574` bytes；SHA-256 `277fa48ee37f2ed31e1c8b42be7af2b4a6480834aae3c3381e0a425374278a31`。

## 4. 逐 claim verdict 摘要

| claim_id | verdict | 对 design decision 的影响 |
|---|---|---|
| `RS01-CL-01` | `entailed` | 支持 `RS01-DD-01` 的非穷尽、记录理由、残余风险和资源约束方向 |
| `RS01-CL-02` | `entailed` | 支持 `RS01-DD-01` 纳入 decision utility、错误后果和检索成本 |
| `RS01-CL-03` | `entailed` | 支持 `RS01-DD-04` 把 screening false exclusion 作为独立风险通道 |
| `RS01-CL-04` | `contested_non_decision_changing` | 保留 `RS01-DD-02`，但必须把完整五分法标成治理设计综合，而不是 `RS01-SRC-04` 的直接实证结论 |
| `RS01-CL-05` | `entailed` | 支持 `RS01-DD-03` 拒绝单一 ground truth 或单轴 closure oracle |
| `RS01-CL-06` | `entailed` | 只支持 verification-debt probe/reopen trigger，不支持发生率或产品排序 |

## 5. 完整逐 claim 审查记录

### `RS01-CL-01`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-01`
- `verdict`: `entailed`
- `reason`: 指定章节把检索描述为在资源限制内尽量全面而非绝对穷尽；明确指出客观判断搜索何时完成通常困难、基于新增记录等 stopping rules 很少得到正式评价、数据库检索仍可能漏掉相关研究、相对 recall 只是在已建立的 eligible set 上评价表现、定性/复杂/living review 的停止逻辑不同，并要求记录停止理由与搜索过程。`#section-4-5` 还明确说明网页内容和搜索算法会变化，网页结果不能达到数据库搜索同等复现性。这些内容共同蕴含“单一 saturation/recall/no-new-record 信号不能自动证明领域穷尽”和“停止理由必须结合任务、表现、漏失、资源并留痕”的有限 claim。
- `checked_source_ranges`:
  - `RS01-SRC-01`, SHA-256 `728bbac9ad5dae544d1a0549e0fe3f3812e00ad0f4e8c69a0dda2916f0efd26b`, Cochrane Handbook `version 6.5.1`, Chapter 4, HTML fragment `#section-4-2-2`。
  - 同一保存字节，HTML fragment `#section-4-4-11`。
  - 同一保存字节，HTML fragment `#section-4-5`。
- `overclaim_or_missing_counterevidence`: 没有发现会改变 `RS01-DD-01` 的遗漏反证。边界是该来源主要针对系统综述和相关网页检索，不提供适用于所有开放研究的统一算法，也不证明任何经验 stopping signal 永远无用；它只反对把该信号自动升级为穷尽证明。原 claim 的限制与这一边界一致。

### `RS01-CL-02`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-02`
- `verdict`: `entailed`
- `reason`: 摘要、引言、系统综述结果、讨论与结论都把提出的方法限定为以 downstream decision utility、错误后果和 screening cost 为目标，并明确使用“generally”及“evaluated cost and payoff settings”。系统综述结果同时报告 fixed-depth Budget 在 aggressive setting 的 net utility 更高、baselines 可有更高 recall/decision agreement、提出的方法不在全部指标和条件下支配 baseline。原 claim 已把这些限制写入句内，因此与保存页范围相符。
- `checked_source_ranges`:
  - `RS01-SRC-02`, SHA-256 `f9123e33da838b45f9aef4787720fb7f58ac3f0535ed39cf77fcb96767c73406`, PDF pp. `1-2`。
  - 同一保存字节，PDF pp. `8-10`。
  - 为检查遗漏反证，另只读检查同一保存字节 PDF p. `7` 的实验边界。
- `overclaim_or_missing_counterevidence`: 未发现会反转 `RS01-DD-01` 的遗漏反证。作者已保留“并非所有条件/指标占优”的主要反证；还应附加一个非 decision-changing 的适用边界：实验是 fixed、precomputed BM25 ranked-list screening，结果依赖 ranking/calibration quality，不覆盖 interactive search、active-learning 或 reranking-rescreening workflow。该边界阻止把论文算法直接外推到开放网络搜索，但不削弱“停止门应显式计入决策后果、成本和残余风险”的决定。

### `RS01-CL-03`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-03`
- `verdict`: `entailed`
- `reason`: 保存全文直接把 relevant studies 在 title/abstract/full-text screening 中被错误排除作为研究对象；摘要和正文同时说明 single-reviewer 与 dual-reviewer screening 都存在 missed-study 风险，并说明恢复 false exclusions 的方法证据有限、不能对最可靠方法作 firm conclusion。由此可直接得到：只观察已经筛选后的集合所产生的 stopping signal，若没有独立 screening-error probe，不能自行覆盖此前的 false-exclusion 通道。
- `checked_source_ranges`:
  - `RS01-SRC-03`, SHA-256 `6aa2f048c23bc62663c14cf11bf13143d07e60e442055cf3282590fbd6850aa0`, XML abstract `Abs1/Par1-Par4`。
  - 同一保存字节，XML body `Sec1/Par24-Par28`。
- `overclaim_or_missing_counterevidence`: 没有发现会改变 `RS01-DD-04` 的遗漏反证。逻辑边界应读作“已筛选集合的 stopping signal **单独**不能检测上游 screening error”；来源没有评价所有 stopping systems，也没有证明 false exclusion 的项目发生率。来源对恢复方法证据有限的反证已被作者保留。

### `RS01-CL-04`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-04`
- `verdict`: `contested_non_decision_changing`
- `reason`: 指定页范围直接蕴含核心 blind spot：只检查 citation-linked statements 会让 uncited factual claims 未被检查；该框架先分段并抽取可核验 statements，再检索外部 evidence，对 cited 与 uncited statements 给出 `Right/Wrong/Unknown`。但是，指定范围没有直接蕴含“完整 material-claim inventory”覆盖所有跨来源关系、因果链和总叙事，也没有建立必须分别检查 exact source snapshot、source quality 和系统性 counterevidence 的完整五分法。因此 claim 的核心前半段成立，后半段是合理但超出该单一来源直接 entailment 的治理设计综合。
- `checked_source_ranges`:
  - `RS01-SRC-04`, SHA-256 `3b6a3b8032dcaea9187e5aea88854268c3cf3782ab83e968ea93e0e8b2129446`, PDF pp. `1-2`。
  - 同一保存字节，PDF pp. `5-6`。
  - 为检查遗漏反证，另只读检查同一保存字节 Appendix D.2、PDF pp. `14-15`。
- `overclaim_or_missing_counterevidence`: 存在非 decision-changing overclaim。Appendix D.2 的实际 prompt 聚焦 core、publicly verifiable claims，并明确不核验每个句子；这证明该自动 evaluator 本身不是“完整 material-claim inventory + 五项独立检查”的实现证据。作者已保留“预印本、自动 evaluator、不能替代独立语义复核”的大方向，但漏记了这一更精确边界。它不反转 `RS01-DD-02`：inventory-before-citation 的核心移动由指定范围支持，exact bytes、entailment、source quality 与 counterevidence 分离仍是保守且与失效模式相符的治理要求；下游必须把这些附加控制标为项目设计综合，不能声称全部由 `RS01-SRC-04` 直接证明。

### `RS01-CL-05`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-05`
- `verdict`: `entailed`
- `reason`: 保存页明确把 human reference list 称为 known-imperfect coverage target，并区分“是否找回作者引用的论文”与“中立读者是否判断结果相关”两个问题；摘要、结果和讨论要求 recall、semantic/topical relevance、ranked-list diversity 与 co-authorship/network-distance diagnostics 共同报告，而不是把任一项单独当 ground truth 或 threshold。原 claim 没有采用论文中的 AI-over-human 排名结论，因此保持在来源可支持范围内。
- `checked_source_ranges`:
  - `RS01-SRC-05`, SHA-256 `90f65ea8fae259321341042124f2446f7deaa697953cb79eb3818a2fdb91c390`, PDF p. `1`。
  - 同一保存字节，PDF pp. `3-5`。
- `overclaim_or_missing_counterevidence`: 没有发现会改变 `RS01-DD-03` 的遗漏反证。必须保留的限制是 computer-science/arXiv 范围、单一 LLM judge、未建模 citation context、bibliography extraction noise，以及单一 judge 不可作自动拒绝 gate；作者已实质保留这些限制。来源不证明 AI list 普遍优于 human list，也不证明所列诊断轴已经完备。

### `RS01-CL-06`

- `reviewer_locator`: `codex_subagent:019f9a28-940e-7472-bb9a-69d0d49ac381`
- `review_input_sha256`: `4f30eee4675f1f6b0791731915b75b96a5ad5e37e5b1ef7c1b96cc3dd1e4ddee`
- `claim_id`: `RS01-CL-06`
- `verdict`: `entailed`
- `reason`: 保存的 item JSON 原文确实报告：用户让一个工具生成历史书，随后用另一个 research tool 核对历史事实与 cited sources 是否存在，第二个工具判断没有问题，但用户仍无法知道它是否重复了第一个工具的 hallucination，并认为完整验证仍需巨大投入。parent JSON 将该 comment 绑定到 verification-debt 主题。原 claim 明确限制为单个 practitioner reported experience 和 probe，因此没有把报告升级为已复现实证。
- `checked_source_ranges`:
  - `RS01-SRC-06`, SHA-256 `4d4f907c245a1dd924f890beaef04c8f4efe726f3724247af2db105a95ff5841`, item JSON `$.text`, `$.time`, `$.parent`。
  - `RS01-SRC-06-CONTEXT`, SHA-256 `f2882f6570e93190e76e3d878e5729c714f15b1690aee139b9d0eb0240b0c6a4`, parent JSON `$.title`, `$.url`。
- `overclaim_or_missing_counterevidence`: 没有 decision-changing overclaim。该 JSON 只能证明匿名用户报告了这段经验，不能证明历史书实际错误、第二个工具确实重复错误、任何错误发生率、产品能力排序或普遍机制。原 claim 和 decision effect 已把它限制为 negative-test/reopen hypothesis。

## 6. `RS01-DD-01..04` 漏反证检查

### 总体结果

没有从保存 bytes 中发现会反转、撤销或实质改变 `RS01-DD-01` 至 `RS01-DD-04` 的遗漏反证。发现的新增限制都属于适用范围或证据归属澄清，不构成 `decision_changing_contestation`：

| decision delta | 漏反证检查结果 | 更新建议 |
|---|---|---|
| `RS01-DD-01` | 无 decision-changing counterevidence。`RS01-SRC-02` 的 fixed-ranked、ranking/calibration-dependent 边界限制具体算法外推，但不反对记录 decision loss、cost、residual risk 与 reopen trigger。 | 保留决定；在证据说明中加入“论文只验证 fixed-ranked screening，不是开放网络 universal stop oracle”。 |
| `RS01-DD-02` | 无 decision-changing counterevidence。`RS01-SRC-04` 的实际 evaluator 不形成被证明完整的 material-claim inventory，也不直接实现全部五项控制。 | 保留决定；把 blind-spot 与 inventory-first 作为 source-supported core，把 snapshot/quality/counterevidence 五分法标为项目治理综合，并继续要求独立测试。 |
| `RS01-DD-03` | 无 decision-changing counterevidence。`RS01-SRC-05` 自身明确不同诊断互补且不能作单一 threshold。 | 保留决定与单轴 rejection；不得把论文中的 AI/human 分数比较升级为普遍主体排序。 |
| `RS01-DD-04` | 无 decision-changing counterevidence。`RS01-SRC-03` 直接支持 screening false-exclusion 独立通道，但不单独实证验证其余全部通道。 | 保留四通道 contract；明确它是跨来源与失效图的架构综合，不把四通道全部归因于 false-exclusion 论文。 |

## 7. 总 verdict

- `overall_verdict`: **RS-01 independent claim-entailment predicate 可用于 design closure**。
- 理由：全部逐 claim verdict 都属于预注册的 closure 允许集合；`RS01-CL-04` 的争议被明确限制为 `contested_non_decision_changing`，没有隐藏为 `entailed`。
- 本审查没有产生 `not_entailed` 或 `decision_changing_contestation`，也没有发现会改变 `RS01-DD-01..04` 的漏反证。
- 本 verdict 只移除 RS-01 的 independent claim-entailment blocker；它不证明开放网络领域穷尽，不完成 round-level ordinary comparison，不代表其他 topic 已 closure，也不意味着 implementation、design pre-review、最终 release 或投资系统完成。

## 8. Topic closure predicates 更新建议

| topic closure predicate | 更新建议 | 本 reviewer 的依据与边界 |
|---|---|---|
| 预注册 commit、文件 hash、祖先关系和检索时间通过 | 保持 `true`；在后续证据中追加 commit `3a0a44285b960d172e240a87567ce62dd90a0cb1` | 当前/commit 内预注册 hash 一致；该 commit 内 raw report 与审查输入 hash 一致；其 merge-base 是预注册 commit。本审查没有重写作者的检索时间台账。 |
| 五个 query_id 均有且仅有一次执行或明确工具失败 receipt | 保持 `true`，无本审查触发的更新 | 本轮没有执行新搜索；该 predicate 不属于逐-claim source-range entailment 的重新执行范围。 |
| 全部可见结果有逐结果筛选记录且归属唯一 query_id | 保持 `true`，无本审查触发的更新 | 本轮没有增加、删除或重新筛选搜索结果；不把 snapshot 检查误写成搜索完整性复验。 |
| required snapshot classes 均有保存字节与哈希，或明确 blocked | 保持 `true` | manifest 所列实际 snapshot byte count 与 SHA-256 全部只读重算匹配；failure receipt hash 也匹配。 |
| 每个决定性 claim 通过独立逐 claim 蕴含复核 | 从 `false` 更新为 `true` | 本文件提供 reviewer locator、input hash 和 `RS01-CL-01..06` 的全部必填字段；所有 verdict 均为 closure 允许值。 |
| 矛盾与反证已保留且有决定影响 | 保持 `true`，并把本文件 Section 5-6 作为附加 review evidence | 新增的 fixed-ranked limitation 与 `RS01-SRC-04` 证据归属限制已在此保存；没有 decision-changing counterevidence。 |
| 稳定性 passing_rule 满足 | 保持 `true` | 本审查没有产生新 high-impact failure class、decision reversal 或 open critical/major contradiction；`RS01-CL-04` 是非 decision-changing 的证据归属澄清。 |
| architecture 或 decision delta 已明确落到可执行 contract、test、gate、defer 或 rejection | 保持 `true`，附加 `RS01-DD-02` provenance clarification | 不改 delta；只要求下游不要把完整五分法误写成 `RS01-SRC-04` 的直接实证结论。 |
| 残余风险和重开触发器已明确 | 保持 `true` | 原有独立 reviewer、source revision/hash、模型/检索能力和实际负担触发器仍适用；若后续把自动 evaluator 当成完整 material-claim oracle，应立即重开 `RS01-DD-02`。 |

若维护者把本审查作为 RS-01 的独立审查证据纳入 closure 计算，则 RS-01 的 topic closure predicates 可全部为 `true`。这只是 RS-01 topic 级更新建议；R8 round 的其他 topics 与 ordinary comparison 仍须各自满足预注册条件。
