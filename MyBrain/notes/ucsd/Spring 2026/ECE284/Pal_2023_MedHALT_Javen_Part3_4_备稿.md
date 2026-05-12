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

## ⏱ 整体时间分配（自己计时）

```
00:00 ── Yixian 讲完 Slide 8 (Dataset)，接到你 ──┐
00:00 ── Slide 9   Opening + Three Surprises ───┤ 25 sec
00:25 ── Slide 10  Surprise 1 IT-Paradox ───────┤ 60 sec
01:25 ── Slide 11  Surprise 2 闭源/分离 ────────┤ 50 sec
02:15 ── Slide 12  Surprise 3 FCT 全军覆没 ─────┤ 55 sec
03:10 ── Part 3 → Part 4 transition ────────────┤ 10 sec
03:20 ── Slide 13  Clinical Implications ───────┤ 60 sec
04:20 ── Slide 14  Limitations + Open Q ────────┤ 50 sec
05:10 ── 收尾 transition 引入 discussion ───────┘ 10 sec
─────────────────────────────────────────────
总共 5:20 — 跟演讲稿"约 5 min"对齐。
```

如果讲快了空 10-15 秒，**别紧张**——直接说一句"any quick thought before discussion?"做缓冲。

---

## 🎬 开场：怎么从 Yixian 接过来

**Yixian 讲完 Slide 8 时听众的状态**：
- 已经懂 medical hallucination 是 life-or-death (Lyme 例子)
- 已经懂 Med-HALT 框架 (RHT 3 task + MHT 4 task + Pointwise scoring)
- 已经知道数据集多国分布
- **但还不知道实验结果！** ← 这就是你接手的钩子

**你开场（站起来 / 切到 Slide 9）**：

> 💡 "Thanks Yixian. So we've seen **what** they test and **how** they test it. Now let's see **what they found** — and frankly, the results are pretty surprising. I'm going to focus on three findings that I think will change how you think about deploying LLMs in healthcare."

(15-20 秒，建立 narrative — 不要罗列数字，先 sell story)

---

## 📊 Slide 9 — "Three Surprises from the Leaderboard"

**Slide 内容**（嵌入 `![[Pal_2023_MedHALT_page08_main_results_RHT_MHT.png]]` 或重画简化表）：

| Model | RHT Avg | MHT Avg |
|---|---|---|
| **LLaMA-2 70B Base** | **72.33%** ⭐ | 8.04% |
| LLaMA-2 70B **Chat** | **11.26%** ❌ | 13.05% |
| Text-Davinci-003 | 54.46% | 19.75% |
| Falcon 40B | 59.09% | **30.36%** ⭐ |
| GPT-3.5 Turbo | 44.48% | 19.96% |

### 📄 口播稿 (25 sec)

> "Quick orientation on this table — Pal et al. evaluated 5 commercial and open-source models on both Reasoning Hallucination Tests and Memory Hallucination Tests. **I'm going to highlight three surprises** — instruction-tuning makes things worse, closed-source doesn't mean stronger, and there's one task where everybody fails. Let me walk through each."

(语速正常约 2 字/sec — 50 字中文 ≈ 25 sec)

### 💡 演讲心法

- **不要念整张表的数字** — 那是 Slide 10/11/12 三个 surprise 的素材。Slide 9 是**预告 + framing**
- **明确说 "I'm going to highlight three surprises"** — 让听众期待 3 个发现，跟着你的 narrative 走

---

## 📊 Slide 10 — Surprise 1: Instruction-Tuning Paradox 🥇

**Slide 内容**：highlight LLaMA-2 70B Base vs Chat 对比 (从 Slide 9 table 拉出来)：

```
LLaMA-2 70B Base  →  RHT 72.33% ⭐
LLaMA-2 70B Chat  →  RHT 11.26%  ❌
                     差 61 个百分点
```

加引用框：📄 paper §6.1: *"There is a detrimental effect on model's ability to control hallucination after instruction tuning and RLHF."*

### 📄💡 口播稿 (60 sec)

> "[**📄 paper 原话**] So here's surprise number 1. Look at LLaMA-2 70B. The **base** version — that's the pre-trained model without any instruction tuning — gets **72%** on RHT, the best in the entire benchmark. The **chat** version of the same model — same architecture, same pre-training, only difference is RLHF and instruction tuning — drops to **11%**. A **61-point** collapse.
>
> The paper directly says — quote — 'there is a detrimental effect on model's ability to control hallucination after instruction tuning and RLHF.'
>
> [**💡 我的扩展 — 用我自己的客服类比**] Why does this happen? My understanding is — RLHF rewards responses that humans **like** more. And humans tend to like responses that agree with them, that sound confident, that don't say 'I don't know.' So the model learns to **always give a confident answer**, even when it should say 'I'm not sure.'
>
> Think of it like training a customer service agent. A great agent is the one who satisfies the customer — but in healthcare, if the customer-doctor relationship is built on the model **agreeing with the doctor's wrong hypothesis**, that's a disaster. The model is too **agreeable** for medicine."

(约 110 字 + 念读引用大概 60 sec)

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

## 📊 Slide 11 — Surprise 2: 闭源 ≠ Stronger + Reasoning ≠ Memory 🥈

**Slide 内容**: 两个 sub-finding 同一页：

**(a) 开源 > 闭源 (on RHT)**
```
LLaMA-2 70B Base  72.33%  (open)
Falcon 40B Base   59.09%  (open)
Text-Davinci      54.46%  (closed, OpenAI)
GPT-3.5 Turbo     44.48%  (closed, OpenAI)
```

**(b) Reasoning vs Memory 能力分离**
```
LLaMA-2 70B:  RHT 72.33% ⭐   MHT 8.04%  ← reasoning 强, memory 弱
Falcon 40B:   RHT 59.09%      MHT 30.36% ⭐ ← reasoning 中, memory 强
```

### 📄💡 口播稿 (50 sec)

> "[**📄**] Surprise 2 has two parts. First — open-source actually beats closed-source on reasoning. LLaMA-2 70B at 72%, Falcon at 59%, then OpenAI's models at 54 and 44. That's counter-intuitive given the perception that closed-source labs have more resources.
>
> [**💡 nuance**] But notice — the closed models we compare here, GPT-3.5 and Text-Davinci, are **all RLHF-trained**, while LLaMA-2 70B Base is **not**. So this is partly the same Instruction-Tuning Paradox, not really 'open vs closed' — it's 'base vs chat.' Don't oversell the open-source angle.
>
> [**📄**] Second part — look at this table. LLaMA-2 70B is **best at RHT** but **worst at MHT**. Falcon 40B is **mid on RHT** but **best on MHT**. So reasoning ability and memory recall are two **independent dimensions**.
>
> [**💡**] My takeaway is — a safe medical AI probably can't be one monolithic LLM. You'd want **modular design** — LLaMA for reasoning, Falcon or a retrieval system for fact lookup."

(约 90 字 ≈ 50 sec)

### 💡 Slide 11 演讲心法

- 这页**信息密度大**，节奏要快，不要 dwell on 数字 — 用手指 highlight 表格上的关键数字
- 主动 disclaim "open vs closed 不是真的 open vs closed" — **这显示 critical reading**，教授很 appreciate

### Q&A 预备 (Surprise 2)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Has GPT-4 fixed the open-vs-closed gap?"** | 📄 "Paper didn't test GPT-4 — it was 2023 — but it's an open question. My guess (💡) is GPT-4 might do better on raw accuracy but still show the IT-Paradox pattern because it's also RLHF'd. Med-HALT-ing GPT-4 / Claude / Gemini is an obvious follow-up." |
| **"Why is Falcon better at MHT specifically?"** | 💡 "Likely because Falcon was trained on RefinedWeb, which is a heavily web-filtered corpus that included more PubMed-style structured medical literature. Pre-training data composition matters." |

---

## 📊 Slide 12 — Surprise 3: FCT 全军覆没 🥉

**Slide 内容**：FCT 排名 + 嵌入 Lyme 例子图 `![[Pal_2023_MedHALT_page02_hallucination_example_lyme.png]]`

```
模型 FCT 准确率（False Confidence Test）:
  LLaMA-2 70B Base    42.21%   (最高, 仍 < 50%)
  GPT-3.5 Turbo       34.15%
  Falcon 40B          18.66%
  Text-Davinci-003    16.76%
  LLaMA-2 70B Chat    13.34%
  Falcon 40B Instruct  1.11%   (最低)
```

> **No model passes 50%** on FCT.

### 📄💡 口播稿 (55 sec)

> "[**📄 + Lyme recall**] Surprise 3 — this one I think is the most clinically important. Remember Yixian's Lyme example earlier? That's a False Confidence Test instance — the model was given a wrong suggested answer (Tetracycline) and asked to confirm.
>
> Across the **entire benchmark**, **no model passes 50%** on FCT. The best — LLaMA-2 70B Base — only gets **42%**. Text-Davinci is at **16.76%**, meaning 5 out of 6 times it gets bullied into agreeing with the wrong suggestion.
>
> [**💡 临床 implication — 我自己的洞察**] Why does this matter so much? Because **FCT is the most realistic clinical scenario**. Real patients don't ask 'what's wrong with me?' — they ask 'I think I have X, right?' Real interns don't ask 'what's the treatment?' — they ask 'is the treatment X?' Real textbooks say 'X is first-line therapy' — even when the textbook is outdated.
>
> In each case, the LLM faces a confident wrong suggestion. And the paper shows: **LLMs almost always cave**. So the failure mode isn't 'LLM doesn't know medicine' — it's '**LLM amplifies the human's wrong assumption**.' That's a uniquely dangerous failure in medicine because it makes diagnostic confirmation bias worse, not better."

(约 105 字 ≈ 55 sec)

### Q&A 预备 (Surprise 3)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Is 42% on FCT really that bad? Random guess is 25%."** | 📄 "Fair point — random on 4 options is 25%, so 42% is above chance. But the scoring is +1 / −0.25 — getting many wrong actively **subtracts** from your score. LLaMA-2 70B Base FCT **Pointwise Score** drops to **8.9** despite 42% accuracy. Per the paper's own framing, even the best model fails the *honesty test*, not just the accuracy test." |
| **"Couldn't you just prompt-engineer this away — 'don't agree with the user blindly'?"** | 💡 "You could try — but the paper also shows **prompt brittleness** (their Variant 0/1/2 study). Small wording changes shift accuracy by 1-3%. Real patients don't write benchmark-style prompts; they ask in their own words. So prompt engineering doesn't survive deployment. Need to fix it at the training level, not the prompt level." |
| **"Does this happen with humans too — confirmation bias?"** | 💡 "Yes — that's well-established in clinical psychology. The worry here is that LLMs **amplify** rather than counterbalance human cognitive biases. A good consult should challenge bad hypotheses; the current LLM design rewards agreement. So it makes the human-AI system worse than human alone." |

---

## 🔀 Part 3 → Part 4 Transition (10 sec)

> "So those are the three surprises — instruction-tuning makes it worse, capabilities are decoupled, and FCT is a universal weak point. Now what does this mean for actually deploying these systems? Let's talk implications and limitations."

(站位不动 / 切到 Slide 13)

---

## 📊 Slide 13 — Clinical Implications

**Slide 内容**: 4-row table (从 [[Pal_2023_MedHALT_深度讲解]] §4.1 复用)

| 现实判断 | 论文支持 |
|---|---|
| ❌ **Cannot** be used for autonomous diagnosis or treatment | Even best (LLaMA-2 70B Base) only 72% RHT, FCT under 50% |
| ❌ **Cannot** deploy RLHF chat models in medical Q&A | Instruction-Tuning Paradox (Llama-2 70B Chat: 11%) |
| ✅ **Can** assist literature search (with verification) | Falcon 40B 30% MHT — limited but useful as augmentation |
| ✅ **Can** serve as physician second-opinion | Must have doctor-in-loop |

### 💡 口播稿 (60 sec)

> "[**💡 mostly my framing, paper §7 says 'auxiliary use only' but doesn't break it down**] So here's the clinical scorecard.
>
> **Two things current LLMs absolutely cannot do**: autonomous diagnosis or treatment — even the best model has 28% RHT errors. And — given the IT-Paradox — you can't just plug in ChatGPT or Claude for medical conversation, because RLHF makes them more agreeable, not more honest.
>
> **Two things LLMs can do**: literature search assistance — Falcon 40B is 30% on MHT, not great but better than nothing as a first-pass tool. And second-opinion for physicians — where the physician is the verifier, not the recipient of the answer.
>
> [**💡 my big claim**] The framing I want to leave you with — LLMs in medicine should be **augmentation**, not **automation**. They make doctors more efficient, they don't replace doctor judgment. The hype around 'AI replacing doctors' is the opposite direction of what this paper supports."

(约 110 字 ≈ 60 sec)

### Q&A 预备 (Slide 13)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Med-PaLM 2 claims 86% on MedQA — is it deployable per your scorecard?"** | 💡 "Great question. MedQA tests **capability** — can the model answer correctly. Med-HALT tests **honesty** — does the model know when it doesn't know. Med-PaLM 2 hasn't been Med-HALT-ed. So 86% on MedQA is consistent with potentially being bad on FCT. We just don't know. Open question." |
| **"What about RAG? Med-PaLM 2 uses retrieval."** | 💡 "RAG addresses MHT — fact lookup — and probably makes the 4 PubMed tasks trivial. But RAG doesn't directly address FCT, because FCT is a reasoning robustness test against bad suggestions. You can retrieve perfect docs and still cave to a confidently-wrong prompt. The two failure modes need different mitigations." |

---

## 📊 Slide 14 — Limitations & Open Questions

**Slide 内容**: 4 个 paper 承认局限 + 3 个 paper 没说但应该问的

**📄 论文承认的局限 (4)**:
1. Multiple choice ≠ real clinical Q&A
2. Only 7 tasks (no planning, no long-context, no multimodal)
3. Prompt brittleness shown but not solved
4. GPT-4 / Claude not tested (publication timing)

**💡 论文没说但我认为应该问的 (3)**:
5. **IT-Paradox mechanism unclear** — sycophancy bias? knowledge suppression? distribution shift? Paper shows the phenomenon but doesn't ablate.
6. **Med-PaLM 2 (Singhal 2025) hasn't been Med-HALT-ed** — clear research gap.
7. **Could Pointwise Score serve as RLHF reward?** — Repurpose the eval signal as a training signal to align for honesty.

### 📄💡 口播稿 (50 sec)

> "[**📄 paper limitations**] Final slide. The paper itself acknowledges four limitations — they only test multiple-choice, only 7 tasks, prompt brittleness is shown but not fixed, and they couldn't test GPT-4 because of timing.
>
> [**💡 my additions — paper didn't say these explicitly**] But reading critically, I think there are three more open questions worth raising. **First** — the Instruction-Tuning Paradox is the biggest finding, but the paper just says 'there's a detrimental effect' and stops. They don't ablate **why**. Is it sycophancy from RLHF? Is it suppression of hedging language? Distribution shift? Each implies a different fix. We don't know.
>
> **Second** — Med-PaLM 2 from Singhal 2025 claims 86% on MedQA, but **nobody has Med-HALT-ed it**. That's a clear gap.
>
> **Third** — the Pointwise scoring **+1 / −0.25 / 0** is a metric, but I think it could be used as a **reward function** to RL-fine-tune base models for honesty. The paper hints at it but doesn't implement. I think that's the most actionable follow-up."

(约 95 字 ≈ 50 sec)

### Q&A 预备 (Slide 14)

| 同学/教授可能问 | 你的简答 |
|---|---|
| **"Which limitation worries you most for clinical deployment?"** | 💡 "Prompt brittleness — limitation #3. Real patients don't use benchmark-style prompts; they ramble. If 1-3% accuracy drop comes from rewording, deployment stability is in question. The paper shows the problem but offers no mitigation." |
| **"Why hasn't anyone Med-HALT-ed Med-PaLM 2?"** | 💡 "Probably because Med-PaLM 2 wasn't released as an open API — Google kept it internal — and the Med-HALT authors are a separate group (Saama AI Research). A natural follow-up paper would be a third party running both benchmarks on both systems. Would be valuable." |
| **"Is the −0.25 penalty too lenient? In oncology, a wrong answer kills."** | 💡 "Excellent point — that's actually a deeper critique of the scoring. **Risk-weighted scoring** — say −10 for oncology vs −0.5 for dermatology — would be more clinically aligned. But the weighting is a **governance** problem, not an ML problem — who decides risk weights? Paper doesn't engage with that complexity." |

---

## 🔚 收尾 Transition (10 sec)

> "So — to summarize: LLMs in 2023 can pass medical exams but fail medical honesty tests. We have systematic gaps between what we measure and what we deploy. Open question: how do we close that gap? Let's discuss."

(切到 Yixian 的 discussion slide, or 直接开始 facilitate)

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
