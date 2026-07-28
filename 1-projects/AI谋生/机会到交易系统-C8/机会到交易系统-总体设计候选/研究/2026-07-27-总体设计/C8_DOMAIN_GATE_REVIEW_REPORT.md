# C8 领域语义 Gate 审查报告

状态：`PENDING-EXACT-CODE-AND-INTERFACE-REVIEW`

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

## 必须被挑战的范围

- C7 Shadow 审查复现的 sampling 未冻结、两条 lane 未封存、contamination、rights/account/external retrieval、legacy schema 与 experiment 已执行变体；
- exact schema、typed ID、parent hash/closure、staleness/invalidity propagation、lane/canary 隔离、complaint 与 explicit request 的结构化分类、污染后的拒绝传播；
- PASS 与 REJECT 都与预声明 exact outcome/error code 及 complete result hash 绑定，无法用自填布尔值或未知字段绕过；
- policy、runner、shadow manifest producer/consumer、acceptance report 和 shadow-review receipt 的 schema/version/hash 同步；
- 正常 REJECT 是领域判定，而 malformed IR、sandbox/runtime 失败、超时或不可重算输出仍 fail closed；
- 不得扩大为自然语言真实性、语义等价、真实需求、客户购买意愿、交付能力或外部权限的证明。

## 待补机械证据与独立结论

当前：`PENDING`。

只有在以上 exact hashes、受管测试、真实 host-required 测试和未参与这些文件编写的 independent reviewer 结论全部写入后，本报告才能由 `PENDING` 改为精确 verdict。机械测试通过不代替独立审查，局部代码审查也不代替 C8 RC-26 完整候选终审。

