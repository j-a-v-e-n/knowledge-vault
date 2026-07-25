## Research result: RESEARCH-REFRESH-R7 / RS-01

### 1) Exact queries 与 UTC 检索时间

预注册边界：commit `3a1bbe4565006745fb3c458066e08a4640c31268`，commit 时间换算为 `2026-07-25T15:40:02Z`；预注册文件 SHA-256 为 `db7e630355719e62c4c9ccd5e50d038539327ef8de952a3bf47c9e4894f30d35`。以下检索均发生在其后。

| Query | Exact query | UTC |
|---|---|---|
| Q-A | `site:prisma-statement.org PRISMA 2020 checklist search sources date last searched selection process` | `2026-07-25T15:42:51Z` |
| Q-B | `site:training.cochrane.org/handbook/current/chapter-04 searching selecting studies sensitivity precision search strategy` | `2026-07-25T15:43:01Z` |
| Q-C | `"When to Stop Reviewing in Technology-Assisted Reviews" residual relevant documents` | `2026-07-25T15:43:06Z` |
| Q-D | `"Guidelines for snowballing in systematic literature studies and a replication in software engineering"` | `2026-07-25T15:43:13Z` |
| Q-E | `"Statistical stopping criteria for automated screening in systematic reviews"` | `2026-07-25T15:43:23Z` |
| Q-F（反证） | `systematic review search saturation unreliable stopping rule missed relevant studies counterexample` | `2026-07-25T15:43:42Z` |
| Q-G | `site:reddit.com/r/ChatGPTPro "deep research" sources missed shallow` | `2026-07-25T15:43:47Z` |
| Q-H | `site:news.ycombinator.com/item "deep research" citations sources` | `2026-07-25T15:43:55Z` |

### 2) Sources consulted / 搜索返回结果集合

字段缩写：`I/E`=include/exclude；`O`=official/primary method documentation；`R`=peer-reviewed/preprint research；`U`=practitioner/user experience；`M`=metadata/secondary/index；`X`=题外或无法恢复。相同 upstream cluster 不计为独立支持。所有结果继承对应 query 的检索时间。

#### Q-A — PRISMA

- [PRISMA 2020 Checklist PDF](https://www.prisma-statement.org/s/PRISMA_2020_checklist-ab3g.pdf) — O；`PRISMA-2020`；I；给出来源、查询、筛选等报告字段；官方当前副本，未暴露不可变 revision ID。
- [PRISMA 2020 checklist landing page](https://www.prisma-statement.org/prisma-2020-checklist) — O；`PRISMA-2020`；E；导航页，未增加机制证据；live official page。
- [PRISMA 2020 expanded checklist](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf) — O；`PRISMA-2020`；I；含精确搜索、验证、peer review、自动化与漏检风险字段；官方当前副本，revision ID 未暴露。
- [PRISMA 2020 statement](https://www.prisma-statement.org/prisma-2020) — O；`PRISMA-2020`；E；方法入口，内容被清单和 E&E 覆盖；live official page。
- [PRISMA expanded checklist alternate PDF](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-rp3l.pdf) — O；`PRISMA-2020`；E；同一清单的重复呈现；副本关系未明确。
- [PRISMA-Search](https://www.prisma-statement.org/prisma-search) — O；`PRISMA-S-2021`；I；检索报告专门扩展，列出 search-specific checklist；current official page。
- [PRISMA homepage](https://www.prisma-statement.org/) — O；`PRISMA-2020`；E；导航重复；live page。
- [PRISMA 2020 statement paper](https://www.prisma-statement.org/prisma-2020-statement) — O；`PRISMA-2020`；I；确认 statement paper 与正式发表版本身份；current landing page/VOR links。
- [PRISMA for Abstracts](https://www.prisma-statement.org/abstracts) — O；`PRISMA-ABSTRACTS`；E；摘要报告，不直接回答检索充分性。
- [PRISMA flow diagram](https://www.prisma-statement.org/prisma-2020-flow-diagram) — O；`PRISMA-2020`；I；支持逐阶段记录识别、筛选、排除及理由；current official template。
- [PRISMA home alternate](https://www.prisma-statement.org/home) — O；`PRISMA-2020`；E；首页重复。
- [PRISMA translations](https://www.prisma-statement.org/translations) — O；`PRISMA-2020`；E；只有翻译入口，无新增机制。
- [PRISMA endorsement](https://www.prisma-statement.org/endorsement) — O；`PRISMA-2020`；E；引用与采用度不证明方法有效性。
- [PRISMA-ScR](https://www.prisma-statement.org/scoping) — O；`PRISMA-SCR-2018`；I；提供领域范围映射的报告框架；current official page。
- [PRISMA Explanation & Elaboration](https://www.prisma-statement.org/prisma-2020-explanation-elaboration) — O；`PRISMA-2020`；I；解释清单各项理由与实例；current landing page/VOR link。

#### Q-B — Cochrane

- [Chapter 4: Searching for and selecting studies](https://training.cochrane.org/handbook/current/chapter-04) — O；`COCHRANE-CH4-6.5.1`；I；直接讨论覆盖、停止、验证、web 可复现性与独立筛选；version `6.5.1`，last updated March 2025。
- [Chapter 4 Technical Supplement](https://training.cochrane.org/handbook/current/chapter-04-technical-supplement) — O；`COCHRANE-CH4-6.5.1`；I；补充检索实施细节；current supplement。
- [Versions and changes to the Handbook](https://training.cochrane.org/versions-and-changes-handbook) — O；`COCHRANE-HANDBOOK-VERSIONS`；I；用于核对修订状态；current change log。
- [Chapter 4 supplement v6.3](https://training.cochrane.org/handbook/current/technical-supplement-chapter-4-searching-and-selecting-studies-v63) — O；`COCHRANE-CH4-6.3`；E；被 current `6.5.1` supersede。
- [Current Handbook](https://training.cochrane.org/handbook/current) — O；`COCHRANE-HANDBOOK`；E；导航重复。
- [Chapter 4 resources appendix](https://training.cochrane.org/handbook/current/chapter-04-appendix-resources) — O；`COCHRANE-CH4-6.5.1`；E；资源目录，搜索返回未给直接支持范围。
- [Chapter 24](https://training.cochrane.org/handbook/current/chapter-24) — O；`COCHRANE-CH24`；E；非随机干预研究专用，当前问题不依赖该边界。
- [Handbook landing page](https://training.cochrane.org/handbook) — O；`COCHRANE-HANDBOOK`；E；导航重复。
- [Part 2: Core methods](https://training.cochrane.org/handbook/current/part-2) — O；`COCHRANE-HANDBOOK`；E；目录页。
- [Diagnostic Test Accuracy Handbook](https://training.cochrane.org/handbook-diagnostic-test-accuracy/current) — O；`COCHRANE-DTA`；E；不同 review 类型。
- [Chapter 16: Equity and specific populations](https://training.cochrane.org/handbook/current/chapter-16) — O；`COCHRANE-CH16`；E；人口专题，不直接回答停止规则。
- [Chapter V: Overviews of Reviews](https://training.cochrane.org/handbook/current/chapter-v) — O；`COCHRANE-OVERVIEWS`；E；综述之综述专用。
- [Chapter 2: Determining scope and questions](https://training.cochrane.org/handbook/current/chapter-02) — O；`COCHRANE-CH2-6.5.1`；I；支持问题/范围变化应触发搜索策略重审；current version。

#### Q-C — TAR residual-document stopping

- [Li & Kanoulas: When to Stop Reviewing in TAR](https://dare.uva.nl/search?identifier=0ce12a76-0580-48c2-9444-15c7141534d8) — R；`LI-KANOULAS-2020`；I；机构库含摘要、DOI、发表身份和残余文档估计机制；VOR 2020 institutional copy。
- [ResearchGate copy](https://www.researchgate.net/publication/347577862_When_to_Stop_Reviewing_in_Technology-Assisted_Reviews_Sampling_from_an_Adaptive_Distribution_to_Estimate_Residual_Relevant_Documents) — M；`LI-KANOULAS-2020`；E；同一上游重复且 revision 权威性较弱。
- [DBLP record](https://dblp.org/rec/journals/tois/LiK20) — M；`LI-KANOULAS-2020`；E；只增元数据，不增机制证据。
- [IR Anthology record](https://ir.webis.de/anthology/2020.tois_journal-ir0anthology0volumeA38A4.9/) — M；`LI-KANOULAS-2020`；E；同一 DOI 元数据重复。
- [DBLP mirror](https://dblp.uni-trier.de/rec/journals/tois/LiK20.html) — M；`LI-KANOULAS-2020`；E；DBLP 镜像重复。
- [TOIS volume index](https://dblp.org/db/journals/tois/tois38.html) — M；`LI-KANOULAS-2020`；E；期刊索引。
- [IRLab publications](https://irlab.science.uva.nl/publications/) — M；`LI-KANOULAS-2020`；E；作者组发表目录。
- [Kudos summary](https://www.growkudos.com/publications/10.1145%25252F3411755/reader) — M；`LI-KANOULAS-2020`；E；二手摘要。
- [ALTARS 2026](https://www.researchgate.net/publication/405426214_Augmented_Intelligence_in_Technology-Assisted_Review_Systems_ALTARS_2026) — R；`ALTARS-2026`；E；结果仅引用目标论文，未提供新的精确停止证据。
- [Heuristic Stopping Rules for TAR](https://www.researchgate.net/publication/352558905_Heuristic_Stopping_Rules_For_Technology-Assisted_Review) — R；`TAR-HEURISTIC-2021`；I；独立的 heuristic stopping 候选；conference paper，revision 未核实。
- [Using Chao’s Estimator](https://www.alphaxiv.org/abs/2404.01176v1) — R；`CHAO-STOP-2024`；I；估计总体相关文档数与 expected recall；preprint v1。
- [Dan Li DBLP author page](https://dblp.uni-trier.de/pid/48/4185-15.html) — M；`LI-KANOULAS-2020`；E；作者索引。
- [Improved risk minimization algorithms](https://openportal.isti.cnr.it/data/2023/481846/2023_481846.published.pdf) — R；`TAR-RISKMIN-2023`；E；结果只显示引用目标，不直接回答停止充分性。
- [Query Variation slides](https://sciforum.net/manuscripts/12084/slides.pdf) — R；`TAR-QUERYVAR`；E；幻灯片只引用目标论文。
- [Point-process stopping methods](https://eprints.whiterose.ac.uk/id/eprint/205161/1/main.pdf) — R；`TAR-POINT-PROCESS`；I；独立停止方法候选；repository copy，revision 未暴露。
- [Vulnerabilities in Discovery Tech](https://law.stanford.edu/wp-content/uploads/2021/11/Vulnerabilities-in-Discovery-Tech-2022.pdf) — R；`DISCOVERY-VULN-2022`；I；提供法律发现技术失效的反证入口；published PDF，revision 未核实。
- [SWAR background PDF](https://www.qub.ac.uk/sites/TheNorthernIrelandNetworkforTrialsMethodologyResearch/FileStore/SWARFileStore/SWAR48%20Sue%20Harnan%2C%20Mark%20Stevenson%2C%20Mark%20Clowes%2C%20Reem%20Bin-Hezam%2C%20Abdullah%20Pandor%20%282024%20JUL%2002%202220%29.pdf) — R；`SWAR48-2024`；E；搜索片段只有目标引用。
- [SIGIR dissertation abstract](https://www.sigir.org/wp-content/uploads/2020/12/p17.pdf) — R；`SIGIR-DISSERTATION`；E；仅引用目标，范围不足。

#### Q-D — Snowballing

- [EPA HERO record: Wohlin 2014](https://hero.epa.gov/reference/6540113/) — R/M；`WOHLIN-2014`；I；提供 DOI、方法、复制研究和结论摘要；fixed 2014 publication metadata。
- [DBLP record](https://dblp.org/rec/conf/ease/Wohlin14) — M；`WOHLIN-2014`；E；元数据重复。
- [ResearchGate copy](https://www.researchgate.net/publication/266658918_Guidelines_for_snowballing_in_systematic_literature_studies_and_a_replication_in_software_engineering) — M；`WOHLIN-2014`；E；同一上游重复。
- [EASE Most Influential Paper page](https://conf.researchr.org/details/ease-2024/ease-2024-most-influential-paper-award/1/Guidelines-for-snowballing-in-systematic-literature-studies-and-a-replication-in-soft) — M；`WOHLIN-2014`；E；奖项不增加机制证据。
- [OUCI record](https://ouci.dntb.gov.ua/en/works/4rzKNPY4/) — M；`WOHLIN-2014`；E；聚合元数据。
- [EASE 2014 index](https://dblp.org/db/conf/ease/ease2014.html) — M；`WOHLIN-2014`；E；会议索引。
- [Bibbase record](https://bibbase.org/network/publication/wohlin-guidelinesforsnowballinginsystematicliteraturestudiesandareplicationinsoftwareengineering-2014) — M；`WOHLIN-2014`；E；摘要/元数据重复。
- [Mining software repositories mapping study](https://www.sciencedirect.com/science/article/pii/S0950584925000163) — X；`MINING-ARCH-2025`；E；仅引用 Wohlin，主题不同。
- [CiNii record](https://cir.nii.ac.jp/crid/1364233268589473792) — M；`WOHLIN-2014`；E；元数据重复。
- [SciSpace copy](https://scispace.com/papers/guidelines-for-snowballing-in-systematic-literature-studies-106rgo5oni) — M；`WOHLIN-2014`；E；聚合副本。
- [OpenAIRE monitor](https://oamonitor.ireland.openaire.eu/rfo/sfi_rfo/search/publication?pid=10.1145%2F2601248.2601268) — M；`WOHLIN-2014`；E；DOI 元数据重复。
- [Reliability of mapping studies](https://www.sciencedirect.com/science/article/pii/S0164121213001234) — R；`MAPPING-RELIABILITY-2013`；E；搜索片段未提供直接停止或覆盖结论。
- [Author-hosted Wohlin PDF](https://www.wohlin.eu/ease14.pdf) — R；`WOHLIN-2014`；I；原作者全文入口，可支持精确范围；2014 paper copy。
- [SLR Protocol PDF](https://research.wu.ac.at/ws/portalfiles/portal/68013011/SLR_Protocol.pdf) — X；`SLR-PROTOCOL`；E；只引用 Wohlin。
- [UU journal PDF](https://dspace.library.uu.nl/bitstream/1874/410076/1/pdf.aspx.pdf) — X；`OTHER-JOURNAL`；E；只出现参考文献。
- [INOMaR paper](https://www.europeanproceedings.com/pdf/article/10.15405/epsbs.2024.05.40) — X；`INOMAR-2024`；E；只出现引用。
- [RE4DSS preprint](https://upcommons.upc.edu/bitstream/handle/2117/89442/RE4DSS_revised%20document%202.3_PREPRINT-1.pdf) — X；`RE4DSS`；E；只出现引用。
- [UFMG dissertation](https://repositorio.ufmg.br/bitstream/1843/53287/1/Disserta%C3%A7%C3%A3o_Daniel%20Ezequiel.pdf) — X；`UFMG-DISSERTATION`；E；只出现引用。

#### Q-E — Statistical stopping criteria

- [PubMed record](https://pubmed.ncbi.nlm.nih.gov/33248464/) — R；`CALLAGHAN-2020`；I；摘要给出统计停止、recall 与实验结果；VOR metadata, 2020-11-28。
- [Springer version of record](https://link.springer.com/article/10.1186/s13643-020-01521-4) — R；`CALLAGHAN-2020`；I；正式全文及复现仓库入口；VOR。
- [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/7700715/) — R；`CALLAGHAN-2020`；I；开放全文 manifestation；本轮打开时遭 reCAPTCHA，revision 跟随 VOR。
- [ResearchGate copy](https://www.researchgate.net/publication/346540695_Statistical_stopping_criteria_for_automated_screening_in_systematic_reviews) — M；`CALLAGHAN-2020`；E；重复副本。
- [Information for Practice](https://ifp.nyu.edu/2020/meta-analyses-systematic-reviews/s13643-020-01521-4/) — M；`CALLAGHAN-2020`；E；二手索引。
- [PIK overview](https://publications.pik-potsdam.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_25190) — M；`CALLAGHAN-2020`；E；机构元数据重复。
- [PIK full page](https://publications.pik-potsdam.de/pubman/faces/ViewItemFullPage.jsp?itemId=item_25190_4) — M；`CALLAGHAN-2020`；E；同一机构记录重复。
- [PIK overview variant](https://publications.pik-potsdam.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_25190_5) — M；`CALLAGHAN-2020`；E；重复 variant。
- [PIK overview variant 2](https://publications.pik-potsdam.de/pubman/faces/ViewItemOverviewPage.jsp?itemId=item_25190_4) — M；`CALLAGHAN-2020`；E；重复 variant。
- [PIK institutional full text](https://publications.pik-potsdam.de/rest/items/item_25190_7/component/file_25191/content) — R；`CALLAGHAN-2020`；I；机构全文 manifestation，不增加独立 cluster；VOR copy。
- [IBOOK mirror](https://ibook.pub/statistical-stopping-criteria-for-automated-screening-in-systematic-reviews.html) — X；`CALLAGHAN-2020`；E；来源身份与版本不可核对。
- [Springer proxy](https://springerlink.fh-diploma.de/article/10.1186/s13643-020-01521-4) — M；`CALLAGHAN-2020`；E；VOR proxy duplicate。
- [Robust Statistical Stopping Criteria preprint](https://www.researchgate.net/publication/340195082_Robust_Statistical_Stopping_Criteria_for_Automated_Screening_in_Systematic_Reviews) — R；`CALLAGHAN-PREPRINT`；E；被 2020 VOR supersede。
- [PIK file variant](https://publications.pik-potsdam.de/rest/items/item_25190_1/component/file_25191/content) — M；`CALLAGHAN-2020`；E；同一全文重复。
- [PLOS registered-report protocol](https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0326521&type=printable) — R；`AI-SR-PROTOCOL`；E；只引用停止研究，未提供该 claim 的独立结果。

#### Q-F — 反证与漏检

- [Callaghan PubMed](https://pubmed.ncbi.nlm.nih.gov/33248464/) — R；`CALLAGHAN-2020`；E；Q-E 重复。
- [Callaghan PMC](https://pmc.ncbi.nlm.nih.gov/articles/7700715/) — R；`CALLAGHAN-2020`；E；Q-E 重复。
- [Don’t Stop Me Now: stopping-method evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12825451/) — R；`STOP-EVAL-2025`；I；比较多种 statistical/heuristic stopping 方法及安全失效条件；PMC copy，全文抓取遭 reCAPTCHA。
- [Cochrane Chapter 4 current](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04) — O；`COCHRANE-CH4-6.5.1`；I；直接承认数据库漏检、停止困难和已知文献过拟合；current version。
- [Defining and Reporting Saturation](https://journals.aom.org/doi/full/10.5465/AMPROC.2024.325bp) — R；`SATURATION-AOM-2024`；I；指出 saturation 定义与报告含糊会影响可信度；conference proceeding，revision 未核实。
- [Searching for qualitative research](https://pmc.ncbi.nlm.nih.gov/articles/PMC4855695/) — R；`QUAL-SEARCH-2016`；I；呈现“全召回”与“目的性取样到饱和”两类方法；VOR/PMC。
- [Falsely excluded studies systematic review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9644550/) — R；`FALSE-EXCLUSION-2022`；I；提供筛选漏排及补充方法恢复的经验结果；VOR/PMC，全文抓取遭 reCAPTCHA。
- [Confidence-Based Stopping Methods](https://arxiv.org/abs/2606.15380) — R；`CONFIDENCE-STOP-2026`；I；以决策信息充分性而非文档全召回为目标；preprint，版本未进一步核实。
- [Capture-mark-recapture stopping rule](https://pubmed.ncbi.nlm.nih.gov/18722088/) — R；`CMR-STOP-2009`；I；估计未发现文献总体的候选方法；VOR metadata。
- [AI and Automation in Evidence Synthesis](https://onlinelibrary.wiley.com/doi/10.1002/cesm.70046) — R；`AI-EVIDENCE-SYNTHESIS-2025`；I；调查实际综述采用的自动化与停止方法；VOR。
- [Cochrane Training mirror](https://training.cochrane.org/handbook/current/chapter-04) — O；`COCHRANE-CH4-6.5.1`；E；同一 current chapter 重复。
- [RTI false-exclusion page](https://www.rti.org/publication/characteristics-recovery-methods-studies-falsely-excluded-literature-screening-systematic-review) — M；`FALSE-EXCLUSION-2022`；E；机构摘要重复。
- [Springer false-exclusion VOR](https://link.springer.com/article/10.1186/s13643-022-02109-w) — R；`FALSE-EXCLUSION-2022`；E；已纳入 PMC manifestation，不另计 cluster。
- [Generic Systematic Reviews PDF](https://dspace.library.uu.nl/bitstream/handle/1874/459755/s13643-024-02699-7.pdf?isAllowed=y&sequence=1) — R；`ROBUST-STOP-UNKNOWN`；E；搜索结果未恢复清晰 title/version。
- [Generic BMC PDF](https://systematicreviewsjournal.biomedcentral.com/counter/pdf/10.1186/s13643-023-02334-x.pdf) — R；`BMC-SCREENING-UNKNOWN`；E；搜索结果不足以恢复精确主张与版本。
- [Guide of Systematic Reviews in Social Sciences](https://fcsalud.ua.es/en/portal-de-investigacion/documentos/tools-for-the-bibliographic-research/guide-of-systematic-reviews-in-social-sciences.pdf) — O/M；`SOCIAL-SR-GUIDE`；I；直接讨论没有统一 hard stopping rule；旧版方法指南，revision 未暴露。
- [Computer-assisted screening requires robust stopping criteria](https://discovery.ucl.ac.uk/id/eprint/10200806/1/Computer-assisted%20screening%20in%20systematic%20evidence%20synthesis%20requires%20robust%20and%20well-evaluated%20stopping%20criteria.pdf) — R；`ROBUST-STOP-2025`；I；强调停止风险须按数据与问题情境评价；repository publication copy。
- [Generic Systematic Reviews PDF mirror](https://dbc.library.uu.nl/bitstream/handle/1874/459755/s13643-024-02699-7.pdf?isAllowed=y&sequence=1) — M；`ROBUST-STOP-UNKNOWN`；E；前述 unresolved PDF 的镜像。
- [Chao estimator arXiv](https://arxiv.org/abs/2404.01176) — R；`CHAO-STOP-2024`；E；Q-C 同一上游重复。
- [Can ChatGPT Write a Good Boolean Query?](https://arxiv.org/abs/2302.03495) — R；`CHATGPT-BOOLEAN-2023`；I；直接测试 AI 查询生成与漏检/成本风险；preprint。
- [Search Strategy Formulation](https://arxiv.org/abs/2112.09424) — R；`SEARCH-FORMULATION-2021`；I；提出透明、可解释和可复现的搜索工具设计原则；preprint。

#### Q-G — Reddit 用户经验

以下纳入项仅作为失效假设/体验证据，不支持产品内部机制或发生率。

- [Anyone use deep research with pro?](https://www.reddit.com/r/ChatGPTPro/comments/1v4uf0j/anyone_use_deep_research_with_pro/) — U；`REDDIT-1v4uf0j`；I；用户报告搜索量、引用和长度变化；live mutable thread，身份/配置未核验。
- [Why deep research is so shallow now?](https://www.reddit.com/r/ChatGPTPro/comments/1q4go5u/why_deep_research_is_so_shallow_now_what_am_i/) — U；`REDDIT-1q4go5u`；I；浅层停止体验；mutable anonymous report。
- [Deep Research for blog posts](https://www.reddit.com/r/ChatGPTPro/comments/1jckuqq) — U；`REDDIT-1jckuqq`；I；用户观察工具可能只聚合少量高排名结果；mutable/promotional risk。
- [Deep Research vs GPT5-Pro](https://www.reddit.com/r/ChatGPTPro/comments/1nw9a48/deep_research_vs_gpt5pro/) — U；`REDDIT-1nw9a48`；I；同用户比较速度、长度和推理深度；未控制实验。
- [Deep Research Tools underwhelming](https://www.reddit.com/r/ChatGPTPro/comments/1jbrxx2/deep_research_tools_am_i_the_only_one/) — U；`REDDIT-1jbrxx2`；I；报告引用无法支持关键连接；mutable anonymous report。
- [GPT Pro Deep Research is dead](https://www.reddit.com/r/ChatGPTPro/comments/1t398n7/gpt_pro_deep_research_is_dead/) — U；`REDDIT-1t398n7`；I；报告忽略 prompt 与选择低垂结果；配置和版本未核验。
- [Fake Citation from Deep Research](https://www.reddit.com/r/ChatGPTPro/comments/1j4hplr/fake_citation_from_deep_research/) — U；`REDDIT-1j4hplr`；I；错引/二手 AI 内容风险体验；mutable。
- [Deep research misconceptions](https://www.reddit.com/r/ChatGPTPro/comments/1ipmqwe) — U；`REDDIT-1ipmqwe`；I；正面工作流解释，但机制属匿名推测，不计机制事实。
- [Deep Research is too much](https://www.reddit.com/r/ChatGPTPro/comments/1smier8/deep_research_is_too_much_and_pro_models_are/) — U；`REDDIT-1smier8`；I；信息量过大导致只浏览、不核验的使用问题；mutable。
- [AI-powered research workflow guide](https://www.reddit.com/r/ChatGPTPro/comments/1in87ic/mastering_aipowered_research_my_guide_to_deep/) — U；`REDDIT-1in87ic`；I；正面 practitioner workflow；可能自我宣传，非对照证据。
- [Best research tool discussion](https://www.reddit.com/r/ChatGPTPro/comments/1iis4wy/deep_research_is_hands_down_the_best_research/) — U；`REDDIT-1iis4wy`；I；同一线程出现正反体验；mutable。
- [Underperforming since GPT-5?](https://www.reddit.com/r/ChatGPTPro/comments/1mys0ck) — U；`REDDIT-1mys0ck`；I；用户报告来源量与深度下降；版本/任务不可复演。
- [AffectionatePiano290 profile](https://us.reddit.com/user/AffectionatePiano290/) — X；`REDDIT-PROFILE`；E；个人主页，不能支持 RS-01。
- [GetEmployed thread](https://np.reddit.com/r/GetEmployed/comments/1qvqsbk/why_am_i_suddenly_not_able_to_even_get_interviews/) — X；`REDDIT-GETEMPLOYED`；E；求职主题，仅偶然出现关键词。
- [Claude usage-limit megathread](https://dd.reddit.com/r/ClaudeAI/comments/1mj0eyf/usage_limits_megathread_discussion_report_july_28/) — X；`REDDIT-CLAUDE-LIMITS`；E；使用额度，不回答研究充分性。
- [GPT search comparison](https://ca.reddit.com/r/singularity/comments/1p9hrd8/gpt51search_is_superior_to_gemini3progrounding/?sort=old) — U；`REDDIT-1p9hrd8`；I；正面报告上传受控来源可节省时间；匿名、无对照。
- [Recruiting thread](https://fr.reddit.com/r/recruiting/comments/1tuizkc/i_interviewed_15_engineers_this_month_and_im/) — X；`REDDIT-RECRUITING`；E；主题无关。
- [ChatGPT at work: Accounting](https://af.reddit.com/r/Accounting/comments/1kglyf4/how_often_do_you_use_chatgpt_on_the_job/?limit=500) — U；`REDDIT-1kglyf4`；I；用户报告引用不支持回答，且把 deep research 当起点；非机制证据。
- [Gemini/NotebookLM thread](https://ns.reddit.com/r/notebooklm/comments/1mje3ub/google_merging_gemini_al_with_notebooklm_research/) — X；`REDDIT-NOTEBOOKLM`；E；产品整合讨论，缺少直接充分性证据。
- [Mamdani thread](https://en.reddit.com/r/thedavidpakmanshow/comments/1upxkqr/mamdani_on_platner_i_believe_its_time_for_him_to/) — X；`REDDIT-POLITICS`；E；关键词偶现。
- [Hair dye experiment](https://np.reddit.com/r/DrWillPowers/comments/1ml6irn/experimental_result_on_dr_powers_hair_dye_hack/) — X；`REDDIT-HAIR`；E；领域无关。
- [RomanceBooks thread](https://us.reddit.com/r/RomanceBooks/comments/1afyf07/do_excellent_mafia_authors_exist/) — X；`REDDIT-ROMANCE`；E；“deep research”仅自然语言。
- [Physical AI thread](https://pt.reddit.com/r/ValueInvesting/comments/1tk8z4a/jensen_said_physical_ai_is_the_next_wave/) — X；`REDDIT-PHYSICAL-AI`；E；无研究方法证据。
- [Small YouTube channel thread](https://th.reddit.com/r/SmallYTChannel/comments/1na1qfp/hi_everyone_im_looking_to_get_started_on_youtube/?sort=new) — X；`REDDIT-YOUTUBE`；E；只有产品建议。

#### Q-H — Hacker News 用户/实践经验

- [Introducing deep research](https://news.ycombinator.com/item?id=42913251) — U；`HN-42913251`；I；同一线程包含事实错配实例与正面效率评价；live mutable discussion。
- [Ask HN: How to Use Deep Research?](https://news.ycombinator.com/item?id=43603574) — U；`HN-43603574`；I；用户报告 blogspam 来源及 source-ranking 困难；mutable anonymous discussion。
- [Reports are no good / starting-point discussion](https://news.ycombinator.com/item?id=43861012) — U；`HN-43861012`；I；同一线程出现浅层批评和“找到罕见文档”正面报告；mutable。
- [OpenAI – Deep Research](https://news.ycombinator.com/item?id=42913235) — U；`HN-42913235`；I；用户讨论 hallucination、authority discrimination 和 calibration；其中官方限制为二手转引。
- [Early positive use case](https://news.ycombinator.com/item?id=42916832) — U；`HN-42916832`；I；单次法律/技术研究正面案例；无独立准确性审计。
- [Employment-regulation comment](https://news.ycombinator.com/item?id=47002109) — U；`HN-47002109`；E；搜索片段被截断，无法恢复具体结果和限制。
- [Local Deep Research discussion](https://news.ycombinator.com/item?id=43330164) — U；`HN-43330164`；I；用户报告把低权威网页表现为科学来源；mutable。
- [Using Deep Research to find citations](https://news.ycombinator.com/item?id=43214438) — U；`HN-43214438`；I；正面 source-discovery workflow；未核验引用质量。
- [Show HN: local filesystem research tool](https://news.ycombinator.com/item?id=45102706) — U；`HN-45102706`；I；维护者明确 citations 尚未实现，说明生成报告不等于可核对；self-report。
- [Differences Between Deep Research tools](https://news.ycombinator.com/item?id=43236184) — U；`HN-43236184`；E；主要是讽刺/推测，无可核对结果。
- [The Deep Research problem](https://news.ycombinator.com/item?id=43133207) — U；`HN-43133207`；I；实践者指出核验 AI 综合结论可能抵消自动化收益；mutable discussion。
- [Claude Integrations comment](https://news.ycombinator.com/item?id=43859536) — U；`HN-43861012-COMMENT`；E；内容与已纳入 HN 线程重复。

### 3) Key findings / 高影响原子 claims

| Claim | 支持精确范围 | Entailment status | Limitations | Decision effect |
|---|---|---|---|---|
| **HC-A：可核对性要求保存问题、纳排、每个来源与日期、完整查询、限制、筛选/自动化流程和排除理由。** | [PRISMA expanded checklist](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf)，pp.1–2，extracted lines 31–105；pp.6，lines 290–304。 | `entailed` | PRISMA 是报告规范，不验证搜索本身已经充分。 | 保留预注册、逐结果筛选、exact-query/time、flow 和 exclusion receipt。 |
| **HC-B：报告完整不蕴含领域完整；开放检索没有由这些来源支持的有限全召回证明。** | PRISMA 定义“应报告什么”；[Cochrane §4.4.10](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)，lines 496–505，明确客观判断完成很困难，估计方法仍需条件。 | `entailed_for_distinction`; “开放网络永不可能完整”则 `not_entailed` | 不能从困难推成绝对不可能；只能说本轮无证明。 | closure 应命名为“时间/威胁模型下 bounded decision sufficiency”，禁止写“domain complete”。 |
| **HC-C：覆盖设计应由问题与 eligibility 驱动，并覆盖不同来源类型；结果数量不是充分性代理。** | [Cochrane §4.3–4.4](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)，lines 131–186、256–261、310–312。 | `entailed_in_systematic-review_domain`; AI 项目迁移为 `inference` | 医疗干预综述的数据库要求不能原样移植到 AI 项目。 | 增加预先冻结的概念覆盖矩阵；source class 只是矩阵一维。 |
| **HC-D：已知关键材料召回可发现浅查询，但只命中已知材料可能是事后过拟合。** | [Cochrane §4.4.10](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)，lines 500–500。 | `entailed` | Sentinel set 不能估计开放网络总 recall。 | 同时设置 frozen sentinel retrieval 与未知来源/新术语 novelty probe；两者均须过。 |
| **HC-E：开放 web 搜索结果受内容、算法、定位和个性化变化影响；应保存实际筛过的集合和停止理由。** | [Cochrane §4.5](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)，lines 527–535；停止建议 lines 497–510。 | `entailed` | 透明记录只能提高可审计性，不能恢复搜索引擎未返回的材料。 | receipt 保存 engine/channel、UTC、exact query、返回 URL、screened set、快照/哈希；不把 estimated total 当 screened total。 |
| **HC-F：在固定、可枚举语料中，可用抽样/总体估计给停止赋予显式 residual-risk 含义。** | [Li & Kanoulas 2020 abstract](https://dare.uva.nl/search?identifier=0ce12a76-0580-48c2-9444-15c7141534d8)；[Callaghan & Müller-Hansen 2020 abstract](https://pubmed.ncbi.nlm.nih.gov/33248464/) 报告按 recall target/confidence 停止，测试数据平均 work reduction 为 `17%`。 | `entailed_for_fixed_collection`; 对开放 web 为 `not_entailed` | 依赖固定文档集、抽样设计、标签质量和数据分布。 | schema 增加 `corpus_type`；只有 `finite_frozen` 可声明估计 recall/confidence。 |
| **HC-G：停止方法可能因 ranking、hyperparameter 或 screening error 而漏掉相关材料。** | [Stopping-method evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12825451/) 的搜索返回摘要称比较 `15` 种方法并定义不安全条件；[false-exclusion review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9644550/) 报告 single-reviewer median missed `5%`、range `0 to 58%`，部分研究 false exclusion 为 `8%`。 | `entailed_for_studied datasets` | 不等于本项目会出现相同发生率；全文抓取受阻，未生成内容哈希。 | 固定语料增加 residual random audit；高影响纳排不能只由同一 AI 单审。 |
| **HC-H：搜索策略 peer review 与独立 eligibility decision 是反自证控制。** | [Cochrane §4.4.8](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)，lines 462–473；§4.6，lines 582–590；[PRISMA](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf)，lines 88–105。 | `entailed_in_source domain`; 项目治理迁移为 `inference` | 独立 reviewer 也会共享语料、模型或偏差；不是密码学独立。 | query plan 在运行前 peer review；高影响 include/exclude 与 claim entailment 由未参与构造者复核。 |
| **HC-I：真实用户同时报告浅层、错引、低权威来源和找到罕见材料；匿名经验不能决定机制 claim。** | [Reddit underwhelmed thread](https://www.reddit.com/r/ChatGPTPro/comments/1jbrxx2/deep_research_tools_am_i_the_only_one/)；[HN mixed-experience thread](https://news.ycombinator.com/item?id=43861012)。 | `observational_only`, `contested` | 自选择、匿名、任务/模型/配置不固定，线程可编辑。 | practitioner class 只用于生成 failure probes、UX burden 和 reopen triggers，不支持算法能力或发生率。 |

#### Verbatim quotes（不超过五条）

> “Present the full search strategies for all databases, registers and websites, including any filters and limits used.”  
> — [PRISMA expanded checklist, lines 70–83](https://www.prisma-statement.org/s/PRISMA_2020_expanded_checklist-yc78.pdf)

> “It is often difficult to decide in a scientific or objective way when a search is complete.”  
> — [Cochrane Chapter 4, line 496](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)

> “current approaches lack robust stopping criteria”  
> — [Callaghan & Müller-Hansen 2020, Abstract](https://pubmed.ncbi.nlm.nih.gov/33248464/)

> “unreliable and cannot be used safely”  
> — [Stopping-method evaluation, search-return scope](https://pmc.ncbi.nlm.nih.gov/articles/PMC12825451/)

> “it is just a starting point … check all the references”  
> — [HN practitioner report](https://news.ycombinator.com/item?id=43861012)

### 4) ⚠️ 矛盾与反证

- **广搜 vs 有界停止：** Cochrane 要求高敏感度、尽可能广泛，但同一章承认搜索完成很难客观判断，并列出 saturation、yield 与统计估计等停止候选。这支持“显式残余风险”，不支持“无限搜索”或“预算到了即充分”。

- **统计停止的可靠性冲突：** [Callaghan 2020](https://pubmed.ncbi.nlm.nih.gov/33248464/) 报告其方法在测试数据上达到可靠 recall；[较新的多方法评价](https://pmc.ncbi.nlm.nih.gov/articles/PMC12825451/) 警告依赖最优 ranking 或调参的方法不安全。方法、数据集与目标不同，不能直接判定哪方普遍正确。

- **数据库与 snowballing：** [Wohlin 2014](https://hero.epa.gov/reference/6540113/) 的软件工程复制研究认为 snowballing 可作为数据库搜索的替代起点；[Cochrane](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04) 在医疗干预综述中要求主题数据库、灰色文献和参考文献检查。差异可能来自领域与 review 目标，不能统一成单一路径。

- **全召回 vs 主题饱和：** [qualitative-search methodological review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4855695/) 明确呈现“找全所有研究”和“目的性取样到主题饱和”两类学派。RS-01 必须先说明追求的是文档 recall、失效类别 coverage，还是 decision sufficiency。

- **用户经验相互冲突：** Reddit/HN 同时存在浅层、错引、来源权威判断差的报告，也存在找到 obscure documents、节省时间的报告。匿名经验不足以消解冲突，只能转化为可复演测试。

### 5) Architecture / decision delta

相对 commit `3a1bbe…` 的冻结基线：

- **保留：** 预注册查询预算、required source classes、逐结果纳排、upstream 去重、反证查询、原子 claim、entailment review、补充轮和 `bounded_incomplete`。本轮没有证据支持降低这些门槛。

- **新增 `research_universe_type`：**
  - `finite_frozen_corpus`：允许声明目标 recall、confidence、估计器和 residual audit。
  - `open_dynamic_web`：只能声明实际渠道、查询、返回集、时间边界和未覆盖风险；不得声明总体 recall。

- **新增 ex-ante coverage matrix：** 至少把“问题/机制或失效类别 × 来源类别 × 支持/反证 × 上游 cluster”冻结。仅满足 official/research/user 三个来源标签仍可能浅层停止。

- **新增 search-quality 双检：** frozen sentinel set 检查是否漏掉已知关键来源；novelty probe 检查查询是否只对已知材料过拟合。

- **加强 stop receipt：** 分开记录：
  - `process_reproducible`
  - `required_cells_covered`
  - `residual_risk_estimated_or_unavailable`
  - `independent_entailment_reviewed`
  - `decision_sufficient_under_declared_scope`
  
  不再用单一 `met=true` 代替这些不同命题。

- **加强反自证边界：** query plan 先由非构造 reviewer 检查；高影响纳排、关键 claim 蕴含和最后 stability probe 不能只由同一个 AI 作者确认。

- **限定 practitioner 证据权限：** Reddit/HN/blog 只能创建 failure hypothesis、用户负担与 reopen trigger；不能支持模型内部机制、准确率或普遍发生率。

- **决策措辞 delta：** 将“可核对的领域充分性”收窄为“在冻结问题、来源矩阵、时间、预算和残余风险下，可复演且足以支持当前决定”；没有证据支持“领域已完整覆盖”。

### 6) 最后一轮稳定性与 gaps

**最后一轮稳定：未证实。当前状态应为 `bounded_incomplete`。**

原因与剩余 gaps：

- required source classes 均有结果，但 Q-F 后的 Q-G/Q-H 只探测 practitioner experience；没有在最后一个方法性 delta 后完成跨 official/research/counterevidence 的独立补充轮。
- 每 topic 的查询预算已经用完；不能事后扩预算制造稳定。继续搜索需要新的预注册续轮。
- 决定性来源尚未生成内容快照及 SHA-256；部分 PMC 全文打开被 reCAPTCHA 阻断。
- entailment 由本轮作者完成，尚无预注册所要求的非作者 reviewer。
- 开放网络没有冻结母集或分母；搜索引擎排序、个性化和未返回结果不可审计。
- 医疗系统综述、法律 TAR、软件工程 snowballing 向 AI 项目研究治理的迁移仍是 inference，缺少同任务实证。
- 预注册的 ordinary-search 与 evidence-governed-search 同任务比较尚未执行。
- practitioner threads 匿名、可变、自选择，不能建立发生率。
- 多个聚合页没有明确 revision/supersession metadata。
- 本轮没有写入或修改任何项目文件。

Suggested next step（lead 接续用）：这份摘要可用于设计 `research_sufficiency receipt`，但若要关闭 RS-01，应另行预注册一个窄范围续轮，补齐内容哈希、跨来源 stability probe、独立 entailment review 和同任务比较，不能直接把本轮改判为通过。

<oai-mem-citation>
<citation_entries>
MEMORY.md:113-113|note=[used evidence-first project preference]
MEMORY.md:159-159|note=[used independent role separation principle]
</citation_entries>
<rollout_ids>
019f83f2-e416-7883-bc44-63190cd9e356
</rollout_ids>
</oai-mem-citation>
