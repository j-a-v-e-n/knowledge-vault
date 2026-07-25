# 设计冻结独立挑战｜Round 2

状态：`blocked-freeze`  
候选 commit：`c33ecbf19d07d2bf25ec07aeae974c51a8cd323f`  
候选 tree：`7fb9c3a2157064ac4406afe032f54543263dd060`  
审查主体：`SUBJECT-DESIGN-REVIEW-GOODALL-R2`  
工具 locator：`subagent:019f98b4-0679-78b1-9454-3b246dda4f0c`  
参与候选构造：`false`  
写候选文件：`false`  
作者完成总结作为输入：`false`

## 审查边界

审查者直接读取了用户原文、意图、验收合同、verification specs、traceability、研究登记、assurance subjects、产品蓝图、AI 项目失效地图、正式数据边界、旧系统审计、治理脚本、mutation tests 和旧 prototype。所有 mutation 只在 `/private/tmp` 隔离副本执行。

## 总裁决

`BLOCK FREEZE`

- `core_release_candidate`：阻断。
- `personal_core_accepted`：不可判定。
- 投资优势、长期纪律改善、Tiingo 真实可用：未证明。
- 第二轮仍发现改变 schema、状态机和 release predicate 的高影响类别，研究 stop rule 不能关闭。

## Critical

### R2-C01｜结构完整不等于语义完整

候选 verifier 只检查 verification ID、非空字符串、路径前缀和反向绑定，不检查 oracle 的具体语义、fixture 的精确输入/输出、selector 是否解析到真实测试或阶段性目标是否存在。

隔离 mutation：

- 把所有 oracle 改为 `always pass`。
- 清空全部负例。
- 把 PIT 要求改成允许未来数据。
- 把实现路径和 mandatory gate 改成不存在的名称。

实际结果：

```text
governance verification: PASS (candidate)
```

关闭证据：冻结结构化不变量、精确 case 输入/动作/期望、selector/target 生命周期；上述 mutation 必须被 governance tests 拒绝。

### R2-C02｜用户原文存在扩写，真实 validation 可被一次演示替代

`USR-06` 只表达“好的设计、好的搭建”，不足以单独证明 `UV-06` 的全部扩展语义。`personal_core_accepted` 仅一条旅程即可取得，field-use gate 没有冻结持续窗口、真实任务样本、操作负担、放弃阈值或行为改善 oracle。

失败情景：一条容易 fixture 旅程通过后获得 personal verdict，随后因录入负担完全弃用。

关闭证据：更直接的 Javen 原文、真实 ConOps/任务、onboarding 与长期 validation 分离、预注册 field-use protocol；失败必须重新进入设计而不只是限制宣传。

### R2-C03｜条件门是孤儿

合同引用的以下 gate 不存在于 gate catalog：

- `GATE-TIINGO-LIVE-PROBE`
- `GATE-LONGITUDINAL-EVALUATION`
- `GATE-JAVEN-FIELD-USE`

`EX-CONDITIONAL` 指向的 `scripts/verify_conditionals.py` 也不存在。

失败情景：长期门永久停在 `not_yet_observable`，没有执行器阻止错误状态转换；离线 fixture 被扩大成真实数据验收。

关闭证据：条件 gate catalog、实际命令、状态 schema、精确 oracle、聚合规则和失败测试；真实 personal journey 至少绑定一份非 fixture 市场快照。

### R2-C04｜引用完整不等于证据集合不误导

来源模型缺少 correction/retraction/supersession 传播、转载去重、事件发生时间与发布时间分离、检索范围与纳入/排除记录。合同“不能作为唯一依据”和蓝图“fail closed”语义不一致。

失败情景：多篇文章全部转述同一新闻稿，后续更正未关联；每条 byte range/hash 都正确，但同一来源被重复计票且反证未检索。

关闭证据：source revision graph、来源簇去重、检索 manifest、更正/撤回级联失效，以及决定性 claim 的单一明确闸门。

### R2-C05｜PIT 与 benchmark 口径仍可给出错误比较

旧 prototype 的实测反例：

```json
{
  "late_retrieval_errors": [],
  "zip_length_mismatch_no_future": true
}
```

同时旧 `23` 个测试全部通过。旧 runner 还使用日期交集，benchmark 明确不含分红。

关闭证据：把上述探针冻结为新验收 case；明确 security/universe as-of、市场日历、决策—成交时序、total-return benchmark、现金流、benchmark suitability，并与独立参考序列核对。

### R2-C06｜experiment family 可重命名逃逸

合同没有定义“相近假设”的机器/独立裁决、污染默认值、跨 universe/benchmark/清洗方案的根谱系，也没有最低信息量、依赖样本、多重选择或顺序停止裁决。

失败情景：语义相同策略换 family 名，只推进赢家；模型污染写成未知；短期未来样本后自行判 passed。

关闭证据：不可重置 root lineage、独立 family adjudication、污染默认 fail closed、预注册统计决策计划和纵向 oracle。

### R2-C07｜human capability 不等于冷静决定

`EX-HUMAN` 未用于关键 verification；自动化执行器承担 `V-HUMAN-CAPABILITY`。首个 mandate/policy 没有冷静期。旧闸门只要求 emotion 非空。

旧 prototype 实测：

```json
{"panic_decision_allowed": true}
```

关闭证据：结构验证与真实人类旅程分门；首个 mandate 冷静期；结构化紧迫度触发确定性等待/阻断；anti-rubber-stamp case 与剩余威胁声明。

### R2-C08｜“已推送”只由本地 remote-tracking ref 声称

`verify_git_state.py` 只比较本地 `@{upstream}` 并读取 origin URL，没有直接查询远端或 fresh clone。

失败情景：本地 remote-tracking ref 指向候选，但远端不可访问或没有该对象，检查仍 pass。

关闭证据：`git ls-remote` 直接观察远端 ref；发布阶段从远端 fresh clone 确切 SHA、重算 tree/blob 并运行核心验收。

## Major

### R2-M01｜Money 与公司行动没有冻结会计语义

缺少 price/quantity/money/fee scale、rounding、守恒方程，以及 merger、spin-off、cash-in-lieu、delisting、correction/reversal 的解决状态。

旧 prototype 审计写入失败后的实测：

```json
{
  "cash_after_audit_failure": "900",
  "fills_after_audit_failure": 1
}
```

关闭证据：冻结 Money 规格、守恒方程、公司行动矩阵和人工解决状态，贯穿 NAV、风险、重放、benchmark 和三轨。

### R2-M02｜restart/restore 不等于长期停用恢复

`long_gap_resume` 只有名字，没有间隔、输入状态或 expected。停用后旧决定、批准、数据、许可、模型/Prompt 可能仍显示可继续。

关闭证据：hiatus/resume 状态机、时钟跳跃、批准失效、数据/政策/许可/migration 重验和恢复摘要。

### R2-M03｜私人备份只有完整性，没有保密生命周期

备份要求缺少文件权限、静态加密/OS 继承边界、密钥恢复、保留/删除和备份目的地约束。

失败情景：私人数据库明文进入同步目录；hash 和 restore 全部通过，但隐私目标失败。

关闭证据：at-rest threat model、OS 权限/加密策略、恢复边界、日志/导出脱敏、目的地与保留策略测试。

## 新增架构级类别

1. 证据语料完整性与更正传播。
2. benchmark 与模拟市场有效性。
3. 行为表格被机械填写或自我误报绕过。
4. 长期停用后的重新授权与语义过期。
5. 私人运行数据的保密恢复。

## 已确认仍然成立

- 候选 commit/tree 固定且当时项目作用域 clean。
- 候选诚实保持 paper-only、no-live 和不声称投资优势。
- 设计已区分引用完整性/语义蕴含、当前快照/PIT vintage、Paper P&L/实盘可实现性。
- 研究登记仍为 `challenge.status=in_progress`、`stop_rule.met=false`，没有伪称关闭。

## 处理决定

本轮全部 Critical/Major 保持 open，先转成机器可读要求、领域规范、case、状态机和执行器；修订后重新固定候选并进行下一轮独立挑战。
