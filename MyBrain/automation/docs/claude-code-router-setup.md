# claude-code-router setup guide — Claude Code 路由到便宜模型

> 你 2026-04-29 凌晨表态对"换 LLM 降成本"路线感兴趣。本文是从 0 到 daemon 真的跑 DeepSeek 的完整路径。
>
> **核心动作**：在你的 Mac 上装一个本地 proxy（claude-code-router），让 Claude Code 的请求先走它，由它路由到不同 LLM。**主对话仍走 Claude，daemon 凌晨走 DeepSeek**——预期省 ~90% daemon 成本。
>
> 详细背景见 [[../wiki/工程方法/超级个体_工具与杠杆]]。

---

## ⚠️ 先警告几条

1. **daemon 才稳定 24 小时，不要急着改它的底层**。本 guide 建议时机：daemon 跑顺**至少一周**（5/6 之后），且你期末缓冲期开始
2. **改 daemon 配置前必须备份现有 wrapper.sh / rules.md / prompt.md**（命令在 Step 4）
3. **第一次切 router 后端到端测试一次再上 daemon**——不要直接交给它凌晨自动跑
4. **DeepSeek 在 Anthropic Tool Use 协议上偶有边界 case**——比如复杂 multi-tool chain 可能失败。预期 daemon 整体可用，但 5%-10% 任务可能因协议不兼容失败。要监控
5. **Anthropic 订阅暂时保留**——主对话仍用 Sonnet。先把 daemon offload 出去验证质量满意了，再考虑降订阅档位

---

## 准备：3 个前置条件

### 1. Node.js + npm

检查：

```bash
node --version    # 应该 ≥ v18
npm --version
```

没装的话：[nodejs.org](https://nodejs.org/) 下 LTS 版本 .pkg 装。或 `brew install node`（如果有 Homebrew）。

### 2. DeepSeek API key（最便宜模型）

1. 注册 [deepseek.com](https://platform.deepseek.com/)
2. 控制台 → API keys → Create new key → 复制（**注意：只显示一次**）
3. 充值：起步充 $5（约 ¥36），按 daemon 一晚 ~$0.02 算，能跑半年。**不要充太多**——还在评估期
4. 把 key 安全保存到 `~/.claude-daemon/.deepseek_key`：

   ```bash
   mkdir -p ~/.claude-daemon
   echo "sk-deepseekxxxxxxxxxxxx" > ~/.claude-daemon/.deepseek_key
   chmod 600 ~/.claude-daemon/.deepseek_key  # 只有你自己能读
   ```

### 3. （可选）OpenRouter API key

如果你想灵活调用 Kimi / GLM / 别的国产模型，[openrouter.ai](https://openrouter.ai/) 注册 → 一个 key 通杀几十个模型。**第一次部署不必要**，先只用 DeepSeek。

---

## Step 1：装 claude-code-router

```bash
npm install -g @musistudio/claude-code-router

# 验证装上了
which ccr   # 应该输出路径，比如 /usr/local/bin/ccr
ccr --help
```

> 包名 `@musistudio/claude-code-router`，命令行工具叫 `ccr`。

---

## Step 2：写配置文件

router 配置在 `~/.claude-code-router/config.json`：

```bash
mkdir -p ~/.claude-code-router
```

把下面内容写到 `~/.claude-code-router/config.json`：

```json
{
  "Providers": [
    {
      "name": "anthropic",
      "api_base_url": "https://api.anthropic.com/v1/messages",
      "api_key": "sk-ant-xxxxx_你的_anthropic_key_或_oauth",
      "models": ["claude-sonnet-4-5", "claude-haiku-4"]
    },
    {
      "name": "deepseek",
      "api_base_url": "https://api.deepseek.com/anthropic",
      "api_key": "sk-deepseekxxx_粘你的_deepseek_key",
      "models": ["deepseek-chat", "deepseek-reasoner"]
    }
  ],
  "Router": {
    "default": "anthropic,claude-sonnet-4-5",
    "background": "deepseek,deepseek-chat",
    "think": "deepseek,deepseek-reasoner",
    "longContext": "anthropic,claude-sonnet-4-5"
  },
  "API_TIMEOUT_MS": 600000
}
```

> **关键字段说明**：
> - `Providers`：你支持的所有模型 source。各自 API key 单独配
> - `Router.default`：默认走哪——这是主对话用的
> - `Router.background`：后台 / agentic 任务（claude code 会自己识别）—— **daemon 走这条**
> - `Router.think`：复杂推理任务
> - `Router.longContext`：长 context（≥60k token）—— Sonnet 支持长 context 比 DeepSeek 好

---

## Step 3：启动 router 验证

```bash
ccr start    # 后台启动 proxy，监听本地端口（默认 3456）

ccr status   # 看是否在跑
```

测一次（在新 terminal 跑）：

```bash
# 让 Claude Code 通过 router 跑一次简单对话
ANTHROPIC_BASE_URL=http://localhost:3456 claude -p "用一句话告诉我 1+1 等于多少"
```

预期输出：`1+1 等于 2。`

如果报错 → 检查 `ccr status` 是否在跑，配置文件是否合法 JSON（用 `jq . ~/.claude-code-router/config.json` 验证语法）。

---

## Step 4：备份 daemon 配置 + 改 wrapper.sh

**先备份**（**重要！** 出问题能 5 秒回滚）：

```bash
cp ~/.claude-daemon/wrapper.sh ~/.claude-daemon/wrapper.sh.pre-router-backup
cp ~/.claude-daemon/prompt.md ~/.claude-daemon/prompt.md.pre-router-backup
cp ~/.claude-daemon/rules.md ~/.claude-daemon/rules.md.pre-router-backup
```

然后改 `~/.claude-daemon/wrapper.sh`，在调用 `claude` 之前注入环境变量：

找到这一段：

```bash
# ─── 调用 claude（perl alarm 限时 30 分钟）───────────────
echo ""
echo "─── Invoking Claude Code ───"
```

在 `echo` 前面加：

```bash
# ─── Router: 走 claude-code-router 的本地 proxy ─────────
export ANTHROPIC_BASE_URL=http://localhost:3456
echo "✓ Router enabled: $ANTHROPIC_BASE_URL (daemon background tasks → DeepSeek via router)"
```

---

## Step 5：保证 ccr 持续在跑（关键，否则 03:00 daemon 起来发现 router 没跑）

`ccr` 默认在你启动它的 terminal 关掉后就停了。要让它后台 24h 在跑：

**方案 A**（最简单）：开机自启动 launchd

`~/Library/LaunchAgents/com.musistudio.ccr.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.musistudio.ccr</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/local/bin/ccr</string>
      <string>start</string>
      <string>--no-daemonize</string>
    </array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/tmp/ccr.log</string>
    <key>StandardErrorPath</key><string>/tmp/ccr.err</string>
</dict>
</plist>
```

加载：

```bash
launchctl load -w ~/Library/LaunchAgents/com.musistudio.ccr.plist
launchctl list | grep ccr   # 应该能看到
```

---

## Step 6：端到端验证 — 手动跑一次 daemon

**关键：先手动跑一次，不要直接等 03:00 自动**

```bash
~/.claude-daemon/wrapper.sh   # 不带 check 参数 = 真实运行
```

观察：
1. `~/Library/Logs/claudian/runs/<时间戳>.log` 看是否报错
2. 看 daemon-runs 报告是否正常产出
3. 比较产出质量跟之前 Claude 跑的有什么差异

**如果 OK** → 继续让它每天 03:00 自动跑

**如果报错或质量差** → 立刻回滚（Step 7）

---

## Step 7：回滚（如果需要）

3 秒回到改 router 之前的状态：

```bash
cp ~/.claude-daemon/wrapper.sh.pre-router-backup ~/.claude-daemon/wrapper.sh

# （可选）停掉 ccr
launchctl unload -w ~/Library/LaunchAgents/com.musistudio.ccr.plist
```

下次 daemon 03:00 跑会自动用回 Claude（因为 wrapper.sh 没了 ANTHROPIC_BASE_URL 这行 → claude 走默认 Anthropic 直连）。

---

## 监控建议

部署后第一周每天看：
1. `daemon-runs/<日期>.md` — daemon 任务推进质量
2. `~/Library/Logs/claudian/runs/<最新>.log` — 有无报错
3. DeepSeek 控制台 → API usage — 看实际消耗了多少（验证省钱效果）

如果一周下来质量满意 → 长期保留
如果发现 5%+ 任务失败 → 调整 Router 配置，把更复杂的任务路由回 Sonnet

---

## 知识缺口（部署后回填）

- [ ] DeepSeek-V3.2 处理 daemon 实际任务（看板推进 / kanban Edit / Markdown 编辑）的成功率？
- [ ] 长 context (≥80k token) 时 DeepSeek vs Sonnet 实测差距？
- [ ] DeepSeek 在 Bash 工具调用上的稳定性？
- [ ] launchd 双重 daemon（claudian + ccr）有没有竞争 / 启动顺序问题？

---

## 跟 vault 已有内容的连接

- [[../wiki/工程方法/超级个体_工具与杠杆]] — 核心评估文档
- [[task-board]] task-013 — 这份 setup guide 是它的 deliverable
- [[../system/经验教训]] — 部署完后如果遇到 debug，参考其中的方法论

---

*生成 2026-04-29 by Claude (响应 Javen 凌晨表达的兴趣)*
*前置：daemon 已稳定运行 1+ 周；用户期末缓冲期或之后*
