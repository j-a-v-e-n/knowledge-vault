# 当前恢复指针｜投研纪律系统

> 本文件是 Google Drive / Obsidian 中的耐久导航镜像，不是候选产物、
> 验收结论、恢复成功证明、设计冻结或完成声明。最后已集成状态仍由项目
> 的机器可读权威记录生成；尚未集成移动树必须在其自身原始证据上核对。

## 为什么存在

聊天上下文、压缩摘要和模型记忆只能帮助导航，不能承担长期项目状态。
本文件让一次新的上下文先找到真实工作树与唯一检查点，再决定继续什么；
不能因为上下文压缩而重新猜测、重复已完成工作或把旧状态当成当前状态。

## 最新已知移动树

- 工作树：`/private/tmp/ids-recovery-r4-review.BYwzIK/repo`
- 项目：`/private/tmp/ids-recovery-r4-review.BYwzIK/repo/MyBrain/projects/investment-discipline-system`
- 分支：`codex/thin-foundation-recovery-r5-work`
- HEAD：`b19ab03c6e6e30e54d6da5571733f981dfe7896a`
- Goal：`active`
- 当前门：`NO-GO`
- 精确候选：不存在；当前是有未提交改动的移动树。
- 当前层：治理基础恢复层。

唯一详细检查点：

`/private/tmp/ids-recovery-r4-review.BYwzIK/repo/MyBrain/projects/investment-discipline-system/.work_packets/archive/FOUNDATION-SUCCESSOR-RECOVERY-2026-07-27/reviews/pre-review-r5-unfixed/RESUME_CHECKPOINT-2026-07-28.md`

该检查点在本次镜像时的 SHA-256：

`da608ea978c42dfb4a42b2e2e48284f1517d089bae92cad9336790535f4caa0f`

## 恢复步骤

1. 先读 `PROJECT_CHARTER.md`、`DECISIONS.md` 和本文件。
2. 检查上述工作树、分支、HEAD、Git 拓扑、脏文件与详细检查点是否存在。
3. 若详细检查点哈希相同，按其中的开放发现和下一条 Graph 边继续。
4. 若详细检查点存在但哈希不同，把它当作更新的移动树重新核对，不能用本
   镜像覆盖它。
5. 若详细检查点或工作树不存在，本镜像只能证明最后已知状态，不能恢复
   未提交代码字节，也不能宣称恢复成功；先寻找可验证的工作树、补丁、提交
   或备份，再决定是否重建。
6. `STATUS.md`、`TASK_BOARD.md` 和 `LOOP_RUN_LOG.md` 是最后已集成权威基础
   的生成视图，不是该未集成移动树的完整描述。

## 当前开放发现

- Critical：现有 clone/genesis 身份确认不能区分真正的新项目与普通分支克隆。
- Critical：直接内部变更入口的主工作树前置闸门已实现并通过聚焦回归，但
  尚未由固定候选上的独立审查关闭。
- Major：archive-anchor CAS 的幂等与推进分支都必须先重新绑定并验证精确的
  已归档完成收据、操作/事务语义和所有实时目标。
- 完整测试集、精确候选物化和新一轮独立只读审查尚未完成。

## 下一条 Graph 边

先完成 CAS 完成事务语义与 genesis 身份机制的修复及负向/邻近正向验证；
然后运行完整保障测试，刷新哈希、台账和生成视图；之后才可物化固定候选并
交给独立审查。任何开放 Critical 或 Major 都在本层循环，不把总 Goal 改成
blocked，也不进入金融研究、模型适配、纸面执行或实盘阶段。

## 仍然存在的耐久性风险

本文件保存的是恢复导航，不是未提交源码的完整副本。当前移动树若在形成
受控提交或独立备份前丢失，最新代码可能无法仅凭本文件逐字节恢复。因此，
“上下文压缩不会丢失方向”目前已有防线；“任意本地故障都不会丢失最新代码”
尚未证明，不能混为一谈。
