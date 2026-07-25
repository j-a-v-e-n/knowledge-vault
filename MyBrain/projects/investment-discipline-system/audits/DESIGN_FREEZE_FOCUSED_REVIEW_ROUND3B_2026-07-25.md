# 设计冻结聚焦审查｜Round 3B

状态：`blocked-freeze`
候选 commit：`6dc1bb3a155a44106cdfb2774e32c198b6624b36`
候选 tree：`f75b0053435608db755731dd8ce1c505c53caf75`
审查主体：`SUBJECT-DESIGN-REVIEW-PASCAL-R3B`
工具 locator：`subagent:019f990e-4e75-77f1-b4f9-75287dad9cab`
参与候选构造：`false`
写候选文件：`false`

## 总裁决

`BLOCK FREEZE`

## Critical

### R3B-CRIT-001｜本地 Git gate 接受任意 upstream

`verify_git_state.py` 比较 `HEAD == @{upstream}`，但没有要求 upstream 属于 `origin`。分支若跟踪 `other/main`，即使 `origin/main` 缺少候选，仍可能通过。

关闭要求：固定可信 remote/branch；直接查询该 remote ref 并与 HEAD 比较。不得把“origin 有 URL”替代“origin 含该 commit”。

## Major

### R3B-MAJ-001｜C→B allowlist 忽略 Git mode/type

闭合检查比较内容和路径，却没有比较 tree mode/type。攻击者可在合法 status 变更中把冻结 JSON 改成 executable，路径和内容均不变。

关闭要求：比较 C/B 的 `git ls-tree` mode/type；冻结文件保持普通文件和原 mode；用 raw diff 验证。

### R3B-MAJ-002｜bundle provenance 可自报

bundle 的 remote/ref/creation rule 只要求非空；没有证明 bundle 工作文件等于 HEAD 中的文件，也没有直接证明 bundle commit 位于可信 origin。

关闭要求：bundle 必须 tracked、与 HEAD blob 相同；bundle-commit 阶段重新直接核对固定远端 ref，并保存观察时间与准确语义。

### R3B-MAJ-003｜远端观察与 bundle 创建存在 TOCTOU

baseline 的 `ls-remote` 通过后，远端仍可移动；当前字段名容易被误读为创建过程与远端原子绑定。

关闭要求：把它表述为带时间戳的观察，而非原子保证；bundle 提交后再直接验证最终 bundle commit 位于固定远端 ref。

## 已执行与限制

- 定向冻结测试通过。
- 未执行的额外反例包括非-origin upstream、未提交手工 bundle、真实 vault 子目录 prefix 和远端移动窗口；这些不能被视为通过。
- 本轮没有提出新的架构级失效类别，但证明已有 Git/证据 provenance 控制仍未闭合。
