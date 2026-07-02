# Vault 整理方案（PARA 改造提案）

> 生成于 2026-07-02，基于对整个 vault 的只读盘点。**本次没有移动/改名/删除任何文件**——以下全部是提案，等你批准后再分阶段执行。
> 审阅建议：先读「TL;DR」和「关键发现」，再看「目标结构」，最后过一遍「迁移清单」里标 ⚠️ 的行。

---

## TL;DR

1. **你的 Obsidian vault 真正的根目录是 `知识库/`，不是 `MyBrain/`**——`.obsidian/` 和 git 仓库（origin: `j-a-v-e-n/knowledge-vault`）都在 `知识库/` 这一层。MyBrain 只是 vault 里最大的一个子文件夹。
2. **你有两个 inbox**：`知识库/inbox/`（高信号人物周报实际写入的地方，launchd `com.javen.people-digest` 锁定此路径）和 `MyBrain/inbox/`（本文件所在，只有 2 份手动笔记）。方案是合并为 `知识库/inbox/` 一个。
3. 建议在 **`知识库/` 根目录**建立 PARA 四文件夹（`1-projects` / `2-areas` / `3-resources` / `4-archive`），`inbox/`、`raw/`、`attachments/` 保留为顶层辅助目录。
4. **有 6 组路径被正在运行的自动化锁死，第一阶段绝对不动**（详见「自动化锁定路径」）。除此之外约 85% 的内容可以安全搬迁——全 vault 的内部链接几乎全是 `[[裸文件名]]` 式 wikilink（Obsidian 默认最短路径），搬文件夹不会断链。
5. 最大的一次性收益：**Spring 2026 三门课已经结课**，notes/raw/attachments/projects 里约 500+ 个相关文件整体进 `4-archive/`，vault 立刻清爽一半。

---

## 一、现状盘点

### 1.1 顶层结构（知识库/ = vault 根）

| 路径 | 文件数 | 内容 | 最后活跃 |
|---|---|---|---|
| `inbox/` | 5 | 周报、暑假作战表、auto-memory 等 | **2026-07-01（活跃）** |
| `AI-itself/` | 3 | AI谋生结论沉淀 + _staging 两篇 | 2026-07-01（活跃） |
| `kaggle/playground-s6e6/` | 8 | Kaggle 6月赛代码+数据（已结束） | 2026-06-13 |
| `projects/` | 1 | adg-interference.md（指向 ~/Projects 的指针笔记） | 2026-05-27 |
| `Clippings/` | 0 | 空（Web Clipper 默认落点，已 gitignore） | — |
| `Untitled/` | 0 | 空文件夹 | — |
| `MyBrain/` | ~870 | 见下 | 2026-07-02 |
| `CLAUDE.md` `AGENTS.md` `.claude/` `.obsidian/` `.git/` 等 | — | 配置，不动 | — |

### 1.2 MyBrain/ 内部

| 路径 | 文件数 | 内容 | 状态 |
|---|---|---|---|
| `inbox/` | 2 | AI独立谋生研究报告、digest搭建记初稿 | 活跃（7/1-7/2） |
| `notes/` | 103 | ucsd 三门课笔记（大头）+ AI + douyin + web-research | 5/28 后静止 |
| `wiki/` | 43 | 8 个主题域 + INDEX/log/gaps，vault 的知识沉淀核心 | 5/18 后静止 |
| `raw/` | 77 | 课程 PDF、论文原文、抖音字幕原文 | 静止 |
| `attachments/` | 178 | 论文/课件截图（按课程分） | 静止 |
| `projects/` | 245 | ece175b-adg、ece284-llm-ppg、PHIL28、douyin-pipeline | 课程项目已结束；douyin-pipeline 运行中 |
| `automation/` | 114 | ai-watch/email-triage 日报、task-board、runs、docs | **每日在写（07-01）** |
| `system/logs/` | 51 | audit.sh hook 的 JSONL 日志 | **每日在写（07-01）** |
| `career/` | 28 | 简历、cover letter、申请追踪、SoP | 5/15 后静止 |
| `research/` | 9 | 两个 5/12 的调研包 | 静止 |
| `research-ideas/` | 3 | 三篇点子 | 6/10 |
| `archive/` | 3 | 旧 CLAUDE.md 备份 | 静止 |
| `ai-collaboration/` | 1 | AI Work Delegation Architect | 6/13 |
| 根散落 | 1 | `Obermeyer_讲解网站.html`（ECE284 的产物，落错位置） | 4/12 |

### 1.3 自动化锁定路径（第一阶段绝对不动 ⚠️）

这些路径被**正在运行**的程序用绝对/相对路径引用，移动 = 自动化静默失败：

| # | 锁定路径 | 谁在写/读 | 依据 |
|---|---|---|---|
| 1 | `知识库/inbox/` | 高信号人物周报（launchd `com.javen.people-digest`，每周一） | `~/people-digest/config.toml:3` → `vault_inbox = ".../知识库/inbox"` |
| 2 | `MyBrain/projects/douyin-favorites-pipeline/` | launchd `com.javen.douyin-pipeline`（WorkingDirectory + monitor.py 绝对路径） | plist 内两处绝对路径 |
| 3 | `MyBrain/raw/douyin-favorites/` | 同上 pipeline 的输出目录 | `process.py:155`、`manual_run.py:94` |
| 4 | `MyBrain/automation/`（reports/、queue/task-board.md、logs/、runs/） | claudian daemon 每日跑 ai-watch / email-triage / task-check 等 skill | `知识库/.claude/skills/*/SKILL.md` 内硬编码路径；07-01 仍有新报告 |
| 5 | `MyBrain/system/logs/` | Claude Code hook | `知识库/.claude/hooks/audit.sh:16` 硬编码 `MyBrain/system/logs` |
| 6 | `MyBrain/career/applications.md` | email-triage skill 读它来对照已投公司 | `email-triage/SKILL.md:128` ——**career 整体搬迁时必须同步改这一行**（属第二阶段） |

另外三个「配置耦合」（不是不能动，是动了必须同一次提交里改配置）：
- `知识库/.gitignore` 排除了 `MyBrain/raw/`、`MyBrain/attachments/`、`MyBrain/archive/`、`MyBrain/automation/logs|runs/`——**raw/attachments 共约 400MB，路径一变就会被 git 收编**，必须先改 .gitignore 再移动。
- `.obsidian/graph.json` 的图谱着色规则引用 `path:MyBrain/notes`、`path:MyBrain/wiki`（纯外观，搬完顺手改）。
- 夜间 git auto-backup（`~/projects/auto-backup/`）会自动提交 vault——**执行搬迁前先在 `知识库/` 根 `touch .no-auto-commit`，搬完删掉**，避免搬到一半被自动提交。

### 1.4 内部链接会不会断？（结论：基本不会）

- 全 vault 133 个 md 文件含 wikilink，抽样统计的高频链接目标（如 `[[Vong_2024_单童语言习得]]`、`[[AI 团队设计原则]]`）**全部是裸文件名**，无路径前缀。`.obsidian/app.json` 为空 = 默认「最短路径」链接。只要**不改文件名、不产生同名文件**，用 Finder/命令行整文件夹搬移后 Obsidian 会自动按文件名重新解析，链接不断。
- 仅发现 **7 处路径式 markdown 链接**，其中 5 处是同文件夹/同项目内相对链接（douyin STATUS/README → `./iOS-Shortcut-setup.md`；ECE175B HW README → `./unistory.pdf`、`../grace-days.md`）——只要**按文件夹整体搬**（方案就是这么设计的），相对关系不变，不断链。其余 2 处是外部 URL / `file:///` 绝对路径，不受影响。
- `wiki/INDEX.md` 的正文里用文字提到过一些旧路径（如 "原始字幕在 projects/douyin-favorites-pipeline/Untitled*.md"），这是叙述不是链接，搬迁后过时但不影响功能，可下次更新 INDEX 时顺手改。
- 同名文件风险：`proposal.pdf`、`Homework_1.pdf` 等存在多份同名副本（见 1.5），若有 `![[proposal.pdf]]` 式嵌入，去重后反而更稳。

### 1.5 重复 / 过期 / 垃圾清单

**字节级重复（md5 已验证相同），建议只留 raw/ 一份：**
- `proposal.pdf` ×3：`notes/.../ECE175B/`、`raw/.../ECE175B/`、`projects/ece175b-adg/` 完全相同
- `Homework_1.pdf` ×2：`notes/.../ECE175B/` 与 `raw/.../ECE175B/`
- `cogs_117_sp26_exam_1_study_guide.pdf` ×2：`notes/.../COGS117/` 与 `raw/.../COGS117/`
- `proposal_javen_revised.pdf` ×2：`notes/.../ECE284/` 与 `raw/.../ECE284/`（同模式，未逐一 md5，删前核对）

**垃圾文件（删除需你批准，本次未删）：**
- `notes/.../ECE284/~$MedHALT_Slides_9_to_15.pptx`（Office 锁文件残留）
- 各处 `.DS_Store`、`__pycache__/`、`*.pyc`、`VAE_ChestXray_Kaggle.ipynb.bak`
- `知识库/Untitled/`（空文件夹）
- `ece284-llm-ppg/data/_source_repo/`（嵌套的完整 .git 克隆，300MB 级 .mat 数据的来源仓库——数据已解压到 DATABASE/，源仓库可删）

**意外发现：**
- `projects/ece284-llm-ppg/code/.env`——含 API key 的环境文件躺在 Google Drive 里。它**没有**被 git 追踪（项目内 .gitignore 挡住了），但仍建议把 key 作废轮换，文件移出 vault。
- `douyin-favorites-pipeline/Untitled*.md` ×8 **不是垃圾**——是 5/11 那批抖音视频的字幕原文，wiki/INDEX 明确引用它们为 source。应改名后归入 `raw/douyin-favorites/`（第三阶段，见迁移清单）。
- `notes/AI/Pal_2023_MedHALT.md` 与 `notes/.../ECE284/Pal_2023_MedHALT_深度讲解.md` 是**不同用途**的两篇（文献笔记 vs 演讲深挖），不算重复，各归各位。
- `wiki/INDEX.md` 自己记录了一个悬案：`Singhal_2025_MedPaLM2_演讲.md` 可能从未成功落盘（被 26 处 `[[Singhal_2025_MedPaLM2_演讲]]` 引用但文件不存在）——本次盘点确认 **notes/ 里确实没有这个文件**，是全 vault 唯一一组悬空链接。

---

## 二、目标结构（PARA @ 知识库根）

PARA 建在真正的 vault 根 `知识库/`，而不是 MyBrain 里——因为唯一的自动化 inbox 就在根上，而且这样 MyBrain 可以逐步退役成纯自动化区。

```
知识库/                          ← vault 根（.obsidian / .git 所在，不变）
├── inbox/                       ← 唯一捕获入口（锁定路径，周报落这里）
├── 1-projects/                  ← 有明确完成态的进行中项目
│   ├── AI谋生/                  ← 当前主项目：调研报告、作战表、结论沉淀
│   ├── digest搭建记/            ← 写作项目（初稿在改）
│   └── adg-interference.md      ← 指向 ~/Projects 的指针笔记
├── 2-areas/                     ← 无截止日期的长期职责
│   ├── career/                  ← 简历/申请/SoP（原 MyBrain/career 整体平移）
│   └── 学业/                    ← 常青学业资料（新学期开课后往这放；健身等
│                                   领域目前 vault 里没有内容，需要时再建）
├── 3-resources/                 ← 主题式长期参考
│   ├── wiki/                    ← 知识沉淀核心，整体平移，内部结构不动
│   ├── notes/                   ← 非课程的文献/视频/调研笔记（AI、douyin、web-research）
│   ├── ideas/                   ← 原 research-ideas
│   ├── ai-collaboration/        ← AI 协作方法论（我的积累、Delegation Architect）
│   └── system-docs/             ← vault 自动化系统的设计与运维文档
├── 4-archive/                   ← 完结项目与过期材料
│   ├── ucsd-2026-spring/        ← 三门课的 notes + projects + 散落产物
│   ├── kaggle-playground-s6e6/
│   └── claude-config-backups/   ← 原 MyBrain/archive
├── raw/                         ← 原始素材库（PDF/字幕/数据），gitignore 整体排除
├── attachments/                 ← 截图/图片库，gitignore 整体排除
└── MyBrain/                     ← 【过渡期遗留区】只剩自动化锁定的 4 块：
    ├── automation/                 automation/、system/、
    ├── system/                     projects/douyin-favorites-pipeline/、
    ├── projects/douyin-…-pipeline/ raw/douyin-favorites/
    └── raw/douyin-favorites/    ← 第三阶段改完配置后迁走，MyBrain 即可退役
```

设计取舍说明：
- **raw/ 和 attachments/ 不进 PARA 四文件夹**：它们是被笔记引用的素材库，已被 gitignore 整体排除（约 400MB）。塞进 4-archive 会导致 git 收编大文件，得不偿失。保留为顶层辅助目录、内部按主题分子目录即可。
- **wiki/ 整体进 3-resources 且内部一动不动**：它有自己的 INDEX/log/gaps 管理体系（ingest pipeline 维护），只平移外壳。
- **已结课的课程笔记进 archive 而不是 resources**：其中的认知科学/ML 知识精华已经沉淀进 wiki（这正是你 ingest pipeline 的设计），课程原始笔记的历史使命完成了。wiki 链接是裸文件名，归档后 `[[Saffran_1996_统计学习]]` 这类链接照常工作。

---

## 三、完整迁移清单

图例：✅ 零风险（无任何配置引用）｜⚠️ 需同步改配置（标注改哪）｜🔒 锁定不动｜🗑️ 建议删除（需批准）

### 第一阶段：零风险搬迁（一次做完，约 20 分钟）

> 执行前：`touch 知识库/.no-auto-commit`；执行后删除该文件并整体 commit 一次。

| 现路径 | → 目标 | 风险 |
|---|---|---|
| `AI-itself/`（3 文件，含 _staging/） | `1-projects/AI谋生/` | ✅ |
| `MyBrain/inbox/AI独立谋生能力模型研究报告.md` | `1-projects/AI谋生/` | ✅ |
| `MyBrain/research/2026-05-12_AI_jobs_capability_audit/`（4 文件） | `1-projects/AI谋生/research/` | ✅ |
| `inbox/暑假作战表-2026.md`、`inbox/预期问卷-调研报告对照用.md` | `1-projects/AI谋生/`（都是该项目的活跃件） | ✅ |
| `MyBrain/inbox/digest搭建记-初稿.md`（及本方案文件，审完后） | `1-projects/digest搭建记/` | ✅ |
| `知识库/projects/adg-interference.md`；随后删除空的 `知识库/projects/` | `1-projects/` | ✅ |
| `MyBrain/wiki/` 全部 43 文件 | `3-resources/wiki/`（内部结构原样） | ✅ |
| `MyBrain/notes/AI/`（2 文件中 `Pal_2023_MedHALT.md`） | `3-resources/notes/AI/` | ✅ |
| `MyBrain/notes/AI/我的积累.md` | `3-resources/ai-collaboration/` | ✅ |
| `MyBrain/notes/douyin-favorites/`（9 文件） | `3-resources/notes/douyin-favorites/` | ✅ |
| `MyBrain/notes/web-research/`（2 文件） | `3-resources/notes/web-research/` | ✅ |
| `MyBrain/ai-collaboration/AI Work Delegation Architect.md` | `3-resources/ai-collaboration/` | ✅ |
| `MyBrain/research-ideas/`（3 文件) | `3-resources/ideas/` | ✅ |
| `MyBrain/research/2026-05-12_wiki_ai_ingest_design/`（5 文件） | `3-resources/system-docs/wiki-ai-ingest-design/` | ✅ |
| `MyBrain/automation/docs/`（9 文件——只有 docs 子目录，skill 不读写它） | `3-resources/system-docs/automation/` | ✅ |
| `inbox/auto-memory.md` | `3-resources/system-docs/` | ✅ |
| `MyBrain/notes/ucsd/Spring 2026/` 整棵树（COGS117 32 + ECE175B 27 + ECE284 29 + PHIL28 2） | `4-archive/ucsd-2026-spring/notes/`（保持课程子结构，HW 文件夹整体随迁，内部相对链接不断） | ✅ |
| `MyBrain/projects/ece175b-adg/`（60 文件） | `4-archive/ucsd-2026-spring/projects/ece175b-adg/` | ⚠️ 见 .gitignore 注 |
| `MyBrain/projects/ece284-llm-ppg/`（~170 文件，含 300MB 数据) | `4-archive/ucsd-2026-spring/projects/ece284-llm-ppg/` | ⚠️ 见 .gitignore 注 |
| `MyBrain/projects/PHIL28/`（3 文件） | `4-archive/ucsd-2026-spring/projects/PHIL28/` | ✅ |
| `MyBrain/Obermeyer_讲解网站.html` | `4-archive/ucsd-2026-spring/ECE284产物/` | ✅ |
| `知识库/kaggle/`（8 文件，比赛已结束） | `4-archive/kaggle-playground-s6e6/` | ⚠️ 同上注 |
| `MyBrain/archive/`（3 份 CLAUDE 备份） | `4-archive/claude-config-backups/` | ✅（原被 gitignore，新位置会入 git——小文本文件，入库反而好） |
| `inbox/2026-04-29_凌晨主对话干了啥.md`（过期两个月） | `4-archive/`（或删） | ✅ |
| `inbox/高信号周报-2026-07-01.md` | 读完即可删或归档（周报是消耗品） | ✅ |
| `MyBrain/inbox/`（清空后的空壳） | 删除，实现单一 inbox | 🗑️ |
| `知识库/Untitled/`（空） | 删除 | 🗑️ |
| `Clippings/` | 原地保留（Web Clipper 落点，已 gitignore） | 🔒 |

**⚠️ .gitignore 注（课程项目与 kaggle 入 archive 前，先在 `知识库/.gitignore` 追加）：**
```gitignore
4-archive/**/__pycache__/
4-archive/**/*.pyc
4-archive/**/data/
4-archive/**/*.mat
4-archive/kaggle-playground-s6e6/data/
```
否则 300MB+ 的 .mat/csv 会在下次自动备份时被 push 到 GitHub。

### 第二阶段：需要同步改一处配置的搬迁（每条 = 移动 + 改配置，同一次 commit）

| 现路径 | → 目标 | 必须同步修改 |
|---|---|---|
| `MyBrain/career/` 全部 28 文件（整体平移，内部 applied/、resume-versions/ 等子结构不动） | `2-areas/career/` | `知识库/.claude/skills/email-triage/SKILL.md:128` 中 `MyBrain/career/applications.md` → `2-areas/career/applications.md` |
| `MyBrain/raw/AI/`、`raw/ucsd/`、`raw/web-research/`（douyin-favorites 除外） | `知识库/raw/` 同名子目录 | `.gitignore`：`MyBrain/raw/` 行改为同时含 `raw/`（过渡期两行并存） |
| `MyBrain/attachments/` 全部 178 文件 | `知识库/attachments/` | `.gitignore`：同上，加 `attachments/`；另 `.obsidian/graph.json` 两处 `path:MyBrain/...` 着色规则顺手更新为新路径 |
| 重复 PDF 去重（1.5 节四组，保留 raw/ 副本，删 notes/、projects/ 副本） | — | 🗑️ 删除前逐组核对 md5 |

### 第三阶段（可选，不急）：给 MyBrain 收尾退役

每一项都要改运行中的自动化配置，建议某个不忙的周末一次做一项、做完观察一天：

| 现路径 | → 目标 | 必须同步修改 |
|---|---|---|
| `MyBrain/automation/`（reports/queue/logs/runs） | `2-areas/automation/` | 4 个 SKILL.md（ai-watch、email-triage、task-add、task-check）里的所有 `MyBrain/automation/...` 路径；`.gitignore` 的 logs/runs 两行 |
| `MyBrain/system/logs/` | `2-areas/automation/audit-logs/` | `.claude/hooks/audit.sh:16` 的 `LOG_DIR` |
| `MyBrain/projects/douyin-favorites-pipeline/` | `1-projects/douyin-pipeline/`（若继续用）或 archive（若不用了） | `~/Library/LaunchAgents/com.javen.douyin-pipeline.plist` 两处绝对路径 + `launchctl unload/load`；`monitor.py:19`、`manual_run.py:41`、`process.py:155` |
| `MyBrain/raw/douyin-favorites/` | `知识库/raw/douyin-favorites/` | 同上 pipeline 的输出路径（与上一行同批改） |
| `douyin-favorites-pipeline/Untitled*.md` ×8（字幕原文） | `raw/douyin-favorites/2026-05-11_字幕_*.md`（改名补日期） | 无自动化引用，但 wiki/INDEX 叙述提到旧位置，下次更新 INDEX 时顺手改 |
| 全部完成后：删除空的 `MyBrain/` | — | 🗑️ 最后一步 |

### 垃圾清理（需你批准，任何阶段都可做）

`~$MedHALT*.pptx`、全部 `.DS_Store`、`__pycache__/`+`.pyc`、`*.ipynb.bak`、`ece284-llm-ppg/data/_source_repo/`（嵌套 git 克隆）。另请尽快处理 `ece284-llm-ppg/code/.env`：**轮换里面的 API key**，文件移出 vault。

---

## 四、每周 inbox 清理例行（5 分钟）

每周一早上读完高信号周报后顺手清 inbox（此时它是你注意力已经在的地方）：从上往下逐条过，每条 30 秒内做且只做一个动作——还在推进的 → 移进 `1-projects/` 对应项目文件夹（没有就新建一个）；属于长期职责（求职、学业）→ `2-areas/`；以后可能查的参考 → `3-resources/`（笔记类进 notes/，点子进 ideas/）；完结或过时 → `4-archive/` 或直接删；读完即弃的周报/日报直接删。两条铁律：**不在 inbox 里写作或建子文件夹**（要写就先移到项目里再写），**离开时 inbox 剩余 ≤ 10 条**——某条连续两周都下不了决心，说明它其实不重要，归档。

---

## 五、批准方式建议

回复时按阶段批：例如「第一阶段照做 + 垃圾清理照删，第二阶段先只做 career，第三阶段缓」。执行时我会：`touch .no-auto-commit` → 按清单 `git mv`（保留历史）→ 改配置 → 删哨兵 → 单次 commit + push。任何一条你不同意的，在上面表格行后标个「不动」即可。
