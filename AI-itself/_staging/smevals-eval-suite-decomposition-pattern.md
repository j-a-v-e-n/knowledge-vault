---
name: smevals eval-suite decomposition pattern
technique: Structure AI evals as a hierarchy of Evals→Tasks, Configs, Runs, Graders, and Checks with execution separated from grading
when_to_use: When building repeatable evaluation pipelines to compare models, prompts, or agent harnesses across the same task suite
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - grading
  - model-comparison
  - agent-harness
  - prompting
  - pipeline
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-01
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: An eval suite is organized as: Evals (a capability question) containing Tasks (individual challenges), run against Configs (model + optional system prompt + parameters + harness).
  faithfulness: 1.0
- claim: Checkers are custom scripts that implement complex or domain-specific evaluation logic beyond the built-in checks.
  faithfulness: 1.0
