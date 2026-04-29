# 审批队列 (Approvals)

> 让 Javen 用**打勾**代替"在 Claude Code 里打字回应"批准简单的 yes/no 决定。
>
> **打勾 `[x]` = ✅ 批准** → Claude / daemon 下次启动看到，立刻执行 + 移到下面已批准列
> **直接删掉那行 = ❌ 拒绝** → AI 看不到了 = 不会做
>
> 在哪里打勾：Obsidian 桌面 / 手机 app（Google Drive 同步盘自动同步）。
>
> 谁能写：主对话 Claude / 凌晨 daemon / Javen 自己。

---

## ⏳ 待审批

- [ ] **2026-04-28 23:30** | GitHub profile setup | fork team repo 让 j-a-v-e-n profile 不空 + 设头像/bio？
  - **建议**：批准（5 分钟事，Anduril recruiter 进入面试阶段会去看你 GitHub）
  - **批准后做**：你自己 fork（30 秒 GUI）+ 我可以指导设 bio/name/profile pic
  - **不批的影响**：GitHub 仍然空 repo，被点进去 looks unprofessional

---

## ✅ 已批准（执行完归档；满 7 天清理）

- [x] **2026-04-28 23:30** | task-006 | 部署 AI Watch v2 daemon skill
  - **done** 2026-04-29 00:15 by 主对话 Claude
  - **outcome**: 写完 `.claude/skills/ai-watch/SKILL.md`（70% 启发好奇心 / 30% 落地建议设计落地）+ daemon `wrapper.sh` 加 WebSearch 白名单 + `rules.md` 改 rule 15 限定 ai-watch 上下文使用 WebSearch + `prompt.md` 加 Step 0.5(a) 每日跑一次 + 输出位置 `MyBrain/automation/reports/ai-watch/<date>.md`
  - **第一份报告**：等 2026-04-29 03:00 daemon 自动跑产出（已 verify 预检全过）

- [x] **2026-04-28 23:30** | task-011 | 部署邮箱 triage daemon
  - **done** 2026-04-29 00:15 by 主对话 Claude
  - **outcome**: 写完 `.claude/skills/email-triage/SKILL.md`（read-only，scan past 24h，分 🔴 立即 / 🟡 当天 / ⚪ 已归类）+ daemon `wrapper.sh` 加 4 个 Gmail MCP read-only 工具 white-list（search_threads / get_thread / list_labels / list_drafts）+ `rules.md` 加 17-19 条 Gmail MCP 边界（write 类不放，避免擅改你 Gmail 状态）+ `prompt.md` 加 Step 0.5(b) + 输出位置 `MyBrain/automation/reports/email-triage/<date>.md`
  - **第一份报告**：等 2026-04-29 03:00 daemon 自动跑产出

- [x] **2026-04-28 23:30** | task-008 c1 | 装 git 备份（Obsidian Git plugin + GitHub 私有 repo）
  - **partial done** 2026-04-29 00:10 by 主对话 Claude
  - **outcome (我做的)**: `.gitignore` 配好（排除 raw/ 300M、attachments/ 99M、archive/、Clippings/、daemon logs、.obsidian/workspace state、plugin binaries）+ `git init -b main` + initial commit `5b1498f`（117 文件，9MB 工作集）+ 写了完整接力指引 `MyBrain/automation/docs/git-backup-setup.md`
  - **awaiting Javen (GUI 步骤)**: ① 浏览器建 GitHub 私有 repo（30s）② Obsidian → Settings → Community plugins 装 Obsidian Git（1min）③ terminal 跑 `git remote add origin ... && git push -u origin main`（30s）。完整步骤见 `git-backup-setup.md`
  - **note**: 不全闭环但卡在 GUI 限制；剩下步骤 ≤ 5 分钟，等 Javen 有空做

- [x] **2026-04-28 23:30** | task-009 (Brain Corp) | fetch braincorp.com 真 JD + finalize 草稿 + 投
  - **done (closed by external)** 2026-04-29 00:00 by 主对话 Claude
  - **outcome**: ⛔ **不可执行** — Brain Corp 的 "2026 Summer Intern - Software Engineering - Autonomy" 已于 **2026-04-01 18:10 CST 下架**（BuiltIn 显示明确 "Sorry, this job was removed at..."）。今天 4/29，错过 28 天
  - **action taken**: 在 `target-companies.md` 把 Brain Corp 标 ❌ 2026 cycle closed；daemon 凌晨写的草稿 (`resume-versions/2026-04-28_braincorp-autonomous-robotics.md`) 保留，给 2026 fall 全职 / 2027 summer 用
  - **next move**: 跳到 target-companies tier 1 的 #1 Qualcomm（SD-based 总部，ECE/嵌入式/Edge AI 完美对口）— 主对话 Claude 在你下次说"投 Qualcomm"时启动

---

## ❌ 已拒绝（满 7 天清理）

（暂无）

---

## 📋 字段约定

每条格式：

```markdown
- [ ] YYYY-MM-DD HH:MM | 任务 ID / 触发源 | 一句话说要审批什么
  - **建议**：批准 / 谨慎 / 看你
  - **批准后做**：（具体执行什么）
  - **不批的影响**：（如果你不批 / 删掉，下一步会怎样）
```

## 🤖 给 Claude / daemon 的操作规则

1. **何时往这里写**：遇到任何"需要 Javen 简单 yes/no 决定"的事 → append 一条到 ⏳ 待审批，**不要**在对话里逼用户打字回答
2. **何时读**：每次 session 启动 / daemon 跑 → 先 Read 此文件
3. **看到 [x] 怎么办**：执行批准的动作 → 完成后把这条**移到** ✅ 已批准列 + 加 done timestamp + 简短 outcome
4. **看不见的（用户删了）**：= 拒绝 = 不动它，不要追问"你为啥删了那条"
5. **不擅自批准**：哪怕 daemon 自己提的，也要等 [x] 才执行
6. **简单决策才用这里**：复杂多选（比如 task-008 的 c1/c2/c3/c4）还是用对话讨论，不要塞 4 条 yes/no 进 approvals

## 📱 手机端使用

vault 在 Google Drive 同步盘 → 手机装 Obsidian app + 同步 vault → 打开 `automation/queue/approvals.md` → 打勾保存 → 几秒同步回 Mac → 下次 Claude 启动看见。

适合场景：你早上通勤 / 课间 / 睡前刷一下，把 AI 排队等批准的事顺手处理掉。
