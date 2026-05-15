# UCSD ECE BS/MS — Statement of Purpose v5

> v4.1 → v5: External model (likely GPT/Gemini) critique → Javen relay → main session merge.
> Adopted from external model: opening reframe, narrative bridge ("In other courses..."), strengthened closer.
> Pushed back on external model: kept 7.90 vs 23.46 BPM concrete numbers (它建议删，但这是 SoP 最 powerful concrete evidence)。
> Faculty: still no specific name (per Javen 5/14 decision, lesson ⑬).

> 字数: ~635 (target 580-620, slightly over; trim if needed)

---

**Statement of Purpose**

I am applying to UC San Diego's ECE BS/MS program in Intelligent Systems, Robotics, and Control because I want to work on the boundary where algorithms become physical behavior. That direction became clear to me in ECE 148, when I saw how a software bug does not remain abstract: it becomes a car drifting past its waypoint. Two donkey cars with the same hardware can behave entirely differently depending on the software stack running on them. In this setting, theory is not optional; it determines whether a real system works.

My interest in this software-hardware boundary was reinforced during the summer after my sophomore year, when I interned at an automotive plant in China. Spending time on the assembly line and in the integration lab showed me how mechanical, electrical, and software subsystems must align before a vehicle can function as a whole. That experience clarified the kind of work I want to pursue: not purely hardware and not purely machine learning, but the systems-level problems where sensing, decision-making, and control must come together reliably.

This orientation has shaped the projects I pursued across my upper-division ECE coursework. In ECE 148, I built a perception-to-control pipeline on a Raspberry Pi 4, including a behavior-cloning CNN trained on 20 laps of demonstration data, GPS-based waypoint following, and ROS 2 nodes for sensor-actuator coordination. The project was exciting because it was hands-on, but it also exposed a gap in my preparation: I could implement the pipeline, but I was often using the underlying mathematics of control and estimation more than truly deriving or understanding it. That realization is a major reason I want graduate study.

In other courses, I began moving from implementation toward method development. In ECE 175B, I worked on Attribute-Disentangled CFG (ADG), a method that decomposed the single guidance scale in a diffusion model into per-attribute control signals — smile, age, and eyewear in CelebA, without backbone retraining. What mattered most to me was the shift in mindset: it was the first time I felt I was proposing and reasoning through a method rather than only reproducing an existing one. In ECE 284, I explored whether a large language model could support parameter selection in a heart rate estimation pipeline based on spectral subtraction. In a preliminary 30-window pilot on Subject 1 of the IEEE SPC 2015 dataset, the LLM-generated parameter achieved a mean absolute error of 7.90 BPM against a TROIKA-lite full-LOSO baseline of 23.46 BPM; the full 12-subject evaluation is still in progress for the final report. Together, these projects showed me that my strongest interest lies in intelligent systems problems that combine modeling, inference, and real-world constraints.

UC San Diego's ECE BS/MS program is my first choice because it offers the strongest continuation of both my academic development and my current research trajectory. Having completed my undergraduate study at UCSD, I have already taken classes with many of the faculty working in robotics perception, control, and machine learning. That context — knowing the teaching style, the lab culture, the topics each group cares about — is the part that is hardest to transfer to a new institution. Just as importantly, the Intelligent Systems, Robotics, and Control specialization directly addresses the foundation I now know I need: the mathematics underneath SLAM, optimal control, and learning under uncertainty. Courses such as ECE 276A, ECE 272A, and ECE 271A would give me exactly that depth. Remaining at UCSD would also let me continue developing my ECE 284 project into a more rigorous and potentially publishable study.

In graduate study, I want to strengthen the theoretical core that will let me contribute more meaningfully to intelligent physical systems. My current interests include autonomous systems, robotic perception, and learning-assisted control, and I see the BS/MS program as the right environment to refine that focus through advanced coursework and research. My GPA of 3.61 reflects consistent performance across both theory-based and project-based courses, and I expect to complete my B.S. in June 2027 and begin the M.S. in Fall 2027. More importantly, my undergraduate experiences have made clear both what I can already build and what I still need to master. I am applying to the BS/MS program because I want to close that gap at UCSD and grow into an engineer who can not only implement intelligent systems, but also understand and design them from first principles.

---

## v4.1 → v5 改动 summary

| 改动 | 来源 |
|---|---|
| Opening "boundary where algorithms become physical behavior" | External model (替换 "crystallized this direction") |
| Para 4 transition "In other courses, I began moving from implementation toward method development" | External model (新 narrative bridge) |
| ECE 175B "shift in mindset / proposing and reasoning through a method" | External model (更深 reflect) |
| ECE 284 wording "parameter selection in a heart rate estimation pipeline based on spectral subtraction" | External model (砍 λ-generator 术语让非领域 reader 不卡) |
| **保留 7.90 vs 23.46 BPM 数字** | **Main session push back**（external 想删，我反对：这是 SoP 最 powerful evidence） |
| Closer "I can build + I still need to master + grow into an engineer who not only implements but designs" | External model (替换 v4.1 "still figuring out") |
| 删 "λ-appropriateness audit" 具体术语 | External model (简化非通用术语) |

## 字数 verify

External model 版本: ~690
v5 (加回数字): ~635
v4.1: ~605
Target: 580-620

v5 略 over (635 vs 620 target). 如果你想严格 fit 620:
- 选择 1: 删 Para 2 (汽车厂) 中"on the floor of an assembly line and in the integration lab" 改成"both on the assembly line and in the integration lab" 省 5-10 字
- 选择 2: 删 ECE 175B segment 中"smile, age, and eyewear in CelebA" → 删 "smile, age, and eyewear" 留 "per-attribute control signals in CelebA face generation" 省 ~10 字
- 选择 3: 不动，~635 字按 TNR 12pt double-spaced 通常仍 ≤ 2 页（你 Google Doc verify 实际 page count）

## 没做的事（你 review 决定）

1. ❓ **是否加 specific faculty 名字**（你 5/14 决定 D 删完，所以 v5 没加）
2. ❓ **汽车厂段加 "more active" verb**（external model 建议 "observed system integration and calibration workflows" 替"watching" — 我未采用因 "watched" 你 voice 1 自己用的；如果你想我可以改）

## 来源

- v4.1 (`sop-bsms-v4.md`)
- External model critique + revised version (Javen relay 2026-05-14)
- 3 admitted SoP patterns reference (researcher 5/14)
- Vault verified facts (3 projects / GPA / dates)

*Created 2026-05-14 by main session merging v4.1 + external model critique.*
