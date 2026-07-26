# R10 第二次独立蕴含审查（Review B）

- 审查方式：独立子代理、只读
- reviewer agent：`019f9bb3-10b6-7191-b0c2-6894df7d7dfe`
- 审查结论：`blocked`
- 审查期间候选未变化：
  - Method SHA-256：`1ce186c16bebfb45defccf05a97e1b5fe2ca7c925060d4f84c99132f51e21c8e`
  - Failure SHA-256：`48416ac6a11e5c2651a7db4dfab1a98c943a7a23ef44a4400f6a33bc43f765c7`
- 只读声明：审查者未修改任何文件。

## 开放问题

### R10-INFERENCE-STATUS

- severity：`major`
- state：`partially_resolved_open`
- location：Method 第 46、48–59、127、134 行附近
- evidence：控制表和 failure 表已区分 `external_fact`、`engineering_inference/hypothesis`、`project_policy` 与 `candidate_control`，但方法族表仍把各方法写成 “Necessary contribution”，并无分类地断言它们 “must compose”。来源不能直接蕴含这种普遍必要性。`M-C01` 又写成 ``project_policy`; adopted candidate``，没有明确究竟是已采用政策还是候选架构。
- required fix：把方法族必要性和组合关系明确降级为本项目的 `project_engineering_hypothesis` 或 `candidate_architecture`，并由本地验证决定；给 `M-C01` 一个无歧义状态和真实本地 locator。

### R10-SOURCE-PROVENANCE

- severity：`major`
- state：`partially_resolved_open`
- location：Method 第 91 行、Failure 第 90 行附近
- evidence：报告已经如实标出 arXiv 固定版本与 GitHub、Reddit、live docs 的 mutable/non-replayable 边界，也禁止不可重放来源关闭 decision-bearing gate；但没有精确 `retrieved_at_utc`、来源内容 SHA-256 或 R10 source manifest/snapshot。living-review state 只绑定报告哈希，不能替代来源字节绑定。
- required fix：为决定承重来源建立 R10 manifest，记录 canonical title、精确检索时间、版本或 commit、内容 SHA-256 与 snapshot locator。无法快照的来源只能保留为 non-replayable field probe，不能关闭历史事实或采用决定。

### R10B-SAME-TASK-PREREG-DRIFT

- severity：`major`
- state：`open`
- location：Method 第 146、220 行附近
- evidence：报告把“待执行的 fixed same-task comparison”写成 daily-market-data provider review，并比较 ordinary prompt 到 DAG 的累积条件；现行 R9 已预注册的任务是公司行动与 point-in-time 数据政策，只比较 `common_contract_only` 与 `common_contract_plus_minimum_core`，并明确禁止把 baseline 称为无治理 ordinary prompting。当前报告会把工作路由到一个未预注册设计。
- required fix：让报告精确摘要 R9 的任务、arms、范围和当前 blocker。若 provider-review 五条件设计仍值得保留，只能标成 `unregistered_future_proposal`，不得称作当前 fixed/preregistered comparison；不得反向修改 R9 来迎合报告。

### R10B-UNLOCATED-LOCAL-AUDIT

- severity：`major`
- state：`open`
- location：Method 第 135 行附近
- evidence：`M-C02` 把 “local R10 state-freshness audit”列为依据，但全仓库只有该行自身，没有审计 artifact、receipt、精确 locator 或哈希。
- required fix：提供真实审计 artifact 的路径、SHA-256、检查范围与结论；否则删除该依据，并保持 `unvalidated end to end`。

## 已关闭的 Review A 问题

### R10-ENTAIL-GRAPH

- state：`resolved`
- evidence：Graph Engineering 结论已限制在 bounded R10 source set；origin、adoption 和 accepted meaning 均保留未知；本地 DAG 决定被明确标成候选工程推断。

### R10-MECH-SELF-PREFERENCE

- state：`resolved`
- evidence：same-model evaluator identity preference、visible-oracle proxy optimization、shared-premise blind spot 与 circular oracle 已分开建模，后两项已降级为工程假设。

### R10-SCOPE-COUNTEREVIDENCE

- state：`resolved`
- evidence：SpecBench 的 mixed effect 已保留；held-out、compositional 和 adversarial controls 已拆分；Reddit 正反经验均保留且不再用于频率或因果泛化。

## 最终边界

两份报告保持 `bounded_incomplete` 是正确的，但该标签不能关闭上述 provenance、状态分类、预注册一致性和不存在证据的问题。Review B 不授权把研究层标记为 current、sufficient 或 accepted。
