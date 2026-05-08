"""
Generate markdown note from video metadata and transcription.
"""

import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def sanitize_filename(title: str, max_len: int = 60) -> str:
    """Sanitize title for filesystem use. Keeps Chinese chars, removes filesystem-unsafe."""
    # Remove filesystem-unsafe chars
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
    # Collapse whitespace -> underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim
    sanitized = sanitized[:max_len].strip('_')
    return sanitized or "未命名"


def escape_yaml_value(s: str) -> str:
    r"""Escape string for safe inclusion as a YAML double-quoted scalar value.

    Handles: backslash, double-quote, newlines, carriage returns. Caller is
    responsible for wrapping the result in double quotes.
    """
    if not isinstance(s, str):
        s = str(s)
    return (s.replace('\\', '\\\\')
             .replace('"', '\\"')
             .replace('\n', ' ')
             .replace('\r', ' '))


def format_timestamp(seconds: float) -> str:
    """Format seconds to [MM:SS] or [HH:MM:SS]."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    else:
        return f"[{minutes:02d}:{secs:02d}]"


def generate_markdown(
    metadata: Dict[str, Any],
    segments: List[Dict[str, Any]],
    output_dir: Path
) -> Path:
    """
    Generate markdown note from video metadata and transcription.

    Args:
        metadata: Video metadata dict (from yt-dlp JSON)
        segments: Transcription segments with start/end/text
        output_dir: Directory to save markdown (MyBrain/raw/douyin-favorites/)

    Returns:
        Path to generated markdown file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract fields with fallbacks
    title = metadata.get("title") or "未命名视频"
    description = metadata.get("description") or ""
    author = metadata.get("uploader") or "未知作者"
    url = metadata.get("webpage_url") or metadata.get("original_url") or ""
    duration = metadata.get("duration") or 0
    video_id = metadata.get("id") or ""

    # Filename: include video_id suffix to avoid collisions for same-title videos
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    sanitized_title = sanitize_filename(title)
    id_suffix = re.sub(r'[^A-Za-z0-9]', '', str(video_id))[:8] or now.strftime("%H%M%S")
    filename = f"{date_str}_{sanitized_title}_{id_suffix}.md"
    output_path = output_dir / filename

    # Build frontmatter — all string values quoted + YAML-escaped to survive ":" "#" '"' etc.
    frontmatter = (
        "---\n"
        f'title: "{escape_yaml_value(title)}"\n'
        f'source_url: "{escape_yaml_value(url)}"\n'
        f'fetched: {now.strftime("%Y-%m-%d %H:%M")}\n'
        f'duration_sec: {int(duration) if isinstance(duration, (int, float)) else 0}\n'
        f'author: "{escape_yaml_value(author)}"\n'
        f'video_id: "{escape_yaml_value(video_id)}"\n'
        f'type: source\n'
        f'tags: [抖音, 短视频]\n'
        "---\n"
    )

    # Build body
    content = (
        f"# {title}\n\n"
        f"> {description}\n\n"
        f"**作者**: {author} · **时长**: {duration}s · [原视频]({url})\n\n"
        f"## 字幕（Whisper 自动转写）\n\n"
    )

    for seg in segments:
        timestamp = format_timestamp(seg["start"])
        text = seg["text"]
        content += f"{timestamp} {text}\n"

    content += f"\n## 📎 来源\n- {url}\n"

    # Write file
    full_content = frontmatter + "\n" + content
    output_path.write_text(full_content, encoding="utf-8")
    logger.info(f"Generated markdown: {output_path}")

    return output_path
