#!/bin/bash
set -e

echo "=== Douyin Favorites Pipeline Setup ==="
echo ""

# Sanity: must run from project directory (so .plist + monitor.py paths resolve)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [[ "$(basename "$(pwd)")" != "douyin-favorites-pipeline" ]]; then
    echo "ERROR: setup.sh must live in douyin-favorites-pipeline/ — refusing to run."
    exit 1
fi

# Check Python — capture full path so plist + pip use SAME Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Install Python 3.8+ first."
    exit 1
fi
PYTHON_PATH="$(command -v python3)"
echo "✓ Python3 found: $PYTHON_PATH ($($PYTHON_PATH --version))"

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ ffmpeg not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "ERROR: Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
    brew install ffmpeg
fi
echo "✓ ffmpeg found: $(ffmpeg -version | head -n1)"

# Check yt-dlp
if ! command -v yt-dlp &> /dev/null; then
    echo "⚠ yt-dlp not found. Installing via Homebrew..."
    brew install yt-dlp
fi
echo "✓ yt-dlp found: $(yt-dlp --version)"

# Install Python dependencies — use SAME interpreter as plist will run
echo ""
echo "Installing Python dependencies via $PYTHON_PATH -m pip..."
"$PYTHON_PATH" -m pip install --upgrade pip
"$PYTHON_PATH" -m pip install -r requirements.txt

# Create directory structure
echo ""
echo "Creating directory structure..."
INBOX_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox"
mkdir -p "$INBOX_DIR"/{processed,errored,cache,logs}
echo "✓ Created directories in $INBOX_DIR"

# Install launchd plist
echo ""
echo "Installing launchd daemon..."
PLIST_SRC="$(pwd)/com.javen.douyin-pipeline.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.javen.douyin-pipeline.plist"

cp "$PLIST_SRC" "$PLIST_DEST"
# Patch hardcoded /usr/bin/python3 in plist to actual Python path used above.
# This is critical: pip3 may install to Homebrew Python but plist would use Apple Python,
# causing ModuleNotFoundError for watchdog/yt-dlp/etc.
PYTHON_PATH_ESCAPED="$(printf '%s' "$PYTHON_PATH" | sed 's:/:\\/:g')"
sed -i.bak "s/\/usr\/bin\/python3/$PYTHON_PATH_ESCAPED/g" "$PLIST_DEST"
rm -f "$PLIST_DEST.bak"
echo "✓ Patched plist to use $PYTHON_PATH"

launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "✓ Daemon installed and loaded"

# Verify daemon status
sleep 2
if launchctl list | grep -q "com.javen.douyin-pipeline"; then
    echo "✓ Daemon is running"
else
    echo "⚠ Daemon may not be running. Check logs:"
    echo "  $INBOX_DIR/logs/launchd-stderr.log"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure iOS Shortcut to save URLs to: $INBOX_DIR"
echo "2. Drop a test .txt file with a Douyin URL"
echo "3. Check logs at: $INBOX_DIR/logs/"
echo ""
echo "To stop daemon:  launchctl unload $PLIST_DEST"
echo "To start daemon: launchctl load $PLIST_DEST"
echo "To view logs:    tail -f $INBOX_DIR/logs/monitor.log"
