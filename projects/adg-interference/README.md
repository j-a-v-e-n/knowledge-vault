# ADG-Interference

研究 multi-attribute conditional diffusion model 中 attribute interference
的来源分解。

## 核心问题

当 CFG guidance 同时控制多个属性时，attribute 之间会互相干扰——
例如调整 smiling 会影响 male 的预测概率。这种干扰来自哪里？
是数据本来就相关，还是模型/sampling 引入的额外纠缠？

## 分解框架

我们把多属性 conditional generation 中的总 interference 分解为三项：

    Δ_total(w) = Δ_data + Δ_model(w=1) + Δ_guidance(w)

- **Δ_data**: CelebA 训练集中 attribute 之间的真实相关性
- **Δ_model(w=1)**: 模型在无 guidance 时（w=1）引入的偏差
- **Δ_guidance(w)**: CFG scale > 1 放大引入的额外干扰

## Spurious interference

    Δ_spurious = Δ_total - Δ_data

为避免 label noise 和 measurement-system mismatch，主测量公式是
apples-to-apples 版本：

    Δ_spurious = Δ_clf_on_generated - Δ_clf_on_real

即用同一个 classifier 分别在生成图像和真实图像上算 attribute correlation，
两者之差即为模型/sampling 引入的额外干扰。

## 数据集 / 模型

- **Dataset**: CelebA / CelebA-HQ
- **Pilot attributes**: smiling, male, eyeglasses（避开 young——label consistency 低）
- **Classifier**: ResNet-50 + ViT (clementapa/CelebFaces_Attributes_Classification)
  - 双 backbone 用于 cross-check measurement robustness
- **Diffusion**: TBD（DCFG 未公开 code，主要候选是 finetune 现有 unconditional checkpoint）

## 关键 prior art

- **CFG** (Ho & Salimans 2022): 单一全局 guidance scale 的标准做法
- **DCFG** (Xia et al. 2025, arxiv 2506.14399): group-wise conditioning control，
  attribute-split embedding，counterfactual generation。我们的工作不在 mitigation
  algorithm 上竞争，而在 diagnostic decomposition 上互补。
- **Giambi & Lisanti 2023**: multi-conditioning via cross-attention（attributes + masks）
- **Composable Diffusion** (Liu et al. 2022): per-concept weights，但是 multi-model
  setting，假设属性独立

## 我们的 contribution（暂定）

1. 一个**诊断分解 framework**，把 attribute interference 拆成 data / model / guidance
   三个来源——可在不重训模型的前提下 operationalize
2. **实证刻画**: 在 CelebA 上展示各来源的相对大小、哪些 attribute pair 由哪个来源主导、
   随 w 如何变化
3. **来源自适应 mitigation 策略**: 根据诊断结果选择对应 intervention——和 DCFG 类
   group-wise 统一处理在切入轴上不同

## 工具栈

- **执行**: Claudian (Obsidian plugin) + Claude Code / Codex backend
- **算力**: Kaggle 免费 GPU (P100/T4, 30h/week)
- **环境**: conda env `adg` (Python 3.11)
- **知识库**: 本 vault 的 papers/ 和 notes/

## 项目结构

    adg-interference/
    ├── README.md          # 本文件
    ├── plan.md            # 决策日志 + phase 计划
    ├── requirements.txt
    ├── kaggle/notebooks/  # 推送到 Kaggle 的 .ipynb
    ├── src/               # 共享 Python 模块
    ├── scripts/           # 环境激活等辅助脚本
    ├── results/
    │   ├── tables/        # 实验结果 (JSON / CSV)
    │   └── figures/       # 图表
    ├── papers/            # 相关 paper PDF
    └── notes/             # 阅读笔记 / 想法

## Status

Phase 0 (measurement system validation) - 进行中
