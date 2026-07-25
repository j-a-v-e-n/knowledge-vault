## Research result: RESEARCH-REFRESH-R7 / RS-02

**裁决：`bounded_incomplete`。** 已按 commit `3a1bbe4565006745fb3c458066e08a4640c31268` 执行全部预注册查询预算；没有写文件或修改工作树。

### Sources consulted

- [R7 预注册](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:20>) — RS-02 问题、查询预算、纳排规则、停止条件。
- [上游失效分类](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/AI_PROJECT_FAILURE_TAXONOMY_2026-07-25.md:59>) — GOV/CTX/ORG/VER 基线与待关闭缺口。
- [上游 AI 工程刷新](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/AI_ENGINEERING_METHOD_REFRESH_2026-07-24.md:55>) — 多代理、图运行时和采用基线。
- [Anthropic long-running harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — 官方内部长周期应用实验。
- [LLM Evaluators Recognize and Favor Their Own Generations](https://arxiv.org/abs/2404.13076) — 自评、自识别、自偏好与顺序偏差。
- [Lost in the Middle, TACL](https://aclanthology.org/2024.tacl-1.9/) — 长上下文位置敏感性。
- [From Spark to Fire v2](https://arxiv.org/abs/2603.04474) — 多代理错误级联、拓扑敏感与治理插件。
- [LangGraph repository](https://github.com/langchain-ai/langgraph) 及其代码、issues — durable execution 的实现语义和实战故障。
- [More Agents Is All You Need v2](https://arxiv.org/abs/2402.05120) — 对“多代理必然更差”的反证。

预注册修订身份：

- prereg Git blob：`ad50be505931939a76b45821a45ef9ee3e26ef10`
- prereg SHA-256：`db7e630355719e62c4c9ccd5e50d038539327ef8de952a3bf47c9e4894f30d35`
- failure-taxonomy blob：`cc42e014c6e580bdbfc03e17340a9c3fdac69972`
- engineering-refresh blob：`8ac625588fe4dffece71540cba9d136af1dc9312`

### Exact query log

UTC 是每批搜索调用前立即取得的时间。搜索界面按批次扁平返回结果，没有暴露单条结果对应哪个查询。

| ID | Exact query | UTC |
|---|---|---|
| RS-02-Q01 | `site:anthropic.com/engineering "effective harnesses for long-running agents" compaction` | `2026-07-25T15:43:08Z` |
| RS-02-Q02 | `site:arxiv.org OR site:aclanthology.org "LLM evaluators recognize and favor their own generations"` | `2026-07-25T15:43:08Z` |
| RS-02-Q03 | `site:aclanthology.org OR site:arxiv.org long context "lost in the middle" memory agents` | `2026-07-25T15:43:08Z` |
| RS-02-Q04 | `site:arxiv.org "From Spark to Fire" "multi-agent"` | `2026-07-25T15:43:08Z` |
| RS-02-Q05 | `site:arxiv.org ("memory poisoning" OR "memory contamination") "LLM agents"` | `2026-07-25T15:43:56Z` |
| RS-02-Q06 | `site:news.ycombinator.com OR site:reddit.com long-running coding agent loop harness context compaction maintenance` | `2026-07-25T15:43:56Z` |
| RS-02-Q07 | `site:github.com/langchain-ai/langgraph checkpoint persistence durable execution recursion_limit` | `2026-07-25T15:43:56Z` |
| RS-02-Q08 | `site:arxiv.org "More Agents Is All You Need"` | `2026-07-25T15:43:56Z` |

Q05、Q06 没有可归属的可见结果；这是 no-visible-result receipt，不代表搜索引擎中不存在相关资料。普通用户经验最终由 Q07 返回的 GitHub issues 覆盖。

### Complete visible result set

筛选码：`IN-D` 决定性证据；`IN-C` 背景/反证；`IN-U` 用户经验，只证明路径存在；`EX-DUP` 同源重复；`EX-NAV` 导航页；`EX-CITE` 仅引用目标；`EX-SCOPE` 不改变本题边界；`EX-FP` 搜索误命中。

#### Batch A：Q01–Q04，按返回顺序

| Result | Screening reason | Source class · upstream cluster · revision |
|---|---|---|
| [From Spark to Fire](https://arxiv.org/abs/2603.04474) | `IN-D`：直接测试错误级联、拓扑与防御 | preprint · `UC-MAS-XIE` · v2 `2026-05-11` |
| [LLM Evaluators Recognize and Favor Their Own Generations](https://arxiv.org/abs/2404.13076) | `IN-D`：直接测试自评偏差 | research · `UC-JUDGE-PANICKSSERY` · v1 `2024-04-15` |
| [Lost in the Middle: Emergent Property](https://arxiv.org/abs/2510.10276) | `IN-C`：提供训练需求导致位置偏差的替代解释 | preprint · `UC-LCTX-SALVATORE` · submitted `2025-10-11` |
| [Lost in the Middle, arXiv](https://arxiv.org/abs/2307.03172) | `EX-DUP`：同一研究已有 TACL 正式版 | preprint · `UC-LCTX-LIU` · superseded for use by TACL |
| [Lost in the Middle, TACL](https://aclanthology.org/2024.tacl-1.9/) | `IN-D`：长上下文位置效应的正式版本 | peer-reviewed · `UC-LCTX-LIU` · TACL `2024` |
| [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents?trk=article-ssr-frontend-pulse_little-text-block) | `IN-D`：官方内部长项目故障与 harness | official primary · `UC-HARNESS-ANTHROPIC` · published `2025-11-26` |
| [Never Lost in the Middle](https://aclanthology.org/2024.acl-long.736/) | `IN-C`：位置无关训练可显著缓解问题 | peer-reviewed counterevidence · `UC-LCTX-PAM` · ACL `2024` |
| [Tree of Agents](https://aclanthology.org/2025.findings-emnlp.246/) | `IN-C`：多代理分块可缓解长上下文问题 | peer-reviewed counterevidence · `UC-LCTX-TOA` · Findings EMNLP `2025` |
| [Found in the Middle](https://aclanthology.org/2024.findings-acl.890/) | `IN-C`：注意力校准缓解位置偏差 | peer-reviewed counterevidence · `UC-LCTX-HSIEH` · Findings ACL `2024` |
| [Lost in Decomposition](https://aclanthology.org/2026.findings-acl.2097/) | `IN-C`：RAG/分解式长上下文方法并非普遍有效 | peer-reviewed limitation · `UC-LCTX-GUO` · Findings ACL `2026` |
| [Anthropic Engineering index](https://www.anthropic.com/engineering?cam=claude) | `EX-NAV`：只导航到已纳入文章 | official index · `UC-HARNESS-ANTHROPIC` · mutable |
| [Gated Differentiable Working Memory](https://aclanthology.org/2026.acl-long.1471/) | `EX-SCOPE`：模型参数工作记忆，不是代理持久记忆污染 | peer-reviewed · `UC-LCTX-GDWM` · ACL `2026` |
| [Song Yu author page](https://aclanthology.org/people/song-yu/) | `EX-NAV`：重复 Tree of Agents | author index · `UC-LCTX-TOA` · mutable |
| [Anthropic Engineering subject filter](https://www.anthropic.com/engineering?subjects=claude) | `EX-NAV`：重复导航 | official index · `UC-HARNESS-ANTHROPIC` · mutable |
| [Anthropic Engineering team filter](https://www.anthropic.com/engineering?team=4002065008) | `EX-NAV`：重复导航 | official index · `UC-HARNESS-ANTHROPIC` · mutable |
| [Mitigating Position Bias](https://aclanthology.org/2026.findings-acl.1059/) | `EX-SCOPE`：没有新增 RS-02 架构决定 | peer-reviewed · `UC-LCTX-LSPE` · Findings ACL `2026` |
| [Never Lost PDF](https://aclanthology.org/2024.acl-long.736.pdf) | `EX-DUP`：HTML 同源重复 | peer-reviewed · `UC-LCTX-PAM` · ACL `2024` |
| [Lost in the Middle PDF](https://aclanthology.org/2024.tacl-1.9.pdf) | `EX-DUP`：HTML 同源重复 | peer-reviewed · `UC-LCTX-LIU` · TACL `2024` |
| [Graders Should Cheat](https://aclanthology.org/2025.emnlp-main.838.pdf) | `EX-CITE`：只因引用目标论文命中 | peer-reviewed · separate upstream · EMNLP `2025` |
| [Frame In, Frame Out](https://aclanthology.org/2026.starsem-conference.25.pdf) | `EX-CITE`：只因参考文献命中 | peer-reviewed · separate upstream · `2026` |
| [From Calculation to Adjudication](https://aclanthology.org/2025.gem-1.65.pdf) | `EX-CITE`：只因参考文献命中 | peer-reviewed · separate upstream · `2025` |
| [Who Wrote This Line?](https://aclanthology.org/2026.acl-long.245.pdf) | `EX-CITE`：只因参考文献命中 | peer-reviewed · separate upstream · ACL `2026` |

#### Batch B：Q05–Q08，按返回顺序

| Result | Screening reason | Source class · upstream cluster · revision |
|---|---|---|
| [More Agents Is All You Need](https://arxiv.org/abs/2402.05120) | `IN-D`：预注册反证；显示简单采样投票可受益 | peer-reviewed/TMLR · `UC-MOREAGENTS-LI` · v2 `2024-10-11` |
| [LangGraph repository](https://github.com/langchain-ai/langgraph) | `IN-D`：durability、memory、HITL 的真实开源实现 | open source · `UC-LANGGRAPH-CORE` · latest visible release `1.2.9`, `2026-07-10`; main mutable |
| [LangGraph types.py](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/types.py) | `IN-D`：同步、异步、退出时持久化及 checkpoint 类型 | open-source code · `UC-LANGGRAPH-CORE` · mutable `main` |
| [LangGraph issue #148](https://github.com/langchain-ai/langgraph/issues/148) | `IN-U`：用户实际遇到无停止条件递归 | user experience · `UC-LG-ISSUE-148` · closed; opened `2024-02-25` |
| [LangGraph issue #6792](https://github.com/langchain-ai/langgraph/issues/6792) | `IN-U`：interrupt/resume 时子图重复执行 | user experience · `UC-LG-ISSUE-6792` · fix relation mentioned; final resolution not verified |
| [LangGraph tool_node.py](https://github.com/langchain-ai/langgraph/blob/main/libs/prebuilt/langgraph/prebuilt/tool_node.py) | `EX-SCOPE`：主要是工具重试示例，未新增 checkpoint 决定 | open-source code · `UC-LANGGRAPH-CORE` · mutable `main` |
| [LangGraph issue #4937](https://github.com/langchain-ai/langgraph/issues/4937) | `IN-U`：Postgres checkpoint 文档/config 负担 | user experience · `UC-LG-ISSUE-4937` · closed by `#4953` |
| [LangGraph discussion #1097](https://github.com/langchain-ai/langgraph/discussions/1097) | `IN-U`：真实 endless-loop 报告 | user experience · `UC-LG-DISC-1097` · Closed Unanswered |
| [LangGraph issue #6053](https://github.com/langchain-ai/langgraph/issues/6053) | `IN-U`：HITL 依赖正确注入 checkpointer | user experience · `UC-LG-ISSUE-6053` · bug/pending visible; current state unverified |
| [LangGraph issue #741](https://github.com/langchain-ai/langgraph/issues/741) | `IN-U`：早期持久化配置与自定义 saver 负担 | user experience · `UC-LG-ISSUE-741` · closed; historical/superseded in part |
| [LangMem repository](https://github.com/langchain-ai/langmem) | `EX-SCOPE`：可见结果过稀，不能支持 contamination claim | open source · `UC-LANGMEM` · mutable |
| [LangChain repositories](https://github.com/orgs/langchain-ai/repositories) | `EX-NAV`：组织导航页 | index · `UC-LANGGRAPH-CORE` · mutable |
| [LangChainJS issue #10096](https://github.com/langchain-ai/langchainjs/issues/10096) | `IN-U`：跨运行环境自动 checkpoint 注入差异 | user experience · `UC-LCJS-ISSUE-10096` · current resolution not visible |
| [Preble](https://arxiv.org/pdf/2407.00023) | `EX-CITE`：仅引用 More Agents | research · separate upstream · `2024` |
| [GitHub Agentic Workflows slides](https://github.github.com/gh-aw/slides/20260224-github-agentic-workflows.pdf) | `EX-SCOPE`：未直接支持本题机制或结果 | official slides · separate upstream · `2026-02-24` |
| [GitHub secure-development ebook](https://resources.github.com/downloads/%E3%82%BB%E3%82%AD%E3%83%A5%E3%82%A2%E3%81%AASW%E9%96%8B%E7%99%BA%E3%81%AE%E3%81%9F%E3%82%81%E3%81%AEEbook.pdf) | `EX-FP`：与查询主题无关 | false positive |
| [Generating Stack Machine Code using LLVM](https://github.com/etclabscore/evm_llvm/wiki/files/Generating_stack_machine_code_using_LLVM.pdf) | `EX-FP`：与查询主题无关 | false positive |
| [Dissect vs SysInternals](https://github.com/reuteras/dfirws/wiki/resources/Dissect.vs.SysInternals.Case.Part.1_.Planning.and.Testing.Pending.Investigations.pdf) | `EX-FP`：与查询主题无关 | false positive |
| [Git cheat sheet](https://resources.github.com/downloads/github-git-cheat-sheet.pdf) | `EX-FP`：与查询主题无关 | false positive |

### Key findings

下列 `excerpt-sha256` 是精确 UTF-8 支持摘录、无尾换行的 SHA-256；不是整页内容哈希。所有 entailment 均为本轮研究者判断，尚无独立 reviewer，因此不能满足预注册的 author-only 禁止条件。

1. **RS-02-C01｜LLM 自评在被测设置中存在 self-preference 与 ordering bias。**  
   支持范围：[论文 HTML 摘要与结果 L3–5、L82、L86、L93](https://arxiv.org/abs/2404.13076)；v1。论文报告 GPT-4、GPT-3.5、Llama 的顺序反转率分别为 `25%`、`58%`、`89%`。  
   `excerpt-sha256=8595fa0ca974711eb187e330258b1dab5da4c6105120f4984fa4b79139768f71`  
   `entailment=entailed`，仅限论文的摘要评价任务与模型。  
   **限制：**不支持完整软件项目中的发生率，也没有证明盲评、换序或跨模型 judge 能消除偏差；论文明确说相关性不能单独证明因果。  
   **Decision effect：**作者模型或同家族 LLM judge 只能产生 candidate signal；高影响完成权继续要求冻结 oracle、换序/隐藏身份的变形检查和独立机制。

2. **RS-02-C02｜长上下文容量不保证均匀利用；被测任务对相关信息位置敏感。**  
   支持范围：[TACL 摘要](https://aclanthology.org/2024.tacl-1.9/)；多文档问答和 key-value retrieval。  
   `excerpt-sha256=be87be20a6cc7dd909361f2518ed46cd6eba976376182e49b7f5326dac0efa97`  
   `entailment=entailed`，限指定任务。  
   **限制：**不能直接量化项目 compaction、文件检索或跨会话遗忘率；其他论文显示专门训练、注意力校准或分块代理可以缓解问题。  
   **Decision effect：**CTX-01 不能只验证“上下文放得下”，必须做需求位于开头/中间/末尾、压缩前后和空上下文恢复的同题探针。

3. **RS-02-C03｜Anthropic 的长周期 web-app 实验中，compaction 单独不足；外部化状态、小步工作与端到端测试改善了交接。**  
   支持范围：[L19–35、L56–70、L73–107](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)。观察到一次做太多、半实现交接、下一会话猜测历史、过早宣布完成；其 harness 使用 feature list、progress file、Git、单 feature 推进和浏览器测试。  
   `excerpt-sha256=3a7871402cc790fbdde6254eb130e2b7971b081231a210d0040a5b39c1f7a339`  
   `entailment=entailed`，限 Anthropic 的内部 full-stack demo。  
   **限制：**厂商自报实验；未提供与无 harness 的完整统计对照；文章自己说多代理是否更优和跨领域泛化仍未知。其“self-verify”也不能自动满足独立完成门。  
   **Decision effect：**维持版本化外部事实源；新增 compaction/restart 故障注入，不把 progress note 本身当正确性证明。

4. **RS-02-C04｜一个原子错误可在被测多代理图中级联，角色名或 reviewer 节点本身不能保证阻断。**  
   支持范围：[v2 L138–156、L188–203、L246–296、L492–503](https://arxiv.org/abs/2603.04474)。六个框架中有五个达到 `100%` final infection；LangGraph hub 注入为 `100%`、leaf 为 `9.7%`。v2 摘要报告治理层至少在 `89%` runs 阻止 final infection。  
   `excerpt-sha256=37e6869bef546c79fab67716e0523459049389b498344cc6dc6e6d5263a9ec34`  
   `entailment=entailed`，限固定拓扑、原子 seed、确定性 infection harness 和论文攻击设置。  
   **限制：**不等于自然发生率；验证层使用自建知识库和 GPT-4o-mini；生产项目复现与维护成本未知。  
   **Decision effect：**ORG-02 应验证信息依赖而非代理数量：原子 claim、lineage、中心节点风险、隔离验证预算、quarantine/rollback、确定性感染 oracle。

5. **RS-02-C05｜多实例并非普遍有害：简单 sampling-and-voting 在指定基准提高表现。**  
   支持范围：[v2 L145–170、L197–229](https://arxiv.org/abs/2402.05120)；论文已发表于 TMLR。  
   `excerpt-sha256=ca7ad0aa87de096045f2319f004c96b8cd9a1fee0e863dbbc98310c513177d18`  
   `entailment=entailed`，限 GSM8K、MATH、Chess、MMLU、HumanEval 及论文模型版本。  
   **限制：**token 随实例数成比例增加；部分 debate 组合因代理输出噪声导致失败；客观投票题不等于开放式项目完成审查。  
   **Decision effect：**撤销任何“多代理一律降低可靠性”的全称解释；允许在有客观 oracle 时试验隔离采样投票，但不把它等同于独立保障或采用 graph runtime。

6. **RS-02-C06｜LangGraph 暴露真实 durability/checkpoint 原语，但持久化、interrupt、replay 与终止仍需应用层机制验证。**  
   支持范围：[README](https://github.com/langchain-ai/langgraph)、[`types.py`](https://github.com/langchain-ai/langgraph/blob/main/libs/langgraph/langgraph/types.py)、[issue #148](https://github.com/langchain-ai/langgraph/issues/148)、[issue #6792](https://github.com/langchain-ai/langgraph/issues/6792)、[issue #4937](https://github.com/langchain-ai/langgraph/issues/4937)、[issue #6053](https://github.com/langchain-ai/langgraph/issues/6053)。代码区分 `sync`、`async`、`exit` durability；issues 暴露无停止条件、嵌套 checkpoint namespace 导致重放、Postgres 配置和 HITL checkpointer 依赖。  
   `excerpt-sha256=11159d55c5fd8e173c02eb7e7c59baba9bd36d0e86e1b33a17594aab03b132fa`  
   `issue-excerpt-sha256=59f4f61386be7d1af0f25ac2b2633d7490415d78ee93d1a70d95d2386314704d`  
   `loop-excerpt-sha256=ebab4f8e6773b21a163bc4e1a002cf2795860e82906c48a8c7e66e373d766900`  
   `entailment=partial`：能力和故障路径存在，但“维护负担很高”没有效果量。  
   **限制：**README 是项目自述；`main` 可变；issue 只证明存在性，不能估计普遍性，部分历史问题已关闭或被后续版本部分取代。  
   **Decision effect：**若试验 graph，必须 pin revision，并执行 crash/restart、interrupt/resume、重复副作用、checkpoint namespace、停止条件和升级重放测试；不能把 durable-execution 标签当 oracle。

7. **RS-02-C07｜长期 memory contamination 的发生方式与控制效果没有被本轮证据关闭。**  
   Q05 没有返回可见结果；LangMem/LangGraph 结果只证明持久记忆能力，不证明污染、陈旧、冲突或 supersession 的控制效果。  
   `entailment=not_entailed`；没有可合法生成的内容哈希。  
   **Decision effect：**上游“长期记忆写入污染、过期和冲突解决机制”保持 open major；不得宣称长期记忆机制已验证。

### Mechanized verification map

这是由纳入证据和冻结项目威胁模型推导的候选验证设计，不是已经执行过的效果证据。

| Failure class | Mechanized probe | Oracle / pass meaning | Current evidence state |
|---|---|---|---|
| GOV-03 / VER-02 自我袒护、LLM-as-judge | 冻结候选与 judge；隐藏作者身份；交换 A/B 顺序；与确定性 oracle 或独立人工标签比较；保存全部分歧 | 顺序变化不能改变裁决；作者 judge 无单独批准权；分歧保持可见 | 偏差存在有证据；控制效果未在本项目验证 |
| CTX-01 / CTX-02 长上下文与 compaction | 同一要求分别放在开头、中间、末尾；跨 compaction/restart 重放；从空上下文只读取冻结事实源 | 需求、授权和 next action 无遗漏；不得恢复旧请求；端到端 smoke 仍通过 | 位置风险与 vendor harness 有证据；项目效果未知 |
| CTX-03 memory contamination | 注入陈旧、相互冲突、被 supersede、来源不可信的 memory；跨重启检索 | 失效记忆不得进入有效决策上下文；来源、版本、as-of、supersession 可追踪 | `open major`，本轮无外部效果证据 |
| ORG-02 错误级联/假共识 | 在 leaf、hub、reviewer 上游分别注入一个原子错误；记录每跳采用、修正和 final infection | 未验证 claim 不进入最终产物；传播路径可回放；quarantine/rollback 生效 | 论文直接测试相邻机制；需项目复现 |
| ORG-04 / IMP-05 / IMP-06 loop、replay、副作用 | 每个状态转换前后 crash；interrupt/resume；重复调用；无终止条件；升级后重放 | 不重复外部副作用；checkpoint 与任务身份一致；达到冻结终态或明确 fail/blocked | 开源代码与用户 issue 支持风险存在 |
| ORG-05 graph/harness 负担 | 同题比较简单顺序 loop、隔离采样投票、graph；记录正确性、token、latency、故障恢复和升级维护 | 只有 graph 的新增控制价值超过其可观察维护负担才采用 | 尚无本地同题 comparison |

### ⚠️ 矛盾或反证

- [Anthropic harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 建议 agent 自行端到端验证；[自偏好论文](https://arxiv.org/abs/2404.13076) 显示同一模型兼任 evaluator 会产生自偏好与顺序偏差。两者并不互相否定，但支持“self-test 可发现 bug，不能单独授予完成权”。

- [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/) 显示位置敏感；[Never Lost](https://aclanthology.org/2024.acl-long.736/)、[Found in the Middle](https://aclanthology.org/2024.findings-acl.890/) 和 [Tree of Agents](https://aclanthology.org/2025.findings-emnlp.246/) 显示训练、校准或分块协作可以缓解。因此不能把长上下文失败写成所有模型、位置和方法的必然结果。

- [From Spark to Fire](https://arxiv.org/abs/2603.04474) 显示协作图可放大错误；[More Agents Is All You Need](https://arxiv.org/abs/2402.05120) 显示独立采样投票可提高指定基准表现。差异在交互方式、共享错误、投票 oracle 和任务结构；“代理多寡”不是足够的架构判据。

- [LangGraph README](https://github.com/langchain-ai/langgraph) 声明 durable execution；[issue #6792](https://github.com/langchain-ai/langgraph/issues/6792) 等显示 replay/checkpoint 配置仍可导致重复执行。能力存在不蕴含应用的 exactly-once、审计或恢复正确性。

### Architecture / decision deltas

相对 commit `3a1bbe…` 的上游基线：

- **AD-RS02-01｜新增 judge metamorphic gate。** GOV-03/VER-02 从“独立 reviewer”细化为身份隐藏、顺序交换、固定 judge revision、确定性/人工参照和分歧留存；同家族模型不得重复计为独立支持。

- **AD-RS02-02｜CTX-01 增加位置与压缩故障矩阵。** 版本化状态、Git 和 progress notes 仍保留，但必须通过开头/中间/末尾、compaction、空上下文 restart 和旧请求回归探针。

- **AD-RS02-03｜ORG-02 从角色隔离细化为 claim-flow 隔离。** reviewer/QA 名称不算防线；新增原子 claim lineage、高中心性节点优先验证、quarantine/rollback 和 deterministic infection oracle。

- **AD-RS02-04｜harness/loop 增加持久化语义验收。** graph 或 loop 的验收必须包括 termination、checkpoint namespace、interrupt/resume、crash/replay、幂等副作用及 upgrade replay。

- **AD-RS02-05｜保留“不先引入 graph runtime”，但加入窄例外。** 对有客观 oracle 的任务，可试验简单隔离采样投票；不把该收益外推到开放式软件审查或证据独立性。

- **AD-RS02-06｜长期记忆仍不得升级为已验证组件。** memory contamination/staleness/supersession 没有合格证据，本轮没有改变 CTX-03 的开放状态。

### Verbatim quotes

> “However, compaction isn’t sufficient.” ([Anthropic，L25](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))

> “One such bias is self-preference” ([Panickssery et al.，abstract](https://arxiv.org/abs/2404.13076))

> “performance is often highest when relevant information occurs at the beginning or end of the input context” ([Liu et al.，abstract](https://aclanthology.org/2024.tacl-1.9/))

> “five reach 100% final infection, including settings with explicit reviewer or QA roles” ([Xie et al.，L148](https://arxiv.org/abs/2603.04474))

> “the token usage increases proportionally with the number of agents” ([Li et al.，L158](https://arxiv.org/abs/2402.05120))

### Stability and gaps

- 必需来源类别均有覆盖：官方 primary、论文/预印本、开源实现、普通用户 issue。Q06 没取得 Reddit/HN 直接结果，因此普通经验覆盖只来自 GitHub 用户报告。
- Q08 是明确反证查询，并改变了 decision：允许客观 oracle 下的简单采样投票。
- 因最后一个 decision delta 出现在最后查询，之后没有“无新增高影响类别”的补充轮；稳定性停止条件不满足。
- 所有 entailment 都是本轮作者判断，尚无独立 reviewer；预注册明确禁止 author-only closure。
- 只有支持摘录哈希，没有整页不可变内容归档或完整 source revision graph。
- memory contamination 专查无可见结果。
- LLM-as-judge 在完整项目中的发生率、控制效果量和可靠性收益没有关闭。
- 多代理错误级联研究是攻击实验，不能外推自然发生率。
- Graph 维护负担只有 issue 存在性证据，没有同题时间、成本或故障率比较。
- 尚未执行本地同题 single-agent / sampling-vote / graph 比较，也未运行上述 fault injection。
- 因查询预算已耗尽，不追加第九个查询制造通过。

### Suggested next step（lead 接续用）

将 RS-02 登记为 `bounded_incomplete`，先由隔离 reviewer 复核上述 claim entailment；下一次重新预注册时专门补 memory contamination 与普通 practitioner 证据，再用本地 fault-injection 收敛 architecture delta。
