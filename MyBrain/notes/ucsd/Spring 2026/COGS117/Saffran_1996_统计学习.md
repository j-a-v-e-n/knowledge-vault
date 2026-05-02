---
title: "Statistical Learning by 8-Month-Old Infants"
type: source
tags: [COGS117, 统计学习, 语言习得, 词语切分, transitional-probability]
sources:
  - raw/ucsd/Spring 2026/COGS117/Saffran (1996).pdf
created: 2026-05-01
updated: 2026-05-01
confidence: high
priority: active
---

# Saffran, Aslin & Newport (1996) — 8 月大婴儿的统计学习

> 8 月大婴儿仅听 2 分钟连续合成语音流，就能用音节间的统计规律切出"词"——奠定了 statistical learning 范式。

---

## 这项研究在解决什么问题？

**婴儿听到的语音是连续流，没有空格——那他们是怎么知道"哪里是一个词的边界"的？**

成人英语者读 *prettybaby* 时会在 pretty 和 baby 之间感受到边界，但语谱图里其实**没有任何静音、停顿或重音线索**标出这个边界（不同语言用的边界线索还各不相同——没有跨语言不变的声学切分线索）。在 1996 年之前，主流认为婴儿主要靠**先天**机制（experience-independent）获得语言结构；本研究要回答的是：**experience-dependent 的统计学习能不能扛起语言习得的核心任务之一——词语切分？**

## 核心发现（一句话）

**8 月大婴儿在听 2 分钟无任何声学切分线索的合成连续音流后，能仅凭音节间的 transitional probability（转移概率）区分"词"和"非词/部分词"**。

也就是说，"哪三个音节合起来是一个词"这件事，婴儿能从纯统计共现频率里学出来——而且只用 2 分钟。

---

## 为什么会这样？机制：转移概率即词语骨架

**生活类比**：
> 你听一段陌生外语，注意 *xy* 这个音节对——如果 x 之后几乎总跟 y（高 transitional probability），那 *xy* 多半在一个词内部。如果 x 之后跟啥都有可能（低概率），那 x 和后面那个音节之间多半是**词的边界**。

**形式定义**：

$$\text{P}(Y|X) = \frac{\text{freq}(XY)}{\text{freq}(X)}$$

举例（英语）：

> *PRETTY BABY*
> - PRE → TTY: 80% (高，词内)
> - TTY → BA: 0.02% (低，跨词边界)
> - BA → BY: 80% (高，词内)

转移概率在词内远高于词间——这是**所有自然语言都有的统计规律**（即使没有声学线索）。问题是：婴儿能不能在如此短的时间内追踪它？

---

## 怎么证明的？两个实验、关键设计

### 实验设计：人造迷你语言

实验者设计了一种"无任何线索"的人造语言，把 4 个三音节假词随机串起来读：

> 4 词：**tupiro, golabu, bidaku, padoti**
>
> 合成连续流（180 词，2 分钟）：`bidakupadotigolabubidaku...`

合成语音用单调女声、180 词/分钟，**完全无停顿、无重音、无音高变化**——意味着唯一可用的切分线索就是 transitional probabilities（词内 ≈ 1.0；跨词边界 ≈ 0.33，因为四个词随机接续）。

![[Saffran_1996_Table1_设计.png]]

> 这张图（page 3）一次性给出实验设计的核心：4 个 nonsense words，artificial language stream 没有任何声学线索，唯一信号就是音节间的统计概率。

### Headturn Preference Procedure（头转偏好范式）

家长戴隔音耳机抱婴儿入测试间。婴儿正前方有提示灯，左右两侧各有一个扬声器+灯。婴儿的视线持续多久 = 听对应刺激多久。婴儿对**新颖刺激**听得更久（novelty preference）——所以**听更久 = 婴儿觉得这"和我刚才听的有差别"**。

### Experiment 1：Word vs Nonword

测试条件：让婴儿听过 2 分钟流后，**对比"词"和"非词"**：

- "Words"：来自训练流的 3 个词（如 *tupiro*）
- "Nonwords"：从未在流里出现过的另外 3 个三音节串（音节都来自同一池但顺序与训练流冲突）

| | Words | Nonwords | t 检验 |
|---|---|---|---|
| 平均听时（秒） | 7.97 (SE 0.41) | 8.85 (SE 0.45) | t(23)=2.3, **p<0.04** |

> 婴儿对 Nonwords 听更久——这个 novelty preference 说明婴儿认得 Words 是熟悉的，而 Nonwords 是新的。**仅 2 分钟暴露后，他们已经把训练流"分块"成了具体的三音节单位。**

### Experiment 2：Word vs Part-Word（关键的"统计 vs 频率"区分）

但 Exp 1 里"非词"是从未出现过的——婴儿可能只是**记住了听过的具体音节序列**，没用统计。Exp 2 让任务更难：

- "Words"：训练流里的词（如 *tupiro*）
- **"Part-words"**：跨越**词边界**的三音节串（例如 *daropi*，来自 *bidaku-padoti* 的尾首拼接）

关键陷阱：**part-words 在训练流里也出现过**（连续语音里这种跨边界三元组会自然产生），只是它们的内部 transitional probability 比真词低（1.0 vs 0.33）。

| | Words | Part-words | t 检验 |
|---|---|---|---|
| 平均听时（秒） | 6.77 (SE 0.44) | 7.60 (SE 0.42) | t(23)=2.4, **p<0.03** |

> 婴儿仍然区分得开——而且这次他们 **必须**用 transitional probability（不是单纯的"出现过没"），因为 part-words 也出现过。这就排除了"婴儿只是记忆音节序列"的简单解释。

### 反事实控制（4 选 1）

研究者还在 Exp 2 里换一组婴儿听**镜像版本**的语言（用同一池音节但不同的 4 词组合）。两组婴儿对同一测试串表现出相反的偏好——证明效应来自**训练流的特定统计结构**，而不是任何音节本身的内禀新奇度。

---

## 意味着什么？

### 对语言习得理论的冲击

1. **婴儿确实拥有强力的 experience-dependent 统计学习机制**——而且是 distributional analysis 级别的（不只是简单的关联）
2. **在 1996 之前**，语言习得主流强调"poverty of the stimulus"，认为关键结构必须靠先天 UG。本文挑战了这一立场：**至少词语切分这一基础任务可以纯靠经验**
3. **"experience-dependent vs experience-independent"** 的天平向经验侧倾斜了
4. 论文最后一段留下开放问题："这种统计学习是语言专属机制，还是能广泛用于环境分布分析的通用学习机制？"——后续 30 年文献基本回答：**通用机制**（视觉、动作、音乐、社会都能见到 statistical learning）

### 边界与局限

- **2 分钟仅对 nonsense words 起效**——真实语言里词语习得需要更长时间 + 多种线索协同
- 自然语言婴儿听到的语音流并非如此 minimal（有重音、停顿、儿向语 prosody），statistical learning 在自然环境里**与其他线索协同**而不是单打独斗
- 研究只测了"切出词"这一步——后续要把切出的"词形"映射到"意义"还需要其他机制（参 [[Vong_2024_单童语言习得]] 中的 cross-situational 学习）
- 8 月大已经接触母语 8 个月——能否说"这是先天的统计学习能力"还是"被母语经验调过的学习能力"，本文无法区分

---

## ⚠️ 矛盾与未解决问题

- **本研究自身留的问题**：作者在 Discussion 末段明确写 *"It remains unclear whether the statistical learning we observed is indicative of a mechanism specific to language acquisition or of a general learning mechanism applicable to a broad range of distributional analyses of environmental input"*——这是文献中承认的局限，已记入 [[gaps]]
- **与 Chomsky / nativist 立场的对立**：Chomsky 在 [[Zettersten_2026_Lecture9_语言2]] 中被引用主张"语言不是经验学的"。本论文是直接的反例。这一对立在 [[争论_先天语言vs统计学习]] 详细展开

---

## 🔗 关联

### 同主题来源（在 vault 内）

- [[Zettersten_2026_Lecture9_语言2]] — L9 详细复现了本实验（PRETTY BABY 例子、artificial language demo、headturn 范式）。Zettersten 把本研究作为"统计学习"机制的奠基实例
- [[Zettersten_2026_Lecture8_语言1与如何读论文]] — 本论文是 L8 的两篇阅读论文之一（Group 1）
- [[Vong_2024_单童语言习得]] — 同一框架的现代延伸：Saffran 在切**音节级**词边界，Vong 在切**视觉-语言**对应。两篇都在挑战 nativist 数据假设

### 概念页

- [[统计学习]] — 本论文是奠基；后续 cross-situational learning（Smith & Yu 2008）、CVCL（Vong 2024）都是同一机制族的扩展
- [[词语学习机制]] — Statistical regularities 是其中一支
- [[感知窄化]] — 8 月大婴儿能学这种统计结构，本身是"感知系统已经被母语调过"的证据，跟 Werker 音素窄化时间表吻合
- [[争论_先天语言vs统计学习]] — Saffran 是 empiricist 一方的关键证据

### 跨课程

- [[ECE175B_Lecture1b_贝叶斯网络]] — Transitional probability = bigram language model = 一阶马尔可夫链。Saffran 的"婴儿统计学习"等价于"婴儿在做无监督的二元语言模型估计"
- [[自监督学习与基础模型]] — 本研究的 minimal supervision setup（只给输入流，不给标签）是自监督学习的最简形式
- [[Frank_2023_数据鸿沟]] — Frank 2023 的数据鸿沟问题问"婴儿如何用如此少的数据学语言"。Saffran 1996 给出第一块拼图：**强大的统计学习机制**让数据效率成为可能

---

## 📎 来源

- `raw/ucsd/Spring 2026/COGS117/Saffran (1996).pdf`
- 原始引用：Saffran, J. R., Aslin, R. N., & Newport, E. L. (1996). *Statistical Learning by 8-Month-Old Infants*. Science, 274(5294), 1926–1928.
