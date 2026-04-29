# 🤖 自动化中心

> Javen 的所有自动化在这里。**每天起床看这一页 + 加新任务，就够了。**

---

## 📅 今天的产出（每日 03:00 daemon 跑出来）

| 文件 | 内容 | 链接 |
|---|---|---|
| Daemon 总结报告 | 昨晚跑了啥 / 完成什么 / 阻塞什么 | [[runs/2026-04-29\|今日 daemon 报告]] |
| AI 早报 | 70% 启发好奇心 + 30% 落地切入点 | [[reports/ai-watch/2026-04-29\|今日 AI 早报]] |
| 邮箱 triage | 24h 内邮件 🔴/🟡/⚪ 分档 | [[reports/email-triage/2026-04-29\|今日邮件]] |

> ⚠️ 链接里的"2026-04-29"是手动维护的当前日期。**daemon 每天会自动覆盖这一节**写新的日期。
> 如果你看到日期跟今天不符 → daemon 没跑 / 跑失败。看 daemon 报告 root cause。

---

## 🚦 队列（你要处理的）

| | 文件 | 看啥 |
|---|---|---|
| 审批 | [[queue/approvals\|approvals.md]] | ⏳ 待审批列里勾 `[x]` 我执行；删行 = 拒绝 |
| 任务 | [[queue/task-board\|task-board.md]] | 📥 待启动 / 🚧 进行中 / 🔒 阻塞 / ✅ 已完成 |

---

## ⚡ 快速命令（跟我说一句话即可）

| 你想干啥 | 跟我说 | 我会做 |
|---|---|---|
| 看看看板状态 | `看板情况` 或 `/task-check` | 调 task-check skill 报告状态 |
| 加个任务 | `加一个任务 ...` 或 `/task-add` | 调 task-add skill 写到 待启动列 |
| 推进某任务 | `推进 task-013` | 接管 task-013 + 干能干的 |
| 把所有能做的都做 | `看板上能做的都做了` | 自主推 owner=@claude 没 blocked 的任务 |
| 临时跑 AI 早报 | `扫一下 AI 趋势` | 调 ai-watch skill |
| 临时扫邮箱 | `扫一下邮箱` | 调 email-triage skill |

---

## 🟢 自动化健康度

| 自动化 | 触发 | 频率 | 上次状态 |
|---|---|---|---|
| **Claudian daemon** | macOS launchd | 每天 03:00 | ❌ 4/29 stream timeout（已修复 fresh session，等 4/30 验证）|
| **Obsidian Git** auto commit | Obsidian plugin | 每 5 分钟 | ⏸️ 待 Javen 关一个 toggle 才生效 |
| **Audit hook** | Claude Code 内嵌 | 实时（SessionStart / Edit）| ✅ 一直在 |
| **审批队列扫描** | 主对话 + daemon | session 启动 + 03:00 | ✅ 一直在 |

---

## 📚 设置指南（要装 / 要改时看）

- [[docs/git-backup-setup\|git-backup-setup.md]] — git 备份初始化（已部分完成，等你 Obsidian 内关一个 toggle）
- [[docs/qclaw-setup\|qclaw-setup.md]] — QClaw 体验试玩（task-014）
- [[docs/claude-code-router-setup\|claude-code-router-setup.md]] — 路由 daemon 到 DeepSeek 降成本（task-013）

---

## 📐 系统规则文档（你不用看，AI 看）

- [[CLAUDE.md\|CLAUDE.md]] — 任务看板系统操作规则（被 main CLAUDE.md import）
- [[docs/user-guide\|user-guide.md]] — 用户文档（看板系统怎么用）
- [[docs/lessons\|lessons.md]] — 经验教训：debug 方法论 + checklist

---

## 📊 历史归档（往回翻）

- [[runs|按日期浏览所有 daemon 报告]]
- [[reports/ai-watch|按日期浏览所有 AI 早报]]
- [[reports/email-triage|按日期浏览所有邮件 triage]]
- [[archive|完成 14+ 天的看板任务归档]]

---

## 🛡 紧急停止（kill switch）

如果想立刻停掉 daemon：

```bash
touch '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/automation/KILL_SWITCH'
```

下次 03:00 daemon 启动会看到这个文件 → 立即退出，不跑任何任务。

恢复：删除该文件即可。

---

## 🗺️ 文件夹结构（参考）

```
MyBrain/automation/
├── README.md           ← 你现在看的这个 dashboard
├── CLAUDE.md           ← 看板操作规则（AI 看）
├── runs/               ← daemon 每日总结报告（每天一份）
├── reports/
│   ├── ai-watch/       ← 每日 AI 趋势早报
│   └── email-triage/   ← 每日邮箱 triage
├── queue/
│   ├── approvals.md    ← 审批队列
│   └── task-board.md   ← 任务看板
├── docs/               ← 设置指南 + 用户文档 + 经验教训
├── logs/               ← 原始 audit log（debug 用）
└── archive/            ← 14+ 天前的已完成任务归档（按月）
```

vault 里**所有跟自动化相关**的文件都在这棵树里。其他位置（`career/`、`wiki/`、`notes/` 等）是知识 / 个人内容，跟自动化系统无关。

---

## 🔗 跟主 vault 的边界

| automation/ 干啥 | wiki/ 和 notes/ 干啥 |
|---|---|
| 自动化任务的状态、产出、日志、规则 | 你的知识网络（concept 页 + source 页 + 跨域 synthesis） |
| 每天会动 | 慢慢长大，按 ingest pipeline 编译进来 |
| 主要是 AI 在写 | 主要是 ingest 流程在写 |
| Javen 主要看 dashboard / queue 这两个入口 | Javen 主要按主题（ECE284 / COGS117 等）查询 |

---

*Dashboard 生成于 2026-04-29 by 主对话 Claude，物理重构所有自动化文件到 `MyBrain/automation/`*
