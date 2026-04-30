"""标准 Classifier-Free Guidance (Ho & Salimans 2022).

ε̃(x_t, y) = ε(x_t, ∅) + w · [ε(x_t, y) - ε(x_t, ∅)]

单一 guidance scale w — 这就是 ADG 想要超越的 baseline.
"""

from __future__ import annotations

import torch

from model import make_null_attr


def cfg_cond_fn(attr: torch.Tensor, w: float):
    """返回一个 cond_fn,用于 ddpm_sample_loop.

    Args:
        attr: (B, K) target attribute vector
        w: guidance scale (常用 1.0 - 7.5)

    Returns:
        callable(x_t, t, model) → guided ε
    """
    null_attr = make_null_attr(attr.shape[0], attr.shape[1], attr.device)

    def fn(x_t: torch.Tensor, t, model) -> torch.Tensor:
        # 拼成 batch 一次过 unet (省 forward pass)
        x_in = torch.cat([x_t, x_t], dim=0)
        a_in = torch.cat([null_attr, attr], dim=0)
        t_in = torch.full((x_in.shape[0],), int(t), device=x_t.device, dtype=torch.long)

        eps_full = model(x_in, t_in, a_in)
        eps_uncond, eps_cond = eps_full.chunk(2, dim=0)
        return eps_uncond + w * (eps_cond - eps_uncond)

    return fn


if __name__ == "__main__":
    print("cfg.py — 由 sample.py --method cfg 调用")
