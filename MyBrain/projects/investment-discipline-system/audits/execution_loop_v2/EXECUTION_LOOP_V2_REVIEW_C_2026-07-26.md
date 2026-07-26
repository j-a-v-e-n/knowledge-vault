# Execution Loop V2 Review C

## Binding and verdict

- Candidate commit:
  `fcf2e6146fa2448c2c8b488fb4887bb2cf22a761`
- Candidate tree:
  `c81ed56418d1558af56b3aa5e2307ec25c60979f`
- State-machine and authority reviewer:
  `agent:019f9c45-ff20-7221-a783-818f6b86d8a7` (`Harvey`)
- Recorder and transaction reviewer:
  `agent:019f9c46-3602-70e2-848b-2049c7ffedc0` (`Sartre`)
- Reviewer access: read-only; both reviewers reported a clean candidate
- Final verdict: **blocked**

This review supersedes no prior evidence and grants no completion, freeze,
authentication, or product-quality claim.

## Findings closed from Reviews A and B

The reviewers independently confirmed that the candidate closes the following
earlier defects within the declared cooperative local-filesystem boundary:

- current top-level governance, project-method acceptance, state derivation,
  and no-live checks use V2 work/execution authority; V1 is fixed history;
- pending ledgers contain exactly one baseline observation;
- failure and evidence state is continuous across attempts;
- every historical no-progress prefix and the retry budget are evaluated, and
  blocked is absorbing;
- exact ledger discovery and derived state-view sidecars avoid the earlier
  self-reference;
- all three human-facing current-state files are whole-file canonical;
- the recorder provides per-packet and global transaction locks, expected-tail
  compare-and-swap, process-captured run results, explicit passive self-report,
  preservation of existing attempts, and journaled roll-forward after a
  durable journal exists;
- the migration audit preserves the raw hashes of the invalid candidate
  ledgers and creates no completion claim.

## Open critical finding

### `C-CRIT-TERMINAL-ANCHOR`

`terminal_completion` and every local receipt it references remain inside one
coherently rewritable local set. In a temporary finalized fixture, the reviewer
changed an execution-receipt output digest, recomputed the terminal receipt
digest, rewrote the ledger, and refreshed the canonical state views. The work
verifier returned `pass`, the execution verifier returned `valid/current`, and
the state views became fresh again without reopen or successor supersession.

Internal hashes therefore establish current consistency, not historical
immutability. A complete packet must compare its terminal digest to an
authority that cannot be regenerated from the same local sidecar set. The
minimum acceptable boundary is a candidate-bound immutable Git/remote review
anchor, or an explicitly verified successor binding to the predecessor
terminal. A regression must change the receipt, terminal, ledger, and views
coherently and still obtain rejection.

## Open major findings

### `C-MAJOR-RUN-OUTCOME-WAL`

`run` and `finalize` execute child processes before creating durable operation
state. If the recorder exits after a child produces an exit code and output but
before the update transaction, the ledger can remain `valid/current` while the
observed outcome disappears. A nonzero run paired with an invalid caller
disposition is also executed before being discarded.

A durable operation intent must precede process launch. Process outcome must be
persisted before ledger construction. Recovery must either commit the durable
outcome or record an explicit indeterminate/blocked result; it may not silently
return to a green pre-operation state.

### `C-MAJOR-PREJOURNAL-RECOVERY`

The recorder stages payloads before writing `journal.json`. A process exit
after staged bytes are durable but before the journal exists leaves the
verifier fail-closed, while built-in recovery cannot classify or remove the
orphan transaction and all later writes remain blocked.

The prepare state must be durable before staging. Recovery must safely discard
a verified pre-commit prepare transaction or roll forward a durable commit
journal.

### `C-MAJOR-FANIN-ACTIVATION`

`finalize_packet` requires every declared successor dependency to be complete
before the current predecessor can complete. In the current fan-in graph,
multiple branches symmetrically declare the same freeze successor. The first
branch to finish cannot finish because the other branches are incomplete, so
the graph deadlocks.

Predecessor completion must always be allowed when its own contract passes.
Successor activation is derived only after all dependencies are complete; an
earlier predecessor completion leaves the successor pending.

### `C-MAJOR-POSTWRITE-COMMIT`

The replacement journal is deleted before post-write verification and before
the three state views are refreshed. An exit in this window can leave a valid
new ledger with stale human-facing views and no recoverable transaction.
Recovery without an explicit verification option does nothing.

The durable operation must remain pending through semantic verification and
canonical view replacement. Recovery must finish these phases idempotently
before clearing the operation.

### `C-MAJOR-ACCEPTANCE-MUTATION`

An acceptance command can modify a bounded file and return success.
Finalization currently creates receipts from a new checkpoint snapshot while
the terminal anchor still references the previous execution attempt snapshot.
The invalid complete state is committed, the journal is removed, and only then
does the post-write verifier detect stale claims.

Finalization must compare controlled claims immediately before and after every
acceptance run and before commit. A modifying acceptance check must fail
without committing completion.

### `C-MAJOR-TIME-ORDER`

The verifier checks each attempt interval internally but does not require a
later attempt to start at or after the previous attempt ended. A wall-clock
rollback can therefore produce a hash-chain sequence whose timestamps run
backward.

Attempt timestamps must be nondecreasing across the chain. The recorder must
clamp a new start to the prior `ended_at` or use an equivalent durable
monotonic sequence rule.

## Verification evidence

The state-machine reviewer reported:

```text
V2 work verifier: pass
V2 execution verifier: valid/current
State views: fresh
86 selected tests: OK
```

The recorder reviewer reported:

```text
10 recorder tests: OK
V2 execution verifier: valid/current
V2 work verifier: pass
```

These positive results are retained as bounded evidence. They do not close the
counterexamples above.
