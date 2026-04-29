---
title: "Toward Foundation Model for Multivariate Wearable Sensing of Physiological Signals"
type: source
tags: [ECE284, 可穿戴设备, 基础模型, 自监督学习, PPG, ECG, EEG, GSR, 数字健康, 时序建模]
sources: [raw/ucsd/Spring 2026/ECE284/3803808.pdf]
created: 2026-04-20
updated: 2026-04-20
confidence: high
priority: active
---

# Luo et al. (2026) — NormWear：可穿戴生理信号的多变量基础模型

> **一个不挑通道的 transformer**——给它 PPG / ECG / EEG / GSR / IMU 任意组合，它在 18 个下游健康任务上几乎都打过专为单一模态训练的"专家"模型，并且能做 zero-shot 推断。

---

## 这项研究在解决什么问题

可穿戴设备一天 24 小时记录心率、脑电、皮肤电、运动等多路生理信号，但**每家厂商的传感器配置都不一样**——Apple Watch 给你 PPG + 加速度，Oura Ring 给你温度 + PPG，临床贴片给你多导 EEG。已有的"基础模型"路线有两个问题：

1. **专家模型路线**（PaPaGei 给 PPG、ECG-FM 给 ECG、CBraMod 给 EEG）：每种信号都要训一个模型，新设备来了就得从头再来。
2. **通用时序模型路线**（Chronos、TF-C、CLAP）：能吃任意单变量序列，但**忽略了通道之间的关系**——心率的波动和运动加速度有没有同步、皮肤电跟脑电一不一致，这些跨传感器信息全丢了。

NormWear 的目标是同时解决这两个问题：**一个模型、任意通道数与组合、自动捕捉跨传感器关联**。

---

## 核心机制：用一个"联络员 token"跨通道交流

为什么要专门搞一个跨通道机制？把所有通道拼成一长串塞进 self-attention 里复杂度是 O(d·(L·C)²)——L 是 patch 数、C 是通道数，几十个传感器拼起来内存炸。但**完全独立处理每个通道**又拿不到跨传感器关系。

NormWear 的折中：每个通道独立走 transformer，但每个通道都有一个 [CLS] token，每隔一层把所有通道的 [CLS] 收上来开个"小会"做 self-attention，然后把更新后的 [CLS] 发回各自通道继续传递信息。这就是**Channel-Aware Attention with Liaison Special Token**。

类比：**联合国大会**。每个国家（通道）内部各自开会（intra-channel encoder），但每过一段时间各国大使（[CLS] token）聚到一起开会交流（inter-channel encoder），回去后把大会信息传达给本国其他人。

![[Luo_2026_NormWear_page02_Fig1_framework.png]]

> 图 1 — 整体框架。模块 A：异构数据流（不同设备、不同场景的信号）。模块 B：NormWear 主干由"层内编码器 + 跨通道融合块"交替堆叠组成；B.2 通过 signal-text 表征对齐实现 zero-shot。模块 C：覆盖心理健康、活动识别、生命体征估计、疾病风险评估四大类应用。**这张图说明：NormWear 不是为单一模态设计的，而是设计成一个"传感器无关的"推理引擎。**

---

## 输入怎么编码：CWT + 一阶/二阶导数 → "RGB 频谱图"

文本 token 化已成共识，时间序列没有。NormWear 把信号当成图像处理：

1. **算原始信号的一阶、二阶导数**——捕捉变化率
2. **对三个序列分别做连续小波变换（CWT）**，用 Mexican Hat 母小波，scale 1–64
3. **三张 scalogram 叠成 RGB 形式**，再切 patch 喂 ViT

为什么不用更熟悉的 STFT？因为 STFT 必须固定窗口大小，PPG 是 25Hz 而 EEG 可能是 250Hz——固定窗就只能对一种模态优化。CWT 自适应多尺度，跨模态都行。消融研究证明 CWT + 导数确实是最好的初始嵌入：

| 输入策略 | 综合得分 |
|----------|---------|
| 原始时间序列 | 80.85 |
| STFT | 76.40 |
| CWT | 80.34 |
| **CWT + 导数** | **82.83** |

![[Luo_2026_NormWear_page03_Fig2_pretraining.png]]

> 图 2 — 预训练框架细节。左侧是主干（CWT 编码 → 12 层 Transformer + lightweight decoder）。右上对比四种 masking 策略，"temporal + scale 联合"最优。右下对比四种跨通道融合方式，[CLS]-Attention 既最优又最便宜（O(d·C²)，与 patch 数 L 无关，因为 L>>C）。

---

## Zero-shot 怎么做：信号 ↔ 文本对齐

光有强大的表征还不够——基础模型的标志是"没见过的任务也能做"。NormWear 借鉴 CLIP 的思路，让信号嵌入和文本嵌入落在同一个语义空间里。但有个独特挑战：**健康任务的标签经常重叠**（"压力"和"抑郁"语义高度相关、"跑步"和"骑车"的 IMU 信号也相似）——纯对比学习无法清晰定义"正/负样本对"。

解法是 **Memory Stream inspired Temporal Fusion (MSiTF)**——融合时按三个分数加权 patch：

- **Relevance**（相关性）：每个 patch 与查询句（"What activity is the subject doing?"）的 cross-attention 分数
- **Recency**（新近性）：指数衰减，最近的时刻更重要
- **Importance**（重要性）：可学的 Gumbel-softmax 门控

![[Luo_2026_NormWear_page08_Fig4_MSiTF_fusion.png]]

> 图 4 — MSiTF 融合机制。输入信号经过 backbone 得到 vanilla embeddings，然后由 query 句通过 text encoder 生成相关性 query；同时 recency 和 importance 各贡献一个分数；三者加权得到 fused embedding，再做对比学习对齐到文本类标签的嵌入空间。**这张图说明：NormWear 不是简单的对比学习，而是用"任务问句"动态聚焦相关信号片段。**

零样本评估在 16 个 unseen 任务上跑赢了基线 CLAP（最强的频谱基线）；ablation 显示移除 importance gate 或文本数据增强后性能都下降，证明每一部分都贡献。

---

## 怎么证明：11 数据集 × 18 任务 × 3 评估设置

预训练规模：**9 个公开数据集，230K segments → 数据增强（随机片段拼接）扩展到 2.5M segments，14,943 小时信号**。

下游评估覆盖四大类：

| 类别 | 任务示例 | 数据集 |
|------|---------|--------|
| 活动识别 | 压力检测、人体活动识别、疲劳检测 | WESAD, UCI-HAR, DriverFatigue |
| 脑电主任务 | 癫痫眼态识别、效价唤醒情绪 | Epilepsy (5 子任务), GAMEEMO |
| 疾病风险 | 心律异常、高血压/糖尿病/CVD/CVA、肌肉病变 | ECG-Abnormal, PPG-BP (4 子任务), PhysioNet EMG |
| 生命体征 | 血压、血红蛋白、胎儿心率 | Noninvasive-BP, PPG-Hgb, Fetal-fPCG |

![[Luo_2026_NormWear_page12_Fig5_performance.png]]

> 图 5 — 性能全景图。Panel A：full-shot linear probing 下 NormWear 在四类任务上几乎全部领先；Panel B：Critical Difference Diagram 显示 NormWear 平均排名 0.83，统计显著优于 Chronos / TF-C / CLAP / 统计基线；Panel C：消融、scaling law、模块贡献等系统性分析。**这张图说明：NormWear 的领先不是单点偶然，而是跨任务、跨指标、跨设置的稳定提升。**

具体数字：宏平均 NormWear 比 SoTA 自监督框架 TF-C 提升 **3.9%**，比频谱基线 CLAP 提升 **5.3%**，比 LLM-backbone 时序模型 Chronos 提升 **6.1%**。

更有意思的是与**模态专家模型**的对比：NormWear 在 PPG 上反超 PaPaGei（63.3 vs 59.3 AUROC），在 ECG 上大幅领先 ECG-FM（87.6 vs 73.2），仅在 EEG 上微微落后 CBraMod（84.2 vs 84.5）。**用更小的数据训练通用模型，反而压过了专门为单一模态精调的模型**——这是 NormWear 最强的论点。

回归任务（血压、血红蛋白、胎心率）所有方法都能做到合理拟合，区分度不大；NormWear 也保持了基本性能。

![[Luo_2026_NormWear_page15_Fig6_regression.png]]

> 图 6 — 回归任务输出可视化（Hgb / SysBP / DiaBP / FetalHR vs 真值）。**这张图说明：模型在物理学已知关系明确的回归任务上表现稳健，作为 sanity check 验证模型没有"作弊"。**

---

## 数据规模：9 类信号、6 种模态、4,294 小时

![[Luo_2026_NormWear_page06_Fig3_data_distribution.png]]

> 图 3 — 预训练数据分布。左：按传感器模态（PPG / ECG / EEG / GSR / PCG / IMU）；右：按生理信息类型（脉搏、心电、脑活动、皮电、声音、运动）。**这张图说明：预训练数据在六种模态上有合理覆盖（虽然 EEG 偏多），跨模态多样性是 NormWear 泛化能力的基础。**

---

## 意味着什么：可穿戴健康进入"基础模型时代"

1. **设备无关推理是可行的**——不再需要为每款新手表训一个新模型
2. **跨模态信息真的有用**——同样数据量下，能看到所有传感器的模型 > 只看一种的模型
3. **健康场景的 zero-shot 推断初步可达**——给一个新任务的文字描述就能出预测，虽然性能还低于全监督，但定性上能用
4. **Scaling law 适用，但是对数缓增**——增加预训练数据收益递减，不是指数；意味着早期工作回报最高

**已知局限：**

- 专门优化某单一模态（如 EEG）时，专家模型 CBraMod 仍微弱领先——通用 vs 专用的权衡客观存在
- 回归任务提升有限，论文承认是因为这些任务（如 PPG → 血压）已有强物理先验，模型空间有限
- 预训练数据偏向 EEG 和 ECG（图 3），其他模态的代表性不足
- 论文未做种族/性别/年龄子群分析（详见 [[gaps.md]]）

---

## 技术细节速查

**架构参数：**

- 主干：12 个 Transformer block，hidden dim 768
- decoder：2 个 Transformer block + 线性投影 + 卷积层
- patching：与 ViT 一致
- 输入嵌入维度 d=768

**关键公式：**

跨通道融合（[CLS]-Attention）：

$$
z_i = \text{softmax}\left(\frac{Q(z) \cdot K(F_{init}(x_i))^T}{\sqrt{d_k}}\right) \cdot V(z)
$$

$$
z_{modulate} = \text{softmax}\left(\frac{Q(z_{all}) \cdot K(z_{all})^T}{\sqrt{d_k}}\right) \cdot V(z_{all})
$$

其中 $z_{all} = [z_1, z_2, ..., z_N] \in \mathbb{R}^{N \times E}$ 是拼接所有通道的 [CLS]，$z_{modulate}$ 拆开后回插各通道。

MSiTF 重要性 gate（Gumbel-softmax）：

$$
W_{imp}(t) = \arg\max_{i \in \{0,1\}} \frac{\exp((\log(\theta_{t,i}) + \epsilon)/\tau)}{\sum_j \exp((\log(\theta_{t,j}) + \epsilon_j)/\tau)}
$$

τ 设小让结果接近 one-hot，使梯度通过 reparameterization 保留。

**预训练目标：** Masked Auto Encoder + 信号-文本对比对齐辅助损失（vector distance）。Masking 策略：temporal + scale 联合（最优），ratio 75%。

**优化与训练：** PyTorch / GPU 实现；CWT 用固定卷积核加速；scaling 验证 10⁴ → 10⁶ 段呈对数增长。

---

## 🔗 关联

### 相同数据/方法链
- [[Zhang_2015_TROIKA]] — TROIKA 也处理 PPG，但用 SSA+SSR 信号处理；NormWear 用学习方法 + 多模态联合，是范式更替
- [[Perez_2019_AppleHeartStudy]] — Apple Heart Study 是 PPG 单模态特定任务（AF）；NormWear 的通用框架理论上可在零样本下做 AF 检测
- [[Shah_2025_LossOfPulse]] — Shah 用 PPG + 运动多门控算法做心脏骤停；NormWear 的 channel-aware attention 是同一思路的"学习版"

### 概念基础
- [[自监督学习与基础模型]] — NormWear 是自监督基础模型在生理信号领域的实例化
- [[ECE175B_Lecture1a_课程导论与DGM概述]] — DGM 三大问题（learning/inference/sampling）；NormWear 的 MAE 预训练对应 learning 任务

### 应用方向
- [[Mason_2024_TemPredict]] — Oura Ring 测距端温度做抑郁筛查；NormWear 的 zero-shot 能力理论上可处理这类"未见模态 → 心理健康"任务
- [[Arakawa_2023_LemurDx]] — Apple Watch 加速度做 ADHD 多动检测；与 NormWear 形成"专用 small-N RF + 手工特征" vs "通用基础模型 + scaling" 的清晰范式对照
- [[Garg_2025_DopFone]] — 智能手机声学多普勒做胎心率；DopFone 用 AdaBoost + 手工声学/人口学特征，与 NormWear 同样形成"传统 ML 在小样本临床场景" vs "基础模型在大样本通用场景"的范式对照

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/3803808.pdf`
- ACM Trans. Comput. Healthcare, 2026, DOI: 10.1145/3803808
- 第一作者：Yunfei Luo (yul268@ucsd.edu), UCSD; 共同一作 Yuliang Chen (UCSD)；通讯：Tauhidur Rahman (UCSD)
