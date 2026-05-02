---
title: "ECE175B Lecture 1b: Bayesian Networks in Depth"
type: source
tags: [ECE175B, Bayesian Network, DAG, LLM, Transformer]
sources: [raw/ucsd/Spring 2026/ECE175B/lecture-1b.pdf]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B Lecture 1b — 贝叶斯网络

> 贝叶斯网络通过有向无环图（DAG）把高维联合分布拆成局部条件分布的乘积——这正是大语言模型"逐词预测"的数学本质。

---

## DAG 分解：一个具体例子

把七个随机变量排成一个 DAG（Directed Acyclic Graph，有向无环图），每个节点只依赖它的父节点：

![[ECE175B_L1b_DAG_example.png]]
> 七节点 DAG 示例：通过图结构可以把 7 维联合分布从 2⁷ = 128 个参数压缩到一系列条件分布的乘积。

**分解过程：**

给定图 X₁ → X₄ ← X₂, X₁ → X₅ ← X₃, X₃ → X₄, X₄ → X₆, X₄ → X₇ ← X₅：

$$P(X_{1:7}) = p(X_1) \cdot p(X_2) \cdot p(X_3) \cdot p(X_4|X_1,X_2,X_3) \cdot p(X_5|X_1,X_3) \cdot p(X_6|X_4) \cdot p(X_7|X_4,X_5)$$

**I-map 性质：** 图结构中的条件独立关系是真实分布的条件独立关系的**子集**——图编码的独立性一定成立，但真实分布可能有更多独立性。

---

## LLM 就是一个贝叶斯网络

这是本讲最关键的洞见：大语言模型的数学本质是一个链式 Bayesian Network。

![[ECE175B_L1b_LLM_as_BN.png]]
> 句子中的每个词都是一个随机变量节点，形成一条链式 DAG：W₁ → W₂ → W₃ → ... → Wₙ。

**建模过程：**

1. **抽象为图：** 句子中的词 W₁, W₂, ..., Wₙ 是对象（objects），词序是关系（relations）
2. **随机变量类型：** 每个 Wₖ 是 **Categorical variable**（从词汇表 V 中选一个词，V ≈ 10,000–100,000）
3. **分解联合分布：**

$$P(W_{1:N}) = p(W_1) \cdot \prod_{k=2}^{N} P(W_k \mid W_{1:k-1})$$

4. **神经网络参数化：** P(Wₖ|W₁:ₖ₋₁) 用 **Transformer** 计算——输入前 k-1 个词，输出一个 V 维向量，经过 softmax 得到每个词的概率

**举例：** "I like apple because it is ___"

| 候选词 | 概率 | 合理？ |
|--------|------|--------|
| delicious | 高 | ✓ |
| handsome | 极低 | ✗ |
| smelly | 极低 | ✗ |

Transformer 学到的条件分布会给 "delicious" 高概率，因为训练数据中 "apple ... delicious" 共现频率高。

---

## 从 BN 到深度生成模型

Bayesian Network 告诉我们**如何分解分布**（图结构），但局部条件分布 P(Xₖ|pa(Xₖ)) 的具体形式需要选择：

- 简单情况：表格（小离散变量）、高斯分布
- 复杂情况：**用神经网络参数化** → 这就是"深度"生成模型

LLM 正是后者的典范：Transformer 网络参数化了 P(Wₖ|W₁:ₖ₋₁)。

---

## 🔗 关联

- [[ECE175B_Lecture1a_课程导论与DGM概述]] — 前置：PGM 基础、BN 分解公式
- [[ECE175B_Lecture2_变分自编码器设计]] — 将 BN 应用于图像生成：Z→X 两节点图
- [[统一多模态生成架构]] — 应用：全自回归路线（Chameleon）让"LLM 是链式 BN"自然延伸到图文混合序列；混合路线（Transfusion）保留文本侧的 AR 分解
- [[ECE175B_概览]] — 课程全局视图

### 跨课程：婴儿统计学习是简化版 BN
- [[Saffran_1996_统计学习]] — Transitional probability $P(Y|X) = \frac{\text{freq}(XY)}{\text{freq}(X)}$ = bigram language model = **一阶马尔可夫链**。Saffran 1996 证明 8 月婴儿能在 2 分钟内做无监督的二元 BN 参数估计——这跟 LLM next-token prediction 用的是同一个数学结构，只是 context window=1
- [[统计学习]] — 婴儿的统计学习是**最简单的链式 BN 估计**
- [[Vong_2024_单童语言习得]] — CVCL contrastive learning 把 BN 推到多模态：视觉、语言两个变量的联合概率分布建模（虽然没有显式 graphical model，但 contrastive loss 等价于一种 noise contrastive estimation）

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-1b.pdf`（8 slides）
