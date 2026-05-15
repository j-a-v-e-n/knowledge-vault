#!/usr/bin/env bash
# Run full 12-subject LOSO Sonnet λ-generator evaluation
# Per-subject JSON output for crash-resilience.
# Wraps in caffeinate -di to prevent sleep.
#
# Usage: ./run_loso_sonnet.sh
# Monitor: tail -f results/loso_sonnet_run.log
# Kill: kill $(cat results/loso_sonnet.pid)

set -u  # Note: NOT set -e — per-subject failure shouldn't abort other subjects

PROJ_DIR="/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/ece284-llm-ppg"
cd "$PROJ_DIR" || exit 1

LOG="results/loso_sonnet_run.log"
PIDFILE="results/loso_sonnet.pid"
DONE_FLAG="results/loso_sonnet_DONE"

# Clean stale done flag
rm -f "$DONE_FLAG"

mkdir -p results

{
  echo "================================================================"
  echo "LOSO Sonnet evaluation — starting $(date '+%Y-%m-%d %H:%M:%S')"
  echo "================================================================"
  echo "PID: $$"
  echo "Working dir: $PROJ_DIR"
  echo "Python: $(python3 --version)"
  echo "Est cost: ~\$6.48, est time: ~5.9 hours"
  echo "Output: per-subject results/llm_lambda_loso_sonnet_s{1..12}.json"
  echo "================================================================"
  echo ""

  for SUBJ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    OUT="results/llm_lambda_loso_sonnet_s${SUBJ}.json"
    if [ -f "$OUT" ]; then
      echo "[$(date '+%H:%M:%S')] Subj $SUBJ: SKIP (output exists: $OUT)"
      continue
    fi

    echo ""
    echo "[$(date '+%H:%M:%S')] === Subj $SUBJ START ==="
    # -u: unbuffered (lesson #12); --subjects N: single subject; NO --pilot = all windows
    PYTHONUNBUFFERED=1 python3 -u llm_lambda.py \
      --subjects "$SUBJ" \
      --model claude-sonnet-4-5 \
      --out "$OUT" 2>&1

    STATUS=$?
    if [ $STATUS -eq 0 ]; then
      echo "[$(date '+%H:%M:%S')] === Subj $SUBJ DONE (exit 0) ==="
    else
      echo "[$(date '+%H:%M:%S')] === Subj $SUBJ FAILED (exit $STATUS) — continuing ==="
    fi
  done

  echo ""
  echo "================================================================"
  echo "ALL SUBJECTS PROCESSED — finished $(date '+%Y-%m-%d %H:%M:%S')"
  echo "================================================================"
  ls -la results/llm_lambda_loso_sonnet_s*.json 2>/dev/null
  echo ""
  echo "DONE flag written: $DONE_FLAG"
  touch "$DONE_FLAG"
} > "$LOG" 2>&1 &

BG_PID=$!
echo "$BG_PID" > "$PIDFILE"
echo "Launched background PID: $BG_PID"
echo "Log: $LOG"
echo "PID file: $PIDFILE"
echo "Done flag (when finished): $DONE_FLAG"
echo ""
echo "Monitor: tail -f \"$LOG\""
echo "Check progress: ls -la results/llm_lambda_loso_sonnet_s*.json"
echo "Kill: kill \$(cat \"$PIDFILE\")"
