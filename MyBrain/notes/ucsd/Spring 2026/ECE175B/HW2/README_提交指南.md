---
title: ECE175B HW2 提交指南
type: source
tags: [ECE175B, HW2, VAE]
created: 2026-05-13
updated: 2026-05-13
confidence: high
priority: active
---

# ECE175B HW2 — VAE on Chest X-ray 提交指南

> **Deadline**: 2026-05-13 23:59 PT (已用 1 grace day,余 4 天 — 见 `../grace-days.md`)
> **要交的**: 1 个 PDF (2 页 NeurIPS 格式) → Gradescope

## 文件清单 (本目录)

| 文件                           | 用途                             |
| ---------------------------- | ------------------------------ |
| `Homework_2.pdf`             | 作业原始要求                         |
| `VAE_ChestXray_Kaggle.ipynb` | **Kaggle notebook** — 一键跑训练+评估 |
| `train_vae_chest_xray.py`    | 同样代码的 .py 版本 (本地跑用)            |
| `report.tex`                 | NeurIPS 报告模板 (有 4 个占位符待填)      |
| `neurips_2024.sty`           | NeurIPS LaTeX 样式               |
| `README_提交指南.md`             | 本文件                            |

## 流程 — 大概 1 小时你的时间 + 30-45 分钟 Kaggle 跑训练

### 第 1 步: Kaggle 跑训练 (10 分钟点击 + 30-45 分钟挂着)

1. 打开 [Kaggle](https://www.kaggle.com) → 登录
2. 右上角 **+** → **New Notebook**
3. 左上 **File** → **Import Notebook** → 上传 `VAE_ChestXray_Kaggle.ipynb`
4. 右侧栏 **+ Add Data** → 搜索 `chest-xray-pneumonia` → **Add** ([paultimothymooney 那个](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia))
5. 右侧栏 **Settings** → Accelerator = **GPU T4 x2** (免费)
6. 点上方 **Save Version** → 选 **Save & Run All (Commit)** → Save
7. 等 30-45 分钟跑完 (期间可以关 tab,Kaggle 后台跑)

### 第 2 步: 下载产物

跑完后在 notebook 页面右侧栏 **Output** tab,下载到本地:
- `loss_curve.png`
- `samples.png`
- `metrics.json` ← 看这个文件拿 4 个数字 (见下)

把 3 个文件放到本目录(HW2/)下,跟 `report.tex` 同级。

### 第 3 步: 填报告 4 个占位符

打开 `metrics.json`,你会看到类似:
```json
{
  "fid": 187.42,
  "inception_score": 2.34,
  "final_loss": 412.5,
  "n_images_train": 5856,
  "n_params_million": 2.81,
  "wall_time_minutes": 38.2,
  ...
}
```

在 `report.tex` 里搜索并替换这 5 个 `\mathbf{...}` 占位符 (用 sed 或编辑器):

| 占位符 | 用 `metrics.json` 里的字段 |
|---|---|
| `\mathbf{NIMAGES}` | `n_images_train` (例: `5856`) |
| `\mathbf{NPARAMS}` | `n_params_million` (例: `2.81`) |
| `\mathbf{WALLTIME}` | `wall_time_minutes` (例: `38`) |
| `\mathbf{ISVAL}` | `inception_score` (例: `2.34`) |
| `\mathbf{FIDVAL}` | `fid` (例: `187.42`) |

一行 sed 全搞定 (在本目录跑):
```bash
M=metrics.json
NI=$(jq -r .n_images_train $M); NP=$(jq -r .n_params_million $M)
WT=$(jq -r .wall_time_minutes $M | cut -d. -f1)
IS=$(jq -r .inception_score $M); FID=$(jq -r .fid $M)
sed -i '' \
  -e "s|\\\\mathbf{NIMAGES}|$NI|g" \
  -e "s|\\\\mathbf{NPARAMS}|$NP|g" \
  -e "s|\\\\mathbf{WALLTIME}|$WT|g" \
  -e "s|\\\\mathbf{ISVAL}|$IS|g" \
  -e "s|\\\\mathbf{FIDVAL}|$FID|g" \
  report.tex
echo "done"
```

### 第 4 步: 编译 PDF

**Overleaf** (最简单):
1. 打开 [Overleaf](https://overleaf.com) → New Project → Upload Project
2. 把整个 HW2 文件夹打 zip,上传 (排除 `Homework_2.pdf` 和 `README_提交指南.md`)
3. 主文件设为 `report.tex` → Recompile

**本地 LaTeX**:
```bash
pdflatex report.tex && pdflatex report.tex
```

→ 得到 `report.pdf`,确认是 2 页。

### 第 5 步: 提交 Gradescope

1. 登录 [Gradescope](https://www.gradescope.com)
2. ECE175B 课程 → HW2 → Submit
3. 上传 `report.pdf`
4. ✅ 完成

## 如果时间真的不够 — 应急方案

**方案 B (放弃 FID/IS,只报训练 loss + samples)**: 在 notebook 里跳过最后一个 cell (FID/IS),只跑训练 + 采样。报告里把 metrics 表格删掉,改成简短一段"computational constraint, omitted IS/FID"。损失大概 10-15% 分数,但 0% 比 75% 强 (24h late).

**方案 C (再用 1 个 grace day)**: 推到 5/14 23:59,余 3 天。需要再给 TA 发邮件 `ruz048@ucsd.edu`,模板:
```
Subject: ECE175B HW2 — Using 1 more grace day

Hi Ruiyi,

I'm using one additional grace day on HW2 (now using 2 total).
New submission deadline: 5/14 23:59 PT.
Remaining balance: 3 grace days.

Thanks,
Javen Cao (A12345678)
```
然后更新 `../grace-days.md`.

## 调试 / 跑歪了

- **OOM error (out of memory)**: 把 `BATCH = 128` 改成 `64`
- **跑得太慢 (>1h)**: 把 `EPOCHS = 30` 改成 `20`
- **FID 出错 (pytorch-ignite 装不上)**: 在第 1 个 cell 加 `!pip install -q pytorch-ignite` 在最开头
- **采样图全黑/全白**: 训练有问题,看 loss curve 是不是 NaN

## 参考

- [paultimothymooney/chest-xray-pneumonia](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) — Kaggle 数据集
- [pytorch-ignite FID/IS recipe](https://pytorch-ignite.ai/blog/gan-evaluation-with-fid-and-is/)
- [VAE original paper (Kingma & Welling 2014)](https://arxiv.org/abs/1312.6114)
- [Grace day tracker](../grace-days.md) — 当前余 4 天 (用 1 天后)

## 🔗 关联

- [[ECE175B_概览]]
- [[ECE175B_Lecture2_变分自编码器设计]]
- [[ECE175B_Lecture3_变分推断与ELBO]]
