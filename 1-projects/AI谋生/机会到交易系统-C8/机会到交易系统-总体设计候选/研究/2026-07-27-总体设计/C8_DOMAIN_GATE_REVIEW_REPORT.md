# C8 领域语义 Gate 审查报告

状态：`PRE-FREEZE-REVIEW-ATTEMPT-1-FAIL / REMEDIATION-IN-PROGRESS / NO-FREEZE-AUTHORITY`

## 用途与证据方向

本报告是 C8 policy、runner、acceptance tests、post-closure verifier 与 phase tests 的下游审查记录。它不是这些代码的输入，不得被 policy、runner 或 verifier 依赖；这样可避免“代码依赖一份声称代码正确的报告”所形成的证据循环。

`C6_SANDBOX_PROBE_REPORT.md` 只保留上游 host-specific sandbox 探针、历史反例和 nonclaims；C8 的领域语义代码、测试和独立结论只记录在本文件。

## 待绑定的 exact 对象

在所有字节稳定后，本节必须记录以下对象的 SHA-256；当前不预填、不猜测：

- `SHADOW_CAPABILITY_POLICY.json`
- `run_shadow_acceptance.py`
- `test_shadow_acceptance.py`
- `verify_post_closure_manifest.py`
- `test_phase_manifests.py`

## Pre-freeze review attempt 1 exact FAIL

被审字节：

```text
31f8d776b593780a62e8283b16e1c4df6ffa5a16613cf7775607e6c528b71405  SHADOW_CAPABILITY_POLICY.json
0f992787de9faeab03c91a0db196950881b699fea598ff2f3bf58d1159e6dad0  run_shadow_acceptance.py
e2e0feab7462ea001a4c8ec05b7ec9ef7914bb46323e7784f111d5b83e5cb053  test_shadow_acceptance.py
a757cb6776196696fef6c9040fffd38ee9099530334978b5799c2a7b10f32e47  verify_post_closure_manifest.py
9b6e89e2bd080c4b8fe713306a3e92f4421e1f7a41ee1e5ee1276a000567feb5  test_phase_manifests.py
8bf39b7f9a0a118cbc05a4bc49581372940189a4b1980e14d393bbe6d3b9bd6f  verify_run2_acceptance.py
6ab827bed1b746ad4ef32eacc416d672556808bdef186f14100ecb7cc3d4f7e6  test_run2_acceptance.py
```

- 主 reviewer：`/root/c8_gate_pre_freeze_review`
- Run2 relocation 独立子审查：`/root/c8_gate_pre_freeze_review/run2_relocation_audit`
- Verdict：`FAIL / NO-GO`
- 计数：`Critical 3 / Major 3 / Minor 0`
- 审查全程只读；七个 exact hashes 在审查前后均一致；未生成 manifest、freeze、governance、shadow、review root 或 receipt。

### Critical

1. Run2 acceptance verifier 没有固定绑定原 C7 receipt 的 raw bytes/hash；顶层 key 重排后字节已变仍可通过。
2. Run2 review scope 只校验 receipt 中的少数直接 bindings，没有将 raw manifests、lead/independent ledgers 等闭合为完整 relocated exact-byte inventory；未列修改、extra 或 hardlink 可漏过。
3. Run2 verifier 对同一 pathname 分开 `stat/hash/read`，hash 后换字节仍可返回 `valid=true`。

### Major

1. 领域 Gate 只检查局部 sequence，没有闭合 acquisition、两 lane seal、contamination assessment 与 merge 的完整内部偏序；矛盾 sequence 仍能返回 `CURRENT`。
2. Manifest-bound mandatory REJECT coverage 少于设计与 Envelope 明确要求；typed-ID/parent/hash/stale、rights account/external retrieval、lane/canary 与 eval 等路径虽有部分单测，却可以不进入实际 Shadow acceptance output set。
3. Exact subrecord schemas 使用 `RightsRecord / SealedLaneOutput / ExperimentSpec` 名称，却拒绝父设计要求的一等 lineage/rights/freeze bindings，使未来 Shadow 无法同时满足 Gate 与父设计接口。

上述任一项都足以阻断 freeze。已有机械测试绿色、当前盘面 C7/C8 字节恰好相同、或权限全为 false，都不能覆盖这些可复现绕过。

## 必须被挑战的范围

- C7 Shadow 审查复现的 sampling 未冻结、两条 lane 未封存、contamination、rights/account/external retrieval、legacy schema 与 experiment 已执行变体；
- exact schema、typed ID、parent hash/closure、staleness/invalidity propagation、lane/canary 隔离、complaint 与 explicit request 的结构化分类、污染后的拒绝传播；
- PASS 与 REJECT 都与预声明 exact outcome/error code 及 complete result hash 绑定，无法用自填布尔值或未知字段绕过；
- policy、runner、shadow manifest producer/consumer、acceptance report 和 shadow-review receipt 的 schema/version/hash 同步；
- 正常 REJECT 是领域判定，而 malformed IR、sandbox/runtime 失败、超时或不可重算输出仍 fail closed；
- 不得扩大为自然语言真实性、语义等价、真实需求、客户购买意愿、交付能力或外部权限的证明。

## 待补机械证据与独立结论

当前：`ATTEMPT-1-FAIL / SUCCESSOR-BYTES-IN-REMEDIATION / FRESH-REVIEW-PENDING`。

只有在修订后新 exact hashes、受管测试、真实 host-required 测试和未参与新字节编写的 fresh independent reviewer 结论全部写入后，本报告才能追加 attempt 2 的精确 verdict。Attempt 1 的 FAIL 不得删除或被新 PASS 覆盖。机械测试通过不代替独立审查，局部代码审查也不代替 C8 RC-26 完整候选终审。
