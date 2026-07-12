---
最后更新: 2026-07-12 by campaign-continuous (session 178bffd9)
类型: 实战经验库 · 赢家案例（战役纲领 §2.4）
证据分级: A=多源/含第三方审计 · B=单一可信源或多源自述一致 · C=仅创始人自述 · D=道听途说
诚实声明: 本页无一个案例达"第三方审计"级收入。唯二真正独立确认点已在文中标出，其余全部 founder-self-reported。不为凑数抬评级。
red-team: 已过 fresh-context 独立反证 pass（16 次工具调用，EN+中文），抓出并修正 2 处 mis-cite。
---

# 收入已验证的 solo / 小团队 AI 生意 · 案例库 v1

> **这页对战役有什么用**：commercial rebuild（纲领 §6）要「battlefield-first + demo-first + 只对真实付款信号优化」。下面五条「跨案例复现 ≥3 次」的打法，是从真实赢家身上扒下来、证据分级过的原材料——选品/获客/交付/定价直接可搬。**最重要的横切发现单独拎出来**：验证得最硬的个人收入，常常来自「讲述这门生意」（卖课/社群）而非生意本身——评估任何「AI 赚钱案例」先问一句「他卖不卖课」。

## TL;DR — 5 条可迁移打法（先看这个）

1. **发行即护城河：founder-as-channel（4/4 案例）**。没有一个赢家靠付费投放起家。公开建造过程（build-in-public / SEO 卡位 / 冲榜叙事）本身就是获客系统。
2. **需求考古，不是需求发明（4/4）**。都从「需求已被证明存在的表面」选品：搜索量、平台缺口、小红书内容热度、竞品痛点。选品 = 读现成信号，不是头脑风暴。
3. **第一周就收钱，把付款当验证器（3/4 明确）**。Chatbase 定价页 30 分钟收款、Base44 三周 $1M ARR、陈云飞 ¥1 付费冲榜。**真实付款是唯一不会 Goodhart 的信号——与本项目 §1.5 同构。**
4. **薄壳快上 → 用工程堆叠加深护城河（3/4）**。起点都是基模薄壳（几周上线），护城河后补、且都补在**质量管线**（Postma 数十模型质检栈、Chatbase 长成平台、Base44 batteries-included + repo 为 AI 优化）。
5. **有意识地利用、并分开记账 meta 层飞轮**。受众→产品→受众的飞轮可以正当设计，但「产品收入」和「讲这门生意的收入（课/社群）」的账必须分开——否则你会把卖铲子的钱误当成挖到金子。

---

## Case 1 — Base44 / Maor Shlomo　【A-｜最硬的一个】

**一句话**：AI「vibe-coding」应用生成平台（说需求→生成完整可用 App，自带 DB / auth / 存储 / 邮件）。

**收入 / 交易（已 fetch 源）**
- 2025-06-18 被 Wix **$80M 全现金**收购，成立仅 6 个月，创始人 100% 持股。Wix 向 TechCrunch 确认现金条款与 8 名员工 → 这部分 **[A]**。[TechCrunch](https://techcrunch.com/2025/06/18/6-month-old-solo-owned-vibe-coder-base44-sells-to-wix-for-80m-cash/)
- 2025-05 单月**利润 $189K**（扣 LLM token 成本后）、~25 万用户 → 创始人公开晒的数字，**[B/C]**。（同 TechCrunch 文）
- 上线 3 周 $1M ARR、全程零市场预算 → 自述 **[C]**。[Lenny's Newsletter](https://www.lennysnewsletter.com/p/the-base44-bootstrapped-startup-success-story-maor-shlomo)

**红队注记**：「solo」有水分——准确说是 **solo-owned（独资）**，收购前有 8 名员工，$80M 里 $25M 是员工 retention。[Inc.](https://www.inc.com/ben-sherry/vibe-coding-base44-wix-avishai-abrahami-maor-shlomo/91267959)

**打法**
- **选品**：切 vibe-coding 浪潮，差异化是 **batteries-included**——竞品（Lovable 等）生成前端后还要自己接 DB / 登录，Base44 全内置，非技术用户拿到即用。
- **获客（真护城河）**：LinkedIn / X **build-in-public**——公开写建造过程和利润数字，原文说这比任何付费渠道有效；叠加以色列科技圈 BD（eToro、Similarweb）。
- **交付**：Claude 系 LLM 做代码生成；自述 3 个月没手写一行前端、~90% 代码 AI 生成、**repo 结构专门为「让 AI 好写代码」优化**。
- **定价**：cite 内未披露（诚实留空）。

**可迁移 vs. 特异**：可迁移＝batteries-included 差异化、build-in-public 当发行、AI-native 开发让 8 人干出独角兽苗子的量。特异＝本人资深工程师（前 Explorium 数据负责人）、以色列人脉、踩中 vibe-coding 风口顶点、收购有运气成分。

---

## Case 2 — Chatbase / Yasser Elsaid　【B】

**一句话**：把你的文档 / 网站变成客服 AI chatbot 的平台（RAG-as-a-product → AI 客服平台）。

**收入（已 fetch 源）**
- $9M ARR（2026-04 时点）、30 人、零融资。[solofounders.com](https://solofounders.com/blog/9m-arr-zero-investors-yasser-elsaid-on-bootstrapping-chatbase-as-a-solo-founder)
- $8M ARR / 18 人（11 个工程师）。[ProductLed](https://productled.com/blog/how-chatbase-hit-8m-arr-with-18-people)
- $5M ARR（2025-02，上线两周年）。创始人本人 [LinkedIn 帖](https://www.linkedin.com/posts/yasserelsaid_we-did-it-we-hit-5m-arr-at-chatbase-activity-7302632659757740032-DJCM)（红队核实存在）

**红队注记**：每个数字（$64K MRR→$5M→$8M→$9-10M）**源头都是创始人本人**；solofounders.com 是给 solo founder 唱赞歌的推广型媒体。三年轨迹多源一致、无被驳斥 / 暗中融资的反证，公司真实扩张（Supabase 官方客户案例佐证规模）→ 扎实 [B]，但担不起「verified」三字。

**打法**
- **选品**：ChatGPT 发布**前**就发现「LLM 很强但看不到你的数据」这个缺口（即后来的 RAG），6 周做出「chat with your PDF」，再演进成客服平台。
- **获客**：2023-02-02 向自己**仅 16 个粉丝**发 demo 推文，挂定价页 **30 分钟后收到第一笔 Stripe 付款**；之后 organic content + word-of-mouth（他称之为最被低估的增长杠杆）；$7-8M ARR 才叠加人肉销售；发现 100 个理想客户 98 个在纽约 → 整队从多伦多搬去 NYC。
- **定价**：freemium，**60 秒内让用户到 aha moment，价值一露头立刻要钱**；定价纯靠实验。
- **交付**：RAG over 客户文档，最早用 DaVinci completion 起家。

**可迁移 vs. 特异**：可迁移＝薄壳快上→收钱验证→随平台能力加深护城河、「先到 aha 再立刻收费」、搬到买家聚集地。特异＝踩中 ChatGPT 引爆时点、最早一批 chat-with-your-data（现坑已挤满）。

---

## Case 3 — 陈云飞「小猫补光灯」（中国）　【B-｜含反面成分】

> 评级说明（2026-07-12 独立评审后收紧）：主源 21 财经属「记者转述创始人自述」——有编辑背书、高于纯自述 [C]，但媒体未独立核实数字、低于标准 [B]，故定 [B-]。

**一句话**：不会写代码的前大厂用户研究员，用 Cursor 约 1 小时做出自拍补光 iOS App，付费版冲上中国区付费榜第一。

**收入（已 fetch 源）**
- Pro 版（定价 **¥1**）累计收入**约 ¥30-40 万**、两款 App 各 30-50 万下载、上架 4 小时冲付费榜第一。[21 财经](https://www.21jingji.com/article/20260522/herald/2892ad4a8a5ef09c1ef93d60ae5ba682.html)（记者转述自述）
- 开发过程、1 元冲榜、收入结构（博主商单 + 课程培训 + 企业定制 2-10 万 / 单）。[PingWest 品玩](https://www.pingwest.com/a/300821)

**红队注记**：广传的「年入百万」**不在**上述 cite 里（来自 36kr / 搜狐系，同为自述），本页不采用；¥1 定价下「付费榜第一」日销量门槛很低，冲榜 ≠ 高收入。App 收入是真的，但只是他年收入的**少数部分**——大头是 meta 层（商单 / 课程 / 咨询，见反面案例区）。

**打法**
- **选品**：在**小红书挖真实需求**（女性自拍补光；他公开教「在 Reddit 和小红书找真实用户需求」）——需求已被平台内容验证过，才动手。
- **交付**：非程序员 + Cursor，~1 小时出品；产品极小（一个纯色补光屏），**小到 AI 一次写完**。
- **定价 / 获客**：免费版冲榜攒量 → Pro ¥1 把「付费榜第一」做成传播素材 → 媒体报道（「中国第一个 Cursor 爆款」叙事）反哺个人 IP。

**可迁移 vs. 特异**：可迁移＝「小红书/Reddit 需求考古 → 最小可付费产品 → 榜单/低价当营销」整链成本近零、可批量复现。特异＝「首个 Cursor 出圈」的媒体时刻不可复制；App 收益天花板明显（¥1）。

---

## Case 4 — HeadshotPro / Danny Postma　【C+｜如实降级，方法论价值高、数字弱】

**一句话**：AI 职业头像生成（上传自拍→训练个人模型→出职业照），后转 B2B 团队头像。

**收入（已 fetch 源）**
- 联盟渠道**每月带来（generates）> $50K 收入、占月收入 15%+**。[Rewardful 案例](https://www.rewardful.com/case-studies/headshotpro)（平台方发布，数字仍出自 Postma；反推总收入上限 ≈ $333K/月）
- 广传的「$300K MRR」只能追溯到 **Postma 本人推文**被 Starter Story 等循环转载 → 典型 [C]。本页只背书「月收入量级在数十万美金档、由 Rewardful 侧面约束」这一弱化表述。
- 方法论细节。[Unite.AI 访谈](https://www.unite.ai/danny-postma-founder-of-headshotpro-interview-series/)（无收入数字）

**红队注记（实锤两条）**：① 常见转述「affiliate pays $50K」是错的，原文是 **generates**；② Postma **确实卖课**——SEO 课 24 小时进账 $106K（[startupspells](https://startupspells.com/p/danny-postma-seo-course-106000-revenue-24-hours)），收入结构里有明显 audience / info-product 飞轮。产品是真的、2025-26 无下滑报道，但引用他必须带此注。

**打法**
- **选品**：连环 pivot 追信号——AI 库存图（撞版权，撤）→ ProfilePicture.AI（Twitter 爆但热度衰减）→ 职业头像（**付费场景明确**：求职 / 领英刚需，即刻成功）。
- **获客**：SEO（"profile pictures" 早期卡位）+ Twitter 病毒 + **联盟计划**（Rewardful，贡献 15%+）→ 后期 pivot B2B 团队订单。
- **交付（本次最具体的技术栈）**：Stable Diffusion + DreamBooth（按用户照片训练）+ LLaVA（过滤上传 / NSFW）+ CodeFormer（修脸部 AI 伪影）+ 一年迭代的**数十个自研 / 开源模型堆叠做质检**——护城河在质量管线不在基模。
- **定价**：按次付费（session），非订阅。

**可迁移 vs. 特异**：可迁移＝「付费场景清晰的窄需求 + 开源模型堆叠出质量差距 + 联盟分销」+ pivot-by-signal 的节奏。特异＝先有 Twitter 受众和顶级 SEO 手艺（他就靠这个卖课），冷启动条件普通人不具备。

---

## ANTI-CASES / 挖到的陷阱（负样本同样是资产，§3.4）

1. **Marc Lou（年入 $1.03M, 2025）——「卖铲子」原型**。最大头是 **ShipFast（$20.3K/月，卖给想做独立开发的人的 boilerplate）+ CodeFast（$21.8K/月，编程课）**。[腾讯新闻](https://news.qq.com/rain/a/20260107A07ECX00)（自晒 dashboard）。真实生意是**向淘金者卖铲子**，不是 AI 产品本身赚钱。数字大体可信，但作为「AI 生意能赚钱」的证据是**错位**的。
2. **idoubi / 艾逗笔（前腾讯，一年上线 11 个 AI 产品）——最诚实的负样本**。[虎嗅访谈（BAAI 镜像）](https://hub.baai.ac.cn/view/40653)亲口确认：**主要收入是 200+ 人付费社群**，11 个 AI 产品收入合计远不及上班（2024-12 四款合计才 $1K MRR）；后来真正赚钱的 ShipAny 又是 boilerplate（铲子）。→ 与 Marc Lou 同构。
3. **陈云飞的 meta 层**：App 本身 ¥30-40 万是真的，但年收入大头同样是商单 + 课程 + 咨询——**一半 Case、一半 Anti-case**，引用必须拆开。
4. **中文「AI 副业」内容农场**：CSDN / 知乎大量「月入 3 万+」「13 天赚 48 万」文章全部无源可溯、以引流卖课为目的，一律不采信。
5. **幸存者偏差的直接反证**：[博客园《做 AI 工具出海一个月，我赚到了 0 美元》](https://www.cnblogs.com/shenchuanchao/p/20405690/ai-tool-overseas-zero-dollars-lessons-learned)——照社区打法做、收入为零；其教训（需求验证 >> 开发、避开 AI 写作/摘要/生图红海、第一天想清付费场景）与四个赢家的方法恰好互为镜像。

---

## 诚实结论

达 **[B-] 及以上共 3 个**（Base44 [A-]、Chatbase [B]、陈云飞 [B-]——2026-07-12 独立评审后从 [B] 收紧一档，理由见该案）；HeadshotPro 如实定 [C+]（方法论价值高、数字弱）。**没有为凑数抬评级；两口子搜索井都已挖干**（尾部查询在中英双语都开始循环同一批名字）。

## 附录 · 溯源
- **已 WebFetch 解析成功的引用源（10）**：TechCrunch、Lenny's Newsletter、solofounders.com、ProductLed、Rewardful、Unite.AI、21 财经、PingWest、BAAI（虎嗅镜像）、腾讯新闻。**失败已换源**：知乎（403→PingWest）、虎嗅原站（502→BAAI 镜像）。
- **红队独立 pass**：fresh-context 子代理、16 次工具调用、EN+中文反证搜索；4 案全部 CONFIRMED 或 WEAKER-THAN-STATED、0 案 REFUTED；抓出的 2 处 mis-cite（Rewardful "generates≠pays"、陈云飞「年入百万」无源）已在上文修正。
- **QUERIES-RUN**：英文本体 6 条 + 中文本体 4 条（含 2 条尾井确认井干），完整清单见 session 178bffd9 调研 agent 记录。
