---
name: RAG System Design: Retrieval-First Methodology with Data Flywheel
technique: Prioritize retrieval quality over generation quality in RAG systems, using synthetic data for evals and a data flywheel to compound improvements over time
when_to_use: When building or improving any RAG pipeline where response quality is poor and the root cause is unknown
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - evals
  - hybrid-search
  - synthetic-data
  - data-flywheel
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-03
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Most teams spend too much time on generation quality before ensuring retrieval works correctly — fix retrieval first.
  faithfulness: 1.0
- claim: Start evaluation with retrieval metrics using synthetic question-answer pairs before production data is available.
  faithfulness: 1.0
- claim: Basic improvements like date filters and hybrid search (combining vector + full-text) often outperform complex architectural changes.
  faithfulness: 1.0
- claim: Six core RAG evaluation dimensions are: retrieval quality, generation accuracy, relevance, citation validation, latency, and user satisfaction.
  faithfulness: 1.0
