---
name: Tree-Search Self-Correcting Agent with Explicit Backtracking Primitives
technique: Structure long-context search as a hierarchical tree traversal where the agent has explicit zoom_in / zoom_out / shift / answer primitives, trains on trajectories that include deliberate wrong-branch detours followed by recovery, and uses RL rewards on grounding accuracy to reinforce self-correction.
when_to_use: When an agent must locate relevant content inside a long, structured information space (long video, large document, hierarchical codebase) where linear scan is too slow and the agent needs to recover from wrong-path decisions.
source: "http://arxiv.org/abs/2607.16189v1"
tags:
  - ai-usage
  - ai-digest
  - agent-patterns
  - self-correction
  - hierarchical-search
  - tree-search
  - long-context
  - rl-training
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-21
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: The agent's action space is restricted to four discrete primitives—zoom_in, zoom_out, shift, and answer—making backtracking an explicit, learnable operation rather than an implicit emergent behavior.
  faithfulness: 1.0
- claim: Training trajectories are synthesized to include deliberate detours into incorrect branches followed by explicit recovery steps, teaching the model to self-correct.
  faithfulness: 1.0
- claim: The training pipeline combines supervised fine-tuning on synthesized trajectories with reinforcement learning using both temporal-grounding rewards and answer-accuracy rewards.
  faithfulness: 1.0
