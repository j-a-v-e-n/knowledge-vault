---
title: "COGS117 Lecture 9 — Language 2 (2026-04-30)"
type: source
tags: [COGS117, Zettersten, Lecture, 语言习得, 统计学习, 词语学习, Chomsky, LLM]
sources:
  - raw/ucsd/Spring 2026/COGS117/9_language.pdf
created: 2026-05-01
updated: 2026-05-01
confidence: high
priority: active
---

# Zettersten Lecture 9 — Language 2（4/30）

> 三个核心问题：(1) 为什么人类语言习得是科学上最难的题之一？(2) 婴儿用哪些工具克服它？(3) LLM 改变了我们对这个问题的回答吗？

---

## 主线（先懂再细）

L9 围绕一个 thought experiment 展开：你是个 1 岁孩子，第一次听到德语句子 *"Guck mal, da läuft ein Hase"*（意思："看哇那有只兔子"）。**为了理解这句话，你必须解决 4 个子问题**：

1. **What are the words?** — 切词边界（Word Boundaries）
2. **What do the words mean?** — 词义指称（Semantics）
3. **What do the words mean when combined?** — 句法（Syntax）
4. **What does the speaker intend to communicate?** — 语用（Pragmatics）

![[Zettersten_L9_四问题Toolkit.png]]

> Zettersten 用 Carroll 笔下的怀表兔做隐喻——孩子面对的语言流是连写大字串 *GUCKMALDALÄUFTEINHASE*，没有空格、没有指南、没有翻译。这张图是整堂讲座的骨架。

L9 主要展开了**前两个问题**（切词 + 词义），后两个留待后续课程。所有讨论的核心 framing 是：**语言习得为什么是 interesting scientific problem？**

---

## 1. 为什么语言习得是个难问题？

### 人类语言独一无二

非人类动物的"通信"系统跟人类语言**不在一个量级**：

![[Zettersten_L9_VervetMonkey.png]]

> Vervet 猴有三种警报叫（豹、鹰、蛇 → 爬树/低头/直立）——这是动物界对"指称"最接近的例子。但仅有几种叫，没有 compositionality（合成性）、abstract symbol use、超越 here-and-now 的能力。

历史上人类尝试教非人类语言——Nim Chimpsky（黑猩猩）、Koko（大猩猩）、Kanzi（倭黑猩猩）、Alex（非洲灰鹦鹉）：

![[Zettersten_L9_Kanzi等灵长.png]]

> Kanzi 能识别词序句子（"put the soap in the water"）、用上百 lexigram 字符通信——但仍**显著区别于人类语言**：缺 compositionality、缺抽象符号能力、**缺主动通信动机**。
>
> "Many interesting (and often tragic) attempts that revealed surprising abilities. However, all attempts have found significant limits..."

### 但 LLM 改变了游戏？

ChatGPT、Gemini、Claude、Perplexity 已经**显然能学语言**——挑战了"只有人类能学语言"的传统命题。

但有一个巨大但书：

![[Zettersten_L9_DataGap_Frank2023.png]]

> 来自 [[Frank_2023_数据鸿沟]]：婴儿用 **10⁶ 量级**词汇输入即可掌握语言；GPT-3、Chinchilla 用 **10¹¹–10¹² 量级**——**数据鸿沟约 10⁵×**。意思：婴儿是**远比 LLM 更 data-efficient** 的学习者。这是讲座反复回到的张力源。

### 经典立场对立：Chomsky vs 经验主义

L9 第 5 张幻灯片直接亮出 Chomsky 立场：

![[Zettersten_L9_Chomsky引用.png]]

> *"To say that language is not innate is to say that there is no difference between my granddaughter, a rock and a rabbit. ... If they believe that there is a difference between my granddaughter, a rabbit, and a rock, then they believe that language is innate."*
> — Noam Chomsky (2000)

Chomsky 的论证：人类必须有先天 language faculty——否则不能解释为何人能学语言而岩石/兔子不能。

但 Pinker (1994) 给了一种更弱版本，"alien from Mars" argument：

![[Zettersten_L9_AlienFromMars.png]]

> "A visiting Martian scientist would conclude that aside from their mutually unintelligible vocabularies, Earthlings speak a single language."
> 火星人会觉得地球语言深层只有一种——但 Zettersten 反问："really? language universals?"

**Evans & Levinson 2009** "myth of language universals" 系统反驳：

![[Zettersten_L9_语言变异_无universals.png]]

| 没有 X 的语言 | 例子 |
|---|---|
| adverbs | （多语） |
| adjectives | Lao |
| noun/verb 区分 | Straits Salish |
| 数词 | Pirahã（"一-二-多"系统）|
| 固定语序 | Jiwarli, Riau Indonesian, Latin |

| 有特殊 X 的语言 | 例子 |
|---|---|
| classifiers | 韩语、汉语、日语 |
| 非 SVO 语序 | VSO ~ 7% |

加上 **whistled languages**（Kuş Dili "鸟村" 土耳其；Silbo 加纳利岛）和 **300+ 手语**：

![[Zettersten_L9_Sign_300+语言.png]]

> 仅美洲就有 American / Argentine / Bolivian / Brazilian / Bribri / Chilean / Colombian / Costa Rican / Cuban / Mexican Sign Language ... 几十种。每个都是**独立完整语言系统**，不是英语转录。
>
> **关键论点**：语言变异如此巨大，"universal grammar"作为单一先天结构 → 难以解释；得允许学习机制做更多工作。

---

## 2. 工具 1：Word Boundaries — 统计学习

回到 4 问题里第一个：**What are the words?**

### 问题：连续语音流没有空格

英文母语者听到 *prettybaby* 时**感觉**有空格，但语谱图里没——边界靠学。Zettersten 用一个简单图解：

![[Zettersten_L9_PrettyBaby统计.png]]

> 词内 PRE→TTY 概率 80%；跨词边界 TTY→BA 仅 0.02%。**transitional probability 在词内 ≫ 词间** —— 这是所有自然语言的统计共性。

### 实验：Saffran, Aslin & Newport (1996)

L9 完整复盘 [[Saffran_1996_统计学习]]：

**人造语言**：4 个三音节 nonsense words（tokibu, gopila, gikoba, tipolu）随机串成连续流，2 分钟，无重音、无停顿、无音高变化。

![[Zettersten_L9_TokibuArtificial.png]]

> 整个流都是这样: `tokibutipolugikobatipolu...`。婴儿能用 transitional probability ($P(Y|X) = \frac{\text{freq}(XY)}{\text{freq}(X)}$) 切出词来吗？

**Headturn Preference Procedure**：

![[Zettersten_L9_HeadturnSetup.png]]

> 婴儿坐家长腿上（家长戴隔音耳机）；提示灯吸引注意 → 转头 → 听对应刺激；测**listening duration**。婴儿对**新颖**听更久。
>
> **关键发现**：训练后听 TOKIBU（词）vs KIBUGO（part-word，跨边界三元组），**婴儿对 part-words 听更久** = 学到了二者的差异。
>
> 这意味着仅 2 分钟暴露后，婴儿已经把流"分块"到了具体的三音节单位——而且不是死记，因为 part-words 也出现过，能区分需要追踪概率。

→ **Statistical Learning** 作为机制被确立。

---

## 3. 工具 2：Semantics — gavagai 问题与三大策略

回到 4 问题第二个：**What do the words mean?**

### gavagai 问题（Quine 1960）

![[Zettersten_L9_Gavagai_Quine.png]]

> 你听到 "HASE"（兔子），眼前是只兔子。HASE 指的是：
> - 整只兔子？
> - 兔子的耳朵？
> - 兔子的颜色？
> - "正在跑动"这个事件？
> - 短毛？
> - 这只**特定**兔子？
>
> 任何单次 word-thing 共现都**严重 underdetermined**——这就是 W. V. Quine 的经典 gavagai 问题：词义映射的**搜索空间在原则上是无穷的**。

### 但孩子词汇成长惊人

> - 6-9 mo: canonical babbling
> - 9-10 mo: word comprehension 出现
> - 11-12 mo: 第一个 produced word
> - **16-18 mo: vocabulary "spurt"** — 词汇爆发
> - 24-28 mo: 用 grammatical morpheme
> - 30-36 mo: productive language（"goed" 这种过度规则化错误）
> - **6 岁 ≈ 14,000 词；大学生 ≈ 50,000 词**

![[Zettersten_L9_TextbookChild时间表.png]]

孩子在 gavagai 困境下还能这么快——因为他们用了**三大策略**：

### 策略 A: Statistical Regularities — Cross-Situational Word Learning

跨情境学习（Smith & Yu 2008）：单次共现 underdetermined，但**多次嘈杂共现的交集**可以聚焦：

![[Zettersten_L9_CrossSituational_Modi.png]]

> Smith & Yu 2008 实验：12-14 月婴儿看 2 个物体 + 听 1 个新词。任一 trial 都歧义（不知道哪个是 modi），但跨多 trial **一致出现**的 word-object 对会被学到。
>
> 测试时给 3 个候选问 "Which one is the modi?" → 紫色恐龙 2/2，其他 1/2。婴儿能用统计聚合切歧义。

![[Zettersten_L9_Vong2024_引用.png]]

→ **Vong 2024 是这个机制的"at scale"现代证据**（详见 [[Vong_2024_单童语言习得]]）：用同一个孩子 61 小时视频 + 通用 contrastive learning，能学 22 个 word-referent 映射 + 零样本泛化。

### 策略 B: Social Cues — 凝视追踪与 referential intent

社交线索：孩子能用**说话者的视线方向**推断指称物（即使从未一起出现过）：

![[Zettersten_L9_Baldwin凝视.png]]

> Baldwin 的 paradigm（19-20 月婴儿）：
> 1. 实验者把两个新颖物（modi 和 toma）藏入两个桶
> 2. 实验者**只看其中一个桶**说 "It's a modi!"
> 3. 婴儿尽管**从未同时看到 modi 和那个物体**，仍把 *modi* 映射到实验者**目光所指的桶里**的物体
>
> → infants use **social-pragmatic cues** to learn word meanings. 还有 Tomasello 的工作：婴儿用的社交信息**远比凝视更细微**（意图推断、共注意 joint attention）。

### 策略 C: Cognitive Biases — Shape Bias 与 Mutual Exclusivity

**Shape Bias**（形状偏好）— 听到新名词时优先按**形状**泛化（不是颜色或材质）：

![[Zettersten_L9_ShapeBias.png]]

> "This is a dax" → "Show me the dax" → 孩子选**形状匹配**那个，而不是 color- 或 texture-匹配。
>
> **跨语言强度差异**：英语母语孩 shape bias 强；汉语、日语等 classifier 语言孩子的 shape bias 较弱（语言经验调节先天倾向）。

**Mutual Exclusivity**（互斥性）— 一个物体一个名（反对同义词）：

![[Zettersten_L9_MutualExclusivity.png]]

> "Where's the fengle?" → 孩子看到香蕉（已知）+ 打蛋器（不知）→ **18 月婴儿选打蛋器**。
>
> 隐含假设：每个物体只有一个名 → 已知物体不会有新名 → 新名必指未知物。Markman & Wachtel (1988) 提出。Bilingual / Trilingual 孩子的 mutual exclusivity 较弱（经验调节）。

---

## 4. 关键 takeaways

1. **语言习得是 inherently underdetermined 问题** — gavagai、词边界、句法都没有"教师信号"
2. **婴儿组合多种策略克服它**：
   - Statistical regularities（统计共现 + 跨情境）
   - Social cues（视线、意图、共注意）
   - Cognitive biases（shape bias、mutual exclusivity）
3. **三种策略都对经验敏感**——bias 强度因语言/文化变化（不是 hard-wired 不变量）
4. **LLM 能学语言但需要 10⁵× 更多数据**——指出我们对人脑学习算法还知之甚少

---

## ⚠️ 矛盾与未解决问题

讲座本身呈现了多组对立（已有文献中存在的）：
- **Chomsky innate vs Saffran/Vong empiricist** — 详见 [[争论_先天语言vs统计学习]]
- **"Language universals" (Pinker 1994) vs "Myth of universals" (Evans & Levinson 2009)** — 讲座引用双方但未做裁决
- **三大策略的相对权重**：统计 / 社交 / 偏好哪个最重要？讲座未给出，留为开放
- **Shape bias 是先天还是学习的**：跨语言变异说明它**至少部分**是经验形成——但是否完全经验形成？讲座没断言
- **Bilingual 弱化 mutual exclusivity 的临界值**：1 岁、2 岁、3 岁前接触第二语言效果一样吗？讲座未展开

---

## 🔗 关联

### 同期讲座
- [[Zettersten_2026_Lecture8_语言1与如何读论文]] — 上一讲，技能训练 + 引入两篇阅读
- [[COGS117_概览]] — 课程整体框架

### 本讲深度引用的两篇阅读
- [[Saffran_1996_统计学习]] — Word boundaries 部分的实验来源
- [[Vong_2024_单童语言习得]] — Statistical regularities 部分的现代证据

### 概念页
- [[统计学习]] — 本讲座是这个概念的最系统讲解
- [[词语学习机制]] — 三大策略的来源讲座
- [[争论_先天语言vs统计学习]] — Chomsky vs empiricist 的展开
- [[感知窄化]] — Werker 音素窄化与本讲的统计学习同根
- [[发展研究方法]] — Headturn preference procedure 是本讲讨论的关键方法

### 跨课程交叉
- [[Frank_2023_数据鸿沟]] — Lecture 9 直接引用 Frank 2023 数据鸿沟图
- [[ECE175B_Lecture1b_贝叶斯网络]] — Transitional probability 是 bigram language model
- [[统一多模态生成架构]] — Vong 2024 的 CVCL 架构跟 ECE175B 的 contrastive vision-language paradigm 同根
- [[自监督学习与基础模型]] — 本讲的核心机制（统计学习）就是自监督学习的认知科学版本

### 引用但未独立建页的来源
- Smith & Yu (2008) Cross-situational word learning — 跨情境学习奠基
- Baldwin — Early Referential Understanding（gaze following paradigm）
- Tomasello — Social cues for word learning（更细微的社交信息）
- Markman & Wachtel (1988) — Mutual exclusivity
- Byers-Heinlein & Werker (2009) — Bilingual mutual exclusivity 较弱
- Quine (1960) *Word and Object* — gavagai 问题源头
- Pinker (1994) *The Language Instinct* — alien from Mars argument
- Evans & Levinson (2009) — myth of language universals
- Seyfarth et al. (1980) — Vervet alarm calls

---

## 📎 来源

- `raw/ucsd/Spring 2026/COGS117/9_language.pdf`
- 课堂日期：2026-04-30
- 讲师：Martin Zettersten（UCSD COGS 117）
- 配套 notebook：Notebook 1 GPT Basics（5/7 截止）
