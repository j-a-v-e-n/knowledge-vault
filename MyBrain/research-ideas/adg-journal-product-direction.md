# ADG 进阶方向：期刊化 / 产品化（搁置中, 重要）

状态: 搁置（final week 优先收尾 175B project + HW3）。这是认真想追的长期目标。

## 核心动机

ADG 作为课程项目已满分。想进一步做成期刊论文或产品。

关键认知: 跟前人（DCFG 等）有重叠很正常, 立足点是"多走的那一步"——
即 interference 的系统刻画（DCFG 是 counterfactual + 修掉干扰, 我是
direct generation + 测量干扰, 侧重点不同）。

## 共同的下一步（论文/产品都从这里开始）

把 ADG 接到一个更强的预训练 backbone 上（FFHQ / Stable Diffusion 级别），
重跑 interference matrix。验证:

- interference 是普遍现象, 不是我的小 DDPM 的特例
- 更强/更平衡数据的模型, 纠缠是否减弱

注意: 深层真相 = 属性纠缠根植于真实世界数据的统计结构, 强模型能减轻
但无法完全消除。这本身是核心洞察。

工程坑: 强模型（如 SD）用文本 + cross-attention conditioning, 和我的
4 维 multi-hot 不同, ADG 接上去需要适配。

## 若走期刊（难度: 半年-1年）

要补:

1. 跨模型验证（换强 backbone, 证明普遍性）← 最关键
2. 和 DCFG/Composable 的正面实验对比（不只 related work 提一句）
3. interference 的更深机制分析: 把 data-induced vs model-induced 干扰
   分离开, 带统计/因果保证（identification problem, 硬骨头, 可能需补因果推断）
4. 更大规模 + 更多属性（K=4 → 更多）, 证明可扩展

投稿策略: 别一上来冲顶会, 先 workshop 或中等会议练手 + 拿反馈。

## 若走产品（要求和论文几乎相反）

产品不在乎首创, 在乎好用 + 解决真实痛点。

方向: 对话→自动调属性旋钮（用现成 LLM 当"人话→wₖ"翻译器, 不用自己训）+
接强 backbone。

关键挑战: 此领域产品已很卷（Midjourney 等）, 必须找一个它们做不好、
而 per-attribute 精细控制正好解决的细分场景（如严格属性可控的合成数据
生成、某垂直行业定制）, 要有人愿意买单的理由。

## 决策逻辑

共同下一步（换强 backbone 重跑）做完后:

- 结论成立 + 能讲深机制 → 往论文走
- 发现对某真实场景特别有用 → 往产品走

## 提醒

- 这是长跑, 别让它冲掉眼前的硬 deadline
- 真要做, 文献检索要彻底（双语 + 引用链 + 近期 arXiv）, 之前查证非穷尽
