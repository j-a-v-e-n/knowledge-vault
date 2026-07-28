# 总体设计终审候选说明

- Candidate ID：`OTTS-DESIGN-20260727-C1`
- 状态：`CANDIDATE-PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- canonical manifest：`FINAL_CANDIDATE_MANIFEST.json`
- 允许的最强候选结论：仅在终审通过和外部 closure decision 生效后，进入 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 定义的本地、零外部副作用 shadow MVP 实现

## Manifest 的角色

canonical JSON 逐文件绑定：

- 研究协议、访谈核查、Claim/RQ/DD、总体设计、来源日志与 closure matrix；
- SSP-1.0 Run2 的协议、raw responses、双方 sealed ledgers、两次 joint、S2 independent receipt、final run status 与 Claim-Evidence crosswalk；
- 只读 Action Envelope、旧实现差距审计和所有用户可能误读的历史入口警告；
- 首次 invalid 检索运行、旧 raw/筛选、旧 runtime/test/Pilot 工件，全部作为 `historical_exclusions` 绑定而非删除。

JSON manifest 不包含自己，避免自引用哈希。最终 independent review receipt 必须绑定 canonical JSON 的外部 SHA-256，并核对所有 active/historical path、hash、role、authority status 与 dependency。

## 机械验证

从本目录运行：

```bash
python3 研究/2026-07-27-总体设计/verify_candidate_manifest.py FINAL_CANDIDATE_MANIFEST.json
```

验证器 fail closed：未知字段、路径逃逸、重复 path、active/historical 重叠、非规范 SHA-256、缺失文件、hash mismatch、未知依赖或 manifest 自包含都会失败。

机械通过只证明候选身份闭合，不证明研究判断正确。最终 reviewer 还必须检查语义：证据是否被过度外推、Run2 限定状态是否被扩大、架构反证是否在当前候选仍闭合、旧原型是否真正隔离、商业未知是否被保留，以及只读权限是否存在任何现实副作用逃逸路径。

## 当前禁止

在 manifest-bound final review 与外部 closure decision 之前，不得开始新 runtime 实现。无论终审结果如何，本候选都不授权选择或声称验证某个真实行业/Pilot，不授权网络采集、联系、发送、发布、报价、签约、账户、凭据、付款、收款、客户数据写入、部署或 production Harness。
