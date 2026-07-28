---
name: PerceptionRubrics: Dual-Stream Gated Rubric Evaluation
technique: Split evaluation rubrics into Must-Right (mandatory facts) and Easy-Wrong (fine-grained traps) categories, then score with gated binary penalties for mandatory failures instead of linear averaging.
when_to_use: When designing evals for multimodal or generative models where holistic similarity scores mask critical factual failures and you need metrics that correlate with human perception.
source: "http://arxiv.org/abs/2606.28322v1"
tags:
  - ai-usage
  - ai-digest
  - evals
  - rubrics
  - multimodal
  - scoring
  - human-alignment
  - llm-as-judge
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-28
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The framework pairs 1,038 information-dense images with over 12,000 instance-specific evaluation rubrics distilled from golden captions.
  faithfulness: 1.0
- claim: Rubrics are split into two types: Must-Right rubrics that capture essential factual elements a model must get correct, and Easy-Wrong rubrics that target fine-grained perceptual details prone to model errors.
  faithfulness: 1.0
- claim: Golden captions are constructed via a Circular Peer-Review consensus pipeline before being distilled into rubrics.
  faithfulness: 1.0
- claim: The scoring mechanism uses gated binary penalties: failure on a Must-Right (mandatory) rubric triggers a sharp binary penalty rather than partial credit, enforcing conjunctive correctness.
  faithfulness: 1.0
