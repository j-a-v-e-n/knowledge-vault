# RS-04 discovery-stage claim and delta freeze

- freeze_status: `frozen_before_R8-RS04-S1`
- frozen_at_utc: `2026-07-25T16:24:39Z`
- permitted discovery inputs: `R8-RS04-D1`, `R8-RS04-D2`, direct opens of their returned locators, and non-search inspection of repositories located by those results
- D1_receipt_sha256: `163d4f02536370e2fe9d22bbdda2fd7a919870f4c299b0f8ae370c948636a014`
- D2_receipt_sha256: `613dddf55504fbecc45d1ab935e19ea4377d13462d1c198cbae398b7bb59f5fd`
- stability_queries_executed_at_freeze: `none`
- review_boundary: author freeze only; this is not an independent entailment review

## Fixed discovery observations

1. `FinRL-X` and classic `FinRL` are separate code/revision lineages. Findings about classic FinRL are not projected onto FinRL-X.
2. A non-search shallow clone of the canonical FinRL-X repository fixed the current candidate at `AI4Finance-Foundation/FinRL-Trading@e65d6f0483ead7d2ef4a5fc940cdf960392a25c1`, retrieved by `2026-07-25T16:23:04Z`. Its commit date is `2026-05-02T23:12:36+08:00`.
3. The fixed FinRL-X tree carries an Apache-2.0 license and implements a positive modular counterexample: a common target-weight surface, a `bt`-based backtest layer, explicit walk-forward helpers, and paper/live Alpaca execution in one repository.
4. The same fixed FinRL-X tree has no tracked test path or test module even though `pytest` packages appear in dependency metadata. Its README assertion of strict no-lookahead semantics therefore does not come with an in-repository regression gate at this revision.
5. The fixed FinRL-X whole package crosses the Paper V1 authority boundary: it includes live broker calls and credentials, makes risk checking configurable, converts price-fetch failure to a default price, submits orders before writing the local JSON execution log, and stores neither the project’s requested→actual source chain nor authoritative event-ledger lineage in the weight interface.
6. The D2 implementation-risk study is direct evidence that equivalent strategy intent can diverge across engines because execution/accounting semantics differ. It is also counterevidence to a blanket “engines always disagree”: within the study’s tested zero-cost regime the reported engines agreed, while nonzero-cost semantics exposed divergence and defects.
7. The D2 temporal-non-interference paper is direct counterevidence to treating differential agreement as a look-ahead certificate: its author reports planted leaks missed by differential and tiling detectors.
8. `ml4t/backtest@459abd81f2f30dc70cf38a40da7591af3da2d02a` is a positive counterexample to the proposition that an open-source engine can expose only marketing claims. Its fixed tree includes an MIT license, explicit limitations, property/contract/regression tests, an independent in-tree oracle implementation, cross-engine adapters, and validation methodology.
9. The positive candidates do not overturn the narrower R7 decision: no examined package may replace the authoritative Paper V1 decision, deterministic gate, execution, or ledger path. They do rebut an over-broad interpretation of “whole-package exclusion”: a pinned package may remain eligible as a quarantined, read-only subprocess oracle if its observed gate and dependency cost pass a later admission trial.

## Frozen atomic claim candidates (`revision=discovery-v1`)

### R8-RS04-C01

- claim_text: At fixed commit `e65d6f0…`, FinRL-X provides a real modular target-weight/backtest/paper-live architecture, but the observed repository evidence is insufficient and boundary-incompatible for replacing Paper V1’s authoritative core.
- impact: `high`
- evidence_cluster_ids: `FINRLX-UPSTREAM`, `FINRLX-PAPER`
- author_entailment: `partially_entailed`
- limitations: The positive architecture is author/maintainer evidence; no independent FinRL-X correctness report was found in D1, and no live path was executed.
- decision_effect: `rejection` from authoritative core; `defer` as a future isolated research adapter candidate.

### R8-RS04-C02

- claim_text: Differential execution on one fixed snapshot is useful for exposing implementation risk, but agreement is not a causality or correctness certificate.
- impact: `high`
- evidence_cluster_ids: `IMPLEMENTATION-RISK-STUDY`, `TEMPORAL-NONINTERFERENCE`
- author_entailment: `entailed_at_discovery`
- limitations: Both papers are preprint-stage at the inspected revisions; the empirical study’s scope is its specified strategies, engines, assets, and cost regimes.
- decision_effect: `contract` strengthening for `DifferentialOracle`.

### R8-RS04-C03

- claim_text: A mature open-source engine with explicit semantics, tests, limitations, and parity adapters may be admitted whole as a quarantined non-authoritative oracle; “atomic reuse only” must not be interpreted as requiring code copying or rejecting every packaged executable.
- impact: `major`
- evidence_cluster_ids: `ML4T-BACKTEST-UPSTREAM`, `RAPTORBT-UPSTREAM`, `HFTBACKTEST-UPSTREAM`
- author_entailment: `decision_fit_candidate`
- limitations: D2 located the candidates; no independent issue/security result or same-task local admission run has yet established net benefit.
- decision_effect: `defer` to a pinned admission test; no authority transfer.

### R8-RS04-C04

- claim_text: A target-weight interface is an eligible atomic strategy-output pattern but is too lossy to carry Paper V1 decision authority unless source, temporal, human-decision, gate, and actual-execution lineage remain separate mandatory records.
- impact: `major`
- evidence_cluster_ids: `FINRLX-UPSTREAM`
- author_entailment: `decision_fit_candidate`
- limitations: This is a project-fit inference from the observed FinRL-X boundary and frozen Paper V1 requirements, not a claim that target weights are inherently unsafe.
- decision_effect: `contract` constraint on `ExternalResearchAdapter`; weights may be candidate output only.

## Frozen discovery architecture/decision deltas

### R8-RS04-DLT-01 — high-impact contract delta

Strengthen `DifferentialOracle` so every comparison receipt binds:

- fixed input snapshot hash and ordered rows;
- component repository/commit, dependency lock, command, environment, and adapter hash;
- named execution/accounting semantics rather than a generic “same strategy” label;
- per-field expected/actual values and tolerances;
- divergence classification, implementation-uncertainty interval where applicable, and whether the final decision conclusion changed;
- an explicit rule that agreement never satisfies prefix-causality or temporal-lineage gates;
- mandatory human/reviewer routing for every disagreement, with no automatic winner.

Reason: D2 produced a new high-impact failure class—semantic-profile mismatch and same-bug agreement can both survive a naive differential check.

### R8-RS04-DLT-02 — major manifest delta

Extend `ExternalComponentManifest` admission evidence with:

- tracked-test inventory and observed test command/receipt, separate from dependency declarations;
- declared versus observed default behavior;
- optional bypasses and fail-open/fabricated-default paths;
- whether live/broker/credential surfaces exist and proof they are unreachable in the adapter;
- documented limitations and revision freshness.

Reason: the fixed FinRL-X tree declares test dependencies without tracked tests and exposes behavior that is incompatible with Paper V1 when used whole.

### R8-RS04-DLT-03 — clarification, not a high-impact reversal

Clarify “whole-package exclusion”:

- still reject any package as an authoritative-core replacement;
- permit a pinned package, without copying its internals, as a quarantined read-only oracle only after admission;
- continue to prefer reimplementation of small architectural patterns when package surface or dependency cost is disproportionate.

This clarification preserves the R7 authority decision while retaining positive counterevidence.

## Frozen stability baseline

The last discovery-stage high-impact delta is `R8-RS04-DLT-01`. Under the preregistered passing rule, at least one later reserved stability query must yield no new high-impact failure class, no decision reversal, and no open critical/major contradiction. Any later delta will be recorded as a new revision rather than silently changing this freeze.
