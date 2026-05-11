---
title: "Med-HALT: Medical Domain Hallucination Test — ECE284 Week 7 演讲稿"
type: source
tags: [ECE284, LLM, 医疗AI, 幻觉评测, EMNLP2023, presentation]
sources: [raw/AI/Med-HALT_Pal_2023/Pal_2023_MedHALT.pdf]
created: 2026-05-11
updated: 2026-05-11
priority: active
confidence: high
---

# Med-HALT — ECE284 Week 7 演讲稿（Co-lead with Yixian Wang）

> **演讲日期**: 2026-05-12 周二 ECE284 Tu/Th 11:00-12:20 EBU1 2315
> **演讲时长**: 7-10 分钟 presentation + facilitate discussion (20 min total)
> **论文**: Pal A., Umapathi L.K., Sankarasubbu M. "Med-HALT: Medical Domain Hallucination Test for Large Language Models." *EMNLP 2023 / CoNLL*. arXiv:2307.15343
> **第 2 次 primary lead**（第 1 次 Week 2 是 [[Perez_2019_AppleHeartStudy_演讲稿]] Apple Heart Study）
> **分工**: Yixian = Part 1 + 2（Slides 1-8 完成）；Javen = **Part 3 (Results) + Part 4 (Discussion / Limitations)** + facilitating 部分 discussion questions
> **底层 source**: [[Pal_2023_MedHALT]]（完整 source 页，含全部数据表和图）

---

## 🎤 演讲 4 段（按 syllabus 要求）

### Part 1 — Problem & Motivation (Yixian, ~1.5 min)

*Yixian 已做 Slides 1-4：*

1. **Slide 1**: Title / 作者 / Saama AI Research
2. **Slide 2**: The Stakes — LLMs 进医疗的三层（Adoption / Hallucination / High Stakes）
3. **Slide 3**: What does medical hallucination look like? — Lyme 病 + 孕妇案例（GPT-3.5 错答 Tetracycline vs Physician 正确 Amoxicillin）
4. **Slide 4**: The GAP — 之前 benchmark 缺什么（4 点）

**Yixian 讲完时听众应该懂的核心点**：医疗 hallucination 是 life-or-death 问题，需要专门 benchmark；通用 hallucination benchmark 不能直接用。

---

### Part 2 — Technical Approach (Yixian, ~2.5 min)

*Yixian 已做 Slides 5-8：*

5. **Slide 5**: Framework overview — RHT + MHT 两类 7 个 task + Scoring (+1 / −0.25 / 0)
6. **Slide 6**: RHT 详细 — FCT / NOTA / FQT 各自挖坑方式
7. **Slide 7**: MHT 详细 — 4 个 PubMed 检索 task + 假 PMID 陷阱
8. **Slide 8**: Dataset — 多国医考分布（India 9,515 / Spain 4,068 / **USMLE 2,482** / **TWMLE 2,801**）

⚠️ **Slide 8 注意提醒 Yixian 改数字**：她目前写的 USMLE=2,801, TWMLE=2,482 数字反了。论文 Table 1 原文：USMLE=2,482, TWMLE=2,801。被问到时如果照搬错的数会被 challenge。

**Yixian 讲完时听众应该懂的核心点**：Med-HALT 的"挖坑式"任务设计 + Pointwise Score 奖励诚实的核心机制 + 数据集多国设计的意义。

---

### Part 3 — Key Results (Javen, ~3 min) ⭐

**讲 Result 的核心策略**：不要把表照搬念数字。挑 **3 个反直觉发现**做 Story。每个发现配一张图。

#### Slide 9 (Javen 新做): "Three Surprises from the Leaderboard"

**Opening hook（30 秒）**:
> "假设你要把一个 LLM 放进医疗 pipeline，你会选哪个？GPT-3.5？Text-Davinci？还是开源 LLaMA-2？这篇论文的结果可能颠覆你的直觉。我挑了三个最反直觉的发现讲。"

放：简化版 leaderboard 表（嵌入 `![[Pal_2023_MedHALT_page08_main_results_RHT_MHT.png]]` 或重画干净版）：

| Model | RHT Avg Acc | MHT Avg Acc |
|---|---|---|
| **LLaMA-2 70B Base** | **72.33%** ⭐ | 8.04% |
| LLaMA-2 70B Chat | 11.26% ❌ | 13.05% |
| Text-Davinci-003 | 54.46% | 19.75% |
| Falcon 40B | 59.09% | **30.36%** ⭐ |
| GPT-3.5 Turbo | 44.48% | 19.96% |

#### Slide 10 (Javen 新做): "Surprise 1 — Instruction-Tuning Paradox" 🥇

**讲故事（约 60 秒）**:
> "LLaMA-2 70B Base 拿了 RHT 全场最高 72.33%——把它做 RLHF / instruction-tuning 变成 Chat 版后，**同模型 acc 掉到 11.26%**。差 61 个百分点。Falcon 40B Base 也是同样模式（59% → 52%）。论文 §6.1 直接说：'There is a detrimental effect on model's ability to control hallucination after instruction tuning and RLHF.'"

**为什么这很重要**:
- 我们日常用的 ChatGPT / Claude 都是 RLHF 后的 chat 模型
- 这说明 **业界主流"对齐"路径反而让 LLM 在医疗 hallucination 控制上更差**
- 不是更"对齐"，是更"善于硬答"

**Discussion hook（给后面留题）**: 为什么会这样？

#### Slide 11 (Javen 新做): "Surprise 2 — 闭源 ≠ 更强 + Capability ≠ Honesty Trade-off" 🥈

**两个小发现合一页**:

(a) **闭源不一定更强**: GPT-3.5 (44.48%) < Text-Davinci (54.46%) < LLaMA-2 70B Base (72.33%)。这是 2023 年——可能数据有变，但当时**最强的医疗 reasoner 是开源模型**。

(b) **Reasoning 强 ≠ Memory 强**:
- LLaMA-2 70B: RHT 第一 72.33%，但 MHT 倒数 8.04%
- Falcon 40B: RHT 中等 59%，但 MHT 第一 30.36%

放：嵌入 `![[Pal_2023_MedHALT_page08_main_results_RHT_MHT.png]]` 局部 highlight 两组数字。

**意义**: LLM 的"推理能力"和"事实记忆能力"是**分离的**——评 LLM 不能只看综合分。

#### Slide 12 (Javen 新做): "Surprise 3 — FCT 全军覆没" 🥉

**讲故事（约 60 秒）**:
> "False Confidence Test 是把'建议错答案'喂给模型——这是临床里太常见的情境，病人或实习医生带着先入印象问。**所有模型 FCT 都低于 50%**——最强的 LLaMA-2 70B Base 也只有 42.21%。Text-Davinci 在 FCT 上只有 16.76%。这意味着**LLM 在医疗 context 里特别容易被错误暗示带偏**——不是它不懂，是它'太给面子'。"

放：嵌入 `![[Pal_2023_MedHALT_page02_hallucination_example_lyme.png]]` 提醒 Yixian 已经讲过的 Lyme 例子——再放一次强化"FCT 不是抽象问题，就是 Lyme 那种"。

**Javen Part 3 讲完时听众应该懂的核心点**: (1) Instruction-tuning 反而让 hallucination 控制更差；(2) Reasoning 和 Memory 是分离能力；(3) FCT 是 LLM 医疗最危险的失效模式。

---

### Part 4 — Limitations & Open Questions (Javen, ~2 min) ⭐

#### Slide 13 (Javen 新做): "What This Means — Clinical Implications"

**主要 take-aways（约 60 秒）**:

| 现实含义 | 论文支持 |
|---|---|
| ❌ **不能**自主诊断 / 自主用药建议 | 即便最强 LLaMA-2 70B Base 也只 72% RHT |
| ❌ **不能** RLHF chat 模型上线医疗 | Instruction-tuning Paradox |
| ✅ **能**辅助文献检索 / 假设生成 | MHT 上 Falcon 40B 30% IR accuracy（不高但有用） |
| ✅ **能**作为医生 second-opinion | 必须有医生在 loop 中 |

#### Slide 14 (Javen 新做): "Limitations & Open Questions"

**论文承认的局限（4 条）**:

1. **Multiple choice ≠ 真实临床问答** — 医生在临床上是自由回答，benchmark 是 MCQ
2. **只测 7 个 task** — 未覆盖治疗规划 / 长 context / 影像-文本联合
3. **Prompt brittleness 没解** — 论文展示了问题但没给解决方案
4. **GPT-4 / Claude 当时没测** — 评估对象不含最强闭源模型

**论文没问但应该问的（Javen 想出来的）**:

5. **Instruction-tuning Paradox 因果机制不明** — 是 RLHF 目标问题？还是 chat data 分布问题？需要 ablation
6. **Med-PaLM 2 跨 benchmark gap** — 这种"产品级"医疗 LLM 没被 Med-HALT 测过，是明显研究 gap
7. **Med-HALT 的 Pointwise Score 能否反向变成 reward function** — 用 +1/−0.25/0 训练更诚实的 LLM？

---

## 💬 Discussion Questions (4 类，每类 1-2 个候选，跟 Yixian 商量谁问哪个)

### 1. Clinical / Real-world Relevance

**Q1a** (推荐): If you were the CMO of a hospital deciding whether to deploy an LLM for **physician second-opinion in radiology**, which finding from this paper would worry you the **most** — the 16.76% FCT score on Text-Davinci, the Llama-2 Chat collapse, or the prompt brittleness? Why that one specifically?

**Q1b**: The paper tests on multiple-choice **exam questions** from USMLE / AIIMS / etc. But real clinical conversation is **free-form**. Would you expect models to perform **better or worse** on free-form medical Q&A vs MCQ? What evidence in the paper supports your guess?

### 2. Methodological Critique

**Q2a** (推荐): The Pointwise Score (+1 / −0.25 / 0) is borrowed from medical exam scoring. But −0.25 is fixed — what if a wrong answer in oncology is **1000x more dangerous** than a wrong answer in dermatology? Should the scoring be **risk-weighted**, and if so, who decides the weights?

**Q2b**: The Fake Questions Test uses "land of undead + mermaid" style absurd prompts. Are these really testing **medical hallucination**, or just testing whether the model recognizes obviously **non-medical** language? If a researcher constructed *plausible-sounding but fictional* medical scenarios (e.g., "Janus syndrome with reverse hepatic conjugation"), would the test be more honest?

### 3. Technical Extension

**Q3a** (推荐): The **Instruction-Tuning Paradox** is the most surprising finding — RLHF makes the chat model **worse** at hallucination control. If you had a research budget, would you (a) try to fix RLHF with a "honesty reward," (b) skip RLHF entirely for medical models, or (c) do a 2-stage training (RLHF for conversation + adversarial fine-tune for honesty)? Defend your choice.

**Q3b**: Med-HALT's MHT requires the model to say "Unknown" when given a **fake PMID**. But the model never sees PubMed at inference time — it relies on **memorized facts**. Would RAG (retrieval-augmented generation, like Med-PaLM 2's chain of retrieval) make this test **trivial** to pass? If yes, is MHT actually a good benchmark for production systems?

### 4. Broader Implications

**Q4a** (推荐): Connect this paper to [[Obermeyer_2019_医疗算法种族偏见]] — both reveal that **a medical AI passing surface metrics doesn't mean it's safe**. Obermeyer's algorithm passed accuracy benchmarks but encoded racial bias through proxy targets. Med-HALT shows MedQA accuracy doesn't mean hallucination safety. **What's the structural pattern?** And what would a "Med-HALT for fairness" look like?

**Q4b**: If we accept that Med-HALT scoring (rewarding "I don't know") is **the right direction**, what does this mean for the **FDA approval process** for medical LLMs? Should there be a regulatory requirement that medical-grade LLMs **demonstrate calibrated abstention** before deployment, similar to how diagnostic devices need clinical validation?

---

## 🎬 演讲流程指南 (给 Javen)

### 演讲前准备 (周一晚 / 周二早)

1. **跟 Yixian 同步**:
   - 提醒 Slide 8 USMLE/TWMLE 数字反了，让她改
   - 确认她做 Slides 1-8，你做 9-14，**总共 14 张 slides（不是 26 张）—— 剩下 12 张 UCSD 模板要删除**
   - 商量 4 个 discussion questions 各负责问哪个

2. **熟悉 source 页**: [[Pal_2023_MedHALT]] 完整数据表 + 5 张渲染好的图全部在 `attachments/AI/`

3. **预演 Part 3+4**: 实际计时 5 分钟（3 min Results + 2 min Discussion 部分），确保不超时

### 演讲当天

- **演讲时长**: 总共 7-10 分钟，你的部分约 5 分钟
- **Engagement 评分占 20%**: 不只念稿，跟听众有眼神交流；问引导问题（"think about this — why would RLHF make things worse?"）
- **Discussion 评分占 20%**: 不是问完就完事，要 follow up — 听众回答后追问"why specifically that one?"

### Primary Oral Assessment (演讲后 / Week 6 截止)

- 单独的 oral assessment 占 30%，会**深挖**论文细节
- **预期会被问的**:
  - Instruction-tuning paradox 的可能机制（论文没给）— 准备 ablation 方案
  - 7 个 task 哪个最不可信 / 最严格 — 准备你的判断 + 理由
  - 如果让你扩展这个 benchmark 你会加什么 task — 准备 specific 候选
  - 跟其他 ECE284 papers 的 connection — 至少能讲清 Obermeyer 的 structural similarity
- **不能用 AI / 笔记** during oral assessment — 提前内化

---

## 📎 来源 & 关联

- [[Pal_2023_MedHALT]] — 完整 source 页（数据 / 公式 / 推理类型分布 / 全部跨页面联系）
- `raw/AI/Med-HALT_Pal_2023/Pal_2023_MedHALT.pdf` — 论文原文
- `raw/ucsd/Spring 2026/ECE284/Singhal_2025_MedPaLM2.pdf` — Med-PaLM 2 (Singhal 2025 Nature Medicine)，Week 7 的另一篇 reading（你**不** lead，但需要 read for oral assessment）
- [[LLM 医疗评测]] — concept 页，把 Med-HALT (诚实度评测) 和 Med-PaLM 2 (能力评测) 串起来
- [[Obermeyer_2019_医疗算法种族偏见]] — discussion Q4a 的对比对象
- [[Perez_2019_AppleHeartStudy_演讲稿]] — 你 Week 2 第 1 次 primary lead 的演讲稿（格式参考）

## 🔗 Yixian 共享的 Google Slides

https://docs.google.com/presentation/d/1OaDtrYwdM6FHO1KfbRfA-FvFD7NgMeqV2hjqUFxYedc/edit?usp=sharing
