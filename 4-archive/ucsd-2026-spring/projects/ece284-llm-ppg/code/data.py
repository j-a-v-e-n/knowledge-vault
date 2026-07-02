"""data.py — IEEE SPC 2015 TROIKA dataset download + load utilities.

ECE 284 LLM-PPG project. Provides:
  - download_subject(subj_id, type_id): idempotent fetch of DATA + REF .mat
  - load_subject(subj_id, type_id):     returns (sig (6,N), bpm0 (W,) flattened)

数据源 Udacity nd320-c4 mirror (镜像 Zhang 2015 IEEE SPC 训练集).
"""

from pathlib import Path
import urllib.request

import scipy.io


# ===================================================================
# 路径配置
# ===================================================================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


# ===================================================================
# 下载源
# ===================================================================
DATA_URL_BASE = (
    "https://github.com/udacity/nd320-c4-wearable-data-project-starter"
    "/raw/master/part_1/datasets/troika/training_data/"
)


def _fmt_id(x) -> str:
    """Accept int or str. Return zero-padded 2-char string ("01", "12", …)."""
    if isinstance(x, int):
        return f"{x:02d}"
    return str(x)


def download_subject(subj_id, type_id):
    """Download DATA_XX_TYPEXX.mat + REF_XX_TYPEXX.mat into code/data/.

    Idempotent: 已存在则 skip. Returns (data_path, ref_path).
    """
    subj_str = _fmt_id(subj_id)
    type_str = _fmt_id(type_id)

    paths = []
    for prefix in ("DATA", "REF"):
        filename = f"{prefix}_{subj_str}_TYPE{type_str}.mat"
        local_path = DATA_DIR / filename
        if local_path.exists():
            size_kb = local_path.stat().st_size / 1024
            print(f"[skip] {filename} already at {local_path} ({size_kb:.1f} KB)")
        else:
            url = DATA_URL_BASE + filename
            print(f"[download] {url}")
            print(f"          → {local_path}")
            urllib.request.urlretrieve(url, local_path)
            size_kb = local_path.stat().st_size / 1024
            print(f"[done]    {filename} {size_kb:.1f} KB")
        paths.append(local_path)
    return paths[0], paths[1]


def load_subject(subj_id, type_id):
    """Load DATA + REF .mat. Returns (sig, bpm0_flat).

    sig:        (6, N) np.ndarray   行 0=ECG, 1=PPG ch1, 2=PPG ch2, 3-5=accel XYZ
    bpm0_flat:  (W,)   np.ndarray   ECG-derived HR ground truth (BPM, 已 flatten)

    Auto-downloads if missing.  loadmat 失败 / 缺 key → 立即 raise ValueError, 不 fallback.
    """
    data_path, ref_path = download_subject(subj_id, type_id)

    # ---------- DATA file ----------
    try:
        data_mat = scipy.io.loadmat(data_path)
    except Exception as e:
        raise ValueError(
            f"loadmat failed on {data_path.name}: {type(e).__name__}: {e}"
        )
    if "sig" not in data_mat:
        avail = ", ".join(repr(k) for k in data_mat.keys())
        raise ValueError(
            f"Expected key 'sig' not found in {data_path.name}. "
            f"Available keys: [{avail}]"
        )
    sig = data_mat["sig"]

    # ---------- REF file ----------
    try:
        ref_mat = scipy.io.loadmat(ref_path)
    except Exception as e:
        raise ValueError(
            f"loadmat failed on {ref_path.name}: {type(e).__name__}: {e}"
        )
    if "BPM0" not in ref_mat:
        avail = ", ".join(repr(k) for k in ref_mat.keys())
        raise ValueError(
            f"Expected key 'BPM0' not found in {ref_path.name}. "
            f"Available keys: [{avail}]"
        )
    bpm0 = ref_mat["BPM0"].flatten()

    return sig, bpm0
