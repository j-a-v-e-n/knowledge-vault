---
name: RAG Master Series: Compound RAG Optimization Patterns
technique: Systematically improve RAG systems by addressing retrieval, ranking, and generation phases in sequence, using synthetic data baselines and a data flywheel for continuous evaluation.
when_to_use: When building or scaling a RAG pipeline and needing a structured framework to diagnose failures, prioritize improvements, and measure progress.
source: "https://jxnl.co/writing/2025/09/11/rag-series-index/"
tags:
  - ai-usage
  - ai-digest
  - rag
  - retrieval
  - evaluation
  - hybrid-search
  - data-flywheel
  - reranking
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-07-22
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: Generating synthetic question-answer pairs from the knowledge base before production deployment establishes a measurable baseline for retrieval quality.
  faithfulness: 1.0
- claim: Six core evaluation dimensions for RAG are: retrieval quality, generation accuracy, relevance, citations, latency, and user satisfaction.
  faithfulness: 1.0
- claim: Evaluation suites should be run automatically on every system change, analogous to unit tests in software development.
  faithfulness: 1.0
