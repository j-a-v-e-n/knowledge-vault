---
name: PerceptionRubrics: Gated Dual-Stream Rubric Evaluation
technique: Evaluate multimodal model outputs using two rubric streams (must-right vs easy-wrong) with gated binary penalties on mandatory facts rather than linear score averaging.
when_to_use: When designing LLM-judge or eval harnesses for vision-language or captioning tasks where holistic semantic similarity masks fine-grained perceptual failures.
source: "http://arxiv.org/abs/2606.28322v1"
tags:
  - ai-usage
  - ai-digest
  - evals
  - multimodal
  - rubrics
  - llm-judge
  - scoring
  - vision-language
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-30
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Models can score well on holistic semantic metrics while failing gated rubric evaluation, revealing brittleness in dense perceptual domains not captured by standard benchmarks.
  faithfulness: 1.0
