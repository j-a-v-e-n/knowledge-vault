# 保障 provenance 专项刷新｜2026-07-25

状态：`candidate-research`

服务的决定：在个人、本地、纸面项目中，怎样避免把构造者自报的 reviewer、命令和结果误称为独立验收，同时不伪造当前工具并不存在的组织级独立性。

## 触发反例

固定候选 `0683a9c3b8d25854b08750641a62f88b4f86560c` 的三路只读审查发现：

1. passing review 的主体、参与历史和 locator 都可由构造者写入；
2. raw attack 的 command、退出码和 stdout 可手写，验证器只检查内部哈希一致；
3. Codex 子代理线程确实与主线程分离，但仓库内尚无来自平台的、绑定审查内容的可验证签名。

因此“内容寻址”与“来源可信”必须拆开。

## 当前外部能力核对

### Codex 子代理

OpenAI 当前手册说明：子代理各自执行模型与工具工作，Codex App 会展示每个子代理线程，用户可以打开线程检查过程与返回主线程的结果。它支持**平台可观察的上下文隔离**。

手册没有给出可由本项目离线验证的、绑定 `subject + prompt + response + candidate commit/tree` 的子代理签名格式。App-server 文档提到桌面宿主可返回 opaque upstream attestation token，但没有公开其内容绑定、导出或本项目验证语义，因此不能把它扩大解释为审查回执。

来源：

- [OpenAI Codex manual — Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents.md)
- [OpenAI Codex manual — App server](https://learn.chatgpt.com/docs/codex-sdk/app-server)

### GitHub Actions artifact attestations

GitHub 官方资料说明：公开仓库在当前计划中可使用 artifact attestations；GitHub Actions 通过 OIDC 和 Sigstore 为产物生成签名 provenance，并绑定 repository、workflow、commit SHA 和触发事件。验证者仍须检查签名者身份和 policy；attestation 证明“从哪里、怎样生成”，不证明内容本身正确。

当前仓库只读实测：

- repository：`j-a-v-e-n/knowledge-vault`
- visibility：`PUBLIC`
- default branch：`main`
- Actions：enabled
- allowed actions：all
- default workflow token：read

来源：

- [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- [Using artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations)
- [GitHub attestation REST API](https://docs.github.com/en/rest/repos/attestations)

### Sigstore、in-toto 与 SLSA

Sigstore keyless signing 用 OIDC 身份取得短期证书，用临时密钥签名，并把公开签名写入透明日志；验证时必须同时验证 artifact digest、issuer 和预期 identity。

in-toto 把预先定义的 layout、被授权 functionary、实际命令、材料/产物和签名 link 分开；threshold 只有在不同 functionary key 真正独立时才增加信任。

SLSA 把 provenance 定位为构建来源证明，并明确需要评估 build platform；provenance 本身不证明产物正确。

来源：

- [Sigstore security model](https://docs.sigstore.dev/about/security/)
- [Sigstore signature verification](https://docs.sigstore.dev/cosign/verifying/verify/)
- [in-toto getting started](https://in-toto.io/docs/getting-started/)
- [in-toto metadata model](https://in-toto.readthedocs.io/en/latest/model.html)
- [SLSA build provenance](https://slsa.dev/spec/v1.2-rc2/build-provenance)

## 采用的信任模型

当前个人 Paper V1 采用两层证据，不再用一个 `independent=true` 覆盖不同主张。

### A. 外部签名的机器执行 provenance

GitHub Actions 在固定 commit 上运行冻结的 assurance runner，生成一个包含命令、候选、tree、workflow、目标/包装退出码、原始输出哈希和总裁决的 manifest；GitHub/Sigstore 对该 manifest 做 artifact attestation。

本地与 fresh-clone 发布谓词必须验证：

- manifest digest；
- GitHub OIDC issuer；
- 精确 repository；
- 精确 workflow identity；
- 精确 commit；
- 所有必需检查确实由 runner 执行；
- 目标退出码与 harness 退出码分离。

它只证明机器执行 provenance，不批准语义设计。

### B. 平台可观察的语义审查

只读 Codex 子代理在候选固定后、隔离上下文中审查原始意图、研究、设计、实现与原始结果；记录 agent locator、完整输入/输出哈希、候选 commit/tree、参与历史、novelty probe 和 findings。

本层的当前强度是 `platform_observable_context_isolation`，不是 `cryptographically_independent_reviewer_identity`。用户可在 Codex App 打开对应子代理线程核对；仓库内验证器只能验证绑定与完整性，不能证明平台身份。

### C. 明确不在当前证明范围

当前不声称抵御：

- 主代理、所有子代理、GitHub、OpenAI 平台与仓库 owner 串通；
- 同一 OS 管理员或恶意软件改写所有本地状态；
- 组织级职责分离；
- 审查者人类身份的密码学证明。

如果未来进入真实资金、多人服务或商业发布，必须升级为独立 GitHub/Git identity、required review/ruleset、受保护的签名 functionary 或等价第三方保证；当前 Paper V1 的证据不得复用为该结论。

## 对治理设计的直接要求

1. 删除“自报 reviewer 字段即可通过”的语义；final verdict 必须同时依赖外部签名机器 receipt 与平台可观察审查记录。
2. raw attack 由固定 runner 实际执行并输出结构化 receipt，不接受任意 command 字符串作为权威。
3. canonical regression 与候选固定后 reviewer 新增的 novelty probe 分开保存。
4. 最终审查范围自动展开原始意图、决定、方法主体、research primary artifacts、冻结规范、实现目标和测试。
5. 研究 stop rule 由机器可读的检索/纳入/排除/来源簇/补充轮/架构差异 receipt 推导，不允许手工翻转布尔值。
6. 完成报告必须使用与实际 assurance level 相符的名称；不能把 `platform_observable_context_isolation` 写成组织级或密码学独立。

## 仍有条件

GitHub Actions attestation 只有在真实 workflow 首次运行、产物被下载并经 `gh attestation verify` 核对后才能从“设计候选”升级为“已观察能力”。在此之前不得声称外部机器 provenance 已通过。
