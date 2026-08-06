---
name: smevals: Hierarchical Eval Structure with Separated Execution and Grading
technique: Structure AI evals as YAML-defined hierarchies (evals→tasks→configs→runs→graders→checkers) with execution and grading as separate phases, enabling flexible post-hoc analysis and LLM-as-judge scoring.
when_to_use: When comparing models, system prompts, or agent harnesses against a repeatable set of challenges and needing reproducible, explorable results.
source: "https://simonwillison.net/2026/Jul/31/smevals/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - evals
  - grading
  - model-as-judge
  - testing
  - harness
  - prompting
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-06
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: An 'eval' is a collection of challenges designed to answer a specific question about a model (e.g., 'how well can this model generate SVGs?').
  faithfulness: 1.0
- claim: Graders evaluate run results by executing a sequence of checks and producing a grade.
  faithfulness: 1.0
- claim: Checkers can range from simple operations (string matching, valid XML check) to sophisticated assessments using other LLMs as judges.
  faithfulness: 1.0
