---
title: LLM 医疗评测
type: concept
tags: [LLM, 医疗AI, 评测, benchmark]
created: 2026-05-11
updated: 2026-05-11
confidence: high
priority: active
---

# LLM 医疗领域评测

> 评估大语言模型在医疗场景下表现的方法学。**核心张力**：高 MedQA 准确率 ≠ 临床可信度。两条互补范式——**能力评测**（模型能不能答对医考题）vs **诚实度评测**（模型敢不敢在不确定时拒答）。

---

## 为什么需要"医疗专用"评测

通用 NLP benchmark（MMLU、HellaSwag、TruthfulQA 等）不足以评估医疗 LLM，因为：

1. **错的代价不对称**：医疗错一句话能致命，通用领域错答可以接受
2. **医学知识有结构**：诊断、治疗规划、药物互动有专业逻辑，不是常识推理
3. **多国差异**：USMLE / AIIMS / 中国执业医师考 知识体系和题型有差异
4. **对抗性场景**：临床上模型经常遇到"症状模糊"、"罕见病"、"病人带先入印象问"——必须能应对

---

## 两条主要评测范式

### 范式 A：能力评测（Capability Benchmark）

**问题**："这个 LLM 能不能在医考题上达到人类水平？"

**典型 benchmark**：MedQA (USMLE)、MedMCQA、PubMedQA、MMLU-Medicine、HealthSearchQA

**评估指标**：accuracy（答对比例）

**代表论文**：[[Singhal_2025_MedPaLM2_演讲|Med-PaLM 2 (Singhal et al. 2025)]] — 在 MedQA 上达 86.5%，超过 USMLE 及格线和大部分人类医生水平。**目标是证明 LLM 已经有医生级知识**。

**局限**：高准确率 ≠ 临床可部署。Med-PaLM 2 在 MCQ 上的表现没解决：
- 模型在不确定时还是会硬答（hallucination）
- Prompt 敏感性问题
- 自由问答场景未覆盖

### 范式 B：诚实度评测（Honesty / Hallucination Benchmark）

**问题**："这个 LLM 敢不敢在不该答时拒答？"

**典型 benchmark**：[[Pal_2023_MedHALT|Med-HALT (Pal et al. 2023)]]、HaluEval、TruthfulQA-Medical

**评估指标**：对抗性 task 上的拒答率 / Pointwise Score（答对 +1，答错 −0.25，弃权 0）

**核心机制**：**故意问错 / 故意问假**——把"建议错答案"塞进 prompt（FCT）、删掉真选项（NOTA）、问完全荒诞的题（FQT）、用假 PMID 测引用幻觉（MHT）。**模型必须识别坑而非硬答**。

**关键发现**：
- 没有 LLM 在医疗 hallucination 上是"安全"的
- **Instruction-tuning Paradox**：chat / RLHF 模型反而比 base 模型在幻觉控制上**退化**（LLaMA-2 70B Base 72.33% → Chat 11.26%，差 61pp）
- 闭源模型不一定比开源强（GPT-3.5 44.48% < LLaMA-2 70B Base 72.33%）

---

## 两条范式互补，不是替代

|| 能力评测 | 诚实度评测 |
|---|---|---|
| 测什么 | 模型知不知道答案 | 模型敢不敢承认不知道 |
| 失效模式 | "不会答" | "胡乱答" |
| 典型分数 | accuracy 越高越好 | Pointwise Score（含 abstention reward）越高越好 |
| Med-PaLM 2 | 86.5% (强) | 未测 |
| LLaMA-2 70B Base | 弱 | 72.33% (强) |
| LLaMA-2 70B Chat | 中 | 11.26% (崩) |

**临床部署需要两条都过**：
- 只过能力评测 → 模型"很会答"但不知道何时该闭嘴 → 危险
- 只过诚实度评测 → 模型很谨慎但医学知识不足 → 没用

**目前 SOTA 问题**：还没有论文同时报告同一模型在两类 benchmark 上的成绩——Med-PaLM 2 没测 Med-HALT，Med-HALT 没测 Med-PaLM 2。这是一个明显的研究 gap。

---

## 评测设计的几个关键决策

### 1. 多国 vs 单国

- 单国（如只用 USMLE）：训练数据可能严重偏 US，benchmark 结果不能泛化
- 多国（Med-HALT 用 5 国医考）：测试模型的**地理鲁棒性**

### 2. MCQ vs 自由问答

- MCQ：易自动评分，但简化了真实临床决策
- 自由问答：贴近真实但需人工评估或 LLM-as-judge

### 3. Scoring 是否惩罚乱猜

- **传统 accuracy**：答错 = 弃权 = 0 分。**鼓励瞎猜**（猜中 25%，弃权 0%）
- **Pointwise Score（Med-HALT）**：答错 −0.25，弃权 0。**奖励诚实**

### 4. 是否设计对抗性 task

- 直接问 → 测知识量
- 故意挖坑（FCT/NOTA/FQT）→ 测"承认无知"能力

---

## 主要 benchmark 速查

| Benchmark | 类型 | 数据来源 | 评估目标 | 备注 |
|---|---|---|---|---|
| MedQA | 能力 | USMLE Step 1-3 | 医考准确率 | Med-PaLM 2 86.5% |
| MedMCQA | 能力 | AIIMS PG + NEET PG (印度) | 医考准确率 | Pal 2022 自家 dataset |
| PubMedQA | 能力 | PubMed 生物医学 QA | 文献理解 | 二元 / 三元分类 |
| HealthSearchQA | 能力 | 模拟消费者医学问答 | 消费场景 | Med-PaLM 2 用 |
| **Med-HALT** | **诚实度** | 5 国医考 + PubMed | 对抗性鲁棒性 | RHT + MHT 7 个 task |
| HaluEval | 诚实度 | 通用领域 | 幻觉检测 | 非医疗专用 |

---

## ⚠️ 矛盾与未解决问题

- **同一模型在两类 benchmark 上的成绩还没人系统报告**：Med-PaLM 2 没测 Med-HALT，Med-HALT 没测 Med-PaLM 2 这种"产品级"模型。需要 cross-benchmark 评估
- **Instruction-tuning 的影响机制不明**：[[Pal_2023_MedHALT]] 揭示 RLHF 后幻觉控制变差，但因果未拆解（训练目标？数据分布？）
- **自由问答评估的金标准缺失**：所有现有 benchmark 都是 MCQ，临床真实场景是自由问答

## 🔗 关联

- [[Pal_2023_MedHALT]] — Med-HALT 的源论文（**诚实度评测**代表）
- [[Singhal_2025_MedPaLM2_演讲]] — Med-PaLM 2（**能力评测**代表）
- [[Obermeyer_2019_医疗算法种族偏见]] — 同样讲"表面指标过关 ≠ 部署安全"
- [[消费级设备健康感知]] — 硬件 / 信号层的医疗 AI 评测视角

## 📎 主要来源

- Pal et al. 2023 (EMNLP) — Med-HALT
- Singhal et al. 2025 (Nature Medicine) — Med-PaLM 2
- Jin et al. 2020 — MedQA / USMLE 题库
- Pal et al. 2022 (CHIL) — MedMCQA
