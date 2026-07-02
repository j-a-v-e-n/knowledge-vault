---
target_company: Anduril Industries
target_role: Software Engineering Intern (Summer 2026)
target_location: Costa Mesa, CA (preferred — 距 SD 1.5h 车程)
based_on: resume-master.md v2 (2026-04-28 honest reframe)
us_person_required: yes ✓ (Javen 美国公民 — 强制要求 + 你的最大优势)
created: 2026-04-28
status: ready (2026-04-28 finalized) — 投递用 PDF: 同目录的 .html 文件浏览器打印
---

# Javen Jiawen Cao
jacao@ucsd.edu | (858) 340-3255 | San Diego, CA
linkedin.com/in/javen-cao · github.com/j-a-v-e-n
**U.S. Citizen** — Eligible for export-controlled work

---

## EDUCATION

**University of California, San Diego** — Expected June 2027
B.S. Electrical Engineering — Machine Learning and Controls Track | GPA: 3.61 / 4.0

**Relevant Coursework:**
- **Autonomy & Robotics**: Intro to Autonomous Vehicles (ECE 148), Linear Control Systems (ECE 171A/B)
- **Machine Learning**: Pattern Recognition & ML (ECE 175A), Probabilistic Reasoning & Graphical Models (ECE 175B), Linear & Nonlinear Optimization (ECE 174)
- **Foundations**: Engineering Probability & Statistics (ECE 109), Linear Systems (ECE 101)

---

## PROJECTS

### ECE 148 — Intro to Autonomous Vehicles (Winter 2026)

Quarter-long hands-on autonomous vehicle build: perception, control, and on-device ML — from RPi system setup through deployed autonomous driving.

**Lab 1 — DonkeyCar Behavior Cloning (Individual)**
- Configured Raspberry Pi 4 stack for autonomous driving: Python venv, **OAK-D Lite stereo camera** (DepthAI + udev USB permissions), **VESC motor controller** (PyVESC), Logitech F710 input
- Collected 20-25 laps of human driving data; trained CNN behavior-cloning model with **TensorFlow 2.15** (CPU-only on Pi); deployed for autonomous driving through EBU2 courtyard
- Hands-on experience with embedded Linux permissions, sensor integration, and full ML pipeline (data → training → on-device inference)

**Lab 2 — GPS-Based Single-Lap Path Following (Individual)**
- Integrated **GPS module** with DonkeyCar framework for waypoint-based autonomous navigation; recorded a single demonstration lap of an extended campus loop and replayed autonomously
- Hands-on experience with GPS coordinate handling, sensor fusion concepts, and path-following control

**Lab 3 — ROS 2 Integration (Individual)**
- Built **ROS 2** system connecting sensors and actuators on the Pi-based vehicle; implemented publisher/subscriber nodes and launch-file orchestration
- Hands-on experience with ROS 2 distributed messaging, node lifecycle, topic-based architecture

**Final Project — Autonomous Recycling Detector & Collector (Team of 4 | Winter 2026)**
🔗 github.com/UCSD-ECEMAE-148/winter-2026-team-3-final-project

- **My contribution**: developed independent Python script for shovel servo motor control (lifting and lowering mechanism)
- Team built: **YOLOv8** detection (Roboflow-trained, deployed on **OAK-D Lite**), **ROS 2** integration with **VESC** via custom `object_follower` node tracking object centerlines, CAD-modeled and 3D-printed shovel mechanism with hinge + pulley
- Cross-disciplinary team of 4: ECE (me) / CompE / Aerospace E / Mechanical E
- Stack: Python, ROS 2, YOLOv8, OAK-D Lite, Raspberry Pi

---

## EXPERIENCE

### Foton Cummins Engine Co., Ltd. — Engineering Intern
*Beijing, China | July 2025*

- Supported diesel engine ECU calibration and validation workflows; assisted with parameter tuning and test data documentation
- Performed test data cleaning and report aggregation primarily using Excel; worked with Linux command-line tools in the test environment

---

## TECHNICAL SKILLS

**Programming:** Python, C, Java, MATLAB, Bash, Assembly (ARM64)
**Machine Learning & CV:** TensorFlow, YOLOv8, OpenCV, NumPy, Roboflow
**Robotics & Embedded:** ROS 2, Raspberry Pi, OAK-D Lite (stereo depth), VESC motor controller, servo control, embedded Linux, GPS integration
**Tools:** Git/GitHub, Linux (Ubuntu), VS Code, Excel
**Hardware:** Circuit testing & calibration (LTspice, PSpice), 3D printing
**Languages:** English (fluent), Mandarin Chinese (native)
