"""Per-attribute classification accuracy + 解耦度评估.

按 proposal §4 的 third metric: "attribute disentanglement —
whether adjusting one attribute's w_k leaves other attributes unchanged."

流程:
1. 训一个 attribute classifier on real CelebA (4 个二分类头, ResNet18 backbone)
2. 在生成的图上跑分类器, 看每个 attribute 的预测准确率
3. 解耦度 = w_k 扫描时,被扫的 attribute 概率 monotonic 上升 + 其他 attributes 概率 stable

输出:
- results/classifier.pt (一次训完反复用)
- results/disentangle_<config>.json
- results/disentangle_curve.png (扫 w_k 时各 attribute 概率曲线)
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
import torch.nn as nn
import torchvision
from torchvision.models import ResNet18_Weights, resnet18
from tqdm import tqdm

from adg import adg_cond_fn
from data import CelebASubset, get_dataloader
from ddpm import ddpm_sample_loop, make_scheduler
from sample import load_model


def make_classifier(n_attrs: int) -> nn.Module:
    """ResNet18 + K 个独立的 binary heads."""
    backbone = resnet18(weights=ResNet18_Weights.DEFAULT)
    backbone.fc = nn.Linear(backbone.fc.in_features, n_attrs)
    return backbone  # output (B, K) logits


def train_classifier(
    save_path: str = "results/classifier.pt",
    attrs: list[str] | None = None,
    resolution: int = 64,
    epochs: int = 5,
    batch_size: int = 128,
):
    """训一个简单 attribute classifier on real CelebA."""
    attrs = attrs or ["smiling", "eyeglasses", "male", "young"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loader = get_dataloader(
        attrs=attrs, resolution=resolution, batch_size=batch_size, num_workers=4, shuffle=True,
    )
    clf = make_classifier(len(attrs)).to(device)
    opt = torch.optim.AdamW(clf.parameters(), lr=1e-4)
    bce = nn.BCEWithLogitsLoss()
    print(f"Training classifier on {len(loader.dataset)} CelebA images...")
    for ep in range(epochs):
        running = 0.0
        n = 0
        for batch in tqdm(loader, desc=f"epoch {ep}"):
            img = batch["image"].to(device)
            attr = batch["attr"].to(device)
            opt.zero_grad()
            logits = clf(img)
            loss = bce(logits, attr)
            loss.backward()
            opt.step()
            running += loss.item() * img.shape[0]
            n += img.shape[0]
        print(f"  epoch {ep}: avg BCE = {running / n:.4f}")
    Path(os.path.dirname(save_path)).mkdir(exist_ok=True, parents=True)
    torch.save({"model": clf.state_dict(), "attrs": attrs}, save_path)
    print(f"Saved classifier → {save_path}")
    return clf


def load_classifier(path: str, n_attrs: int, device) -> nn.Module:
    clf = make_classifier(n_attrs).to(device)
    state = torch.load(path, map_location=device)
    clf.load_state_dict(state["model"])
    clf.eval()
    return clf


@torch.no_grad()
def predict_attrs(clf: nn.Module, imgs: torch.Tensor) -> torch.Tensor:
    """imgs ∈ [-1,1] (B,3,H,W). 返回每个 attribute 的概率 (B,K)."""
    # ResNet 期望 ImageNet normalization,但训分类器时用了 CelebA 的 [-1,1] norm,
    # 所以我们这里直接传不要再 normalize 一次
    return torch.sigmoid(clf(imgs))


def disentangle_sweep(
    model, scheduler, clf, attrs: list[str], target: torch.Tensor,
    sweep_attr: str, w_range: list[float], n_per_w: int = 16,
    other_w: float = 1.0, resolution: int = 64, device=None,
) -> dict:
    """扫描 w_k(sweep_attr), 看每个 attribute 的概率随 w_k 变化."""
    n_attrs = len(attrs)
    sweep_idx = attrs.index(sweep_attr)
    probs_per_w = {}  # {w_value: (n_per_w, K) probs}

    for w in w_range:
        ws = [other_w] * n_attrs
        ws[sweep_idx] = w
        cond = adg_cond_fn(target.repeat(n_per_w, 1), ws)
        imgs = ddpm_sample_loop(
            model, scheduler, (n_per_w, 3, resolution, resolution), device, cond
        )
        probs = predict_attrs(clf, imgs)  # (n_per_w, K)
        probs_per_w[float(w)] = probs.mean(dim=0).cpu().tolist()  # K 个均值
        print(f"  w_{sweep_attr} = {w}: probs = {[f'{p:.2f}' for p in probs_per_w[float(w)]]}")
    return {
        "sweep_attr": sweep_attr,
        "attrs": attrs,
        "probs_per_w": probs_per_w,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="checkpoints/best.pt")
    p.add_argument("--clf-path", default="results/classifier.pt")
    p.add_argument("--attrs", nargs="+", default=["smiling", "eyeglasses", "male", "young"])
    p.add_argument("--train-clf", action="store_true",
                   help="先训 classifier (~10 min on Colab GPU)")
    p.add_argument("--sweep-attr", default="eyeglasses")
    p.add_argument("--w-range", nargs="+", type=float, default=[0, 1, 2, 3, 4, 5, 6])
    p.add_argument("--target", default="1,1,0,1")
    p.add_argument("--resolution", type=int, default=64)
    p.add_argument("--n-per-w", type=int, default=16)
    p.add_argument("--out", default="results/disentangle.json")
    args = p.parse_args()

    if args.train_clf:
        train_classifier(save_path=args.clf_path, attrs=args.attrs, resolution=args.resolution)

    if not Path(args.clf_path).exists():
        raise RuntimeError(f"分类器 {args.clf_path} 不存在. 先 --train-clf")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_attrs = len(args.attrs)

    diff_model = load_model(args.ckpt, n_attrs=n_attrs, resolution=args.resolution, device=device)
    scheduler = make_scheduler()
    clf = load_classifier(args.clf_path, n_attrs=n_attrs, device=device)

    target = torch.tensor([[float(v) for v in args.target.split(",")]], device=device)
    print(f"Target: {target.tolist()}, sweep {args.sweep_attr} over {args.w_range}")
    res = disentangle_sweep(
        diff_model, scheduler, clf, args.attrs, target,
        args.sweep_attr, args.w_range, n_per_w=args.n_per_w,
        resolution=args.resolution, device=device,
    )

    Path("results").mkdir(exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"\nSaved → {args.out}")
    print(f"   解读: 理想情况下,只有 prob_{args.sweep_attr} 单调上升,其他 prob 保持稳定 = 解耦成功")


if __name__ == "__main__":
    main()
