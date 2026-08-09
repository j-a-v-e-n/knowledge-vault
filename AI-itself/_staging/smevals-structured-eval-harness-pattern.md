---
name: smevals: Structured Eval Harness Pattern
technique: Separate eval execution from grading using a layered vocabulary (evals→tasks→configs→runs→graders→checks→checkers) so outputs can be re-graded cheaply without re-running expensive model calls.
when_to_use: When building a repeatable eval suite to compare models, prompts, or agent harnesses across a shared task set.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - llm-as-judge
  - harness
  - grading
  - benchmarking
  - agent-patterns
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-09
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Configs encapsulate not just the model identity but also system prompts, parameters, and agent harnesses, so the same task can be tested across different prompt or harness variations.
  faithfulness: 1.0
- claim: Graded runs can be visualized as interactive web dashboards or built into static HTML reports for sharing.
  faithfulness: 1.0
