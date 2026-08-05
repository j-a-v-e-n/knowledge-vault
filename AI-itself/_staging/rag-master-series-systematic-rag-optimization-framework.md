---
name: RAG Master Series: Systematic RAG Optimization Framework
technique: Prioritize retrieval quality over generation using hybrid search, synthetic evals, re-ranking, query understanding, and a data flywheel loop
when_to_use: When building or improving a production RAG system and needing a structured order of operations to diagnose and optimize it
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - hybrid-search
  - re-ranking
  - query-understanding
  - evals
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-05
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Combining vector search with full-text (keyword) search is a low-hanging fruit optimization that often outperforms complex architectural changes.
  faithfulness: 1.0
- claim: Re-ranking is applied as a post-retrieval filtering step to improve relevance of the initial candidate set.
  faithfulness: 1.0
- claim: A RAG system requires six core evaluations: retrieval quality, generation accuracy, relevance assessment, citation validation, latency measurement, and user satisfaction.
  faithfulness: 1.0
