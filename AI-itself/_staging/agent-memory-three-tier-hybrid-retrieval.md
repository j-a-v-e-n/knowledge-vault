---
name: Three-Tier Agent Memory with Hybrid Retrieval
description: Cognitive-science-grounded pattern for persistent agent memory using episodic/semantic/procedural tiers, hybrid BM25+vector retrieval with RRF, and supersession-based fact updates — use whenever an agent needs long-term, per-user memory across sessions.
tags:
  - ai-usage
  - ai-digest
  - agent-memory
  - rag
  - hybrid-retrieval
  - rrf
  - long-term-memory
source: "https://lobste.rs/s/inzoi4/agent_memory_on_elasticsearch_hybrid"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Three-Tier Agent Memory with Hybrid Retrieval

## What

A persistent agent memory architecture that borrows from cognitive science: three separate memory tiers with distinct lifecycles and retrieval behaviors, combined with a two-stage hybrid search pipeline that fuses keyword and semantic recall.

## When to use

- Agent needs to remember user-specific facts, past interactions, or learned procedures across sessions
- Simple conversation history in the system prompt grows too large or too stale
- Multiple users share the same agent and memory must be isolated per-tenant
- Facts change over time and you need contradiction handling without losing audit trail

## How it works

### Three memory tiers

**Episodic** — raw, timestamped interaction logs written immediately before the LLM responds (hot-path, high volume, short half-life). Serves as the raw material that gets consolidated into the other tiers.

**Semantic** — stable, distilled assertions about a user (e.g. "user owns a MacBook", "user is in Seattle"). Extracted from episodic episodes by a consolidation step; survives sessions; decays slowly. Has a `last_used_at` field that resets on every recall, so actively-used facts stay fresh.

**Procedural** — multi-step how-to playbooks with `success_count` / `failure_count` tracked per playbook. Ranked by effectiveness, not recency. Exempt from time-decay; governed by outcome history instead.

### Hybrid retrieval pipeline

Two-stage retrieval runs on the verbatim user message (not a paraphrase) before the LLM sees the turn:

1. **Candidate expansion**: BM25 (keyword) and dense-vector (semantic) each return ~80 candidates. Reciprocal Rank Fusion (RRF) merges them into a single list without requiring score calibration across the two systems. BM25 is kept because it preserves exact strings — version numbers, error codes, proper nouns — that dense vectors smooth away.
2. **Reranking**: A cross-encoder scores query–document pairs jointly on the narrowed candidate set. More expensive per pair but far more accurate than bi-encoder similarity; affordable because the pool is already small.

### Consolidation loop

After each turn (or on a background schedule in production), a consolidation LLM call receives recent episodes plus existing facts and playbooks, then outputs: new semantic facts with back-references to supporting episode IDs, new or updated playbooks with refined steps. A dedup pass via hybrid search suppresses near-duplicates above a similarity threshold before writing.

### Supersession instead of deletion

When a user's new statement contradicts a stored fact, the agent does not delete the old fact. Instead it writes a new document with a `supersedes_id` pointer and updates the old document with `superseded_by`. All retrieval filters exclude documents that have a `superseded_by` field, so the old fact disappears from queries while the audit chain remains intact. Harsh contradictions also reduce the new fact's confidence score via a penalty constant.

### Scoring at retrieval time

Two multipliers applied via a script inside the query:
- **Time decay**: Gaussian curve with a ~180-day flat zone (no penalty for recent docs) and a ~5-year half-life. Episodic uses write timestamp; semantic uses `last_used_at`, which resets on every recall — frequently-recalled facts self-renew.
- **Use-count boost** (semantic only): `1 + log10(1 + use_count) * weight`. Logarithmic so a heavily-used fact gets a modest boost, not a runaway advantage.

### Agent-coordination hooks

- **Pre-recall hook**: Every turn triggers a `recall_memory` call on the raw user message before the agent's reasoning starts. Avoids the failure mode where the agent paraphrases the query and strips the exact keywords BM25 relies on.
- **Unified tool**: A single `recall_memory` tool spans all tiers simultaneously; the retrieval layer handles routing and blending. The agent does not need to know which tier to query — reduces prompt complexity and agent decision load.
- **Same-turn visibility**: Memory writes force an index refresh and wait for embedding inference to complete before returning. This ensures that if a user mentions a new fact and then asks about it in the same turn, the agent can immediately recall what it just wrote.

### Multi-tenant isolation

Document-level security (DLS) at the storage layer restricts each retrieval query to documents owned by the requesting user or shared (no owner). A redundant application-level `user_id` filter provides a second guard against misconfiguration. Shared catalog data is admitted by widening the DLS predicate, with a gentle prior that slightly favors personal memory over catalog on near-ties.

## Caveats

- **Consolidation cost**: Running a full LLM consolidation call every turn is expensive; in production this should move to a background job, accepting a small lag before episodes become semantic facts.
- **Reranker latency**: Cross-encoder reranking adds a synchronous step; tune the candidate pool size to balance recall vs. latency.
- **Dedup threshold is fragile**: The 0.90 similarity cutoff for duplicate suppression is empirically chosen; too high and near-duplicates accumulate, too low and valid updates get suppressed.
- **Procedural memory scoring is incomplete**: The source explicitly notes that success/failure count–based ranking for procedural memory is not yet wired into the retrieval scoring — it is tracked but not yet used for ranking.
- **Episodic collision risk**: Because episodic entries capture full message text, sibling episodes (same session, similar messages) cause retrieval collisions that lower R@10 for that tier; this is a known tradeoff of high-volume raw logging.
- **Elasticsearch-specific**: DLS, Painless scripts, and `semantic_text` field type are Elasticsearch features; the conceptual patterns (tiers, RRF, supersession) transfer to any vector store, but the exact implementation does not.

---
*Source: https://lobste.rs/s/inzoi4/agent_memory_on_elasticsearch_hybrid. Distilled by the AI-itself digest — review before blessing.*
