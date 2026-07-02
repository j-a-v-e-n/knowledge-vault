---
title: "Med-HALT — Javen Slides 9-15 Google Slides 布局规格"
type: source
tags: [ECE284, presentation, slide-layout, Javen 部分]
sources: [raw/AI/Med-HALT_Pal_2023/Pal_2023_MedHALT.pdf]
created: 2026-05-11
updated: 2026-05-11
priority: active
confidence: high
---

# Med-HALT — Slides 9-15 Google Slides 布局规格

> **用途**：你在 Google Slides 上 5 分钟 layout 完 7 张 slides 的 visual spec。每张含 ASCII mockup + 字号 + 颜色 + 防重叠规则。
> **相关**：[[Pal_2023_MedHALT_Javen_Part3_4_备稿]] 是口播 + Q&A; 本文件只管 **PPT 长啥样**。
> **Google Slides link**: https://docs.google.com/presentation/d/1OaDtrYwdM6FHO1KfbRfA-FvFD7NgMeqV2hjqUFxYedc/edit

---

## 📐 整体设计规则（**所有 slide 都遵守**）

### 字号下限（16:9 投影 + 教室后排能看）

| Element | 字号 (pt) | 何时用 |
|---|---|---|
| **主标题** (slide title) | **32-40 pt** bold | 每张顶部 |
| **副标题** / 重要 finding | **24-28 pt** bold | 强调句 |
| **正文 body** | **20-24 pt** | 表格 / bullet |
| **Caption / footer / 引用** | **16-18 pt** italic | 不重要文字 |
| **🔥 Big number / impact** | **60-100 pt** bold | 1-2 个超大数字 |

**绝对禁忌**：任何字小于 **16 pt**——后排同学看不清，被扣分。

### 防重叠规则（Javen 5/11 强调）

1. **每张 slide 总字数 ≤ 50 英文 word / 100 中文字**——超了就 split 成两张 slide 或砍内容
2. **元素之间留白 ≥ 20px**（Google Slides snap-to-grid 帮你 align）
3. **不要在同一行放超过 2 个大 element**（表 + 表 / 表 + 大字 OK；表 + 表 + 引用 = 挤）
4. **emoji / 颜色不要满天飞** —— 一张 slide ≤ 3 种颜色 + ≤ 4 个 emoji

### 颜色 palette（一致性）

| 颜色 | 用途 | Google Slides 选 | Hex |
|---|---|---|---|
| **黑** | 主体文字 | Default | #000000 |
| **深蓝** | 标题 + Paper 数字 | Custom blue | #1a3a6b |
| **红** | ❌ 失败 / hallucination 警示 | Custom red | #cc4c54 |
| **绿** | ✅ 安全 / 可行 | Custom green | #2d8a4e |
| **金** / **⭐** | 最佳数字 / 重点 | Custom amber | #d9a73c |

---

## 📊 Slide 9 — Three Surprises from the Leaderboard

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│   Three Surprises from the Leaderboard            ← 36pt bold     │
│   ─────────────────────────────────────                           │
│                                                                   │
│  ┌─────────────────────────────────┐  ┌──────────────────────┐    │
│  │ Model          | RHT   | MHT    │  │ RHT = Reasoning      │    │
│  │ ──────────────────────────────  │  │       Hallucination  │    │
│  │ LLaMA-2 70B    | 72.33 | 8.04   │← │       Test           │    │
│  │    Base        | ⭐    |        │  │   • FCT / NOTA / FQT │    │
│  │ LLaMA-2 70B    | 11.26 | 13.05  │  │   • 测推理时被骗     │    │
│  │    Chat        | ❌    |        │  │                      │    │
│  │ Text-Davinci   | 54.46 | 19.75  │  │ MHT = Memory         │    │
│  │ Falcon 40B     | 59.09 | 30.36⭐│  │       Hallucination  │    │
│  │ GPT-3.5 Turbo  | 44.48 | 19.96  │  │       Test           │    │
│  │                                 │  │   • PubMed retrieval │    │
│  │            (22 pt)              │  │   • 测能不能说       │    │
│  │                                 │  │     "Unknown"        │    │
│  └─────────────────────────────────┘  └──────────────────────┘    │
│      Simplified leaderboard (5 rows)        (18 pt body)          │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题** "Three Surprises from the Leaderboard"：36 pt bold 深蓝 #1a3a6b 顶部居中
- **左侧表** (60% 宽)：22 pt body / 24 pt header bold / **⭐ ❌ 大且彩** (32 pt)
- **右侧 recap** (35% 宽)：18 pt body / 22 pt RHT/MHT label bold
- **底部留白** 至少 10% (不要塞底部 footer)
- **不需要 visual figure**——表本身就是 visual

### 防挤 check

- ✅ 总文字 ~80 words——表占 50，recap 占 30
- ✅ 2 个 element 左右排（≤ 2 per row 规则）
- ✅ ⭐ ❌ 视觉重音，不依赖颜色——色盲也能区分

---

## 📊 Slide 10 — Surprise 1: Instruction-Tuning Paradox 🥇

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Surprise 1 — Instruction-Tuning Paradox       ← 36pt bold        │
│  ──────────────────────────────────────                           │
│                                                                   │
│  ┌───────────────────────────────┐  ┌────────────────────────┐    │
│  │                               │  │ Base vs Chat — 区别？  │    │
│  │  LLaMA-2 70B Base             │  │                        │    │
│  │     RHT 72%  ⭐               │  │ Base model             │    │
│  │       │                       │  │  = Pre-training 完就停 │    │
│  │       │  + Instruction Tuning │  │  → 不会对话            │    │
│  │       │  + RLHF               │  │                        │    │
│  │       ▼                       │  │ Chat model             │    │
│  │  LLaMA-2 70B Chat             │  │  = Base + SFT + RLHF   │    │
│  │     RHT 11%  ❌               │  │  → ChatGPT, Claude     │    │
│  │                               │  │                        │    │
│  │  同架构, 差 61 个百分点       │  │ ⚡ 同一架构, 只差     │    │
│  │  (30 pt for 数字)             │  │   最后两步训练        │    │
│  └───────────────────────────────┘  └────────────────────────┘    │
│                                                                   │
│  📄 Paper §6.1: "detrimental effect of instruction tuning"        │
│                  (16 pt italic 灰色)                              │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题**：36 pt bold 深蓝 顶部
- **左侧主对比** (55% 宽)：
  - "LLaMA-2 70B Base" + "RHT 72%" = 24 pt + 60 pt big number
  - 箭头 ↓ + "+SFT +RLHF" 标注 24 pt 红色
  - "LLaMA-2 70B Chat" + "RHT 11%" = 24 pt + 60 pt big number 红色
  - "差 61 个百分点" footer 24 pt bold
- **右侧 Base vs Chat block** (40% 宽)：20 pt body 黑色，"Base"/"Chat" label 22 pt bold
- **底部 paper 引用**：16 pt italic 灰色 (#666)，don't make it big — 它是 footnote 不是主体

### 防挤 check

- ✅ 总文字 ~70 words——主对比 20 + Base/Chat block 50
- ✅ 60 pt big number 让 "72%" "11%" 跳出来
- ✅ 红 vs 绿对比 (72=绿/11=红) 视觉直接
- ⚠️ Base vs Chat block 看起来文字多——用 ↓ 箭头分隔 "Base / Chat" 两块，**不要一整段连续文字**

---

## 📊 Slide 11 — Surprise 2: Reasoning ≠ Memory 🥈

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Surprise 2 — Reasoning ≠ Memory               ← 36pt bold        │
│  ──────────────────────────────────                               │
│                                                                   │
│  Reasoning and Memory are independent skills.   ← 24pt subtitle   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                  │  RHT (推理)    │  MHT (记忆)             │  │
│  │  ─────────────── │ ─────────────  │ ─────────────────────── │  │
│  │  LLaMA-2 70B     │  72%  ⭐      │   8%                    │  │
│  │                  │ (推理强)       │ (记忆弱)                │  │
│  │  ─────────────── │ ─────────────  │ ─────────────────────── │  │
│  │  Falcon 40B      │  59%          │  30%  ⭐                │  │
│  │                  │ (推理中)       │ (记忆强)                │  │
│  │                                                              │  │
│  │  (24 pt body, 32 pt for ⭐ row)                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  💡 Modular design: one model for reasoning, another for facts.   │
│      (20 pt italic 深蓝)                                          │
│                                                                   │
│  ─ Side note: open-source beats closed-source on RHT,             │
│    but mostly because closed models are RLHF'd (Surprise 1 again).│
│    (14 pt italic 灰色 #666)                                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题**：36 pt bold 深蓝
- **副标题** "Reasoning and Memory are independent skills"：24 pt bold 黑
- **主表** (90% 宽，居中)：24 pt body / 32 pt for ⭐ row / "推理强/弱" caption 20 pt 灰
- **Modular design take**：20 pt italic 深蓝（你的 critical insight）
- **Side note caveat**：14 pt italic 灰色（最低优先级，明确是 footnote 不是主 finding）

### 防挤 check

- ✅ 总文字 ~80 words——表占 40 + take 15 + caveat 25
- ✅ 表是**对角线 ⭐**（左上 LLaMA RHT / 右下 Falcon MHT）——视觉强
- ✅ caveat 用 14 pt 灰色明确"不重要"——避免抢主 finding 风头

---

## 📊 Slide 12 — Surprise 3: FCT 全军覆没 🥉

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Surprise 3 — FCT: Where Every Model Fails     ← 36pt bold        │
│  ────────────────────────────────────────                         │
│                                                                   │
│  🚨  No model passes 50%                       ← 32pt bold 红色   │
│                                                                   │
│  ┌──────────────────────────────────────┐                         │
│  │  False Confidence Test (FCT):        │                         │
│  │  ────────────────────────────────    │                         │
│  │  LLaMA-2 70B Base    42%  (best)     │                         │
│  │  GPT-3.5 Turbo       34%             │                         │
│  │  Falcon 40B Base     19%             │                         │
│  │  Text-Davinci-003    17%             │                         │
│  │  LLaMA-2 70B Chat    13%             │                         │
│  │  Falcon 40B Instruct  1%  (worst)    │                         │
│  │                                      │                         │
│  │  (24 pt body, 32 pt for best/worst)  │                         │
│  └──────────────────────────────────────┘                         │
│                                                                   │
│  💡 LLM amplifies the user's wrong assumption   ← 24pt bold       │
│     (confirmation bias amplifier)                                 │
│                                                                   │
│  ─ Recall Yixian's Lyme example — that was FCT in action.         │
│    (16 pt italic 灰色)                                            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题**：36 pt bold 深蓝
- **🚨 red banner** "No model passes 50%"：32 pt bold 红色 #cc4c54
- **FCT 排名表** (70% 宽)：24 pt body / 32 pt for best & worst row
- **你的 punch line** "LLM amplifies the user's wrong assumption"：24 pt bold 深蓝（你最 sharp 的 insight）
- **Lyme recall footnote**：16 pt italic 灰色

### 防挤 check

- ✅ 总文字 ~75 words——表 40 + headline 10 + insight 20 + footnote 5
- ✅ "🚨 No model passes 50%" **不要写在表内**——独立大字 banner
- ✅ 数字简化成整数（42% 不是 42.21%）——口语化 + 不挤

---

## 🔀 Part 3 → Part 4: 不需要 transition slide

**直接从 Slide 12 翻到 Slide 13**。台上说一句 "So — what does this mean for deploying these?" 即可，**不需要单独 slide**。

---

## 📊 Slide 13 — Clinical Implications

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Can we deploy this in hospitals?              ← 36pt bold        │
│  ──────────────────────────────                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  ❌    Autonomous diagnosis / treatment                     │  │
│  │       Best model only 72% RHT, FCT under 50%                │  │
│  │                                                             │  │
│  │  ❌    RLHF chat models for medical Q&A                     │  │
│  │       Instruction-Tuning Paradox (Chat: 11%)                │  │
│  │                                                             │  │
│  │  ✅    Literature search assist (with verification)         │  │
│  │       Falcon 30% MHT — limited but useful                   │  │
│  │                                                             │  │
│  │  ✅    Physician second-opinion                             │  │
│  │       Doctor must be in the loop                            │  │
│  │                                                             │  │
│  │  (❌✅ 48 pt big, 主文 24 pt bold, 副文 18 pt 灰)           │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
│         🩺  Augmentation, not Automation                          │
│              (36 pt bold 深蓝, centered)                          │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题**：36 pt bold
- **Scorecard 4 行**：
  - **❌ / ✅** 大 emoji 48 pt
  - 主 claim line：24 pt bold
  - "why" sub-line：18 pt 灰色 (#666) italic
  - ❌ 行用红色 #cc4c54 微弱背景；✅ 行用绿色 #2d8a4e 微弱背景（**透明度 90% 不要饱和**）
- **底部 punch line** "🩺 Augmentation, not Automation"：36 pt bold 深蓝居中（这是你 Part 4 的核心 message）

### 防挤 check

- ✅ 总文字 ~70 words——4 行 scorecard 60 + punch line 5
- ✅ 4 行各自之间留白 ≥ 30 px（防止 ❌/✅ 行挤）
- ✅ punch line 独立一栏底部——视觉重心明显

---

## 📊 Slide 14 — Limitations & Open Questions

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Limitations & Open Questions                  ← 36pt bold        │
│  ────────────────────────────                                     │
│                                                                   │
│  ┌─────────────────────────────┐ │ ┌────────────────────────────┐ │
│  │  📄 Paper acknowledges      │ │ │ 💡 My open questions       │ │
│  │  ─────────────────────────  │ │ │ ────────────────────────── │ │
│  │                             │ │ │                            │ │
│  │ 1. MCQ ≠ free-form          │ │ │ 5. IT-Paradox: paper shows │ │
│  │    clinical Q&A             │ │ │    "what" not "why"        │ │
│  │                             │ │ │    (needs ablation)        │ │
│  │ 2. Only 7 tasks             │ │ │                            │ │
│  │    (no planning / multimod) │ │ │ 6. Med-PaLM 2 NOT          │ │
│  │                             │ │ │    Med-HALT-ed — research  │ │
│  │ 3. Prompt brittleness       │ │ │    gap                     │ │
│  │    unsolved                 │ │ │                            │ │
│  │                             │ │ │ 7. Pointwise Score →       │ │
│  │ 4. GPT-4 / Claude           │ │ │    RLHF reward function?   │ │
│  │    not tested               │ │ │    (train honest LLMs)     │ │
│  │                             │ │ │                            │ │
│  │  (20 pt body, 24 pt header) │ │ │ (20 pt body, 24 pt header) │ │
│  └─────────────────────────────┘ │ └────────────────────────────┘ │
│                                  │                                │
│                            (verical separator line ⌇⌇⌇)           │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题**：36 pt bold
- **两栏布局**（Google Slides "Two Content" template）：
  - **左栏 header** "📄 Paper acknowledges"：24 pt bold 深蓝
  - **右栏 header** "💡 My open questions"：24 pt bold 深蓝
  - 每条 item：20 pt body / 数字 22 pt bold
- **中间分隔线**：浅灰色 vertical line，让 paper / my 视觉分离
- **不要在 slide 上写"paper 的"vs"我加的"过度细分**——左右栏 emoji + header 已经说清楚

### 防挤 check

- ✅ 总文字 ~90 words——两栏各 45
- ✅ 左 4 条 + 右 3 条 ——左栏行间距比右栏紧一点（4 vs 3 内容）
- ⚠️ 这页**信息密度最大**——口播时 visual point at left then right，**不要逐条念**

---

## 📊 Slide 15 — Discussion (你抛 2 个问题给同学)

### ASCII mockup

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│  Discussion                                    ← 44pt bold        │
│  ──────────                                                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                                                             │  │
│  │  Q1  (Clinical)                                             │  │
│  │  ─────────────                                              │  │
│  │  If you were the CMO of a hospital deciding whether to      │  │
│  │  deploy an LLM for physician second-opinion in radiology,   │  │
│  │  which finding from this paper would worry you the MOST —   │  │
│  │  the 17% FCT score, the LLaMA-Chat collapse, or prompt      │  │
│  │  brittleness? Why that one specifically?                    │  │
│  │                                                             │  │
│  │  (22 pt body, "MOST" + "Why that one" highlighted 24 pt)    │  │
│  │                                                             │  │
│  ├─────────────────────────────────────────────────────────────┤  │
│  │                                                             │  │
│  │  Q2  (Technical)                                            │  │
│  │  ──────────────                                             │  │
│  │  RLHF makes the chat model WORSE at hallucination control.  │  │
│  │  If you had a research budget — would you (a) fix RLHF      │  │
│  │  with a "honesty reward," (b) skip RLHF entirely for        │  │
│  │  medical models, or (c) do 2-stage training? Defend your    │  │
│  │  choice.                                                    │  │
│  │                                                             │  │
│  │  (22 pt body, "WORSE" + "(a)(b)(c)" highlighted bold)       │  │
│  │                                                             │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Layout 细节

- **标题** "Discussion"：44 pt bold 深蓝（**比其他 slide 稍大** — 标志阶段转换）
- **两个 question block**（垂直堆叠）：
  - Q1 label "Q1 (Clinical)"：26 pt bold 深蓝
  - Q1 body：22 pt 黑（强调词 "MOST" / "Why that one specifically?" 用 **bold + 24 pt**）
  - Q2 label "Q2 (Technical)"：26 pt bold 深蓝
  - Q2 body：22 pt 黑（强调词 "WORSE" / "(a)(b)(c)" 用 **bold**）
- **block 之间用横线分隔** — 视觉 separation
- **Q1 Q2 各 2-3 行问题 + 1 行追问** — 不要 4-5 行长问题

### 防挤 check

- ✅ 总文字 ~75 words——Q1 35 + Q2 40
- ✅ **不要把两个 questions 写成一段**——必须横线分隔
- ✅ "Why that one specifically?" / "Defend your choice." 用 bold 突出——告诉同学**这是追问 + 期望具体答案**

### Slide 15 的 facilitation tip（不在 slide 上，你台上做的）

- 抛完 Q1 → **停 5-8 秒** silence 让同学想（**不要怕沉默**）
- 没人主动答 → 点名："John, what's your take?"
- 听到回答 → **always follow up**："Why **that specifically**? What about the others?"
- 等 1-2 个同学发言后 → 切到 Q2
- 时间不够（每题最多 3-4 min discussion）→ 主动说 "Great points, let's move to the second question"

---

## ✅ 7 张 Slide 整体 check 表

| Slide | 主要 visual | 总字数 | 防挤 risk |
|---|---|---|---|
| 9 — Three Surprises | 5-row 简化表 + RHT/MHT recap block | ~80 words | Low |
| 10 — IT-Paradox | 大箭头对比 + Base/Chat 详解 block | ~70 words | Med (右块字密) |
| 11 — Reasoning ≠ Memory | 对角线 ⭐ 表 + take-away | ~80 words | Low |
| 12 — FCT 全军覆没 | 排名表 + 红字 banner + insight | ~75 words | Low |
| 13 — Clinical Implications | ❌❌✅✅ scorecard + punch line | ~70 words | Low |
| 14 — Limitations | 两栏 paper/my | ~90 words | **Med-High**（信息最密）|
| 15 — Discussion | 2 个 question blocks | ~75 words | Low |

**Highest density**: Slide 14 (两栏对比信息多)——保证两栏之间留白 ≥ 30 px + 用 ⌇ 分隔线。

---

## 🎯 5 分钟 layout workflow（你和 Yixian 在 Google Slides）

1. **打开** [共享 Slides](https://docs.google.com/presentation/d/1OaDtrYwdM6FHO1KfbRfA-FvFD7NgMeqV2hjqUFxYedc/edit)
2. **从 Slide 9 开始**——按上面 ASCII mockup layout：
   - 标题 → Insert text box → 设字号 36 pt + bold
   - 内容 → 按 ASCII 位置 → 设字号
   - 颜色 → 选 palette 里的 hex
3. **每张 slide 做完按 "Present"** F5——投影看 visual，**检查是不是有字重叠或太小**
4. **整 7 张做完总共应该 5-10 min**——如果某张 > 5 min，可能在过度设计
5. **跟 Yixian 同步**——她做 Slide 1-8，你做 9-15，**整套 15 张 slides**

如果做完发现哪张挤了 / 字小了，告诉我，我帮你重新 spec layout。
