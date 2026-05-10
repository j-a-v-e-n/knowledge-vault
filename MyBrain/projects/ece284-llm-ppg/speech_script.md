# ECE 284 Week 8 演讲稿 + Q&A 预测

> **时长目标**: 10–15 分钟 + Q&A
> **时间标记**: 每段旁边标估计耗时，严格照稿可控在 12 分钟，留 3–5 分钟 Q&A
> **风格**: 自然口语，不是读稿子。这份是提词器，不是逐字稿——扫一眼要点，用自己的话说。

---

## 开场 (Slide 1) — 30秒

> Hi everyone. I'm Javen, and my project is about benchmarking LLM paradigms for heart rate estimation from wrist PPG signals.

---

## Motivation (Slide 2) — 1分钟

> So the core problem is this: if you wear a fitness tracker and run hard, the wrist sensor picks up not just your heartbeat but also the motion from your arm swinging. That's the motion artifact problem.

> Classical signal processing handles it okay at low intensity, but as motion increases, error spikes — sometimes by tens of beats per minute. Machine learning helps, but it still treats HR estimation as a static pattern-matching task.

> Our question is: **can an LLM contribute something these methods can't** — specifically, context-aware reasoning about what to do given the current motion situation? And if yes, *how* should it be integrated?

---

## Experimental Setup (Slide 3) — 1分钟

> We use the IEEE SPC 2015 dataset — 12 subjects, all wearing a wrist PPG sensor plus an accelerometer on a treadmill at varying speeds. Ground truth is from ECG.

> Each 8-second window gives us one PPG chunk and one HR label. After windowing, we have about 1,768 windows total across the 12 subjects.

> Evaluation is leave-one-subject-out cross-validation — so we train on 11 subjects, predict on the 12th, rotate through all 12. This tests generalization to unseen people, which is the real use case.

> We have four systems in the benchmark. TROIKA-lite and Random Forest are both done. The Claude λ-generator has a 30-window pilot done. ReAct is a stretch goal.

---

## TROIKA-lite (Slide 4) — 1分钟30秒

> TROIKA-lite follows the Zhang et al. 2015 paper. The intuition is simple: take the FFT of the PPG signal, estimate the motion spectrum from the accelerometer, subtract the motion from the PPG spectrum, and pick the dominant remaining frequency as your HR.

> In theory this is elegant. In practice: overall MAE is 23.46 BPM. The best subject hits 6.87 — great. But subject 10 is at 65 BPM error — essentially useless. High variance means the algorithm's reliability is unpredictable.

> The fundamental issue is that spectral subtraction uses a *fixed* subtraction weight. When motion is severe, that one-size-fits-all weight breaks down. This is exactly the gap we're trying to address.

---

## Random Forest (Slide 5) — 1分钟30秒

> Random Forest extracts 4 features per window: dominant spectral frequency from PPG, spectral correlation between PPG and accelerometer, accelerometer RMS, and spectral entropy. Then it trains a 200-tree forest in LOSO-CV.

> Results: 10.53 BPM MAE — 55% improvement over TROIKA. That's a big jump.

> But when we stratify by motion level — I used accelerometer RMS thresholds of 1.3 and 1.7 — we see the pattern clearly: low motion gives you about 3 BPM median error, medium about 5, but high motion still blows up to 10 BPM median.

> So even with learned features, the high-motion regime is unsolved. That's what motivated the LLM design — using motion context explicitly rather than implicitly through features.

---

## Claude λ-generator Design (Slide 6 + 7) — 2分30秒

> Here's the key design decision: I did **not** have Claude predict the heart rate directly. That would require the model to do signal processing arithmetic, which LLMs are bad at.

> Instead, Claude outputs a single number λ — the spectral subtraction weight for TROIKA. λ ranges from 0.1 to 3.0. A high λ means "this is high motion, subtract aggressively." A low λ means "signal is clean, subtract lightly." Then the TROIKA pipeline runs with that weight and produces the HR estimate.

> [Slide 6] This is architecturally elegant because: one, it's interpretable — λ has a physical meaning. Two, computation stays deterministic — Claude only handles the context-aware part. Three, it's cost-efficient — one API call per window generates a scalar, not a full HR prediction.

> [Slide 7 — Architecture] For each window, we send Claude a 6-field JSON: accelerometer RMS, PPG SNR estimate, dominant spectral frequency, motion regime category, the top 3 PPG spectral peaks, and the last 3 HR estimates for temporal context. 

> The system prompt is 5,898 tokens — 10 few-shot examples showing sensible λ choices for different motion scenarios, a physiology reference, and anti-patterns. Because this prompt is the same for every window in a fold, we use Anthropic's prompt caching with `cache_control: ephemeral`. After the first call, 94% of subsequent calls hit the cache.

---

## Pilot Results (Slide 8) — 1分30秒

> The 30-window pilot on subject 1 gives us: TROIKA 10.55, RF 11.94, Claude λ-generator **7.90 BPM**. That's 25% better than TROIKA and 34% better than RF on the same windows.

> Cost: $0.11 for 30 windows. Extrapolating to full LOSO — 1,768 windows — that's about $6.60 total. That's affordable for a research project.

> Two outlier windows — 16 and 28 — were off by over 55 BPM. Looking at them: both are extreme motion cases where the LLM chose λ values that overcorrected. This is exactly the kind of failure mode we'll analyze in the motion-stratified breakdown next week.

> Important caveat: 30 windows is one subject. Full LOSO results are still in progress — we'll have those for the final report.

---

## Next Steps (Slide 9) — 45秒

> Immediately: run full 12-subject LOSO for the λ-generator. Also run a Haiku 4.5 pilot to see if we can cut cost by 5× with an acceptable accuracy tradeoff.

> Week 9: motion-stratified analysis for all three systems — I want to see if the λ-generator's advantage concentrates in the high-motion regime. Also a λ appropriateness audit — manually inspect 100 windows and ask: did Claude pick a sensible λ given the context?

> If time: the ReAct orchestrator, where Claude calls spectral analysis tools step-by-step instead of just generating one parameter.

---

## Summary (Slide 10) — 30秒

> To summarize: TROIKA-lite is our worst performer, RF improves significantly, and Claude λ-generator shows promise — beating both on our pilot. The key design choice was to keep the LLM out of arithmetic and in context-reasoning, which seems to be paying off.

> The full story depends on the complete LOSO results. Thank you — happy to take questions.

---

---

# Q&A 预测题 + 建议回答

> 下面是教授最可能问的 5 类问题，按可能性排序。每个建议 1–2 句核心回答，够了，别扯太长。

---

### Q1: 为什么 LOSO，而不是 train/test split?

**回答**: LOSO is the standard evaluation for physiological sensing because the goal is to predict HR for *unseen users*. A random 80/20 split would leak inter-subject correlations — the model would see windows from the test subject during training, inflating accuracy. LOSO directly measures how well the system generalizes to new individuals.

---

### Q2: λ-generator 为什么不直接预测 HR，而要绕一圈生成 λ?

**回答**: LLMs have two relevant weaknesses: they're unreliable at continuous numeric arithmetic, and they have no access to the raw signal. By having Claude output λ — a semantically meaningful parameter — we let the deterministic spectral pipeline handle the math, while Claude contributes the contextual judgment about *how aggressively* to subtract motion. It's a better division of labor.

---

### Q3: 30 windows 的 pilot 够代表性吗？

**回答**: Not fully — that's why full LOSO is the next step. 30 windows is one subject at one session. Subject 1 might be easier or harder than average. The pilot validates the pipeline and gives a ballpark, but the 12-subject result is what matters for the paper.

---

### Q4: $6.60 的 cost 算不算贵？值不值？

**回答**: It depends on the use case. For a research benchmark, $6.60 is completely reasonable. For deployment in a commercial product, you'd want the Haiku version — our estimate is ~$1.30 for full LOSO at Haiku pricing, which starts to be competitive. The real question is: does the accuracy improvement justify the API cost vs. a pure local RF? That's the ROI analysis for the final report.

---

### Q5: 为什么用 spectral subtraction weight 作为 λ，而不是选择另一个参数？

**回答**: The spectral subtraction weight is the most impactful single parameter in TROIKA — it directly controls how much motion is removed from the PPG spectrum. Other parameters, like the HR search band, are less sensitive to per-window motion context. So λ is the highest-leverage choice for context-aware adaptation.

---

### Q6 (可能): Prompt caching 是什么，对结果有影响吗?

**回答**: Prompt caching lets Anthropic's API store the first 5,898 tokens of our system prompt on their servers for 5 minutes. Subsequent calls within that window pay 0.1× the normal input price instead of 1.0×. It doesn't affect the model's outputs — the prompt content is identical. It's purely a cost optimization, and the 94.1% cache hit rate confirms it's working as expected.

---

### Q7 (少见): 为什么不用更简单的 LLM — 比如 GPT-4o mini 或者本地 Ollama?

**回答**: We chose Claude Sonnet 4.5 and plan a Haiku 4.5 comparison because we're using Anthropic's native prompt caching API, which is the most straightforward integration for cost tracking. A GPT-4o mini comparison would be a good addition for the final report if time permits, but it's not in scope for this update.

---

*speech_script.md — 生成于 2026-05-10 by Claudian dawn-shift (task-022 sub e)*
