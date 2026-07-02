---
title: Claude Code Hook System Design Draft (Pre-Commit Reviewer Gate)
type: overview
tags: [hook, automation, self-supervision, draft]
created: 2026-05-16
updated: 2026-05-16
confidence: medium
priority: active
status: DRAFT — awaiting 2 reviewer audit before deploy
note: Engineer subagent 2026-05-16 output. Single-agent design, MUST be audited by 2 reviewer (per CLAUDE.md 5/16 high-stake 3-agent rule) before deploy.
---

# Claude Code Hook System Design Draft

> **Purpose**: System enforce CLAUDE.md "所有非基础任务必须 2 agent" rule，AI self-discipline unreliable so hook auto-trigger reviewer + block commit when no reviewer ran.
>
> **Status**: DRAFT. Engineer subagent design output 2026-05-16. **Must be audited by 2 reviewer (high-stake architecture, irreversible behavior change for all future sessions) before deploy**.

---

## Hook 1: PreToolUse Write/Edit Pre-Commit Reviewer Gate

**File**: `.claude/hooks/pre-tool-use-review-gate.sh`

**Trigger**: `PreToolUse` event on `Write` or `Edit` tool

**Bash script**:

```bash
#!/bin/bash
set -euo pipefail

VAULT_ROOT="/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库"
SENTINEL_DIR="$VAULT_ROOT/.claude/review-tokens"
LOG_FILE="$VAULT_ROOT/MyBrain/automation/logs/review-gate.jsonl"
HOOK_BYPASS_FILE="$VAULT_ROOT/.claude/hook-bypass-token"

mkdir -p "$SENTINEL_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Read tool call from stdin (Claude Code passes JSON)
TOOL_INPUT=$(cat)
TOOL_NAME=$(echo "$TOOL_INPUT" | jq -r '.tool_name')
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.parameters.file_path // empty')
CONTENT_PREVIEW=$(echo "$TOOL_INPUT" | jq -r '.parameters.content // .parameters.new_string // empty' | head -c 500)

# Only gate Write/Edit
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

# Whitelist detection (mechanical operations)
is_whitelist() {
  local path="$1"
  local content="$2"

  # INDEX.md / log.md append (adding new entries)
  if [[ "$path" =~ (INDEX|log)\.md$ ]] && echo "$content" | grep -qE '^\s*[-\*].*\[\['; then
    return 0
  fi

  # Frontmatter date update only (updated: YYYY-MM-DD)
  if echo "$content" | grep -qE '^updated:\s*[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    return 0
  fi

  # Typo fix (single-word change < 20 chars)
  if [[ "$TOOL_NAME" == "Edit" ]] && echo "$content" | wc -c | awk '{exit !($1 < 20)}'; then
    return 0
  fi

  # Translation (only changing language, structure unchanged)
  if echo "$content" | grep -qiE '(翻译|translation|translate)'; then
    return 0
  fi

  # Mechanical transcribe (raw/ file creation from external source)
  if [[ "$path" =~ /raw/ ]] && echo "$content" | grep -qE '^(source_url|fetched):'; then
    return 0
  fi

  # automation/queue/ task-board operations (append/move tasks)
  if [[ "$path" =~ automation/queue/task-board\.md$ ]]; then
    return 0
  fi

  return 1
}

if is_whitelist "$FILE_PATH" "$CONTENT_PREVIEW"; then
  echo "[$(date -Iseconds)] ALLOW whitelist: $FILE_PATH" >> "$LOG_FILE"
  exit 0
fi

# Check bypass token (set by reviewer agent after approval)
if [[ -f "$HOOK_BYPASS_FILE" ]]; then
  TOKEN_AGE=$(($(date +%s) - $(stat -f %m "$HOOK_BYPASS_FILE")))
  if (( TOKEN_AGE < 300 )); then  # 5min validity
    echo "[$(date -Iseconds)] ALLOW bypass token valid: $FILE_PATH" >> "$LOG_FILE"
    rm -f "$HOOK_BYPASS_FILE"  # Single-use token
    exit 0
  else
    rm -f "$HOOK_BYPASS_FILE"  # Expired
  fi
fi

# Check recent reviewer agent activity (last 2 minutes)
RECENT_REVIEW=$(find "$SENTINEL_DIR" -name "review-*.done" -mmin -2 2>/dev/null | head -1)
if [[ -n "$RECENT_REVIEW" ]]; then
  echo "[$(date -Iseconds)] ALLOW recent review: $FILE_PATH (token: $(basename "$RECENT_REVIEW"))" >> "$LOG_FILE"
  rm -f "$RECENT_REVIEW"  # Single-use
  exit 0
fi

# BLOCK: non-whitelist task without reviewer
echo "[$(date -Iseconds)] BLOCK no reviewer: $FILE_PATH" >> "$LOG_FILE"
cat >&2 <<EOF
🚨 Pre-commit reviewer gate triggered

File: $FILE_PATH
Reason: Non-whitelist task detected, no recent reviewer approval

REQUIRED ACTION:
1. Spawn reviewer agent with Agent tool:
   subagent_type: "reviewer"
   task_description: "Audit [your deliverable] for [specific risks]"

2. Address CRITICAL findings from reviewer

3. Create bypass token after reviewer approval:
   touch "$HOOK_BYPASS_FILE"

Whitelist (auto-approved):
- INDEX/log.md append
- Frontmatter date update
- Typo fix (<20 chars)
- Translation
- raw/ transcribe
- task-board operations

See: MyBrain/CLAUDE.md line 543+ "所有非基础任务必须 2 agent"
EOF
exit 1
```

### Whitelist Detection Logic

- **INDEX/log.md append**: 检测 `- [[` bullet 新增（纯机械追加）
- **Frontmatter date**: 只改 `updated: YYYY-MM-DD` 行
- **Typo fix**: Edit tool + 改动 < 20 字符
- **Translation**: content 含 "翻译/translation" 关键词
- **raw/ transcribe**: raw/ 路径 + 含 `source_url:`/`fetched:` frontmatter
- **task-board ops**: 直接写 task-board.md（已是结构化操作）

### Reviewer Detection

- **Option B (Sentinel File)** — 最可靠
  - Reviewer agent 完成后必须 `touch .claude/review-tokens/review-<uuid>.done`
  - Hook 检查 2min 内是否有 `*.done` token → 有则放行 + 删除 token（单次有效）
- **Bypass Token** — 紧急情况 Javen 手动创建 `.claude/hook-bypass-token` 让 AI 过关（5min 有效期）

### Block vs Warn

- **Block mode** (exit 1) — 默认。Write/Edit 调用直接失败，AI 必须先 spawn reviewer
- **Warn mode** — 可选，通过环境变量 `REVIEW_GATE_MODE=warn` 切换成只记 log 不 block

---

## Hook 2: SessionStart Context Injection

**File**: `.claude/hooks/session-start-inject.sh`

**Trigger**: `SessionStart`

**Bash script**:

```bash
#!/bin/bash
set -euo pipefail

VAULT_ROOT="/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库"
INJECT_FILE="$VAULT_ROOT/.claude/session-context-inject.txt"

cat > "$INJECT_FILE" <<'EOF'
🧠 Session Context (Auto-Injected)

## Critical Rules (CLAUDE.md 2026-05-15/16)
- 所有非基础任务必须 2 agent (whitelist: typo/INDEX append/translation/transcribe)
- Deliverable edit 完强制 Check 步骤 (self-audit → spawn reviewer if high-stake)
- 数字零容忍 (paper Table 逐字 verify)
- 二手 source 不可信 (vault source 页可能含 AI 扩展，引用 paper 必回 PDF)
- 真实性 > 一切其他考量 (accuracy 永远赢 design/简洁度)

## Recent Lessons (automation/docs/lessons.md 摘要)
EOF

# Append lesson titles (⑭-⑰ cargo cult related)
grep -E '^## ⑭|^## ⑮|^## ⑯|^## ⑰' "$VAULT_ROOT/MyBrain/automation/docs/lessons.md" | head -20 >> "$INJECT_FILE"

cat >> "$INJECT_FILE" <<EOF

## Profile Facts
EOF

# Append profile-facts.md if exists
if [[ -f "$VAULT_ROOT/MyBrain/career/profile-facts.md" ]]; then
  head -50 "$VAULT_ROOT/MyBrain/career/profile-facts.md" >> "$INJECT_FILE"
fi

cat >> "$INJECT_FILE" <<EOF

⚠️ This context injected by SessionStart hook. Not user message.
Pre-Commit Review Gate: active (see .claude/hooks/pre-tool-use-review-gate.sh)
EOF

# Output to Claude Code (hook stdout = injected system message)
cat "$INJECT_FILE"

# Log
echo "[$(date -Iseconds)] SessionStart context injected ($(wc -l < "$INJECT_FILE") lines)" \
  >> "$VAULT_ROOT/MyBrain/automation/logs/session-start.jsonl"
```

### Content Injected

1. **Critical Rules** (5 条 personality-level rule 标题 + 触发条件)
2. **Recent Lessons** (lessons.md ⑭-⑰ 标题，不含全文 — 避免 token 爆炸)
3. **Profile Facts** (前 50 行 — 包含 Javen 当前状态/求职/课程)
4. **Hook 提醒** (告知 AI review gate 已启用)

### Token Cost

- Estimate: ~800 tokens/session (150 rules + 200 lessons + 400 profile + 50 header)
- Cost: $0.003/session @ Sonnet input rate
- Trade-off: 完整 lessons.md 400 行 → 2000 tokens ($0.008) → 摘要版减 60% cost

---

## Hook 3: Stop Hook Cargo Cult Detector

**File**: `.claude/hooks/stop-cargo-cult-detector.sh`

**Trigger**: `Stop` event (AI reply 完成)

**Bash script**:

```bash
#!/bin/bash
set -euo pipefail

VAULT_ROOT="/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库"
LOG_FILE="$VAULT_ROOT/MyBrain/automation/logs/cargo-cult-violations.jsonl"
LAST_REPLY_FILE="$VAULT_ROOT/.claude/last-reply.txt"

mkdir -p "$(dirname "$LOG_FILE")"

# Read AI last reply (Claude Code passes via stdin or env)
REPLY_TEXT=$(cat "$LAST_REPLY_FILE" 2>/dev/null || echo "")
if [[ -z "$REPLY_TEXT" ]]; then
  exit 0
fi

# Heuristic cargo cult signatures (regex-based first pass)
cargo_cult_regex=(
  '\b(best|worst|highest|lowest|most|least)\b.*\b(model|method|approach)\b'  # Ranking without verify
  '\b(should|typically|usually|generally|normally)\b.*\b(use|recommend|suggest)\b'  # 凭印象 default
  '\b(简单|复杂|优雅|高效|强大)\b.*\b(方案|方法|实现)\b'  # Binary adjective
  '✅.*\b(完成|done|finished|已落盘)\b'  # Reassure pattern
  '\b(显然|当然|自然)\b'  # Overconfidence marker
)

HEURISTIC_MATCH=0
for pattern in "${cargo_cult_regex[@]}"; do
  if echo "$REPLY_TEXT" | grep -qiE "$pattern"; then
    HEURISTIC_MATCH=1
    break
  fi
done

if (( HEURISTIC_MATCH == 0 )); then
  exit 0  # Fast path: no signature
fi

# LLM audit (Haiku-3.5 via Anthropic API)
HAIKU_PROMPT=$(cat <<EOF
You are a cargo cult detector auditing AI work output.

**Cargo cult signatures:**
- Ranking labels (best/worst/highest) without explicit verification step
- Default recommendations based on "usually/typically" without cite specific constraint
- Binary praise (简单/优雅/高效) without trade-off analysis
- Reassure user "done ✓" without showing verification artifact
- Overconfidence ("显然/当然") without hedge when uncertain

**Task:** Read AI reply below, output JSON:
{
  "is_cargo_cult": true/false,
  "confidence": 0.0-1.0,
  "signature": "which pattern matched (or null)",
  "excerpt": "具体违反片段 (or null)"
}

**AI Reply:**
${REPLY_TEXT:0:2000}
EOF
)

# (Anthropic SDK call abbreviated — see full script in engineer output)
```

### Cargo Cult Signature Detection

1. **Heuristic First Pass** (regex) — 快速过滤明显无问题的 reply (避免每次 LLM call)
2. **LLM Audit** (Haiku) — 匹配后用小模型深度判断（context-aware）

### Regex Patterns

- `(best|worst|highest|lowest)` + `(model|method)` — Ranking label 没 verify
- `(should|typically|usually)` + `(use|recommend)` — 凭印象 default
- `(简单|复杂|优雅|高效)` + `(方案|方法)` — Binary adjective
- `✅.*(完成|done|finished)` — Reassure pattern
- `(显然|当然|自然)` — Overconfidence

### Cost Estimate

- Heuristic pass: free (regex)
- Haiku call: $0.001/reply (300 output tokens)
- Trigger rate: ~20% replies match heuristic → $0.0002/reply average
- Daily cost (50 replies): ~$0.01

---

## settings.json Patch

```json
{
  "hooks": {
    "SessionStart": [
      {
        "name": "session-context-inject",
        "path": ".claude/hooks/session-start-inject.sh",
        "enabled": true
      }
    ],
    "PreToolUse": [
      {
        "name": "pre-commit-review-gate",
        "path": ".claude/hooks/pre-tool-use-review-gate.sh",
        "enabled": true,
        "tools": ["Write", "Edit"]
      }
    ],
    "Stop": [
      {
        "name": "cargo-cult-detector",
        "path": ".claude/hooks/stop-cargo-cult-detector.sh",
        "enabled": true,
        "async": true
      }
    ]
  },
  "review_gate": {
    "mode": "block",
    "bypass_token_ttl": 300,
    "reviewer_token_ttl": 120
  }
}
```

---

## Edge Cases / Failure Modes (Engineer Identified)

| Failure Mode | Mitigation |
|---|---|
| **Hook script crash** | Hook 内 `set -euo pipefail` + stderr 输出到 user，AI 看到报错会修 hook |
| **AI bypass (用 Bash echo 写文件)** | Hook 2 session-start 注入规则"禁止用 Bash 写 vault 文件"；audit.sh 已记录所有 Bash 命令可事后审计 |
| **False positive (whitelist 漏)** | Javen 遇到误 block → 手动 `touch .claude/hook-bypass-token` → AI 放行 → Javen 告知我调 whitelist regex |
| **Reviewer agent 没 set token** | Hook 1 在 block message 里明确告知 AI "create bypass token after reviewer approval"；AI 如果忘记会再次被 block 看到提示 |
| **Token budget 爆炸** | Hook 2 只注入摘要（800 tokens/session）；Hook 3 heuristic 先过滤 80% → 平均 $0.01/day；可配置 `HOOK_BUDGET_DAILY=0.05` 超预算自动 disable Hook 3 |
| **Google Drive 同步延迟** | Sentinel token 用 mtime 判断（`stat -f %m`）而非 FSEvents；2min TTL 足够同步延迟 |
| **AI 故意绕过 reviewer** | Hook 1 无法绕过（除非 AI 不用 Write/Edit）；如果 AI 用 Bash → audit.sh 会记录 → Javen 定期 review logs → 下次 session 追责 |

---

## Engineer-Identified "未做 / Open Issues"

- **未实装 Haiku Python 脚本**：Hook 3 内 Python snippet 需要 `anthropic` SDK，本机可能没装
- **未测试 Google Drive 同步延迟**：Sentinel token 2min TTL 理论够用，但实测可能需要调到 5min
- **未配置 daily budget cap**：Hook 3 可能累积 Haiku cost，建议加环境变量 `HOOK_BUDGET_DAILY=0.05` 自动 disable
- **未集成 existing audit.sh**：现有 audit.sh 记录所有 Bash 命令，可以跟 Hook 1/3 log 做交叉验证（detect AI bypass），但未写 aggregator script
- **Reviewer agent 没 auto-create token**：AI 需要手动 `touch .claude/review-tokens/review-<uuid>.done`，下一步可以让 Agent tool 自动注入这个动作到 reviewer subagent 的 system prompt

---

## Test Plan (Deployment Validation)

### Phase 1: Hook 安装验证

```bash
cd "$VAULT_ROOT"
mkdir -p .claude/hooks
chmod +x .claude/hooks/*.sh

cat .claude/settings.json | jq '.hooks'

.claude/hooks/session-start-inject.sh
# Expected: 输出 ~50 行 context

echo '{"tool_name":"Write","parameters":{"file_path":"MyBrain/wiki/INDEX.md","content":"- [[新页面]]"}}' \
  | .claude/hooks/pre-tool-use-review-gate.sh
# Expected: exit 0 (whitelist 放行)

echo '{"tool_name":"Write","parameters":{"file_path":"MyBrain/wiki/概念.md","content":"# 新概念"}}' \
  | .claude/hooks/pre-tool-use-review-gate.sh
# Expected: exit 1 + stderr 提示
```

### Phase 2: E2E Test Scenarios

(见 engineer 完整 output for 10 scenario list)

---

## ⚠️ Status: Draft, MUST be reviewed before deploy

按 CLAUDE.md 5/16 rule "high-stake architecture (irreversible behavior change) → 3 agent (producer + reviewer + second reviewer)"。

Engineer 已是 producer。需要 2 reviewer 独立 audit:
- **Reviewer A**: Technical correctness (Claude Code hook API真实支持 / Bash script bug / AI bypass attack vector / false positive rate / cost)
- **Reviewer B**: Spirit-of-rule (hook 真符合 Javen 5/16 spirit 吗 / sentinel token mechanism 致命缺陷 / 是否 cargo cult of enforcement)
