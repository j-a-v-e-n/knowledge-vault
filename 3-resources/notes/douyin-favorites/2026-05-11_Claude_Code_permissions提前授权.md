---
title: "Claude Code permissions 提前授权 — 把 babysit AI 变成发任务"
type: source
tags: [douyin, AI, Claude_Code, 配置, settings, permissions]
sources:
  - projects/douyin-favorites-pipeline/Untitled 3.md
created: 2026-05-11
updated: 2026-05-11
priority: active
confidence: high
---

# Claude Code permissions 提前授权 — 把 babysit AI 变成发任务

> 视频核心：通过 `settings.local.json` 的 `permissions` 字段**提前一次性授权**常规操作，避免"走一步问一句"。这是配合 [[2026-05-11_Claude_Code_新功能8项|Auto-Permission Mode]] 的**精确控制**版本。

---

## 1. 发现了什么（一句话）

**Claude Code 默认很守规矩——每次改文件、执行命令、装依赖都问你 yes/no。这看起来安全，但实际让 agent 永远跑不了长任务**（你不在它就一直等）。解法：用 permissions 配置**一次性放行你信任的操作类型**，让 agent 真正自主跑完任务。

---

## 2. 为什么 default 行为是这样

Claude Code 的设计哲学是 **"Safe by default"**：
- 默认所有 mutation 操作（write file, run shell, install dep）都 ask
- 这是因为 LLM 仍然会 hallucinate——比如错以为要 `rm -rf /` 都可能发生
- ask 机制是用户作为 last guardrail

**但这导致一个副作用**：
- 长任务跑到一半总是 stuck
- 用户必须不断回到终端 click "yes"
- agent 从"自主执行者"退化成"半自动建议工具"

**解法的哲学**：
- 不是关掉所有权限检查（危险）
- 而是**精确告诉 Claude 哪些类是预批准的**（不用问），剩余仍 ask
- 这是 **"trust but verify" 的 declarative 实现**

---

## 3. 怎么配（实操）

### 3.1 文件位置

**项目级配置**：在你项目根目录建（或编辑）`.claude/settings.local.json`

vault 项目里这文件可能已经存在（Javen 自己用 `/config` 配过）。**`.local.json` 不被 git 追踪**——是个人 / 机器级配置，跟团队共享配置（`settings.json`）分开。

### 3.2 基础结构

```json
{
  "permissions": {
    "allow": [
      "Bash(npm install:*)",
      "Bash(npm run:*)",
      "Read(**)",
      "Edit(src/**)",
      "Write(test/**)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(sudo:*)",
      "Write(/etc/**)"
    ]
  }
}
```

**关键字段**：
- `allow`：列出**预批准**的操作（pattern matching）
- `deny`：列出**永远禁止**的操作（即使是 allow pattern 命中也不行）

**Pattern syntax**：
- `Bash(npm install:*)` — 任何 `npm install <something>`
- `Read(**)` — 读任何文件
- `Edit(src/**)` — 改 `src/` 下任何文件
- `Bash(rm -rf:*)` — 任何 `rm -rf`

### 3.3 Javen vault 当前的 permissions 配置（已存在）

Javen 你的 vault 应该已有 `.claude/settings.local.json` 配过 permissions（你之前主对话配过）。如果还没全配齐，**视频里这套 pattern 你可以借鉴**：

**推荐 allow（常用 safe 操作）**：
```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Bash(ls *)",
      "Bash(cat *)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Bash(python:*)",
      "Bash(pytest:*)",
      "Bash(npm install:*)",
      "Bash(npm run:*)",
      "Bash(mkdir -p:*)",
      "Edit(MyBrain/**)",
      "Edit(.claude/**)",
      "Write(MyBrain/notes/**)",
      "Write(MyBrain/wiki/**)",
      "Write(MyBrain/inbox/**)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(sudo:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)",
      "Write(.git/**)",
      "Write(MyBrain/raw/**)",
      "Write(MyBrain/archive/**)"
    ]
  }
}
```

**关键注意点**（对应 Javen vault 规则）：
- ✅ `deny Write(MyBrain/raw/**)` — vault 规则永远不修改 raw
- ✅ `deny Write(MyBrain/archive/**)` — vault 规则永远不修改 archive
- ✅ `allow Edit(MyBrain/**)` — 但允许编辑 raw 和 archive 外的所有 vault 文件

### 3.4 验证配置

配完后跑：
```bash
# 在项目根目录
claude config list  # 或类似命令
```

或直接发任务给 Claude Code 跑，看它有没有"少 ask 几次"

---

## 4. 视频 vs 实际：Auto-Permission Mode 跟手动 permissions 的关系

| | Auto-Permission Mode（2026 大会新加） | 手动 `permissions` 配置 |
|---|---|---|
| 默认状态 | enabled | needs config |
| 工作方式 | 分类器判断安全 / 危险 | pattern matching |
| 精度 | 模糊（取决于分类器） | 精确（你自己定 pattern） |
| 修改时机 | Anthropic 升级 model | 你随时改 |
| Override | `--no-auto-permission` flag | `deny` 字段 |

**互补关系**：
- 自动权限模式 ≈ "默认值升级"
- 手动 permissions ≈ "项目定制"
- 两个一起用最稳

### 4.1 推荐使用 strategy

**第 1 层**：让 Auto-Permission Mode 默认开（不用配，2026 大会后默认 enabled）
**第 2 层**：项目级精细化 `permissions` 配置（针对你常用 pattern）
**第 3 层**：`deny` 高危操作绝对禁止（防 prompt injection 或 model hallucination）

---

## 5. 给 Javen 的实战 actionable

### 5.1 你 vault 应该立刻确保的 deny 项

按你 CLAUDE.md 的"不做的事"清单，**确认这些都在 deny**：
```json
"deny": [
  "Write(MyBrain/raw/**)",          // 永远不修改 raw
  "Write(MyBrain/archive/**)",      // 永远不修改 archive
  "Bash(rm -rf MyBrain/**)",        // 防灾难性误删
  "Bash(git push --force:*)",       // 防 git 灾难
  "Bash(git reset --hard:*)"        // 防 git 灾难
]
```

去你 `.claude/settings.local.json` 查一下——如果缺，立刻补。

### 5.2 你应该追加的 allow 项（基于你日常工作流）

```json
"allow": [
  // 你 ECE 项目相关
  "Bash(python MyBrain/projects/**)",
  "Bash(pytest MyBrain/projects/**)",
  "Edit(MyBrain/projects/ece284-llm-ppg/**)",
  "Edit(MyBrain/projects/ece175b-adg/**)",
  // vault 编译相关
  "Edit(MyBrain/notes/**)",
  "Edit(MyBrain/wiki/**)",
  "Write(MyBrain/automation/reports/**)",
  // PDF 图像处理（你 ingest 流程用）
  "Bash(python -c 'import fitz*'):*",
  // git 安全操作（不含 push --force）
  "Bash(git add:*)",
  "Bash(git commit:*)",
  "Bash(git status:*)",
  "Bash(git log:*)"
]
```

### 5.3 验证你的 permissions 已配好

主对话直接跑这条 prompt：
> "扫描 .claude/settings.local.json 里 permissions 字段当前状态，对照 vault CLAUDE.md 的安全规则（raw/ archive/ 不可修改 + 不擅自启动 launchd），告诉我哪些缺失或冲突。"

我会回你 audit 报告。

### 5.4 注意 pitfalls

⚠️ **不要把 `deny` 数组写空** —— 这等于"全放行"，遇到 prompt injection 会出灾难

⚠️ **不要 allow `Bash(*)` 全 wildcard** —— 这等于关闭所有 shell 检查

⚠️ **慎用 YOLO mode**（DeepSeek TUI 视频提到，Claude Code 也有类似）—— 完全自动模式适合 sandbox 项目，**不要在 vault / 关键 repo 上开**

---

## ⚠️ 矛盾与未解决问题

- **`settings.local.json` 跟 `settings.json` 的优先级**：哪个 override 哪个？需要看官方文档
- **多 sub-agent 的 permissions 隔离**：sub-agent 是否继承主 session 的 permissions？还是独立？需要测试

## 🔗 关联

- [[2026-05-11_Claude_Code_新功能8项]] — Feature 4 Auto-Permission Mode 的精细化版本
- [[2026-05-11_DeepSeek_TUI登顶GitHub]] — 同样有 Plan / Agent / YOLO 三模式
- [[Claude Code 平台演化]] (wiki concept, 待编译)
- `MyBrain/CLAUDE.md` — vault 自身安全规则（raw / archive 保护）

## 📎 来源

- `projects/douyin-favorites-pipeline/Untitled 3.md`（视频原始字幕）
- [Claude Code settings 官方文档](https://docs.claude.com/en/docs/claude-code/settings)
