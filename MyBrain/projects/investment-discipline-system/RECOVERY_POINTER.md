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

`0a7e3d56eda8524cf7fe1b7e22151f2871e6f469b81cfda7f996389216eb3498`

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

- archive-anchor 已完成精确完成收据、CAS、故障/邻近路径与固定字节独立
  审查；该 CAS 子节点已关闭，但不代表治理基础恢复父层完成。
- 直接入口的后续独立审查又发现 `child.start` 文件存在性可提前释放 child
  并覆盖并发文件，且扫描器漏掉 class、定义期表达式、`Path.replace` 和依赖
  writer。当前移动树已改为父进程独占 pipe capability，补齐三入口负向矩阵
  与四份生产源码闭包；源码/测试 SHA-256 分别为
  `3903e2944241d61e3037ba4e79f837d1be7e86b1117be59f0de8578a9a070bd6`
  与 `c468a99fc2642f1a9f0862026626072fdb0a790c1b1c4b5c3c94a705512884ef`。
  16 项针对测试通过，但一次复审仍被平台分类器中断；中性替代审查正在运行，
  因此节点仍 OPEN。
- clone/genesis 的私有 capability 候选已被拒绝；restore-only R1 与 R2 也被
  独立审查拒绝。R2 的核心错误包括互相哈希的收据环、错误 pending 切片、
  过度原子性主张、非精确 bundle 闭包和混入私有备份范围。
- R3 已被独立审查拒绝：`closure({C,G})` 实际包含整个知识库历史，E 的终端
  根与源码代际也未闭合。R4 改为从来源描述 C 生成全新、无父历史、仅含允许
  项目文件的投影 P，再走 `C -> P -> G -> A -> V -> E`，并用外部 X 绑定 E；
  C 与历史不进入 bundle。R4 SHA-256 为
  `36a24d6eaad40bde845a519f9c08caa06707c4c73709e447f0819110de24c68c`，
  正在接受独立架构挑战，尚未授权实现。
- 完整测试集、精确候选物化和新一轮独立只读审查尚未完成。

## 下一条 Graph 边

先裁决直接入口中性替代固定字节审查与 R4 独立架构挑战。任一真实缺口继续在
本层红测、根因修复和复审；只有 R4 获得 implementation-only 设计放行后，
才先建立并审查其要求的独立 successor packet/transition，再进入实现。两条原子单元稳定后，刷新
packet/transition/台账/生成视图并发布短窗口精确观察；随后运行完整保障测试、
物化不可变候选并进行候选绑定最终独立审查。任何开放 Critical 或 Major 都
在本层循环，不把总 Goal 改成 blocked，也不进入金融研究、模型适配、纸面
执行或实盘阶段。

## 仍然存在的耐久性风险

本文件保存的是恢复导航，不是未提交源码的完整副本。当前移动树若在形成
受控提交或独立备份前丢失，最新代码可能无法仅凭本文件逐字节恢复。因此，
“上下文压缩不会丢失方向”目前已有防线；“任意本地故障都不会丢失最新代码”
尚未证明，不能混为一谈。
