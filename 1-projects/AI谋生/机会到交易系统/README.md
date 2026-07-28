# 机会到交易系统

> 当前状态：本文件描述的是研究闭合前的旧原型，不是当前总体设计。请先读 [LEGACY_STATUS.md](./LEGACY_STATUS.md)；差距审计已判定旧 CLI 与餐馆 Pilot 只能作为历史样本和 `LEGACY_UNQUALIFIED` fixture，禁止据此推进外部动作或作为新实现入口。

这是一套从零建立的、由 AI 主导的“机会到交易”系统。它不继承旧创新闭环的候选、评分、闸门或结论。

系统的唯一最终目标是：识别他人的真实价值缺口，提供有效解决方案，并以真实交易完成验证。

## 当前边界

- 当前版本只在本地创建、校验和组织证据与项目 Harness。
- 默认不发送消息、不发布内容、不签约、不收付款、不替用户作出外部承诺。
- 网络帖子、AI 推断、Demo、回复、付款和满意度是不同证据层，不得互相替代。
- “完全由 AI 运行”是需要逐步验证的目标，不是预设事实。

## 系统结构

```text
第一性原理通道 ─────┐
                    ├─→ 机会假设 → 最小价值预览 → 外部行为 → 生产 Harness → 交付与交易
现实观察通道 ───────┘
```

两个输入通道必须分别形成记录；只有 `opportunity` 记录可以把它们汇合。系统状态只由外部事件推导，AI 不能直接把机会标成“已验证”。

## 文件说明

- `DESIGN.md`：目标、定义、证据层级、状态机和 AI/人的边界。
- `STATE.md`：当前真实状态和下一步。
- `docs/黄仁勋访谈-原始内容与本项目推论.md`：原访谈事实、合理推论和不受访谈支持的说法。
- `src/opportunity_os.py`：本地 CLI 和确定性校验器。
- `tests/test_opportunity_os.py`：防止证据升级和越权生成交付 Harness 的测试。

## 本地运行

```bash
python3 src/opportunity_os.py init /tmp/opportunity-workspace
python3 src/opportunity_os.py validate /tmp/opportunity-workspace
python3 src/opportunity_os.py status /tmp/opportunity-workspace
python3 -m unittest discover -s tests -v
```

加入记录：

```bash
python3 src/opportunity_os.py add /tmp/opportunity-workspace /path/to/record.json
```

为验证实验生成 Harness：

```bash
python3 src/opportunity_os.py make-harness /tmp/opportunity-workspace \
  --opportunity opportunity-id \
  --probe probe-id \
  --mode probe
```

交付 Harness 默认只有在外部记录达到承诺阶段后才能生成；这避免 AI 在尚无真实需求证据时把 Demo 偷换成正式产品。
