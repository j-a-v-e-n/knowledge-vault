---
name: Living Documentation for Multi-Session Agent Continuity
technique: Maintain named markdown files (notes.md, plan.md, research.md) that agents both read and update each session, preserving accumulated context across multi-session agent work without repeating it in prompts
when_to_use: Any multi-session or multi-agent project where context would otherwise be lost between sessions, or when handing off work between agent instances
source: "https://simonwillison.net/2026/Jun/22/porting-moebius/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - agent-coordination
  - multi-session
  - context-management
  - handoffs
  - prompting
verified: true (every claim sentence-backed by an independent fresh context)
verified_at: 2026-06-29
audience: AI
---
#ai-digest

## claims (each backed by an exact source sentence)
- claim: Saving research outputs from one agent session as markdown files makes them available as structured input for downstream agent sessions or subagents
  source_sentence: "I copied out the last answer and saved it as research.md for Claude Code to read later."
- claim: Subagent delegation for subsidiary analysis tasks (e.g., analyzing obfuscated code) avoids consuming top-level agent context tokens on tangential work
  source_sentence: "That project was entirely obfuscated, built JavaScript files so I figured using a subagent would avoid spending the rest of my top-level token context deciphering those files."
