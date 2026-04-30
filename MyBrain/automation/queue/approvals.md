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

### 🎯 2026-04-30 14:50 一组 (task-017 + task-018) — Javen 派活"两个 project 全让 AI 干"

打勾这 5 条，AI 就能自动接力把 ECE175B 和 ECE284 两个 project 推到「等你检查」的程度。**全部 5 条 5 分钟可批完。**

- [ ] **2026-04-30 14:50** | task-018 (ECE284) | 批准本机装 Python 实验包 (`pip install --user numpy scipy scikit-learn matplotlib anthropic mat73 pyEDFlib`)
  - **建议**：批准（这些都是数据科学标配，不会动系统 Python）
  - **批准后做**：主对话 / 我下次启动时跑 `pip install --user ...` 装到你 user site-packages
  - **不批的影响**：ECE284 实验代码无法运行，daemon 也跑不了 LOSO 评估
  - **隐私/安全**：这些都是 PyPI 知名包；`--user` flag 不动 system Python；Anthropic 是官方 SDK

- [ ] **2026-04-30 14:50** | task-018 (ECE284) | 批准下载 IEEE SPC 2015 dataset 到 `MyBrain/projects/ece284-llm-ppg/data/`（~50 MB，12 .mat 文件）
  - **建议**：批准（论文公开数据，proposal 已 cite [Zhang 2015]）
  - **批准后做**：主对话跑 `curl https://zenodo.org/.../IEEE-SPC-2015.zip -o data.zip && unzip` 一键下完
  - **不批的影响**：ECE284 实验跑不起来（数据是 RQ1/RQ2 的根基）
  - **大小说明**：50MB 远低于 vault 415MB → 15GB Drive 配额安全；之后会被 .gitignore 排除掉不会 push GitHub

- [ ] **2026-04-30 14:50** | task-018 (ECE284) | 批准生成 ANTHROPIC_API_KEY 给 ECE284 用（你 Claude Max 订阅 → console.anthropic.com 5 min 生成）
  - **建议**：批准（proposal 估算 ~3M tokens / $5 以内，远低于你 Max 5x 月度配额）
  - **批准后做**：你打开 https://console.anthropic.com/settings/keys → "Create Key" → 命名 `ece284-ppg` → 复制 key 给我，我写到 `~/.config/anthropic-keys/ece284` (chmod 600)，代码 import 这个 key。**daemon 也能用同一个 key 凌晨跑实验**
  - **不批的影响**：λ-generator 系统跑不了 = 主贡献废了，只剩 baseline
  - **风险**：API key 仅写到 `~/.config/...` 600 权限文件，不会进 git，不会 push GitHub
  - **替代方案**：如果你不想用 API key，可以让 daemon 调本机 Claude Code CLI（更慢但不要 key），但 ~1800 windows 太慢。**强烈推荐 API**

- [ ] **2026-04-30 14:50** | task-017 (ECE175B) | 批准 GPU 方案 — 选一个
  - **(a) Colab Pro $10/月** — **推荐**。30 秒注册，浏览器开 ipynb 就能用 A100/V100，最多 24h 连续。我把代码写成 Jupyter notebook 你直接挂上跑
  - **(b) UCSD DSMLP** — 免费给学生，但 GPU 老（K80），排队等位时间不可控；适合长期跑长 job
  - **(c) RunPod / Vast.ai pay-per-hour** — RTX 3090 $0.3/h，4090 $0.5/h；适合"集中训 6 小时再关"省钱；要 SSH key
  - **(d) Kaggle Notebook 免费 GPU** — 30 小时/周 P100，免费但有限制
  - **建议**：批 (a) Colab Pro（最省事，期末忙起来 GPU 不能成为瓶颈）
  - **批准后做**：你点 colab.research.google.com 注册 Pro → 我把 train.py 改成 ipynb 兼容版本 → 你 Drive mount 后挂上跑
  - **不批的影响**：ECE175B 训练永远卡在"代码写完但跑不了"

- [ ] **2026-04-30 14:50** | task-017 + 018 | 批准建 2 个 GitHub 私有 repo (ece175b-adg, ece284-llm-ppg)
  - **建议**：批准（课程要求"include GitHub repo with README"）
  - **批准后做**：你打开 github.com → "+New" 建 2 个 private repo → 名字 `ece175b-adg` 和 `ece284-llm-ppg`（30 秒）→ 我跑 `git remote add origin ... && git push` 把 vault 里的 projects/ 内容推上去
  - **不批的影响**：可以晚点批，不影响代码开发；但 final report 时要交 GitHub link，不批 = 自己手动建
  - **风险**：private repo，只你看得到；data/ 不 push（已 .gitignore）；API key 不 push（不在 repo 里）

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
