### Bug Description

There are two issues with the memory/skill nudge trigger logic:

1. Nudge Counter Reset on Interruption/Failure : When a memory/skill review opportunity is lost due to an empty final_response or an interruption, the memory/skill nudge counters are reset and need to restart accumulation from scratch.
2. Duplicate Memory Reviews : Duplicate memory reviews occur when _should_review_memory is true while the agent is calling a memory tool within the tool execution loop.

### Steps to Reproduce

### Issue 1: Counter Reset on Interruption
1. Set _memory_nudge_interval = 2
2. Have 1 conversation turn (counter becomes 1)
3. Start a second conversation but interrupt or fail it
4. Counter is reset to 0 instead of preserving the state
5. Need to have 2 more conversation turns to trigger the nudge again 
### Issue 2: Duplicate Memory Reviews
1. Set _memory_nudge_interval = 2
2. Have 1 conversation turn (counter becomes 1)
3. In the second turn, manually call the memory tool
4. Duplicate memory review can be triggered

### Expected Behavior

1. Nudge counters should only be reset when we are actually going to spawn a background review process, not just at the start of a conversation. This way, if a conversation is interrupted or fails, the counter state is preserved and the nudge will trigger on the next successful conversation.
2. Memory nudge checks should happen after tool calls to avoid duplicate reviews when the agent calls memory tools manually.

### Actual Behavior

1. Memory nudge check happens at the start of the conversation, and counters are reset unconditionally.
2. When _should_review_memory is true and the agent calls a memory tool within the execution loop, duplicate memory reviews occur.

### Affected Component

Agent Core (conversation loop, context compression, memory)

### Messaging Platform (if gateway-related)

_No response_

### Debug Report

```shell
N/A
```

### Operating System

macOS 26.3

### Python Version

3.11

### Hermes Version

0.10.0

### Additional Logs / Traceback (optional)

```shell

```

### Root Cause Analysis (optional)

_No response_

### Proposed Fix (optional)

_No response_

### Are you willing to submit a PR for this?

- [x] I'd like to fix this myself and submit a PR
