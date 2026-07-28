状态：`S2-JOINT-ADJUDICATION-COMPLETE-SEALED-IFF-INDEPENDENT-ACCEPTS-THIS-EXACT-HASH`

# SSP-1.0 Run 2 — S2 第二次共同裁决

## 1. 身份绑定、权限边界与条件式最终语义

- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- 协议版本：`SSP-1.0`
- 协议 SHA-256：`911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1`
- S2 原始响应清单 SHA-256：`ec9065810b1191f81b3fabc1fb81460d6459d4de21ade8494d62ce5f0b032f88`
- lead S2 初始账本 SHA-256：`9a035c413dc08c760e23cd1072db0648a2b180d3133c6baa8d2e00bef596f5d6`
- independent S2 初始账本 SHA-256：`325555b723d748cb9cdc3c1442df179eaeb25dd8a31380488bfe8c84db64effe`
- 绑定输入分别是 `S2_RAW_MANIFEST.md`、`lead-screening/S2.md` 与 `independent-screening/S2.md` 的上述精确字节身份；两份初始账本均在互阅前封存。
- 本文件物化 S2 的完整条件式最终共同裁决。首行状态是严格的 `IFF` 条件，不是当前已获接受的自我声明：只有 independent 明确接受本文件修订后精确 SHA-256，且接受后字节未变，本文件才满足该条件式封存状态。
- 即使上述条件日后满足，本文件也不自行构成 `SATURATED-WITHIN-PROTOCOL`、`NOT-SATURATED`、研究闭合、总体设计修改、实现授权或外部商业动作授权；最终运行状态只能由外部运行记录在验收后另行判断。
- 本文件没有新增搜索，也没有修改协议、原始响应、两份封存账本或核心设计。

## 2. 机械对齐结果

以修正后的 S2 原始响应清单定义有序全集 `U345`。逐条抽取并比较三元身份 `query/rank/ref` 后：

- 原始清单、lead 账本和 independent 账本均覆盖 `345` 条；missing=`0`，extra=`0`，重复身份=`0`。
- `query/rank` 顺序一致，且每个 `query/rank` 绑定的 result ref 一致；不存在错位后再比较编码的情况。
- 归一化后的 CATEGORY-DISCOVERY（CD）状态差：`5`；相同：`340`。
- 归一化后的 CLAIM-EVIDENCE（CE）决定差：`85`；相同：`260`。
- 规范化 K-set 字面差：`176`；相同：`169`。
- NC-PROVISIONAL 状态差：`0`；相同：`345`，双方均为 `NO`。

以上维度可以在同一 ref 上重叠，不能相加解释成独立来源数、证据量或证据强度。

## 3. `345` 条条件式最终记录的确定性序列化与重建规则

本节与第 4—8 节共同构成全部 `345` 条记录的无损序列化规范。绑定输入中的原始字段与双方编码必须同时保留；不能用一段合并摘要代替任何一方原记录，也不能靠裁决者自由解释补全。

### 3.1 共同规则

1. `U345` 的 `query/rank/ref/order` 逐字段取自绑定的 S2 原始响应清单；任何不在 `U345` 内的对象都不是本次裁决对象。
2. `MetadataRecord` 的 `title`、`author-or-organization`、`date`、`URL-or-DOI`、`source-type` 逐字段、逐字继承绑定 lead 账本中对应标记字段。lead 写明“未显示”、截断或未知时，该字面值本身就是最终值；不得以 independent 或外部知识猜补。
3. `LeadExactClaim(x)` 严格等于 lead row 中 `CLAIM-EVIDENCE` 字段结束分隔符之后、`K mapping` 字段开始分隔符之前的完整逐字子串；不依赖也不枚举 `支持`、`反驳`、`限制`、`线索`、`返回主张`、`精确主张` 或任何其他前缀。`IndependentExactClaim(x)` 严格等于 independent row 的 `Exact returned proposition` 表列完整逐字字段。`ApplicableOverride(x)` 固定为三槽有序元组 `{S4(x), S5(x), S8(x)}`：每个槽逐字收录对应节内所有对 `x` 适用的完整 scope-override 文本，节内多条时按自上而下顺序保留；不适用槽必须写字面 `NONE`。适用性只由该节中明确列出的单条 identity、包含 `x` 的紧凑 identity group 或包含 `x` 的 query-wide/rank range 决定，不做语义分类猜测。`FinalClaimRecord={LeadExactClaim, IndependentExactClaim, ApplicableClaimOverrideTuple}`，其中 `ApplicableClaimOverrideTuple(x)=ApplicableOverride(x)`；不得把两份原主张融合成一条新主张。
4. `LeadMethodLimit(x)` 严格等于 lead row 中 `NC-PROVISIONAL` 字段结束分隔符之后至该行行尾的完整逐字子串；`范围/方法：` 与 `范围/方法/不可外推：` 两种变体都接受并逐字保留，若 suffix 还有其他字面文本也必须完整保留，不猜补、不规范化。`IndependentMethodLimit(x)` 严格等于 independent row 的 `Scope / method / cannot extrapolate` 表列完整逐字字段。`MethodLimitRecord={LeadMethodLimit, IndependentMethodLimit, ApplicableLimitOverrideTuple}`，其中 `ApplicableLimitOverrideTuple(x)=ApplicableOverride(x)`；因此同一 `{S4,S5,S8}` 三槽元组同时进入 claim-override 与 limit-override，且三槽与槽内 clause 全部累积生效。任何一方的 “no factual claim admitted”“不可跨情境外推”“需全文/方法核验”等限制都不得被另一方较宽表述抵消。
5. `LeadCodingRecord={lead-CD, lead-CE, lead-K, lead-NC}` 与 `IndependentCodingRecord={independent-CD, independent-CE, independent-K, independent-NC}` 必须逐字保留；`FinalJointCoding={final-CD, final-CE, final-K, final-NC}` 由下列规则另行产生。不得只保存最终编码而丢掉任一初始编码。
6. 对每个编码维度，`agreement set = U345 − 本文件该维度完整 disagreement set`。agreement set 的最终值继承双方归一化后相同的值。
7. CD 归一化：lead 的 `INCLUDE` 对应 independent 的 `CD-IN/*`；lead 的 `EXCLUDE—OUT-OF-SCOPE` 对应 independent 的 `CD-OUT/OUT-OF-SCOPE`。在 CD agreement set 中，最终 IN 子型采用 independent 已记录的 `FIT` 或 `MECHANISM-LEAD`；OUT 保持 `CD-OUT/OUT-OF-SCOPE`。第 4 节覆盖全部 `5` 个例外。
8. CE 归一化：`INCLUDE` 与 `CE-IN/*` 比较为纳入，所有排除理由按协议标准原因码比较。在 CE agreement set 中：双方纳入时最终保留 independent 的 `CE-IN/PRIMARY-METHOD`、`CE-IN/OFFICIAL`、`CE-IN/DOCUMENTATION` 或 `CE-IN/CASE-MECHANISM` 子型；双方以同一标准原因排除时保留该原因。第 5 节覆盖全部 `85` 个例外。`S2-K09/R26` 是明确 override：继承 lead 的字面 `INCLUDE`，不增造来源子型。
9. K mapping 先去重并按 `K01`—`K13` 升序规范化。第 6.1—6.3 节覆盖全部 `176` 个字面分歧并产生 preliminary K；第 6.4 节的 `42` 条 final-K override 以最高优先级 applied last。其余 `169` 个 agreement 继承共同 K-set；最终 CD-OUT 的条目最终 K-set 为 `NONE`。不存在“所有 K 分歧一律取并集”的规则。
10. NC agreement set 就是 `U345` 全集，最终统一为 `NC=NO`；第 7 节说明其类别归属和本轮新增类别检查。
11. 任一 `U345` row、`CLAIM-EVIDENCE` 字段结束分隔符、`K mapping` 字段开始分隔符、`NC-PROVISIONAL` 字段结束分隔符、independent 所需表列、任一上述序列化字段、任一方完整编码或任一 `{S4,S5,S8}` 槽缺失、重复、错位或无法逐字取得时，整条记录失败并 fail closed；不得生成部分 `FinalJointRow`。
12. K mapping 是发现机制的路由标签，不是 CE 纳入，也不扩大 exact proposition、scope 或事实主张。

### 3.2 可复算性检查式

对任意 `x ∈ U345`，序列化结果必须同时包含：

- `IdentityTuple(x) = literal U345{query, rank, ref, order}`。
- `FinalMetadata(x) = literal LeadMetadata{title, author-or-organization, date, URL-or-DOI, source-type}`。
- `LeadExactClaim(x) = literal-substring-after(LeadRow(x), end-delimiter-of-CLAIM-EVIDENCE) before start-delimiter-of-K-mapping`；两个边界分隔符不进入子串，边界之间的全部字符逐字保留。
- `IndependentExactClaim(x) = literal IndependentRow(x)[Exact returned proposition]` 完整表列字段。
- `LeadMethodLimit(x) = literal-suffix-after(LeadRow(x), end-delimiter-of-NC-PROVISIONAL) through end-of-line`；结束分隔符不进入 suffix，suffix 的全部字符逐字保留，包括 `范围/方法：`、`范围/方法/不可外推：` 或任何其他字面变体。
- `IndependentMethodLimit(x) = literal IndependentRow(x)[Scope / method / cannot extrapolate]` 完整表列字段。
- `S4(x) / S5(x) / S8(x) = ordered-literal-sequence-of-all-applicable-scope-overrides-in-that-section`；不适用的每个槽分别为字面 `NONE`。
- `ApplicableClaimOverrideTuple(x) = ApplicableLimitOverrideTuple(x) = ordered-literal-tuple{S4(x), S5(x), S8(x)}`，固定按 `S4 → S5 → S8`，不得省略、合槽或重排。
- `FinalClaimRecord(x) = ordered-literal-tuple{LeadExactClaim(x), IndependentExactClaim(x), ApplicableClaimOverrideTuple(x)}`。
- `MethodLimitRecord(x) = ordered-literal-tuple{LeadMethodLimit(x), IndependentMethodLimit(x), ApplicableLimitOverrideTuple(x)}`，且所有元素与 clause cumulative。
- `LeadCodingRecord(x) = literal{LeadCD(x), LeadCE(x), LeadK(x), LeadNC(x)}`。
- `IndependentCodingRecord(x) = literal{IndependentCD(x), IndependentCE(x), IndependentK(x), IndependentNC(x)}`。
- `FinalCD(x) = CD-disagreement-table(x)`，若 `x` 在第 4 节；否则为双方共同 CD，并按规则 7 保留子型。
- `FinalCE(x) = CE-final-group(x)`，若 `x` 在第 5 节；否则为双方共同 CE，并按规则 8 保留子型。
- `PreliminaryK(x) = K-disagreement-preliminary-rule(x)`，若 `x` 在第 6.1—6.3 节；否则为双方共同规范化 K-set。
- `FinalK(x) = NONE`，若 `FinalCD(x)=OUT`；否则若 `x` 在第 6.4 节则取该 applied-last override；否则取 `PreliminaryK(x)`。
- `FinalNC(x) = NO`。
- `FinalJointCoding(x) = {FinalCD(x), FinalCE(x), FinalK(x), FinalNC(x)}`。
- `FinalJointRow(x) = {IdentityTuple(x), FinalMetadata(x), FinalClaimRecord(x), MethodLimitRecord(x), LeadCodingRecord(x), IndependentCodingRecord(x), FinalJointCoding(x)}`。

因此 agreement 数量分别为 CD `340`、CE `260`、K `169`、NC `345`；下文列出的 disagreement 身份必须分别恰好为 `5`、`85`、`176`、`0`，否则重建失败并应 fail closed。

## 4. CD 的全部 `5` 个分歧与最终裁决

| Query/rank | lead | independent | 最终 CD | 最终 CE | 最终 K | 追加的窄 scope |
|---|---|---|---|---|---|---|
| `S2-K03/R16` | OUT | IN/FIT | `CD-IN/FIT` | `CE-IN/PRIMARY-METHOD` | `K06` | 只作 rival firms、acquihire 与 talent allocation 的形式模型；不是客户获取或市场需求的经验效应证据。 |
| `S2-K04/R16` | IN | OUT | `CD-IN/MECHANISM-LEAD` | `CE-OUT/INACCESSIBLE-FOR-VERIFICATION` | `K03+K04+K11` | 截断片段只提示 pre-contract documentation/payment readiness；不得承载事实、效果量或预测效度主张。 |
| `S2-K07/R17` | OUT | IN/FIT | `CD-IN/FIT` | `CE-IN/PRIMARY-METHOD` | `K01+K09` | 只作 Bayesian truth-discovery 方法及其两个 data-integration 数据集的研究；不是商机或真实需求识别准确率。 |
| `S2-K07/R19` | IN | OUT | `CD-IN/MECHANISM-LEAD` | `CE-OUT/INACCESSIBLE-FOR-VERIFICATION` | `K07` | 只保留 verification/selection bias 机制；不得从医疗或准实验片段外推一般市场验证。 |
| `S2-K08/R34` | OUT | IN/MECHANISM-LEAD | `CD-IN/MECHANISM-LEAD` | `CE-OUT/SECONDARY-WHEN-PRIMARY-AVAILABLE` | `K08+K09` | 媒体摘要只提示 expert/novice、capability/reliability 与 business-result 落差；不得承载发生率、因果或效果量。 |

双方共同 CD-OUT 的完整集合是 `S2-K02/R01`、`S2-K02/R20`、`S2-K04/R13`、`S2-K04/R14`、`S2-K04/R15`、`S2-K04/R17`、`S2-K07/R16`；这 `7` 条最终 K=`NONE`。第 4 节的 `5` 条最终均为 CD-IN；全局最终 CD=`IN 338 / OUT 7`。

## 5. CE 的全部 `85` 个分歧与最终裁决

紧凑记法 `S2-Kxx/{Raa,Rbb}` 必须展开为两个完整身份 `S2-Kxx/Raa`、`S2-Kxx/Rbb`；下列分组互斥，合计 `85`，就是完整 CE disagreement set。

### 5.1 `CE-OUT/SECONDARY-WHEN-PRIMARY-AVAILABLE`（`29`）

- `S2-K01/{R13}`
- `S2-K06/{R02}`
- `S2-K07/{R18,R20,R21,R22,R23,R24}`
- `S2-K08/{R18,R34}`
- `S2-K09/{R34,R35}`
- `S2-K11/{R11,R18,R19,R20,R22,R23,R24,R29}`
- `S2-K12/{R23,R24,R26,R27}`
- `S2-K13/{R24,R25,R27,R29,R30}`

Override scope：不得纳入新事实、量化、发生率、因果或效果主张；需要原始/官方来源才能承重，只保留不超出绑定返回的机制表达。

### 5.2 `CE-OUT/INACCESSIBLE-FOR-VERIFICATION`（`23`）

- `S2-K01/{R18}`
- `S2-K02/{R02,R14,R15,R16,R17,R18,R19}`
- `S2-K03/{R14,R15,R17,R18,R21}`
- `S2-K04/{R16}`
- `S2-K05/{R21}`
- `S2-K06/{R20}`
- `S2-K07/{R19}`
- `S2-K09/{R17,R23,R31}`
- `S2-K12/{R19,R20}`
- `S2-K13/{R18}`

Override scope：只核到 title/snippet/截断片段；不得承载 load-bearing factual claim。只有在最终 CD-IN 时才能保留片段直接表达的机制线索。

### 5.3 `CE-IN/*`（`8`）

| Query/rank | 最终 CE | 只允许承载的 scope |
|---|---|---|
| `S2-K03/R10` | `CE-IN/CASE-MECHANISM` | 只保留 Nicira 一手复盘可见范围的 case mechanism；不作跨公司、跨市场或因果外推。 |
| `S2-K03/R16` | `CE-IN/PRIMARY-METHOD` | rival firms/acquihire/talent allocation 的形式模型；不作跨市场客户获取经验结论。 |
| `S2-K05/R07` | `CE-IN/DOCUMENTATION` | IBM 报告的文档内容与其中自述；不证明 service recovery 导致购买。 |
| `S2-K06/R05` | `CE-IN/PRIMARY-METHOD` | 只承载返回中可核的形式模型、假设及其条件；不作跨情境经验 WTP 或利润结论。 |
| `S2-K06/R06` | `CE-IN/PRIMARY-METHOD` | compositional choice 的形式理论及其条件；不作普遍经验替代效应。 |
| `S2-K07/R17` | `CE-IN/PRIMARY-METHOD` | 算法及两个真实 data-integration 数据集上的报告结果；不作开放世界需求发现准确率。 |
| `S2-K09/R26` | `INCLUDE`（逐字继承 lead，不增造子型） | 原论文可见返回中的 benchmark/taxonomy；不作开放世界生产可靠性保证；`R03/R06/R12` 不独立计数。 |
| `S2-K10/R22` | `CE-IN/DOCUMENTATION` | Microsoft 产品文档所述 controls/configuration；不证明安全控制有效性。 |

### 5.4 `CE-OUT/DUPLICATE`（`8`）

| Query/rank | canonical result | 最终 scope |
|---|---|---|
| `S2-K06/R21` | `S2-K02/R16` | 同一 *Entrepreneurial Marketing* PDF，不增加独立证据计数。 |
| `S2-K08/R26` | `S2-K08/R16` | 对 *Generative AI at Work* 的重复 Reddit 摘要，不增加独立证据计数。 |
| `S2-K08/R33` | `S2-K08/R03` | 对同一 BCG 研究的重复新闻转述，不增加独立证据计数。 |
| `S2-K09/R03` | `S2-K09/R26` | 同一 *Why Do Multi-Agent LLM Systems Fail?*；以完整 OpenReview 原始论文为 canonical。 |
| `S2-K09/R06` | `S2-K09/R26` | 对同一 multi-agent failure 论文的二级解说；沿 `R03` 重复链归并到 `R26`。 |
| `S2-K09/R12` | `S2-K09/R26` | 对同一 multi-agent failure 论文的二级解说；沿 `R03` 重复链归并到 `R26`。 |
| `S2-K10/R28` | `S2-K10/R26` | 同一 permission-management 帖子，不增加独立证据计数。 |
| `S2-K13/R19` | `S2-K10/R24` | 同一 URL/帖子跨 query 重复，不增加独立证据计数。 |

### 5.5 `CE-OUT/FABRICATED-OR-UNVERIFIABLE`（`5`）

- `S2-K08/{R22,R23,R29}`
- `S2-K10/{R29}`
- `S2-K13/{R26}`

Override scope：被删除、身份不明或无法核验的统计/来源不得承载任何事实主张；只能记录“该返回无法核验”这一审计事实。

### 5.6 `CE-OUT/NO-METHOD`（`8`）

- `S2-K01/{R07}`
- `S2-K02/{R10}`
- `S2-K03/{R07}`
- `S2-K04/{R08,R10,R12}`
- `S2-K11/{R05}`
- `S2-K12/{R22}`

Override scope：只能作为机制表达；不得承载发生率、效果、预测性或因果主张。

### 5.7 `CE-OUT/PROMOTIONAL-ONLY`（`2`）

- `S2-K08/{R25}`
- `S2-K13/{R14}`

Override scope：只证明 vendor/self-report/marketing 表述或产品设计存在；不证明有效性、普遍性或购买结果。

### 5.8 `CE-OUT/STALE-CURRENT-CLAIM`（`2`）

- `S2-K13/{R17,R23}`

Override scope：旧版、草案或已被替代的材料不能证明当前标准、配置或合规状态；最多支持其历史存在。

最终全局 CE 计数为 `INCLUDE 141 / EXCLUDE 204`。这只是对 `U345` 的编码计数，不是 `141` 个独立研究、证据强度或事实主张数量；DUPLICATE 和同源转述不得重复计数。

### 5.9 双方 CE 分歧形态的完整计数审计

以下是绑定账本中全部 pair-code 差异的归一化计数；它与上面的 `85` 个最终身份集合是两个视图，不能重复计数：

| lead vs independent | 数量 | 最终处理 |
|---|---:|---|
| NO-METHOD vs SECONDARY | `28` | `S2-K01/R07`、`S2-K02/R10`、`S2-K03/R07`、`S2-K04/R12` 最终 NO-METHOD；其余最终 SECONDARY |
| INACCESSIBLE vs INCLUDE | `15` | `S2-K06/R05` 最终 INCLUDE/PRIMARY-METHOD；其余最终 INACCESSIBLE |
| INACCESSIBLE vs SECONDARY | `5` | 最终 INACCESSIBLE |
| NO-METHOD vs FABRICATED | `5` | 最终 FABRICATED-OR-UNVERIFIABLE |
| SECONDARY vs INCLUDE | `4` | 最终 SECONDARY |
| NO-METHOD vs DUPLICATE | `3` | 最终 DUPLICATE |
| NO-METHOD vs INCLUDE | `3` | `S2-K05/R07`、`S2-K06/R06` 最终 INCLUDE；`S2-K11/R05` 最终 NO-METHOD |
| NO-METHOD vs PROMOTIONAL | `3` | `S2-K04/R08,R10` 最终 NO-METHOD；`S2-K08/R25` 最终 PROMOTIONAL |
| SECONDARY vs DUPLICATE | `3` | 最终 DUPLICATE |
| INACCESSIBLE vs OUT-OF-SCOPE | `2` | 最终 INACCESSIBLE，CD 保留 IN |
| NO-METHOD vs INACCESSIBLE | `2` | `S2-K12/R19` 最终 INACCESSIBLE；`S2-K12/R22` 最终 NO-METHOD |
| OUT-OF-SCOPE vs INCLUDE | `2` | 最终 INCLUDE |
| PROMOTIONAL vs INCLUDE | `2` | `S2-K10/R22` INCLUDE/DOCUMENTATION；`S2-K13/R14` PROMOTIONAL |
| STALE vs INCLUDE | `2` | 最终 STALE-CURRENT-CLAIM |
| DUPLICATE vs INCLUDE | `1` | `S2-K09/R03` DUPLICATE |
| INACCESSIBLE vs DUPLICATE | `1` | `S2-K06/R21` DUPLICATE |
| INCLUDE vs DUPLICATE | `1` | `S2-K09/R26` 逐字继承 lead 的 INCLUDE，不增造子型 |
| INCLUDE vs INACCESSIBLE | `1` | `S2-K13/R18` INACCESSIBLE |
| INCLUDE vs NO-METHOD | `1` | `S2-K03/R10` INCLUDE/CASE-MECHANISM |
| OUT-OF-SCOPE vs SECONDARY | `1` | `S2-K08/R34` SECONDARY，CD 保留 IN |

## 6. K mapping 的全部 `176` 个分歧与最终裁决

K mapping 是多标签发现路由。第 6.1—6.3 节先对全部 `176` 个字面分歧建立可复算的 preliminary K，第 6.4 节再对其中 `42` 条作 applied-last final-K override；这明确撤销“所有 K 分歧一律取并集”的旧规则。K 裁决不改变 CE，也不扩大 exact proposition 或 MethodLimit。本节的 `176` 条最终 CD 均为 IN，因此不触发 K=`NONE`。

### 6.1 lead 是 strict superset：preliminary K 采用 lead K-set（`129`）

- `S2-K01/{R01,R02,R03,R04,R06,R07,R08,R09,R10,R12,R13,R14,R16,R17,R18,R19,R20}`
- `S2-K02/{R02,R03,R04,R05,R06,R08,R10,R11,R12,R13,R14,R15,R16,R17,R18,R21}`
- `S2-K03/{R01,R03,R04,R05,R06,R09,R10,R11,R12,R13,R15,R17,R18,R20,R21}`
- `S2-K04/{R01,R02,R03,R04,R05,R06,R07,R08,R09,R10,R11,R12,R16}`
- `S2-K05/{R04,R05,R06,R07,R08,R10,R11,R13,R14,R16,R18,R20,R23}`
- `S2-K06/{R01,R05,R06,R07,R08,R10,R13,R15,R16,R17,R18,R19}`
- `S2-K07/{R15,R19,R21,R22,R23}`
- `S2-K08/{R07,R14,R15,R17,R20,R28,R29,R33}`
- `S2-K09/{R08,R09,R14,R18,R19,R20,R21,R22,R24,R25,R28,R29,R30,R31,R32,R33,R35,R36}`
- `S2-K10/{R06,R09,R14,R25}`
- `S2-K11/{R01,R02}`
- `S2-K12/{R04,R05,R07,R10}`
- `S2-K13/{R04,R19}`

对上列任一身份，先令 `PreliminaryK = LeadK`；若该身份也在第 6.4 节，则最终仍必须使用 applied-last override。MethodLimit 仍按第 3 节累计，不能因较宽标签集而扩大主张。

### 6.2 independent 是 strict superset：preliminary K 采用 independent K-set（`34`）

- `S2-K02/{R07}`
- `S2-K03/{R16}`
- `S2-K07/{R17}`
- `S2-K08/{R21,R22,R27,R34}`
- `S2-K09/{R17}`
- `S2-K10/{R18,R19,R21,R34,R38}`
- `S2-K11/{R06,R07,R11,R13,R14,R15,R16,R20,R22}`
- `S2-K12/{R01,R14,R17,R20,R21,R23,R24,R25,R26,R27}`
- `S2-K13/{R03,R05}`

对上列任一身份，先令 `PreliminaryK = IndependentK`；若该身份也在第 6.4 节，则最终仍必须使用 applied-last override。

### 6.3 双方为 cross-set：preliminary K 采用明确并集（`13`）

| Query/rank | lead K-set | independent K-set | preliminary K-set |
|---|---|---|---|
| `S2-K01/R05` | `K01+K03+K09` | `K01+K03+K04` | `K01+K03+K04+K09` |
| `S2-K03/R19` | `K02+K07` | `K03+K07` | `K02+K03+K07` |
| `S2-K05/R15` | `K01+K05+K09` | `K03+K05+K09` | `K01+K03+K05+K09` |
| `S2-K05/R17` | `K05+K12` | `K04` | `K04+K05+K12` |
| `S2-K06/R21` | `K04+K06+K07` | `K02+K06` | `K02+K04+K06+K07` |
| `S2-K08/R25` | `K08+K12` | `K08+K09` | `K08+K09+K12` |
| `S2-K08/R31` | `K08` | `K09+K10+K13` | `K08+K09+K10+K13` |
| `S2-K10/R11` | `K10+K11+K13` | `K09+K10+K13` | `K09+K10+K11+K13` |
| `S2-K11/R03` | `K01+K11` | `K03+K10+K11` | `K01+K03+K10+K11` |
| `S2-K11/R09` | `K01+K11` | `K10+K11` | `K01+K10+K11` |
| `S2-K11/R17` | `K06+K11` | `K09+K10+K11+K13` | `K06+K09+K10+K11+K13` |
| `S2-K11/R28` | `K06+K11` | `K01+K11` | `K01+K06+K11` |
| `S2-K12/R13` | `K09+K12` | `K03+K12` | `K03+K09+K12` |

`129 + 34 + 13 = 176`。上列三组互斥并覆盖完整 K disagreement set；其余 `169` 条的 preliminary K 继承双方共同规范化 K-set。

### 6.4 Applied-last final-K override（`42`）

下表优先级高于第 6.1—6.3 节。每个身份的 `FinalK` 必须逐字等于下表，不得再与 preliminary K、query provenance 或另一方 K-set 求并集。

| Query/rank | applied-last `FinalK` |
|---|---|
| `S2-K01/R05` | `K01+K03+K09` |
| `S2-K02/R07` | `K02+K06` |
| `S2-K03/R19` | `K02+K07` |
| `S2-K05/R07` | `K04` |
| `S2-K05/R15` | `K01+K05+K09` |
| `S2-K05/R17` | `K05+K12` |
| `S2-K06/R21` | `K04+K06+K07` |
| `S2-K07/R21` | `K07` |
| `S2-K07/R22` | `K07` |
| `S2-K07/R23` | `K07` |
| `S2-K08/R15` | `K08` |
| `S2-K08/R21` | `K12` |
| `S2-K08/R25` | `K08+K09` |
| `S2-K08/R29` | `K08` |
| `S2-K08/R31` | `K09+K10+K13` |
| `S2-K08/R34` | `K08+K09` |
| `S2-K09/R08` | `K09+K13` |
| `S2-K09/R09` | `K09+K13` |
| `S2-K09/R14` | `K09+K13` |
| `S2-K09/R18` | `K09` |
| `S2-K09/R19` | `K09` |
| `S2-K09/R20` | `K09` |
| `S2-K09/R21` | `K09` |
| `S2-K09/R22` | `K09` |
| `S2-K09/R24` | `K09` |
| `S2-K09/R25` | `K09` |
| `S2-K09/R28` | `K09` |
| `S2-K09/R29` | `K09` |
| `S2-K09/R30` | `K09+K13` |
| `S2-K09/R31` | `K09` |
| `S2-K09/R32` | `K09+K13` |
| `S2-K09/R33` | `K09` |
| `S2-K09/R35` | `K09+K13` |
| `S2-K09/R36` | `K09` |
| `S2-K10/R11` | `K09+K10+K13` |
| `S2-K11/R14` | `K06+K11` |
| `S2-K11/R15` | `K06+K11` |
| `S2-K11/R16` | `K06+K11` |
| `S2-K11/R17` | `K09+K10+K11+K13` |
| `S2-K11/R28` | `K06+K11` |
| `S2-K12/R17` | `K11+K12` |
| `S2-K12/R26` | `K12` |

这 `42` 个身份互不重复，且全部属于上文 `176` 个 K disagreement set；其余 `134` 个 K 分歧的最终值等于 preliminary K。第 4 节中的 `S2-K08/R34` 已同步为 `K08+K09`。

## 7. NC、新类别与未决项

- NC disagreement set：空集。
- 双方对 `U345` 的全部 `345` 条都编码为 `NC-PROVISIONAL=NO`；条件式最终为 `NC=NO`。
- consent integrity / trusted approval path → `K10+K13`。
- delegation rights → `K06+K10+K11+K13`。
- least-autonomy / permission-composition → `K09+K10+K13`。
- skill formation / skill erosion → `K08+K12`。
- persistent prompt injection / shared-state corruption → `K09+K10+K13`。
- 上述边界都是既有类别的失效子机制或交叉映射，不要求 `K14`，也不改变主体、资源、伤害路径、Gate 或权限边界。
- 条件式最终 `NEW-CRITICAL=0`。
- 条件式最终 `NEW-NONCRITICAL=0`。
- 条件式最终 `UNRESOLVED=0`。
- 条件式最终 S2 新类别：无。

在 independent 对本文件修订后精确 hash 给出独立 `ACCEPT` 前，上述条件式最终值不得称为双方已经共同接受，也不得据此宣布协议内类别饱和。

## 8. K04 证据质量强制警告

K04 查询返回的 `17` 条最终 CE 全部排除：

- `CE-OUT/NO-METHOD`：`S2-K04/{R01,R04,R07,R08,R10,R12}`（`6`）
- `CE-OUT/PROMOTIONAL-ONLY`：`S2-K04/{R02,R03,R05,R06,R09,R11}`（`6`）
- `CE-OUT/OUT-OF-SCOPE`：`S2-K04/{R13,R14,R15,R17}`（`4`）
- `CE-OUT/INACCESSIBLE-FOR-VERIFICATION`：`S2-K04/{R16}`（`1`）

其中 `R01`—`R12` 与 `R16` 共 `13` 条最终 CD-IN，只能作为机制线索；`R13`—`R15`、`R17` 共 `4` 条 CD-OUT。特别是 `R16` 只保留被截断的 pre-contract documentation/payment-readiness 机制，并交叉映射 `K03+K04+K11`，不能承载事实主张。

因此，本轮没有任何 K04 结果可以证明 interview、waitlist、LOI、deposit 或 paid pilot 对真实购买/支付具有预测效度，也不能证明这些信号之间的普遍排序、校准量、阈值、因果效应或跨市场有效性。既有 K04 的信号层级只能继续作为待验证设计机制，不能被表述成已获 S2 证据支持的经验规律；这不构成新类别。

## 9. 条件式最终 S2 结论与独立验收 Gate

若且仅若 independent：

1. 对本文件精确字节计算 SHA-256；
2. 验证第 2—8 节能按上述三个固定 lead delimiter、两个 independent 完整表列及每条记录显式 `{S4,S5,S8}` 三槽，对全部 `345` 条确定性重建完整 `FinalJointRow`，包括身份、元数据、双方 exact claim、累积 MethodLimit、双方原编码及最终 CD/CE/K/NC；
3. 对该精确 hash 明确给出 `ACCEPT`；
4. 验收后未发生任何字节修改；

本文件才满足首行条件式封存状态。届时只能由外部运行记录基于本文件 hash、独立 `ACCEPT` 及其后无字节变化的事实，另行判断 final run status。本文条件式最终结论是：S2 未发现新类别、`NEW-CRITICAL=0`、`UNRESOLVED=0`，且 K04 只有发现机制、没有可承载预测效度的 CE；本文件自身不能充当自己的独立验收，也不宣告 saturation、研究闭合、总体设计获批、实现授权或任何外部动作授权。
