---
name: VideoTreeSearch: Self-Correcting Hierarchical Agent Search
technique: Structure long-context navigation as tree search with explicit backtracking primitives, trained on synthetic trajectories that include deliberate wrong-branch detours followed by recovery
when_to_use: When an agent must locate specific evidence within a very long sequence (video, document, conversation history) and must be robust to initially exploring wrong branches
source: "http://arxiv.org/abs/2607.16189v1"
tags:
  - ai-usage
  - ai-digest
  - agent-patterns
  - tree-search
  - self-correction
  - backtracking
  - long-context
  - grounding
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-22
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The agent operates over a non-uniform temporal tree built from visual scene boundaries, so each node represents a semantically meaningful segment rather than a fixed-size chunk.
  faithfulness: 1.0
- claim: Training trajectories are synthetically generated to include deliberate detours into incorrect branches followed by explicit recovery steps, teaching the agent to self-correct rather than only learning from correct paths.
  faithfulness: 1.0
- claim: The pipeline combines supervised fine-tuning on these synthetic recovery trajectories with reinforcement learning rewards tied to grounding accuracy and answer accuracy.
  faithfulness: 1.0
