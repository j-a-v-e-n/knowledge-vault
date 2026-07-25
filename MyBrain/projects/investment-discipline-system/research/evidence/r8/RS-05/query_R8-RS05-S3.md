# R8-RS05-S3 search receipt

- query_id: `R8-RS05-S3`
- exact_query: `GitHub artifact attestation user issue verification policy limitation`
- search_tool_call_count: `1`
- search_tool: `web.search_query`
- response_length: `long`
- started_at_utc: `2026-07-25T16:25:45Z`
- completed_at_utc: `2026-07-25T16:25:53Z`
- preregistration_commit_utc: `2026-07-25T16:13:44Z`
- temporal_check: `pass`
- visible_result_count: `11`
- visible_backend_order: `0..10`
- backend_completeness_caveat: The complete visible set is recorded below. No total-hit count or continuation cursor was exposed; summaries were tool-bounded and do not establish latent-corpus completeness.

## Complete visible result set and screening

### Result 0

- result_rank_or_backend_order: `0`
- url_or_fixed_locator: `https://docs.github.com/en/actions/concepts/security/artifact-attestations`
- title: `Artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Current official overview repeating that attestations are cryptographically signed provenance claims and consumers must define/evaluate policy and make their own risk decision.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_decisive_existing_cluster`
- screening_reason: Confirms the core boundary but is the same upstream and source as D1 result 0.
- revision_or_supersession_state: `mutable_live_current_at_retrieval`

### Result 1

- result_rank_or_backend_order: `1`
- url_or_fixed_locator: `https://github.blog/changelog/2025-02-18-recent-improvements-to-artifact-attestations/`
- title: `Recent improvements to Artifact Attestations - GitHub Changelog`
- visible_metadata: `Published: 1.4 years ago; Crawled: today`
- visible_result: Product changelog saying verification now defaults to build provenance and noting changes driven by user feedback.
- source_class: `official_github_product_changelog`
- upstream_cluster_id: `GH-ATTEST-CHANGELOG`
- screening_decision: `include_revision_context`
- screening_reason: Demonstrates evolving defaults and therefore drift risk, but does not establish an independent limitation.
- revision_or_supersession_state: `dated_2025-02-18_product_change`

### Result 2

- result_rank_or_backend_order: `2`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations`
- title: `Managing the lifecycle of artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Attestations can be deleted; deletion can prevent consumers from finding/using an attestation.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting_existing_cluster`
- screening_reason: Repeats D1 lifecycle evidence; no new failure class.
- revision_or_supersession_state: `mutable_live_current_at_retrieval`

### Result 3

- result_rank_or_backend_order: `3`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations`
- title: `Using artifact attestations to establish provenance for builds - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: Current usage and CLI verification guide, including plan limitation for private/internal repositories and JSON predicate inspection.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting_existing_cluster`
- screening_reason: Operational context only; no independent issue.
- revision_or_supersession_state: `mutable_live_current_at_retrieval`

### Result 4

- result_rank_or_backend_order: `4`
- url_or_fixed_locator: `https://docs.github.com/en/rest/users/attestations`
- title: `REST API endpoints for artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: User-scoped creation/list/delete API and predicate-type filtering.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: Duplicates D1 REST/lifecycle evidence.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; example API version 2026-03-10`

### Result 5

- result_rank_or_backend_order: `5`
- url_or_fixed_locator: `https://docs.github.com/en/rest/orgs/attestations`
- title: `REST API endpoints for artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: Organization-scoped creation/list/delete API, predicate filtering, and identity-verification warning.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: Same official REST cluster and no independent limitation.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; example API version 2026-03-10`

### Result 6

- result_rank_or_backend_order: `6`
- url_or_fixed_locator: `https://docs.github.com/en/rest/repos/attestations`
- title: `REST API endpoints for repository attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Repository-scoped attestation API; the visible result included a large example Sigstore bundle with DSSE payload, certificate, subject digest, source repository/ref, workflow, hosted-runner, and predicate fields.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `include_supporting_existing_cluster`
- screening_reason: Concrete schema example, but example values are illustrative and not this project's execution receipt.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; example API version 2026-03-10`

### Result 7

- result_rank_or_backend_order: `7`
- url_or_fixed_locator: `https://github.com/actions/attest`
- title: `GitHub - actions/attest: Action for generating attestations for workflow artifacts · GitHub`
- visible_metadata: `Crawled: last month`
- visible_result: Official action repository describing SLSA and custom predicates, public/private plan boundaries, and CLI verification.
- source_class: `official_github_action_repository`
- upstream_cluster_id: `GH-ACTIONS-ATTEST`
- screening_decision: `include_supporting`
- screening_reason: Current implementation source, but default branch is mutable and a future workflow must pin a full commit.
- revision_or_supersession_state: `mutable_default_branch; exact commit pending`

### Result 8

- result_rank_or_backend_order: `8`
- url_or_fixed_locator: `https://github.com/github/artifact-attestations-opa-provider`
- title: `GitHub - github/artifact-attestations-opa-provider: OPA Gatekeeper provider for GitHub Artifact Attestations · GitHub`
- visible_metadata: `Crawled: last month`
- visible_result: GitHub-owned OPA provider that fetches/verifies cryptographic bundles and passes verified data to OPA for policy evaluation.
- source_class: `official_github_policy_provider_repository`
- upstream_cluster_id: `GH-ATTEST-OPA-PROVIDER`
- screening_decision: `include_supporting`
- screening_reason: Reinforces separation between cryptographic verification and downstream policy evaluation; not independent counterevidence.
- revision_or_supersession_state: `mutable_default_branch; exact commit not selected`

### Result 9

- result_rank_or_backend_order: `9`
- url_or_fixed_locator: `https://github.com/cli/cli/issues/11803`
- title: ``gh attestation verify` should be able to work without token / authentication · Issue #11803 · cli/cli · GitHub`
- visible_metadata: `Published: 10 months ago; Crawled: 2 months ago`
- visible_result: An external user reports that `gh attestation verify` requires a token even for the desired public-repository use case, creating unwanted token exposure when verification is nested in a larger codebase. The issue is open and labeled enhancement/gh-attestation, with no assignee, milestone, or linked development visible.
- source_class: `independent_user_implementation_issue`
- upstream_cluster_id: `GH-CLI-ISSUE-11803`
- screening_decision: `include_required_independent_issue`
- screening_reason: Meets the required independent issue class and adds a concrete least-privilege/operational-burden probe. It is a user report, not a maintainer-confirmed universal defect.
- revision_or_supersession_state: `open_as_of_2026-07-25_retrieval; opened_2025-09-24; current_behavior_not_locally_reproduced`

### Result 10

- result_rank_or_backend_order: `10`
- url_or_fixed_locator: `https://github.com/cli/cli/issues/9602`
- title: `add gh attestation verify options --ref and --commit · Issue #9602 · cli/cli · GitHub`
- visible_metadata: `Published: 1.9 years ago; Crawled: 2 months ago`
- visible_result: User requested direct source ref/commit policy flags because repository/workflow checks did not easily prove a precise approved source revision. The issue is closed with no visible development link. Current D2 documentation now exposes `--source-ref`, `--source-digest`, and `--signer-digest`.
- source_class: `historical_independent_user_issue`
- upstream_cluster_id: `GH-CLI-ISSUE-9602`
- screening_decision: `include_revision_and_supersession_receipt`
- screening_reason: Useful history of a real policy usability gap, but current flags supersede the request; it must not be presented as an open current limitation.
- revision_or_supersession_state: `closed; functionally_superseded_by_current_documented_flags`

## Post-query delta and stability assessment

- assessed_after_query_at_utc: `2026-07-25T16:25:53Z`
- new_high_impact_failure_class: `no`
- decision_reversal: `no`
- open_critical_or_major_contradiction: `none`
- new_major_operational_probe: Automatic bundle lookup/download through `gh` may require authentication and can encounter unauthenticated API rate limits. The saved issue thread also clarifies that `gh attestation verify --bundle ...` can verify an already-saved bundle without GitHub authentication. A future machine gate should therefore preserve the bundle, isolate any authenticated fetch, minimize token scope/lifetime, and record the exact installed CLI behavior. This user report and thread are not promoted to a universal mechanism claim.
- last_high_impact_delta: `R8-RS05-DELTA-S1-VALID-ATTESTATION-COMPROMISED-PIPELINE`
- later_reserved_queries_after_last_high_impact_delta: `R8-RS05-S2`, `R8-RS05-S3`
- later_query_outcomes: Both yielded no new high-impact failure class, no decision reversal, and no open critical/major contradiction.
- stability_passing_rule: `pass`
- final_query_added_high_impact_delta: `no`
- no_sixth_query: `enforced`
- topic_status_implication: Stability itself passes. Topic closure must still be evaluated against every other predicate; this author does not perform the required independent entailment review.

## Post-search exact issue-thread validation

- retrieval_window_utc: `2026-07-25T16:31:31Z`–`2026-07-25T16:31:32Z`
- exact_issue_bytes: `github_cli_issue_11803_2026-07-25.json`
- exact_comment_bytes: `github_cli_issue_11803_comments_2026-07-25.json`
- current_state: Issue `#11803` is open, has `18` comments in the exact API receipt, and is labeled `enhancement` and `gh-attestation`.
- qualification_from_thread: A repository contributor explains that hosted bundle fetching is the authentication-dependent operation and that local verification with an explicitly supplied bundle does not require GitHub authentication. The reporter confirms a bundle-based unauthenticated verification path and later reports rate-limit failures for unauthenticated fetching on some Actions runners.
- authority_boundary: The issue is independent user evidence for burden/failure probes. Contributor comments improve mechanism interpretation, but the thread is not a controlled incidence study and does not prove every version/environment behaves identically.
- supersession_check_for_result_10: `github_cli_issue_9602_2026-07-25.json` is `closed` with `state_reason: completed`; its exact comment receipt records that a CLI contributor linked the shipped implementation. The current D2 manual and local `gh 2.95.0` expose `--source-ref`, `--source-digest`, and `--signer-digest`, so the old request is not counted as a current missing-policy flag.
