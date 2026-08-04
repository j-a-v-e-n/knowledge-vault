---
name: Structured LLM-Assisted Programming Workflows
technique: Apply plan-first, fresh-context, and self-verification patterns to improve LLM coding output quality and reliability.
when_to_use: When using LLMs for non-trivial software development tasks where output quality and reliability matter.
source: "https://news.ycombinator.com/item?id=46255285"
tags:
  - ai-usage
  - ai-digest
  - prompting
  - agent-patterns
  - context-management
  - planning
  - self-verification
  - workflow
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-04
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Iterating on a written plan with the model before approving execution provides a 2–3x quality improvement over issuing direct execution requests.
  faithfulness: 1.0
