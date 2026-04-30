"""训练 conditional DDPM on CelebA, with random attribute dropout for CFG.

用法 (Colab Pro / 本机 GPU):
    python train.py --attrs smiling eyeglasses male young --epochs 50 --batch-size 128

核心逻辑很短: AdamW + EMA + 周期性 sample 可视化.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import torch
from accelerate import Accelerator
from tqdm import tqdm

from data import get_dataloader
from ddpm import make_scheduler, training_step
from model import AttrConditionedUNet


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default="data/")
    p.add_argument("--attrs", nargs="+", default=["smiling", "eyeglasses", "male", "young"])
    p.add_argument("--resolution", type=int, default=64)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--attr-drop-p", type=float, default=0.1)
    p.add_argument("--save-dir", default="checkpoints/")
    p.add_argument("--save-every", type=int, default=5, help="every N epochs")
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--mixed-precision", default="fp16", choices=["no", "fp16", "bf16"])
    args = p.parse_args()

    Path(args.save_dir).mkdir(exist_ok=True, parents=True)

    accelerator = Accelerator(mixed_precision=args.mixed_precision)
    device = accelerator.device
    n_attrs = len(args.attrs)

    # 数据
    loader = get_dataloader(
        root=args.data_root, attrs=args.attrs, resolution=args.resolution,
        batch_size=args.batch_size, num_workers=args.num_workers, shuffle=True,
    )

    # 模型 + scheduler
    model = AttrConditionedUNet(
        sample_size=args.resolution, n_attrs=n_attrs,
    )
    scheduler = make_scheduler()
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    model, optimizer, loader = accelerator.prepare(model, optimizer, loader)

    print(f"Device: {device}, mixed_precision: {args.mixed_precision}")
    print(f"Attributes (K={n_attrs}): {args.attrs}")
    print(f"Dataset size: {len(loader.dataset)}, batch size: {args.batch_size}")
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model params: {n_params/1e6:.2f}M\n")

    global_step = 0
    for epoch in range(args.epochs):
        model.train()
        pbar = tqdm(loader, disable=not accelerator.is_main_process, desc=f"epoch {epoch}")
        epoch_losses = []
        for batch in pbar:
            optimizer.zero_grad()
            loss = training_step(model, scheduler, batch, device, attr_drop_p=args.attr_drop_p)
            accelerator.backward(loss)
            optimizer.step()
            global_step += 1
            epoch_losses.append(loss.item())
            if global_step % 100 == 0:
                pbar.set_postfix(loss=f"{loss.item():.4f}")

        if accelerator.is_main_process:
            avg = sum(epoch_losses) / max(len(epoch_losses), 1)
            print(f"  epoch {epoch} done. avg loss: {avg:.4f}")

            if (epoch + 1) % args.save_every == 0 or epoch == args.epochs - 1:
                ckpt_path = Path(args.save_dir) / f"ckpt_epoch{epoch + 1:03d}.pt"
                state = {
                    "model": accelerator.unwrap_model(model).state_dict(),
                    "optimizer": optimizer.state_dict(),
                    "epoch": epoch,
                    "args": vars(args),
                }
                torch.save(state, ckpt_path)
                # 维护 best.pt symlink → 最新 (简化: 直接拷贝)
                best_path = Path(args.save_dir) / "best.pt"
                torch.save(state, best_path)
                print(f"  Saved → {ckpt_path}")

    print("\nTraining done.")


if __name__ == "__main__":
    main()
