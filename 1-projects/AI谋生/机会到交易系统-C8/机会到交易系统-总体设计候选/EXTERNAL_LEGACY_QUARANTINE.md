# 外部旧实现隔离记录

- 旧实现根：`../../机会到交易系统/`
- 已封存 C7 候选根：`../../机会到交易系统-总体设计候选/`
- 当前 C8 候选根：`./`
- 隔离状态：`LEGACY_UNQUALIFIED / MUTABLE_EXTERNAL_ROOT / NO_CANDIDATE_AUTHORITY`

旧根包含 `schema 0.1` CLI、测试、餐馆网页修复 Pilot 及其历史材料。C3 终审期间，该根中的 runtime/test 字节发生并发变化并生成缓存；本候选不判断或覆盖这些变化的所有者，也不删除、回滚或吸收它们。已封存 C7 候选同样保持不变；C8 不通过路径重用或原地修改 C7。

隔离规则：

- 旧根的任何文件、测试通过、候选、餐馆对象、screening、event、Harness 或状态不得成为本候选的当前证据、代码依赖或实现入口；
- 旧根变化不会使本候选 manifest 失效；反过来，本候选通过也不会给旧根补发权限；
- 未来 shadow MVP 只能在预声明 sibling root 从零实现；若人工决定复用某段旧逻辑，必须作为新文件逐项重建、测试并进入 shadow manifest，不能通过路径引用或 hash 豁免偷渡；
- 旧根中的缓存属于该外部根，本候选不擅自删除；
- 旧根仍受 [`LEGACY_STATUS.md`](./LEGACY_STATUS.md) 与 [`LEGACY_CODE_GAP_AUDIT.md`](./LEGACY_CODE_GAP_AUDIT.md) 的语义警告约束，但二者只是隔离说明，不把可变旧代码纳入候选 inventory。
