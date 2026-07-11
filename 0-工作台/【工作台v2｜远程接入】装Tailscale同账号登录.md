**这是什么**：工作台 v2 手机远程访问的唯一 owner 侧动作——装 Tailscale 并登录（账号/设备登录是身份操作，机器代办不了）。
**需要你做什么**：在 Mac 和 iPhone 上装 Tailscale 并用同一 Google 账号登录（约 10 分钟，$0，逐步点击见下），装完在下面回一行或拖 done/。
**不办会怎样**：手机远程接入一直停在冻结位；办完后机器接着配 serve + 钉死身份。

# 工作台 v2 — Tailscale 接入（owner 身份动作，机器代办不了）

为什么：工作台 v2 的手机远程访问走 Tailscale（零公网暴露、零密钥、免费——调研裁定见 workbench/research/CD-intent-queue-remote-access.md）。账号创建/设备登录是身份动作，按契约到步即停交给你。

## 逐步点击（Mac，约 5 分钟）

1. 浏览器打开 https://tailscale.com/download/mac → 点 **Download Tailscale**（标准版 .pkg，不用 App Store 版也行，二选一均可）
2. 打开下载的安装包 → 一路下一步装完 → 菜单栏出现 Tailscale 图标
3. 点菜单栏图标 → **Log in…** → 浏览器弹出登录页 → 选 **Sign in with Google**（建议用你的 Google 账号；这一步会自动创建免费 tailnet）
4. 浏览器显示 "Connect device?" → 点 **Connect** → 菜单栏图标变实心 = Mac 已入网

## 逐步点击（开 device approval，1 分钟，安全关键）

5. 浏览器打开 https://login.tailscale.com/admin/settings/device-management
6. 找到 **Device approval** → 打开开关 → Save（已在网设备自动视为已批；以后新设备要你点头才能进来——丢手机场景的保险）

## 逐步点击（iPhone，约 3 分钟）

7. App Store 搜 **Tailscale** → 安装（发行方 Tailscale Inc.）
8. 打开 app → **Log in** → 选同一个 Google 账号 → 允许添加 VPN 配置（iOS 会弹系统确认）
9. 因为第 6 步开了 device approval：浏览器打开 https://login.tailscale.com/admin/machines → 找到你的 iPhone 那行 → 右侧 **⋯** → **Approve**
10. iPhone 上 Tailscale 开关拨到 ON = 完成

## 办完之后

- 把本卡拖进 `0-工作台/done/`（或直接告诉任一会话"Tailscale 装好了"）
- 机器侧接手：`tailscale serve` 挂 8787、把你的登录身份钉进 workbench 的 OWNER_LOGIN、手机 Safari 打开 `https://<你的Mac名>.<tailnet>.ts.net` 验收 M0
- ⚠️ 全程 $0；如果任何页面引导你进付费档（Starter/Premium），停下别点——按契约花钱需你另行签字

相关：[[作战板]] · 方案全文 workbench/research/PLAN-approved-2026-07-10.md
