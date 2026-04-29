# 任务看板系统 — Claude 操作指令

本文件被 `MyBrain/CLAUDE.md` import，定义 Claude 如何操作 `MyBrain/automation/queue/task-board.md`。

## 核心原则

1. **看板是 Javen 和我的共用工作区**——他写方向，我执行；遇到决策点写 `⚠️ blocked on @javen`，不擅自决定
2. **看板里只放任务条目**——长内容（设计文档、研究记录、笔记）写到 `wiki/` 或 `notes/`，看板只放"任务卡"
3. **每次改看板必须更新**：任务卡的"更新"日期 + 文件顶部的"最后更新"和"当前状态"统计
4. **看板状态变更要小而精**——只 Edit 受影响的列/任务，不重写整文件

## 任务路由规则（接到新任务时）

### owner 判定

| 任务性质 | owner |
|---|---|
| 写代码、改文件、查资料、整理笔记、生成图表、ingest 编译 | @claude |
| 决定方向、选方案、批准提交、与外部人沟通、付钱买东西 | @javen |
| 部分需 Javen 拍板 + 部分纯执行 | 拆子任务，分别标 owner |

### 优先级判定

| 优先级 | 判定 |
|---|---|
| **P0** | 有明确 deadline 且 ≤7 天；或阻塞了其他任务 |
| **P1** | 重要但无紧迫 deadline；或 deadline 在 7–30 天（**默认**） |
| **P2** | 长期目标、灵感、备选方案；可放后台 |

不确定时默认 P1，让 Javen 后续调整。

### 是否拆子任务

- **拆**：≥3 个独立可验证步骤；或跨多个文件/领域
- **不拆**：单文件改动、单一查询、< 30 分钟可完成

## 阻塞处理

任何任务遇到以下情况，**立即移到"🔒 阻塞"列并标明原因**：

- 需要 Javen 决定方向（"用 A 方案还是 B"）
- 需要外部输入（"等老师回邮件"）
- 依赖另一个未完成的任务

阻塞标记格式：

```
⚠️ blocked on @javen — 需要决定 X 还是 Y
⚠️ blocked on task-005 — 等 task-005 子任务 c 完成
⚠️ blocked on 外部 — 等老师回复 4/30 的邮件
```

**blocked 的任务我不再尝试推进**，转去做别的可推进项。Javen 解阻塞后，我把状态从"🔒 阻塞"移回"🚧 进行中"，并把阻塞标记改为"已解决（YYYY-MM-DD）"或直接删除。

## 主动看板时机

我会在以下时刻**主动**读写看板（不需要 Javen 显式喊）：

1. Javen 问"看板情况"、"今天该干啥"、"还有什么任务" → 调用 `/task-check`
2. Javen 说"加一个任务"、"我刚接到一个活" → 调用 `/task-add`
3. Javen 告诉我某任务可以开始或已完成 → 直接 Edit 看板更新状态
4. **我自己在主对话里完成了一项可写入看板的工作 → 主动添加进"已完成"列**（不要问，直接写，告诉 Javen）
5. Javen 说"推进 task-NNN" → 接管该任务并开始干；遇阻塞按上面流程处理

## 看板维护准则

- **task ID 自增**：读看板找最大 NNN，新任务 = NNN+1，三位数补零
- **完成任务**：从"进行中"移到"✅ 已完成"，把外层 `[ ]` 改为 `[x]`，加 `done YYYY-MM-DD`
- **归档**：超过 14 天的"已完成"任务，移到 `MyBrain/automation/archive/YYYY-MM-task-board.md`（按月分文件）
- **不要重写整个看板**——只 Edit 受影响的列/任务
- **顶部统计每次都要更新**："1 进行中 / 0 阻塞 / 2 待启动 / 0 已完成"

## 与知识库（MyBrain）的协作

- 看板任务**可以引用知识库页面**：`[[wikilink]]`
- 看板任务**不取代知识库**——长内容写到 `wiki/` 或 `notes/`
- 编译任务（标准 ingest 流程）的成果在 `wiki/log.md` 有记录，但**ingest 任务本身可以是看板上的一项**
- ingest / lint / connect 等知识库操作触发后，主动在看板加一条对应任务（标 owner=@claude），完成后移到已完成

## 日志

`MyBrain/automation/logs/YYYY-MM-DD.jsonl` 由 `.claude/hooks/audit.sh` 自动写入，我不直接维护它。日志记录：

- SessionStart / SessionEnd / Stop 事件
- 看板文件被 Edit/Write 时的 tool_input

读日志（Javen 想看历史）：`cat MyBrain/automation/logs/2026-04-27.jsonl | jq`

## 当前阶段

**Stage 0**（手动喊 slash command）—— 当前状态

未来阶段：

- **Stage 1**：UserPromptSubmit hook 自动 task-check + 加 SessionStart 注入看板上下文 + Stop hook 决定是否再跑一轮
- **Stage 2**：launchd 真后台守护，`claude -p --resume` headless 跑（注意 vault 在 Google Drive 同步盘，FSEvents 不可全信，用 StartInterval 兜底）

阶段升级由 Javen 决定。我**不擅自启动 Stage 2**——它涉及 launchd plist 安装和 token 预算限制，必须 Javen 明确指示后再做。

## ⚠️ 安全红线

- 不在 task-board.md 添加 Javen 没说过的任务（除非是我自己干完的归档）
- 不删除"✅ 已完成"任务（除非显式归档到 archive/）
- 不修改 raw/ 和 archive/ 里的内容（vault 主规则也禁止）
- 不擅自启动 Stage 2 后台 daemon
- 不在主 `MyBrain/CLAUDE.md` 之外的位置定义新的"必须执行"指令——所有看板规则都在本文件里
