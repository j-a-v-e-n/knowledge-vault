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

