# Permissions 审计报告 — 2026-05-11

> 对照 [[2026-05-11_Claude_Code_permissions提前授权]] 推荐配置，检查 `.claude/settings.json` 当前状态。

**审计时间**：2026-05-11 03:xx (by daemon)  
**被审文件**：`.claude/settings.json`（**注：`settings.local.json` 不存在，目前只有 `settings.json`**）

---

## 🔴 高优先级缺口（建议 Javen 本周修复）

### 1. 完全缺少 `deny` 字段
**当前**：settings.json 中无任何 `deny` 规则。  
**风险**：遇到 prompt injection 或 model hallucination 时，没有任何硬性拦截。  
**应加的最低 deny 规则**：
```json
"deny": [
  "Bash(rm -rf:*)",
  "Bash(sudo:*)",
  "Bash(git push --force:*)",
  "Bash(git reset --hard:*)",
  "Write(MyBrain/raw/**)",
  "Write(MyBrain/archive/**)"
]
```
这 6 条直接对应 vault CLAUDE.md 的"你不做的事"清单，应该始终存在。

### 2. 缺少 `Read(**)` 全局读权限
**当前**：没有 Read 相关的 allow。  
**影响**：每次 Claude 读取 vault 文件都需要弹窗确认，headless daemon 卡死。  
**应加**：`"Read(**)"` 加入 allow。

---

## 🟡 中优先级缺口（建议 Javen 方便时修复）

### 3. 缺少常用 Bash 读操作
推荐的 `Bash(ls *)`, `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(grep:*)`, `Bash(find * -*)` 均不在 allow 列表。  
影响：daemon 每次查 git 状态、搜索文件都要弹窗。

### 4. 缺少 vault 常规编辑权限
`Edit(MyBrain/**)`, `Write(MyBrain/notes/**)`, `Write(MyBrain/wiki/**)`, `Write(MyBrain/automation/reports/**)` 均不在 allow 列表。  
影响：daemon 每次写报告、更新 wiki 都需要 Javen approve（headless 卡死）。

### 5. 缺少 Python 相关 Bash 权限
`Bash(python:*)`, `Bash(python3:*)`, `Bash(pytest:*)` 不在 allow。  
影响：主对话运行 ECE284/175B 脚本时仍需每次确认。

---

## ✅ 现有配置中好的部分

- `Bash(mkdir -p *)` 已有 — 创建目录不阻塞
- `Bash(open *)` 已有
- Gmail MCP read-only 工具 (`search_threads`, `get_thread`, `list_labels`) 已有
- `.claude/skills/` 相关 Edit 权限已有
- hooks (PostToolUse audit、SessionStart、SessionEnd、Stop) 已配好

---

## 📋 建议补丁（主对话执行，daemon 不动 .claude/ 文件）

主对话让 Javen 跑以下 prompt：

> "帮我把 `.claude/settings.json` 的 permissions 补成以下配置（在现有 allow 基础上追加，并加上 deny 字段）："

```json
// 追加到现有 allow 数组：
"Read(**)",
"Bash(ls *)",
"Bash(git status:*)",
"Bash(git diff:*)",
"Bash(git log:*)",
"Bash(grep:*)",
"Bash(find * -*)",
"Bash(python3 *)",
"Bash(python *)",
"Bash(pytest *)",
"Edit(MyBrain/**)",
"Write(MyBrain/notes/**)",
"Write(MyBrain/wiki/**)",
"Write(MyBrain/automation/reports/**)",
"Write(MyBrain/automation/runs/**)"

// 新增 deny 字段：
"deny": [
  "Bash(rm -rf:*)",
  "Bash(sudo:*)",
  "Bash(git push --force:*)",
  "Bash(git reset --hard:*)",
  "Write(MyBrain/raw/**)",
  "Write(MyBrain/archive/**)",
  "Write(.git/**)"
]
```

---

## 📎 参考
- [[2026-05-11_Claude_Code_permissions提前授权]] — 视频推荐配置
- `MyBrain/CLAUDE.md` §你不做的事 — deny 规则的来源依据

*生成于 2026-05-11 03:xx by daemon (task-026 sub e)*
