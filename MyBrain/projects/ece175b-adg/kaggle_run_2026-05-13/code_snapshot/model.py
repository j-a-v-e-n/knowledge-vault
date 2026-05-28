"""Conditional UNet for CelebA 64×64 — 用 diffusers 的 UNet2DModel 改 attribute 条件。

Conditioning 设计:
- attribute K-hot vector (K=4) 经过一个小 MLP → 时间步 embedding 维度
- 在 timestep embedding 上加上 attribute embedding (residual style)
- Null token: 训练时 10% drop attribute (置 K-zeros) 实现 classifier-free training
"""

from __future__ import annotations

import torch
import torch.nn as nn
from diffusers import UNet2DModel


class AttrConditionedUNet(nn.Module):
    """在 diffusers 的 UNet2DModel 之上加 attribute conditioning."""

    def __init__(
        self,
        sample_size: int = 64,
        in_channels: int = 3,
        out_channels: int = 3,
        n_attrs: int = 4,
        time_embed_dim: int = 256,
    ):
        super().__init__()
        self.n_attrs = n_attrs
        self.time_embed_dim = time_embed_dim

        # diffusers UNet2DModel 自带 timestep embedding,
        # 我们用 class_embed_type="identity" 把 attribute embedding 注入它的 class_emb
        self.unet = UNet2DModel(
            sample_size=sample_size,
            in_channels=in_channels,
            out_channels=out_channels,
            layers_per_block=2,
            block_out_channels=(64, 128, 256, 256),
            down_block_types=(
                "DownBlock2D", "DownBlock2D", "AttnDownBlock2D", "DownBlock2D",
            ),
            up_block_types=(
                "UpBlock2D", "AttnUpBlock2D", "UpBlock2D", "UpBlock2D",
            ),
            class_embed_type="identity",  # 我们直接传 (B, time_embed_dim) 进去
        )

        # attribute (K,) → time_embed_dim
        self.attr_proj = nn.Sequential(
            nn.Linear(n_attrs, time_embed_dim),
            nn.SiLU(),
            nn.Linear(time_embed_dim, time_embed_dim),
        )

    def forward(self, x: torch.Tensor, t: torch.Tensor, attr: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, 3, H, W), 噪声图
            t: (B,), timestep
            attr: (B, K), float 0/1 — null 用 全 0
        Returns:
            (B, 3, H, W) 预测的噪声 ε
        """
        cond = self.attr_proj(attr)  # (B, time_embed_dim)
        return self.unet(x, t, class_labels=cond).sample


def make_null_attr(batch_size: int, n_attrs: int, device: torch.device) -> torch.Tensor:
    """null token = all-zeros K-hot vector."""
    return torch.zeros(batch_size, n_attrs, device=device)


def random_attr_dropout(attr: torch.Tensor, p: float = 0.1) -> torch.Tensor:
    """以概率 p 整批 drop attribute → null. CFG 训练标配."""
    mask = (torch.rand(attr.shape[0], 1, device=attr.device) < p).float()
    return attr * (1 - mask)


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AttrConditionedUNet(sample_size=64, n_attrs=4).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {n_params / 1e6:.2f}M")

    # smoke test
    B = 4
    x = torch.randn(B, 3, 64, 64, device=device)
    t = torch.randint(0, 1000, (B,), device=device)
    attr = torch.randint(0, 2, (B, 4), device=device).float()
    with torch.no_grad():
        out = model(x, t, attr)
    print(f"Forward OK. Output: {out.shape}")
