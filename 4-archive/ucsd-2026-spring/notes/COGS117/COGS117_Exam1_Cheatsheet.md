---
title: "COGS117 Exam 1 Cheatsheet — 高密度速记表"
type: source
tags: [COGS117, Exam1, Cheatsheet, 考试]
sources: ["所有 Week 1-4 讲座和阅读笔记的汇总"]
created: 2026-04-23
updated: 2026-04-23
confidence: high
priority: active
---

# COGS117 Exam 1 Cheatsheet

> Week 1–4 全部考点单页速记。打印后考场直接用。左右两栏结构便于扫读。

---

## 🧪 ① 实验方法 Experimental Methods

**婴儿研究核心难点**：不合作、无语言、注意短 → 需**间接方法**。

**五大方法家族**：
1. **Parental report**（CDI / Wordbank）— 低成本、跨语言；缺：家长偏差、只测"有/无"
2. **Naturalistic observation**（SEEDLingS, SAYCam, 头戴相机）— 婴儿第一视角；**发现婴儿视觉输入高度偏斜**（几个熟悉面孔 + 少量高频物体，**不**像 ImageNet）
3. **Behavioral paradigms**（看时长范式，主力）
4. **Neuroimaging**（EEG / fNIRS / fMRI）
5. **Computational modeling**（贝叶斯 + 神经网络）

**看时长三范式（必须区分）**：

| 范式 | 呈现 | 测 | 逻辑 |
|------|------|---|------|
| **Preferential looking** 偏好观看 | 两刺激**并排同时** | 区分 + 偏好 | 看久 = 偏好 |
| **Habituation** 习惯化 | 单刺激反复到看腻 → 换新 | 区分 A vs B | 看时恢复 = 区分（dishabituation）|
| **Violation of Expectation (VoE)** | 习惯化后呈现"可能 vs 不可能" | 理解**规则** | 看"不可能"久 = 有被违反的预期 |

**神经成像对比**：

| 方法 | 时间 | 空间 | 运动容忍 | 婴儿场景 |
|------|------|------|---------|---------|
| **EEG / ERP** | ⭐⭐⭐⭐⭐ ms | ⭐ 差 | 中 | 戴帽子 OK |
| **fNIRS** | ⭐⭐ 秒 | ⭐⭐⭐ 仅皮层 | **⭐⭐⭐⭐** | **清醒、自然互动最佳** |
| **fMRI** | ⭐⭐⭐ 秒 | ⭐⭐⭐⭐⭐ 全脑 | ⭐ | **仅睡眠扫描** |

**口诀**：**EEG = 时间，fMRI = 空间，fNIRS = 折中 + 自然**。

**测量质量**：**Reliability** 稳定（多次/多评分者一致）+ **Validity** 测对（真的测到想测的建构）。信度是效度的必要不充分条件。

---

## 🧮 ② 模型 Models

**Marr 三层级**：**Computational**（what/why）→ **Representational/Algorithmic**（how）→ **Implementational**（hardware/brain）

**Box 1976**：*"All models are wrong, but some are useful."*
**建模目的**（考点陷阱）：桥接理论与数据 / 显式化假设 / 假设检验 / 迫使抽象 — **NOT** maximize fit（这是 ML benchmarking，不是科学建模）

### 两大框架

| | **贝叶斯** | **神经网络** |
|---|---|---|
| 婴儿类比 | 理性学习者 | 统计引擎 |
| 问题 | 有限数据下如何推断？ | 如何提取海量模式？ |
| Notebook | Notebook 2 | **Notebook 1**（4/28 due）|

**Bayes' Theorem**：
$$\underbrace{P(H|D)}_{\text{posterior 后验}} = \frac{\overbrace{P(D|H)}^{\text{likelihood 似然}} \cdot \overbrace{P(H)}^{\text{prior 先验}}}{P(D)}$$

- **Prior** = 看数据**前**假设概率（例：核心知识）
- **Likelihood** = **若**假设真，看到这数据的概率
- **Posterior** = 看数据**后**的更新信念

**Xu & Tenenbaum (2007) 词学习**："fep" + 三只达尔马提亚 → 窄假设（Dalmatians）似然高（size principle），宽假设（mammals）的话只见达尔马提亚是可疑巧合 → 后验倾向窄假设。

**医学检测例**：疾病率 1% + 敏感度 80% + 假阳 10% → 阳性真正患病只 ~7.5%；**频率表达**（1000 人中 X 人）能纠正直觉。

### 神经网络

**基本组件**：Input units / Hidden units / Output units / **Weights**（学习的核心）/ **Non-linear activation function**

**OR vs XOR**：OR 线性可分 → 单层可解；**XOR 非线性可分 → 必须有 hidden layer**（Minsky & Papert 1969 杀死感知器，Rumelhart/Hinton 1986 backprop 复兴）

**Backpropagation 三步**：
1. 前向：算输出 → 对比目标 → 得**误差**
2. 反向：把误差传回各层
3. 按每个权重对误差的**贡献**调整

### 三种学习类型（必背）

| 类型 | Teaching signal | 信号来源 | 原型 |
|------|----------------|---------|------|
| **Supervised** | ✅ | 外部教师 | 放射科学生读片被告知答案 |
| **Unsupervised** | ❌ | — | **Saffran 1996 婴儿分词**、k-means |
| **Self-supervised** | ✅ | 从数据**自造** | **LLM** 预测下一词、BERT 掩码 |
| Reinforcement | ✅ | 环境奖励 | 婴儿哭→有人来 |

**Love (2026) 核心主张**：supervised 和 unsupervised 是**连续谱**（continuum），不是二元；类别标签可看作"另一个特征"，允许任意混合。

**Supervised vs Unsupervised 的关键差别** = **有无 correction / teaching signal**（不是数据量、不是架构、不是任务类型）。

---

## 📚 ③ 理论 Theories

### 条件反射

- **Classical (Pavlov)**：中性刺激（铃）+ 无条件刺激（食）→ 中性刺激引发条件反应（流口水）
- **Operant (Skinner/Thorndike)**：行为 → 结果（奖/惩）→ 改变行为频率

### 行为主义 → 认知革命

**行为主义 (Watson, Skinner)**：只研究**可观察行为**；心理过程不是科学主题；所有行为 = 环境塑造的刺激–反应链。

**反驳 → 认知革命**：
- Chomsky **"poverty of the stimulus"**：语言输入远不足以解释儿童习得速度 → 必须有先天结构
- Tolman **潜伏学习**（latent learning）：老鼠无奖励也能学迷宫 → 内部认知地图
- Miller **工作记忆**（7±2 chunks）→ 内部表征真实存在

### Piaget 的建构主义

**四阶段**：**Sensorimotor (0–2) → Preoperational (2–7) → Concrete Operational (7–11) → Formal Operational (11+)**

**核心机制**：
- **Schema** 图式 — 内部认知结构
- **Assimilation** 同化 — 把新经验纳入已有图式
- **Accommodation** 顺应 — 新经验不适配时修改图式
- **儿童是主动建构者**（这是 Piaget 最核心被保留的洞见）

**经典实验遗产**：
- **物体永恒性**（Piaget：8 月才有 → 现代：Baillargeon 2.5 月就有）
- **A-not-B 误差**（见下文）
- **守恒任务**（水量、数量、质量）

### Piaget 后的革新

**A-not-B 误差的新解释**：
- **旧 (Piaget)**：缺 object permanence
- **新 (Diamond 1985, Thelen)**：**有**永恒性，但**前额叶抑制控制**不成熟——执行问题，不是表征问题；"知道"≠"做到"

**Baillargeon (1987)**：用 VoE 证明 **2.5 月**物体永恒性 — 远早于 Piaget 预言

**其他早熟能力**：Kellman & Spelke 4 月物体统一性；Xu 10 月小数字追踪

### Vygotsky 社会文化理论

- **ZPD (Zone of Proximal Development)** — 独立能做 vs 在支架下能做 之间的区域
- **Scaffolding** 支架 — 成人/同伴提供的临时帮助
- 发展**根本上是社会的**；语言是思维的工具
- **对比 Piaget**：Piaget 儿童独自探索；Vygotsky 儿童在互动中学习

### 动态系统理论（Thelen, Smith, Adolph）

- 发展 = 多个**互相耦合**子系统（身体、神经、环境）共同演化
- 无中央控制器，能力**自组织**涌现
- 行为是**吸引子**，不是阶段
- **Thelen 1984 stepping reflex 体重实验**：反射"消失"不是神经原因，是**腿变重**；挂配重使其消失、浸水使其重现 → 颠覆成熟论

### Spelke 核心知识（domain-specific 代表）

**5 个核心系统**：**物体 / 主体 (agents) / 数量 (number) / 空间 (space) / 社会伙伴**

**物体的 4 条先验（必背）**：

| 先验 | 英文 | 规则 | 违反场景 |
|------|------|------|---------|
| 凝聚性 | **Cohesion** | 物体是连贯整体 | 棒子拉动时中间断开 |
| 连续性 | **Continuity** | 走连续路径，不瞬移 | 物体消失→另处出现 |
| 接触性 | **Contact** | 影响彼此要靠接触 | 球自动滚 |
| 支撑性 | **Support** | 需要支撑否则掉 | 物体悬浮 |

**口诀**：**整体 · 连续 · 接触 · 支撑**

### Domain-general vs Domain-specific

- **General**：**一个**通用学习机制（统计学习、神经网络）处理所有领域 — 连接主义 / 贝叶斯 / 信息加工
- **Specific**：**多个**为特定领域（物体、数字、语言）专化的系统 — Spelke 核心知识 / 模块论

### 婴儿"无助"的多种解释

1. **产科困境 (Obstetrical Dilemma)**：双足限制骨盆 → 早产 → 脑不成熟
2. **Bogin 保护性不成熟 (Protected Immaturity)**：进化策略，用无助期换更大/更慢熟的大脑（支持后期语言、工具、社交）
3. **Cusack (2024) 自监督预训练**：无助期 = 学习基础表征的"pretraining phase"（基础模型类比）
4. **Zettersten (2025) 反驳**：婴儿从出生就是**主动、目标导向、嵌入社会**的智能体 — 非被动

### ⭐ Cusack vs Zettersten 辩论（高频考点）

| 维度 | **Cusack et al. (2024)** | **Zettersten et al. (2025)** |
|------|--------------------------|------------------------------|
| 无助期本质 | 自监督预训练期 | 主动、目标导向 |
| 学习模式 | 统计学习→后接行动（两阶段）| 统计学习**从一开始就和行动整合** |
| 基础模型类比 | 成立 | 缺少主动性、变异、社会生态、具身 |
| 发展变异 | 弱化 | 强化（跨文化、个体差异）|
| **同意点** | 统计学习早期就重要 | ← 同意 |
| **分歧点** | 学习先于行动 | 学习**与**行动整合 |

---

## 👁️ ④ 感知与类别 Perceptual Categories

### 视觉发展里程碑

| 月龄 | 能力 |
|------|------|
| 新生儿 | 视敏度 **20/200–20/400**（法律盲水平）；高对比度 + 中空间频率优化 |
| 2 月 | 双眼深度知觉（disparity）；颜色扩到蓝–黄 |
| 3–4 月 | **形状习惯化**、**gestalt 原则**、**物体统一性**（Kellman & Spelke）、**语言开始塑造视觉注意** |
| 4–6 月 | 视点不变性成熟 |
| 6 月 | 全球音素 + 他族面孔 + 腹侧皮层对形状敏感（Ayzenberg fNIRS）+ Emberson top-down 预测 |
| **6–9 月** | **Perceptual biases 形成期**（关键窗口）|
| 9 月 | 只剩本族面孔（若无个体化训练）|
| 10 月 | 小数字追踪（Xu 双屏幕）、物体永恒性稳定 |
| 12 月 | 母语音素专化完成 |

**口诀**：**子宫听，出生模糊，6 月全球，9 月专化**

### 面孔感知

- **Farroni 2005**：新生儿偏好 **top-heavy 模式**（点多在上方）→ **CONSPEC 假说**：不是高层"面孔检测"，是低空间频率拓扑偏好
- 面孔是婴儿视觉输入的**主要占比**（Jayaraman, Fausey, Smith）
- 新生儿视敏度刚好够 **50 cm 内辨面**（哺乳姿势距离的进化巧合）

### 物体感知 & 核心知识

- **Kellman & Spelke 1983**：4 月婴儿期待被遮挡的棒子是**完整一根**（VoE）
- **Xu 2007 双屏幕**：10 月能追踪"左屏 1 + 右屏 1 = 2"；看到只有 1 只时惊讶
- **Spelke 四条先验**（见理论栏）

### 感知窄化 Perceptual Narrowing

**定义（Johnson 2024 精确措辞）**：**"A decline in the ability to discriminate unfamiliar types of stimuli during the first year of life."**

**跨领域窄化**（时间平行 → 共享机制）：
- **面孔**：6 月能辨人脸+猴脸 → 9 月只辨人脸
- **语音**：6 月能辨全球音素 → 12 月只辨母语
- **情绪**：类似文化-特异窄化

**窄化 ≠ 丢失** — 成人通过训练可恢复（资源重分配，非物理删除）

### ⭐ Scott & Monesson (2009) 三组实验（**必考**）

6 月龄婴儿 3 个月猴脸训练，9 月龄测猴脸辨别：
- **Individual label 组**（"这是 Dario、这是 Boris"）：**辨别保留** ✅
- **Category label 组**（"这都是 monkey"）：窄化，失去辨别 ❌
- **No label 组**（只看不说）：窄化，失去辨别 ❌

**教训**：窄化不是"用进废退"的曝光量问题，是**加工粒度**（individual vs category）的问题。

### 双语窄化特殊

**Bilingual infants retain the ability to discriminate non-native sounds and visual speech cues *longer* than monolingual infants**（双语窄化延迟）

### 类别发展：Global-to-Basic Shift

- **Mandler 1991**：婴儿先掌握**全局级**类别（动物 vs 车辆，9 月）→ 后掌握**基本级**（狗 vs 鱼，11+ 月）
- 成人则对**基本级最敏锐**——发展方向**相反**
- **Quinn & Eimas 1996**：3–4 月已能分"哺乳动物 vs 家具"（习惯化版）
- **Quinn 猫狗不对称**：习惯化到"猫"能辨"狗"；习惯化到"狗"不能辨"猫"——因为狗视觉变异大，学了"宽"范畴 → 特征统计能解释（连接主义模型可复现）

### 形状 vs 纹理（Ayzenberg & Behrmann 2024）

- **成人和大儿童优先用 shape**（不是 texture、color、size）
- **6 月腹侧颞叶**对形状敏感（fNIRS）
- **骨架 (skeletal) 表征**支持视点不变性（一只狗不同角度骨架图几乎不变）
- **面孔剥夺猕猴实验**：盖面孔养育 → 面孔识别受损，**但物体识别正常** → 物体识别**不依赖**面孔经验；腹侧通路两分支独立
- **6 月婴儿在 one-shot 形状分类上超过 ResNet**（Ayzenberg & Lourenco 2022）→ 归纳偏置的力量

### 标签支持个体化

- **Xu 2007**：9 月龄用两个不同标签（"duck! ball!"）能分辨两个物体；共享标签或不同音调不行
- **LaTourrette & Waxman 2019**：半监督学习在婴儿身上真实存在——**标签和无标签试验相互影响**

### 自上而下预期（Emberson 2015）

fNIRS：6 月龄婴儿学了"声 A → 视 V"关联后，**省略视觉刺激**时视觉皮层**仍产生响应** → 预测编码已在婴儿脑运转。

### Clerkin & Smith (2017) 视觉分布

婴儿物体曝光分布**极度偏斜**——少数物体占大部分时间 → 婴儿"训练数据" ≠ ImageNet 的均匀多样采样 → **curriculum design** 或许比扩规模更重要。

### 听觉 & 跨模态

- **听觉始于子宫内**（**In the womb**）
- 视觉和听觉都经历 **perceptual tuning**（共同机制）
- 新生儿就有跨模态绑定（声音-画面对齐）

---

## 🚶 ⑤ 动作发展 Motor Development

### 为什么走路难？**Moravec 悖论**

> AI 容易的事（下棋、定理）对人难；AI 最难的事（走路、识别物体）对 1 岁婴儿毫不费力。进化优化了感知-运动 5 亿年，符号推理才几万年。

### 反射（进化遗迹）

- **Grasping** 抓握、**Rooting** 根触、**Sucking** 吸吮、**Stepping** 踏步
- 这些是先天固定动作模式，跨灵长类共享

### ⭐ Thelen 1984 Stepping Reflex 实验（颠覆成熟论）

**现象**：stepping reflex 约 2 月消失。
**旧解释**：皮层成熟把皮层下反射压下去（神经原因）
**Thelen 证据**：
- 给**有反射**的婴儿**挂配重** → 反射消失
- 把**失去反射**的婴儿**浸入水中**（浮力减重）→ 反射**重现**

**结论**：反射不是"消失"，是**腿变重举不起来了** → **发展的变化不等于神经的变化** → 动态系统观点标志性证据

### 成熟论 vs 动态系统

| | **Maturational View** | **Dynamic Systems** |
|---|---|---|
| 驱动 | 基因蓝图 | 多系统耦合自组织 |
| 顺序 | 普遍固定 | 局部约束涌现 |
| 跨文化 | 普遍一致 | 因育儿方式差异巨大 |
| 代表 | 经典里程碑表 | Thelen, Smith, Adolph |

### Adolph et al. (2018) 15 条建议（**必考**）

- **里程碑图误导性**：跳过里程碑是常态；日采样显示技能**断续闪烁**而非阶跃；"爬行必须在走路前"被跨文化证据证伪
- **描述统计 ≠ 规范标准**（WHO 标准被误读为"每个婴儿都应达到"）
- 典型幼童自由游戏每小时 **2400 步 / 跌倒 17 次**；73% 路径是曲线；82% 含后退侧步
- **发展 = 多组件 / 嵌套时间尺度 / 级联**——不是单一机制
- Box 1：**15 条建议在语言发展上同样成立**（跨内容域一般原则）

### 跨文化差异（打脸"普遍阶段论"）

- **训练更早**：非洲 Bambara、西印度、中国——婴儿 4 月能独立站
- **延迟**：美国原住民摇篮板、中国沙袋育婴、塔吉克 gahvora
- Miner 1956 "Body Ritual among the Nacirema"（American 反读）讽刺文化盲区

### Oudeyer (2017) 被动动态步行机

- **McGeer 1990**：两条机械腿 + 斜坡 → **无发动机、无电脑、无传感器**也能走出类人步态
- **启示**：走路是**动力涌现**；"先天 vs 学习"在此失效；身体物理本身就藏着解
- **Playground 实验**：给机器人内在好奇心（追学习进步最大的活动）→ 自发组织出发展阶段（没有预编程）→ **普遍性 ≠ 预装，差异 ≠ 故障**

### ⭐ 新生儿模仿争议（3 方辩论）

| | **Meltzoff & Moore 1977** | **Jones 1996+** | **Oostenbroek 2016** |
|---|---|---|---|
| 主张 | 新生儿能模仿吐舌/张嘴 | 是一般性兴奋反应（吐舌对任何刺激都出现）| N=106 找不到选择性模仿 |
| 证据强度 | 原始 N=6–12 | 理论替代解释 | 迄今最大纵向研究 |

**当前共识**：**天生模仿**说法站不住脚；但模仿随发展会出现（Jones 2006）。ManyBabies 6 决定性。

### ⭐ 发展级联 Developmental Cascades

**Adolph 建议 15 的核心**：新技能引发跨域变化。

**走路 → 更多发展**（Walle & Campos 2014 等）：
- 走路**独立于年龄**地与词汇量相关
- 走路改变**视角**（看远处、看父母指方向）
- 走路改变**互动**（主动靠近、带东西）
- 走路改变**父母言语**（更多样、更指令化）

```
动作能力变化 → 视角变化 → 知觉变化 → 认知变化
```

**对 Cusack 的直接挑战**：若"无助期越长表征越好"成立，早走路应预测晚语言——但实际是**早走路预测早语言**，与 Cusack 预测方向**相反**。

### Self-Organization

- 没有"爬行基因"或"爬行回路"
- 爬行是**婴儿自己发现**的"如何移动自己"的解决方案
- 不同婴儿有肚皮爬、四肢爬、熊爬、翻滚 — 同一任务多种解

---

## 📖 每篇 Reading 一行摘要

| 文献 | 核心主张 | 证据 |
|------|---------|------|
| **Frank (2023)** 数据鸿沟 | LLM 训练数据是儿童的 **3–5 数量级**；儿童高效得益于：**先天知识 + 多模态接地 + 社会互动** | 量化比较、BabyLM Challenge |
| **Cusack (2024)** 婴儿=基础模型 | 无助期 = **自监督预训练**；两阶段：编码（无助期）→ 微调（后续）| 跨物种神经发育对齐、新生儿 RSN |
| **Zettersten (2025)** 主动学习 | 婴儿是**主动、目标导向、社会嵌入**的智能体；统计学习与目标从出生就整合 | 早期应急、跨文化变异、适应行为 |
| **Love (2026)** 监督 vs 无监督 | 两者是**连续谱**；自监督 = 把无监督转化为监督 | SUSTAIN 模型、LLM 机制 |
| **Johnson (2024)** 婴儿感知 | 视/听/跨模态/物体感知的综述地图；**窄化跨通道普遍**；**感知 tuning 是视听共同机制** | 时间线、窄化、跨模态绑定 |
| **Scott & Monesson (2009)** 面孔偏差起源 | 窄化受**加工粒度**调节（individual vs category），不是曝光量；**individual label 组**唯一保留猴脸辨别 | 三组对照实验 |
| **Ayzenberg & Behrmann (2024)** 视觉物体识别 | 形状/骨架是识别主通道；**6 月腹侧皮层已对形状敏感**；**物体识别不依赖面孔经验**（面孔剥夺猴）；one-shot 婴儿>ResNet | fNIRS、习惯化、面孔剥夺、行为 |
| **Adolph et al. (2018)** 15 条建议 | 里程碑误导；发展 = 多组件、级联、变异；普适教训适用所有发展领域 | 2400 步/小时、跨文化、Box 1 映射到语言 |
| **Oudeyer (2017)** 发展机器人 | 造出来才懂；走路 = 动力涌现（McGeer）；好奇心驱动阶段自组织 | iCub/Poppy、Playground 实验 |

---

## ⚠️ 易错 & 陷阱点

1. **A-not-B = 执行问题，NOT 表征问题**（Piaget 错了）
2. **建模 ≠ maximize fit**（Box 1976）
3. **Saffran 分词 = unsupervised**（无 teaching signal）；**LLM = self-supervised**（从数据生成 signal）
4. **反射 ≠ goal-directed**（coughing 不是 goal-directed learning）
5. **Reliability 高 ≠ Validity 高**（稳定可以测错东西）
6. **Reliability 是 Validity 的必要条件**
7. **婴儿视觉输入高度偏斜**（不是 ImageNet）
8. **Perceptual narrowing = 丢失辨别力，不是生理丢失**（资源重分配）
9. **Scott 2009：唯一保留猴脸辨别的是 individual-level labeling 组**
10. **Thelen 1984：stepping reflex "消失" = 腿变重，NOT 神经原因**
11. **发展级联：早走路预测早语言**（打脸 Cusack 预测方向）
12. **Bilingual 窄化延迟**（保留非母语辨别更久）
13. **Perceptual biases 形成于 6–9 月**（精确时间点）
14. **Gestalt 原则 ~ 4 月**；**听觉始于子宫内**

---

## 🔑 关键日期 / 名字 / 数字锁定

- **20/200–20/400** = 新生儿视敏度
- **2.5 月** = Baillargeon 物体永恒性
- **4 月** = Kellman & Spelke 物体统一性、gestalt
- **6 月** = 腹侧皮层形状敏感、Emberson top-down、perceptual biases 开始
- **6–9 月** = perceptual biases 形成
- **9 月** = 面孔窄化完成
- **10 月** = Xu 小数字追踪
- **12 月** = 音素窄化完成
- **2400 步/小时** = Adolph 自由游戏
- **N=106** = Oostenbroek 模仿研究
- **3–5 数量级** = Frank 数据鸿沟

**理论家 ↔ 术语**：
- Piaget ↔ 阶段、同化、顺应、schema
- Vygotsky ↔ ZPD、scaffolding、社会文化
- Spelke ↔ 核心知识、cohesion/continuity/contact/support
- Skinner/Watson ↔ 行为主义、operant conditioning
- Pavlov ↔ classical conditioning
- Chomsky ↔ poverty of the stimulus、认知革命
- Tolman ↔ 潜伏学习、认知地图
- Thelen ↔ 动态系统、stepping reflex、A-not-B 新解
- Cusack ↔ 无助 = 自监督预训练、两阶段
- Zettersten ↔ 主动目标导向、统计 + 行动整合
- Adolph ↔ 15 建议、里程碑误导、级联
- Oudeyer ↔ 发展机器人、好奇心、McGeer
- Frank ↔ 数据鸿沟 3 因素
- Scott & Monesson ↔ 三组标签、加工粒度
- Ayzenberg & Behrmann ↔ 形状 > 纹理、骨架、面孔剥夺猴
- Baillargeon ↔ 2.5 月物体永恒性、VoE drawbridge
- Saffran ↔ 统计学习分词（unsupervised）
- Xu & Tenenbaum ↔ 贝叶斯词学习、size principle
- Farroni ↔ top-heavy、CONSPEC
- Emberson ↔ fNIRS top-down 预测
- Diamond ↔ 前额叶抑制控制 → A-not-B 新解
- Minsky & Papert ↔ XOR、感知器局限
- Rumelhart/McClelland/Hinton ↔ backpropagation、UCSD

---

## 📋 考场扫读优先级

**如果考前 5 分钟最后一看**，看这 8 点：
1. **三范式**：Preferential（并排）/ Habituation（看腻→新）/ VoE（不可能看久）
2. **A-not-B = 执行问题**
3. **Bayes**：Prior（前）/ Likelihood（给定 H 看到 D）/ Posterior（后）
4. **三种学习** teaching signal：无（unsup）/ 外部（sup）/ 自造（self-sup）
5. **Cusack vs Zettersten**：同意统计学习；分歧在学习与行动关系
6. **Spelke 四先验**：cohesion / continuity / contact / support
7. **Scott 三组**：individual label 保留；category/none 丢失
8. **Thelen 体重实验**：反射消失 = 腿重 ≠ 神经

---

祝考试顺利！🎯
