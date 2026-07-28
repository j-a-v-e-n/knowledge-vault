# 机会到交易系统：不可变总体设计候选

状态：`DESIGN-ONLY / RUN2-EXACT-ACCEPTED / C6-BLOCKED-PENDING-MANIFEST-BOUND-FINAL-REVIEW`

本目录只承载“机会到交易系统”的研究与总体设计候选，不是 runtime，不包含真实市场、客户、外联、销售、付款、部署或生产 Harness 能力。

它与旧目录 [`../机会到交易系统/`](../机会到交易系统/) 分开，原因不是把旧工作删除，而是旧 `schema 0.1` CLI、测试和餐馆 Pilot 仍可能由其他任务修改；把那些可变字节继续放进设计候选 inventory，会让一次无关实现改动使设计终审身份失效。旧目录因此保持 `LEGACY_UNQUALIFIED`，既不被当前候选复用，也不被当前候选回滚。

当前阅读顺序：

1. [`研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md`](./研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md)
2. [`研究/2026-07-27-总体设计/01-黄仁勋访谈核查.md`](./研究/2026-07-27-总体设计/01-黄仁勋访谈核查.md)
3. [`研究/2026-07-27-总体设计/02-主张与证据地图.md`](./研究/2026-07-27-总体设计/02-主张与证据地图.md)
4. [`研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md`](./研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md)
5. [`研究/2026-07-27-总体设计/RUN2_CLAIM_EVIDENCE_CROSSWALK.md`](./研究/2026-07-27-总体设计/RUN2_CLAIM_EVIDENCE_CROSSWALK.md)
6. [`研究/2026-07-27-总体设计/RESEARCH_CLOSURE_PREDICATE_MATRIX.md`](./研究/2026-07-27-总体设计/RESEARCH_CLOSURE_PREDICATE_MATRIX.md)
7. [`研究/2026-07-27-总体设计/FINAL_REVIEW_HISTORY.md`](./研究/2026-07-27-总体设计/FINAL_REVIEW_HISTORY.md)
8. [`研究/2026-07-27-总体设计/C6_SANDBOX_PROBE_REPORT.md`](./研究/2026-07-27-总体设计/C6_SANDBOX_PROBE_REPORT.md)

Run2 final-status 已取得绑定 exact bytes 的独立接受，但它只关闭冻结协议内的类别代码本谓词。C5 的两个独立拒绝项、C6 pre-freeze Python Gate 的 `NO-GO` 与 declarative Gate iteration A 的 exact-hash `FAIL / NO-GO` 均保留在审查历史中；declarative iteration B 已通过真实 host-required suite 与 exact-byte 独立代码/接口复审，且无 Critical/Major。该局部 PASS 不能替代全候选 manifest/freeze 与 RC-26 独立终审；总体仍为 `BLOCKED-PENDING-C6-MANIFEST-BOUND-INDEPENDENT-REVIEW`，没有 governance 或 shadow authority。

后续 shadow 不再运行 target-controlled Python。它只允许 canonical data/text 与 exact closed declarative IR；唯一解释器固定在设计候选中，并对 read-once snapshot、私有临时 CAS、资源上限和当前主机的隔离探针出具分层证据。只有 exact C6 manifest 的机械冻结、全量 manifest-bound independent review 和后闭合 governance chain 均通过后，才允许依次创建 `机会到交易系统-shadow-mvp/` 与独立的 `机会到交易系统-shadow-review/`。即使全部通过，也只接受本地合成 fixture 的声明式能力候选，全部现实行动权限仍为 false。
