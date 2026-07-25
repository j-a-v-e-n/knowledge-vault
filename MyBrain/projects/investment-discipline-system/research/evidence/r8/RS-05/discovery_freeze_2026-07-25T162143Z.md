# RS-05 discovery freeze

- freeze_id: `R8-RS05-DISCOVERY-FREEZE-1`
- frozen_at_utc: `2026-07-25T16:21:43Z`
- query_inputs_complete: `R8-RS05-D1`, then `R8-RS05-D2`
- stability_queries_executed_before_freeze: `none`
- author_role: `RS-05 research author; not independent entailment reviewer`

## Frozen atomic claims

### R8-RS05-C01 — Verification is a conjunctive policy check

- topic_id: `RS-05`
- claim_text: A positive `github_issued_workflow_provenance` receipt is decision-relevant only when the verifier checks the artifact subject digest and constrains the expected repository, certificate/OIDC issuer, signer workflow identity, signer workflow digest, source repository digest, predicate type, and hosted-runner policy; a bare successful lookup or `--repo`-only verification is insufficient for this project's intended policy.
- impact: `decisive`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `pending exact-byte snapshots`
- source_ranges: D1 result 0 verification section; D1 result 3 verification section; D2 result 0 Understanding Verification, Additional Policy Enforcement, and Options.
- author_entailment: `supported as a project policy composition; individual flags and identity semantics are directly documented, while the exact conjunction is the author's conservative policy decision`
- limitations: The discovery results establish available checks, not a real receipt. Certificate identity/SAN and signer workflow are overlapping ways to narrow identity and must be frozen to exact expected values at the machine gate. Repository and signer repository can differ for reusable workflows.
- decision_effect: Preserve the R7 term `github_issued_workflow_provenance`; keep state `designed_not_observed` until a real artifact, bundle, and exact positive/negative policy receipts exist.

### R8-RS05-C02 — Workflow-controlled predicate is not semantic proof

- topic_id: `RS-05`
- claim_text: GitHub attestation verification can bind a subject digest to GitHub-issued certificate identity and timestamps, but a workflow execution context can manipulate `statement.predicate`; therefore the attestation cannot prove the truth of workflow-reported predicate fields, command correctness, review quality, or investment-design semantics.
- impact: `decisive_counterevidence`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `pending exact-byte snapshots`
- source_ranges: D1 result 0 Verifying artifact attestations warning; D2 result 0 Additional Policy Enforcement.
- author_entailment: `directly supported for the predicate-control and non-security-guarantee boundary; semantic-correctness exclusion follows conservatively`
- limitations: This does not claim every workflow is malicious or every predicate is false. It limits what the receipt alone entails.
- decision_effect: Do not rename the layer as an independent executor, semantic verifier, safe isolation, or cryptographic reviewer.

### R8-RS05-C03 — Signer identity must follow the actual signing workflow

- topic_id: `RS-05`
- claim_text: If provenance is signed from a reusable workflow, verification must identify the reusable signer workflow/repository rather than assume the caller workflow is the signer.
- impact: `major`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `pending exact-byte snapshots`
- source_ranges: D1 result 3 Step 2; D2 result 0 Understanding Verification.
- author_entailment: `directly supported`
- limitations: This is identity routing, not evidence that the reusable workflow is controlled by an independent principal.
- decision_effect: The future policy fixture must separately freeze caller repository/source digest and signer repository/workflow/digest.

### R8-RS05-C04 — Durable verification needs locally preserved inputs

- topic_id: `RS-05`
- claim_text: A durable machine-verification receipt should preserve exact artifact bytes, attestation bundle bytes, trusted-root bytes or locator/version context, verifier version, policy inputs, and JSON output because hosted attestations can be deleted and trust material can rotate or become stale.
- impact: `major`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `pending exact-byte snapshots`
- source_ranges: D1 result 1 lifecycle section; D1 result 10 offline-verification sections; D2 results 3 and 5.
- author_entailment: `directly supported for deletion/download/trust-root mechanics; the evidence-package conjunction is a conservative reproducibility decision`
- limitations: A saved trusted root is not permanent revocation knowledge, and saved bytes do not establish semantic correctness.
- decision_effect: Add a future machine-gate evidence package requirement; do not perform that gate in this research task.

### R8-RS05-C05 — Git and human/Codex labels remain downgraded

- topic_id: `RS-05`
- claim_text: Nothing in D1 or D2 provides evidence to upgrade Git beyond `content_snapshot_anchor`, Codex review beyond `platform_observable_separate_thread_review`, or approval beyond `human_final_decision_by_Javen`.
- impact: `decisive_scope_guard`
- evidence_cluster_ids: `GH-DOC-ATTEST-CURRENT`, `GH-CLI-ATTEST-CURRENT`
- source_snapshot_ids: `none; absence-of-upgrade conclusion within frozen discovery set`
- source_ranges: Complete D1 and D2 visible result sets.
- author_entailment: `bounded absence statement limited to the two preregistered discovery queries`
- limitations: Not a universal claim about all Git, Codex, or organizational controls.
- decision_effect: Preserve all four R7 downgraded terms without upgrade.

## Frozen architecture / decision deltas

### High-impact deltas

1. `none`. D1/D2 confirm R7's core trust model and do not justify a decision reversal or a new high-impact failure class.

### Major executable refinements (not high-impact deltas under the preregistered definition)

1. Future machine policy must model `caller/source` and `signer workflow` as separate identities when reusable workflows are used.
2. Future evidence package must save artifact, attestation bundle, verifier/trusted-root context, exact policy inputs, and JSON positive/negative receipts.
3. Policy evaluation must not consume workflow-controlled predicate values as authoritative semantic facts merely because signature verification passed.

## Frozen candidate state entering stability queries

- Git: `content_snapshot_anchor`; unsigned/non-identity semantics unchanged.
- GitHub: `github_issued_workflow_provenance`; `designed_not_observed`.
- Codex: `platform_observable_separate_thread_review`; no safe-isolation or cryptographic-reviewer claim.
- Final decision: `human_final_decision_by_Javen`.
- discovery_open_critical_or_major_contradiction: `none`
- discovery_last_high_impact_delta: `none in R8 discovery; inherited R7 downgrade remains the candidate`
- stability_rule_implication: S1, S2, and S3 must now actively seek a new high-impact failure class, decision reversal, or open critical/major contradiction. If S3 creates the last such delta, the result must be `bounded_incomplete` with no sixth query.
