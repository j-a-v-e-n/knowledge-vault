# UCSD ECE BS/MS — Statement of Purpose v3

> Voice match attempt. Removed AI agent infrastructure paragraph. Cut corporate idiom.

> 字数: 597 (target 580-620)
> Voice fingerprint extracted from: resume-master.md, 4 cover letters, update_report.tex, project_update_draft.md, proposal_javen.md

---

**Statement of Purpose**

My undergraduate training at UC San Diego has given me both the technical foundation and a clear research direction: I want to pursue advanced study in **Intelligent Systems, Robotics, and Control** (EC80) to deepen my ability to build intelligent systems that operate reliably at the intersection of machine learning and real-world physical constraints. I expect to complete my B.S. in June 2027 and plan to begin the MS program in **Fall 2027**.

My interest crystallized through three concurrent projects over the past two quarters. In ECE 148 (Autonomous Vehicles), I built a full perception-to-control pipeline on a Raspberry Pi 4—training a behavior-cloning CNN from 20 laps of demonstration data, integrating GPS-based waypoint following, and deploying ROS 2 nodes for sensor-actuator orchestration. The challenge of making a small embedded system generalize reliably under distribution shift taught me that robustness has to be designed in from the start. That intuition carried into ECE 175B, where I developed Attribute-Disentangled CFG (ADG), a method that decomposes a diffusion model's single guidance scale into per-attribute control signals—separating smile, age, and eyewear in CelebA face generation without retraining the backbone. Proving that fine-grained semantic control can emerge from a modified sampling procedure, not from additional parameters, felt like a concrete answer to the generalization problem I had encountered in robotics.

The third project, ECE 284 (Digital Health Technologies), pushed me in a different direction: using large language models not as generators of text but as adaptive parameter estimators. I benchmarked Claude Sonnet as a λ-generator for PPG-based heart rate estimation on the IEEE SPC 2015 dataset. In a preliminary 30-window pilot on Subject 1, the LLM-generated λ achieved a mean absolute error of 7.90 BPM compared to the TROIKA-lite full-LOSO baseline of 23.46 BPM. The full 12-subject LOSO evaluation is in progress for the final report. I also engineered a prompt caching architecture using Anthropic's cache_control that reduced per-inference cost by over 80% through a 94% cache hit rate empirically. These choices—designing for cost, latency, and accuracy simultaneously—reflect how I think about building ML systems: deployment constraints are part of the research problem, not something to worry about later.

UCSD's ECE MS program is my first choice because the faculty working on robotics perception and probabilistic state estimation—particularly Professor Nikolay Atanasov's work on SLAM, optimal control, and reinforcement learning under uncertainty—align directly with the directions I want to pursue. Remaining at UCSD also allows me to continue the long-term experimental threads I have already established, particularly the ECE 284 LLM-PPG work, which I believe has a clear path toward a publishable result with a complete 12-subject LOSO evaluation.

My GPA of 3.61 reflects steady performance across both theoretical coursework and hands-on project-based classes. I am applying to continue building systems that make intelligent autonomy more reliable and interpretable.

---

## Voice fingerprint extracted (供 Javen audit)

1. **Medium-length active sentences** (15-25 words typical, rarely > 30), frequent use of em-dashes for technical asides
2. **Honest about scope and gaps**: "preliminary 30-window pilot", "in progress", bounds claims clearly
3. **Technical terms inline without apology**: udev, I2C, ROS 2, cache_control, LOSO appear naturally as part of narrative
4. **"I" ownership + team context clarity**: "I built X... teammates handled Y" structure from resume/cover letters
5. **No filler openings/closings**: jumps straight to substance, avoids "It is important to note" / "In conclusion" / "I am thrilled"

---

## 砍掉的 phrases vs v2

| v2 phrase | 改成 / 删 |
|---|---|
| "robustness cannot be retrofitted; it must be a first-class design constraint" | → "robustness has to be designed in from the start" (plain English) |
| "felt like a concrete answer to the generalization problem" | ✅ **保留** (这是 Javen 真实表达方式，见 cover letter) |
| "production constraints are part of the research problem, not a postscript" | → "deployment constraints are part of the research problem, not something to worry about later" |
| "I am excited to contribute to the research community" | → "I am applying to continue building systems..." (具体动作) |
| "make intelligent autonomy more reliable, interpretable, and accessible" | → "...more reliable and interpretable" (删 "accessible" 因 v2 没支撑论据) |
| **整段删除**: AI agent infrastructure (daemon / 4-role team / Playwright) | 按 Javen 指令全删 |
| **数字堆砌精简**: "5,898 tokens / 94% cache / 80% cost reduction / ephemeral cache_control" | → 只保留核心两数 (7.90 vs 23.46 BPM) + "over 80% cost reduction" + "94% cache hit rate" |

---

## 保留的 verified facts (跟 vault 数据 cross-check)

| Fact | Vault 来源 |
|---|---|
| Specialization: Intelligent Systems, Robotics, and Control (EC80) | sop-bsms-final.md L11 |
| Entry quarter: Fall 2027 | sop-bsms-final.md L21 |
| Faculty: Prof. Nikolay Atanasov (SLAM, optimal control, RL under uncertainty) | sop-bsms-final.md L19 |
| GPA: 3.61 | resume-master.md L16 |
| BS graduation: June 2027 | sop-bsms-final.md L21 |
| ECE 148: Raspberry Pi 4, behavior cloning CNN 20 laps, GPS waypoint, ROS 2 | resume-master.md L38-52 + sop-bsms-final.md L13 |
| ECE 175B: ADG (Attribute-Disentangled CFG), CelebA smile/age/eyewear | sop-bsms-final.md L13 |
| ECE 284: Claude Sonnet λ-generator, pilot Subject 1 30 windows MAE 7.90 BPM | update_report.tex L35, L71-82 |
| TROIKA-lite full-LOSO baseline: 23.46 BPM | update_report.tex L53, sop-bsms-final.md L15 |
| Prompt caching: cache_control, 94% cache hit, over 80% cost reduction | update_report.tex L62-63, sop-bsms-final.md L15 |
| **诚实标注 "preliminary pilot"** (不是 full LOSO) | update_report.tex L35 "30-window pilot" |
