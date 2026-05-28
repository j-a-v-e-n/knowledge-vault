---
title: "ECE175B Final Project — 进度 + 所有产出 snapshot"
type: snapshot
tags: [ECE175B, final-project, ADG, snapshot, UCSD, Spring2026]
created: 2026-05-28
purpose: "可直接喂给 Claude / GPT 的 self-contained context bundle，用于指挥后续工作"
status_source_files:
  - "MyBrain/projects/ece175b-adg/midterm_report.tex"
  - "/Users/javencao/Downloads/Attribute_Disentangled_Classifier_Free_Guidance_for_Fine_Grained_Controllable_Face_Generation_with_Diffusion_Models__2_ (1).pdf (midterm PDF 5/27 重下载)"
  - "/Users/javencao/Downloads/proposal.pdf (proposal PDF 5/27 重下载)"
  - "MyBrain/projects/ece175b-adg/PROJECT_BRIEF.md (5/18 — 已过时)"
  - "MyBrain/projects/ece175b-adg/results/cfg_baseline.png (5/8 真实训出来的，已肉眼确认是 CelebA 真人脸戴墨镜 16-grid)"
  - "Google Sheet 'ECE 175B Presentation time' (TA Ruiyi 5/18 分享)"
---

# ECE175B Final Project — Status Snapshot @ 2026-05-28

> 所有数字逐字摘自源文件（CLAUDE.md 规则 #1）。未知的地方标"未知 / I don't know"，不补造。

---

## 0. TL;DR (给收件 LLM 三句话)

1. **课程 final project 题目**：ADG = Attribute-Disentangled Guidance（per-attribute 拆 CFG 的 guidance scale w → w_k），CelebA 64×64，K=4 属性。
2. **midterm 已交 5/8**（PDF 真出 5 页，含 15-epoch 训练 + 两张 16-grid 样本图）；**final presentation 6/2、final report ~6/12**。
3. **关键约束**：Javen 昨晚 (5/27) 一度想 pivot 到一个独立项目 `adg-interference`（诊断分解 Δ_data/model/guidance），今天 (5/28) 决定**放弃 pivot**，回归原 ECE175B-ADG 路线；snapshot 只描述 ECE175B-ADG。

---

## 1. 课程 + Deadlines

| 项 | 内容 |
|---|---|
| 课程 | ECE175B: Deep Generative Models, Spring 2026, UCSD |
| Instructor | Pengtao Xie (`p1xie@ucsd.edu`) |
| TA | Ruiyi Zhang (`ruz048@ucsd.edu`) |
| Student | Javen Cao (`jacao@ucsd.edu`) |
| 课程评分 | HW × 3（各 10%）+ Project 70%（Proposal 10% + Midterm 20% + **Final 40%**） |
| **Final Presentation** | **2026-06-02 周二**（TA spreadsheet 确认，Javen 在 Jun 2 列） |
| **Final Report** | ~2026-06-12（proposal Week 10-11 推定） |
| Grace days 余额 | 4/5（HW2 用了 1 天） |
| Canvas | https://canvas.ucsd.edu/courses/74401 |

**距今 (2026-05-28)**：presentation **剩 5 天**，report **剩 ~15 天**。

---

## 2. 项目核心定位（一图看懂）

**问题**：标准 CFG 在多属性条件生成里用一个全局 `w` 同时控制所有属性，无法独立调每个属性的强度。

**ADG 公式**（midterm Eq. 2）：

```
标准 CFG (1 个 scale w):
    ε̃(x_t, y) = ε(x_t, ∅) + w · [ε(x_t, y) - ε(x_t, ∅)]

ADG (K 个 scales w_k):
    ε̃(x_t, y) = ε(x_t, ∅) + Σ_{k=1}^K w_k · [ε(x_t, y^(k)) - ε(x_t, ∅)]
```

其中 y^(k) 是只激活第 k 个属性、其他 K-1 个置 null 的 conditioning 向量。

**Contribution 三点**（proposal §5）：
1. **No additional training** — 单 multi-attribute 模型，不需要 K 个独立模型
2. **Continuous per-attribute intensity** — 每个 w_k ∈ ℝ
3. **Attribute negation** — w_k < 0 可以抑制属性

**关键 prior art**：Composable Diffusion (Liu et al. 2022) 公式形式相似，但他们训 K 个独立模型；ADG 用单模型，引入"attribute direction 是否在共享特征空间里近似线性独立"这个新实证问题。

---

## 3. 关键数字（**全部 verbatim from midterm_report.tex / PDF**）

### 3.1 任务设置

| 项 | 值 |
|---|---|
| Dataset | CelebA (`liu2015celeba`) |
| Resolution | 64 × 64 |
| K | 4 binary attributes |
| Attribute list | `Smiling`, `Eyeglasses`, `Male`, `Young` |
| Input shape | $x_0 \in \mathbb{R}^{64 \times 64 \times 3}$, $y \in \{0,1\}^4$ |

### 3.2 模型

| 项 | 值 |
|---|---|
| Backbone | diffusers UNet2DModel |
| `block_out_channels` | (64, 128, 256, 256) |
| Trainable params | **approximately 22M** |
| Attribute conditioning | class embeddings concatenated to timestep embedding, injected into each residual block |
| Diffusion | DDPM, T=1000 timesteps |
| Noise schedule | linear, β_1 = 1e-4 → β_T = 0.02 |
| Prediction target | ε (epsilon-prediction) |

### 3.3 训练

| 项 | 值 |
|---|---|
| Optimizer | AdamW |
| LR | 2e-4 |
| Batch size | 128 |
| Precision | mixed-precision fp16 |
| Hardware | single Tesla T4 GPU, Kaggle Notebooks |
| **Epochs trained** | **15 epochs total** (in 2 segments: **5 epochs initial + 10 epochs resumed from checkpoint**) |
| 中断原因 | Kaggle 9-hour GPU commit limit |
| Attribute dropout | p = 0.1（全 y → ∅，CFG 训练标配） |
| EMA | **未用**（"will be added for final evaluation"） |
| Checkpoint 频率 | per-epoch（含 model weights + optimizer state + best-loss tracking） |

### 3.4 Loss trajectory（midterm §4，verbatim）

| Epoch | Avg per-epoch loss |
|---|---|
| 0 | **0.0366** |
| 13 (best) | **0.0168** |
| 14 (final) | **0.0170** |
| Total reduction | **54%** |
| 收敛特性 | "monotonically decreasing through epoch 5 and exhibits expected diminishing returns thereafter" |

### 3.5 Sampling 配置 (midterm Fig 1/2)

| 配置 | Target y | Scales |
|---|---|---|
| **CFG baseline** (Fig 1) | [smile=1, glasses=1, male=0, young=1] | global w = 4.0 |
| **ADG strong glasses** (Fig 2) | 同上 | w = [w_smile=1, w_glasses=4, w_male=0, w_young=1] |
| Seed (两图) | 0 |
| Samples per fig | 16（4×4 grid） |

**Sampling cost**：DDPM 反扩散 T=1000 步；ADG 每步 K+1 forward pass（1 unconditional + K single-attribute），batched 成单次大 forward 提高 GPU 效率；CFG 每步 2 passes。

---

## 4. 所有产出（按 path 列）

### 4.1 已交 / 已固定的产出

| 文件 | Path | Size | 日期 | 状态 |
|---|---|---|---|---|
| **Proposal PDF** | `MyBrain/raw/ucsd/Spring 2026/ECE175B/proposal.pdf` | 116.9 KB | 2026-04-17 | ✅ 已交 4/22 |
| **Proposal PDF (重下)** | `~/Downloads/proposal.pdf` | 116.9 KB | 2026-05-27 | 与 vault 版本 byte-identical |
| **Midterm Report PDF** | `~/Downloads/Attribute_Disentangled_Classifier_Free_Guidance_for_Fine_Grained_Controllable_Face_Generation_with_Diffusion_Models__2_ (1).pdf` | 651.5 KB | 2026-05-27（重下载） | ✅ 已交 5/8（5 页） |
| Midterm tex 源 | `MyBrain/projects/ece175b-adg/midterm_report.tex` | 14.3 KB | 2026-05-08 16:03 | 与 PDF 一致 |
| Midterm bib | `MyBrain/projects/ece175b-adg/refs.bib` | 1.4 KB | 2026-05-08 15:56 | 5 条引用 |
| NeurIPS style | `MyBrain/projects/ece175b-adg/neurips_2024.sty` | 11.6 KB | — | — |

### 4.2 代码（vault 内，可 read 全文）

| File | Path | Size | 作用 |
|---|---|---|---|
| README | `MyBrain/projects/ece175b-adg/README.md` | 4.5 KB | 项目说明 |
| PROJECT_BRIEF | `MyBrain/projects/ece175b-adg/PROJECT_BRIEF.md` | 2.2 KB | **⚠️ 5/18 写的，已过时**（仍写"blocked on training"） |
| requirements | `MyBrain/projects/ece175b-adg/requirements.txt` | 194 B | — |
| `.gitignore` | `MyBrain/projects/ece175b-adg/.gitignore` | 379 B | 屏蔽 data/ checkpoints/ |
| **data.py** | `MyBrain/projects/ece175b-adg/data.py` | 4.1 KB | CelebA loader + attribute encoding（torchvision 版） |
| **model.py** | `MyBrain/projects/ece175b-adg/model.py` | 3.3 KB | `AttrConditionedUNet` wrapper（diffusers UNet2DModel + attribute MLP） |
| **ddpm.py** | `MyBrain/projects/ece175b-adg/ddpm.py` | 2.3 KB | scheduler / training_step / generic sample loop（注入 cond_fn） |
| **cfg.py** | `MyBrain/projects/ece175b-adg/cfg.py` | 1.2 KB | 标准 CFG 的 cond_fn |
| **adg.py** | `MyBrain/projects/ece175b-adg/adg.py` | 2.7 KB | **主贡献** — ADG 的 cond_fn，K+1 forward pass linear combine |
| **train.py** | `MyBrain/projects/ece175b-adg/train.py` | 3.9 KB | 入口；CelebA + conditional DDPM + dropout 0.1 |
| **sample.py** | `MyBrain/projects/ece175b-adg/sample.py` | 4.5 KB | 采样 + 可视化 + attribute sweep |
| **eval_fid.py** | `MyBrain/projects/ece175b-adg/eval_fid.py` | 4.6 KB | FID 评估（未实测） |
| **eval_disentangle.py** | `MyBrain/projects/ece175b-adg/eval_disentangle.py` | 6.4 KB | per-attribute classifier + 解耦度（未实测） |

### 4.3 Notebooks

| File | Path | Size | 状态 |
|---|---|---|---|
| Kaggle 训练 nb | `MyBrain/projects/ece175b-adg/notebooks/train_kaggle.ipynb` | 30 KB | **midterm 用的就是这个** (10 cells)，在 Kaggle 上跑通过 |
| Colab 训练 nb | `MyBrain/projects/ece175b-adg/notebooks/train_colab.ipynb` | 18 KB | 未用（备份方案） |
| Colab quickstart | `MyBrain/projects/ece175b-adg/notebooks/colab_quickstart.md` | 3.5 KB | Step-by-step（GUI 操作） |

### 4.4 训练 / 采样结果

| File | Path | Size | 内容 | 日期 |
|---|---|---|---|---|
| **CFG baseline 样本** | `MyBrain/projects/ece175b-adg/results/cfg_baseline.png` | 211 KB | 16 张 4×4 grid，target=[1,1,0,1], w=4.0, seed=0。**已肉眼验证：CelebA 真人脸戴墨镜，训练出来的真实结果** | 2026-05-08 15:13 |
| **ADG strong glasses 样本** | `MyBrain/projects/ece175b-adg/results/adg_strong_eyeglasses.png` | 211 KB | 16 张 4×4 grid，target 同上，w=[1,4,0,1], seed=0 | 2026-05-08 15:13 |
| **训练 checkpoints** | ❌ **未同步进 vault** | ~100 MB 估计 | best.pt + per-epoch ckpt 全在 Kaggle session output（`/kaggle/working/checkpoints/`）；本地 `MyBrain/projects/ece175b-adg/checkpoints/` 是空目录 | — |
| **训练 log** | ❌ 未同步进 vault | — | 同上，Kaggle session 内 | — |
| CelebA 数据 | ❌ 未同步进 vault（.gitignore）| ~1.4 GB | Kaggle 通过 Add Data → `jessicali9530/celeba-dataset` 挂载 | — |

⚠️ **关键 ops 问题**：checkpoint 在 Kaggle 上，要么需要重新挂 session 跑（commit/save output），要么从 Kaggle 下回本地。如果 session output 过期被清，需要重训。**建议立即去 Kaggle 看一下那个 notebook 的 output 还在不在**。

### 4.5 课程笔记 + 5/27 整门课快照

- `MyBrain/notes/ucsd/Spring 2026/ECE175B/ECE175B_Lecture1a/1b/2/3/4_*.md`（5 个讲座笔记）
- `MyBrain/notes/ucsd/Spring 2026/ECE175B/ECE175B_项目快照_2026-05-27.md` — 整门课快照（HW1/HW2/proposal/lecture），**注意里面"Midterm / Final Project: 尚未启动"已过时**
- `MyBrain/wiki/机器学习/ECE175B_概览.md`

---

## 5. Remaining Work（midterm §5 承诺要做的 4 件事，**全部未启动**）

| # | 任务 | 状态 | 工具/代码就绪？ |
|---|---|---|---|
| 1 | **FID** on held-out validation set | ❌ 未跑 | ✅ `eval_fid.py` 已写但未实测 |
| 2 | **Per-attribute classifier accuracy** (attribute fidelity) | ❌ 未跑 | ⚠️ `eval_disentangle.py` 写了，但 classifier 没训过/没接入 |
| 3 | **K×K cross-attribute interference matrix**（变一个 w_k 看其他 attribute 的 classifier confidence） | ❌ 未跑 | ⚠️ 同上 |
| 4 | **Failure mode analysis**：哪个 attribute pair 最纠缠？数据 bias 还是模型？ | ❌ 未跑 | — |
| 5 | **Compute cost profiling**：CFG (2 passes) vs ADG (K+1 passes) wall-clock | ❌ 未跑 | — |

外加 final report 自身：

| # | 任务 | 状态 |
|---|---|---|
| 6 | Final report PDF（NeurIPS 风格 7-10 页推测） | ❌ 未起笔 |
| 7 | GitHub repo 公开 + 链接交付 | ❌ 未启动 |
| 8 | **Final presentation slides**（6/2 演讲，~10 页推测） | ❌ 未起笔 |

---

## 6. 已知的 vault 状态不一致（要清理）

| 文件 | 问题 |
|---|---|
| `MyBrain/projects/ece175b-adg/PROJECT_BRIEF.md` | 5/18 写的 "⚠️ Blocker: Javen GUI 跑 Kaggle Free T4 training (Add Data → Run All)" — 实际训练 5/8 前已完成 15 epoch |
| `MyBrain/automation/queue/task-board.md` task-017 | 子任务 c (训练) / d (sampling) 还在 `[ ]`，实际已完成（midterm 已交那一刻这两件事就完成了）|
| `MyBrain/notes/ucsd/Spring 2026/ECE175B/ECE175B_项目快照_2026-05-27.md` §0 | "Midterm / Final Project: 尚未启动" — midterm 实际 5/8 已交 |
| task-board / PROJECT_BRIEF 都没记 | **6/2 presentation deadline**（TA Ruiyi 5/18 spreadsheet 才公布的）|

---

## 7. 被放弃的支线：`adg-interference`（5/28 决定放弃）

> 仅为完整性记录，**不要在 ECE175B final 工作里引入这个项目的产出**。

- **路径**：`~/Projects/adg-interference/`（vault 外，独立 git repo）
- **创建**：2026-05-27 22:46
- **触发**：Javen 读了 DCFG (Xia et al. 2025, arxiv 2506.14399)，判断 ADG 的 per-attribute CFG novelty 被 DCFG 的 group-wise mitigation 覆盖
- **重新框定**：换成"诊断分解 Δ_total = Δ_data + Δ_model(w=1) + Δ_guidance(w)"，pilot attributes 砍掉 young 改成 smile/male/eyeglasses
- **进度**：Phase 0 (measurement system validation)，classifier smoke test 还没完
- **5/28 决定**：放弃。ECE175B final 回归原 ADG proposal 不动。

如果未来要重新捡起，材料在那个 repo 里（plan.md / README.md / data/ / src/ / kaggle/）。

---

## 8. 给收件 LLM 的提问 / 决策点

请帮忙规划下面这几件事中你认为最关键的 2-3 件，并给出可执行步骤：

1. **6/2 presentation slides** 怎么搭（5 天）？10 页左右，可借 midterm 的两张图，但需要新增什么？
2. **Kaggle checkpoint 拯救方案**：现在 best.pt 还在 Kaggle session output。优先级 — 立刻去存？还是重训？
3. **Remaining Work §5 那 4 件事**，5-15 天能做几件？砍掉哪些是 safe 的？建议优先级：
   - FID 5000 samples ≈ 1.5h on T4 — should do
   - Per-attribute classifier 训练 ≈ 几小时 + interference matrix sweep — 核心 ADG contribution，should do
   - Failure mode + Compute profiling — nice-to-have
4. **Final report** 起稿策略：从 midterm tex 扩展，还是新框架？
5. **GitHub repo 公开**：什么时候 push，要不要把 checkpoint 也放？

**关于事实/数字的硬约束**：所有要写进报告 / slides / 给 Javen 看的数字必须 verbatim 从源文件抄（CLAUDE.md 规则 #1）。已锁定的数字见 §3。新数字需要先跑实验拿到。

---

## 9. 相关人物 / 联系

| 角色 | 名字 | 联系 |
|---|---|---|
| Instructor | Pengtao Xie | `p1xie@ucsd.edu` |
| TA | Ruiyi Zhang | `ruz048@ucsd.edu`（grace day 申请走他） |
| Student | Javen Cao | `jacao@ucsd.edu` |

---

## 10. Snapshot 元信息

- **生成日期**：2026-05-28
- **生成方式**：Claudian 主对话读 `midterm_report.tex` + `proposal.pdf` + `PROJECT_BRIEF.md` + ls vault `ece175b-adg/` + Drive search + ls `~/Projects/adg-interference/` 后整合
- **源文件 sanity check**：
  - midterm PDF 5 页内容与 `midterm_report.tex` 完全对齐
  - proposal PDF 3 页内容与 `MyBrain/raw/ucsd/Spring 2026/ECE175B/proposal.pdf` byte-identical（vault 那份和 Downloads 重下版本 119,743 bytes 一致）
  - results/ 两张 PNG 用 image read 确认是真训出的样本（不是占位图）
- **未确认的部分**（"I don't know"）：
  - Final report 具体页数限制（推测 7-10 页 NeurIPS 风格，未在 proposal/midterm 任何源文件明文写出）
  - Final presentation 时长（spreadsheet 无时长信息）
  - HW3 是否存在 / 是否已发布
  - Kaggle session output 是否还活着（需 Javen 去 Kaggle 看一眼）
