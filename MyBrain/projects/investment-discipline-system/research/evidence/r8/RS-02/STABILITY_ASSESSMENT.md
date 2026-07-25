# R8 / RS-02 stability assessment

- Discovery freeze: `DISCOVERY_FREEZE.md`
- Discovery freeze SHA-256:
  `40e4fe8b133c95d9e0c92630fedb8e789c6376a075dfed6a3a964b437d641c07`
- S1 retrieval UTC: `2026-07-25T16:18:58Z`
- S2 retrieval UTC: `2026-07-25T16:19:17Z`
- S3 retrieval UTC: `2026-07-25T16:19:44Z`

## S1 comparison

`R8-RS02-S1` returned both positive and negative multi-agent evidence. The
peer-reviewed `Voting or Consensus?` source shows that the decision protocol,
task type, answer diversity, number of agents, and discussion rounds alter
benchmark performance. It also reports substantial compute cost and convergence
on similar responses. Other visible results describe conformity, correlated
errors, minority suppression, and adversarial persuasion.

Delta verdict: `no_new_high_impact_delta`.

Reason: this confirms the R7 boundary already frozen before S1: agent count is
not the architecture criterion; objective-oracle sampling or voting may be
tested narrowly, while interaction, shared evidence, and unsupported consensus
remain subject to lineage and infection probes. It refines wording but does not
reverse a decision or add a new failure class.

## S2 comparison

`R8-RS02-S2` returned concrete implementation issues for stale writes, session
replay, duplicate memory processing, cross-instance scope leakage, and malformed
checkpoint history. These issue reports are existence evidence only and do not
establish incidence.

Delta verdict: `new_high_impact_delta`.

### S2-AD01 — add authority/scope and concurrency to the memory contract

Every persisted item must bind its content role and authority separately:
historical user/assistant text is untrusted reference data, not a current
instruction. The record and retrieval gate must carry project, thread/session,
agent/profile, source role, instruction-authority state, and applicable scope.

A memory write derived from an older context must also carry the base revision
it observed. Replace/update requires compare-and-swap against the current head;
on mismatch the system must reject, quarantine, explicitly merge with lineage,
or ask for human resolution. A stale flush may not silently overwrite a newer
record.

### S2-AD02 — make replay structural integrity a precondition

Before resume, validate that each persisted tool call has the required matching
result and that the checkpoint/event sequence is structurally complete. Invalid
history is quarantined or repaired under an explicit rule; it is never replayed
as valid state. Tool-call and tool-result persistence must be tested around
every interruption boundary.

Decision impact: these are executable extensions to discovery deltas FD-AD01,
FD-AD02, and FD-AD04. The last high-impact delta therefore occurred at S2.

## S3 comparison

`R8-RS02-S3` returned practitioner reports about unbounded loops, context
exhaustion, handoff artifacts, memory layering, and decision-context loss. They
are useful as failure probes and user-burden indicators only. All fall within
the already frozen termination/budget, context-reset/handoff, memory
type/scope, and replay contracts. Several results are product promotion,
second-hand claims, mirrors, user pages, or false positives.

Delta verdict: `no_new_high_impact_delta`.

No S3 result reversed a decision, introduced a new high-impact failure class,
or opened a critical/major contradiction. Additional support and wording do
not count as a delta.

## Stability predicate

`passing_rule=true`.

The last high-impact architecture/decision delta occurred at S2, and the later
reserved query S3 produced no new high-impact failure class and no open
critical/major contradiction. No sixth query was executed.

This does not close the topic. Independent per-claim entailment review remains
absent by assignment boundary, so the overall topic status must remain
`bounded_incomplete`.
