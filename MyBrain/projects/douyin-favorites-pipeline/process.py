"""
Process a single Douyin URL file: extract URL -> download -> transcribe -> markdown.
"""

import logging
import os
import re
import json
import hashlib
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from transcribe import transcribe_audio
from generate_md import generate_markdown, generate_markdown_partial

logger = logging.getLogger(__name__)

# Python 3.14's bundled pyexpat needs newer libexpat symbols than what macOS
# ships in /usr/lib/libexpat.1.dylib. Point dyld at Homebrew's expat for any
# subprocess (yt-dlp) we spawn. Belt-and-suspenders alongside the plist's
# EnvironmentVariables — launchd's SIP-strip behavior can be quirky.
EXPAT_LIB_PATH = "/opt/homebrew/opt/expat/lib"


def _subprocess_env() -> dict:
    """Build env dict with DYLD_LIBRARY_PATH prepended for expat fix."""
    env = os.environ.copy()
    existing = env.get("DYLD_LIBRARY_PATH", "")
    env["DYLD_LIBRARY_PATH"] = (
        f"{EXPAT_LIB_PATH}:{existing}" if existing else EXPAT_LIB_PATH
    )
    return env

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
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600,
            env=_subprocess_env(),
        )
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
    text = ""
    url = None
    output_dir = vault_path / "MyBrain" / "raw" / "douyin-favorites"
    try:
        # 1. Extract URL — unrecoverable failure if missing
        text = input_file.read_text(encoding="utf-8")
        url = extract_url(text)
        if not url:
            raise ValueError("No Douyin URL found in file")
        result["url"] = url
        logger.info(f"Extracted URL: {url}")

        # 2. Try download + transcribe + full .md. If yt-dlp fails (e.g.,
        # Douyin anti-bot — see yt-dlp issue #12669), fall back to URL-only
        # archival so vault always has at least an index entry.
        cache_dir = cache_base / cache_id_for(url)
        try:
            video_path, metadata = download_video(url, cache_dir)
            segments = transcribe_audio(video_path)
            md_path = generate_markdown(metadata, segments, output_dir)
            result["status"] = "success"
            result["output_path"] = str(md_path)
            logger.info(f"Processing complete (FULL): {md_path.name}")
            cleanup_cache(cache_dir)
        except RuntimeError as download_err:
            # Download/transcribe failed — write partial .md as fallback.
            # Keep cache_dir for debugging; gets cleaned on next retry.
            logger.warning(
                f"Video download/transcribe failed: {download_err}. "
                f"Falling back to URL-only .md (vault will still get index entry)."
            )
            md_path = generate_markdown_partial(
                raw_text=text, url=url, output_dir=output_dir,
                error_reason=str(download_err),
            )
            result["status"] = "partial"
            result["output_path"] = str(md_path)
            result["error"] = str(download_err)
            logger.info(f"Processing complete (PARTIAL — URL only): {md_path.name}")

    except Exception as e:
        # Genuinely unrecoverable: file unreadable, no URL, generate_md crashed.
        result["error"] = str(e)
        logger.error(f"Processing failed for {input_file.name}: {e}", exc_info=True)

    finally:
        result["duration_sec"] = (datetime.now() - start_time).total_seconds()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result
