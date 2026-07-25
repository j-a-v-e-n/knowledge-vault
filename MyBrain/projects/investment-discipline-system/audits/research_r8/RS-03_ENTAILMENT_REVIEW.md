# RESEARCH-REFRESH-R8 / RS-03 independent entailment review

## Review identity and integrity gate

- `review_scope`: `platform_observable_separate_thread`
- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input`: `audits/research_r8/RS-03_RAW_REPORT.md`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `expected_review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `raw_report_sha256_gate`: `pass`
- `claims_packet_sha256`: `4641342e448fc98b46eba88a0b396c84435dfaafd4b1ed987d49deb5d0ae6e63`
- `manifest_sha256`: `004ed1b4aa8f8ac0858929257aa6f5525cfeac6144b6e4d1f454d3b787cb478e`
- `network_or_new_search`: `none`

The manifest, every decisive exact-byte snapshot, and every declared deterministic text derivative were rehashed locally. Their hashes matched the manifest. Re-running `pdftotext -layout` against the saved CRSP, NYSE, FactSet, and Deutsche Bank PDFs reproduced the declared derivative hashes.

This is only a platform-observable separate-thread semantic review. It does not establish human independence, legal review, provider certification, private-account behavior, or implementation correctness.

## Per-claim entailment verdicts

### RS03-R8-C01 — CRSP calculation-context boundary

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C01`
- `verdict`: `entailed`
- `reason`: CRSP states that ordinary cash dividends do not receive a start-of-day price adjustment, that a cash dividend sharing an ex-date with a stock split is reported in post-split terms, that forward and reverse split factors change holdings with proportional offsetting price effects, and that total-return dividends are assumed reinvested at end of day on the ex-date. Those are calculation-context facts, not paper-ledger settlement facts.
- `checked_source_ranges`: `RS03-SNAP-CRSP-JULY-2026`, PDF pages 51-55 and 69-70; deterministic extracted lines 2469-2479, 2621-2626, 3330-3352, and 3359-3375.
- `overclaim_or_missing_counterevidence`: No blocking overclaim if the claim remains confined to CRSP Market Indexes. The report correctly preserves the counterboundary that ex-date return reinvestment is not payment-date cash settlement and does not prove candidate-provider behavior.

### RS03-R8-C02 — non-substitutable corporate-action times

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C02`
- `verdict`: `contested_non_decision_changing`
- `reason`: NYSE and Cboe define declared or announcement, ex, record, pay or effective, and updated dates as different facts. None of those fields establishes local retrieval or decision time, and date-granular updates do not prove first availability. The claim's report-publication component is present in the exact Cboe snapshot, but not inside the packet-requested Cboe lines 1181-1216; Cboe line 1103 defines `Report Date`, while line 1095 describes approximate report availability. This is a source-range locator defect, not a reason to collapse the time model.
- `checked_source_ranges`: `RS03-SNAP-NYSE-V3.2A`, PDF pages 9-12 / deterministic extracted lines 354-389 and 437-489; `RS03-SNAP-CBOE-LIVE`, saved HTML lines 1181-1216, with exact-snapshot countercheck at lines 1095 and 1103.
- `overclaim_or_missing_counterevidence`: The requested ranges alone do not entail the report-publication subclaim. `available_time` also remains unproved at exact-instant precision; an approximate publication schedule or a report date must not be promoted to first provider availability. The separate typed fields and fail-closed `available_time` decision are unchanged.

### RS03-R8-C03 — append-only downstream revision lineage

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C03`
- `verdict`: `entailed`
- `reason`: Cboe exposes `Added`, `Cancelled`, `Unchanged`, and `Updated` states; NYSE exposes cancellation and last-updated fields; CRSP states that restatement files receive new names and that the newest restatement becomes the official record while its website shows only the newest restated data. A downstream decision system therefore cannot rely on upstream presentation to preserve every version it previously observed.
- `checked_source_ranges`: `RS03-SNAP-CBOE-LIVE`, saved HTML lines 1181-1216; `RS03-SNAP-NYSE-V3.2A`, deterministic extracted lines 460-489; `RS03-SNAP-CRSP-JULY-2026`, PDF pages 81-82 / deterministic extracted lines 3945-3953.
- `overclaim_or_missing_counterevidence`: Exact-byte child snapshots, parent hashes, and supersession links are project design inferences, not fields mandated by these sources. CRSP's retention behavior is not universal. A provider lacking a native status must be represented as unknown rather than having a status invented. These qualifications do not change the append-only decision.

### RS03-R8-C04 — minimum automatic split/cash-dividend boundary

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C04`
- `verdict`: `contested_non_decision_changing`
- `reason`: The sources entail the named boundary facts: forward and reverse ratios, post-split terms for a same-ex-date cash dividend, add/update/cancel replay states, and distinct ex, record, pay, and effective dates. They do not entail a complete automatic paper-ledger algorithm or prove that a source row is unambiguous in an actual provider feed. Treating these cases as candidate gold fixtures while routing every unresolved case to `pending_manual` remains a conservative design decision.
- `checked_source_ranges`: `RS03-SNAP-CRSP-JULY-2026`, PDF pages 51-55 / deterministic extracted lines 2469-2496 and 2621-2626; `RS03-SNAP-NYSE-V3.2A`, PDF pages 9-12 / deterministic extracted lines 331-389 and 437-489; `RS03-SNAP-CBOE-LIVE`, saved HTML lines 1181-1216.
- `overclaim_or_missing_counterevidence`: “Minimum automatic boundary” must mean a pre-release fixture and gate boundary, not proven operational automation. The cited sources do not freeze taxes, withholding, fractional shares, cash in lieu, due bills, mixed or special actions, or an authoritative paper-account receivable-to-cash transition. The report preserves those exclusions; implementation, gold-fixture verification, and provider-field acceptance must remain separate gates.

### RS03-R8-C05 — historical observation versus latest-restated replay

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C05`
- `verdict`: `contested_non_decision_changing`
- `reason`: FactSet directly shows that filtering an ordinary database by research or input date is not equivalent to an as-observed snapshot after corrections, deletions, currency changes, dilution treatment, or consensus-class changes. CRSP separately shows newest-restatement replacement behavior. The declared decisive ranges do not directly establish the claim's additional word `backfills`, and FactSet's subject is consensus estimates rather than a universal equity-price or Tiingo behavior. The replay-view discriminator remains justified.
- `checked_source_ranges`: `RS03-SNAP-FACTSET-PIT`, PDF pages 3-7 / deterministic extracted lines 29-35, 64-103, 117-120, and 156-169; exact-snapshot methodology countercheck at extracted lines 185-215; `RS03-SNAP-CRSP-JULY-2026`, PDF pages 81-82 / deterministic extracted lines 3945-3953.
- `overclaim_or_missing_counterevidence`: Remove `backfills` from the atomic claim or bind it to separate exact evidence. Do not generalize FactSet consensus behavior to Tiingo or every price provider. `as_observed_at_decision` and `latest_restated_at_retrieval` remain valid provider-neutral labels, but provider capability to produce either view stays unknown until onboarding evidence exists.

### RS03-R8-C06 — future corporate-action back-adjustment leakage

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C06`
- `verdict`: `contested_non_decision_changing`
- `reason`: The Deutsche Bank snapshot directly supports the split and reverse-split mechanism: later split factors embedded in old adjusted prices can reveal future split outcomes and materially alter a price-level backtest. It also supports PIT use, conservative lagging, and caution about split adjustment. The decisive saved range does not separately demonstrate dividends or every other corporate action. The broader claim is valid only conditionally when a future action is actually embedded in historical values used by the decision.
- `checked_source_ranges`: `RS03-SNAP-DB-SEVEN-SINS`, PDF pages 11-13 / deterministic extracted lines 669-730 and 796-804.
- `overclaim_or_missing_counterevidence`: Narrow the directly evidenced claim to split adjustment, or state the dividend/other-action extension as a conditional inference. The strategy-specific magnitude must not be generalized. Requiring price basis, adjustment cutoff, and action lineage, and rejecting `latest_back_adjusted` for decision reconstruction, remains the safer decision.

### RS03-R8-C07 — license scope and termination are data gates

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C07`
- `verdict`: `contested_non_decision_changing`
- `reason`: Tiingo scopes API data to internal consumption, distinguishes individual and commercial plans, requires permission for redistribution, and terminates the right to use the service when service ends. MarketData supplies a provider-specific counterexample requiring downloaded-data deletion when a subscription ends and cessation, erasure, or destruction on termination. These sources entail that API or personal access alone does not establish redistribution, retention, or post-termination rights. They do not entail the project's complete enumerated state topology or Tiingo-specific cache disposition.
- `checked_source_ranges`: `RS03-SNAP-TIINGO-TOS-2026-07-18`, saved HTML lines 27-29, 407-413, and 660-676; `RS03-SNAP-MARKETDATA-TERMS`, saved HTML lines 1093-1109 and 1165-1167.
- `overclaim_or_missing_counterevidence`: `unknown`, `allowed`, `restricted`, `expired`, and `revoked`, plus their transitions, are a conservative project policy model rather than source-native legal states. Tiingo's `Version 1` beside `Last Updated Date: July 18th, 2026` confirms that a version label alone is insufficient. Tiingo does not visibly grant post-termination cache retention, but that absence is not a deletion duty. Account-specific plans, supplemental terms, licensor terms, and legal interpretation remain outside this review.

### RS03-R8-C08 — external paper is a read-only observer

- `reviewer_locator`: `codex_subagent:019f9a31-f372-7fb0-8e52-5f3e40ac4fa6`
- `review_input_sha256`: `69f769acda924e929e4ad13b24ea0cd9a8ed759a956220e5e2168bb6388df6b8`
- `claim_id`: `RS03-R8-C08`
- `verdict`: `contested_non_decision_changing`
- `reason`: Alpaca's saved public page directly supports the Paper Only IEX entitlement and the listed simulation omissions, including dividends. That is enough to reject Alpaca Paper as authority for local dividend or corporate-action accounting. It does not entail an observer-only capability boundary: the same page says paper works the same way as live trading end to end except exchange routing, permits use of the API, says the paper and live API specification is the same, and says the Market Data API works identically. “Read-only observer” is therefore a local-authority policy, not an Alpaca source fact.
- `checked_source_ranges`: `RS03-SNAP-ALPACA-PAPER-CURRENT`, saved HTML lines 1, 63-78, 141-157, and embedded document metadata at line 378.
- `overclaim_or_missing_counterevidence`: Preserve both sides of the source: useful end-to-end simulation similarity and explicit omissions. The report does preserve that contradiction. Rename the evidence-backed boundary as “external paper is non-authoritative and configured observer-only by local policy.” No private entitlement, account, endpoint, order, fill, disconnect, replay, or reconciliation behavior was tested, so none can be claimed as observed.

## Cross-claim challenge results

### Provider-neutral contract

The exact evidence supports provider-neutral discriminators and fail-closed gates: calculation context, non-substitutable times, replay view, price basis and cutoff, append-only local lineage, scoped license evidence, and local-ledger authority. It does not prove that a selected provider supplies every field, preserves vintages, permits retention, or implements the frozen semantics. The Tiingo EOD snapshot remains shell-only and non-decisive. “Strong-freeze” is therefore closure-eligible only as a design-contract freeze, not as provider acceptance, integration readiness, or release readiness.

### Missing or underbound counterevidence

- The C02 packet range omitted the Cboe `Report Date` locator even though the exact snapshot contains it.
- C05's `backfills` term lacks direct support in the declared decisive ranges.
- C06's decisive snapshot proves split-adjustment leakage, not dividends or every other action.
- C07's source facts justify a fail-closed license gate but not the complete project state topology or any Tiingo deletion duty.
- C08's observer-only role is contradicted as a source-capability claim by Alpaca's API and end-to-end-similarity statements; it survives only as a conservative local policy.
- C04 has enough evidence for a fixture boundary, but not for operational cash-dividend automation, actual-provider field sufficiency, or release.

None of these contests requires weakening the conservative design. They require narrower claim wording and preservation of provider, implementation, legal, and private-observation gates.

## Total verdict

- `verdict`: `contested_non_decision_changing`
- `closure_scope`: `provider_neutral_design_contract_only`
- `blocking_claims_under_declared_scope`: `none`
- `conditional_block`: If “strong-freeze” is interpreted to include selected-provider acceptance, implemented split/cash-dividend automation, account-specific license approval, or validated external-paper operation, closure is blocked by the unobserved gaps above.

The factual cores needed for the conservative design boundaries are either entailed or can be narrowed without changing the decisions to fail closed, preserve local history, separate calculation contexts and times, reject future-adjusted decision inputs, and keep external paper non-authoritative.

## Closure-predicate update recommendation

| Predicate | Recommended update | Basis |
|---|---|---|
| every decisive claim has independent per-claim entailment review | change `false` to `true` | this file binds the separate-thread reviewer locator, hash-gated input, per-claim verdict, reason, checked ranges, and overclaim/counterevidence field |
| every per-claim verdict is closure-eligible | set `true` for design-contract closure | every verdict is `entailed` or `contested_non_decision_changing` |
| provider-neutral design contract is sufficiently bounded | keep `true` only with the scope qualifier above | sources support the discriminators and conservative gates, not provider capability |
| selected-provider capability and license acceptance | remain `unknown` / not satisfied | Tiingo account, plan, body-level EOD fields, retention, PIT, revision, and fault behavior were not observed |
| automatic split/cash-dividend implementation and release | remain deferred / not satisfied | sources bound fixtures and exclusions; implementation and executable verification were outside the report |
| external-paper private operation and reconciliation | remain unobserved / not satisfied | public documentation only; no credentialed behavior was tested |

The raw report states that independent review was the remaining false closure predicate. After attaching this review, that predicate can be updated mechanically. The final governance status token should then be recomputed from the preregistered vocabulary without using this review to convert any provider-onboarding, implementation, legal, or private-observation gap into a pass.
