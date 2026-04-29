---
title: "ECE175B Lecture 3: Variational Inference & ELBO"
type: source
tags: [ECE175B, VAE, 变分推断, ELBO, KL散度, MLE, EM算法]
sources: [raw/ucsd/Spring 2026/ECE175B/lecture-3.pdf]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B Lecture 3 — 变分推断与 ELBO

> VAE 的训练核心：直接最大化数据似然 log p(X) 行不通（涉及不可解的积分），但我们可以最大化它的下界——Evidence Lower Bound (ELBO)。这个"退而求其次"的策略是整个 VAE 的数学支柱。

---

## 问题回顾：为什么需要变分推断？

上一讲建好了 VAE 模型（Z→X），但训练和推断都卡在同一个瓶颈：

$$p(Z \mid X) = \frac{p(Z, X)}{p(X)}, \quad p(X) = \int_Z p(Z, X) \, dZ$$

这个积分在高维空间中是 **NP-hard**——Z 有几百维，无法暴力积分。

![[ECE175B_L3_inference_problem.png]]
> 推断问题的核心困难：分母 p(X) 涉及对所有可能的 Z 求积分，计算量爆炸。

---

## 变分推断：用"近似"绕开不可解的精确解

**核心思想：** 既然 p(Z|X) 算不出来，就找一个"好算的"分布 q(Z|X) 来近似它。

$$q_\theta(Z \mid X) = \mathcal{N}\bigl(Z \mid \tilde{a}(X),\ \tilde{b}(X)\bigr)$$

其中 ã(X) 和 b̃(X) 是**编码器（Encoder）网络**——输入图像 X，输出近似后验的均值和方差。

**目标：** 让 q(Z|X) 尽量接近真实后验 p(Z|X)。怎么度量"接近"？

---

## KL 散度：度量两个分布的差距

![[ECE175B_L3_KL_divergence.png]]
> q(Z|X)（蓝色多峰曲线）试图逼近 p(Z|X)（红色光滑曲线）。KL 散度衡量两者之间的差异。

$$\text{KL}\bigl(q(Z|X) \,\|\, p(Z|X)\bigr) = \mathbb{E}_{q(Z|X)}\left[\log \frac{q(Z|X)}{p(Z|X)}\right] \geq 0$$

**性质：** KL ≥ 0，等号当且仅当 q = p。所以目标变成：

$$\min_\theta \; \text{KL}\bigl(q_\theta(Z|X) \,\|\, p(Z|X)\bigr)$$

**展开 KL：**

$$\text{KL} = \mathbb{E}_{q}\bigl[\log q(Z|X)\bigr] - \mathbb{E}_{q}\bigl[\log p(Z|X)\bigr]$$

$$= \mathbb{E}_{q}\bigl[\log q(Z|X)\bigr] - \mathbb{E}_{q}\bigl[\log p(Z,X)\bigr] + \log p(X)$$

注意最后一项 log p(X) 不依赖 θ，优化时可以忽略。

---

## 参数学习：MLE 遇到的麻烦

训练 VAE 的 decoder 参数 ϕ 用的是最大似然估计（Maximum Likelihood Estimation）：

$$\max_\phi \sum_{i=1}^{N} \log p_\phi(X_i)$$

但每一项都涉及不可解的积分：

$$\log p_\phi(X) = \log \int_Z p_\phi(X, Z) \, dZ$$

---

## ELBO：一个可计算的下界

**关键技巧：** 在积分中引入 q_θ(Z|X)，然后用 **Jensen's Inequality**（对凹函数 f，f(E[X]) ≥ E[f(X)]）推导出下界。

![[ECE175B_L3_ELBO.png]]
> ELBO 推导的核心步骤：引入 q 分布 → 交换积分与对数 → Jensen 不等式 → 得到可计算的下界。

**推导过程：**

$$\log p_\phi(X) = \log \int_Z p_\phi(X, Z) \, dZ = \log \int_Z \frac{p_\phi(X, Z)}{q_\theta(Z|X)} \cdot q_\theta(Z|X) \, dZ$$

$$= \log \, \mathbb{E}_{q_\theta(Z|X)}\left[\frac{p_\phi(X, Z)}{q_\theta(Z|X)}\right]$$

由 Jensen 不等式（log 是凹函数）：

$$\geq \mathbb{E}_{q_\theta(Z|X)}\left[\log \frac{p_\phi(X, Z)}{q_\theta(Z|X)}\right]$$

$$= \underbrace{\mathbb{E}_{q_\theta(Z|X)}\bigl[\log p_\phi(X, Z)\bigr]}_{\text{重建 + 先验匹配}} - \underbrace{\mathbb{E}_{q_\theta(Z|X)}\bigl[\log q_\theta(Z|X)\bigr]}_{\text{编码器熵}} = \textbf{ELBO}$$

**ELBO 的含义：**
- 第一项：在 q 采样的 Z 下，联合分布的期望对数似然——鼓励 decoder 重建出好图像
- 第二项：编码器分布的负熵——鼓励 q 不要太集中（保持多样性）

---

## 训练算法：EM 坐标上升

![[ECE175B_L3_EM_algorithm.png]]
> EM 算法交替优化两组参数：先固定 decoder 优化 encoder（E-step），再固定 encoder 优化 decoder（M-step）。

最终训练目标：

$$\max_{\phi, \theta} \sum_{i=1}^{N} \left[ \mathbb{E}_{q_\theta(Z_i|X_i)}\bigl[\log p_\phi(X_i, Z_i)\bigr] - \mathbb{E}_{q_\theta(Z_i|X_i)}\bigl[\log q_\theta(Z_i|X_i)\bigr] \right]$$

其中 ϕ 是 **模型参数**（decoder），θ 是 **辅助参数**（encoder）。

**Expectation-Maximization（EM）算法：**

```
While not converged:
  ① E-step: 固定 ϕ，优化 θ（让 encoder 更好地近似后验）
  ② M-step: 固定 θ，优化 ϕ（让 decoder 更好地重建数据）
```

这是一种**坐标上升（Coordinate Ascent）**策略——每一步都保证 ELBO 不减小，最终收敛到局部最优。

---

## 技术细节

### Jensen's Inequality

若 f 是凹函数（如 log），则：

$$f\bigl(\mathbb{E}[X]\bigr) \geq \mathbb{E}\bigl[f(X)\bigr]$$

几何含义：凹函数的"弦"在曲线下方。应用于 log：log(期望) ≥ 期望(log)。

### ELBO 与 KL 的关系

$$\log p(X) = \text{ELBO} + \text{KL}(q \| p)$$

因为 KL ≥ 0，所以 ELBO ≤ log p(X)——ELBO 确实是 evidence（边际似然）的下界。最大化 ELBO 同时在**提高数据似然**和**让 q 逼近真实后验**。

---

## 🔗 关联

- [[ECE175B_Lecture2_变分自编码器设计]] — 前置：VAE 模型结构（Z→X、decoder 设计）
- [[ECE175B_Lecture4_生成对抗网络]] — 另一种绕开似然函数的生成模型训练策略
- [[统一多模态生成架构]] — 应用：扩散模型的 DDPM 训练目标可从 ELBO 推出，是 Transfusion 图像侧的理论基础
- [[ECE175B_概览]] — 课程全局视图

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-3.pdf`（7 slides）
