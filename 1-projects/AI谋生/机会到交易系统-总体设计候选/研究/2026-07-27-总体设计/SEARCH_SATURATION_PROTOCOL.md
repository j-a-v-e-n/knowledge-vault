# 未来检索类别饱和协议

- 协议版本：`SSP-1.0`
- 协议状态：`FROZEN`
- 冻结日期：`2026-07-27`
- 执行状态：`NOT_RUN`
- 饱和状态：`NOT_ESTABLISHED`
- 指定引擎：`Codex web search`

## 1. 目的与非追认声明

本协议只约束冻结之后的未来检索，用于判断：在本项目已经声明的研究范围内，两轮预先写死的对抗性检索是否还会发现改变总体设计的**新关键类别**。

本协议不追认任何历史搜索、历史来源列表、历史“饱和复查”或历史闭合结论。冻结时间之前已经执行的查询、已经打开的网页和已经形成的判断可以作为背景材料，但一律不得计入本协议的 `S1` 或 `S2`，也不得据此把 `NOT_ESTABLISHED` 改为已饱和。

本文件本身不证明已经完成检索，也不证明已经达到饱和。只有与本协议精确身份绑定的未来执行记录，经过 lead 与独立审查者共同裁决后，才可能形成限定范围内的类别饱和结论。

允许的最终表述仅为：

> 在本协议声明的范围、引擎、查询、返回结果与审查规则内，两轮预注册检索没有产生新的关键类别。

禁止表述为“搜完了全网”“资料已经穷尽”“不存在其他类别”或“系统已经被证明完整”。

## 2. 协议身份、冻结与失效

1. 执行开始前，执行者必须对本文件的精确字节计算 `SHA-256`，并把 `协议版本 + SHA-256 + 文件路径 + 执行开始时间` 写入单独的执行清单。
2. 哈希不写回本文件；否则会造成自引用哈希。执行清单中的哈希是该次执行唯一有效的协议身份。
3. 冻结后，查询文字、引擎、类别定义、筛选规则、纳入/排除规则、判定规则和审查角色均不得在执行中解释性改写。
4. 本文件任何字节发生变化，都必须同时提升协议版本并产生新的 `SHA-256`。旧哈希立即失去对当前或未来饱和判断的效力，只能保留为历史审计记录。
5. 不得用勘误、口头说明、执行日志备注或事后解释修改冻结协议。需要修改时，必须发布新版本并从 `S1` 开始重新执行。
6. 任何执行记录若不能与一个精确的协议版本和哈希绑定，其结果均为 `INVALID`。

## 3. 判定对象：什么叫新关键类别

### 3.1 新类别

一个检索发现只有同时满足以下条件，才构成“新类别”：

1. 它描述了一个独立的因果机制、失效机制、外部约束、行动主体或伤害路径；
2. 把它归入 `K01`—`K13` 任一现有类别会丢失对系统设计有用的区别，而不是只需给现有类别增加例子或同义词；
3. 它能够被写成可复查的类别定义，并能指出至少一种应被纳入或排除的证据。

以下情况本身不算新类别：

- 同一机制的新案例、新行业、新国家或新产品；
- 已有类别下的新指标、术语、数据集或严重程度；
- 对既有结论提供更强支持、较弱支持或直接反证；
- 只改变参数值而不改变系统模块、Gate、权限或状态语义；
- 无法区分于来源作者的修辞性重新命名。

### 3.2 关键类别

一个新类别只要满足下列任一条件，就属于“关键”：

- 要求新增、删除或重构一个系统模块、确定性 Gate、状态转换或证据维度；
- 改变某类外部动作能否自主执行、是否需要人的批准，或是否必须 fail closed；
- 改变至少一个承重主张成立所需的真值条件；
- 暴露一个此前未建模的主体、资源、权利、责任或伤害路径，足以制造虚假需求、虚假交易、错误交付或不可接受风险；
- 使当前总体架构即使按原设计正确运行，也可能系统性地产生错误结论或越权行为。

“有趣”“值得以后研究”或“可能提高效果”不等于“关键”。

### 3.3 禁止强行归类

若任一审查者认为某发现可能满足新关键类别定义，该发现必须先进入 `NC-PROVISIONAL`，不得为了维持饱和结论而强行塞入 `K01`—`K13`。只有 lead 与独立审查者共同完成书面裁决后，才能判定为：

- `EXISTING-Kxx`：现有类别的实例或子机制；
- `NEW-CRITICAL`：新的关键类别；
- `NEW-NONCRITICAL`：新但不改变承重设计；
- `UNRESOLVED`：证据或分歧尚不足。

任何 `NEW-CRITICAL` 或 `UNRESOLVED` 都禁止作出饱和结论。

## 4. 冻结类别代码本 K01—K13

| 代码 | 冻结类别 | 纳入边界 | 不纳入边界 |
|---|---|---|---|
| `K01` | 网络偏差 | 网络投诉、评论、UGC、搜索趋势和数字足迹中的自选择、沉默群体、平台排序、虚假内容、幸存者偏差、人口与地域偏差、时间漂移，以及由此产生的需求误判 | 一般性的模型幻觉归入 `K09`；具体隐性需求推断归入 `K02` |
| `K02` | 隐性需求 | 未被直接表达的需要、行为摩擦、workaround、Lead User、情境观察、民族志、Demo 唤醒、构造偏好，以及把观察转为需求假设时的投射风险 | 买方是否可触达归入 `K03`；口头意向到付款的差距归入 `K04` |
| `K03` | 买方可达 | 用户、受益者、经济买家、批准者与预算持有人分离；渠道、获客、采购流程、信任、销售周期、组织 buying center 与接触合法性 | 付款意向的测量偏差归入 `K04`；身份认证和账户控制归入 `K10` |
| `K04` | 意图付款 | 态度、兴趣、点击、回复、访谈、LOI、等待名单、预购、定金、付费 Pilot、真实支付意愿及其假阳性与意向—行为差距 | 付款之后的使用、交付、退款与留存归入 `K05` |
| `K05` | 交付负态 | 已成交之后的未使用、实施失败、拒收、质量缺陷、退款、流失、支持负担、未达结果、负留存，以及将一次付款误判为持续价值 | 生产效率本身归入 `K08`；Agent 执行可靠性归入 `K09` |
| `K06` | 竞争、价值捕获与权利 | 替代品、竞争反应、模仿、互补资产、定价与单位经济、议价权、价值创造与价值捕获分离，以及交付物、数据、品牌、许可证和知识产权的权利归属 | 法律合规和侵权风险归入 `K11`；客户采用切换摩擦主要归入 `K03` |
| `K07` | 实验组合 | Customer Discovery、Lean Startup、MVP、A/B、烟雾测试、Wizard-of-Oz、concierge、预注册、测试组合、样本偏差、假阳性/假阴性、停止与 Pivot 规则及外部有效性 | 具体意向或付款证据的强弱归入 `K04` |
| `K08` | AI 生产力 | 生成式 AI 对速度、质量、成本、技能差异、任务边界和生产函数的真实影响，以及“AI使原本不经济的需求变得可做”的证据与边界 | 长任务 Agent 自主执行可靠性归入 `K09`；授权范围归入 `K13` |
| `K09` | Agent 可靠性 | 工具调用、长任务、状态恢复、错误复合、多 Agent 协调、评测缺陷、提示注入、奖励黑客、终态误报和开放环境失败 | 账户身份归入 `K10`；能力是否获授权归入 `K13` |
| `K10` | 身份与权限 | 账户所有权、认证、代表权、批准者身份、凭据、付款与收款身份、签约权限、冒充、审计主体和权限生命周期 | 能力策略与动作范围归入 `K13`；具体法律规则归入 `K11` |
| `K11` | 合规与 IP | 隐私、数据保护、抓取、平台条款、营销与反垃圾信息、消费者保护、合同、税务、许可、版权、商标、专利、许可证和司法辖区差异 | 不一定违法但会造成操纵或伤害的行为归入 `K12` |
| `K12` | 伦理伤害 | 欺骗、操纵、dark patterns、脆弱群体利用、歧视、监控、隐私侵犯、客户反感、工作与社会伤害，以及合法但不可接受的销售行为 | 明确法律义务归入 `K11`；越权机制归入 `K13` |
| `K13` | 能力授权 | 可用能力与获准能力的分离；最小权限、动作范围、确定性策略、审批、预算、速率、可逆性、fail-closed、撤销、监控与责任升级 | 身份和凭据归入 `K10`；底层 Agent 错误率归入 `K09` |

允许一条来源同时命中多个现有类别。多重编码不构成新类别。

## 5. 执行引擎与固定设置

1. 所有搜索必须使用 `Codex web search`。
2. 每条查询必须单独执行，不得合并、拆分、翻译、扩写、增加 domain、增加日期、替换同义词或追加追问。
3. 查询字符串必须逐字复制第 6 节中的代码块内容；代码块外的反引号和编号不是查询的一部分。
4. 每次调用使用该引擎可用的最长结果模式 `response_length: long`。
5. 必须保存每次调用的：协议哈希、轮次、类别、精确查询、开始时间、结束时间、引擎返回的全部可见结果、错误和重试记录。
6. 必须筛选引擎在该次完整响应中返回的每一个不同结果，不得只筛选排名靠前或支持既有设计的结果。
7. 可以打开返回结果、原始 DOI、官方页面、论文附件及同一来源直接链接的方法/附录；这种取回不构成新增搜索查询，但必须记入来源链。
8. 不允许在本协议执行中进行未预注册的补充搜索、citation query 或关键词追搜。若某个结果暴露出需要补搜的新概念，应记录为 `NC-PROVISIONAL`，不得临时扩充查询。

## 6. 两轮精确查询

### S1：机制与直接边界

`S1-K01`

```text
online complaints reviews social media user generated content sampling bias representativeness market demand systematic review
```

`S1-K02`

```text
latent unarticulated customer needs observation ethnography lead users empirical evidence limitations
```

`S1-K03`

```text
B2B buying center economic buyer decision authority customer reach distribution channel startup empirical
```

`S1-K04`

```text
purchase intention actual purchase behavior willingness to pay hypothetical bias meta analysis
```

`S1-K05`

```text
startup paid pilot delivery failure refunds churn retention service quality negative outcomes empirical
```

`S1-K06`

```text
innovation value capture competition imitation complementary assets intellectual property business model empirical
```

`S1-K07`

```text
lean startup experimentation randomized controlled trial customer discovery MVP evidence systematic review
```

`S1-K08`

```text
generative AI productivity field experiment real work quality heterogeneity randomized controlled trial
```

`S1-K09`

```text
AI agents long horizon task reliability benchmark compounding errors tool use real world evaluation
```

`S1-K10`

```text
AI agent identity authentication authorization least privilege external actions payment accounts
```

`S1-K11`

```text
generative AI autonomous marketing privacy consumer protection copyright intellectual property compliance United States European Union
```

`S1-K12`

```text
AI autonomous sales persuasion manipulation dark patterns discrimination vulnerable consumers ethical harms
```

`S1-K13`

```text
AI agent capability control delegated authority action scopes human approval safety framework
```

### S2：替代解释、反例与失效路径

`S2-K01`

```text
digital trace data platform algorithm self selection survivorship bias customer need discovery false positive
```

`S2-K02`

```text
constructed preferences prototype demo demand creation hidden needs false positive customer research
```

`S2-K03`

```text
market need but customer acquisition failure inaccessible buyers trust procurement switching costs startup
```

`S2-K04`

```text
customer interviews letters of intent waitlists preorders deposits paid pilots demand validation false positives
```

`S2-K05`

```text
product sold but not used implementation failure customer abandonment post purchase negative evidence
```

`S2-K06`

```text
customer willingness to pay competition substitutes unit economics appropriation rights startup failure
```

`S2-K07`

```text
entrepreneurial experiments false positive false negative sample bias bundled tests external validity
```

`S2-K08`

```text
generative AI productivity failure outside capability frontier novice expert field study
```

`S2-K09`

```text
multi agent systems coordination failure prompt injection state inconsistency benchmark limitations
```

`S2-K10`

```text
autonomous agents account access impersonation consent approval auditability security risks
```

`S2-K11`

```text
AI agent web scraping outreach terms of service data protection copyright licensing legal risk
```

`S2-K12`

```text
personalized AI marketing privacy intrusion spam deception customer backlash empirical
```

`S2-K13`

```text
autonomous systems capability authorization policy enforcement fail closed least privilege audit logs
```

## 7. 筛选与纳入/排除规则

### 7.1 双层筛选

每个返回结果必须分别接受两层判断：

1. `CATEGORY-DISCOVERY`：它是否描述可能的新机制、约束、主体或伤害路径？
2. `CLAIM-EVIDENCE`：它是否具有足够来源质量，可以支持或反驳一条承重主张？

低质量来源即使不能进入 `CLAIM-EVIDENCE`，只要提出了一个满足定义的潜在新类别，也必须进入 `NC-PROVISIONAL`，随后寻找本次返回结果中是否有独立高质量来源支持；不得因来源质量低而静默删除类别线索。

### 7.2 纳入 `CATEGORY-DISCOVERY`

满足以下任一条件即可纳入：

- 直接涉及 `K01`—`K13` 的机制、边界、反例或外部有效性；
- 直接挑战当前机会到交易架构的模块、Gate、状态、证据或权限假设；
- 描述从需求发现、验证、销售、付款、生产、交付到留存任一环节的系统性失败；
- 描述 AI/Harness/Agent 在真实任务中的能力边界、安全失败或授权问题；
- 描述可能改变自主动作边界的法律、权利或伦理风险。

### 7.3 纳入 `CLAIM-EVIDENCE` 的来源优先级

按下列顺序优先取回原始材料：

1. 同行评审系统综述、元分析、随机试验、现场实验和具有透明方法的纵向/因果研究；
2. 政府、监管机构、法院、标准组织和官方统计；
3. 原始论文、作者或机构正式技术报告、系统卡、官方文档和可复查评测；
4. 具有样本、方法、时间范围和限制说明的平台一手数据；
5. 具有可核验原始材料的案例和失败复盘，只支持其案例范围；
6. 从业者文章、新闻、论坛和单一帖子，只用于机制线索或证明该表达出现过。

对当前 AI 能力、平台规则与现行合规，必须优先使用执行时仍有效的官方或最新独立资料。对基础理论不设年代下限。

### 7.4 排除规则

结果可从 `CLAIM-EVIDENCE` 排除，但仍须留在筛选账本并写明一个标准化原因：

- `DUPLICATE`：同一原始来源或无新增内容的镜像；
- `OUT-OF-SCOPE`：与机会到交易系统及 `K01`—`K13` 无直接关系；
- `NO-METHOD`：作出普遍经验主张却没有样本、方法或原始依据；
- `SECONDARY-WHEN-PRIMARY-AVAILABLE`：可取得原始来源却只提供转述；
- `PROMOTIONAL-ONLY`：只证明厂商自报能力或营销承诺；
- `INACCESSIBLE-FOR-VERIFICATION`：只有标题/片段，关键方法和结论无法核验；
- `STALE-CURRENT-CLAIM`：用明显过期材料证明当前易变能力、规则或法律状态；
- `FABRICATED-OR-UNVERIFIABLE`：身份、来源或引用无法核验。

不得因为来源与当前设计冲突、结论为零、结果为负面、样本不便解释或会触发重启而排除。

### 7.5 一条来源的最低记录

每条结果至少记录：

- 轮次、查询代码和结果排名；
- 标题、作者/机构、日期、URL/DOI、来源类型；
- 纳入或排除决定及标准化原因；
- 支持、反驳或限制的精确主张；
- 命中的 `Kxx`；
- 是否进入 `NC-PROVISIONAL`；
- 适用范围、样本/方法和不可外推点；
- lead 编码、独立审查者编码及共同裁决。

## 8. 轮次顺序与独立审查

1. 先完整执行并冻结 `S1-K01` 至 `S1-K13` 的原始返回结果。
2. lead 与独立审查者使用同一协议、同一原始结果集分别筛选和编码；独立审查者必须在看到 lead 的最终类别裁决之前提交自己的初始记录。
3. 两者完成 `S1` 初始记录后进行第一次共同裁决，但不得修改代码本或 `S2` 查询。
4. 再完整执行并冻结 `S2-K01` 至 `S2-K13` 的原始返回结果，并重复独立编码与共同裁决。
5. 两轮之间即使发现 `NEW-CRITICAL`，本版本的 `S2` 仍按冻结查询执行，以保留对抗覆盖；但该版本已经不可能得到饱和结论。
6. lead 不能兼任独立审查者。独立审查者不得是撰写当前总体设计并负责证明其完成的人。
7. 共同裁决要求双方对每个 `NC-PROVISIONAL` 的最终状态、每个关键排除理由以及最终运行状态形成明确一致意见。多数票、lead 单方决定或 AI 自我批准均无效。

## 9. 运行状态与判定规则

一次执行只能取得以下状态之一：

### `SATURATED-WITHIN-PROTOCOL`

只有同时满足以下全部条件才能取得：

- 两轮共 `26` 条冻结查询均由指定引擎完整执行；
- 每个返回结果均有筛选记录；
- 所有原始来源链、排除理由和编码均可复查；
- `S1` 与 `S2` 均没有 `NEW-CRITICAL`；
- 最终没有 `UNRESOLVED`；
- lead 与独立审查者共同同意上述事实；
- 执行清单、结果集和裁决记录都绑定同一个未变更的协议版本与哈希。

该状态只表示类别代码本在本协议内未被两轮查询扩展，不表示事实结论全部正确，也不表示具体商机、完全自治或盈利已经验证。

### `NOT-SATURATED`

出现任一情况即为该状态：

- 任一轮出现至少一个 `NEW-CRITICAL`；
- 一个新发现要求改变总体架构、Gate、权限或承重主张；
- 现有类别定义存在会影响关键裁决的结构性空白。

### `INCOMPLETE`

出现任一情况即为该状态：

- 查询未执行、返回错误、结果被截断到无法筛选或执行日志缺失；
- 关键来源无法核验且其类别影响尚不清楚；
- 没有合格的独立审查者；
- 双方未完成共同裁决；
- 任一 `NC-PROVISIONAL` 最终为 `UNRESOLVED`。

### `INVALID`

出现任一情况即为该状态：

- 查询、引擎或规则被临时修改；
- 执行发生在冻结之前或无法证明发生在冻结之后；
- 执行记录未绑定协议哈希；
- 协议文件在两轮执行期间发生变化；
- 使用历史搜索结果替代任一冻结查询；
- 结果被选择性遗漏或事后重新定义“新关键类别”。

## 10. 重试与重启规则

### 10.1 同版本允许的机械重试

只有引擎超时、网络错误或没有形成完整响应时，才允许用**完全相同的查询和设置**重试。必须保留失败尝试。第一份完整响应是该查询的正式结果；若意外取得多份完整响应，必须筛选其并集，不得选择更有利的一份。

机械重试不能修复协议内容错误、类别歧义或审查分歧。

### 10.2 必须发布新版本并从 S1 重启

出现任一情况时，当前版本不得通过补丁继续：

- 发现 `NEW-CRITICAL`；
- 需要新增类别、改变类别边界或增加查询；
- 需要修改任何精确查询、引擎或筛选规则；
- 新证据表明“新关键类别”的定义存在会改变结果的歧义；
- 引擎发生实质性变化，无法认为仍是同一检索机制；
- 协议文件被修改或哈希不一致；
- lead 与独立审查者的关键分歧无法在冻结规则下解决。

新版本必须：

1. 保留本版本及其执行结果为历史记录；
2. 提升版本号并产生新哈希；
3. 把新关键类别正式加入代码本；
4. 为全部类别重新预注册两轮精确查询；
5. 不把旧版本结果追认为新版本的 `S1` 或 `S2`；
6. 从新版本的第一条 `S1` 查询完整重跑。

## 11. 最低完成包

未来若执行本协议，必须同时生成以下相互绑定的材料，缺一则为 `INCOMPLETE`：

- 协议身份清单；
- `26` 条查询的原始响应日志；
- 去重但不删除原始映射的结果台账；
- lead 独立筛选表；
- 独立审查者筛选表；
- `NC-PROVISIONAL` 共同裁决表；
- 纳入来源的主张—证据映射；
- 排除来源及原因清单；
- 最终状态记录；
- 范围、残余未知和不能声称事项。

## 12. 当前封印

截至 `2026-07-27`，本协议仅完成预注册并处于 `FROZEN / NOT_RUN / NOT_ESTABLISHED`。本文件没有运行任何 `S1` 或 `S2` 查询，也没有产生检索饱和结论。
