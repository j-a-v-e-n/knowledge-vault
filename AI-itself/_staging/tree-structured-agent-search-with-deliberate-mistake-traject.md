---
name: Tree-Structured Agent Search with Deliberate-Mistake Trajectory Synthesis
technique: Represent a long sequential context as an adaptive tree of segments; train an agent with four navigation actions (zoom_in, zoom_out, shift, answer) using trajectories that include deliberate wrong turns followed by recovery sequences, then fine-tune with RL rewards on both grounding accuracy and answer correctness.
when_to_use: When an LLM agent must search a long, structured context (video, document corpus, code repo) for evidence to answer a question and premature commitment to an early decision is a known failure mode.
source: "http://arxiv.org/abs/2607.16189v1"
tags:
  - ai-usage
  - ai-digest
  - agent-design
  - search
  - self-correction
  - reinforcement-learning
  - trajectory-synthesis
  - hierarchical-context
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-27
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: A trajectory synthesis pipeline generates multi-step paths that deliberately include wrong turns followed by explicit recovery sequences, so the agent is trained on examples of self-correction, not only optimal paths.
  faithfulness: 1.0
- claim: The self-correcting tree-search agent outperforms prior methods by +12.5 mIoU on CG-Bench and +7.4 T-F1 on Haystack-Ego4D for grounded long-video QA.
  faithfulness: 1.0
