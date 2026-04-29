---
company: Qualcomm
role: Embedded Engineering Internship — Summer 2026 (San Diego)
base_version: resume-master v2 (2026-04-28 honest reframe)
status: DRAFT — Javen 醒后审 + 在 careers.qualcomm.com 上对照真实 JD 微调
created: 2026-04-29 (主对话 Claude，Javen 睡觉时)
JD_source: |
  WebSearch + Jobright.ai (官网 careers.qualcomm.com 是 JS 渲染抓不到全文)
  Job ID: 446707492801
  Location: San Diego, CA
  Pay: $0/hr - $98/hr (Jobright 提到的 range，疑似 placeholder，正式 JD 上有具体)
  Required:
    - Bachelor's/Master's CompE/CS/EE
    - Available 11-14 weeks May-Sept 2026
    - Expected graduation Nov 2026 or later  
    - 1+ years of academic experience with C, C++, Python, etc.
  Preferred:
    - Embedded programming in C/C++/Assembly + OS knowledge
    - Resource-constrained (MIPS/Memory) programming
    - Complex algorithms on embedded processor
    - Embedded microcontroller programming
    - Device driver development
    - Real-time embedded programming for general-purpose & heterogeneous (GPU, DSP)
    - Communication systems / DSP / wireless protocols (5G NR / LTE / 802.11)
---

# 给 Javen 的 context（不进 PDF）

> **为什么 Qualcomm 是强匹配**：
> Qualcomm 是 SD 总部、ECE 专业垂直对口、Snapdragon 系列嵌入式 AI 芯片需要的就是"会在 RPi 这种资源受限设备上跑 ML model"的人。你 ECE148 整个 quarter 干的事——RPi 4 配 udev USB 权限 / I2C 接 OAK-D / 在 Pi 上跑 TensorFlow CNN inference / VESC 串口控制——**完全命中** preferred qualifications 里的"embedded programming + OS + 资源受限 + 复杂算法 on embedded processor"。
>
> **JD 里你能命中的 preferred quals**:
> ✅ Embedded programming + OS knowledge (RPi + 嵌入式 Ubuntu)
> ✅ Resource-constrained programming (Pi 4 跑 CNN inference)
> ✅ Complex algorithms on embedded processor (CNN behavior cloning on Pi)
> ⚠️ Real-time embedded (sensor + servo control loop 是软实时)
>
> **JD 里你诚实承认的 gap**（cover letter 里直说）:
> ❌ Microcontroller bare-metal programming (RPi 是 SBC 跑 Linux，不是 MCU)
> ❌ Device driver development (你用 driver，没写 driver)
> ❌ Wireless protocols (5G/LTE/802.11) — 完全没碰过
> ❌ DSP — 完全没碰过
> ❌ C++ specifically — 你有 C / Java / Python / Assembly，没专门 C++ 项目
>
> JD 说 preferred 不是 required，所以 gap 不致命。但要在 cover letter 里诚实交代，不假装。

# 主版本：调整策略

1. **Programming 类放到 Skills 最前**——Qualcomm 第一道门槛是 "1+ years C/C++/Python 学术经验"，要让 ATS / 招聘官第一眼看到
2. **Embedded & Systems 部分加重**——把 ECE148 Lab 1 的 "udev + I2C + serial" 部分加 boldface 关键词（Qualcomm 工程师看 JD 是 driver 经验代理证据）
3. **Foton 实习重新解读**——"diesel engine ECU calibration" 隐含的是嵌入式控制 + 测试方法，可以稍微 frame 成"接触嵌入式 controller 测试流程"
4. **ML on edge 部分保留**——Qualcomm 的核心业务是 Snapdragon AI，"在资源受限的 Pi 上跑 CNN inference"是直接相关，不是无关
5. **Coursework 重排**——把跟嵌入式 / 控制 / 信号处理相关的课放最显眼。ECE171A/B (control), ECE174 (optimization), ECE101 (linear systems = 信号处理基础)
6. **去掉 ECE 284 (Digital Health)** —— 跟 Qualcomm 主营无关
7. **保留 U.S. Citizen 标签**——Qualcomm 国防 / 5G 工作可能涉及 export-controlled

---

# Javen Jiawen Cao
San Diego, CA · jacao@ucsd.edu · (858) 340-3255
linkedin.com/in/javen-cao · github.com/j-a-v-e-n
**U.S. Citizen**

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
**Robotics & Real-Time:** ROS 2 (publisher/subscriber, launch-file orchestration), control loops with sensor feedback
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
- Deployed model on-device for autonomous driving — full pipeline from data collection to on-device inference running in real-time
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

## ⚠️ 待 Javen 醒后核对 + 微调

1. **C++ 这件事**：我没把 C++ 放进 Skills（你没专门做 C++ 项目）。Cover letter 会诚实交代。如果你**自学过一点 C++**（比如读过书 / 看过 OOP 教程）可以加 "C++ (basic, self-study)" 到 Skills。**强烈不建议**为了 ATS 通过加 C++ 但其实不会——HackerRank 那一关就直接挂
2. **GPA 3.61** —— 从 master 直接拿，没改
3. **Foton 实习的措辞**：我 frame 成"嵌入式 controller 测试环境"。如果你实际记得更具体的 ECU calibration 内容（比如用什么软件、哪种数据），告诉我我加细节
4. **HackerRank 准备**：JD 里说"advancing candidates may be invited to complete a timed HackerRank challenge"——意味着投完简历可能有 OA。建议刷一下 LeetCode embedded / C / Bit manipulation 题（embedded 岗 OA 偏向位运算 + 简单算法 + 内存管理）
5. **Available 11-14 weeks May-Sept 2026**：你应该 OK 但确认一下，没冲突就 finalize

## 📎 来源

- WebSearch 2026-04-29 关于 Qualcomm Embedded 2026 Internship JD
- 官网链接 https://careers.qualcomm.com/careers/job/446707492801 (JS rendered, 投递时直接去这里点 Apply)
- 备用来源 https://jobright.ai/jobs/info/68f300bb9a65fd3458582b50（聚合站，不是官网）
