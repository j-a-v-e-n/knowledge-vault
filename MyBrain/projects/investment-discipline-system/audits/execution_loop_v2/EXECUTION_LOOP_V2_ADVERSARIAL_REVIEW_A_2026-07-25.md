# Execution Loop V2 独立只读挑战 A｜2026-07-25

状态：`blocked`

审查边界：本轮是并发开发期间的只读设计挑战，不是 commit/tree-bound 最终裁决。评审没有修改项目文件；评审观察到候选文件在审查期间继续出现，因此所有发现必须由后续固定候选重新验证。

## 审查对象

- `governance/WORK_PACKET_POLICY_V2.json`
- `scripts/verify_work_packets.py`
- `governance/EXECUTION_LOOP_POLICY_V1.json`
- `scripts/verify_execution_loop.py`
- `audits/PROJECT_GOVERNANCE_ADVERSARIAL_REVIEW_R10_2026-07-25.md`
- `governance/PROJECT_STATE_VIEW_POLICY_V1.json`
- `scripts/derive_project_state.py`
- `governance_tests/test_project_state_freshness.py`
- 审查期间出现的 `governance/EXECUTION_LOOP_POLICY_V2.json` 候选
- 当前 V2 packets、legacy receipt、V1 ledger 与治理调用入口

## Critical

### A-CRIT-01｜V2 ledger 尚未进入现行 authority

审查时不存在 `*.attempts.v2.json`，但 V2 work-packet verifier 与 state-view check 仍可通过。V1 verifier 仍绑定单个 V1 packet，不能证明当前 V2 packet 新鲜。

要求：

- 所有现行 V2 packet 必须有唯一、确定命名的 current observation ledger，或有精确冻结的一次性迁移豁免。
- 删除、错名、重复或多余 ledger 必须失败。
- 现行治理入口必须调用 V2 execution verifier；V1 只保留为哈希绑定历史。

### A-CRIT-02｜项目状态投影信任 packet 自报状态

当前 state basis 只观察 `state`、`depends_on` 与 routing 等选定字段，不观察 packet contract、ledger tail、controlled snapshot 或 receipt verification。

攻击：

- 修改 `bounded_write_paths` 或受控文件内容；
- 删除或改写 ledger；
- 保持 `state/depends_on/routing` 不变。

在该攻击下，三个可见入口仍可能保持逐字节“fresh”。

要求：

- state projection 必须先执行 V2 work-packet 与 execution-freshness 验证。
- packet contract 与 ledger tail 变化必须进入 state basis，使旧生成块变 stale。
- raw `complete` 不得在无有效 receipt/freshness authority 时推进依赖。

### A-CRIT-03｜本地手写 exit code 不是 authenticated completion

现有 acceptance receipt 只检查手填 `actual_exit_code` 是否等于 expected；它不执行或认证命令。

要求：

- 本地 receipt 只能称为 self-reported candidate evidence。
- authenticated completion 必须来自 candidate-bound remote execution 与独立只读审查。
- execution freshness、design freeze 与 product completion 必须保持三个不同结论。

### A-CRIT-04｜ledger 排除规则可能形成递归或宽泛逃逸

foundation packet 同时声明自身与下游 ledger。如果只排除自身 ledger，下游 ledger 从 absent 变为 present 会使已完成 foundation stale；如果按宽泛文件名排除，普通 work product 可伪装成 ledger 逃逸 snapshot。

要求：

- 排除集合只能来自 packet discovery 推导出的精确 ledger 路径集合。
- attempts 命名空间中的其他 V2 文件与其他 ledger-like write claim 必须失败。

## Major

### A-MAJOR-01｜pending baseline 语义必须唯一

如果 pending 无 ledger，则 activation 前的修改可以被后验洗成“初始状态”；若要求 baseline，baseline 也只能证明观察时点的当前 bytes，不能证明工作未提前发生。

采用边界：

- pending 必须有 baseline observation；
- baseline 不消耗 retry，不可声称 progress；
-报告必须保留“无法证明修改发生时间或授权顺序”的限制。

### A-MAJOR-02｜legacy exemption 必须是精确 singleton

豁免必须固定 packet path、schema、state、packet contract、checkpoint/acceptance 路径与 digest，并继续执行当前 snapshot receipt 验证。候选不得自行增加第二个 exemption。

### A-MAJOR-03｜blocker label 可以被轮换

只比较作者提供的 root-cause fingerprint 不能识别同一语义 blocker 的拆分或改名。

要求：

- 保留相同 fingerprint 的连续阈值；
- 同时增加不依赖 blocker label 的全局连续无进展阈值；
- 任意 evidence 只有在属于受控 write scope 且当前 hash 有效时才能构成结构化 progress；
- 语义充分性仍由独立审查判断。

### A-MAJOR-04｜tree/symlink/TOCTOU 仅是合作式 point-in-time 检查

nested symlink 与 special entry 应失败；顶层与中间 symlink、hard-link alias、遍历期间替换、权限变化、跨 verifier 非原子观察仍不能完全消除。

边界：冻结裁决必须绑定同一个不可变 Git candidate，并在隔离副本或 fresh clone 中运行；本地文件检查不能升级为强隔离声明。

## 六项明确判断

| 问题 | 裁决 |
|---|---|
| ledger 自引用 | 排除精确发现的 ledger artifacts；禁止宽泛文件名逃逸。 |
| complete 后续变更 | 受控 bytes 改变必须失败；必须 reopen/supersede 并重新验收。 |
| tree/symlink/TOCTOU | 只能声称 point-in-time cooperative observation。 |
| 同一 blocker 拆分 | fingerprint 不能识别语义拆分；需全局 no-progress 限制与独立分类。 |
| 手工伪造 actual exit | 不得导出 authenticated complete。 |
| pending 已有未记录修改 | baseline 只能证明观察到的当前 bytes，不能恢复之前历史。 |

## 最小不可删测试矩阵

1. active/blocked/candidate/complete 缺 ledger、错名、重复 ledger。
2. pending baseline 唯一语义。
3. packet contract、packet state、ledger reported state 任一不一致。
4. foundation 与下游 ledger 递归；普通 work product 伪装 ledger。
5. 最新 attempt 后 file/tree 的 bytes、存在状态或成员改变。
6. complete 后不 reopen 而追加 observation。
7. legacy packet、state、receipt、snapshot 或 exemption 列表变化。
8. attempt 删除、重排、重复、断链、previous hash、序号与 retry index。
9. failure/evidence delta 不等于集合差；无关文件伪装 progress。
10. blocker 轮换 ID 或拆 failure 后连续无实质进展。
11. budget 边界、baseline 不计 retry、unknown/mixed token telemetry。
12. 实际命令失败但 receipt 手填 expected exit。
13. 顶层、路径组件、nested、broken symlink、special file 与遍历替换。
14. raw packet complete 但 ledger/receipt 无效后运行 state projection。
15. packet contract 或 ledger tail 改变、而 `state/depends_on/routing` 不变。

## 本轮可保留结论

- legacy checkpoint/acceptance canonical hash 与候选固定值一致。
- V1 policy、verifier、ledger 的 raw hash 与历史清单一致。
- tree hash 采用稳定排序，且现有实现能拒绝观察到的 nested symlink 与 special entry。
- unknown token 计数为空且 aggregate 为 partial 的规则清楚。
- state-view 的逐字节渲染比较本身有效；缺口位于 authority 输入，而非渲染算法。

## 处置

保持 blocked。实现并验证上述 authority 接线、精确 ledger namespace、pending baseline、全局 no-progress、受控 evidence 与 state-projection 联动后，以固定候选发起 Review B。
