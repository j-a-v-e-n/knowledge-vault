# Kaggle Playground S6E6 — Predicting Stellar Class

预测天体类别（GALAXY / QSO / STAR）的三分类比赛。Deadline: 2026-06-30。

## 数据
- `train.csv`: 577,347 行 × 12 列；`test.csv`: 247,435 行 × 11 列
- 特征：`alpha`, `delta`（天球坐标）、`u/g/r/i/z`（测光星等）、`redshift`、`spectral_type`（4 类）、`galaxy_population`（2 类）
- target `class`：GALAXY 65.4% / QSO 20.3% / STAR 14.3%（类别不平衡）
- 无缺失值
- 评测指标：未能从 Kaggle 页面确认（JS 渲染抓不到）。提交是标签 → 必为标签型分类指标（accuracy 或 macro-F1），建模选择对两者一致。

## Baseline（submission #1）
- 模型：`sklearn.HistGradientBoostingClassifier`，原生处理类别特征
- 参数：max_iter=600, lr=0.05, max_leaf_nodes=63, min_samples_leaf=50, l2=1.0, early_stopping
- 5-fold StratifiedKFold CV：
  - **accuracy = 0.96743 ± 0.00069**
  - **macro-F1 = 0.95596 ± 0.00109**
- 预测分布：GALAXY 65.5% / QSO 20.2% / STAR 14.3%（与训练集一致）
- public LB score：待回填

## 复现
```bash
cd kaggle/playground-s6e6
python3 train.py          # 跑 CV + 生成 submission.csv
python3 -m kaggle competitions submit -c playground-series-s6e6 -f submission.csv -m "..."
```

## 下一步可提分方向（未做）
- 特征工程：颜色指数 u-g, g-r, r-i, i-z（天文上对分类极强）
- 模型集成：XGBoost / LightGBM（需装 libomp）+ HGB 投票
- 调参：max_iter 提到 1000+、学习率网格
