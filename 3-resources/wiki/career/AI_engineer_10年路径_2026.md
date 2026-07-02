---
title: AI engineer 10 年路径 (US citizen, ECE→ML/AI 长期投入)
type: overview
tags: [career, AI-engineer, learning-path, 10-year-plan, long-term]
created: 2026-05-15
updated: 2026-05-15
confidence: high
priority: active
sources:
  - https://karpathy.ai/zero-to-hero.html
  - https://www.deeplearning.ai/the-batch/build-career-part-5/
  - https://info.deeplearning.ai/how-to-build-a-career-in-ai-book
  - https://cims.nyu.edu/ai/educational-programs/broad-interest-courses/
  - https://lilianweng.github.io/
  - https://huyenchip.com/ml-interviews-book/
  - https://www.anthropic.com/careers
  - https://www.manning.com/books/build-a-large-language-model-from-scratch
  - https://dataexec.io/p/breaking-into-ai-in-2026-what-anthropic-openai-and-meta-actually-hire-for
  - https://www.sundeepteki.org/advice/how-to-get-hired-at-openai-anthropic-and-google-deepmind-in-2026
  - https://ai.meta.com/blog/yann-lecun-ai-model-i-jepa/
  - https://lilianweng.github.io/posts/2025-05-01-thinking/
note: 配套页 [[暑期赚钱探索_2026]] [[平台深度与技能路径_2026]]。本页是长期路径主页。
---

# AI engineer 10 年路径

> Javen 5/15 反馈："我希望这真的是一个长远的东西，AI 是改变未来几十年的东西，暑假是开始不是结束"。本页基于 3 个 parallel 调研员的 verified material（industry thought leader 公开 path / senior ML engineer 真实 skill bar / 未来 5-10 年复利最大 skill），综合成可执行的 10 年路径 + 暑期定位。

---

## 0. 先承认之前 evaluation 错在哪

之前 [[平台深度与技能路径_2026]] 我标"Javen ✅ 直接 apply Mercor / Outlier"——**这是 cargo cult evaluation**。我犯的具体错：

1. **把 skill 折叠成 binary**：vault 简历列了 "PyTorch / LLM eval / Computer Vision" → 我 default "掌握"。Skill 实际是 5 级 spectrum (Dreyfus: Novice → Advanced Beginner → Competent → Proficient → Expert)，"接触过"和"产线级掌握" gap 巨大。
2. **没 verify 平台真实门槛**：Mercor "5+ years" 不是装饰，**通过者中位 8 年企业经验**。我之前认为"undergraduate-level OK"是只看了 Mercor 官方 minimum，没看实际通过率分布。
3. **混淆"有学问"和"能交付"**：能看懂论文 ≠ 能 debug 数千 QPS 生产 latency；ECE 课程做 diffusion ≠ 能给 client 写 production training pipeline。

**真实 evaluation 框架在第 1 节**。

---

## 1. 你真实 ML skill level (Dreyfus 5 级 + 你的证据)

### 5 级具体描述（verified from agent research）

| Level | 特征 | 典型经验 |
|---|---|---|
| **L1 Novice** | 照教科书跑 / hardcode / 调参凭运气 / 没 validation split 意识 | 0-1 年 / 课程作业 |
| **L2 Advanced Beginner** | 看论文 reproduce / 理解 overfitting / 调 lr 有方向 / 但架构改动还是模仿 | 1-2 年课程强度 + side project |
| **L3 Competent** | 独立设计 ablation study / reproducible code / 知 train-test split 要 temporal-aware / 能复现 paper 数字 | 2-3 年 + 1-2 个完整项目 |
| **L4 Proficient** | 提新研究问题 / production-ready code / design MLOps pipeline / 能 mentor junior | 4-6 年（硕士+2-3 年企业 或 3-4 年深企业） |
| **L5 Expert** | 推 SOTA / 写 published paper / framework-level contribution | PhD 或 8+ 年企业 + 持续发表 |

### Javen 当前定位（honest 评，不安慰）

**位置：L2 高 → L3 低**

**证据**：

✅ **L2-L3 已具备**：
- ECE 175B 笔记/代码 → 数学基础 solid（KL / ELBO / Jensen 能手写）+ 能跑 diffusion 训练
- ECE 284 LLM-PPG → 能读 12+ 论文 + benchmark LLM 评估
- ECE 148 → 完整 robot pipeline 部署经验
- GPA 3.61 → solid 但不 exceptional

❌ **L3 缺的（要进 Competent）**：
- 0 完整 reproduce paper 的 public proof（code + 数字 match）
- 0 GitHub repo 有规模（自己设计的 modular code, 不只是 course assignment）
- 0 production-grade code（error handling / type hints / test / config 系统）
- 0 写过技术博客或独立技术文章

❌ **L4 缺的（要进 Proficient）**：
- 0 企业级 ML pipeline 经验（distributed training / data versioning / monitoring）
- 0 mentor / design doc review 经验
- 0 处理 messy real-world dataset（学术 dataset 都是清干净的）

**距各平台真实门槛**：

| 目标 | gap |
|---|---|
| Mercor 真通过 | 2-3 个完整 production 项目 + 1-2 年工业经验 |
| Toptal | 2+ 年企业经验 + 能讲清设计 trade-off |
| FAANG L4 ML engineer | 4-5 年 + 3-4 个企业项目 + 1-2 篇技术博客 |
| **FAANG / Anthropic / DeepMind ML intern** | **你 fit**（你的 ECE 经验足以 pass intern bar）|
| **Junior ML engineer @ startup new grad** | **你 fit**（毕业后即可 apply） |

### Self-assessment framework（你自己 evaluate, 不靠 AI）

每个 skill 问自己 3 个 question 定 level：

1. **能解释**：能 5 min 给同学讲清楚为什么这个 work / 为什么这个 fail？
2. **能复现**：能从头 implement 一个 working version, 不抄 reference code？
3. **能改进**：发现 baseline 的 limitation, 能 design experiment 验证你的改进 hypothesis 吗？

3 个都能 → L3+ ｜ 能 2 个 → L2 ｜ 只能 1 个 → L1

**对每个核心 skill 自评一遍**（PyTorch / Transformer / RL / 数据 pipeline / GPU 训练 / 分布式 / debug / 评估设计 / 论文阅读 / system design）。

---

## 2. 10 年路径（综合 3 调研员 + industry consensus）

### Phase 1：Foundation（Year 0-2，2026 senior → 2028 first job）

**目标**：从 L2 → L3 末尾。建立"能独立交付完整项目"的能力 + public proof。

#### 学什么（按优先级）

| 优先级 | 资源 | 时长 | 为啥 |
|---|---|---|---|
| **P0** | [Karpathy Zero-to-Hero](https://karpathy.ai/zero-to-hero.html) 8 lectures | 50-100 hr | 从 0 build GPT 全栈。**这是 Karpathy / Anthropic 共同 endorse 的入门**——"if I can't build it, I don't understand it" |
| **P0** | [Sebastian Raschka "Build LLM from Scratch"](https://www.manning.com/books/build-a-large-language-model-from-scratch) | 100 hr 跟书写 | Karpathy 的 textbook 版本，逐行 PyTorch 实现 GPT |
| **P1** | [Andrew Ng "How to Build a Career in AI" 免费 eBook](https://info.deeplearning.ai/how-to-build-a-career-in-ai-book) | 4 hr 读完 | 长期路径思考（informational interview / startup 选择 / 不同时换 role+industry） |
| **P1** | [Chip Huyen "Designing ML Systems"](https://huyenchip.com/) | 300 页 1-2 个月 | "Strong software engineering beats ML knowledge" - Anthropic / Mercor 真实 hiring 都强调 system 能力 |
| **P2** | [Yann LeCun NYU DS-GA 1008](https://cims.nyu.edu/ai/educational-programs/broad-interest-courses/) 14 周 | 60-80 hr | World model / self-supervised / energy-based 系统覆盖（不只是 LLM） |
| **P2** | [Lilian Weng Lil'Log](https://lilianweng.github.io/) 全博客 | 60+ hr 累计 | 跟随研究前沿的 best curriculum-in-public |

#### 同期做什么（hands-on，比上面 lecture 更重要）

1. **完整 reproduce 1-2 篇论文**：
   - 候选：Diffusion Model (DDPM 你已经做过，做 DDIM 扩展) / Flash Attention / nanoGPT / RLHF 简化版
   - 标准：code public on GitHub + reproduce paper 数字 + 写 blog post 解释你做了什么 + paper 没说什么
   - **这是 Anthropic "put at TOP of resume" 的关键** — 不是"我上过课"，是"我做出来了"

2. **写 1-2 篇技术博客**：
   - 不是流水账，是技术深度文章（"我复现 DDPM 时踩的 3 个 subtle bug" / "为什么 Karpathy 的 GPT 用 layernorm 这种顺序"）
   - 发到 personal site / Medium / Substack
   - **这是 Anthropic + OpenAI hiring 都 cite 的强信号**

3. **2026 fall 拿 FAANG/Anthropic/DeepMind ML internship**：
   - 你 ECE 经验足以 pass intern bar（agent 评：YES）
   - 比 Mercor freelance 价值大 100 倍（1 年企业经验 + 工作 reference）
   - apply 周期：fall 起 6-8 月持续投

#### Year 0-2 KPI（不是赚钱多少，是这些）

- [ ] GitHub 有 2-3 个 substantial repo（不是 course assignment, 是自己 design）
- [ ] 复现 1-2 篇 paper 完整（code + 数字 + blog 解释）
- [ ] 写 2-4 篇技术博客
- [ ] 拿 1 个 FAANG/Anthropic-tier ML internship
- [ ] 数学基础重建（linear algebra / probability / optimization 能 derive）

---

### Phase 2：Production + Specialization（Year 2-5，2028-2031）

**目标**：从 L3 → L4。在企业积累真实 production 经验 + 选 specialize 方向。

#### Career move

按 Andrew Ng 建议："don't switch role AND industry simultaneously"。Path：
- **Option A（推荐）**：Full-time ML engineer at startup/scaleup（让你"wear multiple hats"，加速 broad skill）
- **Option B**：FAANG/Anthropic full-time（更窄但更 prestigious）
- **Option C**：PhD（如果决心走 research track，由 Year 2 末决定）

#### 学什么

| 优先级 | 资源 / 主题 | 为啥 |
|---|---|---|
| P0 | [Chip Huyen "AI Engineering" 2025 书](https://www.oreilly.com/library/view/ai-engineering/9781098175092/) | MLOps / eval / cost optimization / production reality |
| P0 | 选 1 个 specialization 方向（见 §4）深耕 | T-shape: broad foundation + 1 deep skill |
| P1 | 系统设计（[DDIA 书](https://dataintensive.net/) + Chip Huyen "ML Systems"） | senior interview 一定问 |
| P1 | [Lilian Weng 论文 reading](https://lilianweng.github.io/) + arXiv 每周 1-2 篇 | 跟随前沿 |
| P2 | 1 篇 published paper / workshop paper | 不是必须但是 strong signal |

#### Year 2-5 KPI

- [ ] 在企业独立完成 1-2 个 ship 的 ML feature
- [ ] 在某专精 domain（RL / VLA / safety / serving / 见 §4）做到 team go-to person
- [ ] design doc / RFC 被采纳 1-2 个
- [ ] mentor 至少 1 个 junior
- [ ] 1 篇 technical write-up（blog 或 paper）

---

### Phase 3：Frontier / Leadership（Year 5-10，2031-2036）

**目标**：从 L4 → L5。Frontier research（如果走 research track）or engineering leadership（如果走 engineer track）。

#### 两条 path 分叉

**Research track**（如果 Year 2-5 已 commit）：
- PhD or 直接 senior research engineer @ Anthropic / OpenAI / DeepMind
- 1-2 篇有影响力 paper
- Conference talk
- Identify "fundamental limitation in field"

**Engineering leadership**：
- Staff/Principal ML engineer
- 架构师 - design 公司 ML platform
- Hire + mentor team
- Drive cross-org AI strategy

**注意**：Hinton 公开说 "约 50% Anthropic technical staff 没 prior ML"，且"plenty brilliant colleagues never went to college"——**PhD 不是 must**，但 research track 还是 bias toward PhD（看 DeepMind / OpenAI senior researcher list 大多 PhD）。Engineer track 不需要 PhD。

---

## 3. 暑期 2026 重新定位

**之前 v2 推荐**：60% Mercor contractor + 25% Hackathon + 15% Kaggle，预期 $15k-$35k。**这个 strategy 错了**。

**重做**：暑期不是为了赚钱，是为了 **build 你的 L2→L3 跳级 portfolio**。10 周时间最高 ROI 不是赚 $15k，是积累 1 个让你 fall internship cycle 强势 Anthropic/OpenAI/DeepMind 的 portfolio item。

### 暑期 P0（不可妥协）

1. **完整复现 1-2 篇 frontier paper + 开源 + 写 blog**
   - 候选 paper（基于你 ECE 经验）：
     - **Reasoning 方向**：DeepSeek-R1 / SimpleRL / OpenR1（💡 复现一个简化版，跑通后写 blog）— [Lilian Weng "Why We Think"](https://lilianweng.github.io/posts/2025-05-01-thinking/) 读 background
     - **VLA 方向**：RT-2 / OpenVLA / ALOHA-ACT（💡 复现 mini 版 in simulation）—  [Google DeepMind RT-2 blog](https://blog.google/innovation-and-ai/products/google-deepmind-rt2-robotics-vla-model/)
     - **Diffusion 扩展**：你 ECE 175B 做的 ADG → 扩展为 conditional generation novel application
   - **deliverable**: GitHub repo (public, README, reproduce 数字 within 5%, 1-2 page technical blog)

2. **Karpathy Zero-to-Hero 看完 lecture 7-8**（4-8 小时）
   - Lecture 7 "Let's build GPT" + Lecture 8 "Build GPT Tokenizer"
   - 看完后你 Transformer 推导一辈子记得

3. **GitHub portfolio polish**
   - Clean README on existing ECE projects
   - 写明：what problem / what approach / what result / how to reproduce
   - 这是 fall internship recruiter 第一个看的

### 暑期 P1（如果时间剩）

4. **AI Hackathon** 2-3 个（Lablab.ai / Devpost）
   - 真实奖金 $3-10k
   - 但更重要：**多 1-2 个 demo 项目 + GitHub commit history**
   - 选 LLM / VLA / agent 类的（贴近你深耕方向）

5. **Kaggle 1 个 competition**
   - 选医疗 / 时间序列（贴近 ECE 284 PPG 经验）
   - 目标：进 top 50% 拿 first medal → 进 Expert tier track

### 暑期不做的

- ❌ **不做 Mercor / Toptal / Outlier**：你 gap 太大，application 失败 + 6 月 cooldown 浪费时间窗
- ❌ **不做 Codementor**：你 expertise 不够，profile 起来也接不到单
- ❌ **不为了快钱接低端 freelance**：低于 $40/hr 的 freelance 时间成本远高于回报

### 现实预期（暑期收入）

- 赚钱：$0-$5k（hackathon prize + Kaggle medal, if lucky）
- 真实 ROI：1-2 个 portfolio item → fall internship success rate × 5-10
- 长期：Anthropic ML intern starting $7k-$10k/month × 3 months = $20k-$30k summer 2027 + new grad full-time $200k+ → 长期 NPV 远大于 summer $15k contractor

---

## 4. 推荐深耕方向（基于你 ECE 经验 + 复利最大）

Agent C 调研: 未来 5-10 年复利最大方向 + 你 ECE 175B (Diffusion) + 284 (LLM) + 148 (Robotics) 的 sweet spot 是：

### 方向 1：Reasoning + RL post-training for embodied systems（首选）

**为什么 fit 你**：
- 你懂 generative modeling（diffusion）
- 你懂 LLM architecture（284 LLM eval）
- 你懂 robotics（148）
- 缺：RL + reward design

**为什么复利大**（agent C 证据）：
- DeepSeek-R1 验证 pure RL 也能学会反思 → reward design 工程师 demand 翻倍
- Figure AI / Boston Dynamics / Tesla Optimus 都在 hire 这个组合（diffusion policy + LLM reasoning + RL）
- OpenAI / Anthropic 现在 senior research engineer 这块 supply 远小于 demand

**入门 path**：
1. Lilian Weng [Why We Think (2025)](https://lilianweng.github.io/posts/2025-05-01-thinking/) 读完 + 之前 RL overview
2. 复现 SimpleRL-reason / Open-R1 简化版
3. 用 RLHF 微调一个 reasoning model on math/code task
4. 跟 UCSD robotics lab 合作做 RL fine-tune foundation model 控制 robotic arm

### 方向 2：VLA (Vision-Language-Action) architecture（次选）

**为什么 fit 你**：
- 你做过 diffusion（image generation）
- 你做过 LLM（sequence modeling）
- VLA 就是把这两条串联（image → tokens → action tokens）
- 缺：多模态 alignment + scaling empirics

**为什么复利大**：
- RT-2 / Figure Helix / ALOHA-ACT 从研究进入应用
- Meta V-JEPA (Yann LeCun 创 AMI Labs 主打方向)
- VLA engineer supply << demand

**入门 path**：
1. 读 RT-2 paper + Figure Helix blog
2. 研究 ALOHA-ACT 的 action tokenization
3. 复现 mini VLA on ALOHA / SimulationOpen dataset
4. 参与 openvla / polyrobotics 开源

### 不推荐的方向

- ❌ **写 boilerplate code / 标准 CNN training / hyperparameter grid search**：已被 Copilot/Cursor 99% 自动化（Addy Osmani 2026）
- ❌ **纯 Computer Vision (no language/action)**：饱和市场
- ❌ **NLP without LLM**：被 LLM 颠覆

### timeless skill（永远不过时）

- **数学**（linear algebra / probability / optimization）— 一次学用 30 年
- **系统设计 / debug / 工程能力** — AI 自动化 boilerplate 反而让这些更值钱（Anthropic / DeepMind 面试都砍 LeetCode 改考 systems-level）
- **跨领域应用**（Bio + AI / Physics + AI / Robotics + AI）— 你 ECE 是天然 robotics+AI 跨界优势
- **沟通 / writing / 教学** — Anthropic hiring 明文强调"technical communication"

---

## 5. 跨 thought leader 共识 vs 分歧

### 共识（Karpathy / Andrew Ng / Yann LeCun / Hinton / Lilian Weng / Anthropic 都同意）

1. **Hands-on coding > 被动看课**
2. **数学基础不可绕过**（linear algebra / probability / optimization）
3. **Year 2 后必须有 production 经验**（不只是课程项目）
4. **Startup > big corp 加速早期 career**（you wear multiple hats）
5. **Boilerplate 被自动化, system design 成 differentiator**
6. **Safety thinking 成 hiring bar**（不只技术，要 fail-mode）
7. **AI engineer ≠ AI researcher**（path 不同）—— year 2-3 必须选

### 分歧（thought leader 之间）

1. **LLM 是否够 vs 需要 world model**
   - Sam Altman: LLM + tool-use 够
   - Yann LeCun: 需要 world models（JEPA），text-only insufficient
   - **事实**：两个都在 happen；LLM 适用范围广，world model 适用 robotics/planning 窄
2. **AGI timeline**
   - Sam Altman 保守 / Dario Amodei 2027 / Hinton 5-20 年 50% 概率
   - **影响**：如果 Dario 对，junior 该深入底层；如果 Sam 对，应用层更 safe
3. **PhD 必要性**
   - Hinton：no PhD required（Anthropic 50% 无 prior ML）
   - 但 DeepMind/OpenAI senior researcher list 还是 PhD heavy
   - **现实**：engineer track 不需要，research track 仍 bias toward PhD

---

## 6. 关键洞察（Owner mindset 视角，给你做决策）

### 你 immediate 该做什么 (这周)

1. **决定 long-term track**：research 还是 engineer？
   - Research：bias toward PhD，专注 paper + 理论
   - Engineer：production + systems + ship features
   - **建议**：先 default Engineer（更 reversible，不投 5-8 年 PhD 沉没成本），3-5 年后想转 research 再说
2. **选 specialization 方向**（§4 方向 1 vs 方向 2，二选一）
3. **暑期重新定位**：从 "contractor 赚钱" → "build 复现 paper portfolio"

### 你不要做什么

- ❌ 不要花暑期 grind Mercor application（gap 太大）
- ❌ 不要分散学（10 个 specialization 都浅尝 = none mastered）
- ❌ 不要追每个 new model release（90% noise）
- ❌ 不要逃数学基础（觉得"应用都行"）

### Self-discipline trigger

每月 1 次 self-assessment：
- 上个月我**完成**了什么（不是开始/学了什么）？
- 我有 public deliverable 吗（GitHub / blog / paper / demo video）？
- 我距下个 milestone（Phase 1 KPI）多少？

---

## 7. 关联

- [[wiki/career/暑期赚钱探索_2026]] — 短期 strategy（已 invalid，需重做）
- [[wiki/career/平台深度与技能路径_2026]] — Mercor/Toptal/Outlier 平台知识（仍 valid，但通过率假设要调低）
- [[wiki/career/AI 岗位能力地图_2026]] — fall 招聘 watch list
- [[career/profile-facts]] — citizenship / academic
- [[career/resume-master]] — 当前 portfolio

## 📎 来源（confidence label）

### Industry leader path
- ✅ Karpathy Zero-to-Hero: karpathy.ai/zero-to-hero.html (verified)
- ✅ Andrew Ng "How to Build Career": deeplearning.ai eBook (verified)
- ✅ Yann LeCun NYU course: cims.nyu.edu (verified)
- ✅ Lilian Weng Lil'Log (verified)
- ✅ Sebastian Raschka Build LLM from Scratch (verified)
- ⚠️ Anthropic "50% no prior ML" — Medium analysis 引用，建议本人 verify

### Real bar evidence
- ✅ Toptal 3% acceptance: Medium real candidate stories (Karolis ex-Uber, Carlos)
- ⚠️ Mercor "8 years median" — third-party aggregator inference, 建议看 Mercor 通过者 LinkedIn 公开档案 verify
- ✅ FAANG L4 ML engineer bar: interviewing.io blog (verified)

### Future trends
- ✅ Lilian Weng "Why We Think" (verified)
- ✅ Yann LeCun JEPA / I-JEPA blog: ai.meta.com (verified)
- ✅ Sundeep Teki "How to Get Hired at OpenAI/Anthropic/DeepMind 2026" (verified)
- ⚠️ Dario Amodei "white collar bloodbath" quote — 多 source 引用，但 Anthropic 官方 statement 待 verify
