---
title: ECE 284 LLM-PPG Final Project — Project Brief
type: overview
tags: [ECE284, project-brief, LLM-PPG, final-project, Spring2026]
created: 2026-05-19
updated: 2026-05-19
confidence: high
priority: active
sources:
  - projects/ece284-llm-ppg/README.md
  - projects/ece284-llm-ppg/LOSO_RESULTS_2026-05-15.md
  - notes/ucsd/Spring 2026/ECE284/syllabus.md
  - raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf
  - wiki/工程方法/项目默认模板_所有项目必备
related:
  - task-board task-018
  - MyBrain/raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf
  - "[[Zhang_2015_TROIKA]]"
  - "[[Arakawa_2023_LemurDx]]"
  - "[[Garg_2025_DopFone]]"
---

# ECE 284 Final Project — Benchmarking LLM Paradigms for Wearable PPG HR Estimation

> **Course**: ECE 284 Spring 2026 — Digital Health Technologies (Edward Wang + Colin Barry)
> **Student**: Javen Cao (solo)
> **Grade weight**: 44% final project; **remaining 30%** = 15% final report + 15% oral assessment
> **Target deadline**: Final report ~2026-06-05 (Week 10); Oral at finals — ⚠️ verify in syllabus
> **Format constraint**: ACM Large 2-column, 7-10 pages
>
> **Replaces** prior PROJECT_BRIEF 2026-05-18 version (stale — claimed API blocker that was resolved 5/15 night with LOSO completion).

---

## ⚠️ Missing Components (after first draft)

待 reviewer audit pending (Phase A.6 mandatory) — 跑完 reviewer 补全。

---

## Phase A: Design / Spec

### A.1 Problem Statement

**What**: 对比 4 个 PPG-based heart rate (HR) estimation 范式在剧烈运动伪迹下的表现。

**Why**: 消费级 wearable (Apple Watch / Fitbit / Oura) 在运动 motion artifact 下 PPG HR MAE 飙升（Zhang 2015 TROIKA 报 2.34 BPM at rest）；**LLM 是否能作 parameter generator** 替代经典 signal processing 是 open question — 2024-2025 业内多个 LLM-as-signal-processor 工作尚未在 wearable health 评测。

**For whom**: ECE 284 grading committee + Javen 自己 BS/MS SoP reference + portfolio。

### A.2 Acceptance Criteria (Definition of Done)

1. ✅ Final report submitted by ~6/5：ACM Large 2-column 7-10 pages，含 4-system comparison + per-motion-level analysis + λ-appropriateness analysis + cost analysis
2. ✅ 4-system comparison plots（bar / per-subject heatmap）
3. ✅ Reproducible code in `projects/ece284-llm-ppg/` (git versioned + GitHub repo link in report)
4. ✅ Oral defense 备稿：15-min slide deck + Q&A 备答
5. ✅ Honest framing of **negative result** (Sonnet ≈ TROIKA, 2.15× worse than RF) — no overclaim
6. ✅ Report 中所有数字 100% verbatim from raw experiment JSONs (lesson ⑭ 真实性零容忍)

### A.3 Alternatives Considered

| Alt | 选 / 不选 | Rationale |
|---|---|---|
| **A. 沿 proposal 4-system comparison + negative result framing** | ✅ **CHOSEN** | LOSO data 已收齐；reviewer 5/15 audit 确认 scientifically valid negative result；honest framing 不违反 truthfulness rule；不要新 spending |
| B. 跑 ReAct stretch goal | ❌ | Proposal 标 stretch；额外 cost + 不改变核心 negative finding；reviewer 5/15 建议 round 2 not now |
| C. Pivot to ablation (prompt / λ grid / temperature) 救 Sonnet | ❌ | $5-15 + 3+ days；reviewer 5/15 "experimental design strong"；pivoting 是 cherry-picking risk |
| D. 用 pilot Subj1 30w (MAE 7.90) 写报告标 "in progress" | ❌ | Pilot 7.71 误导 (full 28.44 same subj); 不诚实 framing |
| E. Haiku 4.5 ablation | ❌ | system prompt < 4096 tokens 无法 cache → Haiku 反而贵；ROI 低 |

**Decision rationale (multi-source verified)**: Path A is best per (1) reviewer agent 5/15 result integrity audit (2) [[AI 团队设计原则]] Sakana-style single-thread paper writing pattern (3) Cognition + Anthropic best practice on negative-result honesty。

### A.4 Risk Register (Marty Cagan 4 risks)

| 风险类型 | 风险 | Severity | Mitigation |
|---|---|---|---|
| **Value** | Negative result 被 grader 读成"项目失败"打低分 | 🟡 Medium | Framing 强调 paradigm comparison 科学价值；Sakana paper writing 范式（写 negative paper 同样 publishable）；reviewer 5/15 给的 framing "interpretability vs performance trade-off" |
| **Usability** | Final report wording / 数字 mismatch | 🟡 Medium | PDCA L1+L2+L3 mandatory; reviewer 在 submit 前 |
| **Usability** | Oral defense 被问 weakness 答不上 | 🟡 Medium | Q&A 预测题 cheat sheet；模拟 hostile questioning ("为啥 LLM 比 RF 差"，"prompt engineering 调过 vs 没") |
| **Feasibility** | Code crash mid-final / data lost | 🟢 Low | 12 per-subject JSON + git + Google Drive 三重备份 |
| **Feasibility** | LaTeX compile 错误临 submit | 🟢 Low | `update_report.tex` 已 base；早 compile；Overleaf fallback |
| **Cost** | API 额外消费失控 | 🟢 Low | 已花 $5.30；剩 budget $15；report 阶段不应再 API |
| **Business viability** | Final project 44% grade weight；fail → 影响 GPA → 影响 BS/MS Fall 2027 admit timeline + portfolio quality for industry job | 🟡 Medium | 严格按 milestone 执行；reviewer audit + Javen review 双层 gate；不靠 luck；oral defense rehearsal 至少 1 次 mock |

### A.5 Decision Record

| Date | Decision | Rationale | 决策者 |
|---|---|---|---|
| 2026-04-22 | Submit proposal 4-system comparison + ReAct stretch | proposal 通过 | Javen + Prof |
| 2026-05-05 | TROIKA-lite LOSO MAE 23.46 finalized | `results/troika_loso.json` | Tab B daemon |
| 2026-05-05 | RF LOSO MAE 10.53 (-55.1% vs TROIKA) | `results/rf_loso.json` | Tab B daemon |
| 2026-05-10 | Sonnet pilot Subj1 30w MAE 7.90 (later corrected to 7.71) | `results/llm_lambda_pilot_s1_sonnet.json` | Tab B |
| 2026-05-11 | Project update report submitted (Week 8) | `update_report.tex` | Javen |
| 2026-05-15 00:28 | Full 12-subj Sonnet LOSO launched (per-subject crash recovery + caffeinate) | Javen approve Path A; lesson ⑫ heartbeat | Javen + main |
| 2026-05-15 01:04 | LOSO done (35min, MAE 22.63, 0% NaN) | `loso_sonnet_DONE` flag | Auto |
| 2026-05-15 | Reviewer #1 (launcher) + #2 (result integrity) audit — 0 critical, 4 medium each | 反 single-agent rule | 2 reviewer subagents |
| 2026-05-18 | Sakana-style 6-stage pipeline + reviewer checkpoint design approved | Anthropic + Cognition + Sakana + vault 综合 verified | Javen + WebFetch |
| 2026-05-19 | **THIS BRIEF created** (replaces 5/18 stale version) | Javen explicit; 5 phase ABC mandatory | Javen + main |

### A.6 Adversarial Review

**Status**: ✅ **Completed 2026-05-19** by reviewer subagent (fresh perspective brutally-honest mode). Brief committed before review = process violation (template mandates pre-commit review). **Retroactive compliance**: reviewer findings applied as patches L+L+L below. Future briefs spawn reviewer **BEFORE** commit.

**Reviewer findings summary**:
- 6 Critical (all applied as fixes)
- 9 Major (4 applied; 5 logged as known issues)
- 9 Minor (deferred to round 2)
- Numbers verified 100% accurate against `results/*.json` (zero discrepancies)

**Verdict**: B+ with critical fixes applied. **Truthfulness A-grade. Process discipline C-grade** (violated pre-commit Phase A.6 rule).

---

## Phase B: Implementation

### B.1 Test (reproducibility)

| Test type | Status | Evidence |
|---|---|---|
| Unit test | ❌ **Missing** — only mock smoke test exists, no pytest suite, no coverage measurement | `test_caching_mock.py` (mock test, not unit) |
| Coverage ≥ 70% (template requirement) | ❌ **Missing** — no coverage tooling configured |
| Integration (4 systems same schema) | ✅ Done | 同 schema JSON output (troika_loso.json + rf_loso.json + llm_lambda_loso_sonnet_s*.json) |
| E2E (end-to-end pipeline runs) | ✅ Done | `run_all.py` |
| Result verification | ✅ Reviewer #2 5/15 独立 recompute MAE 22.63 confirmed |

**Known gap**: Template requires unit test + 70% coverage. Brief honest 缺。Academic project 范围内 reviewer #2 result audit 提供 functional verification 替代 unit test。**Not fixing this round** (low ROI for one-off submission).

### B.2 Code Review

- ✅ Reviewer #1 (5/15): launcher robustness — 0 critical
- ✅ Reviewer #2 (5/15): result integrity — 0 critical, 4 medium (per-subject crash / API retry / cost ceiling / caffeinate)
- ⏳ Reviewer #3: final report draft audit pre-submit

### B.3 Lint / Format

- ⚠️ Python: no automated black/flake8
- ⚠️ LaTeX: manual eye review only
- Action: pre-submit `python -m py_compile` + `latex compile` smoke test

### B.4 Documentation

| Artifact | Status |
|---|---|
| README.md | ✅ |
| Inline docstrings | ⚠️ Partial |
| LOSO_RESULTS_2026-05-15.md | ✅ Morning brief dashboard |
| THIS BRIEF | ✅ |

### B.5 Logging

- ✅ `results/loso_sonnet_run.log` (1952 lines structured)
- ✅ Per-window JSON: `subject / window / hr_truth / hr_pred / lambda / reason / abs_err`

### B.6 Error Handling

- ✅ API failure → `λ=1.0` fallback (graceful degrade)
- ✅ NaN excluded from MAE
- ⚠️ Known limitation: no exponential backoff retry (reviewer #2 medium)

### B.7 Config Externalization

- ✅ API key: `~/.config/anthropic-keys/ece284`
- ✅ Data path: `--data-dir` flag
- ✅ Subject list: `--subjects` flag

---

## Phase C: Deploy / Launch

### C.1 Staged Rollout

```
Pilot Subj1 30w (5/10) ✅
   ↓
Full LOSO 12 subj 1768w (5/15) ✅
   ↓
Evaluator + plots (target 5/22)
   ↓
Final report v1 draft (target 5/26)
   ↓
Reviewer agent audit + Javen review (target 5/30)
   ↓
Final report v2 + oral deck (target 6/2)
   ↓
Submit (deadline ~6/5)
   ↓
Oral defense rehearsal (1-2 days before)
```

### C.2 Rollback Plan

| 情境 | Rollback action |
|---|---|
| 5/26 v1 framing 不满意 | git revert + redraft；3 days buffer to 5/30 |
| 5/30 reviewer critical finding | 2 days fix buffer; unfixable → submit with limitations honest |
| LaTeX fail submission day | Overleaf cloud + raw .tex 提交 |
| Oral defense 问到没准备的 | "I don't know but would investigate X" 比编 honest |
| 数字 mismatch (lesson ⑭) | 主动 corrigendum email 教授 — 比被抓更好 |

### C.3 Pre-launch Checklist (before submit)

- [ ] `latex compile` ok → PDF generated
- [ ] All PDF numbers cross-checked against `results/*.json` (lesson ⑭)
- [ ] All cited papers in `references.bib` exist + DOI verified
- [ ] No placeholder (`TODO` / `XXX` / `[FILL]`) — `grep -i` check
- [ ] Reviewer #3 agent audit passed
- [ ] Javen final eyeball
- [ ] Git tag `v1.0-final-submission`

### C.4 Cost Guard

- ✅ Budget cap: $20 (Javen approve)
- ✅ Actual: $5.30 used (26.5%)
- ⏳ Remaining: ~$15
- ❌ **No hard ceiling in code** (lesson from 5/15; deferred to round 2)
- **Rule**: Report 阶段 no new API unless ablation explicitly Javen + reviewer approve

---

## Phase D: Run / Monitor

### D.1 Monitoring

| Signal | Source | Freq |
|---|---|---|
| Final report progress | git commit history | per session |
| Cost burn | Anthropic console manual | weekly |
| Reviewer findings | spawn output | per spawn |
| Deadline countdown | days to 6/5 = 17 |

### D.2 Alerting

- ❌ No automated alerting (academic)
- ✅ Manual: vault morning brief pattern (LOSO_RESULTS_2026-05-15.md)

### D.3 Heartbeat

- N/A static project; applied during 5/15 LOSO long-run (`loso_sonnet_run.log` mtime + DONE_FLAG)

### D.4 SLI / SLO

| Indicator | Objective | Current |
|---|---|---|
| Data completeness | 100% windows valid | ✅ 1768/1768 |
| Cost budget | < $20 (Javen cap); KR4 target < $10 | ✅ $5.30 (26.5% of cap) |
| Final report on-time | submit by 6/5 23:59 | TBD |
| Number accuracy | 0 mismatch between PDF and `results/*.json` (lesson ⑭ verbatim) | TBD verify pre-submit |
| Final report grade (M.3 KR1) | ≥ **13/15** (≥87%) | TBD |
| Oral assessment grade (M.3 KR2) | ≥ **13/15** (≥87%) | TBD |

⚠️ Note: KR4 budget target ($10) tighter than C.4 cap ($20). $20 is hard ceiling (Javen approve); $10 is project objective (KR4). Both valid — KR4 is internal goal, C.4 is risk boundary.

### D.5 Dashboard

- **Primary**: `LOSO_RESULTS_2026-05-15.md`
- **Secondary**: this `PROJECT_BRIEF.md`

---

## Phase E: Maintain / Improve

### E.1 Scheduled Audit

| Date | Action |
|---|---|
| 2026-05-19 today | PROJECT_BRIEF create + reviewer audit |
| 2026-05-22 | Evaluator + plots checkpoint |
| 2026-05-26 | v1 draft checkpoint |
| 2026-05-30 | Reviewer audit + Javen review |
| 2026-06-02 | v2 + oral deck checkpoint |
| 2026-06-05 | Submit |
| Post-submit | Post-mortem + lessons.md entry |

### E.2 Post-Mortem (already-identified lessons)

✅ **2026-05-19 落盘**: 4 lessons 已写入 `automation/docs/lessons.md` (per reviewer #3 finding: deferring 到 post-submit = drift risk). 下方保留 quick reference 副本：

1. **Cost tracking bug** — `LambdaGenerator.usage_summary()` state reset 多 subject 间 → Subj 6-12 报 0 cost; real ~$5.30 not $1.87. **Lesson**: per-window cost write-out
2. **Pilot generalization fallacy** — Subj1 前 30w 偶然 low-motion → MAE 7.71 misleading vs full 28.44. **Lesson**: pilot 选样必须 cover dataset variability
3. **Multi-agent reviewer pattern works** — 5/15 2 reviewer agents 独立 audit 各发现不同 issue (4 medium each, 不重叠)。**Lesson**: spawn 2+ reviewer 比 1 agent self-audit 更全面
4. **Negative result framing 需要主动建构** — paper writing 默认 positive；遇 negative 需 Sakana 范式 "interpretability vs performance trade-off" explicit framing

### E.3 Pivot-or-Persevere

- **Current**: Persevere on negative result framing
- **Pivot trigger** (none expected): grader 明确说 negative 不能写 → 极不可能；oral defense 教授深度 probe 发现 prompt engineering 不充分 → 加 limitations section
- **Decision**: persevere

### E.4 Documentation Drift

- ✅ README + LOSO_RESULTS + this BRIEF 都 single source of truth
- Rule: any code change → README update same commit

---

## Management ABC

### M.1 Discovery
- N/A (course-given problem); proposal 4/22 evaluated by Prof + Javen

### M.2 Competitive Analysis
- Internal baselines: TROIKA-lite + RF (本 project)
- External: Zhang 2015 TROIKA (2.34 BPM at rest), Schäck 2017 KalmanNet, LLM-as-signal-processor 2024-2025 业内

### M.3 OKR / KPI

| Objective | Key Result |
|---|---|
| 拿到 final project A-level grade | KR1: Final report 15% → ≥ 13/15; KR2: Oral 15% → ≥ 13/15 |
| 项目可重用于 BS/MS SoP + portfolio | KR3: PDF + code repo + 1-page summary 在 `career/` |
| 不烧 budget | KR4: 剩余 < $5 (total < $10) |

### M.4 Milestone (≤ 1-2 week chunks)

| Week | Milestone | Owner |
|---|---|---|
| Week 9 (5/18-5/24) | Evaluator + 4-system plots | @main + reviewer |
| Week 10 (5/25-5/31) | Final report v1 → reviewer → v2 | @writer subagent + reviewer + Javen |
| Week 11 (6/1-6/5) | Polish + submit + oral deck | @main + Javen |
| Finals | Oral rehearsal + defense | Javen |

### M.5 WIP Limit
- ≤ 3 in-progress concurrently
- Current: 1 (this BRIEF)

### M.6 Retro
- Each milestone hit → ≤ 5 min retro with Javen

### M.7 Stakeholder Communication
- Async: vault morning briefs
- Sync: Javen 主动 check 时

---

## AI Workflow ABC

| # | Rule | Status |
|---|---|---|
| AI.1 | Multi-agent for L2+ decisions | ✅ enforced; 5/15 2 reviewers; 5/19 this BRIEF reviewer pending |
| AI.2 | Source of truth in vault | ✅ all facts → results/*.json + source pages |
| AI.3 | PDCA mandatory Check | ✅ L1 min on every edit; L4 reviewer on high-stakes |
| AI.4 | Hooks | ✅ SessionStart hook references this BRIEF |
| AI.5 | Daily transcript audit | N/A one-off |
| AI.6 | AI 分工 | Main session driver + writer subagent (serial) + reviewer subagent (checkpoint) + Javen approver |

---

## Open Questions / Blockers

| # | Question | Owner | Path |
|---|---|---|---|
| 1 | Final report exact deadline (syllabus 没明示，README 写 ~6/5) | Javen | Check Canvas / syllabus deadline page |
| 2 | Oral assessment format (length / Q&A / slides 要求) | Javen | Verify syllabus |
| 3 | 是否需 ablation 才能 A-level | Javen + Prof | Optional; Prof OH 可问 framing |
| 4 | Report 页数 / 字数 cap (current target 7-10) | Javen | Verify syllabus Final Report section |
| 5 | Bib format (ACM default 沿 proposal) | Javen | Verify syllabus |

---

## Files Quick Reference

```
projects/ece284-llm-ppg/
├── PROJECT_BRIEF.md                    ← 本文件
├── LOSO_RESULTS_2026-05-15.md          ← 5/15 LOSO 完成 brief
├── README.md                           ← setup + reproducibility
├── run_loso_sonnet.sh                  ← LOSO launcher (per-subject crash-safe)
│
├── data.py / data/                     ← IEEE SPC 2015 + window
├── troika_lite.py                      ← Baseline 1 (signal processing)
├── rf_baseline.py                      ← Baseline 2 (ML)
├── llm_lambda.py                       ← Main: Sonnet λ-generator
├── react_agent.py                      ← Stretch (not run)
├── evaluate.py                         ← Metric aggregator
├── run_all.py                          ← End-to-end
├── plot_baselines.py / plot_pilot.py / plot_architecture.py
│
├── results/
│   ├── troika_loso.json                ← MAE 23.46
│   ├── rf_loso.json                    ← MAE 10.53
│   ├── llm_lambda_pilot_s1_sonnet.json ← pilot 30w MAE 7.71
│   ├── llm_lambda_loso_sonnet_s{1..12}.json ← MAE 22.63 (overall)
│   ├── loso_sonnet_run.log
│   ├── loso_sonnet.pid
│   ├── loso_sonnet_DONE
│   ├── baselines_comparison.{pdf,png}
│   ├── architecture.{pdf,png}
│   └── pilot_subj1_comparison.{pdf,png}
│
└── report/
    ├── update_report.tex               ← 5/11 submitted Week 8 update
    ├── README_overleaf.md
    ├── references.bib
    └── (architecture / baselines / pilot pdf copies)
```

---

*Generated 2026-05-19 by main session per 项目默认模板 5 phase ABC. Replaces stale 2026-05-18 PROJECT_BRIEF version. Reviewer audit pending — will spawn immediately for Phase A.6 mandatory adversarial review.*
