---
name: Kernel-Harness Agentic Loop with Evolutionary Run Memory
technique: Separate test execution into a kernel (Playwright/Appium) and an LLM harness that runs observe→plan→execute, generating persistent learning memories after each run.
when_to_use: Building AI agents that automate UI or end-to-end testing and need to self-improve across runs without human re-prompting.
source: "https://news.ycombinator.com/item?id=48191312"
tags:
  - ai-usage
  - ai-digest
  - agent-loop
  - memory
  - harness-pattern
  - agentic-testing
  - self-healing
  - kernel-harness
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-03
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The kernel-harness pattern assigns test execution frameworks (Playwright, Appium) the role of 'kernel' and the LLM the role of 'harness' responsible for observation, planning, and dispatching actions to the kernel.
  faithfulness: 1.0
- claim: Withholding source code from the LLM agent enforces behavioral fidelity: the agent must interact with the UI as a real user would, not exploit implementation details.
  faithfulness: 1.0
