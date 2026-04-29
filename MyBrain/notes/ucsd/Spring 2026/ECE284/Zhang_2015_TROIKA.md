---
title: "TROIKA: A General Framework for Heart Rate Monitoring Using Wrist-Type Photoplethysmographic Signals During Intensive Physical Exercise"
type: source
tags: [PPG, 心率监测, 运动伪影, 稀疏信号重建, SSA, 可穿戴设备, ECE284]
sources: [raw/ucsd/Spring 2026/ECE284/Zhang_2015_TROIKA.pdf]
created: 2026-04-09
updated: 2026-04-09
confidence: high
priority: active
---

# TROIKA：运动中腕式 PPG 心率监测框架

> Zhang et al. 提出 TROIKA 框架，通过信号分解（SSA）去噪 + 稀疏信号重建（FOCUSS）高分辨谱估计 + 谱峰跟踪与验证三步流水线，在剧烈运动（15 km/h 跑步）下从腕式 PPG 信号估计心率，平均绝对误差仅 2.34 BPM，Pearson 相关系数 0.992。

---

## 问题背景

### PPG 信号与心率监测
- Photoplethysmography (PPG，光电容积脉搏波)：脉搏血氧仪通过 LED 照射皮肤，测量反射光强度变化
- PPG 信号的周期性对应心脏节律 → 可估计心率（HR）
- 腕式 PPG 是智能手表的主流方案（Samsung Gear Fit、Mio Alpha 等）

### 核心挑战：运动伪影（Motion Artifact, MA）
- 剧烈运动时手部活动产生**极强的运动伪影**，淹没心跳信号
- 腕部比指尖/耳垂的 MA 更严重：关节灵活度大、传感器-皮肤接触松散
- 已有方法（ICA、ANC、加速度谱减法、EMD 等）多针对**轻度运动**（手指活动、步行），不适用于剧烈跑步

### 为什么传统频谱估计不够？
1. **Periodogram（FFT）**：不一致估计器，高方差；严重的泄漏效应使 HR 谱峰被邻近的 MA 谱峰淹没
2. **MUSIC 等高分辨谱估计**：需要模型阶数选择，对 MA 污染的时变信号很困难
3. **稀疏信号重建（SSR）**：高分辨率、低方差、不需模型选择 → 但要求频谱稀疏

### 图 2–4：频谱分析问题与 TROIKA 流程图

![[Zhang_2015_TROIKA_page03.png]]

> **Fig 2**（左列）：MA 存在时的 PPG 频谱。Periodogram 谱峰对应 MA 而非心率；SSA 处理后 SSR 能清晰恢复对应真实 HR 的谱峰（红圈标注）。
> **Fig 3**（右列）：极端情况——PPG 频谱中 HR 谱峰完全被淹没；原始 PPG 和 Periodogram 均无法识别，SSA 后 SSR 可以。
> **Fig 4**（右下）：TROIKA 整体流程图——带通滤波 → 信号分解（SSA）→ 时间差分 → 稀疏信号重建（FOCUSS）→ 谱峰跟踪（选择 + 验证）→ 输出 BPM。

---

## TROIKA 框架

**TROIKA** = signal decomposiTion + sparse signal RecOnstructIon + spectral peaK trAcking

### 整体流水线

```
输入 PPG + 3 轴加速度
    ↓
带通滤波（0.4–5 Hz）
    ↓
信号分解（SSA）→ 去除 MA 分量，稀疏化频谱
    ↓
时间差分（2 阶）→ 突出周期性分量，抑制随机波动
    ↓
稀疏信号重建（FOCUSS）→ 高分辨率频谱
    ↓
谱峰跟踪（选择 + 验证）→ 输出 BPM
```

### 第一步：信号分解（SSA）

**Singular Spectrum Analysis (SSA，奇异谱分析)**：将时间序列分解为振荡分量 + 噪声

四步：
1. **嵌入**：将长度 M 的时序映射为 L×K 的轨迹矩阵（Hankel 矩阵）
2. **SVD**：对轨迹矩阵做奇异值分解
3. **分组**：将秩 1 矩阵按振荡特性聚类
4. **重构**：对角平均还原时间序列

**MA 识别策略**：
- 用加速度数据的 Periodogram 找到 MA 主频 → 集合 F_acc
- 排除与前一窗口 HR 估计（基频+谐波）接近的频率（保护区 ±Δ）
- 移除 SSA 分量中主频落在 F_acc 内的分量

参数：L=400, FFT 点数 4096, Δ=10（≈0.3 Hz 保护带）

### 第二步：时间差分

- 对 SSA 清洗后的 PPG 做 2 阶差分
- 周期信号差分后保留基频和谐波；非周期 MA 的随机谱波动被抑制
- 使心跳谱峰更突出

### 第三步：稀疏信号重建（SSR）

模型：**y = Φx + v**
- Φ：DFT 基矩阵（M×N，N=4096）
- x：稀疏频谱系数
- 求解：min ‖y - Φx‖² + λg(x)，g(x) 为稀疏惩罚（ℓ_p 范数，p=0.8）

**算法选择**：FOCUSS（Regularized M-FOCUSS），对高度相关列的 Φ 矩阵鲁棒，仅需 5 次迭代。

**计算优化**：基于带通范围裁剪 Φ 的列，大幅减少计算量。

### 第四步：谱峰跟踪

#### 初始化
- 要求佩戴者前 2-3 秒减少手部运动 → 选最高谱峰作为初始 HR

#### 峰选择（三种情况）
1. **Case 1**：基频搜索范围 R₀ 和一阶谐波搜索范围 R₁ 中存在谐波配对 → 选基频峰
2. **Case 2**：无谐波配对 → 选离前一窗口 HR 最近的峰
3. **Case 3**：搜索范围内无峰 → 保持前一窗口的 HR

搜索范围：Δs=16 个频率格（≈5 BPM）

#### 验证规则
1. **防突变**：连续两窗口 BPM 变化 >11 BPM 时正则化（θ=6 格）
2. **防丢失**：连续 h=3 个窗口 HR 不变时，用 3 阶多项式趋势预测微调，并扩大搜索范围（Δs=20）

---

## 实验设计与结果

### 数据采集
- 12 名男性受试者（18-35 岁）
- 腕式绿光 LED PPG（515 nm，勘误修正）+ 3 轴加速度计（嵌入腕带）
- 胸部湿电极 ECG 作为 ground truth
- 采样率：125 Hz
- 运动方案：步行 1-2 km/h → 跑 6-8 km/h → 快跑 12-15 km/h → 跑 6-8 km/h → 快跑 12-15 km/h → 步行 1-2 km/h
- 额外干扰：要求受试者用佩戴腕带的手拉衣服、擦汗、按跑步机按钮

### 性能指标

| 指标 | 完整 TROIKA |
|------|-----------|
| 平均绝对误差（Error1）| **2.34 ± 0.82 BPM** |
| 平均误差百分比（Error2）| **1.80%** |
| Pearson 相关系数 | **0.992** |
| Bland-Altman LOA | [-7.26, 4.79] BPM (σ=3.07) |

### 图 5–7：性能评估（Bland-Altman + Pearson + 示例估计曲线）

![[Zhang_2015_TROIKA_page08.png]]

> **Fig 5**（左）：Bland-Altman 图，12 名受试者全部数据点。Mean = −1.24 BPM，LOA = [−7.26, 4.79] BPM（σ = 3.07）。
> **Fig 6**（右下）：Pearson 相关图，r = 0.992。
> **Fig 7**（右上）：Subject 6 的完整运动序列估计曲线——TROIKA 估计（蓝）与真实 HR（绿）几乎重合；去掉 SSA 后（红）估计严重错误（Error1 暴涨至 55.2 BPM）。

### 消融实验（缺少任一部分均导致性能崩溃）

| 配置 | 跨 12 人的表现 |
|------|-------------|
| 完整 TROIKA（SSA+FOCUSS+验证）| 所有受试者稳定，Error1 = 1.67–4.70 |
| 去掉 SSA | Subject 6 Error1 暴涨到 55.2 BPM |
| FOCUSS→FFT | Subject 1 Error1 暴涨到 62.73 BPM |
| 去掉验证 | Subject 6/10/12 Error1 暴涨到 51-60 BPM |

**结论**：三部分缺一不可。

### 参数鲁棒性
- L 在 100-400、Δ 在 5-15、τ 在 0-4、Δs 在 12-20 范围内变化，性能几乎不变
- 采样率降至 25 Hz 时参数需按比例调整，性能相当但计算大幅缩短

### 与先前方法对比

| 方法 | 条件 | Pearson r |
|------|------|-----------|
| Poh et al. (2010) [16] | 跑步 8 km/h，耳部 PPG | 0.75 |
| Yousefi et al. (2014) [7] | 步行 4.8-8 km/h，指尖 PPG | 0.64-0.78 |
| Fukushima et al. (2012) [8] | 跑步，腕式 PPG | σ = 8.7 BPM |
| **TROIKA** | **跑步 15 km/h，腕式 PPG** | **0.992** (σ=3.07) |

---

### 图 8–9：运动场景估计 + SSA 去噪效果展示

![[Zhang_2015_TROIKA_page09.png]]

> **Fig 8**（左上）：Subject 5 的步行→跑步→快跑→跑步→快跑→步行完整序列估计，TROIKA 与真实 HR 高度吻合。
> **Fig 9**（左下）：同时记录的 ECG、原始 PPG、PPG 频域、SSA 后 PPG 频域（4 行对比）。SSA 前（第 3 行）MA 谱峰掩盖 HR；SSA 后（第 4 行）HR 谱峰清晰可辨，SSR 可准确估计。
> **Fig 10**（右）：参数鲁棒性测试结果——L、Δ、τ、Δs 在合理范围内变化，Error1 几乎不变。

---

## 框架的通用性

TROIKA 是框架而非固定算法——三个核心部分均可替换：
- SSA → EMD（经验模态分解）
- FOCUSS → Sparse Bayesian Learning
- 谱峰跟踪的具体规则可根据场景调整

---

## 勘误（附于论文末）

1. 原文引用 [15] 不应出现在"慢跑"相关引用中 → 应为 [7], [16]
2. LED 波长应为 **515 nm**（绿光），原文误写 609 nm

---

## ⚠️ 矛盾与未解决问题

1. **初始化依赖静止**：框架要求开始时佩戴者减少手部运动 2-3 秒以获取初始 HR。实际使用中（如运动已在进行中启动监测），此假设可能不成立。
2. **受试者多样性有限**：12 名受试者均为黄种男性、18-35 岁——未验证在不同肤色（PPG 信号质量受肤色影响显著）、年龄、性别上的泛化性。
3. **单通道 PPG 极端情况**：论文承认当 PPG 信号完全不含心跳分量时（Fig. 3），框架只能保持前一窗口估计，无法恢复真实 HR。

---

## 🔗 关联

- [[Perez_2019_AppleHeartStudy]] — 同属 PPG 可穿戴心率监测领域；TROIKA 解决信号处理问题，Apple Heart Study 解决大规模临床验证问题
- [[Shah_2025_LossOfPulse]] — 同属 PPG 可穿戴检测；Shah 的多门控系统同样需解决运动噪声，与 TROIKA 的运动伪影去除方向互补
- [[Luo_2026_NormWear]] — 范式转移：TROIKA 用 SSA + FOCUSS 等手工信号处理流水线针对单一任务（HR）优化；NormWear 用 Transformer 基础模型直接学习多任务通用表征。对比说明"信号处理流水线 → 学习方法 + 多模态联合"的方法论演进
- [[Arakawa_2023_LemurDx]] — 同样基于消费级智能手表的运动信号；TROIKA 把运动当作"问题"（运动伪影）去除，LemurDx 把运动本身当作"信号"（多动症标志）——同一类信号在不同任务里角色相反，是有趣的方法学对照
- [[Garg_2025_DopFone]] — 同为无创心率测量；TROIKA 走 PPG（光学），DopFone 走 Doppler（声学）——不同物理原理但相似挑战：消费硬件限制下提取微弱周期信号、应对运动伪影、个体差异
- [[COGS117_概览]] — 同为 UCSD Spring 2026 课程（不同院系/领域）

---

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/Zhang_2015_TROIKA.pdf`
- Zhang, Z., Pi, Z., & Liu, B. (2015). TROIKA: A General Framework for Heart Rate Monitoring Using Wrist-Type Photoplethysmographic Signals During Intensive Physical Exercise. *IEEE Transactions on Biomedical Engineering*, 62(2), 522–531. DOI: 10.1109/TBME.2014.2359372
