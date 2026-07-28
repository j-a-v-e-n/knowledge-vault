# R4 pre-admission NO-GO 与 PB060-C 回溯依据

记录时间：`2026-07-28T04:00:49-07:00`

状态：`PRE_ADMISSION_NO_GO`。这不是 R4 blind、conformance、adversarial 或 successor receipt，也不改写 R1–R3 的 FAIL 历史。

## 审查对象与身份

- 独立 reviewer：`/root/portfolio_r4_protocol_review`
- 审查时 repository commit：`82e4cca3f0aaaf9970d385d9cf41bcdc94db9a3b`
- 审查时 repository tree：`a5489d923284770462bd08381e6c43b340bdbd61`
- R4 request：`evidence/blueprint-r4-review-request.json`
- request 绑定 blueprint SHA-256：`376452a9cd3d0df95682cb30e93edc1aad4ae6152ef2f1e3d1632926964b5027`
- request 绑定 state SHA-256：`986370d2ed09f352961a3986971c017e7c96f6d21b996ac3c47a26cb552df19a`
- reviewer 只读、未修改文件、未执行外部动作；`authority_effect=NONE`。

## 收敛后的 verdict

`NO-GO — 1 Critical / 1 Major / 0 Minor`

### Critical：attempt verifier 不验证 conformance 执行事实

当前 request 和 rubric 要求 distinct conformance reviewer 运行完整 suite 与 validator；但 `review-protocol/verify_r4_review_attempt.py` 只比较 receipt 自报的 command 字符串与 `{exit_code, classification}`，不从 frozen candidate 直接运行 validator，也不绑定可重算的原始执行输出。

独立复现：

```text
B_ACTUAL_VALIDATOR 4 SCHEMA_INVALID
B_ATTEMPT_VERIFIER 0 VALID_SUCCESSOR_PASS PASS
```

因此，一份实际 schema-invalid 的 recovery candidate 可配合自报 PASS receipt，被机械派生为 `VALID_SUCCESSOR_PASS`。这使 R4 的 PASS admission gate 本身失效；虽然现有外部与 workflow activation 权限仍为 false，但不能启动一条可能错误签发 R4 PASS 的正式 attempt。

### Major：standalone conformance validator 不拒绝重复 JSON key

`model-conformance/task-project-recovery-read-only/validate_recovery_output.py` 使用普通 `json.load`。独立复现中，同一对象先出现 `qualification_status=REFUSED`、后出现 `qualification_status=CANDIDATE_OUTPUT` 时，validator 返回：

```text
A_INNER 0 EVAL_QUALIFIED_CANDIDATE_OUTPUT CANDIDATE_OUTPUT
```

R4 外层 strict parser 会拒绝 persisted wrapper 中的重复 key，因此这条 exact end-to-end 利用当前被外层拦住；但 task-class validator 本身仍不是可靠的独立 oracle，不能宣称 executable qualification 已闭合。

## 为什么回溯而不是继续补协议

`17-总体蓝图活动状态.json` 的 PB060 已预先规定：若 R4 再出现同类 oracle、治理或恢复问题，重开 `PB060-C` 并回到 `PB010` 比较只保留 workflow-local baseline 的路线。它也明确把“R4 增加与 R3 finding 无关的治理”列为 stall trigger。

本次 Critical 的根因是把“命令真实执行并产生结果”降成 reviewer 可自报的 scalar。继续增加 log hash、receipt、签名或新 reviewer 层会重复同一路线，而不会产生商业、能力或 workflow 现实进展。

决定：

- 不启动 R4 blind generation；不生成四个 R4 checkpoint；不签发 R4 verdict。
- 保留 `16`、`17`、R4 request/blind request、protocol 与 tests 作为冻结失败候选和复现材料。
- 执行 `PB060-C → PB010` 的最小组合基线：portfolio 只保留战略问题、只读比较和人工跨项目选择；每个 workflow 自己拥有状态、Gate、证据与写权限。
- duplicate-key-safe 的 standalone validator、可重放 command evidence 与任何跨 provider qualification 转入 backlog；只有未来确有独立模型 qualification 需求时才重开。

## 权限与非主张

该记录不授权 R4 PASS、owner-constraint transition、workflow 写入、C8、Shadow、外部联系、消息、发布、账号、私有数据、支付/收款、合同、交付或真实/影子投资。真实需求、付款、收益、复购与资产价值仍均未由该审查证明。
