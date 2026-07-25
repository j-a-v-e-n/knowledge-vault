# R8-RS05-D2 search receipt

- query_id: `R8-RS05-D2`
- exact_query: `site:cli.github.com/manual gh attestation verify signer workflow source digest predicate`
- search_tool_call_count: `1`
- search_tool: `web.search_query`
- response_length: `long`
- started_at_utc: `2026-07-25T16:18:12Z`
- completed_at_utc: `2026-07-25T16:18:21Z`
- preregistration_commit_utc: `2026-07-25T16:13:44Z`
- temporal_check: `pass`
- visible_result_count: `12`
- visible_backend_order: `0..11`
- backend_completeness_caveat: The complete result set visible in the single tool response is recorded below. The backend exposed no total-hit count or continuation cursor, and each result was subject to the tool's visible summary/word limit; no latent-corpus completeness is claimed.

## Complete visible result set and screening

### Result 0

- result_rank_or_backend_order: `0`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_attestation_verify`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: The manual defines an attestation as a workflow actor's claim about an artifact subject. Verification validates actor identity and expected predicate type. Actor identity contains repository/owner and signer workflow; precision can be increased with signer workflow or certificate identity. Flags visible in the result include certificate identity, OIDC issuer, self-hosted-runner denial, artifact digest algorithm, predicate type, repository, signer digest/repository/workflow, source digest/ref, bundle, and JSON output. The manual warns that only the certificate and verified timestamps are non-manipulable by the originating workflow; `statement.predicate` can be falsified from a compromised workflow context.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ATTEST-CURRENT`
- screening_decision: `include_decisive`
- screening_reason: Primary current verification-policy specification and direct counterevidence against treating predicate content as semantic proof.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval; no CLI release version encoded in URL`

### Result 1

- result_rank_or_backend_order: `1`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_release_verify`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Describes release-level attestation verification and JSON output for release assets.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-RELEASE-ATTEST`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Release attestation semantics are not the preregistered workflow provenance verification target.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 2

- result_rank_or_backend_order: `2`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_help_reference`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: 2 weeks ago`
- visible_result: Aggregate CLI reference repeats the `gh attestation verify` flags, including identity, issuer, runner, predicate, signer, and source constraints.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ATTEST-CURRENT`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: Generated aggregate reference duplicates result 0 and is less focused.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 3

- result_rank_or_backend_order: `3`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_attestation_download`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: yesterday`
- visible_result: Public-preview command for downloading attestations to digest-named JSON/JSONL files, requiring artifact/image plus owner or repository and optionally predicate type.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Supports saving the exact attestation bundle for a durable receipt; public-preview status is a drift warning.
- revision_or_supersession_state: `mutable_live_manual; public_preview_subject_to_change`

### Result 4

- result_rank_or_backend_order: `4`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_attestation`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: yesterday`
- visible_result: Parent navigation page listing download, trusted-root, and verify.
- source_class: `current_official_github_cli_manual_index`
- upstream_cluster_id: `GH-CLI-ATTEST-CURRENT`
- screening_decision: `exclude_navigation_only`
- screening_reason: No additional verification semantics.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 5

- result_rank_or_backend_order: `5`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_attestation_trusted-root`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: 2 days ago`
- visible_result: Describes outputting trusted-root JSONL for online/offline verification and custom TUF root/repository inputs.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Supports explicit trust-root capture for offline reproducibility.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 6

- result_rank_or_backend_order: `6`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_release_verify-asset`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Verifies that a release asset digest matches an attestation associated with a release.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-RELEASE-ATTEST`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Release-specific and not the workflow provenance policy under review.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 7

- result_rank_or_backend_order: `7`
- url_or_fixed_locator: `https://cli.github.com/manual/gh`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Root CLI navigation listing `gh attestation` and other commands.
- source_class: `current_official_github_cli_manual_index`
- upstream_cluster_id: `GH-CLI-ROOT`
- screening_decision: `exclude_navigation_only`
- screening_reason: No specific attestation policy content.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 8

- result_rank_or_backend_order: `8`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_run_view`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Workflow-run viewing documentation and log-association limitations.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ACTIONS-OPS`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Operational run inspection is not attestation identity or predicate verification.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 9

- result_rank_or_backend_order: `9`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_extension`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Extension management and warning that extensions are not verified, signed, or endorsed.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-EXTENSIONS`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Generic extension provenance warning; not evidence about GitHub artifact attestation verification.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 10

- result_rank_or_backend_order: `10`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_workflow_run`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: today`
- visible_result: Describes triggering a `workflow_dispatch` workflow.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ACTIONS-OPS`
- screening_decision: `exclude_out_of_scope_and_forbidden_execution`
- screening_reason: Does not address verification policy, and R8 explicitly forbids this agent from running or modifying workflows.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

### Result 11

- result_rank_or_backend_order: `11`
- url_or_fixed_locator: `https://cli.github.com/manual/gh_workflow_list`
- title: `GitHub CLI | Take GitHub to the command line`
- visible_metadata: `Crawled: 2 days ago`
- visible_result: Visible response only showed the workflow-list heading.
- source_class: `current_official_github_cli_manual`
- upstream_cluster_id: `GH-CLI-ACTIONS-OPS`
- screening_decision: `exclude_out_of_scope`
- screening_reason: No attestation verification content in the visible result.
- revision_or_supersession_state: `mutable_live_manual_current_at_retrieval`

