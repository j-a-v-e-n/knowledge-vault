# SSP-1.0 Run2：lead 最终状态对象

- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- lead 提议状态：`SATURATED-WITHIN-PROTOCOL`
- 当前生效状态：`INCOMPLETE-PENDING-EXACT-FINAL-STATUS-INDEPENDENT-ACCEPTANCE`
- 状态对象：冻结类别代码本在 SSP-1.0 声明的引擎、查询、返回结果与筛选规则内是否被两轮查询扩展
- 不属于本状态对象：来源内容是否全部正确、研究是否穷尽、总体架构是否现实有效、是否存在具体商机、是否能够自治或盈利

本文件是 lead 的精确 final-status 对象，不再把 S2 joint 的独立接受误写成对后续最终运行状态的接受。只有独立审查者对本文件精确 SHA-256、完整 CE-IN crosswalk 和同一 Run2 链给出明确接受，且该接受记录随后被 successor candidate 精确绑定，lead 提议状态才生效；在此之前按协议只能是 `INCOMPLETE`。

先前 acceptance receipt 绑定的是已经被 C6 终审发现语义桥错误的旧 crosswalk 字节；human/JSONL crosswalk、verifier 与 tests 已修订，旧 receipt 因任一绑定字节变化而自动失效，不能迁移或补签。本状态对象现在绑定下列修订字节，必须重新接受。修订不改变 S1/S2 final CE-IN universe 或冻结类别饱和命题，只把两个无充分语义桥的 S2 identity 降为 `NO_DIRECT_LOAD_BEARING_USE`，并把另一条来源对 `SS-01` 的过度关系删除。

## 精确身份

| 工件 | SHA-256 | 角色 |
|---|---|---|
| `../SEARCH_SATURATION_PROTOCOL.md` | `911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1` | 冻结协议 |
| `EXECUTION_MANIFEST.md` | `3a0a6da38c748aa51144d07d4788bf09a755cf2016fbea8c67502b7e5d6a8bba` | 本运行身份与顺序记录 |
| `S1_RAW_MANIFEST.md` | `4d1a650979417595b1dad69cd4466fa921b6bcb0ab0c2ac5561ddbdd5273afed` | S1 raw 封存清单 |
| `lead-screening/S1.md` | `e65fd7fc57cb6febe6614d55d509e2d74d52ecb03cb3176481e37ed5e3b4271f` | S1 lead 初始账本 |
| `independent-screening/S1.md` | `02f39fd0e57ae43712db61a93151c84ab79b31dd490a17f6b78e326c88e7dd60` | S1 independent 初始账本 |
| `S1_JOINT_ADJUDICATION.md` | `c8fb7bef800bc0a23370629fa8dfd4e19c802dea65d303f3e67eff690d00880f` | S1 第一次共同裁决 |
| `S2_RAW_MANIFEST.md` | `ec9065810b1191f81b3fabc1fb81460d6459d4de21ade8494d62ce5f0b032f88` | S2 raw 封存清单 |
| `lead-screening/S2.md` | `9a035c413dc08c760e23cd1072db0648a2b180d3133c6baa8d2e00bef596f5d6` | S2 lead 初始账本 |
| `independent-screening/S2.md` | `325555b723d748cb9cdc3c1442df179eaeb25dd8a31380488bfe8c84db64effe` | S2 independent 初始账本 |
| `S2_JOINT_ADJUDICATION.md` | `c6b2f73f41f1669f1d4a096ebede551353f84024d6d281df091feab4a79907d3` | S2 第二次共同裁决 |
| `S2_INDEPENDENT_ACCEPTANCE_RECEIPT.md` | `f10b6f36810bfd5ae441d6286ddb923f379dad4447d37bcecda9485b3a33bbf1` | S2 exact-byte independent ACCEPT 转录 |
| `../RUN2_CLAIM_EVIDENCE_CROSSWALK.md` | `3f4747ab232ea2639b1265f04b4cdb8871f9218bf6d3c037d7e94a93e0892afb` | `24` 条直接 bridge、`248` 条 non-load-bearing 及语义降级说明 |
| `../RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl` | `cbcbf182b03c157a23a2593f888859454d426d49e7aeb82e22863b3797dfaa38` | 全部 `272` 条最终 CE-IN 的 canonical 逐条映射 |
| `../verify_run2_crosswalk.py` | `9a0e875fffd630594f99c59da17d020d6df3b3b32e64abb215173997fd651250` | 从 sealed inputs 复算 crosswalk，并独立拒绝已否决语义桥 |
| `../test_run2_crosswalk.py` | `9c57ec9c0ddced4d7fd3b0b5c388be748c81915d4de7be72b523c1e1cc0f6576` | 缺失、重复、篡改、自晋级与语义桥回归 |

S1/S2 raw manifests 进一步逐文件绑定各自的 raw 查询响应。冻结协议本身的 `NOT_RUN` 是预注册时的静态封印，未被修改；动态执行与本状态只存在于上述外部工件。

## `SATURATED-WITHIN-PROTOCOL` 谓词

| 协议第 9 节条件 | 结果 | 证据与限制 |
|---|---|---|
| 两轮冻结查询均由指定引擎完整执行 | `PASS` | S1/S2 raw manifests 与执行清单；该事实只覆盖冻结查询，不覆盖未预注册查询或其他引擎 |
| 每个返回结果都有筛选记录 | `PASS` | S1 三方账本覆盖 raw universe；S2 三方账本覆盖 raw universe，身份与顺序由独立复核机械对齐 |
| 原始来源链、排除理由与编码可复查 | `PASS` | raw 文件、两方 sealed ledgers、S1/S2 joints；可复查不等于来源内容正确或全文均已核验 |
| S1 与 S2 都没有 `NEW-CRITICAL` | `PASS` | S1 joint 与 independent 接受的 S2 joint |
| 最终没有 `UNRESOLVED` | `PASS` | S1 joint 与 independent 接受的 S2 joint |
| lead 与 independent 共同同意最终运行状态 | `PENDING` | S1 joint 的双方 `AGREED` 与 S2 exact joint hash 的 independent `ACCEPT` 只完成轮次裁决；它们没有接受本文件的后续 final-status 字节。必须另有 exact-hash independent acceptance |
| 清单、结果集与裁决绑定同一未变协议 | `PASS` | 本节全部运行工件均绑定协议版本 `SSP-1.0` 与同一 SHA-256 |

## lead 对其他运行状态的条件式排除

- `NOT-SATURATED`：不适用。两轮都没有 `NEW-CRITICAL`，没有要求新增类别或改变总体架构、Gate、权限或承重主张的发现，也没有影响关键裁决的代码本结构空白。
- `INCOMPLETE`：当前适用，唯一未满足项是独立方尚未对本精确 final-status 对象明确接受；冻结查询、raw logs、逐结果账本、完整 CE-IN crosswalk、两次共同裁决与 provisional 最终处置已经形成，但不能替代该明确接受。
- `INVALID`：不适用。本运行使用新的执行 ID，从 S1 重新开始；没有修改协议、查询、引擎或规则，没有用历史结果替代冻结查询，也没有选择性遗漏返回结果。

位于上级目录的第一次执行 `SSP-1.0-RUN-20260727T152001-0700` 仍是 `INVALID / NO SATURATION AUTHORITY`。它没有被本运行复用或追认；其存在不会污染也不能补强本状态。

## 条件式最终裁决

若未来 exact-hash independent acceptance 有效，允许的完整表述只有：

> 在 SSP-1.0 声明的范围、引擎、冻结查询、可见返回结果与审查规则内，两轮预注册检索没有产生扩展 `K01`—`K13` 的新关键类别。

不得把本状态解释为：

- 搜完所有网络资料或理论/经验已经穷尽；
- 所有 CE-IN 来源都正确、独立、可跨情境外推或具有同等证据强度；
- 访谈、waitlist、LOI、deposit 或 paid pilot 具有通用的付款预测效度、排序、阈值或校准量；S2 K04 没有合格 claim-evidence；
- 已验证任何行业、对象、需求、买家、渠道、价格、交付、客户价值、单位经济、收入或利润；
- 总体设计已经通过最终研究审查；
- 已获得只读实现、真实 Pilot 或任何外部商业动作权限。

在该接受发生前，本运行保持 `INCOMPLETE`，不得使用上面的允许表述。本状态即使生效，也只满足 `RESEARCH_PROTOCOL.md` 中“冻结协议两轮检索共同裁决”的一个闭合谓词；它不替代 successor candidate、closure predicate matrix 与 manifest-bound final independent review。
