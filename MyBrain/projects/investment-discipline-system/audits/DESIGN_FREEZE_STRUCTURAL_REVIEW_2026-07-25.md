# 设计冻结结构闭合审查｜Round 2B

状态：`blocked-freeze`  
候选 commit：`85601b785c5fac46d4b6533845abaca92d4af01d`  
候选 tree：`ae71186bd70282949c2e953fe969d8c6009a8101`  
审查主体：`SUBJECT-DESIGN-REVIEW-BANACH-R2B`  
工具 locator：`subagent:019f98cf-2e33-7e02-a86a-87a564bd733d`  
参与候选构造：`false`  
写候选文件：`false`

## 总裁决

`BLOCK FREEZE`

本轮没有新增一个与 RC-01～RC-22 不同的高影响失效类别，但证明第二轮修订尚未把已有风险真正闭合。以下问题均会允许“规范看似结构化、实际仍可被实现或证据绕过”。

## Critical

1. 候选在该固定 commit 上不能通过自身治理检查：阶段规则、结果 schema 与冻结边界的校验器仍停留在旧版本。
2. requirement、verification spec 与 acceptance case 缺少精确双向对称；宽泛的 `NF-*` 集合不能替代逐项 case 绑定。
3. 条件门允许 evidence 自报 prerequisite readiness，删除 evidence 又会退回非阻断状态；release mapping 与 transition 仍是不可执行自由文本。
4. 新增规范和 implementation target 没有被治理门完整消费，可通过删空、同步改名或从冻结边界移除来绕过。

## Major

1. assertion、operation 与公式仍只是自由文本 token，没有执行器、输入 schema 和结构化表达式。
2. 政策列表条款缺少原子 ID 与反向绑定，删除单项不会形成 orphan。
3. reverse split、ticker/name change、cash merger、stock merger、cash-in-lieu、delisting/bankruptcy 缺少逐项精确 case。

## 要求的关闭证据

- `spec ↔ case` 与 `requirement ↔ spec` 精确对称，且 mutation tests 拒绝断边。
- prerequisite 只从独立权威状态读取；gate evidence 绑定候选 commit/tree、frozen bundle、执行器、case 和原始结果 hash。
- assertion、operation、money calculation 与 invariant 使用稳定目录和可解析 selector/AST。
- 高影响政策条款具有稳定 ID 与 requirement/verification/case 绑定。
- 每类 V1 公司行动有明确 mode、状态与精确 acceptance case。
- 冻结脚本验证完整规范边界、干净 baseline 和直接远端 ref，而非只信任本地 remote-tracking ref。

## 处理决定

本审查只证明固定快照存在阻断项，不为后续修订背书。构造者可依据上述问题修改候选，但必须在新的精确 commit/tree 上重新进行独立挑战；旧审查不得被复用为新候选的通过证据。
