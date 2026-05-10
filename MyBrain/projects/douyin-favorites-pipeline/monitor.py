#!/usr/bin/env python3
"""
Monitor DouyinInbox/ for new .txt files and process them.
Runs as a daemon via launchd.
"""

import logging
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from process import process_one

# Paths
HOME = Path.home()
INBOX_DIR = HOME / "Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox"
VAULT_PATH = Path("/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库")
# Cache (downloaded mp4s during processing) lives OUTSIDE iCloud — large videos
# would otherwise eat Javen's iCloud quota even though they get cleaned up after
# transcription. Local-only path, ~/.cache/douyin-favorites/.
CACHE_BASE = HOME / ".cache" / "douyin-favorites"
LOG_DIR = INBOX_DIR / "logs"
PROCESSED_DIR = INBOX_DIR / "processed"
ERRORED_DIR = INBOX_DIR / "errored"

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "monitor.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DouyinHandler(FileSystemEventHandler):
    """Handle new .txt files in DouyinInbox/."""

    def on_created(self, event):
        if isinstance(event, FileCreatedEvent) and event.src_path.endswith('.txt'):
            self.process_file(Path(event.src_path))

    def process_file(self, file_path: Path):
        """Process a single .txt file."""
        if not file_path.exists() or not file_path.is_file():
            return

        # iCloud sync race-guard: file may appear with 0 bytes while content
        # is still syncing down from iCloud. Wait briefly and re-check size
        # stability before reading.
        for attempt in range(6):  # up to ~12s total
            try:
                size_a = file_path.stat().st_size
                time.sleep(2)
                size_b = file_path.stat().st_size
            except FileNotFoundError:
                logger.warning(f"File disappeared during sync wait: {file_path.name}")
                return
            if size_a > 0 and size_a == size_b:
                break
            logger.info(f"Waiting for iCloud sync ({size_a} -> {size_b} bytes): {file_path.name}")
        else:
            logger.warning(f"Skipping file that never stabilized: {file_path.name}")
            return

        logger.info(f"Processing new file: {file_path.name}")

        # IMPORTANT: We don't call process_one() directly here. Instead spawn a
        # subprocess via /bin/zsh login shell so it inherits the user's full
        # GUI/Aqua session — Playwright headless chromium sees douyin's <video>
        # element when launched from a user shell but not when launched from
        # launchd's process tree (root cause unclear; suspected macOS Aqua
        # session token differences or douyin anti-bot fingerprinting). The
        # subprocess invokes manual_run.py which scans the inbox, processes
        # whatever's pending (including this file), and moves to processed/
        # or errored/ as appropriate.
        import subprocess
        script_dir = Path(__file__).parent
        cmd = [
            "/bin/zsh", "-l", "-c",
            f'cd "{script_dir}" && '
            f'export DYLD_LIBRARY_PATH="/opt/homebrew/opt/expat/lib:${{DYLD_LIBRARY_PATH:-}}" && '
            f'/usr/local/bin/python3 manual_run.py'
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1800,  # 30 min
            )
            if result.returncode == 0:
                logger.info(f"manual_run subprocess succeeded for {file_path.name}")
                if result.stdout:
                    logger.info(f"manual_run stdout (last 500 chars): ...{result.stdout[-500:]}")
            else:
                logger.error(f"manual_run subprocess failed (exit {result.returncode}): {result.stderr[-500:]}")
                # Move file to errored/ so we don't reprocess infinitely
                if file_path.exists():
                    ERRORED_DIR.mkdir(parents=True, exist_ok=True)
                    file_path.replace(ERRORED_DIR / file_path.name)
        except subprocess.TimeoutExpired:
            logger.error(f"manual_run subprocess timed out (30 min) for {file_path.name}")
            if file_path.exists():
                ERRORED_DIR.mkdir(parents=True, exist_ok=True)
                file_path.replace(ERRORED_DIR / file_path.name)


def catchup_existing_files():
    """Process any .txt files already in inbox (catchup mode)."""
    logger.info("Catchup mode: scanning for existing .txt files...")
    txt_files = list(INBOX_DIR.glob("*.txt"))

    if txt_files:
        logger.info(f"Found {len(txt_files)} unprocessed files")
        handler = DouyinHandler()
        for txt_file in txt_files:
            handler.process_file(txt_file)
    else:
        logger.info("No unprocessed files found")


def main():
    """Main daemon loop."""
    logger.info("Douyin pipeline monitor starting...")
    logger.info(f"Watching: {INBOX_DIR}")

    # Ensure directories exist
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_BASE.mkdir(parents=True, exist_ok=True)

    # Process existing files first
    catchup_existing_files()

    # Start watchdog observer
    event_handler = DouyinHandler()
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_DIR), recursive=False)
    observer.start()
    logger.info("Monitoring started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping monitor...")
        observer.stop()

    observer.join()
    logger.info("Monitor stopped.")


if __name__ == "__main__":
    main()
