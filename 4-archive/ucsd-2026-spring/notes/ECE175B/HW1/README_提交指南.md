---
title: ECE175B HW1 — 已完成，可直接提交
created: 2026-04-20
status: ready-to-submit
---

# ECE175B HW1 — ✅ 已完成

## 🎯 直接提交这个文件

**[unistory.pdf](./unistory.pdf)** — 2 页 NeurIPS 格式，249 KB

包含：
- ✅ 1-2 页 NeurIPS 格式（精准 2 页）
- ✅ Figure 1 架构图
- ✅ 4 个关键公式（LM / Diffusion / Align / Total）+ CFG 推理公式
- ✅ 训练策略（两阶段）
- ✅ 5 篇参考文献

---

## ✏️ 提交前只需确认一件事

打开 `unistory.pdf`，检查姓名和邮箱正确：

- **Javen Cao**
- **jacao@ucsd.edu**

如需修改（比如加学号），编辑 `unistory.tex` 里的 `\author{...}` 部分，然后让 Claude 重新编译。

---

## 📁 本文件夹所有文件

| 文件 | 作用 |
|------|------|
| **`unistory.pdf`** ⭐ | **最终提交文件** |
| `unistory.tex` | LaTeX 源文件（修改内容用） |
| `unistory.bib` | BibTeX 参考文献 |
| `unistory_architecture.png` | 架构图（已嵌入 PDF） |
| `neurips_2024.sty` | NeurIPS 官方样式 |
| `make_figure.py` | 架构图生成脚本（改图用） |

---

## 🔄 如果要修改内容

修改 `.tex` 后，重新编译：

```bash
cd "/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/inbox/ECE175B_HW1_files"
tectonic unistory.tex
```

（`tectonic` 是我给你装的轻量 LaTeX 编译器，在 `/opt/homebrew/bin/tectonic`）

改架构图：编辑 `make_figure.py`，然后：
```bash
python3 make_figure.py && tectonic unistory.tex
```

---

## 🧠 这次我做了什么

| 步骤 | 工具 |
|------|------|
| 搜最新研究 | WebSearch + WebFetch |
| 沉淀到 vault | 已存 `MyBrain/raw/web-research/2026-04-20_多模态故事生成研究.md` |
| 设计模型 | 综合课程知识 + 最新 Transfusion 思路 |
| 画架构图 | Python + matplotlib |
| 写 LaTeX 源 | 直接生成 |
| 写 BibTeX | 直接生成 |
| 装 LaTeX 编译器 | `brew install tectonic`（50MB，一次性）|
| 下载 NeurIPS 样式 | curl from GitHub |
| 编译 PDF | `tectonic unistory.tex` |
| 压缩到 2 页 | 多轮微调图片大小、参考文献字号、删减次要引用 |

整个流程**零手工操作**。
