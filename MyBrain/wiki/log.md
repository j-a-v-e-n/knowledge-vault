# Wiki 操作日志

## [2026-04-28] 元规则沉淀 | 经验教训 + AI 团队设计原则

### 操作概览
不是从 raw 编译，是 Javen 主对话产出的 vault 元规则。两份"防摔记忆"文件 + 主 CLAUDE.md 接入。

### 新建文件（2 份元规则）

| 文件 | 类型 | 位置 | 用途 |
|---|---|---|---|
| `system/经验教训.md` | 元方法论（system 类） | `MyBrain/system/` | debug 方法论 6 条 + 5 项 checklist。"同一假设修 3 次失败 → 强制重审 root cause"是核心 |
| `wiki/工程方法/AI 团队设计原则.md` | synthesis | `wiki/工程方法/`（**新子领域**） | 基于 Javen 两条 axiom（AI=员工 / 团队管理是通用学问）+ 业内已验证 framework 调研。**核心立场反直觉：默认 single-agent，multi-agent 只在 Anthropic 三准则全满足时启用** |

### 调研支撑（Multi-agent 设计原则页）
后台 agent 调研 22 个外部源（Anthropic / Cognition / arXiv / ChatDev / DataCamp 等），**精华版 2950 字**。关键发现：
- Anthropic 实测 multi-agent 烧 15× tokens，错误放大 17.2×
- Anthropic + Cognition 都说"先简单"，反 over-engineer
- Lead=Opus + Workers=Sonnet 配置比纯 Opus 单 agent 高 90.2%
- AI Two-Pizza = 3-5 subagent
- DACI 比 RACI 适合 AI 团队
- Skills = Spotify Chapters，Tasks = Squads（vault 已有结构正好对应）

### 顺带补录（daemon 凌晨自动跑产出未及时入 INDEX）
| 文件 | 类型 | 位置 |
|---|---|---|
| [[PHIL28_2026_课程大纲]] | source | `notes/ucsd/Spring 2026/PHIL28/` |
| [[PHIL28_2026_期中考题清单]] | source | `notes/ucsd/Spring 2026/PHIL28/` |
| [[PHIL28_概览]] | overview | `wiki/哲学/`（**新子领域** by daemon） |

### 接入主 CLAUDE.md
在 `MyBrain/CLAUDE.md` 任务看板系统小节末尾加两行 reference：
- "遇到 debug 卡死 → 翻 `system/经验教训.md`"
- "设计任何 AI 系统 / agent / 改 daemon prompt → 翻 `wiki/工程方法/AI 团队设计原则.md`"

意思：以后所有 Claude session（主对话 + daemon）启动时都会自然读到这两条 reference，"防摔记忆"自动生效。

### 决策记录

- **位置选择**：`经验教训.md` 放 `system/` 而非 `wiki/`，因为它是**元规则给 Claude 操作时用**，跟 task-board / system/CLAUDE.md 同性质。`wiki/工程方法/AI 团队设计原则.md` 放 wiki/，因为它是**Javen 自己的方法论思考**，未来可能扩展成"工程方法"知识子领域
- **多源 vs 单源 confidence**：AI 团队设计原则页 confidence: medium。原因：基于 22 个外部权威源 + Javen 个人洞察。框架部分（Anthropic 立场、模型档案、反 pattern）confidence: high；axiom 部分和"给 vault 系统的 10 条 actionable"是 medium（个人洞察 + 推断）
- **不重写已有 INDEX**：本次只 Edit 关键 4 处（最新操作 / 按类型表 / 目录结构图 / 统计），保留其它部分
- **wiki/工程方法/ 子领域开端**：第一篇 = AI 团队设计原则。预期未来扩展：debug 方法论的"高阶版"、工具选型方法论、个人产出系统设计等

### 文件统计变化
| 指标 | 变更前 | 变更后 |
|---|---|---|
| 总页面数 | 50 | **54** |
| overview | 2 | **3** (+PHIL28_概览) |
| source | 34 | **36** (+PHIL28 ×2) |
| synthesis | 1 | **2** (+AI 团队设计原则) |
| wiki 子领域数 | 4 | **6** (+哲学 +工程方法) |

### 待 Javen 确认的后续
1. **PHIL28 子任务 c 还 blocked**：6 个 pptx 课件需要主对话编译（task-003 c），daemon 没 python-pptx
2. **AI 团队设计原则**：用户审阅 + 后续每 6 个月 review 一次（标在文档末尾的"矛盾与未解决问题"小节）
3. **task-006 AI Watch v2 部署**：用户喊"推进 task-006"时启动；本次新建的"AI 团队设计原则"是它的设计指北

---

## [2026-04-27] Ingest | ECE284 两篇新 IMWUT 论文（LemurDx + DopFone）

### 操作概览
按用户指示编译 Javen 下载到 `raw/ucsd/Spring 2026/ECE284/` 的两个新 PDF：

1. `Arakawa_2023_LemurDx.pdf`（原 ACM ID `3596244.pdf`）— Arakawa et al. 2023 IMWUT，Apple Watch 被动感知 + 情境过滤检测儿童 ADHD 多动
2. `Garg_2025_DopFone.pdf`（原 ACM ID `3770671.pdf`）— Garg et al. 2025 IMWUT，智能手机 18 kHz Doppler 测胎心率

第三个下载 `s41598-024-51567-w.pdf`（Mason 2024 TemPredict）经 md5 验证与已有完全相同，已删除 Downloads 重复版本。

### 文件操作
- raw/ 中重命名 `3596244.pdf` → `Arakawa_2023_LemurDx.pdf`（按 vault 命名规范）
- raw/ 中重命名 `3770671.pdf` → `Garg_2025_DopFone.pdf`

### 新文件清单

**新建 source 页（2 个）：**

| 原始文件 | source 页 | 位置 |
|---------|-----------|------|
| Arakawa_2023_LemurDx.pdf | [[Arakawa_2023_LemurDx]] | notes/ucsd/Spring 2026/ECE284/ |
| Garg_2025_DopFone.pdf | [[Garg_2025_DopFone]] | notes/ucsd/Spring 2026/ECE284/ |

### 图片处理（PyMuPDF 2.5× zoom）
- 从 LemurDx PDF 渲染 6 张关键图（pages 1/10/11/13/15/17）→ `attachments/ECE284/`：UI mockup（Fig 1）、原始信号情境对照（Fig 5 — 全文最关键的方法学图）、ML pipeline（Fig 6）、4 种 ML 模型 with/without 情境过滤（Fig 7）、per-day risk score + ROC（Fig 9）、自动 sitting/quiet 检测（Fig 11）
- 从 DopFone PDF 渲染 7 张关键图（pages 8/9/10/12/13/16/18）→ `attachments/ECE284/`：手机贴腹部 3 位置×3 角度（Fig 1）、信号处理 pipeline（Fig 2）、ML 特征 pipeline（Fig 3）、4 方案 CDF + Table 4（Fig 4）、Bland-Altman + 相关图（Fig 5）、4 种混杂因素（Fig 6）、4 款手机频响对照（Fig 7）
- 共 13 张新图

### 更新文件（双向链接整合）
- [[Luo_2026_NormWear]] — 应用方向区新增 LemurDx + DopFone 回链，标注"通用 vs 专用"范式对照
- [[Mason_2024_TemPredict]] — 数字精神健康主题区新增 LemurDx 回链（"长期被动感知 + 心理行为推断"范式同源）
- [[Perez_2019_AppleHeartStudy]] — 关联区新增 LemurDx + DopFone 回链（同 Apple Watch / 同消费设备健康 ML）
- [[Shah_2025_LossOfPulse]] — 关联区新增 LemurDx + DopFone 回链（消费医疗 ML 设计哲学对照）
- [[Zhang_2015_TROIKA]] — 关联区新增 LemurDx + DopFone 回链（PPG vs 加速度 vs Doppler 三种无创心率测量物理原理对照）
- [[Song_2024_SmartphoneMicroscope]] — 关联区新增 DopFone 回链（smartphone-as-medical-device 视觉 vs 主动声学模态）
- [[综合_医疗技术中的种族偏见]] — 新增 DopFone 回链：BMI 33% MAE 升高暗示**身体组成层**作为第三种潜在族群偏差源
- INDEX.md — ECE284 文献笔记新增 2 条；按类型分类表 source 列扩展；目录结构图 ECE284 9 → 11 md；概念导航新增多条；统计 54 → 56 页（source +2）
- gaps.md — 新增 10 条推测性问题（情境过滤推广至自闭症/抑郁/焦虑、LemurDx 自动情境检测增强、LemurDx + TemPredict 多模态融合、VADPRS ground truth 噪声、BMI 自适应 spectrogram、DopFone 跨手机临床验证、DopFone 物理机制推广至肠蠕动/膀胱、多胎源分离 ICA/NMF、DopFone+Paperfuge+m-phone 三件套低资源孕产监护包、LemurDx vs DopFone 架构哲学对照可形式化为 SNR-维度匹配原则）

### 决策记录

- **暂不提取 concept 页**：本次编译让"消费级智能手机 / 可穿戴健康感知"主题积累到 7 个独立来源（LemurDx + DopFone + Bhamla + Song + Perez + Shah + Zhang）——已超过 concept 阈值。**但需要新建 `wiki/医疗技术/` 子目录**，按 CLAUDE.md "新建 wiki 子目录需用户确认"原则——**已在 task-board task-010 副产物中提议，等 Javen 确认后再启动 concept 提取**
- **不建独立 debate 页**：两篇都强调与现有方法的对比但**没有明确对立**（DopFone 与现有 fetal Doppler 是"互补 / 替代"而非"对立"；LemurDx 与现有 ML baseline 是"显著优于"而非"对立结论"）——不符合 debate 页的"两个或多个来源明确对立"标准
- **跨课程 / 跨主题联系**：
  - LemurDx 的"情境过滤"哲学（在合适情境下观察症状特征）与 COGS117 [[Adolph_2018_走路发展15条建议]] 中"情境塑造行为"原则结构相似——但**目前还不成熟为 synthesis 页**，先在 source 页里做 hint 链接
  - DopFone 与 [[综合_医疗技术中的种族偏见]] 在 BMI 子群分析上有自然延伸——已在该综合页加入 DopFone 作为"身体组成层"第三种潜在偏差源，并在 gaps.md 留下未解决的族群子群分析待办
- **"先懂再细"严格执行**：两篇 source 页都按"问题 → 核心结论 → 机制（含类比）→ 证明（图表就近 `>` 引用块解读）→ 鲁棒性 / 临床访谈（DopFone）→ 意味着什么 → 局限 → 技术细节后置"展开
- **类比开路**：
  - LemurDx："车开 100 公里在高速 vs 停车场绕圈，加速度计能看见距离，但只有加上'在哪条路上'才知道是否异常"
  - DopFone："手机不是狙击手对准胎心，而是听诊器贴整间屋子的振动——整个母腹表面在跟着搏动，捕捉的是振动剖面"

### ⚠️ 副产物：发现 vault 内位置错误（lint 待办）

`notes/ucsd/Spring 2026/ECE284/Bhamla_2017_Paperfuge.md` 实际内容是 Apple Heart Study 的演讲稿（`# Apple Heart Study — Speaking Script v2`，218 行）。真正的 Paperfuge source 笔记在 `raw/ucsd/Spring 2026/ECE284/Bhamla_2017_Paperfuge.md`——**违反两条规则**：

1. 演讲稿被错命名为 Paperfuge（应该是 `apple_heart_study_演讲稿.md` 或类似名）
2. Paperfuge source 页放在了 raw/（应该在 notes/）

未在本次 ingest 修复（不属于编译两篇新 PDF 的范围）。已在 task-board task-010 副产物 + 本次变更摘要中告知 Javen 等其拍板修复方案。

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| ECE284 | 11/11 (100%) — 全部 PDF 已编译或归档 |
| COGS117 | 17/17 (100%) |
| ECE175B | 5/5 讲座 (100%) |
| PHIL28 | 2/8（syllabus + midterm 已编译，6 pptx 仍 blocked）|
| web-research | 2/2 (100%) |

### 待用户确认的后续

1. **是否新建 `wiki/医疗技术/` 子目录 + 提取 [[消费级设备健康感知]] concept 页**？已超过 7 源阈值。建议合并 ECE284 全部 9 个 source 的"smartphone/wearable as medical sensor"主题
2. **修复 vault 位置错误**：`notes/ECE284/Bhamla_2017_Paperfuge.md`（实为 Apple Heart Study 演讲稿）该如何处理？建议方案 A：rename 演讲稿为 `apple_heart_study_演讲稿.md`，将 raw/ 中真正的 Paperfuge source 复制（不剪切）到 notes/ 中
3. **lint 全面体检**：vault 总页数到 56 + 跨子目录 / 跨链接复杂度上升，建议在某个空闲时段跑一次完整 `/lint` 检查

---

## [2026-04-27] Daemon Ingest | PHIL28 syllabus + midterm questions（dawn-shift 部分推进）

### 操作概览
Claudian dawn-shift daemon 执行 task-003 PHIL28 编译，受 daemon 工具限制（无 python-pptx），仅完成 2 份 PDF 的编译，6 个 pptx 课件已 blocked 等 Javen 主对话处理。

### 新建文件（3 个）
| 原始文件 | 新建页面 | 类型 |
|---------|---------|------|
| `aa--Phil 28 syllabus.pdf` | [[PHIL28_2026_课程大纲]] | source（notes/PHIL28/）|
| `Midterm questions.pdf` | [[PHIL28_2026_期中考题清单]] | source（notes/PHIL28/）|
| 综合两 PDF | [[PHIL28_概览]] | overview（wiki/哲学/）|

### 新建目录
- `wiki/哲学/`（vault 第 5 个 wiki 子领域）
- `notes/ucsd/Spring 2026/PHIL28/`

### 阻塞与待办
- 6 个 pptx 课件（WK1×2 + WK2×2 + WK3×2）→ task-003 子任务 c blocked on @javen，需主对话用 python-pptx 编译
- Mill 核心 concept 页提取 → 子任务 f 依赖 c 完成
- INDEX.md / gaps.md 全量更新 → daemon 预算紧张未做，待 c/f 解阻塞后一次性更新

### 决策记录
- DoD 字段更正：原写"7 讲座"实际是 6 讲座（WK1 Intro + WK1 Mill I + WK2 II + WK2 III + WK3 IV + WK3 Turner）
- midterm 已于 4/22 考完，但保留完整候选题清单作为期末参考（期末 6/8 覆盖范围更广）
- AI 政策提醒：本课**严禁** ChatGPT/Gemini 生成新文本，本 vault 笔记仅作复习参考

### raw/ 覆盖率（PHIL28）
| 来源类型 | 覆盖率 |
|---------|--------|
| Syllabus PDF | 1/1 ✅ |
| Midterm PDF | 1/1 ✅ |
| 讲座 pptx | 0/6（blocked，等主对话编译）|

详见 `MyBrain/system/daemon-runs/2026-04-27.md`。

---

## [2026-04-27] Ingest | 思瑶视频字幕《AI 任务面板自动化系统》

### 操作概览
编译用户提供的视频字幕（作者：思瑶），介绍其用 Claude Code 搭建的"睡觉时也能干活"任务面板系统。这是 vault 中第一个 AI 工作流/agent 架构主题的来源。

### 新文件清单

| 文件 | 类型 | 位置 |
|------|------|------|
| [[2026-04-27_AI任务面板自动化系统]] | source | `notes/web-research/` |
| `2026-04-27_AI任务面板自动化系统.md`（字幕原文） | raw | `raw/web-research/` |

### 内容要点
- **真假自动化判别标准**：你睡觉时 AI 还能不能继续工作
- **五层架构**：任务面板（看板文件） → 调度层（fswatch + launchd）→ 执行层（主 agent + 子 agent）→ 业务逻辑层（Claude skill）→ 状态日志层
- **关键工程经验**：事件驱动 > 定时轮询（作者从每 30 分钟轮询改为 fswatch 事件驱动后显著省 token）
- **人机协作机制**：blocked on 用户授权——AI 遇到不能自己决定的事写明阻塞、停下、转做别的，避免越权和卡死
- **个性化适配**：作者把"我有 ADHD、启动困难"显式写进 skill，让 AI 任务分配必须具体、单次可完成

### 决策记录

- **暂不提取 concept 页**：单一来源（一个个人视频），按 CLAUDE.md "concept vs source 判定"——拿不准时先建 source 页。视频中的核心概念（事件驱动 agent 调度、任务看板架构、阻塞授权）确实是普适的，但需要等第二来源（如 Anthropic 官方 hooks 文档、其他 agent 框架文章）加入后再提取。已在 source 页 🔗 关联区列出 3 个候选 concept
- **存入 web-research 而非新建 wiki/AI工程/ 子目录**：避免为单源新建 wiki 子文件夹；后续若有更多 AI agent 工程内容再考虑建 `wiki/AI工程/` 或 `wiki/工具与方法/`
- **保留字幕原文转录错误**：raw/ 文件保留视频自动转录的原貌（NAT图、GPS、Sly,ao 等明显误识），在 source 页用对照表显式澄清。这样既忠实于来源又不让错误蔓延到知识层
- **末尾"核对14天时间线..."标注为疑似串入**：与正文无关的另一段内容，在 raw 和 source 页都明确标注，不解读

### 更新文件
- INDEX.md — Web Research 分区新增条目；source 类型分类表新增条目；目录结构图 web-research 从 1 file 更新为 2 files；统计 49 → 50（source +1，confidence: medium +1）
- gaps.md — 新增 4 条推测性问题（fswatch+launchd 重复触发风险、多设备同步、event-driven 省 token 量化、ADHD 适配规则可推广性）

### raw/ 覆盖率（web-research）
| 来源 | 覆盖率 |
|------|--------|
| web-research | 2/2 (100%) — 多模态故事生成 + AI 任务面板自动化 |

### 待用户确认的后续
- 用户表示也想搭一个类似系统——已在对话中给出初步思路，等用户启动该工作流后再决定是否：
  - 在 vault 内建一个真正的 task-board.md
  - 写 Claude Code skill / hooks / settings.json 配置
  - 此时积累的内容达到第二来源阈值，可提取 concept 页

---

## [2026-04-22] Ingest | COGS117 Week 3–4 动作与感知发展新材料

### 操作概览
按用户指示编译 COGS117 新 PDF，其他课程的 HW/Proposal 仅复制不编译：

**完整编译（4 个 COGS117 PDF）：**
1. `raw/ucsd/Spring 2026/COGS117/Adolph et al. (2018).pdf` — Adolph, Hoch & Cole (2018) *TiCS* 走路 15 条建议
2. `raw/ucsd/Spring 2026/COGS117/Oudeyer (2017).pdf` — Oudeyer (2017) *WIREs Cogn Sci* 发展机器人综述
3. `raw/ucsd/Spring 2026/COGS117/5_perception_2.pdf` — Zettersten L6 感知发展 2 (2026-04-16)
4. `raw/ucsd/Spring 2026/COGS117/7_walking.pdf` — Zettersten L7 走路与动作发展 (2026-04-21)

**简单复制到 notes/（4 个文件，不做 source 页编译）：**
- `cogs_117_sp26_exam_1_study_guide.pdf` → `notes/ucsd/Spring 2026/COGS117/`（考前参考）
- `ECE175B/Homework_1.pdf`、`ECE175B/proposal.pdf` → `notes/ucsd/Spring 2026/ECE175B/`（HW/提案副本）
- `ECE284/proposal_javen_revised.pdf` → `notes/ucsd/Spring 2026/ECE284/`（用户自己的项目提案副本）

### 新文件清单

**新建 source 页面（4 个）：**

| 原始文件 | source 页 |
|---------|-----------|
| Adolph et al. (2018).pdf | [[Adolph_2018_走路发展15条建议]] |
| Oudeyer (2017).pdf | [[Oudeyer_2017_婴儿发展机器人]] |
| 5_perception_2.pdf | [[Zettersten_2026_Lecture6_感知发展2]] |
| 7_walking.pdf | [[Zettersten_2026_Lecture7_走路与动作发展]] |

**新建 concept 页面（3 个）：**

| 页面 | 主要来源 |
|------|---------|
| [[动作发展]] | Adolph 2018、Oudeyer 2017、Zettersten L7、Zettersten L4 |
| [[发展级联]] | Adolph 2018（建议 15 原型）、Zettersten L7、Oudeyer 2017 |
| [[内在动机与好奇心驱动学习]] | Oudeyer 2017（主要）、Zettersten 2025（关联） |

**新建 debate 页面（1 个）：**

| 页面 | 争议方 |
|------|--------|
| [[争论_新生儿模仿]] | Meltzoff & Moore 1977 vs Jones 1996-2006 vs Oostenbroek 2016 |

### 图片处理（PyMuPDF 2.5× zoom）
- 从 4 个 PDF 渲染 **26 张关键图**（attachments/COGS117/）：
  - Adolph 2018：2 张（15 suggestions Key Figure、走路案例 4 行对照）
  - Oudeyer 2017：3 张（iCub/Poppy/白蚁巢、被动动态步行机、Playground 实验）
  - Zettersten L6：10 张（Ponzo 错觉新视力、Mandler 全局-基本、Quinn 不对称、婴儿超过 NN、Werker 音素窄化、Scott & Monesson、Xu 标签、LaTourrette 半监督、Clerkin & Smith 视觉饮食、Clerkin & Smith 偏斜分布）
  - Zettersten L7：11 张（反射目录、Thelen stepping、Meltzoff 模仿、Oostenbroek 阴性、Garwicz 物种对比、里程碑表、WHO 问题、爬行风格、文化实践、为什么走路、发展级联）

### 更新文件（交叉链接整合）
- [[争论_婴儿被动vs主动学习]] — 新增"2026-04-22 动作发展证据"小节；补充 Adolph/Oudeyer/Thelen 三方链接；引入"动态系统作为第三条路"的新争论视角
- [[核心知识理论]] — 新增"走路的核心知识"主张受挑战的讨论；链接 Adolph 2018 反驳；链接 Oudeyer 2017 被动动态步行机
- [[感知窄化]] — 新增 Zettersten L6 回链（类别窄化补充）
- [[面孔知觉发展]] — 新增 L6 (Scott 详解) 和 [[争论_新生儿模仿]] 的回链
- [[发展研究方法]] — 新增两小节：生态效度（Adolph 2018）、发展机器人（Oudeyer 2017）；回链至 L6/L7
- [[物体识别与形状感知]] — 新增 one-shot 学习证据小节（L6 呈现 Ayzenberg 2022 婴儿超过 NN）
- [[Zettersten_2025_婴儿主动学习]] — 新增 Adolph/Oudeyer/L6/L7/内在动机等回链
- [[Cusack_2024_婴儿无助期假说]] — 新增 Adolph 2018 挑战、动作发展、发展级联的回链
- [[COGS117_概览]] — 讲座列表补全 L6、L7；文献笔记补全 Adolph 2018、Oudeyer 2017；概念导航新增动作发展、发展级联、内在动机、争论_新生儿模仿；考前参考小节链接到 study guide PDF
- INDEX.md — 全量更新：
  - COGS117 讲座新增 L6/L7 两条
  - COGS117 核心概念新增 3 条（动作发展、发展级联、内在动机与好奇心驱动学习）
  - COGS117 文献笔记新增 2 条（Adolph 2018、Oudeyer 2017）
  - 争论部分新增 [[争论_新生儿模仿]]
  - 按类型分类表全量重写
  - 目录结构图更新所有 new 标注、反映 4 个复制的 PDF
  - 概念导航新增 14 条（动作发展、里程碑、Stepping reflex、发展机器人、内在动机、发展级联、跨文化变异、自然观察、类别发展、标签与个体化、新生儿模仿、被动动态步行机等）
  - 争论汇总新增"2026-04-22 动作发展文献扩展"小节和"新生儿模仿三方辩论"独立小节
  - 统计 41 → 49 页（source +4, concept +3, debate +1）
- gaps.md — 新增 9 条推测性问题（Oudeyer LP 现代复现、infant-like motor curriculum 基准、走路→语言因果识别、Cusack 动作发展兼容性质疑、新生儿模仿 MEG 验证、Thelen 反向实验、Clerkin & Smith 跨文化、LLM-based agents 阶段涌现、发展级联 × 多任务学习）

### 决策记录

- **三个 concept 页同时建立的理由**：
  - [[动作发展]]：Adolph 2018 + Oudeyer 2017 + Zettersten L7 + 已有 L4 = 4 个独立来源，明显跨来源独立存在
  - [[发展级联]]：Adolph 2018 建议 15 明确命名了这个概念；Zettersten L7 详细展开；Oudeyer 2017 Playground 实验是级联的工程示范——三源达到阈值
  - [[内在动机与好奇心驱动学习]]：Oudeyer 2017 提出形式化定义；Zettersten 2025 主动学习框架包含内在动机作为子机制；Kidd & Hayden 等跨年龄证据——从"单源"升级到"主要来源 + 关联来源"，可建 concept 页但标 confidence: medium
- **[[争论_新生儿模仿]] 建独立 debate 页的理由**：L7 清晰呈现了三方阵营（Meltzoff 证据 vs Jones 兴奋说 vs Oostenbroek 大样本无效），**都是文献中已存在**的对立（不是编译者推测）——符合 CLAUDE.md debate 页标准
- **三方争议而非二方**：与 [[争论_婴儿被动vs主动学习]] 的 2 方对立不同，新生儿模仿是 3 方（"先天模仿"、"一般兴奋"、"根本无效"）——这更真实地反映了科学争议的复杂性
- **不建"反射"concept 页**：反射只在 L7 一篇讲座详细讨论；内容已充分在 source 页覆盖；等有更多反射相关文献再提取
- **新生儿模仿列入 debate 而非 concept**：模仿本身是现象；现象**是否存在**是未解决争议。直接建 debate 页更符合知识状态
- **"动态系统"未单独建页**：虽然反复出现，但内容主要在 [[Zettersten_2026_Lecture4_发展理论]] 和 [[动作发展]] 中已分散呈现——等有更多综述性来源再考虑
- **"先懂再细"叙述结构严格执行**：4 篇 source 页都按"问题 → 核心结论 → 机制（含类比）→ 证明（图表就近解读）→ 意味着什么 → 技术细节"六段展开；所有图表用 `>` 引用块解读"告诉我们什么"而非描述画面
- **ECE175B HW1/proposal、ECE284 proposal**：按用户指示"不需要更改，复制一份到对应的 note 部分"——原样复制，不做 source 页编译。PHIL28 的 8 个材料本轮**暂不处理**（用户明确说"主要是 cogs117 的"）

### raw/ 覆盖率
| 课程 | 覆盖率（source 页数 / 可编译 raw 文件数） |
|------|--------|
| COGS117 | 17/17 (100%) — 全部 PDF 已编译或归档 |
| ECE284 | 9/9 (100%) — proposal PDF 作副本归档 |
| ECE175B | 5/5 讲座 (100%) — HW1/proposal 作副本归档 |
| PHIL28 | 0/8 — 全新课程，本轮按用户指示未处理 |
| web-research | 1/1 (100%) |

### 待用户确认的后续
1. **PHIL28（自由言论课，J.S. Mill On Liberty）**：8 个新 pptx/pdf 材料（含 7 讲座 + syllabus + midterm questions）。下轮是否开始编译？建议新建 `wiki/哲学/` 子目录存放 concept 页
2. **Exam 1（COGS117, 4/23）**：考前两天，本轮编译的 Week 3–4 材料齐全。study guide 已放入 notes/，方便结合讲座和文献笔记复习

---

## [2026-04-20] Ingest | ECE284 两篇新文献 + ECE175B HW1 多模态生成研究

### 操作概览
按用户指示编译 raw/ 中的三个新材料（"只管34"——跳过 ECE175B HW1 题目本身、Project Proposal、apple-heart-study.html 等）：
1. `raw/ucsd/Spring 2026/ECE284/3803808.pdf` — NormWear（Luo et al. 2026），可穿戴信号通用基础模型
2. `raw/ucsd/Spring 2026/ECE284/s41598-024-51567-w.pdf` — TemPredict（Mason et al. 2024），20K 人 Oura Ring 体温-抑郁队列研究
3. `raw/web-research/2026-04-20_多模态故事生成研究.md` — 用户为 ECE175B HW1 抓取的 SOTA 调研笔记，覆盖 Transfusion / Chameleon / DiffuStory / Infinite-Story

### 新文件清单

**新建 source 页面（3 个）：**

| 原始文件 | source 页 | 位置 |
|---------|-----------|------|
| 3803808.pdf | [[Luo_2026_NormWear]] | notes/ucsd/Spring 2026/ECE284/ |
| s41598-024-51567-w.pdf | [[Mason_2024_TemPredict]] | notes/ucsd/Spring 2026/ECE284/ |
| 2026-04-20_多模态故事生成研究.md | [[2026-04-20_多模态故事生成研究]] | notes/web-research/（新目录）|

**新建 concept 页面（1 个）：**

| 页面 | 主要来源 |
|------|---------|
| [[统一多模态生成架构]] | 多模态故事生成研究（综述 + Transfusion + Chameleon + DiffuStory + Infinite-Story 共 5 个独立来源）|

### 图片处理（PyMuPDF 2.5× zoom）
- 从 NormWear PDF 渲染 6 张关键图（pages 2/3/6/8/12/15）→ `attachments/ECE284/`：框架总览、预训练流程、数据分布、MSiTF、scaling 性能、回归任务
- 从 TemPredict PDF 渲染 5 张关键图（pages 3/4/5/7/8）→ `attachments/ECE284/`：体温×抑郁分布、自报昼夜节律、OR 森林图、ROC、可穿戴远端体温分布
- 共 11 张新图

### 更新文件（双向链接整合）
- [[Zhang_2015_TROIKA]] — 新增回链至 [[Luo_2026_NormWear]]，标注"信号处理流水线 → 学习方法"的范式转移
- [[Perez_2019_AppleHeartStudy]] — 新增回链至 [[Luo_2026_NormWear]] 和 [[Mason_2024_TemPredict]]，承接"消费级可穿戴大规模研究"范式
- [[Shah_2025_LossOfPulse]] — 新增回链至 [[Luo_2026_NormWear]]，体现"通用 vs 专用"基础模型设计权衡
- [[ECE175B_Lecture1b_贝叶斯网络]] — 新增回链至 [[统一多模态生成架构]]，"LLM 是链式 BN" → 多模态 AR 序列
- [[ECE175B_Lecture3_变分推断与ELBO]] — 新增回链至 [[统一多模态生成架构]]，ELBO → DDPM 扩散损失理论基础
- [[ECE175B_Lecture4_生成对抗网络]] — 新增回链至 [[统一多模态生成架构]]，GAN 作为现代多模态范式的 baseline 对照
- [[ECE175B_概览]] — 新增回链至 [[统一多模态生成架构]] 和 [[2026-04-20_多模态故事生成研究]]，HW1 设计参考
- INDEX.md — 全量更新：
  - 新增"Web Research"分区
  - ECE284 新增 2 个 source 条目
  - 新增 wiki/机器学习/统一多模态生成架构.md
  - 概念导航新增 12 条（可穿戴基础模型、Channel-Aware Attention、CWT、MAE、Oura Ring/体温、抑郁生理标志、统一多模态生成、Transfusion/Chameleon、扩散模型等）
  - 统计 37 → 41 页（source +3, concept +1）
  - 目录结构图新增 web-research 子目录
- gaps.md — 新增 9 条推测性问题（NormWear+TemPredict 体温通道整合、NormWear 与 Transfusion 的"主干+模态适配器"结构同构、Transfusion 的 λ 调优、DiffuStory 反向应用到图像、多模态可穿戴融合到 0.9 AUC、NormWear zero-shot 临床描述、跨领域 alignment 损失统一等）

### 决策记录

- **NormWear 暂不建独立 concept 页**：虽然"可穿戴基础模型"是普适概念，但目前仅 NormWear 一个来源；按 CLAUDE.md "concept vs source 判定"——拿不准时先建 source 页，等更多文献加入再提取 concept。已在 INDEX 概念导航中加入"可穿戴基础模型"条目，方便后续聚类
- **统一多模态生成架构**建独立 concept 页**：调研笔记中讨论了 5 个独立来源（综述 + Transfusion + Chameleon + DiffuStory + Infinite-Story），且 GPT-4o 是工业界标志——已超过单源阈值，符合"概念能脱离特定文献独立存在"的标准
- **新建 notes/web-research/ 子目录**：raw/web-research/ 是用户主动建立的"外部抓取材料"分类，notes/ 镜像 raw/ 结构需要相应建子目录
- **跨课程联系明示**：NormWear 是 ECE284 课程材料，但提供的"通用基础模型 + 模态适配器"设计与 ECE175B 的 Transfusion 形成结构对照——已在 gaps.md 记录这一开放问题，未在正文断言（遵循"忠实于来源"原则）
- **TemPredict 治疗启示部分忠实记录**：原文最有趣的"全身热疗反向降基线体温"机制虽具有反直觉震撼力，但完全是论文已论述内容，不是编译者推测，故放在正文"意味着什么"小节
- **"先懂再细"叙述结构严格执行**：两篇 source 页都按"问题 → 核心发现 → 机制 → 证明 → 意味着什么 → 局限"五段展开；图表用 `>` 引用块解读"支持哪个论点"而非描述像素

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 13/13 (100%) |
| ECE284 | 9/9 (100%) |
| ECE175B | 5/5（讲座）+ 1 web-research / 数个 HW 文件未编译（按用户指示跳过）|
| web-research | 1/1 (100%) |

### 用户主动跳过的文件
按用户"只管34"指示，以下文件**未在本轮编译**：
- `raw/ucsd/Spring 2026/ECE175B/ECE175B HW1.pdf`（HW 题目）
- `raw/ucsd/Spring 2026/ECE175B/ECE175B Project Proposal.pdf`（项目提议要求）
- `raw/ucsd/Spring 2026/ECE284/apple-heart-study.html`（Apple Heart Study 网页镜像，与 [[Perez_2019_AppleHeartStudy]] 重复）

下次编译可询问用户是否需处理 HW/Proposal 文件（其中可能有用户已答的内容值得归档）。

---

## [2026-04-17] Ingest | COGS117 七个新文件（感知发展 + 四堂讲座）

### 操作概览
编译 `raw/ucsd/Spring 2026/COGS117/` 下七个新 PDF——覆盖 Week 1–3 的讲座全部（L1/L2/L4/L5）与 Week 3 的核心阅读（Scott 2009、Johnson 2024、Ayzenberg 2024）。这是 COGS117 课程从"Week 2 外围文献"扩展到"完整讲座 + 感知发展主题"的关键一步，共新增 12 个页面。

### 新文件清单

**源文件 → 新建 source 页面（7 个）：**

| 原始 PDF | source 页 |
|----------|-----------|
| `scott_monesson_2009.pdf` | [[Scott_2009_面孔知觉偏差起源]] |
| `infant_perception.pdf` | [[Johnson_2024_婴儿感知]] |
| `ayzenberg_behrmann_2024.pdf` | [[Ayzenberg_2024_视觉物体识别发展]] |
| `1_intro_big_questions.pdf` | [[Zettersten_2026_Lecture1_课程导论与大问题]] |
| `2_developmental_methods.pdf` | [[Zettersten_2026_Lecture2_发展研究方法]] |
| `4_developmental_theories.pdf` | [[Zettersten_2026_Lecture4_发展理论]] |
| `5_perception_1.pdf` | [[Zettersten_2026_Lecture5_感知发展1]] |

**新建 concept 页面（5 个，多来源综合）：**

| 页面 | 主要来源 |
|------|---------|
| [[感知窄化]] | Scott 2009、Johnson 2024、Ayzenberg 2024、Zettersten L5 |
| [[面孔知觉发展]] | Scott 2009、Ayzenberg 2024、Johnson 2024、Zettersten L5 |
| [[核心知识理论]] | Zettersten L1/L2/L4/L5、Ayzenberg 2024 |
| [[物体识别与形状感知]] | Ayzenberg 2024、Johnson 2024、Zettersten L5 |
| [[发展研究方法]] | Zettersten L2、所有实验来源 |

### 图片处理（PyMuPDF 2.5× zoom）
- 从 7 个 PDF 共渲染 **32 张关键图** → `attachments/COGS117/`
- Scott 2009：Fig 1 方法、Fig 2 结果
- Ayzenberg 2024：6 张关键图（视点不变性挑战、习惯化范式、fNIRS 形状敏感性、骨架模型、面孔剥夺猴、发展时间线）
- Johnson 2024：2 张（视觉发展时间线、音素窄化）
- Zettersten L1：6 张（四大问题、Moravec、Ibex、视崖、核心知识、A-not-B）
- Zettersten L2：5 张（CDI/Wordbank、SEEDLingS、习惯化、违反预期、EEG/fNIRS/MRI）
- Zettersten L4：3 张（Piaget、Vygotsky、动态系统）
- Zettersten L5：6 张（窄化、面孔偏好、面孔经验、Kellman、Spelke、Emberson）

### 更新文件
- [[争论_婴儿被动vs主动学习]] — 新增"感知发展文献获得的额外证据"章节：Scott/Ayzenberg 支持主动派，Emberson 兼容两派；扩充关联链
- [[COGS117_概览]] — 重组关联区为"课程基础 + 讲座笔记（按周）+ 文献笔记 + 概念与争论"四档
- INDEX.md — 全量重写：
  - 新增 "讲座笔记（按周顺序）"分区（5 讲）
  - concept 页从 2 个扩展至 7 个
  - source 页从 19 个扩展至 26 个
  - 概念导航新增 15 条（感知窄化、面孔知觉、物体识别、核心知识、视点不变性、骨架模型、腹侧通路、违反预期、习惯化、fNIRS、预测编码、发展理论、Moravec、保护性不成熟等）
  - 统计 25 → 37 页
- gaps.md — 新增 9 条推测性问题（Scott 2009 推广到非面孔域、语言标签的神经机制、骨架表征 × AI 类比、面孔剥夺的临床推断、Emberson 数据的派系区分实验、Jayaraman + SAYcam 整合训练、核心知识的双胞胎范式、Vygotsky × 元学习、形状表征与类别窄化时差）

### 决策记录

- **5 个 concept 页同时建立的理由**：7 个新 source 共同支撑了多个跨源概念——感知窄化（4 源）、面孔知觉（4 源）、核心知识（5 源）、物体识别（3 源）、研究方法（5+ 源）都达到"概念脱离单一文献独立存在"的建页阈值（CLAUDE.md § concept vs source 判定）
- **讲座笔记命名采用 `Zettersten_2026_LectureN_主题`**：与已有 [[Zettersten_2026_计算模型与框架]] 的 source 命名兼容，且通过 `LectureN` 保持周次可排序
- **debate 页不重建而是增量扩充**：Cusack vs Zettersten 的核心矛盾仍是两篇原论文；新的感知证据是**延伸线索**，作为独立小节加到既有 debate 页底部，不在多个 source 页重复展开（遵循 CLAUDE.md § source vs debate 职责）
- **不新建 synthesis 页**：虽然核心知识理论、感知窄化、预测编码构成一个连贯的"感知发展框架"，但目前还没有跨领域（如认知 × AI × 神经）的结构性对应需要单独综合——等后续 Week 4+ 编译运动/语言后再考虑
- **COGS117 概览补全讲座笔记索引**：将零散的讲座按周整理到概览，让"Week 3 感知发展"有个完整入口，方便考试复习

### raw/ 覆盖率
| 课程 | 覆盖率（source 页数 / raw 文件数） |
|------|--------|
| COGS117 | 13/13 (100%) |
| ECE284 | 7/7 (100%) |
| ECE175B | 5/5 (100%) |

---

## [2026-04-14] Ingest | ECE175B 五讲课程（Deep Generative Models）

### 操作概览
编译 `raw/ucsd/Spring 2026/ECE175B/` 下全部 5 个 PDF（lecture-1a 至 lecture-4），同时结合用户提供的课堂黑板照片（约 30 张）进行交叉验证。这是知识库中首次出现 ECE175B 课程内容。

### 图片处理（幻灯片渲染）
- 从 5 个 lecture PDF 用 PyMuPDF（2.5× zoom）渲染 18 张关键幻灯片 → `attachments/ECE175B/ECE175B_L*.png`
- 覆盖范围：课程总览图、判别 vs 生成对比、三大问题、PGM 概览、BN 分解、DAG 实例、LLM 作为 BN、VAE 图设计、decoder 架构、三大任务、推断问题、KL 散度、ELBO 推导、EM 算法、GAN 引入/架构/训练

### 新建文件
- [[ECE175B_Lecture1a_课程导论与DGM概述]] — 课程后勤、DGM=PGM+DL、判别 vs 生成、三大核心问题、BN 分解公式
- [[ECE175B_Lecture1b_贝叶斯网络]] — DAG 七节点实例、I-map、LLM 是链式 BN、Transformer 参数化
- [[ECE175B_Lecture2_变分自编码器设计]] — Z→X 图、先验 N(0,I)、decoder f(Z)/g(Z)、三大任务（训练/生成/推断）
- [[ECE175B_Lecture3_变分推断与ELBO]] — 推断 NP-hard、KL 散度、MLE 困难、Jensen 不等式→ELBO、EM 坐标上升
- [[ECE175B_Lecture4_生成对抗网络]] — 图灵测试→GAN、Generator/Discriminator、对抗训练、VAE vs GAN 对比
- [[ECE175B_概览]] — 课程信息、知识地图、讲座进度、核心概念索引

### 新建目录
- `notes/ucsd/Spring 2026/ECE175B/`
- `attachments/ECE175B/`

### 更新文件
- INDEX.md — 新增 ECE175B 分区（6 个条目）、概念导航扩充 11 条、统计 19→25 页
- gaps.md — 新增 2 条推测性问题（Diffusion Models 与 ELBO 框架关系；LLM 的 BN 视角 vs 自监督学习视角）

### 决策记录
- **暂不提取 concept 页：** BN、VAE、GAN、ELBO 等概念虽然普适，但目前只有 ECE175B 讲座这一个来源。等后续有论文或其他课程引用这些概念时再提取 concept 页——先积累 source，让概念的普适性自然显现
- **概览页放置：** ECE175B_概览 放 `wiki/机器学习/`，因为 DGM 属于机器学习子领域
- **黑板照片处理：** 用户提供的课堂照片用于内容交叉验证（确认 PDF 幻灯片之外的板书推导细节），但不单独存档为 raw/ 材料（照片内容已完全被 PDF + source 页覆盖）
- **跨课程联系：** 发现 ECE175B L1b（LLM 是 BN）与 COGS117 [[Frank_2023_数据鸿沟]]（LLM 数据效率）和 [[自监督学习与基础模型]]（自监督 ≈ 自回归）存在有趣交叉，已记录至 gaps.md

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 6/6 (100%) |
| ECE284 | 7/7 (100%) |
| ECE175B | 5/5 (100%) |

---

## [2026-04-12] Ingest | ECE284 两篇新文献 + Paperfuge 图片补充 + 种族偏见综合页

### 操作概览
编译 `raw/ucsd/Spring 2026/ECE284/` 下两个新文件（Apr 12 新增）：脉搏血氧仪种族偏差（Jubran 1990）与医疗算法种族偏见（Obermeyer 2019）。同步补充 Bhamla_2017_Paperfuge 四张原文图片，并新建跨文献综合页。

### 图片处理（原资料里的图）
- 从 `PIIS0012369216320293.pdf` 用 PyMuPDF 渲染关键页面，提取 Fig 1 单独图像 → `attachments/ECE284/Jubran_1990_*.png/jpeg`
- 从 `science.aax2342.pdf` 渲染含图页面 → `attachments/ECE284/Obermeyer_2019_*.png`
- 从 Nature Biomedical Engineering 外链下载 Paperfuge 四图 → `attachments/ECE284/Bhamla_2017_Fig*.jpg`

### 新建文件
- [[Jubran_1990_脉搏血氧仪种族偏差]] — CHEST 1990；脉搏血氧仪皮肤色素偏差；SpO₂ 92% 白人 PPV 100% vs 黑人 PPV 50%；含全部 4 图
- [[Obermeyer_2019_医疗算法种族偏见]] — Science 2019；商业医疗管理算法种族偏差；费用代理健康导致黑人风险分低估 26.3%；含 Fig 1–3
- [[综合_医疗技术中的种族偏见]] — 连接 Jubran + Obermeyer + Shah + Perez 的跨文献种族偏差主题；传感器层 × 算法层双层叠加分析

### 更新文件
- [[Bhamla_2017_Paperfuge]] — 补充 Fig 1–4（从 Nature 外链下载至本地）；updated → 2026-04-12；新增综合页回链
- [[Shah_2025_LossOfPulse]] — 🔗 新增回链至 [[Jubran_1990_脉搏血氧仪种族偏差]] 和 [[综合_医疗技术中的种族偏见]]
- INDEX.md — ECE284 新增 2 条目，综合导航扩充，统计 15→18 页；综合/ 文件夹不再为空
- gaps.md — 新增 3 条推测性问题（PPG 种族偏差延伸至 Shah / Perez / Song）

### 决策记录
- 两篇 ECE284 新文献共同揭示"医疗技术种族偏差"主题，达到建立综合页阈值（两篇独立来源，主题可跨越两篇单独讨论）
- 综合页放 `wiki/综合/`（已有文件夹，无需新建）
- 建议日后提取"脉搏血氧仪"或"PPG 信号质量"concept 页时，将 Jubran 1990 + Zhang 2015 作为主要来源

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 6/6 (100%) |
| ECE284 | 7/7 (100%) |

---

## [2026-04-10] Ingest | ECE284 三篇新文献 + title 修正

### 操作概览
编译 ECE284 三个新文件，同时将已有两篇 ECE284 笔记的 frontmatter `title` 字段修正为实际论文标题（英文）。

### 新建文件
- [[Bhamla_2017_Paperfuge]] — 20 美分纸质离心机；陀螺力学非线性振荡器；125,000 rpm；血浆/疟疾寄生虫分离
- [[Song_2024_SmartphoneMicroscope]] — 智能手机显微镜附件（m-phone）术前血细胞计数；Hough 圆检测；R²=0.895
- [[Shah_2025_LossOfPulse]] — 智能手表 PPG + 运动多门控算法检测心脏骤停；特异性 99.987%；敏感度 67.23%

### 更新文件
- [[Zhang_2015_TROIKA]] — title 修正为实际论文标题；🔗 新增回链至 [[Shah_2025_LossOfPulse]]
- [[Perez_2019_AppleHeartStudy]] — title 修正为实际论文标题；🔗 新增回链至 [[Shah_2025_LossOfPulse]]
- INDEX.md — ECE284 新增 3 个条目，概念导航扩充，统计 12→15 页
- gaps.md — 新增 2 条推测性问题（Shah 延迟设计；Paperfuge + m-phone 整合）

### title 修正记录

| 文件 | 修正前 | 修正后 |
|------|--------|--------|
| Zhang_2015_TROIKA.md | TROIKA：运动中腕式 PPG 心率监测框架 | TROIKA: A General Framework for Heart Rate Monitoring Using Wrist-Type Photoplethysmographic Signals During Intensive Physical Exercise |
| Perez_2019_AppleHeartStudy.md | Apple Heart Study：智能手表大规模房颤筛查 | Large-Scale Assessment of a Smartwatch to Identify Atrial Fibrillation |

### 决策记录
- ECE284 现有 5 篇文献，PPG 主题跨越 3 篇（Zhang、Perez、Shah），已接近建 concept 页的阈值——下一篇 ECE284 文献加入后考虑提取「PPG 可穿戴检测」concept 页
- 「即时诊断 POC」主题跨 Paperfuge 和 m-phone 两篇，暂不建 concept 页（仅两篇来源且都是工程原型类）

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 6/6 (100%) |
| ECE284 | 5/5 (100%) |

---

## [2026-04-09] Ingest | ECE284 第二篇文献（Apple Heart Study）

### 操作概览
编译 `raw/ucsd/Spring 2026/ECE284/NEJMoa1901183.pdf`。Perez et al. (2019) Apple Heart Study：419,297 人参与的大规模可穿戴设备房颤筛查临床验证。

### 新建文件
- [[Perez_2019_AppleHeartStudy]] — Apple Watch 不规则脉搏通知算法的大规模前瞻性验证

### 更新文件
- [[Zhang_2015_TROIKA]] — 🔗 新增回链至 [[Perez_2019_AppleHeartStudy]]（双向链接：PPG 信号处理 ↔ 临床验证）
- INDEX.md — ECE284 分区新增条目、概念导航新增房颤/数字健康/可穿戴临床验证、统计更新（11→12 页）
- gaps.md — 新增 2 条推测性问题（ECG 贴片延迟对 PPV 的影响；TROIKA 与 Apple Watch 算法的技术关系）

### 决策记录
- 暂不创建 concept 页（房颤、PPG 临床应用等）：目前仅两篇 ECE284 来源，且两篇侧重不同（信号处理 vs 临床验证），等更多文献后再提取通用概念
- 两篇 ECE284 文献的共同概念「PPG」已在 INDEX 概念导航中关联，待第三篇来源后考虑建立 concept 页

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 6/6 (100%) |
| ECE284 | 2/2 (100%) |

---

## [2026-04-09] Ingest | ECE284 首篇文献

### 操作概览
编译 `raw/ucsd/Spring 2026/ECE284/TROIKA_IEEE_TBME_2015.pdf`。这是一个全新领域（生物医学信号处理/可穿戴设备），知识库中首次出现 ECE284 课程内容。

### 新建文件
- [[Zhang_2015_TROIKA]] — Zhang et al. (2015) TROIKA 框架：腕式 PPG 剧烈运动心率监测

### 新建目录
- `notes/ucsd/Spring 2026/ECE284/`

### 更新文件
- INDEX.md — 新增 ECE284 分区、概念导航、统计更新（10→11 页）

### 决策记录
- 暂不创建 concept 页（PPG、SSA、SSR 等）：目前仅单一来源，等更多 ECE284 文献加入后再提取通用概念

### raw/ 覆盖率
| 课程 | 覆盖率 |
|------|--------|
| COGS117 | 6/6 (100%) |
| ECE284 | 1/1 (100%) |

---

## [2026-04-08] 补全缺失 source 页 | 3 个 raw/ 文件

### 操作概览
发现 raw/ucsd/Spring 2026/COGS117/ 下 6 个文件中有 3 个未建 source 页，按 CLAUDE.md 规范补全。

### 新建文件
- [[COGS117_2026_课程大纲]] — 课程大纲原始记录（`Cogs 117 Sp 2026 Syllabus.pdf`）
- [[Love_2026_监督与无监督学习]] — Love OECS 综述（`supervised_unsupervised_learning.pdf`）
- [[Zettersten_2026_计算模型与框架]] — Week 2 讲座幻灯片（`3_computational_models_frameworks.pdf`）

### 更新文件
- [[监督学习与无监督学习]] — 🔗 新增回链至 [[Love_2026_监督与无监督学习]]
- [[自监督学习与基础模型]] — 🔗 新增回链至 [[Love_2026_监督与无监督学习]]
- [[COGS117_概览]] — 🔗 新增回链至 [[COGS117_2026_课程大纲]] 和 [[Zettersten_2026_计算模型与框架]]
- INDEX.md — 全量重写，页面总数 7 → 10
- gaps.md — 新增 1 条推测性问题（Marr 层级与 Cusack/Zettersten 争论的关系）

### 页面统计
| 指标 | 变更前 | 变更后 |
|------|--------|--------|
| 总页面数 | 7 | 10 |
| source 页 | 3 | 6 |
| raw/ 覆盖率 | 3/6 (50%) | 6/6 (100%) |

---

## [2026-04-08] CLAUDE.md v3 架构重构 | notes/wiki 分离

### 操作概览
按 CLAUDE.md v3 规范执行架构级重构：source 页面从 wiki/ 迁出至 notes/（镜像 raw/ 结构），wiki/ 内按知识领域建立子文件夹，INDEX.md 全量重写。

### 目录结构变更

**新建目录：**
- `notes/ucsd/Spring 2026/COGS117/` — source 页面新位置（镜像 raw/）
- `wiki/机器学习/` — concept 页面
- `wiki/争论/` — debate 页面
- `wiki/认知科学/` — overview 页面
- `wiki/综合/` — synthesis 页面（暂空）

### 文件迁移（7 个页面）

| 页面 | 原路径 | 新路径 |
|------|--------|--------|
| Frank_2023_数据鸿沟 | `wiki/` | `notes/ucsd/Spring 2026/COGS117/` |
| Cusack_2024_婴儿无助期假说 | `wiki/` | `notes/ucsd/Spring 2026/COGS117/` |
| Zettersten_2025_婴儿主动学习 | `wiki/` | `notes/ucsd/Spring 2026/COGS117/` |
| 监督学习与无监督学习 | `wiki/` | `wiki/机器学习/` |
| 自监督学习与基础模型 | `wiki/` | `wiki/机器学习/` |
| 争论_婴儿被动vs主动学习 | `wiki/` | `wiki/争论/` |
| COGS117_概览 | `wiki/` | `wiki/认知科学/` |

### Wikilink 验证
全部 7 个内容页使用短名称 wikilink（如 `[[Frank_2023_数据鸿沟]]`），Obsidian 跨文件夹自动解析，无需路径修改。

### 其他更新
- INDEX.md 全量重写：新增目录结构图、按类型分类表更新
- gaps.md 已验证：6 条待回答问题保持不变

### 决策记录
- 用户决定：`自监督学习与基础模型.md` 暂不拆分为两页，等有更多来源再说

---

## [2026-04-08] Opus 严格合规重构 | 方案 A 一劳永逸

### 操作概览
Opus 模型全面审查后执行严格合规重构：文件重命名、wikilink 级联更新、type 修正、内容去重、⚠️ 小节净化、gaps.md 创建。

### 文件重命名（5 个）

| 旧文件名 | 新文件名 | 依据 |
|----------|----------|------|
| `COGS117_课程概览.md` | `COGS117_概览.md` | overview 命名模板 |
| `儿童与LLM数据鸿沟.md` | `Frank_2023_数据鸿沟.md` | source 命名模板：`作者_年份_关键词` |
| `婴儿无助期假说_Cusack2024.md` | `Cusack_2024_婴儿无助期假说.md` | source 命名模板：作者前置 |
| `婴儿主动学习_Zettersten2025.md` | `Zettersten_2025_婴儿主动学习.md` | source 命名模板：作者前置 |
| `婴儿发展与AI学习的核心争论.md` | `争论_婴儿被动vs主动学习.md` | debate 命名模板：`争论_` 前缀 |

### Wikilink 级联更新
全部 7 个内容页 + INDEX.md 中的旧链接名已更新为新文件名。共替换约 40 处 `[[wikilink]]`。

### 内容修正（4 项）

1. **type 修正**：`监督学习与无监督学习.md` 的 `type: synthesis` → `type: concept`（与 INDEX 分类一致）
2. **内容去重**：
   - `Cusack_2024_婴儿无助期假说.md`：将 4 条反驳展开 → 精简为简要提及 + 链接到 debate 页
   - `Zettersten_2025_婴儿主动学习.md`：将对比表格 → 精简为简要提及 + 链接到 debate 页
3. **⚠️ 小节净化**：移除 agent 推测性内容，仅保留来源文献中已呈现的矛盾和开放问题
   - agent 推测（有价值的）已迁移至 `gaps.md`
4. **INDEX.md 全量重写**：使用新文件名、正确 type 分类

### 新建文件
- `gaps.md`：从各页面 ⚠️ 小节迁移的 6 条推测性问题

### 页面统计

| 指标 | 值 |
|------|------|
| 总内容页 | 7 |
| concept | 2（监督学习与无监督学习、自监督学习与基础模型）|
| source | 3（Frank_2023、Cusack_2024、Zettersten_2025）|
| debate | 1（争论_婴儿被动vs主动学习）|
| overview | 1（COGS117_概览）|
| confidence: high | 3 |
| confidence: medium | 4 |

---

## [2026-04-08] Sonnet 质量审查 | 格式 Bug 修复

发现并修复 8 处问题：4 个双重分隔线、1 个内容重复、2 个 confidence 误标、1 个标签格式。

---

## [2026-04-08] 初始规范化 | Haiku CLAUDE.md 合规性升级

对 wiki/ 下全部 6 个内容页面进行 Frontmatter 标准化（`name` → `title`、新增 type/tags/sources/created/updated/confidence/priority）、结构规范化（🔗 关联、📎 来源）、创建 INDEX.md 和 log.md。
