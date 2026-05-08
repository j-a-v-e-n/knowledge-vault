"""
Process a single Douyin URL file: extract URL -> download -> transcribe -> markdown.
"""

import logging
import re
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from transcribe import transcribe_audio
from generate_md import generate_markdown

logger = logging.getLogger(__name__)

# Regex patterns for Douyin URLs (try in order, use first match).
# Note: Douyin short-link IDs may contain letters, digits, '-', '_'.
URL_PATTERNS = [
    r'https?://v\.douyin\.com/[\w-]+/?',
    r'https?://(?:www\.)?douyin\.com/share/video/\d+',
    r'https?://(?:www\.)?douyin\.com/video/\d+',
    r'https?://(?:www\.)?iesdouyin\.com/share/video/\d+',
]

# Acceptable video file extensions yt-dlp may produce
VIDEO_EXTS = {'.mp4', '.mov', '.webm', '.mkv', '.m4v'}


def extract_url(text: str) -> Optional[str]:
    """Extract first matching Douyin URL from arbitrary text (regardless of language/prefix)."""
    for pattern in URL_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def cache_id_for(url: str) -> str:
    """Stable, collision-free cache directory id derived from URL."""
    return hashlib.md5(url.encode('utf-8')).hexdigest()[:10]


def download_video(url: str, cache_dir: Path) -> tuple[Path, dict]:
    """
    Download video and metadata using yt-dlp.

    Returns:
        (video_path, metadata_dict)

    Raises:
        RuntimeError: If download fails or expected files missing.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(cache_dir / "%(id)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--write-info-json",
        "--format", "best",
        "--output", output_template,
        url,
    ]

    logger.info(f"Downloading: {url}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            raise RuntimeError(f"yt-dlp failed (exit {result.returncode}): {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp timed out after 10 minutes")
    except FileNotFoundError:
        raise RuntimeError("yt-dlp binary not found in PATH — run setup.sh first")

    # Find downloaded files (multi-format support)
    video_files = [p for p in cache_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS]
    json_files = list(cache_dir.glob("*.info.json"))

    if not video_files:
        raise RuntimeError(f"No video file produced in {cache_dir} (expected one of {VIDEO_EXTS})")
    if not json_files:
        raise RuntimeError(f"No .info.json metadata produced in {cache_dir}")

    video_path = video_files[0]
    json_path = json_files[0]

    with open(json_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    logger.info(f"Downloaded: {video_path.name} ({video_path.stat().st_size // 1024} KB)")
    return video_path, metadata


def cleanup_cache(cache_dir: Path) -> None:
    """Remove cache subdir after successful processing (best-effort)."""
    try:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            logger.info(f"Cleaned cache: {cache_dir.name}")
    except Exception as e:
        logger.warning(f"Cache cleanup failed for {cache_dir}: {e}")


def process_one(input_file: Path, vault_path: Path, cache_base: Path, log_path: Path) -> dict:
    """
    Process one .txt file: extract URL -> download -> transcribe -> generate markdown.

    Returns:
        Result dict with status, output_path, error.
    """
    start_time = datetime.now()
    result = {
        "input_file": str(input_file),
        "status": "failed",
        "timestamp": start_time.isoformat(),
        "error": None,
        "output_path": None,
        "duration_sec": 0,
        "url": None,
    }

    cache_dir = None
    try:
        # 1. Extract URL
        text = input_file.read_text(encoding="utf-8")
        url = extract_url(text)
        if not url:
            raise ValueError("No Douyin URL found in file")
        result["url"] = url
        logger.info(f"Extracted URL: {url}")

        # 2. Download (cache dir derived from URL hash — no collisions)
        cache_dir = cache_base / cache_id_for(url)
        video_path, metadata = download_video(url, cache_dir)

        # 3. Transcribe
        segments = transcribe_audio(video_path)

        # 4. Generate markdown
        output_dir = vault_path / "MyBrain" / "raw" / "douyin-favorites"
        md_path = generate_markdown(metadata, segments, output_dir)

        result["status"] = "success"
        result["output_path"] = str(md_path)
        logger.info(f"Processing complete: {md_path.name}")

        # 5. Clean up cache (only on success — keep on failure for debugging)
        cleanup_cache(cache_dir)

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Processing failed for {input_file.name}: {e}", exc_info=True)

    finally:
        result["duration_sec"] = (datetime.now() - start_time).total_seconds()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result
