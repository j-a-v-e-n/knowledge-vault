## Research result: RESEARCH-REFRESH-R7 / RS-04

结论：当前 Paper V1 不应以任何被审查系统整体替换现有核心。可安全复用的是原子模式、只读外部 oracle 和下游账本投影；Vibe-Trading、AI trading harness、完整回测或 live engine 均不应进入决策、风险闸门、执行或权威 ledger 路径。

研究状态为 `bounded_incomplete`：必需来源类别和反证均已覆盖，但查询预算耗尽后，没有剩余检索验证最后一次 architecture delta 的稳定性。

### Sources consulted

- `3a1bbe…:research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json` — 冻结问题、预算、筛选和停止规则。
- `3a1bbe…:research/VIBE_TRADING_REUSE_REVIEW_2026-07-25.md` — Vibe 旧审查基线及故障注入结果。
- [Vibe-Trading `8903f10…`](https://github.com/HKUDS/Vibe-Trading/tree/8903f10d0cbd3a550c26159c5b1047a89da9c1d9) — 当前代码、MIT/NOTICE、依赖、backtest、live 与 hypothesis 实现。
- [Vibe 外部安全审计](https://github.com/HKUDS/Vibe-Trading/issues/476)、[政府安全公告](https://isomer-user-content.by.gov.sg/36/5d5ee95a-41e6-4c77-b9f8-84250ce39e0f/01_Jul_2026.pdf) — 独立攻击面和历史 CVE。
- [TradingAgents `a33fd4c…`](https://github.com/TauricResearch/TradingAgents/tree/a33fd4c0f134485a43553a2c23a63cb14adbd88f) — Apache-2.0、多代理模拟、非确定性声明、依赖与测试配置。
- [FinRL `2334a5f…`](https://github.com/AI4Finance-Foundation/FinRL/tree/2334a5fe6d30629157f13c3b0319e1637e15e123) — MIT、经典 train-test-trade、Alpaca surface 及被 FinRL-X 替代状态。
- [Qlib `79633dd…`](https://github.com/microsoft/qlib/tree/79633dd9506ea689e5400dea0197717b5b3d74b7) — MIT、PIT 数据、Data Handler、依赖及数据限制。
- [LEAN `cd52034…`](https://github.com/QuantConnect/Lean/tree/cd52034ddf55c0c9aa57264d2a148e563924100f) — Apache-2.0、事件驱动接口、回测/live 配置和回归测试。
- [NautilusTrader `54ec803…`](https://github.com/nautechsystems/nautilus_trader/tree/54ec8032f746bd0e7c7b5b0ad4fb976572d47649) — LGPL-3.0、确定性时间模型、live adapters、供应链安全和版本风险。
- [vectorbt `f989752…`](https://github.com/polakowo/vectorbt/tree/f9897528f675114e6b34790178dbb2ca137acb51) — Commons Clause、矩阵化回测、参数扫描和可选 broker 依赖。
- [Zipline-reloaded `943010b…`](https://github.com/stefan-jansen/zipline-reloaded/tree/943010b9da848e317fc520de87edade2b884d329)、[Backtrader `b853d7c…`](https://github.com/mementum/backtrader/tree/b853d7c90b6721476eb5a5ea3135224e33db1f14) — 成熟事件回测、维护和 copyleft 边界。
- [Beancount `a3cb3fd…`](https://github.com/beancount/beancount/tree/a3cb3fd9f946d6213dd350fb87709a8ef198301d)、[Portfolio Performance `2148c6d…`](https://github.com/portfolio-performance/portfolio/tree/2148c6dd0652a4d1ddedd3fe988730708b4dde5c) — 双重记账和投资组合对账工具。

### Counted queries + UTC

检索引擎按每批返回去重后的可见结果集合，因此筛选 receipt 按批次记录。

| Retrieval-start UTC | Exact query |
|---|---|
| `2026-07-25T15:43:42Z` | `HKUDS Vibe-Trading GitHub license tests live trading audit` |
| `2026-07-25T15:43:42Z` | `"HKUDS/Vibe-Trading" issue bug lookahead data leakage security` |
| `2026-07-25T15:43:42Z` | `TradingAgents GitHub license paper trading live trading tests` |
| `2026-07-25T15:43:42Z` | `"Vibe-Trading" benchmark results independent reproduction success -site:github.com/HKUDS/Vibe-Trading` |
| `2026-07-25T15:43:58Z` | `Qlib GitHub license point-in-time data leakage backtest tests` |
| `2026-07-25T15:43:58Z` | `LEAN Engine GitHub license live trading security deterministic backtest` |
| `2026-07-25T15:43:58Z` | `vectorbt zipline-reloaded backtrader GitHub license maintenance lookahead bias` |
| `2026-07-25T15:43:58Z` | `Beancount Portfolio Performance GitHub license tests portfolio ledger` |

### Complete visible-result screening

<details>
<summary>展开完整筛选集合</summary>

`2026-07-25T15:43:42Z`：

- **VIBE-UPSTREAM，纳入但由 pinned revision 替代缓存**：[README](https://github.com/HKUDS/Vibe-Trading/blob/main/README.md)、[Releases](https://github.com/HKUDS/Vibe-Trading/releases)；用于定位功能、安全修订和 license。
- **VIBE-MIRROR，排除重复**：[t.co GitHub redirect](https://t.co/u7K8SbVsbU)、[QuickBooks mirror](https://quickbooks-ai.org/?_=%2FHKUDS%2FVibe-Trading%23zUXcvxMRZtzqyEwTQ70%2Fw8pc)。
- **VIBE-ACTIVITY，仅作活动度交叉核对**：[OSSInsight](https://ossinsight.io/analyze/HKUDS/Vibe-Trading)；不支持安全或正确性 claim。
- **VIBE-SECURITY，纳入历史攻击面**：[CVE platform](https://cve.imfht.com/intel/654310?lang=en)、[Security Bulletin](https://isomer-user-content.by.gov.sg/36/5d5ee95a-41e6-4c77-b9f8-84250ce39e0f/01_Jul_2026.pdf)；受影响范围为旧版本，不当作当前 exploitability。
- **VIBE-SECONDARY，排除宣传性转述**：[腾讯云文章](https://cloud.tencent.com/developer/article/2701447)。
- **TRADINGAGENTS-UPSTREAM，纳入同一上游簇**：[GitHub](https://github.com/TauricResearch/TradingAgents)、[项目站](https://tradingagents-ai.github.io/)、[产品站](https://tradingagents.co/)、[文章页](https://tradingagents.co/articles)、[论文](https://arxiv.org/abs/2412.20138)；文章页只作功能定位。
- **TRADINGAGENTS-PACKAGE，排除 lineage 不清**：[PyPI](https://pypi.org/project/tradingagents/) 的示例指向另一 fork，不能独立证明 canonical repo。
- **COUNTER-BENCHMARK，纳入邻近反证背景**：[When Agents Trade](https://arxiv.org/abs/2510.11695)、[LiveTradeBench](https://arxiv.org/abs/2511.03628)；说明静态回测与 live competence 存在研究缺口，不证明任何候选可复用。
- **ADJACENT-PAPER，排除非同题**：[Fin-Analyst](https://arxiv.org/abs/2607.12233)、[TradeMaster](https://papers.nips.cc/paper_files/paper/2023/file/b8f6f7f2ba4137124ac976286eacb611-Paper-Datasets_and_Benchmarks.pdf)、[HKUST thesis](https://repository.hkust.edu.hk/ir/bitstream/1783.1-123947/1/991013114548503412.pdf)、[VUT thesis](https://dspace.vut.cz/server/api/core/bitstreams/ccd63aba-d714-41cb-b067-8a430f91826e/content)；未直接回答当前组件边界。
- **USER-REPORT，背景保留、不承重**：[broker-plugin 难点](https://www.reddit.com/r/aiagents/comments/1ruewlg/why_building_broker_plugins_for_ai_trading_is/)、[AI options 两日结果](https://www.reddit.com/r/IndiaAlgoTrading/comments/1ufx0gn/built_an_ai_options_trading_agent_paper_trading/)、[agent sandbox](https://www.reddit.com/r/TechGhana/comments/1uw8ovx/i_built_an_ai_trading_sandbox_where_agents/)、[prediction-market experiment](https://www.reddit.com/r/algotrading/comments/1t5g16p/1000_trades_hypothesis_ai_agents_are_more_ratinal/)；均无 pinned code 与独立复现。
- **USER-TOOL，排除未成熟/非同题**：[PaperTrade India](https://www.reddit.com/r/IndiaAlgoTrading/comments/1uv8grj/built_an_opensource_papertrading_broker_for/)、[Open-Papertrade](https://www.reddit.com/r/developersIndia/comments/1rf6zbd/launching_openpapertrade_beta_release_on_github/)、[generic open-source tool](https://www.reddit.com/r/opensource/comments/112vhhh) 及其 [SideProject](https://www.reddit.com/r/SideProject/comments/112vhzy)、[GitHub](https://www.reddit.com/r/github/comments/112vhpk) crossposts。
- **USER-NOT-RECOVERABLE，排除**：[removed algotrading thread](https://www.reddit.com/r/algotrading/comments/1u6w3ra/removed/)、[removed IndiaAlgoTrading thread](https://www.reddit.com/r/IndiaAlgoTrading/comments/1u062qe/removed/)、[live tester 招聘](https://www.reddit.com/r/onlineservicesPH/comments/1symv73/hiringlive_trading_tester_qa_trading_platform/)。
- **UNRELATED，排除**：[HKEX April filing](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0422/2026042200059.pdf)、[HKEX March filing](https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0330/sehk26031901131.pdf)。
- **BACKGROUND，canonical source 取代**：[QuantConnect Wikipedia](https://en.wikipedia.org/wiki/QuantConnect)。

`2026-07-25T15:43:58Z`：

- **LEAN-MIRROR，排除 fork**：[Trading-Lab fork](https://github.com/Trading-Lab/Lean-Algorithmic-Trading-Engine)、[LeanFromQC](https://github.com/MagicSpins/LeanFromQC)。
- **LEAN-UPSTREAM，纳入同一上游簇**：[canonical repo](https://github.com/QuantConnect/Lean)、[lean-cli](https://github.com/QuantConnect/lean-cli)、[lean-cli README](https://github.com/QuantConnect/lean-cli/blob/master/README.md)、[CLI docs](https://www.lean.io/cli/)、[engine site](https://www.lean.io/)；[Wikipedia](https://en.wikipedia.org/wiki/QuantConnect) 仅作重复背景。
- **QLIB-UPSTREAM，纳入**：[PIT maintainer documentation](https://qlib.readthedocs.io/en/stable/advanced/PIT.html)。
- **NAUTILUS-UPSTREAM，纳入**：[canonical repo](https://github.com/nautechsystems/nautilus_trader)。
- **VECTORBT-FORK，排除并改用 canonical locator**：[johnsisibarani fork](https://github.com/johnsisibarani/vectorbt)。
- **STRATEQUEUE，排除**：[repo](https://github.com/StrateQueue/StrateQueue) 自称部分 broker integration “Implemented (not tested)”，且为 AGPL、live-first。
- **BEANCOUNT-ADJACENT，非权威 ledger**：[Fava](https://github.com/beancount/fava)、[fava-portfolio-returns](https://pypi.org/project/fava-portfolio-returns/)；只适合作下游展示。
- 对 Zipline、Backtrader、canonical vectorbt、Beancount core、Portfolio Performance 没有可见命中；使用已知 canonical repo 直接 locator 补齐，没有增加 discovery query。

</details>

### Key findings

1. **Vibe-Trading 整体继续排除。** 当前 `8903f10…` 比旧审查 revision 前进 `39` 个 commits，但 compare 集合未触及关键 provenance、global causality、hypothesis 或 live-audit 文件；当前 smoke 仍重现三个失效。其 README 还明确包含 authorized autonomous broker trading，与 Paper V1 边界冲突。[compare](https://github.com/HKUDS/Vibe-Trading/compare/8643fcd357ccffb639892dfd7add2974fceb123a...8903f10d0cbd3a550c26159c5b1047a89da9c1d9)、[README](https://github.com/HKUDS/Vibe-Trading/blob/8903f10d0cbd3a550c26159c5b1047a89da9c1d9/README.md#L247)

2. **Vibe 的数据来源证明仍可被错误归因。** `_get_loader(source)` 可以返回 fallback class，但 `fetch_data_map` 仍把请求名放入 `effective_sources`；current-head smoke 输出 `actual_fallback` 与 `requested_source` 不一致。[loader registry](https://github.com/HKUDS/Vibe-Trading/blob/8903f10d0cbd3a550c26159c5b1047a89da9c1d9/agent/backtest/loaders/registry.py#L188-L248)、[runner](https://github.com/HKUDS/Vibe-Trading/blob/8903f10d0cbd3a550c26159c5b1047a89da9c1d9/agent/backtest/runner.py#L1148-L1233)

3. **局部 look-ahead 修复不等于全局未来信息隔离。** Vibe 把整个 `data_map` 一次交给策略；位置延后一 bar，但自定义策略中的 `shift(-1)` 通过当前 AST 检查。Qlib 的 PIT 模式可借鉴，但其文档明确当前设计限于季度或年度 fundamental factors，不能直接证明 bar-level causality。[Vibe engine](https://github.com/HKUDS/Vibe-Trading/blob/8903f10d0cbd3a550c26159c5b1047a89da9c1d9/agent/backtest/engines/base.py#L490-L550)、[Qlib PIT](https://github.com/microsoft/qlib/blob/79633dd9506ea689e5400dea0197717b5b3d74b7/docs/advanced/PIT.rst)

4. **TradingAgents 与 FinRL 适合思想实验，不适合权威路径。** TradingAgents 明示结果受模型、温度、数据和非确定因素影响，且依赖 LangGraph、LLM/data keys 和 Backtrader；FinRL 当前 repo 自称教育/研究框架，并把 production/live 路径转交 FinRL-X。[TradingAgents README](https://github.com/TauricResearch/TradingAgents/blob/a33fd4c0f134485a43553a2c23a63cb14adbd88f/README.md)、[FinRL README](https://github.com/AI4Finance-Foundation/FinRL/blob/2334a5fe6d30629157f13c3b0319e1637e15e123/README.md)

5. **LEAN 与 NautilusTrader 提供最强的原子架构模式。** 可借鉴数据源/交易处理接口分离、事件时间模型、research/live 语义一致性和 release-security admission；但整包引入会同时带入 C#/Docker 或 Rust/Python、live broker、凭据和长期版本维护。[LEAN `IDataFeed`](https://github.com/QuantConnect/Lean/blob/cd52034ddf55c0c9aa57264d2a148e563924100f/Engine/DataFeeds/IDataFeed.cs)、[`ITransactionHandler`](https://github.com/QuantConnect/Lean/blob/cd52034ddf55c0c9aa57264d2a148e563924100f/Engine/TransactionHandlers/ITransactionHandler.cs)、[Nautilus security](https://github.com/nautechsystems/nautilus_trader/blob/54ec8032f746bd0e7c7b5b0ad4fb976572d47649/SECURITY.md)

6. **vectorbt/Zipline 只能成为隔离的差分 oracle。** vectorbt 的矩阵化参数扫描便于交叉核算，却放大 whole-array leakage 和多重试验风险，且 Commons Clause 限制出售；Zipline 事件流更接近因果回测，但 Cython、bcolz、calendar、SQL 依赖与维护集中度较高。[vectorbt license](https://github.com/polakowo/vectorbt/blob/f9897528f675114e6b34790178dbb2ca137acb51/LICENSE.md)、[Zipline dependencies](https://github.com/stefan-jansen/zipline-reloaded/blob/943010b9da848e317fc520de87edade2b884d329/pyproject.toml)

7. **Beancount/Portfolio Performance 可复用为下游投影，不可替代权威 ledger。** 双重记账、balance assertions、报表和导入 UI 有用，但它们不保存决策时证据、模型输入、risk-gate 结果或 hash-chain provenance。[Beancount metadata](https://github.com/beancount/beancount/blob/a3cb3fd9f946d6213dd350fb87709a8ef198301d/pyproject.toml)、[Portfolio Performance](https://github.com/portfolio-performance/portfolio/blob/2148c6dd0652a4d1ddedd3fe988730708b4dde5c/README.md)

### Claims support scope

| Claim | Entailment | Exact support | Limitation |
|---|---|---|---|
| Vibe 会误记 fallback 来源 | `entailed` | 当前 code range + exit `0` smoke | 只覆盖显式 source 经 registry fallback 的路径 |
| Vibe 没有全局未来信息隔离 | `entailed` | full `data_map` 调用边界 + `shift(-1)` smoke | 不表示每个 bundled strategy 都泄漏 |
| Vibe hypothesis/live state 不满足本项目门槛 | `entailed` | `update(status=...)`、order-before-audit、audit exception、count corruption paths | live audit 未再做动态 broker smoke；以 current source 为证 |
| Qlib/LEAN/Nautilus 含可借鉴原子模式 | `entailed` | PIT schema、interfaces、deterministic time/security docs | 尚未证明接入本项目后的净收益 |
| 所有整包均应排除 | `decision-fit` | license、surface、时序与依赖矩阵 | 是针对当前 Paper V1 的边界判断，不是断言这些项目本身无用或错误 |

### Reuse / exclusion matrix

| Candidate | License / latest inspected activity | Safe reuse boundary | Exclude from Paper V1 |
|---|---|---|---|
| Vibe-Trading | MIT；`8903f10…`，`2026-07-25T15:01:23Z` | strict JSON、hash manifest、run-card 字段和 invalidation 字段；自行重写 | whole fork、agent runtime、shadow account、validation、hypothesis registry、live connectors/audit |
| TradingAgents | Apache-2.0；`a33fd4c…`，`2026-07-18T15:55:04Z` | bull/bear/risk 分栏和 checkpoint 概念，作为提示模板 | LLM graph、memory authority、simulated exchange、Backtrader transitively |
| FinRL | MIT；`2334a5f…`，`2026-07-12T06:22:09Z` | Gym-style environment 作为隔离实验夹具 | classic framework、RL reward authority、Alpaca/live 模块；当前 repo 已指向 FinRL-X |
| Qlib | MIT；`79633dd…`，`2026-07-23T08:15:29Z` | publication-date PIT schema、data-health checks、Data Handler 思路 | 整包依赖、online/order execution、把 quarterly PIT 外推成通用 causality |
| LEAN | Apache-2.0；`cd52034…`，`2026-07-23T18:59:55Z` | `IDataFeed`/`ITransactionHandler` 分离、事件/订单状态语义 | C#/Docker engine、broker config、live/cloud CLI |
| NautilusTrader | LGPL-3.0；`54ec803…`，`2026-07-25T13:34:37Z` | deterministic clock/event model、release-security checklist；未来可做同题试验 | 当前 core dependency、live adapters、compiled runtime；维护者警告 breaking changes |
| vectorbt | Apache-2.0 + Commons Clause；`f989752…`，`2026-07-14T12:35:23Z` | 固定 snapshot 上的隔离差分核算与可视化 | 核心依赖、商业可迁移性、whole-array 策略权威、parameter sweep 结论 |
| Zipline-reloaded | Apache-2.0；`943010b…`，`2025-11-13T15:14:32Z` | 事件流/calendars 的外部测试 oracle | Cython/bcolz/SQL 栈及维护耦合 |
| Backtrader | GPLv3+；`b853d7c…`，`2023-04-19T14:13:08Z` | 仅作历史语义参考 | whole dependency、live IB/Oanda、cheat modes、低活跃信号 |
| Beancount | GPL-2.0-only；`a3cb3fd…`，`2026-05-18T12:28:06Z` | 单向 export + 独立 `bean-check` 对账 | 权威 ledger、源代码复制、覆盖原事件链 |
| Portfolio Performance | EPL-1.0；`2148c6d…`，`2026-07-25T04:47:13Z` | 外部只读复核、UI/报表基准 | Java/Eclipse 嵌入、决策或 ledger authority |

### Counterevidence

- Vibe 当前 README 声称外部审计 findings 已关闭，并记录 portfolio optimizer 的 look-ahead 修复；当前版本是 `0.1.12`，政府公告中的 CVE 范围是 “before `0.1.10`”。因此这些报告只能证明历史攻击面和维护成本，不能证明当前版本仍存在对应 CVE。
- TradingAgents `0.3.1` 增加 Alpha Vantage look-ahead filtering、checkpoint correctness 和 CI gate。
- NautilusTrader 有确定性时间模型、锁文件、signed/attested releases、daily security scanning 和清晰 disclosure policy。
- 这些反证否定“所有开源投研软件都不安全”的笼统命题；但没有改变当前 Paper V1 不整体接入的边界结论。
- 专门的 positive counterquery 没找到 Vibe 的 version-pinned 独立 performance reproduction；可见命中主要是维护者材料、邻近论文和不可复核用户叙述。

### Architecture delta

| Action | Delta |
|---|---|
| 保持 | `DataSnapshot/DataSource → AI advice → human decision → deterministic gate → PaperAccount → tamper-evident ledger` 不变 |
| 新增 | `ExternalResearchAdapter`：只接收冻结 snapshot，只返回标准化候选结果，不得访问 execution 或 ledger 写端 |
| 新增 | `ExternalComponentManifest`：固定 repo、commit、license、dependency lock、live surface、命令、exit、输出 hash 和失效条件 |
| 新增 | `DifferentialOracle`：vectorbt/Zipline/LEAN/Nautilus 只能作为非权威交叉核算器；分歧进入 review，不自动选赢家 |
| 新增 | `LedgerProjection`：从权威 ledger 单向导出 Beancount/Portfolio Performance；禁止反向覆盖事件链 |
| 强化 | fallback 必须记录 requested/actual source 与完整链；prefix-causality 行为测试继续作为硬门 |
| 拒绝 | 任何 live connector、autonomous mandate、LLM portfolio-manager authority 或外部 mutable ledger |

### Temporary smoke receipts

临时 clone 固定在 `8903f10d0cbd3a550c26159c5b1047a89da9c1d9`，未安装依赖、未提供凭据；完成后临时目录已删除，删除与不存在检查均 exit `0`。

全 pytest probe：

```bash
python3 -c 'import pandas, pydantic, pytest; print("imports_ok")'
```

实际：exit `1`，`ModuleNotFoundError: No module named 'pytest'`。按边界没有安装 pytest。

来源归因：

```bash
python3 -c 'import sys,json; sys.path.insert(0,"agent"); import pandas as pd; from backtest import runner; frame=pd.DataFrame({"open":[1.0],"high":[1.0],"low":[1.0],"close":[1.0]},index=pd.DatetimeIndex([pd.Timestamp("2026-01-01")])); ActualFallback=type("ActualFallback",(),{"name":"actual_fallback","fetch":lambda self,codes,start_date,end_date,**kwargs:{codes[0]:frame}}); runner._get_loader=lambda source:ActualFallback; result=runner.fetch_data_map({"codes":["AAPL.US"],"start_date":"2026-01-01","end_date":"2026-01-02","source":"requested_source","interval":"1D"}); print(json.dumps({"actual_loader":result.loader.name,"effective_sources":result.effective_sources,"source":result.source},sort_keys=True))'
```

实际 exit `0`：

```json
{"actual_loader": "actual_fallback", "effective_sources": ["requested_source"], "source": "requested_source"}
```

未来信号静态检查：

```bash
python3 -c 'import sys,ast; sys.path.insert(0,"agent"); from backtest import runner; source="class SignalEngine:\n    def generate(self, data):\n        return {\"AAPL.US\": data[\"AAPL.US\"][\"close\"].shift(-1)}\n"; runner._scan_runtime_reachable(ast.parse(source)); print("future_signal_static_check=ACCEPTED")'
```

实际 exit `0`：

```text
future_signal_static_check=ACCEPTED
```

无 run-card 验证：

```bash
python3 -c 'import sys,json,tempfile,pathlib; sys.path.insert(0,"agent"); from src.hypotheses.registry import HypothesisRegistry; d=tempfile.TemporaryDirectory(prefix="rs04-hyp-"); r=HypothesisRegistry(pathlib.Path(d.name)/"hypotheses.json"); h=r.create(title="t",thesis="x"); h=r.update(h.hypothesis_id,status="validated"); print(json.dumps({"run_cards":h.run_cards,"status":h.status},sort_keys=True)); d.cleanup()'
```

实际 exit `0`：

```json
{"run_cards": [], "status": "validated"}
```

### Verbatim quotes

> “auditing must never block a decision” ([Vibe `order_guard.py`](https://github.com/HKUDS/Vibe-Trading/blob/8903f10d0cbd3a550c26159c5b1047a89da9c1d9/agent/src/live/order_guard.py#L640-L667))

> “If we only use the latest version for historical backtesting, data leakage will happen.” ([Qlib PIT](https://github.com/microsoft/qlib/blob/79633dd9506ea689e5400dea0197717b5b3d74b7/docs/advanced/PIT.rst))

> “Trading performance may vary based on many factors” ([TradingAgents README](https://github.com/TauricResearch/TradingAgents/blob/a33fd4c0f134485a43553a2c23a63cb14adbd88f/README.md))

> “This repository (`FinRL`) preserves the original end-to-end educational and research framework.” ([FinRL README](https://github.com/AI4Finance-Foundation/FinRL/blob/2334a5fe6d30629157f13c3b0319e1637e15e123/README.md))

> “breaking changes can occur between releases.” ([NautilusTrader README](https://github.com/nautechsystems/nautilus_trader/blob/54ec8032f746bd0e7c7b5b0ad4fb976572d47649/README.md))

### ⚠️ 矛盾或不确定

- 缓存的 Vibe 搜索摘要称“不执行 live trades”，而 pinned README 明示 authorized autonomous broker trading；两者属于 revision 冲突，当前 commit 记录后者。
- 外部 Vibe audit 与政府公告对应修复前状态；它们不支持“当前版本仍可利用”。
- FinRL classic repo 明确把 production 路径转交 FinRL-X，但预算内没有审查 FinRL-X，因此不能对后者下安全结论。
- 独立安全/用户证据集中在 Vibe；其余候选主要由源码和维护者文档支持。
- 未做候选工具与当前系统的同任务、同 snapshot 差分运行，也未做法律意见级 license 评估。

### Stability and gaps

- 必需来源类别已满足：repository/code、maintainer documentation、independent security/user report。
- Vibe “整体排除、仅借鉴原子模式”在当前 revision 上未被反证推翻。
- 成熟引擎带来的新 delta 是隔离 oracle 和 ledger projection；第二批检索后没有预算执行预注册要求的 post-delta supplemental retrieval，故不能声称研究稳定闭合。
- 当前 Paper V1 决策足够稳定：不引入整包、不打开 live surface；领域充分性仍为 `bounded_incomplete`。

交付期间仓库由预注册 HEAD 前进到 `4e4c3587f1018dd02fdac822f0adb956bd41e600`，commit message 为 `vault backup: 2026-07-25 08:56:07`；ancestor check exit `0`。本轮没有写项目文件。

### Suggested next step（lead 接续用）

据此可冻结 `ExternalResearchAdapter + ExternalComponentManifest + LedgerProjection` 三项条件式 architecture delta；下一轮优先补 FinRL-X 与一个固定 snapshot 的同题外部-engine对照，并交独立 reviewer 复核 smoke 与 license 边界。

<oai-mem-citation>
<citation_entries>
MEMORY.md:119-122|note=[paper first architecture and invariants baseline]
</citation_entries>
<rollout_ids>
019f83f2-e416-7883-bc44-63190cd9e356
</rollout_ids>
</oai-mem-citation>
