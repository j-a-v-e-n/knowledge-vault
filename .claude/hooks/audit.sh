#!/bin/bash
# .claude/hooks/audit.sh
# 任务看板审计日志：记录看板改动 + 会话生命周期事件
# 由 .claude/settings.json 在 PostToolUse / SessionStart / SessionEnd / Stop 上触发

set -uo pipefail

# 读取 hook stdin JSON（hook 触发模式 stdin 总是会关闭）
INPUT=$(cat 2>/dev/null || true)
[[ -z "$INPUT" ]] && INPUT='{}'

# 解析事件类型
EVENT=$(echo "$INPUT" | jq -r '.hook_event_name // "unknown"' 2>/dev/null || echo "unknown")

# 日志目录
LOG_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/MyBrain/system/logs"
mkdir -p "$LOG_DIR" 2>/dev/null
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/$TODAY.jsonl"

# 决定是否记录（避免日志膨胀）
SHOULD_LOG=false
case "$EVENT" in
  SessionStart|SessionEnd|Stop)
    # 会话生命周期事件全部记录
    SHOULD_LOG=true
    ;;
  PostToolUse)
    # 只记录看板文件相关的 Edit/Write
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
    if [[ "$FILE_PATH" == *"task-board.md"* ]] \
       || [[ "$FILE_PATH" == *"system/CLAUDE.md"* ]] \
       || [[ "$FILE_PATH" == *"system/README.md"* ]]; then
      SHOULD_LOG=true
    fi
    ;;
esac

if [[ "$SHOULD_LOG" == "true" ]]; then
  TIMESTAMP=$(date -Iseconds 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S%z")
  TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null)
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
  SESSION=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null)
  CWD=$(echo "$INPUT" | jq -r '.cwd // ""' 2>/dev/null)

  # 用 jq 输出干净的 JSONL（每行一个 JSON 对象）
  jq -nc \
    --arg ts "$TIMESTAMP" \
    --arg event "$EVENT" \
    --arg tool "$TOOL" \
    --arg file "$FILE_PATH" \
    --arg session "$SESSION" \
    --arg cwd "$CWD" \
    '{ts: $ts, event: $event, tool: $tool, file: $file, session: $session, cwd: $cwd}' \
    >> "$LOG_FILE" 2>/dev/null
fi

# 永远 exit 0，不阻塞 Claude 主流程
exit 0
