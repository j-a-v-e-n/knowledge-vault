---
name: Sleep-Time Compute: Async Memory Infrastructure for Agents
description: Process agent traces offline between sessions to extract and persist structured memory — decouples long-term retention from real-time context management; use for multi-session or multi-agent systems where context windows can't hold full history.
tags:
  - ai-usage
  - ai-digest
  - agent-memory
  - async
  - harness-pattern
  - multi-agent
  - context-management
source: "https://www.latent.space/p/ainews-its-meta-harness-summer"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Sleep-Time Compute: Async Memory Infrastructure for Agents

## What
Sleep-time compute is an architectural pattern that treats agent memory as an asynchronous infrastructure concern rather than a context-window problem. Conversation traces and action logs are written to a store during a session, then a separate offline worker processes them between sessions — extracting structured facts, deduplicating, reconciling conflicts, and writing the result back to persistent memory. Future sessions pull from this store rather than from raw conversation history.

A complementary pattern from the same source: replace static per-agent permissions (which don't scale) with capability-based, task-scoped access — each agent invocation receives only the minimal credentials needed for that specific task, granted dynamically.

## When to use
- Multi-session agents where a single context window can't hold full history
- Multi-agent systems that need a shared, consistent knowledge base
- Any loop where the agent should improve from past runs without retraining
- Deployments where audit trails and revocable access are required

## How it works
1. During each session, log all traces — tool calls, observations, decisions, errors — to a durable store.
2. After the session ends, a memory worker runs asynchronously (not in the hot path): it reads new traces, extracts key facts and patterns, deduplicates against existing memory, and resolves conflicts.
3. Structured memory (e.g., markdown files, JSON records, embeddings) is written back to persistent storage.
4. At session start, retrieve relevant memory chunks (keyword match or semantic search) and inject into the agent's context.
5. For permissions: define a capability broker that grants task-scoped credentials at invocation time rather than assigning broad standing permissions to an agent identity.

## Caveats
- The memory worker's extraction quality is bounded by trace quality — noisy traces produce noisy memory.
- Conflict reconciliation across multiple agents or sessions writing contradictory facts is non-trivial and needs explicit logic.
- Sleep-time compute introduces a lag between a session ending and the learning being available; not suitable for within-session adaptation.
- Capability-based permissioning adds an infrastructure dependency (a broker that issues scoped credentials); don't underestimate the implementation cost.
- Static per-agent identity can create tacit-knowledge lock-in and budget opacity — the article notes this as a known failure mode of simpler embedding approaches.

---
*Source: https://www.latent.space/p/ainews-its-meta-harness-summer. Distilled by the AI-itself digest — review before blessing.*
