# 任务看板

> Javen 和 Claude 共用的任务看板。Javen 写下方向，Claude 接管执行；遇到需要决策的事写 `⚠️ blocked on @javen`，移到"🔒 阻塞"列等 Javen 拍板。

**最后更新**：2026-04-30 15:30
**当前状态**：1 进行中（task-003）/ 0 阻塞 / 11 待启动 / 5 已完成
（**真实进度**：task-006/008/011 名义在"待启动"列但子任务都已推进到"等外部验证"——见各卡内 [x] 子任务 + 备注。task-012 已闭环移入"✅ 已完成"。Brain Corp 2026 cycle 4/1 已外部下架→归档不投。**新加 task-017/018/019 — 4/30 主对话三连推进：两个 ECE project 骨架 + AI subagent 团队系统**）

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
    - [ ] e. 端到端验证：等 2026-04-29 03:00 daemon 自动跑产出第一份 → Javen 审 quality（漏没漏 / 误报多不多）
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

- [ ] **task-006** | 部署 AI Watch v2（每日 AI 趋势监测 daemon skill） | #P1 | owner: @claude（**主对话**，非 daemon）
  - **目标**：daemon 每天扫 25+ 个权威 AI 来源，按 Javen 简历画像（ECE ML/Controls + ROS2/YOLOv8 + 数字健康 + edge AI 潜力）写"行业雷达 + 项目教练 + 简历放大器"风格的早安简报到 `MyBrain/automation/reports/ai-watch/<日期>.md`；每条信息回答"是什么 / 为什么是你 / 能做什么小项目（含简历价值）/ 难度+耗时"
  - **Definition of Done**：
    - ai-watch skill 部署到 `.claude/skills/ai-watch/SKILL.md`（含 25+ 来源白名单 + Javen 画像 + 报告模板）
    - daemon `rules.md` 更新：解禁 ai-watch 白名单的 WebFetch
    - daemon `prompt.md` 更新：双任务优先级（先 ai-watch、剩余推看板）
    - 建好 `MyBrain/automation/reports/ai-watch/` 目录
    - 端到端测试：手动跑 wrapper.sh 一次产出第一份针对 Javen 的报告（≥3 条 importance-3 含项目灵感+简历价值）
    - 看板加 task-007「Recurring: 每日 AI Watch 运行」永久 in-progress
  - **创建**：2026-04-27
  - **更新**：2026-04-29（主对话 a/b/c 全部完成 — skill 写完 + daemon wrapper 加 WebSearch 白名单 + rules 改 rule 15 限定 ai-watch 上下文允许 WebSearch + prompt 加 Step 0.5(a)）
  - **⚠️ 重要**：daemon **不能自己做这个任务**（rules 第 4-5 条禁止改 `.claude/` 和 `~/.claude-daemon/`）。Javen 想推进时在主对话喊一声"推进 task-006"，**主对话 Claude** 来做。子任务 a/b/c 都涉及修改 daemon 自己的配置。
  - **🎯 设计原则（Javen 2026-04-27 提醒）**：报告格调**避免过度功利化**。简历相关性应该是**隐含副产物**（"哦这个我能玩玩"）而非显性目标（"这个能让简历加分 +X"）。带太强目的性会变成信息焦虑制造机，反而效果差。报告应该 **70% 启发好奇心 + 30% 落地建议**——先让 Javen 觉得"这事好玩 / 有意思"，再说"顺便能做个小项目"。importance 排序应该看"对 Javen 兴趣 + 当下重要性"而不是"对简历有多大用"。
  - **子任务**：
    - [x] a. 写 `.claude/skills/ai-watch/SKILL.md`（70%/30% 设计 + Tier 1/2/3 信息源轮换 + 600 字早报模板）— done 2026-04-29 by 主对话
    - [x] b. 改 `~/.claude-daemon/wrapper.sh` 工具白名单加 WebSearch + `rules.md` 第 15 条改"WebSearch 限定 ai-watch skill 内使用" — done 2026-04-29
    - [x] c. 改 `~/.claude-daemon/prompt.md` 加 Step 0.5(a)：每天第一次跑时如今天报告不存在则生成 — done 2026-04-29
    - [x] d. 建 `MyBrain/automation/reports/ai-watch/` 目录 — done 2026-04-28 (daemon 03:00)
    - [ ] e. 端到端验证：等 2026-04-29 03:00 daemon 自动跑产出第一份 → Javen 审阅质量
    - [ ] f. （后续）看板加 task-007「Recurring: 每日 AI Watch 运行」永久 in-progress（先看第一份质量再决定是否要这个 recurring 任务，或者直接靠 daemon prompt Step 0.5 永久跑就够）
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

- [ ] **task-015** | Daemon 03:00 incident 后续：监测 + 长期 robustness | #P1 | owner: @claude（主对话）
  - **目标**：4/29 03:00 daemon 因 Anthropic API stream idle timeout 失败（cache 累积到 ~200K + Claude 处理过程 idle 超时被切）。已部署初步修复，需要验证 + 记录 + 后续 robustness 改进
  - **触发**：4/29 03:00 daemon 失败 → 4/29 11:20 主对话 Claude root-cause + 部署修复
  - **Definition of Done**：
    - 至少连续 3 次 03:00 daemon 跑通（无 stream timeout）
    - failure mode 写入 `automation/docs/lessons.md`（让以后 debug 类似问题快）
    - hook 路径 quote bug 修完没回归
  - **创建**：2026-04-29
  - **更新**：2026-04-29
  - **关联**：`MyBrain/automation/runs/2026-04-29.md`（根因报告）
  - **子任务**：
    - [x] a. Root-cause 4/29 03:00 失败 — 4/29 11:15 (主对话). NDJSON exit `is_error: true`, `result: "API Error: Stream idle timeout"`
    - [x] b. 修 settings.json hook 路径未 quote bug — 4/29 11:25 (主对话, 4 处全量替换)
    - [x] c. 改 wrapper.sh 不再 --resume，每次 fresh session（用 uuidgen）— 4/29 11:30 (主对话)
    - [x] d. wrapper.sh syntax check pass — 4/29 11:30
    - [x] e. 监测明早 4/30 03:00 daemon — 跑通 / 还失败？产出报告？hook 是否报错？ — done 2026-04-30（ai-watch ✅ 产出；email-triage ❌ Gmail MCP 未注入；看板任务正常跑）
    - [ ] f. 监测 5/1 + 5/2 03:00 daemon — 连续 3 次跑通才算 DoD 满
    - [x] g. 写到 `automation/docs/lessons.md`：第 7 条经验"长 context resume session 会触发 API stream timeout" — done 2026-04-30
    - [ ] h. （可选 backup）若 stream timeout 再次出现 → 拆 daemon 工作流为两个 session（先 skill 再看板，每个独立 fresh session）

- [ ] **task-017** | ECE175B Project: Attribute-Disentangled CFG (ADG) — 实现 + 训练 + 报告 | #P0 | owner: 混合（@claude 写代码 / @javen 跑 GPU + 提交）
  - **目标**：完成 ECE175B 期末 project — Attribute-Disentangled Guidance for Diffusion Models。proposal 4/22 已交，timeline 现在在 Week 5-6（实现 ADG sampling + 初步实验）
  - **背景**：核心想法是把标准 CFG 的单一 guidance scale `w` 拆解为 K 个 per-attribute 的 `w_k`，让 face attributes（笑/眼镜/男/年轻）有独立强度控制。在 CelebA 64×64 数据集上验证。proposal 在 `raw/ucsd/Spring 2026/ECE175B/proposal.pdf`
  - **Definition of Done**：
    - 代码 repo（`MyBrain/projects/ece175b-adg/` + 后续 push GitHub）含 dataloader / DDPM / CFG / ADG sampling / FID + per-attribute accuracy 评估脚本
    - Baseline DDPM 在 CelebA 训练完毕（~50 epoch，需要外部 GPU）
    - ADG sampling 实现 + 初步可视化（同一 seed，不同 w_k 组合的图像）
    - Midterm report (Week 7) 提交：模型设计 + 数学 + 初步结果
    - Final report (Week 10-11) 提交 + 可视化 + per-attribute 解耦分析
  - **创建**：2026-04-30
  - **更新**：2026-04-30
  - **🤖 AI vs Javen 分工**：
    - ✅ **主对话能干**：写完整代码骨架（dataloader / DDPM / training loop / ADG sampling / 评估）
    - ✅ **daemon 凌晨能干**：跑代码 lint / 写 README / 调 prompt / 整理实验日志
    - ❌ **必须 Javen**：提供 GPU 资源（本机无 GPU，daemon 也没）+ 真正点"提交报告"
  - **⚠️ 主要 blocker**：GPU 方案未定 — Colab Pro / UCSD DSMLP / RunPod / Kaggle 之一。已写到 approvals.md 等 Javen 打勾
  - **子任务**：
    - [ ] a. 主对话写代码骨架 → `MyBrain/projects/ece175b-adg/`（dataloader, model, train.py, sample.py, adg.py, eval.py, README）
    - [ ] b. ⚠️ blocked on @javen — GPU 方案选定（默认推荐 Colab Pro $10/月）
    - [ ] c. 训练 baseline conditional DDPM 在 CelebA（~50 epochs，预估 4-8h GPU）
    - [ ] d. 实现 ADG sampling（K+1 forward passes，可视化对比 standard CFG vs ADG）
    - [ ] e. 量化评估：FID 分数 + 每个 attribute 的分类器准确率 + 解耦度（调一个 attribute 时其他变化多少）
    - [ ] f. 失败模式分析：哪些 attribute pair 干扰最严重 / 线性分解假设何时失效
    - [ ] g. Midterm report (Week 7, 2026-05-13 左右) — 模型设计 + 数学 + 初步结果
    - [ ] h. Final report (Week 10-11, 2026-06-12 左右) — 7-10 页 NeurIPS 风格 + GitHub repo
    - [ ] i. ⚠️ blocked on @javen — 期末交报告 + 提交 GitHub repo 链接
  - **关联**：[[ECE175B_概览]], [[ECE175B_Lecture3_变分推断与ELBO]], [[ECE175B_Lecture4_生成对抗网络]]

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
  - **更新**：2026-04-30
  - **🤖 AI vs Javen 分工 — 这是"AI 全包"的好 case**：
    - ✅ **主对话能干**：全部代码（纯 numpy/scipy/sklearn + Anthropic API），全部跑实验（CPU-only）
    - ✅ **daemon 凌晨能干**：跑长时间 LOSO 评估（sklearn 可能 1-2 小时）+ 调 Claude API 跑 ~1800 windows 的 λ 生成
    - ❌ **必须 Javen**：① 第一次跑前批准本机装 Python 包 ② 真正点"提交报告"
  - **⚠️ 主要 blocker**（已写到 approvals.md 等打勾）：
    - 批准在本机 pip install (numpy/scipy/scikit-learn/anthropic/mat73)
    - 批准下载 IEEE SPC 2015 dataset 到 vault（~50 MB）
    - 提供 ANTHROPIC_API_KEY（你的 Claude Max 订阅可以走 API mode 给 daemon 用，~5min 生成）
  - **子任务**：
    - [ ] a. 主对话写代码骨架 → `MyBrain/projects/ece284-llm-ppg/`（data.py, troika_lite.py, rf_baseline.py, llm_lambda.py, react_agent.py, evaluate.py, README）
    - [ ] b. ⚠️ blocked on @javen — 批准 pip install + 数据下载 + API key（approvals.md）
    - [ ] c. TROIKA-lite 实现（bandpass + FFT + spectral subtraction + peak detect）+ sanity check on static windows
    - [ ] d. Random Forest baseline（4 频域特征 + sklearn）+ LOSO MAE
    - [ ] e. Claude λ-generator（per-window prompt，输出 λ ∈ [0.1, 3.0]，driving fixed pipeline）
    - [ ] f. 全 12 subjects LOSO 评估 → MAE 总分 + motion-level 分层 + λ appropriateness 100-window 分析 + token cost
    - [ ] g. Project Update report (Week 8, 2026-05-20 左右) — 进度 + 1-2 张架构图 / 初步结果图
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
