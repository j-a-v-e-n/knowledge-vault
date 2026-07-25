## Research result: 用 AI 可靠完成长期复杂软件项目

### Sources consulted

- [Anthropic：Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) — 分析上下文耗尽、过早收尾和自我验收偏乐观，并测试规划、生成、独立验收的分工。
- [OpenAI：Harness engineering](https://openai.com/index/harness-engineering/) — 复盘一个真实使用、持续部署的 AI 生成项目，重点涵盖测试、CI、可观测性、架构约束和技术债。
- [Google Cloud：2025 DORA Report](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report) — 基于近 5,000 名技术从业者的调查，分析 AI 对生产力、产品表现和交付稳定性的不同影响。

### Key findings

1. **先定义“产品完成”，再让 AI 写代码** — 明确目标用户、关键场景、验收条件、性能与运维要求。“生成了全部页面”不是完成；关键用户路径可用、可部署、可观察、可回归验证，才更接近非 demo 状态。（DORA、OpenAI）

2. **把项目切成可独立验收的纵向功能** — 不给 AI 一个“把整个系统做完”的长期指令；每轮只完成一个能从界面/API 一直验证到数据状态的功能，并在结束时保持项目可运行、可合并。（Anthropic）

3. **把项目状态移出聊天上下文** — 用版本化的简短记录保存已完成内容、当前状态、关键决定和明确下一步。新会话先读取这些状态、查看近期提交并运行基础测试，再开始新工作；不能依赖模型记住旧对话。（Anthropic、OpenAI）

4. **生成者不能兼任唯一验收者** — Anthropic 观察到模型会高估自己刚完成的成果。应让另一轮 AI 或另一位代理按明确标准检查，并实际操作 UI、调用 API、核对数据库状态；人负责最终产品判断。（Anthropic）

5. **让反馈变成 AI 可以直接读取的信号** — 建立稳定的启动和测试方式，并让 AI 能看到测试失败、构建结果、日志、指标和调用链。发现失败时，补足缺少的工具、环境信息或约束，而不是只重复提示“再仔细一点”。（OpenAI）

6. **关键工程要求要由工具自动检查** — 架构依赖方向、类型边界、格式、文件规模和可靠性要求应尽可能进入 CI、lint 或结构测试。仅写在长提示或文档里容易被忽略并随时间失效。（OpenAI）

7. **可直接采用的工作循环** — `恢复当前状态 → 跑基线测试 → 选择一个纵向功能 → 实现 → 独立端到端验收 → 跑完整检查 → 小提交 → 写明下一步`；同时定期修复重复代码、过时文档和架构漂移。（三份来源综合）

### Verbatim quotes（≤ 5 条）

> “decomposing the build into tractable chunks, and using structured artifacts to hand off context between sessions.”  
> （[Anthropic，开篇方法概述](https://www.anthropic.com/engineering/harness-design-long-running-apps)）

> “agents tend to respond by confidently praising the work”  
> （[Anthropic，Why naive implementations fall short](https://www.anthropic.com/engineering/harness-design-long-running-apps)）

> “testing, validation, review, feedback handling, and recovery”  
> （[OpenAI，Increasing levels of autonomy](https://openai.com/index/harness-engineering/)）

> “AI doesn't fix a team; it amplifies what's already there.”  
> （[DORA，报告核心发现](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)）

> “AI adoption does continue to have a negative relationship with software delivery stability.”  
> （[DORA，AI, the great amplifier](https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report)）

### ⚠️ 矛盾或不确定

- OpenAI 的专用高吞吐环境采用较少阻塞式合并检查，并明确表示在低吞吐环境照搬可能不负责任；DORA 则发现 AI 采用与交付稳定性仍呈负向关系，强调自动化测试、版本控制和快速反馈。两者的环境和适用边界不同。
- OpenAI 明确表示，目前仍不知道完全由 AI 生成的系统经过数年后能否保持架构一致性；现有案例支持持续数月的真实交付，尚不能证明多年可靠性。

### Suggested next step（lead 接续用）

先选择一个可部署的纵向功能，用上述循环连续完成数轮；只有每轮都能从旧状态恢复、通过端到端验收并保持既有功能不退化，再逐步扩大 AI 的自主范围。
