# `.claude/agents/` — Javen 的 AI 团队

> 4 个 subagent + 1 个 lead(主对话 Claude)。你(Javen)是老板,只负责派活和验收。
>
> 设计原则见 [[wiki/工程方法/AI 团队设计原则.md]] + [[wiki/工程方法/AI 项目经理_subagent 模式.md]]。

## 团队组织架构

```
                      Javen (老板, Approver)
                            │
                  Main Claude (项目经理, Driver)
                            │
        ┌─────────────┬─────┴─────┬─────────────┐
        ▼             ▼           ▼             ▼
   researcher    engineer      writer       reviewer
   (Haiku)       (Sonnet)      (Sonnet)     (Sonnet)
   调研员         工程师        写手         审稿员
```

## 4 个员工的"岗位说明书"

| 员工 | 模型 | 工资 (in/out) | 干啥 | 不干啥 |
|---|---|---|---|---|
| **researcher** | Haiku 4.5 | $1/$5 per M tok | 读 PDF / 笔记 / 网页, 出摘要 + 引文 | 写代码、写报告、评判对错 |
| **engineer** | Sonnet 4.5 | $3/$15 per M tok | 写代码、改代码、跑实验脚本 | 调研、写报告、审稿 |
| **writer** | Sonnet 4.5 | $3/$15 per M tok | 写论文 / report / docstring / vault 笔记 | 写代码、调研 |
| **reviewer** | Sonnet 4.5 | $3/$15 per M tok | 审代码 / 审稿 / 找事实错 (只读) | 修复、写新内容 |

> Haiku 比 Sonnet 便宜 3×。**让 researcher 干便宜活,Sonnet 留给真专业活**——这就是模式 B 的成本逻辑。
> task-013 (router) 装好后,把 model 字段改成 `deepseek-chat` 就再降 10×。

## 怎么调员工

### 你(Javen)只跟主 Claude 说话

```
你: "推进 ECE284 项目"
主 Claude (lead) 内部决策:
  - 先了解状态? → 派 researcher 看 vault 已有 source 页
  - 写新代码? → 派 engineer
  - 写 update report? → 派 writer
  - 检查事实? → 派 reviewer
你看到的: 主 Claude 给你最终汇总, 不需要管谁干的
```

### 主 Claude 调 subagent 的方式

主 Claude 用 Task tool 派活,例如:

```
Task(
  subagent_type="researcher",
  description="ECE175B ADG 文献调研",
  prompt="读 raw/ucsd/Spring 2026/ECE175B/proposal.pdf, 出 200 字 lay summary + 5 条 key findings + 关键引文"
)
```

或并行调 3 个员工同时干不同活:

```
[同一条消息里]
Task(researcher, "调研 X")
Task(engineer, "写 Y")
Task(writer, "起草 Z")
```

## 派活的 4 条 ground rules

按 [[AI 团队设计原则]] 总结的:

### 1. 一个员工一次只干一件事

- ✅ "读 paper Y 出 200 字 summary"
- ❌ "读 paper Y 然后改成 NeurIPS 段落然后审一遍"  ← 这是 lead 的活, 拆 3 个任务派 3 个员工

### 2. 每个任务必带 4 件套

- **objective**(干啥)
- **input source**(输入是什么 path/url)
- **output format**(输出长什么样)
- **boundary**(不许做什么)

### 3. 只读 subagent 安全, 写操作单线程

- researcher / reviewer 是只读 → 多个并行没事
- engineer / writer 是写 → **不并行,**避免改同一文件冲突

### 4. 5 任务上限 / 单任务 30 分钟上限

每个 subagent 内置 iteration cap (researcher 5 / engineer 30 / writer 20 / reviewer 25 工具调用) + 超出强制 exit + 报告状态。**不会无限烧钱**。

## 用到的实际场景(ECE 175B / 284)

### 场景 1: ECE284 写 update report

```
Javen: "ECE284 的 update report 该写了, 5/20 截止"
Main Claude 拆解:
  1. 派 researcher 读 proposal_javen_revised.pdf + projects/ece284-llm-ppg/results/*.json
     → 输出当前进度摘要
  2. 派 writer 基于 researcher 输出 + ACM Large 2-column 模板, 写 §1-§4
  3. 派 reviewer 审 writer 输出 — 对比 proposal 找事实漂移
  4. 主 Claude 整合 + 给 Javen 看
Javen: 审一遍 → 改一两处 → 提交
```

### 场景 2: ECE175B 加新 sample 模式

```
Javen: "我想看 ADG 在 attribute negation (w_k < 0) 时的效果"
Main Claude:
  1. 派 engineer 在 sample.py 加 `--negate <attr>` 模式 + smoke test
  2. 派 reviewer 审 engineer 改的代码 — 验证数学跟 adg.py 一致
  3. 主 Claude 报告: "可以跑了 — colab notebook cell 改成 X"
Javen: 拷贝命令, Colab 跑
```

### 场景 3: 看板任务推进 (daemon 凌晨)

```
Daemon 03:00 启动:
  - 看 task-board.md 找 owner=@claude 任务
  - 比如 task-018 子任务 c (TROIKA-lite sanity check) 没标 [x]
  - 派 engineer 跑 troika_lite.py + 把结果写进 results/troika.json
  - 派 writer 把结果摘成一句话 update 看板任务卡
  - daemon 总报告里说: "推进了 task-018 c"
```

## 何时**不**用 subagent 模式

参考 [[AI 团队设计原则]] 决策树。**默认 single-agent**, 以下场景才升级到 subagent:

- ✅ 任务能干净拆成 ≥ 3 个独立子步骤
- ✅ 子步骤需要不同 expertise (调研 vs 编码 vs 写作)
- ✅ 单任务 ≥ 30 分钟工作量

不要用 subagent 的:
- ❌ 简单查询 ("vault 里 X 在哪?")
- ❌ 单文件单点修改 ("把 README.md 第 3 行改 typo")
- ❌ 需要紧密 context 共享的 (refactor 跨 5 文件的复杂逻辑)

## 安全 / 边界

- 4 个 subagent 都不能改 `raw/` 和 `archive/` (vault 主规则)
- engineer / writer 写文件前先 Read 整文件 (避免覆盖)
- 没有员工能 git push / git reset / pip install / brew install — 这些是 Javen 的事
- API key / secrets 永远不进 git tracked 文件

## 监控 / 调试

每次 subagent 调用结束, 主 Claude 在最终回复里说明:
- 派给了谁
- 工具调用次数
- 大致 token 消耗
- 子任务是否成功

如果发现某员工反复跑偏 → Javen 可以告诉 lead "暂时不要派给 X" 或者改它的 markdown 调 prompt。

## 跟 task-board 集成

`task-019` 在看板上跟踪 subagent 系统的部署 + 调优:
- a-d 子任务: 4 个 subagent markdown 写完
- e: 这份 README.md
- f: wiki 设计文档
- g: smoke test
- h: (后续) router 装好后路由到 DeepSeek
- i: (1 周后) 总结哪些 subagent 工作好 / 哪些回退 single-agent

## 跟 task-013 router 的关系

**模式 B (subagent) 不强依赖模式 A (router)**:
- 现在用 Anthropic 内档 (Haiku 已经比 Sonnet 便宜 3×)
- 等 router 装好, **改 4 个 markdown 的 `model:` 字段一行就完成**

```yaml
# 现在
model: claude-haiku-4-5
# 装 router 后改成
model: deepseek-chat
```
