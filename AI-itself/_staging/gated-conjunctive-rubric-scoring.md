---
name: Gated Conjunctive Rubric Scoring for AI Evaluators
description: Two-tier (Must-Right / Easy-Wrong) atomic rubric decomposition with conjunctive gating — use when building LLM judges where partial correctness must not mask critical fact failures.
tags:
  - ai-usage
  - ai-digest
  - evaluation
  - llm-judge
  - grading
  - rubrics
  - conjunctive-scoring
source: "http://arxiv.org/abs/2606.28322v1"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Gated Conjunctive Rubric Scoring for AI Evaluators

## What

A structured approach to designing AI evaluators that escapes the averaging trap. Rather than scoring criteria and averaging, you:
1. **Decompose** each evaluation into atomic, instance-specific rubric items — each a single independently verifiable claim.
2. **Classify** items into two tiers: **Must-Right** (non-negotiable essentials — failure here is disqualifying) and **Easy-Wrong** (fine-grained details — failure here is penalized but not fatal).
3. **Gate** the overall score conjunctively: if any Must-Right item fails, the overall verdict collapses to a sharp binary penalty regardless of performance on all other items.

Source: PerceptionRubrics paper (arXiv 2606.28322), validated on 1,038 dense images with 12,000+ instance-specific rubrics; gated metrics showed substantially better alignment to human perception priorities than conventional averaging benchmarks.

## When to use

- Building an LLM judge or auto-grader where certain facts or constraints must all be true simultaneously (dense visual descriptions, medical/legal/safety outputs, structured data extraction).
- Any grading scenario where "9 out of 10 criteria correct but the 1 essential criterion wrong" should NOT score 90%.
- Calibrating automated metrics to human judgment rather than semantic similarity scores.
- Detecting brittleness: models that pass atomic fragment checks individually but fail under conjunctive constraint — the gated approach surfaces this; averaging hides it.

## How it works

1. **Instance-specific rubric construction**: Generate atomic rubric items per test case. Avoid generic rubrics — each item should be a concrete verifiable claim for that specific instance.
2. **Tier assignment**: Label each item Must-Right (essential; mis-getting this is disqualifying) or Easy-Wrong (nuanced; penalized but not fatal). This labeling is domain-expert-driven upfront.
3. **Gated scoring**: Evaluate each rubric item independently (pass/fail). If any Must-Right item fails → overall score drops sharply (hard cap or zero), regardless of Easy-Wrong scores. Only when all Must-Right items pass does Easy-Wrong performance add positive nuance to the final score.
4. **Aggregation**: Report final score using conjunctive logic, not a simple mean — this is what keeps the metric aligned to human priority.

## Caveats

- Rubric and tier quality determines everything: mis-labeled Must-Right items cause the gate to fire incorrectly. Budget upfront effort on tier calibration.
- The Must-Right / Easy-Wrong boundary is domain-specific — there is no universal recipe; human or expert judgment is required per domain.
- For open-ended creative tasks where no single atomic fact is truly non-negotiable, the Must-Right tier may be empty and gating adds no value over averaging.
- Original validation is on vision-language models with information-dense images; the scoring logic is model-agnostic and transferable, but rubric construction difficulty scales with output complexity.
- The paper reports an 8% open-vs-proprietary perception gap that conventional benchmarks miss — a signal that domain-specific gated evals can reveal capability gaps that headline averages obscure.

---
*Source: http://arxiv.org/abs/2606.28322v1. Distilled by the AI-itself digest — review before blessing.*
