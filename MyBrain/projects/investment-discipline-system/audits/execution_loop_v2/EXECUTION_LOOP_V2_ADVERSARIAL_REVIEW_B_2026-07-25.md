# Execution Loop V2 独立对抗审查 B

- 审查者：独立只读子代理 `019f9bd7-5f57-7a92-9797-e1f9eddd183f`
- 候选提交：`b607bc2c26683445b31a77b412942058c6d6e20d`
- 候选树：`a7466150b683bced5d0a1e16cc43669792877a3c`
- 结论：`blocked`
- 远端边界：审查者只确认本地 HEAD 与本地 origin tracking ref 一致，没有执行网络 fetch。

## Review A 关闭情况

| Finding | 判定 | 摘要 |
|---|---|---|
| `A-CRIT-01` V2 ledger 进入现行 authority | open，部分关闭 | project-state projection 已调用 V2 verifier，但顶层 governance 与 project-method acceptance 仍调用 V1 verifier。 |
| `A-CRIT-02` state projection 信任 packet 自报 | closed | work-packet receipt 与 V2 execution freshness 已进入 basis；缺失、损坏、伪 complete 均 fail closed。 |
| `A-CRIT-03` 手写 exit 被当作 authenticated completion | closed | 本地 receipt 只作为 self-reported candidate evidence，远端执行和独立审查仍是单独权威。 |
| `A-CRIT-04` ledger 自引用或宽泛排除 | closed | 只排除精确发现的 V2 ledger 和三个生成视图，未知 attempts claim 与多余 ledger 会失败。 |
| `A-MAJOR-01` pending baseline 唯一语义 | open | pending ledger 在 baseline 后仍可追加 execution attempt 并保持 valid/current。 |
| `A-MAJOR-02` legacy exemption 精确 singleton | closed | 唯一 packet、contract、state、receipt 路径和 digest 均被固定并重算。 |
| `A-MAJOR-03` blocker label rotation | open | 直接轮换标签已被挡住，但第四次伪 progress 和凭空 failure resolution 仍可绕过。 |
| `A-MAJOR-04` tree、symlink、TOCTOU | closed within stated boundary | 顶层、路径组件、树内 symlink 与 special entry 被拒绝；TOCTOU 与 hard-link 保持明确限制。 |

## Critical findings

### `B-CRIT-01` Complete 不是 terminal

政策要求 complete 后的受控变更必须 reopen 或 supersede，但实现只要求最新 snapshot 等于当前字节。审查者在临时副本中修改 complete packet 的受控文件，同时重写 checkpoint、acceptance receipt 与 resolved ledger tail，verifier 仍通过。

必需修复：

- completion transition 形成不可继续追加的 terminal record；
- terminal record 绑定 completion receipt hashes、packet contract 与 controlled snapshot；
- terminal 后 snapshot、receipt 或 attempt 的任何变化必须失败；
- 只有结构化 reopen transition 或 successor packet 才能恢复工作。

### `B-CRIT-02` 强制停止不是 absorbing state

实现只检查最后三个 attempt。审查者构造前三次连续无进展、第四次伪 progress 且 retry index 达到 budget 的链，重算后仍得到 `valid/current`。

必需修复：

- 对每个历史 prefix 执行 stopping rule；
- 第一次达到阈值即形成不可跳过的 forced-block transition；
- 后续 attempt 必须先有独立、结构化 unblock authorization；
- 达到 retry budget 时，单写 `resolved` 不能替代 verified acceptance。

## Major findings

### `B-MAJOR-01` Failure 与 evidence 没有跨 attempt 连续性

单个 attempt 内集合差正确，但未要求：

```text
attempt[n].failure.before == attempt[n-1].failure.after
attempt[n].evidence.before == attempt[n-1].evidence.after
```

审查者可凭空把 `FAKE-01` 写入 before、从 after 消失，再关联一份当前受控文件，制造被 verifier 接受的 progress。

### `B-MAJOR-02` Pending packet 可偷偷执行

pending ledger 在 baseline 后追加 execution attempt、packet 与 ledger 仍报告 pending，verifier 仍返回 `valid/current`。Pending 必须恰好只有一个 baseline；首次 execution attempt 前 packet 必须转为 active 或 blocked。

### `B-MAJOR-03` 三个状态入口只保护生成块

审查者在生成块外加入 `FAKE CURRENT STATUS: COMPLETE`，`check_project_state` 仍通过。当前状态入口必须整文件 canonical，或只允许精确固定的块外模板；非权威历史不能与 current authority 混在同一入口。

### `B-MAJOR-04` 缺少正式 append/run/record 路径

当前生产路径只有 verifier，所有 ledger 由手工 JSON 和整链重算产生。该缺口不会把本地结果升级为 authenticated completion，因此不是独立 Critical，但会带来：

- 两个 writer 从同一 tail 并发追加时后写覆盖先写；
- 手工重算整链后，当前 JSON 无法自证旧 attempt 是否被删改；
- command、snapshot、ledger、packet、receipt、view 间中断，留下无恢复协议的半更新状态；
- passive recorder 接受调用者 exit code 时仍只能是 self-reported。

正式工具最低职责：

- per-packet lock 与 expected-tail compare-and-swap；
- attempt 启动前检查 state、stopping rule 与 retry budget；
- 工具自行取得 before/after snapshot，并复用 verifier canonical 实现；
- 只追加一个 record，拒绝改写既有 records；
- 原子写 ledger，并提供 packet、receipt、view 更新的可恢复 transaction；
- run mode 自行启动 argv、捕获 exit 与输出 digest；passive mode 明示 self-reported；
- 写后立即执行 V2 verifier，不得升级为 remote 或 independent authentication。

## 最小不可删回归矩阵

1. complete 后改受控 bytes、重写 receipts、追加 resolved attempt，必须失败直到 reopen 或 supersede。
2. 任意历史 prefix 达到三次 no-progress 后，再追加 progress，仍必须 blocked。
3. retry budget 尾部写 resolved、但没有 verified acceptance，必须 blocked。
4. failure/evidence before 与上一 attempt after 不连续，或凭空 resolved ID，必须失败。
5. pending baseline 后出现任意 execution attempt，必须失败。
6. 三个状态视图生成块外出现状态性矛盾文本，必须失败。
7. 两个 recorder 对同一 tail 并发追加，只能有一个 CAS 成功。
8. recorder 在 command、snapshot、ledger、packet或 view 更新间被终止，必须可确定性恢复且不能产生 valid 丢失记录。
9. 顶层 governance 与 acceptance entrypoint 不得再执行 V1 verifier；V1 只校验固定历史 hashes。

## 审查时的正向结果及边界

- V2 execution verifier：`valid/current`，7 个 tracked packet、6 个 ledger、1 个精确 pre-V2 exemption。
- V2 work-packet verifier：`pass`，1 个 complete receipt chain。
- 两组候选测试：55 tests passed。
- 三个状态视图：fresh。

这些结果真实，但未覆盖 terminal completion、历史 prefix stopping、跨 attempt continuity、pending execution、整文件视图冲突与正式 writer 并发语义，因此不能授权 foundation candidate。
