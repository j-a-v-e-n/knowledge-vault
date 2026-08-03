---
name: smevals: Structured Eval Suites with Separated Run/Grade Phases
technique: Organize LLM evaluations into tasks+configs, execute runs separately from grading, and compose graders from checks and model-based checkers to comparatively test models, prompts, and harnesses.
when_to_use: When you need to systematically benchmark and compare LLM configurations (models, system prompts, agent harnesses, parameters) on the same task set with reproducible, inspectable results.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - prompting
  - agent-harness
  - grading
  - benchmarking
  - rag
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-03
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: An eval is a collection of 'tasks' (individual concrete challenges) all answering a specific question about model capability.
  faithfulness: 1.0
- claim: 'Checkers' are scripts that enable complex grading logic including model-based assessment of outputs.
  faithfulness: 1.0
