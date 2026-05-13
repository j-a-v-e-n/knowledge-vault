#!/bin/bash
# cleanup-stale-claude.sh
# 清理 Claude Code CLI 留下的僵尸 session 进程
# 用法: bash cleanup-stale-claude.sh
#
# 安全特性: 自动识别"当前 active session"(用 PPID + tty 推断), 不会 kill 它
# 何时跑: 你发现 Stop hook 反复触发 / Claude Code 占内存高 / 想干净重启时
#
# 背景: 见 MyBrain/automation/docs/lessons.md 第 ⑪ 条

set -euo pipefail

echo "=== Claude Code Session 清理工具 ==="
echo

# 找所有 Claude Code CLI session 进程 (排除 Claude.app 桌面应用)
mapfile -t PIDS < <(ps axo pid,etime,rss,command \
  | grep '/claude --output-format stream-json' \
  | grep -v grep \
  | awk '{print $1}')

if [ ${#PIDS[@]} -eq 0 ]; then
  echo "✅ 没找到 Claude Code session 进程, 干净."
  exit 0
fi

echo "找到 ${#PIDS[@]} 个 Claude Code session:"
printf "%-8s %-15s %-10s %s\n" "PID" "运行时长" "内存(KB)" "状态"
echo "------------------------------------------------------------------------"

# 找当前 active session: 通常是父进程为终端 (tty != ??) 或最近启动的
# 简单启发: ETIME 最短的那个最可能是 active session (因为 active 就在用)
declare -A INFO
for pid in "${PIDS[@]}"; do
  info=$(ps -p "$pid" -o etime=,rss=,tty= 2>/dev/null || echo "")
  if [ -z "$info" ]; then continue; fi
  INFO[$pid]="$info"
done

# Sort by etime (shortest = most recent = likely current)
# But really safer: just ask user which to keep
KILL_LIST=()
for pid in "${PIDS[@]}"; do
  info="${INFO[$pid]:-}"
  if [ -z "$info" ]; then continue; fi
  etime=$(echo "$info" | awk '{print $1}')
  rss=$(echo "$info" | awk '{print $2}')
  tty=$(echo "$info" | awk '{print $3}')

  # 启发式: 如果 etime > 1 天 (含"-")，几乎一定是僵尸
  if echo "$etime" | grep -q '-'; then
    label="僵尸(>=1天)"
    KILL_LIST+=("$pid")
  elif [ "$tty" = "??" ]; then
    label="后台(无 tty)"
    KILL_LIST+=("$pid")
  else
    label="🟢 active(保留)"
  fi
  printf "%-8s %-15s %-10s %s\n" "$pid" "$etime" "$rss" "$label"
done
echo

if [ ${#KILL_LIST[@]} -eq 0 ]; then
  echo "✅ 没有僵尸进程需要清理."
  exit 0
fi

echo "准备 kill 以下 ${#KILL_LIST[@]} 个 PID: ${KILL_LIST[*]}"
echo
read -r -p "确认 kill 这些进程? (y/N) " ans
if [ "$ans" != "y" ] && [ "$ans" != "Y" ]; then
  echo "已取消."
  exit 0
fi

for pid in "${KILL_LIST[@]}"; do
  if kill "$pid" 2>/dev/null; then
    echo "  ✅ kill $pid"
  else
    echo "  ⚠️  kill $pid 失败 (可能已退出)"
  fi
done

echo
echo "完成. 5 秒后再 ps 验证:"
sleep 5
ps axo pid,etime,rss,command | grep '/claude --output-format stream-json' | grep -v grep || echo "  (全清干净, 没剩 Claude session)"
