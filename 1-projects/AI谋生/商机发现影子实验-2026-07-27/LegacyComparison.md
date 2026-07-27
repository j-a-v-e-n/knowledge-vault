# 旧创新闭环候选对照

> 对照原件：`/Users/javencao/ai-architect/innovation/runs/2026-07-27/candidates.json`。  
> 目的：检查旧流程在“网络观察 → 产品候选”之间增加了哪些未经外部验证的主张。不是评判产品技术好坏。

| 旧候选 | 原始信号在观察审计中的性质 | 原件实际支持 | 候选增加的承重主张 | 一夜尺子实际能证明什么 |
|---|---|---|---|---|
| intenttrace | O-006：opinion_or_question | 作者主张 AI reviewer 容易只看 diff、不看 intent。 | 把作者称为明确受痛点影响的日常 coding-agent 用户；推定这一群体已经有规范化预算；把 broader literature 当成需求复现。 | 在自建 fixture 上，词法 requirements-to-diff mapping 能否命中预设 gap；不能证明团队需要或购买。 |
| pitchprint | O-012：usable_observation | 一名收件人每天收到结构相似的 AI outreach，并想可靠阻止。 | 从一个人扩展到“公开邮箱的 developers and indie founders”；用该群体购买邮件服务推定对新过滤工具有预算。 | 在 synthetic fixture 上的分类 precision/recall；不能证明真实邮箱误杀率、采用意愿或付款。 |
| apexlint | O-004：usable_observation | 一名用户遇到 dot-dev apex redirect 连接失败，并定位到 port 80 限制。 | 原文没有量化“burned hours”；候选推定一个持续购买域名、反复遇到问题的细分人群和 recurring spend。 | 静态规则在自建 fixture 上能否匹配预设故障；不能证明问题频率或用户需要独立工具。 |
| tokenwage | O-011：opinion_or_question | 作者做了一次 API 成本与当地最低工资的比较，并好奇其他国家情况。 | 将好奇解释为“明确请求 worldwide product”，再把讨论者定义为分发受众；候选自己承认 monetization 为 nil。 | 固定数据下 CSV 是否可重复；不能证明关注、传播或交易价值。 |
| reprocert | O-013：opinion_or_question | 发帖者询问行业是否需要 deterministic training，并推测监管领域可能在意。 | 把问题改写成“必须向审计者证明训练”的 ML engineers 已存在；受监管行业需求仍是二手推断。 | 对自建 checkpoint fixtures 的差异定位是否正确；不能证明法规要求、工作流采用或预算。 |
| clonewatch | 来自 leader/digest，不属于本批 Observation | 领袖/从业者对大模型吞并 indie app 的观点或焦虑。 | 从观点推定有收入的 indie founders 会为个体化风险 verdict 预付费，并认为该群体预算强。 | 它设计的付费预售本来可能产生外部证据，但实际被旧宪法的一夜代码约束拦截，没有运行。 |
| advisorload | O-030：opinion_or_question | 演讲者称 physician advisors 已接受 AI 将到来，并把 volume 作为主题。 | 从演讲者观察推定医院存在紧急 capacity pain、咨询预算和 calculator signup 意愿；系统自己承认是 SECONDHAND/deaf sector。 | 设计的是 signup probe，不是付款；实际同样因不符合一夜代码信封而未运行。 |

## 发现的共同模式

### 1. “battlefield 字段非空”制造了市场具体性的外观

旧候选都能写出 segment、where_they_live、why_them 和 reach_path，但这些字段主要来自模型补全，而不是额外市场证据。结构完整不能证明内容真实。

### 2. 技术尺子验证了解决方案，不验证问题

五个一夜 CLI 候选的 ruler 都可以严格、确定性地判定，但它们判定的是：工具是否符合自建 fixture。真正承重的市场假设——问题频率、切换行为、预算、信任、采用和付款——没有进入 ruler。

### 3. 更接近市场真值的候选反而被宪法拦截

clonewatch 和 advisorload 至少试图把外部 preorder/signup 作为尺子，却因不是一夜代码判定而与 NORTH-STAR ④冲突。这说明旧系统的优化目标更接近“可在一夜内做成并自测的工件”，而不是“最便宜地验证交易假设”。

### 4. 信号类别被错误地当成同一证据等级

产品自荐、个人问题、行业疑问、领袖观点和媒体文章都能被直接组合成产品候选。新架构需要先做来源角色分类，再决定它能支持哪一种主张。

## 对照结论

旧系统并非没有价值：它很擅长跨领域组合、生成可执行工件和构造严格技术测试。但现有证据不支持把这种能力称为“发现真实需求”。它更准确的定位是：

`基于网络信号的创意与可构建性实验室`。

只有经过独立 Observation、NeedHypothesis 与外部行为状态机后，它才可能成为商机发现系统的下游解决方案模块。
