# R8-RS05-D1 search receipt

- query_id: `R8-RS05-D1`
- exact_query: `site:docs.github.com artifact attestations verification policy workflow identity source digest`
- search_tool_call_count: `1`
- search_tool: `web.search_query`
- response_length: `long`
- started_at_utc: `2026-07-25T16:17:56Z`
- completed_at_utc: `2026-07-25T16:18:05Z`
- preregistration_commit_utc: `2026-07-25T16:13:44Z`
- temporal_check: `pass`
- visible_result_count: `14`
- visible_backend_order: `0..13`
- backend_completeness_caveat: The complete result set visible in the single tool response is recorded below. The backend exposed no total-hit count or continuation cursor, and each search result was subject to the tool's visible summary/word limit; therefore this is not a claim that the search engine's latent corpus or all matching hits were exhausted.

## Complete visible result set and screening

### Result 0

- result_rank_or_backend_order: `0`
- url_or_fixed_locator: `https://docs.github.com/en/actions/concepts/security/artifact-attestations`
- title: `Artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: GitHub says artifact attestations link an artifact to the associated workflow, repository, organization, environment, commit SHA, triggering event, and other OIDC information. The result also says verification must be used, consumers must define and evaluate policy, and an attestation is not a guarantee that an artifact is secure.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_decisive`
- screening_reason: Directly addresses provenance scope, verification policy, workflow/source linkage, and the non-semantic-security boundary.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 1

- result_rank_or_backend_order: `1`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/manage-attestations`
- title: `Managing the lifecycle of artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: The visible result states that deleting an attestation can prevent a verification process from using the associated artifact, recommends downloading a copy before deletion, and describes predicate as the type of claim made about an artifact.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Adds a lifecycle/retrievability limitation and supports preserving the exact bundle, but does not independently establish identity-policy semantics.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 2

- result_rank_or_backend_order: `2`
- url_or_fixed_locator: `https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts`
- title: `Workflow artifacts - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Defines a workflow artifact as files produced during a workflow run, repeats that attestations associate a build with workflow, repository, commit, event, and OIDC information, and notes that deleting a workflow run deletes its artifacts.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: Relevant background but duplicates result 0's provenance description and does not add a distinct verification-policy mechanism.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 3

- result_rank_or_backend_order: `3`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating`
- title: `Using artifact attestations and reusable workflows to achieve SLSA v1 Build Level 3 - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: The visible result describes using a reusable workflow to generate attestations and says `gh attestation verify` can constrain `--signer-repo` and `--signer-workflow`; it also states that both caller and reusable workflows need attestation, contents, and OIDC permissions.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Direct support for checking signer repository/workflow identity. Its isolation wording is treated as a product configuration claim, not proof of owner-independent execution.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 4

- result_rank_or_backend_order: `4`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations`
- title: `Using artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Navigation/index page listing provenance generation, reusable-workflow guidance, admission-controller enforcement, offline verification, and lifecycle management.
- source_class: `current_official_github_documentation_index`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `exclude_navigation_only`
- screening_reason: Supplies no additional decisive semantics beyond linked child documents.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 5

- result_rank_or_backend_order: `5`
- url_or_fixed_locator: `https://docs.github.com/en/rest/orgs/attestations`
- title: `REST API endpoints for artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: The organization endpoint lists attestations by subject digest, supports a predicate-type filter, and warns that meaningful security requires cryptographic verification of signatures/timestamps and validation of signer identity.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `include_supporting`
- screening_reason: Supports subject-digest lookup and the requirement to validate signer identity, but is not the primary verification-policy specification.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; example API version 2026-03-10 shown`

### Result 6

- result_rank_or_backend_order: `6`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations`
- title: `Using artifact attestations to establish provenance for builds - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: Shows `gh attestation verify PATH ... -R ORGANIZATION/REPOSITORY` and JSON predicate inspection, plus current build-attestation usage.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Current operational verification guidance; the broader policy semantics remain in result 0 and D2 result 0.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 7

- result_rank_or_backend_order: `7`
- url_or_fixed_locator: `https://docs.github.com/en/rest/users/attestations`
- title: `REST API endpoints for artifact attestations - GitHub Docs`
- visible_metadata: `Crawled: yesterday`
- visible_result: User-scoped equivalent of result 5: list attestations by subject digest, optional predicate filter, and warning to verify signatures/timestamps and signer identity.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: Endpoint scope differs, but the verification claim duplicates result 5.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; example API version 2026-03-10 shown`

### Result 8

- result_rank_or_backend_order: `8`
- url_or_fixed_locator: `https://docs.github.com/en/enterprise-cloud%40latest/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations`
- title: `Using artifact attestations to establish provenance for builds - GitHub Enterprise Cloud Docs`
- visible_metadata: `Crawled: 4 days ago`
- visible_result: Enterprise Cloud `@latest` variant showing `actions/attest@v4`, subject path/name/digest, and required permissions.
- source_class: `current_official_github_enterprise_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `exclude_same_upstream_variant`
- screening_reason: Product-edition duplicate of result 6 and `@latest` is not a fixed revision.
- revision_or_supersession_state: `mutable_enterprise_cloud_latest_alias`

### Result 9

- result_rank_or_backend_order: `9`
- url_or_fixed_locator: `https://docs.github.com/en/rest/repos/attestations`
- title: `REST API endpoints for repository attestations - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Repository-scoped list endpoint by subject digest; repeats that signatures/timestamps must be cryptographically verified and signer identity validated.
- source_class: `current_official_github_api_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-REST`
- screening_decision: `include_supporting`
- screening_reason: Repository is the relevant lookup scope, but the endpoint does not replace full policy verification.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no fixed document version shown`

### Result 10

- result_rank_or_backend_order: `10`
- url_or_fixed_locator: `https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/verify-attestations-offline`
- title: `Verifying attestations offline - GitHub Docs`
- visible_metadata: `Crawled: today`
- visible_result: Describes downloading a bundle and trusted roots, importing artifact/bundle/trusted-root/CLI into an offline environment, and warns that stale roots may miss revocation or later key rotation.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `include_supporting`
- screening_reason: Establishes that a durable receipt needs saved bundle and trust-root/version context, not only a live lookup.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 11

- result_rank_or_backend_order: `11`
- url_or_fixed_locator: `https://docs.github.com/en/code-security/tutorials/implement-supply-chain-best-practices/securing-builds`
- title: `Best practices for securing your build system - GitHub Docs`
- visible_metadata: `Crawled: 2 days ago`
- visible_result: Repeats that attestations include artifact signatures and links to source code/build instructions.
- source_class: `current_official_github_documentation`
- upstream_cluster_id: `GH-DOC-ATTEST-CURRENT`
- screening_decision: `exclude_same_upstream_redundant`
- screening_reason: No new policy or limitation beyond results 0, 3, 6, and 10.
- revision_or_supersession_state: `mutable_live_current_at_retrieval; no version identifier shown`

### Result 12

- result_rank_or_backend_order: `12`
- url_or_fixed_locator: `https://docs.github.com/assets/images/help/site-policy/github-privacy-statement%2807.22.20%29%28fr%29.pdf`
- title: `GitHub Privacy Statement - FR translation 2020.08.31`
- visible_metadata: `Published: last month`
- visible_result: French privacy-statement PDF matched generic words such as policy/verification.
- source_class: `search_noise_official_asset`
- upstream_cluster_id: `NOISE-GH-PDF`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Does not concern artifact attestations or provenance verification.
- revision_or_supersession_state: `historical_policy_asset; irrelevant`

### Result 13

- result_rank_or_backend_order: `13`
- url_or_fixed_locator: `https://docs.github.com/assets/images/help/site-policy/github-statement-against-modern-slavery-and-child-labor.pdf`
- title: `Microsoft Word - GitHub Statement against Modern Slavery and Child Labor - 2018.docx`
- visible_metadata: `Published: 2 months ago`
- visible_result: Corporate statement PDF matched generic policy/verification terms.
- source_class: `search_noise_official_asset`
- upstream_cluster_id: `NOISE-GH-PDF`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Does not concern artifact attestations or provenance verification.
- revision_or_supersession_state: `historical_policy_asset; irrelevant`

