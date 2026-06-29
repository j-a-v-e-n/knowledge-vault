---
name: Semantic Cross-Session Memory for LLM Agents
description: Pattern for persisting agent context across sessions using embedding-based retrieval; covers when flat files suffice vs when semantic search is needed, and how to avoid the tool-bloat trap.
tags:
  - ai-usage
  - ai-digest
  - memory
  - cross-session
  - semantic-search
  - embeddings
  - mcp
source: "https://news.ycombinator.com/item?id=45516584"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Semantic Cross-Session Memory for LLM Agents

## What
Instead of re-loading a full history into every new conversation (which hits context limits), store important decisions, patterns, and directives as embedded vectors in an external store. On each new session, retrieve only the semantically relevant subset — e.g., top-5 most similar memories — and inject them into context. This gives a stateless LLM continuity across sessions without blowing up the context window.

## When to use
- Long-running projects where architectural decisions, constraints, or directives must carry forward across sessions
- When accumulated notes exceed roughly 100KB — below that threshold, a flat markdown file loaded directly is simpler and works fine
- When you need isolation between unrelated projects (preventing context bleed)
- Skip it for short or one-off projects; the operational overhead isn't worth it

## How it works
1. During a session the agent stores notable context — decisions, patterns, standing constraints — as structured memory objects with type labels (e.g., directive, decision, pattern)
2. Each memory is embedded with a text-embedding model and written to an external store (Redis, vector DB, etc.) with metadata
3. At the start of each new session a semantic search retrieves the top-k memories most relevant to the current context
4. Retrieved memories are injected into the system prompt or early context, giving the agent continuity without replaying full history

Key design choices:
- **Type taxonomy**: classifying memories by kind (directives vs. decisions vs. patterns) improves retrieval precision
- **Workspace isolation**: scope memories per project so unrelated context doesn't pollute retrieval
- **Minimal tool surface**: expose 1–3 well-designed retrieval tools, not 20+. Every tool definition consumes context tokens; too many tools create the very bloat you were trying to solve

## Caveats
- LLMs do not reliably self-trigger memory storage or retrieval without explicit instructions in the system prompt — you must tell the agent when and what to save, and when to query
- Tool-count overhead is real: a large tool roster adds its own token cost, which can partially or fully negate the savings from selective retrieval
- Native memory features (e.g., Claude's built-in `/memory` command) now cover many simpler use cases without additional infrastructure
- Redis is workable but purpose-built vector stores (pgvector, Qdrant, Pinecone) offer better approximate nearest-neighbor search at scale
- Adds an external dependency and operational surface area; validate that the retrieval efficiency gain justifies the complexity before building it

---
*Source: https://news.ycombinator.com/item?id=45516584. Distilled by the AI-itself digest — review before blessing.*
