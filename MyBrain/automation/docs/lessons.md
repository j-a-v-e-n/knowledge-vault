# 经验教训 — 排查与协作方法论

> Javen 和 Claude 共同维护的"吃一堑长一智"清单。**逻辑层教训，不写具体 bug 细节**。
> 遇到 debug 卡死或反复修不通时，先翻这页。

---

## ① 假设链不退出 = 最大盲点

**症状**：连续 N 次"修 X"都失败，但仍在 X 这个假设里打转。

**真相**：当一个假设下的解决方案 ≥3 次失败，**假设本身大概率错了**——不是修的不到位。

**避免**：定一个 hard rule：**同一假设修 3 次失败 → 强制退一步问"我是不是搞错了 root cause？"**——不是"再换个角度修"，是"换个 root cause"。

> 例（2026-04-27 daemon auth）：连续在"keychain 问题"假设下试了 SessionCreate / GUI 改 ACL / 命令行 set-partition-list 都失败，本应早点退出去重新评估，结果浪费 30 分钟才看到 `claude setup-token` 这个 Anthropic 自带的另一条路。

---

## ② 工具自带什么，先看全 `--help`

**症状**：debug 时只搜跟当前关键词相关的 flag，错过其它入口。

**真相**：工具的 maintainer 通常已为常见用例（包括你卡的这种）提供专门 flag/subcommand，但你不全看 help 就发现不了。

**避免**：debug 前 30 秒，**完整跑 `<tool> --help`，所有 subcommands 扫一眼**，特别注意陌生的命令名。

> 例：`claude --help` 列表里 `setup-token` 一直在那，专为 daemon/CI 设。但我之前只 grep "auth/keychain"，错过了它。

---

## ③ 同一症状可能有 N 个独立 root cause

**症状**：看到错误信息（比如 "Not logged in"）就跳到一个 root cause 假设。

**真相**：错误信息是工具开发者归类的"用户友好提示"，**通常合并多种内部状态**：
- "Not logged in" 可能 = keychain 拿不到 / token 过期 / 进程没继承 session / 工具产品策略不让 daemon 用 OAuth / ……

**避免**：看到错误信息**先列 3-5 个候选 root cause**，再选最可能的开始 debug，**不要立刻 commit 到第一个**。

---

## ④ 研究的精度 = 问题的精度

**症状**：研究 agent / Web 搜索给的答案不全，错过关键信息。

**真相**：agent 只回答**你问的具体问题**，不会自己扩展边界。问"怎么修 keychain"得到"keychain 修法"；问"daemon 模式所有合法 auth 路径"才会列出 setup-token / API key / apiKeyHelper 等全部选项。

**避免**：研究 agent / 搜索时，**问题要问"枚举所有可能性"而不是"修这个具体问题"**。如果第一轮研究后还卡，**第二轮研究换个问法**，从 solution space 而不是 problem space 出发。

---

## ⑤ Fallback 时机：真耗尽 vs 假设没招

**症状**：还没耗尽免费方案就提议付费 fallback。

**真相**：**"我假设这条路没招"≠"这条路真的没招"**。前者是认知边界，后者才是事实边界。从前者跳到 fallback 是浪费免费机会。

**避免**：提议 fallback（特别是花钱的）之前，**显式问自己**：
1. 我有没有完整跑 `--help`？（教训 ②）
2. 我有没有列其他 root cause？（教训 ③）
3. 我是不是在同一假设里打转？（教训 ①）
4. 上述都没，是不是该再做一轮研究？（教训 ④）

只有**所有四条都做了**还卡，才是真的"没招"，可以提 fallback。

---

## ⑥ AI 自我打破假设链很难，需要外部输入

**症状**：AI 陷入假设链时，自己很难跳出来。需要用户 push（"我不想付钱"、"再想想"、"还有别的吗"）才能跳。

**真相**：LLM 的 next-token 预测倾向**继续当前推理路径**，而不是自我反思"我整个方向是不是错了"。

**避免**：
- **作为 AI（写给我自己）**：每个回答中显式问一遍"我是不是在假设链里打转？"，特别是当解决方案累积失败时
- **作为用户（写给 Javen）**：发现 Claude 反复修同一类问题但都不通，直接 push："换思路 / 别在这条路上继续 / 看看工具自己有什么 flag"——你的 push 是打破假设链最有效的外力

---

## 🔧 遇到 debug 卡死时的 checklist

按顺序问自己：

```
□ 1. 我跑 `<工具> --help` 全文了吗？看完所有 subcommand 了吗？
□ 2. 当前症状能列出 ≥3 个独立 root cause 吗？还是只想到 1 个？
□ 3. 同一假设下我已经修了 N 次失败？N≥3 就强制退出来重新评估
□ 4. 如果做研究，问的是 "枚举可能性" 还是 "修这个具体点"？
□ 5. 我提议的 fallback 是因为真耗尽了，还是因为我假设没招？
```

任何一条 ✗ → **先解决那条再继续 debug**。

---

## 📝 累积更多教训

新教训按以下格式追加（不要删旧的）：

```markdown
## ⑦ [一句话名字]

**症状**：...
**真相**：...
**避免**：...

> 例（YYYY-MM-DD 某事件）：...
```

来源：实际 debug 后用户/Claude 共同总结。每条都是 hindsight，但写下来就能 prevent 下一次。

---

## ⑦ 长 context + `--resume` 会触发 API stream idle timeout

**症状**：daemon 跑到中途（通常 5-15 分钟后）突然中断，NDJSON 输出末尾出现 `is_error: true` + `result: "API Error: Stream idle timeout"`。重试还是超时。

**真相**：`claude --resume <session-id>` 会把历次 session 的 context 都带进去。随着 daemon 日复一日运行，累积 context 接近或超过 200K token 时，Claude 处理时间变长——单步 thinking 时间若超过 Anthropic API 的 stream idle timeout 阈值（大约 5-10 分钟无输出），连接被服务端切断，客户端收到 stream error。**这个问题不是网络问题，也不是 token limit 问题，是"单步处理太慢导致 stream 心跳超时"。**

**避免**：
1. **每次 daemon 都用 fresh session**（不 `--resume`）——在 `wrapper.sh` 里用 `uuidgen` 生成新 session-id 或完全不传 `-r` flag，每次从干净 context 启动
2. 如果要保持 session 连续性：把 daemon 工作流拆成多个独立 fresh session（先 skill、再看板），每个单独跑，避免单 session 累积过多 context
3. 看到 stream timeout 的第一反应：**先检查是不是 resume 了过大的 context**，而不是怀疑网络或 token limit

> 例（2026-04-29 03:00 daemon）：daemon 连续几天 `--resume` 同一 session，context 累积至 ~200K。03:00 启动后处理 Step 0 审批时 idle 超时，整个 run 失败，没有产出报告。根因分析由主对话 Claude 在 2026-04-29 11:15 完成。修复：改 `wrapper.sh` 不再 `--resume`，每次用 `uuidgen` 新建 session。详见 `automation/runs/2026-04-29.md`。

---

## ⑧ Python 解释器升级 vs 系统老 C 库 = 隐藏 dyld 不匹配

**症状**：Python `import xml.parsers.expat` 或 yt-dlp / 任何用到 XML 的库突然报 `Symbol not found: _XML_SetAllocTrackerActivationThreshold` / `No module named expat; use SimpleXMLTreeBuilder instead`。重装 yt-dlp 不解决。`python3 -c "import xml.parsers.expat"` 看似 OK 但 yt-dlp 子进程一调就 fail（或反过来）。

**真相**：Homebrew Python 3.13/3.14 编译时链接了**新版 expat**（含 `XML_SetAllocTrackerActivationThreshold` 等新 symbol），但 macOS 系统自带 `/usr/lib/libexpat.1.dylib` 还是老版（缺这些 symbol）。Python 启动时 dyld 优先去 `/usr/lib/` 找 libexpat → 找到老版 → resolve 不出新 symbol → ImportError。**这不是 Python bug 也不是 yt-dlp bug，是 dyld 版本不匹配**。

**避免**：
1. `brew install expat` 装 Homebrew 新 expat 到 `/opt/homebrew/opt/expat/lib/`
2. 启动 Python 进程时设 `DYLD_LIBRARY_PATH=/opt/homebrew/opt/expat/lib` 让 dyld 优先找 brew 的 expat
3. **launchd plist 里的 `EnvironmentVariables` 可能被 SIP 剥离 DYLD_***——关键 subprocess.run 调 yt-dlp 时**显式传 `env={'DYLD_LIBRARY_PATH': ...}`** 双保险
4. **诊断信号**：错误信息含 `Symbol not found:` + `Expected in: /usr/lib/...dylib` = 100% 这类 dyld mismatch，立刻怀疑系统库 vs brew 库版本

> 例（2026-05-09 task-020 douyin pipeline）：Javen Mac 装了 Python 3.14，daemon 跑 yt-dlp 一律 fail "No module named expat"。误以为 Python 3.14 不兼容 yt-dlp 浪费时间，实际 root cause 是系统 libexpat 老。`brew install expat` + plist 加 DYLD_LIBRARY_PATH + process.py subprocess 双保险传 env 后立即修复。教训：错误信息里"Symbol not found"+"Expected in /usr/lib/"两个关键词同时出现就是 dyld mismatch，别去找 Python/包级别的兼容性问题。

---

## ⑨ 反爬虫游戏中第三方工具会"随时 broken"——pipeline 必须 graceful degrade

**症状**：依赖某个第三方工具下载/抓取某站内容（如 yt-dlp 下抖音 / 微博 / 小红书等），**某天突然 fail**，错误信息可能 misleading（说 cookies 过期 / JSON parse fail / authentication needed），但实际是站点 anti-bot 升级了，工具还没适配。

**真相**：抖音 / 微博 / 小红书等站点反爬虫在打 cat-and-mouse —— 站点改 API → 工具适配 → 站点再改 → 工具再适配，循环往复。**任何依赖单一开源工具的 pipeline 都会经历"工具突然不行了"的状态**，且这个状态可能持续数周到数月（取决于工具维护者反应速度）。

**避免**：
1. **设计 pipeline 时就预设 fallback**：核心 archival action（保存 URL + 元数据）一定 work，富 content extraction（视频 / 字幕 / 图片）允许失败但不阻塞
2. **status 字段三元化**：`success / partial / failed`——partial 是"核心保留 + 富内容缺失"，pipeline 不应该把 partial 当 failure
3. **frontmatter 标记 retryable**：`status: download_pending` 这种，未来 batch retry 时能筛
4. **不依赖单条 path**：对核心功能（如视频下载），调研 2-3 个独立来源（yt-dlp / 第三方 Python 库 / 浏览器自动化），主路径 fail 时自动切换或留路径 ready
5. **错误信息别照单全收**：工具说"cookies needed"不代表加 cookies 就修；先 grep github issues 看是不是已知 broken 状态，再决定 invest 多少时间修

> 例（2026-05-09 task-020 douyin pipeline）：第一次跑用真 douyin URL 测试，yt-dlp 报 "Fresh cookies needed"。我先信了 cookies 是问题，spent 10 分钟试 `--cookies-from-browser chrome/safari`——都 fail。spawn researcher 发现是 yt-dlp issue #12669 + #9667 多个用户同样报告，**底层是 JSON parse fail，cookies 不解决**。立刻 pivot 改 process.py 加 partial fallback：yt-dlp fail 时仍生成 URL-only .md 到 vault，标 status: download_pending，未来 retry 时扫 vault 重跑。**最终解**：Javen push back "URL 索引版不行我要看视频讲什么"。再调研发现可以**自己写 extractor**：Playwright headless chromium + iPhone 移动 UA → douyin 重定向到 iesdouyin 移动分享页（不需要登录）→ 抓 `<video>` 的 `src` (playwm endpoint) → curl 直接下 mp4。整条链路 30 行 Python。教训：(1) 发现某工具对某站突然 broken 时，**先决定 pipeline 是否能 graceful degrade**；(2) 即使主线工具 broken，**不一定要等它修**——很多时候 spend 1-2h 自己写一个针对该站的 minimal extractor 比等社区上游修便宜得多；(3) **mobile UA 是隐藏的"backdoor"**——很多站的反爬虫只针对 PC 网页版，mobile h5 反而宽松。

---

## ⑩ launchd LaunchAgent 跑 Playwright 时 chromium 行为跟 user shell 跑不一样

**症状**：standalone Python 跑 Playwright headless chromium 加载某 page 完全 work，但同样代码在 launchd LaunchAgent daemon 里跑就拿不到 page 内容（比如 `<video>` element 不出现、JS 不执行完、network 请求不一样）。

**真相**：macOS 的 launchd 启动的 process 虽然是 user-level (LaunchAgent)，但**没有 user 的完整 GUI / Aqua session token**。Playwright headless chromium 启动看起来 work，但实际跟 user shell 启动的 chromium **fingerprint 不同**——目标站点的 anti-bot 可能据此返回不同内容（比如不渲染视频、显示客户端推广）。

**避免**：
1. **daemon 不要直接调 Playwright** —— 检测到事件后**spawn `/bin/zsh -l -c '...'`** subprocess 跑实际 Playwright 代码。`-l` (login shell) 让子进程 inherit 完整 user session env
2. **如果连 zsh 也不 work**：上 `osascript -e 'do shell script "..."'` —— 通过 AppleScript 让 GUI session 跑
3. **诊断信号**：standalone 跑 OK，launchd daemon 跑同样代码 fail → 不要怀疑代码 bug，怀疑 session token / fingerprint。检查 `launchctl list` 进程是否在 Aqua session

> 例（2026-05-09 task-020 daemon 跑 Playwright）：写完 douyin_extractor.py，standalone 测试一次成功，集成到 daemon 后 daemon 跑 Playwright 拿不到 douyin `<video>` element。**spent 10 min 怀疑代码 bug 后才意识到**是 launchd vs user shell 的 process tree 差异。**Fix**：改 monitor.py 的 process_file()：daemon 检测到 .txt 后不直接调 process_one，而是 `subprocess.run(['/bin/zsh', '-l', '-c', 'cd ... && python3 manual_run.py'])`。子进程里 Playwright 立刻 work，daemon 流程完整自动化。教训：launchd 里跑 GUI 相关 / browser 相关代码出问题，**第一反应改用 user shell subprocess 隔离**，不要先改代码逻辑。

---

## ⑬ Personal-commitment 类决策 AI 不擅自做 — Faculty 名字 / target school / 合作伙伴

**症状**：写 SoP / cover letter / 个人 essay 时，AI 帮用户挑了 specific 教授名字 / 公司名字 / 合作伙伴 commitment，写进 deliverable 没经用户 explicit confirm。

**真相**：这些是 **personal commitment 类决策**——用户在跟外部世界 publicly 表态 "我跟 X 有 alignment / 我想 join Y / 我尊重 Z"。AI 没有用户的 personal preference / 长期 plan / unstated 信息，**做出来的 commitment 是 hallucinated alignment**。即便 AI 调研 ground truth verify了 X 确实 fit profile，最终选择仍是用户的 personal decision。

**避免**：
- 任何 SoP / cover letter / essay 涉及 **specific person name / specific lab / specific company commitment** 时，default 留 placeholder `[FACULTY/LAB]` + flag "需 Javen confirm 加哪个 / 不加"
- 给 candidate list 让用户选，**不要 default 选 1 个**写进 deliverable
- "推荐 top 1 候选" 时 explicit 说 "我推荐 X，但你 confirm 后我才填" — 不能默认 silence-implies-consent

**反 pattern**:
- ❌ Researcher 给 5 个候选 → 我推荐 #1 → 用户没明确反对 → 我假设 implicit OK → 写进 SoP
- ❌ "I'll add Prof. X by default, change if you want" — 这是 opt-out 不是 opt-in，错的

**Pro pattern**:
- ✅ "I recommend candidate #3 — confirm A/B/C/D before I write it in"
- ✅ Faculty / school / company / 合作 commitment 永远 explicit ask before write

**指令出处**：2026-05-14 Javen "你已经替我选了教授了？？？" — 触发因 v4 SoP 我默认填了 Atanasov 名字（researcher 推荐 + 我推荐 top + Javen 没 explicit confirm 但也没 reject）。Javen reframe 让我看清这是 **personal commitment** 性质决策 AI 越界. 这条违反 owner mindset "需 Javen 决定的事写 blocked on @javen，不擅自决定"。

---

## ⑫ Background Python job — 必须 `-u` + 启动 5 min 内 verify first output

**症状**：spawn 一个 long-running Python script 到 background，log 文件迟迟无新输出，process 看着 alive 但实际不动。

**真相**：两个独立 root cause 一起 conflate:
1. Python `print()` 写到 redirected stdout 是 **block-buffered**（8KB+ 才 flush），`>` redirect / pipe 都触发。log 看似 stuck 实则 buffer 没 flush — 进程是在跑的
2. 真长任务卡在 API call / network blocking 上，process alive 但 CPU 0%

不区分这两个 → 不知道该 wait 还是 kill restart。

**避免**：
- 启动 background Python 永远用 `python3 -u` flag 或 `PYTHONUNBUFFERED=1` env
- **启动后 5-10 分钟内必须 verify first output 出现在 log** —— 不出现立刻 abort + 诊断，不能放着等几十分钟才发现 stuck
- Monitor pattern 不要 match per-iteration log line（如 `s\d+ w\d+`）—— N 个 events 刷屏 + Monitor 自动停。只 match milestone（subject summary / error / final）

> 例（2026-05-14 ECE284 LLM full LOSO）：第一版命令没 `-u`，log 1 小时只 `[start]` 一行，process CPU 0% 跑 40 分钟。Kill 后用 `python3 -u` 立刻看到 first window output。同时一个错：monitor pattern 包含 `s\d+ w\d+` → 每个 window 都 push 一个 notification，瞬间刷屏被自动 stop。

---

## ⑪ Claude Code SDK subagent 状态在内存里，磁盘上没 status 字段——session 一卡只能重启

**症状**：spawn 多个 subagent (e.g. 4-6 个 design / synthesizer / reviewer) 全部 task-notification 回来标 `completed`、`TaskOutput` 也都返回 `No task found with ID: ...`，但 **Stop hook 持续报 `Background subagents are still running`**，导致 turn 无法干净结束——AI 被迫输出 `.` 顶住循环，user 必须 esc 打断才能给新指令。

**真相**：SDK 把 "active subagents" 这个 map 存在 **Claude Code Node.js 进程的 in-memory state** 里。磁盘 `~/.claude/projects/<vault>/<sid>/subagents/agent-*.meta.json` **只存 `{agentType, description}` 两个字段，没有 `status`**——所以从外部改文件清不了 phantom state。Spawn 多个 agent 时 SDK 有 race condition，某个 agent 的 completion 没正确 dec 计数器，map 里残留"幽灵" entry，但实际 task ID 已被 GC。**这是 SDK 层 bug，不是 user-defined hook 的错**（`~/.claude/settings.json` 里没有 hooks）。

**避免 / 应急**：
1. **同 turn 内 spawn agent 上限**：≤ 4 个并行 + 1 个 synthesizer + 1 个 reviewer = **总数 ≤ 6**。超过这个数 race condition 概率显著上升。可拆成两 turn（第一 turn spawn 调研 agent，第二 turn 才 spawn synthesizer）
2. **检测**：发现 `TaskOutput` 对所有已知 task ID 都返 `No task found`，但 Stop hook 仍报 `Background subagents are still running` → 100% 是 phantom state，**不要再 retry TaskOutput / TaskStop，没用**
3. **唯一干净 fix = 重启 Claude Code session**——但前提是 user 已经拿到他要的产出（产出已落盘到 vault，不会丢）
4. **不能 kill 当前 PID**：`ps aux | grep claude` 找到 `claude --output-format stream-json` 那个 process 就是当前 session，kill 它 = 断当前对话
5. **僵尸进程清理**：长时间用 Claude Code 会累积旧 session 进程（每个 ~75MB RSS），定期 `ps aux | grep "claude.*stream-json"` 查，对**不是当前 PID** 的旧 PID 跑 `kill <pid>` 回收内存

> 例（2026-05-12 wiki/AI ingest meta-design pipeline）：spawn 4 parallel design agent (A reliability / B multi-agent / C industry SOTA / D Javen-fit) + 1 writer synthesizer + 1 reviewer = **6 agents**。全部 completed task-notification 回来，但 Stop hook 持续报 background running。Try `TaskOutput task_id=... block=false` 对 6 个 ID 全部 `No task found`。Try `TaskStop` 同样 No task found。Read meta.json 发现磁盘上只有 type+desc 字段——内存状态外部清不了。**结果**：被迫输出 `.` 顶住 Stop hook 几百轮，user esc 打断后才能继续。教训：(1) **spawn agent 数有隐形上限** ≈ 6，超了触发 race condition；(2) **现象是症状**——AI 看起来"罢工"实际是 SDK 不让 turn 结束；(3) **预防**：复杂 meta-design pipeline 拆成 ≤ 2 个 turn，每 turn ≤ 4 agent。

**Workaround 命令**（user 端用）：

```bash
# 查所有 Claude Code session 进程
ps aux | grep "claude.*stream-json" | grep -v grep

# 清非当前的僵尸进程（替换 PIDs 为查到的旧 PID）
kill <PID1> <PID2> ...

# 重启 Claude Code = 让当前 session 自然结束后开新窗口
```

---

## ⑨ WebFetch 拿 enumerated list 必须强制 verbatim 不允许 summarize

**症状**：用 WebFetch 问"list X 上有哪些 item"，LLM 内部 summarize 时**漏项**，给的 partial list 看起来 complete，但其实丢了关键 entry。下游基于这个 partial list 答错。

**真相**：WebFetch 内部用小模型处理 HTML 然后用 prompt 提问。小模型 default "concise summary" 模式——看到长 list 会**摘选 salient subset**，不主动给完整 enumeration。"Quote exact text" 这种 prompt 不够强制——它对 prose 段落有效，但对长 bullet/comma list 仍可能截断。

**避免**：WebFetch 任何涉及**完整 enumerated list / clause** 时，prompt 必须 explicit：

```
Show me the EXACT, COMPLETE text of [list X]. 
Do NOT summarize. Do NOT skip items. Show every single item in the list verbatim.
```

这个 anti-omission 措辞比 "quote exact text" 强。

**适用范围**：approved course list / eligible model list / requirement enumeration / supported features list / policy clause 全文 / 任何"我要看完整 list" 的场景。

> 例（2026-05-15 Warren Area Study）：第一次 WebFetch warren area-studies.html prompt "Find rules... Quote exact text" → LLM 返回 SS Area Study list **只 11 个 discipline**（漏了 COGS / 14 个其他）。Javen catch "COGS 算, 你没好好找"。第二次 prompt 改 "Show me the EXACT, COMPLETE text... Do NOT summarize" → LLM 返回完整 **25 个 discipline list 含 Cognitive Science**。这种漏 list 项的错最隐蔽——partial list 看起来 authoritative，下游基于它出邮件 / 答 Javen 都是错的。

**跟 ④ "研究的精度" 的关系**：④ 说**问题边界**（problem vs solution space），这条说 **answer completeness**（item-level enumeration）——两个独立维度，都要 cover。
