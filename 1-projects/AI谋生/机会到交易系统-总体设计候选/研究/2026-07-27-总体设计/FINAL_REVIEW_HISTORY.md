# 最终候选审查历史

本文件保留总体设计候选在最终独立审查阶段出现的拒绝项。失败候选不得被后续修订静默覆盖，也不得被解释为曾经获得实现权限。

## `OTTS-DESIGN-20260727-C1`

- Candidate manifest SHA-256：`961e2434db55e5ffb9e6dc188ceda13a74c46d0e618e0e0087b11f2a7ede7f6f`
- 审查范围：phase-boundary bounded review；不是全量最终审查
- 裁决：`FAIL / MAJOR`
- 文件修改：审查者只读，未修改候选

### 拒绝原因

候选验证器把 `FINAL_CANDIDATE_MANIFEST.json` 的父目录作为完整 inventory root，并拒绝其中任何未列文件；同一候选又准备在该目录内新建 `shadow_mvp/`，并可能把 review receipt 与 closure decision 写入同一目录。因此，第一份正常的后闭合工件会使已审候选机械失效；若把新工件补入候选 manifest，又会改变 manifest hash，使 review/closure 绑定失效，形成逐文件重封与重审循环。

这个问题没有扩大任何现实权限，系统保持 fail closed，所以不是 Critical；但它阻止候选在保持 exact-hash 身份的同时进入自己定义的下一阶段，必须在开工前修复。

### C2 必须满足的修订

- 当前候选目录继续作为完整、零漏项的不可变设计 inventory root；
- governance 与 shadow implementation 使用两个与候选目录不重叠、名称精确冻结的 sibling roots；
- candidate freeze 时两个 sibling roots 必须不存在，禁止提前藏入文件；
- post-closure root 必须各自使用独立 canonical manifest，完整绑定内部文件、依赖、外部父候选 hash，并拒绝漏项、symlink、hardlink、special file、路径逃逸和依赖环；
- freeze report 先证明两个 sibling roots 在候选终审时均不存在；review receipt 绑定 exact candidate、freeze report、verifier 与 Envelope，closure decision 再绑定 exact candidate、freeze report、exact review receipt、exact shadow root 与 Envelope；
- aggregate Gate 还必须收到与 closure decision 字节一致的外部 expected hash；只读取 root 内自称获准的文件不能授权实现；
- shadow root 的 manifest 再绑定 exact candidate、governance manifest、review receipt、closure decision 与 Envelope；
- frozen candidate 任一字节变化使 RC-26 失效；后闭合工件变化只使依赖它们的 downstream closure/runtime 状态失效，不反向改写历史设计快照。

在修订候选重新冻结并完成一轮新的全量 manifest-bound independent review 前，权威状态继续为 `BLOCKED`。

## `OTTS-DESIGN-20260727-C2` withdrawn pre-final candidate

- Candidate manifest SHA-256：`b66fe735158177a18940667ff7bbd1075df532de948067498cd3748e36715f61`
- Freeze report SHA-256：`614898a499e5348ca765c902848c364e0c421dbc9b3d8db91c8d42e7a82d560c`
- Reviewer ID：`fresh-c2-final-reviewer-20260727-a`
- 裁决：`FAIL / WITHDRAWN`
- 全量研究语义审查：未完成，不能把本轮局部发现解释为 RC-01—RC-24 的 PASS

### 拒绝项

- candidate verifier 对普通文件做 hash/inventory equality，但会跳过 FIFO/socket 等 special node，且未拒绝 hardlink；这与 post-closure root 的闭集策略不一致；
- shadow manifest 的 `status/scope` 只要求非空，因此文件可以写入与 Envelope 冲突的 production/外部权限措辞，即使 aggregate 输出另有 `external_action_authority=false`；
- reviewer 按普通 Python 入口运行 phase tests 后，本地 import 生成两个未列入候选的 `.pyc`；测试断言通过，但紧随其后的 freeze verifier 正确拒绝已被测试自污染的 inventory。

### 后续修订

- candidate inventory 与 post-closure inventory 统一拒绝 symlink、hardlink、special node 和未列目录，并加入 synthetic 负向测试；
- shadow 顶层状态/范围冻结为 `SHADOW_IMPLEMENTATION_CANDIDATE / LOCAL_ZERO_EXTERNAL_SIDE_EFFECT_SHADOW_MVP_ONLY`，且必须显式 `external_action_authority=false`；
- phase test 在任何 local import 前设置 `sys.dont_write_bytecode=True`，并保留 `-B` 作为调用层第二道防线；reviewer 生成的两个可再生 `.pyc` 与空 cache 目录已移除；
- 旧 exact hash 已撤回，必须重新计算全部依赖、重新生成 freeze report，并由另一轮 fresh reviewer 完成从机械边界到研究语义的全量终审。

## `OTTS-DESIGN-20260727-C3`

- Candidate manifest SHA-256：`ca74736da43b07c821389b690075aef86001d8bc0463b13397c8406acc48c285`
- Freeze report SHA-256：`655cea4ce1d2b58b5a111bec13ca6b1dd8653778c9f7cce82adba557dba5b193`
- 审查范围：完整 manifest、active/historical dependencies、Run2、核心语义、phase boundary 与 RC-01—RC-26
- 裁决：`FAIL / MAJOR`
- 审查者独立性：未撰写或修改 C3；此前检查过 C1/C2 phase boundary，因此不是 blind review
- 文件修改：审查者只读，未修改候选

### 拒绝项

1. **候选冻结后发生并发字节漂移。** C3 终审末次复验时，旧 `src/opportunity_os.py`、`tests/test_opportunity_os.py` 已变化，并出现未列入 manifest 的 `__pycache__`；freeze report 只证明较早快照。两个 post-closure sibling roots 仍不存在，没有因此获得权限。
2. **Run2 crosswalk 不完整。** S1 最终 CE-IN 为 `131` 条，旧 crosswalk 只列出 joint disagreement-side 的 `18` 条；S2 最终 CE-IN 为 `141` 条，旧 crosswalk 只列 `8` 条。共 `246` 条 agreement-side CE-IN 没有进入 Claim/RQ/DD/scope/unknown bridge，违反文件自身的全覆盖不变量和 SSP 最低完成包。
3. **最终运行状态缺少明确独立同意。** `S2_INDEPENDENT_ACCEPTANCE_RECEIPT.md` 明确写着 `RUN-FINAL-STATUS-NOT-YET-DECIDED`，只接受 S2 joint exact bytes，不宣布 `SATURATED-WITHIN-PROTOCOL`；旧 `FINAL_RUN_STATUS.md` 却把它当成双方对后续 final-status 对象的同意，未满足 SSP §8.7。

### C4 根因修复

- successor candidate 使用独立 sibling root `机会到交易系统-总体设计候选/`；不再把仍可能被其他任务修改的旧 runtime/test/Pilot 字节纳入不可变设计 inventory；旧根保持外部 `LEGACY_UNQUALIFIED`，不删除、不复用、不反向污染设计身份；
- 从 sealed lead/independent ledgers 与 S1/S2 joints 机械重建全部 `272` 条最终 CE-IN，生成 canonical JSONL；直接进入当前 Claim/DD 图的 `26` 条与 `NO_DIRECT_LOAD_BEARING_USE` 的 `246` 条明确分型；
- 新 verifier/test 拒绝缺失、重复、claim/scope/K 篡改、unused 自晋级和非 canonical 序列化；
- `FINAL_RUN_STATUS.md` 改为 lead exact object；在另一名 independent reviewer 明确接受相同 final-status hash 前，运行状态保持 `INCOMPLETE`；
- Run2 exact acceptance 完成后仍须重新冻结 successor manifest，并由未撰写 successor candidate 的另一名 reviewer 完成全量 RC-01—RC-26 终审。

### Run2 exact final-status acceptance

- 决定：`ACCEPT`，且只接受 `SATURATED-WITHIN-PROTOCOL`；
- 接受对象：`ssp-run2/FINAL_RUN_STATUS.md` SHA-256 `35ffc2e34ca69a491cc5cabe25dc55b7fbf58edde67539fe1257ab23d736d30f`；
- canonical receipt：`ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json` SHA-256 `be30f6967b5872749403eef2af2c1e0cc25f99828c7ceb01aa0b744692b8a788`；
- reviewer：未撰写或修改 C4、successor Run2 package 或当前 remediation；此前审过 C3 并报告相同缺口，因此独立于 authorship，但不是 blind；本轮只读；
- 边界：该接受只证明 frozen SSP category/codebook 范围内的最终运行状态，没有 C4 closure、实现、shadow operation 或外部动作权限；reviewer identity、独立性与时间顺序仍是本地声明，不是加密签名或 trusted timestamp；
- 机械桥：`verify_run2_acceptance.py` 绑定该 reviewer 给出的 exact paths/hashes、空 critical/major、权限全 false，并重新执行 exhaustive crosswalk verifier；相应负向测试拒绝 receipt、artifact、scope 与 authority 篡改。

该 acceptance 完成 C3 的第三项修复，但不替代 C4 canonical manifest、freeze report 和另一轮全量 RC-01—RC-26 independent review。

## `OTTS-DESIGN-20260727-C4`

- Candidate manifest SHA-256：`9e0c88170429083d3042c8ad429e18c6b1fe8fc795a0e5331e58f255961f28fe`
- External freeze report SHA-256：`88f51399359779b28e771e3473445caefc1a3dafb0358c1ebbfbd65aaa3f57a1`
- Reviewer ID：`codex-independent-reviewer-c4-20260727`
- 审查范围：完整 manifest、全部 `62` 个 active files、依赖 DAG、Run2、RC-01–RC-26、legacy quarantine、phase boundary 与权限边界
- 裁决：`FAIL`；`0` Critical、`2` Major、`1` Minor
- RC 结果：RC-01–RC-23 在声明的研究/设计范围内通过；RC-24 exact Run2 链通过；RC-25/RC-26 失败
- 文件修改：reviewer 只读；两个 post-closure sibling roots 均不存在

### 拒绝项

1. **Exact freeze report 不能进入 frozen aggregate Gate。** C4 external report 含 Gate closed schema 不允许的额外字段并使用绝对 `verifier_path`；复制 exact bytes 会被拒绝，投影/改写又会改变 review 绑定的 hash。
2. **终审 receipt 契约与 frozen receipt schema 冲突。** 终审要求 receipt 明确 `external_action_authority=false`，但 C4 `REVIEW_RECEIPT_KEYS` 没有该字段并拒绝 extra key；满足 review contract 的 exact receipt 无法进入 governance root。

Minor：human manifest、closure matrix、frozen pre-acceptance crosswalk 和 Envelope 的可读状态比 canonical JSON/外部 receipt 保守，可能误导人工恢复，但没有放宽权限。Crosswalk 作为 Run2 exact acceptance 的输入不能就地改写；当前状态必须由其外部 acceptance receipt 和 successor 状态入口解释。

### C5 根因修复

- 新增 `build_freeze_report.py`，直接调用 candidate verifier，并只生成 aggregate Gate 接受的 exact key set、相对 verifier path 与两个 sibling root `ABSENT` 证明；拒绝写入 candidate inventory或覆盖不同报告；
- phase tests 不再手写另一个 freeze schema，而是调用同一 builder 生成实际治理输入；新增 extra-key、绝对 verifier path 和整条 hash 链重算后的拒绝回归；
- `REVIEW_RECEIPT_KEYS` 正式加入 `external_action_authority`，aggregate Gate 要求其逐字为 `false`；测试证明即使重算后续 receipt/decision/governance hashes，改成 `true` 仍 fail closed；
- 人类可读 successor 状态改用不依赖“冻结前/后”瞬时切换的 `BLOCKED-PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`；frozen Run2 crosswalk 的旧 header 只作为 pre-acceptance 输入状态，由 exact acceptance receipt 覆盖当前有效状态；
- C4 exact receipt 不得迁移复用。C5 必须产生新 manifest、新 freeze report，并重新接受完整 RC-01–RC-26 independent review。
