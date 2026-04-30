# ECE 284 — Benchmarking LLM Paradigms for Wearable PPG HR Estimation

> Spring 2026 final project. Author: Javen Cao. Course: ECE 284 — Digital Health Technologies.

## 项目目标

在 IEEE SPC 2015 数据集上对比 4 个心率估计系统在运动伪迹下的表现:

| 系统 | 类型 | 说明 |
|---|---|---|
| **TROIKA-lite** | 信号处理 baseline | bandpass + FFT + 频谱减法 + peak detect |
| **Random Forest** | ML baseline | 4 个频域特征 + sklearn |
| **Claude λ-generator** | **主贡献** | LLM 生成 per-window spectral-subtraction weight λ,driving fixed pipeline |
| **Claude ReAct** *(stretch)* | LLM orchestrator | LLM 动态调用工具,跟 λ-generator 头对头对比 |

详见 `../../raw/ucsd/Spring 2026/ECE284/proposal_javen_revised.pdf`。

## 文件结构

```
ece284-llm-ppg/
├── README.md              ← 你在看
├── requirements.txt       ← Python 依赖
├── .gitignore
├── data.py                ← IEEE SPC 2015 加载 + 8s 窗口切分
├── troika_lite.py         ← 信号处理 baseline (Route A)
├── rf_baseline.py         ← Random Forest baseline (Route B)
├── llm_lambda.py          ← Claude λ generator (Route C, 主贡献)
├── react_agent.py         ← Claude ReAct (Route D, stretch)
├── evaluate.py            ← LOSO 交叉验证 + 4 个评估轴
├── run_all.py             ← 端到端跑全部实验 + 写报告
├── data/                  ← .gitignore — IEEE SPC 数据集 (~50MB)
├── results/               ← 实验输出 (csv / png / json)
└── configs/               ← prompt 模板 / 超参 / API key 路径
```

## 怎么跑

### 1. 装依赖

```bash
pip install --user -r requirements.txt
```

### 2. 下数据

```bash
# IEEE SPC 2015 — Zhang TROIKA paper dataset
# 12 subjects, treadmill running, PPG + accel + ECG @ 125Hz
mkdir -p data && cd data
curl -L -o ieee-spc-2015.zip "https://zenodo.org/record/3902710/files/IEEE-SPC-2015.zip"
unzip ieee-spc-2015.zip && cd ..
```

> ⚠️ Zenodo URL 待 Javen 批准后我去验证(proposal 引文是 Zhang 2015 但具体 DOI 要查)。备选:dataset 也常通过 PhysioNet 镜像。

### 3. Anthropic API key

```bash
mkdir -p ~/.config/anthropic-keys
echo "sk-ant-api03-XXX..." > ~/.config/anthropic-keys/ece284
chmod 600 ~/.config/anthropic-keys/ece284
```

代码自动读 `ANTHROPIC_API_KEY` 环境变量,或从该路径读。

### 4. 一键跑

```bash
# 单个 baseline 测试
python troika_lite.py --subject 1
python rf_baseline.py --loso

# Claude λ generator (慢, 调 API)
python llm_lambda.py --subjects 1 2 3 --pilot

# 端到端 (committed scope: TROIKA + RF + λ)
python run_all.py --scope committed

# 全 LOSO + stretch ReAct
python run_all.py --scope all
```

## Timeline 对照 proposal

| Week | Milestone | 状态 |
|---|---|---|
| 3 | Proposal 提交 | ✅ 4/22 done |
| 4 | TROIKA-lite | ⏳ 4/30 写代码骨架,等 dataset 下完跑 |
| 5 | RF baseline | ⏳ 同上 |
| 6 | Claude λ-generator v1 | ⏳ 同上 |
| 7 | Full LOSO 评估 | ⏳ daemon 凌晨可跑 |
| 8 | Project Update report (6%) | ⏳ ~5/20 |
| 9 | (Stretch) ReAct | ⏳ |
| 10 | Final report (15%) | ⏳ ~6/5 |
| Finals | Oral defense (15%) | ⏳ |

## AI 协作模式

这是 "AI 全包" 的 perfect case:

- 代码: 主对话 Claude 写
- 跑 baseline: 本机 CPU 跑
- LOSO 长跑 + λ 生成 ~1800 windows: daemon 凌晨 03:00 跑
- 报告草稿: daemon 写第一版 → Javen 审

Javen 只做: ① 早起在 approvals.md 打勾批 5 件事 ② 期末点"提交"。
