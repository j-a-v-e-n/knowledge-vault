---
name: Multi-Session Agent Continuity via Living Documentation
description: Have agents maintain notes/plan/research files written as briefings for the next agent session — use when a project spans multiple conversations and you need context persistence without re-explaining from scratch.
tags:
  - ai-usage
  - ai-digest
  - agent-coordination
  - context-management
  - multi-session
  - documentation
  - handoff
source: "https://simonwillison.net/2026/Jun/22/porting-moebius/#atom-everything"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Multi-Session Agent Continuity via Living Documentation

## What

For projects that span multiple agent sessions, have the agent maintain dedicated documentation files (`notes.md`, `plan.md`, `research.md`) written explicitly as context for the *next* session — not as internal scratch, but as a structured briefing for a successor agent. Combined with feasibility-first prompting and subagent isolation, this creates continuity across conversations without re-explaining from scratch.

## When to use

- Projects that span more than one conversation or context window
- When you want to resume work later without losing design decisions and documented dead-ends
- When delegating a complex multi-stage task where intermediate research findings matter
- Before starting a new agent session on an ongoing project, point the agent at these docs as the first context item

## How it works

1. **Pre-stage research artifacts before execution.** Before asking for implementation, provide a `research.md` summarizing prior analysis: "Read ./research.md — your goal is to port X." This narrows the search space immediately and prevents the agent from re-deriving what's already known.

2. **Feasibility-first exploratory prompting.** Before committing to implementation, ask the agent to think through the approach (e.g., "muse on the feasibility of porting X to Y") rather than jumping to code. This extracts strategic reasoning and surfaces blockers before resources are spent.

3. **Subagent isolation for complex sub-tasks.** When a specific analysis (e.g., understanding a reference implementation) would pollute the main context, explicitly dispatch it: "use a subagent to look at /tmp/reference-project and report how they handle Y." The main context stays clean; findings return as a summary.

4. **Agent-maintained living docs.** Instruct the agent to keep `notes.md` / `plan.md` updated throughout the session, written as if briefing a successor. These become both debugging artifacts and structured handoffs for the next session.

5. **Post-hoc learning after delegation.** After a heavy-delegation session where you skipped code review, make a separate follow-up query: "teach me everything about the approach you just implemented." This recovers understanding without re-doing the work.

## Caveats

- Living docs only work if explicitly built into the task prompt — agents won't maintain them automatically unless instructed.
- Subagent isolation adds overhead; worthwhile only when the sub-task is genuinely complex and self-contained.
- Post-hoc learning is a partial fix for knowledge gaps from over-delegation; if understanding the implementation matters, incremental review is better.
- The overhead of this pattern is only justified for non-trivial, multi-session projects — short single-session tasks don't need it.

---
*Source: https://simonwillison.net/2026/Jun/22/porting-moebius/#atom-everything. Distilled by the AI-itself digest — review before blessing.*
