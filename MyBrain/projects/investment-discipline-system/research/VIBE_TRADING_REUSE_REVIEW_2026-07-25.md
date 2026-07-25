# Vibe-Trading 复用适配性审查｜2026-07-25

## 审查对象

- 仓库：`HKUDS/Vibe-Trading`
- 审查提交：`8643fcd357ccffb639892dfd7add2974fceb123a`
- 审查方式：不采信 README 宣传，读取数据、回测、假设、影子账户、live gate 与 audit 实现，并执行测试和故障注入。

## 采用结论

不 fork、不整体依赖、不把它作为本项目底座。只借鉴少量原子级模式，并在本项目中按更严格的不变量重写。

## 拒绝原因

### 数据来源会被错误归因

当请求来源不可用而实际使用 fallback loader 时，运行记录仍保存请求来源名。runner 还可能在预取后由引擎再次联网取数，导致实际回测数据与 run card 记录的第一次结果不同。

故障注入：

```json
{
  "actual_loader": "actual_fallback",
  "effective_sources": ["requested_source"],
  "source": "requested_source"
}
```

本项目要求任何 fallback 都成为显式、可拒绝的来源变更，不能静默替换。

### 没有全局未来信息隔离

策略一次收到完整历史区间；把最终 signal 向后移动一个 bar，不能阻止策略内部使用 `shift(-1)`、全样本标准化或未来排序。含未来价格的策略通过了静态检查。

本项目改用 prefix-causality 行为测试和逐时点可见数据边界，不用源码黑名单冒充因果性证明。

### “验证”不能证明策略有优势

Monte Carlo 只打乱同一组已实现交易 PnL；所谓 walk-forward 只是切分已经生成的同一权益曲线，没有重新训练、冻结、前推和独立测试。因此不能把这些输出称为 validated、significant 或 walk-forward evidence。

### Shadow Account 存在赢家选择和旧结果污染

它只从盈利交易挖规则，使用当前标的篮子回测历史，失败运行还可能读到同目录旧指标，并把一个组合指标复制成多个市场指标。

本项目若保留“影子账户”概念，只能用相同人工决定在时间隔离的独立 PaperAccount 中重放；盈利与亏损都保留，不能生成无法由市场路径重建的反事实 PnL 标签。

### Live gate 和 audit 会 fail-open

外部订单先发送，再更新计数和审计；审计写入异常被吞掉。计数文件损坏时按零处理。该实现既越过“人工最终决定、只做纸面”的边界，也违背“记录失败则状态不改变”。

全部 live connector、mandate autonomy 和现有 audit 写法拒绝进入本项目。

### 假设可以无证据地被标为 validated

Hypothesis registry 是可整体覆盖的 JSON 列表；普通 update 可以直接设置 `validated`，run card 不是必需项。

本项目的假设状态改为受控状态机；通过状态只能由冻结假设、独立留出证据、反证检查和明确裁决共同产生。

## 可借鉴但必须重写

- 严格 JSON 序列化、文件 SHA-256 和产物清单。
- run card 的“配置 + 策略 + 产物”结构；必须补足真实来源、fallback、查询、获取/观察/可见时间、原始 payload、universe、代码提交、依赖锁、人工决定和风险结果。
- 日内决策严格排除当日尚不可知收盘价的切片语义。
- 假设卡中的 thesis、universe、signal、source、invalidation 字段。
- unknown 默认拒绝、调用方自报名义金额不可信、风险停止标记等原则。

## 许可证边界

审查提交根许可证为 MIT；NOTICE 中另有 Qlib 特征定义的 Apache 2.0 归属。当前决定不复制其实质代码，只借鉴不可版权化的结构与原则并自行实现，因此不引入整包许可证和传递依赖风险。

## 验证摘要

选定测试运行结果：

```text
197 passed, 4 failed
```

四个失败源于测试即使指定临时输出仍试图写入用户目录，进一步证明其存储路径隔离不足。独立故障注入还确认：

```text
future_signal_static_check=ACCEPTED
audit_failure_result=None
validated_without_run_card={"run_cards":[],"status":"validated"}
```

