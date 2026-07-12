**需要你做什么**：跑一行命令授权启动「十日战役」无人值守守护（这是唯一需要你拍的开关——启用 approval-off 自治，被安全闸挡在你这里）。

---

# 战役 GO-LIVE 授权卡

相关：[[战役纲领]] · [[战役日志]] · [[协调-并行会话]] · [[收入已验证的AI生意-案例库-v1]]

## 一句话现状
续跑引擎**已建成、已证明、已加内存保护**，就差最后一个开关没合——而这个开关**只有你能合**。

## 为什么卡在你这
启用守护 = 让一个常驻 launchd 进程反复起 `claude -p --permission-mode bypassPermissions` 的工作者（**免批准、无沙箱**）连续跑十天+。这是一次真正的「授权机器 approval-off 自治」决定，Claude Code 的安全闸（正确地）把它挡下来，要你**本人显式同意**。跑下面这行命令，就是你的同意。

## 你跑这一行（在**普通（非 auto）**终端里，会弹一次权限确认，按同意）
```bash
bash ~/ai-architect/campaign/go_live.sh
```
它幂等做三件事：① 确保 memguard 起着（内存安全）② 装载并加载 supervisor 守护 ③ 建 `CAMPAIGN_ACTIVE` 哨兵 = 开跑 Round 1，之后自动一轮接一轮。

看它在跑：
```bash
tail -f ~/ai-architect/campaign/logs/events.jsonl
```
想暂停（保状态、可无损恢复，不是「停」）：
```bash
bash ~/ai-architect/campaign/stand_down.sh
```

## 合闸前我已替你做完并**证明**的（都不需要你操心）
- **纲领立为单一真相源**（你的 CONTINUOUS 版，明令取代旧版）；worker 每轮读它当律法，改纲领零代码传播。
- **并行撞车已化解**：你关掉的那个窗口建的续跑层（质量很高）我没重写、直接整合并补全了 finish line。
- **看门狗四证全过、且是 CODE 核验（非机器自评）**：单写者锁 / kill→单份干净恢复+孤儿回收 / 崩溃循环→退避+relaunch 天花板 / 对 v2 夜间窗口完全让路。证据：`campaign/tests/PROOF-RESULTS.md`。
- **内存看门狗已装载**（v2 的那个只管 /v2/ 且本机已停用，有 47GB 崩机前科）；精确只扫战役自己的进程后代，**绝不误杀你手上的交互 claude**。
- 已 commit + push（gitleaks 干净）。

## 我**没有**替你担保的（诚实边界）
只证明了「续跑机器牢」——**还没跑过一轮真实工作**，所以「战役能产出好东西」这句我现在**不能**打包票。合闸后 Round 1 才是第一轮真活；它的质量由**它自己的独立评审闸**把关，坏轮会被证明过的退避/天花板/wallclock/memguard 兜住，不会风暴、不会崩机。你也可以随时 `stand_down.sh` 拉闸。

---
办完 → 把本卡拖进 `0-工作台/done/`（无 watcher，手动归档）。
