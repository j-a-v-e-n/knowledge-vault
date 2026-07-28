---
name: Observer-Planner-Verifier + Execution Kernel Split
technique: Separate the LLM into observer/planner/verifier roles from a deterministic execution kernel so it cannot shortcut through implementation details
when_to_use: When building agentic test or automation harnesses where LLMs would otherwise find code-level shortcuts that bypass real user workflows
source: "https://news.ycombinator.com/item?id=48191312"
tags:
  - ai-usage
  - ai-digest
  - agent-harness
  - agentic-loop
  - memory
  - evals
  - qa
  - role-separation
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-28
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The LLM runs in a harness executing an observation → planning → action-execution → self-healing loop, with the execution kernel (Playwright/Appium) as a separate layer.
  faithfulness: 1.0
- claim: Keeping the LLM as observer, planner, and verifier—rather than code writer—prevents the AI from 'greedily' writing tests that pass via implementation shortcuts instead of genuine user workflows.
  faithfulness: 1.0
