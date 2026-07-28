# 旧原型状态

状态：`HISTORICAL / NOT-AUTHORIZED-AS-CURRENT-DESIGN`

本目录在当前总体研究完成前已经存在一版 `schema 0.1` 本地 CLI、测试和餐馆网页修复 Pilot。它们保留为历史样本，用于以后做差距审计；不能被解释为当前总体设计已经实现，也不能证明餐馆网页修复是已验证商机。

当前权威研究候选位于：

- [`研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md`](./研究/2026-07-27-总体设计/RESEARCH_PROTOCOL.md)
- [`研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md`](./研究/2026-07-27-总体设计/03-机会到交易系统-总体设计.md)

旧实现的逐项差距见 [`LEGACY_CODE_GAP_AUDIT.md`](./LEGACY_CODE_GAP_AUDIT.md)。

旧代码差距审计已经完成，并判定旧 runtime 不可作为新设计的实现入口。无论研究候选以后是否通过，只要旧对象没有逐项重建并重新验证，以下边界持续有效：

- 不从旧 Pilot 继承行业、买家、需求、价格、渠道或交易结论；
- 不把旧测试通过当成新设计的验收证据；
- 不继续对外展示、联系、发布、报价、收付款或部署；
- 不删除旧材料，也不静默把它们改名成新系统证据；
- 只有逐项映射到新记录、状态、Gate、权限和测试语义并重新验证的代码，才可能被保留。

若最终 closure decision 通过，第一版也只能在与本候选目录不重叠的精确 sibling root `机会到交易系统-shadow-mvp/` 内，按研究候选的 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 搭建；governance 记录另存于 `机会到交易系统-闭合记录/`。两个 root 都必须由各自的 post-closure manifest 绑定，且不能解除旧 CLI、旧 `make-harness` 或餐馆 Pilot 的历史状态。

已知必须重点复核的一项旧规则是：旧测试允许在出现 commitment/deposit 后生成 delivery Harness；新设计要求在不可取消订金、结果承诺或正式协议前，同一 exact offer 必须先通过独立的 `DeliveryFeasibilityGate`。旧规则不得继续作为授权依据。
