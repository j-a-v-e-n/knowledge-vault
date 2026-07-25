# R8 / RS-03 claims packet for an independent reviewer

This file is review input, not a review. The RS-03 author has supplied claim text, exact snapshot IDs/ranges, limitations, and decision effects but has not supplied any independent verdict.

Required reviewer output per claim:

- `reviewer_locator`
- `review_input_sha256`
- `claim_id`
- `verdict`
- `reason`
- `checked_source_ranges`
- `overclaim_or_missing_counterevidence`

Allowed design-closure verdicts are only `entailed` or `contested_non_decision_changing`.

## RS03-R8-C01 — CRSP calculation-context boundary

- claim_text: In CRSP's July 2026 Market Indexes methodology, ordinary cash dividends are not applied as a start-of-day price adjustment; same-ex-date cash dividends and stock splits are stated in post-split terms; split factors alter holdings on the ex-date with offsetting price effects; security total return assumes dividend reinvestment at end of day on the ex-date.
- impact: high
- evidence_cluster_ids: `U-CRSP-INDEX-METHOD`
- source_snapshot_ids: `RS03-SNAP-CRSP-JULY-2026`
- checked ranges requested: PDF pages 51-55 and 69-70; extracted lines 2469-2497, 2621-2632, and 3334-3352
- limitations: CRSP Market Indexes semantics are not a universal paper-account settlement rule and do not prove candidate-provider behavior.
- decision_effect: require separate `market_return_series` and `paper_account_ledger` calculation contexts.

## RS03-R8-C02 — non-substitutable corporate-action times

- claim_text: Current official exchange specifications expose distinct declared or announcement, ex, record, payment or effective, updated, and report-publication dates; those fields describe different facts and cannot substitute for actual availability, retrieval, or decision time.
- impact: high
- evidence_cluster_ids: `U-NYSE-CA`, `U-CBOE-CA`
- source_snapshot_ids: `RS03-SNAP-NYSE-V3.2A`, `RS03-SNAP-CBOE-LIVE`
- checked ranges requested: NYSE PDF pages 9-12 / extracted lines 354-389 and 437-489; Cboe saved HTML lines 1181-1216
- limitations: date-granular update fields do not prove the first instant a downstream provider made the record available.
- decision_effect: preserve event, effective, ex, published, available, retrieved, and decision time separately; retain record and pay time as typed metadata.

## RS03-R8-C03 — append-only downstream revision lineage

- claim_text: Official exchange records can be added, updated, cancelled, or unchanged, and CRSP may issue newly named restatement files while later presenting the newest restatement as the official record. A downstream decision system therefore cannot rely on the provider to preserve every version it previously observed.
- impact: high
- evidence_cluster_ids: `U-CBOE-CA`, `U-NYSE-CA`, `U-CRSP-INDEX-METHOD`
- source_snapshot_ids: `RS03-SNAP-CBOE-LIVE`, `RS03-SNAP-NYSE-V3.2A`, `RS03-SNAP-CRSP-JULY-2026`
- checked ranges requested: Cboe saved HTML lines 1181-1216; NYSE extracted lines 460-489; CRSP PDF pages 81-82 / extracted lines 3945-3953
- limitations: CRSP's policy governs Market Indexes and cannot be generalized as the revision policy of every provider.
- decision_effect: every revision is a new exact-byte snapshot with provider-native status, observation time, parent hash, and supersession link; decision inputs are never overwritten.

## RS03-R8-C04 — minimum automatic split/cash-dividend boundary

- claim_text: Even split and ordinary cash-dividend handling has material boundaries: forward and reverse ratios, same-ex-date post-split dividend terms, update/cancellation replay, and distinct ex versus payment/effective time.
- impact: high
- evidence_cluster_ids: `U-CRSP-INDEX-METHOD`, `U-NYSE-CA`, `U-CBOE-CA`
- source_snapshot_ids: `RS03-SNAP-CRSP-JULY-2026`, `RS03-SNAP-NYSE-V3.2A`, `RS03-SNAP-CBOE-LIVE`
- checked ranges requested: CRSP PDF pages 51-55; NYSE PDF pages 9-12; Cboe saved HTML lines 1181-1216
- limitations: the sources do not freeze taxes, withholding, fractional shares, cash in lieu, due bills, or mixed/special actions.
- decision_effect: automatic V1 is restricted to unambiguous split and ordinary cash-dividend fixtures; all other cases fail closed to `pending_manual`.

## RS03-R8-C05 — historical observation versus latest-restated replay

- claim_text: A true historical snapshot is not equivalent to a current database filtered by an event or input date because later corrections, deletions, currency changes, methodology changes, and backfills can change ordinary historical output.
- impact: high
- evidence_cluster_ids: `U-FACTSET-PIT`, supporting `U-CRSP-INDEX-METHOD`
- source_snapshot_ids: `RS03-SNAP-FACTSET-PIT`, `RS03-SNAP-CRSP-JULY-2026`
- checked ranges requested: FactSet PDF pages 3-7 / extracted lines 29-35, 64-103, and 173-201; CRSP PDF pages 81-82
- limitations: FactSet's method concerns consensus estimates and does not prove Tiingo or every equity provider's behavior.
- decision_effect: require mutually exclusive `as_observed_at_decision` and `latest_restated_at_retrieval` replay views.

## RS03-R8-C06 — future corporate-action back-adjustment leakage

- claim_text: A historical price series back-adjusted using splits, dividends, or other actions that occurred after a simulated decision can leak future information into price-level and derived-feature decisions.
- impact: high
- evidence_cluster_ids: `U-DB-SEVEN-SINS`, supporting `U-PIT-BACKTEST-2026` and `U-KIBOT-ADJUSTMENT`
- source_snapshot_ids: `RS03-SNAP-DB-SEVEN-SINS`
- checked ranges requested: Deutsche Bank PDF pages 11-13 / extracted lines 669-730 and 796-804
- limitations: the worked empirical example is strategy-specific; magnitude cannot be generalized. The retrieved 2026 preprint was explicitly not peer-reviewed and is not the decisive saved snapshot.
- decision_effect: require `raw_as_traded`, `pit_adjusted`, or `latest_back_adjusted`, plus adjustment cutoff and action lineage; latest-back-adjusted values fail the decision-time gate.

## RS03-R8-C07 — license scope and termination are data gates

- claim_text: Market-data rights are scoped by provider, plan or addendum, user classification, purpose, redistribution, term, and termination; personal use or API access does not imply a right to redistribute, retain, or continue using cached data after termination.
- impact: high
- evidence_cluster_ids: `U-TIINGO`, `U-MARKETDATA-TERMS`
- source_snapshot_ids: `RS03-SNAP-TIINGO-TOS-2026-07-18`, `RS03-SNAP-MARKETDATA-TERMS`
- checked ranges requested: Tiingo saved HTML lines 29, 408, and 676; MarketData saved HTML lines 1109 and 1167
- limitations: no account-specific terms were accessed; this is not legal advice. Tiingo's public terms did not visibly grant post-termination cache retention, but absence of an express grant is not an express deletion duty.
- decision_effect: retain the fail-closed `unknown`, `allowed`, `restricted`, `expired`, `revoked` license state machine bound to exact terms bytes and scope.

## RS03-R8-C08 — external paper is a read-only observer

- claim_text: Alpaca's current public Paper Trading documentation limits Paper Only accounts to IEX data and lists material simulation omissions, including dividends; external paper results therefore cannot be authoritative for local corporate-action accounting or overwrite the local ledger.
- impact: high
- evidence_cluster_ids: `U-ALPACA-PAPER`
- source_snapshot_ids: `RS03-SNAP-ALPACA-PAPER-CURRENT`
- checked ranges requested: saved HTML body containing Paper Only entitlement, Paper-vs-Live omissions, Rules and Assumptions, and embedded document update metadata
- limitations: no private account, key, endpoint, order, entitlement, or reconciliation was tested.
- decision_effect: external paper remains a read-only observation and reconciliation source; all conflicts are logged and never auto-resolved.

## Required contradiction checks

- CRSP ex-date return reinvestment versus exchange payment-date cash settlement may be a context distinction rather than a contradiction; reviewer must verify that the claims do not collapse them.
- Tiingo terms retained `Version 1` while showing a later last-updated date; reviewer must check the conclusion that version label alone is insufficient.
- Alpaca says paper works similarly end to end but separately lists omissions; reviewer must ensure the observer claim preserves both statements.
- Provider-specific deletion duties must not be generalized from MarketData or CME to Tiingo.

