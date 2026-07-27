# Probe run log

Run date: 2026-07-27

## Inputs

- Public restaurant homepage and menu page;
- public customer discussion about menu-access friction;
- public restaurant-owner discussion about marketing attribution uncertainty;
- moderation context showing that an apparent restaurant-owner request may be promotional spam;
- the two independent first-principle records in the workspace.

## Decisions

- The suspicious menu-site request was retained as a source-authenticity warning and was not used as owner-demand proof.
- The target website inconsistency was recorded as a latent indicator, not as evidence of owner dissatisfaction or willingness to pay.
- The Probe is limited to a local static preview and factual audit.
- No invented phone number, address, opening time, menu freshness, owner identity, performance benefit, or price is used.

## Outputs

- `audit.md`
- `offer-draft.md`
- `preview/index.html`
- `preview/screenshots/desktop.png`
- `preview/screenshots/mobile.png`
- input-bound `probe-5d37e36e25ea-manifest.json` and matching task contract

## Current result

- Workspace validation: `VALID`
- Market stage: `hypothesis`
- Fulfillment stage: `prototype`
- External communication: `not_authorized`
- Financial and contractual actions: `not_authorized`

The local preview demonstrates production capability only. It contributes no market evidence until an authorized decision-maker actually sees the Offer and produces a recorded external event.

The preview was rendered successfully with Chromium in a desktop viewport and a narrow viewport. The screenshots are retained beside the preview for visual verification.

The first pre-binding Harness draft was moved under `superseded/pre-input-binding/` after the source set expanded. The current Harness filename is derived from a digest of the exact input records, so later evidence changes create a new identity instead of silently changing an old run.
