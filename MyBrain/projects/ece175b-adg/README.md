# ECE 175B — Attribute-Disentangled Guidance (ADG) for Diffusion Models

> Spring 2026 final project. Author: Javen Cao. Course: ECE 175B — Deep Generative Models.

## 项目目标

把标准 Classifier-Free Guidance (CFG) 的**单一 guidance scale `w`** 拆解为
**K 个 per-attribute 的 `w_k`**,让多属性条件生成中每个 attribute 有独立强度控制。

**数学**:

```
标准 CFG:   ε̃(x_t, y) = ε(x_t, ∅) + w · [ε(x_t, y) - ε(x_t, ∅)]
我们的 ADG: ε̃(x_t, y) = ε(x_t, ∅) + Σ_k w_k · [ε(x_t, y^(k)) - ε(x_t, ∅)]
```

其中 `y^(k)` 是只激活第 k 个 attribute 的 conditioning 向量。

详见 `../../raw/ucsd/Spring 2026/ECE175B/proposal.pdf`。

## 文件结构

```
ece175b-adg/
├── README.md              ← 你在看
├── requirements.txt
├── .gitignore
├── data.py                ← CelebA 加载 + attribute encoding
├── model.py               ← Conditional UNet (用 diffusers UNet2DModel)
├── ddpm.py                ← DDPM forward / reverse / training step
├── cfg.py                 ← 标准 CFG sampling
├── adg.py                 ← ADG sampling (主贡献)
├── train.py               ← 训练入口
├── sample.py              ← 采样 + 可视化
├── eval_fid.py            ← FID 评估
├── eval_disentangle.py    ← per-attribute 准确率 + 解耦度
├── notebooks/             ← Colab notebook (Javen 用 Colab Pro 跑)
│   └── train_colab.ipynb
├── data/                  ← .gitignore — CelebA (~1.4 GB)
├── checkpoints/           ← .gitignore — model weights (~100 MB)
└── results/               ← FID curves / sample grids / 解耦图
```

## 跑起来 (在 Colab Pro / 本机 GPU)

### 1. 装依赖

```bash
pip install -r requirements.txt
```

### 2. 下数据

CelebA 通过 `torchvision.datasets.CelebA` 自动下,首次运行会用 ~1.4 GB。
若 torchvision 下载受限,从 [Kaggle CelebA](https://www.kaggle.com/datasets/jessicali9530/celeba-dataset) 手动下到 `data/celeba/`。

### 3. 训练 (Colab Pro)

```bash
# 4-attribute 子集: smiling, eyeglasses, male, young
# 64×64 分辨率, 50 epochs, 大约 4-6h on A100
python train.py --attrs smiling eyeglasses male young --resolution 64 --epochs 50 --batch-size 128
```

或在 Colab 打开 `notebooks/train_colab.ipynb`,接挂 Drive 直接 run。

### 4. 采样可视化

```bash
# 标准 CFG (单一 w)
python sample.py --method cfg --w 4.0 --seed 0 --out results/cfg_w4.png

# ADG (per-attribute w_k)
python sample.py --method adg --w 1 4 0 0 --seed 0 --out results/adg_smile_strong.png
# 解释: w_smiling=1, w_eyeglasses=4 (强), w_male=0, w_young=0

# 解耦实验: 固定其他, 扫描 w_eyeglasses 0→6
python sample.py --method adg --sweep eyeglasses 0 6 7 --seed 0 --out results/sweep_eyeglasses.png
```

### 5. 评估

```bash
python eval_fid.py --checkpoint checkpoints/best.pt --n-samples 5000
python eval_disentangle.py --checkpoint checkpoints/best.pt
```

## Timeline 对照 proposal

| Week | 任务 | 状态 |
|---|---|---|
| 1-2 | Lit review + codebase + CelebA | ✅ proposal 4/22 done, codebase 4/30 done |
| 3-4 | Train baseline conditional DDPM | ⏳ blocked on @javen — GPU 方案 |
| 5-6 | Implement ADG + 初步实验 | ⏳ |
| **7** | **Midterm report** (model design, math, initial results) | ⏳ ~5/13 |
| 8-9 | Systematic eval: FID, per-attr accuracy, disentanglement | ⏳ |
| 10-11 | Failure mode analysis + Final report | ⏳ ~6/12 |

## AI 协作模式

- **代码**: 主对话 Claude 写完整 (本文件夹)
- **训练**: ⚠️ blocked on @javen — 必须有外部 GPU (Colab Pro 推荐). 一旦解决,代码上传 Colab 直接跑
- **评估 + 可视化**: 训完 checkpoint 给我或 daemon, 自动跑 FID + sample grid
- **写报告**: daemon 凌晨可起草 midterm/final report 第一版,Javen 审

## 设计决策记录

- **64×64 分辨率**: proposal §4 明确选这个,降 K+1 forward pass 的成本
- **K=4 attributes**: smiling / eyeglasses / male / young — CelebA 里这 4 个标注质量最高 + 语义独立
- **UNet from diffusers**: 不自造轮子,用 huggingface diffusers 的 `UNet2DModel`,省时间
- **DDPMScheduler**: 同上,用 diffusers 的 1000-step linear schedule
- **Attribute dropout 概率 0.1**: CFG 训练标配
- **ADG 实现**: K+1 个 forward pass, 每个用单 attribute one-hot, 在 noise prediction 空间做线性组合
