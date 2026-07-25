# 设计冻结 R4 修复记录｜2026-07-25

状态：`candidate-repaired-not-yet-independently-approved`

修复基线：`698383b77dcb763e504a3706779f8cdb5779e632`

本文件是构造者的修复记录，不是独立审查证据，不能批准冻结。

## 对 R4 三项 major 的处理

1. 条件门运行不再只依赖可覆盖的 current evidence。每次运行必须在主事件链追加唯一 `run_id` 的 `conditional_gate_run`，并由外部 anchor、不可更新投影、raw hash、候选身份、最新前置观察和精确 case 集合共同约束。固定反例同时复演旧的自我证明攻击和同门覆盖重放。
2. 最终审查范围不再只靠手写名单。验证器从冻结的 `IMPLEMENTATION_TARGETS_V1.json` 自动展开全部 `design_freeze` 文件及目录内容；遗漏 schema 自测或合同 supersession 验证器都会失败。
3. bundle commit D 的验证强制执行合同指定远端的 fresh clone、精确 SHA checkout、clone 内冻结治理验证、inner receipt 和 clone 后远端复查。inner 结果只能标记为 `inner_clone`，普通模式只接受 `full_outer`。

## 构造者追加发现并修复

- Git 项目位于仓库子目录时，旧 `ls-tree` pathspec 会重复拼接项目 prefix；现改为从仓库顶层解析的 literal pathspec，并移除测试夹具中的兼容补丁。
- 仅让合同自报 remote URL/branch/prefix 仍可能整体改指；治理验证器现把 GitHub fetch URL、`main` 分支和项目 prefix 固定为精确值，并增加三类 mutation test。
- 普通治理验证器原先未显式拒绝伪造的 inner-scope 成功结果；现要求 outer clone、inner receipt、远端前后观察、commit/tree、URL、branch、upstream 和 prefix 全部一致。
- Git pathspec 改为 literal，remote fetch URL 拒绝前导选项字符，减少路径或参数解释歧义。

## 已运行证据

- `python3 scripts/verify_governance.py --allow-candidate`
- `python3 -m unittest discover -s governance_tests -v`
- `python3 scripts/replay_design_freeze_attacks.py`
- `python3 -m compileall -q scripts governance_tests`
- `ruff check scripts governance_tests`
- `git diff --check`

本轮全量治理回归实际输出：`Ran 113 tests`、`OK`。候选治理验证、四类固定攻击、compileall、Ruff 和 diff check 均通过。

## 尚未满足

- 本修复尚未形成新的候选 commit/tree，也尚未推送并 fresh-clone 核对。
- 尚未由未参与构造的主体对新候选执行严格、机器可绑定的最终挑战。
- 因而 challenge 仍为 `in_progress`，本记录不能转化为 `passed_freeze`。
