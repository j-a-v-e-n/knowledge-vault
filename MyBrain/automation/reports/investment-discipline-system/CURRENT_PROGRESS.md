# 投研纪律系统｜固定蓝图与当前指针

> 这是给 Javen 查看进度的只读窗口，不决定路线、不授权执行、不构成验收。

## 这个页面以后怎么变

- **固定蓝图不随日常工作重画。** 下方产品能力节点和依赖来自 `IDS-PERSONAL-PAPER-PRODUCT-CAPABILITIES-V1`。
- **固定交付链不增删步骤。** 今后只移动当前高亮、更新证据和时间。
- 只有项目目标或能力依赖真的改变，形成单独候选、冻结 exact bytes 并通过独立审查后，蓝图结构才可能产生新版本；候选在被接受前对本页蓝图没有任何影响。
- 调试反例、失败根因和历史回溯不再长进主图，只写在本页后面的当前证据或项目 evidence 中。

| 层 | 现在是什么 | 允许怎么变 |
|---|---|---|
| 冻结蓝图 | Mission Graph + Product Capability Graph | 不能按进度原地改写；只能被“冻结且独立审查通过”的新版本替代 |
| 当前指针 | Paper Gate；方向审查已通过，正在构造隔离 Graph candidate | 只随已发生且有证据的状态移动 |
| 隔离候选 | bounded JSON ingress Graph candidate | 可被审查、拒绝或重写；在接受前不能改蓝图、不能启动产品工作 |

## 固定产品蓝图

```mermaid
flowchart TB
    M["项目使命<br/>personal · local-first · paper-only · human-final"]

    M --> PG["CAP-PAPER-GATE-INTEGRITY<br/>纸面风险闸门与唯一状态提交入口"]
    M --> BT["CAP-HONEST-BACKTEST<br/>无未来信息、计成本、基准与留出"]
    M --> DATA["CAP-PUBLIC-DATA-EVIDENCE<br/>公开数据时点快照与修订谱系"]

    PG --> LEDGER["CAP-LEDGER-REVIEW-INTEGRITY<br/>事务化账本、复盘与重启一致性"]
    PG --> HUMAN["CAP-EVIDENCE-AI-HUMAN-DECISION<br/>证据约束 AI 建议与真实人工决定"]

    LEDGER --> WB["CAP-LOCAL-WORKBENCH<br/>个人可持续使用的 calm 本地工作台"]
    HUMAN --> WB
    BT --> WB
    DATA --> WB

    LEDGER --> REC["CAP-RECOVERY<br/>代码与私人运行状态的可验证恢复"]
    WB --> REC
    WB --> DOG["CAP-PAPER-DOGFOOD<br/>真实个人纸面流程的前瞻 dogfood"]
    REC --> DOG
    DOG --> MVP["RELEASE-PERSONAL-PAPER-MVP<br/>个人 paper-only 发布候选"]

    SAFE["永久安全边界<br/>无真实或 shadow 交易<br/>无券商、资金、凭据、provider account<br/>AI 不修改风险规则"] -.约束全部能力.-> M

    classDef mission fill:#e7f5ff,stroke:#1971c2,stroke-width:2px;
    classDef current fill:#fff3bf,stroke:#f08c00,stroke-width:3px;
    classDef blocked fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    classDef boundary fill:#fff3bf,stroke:#f08c00,stroke-width:2px;
    class M,MVP mission;
    class PG current;
    class LEDGER blocked;
    class HUMAN,BT,DATA,WB,REC,DOG pending;
    class SAFE boundary;
```

**固定结构中的当前位置：** `CAP-PAPER-GATE-INTEGRITY`。它没有验收，所以依赖它的 Ledger 仍是 `BLOCKED`。

## 固定交付链与当前阶段

```mermaid
flowchart LR
    E0["E0<br/>方向已选"] --> E1["E1<br/>Mutable 候选"]
    E1 --> E2["E2<br/>预冻结独立审查"]
    E2 --> E3["E3<br/>冻结 exact C"]
    E3 --> E4["E4<br/>Fresh exact review"]
    E4 --> E5["E5<br/>单收据 activation A"]
    E5 --> E6["E6<br/>本机 authority registration"]
    E6 --> E7["E7<br/>check-work → start-work"]
    E7 --> E8["E8<br/>实现与节点验收"]
    E8 --> E9["E9<br/>移动到下一能力"]

    classDef done fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef current fill:#e7f5ff,stroke:#1971c2,stroke-width:3px;
    classDef failed fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class E0 done;
    class E1 current;
    class E2,E3,E4,E5,E6,E7,E8,E9 pending;
```

**当前指针：`E1｜Mutable Graph candidate`。上一次 attempt 在 `E8` 独立审查失败并已完成 terminal-stall；fresh direction review 已通过，现在只构造新的 Graph candidate。**

上一次 attempt 的 E0–E7 证据全部保留，但不能转移给下一次 attempt。新的 E1–E8 必须重新逐步完成；方向审查通过本身也不等于 Graph 已修改或产品已获授权。

固定产品蓝图中的能力指针仍停在 Paper Gate；只有 Paper Gate 通过产品验收后，才会移动到 Ledger。

## 当前事实

- 更新时间：`2026-07-31T09:56:30-0700`
- 当前 Graph 节点：`CAP-PAPER-GATE-INTEGRITY`
- 历史失败工作：`WORK-PAPER-GATE-INTEGER-AUTHORITY-R1`
- 当前义务：`OBL-PAPER-UNIQUE-COMMIT-SINK`
- accepted Graph 阶段：`activated_review_successor`
- 产品候选阶段：`frozen_exact_review_failed`
- terminal-stall Graph 阶段：`accepted_single_receipt_activation`
- fresh direction 阶段：`PASS — Critical 0 / Major 0 / Minor 0`
- 新 Graph candidate 阶段：`mutable_candidate_under_construction`
- 冻结 candidate C：`aebbbbc15c065cc957ed41a581de1fc8d3324519`
- activation successor A：`4517d099f743bdb20b3e73c046f0296202a788fd`
- 冻结产品候选 P：`e1ec606ec245cc136ea32f98b61ab1bb6a3702dd`
- 产品候选 tree：`00b269ce2e0ae0597e3eacd43cdccb071e814453`
- 冻结 terminal-stall 候选 S：`02a2512c7423bad2f90358737aaae052a1bedd46`
- terminal-stall 候选 tree：`74b399b8be66359b875abfd904348bb327a87624`
- S fresh exact review：`FAIL — Critical 0 / Major 1 / Minor 0`
- 冻结 terminal-stall 候选 S2：`59cd60e6c3e549f0e30fa02ea7a28b10e0bdf578`
- S2 tree：`cb1b91592cda0c3497e26d98760ce0878c2d8954`
- terminal-stall 候选写集：要求 `11 paths`；实际 `11 paths`
- S2 fresh exact review：`PASS — Critical 0 / Major 0 / Minor 0`
- terminal-stall activation As：`f5ccd438bfed54fbe618d225431c61f65800b475`
- As tree：`3c8874a77ca601c2611103d3b6aab8ce45782ef4`
- 新方向提案：`DIR-PAPER-GATE-BOUNDED-JSON-INGRESS-R1`
- 新方向提案阶段：`READ_ONLY_DIRECTION_PROPOSAL_PENDING_INDEPENDENT_REVIEW`
- 新方向提案 bytes：`19734`
- 新方向提案 SHA-256：`8d1fe8144b0e23b30e69306fad62952fad99fa4cc1a5eb571071be51a675273f`
- 新方向审查：`DIR-REVIEW-PAPER-GATE-BOUNDED-JSON-INGRESS-R1`
- 新方向审查 receipt bytes：`16680`
- 新方向审查 receipt SHA-256：`5984e94abb3e757aeeadf56c62420f4862268cfca0336b2ed255954a1a1c1d30`
- 新 Graph candidate 允许写集：精确 `12 paths`；prototype 必须不变
- 当前状态：唯一产品 attempt 已冻结并在 fresh exact review 失败；不再拥有继续编辑产品的权限
- 当前运行路线：accepted Graph 显示 `Paper Gate = STALLED`、`Ledger = BLOCKED`、eligible work 为空、execution 未授权
- 历史 registration：原样保留但只绑定旧 attempt，不能转移或复用
- 历史 attempt ref `refs/ids-attempts/paper-gate-integer-authority-r1`：原样保留并继续只指向旧 activation A
- Ledger 产品写集：`NONE_AUTHORIZED`
- Paper Gate 当前产品写集：`NONE_AUTHORIZED`
- E2 最终结论：`GO_FREEZE_C — Critical 0 / Major 0 / Minor 0`
- E4 最终结论：`PASS — Critical 0 / Major 0 / Minor 0`
- S2 预冻结审查：`GO_FREEZE_STALL_C_R2 — Critical 0 / Major 0 / Minor 0`
- 当前动作：在隔离 worktree 构造 mutable `12-path` Graph candidate；完成后先做预冻结独立审查
- 当前工作：`NONE_AUTHORIZED_DURING_DIRECTION_REVIEW`

## 当前方向提案正在证明什么

- 项目级 `AGENTS.md` 已要求：只有冻结且通过独立审查的 Graph 候选，才可能进入后续启动链；Graph 只能版本化修订，不能按进展原地改写。
- 已接受的 stall 只记录已发生的失败分支：Paper Gate `active → stalled`、Product Build `active → stalled`；Graph 拓扑、目标、旧 current work、义务、V3 和 prototype 均未改变。
- 新提案把根因界定为“JSON 入口没有显式结构资源合同，也没有封闭唯一 decoder 的输入失败边界”，而不是整数、reducer 或 SQLite 问题。
- 它比较并拒绝了只 catch `RecursionError`、取消 bytes facade、降低或推迟义务三条路线。
- 被提议的最小方向是：保留单一 canonical bytes authority，在解码前做非递归的 bytes、nesting、structural-token preflight，并只在 exact loader 边界归一化输入导致的普通解析失败。
- fresh direction review 已通过，但只允许构造一个新的隔离 Graph candidate；不能直接编辑产品。
- 安全边界保持 `personal/local-first/paper-only/human-final`。

## 当前验证证据

- S2 Product + Mission，`PYTHONINTMAXSTRDIGITS=640`：`77 tests in 33.733s`，`OK (skipped=1)`
- S2 Product + Mission，`PYTHONINTMAXSTRDIGITS=0`：`77 tests in 34.327s`，`OK (skipped=1)`
- 冻结 P 的 prototype 回归，`PYTHONINTMAXSTRDIGITS=640`：`114 tests in 3.334s`，`OK`
- 冻结 P 的 prototype 回归，`PYTHONINTMAXSTRDIGITS=0`：`114 tests in 4.521s`，`OK`
- terminal-stall Ruff：`All checks passed!`；`4 files already formatted`
- terminal-stall `git diff --check`：PASS
- 冻结前审查最终结论：`GO_FREEZE_PRODUCT_C — Critical 0 / Major 0 / Minor 0`
- 冻结前审查已发现并关闭三类真实缺陷：post-admission 故障错误分类；损坏 typed command 未封闭为 `MALFORMED`；普通 pre-COMMIT/reconcile 故障未返回 closed outcome
- Fresh exact-object review：`FAIL — Critical 1 / Major 0 / Minor 0`
- Fresh exact FAIL receipt：SHA-256 `304fbbadaa6f1e3bd133013cae9307ea4187d9729bb8f9d3e50c646b0381dfc1`
- 未满足义务：`OBL-PAPER-UNIQUE-COMMIT-SINK`；有限深层 JSON bytes 会泄漏非 typed `RecursionError`
- Graph 规定的结果：`STALL_AND_BACKTRACK_TO_FRESH_DIRECTION_REVIEW`；`automatic_successor=false`、`R5=false`、`field_patch=false`
- terminal-stall prefreeze review：`GO_FREEZE_STALL_C — Critical 0 / Major 0 / Minor 0`
- S fresh exact-object review：`FAIL — Critical 0 / Major 1 / Minor 0`
- S FAIL receipt：`11492` bytes；SHA-256 `fbbaa496b319ca59567cd2f71cf537e9f85f128d6d8ed0d3ace34eeef19e262c`
- S→S2：10 个 candidate blob 相同；唯一差异是负例不再绑定 mutable-only 错误文案，仍要求拒绝
- S2 prefreeze review：`GO_FREEZE_STALL_C_R2 — Critical 0 / Major 0 / Minor 0`
- Product 与 Mission 的 S2 冻结态 `check-candidate`：PASS；`candidate_phase=frozen_candidate`；`execution_authorized=false`
- S2 的唯一父提交：P；prototype subtree：`bde10889591debce701ff4f7a91fb27ae023e902`
- S2 fresh exact-object review：`PASS — Critical 0 / Major 0 / Minor 0`
- S2 review receipt：`4635` bytes；SHA-256 `ecb506ac4dda141b304ae54b8d87d5d41691660c767c9081154575f6cc4ad269`
- terminal-stall 单收据 activation：`f5ccd438bfed54fbe618d225431c61f65800b475`
- activation 后 Product 与 Mission 的 `check`、`check-view`、`check-candidate`：PASS 且 `execution_authorized=false`
- activation 后 Product 与 Mission 的 `register-authority`、`check-work`、`start-work`：全部 fail closed；registration、designation ref、attempt ref 均未改变
- fresh direction proposal：JSON 有效；base identity 和 clean worktree 已复核
- fresh direction review：`PASS — Critical 0 / Major 0 / Minor 0`
- direction review receipt：`16680` bytes；SHA-256 `5984e94abb3e757aeeadf56c62420f4862268cfca0336b2ed255954a1a1c1d30`
- direction review 唯一许可动作：构造独立、冻结且再次审查的 `12-path` Graph candidate；`execution_authorized=false`
- tracked `prototype/**` diff：空；冻结 V3 diff：空

## 当前回退链怎么走

1. 产品候选 P 的 fresh exact review 已失败，保留 P 与 FAIL 收据。
2. 最小 terminal-stall candidate S 已冻结但 fresh exact review 失败；S 与 FAIL 收据均保留。
3. S2 从同一父基线重新冻结；相对 S 只关闭该 review finding，并已通过独立 exact review。
4. 只增加 S2 PASS receipt 的 activation As 已形成；它接受 stall，但不授权产品执行。
5. 从 As 形成的 exact 新方向提案已通过独立方向审查；该 PASS 不改 accepted Graph，也不授权产品。
6. 当前正创建一个以 As 为唯一父提交、prototype 不变的 `12-path` Graph candidate；随后重新走预冻结审查、冻结、fresh exact review、单收据 activation、registration、check-work、start-work 全链。

## 权威入口

- 项目工作规则：`AGENTS.md`
- 全项目路线：`governance/PROJECT_MISSION_GRAPH_V2.json`
- 固定产品能力依赖：`governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
- 冻结失败 attempt 边界：`governance/PAPER_GATE_STATE_MACHINE_BOUNDARY_V3.json`
- terminal-stall candidate contract：`governance/PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.json`
- 产品 FAIL 收据：`governance/evidence/PAPER_GATE_INTEGER_AUTHORITY_PRODUCT_R1.fresh-exact-review.json`
- terminal-stall PASS 收据：`governance/evidence/PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.fresh-review-pass.json`
- S fresh review FAIL 收据：`PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.fresh-review-fail.json`
- 当前无权限方向提案：`/private/tmp/PAPER_GATE_BOUNDED_JSON_INGRESS_DIRECTION_R1.proposal.json`
- 当前方向 PASS 收据：`/private/tmp/PAPER_GATE_BOUNDED_JSON_INGRESS_DIRECTION_R1.fresh-review-pass.json`

以后本页只更新：**当前指针、节点状态、证据、时间**。蓝图结构变化必须作为单独的版本决策说明。
