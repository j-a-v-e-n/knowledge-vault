## Bug Description

The gateway memory flush mechanism (gateway/run.py lines ~520-567) spawns a temporary AIAgent on session reset/inactivity timeout/gateway restart that reviews old conversation history and writes to MEMORY.md. This flush agent has no awareness of memory changes made since that conversation occurred — by the live agent, by other sessions, or by cron jobs — and silently overwrites them.

The result: an agent carefully curates its memory during a session, the gateway restarts (or a session times out), and the flush agent reverts memory to whatever it thinks is important from stale context. The agent's own memory decisions are discarded.

## Reproduction

1. Start a gateway session, have the agent write specific memory entries via the `memory` tool
2. Confirm entries are persisted to `~/.hermes/memories/MEMORY.md` on disk
3. Restart the gateway (`systemctl --user restart hermes-gateway`)
4. Check MEMORY.md — entries written by the live agent are overwritten or reverted by the flush agent

## Root Cause

`gateway/run.py` `_flush_memories_for_session()` (line ~507):
- Creates a temporary `AIAgent` with `enabled_toolsets=["memory", "skills"]`
- Feeds it the old conversation history
- Prompts it: "Review the conversation above and save any important facts to memory"
- The flush agent then calls the `memory` tool with `replace`/`add` actions based on **stale context**
- No timestamp comparison, no conflict resolution, no awareness of concurrent writes

Additionally, `_start_session_expiry_watcher()` (line ~1017) triggers proactive memory flushes before sessions expire — same mechanism, same problem.

## Impact

- Agent memory is unreliable — entries revert unpredictably after restarts
- Cron job memory writes are overwritten by flush agents reviewing unrelated sessions  
- Multi-agent setups are especially affected since gateway restarts on either machine trigger flushes
- Users lose trust in the memory system when entries they confirmed were saved disappear
- The agent's own curation decisions are overridden by a context-less temporary agent

## Observed Pattern

Two independent agents on separate machines both exhibited: working correctly → gateway restart → memory reverted to stale state. Confirmed via:
- md5sum tracking of MEMORY.md before/after restart
- Canary entries that disappeared post-restart
- Cron session logs showing memory tool calls from flush agents
- 566 cron sessions accumulated in state.db, each potentially triggering flushes

## Suggested Fix

Options (not mutually exclusive):
1. **Timestamp-based conflict resolution**: Memory entries should carry last-modified timestamps. Flush agent should not overwrite entries newer than the conversation it is reviewing.
2. **Read-only flush**: The flush agent should only ADD entries, never REPLACE or REMOVE existing ones.
3. **Opt-out config**: `memory.flush_on_reset: false` in config.yaml for users/agents that manage their own memory.
4. **Disable flush for cron sessions**: Cron sessions should never trigger memory flushes — they run headless with different context than the primary agent.
5. **Require explicit consent**: Instead of silent flush, show the user what the flush agent wants to write and let them approve.

## Environment

- Hermes Agent: latest (installed via git at ~/.hermes/hermes-agent)
- Platform: Gateway mode (Telegram + Discord)
- Model: claude-opus-4-6 (Anthropic)
- OS: Ubuntu, two-machine setup
- Config: 10 cron jobs, 151 skills, persistent memory enabled
