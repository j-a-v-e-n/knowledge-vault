# 最终候选审查历史

本文件保留总体设计候选在最终独立审查阶段出现的拒绝项。失败候选不得被后续修订静默覆盖，也不得被解释为曾经获得实现权限。

## `OTTS-DESIGN-20260727-C1`

- Candidate manifest SHA-256：`961e2434db55e5ffb9e6dc188ceda13a74c46d0e618e0e0087b11f2a7ede7f6f`
- 审查范围：phase-boundary bounded review；不是全量最终审查
- 裁决：`FAIL / MAJOR`
- 文件修改：审查者只读，未修改候选

### 拒绝原因

候选验证器把 `FINAL_CANDIDATE_MANIFEST.json` 的父目录作为完整 inventory root，并拒绝其中任何未列文件；同一候选又准备在该目录内新建 `shadow_mvp/`，并可能把 review receipt 与 closure decision 写入同一目录。因此，第一份正常的后闭合工件会使已审候选机械失效；若把新工件补入候选 manifest，又会改变 manifest hash，使 review/closure 绑定失效，形成逐文件重封与重审循环。

这个问题没有扩大任何现实权限，系统保持 fail closed，所以不是 Critical；但它阻止候选在保持 exact-hash 身份的同时进入自己定义的下一阶段，必须在开工前修复。

### C2 必须满足的修订

- 当前候选目录继续作为完整、零漏项的不可变设计 inventory root；
- governance 与 shadow implementation 使用两个与候选目录不重叠、名称精确冻结的 sibling roots；
- candidate freeze 时两个 sibling roots 必须不存在，禁止提前藏入文件；
- post-closure root 必须各自使用独立 canonical manifest，完整绑定内部文件、依赖、外部父候选 hash，并拒绝漏项、symlink、hardlink、special file、路径逃逸和依赖环；
- freeze report 先证明两个 sibling roots 在候选终审时均不存在；review receipt 绑定 exact candidate、freeze report、verifier 与 Envelope，closure decision 再绑定 exact candidate、freeze report、exact review receipt、exact shadow root 与 Envelope；
- aggregate Gate 还必须收到与 closure decision 字节一致的外部 expected hash；只读取 root 内自称获准的文件不能授权实现；
- shadow root 的 manifest 再绑定 exact candidate、governance manifest、review receipt、closure decision 与 Envelope；
- frozen candidate 任一字节变化使 RC-26 失效；后闭合工件变化只使依赖它们的 downstream closure/runtime 状态失效，不反向改写历史设计快照。

在修订候选重新冻结并完成一轮新的全量 manifest-bound independent review 前，权威状态继续为 `BLOCKED`。

## `OTTS-DESIGN-20260727-C2` withdrawn pre-final candidate

- Candidate manifest SHA-256：`b66fe735158177a18940667ff7bbd1075df532de948067498cd3748e36715f61`
- Freeze report SHA-256：`614898a499e5348ca765c902848c364e0c421dbc9b3d8db91c8d42e7a82d560c`
- Reviewer ID：`fresh-c2-final-reviewer-20260727-a`
- 裁决：`FAIL / WITHDRAWN`
- 全量研究语义审查：未完成，不能把本轮局部发现解释为 RC-01—RC-24 的 PASS

### 拒绝项

- candidate verifier 对普通文件做 hash/inventory equality，但会跳过 FIFO/socket 等 special node，且未拒绝 hardlink；这与 post-closure root 的闭集策略不一致；
- shadow manifest 的 `status/scope` 只要求非空，因此文件可以写入与 Envelope 冲突的 production/外部权限措辞，即使 aggregate 输出另有 `external_action_authority=false`；
- reviewer 按普通 Python 入口运行 phase tests 后，本地 import 生成两个未列入候选的 `.pyc`；测试断言通过，但紧随其后的 freeze verifier 正确拒绝已被测试自污染的 inventory。

### 后续修订

- candidate inventory 与 post-closure inventory 统一拒绝 symlink、hardlink、special node 和未列目录，并加入 synthetic 负向测试；
- shadow 顶层状态/范围冻结为 `SHADOW_IMPLEMENTATION_CANDIDATE / LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY`，且必须显式 `external_action_authority=false`；
- phase test 在任何 local import 前设置 `sys.dont_write_bytecode=True`，并保留 `-B` 作为调用层第二道防线；reviewer 生成的两个可再生 `.pyc` 与空 cache 目录已移除；
- 旧 exact hash 已撤回，必须重新计算全部依赖、重新生成 freeze report，并由另一轮 fresh reviewer 完成从机械边界到研究语义的全量终审。
