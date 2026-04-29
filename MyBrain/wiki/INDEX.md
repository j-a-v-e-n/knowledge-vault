# 知识库总目录

**最后更新**：2026-04-27 | **页面总数**：56 | **最新操作**：编译 ECE284 两篇 IMWUT 论文 — [[Arakawa_2023_LemurDx]]（Apple Watch + 情境过滤检测儿童 ADHD 多动）+ [[Garg_2025_DopFone]]（智能手机 18 kHz Doppler 测胎心率）；7 个相关 ECE284 source 加双向回链；渲染 13 张关键图；发现 vault 内位置错误（`notes/Bhamla_2017_Paperfuge.md` 实为 Apple Heart Study 演讲稿）等待 Javen 决策

---

## 📚 UCSD · ECE175B Spring 2026

### 课程总览
- [[ECE175B_概览]] — 课程信息、知识地图、讲座进度、核心概念索引

### 讲座笔记
- [[ECE175B_Lecture1a_课程导论与DGM概述]] — 课程后勤、DGM 定义（概率图模型+深度学习）、判别 vs 生成模型、三大核心问题、BN 分解公式
- [[ECE175B_Lecture1b_贝叶斯网络]] — DAG 七节点分解实例、I-map 性质、LLM 就是链式 BN、Transformer 参数化条件分布
- [[ECE175B_Lecture2_变分自编码器设计]] — VAE 的 Z→X 图设计、先验 N(0,I)、decoder 神经网络输出均值+方差、三大任务
- [[ECE175B_Lecture3_变分推断与ELBO]] — 推断 NP-hard 问题、KL 散度、MLE 困难、Jensen 不等式 → ELBO 推导、EM 坐标上升
- [[ECE175B_Lecture4_生成对抗网络]] — 图灵测试类比、Generator vs Discriminator、对抗训练、VAE vs GAN 对比

### HW / Project 调研
- [[2026-04-20_多模态故事生成研究]] — HW1 调研（位于 notes/web-research/）：三大架构范式、Transfusion / Chameleon / DiffuStory / Infinite-Story 详细对比

---

## 🌐 Web Research（外部资料调研）

存放从外部来源（WebSearch / WebFetch / 视频字幕等）抓取并编译的研究笔记。原始文件在 `raw/web-research/`，source 页镜像至 `notes/web-research/`。

- [[2026-04-20_多模态故事生成研究]] — ECE175B HW1 调研：统一多模态生成架构现状（Transfusion / Chameleon / DiffuStory / Infinite-Story），抓取自 5 个权威来源（arXiv / Elsevier / AAAI）
- [[2026-04-27_AI任务面板自动化系统]] — 思瑶视频字幕：五层架构 AI agent 任务看板系统，事件驱动调度（fswatch + launchd），blocked on 用户授权机制，注意力分配规则适配 ADHD

---

## 📚 UCSD · COGS117 Spring 2026

### 课程总览
- [[COGS117_概览]] — 主题、学习目标、考核结构、完整阅读清单

### 讲座笔记（按周顺序）
- [[Zettersten_2026_Lecture1_课程导论与大问题]] — Week 1：四大问题、Moravec 悖论、Alpine Ibex、保护性不成熟、核心知识、A-not-B
- [[Zettersten_2026_Lecture2_发展研究方法]] — Week 1：家长报告、SEEDLingS、习惯化、违反预期、EEG/fNIRS/MRI
- [[Zettersten_2026_计算模型与框架]] — Week 2：科学建模、Marr 层级、贝叶斯推断、神经网络基础
- [[Zettersten_2026_Lecture4_发展理论]] — Week 2：Piaget / Vygotsky / 信息加工 / 动态系统 / 连接主义
- [[Zettersten_2026_Lecture5_感知发展1]] — Week 3：面孔、物体统一性、核心知识、Emberson 自上而下预期
- [[Zettersten_2026_Lecture6_感知发展2]] — Week 3：类别发展（全局→基本）、标签帮助个体化、Clerkin & Smith 婴儿训练数据统计
- [[Zettersten_2026_Lecture7_走路与动作发展]] — Week 4：反射、Thelen stepping、新生儿模仿争议、里程碑误区、发展级联

### 核心概念
- [[监督学习与无监督学习]] — 定义、历史脉络（心理学+AI）、连续谱观点
- [[自监督学习与基础模型]] — 原理、方法分类、规模效应、与婴儿发展的争议类比
- [[感知窄化]] — 面孔/语音/音乐跨通道窄化机制；曝光 × 加工粒度
- [[面孔知觉发展]] — 从 CONSPEC 到专化；剥夺实验；两条腹侧通路
- [[核心知识理论]] — Spelke 五大领域专化先验（物体/数量/空间/行动/社会）
- [[物体识别与形状感知]] — 骨架模型、视点不变性、婴儿期腹侧通路
- [[发展研究方法]] — 方法论百科：家长报告/自然观察/行为范式/神经成像/计算建模
- [[动作发展]] — 成熟论 vs 动态系统；里程碑的正确 vs 错误用法；跨文化变异
- [[发展级联]] — 一个技能的出现引发其他多领域连锁变化
- [[内在动机与好奇心驱动学习]] — 好奇心形式化为"学习进步最大化"；Playground 实验

### 文献笔记
- [[COGS117_2026_课程大纲]] — 课程大纲原始记录：组织、政策、评分、迟交规则、AI 使用政策
- [[Love_2026_监督与无监督学习]] — Love (2026 OECS)：监督/无监督是连续谱，自监督模糊边界，表征对齐条件
- [[Frank_2023_数据鸿沟]] — Frank (2023)：LLM 与儿童数据量差距 3–5 个数量级的三种解释假说
- [[Cusack_2024_婴儿无助期假说]] — Cusack et al. (2024)：无助期 = 自监督预训练；神经发育和影像证据
- [[Zettersten_2025_婴儿主动学习]] — Zettersten et al. (2025)：四大反驳——主动性、跨域整合、变异性、适应性行为
- [[Scott_2009_面孔知觉偏差起源]] — Scott & Monesson (2009)：个体标签保留猴脸辨别能力（M=61.3%, p=.018）；窄化被加工粒度调节
- [[Johnson_2024_婴儿感知]] — Johnson (2024 OECS)：视觉/听觉/跨通道/物体感知百科综述
- [[Ayzenberg_2024_视觉物体识别发展]] — Ayzenberg & Behrmann (2024)：形状/骨架表征；面孔剥夺猕猴实验；两条腹侧通路
- [[Adolph_2018_走路发展15条建议]] — Adolph, Hoch & Cole (2018)：走路作为发展模型系统；里程碑误区；2400 步/小时；跨文化；15 条普适建议
- [[Oudeyer_2017_婴儿发展机器人]] — Oudeyer (2017 WIREs)：被动动态步行机、Playground 实验、好奇心形式化为"学习进步最大化"

### 理论辩论
- [[争论_婴儿被动vs主动学习]] — Cusack vs Zettersten 四大矛盾点对照 + 感知/动作发展证据的延伸
- [[争论_新生儿模仿]] — Meltzoff 1977 vs Jones 2006 vs Oostenbroek 2016 三方辩论

---

## 📚 UCSD · ECE284 Spring 2026

### 文献笔记
- [[Zhang_2015_TROIKA]] — Zhang et al. (2015)：TROIKA 框架——SSA 去噪 + SSR 高分辨谱估计 + 谱峰跟踪，腕式 PPG 剧烈运动心率监测，误差 2.34 BPM
- [[Perez_2019_AppleHeartStudy]] — Perez et al. (2019)：Apple Watch 大规模房颤筛查——419,297 人，0.52% 通知率，通知 PPV 84%，首个消费级可穿戴 AF 检测临床验证
- [[Shah_2025_LossOfPulse]] — Shah et al. (2025)：智能手表自动检测心脏骤停无脉——多门控 PPG + 运动算法，特异性 99.987%（21.67 用户-年 1 次误报），敏感度 67.23%
- [[Bhamla_2017_Paperfuge]] — Bhamla et al. (2017)：20 美分纸质离心机——基于陀螺力学，125,000 rpm / 30,000 g，1.5 min 分离血浆,15 min 分离疟疾寄生虫（附全部 4 图）
- [[Song_2024_SmartphoneMicroscope]] — Song & Adams (2024)：智能手机显微镜附件术前血细胞计数——Hough 圆检测，R²=0.895，召回率 0.9312，约 1 秒处理
- [[Jubran_1990_脉搏血氧仪种族偏差]] — Jubran & Tobin (1990)：脉搏血氧仪在机械通气患者中的种族差异——SpO₂ 92% 对白人 PPV 100%，对黑人 PPV 50%；深色皮肤色素干扰光学测量
- [[Obermeyer_2019_医疗算法种族偏见]] — Obermeyer et al. (2019)：商业医疗管理算法的种族偏差——费用代理健康导致黑人患者风险分系统性低估，同等风险分下多 26.3% 慢性病
- [[Luo_2026_NormWear]] — Luo et al. (2026)：可穿戴信号通用基础模型——CWT tokenization + 通道感知 [CLS] 联络员 token + MAE 预训练；11 数据集 18 任务上跑赢专用模型，提供 zero-shot 文本对齐能力
- [[Mason_2024_TemPredict]] — Mason et al. (2024)：TemPredict 队列研究——20K 人 Oura Ring 7 个月数据，清醒体温每升 1°C → PROMIS 抑郁 T-score +0.86 分；全身热疗作为治疗启示
- [[Arakawa_2023_LemurDx]] — Arakawa et al. (2023 IMWUT)：Apple Watch 被动感知 + 情境过滤检测儿童 ADHD 多动；N=61，with context filtering RF 准确率 85.2%（家长标签）/ 82.0%（自动情境检测）；半小时分辨率 risk score 支持药物滴定
- [[Garg_2025_DopFone]] — Garg et al. (2025 IMWUT)：智能手机 18 kHz Doppler 测胎心率；N=23 孕妇，AdaBoost MAE 2.1±1.3 BPM、95% LoA ±4.9 BPM（< 临床阈值 ±8 BPM），位置无关 + 用户无需训练；BMI ≥ 30 时误差升 33%

---

## 🗂️ 按类型分类

| type | 页面 |
|------|------|
| **overview** | [[COGS117_概览]], [[ECE175B_概览]], [[PHIL28_概览]] |
| **concept** | [[监督学习与无监督学习]], [[自监督学习与基础模型]], [[感知窄化]], [[面孔知觉发展]], [[核心知识理论]], [[物体识别与形状感知]], [[发展研究方法]], [[统一多模态生成架构]], [[动作发展]], [[发展级联]], [[内在动机与好奇心驱动学习]] |
| **source** | [[COGS117_2026_课程大纲]], [[Love_2026_监督与无监督学习]], [[Zettersten_2026_计算模型与框架]], [[Frank_2023_数据鸿沟]], [[Cusack_2024_婴儿无助期假说]], [[Zettersten_2025_婴儿主动学习]], [[Scott_2009_面孔知觉偏差起源]], [[Johnson_2024_婴儿感知]], [[Ayzenberg_2024_视觉物体识别发展]], [[Adolph_2018_走路发展15条建议]], [[Oudeyer_2017_婴儿发展机器人]], [[Zettersten_2026_Lecture1_课程导论与大问题]], [[Zettersten_2026_Lecture2_发展研究方法]], [[Zettersten_2026_Lecture4_发展理论]], [[Zettersten_2026_Lecture5_感知发展1]], [[Zettersten_2026_Lecture6_感知发展2]], [[Zettersten_2026_Lecture7_走路与动作发展]], [[Zhang_2015_TROIKA]], [[Perez_2019_AppleHeartStudy]], [[Shah_2025_LossOfPulse]], [[Bhamla_2017_Paperfuge]], [[Song_2024_SmartphoneMicroscope]], [[Jubran_1990_脉搏血氧仪种族偏差]], [[Obermeyer_2019_医疗算法种族偏见]], [[Luo_2026_NormWear]], [[Mason_2024_TemPredict]], [[Arakawa_2023_LemurDx]], [[Garg_2025_DopFone]], [[ECE175B_Lecture1a_课程导论与DGM概述]], [[ECE175B_Lecture1b_贝叶斯网络]], [[ECE175B_Lecture2_变分自编码器设计]], [[ECE175B_Lecture3_变分推断与ELBO]], [[ECE175B_Lecture4_生成对抗网络]], [[2026-04-20_多模态故事生成研究]], [[2026-04-27_AI任务面板自动化系统]], [[PHIL28_2026_课程大纲]], [[PHIL28_2026_期中考题清单]] |
| **debate** | [[争论_婴儿被动vs主动学习]], [[争论_新生儿模仿]] |
| **synthesis** | [[综合_医疗技术中的种族偏见]], [[AI 团队设计原则]] |

---

## 📂 目录结构

```
notes/                          ← 文献笔记（source 页面，镜像 raw/ 结构）
├── ucsd/Spring 2026/ECE175B/   (5 md + 2 pdf)
│   ├── ECE175B_Lecture1a_课程导论与DGM概述.md
│   ├── ECE175B_Lecture1b_贝叶斯网络.md
│   ├── ECE175B_Lecture2_变分自编码器设计.md
│   ├── ECE175B_Lecture3_变分推断与ELBO.md
│   ├── ECE175B_Lecture4_生成对抗网络.md
│   ├── Homework_1.pdf                           ← copied 2026-04-22 (不编译, 参考)
│   └── proposal.pdf                             ← copied 2026-04-22 (不编译, 参考)
├── ucsd/Spring 2026/ECE284/    (11 md + 1 pdf)
│   ├── Zhang_2015_TROIKA.md
│   ├── Perez_2019_AppleHeartStudy.md
│   ├── Shah_2025_LossOfPulse.md
│   ├── Bhamla_2017_Paperfuge.md                  ← ⚠️ 内容错位（实为 Apple Heart Study 演讲稿，待修复）
│   ├── Song_2024_SmartphoneMicroscope.md
│   ├── Jubran_1990_脉搏血氧仪种族偏差.md
│   ├── Obermeyer_2019_医疗算法种族偏见.md
│   ├── Luo_2026_NormWear.md
│   ├── Mason_2024_TemPredict.md
│   ├── Arakawa_2023_LemurDx.md                   ← new 2026-04-27
│   ├── Garg_2025_DopFone.md                      ← new 2026-04-27
│   └── proposal_javen_revised.pdf               ← copied 2026-04-22 (不编译, 用户自己的项目提案)
├── ucsd/Spring 2026/COGS117/   (17 md + 1 pdf)
│   ├── COGS117_2026_课程大纲.md
│   ├── Love_2026_监督与无监督学习.md
│   ├── Frank_2023_数据鸿沟.md
│   ├── Cusack_2024_婴儿无助期假说.md
│   ├── Zettersten_2025_婴儿主动学习.md
│   ├── Scott_2009_面孔知觉偏差起源.md
│   ├── Johnson_2024_婴儿感知.md
│   ├── Ayzenberg_2024_视觉物体识别发展.md
│   ├── Adolph_2018_走路发展15条建议.md          ← new 2026-04-22
│   ├── Oudeyer_2017_婴儿发展机器人.md           ← new 2026-04-22
│   ├── Zettersten_2026_计算模型与框架.md
│   ├── Zettersten_2026_Lecture1_课程导论与大问题.md
│   ├── Zettersten_2026_Lecture2_发展研究方法.md
│   ├── Zettersten_2026_Lecture4_发展理论.md
│   ├── Zettersten_2026_Lecture5_感知发展1.md
│   ├── Zettersten_2026_Lecture6_感知发展2.md    ← new 2026-04-22
│   ├── Zettersten_2026_Lecture7_走路与动作发展.md ← new 2026-04-22
│   └── cogs_117_sp26_exam_1_study_guide.pdf     ← copied 2026-04-22 (不编译, 考前参考)
└── web-research/   (2 files)
    ├── 2026-04-20_多模态故事生成研究.md
    └── 2026-04-27_AI任务面板自动化系统.md         ← new 2026-04-27

wiki/                           ← 知识网络（concept/debate/overview/synthesis）
├── 机器学习/
│   ├── 监督学习与无监督学习.md
│   ├── 自监督学习与基础模型.md
│   ├── ECE175B_概览.md
│   └── 统一多模态生成架构.md
├── 争论/
│   ├── 争论_婴儿被动vs主动学习.md
│   └── 争论_新生儿模仿.md                       ← new 2026-04-22
├── 认知科学/
│   ├── COGS117_概览.md
│   ├── 感知窄化.md
│   ├── 面孔知觉发展.md
│   ├── 核心知识理论.md
│   ├── 物体识别与形状感知.md
│   ├── 发展研究方法.md
│   ├── 动作发展.md                              ← new 2026-04-22
│   ├── 发展级联.md                              ← new 2026-04-22
│   └── 内在动机与好奇心驱动学习.md              ← new 2026-04-22
├── 综合/
│   └── 综合_医疗技术中的种族偏见.md
├── 哲学/                                          ← new 2026-04-27 (daemon)
│   └── PHIL28_概览.md
└── 工程方法/                                      ← new 2026-04-28
    ├── AI 团队设计原则.md                         ← Javen+Claude 共撰元方法论
    └── 超级个体_工具与杠杆.md                      ← new 2026-04-29 | QClaw 视频引发的工具/路由策略 synthesis

vault 内 system/ 下的元规则（不算 wiki 页面，但 Claude 启动时通过 MyBrain/CLAUDE.md 引用读到）：
- MyBrain/automation/docs/lessons.md   ← debug 方法论 6 条 + checklist (new 2026-04-28)
- MyBrain/automation/CLAUDE.md     ← 任务看板系统操作规则
- MyBrain/automation/docs/user-guide.md     ← 用户文档

attachments/
├── ECE175B/   (18 slides)
├── ECE284/    (figures for 11 sources, +13 new figs from LemurDx + DopFone)
└── COGS117/   (32 + 26 new = 58 figures: Adolph ×2, Oudeyer ×3, L6 ×10, L7 ×11)
```

---

## 🔍 快速导航：按概念

| 概念 | 相关页面 |
|------|----------|
| 监督学习 | [[监督学习与无监督学习]], [[Love_2026_监督与无监督学习]] |
| 自监督学习 | [[自监督学习与基础模型]], [[Cusack_2024_婴儿无助期假说]] |
| 基础模型 | [[自监督学习与基础模型]], [[Cusack_2024_婴儿无助期假说]] |
| 样本效率 | [[Frank_2023_数据鸿沟]] |
| 主动学习 | [[Zettersten_2025_婴儿主动学习]] |
| 统计学习 | [[监督学习与无监督学习]], [[Love_2026_监督与无监督学习]] |
| LLM | [[Frank_2023_数据鸿沟]], [[自监督学习与基础模型]], [[ECE175B_Lecture1b_贝叶斯网络]] |
| 神经发育 | [[Cusack_2024_婴儿无助期假说]], [[Zettersten_2025_婴儿主动学习]], [[Ayzenberg_2024_视觉物体识别发展]] |
| 贝叶斯推断 | [[Zettersten_2026_计算模型与框架]], [[ECE175B_Lecture1a_课程导论与DGM概述]], [[核心知识理论]] |
| 神经网络 | [[Zettersten_2026_计算模型与框架]], [[自监督学习与基础模型]] |
| Marr 层级 | [[Zettersten_2026_计算模型与框架]] |
| **感知窄化** | [[感知窄化]], [[Scott_2009_面孔知觉偏差起源]], [[Johnson_2024_婴儿感知]], [[Zettersten_2026_Lecture5_感知发展1]] |
| **面孔知觉** | [[面孔知觉发展]], [[Scott_2009_面孔知觉偏差起源]], [[Ayzenberg_2024_视觉物体识别发展]], [[Zettersten_2026_Lecture5_感知发展1]] |
| **物体识别** | [[物体识别与形状感知]], [[Ayzenberg_2024_视觉物体识别发展]], [[Zettersten_2026_Lecture5_感知发展1]] |
| **核心知识** | [[核心知识理论]], [[Zettersten_2026_Lecture1_课程导论与大问题]], [[Zettersten_2026_Lecture5_感知发展1]] |
| **视点不变性** | [[Ayzenberg_2024_视觉物体识别发展]], [[物体识别与形状感知]] |
| **骨架模型** | [[Ayzenberg_2024_视觉物体识别发展]], [[物体识别与形状感知]] |
| **腹侧通路** | [[Ayzenberg_2024_视觉物体识别发展]], [[面孔知觉发展]] |
| **违反预期范式** | [[发展研究方法]], [[Zettersten_2026_Lecture2_发展研究方法]], [[核心知识理论]] |
| **习惯化范式** | [[发展研究方法]], [[Zettersten_2026_Lecture2_发展研究方法]], [[Scott_2009_面孔知觉偏差起源]] |
| **fNIRS** | [[发展研究方法]], [[Zettersten_2026_Lecture2_发展研究方法]], [[Ayzenberg_2024_视觉物体识别发展]] |
| **预测编码** | [[Zettersten_2026_Lecture5_感知发展1]], [[争论_婴儿被动vs主动学习]] |
| **Piaget / Vygotsky / 动态系统** | [[Zettersten_2026_Lecture4_发展理论]], [[Oudeyer_2017_婴儿发展机器人]], [[Adolph_2018_走路发展15条建议]] |
| **Moravec 悖论** | [[Zettersten_2026_Lecture1_课程导论与大问题]] |
| **保护性不成熟** | [[Zettersten_2026_Lecture1_课程导论与大问题]], [[Cusack_2024_婴儿无助期假说]], [[Zettersten_2026_Lecture7_走路与动作发展]] |
| **动作发展 / 走路** | [[动作发展]], [[Adolph_2018_走路发展15条建议]], [[Zettersten_2026_Lecture7_走路与动作发展]], [[Oudeyer_2017_婴儿发展机器人]] |
| **里程碑（Motor Milestones）** | [[动作发展]], [[Zettersten_2026_Lecture7_走路与动作发展]], [[Adolph_2018_走路发展15条建议]] |
| **Stepping reflex / Thelen** | [[Zettersten_2026_Lecture7_走路与动作发展]], [[动作发展]] |
| **发展机器人** | [[Oudeyer_2017_婴儿发展机器人]], [[内在动机与好奇心驱动学习]] |
| **内在动机 / 好奇心** | [[内在动机与好奇心驱动学习]], [[Oudeyer_2017_婴儿发展机器人]] |
| **发展级联** | [[发展级联]], [[Adolph_2018_走路发展15条建议]], [[Zettersten_2026_Lecture7_走路与动作发展]] |
| **跨文化变异** | [[动作发展]], [[Adolph_2018_走路发展15条建议]], [[Zettersten_2026_Lecture7_走路与动作发展]] |
| **自然观察 / 头戴相机** | [[Zettersten_2026_Lecture6_感知发展2]], [[发展研究方法]], [[Adolph_2018_走路发展15条建议]] |
| **类别发展（全局-基本）** | [[Zettersten_2026_Lecture6_感知发展2]] |
| **标签与个体化** | [[Zettersten_2026_Lecture6_感知发展2]], [[Scott_2009_面孔知觉偏差起源]], [[面孔知觉发展]] |
| **新生儿模仿 / Meltzoff** | [[争论_新生儿模仿]], [[Zettersten_2026_Lecture7_走路与动作发展]] |
| **被动动态步行机** | [[Oudeyer_2017_婴儿发展机器人]], [[动作发展]] |
| PPG | [[Zhang_2015_TROIKA]], [[Perez_2019_AppleHeartStudy]], [[Shah_2025_LossOfPulse]], [[Luo_2026_NormWear]] |
| 运动伪影去除 | [[Zhang_2015_TROIKA]] |
| 房颤（AF）| [[Perez_2019_AppleHeartStudy]] |
| 可穿戴设备临床验证 | [[Perez_2019_AppleHeartStudy]], [[Shah_2025_LossOfPulse]] |
| 数字健康 | [[Perez_2019_AppleHeartStudy]], [[Shah_2025_LossOfPulse]], [[Mason_2024_TemPredict]] |
| 即时诊断（POC）| [[Bhamla_2017_Paperfuge]], [[Song_2024_SmartphoneMicroscope]] |
| 种族偏差（传感器层）| [[Jubran_1990_脉搏血氧仪种族偏差]] |
| 种族偏差（算法层）| [[Obermeyer_2019_医疗算法种族偏见]] |
| 算法公平性 | [[Obermeyer_2019_医疗算法种族偏见]], [[综合_医疗技术中的种族偏见]] |
| **可穿戴基础模型** | [[Luo_2026_NormWear]] |
| **多模态时间序列** | [[Luo_2026_NormWear]] |
| **Channel-Aware Attention** | [[Luo_2026_NormWear]] |
| **CWT（连续小波变换）** | [[Luo_2026_NormWear]] |
| **MAE 预训练** | [[Luo_2026_NormWear]] |
| **Oura Ring / 体温监测** | [[Mason_2024_TemPredict]] |
| **抑郁症生理标志** | [[Mason_2024_TemPredict]] |
| **昼夜节律** | [[Mason_2024_TemPredict]] |
| **儿童 ADHD / 多动症** | [[Arakawa_2023_LemurDx]] |
| **情境过滤（context filtering）** | [[Arakawa_2023_LemurDx]] |
| **Apple Watch 被动感知** | [[Arakawa_2023_LemurDx]], [[Perez_2019_AppleHeartStudy]] |
| **临床决策支持 / 可解释 ML** | [[Arakawa_2023_LemurDx]] |
| **胎心率（FHR）监测** | [[Garg_2025_DopFone]] |
| **多普勒声学（智能手机）** | [[Garg_2025_DopFone]] |
| **18 kHz 主动声学传感** | [[Garg_2025_DopFone]] |
| **AdaBoost 回归** | [[Garg_2025_DopFone]] |
| **低资源医疗 / 即时诊断 POC** | [[Bhamla_2017_Paperfuge]], [[Song_2024_SmartphoneMicroscope]], [[Garg_2025_DopFone]] |
| 深度生成模型（DGM）| [[ECE175B_概览]], [[ECE175B_Lecture1a_课程导论与DGM概述]] |
| Bayesian Network | [[ECE175B_Lecture1a_课程导论与DGM概述]], [[ECE175B_Lecture1b_贝叶斯网络]] |
| VAE | [[ECE175B_Lecture2_变分自编码器设计]], [[ECE175B_Lecture3_变分推断与ELBO]] |
| ELBO | [[ECE175B_Lecture3_变分推断与ELBO]], [[统一多模态生成架构]] |
| GAN | [[ECE175B_Lecture4_生成对抗网络]] |
| Transformer | [[ECE175B_Lecture1b_贝叶斯网络]], [[Luo_2026_NormWear]], [[统一多模态生成架构]] |
| **统一多模态生成** | [[统一多模态生成架构]], [[2026-04-20_多模态故事生成研究]] |
| **Transfusion / Chameleon** | [[统一多模态生成架构]], [[2026-04-20_多模态故事生成研究]] |
| **GPT-4o（推断架构）** | [[统一多模态生成架构]], [[2026-04-20_多模态故事生成研究]] |
| **扩散模型** | [[统一多模态生成架构]], [[2026-04-20_多模态故事生成研究]] |
| **自回归生成模型** | [[ECE175B_Lecture1b_贝叶斯网络]], [[统一多模态生成架构]] |

---

## ⚠️ 跨页面矛盾汇总

| 矛盾点 | Cusack et al. (2024) | Zettersten et al. (2025) |
|--------|-------|-------|
| **婴儿学习的主被动性** | 早期表征与行为脱耦，被动自监督 | 从出生即主动、目标导向，行动与表征共演 |
| **无助期缩短的后果** | 较短预训练期→下游表征代价高 | 实证相反：早走路→早出现语言 |
| **社会 vs 非社会信息** | 两者同等重要 | 社会生态互动是核心驱动 |
| **AI类比的有效性** | 有效：婴儿≈自监督预训练的网络 | 不完整：网络无目标/生态情境 |

**扩展**（2026-04-17 编译感知发展文献后）：
- Scott 2009 的个体标签效应 → 支持主动派
- Ayzenberg 2024 的形状/骨架先验 → 支持先天论 / 挑战白板自监督观
- Emberson 2015 的 fNIRS 预测响应 → 两派均可引用

**进一步扩展**（2026-04-22 编译动作发展文献后）：
- Adolph 2018 建议 9（发展结果≠实时动机）+ 走路→语言级联 → 支持主动派
- Oudeyer 2017 Playground 实验 + 好奇心形式化 → 提出"动态系统"作为第三条路
- Thelen 1984 stepping reflex → 支持 Cusack 的"身体不成熟"但给出非"预训练"解释

详见：[[争论_婴儿被动vs主动学习]]

### 新生儿模仿三方辩论（2026-04-22 新增）

| 阵营 | 主张 | 核心证据 |
|------|------|---------|
| **Meltzoff & Moore 1977** | 新生儿选择性模仿面部动作 | N=6 原实验吐舌匹配 |
| **Jones 1996–2006** | 吐舌是一般性探索/兴奋反应，非模仿 | 吐舌对多种非社交刺激出现 |
| **Oostenbroek 2016** | 大样本没能复现选择性模仿 | N=106 纵向无效 |

详见：[[争论_新生儿模仿]]

---

## 📊 统计

| 指标 | 值 |
|------|------|
| 总页面数 | 56 |
| overview | 3 |
| concept | 11 |
| source | 38 |
| debate | 2 |
| synthesis | 2 |
| confidence: high | 45 |
| confidence: medium | 11 |

**本轮增长（2026-04-27）**：+2 source（[[Arakawa_2023_LemurDx]] + [[Garg_2025_DopFone]]，notes/ucsd/Spring 2026/ECE284/）；7 个相关 ECE284 source 加双向回链；渲染 13 张关键图到 attachments/ECE284/；新增 10 条推测性问题至 gaps.md。**concept 提取候选**：消费级智能手机/可穿戴健康感知主题已积累 7 个独立来源，建议建 `wiki/医疗技术/` 子目录（待 Javen 拍板）。**lint 待办**：发现 `notes/ECE284/Bhamla_2017_Paperfuge.md` 内容错位，真正 Paperfuge 笔记错位在 raw/

**前次增长（2026-04-28）**：+1 synthesis（[[AI 团队设计原则]]，wiki/工程方法/）；新增子领域 `wiki/工程方法/`；并补录 daemon 凌晨自动跑产出（+2 source PHIL28 syllabus/midterm + 1 overview PHIL28_概览，wiki/哲学/）

**前前次增长（2026-04-27）**：+1 source（[[2026-04-27_AI任务面板自动化系统]]，web-research 类）

**前前次（2026-04-22）**：+4 source（Adolph 2018, Oudeyer 2017, Lecture 6, Lecture 7）、+3 concept（动作发展, 发展级联, 内在动机与好奇心驱动学习）、+1 debate（争论_新生儿模仿）
