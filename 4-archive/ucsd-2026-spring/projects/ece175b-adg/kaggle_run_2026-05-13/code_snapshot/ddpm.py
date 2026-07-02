"""DDPM training step — 用 diffusers DDPMScheduler.

Forward: q(x_t | x_0) = N(√α̅_t x_0, (1-α̅_t) I)
Reverse: parameterized by ε_θ(x_t, t, attr) — model 预测加进去的噪声

Loss = MSE(ε_predicted, ε_true) — proposal §4 / Ho 2020
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from diffusers import DDPMScheduler


def make_scheduler(num_train_timesteps: int = 1000) -> DDPMScheduler:
    return DDPMScheduler(
        num_train_timesteps=num_train_timesteps,
        beta_schedule="linear",
        beta_start=0.0001,
        beta_end=0.02,
        prediction_type="epsilon",
    )


def training_step(
    model,
    scheduler: DDPMScheduler,
    batch: dict,
    device: torch.device,
    attr_drop_p: float = 0.1,
) -> torch.Tensor:
    """单个 batch 的训练 loss.

    Args:
        model: AttrConditionedUNet
        batch: {"image": (B,3,H,W) ∈ [-1,1], "attr": (B,K) ∈ {0,1}}
    Returns:
        scalar loss
    """
    from model import random_attr_dropout

    x0 = batch["image"].to(device)
    attr = batch["attr"].to(device)
    attr = random_attr_dropout(attr, p=attr_drop_p)  # CFG 训练: 随机 drop 成 null

    B = x0.shape[0]
    noise = torch.randn_like(x0)
    timesteps = torch.randint(
        0, scheduler.config.num_train_timesteps, (B,), device=device, dtype=torch.long
    )

    # q(x_t | x_0)
    x_t = scheduler.add_noise(x0, noise, timesteps)

    # 预测噪声
    eps_pred = model(x_t, timesteps, attr)
    return F.mse_loss(eps_pred, noise)


@torch.no_grad()
def ddpm_sample_loop(
    model,
    scheduler: DDPMScheduler,
    shape: tuple,
    device: torch.device,
    cond_fn,  # callable: (x_t, t, eps_uncond) -> guided_eps
):
    """通用 DDPM 采样, guidance 由 cond_fn 提供.

    cond_fn 接收 (x_t, t_int, model) -> guided_eps.
    这样 cfg.py 和 adg.py 可以注入不同的 guidance 公式.
    """
    x = torch.randn(*shape, device=device)
    scheduler.set_timesteps(scheduler.config.num_train_timesteps)
    for t in scheduler.timesteps:
        eps = cond_fn(x, t, model)
        x = scheduler.step(eps, t, x).prev_sample
    return x.clamp(-1, 1)


if __name__ == "__main__":
    print("ddpm.py — import-only module, 由 train.py / sample.py 调用")
