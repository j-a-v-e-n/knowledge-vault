# 总体设计终审候选说明

- Candidate ID：`OTTS-DESIGN-20260727-C3`
- 状态：`CANDIDATE-PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- canonical manifest：`FINAL_CANDIDATE_MANIFEST.json`
- 允许的最强候选结论：仅在终审通过和外部 closure decision 生效后，进入 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 定义的本地、零外部副作用 shadow MVP 实现

## Manifest 的角色

canonical JSON 逐文件绑定：

- 研究协议、访谈核查、Claim/RQ/DD、总体设计、来源日志与 closure matrix；
- SSP-1.0 Run2 的协议、raw responses、双方 sealed ledgers、两次 joint、S2 independent receipt、final run status 与 Claim-Evidence crosswalk；
- 只读 Action Envelope、旧实现差距审计和所有用户可能误读的历史入口警告；
- 首次 invalid 检索运行、旧 raw/筛选、旧 runtime/test/Pilot 工件，全部作为 `historical_exclusions` 绑定而非删除。
- C1 的 phase-boundary `FAIL / MAJOR` 及其修订要求，保存在 `FINAL_REVIEW_HISTORY.md`，不能因 C2 替换而消失。

JSON manifest 不包含自己，避免自引用哈希。最终 independent review receipt 必须绑定 canonical JSON 的外部 SHA-256，并核对所有 active/historical path、hash、role、authority status 与 dependency。

## 阶段命名空间

- 本目录 `机会到交易系统/` 是 `candidate_inventory_root`；候选 manifest 对这里除自身以外的全部文件做零漏项检查。
- `机会到交易系统-闭合记录/` 是预声明的 governance sibling root；只在 exact candidate final review PASS 后创建。
- `机会到交易系统-shadow-mvp/` 是预声明的 implementation sibling root；只在 governance root 自身闭合且 closure decision 为 `CONDITIONALLY_READY` 后创建。
- 两个后闭合 root 与候选 inventory 不重叠，不属于设计快照；governance 使用 canonical `GOVERNANCE_ARTIFACT_MANIFEST.json`，shadow 使用 `SHADOW_ARTIFACT_MANIFEST.json`，二者绑定父候选 hash 并完整覆盖各自 root 文件。

C1 曾把未来实现放在 candidate inventory 内，使正常开工反向破坏设计复验；C2 又暴露 candidate node-type、shadow 自称状态和 test bytecode 污染问题。C3 不使用 ignore glob，也不允许在 freeze 时提前创建 sibling root：`freeze` 模式要求它们都不存在；`post-closure` 模式只承认 manifest 预声明的精确 sibling name，并要求已出现的 root 带有规定 manifest。

## 机械验证

从本目录运行：

```bash
python3 研究/2026-07-27-总体设计/verify_candidate_manifest.py FINAL_CANDIDATE_MANIFEST.json --phase freeze
```

验证器 fail closed：未知字段、路径逃逸、重复 path、active/historical 重叠、非规范 SHA-256、缺失文件、hash mismatch、未知依赖、manifest 自包含、候选期提前出现的 post-closure root 或重叠/非精确 root 都会失败。

冻结前的正向与负向回归：

```bash
python3 -B 研究/2026-07-27-总体设计/test_phase_manifests.py -v
```

测试在系统临时目录构造 synthetic candidate/governance/shadow，不创建真实 sibling root；入口自身即使漏写 `-B` 也在 local import 前禁用 bytecode 写入。它覆盖候选漏项、special file、hardlink、提前出现的 root、未知 activation gate、governance 漏项/symlink/hardlink、非空 major、错误 decision scope、外部 decision hash 不匹配、shadow status/authority 越界、shadow 未验证与篡改传播。

final PASS 后，governance 或 shadow root 使用另一验证器：

```bash
python3 机会到交易系统/研究/2026-07-27-总体设计/verify_post_closure_manifest.py \
  机会到交易系统/FINAL_CANDIDATE_MANIFEST.json \
  --governance-manifest 机会到交易系统-闭合记录/GOVERNANCE_ARTIFACT_MANIFEST.json \
  --expected-closure-decision-sha256 <authority-supplied-exact-hash> \
  [--shadow-manifest 机会到交易系统-shadow-mvp/SHADOW_ARTIFACT_MANIFEST.json]
```

这是唯一的 post-closure aggregate Gate。它复验父候选、freeze report、独立 review receipt、`CONDITIONALLY_READY` decision、外部提供的 decision exact hash、Action Envelope、governance 完整 inventory；shadow 已出现时还复验其全部文件、依赖和向上 hash 链。shadow 未出现时只能输出 `ABSENT_AUTHORIZED`，不能称 implementation valid。任何单根 verifier 或 root 内自填的 status 都不签发权限；输出始终包含 `external_action_authority=false`。实现测试的可变运行数据只进入系统临时目录，不混入已接受的 shadow implementation inventory。

机械通过只证明候选身份闭合，不证明研究判断正确。最终 reviewer 还必须检查语义：证据是否被过度外推、Run2 限定状态是否被扩大、架构反证是否在当前候选仍闭合、旧原型是否真正隔离、商业未知是否被保留，以及只读权限是否存在任何现实副作用逃逸路径。

## 当前禁止

在 manifest-bound final review、governance root 闭合与外部 closure decision 之前，不得建立 shadow sibling root 或开始新 runtime 实现。无论终审结果如何，本候选都不授权选择或声称验证某个真实行业/Pilot，不授权网络采集、联系、发送、发布、报价、签约、账户、凭据、付款、收款、客户数据写入、部署或 production Harness。
