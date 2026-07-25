# R8 / RS-03 S2 delta record

- Query: `R8-RS03-S2`
- Exact query: `counterexample adjusted historical price lookahead corporate action backtest`
- Search-call window UTC: `2026-07-25T16:22:00Z` → `2026-07-25T16:22:12Z`
- Delta classified at UTC: `2026-07-25T16:22:42Z`
- Entailment status: author assessment only; no independent reviewer verdict is claimed.

## Atomic claim RS03-R8-S2-C01

- topic_id: `RS-03`
- claim_text: A historical price series back-adjusted using splits, dividends, or other actions that occurred after a simulated decision can leak future information into price-level and derived-feature decisions. The same historical date can therefore have a raw-as-traded value, a point-in-time-adjusted value, and a latest-back-adjusted value with different admissibility.
- impact: high
- evidence_cluster_ids: `U-DB-SEVEN-SINS`, `U-PIT-BACKTEST-2026`, supporting provider illustration `U-KIBOT-ADJUSTMENT`
- source_snapshot_ids:
  - `RS03-SNAP-DB-SEVEN-SINS` (bytes/hash pending)
  - `RS03-SNAP-PIT-BACKTEST-2026` (bytes/hash pending)
  - `RS03-SNAP-KIBOT-ADJUSTMENT` (bytes/hash pending; optional supporting snapshot)
- source_ranges:
  - Deutsche Bank, *Seven Sins of Quantitative Investing*, PDF pages 11–13, extracted lines 551–644
  - *Point-in-Time Backtesting of Momentum-Trend Equity Strategies*, preprint v1, PDF pages 5–6, extracted lines 193–245; the retrieved preprint labels itself `NOT PEER-REVIEWED`
  - Kibot provider documentation, extracted lines 8–26 and 41–67
- author_entailment: entailed for the mechanism; the contract consequence is a design inference
- limitations: The 2026 preprint is not peer-reviewed in the retrieved PDF. Deutsche Bank's worked strategy concerns price-level selection, so the empirical magnitude cannot be generalized to every strategy. Kibot is a provider description, not independent validation.
- decision_effect: A price field must carry an explicit basis and adjustment cutoff. Latest-back-adjusted values are ineligible for reconstructing a decision unless the full adjustment set was already available by that decision.

## High-impact delta RS03-R8-S2-DELTA-01

- class: contract / risk gate / high impact
- relationship to S1: S1 separated historical observation from latest restatement; S2 identifies future corporate-action back-adjustment as a concrete path that can violate that boundary even when every price row has an old event date.
- delta:
  - Require `price_basis` with at least `raw_as_traded`, `pit_adjusted`, and `latest_back_adjusted`.
  - Require `adjustment_cutoff_time` and exact corporate-action snapshot lineage for every adjusted series.
  - A decision-time feature may use `raw_as_traded` plus actions available by the decision, or a provider-proven `pit_adjusted` series; `latest_back_adjusted` fails the no-future-information gate.
  - Reject mixed-basis formulas such as adjusted price divided by unadjusted price or shares unless an explicit, tested transformation puts both operands on one basis.
- executable landing:
  - provider-neutral schema and fail-closed eligibility gate;
  - mutation test that adds a future split and proves the prior decision feature/hash is unchanged;
  - differential gold fixture for raw, PIT-adjusted, and latest-back-adjusted views.

## Stability effect

- New high-impact failure class: yes — future corporate actions can alter old price rows and therefore old signals without changing the row's market date.
- Decision reversal: no — this strengthens provider-neutral PIT and raw/adjusted separation.
- Open critical or major contradiction: none identified from S2.
- Stability clock: reset at S2; S3 is the only remaining reserved query. If S3 adds another high-impact delta, the preregistered passing rule cannot be satisfied in this round.

