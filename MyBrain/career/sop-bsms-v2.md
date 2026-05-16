# UCSD ECE BS/MS — Statement of Purpose v2

> **v2 changes (2026-05-14 by Claude per Javen)**：砍掉所有具体数值（GPA / MAE / % 提升 / laps / $ cost / window count），重写为短句通俗英语；保留 ECE148 / ECE175B / ECE284 项目名 + 核心想法；v1 留在 `sop-bsms-v1.md` 作 backup 对比

> **格式**：Times New Roman 12pt, double-spaced, 最多 2 页
> 字数估算：约 500 字 → 双倍行距约 1.5-2 页

---

**Statement of Purpose**

My time at UC San Diego has made one thing clear: I want to keep building intelligent systems, and I want to do it as a Master's student in **Machine Learning & Data Science**. The undergraduate years have given me the math and the engineering side; what I want next is the depth and the time to make these systems work outside the lab, not just inside it.

Three projects shaped this direction.

In **ECE 148 (Autonomous Vehicles)**, I built a small self-driving car on a Raspberry Pi. I trained it to follow a track by showing it laps to imitate, then layered on GPS so it could handle longer routes. The hard part was never getting it to work in the lab. The hard part was getting it to still work when the lighting changed, when the track surface changed, when the battery dipped. I came away believing that reliability is not something you add at the end. It has to be a design choice from the start.

In **ECE 175B (Probabilistic Reasoning & Graphical Models)**, I worked on image generation. Standard diffusion models use one single knob to control how closely the output follows a prompt. I built a method that splits that one knob into several—one for each attribute, like smile or age or eyewear—so each can be adjusted on its own. What made it satisfying was that this control did not require retraining the model at all. It came from changing how the model is sampled. That felt like the same lesson as ECE 148, applied to a very different domain: a smarter design beats a bigger model.

In **ECE 284 (Digital Health Technologies)**, I went in a different direction. I used a large language model not to write text, but to set the parameters of a signal processing algorithm. The task was estimating heart rate from wrist sensor data, which gets noisy when people move. I had the model read each window of sensor data and decide how aggressively to filter it. The results were meaningfully better than the classical baseline. I also designed a caching setup that brought the cost of the experiment way down. What I took from this is that designing for cost and reliability is part of the research, not something to deal with after the paper is written.

Outside of class, I have built and run my own AI agent system. It wakes up every night to process my task queue, summarize the day's AI news, and triage my emails—without me touching it. It splits work between a small team of specialized sub-agents and keeps cost in check by routing simple jobs to smaller models. Keeping a system like this alive through real failure modes—sync glitches, browser session bugs, cost runaways—has taught me things that coursework alone cannot.

UCSD's ECE Master's program is my first choice because the faculty here work on exactly the directions I want to pursue, particularly [SPECIFIC FACULTY/LAB — 可选，等我调研后填; 1-2 个教授名字]. Staying at UCSD also lets me continue the work I have already started, especially the ECE 284 project, which I believe has a real shot at a publishable result if I can finish the full evaluation.

I expect to complete my B.S. in **Winter 2027** and plan to begin the M.S. program in **Spring 2027**, the academic term immediately following my undergraduate completion.

I am excited to keep building practical AI systems at UCSD and to contribute to its research community.

---

## ✅ Javen 提交前 Checklist

| 项目 | 状态 | 说明 |
|---|---|---|
| GPA 不需要提到 SoP | ✅ 已删 | 你 5/14 指令：不要数值 |
| 项目数字（MAE / % / laps / $）| ✅ 全删 | 你 5/14 指令：不要具体数值 |
| 长难句 | ✅ 拆短 | 每句 ≤ 20 词为主，少数论点句 ~25 词 |
| ECE148 / 175B / 284 主线 | ✅ 保留 | 三个项目名 + 核心想法 + 拿走啥 |
| ML & Data Science 方向 | ✅ confirmed | （如要换 Robotics & Control 告诉我）|
| Fall 2027 入学 | ✅ 物理唯一 | UCSD 政策"no gap quarter" |
| [SPECIFIC FACULTY/LAB] | ⏳ 等你决定 | 我 5 min 调 2-3 个 best-fit 教授给你选 |
| 字数 | ✅ 约 500 字 → 双倍行距 ~1.5-2 页 | 贴 Google Doc 后用 word count verify |

## 📋 下一步

1. **你 review v2**（已弹 Obsidian），看看语气/通俗度是否你要的
2. 如不满意某段告诉我哪段，我精改
3. 决定要不要加 FACULTY 名字（yes / no）
4. 满意后：贴 Google Doc → Times New Roman 12pt double-spaced → 确认 ≤ 2 页
5. TritonLink 下 Academic History PDF
6. 填 ECE Internal Application Google Form → 上传 SoP + Academic History → submit
7. **deadline: 2026-05-15 23:59 PT (明天周五)**

## 📎 来源（v2 没引用任何数字，但底层事实仍来自）

- ECE148 项目：`resume-master.md` ECE148 Lab 1
- ECE175B 项目：`projects/ece175b-adg/`
- ECE284 项目：`projects/ece284-llm-ppg/`
- daemon 系统：`MyBrain/automation/`
- 毕业时间 June 2027：`career/applications.md` 备注栏

*创建于 2026-05-14 by Claude (task-027 sub-task b 重写, per Javen 5/14 主对话指令)*
