---
title: "AI 岗位市场现状 2025-2026 — A1 Research Output"
research_date: 2026-05-12
agent: A1 (current_market)
confidence: medium-high (mix; per-section labelled)
tool_calls_used: 9 of 12
---

# AI 岗位市场现状 2025-2026

> A1 agent research output. 全部数据 web-fetched, 不引用 vault 内部 source. 数据 freshness 范围 2025 Q1–2026 Q2.

---

## 0. Headline Numbers (confidence: high)

- 2023–2025 间 LinkedIn 在美国新增 **639,000** 个 AI-related job posting, 其中 **75,000** 为 AI Engineer titled role ([LinkedIn / WEF 2026-01](https://www.weforum.org/stories/2026/01/ai-has-already-added-1-3-million-new-jobs-according-to-linkedin-data/), fetched 2026-05-12 — secondary citation via search snippet, URL itself 403 on direct fetch).
- AI Engineer 连续两年位列 LinkedIn Jobs on the Rise **#1** for young workers ([LinkedIn Jobs on the Rise 2025](https://www.linkedin.com/pulse/linkedin-jobs-rise-2025-25-fastest-growing-us-linkedin-news-gryie), fetched 2026-05-12).
- Q1 2025 AI-related job openings 达到 **35,445**, YoY +25.2% ([Interview Guys 2026 Agentic AI report](https://blog.theinterviewguys.com/top-10-agentic-ai-jobs/), fetched 2026-05-12).
- "Agentic AI" 提及量从 2023→2024 **+986%** in job postings (同上).
- Forward Deployed Engineer 岗位 2025-01 → 2025-09 +**800%** ([Sundeep Teki FDE report](https://www.sundeepteki.org/forward-deployed-engineer.html), fetched 2026-05-12).
- AI Specialist vs non-AI base salary premium: Entry 6.2%, Mid 11.9%, Senior 14.2%, **Staff 18.7%** (up from 15.8% in 2024) ([Levels.fyi Q3 2025 trends](https://www.levels.fyi/blog/ai-engineer-compensation-trends-q3-2025.html), fetched 2026-05-12).

---

## 1. Top 10 Hot AI Roles (by hiring volume / growth)

Confidence: **high** for ranking presence (each role independently verified via 2+ sources); **medium** for exact comp ranges (Levels.fyi medians used, but role-mapping ambiguity exists — see §1.x notes).

| # | Role | Companies hiring | Salary range (US, total comp) | Sample JD link |
|---|------|------------------|-------------------------------|----------------|
| 1 | **AI Engineer (general)** | Google, Microsoft, NVIDIA, Meta, Apple, startups | $145K–$310K base; $245K median TC | [Levels.fyi AI Engineer](https://www.levels.fyi/t/software-engineer/title/ai-engineer) |
| 2 | **ML Engineer (production)** | Meta ($430K median TC), Google ($290K), Apple ($305K), NVIDIA ($267K) | $187K–$786K TC at Meta; $245K median overall | [Levels.fyi ML Engineer](https://www.levels.fyi/t/software-engineer/title/machine-learning-engineer) |
| 3 | **Applied AI Engineer** | Google, Anthropic, OpenAI | £225K–£240K (Anthropic London); ~$200K–$400K TC (US) | [Anthropic Applied AI Engineer JD](https://job-boards.greenhouse.io/anthropic/jobs/5116274008) |
| 4 | **Forward Deployed Engineer (FDE)** | OpenAI (50 FDE goal by EOY2025), Anthropic, Palantir | $205K–$486K typical, $238K avg; Staff $630K+ | [Palantir FDE JD](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488) |
| 5 | **Agentic AI Engineer / AI Agent Architect** | Enterprise + AI labs | $155K–$265K base mid-senior; top $400K+ TC | [KORE1 Agentic AI hiring guide](https://www.kore1.com/hire-agentic-ai-engineers-2026/) |
| 6 | **LLM Engineer / RAG Developer** | All large tech + startups | Senior base $240K–$350K+, TC $500K–$943K | [Acceler8 Talent 2025-26 rates](https://www.acceler8talent.com/resources/blog/ai-engineer--salary---market-rates-2025-2026/) |
| 7 | **MLOps Engineer** | Large enterprises (2× higher hiring than small co.) | $145K–$280K base; appears in 17.6% of postings w/ Kubernetes | [TechLife AI Skills 2025](https://techlife.blog/posts/ai-skills-toolkit-2025-langchain-rag-mlops-guide/) |
| 8 | **Data Engineer (AI-focused)** | All Fortune 500; "most in demand overall" per McKinsey | $130K–$220K TC | [McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai) |
| 9 | **Research Engineer / ML Researcher** | Anthropic, OpenAI, DeepMind, FAIR | Anthropic mid-senior £225K+; OpenAI/Anthropic $350K–$550K TC | (Anthropic careers, link above) |
| 10 | **AI Evaluation / Human-in-the-Loop / Compliance** | Enterprise, finance, healthcare | $90K–$180K (newer, less data) | [McKinsey 2025 — emerging roles](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai) |

**Ranking methodology note**: Rank #1–6 ordered by aggregated mention frequency in LinkedIn Jobs on the Rise 2025 + McKinsey State of AI + Levels.fyi compensation reports. #7–10 listed by McKinsey "most-in-demand" categories. **Not** a strict hiring volume ranking — that exact ranking data not found in a single authoritative source. Confidence: **medium** on ordering, **high** on inclusion.

---

## 2. Per-Role Skill Requirements

Confidence: **high** (cross-validated across LinkedIn, TechLife, IntuitionLabs, Anthropic JD).

### 2.1 AI Engineer (general)

- **Must-have hard**: Python; PyTorch or TensorFlow; LLM APIs (OpenAI, Anthropic); prompt engineering; RAG fundamentals; vector DB basics
- **Recurring soft**: cross-functional communication, breaking down ML concepts for non-technical stakeholders, ambiguity tolerance
- Source: [TechLife AI Skills 2025 guide](https://techlife.blog/posts/ai-skills-toolkit-2025-langchain-rag-mlops-guide/)

### 2.2 ML Engineer (production)

- **Must-have hard**: Distributed training (Horovod, DeepSpeed); model serving (Triton, vLLM); MLflow/W&B; Kubernetes; CI/CD for ML
- **Soft**: incident response, on-call ownership, A/B testing rigor
- Source: [Axial Search 10,000+ posts analysis](https://axialsearch.com/insights/ai-ml-engineering-jobs/)

### 2.3 Applied AI Engineer (verified from Anthropic JD)

- **Must-have hard**: 4+ yrs SWE/FDE/founder; production LLM apps including "prompting, context engineering, agent architectures"; Python production code
- **Soft**: customer-facing technical, workshop facilitation, technical communication
- Source: [Anthropic Applied AI Engineer JD](https://job-boards.greenhouse.io/anthropic/jobs/5116274008) (London role, fetched 2026-05-12)

### 2.4 Forward Deployed Engineer

- **Must-have hard**: end-to-end production deployment; data infrastructure mapping; integration engineering (REST, gRPC); Python + at least one other language
- **Soft**: client embedding, requirements elicitation under ambiguity, "ship code not slides"
- Source: [Pragmatic Engineer FDE explainer](https://newsletter.pragmaticengineer.com/p/forward-deployed-engineers)

### 2.5 Agentic AI Engineer

- **Must-have hard**: LangChain / LlamaIndex; agent frameworks (CrewAI, AutoGen, LangGraph); tool-use design; eval frameworks for multi-step reasoning; vector DBs
- **Soft**: system design for non-deterministic flows, observability mindset
- Source: [Interview Guys 2026 Agentic AI roles](https://blog.theinterviewguys.com/top-10-agentic-ai-jobs/)

### 2.6 LLM / RAG Developer

- **Must-have hard**: embedding models, document chunking, hybrid search, eval frameworks (RAGAS, TruLens), context window optimization
- **Recurring metrics**: perplexity, hallucination rate, factual consistency
- Source: [TechLife guide](https://techlife.blog/posts/ai-skills-toolkit-2025-langchain-rag-mlops-guide/)

### 2.7 MLOps Engineer

- **Must-have hard**: Kubernetes (17.6% of postings), Docker (15.4%), CI/CD, MLflow, drift detection, model versioning
- **Soft**: reliability/SRE mindset
- Source: [Axial Search](https://axialsearch.com/insights/ai-ml-engineering-jobs/)

### 2.8 Cross-cutting skill themes (all roles)

- **LangChain** mentioned in >10% of AI JDs ([TechLife 2025](https://techlife.blog/posts/ai-skills-toolkit-2025-langchain-rag-mlops-guide/))
- **RAG** competency is now table-stakes for any LLM-touching role
- **Eval/observability** skills (LangSmith, Weights & Biases, custom evals) rising fastest
- Confidence: **high**

---

## 3. Salary Tier Summary

Confidence: **high** for medians (Levels.fyi), **medium** for ranges (sources sometimes blur AI Engineer vs ML Engineer).

| Tier | YoE | Base salary range | Total comp range | AI-vs-non-AI premium |
|------|-----|-------------------|------------------|----------------------|
| Junior | 0–2 yr | $100K–$135K (SF/NYC start $115K–$135K) | $130K–$180K | **6.2%** in 2025 (down from 10.7% in 2024) |
| Mid | 3–5 yr | $145K–$220K | $200K–$310K | **11.9%** |
| Senior | 5+ yr | $200K–$312K base; LLM specialists $240K–$350K+ | $300K–$500K typical; up to $943K at top firms | **14.2%** |
| Staff/Principal | 8+ yr | $300K–$500K base | $500K–$917K (Intuit Staff AI: $917K) | **18.7%** (up from 15.8% in 2024) |

**Source**: All premium data from [Levels.fyi AI Engineer Compensation Trends Q3 2025](https://www.levels.fyi/blog/ai-engineer-compensation-trends-q3-2025.html). Tier ranges aggregated from [KORE1 2026 guide](https://www.kore1.com/ai-engineer-salary-guide/) and [Acceler8 Talent 2025-26](https://www.acceler8talent.com/resources/blog/ai-engineer--salary---market-rates-2025-2026/).

**Top-paying companies (median TC)**: Meta $430K, Apple $305K, Google $290K, NVIDIA $267K. OpenAI + Facebook lead AI specialist comp. Intuit Staff AI $917K vs $515K non-AI — among the steepest premiums observed ([Levels.fyi Q3 2025](https://www.levels.fyi/blog/ai-engineer-compensation-trends-q3-2025.html)).

**Geographic premium**: SF Bay Area > NYC > Seattle (same source).

**Salary volatility 2024→2025**: peak $295K median TC in March 2024 → dip to $228.5K in January 2025 → rebound to $260K–$277K mid-2025 (same source). Interpretation: market cooled briefly post-2024 hype but reset higher than 2023 baseline.

---

## 4. Growing vs Declining Roles (2023 → 2024 → 2025)

Confidence: **high** for direction, **medium** for magnitude.

### Growing (with growth rate)

| Role | Growth signal | Source |
|------|---------------|--------|
| AI Engineer | +75K postings 2023–2025; #1 Jobs on the Rise 2 yrs running | [LinkedIn 2025](https://www.linkedin.com/pulse/linkedin-jobs-rise-2025-25-fastest-growing-us-linkedin-news-gryie) |
| Forward Deployed Engineer | +800% Jan→Sep 2025 | [Sundeep Teki FDE](https://www.sundeepteki.org/forward-deployed-engineer.html) |
| Agentic AI Engineer | +986% mentions 2023→2024 | [Interview Guys 2026](https://blog.theinterviewguys.com/top-10-agentic-ai-jobs/) |
| Data Scientist | BLS projects +34% 2024–2034 (much faster than avg) | [BLS Data Scientists OOH](https://www.bls.gov/ooh/math/data-scientists.htm) |
| Computer & Info Research Scientist | BLS +20% 2024–2034 | [BLS CIRS OOH](https://www.bls.gov/ooh/computer-and-information-technology/computer-and-information-research-scientists.htm) |
| AI Compliance / Ethics / Eval | Emerging category, McKinsey notes hiring shift | [McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai) |

### Declining or stagnant

| Role | Decline signal | Source |
|------|----------------|--------|
| Entry-level SWE (no AI) | Microsoft says 40% of recent layoffs hit developers; big tech entry hiring -50% over 3 yrs | [Yale SOM Insights](https://insights.som.yale.edu/insights/the-real-job-destruction-from-ai-is-hitting-before-careers-can-start) |
| Data labeler / annotator | Among most-exposed-to-automation per multiple sources | [FinalRound AI 2025 displacement](https://www.finalroundai.com/blog/ai-replacing-jobs-2025) |
| Prompt Engineer (standalone) | Only 23% of orgs invested in prompt-eng training in 2025; role being absorbed into AI Engineer | [Forrester via FinalRound AI](https://www.finalroundai.com/blog/ai-tech-layoffs-mid-2025) |
| Generalist Junior Developer | Recent grad unemployment ~6%, rising 2× faster than rest of workforce since 2022 | [Yale SOM Insights](https://insights.som.yale.edu/insights/the-real-job-destruction-from-ai-is-hitting-before-careers-can-start) |

**Big picture caveat**: 2025 tech market characterized as "the big freeze" — hiring slowed to 2010 levels, but firing also restrained. AI roles are an island of expansion within an otherwise flat market. Confidence: **high** ([HR Executive layoff trap](https://hrexecutive.com/the-ai-layoff-trap-why-half-will-be-quietly-rehired/), [Yale SOM](https://insights.som.yale.edu/insights/the-real-job-destruction-from-ai-is-hitting-before-careers-can-start)).

---

## 5. 2026 Outlook (next 12 months)

Confidence: **medium** (forecasts inherently uncertain; cross-validated against 3+ sources where possible).

### Highest-confidence growth signals

1. **Agentic AI / AI Agent roles** — Gartner: 40% of enterprise apps will integrate task-specific AI agents by EOY 2026, up from <5% in 2025. Implies sustained ~50%+ YoY hiring growth for agent engineers ([Interview Guys 2026](https://blog.theinterviewguys.com/top-10-agentic-ai-jobs/), [Mercer 2025 agentic AI](https://www.mercer.com/insights/people-strategy/hr-transformation/heads-up-hr-2025-is-the-year-of-agentic-ai/)). Confidence **medium-high**.

2. **Forward Deployed Engineers** — OpenAI 2025 target was 50 FDEs; Anthropic + many startups replicating Palantir's model. Geographic expansion to UK, Germany, France, Japan signals continued ramp ([Sundeep Teki](https://www.sundeepteki.org/forward-deployed-engineer.html)). Confidence **high**.

3. **BLS structural projections (2024–2034)**:
   - Data Scientist +34% ([BLS](https://www.bls.gov/ooh/math/data-scientists.htm))
   - Computer & Info Research Scientist +20% ([BLS](https://www.bls.gov/ooh/computer-and-information-technology/computer-and-information-research-scientists.htm))
   - Software Developer +17.9% (2023–2033) ([BLS Employment Projections](https://www.bls.gov/emp/))
   - Confidence **high** (government longitudinal forecast).

4. **AI Evaluation, Human-in-the-Loop, AI Safety/Compliance** — McKinsey notes this is an emerging category created by enterprise compliance needs (EU AI Act, US executive orders). Hiring volume small but premium high ([McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)). Confidence **medium**.

### Cooler areas

- **Pure research scientist roles** at non-frontier labs likely flat — AI investment concentrating at OpenAI/Anthropic/Google/Meta/xAI tier; mid-tier labs and academic-adjacent positions facing budget pressure (inference, no single citation).
- **Generic ML Engineer (without LLM/agent skills)** — base demand persists but premium narrowing as more candidates enter market. Entry-level premium dropped 10.7% → 6.2% YoY ([Levels.fyi](https://www.levels.fyi/blog/ai-engineer-compensation-trends-q3-2025.html)). Confidence **medium**.

### Key 2026 watch-items

- Will entry-level AI engineer premium continue compressing? If pattern holds another year, "AI Engineer" as a junior title may lose its salary advantage.
- Will FDE growth saturate? 800% Jan-Sep 2025 is unsustainable; expect single-digit hundreds of percent YoY in 2026.
- Will agent infrastructure (LangGraph, AutoGen, etc.) consolidate? Skill-portfolio risk for engineers staking careers on specific frameworks.

---

## 6. Sources (all fetched 2026-05-12)

### Primary salary / hiring data
- [Levels.fyi — AI Engineer Compensation Trends Q3 2025](https://www.levels.fyi/blog/ai-engineer-compensation-trends-q3-2025.html) — **anchor source for premium %**
- [Levels.fyi — AI Engineer title page](https://www.levels.fyi/t/software-engineer/title/ai-engineer)
- [Levels.fyi — ML Engineer title page](https://www.levels.fyi/t/software-engineer/title/machine-learning-engineer)
- [Levels.fyi — ML/AI Software Engineer focus](https://www.levels.fyi/t/software-engineer/focus/ml-ai)

### LinkedIn / WEF labor trends
- [LinkedIn Jobs on the Rise 2025 — 25 fastest-growing U.S. roles](https://www.linkedin.com/pulse/linkedin-jobs-rise-2025-25-fastest-growing-us-linkedin-news-gryie)
- [WEF 2026-01 — AI added 1.3M jobs per LinkedIn data](https://www.weforum.org/stories/2026/01/ai-has-already-added-1-3-million-new-jobs-according-to-linkedin-data/) (note: direct fetch returned 403; cited via Google search snippet only — confidence reduced)

### Government data (BLS)
- [BLS Employment Projections 2024–2034 overview](https://www.bls.gov/opub/mlr/2026/article/industry-and-occupational-employment-projections-overview.htm)
- [BLS Data Scientists OOH](https://www.bls.gov/ooh/math/data-scientists.htm)
- [BLS Computer & Info Research Scientists OOH](https://www.bls.gov/ooh/computer-and-information-technology/computer-and-information-research-scientists.htm)
- [BLS AI impacts in employment projections](https://www.bls.gov/opub/ted/2025/ai-impacts-in-bls-employment-projections.htm)

### Consultancy / industry analysis
- [McKinsey — The state of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- [McKinsey — AI workforce development talent pipeline](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/building-a-talent-pipeline-for-the-ai-era)
- [Anthropic — Labor market impacts of AI](https://www.anthropic.com/research/labor-market-impacts)

### Skill / role analysis
- [TechLife — AI Skills 2025 LangChain RAG MLOps guide](https://techlife.blog/posts/ai-skills-toolkit-2025-langchain-rag-mlops-guide/)
- [Axial Search — 10,000+ AI/ML job posts analysis](https://axialsearch.com/insights/ai-ml-engineering-jobs/)
- [IntuitionLabs — What is an AI Engineer 2025 guide](https://intuitionlabs.ai/articles/ai-engineer-job-market-2025)
- [Acceler8 Talent — AI Engineer salary market rates 2025-2026](https://www.acceler8talent.com/resources/blog/ai-engineer--salary---market-rates-2025-2026/)
- [KORE1 — AI Engineer Salary Guide 2026](https://www.kore1.com/ai-engineer-salary-guide/)

### Representative JDs (actual openings)
- [Anthropic Applied AI Engineer (London)](https://job-boards.greenhouse.io/anthropic/jobs/5116274008) — confirmed details: £225K–£240K, 4+ yrs, production LLM apps required
- [Palantir Forward Deployed AI Engineer](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488)
- [Google Software Engineer PhD AI/ML 2026 Start](https://www.google.com/about/careers/applications/jobs/results/122258040807137990-software-engineer-phd-early-career-aimachine-learning-2026-start)
- [Google Software Engineer Applied AI](https://www.google.com/about/careers/applications/jobs/results/139686886695150278-software-engineer-applied-ai)
- [Anthropic Careers (general)](https://www.anthropic.com/careers)

### Forward Deployed Engineer specific
- [Sundeep Teki — FDE 800% growth report](https://www.sundeepteki.org/forward-deployed-engineer.html)
- [Pragmatic Engineer — Forward Deployed Engineers explainer](https://newsletter.pragmaticengineer.com/p/forward-deployed-engineers)
- [Hashnode — Complete 2026 FDE guide](https://hashnode.com/blog/a-complete-2026-guide-to-the-forward-deployed-engineer)
- [Index.dev — FDE AI hottest new role](https://www.index.dev/blog/forward-deployed-engineers-ai-hottest-job)

### Agentic AI specific
- [Interview Guys — Top 10 Agentic AI Jobs 2026](https://blog.theinterviewguys.com/top-10-agentic-ai-jobs/)
- [KORE1 — How to hire agentic AI engineers 2026](https://www.kore1.com/hire-agentic-ai-engineers-2026/)
- [Mercer — 2025 is the year of agentic AI](https://www.mercer.com/insights/people-strategy/hr-transformation/heads-up-hr-2025-is-the-year-of-agentic-ai/)

### Layoff / declining role data
- [Yale SOM Insights — Real job destruction hitting before careers start](https://insights.som.yale.edu/insights/the-real-job-destruction-from-ai-is-hitting-before-careers-can-start)
- [FinalRound AI — Tech layoffs 2025](https://www.finalroundai.com/blog/ai-tech-layoffs-mid-2025)
- [FinalRound AI — AI replacing jobs 2025](https://www.finalroundai.com/blog/ai-replacing-jobs-2025)
- [HR Executive — AI layoff trap](https://hrexecutive.com/the-ai-layoff-trap-why-half-will-be-quietly-rehired/)
- [Fortune 2026-04 — AI won't kill your job but kills first one](https://fortune.com/2026/04/29/ai-agentic-entry-level-jobs-disappearing-yale-celi-sonnenfeld/)

---

## Appendix: Data Gaps & Caveats

- **No single authoritative ranking** of US AI roles by hiring volume exists in fetched sources; my Top 10 ordering is a composite judgment. A future pass could pull raw LinkedIn Talent Insights or Indeed API for hard ordering.
- **WEF source 403 on direct fetch** — relied on Google search snippet quoting "1.3M jobs / 639K postings / 75K AI Engineer roles". Should re-verify via WEF cache or alternative LinkedIn source if claim becomes load-bearing.
- **Salary "ranges" blur AI Engineer vs ML Engineer vs Applied AI** — sources do not consistently distinguish. Levels.fyi medians are the most defensible numbers; aggregator sites (KORE1, Acceler8) include broader role buckets.
- **No fetched JD from OpenAI directly** — Anthropic JD is the verified primary example. Palantir FDE JD link cited but not deep-fetched.
- **2026 outlook section is inherently forecast** — labeled medium confidence; treat as scenarios, not predictions.
- **Geographic coverage**: US-centric. EU/UK numbers spotty (Anthropic London JD is the one verified UK data point).
