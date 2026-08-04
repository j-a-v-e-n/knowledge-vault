---
name: Structured Eval Taxonomy (smevals pattern)
technique: Organize LLM evaluations using a strict vocabulary hierarchy: Eval > Task > Config > Run > Grader > Checks/Checkers, separating execution from grading from reporting.
when_to_use: When building or standardizing an eval harness for comparing models, prompts, or system configurations across multiple tasks.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - harness
  - grading
  - model-comparison
  - structured-vocabulary
  - agent-testing
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-04
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: An Eval is a collection of challenges that answers a question about model capabilities (e.g., 'How well does this model generate SVGs?').
  faithfulness: 1.0
- claim: A Task is a single individual challenge within an Eval.
  faithfulness: 1.0
- claim: A Config specifies the model and testing parameters including system prompt and model settings.
  faithfulness: 1.0
- claim: A Runner is the script that executes Runs.
  faithfulness: 1.0
- claim: A Grader evaluates Run results and produces grades.
  faithfulness: 1.0
