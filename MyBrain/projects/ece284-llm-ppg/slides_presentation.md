---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  section {
    font-family: 'Helvetica Neue', sans-serif;
    font-size: 22px;
  }
  h1 { color: #1a3a6b; font-size: 36px; }
  h2 { color: #1a3a6b; font-size: 28px; }
  table { font-size: 18px; }
  .highlight { background: #fff3cd; padding: 4px 8px; border-radius: 4px; }
  footer { font-size: 14px; color: #888; }
---

# Benchmarking LLM Paradigms for PPG Heart Rate Estimation

**Javen Cao** | jacao@ucsd.edu
ECE 284 — Spring 2026 | Week 8 Project Update

---

## Motivation: The High-Motion HR Problem

**Problem**: Wrist PPG during exercise is corrupted by motion artifacts

- Standard signal processing (TROIKA): works in low motion, fails badly under high motion
- ML baselines: better, but treat HR estimation as a static pattern-matching task
- **Our question**: Can an LLM contribute context-aware reasoning that classical methods lack?

**Core Research Question**  
*Through which interaction paradigm does an LLM provide the most value for HR estimation: as a parameter generator, or as an autonomous tool orchestrator?*

---

## Experimental Setup

**Dataset**: IEEE SPC 2015 (Zhang et al.)
- 12 subjects, wrist PPG + 3-axis accelerometer + ECG ground truth
- Treadmill exercise at varying speeds
- ~1,768 non-overlapping **8-second windows** (1000 samples at 125 Hz)
- Evaluation: **12-fold Leave-One-Subject-Out Cross-Validation (LOSO-CV)**

**Four Systems Benchmarked**

| System | Paradigm | Status |
|---|---|---|
| TROIKA-lite | Signal processing (FFT + spectral subtraction) | ✅ Complete |
| Random Forest | Learned feature baseline | ✅ Complete |
| Claude λ-generator | LLM as parameter generator | 🔄 Pilot done |
| Claude ReAct | LLM as tool orchestrator | ⏳ Stretch |

---

## System 1: TROIKA-lite (Baseline)

**Algorithm** (Zhang et al., 2015):
1. FFT spectral estimation of PPG
2. Estimate motion spectrum from accelerometer
3. Spectral subtraction to suppress artifacts
4. Dominant frequency search in **[0.4 – 5.0 Hz]** (24 – 300 BPM)

**LOSO-CV Results**

| Metric | Value |
|---|---|
| Overall MAE | **23.46 BPM** |
| Best subject (S4) | 6.87 BPM |
| Worst subject (S10) | **65.06 BPM** |

⚠️ High variance — fails catastrophically under heavy motion

---

## System 2: Random Forest Baseline

**4 hand-crafted features** per window:
- Dominant spectral frequency (PPG)
- PPG-Accel spectral correlation
- Accelerometer RMS
- Spectral entropy

200-tree RF, sklearn defaults, LOSO-CV.

**Results**

| Metric | Value |
|---|---|
| Overall MAE | **10.53 BPM** |
| vs. TROIKA-lite | **−55.1%** |
| Best subject (S5) | 4.27 BPM |

**Motion-stratified breakdown**:

| Motion Level | N windows | RF Median Error |
|---|---|---|
| Low (RMS < 1.3) | 508 | ~3 BPM |
| Medium (1.3–1.7) | 673 | ~5 BPM |
| High (> 1.7) | 587 | **~10 BPM** |

→ High-motion windows remain the bottleneck

---

## System 3: Claude λ-generator

**Key Idea**: Instead of having the LLM predict HR directly, it generates a scalar parameter **λ ∈ [0.1, 3.0]** — the spectral subtraction weight — based on the window's motion context.

```
PPG window → 6-field summary → Claude Sonnet 4.5 → λ → TROIKA pipeline → HR
```

**6-field prompt per window**:
```json
{
  "accel_rms": 1.82,
  "ppg_snr_db": 8.3,
  "dominant_freq_hz": 2.1,
  "motion_regime": "high",
  "ppg_top3_peaks_hz": [1.9, 2.1, 2.4],
  "last_3_hr_bpm": [112, 108, 115]
}
```

**Prompt Caching**: 5,898-token system prompt cached with `cache_control: ephemeral` → **94.1% cache hit rate** in pilot

---

## λ-generator: Pilot Results (Subject 1, 30 windows)

| System | MAE (30 windows) | vs. TROIKA | vs. RF |
|---|---|---|---|
| TROIKA-lite | 10.55 BPM | — | — |
| Random Forest | 11.94 BPM | +13.2% | — |
| **Claude λ-generator** | **7.90 BPM** | **−25.1%** | **−33.8%** |

**Cost**: $0.1104 / 30 windows → extrapolated full LOSO ≈ **$6.60**

**Notable outliers** (2/30):
- Window 16: λ=1.2, pred 142 vs truth 77 BPM (+65 err)
- Window 28: λ=0.6, pred 45 vs truth 103 BPM (−57 err)

→ λ-generator outperforms both baselines on this pilot, but 2 outliers need investigation in motion-stratified analysis

---

## Why λ-generator Instead of Direct HR Prediction?

**Design rationale** — three reasons:

1. **LLMs are bad at arithmetic**: Direct prediction requires the model to reproduce signal processing math. Parameter generation offloads computation to a deterministic pipeline.

2. **Interpretability**: λ is semantically meaningful. `λ = 0.1` → "mostly suppress motion"; `λ = 3.0` → "aggressive subtraction needed for high-motion"

3. **Cost efficiency**: One LLM call per window generates a single number, then the pipeline runs locally. Full LOSO ≈ $6.60 vs. per-window HR call would be 3–5× more expensive.

---

## Architecture Overview

```
              ┌──────────────────────────────────┐
PPG + Accel   │  6-field JSON summary            │
─────────────►│  (accel_rms, snr, freq, regime,  │
              │   top3 peaks, last 3 HR)          │
              └─────────────┬────────────────────┘
                            │
                            ▼
              ┌──────────────────────────────────┐
              │  Claude Sonnet 4.5               │
              │  System: 5,898-tok cached prompt │
              │  → returns λ ∈ [0.1, 3.0]       │
              └─────────────┬────────────────────┘
                            │ λ
                            ▼
              ┌──────────────────────────────────┐
              │  TROIKA spectral subtraction     │
              │  weight = λ                      │
              │  → HR estimate (BPM)             │
              └──────────────────────────────────┘
```

Cache hit rate 94.1% → 82% cost reduction vs. uncached

---

## Next Steps (Weeks 9–10)

**Immediate (Week 8–9)**:
- [ ] Full 12-subject LOSO for λ-generator (~$6.60 budget)
- [ ] Claude Haiku 4.5 pilot: cost comparison vs. Sonnet
- [ ] Motion-stratified breakdown for λ-generator

**Week 9 Analysis**:
- [ ] λ appropriateness audit: 100-window sample — does LLM pick sensible values?
- [ ] Token cost + latency table (Haiku vs. Sonnet vs. RF compute time)
- [ ] Outlier analysis: what makes window 16 and 28 fail?

**Stretch (if time)**:
- [ ] Claude ReAct orchestrator — LLM calls `get_dominant_freq`, `run_spectral_subtraction` as tools, reasons step-by-step

**Final deliverable**: 7–10 page ACM Large 2-column report + GitHub repo

---

## Summary

| | TROIKA-lite | Random Forest | Claude λ-gen (pilot) |
|---|---|---|---|
| MAE (full LOSO) | 23.46 BPM | **10.53 BPM** | TBD |
| MAE (30-win pilot) | 10.55 | 11.94 | **7.90** |
| Interpretable? | ✅ | ❌ | ✅ |
| Motion-aware? | ❌ | Partial | ✅ |
| Cost | $0 | $0 | ~$6.60/LOSO |

**Key finding so far**: Claude λ-generator achieves −25% vs. TROIKA and −34% vs. RF on a 30-window pilot, with strong prompt caching efficiency.

**Questions?**

---

*ECE 284 Spring 2026 · Javen Cao · Week 8 Project Update*
