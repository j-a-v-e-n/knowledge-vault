# 状态总览（Javen 回来看这一个文件就够）

**最后更新**：2026-05-09（主对话 Claude，Javen 在配 iOS Shortcut 中，跨窗口接力）

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

