## Research result: RESEARCH-REFRESH-R7 / RS-05

状态：`bounded_incomplete`。预注册 commit 的远端时间为 `2026-07-25T15:40:02Z`，首个 counted query 为 `2026-07-25T15:43:23Z`，满足先提交后检索。未写入任何文件。

核心结论：Paper V1 可以组合“固定 Git 快照 + GitHub 签名的 workflow provenance + 可打开的 Codex 子代理审查线程”，但只能称为内容绑定、平台来源和可观察审查；当前不能称为独立执行、独立 reviewer 或语义正确证明。

### Sources consulted

- [预注册 commit](https://github.com/j-a-v-e-n/knowledge-vault/commit/3a1bbe4565006745fb3c458066e08a4640c31268) — 固定 RS-05 问题、预算、禁止捷径与停止条件。
- [OpenAI Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md) — 子代理线程、可检查活动及继承权限。
- [OpenAI App Server initialization](https://learn.chatgpt.com/docs/app-server#initialization) — `requestAttestation` 只公开描述为 opaque token。
- [actions/attest](https://github.com/actions/attest) — `actions/attest@v4` 的 subject、predicate、Sigstore 和输出语义。
- [gh attestation verify](https://cli.github.com/manual/gh_attestation_verify) — identity/policy flags 及 malicious workflow 限制。
- [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations) — provenance 能力、验证要求及“不保证安全”边界。
- [Sigstore security model](https://docs.sigstore.dev/about/security/)、[threat model](https://docs.sigstore.dev/about/threat-model/)、[verification](https://docs.sigstore.dev/cosign/verifying/verify/) — identity、issuer、透明日志与不保证可信身份。
- [SLSA v1.2 assessing build platforms](https://slsa.dev/spec/v1.2/assessing-build-platforms) — builder/control plane/maintainer/admin 威胁边界。
- [in-toto getting started](https://in-toto.io/docs/getting-started/) — layout、functionary、link、材料/产物及签名范围。
- GitHub REST 与本机 `gh 2.95.0` — 当前仓库设置、Actions runs、commit verification 的实际 receipt。

### Exact counted queries + UTC

| ID | UTC | Exact query |
|---|---|---|
| Q1 | `2026-07-25T15:43:23Z` | `Codex subagents thread inspection observability` |
| Q2 | `2026-07-25T15:44:10Z` | `Codex app server attestation token` |
| Q3 | `2026-07-25T15:44:37Z` | `site:github.com/actions/attest "v4" artifact attestation README` |
| Q4 | `2026-07-25T15:44:37Z` | `site:cli.github.com/manual/gh_attestation_verify "cert-identity" "signer-workflow"` |
| Q5 | `2026-07-25T15:44:37Z` | `site:docs.github.com artifact attestations malicious workflow owner limitations` |
| Q6 | `2026-07-25T15:44:37Z` | `site:slsa.dev/spec provenance threat model malicious build platform` |
| Q7 | `2026-07-25T15:44:55Z` | `site:docs.sigstore.dev keyless signing verify certificate identity issuer security model` |
| Q8 | `2026-07-25T15:44:55Z` | `(site:in-toto.io/docs OR site:in-toto.readthedocs.io) functionary threshold layout link signatures` |

Q3–Q6、Q7–Q8 的搜索后端返回合并结果，没有保留逐结果对应的原始 query；以下只能精确记录 batch 归属，不能事后假装恢复单条 query 归属。

### Result set screening / clusters / revision

- **OAI-OBS｜官方平台文档**
  - Q1 可恢复结果：[Glossary](https://learn.chatgpt.com/docs/glossary)、[Best practices](https://learn.chatgpt.com/guides/best-practices#organize-long-running-chats)、[Observability metrics](https://learn.chatgpt.com/docs/config-file/config-advanced#threads-tasks-and-features)、[Codex MCP server](https://learn.chatgpt.com/docs/mcp-server#running-codex-as-an-mcp-server)。
  - 决定：前三项仅作术语/可观察性背景；MCP server 与本问题间接，排除。
  - ⚠️ MCP 报告 `nbHits: 213` 并给出 cursor，但响应暴露不完整，Q1 不能满足 `record_every_result`。
  - 直接 locator [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md) 纳入。文档无公开版本号，漂移风险高。

- **OAI-ATTEST｜官方平台文档**
  - Q2 唯一结果：[App Server initialization](https://learn.chatgpt.com/docs/app-server#initialization)。
  - 决定：纳入，但只支持“opaque token 存在”；不支持 token 的内容绑定、导出、信任根或离线验证语义。

- **GH-ACTION / GH-VERIFY / GH-DOC｜官方 GitHub 簇**
  - 纳入：[actions/attest](https://github.com/actions/attest)、[CLI verify manual](https://cli.github.com/manual/gh_attestation_verify)、[artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)、[using artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)。
  - `actions/attest@v4` 在 `2026-07-25T15:47:11Z` 解析到 commit `f7c74d28b9d84cb8768d0b8ca14a4bac6ef463e6`；这是当前 major tag 解析，不是冻结 revision。tag API 返回 `verified:false`、`reason:"unsigned"`。
  - 当前实现应使用完整 action commit，而不是把 `@v4` 当固定内容身份。

- **SLSA-CURRENT｜primary standard**
  - 纳入：[v1.2 index](https://slsa.dev/spec/v1.2/)、[v1.2 provenance](https://slsa.dev/spec/v1.2/provenance)、[v1.2 assessing build platforms](https://slsa.dev/spec/v1.2/assessing-build-platforms)。
  - 历史/被取代，仅作 revision receipt：[v1.0-rc2 provenance](https://slsa.dev/spec/v1.0-rc2/provenance)、[v1.0 changes](https://slsa.dev/spec/v1.0/whats-new)、[v1.2-rc1 assessment](https://slsa.dev/spec/v1.2-rc1/assessing-build-platforms)、[v1.0 levels](https://slsa.dev/spec/v1.0/levels)、[v1.1-rc1 threats](https://slsa.dev/spec/v1.1-rc1/threats)。
  - [draft threats](https://slsa.dev/spec/draft/threats) 因 draft 状态不承载决定性 claim。

- **搜索噪声｜排除**
  - [Consumer Data Standards PDF](https://github.com/ConsumerDataStandardsAustralia/standards/files/13371203/Decision.Proposal.338.-.Banking.Products.and.Accounts.pdf)、[visual-attention PDF](https://github.com/nilumbra/pinealand/wiki/attention/A%20neuro-computational%20model%20of%20visual%20attention%20with%20multiple%20attentional%20control%20sets.pdf)、[Z-Wave PDF](https://github.com/MarkDing/IoT-Developer-Boot-Camp/wiki/files/ZW-ZWave-Boot-Camp/Lab_3A_Compile_Switch_OnOff_and_enable_debug.pdf)。
  - 原因：分别由 `v4`、`attention` 等词误召回，与 RS-05 无关。

- **SIGSTORE-CORE｜primary provenance implementation/standard**
  - 纳入：[signing overview](https://docs.sigstore.dev/cosign/signing/overview/)、[security model](https://docs.sigstore.dev/about/security/)、[verification](https://docs.sigstore.dev/cosign/verifying/verify/)、[threat model](https://docs.sigstore.dev/about/threat-model/)。
  - 支持但不新增独立簇：[overview](https://docs.sigstore.dev/about/overview/)、[blob signing](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/)、[bundle format](https://docs.sigstore.dev/about/bundle/)。
  - 排除为外围教程/实现：[installation](https://docs.sigstore.dev/cosign/system_config/installation/)、[quickstart](https://docs.sigstore.dev/quickstart/quickstart-cosign/)、[custom components](https://docs.sigstore.dev/cosign/system_config/custom_components/)、[Java client](https://docs.sigstore.dev/language_clients/java/)、[policy controller](https://docs.sigstore.dev/policy-controller/overview/)。

- **IN-TOTO｜primary standard**
  - Q8 没有返回 in-toto domain 结果；使用预先已知的直接 locator [Getting started](https://in-toto.io/docs/getting-started/)。
  - 页面标注最后修改 `December 13, 2024`；threshold 没有在该范围出现，不能从本轮来源声称具体 threshold 语义。

- **LIVE-GITHUB｜actual platform receipt**
  - `2026-07-25T15:48:59Z`：预注册 commit 的 Actions API 返回 `total_count:0`。
  - `2026-07-25T15:49:09Z`：全仓库 Actions API 返回 `total_count:0`。
  - `2026-07-25T15:50:07Z`：`enabled:true`、`allowed_actions:"all"`、`sha_pinning_required:false`。
  - `2026-07-25T15:50:15Z`：默认 workflow token 为 `read`，不能 approve PR reviews。
  - `2026-07-25T15:50:21Z`：rulesets 返回 `[]`。
  - `2026-07-25T15:50:31Z`：`main` 返回 `Branch not protected`。
  - 预注册 commit 中 `.github/workflows` 为空；因此没有正向执行 receipt 或 attestation bundle。

### Key findings

1. **Git 只能承担固定内容锚点。** `3a1bbe…` 解析到 tree `7da9a32020dab5282ef9cef7255a8b1a3fff867c`，预注册文件 blob 为 `ad50be505931939a76b45821a45ef9ee3e26ef10`。GitHub 对该 commit 返回 `unsigned`；author/committer 字段不能证明独立身份。[commit receipt](https://github.com/j-a-v-e-n/knowledge-vault/commit/3a1bbe4565006745fb3c458066e08a4640c31268)

2. **`actions/attest@v4` 可以把 artifact digest 绑定到 Sigstore 证书与 attestation。** 它支持 path、digest、checksums 和 SLSA/custom predicate；但 major tag 不是固定 revision，应冻结完整 action commit。[actions/attest](https://github.com/actions/attest)

3. **验证必须是 policy verification，不是“签名存在”检查。** 至少应约束精确 repository、OIDC issuer、workflow identity、signer digest、source digest、predicate type，并拒绝 self-hosted runner；`--repo` 单独使用只提供较宽身份范围。[CLI manual](https://cli.github.com/manual/gh_attestation_verify)

4. **恶意 workflow 或 owner 仍可签出错误内容。** GitHub CLI 明确指出 workflow 可操纵 `statement.predicate`；SLSA 也把 maintainer 修改 build configuration、platform administrator 运行任意代码纳入 threat assessment。[CLI manual](https://cli.github.com/manual/gh_attestation_verify)、[SLSA assessment](https://slsa.dev/spec/v1.2/assessing-build-platforms)

5. **Sigstore证明数字身份控制，不证明该身份可信或结果正确。** verifier 必须检查 artifact digest、certificate identity、OIDC issuer 与信任根；OIDC identity、provider、Fulcio 或日志监控仍是信任假设。[Sigstore verification](https://docs.sigstore.dev/cosign/verifying/verify/)、[threat model](https://docs.sigstore.dev/about/threat-model/)

6. **Codex 支持“可观察的独立线程”，不支持本项目可验证的 reviewer 签名。** 官方文档支持打开子代理线程检查工作；App Server 只公开 opaque token，没有建立 `prompt + response + candidate commit` 的可导出签名语义。[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)、[App Server](https://learn.chatgpt.com/docs/app-server#initialization)

7. **当前 Layer A 仍是设计候选。** 仓库没有 workflow、没有任何 Actions run、没有 attestation；同时 owner 可直接改变 unprotected `main` 和 workflow policy。因此不得声称“外部机器 provenance 已执行/通过”。

### Decisive claims: scope / entailment / limitations

- **`GIT-CONTENT-ANCHOR`｜decisive**
  - 精确范围：该 commit/tree/blob 固定本轮研究输入。
  - 证据：`git cat-file`、GitHub commit API。
  - Entailment：`entailed`，确定性检查。
  - 限制：commit unsigned；不证明 author、reviewer 或人类身份。
  - 决定：保留 Git 层，但名称限定为 `content_snapshot_anchor`。

- **`GH-ATTEST-CAPABILITY`｜decisive**
  - 精确范围：`actions/attest` 可为 artifact subject 生成 Sigstore-backed attestation。
  - 范围：[README lines 227–272](https://github.com/actions/attest)。
  - Entailment：`entailed`。
  - 限制：证明 attestation 被预期 workflow identity 签出，不证明 predicate 真实。
  - 决定：manifest 应作为被验证 artifact，而非把自报字段当权威。

- **`GH-VERIFY-POLICY`｜decisive**
  - 精确范围：actor identity 包含 repo/owner 与 signer workflow；CLI 提供 issuer、identity、workflow/source digest 和 runner policy。
  - 范围：[manual lines 542–597、605–642](https://cli.github.com/manual/gh_attestation_verify)。
  - Entailment：`entailed`；本机 `gh 2.95.0` help 与网页一致。
  - 限制：`statement.predicate` 可被 workflow 伪造。
  - 决定：禁止仅运行 `gh attestation verify --repo ...` 后声称语义通过。

- **`OWNER-CONTROL-LIMIT`｜decisive counterevidence**
  - 精确范围：maintainer 可修改源码和 build configuration；administrator 可运行任意代码。
  - 范围：[SLSA lines 57–63、70–135](https://slsa.dev/spec/v1.2/assessing-build-platforms)。
  - Entailment：`entailed`。
  - 限制：SLSA 描述通用平台评估，不断言 GitHub 当前已被攻破。
  - 决定：当前 attestation 不得命名为 owner-independent execution。

- **`IN-TOTO-MODEL`｜major**
  - 精确范围：layout 定义授权 functionary；link 记录命令、材料、产物并签名。
  - 范围：[lines 2–4、15–20、46–49、59–66](https://in-toto.io/docs/getting-started/)。
  - Entailment：基础模型 `entailed`；“同一 owner 控制的多把 key 不增加独立性”为模型推论。
  - 限制：未显式传入的文件不会记录，传入但未实际使用的文件也能被记录。
  - 决定：functionary identity 必须与真实控制边界一致，不能靠多个名称制造独立性。

- **`CODEX-OBSERVABILITY`｜major**
  - 精确范围：用户可打开 subagent thread 检查工作和返回摘要。
  - 范围：[Availability、Core terms、Managing subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)。
  - Entailment：可观察线程 `entailed`；可验证签名为 `bounded_not_established`。
  - 限制：没有公开的内容绑定、信任根、导出和离线验证格式。
  - 决定：将 `platform_observable_context_isolation` 收窄为 `platform_observable_separate_thread_review`。

- **`LIVE-EXECUTION-STATUS`｜decisive**
  - 精确范围：截至平台 receipts 的时间，仓库和该 commit 均无 Actions run。
  - Entailment：`entailed`，GitHub REST 确定性检查。
  - 限制：这是高漂移状态，未来首次 run 会改变结论。
  - 决定：机器 provenance 状态只能是 `designed_not_observed`。

### Counterevidence

- GitHub CLI：除 certificate 和 verified timestamps 外，workflow-originated statement 内容可能受 workflow 控制。
- GitHub Docs：attestation 不是 artifact 安全或语义正确保证；消费者必须定义并执行 policy。[GitHub Docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- SLSA：可信结论依赖 build platform、control plane 和隔离；maintainer/admin 是显式威胁主体。
- 实际仓库：无 ruleset、`main` 未保护、无 SHA pinning requirement、无历史 Actions run。
- in-toto：签名 link 仍可能遗漏实际使用文件，或记录未实际使用的材料。

### Trust model delta

| 层 | 本轮后允许的名称 | 本轮修订 |
|---|---|---|
| Git | `content_snapshot_anchor` | 固定 commit/tree/blob；明确 unsigned、非身份独立 |
| GitHub | `github_issued_workflow_provenance` | 当前状态加后缀 `designed_not_observed`；不得称 independent executor |
| Codex | `platform_observable_separate_thread_review` | 删除安全意义上的“context isolation”及密码学 reviewer 暗示 |
| 最终决定 | `human_final_decision_by_Javen` | machine receipt 与 AI review 都是输入，不自动批准语义 |

建议组合语义是：

`固定 Git snapshot` + `被 attested 的执行 manifest` + `精确 gh identity/policy verification` + `可打开的 Codex review trace` + `Javen 最终决定`

各层互补，但不相互升级为组织级独立性。

### Claims allowed / forbidden

当前允许：

- “RS-05 在 counted search 前由固定 commit 预注册。”
- “该 commit/tree/blob 是本轮内容快照。”
- “Codex 提供可打开的独立子代理线程。”
- “官方能力支持设计 GitHub-signed workflow provenance。”
- “当前仓库没有实际 Actions/attestation receipt。”

只有完成真实 run、下载 artifact/bundle，并通过精确 policy 与负向测试后才允许：

- “预期 GitHub Actions workflow 对该 manifest digest 生成了可验证 provenance。”
- “artifact 与预期 repository、workflow、source commit、issuer 和 predicate type 匹配。”

禁止：

- “Git author/committer 字段证明独立身份。”
- “GitHub Actions 是独立 reviewer 或抵御恶意 owner。”
- “attestation 证明命令、结果或语义正确。”
- “`--repo` 验证通过即等于完整 policy 通过。”
- “Codex locator、线程 hash 或 opaque token 是 reviewer 密码学签名。”
- “同一 owner 控制的多个 agent、workflow 或 functionary 构成 threshold independence。”
- “Paper V1 已通过外部机器 provenance”或任何 `independent=true` 总括字段。

### Stability and gaps

- **高漂移**：Codex 产品文档、`actions/attest@v4` major tag、GitHub CLI flags、仓库 settings/runs。
- **中等漂移**：GitHub/Sigstore 未版本化操作文档。
- **较稳定且版本化**：SLSA `v1.2`；in-toto 页面模型，但仍应按 reopen trigger 复核。
- 查询预算已用满，最后 trust-model delta 后没有额外稳定性轮，因此不能声称 saturation。
- Q1 结果记录被 MCP 输出截断；批量 WebSearch 没有逐结果 query attribution；严格 `record_every_result` 未完全满足。
- 决定性网页来源没有本轮可保存的内容 hash，只有 URL、范围和部分 revision receipt。
- 没有正向 Actions run、artifact、Sigstore bundle、`gh attestation verify --format json` 输出或故意错误 identity/source 的负向测试。
- 没有独立用户报告；“实际平台”类别只有本仓库的 no-result receipt。
- 因此状态保持 `bounded_incomplete`，不是 research closure。

### Verbatim quotes

> “only the `signature.certificate` and the `verifiedTimestamps` properties contain values that cannot be manipulated by the workflow”  
> ([GitHub CLI manual](https://cli.github.com/manual/gh_attestation_verify), Additional Policy Enforcement)

> “artifact attestations are not a guarantee that an artifact is secure.”  
> ([GitHub Docs](https://docs.github.com/en/actions/concepts/security/artifact-attestations), Verifying artifact attestations)

> “it can show you that a signature came from someone controlling a specific digital identity, but not whether you should trust that identity.”  
> ([Sigstore threat model](https://docs.sigstore.dev/about/threat-model/), Introduction)

> “The app surfaces each subagent thread so you can inspect its work and the summary returned to the main chat.”  
> ([OpenAI Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md), Availability)

> “Any files that are modified or used in any way during the execution of the command are not recorded in the link file”  
> ([in-toto](https://in-toto.io/docs/getting-started/), Supply-chain steps)

### ⚠️ 矛盾或不确定

- GitHub 概览称 provenance/integrity “unfalsifiable”，CLI 手册同时说明 workflow 可伪造 predicate；两者支持范围不同，不能把前者扩大到全部 statement 真实性。
- 既有候选文档称 `platform_observable_context_isolation`，官方来源只明确支持 separate/inspectable thread，没有建立安全隔离证明。
- App Server 存在 opaque attestation token，但本轮来源没有给出其内容绑定和 verifier 语义；不能推定其可用，也不能推定平台永远不存在其他内部语义。

### Suggested next step（lead 接续用）

将 assurance 名称按本摘要降级，并在后续独立执行轮生成真实 manifest、attestation bundle、精确 `gh attestation verify` JSON 与错误 identity/source 的负向 receipt 后，才重新评估 Layer A。
