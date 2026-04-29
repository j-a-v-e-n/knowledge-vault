---
company: Qualcomm
role: Embedded Engineering Internship — Summer 2026 (San Diego)
date: April 29, 2026
status: DRAFT — Javen 醒后审 + finalize
---

Javen Jiawen Cao
San Diego, CA
jacao@ucsd.edu · (858) 340-3255

April 29, 2026

Qualcomm Technologies, Inc.
San Diego, CA

---

Dear Qualcomm Hiring Team,

I'm applying for the Embedded Engineering Internship (Summer 2026, San Diego). I'm a Junior at UC San Diego pursuing a B.S. in Electrical Engineering on the Machine Learning and Controls track, returning to UCSD this fall to finish my final year. I'm a U.S. Citizen, available 11–14 weeks May–September 2026, with expected graduation June 2027.

What draws me to this role is that the embedded layer is exactly where I've been working — the place where you have to handle both the hardware peripherals showing up correctly to the OS *and* the application logic on top of them. In ECE 148 last quarter (Winter 2026), I configured a Raspberry Pi 4 stack from scratch for an autonomous vehicle: writing udev rules for USB device permissions, enabling I2C for an OAK-D Lite stereo camera through the DepthAI driver, configuring serial communication with a VESC motor controller, and patching library compatibility issues to make open-source robotics frameworks work with our specific hardware. I then trained a CNN behavior-cloning model with TensorFlow 2.15 and deployed it CPU-only on the Pi — a resource-constrained embedded environment — for full real-time autonomous driving. Across three individual labs (behavior cloning, GPS path following, ROS 2 integration), I got a real sense of how much of an embedded engineer's work lives at the boundary between "kernel sees the device" and "the system actually behaves correctly."

For my four-person final project (autonomous recycling collector), I owned the Python servo-control script and the Raspberry Pi system integration, while teammates handled YOLOv8 detection, the ROS 2 state machine, and the 3D-printed mechanism. Working across ECE / CompE / Aerospace / Mechanical taught me that delivering an embedded system is mostly about clean interfaces between disciplines.

I want to be honest about the gaps. I haven't yet written bare-metal microcontroller firmware (my embedded work has been on Linux SBCs), I haven't developed Linux kernel device drivers (I've used drivers heavily, including debugging when udev rules and DepthAI permissions interacted unexpectedly, but I haven't authored kernel-level code), and I don't have wireless protocol experience (5G / LTE / 802.11). My primary languages are Python, C, and ARM64 Assembly — I'm comfortable in C but haven't done a project specifically in C++. The good news is that the foundations — embedded Linux internals, scope-level debugging from coursework, sensor integration, real-time control loops, and ML edge deployment — I've actually done, and I learn embedded tooling fast when there's a working system in front of me.

What's particularly exciting is that Qualcomm's core work — running ML inference and signal processing on Snapdragon embedded silicon — is structurally the same problem I tackled at much smaller scale on the Pi: how to get a complex algorithm running well on a resource-constrained processor. I'd love to see that problem at the production scale you operate at.

Thank you for considering my application. I'd be excited to spend a summer building real embedded systems in San Diego.

Sincerely,
Javen Jiawen Cao
