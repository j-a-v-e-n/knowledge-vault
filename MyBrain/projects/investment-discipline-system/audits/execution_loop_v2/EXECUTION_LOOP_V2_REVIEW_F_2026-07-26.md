# Execution Loop V2 Review F

## Binding and verdict

- Candidate commit:
  `f8f4b26e680cd0cecfa0467bf5642640e9f5b013`
- Candidate tree:
  `2e71897e6fede71f2d1296ef008d0d9be0b2dfae`
- Independent runtime/state-machine reviewer:
  `agent:019f9cdf-40ab-7601-b876-aa424fb36fbd` (`Parfit`), read-only
  exact-commit review
- Independent Git seal/tree reviewer:
  `agent:019f9cdf-6803-7930-b7cb-ef24faac570f` (`Mendel`), read-only
  exact-commit review
- Independent stage-closure-proposal reviewer:
  `agent:019f9cdf-9941-70f3-b7cb-ef24faac570f` (`Plato`), read-only
  exact-commit review
- Runtime/state-machine verdict: **accepted within the stated local-process
  boundary**
- Git seal/tree verdict: **blocked**
- Risk-proportionate stage-closure proposal verdict:
  **blocked as a candidate and forbidden from promotion**
- Final foundation verdict: **blocked**

This review grants no completion, freeze, authenticated-reviewer,
product-usability, strategy-edge, or financial-effectiveness claim. The
proposal review is recorded separately from the foundation failure state:
the proposal remains a non-operative backlog candidate and does not change
current completion semantics.

## Positive evidence retained within its tested boundary

Before the independent review, the exact candidate passed:

```text
Ran 130 tests in 56.649s
OK
```

That suite covered the execution loop, recorder, no-live boundary,
project-method runner, and generated-state freshness. The ordinary execution
verifier also returned `verification_status=valid`,
`execution_freshness_status=current`, and `errors=[]`.

The runtime reviewer separately ran two targeted groups:

```text
Ran 7 tests in 2.583s
OK

Ran 4 tests in 6.600s
OK
```

Its candidate-postfix probes confirmed:

- explicit and inherited contradictory `resolved` requests are rejected
  before a new durable operation exists;
- three distinct no-progress blocker labels still trigger the mechanically
  derived `RECORDER-FORCED-STOP` transition;
- old durable contradictory requests recover to
  `RECORDER-INVALID-DURABLE-REQUEST`, preserve prior failures, add
  `RECORDER-908`, and leave no pending operation;
- timeout, output-limit, durable-outcome crash, and post-core crash paths
  leave no pending operation and permit an adjacent normal run;
- the supervisor retains the liveness lock while a target closes inherited
  descriptors and ignores `SIGTERM`, and recovery kills the owned group before
  a delayed controlled write.

The Git reviewer independently ran the complete recorder module:

```text
Ran 44 tests in 48.331s
OK
```

It confirmed the existing replacement-object, literal-pathspec, nested-tree,
real-parent-prefix, file, absent-path, symlink, Git-link, divergent-index, and
review-ancestry checks. Those passing checks did not cover the environment
redirection below.

## Open critical foundation finding

### `F-CRIT-GIT-ENVIRONMENT-REDIRECTION` (`REC-11`)

Every verifier-owned Git subprocess disables replacement objects but still
inherits the caller's other `GIT_*` variables. In particular, `GIT_DIR` and
`GIT_WORK_TREE` can redirect candidate objects, the review tag, ancestry, tree
reconstruction, and review metadata to a decoy repository. The current prefix
helper checks only the returned prefix syntax; it does not bind that answer to
the real parent repository containing the project root.

The independent reviewer created a true parent repository plus a separate
decoy repository, then invoked the real seal under a poisoned environment:

```json
{
  "novelty_probe": "GIT_DIR_GIT_WORK_TREE_redirect",
  "seal_status_under_poisoned_env": "sealed_complete",
  "verification_under_poisoned_env": "valid",
  "candidate_in_true_parent_repo": false,
  "anchor_in_true_parent_repo": false,
  "verification_after_env_removed": "invalid"
}
```

The seal therefore can report success while the user-visible true repository
contains neither the candidate object nor the review anchor. Removing the
poisoned environment makes the same completion fail because the candidate,
tree, ancestry, and tag cannot be resolved in the true repository.

Required remediation:

1. remove every inherited `GIT_*` variable before any authority discovery or
   object/ref query, then add only the verifier-owned safe variables;
2. discover the repository top level, absolute Git directory, and project
   prefix in that clean environment;
3. require the project root to resolve inside that repository and require the
   observed prefix to equal the filesystem-derived relative path;
4. run every later object, ref, tree, blob, and ancestry query against the
   explicitly bound Git directory and work tree;
5. add an end-to-end negative regression in which a complete decoy repository
   is supplied through hostile Git environment variables and cannot create or
   validate a seal;
6. retain an adjacent positive seal path in a project nested below its real
   repository root.

## Runtime hardening item

The runtime reviewer found no Critical or Major runtime defect. It identified
one test-coverage hardening item: the old durable
`outcome_recorded` contradictory request path passed a novelty probe through
`RECORDER-908`, but that exact legacy fixture is not yet a committed regression
test. It should be added with both explicit and inherited unresolved-failure
forms. This does not overturn the runtime verdict, but closing it prevents a
future recovery regression from becoming invisible.

The owned process-group boundary remains explicit: a deliberately detached
descendant that escapes the immediate owned group is not contained without an
OS-level sandbox. This candidate does not claim otherwise.

## Independent challenge of the stage-closure proposal

`RISK_PROPORTIONATE_STAGE_CLOSURE_CANDIDATE_V1.json` remains a useful problem
statement, but the independent reviewer blocked promotion for the following
reasons:

### Critical proposal findings

- The proposal has no `stage_id`, claim ceiling, or allowed-transition model.
  Its deferred-Minor and explicit-unknown language therefore conflicts with
  the current final-release rule, which blocks freeze on any open Critical,
  Major, Minor, unknown, or missing evidence.
- “Every known finding” has no authoritative finding-set continuity. Renaming,
  splitting, deleting, or lowering the severity of a finding can manufacture
  an empty final set.
- Unknowns are fail-open: there is no materiality rule, executable detector,
  polling event, expiry, or failed-trigger disposition preventing a Major from
  being relabelled as an unknown with an event that is never observed.

### Major proposal findings

- Review convergence has no falsifiable stopping predicate and cannot
  distinguish new assurance from same-origin repetition, fixed-prompt
  saturation, or reviewer fatigue.
- One mandatory repair/test chain is type-incorrect for authority,
  provenance, scope, semantic, and non-reproducible external findings.
- The separation between process closure and usability, longitudinal
  operation, and financial effectiveness exists only in prose; no receipt
  field or state transition prevents a governance result from upgrading those
  claims.

The smaller executable successor must reuse the current trust and product
state model, bind an exact `stage_id`, claim ceiling, scope-manifest hash,
trust-model revision, and finding-set hash, preserve finding
alias/supersession/severity history, select evidence profiles by finding type,
make material or unmonitored unknowns blocking, and group reviewers by evidence
lineage. Convergence may stop additional review; it must never produce a pass
by itself. Product use and financial effectiveness remain separate prospective
evidence gates.

At minimum, a future verifier must reject finding rename/split/delete/downgrade,
Major-to-unknown laundering, deferred Minor at a strict freeze stage,
same-origin/no-verdict convergence inflation, cross-candidate or
cross-trust-model receipt reuse, and any governance receipt that upgrades
usability, longitudinal validation, or investment effectiveness.

The proposal therefore remains:

```text
status=candidate_pending_independent_challenge
current_effect=none_beyond_candidate_backlog_and_review_scope
promotion=blocked
```

## Bounded project-method observation

The exact candidate completed all 13 project-method checks that were eligible
to run. The runner remained blocked on:

```text
CTX-02
VER-07
OPS-08
ECO-03
```

Those are later `WP-METHOD-INTEGRATION` failures and are not relabelled as a
foundation regression.

The complete governance regression reported:

```text
discovered=498
planned=498
loaded=498
started=476
successful=436
coverage_complete=false
status=fail
source_same=true
active_after=0
temp_removed=true
```

The failure population includes stale frozen hashes and locators, missing
research review artifacts, the stale `WP-METHOD-INTEGRATION` controlled
snapshot, and historical candidate Git identities absent from isolated
fixtures. This is affirmative evidence that the overall project is not
complete. It does not erase the positive, bounded foundation tests above.

## Required closure evidence

Review F remains open until a later exact candidate:

1. rejects the decoy-repository environment-redirection probe before any seal
   state change;
2. binds cleanly discovered repository root, Git directory, and project prefix
   to the real project location;
3. explicitly targets that authority for every later Git observation;
4. retains all Review C, D, and E Git and runtime regressions;
5. commits the two direct `RECORDER-908` legacy recovery regressions;
6. passes the real nested-parent positive seal path;
7. receives a new candidate-bound independent Git-authority challenge with an
   explicit verdict.

The blocked proposal may not be promoted merely because these foundation
conditions later pass.
