---
name: Three-Phase LLM Eval Pipeline (run / grade / report)
technique: Separate LLM evaluation into three independent stages—run (model inference), grade (check outputs), report (visualize)—with typed graders and reusable configs.
when_to_use: When building or iterating eval suites for models, prompts, or agent harnesses across multiple model configurations.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - grading
  - harness
  - pipeline
  - llm-as-judge
  - multi-model
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-08
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: A config specifies a model selection plus optional parameters such as system prompts or model-level settings, enabling the same task to be tested under different conditions.
  faithfulness: 1.0
- claim: Graders assess run outputs by executing checks; supported check types include string matching, XML validation, and custom operations.
  faithfulness: 1.0
