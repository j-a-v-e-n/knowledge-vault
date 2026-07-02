---
title: "Learning From Others: The Consequences of Psychological Reasoning for Human Learning"
type: source
tags: [COGS117, 社会学习, 贝叶斯模型, 教学性inference, natural-pedagogy, 心理推理]
sources:
  - raw/ucsd/Spring 2026/COGS117/Shafto et al. (2012).pdf
authors: Patrick Shafto, Noah D. Goodman, Michael C. Frank
journal: Perspectives on Psychological Science 7(4), 341–351
doi: 10.1177/1745691612448481
year: 2012
week: Week 7
created: 2026-05-14
updated: 2026-05-14
confidence: high
priority: active
---

# Shafto, Goodman & Frank (2012) — 从他人学习：心理推理对人类学习的影响

> 学习者不只看 data 是什么，还看 **谁** 选的、**为什么** 选的——goal-directed action 和 communicative action 让学习者从极有限的 data 做出强 inference，而 random sampling 做不到。

---

## 这项研究在解决什么问题？

**为什么人类能从如此少的 data 学得这么快？**

传统 formal learning models（Gold 1967 起）假设 data 是"randomly collected facts about the world"——这种假设下：
- Gold (1967) 证明：human languages **不可学**（足够 broad 的 formal language 不能从 finite examples 推断出来）
- Wolpert & Macready (1997) No Free Lunch — 没有 prior 时学不动
- 跟 human intuition 完全对不上：儿童被誉为"小科学家"，但即使是 perfect scientist 用实验也学不到人类一生掌握的所有知识

**Gap**：data 在人类学习中**不是随机收集的**——data 经常 *由某人 / 为某目的* 提供的：
- 制陶人示范如何捏陶
- 父母示范如何系鞋带
- 老师示范数学概念

这些 data 是 **goal-directed**：作者选择 data 是想让 observer 学到特定东西。但传统模型把 data 当 inert observations，**无法 explain 这种 social context 如何 fundamentally 改变 learning**。

## 核心论点（一句话）

**Bayesian formal framework：把 actor 的 actions、goals、knowledge 显式纳入 learner 的 posterior inference**——同一份 evidence，在 (a) random / (b) goal-directed / (c) communicative context 下导致 **qualitatively 不同** 的 inferences。

---

## 框架：三种 social learning context

paper Fig 1 区分（verbatim labels）：

| Context | Actor | Goal | Effect |
|---|---|---|---|
| (a) **Physical evidence** | Not Knowledgeable | Unknown / no goal | Unintentional |
| (b) **Goal-directed action** | Knowledgeable | Non-social Goal | Intentional |
| (c) **Communicative action** | Knowledgeable | **Social Goal**（teach learner） | Intentional |

**贝叶斯形式化**：

$$P(h \mid a, e, g) = \frac{P(e \mid a, h) \cdot P(a \mid g, h) \cdot P(h)}{\sum_{h'} P(e \mid a, h') \cdot P(a \mid g, h') \cdot P(h')}$$

四个量：
- $h$ — 关于 world 的 hypothesis
- $a$ — actor 的 action
- $e$ — observed effect
- $g$ — actor 的 goal
- $P(a \mid g, h)$ **关键 psychological term** — encode 关于 actor knowledge + goal 的 belief

不同 context 对 $P(a \mid g, h)$ 的假设不同 → 不同 posterior。

**Communicative case 的额外 twist**：teacher 选 action 时也 reason about learner 的 inferences → recursive：

$$P(a \mid g, h) = \frac{P(g \mid a, h)}{\sum_{a'} P(g \mid a', h)}$$

（Luce's choice axiom；Eq. 3 in paper）

---

## 两个核心 demonstration（Fig 2）

### Scenario 1: Bob's Box（推因果）

**Setup**：box 上有 2 个 button。Bob 同时按下 A + B → 灯亮了。Learner 推断：哪个 button cause 灯？

**4 个 hypothesis**：A alone / B alone / A&B both / Neither。Prior 全等于 0.25。

**Posterior（paper 算出来的）**：

| Hypothesis | Physical evidence | Goal-directed | Communicative |
|---|---|---|---|
| Neither | 0 | 0 | 0 |
| A alone | 0.33 | 0.25 | ≈ 0.17 |
| B alone | 0.33 | 0.25 | ≈ 0.17 |
| **A&B both** | 0.33 | **0.50** | **≈ 0.67** |

**机制**：
- **Physical evidence**：Bob 按啥是随机的 → 三个 viable hypothesis 等概率
- **Goal-directed**：Bob 知道 box 怎么工作，他选按 both → 如果只是 A 或 B 单独 cause，他没必要按 both → A&B both 概率提升
- **Communicative**：Bob 是 teach，他按 A&B 而不是只按 A，是因为想让 learner 推断"both 都 necessary"。如果只 A cause，他会只按 A 避免混淆 learner → A&B 概率最高

### Scenario 2: Tim's Toy（推 latent cause 数量）

**Setup**：Tim 拉 knob 一次 → 听到 squeak。Learner 推断：toy 一共有几个 cause-effect pair？

**3 hypothesis**：0 / 1 / 2 pairs。

**Posterior**：

| Hypothesis | Physical evidence | Goal-directed | Communicative |
|---|---|---|---|
| 0 pairs | 0 | 0 | 0 |
| 1 pair | ≈ 0.5 | ≈ 0.5 | **≈ 1.0** |
| 2 pairs | ≈ 0.5 | ≈ 0.5 | ≈ 0 |

**机制**：
- Physical / Goal-directed：observation 排除 0 pairs，但 1 vs 2 还不确定
- **Communicative**：Tim 是 teach，如果有 2 pairs，他会 demonstrate 两个。他只示范 1 个 → strong inference "toy 只有 1 个 cause-effect pair"

这是 **pedagogical sampling 的 narrowing effect**：teacher's restraint 本身就是 information。

---

## Empirical evidence supporting framework

paper 引的 3 个关键实证：

| Study | Finding | Framework 预测 |
|---|---|---|
| **Goodman et al. (2009)** — adults Bob's Box | Goal-directed condition 推 "A&B both"；physical evidence condition 不确定 cause | ✓ |
| **Bonawitz et al. (2011)** — children Tim's Toy | Communicative condition 下儿童**少 explore** + 少 discover 其他 causal relations | ✓ "narrower inference" |
| **Xu & Tenenbaum (2007)** — word learning | Teacher 选 examples → learners 保守 generalize；naïve learner 选 examples → broadly generalize | ✓ |

**更广 implications**：

- **Over-imitation** (Lyons, Young & Keil 2007；Horner & Whiten 2005)：儿童 imitate 显然 superfluous 的 action — 因为 they assume teacher's action 是 informative。 paper 把这从"奇怪 anomaly"reframe 成"rational inference under pedagogical assumption"
- **McNeill (2008) math equality**：教 `X + Y = Z` 格式（非 diverse）导致儿童错误推断 `=` 是 "compute" 而非 "equality" — 因为儿童假设 teacher 选 examples 代表了 concept 的全貌
- **Csibra & Gergely (2009) Natural Pedagogy**：ostensive cues（叫名字、child-directed speech、shifting gaze）→ child 推断 "demonstrated data 是 purposefully sampled，支持 broad generalization"
- **Frank & Goodman (in press)**：communicative model 捕捉 Gricean maxim "be informative"
- **Shafto et al. (2012, separate work)**：epistemic trust 发展 — 4 岁儿童 best explained by **joint inference about informants' knowledge + intent**，而非 knowledge 一项（3 岁儿童只看 knowledge）

---

## 跟其他 framework 的关系

paper Appendix A 显式 derive：

如果假设 $P(e \mid a, h) = P(e \mid h)$（evidence 独立于 actor），就 recover 标准 Bayesian learning：
$$P(h \mid e, g) = \frac{P(e \mid h) P(h)}{\sum_{h'} P(e \mid h') P(h')}$$

如果假设 $P(a \mid g, h) \propto 1$（actions uniformly random），recover Bayesian causal learning（Anderson 1991; Gopnik et al. 2004）。

→ **传统 Bayesian models 是这个 framework 的 special case**（actor 假设 random or no-role 时）。

---

## paper 自己承认的局限

1. **Deterministic causality assumption**：paper §"Implications of Goal-Directed Actions for Learning"明确 disclaim："These assumptions are not meant to represent people's beliefs about these particular causal-learning problems; rather, these assumptions allow for pedagogical and computational simplicity"
2. **Goal taxonomy 未完成**：paper §"Summary"："we do not yet have definitive lists of the kinds of goals that are relevant. Considerable work remains in identifying, cataloging, and organizing the myriad goals that people may have"
3. **假设 actor 是 knowledgeable**：但 paper 引自己 (Shafto et al. 2012 separate) work formalize naïve vs knowledgeable informants 的 case
4. **Simple causal scenarios for exposition**："framework naturally applies to noncausal learning domains and to situations of considerably greater complexity"（concept learning / language learning / preference learning 都已在 follow-up work 应用）
5. **没解决 deceptive actor 情况**："a person may be interested in deceiving or lying instead of teaching or (cooperatively) communicating. These kinds of goals can be straightforwardly formalized within this framework... However, we do not yet have definitive lists"

---

## ⚠️ 矛盾与未解决问题

- **跟 Saffran 1996 statistical learning 的 framing 矛盾**：Saffran 假设婴儿 track transitional probabilities **agnostic to actor**——纯统计 over evidence stream。Shafto framework 说 inferences 应 condition on actor — 婴儿听 mother 说 vs 听 TV 说，data 完全一样但 inference 应不同。
  - 这是 **被动统计 vs 主动社会学习** 在 framework level 的张力（不只是 empirical level）
  - 现实可能：两个 system 共存，task / age 决定 weight。Shafto framework 也 explicitly 把 statistical learning model 作为 special case 涵盖（actions 假设 random 时）

- **跟 Csibra & Gergely 2009 Natural Pedagogy 重叠 vs 区别**：
  - NP 是 **理论/现象级** claim（婴儿有 inherent disposition 把 ostensive 信号当 pedagogical 信号）
  - Shafto 2012 是 **Bayesian formal model**——可以 derive NP-like behavior 但不需要假设 dedicated cognitive module
  - 二者 mutually compatible，paper 引 NP 作为 framework 的支持证据之一

---

## 🔗 关联

### Week 7 主题
- [[Vong_2024_单童语言习得]] — Week 5：CVCL 单孩学词，依赖 caregiver child-directed speech = communicative context，符合 Shafto framework
- [[Saffran_1996_统计学习]] — Week 5：纯统计学习 framework，Shafto framework 的 evidence-only special case

### 概念
- [[内在动机与好奇心驱动学习]] — Bonawitz 2011 "communicative context 减少探索" 跟好奇心 / 探索 driver 直接对接
- [[统计学习]] — 形成对比：transitional probability 仅 evidence-based vs Shafto 加入 actor reasoning
- [[争论_婴儿被动vs主动学习]] — 主动学习的一个重要 dimension 是"对 actor 的 social reasoning"

### Cross-paper
- [[Liu_2017_婴儿成本推理]] — Week 6：婴儿用 action 推 goal value —— Shafto 是 reverse direction（用 goal 推 belief）
- [[Stojnic_2023_常识心理BIB]] — 评测 agent reasoning 的 benchmark，可用 Shafto framework 评估 model 表现

### 计算建模
- [[Zettersten_2026_计算模型与框架]] — Week 2：Bayesian inference 课堂介绍；Shafto 是 social learning context 的 Bayesian application
- Notebook 2 — 贝叶斯模型基础（5/19 due），Shafto 可作 framework reference

---

## 📎 来源

- `raw/ucsd/Spring 2026/COGS117/Shafto et al. (2012).pdf`
- Perspectives on Psychological Science 7(4), 341–351
- DOI: 10.1177/1745691612448481
