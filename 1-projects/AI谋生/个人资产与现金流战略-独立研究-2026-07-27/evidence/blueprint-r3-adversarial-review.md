## Review result: Portfolio Blueprint R3 adversarial leg

**Reviewer task identity:** `/root/blueprint_r3_adversarial`  
**Verdict:** **FAIL**

原因：存在 Major findings。按 `pass_rule`，本 leg 必须 FAIL。

### Reviewed

仅使用：

- `evidence/blueprint-r3-review-request.json`
- request 绑定的 blueprint、portfolio state、root instructions
- request 绑定的三份 observation records
- request 绑定的 model-conformance artifacts

未使用 memory、旧聊天、R1/R2 reviewer 输出、未绑定项目摘要或网络。

### 🔴 Critical

无。

### 🟡 Major

- **Recovery oracle 漏掉 request 明确要求的决策关键字段。**

  `evidence/blueprint-r3-review-request.json:113` 要求恢复 conditional tie-break，`:121` 要求 review receipt successor rule。权威值分别存在于：

  - `17-总体蓝图活动状态.json:38-51`
  - `17-总体蓝图活动状态.json:231-240`

  但以下文件均未包含 `objective_conflict_policy`、`feasible_branch_tiebreak` 或 `state_transition_rule`：

  - `model-conformance/task-project-recovery-read-only/output.schema.json:27-45`
  - `model-conformance/task-project-recovery-read-only/validate_recovery_output.py:72-139`
  - `model-conformance/task-project-recovery-read-only/gold-projection.json`
  - `model-conformance/task-project-recovery-read-only/fixtures/valid-output.json`

  `output.schema.json:27` 禁止额外 projection 字段，validator 又在 `validate_recovery_output.py:288-293` 要求与缺字段的 gold 完全相等。因此，一个遗漏或误解条件式优先级及 fail-closed successor rule 的输出仍可获得 `EVAL_QUALIFIED_CANDIDATE_OUTPUT`。

  **复现：**

  ```text
  rg -n 'objective_conflict_policy|feasible_branch_tiebreak|state_transition_rule|successor_rule' \
    output.schema.json gold-projection.json validate_recovery_output.py fixtures/valid-output.json
  exit 1; no matches
  ```

  **修复建议：** 将这两组语义加入 schema、机械 projection、gold 和 normal fixture；分别加入错误 tie-break 与错误 successor rule 必须被拒绝的测试。

- **stale fixture 是错误路径导致的假阳性，没有测试其声明的 hash-drift 场景。**

  `fixtures/stale-task-class.json:9-64` 复制了位于父目录的 manifest 相对路径；validator 在 `validate_recovery_output.py:173,188` 却始终以 manifest 自身目录为基准。由于 stale manifest 位于 `fixtures/`，所有路径整体偏移一级。

  `test_validate_recovery_output.py:42-49` 只断言分类为 `STALE_INPUT_BUNDLE` 且 mismatch 非空，未断言只有目标 blueprint hash 漂移，也未拒绝 `actual=MISSING`。

  **复现：**

  ```text
  python3 -B validate_recovery_output.py \
    --manifest fixtures/stale-task-class.json \
    --output fixtures/valid-output.json
  exit 3 / STALE_INPUT_BUNDLE
  ```

  输出不是目标文件的实际 hash mismatch，而是多项 `MISSING`，例如：

  ```text
  /知识库/1-projects/AGENTS.md
  .../model-conformance/16-总体蓝图闭合合同与状态审计.md
  .../fixtures/validate_recovery_output.py
  .../fixtures/gold-projection.json
  ```

  因此 suite 虽“绿”，却没有证明候选内容漂移检测正确。

  **修复建议：** 让 stale manifest 在与正式 manifest 相同的解析基准运行，或修正所有相对路径；测试应断言精确 mismatch target、实际 hash 非 `MISSING`，并且只有预期漂移项失败。

- **portfolio state 的 `as_of` 早于它绑定并投影的 C8 补充观察。**

  - `17-总体蓝图活动状态.json:4`：`2026-07-28T02:24:38-07:00`
  - `evidence/opportunity-c8-read-only-observation-2026-07-28.json:3`：`2026-07-28T02:28:57-07:00`
  - state 在 `:84-85` 已绑定该 observation，并在 `:104` 投影其 route finding。

  **复现：**

  ```text
  jq -r '.as_of // .recorded_at' \
    ../17-总体蓝图活动状态.json \
    opportunity-c8-read-only-observation-2026-07-28.json
  ```

  输出：

  ```text
  2026-07-28T02:24:38-07:00
  2026-07-28T02:28:57-07:00
  ```

  机器状态因此包含其 `as_of` 之后的证据，破坏 snapshot/freshness 的时间语义；当前 conformance projection 又不恢复或检查这些时间字段。

  **修复建议：** 将 state `as_of` 更新到不早于所有绑定 observation，并为 supplemental C8 observation 保存独立 observed timestamp；增加机械时间顺序检查。

### 🟢 Minor

无。

### ✅ 检查通过

- Primary action 正确标为 `READ_ONLY`，`write_set=[]`，`primary_write_action=null`。
- Candidate-bound live workflow pointers 为空；workflow 输入为 immutable observation records。
- 后续 workflow 漂移只阻塞 activation，不改写历史 review；跨任务写入要求 fresh refresh 与 bilateral coordination。
- 三类 blocker 已分离，review admission 为空，没有把本轮 review 放进 admission cycle。
- PB050 的 parent、相邻分支和具体 backtrack `PB010` 可恢复。
- C8 两条路线仍为 workflow future decision；窄分支只被 observation favor，没有获得授权；C8 write、Shadow 和 external action 仍禁止。
- Review receipt 路径、verbatim mutation rule 和 fail-closed successor transition 已写入 state；但其 successor rule 尚未进入 recovery oracle，见 Major finding。
- 模型状态保持 `NOT_TESTED`，task class 为 `EXECUTABLE_EVAL_NOT_YET_MODEL_RUN`；fixture 和本次 review 都没有自签 provider/model qualification。
- Owner constraint action 只有在两份 PASS receipt 后才可进入，且不会自动激活 workflow。
- 外部联系、申请/发消息、发布、账户/私有数据、支付/收款、合同/交付承诺、真实或影子投资、workflow candidate 写入均保持禁止。
- 未发现旧 restart checkpoint 重新取得 current action authority。
- 没有发现额外权限扩张；治理组件均有声明的失败映射，但 flawed stale test 使当前复杂度尚未取得所声称的验证价值。

### Recomputed hashes

Request 中声明的全部绑定 hash 均匹配；测试前后复算结果相同。

```text
7742a08e0f216abf5c749197b74a2bd3021c2260d666f8a0a9354f85b1ef42bd  16-总体蓝图闭合合同与状态审计.md
2e2c779b2599a377565cb97f2744831a36d9744303fc3eb9cfb7271d9efcf708  17-总体蓝图活动状态.json
ad43df133a5c463b6de84d4504dcb35e704525661074428b0855181f62f67be9  AGENTS.md
ce1f427b0e256f2a8d33cbe440d629a9b927da55346046b5fe87c294f822826c  opportunity-control-plane-observation-2026-07-28.json
9e50b0db1fa7fff5246df2573c745b41a191919d5d397c84aeb78f4e1ab6d768  opportunity-c8-read-only-observation-2026-07-28.json
3b258e01a2dcdffac090d5485c089c9f32fa7caf9cb03b84526f9b0091745386  investment-workflow-observation-2026-07-28.json
6e1702d52e083f217105312030bfafb138b9ada68585743d116279f57f1f404a  task-class.json
0e0d8e3b2ebf21e63fff7cd21d3fb7700e574345ea7d4030642eed7de7b23caf  validate_recovery_output.py
86119d9bdf87bf3d945fb1048450f334cfcc0b5290e88f74daa2921e760c0d55  output.schema.json
c22afa61ea187c616acd362c43d7b74a6fbf7762d66402b4a309f81185f3016e  SEMANTIC_RUBRIC.md
aa18ac23913b07d50a90a382490fb67086ff97df92464f283965902c57d0422d  gold-projection.json
4821b1c0fcd858092f38087f8bc1919da688015d8ca7bd293b17882daf040ba0  fixtures/valid-output.json
d5f0641cd2778720e5c04ead46dc6f72918df26b74d6a68aa48525a86bf0ed41  fixtures/refusal-output.json
c7639cfa91b133b2417728368e05e5c213758bc9e2356eb9f340fb8992535885  fixtures/wrong-output.json
bbcf175f6abf569e1cfe7f31deb36426ae8927d7ec69d56725519097c6cf420b  fixtures/stale-task-class.json
c7ef70c02ed581c93b041bc037305d9d706c0d4d5680ff966fc0f4a19dc4ad53  test_validate_recovery_output.py
```

入口 request 本次观察 hash，供 receipt 定位；它不是 request 内自声明的 binding：

```text
41192daea965f4e2c3f94af603879eaa2a1f9719a6b695de8b9695f9c7375d2e  blueprint-r3-review-request.json
```

### Verification commands and results

```text
python3 -B -m unittest -v test_validate_recovery_output.py
exit 0
Ran 7 tests in 0.044s
OK
```

```text
valid-output.json    -> exit 0 / EVAL_QUALIFIED_CANDIDATE_OUTPUT
refusal-output.json  -> exit 2 / NOT_QUALIFIED_REFUSAL
wrong-output.json    -> exit 4 / WRONG_STATE_PROJECTION
stale-task-class     -> exit 3 / STALE_INPUT_BUNDLE
```

stale 的 exit/classification 符合表面期望，但其 mismatch 内容证明是路径错误假阳性，不能算该语义通过。

其他只读命令包括 `pwd`、`find ... AGENTS.md`、`sed`、`nl`、`wc`、`shasum -a 256`、`jq`、`rg` 和 transient artifact 检查。

### Modification / external-action confirmation

- 项目文件修改：**无**。绑定文件测试前后 hash 完全一致。
- Required unittest 仅在系统临时目录创建并自动清理测试 JSON；项目中无 `__pycache__` 或 `.pyc` 残留。
- 网络、账户、联系人、发布、支付、合同或投资动作：**无**。
