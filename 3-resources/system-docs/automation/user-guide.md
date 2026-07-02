# 任务看板系统

> 一个让 Javen 和 Claude 共同维护任务、Claude 在 Javen 离开时也能继续推进的系统。
> 灵感来自思瑶的视频字幕（[[2026-04-27_AI任务面板自动化系统]]）+ 开源参考（ClaudeNightsWatch / alessiocol/claude-kanban / Ralph Wiggum loop）。

## 文件结构

```
MyBrain/system/
├── task-board.md        ← 主看板（你和 Claude 共同读写）
├── CLAUDE.md            ← Claude 的操作指令（被主 CLAUDE.md import）
├── README.md            ← 本文件（用户文档）
├── logs/                ← 自动审计日志（每天一个 .jsonl）
└── archive/             ← 月度归档（满 14 天的已完成任务）

.claude/                 ← Claude Code 配置
├── settings.json        ← 项目级设置（hooks 注册）
├── hooks/
│   └── audit.sh         ← 看板/会话事件审计日志
└── skills/
    ├── task-check/SKILL.md   ← /task-check 扫看板报状态
    └── task-add/SKILL.md     ← /task-add 添加新任务
```

## 三种使用方式（任选一种）

### 1. 显式 Slash Command

```
/task-check                          ← 看现在状态
/task-add 做一个个人 portfolio 网站   ← 加新任务
```

### 2. 自然语言对 Claude 说

```
看板情况怎么样？               ← 等同于 /task-check
加个任务，做 X                ← 等同于 /task-add X
推进 task-005                ← 让 Claude 接管 task-005
看板上能做的都做了           ← 让 Claude 推所有 owner=@claude 无阻塞任务
task-005 用 X 方案           ← 解阻塞，重新推进
```

### 3. 直接编辑 task-board.md

你打开 Obsidian 直接改也行——Claude 下次读看板时会看到你的改动并相应处理。

> 提醒：你的 vault 在 Google Drive 同步盘上，多设备同步可能滞后，**避免两台机器同时改看板**。

## 任务卡格式

```markdown
- [ ] **task-005** | 整理 PHIL28 课程材料 | #P1 | owner: @claude
  - **目标**：为期末考试准备结构化笔记
  - **Definition of Done**：8 个 PDF 全部建 source 页 + 1 个 overview 页
  - **创建**：2026-04-27
  - **更新**：2026-04-27
  - **子任务**：
    - [ ] a. 扫描 raw/PHIL28，列文件清单
    - [ ] b. 编译 syllabus → COGS 风格 overview
    - [x] c. 按周编译 7 个讲座 PDF
    - [ ] d. 中期问题做成 cheat sheet ⚠️ blocked on @javen — 用图表式还是问答式？
```

四列含义：

- **📥 待启动**：还没开始做
- **🚧 进行中**：Claude 或 Javen 正在推进
- **🔒 阻塞**：卡在等决策/等外部输入
- **✅ 已完成**：搞定了；满 14 天后自动归档

## 阻塞机制（"blocked on" 设计）

这是整个系统的灵魂——AI 遇到不能自己决定的事**不瞎猜也不卡死**：

1. 子任务旁标 `⚠️ blocked on @javen — 具体原因`
2. 整个任务从"🚧 进行中"移到"🔒 阻塞"列
3. Claude 转去做别的可推进任务
4. Javen 看到阻塞列，逐个解锁；解锁后任务回"🚧 进行中"

## 当前阶段：Stage 0（手动）

| 阶段 | 状态 | 说明 |
|---|---|---|
| **Stage 0** | ✅ 完成 | 看板 + 2 个 skill + audit hook，全靠手动喊命令 |
| **Stage 1** | ⏸ 待启动 | UserPromptSubmit hook 自动 task-check / SessionStart 注入看板上下文 / Stop hook 决定再跑一轮 |
| **Stage 2** | ⏸ 待启动 | launchd 后台守护，真正"睡觉时也能干活"（用定时而非 fswatch，绕开 Google Drive 同步盘问题） |

阶段升级请告诉 Claude，**不要直接动 settings.json/launchd**——Claude 会按规则做并写日志。

## 日志查看

```bash
# 看今天发生了什么
cat MyBrain/automation/logs/2026-04-27.jsonl | jq

# 看某个任务相关的所有改动
cat MyBrain/automation/logs/*.jsonl | jq 'select(.file | contains("task-board"))'

# 看某个 session 的全部
cat MyBrain/automation/logs/*.jsonl | jq 'select(.session=="<session-id>")'
```

## 设计原则（取自思瑶视频 + 开源经验）

1. **简单的 Markdown 看板**——人类点开是看板，AI 看到的是结构化文本
2. **Claude 自主 + 人类授权**——可推进的自己做，不能决定的写 blocked
3. **每件事可回溯**——audit 日志 + Claude transcript 双备份
4. **不强制看板维护成本**——你不喊 `/task-check` Claude 也不强迫你维护，但 Claude 自己干完事会主动归档

## 相关文件

- 思瑶视频字幕（设计起点）：[[2026-04-27_AI任务面板自动化系统]]
- Claude 操作规则细节：`CLAUDE.md`
- 任务卡格式与字段定义：`task-board.md` 底部
