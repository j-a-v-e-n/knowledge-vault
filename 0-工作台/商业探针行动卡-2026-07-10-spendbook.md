> 归宿：审批请求——看文案，去同目录《商业探针发布审批-*》回一个词（发/edit/跳过）。发布确认或跳过后机器自动清进 done/（原件在 innovation/commercial/runs/ 留档）
**需要你做什么**：看完本卡后在 [[商业探针发布审批-spendbook]] 的 decision: 行回一个词（发 / edit: 怎么改 / 跳过）；手动渠道发完在 [[商业探针回执-spendbook]] 填 posted_date。

# 商业探针行动卡（审批请求）— spendbook（2026-07-10）

**探针页已上线（验收通过：GET 200 / POST 303→Stripe）**：https://probe-spendbook.vercel.app
**Offer**：spendbook — $19.00。Turn your agent's JSONL transcripts into an audit-grade cost ledger: versioned price table, hard-fail on missing prices, daily reconciliation against your provider's own Cost API — never a silent guess.

## 待批文案（批准后逐字发出，≤1 卡待批）

### 帖子 1 → **Hacker News (Ask HN / regular submission)**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：Ask HN: How do you catch cost bugs hiding in your agent's token spend?

```
I run agents in production and the only signal I have on whether something's off is the inference-cost number my logging spits out. That number is just tokens times a price table, so when a bug adds redundant tool-calls or reloads a huge context every turn, the extra cost looks like normal noise — I've had a ~300-tool loading bug sit hidden in cost noise for weeks before I noticed.

I've started building spendbook: it reads the same JSONL transcripts tools like ccusage already read, but instead of just estimating a number, it keeps a double-entry ledger — every usage event posts once, a model missing from the price table fails the run instead of quietly costing zero, and the daily total has to reconcile against Anthropic/OpenAI's own Cost API before I trust it.

I don't know yet if this is worth paying for over just using ccusage for free, so I'm running a two-week presale to find out honestly — no charge today, just gauging real interest: https://probe-spendbook.vercel.app

Curious how others here reconcile agent cost against actual provider bills, or if you've hit the same silent-failure problem.
```

### 帖子 2 → **r/LocalLLaMA**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：Built a tool that double-entry-reconciles agent token costs against provider billing (presale, feedback wanted)

```
Cost tracking for local/self-hosted agent harnesses always comes down to the same thing: you keep paying for every redundant log token on every turn, and you trust a hand-rolled tokens-times-price estimate to tell you when something's wrong. I wanted something stricter, so I built spendbook.

It reads the same agent JSONL transcripts ccusage reads, but instead of just estimating a cost number, it posts every usage event once into a double-entry ledger, hard-fails on any model missing from the price table instead of silently recording zero, and reconciles the daily ledger total against Anthropic/OpenAI's own Cost API. Output is a plain ledger-cli/beancount-compatible file, so you get 40 years of accounting tooling for free instead of a locked-in dashboard.

This is a two-week presale to see if this is worth building past a weekend project — Stripe is in test mode, you won't be charged today, I just want to know if the interest is real: https://probe-spendbook.vercel.app

Happy to hear if ccusage already covers what you need, or where this kind of reconciliation would actually matter to your setup.
```

## 怎么批

打开同目录《商业探针发布审批-spendbook.md》，在 decision: 后回一个词：
**发**（照发）/ **edit: 怎么改**（改完重出卡再等你的发）/ **跳过**（本周不发）。

## 什么算信号（预注册，从真实发布时刻起 14 天）

- 主指标：≥ 5 次"点进 checkout"（每周一自动报告；监控流量已剔除）
- 自动渠道回执机器自记；手动渠道发完填 `商业探针回执-spendbook.md` 的 posted_date
- 不批也行——deploy+14 天自动记 not-run（不算负例）
