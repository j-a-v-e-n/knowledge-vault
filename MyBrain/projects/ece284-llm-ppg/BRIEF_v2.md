# BRIEF v2 — 真人版

> 5 分钟版。不写 Phase / PDCA / reviewer。Javen 自己的脑子在哪里。
> 标 ✅ = verified；⚠️ = 我（或 AI）其实没想清楚。

---

## 1. 目标

我要在 ~6/5 前交 final report + 做 oral defense，主题是对比 TROIKA / RF / LLM 在 IEEE SPC 2015 PPG HR estimation 上的表现。

- ✅ "要交 final report + oral" — verified by syllabus (44% grade = 15% report + 15% oral)
- ⚠️ "~6/5" — README 推断的，**syllabus 实际 deadline 不确定**
- ✅ "对比 TROIKA / RF / LLM" — proposal 4/22 已 commit
- ⚠️ ReAct 是 stretch — 不跑就要在 report 里 honest 说为啥不跑

---

## 2. 当前进度

- ✅ TROIKA-lite LOSO done — MAE **23.46** BPM
- ✅ RF LOSO done — MAE **10.53** BPM
- ✅ Sonnet LLM LOSO done — MAE **22.63** BPM
- ✅ 1768 windows / 12 subjects 全跑 / 0% NaN
- ✅ 数据已齐（`results/*.json` 12+2 个文件）
- ✅ Week 8 update report 5/11 已交（不用再动）
- ❌ Final report 还没开始
- ❌ Oral slides 还没开始
- ❌ 4-system 对比 plot 还没出（只有 baselines 2-system plot + Subj1 pilot plot）

---

## 3. 接下来要做什么

按时间顺序，剩 3 件事：

### a. Evaluator + plot

- 4-system MAE 表（含 motion-level stratification 如果做）
- Per-subject heatmap 或 bar chart
- ✅ 数据 in hand
- ⚠️ "motion-level stratification" 是 proposal 写的，但**我不确定 IEEE SPC 2015 标注 motion level 怎么用** — 之前 reviewer 提过但没真做

### b. 写 final report

- ACM 2-column, 7-10 pages（旧 brief 写的，没 verify syllabus）
- 主线: paradigm comparison → 4 system 数字 → **negative finding**（LLM ≈ TROIKA, 比 RF 差 2.15×）→ 讨论 why
- ⚠️ **我能解释为啥 LLM 比 RF 差吗** — 这是 oral 最关键问题，**现在我不确定我自己懂**
  - Reviewer 给的 framing "interpretability vs performance" 是 packaging，不是 mechanism
  - 真正 mechanism candidates: (1) RF 学到了 implicit motion compensation 在 4 个 spectral feature 里 (2) LLM 没看到 raw signal 只看 narrative description 丢了关键信息 (3) λ 参数 search space 太窄
  - **我没真深入想过哪条 candidate 是 root cause**

### c. 准备 oral

- 15-min slides + Q&A 备稿
- ⚠️ Oral format 实际不确定（length / Q&A 比例 / slides 要求 / 必须 in-person 吗）

---

## 4. 成功标准

- ✅ 一份完整 report（ACM 2-col, 7-10 页 — 待 verify）
- ✅ 图表对比 4 system
- ✅ 所有数字 verbatim 跟 `results/*.json` 一致（zero mismatch）
- ⚠️ **能解释为什么 LLM 比 RF 差** — 见 3.b 第二个 ⚠️。这条是 oral 最大风险。**我现在 honest 答不上来 mechanism level**

---

## 5. 卡点

- ⚠️ Final report exact deadline 不确定（README 写 ~6/5；syllabus 没明示）
- ⚠️ Oral format 不确定（length / 形式 / 评分 rubric）
- ⚠️ Report 页数限制不确定（默认 ACM 2-col 7-10，但没 verify syllabus）
- ⚠️ **我对 LLM 比 RF 差的 mechanism 解释没想清楚**（成功标准里最高 stakes 那条）
- ✅ Budget 不卡（用了 $5.30，剩 $15）
- ✅ Code 不卡（数据 + 12 subject JSON 都 in hand）

---

## ⚠️ 我自己 honest 的 unverified 假设

1. "syllabus deadline ~6/5" — 没 verify
2. "ACM 2-col 7-10 页" — 没 verify
3. "我懂 LLM 比 RF 差的原因" — 我没真深入想
4. "Oral 15-min slides 标准" — 没 verify
5. "motion-level stratification 怎么算" — proposal 写了我没真做

5 条里 4 条是"我应该 verify 但 deferred"，1 条是"我应该想但没想"。

后者 (#3) 是最 dangerous — 因为 verify 那些 (#1 #2 #4 #5) 是 mechanical 任务我可以做，但 #3 是**自己真懂这个 project 的 finding 意味着什么** —— 这件事不能 outsource。

---

*v2 created 2026-05-19 by main session per Javen 外部 review feedback: "BRIEF 应是 5 分钟说明书不是系统运行日志"。旧 PROJECT_BRIEF.md 不删，作为系统/流程 reference 留着。*
