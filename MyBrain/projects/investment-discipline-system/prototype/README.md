# 纵切片原型

这是投研纪律系统的纸面闭环原型，只包含确定性流程验证，不连接真实券商，也不执行真实交易。

## 运行测试

在项目目录执行：

    python3 -m unittest discover -s prototype/tests -v

原型目前验证：

- 合法纸面操作可以通过风险闸门。
- 超过额度或频率限制的操作会被拒绝。
- 决策不能使用决策时点之后的信息。
- 追加式记录链可以发现事后修改。
- 数据快照必须记录来源版本、原始响应哈希，以及每条记录的观察时间和可见时间。
- 执行适配器返回结构化的成交、拒绝或未知结果；本地纸面适配器不具备真实交易路径。

## 运行真实来源纸面案例

先准备本地来源文件，再运行：

    python3 -m prototype.run_real_data_case

案例只使用保存于 prototype/data/raw/ 的 FRED CSV，结果写入 prototype/data/runs/real_data_case_v2/。来源哈希和计算版本变化时禁止覆盖旧结果；原始数据和运行产物默认不进入版本库，发布前必须单独检查数据许可。

## 运行历史检验案例

    python3 -m prototype.run_real_data_backtest

该案例使用固定基准规则，分开开发区间和留出区间，并把成本、基准和无未来信息审计写入 prototype/data/runs/backtest_v1/。

## 运行连续纸面套件

    python3 -m prototype.run_paper_suite

该套件在同一一本地账户和追加式账本中覆盖合法成交、风险拦截、人工偏离、执行失败和复盘。它使用受控夹具，不代表市场表现。

## 运行统一研究原型

    python3 -m prototype.run_unified_prototype_case

该案例把开发/留出历史检验、纸面工作流、账本和复盘写入同一条运行链；它使用受控夹具，只验证模块连接。

## 运行真实来源统一研究案例

    python3 -m prototype.run_real_data_unified

该案例使用已经保存的 FRED CSV，把来源哈希、决策快照、历史检验、纸面工作流和复盘写入同一条账本；仍然不连接真实券商。

## 运行契约故障注入

    python3 -m prototype.run_contract_faults

该案例验证未来可见数据、异常成交状态、未知状态和重复订单号的拒绝/待对账路径。

## 原型模块

- discipline_system.py：证据、建议、决定、风险闸门和账本。
- contracts.py：供应商无关的数据快照与执行适配器契约。
- backtest.py：历史检验和留出审计。
- paper.py：本地纸面现金、持仓和成交。
- workflow.py：把风险闸门和本地纸面执行串成不可跳过的中间层。
- run_real_data_case.py：真实来源纸面案例。
- run_real_data_backtest.py：真实来源历史检验案例。
- run_paper_suite.py：连续纸面运行和分支覆盖案例。
- research_run.py：把历史检验结果记录为统一研究运行事件。
- run_unified_prototype_case.py：统一研究运行的受控端到端案例。
- run_real_data_unified.py：保存的 FRED 来源统一研究案例。
- run_contract_faults.py：数据/执行契约的本地故障注入案例。
