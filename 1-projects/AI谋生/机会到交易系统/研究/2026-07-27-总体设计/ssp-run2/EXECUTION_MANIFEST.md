# SSP-1.0 第二次执行身份清单

- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- 执行状态：`S2-BOTH-INITIAL-CODINGS-SEALED / S2-JOINT-ADJUDICATION-AUTHORIZED`
- 协议版本：`SSP-1.0`
- 协议相对路径：`../SEARCH_SATURATION_PROTOCOL.md`
- 协议 SHA-256：`911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1`
- 执行开始时间：`2026-07-27T15:48:03-0700`
- 指定引擎：`Codex web search`
- 当前允许动作：`S2` 第二次共同裁决；双方初始编码已分别封存，现在允许比较
- 饱和裁决：`NOT_ESTABLISHED`

本运行不复用或追认第一次失效运行的任何 S1/S2 响应、筛选或裁决。旧材料可以作为运行外设计背景，但不得进入本运行的返回结果宇宙。

## S1 封存身份

- S1 原始响应清单 SHA-256：`4d1a650979417595b1dad69cd4466fa921b6bcb0ab0c2ac5561ddbdd5273afed`
- lead 初始筛选 SHA-256：`e65fd7fc57cb6febe6614d55d509e2d74d52ecb03cb3176481e37ed5e3b4271f`
- independent 初始筛选 SHA-256：`02f39fd0e57ae43712db61a93151c84ab79b31dd490a17f6b78e326c88e7dd60`
- S1 第一次共同裁决 SHA-256：`c8fb7bef800bc0a23370629fa8dfd4e19c802dea65d303f3e67eff690d00880f`
- S1 共同结论：`NEW-CRITICAL=0 / UNRESOLVED=0 / NC-PROVISIONAL-S1-01→EXISTING-K13`

以上只完成 S1，不是类别饱和结论。只有 S2 原始结果、双方独立筛选、第二次共同裁决和最终运行记录全部完成后，才能按协议第 9 节判定最终状态。

## S2 原始响应封存身份

- S2 原始响应清单：`S2_RAW_MANIFEST.md`
- S2 原始响应清单 SHA-256：`ec9065810b1191f81b3fabc1fb81460d6459d4de21ade8494d62ce5f0b032f88`
- S2 原始结果宇宙：`345` 个可见结果块
- S2 查询执行：`S2-K01`—`S2-K13` 均为 `COMPLETE`，没有机械重试
- lead S2 初始筛选 SHA-256：`9a035c413dc08c760e23cd1072db0648a2b180d3133c6baa8d2e00bef596f5d6`
- independent S2 初始筛选 SHA-256：`325555b723d748cb9cdc3c1442df179eaeb25dd8a31380488bfe8c84db64effe`
- lead S2 单方结论：`NEW-CRITICAL=0 / NC-PROVISIONAL=0 / UNRESOLVED=0`
- independent S2 单方结论：`NEW-CRITICAL=0 / NC-PROVISIONAL=0 / UNRESOLVED=0`
- 当前饱和裁决：`NOT_ESTABLISHED`

S2 原始响应与双方全部 `345` 条初始编码已经封存。双方在封存前均声明未读取或探测对方 S2 文件；现在才允许打开对方账本，比较每一条 CATEGORY-DISCOVERY、CLAIM-EVIDENCE、K mapping 和 NC 判断并形成第二次共同裁决。

## S2 清单纠正记录

首次清单的十三个逐项计数与 raw 文件一致，但末行把正确总和 `345` 误写为 `315`。lead 与 independent 都在创建 S2 初始编码前独立拒绝了这个不一致。旧清单 SHA-256 `b4bcfeed8fd3d31f0b0b50a53e347179f5c35e2183b33be017cef9a09e96c993` 已作废；raw 文件与查询执行没有变化，也没有发生重搜。只有纠正后的新清单 SHA-256 可以绑定双方 S2 编码。
