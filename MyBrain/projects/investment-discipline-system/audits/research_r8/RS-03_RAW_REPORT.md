# RESEARCH-REFRESH-R8 / RS-03 raw report

## Final status

`bounded_incomplete`

Design result: the provider-neutral Paper V1 contract is sufficiently supported to **strong-freeze with five explicit high-impact refinements**:

1. separate `market_return_series` from `paper_account_ledger` calculation context;
2. preserve exact-byte, append-only revision lineage;
3. freeze the minimum split/cash-dividend gold boundary;
4. distinguish `as_observed_at_decision` from `latest_restated_at_retrieval`;
5. distinguish `raw_as_traded`, `pit_adjusted`, and `latest_back_adjusted` with an adjustment cutoff.

Provider capability remains conditional: public Tiingo material does not prove account-specific license, retention, PIT replay, coverage, or revision behavior; public Alpaca Paper material supports only a read-only observer/reconciliation role and explicitly does not simulate dividends.

The preregistered stability rule passed: S2 was the last high-impact delta and the later reserved S3 query produced no new high-impact failure class, decision reversal, or open critical/major contradiction.

The topic still cannot close because **no independent reviewer has issued a per-claim entailment verdict**. This report deliberately does not self-review entailment. Required source bytes, query accounting, contradictions, executable deltas, stability, and residual risks are present; independent review remains false, so the preregistered final state must be `bounded_incomplete`.

## Scope and guardrails

- Research topic: `RS-03`
- Question: whether Paper V1's provider-neutral data contract, PIT times, license state, revisions, and corporate-action boundary are sufficient to freeze.
- Writes were limited to:
  - `audits/research_r8/RS-03_RAW_REPORT.md`
  - `research/evidence/r8/RS-03/**`
- No governance, prototype, scripts, shared project documents, or other agents' files were modified.
- No private credential was accessed, requested, displayed, recorded, or uploaded.
- No Tiingo or Alpaca private account, token, entitlement, endpoint, order, fill, or reconciliation test was performed.
- Direct opens and exact-byte downloads used only public locators.

## Preregistration and temporal proof

### Frozen boundary

- Preregistration file: `research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json`
- Required commit: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- Git commit timestamp: `2026-07-25T09:13:44-07:00`
- Required UTC boundary: `2026-07-25T16:13:44Z`
- Required file SHA-256: `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`
- Observed file SHA-256: `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`
- File size read before search: `19278` bytes
- File length read before search: `418` lines
- Initial HEAD: exactly `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- Initial working tree: clean
- Diff from required commit to preregistration file: none

The full preregistration file was read before any counted query. The first query started at `2026-07-25T16:17:07Z`, after the required UTC boundary.

### Later evidence-commit ancestry

Concurrent `vault backup` advanced the branch during the research. The RS-03 author did not create, amend, revert, or attribute those commits. The required preregistration commit returned exit `0` for `git merge-base --is-ancestor` against every later commit visible at the ancestry check:

| Later commit | Git timestamp | Subject | RS-03 content observed |
|---|---|---|---|
| `216dde18eefb6e6e26ce3d3082252cc128c6bcd3` | `2026-07-25T09:18:09-07:00` | `vault backup: 2026-07-25 09:18:09` | none |
| `1ebc3f3592953cb4fe52821cd551a70921b657fb` | `2026-07-25T09:23:17-07:00` | `vault backup: 2026-07-25 09:23:17` | discovery freeze, S1 and S2 delta records |
| `9a930cee9915510e01880b96b6f1f2d7be476bd0` | `2026-07-25T09:28:40-07:00` | `vault backup: 2026-07-25 09:28:39` | S3 record and exact source snapshots |
| `98bdf382cf34c7cc3ca5f6e889983e51c60e1695` | `2026-07-25T09:33:58-07:00` | `vault backup: 2026-07-25 09:33:58` | derivative text, manifest, and failure receipts |
| `c768ea481507a16a605cd7bdc05a83a7f8b5d8db` | `2026-07-25T09:38:36-07:00` | `vault backup: 2026-07-25 09:38:36` | complete query ledger |

At that check, current HEAD was `c768ea481507a16a605cd7bdc05a83a7f8b5d8db`; the preregistration commit was its ancestor. Retrieval times and search calls below are all later than the preregistration UTC.

## Exact query accounting

Every query was executed in its own search-tool call, exactly once, with unchanged text. No batched, rewritten, expanded, or sixth query was issued.

| Query ID | Exact query | Search-call UTC | Visible results |
|---|---|---|---:|
| `R8-RS03-D1` | `CRSP stock return calculations distributions splits dividends methodology PDF` | `2026-07-25T16:17:07Z` → `2026-07-25T16:17:22Z` | 35 |
| `R8-RS03-D2` | `official corporate action event effective ex date cash dividend stock split data standard` | `2026-07-25T16:17:30Z` → `2026-07-25T16:17:39Z` | 32 |
| `R8-RS03-S1` | `point in time market data correction revision available timestamp methodology` | `2026-07-25T16:20:49Z` → `2026-07-25T16:20:57Z` | 24 |
| `R8-RS03-S2` | `counterexample adjusted historical price lookahead corporate action backtest` | `2026-07-25T16:22:00Z` → `2026-07-25T16:22:12Z` | 35 |
| `R8-RS03-S3` | `market data license personal use cache retention termination API terms` | `2026-07-25T16:23:12Z` → `2026-07-25T16:23:22Z` | 17 |

The complete result ledger contains every visible result in backend presentation order, with unique query ownership, class, upstream cluster, inclusion/exclusion decision, reason, and revision/supersession state:

- Evidence file: `research/evidence/r8/RS-03/receipts/QUERY_LEDGER.md`
- SHA-256: `7a91adece4f3338b4cf5c39df65b713c929c4b963b21b36dc0a45cf68f63beb6`
- Per-query row-count verification: D1 `35`, D2 `32`, S1 `24`, S2 `35`, S3 `17`
- Search-tool truncation marker observed: none

The same complete ledger is copied verbatim into Appendix A of this report.

## Discovery freeze proof

D1 and D2 were completed before any S query. Discovery claims and deltas were frozen at `2026-07-25T16:19:34Z`:

- File: `research/evidence/r8/RS-03/00_DISCOVERY_FREEZE.md`
- SHA-256 before S1: `95817561dd206b04bc81bb14fa98eef2369739d85cdf628323963930d11180b8`
- Hash proof time: `2026-07-25T16:20:42Z`
- S queries executed before freeze: none

Discovery froze three high-impact deltas:

- `RS03-R8-D-DELTA-01`: calculation-context separation;
- `RS03-R8-D-DELTA-02`: observable append-only revision lineage;
- `RS03-R8-D-DELTA-03`: minimum automatic split/cash-dividend gold boundary.

Later stability evidence did not rewrite the discovery freeze. S1 and S2 added separately recorded deltas; S3 supplied a separately recorded no-delta adjudication.

## Saved source snapshots and manifest

Manifest:

- Path: `research/evidence/r8/RS-03/manifest.json`
- SHA-256: `004ed1b4aa8f8ac0858929257aa6f5525cfeac6144b6e4d1f454d3b787cb478e`

### Required snapshot classes

| Required class | Source ID and exact-byte file | Retrieved UTC | Bytes | SHA-256 | Result |
|---|---|---|---:|---|---|
| one primary return or corporate-action calculation method | `RS03-SNAP-CRSP-JULY-2026` — `snapshots/CRSP_Market_Indexes_Methodology_Guide_July_2026.pdf` | `2026-07-25T16:25:25Z` | 5167396 | `8e212b1514e34eea6968295b4b13cd9f316654ed6c9ec15cec8c364eda77760c` | exact PDF bytes saved |
| one official timing or corporate-action definition | `RS03-SNAP-NYSE-V3.2A` — `snapshots/NYSE_CorporateActions_Client_Specification_v3.2a.pdf` | `2026-07-25T16:26:00Z` | 708910 | `61e15ff3250c2f94718896cfd27bd18fa98529d9a0ed225c2d22d08a5759092c` | exact PDF bytes saved |
| one provider license or revision boundary source | `RS03-SNAP-TIINGO-TOS-2026-07-18` — `snapshots/Tiingo_Terms_of_Use_2026-07-18.html` | `2026-07-25T16:27:13Z` | 663905 | `9a5cfcdeb5588ae89fb55cc9895f5ba21b3eea133c40db1eb74d98ffbf944de3` | exact HTML response bytes saved |

### Additional decisive/supporting snapshots

| Source ID | Boundary | Bytes | SHA-256 |
|---|---|---:|---|
| `RS03-SNAP-CBOE-LIVE` | official action ID/status and declared/updated/ex/record/payment/effective fields | 450101 | `2ede407424b5fec02e22672bde8da4a08572f4dff81f9f52f04a66eb452f44d1` |
| `RS03-SNAP-FACTSET-PIT` | historical snapshot versus later correction/deletion/recalculation | 9158902 | `b2ad639c2463bb9d08729874fabd3011f2dba306a5b3334ac440cc0e3b58ff34` |
| `RS03-SNAP-DB-SEVEN-SINS` | independent split-adjustment look-ahead counterexample | 3132081 | `fd9de52b947605ec9ea5333aa288957c4bec70766ac039e6d55005de4e294646` |
| `RS03-SNAP-ALPACA-PAPER-CURRENT` | external Paper limitations and observer boundary | 483969 | `acacd1f871c2e08d7677122a19a105077a0abd64c0ad39cd3b1d9d9633879001` |
| `RS03-SNAP-MARKETDATA-TERMS` | provider-specific termination/deletion counterexample | 191943 | `44ac9d9378eea61dd0ac50d80ab2afaa2710ee73ca85c6dc5dfcecf1480cb942` |

The CRSP, NYSE, FactSet, and Deutsche Bank PDFs also have deterministic `pdftotext -layout` derivatives with their own hashes and exact ranges in the manifest. The original source-byte hashes above, not derivative hashes, are the content-integrity anchors.

### Explicit partial/blocked receipts

- Tiingo EOD direct response:
  - exact saved shell bytes: `10302`
  - SHA-256: `7e6ce120afad8105ffe25015edc638418d1b63eaabfc2d85fe8468ab3f3f3e63`
  - result: Angular application shell only; documentation body absent
  - effect: non-counting transport receipt; no search excerpt was substituted for source bytes
- CME DS-45:
  - first exact-byte attempt: curl exit `92`, HTTP/2 stream error
  - unchanged HTTP/1.1 retry: did not complete or create a file; task-owned transfer was terminated
  - result: supporting blocked source, not used to satisfy a required snapshot class
- Legacy CRSP Calculations locators:
  - direct opens returned HTTP `404`
  - current official July 2026 guide was obtained through the CRSP guide archive instead
  - indexed search excerpt was not treated as a snapshot

Receipts:

- `research/evidence/r8/RS-03/receipts/TIINGO_EOD_SHELL_ONLY.md`
- `research/evidence/r8/RS-03/receipts/CME_DS45_DOWNLOAD_FAILURE.md`
- `research/evidence/r8/RS-03/receipts/CRSP_LEGACY_CALCULATIONS_LOCATOR.md`

## Atomic claims

The claims below are **author-produced review inputs**, not independent entailment verdicts.

Independent-review packet:

- Path: `research/evidence/r8/RS-03/CLAIMS_FOR_INDEPENDENT_REVIEW.md`
- SHA-256: `4641342e448fc98b46eba88a0b396c84435dfaafd4b1ed987d49deb5d0ae6e63`
- Reviewer locator: pending
- Independent verdicts: none

### `RS03-R8-C01` — calculation context

- Claim: CRSP's July 2026 Market Indexes method treats ordinary cash dividends, same-ex-date split/dividend terms, split factors, and total-return dividend reinvestment in a defined index-calculation context.
- Impact: high
- Evidence clusters: `U-CRSP-INDEX-METHOD`
- Snapshot/ranges: `RS03-SNAP-CRSP-JULY-2026`; PDF pages 51–55 and 69–70; extracted lines 2469–2497, 2621–2632, 3334–3352
- Author assessment: source supports the named CRSP method semantics.
- Limitation: index-return semantics are not universal paper-ledger settlement rules and do not prove candidate-provider implementation.
- Decision effect: require `calculation_context`; never turn ex-date return reinvestment into an automatic ledger cash credit.

### `RS03-R8-C02` — non-substitutable times

- Claim: NYSE and Cboe specifications distinguish declared/announcement, ex, record, payment/effective, update, and report-publication fields; none proves project availability, retrieval, or decision time.
- Impact: high
- Evidence clusters: `U-NYSE-CA`, `U-CBOE-CA`
- Snapshots/ranges: `RS03-SNAP-NYSE-V3.2A`, PDF pages 9–12 / extracted lines 354–389 and 437–489; `RS03-SNAP-CBOE-LIVE`, saved HTML lines 1181–1216
- Author assessment: source supports the field distinctions.
- Limitation: date-granular update fields are not first-availability timestamps.
- Decision effect: preserve event, effective, ex, published, available, retrieved, and decision time as separate typed fields; retain record and pay time rather than aliasing them.

### `RS03-R8-C03` — append-only revision lineage

- Claim: official action records can be added, updated, cancelled, or unchanged; CRSP may issue new restatement filenames and later expose the newest restatement as official, so downstream systems cannot rely on upstream retention of every observed version.
- Impact: high
- Evidence clusters: `U-CBOE-CA`, `U-NYSE-CA`, `U-CRSP-INDEX-METHOD`
- Snapshots/ranges: Cboe saved HTML lines 1181–1216; NYSE extracted lines 460–489; CRSP PDF pages 81–82 / extracted lines 3945–3953
- Author assessment: source supports the named upstream behavior; downstream schema is an inference.
- Limitation: CRSP Market Index restatement policy is not every provider's policy.
- Decision effect: each revision is a new exact-byte snapshot with parent/supersession lineage; no decision-used bytes are overwritten.

### `RS03-R8-C04` — split/cash-dividend gold boundary

- Claim: split and ordinary cash-dividend handling still has material boundaries: forward/reverse ratios, same-ex-date post-split dividend terms, updates/cancellations, and ex versus payment/effective time.
- Impact: high
- Evidence clusters: `U-CRSP-INDEX-METHOD`, `U-NYSE-CA`, `U-CBOE-CA`
- Snapshots/ranges: CRSP PDF pages 51–55; NYSE PDF pages 9–12; Cboe saved HTML lines 1181–1216
- Author assessment: source supports the boundary facts; test selection is an inference.
- Limitation: taxes, withholding, fractional shares, cash in lieu, due bills, and mixed/special actions are not frozen.
- Decision effect: automatic V1 is limited to unambiguous split and ordinary cash-dividend fixtures; all other cases are `pending_manual`.

### `RS03-R8-C05` — historical replay view

- Claim: a current/latest database filtered by an old event/input date is not necessarily the historical view because later corrections, deletions, currency changes, methodology changes, or backfills can alter old output.
- Impact: high
- Evidence clusters: `U-FACTSET-PIT`, supporting `U-CRSP-INDEX-METHOD`
- Snapshots/ranges: FactSet PDF pages 3–7 / extracted lines 29–35, 64–103, 173–201; CRSP PDF pages 81–82
- Author assessment: source supports the named products' difference; provider-neutral discriminator is an inference.
- Limitation: FactSet concerns estimates and does not prove Tiingo behavior.
- Decision effect: require `as_observed_at_decision` versus `latest_restated_at_retrieval`.

### `RS03-R8-C06` — adjusted-price future leakage

- Claim: back-adjusting historical prices with splits/dividends occurring after a simulated decision can leak future information into price-level and derived-feature decisions.
- Impact: high
- Evidence clusters: `U-DB-SEVEN-SINS`, supporting `U-PIT-BACKTEST-2026`, `U-KIBOT-ADJUSTMENT`
- Snapshot/ranges: Deutsche Bank PDF pages 11–13 / extracted lines 669–730 and 796–804
- Author assessment: the saved institutional research supports the mechanism and worked counterexample.
- Limitation: empirical magnitude is strategy-specific; the retrieved 2026 preprint explicitly labels itself not peer-reviewed and is not the decisive saved snapshot.
- Decision effect: require price basis, adjustment cutoff, and action lineage; `latest_back_adjusted` fails the decision-time gate.

### `RS03-R8-C07` — license state is a data gate

- Claim: use rights depend on provider, licensor, plan/addendum, user class, purpose, redistribution, term, and termination; personal use/API access does not imply retention or continued use after termination.
- Impact: high
- Evidence clusters: `U-TIINGO`, `U-MARKETDATA-TERMS`
- Snapshots/ranges: Tiingo saved HTML lines 29, 408, 676; MarketData saved HTML lines 1109, 1167
- Author assessment: source supports the named terms; no legal interpretation beyond visible text is claimed.
- Limitation: no account-specific or supplemental terms were accessed. Tiingo's visible terms do not expressly grant post-termination cache retention, but absence of a grant is not an express deletion duty.
- Decision effect: keep the fail-closed `unknown`, `allowed`, `restricted`, `expired`, `revoked` state machine, bound to exact terms bytes and scope.

### `RS03-R8-C08` — external paper is observation, not authority

- Claim: Alpaca's current public Paper documentation limits Paper Only data to IEX and lists simulation omissions including dividends; it cannot be authoritative for local corporate-action accounting.
- Impact: high
- Evidence cluster: `U-ALPACA-PAPER`
- Snapshot/range: `RS03-SNAP-ALPACA-PAPER-CURRENT`; saved HTML body and embedded document metadata
- Author assessment: source supports the named public limitations.
- Limitation: no private behavior was tested.
- Decision effect: external paper remains a read-only observer and reconciliation source; disagreement is logged and never auto-resolved.

## Contract freeze

### Time model

| Field | Meaning | Eligibility rule |
|---|---|---|
| `event_time` | provider-native event or declaration time | descriptive only; does not prove visibility |
| `effective_time` | time/date at which a non-distribution action takes effect | must remain distinct from declaration and retrieval |
| `ex_time` | first trading time/date without the dividend/distribution entitlement in the selected source semantics | action/accounting input; does not prove publication |
| `record_time` | source-defined holder-of-record date/time | retained for entitlement evidence; not aliased to ex time without an explicit source rule |
| `pay_time` | source-defined distribution payment time/date | ledger settlement input; not aliased to return-series reinvestment time |
| `published_time` | source/report publication time | source-native; must include timezone/precision/provenance |
| `available_time` | first proven time the selected provider/channel made the exact version available to this use | never inferred from event, effective, ex, record, pay, or generic date |
| `retrieved_time` | local acquisition time for exact saved bytes | mandatory; a decision snapshot requires `retrieved_time <= decision_time` |
| `decision_time` | immutable human/AI decision cutoff | all eligible bytes and transformations must be available and retrieved no later than this time |

Sanity rule: an old market/event date does not make a row PIT-safe. If `available_time` is unproved, provider capability stays `unknown`; only a locally saved pre-decision exact-byte snapshot can support `as_observed_at_decision`.

### Snapshot and revision contract

Every decision-eligible source object must bind:

- provider/dataset/schema identity;
- exact saved response bytes and `raw_payload_sha256`;
- source locator and retrieval time;
- all native event/date fields with timezone and precision;
- `replay_view`;
- `price_basis` and `adjustment_cutoff_time`;
- corporate-action snapshot lineage used for any adjustment;
- provider-native add/update/cancel state;
- `parent_snapshot_id` and `supersedes_snapshot_id`;
- license scope/state evidence.

Revision behavior:

- correction, deletion, cancellation, and restatement create new child snapshots;
- a later version can become current but cannot mutate the decision snapshot or prior ledger effect;
- retrospective evaluation may use `latest_restated_at_retrieval`, but the output is post-hoc evidence with separate identity;
- mutation tests must prove future revisions and corporate actions cannot change a prior decision hash.

### Price and replay views

| Discriminator | Allowed use |
|---|---|
| `as_observed_at_decision` | only view eligible to reconstruct a past decision |
| `latest_restated_at_retrieval` | post-hoc correction/evaluation only |
| `raw_as_traded` | eligible if exact raw bytes were available/retrieved before the decision and corporate actions are handled explicitly |
| `pit_adjusted` | eligible only with provider proof and adjustment factors available by the decision |
| `latest_back_adjusted` | ineligible for decision reconstruction; may be used only as a labelled post-hoc view |

Mixed-basis formulas fail closed unless every operand is transformed onto one explicitly tested basis.

### License state machine

| State | Required behavior |
|---|---|
| `unknown` | default; no new decision use or provider acceptance |
| `allowed` | exact terms/plan/purpose/retention/redistribution scope proven for the intended use |
| `restricted` | only explicitly permitted operations; all other use blocked |
| `expired` | term ended; no new use; retention/purge behavior follows exact applicable terms |
| `revoked` | access/right withdrawn or terminated; cease use and execute only the obligations actually established by the applicable terms |

Terms changes, plan changes, licensor changes, account-class changes, or ambiguous supplemental terms send a previously accepted capability back to `unknown` pending revalidation. The state record must bind exact terms bytes, provider/plan/user class, purpose, storage/cache, redistribution, termination action, effective/last-updated date, reviewer, and next recheck trigger.

No conclusion is made that keeping even a hash or audit metadata after a deletion duty is always permitted. If a future agreement requires purge, the implementation must follow the exact applicable obligation and mark any lost reproducibility; it must not invent a retention exception.

## Split and cash-dividend gold boundary

Automatic Paper V1 may cover only an unambiguous, source-typed action with all required fields and no unresolved exception.

Required gold classes:

1. forward split;
2. reverse split;
3. ordinary cash dividend in `market_return_series` context;
4. ordinary cash dividend in `paper_account_ledger` context with distinct entitlement and payment handling;
5. same-ex-date split plus ordinary cash dividend, where the source states the dividend in post-split terms;
6. update replay;
7. cancellation replay;
8. future-split mutation proving an old decision feature/hash does not change;
9. raw/PIT-adjusted/latest-back-adjusted differential result.

Required context rules:

- A split changes share quantity and price basis proportionally on the action boundary; it is not a cash gain.
- A return-series dividend convention may place reinvestment at ex-date.
- The local authoritative ledger must not equate return-series reinvestment with cash receipt. It needs an explicit receivable/payment transition supported by unambiguous source fields.
- Gold fixtures must avoid unresolved due-bill or settlement ambiguity; otherwise they fail closed.
- Same-ex-date split/dividend ordering must use source-stated post-split terms and prove that price, shares, receivable, cash, and total value are not double-adjusted.

Automatically rejected to `pending_manual` unless separately frozen and tested:

- special/conditional dividends;
- return of capital;
- stock/cash elections;
- stock dividends not equivalent to the frozen split rule;
- fractional shares and cash in lieu;
- taxes and withholding;
- rights, spin-offs, mergers, tender offers, symbol/security-master changes, delistings;
- due bills;
- mixed, missing, contradictory, revised-but-unresolved, or unknown actions.

## External paper read-only observer

The external paper adapter may:

- read order, fill, position, cash, and account snapshots;
- append timestamped observation records;
- compute a differential reconciliation against the local authoritative ledger;
- classify disagreements and open a human review.

It may not:

- overwrite local orders, fills, positions, cash, corporate actions, or ledger history;
- auto-resolve a disagreement;
- prove local dividend accounting, because the current public Alpaca Paper page says dividends are not simulated;
- prove live execution, market impact, queue position, latency/slippage, fees, or private entitlement.

The observer manifest must bind public document version/retrieval, feed entitlement, paper endpoint class, simulation omissions, exact observation time, and reconciliation result. Private credentials remain a future Javen-only onboarding action and were outside this research.

## Counterevidence, contradictions, and sanity checks

1. **Return convention versus ledger settlement**  
   CRSP's ex-date reinvestment convention and exchange payment-date fields answer different questions. Collapsing them would create a false contradiction and likely a ledger timing error. The calculation-context discriminator resolves the category difference.

2. **“Updated date” versus PIT availability**  
   NYSE/Cboe update fields establish that records change, but a date-granular update does not prove first provider availability. The contract therefore cannot infer `available_time`.

3. **Current official record versus historical observation**  
   CRSP may publish newly named restatement files while later exposing the newest restatement as official. Provider “official current” does not preserve what a decision saw. Local append-only bytes are necessary.

4. **Adjusted continuity versus future leakage**  
   Adjusted series avoid mechanical split/dividend gaps, but current back-adjustment can leak later actions into old signals. Raw and adjusted are both useful; admissibility depends on replay view, adjustment cutoff, and calculation context.

5. **Tiingo terms revision marker**  
   The exact Tiingo terms page showed `Version 1` and `Last Updated Date: July 18th, 2026`. A version label alone is therefore insufficient; exact bytes plus date are required.

6. **Tiingo EOD snapshot limitation**  
   The public direct locator was readable through the extraction tool, but the exact curl response saved only the Angular shell. Search/tool text was not substituted. CRSP/NYSE bytes close the required method/timing classes, while current Tiingo field semantics remain a provider-onboarding revalidation item.

7. **Provider-specific license duties**  
   MarketData public terms require deletion at subscription end; its addenda and CME's visible update show scope/exception differences. These cannot be generalized into a Tiingo deletion duty. They validate the state-machine failure class, not a universal legal conclusion.

8. **Alpaca “same end to end” versus omissions**  
   The public page describes Paper as similar except routing, then lists missing market impact, information leakage, latency slippage, queue position, price improvement, fees, and dividends. Both statements are preserved; the result cannot be summarized as live-equivalent.

9. **Source migration**  
   The D1 legacy CRSP calculations URLs returned 404 after the CRSP Research Data Products migration. The saved July 2026 CRSP guide is a current primary corporate-action/return method, but it is an index method rather than proof of a candidate provider's data implementation.

Sanity result: the design remains provider-neutral, paper-first, human-decision-controlled, no-future-information, and local-ledger-authoritative. No source supports weakening those boundaries.

## Delta chronology and stability

| Stage | Artifact | High-impact result | Stability consequence |
|---|---|---|---|
| D1/D2 discovery | `00_DISCOVERY_FREEZE.md` | calculation context; append-only revision lineage; minimum corporate-action gold gate | discovery state frozen before S1 |
| S1 | `01_S1_DELTA.md` | new failure class: date-filtered latest data can masquerade as PIT; add replay view | stability clock reset |
| S2 | `02_S2_DELTA.md` | new failure class: future corporate actions can back-adjust old price rows; add price basis/cutoff | stability clock reset |
| S3 | `03_S3_STABILITY.md` | no new high-impact failure class; license examples fit existing state machine | one later stable reserved query completed |

Recorded hashes:

- `00_DISCOVERY_FREEZE.md`: `95817561dd206b04bc81bb14fa98eef2369739d85cdf628323963930d11180b8`
- `01_S1_DELTA.md`: `d14d6527f491b2c66946418cdd05dd328b00628bc3138006941fc267749ccc03`
- `02_S2_DELTA.md`: `adddb35f365c1d40a279b65ab34e79b2e94cddb84ecb505cace8034cf2f4e478`
- `03_S3_STABILITY.md`: `8fb2f127350e4059d3874b82c661bcc96d2aecc4d6821710e5733169bb45b213`

Stability adjudication:

- last high-impact delta: S2;
- later reserved query: S3;
- new high-impact failure class in S3: no;
- decision reversal in S3: no;
- open critical/major contradiction after S3: none;
- preregistered stability predicate: pass.

## Remaining gaps

### Design-review blocker

- Independent reviewer must review `CLAIMS_FOR_INDEPENDENT_REVIEW.md` at SHA-256 `4641342e448fc98b46eba88a0b396c84435dfaafd4b1ed987d49deb5d0ae6e63`.
- Every claim needs reviewer locator, input hash, verdict, reason, checked ranges, and overclaim/missing-counterevidence field.
- This author supplied no independent verdict and did not self-review.

### Provider-onboarding conditional gaps

- Tiingo account/plan-specific license, supplemental terms, cache retention, redistribution, exact universe coverage, PIT/vintage capability, correction history, quotas, and fault behavior remain `unknown`.
- Tiingo EOD exact body bytes need a stable savable locator or provider artifact before field-level provider acceptance.
- Alpaca current private entitlement, authentication, paper account behavior, ACK/partial fill/disconnect/replay, and real reconciliation remain unobserved.
- No private account may be tested without a later explicit Javen onboarding action.

### Deferred implementation/release gaps

- Contract/schema implementation and mutation tests are outside this research write scope.
- Gold fixtures must be implemented and independently checked.
- License purge/tombstone behavior needs exact future agreement text and, where needed, legal review.
- External-paper differential observation needs a later credential-safe, Javen-authorized run.
- Complex corporate actions remain manual.

## Reopen triggers

- Tiingo, Alpaca, CRSP/Morningstar, NYSE, Cboe, or another selected provider changes terms, API, schema, corporate-action method, revision policy, PIT capability, or entitlement.
- An exact provider agreement differs from the public terms snapshot.
- A gold fixture fails, or a future correction/action changes a prior decision hash.
- A paper reconciliation finds an unclassified difference.
- A due-bill, fractional-share, tax, withholding, special-dividend, merger, spin-off, delisting, or other excluded action must be automated.
- A provider cannot preserve or legally permit the evidence needed for a decision.
- An independent reviewer finds overclaim, missing counterevidence, or a new high-impact failure class.

## Closure predicates

| Preregistered predicate | Result | Evidence |
|---|---|---|
| preregistration commit, file hash, ancestry, and retrieval time pass | `true` | exact commit/hash; all query/retrieval UTC later; ancestor checks against every observed later commit returned exit `0` |
| five query IDs each have exactly one execution or failure receipt | `true` | exact-query table and Appendix A |
| every visible result has unique query ownership and per-result screening | `true` | `QUERY_LEDGER.md`, verified row counts |
| required snapshot classes have saved bytes/hashes or block closure | `true` | CRSP, NYSE, Tiingo exact bytes and manifest |
| every decisive claim has independent per-claim entailment review | `false` | review packet exists; reviewer locator/verdicts absent by design |
| contradictions and counterevidence are preserved with decision effects | `true` | counterevidence/sanity section and per-result ledger |
| stability passing rule is satisfied | `true` | S2 last delta; S3 later no-delta |
| architecture/decision deltas map to executable contract, test, gate, defer, or rejection | `true` | contract freeze, gold boundary, license gate, observer boundary |
| residual risks and reopen triggers are explicit | `true` | remaining-gaps and reopen sections |

Because one predicate is false after the fixed five-query budget, final status is:

`bounded_incomplete`

This status does not reverse the design result. It means the provider-neutral freeze candidate is ready for a separate semantic reviewer, not that the topic has passed review or that any provider is accepted.

## Appendix A — complete visible result sets

# R8 / RS-03 exact-query ledger and complete visible result sets

Accounting rule: each section below corresponds to one and only one search-tool call with the exact preregistered query text. Direct opens, clicks, fixed-locator retrievals, redirects, and unchanged transport retries were not search calls. Backend order is the order visibly returned by the search tool, including its non-numeric reference ordering. Every row inherits the section's `query_id` and retrieval window.

Screening vocabulary:

- `IN-D`: included as decisive or direct source candidate.
- `IN-S`: included as supporting/background evidence.
- `IN-C`: retained as counterevidence, failure hypothesis, user burden, or reopen trigger.
- `EX-DUP`: excluded as same-upstream duplicate or superseded version.
- `EX-SCOPE`: excluded as not answering RS-03.
- `EX-AUTH`: excluded from decision support because authority/provenance was insufficient; any useful content remains hypothesis-only.
- `EX-NOISE`: irrelevant search noise.

## R8-RS03-D1

- Exact query: `CRSP stock return calculations distributions splits dividends methodology PDF`
- Search-call window UTC: `2026-07-25T16:17:07Z` → `2026-07-25T16:17:22Z`
- Search calls for this query_id: exactly one
- Complete visible result count: 35

| Order / backend ref | Title and URL | Source class | Upstream cluster | Screening and reason | Revision / supersession state |
|---|---|---|---|---|---|
| 1 / `turn184search12` | [CRSP US Stock & Indexes](https://www.crsp.org/wp-content/uploads/guides/CRSP_Calculations_and_Index_Methodologies.pdf) | official primary method | `U-CRSP-RDP-METHOD` | `IN-S`; directly answers return/distribution calculation, but direct live retrieval returned 404 and search excerpt was not substituted for bytes | Indexed as current-looking; live locator 404 after query; Research Data Products migration receipt retained |
| 2 / `turn184search13` | [CRSP Market Indexes Methodology Guide — January 2024](https://www.crsp.org/wp-content/uploads/guides/CRSP_Market_Indexes_Methodology_Guide_2024.pdf) | official versioned method | `U-CRSP-INDEX-METHOD` | `EX-DUP`; older same-upstream guide | Versioned January 2024; superseded by later guides |
| 3 / `turn184search14` | [CRSP Market Indexes Methodology Guide](https://www.crsp.org/wp-content/uploads/guides/CRSP_Market_Indexes_Methodology_Guide.pdf) | official current method | `U-CRSP-INDEX-METHOD` | `IN-D`; current official calculation/corporate-action method and restatement policy; exact bytes saved | Saved document says July 2026 and last modified July 1, 2026 |
| 4 / `turn184search15` | [CRSP US Stock & Indexes — flat-file format 2.0](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-calculations-index-methodologies-guide-flat-file-format-2-0/) | official primary method | `U-CRSP-RDP-METHOD` | `EX-DUP`; same legacy method family as order 1; direct live locator returned 404 | Legacy/migrated locator; no saved content bytes |
| 5 / `turn184search16` | [CRSP Market Indexes Methodology Guide — January 2025](https://www.crsp.org/wp-content/uploads/guides/CRSP_Market_Indexes_Methodology_Guide_January_2025.pdf) | official versioned method | `U-CRSP-INDEX-METHOD` | `EX-DUP`; older same-upstream guide | Versioned January 2025; superseded by July 2026 guide |
| 6 / `turn184search0` | [(PDF) “True Returns: Adjusting Stock Prices for Cash Dividends and Stock Splits”](https://www.researchgate.net/publication/331962610_True_Returns_Adjusting_Stock_Prices_for_Cash_Dividends_and_Stock_Splits_Advances_in_Financial_Education_Summer_2019_192-205) | academic-paper locator / repository | `U-TRUE-RETURNS-2019` | `IN-S`; relevant independent adjustment method, but not needed over saved primary CRSP method | Repository copy; visible result did not establish a versioned canonical artifact |
| 7 / `turn184search1` | [Replicating Financial Anomalies Study](https://www.scribd.com/document/877010215/Replicating-Anomalies) | document-host mirror | `U-REPLICATING-ANOMALIES` | `EX-SCOPE`; anomaly replication snippet did not answer the calculation boundary | Mutable mirror; no authoritative revision state |
| 8 / `turn184search2` | [Terms Glossary — CRSP U.S. Equity Indexes Methodology Guide](https://1library.net/article/terms-glossary-crsp-u-equity-indexes-methodology-guide.q02wjjvy) | mirror of official method | `U-CRSP-INDEX-METHOD` | `EX-DUP`; same upstream as official CRSP guide | Unversioned mirror; official current bytes preferred |
| 9 / `turn184search3` | [CRSP — Universidad Carlos III de Madrid](https://business.uc3m.es/en/databases/crsp/) | institutional database description | `U-UC3M-CRSP` | `IN-S`; useful product background, not a calculation authority | Mutable university page; no visible revision |
| 10 / `turn184search4` | [Comment on CRSP CIZ Monthly Return — PDF](https://papers.ssrn.com/sol3/Delivery.cfm/5203740.pdf?abstractid=5203740&mirid=1) | independent working paper | `U-CRSP-CIZ-COMMENT` | `IN-C`; identifies monthly-return differences from stale prices and distribution timing; retained as method-change counterevidence | SSRN working-paper artifact; visible result did not expose fixed revision identifier |
| 11 / `turn184search5` | [CRSP U.S. Equity Indexes Methodology Guide](https://www.yumpu.com/en/document/view/54694374/crsp-us-equity-indexes-methodology-guide) | mirror of official method | `U-CRSP-INDEX-METHOD` | `EX-DUP`; same upstream, older mirror | Mutable mirror; superseded by official July 2026 bytes |
| 12 / `turn184search6` | [CRSP Data Description Guide: US Stock & Indices Database](https://studylib.net/doc/8889446/crsp-data-description-guide) | mirror of official method | `U-CRSP-RDP-METHOD` | `EX-DUP`; same legacy upstream, mirror authority weaker | Old mirror; no reliable revision state |
| 13 / `turn184search7` | [SEC archive filing containing CRSP index methodology](https://www.sec.gov/Archives/edgar/data/19617/000095010316012649/dp64909_424b2-usn1i.htm) | official filing containing third-party method text | `U-SEC-JPM-NOTE` | `EX-DUP`; filing is primary for the note, not the current CRSP method; same calculations available from CRSP | Immutable SEC filing, but historical and not current method authority |
| 14 / `turn184search8` | [CRSP Guides Archive](https://www.crsp.org/pdf_type/guides/) | official archive/navigation | `U-CRSP-INDEX-METHOD` | `IN-S`; used to navigate to the saved current official guide | Mutable archive page; points to current July 2026 PDF |
| 15 / `turn184search9` | [Comment on CRSP CIZ Monthly Return — abstract](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5203740) | independent working-paper landing page | `U-CRSP-CIZ-COMMENT` | `EX-DUP`; duplicate of order 10 | Same working paper; landing page mutable |
| 16 / `turn184search10` | [How do I obtain returns with dividends from CRSP?](https://www.stat.rice.edu/~dobelman/courses/486/faq/FAQ00054.htm) | instructional FAQ | `U-RICE-CRSP-FAQ` | `EX-AUTH`; concise secondary explanation, not a current method source | Mutable course page; no visible revision |
| 17 / `turn184search11` | [(PDF) Stock Dividends, Stock Splits, and Signaling](https://www.researchgate.net/publication/4992238_Stock_Dividends_Stock_Splits_and_Signaling) | academic-paper locator | `U-SPLIT-SIGNALING-PAPER` | `EX-SCOPE`; studies signaling/returns, not the provider-neutral accounting/PIT contract | Historical paper repository copy |
| 18 / `turn184academia17` | [Stock market return distributions: from past to present](https://arxiv.org/abs/0704.0664) | preprint | `U-RETURN-DISTRIBUTION-2007` | `EX-NOISE`; “return distributions” semantic collision | Versioned arXiv record but unrelated |
| 19 / `turn184academia18` | [Precision measurement of the return distribution property of the Chinese stock market index](https://arxiv.org/abs/2209.08521) | preprint | `U-CN-RETURN-DISTRIBUTION` | `EX-NOISE`; statistical return distribution, not corporate-action calculations | Versioned arXiv record but unrelated |
| 20 / `turn184academia19` | [Financial Return Distributions: Past, Present, and COVID-19](https://arxiv.org/abs/2107.06659) | preprint | `U-FINANCIAL-RETURN-DISTRIBUTION` | `EX-NOISE`; statistical return distribution, not accounting method | Versioned arXiv record but unrelated |
| 21 / `turn184search20` | [Center for Research in Security Prices](https://en.wikipedia.org/wiki/Center_for_Research_in_Security_Prices) | encyclopedia | `U-WIKIPEDIA-CRSP` | `EX-AUTH`; orientation only, not claim evidence | Continuously mutable |
| 22 / `turn184academia21` | [Distributions of Historic Market Data — Stock Returns](https://arxiv.org/abs/1711.11003) | preprint | `U-HISTORIC-RETURN-DISTRIBUTION` | `EX-NOISE`; unrelated statistical distribution paper | Versioned arXiv record but unrelated |
| 23 / `turn184reddit22` | [Does the DRP double calculated return?](https://www.reddit.com/r/CSPersonalFinance/comments/1u9trq2/does_the_drp_double_calculated_in_the_estreturnyr/) | practitioner thread | `U-REDDIT-CSPF-DRP` | `EX-SCOPE`; consumer spreadsheet question, no provider/PIT boundary | Mutable thread |
| 24 / `turn184search23` | [Rate of return](https://en.wikipedia.org/wiki/Rate_of_return) | encyclopedia | `U-WIKIPEDIA-RATE-RETURN` | `EX-AUTH`; generic definition, no RS-03 boundary | Continuously mutable |
| 25 / `turn184reddit24` | [Calculating the dividend rate of STRC/SATA](https://www.reddit.com/r/STRC/comments/1v2krx0/calculating_the_dividend_rate_of_strcsata_based/) | practitioner thread | `U-REDDIT-STRC-DIVIDEND` | `EX-SCOPE`; forward-yield discussion | Mutable thread |
| 26 / `turn184reddit25` | [MOD: show total return without distribution/dividend component](https://www.reddit.com/r/CSPersonalFinance/comments/16od0q7) | practitioner thread | `U-REDDIT-CSPF-MOD` | `EX-SCOPE`; application-specific feature request | Mutable thread |
| 27 / `turn184reddit26` | [Total monthly stock returns from Compustat versus CRSP](https://www.reddit.com/r/quant/comments/yb1dp8) | practitioner thread | `U-REDDIT-QUANT-CRSP-COMPUSTAT` | `EX-AUTH`; relevant user question but no primary mechanism evidence | Mutable thread |
| 28 / `turn184reddit27` | [Backtesting a value strategy with CRSP and Compustat](https://www.reddit.com/r/algorithmictrading/comments/1rlfs80/backtesting_a_value_strategy_top_20_booktomarket/) | practitioner thread | `U-REDDIT-VALUE-BACKTEST` | `EX-SCOPE`; strategy review request, not calculation standard | Mutable thread |
| 29 / `turn184reddit28` | [The DIVIDEND GRAIL — dividends and splits](https://www.reddit.com/r/Superstonk/comments/ttszs6) | practitioner thread | `U-REDDIT-SUPERSTONK-GRAIL` | `EX-AUTH`; terminology discussion without authoritative method | Mutable thread |
| 30 / `turn184reddit29` | [Total Return and Total Growth spreadsheet question](https://www.reddit.com/r/CSPersonalFinance/comments/p0z8py) | practitioner thread | `U-REDDIT-CSPF-RETURN` | `EX-SCOPE`; spreadsheet behavior | Mutable thread |
| 31 / `turn184reddit30` | [How to adjust historical prices for stock splits and dividends](https://www.reddit.com/r/Massive/comments/1r8fv3a/how_to_adjust_historical_prices_for_stock_splits/) | provider-affiliated practitioner thread | `U-MASSIVE-CA-API` | `IN-C`; classification example and reopen probe only; not independent authority | Mutable promotional thread; provider behavior can change |
| 32 / `turn184reddit31` | [Why are CRSP and TWS API historical daily data different?](https://www.reddit.com/r/algotrading/comments/mcjz8n) | practitioner thread | `U-REDDIT-CRSP-TWS-DIFF` | `IN-C`; retained as cross-provider reconciliation failure hypothesis only | Mutable historical thread |
| 33 / `turn184reddit32` | [Segmenting total return between price return and dividends](https://www.reddit.com/r/CFA/comments/lkf67h) | practitioner thread | `U-REDDIT-CFA-RETURN` | `EX-AUTH`; generic formula discussion | Mutable thread |
| 34 / `turn184reddit33` | [Stock calculator including splits and dividends](https://www.reddit.com/r/learnpython/comments/1d30bzs) | practitioner thread | `U-REDDIT-LEARNPYTHON-CALC` | `EX-SCOPE`; implementation help request | Mutable thread |
| 35 / `turn184reddit34` | [Dividend splits versus traditional splits in return swaps](https://www.reddit.com/r/Superstonk/comments/1f9ywfo) | practitioner thread | `U-REDDIT-SUPERSTONK-SWAP` | `EX-AUTH`; terminology assertion without authoritative source | Mutable thread |

## R8-RS03-D2

- Exact query: `official corporate action event effective ex date cash dividend stock split data standard`
- Search-call window UTC: `2026-07-25T16:17:30Z` → `2026-07-25T16:17:39Z`
- Search calls for this query_id: exactly one
- Complete visible result count: 32

| Order / backend ref | Title and URL | Source class | Upstream cluster | Screening and reason | Revision / supersession state |
|---|---|---|---|---|---|
| 1 / `turn187search12` | [NYSE Corporate Actions Client Specification v3.2](https://www.nyse.com/publicdocs/nyse/data/NYSE_CorporateActions_Client_Specification.v3.2.pdf) | official exchange specification | `U-NYSE-CA` | `EX-DUP`; superseded by adjacent v3.2a result | Versioned v3.2; superseded by v3.2a |
| 2 / `turn187search13` | [NYSE Corporate Actions Client Specification v3.2a](https://www.nyse.com/publicdocs/nyse/data/NYSE_CorporateActions_Client_Specification.v3.2a.pdf) | official exchange specification | `U-NYSE-CA` | `IN-D`; explicit declared, ex, record, pay/effective, split, cancel, and update fields; exact bytes saved | Versioned v3.2a; exact artifact saved |
| 3 / `turn187search0` | [Cboe BZX Exchange U.S. Listing Corporate Actions Specification](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-bzx-exchange-u.s.-listing-corporate-actions-specification) | official exchange specification | `U-CBOE-CA` | `IN-D`; distinct report publication, declared, updated, ex, record, payment, effective, and status fields; exact bytes saved | Mutable live specification with embedded revision history |
| 4 / `turn187search1` | [Corporate Actions for NYSE Group Listings](https://www.nyse.com/data-products/catalog/corporate-actions-for-nyse-group-listings) | official exchange product documentation | `U-NYSE-CA` | `IN-S`; supports intraday/end-of-day publication cadence and product boundary | Mutable live catalog page |
| 5 / `turn187search2` | [NYSE Corporate Actions](https://www.nyse.com/market-data/corporate-actions) | official exchange landing page | `U-NYSE-CA` | `EX-DUP`; product overview duplicates order 4/specification family | Mutable live landing page |
| 6 / `turn187search14` | [NYSE Corporate Actions Client Specification v3.1](https://www.nyse.com/publicdocs/nyse/data/NYSE_CorporateActions_Client_Specification.v3.1.pdf) | official exchange specification | `U-NYSE-CA` | `EX-DUP`; older version | Versioned v3.1; superseded |
| 7 / `turn187search3` | [Kaiko Corporate Action Reference Data](https://docs.kaiko.com/kaiko-indices/reference-rates-others/subscribe/corporate-action-reference-data) | provider documentation | `U-KAIKO-CA` | `IN-S`; useful typed-event/status illustration, not an exchange standard | Mutable provider docs; no visible fixed revision |
| 8 / `turn187search15` | [ASX ReferencePoint ISO 20022 Corporate Actions FAQ v1.2](https://www2.asx.com.au/content/dam/asx/participants/clearing-and-settlement/settlement/referencepoint-iso-20022-corporate-actions-frequently-asked-questions-v-1.2.pdf) | official exchange FAQ | `U-ASX-CA` | `IN-C`; jurisdiction-specific effective/ex mapping retained as variation probe | Versioned v1.2 PDF |
| 9 / `turn187search4` | [NYSE Regulation — Corporate Actions, Market Watch & Proxy Compliance](https://www.nyse.com/regulation/corporate-actions-market-watch-proxy-compliance) | official exchange regulation page | `U-NYSE-REG-CA` | `IN-S`; distinguishes announcement from anticipated effective timing | Mutable official page |
| 10 / `turn187search5` | [FINRA Uniform Practice Code FAQ](https://www.finra.org/filing-reporting/market-transparency-reporting/uniform-practice-code-upc/faq) | official regulator FAQ | `U-FINRA-UPC` | `IN-S`; official ex-dividend and notice context | Mutable official FAQ |
| 11 / `turn187search6` | [LSEG Workspace Corporate Actions Content Set](https://developers.lseg.com/en/article-catalog/article/workspace-corporate-actions-content-set-guide) | provider documentation | `U-LSEG-CA` | `IN-S`; date taxonomy and downstream-error background; not the selected standard | Mutable provider article |
| 12 / `turn187search7` | [ICE Reference Data — Corporate Actions](https://developer.ice.com/fixed-income-data-services/catalog/ice-reference-data-corporate-actions) | provider catalog | `U-ICE-CA` | `IN-S`; event taxonomy and official-source claim only; no calculation details | Mutable product catalog |
| 13 / `turn187search8` | [FINRA — Corporate Actions by Public Companies](https://www.finra.org/investors/insights/corporate-actions-public-companies-what-you-should-know) | official regulator investor guidance | `U-FINRA-INVESTOR-CA` | `IN-S`; split and ex-date orientation, weaker than operational specification | Mutable official guidance |
| 14 / `turn187search9` | [Webull Corporate Actions Events API](https://developer.webull.com/apis/docs/reference/fd-events/ca-events/) | provider API documentation | `U-WEBULL-CA` | `EX-AUTH`; provider schema not needed over exchange specifications | Mutable provider docs |
| 15 / `turn187search10` | [TW Market Data — Corporate Actions](https://twmarketdata.com/en/docs/api/companies-events/corporate-actions) | downstream provider documentation | `U-TW-MARKETDATA-CA` | `IN-C`; PIT warning retained as provider hypothesis only, not standard evidence | Mutable provider docs |
| 16 / `turn187search11` | [FINRA Notice to Members 91-63](https://www.finra.org/rules-guidance/notices/91-63) | official historical rule notice | `U-FINRA-1991-CA` | `EX-DUP`; historical settlement/ex-date convention is not current operational boundary | Immutable historical notice; later settlement regimes supersede |
| 17 / `turn187search16` | [Corporate action](https://en.wikipedia.org/wiki/Corporate_action) | encyclopedia | `U-WIKIPEDIA-CA` | `EX-AUTH`; orientation only | Continuously mutable |
| 18 / `turn187reddit17` | [Updated questions for your brokerage as to how they were directed to do the dividend](https://www.reddit.com/r/Superstonk/comments/wic2x6) | practitioner thread | `U-REDDIT-SUPERSTONK-CA1` | `EX-AUTH`; classification discussion without primary standard bytes | Mutable thread |
| 19 / `turn187search18` | [Ex-dividend date](https://en.wikipedia.org/wiki/Ex-dividend_date) | encyclopedia | `U-WIKIPEDIA-EXDATE` | `EX-AUTH`; secondary and continuously mutable | Continuously mutable |
| 20 / `turn187reddit19` | [Clarifications on dividend filing discussions](https://www.reddit.com/r/Superstonk/comments/wgtxjo) | practitioner thread | `U-REDDIT-SUPERSTONK-CA2` | `IN-C`; event-code confusion retained only as classification failure hypothesis | Mutable thread |
| 21 / `turn187academia20` | [The Pricing of Vanilla Options with Cash Dividends](https://arxiv.org/abs/2106.12971) | preprint | `U-OPTIONS-CASH-DIVIDEND` | `EX-SCOPE`; option-pricing model, not operational corporate-action timing | Versioned arXiv record |
| 22 / `turn187reddit21` | [Analysis of dividend ex-date recovery events](https://www.reddit.com/r/dividends/comments/1t026ja/i_analyzed_151422_dividend_exdate_events_across/) | practitioner thread | `U-REDDIT-DIVIDEND-STATS` | `EX-AUTH`; self-reported dataset and bot content, not timing standard | Mutable thread |
| 23 / `turn187academia22` | [Trade the Event: Corporate Events Detection for News-Based Trading](https://arxiv.org/abs/2105.12825) | preprint | `U-NEWS-EVENT-DETECTION` | `EX-SCOPE`; event detection, not accounting/timing definition | Versioned arXiv record |
| 24 / `turn187search23` | [Stock split](https://en.wikipedia.org/wiki/Stock_split) | encyclopedia | `U-WIKIPEDIA-SPLIT` | `EX-AUTH`; secondary orientation only | Continuously mutable |
| 25 / `turn187reddit24` | [What Are Corporate Actions?](https://www.reddit.com/r/Backpack_official/comments/1tlcjwn/what_are_corporate_actions_types_dates_and_what/) | provider-affiliated practitioner post | `U-REDDIT-BACKPACK-CA` | `EX-AUTH`; marketing/education post, no standard authority | Mutable thread |
| 26 / `turn187search25` | [Dividend](https://en.wikipedia.org/wiki/Dividend) | encyclopedia | `U-WIKIPEDIA-DIVIDEND` | `EX-AUTH`; secondary orientation only | Continuously mutable |
| 27 / `turn187academia26` | [On the optimality of joint periodic and extraordinary dividend strategies](https://arxiv.org/abs/2006.00717) | preprint | `U-DIVIDEND-OPTIMIZATION` | `EX-SCOPE`; mathematical payout strategy, not data standard | Versioned arXiv record |
| 28 / `turn187academia27` | [A study about who is interested in stock splitting and why](https://arxiv.org/abs/2510.15879) | preprint | `U-SPLIT-BEHAVIOR-STUDY` | `EX-SCOPE`; behavioral study, not operational data semantics | Versioned arXiv record |
| 29 / `turn187reddit28` | [Why have I got this message?](https://www.reddit.com/r/MU_Stock/comments/1um5w0r/why_have_i_got_this_message/) | practitioner thread | `U-REDDIT-MU-CA` | `EX-NOISE`; isolated user question | Mutable thread |
| 30 / `turn187search29` | [Special dividend](https://en.wikipedia.org/wiki/Special_dividend) | encyclopedia | `U-WIKIPEDIA-SPECIAL-DIVIDEND` | `EX-AUTH`; secondary and special-action scope outside automatic V1 | Continuously mutable |
| 31 / `turn187search30` | [Common stock dividend](https://en.wikipedia.org/wiki/Common_stock_dividend) | encyclopedia | `U-WIKIPEDIA-COMMON-DIVIDEND` | `EX-AUTH`; secondary orientation only | Continuously mutable |
| 32 / `turn187reddit31` | [This is about share distribution and not the stock split](https://www.reddit.com/r/Superstonk/comments/whchin) | practitioner thread | `U-REDDIT-SUPERSTONK-CA3` | `IN-C`; classification-confusion probe only; same practitioner family as orders 18/20 | Mutable thread |

## R8-RS03-S1

- Exact query: `point in time market data correction revision available timestamp methodology`
- Search-call window UTC: `2026-07-25T16:20:49Z` → `2026-07-25T16:20:57Z`
- Search calls for this query_id: exactly one
- Complete visible result count: 24

| Order / backend ref | Title and URL | Source class | Upstream cluster | Screening and reason | Revision / supersession state |
|---|---|---|---|---|---|
| 1 / `turn201search0` | [Platts Market Data User Guide](https://paperzz.com/doc/6970554/platts-market-data-user-guide) | mirror of provider manual | `U-PLATTS-MANUAL` | `IN-S`; correction ordering and last-correction mechanism relevant, but mirror not selected as decisive | Unversioned mirror; upstream provider manual revision unclear |
| 2 / `turn201search1` | [Cboe Titanium U.S. Equities Last Sale Specification](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-titanium-u.s.-equities-last-sale-specification) | official exchange specification | `U-CBOE-LAST-SALE` | `IN-S`; demonstrates distinct clock/reference semantics and revision history | Live spec includes revision history and future effective fields |
| 3 / `turn201search2` | [CoinAPI Glossary — Point-in-Time](https://www.coinapi.io/learn/glossary/point-in-time-pit) | provider glossary | `U-COINAPI-PIT` | `EX-AUTH`; correct orientation but marketing-level definition | Mutable provider page |
| 4 / `turn201search3` | [Platts Market Data User Guide 2021](https://www.scribd.com/document/714384717/S-P-Platts-market-data-user-manual) | mirror of provider manual | `U-PLATTS-MANUAL` | `EX-DUP`; same upstream as order 1 | Historical mirror copy |
| 5 / `turn201search4` | [Messari Market Data Methodology](https://old-docs.messari.io/docs/market-data-methodology) | provider methodology | `U-MESSARI-METHOD` | `IN-C`; explicit recomputation/backfill behavior supports revision failure class; provider-specific | Old-docs route; mutable and potentially superseded |
| 6 / `turn201search12` | [Accurately Backtesting Financial Models Through Point-in-Time Consensus Estimates](https://www.insight.factset.com/hubfs/Resources%20Section/White%20Papers/ID11996_point_in_time.pdf?hsLang=en-us) | primary provider methodology / white paper | `U-FACTSET-PIT` | `IN-D`; directly contrasts historical snapshot with latest corrected/deleted database behavior; exact canonical bytes saved without query suffix | Mutable locator to fixed PDF bytes as retrieved |
| 7 / `turn201search5` | [The Participant Timestamp: Get The Most Out Of TAQ Data](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID4077824_code4513650.pdf?abstractid=3744743&mirid=1&type=2) | research paper | `U-TAQ-PARTICIPANT-TIMESTAMP` | `IN-S`; supports multiple non-equivalent timestamps, but not revision storage | SSRN paper showed a later revision date in visible result |
| 8 / `turn201search6` | [TradeStation Corrections, Deletions & Insertions](https://help.tradestation.com/09_01/tradestationhelp/desktop/corrections_deletions_insertions.htm) | provider help | `U-TRADESTATION-CORRECTIONS` | `IN-S`; concrete correction/delete/insert mechanism | Versioned-looking help route `09_01`; current status unclear |
| 9 / `turn201search7` | [SIX API Portal Data Dictionary](https://web.apiportal.six-group.com/portal/bfi/data-dictionary) | provider data dictionary | `U-SIX-TIMESTAMP` | `IN-S`; multiple upstream timestamp meanings and priority ordering | Mutable live dictionary; no visible revision |
| 10 / `turn201search8` | [Cboe Titanium Equities/Options Multicast PITCH Specification](https://www.cboe.com/document/tech-spec/document/technical-specifications/cboe-titanium-u.s.-equitiesoptions-multicast-pitch-specification) | official exchange specification | `U-CBOE-PITCH` | `IN-S`; unambiguous absolute-time warning, not correction methodology | Live spec with revision/effective-date sections |
| 11 / `turn201search13` | [Accurately Backtesting Financial Models Through Point-in-Time Consensus Estimates — duplicate locator](https://www.insight.factset.com/hubfs/Resources%20Section/White%20Papers/ID11996_point_in_time.pdf) | primary provider methodology / white paper | `U-FACTSET-PIT` | `EX-DUP`; same exact upstream artifact as order 6 | Same PDF |
| 12 / `turn201search9` | [Valuein Methodology — Point-in-Time SEC Data](https://valuein.biz/methodology) | downstream provider methodology | `U-VALUEIN-PIT` | `IN-S`; append-on-restatement and accepted-time illustration; self-described provider behavior only | Mutable live page |
| 13 / `turn201search10` | [Glassnode Data Finalization](https://docs.glassnode.com/data/general-information/data-finalization) | provider documentation | `U-GLASSNODE-FINALIZATION` | `IN-C`; mutable/finalized data and retrospective correction failure probe | Mutable docs; visible result said recently updated but no fixed revision |
| 14 / `turn201search11` | [Cboe LiveVol Data Shop FAQ](https://datashop.cboe.com/faqs) | official exchange/provider FAQ | `U-CBOE-LIVEVOL` | `EX-SCOPE`; timestamp orientation but no correction/revision boundary for selected design | Mutable FAQ |
| 15 / `turn201search14` | [Euronext Clearing Reporting Guide](https://www.euronext.com/sites/default/files/2024-02/emir_reporting_guidelines_for_euronext_legacy_markets_v1.0_-_applicable_from_migration-go-live_dates.pdf) | official clearing guide | `U-EURONEXT-REPORTING` | `EX-SCOPE`; transaction reporting, not market-data PIT revision | Versioned v1.0 PDF |
| 16 / `turn201search15` | [Cboe Options Timestamping Service Specification](https://cdn.cboe.com/resources/membership/Options_Timestamping_Service_Specification.pdf) | official exchange specification | `U-CBOE-OPTIONS-TIMESTAMP` | `EX-SCOPE`; options architecture and future/effective revisions, not selected daily-data contract | Versioned PDF with revision history |
| 17 / `turn201search16` | [CPMI-IOSCO CDE2 ISDA response](https://www.isda.org/a/7ZiDE/cpmi-iosco-cde2-isda-response-30-november-2016-public.pdf) | industry response paper | `U-ISDA-REPORTING-TIMESTAMP` | `EX-SCOPE`; trade repository reporting time, not market-data availability | Fixed dated PDF |
| 18 / `turn201academia17` | [Quantitative Analysis by the Point-Centered Quarter Method](https://arxiv.org/abs/1010.3303) | preprint | `U-ECOLOGY-PCQ` | `EX-NOISE`; “point-in-time” semantic collision | Versioned arXiv record |
| 19 / `turn201academia18` | [Time Accuracy Analysis of Packet-Switched Charging Data Records](https://arxiv.org/abs/1705.04418) | preprint | `U-CDR-TIME-ACCURACY` | `EX-NOISE`; telecom timestamps | Versioned arXiv record |
| 20 / `turn201academia19` | [Topological Data Analysis of Financial Time Series](https://arxiv.org/abs/1703.04385) | preprint | `U-TDA-FINANCIAL-TIME` | `EX-SCOPE`; no revision/availability method | Versioned arXiv record |
| 21 / `turn201academia20` | [Fluctuations and response in financial markets](https://arxiv.org/abs/cond-mat/0307332) | preprint | `U-MARKET-RESPONSE-PAPER` | `EX-SCOPE`; market microstructure theory, not snapshot revision | Versioned arXiv record |
| 22 / `turn201reddit21` | [TradingView data-corruption proof claim](https://www.reddit.com/r/TradingView/comments/1t6hx5w/data_corruption_proof_1d1w1m_timeframes_are/) | practitioner report | `U-REDDIT-TRADINGVIEW-CORRECTION` | `IN-C`; aggregation/correction failure hypothesis only | Mutable thread; self-reported |
| 23 / `turn201reddit22` | [Interpreting timestamps in the IBKR audit trail](https://www.reddit.com/r/IBKR_Official/comments/1sx7gqk/interpreting_time_stamps_in_the_audit_trail/) | practitioner thread | `U-REDDIT-IBKR-TIMESTAMP` | `EX-AUTH`; speculative explanation, no official mechanism | Mutable thread |
| 24 / `turn201reddit23` | [Structured point-in-time historical data?](https://www.reddit.com/r/algotrading/comments/1tj2b3p/structured_pointintime_historical_data/) | practitioner thread | `U-REDDIT-PIT-DATA` | `IN-C`; provider shortfall/user-burden hypothesis only | Mutable thread |

## R8-RS03-S2

- Exact query: `counterexample adjusted historical price lookahead corporate action backtest`
- Search-call window UTC: `2026-07-25T16:22:00Z` → `2026-07-25T16:22:12Z`
- Search calls for this query_id: exactly one
- Complete visible result count: 35

| Order / backend ref | Title and URL | Source class | Upstream cluster | Screening and reason | Revision / supersession state |
|---|---|---|---|---|---|
| 1 / `turn209search0` | [Kibot Adjusted vs Unadjusted Historical Data](https://www.kibot.com/file-format/adjusted-vs-unadjusted-data.html) | provider documentation | `U-KIBOT-ADJUSTMENT` | `IN-S`; explicitly describes retroactive rewrites and audit use of raw data | Mutable provider docs; no visible revision |
| 2 / `turn209search1` | [How to Handle Corporate Actions in Backtests](https://www.alphanume.com/blog/how-to-handle-corporate-actions-in-backtests) | provider/practitioner article | `U-ALPHANUME-CA` | `IN-S`; direct PIT-adjustment warning, but not independent method authority | Dated article; mutable site |
| 3 / `turn209search2` | [Point-in-Time Backtesting of Momentum-Trend Equity Strategies — preprint page](https://www.preprints.org/manuscript/202606.0436) | preprint | `U-PIT-BACKTEST-2026` | `IN-S`; formalizes price-data forward leakage; retrieved PDF labels itself not peer-reviewed | Versioned preprint v1 |
| 4 / `turn209search3` | [OpenAlgo — Look-Ahead, Survivorship and Corporate-Action Bias](https://openalgo.in/quant/bias-lookahead-survivorship) | practitioner/educational article | `U-OPENALGO-BIAS` | `IN-S`; clear failure mechanism, secondary authority | Mutable article |
| 5 / `turn209search4` | [A Taxonomy of Backtest Lies](https://www.susanpotter.net/quant/backtest-bias-taxonomy/) | practitioner article | `U-POTTER-BIAS` | `IN-S`; supporting explanation only | Mutable article |
| 6 / `turn209search5` | [Forward- and backward-adjusting stock prices](https://quant.stackexchange.com/questions/4383/forward-and-backward-adjusting-stockprices) | practitioner Q&A | `U-QSE-FORWARD-BACKWARD` | `IN-C`; practical counterexample/alternative adjustment direction, not primary authority | Mutable Q&A; historical edits possible |
| 7 / `turn209search6` | [Pomegra Historical Data Sources](https://pomegra.io/learn/library/track-e-trading-risk/active-trading/chapter-10-backtesting/historical-data-sources) | educational secondary | `U-POMEGRA-DATA` | `EX-AUTH`; generic guidance | Mutable training page |
| 8 / `turn209search7` | [Futubull — How corporate actions are handled in a backtest](https://support.futunn.com/en/topic801) | broker/provider help | `U-FUTU-CA` | `IN-S`; illustrates separate holdings and cash effects, provider-specific | Mutable provider help |
| 9 / `turn209reddit12` | [NSE backtesting engine with corporate-action-adjusted data](https://www.reddit.com/r/DalalStreetTalks/comments/1uo1hzv/built_a_backtesting_engine_for_nse_stocks_with/) | practitioner thread | `U-REDDIT-NSE-ENGINE` | `IN-C`; user-burden and missing-path hypothesis only | Mutable thread |
| 10 / `turn209search8` | [algoseek Equity Adjustment Factors Detail](https://algoseek.com/data-sets/docs/eq_adj_factors_detail) | provider documentation | `U-ALGOSEEK-ADJUSTMENT` | `IN-S`; raw/as-is versus adjustment-factor product boundary | Mutable provider docs |
| 11 / `turn209search9` | [Point-in-Time Backtesting of Momentum-Trend Equity Strategies — Mathematics](https://www.mdpi.com/2227-7390/14/12/2182) | journal article | `U-PIT-BACKTEST-2026` | `IN-D`; peer-reviewed publication locator for the same failure class; direct web open failed, so saved preprint was not misrepresented as this artifact | Current journal page; no saved exact bytes |
| 12 / `turn209search10` | [How to Avoid Look-Ahead Bias in Universe Construction](https://www.alphanume.com/blog/avoid-look-ahead-bias-universe-construction) | provider/practitioner article | `U-ALPHANUME-CA` | `EX-DUP`; same upstream and broader universe scope than order 2 | Dated article; mutable site |
| 13 / `turn209search11` | [Adjusted close prices on S&P 500](https://quant.stackexchange.com/questions/9070/adjusted-close-prices-on-sp500) | practitioner Q&A | `U-QSE-ADJUSTED-CLOSE` | `IN-C`; cumulative historical-basis confusion probe only | Mutable Q&A |
| 14 / `turn209reddit13` | [NSE backtesting engine — cross-post](https://www.reddit.com/r/IndiaAlgoTrading/comments/1uo16oq/built_a_backtesting_engine_for_nse_stocks_with/) | practitioner thread | `U-REDDIT-NSE-ENGINE` | `EX-DUP`; same project/content as order 9 | Mutable cross-post |
| 15 / `turn209academia14` | [Uncertainty-Aware Lookahead Factor Models for Quantitative Investing](https://arxiv.org/abs/2007.04082) | preprint | `U-LOOKAHEAD-FACTOR-MODEL` | `EX-NOISE`; “lookahead” is the model name, not leakage/corporate-action bias | Versioned arXiv record |
| 16 / `turn209search15` | [Seven Sins of Quantitative Investing](https://hudsonthames.org/wp-content/uploads/2022/01/DB-201409-Seven_Sins_of_Quantitative_Investing.pdf) | independent institutional research | `U-DB-SEVEN-SINS` | `IN-D`; worked split-adjustment look-ahead counterexample and mitigation; exact bytes saved | Fixed dated PDF as retrieved |
| 17 / `turn209search16` | [Point-in-Time Backtesting — preprint PDF](https://www.preprints.org/frontend/manuscript/b8db286b07452ae7019c308413c28e10/download_pub) | preprint | `U-PIT-BACKTEST-2026` | `EX-DUP`; same upstream as orders 3/11; useful text extraction but not a separate cluster | Versioned preprint v1; explicitly not peer-reviewed |
| 18 / `turn209reddit17` | [Corporate action effects on bhav copy and short-term swing trades](https://www.reddit.com/r/IndianStockMarket/comments/1taz7ym/corporate_action_effects_on_bhav_copy_and_how_it/) | practitioner report | `U-REDDIT-BHAV-MISMATCH` | `IN-C`; adjusted monthly versus unadjusted intraday mismatch hypothesis | Mutable self-report |
| 19 / `turn209reddit18` | [Backtest/live divergence caused by a stock split](https://www.reddit.com/r/Trading/comments/1un7y9l/a_subtle_backtestlive_divergence_caused_by_a/) | practitioner report | `U-REDDIT-SPLIT-DIVERGENCE` | `IN-C`; vendor re-adjustment between signal/execution failure hypothesis | Mutable self-report |
| 20 / `turn209reddit19` | [Building a local NSE/BSE data pipeline](https://www.reddit.com/r/IndiaAlgoTrading/comments/1uoxpzy/advice_needed_building_a_local_nsebse_data/) | practitioner thread | `U-REDDIT-NSE-PIPELINE` | `IN-C`; implementation burden and raw-action parsing probe | Mutable thread |
| 21 / `turn209academia20` | [Adjusted Closing Prices](https://arxiv.org/abs/1105.2956) | preprint | `U-ADJUSTED-CLOSING-PRICES` | `IN-S`; calculation method background, not itself a look-ahead counterexample | Versioned arXiv record |
| 22 / `turn209academia21` | [Determining Optimal Trading Rules without Backtesting](https://arxiv.org/abs/1408.1159) | preprint | `U-OPTIMAL-RULES` | `EX-SCOPE`; backtest overfitting, not corporate-action adjustment | Versioned arXiv record |
| 23 / `turn209reddit22` | [Reliable historical Indian market data for backtesting](https://www.reddit.com/r/IndiaAlgoTrading/comments/1u39pdq/best_sources_for_reliable_historical_indian_stock/) | practitioner thread | `U-REDDIT-INDIA-DATA` | `IN-C`; data-source burden only | Mutable thread |
| 24 / `turn209search23` | [Wiley excerpt — corporate-action adjustment](https://catalogimages.wiley.com/images/db/pdf/9781118460146.excerpt.pdf) | book excerpt | `U-WILEY-ALGO-BOOK` | `IN-S`; secondary method background | Fixed publisher excerpt |
| 25 / `turn209search25` | [Pocketbook sample — corporate actions and adjustment](https://pocketbook.de/en/downloadable/download/sample/sample_id/5576353/?bookId=MTQzMTYyMTU%3D) | book sample | `U-POCKETBOOK-CA` | `EX-AUTH`; snippet insufficient and no clear canonical range | Mutable download route |
| 26 / `turn209reddit24` | [Pine Script defaults that improved a backtest](https://www.reddit.com/r/pinescript/comments/1trqi21/the_three_pine_script_defaults_that_made_my/) | practitioner thread | `U-REDDIT-PINESCRIPT-LOOKAHEAD` | `EX-SCOPE`; same-bar/higher-timeframe leakage, not corporate-action adjustment | Mutable thread |
| 27 / `turn209reddit26` | [Options data made the backtest lie](https://www.reddit.com/r/IndiaAlgoTrading/comments/1u8a399/your_backtest_is_probably_lying_to_you_and_its/) | practitioner thread | `U-REDDIT-OPTIONS-DATA` | `EX-SCOPE`; options cleaning/slippage, not selected equity-action boundary | Mutable thread |
| 28 / `turn209reddit27` | [Backtest/data assuring accuracy](https://www.reddit.com/r/algotrading/comments/1so6l7n/backtestdata_assuring_accuracy/) | practitioner thread | `U-REDDIT-DATA-ACCURACY` | `IN-C`; no-reconstructed-history and event-at-occurrence probe | Mutable thread |
| 29 / `turn209search28` | [Algorithmic Trading preview](https://s3-euw1-ap-pe-df-pch-content-store-p.s3.eu-west-1.amazonaws.com/9780429183942/63b9fd89-9d09-4b8c-9b01-8ccd5db854f4/preview.pdf) | book preview | `U-ALGO-TRADING-BOOK` | `IN-S`; general corporate-action continuity background; the visible result supplied an expiring signed query whose credential-like parameters were intentionally not persisted | Base object locator retained; signed query was temporary and not a stable canonical locator |
| 30 / `turn209reddit29` | [Backtested three textbook rules over twenty years](https://www.reddit.com/r/algorithmictrading/comments/1ue4oj0/i_backtested_the_3_most_boring_textbook_rules/) | practitioner thread | `U-REDDIT-TEXTBOOK-RULES` | `EX-SCOPE`; method-review thread, adjusted data merely mentioned | Mutable thread |
| 31 / `turn209reddit30` | [Platform for backtesting without building from scratch](https://www.reddit.com/r/IndiaAlgoTrading/comments/1uhu7r1/is_there_any_platform_where_i_can_backtest_stock/) | practitioner thread | `U-REDDIT-BACKTEST-PLATFORM` | `EX-SCOPE`; recommendation request | Mutable thread |
| 32 / `turn209academia31` | [Boosting Stock Price Prediction with Anticipated Macro Policy Changes](https://arxiv.org/abs/2311.06278) | preprint | `U-ANTICIPATED-MACRO` | `EX-NOISE`; intentional forecasting, not leakage | Versioned arXiv record |
| 33 / `turn209reddit32` | [Backtested strategies from academic finance papers](https://www.reddit.com/r/ai_trading/comments/1spz3j3/we_backtested_5000_strategies_from_30_years_of/) | practitioner thread | `U-REDDIT-RESTATEMENT-CLAIM` | `IN-C`; restatement-look-ahead hypothesis without primary evidence | Mutable thread |
| 34 / `turn209search33` | [Backtesting](https://en.wikipedia.org/wiki/Backtesting) | encyclopedia | `U-WIKIPEDIA-BACKTEST` | `EX-AUTH`; generic background | Continuously mutable |
| 35 / `turn209search34` | [Purged cross-validation](https://en.wikipedia.org/wiki/Purged_cross-validation) | encyclopedia | `U-WIKIPEDIA-PURGED-CV` | `EX-SCOPE`; model-validation method, not corporate actions | Continuously mutable |

## R8-RS03-S3

- Exact query: `market data license personal use cache retention termination API terms`
- Search-call window UTC: `2026-07-25T16:23:12Z` → `2026-07-25T16:23:22Z`
- Search calls for this query_id: exactly one
- Complete visible result count: 17

| Order / backend ref | Title and URL | Source class | Upstream cluster | Screening and reason | Revision / supersession state |
|---|---|---|---|---|---|
| 1 / `turn213search0` | [Market Data Terms of Service](https://www.marketdata.app/terms/) | provider terms | `U-MARKETDATA-TERMS` | `IN-D`; personal-use, third-party terms, subscription deletion, and termination effects; exact bytes saved | Page states Last Updated 18 August 2025; mutable terms |
| 2 / `turn213search1` | [Market Data Professional Use Addendum](https://www.marketdata.app/terms/professional-use/) | provider addendum | `U-MARKETDATA-TERMS` | `IN-S`; plan-specific retention/deletion exception contrast; same upstream not independent | Mutable addendum; relationship to main agreement explicit |
| 3 / `turn213search2` | [Market Data Commercial Use Addendum](https://www.marketdata.app/terms/commercial-use-addendum/) | provider addendum | `U-MARKETDATA-TERMS` | `IN-S`; different permitted-use and audit-material exception; same upstream not independent | Page states Last Updated 26 October 2025; mutable |
| 4 / `turn213search3` | [Market Data Redistribution Policy](https://www.marketdata.app/docs/account/data-policies/data-redistribution/) | provider policy | `U-MARKETDATA-TERMS` | `EX-DUP`; reinforces personal-license redistribution boundary from same provider | Mutable docs |
| 5 / `turn213search4` | [Market Data CORS Policy](https://www.marketdata.app/docs/api/cors/) | provider policy | `U-MARKETDATA-TERMS` | `EX-DUP`; browser access does not expand license; same upstream | Mutable docs |
| 6 / `turn213search5` | [MetaTrader Terms of Use](https://www.metatrader.com/en/about/terms) | provider terms | `U-METATRADER-TERMS` | `IN-S`; personal/display-only and termination example, provider-specific | Mutable live terms; no visible fixed version |
| 7 / `turn213search6` | [Massive Market Data Terms of Service](https://massive.com/legal/market-data-terms-of-service) | provider terms | `U-MASSIVE-TERMS` | `IN-S`; current personal/non-business license boundary | Page states Last Updated August 28, 2025; mutable |
| 8 / `turn213search7` | [OKX API Agreement](https://www.okx.com/en-us/help/okx-api-agreement) | provider terms | `U-OKX-API-TERMS` | `IN-S`; own-account/internal-use and redistribution example, but crypto/provider scope | Mutable agreement |
| 9 / `turn213search8` | [Followme Market Data Policy](https://www.followme.com/policies/trading-and-risk-disclosure/market-data-policy) | provider policy | `U-FOLLOWME-TERMS` | `EX-DUP`; visible effective date was after the retrieval date, so not current operative evidence | Future-effective policy as shown by result |
| 10 / `turn213search12` | [CME DS-45 Market Data License Agreement Updates — June 2026](https://www.cmegroup.com/market-data/files/market-data-license-agreement-updates-june-2026.pdf) | official venue license update | `U-CME-LICENSE` | `IN-S`; license-scoped purge obligation and exceptions; exact-byte download failed and receipt retained | Versioned June 2026 update; no local content snapshot |
| 11 / `turn213search9` | [London Stock Exchange Pricing and Policies](https://www.londonstockexchange.com/equities-trading/market-data/pricing-and-policies) | official venue policy landing page | `U-LSE-LICENSE` | `IN-S`; current licensing portal locator only; no visible operative terms in result | Mutable landing page |
| 12 / `turn213search10` | [Market Data Plan Limits](https://www.marketdata.app/docs/account/plan-limits/) | provider policy | `U-MARKETDATA-TERMS` | `EX-DUP`; quota mechanics do not add license-state semantics | Mutable same-provider docs |
| 13 / `turn213search11` | [Foreclosure Data Hub Commercial Data License Terms](https://www.foreclosuredatahub.com/data-licensing/terms) | unrelated data-provider terms | `U-FORECLOSURE-DATA-TERMS` | `EX-SCOPE`; not market data despite retention contrast | Mutable terms summary |
| 14 / `turn213search13` | [marketdata.ai Terms and Conditions](https://marketdata.ai/downloads/terms) | generic SaaS terms | `U-MARKETDATA-AI-TERMS` | `EX-SCOPE`; visible excerpt did not establish the selected market-data license boundary | Mutable terms |
| 15 / `turn213search14` | [CB Insights Master Subscription Agreement](https://cbinsights.pactsafe.io/versions/642328c60f244cdf00243faf.pdf) | commercial data agreement | `U-CBINSIGHTS-MSA` | `EX-SCOPE`; broader licensed-material agreement, not selected equity market-data provider | Versioned Pactsafe PDF locator |
| 16 / `turn213academia15` | [Configurable Per-Query Data Minimization for Privacy-Compliant Web APIs](https://arxiv.org/abs/2203.09903) | preprint | `U-API-DATA-MINIMIZATION` | `EX-NOISE`; privacy data minimization, not market-data licensing | Versioned arXiv record |
| 17 / `turn213academia16` | [A Theory of Pricing Private Data](https://arxiv.org/abs/1208.5258) | preprint | `U-PRIVATE-DATA-PRICING` | `EX-NOISE`; economic theory of private data | Versioned arXiv record |

## Accounting summary

- Query IDs executed: `R8-RS03-D1`, `R8-RS03-D2`, `R8-RS03-S1`, `R8-RS03-S2`, `R8-RS03-S3`
- Exact-query search calls: one per query ID
- Additional or rewritten search queries: none
- Visible result sets recorded: all rows visibly returned by the tool, in backend presentation order
- Same-upstream duplicates: retained in the ledger but never counted as independent evidence
- Truncated backend result set: no truncation marker was shown by the search tool for these five calls
