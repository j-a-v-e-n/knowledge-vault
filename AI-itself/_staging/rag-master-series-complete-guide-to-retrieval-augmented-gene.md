---
name: RAG Master Series: Complete Guide to Retrieval-Augmented Generation
technique: Systematic RAG pipeline construction combining hybrid search, query understanding, re-ranking, citation attribution, and layered evaluation into a continuously improving data flywheel
when_to_use: When building or auditing a retrieval-augmented generation system that needs production-grade retrieval quality, measurable accuracy, and iterative improvement from user signals
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - hybrid-search
  - re-ranking
  - evals
  - chunking
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-31
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Hybrid search combines vector and full-text search to improve coverage beyond what either single-modality approach achieves alone.
  faithfulness: 1.0
- claim: Re-ranking as a post-retrieval step improves relevance of results returned by the initial search pass.
  faithfulness: 1.0
- claim: Six core RAG evaluations cover retrieval quality, generation accuracy, relevance, citation validation, latency, and user satisfaction.
  faithfulness: 1.0
