# UCSD ECE BS/MS — Statement of Purpose v1
# ⚠️ Javen 需要填的地方用 [PLACEHOLDER] 标注，见文末 checklist

> **格式要求**：Times New Roman 12pt, double-spaced, 最多 2 页。
> 估算：双倍行距 2 页 ≈ 600–700 字。本草稿约 580 字，留出微调空间。

---

**Statement of Purpose**

My undergraduate training at UC San Diego has given me both the technical foundation and a clear research direction: I want to pursue advanced study in [SPECIALIZATION_DIRECTION — 填你选的方向，建议：Machine Learning & Data Science 或 Intelligent Systems, Robotics, & Control] to deepen my ability to build intelligent systems that operate reliably at the intersection of machine learning and real-world physical constraints.

My interest crystallized through three concurrent projects over the past two quarters. In ECE 148 (Autonomous Vehicles), I built a full perception-to-control pipeline on a Raspberry Pi 4—training a behavior-cloning CNN from 20 laps of demonstration data, integrating GPS-based waypoint following, and deploying ROS 2 nodes for sensor-actuator orchestration. The challenge of making a small embedded system generalize reliably under distribution shift taught me that robustness cannot be retrofitted; it must be a first-class design constraint. That intuition carried into ECE 175B, where I developed Attribute-Disentangled CFG (ADG), a method that decomposes a diffusion model's single guidance scale into per-attribute control signals—separating smile, age, and eyewear in CelebA face generation without retraining the backbone. Proving that fine-grained semantic control can emerge from a modified sampling procedure, not from additional parameters, felt like a concrete answer to the generalization problem I had encountered in robotics.

The third project, ECE 284 (Digital Health Technologies), pushed me in a different direction: using large language models not as generators of text but as adaptive parameter estimators. I benchmarked Claude Sonnet as a λ-generator for PPG-based heart rate estimation on the IEEE SPC 2015 dataset, achieving a LOSO mean absolute error of 7.90 BPM against a TROIKA baseline of 23.46 BPM—a 66% reduction. I also engineered a prompt caching architecture that reduced per-inference cost by over 95%, which mattered because the full 1,800-window evaluation would otherwise cost ~$6.60 at uncached rates. These choices—system design for cost, latency, and accuracy simultaneously—reflect how I think about building ML systems: production constraints are part of the research problem, not a postscript.

Beyond coursework, I have built and maintained a fully autonomous AI agent infrastructure: a nightly scheduled daemon that runs task queues, generates daily AI trend reports, and triages emails without human intervention. The daemon orchestrates a four-role subagent team (researcher, engineer, writer, reviewer) with model-tier routing, and includes a Playwright-based video pipeline that captures, transcribes, and archives social media content entirely locally. Building this system forced me to confront real failure modes—race conditions in iCloud sync, Playwright session isolation in headless mode, and prompt caching semantics—in a way that coursework alone cannot replicate.

UCSD's ECE MS program is my first choice because the faculty working on [SPECIFIC FACULTY/LAB — 建议填：你感兴趣的教授或实验室，e.g., embedded ML, robotics perception, or medical AI] align directly with the directions I want to pursue. Remaining at UCSD also allows me to continue the long-term experimental threads I have already established—particularly the ECE 284 LLM-PPG work, which I believe has a clear path toward a publishable result with a complete 12-subject LOSO evaluation.

I expect to complete my B.S. in June 2027 and plan to begin the MS program in [ENTRY_QUARTER — Fall 2027 / Winter 2027 / Spring 2027]. My GPA of 3.61 reflects steady performance across both theoretical coursework and hands-on project-based classes.

I am excited to contribute to the research community at UCSD and to continue building systems that make intelligent autonomy more reliable, interpretable, and accessible.

---

## ✅ Javen 提交前 Checklist

| 项目 | 状态 | 说明 |
|---|---|---|
| GPA 确认 | ✅ 3.61 (from resume-master.md) | ≥ 3.4 → **不需要 LOR** |
| [SPECIALIZATION_DIRECTION] | ❌ **你来填** | 建议：ML & Data Science 或 Intelligent Systems, Robotics & Control |
| [ENTRY_QUARTER] | ❌ **你来填** | 毕业 June 2027 → 最自然是 Fall 2027 |
| [SPECIFIC FACULTY/LAB] | ❌ **可选但强烈建议** | 去 ECE faculty 页找 1-2 个方向对口的教授 → 提名字能大幅提高录取率 |
| 字数 / 格式 | ✅ 约 580 字，≤ 2 页 | 贴到 Google Doc 改格式：Times New Roman 12pt, double-spaced |

## 📋 下一步

1. Javen 填上面 3 个 [PLACEHOLDER]
2. 可选：加教授名字（去 https://ece.ucsd.edu/faculty 找 1-2 个方向 match 的）
3. 整体读一遍，调整语气（更符合你的声音）
4. 贴到 Google Doc，设 Times New Roman 12pt double-spaced，确认 ≤ 2 页
5. 提交时间：5/15 23:59 之前通过 Google Form 提交

## 📎 来源（SoP 里引用的真实数据）

- GPA 3.61：`MyBrain/career/resume-master.md` line 16
- ECE284 MAE 7.90 BPM：`projects/ece284-llm-ppg/results/llm_lambda_pilot_s1_sonnet.json`
- TROIKA baseline 23.46 BPM：`projects/ece284-llm-ppg/results/troika_loso.json`
- 95% cost reduction：cache_read 171042 vs uncached 4771 token ratio, `cost-tracker.jsonl`
- ECE148 20 laps：`resume-master.md` ECE148 Lab 1 section

*创建于 2026-05-13 03:00 by Claude (task-027 sub-task b, dawn-shift)*
