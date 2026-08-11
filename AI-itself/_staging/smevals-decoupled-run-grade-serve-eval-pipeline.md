---
name: smevals: Decoupled Run-Grade-Serve Eval Pipeline
technique: Structure AI evals as separate run, grade, and serve phases with a shared vocabulary of evals/tasks/configs/runs/graders/checks to enable reusable, composable evaluation harnesses.
when_to_use: When building or formalizing an eval suite to compare models, system prompts, or agent harnesses across a consistent set of tasks.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - evaluation
  - harness
  - grading
  - model-comparison
  - agent-patterns
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-11
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Checks exist on a spectrum from simple operations (string matching, XML validation) to complex operations that themselves invoke a model to evaluate the output, allowing grading sophistication to scale with need.
  faithfulness: 1.0
- claim: Configs encapsulate not just model identity but also system prompt, inference parameters, and agent harness, so the same task can be run under radically different LLM setups and compared directly.
  faithfulness: 1.0
