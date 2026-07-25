# RS-05 boundary and execution-status receipt

- receipt_updated_at_utc: `2026-07-25T16:35:07Z`
- author_scope: read-only Git/GitHub checks plus RS-05 evidence recording; no workflow execution or modification.

## Preregistration boundary

- required_commit: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- `git rev-parse --verify <required_commit>^{commit}`: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- commit_committer_time: `2026-07-25T09:13:44-07:00`
- commit_committer_epoch: `1784996024`
- commit_utc: `2026-07-25T16:13:44Z`
- commit_subject: `preregister investment research refresh r8`
- commit_tree: `7cb2268e3715102c540f50f78ab0829dc0eaaeb6`
- preregistration_file: `MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R8_2026-07-25.json`
- required_and_observed_file_sha256: `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8`
- commit_file_git_blob: `0feba2836b8c83adf2bd6e109416bca8072a1c0c`
- working_file_git_blob_at_initial_check: `0feba2836b8c83adf2bd6e109416bca8072a1c0c`
- remote_branch_containing_commit_at_initial_check: `origin/codex/investment-assurance-r7`
- initial_HEAD_before_D1: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- first_counted_retrieval_started_at_utc: `2026-07-25T16:17:56Z`
- temporal_order: `2026-07-25T16:13:44Z < 2026-07-25T16:17:56Z`
- initial_boundary_result: `pass`

## Concurrent branch movement and ancestry

The shared branch advanced through automatic vault-backup commits while multiple agents worked. No commit was reset or rewritten by RS-05.

- observed_HEAD_at_receipt_update: `98bdf382cf34c7cc3ca5f6e889983e51c60e1695`
- `git merge-base --is-ancestor 7824a63... 98bdf382...` exit: `0`

Observed post-preregistration commits that contained R8 evidence and the ancestry exit for each:

| commit | commit time | subject | `7824a63...` ancestor exit |
|---|---|---|---:|
| `1ebc3f3592953cb4fe52821cd551a70921b657fb` | `2026-07-25T09:23:17-07:00` | `vault backup: 2026-07-25 09:23:17` | `0` |
| `9a930cee9915510e01880b96b6f1f2d7be476bd0` | `2026-07-25T09:28:40-07:00` | `vault backup: 2026-07-25 09:28:39` | `0` |
| `98bdf382cf34c7cc3ca5f6e889983e51c60e1695` | `2026-07-25T09:33:58-07:00` | `vault backup: 2026-07-25 09:33:58` | `0` |

`216dde18eefb6e6e26ce3d3082252cc128c6bcd3` is also a descendant (`exit 0`) but the scoped path check showed no RS-05 evidence file in that commit.

The final RS-05 raw report and newest evidence files were not yet all contained in a Git commit when this receipt was written. The integration agent must rerun the ancestor check on the final evidence commit; this author does not predeclare that future check as passed.

## Git content anchor and workflow design

- boundary_workflow_path: `.github/workflows/investment-discipline-assurance.yml`
- boundary_workflow_git_blob: `e7950d06e41f149a7e5b6ed070d2a40f3bf74c2a`
- working_file_git_blob_at_check: `e7950d06e41f149a7e5b6ed070d2a40f3bf74c2a`
- workflow_file_sha256: `39f34cd20de4a2612c3c1a333e9e361e57b6bc19b9a5877fb3737024c55d42`
- workflow_declared_triggers: push to `main` for the project/workflow paths, plus `workflow_dispatch`
- workflow_declared_runner: `ubuntu-latest`
- workflow_declared_attestation_action: `actions/attest@36051bcae73b7c2a8a6945a48cbf80953c6baa35`
- workflow_read_boundary: Presence and pinned action references establish only a design/configuration snapshot. A workflow file is workflow-controlled input and is not an execution receipt, hosted-runner proof, or semantic-correctness proof.

## Live GitHub read-only receipts

### Boundary commit

- retrieved_at_utc: `2026-07-25T16:31:04Z`–`2026-07-25T16:31:05Z`
- exact_bytes: `github_commit_7824a63_2026-07-25.json`
- API sha: `7824a63afe923d5e38c0c6f06577a7d1adfb81d5`
- verification.verified: `false`
- verification.reason: `unsigned`
- verification.signature: `null`
- verification.payload: `null`
- verification.verified_at: `null`
- interpretation: supports `content_snapshot_anchor`; does not prove author/reviewer identity.

### Exact-SHA Actions runs

- retrieved_at_utc: `2026-07-25T16:31:04Z`
- exact_bytes: `github_actions_runs_head_7824a63_2026-07-25.json`
- API total_count: `0`
- API workflow_runs: `[]`

### Registered workflows visible through repository API

- retrieved_at_utc: `2026-07-25T16:31:04Z`
- exact_bytes: `github_actions_workflows_2026-07-25.json`
- API total_count: `0`
- API workflows: `[]`

### Execution-state conclusion

- actual_workflow_run_for_boundary_commit_observed: `no`
- actual_artifact_observed: `no`
- actual_attestation_bundle_observed: `no`
- actual_positive_policy_verification_observed: `no`
- actual_negative_policy_test_observed: `no`
- allowed_state: `github_issued_workflow_provenance: designed_not_observed`
- forbidden_inference: The boundary commit's workflow file cannot be used to claim that GitHub ran it, that the artifact came from a hosted runner, that any predicate is true, or that machine assurance passed.
