"""ECE175B HW2 — VAE on Chest X-ray Pneumonia dataset.

End-to-end script for Kaggle:
  Input: /kaggle/input/chest-xray-pneumonia/chest_xray/
  Output: /kaggle/working/{loss_curve.png, samples.png, metrics.txt, model.pt}

Architecture: Conv β-VAE, 64×64 grayscale, latent=128.
Training: 30 epochs, AdamW 2e-3, KL warmup over first 10 epochs.
Evaluation: FID + Inception Score (via pytorch-ignite) on 1000 generated samples.

Usage on Kaggle:
  1) Add dataset 'paultimothymooney/chest-xray-pneumonia' as input
  2) Set Accelerator = GPU (T4 free)
  3) Run all cells
  Total runtime: ~30-45 min on T4.
"""

from __future__ import annotations

import os
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, ConcatDataset
from torchvision import datasets, transforms
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────
SEED = 42
IMG_SIZE = 64
LATENT_DIM = 128
BATCH = 128
EPOCHS = 30
LR = 2e-3
WD = 1e-5
BETA_MAX = 1.0      # KL weight after warmup
WARMUP_EPOCHS = 10  # linear KL annealing schedule

KAGGLE_DATA_ROOT = "/kaggle/input/chest-xray-pneumonia/chest_xray"
LOCAL_DATA_ROOT = "./chest_xray"  # fallback for local run
OUT_DIR = Path("/kaggle/working") if Path("/kaggle/working").exists() else Path("./outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

torch.manual_seed(SEED)
np.random.seed(SEED)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[setup] device={DEVICE} | out_dir={OUT_DIR}")

# ──────────────────────────────────────────────────────────────────
# Data
# ──────────────────────────────────────────────────────────────────
TRANSFORM = transforms.Compose(
    [
        transforms.Grayscale(num_output_channels=1),
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),  # → [0, 1]
    ]
)

def load_chest_xray():
    """Loads all chest x-ray images (train+val+test, both classes) for VAE training.

    VAE is unsupervised, so we ignore labels and pool all available images.
    """
    root = KAGGLE_DATA_ROOT if Path(KAGGLE_DATA_ROOT).exists() else LOCAL_DATA_ROOT
    splits = ["train", "val", "test"]
    sets = []
    for s in splits:
        path = Path(root) / s
        if path.exists():
            sets.append(datasets.ImageFolder(str(path), transform=TRANSFORM))
    if not sets:
        raise FileNotFoundError(f"No chest_xray data at {root}. "
                                f"Add Kaggle dataset 'paultimothymooney/chest-xray-pneumonia'.")
    full = ConcatDataset(sets)
    print(f"[data] total images = {len(full)} (pooled across {[s for s in splits if (Path(root)/s).exists()]})")
    return full

DATASET = load_chest_xray()
LOADER = DataLoader(DATASET, batch_size=BATCH, shuffle=True, num_workers=2, pin_memory=True, drop_last=True)

# ──────────────────────────────────────────────────────────────────
# VAE Model
# ──────────────────────────────────────────────────────────────────
class ConvVAE(nn.Module):
    """Symmetric Conv β-VAE, 64×64×1 → latent=128 → 64×64×1."""

    def __init__(self, latent_dim=128):
        super().__init__()
        self.latent_dim = latent_dim
        # Encoder: 64×64 → 4×4×256
        self.enc = nn.Sequential(
            nn.Conv2d(1, 32, 4, stride=2, padding=1), nn.GroupNorm(8, 32), nn.SiLU(),   # 32×32
            nn.Conv2d(32, 64, 4, stride=2, padding=1), nn.GroupNorm(8, 64), nn.SiLU(),  # 16×16
            nn.Conv2d(64, 128, 4, stride=2, padding=1), nn.GroupNorm(8, 128), nn.SiLU(),# 8×8
            nn.Conv2d(128, 256, 4, stride=2, padding=1), nn.GroupNorm(8, 256), nn.SiLU(),# 4×4
        )
        self.fc_mu = nn.Linear(256 * 4 * 4, latent_dim)
        self.fc_lv = nn.Linear(256 * 4 * 4, latent_dim)
        # Decoder: latent → 4×4×256 → 64×64×1
        self.fc_dec = nn.Linear(latent_dim, 256 * 4 * 4)
        self.dec = nn.Sequential(
            nn.ConvTranspose2d(256, 128, 4, stride=2, padding=1), nn.GroupNorm(8, 128), nn.SiLU(),
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1), nn.GroupNorm(8, 64), nn.SiLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1), nn.GroupNorm(8, 32), nn.SiLU(),
            nn.ConvTranspose2d(32, 1, 4, stride=2, padding=1),   # logits
        )

    def encode(self, x):
        h = self.enc(x).flatten(1)
        return self.fc_mu(h), self.fc_lv(h)

    def reparam(self, mu, lv):
        std = torch.exp(0.5 * lv)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h = self.fc_dec(z).view(-1, 256, 4, 4)
        return self.dec(h)  # logits

    def forward(self, x):
        mu, lv = self.encode(x)
        z = self.reparam(mu, lv)
        return self.decode(z), mu, lv


def vae_loss(logits, x, mu, lv, beta):
    """ELBO loss: BCE recon + β·KL. Returns per-sample average."""
    bce = F.binary_cross_entropy_with_logits(logits, x, reduction="sum") / x.size(0)
    kl = -0.5 * torch.sum(1 + lv - mu.pow(2) - lv.exp()) / x.size(0)
    return bce + beta * kl, bce.detach(), kl.detach()


# ──────────────────────────────────────────────────────────────────
# Train
# ──────────────────────────────────────────────────────────────────
model = ConvVAE(LATENT_DIM).to(DEVICE)
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
print(f"[model] params = {sum(p.numel() for p in model.parameters())/1e6:.2f} M")

history = {"epoch": [], "loss": [], "bce": [], "kl": [], "beta": []}
t0 = time.time()
for epoch in range(EPOCHS):
    model.train()
    beta = BETA_MAX * min(1.0, (epoch + 1) / WARMUP_EPOCHS)  # KL warmup
    sums = {"loss": 0.0, "bce": 0.0, "kl": 0.0, "n": 0}
    for x, _ in LOADER:
        x = x.to(DEVICE, non_blocking=True)
        logits, mu, lv = model(x)
        loss, bce, kl = vae_loss(logits, x, mu, lv, beta)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        opt.step()
        sums["loss"] += loss.item() * x.size(0)
        sums["bce"] += bce.item() * x.size(0)
        sums["kl"] += kl.item() * x.size(0)
        sums["n"] += x.size(0)
    avg = {k: sums[k] / sums["n"] for k in ("loss", "bce", "kl")}
    history["epoch"].append(epoch + 1)
    history["loss"].append(avg["loss"])
    history["bce"].append(avg["bce"])
    history["kl"].append(avg["kl"])
    history["beta"].append(beta)
    dt = time.time() - t0
    print(f"[epoch {epoch+1:02d}/{EPOCHS}] loss={avg['loss']:.2f} bce={avg['bce']:.2f} kl={avg['kl']:.2f} β={beta:.2f} elapsed={dt/60:.1f}min")

torch.save(model.state_dict(), OUT_DIR / "model.pt")
print(f"[save] model → {OUT_DIR/'model.pt'}")

# Loss curve
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
ax[0].plot(history["epoch"], history["loss"], label="total")
ax[0].plot(history["epoch"], history["bce"], label="recon (BCE)")
ax[0].set_xlabel("epoch"); ax[0].set_ylabel("loss"); ax[0].legend(); ax[0].set_title("Total / Recon Loss")
ax[1].plot(history["epoch"], history["kl"], label="KL", color="C2")
ax2 = ax[1].twinx(); ax2.plot(history["epoch"], history["beta"], color="C3", linestyle="--", label="β"); ax2.set_ylabel("β", color="C3")
ax[1].set_xlabel("epoch"); ax[1].set_ylabel("KL"); ax[1].set_title("KL Divergence + β Warmup")
plt.tight_layout()
plt.savefig(OUT_DIR / "loss_curve.png", dpi=150, bbox_inches="tight")
print(f"[save] loss curve → {OUT_DIR/'loss_curve.png'}")

# ──────────────────────────────────────────────────────────────────
# Generate samples
# ──────────────────────────────────────────────────────────────────
model.eval()
N_GEN = 1000
with torch.no_grad():
    z = torch.randn(N_GEN, LATENT_DIM, device=DEVICE)
    gen = torch.sigmoid(model.decode(z)).cpu()  # (N, 1, 64, 64), values [0,1]

# Save 16 samples as a grid
fig, axes = plt.subplots(4, 4, figsize=(8, 8))
for i, ax in enumerate(axes.flatten()):
    ax.imshow(gen[i, 0].numpy(), cmap="gray")
    ax.axis("off")
plt.suptitle("VAE Generated Chest X-rays (16 samples)")
plt.tight_layout()
plt.savefig(OUT_DIR / "samples.png", dpi=150, bbox_inches="tight")
print(f"[save] samples grid → {OUT_DIR/'samples.png'}")

# ──────────────────────────────────────────────────────────────────
# FID + Inception Score (pytorch-ignite recipe)
# ──────────────────────────────────────────────────────────────────
# Reference: https://pytorch-ignite.ai/blog/gan-evaluation-with-fid-and-is/
try:
    from ignite.metrics import FID, InceptionScore
except ImportError:
    print("[warn] pytorch-ignite not found, installing...")
    os.system("pip install -q pytorch-ignite")
    from ignite.metrics import FID, InceptionScore

# Prepare real samples (1000 from test split, or random subset of full dataset)
real_loader = DataLoader(DATASET, batch_size=64, shuffle=True, num_workers=2)
real_imgs = []
for x, _ in real_loader:
    real_imgs.append(x)
    if sum(b.size(0) for b in real_imgs) >= N_GEN:
        break
real_imgs = torch.cat(real_imgs)[:N_GEN]  # (N, 1, 64, 64)

def to_inception_input(x_1ch):
    """Convert (N, 1, 64, 64) [0,1] → (N, 3, 299, 299) uint8 for InceptionV3."""
    x = x_1ch.expand(-1, 3, -1, -1)  # repeat grayscale to 3 channels
    x = F.interpolate(x, size=(299, 299), mode="bilinear", align_corners=False)
    return x.clamp(0, 1)

print("[eval] computing FID + IS on 1000 generated vs 1000 real samples...")
fid_metric = FID(device=DEVICE)
is_metric = InceptionScore(device=DEVICE)
BATCH_EVAL = 32
for i in range(0, N_GEN, BATCH_EVAL):
    gen_b = to_inception_input(gen[i:i+BATCH_EVAL]).to(DEVICE)
    real_b = to_inception_input(real_imgs[i:i+BATCH_EVAL]).to(DEVICE)
    fid_metric.update((gen_b, real_b))
    is_metric.update(gen_b)

fid_value = float(fid_metric.compute())
is_value = float(is_metric.compute())
print(f"[eval] FID = {fid_value:.2f} | IS = {is_value:.2f}")

# ──────────────────────────────────────────────────────────────────
# Save metrics
# ──────────────────────────────────────────────────────────────────
metrics = {
    "fid": round(fid_value, 2),
    "inception_score": round(is_value, 2),
    "final_loss": round(history["loss"][-1], 2),
    "final_bce": round(history["bce"][-1], 2),
    "final_kl": round(history["kl"][-1], 2),
    "n_params_million": round(sum(p.numel() for p in model.parameters()) / 1e6, 2),
    "n_images_train": len(DATASET),
    "n_samples_generated": N_GEN,
    "img_size": IMG_SIZE,
    "latent_dim": LATENT_DIM,
    "batch_size": BATCH,
    "epochs": EPOCHS,
    "lr": LR,
    "weight_decay": WD,
    "beta_max": BETA_MAX,
    "warmup_epochs": WARMUP_EPOCHS,
    "wall_time_minutes": round((time.time() - t0) / 60, 1),
}
with open(OUT_DIR / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[save] metrics → {OUT_DIR/'metrics.json'}")
print(json.dumps(metrics, indent=2))

# Also save training history CSV for plotting in report if needed
import csv
with open(OUT_DIR / "history.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(history.keys()))
    w.writeheader()
    for row in zip(*history.values()):
        w.writerow(dict(zip(history.keys(), row)))
print(f"[save] history → {OUT_DIR/'history.csv'}")
print(f"\n[done] total wall time: {(time.time()-t0)/60:.1f} min")
