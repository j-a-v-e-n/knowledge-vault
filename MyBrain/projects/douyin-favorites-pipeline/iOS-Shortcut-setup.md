# iOS Shortcut 配置指南 — 抖音收藏字幕 Pipeline 入口

> 这个 Shortcut 是整套 pipeline 的**入口**：iPhone 抖音 app → 分享 → Shortcut 落地到 iCloud Drive → Mac 接管处理。
>
> **配置时间**：~10 分钟 · **永久有效**：iOS Shortcut 是 Apple 官方功能，永远不失效。

---

## 配置前确认

- ✅ iPhone 已升级到 iOS 16+（Shortcuts app 默认安装）
- ✅ iCloud Drive 已开（设置 → [你的名字] → iCloud → iCloud Drive 打开）
- ✅ Mac 端已跑过 `setup.sh`（会创建 `~/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/`，你 iPhone 文件 app 里能看到这个文件夹）

如果 Mac 端 setup.sh 还没跑——回头让我帮你跑，**iOS Shortcut 这边可以同时配**，互不阻塞。

---

## 配置步骤（共 8 步）

### Step 1: 打开 Shortcuts app

iPhone 桌面找 **Shortcuts**（图标是两个交叠的彩色方块）→ 右上角 **+** 新建 Shortcut。

### Step 2: 命名 + 设为分享菜单可用

1. 顶部点 Shortcut 名字 → 改成 "**抖音收藏存档**"（自己取，但这个名字以后在分享菜单看到的就是这个）
2. 顶部右边 **(i) 信息按钮** → 滑开 **Use with Share Sheet**
3. **Share Sheet Types** 只勾：
   - ✅ Text
   - ✅ URLs
   - ❌ 其他全关掉

### Step 3: 添加 Action 1 — 接收输入

1. 搜索栏输入 "Receive"
2. 选 **Receive [Input] from Share Sheet**
3. 点 [Input] → 改成 **Text**（抖音分享出来主要是文本含 URL）
4. **If there's no input**: Stop and respond → Stop（这样如果用户不通过分享触发，会优雅退出）

### Step 4: 添加 Action 2 — 提取 URL（可选但强烈建议）

抖音分享文本通常长这样：
```
看看这个视频 #美食探店 https://v.douyin.com/abc123XYZ/ -- 复制此链接...
```

我们要从中拿到那个 `v.douyin.com/...` 链接：

1. 搜索 "Match Text"
2. 选 **Match Text** action
3. **Pattern** 填这个 regex：
   ```
   https?://v\.douyin\.com/[^\s/]+/?|https?://(?:www\.)?douyin\.com/video/\d+
   ```
   （这个正则匹配抖音短链 v.douyin.com/xxx 和长链 douyin.com/video/数字）
4. 默认会输出 **Matches** 列表

### Step 5: 添加 Action 3 — 准备文件内容

1. 搜索 "Text"
2. 选 **Text** action（黄色那个）
3. 在文本框里写：
   ```
   [URL]
   [SHARED_TEXT]
   ```
   把 `[URL]` 替换成 **Matches**（点变量插入），`[SHARED_TEXT]` 替换成 **Shortcut Input**

   最终应该长这样（变量是带颜色的胶囊）：
   ```
   <Matches>

   <Shortcut Input>
   ```

### Step 6: 添加 Action 4 — 生成唯一文件名

1. 搜索 "Format Date"
2. 选 **Format Date**
3. **Date**：选 **Current Date**
4. **Format**：选 **Custom**
5. **Format String**：`yyyy-MM-dd_HHmmss`（这样文件名 = 2026-05-08_163045）

### Step 7: 添加 Action 5 — 保存到 iCloud Drive

1. 搜索 "Save File"
2. 选 **Save File**
3. **File**：上一步的 **Text**（Step 5 的输出）
4. **Service**：iCloud Drive
5. **Destination Path**：`/DouyinInbox/<Formatted Date>.txt`
   - `<Formatted Date>` 是 Step 6 的变量
   - 完整路径示例：`/DouyinInbox/2026-05-08_163045.txt`
6. **Overwrite If File Exists**：关闭（每次都新文件）
7. **Ask Where to Save**：**关掉**（自动保存，不要每次问）

### Step 8: 添加 Action 6 — 通知（可选，让你知道存好了）

1. 搜索 "Show Notification"
2. **Title**：抖音收藏存档
3. **Body**：`已保存 → Mac 处理中`

---

## 测试

### 第一次手动测试（不走分享菜单）

1. 在 Shortcuts app 里点你刚建的 "抖音收藏存档" 看完整 actions 列表
2. 顶部 ▶️ Play 测试运行——它会要你输入文本
3. 粘贴一段假数据，比如：
   ```
   测试视频 https://v.douyin.com/test123/ 美食
   ```
4. 应该会通知"已保存"
5. 打开 iPhone Files app → iCloud Drive → DouyinInbox → 看到 `2026-05-08_xxxxxx.txt`

### 真实测试（走抖音分享）

1. 打开抖音 app → 任一视频 → 右下角 **分享** 图标（箭头）
2. 滑出来的菜单里找 **抖音收藏存档**（如果没看到，下滑找"更多"→ 启用它）
3. 点 → 应该秒回 + 通知
4. iCloud Files 里出现新 .txt
5. 几分钟内 Mac launchd 检测到 → yt-dlp 下载 → Whisper 转字幕 → vault `MyBrain/raw/douyin-favorites/` 出一个 .md 文件

---

## 故障排查

| 现象 | 原因 | 修复 |
|---|---|---|
| 分享菜单看不到 Shortcut | Step 2 的 Share Sheet 没开 / iPhone 需要重启 | 检查 Shortcut 信息页 Share Sheet 开关；重启 iPhone |
| 保存失败 | iCloud Drive 没开 / DouyinInbox 文件夹不存在 | Mac 上跑 `setup.sh` 会创建该文件夹（iCloud 同步几秒后 iPhone 也能看到） |
| Match Text 抓不到 URL | 抖音分享文本格式变了 / 用了其他短链 | 不影响 pipeline——Mac 端 process.py 也会 regex 抓 URL（双保险） |
| Mac 端没拉到文件 | iCloud 同步慢（最坏 1-2 分钟）/ launchd 没跑 | 先等 2 分钟；不行的话 `launchctl list \| grep douyin` 看进程在不在 |

---

## 流程总览

```
┌──────────────────────────────────────────────┐
│ iPhone                                        │
│                                               │
│  抖音 app 看到喜欢的视频                      │
│  → 点 ↗ 分享                                  │
│  → 选 「抖音收藏存档」                         │
│  → Shortcut 自动跑                            │
│  → 写 yyyy-MM-dd_HHmmss.txt                   │
│  → iCloud Drive: DouyinInbox/                 │
└──────────────────────────────────────────────┘
                    ↓ iCloud 同步（秒级）
┌──────────────────────────────────────────────┐
│ Mac                                           │
│                                               │
│  launchd 守护 monitor.py                      │
│  → watchdog 检测到新 .txt                     │
│  → process.py 提取 URL                        │
│  → yt-dlp 下载 mp4 + metadata                 │
│  → Whisper Large v3 本地转中文字幕            │
│  → generate_md.py 生成 markdown               │
│  → vault/raw/douyin-favorites/                │
└──────────────────────────────────────────────┘
                    ↓
              你跟 Claudian 聊
              → ingest 沉淀进 wiki
```

---

## Phase 1 存量批量分享（一次性）

setup 完成后，把现在 iPhone 抖音收藏夹里的几十条**手动分享一遍**：

1. 抖音 app → 我 → 收藏 / 喜欢
2. 一个个点开 → 分享 → 抖音收藏存档
3. 大约 10 秒/条 × 几十条 ≈ 5-10 分钟

存量分享完，所有视频自动进 vault。**之后看到喜欢的视频就分享（取代点 ❤️ 收藏）**，pipeline 永久跑。

---

## 备份方案：不用 Shortcut 也能跑

万一 iOS Shortcut 真出问题，**手动 fallback**：

1. 抖音 app 分享 → 选 **拷贝链接**
2. iPhone 打开 Files / iCloud Drive / DouyinInbox
3. 新建一个 .txt 文件，粘贴那个链接

效果一样——pipeline 同样能拉到。

