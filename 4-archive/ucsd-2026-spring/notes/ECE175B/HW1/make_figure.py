"""Generate the UniStory architecture figure for ECE175B HW1.

Layout:
    [c] [⟨SK⟩] [s̃] [⟨FS⟩] [s]   |   image patches z_t          ← input sequence
                              │
                    Unified Transformer  (L layers)
                              │
                ┌────── splits to two heads ──────┐
           Text Head                         Diffusion Head
       (emit s̃ after ⟨SK⟩,                   (ε-prediction)
        emit s after ⟨FS⟩)                        │
                                            Image Latent z_0
                                                  │
                                            VAE Decoder D
                                                  │
                                               Image I

    Dashed attention cue: image block attends to preceding text ⇒
    diffusion head conditioned on c and generated story s.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(8.8, 6.6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Colors
C_TEXT_TOK = '#BBDEFB'
C_SEP      = '#FFCCBC'
C_IMG_TOK  = '#C8E6C9'
C_TRANS    = '#1565C0'
C_HEAD_T   = '#FFE0B2'
C_HEAD_I   = '#A5D6A7'
C_VAE      = '#81C784'
C_OUT      = '#F5F5F5'
EDGE       = '#37474F'


def box(x, y, w, h, text, fc, fontsize=10, textcolor='black', bold=False):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.12",
                       linewidth=1.1, edgecolor=EDGE, facecolor=fc)
    ax.add_patch(b)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
            fontsize=fontsize, color=textcolor, weight=weight)


def arrow(x1, y1, x2, y2, label=None, rad=0.0, label_xy=None,
          label_fontsize=7.5, dashed=False, color=None):
    style = "Simple, tail_width=0.5, head_width=4, head_length=6"
    kwargs = dict(arrowstyle=style,
                  connectionstyle=f"arc3,rad={rad}",
                  color=color or EDGE, linewidth=1.1)
    if dashed:
        kwargs['linestyle'] = (0, (3, 2))
    a = FancyArrowPatch((x1, y1), (x2, y2), **kwargs)
    ax.add_patch(a)
    if label:
        if label_xy is None:
            lx, ly = (x1 + x2) / 2 + 0.15, (y1 + y2) / 2
        else:
            lx, ly = label_xy
        ax.text(lx, ly, label, fontsize=label_fontsize,
                color='#455A64', style='italic')


# ─────────── Title ───────────
ax.text(5.0, 9.68, 'UniStory  Architecture',
        ha='center', fontsize=13, weight='bold')

# ─────────── Input sequence (top strip) ───────────
ax.text(5.0, 9.18, 'Mixed-modal input sequence',
        ha='center', fontsize=8.5, style='italic', color='#455A64')

# Text tokens: c | ⟨SK⟩ | s̃ | ⟨FS⟩ | s
box(0.25, 8.35, 0.75, 0.60, r'$c$',                     C_TEXT_TOK, fontsize=11)
box(1.07, 8.35, 0.95, 0.60, r'$\langle\mathrm{SK}\rangle$', C_SEP,      fontsize=9.5)
box(2.09, 8.35, 1.20, 0.60, r'$\tilde{s}$',             C_TEXT_TOK, fontsize=11)
box(3.36, 8.35, 0.95, 0.60, r'$\langle\mathrm{FS}\rangle$', C_SEP,      fontsize=9.5)
box(4.38, 8.35, 1.85, 0.60, r'$s$',                     C_TEXT_TOK, fontsize=11)
# Image patches block
box(6.45, 8.35, 3.30, 0.60, r'image patches  $z_t$',    C_IMG_TOK,  fontsize=9.5)

# Sub-labels under token groups
ax.text(3.24, 8.05, 'text tokens  (sketch-then-expand)',
        ha='center', fontsize=7.3, color='#546E7A', style='italic')
ax.text(8.10, 8.05, 'image block',
        ha='center', fontsize=7.3, color='#546E7A', style='italic')

# Dashed attention arrow: image patches attend back to c and s
# Start: left edge of image block (6.45, 8.65); end: near right edge of s token (6.20, 8.65)
arrow(6.45, 8.65, 6.24, 8.65, rad=0.0, dashed=True, color='#6D4C41')
# A curved one going to c as well (longer range, above the sequence)
arrow(6.55, 8.95, 0.70, 8.95, rad=0.22, dashed=True, color='#6D4C41',
      label=r'attention: image block sees preceding text',
      label_xy=(2.35, 9.52), label_fontsize=7.0)

# ─────────── Arrow: sequence → transformer ───────────
arrow(5.0, 8.35, 5.0, 7.55)

# ─────────── Transformer ───────────
box(0.30, 6.05, 9.40, 1.50,
    'Unified Transformer  (L layers)\n'
    'shared self-attention over text tokens + image patches\n'
    'causal mask on text  ·  bidirectional within image block',
    C_TRANS, fontsize=9.5, textcolor='white', bold=True)

# ─────────── Two heads ───────────
box(0.70, 4.25, 3.80, 1.15, 'Text Head\n(AR softmax)',
    C_HEAD_T, fontsize=10.5)
box(5.50, 4.25, 3.80, 1.15, 'Diffusion Head\n($\\epsilon$-prediction)',
    C_HEAD_I, fontsize=10.5)

# Transformer → heads
arrow(2.60, 6.05, 2.60, 5.40, label='text logits', label_xy=(2.73, 5.68))
arrow(7.40, 6.05, 7.40, 5.40, label=r'image $\epsilon$',    label_xy=(7.53, 5.68))

# ─────────── Text head output ───────────
box(0.70, 1.80, 3.80, 1.95,
    'emit  $\\tilde{s}$  after  $\\langle\\mathrm{SK}\\rangle$\n'
    r'($\leq 50$ tokens, narrative sketch)'
    '\n\n'
    'emit  $s$  after  $\\langle\\mathrm{FS}\\rangle$\n'
    r'($\sim 500$ tokens, full story)',
    C_OUT, fontsize=9)
arrow(2.60, 4.25, 2.60, 3.75)

# ─────────── Diffusion head → image latent → VAE → image ───────────
box(5.50, 2.95, 3.80, 0.60, r'Image Latent  $z_0$', C_OUT, fontsize=10)
arrow(7.40, 4.25, 7.40, 3.55)

box(5.50, 1.70, 3.80, 0.75, 'VAE Decoder  $D$  (frozen)',
    C_VAE, fontsize=10)
arrow(7.40, 2.95, 7.40, 2.45)

box(5.50, 0.30, 3.80, 0.95, 'Image  $I$', C_OUT, fontsize=11.5, bold=True)
arrow(7.40, 1.70, 7.40, 1.25)

# ─────────── Conditioning: story s → diffusion head (the key new arrow) ───────────
# From top of text-head output box (≈ x=4.50, y=3.75) curving up to
# bottom-left of diffusion head (≈ x=5.50, y=4.25).
arrow(4.50, 3.40, 5.50, 4.35,
      label=r'$s$ conditions',
      label_xy=(4.55, 3.88),
      label_fontsize=7.5,
      rad=-0.30)

plt.savefig(
    '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/'
    'My Drive/知识库/MyBrain/inbox/ECE175B_HW1_files/unistory_architecture.png',
    bbox_inches='tight', dpi=300, facecolor='white'
)
print("Architecture figure saved.")
