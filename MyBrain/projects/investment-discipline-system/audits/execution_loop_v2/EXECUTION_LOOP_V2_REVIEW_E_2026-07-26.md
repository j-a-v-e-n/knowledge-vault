# Execution Loop V2 Review E

## Binding and verdict

- Candidate commit:
  `54e3e5aba0ecebc61fa78c3306b028be642a612d`
- Candidate tree:
  `2955039f5dd4360763fb9803ab317add85310ff0`
- Primary counterexample reviewer: main agent, clean exact candidate checkout
- Independent adversarial reviewer:
  `agent:019f9cb7-c122-7eb0-aeec-5a6e0bcdeccf` (`Bacon`), read-only
  exact-commit review
- Additional independent reviewer:
  `agent:019f9cb7-9b7c-7c30-b8d0-23eb793685d0` (`Lagrange`);
  the review was interrupted after it failed to return within the bounded
  review interval and therefore produced **no verdict**
- Final verdict: **blocked**

This review grants no completion, freeze, authentication, or product-quality
claim. The interrupted reviewer is not counted as support for either
acceptance or rejection.

## Positive evidence retained within its tested boundary

The candidate passed the 123-test targeted execution-loop suite, compileall,
Ruff check and format checks, project-state freshness, execution freshness,
and the no-live boundary before this review. The independent reviewer also ran
the two current execution-loop modules:

```text
Ran 69 tests
OK
```

The candidate correctly retained the Review D fixes for the real
parent-repository prefix, file and absent-path candidate claims,
index/working-tree divergence, symlink and Git-link rejection, candidate and
review ancestry, acceptance chronology, bounded output, bounded acceptance
execution, and prior-failure preservation.

Those positive observations do not close the counterexamples below.

## Open critical findings

### `E-CRIT-NESTED-TREE-ORDERING` (`REC-11`)

The worktree tree digest and candidate Git tree digest enumerate the same
legal nested tree in different orders. The worktree side follows
directory-first `os.walk` order at every directory, while the Git side hashes
raw `git ls-tree -r -t` order.

The independent reviewer reproduced one legal nested tree in a parent
repository:

```text
worktree=b82084aa9762b13fd4d8a5dd87e526018a3adbe64fdffb3b98401ea8fc042e1e
candidate=a806e2cef3f66006fcd785ee6113f9605fa8891744ef0b3796aaca38fd90ffa9
```

The real foundation packet contains a tree claim, so an honest exact candidate
can be rejected at sealing time. Both sources must use one shared,
deterministic directory-first traversal without changing the already-recorded
worktree algorithm.

### `E-CRIT-SEMANTIC-REQUEST-PREVALIDATION` (`REC-19`)

An explicit request for `status_after=resolved` with a nonempty
`failure_after` passes the shape-only request validator. The recorder then
writes a durable operation and outcome before the core rejects the
contradiction.

Observed result:

```text
raised=RecorderError
pending_operations=1
verification=invalid
error=resolved status requires an empty failure set
```

The same contradiction also exists when `failure_after` is omitted and the
prior ledger still contains unresolved failures. Both forms must be rejected
before a durable operation is created. An explicit empty after-set remains a
valid resolution request but still requires newly observed supporting
evidence.

### `E-CRIT-FORCED-STOP-COMMIT` (`REC-19`)

The recorder detects the third consecutive no-progress attempt only after
constructing the proposed open attempt. It raises instead of mechanically
turning that exact attempt into the required final blocked transition.

Observed result:

```text
third_request=open
raised=RecorderError
pending_operations=1
verification=invalid
error=this attempt reaches a stopping threshold and must be recorded as the final blocked transition
```

A forced-stop rule is recorder-owned policy, not caller-owned input. The
recorder must persist the mechanically derived blocked disposition before
hashing and commit it atomically, leaving no pending operation.

### `E-CRIT-INHERITED-LIVENESS-LOCK` (`REC-12`)

The bootstrap process marks its liveness-lock descriptor inheritable and then
executes the target command in place. The target therefore owns the only
liveness proof and can close it while continuing to run.

The main-agent reproduction used a target that closed descriptors `3..255`,
wrote a readiness marker, slept, and then changed a controlled file. After the
main recorder was killed, recovery observed the lock as free, retired the
operation as indeterminate, and the target wrote later:

```text
recovered=[operation_id]
controlled_file=late
verification=invalid
error=latest controlled snapshot is stale
```

The bootstrap must remain a supervisor that alone holds the lock while it
waits for the target process. The target must run inside the owned process
group without inheriting the sole lock descriptor. Recovery must terminate
that group before recording the final snapshot. The remediation challenge
must also use a target that ignores `SIGTERM`: the supervisor must retain the
lock through the grace interval and recovery must escalate to an
unignorable group termination before retiring the operation.

## Open hardening finding

### `E-MAJOR-GIT-REPLACEMENT-AND-PATHSPEC` (`REC-11`)

Git observations inherit replacement-object behavior from the surrounding
repository, and the controlled-path lookup does not request literal pathspec
semantics. No replacement attack was needed for the critical findings above,
but candidate authority should be independent of local `refs/replace`, and
packet-controlled paths should not acquire glob semantics.

Every verifier-owned Git subprocess must disable replacement objects, and
tree lookups must use top-level literal pathspecs. The local review tag remains
explicitly unauthenticated and is not upgraded by this hardening.

## Bounded project-method observation

The clean exact candidate completed all 13 checks that were eligible to run in
the project-method acceptance runner. The remaining blockers were:

```text
CTX-02
VER-07
OPS-08
ECO-03
```

Those are later `WP-METHOD-INTEGRATION` blockers. They are not reclassified as
foundation regressions and remain affirmative evidence that the overall
project is not complete.

## Required closure evidence

Review E remains open until a later exact candidate demonstrates all of the
following:

1. one legal nested tree with sibling files produces exactly the same
   worktree and candidate Git digest;
2. explicit nonempty and inherited nonempty resolved requests leave every
   project file and operation directory unchanged;
3. the first forced-stop prefix is atomically recorded as the final blocked
   transition and leaves no pending operation;
4. a target that closes every nonstandard descriptor and ignores `SIGTERM`
   cannot release the supervisor-held liveness lock;
5. recorder termination followed by recovery kills that target before any
   delayed controlled write;
6. Git replacement objects cannot alter verifier observations and tree
   pathspecs are literal;
7. all Review C and Review D regressions remain green;
8. a new independent reviewer challenges the exact remediated candidate and
   returns a bounded, explicit verdict.
