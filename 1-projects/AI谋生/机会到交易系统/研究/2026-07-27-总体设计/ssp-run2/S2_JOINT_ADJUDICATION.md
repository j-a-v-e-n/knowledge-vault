状态：`DRAFT-PENDING-INDEPENDENT-ACCEPTANCE`

# SSP-1.0 Run 2 — S2 第二次共同裁决候选草案

## 1. 身份绑定、权限边界与候选语义

- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- 协议版本：`SSP-1.0`
- 协议 SHA-256：`911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1`
- S2 原始响应清单 SHA-256：`ec9065810b1191f81b3fabc1fb81460d6459d4de21ade8494d62ce5f0b032f88`
- lead S2 初始账本 SHA-256：`9a035c413dc08c760e23cd1072db0648a2b180d3133c6baa8d2e00bef596f5d6`
- independent S2 初始账本 SHA-256：`325555b723d748cb9cdc3c1442df179eaeb25dd8a31380488bfe8c84db64effe`
- 绑定输入分别是 `S2_RAW_MANIFEST.md`、`lead-screening/S2.md` 与 `independent-screening/S2.md` 的上述精确字节身份；两份初始账本均在互阅前封存。
- 本文件只提出 S2 的候选共同裁决。它尚未得到 independent 对本文件精确 SHA-256 的验收，因此不是 `S2-JOINT-ADJUDICATION-COMPLETE-SEALED`，也不构成 `SATURATED-WITHIN-PROTOCOL`、`NOT-SATURATED`、总体设计修改、实现授权或外部商业动作授权。
- 本草案没有新增搜索、没有修改协议、原始响应、两份封存账本或核心设计。

## 2. 机械对齐结果

以修正后的 S2 原始响应清单定义有序全集 `U345`。逐条抽取并比较三元身份 `query/rank/ref` 后：

- 原始清单、lead 账本和 independent 账本均覆盖 `345` 条；missing=`0`，extra=`0`，重复身份=`0`。
- `query/rank` 顺序一致，且每个 `query/rank` 绑定的 result ref 一致；不存在错位后再比较编码的情况。
- 归一化后的 CATEGORY-DISCOVERY（CD）状态差：`5`；相同：`340`。
- 归一化后的 CLAIM-EVIDENCE（CE）决定差：`85`；相同：`260`。
- 规范化 K-set 字面差：`176`；相同：`169`。
- NC-PROVISIONAL 状态差：`0`；相同：`345`，双方均为 `NO`。

以上维度可以在同一 ref 上重叠，不能相加解释成独立来源数、证据量或证据强度。

## 3. `345` 条候选共同决定的确定性重建规则

本节与第 4—7 节共同构成完整裁决表的无损压缩表示；不需要把 `345` 行再次抄写一遍，也不能靠裁决者自由解释补全。

### 3.1 共同规则

1. `U345` 的身份与顺序只取自绑定的 S2 原始响应清单；任何不在 `U345` 内的对象都不是本次裁决对象。
2. 对每个维度，`agreement set = U345 − 本文件该维度完整 disagreement set`。agreement set 的最终值继承双方归一化后相同的值。
3. CD 归一化：lead 的 `INCLUDE` 对应 independent 的 `CD-IN/*`；lead 的 `EXCLUDE—OUT-OF-SCOPE` 对应 independent 的 `CD-OUT/OUT-OF-SCOPE`。在 CD agreement set 中，最终 IN 子型采用 independent 已记录的 `FIT` 或 `MECHANISM-LEAD`；OUT 保持 `CD-OUT/OUT-OF-SCOPE`。第 4 节覆盖全部 `5` 个例外。
4. CE 归一化：`INCLUDE` 与 `CE-IN/*` 比较为纳入，所有排除理由按协议标准原因码比较。在 CE agreement set 中：双方纳入时最终保留 independent 的 `CE-IN/PRIMARY-METHOD`、`CE-IN/OFFICIAL`、`CE-IN/DOCUMENTATION` 或 `CE-IN/CASE-MECHANISM` 子型；双方以同一标准原因排除时保留该原因。第 5 节覆盖全部 `85` 个例外。
5. K mapping 先去重并按 `K01`—`K13` 升序规范化。K agreement set 继承共同 K-set；CD 最终 OUT 的条目最终 K-set 为 `NONE`。第 6 节覆盖全部 `176` 个例外。
6. NC agreement set 就是 `U345` 全集，最终统一为 `NC=NO`；第 7 节说明其类别归属和本轮新增类别检查。
7. 每条最终 scope 是两份绑定账本该行 scope/limit 的逻辑合取：只能同时满足双方限制，不能选择较宽的一边。若第 4 或第 5 节另列更窄的 override scope，还须再与 override 合取。任何一方的“no factual claim admitted”“不可跨情境外推”“需全文/方法核验”等限制均不得被另一方较宽表述抵消。
8. exact proposition 不因 K-set 取并集而扩大；K mapping 是发现机制的路由标签，不是 CE 纳入，也不是新事实主张。

### 3.2 可复算性检查式

对任意 `x ∈ U345`：

- `FinalCD(x) = CD-disagreement-table(x)`，若 `x` 在第 4 节；否则为双方共同 CD，并按规则 3 保留子型。
- `FinalCE(x) = CE-final-group(x)`，若 `x` 在第 5 节；否则为双方共同 CE，并按规则 4 保留子型。
- `FinalK(x) = K-disagreement-rule(x)`，若 `x` 在第 6 节；否则为双方共同规范化 K-set；若 `FinalCD(x)=OUT`，再强制为 `NONE`。
- `FinalNC(x) = NO`。
- `FinalScope(x) = LeadScope(x) AND IndependentScope(x) AND applicable override(x)`。

因此 agreement 数量分别为 CD `340`、CE `260`、K `169`、NC `345`；下文列出的 disagreement 身份必须分别恰好为 `5`、`85`、`176`、`0`，否则重建失败并应 fail closed。

## 4. CD 的全部 `5` 个分歧与候选裁决

| Query/rank | lead | independent | 候选最终 CD | 候选最终 CE | 候选最终 K | 追加的窄 scope |
|---|---|---|---|---|---|---|
| `S2-K03/R16` | OUT | IN/FIT | `CD-IN/FIT` | `CE-IN/PRIMARY-METHOD` | `K06` | 只作 rival firms、acquihire 与 talent allocation 的形式模型；不是客户获取或市场需求的经验效应证据。 |
| `S2-K04/R16` | IN | OUT | `CD-IN/MECHANISM-LEAD` | `CE-OUT/INACCESSIBLE-FOR-VERIFICATION` | `K03+K04+K11` | 截断片段只提示 pre-contract documentation/payment readiness；不得承载事实、效果量或预测效度主张。 |
| `S2-K07/R17` | OUT | IN/FIT | `CD-IN/FIT` | `CE-IN/PRIMARY-METHOD` | `K01+K09` | 只作 Bayesian truth-discovery 方法及其两个 data-integration 数据集的研究；不是商机或真实需求识别准确率。 |
| `S2-K07/R19` | IN | OUT | `CD-IN/MECHANISM-LEAD` | `CE-OUT/INACCESSIBLE-FOR-VERIFICATION` | `K07` | 只保留 verification/selection bias 机制；不得从医疗或准实验片段外推一般市场验证。 |
| `S2-K08/R34` | OUT | IN/MECHANISM-LEAD | `CD-IN/MECHANISM-LEAD` | `CE-OUT/SECONDARY-WHEN-PRIMARY-AVAILABLE` | `K06+K08` | 媒体摘要只提示 expert/novice、capability/reliability 与 business-result 落差；不得承载发生率、因果或效果量。 |

双方共同 CD-OUT 的完整集合是 `S2-K02/R01`、`S2-K02/R20`、`S2-K04/R13`、`S2-K04/R14`、`S2-K04/R15`、`S2-K04/R17`、`S2-K07/R16`；这 `7` 条最终 K=`NONE`。第 4 节的 `5` 条候选最终均为 CD-IN。

## 5. CE 的全部 `85` 个分歧与候选裁决

紧凑记法 `S2-Kxx/{Raa,Rbb}` 必须展开为两个完整身份 `S2-Kxx/Raa`、`S2-Kxx/Rbb`；下列分组互斥，合计 `85`，就是完整 CE disagreement set。

### 5.1 `CE-OUT/SECONDARY-WHEN-PRIMARY-AVAILABLE`（`34`）

- `S2-K01/{R07,R13}`
- `S2-K03/{R07}`
- `S2-K06/{R02}`
- `S2-K07/{R18,R20,R21,R22,R23,R24}`
- `S2-K08/{R18,R33,R34}`
- `S2-K09/{R06,R12,R34,R35}`
- `S2-K11/{R11,R18,R19,R20,R22,R23,R24,R29}`
- `S2-K12/{R23,R24,R26,R27}`
- `S2-K13/{R24,R25,R27,R29,R30}`

Override scope：不得纳入新事实、量化、发生率、因果或效果主张；需要原始/官方来源才能承重，只保留不超出绑定返回的机制表达。

### 5.2 `CE-OUT/INACCESSIBLE-FOR-VERIFICATION`（`25`）

- `S2-K01/{R18}`
- `S2-K02/{R02,R14,R15,R16,R17,R18,R19}`
- `S2-K03/{R14,R15,R17,R18,R21}`
- `S2-K04/{R16}`
- `S2-K05/{R21}`
- `S2-K06/{R05,R20}`
- `S2-K07/{R19}`
- `S2-K09/{R17,R23,R31}`
- `S2-K12/{R19,R20,R22}`
- `S2-K13/{R18}`

Override scope：只核到 title/snippet/截断片段；不得承载 load-bearing factual claim。只有在最终 CD-IN 时才能保留片段直接表达的机制线索。

### 5.3 `CE-IN/*`（`7`）

| Query/rank | 候选最终 CE | 只允许承载的 scope |
|---|---|---|
| `S2-K03/R16` | `CE-IN/PRIMARY-METHOD` | rival firms/acquihire/talent allocation 的形式模型；不作跨市场客户获取经验结论。 |
| `S2-K05/R07` | `CE-IN/DOCUMENTATION` | IBM 报告的文档内容与其中自述；不证明 service recovery 导致购买。 |
| `S2-K06/R06` | `CE-IN/PRIMARY-METHOD` | compositional choice 的形式理论及其条件；不作普遍经验替代效应。 |
| `S2-K07/R17` | `CE-IN/PRIMARY-METHOD` | 算法及两个真实 data-integration 数据集上的报告结果；不作开放世界需求发现准确率。 |
| `S2-K09/R26` | `CE-IN/PRIMARY-METHOD` | 原论文中的 benchmark/taxonomy；不作开放世界生产可靠性保证。 |
| `S2-K10/R22` | `CE-IN/DOCUMENTATION` | Microsoft 产品文档所述 controls/configuration；不证明安全控制有效性。 |
| `S2-K11/R05` | `CE-IN/DOCUMENTATION` | Browse AI 帮助/发布者说明及其责任分配；不是法律裁定。 |

### 5.4 `CE-OUT/DUPLICATE`（`5`）

| Query/rank | canonical result | 候选 scope |
|---|---|---|
| `S2-K06/R21` | `S2-K02/R16` | 同一 *Entrepreneurial Marketing* PDF，不增加独立证据计数。 |
| `S2-K08/R26` | `S2-K08/R16` | 对 *Generative AI at Work* 的重复 Reddit 摘要，不增加独立证据计数。 |
| `S2-K09/R03` | `S2-K09/R26` | 同一 *Why Do Multi-Agent LLM Systems Fail?*；以完整 OpenReview 原始论文为 canonical。 |
| `S2-K10/R28` | `S2-K10/R26` | 同一 permission-management 帖子，不增加独立证据计数。 |
| `S2-K13/R19` | `S2-K10/R24` | 同一 URL/帖子跨 query 重复，不增加独立证据计数。 |

### 5.5 `CE-OUT/FABRICATED-OR-UNVERIFIABLE`（`5`）

- `S2-K08/{R22,R23,R29}`
- `S2-K10/{R29}`
- `S2-K13/{R26}`

Override scope：被删除、身份不明或无法核验的统计/来源不得承载任何事实主张；只能记录“该返回无法核验”这一审计事实。

### 5.6 `CE-OUT/NO-METHOD`（`4`）

- `S2-K02/{R10}`
- `S2-K03/{R10}`
- `S2-K04/{R12}`
- `S2-K08/{R25}`

Override scope：只能作为机制表达；不得承载发生率、效果、预测性或因果主张。

### 5.7 `CE-OUT/PROMOTIONAL-ONLY`（`3`）

- `S2-K04/{R08,R10}`
- `S2-K13/{R14}`

Override scope：只证明 vendor/self-report/marketing 表述或产品设计存在；不证明有效性、普遍性或购买结果。

### 5.8 `CE-OUT/STALE-CURRENT-CLAIM`（`2`）

- `S2-K13/{R17,R23}`

Override scope：旧版、草案或已被替代的材料不能证明当前标准、配置或合规状态；最多支持其历史存在。

### 5.9 双方 CE 分歧形态的完整计数审计

以下是绑定账本中全部 pair-code 差异的归一化计数；它与上面的 `85` 个最终身份集合是两个视图，不能重复计数：

| lead vs independent | 数量 | 候选处理 |
|---|---:|---|
| NO-METHOD vs SECONDARY | `28` | 除 `S2-K02/R10`、`S2-K04/R12` 最终 NO-METHOD 外，其余最终 SECONDARY |
| INACCESSIBLE vs INCLUDE | `15` | 最终 INACCESSIBLE |
| INACCESSIBLE vs SECONDARY | `5` | 最终 INACCESSIBLE |
| NO-METHOD vs FABRICATED | `5` | 最终 FABRICATED-OR-UNVERIFIABLE |
| SECONDARY vs INCLUDE | `4` | 最终 SECONDARY |
| NO-METHOD vs DUPLICATE | `3` | 最终 DUPLICATE |
| NO-METHOD vs INCLUDE | `3` | 最终 INCLUDE |
| NO-METHOD vs PROMOTIONAL | `3` | `S2-K04/R08,R10` PROMOTIONAL；`S2-K08/R25` NO-METHOD |
| SECONDARY vs DUPLICATE | `3` | 最终 SECONDARY |
| INACCESSIBLE vs OUT-OF-SCOPE | `2` | 最终 INACCESSIBLE，CD 保留 IN |
| NO-METHOD vs INACCESSIBLE | `2` | 最终 INACCESSIBLE |
| OUT-OF-SCOPE vs INCLUDE | `2` | 最终 INCLUDE |
| PROMOTIONAL vs INCLUDE | `2` | `S2-K10/R22` INCLUDE/DOCUMENTATION；`S2-K13/R14` PROMOTIONAL |
| STALE vs INCLUDE | `2` | 最终 STALE-CURRENT-CLAIM |
| DUPLICATE vs INCLUDE | `1` | `S2-K09/R03` DUPLICATE |
| INACCESSIBLE vs DUPLICATE | `1` | `S2-K06/R21` DUPLICATE |
| INCLUDE vs DUPLICATE | `1` | `S2-K09/R26` INCLUDE/PRIMARY-METHOD |
| INCLUDE vs INACCESSIBLE | `1` | `S2-K13/R18` INACCESSIBLE |
| INCLUDE vs NO-METHOD | `1` | `S2-K03/R10` NO-METHOD |
| OUT-OF-SCOPE vs SECONDARY | `1` | `S2-K08/R34` SECONDARY，CD 保留 IN |

## 6. K mapping 的全部 `176` 个分歧与候选裁决

K mapping 是多标签发现路由。对最终 CD-IN 的 K 分歧采用双方 K-set 并集，以免在已冻结的 `K01`—`K13` 内丢失交叉机制；它不改变 CE，也不扩大 exact proposition 或 scope。本节的 `176` 条均候选最终 CD-IN，因此不触发 K=`NONE`。

### 6.1 lead 是 strict superset：最终采用 lead K-set（`129`）

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

对上列任一身份，`FinalK = LeadK`；最终 scope 仍按第 3 节合取，不能因采用较宽标签集而扩大主张。

### 6.2 independent 是 strict superset：最终采用 independent K-set（`34`）

- `S2-K02/{R07}`
- `S2-K03/{R16}`
- `S2-K07/{R17}`
- `S2-K08/{R21,R22,R27,R34}`
- `S2-K09/{R17}`
- `S2-K10/{R18,R19,R21,R34,R38}`
- `S2-K11/{R06,R07,R11,R13,R14,R15,R16,R20,R22}`
- `S2-K12/{R01,R14,R17,R20,R21,R23,R24,R25,R26,R27}`
- `S2-K13/{R03,R05}`

对上列任一身份，`FinalK = IndependentK`；最终 scope 仍按第 3 节合取。

### 6.3 双方为 cross-set：最终采用明确并集（`13`）

| Query/rank | lead K-set | independent K-set | 候选最终 K-set |
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

`129 + 34 + 13 = 176`。上列三组互斥并覆盖完整 K disagreement set；其余 `169` 条继承双方共同规范化 K-set。

## 7. NC、候选新类别与未决项

- NC disagreement set：空集。
- 双方对 `U345` 的全部 `345` 条都编码为 `NC-PROVISIONAL=NO`；候选最终为 `NC=NO`。
- consent integrity 仍可无损路由到既有 `K11/K12/K13`；delegation rights 路由到 `K10/K11/K13`；skill erosion 路由到 `K08/K12`；cross-session prompt injection 路由到 `K09/K10/K13`。这些是既有类别的失效子机制或交叉映射，不要求 `K14`，也不改变主体、资源、伤害路径、Gate 或权限边界。
- 候选 `NEW-CRITICAL=0`。
- 候选 `NEW-NONCRITICAL=0`。
- 候选 `UNRESOLVED=0`。
- 候选 S2 新类别：无。

这些只是本草案对绑定 S2 输入的候选结果。在 independent 对本文件精确 hash 给出独立接受前，不得称为共同同意，也不得据此宣布协议内类别饱和。

## 8. K04 证据质量强制警告

K04 查询返回的 `17` 条候选最终 CE 全部排除：

- `CE-OUT/NO-METHOD`：`S2-K04/{R01,R04,R07,R12}`（`4`）
- `CE-OUT/PROMOTIONAL-ONLY`：`S2-K04/{R02,R03,R05,R06,R08,R09,R10,R11}`（`8`）
- `CE-OUT/OUT-OF-SCOPE`：`S2-K04/{R13,R14,R15,R17}`（`4`）
- `CE-OUT/INACCESSIBLE-FOR-VERIFICATION`：`S2-K04/{R16}`（`1`）

其中 `R01`—`R12` 与 `R16` 共 `13` 条候选 CD-IN，只能作为机制线索；`R13`—`R15`、`R17` 共 `4` 条 CD-OUT。特别是 `R16` 只保留被截断的 pre-contract documentation/payment-readiness 机制，并交叉映射 `K03+K04+K11`，不能承载事实主张。

因此，本轮没有任何 K04 结果可以证明 interview、waitlist、LOI、deposit 或 paid pilot 对真实购买/支付具有预测效度，也不能证明这些信号之间的普遍排序、校准量、阈值、因果效应或跨市场有效性。既有 K04 的信号层级只能继续作为待验证设计机制，不能被表述成已获 S2 证据支持的经验规律；这不构成新类别。

## 9. 候选 S2 结论与独立验收 Gate

若且仅若 independent：

1. 对本文件精确字节计算 SHA-256；
2. 验证第 2—8 节能对全部 `345` 条确定性重建 CD/CE/K/NC；
3. 对该精确 hash 明确给出 `ACCEPT`；
4. 验收后未发生任何字节修改；

才允许另行记录 S2 共同裁决完成及其 hash。当前候选结论是：S2 未发现新类别、`NEW-CRITICAL=0`、`UNRESOLVED=0`，且 K04 只有发现机制、没有可承载预测效度的 CE；但这些都仍处于 `DRAFT-PENDING-INDEPENDENT-ACCEPTANCE`。本文件自身不能充当自己的独立验收，也不授权自行宣布饱和。
