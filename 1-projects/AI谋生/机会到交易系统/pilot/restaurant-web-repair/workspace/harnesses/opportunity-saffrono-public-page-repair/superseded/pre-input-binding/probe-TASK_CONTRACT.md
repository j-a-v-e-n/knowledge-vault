# Probe Task Contract

- Opportunity: `opportunity-saffrono-public-page-repair`
- Probe: `probe-saffrono-private-preview`
- Generated: `2026-07-27T21:05:42Z`

## Objective

After seeing an accurate private before-and-after preview, the authorized decision-maker will request a concrete next step.

## Permissions

- read_public_information: `True`
- create_local_artifacts: `True`
- external_communication: `not_authorized`
- financial_actions: `not_authorized`
- contractual_commitments: `not_authorized`

## Constraints

- Preserve source wording and provenance.
- Label AI interpretation as hypothesis.
- Do not infer budget, authority, urgency, payment, or satisfaction without evidence.
- Record counterevidence and negative outcomes.
- Do not broaden the target or Offer without a new probe record.

## Stop conditions

- Stop after one local static preview and factual audit; do not publish, contact, purchase, or modify external systems.
- Stop before any external action not allowed by the probe policy.
- Stop if the artifact would require invented facts about the target.

## Required outputs

- A local, unpublished single-page preview plus a factual discrepancy list
- evidence-ready Offer draft
- run log

## Completion rule

Completion may be claimed only from the evaluation events in the manifest and their evidence locators.
