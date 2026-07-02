---
title: Stojnić et al. (2023) — 人类婴儿与机器的常识心理学
type: source
tags: [COGS117, BIB, 婴儿认知, AI对比, 常识心理学, 神经网络, 理性行动]
sources: [raw/ucsd/Spring 2026/COGS117/Stojnic et al. (2023).pdf]
created: 2026-05-04
confidence: high
priority: active
---

# Stojnić et al. (2023) — 人类婴儿与机器的常识心理学

> 11月龄婴儿通过 Baby Intuitions Benchmark (BIB) 的所有 6 项 agent 推理任务，但当前 SOTA 神经网络全部失败——揭示婴儿拥有 AI 尚未获得的常识心理学

---

## 发现了什么

**核心问题：** 人类婴儿在生命第一年就展现出对他人行为的复杂理解——知道别人有目标、会选择高效路径、能使用工具。当前 AI 模型虽然在图像识别、语言生成等任务上表现出色，但它们是否具备这种"常识心理学" (commonsense psychology)？

**核心发现：** 研究团队创建了 **Baby Intuitions Benchmark (BIB)**，包含 6 个测试 agent 推理的任务：

1. **Goal-Directed** — agent 的行动指向物体，不是位置
2. **Multi-Agent** — 区分不同 agent 的不同目标
3. **Inaccessible-Goal** — agent 是否理解障碍物阻挡了目标
4. **Efficient-Agent** — agent 会选择高效路径
5. **Inefficient-Agent** — agent 不会选择低效路径
6. **Instrumental-Action** — agent 会使用工具达成目标

**结果对比：**

- **11月龄婴儿** (N=26 infants in Exp 1, N=58 in Exp 2)：通过所有 6 项任务
- **SOTA 神经网络** (BC-RNN 和 Video models)：在所有任务上**系统性失败**——不仅是"表现不如婴儿"，而是完全没有展现出对 agent rationality 的理解

这是首次在**受控、可直接对比**的实验环境中证明：婴儿的常识心理学远超当前 AI 的能力。

---

## 为什么会这样

### BIB 的设计哲学：控制变量 + 违反期待范式

BIB 的任务环境高度简化——2D grid world，agent 是彩色形状 (圆形、方形、三角形)，背景是黑白网格——这种极简设计有两个用意：

1. **排除低层次感知差异：** 婴儿和 AI 都看到完全相同的刺激 (short silent animated videos)，没有眼睛、毛发、面部表情等"生物性线索"
2. **隔离高层次推理：** 如果 agent 在这种抽象环境下的行为都能被婴儿理解，说明婴儿具备的不是"识别人类 / 动物"的特定模式，而是关于"理性 agent"的抽象原则

**违反期待范式 (Violation-of-Expectation, VoE)：**

- **Familiarization trials：** 婴儿看到 agent 以某种一致方式行动（比如重复移动到同一物体）
- **Test trials：** 呈现两种情况：
  - **Expected outcome** — agent 行为符合之前建立的模式（比如继续移动到相同物体）
  - **Unexpected outcome** — agent 行为违反模式（比如移动到之前从未去过的物体）
- **测量：** 婴儿对 unexpected outcome 的注视时间。如果婴儿理解了潜在规则，他们会对违反期待的事件看得更久（surprise response）

**生活类比：** 就像你看到朋友每天早上都去同一家咖啡店，某天她突然去了另一家——你会多看一眼 / 感到好奇。婴儿的长注视时间是"心理上的双击"：说明他们注意到了异常。

---

## 怎么证明的

### 实验 1 和 2：婴儿通过 BIB 所有任务

**参与者：**

- Experiment 1: N=26, 平均 11.13 月龄
- Experiment 2: N=58, 平均 11.06 月龄 (增加了 4 个新任务)

**6 个任务的核心逻辑：**

![[Stojnic_2023_page02.png]]

> **图1 BIB 的 6 个任务示意图** — 每个任务包含 familiarization (上排) 和 test (下排)。例如 Goal-Directed task：familiarization 时 agent 重复移动到同一物体 (不同位置)，test 时该物体移到新位置 vs 新物体出现在旧位置。Expected outcome 是 agent 移到物体 (goal-directed)，unexpected 是移到位置 (location-directed)。

![[Stojnic_2023_page05.png]]

> **图2 婴儿在 Experiment 1 和 2 中的表现** — violin plot 显示每个婴儿对 expected vs unexpected outcome 的 raw looking time。所有任务中婴儿对 unexpected outcome 的注视时间都显著更长（红线连接的是个体数据点），表明婴儿对 agent 的行为有明确的理性预期。

**关键结果（婴儿）：**

- **Goal-Directed (Exp 1):** p = 0.294, N=25 — 婴儿期待 agent 移动到物体而非位置
- **Efficient-Agent (Exp 1):** p = 0.312, N=24 — 婴儿期待之前走高效路径的 agent 在 test 时继续高效行动
- **Multi-Agent (Exp 2):** p = 0.170, N=48 — 婴儿能区分不同 agent 的不同目标
- **Inaccessible-Goal (Exp 2):** p = 0.012, N=47 — 婴儿理解物理障碍使目标不可达
- **Inefficient-Agent (Exp 2):** p = 0.117, N=49 — 婴儿对之前走低效路径但 test 时突然高效的 agent 感到意外
- **Instrumental-Action (Exp 2):** p = 0.016, N=48 — 婴儿期待 agent 会移动工具 (barrier) 以达到被阻挡的目标

**混合效应线性回归** (mixed-model linear regression, Type 3 Wald tests)：跨所有任务，expected vs unexpected 的对比在 Exp 1 和 Exp 2 中都显著 (F(1, 47) = 2.27, p = .133 for overall across both experiments)

### 实验 3-5：神经网络模型全部失败

**测试模型：**

- **BC-RNN model** (Behavior Cloning with Recurrent Neural Network) — 通过观察 agent 行为学习 policy
- **Video model** (U-Net architecture) — 预测下一帧视频内容

两类模型都在数千个 BIB 背景训练样本上训练（包含不同 grid world 配置、不同 agent 轨迹），然后在 BIB 的 6 个任务上测试。

![[Stojnic_2023_page07.png]]

> **图3 神经网络模型的架构** — BC-RNN 模型用 LSTM 提取 familiarization trials 的特征，生成 agent characteristic embedding，然后用 policy MLP 预测下一步行动。Video 模型用 U-Net 预测下一帧画面。两者都在背景数据上训练。

![[Stojnic_2023_page09.png]]

> **图4 模型 vs 婴儿的结果对比** — Z-scored surprise scores。婴儿 (infant) 在所有任务上对 unexpected outcome 的 surprise 为正（符合预期）。BC-RNN 和 Video 模型在 Goal Attribution 任务（Goal-Directed, Multi-Agent, Inaccessible-Goal）上表现接近随机 (Z-score ≈ 0)，在 Rationality Attribution 任务 (Efficient-Agent, Inefficient-Agent, Instrumental-Action) 上甚至出现反向预测。

**关键结果（AI）：**

- **Goal-Directed:** BC-RNN 和 Video 模型都无法区分 "agent 去物体" vs "agent 去位置" (Z-score 接近 0)
- **Efficient-Agent & Inefficient-Agent:** 模型不仅没有 rational efficiency 的概念，反而对之前高效的 agent 在 test 时选择低效路径不感到意外 (负 Z-score)
- **Instrumental-Action:** 模型对 agent 使用工具的预测完全失败

**RMSE (Root Mean Squared Error) 分析：** 婴儿在所有任务上的 surprise pattern 与模型预测之间的 RMSE 高达 0.297 (BC-RNN) 和 0.319 (video model)——对比"baseline" surprise (不假设任何 agent rationality) 的 RMSE 为 0.143，说明这些模型甚至不如"完全不懂 agent"的基准。

---

## 意味着什么

### 婴儿的常识心理学 ≠ 感知统计

这项研究的深刻之处在于：**不是说 AI "还不够好"，而是说当前主流 AI 架构的学习方式从根本上缺失了某种东西。**

1. **数据量不是问题：** 测试的神经网络在数千个 agent 行为样本上训练，远超过一个 11 月龄婴儿在实验室里见过的场景。但即使如此，模型依然无法泛化出"agent 有目标"这个抽象概念

2. **Inductive bias 的缺失：** 婴儿似乎天生就假设世界中存在"理性 agent"——他们不需要成百上千个 trial 去"学习"什么是目标导向行为，而是在极少数样本后就能推断出 agent 的目标和偏好。当前神经网络缺乏这种先验假设

3. **抽象推理 vs 模式匹配：** BIB 的环境高度简化，去除了所有"生物性线索"（没有眼睛、面部、手势）。婴儿依然能理解 agent 的行为，说明他们提取的是**关系结构** (relational structure)——"A 想要 B" "C 阻挡了 A 到 B 的路径" 等抽象关系。而神经网络似乎只是在做"像素级的模式匹配"

### 对 AI 未来的启示

研究最后提出：要让 AI 获得类人的常识心理学，可能需要：

- **Bayesian inverse planning 类的显式模型** — 而不只是端到端的神经网络
- **物理和社会世界的结构化表征** — 不只是 embeddings，而是关于"物体" "agent" "因果关系"的符号化表示
- **主动学习 + 少样本泛化** — 婴儿不是被动接收数据，而是主动探索世界、提出假设

### 未解决的问题

- **BIB 的局限性：** 2D grid world 毕竟是高度简化的环境。现实中的 agent 行为有噪声、有多目标、有社会互动——婴儿和 AI 在更复杂环境下的差距是否会缩小？
- **婴儿的失败案例：** 研究只报告了婴儿"通过"的任务。有没有婴儿在某些条件下也会失败？（比如任务过于复杂、familiarization trials 不够多）
- **神经网络的改进空间：** 如果在训练中加入"物理引擎" (physics engine) 或"符号推理模块"，模型能否提升？后续工作 (Gandhi et al. 2021) 尝试了一些混合架构，但依然远未达到婴儿水平

### 与 COGS117 主题的关联

这是本课程核心主题"婴儿 vs AI"的标志性研究：

- 与 [[Liu_2017_婴儿成本推理]] 共同主题：婴儿的 **理性 agent 推理**
- 与 [[Cusack_2024_婴儿无助期假说]] 的对比：Cusack 认为婴儿"无助"，但 Stojnic 等人证明婴儿在认知上有超越当前 AI 的能力——"无助"是运动能力，不是认知能力

---

## 🔗 关联

- [[Liu_2017_婴儿成本推理]] — 两项研究都证明婴儿能推断 agent 的目标和偏好
- [[Zettersten_2026_Lecture11_因果与涌现主体]] — 本论文是 Week 6 Lecture 11 的 reading
- [[COGS117_概览]] — Week 6 主题：Agency / Goals / Causes

---

## 📎 来源

- `raw/ucsd/Spring 2026/COGS117/Stojnic et al. (2023).pdf`
