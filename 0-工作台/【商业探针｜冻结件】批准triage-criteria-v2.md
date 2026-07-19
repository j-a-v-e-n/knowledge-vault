**这是什么**：商业探针裁决尺子的 Gen-2 修订提案（criteria v2）——你 07-11 直令 D1/D2/D3 落成可机判的判据。尺子=冻结内核，改动只能等你一词。
**需要你做什么**：在下面 decision: 行回一个词（批 / edit: 哪里改 / 驳）。批 = 机器把 DRAFT 冻结、重钉 sha、triage 从下个 tick 起按 v2 判。
**不办会怎样**：triage 继续按 v1.1 判（想法出生仍市场盲）；v2 码检已在 report-only 试跑、管线代码已建好，批了即刻生效，不批不损失任何已建的东西。

# 冻结件提案 — commercial triage criteria v2

decision: 批

## 改了什么（全文见 repo `innovation/commercial/criteria-v2.DRAFT.md`，其余逐字继承 v1.1）

1. **K4v2 器械选择**（D3）：presale 页不再是唯一器械——{presale-page, demo-kit, both} 选定并论证；机器只造 kit，发送永远你的手。
2. **K5v2 渠道合规硬表**（D3）：渠道母表焊成代码（`outreach.py CHANNEL_POLICY`，28 条官方规则原文引用经独立红队逐字复核）。结构性剔除 Etsy/小红书/闲鱼/Reddit-DM/一切自动化群发；冷邮要 CAN-SPAM 六件套且地址不得来自 GitHub；GitHub 回帖 ≤1 发/repo。
3. **K6 能力滤镜**（D1）：今日模型+现成组件交付 ≥90% 承诺价值、路径具体到组件名，否则 kill（capability-gap）。
4. **K7 战场五问**（D2，查证框架 = Aulet 滩头八准则 + Moore + Hoy/Kahl 水坑测试）：谁/为何是他们/**够得着吗（前置一票否决）**/赢得下吗/赢了通向哪。答不出①③ = kill（no-battlefield）。
5. **demo-kit 预注册 ruler**：14 天窗锚定你手填的 sent 日期，replies/positive_intent 你自报、代码判读（intent ≥2 positive）；≤1 kit 在外。

## 证据与纪律

- 冻结件 criteria.md / checks.py 一字未动（git diff 可验）；v2 判据在新文件+新模块，默认关（config `[criteria_v2] enforced=false`）。
- 首个实例已按 v2 精神造好：spendbook 外联 kit（另一张卡）——你可以拿实物判这把尺子合不合用。
- 出处分级与调研原文：repo `research/outreach-channel-compliance/` + 二代改造方案 §11。

你回词后：战役的下一轮工作者读到即执行（冻结 DRAFT → 重钉 sha → 翻开关），执行记录进战役日志；执行完把本卡移进 done/。本卡族无 30 分钟 watcher，如实说明。

