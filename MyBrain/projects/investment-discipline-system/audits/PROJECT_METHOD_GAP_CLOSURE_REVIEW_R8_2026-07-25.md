# 项目方法 gap closure 独立语义审查 R8｜2026-07-25

状态：`blocked-freeze`

裁决：**否决当前 gap closure；不得冻结。**

本审查是 Codex 平台可观察的 separate-thread review。它提供上下文与过程可见性，不构成安全隔离、密码学身份、组织独立性或技术上的只读强制。审查者遵守本轮只写本报告的任务边界，但当前 workspace 权限本身没有把候选文件变成不可写。

## 审查对象与候选绑定

本轮重跑所绑定的候选：

- branch：`codex/investment-assurance-r7`
- HEAD：`2fc2b710d0494afbf92a69855b35cf0e564b8540`
- tree：`65e1924ef2634fe41e85055f3e169359f2ca9bf2`
- 当次重跑前状态：branch 与 `origin/codex/investment-assurance-r7` 对齐，项目工作树 clean。

并发说明：

- 审查开始时观察到 HEAD `e9f4585037d19b4fef60b770f1ac5793fd279d5d`、tree `3349526ec2b6c424c14cc32937576a12fae17447`。
- 审查期间并发 backup commits 推进了 HEAD，并修改过本轮主输入之外的 workflow、trust model、ground-truth manifest、`scripts/verify_governance.py` 和另一测试。
- 指定主输入的 SHA-256 在前后观察中保持不变。支持调用链发生变化后，本报告在上述 `2fc2b710...` 候选上重新运行了项目方法 verifier、项目方法 mutation suite、候选治理 verifier 和失败的 attack-runner 基线测试。
- 本报告只对下列精确字节与该重跑候选作裁决；任何后续候选或输入变化都使本审查绑定失效。

## 输入 SHA-256

### 指定主输入

| path | SHA-256 |
| --- | --- |
| `governance/PROJECT_METHOD_POLICY_V1.json` | `552ff39732d210129e207cb4f752768e8195a6640368dad66d8ff61808f750ad` |
| `scripts/verify_project_method.py` | `343acfb51b0ab79470859e32227a259353eadaba32d6b8958571194c50f8d559` |
| `governance_tests/test_project_method.py` | `256b1a86614542161eef9f490fb86effb7b212973d17c53ce4eb623e721bbb7f` |
| `governance/ACCEPTANCE_CONTRACT_V1.json` | `82a88217c5ab6be1b9b444ca8fca7a118cde64f75dfed7846004a213c1f7660f` |
| `governance/ACCEPTANCE_CASES_V1.json` | `51fbfe8203d62b56c04b6e050d7481fed413f0c6ec81cbcee71efded292080e8` |
| `governance/VERIFICATION_SPECS_V1.json` | `adbc13b6227cf5ee163400d4a405059c9594aa2ae3187e2e97109bbc87170c4c` |
| `governance/TRACEABILITY_V1.json` | `bc7c2956f50ebd34ddc7639c63f85781d74a22900e75c94ab3a11757122b3407` |
| `governance/IMPLEMENTATION_TARGETS_V1.json` | `eac4989de824013ba775ceba56a55af040e32a0047fdfe203c6b260263a49c1c` |
| `governance/FAILURE_CLASSES_V1.json` | `f4918be6c32bec1c0e8d8cd4b493dc69f466e0b26bd01da867ce3d46c03b010c` |

### 为判断实际调用链直接跟读的输入

| path | SHA-256 |
| --- | --- |
| `scripts/verify_governance.py` | `8c6b7bcff439e16c5dc89acc62cec79fdcf6ee17f56458bd9f3334d57db1e56d` |
| `scripts/run_assurance_ci.py` | `173abafb2674d0224d0f467f1b85c66b1537e9a4d3e0eb02171d3b0a97981e5d` |
| `governance_tests/test_attack_runner.py` | `ffd460465db36685738eadd87e4b385f095647381632af2bab840475ea96bfd1` |
| `scripts/verify_contract_supersession.py` | `f19f313938fe72a89e77fbf5399b55d60ae25df23adfb4a64d2bf7638f957d5f` |
| `governance/GROUND_TRUTH_MANIFEST_V1.json` | `e8f4d54a20f41ebb7b5d9645f6897c6ee546f8e635291333c2ed3d67cbf7aaca` |
| `research/AI_PROJECT_FAILURE_TAXONOMY_2026-07-25.md` | `06b1fa2978ab18149e77b3e346279515418d9b3d6ffc5c6ee333a2abcd04606b` |
| `AI_COLLABORATION_METHOD.md` | `2351a0bbd9f5f7449feec7aee4cb3a7046438c26b293a26ffb5af30c84f09cfb` |

## 状态语义

- `covered`：存在候选绑定的实际机制，且对应反例真正驱动该机制并由与 failure 相符的 oracle 观察。
- `partially_covered`：存在有价值的规范、冻结或局部执行控制，但 mutation 只锁字段，或仍缺少会改变结论的行为证据。
- `gap`：没有可执行的对应机制，或声称的机制当前不能运行；字段、标签或文件存在性不能替代它。

按此语义，结构上“有 requirement/control/verification/case ID”不等于 failure 已 `covered`。本轮没有任何一项达到完整 `covered`。

## 阻断发现

### `PM-GAP-CRITICAL-CIRCULAR-CLOSURE`｜closure oracle 循环信任 `covered`

`scripts/verify_project_method.py` 没有从每个 failure 的行为证据推导状态。它读取 `FAILURE_CLASSES_V1.json` 后，直接要求每项已经写成 `status="covered"`、`open_gaps=[]`，并要求顶层 `gap_failure_classes=0`、`open_gap_ids=[]`。因此 registry 的结论成为 verifier 的前提，而不是 verifier 的输出。

本轮构造了不修改候选输入的临时最小夹具。夹具只有 policy、failure registry、空的 required-state 文件和一个空的 incident regression 路径；它没有 acceptance contract，也没有任何 work-packet instance。实际观察：

```text
fixture_has_acceptance_contract=False
fixture_has_work_packet_instance=False
fixture_state_file_bytes=0
exit=0
{"error_count": 0, "errors": [], "status": "pass"}
```

这证明 verifier 可在 CTX-02、ORG-03、HUM-05、ECO-03 等实际机制完全不存在时仍给出 pass。`FAILURE_CLASSES_V1.json` 中 `total_failure_classes=74`、`covered_failure_classes=74`、`gap_failure_classes=0` 的摘要不能作为独立 closure 证据。

影响：`REQ-METHOD-001` 被标为 `critical`，而它唯一绑定的 `V-PROJECT-METHOD` 可在无行为机制的夹具上 false-green。该问题单独阻塞 freeze。

### `PM-GAP-MAJOR-MUTATION-WIRING`｜mutation 运行存在，但正式 V/oracle 绑定没有闭合

`governance_tests/test_project_method.py` 的共同 harness 做了有价值的两件事：每次 mutation 前要求 baseline 通过，并检查目标错误文本至少出现一次。本轮全部定向测试也确实执行并通过。

但正式绑定仍有以下缺口：

- `V-PROJECT-METHOD` 指定 `EX-GOVERNANCE`；`scripts/verify_governance.py` 只调用 baseline `verify_project_method.py --json`，不执行这些 mutation。
- `scripts/run_assurance_ci.py` 通过独立的 `CHECK-GOVERNANCE-REGRESSION` 执行整个 `governance_tests/`，所以 mutation 在完整 CI 中有执行路径；但这条路径没有生成 `V-PROJECT-METHOD` 结果 schema 所要求的逐 case `acceptance_case_results`、`oracle_observations`、`selector_observation` 和 raw-result binding。
- `operation_catalog.selector` 与 `V-PROJECT-METHOD.test_selector` 只被正则检查为“可解析形状”，没有解析到实际 callable。真正可运行的是 case 里的自由文本 unittest command。
- `O-FAIL-CLOSED` 要求 `protected_state_unchanged_or_recovery_explicit` 与 `reason_code_equal`；当前 test 只检查外层 unittest 成功、内层 verifier 非零和自然语言错误 substring。
- 候选中不存在声明的 `evidence/verification/V-PROJECT-METHOD.json`。设计冻结可允许产品行为 `not_run_preimplementation`，但 `V-PROJECT-METHOD.required_for=["design_freeze"]` 本身不是产品行为。
- `CASE-METHOD-FROZEN-TEST-DELETED` 没有删除、skip 或 xfail 任何冻结测试；它只把 policy 的 `baseline_must_pass_before_mutation` 从 `true` 改为 `false`。case ID、failure VER-07 与实际 mutation 不同义。

影响：可以说“policy 的精确字段弱化会被当前 unit test 拒绝”，不能说“17 个 failure 的正式 fail-closed oracle 已逐项闭合”。

### `PM-GAP-MAJOR-INCIDENT-REGRESSION`｜OPS-08 指向的回归当前 baseline 失败

policy 的 `INC-R5-NON-ISOLATED-ORACLE` 把 `governance_tests/test_attack_runner.py` 指定为 regression，并声称 preventive control 会保留 Git objects、project prefix、origin 和完整候选上下文。`verify_project_method.py` 只检查这个 path 是文件，不运行它，也不检查它与 incident 的因果关系。

本轮实际运行该 regression：

```text
Ran 4 tests in 5.356s
FAILED (failures=3, errors=1)
```

在最终候选上重跑其基线隔离测试：

```text
Ran 1 test in 3.081s
FAILED (failures=1)
```

目标 runner 没有到达 mutation。未变异 baseline 已以 `runner_exit_code=2`、`result="invalid_baseline"` 失败，原因是：

```text
assurance metadata executable verification failed:
verifier setup: project root must be a non-root repository subtree
```

`governance_tests/test_attack_runner.py` 把复制出的 project 直接初始化成 Git repository root，得到空 `project_prefix`；这与 incident record 所写的 preventive control 相冲突。与此同时，`test_incident_without_regression_is_rejected` 和候选治理 verifier 仍为绿，形成可复现 false-green。

影响：OPS-08 仍是 `gap`；该失败也证明文件存在性不是 regression oracle。当前候选不能进入 freeze。

### `PM-GAP-MAJOR-IRREDUCIBLE-BEHAVIOR`｜静态 policy mutation 过度关闭行为与长期 failure

- CTX-02：删除字符串 `middle` 会被拒绝，但没有长上下文输入、sentinel 内容、检索器、位置随机化、compaction/restart/stale-request 执行或召回/遗漏 oracle。它仍是 `gap`。
- ORG-03：把 `parallel_write_rule` 改成允许共享路径会被拒绝，但没有 active packet registry、规范化路径相交检查、worktree/ownership 执行、并发写实验、merge 后集成测试或语义 diff。尤其不能检测“无文本冲突但行为冲突”。它仍是 `gap`。
- HUM-05：policy 正确写明 fixture 不能证明 comprehension，并把真实理解放到 `human_onboarding_and_longitudinal_conditional`；但 failure registry 同时写 `covered` 和 `open_gaps=[]`。设计冻结只能锁解释 schema，不能证明真实非专业用户理解风险、后果与未知。它只能是 `partially_covered`。
- ECO-03：删除 `removal_path` 字段会被拒绝，但没有 component inventory、真实 contract/test/observability 审计、重复与耦合趋势、migration 演练、重构预算执行、架构风险复核或纵向维护成本。长期技术债不能由一次静态字段 mutation 关闭。它仍是 `gap`。

## 逐 failure 裁决

| failure | actual mechanism | mutation 是否到达对应 oracle | 设计冻结能证明 | 设计冻结不能证明 | status |
| --- | --- | --- | --- | --- | --- |
| GOV-04 | 规范文件进入 hash/Git/bundle 边界；另有 `verify_contract_supersession.py` | mutation 能触发 `monotonic_rule differs`，但只测 policy 文字；supersession verifier 未在本 V 中执行 | 当前 V1 的禁止弱化文字和 frozen-file 边界可锁定 | V2/conditional 的真实语义单调性、human exception provenance、supersession 自动执行 | `partially_covered` |
| GOV-07 | old/new contract diff 能检查 statement、severity、scope、non-goal 和 conditional gate 的精确变化 | mutation 截短 `conditional_gate_rule`，触发 phrase oracle；没有运行 old→new contract | 当前规则包含“不能弱化”的必要短语 | 同义改写、拆分 requirement、放宽 selector/oracle、未被调用的 supersession path | `partially_covered` |
| CTX-02 | required-state 文件清单与 position-probe 标签；文件仅检查 `is_file()` | 只证明删除 `middle` 标签会失败 | probe 名称与 state-file 名称被保留 | 真实长上下文检索、位置效应、compaction、restart、stale-request 和遗漏率 | `gap` |
| ORG-01 | work-packet 字段与 forbidden write-scope 合同；本轮人工任务边界有效 | 删除 `/` 会触发 exact-set oracle | policy 不允许根路径和未声明路径 | packet instance validator、实际写入拦截、checkpoint/receipt 完整性和半成品恢复 | `partially_covered` |
| ORG-03 | 只有 disjoint-write 自然语言规则 | 改写规则会触发 exact-string oracle | 禁止共享写路径的意图被锁定 | 并发路径冲突、symlink/canonical path、共享状态、无文本冲突的语义覆盖与集成行为 | `gap` |
| ORG-04 | policy 定义 execution states、same-blocker threshold、blocked 与 bounded-incomplete | `max_consecutive_same_blocker_turns` 从 `3` 改成 `4` 会命中目标分支 | 阈值和终态文字不可静默改变 | blocker 身份判定、计数持久化、真实停止、替代路径和预算执行 | `partially_covered` |
| ORG-05 | harness admission schema、same-task 字段与默认 `not_adopted` | 把 missing-ablation outcome 改为 `adopted` 会命中目标分支 | 缺少消融时政策不得采用 harness | baseline/target 真正同任务、objective oracle 有效性、time/maintenance/failure delta 与 adoption registry | `partially_covered` |
| ORG-06 | review boundary、candidate-change invalidation、final-review candidate/hash 绑定；本轮 separate thread 只写 audit | 写入 `reviewer_candidate_write_paths=["src/"]` 会被拒绝 | 审查角色的声明边界、append-only 输出位置和候选变化失效规则 | 安全只读、审查者身份、阻止实际写候选；只能通过事后 diff/hash 检测 | `partially_covered` |
| IMP-04 | stdlib-first policy、dependency manifest 字段、external action full-SHA 检查 | mutation 只把 `floating_versions_allowed` 改为 `true`；没有注入真实依赖或 action | no-floating 与 manifest 要求文字、workflow action revision 形状 | 实际 import/install graph、package hash、license、install script、间接依赖、更新后重验；workflow 仍安装 `ruff==0.15.17` 而无本 policy 的 manifest receipt | `partially_covered` |
| VER-07 | candidate commit/tree、`governance_tests/` 实现目标和 CI discovery 提供局部 test integrity | 对应 case 没有删除测试，只关闭 baseline flag | baseline-before-mutation 规则和当前 method tests 的存在 | test 删除、skip、xfail、assertion 放宽、oracle 替换；incident regression 当前实际失败 | `partially_covered` |
| SEC-06 | telemetry unknown=`blocked`、external action full-SHA 检查、stdlib-first 边界 | `blocked`→`warn` 能命中目标分支，但没有执行依赖行为探针 | 未知 telemetry 的政策终态和 action revision 要求 | package/间接依赖遥测、恶意 install、SBOM/license/source 完整性、标准库与系统风险 | `partially_covered` |
| OPS-08 | 有结构化 incident record，并检查 regression path 存在 | 指向不存在的 path 会被拒绝；真实 regression 不被运行 | incident 字段齐全且 path 存在 | root cause 正确、preventive control 已实现、regression 能通过 baseline 并击中原故障；本轮实际失败 | `gap` |
| HUM-05 | nontechnical explanation 字段、状态区分、fixture 限制和未来 EX-HUMAN 阶段 | 删除 `what_remains_unknown` 会命中 exact-set oracle | 报告 schema 必须包含未知、阻塞、后果相关槽位 | 真实非专业用户是否理解、能否比较风险、是否在真实决定中正确使用 | `partially_covered` |
| ECO-01 | finite retry-budget 字段、budget exhaustion=`bounded_incomplete`、禁止改写成功 | 关闭 `budget_exhaustion_cannot_be_relabelled_success` 会命中目标分支 | 预算耗尽不能在 policy 中标为成功 | 每个真实 packet 有预算、token/time 被计量、no-progress 真正停止、边际收益检查 | `partially_covered` |
| ECO-02 | current allowed/forbidden scope、human decision requirement、章程与 contract 冻结边界 | 删除 `live broker execution` 会命中 exact-set oracle | 当前单人/local/paper/no-live 边界文字被锁定 | 通过新字段、任务拆分、实现入口或后续 V2 的语义 scope creep；真实 packet scope enforcement | `partially_covered` |
| ECO-03 | 只有 new-component 与 migration required-field 清单 | 删除 `removal_path` 会命中 exact-set oracle | 新组件模板必须保留 removal-path 槽位 | 真实长期维护债务、接口质量、重复代码、migration 可行性、重构预算和维护趋势 | `gap` |
| ECO-04 | rename-only 禁止规则、terminology rule、harness exit-plan 字段 | `rename_only_rewrite_allowed=false`→`true` 会命中目标分支 | 不能仅凭术语名称授权重写的意图被锁定 | 伪装成“功能变化”的实际重写、architecture delta 真实性、迁移/退出计划执行与可逆性 | `partially_covered` |

## 实际运行结果

所有命令均设置 `PYTHONDONTWRITEBYTECODE=1`；测试只在系统临时目录创建 fixture，没有修改候选输入。

### 项目方法 baseline verifier

命令：

```text
python3 scripts/verify_project_method.py --json
```

结果：

```text
exit 0
{"error_count": 0, "errors": [], "status": "pass"}
```

### 项目方法定向 mutation suite

命令：

```text
python3 -m unittest governance_tests.test_project_method -v
```

结果：

```text
Ran 18 tests in 1.650s
OK
```

该结果证明 benign fixture 通过，且每个测试制造的 policy 字段变化会出现预期错误 substring。它不推翻上述语义缺口。

### 候选治理 verifier

命令：

```text
python3 scripts/verify_governance.py --allow-candidate
```

结果：

```text
exit 0
governance verification: PASS (candidate)
```

### policy 指定的 incident regression

命令：

```text
python3 -m unittest governance_tests.test_attack_runner -v
```

结果：

```text
Ran 4 tests in 5.356s
FAILED (failures=3, errors=1)
```

在最终候选上再次运行其 baseline/target exit 隔离 case，仍为：

```text
Ran 1 test in 3.081s
FAILED (failures=1)
```

没有继续运行全量 governance discovery：被 policy 明确命名的 regression 已在未变异 baseline 上失败，足以否决 freeze；继续汇总更多绿灯不能修复这个 oracle。

## 设计冻结的正确主张边界

当前证据允许以下有限主张：

- 指定 policy、case、spec、trace、target 和 failure registry 在结构上互相引用。
- 当前 `verify_project_method.py` 接受 baseline policy。
- 定向 unit mutations 会触发各自预期的静态错误分支。
- 候选治理 verifier 在真实嵌套仓库上下文中通过。
- frozen-file/hash/Git 设计能够在执行完整冻结流程后约束这些字节的变化。

当前证据不允许以下强主张：

- 17 个 failure 已被真实机制逐项关闭。
- 长上下文 retrieval、并行语义冲突检测、真实用户理解或长期技术债已经被验证。
- `V-PROJECT-METHOD` 已按自己的 result schema 生成 candidate-bound、逐 case、逐 oracle 的设计冻结证据。
- incident regression 已有效防止 R5 non-isolated-oracle 复发。
- reviewer 具有安全隔离或技术强制只读。
- `FAILURE_CLASSES_V1.json` 的全 `covered`、零 gap 摘要是独立推导结果。

## 必须满足后才可重审 freeze

- failure status 必须由每项可执行证据推导，不能由 verifier 强制接受 registry 自报的 `covered`。
- `V-PROJECT-METHOD` 的 executor 必须真实运行其 acceptance cases，并生成符合 result schema 的 candidate/tree、输入/raw hash、selector、oracle observation、case result 与 finding binding。
- CTX-02 必须有真实长上下文、位置、compaction、restart 与 stale-request probe；不能只 mutation probe 名称。
- ORG-03 必须有 active packet/path ownership 与并发写实验，并加入无文本冲突的语义集成反例。
- HUM-05 保持 `partially_covered`，直到 EX-HUMAN 的真实非 fixture comprehension evidence；不得在 design freeze 写成完整 `covered`。
- ECO-03 必须建立 component inventory、可检查的边界/迁移/退出证据和纵向 maintenance review；静态 removal-path 字段只能算局部控制。
- 修复 `governance_tests/test_attack_runner.py` 的嵌套仓库 fixture，使未变异 baseline 先通过，再证明目标 mutation 被目标 oracle 独立拒绝。
- `CASE-METHOD-FROZEN-TEST-DELETED` 必须真正删除、skip、xfail 或放宽冻结测试，并观察 test-integrity 控制拒绝，而不是改 policy 自述。
- 形成新的精确 commit/tree 后重跑，并由新的 platform-observable separate-thread review 重新裁决；本报告不得复用为新候选通过证据。

## Residual risks

- 同源模型、相同工具和相似训练分布仍可能共享盲点。
- separate thread 可被平台观察，但不是安全隔离；workspace 权限和 OS 用户仍是共同信任边界。
- 自然语言单调性、用户理解、语义 merge 冲突和长期维护债务不能被有限静态测试完全判定。
- 并发自动 backup 会推进 HEAD；候选绑定必须以精确 commit/tree 和输入 hash 为准，不能以“当前分支名”代替。
- 即使上述 blocker 修复，有限 mutation 仍只能证明已测试反例，不证明未知 failure 不存在。
