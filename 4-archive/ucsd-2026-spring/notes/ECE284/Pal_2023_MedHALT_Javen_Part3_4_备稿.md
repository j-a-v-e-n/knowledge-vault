---
title: "Med-HALT — Javen 的 Part 3 + Part 4 备稿（5 min on-stage）"
type: source
tags: [ECE284, LLM, 医疗AI, 幻觉评测, EMNLP2023, presentation, Javen 部分]
sources: [raw/AI/Med-HALT_Pal_2023/Pal_2023_MedHALT.pdf]
created: 2026-05-11
updated: 2026-05-11
priority: active
confidence: high
---

# Med-HALT — Javen 的 Part 3 + Part 4 备稿

> **你上台讲什么**：6 张 slides (Slide 9-14)，**约 5 min** —— 3 min Part 3 (Results) + 2 min Part 4 (Discussion / Limitations)。
> **本文件目的**：working doc，逐 slide 给口播稿 + transition + Q&A + 5-min emergency drill。可以用 voice 改任何段，咱们 iterate。
>
> **相关文件**：[[Pal_2023_MedHALT_演讲稿]]（含 Yixian Part 1+2，4 段 outline）/ [[Pal_2023_MedHALT_深度讲解]]（704 行知识深度版）/ [[Pal_2023_MedHALT]]（结构化 source 页）

**emoji 标注**（沿用深度讲解习惯）：
- **📄** = paper 原话 / 数字 / 论断 → 可以 attribute "Pal et al. report..."
- **💡** = 我的扩展（推论 / 类比 / framing） → 引用 "My understanding is..."

---

## 📐 设计原则（Javen 5/11 决定 — 整个备稿都按这个走）

> **PPT 是中心，演讲是辅助**。不是"我在台上讲故事 + PPT 放点配图"，是"听众主要看 PPT 接收信息 + 我在旁边补强调和类比"。

**PPT 上应该有的**：
- 重要数字（直接打出 72% → 11% 这种对比）
- 关键术语 + 一句话定义（Base vs Chat 直接对位写清楚）
- 视觉对比（箭头 / 颜色 / 排版让重点跳出来）
- 主要 finding 的一句话标题

**口播应该做的**：
- 指引方向（"surprise 1 → 2 → 3"）
- 强调 PPT 上的关键点（用手指/激光笔指）
- **补充 PPT 没写的**——主要是**我的类比 + 我的 take**（"think of it like a customer service agent..."）
- 留 1-2 秒空白让听众看 PPT

**口播不应该做的**：
- ❌ 把 PPT 上写的东西**逐字念一遍**（浪费时间 + 听众觉得啰嗦）
- ❌ 长 narrative 段（"So we've seen what they test, and how they test it, and now let's see what they found..."）
- ❌ 学术装逼风（"Let me walk through each finding in detail..."）

**判断 standard**：每张 slide 我口播之后，问自己——**如果我啥都不说，听众光看 PPT 能不能懂 80%？** 能 → PPT 设计 OK，我口播只补强调和类比；不能 → PPT 还得加东西，不要靠口播 carry。

---

## ⏱ 整体时间分配（自己计时 — 已 ×1.6 buffer）

> **⚠️ 时间校准（Javen 5/11 反馈）**：第一版我估的时间太乐观——新手 presenter 现场会下意识 slow down 让听众跟上，实际比照稿念慢 50-80%。本表已乘 1.6 倍 buffer。

```
00:00 ── Yixian 讲完 Slide 8 (Dataset)，直接切 Slide 9
00:00 ── Slide 9   Three Surprises overview ──────┤ 20 sec  (口播指引)
00:20 ── Slide 10  Surprise 1 IT-Paradox ─────────┤ 50 sec  (+ 金牌客服类比)
01:10 ── Slide 11  Surprise 2 Reasoning≠Memory ───┤ 40 sec
01:50 ── Slide 12  Surprise 3 FCT 全军覆没 ───────┤ 50 sec  (+ confirmation bias amplifier)
02:40 ── Part 3 → Part 4 transition ──────────────┤ 5 sec
02:45 ── Slide 13  Clinical Implications ─────────┤ 45 sec  (+ augmentation not automation)
03:30 ── Slide 14  Limitations + Open Q ──────────┤ 50 sec  (左 paper / 右 my)
04:20 ── 收尾 transition ─────────────────────────┘ 5 sec
─────────────────────────────────────────────
总共 ≈ 4:25 — 留 5+ min 给 discussion facilitation
```

**为什么这个节奏好**：原 syllabus 说"7-10 min presentation + facilitate discussion"。Yixian 4-5 min + 你 4-5 min = 共 ~9 min，留 11 min discussion。Engagement / Discussion 评分占 20%+20% — 给讨论留时间反而 grade 高。

---

## 🎬 接手 Yixian（Javen 5/11 决定：不要长 transition，直接上 Slide 9）

**Yixian 讲完 Slide 8 之后**：你直接站起来 / 接 mic / 翻到 Slide 9。**不要**说"Thanks Yixian, so we've seen..."——浪费时间。

**最多 5-8 秒站位 + 一句话开场**：
> "OK so now let's look at what they actually found."

然后立刻进 Slide 9 内容。

---

## 📊 Slide 9 — "Three Surprises from the Leaderboard"

> ⚠️ **关于 visual**：paper page 8 是 Table 2 + Table 3 两个大数字表，**不是单一图**——所以你和 Yixian 在 Google Slides 上**自己做简化版对比表**（不能直接 screenshot paper）。

### Slide 9 PPT 上要放的东西

**(a) 左侧 — 简化版 leaderboard 表**（5 行不要更多）：

| Model | RHT Avg | MHT Avg |
|---|---|---|
| **LLaMA-2 70B Base** | **72.33%** ⭐ | 8.04% |
| LLaMA-2 70B **Chat** | **11.26%** ❌ | 13.05% |
| Text-Davinci-003 | 54.46% | 19.75% |
| Falcon 40B | 59.09% | **30.36%** ⭐ |
| GPT-3.5 Turbo | 44.48% | 19.96% |

**(b) 右侧 — RHT / MHT 全称小字 recap**（防止同学忘了 Yixian Part 2 讲过的）：

```
RHT = Reasoning Hallucination Test
  → 3 tasks: FCT / NOTA / FQT
  → 测推理时被骗 / 被坑

MHT = Memory Hallucination Test
  → 4 tasks: PubMed retrieval
  → 测能不能忠实回忆文献
```

**(c) 顶部标题**：*"Three Surprises from the Leaderboard"*

### 📄 口播稿 (20 sec — PPT-centric, 不念 PPT 上的字)

> "OK so this is what they found. (停 1 秒让大家看表) **Three things stand out** — and each gets its own slide. (手指 / 激光笔 highlight ⭐ ❌) Let's go."

(英文约 25 字 ×1.6 ≈ 20 sec 现场)

### 💡 演讲心法

- **不念 RHT/MHT 全称** — PPT (b) 已经写了，听众自己看
- **不念三个 surprise 各自内容** — 后面三张 slide 会展开，这里只 tease
- 用**手指/激光笔指** ⭐ 和 ❌ — 视觉锚点比口播有效
- "Three things stand out" 是唯一需要口头强调的——告诉听众"接下来是 3 张并列的 slides"

---

## 📊 Slide 10 — Surprise 1: Instruction-Tuning Paradox 🥇

### Slide 10 PPT 上要放的东西

**(a) 左侧 — 主对比**（big visual impact）：

```
   LLaMA-2 70B Base  →  RHT 72.33% ⭐
              ↓ + Instruction Tuning + RLHF
   LLaMA-2 70B Chat  →  RHT 11.26%  ❌

   ── 同模型架构，差 61 个百分点 ──
```

**(b) 右上小字 — Base model vs Chat model 到底差啥**（Javen 5/11 加的 — 听众看到 Base / Chat 两个标签不知道差啥，必须 anchor）：

```
LLaMA-2 70B "Base" vs "Chat" — 什么关系？

Base model
  = Pre-training 完就停（互联网海量文本 → 学预测下一个字）
  → 知识丰富，但不会对话、不会听指令

Chat model
  = Base + Instruction Tuning (SFT) + RLHF
  → 学会对话格式 + 用人类打分调成"让人爽"
  → 例: ChatGPT, Claude, Gemini 都是 Chat 形态

⚡ 同一个架构 + 同一个 pre-training，只差最后这两步训练
```

**(c) 引用框**：📄 paper §6.1 — *"There is a detrimental effect on model's ability to control hallucination after instruction tuning and RLHF."*

### 📄💡 口播稿 (50 sec — PPT-centric, 不念 PPT 上的字)

> "Surprise 1. (停 2 秒让大家看 PPT 主对比 + Base vs Chat block)
>
> Same model. Same pre-training. Just adding RLHF — the chat version of LLaMA-2 drops from **72 percent to 11 percent**. The paper calls this 'a detrimental effect of instruction tuning.' (停 1 秒)
>
> [**💡 我的金牌客服类比**] Why? My take — RLHF is **customer service satisfaction training**. Humans rate agreeable answers higher, so the model learns to agree. That's great for casual chat. But in medicine, the user is often a doctor with a **wrong** hypothesis — and an agreeable model just confirms it. The agent is too good at making customers happy."

(英文约 80 字 ×1.6 ≈ 50 sec 现场)

### 💡 演讲心法

- **PPT (b) 已经把 Base vs Chat 写清楚了** — 不要再口头念"Base 是啥 Chat 是啥"，停 2 秒让听众看 PPT 即可
- 数字说"72 percent → 11 percent"**不要说 72.33% / 11.26%** — 口语化，听众记不住小数
- **"金牌客服" 类比是你整场最大记忆点** — 慢一点说，让听众笑 / 点头
- 引用 "detrimental effect" 那句**直接念 paper 原话**——显得严谨，不是你随便说的

### 💡 你自己想出来的"金牌客服"类比 — 这是你的杀手锏

明天教授如果追问 "Why specifically does RLHF hurt?" 你直接讲：

> "Imagine training a customer service agent. RLHF is like satisfaction-score training — it makes her good at making customers happy. But sometimes a happy customer is a wrongly-confirmed customer. In medical Q&A, the model trained this way will agree with a doctor's wrong hypothesis to be 'helpful,' rather than push back. That's the False Confidence failure mode."

### Q&A 预备 (Surprise 1)

| 同学/教授可能问 | 你的简答 (15-25 sec) |
|---|---|
| **"Did the paper test if more RLHF makes it even worse?"** | 📄 "Falcon 40B shows the same pattern — Base 59% vs Instruct 52% — but they didn't do a graduated study with varying RLHF intensity. That's a clear follow-up." |
| **"Could you fix this by adding 'I don't know' to RLHF rewards?"** | 💡 "That's actually what I'd argue. The Pointwise scoring of Med-HALT — +1 / −0.25 / 0 for abstention — could be repurposed as a reward function. Use it to RL-fine-tune Base models. Paper hints at it in Discussion, doesn't implement it. Good thesis topic." |
| **"Is this just because Chat models are smaller / different in size?"** | 📄 "No — they compare same-architecture pairs. LLaMA-2 70B Base vs LLaMA-2 70B Chat are identical in size and pre-training. Only RLHF differs." |

---

## 📊 Slide 11 — Surprise 2: Reasoning ≠ Memory 🥈

### Slide 11 PPT 上要放的东西

**(a) 主对比表 — 两个能力分离**：

```
              RHT (推理)        MHT (记忆)
LLaMA-2 70B    72.33% ⭐         8.04%       ← 推理强, 记忆弱
Falcon 40B     59.09%           30.36% ⭐    ← 推理中, 记忆强
```

**(b) 关键 take-away（顶部大字）**:
> **"Reasoning ability ≠ Memory ability — they're independent dimensions"**

**(c) 底部小字 caveat**:
> Side note: open-source (LLaMA / Falcon) beats closed-source (GPT-3.5) on RHT — but mostly because closed models are RLHF'd (Surprise 1 again), not a true "open vs closed" finding.

### 📄💡 口播稿 (40 sec — PPT-centric)

> "Surprise 2. *(停 1 秒看表)* LLaMA-2 is best at reasoning but **worst** at memory recall. Falcon is the opposite. These two skills don't correlate.
>
> [**💡 my take**] My take — a safe medical AI probably can't be one monolithic model. You'd want **modular design** — one model for reasoning, another (or a retrieval system) for fact lookup. No single LLM is good at everything.
>
> *(指底部 caveat)* Quick note — you might also see open-source beating closed on RHT here, but that's mostly Surprise 1 again — the closed models are all RLHF'd. Don't oversell the open-vs-closed angle."

(英文约 65 字 ×1.6 ≈ 40 sec)

### 💡 演讲心法

- **主 finding 是 "Reasoning ≠ Memory"** —— "open vs closed" 是 nuance / caveat，别浪费太多时间
- **手指 highlight 表上的 ⭐ 对角线** — 视觉打动 > 念数字
- "Modular design" 这句**主动 sell 一下**——这是你 critical thinking 的展示

### Q&A 预备 (Surprise 2)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Has GPT-4 fixed the open-vs-closed gap?"** | 📄 "Paper didn't test GPT-4 — it was 2023 — but it's an open question. My guess (💡) is GPT-4 might do better on raw accuracy but still show the IT-Paradox pattern because it's also RLHF'd. Med-HALT-ing GPT-4 / Claude / Gemini is an obvious follow-up." |
| **"Why is Falcon better at MHT specifically?"** | 💡 "Likely because Falcon was trained on RefinedWeb, which is a heavily web-filtered corpus that included more PubMed-style structured medical literature. Pre-training data composition matters." |

---

## 📊 Slide 12 — Surprise 3: FCT 全军覆没 🥉

### Slide 12 PPT 上要放的东西

**(a) 标题大字**: *"FCT — Where Every Model Fails"*

**(b) FCT 排名表**（按分数排序，大字突出）：

```
False Confidence Test (FCT) accuracy:

  LLaMA-2 70B Base    42.21%  (best, still < 50%)
  GPT-3.5 Turbo       34.15%
  Falcon 40B Base     18.66%
  Text-Davinci-003    16.76%
  LLaMA-2 70B Chat    13.34%
  Falcon 40B Instruct  1.11%
```

**(c) 顶部 / 底部红字强调**:
> **🚨 No model passes 50%.**

**(d) 左下角小字 — Recall**:
> "Recall Yixian's Lyme example — that's an FCT instance."
> (可嵌入 `![[Pal_2023_MedHALT_page02_hallucination_example_lyme.png]]` 缩略图)

### 📄💡 口播稿 (50 sec — PPT-centric)

> "Surprise 3 — and this one I think matters most clinically. *(停 1 秒)*
>
> FCT — False Confidence Test — is when you feed the model a wrong suggested answer. **No model passes 50%**. Even the best, LLaMA-2 70B Base, only gets 42. Text-Davinci, 17 percent — gets bullied 5 out of 6 times. *(停 1 秒)*
>
> [**💡 my take**] Why this matters — this is the **most realistic clinical scenario**. Patients don't ask 'what's wrong with me?' — they ask **'I think I have X, right?'** Interns ask 'is the treatment X, right?' Textbooks confidently state outdated info. *(停 1 秒)*
>
> Every time, the model faces a **confident wrong suggestion** and caves. So the failure isn't 'LLM doesn't know medicine.' It's **'LLM amplifies the human's wrong assumption.'** That's a confirmation bias amplifier — uniquely dangerous in medicine."

(英文约 110 字 ×1.6 ≈ 50 sec)

### 💡 演讲心法

- **"No model passes 50%"** 是这页**最大记忆点**——慢一点说，重复一次
- "I think I have X, right?" 用**轻微病人语气**说——演技加分
- **"LLM amplifies the human's wrong assumption"** 是你的 punch line——慢一点

### Q&A 预备 (Surprise 3)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Is 42% on FCT really that bad? Random guess is 25%."** | 📄 "Fair point — random on 4 options is 25%, so 42% is above chance. But the scoring is +1 / −0.25 — getting many wrong actively **subtracts** from your score. LLaMA-2 70B Base FCT **Pointwise Score** drops to **8.9** despite 42% accuracy. Per the paper's own framing, even the best model fails the *honesty test*, not just the accuracy test." |
| **"Couldn't you just prompt-engineer this away — 'don't agree with the user blindly'?"** | 💡 "You could try — but the paper also shows **prompt brittleness** (their Variant 0/1/2 study). Small wording changes shift accuracy by 1-3%. Real patients don't write benchmark-style prompts; they ask in their own words. So prompt engineering doesn't survive deployment. Need to fix it at the training level, not the prompt level." |
| **"Does this happen with humans too — confirmation bias?"** | 💡 "Yes — that's well-established in clinical psychology. The worry here is that LLMs **amplify** rather than counterbalance human cognitive biases. A good consult should challenge bad hypotheses; the current LLM design rewards agreement. So it makes the human-AI system worse than human alone." |

---

## 🔀 Part 3 → Part 4 Transition (5 sec)

> "So — what does this mean for actually deploying these?"

(直接切到 Slide 13，不要 recap 三个 surprise — PPT 上已经讲过)

---

## 📊 Slide 13 — Clinical Implications

### Slide 13 PPT 上要放的东西

**(a) 标题大字**: *"Can we deploy this in hospitals?"*

**(b) Scorecard table（4 行，颜色突出 ❌ vs ✅）**:

|     | What                                         | Why                                    |
| --- | -------------------------------------------- | -------------------------------------- |
| ❌   | Autonomous diagnosis / treatment             | Best model only 72% RHT, FCT under 50% |
| ❌   | RLHF chat models for medical Q&A             | Instruction-Tuning Paradox (Chat: 11%) |
| ✅   | Assist literature search (with verification) | Falcon 30% MHT — limited but useful    |
| ✅   | Physician second-opinion                     | Doctor must be in the loop             |

**(c) 底部大字 punch line**:
> **🩺 Augmentation, not Automation**

### 💡 口播稿 (45 sec — PPT-centric)

> "So can we put these in hospitals today? *(停 1 秒看表)*
>
> **Two things LLMs cannot do**: autonomous diagnosis — best model misses 28% — and — you can't just plug in ChatGPT, because RLHF makes it more agreeable, not more honest.
>
> **Two things LLMs can do**: literature search as a first-pass tool, and second-opinion where a doctor verifies the output. *(停 1 秒)*
>
> [**💡 my framing**] The takeaway I want to leave you with — LLMs in medicine should be **augmentation, not automation**. They make doctors faster. They don't replace doctor judgment. The hype about 'AI replacing doctors' is the opposite of what this paper supports."

(英文约 90 字 ×1.6 ≈ 45 sec)

### 💡 演讲心法

- **手指 ❌ ❌ ✅ ✅ 四行** — 视觉打动比念字快
- "**Augmentation, not automation**" 是**整场 Part 4 punch line** — 慢一点说，停顿，让大家记住
- 不要 over-elaborate ✅✅ — PPT 已经写了 "with verification" "doctor in loop"，不需要重复

### Q&A 预备 (Slide 13)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Med-PaLM 2 claims 86% on MedQA — is it deployable per your scorecard?"** | 💡 "Great question. MedQA tests **capability** — can the model answer correctly. Med-HALT tests **honesty** — does the model know when it doesn't know. Med-PaLM 2 hasn't been Med-HALT-ed. So 86% on MedQA is consistent with potentially being bad on FCT. We just don't know. Open question." |
| **"What about RAG? Med-PaLM 2 uses retrieval."** | 💡 "RAG addresses MHT — fact lookup — and probably makes the 4 PubMed tasks trivial. But RAG doesn't directly address FCT, because FCT is a reasoning robustness test against bad suggestions. You can retrieve perfect docs and still cave to a confidently-wrong prompt. The two failure modes need different mitigations." |

---

## 📊 Slide 14 — Limitations & Open Questions

### Slide 14 PPT 上要放的东西

**两栏对照设计** —— 左栏 paper 承认的，右栏 Javen 加的批评：

```
┌─ 📄 Paper 承认的局限 ────────┬─ 💡 My open questions ─────────┐
│                              │                                │
│ 1. MCQ ≠ free-form clinical  │ 5. IT-Paradox: paper shows     │
│    Q&A                       │    "what" not "why" — needs    │
│                              │    ablation                    │
│ 2. Only 7 tasks (no planning,│                                │
│    no long-context, no       │ 6. Med-PaLM 2 (Singhal 2025)   │
│    multimodal)               │    NOT Med-HALT-ed — gap       │
│                              │                                │
│ 3. Prompt brittleness shown  │ 7. Pointwise Score (+1/-0.25/0)│
│    but not solved            │    → RLHF reward function?     │
│                              │    (train honest LLMs)         │
│ 4. GPT-4 / Claude not tested │                                │
│    (publication timing)      │                                │
│                              │                                │
└──────────────────────────────┴────────────────────────────────┘
```

### 📄💡 口播稿 (50 sec — PPT-centric)

> "Final slide. *(停 1 秒指左栏)* The paper acknowledges four limitations — MCQ isn't real clinical Q&A, only 7 tasks, prompt brittleness unsolved, and GPT-4 wasn't tested.
>
> *(指右栏)* But reading critically, I think there are **three more open questions** worth raising.
>
> **One** — the IT-Paradox is the biggest finding, but the paper shows '**what**' not '**why**.' Could be sycophancy, could be knowledge suppression, could be distribution shift. Each implies a different fix. We don't know.
>
> **Two** — Med-PaLM 2 from Singhal 2025 claims 86% on MedQA, but **nobody has Med-HALT-ed it**. Clear research gap.
>
> **Three** — the Pointwise scoring could be **repurposed as a reward function** to RL-fine-tune base models for honesty. The paper hints at it; nobody's done it yet. Most actionable follow-up."

(英文约 95 字 ×1.6 ≈ 50 sec)

### 💡 演讲心法

- **左右栏对比 visual** 比 "paper 4 个 + 我加 3 个" 文字列表强 — 听众一眼看到"paper 说的"和"你加的"分离
- "Three more open questions" 是 critical reading 展示——**慢一点过 3 条**，每条 1 句话即可
- 第三条 **"reward function for honesty"** 是你最 sellable 的 follow-up——明天 oral assessment 可能被点这个

### Q&A 预备 (Slide 14)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Which limitation worries you most for clinical deployment?"** | 💡 "Prompt brittleness — limitation #3. Real patients don't use benchmark-style prompts; they ramble. If 1-3% accuracy drop comes from rewording, deployment stability is in question. The paper shows the problem but offers no mitigation." |
| **"Why hasn't anyone Med-HALT-ed Med-PaLM 2?"** | 💡 "Probably because Med-PaLM 2 wasn't released as an open API — Google kept it internal — and the Med-HALT authors are a separate group (Saama AI Research). A natural follow-up paper would be a third party running both benchmarks on both systems. Would be valuable." |
| **"Is the −0.25 penalty too lenient? In oncology, a wrong answer kills."** | 💡 "Excellent point — that's actually a deeper critique of the scoring. **Risk-weighted scoring** — say −10 for oncology vs −0.5 for dermatology — would be more clinically aligned. But the weighting is a **governance** problem, not an ML problem — who decides risk weights? Paper doesn't engage with that complexity." |

---

## 🔚 收尾 Transition (5 sec)

> "Pass medical exams ≠ safe to deploy. **Let's discuss.**"

(直接切到 discussion 阶段 — 别 over-explain)

---

## 💬 Discussion Facilitation (你 lead 哪些)

跟 Yixian 还没分完 4 个 question — 我推荐你 lead **Q1a + Q3a**（这两个对应 Part 3+4 内容，连贯）：

### Q1a (你 lead) — Clinical relevance

> "If you were the CMO of a hospital deciding whether to deploy an LLM for **physician second-opinion in radiology**, which finding from this paper would worry you the **most** — the 16.76% FCT score on Text-Davinci, the Llama-2 Chat collapse, or the prompt brittleness? Why **that one** specifically?"

**怎么 facilitate**：
- 等一两秒看谁举手 / 主动说
- 没人回 → 点名："John, what do you think?"
- 听到回答 → **follow up**："Why **specifically** that one? What about the others?"
- 引到其他角度："Anyone disagree? What if you're a primary care doctor instead of radiologist?"

### Q3a (你 lead) — Technical extension

> "The Instruction-Tuning Paradox is the most surprising finding — RLHF makes the chat model **worse** at hallucination control. If you had a research budget, would you (a) try to fix RLHF with a 'honesty reward,' (b) skip RLHF entirely for medical models, or (c) do a 2-stage training (RLHF for conversation + adversarial fine-tune for honesty)? Defend your choice."

**怎么 facilitate**：
- 这题 ML-heavy — 工程类同学会想答
- 听到选项后追问 "Why not the other two? What's the trade-off?"
- 如果讨论冷场，主动给一个 thinking aloud："I lean toward option (c) because RLHF is good for general conversation, you don't want to throw the baby out with the bathwater. But that's just my intuition."

---

## 🚨 上场前 5 分钟 emergency drill

**Cmd+O 打开本文件 → 滚到这里 → 念以下 5 件事各 1 遍**：

1. **5 个数字**（深度讲解 §6.1 复用）:
   - LLaMA-2 70B Base → Chat: **72.33% → 11.26%** (drop 61 pts)
   - Best FCT score: **42.21%** (LLaMA-2 70B Base, still under 50%)
   - LLaMA-2 70B Base / Chat Pointwise Score: **86.32 / −10.32**
   - Falcon 40B MHT avg: **30.36%** (best across all models)
   - GPT-3.5 zero-shot: **7.31%** (essentially random)

2. **三个 Surprise 一句话各**：
   - Surprise 1: RLHF **collapses** hallucination control (61-point drop in same architecture)
   - Surprise 2: Open-source **beats** closed-source on RHT; reasoning and memory **decouple**
   - Surprise 3: **No model passes FCT** — universal sycophancy failure

3. **3 个 implication 一句话各**：
   - Clinical: **augmentation, not automation**
   - Architecture: probably **modular** (LLaMA reason + Falcon recall + RAG fact-check)
   - Training: **Pointwise Score as reward function** is the obvious follow-up

4. **2 个杀手锏类比**（你自己想出来的，直接用）：
   - "RLHF 是**金牌客服培训** — 让客服讨客户喜欢，但客户喜欢的回答可能是错的"
   - "FCT 失效 = LLM **放大医生的错误诊断**，不是补充医生 — 是 confirmation bias amplifier"

5. **被问"paper 没说你怎么知道"时的标准 phrasing**：
   - ✅ "My understanding is..." / "Reading critically, I think..." / "Paper doesn't say explicitly, but my interpretation is..."
   - ❌ "Paper says..." (when it doesn't)

---

## 📎 来源 attribution（明天有任何 attribution 不确定查这里）

| 你讲的 claim | Attribution |
|---|---|
| 全部 RHT / MHT 数字 (72%, 11%, 42%, etc.) | 📄 Pal et al. (2023) Tables 2-3 |
| "Detrimental effect after RLHF" 引用 | 📄 Pal et al. §6.1 直接 quote |
| Lyme 例子 / Tetracycline 错答 | 📄 Pal et al. Figure 2 |
| 三个 RLHF 机制假说 (sycophancy / suppression / distribution) | 💡 我加的扩展，paper 没拆机制 |
| "金牌客服" / "customer service agent" 类比 | 💡 我自己的类比 |
| "Modular architecture" 建议 (LLaMA + Falcon) | 💡 我的推论 |
| Med-PaLM 2 比较 / "hasn't been Med-HALT-ed" | 💡 我从 vault 其他笔记 link，paper 没引 Med-PaLM 2 |
| "Pointwise Score as reward function" | 💡 paper Discussion 暗示，4 步操作是我加的 |
| "Augmentation not automation" | 💡 我的 framing，paper §7 只笼统说 auxiliary use |
| 论文承认的 4 个 limitation | 📄 Pal et al. §7 |
| 我加的 3 个额外 limitation | 💡 critical reading |
| Risk-weighted scoring critique | 💡 我的 critique，paper 没讨论 |

---

## 🎤 跟 Yixian 同步事项（今晚要做）

1. 提醒她 **Slide 8 USMLE / TWMLE 数字反了**（演讲稿 line 47 已记，正确是 USMLE=2,482 / TWMLE=2,801）
2. 确认她做 Slides 1-8，你做 9-14，**共 14 张** — UCSD 模板里多的删掉
3. 商量 4 个 discussion questions 分工 —— 我推荐你 lead Q1a + Q3a（理由见上方 Discussion Facilitation section）
4. （可选）跟她 dry-run 一遍 Yixian → Javen 的 hand-off (Slide 8 → Slide 9) — 衔接顺不顺
