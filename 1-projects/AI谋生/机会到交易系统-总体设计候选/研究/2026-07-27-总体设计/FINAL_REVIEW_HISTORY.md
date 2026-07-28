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

## `OTTS-DESIGN-20260727-C5`

- Candidate manifest SHA-256：`06c8624b0c2d8ef82bfe9ec4759c7cfa064fa5864681c09d285b35b54edc49a9`
- External freeze report SHA-256：`0ce0786f6c311d9558ade895dfd5487158bbc202d6d5b53601842fd466d676d3`
- 审查范围 A：完整 manifest、全部 `63` 个 active entries、依赖 DAG、C4 remediation、Run2 限定语义、RC-01–RC-26、legacy isolation 与权限边界
- 审查范围 B：同一 exact manifest/freeze 的 shadow capability、旧根逃逸与零外部副作用语义
- 裁决：两轮均为 `FAIL`；每轮各为 `0` Critical、`1` Major；两项 Major 相互独立
- PASS receipt：两轮均未签发
- 文件修改：reviewer 只在 `/private/tmp` 副本复现，未修改 candidate；两个 post-closure sibling roots 均不存在

### 拒绝项

**文档化的 post-closure aggregate Gate 会在验证前污染 immutable candidate。** `verify_post_closure_manifest.py` 在任何 bytecode 禁写设置之前导入本地 `verify_candidate_manifest`，而 `FINAL_CANDIDATE_MANIFEST.md` 给出的唯一 post-closure 命令使用不带 `-B` 的 `python3`。独立审查者在临时副本按该入口启动时，立即得到 `__pycache__/verify_candidate_manifest.cpython-314.pyc`；候选 verifier 会把新目录和 `.pyc` 判为 unlisted inventory。因此照文档执行会先改变已冻结候选，再使唯一 aggregate Gate 拒绝它，阻断 RC-25/RC-26 与 governance closure。

该缺口保持 fail closed，没有扩大现实权限，所以是 Major 而不是 Critical。C5 exact candidate 本身未被复现污染；C4 的 freeze-report schema 和 receipt 权限字段两项修复、Run2 限定语义及此前机械测试仍通过，但不能覆盖本项承重失败。

### 补充独立审查拒绝项

另一名只读 reviewer `/root/opportunity_successor_audit` 对同一 C5 manifest、inventory digest `f4cd5063f66a9967650b9a8c630e4ffe2d7187b000717cb9728eddc4fe28ea48` 与同一 external freeze report 给出 `FAIL / 0 Critical / 1 Major`，未修改文件：C5 的 post-closure Gate 只核对 shadow 文件路径、hash、role、自称的 `NO_EXTERNAL_AUTHORITY`、依赖 DAG 与 inventory；任意源码只要被标成允许的 `source` 或 `verification-script`，即使包含网络、账户、凭据、支付、旧根读取或其他外部副作用能力，仍可返回 `PRESENT_VALID / shadow_generation_valid=true`。Gate 没有 capability/SBOM 闭包、隔离运行、zero-side-effect 测试回执或绑定 exact shadow 的独立实现验收。

这没有直接把 `external_action_authority` 改为 true，但会把只完成文件哈希绑定的实现错误表示为有效 shadow，与 Envelope“禁止能力必须不存在且可机械证明”的要求冲突。因此这是第二项独立 Major，RC-25/RC-26 仍不能通过。

### C6 根因修复

- `verify_post_closure_manifest.py` 必须在任何 local import 前设置 `sys.dont_write_bytecode=True`；
- 人类可读 post-closure 命令必须同时使用 `python3 -B`，作为调用层第二道防线；
- phase regression 必须把入口及其 local imports 复制到系统临时目录，清除 child 的 `PYTHONDONTWRITEBYTECODE` 与 `PYTHONPYCACHEPREFIX`，用不带 `-B` 的 subprocess 启动，并证明没有 `__pycache__`/`.pyc`、真实 candidate 的文件集合、逐文件 hash 与 inventory digest 前后不变；
- shadow manifest 必须绑定 capability policy、Python-source SBOM、静态 capability report、隔离 runtime acceptance report、入口与合成 acceptance cases；未取得 exact independent shadow review 前只能输出 `PRESENT_HASH_BOUND_UNREVIEWED`，全部 capability/runtime/external authority 保持 false；
- 另设预声明的 `shadow-review` sibling root；只有 caller 提供的 exact review receipt hash、shadow manifest、policy、SBOM、capability report、acceptance report、runner 与治理链全部匹配，且无 unresolved critical/major，才能得到限定的 local zero-external-side-effect candidate acceptance；
- C5 manifest、freeze report 与任何派生 receipt/decision/governance 均不得迁移。C6 必须重新计算全部 candidate hashes、生成新的 external freeze report，并重新接受完整 manifest-bound independent review。

## C6 pre-freeze Capability Gate draft（未形成 frozen candidate）

- 被审 policy SHA-256：`768ad742fdb702816c09647f04242c10c5278f51c515d9b5fa2309fcaa8c4241`
- 被审 runner SHA-256：`d271b4a09a0880ea50404eff118b9b62cbd584a1709c19528b7006164eb78836`
- 被审 tests SHA-256：`030712de48880080a6743ba15fbba170e944fe9f0c7744c9fbef3a7f07e456dd`
- 审查身份：`/root/independent_review` 与 `/root/capability_escape_challenge`；两者只读，未修改文件
- 裁决：`FREEZE BLOCKED / NO-GO`
- candidate manifest、freeze report、PASS receipt、governance/shadow roots：均未生成

### 阻断原因

该草案把 shadow 自带的任意 Python source 放进高能力 CPython，再用 AST denylist 与有限 audit events 推断“网络、进程、native、环境、项目外读取和非临时写入均不存在”。这只能发现一部分直接语法和已枚举事件，无法关闭别名、反射、预载模块、未枚举 audit event 或解释器/stdlib 可达能力，却会无条件生成强于机制的 runtime 结论。另有独立 TOCTOU：源码先按 pathname 解析、hash，worker 随后再按 pathname 打开执行；事后重算无法证明执行的是先前被绑定的同一字节。worker 还缺少内存、进程、文件描述符、stdout/stderr、输出数量/总量和整个 process group 的完整资源边界。

这些发现没有让任何现实权限变为 true，但会让一个只能称为 best-effort lint/audit smoke test 的机制被误读成 Capability Gate；因此 C6 不得在该草案上冻结。已通过的 bytecode 修复不覆盖本拒绝。

### 根因级替代契约

- shadow artifact 不再携带或执行 target-controlled Python、bytecode、native code、脚本、plugin、callback、模板求值或其他通用代码；只允许 canonical JSON/text 与 exact closed declarative IR；
- opcode 使用逐类型 exact-key schema，数据不能选择新 opcode、路径、URI、模块或函数，且无循环、递归、跳转、动态 instruction、环境、时间、随机、网络、进程、connector 或任意文件原语；
- 当时提议 manifest、program、fixture、policy 与 runner 使用 `O_NOFOLLOW` opened-object 的单次有界读取完成 hash+copy，前后 `fstat` 不一致即拒绝，并称 runner-owned private staging 为 immutable；后续 iteration A 证明同 UID 仍可覆写该 pathname，iteration B 才改为 opened-and-unlinked descriptor；
- 唯一写原语是由 SHA-256 digest 推导路径的本次私有临时 CAS；输入不能提供路径或文件名；资源、JSON 深度、节点、放大率、输出和日志均有闭集上限；
- macOS `sandbox-exec` 只能作为当前主机的 deprecated/unsupported defense-in-depth 并必须实测、失败关闭，不能作为跨平台或 host-level universal noninterference 证明；真正承重边界是 artifact IR 中相应能力不可表达；
- receipt 只允许声明 exact local deterministic declarative evaluation、snapshot/output identities 与全部 authority false；不得声明 runner/TCB 无 bug、跨平台 OS attestation、保密性、deployment、production 或外部行动权限。

只有这套替代实现、对抗回归、三根 producer/consumer schema 和人类文档全部闭合后，才能生成第一份 C6 canonical manifest；上述 pre-freeze draft hashes 不得作为 successor PASS 证据。

## C6 declarative Gate pre-freeze iteration A（未形成 frozen candidate）

- 被审 policy SHA-256：`04f300fa5a9bc0c77bfa9419c77acd8aeaad625868945d03e8d20fa092a40319`
- 被审 runner SHA-256：`00f04acaa8d8efc8fb775e58eee0f0f9d5a65317d65b89307bf38f73f41fecee`
- 被审 tests SHA-256：`78f3c9ccd343dcd92bff76a5e2011b0dd8071fdd84404d8845332ae08cb7fad8`
- 当时 aggregate verifier SHA-256：`84c1c060efc826dd73b6ae92316a9cffe698c4d2ffc22110d6f0d7e4acbd9b50`
- 审查身份：`/root/declarative_gate_code_review`；只读，未修改文件
- 裁决：`FAIL / NO-GO`；`1` Critical、`4` Major、`1` documented residual
- candidate manifest、freeze report、PASS receipt、governance/shadow roots：均未生成

### 阻断原因

1. **同一 uid 下的 staged pathname 不是不可变执行对象。** Runner 只在 launch 前检查一次 `0400`，随后又按路径打开 runner、profile 和 request；同 uid 进程可以 `chmod`、覆写并伪造 probe/worker 响应。审查者实测得到 `before=trusted / after=attacker / mode=0o600`。这与当时文档的“immutable staged execution”强主张冲突。
2. **Aggregate 末端只重算路径 inventory，不重算已接受 snapshot。** 同名文件内容替换后 path set 不变，Gate 仍可返回基于旧快照的结果，却没有显式说当前 root 已漂移。
3. **Runtime TCB identity 只哈希 Python executable 与 `sandbox-exec`，没有闭合实际加载的 stdlib/extension/dylib。** 当时选用的 Python 3.14 home 为 `root:admin` 且 group-writable，当前用户属于该 group；改动已导入模块不会改变当时的 TCB digest。
4. **Resource policy 可自我放大且 workload 无 aggregate bound。** Loader 接受任意正整数；acceptance case 数、`BUILD_OBJECT` fan-out 和全程时间没有闭集上限；CAS 数量/总字节在写后才检查；Darwin 上没有实际 RSS/address-space 限制。
5. **Managed suite 的绿色可以没有任何真实 sandbox positive path。** 主流程测试 mock `run_case`；真 sandbox 测试捕获任意 `CapabilityError` 也算通过。这正确证明生产代码在 nested sandbox 中 fail closed，却不能作为宿主 profile/probe/worker 已成功的证据。

Reviewer 同时确认 closed opcode 没有 import/eval/shell/subprocess/connector/path/URI primitive，未发现 unsandboxed fallback，且所有 authority 仍为 false。因此本轮拒绝不说明 artifact 已经执行外部动作；它说明 snapshot/TCB/resource/test 证据强度不足以支撑当时的 acceptance 命名。修订后必须换用新 exact hashes 重新审查，本轮不得迁移为 PASS。

## C6 declarative Gate pre-freeze iteration B（代码/接口审查 PASS；尚非总体候选终审）

- capability policy SHA-256：`8ca4d90c958ea04adf14d003226a620a4000ad805e439823b5c5cc34a7e7ebb9`
- runner SHA-256：`ba5bb3aeb55b14eaa8135c8367ed16295d0782a4f7813b337397998117edbc97`
- runner tests SHA-256：`a870a2262633b19d40bd892a00c72240d8e8f4c65be436f32573cc8378176eec`
- aggregate verifier SHA-256：`823acd5aba8ac2949312c663acd25bd4c3de203a7c18604d9da066df2f2d45b3`
- phase tests SHA-256：`d6ea9916c9bff14e9111d5b881dce518a35df9d9c23a9841b1e3f84d91f9bcad`
- 审查身份：`/root/declarative_gate_code_review`；只读，未修改文件
- exact-byte 代码/接口裁决：`PASS`；无 Critical、无 Major
- managed suite：`OK (skipped=1)`；唯一 skip 是必须显式启用的 host sandbox positive path，不能被算作 host PASS
- lead 在真实 host context 独立运行 `OTTS_REQUIRE_HOST_SANDBOX=1 python3 -B test_shadow_acceptance.py -v`：`OK`，host 项未 skip
- phase-boundary suite：`OK`
- candidate manifest、freeze report、总体 final-review receipt、governance/shadow roots：本节审查时均未生成

### 已关闭的 iteration A 根因

- target-controlled artifact 只能使用 canonical JSON closed IR；runner、policy、program、fixture 与 request 通过 opened-and-unlinked read-only descriptor 传入，profile 以 exact bytes 交给 `sandbox-exec -p`，不再重开 target-controlled pathname；
- policy 每个 limit 必须等于 runner 内置 ceiling；case、entry、总输入、node/depth/fan-out、结构值、CAS、output/log、per-case 与 aggregate deadline 都有限定，CAS 在 create/write 前检查配额；
- runtime 改用 Xcode 内 root-owned/non-writable anchor chain，final TCB 同时绑定实际 worker 观察到的 Python module file rows/digest；完整 dynamic-library/host closure 仍为 false；
- post-closure verifier 在读取 shadow entry 前先 hash-bind/解析 fixed policy，前置限制 case/entry 数，并对每个 role 和总输入使用固定上限；末端重新 snapshot candidate、shadow manifest、每个 entry、policy 与 runner；
- shadow review receipt exact schema 绑定 loaded-module closure、opened-unlinked execution、target-controlled pathname reopen count、same-UID non-claim、memory boundary、aggregate deadline/timeout 与全部 authority false；数值零必须是 non-boolean integer，JSON `false` 不能冒充；
- 未经 exact shadow review 的初见状态只能是 `PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED`；限定接受状态仍保持 host universal noninterference 与全部现实权限 false。

### 保留的 Minor / non-claims

- stdout/stderr 的命名 ceiling 在进程结束后读取时检查；写入阶段承重的是更宽的固定 `RLIMIT_FSIZE`，所以该命名 ceiling 不是严格 pre-write enforcement；
- 结构值累计字节 ceiling 在节点构造与 canonical serialization 后检查；其他 fixed input/node/fan-out/output ceilings 使范围有界，但该累计 ceiling 仍是检测型边界；
- parent 只证明 `close_fds/pass_fds` 配置，worker 未在 sandbox-exec 后枚举实际 FD set，因此回执只允许写 `PARENT_CONFIGURED_ONLY ... POST_SANDBOX_FD_ENUMERATION_NOT_PERFORMED`；
- hostile same-UID/admin race-and-restore、完整 dylib/host TCB、Darwin 进程级 RSS 隔离、跨平台隔离、runner 无 bug、保密性和 host-level universal noninterference 均未证明。

该 PASS 只关闭上述五个 exact files 的 Gate 代码/接口拒绝项，不是 RC-26、freeze、deployment、runtime 或外部行动授权。下一步仍须把全部候选字节封装成新的 C6 manifest/freeze，并接受另一轮完整 manifest-bound independent review；本节 PASS 不得迁移成总体终审 PASS。

## `OTTS-DESIGN-20260727-C6` withdrawn after exact final review

- Candidate manifest SHA-256：`68ed50299468c7e1e2f5a886e9199f1e60dad9e371329b40d721cb0a62aaa38d`
- Inventory digest：`f2a631c5759c2409a5a8a7e746a0e7c13fb1b0057c3f65c8b8418a2a30ec95c0`
- External freeze report SHA-256：`51917e3c663cbf4472617ee235872d6a10f9e93f4fd0cf0773398f343c1449cb`
- Reviewer ID：`codex-independent-final-reviewer-c6-20260727-fresh-a`
- 审查范围：全部 `67` 个 active entries、依赖 DAG、全部 `26` 个 raw originals、Run2 Claim→Evidence 语义、declarative Gate、post-closure schema、三个 sibling roots 与 RC-01–RC-26
- 裁决：`FAIL`；`0` Critical、`2` Major、`1` Minor
- RC 结果：`RC-02`、`RC-05` 失败，因而 `RC-26` 失败；总体继续 `BLOCKED`
- 文件修改：reviewer 只读；三个 post-closure sibling roots 均不存在；未生成 receipt

### 两个独立 Major

1. `S2-K03/R16/turn163academia15` 的原件与 joint 只承载 rival firms、acquihire 与 talent allocation 的形式模型，lead 还把它识别为 customer-acquisition 词义误命中；它没有 AI 降本、卖方利润或价值捕获命题，却被 human/JSONL crosswalk 提升为 `SS-01` 的 direct-load-bearing support。
2. `S2-K06/R06/turn166search4` 只承载 compositional consumer choice、效用成分与相似商品未必为 substitutes 的条件性理论；它没有 AI 降本、卖方利润或价值捕获结论，却被同时提升为 `TF-04,SS-01` 的 direct-load-bearing support。

机械 verifier、crosswalk tests、Run2 acceptance tests、managed/host Gate suites、phase suite、manifest/freeze inventory 与 DAG 均通过，但它们只能证明 identity/hash/reconstruction/schema，不能自行判断上述语义桥成立。因为两条边被显式标为 load-bearing，机械 PASS 不能覆盖语义 FAIL。

Minor：`RESEARCH_CLOSURE_PREDICATE_MATRIX.md` 仍用“manifest/freeze 待生成”的瞬时措辞；supplemental exact-candidate assurance 另指出 candidate verifier 对顶层 `status/scope` 只要求非空。当前 exact manifest 的值本身安全，但 successor 必须冻结闭集常量并加入过度声明负向测试。

### 后续修订边界

- 上述 exact manifest/freeze 永久作为失败历史，不得签发 governance receipt，也不得迁移到后续候选；
- 两条来源保留 final CE-IN 与类别/方法线索，但降为 `NO_DIRECT_LOAD_BEARING_USE`，Claim/DD 为空；
- 同一语义原则也把 `S2-K06/R05/turn166search3` 对 `SS-01` 的桥删除，只保留其形式模型对 `TF-04` 中 quality-WTP/price 比较机制的窄支持；
- verifier 必须以独立于计数的拒绝集和负向回归阻止已否决 identity/claim 重新晋级；
- 修订后的 human/JSONL crosswalk、verifier、tests 与 `FINAL_RUN_STATUS.md` 必须形成新 exact bytes，并取得新的独立 Run2 acceptance；
- closure matrix 的阶段措辞与 candidate 顶层 `status/scope` 必须改为 forward-stable、exact closed values；
- 只有重建全候选 manifest/freeze 并由 fresh full reviewer 给出无 Critical/Major 的 PASS 后，才可创建 governance root。当前没有 implementation、shadow operation、deployment 或 external-action authority。
