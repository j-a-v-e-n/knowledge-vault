# RESEARCH-REFRESH-R8 / RS-02 independent entailment review

## 0. Review identity, input, and boundary

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input`: `audits/research_r8/RS-02_RAW_REPORT.md`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `expected_review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `input_integrity_verdict`: `pass`
- `review_type`: `platform_observable_separate_thread_review`

This is a claim-by-claim review performed in a Codex thread separate from the
RS-02 author. It is platform-observable separation only. It is not a claim of
organizational independence, security isolation, cryptographic reviewer
identity, or absence of shared platform/model failure modes.

No network access or new search was used. The review was limited to the frozen
R8 preregistration schema, the exact RS-02 raw-report bytes, the RS-02 manifest,
and the saved source bytes at the report's declared source ranges. Every
manifest-listed source snapshot used below was re-hashed and matched its
manifest SHA-256. This review does not independently re-audit query accounting,
search-result completeness, temporal Git ancestry, implementation, control
effectiveness, or the other topic-closure predicates.

The reviewed decisive-claim set is the report's preregistration-shaped atomic
set `RS02-C01` through `RS02-C09`. Section 8 is treated as synthesis of those
claims' `decision_effect` fields, not as additional empirical claims. If a
Section 8 prescription is later asserted as a separately decisive factual or
control-sufficiency claim, it must first be atomized with the preregistered
claim fields and independently reviewed; it is not silently certified here.

Verdict interpretation:

- `entailed`: the bounded empirical claim is directly supported by the checked
  source ranges, and its stated decision effect does not depend on a material
  evidence-expanding assertion.
- `contested_non_decision_changing`: the bounded empirical core is supported,
  but a conservative, carry-forward, or implementation-facing part of the
  decision effect is not itself established by these R8 ranges. The contest
  limits what this review certifies but does not reverse or relax the report's
  fail-closed decision.
- Any other verdict would block the independent-entailment closure predicate.

## 1. Per-claim review

### `RS02-C01`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C01`
- `verdict`: `contested_non_decision_changing`
- `reason`: The saved Supersede v1 abstract and Section 5.1 directly report
  the LongMemEval knowledge-update comparison from `92%` full context to `77%`
  bounded memory for gpt-5.4, and the cross-model table shows that the bounded
  memory gap remained as model scale increased. The limitations range records
  the LLM-judge noise, smaller scale-study sample, and single training run.
  Therefore the bounded empirical claim is entailed. “Long-term memory remains
  non-authoritative” is a conditional project policy, not a universal empirical
  consequence of this one setup. It remains a defensible fail-closed policy
  because the report does not claim memory can never work and conditions
  authority on later gates; narrowing the certification to that policy framing
  does not change the current decision.
- `checked_source_ranges`: `RS02-SRC-MEM-01`
  (`ba7175324f30b02ff1967242250d421afdb0a6f1f80c3f48d2576f4f77de7e1b`),
  PDF p. 1 abstract; p. 5 Figure 2, Table 1, and Section 5.1; p. 8
  limitations.
- `overclaim_or_missing_counterevidence`: These ranges do not establish that
  every long-term-memory architecture is non-authoritative, nor that the
  proposed supersession schema and regression probes are sufficient controls.
  Positive counterevidence is present in the same snapshot: full-context
  performance is stronger and the reported training result is directional.
  The review certifies the observed failure and the conditional gate, not a
  timeless ban or control-sufficiency claim.

### `RS02-C02`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C02`
- `verdict`: `entailed`
- `reason`: STALE explicitly defines implicit conflict as later evidence
  invalidating an earlier belief without explicit invalidation, separates State
  Resolution, Premise Resistance, and Implicit Policy Adaptation, and reports
  materially different performance across those probes. Its discussion
  directly states that recognition/retrieval of the updated state does not
  imply stale-premise rejection or downstream application. The proposed
  separate memory-test assertions track those measured dimensions.
- `checked_source_ranges`: `RS02-SRC-MEM-02`
  (`388f71f1eb952e7d7e7b19c2f25bfc744c47efa8ee00a548093b949432495109`),
  PDF p. 1 abstract; pp. 3-4 definition and taxonomy; p. 7 Table 2 and
  discussion; p. 14 limitations.
- `overclaim_or_missing_counterevidence`: No decision-changing overclaim
  found. The ranges do not prove that the CUPMEM prototype is sufficient or
  that the benchmark covers repeated updates, gradual drift, or arbitrary
  open-ended interactions; the raw report preserves those limitations.

### `RS02-C03`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C03`
- `verdict`: `entailed`
- `reason`: MemGuard directly defines heterogeneous memory contamination as
  functionally incompatible semantic, episodic, and procedural memories being
  stored, retrieved, or composed without adequate boundaries. The component
  analysis reports degradation when relational composition and query-adaptive
  routing are removed. The claimed type-separation and routing mitigation is
  therefore entailed within the tested benchmarks, and the decision to test
  evidential-role mismatches is aligned with the observed mechanism.
- `checked_source_ranges`: `RS02-SRC-MEM-03`
  (`b396784d2f056b3310ee4012b2d909fa148f27a24a3a8ea249e3fba32271a5fd`),
  PDF p. 1 abstract and example; p. 3 Section 3 definition; p. 8 component
  analysis; p. 9 limitation.
- `overclaim_or_missing_counterevidence`: No decision-changing overclaim
  found. The source does not establish a universal memory-type taxonomy or
  complete safety boundary. It explicitly leaves generation-time composition
  error and added inference cost unresolved, which the raw report retains.

### `RS02-C04`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C04`
- `verdict`: `contested_non_decision_changing`
- `reason`: The saved ACL paper directly reports experience-following,
  error propagation, misaligned experience replay, and sensitivity to
  evaluator quality in the tested memory-addition/deletion systems. The
  empirical claim is entailed. The decision effect's outcome labels and
  provenance are reasonable regression controls, but treating every
  agent-written lesson as tainted until later grounding, and extending the
  result to atomic cross-agent claim lineage, quarantine, rollback, and an
  infection oracle, are conservative design choices rather than findings
  demonstrated by these ranges. Keeping those gates as unvalidated,
  fail-closed controls does not reverse the current decision.
- `checked_source_ranges`: `RS02-SRC-MEM-04`
  (`2c3992d238f5d6dec4ed96faae0a82e3b88edc6e37b26d8622a2b780f2160400`),
  PDF p. 1 abstract; pp. 5-6 Sections 3.3-3.4; p. 9 conclusion and
  limitations.
- `overclaim_or_missing_counterevidence`: The source studies retrieved
  trajectory memory, not multi-agent claim-flow isolation. It does not test
  role-name isolation, atomic claim lineage, rollback, quarantine semantics, or
  an infection oracle, and it omits structural transformation, merging,
  summarization, and reflection. Those controls must remain labeled
  carry-forward design gates requiring their own tests, not R8-entitled
  mechanisms.

### `RS02-C05`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C05`
- `verdict`: `contested_non_decision_changing`
- `reason`: ACRFence v1 directly describes and validates, in its fixed
  proof-of-concept, Action Replay and Authority Resurrection after
  checkpoint-restore. The saved ranges show a semantically repeated action
  receiving a different request reference and being accepted as a new external
  action. They support the bounded conclusion that checkpoint presence or a
  regenerated request identifier is not exactly-once proof. The report also
  correctly records that the proposed mitigation was not implemented or
  evaluated. The full replay/effect contract is therefore a conservative design
  hypothesis and fault-test plan, not a control proven sufficient by the paper.
  Maintaining the defer-and-test decision is non-decision-changing.
- `checked_source_ranges`: `RS02-SRC-DUR-01`
  (`5b88ebb1f9dc1cb136c2e8b282a5b9d31122dc172ecd9c1893f4a5b578e86263`),
  PDF p. 1 abstract and root cause; p. 2 threat model and attack validation;
  pp. 2-3 proposed mitigation, discussion, and evaluation limitation.
- `overclaim_or_missing_counterevidence`: The ranges do not validate
  normalized-intent hashes, authority/capability epochs, precondition hashes,
  external receipts, reconciliation, compensation, `human_blocked` handling,
  upgrade replay, graph termination, or the complete crash matrix. They also do
  not compare a persistent graph with a simple loop. Those items may remain
  proposed gates, but neither ACRFence nor the broader persistent-graph
  replay/idempotency design is certified as sufficient. ACRFence adoption must
  remain deferred pending implementation and adversarial fault tests.

### `RS02-C06`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C06`
- `verdict`: `contested_non_decision_changing`
- `reason`: The exact Anthropic article says agents skew positive when grading
  their own work, calls generator/evaluator separation a strong lever, and
  explicitly says separation alone does not eliminate evaluator leniency. That
  vendor-reported claim is entailed. The article does not test blind candidate
  identity, order swap, pinned judge revision, deterministic references, or
  Javen-approved labels. Retaining those as a carry-forward metamorphic gate is
  conservative and does not change the current refusal to let evaluator naming
  alone grant completion.
- `checked_source_ranges`: `RS02-SRC-DUR-02`
  (`3643c6685d30c4d4a3e3e9d7bef5ed53da5f2ce0e4c070f11c07c5c4e43e6aa7`),
  exact HTML section “Why naive implementations fall short,”
  self-evaluation and separate-evaluator paragraphs.
- `overclaim_or_missing_counterevidence`: The source is a vendor
  self-report without blind replication or an effect-size estimate. It supports
  “separation alone is insufficient,” but it does not itself establish
  claim-flow isolation, organizational independence, or the effectiveness of
  the report's exact blind-identity/order-swap gate. Those controls are not
  newly entailed by R8.

### `RS02-C07`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C07`
- `verdict`: `contested_non_decision_changing`
- `reason`: The exact article reports that the earlier Sonnet 4.5 harness
  needed context resets because compaction alone was insufficient in that
  setup, while the later Opus 4.5 harness dropped resets and used automatic
  compaction. This entails the bounded model/harness-revision-dependence claim
  and refutes the report's two universal formulations. It does not measure
  positional loss, empty-context project restart correctness, stale-request
  handling, or correctness after compaction. Retaining those probes as
  carry-forward tests is conservative, but this review does not certify them as
  newly supported by R8.
- `checked_source_ranges`: `RS02-SRC-DUR-02`
  (`3643c6685d30c4d4a3e3e9d7bef5ed53da5f2ce0e4c070f11c07c5c4e43e6aa7`),
  exact HTML context-reset/compaction paragraphs and “The architecture”
  paragraph.
- `overclaim_or_missing_counterevidence`: A structured handoff between
  context-reset sessions is not evidence of crash/restart correctness, and one
  successful continuous-session vendor setup is not proof that compaction is
  sufficient. Beginning/middle/end, compaction, restart, and stale-request
  probes remain unvalidated carry-forward gates. The raw report acknowledges
  the absence of a new direct positional benchmark, so the contest does not
  alter its current decision.

### `RS02-C08`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C08`
- `verdict`: `contested_non_decision_changing`
- `reason`: The peer-reviewed paper directly reports the task-dependent
  voting/consensus comparison, the `13.2%` reasoning-task result, and reduced
  performance as discussion rounds increased in the stated setup. Its
  limitations preserve sampled subsets, repeated runs, compute cost, response
  convergence, and incomplete prompt/persona ablation. This entails the bounded
  counterevidence against universal “more agents help” or “more agents hurt”
  claims. The report's test-only adoption remains appropriately narrow.
- `checked_source_ranges`: `RS02-SRC-MAS-01`
  (`f4c85dab5bc9dada9d6bc4554dbc7224386769039bc1c2fcff7d856e31863f6d`),
  PDF p. 1 abstract; p. 5 task/protocol comparison; p. 6 agent/round
  analysis; p. 9 conclusion and limitations.
- `overclaim_or_missing_counterevidence`: The source does not evaluate
  open-project semantic review, deterministic-oracle isolation, claim lineage,
  quarantine, rollback, or infection tests. It also does not establish that
  shared debate is generally unsafe. Those are conservative adoption
  conditions and carry-forward controls, not findings entailed by this
  snapshot. Because the report allows only a test-only experiment and does not
  use agent count as an independence guarantee, this limitation does not change
  the current decision.

### `RS02-C09`

- `reviewer_locator`: `codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
- `review_input_sha256`: `5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`
- `claim_id`: `RS02-C09`
- `verdict`: `contested_non_decision_changing`
- `reason`: The four fixed JSON bodies directly report the four existence
  paths stated in the claim: stale-context overwrite after reset/restart,
  prior commands re-entering a new context as current input, an orphaned tool
  call poisoning replay, and interruption/loop logic producing missed or
  duplicate memory review. The claim is carefully bounded to reported
  existence and not independent reproduction. Turning these reports into
  regression probes is supported; the complete metadata/CAS/edge-transition
  design remains a conservative extrapolation.
- `checked_source_ranges`: `RS02-SRC-ISSUE-01`
  (`17813fa4e55d80cf8f857db257986935be54d064dbc20e139071140489263113`),
  JSON `$.body`, derived lines 1-39; `RS02-SRC-ISSUE-02`
  (`ce3654c614349083c1737da7f45f87f161620ad31137ae3fc9349e50e2afcccd`),
  JSON `$.body`, derived lines 1-23 and 100-104;
  `RS02-SRC-ISSUE-03`
  (`e12ee1b466d02ed8cfa88ddabf465968ff847be26741a807dd8606df5f60d1bc`),
  JSON `$.body`, derived lines 1-25, 61-73, and 83-123;
  `RS02-SRC-ISSUE-04`
  (`6c51d5fa9f8afd8f36ce1dc4278f70f7b9ae4fcdf85e03186256caf3de50b283`),
  JSON `$.body`, derived lines 3-30.
- `overclaim_or_missing_counterevidence`: The issue snapshots are reports,
  not pinned-release reproductions or incidence evidence. They do not by
  themselves establish all project/thread/session/agent/profile scope fields,
  compare-and-swap as the sufficient stale-writer solution, or correctness over
  every interruption edge. Closed/completed states are material
  counterevidence against present-release incidence. The raw report preserves
  that boundary, so the regression-gate decision remains unchanged.

## 2. Cross-claim challenge of the named decision boundaries

### Context, compaction, and restart

R8 directly supports only the vendor-reported, revision-specific contrast in
`RS02-C07`. It does not newly entail lost-in-the-middle incidence,
empty-context restart correctness, stale-request correctness, or the
sufficiency of compaction. Those probes may be retained as R7 carry-forward
gates, but this review does not convert them into R8-proven facts.

### Claim-flow isolation

`RS02-C04`, `RS02-C06`, and `RS02-C08` support trajectory error propagation,
evaluator leniency despite role separation, and task/protocol-dependent
multi-agent results. They do not directly test atomic claim lineage,
quarantine, rollback, or an infection oracle. “Different role names do not
establish independence” is a sound boundary for this platform-observable
review, but the effectiveness of the proposed claim-flow controls remains a
design/test hypothesis.

### Persistent graph replay and idempotency

`RS02-C05` and `RS02-C09` support concrete semantic replay and malformed-history
failure paths. They do not prove the sufficiency of the complete Section 8
effect contract, do not compare a graph runtime with a simple loop, and do not
validate termination, upgrade replay, compensation, or exactly-once behavior.
The entailed decision is to reject exactly-once claims based only on checkpoint
or request-ID labels and to require implementation/fault evidence before
adoption. The detailed contract is not itself certified as sufficient.

### Long-term memory as authority

The memory snapshots establish several bounded failure mechanisms and also
contain positive mitigation evidence. They do not entail a universal statement
that long-term memory can never be authoritative. The report's actual decision
is narrower: no authoritative use before provenance, update, type, scope,
contamination, and decision-time gates are tested. This is a conservative
project policy supported by unresolved failure evidence, not a universal
scientific conclusion.

## 3. Overall verdict and closure-predicate recommendation

- `overall_verdict`: `contested_non_decision_changing`
- `independent_entailment_predicate_result`: `true`
- `blocking_claim_verdict_present`: `false`

Every reviewed atomic claim has an allowed design-closure verdict:
`entailed` or `contested_non_decision_changing`. The contestations limit the
scope of certification to the bounded empirical claims and conservative
fail-closed decisions. They do not certify the sufficiency of the proposed
controls, and they do not convert carry-forward R7 probes into newly evidenced
R8 findings.

Recommended update to the RS-02 closure predicate:

- Change only `every decisive claim passes independent per-claim entailment
  review` from `false` to `true`, bound to
  `reviewer_locator=codex_subagent:019f9a31-b5c3-78e2-a63f-a24aec4ec8df`
  and
  `review_input_sha256=5ac9ee46db12f9405fa4e35a502d33fd7bcb6bf711134b272da32a0253d81b24`.
- Do not infer implementation completion, control sufficiency, machine
  provenance, release readiness, provider onboarding, Javen approval, or
  topic-wide/round-wide closure from this review.
- Do not change the raw report. The integrating reviewer must recompute the
  overall topic disposition from all preregistered predicates and must keep
  Section 8 prescriptions labeled as design outputs pending implementation and
  fault evidence.
- If any Section 8 prescription is promoted to a separately decisive factual
  or sufficiency claim, the independent-entailment predicate becomes blocked
  until that claim is atomized and independently reviewed against declared
  exact source ranges.
