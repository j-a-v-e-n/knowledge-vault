# Colab Pro 快速启动 (ECE 175B ADG)

> Javen 起来后:① 注册 Colab Pro → ② 新建 notebook → ③ 按下面 4 个 cell 顺序粘贴并跑就行。
>
> 全程不用懂 PyTorch — 4 个 cell 跑完会自动训练 + 输出 ADG 采样图。

## Cell 1: 挂 Drive + clone 项目

```python
from google.colab import drive
drive.mount('/content/drive')

# 假设你已经把 vault git push 到了 GitHub 私有 repo `ece175b-adg`
# 如果没 push 也可以从 Drive 直接 cp 过来:
!cp -r "/content/drive/MyDrive/知识库/MyBrain/projects/ece175b-adg" /content/
%cd /content/ece175b-adg

!pip install -q -r requirements.txt
print("环境就绪")
```

## Cell 2: 验证 GPU

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NO GPU'}")
# Colab Pro 应该给 V100 / A100 / L4
```

## Cell 3: 训练 (4-6h on A100)

```python
# CelebA 自动下到 /content/data — Colab 容器空间 100GB, 装得下
!python train.py \
    --data-root /content/data/ \
    --attrs smiling eyeglasses male young \
    --resolution 64 \
    --epochs 50 \
    --batch-size 128 \
    --save-dir /content/checkpoints/ \
    --mixed-precision fp16
```

> 训完 checkpoint 自动写到 `/content/checkpoints/best.pt` (~100 MB).
> 跑前可以先 `--epochs 2` 跑 smoke test 确认 pipeline 没问题。

## Cell 4: 采样 + 保存图片到 Drive

```python
# 标准 CFG baseline
!python sample.py --ckpt /content/checkpoints/best.pt --method cfg --w 4.0 \
    --out /content/results/cfg_baseline.png

# ADG: 强 eyeglasses, 弱 smile, 默认 male/young
!python sample.py --ckpt /content/checkpoints/best.pt --method adg --w 1 4 0 1 \
    --out /content/results/adg_strong_glasses.png

# ADG sweep: 扫 eyeglasses 的 w_k 0→6, 看人脸戴眼镜程度
!python sample.py --ckpt /content/checkpoints/best.pt --method adg \
    --sweep eyeglasses 0 6 7 \
    --out /content/results/sweep_eyeglasses.png

# 把结果回传 Drive
!cp -r /content/results "/content/drive/MyDrive/知识库/MyBrain/projects/ece175b-adg/results/"
!cp /content/checkpoints/best.pt "/content/drive/MyDrive/知识库/MyBrain/projects/ece175b-adg/checkpoints/"
```

## Cell 5: (可选) FID + 解耦度评估

```python
# 训分类器 (~10 min)
!python eval_disentangle.py --ckpt /content/checkpoints/best.pt --train-clf

# 跑解耦扫描
!python eval_disentangle.py --ckpt /content/checkpoints/best.pt --sweep-attr eyeglasses

# FID (~30 min for 5000 samples)
!python eval_fid.py --ckpt /content/checkpoints/best.pt --n-samples 5000

!cp -r /content/results "/content/drive/MyDrive/知识库/MyBrain/projects/ece175b-adg/results/"
```

## 常见坑

| 问题 | 解法 |
|---|---|
| `torchvision CelebA download failed` | 手动下 [Kaggle CelebA](https://www.kaggle.com/datasets/jessicali9530/celeba-dataset) → 解压到 `/content/data/celeba/` |
| Colab 把 GPU 收走了 | Pro 用户冷却 ~30 min 后能重连; 集中 8h 周末跑 |
| OOM | `--batch-size 64` (V100 是 16GB, A100 40GB) |
| 训练 loss 不降 | 检查 `data.py` 的 attribute index — CELEBA_ATTR_NAMES 顺序不能乱 |

## 时间预算

| Step | Colab Pro A100 | Colab Pro T4 |
|---|---|---|
| 训练 50 epochs | ~4-5h | ~12-15h (一次跑不完, 分 3 次) |
| FID 5000 samples | ~30 min | ~1.5h |
| 解耦扫描 7 个 w | ~15 min | ~1h |
| **总计** | **~6h** | **~18h** |

A100 跑一晚就完事; T4 要分两个周末。
