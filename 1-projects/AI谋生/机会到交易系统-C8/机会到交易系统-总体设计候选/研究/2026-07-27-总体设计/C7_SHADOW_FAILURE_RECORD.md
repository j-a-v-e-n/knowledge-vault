# C7 post-closure Shadow 实现拒绝记录

## 精确身份

- C7 candidate ID：`OTTS-DESIGN-20260727-C7`
- C7 candidate manifest SHA-256：`6515fe17eed7537745b7094ef597321ca30956e57b3306b77570c02a8b9402fd`
- C7 governance manifest SHA-256：`8e5b7fd056f7c07d466e2ead03809ab4de093d46dd52d19471aeff5fde024f1d`
- C7 closure decision SHA-256：`3dfc477fcdc2375e4dd5b6c13e5bd0b9b303bf0949bf7ed25b538bbb631afd72`
- 被审 Shadow manifest SHA-256：`571d5fbe5e7cae7acea8ff2041c1e650d1569fb93720981a64e650a207ff6c63`
- 审查者：`/root/declarative_gate_code_review`（只读，未参与该 Shadow root 的实现，未修改文件）
- Verdict：`FAIL / NO-GO`
- 计数：`Critical 0 / Major 4 / Minor 0`
- 审查身份 root：未创建；禁止生成 PASS receipt

## 实际拒绝项

1. `program.json` 只做字段投影、CAS round trip 与对象封装；`frozen_before_observation`、lane sealing、contamination、rights 和 experiment status 全部信任 fixture 自述，不是机械验证。审查者向 exact program 注入 sampling 未冻结、两条 lane 未封存、`contamination=true`、rights denied 且使用账户/外部取回、legacy `schema_version: 0.1`、experiment `EXECUTED` 等不安全变体，全部成功返回并原样输出不安全值。
2. Shadow manifest 只有两个正向 synthetic cases，没有 Action Envelope 完成定义要求的 semantic tamper、cross-lane、contamination、rights-change、legacy-quarantine 或 staleness 拒绝路径。
3. “显性” fixture 只有对重复劳动的抱怨，没有请求解决方案，却写成 `explicit_request_present=true`，把问题表达与明确请求混淆。
4. 潜在需求 fixture 把人工构造的 presentation gap 与 mockup 可比较性放进 observation/supporting evidence；first-principles lane 又预载 demo/mockup 具体方案，却仍自称 `contamination_detected=false`。

## 机械通过不等于语义通过

该快照的 inventory、canonical JSON、hash/DAG、closed opcode graph、CAS、snapshot ledger、SBOM、capability/runtime reports 和真实主机 sandbox probes 机械闭合。Aggregate Gate 正确输出：

```text
valid=true
shadow_state=PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED
shadow_generation_valid=false
local_shadow_candidate_accepted=false
capability/runtime/deployment/freeze/external authority=false
host_level_universal_noninterference_proven=false
```

这只证明它是一个可复算的 `closed-IR transport/sealer + CAS/sandbox/report-binding` 里程碑，不证明它满足首版 Shadow MVP 的领域语义完成定义。

## 根因与 successor 要求

C7 冻结 policy 只支持 `INPUT`、`LITERAL`、`JSON_POINTER`、`BUILD_OBJECT`、`CANONICAL_SHA256`、`CAS_PUT` 和 `CAS_GET`。该语言无法可信表达 semantic assertions、条件状态转移、canary/cross-lane 检测、typed record 验证或 staleness/rights/legacy 传播。

因此修复必须进入 successor 设计候选，更新 exact policy、runner、post-closure verifier 和拒绝型验收协议，并重新执行 manifest、freeze、independent review 与 governance chain。C7 候选、治理根和失败 Shadow 必须保持原样，不得热修或追认 PASS。

本拒绝不产生任何真实市场、客户、需求、价格、收入或外部行动结论。
