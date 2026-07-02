"""采样 + 可视化. 支持标准 CFG 和 ADG, 也支持 sweep (扫一个 attribute 的 w_k).

例:
    # 标准 CFG, w=4.0, 16 张图
    python sample.py --method cfg --w 4.0 --n 16 --out results/cfg.png

    # ADG, 给每个 attribute 单独 w_k
    python sample.py --method adg --w 1 4 0 0 --out results/adg.png

    # ADG sweep: 固定其他 attribute, w_eyeglasses 扫 0→6 (7 步)
    python sample.py --method adg --sweep eyeglasses 0 6 7 --out results/sweep.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import torch
import torchvision

from adg import adg_cond_fn
from cfg import cfg_cond_fn
from data import attr_indices
from ddpm import ddpm_sample_loop, make_scheduler
from model import AttrConditionedUNet


def load_model(ckpt_path: str, n_attrs: int, resolution: int, device: torch.device) -> AttrConditionedUNet:
    model = AttrConditionedUNet(sample_size=resolution, n_attrs=n_attrs).to(device)
    ckpt = torch.load(ckpt_path, map_location=device)
    state = ckpt.get("model", ckpt)
    model.load_state_dict(state)
    model.eval()
    return model


def to_grid(tensor: torch.Tensor, n_per_row: int = 4):
    # tensor: (B, 3, H, W) ∈ [-1, 1]
    grid = torchvision.utils.make_grid(
        tensor, nrow=n_per_row, normalize=True, value_range=(-1, 1)
    )
    return grid.permute(1, 2, 0).cpu().numpy()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="checkpoints/best.pt")
    p.add_argument("--method", choices=["cfg", "adg"], required=True)
    p.add_argument("--attrs", nargs="+", default=["smiling", "eyeglasses", "male", "young"])
    p.add_argument("--resolution", type=int, default=64)
    p.add_argument("--n", type=int, default=16, help="number of samples")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--out", default="results/sample.png")
    # CFG: 单一 w
    p.add_argument("--w", nargs="+", type=float,
                   help="cfg: 单一标量; adg: K 个标量 w_k")
    # ADG sweep: --sweep <attr_name> <lo> <hi> <n_steps>
    p.add_argument("--sweep", nargs=4, default=None,
                   metavar=("ATTR", "LO", "HI", "N_STEPS"),
                   help="ADG only: 扫描某 attribute 的 w_k, 其他固定")
    p.add_argument("--target", default="1,1,0,1",
                   help="K 个 0/1 逗号分隔, target attribute vector")
    args = p.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    Path(args.out).parent.mkdir(exist_ok=True, parents=True)
    n_attrs = len(args.attrs)

    model = load_model(args.ckpt, n_attrs=n_attrs, resolution=args.resolution, device=device)
    scheduler = make_scheduler()

    target = torch.tensor([[float(v) for v in args.target.split(",")]], device=device)
    target = target.repeat(args.n, 1)
    assert target.shape[1] == n_attrs

    torch.manual_seed(args.seed)
    shape = (args.n, 3, args.resolution, args.resolution)

    if args.sweep:
        attr_name, lo, hi, n_steps = args.sweep
        attr_idx = args.attrs.index(attr_name)
        sweep_values = torch.linspace(float(lo), float(hi), int(n_steps))
        all_imgs = []
        for v in sweep_values:
            ws = [1.0] * n_attrs  # 默认 w_k=1 for non-swept
            ws[attr_idx] = float(v)
            cond = adg_cond_fn(target, ws)
            imgs = ddpm_sample_loop(model, scheduler, shape, device, cond)
            all_imgs.append(imgs)
            print(f"  {attr_name} = {v:.2f}: done")
        imgs = torch.cat(all_imgs, dim=0)
        title = f"ADG sweep {attr_name} from {lo} to {hi}"
    elif args.method == "cfg":
        w = args.w[0] if args.w else 4.0
        cond = cfg_cond_fn(target, w=w)
        imgs = ddpm_sample_loop(model, scheduler, shape, device, cond)
        title = f"CFG (w={w})"
    else:  # adg
        ws = args.w if args.w else [1.0] * n_attrs
        assert len(ws) == n_attrs, f"--w needs {n_attrs} values for ADG"
        cond = adg_cond_fn(target, ws)
        imgs = ddpm_sample_loop(model, scheduler, shape, device, cond)
        title = f"ADG (w={ws}) target=[{','.join(args.attrs)}={args.target}]"

    grid = to_grid(imgs, n_per_row=int(args.n ** 0.5) or 4)
    plt.figure(figsize=(8, 8))
    plt.imshow(grid)
    plt.axis("off")
    plt.title(title, fontsize=10)
    plt.tight_layout()
    plt.savefig(args.out, dpi=120, bbox_inches="tight")
    print(f"\nSaved → {args.out}")


if __name__ == "__main__":
    main()
