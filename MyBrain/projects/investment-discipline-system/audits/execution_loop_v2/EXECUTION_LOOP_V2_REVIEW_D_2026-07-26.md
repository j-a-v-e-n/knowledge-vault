# Execution Loop V2 Review D

## Binding and verdict

- Candidate commit:
  `7794e74403b2a7a29444ab555311bcbf045edd29`
- Candidate tree:
  `f074e27883f461ca8954ec4821c54a0c08d5992a`
- Primary counterexample reviewer: main agent, clean candidate checkout
- Independent recorder/recovery reviewer:
  `agent:019f9c92-fdc0-74d2-9300-d6d198bf2724` (`Nietzsche`), read-only exact
  commit review
- Independent state-machine reviewer:
  `agent:019f9c9a-750d-76c1-beea-00cd6bba991b` (`Maxwell`), detached-clone
  read-only exact commit review
- Final verdict: **blocked**

This review grants no completion, freeze, authentication, or product-quality
claim. The positive targeted suite is retained as bounded evidence only.

## Review C closures retained only inside the existing fixture boundary

The candidate closes the original reproductions for the seven Review C
findings within its existing fixture and cooperative local-filesystem
boundary:

- terminal state and receipts are bound to an exact candidate commit plus a
  later review commit and named Git review ref;
- run and finalization intents precede process launch, while observed outcomes
  precede ledger construction;
- pre-journal transaction staging is recoverable;
- fan-in predecessors can complete independently and activate a successor only
  after all dependencies complete;
- the durable operation remains present through core replacement, state-view
  refresh, and ordinary verification;
- acceptance checks compare controlled claims before and after execution;
- attempt timestamps cannot move backward across the hash chain.

The independent review below reopens parts of `REC-11`, `REC-12`, and `REC-17`
under real parent-repository layout, candidate-index divergence, a live child
at recorder termination, and cross-stage time rollback. Therefore the list
above is not a closure claim for the real project.

The candidate passed the 112-test targeted suite, compileall, Ruff, state-view
freshness, and the no-live boundary checks before this review. Those results do
not close the new counterexamples below.

## Open critical findings

### `D-CRIT-PARENT-REPOSITORY-GIT-PATH` (`REC-11`)

The real project is a subdirectory of the knowledge-vault Git repository.
`git_json()` invokes `git show <commit>:<project-relative-path>`, but Git
interprets that path from the repository top level. The isolated recorder
fixture runs `git init` at the project root, so it masks the mismatch.

The independent reviewer confirmed:

```text
git show 7794e744...:.work_packets/packets/WP-METHOD-RUNTIME-FOUNDATION.packet.json
exit=128
fatal: the file exists under
MyBrain/projects/investment-discipline-system/.work_packets/...
but not at the requested repository-root path
```

The real transition reaches `candidate_complete` but `seal_packet()` fails
before creating its operation WAL, leaving the successor pending. Every Git
blob lookup must prepend the canonical `git rev-parse --show-prefix` value, and
the regression fixture must place the project inside a parent repository.

### `D-CRIT-CANDIDATE-CONTROLLED-CONTENT` (`REC-11`)

The seal checks candidate packet, ledger, and receipt metadata but does not
recompute each `bounded_write_paths` claim from the candidate Git tree. An
index/working-tree split can therefore place byte set `B` in the candidate
commit while acceptance and the current working tree observe byte set `A`.
Because the metadata still describes `A`, the untested candidate `B` can be
sealed.

Candidate Git blobs, trees, absent paths, symlinks, and special entries must be
reconstructed under the real repository prefix and compared exactly with the
latest accepted controlled snapshot.

### `D-CRIT-OUTCOME-SNAPSHOT-BINDING` (`REC-18`)

The durable run outcome contains the child exit code and output digests, but it
does not contain the controlled-file snapshot observed when that child ended.
Recovery obtains a new snapshot later and treats it as if it belonged to the
already-finished command.

Reproduction on an isolated copy:

1. record unresolved failure `REC-01`;
2. run a successful child that changes no controlled file and interrupt after
   the process outcome is durable;
3. change `src/recorder-target.txt` after the outcome;
4. recover the pending operation.

Observed result:

```text
status=resolved
failure_after=[]
resolved=['REC-01']
added_paths=['src/recorder-target.txt']
verification=valid
```

The later file change is therefore misattributed to the earlier command and can
manufacture both supporting evidence and resolution. The process outcome and
the controlled snapshot must be captured in one durable outcome envelope.
Recovery must compare that snapshot with current claims; divergence must
preserve every prior failure and record an explicit blocked transition.

### `D-CRIT-PRECOMMIT-SEMANTIC-VALIDATION` (`REC-19`)

Caller-controlled transition data is written before the proposed attempt is
proved valid. An append with malformed failure and root-cause identifiers
writes the invalid attempt, then post-write verification fails. The operation
remains pending over a core state that the built-in recovery path cannot make
valid.

Observed result:

```text
raised=RecorderError
pending_operations=1
verification=invalid
error=attempt blocker is invalid
```

The recorder must validate caller input before creating a durable operation and
must validate the complete proposed attempt chain before planning any
replacement. A child outcome that cannot support the requested disposition
must be retained as an explicit open failure, rather than committed as an
invalid attempt or silently discarded.

## Open major findings

### `D-MAJOR-LIVE-CHILD-RECOVERY` (`REC-12`)

If the recorder is terminated while its child is still running, recovery sees
a durable intent without an outcome and records an indeterminate block.
However, the child has no durable process-group identity and can continue
running after the operation is retired. A delayed child write then makes the
new blocked ledger stale with no pending operation left to reconcile it.

The recorder must launch an owned process group, durably record its identity,
and on recovery first prove that the child has terminated or terminate and
reap the owned group. Only then may it capture the final controlled snapshot
and retire the operation.

### `D-MAJOR-PRIOR-FAILURE-PRESERVATION` (`REC-20`)

When a caller asks a nonzero run to resolve prior failures, the recorder adds
`RECORDER-901` but uses the caller's requested after-set instead of unioning it
with the prior unresolved set. In the isolated fixture, prior failure
`REC-01` disappears from the proposed after-set. Post-write validation then
detects unsupported resolution, but only after the invalid ledger is already
committed and the operation is left pending.

Failed and indeterminate process observations cannot prove earlier failures
resolved. Their after-set must include every prior unresolved failure, every
new caller-declared failure, and the recorder failure that explains the
observation.

### `D-MAJOR-ACCEPTANCE-DEADLINE` (`REC-21`)

`run` has an explicit timeout, but packet finalization invokes each acceptance
command without one. A hung acceptance child can hold the global operation and
packet locks indefinitely, preventing both progress and normal recovery.

Every acceptance process needs a deterministic upper bound. Timeout must
produce a durable observed exit `124` and an explicit failed-acceptance
transition; it may not be inferred as success or allowed to hang forever.

### `D-MAJOR-ACCEPTANCE-CHRONOLOGY` (`REC-17`)

Execution-attempt time is clamped against the prior attempt, but finalization
reads the wall clock directly. The verifier checks each acceptance interval
internally and does not require the first check to start after the latest
resolved attempt or each later check to start after the prior check.

Finalization must clamp the first check to
`latest_attempt.ended_at`, clamp each later check to the previous
`ended_at`, and the verifier must enforce the same cross-stage sequence.

## Project-wide regression evidence

The complete governance regression ran against the clean candidate and
reported:

```text
discovered=480
successful=418
coverage_complete=false
status=fail
source_same=true
active_after=0
temp_removed=true
```

The failure population includes stale frozen-test hashes, stale governance
locators, missing research review artifacts, a stale
`WP-METHOD-INTEGRATION` controlled snapshot, and old candidate Git identities
that are absent from isolated fixtures. These are not reclassified as
foundation regressions, but they are affirmative evidence that the overall
project is not complete and must remain blocked at the later method-integration
and assurance layers.

## Required closure evidence

Review D remains open until a later exact candidate demonstrates all of the
following:

1. a durable process outcome contains the exact controlled snapshot observed
   at outcome time;
2. post-outcome divergence produces a current, explicit blocked record and
   cannot resolve any prior failure;
3. malformed caller input leaves all project files and operation directories
   unchanged;
4. nonzero and indeterminate runs preserve the full prior failure set;
5. a requested resolution without newly observed supporting evidence becomes
   a valid explicit recorder failure before any commit;
6. acceptance timeout is bounded and durably recorded;
7. real parent-repository Git paths are used and candidate controlled bytes
   exactly match the accepted snapshot, including tree and absent-path cases;
8. recovery terminates or reaps a still-running recorder-owned child before
   recording its final snapshot and retiring the operation;
9. acceptance timestamps are nondecreasing from the resolved attempt through
   every check;
10. the ordinary verifier and operation-aware verifier still produce identical
   receipts after successful retirement;
11. all prior Review C regressions remain green.

The independent reviewer ran both current execution-loop test modules:

```text
Ran 58 tests in 21.612s
OK
```

This is positive regression evidence only. It also demonstrates that the
existing suite did not cover parent-repository path resolution,
index/working-tree candidate divergence, or a child still alive when the
recorder is terminated.

The second independent reviewer separately reproduced the precommit-invalid
state, outcome/snapshot misattribution, prior-failure loss, and unbounded
acceptance process in a detached clone. Its baseline was:

```text
Ran 58 tests in 24.926s
OK
execution freshness current: 6 ledgers
```

Both independent verdicts were `blocked`. Neither reviewer modified the exact
candidate under review.
