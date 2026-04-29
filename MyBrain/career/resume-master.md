---
version: master v2 (2026-04-28 honest reframe)
note: 替代之前 daemon 写的版本（基于"servo arm 是 Javen 做"的错误假设）。本版基于 Javen 实际确认：所有 lab 按 TA 指南做、用 AI debug、问 TA 兜底；他独立 own 的部分是 final project 的 servo 控制代码 + RPi 设置 + 跨 lab 的整套 hands-on
---

# Javen Jiawen Cao
jacao@ucsd.edu | (858) 340-3255 | San Diego, CA
linkedin.com/in/javen-cao · github.com/j-a-v-e-n
**U.S. Citizen** ← 关键放显眼处

---

## EDUCATION

**University of California, San Diego** — Expected June 2027
B.S. Electrical Engineering — Machine Learning and Controls Track | GPA: 3.61 / 4.0

**Relevant Coursework:**
- **Autonomy & Robotics**: Intro to Autonomous Vehicles (ECE 148), Linear Control Systems (ECE 171A/B)
- **Machine Learning**: Pattern Recognition & ML (ECE 175A), Probabilistic Reasoning & Graphical Models (ECE 175B), Linear & Nonlinear Optimization (ECE 174)
- **Foundations**: Engineering Probability & Statistics (ECE 109), Linear Systems (ECE 101), Digital Health Technologies (ECE 284)

---

## EXPERIENCE

### Foton Cummins Engine Co., Ltd. — Engineering Intern
*Beijing, China | July 2025*

- Participated in diesel engine ECU calibration and validation workflows; supported parameter tuning and test data documentation
- Performed test data cleaning and report aggregation primarily using Excel; worked with Linux command-line tools in the test environment

---

## PROJECTS

### ECE 148 — Intro to Autonomous Vehicles (Winter 2026)

Over the course of the quarter, completed full hands-on autonomous vehicle build covering perception, control, and ML — from Raspberry Pi setup through autonomous driving deployment. Worked with team and TA-provided guides; debugging supported by AI tooling and TA office hours.

**Lab 1: DonkeyCar Behavior Cloning (Individual)**
- Configured Raspberry Pi 4 environment for autonomous vehicle: Python virtual environment, OAK-D Lite stereo camera (DepthAI + udev permissions), VESC motor controller (PyVESC), Logitech F710 input
- Collected 20-25 laps of human driving data through EBU2 courtyard; trained CNN behavior-cloning model with TensorFlow 2.15 (CPU-only on Pi); deployed for autonomous driving
- Hands-on experience with embedded Linux permissions, sensor integration, and full ML pipeline (data → training → on-device inference)

**Lab 2: GPS-Based Single-Lap Path Following (Individual)**
- Integrated GPS module with DonkeyCar framework for waypoint-based autonomous navigation; recorded one demonstration lap of a larger campus loop and replayed autonomously
- Hands-on experience with GPS coordinate handling and path-following control

**Lab 3: ROS 2 Integration (Individual)**
- Built ROS 2 system connecting sensors and actuators on the Pi-based vehicle; implemented publisher/subscriber nodes and launch-file orchestration
- Hands-on experience with ROS 2 distributed messaging, node lifecycle, and topic-based architecture

**Final Project: Autonomous Recycling Detector & Collector (Team of 4 | Winter 2026)**
🔗 github.com/UCSD-ECEMAE-148/winter-2026-team-3-final-project

- **My contribution**: developed independent Python script for shovel servo motor control (lifting and lowering mechanism)
- Team built: YOLOv8 detection model (Roboflow-trained, deployed on OAK-D Lite), ROS 2 integration with VESC via custom `object_follower` node tracking object centerlines, CAD-modeled and 3D-printed shovel with hinge + pulley mechanism
- Cross-disciplinary team of 4: ECE (me) / CompE / Aerospace E / Mechanical E
- Stack: Python, ROS 2, YOLOv8, OAK-D Lite, Raspberry Pi

> 注：team-of-4 项目我**只 claim 我 own 的部分**（servo code + RPi setup），团队产出在第二条说明用 "Team built"——诚实区分。

---

## TECHNICAL SKILLS

**Programming:** Python, C, Java, MATLAB, Bash, Assembly (ARM64)
**Machine Learning & CV:** TensorFlow, YOLOv8, OpenCV, NumPy, Roboflow (data annotation)
**Robotics & Embedded:** ROS 2, Raspberry Pi, OAK-D Lite (stereo depth + RGB), VESC motor controller, servo control, embedded Linux, GPS sensor integration
**Tools:** Git/GitHub, Linux (Ubuntu), VS Code, Excel
**Hardware:** Circuit testing & calibration (LTspice, PSpice), 3D printing
**Languages:** English (fluent), Mandarin Chinese (native)

