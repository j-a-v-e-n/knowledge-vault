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
| 当前指针 | Paper Gate；精确 Graph candidate 已冻结，正在 fresh exact-object review | 只随已发生且有证据的状态移动 |
| 隔离候选 | accepted Graph 仍是 `f5ccd438bfed54fbe618d225431c61f65800b475`；冻结候选是 `f9db672637df754a6fbc608777e7504c31fd7b70` | frozen-but-unreviewed 候选无执行权；fresh exact review 与单收据 activation 缺一不可 |

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
    E0["E0<br/>方向选择门"] --> E1["E1<br/>Mutable 候选"]
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
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class E0,E1,E2,E3 done;
    class E4 current;
    class E5,E6,E7,E8,E9 pending;
```

**当前指针：`E4｜Fresh exact review`。候选已经完成预冻结审查和串行 activation E2E，再以 accepted stall 为唯一父提交冻结；它尚未通过 fresh exact review 或激活，因此没有任何产品执行权。**

每一次失败候选都保留，但证据不能转移给下一候选。若 fresh direction review 选出新方向，新的 E1–E8 必须重新逐步完成；方向审查通过本身也不等于 Graph 已修改或产品已获授权。

固定产品蓝图中的能力指针仍停在 Paper Gate；只有 Paper Gate 通过产品验收后，才会移动到 Ledger。

## 这一次指针为什么退回

```mermaid
flowchart LR
    AS["已接受 authority<br/>As f5ccd438"] --> D1["旧方向审查<br/>PASS，但只允许一个候选"]
    D1 --> C1["bounded JSON Graph 候选<br/>15478231"]
    C1 --> R1["预冻结独立审查<br/>FAIL · Critical 1 / Major 2"]
    R1 --> D2["两层 compositional 方向<br/>只读提案"]
    D2 --> R2["Fresh direction review<br/>FAIL · Critical 1 / Major 2"]
    R2 --> D3["边界重建<br/>回到原 FAIL 与 V3"]
    D3 --> D4["exact-decoder 提案 R1<br/>无 Graph / 产品权限"]
    D4 --> R3["Fresh direction review<br/>FAIL · Major 1 / Minor 1"]
    R3 --> D5["修正事实措辞<br/>技术方向不变"]
    D5 --> R4["第二次 fresh review<br/>FAIL · Major 1"]
    R4 --> D6["保存第一组 exact bytes + FAIL<br/>版本化 R2 · 17 paths"]
    D6 --> R5["第三次 fresh review<br/>FAIL · Major 1"]
    R5 --> D7["保存三组 exact bytes + FAIL<br/>版本化 R3 · 21 paths"]
    D7 --> R6["第四次 fresh review<br/>PASS · 0 / 0 / 0"]
    R6 --> C2["当前<br/>冻结 candidate f9db672<br/>fresh exact review 中"]

    classDef accepted fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef historical fill:#f1f3f5,stroke:#868e96;
    classDef failed fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef current fill:#e7f5ff,stroke:#1971c2,stroke-width:3px;
    class AS accepted;
    class D1,C1,D3,D4,D5,D6,D7 historical;
    class R1,R2,R3,R4,R5 failed;
    class D2 historical;
    class R6 accepted;
    class C2 current;
```

## 当前最短状态

| 问题 | 现在的答案 |
|---|---|
| 固定目标变了吗？ | 没有。仍是 personal / local-first / paper-only / human-final |
| 固定能力蓝图变了吗？ | 没有。当前能力仍是 Paper Gate，Ledger 仍 blocked |
| accepted Graph 变了吗？ | 没有。仍停在 terminal-stall activation `f5ccd438bfed54fbe618d225431c61f65800b475` |
| 产品有编辑权吗？ | 没有。冻结候选仍为 `execution_authorized=false`；Graph activation、registration、check-work、start-work 均未发生 |
| 哪些东西失败了？ | 未获权的 bounded JSON Graph candidate `154782315b2e50ebedd74d4e78f7a2e3cd985d71`、compositional 方向，以及三份不完整的 exact-decoder 方向提案；全部保留为历史 |
| 第二次为什么失败？ | 有限共享 H、Ledger 不改、V3 当前无界 typed 行为完整保留，三项不能同时成立 |
| 现在做什么？ | 只审查冻结候选 `f9db672637df754a6fbc608777e7504c31fd7b70`；PASS 后才允许单收据 activation |

## 历史明细（只作追溯，不决定当前路线）

- 更新时间：`2026-07-31`
- 当前 Graph 节点：`CAP-PAPER-GATE-INTEGRITY`
- 历史失败工作：`WORK-PAPER-GATE-INTEGER-AUTHORITY-R1`
- 当前义务：`OBL-PAPER-UNIQUE-COMMIT-SINK`
- accepted Graph 阶段：`activated_review_successor`
- 产品候选阶段：`frozen_exact_review_failed`
- terminal-stall Graph 阶段：`accepted_single_receipt_activation`
- 上一 fresh direction 阶段：`PASS — Critical 0 / Major 0 / Minor 0`，但只允许一个候选，现已耗尽且不可复用
- bounded JSON Graph candidate 阶段：`FAILED_PREFREEZE_NOT_ACCEPTED`
- bounded JSON Graph candidate commit：`154782315b2e50ebedd74d4e78f7a2e3cd985d71`
- bounded JSON Graph candidate tree：`24c0b86f864582506a4e5dd7b6d0656edf94893c`
- bounded JSON Graph prefreeze review：`FAIL — Critical 1 / Major 2 / Minor 0`
- bounded JSON failure receipt commit：`2d46b54eb9214d5e07bb2a9d57326ea724312924`
- bounded JSON failure receipt bytes：`8644`
- bounded JSON failure receipt SHA-256：`6e46d473d4f52efb160f8697c15d48d8c1fc064fe80e150a40f0ce47539d5fa9`
- compositional direction proposal bytes：`20567`
- compositional direction proposal SHA-256：`6858efcc4ecf8f0c6316c237a3cf6cb7d31552b8d66aa0a10a2cf2e1710a7513`
- compositional direction fresh review：`FAIL — Critical 1 / Major 2 / Minor 0`
- compositional direction FAIL receipt bytes：`9100`
- compositional direction FAIL receipt SHA-256：`22ca4fa65d9891eb70ee6391979cafc1e036759ba86adf7a1650ec4add119d09`
- compositional direction evidence commit：`a71717780105cbdb42377041c330623be9e5c25c`
- exact-decoder direction proposal：`DIR-PAPER-GATE-EXACT-DECODER-EXCEPTION-R1`
- exact-decoder direction proposal R1 bytes：`20988`
- exact-decoder direction proposal R1 SHA-256：`55be62f5041156a23e33f4af60ed9a0a462b2184ec16f0a9b012ed4ae3e676a1`
- exact-decoder direction review R1：`FAIL — Critical 0 / Major 1 / Minor 1`
- exact-decoder corrected proposal bytes：`21514`
- exact-decoder corrected proposal SHA-256：`094b0b95cb05d993ff7cc1e9385c52265b64d5bce5c4e41d74858a731138ae55`
- exact-decoder direction review R2：`FAIL — Critical 0 / Major 1 / Minor 0`
- preserved R1 FAIL receipt bytes：`8537`
- preserved R1 FAIL receipt SHA-256：`9eb43defd17383c6c699d9188d267c144412fdce09645c425a3425b99a83e72b`
- versioned R2 proposal bytes：`23531`
- versioned R2 proposal SHA-256：`f17e977b3dcd00a898470fe4421d94a3de14230df271b31ef94a3bca2bca8f7a`
- exact-decoder direction review R3：`FAIL — Critical 0 / Major 1 / Minor 0`
- corrected R1 proposal bytes：`21514`
- corrected R1 proposal SHA-256：`094b0b95cb05d993ff7cc1e9385c52265b64d5bce5c4e41d74858a731138ae55`
- corrected R1 FAIL receipt bytes：`5619`
- corrected R1 FAIL receipt SHA-256：`abbcbba097b4a5902f36ca3ba4ff369ba7a9d141a59a76a1eb3b3e9d222d34d9`
- R2 FAIL receipt bytes：`5491`
- R2 FAIL receipt SHA-256：`a72ff1d418e4d4286a4b74f418dd4222cf433adfd85922e72c9a5a1b1343eb62`
- versioned R3 proposal bytes：`26884`
- versioned R3 proposal SHA-256：`2dbaf3104be6a850653829850feabc081f46e60e8f84f691c873faedda64f9e5`
- exact-decoder direction review R4：`PASS_DIRECTION_ONLY — Critical 0 / Major 0 / Minor 0`
- exact-decoder R3 review receipt bytes：`9410`
- exact-decoder R3 review receipt SHA-256：`0d26af5ffb96447ee2ee8774c333e0d0cb98e9031cbbb620b17f05f57f8ddfff`
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
- 上一方向提案阶段：`HISTORICAL_PASS_EXHAUSTED_BY_FAILED_CANDIDATE`
- 新方向提案 bytes：`19734`
- 新方向提案 SHA-256：`8d1fe8144b0e23b30e69306fad62952fad99fa4cc1a5eb571071be51a675273f`
- 新方向审查：`DIR-REVIEW-PAPER-GATE-BOUNDED-JSON-INGRESS-R1`
- 新方向审查 receipt bytes：`16680`
- 新方向审查 receipt SHA-256：`5984e94abb3e757aeeadf56c62420f4862268cfca0336b2ed255954a1a1c1d30`
- 新 Graph candidate 允许写集：精确 `12 paths`；prototype 必须不变
- 当前状态：精确 21-path Graph candidate 已通过 prefreeze 和串行 activation E2E，并冻结为 `f9db672637df754a6fbc608777e7504c31fd7b70`；fresh exact review 进行中，仍无产品编辑权
- 当前运行路线：accepted Graph 仍显示 `Paper Gate = STALLED`、`Ledger = BLOCKED`；冻结候选显示 Paper Gate active，但 `execution_authorized=false`，不能反向覆盖 accepted 状态
- 历史 registration：原样保留但只绑定旧 attempt，不能转移或复用
- 历史 attempt ref `refs/ids-attempts/paper-gate-integer-authority-r1`：原样保留并继续只指向旧 activation A
- Ledger 产品写集：`NONE_AUTHORIZED`
- Paper Gate 当前产品写集：`NONE_AUTHORIZED`
- bounded JSON E2 最终结论：`FAIL — Critical 1 / Major 2 / Minor 0`
- E4 最终结论：`PASS — Critical 0 / Major 0 / Minor 0`
- S2 预冻结审查：`GO_FREEZE_STALL_C_R2 — Critical 0 / Major 0 / Minor 0`
- 当前动作：只对冻结 candidate 做 fresh exact-object review；不修改候选、不新增 public E、global H、Ledger resource domain 或容量数字
- 当前工作：`FROZEN_GRAPH_CANDIDATE_EXACT_REVIEW_ONLY_NO_EXECUTION_AUTHORITY`

## 这次失败证明了什么

- 项目级 `AGENTS.md` 已要求：只有冻结且通过独立审查的 Graph 候选，才可能进入后续启动链；Graph 只能版本化修订，不能按进展原地改写。
- 旧方向正确识别了 decoder 的资源边界问题，但错误要求所有输入和派生工件共用同一有限 profile；一个合法 envelope 可能生成更大的 approval，因此该方向不能闭合现有工作流。
- V4 的 trace 尺寸指标能够复现，但生成时把第一次 `create_account` 放在固定时钟 patch 之外；后续事件 hash 链和两个 receipt 因此不能按文档配方复现。
- V4 还把 V3 的真实产品范围误标为“旧授权历史”，会无意缩小既有验收；独立审查因此拒绝候选。
- 失败候选和失败收据已经保存；旧 direction PASS 只允许过这一个候选，不能成为下一候选的授权。
- 后续两层 compositional 提案证明 envelope 派生链可以用 E/H 闭包，但遗漏了同一个 loader 还消费独立的 account/rules typed 输入；fresh review 因此再次 FAIL。
- 原 FAIL 与 V3 复核证明：当前义务要求的是公开 writer 的闭合 typed outcome；原收据明确允许“有限 depth/size policy”或“在 exact decoder 归一化 parser recursion”二选一，V3 没有 byte/depth/token 的全局预算。
- 因而当前提案不再调 H，也不再顺手增加 public E；它只把 `RecursionError` 放回既有 `ValueError → MALFORMED` 通道，并明确不声称全局 JSON 资源闭包。该方向仍须 fresh review。
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
- direction review 的唯一候选已构造并在 prefreeze 被拒绝；该 PASS 已耗尽，不能授权第二个候选
- 失败候选：`154782315b2e50ebedd74d4e78f7a2e3cd985d71`；tree `24c0b86f864582506a4e5dd7b6d0656edf94893c`；prototype subtree 仍为 `bde10889591debce701ff4f7a91fb27ae023e902`
- bounded JSON prefreeze review：`FAIL — Critical 1 / Major 2 / Minor 0`
- failure receipt：`8644` bytes；SHA-256 `6e46d473d4f52efb160f8697c15d48d8c1fc064fe80e150a40f0ce47539d5fa9`
- failure receipt commit：`2d46b54eb9214d5e07bb2a9d57326ea724312924`
- compositional direction proposal：`20567` bytes；SHA-256 `6858efcc4ecf8f0c6316c237a3cf6cb7d31552b8d66aa0a10a2cf2e1710a7513`
- compositional direction fresh review：`FAIL — Critical 1 / Major 2 / Minor 0`
- compositional direction FAIL receipt：`9100` bytes；SHA-256 `22ca4fa65d9891eb70ee6391979cafc1e036759ba86adf7a1650ec4add119d09`
- reviewer 已再次核验 FAIL receipt 的 exact bytes、hash、finding 与无授权语义一致
- compositional direction evidence commit：`a71717780105cbdb42377041c330623be9e5c25c`
- exact-decoder direction review R1：`FAIL — Critical 0 / Major 1 / Minor 1`；官方文档未承诺 decode `RecursionError`，stored JSON 的可见异常变化也需明说
- exact-decoder direction review R2：`FAIL — Critical 0 / Major 1 / Minor 0`；15-path 写集遗漏了刚发生的 R1 exact proposal 与 FAIL receipt
- failed R1 proposal 已恢复为原 exact bytes：`20988`；SHA-256 `55be62f5041156a23e33f4af60ed9a0a462b2184ec16f0a9b012ed4ae3e676a1`
- R1 FAIL receipt：`8537` bytes；SHA-256 `9eb43defd17383c6c699d9188d267c144412fdce09645c425a3425b99a83e72b`；原 reviewer 已确认忠实转录
- versioned R2 proposal：JSON 有效；`23531` bytes；SHA-256 `f17e977b3dcd00a898470fe4421d94a3de14230df271b31ef94a3bca2bca8f7a`
- exact-decoder direction proposal 的产品预估写集：仅 `README.md`、`discipline_system.py`、`test_paper_gate_state_machine.py`；这只是待审 scope，不是权限
- versioned R2 的 Graph 预估写集：精确 `17 paths`；这只是待审 scope，不是权限
- exact-decoder direction review R3：`FAIL — Critical 0 / Major 1 / Minor 0`；17-path scope 又遗漏了 21,514-byte intermediate 与第二 FAIL
- 三组 failed proposal + FAIL receipt 均已恢复为 exact objects；三份 receipt 均经原 reviewer 确认忠实
- versioned R3 proposal：`26884` bytes；SHA-256 `2dbaf3104be6a850653829850feabc081f46e60e8f84f691c873faedda64f9e5`
- versioned R3 的 Graph 预估写集：精确 `21 paths`；产品预估写集仍为 `3 paths`
- 第四个 fresh non-builder exact-decoder direction review：进行中
- tracked `prototype/**` diff：空；冻结 V3 diff：空

## 当前回退链怎么走

1. 产品候选 P 的 fresh exact review 已失败，保留 P 与 FAIL 收据。
2. 最小 terminal-stall candidate S 已冻结但 fresh exact review 失败；S 与 FAIL 收据均保留。
3. S2 从同一父基线重新冻结；相对 S 只关闭该 review finding，并已通过独立 exact review。
4. 只增加 S2 PASS receipt 的 activation As 已形成；它接受 stall，但不授权产品执行。
5. 从 As 形成的 bounded JSON 方向提案通过独立方向审查；该 PASS 只允许一个新候选，不改 accepted Graph，也不授权产品。
6. 该 `12-path` Graph candidate 已保存为 `154782315b2e50ebedd74d4e78f7a2e3cd985d71`，并在 prefreeze review 以 `Critical 1 / Major 2 / Minor 0` 失败。
7. 单文件失败收据保存在 commit `2d46b54eb9214d5e07bb2a9d57326ea724312924`；当前从 As 回到 fresh direction review，不能从失败候选继续。
8. 两层 compositional JSON 方向提案随后在 fresh review 以 `Critical 1 / Major 2 / Minor 0` 失败；proposal 与 exact FAIL receipt 保存在 `a71717780105cbdb42377041c330623be9e5c25c`。
9. 当前继续以 As 为 accepted authority；复核原 FAIL 后形成 project-external exact-decoder 方向提案，只选择异常边界根因修正，不新增资源预算。
10. R1 fresh direction review 因一项来源措辞 Major 和一项 stored-error 说明 Minor 拒绝提案；旧 review 不可转为 PASS。
11. 只修正两项事实后的 exact bytes 在第二次 review 因遗漏即时失败历史而再次 FAIL；15-path scope 被否定。
12. 原 20,988-byte proposal 与 8,537-byte FAIL receipt 已独立保留并校验；新 proposal 改为 R2 身份与 17-path scope。
13. 第三个 fresh review 又发现 21,514-byte intermediate proposal 与第二 FAIL 未保存，R2 与 17-path scope 因此 FAIL。
14. 三组失败 proposal 与三份 FAIL receipt 现均已恢复 exact bytes，并由各自原 reviewer 确认转录忠实。
15. versioned R3 以 21-path scope 进入第四次 fresh review；仍未进入任何 Graph candidate 或产品写集。

## 权威入口

- 项目工作规则：`AGENTS.md`
- 全项目路线：`governance/PROJECT_MISSION_GRAPH_V2.json`
- 固定产品能力依赖：`governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
- 冻结失败 attempt 边界：`governance/PAPER_GATE_STATE_MACHINE_BOUNDARY_V3.json`
- terminal-stall candidate contract：`governance/PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.json`
- 产品 FAIL 收据：`governance/evidence/PAPER_GATE_INTEGER_AUTHORITY_PRODUCT_R1.fresh-exact-review.json`
- terminal-stall PASS 收据：`governance/evidence/PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.fresh-review-pass.json`
- S fresh review FAIL 收据：`PAPER_GATE_INTEGER_AUTHORITY_STALL_TRANSITION_R1.fresh-review-fail.json`
- 历史 bounded JSON 方向提案：`governance/evidence/PAPER_GATE_BOUNDED_JSON_INGRESS_DIRECTION_R1.proposal.json`，只存在于失败候选历史
- 历史方向 PASS 收据：`governance/evidence/PAPER_GATE_BOUNDED_JSON_INGRESS_DIRECTION_R1.fresh-review-pass.json`，不可复用
- bounded JSON Graph prefreeze FAIL 收据：`governance/evidence/PAPER_GATE_BOUNDED_JSON_INGRESS_GRAPH_R1.prefreeze-failure.json`
- compositional direction 失败提案：`governance/evidence/PAPER_GATE_COMPOSITIONAL_JSON_RESOURCE_DIRECTION_R1.proposal.json`
- compositional direction FAIL 收据：`governance/evidence/PAPER_GATE_COMPOSITIONAL_JSON_RESOURCE_DIRECTION_R1.fresh-review-fail.json`

以后本页只更新：**当前指针、节点状态、证据、时间**。蓝图结构变化必须作为单独的版本决策说明。
