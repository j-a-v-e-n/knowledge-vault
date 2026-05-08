# 状态总览（Javen 回来看这一个文件就够）

**最后更新**：2026-05-08（主对话 Claude 自主推进，Javen 临时离开）

---

## 当前进度：⏳ 等你回来跑 setup.sh + 配 iOS Shortcut

```
[✅] 1. 代码全写完（8 文件 + 1 教程）
[✅] 2. reviewer audit + 11 bug fix 全部 apply
[✅] 3. 全部 syntax 通过（python -m py_compile / bash -n）
[⏳] 4. 你跑 setup.sh         ← 接下来要做
[⏳] 5. 你配 iOS Shortcut      ← 接下来要做
[⏳] 6. 端到端测试一条 test.txt
[⏳] 7. Phase 1 存量批量分享 ~几十条
```

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

