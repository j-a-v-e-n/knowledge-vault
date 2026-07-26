# AI project method evidence refresh R10

## 0. Disposition

- Evidence cutoff: `2026-07-25`
- Research claim status: `bounded_incomplete`
- Review status: independent review `10B` kept four major defects open; this
  revision is the next repair candidate and has not received a replacement
  acceptance review
- Decision served: determine which AI-project methods change the control
  architecture of this project, which are implementation patterns, and which
  are only new labels

This file does not prove that the project method is sufficient, that the
investment product is complete, or that any named framework is reliable for
this project. It records a bounded evidence refresh and the falsifiable
decisions derived from it.

## 1. Question reduced to first principles

The practical question is not “which current engineering label should the
project follow?” It is:

> What system lets a fallible, context-limited, potentially self-favoring AI
> transform a durable human goal into a working product while making drift,
> failure, unsupported completion, and recovery mechanically observable?

This project hypothesizes that the following responsibilities are needed,
regardless of the names used by current articles or tools. “Needed” here is a
project design hypothesis, not an externally proved universal requirement:

1. durable intent and acceptance criteria;
2. explicit task and information dependencies;
3. bounded local execution loops;
4. controlled tools, permissions, and side effects;
5. durable current state and supersession rules;
6. observable actions, evidence, and failure attribution;
7. an oracle that is not authored and judged solely by the same process;
8. termination, no-progress, recovery, and escalation semantics;
9. provenance and versioning;
10. a human authority boundary for consequences the AI may not take.

The project should therefore adopt useful mechanisms, not pledge allegiance to
a vocabulary.

## 2. Candidate method families map to different control surfaces

This table is a `project_engineering_hypothesis`, not a taxonomy established by
the cited sources and not a claim that every project needs every row.

| Method family | Primary control surface | Hypothesized local contribution | What it does not prove |
|---|---|---|---|
| Prompt engineering | one model invocation | local instruction quality | durable state, recovery, or product correctness |
| Context engineering | information visible for a decision | relevance and authority of current inputs | that remembered information is current or sufficient |
| Specification-driven development | durable intent and contracts | traceable requirements, plans, and tests | that the specification is complete or correct |
| Harness engineering | model–tool–environment runtime | permissions, state, feedback, observability, recovery | that the model or evaluator is unbiased |
| Loop engineering | bounded iteration toward a local condition | persistence and repeated correction | global coordination or valid stopping by itself |
| Graph/workflow engineering | dependencies and routing among work units | parallelism, joins, failure propagation, explicit control flow | truth of node outputs or independence of reviewers |
| Evaluation/assurance engineering | evidence-to-verdict transformation | calibrated completion and failure detection | correctness when the oracle shares the same blind spots |

The bounded evidence does not establish a clean historical ladder in which each
new term replaces the previous one. This project will test a candidate
architecture in which selected controls compose only where a traced local
failure and falsification test justify them. A family may be omitted, reduced,
or replaced when the local test does not support its cost.

## 3. “Graph Engineering” finding

The bounded R10 source set does not contain a standards document or a source
that defines `Graph Engineering` as a technical standard. It also does not
establish the term's origin, adoption rate, or generally accepted meaning.

Official LangGraph and Spec Kit documentation independently demonstrate that
state graphs, routing, parallel branches, loops, structured artifacts, and
workflow automation existed as concrete implementation primitives in the
reviewed products. That fact does not establish what the newer label means or
whether it adds a capability.

Local engineering inference, not an external fact:

- use a typed work DAG where dependencies, activation, joins, and failure
  propagation are machine-checkable;
- retain bounded execution loops inside appropriate nodes;
- do not add a graph runtime merely to satisfy the label;
- require a demonstrated need before introducing orchestration infrastructure
  beyond repository-native data and deterministic scripts.

These choices are `candidate_control` decisions derived from the project's
current dependency and failure structure. They require the local DAG,
cycle/conflict, activation, and join tests described below; the terminology
itself is not admission evidence.

## 4. Evidence matrix

### 4.1 Primary and official technical sources

All rows were re-opened on `2026-07-25`. The replay authority is
`research/evidence/r10/SOURCE_MANIFEST.json`, which records exact retrieval
times, versions or commits, local paths, byte counts, and SHA-256 values.
`fixed snapshot` means the named source version and retained bytes are bound;
it does not make the source sufficient or universally applicable. A field probe
without retained bytes cannot close a decision-bearing research gate.

| ID | Source · publication/submission | Class · revision state | Relevant observation | Claim boundary |
|---|---|---|---|---|
| `M-S01` | [OpenAI, Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) · `2026-02-11` | vendor primary experience report · mutable page · direct snapshot attempts returned HTTP 403 · field probe only | repository knowledge, legibility, constraints, feedback loops, and entropy control are treated as the main human engineering work | one internal product experience; not replayable locally and not an independent comparative trial |
| `M-S02` | [Anthropic, Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) · `2026-03-24` | vendor primary experience report · exact R8 snapshot reused and hash-bound in the R10 manifest | decomposition, structured handoffs, generator/evaluator separation, and repeated evaluation changed the reported build | vendor-authored, model- and task-specific; evaluator separation does not itself prove independence |
| `M-S03` | [AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents](https://arxiv.org/abs/2605.13357v1) · `2026-05-13` | primary preprint · arXiv `v1` · fixed snapshot | formalizes the harness as the runtime between model and environment and proposes auditable episode packages | conceptual framework plus controlled validation; not broad production reliability evidence |
| `M-S04` | [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850v4) · revised `2026-05-18` | primary preprint · arXiv `v4` · fixed snapshot | treats observability and harness adaptation as optimization targets | automatic optimization can optimize an incomplete oracle |
| `M-S05` | [GitHub Spec Kit documentation](https://github.github.com/spec-kit/index.html) and [commit-pinned spec-driven reference](https://github.com/github/spec-kit/blob/c0fe0e43cd728ebc3dd1f714343f3921510a157f/spec-driven.md) | official open-source documentation · commit `c0fe0e43cd728ebc3dd1f714343f3921510a157f` plus retained content | specification, plan, task, artifact-analysis, and workflow mechanisms are documented | intended capability, not independent effectiveness |
| `M-S06` | [LangGraph workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents) | official framework documentation · exact mutable-page snapshot; no repository commit established · field probe only | documents predetermined workflows, autonomous tool loops, and explicit state graphs | framework capability only; does not define “Graph Engineering” or justify adoption |
| `M-S07` | [Coding Agents are Effective Long-Context Processors](https://arxiv.org/abs/2603.20432v1) · `2026-03-20` | primary preprint · arXiv `v1` · fixed snapshot | filesystem and executable tools externalized long-context processing in the studied benchmarks | does not show that arbitrary long projects retain goals or avoid stale state |
| `M-S08` | [SpecBench: Measuring Reward Hacking in Long-Horizon Coding Agents](https://arxiv.org/abs/2605.21384v1) · `2026-05-20` | primary preprint · arXiv `v1` · fixed snapshot | visible-suite success and held-out compositional behavior diverged in the benchmark | benchmark-specific; richer visible compositional tests had mixed effects and may either improve coverage or enlarge proxy optimization |
| `M-S09` | [BackendForge](https://arxiv.org/abs/2607.11042v1) · `2026-07-13` | primary preprint · arXiv `v1` · fixed snapshot | deployable end-to-end behavior was harder than satisfying the initial oracle in the tested backend tasks | benchmark-specific and recent preprint |
| `M-S10` | [When Agents Do Not Stop](https://arxiv.org/abs/2607.01641v1) · `2026-07-02` | primary preprint · arXiv `v1` · fixed snapshot | re-enterable feedback paths can reach costly or state-growing operations without effective bounds | supports bounded-path analysis, not this project's particular stopping state or threshold |

### 4.2 Practitioner and field evidence

Practitioner material is used only to generate failure probes and maintenance
requirements. It is not used to estimate incidence or prove causality.

| ID | Source · observed state on `2026-07-25` | Field observation used as a probe | Counterweight and replay limit |
|---|---|---|---|
| `M-P01` | [Codex issue 35226](https://github.com/openai/codex/issues/35226) · open | repeated reads, loss of progress, and credit consumption were reported in one long-running task | mutable issue without R10 snapshot; no incidence or causal estimate |
| `M-P02` | [Codex issue 21269](https://github.com/openai/codex/issues/21269) · closed | duplicated active instruction packets were reported in compacted history | mutable issue without R10 snapshot; closure does not establish historical prevalence |
| `M-P03` | [Reddit: Context Compaction](https://www.reddit.com/r/codex/comments/1r1qya8/context_compaction/) · posted `2026-02-11` | a user reported post-compaction forgetting and commenters proposed an external progress file | editable anecdotal discussion without R10 snapshot |
| `M-P04` | [Reddit: Context compactment is completely broken?](https://www.reddit.com/r/codex/comments/1uy70sl/context_compactment_is_completely_broken/) · posted `2026-07-16` | one user reported old screenshots and already-fixed state being treated as current | editable, version-specific anecdote without R10 snapshot |
| `M-P05` | [Reddit: How many here manage context in Codex?](https://www.reddit.com/r/codex/comments/1v4xisu/how_many_here_manage_context_in_codex/) · posted `2026-07-24` | the same discussion contains separate positive-continuity and external-milestone-file anecdotes | the anecdotes do not establish frequency or causality |
| `M-P06` | [Reddit: In praise of Codex context management](https://www.reddit.com/r/codex/comments/1t1w5dn/in_praise_of_codexs_context_management_and/) · posted `2026-05-02` | one user reported good continuity while maintaining repository rules and an operations log | positive editable anecdote; useful contrary probe, not effect evidence |

The mixed practitioner record matters: the correct control is not “assume
compaction always fails.” It is “make recovery independent of whether
compaction happens to work on a given run.”

## 5. External facts versus local decisions

The following table prevents external evidence from being relabelled as proof
that a project-specific control is necessary or sufficient.

| ID | Claim type and current status | External basis | Project inference or policy | Required local falsification |
|---|---|---|---|---|
| `M-C01` | `project_policy`; adopted | local `AGENTS.md` and `PROJECT_CHARTER.md`, hash-bound in the R10 manifest; `M-S02` is supporting external context only | repository state, not chat history, is the durable recovery authority | a fresh-context run must recover exact current goal, blocker, route, and prohibitions; stale prose must fail |
| `M-C02` | `candidate_control`; unvalidated end to end | `audits/PROJECT_GOVERNANCE_ADVERSARIAL_REVIEW_R10_2026-07-25.md`, SHA-256 `9a245d75ed44a763175f34fba61593a6a1b50346b261d925c50016064bc79633`, finding `R10-CRIT-STATE-FRESHNESS`; field probes are non-authoritative | derive visible status from structured, versioned facts | mutate only a structured blocker or route and require all visible state blocks to become stale |
| `M-C03` | `candidate_control`; verifier tests required | `M-S06` proves graph mechanisms exist, not their necessity | use explicit scheduling edges, activation, joins, and failure propagation because the current packets require branching and rejoining | reject cycles, unreachable nodes, premature activation, write conflicts, and a missing join invariant |
| `M-C04` | `candidate_control`; threshold uncalibrated | `M-S10` | use a budget and a distinct no-progress terminal state for local loops | unchanged blocker/evidence fingerprints must stop at the declared bound; threshold remains a policy choice |
| `M-C05` | `candidate_control`; comparison pending | `M-S08`, `M-S09` | keep a withheld end-to-end evaluation surface outside builder control | a visible-pass/withheld-fail fixture must block completion; compositional and adversarial suite design remain locally unvalidated |
| `M-C06` | `engineering_inference`; not an external fact | evaluator separation in `M-S02` plus bias evidence in the companion failure report | fresh context reduces trajectory sharing but does not prove reviewer independence | record model, source, oracle, write-access, and candidate-identity overlap; shared-premise consensus must not self-authorize |
| `M-C07` | `candidate_control`; verifier tests required | `M-S07` positive tool evidence and mixed `M-P01`–`M-P06` field probes | recovery should reject stale or contradictory routes | inject superseded facts and two live routes; derivation must fail closed |
| `M-C08` | `project_metric_policy`; longitudinal result absent | vendor reports discuss human attention; field evidence reports token and repetition burden | track elapsed time, model/tool use, interventions, false alarms, and maintenance work | the same-task comparison and paper-use period must include human burden; no benefit claim is allowed before measurement |

The fixed same-task comparison remains necessary because none of these sources
establish the best control stack for this repository.

## 6. Current preregistered same-task comparison

The only current fixed comparison is
`research/SAME_TASK_METHOD_COMPARISON_PREREGISTRATION_R9_2026-07-25.json`,
SHA-256
`948c4d06a0c3835c7e508a7700beba59e73f4875b04ffd74d9c465216debb5ef`.
Its status is `preregistered_not_executed`.

R9 fixes a company-actions and point-in-time data-policy synthesis task using a
finite frozen corpus. It compares exactly two arms:

1. `common_contract_only`;
2. `common_contract_plus_minimum_core`.

Both arms already share the same governed task/output contract, citations,
counterevidence, unknown, paper-only, strict-JSON, no-tool, no-network, and
`bounded_incomplete` requirements. The contrast estimates only the marginal
effect of the added minimum-core wrapper. The baseline must not be described as
ungoverned ordinary prompting, and R9 cannot establish the value of the full
project governance stack.

R9 is presently blocked before generation: the required external independent
stateless-process harness, runtime binding, complete tree manifests, digest
sidecars, and capability/package-fit receipts do not exist. The project parent
thread or its native subagents are explicitly ineligible substitutes. This
report does not authorize relaxing that blocker or executing the experiment in
an unregistered configuration.

A daily-market-data provider review with five cumulative method conditions may
be useful as a future experiment, but it is currently an
`unregistered_future_proposal`. It cannot replace R9, inherit R9's
preregistration status, or support any method-adoption claim until separately
preregistered before outputs exist and independently reviewed.

## 7. Living-review triggers

This research must be re-evaluated when any of the following occurs:

- the project changes model, agent runtime, compaction behavior, or principal
  orchestration tool;
- a source used for an architecture decision is revised or retracted;
- a new field failure matches an unmodeled failure class;
- a control repeatedly produces false positives, false negatives, or excessive
  human burden;
- the project moves from one user to multiple users;
- paper-only execution authority changes;
- the fixed same-task comparison materially contradicts a current decision;
- the scheduled maximum age for this evidence expires.

Re-evaluation means reopening fixed-version sources and re-snapshotting mutable
decision-bearing sources, recording revision state, searching explicitly for
contrary evidence, updating only claims supported by the new evidence, and
obtaining a fresh independent entailment review. A calendar reminder or
successful script exit is not itself a research verdict.

## 8. Open unknowns

- The bounded R10 source set does not establish a technical standard, origin,
  adoption rate, or accepted definition for “Graph Engineering.”
- No evidence reviewed establishes a universal context length, loop count,
  retry count, or agent count that is safe.
- Fresh-context evaluation reduces shared trajectory exposure but does not
  eliminate shared-model, shared-source, shared-test, or shared-specification
  bias.
- The best trade-off among governance strength, execution speed, cost, and
  supervision fatigue for this project remains unmeasured.
- R9 is preregistered but blocked before generation and has not been executed.
- Review `10B` blocked the preceding revision. This repair has not yet received
  a replacement independent acceptance review.
