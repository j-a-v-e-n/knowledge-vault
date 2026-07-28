# 旧 CLI 与餐馆 Pilot：差距审计结案

状态：`GAP-AUDIT-CLOSED-BY-GLOBAL-QUARANTINE / LEGACY-REUSE-NOT-AUTHORIZED`

## 结论

旧 `schema/workspace 0.1` 不能通过增量修补成为当前系统的可靠基础。它把调用者自填记录压成 candidate-wide 商业阶段和权限字符串，再生成可能被下游误读的任务工件；缺失的是对象身份、原件来源、exact-offer 绑定、独立 Gate、失效传播和提交时重验等基础语义。继续在旧模型上加筛选条件只能改变 fail-open 的位置，不能消除根因。

因此，本次结案动作不是声称旧模型已被修好，而是永久撤销它的运行与授权面。

## 历史根因

| 审计项 | 旧模型的承重缺口 | 为何不能局部补丁解决 |
|---|---|---|
| `LG-01` | candidate-level 事件可解锁 delivery | 没有 counterparty、exact offer、agreement、order 或 feasibility decision 身份 |
| `LG-02` | 外部证据主要依赖调用者自填来源标签 | 缺少原始回执、外部对象身份和独立验收 |
| `LG-03` | authorization 字段直接映射为 permission | 缺少 canonical action envelope、policy decision、grant、提交时重验和执行回执 |
| `LG-04` | 可变输入与不完整 digest 不能可靠撤销旧工件 | 缺少完整闭包、append-only 证据和机械失效传播 |
| `LG-05` | CLI 可输出无范围合格声明或生成工件 | 文档警告和 workspace marker 都不是确定性权限门 |
| `LG-06` | 双通道只验证引用存在 | 没有独立采样、采集 lineage、sealed output 和污染传播 |
| `LG-07` | candidate-wide 单向阶段覆盖并存现实 | 没有按对象与窗口分离的正交状态和 blocker |
| `LG-08` | 结构检查结果容易被误读成需求或权威成立 | 输出没有声明范围，也没有排除商业推断 |
| `LG-09` | Pilot 输入闭包缺少负证据与失效依赖 | 文件名或局部 hash 不能证明完整 provenance |
| `LG-10` | 来源和预览没有可迁移的权利链 | 缺少原始快照、rights record、asset BOM 和 right-to-sell Gate |
| `LG-11` | 历史正文与工作区仍可能被当作当前状态读取 | 需要全局隔离，而不是依赖读者正确解释文档 |

## 已实施的 fail-closed control

- 活跃 `src/opportunity_os.py` 与 `tests/test_opportunity_os.py` 已被有意替换为 tombstone 和对抗性验收；版本控制差异保留历史变更证据，但活动源码树中不保留可执行的旧 runtime 副本；
- 保留的旧公开 API 只执行同一个无条件 quarantine guard；
- guard 在访问参数、读取路径、创建目录或写文件前执行；
- `validate_record` 与 `validate_workspace` 也被 tombstone，不保留会返回空 issue 或无范围合格结论的 inspector；
- CLI 保留旧语法只为向既有调用者返回稳定拒绝，所有子命令均非零退出；
- `derive_opportunity_status` 不再产生商业状态；
- `external_permission_for_probe` 不再产生 permission；
- `make_harness` 的两个历史 mode 均不可运行；
- 没有 screening、路径、marker 或调用者字段能够解除隔离。

## 对抗性验收范围

活跃测试覆盖：直接 API、每个 CLI 子命令、两个历史工件 mode、复制到新路径、删除 marker、加入 `pass` screening、文件系统前后快照、stdout 禁止声明、撤销清单字段和每个隔离原件的 SHA-256。测试只证明 tombstone 与撤销边界生效，不证明研究闭合、新设计正确或任何商业结论。

## 工件处置

旧 Pilot 的四个任务工件已从活跃 `workspace/harnesses/` 移除；两张仍显示旧 banner 的截图也已从活跃 preview 路径移除；原 RUN_LOG 的精确字节已隔离。路径、哈希与空权威范围见 [`pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json`](./pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json)。活跃 RUN_LOG 仅为撤销通知。

## 明确非目标

本次结案不创建 successor runtime，不迁移旧商业状态，不恢复 Pilot，不把历史测试改写成新系统验收，也不授权任何外部动作。未来实现必须另行授权并从独立身份、独立对象模型和独立证据闭包开始。
