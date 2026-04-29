---
title: "ECE175B Lecture 1a: Course Introduction & Deep Generative Models Overview"
type: source
tags: [ECE175B, 深度生成模型, 概率图模型, Bayesian Network]
sources: [raw/ucsd/Spring 2026/ECE175B/lecture-1a.pdf]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B Lecture 1a — 课程导论与深度生成模型概述

> 深度生成模型 = 概率图模型 + 深度学习：用神经网络参数化概率分布，从而能生成文本、图像、视频等各种数据。

---

## 这门课在解决什么问题？

想象一台能「画画」「写诗」「编代码」的机器——它本质上在做一件事：**从一个概率分布中采样**。Deep Generative Models（DGM，深度生成模型）就是学习如何定义和采样这些分布的理论框架。

![[ECE175B_L1a_DGM_overview.png]]
> 这张 slide 总结了课程的核心公式：DGM 本质上是用"概率分布 + 深度学习"来生成数据。

**课程定位：** DGM 是概率理论（probability theory）、图论（graph theory）和深度学习（deep learning）三者的交叉。先学前两者合成的概率图模型（PGM），再加上神经网络得到 DGM。

---

## 判别模型 vs 生成模型

理解 DGM 之前需要先区分两种建模范式：

![[ECE175B_L1a_disc_vs_gen.png]]
> 判别模型学"边界"（哪边是猫哪边是狗），生成模型学"全貌"（猫长什么样、狗长什么样）。

|          | Discriminative Model           | Generative Model        |
| -------- | ------------------------------ | ----------------------- |
| **建模对象** | P(Y\|X) — 给定输入预测标签             | P(X) 或 P(X,Y) — 数据本身的分布 |
| **能力**   | 分类、回归                          | 分类 + **生成新数据**          |
| **关系**   | 知道 P(X,Y) 就能用 Bayes 得到 P(Y\|X) | 生成模型 ⊃ 判别模型（能力更广）       |

**条件生成模型 P(X\|Y)：** 给定条件生成数据，例如 P(图像\|文字描述) 就是 Stable Diffusion 在做的事；P(翻译\|原文) 就是机器翻译。

---

## 深度生成模型的三大核心问题

![[ECE175B_L1a_key_problems.png]]
> DGM 的三大任务：怎么表示分布、怎么从数据学习、怎么做推断。

1. **Representation（表示）：** 如何定义 p(x)？直接写出所有变量的联合分布？维度灾难——10 个二值变量就需要 2¹⁰ = 1024 个参数。
2. **Learning（学习）：** 给定数据，如何学到分布的参数？→ Maximum Likelihood Estimation（MLE）
3. **Inference（推断）：** 已知 p(x) 后，如何计算后验 p(z\|x)？→ 通常是 NP-hard，需要近似

---

## 概率图模型：解决 Representation 问题

**核心思想：** 与其直接定义高维联合分布（指数级参数），不如用图来编码变量间的条件独立关系，将联合分布分解为局部条件分布的乘积。

![[ECE175B_L1a_PGM_overview.png]]
> 概率图模型用图结构表达随机变量之间的关系：节点 = 随机变量，边 = 依赖关系。

**构建 PGM 的步骤：**

1. **抽象为图：** Objects → Nodes，Relations → Edges
2. **为节点赋予随机变量：** 每个节点对应一个概率分布（Gaussian、Bernoulli、Categorical 等）
3. **定义局部条件分布：** 每个节点的分布只依赖其父节点
4. **乘积得到联合分布**

**两种图模型：**

| 类型 | 边 | 含义 | 名称 |
|------|------|------|------|
| Directed | A → B | 因果关系（causality） | Bayesian Network |
| Undirected | A — B | 相关关系（correlation） | Markov Random Fields |

---

## Bayesian Network：有向图的联合分布分解

![[ECE175B_L1a_BN_factorization.png]]
> Bayesian Network 的核心公式：联合分布 = 每个节点的条件分布之积。

**分解公式：** 给定有向无环图（DAG），联合分布可以写为：

$$p(x_1, x_2, \ldots, x_K) = \prod_{k=1}^{K} p(x_k \mid \text{pa}(x_k))$$

其中 pa(xₖ) 是节点 xₖ 的所有父节点。这将指数级参数降低到**多项式级**。

**教材参考：** Koller & Friedman, *Probabilistic Graphical Models* — 课程主要理论基础。

---

## 课程后勤

| 项目 | 内容 |
|------|------|
| **课程名** | ECE175B: Deep Generative Models |
| **教授** | Pengtao Xie, UCSD ECE |
| **评分** | HW × 3（各 10%）+ Project（70%：Proposal 10% + Midterm 20% + Final 40%） |
| **迟交** | 0–24h = 75%，24–48h = 50%，>48h = 0；共 5 grace days |
| **前置知识** | Probability distributions, Linear algebra, Optimization, Machine learning, Kernels |

---

## 🔗 关联

- [[ECE175B_Lecture1b_贝叶斯网络]] — 续讲 BN：DAG 分解实例、LLM 作为 BN 的例子
- [[ECE175B_Lecture2_变分自编码器设计]] — 将 BN 应用于图像生成 → VAE
- [[ECE175B_概览]] — 课程全局视图

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-1a.pdf`（40 slides）
