---
title: "ECE175B-ADG Checkpoint Manifest — Kaggle 5/13 run"
created: 2026-05-28
type: manifest
note: "本文件仅是 .pt 清单 + metadata。.pt 本体不入 vault，全部在系统盘绝对路径。"
---

# Checkpoint Manifest

## 物理位置（vault 外）

所有 17 个 `.pt` 文件本体位于本机系统盘：

```
/Users/javencao/Projects/ece175b-adg-artifacts/checkpoints/
```

总占用 **~4.85 GB**（17 × 约 291 MB），未同步 Google Drive。

## 来源

- **Kaggle session**: `javencao321/notebook5850c92f07`
- **Last run**: 2026-05-13 21:58:21 PT
- **Hardware**: NvidiaTeslaT4, fp16, batch=128
- **数字金标准源**: `training_log.log`（同目录, 19,426 行 Kaggle session log）
- **训练过程**: 一次跑完 15 epoch（log 显示 `🆕 Training from scratch.`），**非** midterm PDF 所写 "5+10 两段"
- **总训练时长**: 19,239 秒 ≈ 5.3 小时

## Checkpoint 清单

`epoch` 和 `best_loss` 字段由 `torch.load` 直接抽取；`per_epoch_avg_loss` 来自 `training_log.log` grep。

`best_loss` 字段含义：**save 那一刻为止历史最低 avg loss**（不是该 epoch 自身 loss）。所以 epoch 13 之后字段冻在 `0.016772636761933`。

| File | Size | `epoch` 字段 | `best_loss` 字段 | per-epoch avg (from log) | 标记 |
|---|---|---|---|---|---|
| `ckpt_epoch001.pt` | 290.7 MB | 0 | 0.035907149 | **0.0359** | ⭐ 第一次最低 |
| `ckpt_epoch002.pt` | 290.7 MB | 1 | 0.020336267 | **0.0203** | ⭐ best |
| `ckpt_epoch003.pt` | 290.7 MB | 2 | 0.018853770 | **0.0189** | ⭐ best |
| `ckpt_epoch004.pt` | 290.7 MB | 3 | 0.018560469 | **0.0186** | ⭐ best |
| `ckpt_epoch005.pt` | 290.7 MB | 4 | 0.018110638 | **0.0181** | ⭐ best |
| `ckpt_epoch006.pt` | 290.7 MB | 5 | 0.017914295 | **0.0179** | ⭐ best |
| `ckpt_epoch007.pt` | 290.7 MB | 6 | 0.017768785 | **0.0178** | ⭐ best |
| `ckpt_epoch008.pt` | 290.7 MB | 7 | 0.017353041 | **0.0174** | ⭐ best |
| `ckpt_epoch009.pt` | 290.7 MB | 8 | 0.017298569 | **0.0173** | ⭐ best |
| `ckpt_epoch010.pt` | 290.7 MB | 9 | 0.017137543 | **0.0171** | ⭐ best |
| `ckpt_epoch011.pt` | 290.7 MB | 10 | 0.017137543 | 0.0172 | — (no improvement) |
| `ckpt_epoch012.pt` | 290.7 MB | 11 | 0.016991046 | **0.0170** | ⭐ best |
| `ckpt_epoch013.pt` | 290.7 MB | 12 | 0.016871835 | **0.0169** | ⭐ best |
| `ckpt_epoch014.pt` | 290.7 MB | 13 | **0.016772637** | **0.0168** | ⭐⭐ **best (last)** |
| `ckpt_epoch015.pt` | 290.7 MB | 14 | 0.016772637 | 0.0170 | — (final epoch, no improvement) |
| `best_loss.pt` | 290.7 MB | 13 | 0.016772637 | (同 ckpt_epoch014 内容) | 🏆 **真正的 best** |
| `best.pt` | 290.6 MB | 14 | 0.016772637 | (同 ckpt_epoch015 内容) | "latest" (= 最终 epoch) |

注：`best.pt` 是 train.py 在每 epoch 结束时覆盖写的"最新 state"（不是真正的 best 模型），`best_loss.pt` 才是 best loss epoch 触发时 save 的快照。

## Final report 用哪个？

**建议：`best_loss.pt`**

理由：
- epoch=13、avg_loss=0.0168，跟 midterm PDF §4 写的 "minimum of 0.0168 at epoch 13" **完全一致**
- 用 best_loss 不用 last_epoch 是 ML 报告通行做法（避免 overfitting 的 last epoch）
- A3 已验证可 load + sample，出 CelebA 面部 + 戴墨镜 + 女性 + 微笑

## A3 验证记录（2026-05-28）

- **脚本**: `/Users/javencao/Projects/ece175b-adg-artifacts/A3_smoke.py`
- **设备**: MPS（macOS）
- **Sampler**: DDIM 50 steps（求快，非 final 评估）
- **CFG**: w=4.0, target=[smile=1, glasses=1, male=0, young=1], seed=0, N=4
- **架构 load 结果**: `missing=0, unexpected=0` strict match
- **sample loop**: 6.6 秒
- **输出 PNG**: `/Users/javencao/Projects/ece175b-adg-artifacts/A3_smoke_cfg_w4_best_loss.png`
- **视觉判定**: ✅ 4 张全部 CelebA 面部 + 墨镜 + 微笑 + 偏 female + 偏 young，与 target 一致

## ⚠️ 跟 midterm PDF 不一致的事实

供 final report 修订时参考（必改）：

| 项 | PDF §3 写的 | Log 实测 | 处理 |
|---|---|---|---|
| Model trainable params | "approximately 22M" | **25.37M** | 改 |
| Epoch 0 avg loss | 0.0366 | 0.0359 | 改 |
| 训练分段叙述 | "5 epochs initial + 10 epochs resumed from checkpoint" | log 显示 `🆕 Training from scratch.` + 一次性 15 epoch | 改 |
| Epoch 13 best loss | 0.0168 ✅ | 0.0168 ✓ | 一致 |
| Epoch 14 final loss | 0.0170 ✅ | 0.0170 ✓ | 一致 |
| Total reduction | 54% | (0.0359-0.0168)/0.0359 = 53.2% ≈ 54% | 一致（近似） |
