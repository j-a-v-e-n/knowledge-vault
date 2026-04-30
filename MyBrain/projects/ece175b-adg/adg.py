"""Attribute-Disentangled Guidance (ADG) — 主贡献.

ε̃(x_t, y) = ε(x_t, ∅) + Σ_k w_k · [ε(x_t, y^(k)) - ε(x_t, ∅)]

其中 y^(k) 是只激活第 k 个 attribute 的 conditioning 向量 (其他 K-1 个 = 0).

每个 attribute 有独立 guidance scale w_k:
- w_k > 0: 强化第 k 个 attribute
- w_k = 0: 让第 k 个 attribute 自由 (跟 unconditional 一样)
- w_k < 0: 反向 — attribute negation (proposal §5 提到的 novelty)
"""

from __future__ import annotations

import torch

from model import make_null_attr


def make_single_attr_vectors(attr: torch.Tensor) -> list[torch.Tensor]:
    """给定 (B, K) target 向量, 返回 K 个"只激活一个 attribute"的向量列表.

    y^(k)[k] = attr[k], 其他位 = 0.
    """
    B, K = attr.shape
    out = []
    for k in range(K):
        single = torch.zeros_like(attr)
        single[:, k] = attr[:, k]
        out.append(single)
    return out


def adg_cond_fn(attr: torch.Tensor, ws: list[float] | torch.Tensor):
    """ADG cond_fn for ddpm_sample_loop.

    Args:
        attr: (B, K) target attribute vector
        ws: K-length 的 guidance scales (each w_k)

    Returns:
        callable(x_t, t, model) → guided ε
    """
    B, K = attr.shape
    if not isinstance(ws, torch.Tensor):
        ws = torch.tensor(ws, dtype=torch.float32, device=attr.device)
    assert ws.shape == (K,), f"ws shape {ws.shape} 不匹配 K={K}"

    null_attr = make_null_attr(B, K, attr.device)
    single_attrs = make_single_attr_vectors(attr)  # K 个 (B, K)

    def fn(x_t: torch.Tensor, t, model) -> torch.Tensor:
        # 把 K+1 个 forward pass 拼成一个大 batch:
        # [null, y^(1), y^(2), ..., y^(K)]
        x_in = torch.cat([x_t] * (K + 1), dim=0)
        a_in = torch.cat([null_attr] + single_attrs, dim=0)  # (B*(K+1), K)
        t_in = torch.full((x_in.shape[0],), int(t), device=x_t.device, dtype=torch.long)

        eps_full = model(x_in, t_in, a_in)  # (B*(K+1), 3, H, W)
        eps_chunks = eps_full.chunk(K + 1, dim=0)
        eps_uncond = eps_chunks[0]
        eps_singles = eps_chunks[1:]  # K 个

        # ADG 公式
        guided = eps_uncond.clone()
        for k in range(K):
            guided = guided + ws[k] * (eps_singles[k] - eps_uncond)
        return guided

    return fn


if __name__ == "__main__":
    # smoke test
    print("adg.py — smoke test")
    attr = torch.zeros(2, 4)
    attr[0] = torch.tensor([1.0, 1.0, 0.0, 1.0])  # smile + glasses + young
    attr[1] = torch.tensor([0.0, 0.0, 1.0, 0.0])  # male only
    singles = make_single_attr_vectors(attr)
    print(f"target attr: {attr}")
    for k, s in enumerate(singles):
        print(f"  y^({k}): {s}")
