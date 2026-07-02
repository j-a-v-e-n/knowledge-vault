---
title: "ECE175B: Deep Generative Models — 课程概览"
type: overview
tags: [ECE175B, 深度生成模型, UCSD]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B: Deep Generative Models — 课程概览

> 深度生成模型 = 概率图模型 + 深度学习。这门课从概率论和图论出发，构建起能生成文本、图像、视频的数学框架。

---

## 课程信息

| 项目 | 内容 |
|------|------|
| **课程** | ECE175B: Deep Generative Models |
| **教授** | Pengtao Xie, UCSD ECE |
| **学期** | Spring 2026 |
| **评分** | HW × 3（各 10%）+ Project 70%（Proposal 10% + Midterm 20% + Final 40%） |
| **迟交** | 0–24h = 75%，24–48h = 50%，>48h = 0；共 5 grace days |
| **前置知识** | Probability distributions, Linear algebra, Optimization, Machine learning, Kernels |

---

## 课程知识地图

```
概率论 + 图论
    ↓
概率图模型 (PGM)
    ├── Bayesian Network (有向图, 因果)
    └── Markov Random Fields (无向图, 相关)
    ↓  + 深度学习
深度生成模型 (DGM)
    ├── VAE (变分自编码器) ← ELBO + 变分推断
    ├── GAN (生成对抗网络) ← 对抗训练
    ├── Diffusion Models (扩散模型) ← 待讲
    └── Autoregressive Models (自回归) ← LLM 就是这个
```

**核心思路：** DGM 的四大任务是 ① 设计模型（表示问题）→ ② 参数学习（学习问题）→ ③ 数据生成（采样问题）→ ④ 数据理解（推断问题）。前两步是"建模型"，后两步是"用模型"。

---

## 讲座进度与笔记

| 讲座 | 主题 | 核心内容 | 笔记链接 |
|------|------|----------|----------|
| Lecture 1a | 课程导论与 DGM 概述 | DGM 定义、判别 vs 生成模型、PGM 基础、BN 分解公式 | [[ECE175B_Lecture1a_课程导论与DGM概述]] |
| Lecture 1b | 贝叶斯网络 | DAG 分解实例、I-map、LLM 是链式 BN、Transformer 参数化 | [[ECE175B_Lecture1b_贝叶斯网络]] |
| Lecture 2 | VAE 模型设计 | Z→X 图、先验 N(0,I)、decoder 网络、三大任务 | [[ECE175B_Lecture2_变分自编码器设计]] |
| Lecture 3 | 变分推断与 ELBO | KL 散度、MLE 困难、Jensen 不等式、ELBO 推导、EM 算法 | [[ECE175B_Lecture3_变分推断与ELBO]] |
| Lecture 4 | GAN | 对抗训练、Generator vs Discriminator、VAE vs GAN 对比 | [[ECE175B_Lecture4_生成对抗网络]] |

---

## 核心概念索引

| 概念 | 首次出现 | 简述 |
|------|----------|------|
| **Generative Model** | L1a | 建模 P(X) 或 P(X,Y)，能生成新数据 |
| **Bayesian Network** | L1a/L1b | 有向图编码因果关系，联合分布 = ∏p(xₖ\|pa(xₖ)) |
| **DAG** | L1b | Directed Acyclic Graph，BN 的图结构 |
| **I-map** | L1b | 图的独立性是真实分布独立性的子集 |
| **VAE** | L2 | 编码器-解码器架构，用变分推断训练 |
| **Latent Variable (Z)** | L2 | 隐含的语义表示，不可直接观测 |
| **ELBO** | L3 | Evidence Lower Bound，VAE 的可计算训练目标 |
| **KL Divergence** | L3 | 度量两个分布差距，KL(q‖p) ≥ 0 |
| **Variational Inference** | L3 | 用参数化分布 q 近似不可解的后验 p(Z\|X) |
| **Jensen's Inequality** | L3 | 凹函数 f(E[X]) ≥ E[f(X)]，ELBO 推导的关键 |
| **EM Algorithm** | L3 | E-step（优化 encoder）+ M-step（优化 decoder）交替 |
| **MLE** | L3 | Maximum Likelihood Estimation，参数学习的标准方法 |
| **GAN** | L4 | Generator vs Discriminator 对抗博弈 |

---

## 🔗 关联

- [[Zettersten_2026_计算模型与框架]] — COGS117 中也涉及贝叶斯推断，但侧重认知科学建模
- [[自监督学习与基础模型]] — 自监督学习与生成式预训练的联系
- [[统一多模态生成架构]] — DGM 三大范式（AR / VAE / GAN / Diffusion）在多模态生成中的实际整合（HW1 设计参考）
- [[2026-04-20_多模态故事生成研究]] — HW1 调研笔记：Transfusion / Chameleon / DiffuStory / Infinite-Story 的对比

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-1a.pdf`
- `raw/ucsd/Spring 2026/ECE175B/lecture-1b.pdf`
- `raw/ucsd/Spring 2026/ECE175B/lecture-2.pdf`
- `raw/ucsd/Spring 2026/ECE175B/lecture-3.pdf`
- `raw/ucsd/Spring 2026/ECE175B/lecture-4.pdf`
