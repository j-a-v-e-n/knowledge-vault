---
title: "Harnessing wearable device data to improve state-level real-time surveillance of influenza-like illness in the USA: a population-based study"
type: source
tags: [ECE284, wearable, Fitbit, 流感, ILI, 公共卫生监测, nowcasting, 静息心率, Topol]
sources:
  - raw/ucsd/Spring 2026/ECE284/nihms-1569235.pdf
authors: Jennifer M Radin, Nathan E Wineinger, Eric J Topol, Steven R Steinhubl
journal: Lancet Digital Health 2020;2(2):e85-e93
doi: 10.1016/S2589-7500(19)30222-5
year: 2020
created: 2026-05-18
updated: 2026-05-18
confidence: high
priority: active
---

# Radin et al. 2020 — 用 Fitbit 数据改善美国州级流感实时监测

> Scripps + Topol 团队：47,249 个 Fitbit 用户 + 13.3M 个 RHR/睡眠测量数据 → 在 5 个州把 CDC ILI rate 的预测相关系数提升 6.3-32.9%（average +0.12 Pearson r）。**首次证实** consumer wearable 数据可在 population 级补足 CDC 1-3 周报告滞后。

---

## 这项研究在解决什么问题？

**CDC 的 ILI（influenza-like illness）surveillance 有 1-3 周滞后 + 数月后还要 revise——疫情爆发时这种延迟就是"看到大火时已经烧了 3 周"。**

之前的尝试都翻车：
- **Google Flu Trends**: 错过 2009 H1N1 早期 wave + outbreak 期间 over-estimate
- **Twitter**: 受媒体报道污染（"worried well" 搜索）
- 这些都是 indirect signal（搜索 / 推文），不是生理 signal

2016 年 12% 美国 consumer 已用 fitness band / smartwatch。Wearable 持续测 RHR + sleep — 当人发烧 / 感染时 RHR 升 + sleep 异常是已知生理反应。**问题**：能不能在 population level 用这些数据做实时 nowcasting？

## 核心论点（一句话）

**Fitbit 用户的 RHR + sleep 数据加入 negative binomial 模型，能让所有 5 个测试州（CA / TX / NY / IL / PA）的 CDC ILI 预测 Pearson 相关系数平均提升 0.12（6.3-32.9%），final r = 0.84-0.97**。

---

## 数据 + 方法

### Dataset
- **200,000 Fitbit 用户**（Scripps × Fitbit 合作，de-identified）
- 2016-03-01 → 2018-03-01（2 年）
- 5 个 top-user 州：California / Texas / New York / Illinois / Pennsylvania
- Inclusion：≥60 天 wear，single device，birth year 1930-2004
- **筛后 47,249 users + 13,342,651 daily measurements**
- 平均年龄 42.7 岁（SD 14.6），60.2% 女性
- 平均 RHR 65.6 bpm（SD 8.4），睡眠 6.6 h/night（SD 1.9），wear time 22.5 h/day

### Calculation of RHR (Fitbit 内置)
- Accelerometer 检测 ≥5 min inactivity period → 估当时 HR = resting
- Sleep HR 也辅助 estimate
- Fitbit 自己 validation：vs ECG **mean error < 1 bpm**

### CDC ILI ground truth
- CDC FluView database
- ILI = weekly % outpatient visits with temp > 37.8°C + cough/sore throat without known cause
- Collected from sentinel surveillance clinics

### Abnormality 阈值（核心 design）
- 每周 RHR 平均 > user 自己 overall mean + 0.5 SD（model 1）or 1.0 SD（model 2）→ "elevated RHR"
- 睡眠平均 > user 自己 mean + 0.5 SD → "elevated sleep"
- "Abnormal" = elevated RHR **AND** elevated sleep（两条件 both 满足）
- Model 1 (0.5 SD): 24.3% weekly measurements 被标 abnormal
- Model 2 (1.0 SD): 11.2% abnormal

→ **Final model 用 0.5 SD 阈值 + RHR + sleep combined**（correlation 最高）

### Statistical model
Negative binomial models:

$$m_{abs,H1}: \log(Y_{jk}) = \beta_0 + \beta_{p,k} \cdot p_{j-3,k} + \beta_{x,k} \cdot x_{j,k,l} + \log(n_{j,k})$$

- $Y_{jk}$ = ILI case count week $j$ state $k$
- $p_{j-3,k}$ = ILI rate 3 weeks ago（baseline term, autoregressive）
- $x_{j,k,l}$ = proportion Fitbit users abnormal week $j$ state $k$
- $n_{j,k}$ = offset (number of outpatient visits)
- Null: $\beta_x = 0$（no Fitbit contribution）
- State-stratified (state-by-Fitbit interaction term significant)

Linear regression for week-over-week change ($m_{change}$) — better corrected for autocorrelation

### Validation
- Train: season 1 (2016 wk 11 - 2017 wk 10)
- Validate: season 2 (2017 wk 11 - 2018 wk 9)
- All states except NY improved with Fitbit variable on validation
- NY 弱 because season 1 NY 没报 summer week ILI → training 数据短

---

## 关键结果（数字 verbatim）

### Main model 结果

**全部 5 个州 $m_{abs,H1}$（含 Fitbit）> baseline $m_{abs,H0}$**：
| State | Pearson r improvement | Final r |
|---|---|---|
| California | **+32.9%** | **0.97** (highest) |
| Texas | (中) | 中 |
| Illinois | (中) | 中 |
| Pennsylvania | (中) | 中 |
| New York | +6.3% (lowest) | 0.89 (lowest) |

- **平均 Pearson improvement: +0.12 (SD 0.07)**
- 所有 state × Fitbit interaction term 显著（p < 0.0001）

### 跨季节 validation
- Season 1 → Season 2: 全部 state 改善（除 NY）
- Validated Fitbit signal 不是 fluke

### Change model ($m_{change}$)
- 部分 state 周-周变化也能预测
- **但 cross-correlation 显示 Fitbit data 不 lead ILI**——Fitbit 信号跟 ILI 信号 **concurrent 或 1-week lag**，不提前

---

## paper 自己 acknowledged 关键局限

1. **No activity data** — 数据集只 RHR + sleep，没 step / activity 强度（本来能提升模型）
2. **Weekly average 混合 sick + non-sick days** — 一周 1 天发烧 + 6 天健康 → mean RHR 被稀释
3. **Sleep tracker accuracy low** (cited 一篇 critical review)
4. **Fitbit users wealthier than general population** → selection bias，可能 healthier / better vaccinated → underestimate ILI in low-SES communities
5. **2017-18 是 H3N2 严重季** → 更高 ILI peak，可能 model fit 部分由 H3N2 严重性驱动
6. **非流感感染也能引起 RHR↑** → Fitbit signal 不是 flu-specific
7. **NY 1 季 summer 没报 ILI → training data 少 → NY 模型最弱**

---

## Discussion 关键 framings

### 跟之前 nowcasting 比的优势
- Google Flu Trends / Twitter / Wikipedia / weather / school vacations 全部 affected by "worried well"（媒体一报道 → 搜索/推文飙升 ≠ 真实 ILI）
- **Wearable 数据是 objective**, 不被 media coverage 影响
- 这是 "first study to evaluate use of RHR and sleep data in a large population to predict real-time ILI rates at the state level"

### Lead-time 局限
- $m_{change}$ 模型 1-week LAG 比 1-week LEAD 表现更好
- → 意味着 wearable signal 通常**跟随**或**concurrent**，不**先于** clinical ILI
- 但仍快于 CDC 1-3 周报告滞后
- "individuals with febrile respiratory illness typically seek care 3-8 days after symptom onset" → wearable 可能比 clinic-based 早 3-8 天

### Mechanism
- 引 Karjalainen 1986: 27 个 acute febrile infections 患者 HR ↑ 8.5 bpm per 1°C 体温上升
- 引 Thompson 2009: 急性感染儿童 HR ↑ 9.9-14.1 bpm per 1°C
- → "infections can increase heart rate, probably due to increased body temperature and inflammatory responses"

### Future
- 新一代 wearable + BP / temp / pulse ox / ECG / cough sound → 进一步提升
- Daily prediction 可能（不只 weekly）
- 全球扩展（surveillance 不发达地区可用）

---

## ⚠️ 矛盾与未解决问题

- **Lead vs Lag 张力**: paper claims "real-time surveillance"，但实证显示 Fitbit signal lag ILI，不 lead — 它是更快报告，不是更早预测
- **Wearable bias**: 测的是 self-selected fitness-conscious 富裕 population → 跟 CDC ILI 测的 outpatient visit 人群（全民）不重合 → 1.0 correlation 不应预期
- **"Abnormal" threshold 是 ad-hoc**: 0.5 SD vs 1.0 SD 选 0.5 因为 correlation 高 — 但这是 outcome-driven model selection（overfit risk）
- **不能区分 flu vs 其他急性感染** — paper 自己承认；意味着 "ILI rate prediction" 实际是 "any febrile respiratory illness rate prediction"，跟 CDC ILI definition 本来就不完全对齐

---

## 🔗 关联

### 核心 concept
- [[消费级设备健康感知]] — 本 paper 是 population-level 消费级设备 PH surveillance 的 landmark 证据
- 跟 individual-level wearable health detection 形成对比维度（同样 wearable，population vs individual scale）

### 同主题（wearable for surveillance）
- [[Perez_2019_AppleHeartStudy]] — Apple Watch 大规模 enrollment，同样 selection bias 问题
- [[Mason_2024_TemPredict]] — Oura ring 个体级 COVID detection
- [[Shah_2025_LossOfPulse]] — Pixel Watch loss-of-pulse 检测
- [[Garg_2025_DopFone]] — smartphone doppler vitals

### 对比维度
- [[Anglemyer_2020_数字接触追踪Cochrane综述]] — 都是 digital PH surveillance，但本 paper 是 physiological signal aggregation，Anglemyer 是 contact graph tracking
- [[Minakshi_2020_智能手机蚊媒识别]] — 都是 surveillance 自动化，但 Minakshi 是 vector 不是 human

### 方法学
- Negative binomial + state-stratified interaction term — 跟传染病建模常用的 GLM
- AR(3) baseline term 设计 — 跟 Yang 2015 ARGO 同源

### 课程对接
- ECE284 wearable surveillance 主题核心 reading
- Topol 团队是 ECE284 syllabus 常引

---

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/nihms-1569235.pdf`
- Lancet Digital Health 2020;2(2):e85-e93
- DOI: 10.1016/S2589-7500(19)30222-5
- Available PMC: 2021-04-15
