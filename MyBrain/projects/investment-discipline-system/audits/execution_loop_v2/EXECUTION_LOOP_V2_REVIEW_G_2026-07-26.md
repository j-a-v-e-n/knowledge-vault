# Execution Loop V2 — Independent Review G

## Exact subject and verdict

- Candidate commit: `ea69d25c0cc190ae0fc3f72c5fc79f738ff1d68b`
- Candidate tree: `dd0d4d7a14ec391d8ffab8956719e08a6f5adcc6`
- Candidate parent: `f8f4b26e680cd0cecfa0467bf5642640e9f5b013`
- Review result: **BLOCKED**
- Packet disposition: remain `active`; preserve every existing failure as open
- Completion, design-freeze, product-quality, usability, strategy-edge, and
  investment-effectiveness claims: **not created**

Review G used three platform-observable separate-agent review routes. One earlier
route was stopped by a platform filter and produced no substantive verdict; it is
recorded as `no verdict` and is not counted as an acceptance, rejection, or
independent corroboration. The three substantive routes challenged runtime
recovery, Git authority, finite-loop governance, and the candidate stage-closure
proposal. Platform separation is auditable process evidence, not proof of
organizational independence, reviewer identity, or a hostile security boundary.

## Candidate baseline evidence

Before independent challenge, the builder-side bounded regression on the exact
candidate passed `133` related tests. The exact-candidate project-method runner
executed `13` declared checks and honestly remained blocked on `CTX-02`, `VER-07`,
`OPS-08`, and `ECO-03`; its evidence hash was
`04b9a93fe4128cbe38765daf7417d9178b141edc92e2559b3ce0a5d929f11307`.

The full governance runner discovered and planned `501` selectors, loaded all
`501`, started `479`, and recorded `439` successful selectors. It returned
`status=fail` and `coverage_complete=false`. Source fingerprints were unchanged,
the active-process count after the run was `0`, and all temporary roots were
removed. This is failure evidence, not a full-regression pass.

## Blocking findings

### G-CRITICAL-GIT-PARENT-AUTHORITY

The repository authority is still discovered from the project directory. A
nested `.git` placed at the project root can therefore replace the true parent
repository. A reviewer reproduced an end-to-end seal in which the candidate and
review anchor existed only in the nested repository, neither existed in the true
parent repository, and the recorder nevertheless returned `sealed_complete`.

Required closure:

1. Pin the trusted worktree top-level outside project-local Git discovery.
2. Derive the project prefix from that pinned root.
3. Parse and bind main-worktree and linked-worktree Git metadata without trusting
   the nearest `.git`.
4. Add a committed nested-repository substitution regression that fails closed.

### G-CRITICAL-FINAL-RETRY-CEILING

The `12 → 16` foundation retry-budget migration is finite only in prose. The
current verifier accepts the packet's current budget and the generic packet
schema permits later values up to its broad schema ceiling. Nothing
machine-enforces that this is the only migration or that `16` is final.

Required closure:

1. Bind the exact packet, `from=12`, `to=16`, migration path and hash,
   predecessor commit/tree, and predecessor committed ledger hash.
2. Bind the reconstructible uncommitted intermediate ledger state and its
   deterministic reconstruction rule.
3. Mark the authority `final=true`.
4. Reject `16 → 20`, a second migration artifact, or any unprogrammed remaining
   transition without requiring another narrative decision.

### G-MAJOR-FINALIZE-LIVE-CHILD

`quiesce_recorded_child()` returns immediately for every operation kind except
`run`, while finalization recovery invokes it for a `finalize` operation in
`check_prepared`. A reviewer killed the recorder after a live acceptance target
had started. Recovery immediately recorded `RECORDER-902`, retired the operation,
and reported the controlled snapshot current, but the still-live target later
changed a controlled file and made the ledger stale.

The target closed file descriptors `3..255`, ignored `SIGTERM`, and delayed its
write. The observed sequence was:

- operation phase before recovery: `check_prepared`
- supervisor lock held before recovery: `true`
- immediate target content after recovery: unchanged
- delayed target content: `late-finalize-write`
- immediate verification: valid
- delayed verification: invalid, because the latest controlled snapshot was stale

Required closure: finalization recovery must terminate the recorded process group,
wait for the supervisor liveness lock, escalate to `SIGKILL` when necessary, and
only then snapshot, record `RECORDER-902`, and retire the operation. Preserve both
the hostile delayed-write negative regression and the adjacent successful
finalization path.

### G-MAJOR-STOPPING-PROGRESS-CONFLATION

The recorder currently derives `declared_progress` from any newly added evidence
or resolved failure. Migration audits, narrative review files, and formatter-only
implementation-byte changes can therefore reset both no-progress counters even
when they do not reduce uncertainty or close a defect.

Required closure: keep evidence-accounting progress distinct from stopping-rule
progress. For the active foundation packet, bind the existing history and a
finite remaining transition program. Audit-only, migration-only, formatter-only,
or unprogrammed changes must not reset stopping counters.

### G-MAJOR-REMAINING-ATTEMPT-PROGRAM

The arithmetic of the current budget is internally consistent: after execution
attempt `11`, attempts `12` through `15` can be nonterminal and attempt `16` is the
budget boundary. However, the system does not constrain that capacity to review,
repair, fresh-candidate observation, and independent disposition. The same
capacity can be consumed by arbitrary evidence churn.

Required closure: install a packet-specific finite state program. Review G may be
recorded once; one bounded semantic remediation may follow; the next exact
candidate must receive a fresh independent disposition; acceptance may resolve
only with supporting evidence for every failure, while another blocking verdict
must stop the packet rather than widen it again.

### G-MAJOR-REPOSITORY-LOCAL-CONFIG

Inherited `GIT_*` variables are stripped correctly, but repository-local
configuration remains trusted. A reviewer changed local `core.worktree` and made
Git return a different top-level and prefix without authority errors.

Required closure: pinned authority must not be derived from local configuration.
Dangerous local include/worktree/promisor settings must be rejected or explicitly
overridden under a documented, tested trust boundary.

### G-MAJOR-OBJECT-STORE-BOUNDARY

Explicit `--git-dir` and `--work-tree` do not prove that objects come from the
primary object directory. A shared-clone probe resolved a commit solely through
`objects/info/alternates`. The current policy does not say whether alternates,
linked-worktree common directories, promisor objects, or partial clones are
trusted.

Required closure: bind the common Git directory and object-store set. The bounded
foundation design should fail closed on alternates and promisor/partial-clone
configuration while retaining a positive linked-worktree path. Record TOCTOU,
filesystem ownership, Git executable, mount replacement, and protected-remote
identity as limitations rather than solved properties.

### G-MAJOR-CANDIDATE-OBJECT-REGRESSION-GAPS

The committed suite covers parent-prefix positive behavior, hostile inherited
Git environment, nested-tree ordering, literal pathspecs, replacement objects,
divergent index state, positive seal, and anchor rewrite. It does not retain
candidate-tree regressions for an absent path, symlink blob, gitlink/submodule, or
non-ancestor review commit. Earlier independent probes on another candidate are
not repeatable evidence for this candidate.

Required closure: add those four negative candidate-object regressions and keep
the adjacent valid candidate path.

## Retry-migration reconstruction limitation

The migration's `before.ledger_raw_sha256`
`d380e0fe03f460b18ef38109baf70a6bb9024c66223435e0648749744d738385`
is not the ledger blob in parent commit `f8f4b26...`; that committed ledger hash is
`ac57f75f4da4a4187fd433bd94613f15061147da5cacead171d2265101fabf00`.
This does not show that old attempts were rewritten: the parent contains `8`
attempts, the candidate preserves all eight record hashes, and the migration
before-state is the later uncommitted intermediate containing attempts through
retry index `9` with the pre-migration packet contract.

The executable migration authority must state this boundary and reconstruct the
intermediate from the current immutable prefix using the canonical indented JSON
serialization rule. It must not describe the intermediate as an independently
authenticated historical snapshot.

## Risk-proportionate stage-closure candidate

`RISK_PROPORTIONATE_STAGE_CLOSURE_CANDIDATE_V1.json` remains a useful candidate
problem statement and candidate backlog item. Review G confirms that it was not
secretly activated:

- status remains `candidate_pending_independent_challenge`
- authority remains `record_and_challenge_only`
- it may neither freeze core rules nor alter completion semantics
- no current script or governance policy consumes it
- Review F already forbids promotion

Promotion remains **BLOCKED**. Its own risks are part of the review subject:

1. complexity and maintenance work can displace product work;
2. same-origin agents and evidence can create an illusion of independence;
3. a process green light does not establish usability or financial validity;
4. explicit unknowns can become a premature-freeze dumping ground;
5. fixed prompts and reviewer fatigue can imitate convergence.

Assurance cases, independent verification and validation, and
defeater/eliminative argumentation are supporting analogies, not automatic
authorization. A later proposal review must produce a smaller executable
mechanism and independently challenge scope omissions before any promotion.

## Reviewer verification and limitations

The runtime reviewer ran `47` recorder tests and the execution verifier, plus
novelty probes for durable outcomes, forced stop, timeouts, output bounds,
post-core recovery, hostile child supervision, Git environment redirection, and
adjacent recovery paths.

The Git reviewer ran `47` recorder tests and `32` execution-loop tests, plus
novelty probes for nested repository replacement, local `core.worktree`,
alternates, and linked worktrees. The finite-loop reviewer inspected the exact
migration, packet, ledger, recorder, verifier, and proposal. Its planned complete
record-chain recomputation did not run because its one-line probe had a syntax
error; no such recomputation is claimed here.

The reviews do not prove operating-system isolation, malicious-author resistance,
Git executable integrity, repository ownership, protected remote identity,
organizational reviewer independence, or absence of unknown defects.

## Required next candidate

The next candidate must close every Critical and Major item above in one coherent
authority model, add the listed negative and adjacent positive regressions,
machine-bind the final retry ceiling and remaining transition program, rerun
affected and global checks, commit and push one exact candidate, and receive a
fresh review that challenges both implementation defects and omitted scope.
