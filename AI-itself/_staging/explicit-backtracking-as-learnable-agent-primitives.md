---
name: Explicit Backtracking as Learnable Agent Primitives
technique: Train agents with explicit backtrack/recovery actions using trajectory synthesis that deliberately includes wrong-branch detours followed by corrections, plus RL reward on final accuracy.
when_to_use: When building search or retrieval agents over large corpora where greedy forward-only navigation causes irrecoverable errors from early mistakes.
source: "http://arxiv.org/abs/2607.16189v1"
tags:
  - ai-usage
  - ai-digest
  - agents
  - search
  - self-correction
  - rl
  - trajectory-synthesis
  - tree-search
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-28
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Prior agentic search methods support only forward narrowing and cannot recover from early navigation mistakes.
  faithfulness: 1.0
- claim: The tree structure for search is built from semantic scene boundaries, producing semantically coherent segments rather than uniform time windows.
  faithfulness: 1.0
- claim: Supervised fine-tuning uses synthetically generated trajectories that deliberately include detours into incorrect branches followed by recovery steps, teaching the agent to correct itself.
  faithfulness: 1.0
