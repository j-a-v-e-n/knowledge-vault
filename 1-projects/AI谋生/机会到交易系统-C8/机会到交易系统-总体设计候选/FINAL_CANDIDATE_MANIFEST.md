# 总体设计终审候选说明

- Candidate ID：`OTTS-DESIGN-20260727-C8`
- 状态：`SUCCESSOR-BLOCKED-PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- canonical manifest：`FINAL_CANDIDATE_MANIFEST.json`
- 允许的最强候选结论：仅在终审通过和外部 closure decision 生效后，进入 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 定义的本地、零外部副作用 shadow MVP 实现

## Manifest 的角色

canonical JSON 逐文件绑定：

- 研究协议、访谈核查、Claim/RQ/DD、总体设计、来源日志与 closure matrix；
- SSP-1.0 Run2 的协议、raw responses、双方 sealed ledgers、两次 joint、S2 independent receipt、lead final-status object、完整 CE-IN JSONL、exact final-status independent acceptance receipt、两个验证器与两组负向测试；原 receipt 的 C7 reviewed paths 保持不变，C8 verifier 只在另一层机械证明本地副本与被接受 hashes 相同，不改写或扩大独立审查范围；
- 只读 Action Envelope、旧实现差距审计、外部旧根隔离记录和所有用户可能误读的历史入口警告；
- C1–C7 的实际 `FAIL`/PASS 边界、两次 Run2 semantic remediation、C7 exact final review/governance 与 C7 Shadow `FAIL` 保存在 `FINAL_REVIEW_HISTORY.md` 和 `C7_SHADOW_FAILURE_RECORD.md`，不能被 successor 替换静默覆盖；
- C6 pre-freeze Python Capability Gate 的两份 `FREEZE BLOCKED / NO-GO` 静态审查、被审 exact hashes 与 declarative IR 根因修订也保存在同一历史；该草案没有形成 candidate manifest 或任何 PASS；
- shadow declarative capability policy、exact-snapshot interpreter、窄而闭合的 OpportunityRecord 领域验证、PASS/REJECT 双类验收、macOS 隔离防御增强、资源边界与对抗测试；这些只是未来 data-only shadow 的局部机械边界，不是实现或外部授权；
- `C6_SANDBOX_PROBE_REPORT.md` 保存当前 host 的 exact profile、拒绝探针、same-process exec 与 inherited-FD 反例及 non-claims；它是 platform-bound evidence，不是 portable attestation；
- 旧 raw/筛选、旧 runtime/test/Pilot 和其并发变化仍保留在外部 sibling `机会到交易系统/`，但不再进入本候选 inventory，也不成为本候选依赖或权威证据。

JSON manifest 不包含自己，避免自引用哈希。最终 independent review receipt 必须绑定 canonical JSON 的外部 SHA-256，并核对所有 inventory path、hash、role、authority status 与 dependency。本候选的历史旧代码和失效 Run1/C1/C2/C3 原件保存在外部旧根或不可承重历史文件中，不用 `historical_exclusions` 把外部可变字节重新拉入 candidate root。

## 阶段命名空间

- 本目录 `机会到交易系统-总体设计候选/` 是 `candidate_inventory_root`；候选 manifest 对这里除自身以外的全部文件做零漏项检查。
- `机会到交易系统-闭合记录/` 是预声明的 governance sibling root；只在 exact candidate final review PASS 后创建。
- `机会到交易系统-shadow-mvp/` 是预声明的 implementation sibling root；只在 governance root 自身闭合且 closure decision 为 `CONDITIONALLY_READY` 后创建。
- `机会到交易系统-shadow-review/` 是预声明的独立实现审查 sibling root；只在 exact shadow snapshot 已形成后创建，并要求 caller 提供 exact receipt hash。
- 三个后闭合 root 与候选 inventory 不重叠，不属于设计快照；分别使用 canonical governance、shadow 与 shadow-review manifests，绑定完整父链并覆盖各自 root 文件。

C1 曾把未来实现放在 candidate inventory 内，使正常开工反向破坏设计复验；C2 又暴露 candidate node-type、shadow 自称状态和 test bytecode 污染问题；C3 暴露不完整 CE-IN crosswalk、final-status 独立同意缺失，以及旧 runtime 并发变化会污染设计快照；C4 的研究语义通过，但 freeze report 与 final receipt 的生产/消费 schema 不一致，无法进入 governance Gate；C5 同时因文档化 post-closure 入口的 bytecode 自污染和 Capability Gate 只认 self-claim/hash 而失败。最初 C6 pre-freeze 草案仍尝试用 AST/audit hook 执行 arbitrary Python，被两份独立静态审查阻断；declarative iteration A 又因同 UID staged-path substitution、末端 snapshot、partial TCB、可放大资源策略和虚假的 host-test 绿色证明被拒绝。Iteration B 改用 data-only closed declarative IR、opened-and-unlinked descriptor、固定结构性资源上限、私有临时 digest-addressed CAS 和分层 runtime evidence，并取得真实 host-required suite 与 exact-byte 代码/接口 `PASS`、无 Critical/Major。随后形成的 C6 exact manifest/freeze 仍因 Run2 direct Claim bridge 的语义 overreach 被完整终审拒绝；attempt 1 再暴露五项过度关系，attempt 2 才由两份只读审查以 exact bytes 接受。C7 完整 RC-26 review 与限定 governance 通过，但 post-closure Shadow 实现审查反证冻结 IR 无法执行 Action Envelope 的领域语义完成定义。C8 因此保留 C7 原件和拒绝快照，修订 policy/runner/verifier 和拒绝型 acceptance contract，并必须重新接受尚待完成的完整 RC-26 review。同 UID/管理员并发抵抗、完整 dylib/host TCB 与 Darwin 进程级 memory/RSS 硬限制仍明确不声称闭合。`sandbox-exec` 只作为当前 Mac 的 deprecated/unsupported defense-in-depth，不承担跨平台证明。候选不使用 ignore glob，也不允许在 freeze 时提前创建任何 post-closure sibling root。

## 机械验证

从本目录运行：

```bash
python3 -B 研究/2026-07-27-总体设计/verify_run2_crosswalk.py
python3 -B 研究/2026-07-27-总体设计/test_run2_crosswalk.py -v
python3 -B 研究/2026-07-27-总体设计/verify_run2_acceptance.py
python3 -B 研究/2026-07-27-总体设计/test_run2_acceptance.py -v
python3 -B 研究/2026-07-27-总体设计/test_shadow_acceptance.py -v
# 上一命令的 host positive-path 在受管 sandbox 内必须显式 SKIP，不能当作 host PASS。
# C8 冻结前还必须在允许嵌套 sandbox-exec 的真实主机上下文单独运行：
OTTS_REQUIRE_HOST_SANDBOX=1 python3 -B 研究/2026-07-27-总体设计/test_shadow_acceptance.py -v
python3 -B 研究/2026-07-27-总体设计/test_phase_manifests.py -v
python3 -B 研究/2026-07-27-总体设计/build_candidate_manifest.py
python3 -B 研究/2026-07-27-总体设计/verify_candidate_manifest.py FINAL_CANDIDATE_MANIFEST.json --phase freeze
python3 -B 研究/2026-07-27-总体设计/build_freeze_report.py FINAL_CANDIDATE_MANIFEST.json \
  --output /private/tmp/OTTS-DESIGN-20260727-C8-FREEZE_VERIFICATION_REPORT.json
```

验证器 fail closed：未知字段、路径逃逸、重复 path、active/historical 重叠、非规范 SHA-256、缺失文件、hash mismatch、未知依赖、manifest 自包含、候选期提前出现的 post-closure root 或重叠/非精确 root 都会失败。

测试在系统临时目录构造 synthetic candidate/governance/declarative-shadow/review，不创建真实 sibling root；入口自身即使漏写 `-B` 也在 local import 前禁用 bytecode 写入。除既有 crosswalk、receipt、inventory、governance 与 phase-boundary 负向路径外，Capability Gate 测试还必须覆盖 IR exact schema/typed DAG、未知 opcode、代码或 native artifact、snapshot mutation、路径与 URI 数据注入、CAS digest round-trip/corruption、资源上限、OS sandbox 外部读写/网络/进程拒绝、bounded logs/timeout 和全部报告绑定。manifest builder 只接受显式声明的闭集文件，不会把意外文件自动吸收为候选；freeze-report builder 拒绝写入 candidate inventory 或覆盖不同的已有报告。

final PASS 后，governance 或 shadow root 使用另一验证器。下列命令从 C8 container 目录（即候选目录的父目录）运行，不是从候选目录内运行：

```bash
python3 -B 机会到交易系统-总体设计候选/研究/2026-07-27-总体设计/verify_post_closure_manifest.py \
  机会到交易系统-总体设计候选/FINAL_CANDIDATE_MANIFEST.json \
  --governance-manifest 机会到交易系统-闭合记录/GOVERNANCE_ARTIFACT_MANIFEST.json \
  --expected-closure-decision-sha256 <authority-supplied-exact-hash> \
  [--shadow-manifest 机会到交易系统-shadow-mvp/SHADOW_ARTIFACT_MANIFEST.json \
   --shadow-review-manifest 机会到交易系统-shadow-review/SHADOW_REVIEW_MANIFEST.json \
   --expected-shadow-review-receipt-sha256 <caller-supplied-exact-hash>]
```

这是唯一的 post-closure aggregate Gate。它复验父候选、freeze report、独立 review receipt、`CONDITIONALLY_READY` decision、外部提供的 decision exact hash、Action Envelope、governance 完整 inventory；shadow 已出现时还复验其 data-only closed IR、read-once snapshot ledger、policy、artifact SBOM、capability/runtime reports、合成 acceptance cases 与向上 hash 链。没有 shadow review root 时只能输出 observed/unreviewed 状态；只有 caller-bound exact shadow receipt 完整闭合，才可接受限定的 local declarative candidate。任何单根 verifier 或 root 内自填的 status 都不签发权限；输出始终包含 `external_action_authority=false`，并明确不声称 host-level universal noninterference、deployment 或 production safety。

机械通过只证明候选身份闭合，不证明研究判断正确。最终 reviewer 还必须检查语义：证据是否被过度外推、Run2 限定状态是否被扩大、架构反证是否在当前候选仍闭合、旧原型是否真正隔离、商业未知是否被保留，以及只读权限是否存在任何现实副作用逃逸路径。

## 当前禁止

在 manifest-bound final review、governance root 闭合与外部 closure decision 之前，不得建立 shadow sibling root 或开始新 runtime 实现。无论终审结果如何，本候选都不授权选择或声称验证某个真实行业/Pilot，不授权网络采集、联系、发送、发布、报价、签约、账户、凭据、付款、收款、客户数据写入、部署或 production Harness。
