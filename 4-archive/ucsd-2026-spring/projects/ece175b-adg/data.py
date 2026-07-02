"""CelebA dataloader with attribute conditioning.

Proposal §4: K=4 attributes — smiling, eyeglasses, male, young — at 64×64.
"""

from __future__ import annotations

from pathlib import Path

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import CelebA

# CelebA 40 个属性的 index — 用于从原始 attr tensor 切出我们要的子集
CELEBA_ATTR_NAMES = [
    "5_o_Clock_Shadow", "Arched_Eyebrows", "Attractive", "Bags_Under_Eyes", "Bald",
    "Bangs", "Big_Lips", "Big_Nose", "Black_Hair", "Blond_Hair", "Blurry",
    "Brown_Hair", "Bushy_Eyebrows", "Chubby", "Double_Chin", "Eyeglasses",
    "Goatee", "Gray_Hair", "Heavy_Makeup", "High_Cheekbones", "Male",
    "Mouth_Slightly_Open", "Mustache", "Narrow_Eyes", "No_Beard", "Oval_Face",
    "Pale_Skin", "Pointy_Nose", "Receding_Hairline", "Rosy_Cheeks", "Sideburns",
    "Smiling", "Straight_Hair", "Wavy_Hair", "Wearing_Earrings", "Wearing_Hat",
    "Wearing_Lipstick", "Wearing_Necklace", "Wearing_Necktie", "Young",
]
ATTR_NAME_TO_IDX = {n.lower(): i for i, n in enumerate(CELEBA_ATTR_NAMES)}


def attr_indices(attrs: list[str]) -> list[int]:
    """attribute name → CelebA tensor 中的列索引."""
    return [ATTR_NAME_TO_IDX[a.lower()] for a in attrs]


class CelebASubset(Dataset):
    """CelebA + 选定 K 个 attributes,以 ±1 (0/1) 编码,缩放到指定分辨率."""

    def __init__(
        self,
        root: str | Path = "data/",
        attrs: list[str] | None = None,
        resolution: int = 64,
        split: str = "train",
        download: bool = True,
    ):
        attrs = attrs or ["smiling", "eyeglasses", "male", "young"]
        self.attrs = attrs
        self.attr_idx = attr_indices(attrs)

        self.transform = transforms.Compose([
            transforms.Resize(resolution),
            transforms.CenterCrop(resolution),
            transforms.ToTensor(),
            transforms.Normalize([0.5] * 3, [0.5] * 3),  # → [-1, 1]
        ])

        try:
            self.dataset = CelebA(
                root=str(root), split=split, target_type="attr",
                transform=self.transform, download=download,
            )
        except Exception as e:
            raise RuntimeError(
                f"CelebA 自动下载失败: {e}\n"
                f"手动下: https://www.kaggle.com/datasets/jessicali9530/celeba-dataset 解压到 {root}/celeba/"
            )

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> dict:
        img, attr_full = self.dataset[idx]
        # CelebA attributes 是 0/1 的 long tensor; 取我们要的 K 个
        attr = attr_full[self.attr_idx].float()  # (K,) ∈ {0., 1.}
        return {"image": img, "attr": attr}


def get_dataloader(
    root: str | Path = "data/",
    attrs: list[str] | None = None,
    resolution: int = 64,
    batch_size: int = 128,
    split: str = "train",
    num_workers: int = 4,
    shuffle: bool = True,
) -> DataLoader:
    ds = CelebASubset(root=root, attrs=attrs, resolution=resolution, split=split)
    return DataLoader(
        ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
        pin_memory=torch.cuda.is_available(), drop_last=True,
    )


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--root", default="data/")
    p.add_argument("--attrs", nargs="+", default=["smiling", "eyeglasses", "male", "young"])
    p.add_argument("--resolution", type=int, default=64)
    p.add_argument("--batch-size", type=int, default=8)
    args = p.parse_args()

    loader = get_dataloader(
        root=args.root, attrs=args.attrs, resolution=args.resolution,
        batch_size=args.batch_size, num_workers=0, shuffle=False,
    )
    print(f"Dataset size: {len(loader.dataset)}")
    batch = next(iter(loader))
    print(f"Image: {batch['image'].shape}, range [{batch['image'].min():.2f}, {batch['image'].max():.2f}]")
    print(f"Attr: {batch['attr'].shape}, sample row: {batch['attr'][0].tolist()} → {args.attrs}")
