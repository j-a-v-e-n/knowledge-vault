# 市场、数据与纸面券商｜暂定约束

## 暂定 MVP 范围

- 市场：美国上市股票和 ETF。
- 节奏：日线数据支撑周、月尺度的研究与决定。
- 执行：先不接券商；纸面执行由本地原型负责。
- 基准：正式系统优先寻找总回报基准；FRED 的价格指数只用于原型管线。
- 架构：研究、闸门、账本和复盘保持券商中立。

这不是最终投资市场决定，而是让系统有一个可以继续搭建和验证的暂定边界。

## 选择理由

- 与原始构想的成熟市场、中长线和个人使用边界一致。
- 数据、纸面交易和研究工具的公开资料较多，容易做复现和对照。
- 日线和低频节奏降低实时系统、延迟和高频执行带来的额外复杂度。
- 股票和 ETF 的交易对象、风险规则和基准关系比多资产系统更容易先形成闭环。

## 数据来源路径

### 原型来源：FRED

FRED 提供可导出的日收盘序列，适合验证来源保存、快照哈希、时间边界和基准比较。当前使用的序列是价格指数，不含分红，不能直接作为正式总回报基准。

来源：[SP500](https://fred.stlouisfed.org/series/SP500)、[NASDAQCOM](https://fred.stlouisfed.org/series/NASDAQCOM)、[FRED 导出说明](https://fredhelp.stlouisfed.org/fred/graphs/share-my-fred-graph/export-options/)

### 正式数据仍需选择

正式系统需要能处理：

- 复权价格、拆分、分红和公司行动。
- 历史快照、修订记录和可重现的获取时间。
- 个股退市和生存者偏差。
- 新闻或基本面数据的发布日期与可见时间。
- 使用许可、下载限制、成本和长期可维护性。

## 纸面执行候选

### Alpaca Paper Trading

Alpaca 提供纸面环境，订单不发送到真实交易所，而是基于实时行情模拟成交；官方同时明确说明纸面成交与活跃市场的真实行为可能存在差异。[纸面与实盘差异](https://alpaca.markets/support/difference-paper-live-trading)

其市场数据 API 同时提供历史和实时接口，并有 Python、Go、NodeJS 和 C# SDK；个人 Trading API 的基础数据覆盖和交易所范围存在限制，不能直接把“有 API”理解成数据完整。[Market Data API](https://docs.alpaca.markets/us/docs/about-market-data-api)

暂定判断：适合作为未来纸面适配器的第一候选，但要先验证成交、数据覆盖、权限和本地账本对账。

### Interactive Brokers

IBKR 的纸面账户和 API 更接近成熟券商环境，但 Client Portal API 对本机网关、浏览器登录、单一交易会话和再次认证有明确约束；纸面账户也存在成交和订单类型模拟差异。[Client Portal API](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/) [Paper Trading](https://www.interactivebrokers.com/en/trading/tws.php)

暂定判断：作为更成熟的备选适配器，不作为当前第一实现；集成复杂度和会话约束需要先做小规模验证。

### QuantConnect Paper Trading

QuantConnect 可用实时数据配合虚拟资金，并提供回测、纸面和多种资产支持；官方文档也列出了其默认费用、成交和滑点模型的具体边界。[QuantConnect Paper Trading](https://www.quantconnect.com/docs/v2/cloud-platform/live-trading/brokerages/quantconnect-paper-trading)

暂定判断：适合作为研究与回测环境候选，但核心账本、证据和风控不应依赖平台内部状态。

## 进入下一阶段的门槛

- 对候选数据源做一次保存、重跑、修订和缺失值试验。
- 对候选纸面路径做只读账户、纸面订单、成交回报和账本对账试验。
- 明确纸面模拟和正式交易之间的差异清单。
- 在没有通过这些门槛前，不创建真实交易执行路径。

## 最新调研后的调整

- 数据和执行核心继续保持供应商中立；候选供应商只能通过适配器进入。
- yfinance 不进入正式唯一数据源清单，只保留研究便利和交叉检查用途。
- Tiingo 进入正式日线数据候选，先验证复权、分红、拆分、覆盖、修订、许可和重跑。
- Alpaca 仍是外部纸面执行第一候选，但纸面成交模型、数据计划和本地账本对账必须先完成验收。
- IBKR 保留为第二候选，认证、单一会话和持续保活是接入前的硬约束。
