---
title: "Design C — Industry SOTA 借鉴派"
date: 2026-05-12
agent: researcher (Haiku)
agent_id: a85efb062547cb0d9
philosophy: 借 7-8 个业界已验证 system 拼最优组合
cost_per_day: $0.25-0.35
new_files: 中等 (seed 10 wiki + scripts)
build_time: ~2 weeks + 2 weeks pilot
---

# Design C: Industry SOTA Borrowing for Daily Wiki/AI Ingestion

## Reference Systems Analyzed

### 1. arxiv-sanity-preserver (Karpathy)
Batch daily arxiv API poll → TF-IDF vectorization over abstracts → SVM-based similarity ranking. Single daemon, no LLM. Quality gate: relies on human curation and tags. Cost: negligible. Pitfall: TF-IDF is word-blind.

### 2. Papers With Code (PWC+)
Daily scheduled ingestion → parse paper metadata + code repos → LLM-powered classification + dataset matching. Multi-stage: backfill + incremental. Quality gate: LLM classification + human review queue. Cost: ~$0.02-0.05/paper. Pitfall: misses 30-40% of papers without code.

### 3. Stanford STORM
Multi-agent pipeline: perspective mining from Wikipedia → LLM expert agents simulate researcher dialogue → concurrent fetch from 20+ sources → outline synthesis → full article. Quality gate: **cited-only** — every claim must anchor to retrieved sources. Failure mode: Cannot produce "publication-ready" articles; admits ~30% require significant edits.

### 4. GPT Researcher
Planner → Executors (parallel crawlers on 20+ sources) → Publisher. Quality gate: **frequency consensus** — "choose most frequent information; chances all sources are wrong is extremely low." Cost: ~$0.10-0.30 per report. Pitfall: No explicit conflict detection; 12-15% of returned sources are paywalled.

### 5. TLDR (Daily Tech Newsletter)
Manual curation (human editors identify ~10-20 top stories/day) + LLM summary generation. Serves 1.6M readers. Quality gate: **human pre-filter** — editors read all stories, LLM only summarizes vetted. Cost: Human cost dominates (~$3-5k/day). Pitfall: Does not scale beyond boutique niches.

### 6. Obsidian Smart Connections + Smart Graph
Local embeddings (TaylorAI/bge-micro-v2, 384-dim) computed on every note → stored in `.smart-env/multi/` → semantic similarity retrieval. AI integration: Claude can query notes with block-level granularity via MCP. **No hallucination risk** (only retrieves existing notes). Pitfall: Requires manual note creation upstream.

### 7. Karpathy's LLM Wiki Pattern
Incremental wiki building: new papers → routing LLM decides if existing concept or new page → synthesis LLM writes/updates concept page with citations. Cost: **~100-200 Claude API calls per 50-paper corpus**; prompt caching reduces marginal cost. Efficiency: 95% fewer tokens than naive RAG. Pitfall: Ingest slow (~2 min/paper); loses nuance on multi-perspective topics.

### 8. Anthropic's Multi-Agent Research System
Orchestrator-worker pattern: central coordinator routes to specialist agents (researcher, fact-checker, integrator). Quality gate: fact-checker validates each claim. Internal only — no public codebase. Estimated cost: $0.50-2.00 per report. Pitfall: Coordination complexity.

## Design Patterns Extracted

| # | Pattern | From | Used in Javen's design |
|---|---|---|---|
| 1 | **Staged Verification** | STORM, GPT Researcher, Anthropic | Research → Quality gate → Synthesis phases |
| 2 | **Frequency-Based Consensus** | GPT Researcher, PWC+ | Aggregate 15-25 sources, consensus = signal |
| 3 | **Cited-Only Grounding** | STORM, Karpathy LLM Wiki | Every claim must have source URL |
| 4 | **Human Pre-Filter + AI Summarization** | TLDR | Humans curate scope; LLMs do scale work |
| 5 | **Embeddings-First Semantic Discovery** | Smart Connections | Local vector similarity, no API calls |

## Proposed: Javen-Adapted System

**Core philosophy**: _Minimize hallucination surface + maximize daily throughput + reuse Javen's existing launchd/subagent infra._

### Architecture

```
[Daily 03:00 UTC cron via launchd]
    ↓
[Intake Agent: Gather Sources (Pattern 4 human filter)]
  - Check vault for manual "daily watch list"
  - Query arxiv API: top papers (cat: cs.AI, cs.LG, last 24h)
  - Scrape 3-5 curated RSS feeds
  - Collect: ~40-60 sources/day
    ↓
[Routing Agent: Triage (Pattern 1 early gate)]
  - For each source: "new concept" or "existing concept update"?
  - Route to wiki/AI/ or notes/
  - Reject: duplicates, off-topic
  - Output: 15-20 high-signal sources
    ↓
[Synthesis Agent: Increment Wiki (Pattern 3 cited-only)]
  - For new concept → create source page notes/web-research/YYYY_topic.md
  - For existing → append to wiki/AI/concept.md
  - Rule: Every bullet ≥ 1 source URL
  - Prompt caching on repeated sys prompts (~20% reduction)
    ↓
[Semantic Indexing: Update Embeddings (Pattern 5)]
  - Recompute embeddings for modified pages
  - Smart Connections auto-discovers backlinks
    ↓
[Daily Digest (existing .claude/skills/ai-watch/)]
  - Generate "Yesterday's AI digest"
  - Push to inbox/daily
    ↓
[Log + Cost Tracking]
  - Append to MyBrain/system/logs/2026-05-XX.jsonl
```

## Quality Gates (Javen's "零容忍")

1. **Pre-synthesis Gate (Routing Agent)**:
   - Reject if arxiv abstract + title both mention "theoretical" but no experiment
   - Reject if RSS entry > 7 days old
   - Reject if clearly secondary source

2. **Post-synthesis Gate (Human Review)**:
   - Before wiki commit: Javen's approval queue
   - Javen sees: proposed concept title + first 3 bullets + source list
   - 1-click approves or rejects
   - Rejected → wiki/AI/disputed.md

3. **Citation Integrity Check (Automation)**:
   - Every generated bullet must contain ≥1 URL
   - URLs must be curl-checkable (not 404)
   - Fail-safe: if URL dead, mark `[BROKEN_LINK]`

4. **Frequency Consensus (multi-source)**:
   - If 3+ sources claim "X is true", confidence = high
   - If 1-2 sources claim X, flag as `[SINGLE_SOURCE]`

## Cost Estimate (Daily)

- Intake: arxiv API (free) + 3 RSS = $0.00
- Routing: 40-60 sources × Claude Haiku = $0.05
- Synthesis: 15-20 pages × 3 API calls (Haiku + caching) = $0.15-0.25
- Embeddings: local compute = $0.00
- Daily digest: 1 summary call = $0.01

**Total: ~$0.25-0.35/day = ~$90-130/year**

## Differences from Reference Systems

| System | Advantage | Why Javen's Differs |
|--------|-----------|-------------------|
| TLDR | human curation → zero hallucination | Javen wants auto-daily, not human-curated |
| GPT Researcher | 20+ source consensus | Overkill for niche AI topics |
| STORM | multi-perspective debate articles | Javen wants incremental wiki, not full articles |
| Karpathy's LLM Wiki | incremental page synthesis | **Borrowing this** + Javen's cited-only + approval gate |
| Obsidian Smart Connections | no hallucination (only retrieval) | Requires manual upstream; Javen wants auto |
| arxiv-sanity | low cost, fast | Misses semantic signals |

## Strengths vs Weaknesses

### Strengths
1. **Minimal hallucination surface** — cited-only + approval gate
2. **Reuses Javen's infra** — launchd cron + cost_tracker.py + vault git
3. **Cost sustainable** — $90-130/year
4. **Human still in control** — Javen approves each new concept
5. **Incremental cumulation** — wikis grow; old pages updated
6. **Semantic discovery** — Smart Connections embeddings find backlinks

### Weaknesses
1. **Routing agent SPOF** — if noisy, waste cycles. Mitigation: run twice; if confidence diverges, mark `[LOW_CONF]`
2. **Approval queue bottleneck** — if Javen has 20+/day to approve, defeats "daily auto". Mitigation: auto-approve if confidence ≥ 0.85; only human-review 0.60-0.85
3. **Cold start** — wiki structure must be pre-built. Mitigation: Create ~10-15 seed concepts by hand once
4. **Drift over time** — Synthesis agent might diverge from Javen's style. Mitigation: monthly review of wiki/AI/
5. **Missing OOD sources** — relies on arxiv + 3 RSS. Mitigation: Javen maintains manual "watch list"

## Next Steps for Javen

1. **Seed the wiki structure** — create ~10 concept pages in `wiki/AI/` with skeleton (title, placeholder bullets, empty backlinks)
2. **Define the "watch list"** — `wiki/AI/日常关注清单.md` listing 3-5 RSS feeds, Twitter, arxiv subcats
3. **Prototype Intake agent** — Python script, test on past 1 week of data
4. **Set approval queue SLA** — "I'll review daily digest 1x/day at 09:00 UTC"
5. **Run pilot for 2 weeks** — launchd daemon runs; Javen approves/rejects each morning
6. **Integrate Smart Connections** — after wiki stabilizes (~100 pages), enable Smart Graph
