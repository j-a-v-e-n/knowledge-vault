# R8 / RS-03 discovery freeze

- Frozen at UTC: `2026-07-25T16:19:34Z`
- Discovery queries already executed exactly once: `R8-RS03-D1`, then `R8-RS03-D2`
- Stability queries executed before this freeze: none
- Freeze rule: the claims and decision deltas below are the discovery-stage state. Later S1–S3 evidence may support, contest, or add a new delta, but it must not rewrite this section.
- Entailment status: author assessment only; no independent reviewer verdict is claimed.

## Frozen atomic claims

### RS03-R8-D-C01

- topic_id: `RS-03`
- claim_text: In CRSP's July 2026 Market Indexes methodology, ordinary cash dividends are not applied as a start-of-day price adjustment; a cash dividend sharing an ex-date with a stock split is reported in post-split terms; forward and reverse splits change holdings by a split factor on the ex-date while the proportional price change offsets the share change; security total return assumes dividends are reinvested at end of day on the ex-date.
- impact: high
- evidence_cluster_ids: `U-CRSP-METHOD`
- source_snapshot_ids: `RS03-SNAP-CRSP-JULY-2026` (bytes/hash pending at freeze time)
- source_ranges:
  - CRSP Market Indexes Methodology Guide, document header, PDF page 1: `JULY 2026`, `Document last modified July 1, 2026`
  - PDF pages 51–52, extracted lines 1946–1963
  - PDF page 54, extracted lines 2062–2067
  - PDF pages 69–70, extracted lines 2665–2683
- author_entailment: entailed for CRSP Market Indexes calculation semantics
- limitations: This is an index methodology, not a universal paper-account settlement rule and not proof of any candidate data provider's implementation. Ex-date return reinvestment must not be silently reused as the paper ledger's cash-credit time.
- decision_effect: Freeze an explicit `calculation_context` boundary between market-return normalization and paper-ledger accounting. Gold samples must prove each context separately.

### RS03-R8-D-C02

- topic_id: `RS-03`
- claim_text: Current official exchange specifications expose distinct declared or announcement, ex, record, payment or effective, updated, and report-publication dates; those fields describe different facts and cannot substitute for actual availability, retrieval, or decision time.
- impact: high
- evidence_cluster_ids: `U-NYSE-CA`, `U-CBOE-CA`
- source_snapshot_ids:
  - `RS03-SNAP-NYSE-V3.2A` (bytes/hash pending at freeze time)
  - `RS03-SNAP-CBOE-LIVE` (bytes/hash pending at freeze time)
- source_ranges:
  - NYSE Corporate Actions Client Specification v3.2a, PDF pages 9–12, extracted lines 244–264 and 316–351
  - Cboe BZX U.S. Listing Corporate Actions Specification, extracted lines 30–50 and 211–231
  - Cboe BZX U.S. Listing Corporate Actions Specification, extracted lines 297–307
- author_entailment: entailed for the named exchange specifications
- limitations: A field named `Updated Date` is date-granular and is not itself a complete point-in-time availability proof. The specifications do not prove what a downstream provider exposed to this project at any particular instant.
- decision_effect: Strong-freeze separate `event_time`, `effective_time`, `ex_time`, `published_time`, `available_time`, `retrieved_time`, and `decision_time`; preserve `record_time`, `pay_time`, and provider-native date fields as typed source metadata rather than aliases.

### RS03-R8-D-C03

- topic_id: `RS-03`
- claim_text: Official exchange records can be added, updated, cancelled, or unchanged, and CRSP's July 2026 restatement policy may issue newly named restatement files while later presenting the newest restated data as the official record. Therefore a downstream decision system cannot rely on the provider to preserve every previously observed version.
- impact: high
- evidence_cluster_ids: `U-CBOE-CA`, `U-NYSE-CA`, `U-CRSP-METHOD`
- source_snapshot_ids:
  - `RS03-SNAP-CBOE-LIVE` (bytes/hash pending at freeze time)
  - `RS03-SNAP-NYSE-V3.2A` (bytes/hash pending at freeze time)
  - `RS03-SNAP-CRSP-JULY-2026` (bytes/hash pending at freeze time)
- source_ranges:
  - Cboe specification, extracted lines 211–219 and 297–305
  - NYSE v3.2a, PDF pages 11–12, extracted lines 316–351
  - CRSP July 2026 guide, Appendix F, PDF pages 81–82, extracted lines 3164–3197
- author_entailment: entailed for source revision/cancellation behavior; the downstream consequence is a design inference
- limitations: CRSP's policy governs CRSP Market Indexes and must not be generalized to every data product or provider. A provider's replacement behavior does not by itself prescribe this project's storage schema.
- decision_effect: Keep revisions append-only locally. Each revision must bind exact source bytes, observed retrieval time, provider-native update/cancel status, parent snapshot hash, and a supersession relation; no revision may mutate a decision input already used.

### RS03-R8-D-C04

- topic_id: `RS-03`
- claim_text: Split and cash-dividend processing has non-trivial boundary cases even before mergers or spin-offs: same-ex-date cash dividends can be stated in post-split terms, forward and reverse split ratios move shares inversely to price, actions can be cancelled or updated, and payment/effective time differs from ex-date.
- impact: high
- evidence_cluster_ids: `U-CRSP-METHOD`, `U-NYSE-CA`, `U-CBOE-CA`
- source_snapshot_ids:
  - `RS03-SNAP-CRSP-JULY-2026` (bytes/hash pending at freeze time)
  - `RS03-SNAP-NYSE-V3.2A` (bytes/hash pending at freeze time)
  - `RS03-SNAP-CBOE-LIVE` (bytes/hash pending at freeze time)
- source_ranges:
  - CRSP July 2026 guide, extracted lines 1946–1963 and 2062–2067
  - NYSE v3.2a, extracted lines 262–305 and 316–351
  - Cboe specification, extracted lines 211–231
- author_entailment: entailed for the listed boundary facts; test selection is a design inference
- limitations: The sources do not define this project's fractional-share, tax, withholding, cash-in-lieu, or settlement policy. Those remain outside automatic V1 unless separately frozen.
- decision_effect: Automatic Paper V1 remains limited to frozen split and ordinary cash-dividend semantics. Required gold boundaries are split-only (forward and reverse), cash-dividend-only, same-ex-date split plus cash dividend with post-split amount ordering, and update/cancellation replay. All mixed, conditional, special, fractional, tax, rights, spin-off, merger, or unknown cases remain `pending_manual`.

## Frozen discovery decision deltas

### RS03-R8-D-DELTA-01 — calculation-context separation

- class: architecture / high impact
- prior state: R7 separated event/ex/pay timing but did not make the market-return-versus-paper-ledger calculation context an explicit contract discriminator.
- frozen delta: Add a required `calculation_context` (at minimum `market_return_series` or `paper_account_ledger`) to corporate-action transformations. CRSP ex-date reinvestment may define a return-series gold result; it cannot cause an ex-date cash credit in the local authoritative ledger without a separately frozen ledger rule.
- executable landing: provider-neutral contract plus gold tests; no provider onboarding required.

### RS03-R8-D-DELTA-02 — observable revision lineage

- class: contract / high impact
- prior state: R7 required append-only revision and a parent snapshot.
- frozen delta: Make provider-native update/cancel status, source artifact identity, exact-byte hash, observation time, and `supersedes_snapshot_id` mandatory. Preserve every decision-used version even when the provider later exposes only its newest official record.
- executable landing: revision schema and mutation/replay tests.

### RS03-R8-D-DELTA-03 — corporate-action gold boundary

- class: test gate / high impact
- prior state: R7 limited automatic V1 handling to split and cash dividend but did not freeze the complete minimum gold boundary.
- frozen delta: The minimum automatic-action gate must cover forward split, reverse split, ordinary cash dividend, same-ex-date split plus cash dividend in post-split terms, and update/cancellation replay in both calculation contexts. Unspecified mixed or exceptional actions fail closed to `pending_manual`.
- executable landing: deterministic gold fixtures and fail-closed tests.

## Discovery-stage contradictions and retained uncertainty

- CRSP's return-series reinvestment convention and exchange payment-date semantics answer different accounting questions. Treating either as universally authoritative would be a category error.
- `Updated Date` and a report's publication date improve lineage but do not prove the first instant a downstream provider made a record available.
- Current official methods show revision and cancellation behavior but do not establish candidate-provider licensing, retention rights, point-in-time replay, or account-specific capability.
- The external paper broker remains a read-only observer by prior frozen design; D1/D2 produced no evidence that would justify allowing it to overwrite the local authoritative ledger.

