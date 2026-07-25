# 设计冻结机制复核 R4｜2026-07-25

状态：`blocked-freeze`

候选 commit：`698383b77dcb763e504a3706779f8cdb5779e632`

候选 tree：`cef2949295b4e54cab960cd65821aec3a99f3ebc`

审查主体：`SUBJECT-DESIGN-REVIEW-SINGER-R4`

工具 locator：`subagent:019f9951-a680-78b0-a542-503de4762262`

参与候选构造：`false`

写入候选：`false`

## 裁决

没有发现新的架构类别，但存在三个可复现的 open major，因此候选不能冻结。

## Open major

### GOV-MECH-MAJ-001｜同一条件门可覆盖证据并复用 run_id

合同要求每次通过证据来自 fresh unique run。候选的 `run_id_replayed()` 只扫描其他条件门当前 evidence，并跳过当前条件门路径；它没有追加式历史或已消费 run ID 的权威记录。

审查者在临时仓库中先用固定 UUID 生成合法 evidence 并通过，随后追加新观察，以同一 UUID 覆盖当前条件门的 raw/evidence 后再次运行。两次返回码均为 `0`，第二次 `status=pass` 且 `errors=[]`。

通过条件：把已使用 run ID 绑定候选、观察、原始结果和追加式权威记录；同门历史复用必须有固定反例测试并被拒绝。

### GOV-MECH-MAJ-002｜最终审查完整范围漏掉自身 schema 测试

`FINAL_REVIEW_REQUIRED_SCOPE` 未包含 `governance_tests/test_final_review_schema.py`。审查者在临时 fixture 中构造不含该文件的 passing review，治理验证仍返回 `PASS (candidate)`。

通过条件：最终审查范围包含所有冻结治理脚本及对应治理测试，并有“遗漏 schema test 必须失败”的 mutation test。

### GOV-MECH-MAJ-003｜bundle commit D 未强制 fresh-clone 后验证

合同要求 bundle commit D 推送后，从可信远端 fresh clone 并运行冻结验证。候选的最终 bundle 校验没有强制传入 `--fresh-clone`；即使手工启用，remote verifier 也只解析 clone 中的 commit/tree，不在 clone 中运行冻结 verifier。

通过条件：D 的 post-bundle gate 必须强制从明确远端/分支 fresh clone 精确 SHA，在 clone 中运行冻结治理验证，并把退出状态与输出绑定结果。

## 已实际运行

- `git status --short --branch`
- `git rev-parse HEAD`
- `git rev-parse 698383b77dcb763e504a3706779f8cdb5779e632^{tree}`
- `git show -s --format=%H%n%T%n%P%n%D%n%ai%n%s 698383b77dcb763e504a3706779f8cdb5779e632`
- `python3 scripts/verify_governance.py --allow-candidate`
- `python3 -m unittest discover -s governance_tests -v`

候选治理验证通过；治理测试为 `Ran 88 tests`、`OK`。这些绿灯与三个反例同时成立，不能替代本裁决。

## 已确认有效的控制

- SQLite 条件事件的列、类型、主键、观察外键、精确 trigger 和实际 UPDATE/DELETE 探针均有检查。
- 事件序列、canonical payload、hash chain、观察投影、状态 hash、anchor chain 与 tail 基本闭合。
- CLI 候选身份、bundle 和 runtime DB 参数只是 expected value。
- C→B closure 检查累计路径、Git mode/type/blob、非 JSON 不变性和允许的状态迁移。
- finding 计数、raw result hash、selector 和候选 commit/tree 具有机器绑定。
- 冻结程序会自行运行候选治理验证和固定 selector，但尚未满足上述 fresh-clone 后验证义务。

## 限制

- 本次审查没有对真实 GitHub 执行 live `ls-remote`；远端逻辑来自静态调用链和临时 bare remote。
- 条件反例使用 fixture runtime 与 core verdict，只证明 run 唯一性缺口，不表示 fixture 可满足 human/longitudinal release。
- 候选没有 bundle commit D；第三项来自确定的调用链缺口，而不是生产 D 演练。
