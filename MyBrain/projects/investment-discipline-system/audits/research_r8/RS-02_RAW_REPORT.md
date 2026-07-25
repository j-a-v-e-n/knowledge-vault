# RESEARCH-REFRESH-R8 / RS-02 raw report

## 0. Assignment boundary and final status

**Final status: `bounded_incomplete`.**

This report executes only topic `RS-02`. The only writes made are
`audits/research_r8/RS-02_RAW_REPORT.md` and
`research/evidence/r8/RS-02/**`. No governance, prototype, script, shared
document, or other agent file was edited.

All claim judgments below are `author_entailment` only. Per the assignment,
this agent did **not** perform or impersonate the independent per-claim
entailment review required for design closure. That predicate is false, so
`bounded_incomplete` is mandatory even though the fixed search budget,
snapshot classes, and stability rule were completed.

## 1. Temporal proof and preregistration verification

Preregistration file:
`research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json`.
It was read completely: `418` lines and `19278` bytes.

| Check | Observation | Verdict |
|---|---|---|
| Required commit | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | pass |
| Current `HEAD` at start | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | pass |
| Commit UTC | Git showed `2026-07-25 09:13:44 -0700`, equal to `2026-07-25T16:13:44Z` | pass |
| Ancestor relation | `git merge-base --is-ancestor 7824a63a… HEAD` returned exit `0` | pass |
| Remote containment | local remote ref `origin/codex/investment-assurance-r7` contains the commit | pass |
| Working-tree prereg SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | pass |
| Commit-contained prereg SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | pass |
| Worktree at start | clean | pass |

The repository top level is the knowledge-vault root, not the project
subdirectory. An initial `git show` used the project-relative path against the
repository root and failed; the corrected repository-relative path
`MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json`
produced the expected committed-file hash. No evidence or query was collected
before the correction.

Every counted retrieval UTC below is later than
`2026-07-25T16:13:44Z`. At report-authoring time there is no later evidence
commit yet; the ancestor check passes against every extant checkout commit and
must be rerun by the coordinator against the later commit that first contains
these artifacts.

## 2. Frozen protocol for RS-02

Question:

> AI 长项目中的自我袒护、上下文遗忘、记忆污染、代理错误传播和持久执行怎样由可执行反例约束？

Required query order and exact accounting:

| Query ID | Exact query | Retrieval UTC | Search calls |
|---|---|---|---|
| `R8-RS02-D1` | `LLM long term memory contamination stale memory supersession benchmark agent 2025 2026` | `2026-07-25T16:17:05Z` | exactly one |
| `R8-RS02-D2` | `long running AI agent harness checkpoint replay idempotency failure evaluation 2025 2026` | `2026-07-25T16:17:14Z` | exactly one |
| discovery freeze | D1/D2 claims and deltas frozen before S1 | `2026-07-25T16:17:56Z` | not a search |
| `R8-RS02-S1` | `counterexample multi agent debate voting improves accuracy objective benchmark` | `2026-07-25T16:18:58Z` | exactly one |
| `R8-RS02-S2` | `site:github.com agent memory stale contamination issue checkpoint replay duplicate` | `2026-07-25T16:19:17Z` | exactly one |
| `R8-RS02-S3` | `site:reddit.com coding agent long project memory context lost loop harness` | `2026-07-25T16:19:44Z` | exactly one |

No batch search, changed query, retry search, or sixth search was executed.
Direct opens, fixed-URL downloads, and a same-URL download retry are not search
calls. The search backend exposed no truncation flag. “Complete visible result
set” below means every result returned by that one call, in returned order; it
does not mean the dynamic web or search index was exhausted.

Screening codes:

- `IN-D`: decisive technical source selected for content checking/snapshot.
- `IN-C`: context or counterevidence; not independently decisive.
- `IN-P`: practitioner/issue evidence used only as a failure probe, burden, or
  reopen trigger; never as incidence.
- `EX-DUP`: same upstream paper/thread or mirror already represented.
- `EX-NAV`: author, index, profile, or navigation result.
- `EX-SCOPE`: adjacent but does not change an RS-02 decision.
- `EX-FP`: false positive.
- `EX-REMOVED`: removed result; snippet is not an adequate source.
- `EX-SECONDARY`: tertiary summary unsuitable for technical entailment.

## 3. Complete visible result sets and per-result screening

### 3.1 `R8-RS02-D1`

All rows inherit the exact query and UTC shown in the `Query · UTC` column.

| Order | Query · UTC | Visible result | Source class | Upstream cluster | Screening decision and reason | Revision / supersession |
|---:|---|---|---|---|---|---|
| 1 | `D1` · `2026-07-25T16:17:05Z` | [Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents](https://arxiv.org/abs/2606.27472) | primary preprint | `UC-SUPERSEDE-2606.27472` | `IN-D`: directly isolates stale-value supersession under bounded self-maintained memory | arXiv v1, `2026-06-25`; preprint under review |
| 2 | `D1` · `2026-07-25T16:17:05Z` | [STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?](https://arxiv.org/abs/2605.06527) | primary preprint | `UC-STALE-2605.06527` | `IN-D`: direct implicit-conflict, stale-premise, and downstream-adaptation benchmark | arXiv v1, `2026-05-07`; preprint |
| 3 | `D1` · `2026-07-25T16:17:05Z` | [MemGuard: Preventing Memory Contamination in Long-Term Memory-Augmented Large Language Models](https://arxiv.org/abs/2605.28009) | primary preprint | `UC-MEMGUARD-2605.28009` | `IN-D`: directly defines heterogeneous functional-role contamination and tests a mitigation | arXiv v1, `2026-05-27`; preprint |
| 4 | `D1` · `2026-07-25T16:17:05Z` | [PersistBench: When Should Long-Term Memories Be Forgotten by LLMs?](https://arxiv.org/abs/2602.01146) | primary preprint | `UC-PERSISTBENCH-2602.01146` | `IN-C`: cross-domain leakage and memory-induced sycophancy are relevant counterexamples, but not the main supersession contract | arXiv result dated `2026-02-01`; mutable abstract page |
| 5 | `D1` · `2026-07-25T16:17:05Z` | [Context Collapse in Long-Horizon Agents](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6976218) | SSRN paper | `UC-CONTEXT-COLLAPSE-6976218` | `IN-C`: compares memory designs, but a short non-peer-reviewed letter is not decisive | posted `2026-07-06`; SSRN record mutable |
| 6 | `D1` · `2026-07-25T16:17:05Z` | [Human-Inspired Memory Architecture for LLM Agents](https://www.microsoft.com/en-us/research/publication/human-inspired-memory-architecture-for-llm-agents/) | official research landing page | `UC-HUMAN-MEMORY-MSFT-2026` | `IN-C`: positive counterevidence that structured consolidation can work; vendor landing is a locator, not independent validation | May `2026`; page mutable |
| 7 | `D1` · `2026-07-25T16:17:05Z` | [How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior](https://aclanthology.org/2026.acl-long.27/) | peer-reviewed paper | `UC-XIONG-ACL2026` | `IN-D`: directly tests memory addition/deletion, experience following, and error propagation | ACL `2026`, fixed Anthology ID |
| 8 | `D1` · `2026-07-25T16:17:05Z` | [Paper page - Supersede](https://huggingface.co/papers/2606.27472) | paper mirror | `UC-SUPERSEDE-2606.27472` | `EX-DUP`: same upstream as result 1 | mutable mirror of arXiv v1 |
| 9 | `D1` · `2026-07-25T16:17:05Z` | [LongMemEval bibliography page](https://web.cs.ucla.edu/~kwchang/bibliography/wu2025longmemeval/) | author bibliography | `UC-LONGMEMEVAL-2410.10813` | `EX-NAV`: bibliographic locator only | mutable bibliography; cites ICLR `2025` |
| 10 | `D1` · `2026-07-25T16:17:05Z` | [MemEvoBench: Benchmarking Memory MisEvolution](https://www.emergentmind.com/papers/2604.15774) | secondary paper summary | `UC-MEMEVOBENCH-2604.15774` | `IN-C`: contamination hypothesis locator only; not used for a decisive claim | secondary summary of arXiv v1 |
| 11 | `D1` · `2026-07-25T16:17:05Z` | [LongMemEval \| ML Anthology](https://mlanthology.org/iclr/2025/wu2025iclr-longmemeval/) | secondary anthology mirror | `UC-LONGMEMEVAL-2410.10813` | `EX-DUP`: same LongMemEval upstream as result 9 | mutable mirror of ICLR `2025` |
| 12 | `D1` · `2026-07-25T16:17:05Z` | [Research \| Supersalience on LongMemEval](https://supersalience.com/research) | product self-report | `UC-SUPERSALIENCE-PRODUCT` | `IN-C`: positive capability counterevidence only; no independent audit | published `2026-05-22`; mutable commercial page |
| 13 | `D1` · `2026-07-25T16:17:05Z` | [Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions](https://mlanthology.org/iclr/2026/hu2026iclr-evaluating/) | secondary anthology mirror | `UC-MEMORYAGENTBENCH-ICLR2026` | `IN-C`: benchmark locator; not used without primary bytes | ICLR `2026`; mirror mutable |
| 14 | `D1` · `2026-07-25T16:17:05Z` | [LongMemEval — Supermemory Research](https://supermemory.ai/research/longmembench/) | product self-report | `UC-SUPERMEMORY-PRODUCT` | `IN-C`: positive counterevidence and benchmark-use warning only | mutable commercial page |
| 15 | `D1` · `2026-07-25T16:17:05Z` | [MemEvoBench API summary](https://api.emergentmind.com/papers/2604.15774) | secondary paper summary | `UC-MEMEVOBENCH-2604.15774` | `EX-DUP`: same upstream and summary provider as result 10 | cached secondary record |
| 16 | `D1` · `2026-07-25T16:17:05Z` | [Paper page - STALE](https://huggingface.co/papers/2605.06527) | paper mirror | `UC-STALE-2605.06527` | `EX-DUP`: same upstream as result 2 | mutable mirror of arXiv v1 |
| 17 | `D1` · `2026-07-25T16:17:05Z` | [How Memory Management Impacts LLM Agents PDF](https://aclanthology.org/2026.acl-long.27.pdf) | peer-reviewed PDF | `UC-XIONG-ACL2026` | `EX-DUP`: exact-content form of result 7; selected as the saved snapshot, not independent support | fixed ACL `2026` PDF |
| 18 | `D1` · `2026-07-25T16:17:05Z` | [How do you keep an agent from acting on facts that have since changed?](https://www.reddit.com/r/MLQuestions/comments/1uauqeg/how_do_you_keep_an_agent_from_acting_on_facts/) | practitioner thread | `UC-RDD-STALE-CROSSPOST` | `IN-P`: concrete stale-retrieval hypothesis only | thread dated `2026-06-20`; mutable |
| 19 | `D1` · `2026-07-25T16:17:05Z` | [We asked AI agents what was broken about their memory](https://www.reddit.com/r/AI_Agents/comments/1t5hkdq/we_asked_ai_agents_what_was_broken_about_their/) | practitioner/product thread | `UC-RDD-MEMANTO` | `IN-P`: provenance and indexing-delay burden only; promotional and not effect evidence | thread dated `2026-05-06`; mutable |
| 20 | `D1` · `2026-07-25T16:17:05Z` | [How do you keep an agent from acting on facts that have since changed?](https://www.reddit.com/r/LocalLLM/comments/1uauqo4/how_do_you_keep_an_agent_from_acting_on_facts/) | practitioner crosspost | `UC-RDD-STALE-CROSSPOST` | `EX-DUP`: same title/content upstream as result 18 | thread dated `2026-06-20`; mutable |
| 21 | `D1` · `2026-07-25T16:17:05Z` | [Long-term memory still feels like the weakest part of most LLM agents](https://www.reddit.com/r/learnmachinelearning/comments/1tb8gr9/longterm_memory_still_feels_like_the_weakest_part/) | practitioner thread | `UC-RDD-MEM-WEAKEST` | `IN-P`: stale-summary/noisy-retrieval failure probe only | thread dated `2026-05-12`; mutable |
| 22 | `D1` · `2026-07-25T16:17:05Z` | [How to benchmark whether agents actually learn across tasks](https://www.reddit.com/r/LLMDevs/comments/1uj38i5/how_to_benchmark_whether_agents_actually_learn/) | practitioner thread | `UC-RDD-CONTINUAL-BENCH` | `IN-P`: suggests persisted-vs-wiped sequence probe; no validated incidence | thread dated `2026-06-29`; mutable |
| 23 | `D1` · `2026-07-25T16:17:05Z` | [Project: I gave an LLM memory of its own mistakes](https://www.reddit.com/r/reinforcementlearning/comments/1t46tyy/project_i_gave_an_llm_memory_of_its_own_mistakes/) | practitioner/project thread | `UC-RDD-MISTAKE-MEMORY` | `IN-P`: positive anecdote and long-horizon collapse hypothesis only | thread dated `2026-05-05`; mutable |
| 24 | `D1` · `2026-07-25T16:17:05Z` | [RAG has not felt like enough for agent memory](https://www.reddit.com/r/LLMDevs/comments/1ubqyqk/rag_has_not_felt_like_enough_for_agent_memory_at/) | practitioner thread | `UC-RDD-CONFAB-MEMORY` | `IN-P`: ungrounded self-written memory is a concrete failure probe | thread dated `2026-06-21`; mutable |
| 25 | `D1` · `2026-07-25T16:17:05Z` | [My agents kept remembering things that weren't true](https://www.reddit.com/r/AI_Agents/comments/1uqj252/my_agents_kept_remembering_things_that_werent/) | practitioner thread | `UC-RDD-FALSE-MEMORY` | `IN-P`: stale-balance and truth-gate probe only | thread dated `2026-07-08`; mutable |
| 26 | `D1` · `2026-07-25T16:17:05Z` | [Persistent memory with high precision for long term and multi agent projects](https://www.reddit.com/r/claude/comments/1r4lb0r/persistent_memory_with_high_precision_for_long/) | practitioner/product thread | `UC-RDD-PERSIST-PROMO` | `EX-SCOPE`: solution promotion without comparative or failure evidence | thread dated `2026-02-14`; mutable |
| 27 | `D1` · `2026-07-25T16:17:05Z` | [STALE mirror](https://quickbooks-ai.org/?_=%2Fpdf%2F2605.06527%23zUXcvxMRZtzs00ASQPF%2B0sI%3D) | low-trust mirror | `UC-STALE-2605.06527` | `EX-DUP`: suspicious mirror of result 2 | mutable mirror; not used |
| 28 | `D1` · `2026-07-25T16:17:05Z` | [Tested 4 agent memory strategies over 50 turns](https://www.reddit.com/r/LLMDevs/comments/1u1xkmd/tested_4_agent_memory_strategies_over_50_turns/) | practitioner thread | `UC-RDD-FOUR-STRATEGIES` | `IN-P`: reported benchmark idea only; second-hand and not independently checked | thread dated `2026-06-10`; mutable |
| 29 | `D1` · `2026-07-25T16:17:05Z` | [Long-Term Memory Benchmark - Preliminary Tests](https://www.reddit.com/r/AiBuilders/comments/1skmj0b/longterm_memory_benchmark_preliminary_tests/) | practitioner thread | `UC-RDD-MEM-BENCH-GAP` | `IN-P`: benchmark-gap and test-dimension probe only | thread dated `2026-04-13`; mutable |
| 30 | `D1` · `2026-07-25T16:17:05Z` | [I mapped Alzheimer's research to agentic memory failures](https://www.reddit.com/r/ClaudeCode/comments/1uhq1bd/i_mapped_alzheimers_research_to_agentic_memory/) | practitioner/spec thread | `UC-RDD-ALZ-MEMORY` | `IN-P`: stale-memory curation hypothesis only; analogy is not mechanism evidence | thread dated `2026-06-28`; mutable |
| 31 | `D1` · `2026-07-25T16:17:05Z` | [From Storage to Experience: A Survey on the Evolution of LLM Agent Memory](https://aclanthology.org/2026.findings-acl.2069.pdf) | peer-reviewed survey | `UC-MEMORY-SURVEY-ACL2026` | `IN-C`: taxonomy/background only; not independent evidence for an atomic failure | Findings ACL `2026` PDF |
| 32 | `D1` · `2026-07-25T16:17:05Z` | [In Prospect and Retrospect: Reflective Memory Management](https://aclanthology.org/2025.acl-long.413.pdf) | peer-reviewed paper | `UC-RMM-ACL2025` | `IN-C`: positive memory-management counterevidence; does not close supersession or contamination | ACL `2025` PDF |

### 3.2 `R8-RS02-D2`

| Order | Query · UTC | Visible result | Source class | Upstream cluster | Screening decision and reason | Revision / supersession |
|---:|---|---|---|---|---|---|
| 1 | `D2` · `2026-07-25T16:17:14Z` | [AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents](https://arxiv.org/abs/2605.13357) | primary preprint | `UC-AIHE-2605.13357` | `IN-C`: auditable episode-package proposal; conceptual validation is not crash/replay correctness evidence | arXiv result dated `2026-05-13`; preprint |
| 2 | `D2` · `2026-07-25T16:17:14Z` | [Retrospective Harness Optimization](https://www.microsoft.com/en-us/research/publication/retrospective-harness-optimization-improving-llm-agents-via-self-preference-over-trajectory-rollouts/) | official research landing page | `UC-RHO-2606.05922` | `EX-DUP`: official locator for result 6; self-preference method is also relevant judge counterevidence | June `2026`; mutable landing page |
| 3 | `D2` · `2026-07-25T16:17:14Z` | [ACRFence: Preventing Semantic Rollback Attacks in Agent Checkpoint-Restore](https://arxiv.org/abs/2603.20625) | primary preprint/proof-of-concept | `UC-ACRFENCE-2603.20625` | `IN-D`: directly tests semantic replay and authority resurrection at checkpoint restore | arXiv v1, `2026-03-21`; proposed mitigation unimplemented in the paper |
| 4 | `D2` · `2026-07-25T16:17:14Z` | [SEAGym: An Evaluation Environment for Self-Evolving LLM Agents](https://www.alphaxiv.org/abs/2606.17546) | secondary paper mirror | `UC-SEAGYM-2606.17546` | `IN-C`: replay/cost evaluation locator only; secondary mirror not decisive | mutable alphaXiv mirror |
| 5 | `D2` · `2026-07-25T16:17:14Z` | [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | official vendor primary report | `UC-ANTHROPIC-HARNESS-20260324` | `IN-D`: reports context-reset/compaction and self-evaluation behavior, including model-specific counterevidence | article `2026-03-24`; exact Sanity revision saved |
| 6 | `D2` · `2026-07-25T16:17:14Z` | [Retrospective Harness Optimization: Improving LLM Agents via Self-Preference over Trajectory Rollouts](https://arxiv.org/abs/2606.05922) | primary preprint | `UC-RHO-2606.05922` | `IN-C`: positive harness-improvement evidence but uses self-validation/self-preference, so it cannot close judge independence | arXiv result dated `2026-06-04`; preprint |
| 7 | `D2` · `2026-07-25T16:17:14Z` | [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents?lid=1f0n56CPItf3Nm9NR) | official vendor primary report | `UC-ANTHROPIC-HARNESS-20251126` | `IN-D`: externalized state, incremental work, and handoff observations; vendor self-report only | published `2025-11-26`; live page mutable |
| 8 | `D2` · `2026-07-25T16:17:14Z` | [Long-Running AI Agent Runtime in 2026](https://slavadubrov.github.io/blog/2026/05/26/the-runtime--running-agents-for-hours-not-seconds/) | practitioner technical blog | `UC-BLOG-RUNTIME-20260526` | `IN-P`: useful runtime/checkpoint/idempotency checklist, not primary effect evidence | published `2026-05-26`; mutable |
| 9 | `D2` · `2026-07-25T16:17:14Z` | [Harness Engineering: The Retry That Booked Marta's Flight Twice](https://rickhigh.substack.com/p/harness-engineering-the-retry-that) | practitioner newsletter | `UC-SUBSTACK-DOUBLE-FLIGHT` | `IN-P`: duplicate-side-effect failure hypothesis only | published `2026-06-29`; mutable/paywalled context |
| 10 | `D2` · `2026-07-25T16:17:14Z` | [Harness Engineering: The Agent Control Plane](https://www.tmls.nyc/research/harness-engineering) | professional-society article | `UC-TMLS-HARNESS-202606` | `IN-C`: trajectory and bounded-retry guidance; secondary synthesis | published `2026-06-01`; mutable |
| 11 | `D2` · `2026-07-25T16:17:14Z` | [Scoped Verification for Reliable Long-Horizon Agentic Context Evolution](https://arxiv.org/abs/2607.09175) | primary preprint | `UC-GRACE-2607.09175` | `IN-C`: positive long-horizon verification counterevidence in a fixed telecom harness | arXiv result dated `2026-07-10`; preprint |
| 12 | `D2` · `2026-07-25T16:17:14Z` | [Durable Execution for AI Agents](https://www.dataaihub.co/learn/durable-execution) | educational article | `UC-DATAAIHUB-DURABLE` | `EX-SECONDARY`: generic guidance; no independent experiment | updated `2026-07-16`; mutable |
| 13 | `D2` · `2026-07-25T16:17:14Z` | [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | official vendor guide | `UC-ANTHROPIC-EVALS-20260109` | `IN-C`: supports frozen traces and task/grader separation, not crash/replay semantics | published `2026-01-09`; live page mutable |
| 14 | `D2` · `2026-07-25T16:17:14Z` | [Harness Evolution for LLM Agents](https://www.emergentmind.com/papers/2607.12227) | secondary paper summary | `UC-HARNESS-EVOLUTION-2607.12227` | `IN-C`: held-out comparison locator only; not used for a claim | summary of arXiv v1, `2026-07-14` |
| 15 | `D2` · `2026-07-25T16:17:14Z` | [AI Agent State Management: Checkpoints, Replay, and Recovery](https://sincllm.com/blog/ai-agent-state-management) | practitioner blog | `UC-SINCLLM-STATE` | `IN-P`: checkpoint/receipt probe ideas only | published `2026-07-10`; mutable |
| 16 | `D2` · `2026-07-25T16:17:14Z` | [Durable Execution for AI Agent Runtimes](https://zylos.ai/research/2026-04-24-durable-execution-agent-runtimes/) | vendor research article | `UC-ZYLOS-DURABLE` | `IN-C`: distributed-systems analogy and upgrade-replay hypothesis; not independent primary evidence | published `2026-04-24`; mutable |
| 17 | `D2` · `2026-07-25T16:17:14Z` | [After 3 months of running multi-agent orchestration in production](https://www.reddit.com/r/aiagents/comments/1rt1kjh/after_3_months_of_running_multiagent/) | practitioner thread | `UC-RDD-MAS-ORCH` | `IN-P`: context-bloat and compensator/idempotency probes only | thread displayed as four months old; mutable |
| 18 | `D2` · `2026-07-25T16:17:14Z` | [What failure only appeared after your AI agent had been running for a month?](https://www.reddit.com/r/AI_Agents/comments/1uy96vr/what_failure_only_appeared_after_your_ai_agent/) | practitioner thread | `UC-RDD-MONTH-FAILURE` | `IN-P`: retry-deduplication race and stale-read probes only | thread dated `2026-07-16`; mutable |
| 19 | `D2` · `2026-07-25T16:17:14Z` | [Agent Harness Engineering: A Survey](https://openreview.net/pdf/f358711a95aaaf61fdeffd4ef3fc60fba9b8da57.pdf) | survey/preprint PDF | `UC-HARNESS-SURVEY-OPENREVIEW` | `IN-C`: taxonomy and replay concern; not an atomic mechanism result | OpenReview PDF, displayed two months old |
| 20 | `D2` · `2026-07-25T16:17:14Z` | [The AI Agent Engineering Handbook](https://www.elephantclock.ae/downloads/ai-agent-engineering-handbook-elephantclock-2026.pdf) | commercial handbook | `UC-ELEPHANTCLOCK-HANDBOOK` | `EX-SECONDARY`: generic compounding/idempotency claims; unsuitable for technical entailment | `2026` PDF; mutable distribution |
| 21 | `D2` · `2026-07-25T16:17:14Z` | [What does it actually take to make long-running agent evals run at scale?](https://www.reddit.com/r/AI_Agents/comments/1syo3l6/what_does_it_actually_take_to_make_longrunning/) | practitioner thread | `UC-RDD-EVAL-SCALE` | `IN-P`: shared-environment contamination is a useful isolation probe | thread dated `2026-04-29`; mutable |
| 22 | `D2` · `2026-07-25T16:17:14Z` | [CSAI Foundation \| Cloud Security Alliance](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/06/CSA_research_note_langgraph_rce_chain_20260614-csa-styled-2.pdf) | security research note | `UC-CSA-LANGGRAPH-RCE` | `IN-C`: checkpoint-store poisoning is adjacent security counterevidence; not needed for the core claim | PDF published four weeks before retrieval |
| 23 | `D2` · `2026-07-25T16:17:14Z` | [Production agent evals should test incident replay](https://www.reddit.com/r/AI_Agents/comments/1uqjipq/production_agent_evals_should_test_incident/) | practitioner thread | `UC-RDD-INCIDENT-REPLAY` | `IN-P`: external-effect receipt is a concrete test hypothesis | thread dated `2026-07-08`; mutable |
| 24 | `D2` · `2026-07-25T16:17:14Z` | [We tried to run AI agents in production](https://www.reddit.com/r/aiagents/comments/1r32jv8/we_tried_to_run_ai_agents_in_production/) | practitioner thread | `UC-RDD-PRODUCTION-BROKE` | `IN-P`: partial failure, persisted inputs/outputs, and revalidation probes only | thread dated `2026-02-12`; mutable |
| 25 | `D2` · `2026-07-25T16:17:14Z` | [The longer an agent runs, the less I care about the prompt](https://www.reddit.com/r/AI_Agents/comments/1v50ker/the_longer_an_agent_runs_the_less_i_care_about/) | practitioner thread | `UC-RDD-LONGER-HARNESS` | `IN-P`: hard-gate, stale-file, and stopping-condition probes only | thread displayed as one day old; mutable |
| 26 | `D2` · `2026-07-25T16:17:14Z` | [SEAGym mirror](https://shoepaly.app/?_=%2Fpdf%2F2606.17546%23hKr38k1yZITo%2FkpxGBdjJos%3D) | low-trust mirror | `UC-SEAGYM-2606.17546` | `EX-DUP`: suspicious mirror of result 4 | mutable mirror; not used |
| 27 | `D2` · `2026-07-25T16:17:14Z` | [Building AI agents: days. Getting them to production: 6 months.](https://www.reddit.com/r/AI_Agents/comments/1srn9eo/building_ai_agents_days_getting_them_to/) | practitioner thread | `UC-RDD-PRODUCTION-TAIL` | `IN-P`: infinite-retry/budget probe only | thread dated `2026-04-21`; mutable |
| 28 | `D2` · `2026-07-25T16:17:14Z` | [Your agent keeps failing after you upgrade the model](https://www.reddit.com/r/AI_Agents/comments/1tkxlw3/your_agent_keeps_failing_after_you_upgrade_the/) | practitioner thread | `UC-RDD-UPGRADE-DRIFT` | `IN-P`: model/harness revision compatibility probe only | thread dated `2026-05-22`; mutable |
| 29 | `D2` · `2026-07-25T16:17:14Z` | [[Removed]](https://www.reddit.com/r/AI_Agents/comments/1u9zrvk/removed/) | removed practitioner result | `UC-RDD-REMOVED-1U9ZRVK` | `EX-REMOVED`: snippet cannot support a claim or stable snapshot | removed; thread dated `2026-06-19` |
| 30 | `D2` · `2026-07-25T16:17:14Z` | [After 6 months of agent failures in production, I stopped blaming the model](https://www.reddit.com/r/LangChain/comments/1rxt7c2/after_6_months_of_agent_failures_in_production_i/) | practitioner thread | `UC-RDD-LANGCHAIN-FAILURES` | `IN-P`: schema-drift and trace-replay probes only | thread dated `2026-03-19`; mutable |
| 31 | `D2` · `2026-07-25T16:17:14Z` | [When to use checkpointing and rollback?](https://www.reddit.com/r/AI_Agents/comments/1t7352g/when_to_use_checkpointing_and_rollback/) | practitioner thread | `UC-RDD-ROLLBACK` | `IN-P`: checkpoint cannot undo database side effects; existence hypothesis only | thread dated `2026-05-08`; mutable |
| 32 | `D2` · `2026-07-25T16:17:14Z` | [[Removed]](https://www.reddit.com/r/AI_Agents/comments/1t9xlfw/removed/) | removed practitioner result | `UC-RDD-REMOVED-1T9XLFW` | `EX-REMOVED`: snippet cannot support a claim or stable snapshot | removed; thread dated `2026-05-11` |
| 33 | `D2` · `2026-07-25T16:17:14Z` | [AI agent](https://en.wikipedia.org/wiki/AI_agent) | tertiary encyclopedia | `UC-WIKIPEDIA-AI-AGENT` | `EX-SECONDARY`: broad definition, no RS-02 mechanism entailment | mutable |
| 34 | `D2` · `2026-07-25T16:17:14Z` | [Agentic Artificial Intelligence](https://en.wikipedia.org/wiki/Agentic_Artificial_Intelligence) | tertiary encyclopedia | `UC-WIKIPEDIA-AGENTIC-AI` | `EX-SECONDARY`: broad taxonomy, no RS-02 mechanism entailment | mutable |

### 3.3 `R8-RS02-S1`

| Order | Query · UTC | Visible result | Source class | Upstream cluster | Screening decision and reason | Revision / supersession |
|---:|---|---|---|---|---|---|
| 1 | `S1` · `2026-07-25T16:18:58Z` | [Voting or Consensus? Decision-Making in Multi-Agent Debate](https://aclanthology.org/2025.findings-acl.606/) | peer-reviewed paper | `UC-VOTING-ACL2025` | `IN-D`: direct positive counterevidence; protocol/task type changes objective benchmark outcomes | Findings ACL `2025`, fixed Anthology ID |
| 2 | `S1` · `2026-07-25T16:18:58Z` | [Free-MAD: Consensus-Free Multi-Agent Debate](https://arxiv.org/abs/2509.11035) | primary preprint | `UC-FREEMAD-2509.11035` | `EX-DUP`: same upstream later represented by peer-reviewed result 3 | arXiv result dated `2025-09-14`; superseded for use by ACL `2026` |
| 3 | `S1` · `2026-07-25T16:18:58Z` | [Free-MAD: Consensus-Free Multi-Agent Debate](https://aclanthology.org/2026.findings-acl.1600/) | peer-reviewed paper | `UC-FREEMAD-ACL2026` | `IN-C`: positive single-round/anti-conformity result and negative evidence against forced consensus | Findings ACL `2026`, fixed Anthology ID |
| 4 | `S1` · `2026-07-25T16:18:58Z` | [Voting or Consensus? arXiv](https://arxiv.org/abs/2502.19130) | primary preprint | `UC-VOTING-ACL2025` | `EX-DUP`: same upstream as peer-reviewed result 1 | arXiv preprint superseded for use by ACL `2025` |
| 5 | `S1` · `2026-07-25T16:18:58Z` | [Voting or Consensus? alphaXiv](https://www.alphaxiv.org/abs/2502.19130v4) | secondary paper mirror | `UC-VOTING-ACL2025` | `EX-DUP`: same upstream as result 1 | alphaXiv v4 mirror |
| 6 | `S1` · `2026-07-25T16:18:58Z` | [Minority Sentinel: When to Overturn Majority Voting](https://arxiv.org/abs/2606.29270) | primary preprint | `UC-MINORITY-SENTINEL-2606.29270` | `IN-C`: correlated-error/minority-suppression counterevidence; no general incidence claim | arXiv result dated `2026-06-28`; preprint |
| 7 | `S1` · `2026-07-25T16:18:58Z` | [DynaDebate: Breaking Homogeneity in Multi-Agent Debate](https://arxiv.org/abs/2601.05746) | primary preprint | `UC-DYNADEBATE-2601.05746` | `IN-C`: homogeneity and external-tool verification refine the existing infection-oracle boundary | arXiv result dated `2026-01-09`; preprint |
| 8 | `S1` · `2026-07-25T16:18:58Z` | [Free-MAD \| Emergent Mind](https://www.emergentmind.com/papers/2509.11035) | secondary summary | `UC-FREEMAD-ACL2026` | `EX-DUP`: same upstream as result 3 | mutable secondary summary |
| 9 | `S1` · `2026-07-25T16:18:58Z` | [Voting or Consensus? alphaXiv overview](https://www.alphaxiv.org/overview/2502.19130v4) | secondary summary | `UC-VOTING-ACL2025` | `EX-DUP`: same upstream as result 1 | mutable secondary summary |
| 10 | `S1` · `2026-07-25T16:18:58Z` | [Free-MAD alphaXiv overview](https://www.alphaxiv.org/overview/2509.11035) | secondary summary | `UC-FREEMAD-ACL2026` | `EX-DUP`: same upstream as result 3 | mutable secondary summary |
| 11 | `S1` · `2026-07-25T16:18:58Z` | [Free-MAD alphaXiv full page](https://www.alphaxiv.org/abs/2509.11035) | secondary mirror | `UC-FREEMAD-ACL2026` | `EX-DUP`: same upstream as result 3 | mutable secondary mirror |
| 12 | `S1` · `2026-07-25T16:18:58Z` | [Literature Review: Free-MAD](https://www.themoonlight.io/en/review/free-mad-consensus-free-multi-agent-debate) | tertiary review | `UC-FREEMAD-ACL2026` | `EX-DUP`: same upstream and adds no independent evidence | mutable tertiary review |
| 13 | `S1` · `2026-07-25T16:18:58Z` | [When collaboration fails: persuasion driven adversarial influence in multi agent LLM debate](https://www.nature.com/articles/s41598-026-42705-7) | peer-reviewed paper | `UC-MAS-PERSUASION-NATURE2026` | `IN-C`: negative counterevidence that a persuasive adversarial agent can defeat collaboration/majority mechanisms in the tested setup | Scientific Reports `2026`; fixed article |
| 14 | `S1` · `2026-07-25T16:18:58Z` | [lkaesberg/decision-protocols](https://github.com/lkaesberg/decision-protocols) | open-source companion repository | `UC-VOTING-ACL2025` | `IN-C`: implementation/reproducibility locator; same upstream, not independent support | mutable repository main; Apache-2.0 displayed |

S1 delta verdict: `no_new_high_impact_delta`. Positive and negative results
preserve the frozen boundary: agent count alone is not the decision criterion;
task, interaction topology, error correlation, answer diversity, aggregation
rule, and objective oracle determine whether a multi-agent method helps.

### 3.4 `R8-RS02-S2`

| Order | Query · UTC | Visible result | Source class | Upstream cluster | Screening decision and reason | Revision / supersession |
|---:|---|---|---|---|---|---|
| 1 | `S2` · `2026-07-25T16:19:17Z` | [[Bug] Memory/Skill Review Issues in run_agent #13075](https://github.com/NousResearch/hermes-agent/issues/13075) | fixed GitHub issue | `UC-HERMES-13075` | `IN-P`: interruption counter reset and duplicate memory review are executable regression probes; exact API snapshot saved | opened `2026-04-20`; API snapshot state `open`, updated `2026-07-25T06:00:37Z` |
| 2 | `S2` · `2026-07-25T16:19:17Z` | [Memory persistence, token waste, state.db corruption, and environment hallucination #5563](https://github.com/NousResearch/hermes-agent/issues/5563) | GitHub field-report issue | `UC-HERMES-5563` | `IN-P`: stale file-read/context and session-fragmentation probes only | opened `2026-04-06`; mutable; state not fixed by backend output |
| 3 | `S2` · `2026-07-25T16:19:17Z` | [Compacted replacement_history retains active startup/context packets #21269](https://github.com/openai/codex/issues/21269) | fixed GitHub issue | `UC-CODEX-21269` | `IN-P`: duplicate/stale instruction-surface probe after compaction | opened `2026-05-05`; backend displayed `Open` |
| 4 | `S2` · `2026-07-25T16:19:17Z` | [Background memory review creates second provider instance on same DB #5129](https://github.com/NousResearch/hermes-agent/issues/5129) | fixed GitHub issue | `UC-HERMES-5129` | `IN-P`: concurrent duplicate extraction/consolidation probe | opened `2026-04-04`; backend displayed `Open`, related `#5140` |
| 5 | `S2` · `2026-07-25T16:19:17Z` | [Persisted orphaned toolCall poisons session replay #42112](https://github.com/openclaw/openclaw/issues/42112) | fixed GitHub issue | `UC-OPENCLAW-42112` | `IN-P`: structural checkpoint-history and atomic tool-call/result persistence probe; exact API snapshot saved | API snapshot state `closed/completed`, updated `2026-04-27T04:53:34Z` |
| 6 | `S2` · `2026-07-25T16:19:17Z` | [Memory flush agent overwrites live memory on reset/restart #2670](https://github.com/NousResearch/hermes-agent/issues/2670) | fixed GitHub issue | `UC-HERMES-2670` | `IN-P`: stale-writer/CAS/supersession probe; exact API snapshot saved | API snapshot state `closed/completed`; issue body updated `2026-03-23T23:08:40Z` |
| 7 | `S2` · `2026-07-25T16:19:17Z` | [Resume replay can surface a stale assistant final message #17487](https://github.com/openai/codex/issues/17487) | fixed GitHub issue | `UC-CODEX-17487` | `IN-P`: replayed-history versus fresh-output role probe | opened `2026-04-11`; backend displayed `Open` |
| 8 | `S2` · `2026-07-25T16:19:17Z` | [Codex local history index becomes stale #19822](https://github.com/openai/codex/issues/19822) | fixed GitHub issue | `UC-CODEX-19822` | `IN-P`: stale-index/context-loss and duplicate-work probe | opened in `2026`; mutable; exact state not exposed |
| 9 | `S2` · `2026-07-25T16:19:17Z` | [Raw prior-session turns replay as current input on /reset #68751](https://github.com/openclaw/openclaw/issues/68751) | fixed GitHub issue | `UC-OPENCLAW-68751` | `IN-P`: historical-data/instruction-authority boundary and autonomous re-execution probe; exact API snapshot saved | backend displayed `Open`; later API snapshot supersedes it with `closed/completed`, updated `2026-06-25T04:54:14Z` |
| 10 | `S2` · `2026-07-25T16:19:17Z` | [openai-agents-python memory.py at main](https://github.com/openai/openai-agents-python/blob/main/examples/sandbox/memory.py) | mutable open-source code | `UC-OPENAI-AGENTS-MEMORY-MAIN` | `IN-C`: positive implementation example explicitly acknowledges stale-memory debt; not pinned and not failure-rate evidence | mutable `main`; no commit returned |
| 11 | `S2` · `2026-07-25T16:19:17Z` | [Session/Memory contamination between multiple agent instances #6320](https://github.com/NousResearch/hermes-agent/issues/6320) | fixed GitHub issue | `UC-HERMES-6320` | `IN-P`: agent/profile scope-isolation and leakage probe | opened `2026-04-08`; backend displayed `Open`, related `#6332` |
| 12 | `S2` · `2026-07-25T16:19:17Z` | [Notify memory providers on /resume and /branch switches #6672](https://github.com/NousResearch/hermes-agent/issues/6672) | fixed GitHub issue | `UC-HERMES-6672` | `IN-P`: session-identity switch and cached-provider-state probe | opened `2026-04-09`; backend displayed `Open` |
| 13 | `S2` · `2026-07-25T16:19:17Z` | [Copilot Agent workshop PDF](https://github.github.com/workshops/general.ja.marp.pdf) | official workshop PDF | `UC-FP-COPILOT-WORKSHOP` | `EX-FP`: search-term overlap only | mutable workshop asset |
| 14 | `S2` · `2026-07-25T16:19:17Z` | [AD Bridge Quick Start Guide](https://github.com/BeyondTrust/pbis-open/wiki/docs/adb-quick-start-guide.pdf) | unrelated PDF | `UC-FP-AD-BRIDGE` | `EX-FP`: “agent”/“memory” term overlap only | historical guide |
| 15 | `S2` · `2026-07-25T16:19:17Z` | [Generating Stack Machine](https://github.com/etclabscore/evm_llvm/wiki/files/LLVM_talk.pdf) | unrelated PDF | `UC-FP-LLVM-STACK` | `EX-FP`: “duplicate”/“memory” term overlap only | historical asset |
| 16 | `S2` · `2026-07-25T16:19:17Z` | [A Workflow for the Synthesis of Irregular Memory Access](https://github.com/hpcgarage/spatter/wiki/pubs/memsys24/sheridan_et_al_scatter_gather_traces_memsys24.pdf) | unrelated systems paper | `UC-FP-SPATTER` | `EX-FP`: computer-memory/replay vocabulary, not agent memory | fixed conference PDF |
| 17 | `S2` · `2026-07-25T16:19:17Z` | [Pulsar – Real-time Analytics at Scale](https://github.com/pulsarIO/realtime-analytics/wiki/documents/Whitepaper_Pulsar_Real-timeAnalyticsatScale.pdf) | unrelated whitepaper | `UC-FP-PULSAR` | `EX-FP`: event replay term overlap only | historical PDF |

S2 delta verdict: `new_high_impact_delta`. The returned implementation issues
add authority/scope and concurrent-write revision to the memory contract, and
structural history validation to replay. This is frozen as `S2-AD01` and
`S2-AD02` in `research/evidence/r8/RS-02/STABILITY_ASSESSMENT.md`.

### 3.5 `R8-RS02-S3`

| Order | Query · UTC | Visible result | Source class | Upstream cluster | Screening decision and reason | Revision / supersession |
|---:|---|---|---|---|---|---|
| 1 | `S3` · `2026-07-25T16:19:44Z` | [We burned $12 in an unbounded agent loop before we noticed](https://www.reddit.com/r/DataGOL/comments/1shh2ks/we_burned_12_in_an_unbounded_agent_loop_before_we/) | practitioner thread | `UC-RDD-UNBOUNDED-LOOP` | `IN-P`: termination, budget, retry visibility, and memory-layer probes only | thread dated `2026-04-10`; mutable |
| 2 | `S3` · `2026-07-25T16:19:44Z` | [Agentic projects have a memory problem, so I built a small skill](https://www.reddit.com/r/AI_Agents/comments/1urmt1o/agentic_projects_have_a_memory_problem_so_i_built/) | practitioner/product thread | `UC-RDD-DECISION-CONTEXT` | `IN-P`: decision-lineage loss and raw-capture burden only | thread dated `2026-07-09`; mutable |
| 3 | `S3` · `2026-07-25T16:19:44Z` | [Long Term Memory Harness Benchmarks?](https://www.reddit.com/r/AiBuilders/comments/1she13i/long_term_memory_harness_benchmarks/) | practitioner thread | `UC-RDD-LTM-BENCH-GAP` | `IN-P`: continuity/contradiction benchmark gap and over-retrieval probes only | thread dated `2026-04-10`; mutable |
| 4 | `S3` · `2026-07-25T16:19:44Z` | [Built a way to monitor agents, detect loops and give agents shared memory](https://www.reddit.com/r/ClaudeCode/comments/1t78rgy/built_a_way_to_monitor_agents_detect_loops_email/) | practitioner/product thread | `UC-RDD-CONTEXT-EXHAUSTION` | `IN-P`: context-exhaustion-before-loop and structured-handoff probes only | thread dated `2026-05-08`; mutable |
| 5 | `S3` · `2026-07-25T16:19:44Z` | [AI Harness Engineering: an LLM without memory is Groundhog Day](https://www.reddit.com/r/vibecoding/comments/1sxw4tr/ai_harness_engineering_an_llm_without_memory_is/) | practitioner/product thread | `UC-RDD-HARNESS-SPEC` | `IN-P`: harness checklist and memory feedback-loop hypothesis only | thread dated `2026-04-28`; mutable |
| 6 | `S3` · `2026-07-25T16:19:44Z` | [Agent amnesia isn't a memory problem. It's a context engineering problem](https://www.reddit.com/r/ContextEngineering/comments/1sufmvb/agent_amnesia_isnt_a_memory_problem_its_a_context/) | practitioner essay | `UC-RDD-CONTEXT-ENGINEERING` | `IN-P`: selective retrieval/control-process hypothesis only | mutable thread, displayed three months old |
| 7 | `S3` · `2026-07-25T16:19:44Z` | [I built a pip-installable Python coding agent from first principles](https://af.reddit.com/r/OpenSourceAI/comments/1tjuxvp/i_built_a_pipinstallable_python_coding_agent_from/) | practitioner/product thread | `UC-RDD-HUMMCODE` | `IN-P`: tree-history/rewind implementation example; no reliability comparison | submitted `2026-05-21`; mutable |
| 8 | `S3` · `2026-07-25T16:19:44Z` | [Agent amnesia mirror](https://dd.reddit.com/r/ContextEngineering/comments/1sufmvb/agent_amnesia_isnt_a_memory_problem_its_a_context/) | Reddit regional mirror | `UC-RDD-CONTEXT-ENGINEERING` | `EX-DUP`: same thread as result 6 | mutable mirror |
| 9 | `S3` · `2026-07-25T16:19:44Z` | [I was mass-producing half-finished projects](https://ru.reddit.com/r/microsaas/comments/1scdtv0/i_was_massproducing_halffinished_projects_built_a/) | practitioner/product thread | `UC-RDD-PROJECT-CONTEXT` | `IN-P`: task/status/decision-log burden only; promotional | mutable regional mirror |
| 10 | `S3` · `2026-07-25T16:19:44Z` | [If you are unsatisfied with Opus 4.7, switch to 4.6](https://gl.reddit.com/r/ClaudeAI/comments/1spv2qi/if_you_are_unsatisfied_with_opus_47_please_simply/) | practitioner thread | `UC-RDD-MODEL-HARNESS-CONFOUND` | `IN-P`: model-versus-wrapper/compaction confounding is a reopen trigger only | mutable regional mirror |
| 11 | `S3` · `2026-07-25T16:19:44Z` | [admajic user page](https://www.reddit.com/user/admajic/) | user profile/navigation | `UC-RDD-USER-ADMAJIC` | `EX-NAV`: no stable thread-level claim | mutable profile |
| 12 | `S3` · `2026-07-25T16:19:44Z` | [Testing Your App \| Reddit for Developers](https://developers.reddit.com/docs/guides/tools/devvit_test) | official developer docs | `UC-REDDIT-DEVVIT-TEST` | `EX-SCOPE`: stateful mocks are unrelated to coding-agent long-project memory | mutable docs |
| 13 | `S3` · `2026-07-25T16:19:44Z` | [Extension-Aside29 user overview](https://it.reddit.com/user/Extension-Aside29/?sort=top) | user profile/navigation | `UC-RDD-USER-EXTENSION` | `EX-NAV`: snippets from multiple posts have no unique source assignment | mutable profile |
| 14 | `S3` · `2026-07-25T16:19:44Z` | [Read through Anthropic's 2026 agentic coding report](https://es.reddit.com/r/ClaudeAI/comments/1smuabd/read_through_anthropics_2026_agentic_coding/) | practitioner/second-hand thread | `UC-RDD-ANTHROPIC-REPORT` | `IN-P`: independent-task/clean-context hypothesis only; second-hand numbers are not used | mutable regional mirror |
| 15 | `S3` · `2026-07-25T16:19:44Z` | [AI Tools \| Reddit for Developers](https://developers.reddit.com/docs/guides/ai) | official developer docs | `UC-REDDIT-AI-DOCS` | `EX-SCOPE`: product-specific context-pollution warning does not establish RS-02 mechanism incidence | mutable docs |
| 16 | `S3` · `2026-07-25T16:19:44Z` | [Model recommendations for 128GB Strix Halo](https://vi.reddit.com/r/LocalLLaMA/comments/1oy1v7q/model_recommendations_for_128gb_strix_halo_and/?sort=new) | practitioner thread | `UC-RDD-HARDWARE-MODELS` | `EX-SCOPE`: model/hardware recommendations are not long-project evidence | mutable regional mirror |
| 17 | `S3` · `2026-07-25T16:19:44Z` | [Signal Seek](https://developers.reddit.com/apps/signal-seek) | unrelated app page | `UC-FP-SIGNAL-SEEK` | `EX-FP`: “memory/context” narrative overlap only | mutable app listing |
| 18 | `S3` · `2026-07-25T16:19:44Z` | [Snoosings](https://developers.reddit.com/apps/snoosings) | unrelated app page | `UC-FP-SNOOSINGS` | `EX-FP`: “loop/project” term overlap only | mutable app listing |

S3 delta verdict: `no_new_high_impact_delta`. Every included practitioner
result maps to an already frozen termination/budget, context-handoff,
memory-type/scope, or replay probe. No S3 result reversed a decision, added a
new high-impact failure class, or opened a critical/major contradiction.

## 4. Discovery freeze and stability result

The D1/D2 freeze was written before S1:

- file: `research/evidence/r8/RS-02/DISCOVERY_FREEZE.md`
- freeze UTC: `2026-07-25T16:17:56Z`
- SHA-256:
  `40e4fe8b133c95d9e0c92630fedb8e789c6376a075dfed6a3a964b437d641c07`

Frozen discovery claims: supersession failure; implicit invalidation;
functional-role contamination; experience-following/error propagation;
semantic rollback; trace package versus oracle; and the limited vendor claim
that compaction alone was insufficient in its cited setup.

Frozen discovery deltas: a versioned memory-assertion state contract; a wider
memory fault matrix; a semantic replay fence with effect receipts; and a
versioned crash/replay episode contract.

Stability sequence:

| Query | Delta result | Decision effect |
|---|---|---|
| S1 | no new high-impact delta | preserves narrow objective-oracle multi-agent exception and infection controls |
| S2 | new high-impact delta | adds authority/scope, stale-writer compare-and-swap, and structural replay validation |
| S3 | no new high-impact delta | all visible practitioner failures fit frozen classes |

The last high-impact delta was S2 and a later reserved query, S3, produced no
new high-impact failure class and no open critical/major contradiction.
Therefore `stability_protocol.passing_rule=true`. The detailed frozen
assessment is
`research/evidence/r8/RS-02/STABILITY_ASSESSMENT.md`, SHA-256
`a7ba40fb327508d9a5df2b875445170554e7833977e015204e79741f4fa03e4f`.
No sixth query was used to manufacture stability.

## 5. Exact-byte snapshots and manifest

Machine-readable manifest:
`research/evidence/r8/RS-02/MANIFEST.json`.

All selected bodies were saved as exact response bytes. Response headers were
saved separately under `headers/`, including media type and available
ETag/Last-Modified validators. A first local-path failure and then a sandbox DNS
failure occurred before the Supersede download; the same fixed URL later
succeeded with approved network access. The exact errors and times are in
`receipts/SNAPSHOT_RETRIEVAL_RETRIES.md`. Because the fixed-version bytes were
ultimately saved, no required snapshot class remained blocked.

| Source ID | Fixed URL / revision | Retrieval UTC | Media type | Bytes | SHA-256 | Source range used | License / quotation boundary |
|---|---|---|---|---:|---|---|---|
| `RS02-SRC-MEM-01` | `https://arxiv.org/pdf/2606.27472v1`; arXiv v1 | `2026-07-25T16:21:53Z` | `application/pdf` | `275393` | `ba7175324f30b02ff1967242250d421afdb0a6f1f80c3f48d2576f4f77de7e1b` | PDF pp. 1, 5, 8 | license not independently established; local verification and short attributed quotation only |
| `RS02-SRC-MEM-02` | `https://arxiv.org/pdf/2605.06527v1`; arXiv v1 | `2026-07-25T16:22:49Z` | `application/pdf` | `5568857` | `388f71f1eb952e7d7e7b19c2f25bfc744c47efa8ee00a548093b949432495109` | PDF pp. 1, 3-4, 7, 14 | license not independently established; local verification and short attributed quotation only |
| `RS02-SRC-MEM-03` | `https://arxiv.org/pdf/2605.28009v1`; arXiv v1 | `2026-07-25T16:22:56Z` | `application/pdf` | `1312901` | `b396784d2f056b3310ee4012b2d909fa148f27a24a3a8ea249e3fba32271a5fd` | PDF pp. 1, 3, 8-9 | license not independently established; local verification and short attributed quotation only |
| `RS02-SRC-MEM-04` | `https://aclanthology.org/2026.acl-long.27.pdf`; ACL `2026` | `2026-07-25T16:23:08Z` | `application/pdf` | `10212411` | `2c3992d238f5d6dec4ed96faae0a82e3b88edc6e37b26d8622a2b780f2160400` | PDF pp. 1, 5-6, 9 | saved ranges do not state a redistribution license; cite and quote minimally |
| `RS02-SRC-DUR-01` | `https://arxiv.org/pdf/2603.20625v1`; arXiv v1 | `2026-07-25T16:22:40Z` | `application/pdf` | `463072` | `5b88ebb1f9dc1cb136c2e8b282a5b9d31122dc172ecd9c1893f4a5b578e86263` | PDF pp. 1-3 | license not independently established; local verification and short attributed quotation only |
| `RS02-SRC-DUR-02` | Anthropic article `_rev=nndkrAuP7NXH0SvEsFos86`, `_updatedAt=2026-03-24T16:23:08Z` | `2026-07-25T16:23:27Z` | `text/html; charset=utf-8` | `248479` | `3643c6685d30c4d4a3e3e9d7bef5ed53da5f2ce0e4c070f11c07c5c4e43e6aa7` | “Why naive implementations fall short” and architecture paragraphs | Anthropic copyright; internal verification and short attributed quotation only |
| `RS02-SRC-MAS-01` | `https://aclanthology.org/2025.findings-acl.606.pdf`; Findings ACL `2025` | `2026-07-25T16:23:17Z` | `application/pdf` | `978424` | `f4c85dab5bc9dada9d6bc4554dbc7224386769039bc1c2fcff7d856e31863f6d` | PDF pp. 1, 5-6, 9 | saved ranges do not state a redistribution license; cite and quote minimally |
| `RS02-SRC-ISSUE-01` | Hermes issue `#2670`; API ETag recorded | `2026-07-25T16:23:43Z` | `application/json; charset=utf-8` | `7444` | `17813fa4e55d80cf8f857db257986935be54d064dbc20e139071140489263113` | `$.body`, derived lines 1-39 | failure probe only; no incidence; minimal attributed quotation |
| `RS02-SRC-ISSUE-02` | OpenClaw issue `#68751`; API state `closed/completed` | `2026-07-25T16:23:55Z` | `application/json; charset=utf-8` | `15533` | `ce3654c614349083c1737da7f45f87f161620ad31137ae3fc9349e50e2afcccd` | `$.body`, derived lines 1-23, 100-104 | failure probe only; no incidence; minimal attributed quotation |
| `RS02-SRC-ISSUE-03` | OpenClaw issue `#42112`; API state `closed/completed` | `2026-07-25T16:24:03Z` | `application/json; charset=utf-8` | `9304` | `e12ee1b466d02ed8cfa88ddabf465968ff847be26741a807dd8606df5f60d1bc` | `$.body`, derived lines 1-25, 61-73, 83-123 | failure probe only; no incidence; minimal attributed quotation |
| `RS02-SRC-ISSUE-04` | Hermes issue `#13075`; API state `open` | `2026-07-25T16:24:14Z` | `application/json; charset=utf-8` | `5822` | `6c51d5fa9f8afd8f36ce1dc4278f70f7b9ae4fcdf85e03186256caf3de50b283` | `$.body`, derived lines 3-30 | failure probe only; no incidence; minimal attributed quotation |

Required snapshot-class predicates:

| Required class | Predicate | Evidence |
|---|---|---|
| one primary or peer-reviewed memory failure source | `true` | four saved primary/peer-reviewed PDFs |
| one primary harness or durable execution source | `true` | ACRFence v1 PDF and exact Anthropic article HTML |
| one implementation issue or practitioner failure report | `true` | four exact GitHub API JSON bodies |

PDF integrity and visual verification:

- ACRFence: `4` pages; unencrypted; PDF `1.7`.
- Voting or Consensus?: `32` pages; unencrypted; PDF `1.5`.
- MemGuard: `29` pages; unencrypted; PDF `1.7`.
- STALE: `37` pages; unencrypted; PDF `1.7`.
- Supersede: `11` pages; unencrypted; PDF `1.7`.
- Xiong et al.: `23` pages; unencrypted; PDF `1.7`.
- Text was extracted with Poppler for range location. Page 1 of every PDF was
  rendered to PNG and visually inspected; titles, abstracts, diagrams, and text
  were legible with no clipping or corrupt rendering.

## 6. Atomic claims

No claim below has an independent-review verdict. The stated entailment is the
author's screening judgment and cannot satisfy the preregistered independent
review predicate.

### `RS02-C01` — bounded memory can preserve a stale value despite stronger full-context performance

- `topic_id`: `RS-02`
- `claim_text`: In the Supersede paper's LongMemEval knowledge-update setup,
  replacing full context with bounded self-maintained memory reduced the
  reported gpt-5.4 accuracy from `92%` to `77%`; the paper attributes the
  within-setup gap to memory maintenance and reports that model scaling did not
  close it.
- `impact`: high
- `evidence_cluster_ids`: `UC-SUPERSEDE-2606.27472`
- `source_snapshot_ids`: `RS02-SRC-MEM-01`
- `source_ranges`: PDF p. 1 abstract; p. 5 Figure 2, Table 1, Section 5.1;
  p. 8 limitations
- `author_entailment`: `entailed_within_reported_setup`
- `limitations`: preprint; one benchmark subset; the frontier comparison uses
  an LLM judge and the paper identifies judge noise; the scale ablation uses a
  smaller sample; the training result is one run. It does not establish a
  production incidence or universal model failure.
- `decision_effect`: long-term memory remains non-authoritative. Add explicit
  current-value/supersession state, retain old versions as lineage, and require
  direct-update plus long-history regression probes before use in a decision.

### `RS02-C02` — implicit invalidation is separable from retrieval of the latest evidence

- `topic_id`: `RS-02`
- `claim_text`: STALE defines implicit conflict as a later observation
  invalidating an earlier belief without explicit negation and separately tests
  State Resolution, Premise Resistance, and Implicit Policy Adaptation. In its
  reported evaluation, retrieving updated evidence did not guarantee rejecting
  a stale premise or acting on the updated state.
- `impact`: high
- `evidence_cluster_ids`: `UC-STALE-2605.06527`
- `source_snapshot_ids`: `RS02-SRC-MEM-02`
- `source_ranges`: PDF p. 1 abstract; pp. 3-4 definition/taxonomy; p. 7 result
  table/discussion; p. 14 limitations
- `author_entailment`: `entailed_within_benchmark_scope`
- `limitations`: preprint; controlled one-shot conflict pairs; scenarios were
  LLM-generated then expert-validated; open-ended repeated updates and gradual
  drift are outside the benchmark. The prototype mitigation is directional,
  not proof of sufficiency.
- `decision_effect`: the memory test oracle must separately assert current-state
  selection, stale-premise rejection, and downstream policy adaptation,
  including indirect/propagated invalidation.

### `RS02-C03` — semantic similarity can mix memories with incompatible evidential roles

- `topic_id`: `RS-02`
- `claim_text`: MemGuard identifies heterogeneous memory contamination when
  stable facts, episodic events, and behavioral rules are stored or retrieved
  as interchangeable evidence despite different functional roles. Its
  experiments support type separation plus query-adaptive routing as a
  mitigation in the tested benchmarks.
- `impact`: high
- `evidence_cluster_ids`: `UC-MEMGUARD-2605.28009`
- `source_snapshot_ids`: `RS02-SRC-MEM-03`
- `source_ranges`: PDF p. 1 abstract/example; p. 3 Section 3 definition;
  p. 8 component analysis; p. 9 limitation
- `author_entailment`: `entailed_within_reported_benchmarks`
- `limitations`: preprint; type assignment and routing are themselves
  LLM-based; the paper says correct retrieval does not prevent
  generation-time composition errors and may add inference cost. It does not
  prove universal types or a sufficient safety boundary.
- `decision_effect`: bind each memory atom to an evidential role and allowed
  query scope; retrieval volume alone cannot authorize use. Add
  episodic-as-semantic, rule-as-fact, and cross-domain mismatch probes.

### `RS02-C04` — unverified trajectories can propagate into later behavior

- `topic_id`: `RS-02`
- `claim_text`: Xiong et al. report an experience-following property in which
  similar retrieved task inputs tend to yield similar outputs, plus error
  propagation and misaligned experience replay under their tested agent-memory
  systems. Evaluator quality affects which trajectories are retained.
- `impact`: high
- `evidence_cluster_ids`: `UC-XIONG-ACL2026`
- `source_snapshot_ids`: `RS02-SRC-MEM-04`
- `source_ranges`: PDF p. 1 abstract; pp. 5-6 Sections 3.3-3.4; p. 9 conclusion
  and limitations
- `author_entailment`: `entailed_within_tested_agents_and_tasks`
- `limitations`: the paper focuses on addition/deletion and omits more complex
  structural transformation, merging, summarization, and reflection. It does
  not establish a universal propagation rate.
- `decision_effect`: an agent-written lesson or prior trajectory is tainted
  until grounded by the later observed result. Store outcome labels and
  provenance; quarantine failed/unknown trajectories; never promote repetition
  into truth by retrieval frequency.

### `RS02-C05` — checkpoint restore can replay intent under a new request identity

- `topic_id`: `RS-02`
- `claim_text`: ACRFence demonstrates in its proof-of-concept that an LLM can
  re-synthesize a changed request after checkpoint restore, allowing an
  external service to treat repeated intent as a new action. The paper names
  Action Replay and Authority Resurrection as two attack classes.
- `impact`: critical
- `evidence_cluster_ids`: `UC-ACRFENCE-2603.20625`
- `source_snapshot_ids`: `RS02-SRC-DUR-01`
- `source_ranges`: PDF p. 1 abstract/root cause; p. 2 threat model and attack
  validation; pp. 2-3 proposed mitigation and discussion
- `author_entailment`: `entailed_for_authors_proof_of_concept`
- `limitations`: preprint; simulated external services and a fixed testbed; the
  proposed ACRFence mitigation was **not implemented or evaluated** in the
  paper; its analyzer LLM introduces misclassification and adversarial-evasion
  risk. The paper cannot support adopting ACRFence as a solved control.
- `decision_effect`: checkpoint presence and request-ID idempotency cannot prove
  exactly-once effects. Bind normalized intent, operation identity,
  authority/capability epoch, preconditions, and checkpoint lineage; persist an
  external-effect receipt; reconcile observed external state before retry; and
  require explicit replay/fork/compensate/human-blocked handling.

### `RS02-C06` — separating generator and evaluator helps in a vendor report but does not remove evaluator leniency

- `topic_id`: `RS-02`
- `claim_text`: Anthropic's saved harness article reports self-evaluation that
  skews positive and says a separate evaluator was a useful lever, while also
  stating that separation alone did not eliminate evaluator leniency.
- `impact`: high
- `evidence_cluster_ids`: `UC-ANTHROPIC-HARNESS-20260324`
- `source_snapshot_ids`: `RS02-SRC-DUR-02`
- `source_ranges`: HTML article section “Why naive implementations fall short,”
  self-evaluation paragraphs
- `author_entailment`: `entailed_as_vendor_report`
- `limitations`: vendor self-report; subjective design and application
  experiments; no independent blind replication or effect-size estimate.
  Merely naming another LLM “reviewer” does not establish independence.
- `decision_effect`: retain blind identity, order swap, pinned judge revision,
  deterministic or human reference, and disagreement retention. A separate
  evaluator may propose a signal but cannot alone grant completion.

### `RS02-C07` — compaction/reset behavior is model- and harness-revision dependent

- `topic_id`: `RS-02`
- `claim_text`: The same Anthropic article reports that an earlier Sonnet 4.5
  harness required context resets because compaction alone was insufficient in
  that setup, but that a later Opus 4.5 harness dropped resets and used
  automatic compaction. This is direct counterevidence to a universal claim
  that every long task requires resets or that compaction always fails.
- `impact`: high
- `evidence_cluster_ids`: `UC-ANTHROPIC-HARNESS-20260324`
- `source_snapshot_ids`: `RS02-SRC-DUR-02`
- `source_ranges`: HTML context-reset/compaction paragraphs and “The
  architecture” paragraph
- `author_entailment`: `entailed_as_vendor_report`
- `limitations`: vendor-specific models, prompts, tasks, and orchestration;
  does not directly measure lost-in-the-middle position effects or project
  restart correctness.
- `decision_effect`: pin model, prompt, compaction, and harness revisions. Keep
  start/middle/end, compaction, restart, and stale-request metamorphic probes;
  do not encode “always reset” or “compaction is sufficient” as a timeless rule.

### `RS02-C08` — multi-agent methods can help objective tasks, but protocol and interaction can also degrade them

- `topic_id`: `RS-02`
- `claim_text`: In the peer-reviewed Voting or Consensus study, voting
  protocols improved the reported reasoning-task result by `13.2%` relative to
  the compared decision protocols, consensus performed better on the tested
  knowledge tasks, and increasing discussion rounds before voting reduced
  performance in the reported setup.
- `impact`: high counterevidence
- `evidence_cluster_ids`: `UC-VOTING-ACL2025`
- `source_snapshot_ids`: `RS02-SRC-MAS-01`
- `source_ranges`: PDF p. 1 abstract; p. 5 task/protocol comparison; p. 6
  agent/round analysis; p. 9 limitations
- `author_entailment`: `entailed_within_reported_benchmarks`
- `limitations`: sampled subsets; three independent runs; substantial compute
  cost; agents often converged on similar responses; prompt/persona effects
  were not fully ablated. Objective QA/reasoning benchmarks do not imply
  independent semantic review of an open software project.
- `decision_effect`: reject “more agents always hurt” and “more agents always
  help.” Permit a narrow experiment with isolated samples, a deterministic
  objective oracle, pinned aggregation, and cost accounting. Shared debate,
  majority vote, or agent count cannot substitute for claim lineage and
  infection tests.

### `RS02-C09` — implementation reports expose stale-write, instruction-replay, malformed-history, and duplicate-review paths

- `topic_id`: `RS-02`
- `claim_text`: The saved fixed GitHub issues report four concrete paths:
  an old-context flush overwriting newer memory; historical commands re-entering
  context as current input after reset; a persisted tool call without its result
  poisoning replay; and interruption/loop logic causing missed or duplicate
  memory review.
- `impact`: high failure-probe evidence
- `evidence_cluster_ids`: `UC-HERMES-2670`,
  `UC-OPENCLAW-68751`, `UC-OPENCLAW-42112`, `UC-HERMES-13075`
- `source_snapshot_ids`: `RS02-SRC-ISSUE-01`,
  `RS02-SRC-ISSUE-02`, `RS02-SRC-ISSUE-03`, `RS02-SRC-ISSUE-04`
- `source_ranges`: exact JSON `$.body` ranges listed in the manifest
- `author_entailment`: `entailed_as_reported_existence_not_independently_reproduced`
- `limitations`: issue reports are user/maintainer artifacts, not controlled
  incidence studies; three snapshots are closed/completed and may be fixed in
  current releases; the open issue can also change. They cannot establish
  prevalence or current universal framework behavior.
- `decision_effect`: add project/session/agent/profile scope and
  instruction-authority metadata; use compare-and-swap for stale writers;
  treat historical content as untrusted data; validate tool-call/result
  structure before replay; and test every interruption edge for zero/duplicate
  state transitions.

