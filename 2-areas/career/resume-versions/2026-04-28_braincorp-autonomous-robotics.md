---
company: Brain Corp
role: Software Engineering Intern — Autonomous Robotics (Summer 2026)
base_version: resume-master v2 (2026-04-28)
status: DRAFT — JD not yet fetched (daemon 无法 WebFetch). Javen 拿到真实 JD 后比对并微调
created: 2026-04-28 (daemon dawn-shift)
---

# 为什么 Brain Corp 是最强匹配（给 Javen 的 context）

> Brain Corp 做的是**商业自主移动机器人**（商场扫地机器人 / 清洁机器人）。他们的核心技术栈：
> **ROS 2 + 视觉 detection + state machine 导航 + 嵌入式 Linux + edge deployment**
>
> Javen 的 ECE148 final project（Autonomous Recycling Detector & Collector）：
> **ROS 2 + YOLOv8 detection + state machine + OAK-D Lite + Raspberry Pi**
>
> 这不是"相关经验"——这是**在不同规模上做同一件事**。Brain Corp 在 SD，还是 hometown 公司。

---

# Javen Jiawen Cao
jacao@ucsd.edu | (858) 340-3255 | San Diego, CA
linkedin.com/in/javen-cao · github.com/j-a-v-e-n
**U.S. Citizen**

---

## EDUCATION

**University of California, San Diego** — Expected June 2027
B.S. Electrical Engineering — Machine Learning and Controls Track | GPA: 3.61 / 4.0

Relevant Coursework: Intro to Autonomous Vehicles (ECE 148), Linear Control Systems (ECE 171A/B),
Pattern Recognition & ML (ECE 175A), Probabilistic Reasoning & Graphical Models (ECE 175B),
Linear & Nonlinear Optimization (ECE 174), Engineering Probability & Statistics (ECE 109)

---

## PROJECTS

### ECE 148 — Autonomous Robotics Build (Winter 2026)

Full-quarter hands-on autonomous vehicle build: from bare Raspberry Pi 4 setup through perception, control, and autonomous deployment. Relevant labs below:

**DonkeyCar End-to-End Learning (Lab 1)**
- Configured Raspberry Pi 4 from scratch: Python venv, OAK-D Lite stereo camera (DepthAI + udev), VESC motor controller (PyVESC), F710 gamepad
- Collected 20–25 laps of human driving data; trained CNN behavior-cloning model (TensorFlow 2.15, CPU inference on Pi); deployed for autonomous laps
- Hands-on: embedded Linux, sensor integration, full ML pipeline (data collection → on-device inference)

**ROS 2 Robotics Integration (Lab 3)**
- Built ROS 2 system connecting sensors and actuators on the vehicle: publisher/subscriber nodes, launch-file orchestration, distributed topic messaging
- Hands-on: ROS 2 node lifecycle, inter-process communication, sensor-actuator pipeline architecture

**Final Project: Autonomous Recycling Detector & Collector (Team of 4)**
🔗 github.com/UCSD-ECEMAE-148/winter-2026-team-3-final-project

- **My contribution**: developed servo motor control module (Python) for actuated shovel mechanism — lifting and lowering driven by detection state transitions
- **Team system**: YOLOv8 object detection (Roboflow-trained, OAK-D Lite deployment) + ROS 2 state machine (`random_drive → detect → approach → collect → return_base`) + VESC drive via custom `object_follower` node tracking object centerlines
- Real-world autonomous operation: vehicle detects recyclables (cans, bottles, cardboard), approaches, collects, returns to base — **same problem domain as Brain Corp's commercial floor-cleaning robots**
- Stack: Python, ROS 2, YOLOv8, OAK-D Lite, Raspberry Pi, VESC

---

## EXPERIENCE

### Foton Cummins Engine Co., Ltd. — Engineering Intern
*Beijing, China | July 2025*

- Supported diesel engine ECU calibration and validation workflows; assisted with parameter tuning cycles and test documentation
- Processed and aggregated test datasets using Excel; worked with Linux CLI in the calibration test environment

---

## TECHNICAL SKILLS

**Robotics & Embedded:** ROS 2, Raspberry Pi 4, OAK-D Lite (stereo depth + RGB), VESC motor controller, servo control, embedded Linux (Ubuntu ARM), GPS sensor integration
**Machine Learning & CV:** YOLOv8, TensorFlow, OpenCV, NumPy, Roboflow (data annotation pipeline)
**Programming:** Python, C, Bash, MATLAB, Java, Assembly (ARM64)
**Tools:** Git/GitHub, Linux (Ubuntu), VS Code
**Languages:** English (fluent), Mandarin Chinese (native)

---

## 给 Javen 的定制要点说明（不进 PDF）

### 调整策略
1. **Projects 放最前**（通常 Experience 在前）：Brain Corp 是 robotics startup，他们看 project 比看 internship 更重。ECE148 和他们的产品直接对应
2. **Coursework 精简为 Robotics 相关**：保留 ECE 148/171/175A/175B/174，去掉 ECE 284（digital health 对 Brain Corp 无关）
3. **Labs 1-3 展开**：展示系统性 hands-on 积累，不是一个 project 碰巧用了 ROS，而是整个 quarter 的 robotics engineering 训练
4. **Final project 第一 bullet 明确说 "My contribution"**：诚实区分 own work vs team work（resume-master v2 的原则保留）
5. **Skills 重排序**：Robotics & Embedded 放最前，ML & CV 第二，Programming 第三

### 待 JD 核对的点
- Brain Corp 用的是 ROS 2 还是 ROS 1？（如果 ROS 1，把 "ROS 2" 相关改成 "ROS (ROS 2 primary, familiar with ROS architecture)"）
- JD 有没有提 SLAM / mapping？如果有：你 ECE148 有 GPS waypoint 跟随（Lab 2），可以提一下
- JD 有没有 C++ 要求？你有 C 但没有 C++ 项目经验——诚实标注
- JD 有没有 Docker？如果你在 ROS 2 lab 里用过容器，加进去

### 还需要 Javen 补充
- [ ] GitHub 账号确认（现用 `github.com/j-a-v-e-n` 占位，需要真实链接）
- [ ] ECE148 final project GitHub 链接是否公开？（task board 里有 UCSD GitHub org 的链接）
- [ ] Brain Corp 真实 JD 链接（Javen 或 daemon 主对话 fetch）
- [ ] Foton 实习：有没有比 "supported / assisted" 更有力的具体数字？
