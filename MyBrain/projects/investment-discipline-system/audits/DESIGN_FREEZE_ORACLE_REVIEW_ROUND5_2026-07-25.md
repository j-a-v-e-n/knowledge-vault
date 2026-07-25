# 设计冻结固定攻击 Oracle 复核 R5｜2026-07-25

状态：`blocked-freeze`

候选 commit：`854dbb0c900ad46aef2f86523d3ac4303705013a`

候选 tree：`f489e75c3aeb3095a914aea28dff236db4155314`

## 裁决

候选不能冻结。构造者在为最终审查保存逐项原始结果时，先运行了 canonical attack 的**未变异基线**，发现该基线已经失败；因此已有“变异被拒绝”测试不能证明拒绝由目标变异造成。

这不是新的产品架构类别，而是保障 oracle 的 open major。

## Open major

### GOV-MECH-MAJ-004｜固定攻击夹具未变异时已经失败

`governance_tests/test_final_review_attacks.py` 的 `setUp()` 只复制了 `governance/`、`research/`、`audits/` 和 `scripts/`，没有复制合同列为 `design_freeze` 必需目标的 `governance_tests/`。

对未做任何语义变异的夹具直接运行候选治理验证，实际结果为：

```text
exit 1
governance verification: FAIL
- required design_freeze implementation target missing: governance_tests/
```

对 PIT oracle 变异运行时，输出同时包含目标错误和上述无关基线错误。测试只断言目标错误存在，没有先证明基线为绿，因此属于可产生假阳性的非隔离 oracle。

通过条件：

1. 固定攻击夹具复制完整 `governance_tests/`，排除缓存文件；
2. 每次目标变异前，未变异夹具必须先由 `verify_governance.py --allow-candidate` 返回 `0`；
3. 三个治理语义变异的原始结果只能在基线通过后用于最终证据；
4. 条件门固定入口继续同时覆盖旧自我证明与同门 run 重放；
5. 形成新 commit/tree 后重新执行完整回归、GitHub fresh clone 和全新独立审查。

### GOV-MECH-MAJ-005｜修复后的夹具脱离 Git 候选上下文

补齐 `governance_tests/` 后，全量回归中的 bundle 参数组合反例仍然失败。原因是 fixed attack 的临时夹具只复制项目文件，却没有保留来源仓库的 Git objects、项目 prefix 和 origin；一旦研究登记中出现绑定候选 commit/tree 的 passing final review，未变异基线就无法执行 `ls-tree` 和 candidate-tree 校验。

这说明仅在当前尚未关闭的候选状态下看到基线为绿还不够；同一个 oracle 必须在最终审查关闭与两阶段冻结路径中仍能运行。

通过条件：

1. 夹具从当前来源仓库建立无 checkout 的共享对象副本，保留候选 Git objects；
2. 夹具恢复来源 `origin`，并把项目复制到来源 `git rev-parse --show-prefix` 对应位置；
3. 直接 fixed-attack 测试和创建 frozen bundle 的嵌套测试都通过；
4. 新候选形成后再执行完整回归和 fresh clone，旧候选不得复用。

## 审查尝试记录

- `subagent:019f9998-a194-7d43-8961-5f49d0269cd3` 与 `subagent:019f9998-f28d-7941-b34f-7ed9c5ca1dc1` 被平台安全过滤器中止，没有审查证据，不能计数。
- `subagent:019f99a0-2f12-7681-be29-ee5ab7200d74` 与 `subagent:019f99a1-3e96-7070-96ba-ecf8dd9e5b50` 在候选被构造者阻断后按指令停止，均返回 `incomplete/superseded`，没有给出通过裁决。
- 两个已返回的未完成审查都把本问题列为 open major；它们没有在停止后独立复现，因此本报告不把该事实扩大为“两次独立确认”。

## 修复后的局部证据

夹具现复制 `governance_tests/`，并在 `setUp()` 中先执行未变异候选验证。局部复核实际输出：

```text
Ran 6 tests
OK
unmodified_exit 0
governance verification: PASS (candidate)
```

夹具进一步保留来源 Git objects、project prefix 和 origin 后，直接 fixed-attack 六项测试以及此前失败的 bundle 参数组合反例均通过。

这些只证明工作树局部修复有效。候选 `854dbb0...` 已被 supersede；完整通过必须绑定后续新候选。
