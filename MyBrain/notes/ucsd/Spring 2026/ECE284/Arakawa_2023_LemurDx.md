---
title: "LemurDx: Using Unconstrained Passive Sensing for an Objective Measurement of Hyperactivity in Children with no Parent Input"
type: source
tags: [ECE284, ADHD, 多动症, Apple Watch, 被动感知, 情境过滤, 临床决策支持, Random Forest, 可穿戴设备, 儿童健康]
sources: ["raw/ucsd/Spring 2026/ECE284/Arakawa_2023_LemurDx.pdf"]
created: 2026-04-27
updated: 2026-04-27
confidence: high
priority: active
---

# LemurDx: Using Unconstrained Passive Sensing for an Objective Measurement of Hyperactivity in Children with no Parent Input

> Apple Watch 在儿童不受约束的日常生活中被动采集运动数据，用"只看安静坐着时的数据"这一情境过滤把 multi-day 加速度信号变成可解释的多动风险分——核心 Random Forest 在 7 天 61 名儿童（25 ADHD/多动）上达到 85.2% 准确率（家长打活动标签）/ 82.0%（自动情境检测，无家长负担）。

---

## 这项研究在解决什么问题

诊断儿童 ADHD 多动表现，目前的金标准是家长和老师填写的 Vanderbilt 等问卷——但**家长和老师对同一个孩子的评分一致度只有 κ = 0.11**（几乎是抛硬币），导致大量过诊或漏诊。临床医生想要一个客观、可在多种情境下对比、用现成设备就能跑的工具。已有研究用动作传感器测多动，但要么是**实验室单次会话**（对慢性病不够用），要么是**24 小时全量数据**（"普通好动小孩 vs 多动小孩"在游乐场都疯——总能量分不出来）。LemurDx 的赌注是：**情境（context）才是把"普通好动"和"病理多动"分开的关键**。

## 核心结论：情境过滤把识别准确率从 67% 拉到 85%

LemurDx 的 ML pipeline 在两种条件下评估：

| 条件 | RF 准确率 | F1-score |
|------|-----------|----------|
| 全部活动（无情境过滤） | 67.2% | 63.0% |
| **只用 sitting/quiet 时段**（情境过滤） | **85.2%** | **81.6%** |
| 自动估计情境（无家长标签） | 82.0% | 78.4% |

12 个对照组儿童（没有 ADHD 但平时挺活跃）在不带情境过滤的模型里被误判成多动；加上"只看安静该静时"的过滤后，10 个被纠正回来。

ROC AUC 同样跳升：with context filtering 0.85，without 0.70。

## 为什么会这样：多动 = 运动量 + "该静不静" 的抖动

直觉先行：**所有小孩在踢足球时都很忙，但在课堂安静做功课时，多动的小孩坐不住——这才是病理特征**。论文用一个对照图把这一点说得很清楚：

![[Arakawa_2023_LemurDx_page10_Fig5_raw_signals.png]]

> Fig 5：同一对照儿童（上）和同一多动儿童（下）在 sleeping / everyday / exercise / at school / sitting/quiet 五种情境下的 5 分钟原始加速度。**前四种情境两组几乎一样**——就 sitting/quiet 列，下方多动儿童出现明显的不规则尖峰。这一张图就是整篇论文的方法学动机。

作者把"多动 = 运动量（amount）+ 抖动（jitteriness）"分开。他们试过用"加速度总能量"作 risk score——准确率只有 67.2%，因为一些对照儿童本来就活跃；但 ML 模型从同一段加速度里学到的"风险分"能区分两组（图 8a：sitting/quiet 时段 p < 0.001 显著；图 8b：单纯能量值不显著）。

> **类比**：同样是车开 100 公里，在高速上和在停车场绕圈，意味完全不同——加速度计能看见"距离 100 km"，但只有加上"在哪条路上"才知道司机的行为是否异常。

## 怎么证明的：61 个孩子 + 256 维特征 + 4 类分类器

**数据**：61 名 5–12 岁儿童（25 多动 / 36 对照），戴 Apple Watch Series 5 共 2–7 天（COVID 期间分两期），用自定义 iOS 应用以 50 Hz 采集三轴加速度（CMSensorRecorder API，权衡电池续航后唯一能稳定跑 12 小时的接口）。家长每天结束时按半小时粒度标记孩子在做什么（sleeping / sitting/quiet / everyday/household / exercise / at school / not wearing / other）。

**特征工程**：每个 30 分钟时段 × 3 轴 × 3 个滑动窗口（5s / 60s / 600s），每窗口提取 12 个时域特征（max, min, range, std, mean, median, skew, kurtosis, ZCR, energy, peak count）+ 12 个 FFT 后频域特征——共 (12+12) × 3 × 3 = **256 维特征/天**。

![[Arakawa_2023_LemurDx_page11_Fig6_pipeline.png]]

> Fig 6：流水线 = 加速度 + 活动标签 → 特征化 → **情境过滤**（只保留 sitting/quiet 行）→ 特征选择 → 分类器输出每日"多动风险分"。第 8 节进一步证明这条流水线的"活动标签"环节可以由另一个 ML 模型自动产生，无需家长标注。

**模型对照**：scikit-learn 的 SGD / 决策树 / Random Forest / Gradient Boost，5 折网格搜索调参，按参与者留一交叉验证（leave-one-participant-out）。Random Forest 全面胜出。

![[Arakawa_2023_LemurDx_page13_Fig7_ML_comparison.png]]

> Fig 7：上图（无情境过滤）所有四个模型勉强 60% 上下；下图（情境过滤后）RF 全线达到 80% 以上。**情境过滤的提升对四种模型都成立**——不是某个模型偶然受益，而是问题表征发生了根本变化。

**与现有方法对比**：在同一数据集上跑 Muñoz-Organero 的 CNN 得 70.5%，跑 Lin 的 ZCR 得 65.6%——和 LemurDx 不带情境过滤时相近。这进一步说明 LemurDx 的核心贡献不是模型架构，而是**让 ML 看着合适的情境数据**。

![[Arakawa_2023_LemurDx_page15_Fig9_per_day_ROC.png]]

> Fig 9 (a)：每个孩子的平均 per-day 风险分按多动 / 对照分组，分布几乎不重叠——绿色虚线 0.5 截断点把两组干净分开。(b) ROC 曲线对照，AUC 从 0.70（无情境过滤）跳到 0.85。

**risk score 还能反映严重程度**：把 RF 输出的连续风险分对照家长填的 VADPRS 量表（0–14 分，越高越多动），存在弱正相关（图 10）——意味着 LemurDx 不仅做二分类，还能给"严重程度连续刻度"，对**药物滴定**（dose titration，目前需要数月家长老师反复问卷）有直接价值。

## 自动情境检测：去掉对家长每日打标签的依赖

如果系统部署给所有家长，让他们每天填 7 类活动标签是不现实的。第 8 节提出：**用同一份运动数据 + 时间索引（48 个半小时槽）+ 校日类型（在校 / 虚拟 / 不上学）训练另一个 RF，自动判断每个半小时是不是 sitting/quiet**。

![[Arakawa_2023_LemurDx_page17_Fig11_context_detection.png]]

> Fig 11 (a)：估计的 sitting/quiet 似然按家长打的真实标签分布——蓝色（everyday/household）和绿色（sitting/quiet）确实有偏移。(b)：精度按家长标签拆分——sitting/quiet 是 0.61，最容易被识别；at school 是 0.018，几乎从不被误判为 sitting/quiet（因为时间索引和"上学日"特征强约束）。

把这个自动情境检测器接到主 pipeline 里，**最终多动检测准确率 82.0%（vs 家长标签的 85.2%）**——掉 3 个百分点，但**整个系统不再需要家长每天打标签**。这个 3 个百分点的小差距，作者归因于家长标签本身就 noisy（家长是日终一次性回忆性补登的，分辨率粗）。

## 这意味着什么

1. **临床部署可行**：用现成 Apple Watch（无需专用 IMU），临床医生有了"客观、连续、按情境过滤、可视化的多动 timeline"——可以填补诊断决策支持工具的空缺
2. **药物滴定加速**：目前 1/4 的儿科患者需要 4 个月以上反复调药，每次调整都要家长 + 老师重填问卷。LemurDx 的半小时分辨率风险分让药效观测周期从"数月"缩短到"数天"
3. **设计哲学：人机协作而非黑盒** —— 5 位临床医生（3 儿科医生 + 2 心理学家）在访谈中明确：**他们不接受黑盒**。LemurDx 把风险分按时间 / 活动情境分解，让医生能"切片查看"——这是研究 [46] 中"Unremarkable AI"理念在 ADHD 诊断上的具体落地
4. **方法学迁移**：情境过滤的核心思想——**"在合适的行为情境下观察症状特征"——可以推广到其他基于运动的精神 / 行为状态评估**（自闭症的重复刻板动作、抑郁的活动减少、儿童焦虑的逃避行为等）

## 局限与作者承认的边界

- **缺中间档样本**：研究只招了 VADPRS ≥ 8（明确多动）和 ≤ 5（明确对照）的孩子；6 / 7 分的"灰色地带"未测
- **二分类太粗**：ADHD 有 3 种表现型（注意力缺失型 / 多动冲动型 / 混合型），LemurDx 只做二分类
- **样本规模**：61 人中 25 多动——对深度学习不够；作者明确选传统 ML 是 small-N 决定的（RF/GB 集成方法在小样本上更鲁棒，参考 Friedman 2001）
- **多药混淆**：Phase 1 的多动儿童在两天数据中有一天用药——已剔除该天
- **无用心率/GPS/Bluetooth**：Apple Watch 已采集这些数据，但 ML 还没用——未来可加入提升情境检测精度

## 技术细节（按需深入）

**特征选择**：256 维特征对 61 个样本太多，作者用迭代法：每轮训练 RF / GB → 取特征重要性高于均值的子集 → 重复直到剩 2–10 维 → 选 LOOCV 表现最佳的子集。

**最优超参数**（5 折网格搜索）：

| 模型 | 无情境过滤 | 带情境过滤 |
|------|------------|------------|
| SGD | iter=4 | iter=4 |
| DT | depth=5 | depth=6 |
| RF | depth=4, n=600 | depth=5, n=400 |
| GB | depth=4, n=500 | depth=4, n=300 |

**自动情境检测器**：RF 输入 = 5 维高相关运动特征 + 时间索引（0–47 半小时槽）+ 校日类型（0/1/2）。准确率 74.5%，精确率 60.8%，召回 60.9%。CNN baseline（修改自 [29]）只有 63.3% / 41.1% / 45.6%——再次说明 small-N 不利于 DL。

**受访 5 位临床医生提出的系统需求**：

1. 算法应输出"随时间变化的多动模式"（时间线，不只是数字）
2. 医生应能按时间 / 情境过滤评分
3. 量化数据应作为"额外证据"而非自动诊断（参考 Sivaraman 2023）

LemurDx 的最终 UI mockup（Fig 1）按这三条需求设计：每日总分 + 按情境分解的小时级风险图 + 按场所标记（家 / 学校 / 室外）。

![[Arakawa_2023_LemurDx_page01_Fig1_UI_mockup.png]]

> Fig 1：临床端 UI 原型。左侧"今日风险分"对比患者本人（红）与对照组（蓝绿色）；右侧小时级风险线 + 底部活动+地点条带——这正是访谈中医生想要的"按情境过滤的 timeline 视角"。

---

## 🔗 关联

### ECE284 内的方法学对照
- [[Luo_2026_NormWear]] — 都是可穿戴 ML，但 NormWear 走基础模型 + 自监督 + scaling 路线（11 数据集 18 任务），LemurDx 走专用 RF + 手工特征 + small-N 路线。形成"通用 vs 专用"清晰对照
- [[Mason_2024_TemPredict]] — 都是消费级智能设备 + 多日采集 + ML 预测心理行为状态；TemPredict 用 Oura Ring 体温做抑郁标志，LemurDx 用 Apple Watch 加速度做 ADHD——同属"长期被动感知 + 临床心理评估"范式
- [[Perez_2019_AppleHeartStudy]] — 同样用 Apple Watch + 大规模消费数据进入诊断；都需要应对"佩戴不连续 / 数据稀疏"。Apple Heart Study 是大规模验证（41 万人）模型已部署，LemurDx 仍处于 N=61 验证阶段
- [[Shah_2025_LossOfPulse]] — 都是消费级智能手表用于临床 ML；LossOfPulse 用多门控规则 + 极高特异性约束，LemurDx 用情境过滤 + 解释性优先约束——两种"ML 进入消费医疗设备"的不同设计哲学
- [[Zhang_2015_TROIKA]] — TROIKA 处理腕式 PPG 在剧烈运动下的伪影（运动是"问题"），LemurDx 把运动本身当作"信号"——同一类信号在不同任务里角色相反

### 跨课程关联
- [[争论_婴儿被动vs主动学习]] — Adolph 2018 提出的"发展研究中情境塑造行为"原则，与 LemurDx 的"情境塑造可观测多动"哲学结构相似（待考察是否值得 synthesis 页）

### 概念
- 情境过滤（context filtering）作为可穿戴 ML 的特征工程范式——目前 LemurDx 是 vault 内最系统论述者，建议未来若有第二来源加入再提取 concept 页

> 💡 此论文是 concept [[消费级设备健康感知]] 的核心支柱之一（Apple Watch 被动感知 + 情境过滤，2026-05-02 提取）。

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/Arakawa_2023_LemurDx.pdf`
- 出版：*Proc. ACM Interact. Mob. Wearable Ubiquitous Technol. (IMWUT)*, Vol. 7, No. 2, Article 46, June 2023
- DOI: 10.1145/3596244
