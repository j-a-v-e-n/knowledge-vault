# R8-RS05-S1 search receipt

- query_id: `R8-RS05-S1`
- exact_query: `SLSA provenance threat model maintainer platform isolation limitations`
- search_tool_call_count: `1`
- search_tool: `web.search_query`
- response_length: `long`
- started_at_utc: `2026-07-25T16:21:58Z`
- completed_at_utc: `2026-07-25T16:22:08Z`
- preregistration_commit_utc: `2026-07-25T16:13:44Z`
- temporal_check: `pass`
- visible_result_count: `21`
- visible_backend_order: `0..20`
- backend_completeness_caveat: The complete visible set is recorded below. The backend exposed no total-hit count or continuation cursor; visible summaries were tool-bounded, so no latent-corpus completeness is claimed.

## Complete visible result set and screening

### Result 0

- result_rank_or_backend_order: `0`
- url_or_fixed_locator: `https://github.com/slsa-framework/slsa-github-generator/blob/main/SPECIFICATIONS.md`
- title: `slsa-github-generator/SPECIFICATIONS.md at main · slsa-framework/slsa-github-generator · GitHub`
- visible_metadata: `Crawled: 2 months ago`
- visible_result: The threat model places GitHub, Sigstore, builder, reusable provenance generator, and verifier in the trusted computing base. It requires builder/generator isolation from maintainer interference, assumes GitHub-hosted runner behavior, and says self-hosted runners need separate trust.
- source_class: `primary_open_source_design_and_threat_model`
- upstream_cluster_id: `SLSA-GH-GENERATOR`
- screening_decision: `include_supporting`
- screening_reason: Direct implementation threat model for GitHub-hosted SLSA generation; `main` is mutable and must be pinned before use.
- revision_or_supersession_state: `mutable_main_locator; exact commit pending`

### Result 1

- result_rank_or_backend_order: `1`
- url_or_fixed_locator: `https://openssf.org/blog/2026/06/10/mini-shai-hulud-where-slsas-boundaries-fall/`
- title: `Mini Shai-Hulud: Where SLSA’s Boundaries Fall – Open Source Security Foundation`
- visible_metadata: `Published: last month; Crawled: yesterday`
- visible_result: The visible result reports compromised packages with cryptographically valid attestations that accurately named the expected hosted builder, repository, and workflow. It attributes the compromise to attacker-controlled code, shared-cache poisoning, and access to a legitimate OIDC signing identity, and says provenance records what the platform observed rather than whether the artifact was intended or uncompromised.
- source_class: `independent_foundation_incident_analysis`
- upstream_cluster_id: `OPENSSF-MINI-SHAI-HULUD`
- screening_decision: `include_decisive_counterevidence`
- screening_reason: Concrete public counterexample to treating valid expected-identity attestations as semantic correctness or uncompromised-build proof.
- revision_or_supersession_state: `dated_2026-06-10_live_article; no revision identifier shown`

### Result 2

- result_rank_or_backend_order: `2`
- url_or_fixed_locator: `https://slsa.dev/spec/v1.2/threats`
- title: `SLSA • Threats & mitigations`
- visible_metadata: `Crawled: last week`
- visible_result: The v1.2 threat model covers false provenance, owner/project compromise, cross-build influence, signing-secret theft, cache poisoning, platform-admin compromise, source/build expectation checks, and availability gaps. It states that subject digest may come from a tenant-controlled process and that consumers must compare provenance to expected source/builder values.
- source_class: `versioned_primary_standard`
- upstream_cluster_id: `SLSA-V1.2-STANDARD`
- screening_decision: `include_decisive`
- screening_reason: Required versioned provenance threat model and primary basis for isolation/trust-boundary limits.
- revision_or_supersession_state: `versioned_v1.2_current_for_this_snapshot`

### Result 3

- result_rank_or_backend_order: `3`
- url_or_fixed_locator: `https://kannkyo.github.io/slsa/spec/v1.0/verifying-systems`
- title: `SLSA • Verifying build platforms`
- visible_metadata: `Crawled: last month`
- visible_result: A mirror of v1.0 platform-verification guidance saying consumers need proof that provenance is unforgeable and builds isolated before trusting Build L3.
- source_class: `unofficial_mirror_of_versioned_standard`
- upstream_cluster_id: `SLSA-STANDARD-MIRROR`
- screening_decision: `exclude_same_upstream_mirror`
- screening_reason: Useful wording but not independent and superseded by official v1.2 material.
- revision_or_supersession_state: `historical_v1.0_mirror; superseded_for_decisive_use`

### Result 4

- result_rank_or_backend_order: `4`
- url_or_fixed_locator: `https://slsa.dev/spec/v1.0-rc2/provenance`
- title: `SLSA • Provenance`
- visible_metadata: `Crawled: today`
- visible_result: Historical provenance model defining builder ID as the transitive closure of trusted entities and provenance as a build-platform attestation.
- source_class: `historical_primary_standard`
- upstream_cluster_id: `SLSA-HISTORICAL-STANDARD`
- screening_decision: `exclude_superseded`
- screening_reason: Superseded release candidate; no need to use it over v1.2.
- revision_or_supersession_state: `v1.0-rc2_superseded`

### Result 5

- result_rank_or_backend_order: `5`
- url_or_fixed_locator: `https://slsa.dev/spec/v0.1/levels`
- title: `SLSA • Security levels`
- visible_metadata: `Crawled: today`
- visible_result: Historical level definitions and limitations, including hosted provenance, isolation, two-person review, and non-transitivity.
- source_class: `historical_primary_standard`
- upstream_cluster_id: `SLSA-HISTORICAL-STANDARD`
- screening_decision: `exclude_superseded`
- screening_reason: v0.1 is obsolete and its level model changed.
- revision_or_supersession_state: `v0.1_superseded`

### Result 6

- result_rank_or_backend_order: `6`
- url_or_fixed_locator: `https://deepwiki.com/slsa-framework/slsa/2-slsa-specification`
- title: `SLSA Specification | slsa-framework/slsa | DeepWiki`
- visible_metadata: `Crawled: 2 days ago`
- visible_result: Third-party generated summary of SLSA authenticity, isolation, and threats.
- source_class: `tertiary_generated_summary`
- upstream_cluster_id: `TERTIARY-SLSA-SUMMARY`
- screening_decision: `exclude_lower_authority`
- screening_reason: Adds no authority over the primary standard and may conflate versions.
- revision_or_supersession_state: `mutable_tertiary_summary`

### Result 7

- result_rank_or_backend_order: `7`
- url_or_fixed_locator: `https://github.com/PAIR-Systems-Inc/slsa`
- title: `GitHub - PAIR-Systems-Inc/slsa · GitHub`
- visible_metadata: `Published: 2 months ago; Crawled: 2 months ago`
- visible_result: A third-party repository summarizing SLSA Build L2/L3 and provenance/isolation concepts.
- source_class: `third_party_repository_summary`
- upstream_cluster_id: `PAIR-SLSA-FORK`
- screening_decision: `exclude_lower_authority`
- screening_reason: No evidence of standards authority or independent empirical result.
- revision_or_supersession_state: `mutable_repository_default_branch`

### Result 8

- result_rank_or_backend_order: `8`
- url_or_fixed_locator: `https://ithub.global.ssl.fastly.net/threatcl/threatcl/blob/main/docs/SLSA.md`
- title: `threatcl/docs/SLSA.md at main · threatcl/threatcl · GitHub`
- visible_metadata: `Crawled: today`
- visible_result: Project self-report claiming L2/L3-shaped controls, provenance, rulesets, and GitHub-hosted isolation.
- source_class: `project_self_report_via_mirror`
- upstream_cluster_id: `THREATCL-SELF-REPORT`
- screening_decision: `exclude_not_independently_verified`
- screening_reason: Mutable self-assertion and not evidence for this repository or GitHub's general guarantee.
- revision_or_supersession_state: `mutable_main_via_noncanonical_mirror`

### Result 9

- result_rank_or_backend_order: `9`
- url_or_fixed_locator: `https://kannkyo.github.io/slsa/spec/v1.0/whats-new`
- title: `SLSA • What's new in SLSA v1.0`
- visible_metadata: `Crawled: last week`
- visible_result: Mirror of historical change notes explaining build-platform trust and provenance expectations verification.
- source_class: `unofficial_mirror_of_historical_standard`
- upstream_cluster_id: `SLSA-STANDARD-MIRROR`
- screening_decision: `exclude_same_upstream_mirror`
- screening_reason: Historical and noncanonical; no new independent evidence.
- revision_or_supersession_state: `v1.0_historical_mirror`

### Result 10

- result_rank_or_backend_order: `10`
- url_or_fixed_locator: `https://security.googleblog.com/2021/06/introducing-slsa-end-to-end-framework.html`
- title: `Google Online Security Blog: Introducing SLSA, an End-to-End Framework for Supply Chain Integrity`
- visible_metadata: `Published: 5.1 years ago; Crawled: yesterday`
- visible_result: Original high-level introduction to SLSA levels and provenance.
- source_class: `historical_primary_practitioner_announcement`
- upstream_cluster_id: `SLSA-ORIGIN-ANNOUNCEMENT`
- screening_decision: `exclude_superseded_background`
- screening_reason: Predates current v1.2 standard and adds no current limitation beyond it.
- revision_or_supersession_state: `historical_2021`

### Result 11

- result_rank_or_backend_order: `11`
- url_or_fixed_locator: `https://marklodato.github.io/slsa/provenance/v1-rc1`
- title: `SLSA • Provenance`
- visible_metadata: `Crawled: 2 weeks ago`
- visible_result: Mirror of a release-candidate provenance document with expectation checks and assumed build-platform trust.
- source_class: `unofficial_mirror_of_historical_standard`
- upstream_cluster_id: `SLSA-STANDARD-MIRROR`
- screening_decision: `exclude_superseded_mirror`
- screening_reason: Historical release candidate and noncanonical mirror.
- revision_or_supersession_state: `v1-rc1_superseded`

### Result 12

- result_rank_or_backend_order: `12`
- url_or_fixed_locator: `https://ostif.org/wp-content/uploads/2026/01/ZLB-01-zlib_OSTIF-Audit-Public-RC1.1.pdf`
- title: `ISO/IEC 27001:2022`
- visible_metadata: `Published: 5 months ago`
- visible_result: Audit PDF with a visible mention of SLSA Build Level 3 isolation.
- source_class: `independent_audit_pdf`
- upstream_cluster_id: `OSTIF-ZLIB-AUDIT`
- screening_decision: `exclude_incidental_match`
- screening_reason: Visible result does not provide an RS-05-specific attestation counterexample or policy finding.
- revision_or_supersession_state: `dated_2026_audit_release_candidate`

### Result 13

- result_rank_or_backend_order: `13`
- url_or_fixed_locator: `https://arxiv.org/abs/2307.15895`
- title: `Auditing Frameworks Need Resource Isolation: A Systematic Study on the Super Producer Threat to System Auditing and Its Mitigation`
- visible_metadata: `Published: 3.0 years ago`
- visible_result: Academic system-level provenance/auditing isolation study.
- source_class: `academic_preprint`
- upstream_cluster_id: `SYSTEM-PROVENANCE-NODROP`
- screening_decision: `exclude_different_provenance_domain`
- screening_reason: Concerns runtime/system audit provenance, not SLSA/GitHub artifact attestations.
- revision_or_supersession_state: `historical_preprint`

### Result 14

- result_rank_or_backend_order: `14`
- url_or_fixed_locator: `https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_shai-hulud-ai-supply-chain_20260517-csa-styled.pdf`
- title: `CSAI Foundation | Cloud Security Alliance`
- visible_metadata: `Published: 2 months ago`
- visible_result: Research note about Mini Shai-Hulud and provenance assumptions.
- source_class: `independent_foundation_research_note`
- upstream_cluster_id: `MINI-SHAI-HULUD-DERIVED-ANALYSES`
- screening_decision: `exclude_same_incident_secondary`
- screening_reason: Same incident cluster as result 1 and no visible independent primary evidence.
- revision_or_supersession_state: `dated_2026-05_secondary_analysis`

### Result 15

- result_rank_or_backend_order: `15`
- url_or_fixed_locator: `https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_shai-hulud-ai-npm-supply-chain-attack_20260514-csa-styled.pdf`
- title: `CSAI Foundation | Cloud Security Alliance`
- visible_metadata: `Published: 2 months ago`
- visible_result: Related research note saying valid provenance may coexist with malicious packages.
- source_class: `independent_foundation_research_note`
- upstream_cluster_id: `MINI-SHAI-HULUD-DERIVED-ANALYSES`
- screening_decision: `exclude_same_incident_secondary`
- screening_reason: Same incident/upstream claim family as result 1.
- revision_or_supersession_state: `dated_2026-05_secondary_analysis`

### Result 16

- result_rank_or_backend_order: `16`
- url_or_fixed_locator: `https://arxiv.org/abs/2409.05014`
- title: `Analyzing Challenges in Deployment of the SLSA Framework for Software Supply Chain Security`
- visible_metadata: `Published: 1.9 years ago`
- visible_result: Preprint on deployment challenges, including provenance generation and verification documentation.
- source_class: `academic_preprint`
- upstream_cluster_id: `SLSA-DEPLOYMENT-STUDY`
- screening_decision: `include_supporting_counterevidence`
- screening_reason: Independent deployment perspective, but the visible result does not establish a new failure class beyond policy/implementation burden.
- revision_or_supersession_state: `preprint_version_not_shown_in_search_result`

### Result 17

- result_rank_or_backend_order: `17`
- url_or_fixed_locator: `https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/05/CSA_research_note_mini_shai_hulud_supply_chain_sigstore_20260515-csa-styled.pdf`
- title: `CSAI Foundation | Cloud Security Alliance`
- visible_metadata: `Published: 2 months ago`
- visible_result: Related note stating attestation is necessary but insufficient and threat-model assumptions matter.
- source_class: `independent_foundation_research_note`
- upstream_cluster_id: `MINI-SHAI-HULUD-DERIVED-ANALYSES`
- screening_decision: `exclude_same_incident_secondary`
- screening_reason: Same incident cluster as result 1.
- revision_or_supersession_state: `dated_2026-05_secondary_analysis`

### Result 18

- result_rank_or_backend_order: `18`
- url_or_fixed_locator: `https://arxiv.org/abs/2512.23480`
- title: `Agentic AI for Autonomous Defense in Software Supply Chain Security: Beyond Provenance to Vulnerability Mitigation`
- visible_metadata: `Published: 6 months ago`
- visible_result: Proposes AI-based supply-chain defense and says provenance frameworks do not actively remove vulnerabilities.
- source_class: `academic_preprint`
- upstream_cluster_id: `AI-SUPPLY-CHAIN-DEFENSE`
- screening_decision: `exclude_out_of_scope`
- screening_reason: AI mitigation proposal does not bear on the exact GitHub policy and trust claims.
- revision_or_supersession_state: `preprint_version_not_shown`

### Result 19

- result_rank_or_backend_order: `19`
- url_or_fixed_locator: `https://www.cybersymposiums.com/tdf/EarlyAccess/images/pdfs/scribe02.pdf`
- title: `A Use Case of Using Scribe Trust Hub`
- visible_metadata: `Published: 5 months ago`
- visible_result: Use-case PDF mentioning SLSA L3 isolation/signing-secret requirements.
- source_class: `practitioner_use_case_pdf`
- upstream_cluster_id: `SCRIBE-USE-CASE`
- screening_decision: `exclude_lower_relevance`
- screening_reason: Visible result does not provide independent evidence about GitHub's actual implementation or this design.
- revision_or_supersession_state: `dated_2026_early_access`

### Result 20

- result_rank_or_backend_order: `20`
- url_or_fixed_locator: `https://arxiv.org/abs/2006.01722`
- title: `Threat Detection and Investigation with System-level Provenance Graphs: A Survey`
- visible_metadata: `Published: 6.1 years ago`
- visible_result: Survey of system-level provenance graphs.
- source_class: `academic_preprint`
- upstream_cluster_id: `SYSTEM-PROVENANCE-SURVEY`
- screening_decision: `exclude_different_provenance_domain`
- screening_reason: Not software-build attestation provenance.
- revision_or_supersession_state: `historical_preprint`

## Post-query delta assessment

- assessed_after_query_at_utc: `2026-07-25T16:22:08Z`
- new_high_impact_failure_class: `yes`
- delta_id: `R8-RS05-DELTA-S1-VALID-ATTESTATION-COMPROMISED-PIPELINE`
- delta: A build/pipeline compromise can use the expected hosted environment and legitimate OIDC identity and still emit an attestation matching expected builder, repository, and workflow. Exact identity policy narrows provenance origin but does not establish an uncompromised artifact or intended semantics.
- evidence: Result 1, supported by versioned threat classes in result 2.
- candidate_decision_effect: Keep all R7 downgraded terms. For the future machine gate, treat hosted-runner, repository, issuer, workflow identity, signer digest, source digest, predicate type, and subject digest checks as necessary but not sufficient. Preserve a separate artifact/manifest semantic review and explicitly assess build-environment, cache, untrusted-code, and OIDC exposure boundaries.
- open_critical_or_major_contradiction: `none; the counterexample narrows assurance and is compatible with the frozen non-semantic claim`
- stability_implication: At least one of S2 or S3 must occur after this delta and yield no later high-impact failure class or open critical/major contradiction for the passing rule to be satisfiable.

