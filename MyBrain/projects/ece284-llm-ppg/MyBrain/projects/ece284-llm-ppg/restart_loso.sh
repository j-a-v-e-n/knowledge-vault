#!/usr/bin/env bash
# Resume Sonnet 12-subject LOSO after Javen 5/14 leave-and-come-back.
# Run from project root: bash restart_loso.sh
# Or just: source restart_loso.sh (if you want env exported)
#
# What this does:
#   - caffeinate -di: prevent idle sleep + display sleep (but NOT lid-close sleep)
#   - python3 -u: unbuffered stdout (lesson ⑫)
#   - tee log: see real-time + persist to /tmp
#   - timestamped output JSON
#
# IMPORTANT: 不要合盖. caffeinate 防不了 lid-close. 不合盖 + 屏幕暗下来即可.

set -e
cd "$(dirname "$0")"
export ANTHROPIC_API_KEY="$(cat ~/.config/anthropic-keys/ece284)"
export PYTHONUNBUFFERED=1
OUT="results/llm_lambda_full_loso_sonnet_$(date +%Y%m%d_%H%M%S).json"
LOG="/tmp/llm_lambda_full_loso.log"

echo "[start] $(date) | output: $OUT | log: $LOG"

caffeinate -di python3 -u llm_lambda.py \
  --subjects 1 2 3 4 5 6 7 8 9 10 11 12 \
  --out "$OUT" 2>&1 | tee "$LOG"
