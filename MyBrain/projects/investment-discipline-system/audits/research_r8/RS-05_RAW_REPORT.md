# RESEARCH-REFRESH-R8 / RS-05 raw report

## 0. Disposition

- topic_id: `RS-05`
- question: Git、GitHub Actions provenance、可观察 Codex 审查与 Javen 最终决定应怎样组合而不夸大独立性或语义保证？
- author_role: RS-05 evidence collector and claim author; **not** the independent entailment reviewer.
- final_topic_status: `bounded_incomplete`
- stability_status: `pass`
- required_snapshot_classes: `satisfied`
- independent_entailment_review: `not_performed`
- GitHub machine provenance state: `github_issued_workflow_provenance: designed_not_observed`
- workflow boundary: This author did not run, dispatch, or modify a GitHub workflow.

结论先限定在证据实际支持的范围内：

1. 保留 R7 的四个降级名称：`content_snapshot_anchor`、`github_issued_workflow_provenance`、`platform_observable_separate_thread_review`、`human_final_decision_by_Javen`。
2. GitHub attestation 可以把本地 artifact digest 与签名 statement、GitHub-issued certificate identity 和 timestamps 绑定起来；它不证明 workflow-controlled predicate、命令、材料完整性、review 质量或投资设计语义正确。
3. 精确 repository、issuer、workflow identity、source digest、predicate type、signer 与 hosted-runner policy 都是必要条件，但不是充分条件。S1 找到的公开反例显示：预期 builder、repository、workflow 都匹配的有效 attestation 仍可来自已被 cache/OIDC/build-environment compromise 的流水线。
4. 边界 commit 含有 workflow 设计文件，但只读 GitHub API 对该 SHA 返回 `total_count: 0` 的 runs receipt；没有 artifact、bundle、正向 verification JSON 或负向 policy receipts。因此不能把 workflow 文件写成 observed provenance。
5. 稳定性规则通过：最后一个高影响 delta 出现在 S1，之后 S2 与 S3 都没有新增高影响失效类、决定反转或开放 critical/major contradiction。
6. 主题仍为 `bounded_incomplete`，因为决定性 claims 没有由与作者分离的 reviewer 逐 claim 复核；最新 RS-05 文件进入最终 integration commit 后的 ancestry 也必须由主代理重验。作者不能自签为 independent reviewer。

## 1. Temporal boundary and Git proof

完整只读输出保存在 `research/evidence/r8/RS-05/boundary_and_execution_status_receipt_2026-07-25.md`。

| check | observed source value | result |
|---|---|---|
| preregistration commit | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | pass |
| commit time | `2026-07-25T09:13:44-07:00` = `2026-07-25T16:13:44Z` | pass |
| commit tree | `7cb2268e3715102c540f50f78ab0829dc0eaaeb6` | recorded |
| preregistration file SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | exact match |
| commit file blob | `0feba2836b8c83adf2bd6e109416bca8072a1c0c` | working bytes matched at initial check |
| remote containment | `origin/codex/investment-assurance-r7` | pass at initial check |
| initial `HEAD` | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | exact boundary before D1 |
| first counted retrieval | `2026-07-25T16:17:56Z` | after `2026-07-25T16:13:44Z` |
| GitHub commit verification | `verified: false`, `reason: unsigned` | supports content anchor only |

并发工作期间共享分支被自动 vault-backup commits 推进。RS-05 没有 reset、rebase 或修改他人文件。下列当前已观察到的 R8 evidence commits 都以 exit `0` 通过 `git merge-base --is-ancestor 7824a63... <commit>`：

| later evidence commit | commit time | subject | ancestry exit |
|---|---|---|---:|
| `1ebc3f3592953cb4fe52821cd551a70921b657fb` | `2026-07-25T09:23:17-07:00` | `vault backup: 2026-07-25 09:23:17` | `0` |
| `9a930cee9915510e01880b96b6f1f2d7be476bd0` | `2026-07-25T09:28:40-07:00` | `vault backup: 2026-07-25 09:28:39` | `0` |
| `98bdf382cf34c7cc3ca5f6e889983e51c60e1695` | `2026-07-25T09:33:58-07:00` | `vault backup: 2026-07-25 09:33:58` | `0` |

`216dde18eefb6e6e26ce3d3082252cc128c6bcd3` 也是后代（exit `0`），但 scoped path check 没有发现该 commit 写入 RS-05 evidence。最终 raw report 与最新 evidence 被 integration commit 收纳后，主代理仍须对那个最终 commit 重跑 ancestry；未来结果不在本报告中预写为 pass。

## 2. Current workflow / execution receipt boundary

边界 tree 中存在 `.github/workflows/investment-discipline-assurance.yml`：

- Git blob: `e7950d06e41f149a7e5b6ed070d2a40f3bf74c2a`
- SHA-256: `39f34cd20de4a2612c3c3c1a333e9e361e57b6bc19b9a5877fb3737024c55d42`
- declared runner: `ubuntu-latest`
- declared attestation action: `actions/attest@36051bcae73b7c2a8a6945a48cbf80953c6baa35`

这些值只证明 workflow configuration 的内容快照。workflow 可以控制自己的 predicate 与执行步骤；`runs-on` 声明也不是 hosted-runner certificate receipt。

`2026-07-25T16:31:04Z` 的只读 GitHub receipts：

- exact boundary SHA runs API：`{"total_count":0,"workflow_runs":[]}`
- repository workflows API：`{"total_count":0,"workflows":[]}`
- boundary commit API：`verification.verified=false`、`verification.reason=unsigned`

因此当前状态必须是：

```text
content_snapshot_anchor: observed
github_issued_workflow_provenance: designed_not_observed
actual_artifact: not_observed
actual_attestation_bundle: not_observed
positive_policy_verification: not_observed
negative_policy_tests: not_observed
```

## 3. Exact query accounting and discovery freeze

每个 query 均为一次独立 `web.search_query` 调用；没有 batch、改写、追加或第六次查询。完整 visible summaries、screening reason、class、cluster 与 revision 保存在对应 receipt。

| ID | exact query | start UTC | end UTC | visible result count | receipt |
|---|---|---|---|---:|---|
| `R8-RS05-D1` | `site:docs.github.com artifact attestations verification policy workflow identity source digest` | `2026-07-25T16:17:56Z` | `2026-07-25T16:18:05Z` | `14` | `query_R8-RS05-D1.md` |
| `R8-RS05-D2` | `site:cli.github.com/manual gh attestation verify signer workflow source digest predicate` | `2026-07-25T16:18:12Z` | `2026-07-25T16:18:21Z` | `12` | `query_R8-RS05-D2.md` |
| discovery freeze | claims/deltas frozen; no stability query yet | `2026-07-25T16:21:43Z` | `2026-07-25T16:21:43Z` | n/a | `discovery_freeze_2026-07-25T162143Z.md` |
| `R8-RS05-S1` | `SLSA provenance threat model maintainer platform isolation limitations` | `2026-07-25T16:21:58Z` | `2026-07-25T16:22:08Z` | `21` | `query_R8-RS05-S1.md` |
| `R8-RS05-S2` | `in-toto attestation limitations omitted materials false predicate` | `2026-07-25T16:24:06Z` | `2026-07-25T16:24:22Z` | `18` | `query_R8-RS05-S2.md` |
| `R8-RS05-S3` | `GitHub artifact attestation user issue verification policy limitation` | `2026-07-25T16:25:45Z` | `2026-07-25T16:25:53Z` | `11` | `query_R8-RS05-S3.md` |

Backend provenance caveat：每次 receipt 都保存了单次工具响应中完整可见的结果集合，但后端没有暴露 total-hit count 或 continuation cursor，visible summaries 也受工具输出边界约束。本报告不把“全部可见结果已记录”扩大成“搜索引擎潜在语料已穷尽”。

## 4. Complete visible result-set ledger

以下表格不漏掉任何 visible rank。逐结果 visible summary 和完整 screening reason 见对应 query receipt。

### 4.1 D1 complete visible results

| rank | result | class / cluster | screening | revision |
|---:|---|---|---|---|
| `0` | [Artifact attestations - GitHub Docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include decisive | mutable live current |
| `1` | [Managing the lifecycle of artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting | mutable live current |
| `2` | [Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | exclude same-upstream redundant | mutable live current |
| `3` | [Using artifact attestations and reusable workflows to achieve SLSA v1 Build Level 3](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting | mutable live current |
| `4` | [Using artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations) | official docs index / `GH-DOC-ATTEST-CURRENT` | exclude navigation only | mutable live current |
| `5` | [REST API endpoints for artifact attestations — orgs](https://docs.github.com/en/rest/orgs/attestations) | official API docs / `GH-DOC-ATTEST-REST` | include supporting | mutable; example API `2026-03-10` |
| `6` | [Using artifact attestations to establish provenance for builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting | mutable live current |
| `7` | [REST API endpoints for artifact attestations — users](https://docs.github.com/en/rest/users/attestations) | official API docs / `GH-DOC-ATTEST-REST` | exclude same-upstream redundant | mutable; example API `2026-03-10` |
| `8` | [Enterprise Cloud @latest usage guide](https://docs.github.com/en/enterprise-cloud%40latest/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) | official Enterprise docs / `GH-DOC-ATTEST-CURRENT` | exclude same-upstream variant | mutable `@latest` |
| `9` | [REST API endpoints for repository attestations](https://docs.github.com/en/rest/repos/attestations) | official API docs / `GH-DOC-ATTEST-REST` | include supporting | mutable live current |
| `10` | [Verifying attestations offline](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting | mutable live current |
| `11` | [Best practices for securing your build system](https://docs.github.com/en/code-security/tutorials/implement-supply-chain-best-practices/securing-builds) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | exclude same-upstream redundant | mutable live current |
| `12` | [GitHub Privacy Statement - FR translation 2020.08.31](https://docs.github.com/assets/images/help/site-policy/github-privacy-statement%2807.22.20%29%28fr%29.pdf) | search noise / `NOISE-GH-PDF` | exclude out of scope | historical irrelevant |
| `13` | [GitHub Statement against Modern Slavery and Child Labor](https://docs.github.com/assets/images/help/site-policy/github-statement-against-modern-slavery-and-child-labor.pdf) | search noise / `NOISE-GH-PDF` | exclude out of scope | historical irrelevant |

### 4.2 D2 complete visible results

| rank | result | class / cluster | screening | revision |
|---:|---|---|---|---|
| `0` | [gh attestation verify](https://cli.github.com/manual/gh_attestation_verify) | current official CLI manual / `GH-CLI-ATTEST-CURRENT` | include decisive | mutable live manual |
| `1` | [gh release verify](https://cli.github.com/manual/gh_release_verify) | current official CLI manual / `GH-CLI-RELEASE-ATTEST` | exclude out of scope | mutable live manual |
| `2` | [gh help reference](https://cli.github.com/manual/gh_help_reference) | current official CLI manual / `GH-CLI-ATTEST-CURRENT` | exclude same-upstream redundant | mutable live manual |
| `3` | [gh attestation download](https://cli.github.com/manual/gh_attestation_download) | current official CLI manual / `GH-CLI-ATTEST-CURRENT` | include supporting | public preview |
| `4` | [gh attestation](https://cli.github.com/manual/gh_attestation) | official CLI index / `GH-CLI-ATTEST-CURRENT` | exclude navigation only | mutable live manual |
| `5` | [gh attestation trusted-root](https://cli.github.com/manual/gh_attestation_trusted-root) | current official CLI manual / `GH-CLI-ATTEST-CURRENT` | include supporting | mutable live manual |
| `6` | [gh release verify-asset](https://cli.github.com/manual/gh_release_verify-asset) | current official CLI manual / `GH-CLI-RELEASE-ATTEST` | exclude out of scope | mutable live manual |
| `7` | [gh](https://cli.github.com/manual/gh) | official CLI root / `GH-CLI-ROOT` | exclude navigation only | mutable live manual |
| `8` | [gh run view](https://cli.github.com/manual/gh_run_view) | current official CLI manual / `GH-CLI-ACTIONS-OPS` | exclude out of scope | mutable live manual |
| `9` | [gh extension](https://cli.github.com/manual/gh_extension) | current official CLI manual / `GH-CLI-EXTENSIONS` | exclude out of scope | mutable live manual |
| `10` | [gh workflow run](https://cli.github.com/manual/gh_workflow_run) | current official CLI manual / `GH-CLI-ACTIONS-OPS` | exclude out of scope and forbidden execution | mutable live manual |
| `11` | [gh workflow list](https://cli.github.com/manual/gh_workflow_list) | current official CLI manual / `GH-CLI-ACTIONS-OPS` | exclude out of scope | mutable live manual |

### 4.3 S1 complete visible results

| rank | result | class / cluster | screening | revision |
|---:|---|---|---|---|
| `0` | [slsa-github-generator SPECIFICATIONS.md](https://github.com/slsa-framework/slsa-github-generator/blob/main/SPECIFICATIONS.md) | primary implementation threat model / `SLSA-GH-GENERATOR` | include supporting | mutable `main` |
| `1` | [Mini Shai-Hulud: Where SLSA’s Boundaries Fall](https://openssf.org/blog/2026/06/10/mini-shai-hulud-where-slsas-boundaries-fall/) | independent foundation incident analysis / `OPENSSF-MINI-SHAI-HULUD` | include decisive counterevidence | dated `2026-06-10` |
| `2` | [SLSA v1.2 Threats & mitigations](https://slsa.dev/spec/v1.2/threats) | versioned primary standard / `SLSA-V1.2-STANDARD` | include decisive | versioned `v1.2` |
| `3` | [SLSA v1.0 Verifying build platforms mirror](https://kannkyo.github.io/slsa/spec/v1.0/verifying-systems) | unofficial standard mirror / `SLSA-STANDARD-MIRROR` | exclude same-upstream mirror | historical `v1.0` |
| `4` | [SLSA v1.0-rc2 Provenance](https://slsa.dev/spec/v1.0-rc2/provenance) | historical primary standard / `SLSA-HISTORICAL-STANDARD` | exclude superseded | `v1.0-rc2` |
| `5` | [SLSA v0.1 Security levels](https://slsa.dev/spec/v0.1/levels) | historical primary standard / `SLSA-HISTORICAL-STANDARD` | exclude superseded | `v0.1` |
| `6` | [DeepWiki SLSA Specification](https://deepwiki.com/slsa-framework/slsa/2-slsa-specification) | tertiary generated summary / `TERTIARY-SLSA-SUMMARY` | exclude lower authority | mutable |
| `7` | [PAIR-Systems-Inc/slsa](https://github.com/PAIR-Systems-Inc/slsa) | third-party repository summary / `PAIR-SLSA-FORK` | exclude lower authority | mutable default branch |
| `8` | [threatcl SLSA self-report mirror](https://ithub.global.ssl.fastly.net/threatcl/threatcl/blob/main/docs/SLSA.md) | project self-report / `THREATCL-SELF-REPORT` | exclude not independently verified | mutable mirror |
| `9` | [SLSA v1.0 What's new mirror](https://kannkyo.github.io/slsa/spec/v1.0/whats-new) | unofficial historical mirror / `SLSA-STANDARD-MIRROR` | exclude same-upstream mirror | historical |
| `10` | [Google Online Security Blog: Introducing SLSA](https://security.googleblog.com/2021/06/introducing-slsa-end-to-end-framework.html) | historical primary announcement / `SLSA-ORIGIN-ANNOUNCEMENT` | exclude superseded background | dated `2021` |
| `11` | [SLSA Provenance v1-rc1 mirror](https://marklodato.github.io/slsa/provenance/v1-rc1) | unofficial historical mirror / `SLSA-STANDARD-MIRROR` | exclude superseded mirror | `v1-rc1` |
| `12` | [OSTIF zlib audit PDF](https://ostif.org/wp-content/uploads/2026/01/ZLB-01-zlib_OSTIF-Audit-Public-RC1.1.pdf) | independent audit PDF / `OSTIF-ZLIB-AUDIT` | exclude incidental match | `2026` release candidate |
| `13` | [Auditing Frameworks Need Resource Isolation](https://arxiv.org/abs/2307.15895) | academic preprint / `SYSTEM-PROVENANCE-NODROP` | exclude different provenance domain | historical preprint |
| `14` | [Cloud Security Alliance Shai-Hulud note 20260517](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_shai-hulud-ai-supply-chain_20260517-csa-styled.pdf) | independent foundation note / `MINI-SHAI-HULUD-DERIVED-ANALYSES` | exclude same-incident secondary | dated `2026-05` |
| `15` | [Cloud Security Alliance Shai-Hulud note 20260514](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_shai-hulud-ai-npm-supply-chain-attack_20260514-csa-styled.pdf) | independent foundation note / `MINI-SHAI-HULUD-DERIVED-ANALYSES` | exclude same-incident secondary | dated `2026-05` |
| `16` | [Analyzing Challenges in Deployment of the SLSA Framework](https://arxiv.org/abs/2409.05014) | academic preprint / `SLSA-DEPLOYMENT-STUDY` | include supporting counterevidence | preprint version not shown |
| `17` | [Cloud Security Alliance Shai-Hulud note 20260515](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_mini_shai_hulud_supply_chain_sigstore_20260515-csa-styled.pdf) | independent foundation note / `MINI-SHAI-HULUD-DERIVED-ANALYSES` | exclude same-incident secondary | dated `2026-05` |
| `18` | [Agentic AI for Autonomous Defense in Software Supply Chain Security](https://arxiv.org/abs/2512.23480) | academic preprint / `AI-SUPPLY-CHAIN-DEFENSE` | exclude out of scope | preprint |
| `19` | [A Use Case of Using Scribe Trust Hub](https://www.cybersymposiums.com/tdf/EarlyAccess/images/pdfs/scribe02.pdf) | practitioner use-case PDF / `SCRIBE-USE-CASE` | exclude lower relevance | `2026` early access |
| `20` | [Threat Detection and Investigation with System-level Provenance Graphs](https://arxiv.org/abs/2006.01722) | academic preprint / `SYSTEM-PROVENANCE-SURVEY` | exclude different provenance domain | historical preprint |

### 4.4 S2 complete visible results

| rank | result | class / cluster | screening | revision |
|---:|---|---|---|---|
| `0` | [in-toto Link predicate](https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md) | primary attestation standard repo / `IN-TOTO-ATTESTATION-SPEC` | include decisive | mutable `main`; Link `v0.3` |
| `1` | [in-toto SCAI predicate](https://github.com/in-toto/attestation/blob/main/spec/predicates/scai.md) | primary attestation standard repo / `IN-TOTO-ATTESTATION-SPEC` | include supporting counterevidence | mutable `main`; SCAI `v0.3` |
| `2` | [in-toto Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) | primary attestation standard repo / `IN-TOTO-ATTESTATION-SPEC` | include decisive | mutable `main`; Statement `v1` |
| `3` | [in-toto/attestation repository](https://github.com/in-toto/attestation) | primary standard repo / `IN-TOTO-ATTESTATION-SPEC` | include revision receipt | latest visible release `v1.2.0` |
| `4` | [in-toto Attestation Framework Spec README](https://github.com/in-toto/attestation/blob/main/spec/README.md) | primary standard repo / `IN-TOTO-ATTESTATION-SPEC` | include supporting | reports `v1.2` |
| `5` | [Legacy in-toto specification](https://github.com/in-toto/docs/blob/master/in-toto-spec.md) | primary legacy spec / `IN-TOTO-LEGACY-SPEC` | include decisive counterevidence | legacy `master` |
| `6` | [in-toto predicate registry](https://github.com/in-toto/attestation/blob/main/spec/predicates/README.md) | primary standard repo / `IN-TOTO-ATTESTATION-SPEC` | include supporting | mutable `main` |
| `7` | [Python Packaging index-hosted attestations](https://packaging.python.org/en/latest/specifications/index-hosted-attestations/) | official ecosystem spec / `PYPA-INDEX-ATTESTATIONS` | exclude different implementation scope | mutable latest |
| `8` | [Fail-Closed Policy](https://wiki.totto.org/topics/defendable-agents/primitives/fail-closed-policy/) | individual practitioner design / `TOTTO-AGENT-DESIGN` | exclude out of scope/lower authority | recent mutable |
| `9` | [Trust & Attestation](https://wiki.totto.org/topics/defendable-agents/primitives/trust-and-attestation/) | individual practitioner design / `TOTTO-AGENT-DESIGN` | exclude out of scope/lower authority | recent mutable |
| `10` | [in-toto Attestation Formats Reviewed](https://safeguard.sh/resources/blog/in-toto-attestation-formats-review) | vendor summary / `SAFEGUARD-IN-TOTO-REVIEW` | exclude lower authority | historical mutable |
| `11` | [DevGuard in-toto framework docs](https://docs.devguard.org/explanations/supply-chain-security/in-toto-framework/) | vendor docs / `DEVGUARD-IN-TOTO-SUMMARY` | exclude lower authority | mutable |
| `12` | [Federal Register PDF](https://www.govinfo.gov/content/pkg/FR-1955-05-14/pdf/FR-1955-05-14.pdf) | search noise / `NOISE-GENERIC-ATTESTATION` | exclude out of scope | historical irrelevant |
| `13` | [Omslag exjobb utan bild(1)](https://www.diva-portal.org/smash/get/diva2%3A1959293/FULLTEXT01.pdf) | academic thesis / `THESIS-IN-TOTO` | exclude lower authority | dated thesis |
| `14` | [Jeremy Bentham book PDF](https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/1998/0872.07_Bk.pdf) | search noise / `NOISE-GENERIC-ATTESTATION` | exclude out of scope | historical irrelevant |
| `15` | [Enhancing Validation Through](https://pnsqc.org/docs/PROP101618755-PNSQC_Clausner_2024_Final.pdf) | conference practitioner paper / `PNSQC-IN-TOTO` | exclude background only | dated `2024` |
| `16` | [Allahabad High Court document 6169](https://elegalix.allahabadhighcourt.in/elegalix/WebDownloadOriginalHCJudgmentDocument.do?translatedJudgmentID=6169) | search noise / `NOISE-IN-TOTO-PHRASE` | exclude out of scope | historical irrelevant |
| `17` | [Allahabad High Court document 3961](https://elegalix.allahabadhighcourt.in/elegalix/WebDownloadOriginalHCJudgmentDocument.do?translatedJudgmentID=3961) | search noise / `NOISE-GENERIC-ATTESTATION` | exclude out of scope | historical irrelevant |

### 4.5 S3 complete visible results

| rank | result | class / cluster | screening | revision |
|---:|---|---|---|---|
| `0` | [Artifact attestations - GitHub Docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include decisive existing cluster | mutable live current |
| `1` | [Recent improvements to Artifact Attestations](https://github.blog/changelog/2025-02-18-recent-improvements-to-artifact-attestations/) | official product changelog / `GH-ATTEST-CHANGELOG` | include revision context | dated `2025-02-18` |
| `2` | [Managing the lifecycle of artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting existing cluster | mutable live current |
| `3` | [Using artifact attestations to establish provenance](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations) | current official GitHub docs / `GH-DOC-ATTEST-CURRENT` | include supporting existing cluster | mutable live current |
| `4` | [REST users attestations](https://docs.github.com/en/rest/users/attestations) | official API docs / `GH-DOC-ATTEST-REST` | exclude same-upstream redundant | mutable; example API `2026-03-10` |
| `5` | [REST orgs attestations](https://docs.github.com/en/rest/orgs/attestations) | official API docs / `GH-DOC-ATTEST-REST` | exclude same-upstream redundant | mutable; example API `2026-03-10` |
| `6` | [REST repository attestations](https://docs.github.com/en/rest/repos/attestations) | official API docs / `GH-DOC-ATTEST-REST` | include supporting existing cluster | mutable; example API `2026-03-10` |
| `7` | [actions/attest](https://github.com/actions/attest) | official action repo / `GH-ACTIONS-ATTEST` | include supporting | mutable default branch |
| `8` | [artifact-attestations-opa-provider](https://github.com/github/artifact-attestations-opa-provider) | official policy provider repo / `GH-ATTEST-OPA-PROVIDER` | include supporting | mutable default branch |
| `9` | [cli/cli issue #11803](https://github.com/cli/cli/issues/11803) | independent user implementation issue / `GH-CLI-ISSUE-11803` | include required independent issue | open at retrieval |
| `10` | [cli/cli issue #9602](https://github.com/cli/cli/issues/9602) | historical independent user issue / `GH-CLI-ISSUE-9602` | include revision/supersession receipt | closed/completed |

## 5. Exact-byte snapshots and manifest

Machine-readable manifest: `research/evidence/r8/RS-05/source_snapshot_manifest.json`. The manifest was validated with `jq`, and every declared local byte count/SHA-256 was recomputed with no mismatch.

### Required snapshot classes

| required class | decisive local bytes | byte count | SHA-256 | status |
|---|---|---:|---|---|
| current official GitHub verification documentation | `github_docs_artifact_attestations_2026-07-25.html` | `298345` | `d91064f240ea74e135440faf4c59585ba639dd907f68466347cdf250a4eb7c81` | satisfied |
| current official GitHub CLI verification manual | `github_cli_gh_attestation_verify_2026-07-25.html` | `110557` | `b5cffef82b3ed36d64d74e7fe8eaef4eea08a9eed29cf8e616f43b6ef770fd62` | satisfied |
| immutable GitHub Docs source revision | `github_docs_artifact_attestations_b17436de8f10c3e7f6a185d6813bf94bc82d22f8.md` | `3828` | `664b528c604fb5b1cd0100b7dc5f785ccbef5091421840b460cd2a750d02f4dd` | satisfied |
| versioned provenance threat model | `slsa_v1.2_threats_19e4e2f005f871270c4f555fc47afecfb37f3efe.md` | `48854` | `2d86d5ed3b2d70771773eb79724ce6cc034ef131ade49ebb48f28a2fe2961cda` | satisfied |
| versioned primary attestation standard | `in_toto_link_v0.3_df02077bf97218a8860a5c534eff1f1381f56984.md` | `4917` | `23703e071424e2468382a90355493cdc2c0defe8b97250a93db2be24c14cfbb0` | satisfied |
| versioned primary Statement standard | `in_toto_statement_v1_df02077bf97218a8860a5c534eff1f1381f56984.md` | `2492` | `cbe684a18b812b8b613d9202eb43b2ea24477f91a2ad6ca5be935185a455ebea` | satisfied |
| independent implementation issue | `github_cli_issue_11803_2026-07-25.json` | `4118` | `fb8bdb0f23177c2c13ee1a594930d8ed9f3d80832e3f644b9f362000f2770f8a` | satisfied |
| independent issue comments | `github_cli_issue_11803_comments_2026-07-25.json` | `52081` | `3c636a44a02ce411bafa3ec4b48f4c083c674c5c5186572567dda843534c06f1` | satisfied |
| decisive counterexample article | `openssf_mini_shai_hulud_2026-06-10.html` | `112303` | `59d5b13eab8bfcb4b9ee7044e64a3bfeb5ab573c1e43c967407daf92c28fd452` | saved |
| boundary exact-SHA no-run receipt | `github_actions_runs_head_7824a63_2026-07-25.json` | `50` | `52d589da93373d1efadfa660185a0970a1b2320703a8b87d6ed693946661e1cd` | saved |
| boundary GitHub commit receipt | `github_commit_7824a63_2026-07-25.json` | `25825` | `80667b71ae9e8b2f00f7680f03cf4e2613708b8c8dd3e11e78acf1268348bef1` | saved |

SLSA tag `v1.2` 的 exact ref receipt 指向 commit `19e4e2f005f871270c4f555fc47afecfb37f3efe`；in-toto tag `v1.2.0` 的 exact ref receipt 指向 commit `df02077bf97218a8860a5c534eff1f1381f56984`。因此决定性标准不是只靠 mutable `main` locator。

## 6. Frozen claims and delta chronology

### Discovery freeze after D2

`2026-07-25T16:21:43Z` 冻结的 claims：

- `R8-RS05-C01`: verification 是 conjunctive policy check；裸 `--repo` 或“有签名”不足。
- `R8-RS05-C02`: workflow-controlled predicate 不能成为语义证明。
- `R8-RS05-C03`: reusable workflow 情况下 caller/source 与 actual signer identity 必须分开。
- `R8-RS05-C04`: durable receipt 必须保存 artifact、bundle、trust-root/version context、verifier version、policy inputs 和 JSON output。
- `R8-RS05-C05`: D1/D2 没有证据升级 Git、GitHub、Codex 或最终批准角色。

Discovery high-impact delta：`none`。下列为 major executable refinements，不是高影响决定反转：

1. future machine gate 分离 caller/source 与 signer workflow。
2. future evidence package 保存 bundle、trust-root/verifier/policy receipts。
3. policy 不把 workflow-controlled predicate 当权威语义事实。

### Stability-stage deltas

- S1：新增 high-impact failure class `R8-RS05-DELTA-S1-VALID-ATTESTATION-COMPROMISED-PIPELINE`。有效且匹配预期 hosted builder、repository、workflow 的 attestation 可与 compromised pipeline 共存；identity policy 不能证明 artifact 未被破坏或语义符合意图。
- S1 executable effect：未来 gate 还必须关联同一 run 的成功 conclusion 与 artifact，并显式审查 cache、untrusted code、OIDC exposure 和 build-environment trust；这些仍是必要非充分控制。
- S2：没有新增 high-impact delta；确认 Link `command` / `materials` 和 Statement `predicate` 可选，必须 fail closed。
- S3：没有新增 high-impact delta；新增 operational probe：在线 bundle fetch 可能需要 authentication 并受 rate limit 影响，而显式 `--bundle` 的 local verification 可不依赖 GitHub authentication。保存 bundle 并隔离最小权限 fetch。

## 7. Atomic claim ledger

以下 verdict 均为 **author entailment**，不是 independent verdict。

### R8-RS05-C01 — Exact policy is necessary, not sufficient

- topic_id: `RS-05`
- claim_text: future positive provenance receipt 只有在 artifact digest、repository、OIDC issuer、workflow/certificate identity、signer repository/workflow/digest、source digest/ref、predicate type 与 hosted-runner policy 全部满足时才具有本项目定义的来源意义；即使全部满足，也不证明语义正确。
- impact: `decisive`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`, `OPENSSF-MINI-SHAI-HULUD`
- source_snapshot_ids: `RS05-SRC-GH-DOC-LIVE`, `RS05-SRC-GH-CLI-MANUAL-LIVE`, `RS05-SRC-OPENSSF-MINI-SHAI-HULUD`
- source_ranges: GitHub Docs HTML `20-25`, `46-51`; CLI HTML `7395-7438`, `7464-7509`, `7514-7596`; OpenSSF HTML `895-929`.
- author_entailment: documented flags/identity fields are directly supported；exact conjunction is a conservative project policy；“not sufficient” is supported by S1 counterexample.
- limitations: no actual artifact/bundle was available to exercise the conjunction；future exact expected values must be frozen before verification.
- decision_effect: retain `github_issued_workflow_provenance`; current state `designed_not_observed`.

### R8-RS05-C02 — Certificate/timestamps do not make predicate true

- topic_id: `RS-05`
- claim_text: GitHub CLI 文档只把 `signature.certificate` 与 `verifiedTimestamps` 描述为不能被 originating workflow 操纵的值，并明确警告 workflow execution context 可伪造 `statement.predicate`。
- impact: `decisive_counterevidence`
- evidence_cluster_ids: `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `RS05-SRC-GH-CLI-MANUAL-LIVE`
- source_ranges: CLI HTML `7464-7509`.
- author_entailment: `directly supported`
- limitations: 这不表示每个 predicate 都是 false；它限制 receipt 单独能蕴含什么。
- decision_effect: attestation 不得被写成 command correctness、test correctness、review correctness 或 investment-design semantics 的证明。

### R8-RS05-C03 — Caller/source and signer are distinct identities

- topic_id: `RS-05`
- claim_text: reusable workflow 生成 attestation 时，actual reusable workflow 是 signer；repository/source identity 与 signer workflow identity 必须分别冻结和验证。
- impact: `major`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `RS05-SRC-GH-DOC-LIVE`, `RS05-SRC-GH-CLI-MANUAL-LIVE`
- source_ranges: CLI HTML `7410-7438`; GitHub reusable-workflow result documented in D1 rank `3`.
- author_entailment: `directly supported`
- limitations: identity separation 不证明两个 controller 是组织上独立的。
- decision_effect: future policy separate `source-*` and `signer-*`; no fake threshold independence.

### R8-RS05-C04 — Durable verification needs preserved local inputs

- topic_id: `RS-05`
- claim_text: durable receipt 应保存 exact artifact、bundle、trust-root/version context、verifier version、policy inputs 与 JSON output；hosted attestation deletion、root rotation/staleness 与 authenticated fetch burden 使 live lookup 不能成为唯一证据。
- impact: `major`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`, `GH-CLI-ISSUE-11803`
- source_snapshot_ids: `RS05-SRC-GH-CLI-MANUAL-LIVE`, `RS05-SRC-GH-CLI-ISSUE-11803`, `RS05-SRC-GH-CLI-ISSUE-11803-COMMENTS`
- source_ranges: CLI HTML Loading Artifacts section；issue JSON body；comments local lines `261`, `402`, `449`, `645`.
- author_entailment: mechanics directly supported；package conjunction is conservative reproducibility design.
- limitations: saved trust root does not provide permanent revocation knowledge；saved bytes do not prove semantics.
- decision_effect: defer real evidence package to main agent’s machine gate.

### R8-RS05-C05a — Git is only a content snapshot anchor

- topic_id: `RS-05`
- claim_text: commit `7824a63...`, tree `7cb2268...`, preregistration blob `0feba28...` and file SHA-256 fix the counted-search boundary bytes.
- impact: `decisive`
- evidence_cluster_ids: `LOCAL-GIT`, `LIVE-GITHUB-COMMIT`
- source_snapshot_ids: `RS05-SRC-GH-COMMIT-BOUNDARY`
- source_ranges: boundary receipt preregistration section；commit API fields `sha`, `commit.verification`, `parents`.
- author_entailment: `deterministically supported`
- limitations: GitHub says commit `unsigned`; author/committer strings do not prove independent identity.
- decision_effect: name stays `content_snapshot_anchor`.

### R8-RS05-C05b — GitHub layer remains designed_not_observed

- topic_id: `RS-05`
- claim_text: boundary tree 有 workflow design，但 exact-SHA Actions API 返回 `total_count: 0`；没有 artifact、attestation bundle、positive policy JSON 或 negative receipts。
- impact: `decisive`
- evidence_cluster_ids: `LIVE-GITHUB-RUNS`, `LOCAL-GIT-WORKFLOW`
- source_snapshot_ids: `RS05-SRC-GH-RUNS-BOUNDARY-NORESULT`, `RS05-SRC-GH-WORKFLOWS-LIVE-NORESULT`
- source_ranges: both complete API responses；boundary workflow content/blob receipt.
- author_entailment: `deterministically supported at retrieval time`
- limitations: high-drift live state；a later machine run will change it.
- decision_effect: `github_issued_workflow_provenance: designed_not_observed`.

### R8-RS05-C05c — Codex review naming cannot be upgraded

- topic_id: `RS-05`
- claim_text: 固定的五个 R8 query 没有产生新证据把 separate-thread review 升级为安全隔离、密码学 reviewer 或组织级独立 reviewer。
- impact: `decisive_scope_guard`
- evidence_cluster_ids: `R8-RS05-COMPLETE-QUERY-SET`
- source_snapshot_ids: five query receipts and discovery freeze.
- source_ranges: complete D1, D2, S1, S2, S3 visible result ledgers.
- author_entailment: bounded absence statement limited to preregistered query set.
- limitations: 不是关于所有 Codex 内部能力的 universal claim。
- decision_effect: name stays `platform_observable_separate_thread_review`.

### R8-RS05-C05d — Javen retains final decision

- topic_id: `RS-05`
- claim_text: machine receipt 与 AI review 都只是输入，不能自动批准；最终决定保留给 Javen。
- impact: `decisive_normative_boundary`
- evidence_cluster_ids: `R8-PREREGISTRATION`
- source_snapshot_ids: preregistration file at SHA-256 `613f2feb...`.
- source_ranges: RS-05 `r7_decisions_under_review` and round closure boundaries.
- author_entailment: direct normative rule from preregistration/user boundary.
- limitations: not an empirical claim about human accuracy.
- decision_effect: name stays `human_final_decision_by_Javen`.

### R8-RS05-C06 — Expected identity can coexist with compromised pipeline

- topic_id: `RS-05`
- claim_text: S1 的独立事件分析报告了 cryptographically valid attestations，且 builder、repository、workflow 指向预期值，但 pipeline 已被 cache poisoning、untrusted code 与 OIDC token extraction 破坏。
- impact: `decisive_counterevidence`
- evidence_cluster_ids: `OPENSSF-MINI-SHAI-HULUD`, `SLSA-V1.2-STANDARD`
- source_snapshot_ids: `RS05-SRC-OPENSSF-MINI-SHAI-HULUD`, `RS05-SRC-SLSA-V1.2-THREATS-PIN`
- source_ranges: OpenSSF HTML `895-929`; SLSA lines `460-615`.
- author_entailment: directly supported as a reported public counterexample and standard threat classes.
- limitations: article analysis is not a universal incidence study；the report does not claim GitHub’s platform was universally compromised.
- decision_effect: exact identity policy is necessary-not-sufficient；same-run conclusion/artifact linkage and separate semantic review remain required.

### R8-RS05-C07 — Typed attestation does not imply complete materials or command

- topic_id: `RS-05`
- claim_text: in-toto Link `command` 和 `materials` 可选，Statement `predicate` 可省略或为空；因此 predicate type 与 signature 不能自动证明 materials complete、command truthful 或 evidence present。
- impact: `major_counterevidence`
- evidence_cluster_ids: `IN-TOTO-ATTESTATION-SPEC`
- source_snapshot_ids: `RS05-SRC-INTOTO-LINK-PIN`, `RS05-SRC-INTOTO-STATEMENT-PIN`
- source_ranges: Link lines `24-33`, `68-95`; Statement lines `35-66`.
- author_entailment: `directly supported`
- limitations: optional 不等于 always omitted；consumer policy 可以要求更严格字段。
- decision_effect: fail closed on every project-required field；do not infer completeness.

## 8. Counterevidence and contradictions retained

1. GitHub Docs 的高层“provenance/integrity”语言与同页 security warning 必须共同解释；warning 明确说 attestation 不是 artifact secure 的保证。
2. CLI manual 明确：只有 certificate 与 verified timestamps 不能被 originating workflow 操纵；predicate 可被 compromised workflow context 伪造。
3. OpenSSF incident analysis：expected builder/repository/workflow check 可通过，而 artifact 仍来自 compromised pipeline。这个反例禁止把精确 identity policy 升级为 semantic correctness。
4. SLSA v1.2：owner compromise、cross-build influence、signing-secret theft、cache poisoning、platform-admin compromise、expectations tampering 与 provenance de-listing 都是显式边界。
5. in-toto：materials、command 或 predicate 可缺失/为空；schema authentication 不等于 completeness。
6. `cli/cli#11803`：在线 fetch 的 authentication/rate-limit burden 是实际用户失效探针；同一 thread 也给出 `--bundle` local verification 的限定性 workaround，不能只保留负面一半。
7. `cli/cli#9602` 已 `closed/completed`，current manual 和 local `gh 2.95.0` 已显示 `--source-ref`、`--source-digest`、`--signer-digest`；旧 issue 不能冒充当前缺失 flag。
8. boundary commit 为 `unsigned`；Git 字段不证明人类或 reviewer identity。
9. boundary workflow 文件存在，但 no-run receipt 为 `total_count: 0`；设计存在不等于执行发生。

没有需要通过升级 assurance 来“调和”的矛盾。所有冲突都通过缩小 claim scope、区分 identity/integrity/semantics、保留 counterevidence 解决。

## 9. Future machine-policy predicates — required, not executed here

下表是 main agent 最终 machine gate 的 **候选 contract**。`expected value` 必须在真实 verification 前冻结；本报告不运行 gate，也不伪造 observed result。

| predicate | future expected policy | R8 observed state | failure meaning |
|---|---|---|---|
| local artifact digest | verifier 对 exact local artifact bytes 计算 digest，并与 signed subject 匹配 | no artifact | reject |
| repository | exact `j-a-v-e-n/knowledge-vault`，不只用 owner scope | no bundle | reject |
| OIDC issuer | exact `https://token.actions.githubusercontent.com` | documented default only | reject |
| certificate identity / SAN | exact expected signer workflow identity；优先 exact value，不用宽 regex | no certificate | reject |
| signer repository | exact repository controlling actual signer workflow | no certificate | reject |
| signer workflow | exact `j-a-v-e-n/knowledge-vault/.github/workflows/investment-discipline-assurance.yml` for current non-reusable design；若改为 reusable workflow，必须换成 actual reusable signer | design file only | reject |
| signer digest | exact predeclared revision associated with trusted signer workflow；不得把 workflow blob SHA 与 certificate signer digest 混写 | unobserved | reject |
| source digest | exact final candidate commit；R8 preregistration commit 只有在它本身被 run 时才可作为该值 | boundary run absent | reject |
| source ref | exact intended protected ref such as `refs/heads/main` | unobserved | reject |
| predicate type | exact `https://slsa.dev/provenance/v1` | documented default only | reject |
| hosted runner | `--deny-self-hosted-runners` 且核对 certificate/result 的 runner environment；workflow `runs-on` 不是 receipt | declared `ubuntu-latest` only | reject |
| signer/source split | caller/source 与 signer 分开核对；same repo 不等于 same field | no receipt | reject |
| run conclusion | same invocation/run 必须成功；不能接受 failed run 期间发布的 artifact | no run | reject |
| artifact/run linkage | artifact、manifest、bundle、certificate invocation 必须指向同一实际 run | no artifact/run | reject |
| bundle and trust context | 保存 exact bundle、trusted-root/version context、CLI version 与 policy inputs | no bundle | reject |
| positive JSON receipt | 保存完整 `--format json` result | absent | reject |
| negative tests | wrong repository、issuer、workflow identity、signer digest、source digest、predicate type 与 self-hosted case 必须失败 | absent | reject |
| workflow-controlled predicate | 不能把 predicate 中自报字段当 independent semantic oracle；额外 policy 只消费预先定义且可验证的字段 | known limitation | semantic claim rejected |
| manifest semantics | deterministic tests 与 separate semantic review 检查内容；attestation 只绑定 bytes/origin | deferred to main/reviewer | no auto-approval |
| human approval | unresolved decision 只由 Javen 最终批准 | retained | no auto-approval |

即使上述 machine predicates 全部通过，允许的语句也只能是：预期 GitHub identity 对该 exact artifact digest 产生了可验证的 provenance receipt，并通过预先冻结的 policy。仍禁止写成“GitHub 是 independent executor”“artifact 安全”“review 密码学独立”或“设计语义正确”。

## 10. Final trust-model terms

| layer | allowed term | observed status | prohibited upgrade |
|---|---|---|---|
| Git | `content_snapshot_anchor` | observed for R8 preregistration bytes | signed identity、independent author、tamper-proof semantics |
| GitHub | `github_issued_workflow_provenance` | `designed_not_observed` | independent executor、owner-independent safety、semantic correctness |
| Codex | `platform_observable_separate_thread_review` | inherited candidate; no R8 upgrade evidence | secure isolation、cryptographic reviewer、organizational independence |
| final decision | `human_final_decision_by_Javen` | retained normative boundary | automatic AI/machine approval |

组合语义：

```text
content_snapshot_anchor
+ future exact github_issued_workflow_provenance receipt
+ platform_observable_separate_thread_review
+ separate semantic entailment review
+ human_final_decision_by_Javen
```

这些层互补，但不能相互“传递升级”为独立性或语义保证。

## 11. Stability assessment

- discovery freeze: `2026-07-25T16:21:43Z`
- last high-impact delta: `R8-RS05-DELTA-S1-VALID-ATTESTATION-COMPROMISED-PIPELINE`
- later reserved queries: `R8-RS05-S2`, `R8-RS05-S3`
- S2 new high-impact failure class: `no`
- S2 decision reversal: `no`
- S2 open critical/major contradiction: `none`
- S3 new high-impact failure class: `no`
- S3 decision reversal: `no`
- S3 open critical/major contradiction: `none`
- final query adds high-impact delta: `no`
- sixth query: `not executed`
- stability passing rule: `pass`

因此不是“最后一个 delta 后无后续稳定查询”的情形；S1 后有 S2 与 S3。`bounded_incomplete` 的原因是其他 closure predicates，而不是 stability failure。

## 12. Residual gaps and reopen triggers

### Residual gaps

1. 没有独立逐 claim entailment review；作者不能填 `entailed` 充当独立 verdict。
2. 最新 RS-05 raw report/evidence 进入最终 integration commit 后的 ancestry 尚需主代理重验。
3. 没有真实 Actions run、artifact、manifest、attestation bundle、trusted-root receipt、positive verification JSON 或 negative policy tests。
4. live GitHub Docs、CLI manual、GitHub API 状态、issue 状态与 `gh` flags 都是高漂移来源。
5. OpenSSF 事件分析是强 counterexample，不是 universal incidence estimate；其事件事实没有在本 topic 内独立法证复核。
6. workflow 声明 `ubuntu-latest` 与按版本安装工具，不构成 hermetic/reproducible guarantee；本 topic 没有执行或审计 runner image/dependency closure。
7. same-run successful conclusion/artifact linkage 尚无实现 receipt。
8. Codex separate-thread review 的内容绑定、导出签名、trust root 与离线 verifier 语义没有由本轮五个 query 建立。
9. Javen 最终决定仍是 deliberate human boundary，不是 correctness oracle。

### Reopen triggers

- GitHub Actions、artifact attestations、GitHub CLI flags/defaults、OIDC certificate fields 或 runner semantics 变化。
- `actions/attest`、workflow revision、source branch/ruleset 或 trust-root 变化。
- `cli/cli#11803` 关闭、行为改变，或 bundle fetch/authentication policy 变化。
- 新的 cache poisoning、OIDC theft、reusable-workflow interference、predicate/subject manipulation 或 false-positive verification counterexample。
- real machine gate 的 positive/negative receipt 与本报告的 candidate policy 不一致。
- independent reviewer 对任何 decisive claim 给出 `not_entailed` 或 decision-changing contradiction。
- Codex 提供新的可导出、内容绑定、可验证 reviewer-attestation mechanism；在实证前仍不得升级名称。

## 13. Topic closure predicates

| preregistered predicate | author assessment | evidence / blocker |
|---|---|---|
| preregistration commit、file hash、ancestor relation、retrieval time | `partial_pass_pending_final_integration_commit` | commit/hash/time pass；目前观察到的 evidence commits ancestry pass；最终 report/evidence commit 需主代理重验 |
| five query IDs each exactly once or explicit failure receipt | `pass` | five single-call receipts；no extra query |
| all visible results screened and uniquely attributed | `pass_with_backend_scope_caveat` | complete rank ledgers in five receipts；no latent-corpus completeness claim |
| required snapshot classes saved with bytes and hashes | `pass` | manifest validated；current GitHub docs、versioned standards、independent issue/no-run receipt saved |
| every decisive claim independently reviewed | `fail_pending` | no separate reviewer；author did not self-review |
| contradictions/counterevidence retained with decision effect | `pass` | GitHub warning、CLI predicate limit、OpenSSF incident、SLSA threats、in-toto omissions、issues retained |
| stability passing rule | `pass` | S1 delta followed by S2 and S3 with no later high-impact delta |
| architecture/decision delta mapped to contract/test/gate/defer/rejection | `pass_author_design` | future machine-policy matrix and explicit defer/reject semantics |
| residual risk and reopen triggers explicit | `pass` | section 12 |

## 14. Final status

`RS-05 = bounded_incomplete`.

这是 protocol-correct 的降级，不是证据失败：

- stability 已通过；
- required snapshots 已满足；
- R7 候选术语得到强化而不是升级；
- S1 增加了一个真实高影响反证类，并在后续两次 reserved queries 后稳定；
- 但 author-only closure 被预注册明确禁止，最终 integration ancestry 与真实 machine receipts 也尚未完成。

主代理下一步应当：

1. 将本报告和 manifest 纳入最终 evidence commit 后重跑 ancestry。
2. 交给与作者分离的 reviewer，以本报告 SHA-256 和 exact source ranges 为输入逐 claim 出 verdict。
3. 在最终 machine gate 执行真实 workflow、保存 artifact/bundle/JSON，并做全部正负 policy tests。
4. 把 machine receipt 与 independent semantic review 作为输入交给 Javen；不自动批准。

