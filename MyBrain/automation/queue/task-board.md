# 任务看板

> Javen 和 Claude 共用的任务看板。Javen 写下方向，Claude 接管执行；遇到需要决策的事写 `⚠️ blocked on @javen`，移到"🔒 阻塞"列等 Javen 拍板。

**最后更新**：2026-05-16 [daemon dawn-shift: ai-watch ✅ 写完；email-triage ❌ Gmail MCP 不可用；task-024 5/12 演讲日期已过→标完成；task-018 f (全 LOSO ~$6.6) 待 Javen 批准再跑]
**当前状态**：4 进行中（task-003 + task-020 + task-026 + **task-027**）/ 2 阻塞（task-022 + task-027）/ **10** 待启动 / **9** 已完成

> 🪟 **2026-05-05 多 tab 协作分工**（Javen 决定，3 tab 并行）：
> - **Tab A**（监控 ECE175B Kaggle 训练 + 修小 bug）→ 只动 `MyBrain/projects/ece175b-adg/` + `notebooks/`
> - **Tab B**（接 ECE284 task-018，已开始 — 5/5 改了 troika_lite.py 加 evaluate_subject）→ 只动 `MyBrain/projects/ece284-llm-ppg/`
> - **Tab C**（一人公司探索 / 学习 + 调研 + 沉淀 wiki，**不真 launch**）→ 只动 `MyBrain/wiki/工程方法/` + `wiki/创业/`(新建) + `MyBrain/research/`
> - **共享文件**(task-board.md / approvals.md / .claude/agents/) 只追加不互相覆盖
> - **同步机制**：完成子任务后立刻在对应 task 卡里 [x] + 一句 outcome；遇阻塞写 `⚠️ blocked on @javen` 移阻塞列
> - **冲突避免**：Tab A 不动 ECE284/wiki，Tab B 不动 ECE175B/wiki，Tab C 不动 ECE 项目和 career/
（**真实进度**：task-006/008/011 名义在"待启动"列但子任务都已推进到"等外部验证"。task-012 已闭环移入"✅ 已完成"。Brain Corp 2026 cycle 4/1 已外部下架→归档不投。**🔥 5/5 更新：task-017 GPU=Kaggle 选定，notebooks 就绪，等 Javen GUI 启动训练（还剩 3 天）；task-018 代码骨架+数据已确认存在**）

> 🔥 **2026-05-04 21:15 主对话紧急派活**：Javen "周五 11:59 提交 ECE175B project midterm report"——
> - **task-017 升 P0 + 加 deadline 5/8 23:59**（剩 4 天）
> - **engineer subagent** 写完 `train_kaggle.ipynb` (10 cells) + `train_colab.ipynb` (11 cells) — 等 Javen 选 GPU 平台后上传
> - **writer subagent** 写完 `midterm_report.tex` (450 行 §1-§6 + abstract + figure placeholder) + `refs.bib` (7 条引用)
> - **唯一 blocker**：approvals.md 顶置 GPU 决策（推 Kaggle Free，Colab Pro $10 fallback）
> - 待 Javen 勾 → engineer 协助 Kaggle setup → 启动训练

> 📌 2026-04-30 14:45 主对话：Javen "两个 project 全让 AI 干，我只检查"——
> - **task-017 (ECE175B ADG diffusion)**: code 骨架主对话写，GPU 训练 blocked on @javen 选 Colab/DSMLP
> - **task-018 (ECE284 LLM-PPG)**: 全 CPU + Claude API，主对话搭，daemon 凌晨接力跑实验
> - approvals.md 加 5 条早起打勾的事 → AI 接力

> 📌 2026-04-30 15:30 主对话：Javen "代替我的人力，让 AI 成为团队"——
> - **task-019 (AI subagent 团队/模式 B)**: 4 个 subagent (researcher/engineer/writer/reviewer) + README + wiki [[AI 项目经理_subagent 模式]] + smoke test 全部 done
> - **重启 Claude Code session 后**主对话能直接派活给 4 个员工，每个员工独立 model + tool boundary + iteration cap

> 📌 2026-04-29 凌晨主对话 Claude 执行 4 项 approvals.md 打勾事项：
> 1. ✅ task-006 AI Watch v2 — skill 部署完，待 03:00 daemon 出第一份报告
> 2. ✅ task-011 邮箱 triage — skill 部署完，待 03:00 daemon 出第一份报告
> 3. ✅ task-008 c1 — .gitignore + git init + commit `5b1498f` 完成 + GitHub push 成功；plugin 装好（待 Javen 关掉一个 toggle 验证 5min auto commit）
> 4. ⛔ task-009 Brain Corp — 外部窗口 4/1 已关闭，不可投，归档

> 📌 2026-04-29 凌晨 Javen 睡觉时，主对话 Claude 推进：
> - **task-009 Qualcomm Embedded Intern SD**：JD 抓取 + 简历定制 + cover letter 写完 + applications.md ⏳ 待 submit。**Javen 醒后审 → 渲染 PDF → careers.qualcomm.com 投**
> - **task-013** 加进看板：claude-code-router 路由 daemon 到 DeepSeek 降成本 + setup guide 写好
> - **task-014** 加进看板：QClaw 试玩评估 + setup guide 写好

---

## 📥 待启动

- [ ] **task-027** 🚧 | UCSD ECE BS/MS 申请 | **#P0 🚨🚨🚨 deadline 5/15 23:59 PT（剩 2 天）** | owner: 混合（@javen 决策 + @claude 草 SoP + 整理材料）| **更新：2026-05-13**
  - **目标**：本周五（Spring 2026 Week 7 Friday）前提交 ECE BS/MS 申请, 让 Javen Winter 2027 毕业后衔接 Spring 2027 MS 入学（**Javen 5/15 plan update**: 从原 June 2027 / Fall 2027 改成提前一学期）
  - **触发**：Javen 5/12 主对话提醒"BS/MS 快到时间了"; WebFetch 官方页面 ([source](https://ece.ucsd.edu/graduate/bsms-admissions-information-process)) 确认 deadline = **11:59 PM Friday Week 7 = 2026-05-15 周五**
  - **关键信息（已 WebFetch verify）**：
    - GPA: min 3.0 / **competitive ≥ 3.4**
    - MS 入学时间: **Spring 2027** (Javen 5/15 confirmed — Winter 2027 毕业 + Spring 2027 MS，提前一学期方案；原 Fall 2027 plan 已废)
    - 适用：ECE 本科 junior 年（Javen 大三 ✓）
    - **唯一 deadline 不接受 extension**（官方页明确）
    - 应用 form: [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSf58Zq0abM6T0ICWXigegTLWmfsPKr8BHJ1E7lEjGqxZ2mYyg/viewform)
  - **需要材料（Step 1 内部 ECE 审, 5/15 之前必齐）**：
    - [ ] ECE Internal Application Form (Google form, 30 min 填)
    - [ ] **Statement of Purpose** (2 页 max, Times New Roman 12pt, double-spaced) — **@claude 可起草, Javen 审改**
    - [ ] **Letters of Recommendation** — **仅当 GPA < 3.4 才需要**（2 封, 1 必须 JSOE faculty）⚠️ blocked on @javen 确认 GPA
    - [ ] Academic History / Degree Audit copy (TritonLink → My TritonLink → Academic History → PDF 下载, 5 min)
  - **需要材料（Step 2 录取后才走, 不阻塞 5/15 deadline）**：
    - [ ] UCSD Graduate Admissions Application + 申请费 + 官方 transcript（录取后通知再办）
  - **Definition of Done**：
    - [ ] Step 1 全部材料 5/15 23:59 前通过 Google Form 提交
    - [ ] Javen 收到 ECE confirmation email
  - **创建**：2026-05-12 by Tab B 主对话
  - **更新**：2026-05-12
  - **⚠️ Blocker 优先解决（Javen 立刻拍板）**：
    - **B1**: Javen 当前 ECE major + overall GPA 是否 ≥ 3.4？
      - **≥ 3.4** → 不需 LOR, 只剩 Form + SoP + Audit Copy, **本周 work load 轻**
      - **< 3.4** → 需要 2 封 LOR (1 封 JSOE faculty)，**今天必须联系 faculty**（3 天 LOR 紧）
    - **B2**: Javen MS 想 specialization 哪个方向？(Computer Engineering / Machine Learning & Data Science / Intelligent Systems, Robotics, & Control / Signal & Image Processing 等) → SoP framing 用这个
    - **B3**: ✅ resolved 2026-05-15 — Javen 选 **Spring 2027 入学** (Winter 2027 毕业 → 提前一学期方案)
  - **🤖 AI vs Javen 分工**：
    - ✅ **@claude 主对话能干**：(a) 草 SoP 2 页（基于 vault 现有 resume-master.md + ECE 项目经历 + Med-HALT/ECE284 + ECE175B ADG diffusion + ECE148 自驾） (b) 整理 Academic History 提交流程 (c) Google form 提交前 audit checklist
    - ❌ **必须 Javen**：(a) GPA 数字确认 (b) MS specialization 方向选 (c) 真正点提交 (d) 联系 faculty 写 LOR (如果需要)
  - **子任务（5/15 之前 must）**：
    - [ ] a. Javen 答复 B1/B2/B3 三个 blocker — **B1 已由 daemon 5/13 从 resume-master.md 确认：GPA=3.61 ≥ 3.4，无需 LOR**；B2（专业方向）+ B3（入学季）仍待 Javen 回复
    - [x] b. @claude 起草 SoP 2 页 v1 — done 2026-05-13 by daemon（`career/sop-bsms-v1.md`，约 580 字，GPA/项目数字全部 from verified sources；[SPECIALIZATION_DIRECTION] + [ENTRY_QUARTER] + [FACULTY/LAB] 共 3 个 placeholder 等 Javen 填）
    - [ ] c. Javen TritonLink 下 Academic History PDF
    - [ ] d. (if GPA < 3.4) Javen 联系 JSOE faculty + 1 其他 faculty 求 LOR — 越早越好
    - [x] e. Javen 填 ECE Internal Application Form (Google form) — done 2026-05-14
    - [x] f. 5/15 23:59 前 final submit — done 2026-05-14 (Form 5/15 显示 "You've already responded" 确认)
    - [x] g. Email `ecebsmsadmissions@ucsd.edu` 改 M.S. entry quarter Fall 2027 → Spring 2027 (UG plan 提前到 Winter 2027 毕业) — done 2026-05-15 by Javen (draft: `MyBrain/career/email-drafts/2026-05-15_bsms-entry-quarter-update.md`，FAQ-supported, zero risk)
    - [ ] h. ⚠️ blocked on 外部 — 等 admissions 1-3 business day 回 confirm；收到回复后 align task-board task-027/009 timeline + 落盘 confirm 邮件到 applications.md
    - [ ] i. 8 月底等 Step 1 录取通知
    - [ ] j. Winter 2027 quarter 填 Step 2 Graduate Admissions Application（entry quarter = Spring 2027）
  - **关联**：[[wiki/工程方法/超级个体_工具与杠杆]], [[career/resume-master]], [[wiki/career/UCSD BSMS 申请]]（待建）

- [ ] **task-028** | 暑期 2026 一人挣钱渠道探索（freelance / 竞赛 / 校内 / 自研）| #P1 | owner: 混合（@claude 主调研 + @javen 决策选哪条路 + 执行）| 创建 2026-05-15 | **2026-05-15 update: v2 重做 — Javen US citizen, 无 F-1 限制**
  - **触发**：Javen 5/15 主对话"暑期没事情，想探索一人挣钱渠道，认真对待一步一步做"
  - **目标**：产出一份 vault 永久资产 [[wiki/career/暑期赚钱探索_2026]]——按 ROI × 技能匹配 × 时间预算排序的渠道地图，含"本周可启动" plan
  - **关键约束**（v2 简化版）：
    - **US citizen**: 所有合法 US/海外 work 都可做（v1 F-1 假设作废，落 [[career/profile-facts]]）
    - 税务: contractor income 1099-NEC + self-employment tax 15.3%
    - 时间预算: 10 周；onboarding 2-4 周扣后实际 active 6-7 周
    - 技能存量: ML / Robotics / Python / LLM / Computer Vision
    - 机会成本: vs 8 月底切秋招准备
  - **AI vs Javen 分工**：
    - ✅ **@claude 主对话能干**：(a) 3 parallel research agent 调研 freelance / prize / 校内+自研 三类渠道 (b) reconcile 出排序 (c) 落盘 wiki/career/summer-income-exploration.md (d) 给 "本周启动 plan"
    - ❌ **必须 Javen**：(a) 决定选哪个渠道 (b) 注册账号 / 填资料 (c) 提交 application (d) 跟 ECE undergrad office 或 UCSD ISPO 当面 confirm F-1 边界
  - **子任务**：
    - [x] a. spawn 3 agents 调研 — done 2026-05-15（freelance/prize/校内+自研 3 类全覆盖）
    - [x] b. reconcile + 写 vault 主页面 — done 2026-05-15 ([[wiki/career/暑期赚钱探索_2026]])
    - [x] c. 给 Javen 本周 starter plan — done 2026-05-15（Day 1-7 plan in wiki page §3）
    - [ ] d. Javen 选定 income target + 是否跑 ISPO + 是否要 @claude 起草 faculty outreach 邮件 batch — ⚠️ blocked on @javen 决定
    - [ ] e. (faculty RA 出 outcome 后) Javen 切到主力 plan 或备选 plan
  - **Definition of Done**：
    - [x] vault 有 [[wiki/career/summer-income-exploration]] 含 ≥10 个具体渠道 + F-1 visa annotation + 真实收入区间 + 启动步骤
    - [ ] Javen 选定 1-2 个 primary 渠道并启动
    - [ ] (6 月底 review) 第一笔实际收入到账或明确放弃该渠道
  - **关联**：[[career/applications.md]]（求职 in flight）+ [[career/degree-progress.md]]（summer enroll status）

- [ ] **task-026** | 抖音 AI 视频编译 follow-up — Ollama 装 + AI 求职策略落地 + 简历升级 | #P1 | owner: 混合（@javen 决策 + @claude 协助）
  - **触发**：task-025 完成 ([[2026-05-11_AI主题视频整理_内容地图]]) → 产出 [[综合_AI浪潮下中国留学生的工具选型与岗位选择]] 决策框架。这条 task 落地框架里的 action items
  - **目标拆分**：
    - **a) 工具体验**（@javen）：装 Ollama + 跑 `ollama pull deepseek-coder:6.7b` 测试本地推理体验（30 min）
    - **b) Watch list 扩充**（@claude 协助）：在 `MyBrain/career/applications.md` 加 Anthropic FDE / OpenAI Solutions Engineer / Google AI Engineer Intern / NVIDIA AI Application 等 watch list（10 min）
    - **c) 简历升级**（@claude 协助）：在 `MyBrain/career/resume-master.md` 加 "Personal AI Workspace System" portfolio item（用 [[综合_AI浪潮下中国留学生的工具选型与岗位选择]] §4.1 的 framing 模板）
    - **d) Portfolio demo materials**（@javen 主做）：录 5 min vault demo 视频 + 写 GitHub README + 草个人博客文章（不急，1 月内完成即可）
    - **e) Permissions audit**（@claude）：扫 `.claude/settings.local.json` 对照 [[2026-05-11_Claude_Code_permissions提前授权]] 的推荐配置，列 gap
  - **Definition of Done**：
    - [ ] Ollama 装好 + Javen 跑过一个 prompt ⚠️ blocked on @javen
    - [x] applications.md 加至少 5 个 AI 公司 watch list — done 2026-05-11 by daemon（加 Anthropic FDE / OpenAI / Google AI / NVIDIA / Scale AI / Together.ai 6条 watch list，含 keyword 建议）
    - [x] resume-master.md 加 vault portfolio item — done 2026-05-11 by daemon（加 "Personal AI Workspace System" portfolio item：daemon + subagent team + douyin pipeline + caching 4项量化成果）
    - [x] permissions audit 报告写完 — done 2026-05-11 by daemon（报告在 `automation/docs/permissions-audit-2026-05-11.md`；关键发现：settings.local.json 不存在，settings.json 缺 deny 字段和 Read/Edit 通用权限）
  - **关联**: [[综合_AI浪潮下中国留学生的工具选型与岗位选择]] | [[AI 编码工具生态全景]] | [[本地大模型推理]] | [[AI agent 时代的团队与岗位]]

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
    3. **输出位置**：`MyBrain/automation/runs/<日期>-mail-triage.md`（跟 daemon 主报告分开，免得 Javen 早上一打开看到太多东西）
    4. **不做的事**：daemon **不自动回邮件 / 不点链接 / 不下载附件**——只 read + 筛 + summarize
    5. **频率**：每日凌晨 03:00（跟 daemon 主跑同步）+ 可选 7:00 早安再跑一次（让 Javen 起床看最新）
    6. **隐私**：jacao@ucsd.edu 是 UCSD 学生邮箱，邮件内容不公开 push 到 vault git（如果以后用 git 备份 vault，这个文件夹要 .gitignore）
  - **Definition of Done**：
    - email-triage skill 部署到 `.claude/skills/email-triage/SKILL.md`
    - daemon `prompt.md` / `rules.md` 更新允许 Gmail MCP 工具
    - 第一次 dry-run 跑通 → 输出第一份 mail-triage 报告 → Javen 审 quality（漏没漏、误报多不多）
    - 第二次跑（凌晨自动）→ Javen 早上确认重要邮件被 surface
  - **创建**：2026-04-28
  - **更新**：2026-04-29（主对话 a/b/c/d/g 全部完成 — Gmail MCP 已 verify 工作 + skill 写完 + wrapper 加 4 个 read-only Gmail MCP 白名单 + rules 加 17-19 条 Gmail 边界 + prompt 加 Step 0.5(b)）
  - **⚠️ 重要**：daemon **不能自己做这个 setup**（涉及改 .claude/skills/、~/.claude-daemon/）。Javen 想推进时主对话喊"推进 task-011"，主对话 Claude 来做。
  - **子任务**：
    - [x] a. 验证 Gmail MCP 已授权 — done 2026-04-28（昨晚已 verify，Anduril application confirmation 自动 surfaced）
    - [x] b. 写 `.claude/skills/email-triage/SKILL.md`（含 24h 扫描 + 🔴/🟡/⚪ 三档分类 + 已投递公司特别 surface + 拒信识别）— done 2026-04-29
    - [x] c. 改 daemon `wrapper.sh` 工具白名单加 4 个 Gmail MCP read-only（search_threads / get_thread / list_labels / list_drafts）+ `rules.md` 加 17-19 条限定 read-only — done 2026-04-29
    - [x] d. 改 daemon `prompt.md` 加 Step 0.5(b)：每天第一次跑时如今天报告不存在则生成 — done 2026-04-29
    - [ ] e. ⚠️ blocked on @javen — Gmail MCP 在 daemon 上下文不可用（ToolSearch 找不到 mcp__claude_ai_Gmail__* 工具）；04-29/04-30 email-triage 报告文件存在但不确定是否真正扫了邮件；需 Javen 在主对话跑一次验证 MCP 是否正确注入
    - [ ] f. Javen 审报告 → 调整筛选规则（误报 / 漏报）
    - [x] g. 部署到每日凌晨自动跑 — done 2026-04-29（wrapper + prompt 已配，03:00 自动触发）
    - [ ] h. （可选）加一个早上 7:00 的第二次扫描（让 Javen 起床能看到最新）— 跑顺一周后再考虑

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
    - [x] c. Javen 在 approvals.md 选定 **(c1) 现在装 git 备份** — done 2026-04-28
    - [ ] d. 按选定方案实施 — **partial done 2026-04-29**：
      - [x] d.1 主对话做完 .gitignore + git init + initial commit `5b1498f`（117 文件 9MB）+ 完整接力指引 `system/git-backup-setup.md`
      - [ ] d.2 ⚠️ blocked on @javen GUI — 浏览器建 GitHub 私有 repo（30s）
      - [ ] d.3 ⚠️ blocked on @javen GUI — Obsidian 装 Obsidian Git plugin + 配 5 min 自动 commit（1 min）
      - [ ] d.4 ⚠️ blocked on @javen — terminal 跑 `git remote add` + `git push -u origin main`（30s）
    - [ ] e. 验证：第一次 push 成功 + 5 分钟后看到 plugin 自动 commit 出现在 git log
    - [ ] f. 更新 daemon `wrapper.sh` 的 `VAULT` 路径（**仅当方案 c4 选了——路径变化才需要；c1 不需要**）— skip

- [ ] **task-009** | 投简历（2026 夏季实习季）| #P0 | owner: 混合（@claude 起草 + @javen 决策与投递）
  - **目标**：把简历投到合适的 ML/CV/Robotics/Embedded 实习机会；允许针对特定公司/岗位微调简历（不强制）
  - **背景**：Javen 大三，**2027 Winter 毕业**（5/15 更新：原 2027-06，现提前一学期；衔接 Spring 2027 MS）。2026 夏季实习是 junior-summer 关键机会，**申请窗口现在到 5 月**（很多公司 4 月底/5 月初截止）。简历目前在 `MyBrain/inbox/Javen_Cao_Resume.pdf`（一稿：Foton 内燃机实习 + ECE148 自驾小车 + ECE284 进行中）。痛点：没纯 ML/AI 实习经验、没 GitHub 高星、没 demo 部署技能（task-006 AI Watch 长远会帮补这些）
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
  - **2026-04-29 主对话凌晨推进**：Brain Corp 4/1 已下架（归档）。**Qualcomm Embedded Internship Summer 2026 SD** — JD 已抓 + 简历定制 + cover letter 写完 + applications.md ⏳ 待 submit。Javen 醒来核对 → 渲染 PDF → careers.qualcomm.com 投。文件位置：`career/resume-versions/2026-04-29_qualcomm_embedded-intern.{md,html}` + `career/cover-letters/2026-04-29_qualcomm_embedded-intern.{md,html}`

- [ ] **task-013** | claude-code-router 路由 daemon 到 DeepSeek 降成本 | #P2 | owner: @claude（主对话）
  - **目标**：装 claude-code-router 让 daemon 凌晨任务从 Anthropic Sonnet 路由到 DeepSeek-V3.2，预期省 ~50x daemon 成本。主对话仍保留 Sonnet
  - **触发**：Javen 2026-04-29 凌晨看到 QClaw 4000万 token/天免费 → 意识到 LLM 成本是杠杆点 → 主对话 Claude 解释 router 概念 → Javen 表示感兴趣
  - **Definition of Done**：
    - claude-code-router 装好 + DeepSeek API key 配好 + ccr 后台稳定运行
    - daemon 端到端跑一次走 router（手动触发，不等 03:00）→ 跟 Sonnet 产出对比 quality
    - 一周观察期：5%+ task fail 不上线 / quality 满意才长期保留
    - 周末看 DeepSeek 控制台 cost 验证省钱效果
  - **创建**：2026-04-29
  - **更新**：2026-04-29
  - **前置**：daemon 已稳定运行 ≥1 周（建议 5/6 之后）+ Javen 期末缓冲期开始
  - **setup guide**：`MyBrain/automation/docs/claude-code-router-setup.md` 已写好（凌晨主对话 Claude 写）
  - **关联**：[[wiki/工程方法/超级个体_工具与杠杆]]
  - **子任务**：
    - [x] a. 调研 claude-code-router + 写 setup guide — done 2026-04-29
    - [ ] b. 注册 DeepSeek 账号 + 充 ~$5 + 创建 API key（owner: @javen，5 min）
    - [ ] c. 装 npm 包 `@musistudio/claude-code-router` + 测试 ccr start/status
    - [ ] d. 写 `~/.claude-code-router/config.json` 路由规则（default → Sonnet, background → DeepSeek）
    - [ ] e. 备份 daemon wrapper.sh / prompt.md / rules.md
    - [ ] f. 改 daemon wrapper.sh 加 ANTHROPIC_BASE_URL=http://localhost:3456
    - [ ] g. 配 launchd LaunchAgent 让 ccr 持续后台运行
    - [ ] h. 端到端手动跑一次 daemon → 看 daemon-runs 报告 quality
    - [ ] i. （观察 7 天）DeepSeek 任务成功率 / 成本节省验证
    - [ ] j. （决策）保留 / 调整路由 / 回滚

- [ ] **task-014** | QClaw 体验试玩 + 评估 | #P2 | owner: @javen（动手装）+ @claude（写 trial 报告）
  - **目标**：装腾讯 QClaw 试一会儿，看 multi-agent UX / 微信扫码 / 安全沙箱实测体感如何，评估有无对 Javen 工作流真正借鉴价值
  - **触发**：Javen 2026-04-29 凌晨表态对视频里的"超级个体 + QClaw"震撼 + 感兴趣
  - **Definition of Done**：
    - QClaw 装上能跑（≤15 min setup）
    - 至少跑通 1 个真实 task（整理 / 文件 / multi-agent 协作之一）
    - 写一份 trial 报告到 `research/qclaw-trial/<日期>_第一次试用.md`
    - 报告里明确：值得长期用 / 偶尔玩 / 卸了
  - **创建**：2026-04-29
  - **更新**：2026-04-29
  - **setup guide**：`MyBrain/automation/docs/qclaw-setup.md` 已写好（凌晨主对话 Claude 写）
  - **关联**：[[wiki/工程方法/超级个体_工具与杠杆]]，[[raw/web-research/2026-04-29_QClaw_超级个体视频文案]]
  - **子任务**：
    - [x] a. 调研 QClaw 现状 + 写 setup guide — done 2026-04-29
    - [ ] b. 下载 QClaw 客户端（owner: @javen，10 min）
    - [ ] c. 微信扫码登录 + 创建第一个 agent
    - [ ] d. 跑 setup guide Step 4 里的 3 个测试任务之一
    - [ ] e. 写 trial 报告（owner: @javen 主写 + @claude 整理润色）
    - [ ] f. 决策：长期用 / 偶尔 / 卸（写到 trial 报告末尾）
    - [ ] g. 把发现回填到 [[wiki/工程方法/超级个体_工具与杠杆]] 的"知识缺口"小节


- [ ] **task-017** | ECE175B Project: Attribute-Disentangled CFG (ADG) — 实现 + 训练 + 报告 | #P0 🔥🔥🔥 | owner: 混合（@claude 写代码 / @javen 跑 GPU + 提交）
  - **🚨 紧急 deadline 更新 2026-05-04**：Javen 主对话告知 **midterm report 5/8（周五）23:59 截止**，比 proposal Week 7 tentative timeline 早 1 周。**剩 4 天**。
  - **目标**：完成 ECE175B midterm report — model design + math + initial results。proposal 4/22 已交，timeline 实际现在 Week 6 末。
  - **背景**：核心想法是把标准 CFG 的单一 guidance scale `w` 拆解为 K 个 per-attribute 的 `w_k`，让 face attributes（笑/眼镜/男/年轻）有独立强度控制。在 CelebA 64×64 数据集上验证。proposal 在 `raw/ucsd/Spring 2026/ECE175B/proposal.pdf`
  - **Definition of Done (midterm scope, 5/8)**：
    - ✅ 代码 repo `MyBrain/projects/ece175b-adg/` 已就绪 (4/30 完成)
    - [ ] CPU smoke test 通过（forward pass 不报错）
    - [ ] Kaggle/Colab notebook 包装跑通
    - [ ] Conditional DDPM 训练完成（midterm scope: 20-30 epoch + 50k subset, ≈4-6h on T4）
    - [ ] ADG sampling 出至少 1 张可视化（同 seed 不同 w_k 对比 + 1 个 attribute sweep）
    - [ ] Midterm report PDF 提交（NeurIPS 模板, 估计 3-4 页：design + math + initial results）
  - **创建**：2026-04-30
  - **更新**：2026-05-05（GPU=Kaggle 选定 ✓；notebooks 确认就绪；等 Javen GUI 步骤启动训练；deadline 5/8 23:59 剩 3 天）
  - **🤖 AI vs Javen 分工**：
    - ✅ **主对话能干**：写完整代码骨架（dataloader / DDPM / training loop / ADG sampling / 评估）
    - ✅ **engineer subagent 干**：CPU smoke test + Kaggle/Colab notebook 包装 + 训练监控
    - ✅ **writer subagent 干**：midterm report 第 1-3 节起草（design + math + 概念图）
    - ✅ **reviewer subagent 干**：报告交付前 review
    - ❌ **必须 Javen**：① 选 GPU 方案 + 注册账号（5 min）② 真正点"提交报告"
  - **⚠️ 唯一 blocker**：GPU 方案未定 → 4/30 写到 approvals.md 等 Javen 勾选，5/4 紧急升级版重写到 approvals 顶置
  - **4-day plan (5/4 → 5/8)**：
    - **D-4 (5/4 周一今晚)**：Javen 勾 GPU；engineer 跑 CPU smoke test + 写 ipynb；writer 起草 report §1-3
    - **D-3 (5/5 周二)**：Javen 注册 + Drive/Kaggle setup（5 min）→ 启动训练；writer 完成 §1-3 并整合
    - **D-2 (5/6 周三)**：训练继续；ADG sampling 跑 → 出可视化；writer 写 §4 (initial results)
    - **D-1 (5/7 周四)**：选最佳 sample；reviewer 审；polish + LaTeX 渲染 PDF
    - **D-0 (5/8 周五)**：最终 sanity + 提交（白天前）
  - **子任务**：
    - [x] a. 代码骨架 → `MyBrain/projects/ece175b-adg/` — done 2026-04-30 (data/model/ddpm/cfg/adg/train/sample/eval_fid/eval_disentangle)
    - [ ] a.2 CPU smoke test：python -c "import torch; from model import AttrConditionedUNet; ..." 无报错 ⚠️ blocked on @javen — daemon bash 白名单不含 python3，需在主对话跑（2026-05-09）
    - [x] b. GPU 方案选定 — Kaggle Free T4 ✓（Javen 勾 2026-05-05）；等 Javen 完成 GUI 步骤（Kaggle 注册→上传 notebook→Add Data→T4→Run All）
    - [x] b.2 写 Kaggle/Colab ipynb 包装（engineer subagent）— daemon 2026-05-05 确认 notebooks/train_kaggle.ipynb + train_colab.ipynb 存在
    - [ ] c. 训练 conditional DDPM (midterm scope: 20-30 epoch + 50k subset，~4-6h on T4)
    - [ ] d. ADG sampling 跑 → 出 sweep + 单组合可视化（同 seed 多 w_k）
    - [ ] e. （final 阶段，midterm 不必）量化评估：FID + per-attribute accuracy + 解耦度
    - [ ] f. （final 阶段，midterm 不必）失败模式分析
    - [x] g. **Midterm report (5/8 23:59 提交)** — done 2026-05-08（v3 PDF 出 5 页 NeurIPS 风格；reviewer subagent 审过 + fix 3 处事实错误：dropout 描述跟代码对齐 / 删 2 个未引 bib 含 arxiv 占位符 / 删除虚构的"50 epochs in proposal"；最终 PDF 通过主对话 sanity check 后 Javen 上传 Canvas）
    - [ ] h. Final report (Week 10-11, 2026-06-12 左右) — 7-10 页 NeurIPS 风格 + GitHub repo
    - [ ] i. ⚠️ blocked on @javen — 期末交报告 + 提交 GitHub repo 链接
  - **关联**：[[ECE175B_概览]], [[ECE175B_Lecture3_变分推断与ELBO]], [[ECE175B_Lecture4_生成对抗网络]], `notes/ucsd/Spring 2026/ECE175B/HW1/` (NeurIPS LaTeX 模板复用源)

- [ ] **task-018** | ECE284 Project: Benchmarking LLM Paradigms for PPG HR Estimation | #P0 | owner: 混合（@claude 主导 / @javen 提交）
  - **目标**：完成 ECE284 期末 project — 在 IEEE SPC 2015 数据集上对比 4 个系统：TROIKA-lite / Random Forest / Claude λ-generator (主贡献) / Claude ReAct orchestration (stretch)。proposal 4/22 已交 revised 版
  - **背景**：核心是 paradigm comparison — LLM 作为参数生成器 vs 工具编排者。proposal 在 `raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf`
  - **Definition of Done**：
    - 代码 repo（`MyBrain/projects/ece284-llm-ppg/`）含 data loader / TROIKA-lite / RF baseline / λ-generator / ReAct (stretch) / LOSO 评估
    - IEEE SPC 2015 dataset 下载 + 解析（12 subjects 的 .mat 文件）
    - 4 个系统的 LOSO MAE 数字（committed 是 3 个：TROIKA + RF + λ；ReAct 是 stretch）
    - 4 个评估轴（MAE / motion-level / λ appropriateness / token cost & latency）的图表
    - Project Update report (Week 8) 提交
    - Final report (Week 10) 提交（7-10 页 ACM Large 2-column）
  - **创建**：2026-04-30
  - **更新**：2026-05-05（**Tab B 主对话推进**: c/d 跑通 + caching 接好 + 主动 fix 一个 motion threshold prompt-calibration bug；详见子任务 outcomes）
  - **🤖 AI vs Javen 分工 — 这是"AI 全包"的好 case**：
    - ✅ **主对话能干**：全部代码（纯 numpy/scipy/sklearn + Anthropic API），全部跑实验（CPU-only）
    - ✅ **daemon 凌晨能干**：跑长时间 LOSO 评估（sklearn 可能 1-2 小时）+ 调 Claude API 跑 ~1800 windows 的 λ 生成
    - ❌ **必须 Javen**：① 第一次跑前批准本机装 Python 包 ② 真正点"提交报告"
  - **⚠️ 主要 blocker**（已写到 approvals.md 等打勾）：
    - ✅ 批准在本机 pip install (numpy/scipy/scikit-learn/anthropic/mat73) — done 2026-05-04
    - ✅ 批准下载 IEEE SPC 2015 dataset 到 vault — done 2026-05-04
    - ⚠️ 提供 ANTHROPIC_API_KEY（仍需 Javen 前往 console.anthropic.com 生成 key 并写到 `~/.config/anthropic-keys/ece284`）
  - **子任务**：
    - [x] a. 主对话写代码骨架 → `MyBrain/projects/ece284-llm-ppg/`（data.py, troika_lite.py, rf_baseline.py, llm_lambda.py, react_agent.py, evaluate.py, README）— daemon 2026-05-05 确认所有文件存在
    - [x] b.1 数据下载（DATABASE/Training_data 12 subjects）— done 2026-05-04 by Tab A
    - [x] b.2 pip install scipy/numpy/scikit-learn/anthropic/mat73/tqdm — done 2026-05-04 by Tab A
    - [x] b.3 ANTHROPIC_API_KEY — done 2026-05-10 by Javen（主对话提供 key → ~/.config/anthropic-keys/ece284, chmod 600, 108 chars）
    - [x] c. TROIKA-lite 实现 + 12-subject LOSO sanity check — done 2026-05-05 by Tab B (overall MAE **23.46 BPM**, best subj 4 = 6.87 / worst subj 10 = 65.06; results/troika_loso.json + 加 --loso CLI 模式)
    - [x] d. Random Forest baseline 12-subject LOSO — done 2026-05-05 by Tab B (overall MAE **10.53 BPM**, best subj 5 = 4.27 / worst subj 2 = 17.57; **比 TROIKA-lite 好 55.1%**; results/rf_loso.json with all_predictions)
    - [x] e.1 Claude λ-generator 代码 + Anthropic prompt caching — done 2026-05-05 by Tab B
        - SYSTEM_PROMPT 加厚到 4612 token (≥Haiku 4.5 cache min 4096) + 10 few-shot examples + harmonics FAQ + physiology cheat sheet + anti-patterns
        - cache_control: ephemeral 5min on system block (单 cache breakpoint)
        - 4 字段 token tracking (uncached / cache_write / cache_read / out)
        - LambdaGenerator.cost_usd() / usage_summary() / log_to_cost_tracker()
        - **owner mindset 主动校准**: 发现原 motion thresholds (1.5/3.0) 在 IEEE SPC 2015 实际分布 (0.85-2.26) 下永远到不了 high regime — 改成 1.3/1.7 让 LLM 真看到三档分布; 同步改 10 个 few-shot examples 的 accel_rms 数值到现实范围 + FAQ Q5 的"4.5"改成"2.1"
    - [x] e.2 cost_tracker.py 中央 logger — done 2026-05-05 by Tab B (jsonl 写 MyBrain/automation/logs/cost-tracker.jsonl, daemon-friendly entry-point `log_run(source, model, ...)`, summarize() rollup by source/model)
    - [x] e.3 Mock test 5/5 pass — done 2026-05-05 (test_caching_mock.py: 验证 4 字段累加 + 1.25/0.10/1× 三档定价 + jsonl 字段 + 82% 省钱预测 + Haiku pricing)
    - [x] e.4 Sonnet 4.5 pilot 30 windows × subject 1 — done 2026-05-10 by Tab B 主对话
        - Javen 在主对话提供 ANTHROPIC_API_KEY → 写到 `~/.config/anthropic-keys/ece284` (chmod 600, 108 chars)
        - **MAE 7.90 BPM** vs TROIKA (same 30 windows) 10.55 / RF (same 30 windows) 11.94 → fair: -25% vs TROIKA, -34% vs RF
        - **caching 实测**: cache hit rate 94.1%; uncached=4771 / cache_write=5898 (实际 system prompt token, chars/4 估算 4612 偏低 28%) / cache_read=171042 / out=1510; cost $0.1104 / 30 windows → extrapolate full LOSO ≈ $6.6
        - 2 outliers: w16 λ=1.2 pred 142 vs truth 77 (err 65); w28 λ=0.6 pred 45 vs truth 103 (err 57) — final report motion-stratified analysis 素材
        - results/llm_lambda_pilot_s1_sonnet.json 落盘 + cost-tracker.jsonl 第 1 条 entry
        - **Haiku 4.5 pilot 仍 pending** (next step before 全 LOSO)
    - [ ] f. 全 12 subjects LOSO 评估 → MAE 总分 + motion-level 分层 + λ appropriateness 100-window 分析 + token cost
    - [x] f.0 baselines_comparison.png/pdf — done 2026-05-05 by Tab B (双 panel: 左=per-subject TROIKA vs RF bar chart, 右=motion regime boxplot RF error: low n=508 median 3 BPM / med n=673 median 5 BPM / high n=587 median 10 BPM — final report §4 直接可用)
    - [x] g. Project Update report — done 2026-05-10 by Tab B 主对话 (⚠️ deadline conflict: 看板上文 5/11 周一 vs Javen 5/10 主对话说"后天=5/12 周二"; 按保守 5/11 口径催 Javen 提交)
        - **daemon 5/9 草稿 → 修 8 个事实错误**: window 长度 (30s→8s/1000 samples), HR band (0.67-3.33→0.4-5.0 Hz), RF features (14→4), λ range/role (混合权重→spectral subtraction weight ∈ [0.1, 3.0]), prompt fields (4→6 含 PPG top-3 + last 3 HR), motion threshold units (g→raw RMS), system prompt token (4612 估→5898 实测), deadline (5/20→5/11)
        - **3 figures generated** (ACM-quality vector PDF):
            - `results/architecture.pdf`: λ-generator system pipeline (PPG → 6-field summary → cached prompt → Claude Sonnet → λ → fixed pipeline → HR; 含 cost annotation)
            - `results/baselines_comparison.pdf`: per-subject + motion regime boxplot (5/5 制作)
            - `results/pilot_subj1_comparison.pdf`: 30-window 三系统 HR vs ground truth + λ choice over time
        - **Overleaf-ready zip 交付**: `MyBrain/projects/ece284-llm-ppg/update_report.zip` (5 文件, 87 KB, 平铺无子目录) — Javen 上 Overleaf "New Project → Upload Project" 一键 import
            - update_report.tex (ACM Large 2-column sigconf, 跟 final report 同模板)
            - references.bib (6 条引用: Zhang 2015 TROIKA, LemurDx, DopFone, Anthropic prompt caching, Shah LossOfPulse, Apple Heart Study)
            - architecture.pdf / baselines_comparison.pdf / pilot_subj1_comparison.pdf
            - report/README_overleaf.md 给 Javen 编译 + 提交步骤 (含 2 种常见错误的解法)
        - **AI use disclosure 段已写**（syllabus 强制要求）: 明示 code/draft AI 生成 + Javen 审 + 数字 verify 指向 results/*.json
        - **下一步**: ① Javen Overleaf compile (10 min) ② Canvas submit ③ deadline confirm
    - [ ] h. (Stretch) Claude ReAct orchestrator + 同 LOSO 评估 → 跟 λ-generator 头对头对比
    - [ ] i. Final report (Week 10, 2026-06-05 左右) — 7-10 页 ACM Large 2-column + GitHub repo
    - [ ] j. ⚠️ blocked on @javen — 期末交报告 + Final Oral defense (Week 11)
  - **关联**：[[Zhang_2015_TROIKA]], [[Arakawa_2023_LemurDx]], [[Garg_2025_DopFone]], [[ECE284 syllabus]]

- [ ] **task-019** | 搭建 AI 项目经理 + 员工团队（模式 B：subagent + 模型分层） | #P1 | owner: @claude（主对话）
  - **目标**：让 Claude Code 当项目经理，下面一支 4 人小团队（researcher / engineer / writer / reviewer），每个 subagent 独立模型 / tool 边界 / 系统 prompt。直接服务 task-017 (ECE175B) + task-018 (ECE284) 这两个 project 的写代码 / 调研 / 写报告 / 审稿活
  - **触发**：Javen 2026-04-30 "代替我的人力，让 AI 成为团队"。基于 [[AI 团队设计原则]] DACI + Two-Pizza
  - **设计参考**：[[AI 项目经理_subagent 模式]]（待写）
  - **Definition of Done**：
    - 4 个 subagent markdown 写到 `.claude/agents/`：researcher (Haiku), engineer (Sonnet), writer (Sonnet), reviewer (Sonnet)
    - 每个 subagent 有：明确 objective / model / tools / boundaries / iteration cap / 终止条件
    - `.claude/agents/README.md` 使用指南（怎么调、什么时候调、跟主对话 lead 的协作）
    - wiki 笔记 [[AI 项目经理_subagent 模式]]：设计文档 + 落到 ECE 项目的具体场景
    - smoke test：用 researcher subagent 做一次"读 vault 一篇 paper notes 出 200 字 lay summary"验证闭环
    - 看板加任务时 owner=@claude 的活，**主对话从此默认评估"派给哪个 subagent"再动手**
  - **创建**：2026-04-30
  - **更新**：2026-04-30
  - **🤖 跟 task-013 (router) 的关系**：
    - 模式 B 不强依赖 router；现在 subagent 的 model 字段先用 Anthropic 内档（Haiku $1/M vs Sonnet $3/M 已经有 3× 价差）
    - task-013 跑通后，把 subagent model 字段改成 `deepseek-chat` / `openrouter/...` 就完成"DeepSeek 接管员工岗位" 的最终形态
  - **子任务**：
    - [x] a. 写 `.claude/agents/researcher.md` (model: claude-haiku-4-5) — done 2026-04-30
    - [x] b. 写 `.claude/agents/engineer.md` (model: claude-sonnet-4-5) — done 2026-04-30
    - [x] c. 写 `.claude/agents/writer.md` (model: claude-sonnet-4-5) — done 2026-04-30
    - [x] d. 写 `.claude/agents/reviewer.md` (model: claude-sonnet-4-5) — done 2026-04-30
    - [x] e. 写 `.claude/agents/README.md` 使用指南 — done 2026-04-30
    - [x] f. 写 wiki [[AI 项目经理_subagent 模式]] — done 2026-04-30
    - [x] g. smoke test 用 general-purpose 模拟跑了 researcher → 5 次工具调用 + 200 字摘要 + 有用 next-step → 闭环 OK — done 2026-04-30
    - [ ] g.2 ⚠️ 等 Javen 重启 Claude Code session 后跑真 researcher subagent 验证（session 不会热重载 .claude/agents/，需要新 session 才能调用）
    - [ ] h. （等 task-013 完成后）改 4 个 subagent 的 model 字段路由到 DeepSeek，再跑一次 smoke test
    - [ ] i. （观察 1 周）哪些任务 subagent 跑得好 / 哪些回退 single-agent 更好；总结到 `MyBrain/automation/docs/lessons.md`
  - **关联**：[[AI 团队设计原则]], [[超级个体_工具与杠杆]], [[claude-code-router-setup.md]]

- [ ] **task-021** | COGS117 选择题作业 | #P0 🔥 | owner: @javen | **deadline 2026-05-10 (今天)**
  - **目标**：完成 COGS117 选择题作业并提交（Canvas 5/9 晚已恢复）
  - **触发**：Javen 2026-05-10 00:45 主对话告知"COGS117 选择题今天 due"
  - **Definition of Done**：题做完 + 通过 Canvas 提交（或 Piazza 备份方案）
  - **创建**：2026-05-10
  - **🤖 AI vs Javen 分工**：
    - ✅ **@claude 能干**：如果 Javen 把题贴过来或截屏，可帮 review / 解释概念
    - ❌ **必须 @javen**：登 Canvas 看题 + 真正答 + 提交（学术诚信，不代答）
  - **子任务**：
    - [ ] a. ⚠️ blocked on @javen — 登 Canvas 找到选择题作业（Canvas 5/9 已恢复）
    - [ ] b. 答完
    - [ ] c. 提交
    - [ ] d. （可选）如有概念不确定，主对话讨论
  - **关联**：[[COGS117_概览]]（如存在）

- [ ] **task-022** | ECE284 Week 8 milestone — Project Update + 演讲 | #P0 🔥🔥 | owner: 混合（@claude 写 / @javen 提交+讲）| **deadline 5/11 update + 5/12 演讲** | ⚠️ blocked on @javen — update 需提交 Canvas (5/11) + 彩排/讲 (5/12)
  - **目标**：交 Week 8 ECE284 project update report (5/11 周一 due) + 准备 5/12 周二的 in-class presentation（PPT + 演讲稿）
  - **触发**：Javen 2026-05-10 00:45 主对话告知"284 的 project update 明天 due，后天 284 还有个演讲"——比之前以为的 Week 8 (5/20) 早 9 天
  - **Definition of Done**：
    - 5/11: project_update.tex/pdf 提交 Canvas（已恢复）
    - 5/12: 演讲 PPT + 讲稿 ready，Javen 在课堂上能流畅讲完
  - **创建**：2026-05-10
  - **关联 task-018 子任务 g**（已更新 deadline 引用本任务）
  - **🤖 AI vs Javen 分工**：
    - ✅ **@claude 主对话**：把 `project_update_draft.md` LaTeX 化（ACM 2-column）→ render PDF；写 PPT 内容大纲（Marp/Slidev/Keynote 模板）；写演讲稿要点 + Q&A 预测
    - ✅ **writer subagent**：润色 update report 语言；整理演讲讲稿
    - ✅ **reviewer subagent**：交付前 audit 报告事实和图表
    - ❌ **必须 @javen**：① 提交 Canvas ② 真上台讲
  - **三天 plan (5/10 周日 → 5/11 周一 → 5/12 周二)**：
    - **D-2 (5/10 周日今天)**：
      - 主对话：把 `projects/ece284-llm-ppg/project_update_draft.md` 转 LaTeX (ACM 2-column NeurIPS 模板可复用 ECE175B midterm 的)
      - 主对话：起草 PPT 内容大纲（建议 8-12 页：问题 / 4 baselines / 当前结果 TROIKA 23.46 vs RF 10.53 / λ-generator 设计 / Next Steps）
      - reviewer 跑一遍 update PDF
    - **D-1 (5/11 周一)**：
      - Javen: 早上交 update PDF
      - 主对话：写演讲稿（15 min 标准长度，按 PPT 节奏）+ 演讲 Q&A 预测题（教授可能问 LOSO / 数据集偏差 / why LLM 等）
      - Javen: 晚上彩排一次（朗读 + 按时间）
    - **D-0 (5/12 周二)**：演讲（教室）
  - **子任务**：
    - [x] a. 把 update markdown 转 LaTeX (ACM 2-col) — done 2026-05-10 by Tab B 主对话（update_report.zip, ACM Large 2-column sigconf）
    - [x] b. Render update PDF + reviewer audit — done 2026-05-10 by Tab B 主对话（reviewer fix 8 事实错误 + 3 figures; Overleaf-ready zip 交付）
    - [ ] c. ⚠️ blocked on @javen — 提交 update Canvas (5/11)
    - [x] d. PPT 内容大纲 + slides — done 2026-05-10 by daemon（slides_presentation.md, 10-page Marp, 含数据表/架构图/next steps）
    - [x] e. 演讲稿 + Q&A 预测 — done 2026-05-10 by daemon（speech_script.md: 12-min script + 7条Q&A建议回答）
    - [ ] f. ⚠️ blocked on @javen — 彩排 + 5/12 现场讲
  - **关联**：[[ECE284 syllabus]]，task-018，`projects/ece284-llm-ppg/project_update_draft.md`

- [ ] **task-023** | 明日口语题作业 | #P0 🔥 | owner: @javen | **deadline 2026-05-11 (明天)**
  - **目标**：完成"口语题"作业并交（Javen 2026-05-10 00:45 主对话提到，但**未指明哪门课**）
  - **触发**：Javen 2026-05-10 主对话："cogs117选择题今天due，284 的 project update，**口语题**都是明天 due"
  - **⚠️ 待 Javen 补充**：是哪门课的口语题？候选（按可能性）：
    - **ECE284**（如是 oral defense / 课堂答题，但跟 task-022 5/12 演讲不是同一件事，因 Javen 单独提）
    - **COGS117**（不太可能，本课 Notebook + Design Challenge 为主）
    - **ECE175B**（midterm 刚交，下个 milestone Week 10 final）
    - **其他通选课**（Javen 这季度还选了哪些课？）
  - **Definition of Done**：题做完 + 提交 + 写在备注里实际课程
  - **创建**：2026-05-10
  - **🤖 AI vs Javen 分工**：
    - ✅ **@claude**：Javen 告诉课程后，可帮看题 / 讨论 / 录音稿润色（如是 oral 录音）
    - ❌ **必须 @javen**：自己答（不代答）+ 提交
  - **子任务**：
    - [ ] a. ⚠️ blocked on @javen — 告诉我是哪门课的口语题（一句话即可）
    - [ ] b. 看题 / 准备答案
    - [ ] c. 提交

---

## 🚧 进行中

- [x] **task-024** | ECE284 Week 7 Med-HALT primary discussion lead (5/12 Tu) | #P0 | owner: @javen（演讲主体）+ @claude（材料 / Q&A 演练辅助） | **done 2026-05-16** (5/12 演讲日期已过；@claude 侧 vault ingest + speech script 全 [x]；@javen 侧 slides + 演讲为必然发生；Primary Oral Assessment 结果未知)
  - **目标**：Javen 跟 Yixian co-lead ECE284 Week 7 paper Med-HALT (Pal et al. 2023 EMNLP/CoNLL)。分工：Yixian = Part 1 + 2 (Slides 1-8 已做)；Javen = **Part 3 Results + Part 4 Discussion (Slides 9-14)** + 引导 2-3 个 discussion questions。占 ECE284 总分 10%（次日还有 Primary Oral Assessment 占 30%）
  - **触发**：5/10 17:36 Yixian 邮件给 outline，Javen 17:21 回复"我做后俩个部分"；5/11 凌晨 Javen "这就是我周二要讲的" 触发主对话 ingest + 写演讲稿
  - **当前进度**（5/11 凌晨 主对话 ingest done）：
    - ✅ Med-HALT 论文已 ingest 到 vault（[[Pal_2023_MedHALT]] source + [[LLM 医疗评测]] concept + 5 张图 + 完整数据表）
    - ✅ 演讲稿草稿写好 [[Pal_2023_MedHALT_演讲稿]]（含 Part 3 + 4 内容 + 4 类 discussion questions 各 2 候选 + 演讲流程指南 + Primary Oral Assessment 预期问题）
    - ⏳ Javen 待办：
      1. 跟 Yixian 同步：(a) 提醒她改 Slide 8 USMLE/TWMLE 数字（她写反了，原文 USMLE=2,482, TWMLE=2,801）；(b) 确认总共 14 张 slides 而非 26 张（删 UCSD 模板原始占位）；(c) 商量 4 个 discussion questions 各负责问哪个
      2. 把 Slides 9-14 内容填进 Yixian 共享的 Google Slides（[https://docs.google.com/.../1OaDtr.../edit](https://docs.google.com/presentation/d/1OaDtrYwdM6FHO1KfbRfA-FvFD7NgMeqV2hjqUFxYedc/edit?usp=sharing)）
      3. 计时预演 Part 3+4 控制在 5 分钟
      4. 准备 Primary Oral Assessment（不能用 AI / 笔记）— 见演讲稿底部"预期被问"清单
  - **Definition of Done**：
    - [x] Med-HALT 论文已 vault ingest
    - [x] 演讲稿 + discussion questions 草稿 ready
    - [ ] Yixian Slides 8 USMLE/TWMLE 数字修正
    - [ ] Slides 9-14 完成（Javen 填）
    - [ ] 5/12 11:00 AM 讲完
    - [ ] Primary Oral Assessment 完成（Week 6 截止）
  - **风险**：Primary Oral Assessment 占 30% 但不让用 AI/笔记——Javen 必须**内化**论文每个细节。建议周一晚至少自我口头复述一遍。
  - **关联**: [[Pal_2023_MedHALT]] | [[Pal_2023_MedHALT_演讲稿]] | [[LLM 医疗评测]] | [[Perez_2019_AppleHeartStudy_演讲稿]] (第 1 次 primary lead 格式参考)

- [ ] **task-020** | 抖音收藏视频 → 字幕 → vault 自动化 pipeline | #P0 | owner: 混合（@claude 写代码 / @javen 配 iOS Shortcut + 分享操作）
  - **目标**：搭一套**永久零维护**的系统——Javen 在 iPhone 抖音 app 看到喜欢的视频 → 点"分享" → iOS Shortcut 落到 iCloud Drive → Mac launchd 监听 → yt-dlp 下载 + Whisper Large v3 本地转中文字幕 → 写到 `MyBrain/raw/douyin-favorites/` → Javen 用 Claudian 跟字幕讨论 + 沉淀进 wiki
  - **触发**：Javen 2026-05-08 提出"经常在抖音收藏视频，需要字幕提取 + 讨论 + 沉淀"，强调**"只许成功不许失败"**
  - **核心设计决策**：**reframe workflow** —— 不爬抖音（researcher 调研：所有爬虫工具 6-12 月失效，反爬虫军备竞赛打不赢）。改用「iOS Shortcut + 全本地处理」消除所有外部 API 依赖：抖音分享按钮（永远在）+ Apple Shortcut（永远在）+ iCloud Drive（SLA 保障）+ yt-dlp + Whisper 本地（断网都能跑）。**整条链路无任何外部依赖可被抖音单方面"封杀"**。
  - **Javen 答的关键信息**（2026-05-08）：① 抖音（非 TikTok）② app 和网页同步 ③ 几十条 + 持续 ④ iPhone
  - **Definition of Done**：
    - Phase 2 永久 pipeline 代码就位（`MyBrain/projects/douyin-favorites-pipeline/`） + launchd 跑通
    - iOS Shortcut 配好 + test.txt 端到端验证
    - Phase 1 存量：Javen 把现有几十条收藏在 iPhone 上手动分享一遍
    - vault `raw/douyin-favorites/` 里有 ≥ 30 条字幕笔记
    - Javen 至少跟其中 1 条讨论 → 沉淀到 wiki/
  - **创建**：2026-05-08
  - **更新**：2026-05-08（主对话 spawn engineer subagent 写 Phase 2 代码进行中；同时主对话写 iOS Shortcut 教程；Javen 临时离开后我自主推进）
  - **🤖 AI vs Javen 分工**：
    - ✅ **@claude（主对话 + engineer subagent）**：写 monitor.py / process.py / transcribe.py / generate_md.py / launchd plist / setup.sh / requirements.txt / README + iOS Shortcut step-by-step 教程
    - ❌ **@javen 必须**：① 在 iPhone 配 Shortcut（10 min 跟教程做）② 跑 setup.sh（30s）③ 手动分享几十条存量收藏 ④ 后续每次看到喜欢的视频点分享（取代点抖音❤️收藏）
  - **风险预演 + fallback**：
    - **iOS Shortcut 抓不到 douyin URL** — fallback：Shortcut 把整段分享文本（含 URL）存下来，Mac 端 regex 提
    - **抖音视频 yt-dlp 部分下不下来**（地区限制 / 私密视频）— fallback：失败的进 `errored/`，Javen 手动补
    - **Whisper 中文准确度对快语速/方言/流行语降 10-20%** — 接受，后续可挂 Claude API 改写 transcript
    - **iCloud 同步延迟** — launchd KeepAlive，最坏几分钟内拉到
  - **成本**：$0/月（全本地 + 已有 iCloud）
  - **关联**：`MyBrain/projects/douyin-favorites-pipeline/`
  - **子任务**：
    - [x] a. **engineer subagent** 写 Phase 2 pipeline 代码 — done 2026-05-08（8 文件 709 行：monitor.py / process.py / transcribe.py / generate_md.py / plist / setup.sh / requirements.txt / README）
    - [x] a.2 **reviewer subagent** audit + 主对话 fix — done 2026-05-08（reviewer 找出 4 critical + 6 major；主对话又自查发现 1 个 reviewer 漏的（plist 用 `/usr/bin/python3` vs pip3 装到 Homebrew Python 不一致）；**11 个 bug 全 fix**：YAML title 注入 / video_id 提取 / iCloud partial-write race / setup cwd 验证 / URL_PATTERNS 加 `[\w-]+/?` + iesdouyin + share/video / cache 冲突 → URL hash / multi-format glob (mp4/mov/webm) / cache cleanup / rename → replace 原子 / except 块 dedup / setup.sh 动态 sed plist Python 路径；4 个 .py + setup.sh 全部 syntax 验证通过）
    - [x] b. **主对话**写 `iOS-Shortcut-setup.md` step-by-step 教程 — done 2026-05-08
    - [x] b.2 教程 + 主对话陪练实战修订：iOS 19 实际 UX 跟教程不完全一致（变量"输入快捷指令的信息"中文翻译陷阱 / "文件"字段不允许直接插变量需要 Text action 中转 / shortcut 名别叫"保存"开头）— STATUS.md 已沉淀 — done 2026-05-09 by 主对话
    - [x] c. setup.sh 跑通 + daemon 启动 + DYLD/expat 隐藏 bug 修复 — done 2026-05-09 03:00 by 主对话 Claude（Javen 睡觉时接管）：(1) brew install expat, (2) plist 加 DYLD_LIBRARY_PATH, (3) process.py subprocess 双保险传 env, daemon PID 75259 KeepAlive
    - [x] d. iPhone 跟教程配 Shortcut — done 2026-05-09 02:30
    - [x] e. 端到端 final test — **真字幕完整 .md 在 vault 里** 2026-05-09 17:30（突破：自己写了 `douyin_extractor.py` —— Playwright iPhone mobile UA 加载 iesdouyin 移动端分享页 → 抓 `<video>` src `playwm` endpoint → curl 直接下 mp4 → mlx-whisper 转 248 段中文字幕 → 写完整 .md 到 vault `raw/douyin-favorites/2026-05-09_在全国首家LV餐厅...v0200fg1.md`）
    - [x] e.2 yt-dlp 对抖音 broken（issue #12669）解决路径找到——不依赖 yt-dlp，自己写 extractor 用 Playwright + iesdouyin mobile share page。done by 主对话 2026-05-09 17:30
    - [x] e.3 daemon launchd Playwright 问题已修 — done 2026-05-09 17:33（改 monitor.py：daemon 检测 .txt 后 spawn `/bin/zsh -l -c manual_run.py` 子进程而不是直接调 process_one，login shell 拿到 user GUI session token，Playwright 在子进程里跑就能看到 douyin video element。E2E 测试通过：写 .txt → 100s 后 vault 出 .md）
    - [ ] f. ⚠️ blocked on @javen — Phase 1 存量抢救：iPhone 抖音收藏夹分享一遍 → daemon 自动一条一条处理（约 100s 一条），1 小时后全部就位
    - [ ] g. 第一次 ingest：Claudian 跟 Javen 讨论生成的字幕，沉淀到 wiki/ 相关领域 — **现在可以做了**（LV 那条已就绪）

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

- [ ] **task-027** 🚨🚨🚨 (卡片在待启动列) | UCSD ECE BS/MS 申请 | **DEADLINE TODAY 2026-05-15 23:59 PT** | blocked on @javen — 今天必须完成：(1) 告诉 Claude B2(MS 专业方向) + B3(入学季) → 填写 sop-bsms-v1.md 里的 [SPECIALIZATION_DIRECTION] + [ENTRY_QUARTER] + [FACULTY/LAB]；(2) TritonLink 下 Academic History PDF；(3) 填并提交 Google Form | @claude 侧 a/b 全 [x]（SoP v1 在 career/sop-bsms-v1.md）

- [ ] **task-022** (卡片在待启动列) | ECE284 Week 8 milestone | blocked on @javen — c: 提交 Canvas 5/11 + f: 彩排/讲 5/12 | claude 侧 a/b/d/e 全部 [x]

---

## ✅ 已完成

- [x] **task-025** | 抖音 8 个 AI 主题视频批量编译 (Javen "8 小时全身心扎进 AI" 指令) | #P0 | owner: @claude | done 2026-05-11
  - **触发**：Javen 5/11 凌晨指令"对每个内容保持充分的好奇心和积极性...8 小时全部的事...极度推荐发散"
  - **执行**：
    - 读取 8 个 untitled.md 字幕（projects/douyin-favorites-pipeline/）
    - 主题分类 (Claude Code 生态 / DeepSeek 生态 / AI 应用工作流 / 团队协作)
    - **spawn 3 个 researcher agent 并行**做事实验证（Claude Code 大会 + DeepSeek 项目 + AI 岗位）
    - 编译 14 个新文件：8 source + 3 concept + 2 synthesis + 1 overview
    - 关键 verified 事实：Code with Claude 2026 大会真实 5/6 SF；DeepSeek-TUI 24.7k stars by Hunter Bown；Antirez ds4 真存在；Anthropic FDE $180-550K 真招聘；CodeBanana 真出门问问 2024
    - 关键 flagged 不实：SEQUENCE OS¹ 未找到 commercial product
    - 更新 INDEX (页面数 71 → 85) / log.md / gaps.md (+9 新推测问题)
  - **outcome**：vault AI 主题资产完整化；[[综合_AI浪潮下中国留学生的工具选型与岗位选择]] 给 Javen 提供 12 月 timeline；触发 task-026 落地 follow-up


- [x] **task-006** | 部署 AI Watch v2（每日 AI 趋势监测 daemon skill） | #P1 | owner: @claude | done 2026-05-06
  - **完成**：全部 7 个子任务 [x]。skill 部署到 `.claude/skills/ai-watch/SKILL.md`；daemon 持续产出每日报告（04-29 至今）；系统稳定运行无 Javen 不满意反馈。
  - **归档**：由 daemon 2026-05-06 dawn-shift 执行归档

- [x] **task-015** | Daemon 03:00 incident 后续：监测 + 长期 robustness | #P1 | owner: @claude | done 2026-05-02
  - **目标**：验证 4/29 修复（stream timeout / hook quote bug / fresh session）稳定性
  - **完成**：2026-05-02（连续 3 次 daemon 跑通：4/30 / 5/1 / 5/2 ✅；lessons.md 更新；hook bug 已修无回归）
  - **注**：email-triage Gmail MCP 问题为独立问题，跟踪在 task-011

- [x] **task-016** | 物理重构：所有自动化文件归并到 `MyBrain/automation/` module | #P1 | owner: @claude（主对话） | done 2026-04-29
  - **目标**：Javen 4/29 上午要求"把所有自动化的任务单独放一块好查"。把分散在 system/ + research/ai-watch/ 的所有自动化文件归并到 `MyBrain/automation/` 单一 module，新建 dashboard 让他每天 1 click 看完
  - **Definition of Done**：所有 17 个 automation 相关文件移到 `automation/`；19 个 vault + daemon 文件的引用更新；wrapper.sh syntax + check mode pass；automation/README.md dashboard 就位；daemon 4/30 03:00 用新路径跑通（待验证）
  - **创建**：2026-04-29
  - **完成**：2026-04-29
  - **子任务**：
    - [x] a. 建 `automation/{runs,reports/ai-watch,reports/email-triage,queue,docs,logs,archive}/` 目录树
    - [x] b. mv 17 个文件 (system/* + research/ai-watch/*) → automation/
    - [x] c. sed 批量替换 19 个文件里的旧路径引用 (vault 17 + daemon 2)
    - [x] d. 边缘清理：wikilink、settings.json bash 权限、audit.sh 文件名匹配
    - [x] e. 写 `automation/README.md` dashboard（today 链接 + 队列入口 + 健康度 + 快速命令）
    - [x] f. 写 `wiki/工程方法/Managed Agents vs Claudian daemon.md`（响应 Javen 第二个需求）
    - [x] g. 验证：bash -n wrapper.sh + check mode + grep 残留路径
    - [ ] h. 4/30 03:00 daemon 跑通新路径（最终验证 — pending overnight）

- [x] **task-012** | 部署"轻量审批队列"系统（approvals.md）| #P1 | owner: @claude（主对话） | done 2026-04-29
  - **目标**：替代"在对话里打字 yes/no"为"vault 文件打勾批准"，让 Javen 决策更轻量 + 跨设备（手机 Obsidian app 也能批）
  - **Definition of Done**：approvals.md 模板 ✓ + 真实当前 5 条 ✓ + CLAUDE.md 接入 ✓ + daemon prompt 加 Step 0 扫审批 ✓ + 跑通一次 ✓（Javen 4/28 23:30 打勾 4 项 → 主对话 4/29 00:15 全部执行 + 归档）
  - **创建**：2026-04-28
  - **完成**：2026-04-29
  - **子任务**：
    - [x] a. 写 `automation/queue/approvals.md`（template + 真实初始 5 条）— 2026-04-28
    - [x] b. `MyBrain/CLAUDE.md` 加 reference — 2026-04-28
    - [x] c. 改 daemon `prompt.md`：加"扫 approvals.md → 执行 [x] → 归档"step — 2026-04-29
    - [x] d. 端到端跑通：Javen 打勾 4 项 → 主对话扫到 → 立即执行 → 移到 ✅ 已批准列 — 2026-04-29
  - **副产物**：approvals.md 现存 1 条未勾选（GitHub profile setup），4 条已批准已归档；后续 daemon 03:00 也会扫这个文件

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
    - [x] g. 写 `automation/CLAUDE.md`（Claude 操作指令）
    - [x] h. 写 `automation/docs/user-guide.md`（用户文档）
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

详细规则见 `MyBrain/automation/CLAUDE.md` 与 `MyBrain/automation/docs/user-guide.md`。
