---
title: audit.sh changelog 2026-05-16
type: overview
created: 2026-05-18
---

# audit.sh Schema Update 2026-05-16

## What changed

`.claude/hooks/audit.sh` now logs 3 additional optional fields:

- `subagent_type`: captured from Agent tool `tool_input.subagent_type` (e.g., "reviewer")
- `description`: captured from Agent tool `tool_input.description`, truncated to first 200 chars
- `bash_command`: captured from Bash tool `tool_input.command`, truncated to first 200 chars

These fields enable Path 1 test-plan-metrics.sh to measure compliance with 5/16 "2 agent" rule.

## Backwards compatibility

Additive schema extension. Existing log consumers unaffected:
- Base fields (`ts`, `event`, `tool`, `file`, `session`, `cwd`) unchanged
- Optional fields appear only when tool provides them
- Old logs without these fields remain valid

## New schema fields

```jsonl
{"ts":"2026-05-18T22:02:14-07:00","event":"PostToolUse","tool":"Agent","file":"","session":"test","cwd":"/test","subagent_type":"reviewer","description":"audit file X for errors"}
{"ts":"2026-05-18T22:02:19-07:00","event":"PostToolUse","tool":"Bash","file":"","session":"test","cwd":"/test","bash_command":"echo 'test' > file.md"}
```

## Files modified

- `.claude/hooks/audit.sh`: schema extension
- `MyBrain/automation/scripts/test-plan-metrics.sh`: NEW - compliance measurement script
