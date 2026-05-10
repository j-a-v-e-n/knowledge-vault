#!/usr/bin/env python3
"""
Manual catch-up runner — process all pending .txt files in DouyinInbox.

Workaround for the launchd-Playwright issue: launchd LaunchAgent processes
seem to get a different douyin response (no <video> element) than user-shell
processes. Until we figure out why, run this script from a Terminal whenever
you want to process the inbox.

Usage:
    cd MyBrain/projects/douyin-favorites-pipeline
    DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib /usr/local/bin/python3 manual_run.py

What it does:
    1. Scans ~/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/*.txt
    2. For each, runs process_one (Playwright extract + Whisper transcribe + .md)
    3. On success → moves .txt to processed/ and writes full .md to vault
    4. On partial → moves .txt to processed/ and writes URL-only .md
    5. Reports a summary at the end

Idempotent: skips files already in processed/ or errored/ subdirs.
"""
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Make sure we can import sibling modules
sys.path.insert(0, str(Path(__file__).parent))
from process import process_one

# Paths (mirrored from monitor.py)
HOME = Path.home()
INBOX_DIR = HOME / "Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox"
VAULT_PATH = Path("/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库")
CACHE_BASE = HOME / ".cache" / "douyin-favorites"
LOG_DIR = INBOX_DIR / "logs"
PROCESSED_DIR = INBOX_DIR / "processed"
ERRORED_DIR = INBOX_DIR / "errored"


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_BASE.mkdir(parents=True, exist_ok=True)

    # Find pending .txt files in inbox root (not in processed/ or errored/)
    txt_files = sorted(INBOX_DIR.glob("*.txt"))
    if not txt_files:
        print("No pending .txt files in DouyinInbox. Nothing to do.")
        return

    print(f"Found {len(txt_files)} pending file(s):")
    for f in txt_files:
        print(f"  - {f.name}")
    print()

    log_path = LOG_DIR / "processed.jsonl"
    counts = {"success": 0, "partial": 0, "failed": 0}
    for txt_file in txt_files:
        print(f"\n{'=' * 60}")
        print(f"Processing: {txt_file.name}")
        print('=' * 60)

        result = process_one(txt_file, VAULT_PATH, CACHE_BASE, log_path)

        # Move to processed/ or errored/ based on status
        if result["status"] in ("success", "partial"):
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            dest = PROCESSED_DIR / txt_file.name
            txt_file.replace(dest)
            counts[result["status"]] += 1
            tag = "✅ FULL" if result["status"] == "success" else "⚠️ PARTIAL (URL only)"
            print(f"\n{tag}: {result['output_path']}")
        else:
            ERRORED_DIR.mkdir(parents=True, exist_ok=True)
            dest = ERRORED_DIR / txt_file.name
            txt_file.replace(dest)
            counts["failed"] += 1
            print(f"\n❌ FAILED: {result.get('error', 'unknown error')}")

    # Summary
    print(f"\n\n{'=' * 60}")
    print("SUMMARY")
    print('=' * 60)
    print(f"  ✅ Full (with subtitles): {counts['success']}")
    print(f"  ⚠️ Partial (URL only):    {counts['partial']}")
    print(f"  ❌ Failed:                 {counts['failed']}")
    print(f"\nVault output: {VAULT_PATH}/MyBrain/raw/douyin-favorites/")


if __name__ == "__main__":
    main()
