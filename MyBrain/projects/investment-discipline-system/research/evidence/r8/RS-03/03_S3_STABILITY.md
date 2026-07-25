# R8 / RS-03 S3 stability record

- Query: `R8-RS03-S3`
- Exact query: `market data license personal use cache retention termination API terms`
- Search-call window UTC: `2026-07-25T16:23:12Z` → `2026-07-25T16:23:22Z`
- Stability classified at UTC: `2026-07-25T16:24:24Z`
- Entailment status: author assessment only; no independent reviewer verdict is claimed.

## Atomic claim RS03-R8-S3-C01

- topic_id: `RS-03`
- claim_text: Market-data rights are scoped by provider, licensor, plan or addendum, user classification, permitted purpose, redistribution boundary, term, and termination effect. Personal use or technical API access does not imply a right to redistribute, retain, or continue using cached data after termination.
- impact: high, but not a new failure class in this round
- evidence_cluster_ids: `U-MARKETDATA-TERMS`, `U-CME-LICENSE`, current-candidate boundary `U-TIINGO`
- source_snapshot_ids:
  - `RS03-SNAP-MARKETDATA-TERMS` (bytes/hash pending)
  - `RS03-SNAP-CME-DS45-2026` (bytes/hash pending; supporting counterexample)
  - `RS03-SNAP-TIINGO-TOS-2026-07-18` (bytes/hash pending)
- source_ranges:
  - Market Data Terms, extracted lines 131–149 and 224–228
  - CME DS-45 June 2026 update, PDF pages 6–7, extracted lines 284–318
  - Tiingo Terms of Use, extracted lines 0–20, 141–144, and 213–225
- author_entailment: entailed for the named terms; no legal interpretation beyond the visible text is claimed
- limitations: These terms do not determine Javen's future account-specific agreement, supplemental terms, exchange entitlements, or legal obligations. This report is not legal advice. Tiingo's public terms do not visibly grant post-termination cache retention, but absence of an express grant is not an express deletion duty.
- decision_effect: Preserve the existing fail-closed license state machine `unknown → allowed/restricted/expired/revoked`, bound to exact terms bytes, provider/plan/purpose, effective or last-updated date, permitted storage/use/redistribution, termination action, and re-confirmation trigger.

## Current candidate boundary receipt

- Tiingo public Terms of Use showed `Version 1`, `Effective Date: January 16th, 2022`, and `Last Updated Date: July 18th, 2026` at retrieval. The same page permits individual versus commercial plan selection, restricts API data to internal consumption, and makes continued use terminate with the service. It did not visibly settle post-termination local cache retention.
- Tiingo's public EOD page states that U.S. equity prices are generally available in the evening, may receive later exchange corrections, exposes raw and adjusted fields, maps `divCash` to ex-date, and exposes `splitFactor`. This is public documentation only; no token or private capability test was performed.
- Alpaca's current public Paper Trading page says Paper Only accounts are entitled to IEX market data, lists simulation omissions including dividends, and gives explicit fill assumptions. No account, key, endpoint, order, or private entitlement was tested.
- Observer boundary remains unchanged: external paper state is read-only evidence for reconciliation and must never overwrite the local authoritative ledger.

## No-delta adjudication

- New high-impact failure class: no.
- Decision reversal: no.
- Open critical or major contradiction: none.
- Reason: The search results and current-candidate direct receipts instantiate the already frozen R7/R8 license-state design: rights differ by provider/plan/purpose; cache retention cannot be inferred; termination can require use cessation or deletion; terms can change and must be re-confirmed. They do not require a new architecture component, contract discriminator, or test class beyond the existing license record/state machine and exact-byte revalidation gate.
- Stability result: pass for the preregistered stability rule. S3 occurred after the last high-impact delta at S2 and added no new high-impact failure class, decision reversal, or open critical/major contradiction.
- Topic closure result is not implied: independent per-claim entailment review and evidence-commit ancestry remain separate closure predicates.

