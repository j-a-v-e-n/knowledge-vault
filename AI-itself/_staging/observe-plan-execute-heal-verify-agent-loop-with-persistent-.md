---
name: Observe-Plan-Execute-Heal-Verify Agent Loop with Persistent Memory
technique: Structure an agentic test harness as a five-phase loop (observation → planning → action execution via deterministic kernel → self-healing on failure → verification) and persist learning/product memories across runs so the agent improves over time.
when_to_use: When building LLM-driven QA or automation agents that must reliably reflect real user behavior, recover from transient failures, and accumulate domain knowledge across sessions.
source: "https://news.ycombinator.com/item?id=48191312"
tags:
  - ai-usage
  - ai-digest
  - agent-patterns
  - agentic-loop
  - self-healing
  - memory
  - evals
  - qa-harness
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-27
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Delegating physical execution to a deterministic kernel (Playwright for web, Appium for mobile) while keeping observation, planning, and verification in the LLM prevents the model from writing shortcuts that do not mimic real user behavior.
  faithfulness: 1.0
- claim: When LLMs write both code and tests directly, they greedily optimize for test passage rather than genuine behavioral validation.
  faithfulness: 1.0
