---
name: RAG Master Series: Complete Guide to Retrieval-Augmented Generation
technique: End-to-end RAG system design covering chunking, hybrid search, re-ranking, query understanding, evals, and improvement loops
when_to_use: When building or improving any retrieval-augmented generation system from prototype to production
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - hybrid-search
  - evals
  - chunking
  - query-understanding
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-07
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Combine vector search with BM25 full-text keyword search (hybrid search) to improve retrieval coverage over either method alone.
  faithfulness: 1.0
