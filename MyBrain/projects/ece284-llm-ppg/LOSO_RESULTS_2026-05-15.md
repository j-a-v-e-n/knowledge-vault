# ECE284 LOSO Sonnet λ-generator — Morning Brief

> Javen 早上 read 第一件事。LOSO 已完成 + 两个 reviewer agent 独立 audit (launcher robustness + result integrity)。所有 framing / 下一步 decision 留给你醒后跟 reviewer 一起做。

---

## TL;DR (一句话)

**LLM-as-parameter-generator paradigm 在 PPG HR 估计上 underperforms ML baseline 2.15×；overall MAE 22.63 BPM 跟 TROIKA-lite 23.46 几乎打平，但 Random Forest 10.53 更好。这是一个 scientifically valid 的 negative result，可用于 final report。Pilot 7.90 BPM 部分 misleading — 后续 windows performance 退化严重 (Subj 1: 7.71 → 33.72)。**

---

## 实跑数据

### 时间 / 成本
- 启动: 2026-05-15 00:28:58
- 完成: 2026-05-15 01:04:xx
- **实际耗时: ~35 分钟** (vs 估计 6h，快 10x，cache 命中率比 pilot 还高)
- **实际成本: ~$5.30 ± $0.50** (reviewer audit 发现 usage tracking bug — 见下方)
- ⚠️ 之前我 reported $1.87 是 bug，真实约 $5.30。理由：1768 windows × $0.003/window ≈ $5.30。Verify 在 Anthropic console
- API errors: **0** (1768 valid / 1768 total)

### Overall MAE (4 system 对比)

| System | Overall MAE (BPM) | vs RF baseline |
|---|---|---|
| Random Forest | **10.53** | — (best) |
| Claude Sonnet λ-generator | **22.63** | **+114.9% worse** |
| TROIKA-lite | **23.46** | +122.7% worse |
| (ReAct stretch goal — not run) | — | — |

→ **Sonnet ≈ TROIKA**, Sonnet **2.15× worse than RF**

### Per-subject MAE breakdown (Sonnet λ-generator)

| Subj | MAE (BPM) | 备注 |
|---|---|---|
| 1 | 28.44 | pilot 30w 测的是 7.71 — 后段 30-148 MAE 33.72 |
| 2 | 33.98 | |
| 3 | 19.98 | |
| 4 | **5.40** | 最好 — 低 motion subject |
| 5 | 12.50 | |
| 6 | 13.67 | |
| 7 | 19.94 | |
| 8 | 15.12 | |
| 9 | 10.15 | |
| 10 | **65.06** | 最差 — 高 motion + 大概率 sensor 不稳 |
| 11 | 32.06 | |
| 12 | 15.44 | |

Variance 巨大：5.4 ↔ 65.06，跨 12× 差距。

---

## Reviewer #2 audit 关键 finding (result integrity)

### ✅ Verified correct
- MAE computation 22.63 BPM 正确 (reviewer 独立 recompute)
- TROIKA / RF baseline 数字 (23.46 / 10.53) 都 verified
- Per-subject MAE 12/12 全部 verified
- 无 LLM degeneration (λ range 0.2-2.3, HR pred range 30-217)
- 无 "narrow output" pathology — `reason` field 显示 LLM 真在 reason

### 🚨 Critical bug found
- **Cost accounting**: Subj 6-12 的 JSON `n_calls=0 / cost=$0` 但 windows 全 valid
- **Root cause**: `LambdaGenerator.usage_summary()` 在 multi-subject run 间有 state reset bug
- **Impact**: 只影响 cost tracking，**不影响 MAE 数据正确性**
- Action: 不需 re-run；report 写 "$5.30 ± $0.50" 加 footnote

### ⚠️ Pilot misleading hypothesis — nuanced
- Subj 1 第 30 窗口前 MAE 7.71 vs 第 30 窗后 MAE 33.72 — **4.37× 恶化** ✓ confirm
- **跨 12 subject pattern**:
  - **7/12 subjects** 跟 Subj 1 一样后段恶化 ≥ 2×
  - **5/12 subjects** (Subj 4, 5, 9, 12 等) 反例 — 后段同样 OK 或更好
- 真实解读：**不是** "time-indexed low-motion warm-up" 现象，**是** subject-specific motion profile — Subj 1 前 30w 恰好 hit 低 motion
- → Pilot strategy 取 "前 30w" 是 unlucky generalization，本身没设计错

### Recommended report framing (来自 reviewer)

> "We demonstrate that LLM-as-parameter-generator can **match classical signal processing** (TROIKA) but **cannot compete with supervised ML** (Random Forest) on this physiological signal task. This suggests LLM reasoning over spectral features is fundamentally limited compared to learned feature extraction. The paradigm may be viable for **interpretability** (λ tuning is human-readable) but not for **SOTA performance**."

---

## 你醒后需要决定的事 (按新规则跟 reviewer 一起)

| # | Decision | Stakes | 谁参与 |
|---|---|---|---|
| 1 | Final report 大方向 framing — "negative result valuable" 还是 "mixed" 还是 "limitations heavy" | 报告整体调性 | Javen + writer subagent + reviewer |
| 2 | 是否做额外 ablation (prompt 改 / λ grid 调 / temperature 变)？时间 + 成本 commitment | $5-15 + ~3h | Javen 拍板 + reviewer 审 cost-benefit |
| 3 | 是否启动 ReAct stretch goal | $$ + time | Javen 拍板，按 proposal 是 stretch 不强求 |
| 4 | 4-system comparison plot 设计 (bar / box / violin / per-subject heatmap) | 视觉表达 | Javen + engineer subagent |
| 5 | 何时开始 final report draft | timeline | Javen — 目前距 6/5 ~21 天充足 |
| 6 | Patch `llm_lambda.py` 修 cost tracking bug — 是 fix 还是留到下次 | low priority | Javen 决定 |

---

## 接下来不做的事 (按新规则 + 我睡前 commitment)

- ❌ 不写 evaluator / merge script (架构决定 — 需 reviewer 在 loop)
- ❌ 不写 plot script (同上)
- ❌ 不 patch `llm_lambda.py` (架构决定)
- ❌ 不写 final report 任何段落 (key deliverable — 需 writer subagent + reviewer + Javen)
- ❌ 不 launch 任何 new API spending
- ❌ 不 commit 不可逆操作

---

## 当下 vault 落盘清单

- ✅ 12 个 per-subject JSON `results/llm_lambda_loso_sonnet_s{1..12}.json`
- ✅ Run log `results/loso_sonnet_run.log`
- ✅ Done flag `results/loso_sonnet_DONE`
- ✅ Launcher script `run_loso_sonnet.sh` (可复用)
- ✅ 本文件 `LOSO_RESULTS_2026-05-15.md`
- ✅ CLAUDE.md L535 新规则 "重大决定不允许 single-agent"
- ❌ Task-board 还没 update LOSO 完成状态 (留你醒后看，避免我 single-agent decide 移到哪列)

---

## 文件路径快查

```
projects/ece284-llm-ppg/
├── LOSO_RESULTS_2026-05-15.md       ← 本文件
├── results/
│   ├── loso_sonnet_DONE              ← 完成 flag
│   ├── loso_sonnet_run.log           ← 完整 run log
│   ├── llm_lambda_loso_sonnet_s1.json
│   ├── ... (s2 to s12)
│   ├── llm_lambda_pilot_s1_sonnet.json  ← 之前 30w pilot
│   ├── troika_loso.json              ← TROIKA baseline (MAE 23.46)
│   └── rf_loso.json                  ← RF baseline (MAE 10.53)
├── run_loso_sonnet.sh                ← per-subject launcher with crash recovery
└── report/
    └── update_report.tex             ← 5/11 update report 已交 — 没动
```

---

*Generated 2026-05-15 by main session after LOSO 35-min run + 2 reviewer subagents audit (launcher robustness pre-launch + result integrity post-completion).*
