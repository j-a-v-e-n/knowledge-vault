# 正式日线数据与纸面执行边界｜2026-07-25

## 当前采用判断

没有单一供应商同时满足正式日线、历史可复现证券宇宙、本地长期归档和可信纸面执行。系统必须把四个角色分开：

1. 日线价格与公司行动源。
2. 需要历史动态选股时才引入的 Security Master / point-in-time universe 源。
3. 本地确定性 PaperAccount 与事件账本。
4. 未来可选的外部 Paper 协议观察器。

“生产候选”只表示值得进入试用验收，不表示已经通过。

## 当前候选与拒绝

### 日线价格

- **Tiingo：首个试用候选。** 只用于人工维护的小型美国股票/ETF 宇宙。官方 EOD 返回 raw/adjusted OHLCV、现金分红和拆分因子，并说明晚间仍可能修订。进入正式使用前必须用固定金样本验证，并确认个人本地缓存及退订后保留权。[EOD 文档](https://www.tiingo.com/documentation/end-of-day)
- **Sharadar：需要历史选股/PIT 时优先试用。** 活跃/退市证券和历史成分较符合研究需求，但精确报价、ETF 范围、缓存与退订保留权需向供应商确认。[Sharadar](https://sharadar.com/)
- **Norgate Platinum：PIT/Security Master 备选。** 覆盖退市与历史成分，但 Windows-only 和专有本地格式给当前 Mac 环境带来明显成本。[数据内容](https://norgatedata.com/data-content-tables.php)
- **EODHD：拒绝作为本地长期主档。** 公开条款要求订阅结束后删除数据，与本地可恢复历史直接冲突；近期用户还报告缺口和公司行动错误。[条款](https://eodhd.com/financial-apis/terms-conditions)
- **Alpha Vantage、yfinance/Yahoo、Stooq：只作交叉检查或故障样本。** 不承担 canonical source 角色。

### 纸面执行

- **本地 PaperAccount 是唯一权威账。** 人工决定、闸门、订单生命周期、现金、持仓、费用和公司行动必须进入可重放事务账本。
- **Alpaca Paper 仅作为未来第二协议实现和偏差观察器。** 官方明确 Paper 不模拟市场冲击、信息泄漏、延迟滑点、队列、价格改善、监管费和分红，不能把其收益当作实盘证据。[Paper 限制](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading)
- **IBKR 首期拒绝接入。** 当前不实盘边界下，没有理由引入开户、会话认证和实盘端点耦合。
- **QuantConnect/LEAN 只作未来参考引擎或 oracle 候选。** 默认 Paper 无滑点且即时完整成交，数据许可还与 LEAN 使用绑定。[Paper 模型](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading)

## 正式数据适配器的硬要求

- 保存未调整 OHLCV、公司行动和稳定证券身份，不以 ticker 直接连接跨期身份。
- 每次抓取保存真实供应商、实际 fallback、请求参数、获取时间、覆盖区间、原始响应、规范化结果和各自哈希。
- 禁止静默 fallback；来源变化使运行进入 `incomplete` 或明确重批。
- 决策快照冻结；后续修订另存新版本，不能覆盖当时输入。
- 调整价格由本地 raw 数据、分红和拆分重算；供应商 adjusted 字段只作差异检测。
- 历史动态选股必须有 as-of universe；没有时只允许冻结的人工小宇宙。
- 数据许可必须允许个人本地存储，并明确退订后的保留边界。

## 外部 Paper 的进入门

- 独立 Paper-only 凭据与固定 Paper hostname。
- 任何 live hostname、live key 或缺少人工决定哈希的请求都 fail closed。
- 客户端幂等键；ACK 丢失、重复提交、乱序、部分成交、撤单后成交和未知状态均可重放和对账。
- 外部状态只生成差异报告，不自动覆盖本地权威账。
- 认证、网络、审计或对账失败时，不把订单标为成功。
- 任何 Paper P&L 都附带成交模型限制，不推断实盘可实现性。

## 首批故障注入

| 类别 | 注入 | 必须观察到 |
| --- | --- | --- |
| 传输 | 超时、限流、未授权、截断、格式错误 | 不生成成功快照；重试不重复写入 |
| 完整性 | 缺失、重复、乱序、陈旧或伪交易日 | 数据隔离并报告覆盖缺口 |
| 价格语义 | OHLC 自相矛盾、货币单位错误、raw/adjusted 互换 | 阻断或产生明确差异告警 |
| 公司行动 | 拆分/分红缺失、重复、方向反转、日期错误 | 本地重算可定位差异 |
| 证券身份 | ticker 改名、复用、退市、当前成员泄漏到历史 | 稳定 ID 和 as-of universe 阻断错误连接 |
| 修订 | 同一请求返回修改后的旧 bar | 保存两个哈希，原决策快照不变 |
| Feed | IEX 与 SIP 被切换 | manifest 来源不符并失败 |
| 订单 | 重复、ACK 丢失、乱序、部分成交后断线 | 幂等状态机可重放，不重复持仓 |
| 会计 | 费用/分红遗漏、持仓拆分、现金漂移 | 对账逐项列差异，不静默修正 |
| 安全 | key 过期、重启、live 地址注入 | 明确拒绝，人工批准不可绕过 |

## 无个人凭据可完成的验证边界

EODHD 和 Alpha Vantage 的共享 demo、Yahoo/yfinance 以及 Stooq 可以用于响应形状、交叉比较和故障样本验证；它们不能证明生产覆盖和质量。Tiingo、Sharadar、Norgate、Alpaca、IBKR 与 QuantConnect 的真实试用都需要注册、订阅或账户状态。

因此，本阶段可以完成：

- 供应商中立契约、原始归档、时间边界和故障注入。
- Tiingo 适配器实现及离线契约测试。
- 公开 demo 的在线只读结构探针。
- 本地 Paper 全生命周期。

在没有个人 token 的情况下不能诚实宣称：

- Tiingo 的真实账户试用已通过。
- Sharadar/Norgate 的 PIT 覆盖已通过。
- Alpaca Paper 的真实认证、成交和对账已通过。

这些保持为明确的条件性验收项，而不是伪造绿灯或阻塞本地产品。

