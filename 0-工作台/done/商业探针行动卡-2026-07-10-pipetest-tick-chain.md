> 归宿：审批请求——看文案，去同目录《商业探针发布审批-*》回一个词（发/edit/跳过）。发布确认或跳过后机器自动清进 done/（原件在 innovation/commercial/runs/ 留档）
**需要你做什么**：看完本卡后在 [[商业探针发布审批-pipetest-tick-chain]] 的 decision: 行回一个词（发 / edit: 怎么改 / 跳过）；手动渠道发完在 [[商业探针回执-pipetest-tick-chain]] 填 posted_date。

# 商业探针行动卡（审批请求）— pipetest-tick-chain（2026-07-10）

**探针页已上线（验收通过：GET 200 / POST 303→Stripe）**：https://probe-pipetest-tick-chain.vercel.app
**Offer**：PipeTest CertWatch — $9.00。A hosted, zero-maintenance watcher that tracks certs and uptime across your homelab fleet, with deadlines that adjust as cert lifespans shrink.

## 待批文案（批准后逐字发出，≤1 卡待批）

### 帖子 1 → **r/selfhosted**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：Building a hosted cert/uptime watcher for homelab fleets — presale validation, feedback wanted

```
Cert lifespans are shrinking: 200 days by 2026, maybe 47 by 2029. I don't think most of us have a good way to track that across a whole fleet of self-hosted services without babysitting a spreadsheet or a cron job. I'm testing whether a hosted, zero-maintenance watcher with lifespan-aware deadlines is worth building before I sink more time into it. This is a presale validation page, not a live product — Stripe is in test mode, you will not be charged: https://probe-pipetest-tick-chain.vercel.app. Genuinely curious if this overlaps with what you already do in Uptime Kuma or Healthchecks.io, or if I'm solving a non-problem.
```

### 帖子 2 → **Ask HN**（手动：credentials 未配或该渠道无写 API——批准后此文案原样手贴）

**标题**：Ask HN: Would you pre-order a hosted cert/uptime watcher for a homelab fleet?

```
TLS cert lifespans are heading toward 200 days by 2026 and maybe 47 by 2029, and manual tracking stops scaling once you have more than a couple of self-hosted services. I'm testing whether a hosted, zero-maintenance watcher with lifespan-aware deadlines is worth building. This link is a presale validation page — Stripe is in test mode, no charge today: https://probe-pipetest-tick-chain.vercel.app. Curious whether people running homelabs actually feel this pain, or already have it solved with Uptime Kuma / Healthchecks.io.
```

## 怎么批

打开同目录《商业探针发布审批-pipetest-tick-chain.md》，在 decision: 后回一个词：
**发**（照发）/ **edit: 怎么改**（改完重出卡再等你的发）/ **跳过**（本周不发）。

## 什么算信号（预注册，从真实发布时刻起 14 天）

- 主指标：≥ 5 次"点进 checkout"（每周一自动报告；监控流量已剔除）
- 自动渠道回执机器自记；手动渠道发完填 `商业探针回执-pipetest-tick-chain.md` 的 posted_date
- 不批也行——deploy+14 天自动记 not-run（不算负例）
