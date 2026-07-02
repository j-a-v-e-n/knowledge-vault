# Git 备份 — 收尾步骤

> 我（Claude）已经做完：建 `.gitignore`、`git init`、initial commit (`5b1498f`)。
> 剩下 GUI 部分必须你点。每步标了预计耗时。**总共 ≤ 5 分钟。**

## ✅ 已完成（我做的）

- `.gitignore` 已配（排除 raw/、attachments/、archive/、Clippings/、daemon logs、Obsidian workspace state、plugin binaries）
- `git init -b main` 已运行
- `git config user.name / user.email` 已设
- Initial commit `5b1498f` 已建（117 文件，9MB）
- 当前还没有 remote，纯本地仓库

## ⏳ 待你做

### 步骤 1：建 GitHub 私有 repo（30 秒）

1. 打开 https://github.com/new
2. 填：
   - **Repository name**: `knowledge-vault`（或你喜欢的名字，注意是 private）
   - **Description**: `My Obsidian knowledge vault — text + config only, raw/ excluded`
   - **Visibility**: ⚠️ 选 **Private**
   - **不要勾** "Add a README", "Add .gitignore", "Choose a license"（我们已经有了）
3. 点 **Create repository**

### 步骤 2：连接远程并 push（复制粘贴 1 行命令，30 秒）

打开 terminal，进 vault，跑（替换 `<你的GitHub用户名>` 为 `j-a-v-e-n` 或实际的）：

```bash
cd '/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库'
git remote add origin git@github.com:j-a-v-e-n/knowledge-vault.git
git push -u origin main
```

如果你没配 SSH key，用 HTTPS 版本（会让你登 GitHub）：

```bash
git remote add origin https://github.com/j-a-v-e-n/knowledge-vault.git
git push -u origin main
```

push 成功后，你的 vault 就在 GitHub 私有 repo 里了，**第一次异地备份达成**。

### 步骤 3：装 Obsidian Git plugin（实现自动 5 分钟 commit + push，1 分钟）

1. 打开 Obsidian → 左下角 ⚙️ Settings
2. 左侧 **Community plugins** → 如果第一次用，点 **Turn on community plugins**
3. 点 **Browse**（社区插件商店）
4. 搜 `Obsidian Git`（作者 Vinzent03，下载量最高那个）
5. 点 **Install** → **Enable**
6. 关闭 settings，等 1-2 秒，plugin 自动认识到你已经 git init 了
7. 重新打开 Settings → 左侧最下面找到 **Obsidian Git**，进设置：
   - **Vault backup interval (minutes)**: `5`（默认就是 5）
   - **Auto pull on startup**: 关掉（不必要——Google Drive 已经在跨设备 sync）
   - **Auto push interval (minutes)**: `5`
   - **Commit message**: 默认的 `vault backup: {{date}}` 就行

搞定。从此每 5 分钟自动 commit + push 到 GitHub。

## 验证

跑完上面 3 步后，回来跟我说 "git 装好了"，我会：
- 查 `git log` 确认有 plugin 自动 commit 出现
- 标 task-008 c1 ✅ 在看板
- 把审批移到 ✅ 已批准列

## 问题处理

### Q: SSH key 我从来没配过怎么办？

用 HTTPS 路径（步骤 2 的第二个命令）。第一次 push 会让你登 GitHub，照做就行。

### Q: 插件 settings 里"Source control" 一直说 "fatal: not a git repository"？

那说明 Obsidian 没看到 `.git/` 目录。可能是：
1. Vault root 不对——确认 Obsidian 打开的是 `/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库`
2. 插件版本太旧——Update 到最新

如果还卡，告诉我具体报错，我看。

### Q: Google Drive sync 会不会跟 git 打架？

不会。Drive sync 只关心文件内容变化，git 的 `.git/` 目录 Drive 也会同步。理论上多设备同时改同一文件时，Drive 的"最后写入赢"和 git 的"先 commit 谁赢"会冲突——但你只在一台 Mac 上写，所以无影响。**只要别在第二台设备 git push 改写，Drive 自己 sync 就行。**

### Q: 想不要 plugin，让 Claude 帮我装个 launchd 自动 commit？

可以，告诉我 "用 launchd 不用 plugin"，我帮你写一个 LaunchAgent 跑 `git -C vault add -A && git commit -m "auto" && git push` 每 5 分钟。但前提是你已经做完上面步骤 1 + 2（建 GitHub repo + 配 remote）。

---

*生成 2026-04-28 by Claude (task-008 c1, approved in approvals.md)*
