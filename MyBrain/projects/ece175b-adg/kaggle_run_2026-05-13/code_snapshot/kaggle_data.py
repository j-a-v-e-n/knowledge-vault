
"""Kaggle-specific data wrapper for CelebA.

Kaggle CelebA dataset structure:
/kaggle/input/celeba-dataset/
  img_align_celeba/img_align_celeba/  <- images
  list_attr_celeba.csv                <- attributes

torchvision CelebA expects:
  <root>/celeba/img_align_celeba/     <- images
  <root>/celeba/list_attr_celeba.txt  <- attributes

So we need to manually point to Kaggle paths.
"""
from pathlib import Path
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from PIL import Image
import pandas as pd

# Kaggle CelebA paths
KAGGLE_IMG_DIR = Path("/kaggle/input/datasets/jessicali9530/celeba-dataset/img_align_celeba/img_align_celeba")
KAGGLE_ATTR_CSV = Path("/kaggle/input/datasets/jessicali9530/celeba-dataset/list_attr_celeba.csv")

ATTR_NAMES = [
    "5_o_Clock_Shadow", "Arched_Eyebrows", "Attractive", "Bags_Under_Eyes", "Bald",
    "Bangs", "Big_Lips", "Big_Nose", "Black_Hair", "Blond_Hair", "Blurry",
    "Brown_Hair", "Bushy_Eyebrows", "Chubby", "Double_Chin", "Eyeglasses",
    "Goatee", "Gray_Hair", "Heavy_Makeup", "High_Cheekbones", "Male",
    "Mouth_Slightly_Open", "Mustache", "Narrow_Eyes", "No_Beard", "Oval_Face",
    "Pale_Skin", "Pointy_Nose", "Receding_Hairline", "Rosy_Cheeks", "Sideburns",
    "Smiling", "Straight_Hair", "Wavy_Hair", "Wearing_Earrings", "Wearing_Hat",
    "Wearing_Lipstick", "Wearing_Necklace", "Wearing_Necktie", "Young",
]
ATTR_NAME_TO_IDX = {n.lower(): i for i, n in enumerate(ATTR_NAMES)}

def attr_indices(attrs):
    return [ATTR_NAME_TO_IDX[a.lower()] for a in attrs]

class KaggleCelebASubset(Dataset):
    def __init__(self, attrs=None, resolution=64, split="train"):
        attrs = attrs or ["smiling", "eyeglasses", "male", "young"]
        self.attrs = attrs
        self.attr_idx = attr_indices(attrs)
        self.resolution = resolution
        
        # Load attribute CSV
        df = pd.read_csv(KAGGLE_ATTR_CSV)
        # CSV columns: image_id, attr1, attr2, ... (40 attrs)
        # Values: 1 or -1 → convert to 0/1
        self.image_names = df.iloc[:, 0].tolist()
        attr_cols = df.columns[1:]
        attr_matrix = df[attr_cols].values  # (N, 40)
        attr_matrix = (attr_matrix + 1) // 2  # -1→0, 1→1
        self.attr_matrix = torch.tensor(attr_matrix, dtype=torch.float32)
        
        # Split: use first 80% for train, last 20% for val (simple split)
        n = len(self.image_names)
        if split == "train":
            self.indices = list(range(int(n * 0.8)))
        else:
            self.indices = list(range(int(n * 0.8), n))
        
        self.transform = transforms.Compose([
            transforms.Resize(resolution),
            transforms.CenterCrop(resolution),
            transforms.ToTensor(),
            transforms.Normalize([0.5] * 3, [0.5] * 3),
        ])
    
    def __len__(self):
        return len(self.indices)
    
    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        img_name = self.image_names[real_idx]
        img_path = KAGGLE_IMG_DIR / img_name
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)
        
        attr = self.attr_matrix[real_idx][self.attr_idx]
        return {"image": img, "attr": attr}

def get_kaggle_dataloader(attrs=None, resolution=64, batch_size=128, split="train", num_workers=2, shuffle=True):
    ds = KaggleCelebASubset(attrs=attrs, resolution=resolution, split=split)
    return DataLoader(
        ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
        pin_memory=torch.cuda.is_available(), drop_last=True,
    )
