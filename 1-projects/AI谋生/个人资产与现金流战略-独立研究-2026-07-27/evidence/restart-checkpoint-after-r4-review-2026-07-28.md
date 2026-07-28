# 重启接续点：pre-contact successor r4 review 后

## 当前目标

继续严谨运行“个人资产与现金流”项目：恢复并治理投研纪律与机会到交易，补否决门、现实校验、本地可逆反证实验与独立验证，形成可持续活动状态。任何外部联系、发布、支付、合同、私有账户数据、真实或影子投资前均 fail closed，并精确申请用户授权。

## 安全边界

- 没有 Gmail draft、send、contact 或 follow-up。
- 没有申请、表单、登录、账户、私有数据、合同、支付或 payout。
- 没有发布或 cloud model。
- 没有真实/影子投资、broker 或 funds 动作。
- `08-活动状态.json` 仍是 predecessor，SHA-256 为 `17815b0ff22a1250f0f47d2fda22b65c344eee3d359729fa6d67a8f7d45ba2ab`；本次重启前未 transition。

## 已完成且已持久化

### 酒店 pre-contact rejection successor r4

- 独立 reviewer：`/root/ca_precontact_successor_r4_review`
- verdict：`PASS`
- severity：`0 Critical / 0 Major`
- reviewer 未修改候选，未执行外部动作。
- receipt：`evidence/review-ca012650-precontact-rejection-successor-2026-07-28-r4.json`
- receipt SHA-256：`974ee2adae78e8de01ec18ed2b27d5466e8dad558c3826cfdb17730037ee20db`
- validator SHA-256：`d77dc8c523b54efed5f9f54efada6b5bef98f6f830e4768e538d54c091a47a41`
- test SHA-256：`bb67000748c3b103569b184730bc123dc0ac87f1424bd04279a8f75075299c25`
- root 重跑：`Ran 42 tests in 13.853s`、`OK`。
- reviewer 重跑：`Ran 42 tests in 16.088s`、`OK`。
- production CLI 在 predecessor state 上 exit `1`，精确报告 `4` 个 fail-closed errors；这是预期状态，不是授权。
- 该 PASS 只审查候选代码、测试、证据与 transition contract；尚未审查或激活 mutable live `08`。

历史记录保持：

- attempt-1：`FAIL`，`1 Critical / 0 Major`，receipt SHA-256 `ee68cd328a029f3e6a954592c3a4903d78cab46c122bbd47e148fbc4f31f643e`。
- r2：review-infrastructure failure，无 verdict、无 severity、无 substantive review，receipt SHA-256 `ccf27c810fdf80c4429f874c1a128d6626905fe200280b9b0b4928e37c30d1d7`。
- r3：candidate drift `FAIL`，`1 Critical / 0 Major`，receipt SHA-256 `c13e058342a1c9035ed6134740306413af77f0dfbdaf00c3a1ce343f5ae32a57`。

### 现实需求 leads r2

- locator：`evidence/demand-carrier-readonly-leads-2026-07-28.json`，SHA-256 `eef6bdcbff766cf3b20e2eb694c68541eb8c6858ad35b886f761e2d5a568295a`。
- independent review receipt：`evidence/review-demand-carrier-readonly-leads-2026-07-28-r2.json`，SHA-256 `863e2b5c1159553dcc2e566d29ece1aa205ea979a9c73fd3ee58e00f7580be8e`，`PASS 0 Critical / 0 Major`。
- `6` 条记录均是 locator，`0` 条达到 Gate-evidence-qualified cashflow candidate，`0` 条 application-ready；外部状态仍是 `BLOCKED_NOT_AUTHORIZED`。

## 未完成，不得冒充候选或完成态

### `15-需求优先的现实实验重设计.md`

- 当前 SHA-256：`49197881c7fb8ec9bf2a21da5e4dc6fe55bd43b4f4d8d1f1e2778281aebbd8cc`。
- 当前状态必须视为 `PARTIAL_NOT_CANDIDATE`。
- r4 review receipt：`evidence/review-demand-first-redesign-2026-07-28-r4.json`，SHA-256 `60b38758783853d887cb77a41c32cad9cfca8341debd4f340a48c5e230af83ef`，`FAIL 2 Critical / 3 Major`。
- 已部分加入：r4 FAIL binding、external trust-root/principal framework、UNKNOWN self-transition、pre-call-crash terminal、cross-authorization active-effect index 初版。
- 尚未闭合：semantic projection schema 与 effect-key encoder 尚未在 GateReceipt、guard、ActionAttempt 全链路绑定；cross-policy namespace/migration 尚未完全同步和独立审查；尚无 local development smoke。
- 不得称为 r5 candidate，不得创建 PASS receipt，不得据此执行外部动作。

### 投研纪律系统

- 下一步仍是 `ACT-METHOD-RUNTIME-FOUNDATION`。
- 状态仍 blocked：`GATE-DESIGN-FREEZE-OPEN-FINDINGS`、`GATE-DESIGN-FREEZE-AUTHORITY-MISSING`。
- 活跃 R5 临时 worktree `/private/tmp/ids-recovery-r4-review.BYwzIK/repo` 仍为 dirty candidate；不得清理、提交或声称 recovered。
- 没有真实或影子投资动作。

### 单独的“创意实现自动化”任务

- thread id：`019fa520-5072-7b60-8216-167f431d57e7`。
- 它仍在从第一性原理做总体设计研究；尚未完成，不干预其并行目录，不据此联系市场或发布产品。

## 重启后的精确恢复顺序

1. 读取项目 `AGENTS.md` 与本检查点；先 dump 当前状态，不从旧聊天印象直接行动。
2. 严格解析 r4 receipt，复核 receipt/validator/test/live-08 的 SHA-256；重跑 `42` 项测试与 predecessor production CLI。
3. 只有上述全部稳定后，才使用测试 helper `tests.ActiveStateValidatorTests.rejected_state(review)` 构造 terminal rejected `08`，并用 `apply_patch` 写入；不得手工放宽字段。
4. 对 transition 后 live `08` 重跑 CLI/tests，并交给新的独立只读 reviewer 做 post-transition review；在此之前不得声称 live state 已被审查或激活。
5. 再恢复 demand r5 partial，先闭合 effect-key encoder 的 GateReceipt → guard → ActionAttempt 全链，再冻结候选并独立审查。
6. 最后统一审计活动状态、投研纪律系统以及“创意实现自动化”任务；任何外部动作继续 fail closed。

## 恢复时的第一句判断

当前是“pre-contact successor r4 候选审查已 PASS 并持久化，但 live `08` 尚未 transition；demand r5 仍是 partial；投资恢复仍 blocked；所有外部动作均未获授权”。
