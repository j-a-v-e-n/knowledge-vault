---
name: smevals: structured eval taxonomy with separated runs and grading
technique: Organize LLM evaluations into a strict hierarchy (eval → tasks → configs → runs → graders → checks) and decouple execution of runs from the grading step for flexible, repeatable evaluation workflows.
when_to_use: When building or structuring an eval suite to benchmark models, prompts, or agent harnesses across multiple configurations.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - evaluation
  - grading
  - testing
  - agent-harness
  - prompting
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-02
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: An eval is a collection of challenges designed to answer specific questions about model capabilities.
  faithfulness: 1.0
- claim: Graders are systems that evaluate run results using one or more defined checks.
  faithfulness: 1.0
- claim: Checks are individual evaluation operations that range from simple string matching to XML validation to model-based analysis.
  faithfulness: 1.0
