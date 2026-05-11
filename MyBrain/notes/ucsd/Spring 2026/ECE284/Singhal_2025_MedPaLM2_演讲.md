---
title: "Med-PaLM 2: Toward Expert-Level Medical Question Answering with LLMs"
type: source
tags: [ECE284, LLM, 医疗AI, MedQA, Nature_Medicine_2025]
sources: [raw/ucsd/Spring 2026/ECE284/Singhal_2025_MedPaLM2.pdf]
created: 2026-05-10
updated: 2026-05-10
priority: active
confidence: high
---

# Med-PaLM 2 — ECE284 Week 7 演讲稿

> **演讲日期**: 2026-05-12 周二 ECE284 Tu/Th 11:00-12:20 EBU1 2315
> **演讲时长**: 7-10 分钟 presentation + 后续 discussion lead
> **论文**: Singhal et al., "Toward expert-level medical question answering with large language models", *Nature Medicine* 31, 943-950 (2025)
> **第 2 次 primary lead**（第 1 次 Week 2 是 [[Perez_2019_AppleHeartStudy_演讲稿]] Apple Heart Study）

---

## 🎤 演讲 4 段（按 syllabus 要求）

### Part 1 — Problem & Motivation (1.5 min)

Today I'm presenting Med-PaLM 2, published in *Nature Medicine* this past March. The deceptively simple question: **can an LLM match physician-level performance on medical knowledge?**

Why it matters: there's a massive global gap in healthcare access — globally not enough physicians, rural US has critical shortages, low-income countries need basic triage at scale. LLMs are an obvious lever, but they have a credibility problem in medicine.

A year before this paper, **Med-PaLM 1 scored 67.2% on USMLE-style questions**. The USMLE passing threshold is 60%, and the lowest-performing US medical graduates score 74%. So Med-PaLM 1 was *barely passing*, definitely not expert-level. And accuracy isn't even the hardest part — the real problem is **confidence under uncertainty**: when the model is wrong, does it know? When it's right, is it reasoning or just pattern-matching training data? Can we trust it on adversarial / rare cases?

That's what Med-PaLM 2 attempts to fix.

---

### Part 2 — Technical Approach (2.5 min)

Three ingredients, each solving a specific problem.

**① Base model: PaLM 2**

PaLM 2 is a substantially improved successor to PaLM 1 (architecture details not fully disclosed). Base PaLM 2 scores **60.2% on MedQA out of the box** vs Flan-PaLM's 51.4%. That ~9% jump is significant before any medical-specific work begins.

**② Medical domain fine-tuning — mixed dataset training**

Key: not single-dataset fine-tuning. They mix **five medical QA corpora** at specific ratios — MedQA + MedMCQA (37.5% each), then HealthSearchQA + LiveQA + MedicationQA (smaller weights). Think of it like a resident reading textbooks, practicing exam questions, answering online consumer health questions, and handling medication queries — all in one training loop. The ratios were tuned experimentally; over-weighting one corpus causes overfitting to that style.

**③ Ensemble refinement + chain of retrieval (the novel contributions)**

**Analogy**: ask 10 doctors the same hard question. Each gives an answer + reasoning. Some think step-by-step, others jump to conclusions. You **vote** and **observe where they disagree** — disagreement signals ambiguity. Med-PaLM 2 does something similar:

- **Chain of Thought (CoT)**: model generates reasoning before answering ("Patient presents X. Could be A, B, or C. A ruled out because Y. Test Z distinguishes B vs C."). More transparent + often more accurate.
- **Ensemble Refinement (ER)**: model generates K=11 different reasoning paths, then **synthesizes** them ("Most paths point to X, dissent says Y..."). Catches local-minimum wrong answers a single chain might get stuck on.
- **Self-consistency**: sample multiple times, vote on final answer.

For **bedside consultation questions** they added **chain of retrieval** — the model dynamically generates search queries at each reasoning step ("Let me check the latest guidelines on X"), retrieves docs, incorporates them. Different from vanilla RAG because retrieval is *iterative within reasoning*, like a physician saying "let me check the latest evidence before answering."

---

### Part 3 — Key Results (3 min)

I'll focus on three findings.

#### Result 1: Benchmark performance jump

![[Singhal_2025_MedPaLM2_page02.png]]

> Med-PaLM 2 hits **86.5% on MedQA** vs Med-PaLM 1's 67.2% — a **19 percentage point jump**. It now crosses the USMLE passing line by a healthy margin and approaches the physical-expert baseline. GPT-4 sits at 86.1% — so Med-PaLM 2 is essentially **comparable to GPT-4 within statistical noise**, not strictly "better than."

Looking at Table 1 (cross-dataset performance):

![[Singhal_2025_MedPaLM2_page03.png]]

> Med-PaLM 2 scores **86.5% MedQA, 72.3% MedMCQA, 75.0% PubMedQA, 88.7% MMLU clinical**. The consistency across formats (USMLE, Indian medical entrance, PubMed abstract, undergrad clinical) suggests it's not just overfit to one exam style. Caveat: Table 2 reports **MedMCQA has 21.4% test/train overlap**, so some of that score is leakage. The authors call out the overlap and argue the difference is "still statistically significant" but don't quantify *how much* of the boost is real generalization.

#### Result 2: Physician evaluation on 9 quality axes

![[Singhal_2025_MedPaLM2_page04.png]]

> Two physician raters scored Med-PaLM 2 vs Med-PaLM 1 answers on 9 clinical axes — reading comprehension, knowledge recall, reasoning, consensus alignment, demographic bias risk, harm likelihood, etc. **On every axis Med-PaLM 2 rated higher than Med-PaLM 1**. More importantly, the model's distribution now clusters closer to the physician distribution (red dots) — meaning it's more *representative of how doctors think*, not just more accurate. Note wide CIs on "harm likelihood" — physicians weren't confident in that judgment, which is actually reassuring: it suggests the model isn't systematically more harmful than physicians, but we can't fully rule it out either.

#### Result 3: Bedside consultation pilot

![[Singhal_2025_MedPaLM2_page05.png]]

> Three-way preference ranking on real bedside questions submitted by specialists during routine care: **specialists preferred Med-PaLM 2 answers 65% of the time over generalist physicians**; generalists preferred Med-PaLM 2 over specialists' answers 41% of the time. Subtle but critical: even when **specialists rated their own specialist colleagues' answers, they only preferred those 79%** — that's the ceiling. 100% expert performance isn't realistic because experts can't even fully satisfy each other. Med-PaLM 2 is "expert-adjacent" by this metric, not "expert-level." Also: pilot N=20, proof-of-concept only.

---

### Part 4 — Limitations & Open Questions (1.5 min)

**What the authors acknowledge:**

- **Data leakage**: 21.4% test/train overlap on MedMCQA, lower on others. Impact debated, not quantified.
- **Pilot size**: only 20 bedside questions = proof-of-concept, not deployment-ready.
- **Benchmark-to-clinic gap**: all evaluation is on exam-style questions. Real clinic involves time pressure, incomplete info, follow-up dialogue — none captured.

**What I'd add (not explicit in paper but follow from critical reading):**

1. **Closed-weight model — no independent audit possible.** The paper explicitly says weights/code are not open-sourced "for safety and IP reasons." Consequence: researchers, hospitals, regulators can't independently audit for race/gender/SES bias, can't fine-tune for local population, can't inspect failure modes. Fundamentally different from open models like Llama. For a safety-critical domain, **auditability matters**.
2. **Not 100% expert-level.** 65% specialist preference means physicians still catch what the model misses 35% of the time. And the 79% specialist-vs-specialist ceiling means inherent ambiguity caps any LLM at sub-perfect.
3. **No demographic subgroup analysis.** Paper doesn't report performance broken down by patient demographics. Given the history of medical AI bias (Obermeyer 2019), this is a serious gap.
4. **No stress testing.** What if input is misspelled? Adversarial? About a very rare disease? Not tested.

---

## ❓ 4 个 Discussion Questions (按 syllabus 4 类别)

### Q1 — Clinical/Real-world Relevance

> "The paper shows 86.5% on MedQA and 65% specialist preference on a 20-question pilot, but those are controlled settings. In real bedside practice, you have 2 minutes per patient, incomplete history, conflicting vitals, and an anxious patient who can't articulate symptoms. The model can't see nonverbal cues, can't ask follow-ups in real time, doesn't know what the patient *didn't* say (often the diagnostic key). So: **what are the actual operational requirements for this system in a real clinic?** Must a physician review every model suggestion (defeating efficiency)? Can nurses use it autonomously? **And who's liable when the model misses a diagnosis** — Google (owns model), hospital (deployed it), or physician (should have caught it)? The model is closed-weight, so hospitals can't even audit the reasoning trail for malpractice discovery."

### Q2 — Methodological Critique

> "Table 2 reports 21.4% MedMCQA test/train overlap. The authors say the difference is 'still statistically significant' but **don't quantify how much score boost is real generalization vs contamination**. If you remove the overlapping questions and re-score, what's the revised accuracy? More critically: human evaluation used pairwise ranking on only **140 MultiMedQA questions — about 11% of the test set**. How confident are we that specialist preference scales? And my biggest concern: **the paper measures whether physicians prefer the model's answer, not whether they calibrate correctly to model accuracy.** Do doctors know *when to trust* the model and when to doubt it? High confidence in an incorrect answer is actively more dangerous than low confidence. Did the paper test physician calibration to model error?"

### Q3 — Technical Extension (connects to my own ECE284 project)

> "The paper's chain of retrieval works for *static* medical knowledge — 'is drug X contraindicated with symptom Y?'. But real medicine requires **temporal, personalized context**. My own ECE284 project is benchmarking LLM paradigms for PPG heart rate estimation under motion artifacts — and the key insight there is that the LLM should emit motion-artifact parameters that depend on the *individual's* sensor placement, prior recordings, and motion history. Similarly here: if a patient has 3 years of EHR data showing declining thyroid function plus a documented penicillin allergy, the model should weight those signals over generic textbook knowledge. **How would you design chain-of-retrieval to integrate patient-specific longitudinal data without per-patient retraining?** Currently the retrieval feels query-based and static."

### Q4 — Broader Implications (connects to Obermeyer + Ayers)

> "This connects to two earlier papers — Obermeyer 2019 on algorithmic bias in medical risk scores, and Ayers 2023 (this week) on ChatGPT vs physician empathy. Pattern I'm noticing: (1) **Closed-weight models break independent audit.** With Obermeyer's risk-score case, researchers *could* inspect the algorithm and find Black patients were systematically underestimated via a healthcare-spending proxy. With Med-PaLM 2, that kind of forensic analysis is impossible. (2) **Regulatory gap**: FDA hasn't clarified liability — Google, hospital, or physician? (3) **Innovation equity**: if only Google/OpenAI/Anthropic can build medical LLMs at scale, medical AI innovation concentrates in three for-profit companies; smaller hospitals, low-income countries, and academic researchers can only access via expensive APIs. **What's the path to equitable, auditable, deployed medical AI?** Smaller open-source models that sacrifice SOTA for auditability? Stronger transparency regulation? Something else?"

---

## 🧠 Critical Reading Notes (for oral assessment prep — not in slides)

**Likely follow-up questions:**

1. **"Ensemble refinement vs self-consistency — what's the difference?"**
   Self-consistency = K independent forward passes, vote. Ensemble refinement = K paths + *synthesis step* where the model meta-reasons about the disagreement. Voting + meta-reasoning about the vote.

2. **"Chain of retrieval vs RAG?"**
   RAG = retrieve once upfront based on input question. Chain of retrieval = model generates search queries *dynamically at each reasoning step*. Iterative within the chain.

3. **"You said 'comparable to GPT-4', but paper says Med-PaLM 2 exceeds it. Which is right?"**
   Within statistical noise. Table 1 shows Med-PaLM 2 86.5% [84.5, 88.3] vs GPT-4 86.1% [79.1, 93.5] — CI overlap is large. Paper hedges with "comparable to or exceeding."

4. **"If it's not expert-level and is closed-source, why publish?"**
   Because 19% improvement over Med-PaLM 1 is real and replicable. Because ensemble refinement + chain of retrieval is a *transferable methodological contribution* (could apply to other safety-critical domains). Because demonstrating LLMs are approaching practical clinical utility — even if not superhuman — shifts the deployment conversation.

**Things to be careful saying in front of the class:**

- Don't say "Med-PaLM 2 is better than GPT-4" — say "comparable within CI overlap"
- Don't say "approaches expert-level" without noting the 79% specialist-vs-specialist ceiling
- Don't say closed-source is a paper weakness — it's a deployment-reality concern, the paper makes the choice explicit and defensible

---

## 🔗 关联

- [[Perez_2019_AppleHeartStudy_演讲稿]] — Week 2 自己 lead 的，consumer-grade health monitoring。Med-PaLM 2 是 clinical-grade end of the spectrum — broader-implications angle
- [[Obermeyer_2019_医疗算法种族偏见]] — Q4 直接引用，algorithmic bias 角度
- [[Ayers_2023_ChatGPT_vs_Physicians]] — 同周 paper，empathy 角度互补（Singhal 偏 medical knowledge accuracy，Ayers 偏 bedside communication quality）
- [[Thirunavukarasu_2023_LLMs_in_Medicine]] — 同周 background review
- `raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf` — 自己 ECE284 project (LLM paradigms for PPG HR estimation), Q3 自然 bridge

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/Singhal_2025_MedPaLM2.pdf`
