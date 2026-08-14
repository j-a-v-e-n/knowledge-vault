**需要你做什么**：花约 1 分钟注册 healthchecks.io 免费账号并把 API key 填入 `.env`，激活「机器停摆也能发现」的离机心跳告警（可选再花 1 分钟装 ntfy 手机推送）。

## 背景（30 秒）

投资系统 V3 的 L1 心跳站已建成（2026-08-14，`make accept-l1` 全绿）：每日/每周/每月/每季四个任务**成功才 ping**；超过宽限期没 ping，healthchecks.io 自动**发邮件**给你——这是唯一能抓「机器根本没跑」（断电/卡登录屏/LaunchAgent 掉载）的机制。机械部分全部建好，只差你的免费账号钥匙。

## 一次性动作（约 1 分钟）

1. 打开 https://healthchecks.io ，用邮箱注册免费账号（免费层 20 个 check，本系统用 4 个，$0）。
2. 登录后 Settings → API Access，创建一个 **read-write API key** 并复制。
3. 把 key 粘进 `~/Projects/ai-investment-v3/.env` 已留好的空槽：`HEALTHCHECKS_API_KEY=<粘贴>`
4. 终端运行：`cd ~/Projects/ai-investment-v3 && make heartbeat-setup`（自动建好 4 个 check，看到 4 行 "heartbeat check ready" 即完成）。

之后无需任何日常动作；随时 `make heartbeat-status` 可查警报态。

## 可选加装：手机推送镜像（约 1 分钟）

手机装 **ntfy** 应用（App Store 免费），订阅主题：`aiinv3-b0b752cb970b`（已写在 .env 的 NTFY_TOPIC）。此后系统本机通知（每日红灯、对账警报、周报生成等）会同步推送到手机。不装不影响心跳邮件。

办完 → 把本卡拖进 done/

相关：[[作战板]]（该项目按你的裁定不上板，仅此一卡）
