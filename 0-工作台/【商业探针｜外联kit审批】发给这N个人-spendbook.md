**这是什么**：spendbook 的 demo-first 定向外联 kit（Gen-2 D3 试点）——5 个点名目标，逐目标真数字 demo + 文案 + 合规检查。机器只造 kit，发送永远你的手。
**需要你做什么**：审下面逐目标文案 → 在 decision 行回一个词（发 / edit: 怎么改 / 跳过）。回「发」后你逐个手发，发一个就把该目标的 sent_<handle>: 填上日期（YYYY-MM-DD）；此后有回复再把 reply_<handle>: 改成 replied / positive / paid。
**不办会怎样**：kit 一直躺着，spendbook 就没有任何外联在跑（原社区帖已按 02:51 事故补救令记 not-run）；预注册 ruler 记 not-run（不算负例）。机器每 30 分钟看一次；窗口按你填的 sent 日期逐目标起算，14 天后代码自动判读（判表冻结在 [[spendbook.KIT]]，不再议）。

# 外联 kit 发布审批 — spendbook

decision: 发

## 发送与回执表（发一个填一个；机器只读你的字，绝不代填）

| # | 目标 | 渠道 | 发出日期 | 回复 |
|---|------|------|----------|------|
| 1 | lichenyang-spdev | github-own-thread | sent_lichenyang-spdev: | reply_lichenyang-spdev: none |
| 2 | thiswillbeyourgithub | github-own-thread | sent_thiswillbeyourgithub: | reply_thiswillbeyourgithub: none |
| 3 | gakugaku | github-own-thread | sent_gakugaku: | reply_gakugaku: none |
| 4 | rstagi | email-published | sent_rstagi: | reply_rstagi: none |
| 5 | jfrog-boost | reddit-thread-reply | sent_jfrog-boost: | reply_jfrog-boost: none |

reply 取值：none（默认）/ replied（有人工回复）/ positive（明确想要）/ paid（走到付费）。

## 硬性提醒（发送前）

- rstagi 的邮件里 «OWNER-POSTAL-ADDRESS» 要换成你的真实通信地址（CAN-SPAM 要求，机器不掌握不代填）。
- 每目标只发一次，永不追帖；对方说不再联系即终局。
- 三条 GitHub 回帖各占一个 repo 名额（langfuse / tokencost / litellm），此 kit 内不得再向同 repo 发第二条。
- **GitHub 回帖的合规判定含推断，风险在你的账号上**：官方明文只禁"monetized or excessive
  bulk content in issues"，对"单条、切题、答对方所报问题的回复"无裁定——"单发不算 bulk"是
  我们的推断（出处与原文在 outreach.py CHANNEL_POLICY）。三条回帖都带产品披露；不想担这个
  灰边就回 edit 剔除 GitHub 三条、只发 email+reddit 两条。
- 本卡生命周期：回「跳过」→ 机器 30 分钟内归档进 done/；回「发」→ 卡留在桌面当回执表，
  直到判读收口（intent/weak/zero）机器才归档进 done/（repo runs/ 同步留档）。

## 逐目标最终文案（与 repo 内 spendbook.KIT/targets/ 逐字一致）

### 1. lichenyang-spdev — github-own-thread
（langfuse repo 唯一名额（≤1 发/第三方 repo 码规）；issue 仍 open，他是发起人）

```````
# channel: github-own-thread — reply on https://github.com/langfuse/langfuse/issues/14249
# 发送人：owner 本人 GitHub 账号；单发一次，不追帖。

Your arithmetic in this issue is the failure mode I'm building against, so I ran your numbers through it.

spendbook posts each usage event as a balanced double-entry journal entry, priced from an explicit, versioned price table (LiteLLM commit `8447cd3a` below — its `claude-sonnet-4-6` entry carries the same $3/$15/$3.75 per-Mtok rates as your hand calculation):

```
; spendbook trial balance — 1 usage events (token counts from your issue text)
; prices: litellm-8447cd3a.json (explicit, versioned input — never a hidden constant)
Expenses:LLM:Anthropic:ClaudeSonnet46:CacheWrite5m        0.074288 USD   ; 19,810 tok
Expenses:LLM:Anthropic:ClaudeSonnet46:Input               0.046380 USD   ; 15,460 tok
Expenses:LLM:Anthropic:ClaudeSonnet46:Output              0.155550 USD   ; 10,370 tok
Liabilities:Provider:Anthropic                           -0.276218 USD
sum-check (must be 0)                                     0.000000
```

The cache-write leg is its own posted line: $0.074288 on your trace, the ~$0.08 you found missing. A cost dashboard that drops a leg still shows a plausible smaller total; a double-entry ledger that drops a leg fails its trial balance. Completeness failures become hard failures instead of smaller numbers.

Disclosure: I'm building spendbook and this is a presale validation — the page (https://probe-spendbook.vercel.app) runs Stripe in TEST mode, so nobody can actually be charged today. One question, if you're willing: when you filed this, did you need a per-trace auditable ledger, or was a corrected langfuse formula enough for your case?

```````

### 2. thiswillbeyourgithub — github-own-thread
（tokencost repo 唯一名额；他 contact 页明说首选 GitHub ping（email 渠道因 GitHub AUP §7 弃用——身份链经 GitHub））

```````
# channel: github-own-thread — reply on https://github.com/AgentOps-AI/tokencost/issues/145
# （他发起的 issue；且他本人 contact 页写明首选渠道就是 GitHub ping。改走 GitHub 的原因：
#  GitHub AUP §7 禁止把 GitHub 来源信息用于未经请求邮件，而我们对他的身份链经由 GitHub——
#  冷邮渠道对他不干净，他自宣的首选渠道反而最合规。本 kit 对 AgentOps-AI/tokencost repo
#  仅此一发，单发不追帖）

@thiswillbeyourgithub you filed this issue a year ago — "the openrouter prices are not automatically updated even though could be updated automatically using their API" — and it's still the standing failure mode of that tool class: a price table quietly goes stale and the numbers keep looking plausible.

I'm building the opposite behavior into a small CLI called spendbook: the price table is an explicit, versioned input (a pinned LiteLLM commit), and a model missing from the table refuses to book — never $0, never a guess. Two real runs of the current prototype — same real usage events (17 events extracted from one of my own agent sessions), two real LiteLLM table versions:

```
run 1 — table pinned at commit 8447cd3a (current):
  17 usage events → balanced ledger, total $2.256045, sum-check 0

run 2 — table pinned at commit 3f5c5892 (real table from 2026-04-29):
  ✗ HARD FAIL — model 'claude-opus-4-8' not in price table: refusing to post
    this event at $0 or a guessed price. (exit 2)
```

(spendbook is presale — this is the prototype's real output, not a shipped binary you can install today.)

The usage events are extracted from one of my own agent sessions (token counts verbatim, content stripped); both tables are real LiteLLM commits. Your proposal here was "update automatically via their API" — spendbook's version of the same instinct is "pin explicitly and fail hard on gaps", because an auto-updated table can also silently break, and an audit tool shouldn't guess.

Disclosure: spendbook is mine and in presale validation — the page (https://probe-spendbook.vercel.app) runs Stripe in TEST mode, nobody can actually be charged today. If the hard-fail behavior is what you wanted tokencost to do, that's one real data point for me; if your setup has moved past this problem, that's a useful data point too.

```````

### 3. gakugaku — github-own-thread
（litellm repo 唯一名额；他是 issue 发起人）

```````
# channel: github-own-thread — reply on https://github.com/BerriAI/litellm/issues/29011
# （他发起的 issue；本 kit 对 BerriAI/litellm repo 仅此一发，单发不追帖）

Your audit in this issue is now a before/after case study: the gpt-oss-120b copy-paste pricing you flagged ($3.00/M carrying DeepSeek-V3.1's rate) is fixed in the current table — which means any tool that follows the table silently repriced by ~13× at some commit in between, and nothing anywhere failed loudly.

I'm building a small CLI (spendbook) on the position that the price table must be an explicit, versioned input — same events, two real LiteLLM commits, booked by the current prototype as double-entry ledgers:

```
prices = LiteLLM table at commit 3f5c5892 (real table, 2026-04-29):
Expenses:LLM:Sambanova:GptOss120b:Input         3.000000 USD   ; 1,000,000 tok
Expenses:LLM:Sambanova:GptOss120b:Output        0.900000 USD   ; 200,000 tok
Liabilities:Provider:Sambanova                 -3.900000 USD
sum-check (must be 0)                           0.000000

prices = LiteLLM table at commit 8447cd3a (current pin):
Expenses:LLM:Sambanova:GptOss120b:Input         0.220000 USD   ; 1,000,000 tok
Expenses:LLM:Sambanova:GptOss120b:Output        0.118000 USD   ; 200,000 tok
Liabilities:Provider:Sambanova                 -0.338000 USD
sum-check (must be 0)                           0.000000
```

(Token counts illustrative; both tables and both rates are real. The input-rate delta is exactly your finding — $3.00/M vs $0.22/M, ~13.6×; the ledger totals differ ~11.5× because the output leg moved less. spendbook is presale — prototype output, not a shipped binary.) A missing model is a hard failure (exit 2, never $0); a present-but-wrong price is the failure class pinning alone can't catch — the table diff between pins makes it visible, and reconciling ledger totals against the provider's own billing is the layer I'm building for the rest.

Disclosure: spendbook is mine and in presale validation — the page (https://probe-spendbook.vercel.app) runs Stripe in TEST mode, nobody can actually be charged today. Question: when you did the SambaNova audit, was that for a production cost pipeline of yours, and what does it treat as the source of truth today?

```````

### 4. rstagi — email-published
（hello@ratel.sh 出自公司官网公开业务联系方式（非 GitHub 来源）；CAN-SPAM 六件套齐（邮政地址 owner 发送前替换占位符）；备选 LinkedIn 手动）

```````
# channel: email-published — hello@ratel.sh（地址出自公司官网 ratel.sh 的公开业务联系方式，
# 非 GitHub 抓取；身份发现链经由 HN→GitHub，如实标注）；备选 LinkedIn 手动 linkedin.com/in/rstagi。
# 只发一次。注意：Ratel 做 context 工程（省 token），与 spendbook（成本对账）互补非竞品。
# CAN-SPAM 六件套（FTC compliance guide 逐项）：header/From 真实 ✓、subject 如实 ✓、
# 广告披露 ✓（正文 Disclosure 段，clear and conspicuous）、opt-out ✓（尾段，30 天有效）、
# 邮政地址 = owner 发送前把 «OWNER-POSTAL-ADDRESS» 替换成真实通信地址（机器不掌握、不代填）。
# subject: Your Ask HN post — the 300-tool bug that cost noise hid

Hello Roberto,

I'm writing because of your Ask HN post: inference cost is your main metric, and a bug loading ~300 tools stayed invisible for weeks because the cost movement "got hidden by other changes I made in the same period". That is a totals problem — one number absorbs everything, so nothing stands out.

I'm building spendbook: it posts every usage event from an agent transcript as a double-entry journal entry, so cost lives in per-leg accounts instead of one total. A real session of mine (89 usage events, token counts verbatim, content stripped):

```
; spendbook trial balance — 89 usage events
; prices: litellm-8447cd3a.json (pinned commit — explicit, versioned input)
Expenses:LLM:Anthropic:ClaudeFable5:CacheRead           5.844290 USD   ; 5,844,290 tok
Expenses:LLM:Anthropic:ClaudeFable5:CacheWrite1h        5.187780 USD   ; 259,389 tok
Expenses:LLM:Anthropic:ClaudeFable5:Input               0.000640 USD   ; 64 tok
Expenses:LLM:Anthropic:ClaudeFable5:Output              3.579350 USD   ; 71,587 tok
Expenses:LLM:Anthropic:ClaudeOpus48:CacheRead           4.234090 USD   ; 8,468,179 tok
Expenses:LLM:Anthropic:ClaudeOpus48:CacheWrite1h        1.683990 USD   ; 168,399 tok
Expenses:LLM:Anthropic:ClaudeOpus48:Input               0.000570 USD   ; 114 tok
Expenses:LLM:Anthropic:ClaudeOpus48:Output              2.904750 USD   ; 116,190 tok
Liabilities:Provider:Anthropic                        -23.435460 USD
sum-check (must be 0)                                   0.000000
```

Your 300-tool bug lands in specific legs (tool definitions inflate the input/cache-write side), so it moves those account lines even while the total is being pushed around by unrelated changes. Leg-level history is what makes "hidden by other changes" hard to repeat.

Disclosure, plainly: this email is promoting a product I'm building — spendbook is mine, in presale validation; the page (https://probe-spendbook.vercel.app) runs Stripe in TEST mode, nobody can actually be charged today. And it's adjacent to Ratel, not competing with it — you reduce the spend, this audits it. Question: after the 300-tool incident, did you add any per-component cost attribution, or is the total still the instrument?

Javen
«OWNER-POSTAL-ADDRESS»

If you'd rather not hear from me about this again, reply "stop" and that's the end of it — no list, no follow-up.

```````

### 5. jfrog-boost — reddit-thread-reply
（在他们公开提问（'Are you using … or just letting the tokens burn?'）的帖子里公开回帖——Reddit 官方文本下比 DM/另发帖更稳的形态；遵守 r/LocalLLaMA 10% 自荐比例（owner 账号非推广号））

```````
# channel: reddit-thread-reply — 在他们的帖子里公开回帖（评论），不是新帖、不是 DM：
# https://old.reddit.com/r/LocalLLaMA/comments/1urugnh/stripping_terminal_noise_from_agent_context_via_a/
# （他们帖内公开求教 "Are you using … or just letting the tokens burn?"——公开回帖=答其公开之问，
#  Reddit 官方文本下比 DM/另发帖更稳的形态；遵守 r/LocalLLaMA 10% 自荐比例，owner 账号非推广号；
#  单发一次，不追帖）

Your closing question — "Are you using something similar, or just letting the tokens burn?" — the cost side of my answer: I couldn't tell which, until the spend was a ledger instead of a total.

I'm building spendbook: it books every usage event from an agent transcript as a balanced double-entry journal entry against a pinned, versioned price table. One of my own real sessions (89 events, token counts verbatim, content stripped):

    ; spendbook trial balance — 89 usage events
    ; prices: LiteLLM table pinned at commit 8447cd3a (explicit, versioned input)
    Expenses:LLM:Anthropic:ClaudeFable5:CacheRead           5.844290 USD   ; 5,844,290 tok
    Expenses:LLM:Anthropic:ClaudeFable5:CacheWrite1h        5.187780 USD   ; 259,389 tok
    Expenses:LLM:Anthropic:ClaudeFable5:Input               0.000640 USD   ; 64 tok
    Expenses:LLM:Anthropic:ClaudeFable5:Output              3.579350 USD   ; 71,587 tok
    Expenses:LLM:Anthropic:ClaudeOpus48:CacheRead           4.234090 USD   ; 8,468,179 tok
    Expenses:LLM:Anthropic:ClaudeOpus48:CacheWrite1h        1.683990 USD   ; 168,399 tok
    Expenses:LLM:Anthropic:ClaudeOpus48:Input               0.000570 USD   ; 114 tok
    Expenses:LLM:Anthropic:ClaudeOpus48:Output              2.904750 USD   ; 116,190 tok
    Liabilities:Provider:Anthropic                        -23.435460 USD
    sum-check (must be 0)                                   0.000000

The "massive, redundant log tokens on every subsequent turn" from your post live in the CacheRead/Input legs — in this session the read side alone is ~14.3M tokens, $10.08, visible as its own account lines instead of buried in one number. Which connects to what you're building: a tool that strips context can state its savings as a before/after ledger diff a customer can recompute from their own transcripts, instead of an aggregate counter.

Disclosure: spendbook is mine and in presale validation — the page (https://probe-spendbook.vercel.app) runs Stripe in TEST mode, nobody can actually be charged today. Genuine question back: does Boost's telemetry keep per-leg (input / cache-read / cache-write / output) attribution internally, or aggregate savings only?

```````

