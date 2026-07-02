---
name: Living Documentation for Multi-Session Agent Continuity
technique: Maintain plan.md + notes.md + understanding.md throughout agent execution so each new session resumes with full context instead of starting blind
when_to_use: Any multi-session agentic project where context cannot fit in one window or work spans multiple Claude sessions
source: "https://simonwillison.net/2026/Jun/22/porting-moebius/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - multi-session
  - context-management
  - documentation
  - agent-continuity
  - handoff
  - subagent
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-06-29
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Save Claude's exploratory analysis from one session to a markdown file (e.g. research.md) so the next agent session can read it as a context bridge between Claude.ai chat work and Claude Code implementation work.
  faithfulness: 1.0
- claim: Instruct the agent to maintain a notes.md file continuously during execution to record discoveries and technical findings as they emerge.
  faithfulness: 1.0
- claim: When facing obfuscated or very large files, spawn a focused subagent to decipher them rather than consuming the main session's remaining token context.
  faithfulness: 1.0
