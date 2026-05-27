# Project Plan

跨 session / 跨 AI agent 共享的项目状态文件。任何 AI 打开这个文件应该能
立刻 onboard。

---

## 决策日志

按时间倒序，最新的放最上面。

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-W22 | Kaggle CLI 用 legacy kaggle.json 通过 - 新版 OAuth access_token 服务端 404 | 新版 IntrospectToken endpoint 在 api.kaggle.com 返回 404（CLI 端实现了但 server 未发布）；legacy kaggle.json 多年稳定 |
| 2026-W22 | 项目初始化（conda env adg, Python 3.11, vault 内 projects/adg-interference/） | 从零开始；Python 3.14 系统版本对 PyTorch 支持不稳定，单独建 3.11 env |
| 2026-W22 | Pilot attribute 选 smiling / male / eyeglasses，放弃 young | young 在 CelebA 上 label consistency 偏低（arxiv 2210.07356）；eyeglasses 视觉局部化，若与其他 attribute 出现 spurious 链接最 striking |
| 2026-W22 | 主测量公式改为 Δ_clf_on_gen - Δ_clf_on_real（同一 classifier apples-to-apples），label-based 仅作 sanity check | label 自身有 systematic noise；classifier-perceived correlation 是更接近 model 实际学习目标的 baseline |
| 2026-W22 | 不主打 per-attribute CFG novelty | DCFG (arxiv 2506.14399) 已覆盖 group-wise mitigation 这条线；我们聚焦 diagnostic decomposition |

（具体周数日期之后再 fill）

---

## 当前 Phase

### Phase 0: Measurement system validation（本周）

目标: 不涉及 diffusion，先确认 classifier 在 real CelebA 上的测量靠谱，
算出 baseline correlation matrix。

里程碑:
- [ ] 项目骨架 + 环境 setup
- [ ] Classifier smoke test (本地，小样本，确认 repo clone / checkpoint load /
      输出 probability / attribute 名映射)
- [ ] Classifier full eval on CelebA test set (per-attribute accuracy)
- [ ] Label-based Δ_data_label matrix for {smiling, male, eyeglasses}
- [ ] Classifier-based Δ_data_clf matrix for 同上
- [ ] 两个 matrix 差异分析 + measurement noise floor 估计

退出条件 (进入 Phase 1 的标准):
- 三个 pilot attribute 上 classifier per-attribute accuracy ≥ 90%
- Δ_data_label 和 Δ_data_clf 数值上有合理 alignment（不要求一致，但量级和符号
  应该 match）
- Measurement noise floor 明确：单个 Δ 测量的 std error 量级是多少

---

## 后续 Phase（高层 overview，细节随 Phase 0 结果调整）

### Phase 1: 拿到 / 训出 multi-attribute conditional diffusion model

候选路径，决策依据是 Phase 0 完成后的资源 / 时间预算：

- **选项 A**: 联系 DCFG 作者要 code（暂跳过，由用户决定不发邮件）
- **选项 B**: Finetune google/ddpm-celebahq-256 加 attribute conditioning
  (FiLM 或 cross-attention)
- **选项 C**: 从零训 64×64 conditional DDPM
- **选项 D**: 尝试用 Giambi & Lisanti 论文复现 cross-attention 多属性 conditioning

倾向: B（finetune 最快）

### Phase 2: Pilot 实验

- 3 attributes (smiling / male / eyeglasses) × 4 guidance scales (w ∈ {1, 3, 5, 7})
- 必须包含 w = 1（关键！只有 w=1 才能分离 model-bias 和 guidance-amplification）
- 每个 (attribute combination, w) 至少 400 samples（基于 Δ std error ≈ 0.07 估算）
- 输出 Δ_spurious matrix over w
- Sampling variance check: fixed seed vs random seed 对照

### Phase 3: Diagnostic analysis + mitigation 设计

根据 Phase 2 诊断结果选择 intervention 策略：
- 若 guidance-induced 占主导 → adaptive w_k schedule
- 若 model-induced 占主导 → noise-space subspace projection
- 若 data-induced 占主导 → 不干预（这是真实分布）

Baseline 对比: vanilla CFG, DCFG (如果届时 code 已 release)

### Phase 4: Writing

---

## 关键风险（持续监控）

| 风险 | 触发条件 | 应对 |
|---|---|---|
| Δ_spurious 在 vanilla CFG 上不显著 | Phase 2 主图 K×K matrix 几乎全 0 | 项目废，换题 |
| DCFG ablation 已覆盖部分 contribution | 精读 DCFG 后发现 | C1/C2 contribution 收缩，加强 C3 |
| CelebA label noise 污染 Δ_data | Phase 0 中 Δ_data_label vs Δ_data_clf 严重背离 | 主测量公式只用 classifier-based，label 仅作 reference |
| Classifier artifact 制造假 spurious | Phase 0 noise floor 测试 + Phase 2 双 classifier (ResNet vs ViT) cross-check | 已经设计在 plan 里 |
| Diffusion model 训练不收敛 / FID 过高 | Phase 1 训完后样本质量肉眼差 | 退到更小 resolution (32×32) 或 fallback 到 unconditional + classifier guidance |

---

## 资源

- **算力**: Kaggle 免费 GPU (P100/T4, 30h/week, 12h/session)
- **存储**: vault 内 + Kaggle 远端（生成数据不入 git）
- **AI 工具**:
  - Claudian (Obsidian) → Claude Code / Codex backend (执行)
  - Claude.ai webchat (架构 / review)
  - Codex (cross-check 关键 metric 代码)
- **知识库**: vault 的 papers/ 和 notes/

---

## 当前 status

Phase 0 进行中。环境已 ready，准备进 Step 6+（git init + Kaggle CLI 检查），
之后开 Phase 0 第一个实际任务：classifier smoke test。
