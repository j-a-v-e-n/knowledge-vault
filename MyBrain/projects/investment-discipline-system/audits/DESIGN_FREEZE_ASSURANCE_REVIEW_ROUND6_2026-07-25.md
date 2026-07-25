# 设计冻结保障审查 R6｜2026-07-25

状态：`blocked-freeze`

候选 commit：`0683a9c3b8d25854b08750641a62f88b4f86560c`

候选 tree：`41d04b1806c2b0eff6c72b0d26964b3a89fdf0d0`

## 候选形成与基线证据

候选已推送到合同固定的 `origin/main`。构造者直接 `ls-remote`、GitHub fresh clone、clone 内候选治理验证、四类 canonical replay、Ruff、compileall、diff check 和全量治理回归均通过。

本地全量回归：

```text
Ran 113 tests in 188.599s
OK
```

GitHub fresh clone 全量回归：

```text
Ran 113 tests in 188.787s
OK
```

这些绿灯随后被三路独立审查证明仍不足以支持冻结。

## 审查主体

- `SUBJECT-DESIGN-REVIEW-ZENO-R6`
  - locator：`subagent:019f99b8-3696-7cd2-a22a-128d9fb701c0`
  - 角色：保障机制与 trust boundary 只读审查
- `SUBJECT-DESIGN-REVIEW-DARWIN-R6`
  - locator：`subagent:019f99b8-756e-76c3-b3b8-01c5bd5070e0`
  - 角色：用户意图、研究充分性与双向追踪只读审查
- `SUBJECT-DESIGN-REVIEW-HILBERT-R6`
  - locator：`subagent:019f99b8-aabd-7663-95ce-59e57adfaac9`
  - 角色：测试 oracle 与构造者未知探针只读审查

三者均在候选 commit/tree 固定后启动，没有参与该候选构造，也没有写项目文件。

## Open critical

### GOV-MECH-CRIT-001｜独立 reviewer 身份与结果来源只有自报

passing fixture 可以由构造者自行创建 reviewer subject、locator、参与历史、raw stdout、退出码和哈希，再被治理验证器与 freezer 接受。现有 Git 与 fresh clone 只能证明这些字节被提交和恢复，不能证明它们来自独立主体。

Zeno 将其识别为新的架构类别：**独立审查身份与结果来源的可信边界**。

### GOV-SCOPE-CRIT-001｜最终审查范围漏掉 ground truth 与研究主体

最终审查强制范围没有自动包含 `PROJECT_CHARTER.md`、`DECISIONS.md`、AI 方法主体和 research register 的全部 `primary_artifacts`。passing review 可以只审构造者选择过的摘要，而不审原始意图、失效地图和研究主体。

### RES-CLOSURE-CRIT-001｜研究 stop rule 只是可翻转布尔值

search log 没有冻结结果集合、纳入/排除、来源簇、claim entailment、停止预算和补充轮架构差异。closure 又只允许把 `stop_rule.met` 从 `false` 改成 `true`，导致研究充分性没有可执行 receipt。

### GOV-NOVELTY-CRIT-001｜机器路径拒绝真正的 reviewer novelty probe

规范要求候选固定后由 reviewer 新增构造者未知探针，但 schema 和 verifier 只接受四个构造者预先知道的 canonical ID，额外 probe 会作为 `extra` 被拒绝。

## Open major

### GOV-MECH-MAJ-006｜raw attack result 与实际执行没有绑定

raw evidence 中的 command、`exit_code` 和 stdout 可手写。wrapper `exit_code == 0` 表示 unittest 通过，raw `exit_code != 0` 声称目标 verifier 拒绝，但两者没有机器关系。

Hilbert 的候选后新探针把四份 raw command 改成实际退出 `0` 的无害命令，同时声明 `exit_code=73` 并重算所有内部哈希。实际结果：

```text
declared_command=python3 -c "raise SystemExit(0)"
actual_command_exit=0
declared_raw_exit=73
expected_verifier_exit=nonzero
actual_verifier_exit=0
governance verification: PASS (candidate)
```

### GOV-TRACE-MAJ-001｜失效类别没有双向无孤儿追踪

当前只检查 requirement 填写的 hazard 是否存在，没有检查每个冻结范围内高影响 failure class 是否被 requirement、control、verification 和 case 消费。现有类别可成为 orphan 而全量治理回归仍绿。

### GOV-AUTH-MAJ-001｜可逆技术选择缺少 authority provenance

`DECISIONS.md` 仍把市场、数据源、技术保证和回测条件列为待确认，候选合同却固定了美国股票/ETF、SQLite 和 Tiingo 角色。选择本身未被判错，但缺少 `human_confirmed`、`delegated_reversible_v1` 或 `conditional` 的明确 authority/status/source/rationale/reversibility。

## 已确认仍有效的机制

- R5 未变异 baseline 与 Git context 修复有效。
- C→B 路径、mode/type/blob 限制与 D 单父提交结构有效。
- trusted remote、fresh clone、inner receipt 和 full-outer 的既有反例有效。
- 条件门 receipt 对候选、bundle、主事件链、最新 observation、raw hash 和 run ID 的既有反例有效。
- 当前设计没有 live broker 或真实资金执行路径。

## 裁决

候选 `0683a9c3...` 已 supersede，不能关闭 research stop rule，不能生成 frozen bundle。

下一候选必须同时完成：

1. 采用显式 assurance trust model，区分 GitHub/Sigstore 机器执行 provenance 与 Codex 平台可观察的上下文隔离语义审查，并禁止夸大为组织级密码学独立；
2. 固定 runner 实际生成 baseline、mutation、target 和 harness 的结构化执行 receipt；
3. 把完整 ground truth、方法主体和 research primary artifacts 自动展开到冻结与最终审查范围；
4. 增加机器可读 research sufficiency receipt，由验证器推导 stop-rule eligibility；
5. 分离 canonical regression 与候选后 novelty probes，后者至少一项且由冻结 runner 可复演；
6. 建立 failure-class 一等 registry 与双向无孤儿检查；
7. 为会改变产品边界的决定记录 authority provenance；
8. 形成新 commit/tree 后重新执行本地、GitHub signed Actions receipt、fresh clone 和全新独立挑战。

专项设计依据见 `research/ASSURANCE_PROVENANCE_REFRESH_2026-07-25.md`。
