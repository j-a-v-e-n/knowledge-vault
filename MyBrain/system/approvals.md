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

- [x] **2026-04-28 23:30** | task-006 | 部署 AI Watch v2 daemon skill（每日 AI 趋势早报）?
  - **建议**：批准（你昨晚明确表过兴趣 + 设计原则已定 70% 启发好奇心 / 30% 落地建议）
  - **批准后做**：30-60 min 工作。写 `.claude/skills/ai-watch/SKILL.md` + 改 daemon rules/prompt 解禁 ai-watch 白名单 + 端到端测试 + 第一份报告产出
  - **不批的影响**：daemon 不会扫 AI 资讯，你需要自己每天关注 SOTA / 找项目灵感

- [x] **2026-04-28 23:30** | task-011 | 部署邮箱 triage daemon？
  - **建议**：批准（早上已验证 Gmail MCP 真能 access 你邮箱 + Anduril confirmation 已自动 surface）
  - **批准后做**：30-60 min。写 `.claude/skills/email-triage/SKILL.md` + 改 daemon rules/prompt 允许 Gmail MCP + 测试一次产出第一份 mail-triage 报告
  - **不批的影响**：每天得手动扫邮箱，可能漏 recruiter 回信 / OA 邀请

- [x] **2026-04-28 23:30** | task-008 c1 | 装 git 备份（Obsidian Git plugin + GitHub 私有 repo）？
  - **建议**：批准（免费、半小时、即使将来不真迁 GitHub 也是异地备份保险）
  - **批准后做**：装 Obsidian Git plugin + 配 .gitignore（排除 raw/ attachments/）+ 建 GitHub 私有 repo + 自动 5 分钟 commit
  - **不批的影响**：vault 仍然只在 Google Drive 一份，没版本历史

- [x] **2026-04-28 23:30** | task-009 (Brain Corp) | fetch braincorp.com 真 JD + finalize daemon 凌晨写的草稿 + 投？
  - **建议**：先看 daemon 草稿质量决定
  - **批准后做**：我 WebFetch braincorp.com careers + 找 SWE/Robotics intern + 调整草稿 + 你审 + 渲染 PDF + 投
  - **不批的影响**：第二家公司今天不投；草稿留 vault 以后可用

- [ ] **2026-04-28 23:30** | GitHub profile setup | fork team repo 让 j-a-v-e-n profile 不空 + 设头像/bio？
  - **建议**：批准（5 分钟事，Anduril recruiter 进入面试阶段会去看你 GitHub）
  - **批准后做**：你自己 fork（30 秒 GUI）+ 我可以指导设 bio/name/profile pic
  - **不批的影响**：GitHub 仍然空 repo，被点进去 looks unprofessional

---

## ✅ 已批准（执行完归档；满 7 天清理）

（暂无）

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

vault 在 Google Drive 同步盘 → 手机装 Obsidian app + 同步 vault → 打开 `system/approvals.md` → 打勾保存 → 几秒同步回 Mac → 下次 Claude 启动看见。

适合场景：你早上通勤 / 课间 / 睡前刷一下，把 AI 排队等批准的事顺手处理掉。
