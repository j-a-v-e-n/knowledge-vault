---
title: "ECE175B Lecture 4: Generative Adversarial Networks (GAN)"
type: source
tags: [ECE175B, GAN, 生成模型, 对抗训练]
sources: [raw/ucsd/Spring 2026/ECE175B/lecture-4.pdf]
created: 2026-04-14
updated: 2026-04-14
confidence: high
priority: active
---

# ECE175B Lecture 4 — 生成对抗网络（GAN）

> VAE 用变分推断绕开不可解的积分；GAN 走了一条完全不同的路——干脆不算似然函数，而是让两个网络互相博弈来学习生成分布。

---

## 从图灵测试到 GAN

**类比：** 想象一场鉴定比赛——一个鉴定师（Discriminator）要分辨"真画"和"赝品"，一个造假者（Generator）要画出以假乱真的作品。双方你追我赶，最终造假者的水平会越来越高。

![[ECE175B_L4_GAN_intro.png]]
> GAN 的灵感来自图灵测试：人类测试者区分人和机器的对话。GAN 把这个思想应用到图像生成。

**关键角色：**

| 角色 | 数学 | 功能 |
|------|------|------|
| **Generator（生成器）** | G: Z → X | 从噪声生成假图像 |
| **Discriminator（判别器）** | D: X → [0,1] | 判断图像是真(0)还是假(1) |

---

## GAN 的架构

![[ECE175B_L4_GAN_architecture.png]]
> GAN 的训练循环：真实图像和生成图像一起送入判别器，判别器输出真/假判断。

**生成过程（与 VAE 相同）：**

$$\hat{z} \sim \mathcal{N}(\vec{0}, I)$$
$$\hat{x} \sim \mathcal{N}\bigl(x \mid f(\hat{z}),\ \text{diag}(g(\hat{z}))\bigr)$$

生成器的结构和 VAE 的 decoder 完全一样——都是从高斯噪声通过神经网络映射到图像空间。

**训练循环：**

1. 从训练集中随机选一张**真实图像**
2. 生成器从噪声生成一张**假图像**
3. 两张图像分别送入判别器
4. 判别器尝试正确分类（真 vs 假）
5. 生成器尝试让判别器犯错

---

## VAE vs GAN：两条通向生成模型的路

![[ECE175B_L4_GAN_training.png]]
> GAN 的训练目标是一个 minimax 博弈：生成器最小化判别器的准确率，判别器最大化自己的准确率。

| 维度 | VAE | GAN |
|------|-----|-----|
| **训练信号** | ELBO（似然下界） | 对抗博弈（minimax） |
| **需要计算 p(X)?** | 需要（通过 ELBO 近似） | 不需要 |
| **推断能力** | ✓ 有 encoder，能算 q(Z\|X) | ✗ 无直接推断 |
| **生成质量** | 倾向模糊（因为高斯假设） | 倾向锐利（但可能 mode collapse） |
| **训练稳定性** | 较稳定（有明确目标函数） | 不稳定（博弈可能不收敛） |

**核心差异：** VAE 显式地定义和优化概率分布；GAN 隐式地通过对抗训练学习分布，从不写出 p(X) 的表达式。

---

## GAN 的已知问题

- **Mode Collapse（模式坍塌）：** 生成器只学会生成少数几种图像来骗过判别器，丧失多样性
- **训练不稳定：** 生成器和判别器的平衡很脆弱——一方太强会导致另一方无法学习
- **无法评估似然：** 因为不显式建模 p(X)，无法用 log-likelihood 评估模型质量

---

## 🔗 关联

- [[ECE175B_Lecture2_变分自编码器设计]] — VAE：另一种生成模型，共享相同的生成器结构（Z→X 的 decoder）
- [[ECE175B_Lecture3_变分推断与ELBO]] — VAE 的训练方法：ELBO 最大化，与 GAN 的对抗训练形成对比
- [[统一多模态生成架构]] — 现代统一多模态范式（Transfusion / Chameleon）已转向 AR + 扩散，GAN 可作 baseline 对比生成质量与稳定性
- [[ECE175B_概览]] — 课程全局视图

## 📎 来源

- `raw/ucsd/Spring 2026/ECE175B/lecture-4.pdf`（7 slides）
