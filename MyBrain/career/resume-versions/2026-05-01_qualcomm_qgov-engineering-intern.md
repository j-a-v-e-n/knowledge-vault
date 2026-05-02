---
company: Qualcomm Government Technologies (QGOV)
role: QGOV Engineering Internship — Summer 2026 (San Diego or Boulder) | US CITIZENSHIP REQUIRED
base_version: 2026-04-29_qualcomm_embedded-intern (reframed for QGOV after Embedded SD listing closed 2026-05-01)
status: DRAFT — Javen finalizing same day, then submitting
created: 2026-05-01
JD_source: |
  WebSearch (capd.mit.edu / Indeed / careers.qualcomm.com listing)
  Job ID: 446707492633
  Locations: San Diego, CA OR Boulder, CO
  US CITIZENSHIP REQUIRED
  Required:
    - US Citizen
    - Bachelor's CompE/CS/EE
    - Available 11-14 weeks May-Sept 2026
    - Expected graduation Nov 2026 or later
    - 1+ year of programming experience: C, C++, Java, or Python
  Preferred (Track 1: Embedded Software):
    - Real-time embedded software development
    - Cellular systems / communications systems knowledge
    - Familiarity with Git, Gerrit, debugging tools
    - Digital signal processing
    - Software vulnerability analysis tools
  Preferred (Track 2: Software in Test):
    - Test automation framework design with Python
    - Cellular / communications / wireless evaluation
    - Mobile OS (Linux, Android, iOS)
    - Tools: Linux, Git, Jenkins, Testlink, Docker
---

# 给 Javen 的 context（不进 PDF）

> **为什么 QGOV 是更强匹配（vs 之前 Embedded SD 那个）**：
> Qualcomm Government Technologies 做政府赞助的 R&D（把商业 Snapdragon / 通信系统适配到军方 / 政府场景）。**US CITIZENSHIP REQUIRED** 是核心壁垒——直接筛掉一半申请者（国际生）。你公民身份 = **真正的差异化优势**，跟 Anduril 那条国防线一脉相承。
>
> Track 1 (Embedded Software) 跟你 ECE148 经验高度对接：
> ✅ Embedded software dev（你 Pi 4 整 quarter）
> ✅ Git workflow（你日常）
> ✅ Linux / embedded systems（你 udev / I2C / serial 实操）
> ⚠️ Real-time（你 ECE148 sensor + control loop 算软实时；JD 是 hard real-time，需要诚实标注）
>
> **JD 里你不命中的（cover letter 已直说）**:
> ❌ Cellular systems / communications / DSP / 软件漏洞分析 / 设备驱动开发 / C++ 项目
>
> JD 说 preferred 不是 required，所以 gap 不致命；US Citizen 已经把你抬到 top tier 候选池。

# 主版本：调整策略（vs 之前 Embedded SD 版本）

1. 内容**几乎不变**——你 actual experience 不变
2. 主要 reframe 在 **cover letter 头部叙事**：从 "Snapdragon embedded silicon" → "government-sponsored R&D / mission-critical embedded"
3. 简历**保留** US Citizen 标签放显眼处（QGOV 是核心要求，不是装饰）
4. 简历**增加** 一行 emphasizing real-time（Lab 1 的 "real-time" 关键词加 boldface）
5. ECE 284 (Digital Health) 仍去掉——跟 QGOV 无关

---

# Javen Jiawen Cao
San Diego, CA · jacao@ucsd.edu · (858) 340-3255
linkedin.com/in/javen-cao · github.com/j-a-v-e-n
**U.S. Citizen** ← 关键放显眼处（QGOV 必须）

---

## EDUCATION

**University of California, San Diego** — Expected June 2027
B.S. Electrical Engineering — Machine Learning and Controls Track | GPA: 3.61 / 4.0

**Relevant Coursework:**
- **Embedded & Systems**: Intro to Autonomous Vehicles (ECE 148), Linear Systems (ECE 101)
- **Controls**: Linear Control Systems (ECE 171A/B), Linear & Nonlinear Optimization (ECE 174)
- **Machine Learning**: Pattern Recognition & ML (ECE 175A), Probabilistic Reasoning & Graphical Models (ECE 175B)
- **Foundations**: Engineering Probability & Statistics (ECE 109)

---

## TECHNICAL SKILLS

**Programming:** **Python, C, Assembly (ARM64)**, Java, MATLAB, Bash
**Embedded & Systems:** Raspberry Pi 4, embedded Linux (Ubuntu ARM), udev USB permissions, I2C interface configuration, serial / UART communication, GPIO, kernel-level device access
**Sensors & Peripherals:** OAK-D Lite stereo camera (DepthAI), VESC motor controller (PyVESC), GPS modules, servo control
**Robotics & Real-Time:** ROS 2 (publisher/subscriber, launch-file orchestration), real-time sensor + actuator control loops
**Machine Learning on Edge:** TensorFlow 2.15 (CPU-only inference on Pi 4), CNN behavior cloning, YOLOv8 (team work), OpenCV
**Tools:** Git/GitHub, VS Code, LTspice / PSpice (circuit simulation), Excel
**Languages:** English (fluent), Mandarin Chinese (native)

---

## PROJECTS

### ECE 148 — Intro to Autonomous Vehicles (Winter 2026)

Quarter-long hands-on build of an autonomous robot vehicle from a bare Raspberry Pi 4 through deployed autonomous driving. Worked across three individual labs and one team final project; all hands-on system integration, embedded Linux, and ML deployment work performed by me.

**Lab 1 — DonkeyCar Behavior Cloning (Individual)**
- Configured **Raspberry Pi 4** Ubuntu environment from scratch: Python virtual environment, **udev rules for USB device permissions**, **I2C interface enablement** for OAK-D Lite stereo camera (DepthAI driver), **serial communication** with VESC motor controller (PyVESC library)
- Collected 20–25 laps of human driving training data through campus courtyard; trained **CNN behavior-cloning model** with TensorFlow 2.15 running CPU-only on Pi 4 — a **resource-constrained embedded environment** (4GB RAM, no GPU)
- Deployed model on-device for autonomous driving — full pipeline from data collection to **real-time on-device inference**
- Hands-on with embedded Linux internals (udev, kernel device handling, dmesg debugging), sensor integration, and ML edge deployment

**Lab 2 — GPS-Based Path Following (Individual)**
- Integrated GPS module with DonkeyCar via serial; recorded a demonstration lap of an extended campus loop and autonomously replayed it via waypoint following
- Hands-on with GPS coordinate handling, sensor fusion concepts, and closed-loop path tracking

**Lab 3 — ROS 2 Integration (Individual)**
- Built ROS 2 system on Pi connecting sensors (camera, IMU) and actuators (motor, servo) via publisher/subscriber nodes and launch-file orchestration; experienced node lifecycle, topic-based messaging, and distributed inter-process communication

**Final Project — Autonomous Recycling Detector & Collector (Team of 4 · Winter 2026)**
🔗 github.com/UCSD-ECEMAE-148/winter-2026-team-3-final-project
- **My contribution:** developed independent Python script controlling shovel servo motor (lifting/lowering mechanism); responsible for Raspberry Pi system setup and integration across team's components
- Team built: YOLOv8 detection (deployed on OAK-D Lite), ROS 2 state machine for the autonomous recycling-collection pipeline, custom `object_follower` ROS node, CAD-modeled and 3D-printed shovel
- Cross-disciplinary team: ECE (me) / CompE / Aerospace E / Mechanical E

---

## EXPERIENCE

### Foton Cummins Engine Co., Ltd. — Engineering Intern
*Beijing, China | July 2025*

- Participated in **diesel engine ECU (Embedded Control Unit) calibration and validation** workflows; supported parameter tuning cycles and test data documentation in an automotive embedded controller environment
- Performed test data cleaning and report aggregation using Excel; **worked with Linux command-line tools** in the calibration test environment

---

## 📎 来源

- WebSearch + capd.mit.edu / Indeed / careers.qualcomm.com 2026-05-01 by 主对话 Claude
- Job ID 446707492633
- 投递地址：https://careers.qualcomm.com/careers/job/446707492633-qualcomm-government-technologies-qgov-engineering-internship-%E2%80%93-summer-2026-san-diego-or-boulder-us-citizenship-required-san-diego-california-united-states-of-america
