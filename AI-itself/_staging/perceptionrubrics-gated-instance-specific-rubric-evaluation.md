---
name: PerceptionRubrics: Gated Instance-Specific Rubric Evaluation
technique: Evaluate multimodal model outputs using instance-specific Must-Right / Easy-Wrong rubrics with a gated binary-penalty scoring mechanism instead of holistic averaging
when_to_use: When benchmarking VLMs or LLMs on dense visual or factual tasks where partial credit averaging masks critical failures in essential facts
source: "http://arxiv.org/abs/2606.28322v1"
tags:
  - ai-usage
  - ai-digest
  - evals
  - multimodal
  - rubric-based-scoring
  - llm-as-judge
  - vlm
  - human-alignment
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-29
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: PerceptionRubrics pairs 1,038 information-dense images with over 12,000 instance-specific rubrics derived from golden captions, rather than using generic shared rubrics across items.
  faithfulness: 1.0
- claim: The gated scoring mechanism applies a sharp binary penalty when a model fails any Must-Right rubric, preventing partial-credit averaging from concealing critical perceptual failures.
  faithfulness: 1.0
- claim: Models that verify fragmented rubric elements individually often fail when conjunctive constraints across all Must-Right rubrics are applied simultaneously, exposing brittleness in dense perception.
  faithfulness: 1.0
