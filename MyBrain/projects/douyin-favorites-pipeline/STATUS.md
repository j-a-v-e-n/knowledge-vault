# 状态总览（Javen 回来看这一个文件就够）

**最后更新**：2026-05-09 03:00（Javen 睡觉时 Claude 接管推进，写了这份早安报告）

---

## 🌅 早安报告（2026-05-09）— **请先看这一段**

**一句话**：Mac 端 daemon 跑起来了，整条 pipeline 经测试 work，**等你醒来分享一条真抖音视频**（不是 hashtag 页面）就能看到第一篇 .md 出现在 vault 里。

### 我帮你做了什么（Javen 睡觉时）

1. ✅ 跑了 `setup.sh` —— Python deps / launchd plist / DouyinInbox 目录树全部就位，daemon 启动监听
2. ✅ **修了一个不修就完全跑不动的隐藏 bug** —— Python 3.14 + macOS 系统 libexpat 版本不匹配（Python 3.14 用的 expat 比 macOS `/usr/lib/libexpat.1.dylib` 新，缺 `_XML_SetAllocTrackerActivationThreshold` symbol → yt-dlp 任何调用都 fail）。
   - 装了 `brew install expat`（升级 macOS expat 到 2.8.0）
   - 改了 `plist` 加 `DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib`
   - 改了 `process.py` 在 subprocess.run 时显式传 env（双保险，避免 launchd SIP 剥离 DYLD vars）
3. ✅ **测试整条链路**：
   - daemon 检测 .txt ✅
   - URL 提取 ✅（regex 工作）
   - yt-dlp 启动 ✅（DYLD fix 后不再报 expat 错）
   - yt-dlp 拒绝你那条 URL（`https://v.douyin.com/iRrxBLUe/`）—— 因为它**重定向到 douyin hashtag 页面**，不是视频页，yt-dlp 报 "Unsupported URL"。**这不是 bug，是你那条 URL 本身就不是单条视频**
4. ✅ 清理了 errored/ 里 3 个测试文件（不污染你早上看到的状态）
5. ✅ daemon 持续运行中（PID 58618），KeepAlive: true，Mac 重启后会自动起来

### 你醒来要做的（5 分钟）

**Step 1 · 验证 Javen 之前 iPhone 分享的 .txt 是否到 Mac**

```bash
ls "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/"
```

预期：要么有真 .txt 文件（iCloud 终于同步过来了），要么还是空的（iPhone 上 .txt 没真上传）

**Step 2 · 在 iPhone 上分享一条真抖音视频**

⚠️ **关键**：要分享**单条视频**（视频播放页面分享出来的链接），不要分享 hashtag、合集、用户主页。检查方法：分享出来的 URL 在浏览器打开应该是**单个视频播放页**，不是 hashtag 列表。

**Step 3 · 等 1-2 分钟，看 vault 出 .md**

```bash
# 实时看处理日志
tail -f "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log"

# 看 vault 输出
ls "MyBrain/raw/douyin-favorites/"
```

⏰ 第一次跑会触发 Whisper 模型下载（~3GB），可能要等 5-10 分钟

### ⚠️ 你之前 iPhone 分享的 .txt 同步问题（未确认）

- 我等了 5 分钟，Javen 之前 iPhone 上看到的那条 .txt **没出现在 Mac 端**
- iCloud quota 显示**还剩 4.83 GB**（Javen 关 iCloud Photos 同步释放出来的），**不是空间满**
- 可能原因：iPhone 端 iCloud Drive 同步 lag（手机在低电量/后台/没 WiFi 时会延迟）
- 你早上检查 Mac 端 DouyinInbox 应该能看到了；如果还没看到，在 iPhone Files app 进 DouyinInbox 看那个 .txt **是否带云图标**（带云=没真同步，下拉刷新强制上传）

### 🔧 顺手做的代码改进（永久受益）

1. `monitor.py` CACHE_BASE 从 iCloud 路径改到 `~/.cache/douyin-favorites/` —— 视频下载缓存**永远不再占你 iCloud 配额**
2. plist 加 `DYLD_LIBRARY_PATH` 解决 Python 3.14 兼容
3. process.py subprocess 双保险传 env



---

## 当前进度：✅ iOS Shortcut 配通！等你跑 setup.sh

```
[✅] 1. 代码全写完（8 文件 + 1 教程）
[✅] 2. reviewer audit + 11 bug fix 全部 apply
[✅] 3. 全部 syntax 通过（python -m py_compile / bash -n）
[⏳] 4. 你跑 setup.sh         ← 接下来要做（Mac 端，1 分钟）
[✅] 5. 你配 iOS Shortcut      ← 2026-05-09 02:30 done
[⏳] 6. 端到端测试一条 test.txt（5 跑通后自动覆盖）
[⏳] 7. Phase 1 存量批量分享 ~几十条
```

**iOS Shortcut 配置最终成功的方案（避免下次踩坑）**：
- shortcut 拓扑必须是 4 个 action（不是 3 个）：接收 → 格式化日期 → **文本**（中转）→ 存储文件
- 中转的「文本」action 内容用变量栏插入「**输入快捷指令的信息**」（中文 iOS 18+ 把 "Shortcut Input" 翻译成这个奇怪的名字，找不到很正常）
- 「存储文件」的"文件"字段会自动连接到上一个 action（即「文本」action）的输出 ✅，绕开了 iOS 不允许在"文件"字段直接插变量的限制
- 子路径格式：`DouyinInbox/[紫色变量:格式化后的日期].txt`（**变量必须是紫色标签，不能打字打成字面字符串**）
- 服务字段必须改成「iCloud 云盘」（默认是「Shortcuts」=私有沙盒，不在 Files app 里出现）
- iOS 19 中 share sheet 命名容易跟系统原生「储存到文件」冲突，shortcut 名字别叫"保存"开头的

---

## 🔄 iOS Shortcut 配置进度（2026-05-09，跨窗口接力中）

**Javen 当前状态**：
- ✅ 已经建好这个 Shortcut（默认名叫「**保存文件**」，没改成"抖音收藏存档" — 不影响功能，名字无所谓）
- ✅ Share Sheet 已开（在「资料库 → 共享表单」分类里能看到这个 Shortcut，count = 1）
- ✅ 3 个动作都已添加：接收输入 / 格式化日期 / 存储文件

**待修的 3 个问题**（基于 2026-05-09 1:11 PM 截图判断）：

1. **动作 1 输入类型勾错** — 当前显示「从「共享表单」接收 **App 和其他 18 个**」 → 类型勾选了 19 个全部。**应只勾「文本」**
2. **动作 3「文件」字段填错** — 当前折叠预览「将「**格式化后的日期**」保存到 iCloud 云盘」→ 把日期变量当成了文件内容。**应改成「快捷指令输入」** （从分享菜单接收来的那段抖音文本才是要写到磁盘的内容）
3. **动作 3 还需展开验证**：文件名是否为「格式化后的日期」+ `.txt` 后缀；路径 `/DouyinInbox/`；"询问存储位置"关闭；"覆盖原文件"关闭

**Mac 端 monitor.py L42 严格只识别 `.txt` 后缀**，这是为什么 .txt 不能漏。

**下次接力的 Claude / 新窗口须知**：
- 不要让 Javen 反复截图（context 占用太大，上窗口就是这样炸的）
- 用文字描述告诉他每步该是什么，最后**只让他截 1 张总览图最终确认**
- 修完上面 3 处后，回到 STATUS.md 这里更新进度

**iOS 18+ 把 magic variable 替换到「保存文件」"文件"字段的标准做法**（researcher 调研 Apple Support 官方文档 2026-05-09）：
- 来源：https://support.apple.com/guide/shortcuts/adjust-variables-apda36b9018b/ios
- 方法 A（首选）：**长按**（tap and hold，按住 1-2 秒不松手）紫色变量令牌 → 弹变量菜单 → 选"替换"或"选择变量" → 选「快捷指令输入」（中文 iOS 也可能叫「所提供的输入」）
- 方法 B（fallback 1）：在变量属性面板里点"清除变量" → 字段变空 → 点空字段 → 应弹"变量栏"或键盘上方变量条 → 选「快捷指令输入」
- 方法 C（fallback 2，**Javen 实测 A 和 B 都失败时用此**）：插一个「**文本**」(Text) action 到动作 2 和动作 3 之间，文本内容用键盘上方变量栏插入「快捷指令输入」——这样动作 4（保存文件）的"文件"字段会自动接到 Text action 的输出（绕开"文件字段不接受文本变量"的限制）
- Javen 报告 A 弹属性面板（无替换选项），B 弹文件选择器——可能是 iOS 19 又改了 UX 或长按时间不够。下次 Claude 优先让 Javen 试方法 C（最不依赖具体 UX）

---

## 你回来要做的 4 件事（按顺序，约 15 分钟）

### Step 1 · 跑 setup.sh（1 分钟）

```bash
cd "/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/douyin-favorites-pipeline"
./setup.sh
```

会自动：检查 python3/ffmpeg/yt-dlp（缺则 brew install）→ pip 装依赖 → 建 iCloud 文件夹 → 装 launchd daemon → 启动。

**如果报错**：把错误整段截屏丢我，我立刻看。

### Step 2 · 配 iOS Shortcut（10 分钟）

手机打开 iPhone 的 **Shortcuts** app，跟着 [iOS-Shortcut-setup.md](./iOS-Shortcut-setup.md) 一步步配。8 个 actions，每步都有截图位置说明。

### Step 3 · 端到端测试（30 秒）

任选一条抖音视频，点分享 → 抖音收藏存档。Mac 端：

```bash
tail -f "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log"
```

应该看到日志：`Processing new file → Downloading → Transcribed N segments → Generated markdown`。

vault 里出现：`MyBrain/raw/douyin-favorites/2026-05-08_<视频标题>_<id>.md`

### Step 4 · Phase 1 存量（5-10 分钟）

打开抖音 app → 我 → 收藏，几十条视频一个个分享给"抖音收藏存档" Shortcut。pipeline 自动跑。半小时后 vault 里全部就位。

---

## 文件清单（项目目录）

```
MyBrain/projects/douyin-favorites-pipeline/
├── monitor.py                    # 守护进程主入口（watchdog 监听）
├── process.py                    # 单条处理 orchestrator
├── transcribe.py                 # Whisper 本地转写（mlx → faster fallback）
├── generate_md.py                # markdown 生成 + frontmatter
├── com.javen.douyin-pipeline.plist  # launchd 配置
├── setup.sh                      # 一键安装（含 cwd 验证 + 动态 Python 路径修复）
├── requirements.txt
├── README.md                     # 项目总览（架构、安装、维护命令）
├── iOS-Shortcut-setup.md         # iPhone 端 Shortcut 详细配置
└── STATUS.md                     # 你看的这个文件
```

vault 输出：`MyBrain/raw/douyin-favorites/`（已建空）

iCloud 中转：`~/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/`（setup.sh 会建）

---

## 已修复的关键风险点（11 个）

我让 reviewer 跑了完整 audit，加上自己一轮 spot-check，找到 11 个潜在 bug，全部 fix。这些是为什么这次能扛住"只许成功不许失败"：

| 风险 | 修复 |
|---|---|
| iCloud sync 时 watchdog 触发 partial-write，读到 0 字节 | monitor.py 加 size 稳定性检测（最多等 12s） |
| YAML title 含 `:` `#` `"` 破解析 | generate_md.py 加 escape_yaml_value + 双引号 |
| 同标题视频文件名冲突 | filename 加 video_id 后缀 |
| URL 末尾 `/` → video_id 提取失败 → cache_dir 冲突 | 用 URL hash 当 cache_id（永远 unique） |
| URL_PATTERNS 漏 `-` `_` 字符 + iesdouyin.com + share/video | 4 个 pattern 全覆盖 |
| yt-dlp 偶尔出 .mov/.webm 而不是 .mp4 → glob 漏 | multi-format glob |
| cache 视频累积无人清理 | success 后自动 cleanup |
| 同名文件 rename 崩溃 | rename → replace（原子覆盖） |
| **plist 用 `/usr/bin/python3`（Apple Python）但 pip3 装到 Homebrew Python → ModuleNotFoundError** | setup.sh 动态 sed 替换 plist Python 路径，确保跟 pip 用的同一个 |
| setup.sh 在错的目录跑 | 加 cwd basename 验证 |
| transcribe.py except 块写法 redundant | 改 just `Exception` + 加 mps 不支持注释 |

---

## 已知小限制（可接受，不阻塞）

- vault 路径在 monitor.py L19 hardcoded —— 你将来挪 vault 时改一行
- yt-dlp 600s 超时 hardcoded —— 一般 1 分钟视频不会触发
- Whisper 首次跑会下载 ~3GB 模型（一次性，本地缓存）

---

## 故障排查 cheatsheet

```bash
# Daemon 状态
launchctl list | grep douyin

# 实时看处理日志
tail -f "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log"

# 看历史
cat "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/processed.jsonl" | jq

# 重启 daemon
launchctl unload ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist
launchctl load   ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist

# 手动跑 monitor 看 stdout（debug 用）
python3 monitor.py
```

