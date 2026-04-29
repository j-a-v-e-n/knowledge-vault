---
title: "ECE175B Lecture 2: Variational Autoencoder — Model Design"
type: source
tags: [ECE175B, VAE, Bayesian Network, 生成模型, 图像生成]
sources: [raw/ucsd/Spring 2026/ECE175B/lecture-2.pdf]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B Lecture 2 — 变分自编码器（VAE）：模型设计

> VAE 的核心思想：图像是由"语义"生成的——先有"天空、建筑、猫"的概念（隐变量 Z），再映射到像素（观测变量 X）。用 Bayesian Network Z→X 建模这个过程。

---

## 问题：如何生成逼真的图像？

假设你想让机器"画"一张图片。直觉上，画画需要先有一个想法（"画一只猫在草地上"），然后把想法变成像素。VAE 把这个直觉数学化：

- **Z（隐变量/语义）：** 抽象的"想法"——天空占多大面积、有没有猫、建筑在哪里
- **X（观测变量/图像）：** 具体的像素矩阵

![[ECE175B_L2_VAE_graph.png]]
> VAE 的图结构极其简单：只有两个节点 Z→X。Z 是隐含的语义概念，X 是我们能看到的图像。

---

## 步骤一：设计图结构（Graph）

| 元素 | 对应 |
|------|------|
| Objects | 图像 X（像素矩阵）+ 语义 Z（概念向量） |
| Relations | 语义决定图像：Z → X |
| 图类型 | 有向图 → Bayesian Network |

---

## 步骤二：为节点赋予随机变量

- **Z（语义）：** 连续向量，每个维度可能编码一个属性（"天空程度""猫的存在"等）
  - 分布类型：**Multi-variate Gaussian**（多元高斯分布）
  - 例：Z 的某个维度 = (dog: 1, cat: 2.8, desk: 0.1)

- **X（图像）：** 像素值构成的高维向量
  - 分布类型：**Multi-variate Gaussian**（条件于 Z）

---

## 步骤三：定义局部分布

**先验分布（Prior）：**

$$p(Z) = \mathcal{N}(Z \mid \vec{0}, I)$$

为什么用标准正态？因为**先验不含任何信息**——我们不预设"猫比狗更常见"，让数据自己决定。

**似然分布（Likelihood / Decoder）：**

$$p(X \mid Z) = \mathcal{N}\bigl(X \mid f(Z),\ \text{diag}(g(Z))\bigr)$$

![[ECE175B_L2_VAE_decoder.png]]
> Decoder 网络结构：Z 通过多层神经网络分别输出均值 f(Z) 和方差 g(Z)，定义 X 的条件分布。

其中 f(Z) 和 g(Z) 是**两个神经网络**（共享部分参数）：
- f(Z) 输出图像的均值（"最可能的像素值"）
- g(Z) 输出图像每个像素的方差（"不确定度"）
- diag(g(Z))：对角协方差矩阵——假设像素间条件独立

---

## 步骤四：联合分布

$$p(X, Z) = p(Z) \cdot p(X \mid Z)$$

这就是 Bayesian Network 分解公式在两节点图上的直接应用。

---

## VAE 的三大任务

![[ECE175B_L2_VAE_three_tasks.png]]
> VAE 定义好后，有三件事要做：训练、生成、理解。

| 任务 | 数学表述 | 阶段 |
|------|----------|------|
| ① **参数学习（Training）** | 从数据学到 f、g 的网络参数 ϕ | 构建模型 |
| ② **数据生成（Sampling）** | ẑ ~ N(0, I)，x̂ ~ N(x\|f(ẑ), diag(g(ẑ))) | 使用模型 |
| ③ **数据理解（Inference）** | 给定图像 X，推断其语义 P(Z\|X) | 使用模型 |

**生成过程（采样）：**
1. 从标准正态中随机抽一个语义向量 ẑ
2. 通过 decoder 网络计算 f(ẑ) 和 g(ẑ)
3. 从 N(x|f(ẑ), diag(g(ẑ))) 中采样得到图像 x̂

**推断问题：** 给定图像 X，其"语义"是什么？即计算 P(Z|X) = p(Z,X)/p(X)。但 p(X) = ∫p(Z,X)dZ 是一个高维积分，**NP-hard**——这正是下一讲（变分推断）要解决的问题。

---

## 🔗 关联

- [[ECE175B_Lecture1a_课程导论与DGM概述]] — PGM/BN 基础理论
- [[ECE175B_Lecture1b_贝叶斯网络]] — BN 分解公式、DAG
- [[ECE175B_Lecture3_变分推断与ELBO]] — 续：如何训练 VAE（解决任务 ① 和 ③）
- [[ECE175B_概览]] — 课程全局视图

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-2.pdf`（9 slides）
