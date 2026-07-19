**需要你做什么**：在 box（ROG-STRIX）的 Windows 上做两步各 1 分钟的设置（下面有逐步点击），让开机后 WSL 自动拉起；做完在本卡末行填 `done: YYYY-MM-DD`。
**这是什么**：v2 夜窗 07-15..07-18 连丢四晚的最后一块拼图。R13 已修好 systemd 侧（Persistent=true 补火 + 早晨补窗截断到 09:00，box 上已部署实测），但这些都要求 **WSL 在开机后真的被拉起**——机器查证：Windows 开机不会自动启动 WSL，Startup 目录里也没有拉起项，所以 box 半夜/清晨开机时窗口机制根本没机会跑。机器无管理员权限、且这是你 Windows 主机的安全姿态（自动登录），按三停②排队给你。
**不办会怎样**：box 只要在 21:00-23:00 处于关机，那晚的 v2 学习窗仍会丢（Persistent 补火只在 WSL 被拉起后才评估）；等于四晚故障只修了一半。新监控（v2-window-nightly）会在连丢两晚时告警，但告警不能替你把 WSL 拉起来。

---

## 两步（照点即可）

**第 1 步 — 开机自动登录**（否则停在登录界面，什么都不会跑）：
1. `Win+R` → 输入 `netplwiz` → 回车。
2. 取消勾选「要使用本计算机，用户必须输入用户名和密码」→ 应用 → 输两次你的密码。
   - 若没有这个勾选项：设置 → 账户 → 登录选项 → 把「若离开，何时要求再次登录」设为「从不」，并关闭 Windows Hello 登录要求后重试。
   - 安全取舍你拍：这台是家里的专用工作机，自动登录=拿到物理接触的人可直接进系统。

**第 2 步 — 登录后自动拉起 WSL**：
1. `Win+R` → 输入 `shell:startup` → 回车（打开当前用户的启动文件夹）。
2. 在里面新建文本文件，改名为 `ai-architect-wsl.bat`（确认后缀是 .bat），内容一行：
   ```
   C:\Windows\System32\wsl.exe -d Ubuntu --exec /bin/true
   ```
   （distro 名以 `wsl -l -q` 输出为准；机器从 box 内部查到是 Ubuntu 26.04，名字通常就是 `Ubuntu`。）
3. 原理：这一下把 WSL 虚拟机连同 systemd 一起拉起；systemd 常驻后 WSL 不会闲置关机，战役 watchdog、v2 定时器、Persistent 补火全部就位。窗口一闪而过属正常。

**验证（可选，30 秒）**：重启 box → 等 2 分钟 → 开个终端进 WSL 跑
`systemctl --user list-timers | grep v2-start` 有输出即成。

---

done: <填YYYY-MM-DD>
