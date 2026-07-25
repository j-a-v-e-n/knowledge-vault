# R8 / RS-02 discovery freeze

- Freeze UTC: `2026-07-25T16:17:56Z`
- Preregistration commit: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- Preregistration commit UTC: `2026-07-25T16:13:44Z`
- Preregistration SHA-256: `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`
- D1 retrieval UTC: `2026-07-25T16:17:05Z`
- D2 retrieval UTC: `2026-07-25T16:17:14Z`
- Status: frozen after D1 and D2 and before S1

This file freezes the discovery-stage candidate claims and architecture/decision
deltas. It is not an independent entailment review and does not close RS-02.
Search-result snippets are locators only until selected source bytes and ranges
are saved and checked.

## Frozen discovery claims

### FD-C01 — supersession is a distinct memory-maintenance failure

In the settings reported by `Supersede` (`arXiv:2606.27472`), a bounded,
self-maintained memory can select a stale value even when the same model can
answer from full context. The claim is limited to the paper's LongMemEval
knowledge-update experiments; it does not establish a natural production
incidence or universal model failure.

### FD-C02 — implicit invalidation requires more than latest-item retrieval

`STALE` (`arXiv:2605.06527`) defines cases where a later observation invalidates
an earlier state without explicit negation and separates state resolution,
resistance to a stale premise, and downstream policy adaptation. The candidate
claim is that a memory gate must test these behaviors separately. The benchmark
does not prove that any proposed implementation is sufficient.

### FD-C03 — functionally incompatible memories can contaminate an answer

`MemGuard` (`arXiv:2605.28009`) studies heterogeneous memory contamination:
semantically related records with different functional roles can be retrieved
as interchangeable evidence. Type separation plus selective routing is a
candidate mitigation, not a proven universal solution.

### FD-C04 — stored experience quality can propagate into later behavior

Xiong et al., `How Memory Management Impacts LLM Agents`
(`ACL 2026, 2026.acl-long.27`), report experience-following behavior under their
controlled tasks. This supports treating an unverified past trajectory as
tainted input and tracking later outcome labels. It does not support a general
failure rate.

### FD-C05 — checkpoint restore can create semantic, not merely byte-identical, replay

`ACRFence` (`arXiv:2603.20625`) reports that an LLM may re-synthesize a changed
request after restore, allowing an external server to treat a repeated intent
as a new operation. The paper's two candidate failure classes are Action Replay
and Authority Resurrection. This is limited to the authors' threat model and
proof-of-concept; the proposed mitigation is not assumed sufficient for this
project.

### FD-C06 — an auditable episode package is evidence, not a correctness oracle

`AI Harness Engineering` (`arXiv:2605.13357`) proposes trace-based episode
packages covering task state, observability, failure attribution, verification,
permissions, and intervention recording. A trace package can make a run
inspectable, but its existence alone does not entail correct replay or correct
external effects.

### FD-C07 — compaction alone remains insufficient in the cited vendor experiments

The D2-visible Anthropic long-running harness sources preserve the R7 result:
their reported long-application experiments still required externalized state,
resets, decomposition, and verification beyond compaction. This remains
vendor-reported evidence and does not estimate incidence across projects.

## Frozen architecture / decision deltas

### FD-AD01 — add a versioned memory-assertion state contract

High-impact delta. A memory record cannot become an authoritative fact merely
because it was retrieved. The executable contract must bind an atomic assertion
to source/provenance, observation and retrieval time, validity interval or
as-of boundary, supersession links, and a state such as `active`,
`superseded`, `contested`, or `quarantined`. A decision-time gate must reject
stale, contested, provenance-missing, or cross-domain records unless a
deterministic or human-approved exception is recorded.

### FD-AD02 — expand the memory fault matrix

High-impact delta. Add direct correction, implicit invalidation, stale-premise,
cross-domain leakage, functional-type mismatch, unverified-trajectory
contamination, and restart-after-supersession probes. Passing requires the
current assertion to be selected, the stale premise to be rejected, downstream
behavior to use the current state, and the supersession lineage to remain
replayable. These are proposed acceptance tests, not tests already executed.

### FD-AD03 — replace retry-only reasoning with a semantic replay fence

High-impact delta. Before an irreversible side effect, bind a stable operation
identity to normalized intent, authority/capability epoch, preconditions, and
the checkpoint lineage. Persist an external-effect receipt. On resume,
reconcile observed external state before any retry. If regenerated semantics or
authority differ, require explicit `replay`, `fork`, `compensate`, or
human-blocked handling. Do not claim exactly-once behavior from a checkpoint or
idempotency-key label alone.

### FD-AD04 — make crash/replay evidence an episode contract

High-impact refinement. The replay test artifact must preserve checkpoint and
parent identity, pinned model/prompt/tool/harness revisions, requested versus
observed effects, interruption point, resume decision, termination/budget
state, and reconciliation outcome. Missing effect receipts make the replay
predicate false.

## R7 decisions retained without a new discovery delta

- Blind identity, order swap, pinned judge revision, and deterministic or human
  reference remain required for judge metamorphic gates.
- Position, compaction, restart, and stale-request probes remain required for
  long-context behavior.
- Atomic claim lineage, quarantine, rollback, and an infection oracle remain
  required for multi-agent flows.
- No graph runtime is adopted merely because it exposes checkpoint primitives.
- Long-term memory remains non-authoritative until the new state contract and
  fault matrix are implemented and passed.

## Stability comparison rule

S1, S2, and S3 must be compared against this freeze in order. A later source
that only adds support or wording is not a delta. A new high-impact failure
class, decision reversal, or open critical/major contradiction is a delta. If
S3 produces such a delta, the topic is `bounded_incomplete`; no sixth query is
permitted.
