---
name: PerceptionRubrics: Dual-Stream Rubric Eval with Gated Scoring
technique: Structure multimodal evals into Must-Right + Easy-Wrong rubric streams with binary-penalty gated scoring instead of linear average scores.
when_to_use: When evaluating vision-language or multimodal models where holistic semantic matching masks fine-grained perceptual failures.
source: "http://arxiv.org/abs/2606.28322v1"
tags:
  - ai-usage
  - ai-digest
  - evals
  - multimodal
  - rubrics
  - scoring
  - llm-as-judge
  - vision-language
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-22
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Models can score high on standard benchmarks while failing strict conjunctive constraints, a brittleness the gated rubric scoring surfaces that linear averaging conceals.
  faithfulness: 1.0
