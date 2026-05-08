"""
Transcribe video to text using Whisper (mlx-whisper preferred, faster-whisper fallback).
All processing is local — no external API calls.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def transcribe_audio(video_path: Path) -> List[Dict[str, Any]]:
    """
    Transcribe video audio to text with timestamps.

    Args:
        video_path: Path to video file (.mp4)

    Returns:
        List of segments with 'start', 'end', 'text' keys

    Raises:
        RuntimeError: If transcription fails
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Try mlx-whisper first (Apple Silicon optimized)
    try:
        import mlx_whisper
        logger.info("Using mlx-whisper (Apple Silicon accelerated)")
        result = mlx_whisper.transcribe(
            str(video_path),
            path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
            language="zh"
        )
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            })
        logger.info(f"Transcribed {len(segments)} segments using mlx-whisper")
        return segments

    except Exception as e:
        # Catches ImportError (mlx-whisper not installed, e.g., Intel Mac) and runtime failures.
        logger.warning(f"mlx-whisper unavailable or failed ({e}), falling back to faster-whisper")

    # Fallback to faster-whisper.
    # Note: faster-whisper (CTranslate2 backend) does NOT support Apple MPS as of 2026-05;
    # only CPU and CUDA. On Apple Silicon, mlx-whisper above is the accelerated path; this
    # CPU branch is the universal fallback.
    try:
        from faster_whisper import WhisperModel
        logger.info("Using faster-whisper (CPU)")
        model = WhisperModel("large-v3", device="cpu", compute_type="int8")
        segments_iter, info = model.transcribe(str(video_path), language="zh")

        segments = []
        for seg in segments_iter:
            segments.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip()
            })
        logger.info(f"Transcribed {len(segments)} segments using faster-whisper")
        return segments

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise RuntimeError(f"Both mlx-whisper and faster-whisper failed: {e}")
