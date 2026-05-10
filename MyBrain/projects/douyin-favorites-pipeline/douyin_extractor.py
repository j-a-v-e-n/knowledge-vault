"""
Douyin video extractor — Playwright (mobile UA) + direct mp4 download.

Bypasses yt-dlp's broken Douyin support (yt-dlp issue #12669) by:
1. Loading the share URL with iPhone Mobile Safari user-agent
2. Auto-redirects to iesdouyin.com share page (which doesn't require login)
3. Extracting <video> element's src — which points at the
   /aweme/v1/playwm/ endpoint (publicly downloadable mp4)
4. Direct curl-style download with mobile UA

Requires: playwright (pip) + chromium (`playwright install chromium`)

This module mimics yt-dlp's download_video() return signature so process.py
stays unchanged in shape.
"""

import asyncio
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Apple iOS Safari mobile UA — what makes douyin redirect to iesdouyin (mobile share page)
# instead of pc client install prompt
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 "
    "Mobile/15E148 Safari/604.1"
)


async def _extract_video_metadata(url: str) -> Dict[str, Any]:
    """
    Load Douyin share URL with mobile UA and extract video src + page metadata.

    Returns dict with: video_src, title, uploader, final_url, video_id
    Raises RuntimeError if no <video> element appears.
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, channel="chromium")
        context = await browser.new_context(
            user_agent=MOBILE_UA,
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                await page.wait_for_selector("video", timeout=20000)
            except Exception:
                logger.warning("video element didn't appear within 20s; trying to extract anyway")
            # Brief settle for video src to populate
            await asyncio.sleep(3)

            video_src = await page.evaluate("""() => {
                const v = document.querySelector('video');
                return v ? v.src : null;
            }""")
            if not video_src:
                raise RuntimeError("No <video> element with src found on page")

            # Title — from <title>, strip trailing "- 抖音" or similar
            title_raw = await page.evaluate(
                "() => document.querySelector('title')?.textContent || ''"
            )
            title = re.sub(r"[\s\-–—]*抖音.*$", "", title_raw).strip() or "抖音视频"

            # Uploader — best effort heuristic (DOM-dependent, may be empty)
            uploader = await page.evaluate("""() => {
                const candidates = [
                    document.querySelector('[class*="nickname" i]'),
                    document.querySelector('[class*="author" i]'),
                    document.querySelector('[class*="user-name" i]'),
                ];
                for (const c of candidates) {
                    if (c && c.textContent && c.textContent.trim()) return c.textContent.trim();
                }
                return '';
            }""")

            # Extract video_id from src (e.g. ?video_id=v0200fg10000d7umgtfog65nng5civ70)
            vid_m = re.search(r"video_id=([^&]+)", video_src)
            video_id = vid_m.group(1) if vid_m else ""

            return {
                "video_src": video_src,
                "title": title,
                "uploader": uploader,
                "final_url": page.url,
                "video_id": video_id,
            }
        finally:
            await browser.close()


def _download_mp4(video_src: str, dest_path: Path, timeout_sec: int = 600) -> None:
    """
    Stream-download mp4 via curl subprocess.

    We use curl rather than urllib because Python 3.14 on macOS doesn't
    automatically pick up the system CA bundle, and curl just works with
    system certs out of the box.
    """
    cmd = [
        "curl", "-fsSL",  # -f fail on http error, -s silent, -S show errors, -L follow redirects
        "--max-time", str(timeout_sec),
        "-A", MOBILE_UA,
        "-o", str(dest_path),
        video_src,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec + 30)
    if result.returncode != 0:
        raise RuntimeError(
            f"curl failed (exit {result.returncode}): {result.stderr.strip() or '(no stderr)'}"
        )


def _ffprobe_duration(video_path: Path) -> int:
    """Get video duration in seconds via ffprobe; returns 0 on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        return int(float(result.stdout.strip())) if result.returncode == 0 else 0
    except Exception:
        return 0


def download_douyin_video(url: str, cache_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    """
    Download a Douyin single video. Drop-in replacement for yt-dlp.

    Args:
        url: Douyin share URL (v.douyin.com short or www.douyin.com/video/<id> long)
        cache_dir: Directory to write mp4 file into

    Returns:
        (mp4_path, metadata_dict) — metadata mimics yt-dlp keys (id/title/uploader/
        webpage_url/duration) so generate_md.generate_markdown() works unchanged.

    Raises:
        RuntimeError: extraction or download failed
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Extracting via Playwright: {url}")
    info = asyncio.run(_extract_video_metadata(url))
    logger.info(f"Got video_src ({len(info['video_src'])} chars), video_id={info['video_id']}")

    # Filename from video_id (or a hash fallback if unknown)
    video_id = info["video_id"] or "unknown"
    output_path = cache_dir / f"{video_id}.mp4"

    logger.info(f"Downloading mp4 to {output_path.name}...")
    _download_mp4(info["video_src"], output_path)

    if not output_path.exists() or output_path.stat().st_size < 100_000:
        raise RuntimeError(
            f"Downloaded mp4 too small ({output_path.stat().st_size if output_path.exists() else 0} bytes)"
        )

    # Build yt-dlp-compatible metadata
    metadata = {
        "id": video_id,
        "title": info["title"],
        "uploader": info["uploader"] or "未知作者",
        "webpage_url": info["final_url"],
        "original_url": url,
        "duration": _ffprobe_duration(output_path),
        "description": "",  # Could extract from share page if needed
    }

    # Write a sidecar info.json (matches yt-dlp's --write-info-json behavior,
    # in case future code wants it)
    info_json_path = cache_dir / f"{video_id}.info.json"
    info_json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(
        f"Downloaded: {output_path.name} "
        f"({output_path.stat().st_size // 1024} KB, {metadata['duration']}s)"
    )
    return output_path, metadata
