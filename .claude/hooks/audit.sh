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
    # 记录所有 MyBrain/ 文件的 Write/Edit + Agent/Bash 工具调用
    TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null)
    FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""' 2>/dev/null)

    # A. Write/Edit on MyBrain/ files (排除 .git/.obsidian/logs 避免递归)
    if [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "Edit" ]]; then
      if [[ "$FILE_PATH" == *"MyBrain/"* ]] || [[ "$FILE_PATH" == MyBrain/* ]]; then
        if [[ "$FILE_PATH" != *"/.git/"* ]] \
           && [[ "$FILE_PATH" != *"/.obsidian/"* ]] \
           && [[ "$FILE_PATH" != *"/MyBrain/system/logs/"* ]]; then
          SHOULD_LOG=true
        fi
      fi
    fi

    # B. Agent tool calls (任何 Agent 调用都记)
    if [[ "$TOOL_NAME" == "Agent" ]]; then
      SHOULD_LOG=true
    fi

    # C. Bash tool calls (记录命令用于 bypass 检测)
    if [[ "$TOOL_NAME" == "Bash" ]]; then
      SHOULD_LOG=true
    fi

    # 保留原有 4 个白名单文件的额外 logging (backwards compat)
    if [[ "$FILE_PATH" == *"task-board.md"* ]] \
       || [[ "$FILE_PATH" == *"approvals.md"* ]] \
       || [[ "$FILE_PATH" == *"automation/CLAUDE.md"* ]] \
       || [[ "$FILE_PATH" == *"automation/docs/user-guide.md"* ]]; then
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

  # Extract optional fields (additive schema, max 200 chars each)
  SUBAGENT_TYPE=$(echo "$INPUT" | jq -r '.tool_input.subagent_type // ""' 2>/dev/null)
  DESCRIPTION_RAW=$(echo "$INPUT" | jq -r '.tool_input.description // ""' 2>/dev/null)
  DESCRIPTION="${DESCRIPTION_RAW:0:200}"
  BASH_COMMAND_RAW=$(echo "$INPUT" | jq -r '.tool_input.command // ""' 2>/dev/null)
  BASH_COMMAND="${BASH_COMMAND_RAW:0:200}"

  # Build base JSON object
  jq -nc \
    --arg ts "$TIMESTAMP" \
    --arg event "$EVENT" \
    --arg tool "$TOOL" \
    --arg file "$FILE_PATH" \
    --arg session "$SESSION" \
    --arg cwd "$CWD" \
    --arg subagent_type "$SUBAGENT_TYPE" \
    --arg description "$DESCRIPTION" \
    --arg bash_command "$BASH_COMMAND" \
    '{
      ts: $ts,
      event: $event,
      tool: $tool,
      file: $file,
      session: $session,
      cwd: $cwd
    } + (if $subagent_type != "" then {subagent_type: $subagent_type} else {} end)
      + (if $description != "" then {description: $description} else {} end)
      + (if $bash_command != "" then {bash_command: $bash_command} else {} end)
    ' \
    >> "$LOG_FILE" 2>/dev/null
fi

# 永远 exit 0，不阻塞 Claude 主流程
exit 0
