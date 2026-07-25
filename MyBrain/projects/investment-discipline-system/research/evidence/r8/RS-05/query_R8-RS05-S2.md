# R8-RS05-S2 search receipt

- query_id: `R8-RS05-S2`
- exact_query: `in-toto attestation limitations omitted materials false predicate`
- search_tool_call_count: `1`
- search_tool: `web.search_query`
- response_length: `long`
- started_at_utc: `2026-07-25T16:24:06Z`
- completed_at_utc: `2026-07-25T16:24:22Z`
- preregistration_commit_utc: `2026-07-25T16:13:44Z`
- temporal_check: `pass`
- visible_result_count: `18`
- visible_backend_order: `0..17`
- backend_completeness_caveat: The complete visible set is recorded below. No total-hit count or continuation cursor was exposed, and result summaries were tool-bounded; no latent-corpus completeness is claimed.

## Complete visible result set and screening

### Result 0

- result_rank_or_backend_order: `0`
- url_or_fixed_locator: `https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md`
- title: `attestation/spec/predicates/link.md at main · in-toto/attestation · GitHub`
- visible_metadata: `Crawled: 2 months ago`
- visible_result: Link predicate v0.3 binds products through Statement subjects and can list step materials, command, byproducts, and environment. The visible schema says `command` and `materials` are optional, and environment/byproducts are opaque.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_decisive`
- screening_reason: Direct standard evidence that a valid Link predicate type does not imply command or materials completeness.
- revision_or_supersession_state: `mutable_main; predicate_version_0.3; exact release commit pending`

### Result 1

- result_rank_or_backend_order: `1`
- url_or_fixed_locator: `https://github.com/in-toto/attestation/blob/main/spec/predicates/scai.md`
- title: `attestation/spec/predicates/scai.md at main · in-toto/attestation · GitHub`
- visible_metadata: `Crawled: 2 months ago`
- visible_result: SCAI v0.3 permits optional target, conditions, evidence, and producer fields; when evidence is omitted, a consumer may choose to evaluate based on producer identity.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_supporting_counterevidence`
- screening_reason: Shows that authenticated producer identity can coexist with evidence omission; policy must not infer evidence from signature alone.
- revision_or_supersession_state: `mutable_main; predicate_version_0.3; exact release commit pending`

### Result 2

- result_rank_or_backend_order: `2`
- url_or_fixed_locator: `https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md`
- title: `attestation/spec/v1/statement.md at main · in-toto/attestation · GitHub`
- visible_metadata: `Crawled: 2 months ago`
- visible_result: Statement v1 binds subjects by digest to a predicate type. Subject matching is purely by digest; predicate is optional and unset equals empty when the type fully describes it.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_decisive`
- screening_reason: Directly separates subject/type binding from predicate-content completeness.
- revision_or_supersession_state: `mutable_main; Statement_v1; exact release commit pending`

### Result 3

- result_rank_or_backend_order: `3`
- url_or_fixed_locator: `https://github.com/in-toto/attestation`
- title: `GitHub - in-toto/attestation: in-toto Attestation Framework · GitHub`
- visible_metadata: `Crawled: last month`
- visible_result: Repository overview calls the framework still under development, lists language bindings, and shows latest release `v1.2.0` dated March 18, 2026.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_revision_receipt`
- screening_reason: Identifies the current release family and development status but carries no additional decisive limitation.
- revision_or_supersession_state: `repository_latest_release_visible_as_v1.2.0`

### Result 4

- result_rank_or_backend_order: `4`
- url_or_fixed_locator: `https://github.com/in-toto/attestation/blob/main/spec/README.md`
- title: `attestation/spec/README.md at main · in-toto/attestation · GitHub`
- visible_metadata: `Crawled: 2 months ago`
- visible_result: Framework specification overview says predicate contains arbitrary typed metadata, Statement binds subject/type, Envelope authenticates, and Bundle groups attestations; it describes tagged-release versioning and identifies latest spec as v1.2.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_supporting`
- screening_reason: Supports the layer separation and release-pinning method.
- revision_or_supersession_state: `mutable_main_reporting_latest_spec_v1.2`

### Result 5

- result_rank_or_backend_order: `5`
- url_or_fixed_locator: `https://github.com/in-toto/docs/blob/master/in-toto-spec.md`
- title: `specification/in-toto-spec.md at master · in-toto/specification · GitHub`
- visible_metadata: `Published: 3.1 years ago; Crawled: last month`
- visible_result: The original in-toto specification says expected command mismatch is warning-only because a compromised functionary key/PATH can forge it. Artifact-rule lists have implicit `ALLOW *`; an explicit final `DISALLOW *` is recommended to prevent unconsumed artifacts from passing.
- source_class: `primary_legacy_in_toto_specification`
- upstream_cluster_id: `IN-TOTO-LEGACY-SPEC`
- screening_decision: `include_decisive_counterevidence`
- screening_reason: Directly demonstrates fail-open defaults and why signed command metadata is not a security proof.
- revision_or_supersession_state: `legacy_master_locator; published_approximately_3.1_years_before_retrieval; superseded for format but relevant historical semantics`

### Result 6

- result_rank_or_backend_order: `6`
- url_or_fixed_locator: `https://github.com/in-toto/attestation/blob/main/spec/predicates/README.md`
- title: `attestation/spec/predicates/README.md at main · in-toto/attestation · GitHub`
- visible_metadata: `Crawled: today`
- visible_result: Registry of vetted predicate schemas and guidance to choose a predicate matching the use case.
- source_class: `primary_attestation_standard_repository`
- upstream_cluster_id: `IN-TOTO-ATTESTATION-SPEC`
- screening_decision: `include_supporting`
- screening_reason: Supports type-specific policy but adds no independent completeness guarantee.
- revision_or_supersession_state: `mutable_main; exact release commit pending`

### Result 7

- result_rank_or_backend_order: `7`
- url_or_fixed_locator: `https://packaging.python.org/en/latest/specifications/index-hosted-attestations/`
- title: `Index hosted attestations - Python Packaging User Guide`
- visible_metadata: `Published: last month; Crawled: 4 days ago`
- visible_result: Ecosystem specification for index-hosted in-toto Statement attestations and certificate-based publisher identity.
- source_class: `official_ecosystem_specification`
- upstream_cluster_id: `PYPA-INDEX-ATTESTATIONS`
- screening_decision: `exclude_different_implementation_scope`
- screening_reason: Does not establish GitHub/in-toto completeness or semantic correctness for this design.
- revision_or_supersession_state: `latest_mutable_packaging_spec`

### Result 8

- result_rank_or_backend_order: `8`
- url_or_fixed_locator: `https://wiki.totto.org/topics/defendable-agents/primitives/fail-closed-policy/`
- title: `Fail-Closed Policy - Thor Henning Hetland`
- visible_metadata: `Published: 2 weeks ago; Crawled: 2 days ago`
- visible_result: Personal wiki design for fail-closed agent audit policy.
- source_class: `individual_practitioner_design`
- upstream_cluster_id: `TOTTO-AGENT-DESIGN`
- screening_decision: `exclude_out_of_scope_and_low_authority`
- screening_reason: Not an in-toto/GitHub implementation or independent standard.
- revision_or_supersession_state: `recent_mutable_personal_wiki`

### Result 9

- result_rank_or_backend_order: `9`
- url_or_fixed_locator: `https://wiki.totto.org/topics/defendable-agents/primitives/trust-and-attestation/`
- title: `Trust & Attestation - Thor Henning Hetland`
- visible_metadata: `Published: 2 weeks ago; Crawled: 2 days ago`
- visible_result: Personal wiki trust-state model for agent artifacts.
- source_class: `individual_practitioner_design`
- upstream_cluster_id: `TOTTO-AGENT-DESIGN`
- screening_decision: `exclude_out_of_scope_and_low_authority`
- screening_reason: Does not bear on in-toto's specified fields or GitHub provenance.
- revision_or_supersession_state: `recent_mutable_personal_wiki`

### Result 10

- result_rank_or_backend_order: `10`
- url_or_fixed_locator: `https://safeguard.sh/resources/blog/in-toto-attestation-formats-review`
- title: `in-toto Attestation Formats Reviewed`
- visible_metadata: `Published: 2.1 years ago; Crawled: 4 days ago`
- visible_result: Vendor review of in-toto/SLSA formats and predicate routing.
- source_class: `vendor_secondary_summary`
- upstream_cluster_id: `SAFEGUARD-IN-TOTO-REVIEW`
- screening_decision: `exclude_lower_authority`
- screening_reason: Adds no independent limitation beyond primary specifications.
- revision_or_supersession_state: `historical_mutable_vendor_article`

### Result 11

- result_rank_or_backend_order: `11`
- url_or_fixed_locator: `https://docs.devguard.org/explanations/supply-chain-security/in-toto-framework/`
- title: `In-Toto Supply Chain Security Framework Documentation`
- visible_metadata: `Crawled: 2 days ago`
- visible_result: Secondary product documentation summarizing materials/products and Statement fields.
- source_class: `vendor_secondary_documentation`
- upstream_cluster_id: `DEVGUARD-IN-TOTO-SUMMARY`
- screening_decision: `exclude_lower_authority`
- screening_reason: No new evidence over the standards.
- revision_or_supersession_state: `mutable_vendor_documentation`

### Result 12

- result_rank_or_backend_order: `12`
- url_or_fixed_locator: `https://www.govinfo.gov/content/pkg/FR-1955-05-14/pdf/FR-1955-05-14.pdf`
- title: `^ \ O N A U ^ Part I tii.isnit NUMBER 95 VOLUME 20`
- visible_metadata: `Published: 8.3 years ago`
- visible_result: Historical Federal Register PDF matched generic words including material, limitations, verification, and attestation.
- source_class: `search_noise_government_pdf`
- upstream_cluster_id: `NOISE-GENERIC-ATTESTATION`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Unrelated legal use of “attestation.”
- revision_or_supersession_state: `historical_irrelevant`

### Result 13

- result_rank_or_backend_order: `13`
- url_or_fixed_locator: `https://www.diva-portal.org/smash/get/diva2%3A1959293/FULLTEXT01.pdf`
- title: `Omslag exjobb utan bild(1)`
- visible_metadata: `Published: 1.2 years ago`
- visible_result: Thesis PDF with generic in-toto attestation discussion.
- source_class: `academic_thesis`
- upstream_cluster_id: `THESIS-IN-TOTO`
- screening_decision: `exclude_lower_authority`
- screening_reason: Visible result does not show an independent counterexample or new limitation.
- revision_or_supersession_state: `dated_thesis`

### Result 14

- result_rank_or_backend_order: `14`
- url_or_fixed_locator: `https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/1998/0872.07_Bk.pdf`
- title: `THEWORKSJEREMY BENTHAM,PUBLISHED UNDER THE SUPERINTENDENCE OF`
- visible_metadata: `Published: 4 months ago`
- visible_result: Historical book PDF matched generic “attestation” and “omitted.”
- source_class: `search_noise_book`
- upstream_cluster_id: `NOISE-GENERIC-ATTESTATION`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Unrelated to software attestations.
- revision_or_supersession_state: `historical_irrelevant`

### Result 15

- result_rank_or_backend_order: `15`
- url_or_fixed_locator: `https://pnsqc.org/docs/PROP101618755-PNSQC_Clausner_2024_Final.pdf`
- title: `Enhancing Validation Through`
- visible_metadata: `Published: 1.1 years ago`
- visible_result: Conference paper overview of in-toto statements, predicates, materials, and products.
- source_class: `conference_practitioner_paper`
- upstream_cluster_id: `PNSQC-IN-TOTO`
- screening_decision: `exclude_background_only`
- screening_reason: No visible new limitation over the primary specification.
- revision_or_supersession_state: `dated_2024_paper`

### Result 16

- result_rank_or_backend_order: `16`
- url_or_fixed_locator: `https://elegalix.allahabadhighcourt.in/elegalix/WebDownloadOriginalHCJudgmentDocument.do?translatedJudgmentID=6169`
- title: `mytemplet`
- visible_metadata: `Published: 4.5 years ago`
- visible_result: Court document matched Latin phrase “in toto.”
- source_class: `search_noise_legal_document`
- upstream_cluster_id: `NOISE-IN-TOTO-PHRASE`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Not the in-toto software project.
- revision_or_supersession_state: `historical_irrelevant`

### Result 17

- result_rank_or_backend_order: `17`
- url_or_fixed_locator: `https://elegalix.allahabadhighcourt.in/elegalix/WebDownloadOriginalHCJudgmentDocument.do?translatedJudgmentID=3961`
- title: `mytemplet`
- visible_metadata: `Published: 3.5 years ago`
- visible_result: Court document matched “attestation/verification.”
- source_class: `search_noise_legal_document`
- upstream_cluster_id: `NOISE-GENERIC-ATTESTATION`
- screening_decision: `exclude_out_of_scope`
- screening_reason: Not software provenance.
- revision_or_supersession_state: `historical_irrelevant`

## Post-query delta assessment

- assessed_after_query_at_utc: `2026-07-25T16:24:22Z`
- new_high_impact_failure_class: `no`
- decision_reversal: `no`
- open_critical_or_major_contradiction: `none`
- finding: Valid subject/type authentication does not imply complete materials, a truthful command, nonempty predicate, or evidence-backed attribute. These are the preregistered omitted-materials/false-predicate limitations and confirm, rather than change, the R7 downgrade and S1 delta.
- major_policy_refinement: Future policy should fail closed on every field the project requires, reject absent/unexpected materials, avoid command metadata as a security oracle, and never treat a signature over a typed predicate as proof that the predicate is complete or semantically true.
- stability_implication: This query occurred after `R8-RS05-DELTA-S1-VALID-ATTESTATION-COMPROMISED-PIPELINE` and added no high-impact failure class or open critical/major contradiction. The reserved S3 query remains mandatory; if S3 adds a high-impact delta, no later query will exist and the topic must be `bounded_incomplete`.

