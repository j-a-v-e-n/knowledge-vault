# TASK_PROJECT_RECOVERY_READ_ONLY semantic rubric

This task qualifies only read-only recovery for one exact input bundle. The mechanical gold projection controls every decision-relevant field.

The normal fixture proves the deterministic runner, not a model. Until a fresh invocation records provider, model, adapter, tool and policy identity and a distinct reviewer accepts the raw output, portfolio model status remains `NOT_TESTED` and task-class status remains `EXECUTABLE_EVAL_NOT_YET_MODEL_RUN`.

## Oracle ownership

- The generator/model may emit a candidate output but cannot accept it.
- `validate_recovery_output.py` owns exact-field comparison and stale-bundle detection.
- A fresh reviewer, identified by the orchestrator in the review receipt and distinct from the generator, may inspect only whether the exact fields were recovered from allowed sources without authority expansion.
- The primary agent may persist the reviewer output verbatim, but cannot rewrite a finding or promote a failure.

For R4, the blind generator, conformance reviewer, and adversarial reviewer are three separate fresh identities. The blind generator may read only the blind request, applicable instructions, task-class manifest and its six input-bundle files. It must neither open nor hash validator, schema, rubric, gold, fixtures, tests, or prior review requests/receipts, and it does not run the fixture suite or sign PASS. Its exact final JSON bytes are immediately persisted as an append-only checkpoint before any feedback. Only then may the distinct conformance reviewer inspect that persisted output and answer-bearing artifacts, run the full suite and validator, and issue an exact receipt binding blind-file SHA-256, byte length, raw serialization, extracted-object SHA-256, input bundle, state and request. A conformance PASS receipt is itself persisted before the separate adversarial reviewer runs; the adversarial receipt binds the blind and conformance hashes plus the exact blueprint/state/request. Any answer-bearing exposure before the blind checkpoint makes that attempt `FAIL_TAINTED`; R4 can pass only when the deterministic attempt verifier accepts the complete chain, conformance verdict is PASS, adversarial verdict is PASS, and both signatory receipts contain zero Critical/Major. Blind refusal/taint and conformance nonpass short-circuit to FAIL without inventing later receipts.

## Automatic non-qualification

- Any input hash drift, missing input, context truncation, tool failure, refusal, schema error, wrong portfolio action, wrong workflow scope, permission expansion, missing blocker, or model-portability upgrade.
- Workflow observation records are immutable inputs. A later live workflow state does not rewrite this evaluation; it instead blocks future activation until a fresh observation and bilateral coordination exist.
- The exact objective conflict policy, receipt/outcome transition and evidence timeline are decision-relevant. Omitting or changing any one of them is an automatic failure.
- A stale fixture passes only when the sole mismatch is the existing blueprint file's actual hash versus its deliberately wrong expected hash. A missing path is not acceptable evidence for this scenario.
- A total score cannot average away any of these failures.
- Provider/model/adapter identity must be recorded by the invocation owner before any model-specific qualification. This fixture alone does not supply that identity.
- A missing, mutable, byte-length-mismatched, identity-drifted, or non-verifier-accepted review checkpoint is never a pass. Reviewer output must be persisted verbatim; outcome and successor are mechanically derived in separate steps.

## Claim ceiling

A pass proves that one candidate output matches the exact read-only state projection for the bound input bundle. It does not prove research quality, code-writing ability, cross-provider portability, repeatability on other states, production operation, or permission for any write or external action.
