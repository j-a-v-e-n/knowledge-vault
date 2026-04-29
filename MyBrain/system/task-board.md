# 任务看板

> Javen 和 Claude 共用的任务看板。Javen 写下方向，Claude 接管执行；遇到需要决策的事写 `⚠️ blocked on @javen`，移到"🔒 阻塞"列等 Javen 拍板。

**最后更新**：2026-04-28
**当前状态**：2 进行中 / 0 阻塞 / 5 待启动 / 3 已完成
（更新 2026-04-28 晚：Anduril SWE Frontier Systems 已投出 (#2 📤)；inbox 整理完毕；新加 task-012 审批队列系统（已部分部署，approvals.md 就位 + CLAUDE.md 接入），daemon prompt 集成待主对话推进）

---

## 📥 待启动

- [ ] **task-012** | 部署"轻量审批队列"系统（approvals.md）| #P1 | owner: @claude（主对话）
  - **目标**：替代"在对话里打字 yes/no"为"vault 文件打勾批准"，让 Javen 决策更轻量 + 跨设备（手机 Obsidian app 也能批）
  - **触发**：Javen 2026-04-28 提出——简单审批不该需要打开 Claude Code 输入文字
  - **Definition of Done**：
    - `system/approvals.md` 文件就位 + 模板 + 真实当前 3-5 条待审批事项
    - `MyBrain/CLAUDE.md` 加 reference（每次 Claude session 启动就读）
    - daemon `prompt.md` 加 step：扫 approvals.md / 执行 [x] / 归档
    - 跑通一次：Javen 在某条上 `[x]` → 主对话或 daemon 看到 → 执行 → 移到 ✅ 已批准
  - **创建**：2026-04-28
  - **更新**：2026-04-28
  - **子任务**：
    - [x] a. 写 `system/approvals.md`（template + 真实初始 5 条待审批）— 2026-04-28
    - [x] b. `MyBrain/CLAUDE.md` 加 reference — 2026-04-28
    - [ ] c. 改 daemon `prompt.md`：加"扫 approvals.md → 执行 [x] → 归档"step ⚠️ blocked on 主对话（daemon 不能改 `~/.claude-daemon/`）
    - [ ] d. 端到端测试：Javen 打勾 → daemon 凌晨跑 → 验证执行成功 + 归档动作正确

- [ ] **task-011** | 每日邮箱 triage（daemon 自动扫 jacao@ucsd.edu 把重要邮件提上来） | #P0 | owner: @claude（**主对话**搭，daemon 跑）
  - **目标**：daemon 每天扫 Javen 邮箱过去 24h 邮件，按规则筛选重要的（招聘回复 / 学校重要通知 / 导师联系），写到 vault 让 Javen 早上一起来 5 分钟知道"今天有什么要处理"
  - **触发**：Javen 2026-04-28 凌晨提出——刚投 Anduril 简历，需要监控 recruiter 回信不漏掉 OA/面试邀请
  - **设计要点**（明天主对话推进时讨论）：
    1. **用 Anthropic Claude.ai Gmail MCP**（已有 `mcp__claude_ai_Gmail__*` 工具，list_threads / get_thread / label / create_draft 等）
    2. **筛选规则**（按重要性）：
       - 🔴 P0：投递公司（Anduril / Brain Corp 等 target-companies.md 上的）回信 / OA / 面试邀请 / 拒信
       - 🔴 P0：UCSD 老师 / TA 紧急（deadline / grade / 推荐信请求）
       - 🟡 P1：UCSD 课程通知（作业截止 / 考试时间）
       - 🟡 P1：学院讲座 / 实验室招人邮件（如果跟 Javen 兴趣 match）
       - 🟢 跳过：marketing / promotion / GitHub PR notifications / 推送类
    3. **输出位置**：`MyBrain/system/daemon-runs/<日期>-mail-triage.md`（跟 daemon 主报告分开，免得 Javen 早上一打开看到太多东西）
    4. **不做的事**：daemon **不自动回邮件 / 不点链接 / 不下载附件**——只 read + 筛 + summarize
    5. **频率**：每日凌晨 03:00（跟 daemon 主跑同步）+ 可选 7:00 早安再跑一次（让 Javen 起床看最新）
    6. **隐私**：jacao@ucsd.edu 是 UCSD 学生邮箱，邮件内容不公开 push 到 vault git（如果以后用 git 备份 vault，这个文件夹要 .gitignore）
  - **Definition of Done**：
    - email-triage skill 部署到 `.claude/skills/email-triage/SKILL.md`
    - daemon `prompt.md` / `rules.md` 更新允许 Gmail MCP 工具
    - 第一次 dry-run 跑通 → 输出第一份 mail-triage 报告 → Javen 审 quality（漏没漏、误报多不多）
    - 第二次跑（凌晨自动）→ Javen 早上确认重要邮件被 surface
  - **创建**：2026-04-28
  - **更新**：2026-04-28
  - **⚠️ 重要**：daemon **不能自己做这个 setup**（涉及改 .claude/skills/、~/.claude-daemon/）。Javen 想推进时主对话喊"推进 task-011"，主对话 Claude 来做。
  - **子任务**：
    - [ ] a. ⚠️ blocked on @javen — 验证 Gmail MCP 已授权（Anthropic Claude.ai 应该已通过 OAuth 连了 Javen 的 Google 账号；让 Javen 在某次对话里跑 `list_labels` 看是否真能访问邮箱）
    - [ ] b. 写 `.claude/skills/email-triage/SKILL.md`（含筛选规则 + 输出 format）
    - [ ] c. 改 daemon `rules.md`：允许 `mcp__claude_ai_Gmail__*` 工具（之前是禁的）
    - [ ] d. 改 daemon `prompt.md`：加邮箱 triage 优先级（早晨第一项）
    - [ ] e. dry-run：手动 spawn wrapper.sh，看第一份 mail-triage 报告 quality
    - [ ] f. Javen 审报告 → 调整筛选规则（误报 / 漏报）
    - [ ] g. 部署到每日凌晨自动跑 + 写到 daemon-runs/<日期>-mail-triage.md
    - [ ] h. （可选）加一个早上 7:00 的第二次扫描（让 Javen 起床能看到最新）

- [ ] **task-002** | Stage 1：UserPromptSubmit hook 自动 task-check | #P2 | owner: @javen
  - **目标**：每次跟 Claude 对话时自动注入看板状态，省去手动 `/task-check`
  - **Definition of Done**：UserPromptSubmit hook 配好；测试三次对话，每次 Claude 都能看到看板上下文
  - **创建**：2026-04-27
  - **更新**：2026-04-27
  - **子任务**：
    - [ ] a. 决定何时启动 Stage 1（建议 Stage 0 跑顺一周后再说）
    - [ ] b. 写 `hooks/inject-board.sh` 输出看板摘要
    - [ ] c. 在 settings.json 挂 UserPromptSubmit hook
    - [ ] d. 端到端测试

- [ ] **task-006** | 部署 AI Watch v2（每日 AI 趋势监测 daemon skill） | #P1 | owner: @claude（**主对话**，非 daemon）
  - **目标**：daemon 每天扫 25+ 个权威 AI 来源，按 Javen 简历画像（ECE ML/Controls + ROS2/YOLOv8 + 数字健康 + edge AI 潜力）写"行业雷达 + 项目教练 + 简历放大器"风格的早安简报到 `MyBrain/research/ai-watch/<日期>.md`；每条信息回答"是什么 / 为什么是你 / 能做什么小项目（含简历价值）/ 难度+耗时"
  - **Definition of Done**：
    - ai-watch skill 部署到 `.claude/skills/ai-watch/SKILL.md`（含 25+ 来源白名单 + Javen 画像 + 报告模板）
    - daemon `rules.md` 更新：解禁 ai-watch 白名单的 WebFetch
    - daemon `prompt.md` 更新：双任务优先级（先 ai-watch、剩余推看板）
    - 建好 `MyBrain/research/ai-watch/` 目录
    - 端到端测试：手动跑 wrapper.sh 一次产出第一份针对 Javen 的报告（≥3 条 importance-3 含项目灵感+简历价值）
    - 看板加 task-007「Recurring: 每日 AI Watch 运行」永久 in-progress
  - **创建**：2026-04-27
  - **更新**：2026-04-27
  - **⚠️ 重要**：daemon **不能自己做这个任务**（rules 第 4-5 条禁止改 `.claude/` 和 `~/.claude-daemon/`）。Javen 想推进时在主对话喊一声"推进 task-006"，**主对话 Claude** 来做。子任务 a/b/c 都涉及修改 daemon 自己的配置。
  - **🎯 设计原则（Javen 2026-04-27 提醒）**：报告格调**避免过度功利化**。简历相关性应该是**隐含副产物**（"哦这个我能玩玩"）而非显性目标（"这个能让简历加分 +X"）。带太强目的性会变成信息焦虑制造机，反而效果差。报告应该 **70% 启发好奇心 + 30% 落地建议**——先让 Javen 觉得"这事好玩 / 有意思"，再说"顺便能做个小项目"。importance 排序应该看"对 Javen 兴趣 + 当下重要性"而不是"对简历有多大用"。
  - **子任务**：
    - [ ] a. 写 `.claude/skills/ai-watch/SKILL.md`（含 25+ 来源白名单 + Javen 画像摘要 + 4-问题报告模板）⚠️ blocked on 主对话（daemon 不能改 .claude/）
    - [ ] b. 改 `~/.claude-daemon/rules.md`：解禁 ai-watch 白名单 URL 的 WebFetch ⚠️ blocked on 主对话（daemon 不能改自己配置）
    - [ ] c. 改 `~/.claude-daemon/prompt.md`：加双任务优先级 ⚠️ blocked on 主对话（同上）
    - [x] d. 建 `MyBrain/research/ai-watch/` 目录 — done 2026-04-28 (daemon 03:00)
    - [ ] e. 端到端测试：跑 wrapper.sh 烧 ~$1 看第一份报告（产出后 Javen 审阅质量）
    - [ ] f. 看板加 task-007「Recurring: 每日 AI Watch 运行」永久 in-progress（owner=@claude，daemon 自动跑）
    - [ ] g. （可选）如果第一份报告 Javen 不满意，迭代调整 skill 中的 Javen 画像 / 报告模板

- [ ] **task-008** | Google Drive 5GB 容量危机 — 长期存储方案 | #P2 | owner: @claude（**主对话**，需 Javen 决策）
  - **目标**：Javen vault 在 Google Drive 同步盘上，免费配额 15GB 但 Photos+Gmail 共享。担心未来满。调研 GitHub / Obsidian Sync / 自托管 / 升级付费等替代方案，给出推荐路径
  - **触发**：Javen 提到"刷到一个人把所有东西放 GitHub 上"，自己不懂细节，让我帮调研
  - **Definition of Done**：
    - 有一份 vault 大小现状报告（已盘点，见 daemon-runs/2026-04-27.md 或本对话）
    - 有一份方案对比表（GitHub / Obsidian Sync / Syncthing / iCloud / Dropbox / Google One / Nextcloud / 混合）
    - 给 Javen 一个明确推荐 + 风险/收益
    - Javen 选定方案后实施迁移
  - **创建**：2026-04-27
  - **更新**：2026-04-27（agent 调研完成，结论："不急、现在只装 git 备份就够"）
  - **🔑 调研关键发现**：
    1. **Vault 当前 415 MB，远低于 15 GB Drive 上限。按 ~500MB/学期增长，还能用 15-30 学期** = 整个本科+研究生都够
    2. **那个朋友的"放 GitHub"方法**：用 Obsidian Git plugin（[Vinzent03 维护](https://github.com/Vinzent03/obsidian-git)），桌面端真的"装上设个 5 分钟自动 commit 就忘了它存在"
    3. **GitHub 不是真"主存储"，是"备份 + 版本"**：单文件 100 MiB 限制，415 MB 完整 push clone 太重；只 push markdown（< 10 MB）就完美
    4. **不要去整体迁移到 GitHub**：vault 继续在 Drive，git 只做异地备份
  - **🎯 给 Javen 的明确推荐路径**：
    - **现在（这周）**：装 Obsidian Git plugin + 配 `.gitignore`（排除 raw/ attachments/）+ 建 GitHub 私有 repo → 30 分钟搞定，免费，从此有版本历史 + 异地备份
    - **下学期开学前**：评估 vault 是否过 2 GB，过了就升 Google One 100GB ($1.99/月)
    - **过 5 GB 时（2-3 年后）**：再考虑真迁移，那时候选 iCloud 50GB（$0.99/月）或 Obsidian Sync（$4/月，端到端加密）
    - **永远不要**：把 raw/ + attachments/ 整个 push 到 GitHub，或开 Git LFS（10GB 后收费且贵）
  - **子任务**：
    - [x] a. vault 大小盘点（du -sh 各类文件 / 各文件夹）→ 415 MB
    - [x] b. 调研 agent 报告完成（覆盖 GitHub / Obsidian Sync / iCloud / Syncthing / 混合方案 / Drive 坑等）
    - [ ] c. ⚠️ blocked on @javen — Javen 选 4 个动作之一：
      - **(c1) 现在装 git 备份**（推荐，半小时，免费）
      - **(c2) 现在啥也不做，等过 2 GB 再说**
      - **(c3) 直接升 Google One 100GB**（$1.99/月，省事）
      - **(c4) 我有 iPhone，迁去 iCloud**
    - [ ] d. 按选定方案实施
    - [ ] e. 验证：vault 仍能在 Obsidian 正常打开 + Claude Code 仍能 cwd 进去
    - [ ] f. 更新 daemon `wrapper.sh` 的 `VAULT` 路径（**仅当方案 c4 选了——路径变化才需要**）

- [ ] **task-009** | 投简历（2026 夏季实习季）| #P0 | owner: 混合（@claude 起草 + @javen 决策与投递）
  - **目标**：把简历投到合适的 ML/CV/Robotics/Embedded 实习机会；允许针对特定公司/岗位微调简历（不强制）
  - **背景**：Javen 大三，2027-06 毕业。2026 夏季实习是 junior-summer 关键机会，**申请窗口现在到 5 月**（很多公司 4 月底/5 月初截止）。简历目前在 `MyBrain/inbox/Javen_Cao_Resume.pdf`（一稿：Foton 内燃机实习 + ECE148 自驾小车 + ECE284 进行中）。痛点：没纯 ML/AI 实习经验、没 GitHub 高星、没 demo 部署技能（task-006 AI Watch 长远会帮补这些）
  - **Definition of Done**（recurring 任务，按阶段算）：
    - Spring 2026 末：投递策略 + 目标公司清单 + 主版本简历定稿
    - 第一批投出 20 份（精投）或 50 份（海投）
    - 至少 1 个面试反馈
  - **创建**：2026-04-27
  - **更新**：2026-04-28（**a/b/c/d 完成**：策略定 + career/ 建好 + 21 家公司 v1 + resume-master.md 含 7 强化点；待 Javen 拍板后推进 e-h）
  - **🤖 Daemon vs 主对话分工**：
    - ✅ Daemon 能做：研究目标公司、读 JD、起草定制简历版本（写到 vault）、夜间监测招聘页更新
    - ❌ Daemon 不能做：真正点击"投递"（涉及 LinkedIn/网申账号 + 个人身份）、与招聘官沟通邮件
    - daemon 推进受 task-009 子任务 a 是否解阻塞驱动
  - **子任务**：
    - [x] a. 投递策略已定（2026-04-27 by Javen）：
      - **方向**：ML / Robotics / AI 相关都行（不挑细分）
      - **公司类型**：无要求（all-inclusive）
      - **🇺🇸 国籍**：美国公民 — **不需要 visa sponsorship；国防类公司（Anduril/Northrop/General Atomics）都能投，这是大优势**
      - **地理优先级**：SD > 中国 > 远程 > 其他
      - **时间**：先冲 2026 夏季实习（紧急，5 月底大公司截止居多）
      - **方式**：精投（每份 30 min 定制，目标 ~20 份命中率高）
    - [x] b. 建 `MyBrain/career/` 目录结构 + 写好 `applications.md`（投递追踪表模板）+ `target-companies.md` v1（21 家公司，按 SD > Bay/SoCal > AI 独角兽 > 中国 分 4 tier，含"先投这 5 家"建议：Anduril / Brain Corp / Qualcomm / Pony.ai / Tesla）
    - [x] c. 简历主版本审阅：发现 7 个强化点（Foton 无数字、ECE148 缺 mAP、ECE284 占位符、Skills 缺 OpenCV/PyTorch、无 GitHub 链接、Claude daemon 独特经历可加）→ 详见 resume-master.md 文末注释 + daemon-runs/2026-04-28.md
    - [x] d. 把简历从 `inbox/` 挪到 `MyBrain/career/resume-master.md`（写一份**可微调的 markdown 版本**，含 7 个强化点注释 + 5 个待 Javen 确认事项）— done 2026-04-28
    - [ ] e. （recurring）建立目标公司清单首版（20-30 家）+ 招聘节奏（哪些已开放、哪些 5 月开放、哪些 fall）
    - [ ] f. （recurring）每次新投：Claude 读 JD → 起草定制简历 → 起草 cover letter（如需）→ 你审阅 → 投 → 记到 applications.md
    - [ ] g. （recurring）每周末复盘：投了几份 / 收到几个反馈 / 下周目标 + 节奏调整
    - [ ] h. （recurring，daemon 可做）监测目标公司招聘页有无新岗位 → 在 daemon-runs 里通知 Javen

---

## 🚧 进行中

- [ ] **task-003** | PHIL28 课程材料编译 | #P1 | owner: @claude
  - **目标**：把 `raw/PHIL28/` 下 8 个材料（6 讲座 pptx + syllabus + midterm questions）编入 wiki 体系
  - **Definition of Done**：8 个 source 页 + 1 个 PHIL28_概览 + Mill 核心论点提取为 concept 页 + INDEX/log/gaps 同步
  - **创建**：2026-04-27
  - **更新**：2026-04-27（daemon dawn-shift 推进 a/b/d/e）
  - **子任务**：
    - [x] a. 扫描 `raw/ucsd/Spring 2026/PHIL28/`，列文件清单（6 pptx + 2 pdf；DoD 原写"7 讲座"实际 6 个）
    - [x] b. 建 `wiki/哲学/` 子目录
    - [ ] c. ⚠️ blocked on @javen — 按周编译 6 个 pptx → source 页（daemon 无 python-pptx 工具，需 Javen 在主对话触发）
    - [x] d. 编译 syllabus → [[PHIL28_2026_课程大纲]] + [[PHIL28_概览]]
    - [x] e. midterm questions → [[PHIL28_2026_期中考题清单]]（6 题候选 + 关键词索引）
    - [ ] f. ⚠️ blocked on @javen — 提取 Mill 核心 concept 页（依赖 c 子任务的 pptx 内容才能交叉验证）
    - [ ] g. 更新 INDEX/log/gaps（daemon 已部分推进，待 c/f 完成后做最终汇总）

---

## 🔒 阻塞

（暂无）

---

## ✅ 已完成

- [x] **task-010** | Ingest：ECE284 两篇新 IMWUT 论文（LemurDx + DopFone） | #P1 | owner: @claude | done 2026-04-27
  - **目标**：编译 Javen 下载的两篇 ACM IMWUT 论文进 vault（重命名 + 渲染图 + source 页 + 双向回链 + 索引/日志/gaps 更新）
  - **Definition of Done**：
    - PDF 重命名到 `作者_年份_关键词.pdf` 规范 ✓
    - 13 张关键图渲染到 `attachments/ECE284/`（PyMuPDF 2.5×）✓
    - 两个 source 页按"先懂再细"四步结构写完 ✓（[[Arakawa_2023_LemurDx]]、[[Garg_2025_DopFone]]）
    - 7 个相关 ECE284 source 页加双向回链 ✓
    - INDEX.md / log.md / gaps.md 更新 ✓
  - **完成**：2026-04-27
  - **副产物（lint 待办）**：发现 `notes/ucsd/Spring 2026/ECE284/Bhamla_2017_Paperfuge.md` 实际内容是 Apple Heart Study 演讲稿，真正 Paperfuge 笔记错位在 `raw/` 里——两条违反"raw 不修改 + source 只在 notes/"规则。已在变更摘要里告知 Javen，等其拍板修复方案
  - **副产物（concept 提取候选）**：消费级智能手机/可穿戴健康感知现已积累 7 个独立来源（LemurDx + DopFone + Bhamla + Song + Perez + Shah + Zhang）——达到 concept 阈值。建议建 `wiki/医疗技术/` 子目录 + 提取 [[消费级设备健康感知]] concept 页。等 Javen 确认后启动

- [x] **task-005** | 部署 Stage 2 后台守护（launchd daemon） | #P0 | owner: @claude | done 2026-04-28
  - **目标**：让 Claude Code 在 Javen 睡觉时自动推进看板任务（每天凌晨 3:00 唤醒、$2/次、30 分钟、最多 5 任务）
  - **Definition of Done**：plist 装载 launchctl ✓ + 端到端跑通一次 ✓ + 第二天早上 daemon-runs/<日期>.md 有真实运行报告 ✓
  - **创建**：2026-04-27
  - **完成**：2026-04-28（daemon 首次在夜间自动运行：推进 task-009 c/d，写 resume-master.md，报告在 daemon-runs/2026-04-28.md）
  - **子任务**：全部完成（a-m [x]），最后 m = 本次 daemon 运行本身即为验证

- [x] **task-001** | 搭建任务看板自动化系统 Stage 0 | #P0 | owner: @claude | done 2026-04-27
  - **目标**：复刻思瑶视频里的"睡觉时也能干活"看板系统的最小可用版本
  - **Definition of Done**：看板文件 + 2 个 skill + audit hook + Claude 操作指令 + 端到端 demo 跑通 ✓
  - **创建**：2026-04-27
  - **完成**：2026-04-27
  - **子任务**：
    - [x] a. 编译思瑶视频字幕到 vault（source 页 + raw 字幕）
    - [x] b. 研究 Claude Code 官方 hooks/skills/subagents 文档
    - [x] c. 研究开源对标项目（ClaudeNightsWatch / claude-kanban / Ralph Wiggum）
    - [x] d. 设计五层架构与分阶段方案
    - [x] e. 创建 `MyBrain/system/` 目录结构
    - [x] f. 写 `task-board.md` 模板（本文件）
    - [x] g. 写 `system/CLAUDE.md`（Claude 操作指令）
    - [x] h. 写 `system/README.md`（用户文档）
    - [x] i. 写 `task-check` / `task-add` skills
    - [x] j. 写 `audit.sh` hook 与 `settings.json`（pipe-test 5 种输入全过；jq schema 校验通过）
    - [x] k. 在 `MyBrain/CLAUDE.md` 末尾接入"任务看板系统"小节（要点速览 + 指向 system/CLAUDE.md）
    - [x] l. 端到端 demo：本次完成所有子任务的 Edit 操作即是 demo（task-board 状态已正确更新到此卡）

---

## 📋 任务卡格式说明

每个任务卡都用如下结构：

```markdown
- [ ] **task-NNN** | 任务标题 | #P0/#P1/#P2 | owner: @claude / @javen
  - **目标**：一句话说为什么做这件事
  - **Definition of Done**：判断完成的标准（可验证）
  - **创建**：YYYY-MM-DD
  - **更新**：YYYY-MM-DD
  - **子任务**：
    - [ ] a. 子任务 1
    - [x] b. 子任务 2（已完成）
    - [ ] c. 子任务 3 ⚠️ blocked on @javen — 需要决定 X 还是 Y
```

**字段约定：**

| 字段 | 含义 |
|---|---|
| `task-NNN` | 三位数字 ID，自动递增 |
| `#P0` | 紧急且重要（7 天内 deadline 或阻塞他人） |
| `#P1` | 重要不紧急（默认） |
| `#P2` | 长期/灵感/可选 |
| `owner: @claude` | Claude 可自主推进 |
| `owner: @javen` | 需要 Javen 决策或动手 |
| `⚠️ blocked on X` | 卡住，等 X 解锁；Claude 不再尝试推进，转做别的 |

**操作命令**：

| 命令 | 用途 |
|---|---|
| `/task-check` | 扫一遍看板报告状态（不修改） |
| `/task-add <标题>` | 添加新任务到"待启动"列 |
| 直接说"推进 task-005" | Claude 接管该任务 |
| 直接说"看板上能做的都做了" | Claude 自主推进所有 owner=@claude 且无阻塞的任务 |
| 直接说"task-005 用 X 方案" | Claude 解阻塞、移回"进行中" |

详细规则见 `MyBrain/system/CLAUDE.md` 与 `MyBrain/system/README.md`。
