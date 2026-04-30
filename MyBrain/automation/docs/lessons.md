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
