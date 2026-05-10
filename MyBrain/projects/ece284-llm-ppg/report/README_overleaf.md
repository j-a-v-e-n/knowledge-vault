# ECE 284 Project Update Report — Overleaf compile guide

## 提交流程（10 分钟）

1. 打开 https://www.overleaf.com → 登录 → **New Project → Upload Project**
2. 上传 `update_report.zip`（在父目录 `MyBrain/projects/ece284-llm-ppg/`）
3. 进入项目后 main file 应该自动识别 `update_report.tex`；如果没有，左上角点击文件名 → 设为 main
4. 右上角 **Recompile** → 等 10 秒应该出 PDF
5. 如果第一次 compile 报错说 `acmart.cls not found` —— Overleaf 应该自带 ACM 模板；如果真没有：
   - Overleaf "Menu (左上)" → "Settings" → "TeX Live version" 选最新（通常 2024+ 自带 acmart）
6. PDF 看起来：约 2 页正文 + 1 页 references。**syllabus 要求 2 页** —— 如果超出 1 页 references 不算就 OK；如果正文超 2 页通知我裁剪
7. 下载 PDF → 上传 Canvas → 提交

## 文件清单

- `update_report.tex` — 主 LaTeX 文档（ACM Large 2-column, sigconf style）
- `references.bib` — 6 条引用
- `architecture.pdf` — Figure 1（system architecture, full-width 跨双列）
- `baselines_comparison.pdf` — Figure 2（per-subject + motion regime boxplot）
- `pilot_subj1_comparison.pdf` — Figure 3（30-window pilot: 3 systems + λ choice）

## 万一 Overleaf 编译错误

最可能的 2 种 + 解法：

| 错误 | 原因 | 解法 |
|---|---|---|
| `! LaTeX Error: File acmart.cls not found.` | TeX Live 版本太旧 | Menu → Settings → TeX Live 选 2024 或 2023 |
| `! Package Fontenc Error: Encoding file T1...` | encoding 包缺 | 把 .tex 第 14 行 `\usepackage[T1]{fontenc}` 删掉 |

如果有别的报错，截图发我，我远程修。

## 不要做的事

- **不要本地装 LaTeX**——你 Mac 没装 pdflatex（5/10 我 verify 过），用 Overleaf 是最快的
- 不要改 figure 路径——三个 .pdf 跟 .tex 在同一文件夹内，相对引用就 work

## AI use disclosure（已写在论文里）

按 syllabus 要求，已经在论文 §"AI-tool disclosure" 段落明确说明：
- 代码主要 AI 生成 + 你审
- Report 主要 AI draft + 你审
- 实验数据 / MAE / cost 数字全部 verify 过 results/*.json

如果教授事后追问，所有数字都能从 vault `MyBrain/projects/ece284-llm-ppg/results/` 复现。
