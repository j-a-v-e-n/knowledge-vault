# R8 RS-01 原始研究报告

> 状态：`in_progress_s1_recorded`
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
| `R8-RS01-S2` | `site:reddit.com AI deep research citations shallow missed sources workflow` | — | 尚未执行 | discovery freeze 后执行 |
| `R8-RS01-S3` | `site:news.ycombinator.com deep research citations verify sources shallow` | — | 尚未执行 | discovery freeze 后执行 |

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

## 8. 待执行稳定性阶段

剩余固定执行顺序为 `R8-RS01-S2` → `R8-RS01-S3`。每次执行后将记录：

- 完整可见结果、原始顺序、逐结果纳排；
- source class、upstream cluster、revision/supersession；
- 是否出现新 high-impact failure class、决定反转或 open critical/major contradiction；
- 最后一个 high-impact delta 后是否至少存在一个后续“无高影响 delta”查询。

若 `S3` 仍产生 high-impact delta，则不追加第六个 query，最终状态必须为 `bounded_incomplete`。

## 9. 快照、原子 claims、predicate 与最终状态

尚未完成。决定性来源精确字节、manifest、反证、剩余 gaps、逐 predicate 裁决和最终状态将在 S1-S3 后补齐。任何无法保存 exact bytes 的来源都将保存失败 receipt，并使对应 snapshot predicate 为 false。
