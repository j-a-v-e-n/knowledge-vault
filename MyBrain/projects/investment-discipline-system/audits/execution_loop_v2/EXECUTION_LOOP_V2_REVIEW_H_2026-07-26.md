# Execution Loop V2 — Independent Review H

## Exact subject and verdict

- Candidate commit:
  `d0b77ede32ff3b04fb9b44b767d0181d5176f3a5`
- Candidate tree:
  `bb0e01a0a1ff52d7ae40ffb24d1a06ab9631b36f`
- Candidate parent:
  `60b6ba21c86153c454c515bb819bd9a75d6b0b4b`
- Candidate project-subtree tree:
  `651fbb53dc78ec408b70c3940f3d3d3404e74ff9`
- Review result: **BLOCKED**
- Required packet disposition: terminal `blocked`; preserve every existing
  failure
- In-place continuation, another retry-budget migration, retry index `14`, and
  promotion of the stage-closure proposal: **FORBIDDEN**
- Foundation acceptance, design freeze, project completion, product quality,
  usability, strategy edge, and investment effectiveness: **not established**

The candidate commit was pushed as an ancestor of remote branch head
`141ee60eb58eb01b9e0f4c9581a66674615b2ae8`. That later commit changed only a
project-external panel file; its project-subtree tree was exactly the same as
the candidate project-subtree tree above.

Review H used three substantive platform-observable separate-agent routes:

1. Git object-store authority and finalization process quiescence;
2. finite-program, migration reconstruction, and terminal-transition
   consistency;
3. scope omissions, evidence independence, and the candidate stage-closure
   proposal.

An earlier finite-program route was stopped by a platform filter and produced
no substantive verdict. It is a **no verdict** and is not counted as
acceptance, rejection, or corroboration. Every substantive route returned
`blocked`. Platform separation is process evidence only; it does not prove
organizational independence, authenticated reviewer identity, or a hostile
security boundary.

## Candidate baseline evidence

Before independent challenge:

- the exact post-record targeted suite ran `150` tests and passed all `150`;
- the directly relevant execution-loop and recorder suite ran `96` tests and
  passed all `96`;
- the no-live verifier returned `status=pass`, with `15` Python files, `10`
  configuration files, `21` inert files, `18` endpoint observations, and `1`
  active work packet;
- the execution-loop verifier returned `verification_status=valid`,
  `execution_freshness_status=current`, and no errors;
- project state views were fresh;
- `ruff check` passed;
- `py_compile` passed;
- `git diff --check` passed;
- `ruff format --check` reported that
  `scripts/verify_execution_loop_v2.py` would be reformatted.

The exact-candidate project-method runner passed `13` declared checks and
remained blocked on `CTX-02`, `VER-07`, `OPS-08`, and `ECO-03`. Its ephemeral
evidence SHA-256 was
`61544426a7b3047ba714c9e5e2c8765fb20b384b84cb1fa2d2a691037f1e105a`,
and it reported no precondition errors.

The full governance runner discovered, planned, and loaded `518` selectors,
started `496`, and recorded `456` successful selectors. It returned
`status=fail` and `coverage_complete=false`. Source fingerprints were unchanged,
the active-process count after the run was `0`, and all temporary roots were
removed. A direct non-heavy replay ran `472` tests and returned `25` failures
and `2` errors. The failures were concentrated in the known stale integration
chain: research sufficiency, ground-truth artifacts, context recovery,
component locators, frozen-test metadata, method-integration execution state,
attack baselines, and the normative frozen-file boundary.

These are honest failure results. Targeted passing tests do not substitute for
the failed global regression.

## Blocking findings

### H-MAJOR-GIT-OBJECT-STORE-SYMLINK

The verifier rejects a top-level alternate object store, promisor configuration,
partial-clone indicators, grafts, shallow state, and a symlinked top-level
`objects` directory. It does not reject internal object-store paths such as
`objects/pack` when they are symlinks to storage outside the pinned common Git
directory.

The reviewer created a temporary packed repository, moved its pack directory
outside the repository, and replaced `objects/pack` with a symlink. The
candidate's `git_repository_authority()` returned an authority with no errors,
and Git successfully resolved the candidate object from the external pack.

This contradicts the recorded
`pinned_common_directory_primary_objects_only_no_alternates_or_promisor`
authority. The implementation does not yet bind the complete object-store set.

### H-MAJOR-DETACHED-DESCENDANT-QUIESCENCE

The finalization supervisor proves liveness for its direct bootstrap and can
terminate the recorded process group. An acceptance target can nevertheless
start a delayed writer in a new session and then exit normally. That descendant
is outside the recorded process group, the bootstrap releases its liveness
lock, and finalization may snapshot and commit while the detached descendant
remains alive.

The reviewer observed:

```text
finalize_status=finalized_local_candidate
immediate_verification=valid/current
target_immediate=target-v1
target_delayed=late-detached-write
delayed_verification=invalid/invalid
```

The existing hostile delayed-write regression remains in the original process
group and therefore does not cover this path. Current process-group supervision
is not an operating-system containment guarantee.

### H-MAJOR-FINITE-PROGRAM-ACTIVATION-FAIL-OPEN

The finite-program loader returns no authority when the configured activation
record hash is absent from the history. The verifier and recorder then fall
back to generic evidence-progress rules rather than treating the missing
activation as an error for this packet.

In a temporary candidate-bound variant, the reviewer changed the descriptive
`root_cause` field in retry `0`, recomputed the blocker fingerprint and complete
record hash chain, and retained a structurally valid ledger. The full verifier
returned `valid/current`. The recorder then accepted an unlisted
`retry13/open`, accepted `retry14/open`, and again reported valid execution
verification.

The low-level tests that reject retry `14` receive an already-loaded finite
authority and therefore do not exercise authority disappearance. The packet
must fail closed whenever its configured finite authority cannot be activated.

### H-MAJOR-BLOCKED-TERMINAL-TRANSITION-UNRECORDABLE

The exact transition required by this review cannot be recorded by the
candidate recorder.

When the recorder prepares `retry13` with:

- root cause ID `REVIEW-H-BLOCKING-FINDINGS`;
- status `blocked`;
- every existing failure preserved; and
- this exact Review H audit path added,

it changes the packet and ledger envelope to `blocked` before validating the
proposed chain. The finite-program historical reconstruction spreads the
current envelope while replacing only the contract and attempts. It therefore
reconstructs predecessor and intermediate ledgers with the wrong
`reported_state` and terminal-envelope fields.

The reviewer reproduced the exact branch in a temporary candidate and the
recorder rejected it with:

```text
finite program WP-METHOD-RUNTIME-FOUNDATION: predecessor ledger differs
finite program WP-METHOD-RUNTIME-FOUNDATION: intermediate ledger reconstruction differs
```

This is a fail-closed rejection, but it means the machine-declared terminal
blocked path is internally inconsistent. The audit must not claim that the
packet was successfully moved to `blocked` unless the real recorder produces
that record.

### H-MAJOR-PREDECESSOR-GIT-RELATION-UNVERIFIED

The finite authority stores a predecessor commit, tree, committed ledger hash,
and record count. The verifier checks their formats and reconstructs ledger
bytes, but it does not use the pinned Git authority to prove that:

1. the commit object exists;
2. its tree equals the declared tree;
3. the project ledger blob in that commit equals the declared committed
   eight-record ledger.

The values are correct for this candidate under an external read-only Git
check, but that relation is not established by the execution-loop receipt
itself.

### H-MAJOR-REVIEW-DISPOSITION-SEMANTICS-SELF-REPORTED

The finite program's acceptance transition requires the expected root-cause
label, `status_after=resolved`, an empty failure set, and this Markdown path.
The verifier does not parse this report's candidate commit/tree, verdict,
findings, or evidence lineage. The evidence support relation is generated from
the caller's requested resolved-failure set.

A later Git sidecar can bind candidate and review commits, but neither that
sidecar nor the local review tag authenticates independent reviewer identity.
The machine rule proves the presence and hash of a controlled report path, not
semantic independence or organizational assurance. It must not be described as
proof that review findings converged.

## Risk-proportionate stage-closure candidate

`RISK_PROPORTIONATE_STAGE_CLOSURE_CANDIDATE_V1.json` remains **BLOCKED** and may
not be promoted or used to change completion semantics.

Review H makes a more precise distinction than the prior claim that the
proposal was entirely inert:

- no policy or verifier adopts its proposed stage-closure semantics;
- it has not changed a core rule, completion gate, product state, or financial
  claim;
- however, it is inside the foundation packet's bounded audit tree, entered the
  attempt ledger as evidence, remains in `evidence_after`, and participates in
  current-file hash and snapshot freshness checks.

That ledger/freshness coupling is still within record-and-review activity, but
it is a real operational effect and maintenance cost. The proposal therefore
must not be described as having no effect in the broader sense.

The proposal's known side effects remain open review subjects:

1. governance complexity can displace product work;
2. same-origin agents and evidence can create false confidence;
3. a process green light is not product usability or financial validity;
4. unknowns can become a premature-closure dumping ground;
5. fixed prompts and reviewer fatigue can imitate convergence;
6. binding the whole audit tree into execution evidence makes narrative review
   churn create freshness and ledger maintenance work.

Its unresolved design issues still include stage identity, claim ceilings,
finding-set continuity, severity-change authority, evidence lineage,
type-appropriate closure profiles, executable future triggers, expiry/reopen
semantics, and a falsifiable convergence predicate. Assurance cases, IV&V, and
defeater/eliminative argumentation remain supporting analogies only.

## Review G closure status

The candidate has code and committed tests for every named Review G finding:

- pinned parent authority and nested-repository rejection;
- final retry-budget authority and bounded migration set;
- finalization process-group quiescence;
- stopping progress separated from evidence progress;
- a packet-specific remaining transition program;
- local `core.worktree`, include, promisor, alternate, graft, and shallow
  rejection;
- a positive linked-worktree path;
- absent, symlink, gitlink, and non-ancestor candidate-object regressions.

Those controls close the specific previously known examples. Review H's
findings are adjacent omitted cases and state-machine inconsistencies, so the
candidate remains blocked.

## Required terminal disposition

The only transition authorized by the candidate finite program is:

```text
retry_index=13
root_cause_id=REVIEW-H-BLOCKING-FINDINGS
status_after=blocked
failure_after=[
  ECO-01,
  ORG-04,
  REC-11,
  REC-12,
  REC-13,
  REC-14,
  REC-15,
  REC-16,
  REC-17,
  REC-18,
  REC-19,
  REC-20,
  REC-21
]
```

The recorder must be invoked once with that exact disposition. If it rejects
the transition as reproduced above, the result is an unrecordable terminal
stop, not authorization to patch the implementation, alter history, widen the
budget, add another migration, or continue in place.

## Actual terminal-transition attempt

The operator invoked the candidate recorder once with the exact disposition
above and expected tail
`09e70996869892340b364d88683b4662f08dac22b1d3bda1a1e899e6217d29ac`.
It returned nonzero:

```json
{
  "error": "finite program WP-METHOD-RUNTIME-FOUNDATION: predecessor ledger differs; finite program WP-METHOD-RUNTIME-FOUNDATION: intermediate ledger reconstruction differs",
  "status": "fail"
}
```

The failed append left durable operation
`86b964b1709c466e8ca4c05fb4c2225b` at phase `outcome_recorded`. The standard
`recover --verify` command was invoked once and returned the same reconstruction
errors. The ordinary verifier then honestly returned:

```text
verification_status=invalid
execution_freshness_status=invalid
execution recorder has an interrupted operation requiring recovery
latest controlled snapshot is stale
```

The operation was not manually deleted, rewritten, or relabelled as recovered.
The packet was not represented as successfully blocked. This is the terminal
machine state produced by the only authorized transition and its standard
recovery path.

## Claim ceiling and remaining unknowns

The highest supportable statement is:

> Candidate `d0b77ede...` contains coherent remediations and passing targeted
> checks for the Review G examples, but independent Review H found reproducible
> Major omissions in object-store authority, descendant-process quiescence,
> finite-program activation, terminal transition recording, predecessor Git
> binding, and review-disposition semantics. The foundation is blocked.

This review does not establish:

- a successfully recorded terminal packet state;
- a clean global governance regression;
- closure of `CTX-02`, `VER-07`, `OPS-08`, or `ECO-03`;
- design freeze or project completion;
- product usability or long-term personal adoption;
- paper-trading calibration or behavioral improvement;
- a strategy edge, investment effectiveness, or realizable returns;
- operating-system containment, Git executable integrity, repository ownership,
  protected remote identity, or organizationally independent review.

## Review-process limitations

- One substantive review route temporarily wrote
  `evidence/verification/V-PROJECT-METHOD.json` by invoking the method runner
  without its ephemeral option. It then deleted exactly that generated file and
  the two newly empty directories. Git status returned clean; no tracked
  project bytes changed. This demonstrates that a platform-separated review
  route is not automatically a read-only filesystem boundary.
- All novelty probes used temporary directories and did not modify the exact
  candidate.
- Review H does not use the candidate stage-closure proposal as an acceptance
  rule.
- The single formatter diff is a Minor hygiene defect and is not used as a
  substitute for the Major findings above.
