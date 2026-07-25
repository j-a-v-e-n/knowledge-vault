# R8 RS-01 原始研究报告

> 状态：`bounded_incomplete`
>
> 主题：怎样把开放动态网络研究约束成可复演、可停止且不夸大覆盖的决定充分性流程？
>
> 作者边界：本报告作者只负责检索、筛选、快照、原子 claim 草拟和作者侧 entailment。作者不充当独立 entailment reviewer；独立逐 claim 复核留给与作者分离的 reviewer。

## 1. 范围与不可越界边界

- 唯一计数查询：`R8-RS01-D1`、`R8-RS01-D2`、`R8-RS01-S1`、`R8-RS01-S2`、`R8-RS01-S3`。
- 每个 query 单独执行一次；不批量、不改写、不追加第六个查询。
- 开放动态网络不允许产生“领域穷尽”结论。允许的最强结论仅是：在冻结问题、来源类别、查询、时间、预算、残余风险和重开触发器内，当前 Paper V1 决定充分或不足。
- practitioner/community 资料只支持 failure hypothesis、用户负担、实现反例或 reopen trigger；不支持机制发生率或普遍能力。
- 本文件当前只冻结 D1/D2 后的 discovery 状态；S1-S3 尚未执行。

## 2. 时间边界证明

| 检查项 | 观察值 | 裁决 |
|---|---|---|
| preregistration commit | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | 与用户指定值一致 |
| commit UTC | `2026-07-25T16:13:44Z`（Git 显示 `2026-07-25T09:13:44-07:00`） | 一致 |
| commit parent | `18ba3164714012e54c1b08e90d77fa4c3f366976` | 已记录 |
| 当前文件 SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | 与用户指定值一致 |
| commit 内文件 SHA-256 | `613f2feb98707e6bcba5835632e2eba657ab98f81825a7678213de7ceddf92a8` | 与当前字节一致 |
| 执行检索前 `HEAD` | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | 等于 preregistration commit |
| `origin/codex/investment-assurance-r7` | `7824a63afe923d5e38c0c6f06577a7d1adfb81d5` | 远端已含精确预注册字节 |
| `git merge-base --is-ancestor prereg HEAD` | exit `0` | 通过；当前尚无本主题后续 evidence commit |

检索工具不暴露独立的后端完成时间。下文 `retrieved_at_utc` 使用每次搜索调用紧前记录的 UTC，作为保守的调用开始边界；它们均晚于 preregistration commit UTC。

## 3. Query execution ledger

| query_id | exact query | retrieved_at_utc | 单独搜索调用 | 可见结果集状态 |
|---|---|---|---|---|
| `R8-RS01-D1` | `systematic review search stopping decision focused saturation residual risk 2025 2026` | `2026-07-25T16:16:08Z` | 是；一次 | 完整记录本次调用返回的全部可见结果；后端未声明总索引规模，故不推断网络完整性 |
| `R8-RS01-D2` | `AI deep research evaluation citation completeness source quality user study 2025 2026` | `2026-07-25T16:16:19Z` | 是；一次 | 完整记录本次调用返回的全部可见结果；后端未声明总索引规模，故不推断网络完整性 |
| `R8-RS01-S1` | `counterexample systematic review search saturation stopping rule misses studies` | `2026-07-25T16:20:54Z` | 是；一次 | 完整记录本次调用返回的全部可见结果；产生一个 high-impact delta |
| `R8-RS01-S2` | `site:reddit.com AI deep research citations shallow missed sources workflow` | `2026-07-25T16:22:50Z` | 是；一次 | 完整记录本次调用返回的全部可见结果；无 high-impact delta |
| `R8-RS01-S3` | `site:news.ycombinator.com deep research citations verify sources shallow` | `2026-07-25T16:23:57Z` | 是；一次 | 完整记录本次调用返回的全部可见结果；无 high-impact delta |

## 4. D1 完整可见结果与逐结果筛选

所有行的 `retrieved_at_utc` 均为 `2026-07-25T16:16:08Z`。`source class` 是本轮筛选分类，不把搜索摘要当作内容快照。`revision` 只记录当前可见状态；决定性来源仍须解析固定 revision 并保存精确字节。

| order | title | URL / locator | source class | upstream cluster | 纳排 | 理由 | revision / supersession |
|---:|---|---|---|---|---|---|---|
| 1 | Confidence-Based Stopping Methods for Systematic Reviews | https://arxiv.org/abs/2606.15380 | peer-reviewed-or-preprint / primary empirical | `D1-C01` | 纳入：决定性候选 | 直接比较以决策信息为中心的停止法与目标 recall；命中问题核心 | arXiv current landing；搜索摘要标注 `2026-06-13`；固定版本待快照 |
| 2 | How perceived future risk shapes consumer decision responses: a systematic review and research agenda | https://www.nature.com/articles/s41599-026-08034-w | peer-reviewed / topical review | `D1-C02` | 排除 | “future risk”是研究对象，不是检索停止或残余漏检风险 | published `2026-06-25`；live article |
| 3 | Time's Influence: A Systematic Review of Biases in Intertemporal Decision-Making | https://pubmed.ncbi.nlm.nih.gov/40829785/ | official index / peer-reviewed metadata | `D1-C03` | 排除 | 研究主题为跨期决策偏差，与搜索停止机制无关 | PubMed live metadata；`Epub 2025-08-19` |
| 4 | Decision-Theoretic Stopping Rules for Document Screening | https://arxiv.org/abs/2606.07071 | peer-reviewed-or-preprint / primary empirical | `D1-C04` | 纳入：决定性候选 | 直接以 Expected Value of Perfect Information 推导停止政策并在专利与系统综述任务上实验 | arXiv current landing；搜索摘要标注 `2026-06-05`；固定版本待快照 |
| 5 | Systematic review of the effects of decision fatigue in healthcare professionals on medical decision-making | https://www.tandfonline.com/doi/full/10.1080/17437199.2025.2513916 | peer-reviewed / topical review | `D1-C05` | 排除 | “decision”仅属于被综述主题，不是检索停止规则 | published online `2025-07-01`；live article |
| 6 | Time's Influence: A Systematic Review of Biases in Intertemporal Decision-Making | https://www.annualreviews.org/content/journals/10.1146/annurev-psych-091924-040158?TRACK=RSS | publisher page / peer-reviewed | `D1-C03` | 排除：同上游重复 | 与 order 3 同一论文，且主题不相关 | publisher live page；同一 DOI |
| 7 | Purposeful sampling and saturation in qualitative research methodologies: recommendations and review | https://link.springer.com/article/10.1007/s11846-025-00881-2 | peer-reviewed / method review | `D1-C06` | 纳入：背景限定 | 可帮助区分 qualitative saturation 与开放网络文档检索停止；不能直接证明后者 | published `2025-03-25`；live article |
| 8 | Fuzzy set-based decision-making methods in business management and finance research: a systematic literature review | https://link.springer.com/article/10.1186/s43093-026-00896-5 | peer-reviewed / topical review | `D1-C07` | 排除 | 仅说明一般 SLR 流程；不评价停止规则 | published `2026-06-18`；live article |
| 9 | The exploitation of data to support decision-making in healthcare: a systematic literature review and future research directions | https://link.springer.com/article/10.1007/s11301-024-00482-5 | peer-reviewed / topical review | `D1-C08` | 排除 | 与检索停止问题无直接关系 | published `2025-04-03`；live article |
| 10 | An integrative review on unveiling the causes and effects of decision fatigue to develop a multi-domain conceptual framework | https://www.frontiersin.org/journals/cognition/articles/10.3389/fcogn.2025.1719312/full | peer-reviewed / topical review | `D1-C09` | 排除 | 研究 decision fatigue；PRISMA 使用不等于停止规则证据 | published `2026-01-09`；live article |
| 11 | What Decision-Making Processes Are Used by Nurses in Initiating, Monitoring, and Ending One-to-One Observations? A Systematic Review | https://discovery.ucl.ac.uk/id/eprint/10220505/ | institutional repository / accepted manuscript metadata | `D1-C10` | 排除 | “ending”是护理观察决策，不是综述搜索停止 | repository live record；accepted manuscript |
| 12 | Prediction models for maltreatment risk: TRIPOD/PROBAST compliance, calibration, and fairness-A systematic review | https://pubmed.ncbi.nlm.nih.gov/41643238/ | official index / peer-reviewed metadata | `D1-C11` | 排除 | 风险模型综述，不是停止规则研究 | PubMed live metadata；`Epub 2026-02-04` |
| 13 | A systematic review and meta-analyses of the temporal stability and convergent validity of risk preference measures | https://www.nature.com/articles/s41562-024-02085-2 | peer-reviewed / topical review | `D1-C12` | 排除 | “stability”指测量稳定性，不是搜索稳定性 | published `2025-01-27`；live article |
| 14 | Decision making tools for post-wildfire flood response and resilience: a systematic literature review | https://link.springer.com/article/10.1007/s10669-026-10096-9 | peer-reviewed / topical review | `D1-C13` | 排除 | 展示一次具体综述的检索流程，不检验停止充分性 | live article；检索覆盖至 `2025-05-01` |
| 15 | How perceived future risk shapes consumer decision responses reference PDF | https://www.nature.com/articles/s41599-026-08034-w_reference.pdf | publisher PDF / same article | `D1-C02` | 排除：同上游重复 | 与 order 2 同一论文且不相关 | publisher PDF；同一 DOI |
| 16 | Systematic Reviews | https://fcsalud.ua.es/en/portal-de-investigacion/documentos/tools-for-the-bibliographic-research/guide-of-systematic-reviews-in-social-sciences.pdf | institutional-hosted method guide | `D1-C14` | 纳入：历史反证/背景 | 摘要明确提示没有通用硬停止规则；用于限制任何“单一规则普适”表述 | 旧版 PDF；精确版本与原始出版信息待核 |
| 17 | Submitted May 29, 2026 | https://ecoevorxiv.org/repository/object/13264/download/23422/?embed=True | preprint PDF / topical review | `D1-C15` | 排除 | 摘要只显示某生态综述使用 stopping heuristic，未显示其能回答本主题 | submitted `2026-05-29`；版本待核 |
| 18 | Volume 8 Issue 24 (March 2026) PP. 13-34 | https://gaexcellence.com/ijirev/article/download/6950/6221/22688 | journal PDF / topical review | `D1-C16` | 排除 | 只描述一般系统综述收集，未出现停止规则评估 | issue `2026-03`；固定性待核 |
| 19 | JANUARY 2026 | https://www.ncbi.nlm.nih.gov/books/NBK621684/pdf/Bookshelf_NBK621684.pdf | official government-hosted report PDF | `D1-C17` | 排除 | 搜索摘要涉及更新检索与 PRESS，但没有停止规则比较 | PDF 标注 `2026-01`；版本待核 |
| 20 | Systematic Reviews | https://systematicreviewsjournal.biomedcentral.com/counter/pdf/10.1186/s13643-025-02864-6.pdf | peer-reviewed PDF / topical review | `D1-C18` | 排除 | 具体综述方法，不直接研究停止充分性 | `2025` article PDF；live counter endpoint |
| 21 | Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search? | https://arxiv.org/abs/2302.03495 | preprint / primary evaluation | `D1-C19` | 排除 | 评价 query formulation，而不是何时停止 | arXiv current landing；固定版本待核 |
| 22 | Search Strategy Formulation for Systematic Reviews: issues, challenges and opportunities | https://arxiv.org/abs/2112.09424 | preprint / method study | `D1-C20` | 纳入：背景支持 | 支持搜索策略透明、可复现与可解释；不单独支持停止充分性 | arXiv current landing；固定版本待核 |

## 5. D2 完整可见结果与逐结果筛选

所有行的 `retrieved_at_utc` 均为 `2026-07-25T16:16:19Z`。社区结果即使纳入，也只进入 failure hypothesis、用户负担或 reopen trigger。

| order | title | URL / locator | source class | upstream cluster | 纳排 | 理由 | revision / supersession |
|---:|---|---|---|---|---|---|---|
| 1 | DRACO: a Cross-Domain Benchmark for Deep Research Accuracy, Completeness, and Objectivity | https://arxiv.org/abs/2602.11685 | preprint / primary benchmark | `D2-C01` | 纳入：决定性候选 | 直接把 accuracy、completeness/objectivity 与 citation quality 分维度评估 | arXiv current landing；搜索摘要标注 `2026-02-12`；固定版本待快照 |
| 2 | Rethinking Literature Search Evaluation: Deep Research Helps, and Human Citation Lists Are Not a Ground Truth | https://arxiv.org/abs/2605.29234 | preprint / primary evaluation | `D2-C02` | 纳入：决定性候选 | 直接反驳把人工 citation list 当完备 ground truth，并主张多轴评价 | arXiv current landing；搜索摘要标注 `2026-05-28`；固定版本待快照 |
| 3 | Deep-Research Eval: An Automated Framework for Assessing Quality and Reliability in Long-Form Reports | https://www.mdpi.com/2076-3417/16/5/2546 | peer-reviewed / primary framework | `D2-C03` | 纳入：决定性候选 | 把内容质量与来源可靠性拆分，且公开其自动评价边界 | published `2026`；live article |
| 4 | Evaluating Deep Research Performance in the Wild with the DRACO Benchmark | https://research.perplexity.ai/articles/evaluating-deep-research-performance-in-the-wild-with-the-draco-benchmark | vendor primary report / benchmark release | `D2-C01` | 纳入：同上游背景 | 是 DRACO 作者/发布方说明，不算独立支持；可用于任务构造与发布上下文 | published `2026-02-04`；mutable vendor page |
| 5 | Research quality evaluation by AI in the era of Large Language Models: Advantages, disadvantages, and systemic effects | https://arxiv.org/abs/2506.07748 | preprint / review | `D2-C04` | 排除 | 主题是 AI 评价科研质量，不是 deep-research 输出证据完整性 | arXiv current landing；固定版本待核 |
| 6 | ResearcherBench: Evaluating Deep AI Research Systems on the Frontiers of Scientific Inquiry | https://arxiv.org/abs/2507.16280 | preprint / primary benchmark | `D2-C05` | 纳入：决定性候选 | 显式拆分专家 rubric、citation faithfulness 与 groundedness/coverage | arXiv current landing；搜索摘要标注 `2025-07-22`；固定版本待快照 |
| 7 | Deep-Research Eval: An Automated Framework for Assessing Quality and Reliability in Long-Form Reports | https://www.researchgate.net/publication/401662522_Deep-Research_Eval_An_Automated_Framework_for_Assessing_Quality_and_Reliability_in_Long-Form_Reports | secondary mirror / author-upload locator | `D2-C03` | 排除：同上游重复 | 与 order 3 同一论文，且镜像不优于出版方 | ResearchGate mutable record |
| 8 | LiveResearchBench: A Live Benchmark for User-Centric Deep Research in the Wild | https://openreview.net/forum?id=ghwbZ3uhEd&noteId=0F4GZSjDbn | peer-reviewed conference record / primary benchmark | `D2-C06` | 纳入：决定性候选 | 动态任务与多维评价直接暴露开放网络、覆盖、citation quality 的边界 | published `2026-01-26`；last modified `2026-03-01`；OpenReview revisions |
| 9 | Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents - Paper Detail | https://deeplearn.org/arxiv/746191/cited-but-not-verified%3A-parsing-and-evaluating-source-attribution-in-llm-deep-research-agents | secondary paper index | `D2-C07` | 排除：仅作上游发现 | 摘要命中 citation 表面质量与事实可靠性断裂，但该页面不是上游论文 | mutable secondary index；应解析上游论文 |
| 10 | DeepResearchEval: An Automated Framework for Deep Research Task Construction and Agentic Evaluation | https://www.alphaxiv.org/abs/2601.09688 | secondary paper explainer | `D2-C08` | 纳入：仅作上游发现 | 摘要提出只核 cited claims 会漏 uncited factual claims；决定性使用须转到上游固定版本 | alphaXiv mutable explainer；上游 arXiv id `2601.09688` |
| 11 | DR3-Eval: Towards Realistic and Reproducible Deep Research Evaluation | https://www.alphaxiv.org/abs/2604.14683v1 | secondary paper explainer | `D2-C09` | 纳入：背景限定 | 动态 web 与任务歧义直接相关，但需上游论文/仓库才可作证据 | alphaXiv locator 指向 `2604.14683v1` |
| 12 | Evaluation Sheet for Deep Research: A Use Case for Academic Survey Writing | https://aclanthology.org/2025.winlp-main.36/ | official proceedings / primary evaluation | `D2-C10` | 纳入：背景支持 | 是学术 survey-writing 场景的评价表，可检查维度是否遗漏 | ACL Anthology fixed proceedings locator `2025.winlp-main.36` |
| 13 | Citation Evaluation in LLM Research Agents | https://www.emergentmind.com/papers/2605.06635 | secondary paper index | `D2-C07` | 排除：同上游发现簇 | 与 order 9 指向同一 citation-evaluation 上游主题，二级摘要不算独立来源 | mutable secondary index；上游 arXiv id `2605.06635` |
| 14 | Paper page - ReportBench: Evaluating Deep Research Agents via Academic Survey Tasks | https://huggingface.co/papers/2508.15804 | secondary paper index / community platform | `D2-C11` | 纳入：仅作上游发现 | 命中 statement faithfulness、literature quality 与 reproducibility，但应使用上游论文/仓库 | mutable paper page；上游 id `2508.15804` |
| 15 | ReportBench: Evaluating Deep Research Agents via Academic Survey Tasks | https://www.alphaxiv.org/abs/2508.15804v1 | secondary paper explainer | `D2-C11` | 排除：同上游重复 | 与 order 14 同一论文；不增加独立性 | alphaXiv locator 指向 `2508.15804v1` |
| 16 | Exploring the Dilemma of AI Use in Medical Research and Knowledge Synthesis: A Perspective on Deep Research Tools | https://www.jmir.org/2025/1/e75666/ | peer-reviewed perspective with empirical evaluation | `D2-C12` | 纳入：反证候选 | 直接讨论 citation integrity、critical appraisal 与人工验证负担；不能外推全部领域 | published `2025`；DOI `10.2196/75666`；live article |
| 17 | Vol. 7, n. 2, julio-diciembre 2025 | https://revistas.up.edu.mx/rpc/article/download/3675/2981/12540 | journal PDF / perspective or review | `D2-C13` | 纳入：背景限定 | 搜索摘要涉及 source verification 与错误 attribution；题名/方法信息不足，不能作决定性来源 | issue `2025`；PDF endpoint |
| 18 | Under review as a conference paper at ICLR 2026 | https://openreview.net/pdf/55441a98c82fba30b636617825e8e1c3bcf32658.pdf | conference submission PDF / primary candidate | `D2-C14` | 排除：元数据不足 | 可见标题只有投稿状态，无法在搜索结果层唯一判断论文与 revision | under review；fixed-looking PDF token，身份待核 |
| 19 | Published as a conference paper at ICLR 2026 | https://openreview.net/pdf/df1bb1c9eebe1f58b29a9a252921ee5a1f6234d7.pdf | conference paper PDF / primary candidate | `D2-C15` | 排除：元数据不足 | 可见标题不足以判断与本主题的直接关系 | published at ICLR `2026`；PDF token |
| 20 | Under review as a conference paper at ICLR 2026 | https://openreview.net/pdf/7698f44b6aed21c92eeafc9966df50d81bcf9208.pdf | conference submission PDF / primary candidate | `D2-C16` | 排除：元数据不足 | 可见标题不足，摘要片段不能唯一确定评价设计 | under review；PDF token |
| 21 | Deep Research: A Systematic Survey | https://deep-research-survey.github.io/static/doc/Deep-Research-Survey.pdf | survey PDF / secondary synthesis | `D2-C17` | 纳入：背景支持 | 可用于评价维度和基准版图，不作为任一机制发生率的独立主证据 | project-hosted PDF；搜索摘要标注 `2026` |
| 22 | SIGIR 2026 Program | https://sigir2026.org/SIGIR2026_program.pdf | official conference program | `D2-C18` | 排除 | 仅由节目摘要偶然命中 citation-rich 文本，不是评价研究本体 | conference program `2026` |
| 23 | ChatGPT Deep Research | https://en.wikipedia.org/wiki/ChatGPT_Deep_Research | encyclopedia / secondary | `D2-C19` | 排除 | 二级产品概述，不支持决定性机制 claim | mutable page；crawl snapshot 未保存 |
| 24 | I measured how often AI engines cite the sources they retrieve. Across 8 B2B projects, ChatGPT cited 41%, Google AI Overview 77%. | https://www.reddit.com/r/GEO_optimization/comments/1v0ltsc/i_measured_how_often_ai_engines_cite_the_sources/ | practitioner/community self-report | `D2-C20` | 纳入：failure hypothesis only | 可产生“retrieval 与 citation 不等价”的审计探针；不能支持发生率，标题数字不进入机制结论 | mutable Reddit thread |
| 25 | Is “Deep Research” really supposed to check only 15 sources? | https://www.reddit.com/r/perplexity_ai/comments/1thln76/is_deep_research_really_supposed_to_check_only_15/ | practitioner/community report | `D2-C21` | 纳入：用户负担/reopen trigger only | 提供用户对来源深度与交叉核验的失败感受；不证明系统普遍行为 | mutable Reddit thread |
| 26 | We analyzed 10,000 AI citations and found 7 patterns that separate content that gets referenced from content that gets ignored | https://www.reddit.com/r/AISearchLab/comments/1r2181s/we_analyzed_10000_ai_citations_and_found_7/ | practitioner/community promotional self-report | `D2-C22` | 排除：不可靠机制证据 | 未见可复核数据与方法；营销动机明显 | mutable Reddit thread |
| 27 | We analyzed 10,000 sources cited by AI models. Here's what we're seeing works to get cited on AI models. | https://www.reddit.com/r/GenEngineOptimization/comments/1r214p4/we_analyzed_10000_sources_cited_by_ai_models/ | practitioner/community promotional self-report | `D2-C22` | 排除：同上游重复 | 与 order 26 同一组织/分析，不增加独立性 | mutable Reddit thread |
| 28 | Pearl Pu | https://en.wikipedia.org/wiki/Pearl_Pu | encyclopedia / biography | `D2-C23` | 排除 | 人物条目中的 user study 片段与 deep-research 评价无直接关系 | mutable page |
| 29 | AI citations don’t last nearly as long as people think. Data from a recent study, and the drop-off is kinda wild | https://www.reddit.com/r/AISEOTricks/comments/1uxw3pk/ai_citations_dont_last_nearly_as_long_as_people/ | practitioner/community second-hand report | `D2-C24` | 纳入：reopen trigger only | 可产生“动态 citation 可见性漂移”重开触发器；不能支持标题中的发生率 | mutable Reddit thread |
| 30 | Which AI Model Is Best for Deep Research in 2026? | https://www.reddit.com/r/OriginalityHub/comments/1ux5rgg/which_ai_model_is_best_for_deep_research_in_2026/ | practitioner/community promotional comparison | `D2-C25` | 排除 | 推广性产品比较，来源与方法不透明 | mutable Reddit thread |
| 31 | Which AI for actual research ? | https://www.reddit.com/r/OpenAI/comments/1tku36g/which_ai_for_actual_research/ | practitioner/community discussion | `D2-C26` | 纳入：用户负担 hypothesis only | 表明用户目标包含限制 hallucination 与页级引用；评论中的产品数字与性能说法不采信 | mutable Reddit thread |
| 32 | Generative engine optimization | https://en.wikipedia.org/wiki/Generative_engine_optimization | encyclopedia / secondary | `D2-C27` | 排除 | GEO 与研究报告证据完整性不是同一评价对象 | mutable page |
| 33 | How AI Systems Choose What to Cite: The Science Behind LLM Citations (2026 Research) | https://www.reddit.com/r/GEO__AI__SEO/comments/1rv5s7s/how_ai_systems_choose_what_to_cite_the_science/ | practitioner/community promotional post | `D2-C28` | 排除 | 以品牌监测/SEO 为导向，未见可复核研究设计 | mutable Reddit thread |
| 34 | AI research compilation 2025 | https://www.reddit.com/r/ArtificialInteligence/comments/1lk0w9x | practitioner/community compilation | `D2-C29` | 排除 | 泛 AI 论文汇编，与 deep-research citation 评价不直接相关 | mutable Reddit thread |
| 35 | Perplexity AI | https://en.wikipedia.org/wiki/Perplexity_AI | encyclopedia / secondary | `D2-C30` | 排除 | 二级产品条目；不能替代原始评价论文 | mutable page |
| 36 | AI Research Compilation 2025 | https://www.reddit.com/r/ArtificialSentience/comments/1lk10xb | practitioner/community compilation | `D2-C29` | 排除：同上游重复 | 与 order 34 同一汇编文本的跨版发布 | mutable Reddit thread |
| 37 | Reasoning model | https://en.wikipedia.org/wiki/Reasoning_model | encyclopedia / secondary | `D2-C31` | 排除 | 泛模型条目，仅偶然提及 Deep Research | mutable page |

## 6. D1/D2 后冻结的 discovery claims 与 deltas

冻结 UTC：`2026-07-25T16:17:52Z`。以下内容在任何 S 查询之前写入。S1-S3 可以反驳、限制或新增 delta，但不得事后改写本节的发现阶段状态。

### 6.1 冻结的候选原子 claims

| discovery claim id | 冻结 claim | 当前证据簇 | impact | 作者侧状态与限制 |
|---|---|---|---|---|
| `RS01-DC-01` | 对开放检索，“没有新结果”或单一 target recall 不是天然的决定充分性证明；停止条件需要显式绑定决策目标、漏失后果、继续检索成本和残余风险。 | `D1-C01`, `D1-C04`, 反证边界 `D1-C14` | high | 搜索摘要支持候选方向；需固定论文版本与精确页/段快照。现阶段不能外推为普适最优规则。 |
| `RS01-DC-02` | 研究报告评价必须把 claim-level entailment、citation presence、citation/source quality 与 coverage/completeness 分开；任何单一维度都不足以推出整体可靠。 | `D2-C01`, `D2-C03`, `D2-C05`, `D2-C06`, `D2-C07` | high | 多个评价工作方向一致，但簇间任务和标注定义不同；需快照后逐 claim 核实。 |
| `RS01-DC-03` | 只审计带 citation 的句子会留下“无引用实质事实 claim”盲点，因此 material-claim inventory 必须先于 citation 审核。 | `D2-C08`，由 `D2-C07` 提供相邻失败方向 | high | 当前只由二级发现页摘要直接暴露；必须取得上游固定版本，否则该 claim 的内容快照 predicate 为 false。 |
| `RS01-DC-04` | 人工 citation list 也不能自动当作开放网络检索的完备 ground truth；评价需要多轴指标和对 ground truth 偏差的显式限制。 | `D2-C02` | medium | 单一预印本候选；需要固定版本、方法与结果范围核验。 |
| `RS01-DC-05` | practitioner 对浅来源、漏源、动态引用和核验负担的报告只能转化为失败探针与重开触发器，不能转化为机制发生率。 | `D2-C20`, `D2-C21`, `D2-C24`, `D2-C26` | medium | 权限边界来自预注册；社区材料只用于构造 probe，不作 incidence 证据。 |

### 6.2 冻结的 architecture / decision deltas

| delta id | 相对 R7 冻结决定的变化 | 可执行落点 | impact | discovery 后状态 |
|---|---|---|---|---|
| `RS01-DD-01` | 将“稳定性轮无高影响 delta”保留为必要条件，但明确它不是单独充分的停止理由；加入 decision-loss/cost/residual-risk stop receipt。 | contract + gate：每次 closure receipt 必须列出 decision cell、未检索到的可能后果、继续搜索成本、可接受残余风险与 reopen trigger；任一 critical/major contradiction 未关闭则拒绝停止。 | high | 冻结，等待 S1-S3 反证 |
| `RS01-DD-02` | 将引用审核入口从“已有 citation 的句子”前移到“完整 material-claim inventory”。 | contract + test：先枚举报告中所有 material claims（有引用和无引用），再分别检查 citation presence、source snapshot、entailment、source quality、counterevidence；测试必须含 uncited factual claim negative case。 | high | 冻结，等待 S1-S3 反证 |
| `RS01-DD-03` | 不把单一 human reference list、URL 数量、citation 数量或 benchmark 总分当 closure oracle。 | rejection + gate：closure 至少保留来源簇去重、claim coverage、逐 claim entailment、反证、残余风险和任务特定决策影响；ground-truth 来源偏差单列 limitation。 | medium | 冻结，等待 S1-S3 反证 |

### 6.3 discovery 阶段无 delta 的内容

- D1 中大量“主题包含 decision/risk/stability 的系统综述”只是词面命中，不改变架构。
- D2 中同一论文的镜像、作者博客或二级索引不增加独立证据簇。
- benchmark 多一个评价维度、额外支持来源或措辞改进，若不引入新高影响 failure class、决定反转或 open critical/major contradiction，不单独计为稳定性 delta。

## 7. S1 完整可见结果与逐结果筛选

所有行的 `retrieved_at_utc` 均为 `2026-07-25T16:20:54Z`。

| order | title | URL / locator | source class | upstream cluster | 纳排 | 理由 | revision / supersession |
|---:|---|---|---|---|---|---|---|
| 1 | Feasibility and desirability of screening search results from Google Search exhaustively for systematic reviews: A cross-case analysis | https://pubmed.ncbi.nlm.nih.gov/36633509/ | official index / peer-reviewed empirical study | `S1-C01` | 纳入：决定性候选 | 直接研究 Google Search 可见结果、固定前若干条停止与穷尽筛选的可行性 | PubMed live metadata；PMID `36633509`；DOI `10.1002/jrsm.1622` |
| 2 | The capture-mark-recapture technique can be used as a stopping rule when searching in systematic reviews | https://pubmed.ncbi.nlm.nih.gov/18722088/ | official index / peer-reviewed empirical study | `S1-C02` | 纳入：历史方法候选 | 直接测试 CMR/Horizon Estimate，并明确还需更多研究 | PubMed live metadata；PMID `18722088`；DOI `10.1016/j.jclinepi.2008.06.001` |
| 3 | Characteristics and recovery methods of studies falsely excluded during literature screening—a systematic review | https://pmc.ncbi.nlm.nih.gov/articles/PMC9644550/ | official full-text archive / peer-reviewed systematic review | `S1-C03` | 纳入：决定性 missed-study 候选 | 直接研究 screening false exclusion 与恢复方法；证明停止信号之外仍有筛选漏失通道 | PMC full text；article version of record linked；exact bytes 待快照 |
| 4 | The capture–mark–recapture technique can be used as a stopping rule when searching in systematic reviews | https://www.sciencedirect.com/science/article/pii/S0895435608001509 | publisher page / peer-reviewed empirical study | `S1-C02` | 排除：同上游重复 | 与 order 2 同一论文；出版页不增加独立性 | publisher live page；PII `S0895435608001509` |
| 5 | Confidence-Based Stopping Methods for Systematic Reviews | https://arxiv.org/abs/2606.15380 | preprint / primary empirical | `D1-C01` | 纳入：发现阶段同源复现 | 与 D1 决定性候选相同；支持检索稳定性但不是新证据簇 | arXiv current landing；固定版本待快照 |
| 6 | Chapter 4: Searching for and selecting studies | https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04 | official primary reporting/search method | `S1-C04` | 纳入：决定性候选 | 官方方法章明确数据库搜索会漏研究、应记录停止理由，并区分 review 类型的停止逻辑 | mutable “current” handbook page；版本号与精确字节待快照 |
| 7 | Sample sizes for saturation in qualitative research: A systematic review of empirical tests | https://pubmed.ncbi.nlm.nih.gov/34785096/ | official index / peer-reviewed topical method review | `S1-C05` | 排除 | 研究 qualitative sample saturation，不是开放文档检索停止 | PubMed live metadata；PMID `34785096` |
| 8 | Characteristics and recovery methods of studies falsely excluded during literature screening—a systematic review | https://link.springer.com/article/10.1186/s13643-022-02109-w | publisher page / peer-reviewed systematic review | `S1-C03` | 排除：同上游重复 | 与 order 3 同一论文 | publisher live page；DOI `10.1186/s13643-022-02109-w` |
| 9 | Characteristics and recovery methods of studies falsely excluded during literature screening-a systematic review | https://www.rti.org/publication/characteristics-recovery-methods-studies-falsely-excluded-literature-screening-systematic-review | institutional author record | `S1-C03` | 排除：同上游重复 | 与 order 3 同一论文；机构记录不增加独立性 | mutable institutional record |
| 10 | Chapter 4: Searching for and selecting studies | https://training.cochrane.org/handbook/current/chapter-04 | official mirror / primary method | `S1-C04` | 排除：同上游重复 | 与 order 6 同一 Cochrane 章节 | mutable “current” mirror |
| 11 | Statistical stopping criteria for automated screening in systematic reviews | https://pmc.ncbi.nlm.nih.gov/articles/7700715/ | official full-text archive / peer-reviewed primary method | `S1-C06` | 纳入：方法对照 | 提供带置信度的 recall stopping workflow；用于对照 decision-focused stopping 的适用边界 | PMC full text；exact version 待快照 |
| 12 | Estimating the Horizon of Articles to Decide When to Stop Searching in Systematic Reviews: An Example Using a Systematic Review of RCTs Evaluating Osteoporosis Clinical Decision Support Tools | https://pmc.ncbi.nlm.nih.gov/articles/PMC2655834/ | official full-text archive / peer-reviewed empirical study | `S1-C02` | 排除：同上游重复 | 与 order 2/4 同一 CMR 研究的全文版本 | PMC full text；PMCID `PMC2655834` |
| 13 | A practical guide to evaluating sensitivity of literature search strings for systematic reviews using relative recall | https://pubmed.ncbi.nlm.nih.gov/41626904/ | official index / peer-reviewed method guide | `S1-C07` | 纳入：决定性候选 | 直接指出不敏感 search string 会漏相关研究并限制/偏置证据范围；对应检索式漏失通道 | PubMed live metadata；PMID `41626904` |
| 14 | Systematic Reviews | https://dbc.library.uu.nl/bitstream/handle/1874/459755/s13643-024-02699-7.pdf?isAllowed=y&sequence=1 | institutional repository PDF / peer-reviewed method paper | `S1-C08` | 纳入：上游发现 | 摘要命中 early stopping、漏研究与透明/accountable search；标题元数据不足，决定性使用前须解析版本 | repository PDF；搜索摘要标注 `2024` article |
| 15 | Decision-Theoretic Stopping Rules for Document Screening | https://arxiv.org/abs/2606.07071 | preprint / primary empirical | `D1-C04` | 纳入：发现阶段同源复现 | 与 D1 决定性候选相同；不是新证据簇 | arXiv current landing；固定版本待快照 |
| 16 | A systematic literature review on counterexample explanation | https://arxiv.org/abs/2201.03061 | preprint / topical review | `S1-C09` | 排除 | “counterexample”是被综述主题，不是对停止规则的反例 | arXiv current landing |
| 17 | Systematic Reviews | https://fcsalud.ua.es/en/portal-de-investigacion/documentos/tools-for-the-bibliographic-research/guide-of-systematic-reviews-in-social-sciences.pdf | institutional-hosted method guide | `D1-C14` | 纳入：发现阶段同源复现 | 与 D1 历史背景相同；强调 saturation 的条件性 | 旧版 PDF；精确版本待核 |
| 18 | Computer-assisted screening in systematic evidence synthesis requires robust and well-evaluated stopping criteria | https://discovery.ucl.ac.uk/id/eprint/10200806/1/Computer-assisted%20screening%20in%20systematic%20evidence%20synthesis%20requires%20robust%20and%20well-evaluated%20stopping%20criteria.pdf | institutional repository PDF / primary method commentary | `S1-C10` | 纳入：反证候选 | 直接要求 stopping rule 的稳健置信度并按漏失风险调整；限制自动停止外推 | repository PDF；搜索摘要标注 `2025`；版本待快照 |
| 19 | Searching and Stopping: | https://pure.strath.ac.uk/ws/portalfiles/portal/118318378/Maxwell_etal_CIKM_2015_Searching_and_stopping_an_analysis_of_stopping_rules_and_strategies.pdf | institutional repository / empirical search-behavior paper | `S1-C11` | 纳入：背景限定 | 研究人类搜索停止策略；可说明行为因素，但不证明系统综述 closure | repository PDF；CIKM `2015` paper |
| 20 | Systematic Reviews | https://systematicreviewsjournal.biomedcentral.com/counter/pdf/10.1186/s13643-024-02502-7.pdf | peer-reviewed PDF / active-learning method | `S1-C12` | 纳入：方法对照 | 摘要命中主动学习停止与 search validation；需解析完整题名和方法后才能决定性使用 | `2024` article PDF endpoint |
| 21 | Can ChatGPT Write a Good Boolean Query for Systematic Review Literature Search? | https://arxiv.org/abs/2302.03495 | preprint / primary evaluation | `D1-C19` | 纳入：failure-channel 支持 | 虽不研究停止，但说明 search-query 质量可在停止判断之前制造漏召回/偏差 | arXiv current landing；固定版本待核 |
| 22 | Systematic review search issue | https://www.reddit.com/r/research/comments/1uu5fwk/systematic_review_search_issue/ | practitioner/community cross-post | `S1-C13` | 纳入：implementation failure hypothesis only | 过滤错误导致潜在漏文献；只生成“过滤与索引延迟”探针 | mutable Reddit thread |
| 23 | Systematic review search issue | https://www.reddit.com/r/AskAcademia/comments/1uu5ew1/systematic_review_search_issue/ | practitioner/community cross-post | `S1-C13` | 排除：同上游重复 | 与 order 22 同一问题的跨版发布 | mutable Reddit thread |
| 24 | Systematic review search issue | https://www.reddit.com/r/academicpublishing/comments/1uu5ky6/systematic_review_search_issue/ | practitioner/community cross-post | `S1-C13` | 排除：同上游重复 | 与 order 22/23 同一问题 | mutable Reddit thread |
| 25 | Systematic review needs search criteria, lost due to many searches | https://www.reddit.com/r/academia/comments/1cdp6rp | practitioner/community report | `S1-C14` | 纳入：reopen trigger only | 搜索引擎算法变化导致复演漂移的用户报告；不证明发生率 | mutable Reddit thread |
| 26 | systematic review of the literature /methods | https://www.reddit.com/r/AskAcademia/comments/w5ehm7 | practitioner/community report | `S1-C15` | 纳入：user-burden hypothesis only | 错误检索语法和重做成本可用于用户负担 probe | mutable Reddit thread |
| 27 | Systematic Review | https://www.reddit.com/r/AskAcademia/comments/e9vbt5 | practitioner/community advice | `S1-C16` | 纳入：reproducibility hypothesis only | 社区强调完整记录与过滤理由；只能作工作流假设 | mutable Reddit thread |
| 28 | Systematic review help! | https://www.reddit.com/r/academia/comments/15y0lth | practitioner/community help thread | `S1-C17` | 排除 | 初学者方法建议，不提供可核反例 | mutable Reddit thread |
| 29 | The citation rabbit hole problem: How do you decide when to stop following references? | https://www.reddit.com/r/Researcher/comments/1refm1c/the_citation_rabbit_hole_problem_how_do_you/ | practitioner/community report | `S1-C18` | 纳入：user-burden/reopen hypothesis only | 暴露近期低引用材料与深度核验负担，不能证明最佳停止规则 | mutable Reddit thread |
| 30 | is there a problem with scopus filtering process? or do am i doing something wrong? | https://www.reddit.com/r/AskAcademia/comments/1us1hjz/is_there_a_problem_with_scopus_filtering_process/ | practitioner/community report | `S1-C19` | 纳入：failure hypothesis only | 可生成字段限定和跨数据库结果差异探针 | mutable Reddit thread |
| 31 | [D] Inclusion/Exclusion criteria for systematic review in statstics | https://www.reddit.com/r/statistics/comments/1tfs6p1/d_inclusionexclusion_criteria_for_systematic/ | practitioner/community question | `S1-C20` | 排除 | 讨论是否按代码可复现性排文，不是漏失或停止证据 | mutable Reddit thread |
| 32 | Down the systematic review rabbit hole | https://www.reddit.com/r/PhD/comments/ubjsos | practitioner/community report | `S1-C21` | 纳入：user-burden hypothesis only | 提供 citation-chasing 无界负担场景；不支持机制发生率 | mutable Reddit thread |
| 33 | Minimum of studies for a systematic review? (thoughts) | https://www.reddit.com/r/AskAcademia/comments/10k0nnh/minimum_of_studies_for_a_systematic_review/ | practitioner/community discussion | `S1-C22` | 排除 | 讨论纳入研究数量，不是检索停止充分性 | mutable Reddit thread |

### 7.1 S1 稳定性裁决

裁决 UTC：`2026-07-25T16:21:13Z`。

- `new_high_impact_failure_class = true`。
- 新失效类别：停止规则通常只对其已观察/已排序/已筛选的候选集合给出信号，但相关研究还可能在 search-string/database retrieval、搜索引擎 viewability/ranking、以及 human/automated screening exclusion 三个上游或旁路通道丢失。一个 aggregate “saturation/stopping” 指标会掩盖通道差异。
- 这不反转 `RS01-DD-01`，但使其原表述不足；必须新增 channel-separated residual-risk contract。

| delta id | S1 新增可执行 delta | impact | 冻结状态 |
|---|---|---|---|
| `RS01-DD-04` | contract + gate + tests：closure receipt 分开记录 `(a) query/database retrieval miss risk`、`(b) ranking/viewability/truncation risk`、`(c) screening false-exclusion risk`、`(d) synthesis/claim-coverage risk`。任何通道没有可验证 probe 或有 open critical/major contradiction 时，不得用另一通道的良好停止信号抵消。最小 negative tests 包含已知相关文献未被 query 命中、结果存在但落在可见截断外、结果被错误筛除、来源已纳入但 material claim 未进入报告。 | high | `2026-07-25T16:21:13Z` 冻结；等待 S2/S3 是否出现后续无 high-impact delta 查询 |

因此，S1 不能成为“最后 delta 后的无 delta 稳定性轮”。passing rule 仍未满足。

## 8. S2 完整可见结果与逐结果筛选

所有行的 `retrieved_at_utc` 均为 `2026-07-25T16:22:50Z`。搜索后端返回了 Reddit 多语言镜像、用户页和 Reddit Developers 页面；它们都属于本次调用的可见结果，因此即使无关也逐项保留。

| order | title | URL / locator | source class | upstream cluster | 纳排 | 理由 | revision / supersession |
|---:|---|---|---|---|---|---|---|
| 1 | Building a better search workflow for academic research papers with ai | https://ja.reddit.com/r/searchengines/comments/1upwqei/building_a_better_search_workflow_for_academic/ | practitioner/community self-promotion | `S2-C01` | 纳入：user-burden hypothesis only | 描述搜索、筛选、组织与阅读优先级负担；不支持工具有效性或机制发生率 | mutable Reddit language mirror；post id `1upwqei` |
| 2 | Reddit for Developers | https://developers.reddit.com/apps/venice-bot | developer app listing / implementation README | `S2-C02` | 排除 | 是 subreddit bot 的 missed-post recovery，不是 deep-research citation 失败 | mutable app listing |
| 3 | Are hallucinated citations still a thing? I miss them already. | https://fr.reddit.com/r/Professors/comments/1otqkvh/are_hallucinated_citations_still_a_thing_i_miss/?sort=live | practitioner/community thread | `S2-C03` | 纳入：failure hypotheses only | 可生成 source-existence、DOI、作者、页码、quote 与 claim-source mismatch 的负向探针；匿名报告不能支持发生率 | mutable Reddit language mirror；post id `1otqkvh`；live sort |
| 4 | Building a workflow tool for Radiology study materials—input needed. | https://vi.reddit.com/r/medicalschoolanki/comments/1uj9fvv/building_a_workflow_tool_for_radiology_study/ | practitioner/community product feedback | `S2-C04` | 排除 | 主题是 Radiopaedia 内容搬运与格式化，不是研究 citation 可靠性 | mutable Reddit language mirror |
| 5 | Reddit for Developers | https://developers.reddit.com/apps/botforlazymods | developer app listing / implementation README | `S2-C05` | 排除 | 是宣传内容分类 bot；“verified sources”只出现在配置说明 | mutable app listing |
| 6 | How do younger brands get mentioned in AI search recommendations when competing against legacy giants? | https://pl.reddit.com/r/AISEOTricks/comments/1u8ijio/how_do_younger_brands_get_mentioned_in_ai_search/?sort=top | practitioner/community promotional post | `S2-C06` | 排除 | 目标为 AI SEO，方法与商业动机不适合支持研究 workflow 机制 | mutable Reddit language mirror |
| 7 | chrisq32 (u/chrisq32) - Reddit | https://www.reddit.com/user/chrisq32/ | practitioner/community user profile | `S2-C07` | 排除 | 可见片段是自动化节点连接错误，与 deep-research citation 无关 | mutable user profile |
| 8 | revu pour justinnealey | https://fr.reddit.com/user/justinnealey | practitioner/community user profile/comment aggregation | `S2-C08` | 纳入：failure hypothesis only | 评论把 crawler access、referral、mention/citation 分开；只能生成“观测信号不可互相替代”探针 | mutable user profile aggregation |
| 9 | State standardized tests were graded in less than 24 hours | https://vi.reddit.com/r/Teachers/comments/1t0h32i/state_standardized_tests_were_graded_in_less_than/ | practitioner/community thread | `S2-C09` | 纳入：failure hypothesis only | 可见片段提到带引用回答在 query variations 下互相矛盾；用于 metamorphic probe，不支持发生率 | mutable Reddit language mirror |
| 10 | overzicht voor rahul_4040 | https://nl.reddit.com/user/rahul_4040 | practitioner/community user profile/comment aggregation | `S2-C10` | 排除 | AI SEO/local citation 讨论，不是研究报告可靠性 | mutable user profile aggregation |
| 11 | Request to impliment report feature to remove AI generated images from search results | https://vi.reddit.com/r/duckduckgo/comments/1uzlrhm/request_to_impliment_report_feature_to_remove_ai/ | practitioner/community feature request | `S2-C11` | 排除 | 主题是图像搜索结果过滤 | mutable Reddit language mirror |
| 12 | What's been working best with algos/AI connected to kite(websocket or live data kind of a thing? | https://vi.reddit.com/r/IndiaAlgoTrading/comments/1utw9p8/whats_been_working_best_with_algosai_connected_to/?sort=top | practitioner/community question | `S2-C12` | 排除 | 主题是交易 API/策略，不是 deep-research citation workflow | mutable Reddit language mirror |

### 8.1 S2 稳定性裁决

裁决 UTC：`2026-07-25T16:23:13Z`。

- `new_high_impact_failure_class = false`。
- `decision_reversal = false`。
- `open_critical_or_major_contradiction = false`。
- S2-C03 产生的 source existence、作者/DOI/页码/quote mismatch probes 已被 `RS01-DD-02` 的 citation presence、source snapshot、source range 与 entailment 分离覆盖；S2-C08 的观测信号分层已被 `RS01-DD-04` 的通道分离覆盖；S2-C09 只为现有稳定性/metamorphic 检查增加实例。
- 因此 S2 是 `RS01-DD-04` 之后的后续 reserved stability query，且没有新 high-impact delta。到 S2 为止，预注册 passing rule 已满足；S3 仍须执行，且可推翻该临时结论。

## 9. S3 完整可见结果与逐结果筛选

所有行的 `retrieved_at_utc` 均为 `2026-07-25T16:23:57Z`。全部结果均为 Hacker News 社区讨论，故只支持 failure hypothesis、用户负担、实现反例或 reopen trigger。

| order | title | URL / locator | source class | upstream cluster | 纳排 | 理由 | revision / supersession |
|---:|---|---|---|---|---|---|---|
| 1 | None of those reports are any good though. Maybe for shallow research, but I hav... | https://news.ycombinator.com/item?id=43861012 | practitioner/community discussion | `S3-C01` | 纳入：failure/user-burden hypothesis only | 暴露来源判断不足、任务未完成却返回检索建议、报告过短等 probe；不能支持发生率 | mutable HN item `43861012` |
| 2 | The Differences Between Deep Research, Deep Research, and Deep Research | https://news.ycombinator.com/item?id=43236184 | practitioner/community discussion | `S3-C02` | 纳入：failure/user-burden hypotheses only | 暴露 source attribution、veracity、source selection 与人工复核成本；不能比较产品普遍能力 | mutable HN item `43236184` |
| 3 | Introducing deep research | https://news.ycombinator.com/item?id=42913251 | practitioner/community launch discussion | `S3-C03` | 纳入：implementation counterexample hypotheses only | 含“引用真实页面但误读字段/作者角色”的具体 probe，并讨论验证债务；匿名报告不支持发生率 | mutable HN item `42913251` |
| 4 | The Deep Research problem | https://news.ycombinator.com/item?id=43133207 | practitioner/community article discussion | `S3-C04` | 纳入：failure/user-burden hypotheses only | 暴露 polished completeness overclaim、source-quality 漏检与“真事实拼成错误叙事”风险 | mutable HN item `43133207` |
| 5 | This verification problem is general. As an experiment, I had Claude Cowork writ... | https://news.ycombinator.com/item?id=47289837 | practitioner/community comment | `S3-C05` | 纳入：implementation counterexample hypothesis only | 提供“来源真实但叙事完全错误”的组合型 negative-test 模板；不支持发生率 | mutable HN item `47289837` |
| 6 | Are there good benchmarks for this type of tool? It seems not? Also, I'd compare... | https://news.ycombinator.com/item?id=43065221 | practitioner/community discussion | `S3-C06` | 纳入：failure hypothesis only | 暴露领域背景不足、作者动机/上下文判断缺失；不能把专家自测当标准 benchmark | mutable HN item `43065221` |
| 7 | Ask HN: How to Use "Deep Research"? | https://news.ycombinator.com/item?id=43603574 | practitioner/community question | `S3-C07` | 纳入：source-quality failure hypothesis only | 报告引用 blogspam/listicle 的用户经历可产生低质量来源 probe | mutable HN item `43603574` |
| 8 | I did a trial run with Deep Research this weekend to do a comparative analysis o... | https://news.ycombinator.com/item?id=43177105 | practitioner/community comment | `S3-C04` | 排除：同上游讨论重复 | 是 order 4 讨论中的具体评论/分支，不增加独立来源簇 | mutable HN item `43177105` |
| 9 | How I Don't Use LLMs | https://news.ycombinator.com/item?id=43688005 | practitioner/community article discussion | `S3-C08` | 纳入：failure hypothesis only | 暴露浅层拼接、未回答 prompt 的报告形态；由 completeness/relevance probes 覆盖 | mutable HN item `43688005` |
| 10 | Ask HN: Does acceptance of Wikipedia as reliable source foreshadow same for AI? | https://news.ycombinator.com/item?id=43673637 | practitioner/community question | `S3-C09` | 纳入：source-quality hypothesis only | 简短反例指向“有 citation 不等于 vet source”；不提供独立机制证据 | mutable HN item `43673637` |
| 11 | The Unreliability of LLMs and What Lies Ahead | https://news.ycombinator.com/item?id=44160573 | practitioner/community discussion | `S3-C10` | 纳入：synthesis failure hypothesis only | 暴露词共现被误当因果/物理连接的推断错误；可构造组合型 entailment test | mutable HN item `44160573` |
| 12 | I’ve reviewed a lot of papers, I don’t consider it the reviewers responsibility ... | https://news.ycombinator.com/item?id=46182431 | practitioner/community discussion | `S3-C11` | 纳入：review-burden hypothesis only | 暴露大量弱引用会稀释 reviewer 注意力；只能用于基于影响的复核优先级设计 | mutable HN item `46182431` |

### 9.1 S3 稳定性裁决

裁决 UTC：`2026-07-25T16:24:28Z`。

- `new_high_impact_failure_class = false`。
- `decision_reversal = false`。
- `open_critical_or_major_contradiction = false`。
- S3-C04、S3-C05、S3-C10 强化一个组合型 probe：所有 source locator 可解析、局部事实可各自为真，但跨来源的关系、因果链或总叙事仍不被来源蕴含。该 probe 已属于 `RS01-DD-02` 的 material-claim inventory/entailment 与 `RS01-DD-04` 的 synthesis-risk 通道，不产生新 architecture delta。
- 对 `RS01-DD-02`/`RS01-DD-04` 的 test clarification（非 delta）：增加 negative case——`source_exists=true` 且 atomic supporting facts 为真，但 synthesized conclusion/causal relation 为 false；gate 必须拒绝。
- practitioner 结果不支持任何产品错误率、能力排序或普遍机制结论。

### 9.2 最终稳定性结果

- 最后一个 high-impact delta：`RS01-DD-04`，由 S1 在 `2026-07-25T16:21:13Z` 冻结。
- 后续 reserved stability query S2：无 high-impact delta、无 decision reversal、无 open critical/major contradiction。
- 后续 reserved stability query S3：无 high-impact delta、无 decision reversal、无 open critical/major contradiction。
- `stability_protocol.passing_rule = true`。
- 没有执行或追加第六个 query。

## 10. 快照、原子 claims、predicate 与最终状态

### 10.1 快照清单

规范 manifest：`research/evidence/r8/RS-01/manifest.json`。下表哈希均针对实际保存字节，不是 URL 或搜索摘要的哈希。

| source id | required class / role | fixed revision or mutable identity | UTC | media type | bytes | SHA-256 | 使用范围 | 许可/引用边界 |
|---|---|---|---|---|---:|---|---|---|
| `RS01-SRC-01` | versioned primary reporting/search method | Cochrane Handbook `version 6.5.1`；Chapter 4 last updated `March 2025` | `2026-07-25T16:27:03Z` | `text/html; charset=UTF-8` | `382125` | `728bbac9ad5dae544d1a0549e0fe3f3812e00ad0f4e8c69a0dda2916f0efd26b` | chapter citation；HTML fragments `#section-4-2-2`、`#section-4-4-11`、`#section-4-5` | 未推断开放许可；仅内部证据快照与简短署名引用，不重分发全文 |
| `RS01-SRC-02` | empirical stopping source | `arXiv:2606.07071v1` | `2026-07-25T16:27:25Z` | `application/pdf` | `901478` | `f9123e33da838b45f9aef4787720fb7f58ac3f0535ed39cf77fcb96767c73406` | PDF pp. 1-2, 8-10 | arXiv non-exclusive distribution；仅内部快照和简短署名引用 |
| `RS01-SRC-03` | empirical missed-study source | Europe PMC released version-of-record；`PMC9644550`；DOI `10.1186/s13643-022-02109-w` | `2026-07-25T16:29:40Z` | `application/xml` | `73645` | `6aa2f048c23bc62663c14cf11bf13143d07e60e442055cf3282590fbd6850aa0` | XML article-meta；`Abs1/Par1-Par4`；`Sec1/Par24-Par28` | XML 声明 `CC BY 4.0`；需署名、来源/许可链接与变更说明 |
| `RS01-SRC-04` | decisive deep-research evaluation source | `arXiv:2601.09688v1` | `2026-07-25T16:27:38Z` | `application/pdf` | `2019220` | `3b6a3b8032dcaea9187e5aea88854268c3cf3782ab83e968ea93e0e8b2129446` | PDF pp. 1-2, 5-6 | arXiv non-exclusive distribution；仅内部快照和简短署名引用 |
| `RS01-SRC-05` | decisive literature-search evaluation source | `arXiv:2605.29234v1` | `2026-07-25T16:27:49Z` | `application/pdf` | `488268` | `90f65ea8fae259321341042124f2446f7deaa697953cb79eb3818a2fdb91c390` | PDF pp. 1, 3-5 | arXiv record links `CC BY 4.0`；需署名、许可链接与变更说明 |
| `RS01-SRC-06` | practitioner counterexample | mutable HN item `47289837`；source time `1772906060` / `2026-03-07T17:54:20Z` | `2026-07-25T16:28:25Z` | `application/json; charset=utf-8` | `1545` | `4d4f907c245a1dd924f890beaef04c8f4efe726f3724247af2db105a95ff5841` | JSON `$.id`、`$.parent`、`$.time`、`$.type`、`$.text` | 未推断开放许可；仅内部快照和简短署名引用；只支持 failure hypothesis/verification burden |
| `RS01-SRC-06-CONTEXT` | practitioner parent context | mutable HN story `47289406`；source time `1772903310` / `2026-03-07T17:08:30Z` | `2026-07-25T16:28:44Z` | `application/json; charset=utf-8` | `491` | `f2882f6570e93190e76e3d878e5729c714f15b1690aee139b9d0eb0240b0c6a4` | JSON `$.id`、`$.title`、`$.url`、`$.time`、`$.kids` | 未推断开放许可；仅作 parent context |

控制文件：

| file | bytes | SHA-256 | 用途 |
|---|---:|---|---|
| `research/evidence/r8/RS-01/manifest.json` | `12025` | `2ef7bd6357f037b4fdf1b37b75684b479e624775f3427d34052cc633d19f19e6` | machine-readable snapshot metadata 与 required-class verdict |
| `research/evidence/r8/RS-01/RS01_RETRIEVAL_FAILURE_RECEIPTS.md` | `1574` | `277fa48ee37f2ed31e1c8b42be7af2b4a6480834aae3c3381e0a425374278a31` | HN HTML `429` 与 NCBI OA package `404`/`550` 的失败记录及替代精确字节路径 |

Required snapshot class 裁决：

- `one versioned primary reporting or search method source = true`，由 `RS01-SRC-01` 满足。
- `one empirical stopping or missed-study source = true`，由 `RS01-SRC-02` 与 `RS01-SRC-03` 满足。
- `one practitioner counterexample thread or explicit no-result receipt = true`，由 counted HN item 的官方 API 精确 JSON `RS01-SRC-06` 满足；HTML 线程端点失败不被掩盖，receipt 已保存。
- 两次 preferred representation 失败都没有用 URL/hash-only 代替内容：HN 改用同 item 的官方 API 精确字节；NCBI package 改用同 PMCID/DOI 的 Europe PMC version-of-record full-text XML 精确字节。

### 10.2 最终原子 claims

以下 `author_entailment` 只是作者侧判断，不是独立复核 verdict。

#### `RS01-CL-01`

- `claim_id`: `RS01-CL-01`
- `topic_id`: `RS-01`
- `claim_text`: 对开放检索，新增检索词不再产生相关记录、达到某个 recall 或出现经验性 saturation 都不能自动证明领域穷尽；停止理由应被记录，并应结合 review 类型、检索表现、漏失风险与资源约束。
- `impact`: `high`
- `evidence_cluster_ids`: `S1-C04`
- `source_snapshot_ids`: `RS01-SRC-01`
- `source_ranges`: Cochrane Handbook `version 6.5.1` Chapter 4，HTML fragments `#section-4-2-2`、`#section-4-4-11`、`#section-4-5`
- `author_entailment`: `entailed_for_limited_claim`。保存章节明确说客观判断搜索完成通常困难、已有停止方法很少被正式评价、数据库检索可能漏研究、应记录停止理由，且复杂/定性/living review 的停止重点不同。
- `limitations`: 该章节主要面向系统综述，尤其干预综述；不能单独证明本项目所有开放网络研究任务应采用同一停止算法。
- `decision_effect`: 保留 `open_dynamic_web` 分类；拒绝 field-exhausted 声称；要求 stop receipt、残余风险和重开触发器。

#### `RS01-CL-02`

- `claim_id`: `RS01-CL-02`
- `topic_id`: `RS-01`
- `claim_text`: 在该论文评价的专利与系统综述任务、成本和 payoff 设定内，以 downstream decision utility 与信息价值建模的停止策略通常比只优化 recall 的策略得到更高 net utility；这支持把决策后果和检索成本纳入停止门，但不支持其普适最优。
- `impact`: `high`
- `evidence_cluster_ids`: `D1-C04`
- `source_snapshot_ids`: `RS01-SRC-02`
- `source_ranges`: PDF pp. 1-2, 8-10
- `author_entailment`: `entailed_for_evaluated_conditions_only`。摘要、系统综述结果、讨论和结论都把结论限定在 evaluated cost/payoff settings。
- `limitations`: 单一作者组、固定数据集和参数化 utility；论文也报告某些条件下 fixed budget 或 recall-centric baseline 在特定指标上更好，且 proposed policies 不在所有指标/条件下支配 baseline。
- `decision_effect`: 冻结 `RS01-DD-01`：稳定性无 delta 仍是必要条件，但 stop gate 还必须绑定 decision cell、错误成本、继续搜索成本和残余风险。

#### `RS01-CL-03`

- `claim_id`: `RS01-CL-03`
- `topic_id`: `RS-01`
- `claim_text`: 相关资料可以在检索后筛选阶段被错误排除，因此对已筛选集合的停止信号不能覆盖 screening false-exclusion 风险；恢复方法本身的证据仍有限。
- `impact`: `high`
- `evidence_cluster_ids`: `S1-C03`
- `source_snapshot_ids`: `RS01-SRC-03`
- `source_ranges`: XML `Abs1/Par1-Par4` 与 `Sec1/Par24-Par28`
- `author_entailment`: `entailed`。保存全文直接研究 falsely excluded studies，并在结论中限制恢复方法的确定性。
- `limitations`: 该综述只找到有限方法研究；报告中的 missed-study 数字来自特定 screening 设计，不能外推为本项目、所有 reviewer 或所有 AI workflow 的发生率。
- `decision_effect`: 冻结 `RS01-DD-04`：retrieval、ranking/viewability、screening 与 synthesis/claim coverage 四个漏失通道分开记录和测试，不能互相抵消。

#### `RS01-CL-04`

- `claim_id`: `RS01-CL-04`
- `topic_id`: `RS-01`
- `claim_text`: 只核验 citation-linked statements 会留下 uncited factual claims 未检查的盲点；研究报告审计应先形成 material-claim inventory，再分别检查 citation presence、source snapshot、entailment、source quality 与 counterevidence。
- `impact`: `high`
- `evidence_cluster_ids`: `D2-C08`
- `source_snapshot_ids`: `RS01-SRC-04`
- `source_ranges`: PDF pp. 1-2, 5-6
- `author_entailment`: `entailed_for_blind-spot_claim`。论文明确指出 citation-linked-only verification 留下 uncited factual claims，并将 cited/uncited statement checking 作为其设计目标。
- `limitations`: 这是预印本；其 active fact-checking 是自动化 agentic evaluator，本轮没有独立重跑其 benchmark，也不据此声称其框架已经可靠解决该盲点。
- `decision_effect`: 冻结 `RS01-DD-02`；增加 uncited material fact negative test，且不把 citation existence 当 factual correctness。

#### `RS01-CL-05`

- `claim_id`: `RS01-CL-05`
- `topic_id`: `RS-01`
- `claim_text`: 人工 reference list 是一个已知不完美的 coverage target，不能自动作为开放文献检索的完整 ground truth；recall、topical relevance、diversity 与 network-distance 等诊断回答不同问题，不能用单一轴替代。
- `impact`: `medium`
- `evidence_cluster_ids`: `D2-C02`
- `source_snapshot_ids`: `RS01-SRC-05`
- `source_ranges`: PDF pp. 1, 3-5
- `author_entailment`: `entailed_with_material_limitations`。论文明确区分 coverage against human citations 与 neutral-reader relevance，并要求把诊断共同报告而非单独当阈值。
- `limitations`: 预印本只覆盖 computer-science/arXiv 范围；使用单一 LLM judge、未建模 citation context、bibliography extraction 仍有噪声，并明确说单一 LLM judge 不能作为拒稿 gate。
- `decision_effect`: 冻结 `RS01-DD-03`：拒绝把 human list、URL/citation 数量或单一 benchmark 总分当 closure oracle。

#### `RS01-CL-06`

- `claim_id`: `RS01-CL-06`
- `topic_id`: `RS-01`
- `claim_text`: 一个 practitioner counterexample 报告显示，即使另一个研究工具确认历史事实和 citation source 存在，用户仍面临“验证工具是否重复相同错误”的验证债务；该材料只足以构造循环验证与人工负担 probe。
- `impact`: `medium`
- `evidence_cluster_ids`: `S3-C05`
- `source_snapshot_ids`: `RS01-SRC-06`, `RS01-SRC-06-CONTEXT`
- `source_ranges`: item JSON `$.text`, `$.time`, `$.parent`；parent JSON `$.title`, `$.url`
- `author_entailment`: `entailed_as_reported_experience_only`
- `limitations`: 单一匿名社区报告、无独立复现、任务是历史写作实验；不能支持任何错误率、产品能力排序或普遍机制。
- `decision_effect`: 只加入 negative test/reopen trigger：不得用同类模型的二次认可冒充独立 source-range entailment 复核。

### 10.3 反证、矛盾与决定影响

| counterevidence id | 保留内容 | 影响 |
|---|---|---|
| `RS01-CE-01` | Cochrane 章节没有给出普适 objective stopping rule，并指出相关方法正式评价很少。 | 禁止把 `RS01-SRC-02` 的单一论文算法升级成通用 closure oracle。 |
| `RS01-CE-02` | `RS01-SRC-02` 中 proposed policies 并非在所有条件和指标下支配 baselines；某些设定中 fixed budget 表现更好，而 recall/decision agreement 更高可能伴随更大成本。 | stop contract 必须显式写 utility、cost、error profile 和适用条件；不采用固定万能阈值。 |
| `RS01-CE-03` | `RS01-SRC-03` 明确说恢复 false exclusions 的证据有限，不能对最可靠方法下 firm conclusion。 | channel-separated probe 是 gate；不把某一种 recovery method 写成保证。 |
| `RS01-CE-04` | `RS01-SRC-04` 是自动 evaluator 预印本；“可检查 cited+uncited”是设计/实验，不等于已经可靠完成独立语义复核。 | 独立 reviewer predicate 保持强制，不能由同一研究 agent 或另一个 LLM score 自动替代。 |
| `RS01-CE-05` | `RS01-SRC-05` 的 judge/domain/citation-context 限制使其不能证明 AI list 优于 human list，也不能充当自动拒绝 gate。 | 只采纳“单一 ground truth 不足”和多轴诊断，不采纳产品/主体优劣结论。 |
| `RS01-CE-06` | S3 practitioner 结果包含“真实局部事实/真实来源仍可拼成错误叙事”的报告。 | synthesized relation、因果链和总叙事必须作为 material claim 审核；不能只核每个 citation 是否存在。 |
| `RS01-CE-07` | 搜索后端未提供其全索引规模、排名算法或未显示结果，因此“完整可见结果集”不等于“完整网络结果集”。 | 最强结论仍是 bounded decision sufficiency；保留 backend/ranking/viewability residual risk。 |

当前没有 open critical/major contradiction 会反转 `RS01-DD-01` 至 `RS01-DD-04`；但独立 claim entailment 尚未发生，所以这些决定不能进入 design closure。

### 10.4 冻结 deltas 的可执行规范化

本节只把 D1/D2 和 S1 已冻结的 `RS01-DD-01` 至 `RS01-DD-04` 归一化为 contract/test/gate；不新增 S3 后 architecture delta。

| artifact / gate | 必填内容 | rejection / negative test |
|---|---|---|
| `OpenWebResearchReceipt` | prereg commit/hash/UTC、exact query text、单次调用 UTC、backend 可见集合、result order、逐结果纳排、source class、upstream cluster、revision | query 改写、批量调用、漏记可见结果、backend truncation 未标记时拒绝 |
| `SnapshotManifest` | source id、canonical URL/fixed revision、UTC、media type、byte count、SHA-256、source range、license boundary | URL-only、hash-only、mutable source 无 UTC、exact bytes 失败无 receipt 时拒绝 |
| `MaterialClaimInventory` | 所有 material claim，包括无 citation 的事实、跨来源关系、因果链与总叙事；每项绑定 snapshot/range/counterevidence | uncited factual claim；真实 source 但错误作者/DOI/页码/quote；局部事实为真但 synthesized conclusion 为假时拒绝 |
| `ChannelResidualRiskReceipt` | 分列 query/database retrieval、ranking/viewability/truncation、screening false exclusion、synthesis/claim coverage | 已知相关资料未被 query 命中；结果在可见截断外；结果被误排；来源纳入但 material claim 遗漏，任一发生且未处置时拒绝 |
| `DecisionStopReceipt` | decision cell、错误后果、继续检索成本、当前残余风险、可接受条件、reopen trigger | 只因“没有新结果”、URL/引用数量、human list recall 或单一总分停止时拒绝 |
| `StabilityReceipt` | discovery freeze hash/UTC、S1-S3 顺序、每轮 high-impact delta/contradiction、最后 delta 与后续 no-delta 查询 | 最后 query 产生 high-impact delta，或最后 delta 后无 reserved no-delta query 时 `bounded_incomplete`，禁止第六查询 |
| `IndependentEntailmentReview` | 与 claim 作者分离的 reviewer locator、review input SHA-256、逐 claim verdict/reason/ranges/overclaim/counterevidence | 作者自审、仅 agent 角色改名、没有逐 claim verdict，或 verdict 非 `entailed`/`contested_non_decision_changing` 时拒绝 design closure |

### 10.5 剩余 gaps

1. `independent_entailment_review`: 未执行。作者没有也不会充当独立 reviewer；`RS01-CL-01` 至 `RS01-CL-06` 必须由与作者分离的 reviewer 绑定本报告外部 SHA-256 和上述 source snapshot SHA-256 后逐 claim 裁决。
2. `later_evidence_commit_ancestry`: 当前 raw artifacts 未由本代理提交；检索前 `HEAD` 等于 preregistration commit，当前祖先检查通过。若这些证据之后进入任一 evidence commit，提交者必须对该 commit 重新运行 `git merge-base --is-ancestor 7824a63... <evidence_commit>` 并保存结果。
3. `search_backend_provenance`: 后端没有披露未显示结果、排名算法或全索引规模；因此只能证明完整记录“调用返回的可见集合”。
4. `cross-domain_external_validity`: 决策停止与 deep-research benchmark 来源的任务/领域有限，不能推出跨领域普适性能。
5. `practitioner_replication`: HN item 只产生 probe；本轮固定预算不允许新增第六 query 或另做产品 incidence 研究。
6. `round_level_ordinary_comparison`: 预注册要求的 ordinary baseline comparison 需要独立 reviewer；不在本 RS-01 作者权限内，本报告不对其完成状态作肯定声明。
7. `implementation_evidence`: 本主题只给出 contract/test/gate 研究 delta；没有修改 governance、prototype、scripts，也没有运行实现/变异测试。

### 10.6 残余风险与重开触发器

- Cochrane/PRISMA-S/其他正式搜索与报告规范发布新版本，改变 stopping、reporting 或 reproducibility 要求。
- 出现对 decision-theoretic stopping、false-exclusion recovery、deep-research citation/coverage benchmark 的直接复现失败或新的 high-impact failure class。
- 搜索后端改变索引、ranking、可见结果上限、site filter 或结果去重语义。
- 关键 AI/deep-research 模型、检索栈、citation UI 或可观察 verification 能力变化。
- 实际 negative tests 发现四个 residual-risk 通道之外的新漏失路径，或 frozen tests 无法阻止已知误报。
- 独立 reviewer 对任一 high-impact claim 给出 `not_entailed`、指出遗漏重大反证，或判定 decision delta 超出 source range。
- 实际使用的人工核验/记录成本不可接受，使治理收益低于负担；这需要 ordinary comparison 的独立成本判断。
- 任一快照许可、可访问性、revision 或 hash 与本 manifest 不一致。

### 10.7 Topic closure predicates

| predicate | verdict | 证据/原因 |
|---|---|---|
| 预注册 commit、文件 hash、祖先关系和检索时间通过 | `true_at_raw_artifact_stage` | prereg commit/hash 与 commit 内字节一致；检索 UTC 均晚于 commit UTC；检索前/当前 `HEAD` 等于 prereg commit，ancestor exit `0`。未来 evidence commit 仍须重跑。 |
| 五个 query_id 均有且仅有一次执行或明确工具失败 receipt | `true` | D1、D2、S1、S2、S3 各一次独立 exact-query 搜索；无改写、无批量、无第六 query。 |
| 全部可见结果有逐结果筛选记录且归属唯一 query_id | `true` | Sections 4、5、7、8、9 保留每次调用的完整可见集合、原顺序、纳排、理由、class、cluster、revision。 |
| required snapshot classes 均有保存字节与哈希，或明确 blocked | `true` | 三类均由 exact saved bytes 满足；preferred representation 失败另有 receipt，未用 URL/hash-only 冒充。 |
| 每个决定性 claim 通过独立逐 claim 蕴含复核 | `false` | 只有作者侧 entailment；按用户要求明确留给另一 reviewer。 |
| 矛盾与反证已保留且有决定影响 | `true` | Section 10.3。 |
| 稳定性 passing rule 满足 | `true` | 最后 high-impact delta 在 S1；后续 S2、S3 均无 high-impact delta、decision reversal 或 open critical/major contradiction。 |
| architecture/decision delta 已落到可执行 contract、test、gate、defer 或 rejection | `true` | Sections 6.2、7.1、10.4。 |
| 残余风险和重开触发器已明确 | `true` | Sections 10.5、10.6。 |

### 10.8 最终状态

`bounded_incomplete`

直接阻塞原因：`independent claim entailment review = false`。固定查询预算已正确用完，稳定性规则通过，required snapshots 通过，但预注册明确规定 `author_only_closure = false`。因此本报告不能宣称 design closure、领域穷尽、普通搜索比较完成或最终 release；下一步必须由与本作者分离的 reviewer 对 `RS01-CL-01` 至 `RS01-CL-06` 逐项复核。
