# R8 / RS-03 S1 delta record

- Query: `R8-RS03-S1`
- Exact query: `point in time market data correction revision available timestamp methodology`
- Search-call window UTC: `2026-07-25T16:20:49Z` → `2026-07-25T16:20:57Z`
- Delta classified at UTC: `2026-07-25T16:21:24Z`
- Entailment status: author assessment only; no independent reviewer verdict is claimed.

## Atomic claim RS03-R8-S1-C01

- topic_id: `RS-03`
- claim_text: A point-in-time view that reconstructs what was available at a historical cutoff is not equivalent to a latest database filtered by an input or event date. Later corrections, deletions, currency changes, methodology changes, and backfills can alter ordinary historical output while a true as-of snapshot preserves the historical view.
- impact: high
- evidence_cluster_ids: `U-FACTSET-PIT`, `U-MESSARI-METHOD`; discovery support from `U-CRSP-METHOD`
- source_snapshot_ids:
  - `RS03-SNAP-FACTSET-PIT` (bytes/hash pending)
  - `RS03-SNAP-MESSARI-METHOD` (bytes/hash pending; optional supporting snapshot)
  - `RS03-SNAP-CRSP-JULY-2026` (bytes/hash pending)
- source_ranges:
  - FactSet, *Accurately Backtesting Financial Models Through Point-in-Time Consensus Estimates*, PDF pages 3–7, extracted lines 57–97 and 128–160
  - Messari Market Data Methodology, extracted lines 193–223
  - CRSP July 2026 guide, Appendix F, extracted lines 3164–3197
- author_entailment: entailed for the named products' behavior; provider-neutral contract consequence is a design inference
- limitations: FactSet's source concerns consensus estimates and Messari's source concerns crypto market data; neither proves the behavior of Tiingo, Alpaca, or every equity-data provider. The sources establish a failure class and the need for an explicit replay semantic, not provider capability.
- decision_effect: Add an explicit point-in-time replay policy to every snapshot/query. Only the historically observed view may reconstruct a decision; corrected/latest views are separate post-hoc evidence and must not overwrite the decision input.

## High-impact delta RS03-R8-S1-DELTA-01

- class: contract / architecture / high impact
- relationship to discovery freeze: new high-impact refinement after the discovery freeze
- delta: Require `replay_view` with mutually exclusive values at least `as_observed_at_decision` and `latest_restated_at_retrieval`. An eligible decision snapshot must bind exact bytes whose `retrieved_time <= decision_time`; a latest-restated query may be used only for post-hoc evaluation and must retain lineage to, not replace, the decision snapshot.
- executable landing:
  - contract discriminator and fail-closed validation;
  - mutation test proving a later correction cannot change a prior decision hash or ledger effect;
  - differential fixture comparing `as_observed_at_decision` with `latest_restated_at_retrieval`.

## Stability effect

- New high-impact failure class: yes — a date-filtered latest database can masquerade as point-in-time even when event/input dates look valid.
- Decision reversal: no — this strengthens the append-only and no-future-information rules.
- Open critical or major contradiction: none identified from S1.
- Stability clock: reset at S1; at least one later reserved query must yield no new high-impact delta.

