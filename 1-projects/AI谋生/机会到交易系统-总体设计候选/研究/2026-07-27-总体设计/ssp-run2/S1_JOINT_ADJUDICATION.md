# SSP-1.0 Run 2 — S1 第一次共同裁决

状态：`S1-JOINT-ADJUDICATION-COMPLETE-SEALED`

## 绑定身份

- 执行 ID：`SSP-1.0-RUN-20260727T154803-0700`
- 协议版本：`SSP-1.0`
- 协议 SHA-256：`911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1`
- S1 原始响应清单 SHA-256：`4d1a650979417595b1dad69cd4466fa921b6bcb0ab0c2ac5561ddbdd5273afed`
- lead 初始筛选 SHA-256：`e65fd7fc57cb6febe6614d55d509e2d74d52ecb03cb3176481e37ed5e3b4271f`
- independent 初始筛选 SHA-256：`02f39fd0e57ae43712db61a93151c84ab79b31dd490a17f6b78e326c88e7dd60`
- lead 与 independent 均在初始账本封存后才读取对方文件；两份封存账本未被修改。

本文件只完成协议第 8 节要求的 S1 第一次共同裁决。`S2` 尚未执行，因此本文件不构成 `SATURATED-WITHIN-PROTOCOL`、`NOT-SATURATED` 或最终运行状态。

## 机械对齐

- S1 原始结果、lead ledger 与 independent ledger 均为 `432` 个 ref/rank；missing=`0`，extra=`0`，顺序一致。
- CD 纳排状态差：`6`。
- CE 纳入/排除状态差：`81`。
- 双方均排除但标准理由不同：`116`。
- 双方均纳入但来源类型标签不同：`113`。
- 归一化 K-set 字面差：`181`；其中 CATEGORY-DISCOVERY 纳入结果的实质差为 `180`，另 `1` 条是 `S1-K06/R19` 的 OOS 空映射与 query-provenance `K06` 表示差，不构成类别分歧。
- NC 状态差：`3`，恰为下节的三个 ref。
- 标题规范化差：`103`；URL 字面差：`1`，后者是去除过期 signed-query 参数后的同一基准 URL。

这些机械差异可重叠，不能相加解释为独立来源数或证据强度。

## NC-PROVISIONAL-S1-01

### 涉及结果

| Query/rank | Ref | 机制线索 | 最终 CATEGORY 裁决 | 最终 CLAIM-EVIDENCE |
|---|---|---|---|---|
| `S1-K13/R24` | `turn160reddit23` | 无具体 action scope 的 approval 可能退化为 rubber stamp | `EXISTING-K13` | `EXCLUDE:NO-METHOD` |
| `S1-K13/R27` | `turn160reddit26` | 监督者可能没有能力实际评估输出 | `EXISTING-K13` | `EXCLUDE:NO-METHOD` |
| `S1-K13/R34` | `turn160news37` | time pressure、approval fatigue 与 automation bias 可能削弱人审 | `EXISTING-K13`，伤害侧面 cross-map `K12` | `EXCLUDE:SECONDARY-WHEN-PRIMARY-AVAILABLE` |

### 共同理由

冻结的 `K13` 已明确包含 action scope、least privilege、approval、monitoring 与责任升级。“形式批准不等于有效监督”描述的是这些控制是否真实有效的失效子机制；把它放入 `K13` 不会丢失对设计有用的区别，也不需要新增顶层类别、主体、资源或伤害路径。因此共同裁决为 `EXISTING-K13`，不是 `NEW-CRITICAL`、`NEW-NONCRITICAL` 或 `UNRESOLVED`。

approval receipt 只证明特定主体对特定动作作过授权，不证明其理解、能力、注意力或监督有效性。依赖实质人审时，现有 `K13` Gate 仍须检查 action specificity、上下文、reviewer authority/competence、fresh state 和 fail-closed 条件；这是 K13 的实现与验收要求，不是新类别。

三条直接返回只支持 CATEGORY-DISCOVERY 和机制表达，不支持发生率、因果效应、风险强度或“人工审批普遍失效”的承重经验主张。运行外取得的其他来源不得追认进入本次 S1。

## CE 纳入/排除差异的共同裁决

### 最终分组

`EXCLUDE:INACCESSIBLE-FOR-VERIFICATION`（`39`）：

- `K01/R11,R14,R15,R16,R22,R24`
- `K02/R04,R07,R09,R15,R17`
- `K03/R07,R08,R13,R15,R20,R23`
- `K04/R08,R16,R17`
- `K05/R12,R14,R17,R19,R20`
- `K06/R06,R08,R10,R15,R16,R20,R21,R22`
- `K07/R16`
- `K09/R14`
- `K12/R03,R07,R09,R22`

`EXCLUDE:DUPLICATE`（`17`）：

- `K01/R06,R09`
- `K03/R10`
- `K04/R02,R04`
- `K05/R09,R11`
- `K06/R11`
- `K07/R17`
- `K08/R03,R06,R10,R12,R16`
- `K12/R21`
- `K13/R06,R18`

`EXCLUDE:SECONDARY-WHEN-PRIMARY-AVAILABLE`（`6`）：

- `K04/R09`
- `K05/R04`
- `K11/R13,R14,R15`
- `K12/R06`

`EXCLUDE:FABRICATED-OR-UNVERIFIABLE`（`1`）：

- `K04/R18`

`INCLUDE`（`18`）：

- `K02/R03`
- `K04/R11`
- `K05/R03`
- `K06/R03,R05`
- `K07/R01,R03,R09,R11`
- `K08/R20`
- `K09/R08,R16`
- `K10/R15,R18,R22`
- `K11/R03,R22`
- `K12/R19`

### 关键范围决定

- `K04/R11 turn150search10`：`INCLUDE`，以 ScienceDirect 原始页承载 WTP criterion-validity 系统综述/meta-analysis；只支持其证据更 mixed、设计不可直接比较的范围，不外推校正量。
- `K08/R20 turn154search19`：`INCLUDE`，只支持该 GitHub Copilot field experiment 使用自然工作环境及任务异质使标准化测量困难；不纳入未显示的效果量或普遍生产力结论。
- `K11/R03 turn158search2`：`INCLUDE`，只承载美国版权局官方发布所述政策立场；不替代法院对具体事实的裁决。
- `K10/R15 turn156search15`：`INCLUDE`，只证明 NIST NCCoE concept paper 把 strong authentication、least privilege 与 action intent 列为待解决标准问题；不是生效标准或效果验证。
- `K10/R18 turn156search17`：`INCLUDE`，只承载 CSA 文件所述 authentication、authorization、session management 与 credentials 控制内容；不证明有效性。
- `K10/R22 turn156search21`：`INCLUDE`，只承载 IMF 文件对 agent-initiated commerce 的 authorization、identity 与 account-holder boundary 讨论；不确认具体产品或法律代理关系。

### 跨查询重复

- `K13/R06 turn160search1` 与已纳入的 `K10/R02 turn156search1` 是同一 Microsoft Learn URL；canonical CE-IN 留在 `K10/R02`，`K13/R06` 最终为 `EXCLUDE:DUPLICATE`，保留 `K10+K13` 类别映射。
- `K13/R18 turn160search17` 与已纳入的 `K10/R15 turn156search15` 是同一 NIST PDF；canonical CE-IN 留在 `K10/R15`，`K13/R18` 最终为 `EXCLUDE:DUPLICATE`，保留 `K10+K13` 类别映射。

其余 CE 纳排差异只改变证据密度、载体或可承载范围，没有任何一个提供只存在于被排除结果中的新机制。被排除结果仍保留在 CATEGORY-DISCOVERY 账本；没有由这些分歧产生新的类别或承重 claim。

## 其他差异

- 六个 CD 纳排差最终采用：`K04/R28,R34,R37` 与 `K06/R34` 为 CD-OUT；`K13/R22,R30` 为 CD-IN/`EXISTING-K10+K13`，但 CE 仍为 `EXCLUDE:NO-METHOD`。
- 双方均排除但理由不同的 `116` 条不改变最终证据集合；采用 lead 对可见返回中 NO-METHOD、SECONDARY、PROMOTIONAL、DUPLICATE、STALE、FABRICATED 等标准码的逐条区分。
- K-set 差异均落在冻结 `K01`—`K13` 内；多重交叉映射由协议允许，没有一项需要 `K14` 或会丢失设计区别。
- exact-claim 与 scope 采用 lead 的可核验窄表述；independent 的 citation fragment 只用于原始定位，不扩大事实主张。

## S1 共同结论

- `NEW-CRITICAL`：`0`
- `UNRESOLVED`：`0`
- `NC-PROVISIONAL-S1-01`：共同裁决为 `EXISTING-K13`，其中一条 cross-map `K12`
- 第二个 provisional：未发现
- lead 最终同意：`AGREED`
- independent 最终同意：`AGREED`

因此，S1 第一次共同裁决已经完成，协议允许在本文件封存并计算 SHA-256、执行清单记录该 hash 后开始 S2。该结论只授权按冻结协议继续检索，不授权修改代码本、S2 查询、总体设计状态或任何外部商业动作，也绝不构成类别饱和结论。
