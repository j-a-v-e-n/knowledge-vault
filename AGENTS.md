# Agent Rules — Entry Point

This file exists for cross-agent compatibility (Codex, Cursor, Aider, etc.).

**All agents working in this vault MUST read `MyBrain/CLAUDE.md` as the primary rule file.**

That file contains:
- Vault architecture (raw/ notes/ wiki/ inbox/ archive/ rules)
- Owner mindset interaction protocol
- Memory Commit Protocol (cross-session fact persistence)
- Quality bars (truthfulness, no-second-hand-source, paper-data accuracy zero-tolerance)
- File-handling protocols (auto-open generated files, osascript activate)
- Task board system (`MyBrain/automation/queue/task-board.md`)
- Approval queue (`MyBrain/automation/queue/approvals.md`)
- Lessons + checklists (`MyBrain/automation/docs/lessons.md`)

Do NOT maintain duplicate rules here. This file is a stub pointer.

If you are Claude Code, root `CLAUDE.md` already imports `MyBrain/CLAUDE.md` automatically.
If you are any other agent, read `MyBrain/CLAUDE.md` before any work.
