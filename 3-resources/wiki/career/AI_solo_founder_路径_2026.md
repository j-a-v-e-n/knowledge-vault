---
title: AI-leveraged solo founder 10 年路径 + dual-track (个人公司 + 打工)
type: overview
tags: [career, solo-founder, indie-hacker, AI-leverage, dual-track]
created: 2026-05-15
updated: 2026-05-15
confidence: high
priority: active
sources:
  - https://lexfridman.com/pieter-levels/
  - https://paulgraham.com/foundermode.html
  - https://www.navalmanack.com/almanack-of-naval-ravikant/find-a-position-of-leverage
  - https://www.darioamodei.com/essay/machines-of-loving-grace
  - https://newsletter.marclou.com/p/i-grew-a-saas-to-1m
  - https://news.tonydinh.com/p/nov-2024-my-first-million
  - https://www.indiehackers.com/post/photo-ai-by-pieter-levels-complete-deep-dive-case-study-0-to-132k-mrr-in-18-months-3a9a2b1579
  - https://scrapingfish.com/blog/indie-hackers-revenue
  - https://www.project-syndicate.org/commentary/ai-productivity-boom-forecasts-countered-by-theory-and-data-by-daron-acemoglu-2024-05
  - https://www.pin.com/blog/tech-job-market-report/
note: 配套 [[AI_engineer_10年路径_2026]]。本页主推 Track B (solo)，前者主推 Track A (employee)。Javen 明确 dual-track 要同时考虑。
---

# AI-leveraged solo founder 路径

> Javen 5/15 反馈："不是 single-choice，自己赚钱跟打工都要考虑，但你 (AI) 之前主要考虑 employee 这边"。本页是 Track B（solo / 个人公司）深度调研，配套 [[AI_engineer_10年路径_2026]]（Track A employee）。3 个 parallel researcher verified：solo founder thought leader 共识 + GitHub trending + 真实 income distribution + AI 替代员工时间表。

---

## 0. 你直觉的 verdict（verified vs 直觉）

### ✅ 对的部分

- **AI 替代初中级员工正在发生**（CEO 共识）：
  - **Dario Amodei (Anthropic)**：AI 可能 5 年内消灭 50% entry-level white-collar 工作（[Axios](https://www.axios.com/2025/05/28/ai-jobs-white-collar-unemployment-anthropic)）
  - **Sam Altman (OpenAI)**：AI agent 能做"2-3 年经验工程师的任务"
  - **Mark Zuckerberg (Meta)**：2025 AI 达到中层 engineer 能力（Joe Rogan podcast）
- **Entry-level 招聘真崩了**（[Tech Job Market Report 2026](https://www.pin.com/blog/tech-job-market-report/)）：
  - Junior developer 职位 vs 2020 基线 **-40%**
  - CS 应届失业率 5.8%
  - 22-25 岁 AI 相关岗位就业 -13% (2025)
- **Sam Altman 公开 predict "billion-dollar 1-person company"** (NYT 2024)：背书 individual leverage
- **Naval / Karpathy / Paul Graham 共识 "code + media = leverage"**：1 人能 build asset 而非 trade time

### ❌ 错或不确定的部分

- **"公司缩水" 无强证据**：YC solo founder 比例 2020 年 33.64% → 2026 年 **11%**，**反而下降**（VC 偏好 co-founder 团队风险对冲）
- **"个人公司激增" 间接信号弱**：Stripe Atlas LLC 注册 +130% YoY，但是**总体**增长，不分 1 人 vs 多人
- **历史类比不准**：工业革命 → 工人激增（反例）；互联网 → indie 兴起靠**工具杠杆**（博客平台 + 支付 + CDN），不是因为"前一代被替代"

### 🚨 verified Counter-arguments

- **Daron Acemoglu (MIT, 2024 Nobel Economics)**：[AI 仅贡献 1.1-1.6% 10 年 GDP 增长](https://www.project-syndicate.org/commentary/ai-productivity-boom-forecasts-countered-by-theory-and-data-by-daron-acemoglu-2024-05)，远低于业界"翻倍"预期。"问题不是泡沫破裂，是炒作持续更久、伤害更深，因为我们被骗去投资不良技术方向"
- **Yann LeCun**：[LLM 5 年内过时](https://www.newsweek.com/nw-ai/ai-impact-interview-yann-lecun-llm-limitations-analysis-2054255)，被 JEPA 类型替代。当前 LLM "缺乏物理世界理解、持久记忆、真正推理能力"
- **Greg Isenberg**：[多数 solopreneur 不快乐](https://www.gregisenberg.com/)，"multipreneur"（2-3 人小团队）才是 future

### 修正 verdict

你直觉**部分成立**（entry-level 真消失）但**过度外推**（公司缩水 + 个人公司激增 缺数据）。**关键风险不是"被 AI 替代"而是"entry-level 通道关闭，后进入者门槛上升"**。

**Reframe**：不是"赶快逃离打工浪潮"，是"**筛选加速时代**"——能做到 Phase 2 (solo) 的人赢更多，做不到的被挤出。

---

## 1. Dual-track 长期框架（不是 single choice）

```
                  [ Year 0 (现在, 2026) ]
                          |
              你的 ECE senior + ML 经验 + US citizen
                          |
                +---------+-----------+
                |                     |
         Track A: Employee     Track B: Solo Founder
         (FAANG/Anthropic       (build SaaS / content
          intern → FT)           / micro-business)
                |                     |
                |                     |
              [ Year 1-2 ]          [ Year 0-1 ]
              建立 production     先 ship MVP, 测
              经验 + paycheck       product-market fit
                |                     |
                |       <----- 大多数成功 solo 都
                |       <------ 先打工 1-2 年攒了经验+资金
                |                     |
                |                     V
                +---> [混合 / 全 solo] <---+
                          |
                  [ Year 3-5 ]
                  - 主业 solo $5-50K MRR
                  - OR senior engineer + side project
                          |
                          V
                  [ Year 5-10 ]
                  - solo $50K-$500K MRR (lifestyle)
                  - OR small team 2-5 人公司
                  - OR sell + start new
```

**核心 insight**（verified from cases）：
- **Pieter Levels** — 10 年 indie 才到 $250K/mo（Nomad List 2014 → Photo AI 2023）
- **Daniel Vassallo** — 10 年 AWS 攒 $1M savings → 2019 quit → 5 年 Small Bets portfolio
- **Marc Lou** — 被 laid off 后 forced solo（不是主动 quit）
- **Tony Dinh** — 多个 side project 数年后才 ChatGPT 时机命中

**Pattern**：先打工攒经验 + 资金 + side project skill → 时机到了 quit / 被迫 quit → solo。**很少有人直接从大学 → 全职 solo**。

**给你的实际建议**：暑期同时**两条腿走路**——主线 build solo MVP 测试 product-market fit + 副线申请 fall internship 兜底。不是 either/or。

---

## 2. Solo founder 真实 income distribution（反 selection bias）

来源：[Indie Hackers verified revenue analysis](https://scrapingfish.com/blog/indie-hackers-revenue)

| Tier | % of indie 项目 | MRR 区间 |
|---|---|---|
| **Dead** | 54% | $0 |
| **零碎** | 80.9% | < $500 MRR |
| **持续** | 6.4% | $5K+ MRR |
| **Superstar** | **4.8%** | $10K+ MRR |
| 中位数 (有 revenue 的) | — | $303/mo |

**Time to first revenue**：
- Part-time solo：6-18 月 中位数
- Full-time solo：12-24 月 中位数

**Pieter / Tony / Marc 都是 4.8% Superstar tier**——99th percentile outliers，**不能作为 median expectation**。

**对你的 implication**：如果你 6 个月 build solo 项目，statistically：
- 54% 概率 dead
- 80% 概率 < $500/mo (不够 quit 内涵)
- 5% 概率 真做出来 $5K+/mo（这就是为啥 dual-track 重要——5% 概率要 employee path 兜底）

---

## 3. Verified solo founder case study（你能 copy 哪部分）

### 3.1 Pieter Levels — Photo AI / Nomad List ($3M+ ARR solo)

- **Build**：Photo AI 3-4 周 launch (Feb 2023)；Nomad List 60 天 + $150 startup cost
- **First revenue**：Photo AI week 1 = $5.4K MRR（organic Product Hunt）
- **Peak**：Photo AI $132K MRR (2024)
- **Stack（这里你会被震惊）**：**vanilla PHP 14K lines + SQLite + Replicate API + 单 DigitalOcean VPS $40/mo**。不是 Next.js, 不是 Postgres, 不是 Kubernetes
- **Cost**：$13K/mo expenses ($12K API)，**87% profit margin**
- **Distribution**：build in public on Twitter/X (monthly MRR public)；Product Hunt launches
- **Verbatim**："Competitive advantage is shipping before things are ready. No planning, no roadmaps, just shipping and adapting." ([Lex Fridman #440](https://lexfridman.com/pieter-levels/))
- **核心可 copy 模式**：solve own problem (他是 nomad → Nomad List) + 简单 stack + ship fast + build in public

### 3.2 Tony Dinh — TypingMind ($1M Year 1)

- **Build**：48 小时 first version
- **时机**：ChatGPT launch **几小时后** ship
- **First revenue**：$22K first week
- **Year 1**：$500K，Year 2 累计 $1M
- **Stack**：API wrapper (OpenAI/Anthropic) + React frontend
- **核心可 copy**：**时机 + 速度** > **代码复杂度**。Tony 之前是 DevUtils ($8K/mo background）+ Black Magic 多个 side project 累积的 indie skill，ChatGPT 来时反应最快

### 3.3 Marc Lou — ShipFast ($1M lifetime by 2024)

- **背景**：被 laid off 后 forced solo
- **Strategy**：2 年 ship 16 个产品（不是死磕一个）
- **ShipFast 单月 $20K+ MRR**；CodeFast $20K+；DataFast $15K
- **Stack**：Next.js boilerplate
- **核心可 copy**：**Portfolio approach** — 不押注一个产品，多个 ship 找 product-market fit

### 3.4 Daniel Vassallo — Small Bets ($3.6M exit)

- **背景**：ex-AWS $511K/year，2019 quit with $1M savings
- **Failure**：SaaS Userbase 失败
- **Pivot**：Small Bets — "Good Parts of AWS" book $140K in 2 weeks；Twitter course $310K from 16 小时录制
- **2024 exit**：Small Bets community + investing fund 卖 $3.6M
- **核心可 copy**：**小赌博 portfolio** — 不追 unicorn，追"keep self-employed"。低风险版

### 3.5 Justin Welsh — Solo creator ($10M+ ARR)

- **不是 SaaS**：digital courses (LinkedIn OS, Content OS) + newsletter (175K subs) + coaching
- **Profit margin**：92%（Kajabi + Zapier 极简 ops）
- **核心可 copy**：**Content-as-leverage** — 不一定要 build SaaS，做 course / newsletter 也是 solo path

### 共性 pattern（5 个 case study）

1. **极快 ship**（3 天 - 4 周，**不是 6 个月**）
2. **极简 stack**（vanilla / 现有 framework / API wrapper）
3. **Distribution = build in public**（Twitter/X / IndieHackers / Product Hunt / HN）
4. **解决自己的痛点**（Pieter 是 nomad；Tony 是 ChatGPT 早期用户）
5. **多数有 prior 积累**（10 年 indie / $1M savings / multiple side projects / forced 解雇）

---

## 4. Naval 框架 fit 你

> "Wealth = Specific Knowledge + Accountability + Leverage" — Naval Ravikant

**你 specific knowledge**（其他人没有的组合）：
- UCSD ECE technical depth（signal processing, optimization）
- ML 实战（diffusion / LLM / robotics）
- AI workflow expert（vault + Claude Code daemon + subagent team）— **你已经在用 AI build personal AI workspace 6 个月**

**你 leverage candidate**：
- **Code**：build SaaS / Chrome extension / Obsidian plugin（permissionless replication, zero marginal cost）
- **Media**：技术博客 / Twitter / YouTube tutorial / course / Substack newsletter（permissionless, scale to millions）

**你 accountability**：
- **Build in public**：用 Twitter/IndieHackers 公开 build process + MRR — 这是 Pieter / Marc Lou / Tony 都背书的 distribution channel + accountability mechanism

---

## 5. 1-人 project management framework（self-derived from 业界）

我从这些 framework 综合 derive（**不让你教**）：

- **Drucker** "Effective Decision" 5 步：problem type → boundary conditions → spec → action → feedback
- **Eric Ries Lean Startup**：Build-Measure-Learn loop + MVP + validated learning
- **Marty Cagan "Inspired"**：4 risks (value / usability / feasibility / business viability)
- **Pieter Levels playbook**：ship fast + solve own problem + simple stack
- **Agile/Kanban**：WIP limit + continuous delivery
- **80/20 Pareto**：focus on 20% effort → 80% outcome

### 1-人 solo founder 通用 stage 框架

```
Stage 1: Discovery (1 周)
  ├─ Drucker: 明确问题边界
  ├─ Marty Cagan: validate 4 risks
  │   - Value: 真有人买吗?
  │   - Usability: 用户能用吗?
  │   - Feasibility: 你能 build 出来吗?
  │   - Business: 经济模型成立吗?
  ├─ 用户访谈 5 人 (Pieter rule: 解决自己 + 5 个朋友的痛点)
  └─ 输出: 1-pager spec (problem / user / solution / monetization)

Stage 2: MVP Build (1-4 周)
  ├─ Pieter rule: 极简 stack, ship 越快越好
  ├─ Lean MVP: 只 build "Minimum Viable" 不要完美
  ├─ Agile: WIP=1, 完一个 feature 再下一个
  └─ 输出: Live product URL, 能 sign up + pay

Stage 3: Launch (1 天)
  ├─ Product Hunt + Twitter/X build in public post
  ├─ IndieHackers + HackerNews + Reddit niche subreddit
  ├─ 用 Naval: build in public 是 long-term audience asset
  └─ 输出: First 100 visitors, first $1

Stage 4: Iterate (持续, 2-4 周内/cycle)
  ├─ Build-Measure-Learn loop (Eric Ries)
  ├─ Daily metric review (MRR, signup, churn)
  ├─ Weekly Drucker self-mgmt: what worked? what wasted?
  ├─ Customer feedback → next ship
  └─ 输出: traction signal (MRR growth, retention)

Stage 5: Decide (60-day review)
  ├─ Kill if < $100 MRR 60 days
  ├─ Scale if $500+ MRR with growth
  ├─ Pivot if signal but wrong direction
  └─ 输出: keep / pivot / kill decision
```

### 你的"AI 团队"设计（你 PM，AI agent 干活）

你说"AI 比人厉害的多，该派什么人干什么活" — verified from Karpathy "Software 3.0" + Anthropic Claude Code + 业界 multi-agent practice：

| Role | AI 工具 | 你的输入 | 输出 |
|---|---|---|---|
| **Engineer** | Claude Code / Cursor / Aider | Spec + acceptance criteria | Working code + tests |
| **Designer** | Midjourney + Figma AI / v0.dev | "marketing site for X" + brand vibe | UI mock + Tailwind code |
| **Marketer** | Claude/GPT | product description + target user | Landing copy / social posts / email |
| **Researcher** | Perplexity / Claude WebSearch | "竞品分析 X 类工具" | Competitor matrix + market sizing |
| **Customer support tier-1** | LLM API + 你 SaaS 内嵌 | FAQ + product knowledge | 自动答 80% repetitive question |
| **DevOps** | Claude Code + Bash + Railway/Fly.io | "deploy this and monitor" | CI/CD + uptime monitor |
| **Analyst** | Claude + 数据 | raw MRR/user data | 趋势图 + insight 建议 |

**你的 unique role**（AI 替代不了的）：
1. **Product judgment / taste** — 决定什么 build 什么不 build
2. **Customer interview** — 真用户对话, AI 无法替代 (Marty Cagan: discovery 必须人做)
3. **Make hard call** — 商业 decision (定价 / pivot / kill)
4. **Brand + accountability** — 你的 face + 信任 (Pieter Levels build in public 模式)

**Drucker insight**：管理的本质是 **outcome > activity**。你 measure agent 的 output (是否 ship feature, 是否解决 bug)，不 micromanage agent 怎么做。

---

## 6. 3 个具体 candidate project（基于你 ECE 经验）

每个 project 详细 spec + MVP timeline + monetization + 现实预期。

### Project A: AI-Native Researcher Workspace（推荐 #1）

#### Problem

PhD students / researchers / 像你这种学术工作者面临的痛点：
- 论文 reading + 笔记 + cross-reference 慢
- 多个论文之间 relationship 难追踪
- 笔记跨 session/laptop 同步麻烦
- 当下工具 (Notion / Obsidian / Roam) 都是 generic, **不是 AI-native**

#### Target user

- PhD students (CS / Bio / Eng)
- ML researcher 
- Senior undergrad doing research
- 总规模 US：~200K-300K 人

#### 你的 unique fit

**这是你 6 个月已经在 build 的东西**——你的 vault + Claude Code daemon + subagent team + 抖音 pipeline。你 dogfood 自己产品 6 个月。

**Naval framework**：
- Specific knowledge ✓ (你已经 build 出来了一个 working version)
- Leverage = code (Obsidian plugin or standalone Electron app)
- Accountability = build in public (你 vault 经验写成 series)

#### Tech stack

- **Frontend**：Obsidian plugin (TypeScript) 或 Electron app
- **AI 层**：Anthropic API + 本地 embedding (sentence-transformers)
- **Storage**：用户本地 (privacy 卖点) + optional sync (Cloudflare R2)
- **Payment**：Stripe + Gumroad

#### MVP（4-6 周）

Features (最 minimal viable)：
1. Auto-summarize PDF 论文 (Claude API)
2. Cross-reference 多篇论文（"哪些论文都引用了 X？"）
3. AI-powered 笔记 query ("我笔记里提过 KL divergence 在哪?")
4. Daily research log auto-generated (类似你 daemon ai-watch)
5. Export to Obsidian / Markdown

非 MVP 留后面：multi-user sync, mobile, voice input, advanced agent

#### Monetization

- **Free tier**：local-only, no API quota（你 vault 现状）
- **Pro $9/mo**：Anthropic API 用我的 key + 50K message/月
- **Team $29/mo**：share annotations across team

#### Distribution

- Twitter/X build in public（你日常 vault demo 视频）
- Reddit r/Obsidian (180K 用户) + r/PhDStudents
- HackerNews "Show HN" launch
- 你 vault 已是 living demo

#### Timeline

- Week 1: Discovery + 5 user interview（你已认识 PhD 学生 cohort）
- Week 2-4: MVP build (用你 vault 现有 daemon code 重构)
- Week 5: Launch (PH + Twitter + HN)
- Week 6-12: Iterate based on feedback

#### Realistic income

- 6 个月: $200-$2K MRR (基于 PhD niche TAM + 你 dogfood credibility)
- 12 个月: $1K-$5K MRR (如果 reach product-market fit)
- **80% 概率不到 $1K MRR**，**5% 概率到 $5K+ MRR**

#### 风险

- Obsidian 自身在 build AI features → 可能被吞
- Roam / Heptabase / Reflect 已 occupied niche
- 学术 user 付费意愿低 (PhD 穷)

---

### Project B: Diffusion Model API for Vertical (科技/医疗/电路图)（推荐 #2）

#### Problem

通用 image gen (Midjourney / DALL-E) 不针对特定 vertical：
- 学术 lecture slides 需要 schematic / diagram → Midjourney 出的全是抽象画
- 医疗影像可视化 → 通用 model 不准确
- 电路图 / engineering drawing → 通用 model 完全不行

#### Target user

- ECE/EE professors / students 做 lecture slides
- Bio/Med researcher 做 visualization
- Engineering company 做 doc illustration

#### 你的 unique fit

ECE 175B Diffusion 经验 + 你的 ADG 项目（attribute-disentangled）→ 直接 transfer 到 vertical fine-tuning。Naval specific knowledge ✓.

#### Tech stack

- HuggingFace Diffusers + Stable Diffusion XL base
- LoRA fine-tuning on 学术 figure dataset (开源 scientific figure datasets)
- Replicate API for inference (serverless)
- Simple React/Streamlit UI

#### MVP（6-8 周）

1. 收集训练 dataset (scientific figures, 你 ECE 项目作 starter)
2. LoRA fine-tune SDXL on vertical
3. 简单 UI (text → 学术 figure)
4. Stripe pay-per-image

#### Monetization

- Pay-per-image $0.10-$0.50
- Or $19/mo unlimited (cap fair use)
- B2B custom fine-tune $500-$5K (educator / company custom training)

#### Distribution

- Reddit r/MachineLearning + r/AcademicTwitter
- ECE/EE Twitter community
- Product Hunt
- Demo video on Twitter (你 ECE 175B 项目 already demo material)

#### Timeline

- Week 1-2: 收集 dataset + train baseline LoRA
- Week 3-4: UI build + Stripe integration
- Week 5: launch
- Week 6-12: iterate based on user prompts

#### Realistic income

- 6 个月: $100-$1K MRR (niche TAM 小)
- 12 个月: $500-$3K MRR
- **upside**：B2B custom contract $5K+ one-time

#### 风险

- Stability AI / OpenAI 可能自己 ship vertical model
- 学术 figure dataset 难收集
- Compute cost 可能蚕食 margin

---

### Project C: LLM Evaluation / Benchmark SaaS for B2B（推荐 #3，长期 NPV 大）

#### Problem

中小公司想用 LLM 但不知道哪个 model fit：
- Claude vs GPT vs DeepSeek vs Llama 哪个最适合我 use case？
- 我 prompt engineering 改进真 work 吗？
- 我自己 fine-tune model vs 用 API 哪个 ROI 高？

当下 tool 都太复杂 (LangSmith / Weights & Biases / Helicone) 或太基本 (custom Python script)。

#### Target user

- B2B：中小公司 (10-200 人) 正在 deploy AI feature
- 中型 SaaS 公司想 add LLM
- 不是 individual developer

#### 你的 unique fit

**ECE 284 LLM-PPG benchmark 是你已经做过的事**（Med-HALT 类）。直接 transfer。Naval specific knowledge ✓.

#### Tech stack

- Python backend (FastAPI)
- React/Next.js frontend (你不熟 → Cursor/Claude Code 代写)
- 数据库：Postgres + Redis
- 多 LLM provider：Anthropic / OpenAI / DeepSeek / OpenRouter
- Deploy：Railway / Fly.io

#### MVP（8-10 周）

1. 用户 upload eval dataset (CSV)
2. 选 model 跑 eval
3. Dashboard 显示 accuracy / cost / latency
4. A/B test prompt variations
5. Subscribe to weekly auto-eval report

#### Monetization

- Free tier：100 evals/月
- Starter $99/mo: 10K evals
- Pro $499/mo: 100K evals + custom eval framework
- Enterprise custom $X K/mo

#### Distribution

- LinkedIn (B2B target user 在那)
- IndieHackers + HackerNews
- Dev.to / Medium 技术博客 SEO ("How we evaluated 5 LLMs for X use case")
- Cold email (5-10/day) to mid-market SaaS CTOs

#### Timeline

- Week 1-2: User interview 10 个 B2B (LinkedIn outreach)
- Week 3-6: MVP build
- Week 7-8: Beta with 5 design partners
- Week 9-10: Launch + sales
- Month 3-12: B2B sales cycle long

#### Realistic income

- 6 个月: $0-$500 MRR (B2B sales cycle 长)
- 12 个月: $1K-$5K MRR
- 24 个月: $5K-$50K MRR (B2B LTV 高)
- **upside**：1-2 enterprise deal = $20K+/year each

#### 风险

- 红海市场 (LangSmith / Helicone / Promptfoo 已存在)
- B2B sales cycle 6-12 月，cash flow 慢
- 你是 student → 信任度比 ex-FAANG 创始人低

---

### 3 个 project 对比

| 维度 | Project A (Researcher) | Project B (Vertical Diffusion) | Project C (LLM Eval B2B) |
|---|---|---|---|
| **MVP time** | 4-6 周 | 6-8 周 | 8-10 周 |
| **6 月 MRR** | $200-$2K | $100-$1K | $0-$500 |
| **12 月 MRR** | $1-$5K | $500-$3K | $1-$5K |
| **24 月 MRR potential** | $3-$15K | $1-$5K | **$5-$50K** |
| **fit Javen ECE** | high (你 vault 经验) | high (你 175B) | high (你 284) |
| **入门难度** | 低 (你已 build 6 月) | 中 | 高 (B2B sales) |
| **失败概率** | 60% | 70% | 80% |
| **upside** | lifestyle ($10K MRR) | medium ($5K MRR) | **big ($50K MRR)** |

**推荐顺序**：
- 如果你 risk tolerance 低 + 想 6 个月看到 $1K MRR → **A**
- 如果你 ML expertise 强 + 想 unique technical moat → **B**
- 如果你长期 ambition 大 + 愿意 12-24 月 cash flow 慢 → **C**

---

## 7. 暑期具体 starter plan（dual-track）

### Week 1 (5/15-5/22)

- [ ] **决定 Track A / Track B / dual-track 比例**（建议 dual-track 50/50）
- [ ] **选 1 个 project (A/B/C)** by 5/22
- [ ] **5 个用户 discovery interview** (Marty Cagan validate)
- [ ] (Track A) 投 1-2 个 fall internship application（FAANG/Anthropic 已开 fall apply）

### Week 2-3 (5/23-6/5)

- [ ] (Track B) Project MVP build start
- [ ] (Track A) Karpathy lecture 7 (4 小时，强化你 LLM 基础)
- [ ] Build in public on Twitter (every Mon/Thu 更新)

### Week 4-6 (6/6-6/26)

- [ ] (Track B) MVP soft launch (private beta with friends)
- [ ] (Track A) 复现 1 篇 paper (Anthropic hire 强信号)
- [ ] Iterate based on feedback

### Week 7-8 (6/27-7/10)

- [ ] (Track B) Public launch (PH + HN + Twitter)
- [ ] First $$$ target
- [ ] (Track A) 写 1 篇技术博客发 Substack/Medium

### Week 9-10 (7/11-8/14)

- [ ] (Track B) Iterate, measure MRR weekly
- [ ] (Track A) 第 2 篇技术博客 + GitHub portfolio polish
- [ ] 8/15 后切到 fall 秋招 mode

### 60-day review (7/14)

- 如果 (B) MRR > $500/mo → 加倍 invest，降 fall internship 比例
- 如果 (B) MRR < $100/mo → kill 或 pivot，提高 fall internship 比例
- 任何情况：(A) GitHub portfolio + 技术 blog 是 universal 资产

---

## 8. 跟 employee path 的整合策略

| 情境 | Track A 比例 | Track B 比例 |
|---|---|---|
| Solo MVP 失败 (60-day < $100 MRR) | 100% A | 0% (kill) |
| Solo MVP 微 traction ($100-$1K MRR) | 70% A | 30% B (side) |
| Solo MVP 强 traction ($1K+ MRR growth) | 30% A | 70% B |
| Solo MVP unicorn ($5K+ MRR) | 0% A | 100% B (quit school?) |

**关键 insight**：Track A 不是失败者的 backup，是**长期资产**——你 fall internship 拿到 Anthropic ML 经验 + 1-2 年企业 production code，**之后 solo founder 信任度 100x**（"ex-Anthropic ML engineer build X" vs "UCSD student build X"）。

Pieter Levels / Tony Dinh / Marc Lou 都不是大学直接 solo，都是积累后做。**所以 Track A 不是放弃 solo，是 set up solo 的资本**。

---

## 9. 你要决定的事

1. **暑期 dual-track 比例**：50/50 / 70 Track A 30 Track B / 30 A 70 B？建议 50/50（unless 你已经有 strong Track B idea + 信心）
2. **选哪个 project (A / B / C)**？建议 A（你已有 6 月 dogfood + 最低风险 + 最快 MVP）
3. **是否 @claude 帮起草 Project MVP Phase 1 (Discovery 1 周的 user interview script + 1-pager spec)**？— [[approvals.md]] yes/no
4. **是否 @claude 帮起草 Fall internship batch application materials**（Track A 兜底）？— [[approvals.md]] yes/no

---

## 10. 关联

- [[wiki/career/AI_engineer_10年路径_2026]] — Track A employee path 主页
- [[wiki/career/暑期赚钱探索_2026]] — superseded, 但 platform reference 仍 valid
- [[wiki/career/平台深度与技能路径_2026]] — Mercor/Toptal 真实门槛（之前过乐观，已 corrected）
- [[wiki/career/AI 岗位能力地图_2026]] — fall 招聘 watch list
- [[career/profile-facts]] — US citizen baseline

## 📎 来源（confidence label）

### Solo founder thought leader
- ✅ Sam Altman "billion-dollar 1-person company": [NYT/Fortune](https://fortune.com/2024/02/04/sam-altman-one-person-unicorn-silicon-valley-founder-myth/)
- ✅ Naval Ravikant Almanack: navalmanack.com (verified)
- ✅ Paul Graham "Founder Mode": [paulgraham.com/foundermode.html](https://paulgraham.com/foundermode.html)
- ✅ Pieter Levels Lex Fridman #440 (verified transcript)
- ✅ Dario Amodei "Machines of Loving Grace": darioamodei.com
- ✅ Greg Isenberg multipreneur critique: gregisenberg.com

### Real case study (verified income)
- ✅ Pieter Levels Photo AI $132K MRR: Indie Hackers case study + Twitter MRR public
- ✅ Tony Dinh TypingMind $1M Year 1: news.tonydinh.com
- ✅ Marc Lou ShipFast $1M lifetime: newsletter.marclou.com
- ✅ Daniel Vassallo Small Bets $3.6M exit: starterstory.com
- ✅ Justin Welsh $10M solo: justinwelsh.me

### AI 替代员工趋势
- ✅ Dario Amodei "50% entry-level in 5 years": Axios / CNN
- ✅ Mark Zuckerberg "AI replace mid-level engineers": Joe Rogan podcast verified
- ✅ Tech Job Market Report 2026: junior dev -40% verified
- ✅ Acemoglu "AI productivity overhyped": project-syndicate.org
- ✅ Yann LeCun "LLM 5 年内过时": Newsweek interview

### Income distribution reality
- ✅ Indie Hackers 54% dead / 80.9% <$500 MRR: scrapingfish.com verified analysis
- ✅ YC solo founder ratio 2020 33% → 2026 11%: Ellenox.com analysis

### Counter-evidence (反方)
- ✅ Acemoglu Nobel 2024: project-syndicate.org / MIT Tech Review
- ✅ LeCun LLM critique: Newsweek interview
- ✅ Greg Isenberg "solo unhappy": gregisenberg.com
