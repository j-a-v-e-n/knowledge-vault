"""FID 评估 — 用 torch-fidelity (官方 InceptionV3 implementation).

跑法:
    python eval_fid.py --ckpt checkpoints/best.pt --n-samples 5000

输出:
    results/fid_<method>_<config>.json
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import torch
import torchvision

from adg import adg_cond_fn
from cfg import cfg_cond_fn
from ddpm import ddpm_sample_loop, make_scheduler
from model import AttrConditionedUNet
from sample import load_model

try:
    from torch_fidelity import calculate_metrics  # type: ignore

    HAS_FIDELITY = True
except ImportError:
    HAS_FIDELITY = False


def gen_samples(
    model, scheduler, n_samples: int, attrs: list[str], target_str: str,
    method: str, w, batch_size: int, device, resolution: int,
    seed: int = 0,
) -> torch.Tensor:
    """生成 n_samples 张图,返回 [-1,1] tensor (B,3,H,W)."""
    torch.manual_seed(seed)
    n_attrs = len(attrs)
    target = torch.tensor([[float(v) for v in target_str.split(",")]], device=device)

    all_imgs = []
    n_done = 0
    while n_done < n_samples:
        b = min(batch_size, n_samples - n_done)
        t = target.repeat(b, 1)
        if method == "cfg":
            w_v = w if isinstance(w, (int, float)) else w[0]
            cond = cfg_cond_fn(t, w=float(w_v))
        else:
            cond = adg_cond_fn(t, w if isinstance(w, list) else [w] * n_attrs)
        imgs = ddpm_sample_loop(model, scheduler, (b, 3, resolution, resolution), device, cond)
        all_imgs.append(imgs)
        n_done += b
        print(f"  generated {n_done}/{n_samples}")
    return torch.cat(all_imgs, dim=0)[:n_samples]


def save_imgs_to_dir(imgs: torch.Tensor, out_dir: Path):
    """把 (B,3,H,W) ∈ [-1,1] 写成 PNG 文件给 torch-fidelity."""
    out_dir.mkdir(exist_ok=True, parents=True)
    imgs = (imgs.clamp(-1, 1) + 1) / 2  # [0, 1]
    for i, img in enumerate(imgs):
        torchvision.utils.save_image(img, out_dir / f"{i:06d}.png")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="checkpoints/best.pt")
    p.add_argument("--attrs", nargs="+", default=["smiling", "eyeglasses", "male", "young"])
    p.add_argument("--resolution", type=int, default=64)
    p.add_argument("--n-samples", type=int, default=5000)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--method", choices=["cfg", "adg"], default="cfg")
    p.add_argument("--w", nargs="+", type=float, default=[4.0])
    p.add_argument("--target", default="1,1,0,1")
    p.add_argument("--real-dir", default="data/celeba/img_align_celeba",
                   help="real CelebA images for FID reference")
    p.add_argument("--out", default="results/fid.json")
    p.add_argument("--keep-samples", action="store_true",
                   help="不删 _tmp_samples (debug 用)")
    args = p.parse_args()

    if not HAS_FIDELITY:
        raise RuntimeError("`torch-fidelity` 未装. pip install torch-fidelity")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    n_attrs = len(args.attrs)
    model = load_model(args.ckpt, n_attrs=n_attrs, resolution=args.resolution, device=device)
    scheduler = make_scheduler()

    sample_dir = Path("results/_tmp_fid_samples")
    if sample_dir.exists():
        shutil.rmtree(sample_dir)

    print(f"Generating {args.n_samples} samples ({args.method} w={args.w})...")
    w = args.w[0] if args.method == "cfg" else args.w
    imgs = gen_samples(
        model, scheduler, args.n_samples, args.attrs, args.target,
        args.method, w, args.batch_size, device, args.resolution,
    )
    save_imgs_to_dir(imgs, sample_dir)

    print(f"Computing FID against {args.real_dir}...")
    metrics = calculate_metrics(
        input1=str(sample_dir),
        input2=args.real_dir,
        cuda=device.type == "cuda",
        fid=True, isc=True, kid=False,
    )
    print(f"  FID = {metrics['frechet_inception_distance']:.2f}")
    print(f"  IS  = {metrics['inception_score_mean']:.2f} ± {metrics['inception_score_std']:.2f}")

    Path("results").mkdir(exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({
            "method": args.method, "w": args.w, "n_samples": args.n_samples,
            "fid": metrics["frechet_inception_distance"],
            "is_mean": metrics["inception_score_mean"],
            "is_std": metrics["inception_score_std"],
        }, f, indent=2)
    print(f"Saved → {args.out}")

    if not args.keep_samples:
        shutil.rmtree(sample_dir)


if __name__ == "__main__":
    main()
