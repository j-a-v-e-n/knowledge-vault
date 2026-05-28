# ADG 后续研究 Idea (暂存, 非 final report 内容)

来源: 2026-W22 与 AI 讨论 ADG 项目时衍生的两个方向。
两个都不在本学期 final report 范围内, 仅作未来研究备选。
已做初步文献查证 (各 2 轮 web search, 非穷尽, 真要做需更彻底检索)。

---

## Idea 1: 序贯 / 自回归属性引导 (Sequential / Autoregressive Attribute Guidance)

### 核心想法
现有 multi-attribute guidance (ADG, DCFG, Composable Diffusion) 都是**并行**
线性组合各属性方向: eps = eps_uncond + Σ wₖ·dₖ。
本 idea: 改成**序贯施加**——一个属性一个属性按顺序加, 后一个的方向在
"已施加前序属性"的条件下重新计算, 显式建模属性间的条件依赖。

形式 (一种可能):
  eps^(0) = eps_uncond
  eps^(k) = eps^(k-1) + wₖ·[eps(x, y^(k) | 已施加前k-1个) - eps^(k-1)]

### 动机
并行加权假设属性方向线性独立。若属性相关 (CelebA 里 male↔young),
并行会产生串扰 (interference)。序贯施加可能通过建模条件依赖减少串扰。

### 文献查证结论 (2026-W22)
- Composable Diffusion (Liu 2022) / LogDiff (2026): 并行/逻辑组合, 非序贯
- SEED (2025) 等 sequential editing: 是"序贯编辑已有图", 非"序贯 guidance 机制"
- Blending Concepts (2025): 观察到 prompt ordering 影响结果, 但当现象报告, 未系统化
- **缝隙**: "序贯 vs 并行 guidance 在属性相关时哪个 interference 更小" +
  "guidance 组合的非交换性 (non-commutativity)" 作为系统研究, 似乎没人做

### 潜力评估: 中等偏低
- 风险: 序贯引入顺序依赖 (A→B ≠ B→A), 这是 bug-like 性质 (用户得选顺序),
  可能是"别人有意绕开"而非"被忽略的金矿"。Composable 用并行正是为避免顺序问题。
- 天花板: 偏 workshop paper / 某 paper 的一个 section, 难撑独立强 paper
- 要做成需找到"让顺序依赖从 bug 变 feature"的具体场景, 目前没想到明显的

---

## Idea 2: 属性干扰的因果可识别分解 (Causal Identification of Model-Induced Attribute Interference)

### 核心想法
生成模型里"调一个属性, 另一个跟着变"的干扰, 区分两个来源:
- data-inherent: 数据里属性本来就相关 (CelebA male↔young 真实相关)
- model/sampling-induced: 模型/采样引入的、超出数据的额外纠缠
目标: 一个**有因果可识别性保证**的测量框架, 干净地分离这两者。

### 演化历史
最初版本是简单减法: Δ_spurious = Δ_gen - Δ_real (同一 classifier 在
生成图 vs 真实图上测属性相关性相减)。
**这个简单版有 identification problem**: 减出来的差混了模型纠缠 + 采样噪声 +
classifier domain shift + mode coverage 偏差, 无法干净分离。
所以升级目标是: 用因果推断方法 (SCM / do-calculus / 精心设计 intervention)
真正解决可识别性, 而非简单 correlation 减法。

### 文献查证结论 (2026-W22)
- Bias amplification (Zhao 2017 起, diffusion 上 Luccioni/Bianchi 2023):
  "模型放大数据相关性"这个核心观察**已被大量研究, 不新**
- DCFG (Xia 2025): motivation 就是 attribute amplification, 且用 causal graph
  分 intervened/invariant, 已沾边因果
- Spurious correlation (fairness/robustness): 有精确定义和大量方法
- **缝隙**: "可识别地分离 data-induced vs model-induced attribute correlation,
  带因果保证"的测量框架, 可能有缝 (简单减法不算, 要真因果方法)

### 潜力评估: 中等偏高 (但门槛高)
- 天花板比 Idea 1 高: 连接 fairness / causal inference, 做扎实能上好会议
- 门槛: 要真正解决 identification, 需因果推断硬功夫, 远超 course project
- 风险: 撞 bias amplification 大片文献 + DCFG; 要非常小心定位差异

---

## 共同提醒
- 两个查证都非穷尽 (各 2 轮搜索)。真要 commit 必须做彻底文献检索:
  双语 (中英) + Google Scholar 引用链 + 近半年 arXiv
- "我搜了没找到" ≠ "没人做过", 尤其 Idea 2 连接的 fairness/causal 领域很大
- 当前优先级: 0 (不做, 仅存档)。focus 在 ADG final report。
