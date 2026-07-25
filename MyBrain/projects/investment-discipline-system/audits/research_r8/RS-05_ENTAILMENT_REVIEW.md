# RS-05 independent per-claim entailment review

## Review disposition

- topic_id: `RS-05`
- round_id: `RESEARCH-REFRESH-R8`
- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_mode: `platform_observable_separate_thread_review`
- review_input: `audits/research_r8/RS-05_RAW_REPORT.md`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- expected_review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- review_input_integrity: `pass_exact_match`
- network_or_new_search: `not_performed`
- workflow_run_dispatch_or_modification: `not_performed`
- author_report_modified: `no`

本 review 的“分离”只表示 Codex 平台上可由上述 locator 观察到的 separate-thread review，并结合任务指定的 reviewer/author 角色分离。它不证明组织隔离、安全隔离、独立安全域、密码学 reviewer identity、内容签名的 reviewer attestation 或抗串通性。仓库内文件和本 review 自身都不能把该平台可观察事实升级为这些更强保证。

## Preregistered schema and verdict boundary

R8 preregistration 的逐 claim review 必填字段为：

- `reviewer_locator`
- `review_input_sha256`
- `claim_id`
- `verdict`
- `reason`
- `checked_source_ranges`
- `overclaim_or_missing_counterevidence`

可用于 design closure 的 verdict 仅为：

- `entailed`
- `contested_non_decision_changing`

`author_only_closure` 为 `false`，且 reviewer 不得撰写被审查 claims。本文件不改写作者 claims，只裁决其是否由冻结输入蕴含。

## Input and byte-integrity checks

- `RS-05_RAW_REPORT.md` SHA-256 重算后与预期值精确一致，未触发 fail-closed。
- `research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json` SHA-256 重算为 `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`。
- `source_snapshot_manifest.json` 声明的每个 source snapshot 与 procedural artifact 均按本地保存 bytes 重算 `byte_count` 和 SHA-256，未发现 mismatch。
- 对 Git anchor 另做只读对象级交叉核对：commit `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` 的 tree 为 `7cb2268e3715102c540f50f78ab0829dc0eaaeb6`；preregistration path blob 为 `0feba2836b8c83adf2bd6e109416bca8072a1c0c`，其 bytes SHA-256 为 `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`。
- 对 frozen workflow 另做只读对象级交叉核对：blob 为 `e7950d06e41f149a7e5b6ed070d2a40f3bf74c2a`，bytes SHA-256 为 `39f34cd20de4a2612c3c3c1a333e9e361e57b6bc19b9a5877fb3737024c55d42`；该检查只证明 configuration snapshot，不是 execution receipt。

## Decisive claim set

按 atomic ledger 中 `impact` 含 `decisive` 的记录，closure review 集合为：

- `R8-RS05-C01`
- `R8-RS05-C02`
- `R8-RS05-C05a`
- `R8-RS05-C05b`
- `R8-RS05-C05c`
- `R8-RS05-C05d`
- `R8-RS05-C06`

`R8-RS05-C03`、`R8-RS05-C04` 与 `R8-RS05-C07` 的 impact 为 `major` 或 `major_counterevidence`，不属于 preregistered decisive-claim closure 集合。

## Per-claim verdicts

### R8-RS05-C01

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C01`
- verdict: `entailed`
- reason: 保存的 GitHub CLI manual bytes 明确要求 artifact、actor identity 与 predicate type，并逐项提供 exact certificate identity、OIDC issuer、repository、signer repository/workflow/digest、source digest/ref、predicate type 与 self-hosted-runner rejection 等 policy controls。GitHub Docs 的固定 source revision 明确说 attestation 必须被验证、由 consumer 定义 policy，且不保证 artifact secure。OpenSSF 保存文章给出 expected builder/repository/workflow 与有效 attestation 仍可和 compromised pipeline 共存的具体反例。因此，这些条件作为本项目保守的 conjunctive policy 是有依据的，而“全部通过仍不证明语义正确”被直接反证支持。该 verdict 只裁决 policy design，不声称真实 receipt 已存在。
- checked_source_ranges: `github_docs_artifact_attestations_2026-07-25.html` lines `20-25`, `46-51`; immutable source cross-check `github_docs_artifact_attestations_b17436de8f10c3e7f6a185d6813bf94bc82d22f8.md` lines `18-20`, `28-30`, `34-50`; `github_cli_gh_attestation_verify_2026-07-25.html` lines `7395-7438`, `7464-7509`, `7514-7596`; `openssf_mini_shai_hulud_2026-06-10.html` lines `895-929`.
- overclaim_or_missing_counterevidence: 未发现 decision-changing overclaim，但必须保留三项限定：exact conjunction 是 project policy，不是文档承诺的充分保证；尚无 actual artifact/bundle/positive/negative receipt；OpenSSF 反例证明 identity match 不能升级为 artifact safety、predicate truth 或 semantic correctness。当前状态必须继续为 `github_issued_workflow_provenance: designed_not_observed`。

### R8-RS05-C02

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C02`
- verdict: `entailed`
- reason: CLI manual 的保存 bytes 明确限定只有 `signature.certificate` 与 `verifiedTimestamps` 含 originating workflow 不能操纵的值，并明确警告获得 workflow execution context 的 attacker 可 falsify `statement.predicate`。因此 certificate/timestamps 不蕴含 predicate truth，更不蕴含 command correctness、test correctness、review quality 或 investment-design semantics。
- checked_source_ranges: `github_cli_gh_attestation_verify_2026-07-25.html` lines `7464-7509`; supporting boundary cross-check `github_docs_artifact_attestations_b17436de8f10c3e7f6a185d6813bf94bc82d22f8.md` lines `46-50`.
- overclaim_or_missing_counterevidence: 没有把“可伪造”夸大为“每个 predicate 都是 false”；claim 与 limitations 均只限制 receipt 单独能证明什么。未发现缺失的 decision-changing counterevidence。

### R8-RS05-C05a

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C05a`
- verdict: `entailed`
- reason: 保存的 boundary receipt、GitHub commit response 与只读 Git object bytes 对 commit、tree、preregistration blob 和 preregistration SHA-256 给出一致值。它们足以固定 preregistered counted-search boundary 的内容 bytes。GitHub commit response 同时显示 `verified: false`、`reason: unsigned`，所以该锚只能命名为 `content_snapshot_anchor`。
- checked_source_ranges: `boundary_and_execution_status_receipt_2026-07-25.md` lines `6-23`, `44-67`; `github_commit_7824a63_2026-07-25.json` fields `sha`, `commit.tree.sha`, `commit.verification`, `parents`; frozen Git objects at commit `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`, tree `7cb2268e3715102c540f50f78ab0829dc0eaaeb6`, preregistration path blob `0feba2836b8c83adf2bd6e109416bca8072a1c0c`.
- overclaim_or_missing_counterevidence: Entailment 仅覆盖 preregistration boundary bytes，不覆盖 later evidence、raw report、review 文件或 final integration commit ancestry。该 anchor 不证明 author/reviewer identity、组织独立性、内容真值、semantic correctness 或 tamper-proof execution。最终 integration ancestry 仍是明确 blocker。

### R8-RS05-C05b

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C05b`
- verdict: `entailed`
- reason: Frozen Git object bytes 证明 boundary tree 中存在 workflow design；保存的 exact-SHA Actions response 为 `total_count: 0`、`workflow_runs: []`，repository workflows response 为 `total_count: 0`、`workflows: []`。Manifest execution boundary 同时记录未观察到 actual artifact 或 attestation bundle。冻结 packet 中没有 positive policy JSON 或 negative policy receipts。因此只允许 `designed_not_observed`，不能把 configuration 写成 execution。
- checked_source_ranges: complete bytes of `github_actions_runs_head_7824a63_2026-07-25.json`; complete bytes of `github_actions_workflows_2026-07-25.json`; `source_snapshot_manifest.json` object `execution_boundary`; `boundary_and_execution_status_receipt_2026-07-25.md` lines `44-53`, `69-90`; frozen workflow blob `e7950d06e41f149a7e5b6ed070d2a40f3bf74c2a`.
- overclaim_or_missing_counterevidence: No-result API state 是 retrieval-time frozen fact，不是当前 GitHub 状态的永久断言。冻结 packet 没有真实 workflow receipt；本 review 也没有运行、dispatch 或修改 workflow。`github_issued_workflow_provenance` 必须继续标为 `designed_not_observed`，且该研究 verdict 不能冒充 machine gate。

### R8-RS05-C05c

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C05c`
- verdict: `contested_non_decision_changing`
- reason: 完整保存的 D1、D2、S1、S2、S3 procedural receipts 中没有 source bytes 建立 Codex reviewer 的安全隔离、密码学 identity 或组织独立性。因此“本轮固定检索包没有升级证据”这一 bounded absence 结论成立，且保守地不升级名称是正确 decision effect。争议在于这些 receipts 保存的是检索结果与 screening 记录，不是 Codex 平台机制的 primary snapshot；它们不能正向证明 `platform_observable_separate_thread_review` 本身，更不能证明更强独立性。该证据缺口不会改变“不升级”的决定。
- checked_source_ranges: complete saved receipts `query_R8-RS05-D1.md`, `query_R8-RS05-D2.md`, `query_R8-RS05-S1.md`, `query_R8-RS05-S2.md`, `query_R8-RS05-S3.md`; `discovery_freeze_2026-07-25T162143Z.md` lines `59-69`, `83-91`; `RS-05_RAW_REPORT.md` lines `321-331`, `412-431`, `450-462`.
- overclaim_or_missing_counterevidence: Positive platform independence remains unproved. 本 review 的 locator 只使 separate-thread review 在平台层可观察；它不是组织/安全隔离或密码学独立保证，也没有 repository-verifiable content binding、reviewer signature、trust root 或 offline verifier。缺失证据要求保持原降级名称，不构成 decision-changing contradiction。

### R8-RS05-C05d

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C05d`
- verdict: `entailed`
- reason: Preregistration 的 RS-05 决策边界逐字保留“最终批准权属于 Javen”，round closure 又把 `Javen-only unresolved human decisions` 保留在 design pre-review 之后。故 machine receipt 与 AI review 只能作为输入，不能自动批准。这是 normative authority boundary，不是关于人类准确性的 empirical claim。
- checked_source_ranges: `RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json` lines `243-250`, `281`, `389-400`; `RS-05_RAW_REPORT.md` lines `333-343`, `383-410`, `412-431`, `450-462`.
- overclaim_or_missing_counterevidence: `human_final_decision_by_Javen` 不得被写成 correctness oracle、身份加密证明或 delegation receipt。它只规定最终批准权和禁止自动批准；未发现 decision-changing counterevidence。

### R8-RS05-C06

- reviewer_locator: `codex_subagent:019f9a2e-4bc6-7c73-89eb-2d42d7c08d42`
- review_input_sha256: `0c3ef71d9e921675c7aa230f54080fa82a4e84685ee76082a3b311bc5050d81b`
- claim_id: `R8-RS05-C06`
- verdict: `entailed`
- reason: 保存的 OpenSSF article bytes 明确报告 attacker 通过 untrusted code、shared-cache poisoning 与 OIDC token extraction 发布恶意 packages；attestations 被描述为 cryptographically valid，并准确指向 expected builder、repository、workflow。固定的 SLSA v1.2 threat-model bytes 独立列出 cross-build influence、signing-secret theft、cache poisoning 与 platform-admin compromise 等 threat classes。Claim 谨慎表述为 article “报告了”该反例，足以推翻 expected identity 是充分语义保证的推断。
- checked_source_ranges: `openssf_mini_shai_hulud_2026-06-10.html` lines `895-929`; `slsa_v1.2_threats_19e4e2f005f871270c4f555fc47afecfb37f3efe.md` lines `460-615`.
- overclaim_or_missing_counterevidence: OpenSSF article 是保存的事件分析，不是本 topic 内独立完成的 incident forensics，也不是 universal incidence estimate。文章同时说明更强 build isolation 可缓解该 attack class，且 expected-builder policy 仍有价值；报告将 identity policy 保持为 necessary-not-sufficient，已保留这项限定。未发现 decision-changing overclaim。

## Claim summary

| claim_id | verdict | closure effect |
|---|---|---|
| `R8-RS05-C01` | `entailed` | exact policy 可作为 design contract；真实 provenance 仍未观察 |
| `R8-RS05-C02` | `entailed` | certificate/timestamps 不证明 predicate truth 或 semantic correctness |
| `R8-RS05-C05a` | `entailed` | Git 仅为 `content_snapshot_anchor` |
| `R8-RS05-C05b` | `entailed` | GitHub 层保持 `designed_not_observed` |
| `R8-RS05-C05c` | `contested_non_decision_changing` | 只支持 bounded no-upgrade；不支持安全/组织/密码学独立性 |
| `R8-RS05-C05d` | `entailed` | 最终批准权仍属于 Javen；不自动批准 |
| `R8-RS05-C06` | `entailed` | expected identity 是必要非充分控制 |

所有 decisive claims 的 verdict 均位于 preregistration 允许的 design-closure verdict 集合内。没有 claim 需要 `not_entailed` blocker；`R8-RS05-C05c` 的争议明确收窄证据强度，但不改变保守 decision effect。

## Special boundary challenges

| boundary | reviewer finding |
|---|---|
| `content_snapshot_anchor` | Frozen Git object bytes 只锚定内容；commit 为 `unsigned`，不证明作者、reviewer、组织独立性或语义真值。 |
| `github_issued_workflow_provenance` | Workflow blob 只证明 design；真实 run/artifact/bundle/policy receipts 未发生，必须继续为 `designed_not_observed`。 |
| `platform_observable_separate_thread_review` | 本 review 只有 platform-observable locator；没有安全隔离、组织隔离、密码学 identity、签名内容绑定或 anti-collusion 保证。 |
| attestation semantics | Certificate identity、timestamps、subject/type binding 与 predicate truth、materials completeness、command truth、review quality、investment semantics 是不同命题；前者不能自动证明后者。 |
| `human_final_decision_by_Javen` | Javen 保留最终批准权；该规范边界不是 correctness oracle，machine/AI 结果不得自动批准。 |

## Topic closure predicate update recommendations

| preregistered predicate | recommended state after this review | reason / remaining blocker |
|---|---|---|
| preregistration commit、file hash、ancestor relation、retrieval time | `partial_pass_pending_final_integration_commit` | Frozen boundary bytes pass；包含 raw report、manifest 与本 review 的 final integration commit ancestry 尚未验证。 |
| five query IDs each exactly once or explicit failure receipt | `pass` | 保存 receipts 与 manifest accounting 一致；本 review 未执行新搜索。 |
| all visible results screened and uniquely attributed | `pass_with_backend_scope_caveat` | 保存 ledgers 完整覆盖 tool-visible ranks；不声称 latent corpus completeness。 |
| required snapshot classes saved with bytes and hashes | `pass` | Manifest-declared saved bytes、byte counts 与 SHA-256 均重算无 mismatch。 |
| every decisive claim independently reviewed | `pass_platform_observable_separate_thread` | 本文件绑定 exact raw-report SHA-256；逐 claim verdict 全部属于 allowed closure set。该 pass 不升级 reviewer independence strength。 |
| contradictions/counterevidence retained with decision effect | `pass` | Predicate-control warning、compromised-pipeline counterexample、unsigned Git、no-run receipt 与 platform-independence limits 均保留。 |
| stability passing rule | `pass` | 维持作者记录的 S1 后 S2、S3 无新增 high-impact delta 结论；本 review 未做新搜索或重开 stability。 |
| architecture/decision delta mapped to contract/test/gate/defer/rejection | `pass_design_only` | Future policy matrix 是 design contract；实际 machine gate 未执行，不能升级为 observed assurance。 |
| residual risk and reopen triggers explicit | `pass` | Final integration ancestry、真实 workflow receipts、platform review binding 与 Javen human boundary 均仍明确。 |

## Overall verdict and blockers

- independent_decisive_claim_entailment_predicate: `pass`
- current_RS-05_topic_status_recommendation: `bounded_incomplete`
- current_github_machine_state: `github_issued_workflow_provenance: designed_not_observed`
- machine_assurance_gate: `not_executed_not_observed`
- automatic_approval: `forbidden`
- final_decision_authority: `Javen`

当前 `bounded_incomplete` 的 remaining topic-closure blocker 是 final integration commit ancestry 尚未验证。本 review 文件本身必须先被纳入 final integration commit，之后才能对该 commit 做 ancestor check；本文件不预写未来结果为 pass。

真实 GitHub workflow receipt 未发生不应被伪装为已通过，也不应被错误地用来否定 design-research 中已经成立的有限 entailment。它仍然是独立的 machine-assurance gate 和后续 final-release prerequisite。换言之：研究 closure predicate、machine gate 与 Javen 最终批准是三个不同层次，任何一层都不能替另一层自动通过。

若 final integration ancestry 后续通过，可把 RS-05 的 design-research topic closure predicates 更新为满足；这仍只表示 design pre-review 层面的研究 closure，不表示 workflow provenance observed、machine assurance passed、final release allowed 或 Javen 已批准。
