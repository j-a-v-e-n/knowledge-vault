**需要你做什么**：在这台 Mac 终端运行 `claude setup-token`，浏览器里完成一次登录授权（约一分钟），把输出的长期 token 写进 `~/Projects/ai-investment-v3/.env` 新增一行：`CLAUDE_CODE_OAUTH_TOKEN=<粘贴 token>`。

**为什么**：周研究回合（每周六 10:00 launchd）走 headless `claude -p`，交互态 OAuth 过期后无法自动刷新（官方已知问题，LONGRUN.md H-B3，近期必发）。L3 站已建好插槽：token 会自动从 `.env` 注入子进程环境（`.env` 不入 git）；401/过期时研究轮红灯 + 通知 + 周报如实记录并附本说明，不静默不重试。你这一分钟做完后，周研究轮即不再依赖交互态登录；token 约一年有效，年续提醒归 L6 承诺台账。

**验证（可选）**：`cd ~/Projects/ai-investment-v3 && make accept-l3` —— 冒烟行应显示「auth mode = 长期 token」。

办完 → 拖进 done/
