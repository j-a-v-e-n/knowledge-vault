**这是什么**：商业探针 wipebreaker 的待批发布文案——探针页已上线，这里是准备发到各社区的最终帖子。
**需要你做什么**：看完本卡后在 [[【商业探针｜发布审批】回一个词-wipebreaker]] 的 decision: 行回一个词（发 / edit: 怎么改 / 跳过）；手动渠道发完在 [[【商业探针｜手发回执】发完填日期-wipebreaker]] 填 posted_date。
**不办会怎样**：不批就不发布，deploy+窗口天数到期自动记 not-run（不算负例）。办结后机器自动清进 done/（原件在 innovation/commercial/runs/ 留档）。

# 商业探针行动卡（审批请求）— wipebreaker（2026-07-29）

**探针页已上线（验收通过：GET 200 / POST 303→Stripe）**：https://probe-wipebreaker.vercel.app
**Offer**：wipebreaker — $19.00。A single-file circuit breaker for your data-refresh jobs: it diffs old vs. new snapshot against rules.json and refuses the overwrite when the delta looks catastrophic — prevention before the write, not restore after the loss.

## 待批文案（批准后逐字发出，≤1 卡待批）

### 帖子 1 → **Ask HN — reply in https://news.ycombinator.com/item?id=48831580 and https://news.ycombinator.com/item?id=48858552**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：(reply comment, not a Show HN submission — a bare sign-up page isn't eligible for Show HN, so this stays a disclosed reply in the existing thread)

```
This is exactly the gap I'm trying to close. I'm building wipebreaker: a single-file circuit breaker that sits between a fetch and the write, whether the writer is a cron script or an agent. It diffs the old snapshot against the new one against a rules.json you define (max deletion ratio, required columns, that kind of thing) and refuses the overwrite with a nonzero exit code if the delta looks catastrophic — something you can wire into any pipeline or agent's pre-write hook. I haven't built the full thing yet. Right now this is a presale validation page, said plainly as that, not a working tool: https://probe-wipebreaker.vercel.app. If enough people want it I'll build it over the next couple weeks; if not, I'll drop it and say so.
```

### 帖子 2 → **r/selfhosted**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：Building a circuit breaker for silent data-refresh failures — honest presale validation, not a finished tool

```
I keep seeing the same failure shape here: a cron job or refresh script keeps 'succeeding' while quietly wiping or corrupting the data underneath it, and nobody notices until later. I'm working on wipebreaker, a single-file tool meant to sit between a refresh job and the actual write: it diffs old vs. new data against a rules file you set (max deletion ratio, required columns) and blocks the overwrite if the delta looks wrong, instead of you finding out after the fact. To be upfront: this isn't built yet, and this post is a presale validation, not a launch — Stripe is in test mode and nobody gets charged today. Page is here if you want to see the pitch or leave a pre-order: https://probe-wipebreaker.vercel.app. Also disclosing I used AI assistance for parts of the copy and page. Happy to answer questions about the design or the rules format in the comments.
```

## 怎么批

打开同目录《【商业探针｜发布审批】回一个词-wipebreaker.md》，在 decision: 后回一个词：
**发**（照发）/ **edit: 怎么改**（改完重出卡再等你的发）/ **跳过**（本周不发）。

## 什么算信号（预注册，从真实发布时刻起 14 天）

- 主指标：≥ 5 次"点进 checkout"（每周一自动报告；监控流量已剔除）
- 自动渠道回执机器自记；手动渠道发完填 `【商业探针｜手发回执】发完填日期-wipebreaker.md` 的 posted_date
- 不批也行——deploy+14 天自动记 not-run（不算负例）
