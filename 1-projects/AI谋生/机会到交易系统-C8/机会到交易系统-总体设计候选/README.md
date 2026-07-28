# 机会到交易系统：C8 successor 总体设计候选

状态：`DESIGN-ONLY / C7-DESIGN-CLOSED / C7-SHADOW-FAIL / C8-BLOCKED-PENDING-EXACT-FREEZE-AND-FINAL-REVIEW`

本目录只承载“机会到交易系统”的 C8 successor 研究与总体设计候选，不是 runtime，不包含真实市场、客户、外联、销售、付款、部署或 production Harness 能力。

C7 原件、限定治理链和失败 Shadow 均保持原样：

- [C7 设计候选](../../机会到交易系统-总体设计候选/)
- [C7 治理闭合记录](../../机会到交易系统-闭合记录/)
- [C7 失败 Shadow 快照](../../机会到交易系统-shadow-mvp/)
- [外部旧实现根](../../机会到交易系统/)

C7 的 exact design review 本身通过，且 governance Gate 正确只授权本地零外部副作用 Shadow。但第一份 Shadow 的独立实现审查发现：C7 closed IR 只是安全的 transport/sealer，不能机械验证领域 record、两条 lane 隔离、contamination、rights、legacy、staleness 和未执行实验状态。因此该 Shadow 保持 `PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED`，没有 shadow-review receipt/root，不得追认 PASS。

C8 的根因修订目标是：在仍然不能表达网络、账户、脚本或任意代码的 closed IR 中，加入窄而闭合的 OpportunityRecord 领域验证器；验收协议同时绑定“应当 PASS 的 exact output”与“应当 REJECT 的 exact error code”。它是否真正使污染、权利变化、旧 schema、失效父节点和已执行实验不再依赖 fixture 自述，必须由对抗测试和独立代码/接口审查确认，当前不预告 PASS。

当前阅读顺序：

1. [`研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md`](./研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md)
2. [`研究/2026-07-27-总体设计/01-黄仁勋访谈核查.md`](./研究/2026-07-27-总体设计/01-黄仁勋访谈核查.md)
3. [`研究/2026-07-27-总体设计/02-主张与证据地图.md`](./研究/2026-07-27-总体设计/02-主张与证据地图.md)
4. [`研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md`](./研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md)
5. [`研究/2026-07-27-总体设计/RUN2_CLAIM_EVIDENCE_CROSSWALK.md`](./研究/2026-07-27-总体设计/RUN2_CLAIM_EVIDENCE_CROSSWALK.md)
6. [`研究/2026-07-27-总体设计/C7_SHADOW_FAILURE_RECORD.md`](./研究/2026-07-27-总体设计/C7_SHADOW_FAILURE_RECORD.md)
7. [`研究/2026-07-27-总体设计/RESEARCH_CLOSURE_PREDICATE_MATRIX.md`](./研究/2026-07-27-总体设计/RESEARCH_CLOSURE_PREDICATE_MATRIX.md)
8. [`研究/2026-07-27-总体设计/FINAL_REVIEW_HISTORY.md`](./研究/2026-07-27-总体设计/FINAL_REVIEW_HISTORY.md)

只有 C8 exact manifest/freeze、全量 manifest-bound independent review 与新 governance chain 均通过后，才可在本 C8 container 内创建新的 `机会到交易系统-shadow-mvp/` 和 `机会到交易系统-shadow-review/`。即使最终通过，也只接受本地合成 fixture 的声明式能力候选，全部现实行动权限仍为 false。
