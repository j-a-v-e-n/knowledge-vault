# 投研纪律系统｜Ledger R1 干净窗口接力包

状态：`NEXT_THREAD_RECOVERY_INPUT`。本文件只负责接力，不替代 Git、Mission Graph、Product Graph、节点合同或独立审查。

## 1. 新窗口的任务

从当前产品节点继续完成个人、本地优先、paper-only 的投研纪律系统，不从头重做，也不继续扩建已经退出关键路径的治理基础设施。

当前权威路线：

- workstream: `STREAM-PRODUCT-BUILD`
- child graph: `IDS-PERSONAL-PAPER-PRODUCT-CAPABILITIES-V1`
- subject/node: `CAP-LEDGER-REVIEW-INTEGRITY`
- work: `WORK-LEDGER-SQLITE-VERTICAL-SLICE-R1`
- obligation: `OBL-LEDGER-SINGLE-SQLITE-AUTHORITY`
- objective: `implement_one_bounded_SQLite_authority_atomic_paper_commit_restart_replay_review_and_migration_candidate`

服务的最终结果没有变化：AI 研究和建议，Javen 保留最终投资决策；个人、本地优先、paper-only；不接真实资金、券商或自动实盘；AI 不修改用户风险规则。

## 2. 精确工作区

继续使用现有独立 worktree，不在 main 上重做：

```text
/private/tmp/investment-ledger-r1.SUwL0q
```

项目目录：

```text
/private/tmp/investment-ledger-r1.SUwL0q/MyBrain/projects/investment-discipline-system
```

Git 状态：

- branch: `codex/ledger-implementation-r1`
- HEAD: `931817a0251bef1ad3975afee7ad06f59aedf06a`
- tree: `b21ea09a18c9b00ef2f1e4fec09e2ed6d8810ae9`
- index: clean at handoff
- ordinary branch and refs must not be rewritten merely to make recovery easier

Exactly four moving files existed at handoff:

| Path | SHA-256 |
|---|---|
| `prototype/ledger_sqlite.py` | `fd6f0ae3d8a644abd2b36ad7af89e73090b52535a246a0a4aa7b854d9f9a397a` |
| `prototype/migrations/0002_ledger_next.sql` | `09797ed1b0236a7baf7d75acc47d24f9af2f949b5e0881eca6b0ad54928692f3` |
| `prototype/tests/test_sqlite_ledger.py` | `4b99f1d8282e068159954e36e25ca9e1ccae0a239882dec1ab122bf2748c7b85` |
| `prototype/workflow.py` | `04c579de110c6fd06afaa5952b212b659656348c8772e1a9c7ba3fb4b33ac480` |

Observed diff size was `4 files changed, 3788 insertions(+), 268 deletions(-)`. This is only size evidence, not correctness evidence. Do not discard, reset, or overwrite these bytes.

## 3. Startup preflight

Read, in this order, from the worktree above:

1. `AGENTS.md`
2. `PROJECT_CHARTER.md`
3. `governance/PROJECT_MISSION_GRAPH_V2.json`
4. `PROJECT_GRAPH.md`
5. `governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
6. `DECISIONS.md`
7. `EVIDENCE_GOVERNED_AI_SYSTEM.md`
8. `governance/LEDGER_IMPLEMENTATION_HANDOFF_V1.json`
9. `governance/LEDGER_COMPONENT_DECISION_V2.json`
10. `governance/evidence/LEDGER_IMPLEMENTATION_8F3A99C.deterministic-receipt.json`

Then run read-only:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_project_mission_graph.py check
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_project_mission_graph.py check-view
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/verify_project_mission_graph.py check-work \
  --work-id WORK-LEDGER-SQLITE-VERTICAL-SLICE-R1 \
  --node CAP-LEDGER-REVIEW-INTEGRITY \
  --obligation OBL-LEDGER-SINGLE-SQLITE-AUTHORITY
```

At handoff all three passed. Any later mismatch stops implementation and triggers fact recovery; `STATUS.md`, `TASK_BOARD.md`, `RECOVERY_POINTER.md`, old UI `blocked`, or this handoff cannot override Mission Graph.

## 4. 已有过硬产出

- Commit `8f3a99c2d7961008b1007f92edab4b32c92a0af2`: bounded SQLite paper-ledger candidate.
- Commit `931817a0251bef1ad3975afee7ad06f59aedf06a`: bound deterministic implementation evidence.
- At commit `8f3a99c…`, the checked-in receipt records a bounded `157`-test command PASS, three consecutive `18`-test Ledger runs PASS, ruff PASS, no-live verifier PASS, dependency-boundary PASS, Product/Mission Graph PASS, and full legacy governance verifier FAIL without relabelling. Those numbers apply only to that fixed candidate and receipt, not automatically to the four current moving files.
- Current Mission Graph checks passed again immediately before this handoff.
- A static owner inventory and reverse-required-CI closure were produced outside the repo to expose hidden owners and stale assurance pins.

## 5. 当前真正的未闭合根因

The four moving files do not yet prove the single-SQLite authority cutover is complete.

Read-only fact closure found:

- the original handoff scope cannot close its own single-SQLite exit condition;
- `prototype/discipline_system.py` owns `record_paper_workflow`, `record_paper_review`, and `AppendOnlyLedger`, but was omitted from the later four-file moving scope;
- `prototype/run_real_data_case.py` also calls `record_paper_workflow` and was omitted;
- four direct legacy runners still need an exact terminal disposition;
- the receipt same-key fast path trusts stored JSON without full reconciliation;
- three broad `sqlite3.OperationalError` catches misclassify unrelated failures as `LedgerBusy`;
- `RunManifest` is used only in tests, leaving `REQ-CORE-003` open.

These are candidate facts, not permission to broaden the write set blindly. Recompute them from source before editing.

Supporting temp evidence directory:

```text
/private/tmp/ledger-cutover-direction-v2.uQSn8g
```

Important files:

- `LEDGER_CUTOVER_OWNER_INVENTORY_V1.json` — `9116` bytes, SHA-256 `a054276ae0857e43e2805fdabc280a55adb8ebbc0c3112fb98cad0fc3196d1f0`
- `LEDGER_REQUIRED_CI_REVERSE_CLOSURE_V1.json` — `93176` bytes, SHA-256 `2c71f28c3c1cb7c2c19ec4dad18d7c4e3331aa353f7222f84761b96fc222ec9a`
- `LEDGER_SCOPE_DIRECTION_PROPOSAL_V3.json` — `10860` bytes, SHA-256 `0d868b74ad84e825f1e42b06f25bb2a4eaca9ac706cafb8cacda364bbfd4d6cc`; rejected because it incorrectly treated a live required-CI component registry as history
- `CURRENT_PRODUCT_ASSURANCE_SUCCESSOR_PROPOSAL_V2.json` — `14696` bytes, SHA-256 `9ca553dbe59228eb82bf2b290a6c1af3c8573135656d3efe502bc12d0e733236`; rejected/incomplete, not an implementation plan
- `GOVERNANCE_TEST_SUBJECT_CLASSIFICATION_V2.json` — `271632` bytes, SHA-256 `4e570521c34cc72326b77c0d93933012435dadc7dfe889fe67ec552c03a6abf8`; static heuristic only
- `GOVERNANCE_TEST_SUBJECT_DISPOSITION_V1.json` — `14589` bytes, SHA-256 `9a30f23a90c04b27265df97bdd73ec25cc4cae0534b2127edf80f9ef76af168a`; builder candidate superseded by the direction synthesis below

## 6. 方向回溯结论

Do not continue building a global `CURRENT_PRODUCT_ASSURANCE_V2` before finishing the Ledger node.

Why:

1. Mission Graph explicitly selects the Ledger vertical slice.
2. Product Graph marks `METHOD-GOVERNANCE-CLOSURE` as `stalled_off_product_path`; re-entry requires a current product obligation that cannot otherwise close.
3. The fixed Ledger receipt intentionally excludes the failing full legacy governance gate and refuses to relabel it.
4. Three fresh read-only reviewers showed that old tests contain three different classes which must not be conflated:
   - exact Ledger-node controls needed now, such as dependency/no-live, exact candidate identity, bounded delta, receipt binding, migration/reconciliation, and fresh independent review;
   - useful product-release controls to migrate only when their owning future node is active, such as PIT, same-bar, conditional field use, research release, and broader assurance;
   - exact old design-freeze machinery that remains historical replay only.
5. Therefore “all 32 governance modules must become one new current gate” is the wrong abstraction. Reuse a control only when the current Ledger contract names the protected fact.

This does not discard the prior work. It converts it into a negative result and future migration backlog, preventing another multi-day governance detour.

## 7. 新窗口的唯一下一动作

First reconstruct an exact Ledger cutover write-set from:

- current Graph obligation;
- `LEDGER_IMPLEMENTATION_HANDOFF_V1.json` exit conditions;
- `LEDGER_COMPONENT_DECISION_V2.json` claims and attack requirements;
- the current four moving files;
- `LEDGER_CUTOVER_OWNER_INVENTORY_V1.json` and source inspection of `discipline_system.py`, `run_real_data_case.py`, all direct legacy runners, tests, and declared paper entrypoints.

Then choose the smallest route that closes one-SQLite authority. Do not implement a generic assurance framework first. Before changing files, record the exact bounded write set and test/review obligations. After implementation:

1. run node-specific normal, negative, restart, retry, replay, reconciliation, migration, no-live, dependency, Graph, and full prototype-discovery checks;
2. freeze one exact commit/tree/project-subtree candidate;
3. obtain one fresh non-builder exact-object correctness review and one direction check if a Graph trigger fired;
4. only then transition the Ledger node or backtrack to the named upstream design decision.

## 8. Anti-drift rules for the new window

- Do not restart the four-day investigation.
- Do not treat this handoff summary, test count, builder self-check, Claude/Codex opinion, or old green CI as acceptance.
- Do not revive `METHOD-GOVERNANCE-CLOSURE`, custom protocol-definition work, backup/genesis experiments, or global assurance unless the current Graph obligation proves they are necessary.
- One root correction plus one fresh review; recurrence of the same root triggers backtrack, not more fields.
- Use Claude/Sonnet or other agents for bounded code construction and independent review after the exact scope is fixed; the lead owns Graph alignment and integration.
- No real or shadow trading, broker, funds, credentials, provider-account action, risk-rule change, external publication, or paid action.
- No user question is presently required. Continue autonomously until a genuine external authority or personal-value decision is needed.

## 9. Handoff ceiling

`RECOVERY_INPUT_ONLY`.

This file grants no repository write, commit, review PASS, Ledger completion, product-node transition, paper execution, backup, restore, deployment, account, credential, provider, funds, risk, or financial authority. Existing user authorization permits normal bounded local project work; exact project controls still govern each action.
