---
name: RAG Master Series: Systematic RAG Design & Evaluation Patterns
technique: Build RAG systems with staged complexity, hybrid search, synthetic-data evals, and a data flywheel to iteratively improve retrieval before generation.
when_to_use: When designing or improving any RAG pipeline—from initial architecture through production monitoring.
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - evals
  - hybrid-search
  - data-flywheel
  - agent-patterns
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-08-10
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Combining vector search and full-text search (hybrid search) improves retrieval coverage beyond either method alone.
  faithfulness: 1.0
- claim: Applying date filters and including document metadata in search indexes addresses common retrieval gaps.
  faithfulness: 1.0
- claim: Automated RAG evaluation should cover six dimensions: retrieval quality, generation accuracy, relevance, citation validation, latency, and user satisfaction—treated like unit tests.
  faithfulness: 1.0
- claim: Building evaluation pipelines with synthetic Q&A pairs before production deployment provides baselines to guide optimization decisions.
  faithfulness: 1.0
