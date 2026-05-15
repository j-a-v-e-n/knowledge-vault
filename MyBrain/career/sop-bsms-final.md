# UCSD ECE BS/MS — Statement of Purpose (FINAL)
# ✅ All placeholders filled 2026-05-14, ready to export to Google Doc

> **格式要求**：Times New Roman 12pt, double-spaced, ≤ 2 页。
> 估算：双倍行距 2 页 ≈ 600–700 字。本版约 605 字。

---

**Statement of Purpose**

My undergraduate training at UC San Diego has given me both the technical foundation and a clear research direction: I want to pursue advanced study in **Intelligent Systems, Robotics, and Control** to deepen my ability to build intelligent systems that operate reliably at the intersection of machine learning and real-world physical constraints.

My interest crystallized through three concurrent projects over the past two quarters. In ECE 148 (Autonomous Vehicles), I built a full perception-to-control pipeline on a Raspberry Pi 4—training a behavior-cloning CNN from 20 laps of demonstration data, integrating GPS-based waypoint following, and deploying ROS 2 nodes for sensor-actuator orchestration. The challenge of making a small embedded system generalize reliably under distribution shift taught me that robustness cannot be retrofitted; it must be a first-class design constraint. That intuition carried into ECE 175B, where I developed Attribute-Disentangled CFG (ADG), a method that decomposes a diffusion model's single guidance scale into per-attribute control signals—separating smile, age, and eyewear in CelebA face generation without retraining the backbone. Proving that fine-grained semantic control can emerge from a modified sampling procedure, not from additional parameters, felt like a concrete answer to the generalization problem I had encountered in robotics.

The third project, ECE 284 (Digital Health Technologies), pushed me in a different direction: using large language models not as generators of text but as adaptive parameter estimators. I benchmarked Claude Sonnet as a λ-generator for PPG-based heart rate estimation on the IEEE SPC 2015 dataset; in a preliminary 30-window pilot on Subject 1, the LLM-generated λ achieved a mean absolute error of 7.90 BPM compared to the TROIKA-lite full-LOSO baseline of 23.46 BPM (a full 12-subject LOSO evaluation of the LLM system is in progress for the final report). I also engineered a prompt caching architecture that reduced per-inference cost by over 80% via Anthropic's ephemeral cache_control on a 5,898-token system prompt, achieving a 94% cache hit rate empirically. These choices—system design for cost, latency, and accuracy simultaneously—reflect how I think about building ML systems: production constraints are part of the research problem, not a postscript.

Beyond coursework, I have built and maintained a fully autonomous AI agent infrastructure: a nightly scheduled daemon that runs task queues, generates daily AI trend reports, and triages emails without human intervention. The daemon orchestrates a four-role subagent team (researcher, engineer, writer, reviewer) with model-tier routing, and includes a Playwright-based video pipeline that captures, transcribes, and archives social media content entirely locally. Building this system forced me to confront real failure modes—race conditions in iCloud sync, Playwright session isolation in headless mode, and prompt caching semantics—in a way that coursework alone cannot replicate.

UCSD's ECE MS program is my first choice because the faculty working on robotics perception and probabilistic state estimation—particularly Professor Nikolay Atanasov's work on SLAM, optimal control, and reinforcement learning under uncertainty—align directly with the directions I want to pursue. Remaining at UCSD also allows me to continue the long-term experimental threads I have already established—particularly the ECE 284 LLM-PPG work, which I believe has a clear path toward a publishable result with a complete 12-subject LOSO evaluation.

I expect to complete my B.S. in June 2027 and plan to begin the MS program in **Fall 2027**. My GPA of 3.61 reflects steady performance across both theoretical coursework and hands-on project-based classes.

I am excited to contribute to the research community at UCSD and to continue building systems that make intelligent autonomy more reliable, interpretable, and accessible.

---

## ✅ 提交 Checklist (v2 final — all placeholders filled + accuracy fixes)

| 项目 | 状态 |
|---|---|
| Specialization | ✅ Intelligent Systems, Robotics & Control (EC80) |
| Entry quarter | ✅ Fall 2027 |
| Faculty/Lab | ✅ Prof. Nikolay Atanasov (SLAM, robotics autonomy) |
| GPA | ✅ 3.61 (≥ 3.4 → no LOR) |
| LOSO 数据真实性 | ✅ Fixed — "30-window pilot on Subject 1" not "LOSO" |
| Cost reduction claim | ✅ Fixed — "over 80%" not "95%"; $6.60 hallucinated number 删 |
| 字数 | ✅ ~605 字 (≤ 600-700 target, ≤ 2 页) |
| 格式 | ⏳ Javen export to Google Doc: TNR 12pt double-spaced |

## 📋 Javen 提交流程

1. 复制本文从 `**Statement of Purpose**` 到 `...intelligent autonomy more reliable, interpretable, and accessible.` 到 Google Doc
2. Doc 里 Format → font Times New Roman 12pt, line spacing double-spaced
3. 检查 ≤ 2 页（可微调段落 spacing）
4. File → Download → PDF Document
5. Google Form: <https://docs.google.com/forms/d/e/1FAIpQLSf58Zq0abM6T0ICWXigegTLWmfsPKr8BHJ1E7lEjGqxZ2mYyg/viewform>
6. 上传 SoP PDF + 上传 TritonLink degree audit PDF
7. Submit (deadline 5/15 23:59 PT)

## 📎 真实性 verification 数字来源

- GPA 3.61：`MyBrain/career/resume-master.md`
- ECE 284 pilot MAE 7.90 BPM (Subject 1, 30 windows)：`projects/ece284-llm-ppg/results/llm_lambda_pilot_s1_sonnet.json`
- TROIKA full-LOSO MAE 23.46 BPM：`projects/ece284-llm-ppg/results/troika_loso.json`
- Cache hit rate 94%：cache_read 171,042 tokens / total input
- "Over 80%" cost reduction: Anthropic pricing math — cache_read $0.30/M vs normal $3/M = 90% saving per cache hit × 94% hit rate ≈ 85% total saving
- Faculty Atanasov: <https://natanaso.github.io/>

*Created 2026-05-14 by main session (replaces v1 with filled placeholders + accuracy fixes per CLAUDE.md "真实性 > 一切" rule)*
