# 调研索引｜投研纪律系统与 AI 协作

这里是来源登记表，不是把所有文章复制进项目。每条重要判断都应能回答：来源是谁、它属于哪类证据、它支持什么、它的边界是什么。

## 来源类型

- 官方文档：说明工具作者支持什么，不等于真实使用一定顺利。
- 开源仓库与实际产物：观察别人如何组织文件、流程和验证。
- 社区经验：发现真实痛点和替代做法，但通常是个案，不能直接当成事实。
- 独立研究：提供方法和外部检验，但要检查研究对象与本项目是否相似。
- 自己的试验：最贴近本项目，必须保留输入、过程、结果和失败记录。

## AI 协作与搭建

### Codex 与项目上下文

- 来源：[Codex best practices](https://learn.chatgpt.com/guides/best-practices)
- 类型：官方指导
- 可借鉴：明确目标、上下文、约束和完成标准；用项目上下文文件保存持久规则；先计划、再实现、再验证。
- 边界：官方推荐不等于个人项目中的实测效果，需要通过本项目验证。

### Codex 执行计划

- 来源：[Codex ExecPlans](https://developers.openai.com/cookbook/articles/codex_exec_plans)
- 类型：官方方法文档
- 可借鉴：复杂任务先写计划，计划包含现状、目标、方案、验证和风险。
- 边界：计划不能替代需求确认，也不能替代最终验收。

### 代理上下文文件

- 来源：[Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/abs/2511.12884)
- 类型：独立研究
- 可借鉴：上下文文件是持久项目记忆和持续维护的配置资产，应版本化、审查，并写清非功能要求。
- 边界：研究对象和项目环境会变化，具体结论需要在本地工作流中复核。

### 实际社区经验

- 来源：[Codex context engineering 讨论](https://www.reddit.com/r/codex/comments/1r2pw9q/read_this_or_stay_behind/)
- 类型：社区经验
- 可借鉴：社区常把上下文分层、先设计后实现、测试和复盘作为减少长任务漂移的办法。
- 边界：这是用户经验和观点，不能单独证明方法有效。

- 来源：[AI 辅助开发工作流讨论](https://www.reddit.com/r/ClaudeWorkflows/comments/1uyq0qq/workflow_optimizing_aiassisted_development_a/)
- 类型：社区经验
- 可借鉴：观察真实使用者如何安排研究、计划、实现和检查。
- 边界：需要结合更多用户、仓库和本项目试验。

### 代码审查与人类把关

- 来源：[GitHub Copilot code review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)
- 类型：官方产品文档
- 可借鉴：AI 审查可以辅助发现问题，但不能替代人类审查和合并责任。
- 边界：这是 GitHub 的功能边界，不是所有 AI 工具的统一行为。

### 文件型持续循环

- 来源：[Ralph](https://github.com/iannuttall/ralph)
- 类型：开源实际产物
- 可借鉴：每轮从磁盘状态重新开始；用任务规格、状态、进度、错误和运行日志作为记忆；一次只推进一个故事；状态文件和 Git 负责跨上下文持续性。
- 边界：它面向代码任务，具体运行方式和权限模型需要在本项目中重新验证。

### 完整软件工程 Harness

- 来源：[OpenHands](https://www.openhands.dev/)
- 类型：开源平台
- 可借鉴：将代理执行、工具调用、代码库操作、并行任务和治理控制组合成更完整的平台。
- 边界：当前项目还没有证明需要引入完整平台；平台复杂度、运行成本和权限面都需要评估。

### 事件型项目记忆与行动前判断

- 来源：[PROJECTMEM](https://arxiv.org/abs/2606.12329)
- 类型：独立研究与开源实现
- 可借鉴：用追加式事件日志保存问题、尝试、修复、决定和笔记，再生成适合 AI 读取的摘要；记忆还可以在行动前提醒重复失败。
- 边界：论文和自我研究不能直接证明它适合本项目；当前项目先用现有 Markdown 文档验证需求。

### Obsidian 项目协作运行时

- 来源：[work-buddy](https://github.com/KadenMc/work-buddy)
- 类型：开源实际产物
- 可借鉴：把 Obsidian、任务、跨会话记忆和多步骤工作流连接成个人工作运行时。
- 边界：它围绕其他代理运行时设计，当前不直接采用；需要先确认与 Codex、现有知识库结构和授权模型的兼容性。

## 原型数据来源

### FRED 日收盘序列

- 来源：[S&P 500 series](https://fred.stlouisfed.org/series/SP500)、[Nasdaq Composite series](https://fred.stlouisfed.org/series/NASDAQCOM)、[FRED export options](https://fredhelp.stlouisfed.org/fred/graphs/share-my-fred-graph/export-options/)
- 类型：官方数据平台与来源说明
- 可借鉴：可以通过 CSV 保存日收盘来源文件，用文件哈希和处理脚本保持案例可复核。
- 边界：当前序列是价格指数，不含分红；版权和再发布限制需要在公开发布前重新检查；它们只是原型来源，不是最终数据供应商决定。

### 数据供应商与纸面执行候选

- 来源：[yfinance README](https://github.com/ranaroussi/yfinance)
- 类型：开源项目维护者说明
- 可借鉴：适合个人研究和探索的便利接口可以快速验证想法。
- 边界：项目维护者明确说明它不是 Yahoo! 官方背书工具，实际数据使用受 Yahoo! 条款约束；不能把它当作正式唯一事实源。

- 来源：[Tiingo EOD 文档](https://www.tiingo.com/documentation/end-of-day)
- 类型：供应商官方技术文档
- 可借鉴：文档显式区分原始/复权价格并提供分红、拆分字段，值得作为正式日线候选进行本地验收。
- 边界：供应商描述不等于本地已经验证覆盖、许可、修订和长期可复现性。

- 来源：[Alpaca Paper Trading](https://docs.alpaca.markets/us/v1.4.2/docs/paper-trading)、[Alpaca Market Data API](https://docs.alpaca.markets/us/docs/about-market-data-api)
- 类型：券商官方文档
- 可借鉴：纸面执行和市场数据接口可作为未来外部适配器候选。
- 边界：纸面模型不等同真实市场，数据计划存在覆盖边界；不能替代本地账本与独立复盘。

- 来源：[IBKR Client Portal API](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/)、[Alpaca 社区数据限制讨论](https://forum.alpaca.markets/t/key-limitations-on-paper-trading-keys/17789)、[IBKR 社区登录实例](https://www.reddit.com/r/interactivebrokers/comments/1owcw5h)
- 类型：官方技术文档与社区经验
- 可借鉴：官方限制定义集成边界，社区实例补充登录、会话和权限摩擦的真实信号。
- 边界：社区帖子是个案，不足以单独证明普遍性；适配器必须通过本项目的对账和故障注入验收。

## 投研纪律与验证

本项目此前已调研过以下相邻方向，后续实现前需要把来源补成可逐条复核的条目：

- 历史检验、纸面交易、实时模拟和订单对账。
- 交易日志、心理记录和经过验证的绩效展示。
- 券商侧风险控制、订单前检查和审计记录。
- 数据边界、交易成本、未来信息泄漏、过拟合和留出检验。
- 基准对照、不可交易结论和策略失效监控。

## 研究纪律

- 先登记问题，再收集来源。
- 每条结论标记事实、观点、推测或待验证假设。
- 不把单一官方宣传、单个社区帖子或一次成功试验当成普遍规律。
- 需要做实现选择时，记录采用、改造、组合或自建的理由。
- 调研结果必须回到任务板、决定日志或实现计划，而不是停留在链接集合。
