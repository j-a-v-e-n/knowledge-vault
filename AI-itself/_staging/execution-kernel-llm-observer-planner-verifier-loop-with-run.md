---
name: Execution-Kernel + LLM Observer-Planner-Verifier Loop with Run Memory
technique: Separate a deterministic execution kernel (e.g. Playwright, Appium) from the LLM, which acts only as observer, planner, and verifier, and accumulate persistent 'learning memories' after each run to improve future runs.
when_to_use: When building agentic QA or automation harnesses where you need reliable action execution, self-healing on failure, and iterative improvement without rewriting test logic.
source: "https://news.ycombinator.com/item?id=48191312"
tags:
  - ai-usage
  - ai-digest
  - agent-loop
  - agentic-qa
  - memory
  - self-healing
  - tool-use
  - harness
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-22
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The agent loop follows the sequence: observation → planning → executing planned actions via kernel → self-healing (when a planned action fails) → verification.
  faithfulness: 1.0
- claim: Tests are defined in natural language rather than code, which addresses the problem of AI 'greedily chasing passing tests and sometimes bending the rules'.
  faithfulness: 1.0
- claim: The framework generates 'learning & product memories from each run, improving itself over time', implementing persistent cross-run memory for agent self-improvement.
  faithfulness: 1.0
- claim: Mobile automation uses Appium as the execution kernel, applying the same kernel/LLM separation pattern to non-web targets.
  faithfulness: 1.0
