---
title: "COGS117 过往周 Quiz 原题与考试风格分析"
type: source
tags: [COGS117, 考试, Quiz, 考点分析, 期中复习]
sources: ["用户提供（chat，2026-04-22）"]
created: 2026-04-22
updated: 2026-04-22
confidence: high
priority: active
---

# COGS117 过往周 Quiz 原题与考试风格分析

> 用户在 Exam 1 前一晚提供的 Week 1、Week 2 真实 quiz 题目。这是**出题风格**和**真实考点**的最佳参考样本——比任何对课程结构的推测都直接。

---

## 为什么这份材料重要

- **真实风格参考**：出自同一讲师/TA，Exam 1 极可能沿用这些出题习惯
- **真实考点锚定**：能过筛出哪些细节被判为"必考级"
- **题型分布已知**：单选、多选、填空、匹配都有先例

---

## 考试风格特征（提炼）

### 题型分布
| 题型 | Week 1 | Week 2 | 占比 |
|------|--------|--------|------|
| 4 选 1 单选 | 7 | 8 | 主力 |
| 多选 (Select all that apply) | 1 | 0 | 偶尔 |
| 填空 | 1 | 1 | 偶尔 |
| 匹配 (Match) | 0 | 1 | 偶尔 |

**Exam 1 合理预期**：50–60 题以 4 选 1 为主，夹杂 1–3 道填空/多选/匹配。

### 出题风格五大特征

1. **认人（按作者查立场）**
   - "According to Cusack et al. (2024), what is X?"
   - "Which of the following would Zettersten et al. (2025) most likely agree with?"
   - → 期末必考：**谁说了什么**、**两派分歧在哪**、**两派共识在哪**

2. **认时间点**（窄化、里程碑、感知发展时间节点具体到月）
   - "Perceptual biases are formed between 6 to 9 months of age"
   - "When are infants thought to begin to use gestalt principles in shape perception? By 4 months"
   - → 需要准确记住几个关键时间锚点

3. **认定义的精确措辞**
   - "perceptual narrowing = a decline in the ability to discriminate **unfamiliar types of stimuli** during the first year of life"
   - → 不能只懂大意，要记准确短语

4. **认实验的具体条件**
   - Scott & Monesson 的三组：exposure / category-level / **individual-level** 标签
   - → 记得住三组的区别，以及谁是唯一保持辨别力的组

5. **概念分类题**
   - "Which learning type does 婴儿 word segmentation 属于？ → unsupervised"
   - "LLM relies on ___ learning → self-supervised"
   - → 对每种学习类型要能给出原型实例

### 分散点（易错陷阱）

- **监督 vs 无监督的关键差别** = "whether the learner receives correction / teaching signal"（不是数据量、不是语言、不是模型架构）
- **自监督 vs 无监督**：LLM 是**自监督**（从数据自己生成监督信号，比如"下一个词"），不是纯无监督
- **婴儿统计学习分词（Saffran）** = **无监督**（完全没有外部信号）

---

## Week 1 Quiz 原题（Cusack / Zettersten / 监督学习）

### Q1. According to Cusack et al. (2024), what is helplessness?
- ✅ **Reliance on caregivers stemming from undeveloped adaptive behaviors.**

### Q2. Cusack et al. (2024) 的 two-stage theory
- ✅ **Self-supervised learning first (building sensory representations without acting on them), followed by supervised or reinforcement learning once other cognitive functions develop.**

### Q3. Zettersten et al. (2025) 最可能同意的
- ✅ **Statistical learning is integrated across domains**

### Q4. 两派 agree / push back
- ✅ **They agree that statistical learning is important for early development, but challenge the idea that this learning is initially disconnected from goals and actions.**

### Q5. Goal-driven learning 的例子（Select all that apply）
- ✅ Seeking eye contact to attract caregivers
- ✅ Targeted crying to elicit caregiver response
- ✅ Word learning being driven by a desire to communicate
- ❌ Coughing to avoid choking（反射，不是目标导向学习）

### Q6. Supervised vs unsupervised 的关键差别
- ✅ **Whether or not the learner receives correction during learning**

### Q7. 填空：LLM 依赖 ___ learning
- ✅ **self-supervised**

### Q8. 婴儿 word segmentation 是哪种学习？
- ✅ **Unsupervised learning. Structure is extracted from raw input without any external teaching signal.**
- 关键：Saffran 1996 范式没有 teaching signal → 无监督（不是自监督，因为婴儿没有"生成自己的 error signal"）

---

## Week 2 Quiz 原题（感知发展）

### Q1. 成人/大儿童优先用什么识别物体？
- ✅ **Shape**

### Q2. 婴儿什么时候开始用 gestalt 原则做形状感知？
- ✅ **By 4 months**

### Q3. Match 题
- Object categorization → Infants can successfully accomplish **one-shot categorization**
- Shape perception → **magnocellular pathway develops before parvocellular pathway**
- Viewpoint invariance → **Newborns are sensitive to some depth properties**

### Q4. 填空：低视敏度帮助学习 ___ object features（两词，用 categorical 或 general）
- ✅ **general categorical** 或 **categorical object features**（接受 categorical/general 其一）

### Q5. 听觉感知什么时候开始？
- ✅ **In the womb（子宫内）**

### Q6. 视觉和听觉发展的一个共同点？
- ✅ **Both undergo a process of perceptual tuning**

### Q7. 双语婴儿的 perceptual tuning 与单语婴儿有何不同？
- ✅ **Bilingual infants retain the ability to discriminate non-native sounds and visual speech cues longer than monolingual infants**

### Q8. 感知偏差（perceptual biases）形成于：
- ✅ **Between 6 to 9 months of age**

### Q9. Perceptual narrowing 的定义
- ✅ **A decline in the ability to discriminate unfamiliar types of stimuli during the first year of life**

### Q10. Scott & Monesson (2009)：哪组是唯一在 9 月龄仍能辨猴脸的？
- ✅ **The individual-level labeling group**

---

## 从这两份 Quiz 能反推的高频考点（Exam 1 必备）

### 作者立场对照表（高度建议记）

| 主题 | Cusack (2024) | Zettersten (2025) |
|------|---------------|-------------------|
| 无助期本质 | 自监督预训练 | 主动、目标导向的学习 |
| 婴儿学习模式 | 统计学习 → 后期再接目标 | 统计学习从一开始就和目标、动作整合 |
| 基础模型类比 | 成立 | 缺少主动性、变异、社会生态、具身 |
| 发展变异 | 弱化（强调普遍机制） | 强化（跨文化、个体差异） |
| **同意点** | 统计学习早期就很重要 | 同上 |
| **分歧点** | 统计学习**先于**行动 | 统计学习**与**行动整合 |

### 学习类型对照表

| 类型 | 有无 teaching signal | 信号来源 | 原型实例 |
|------|------------------|---------|---------|
| Supervised | ✅ 有 | 外部教师标签 | 放射科学生读片后被告知答案 |
| Unsupervised | ❌ 无 | — | 婴儿 Saffran 分词、聚类算法 |
| Self-supervised | ✅ 有 | 从数据自己生成 | LLM 预测下一词、BERT 掩码 |
| Reinforcement | ✅ 有 | 环境奖励 | 哭 → 有人来 → 反馈回路 |

### 感知发展时间线（Exam 必背）

| 月龄 | 里程碑 |
|------|------|
| 子宫内 | 听觉开始 |
| 新生儿 | 视敏度 20/200–20/400；面孔偏好（top-heavy） |
| 2 月 | 双眼深度知觉、颜色扩展到蓝黄 |
| 3–4 月 | 形状习惯化、物体统一性（Kellman & Spelke）、gestalt 原则、**语言开始塑造视觉注意** |
| 4–6 月 | 视点不变性成熟 |
| 6 月 | 全球音素辨别 + 他族面孔辨别；腹侧皮层对形状已敏感；Emberson top-down |
| **6–9 月** | **perceptual biases 形成期** |
| 9 月 | 只剩本族面孔 + 母语音素（perceptual narrowing 完成） |
| 10 月 | 数数（Xu 2007）、物体永恒性确立 |
| 12 月 | 母语音素专化 |

**关键口诀**：**子宫听-出生模糊-6 月全球-9 月专化**

### 方法论

| 范式 | 核心逻辑 | 主要用途 |
|------|--------|---------|
| 习惯化 (Habituation) | 看腻 → 新刺激 → 看久 = 区分 | 区分 A vs B、音素辨别、视点不变 |
| 偏好观看 | 两刺激并列，看哪个久 | 新奇偏好、面孔偏好 |
| 违反预期 (VoE) | 看"不可能"更久 = 理解规则 | 核心知识（物体、数量、因果）|
| fNIRS | 血氧反应，移动容忍高 | Ayzenberg 形状、Emberson 预测 |
| 家长报告 (CDI) / Wordbank | 大规模纵向 | 跨语言词汇发展 |
| 头戴相机 (SEEDLingS / SAYCam) | 婴儿第一视角 | 输入分布研究 |

---

## 对 Exam 1 复习的具体启示

1. **每篇 reading 都可能有"According to X"题** — 重点记：
   - Frank (2023) 数据鸿沟三大原因
   - Cusack (2024) 两阶段、帮助定义、预测
   - Zettersten (2025) 四条反驳
   - Love (2026) 监督/无监督连续谱
   - Adolph (2018) 15 条建议的核心意图
   - Oudeyer (2017) 被动步行机启示
   - Ayzenberg & Behrmann (2024) 形状/骨架、面孔剥夺猴
   - Scott & Monesson (2009) 三组条件
   - Johnson (2024) 窄化时间线

2. **注意"Select all that apply"陷阱** — 反射 (reflex) 不是 goal-directed learning。任何"反射 / 纯统计响应"都不算 goal-directed。

3. **注意填空** — 关键术语拼写要会：self-supervised, perceptual narrowing, developmental cascade, prefrontal inhibitory control

4. **注意匹配题** — 几组可能的匹配：
   - 方法 ↔ 测量
   - 理论家 ↔ 观点
   - 发展阶段 ↔ 能力

---

## 🔗 关联

- [[COGS117_2026_课程大纲]]
- [[Frank_2023_数据鸿沟]]
- [[Cusack_2024_婴儿无助期假说]]
- [[Zettersten_2025_婴儿主动学习]]
- [[Love_2026_监督与无监督学习]]
- [[Scott_2009_面孔知觉偏差起源]]
- [[Ayzenberg_2024_视觉物体识别发展]]
- [[Johnson_2024_婴儿感知]]
- [[Adolph_2018_走路发展15条建议]]
- [[Oudeyer_2017_婴儿发展机器人]]
- [[争论_婴儿被动vs主动学习]]

## 📎 来源

- 用户 Chat 会话提供（2026-04-22 夜），Week 1 / Week 2 原始 quiz 题 + 答案

## 💡 建议

用户以后拿到新的 weekly quiz 或 practice 题，建议放到 `raw/ucsd/Spring 2026/COGS117/weekly_quizzes/` 下（需创建文件夹），保持原题的可追溯性；本文件作为 notes/ 下的风格分析汇总页。
