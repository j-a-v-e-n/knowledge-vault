---
title: "Dying / Commoditizing AI Skills 2023-2026 — A4 Research Output"
research_date: 2026-05-12
agent: A4 (dying_skills)
confidence: medium
tags: [AI职业, 技能淘汰, 求职市场]
---

# Dying / Commoditizing AI Skills 2023-2026

## Executive Summary

2023-2026 这三年里，"AI skill" 这个词的含义被重写了至少两次：从 2023 H1 的 "懂 prompt = AI 工程师"，到 2024 H2 的 "懂 RAG/LangChain = AI 工程师"，再到 2025-2026 的 "懂 agentic / evals / tool-use 才是 AI 工程师"。每一波都把上一波的招牌技能压成了 "expected baseline"。本报告盘点 11 个已商品化或正在 dying 的 AI skill / role，关键发现：（1）**Prompt Engineer 1.0** 作为独立头衔已死——Microsoft 调查中它在"最不想新增"的 role 里排倒数第二（Fortune 2025-05），standalone title 在 2024-2026 间下降约 30%；（2）**Naive RAG**（fixed-size chunk + vector DB + top-k retrieval）已是 commodity，工业界讨论从 "RAG vs long-context" 转向 "agentic retrieval" 才是新基线；（3）**初级 SEO / 文案 / 翻译**类内容工作大量塌方——BlueFocus 2023 整批解雇人类写手、DeepL 2025 裁员 25%、一项 UK 调查显示 84% 译者预期需求下降。但 commoditize ≠ disappear：技能往往被 absorb 进更大的 role，活下来的人是 "懂 AI + 懂 domain" 的复合工种。Confidence 整体 medium——单点 datapoint 充分，但 "整个 role 在死" 这种宏观判断仍受不同 source 的口径不一致影响。

---

## Skills / Roles Already Commoditized

| # | Skill / Role | Peak hype | Current status (2026-05) | Replaced by | Strongest evidence |
|---|---|---|---|---|---|
| 1 | Prompt Engineer 1.0 (standalone) | 2023 Q1-Q3 | Commoditized → 嵌入 SWE/ML role | 模型自身改进 + meta-prompting + RAG/eval workflow | Fortune 2025-05 "$200K role obsolete"；Microsoft Work Trend Index |
| 2 | Naive RAG (fixed chunk + vector DB) | 2024 全年 | Commoditized baseline | Long-context + agentic retrieval + late chunking | Dataiku、LlamaIndex 2025-2026 "naive RAG → agentic" |
| 3 | Vanilla LangChain pipeline coding | 2024 | Declining (替代品涌现) | LangGraph / PydanticAI / 自研直调 | HN "Why we no longer use LangChain" (40k+ 浏览)；Latenode 2025 |
| 4 | Pure ML Engineer (无 LLM/agent) | 2020-2023 | Stagnant / 转岗压力 | LLM / AI Engineer 头衔 + agent stack | Medium "AI companies stopped hiring ML engineers Q3 2024" |
| 5 | Data labeling / annotation 操作员 | 2018-2024 | 急剧塌方 | Synthetic data + LLM self-labeling + 高端 expert labeling | Scale AI 2025-07 裁 14% (TechCrunch) |
| 6 | SEO content writer / 低端 copywriter | 2010-2022 | 大量替代 | ChatGPT 直接出稿 | BlueFocus 2023-04 全裁；Washington Post 2023 报道 |
| 7 | Basic-tier 客服 agent | 2022-2024 | 部分替代 (但回潮) | LLM chatbot (Klarna 2024 → 2025 回滚) | Klarna 减 700 岗 → 2025 重新招聘 |
| 8 | General-purpose 翻译员 | 2010s | 价格塌方 | DeepL + GPT-4 / Claude 翻译 | DeepL 2025 自己裁 25%；UK 调查 84% 译者预期需求降 |
| 9 | Traditional NLP engineer (无 transformer) | 2010-2019 | 路径已淘汰 (skill 被 absorb) | Transformer-based NLP (BERT/GPT/T5) | LinkedIn fastest-growing 用的全是 transformer skill |
| 10 | Classic CV engineer (CNN-only) | 2015-2022 | Niche 仍存活 | ViT + multimodal LLM (但 CNN 不死) | NVIDIA / Viso.ai 2025 trend；CNN 仍是 edge/realtime 主力 |
| 11 | AutoML / 大规模超参网格搜索 SaaS | 2018-2023 | 商品化（已 commoditized 成 library） | Foundation model + few-shot；Optuna 等开源 lib | OpenML benchmark；纯 AutoML SaaS 没再出新独角兽 |

---

## Per-skill Deep Dive

### 1. Prompt Engineer 1.0 — "$200K 的 standalone 头衔"

**Peak**: 2023 Q1-Q3。彭博、WSJ 都有过 "Anthropic 给 prompt engineer 开 $375K" 的爆款标题；Coursera 一上线 prompt engineering 课就冲到顶。

**Current status (2026-05)**: 作为 standalone job title 已基本死亡。Fortune 2025-05-07 文章直接定性 "this six-figure role… now obsolete thanks to AI"。Microsoft Work Trend Index 调查里，Prompt Engineer 在 "公司未来计划新增的 role" 里排倒数第二。Salesforce Ben 的 2025 分析称 standalone title 在 2024-2026 减少约 30%，而 "需要 prompt skill 的岗位" 同期增长 3 倍——技能被 absorb 进 SWE / ML / DevOps / Security。

**What replaced it**:
- 模型自己变聪明了——GPT-4o、Claude 3.5/3.7、Gemini 2 都不再依赖 "perfect prompt"，Microsoft CMO 明说 "you don't have to have the perfect prompt anymore"
- Meta-prompting：让 AI 自己写 prompt（DSPy 等框架）
- Evaluation-driven prompt tuning 取代手工调字眼

**Evidence URLs**:
- https://fortune.com/2025/05/07/prompt-engineering-200k-six-figure-role-now-obsolete-thanks-to-ai/
- https://www.salesforceben.com/prompt-engineering-jobs-are-obsolete-in-2025-heres-why/
- https://www.fastcompany.com/91327911/prompt-engineering-going-extinct

**Survival niche**: 模型 red-teaming / safety prompting、structured output engineering for compliance-heavy 行业。不再是 entry-level 入门岗，而是 senior 工程师的一项 sub-skill。

---

### 2. Naive RAG — "fixed-chunk + vector DB + top-k" 三件套

**Peak**: 2024 全年。这一年 LangChain + Pinecone + OpenAI embeddings 是几乎所有 demo 的标配；HackerNews 每周都有 "I built a RAG app" 类型帖子。

**Current status**: Naive RAG 已是 commodity baseline。2024 年 5 月 Anthropic 推 100K context、2024-02 Gemini 1.5 Pro 推 1M context 之后，业界正式开始 "RAG is dead" 辩论。2025 年共识收敛到："naive RAG 死了，agentic RAG 是新基线"——LlamaIndex 2025 标题就叫 *RAG is Dead, Long Live Agentic Retrieval*。

**What replaced it**:
- **Long-context model** 处理整个文档（Wikipedia-style QA、summarization 这类场景 long-context 完胜）
- **Agentic retrieval** —— LLM 自己决定怎么切、怎么搜、要不要多轮
- **Late chunking**（Jina AI 2024）—— 先 encode 全文再切，保留上下文
- **Contextual retrieval**（Anthropic 2024 推出）—— chunk + 上下文摘要联合 embedding

**Evidence**:
- Dataiku blog 直接问 "Is RAG Obsolete?"
- 数据点：full-context 处理同样问题平均 45 秒，naive RAG 1 秒，但 long-context API 成本巨高——Gemini 1.5 Pro 处理 50M token 法律档案 / 天 = $12,500，所以 RAG 没死透
- LlamaIndex / RAGFlow 2025 年终回顾都强调 "naive → agentic" 转型

**Evidence URLs**:
- https://blog.dataiku.com/is-rag-obsolete
- https://www.llamaindex.ai/blog/rag-is-dead-long-live-agentic-retrieval
- https://ragflow.io/blog/rag-review-2025-from-rag-to-context

**Survival niche**: 中小企业、隐私敏感场景、cost-sensitive 应用、citation-quality 要求高的法律/医疗。但 "只会搭 naive RAG" 已不是 hire-able skill。

---

### 3. Vanilla LangChain pipeline 编码

**Peak**: 2023 H2 - 2024 H1。一度是每个 AI tutorial 的默认 stack。

**Current status**: Declining。HackerNews 2024 帖 "Why we no longer use LangChain for building our AI agents" 是 40K+ 浏览的爆款。Latenode 社区 2025 标题就叫 *Why I'm avoiding LangChain in 2025*。开发者抱怨：（1）频繁 breaking change、（2）过度嵌套抽象、（3）文档跟不上更新。

**What replaced it**:
- **LangGraph**（LangChain 自家 pivot，多状态机模型）
- **PydanticAI**（类型安全、轻量）
- **LlamaIndex**（更专 RAG）
- **直接调 API + 少量 glue 代码** —— "自己手写 200 行" 流派

**Evidence URLs**:
- https://news.ycombinator.com/item?id=40739982
- https://community.latenode.com/t/why-im-avoiding-langchain-in-2025/39046
- https://akka.io/blog/langchain-alternatives

**Survival niche**: 大型企业有 100+ integration 的场景、需要 LangSmith 可观测性。LangChain 本身没死，但 "只会用 LangChain" 的 dev 已不抢手。

---

### 4. Pure ML Engineer（无 LLM / agent 经验）

**Peak**: 2020-2023。

**Current status**: Stagnant。Medium 报告 *AI Companies Stopped Hiring ML Engineers Last Quarter* 用 73 家 AI-first 公司数据：Q2 2024 有 1,247 个 ML Engineer 岗，Q3 2024 跌到 413（-67%）。一般 software hiring 也降，但 LLM / Agent / AI Engineer 头衔在涨——岗位结构在 reshape。

**What replaced it**: 不是被取代，是被 rebrand：现在叫 AI Engineer / LLM Engineer / Applied AI Engineer，要求里多了 RAG / agent / eval / prompt 这些。

**Evidence URLs**:
- https://medium.com/@coders.stop/nobody-noticed-but-ai-companies-stopped-hiring-ml-engineers-last-quarter-10cfa08e11dd
- https://www.secondtalent.com/resources/most-in-demand-ai-engineering-skills-and-salary-ranges/

**Survival niche**: 传统行业（金融风控、广告、推荐系统）+ MLOps + 大规模训练 infra（这些 LLM-only 工程师反而不会）。

---

### 5. Data labeling / annotation 操作员

**Peak**: 2018-2024。Scale AI 估值一路冲到 $29B。

**Current status**: 急剧塌方。TechCrunch 2025-07-16：Scale AI 裁员 14%（约 200 人）+ 解约 500 全球承包商，主要是 data-labeling 这块。CEO 直接说 "scaled the core data-labeling business too quickly"。客户大流失：Google（原计划 $200M 合同）减少、OpenAI / xAI 也暂停。

**What replaced it**:
- **Synthetic data**（LLM 自己生成 + filter）
- **LLM self-labeling**（用 GPT-4 给数据打标比人快 100×、便宜 20×）
- **Mercor 模式**——Scale AI 的对手 Mercor 估值冲到 $10B（CNBC 2025-10），专做 expert labeler（医生、律师、PhD），而不是众包标 cat/dog

**Evidence URLs**:
- https://techcrunch.com/2025/07/16/scale-ai-lays-off-14-of-staff-largely-in-data-labeling-business/
- https://www.cnbc.com/2025/10/27/ai-hiring-startup-mercor-funding.html

**Survival niche**: Expert labeling（医学影像、法律推理、Code）、Physical AI / robotics 视频标注（Scale AI 自己 pivot 方向）、安全相关的 RLHF。低端 crowdsource 已死透。

---

### 6. SEO content writer / 低端 copywriter

**Peak**: 2010-2022。

**Current status**: 塌方式替代。Bloodinthemachine 长篇报道 *Copywriters reveal how AI has decimated their industry*；BlueFocus（中国营销大厂）2023-04 全裁人类 content writer + 设计；某 audio 公司 2024-07 砍 200 个 writer。Washington Post 2023 跟踪一群被 ChatGPT 取代的 writer，最后转去做遛狗、HVAC 维修。

**What replaced it**: GPT-4 / Claude 直接出稿；Writesonic、Jasper 等 SaaS 工具；Google AI Overviews 也减少了 SEO 流量本身。

**Evidence URLs**:
- https://www.bloodinthemachine.com/p/i-was-forced-to-use-ai-until-the
- https://www.washingtonpost.com/technology/2023/06/02/ai-taking-jobs/
- https://tech.co/news/companies-replace-workers-with-ai

**Survival niche**: 高质量 long-form / 调查报道 / 品牌 voice 强的 copy；技术性 doc writing（API、合规、医学）。

---

### 7. Basic-tier 客服 agent

**Peak**: 2022-2024。

**Current status**: 部分替代但有回潮。Klarna 2024-02 高调宣布 AI 处理 2/3 客服对话、声称 "等于 700 个全职人力"，2024 全年预计省 $40M。**但 2025 年回滚**——CEO Siemiatkowski 公开承认 "走得太远，质量下降"，重新招人，采用 "Uber 式弹性客服" 混合模式。Five9 2024-10 调查：75% 消费者仍偏好和人说话。

**What replaced it**: Chatbot（部分），但满意度天花板压制了完全替代。

**Evidence URLs**:
- https://tech.co/news/klarna-reverses-ai-overhaul
- https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/

**Survival niche**: 复杂咨询、医疗保险/金融纠纷、高价值客户专属。"basic tier" Tier 1 仍在被切。

---

### 8. 普通翻译员

**Peak**: 2010s。

**Current status**: 价格塌方。DeepL 2025 自己裁员 25%（约 250 人）—— 这是 *AI 翻译公司* 都受到 *通用 LLM* 冲击的标志，说明 commoditization 跨级冲击。UK 2025 调查：84% 译者预期需求下降；法国 ADAGP/SGDL：79% 认为 AI 是替代威胁。市场报价从 80 cents/line 压到 60 cents。

**What replaced it**: GPT-4 / Claude 3.5（Lokalise 2025 盲测：Claude 3.5 翻译评 "good" 频次高于 GPT-4 / DeepL / Google Translate）。

**Evidence URLs**:
- https://startupfortune.com/deepls-25-percent-staff-cut-is-europes-ai-translation-leader-adapting-to-generalist-model-pressure/
- https://www.resultsense.com/news/2026-05-08-europe-translators-ai-deepl/

**Survival niche**: 文学翻译、法律 / 医疗 / 合同的 sworn translator（法律追责）、本地化 + 文化适配（不只是翻字）。

---

### 9. Traditional NLP engineer（无 transformer 经验）

**Peak**: 2010-2019。SVM、CRF、word2vec、LDA、TF-IDF 时代。

**Current status**: 路径性淘汰——技能被 transformer 全面 absorb。但讽刺的是 "NLP Engineer" 头衔本身在涨，是因为 *NLP* 这个词被 *transformer / LLM* 借用了。LinkedIn 把 NLP Engineer 列为 fastest-growing #5 role，但要求里全是 BERT / GPT / T5。

**What replaced it**: Transformer 一统天下。pre-LLM 的 SVM/CRF/word2vec 路线在工业界几乎归零。

**Evidence URLs**:
- https://blog.promptlayer.com/ai-prompt-engineering-jobs-in-2025-skills-salaries-future-outlook/
- https://www.secondtalent.com/resources/most-in-demand-ai-engineering-skills-and-salary-ranges/

**Survival niche**: 极少数：低资源语言、嵌入式设备无 GPU 场景、可解释性研究。

---

### 10. Classic CV engineer（CNN-only）

**Peak**: 2015-2022。

**Current status**: Niche 仍存活但不增长。Vision Transformer (ViT) + multimodal LLM（GPT-4V / Claude / Gemini）抢走了高端市场。但 NVIDIA / Viso.ai 的 2025 trend 报告反复强调：**CNN 在 edge / 实时 / 数据少场景仍是主力**——ViT 数据饥渴、计算重。

**What replaced it**: ViT（高精度场景）、multimodal LLM（通用 image understanding）。但 YOLO / EfficientNet 在自动驾驶、工业检测、医疗 imaging 的 deployment 还是 CNN。

**Evidence URLs**:
- https://viso.ai/deep-learning/computer-vision-trends-2025/
- https://imagevision.ai/blog/inside-the-latest-computer-vision-models-in-2025/

**Survival niche**: Real-time edge 推理、autonomous vehicle perception、工业 inspection、医疗影像。**CNN 不会死，但"只会 CNN 不懂 ViT/multimodal"的 CV 工程师议价能力下降。**

---

### 11. AutoML SaaS / 大规模超参网格搜索

**Peak**: 2018-2023（DataRobot、H2O.ai 都冲过独角兽）。

**Current status**: 商品化为开源 library。Optuna、Ray Tune、AutoGluon（AWS）+ Bayesian optimization 已成默认。纯 AutoML SaaS 没再出新独角兽，DataRobot 估值过山车。Foundation model + few-shot 让很多原本需要 AutoML 的 tabular task 直接靠 GPT-4 + 提示工程解决。

**What replaced it**: Open-source HPO lib（Optuna 等）+ foundation model 的 few-shot 能力 + AutoGluon 这类 free framework。

**Evidence URLs**:
- https://geniusee.com/single-blog/automl-frameworks
- https://auto.gluon.ai/dev/tutorials/multimodal/advanced_topics/hyperparameter_optimization.html

**Survival niche**: 严肃 tabular ML（金融、电信、医疗保险）—— LLM 在这些场景做 tabular prediction 仍不如 XGBoost+HPO。

---

## Survival Niches — Dying skill 还能活的几片土壤

跨这 11 项归纳，"dying" skill 的常见 survival pattern：

1. **High-stakes / 法律追责场景** —— sworn translator、医疗 labeling、金融 ML
2. **Edge / cost-constrained** —— CNN 在嵌入式、naive RAG 在小项目
3. **Domain-fused** —— "AI + 医学"、"AI + 法律"、"AI + 制造"，单纯 AI 技能塌价，但 + domain 后议价回升
4. **数据稀缺 / 隐私敏感** —— LLM 进不去的领域，传统 ML 仍是首选
5. **Real-time low-latency** —— LLM 还是慢，CNN / 经典 NLP pipeline 在 sub-100ms 场景仍有位置

**通用 takeaway**：commoditization 杀的是"通用版本"，留活的是"特化版本"。

---

## Predictions: Skills Likely to Commoditize in 12-24 mo (2026-05 → 2028-05)

基于上述 pattern + WEF Future of Jobs 2025（39% skill 预计 2030 年前过时）+ 业内 analyst 信号：

1. **Vanilla agentic 框架编码（LangGraph / CrewAI / AutoGen 三选一）** —— 现在是 hot skill，会重演 LangChain 之路。理由：抽象层会被更上层的 "Agent SDK by Anthropic / OpenAI" 取代（OpenAI 已发 Agents SDK）。

2. **手工 RAG + reranker tuning** —— Anthropic Contextual Retrieval、Cohere Rerank v4、Voyage 等已把这块自动化。

3. **Fine-tuning specialist（LoRA / QLoRA 手工调）** —— 模型自带 fine-tuning API + Constitutional AI / RLAIF 让定制门槛降低；很多场景 fine-tune 都不如直接换更强 base model。

4. **基础 ML Ops（部署 model server、写 inference API）** —— Modal / Replicate / Together / Anyscale 这类 inference SaaS 把这层包起来；"手搭 Triton + K8s" 的 niche 化。

5. **Junior-level data scientist 做 dashboard / EDA** —— Claude / GPT 直接接 BigQuery + Plotly 出图，业务方自助。BLS 2025 已点名 admin/clerical 是最高 displacement 类。

6. **第一波 multimodal labeling**（image caption、basic OCR labeling）—— GPT-4V / Gemini 已能自动出高质量 caption；众包 multimodal 标注会重走文本 labeling 的塌方路径。

7. **基础 vector DB 选型 / 调优**（Pinecone / Weaviate / Qdrant 选哪个）—— 长上下文 + agentic 让向量库变成 commodity infra，类似选 PostgreSQL vs MySQL，不再是 differentiator。

**反向预测——这些"看起来该死却不会死"**：
- Eval / 测试设计（反而越来越值钱）
- LLM safety / red-teaming
- AI + domain expert（医学、法律、金融）
- 高级 MLOps（多模型路由、cost optimization、可观测性）

---

## Sources

### Prompt Engineering
- Fortune (2025-05-07): https://fortune.com/2025/05/07/prompt-engineering-200k-six-figure-role-now-obsolete-thanks-to-ai/
- Salesforce Ben (2025): https://www.salesforceben.com/prompt-engineering-jobs-are-obsolete-in-2025-heres-why/
- Fast Company: https://www.fastcompany.com/91327911/prompt-engineering-going-extinct
- MentorCruise: https://mentorcruise.com/blog/how-to-become-an-ai-prompt-engineer-without-chasing-a-dying-job-title/

### RAG vs Long Context
- Dataiku Blog: https://blog.dataiku.com/is-rag-obsolete
- LlamaIndex (Agentic Retrieval): https://www.llamaindex.ai/blog/rag-is-dead-long-live-agentic-retrieval
- LightOn: https://lighton.ai/lighton-blogs/rag-is-dead-long-live-rag-retrieval-in-the-age-of-agents
- RAGFlow 2025 review: https://ragflow.io/blog/rag-review-2025-from-rag-to-context
- AkitaOnRails: https://akitaonrails.com/en/2026/04/06/rag-is-dead-long-context/

### Scale AI / Data Labeling
- TechCrunch (2025-07-16): https://techcrunch.com/2025/07/16/scale-ai-lays-off-14-of-staff-largely-in-data-labeling-business/
- CNBC (Mercor): https://www.cnbc.com/2025/10/27/ai-hiring-startup-mercor-funding.html
- Sacra (Scale AI): https://sacra.com/c/scale-ai/

### LangChain Decline
- HackerNews: https://news.ycombinator.com/item?id=40739982
- Latenode community: https://community.latenode.com/t/why-im-avoiding-langchain-in-2025/39046
- Akka.io alternatives list: https://akka.io/blog/langchain-alternatives
- Medium / Hernandez: https://medium.com/@jhoansfuentes1999/the-decline-of-langchain-why-are-developers-abandoning-this-tool-a6f981566e03

### SEO / Copywriter
- Blood in the Machine: https://www.bloodinthemachine.com/p/i-was-forced-to-use-ai-until-the
- Washington Post (2023-06): https://www.washingtonpost.com/technology/2023/06/02/ai-taking-jobs/
- Tech.co companies-replace list: https://tech.co/news/companies-replace-workers-with-ai

### Customer Support / Klarna
- Tech.co (Klarna reverse): https://tech.co/news/klarna-reverses-ai-overhaul
- CX Dive: https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/
- CBS News: https://www.cbsnews.com/news/klarna-ceo-ai-chatbot-replacing-workers-sebastian-siemiatkowski/

### Translation / DeepL
- StartupFortune (DeepL 25% cut): https://startupfortune.com/deepls-25-percent-staff-cut-is-europes-ai-translation-leader-adapting-to-generalist-model-pressure/
- ResultSense: https://www.resultsense.com/news/2026-05-08-europe-translators-ai-deepl/
- Lokalise blind study: https://lokalise.com/blog/what-is-the-best-llm-for-translation/

### ML / NLP Engineer Market
- Medium "AI companies stopped hiring ML engineers": https://medium.com/@coders.stop/nobody-noticed-but-ai-companies-stopped-hiring-ml-engineers-last-quarter-10cfa08e11dd
- Second Talent: https://www.secondtalent.com/resources/most-in-demand-ai-engineering-skills-and-salary-ranges/
- 365 Data Science: https://365datascience.com/career-advice/career-guides/machine-learning-engineer-job-outlook-2025/

### Computer Vision
- Viso.ai trends: https://viso.ai/deep-learning/computer-vision-trends-2025/
- ImageVision: https://imagevision.ai/blog/inside-the-latest-computer-vision-models-in-2025/

### Macro Reports
- WEF Future of Jobs 2025 (full PDF): https://reports.weforum.org/docs/WEF_Future_of_Jobs_Report_2025.pdf
- BLS AI Employment Projections: https://www.bls.gov/opub/ted/2025/ai-impacts-in-bls-employment-projections.htm
- BLS occupational case studies: https://www.bls.gov/opub/mlr/2025/article/incorporating-ai-impacts-in-bls-employment-projections.htm
