# Douyin Favorites Pipeline

自动化处理抖音收藏视频：下载 → 转字幕 → 生成 vault 笔记

## 架构

```
iPhone Shortcut
    ↓ (保存 URL 到 iCloud Drive)
~/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/
    ↓ (watchdog 监听)
monitor.py → process.py → transcribe.py → generate_md.py
    ↓
MyBrain/raw/douyin-favorites/<date>_<title>.md
```

## 组件

| 文件 | 功能 |
|------|------|
| `monitor.py` | 守护进程，监听 DouyinInbox/ 新 .txt 文件 |
| `process.py` | 处理单条 URL：提取 → 下载 → 转字幕 → 生成笔记 |
| `transcribe.py` | Whisper 本地转写（优先 mlx-whisper，fallback faster-whisper） |
| `generate_md.py` | 生成 markdown 笔记 |
| `com.javen.douyin-pipeline.plist` | launchd 配置（开机自启 + 自动重启） |
| `setup.sh` | 一键安装脚本 |

## 安装

```bash
cd "/Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/douyin-favorites-pipeline"
chmod +x setup.sh
./setup.sh
```

安装过程会：
1. 检查 python3、ffmpeg、yt-dlp（缺失则自动安装）
2. 安装 Python 依赖（watchdog、yt-dlp、mlx-whisper/faster-whisper）
3. 创建目录结构（processed、errored、cache、logs）
4. 注册 launchd daemon（开机自启）

## iOS Shortcut 配置

**详细 step-by-step 教程**：[iOS-Shortcut-setup.md](./iOS-Shortcut-setup.md)（包含 8 个 actions 配置 + 测试步骤 + 故障排查 + Phase 1 存量批量分享指南）

简要概览：
1. **触发**: 分享菜单 → 接受 Text/URL
2. **动作**: Match Text 提 douyin URL → Format Date → Save File 到 iCloud Drive `DouyinInbox/<timestamp>.txt`
3. **内容**: URL + 原始分享文本（双保险，Mac 端 process.py 也会再 regex 提一次）

## 使用流程

1. iPhone 看到想保存的抖音视频 → 分享 → 运行快捷指令
2. URL 自动保存到 iCloud Drive
3. Mac 端 daemon 检测到新文件 → 自动处理
4. 笔记生成到 `MyBrain/raw/douyin-favorites/`

处理时间：1 分钟视频约 3-5 分钟（含下载、转写）

## 日志位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/
├── monitor.log          # monitor.py 运行日志
├── processed.jsonl      # 处理记录（每条 URL 一行 JSON）
├── launchd-stdout.log   # launchd 标准输出
└── launchd-stderr.log   # launchd 错误输出
```

## 故障排查

### Daemon 没在跑

```bash
# 查看状态
launchctl list | grep douyin

# 重启 daemon
launchctl unload ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist
launchctl load ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist

# 查看错误日志
tail -f ~/Library/Mobile\ Documents/com~apple~CloudDocs/DouyinInbox/logs/launchd-stderr.log
```

### mlx-whisper 装不上

mlx-whisper 只支持 Apple Silicon。如果安装失败，代码会自动 fallback 到 faster-whisper。

手动装 faster-whisper:
```bash
pip3 install faster-whisper
```

### yt-dlp 下载失败

抖音可能会封禁 IP 或需要登录。检查：
```bash
yt-dlp --verbose <抖音URL>
```

可能需要：
- 更新 yt-dlp: `brew upgrade yt-dlp`
- 配置 cookies（见 yt-dlp 文档）

### iCloud 文件不同步

- 确保 Mac 和 iPhone 登录同一 Apple ID
- 系统偏好设置 → Apple ID → iCloud Drive 已开启
- iCloud 存储空间充足
- 强制刷新: Finder → iCloud Drive → 右键该文件夹 → 下载

### 字幕质量差

Whisper large-v3 是目前最强中文 ASR 模型。如果质量仍不理想：
- 检查视频音质（背景音乐太响、环境噪音）
- mlx-whisper 比 faster-whisper 快但可能精度略低，切换试试

## 维护命令

```bash
# 停止 daemon
launchctl unload ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist

# 启动 daemon
launchctl load ~/Library/LaunchAgents/com.javen.douyin-pipeline.plist

# 实时查看日志
tail -f ~/Library/Mobile\ Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log

# 清理缓存（释放空间）
rm -rf ~/Library/Mobile\ Documents/com~apple~CloudDocs/DouyinInbox/cache/*

# 查看处理历史
cat ~/Library/Mobile\ Documents/com~apple~CloudDocs/DouyinInbox/logs/processed.jsonl | jq
```

## 隐私与性能

- **所有处理本地完成**，不发数据到外部 API
- Whisper 模型首次运行会下载约 3GB（缓存后不再下载）
- mlx-whisper 利用 Apple Silicon Neural Engine，比 CPU 快 2-3x
- 单条视频失败不影响后续处理（错误隔离）

## 技术栈

- **文件监听**: watchdog
- **视频下载**: yt-dlp
- **语音转写**: mlx-whisper (Apple Silicon) / faster-whisper (fallback)
- **进程管理**: launchd (macOS native)
