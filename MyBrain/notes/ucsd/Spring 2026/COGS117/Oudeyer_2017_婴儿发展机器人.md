---
title: "What do we learn about development from baby robots? (Oudeyer 2017)"
type: source
tags: [认知科学, 发展机器人, 动态系统, 自组织, 内在动机, 好奇心驱动学习, 具身认知]
sources: ["raw/ucsd/Spring 2026/COGS117/Oudeyer (2017).pdf"]
created: 2026-04-22
updated: 2026-04-22
confidence: high
priority: active
---

# What do we learn about development from baby robots?

> Pierre-Yves Oudeyer 2017 综述：把婴儿发展**造出来**才能理解它——机器人是"可编辑的婴儿实验台"，让我们看到行走不是"大脑计算"而是"身体自组织"，发展阶段不是"基因日历"而是"好奇心在动态系统中涌现的吸引子"。

---

## 这项研究在解决什么问题？

婴儿发展是一团乱麻。传统心理学实验一次只能操控 1–2 个变量，但婴儿发展涉及大脑、身体、环境、社交——几十个相互耦合的变量同时演化。**口头描述"它们互动"是容易的，用机器证明"这种互动确实能产生观察到的发展轨迹"才难**。

Oudeyer 的回答：**造一个。** 物理学家靠数学+计算机模拟理解星云和心跳；发展科学家应该靠**会动的机器人**理解婴儿。这是把 Feynman 的名言"What I cannot create I cannot understand"应用到认知发展上。

## 核心结论（一句话）

发展不是"基因在执行程序"也不是"环境在填白板"——它是**身体、神经系统、环境三者在持续交互中自组织**涌现出来的复杂动力系统模式。发展机器人证明了这个主张，同时把"先天 vs 后天"这个老二分法变得没有意义。

## 两个关键示范：走路 & 好奇心驱动的阶段演化

![[Oudeyer_2017_page02_robots_icub_poppy_termites.png]]

> **左图的意义**：iCub 和 3D 打印的 Poppy 是开源机器人平台，允许研究者**系统地改变身体**（例如"直腿 vs 屈腿"），然后看发展结果如何随身体变化——这是把身体变成**实验变量**的新方法。**右图的意义**：白蚁巢的复杂结构是上千只白蚁**无全局计划**局部互动自组织的产物，为"婴儿发展 = 自组织"提供了类比先例。

### 示范 1：走路其实不是"计算"

**传统观点**：走路需要大脑每几毫秒观察身体状态，计算正确的肌肉激活，维持平衡并推进。按这个观点，学会走路 = 学会这套计算。

**颠覆证据（McGeer 被动动态步行机）**：

![[Oudeyer_2017_page03_passive_walker_mcgeer.png]]

> **这张图告诉我们**：McGeer 1990 造的两条机械腿放在斜坡上，**没有发动机、没有电脑、没有传感器**——只靠重力和力学耦合——就走出了与人类步态高度相似的步行，甚至能抵抗扰动。这把"走路需要大脑计算"证伪。

**这意味着什么**：
- 走路是**动力涌现**模式——身体物理本身就"藏着"步行的解
- "先天 vs 学习"在这里**失去意义**：没有基因编码，也没有学习发生，但结构出现了
- 婴儿学走路可能**不是从零计算**，而是**调谐**身体已有的动力学——这与 Thelen 的动态系统观点一致（见 [[Zettersten_2026_Lecture7_走路与动作发展]] 关于 Thelen 1984 stepping reflex 的讨论）

### 示范 2：发展阶段不是"预装日历"

**观察到的现象**：婴儿典型地先控制脖子 → 翻身 → 坐 → 站 → 扶墙走 → 独立走。**但也有变异**：有些婴儿跳过爬行直接走；有些顺序颠倒。为什么**普遍性**和**个体差异**同时存在？

**Playground 实验（Oudeyer 团队）**：

![[Oudeyer_2017_page05_playground_experiment.png]]

> **这张图告诉我们**：给机器人装上一个**好奇心机制**——倾向于探索"学习进步 (learning progress) 最大"的活动——它会自发组织出发展阶段：先随机"身体胡乱动" → 专注用腿碰物体 → 用嘴抓物体 → 与另一机器人发声互动。**工程师没有预编程任何阶段或顺序**。

**好奇心的形式化定义（文中第 5 页）**：
> **"Epistemic curiosity** is a motivational mechanism that pushes an organism to explore activities for the primary sake of gaining information (as opposed to searching for information to achieve an external goal)."

数学化：追求"**刚好超出当前能力水平的**"活动——既不是已经会的（无聊），也不是完全不会的（太难）——这是 Vygotsky "最近发展区 (zone of proximal development)" 的计算版本。

**这意味着什么**：
- 相同参数重复实验，**阶段常常重现但偶尔会变**——这对应到数学里的"吸引子 (attractor)"和"吸引域 (basin of attraction)"
- **普遍性 ≠ 预装程序**；**差异 ≠ 故障**。两者都是**复杂系统的自然产物**——同一机制在不同初始条件下产生不同发展路径
- 阶段不需要"成熟日历"来解释——**短期的局部机制（好奇心、学习、身体-环境互动）自组织出长期的宏观结构**

## 对发展科学的含义

### 方法论
机器人互补（不取代）心理学和神经科学：
- 心理学：可以一次测几个变量
- 机器人：可以同时让几十个机制互动，看行为如何涌现
- 两者合力 → 理解复杂系统

### 理论
- **"先天 vs 后天"争论应该让位于"什么在与什么互动"**
- 发展 = 多层次、多时间尺度的耦合动力系统
- 身体**不是外设**，是塑造认知的核心变量

### 对 AI 的反向启发
- 从零学起（tabula rasa）在真实世界做不到——需要身体和约束
- 预编程成年智能的 AI 走不远（Oudeyer 明确引用 Turing 关于"模仿儿童比模仿成人更合理"的话）

## 技术细节

### 引用的经典工作
- Turing (1950)：提议模仿儿童心智而非成人
- McGeer (1990)：被动动态步行机（*IEEE Robotics & Automation Conference*）
- Collins et al. (2005, *Science*)：被动动态步行机的跑步机扩展
- Thelen & Smith (1994)：动态系统方法（MIT Press）
- Oudeyer & Kaplan (2007)：内在动机的计算类型学（*Front. Neurorobot.*）
- Gottlieb, Oudeyer, Lopes, Baranes (2013, *Trends Cogn Sci*)：好奇心的计算和神经机制

### 开源平台
- **iCub**（http://www.icub.org）：欧洲研究合作开发的婴儿型类人机器人
- **Poppy**（http://www.poppy-project.org）：3D 打印类人平台，可快速修改身体形态

### Playground 实验视频
https://www.youtube.com/watch?v=uAoNzHjzzys

## 🔗 关联

- [[Adolph_2018_走路发展15条建议]] — Adolph 用行为数据支撑同一个动态系统观点；两者在"婴儿学走路"这件事上结论一致
- [[Zettersten_2026_Lecture4_发展理论]] — 动态系统假设的课堂总论
- [[Zettersten_2026_Lecture7_走路与动作发展]] — Thelen 1984 stepping reflex 实验是此文观点的实验依据
- [[Zettersten_2025_婴儿主动学习]] — 主动学习派的理论根据之一正是好奇心驱动
- [[动作发展]] — 本文是动作发展动态系统派的核心文献
- [[内在动机与好奇心驱动学习]] — 本文提出好奇心的形式化定义
- [[发展级联]] — 身体与环境互动导致阶段涌现，与 Adolph 级联观相连

## 📎 来源

- `raw/ucsd/Spring 2026/COGS117/Oudeyer (2017).pdf`
- Oudeyer, P.-Y. (2017). What do we learn about development from baby robots? *WIREs Cognitive Science*, 8:e1395. doi:10.1002/wcs.1395
