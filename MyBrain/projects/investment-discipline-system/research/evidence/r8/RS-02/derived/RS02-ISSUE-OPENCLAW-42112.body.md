## Summary
On **OpenClaw 2026.3.8**, a persisted session can become unrecoverable if an assistant `toolCall` is written without the required immediate matching `toolResult`. Once that happens, later turns on the same session are rejected by the model provider, and the chat agent appears down until the bad session file is manually quarantined or reset.

This was observed on a **Telegram direct-chat agent** using **`openai-codex/gpt-5.4`**.

This does **not** look like a brand-new bug class. It appears to be a still-unfixed / newly resurfaced variant of the orphaned `tool_use` / `tool_result` session-corruption family.

## Environment
- **OpenClaw version:** 2026.3.8
- **OS:** macOS arm64
- **Channel:** Telegram
- **Agent/session type:** main direct-chat agent (`main-telegram`)
- **Model involved at time of incident:** `openai-codex/gpt-5.4`

## User-visible symptom
The Telegram bot stopped replying after a prompt that triggered memory lookup. Telegram transport remained healthy; the failure was in session replay.

## Concrete failure
The persisted session ended with:
1. assistant `toolCall: read`
2. matching `toolResult` for `read`
3. assistant `toolCall: memory_search`
4. **no matching `toolResult` persisted**

On the next run, the provider rejected the replayed history.

### Exact error seen
```text
LLM request rejected: messages.29: `tool_use` ids were found without `tool_result` blocks immediately after: call36902724. Each `tool_use` block must have a corresponding `tool_result` block in the next message.
```

## Evidence
### Session evidence
Affected persisted session contained:
- user asks for memory/vector/notes token search
- assistant issues `read`
- `toolResult` recorded for `read`
- assistant issues `memory_search`
- no subsequent `toolResult`

### Gateway evidence
Gateway error log recorded:
```text
[agent/embedded] embedded run agent end: ... isError=true error=LLM request rejected: messages.29: `tool_use` ids were found without `tool_result` blocks immediately after: call36902724 ...
```

### Transport was not broken
Telegram sends succeeded both:
- before the failure
- immediately after manual quarantine of the bad session and gateway restart

So this was **not** a Telegram outage.

## Why this matters
The failure mode is bad for operators because:
- the channel still looks healthy
- the gateway service is still running
- the bot simply stops replying
- the poisoned session keeps failing until manually removed

## Likely root cause
OpenClaw’s session persistence / recovery path appears able to durably record an assistant `toolCall` without guaranteeing that the corresponding `toolResult` is also durably present in the next message block.

That leaves the session in a replay-invalid state for providers/models that strictly enforce tool-call sequencing.

## Why this looks systemic, not one-off
The same class of error appears multiple times in historical logs with different tool-call IDs, so this looks like a recurring integrity bug rather than a single damaged file.

## Expected behavior
If a persisted session is structurally invalid due to an orphaned tool call, OpenClaw should detect and recover automatically rather than repeatedly replaying poisoned history.

## Actual behavior
OpenClaw reuses the corrupted session, the provider rejects replay, and the agent stops responding until manual intervention.

## Manual workaround used
1. back up the bad session file
2. move it out of the active session directory
3. remove stale lock file
4. restart gateway

That restored replies immediately.

## Suggested fixes
### 1. Add replay integrity validation
Before replaying a persisted session, validate:
- every assistant `toolCall` has immediate matching `toolResult`
- no dangling tool-call IDs
- no assistant tool-call block at EOF without result

If invalid:
- quarantine the session automatically, or
- truncate the invalid tail safely, or
- rotate to a fresh session

### 2. Make tool persistence atomic
Do not durably persist assistant `toolCall` state unless the corresponding tool-result transition can also be committed safely.

### 3. Auto-heal on this exact error
On:
```text
tool_use ids were found without tool_result blocks immediately after
```
automatically:
- mark session corrupted
- preserve backup
- open fresh session
- continue service

### 4. Improve diagnostics
Include in logs:
- session key
- session file path
- offending tool call ID
- whether quarantine/rotation was attempted

## Related prior issues / PRs
This report appears related to prior work in the same area:
- #37834 — Session context corruption: orphaned tool_use ID causes permanent 400 loop after abort
- #26936 — orphan tool_use persisted to session .jsonl after rate limit retry exhaustion
- #19048 — Auto-repair orphaned tool_use blocks in session history
- #33621 — Anthropic rejects history with dangling tool_use blocks after compaction
- #27804 — Session compaction breaks tool_use/tool_result pairing, causing 400 API errors
- #40416 — Post-compaction message serialization drops tool_result blocks → permanent session death
- #20980 — pair-atomic tool_use/tool_result commit

## Severity
High for interactive agents:
- causes apparent bot outage
- difficult to distinguish from transport problems
- recurring across sessions/log history

