# PROJECT_BRIEF — ECE 284 LLM-PPG

## Goal
Benchmark 4 LLM-vs-classical paradigms for wearable PPG heart-rate estimation under motion artifacts on IEEE SPC 2015 (12-subject LOSO), demonstrating LLM-as-parameter-generator (λ-generator) outperforms both signal-processing and ML baselines.

## User
Javen Cao | ECE 284 Spring 2026 final project | Course = Digital Health Technologies

## MVP (committed scope per proposal)
- TROIKA-lite baseline (signal processing): bandpass + FFT + spectral subtraction
- Random Forest baseline (ML): 4 hand-crafted spectral features
- **Claude λ-generator (main contribution)**: LLM reads each 8s window → outputs spectral-subtraction λ → driving fixed pipeline
- 12-subject LOSO evaluation on all 3 above, motion-stratified breakdown
- Project Update report (Week 8) + Final report (Week 10) + Oral defense (Week 11)

## Stretch (only if main MVP done)
- Claude ReAct orchestrator: LLM dynamically calls tools, head-to-head vs λ-generator

## Non-goals
- Not building new sensor hardware
- Not deploying to phone / smartwatch
- Not claiming SOTA on PPG HR estimation (paradigm comparison, not optimization)
- Not retraining any LLM (use Claude API only)

## Definition of Done
- [ ] Project Update report submitted (deadline shifted to 5/11 per Javen 5/10 update, draft already at `project_update_draft.md`)
- [ ] All 3 committed-scope LOSO results in `results/*.json`
- [ ] Final report (ACM 2-column, 7-10 pages) submitted ~2026-06-05
- [ ] Final Oral defense (Week 11)
- [ ] GitHub repo link submitted with final report

## Status (2026-05-18)
- TROIKA-lite ✅ done (overall MAE 23.46 BPM)
- RF baseline ✅ done (overall MAE 10.53 BPM, 55.1% better than TROIKA)
- λ-generator pilot ✅ done on Subject 1 30-window (MAE 7.90 BPM, sonnet)
- ⚠️ **Blocker (5/15)**: Anthropic API account out of credits → 12-subject LOSO 跑不了 → 阻塞 final report quantitative section
- Update report draft written by daemon 5/9; LaTeX 化 + Javen submit pending

## Files of interest
- `troika_lite.py` — Route A baseline + LOSO CLI
- `rf_baseline.py` — Route B baseline + LOSO CLI
- `llm_lambda.py` — Route C main contribution; has prompt caching
- `evaluate.py` — LOSO orchestrator + 4 eval axes
- `run_all.py` — end-to-end runner
- `project_update_draft.md` — Week 8 update draft

## Constraints
- Budget: <$5 Anthropic API total (94% cache hit rate keeps cost down)
- All CPU (no GPU needed)
- Dataset: IEEE SPC 2015 12 subjects already downloaded in `data/`
- Final report = ACM Large 2-column format

## Related vault entries
- task-board: `task-018`
- proposal: `MyBrain/raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf`
- related papers: `[[Zhang_2015_TROIKA]]`, `[[Arakawa_2023_LemurDx]]`, `[[Garg_2025_DopFone]]`
