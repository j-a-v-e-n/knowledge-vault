# 我让 AI 半天给我搭了个私人情报员

> 草稿 v1(AI 起草,待我重写)。文末有「待核实清单」,发布前删掉。

## 为什么想要这个东西

我长期关注几个高信号的人:Karpathy、swyx、Simon Willison、Hamel Husain、Eugene Yan、Pieter Levels、宝玉,再加上 Anthropic 和 OpenAI 的官方博客。以前的做法是想起来就去刷,结果要么漏掉,要么被时间线上的噪音带跑。【待核实 ①】我想要的东西其实很具体:固定名单,每周一早上一份中文周报,自动出现在我 Obsidian 笔记的 inbox 里,之后零维护。

## 活是怎么分的

我做的事加起来不超过十分钟:写了一份需求 brief(原文见文末),等 AI 出完计划后回了一句「装上,默认都按你的来」,外加提了三条验收标准。剩下全是 Claude Code 干的——

它先开了三个并行调研 agent,外加一个专门唱反调的红队,把 15 个以上的开源 RSS 摘要项目筛了一遍,结论是:没有现成项目能同时满足「固定源、7 天窗口、中文摘要、输出单个本地 Markdown、不装服务器不开 Docker」。最接近的一个本身就是段两百行的小脚本,还把 LLM 环节留白了。于是自建:239 行 Python(用 uv 内联声明依赖,连 venv 都不用建)+ 73 行配置 + 39 行 launchd plist,加上 README 总共 406 行,一次 commit。每个 RSS 地址都被真实抓取验证过——它顺手发现 Karpathy 的博客只封 curl 的 User-Agent、Eugene Yan 的 `/rss.xml` 是 404 得用 `/rss/`。

## 出岔子的地方,以及怎么被抓住的

三件事,都挺真实:

**一、批准环节超时了。** AI 出完计划弹了三个问题等我确认(是否批准、周报几点生成、Simon Willison 的 feed 用高信噪比档还是全量档),我人不在,60 秒后超时。它按推荐默认先跑了一次 dry-run,我回来时一份从真实内容生成的周报已经躺在那了,看完一句话补了批准。【待核实 ②】

**二、launchd 是个著名的坑,这次是被验收逼出来的确定性。** launchd 的运行环境几乎没有 PATH,也不一定继承你终端里的登录态——而我的 claude CLI 是订阅 OAuth 登录,这台机器上没有任何 API key,摘要那步在 launchd 下能不能跑通,不试没人敢打包票。所以我的验收标准里专门写了一条:必须用 `launchctl kickstart` 从 launchd 环境真实触发一次完整运行,不许拿手动跑脚本充数;跑不通就如实报告。结果因为计划阶段就预判了这个坑——PATH 和绝对路径直接写死进 plist——第一次触发就通了。但「通了」是验证出来的,不是假设出来的,这两者的区别就是我提验收标准的全部意义。

**三、Karpathy 的 YouTube feed 两次抓取都是 404。** 脚本设计成单个源失败不中断整体运行,失败清单直接打印在周报底部,所以这个 404 明晃晃躺在第一期周报里等我处理,而不是静默烂掉。【待核实 ③】

## 每周一早上我收到什么

launchd 每周一 08:30 触发:抓 13 个 feed(7 个人 + 两家实验室新闻 + smol.ai 的 AI News 日报),把近 7 天的新内容喂给 `claude -p` 生成中文摘要,按人分节、每条带原文链接、没动静的人明确标「本周无更新」,最后写进 Obsidian vault 的 inbox。第一期:34 条新内容,一份 17KB 的 Markdown,摘要生成花了两分多钟,走订阅额度,没花一分 API 钱。

**已知盲区(没绕、没 hack):** 所有人的 X/Twitter 都不覆盖——X 没有免费 API,而 Karpathy 和 Pieter Levels 的主要输出恰恰在 X 上,这是最大的洞,README 里白纸黑字写着。两家的 API changelog 也没官方 RSS(第三方做的 RSS 要 $50/年,没买)。Anthropic News 用的是志愿者维护的非官方镜像,断更了周报底部会显示出来。

## 给想抄作业的人

我发给 AI 的 brief 原文(英文,照贴):

```
# Task: Personal "high-signal people" digest tool

## Goal & why
Build a small automated tool that tracks a fixed list of people (their blogs/RSS,
X/Twitter, newsletters where accessible), summarizes new content weekly in Chinese,
and delivers it to me. Why: I outsource fast-changing AI trend awareness to a
zero-maintenance pipeline instead of manual browsing.

## People list
Andrej Karpathy, swyx (Latent Space), Simon Willison, Hamel Husain, Eugene Yan,
Pieter Levels, 宝玉 (baoyu.io). Also monitor: Anthropic/OpenAI official blogs +
API changelogs (for lab-roadmap signals).

## Constraints
- Prefer RSS/official feeds over scraping; X/Twitter has no free API — use each
  person's blog/newsletter as the primary source and note in the README which
  sources are not covered rather than hacking around paywalls.
- Fork/reuse existing open-source RSS-digest projects if a good one exists
  (search first); do not build from scratch if avoidable.
- Output: one weekly Markdown digest file into my Obsidian vault inbox folder;
  scheduling via launchd.

## Process
This touches my system (launchd, vault folder), so PLAN FIRST: propose the design
and WAIT for my approval before writing anything.

## Done means
A dry-run digest generated from the last 7 days of real content, shown to me, plus
the launchd job installed and verified with `launchctl list`.
```

回头看,这份 brief 里最值钱的是三处:**约束里写了「不许 hack、盲区写进 README」**,所以 AI 老老实实告诉我 X 覆盖不了,而不是拿个半残方案糊弄;**要求先调研复用、别上来就写码**,所以那 406 行代码是筛完一圈开源项目后的结论,不是默认选项;**「完成」被定义成可验证的证据**(dry-run 出真实内容 + launchctl 可查),后来我又加码到「必须从 launchd 环境真实触发」。宏观决策我做,微观执行全交出去——这个分工能成立,前提是验收标准足够硬。

这是我公开记录学习过程的第一周,这个东西才跑了一期,它到底能不能改变我获取信息的习惯,得等几个周一之后再说。

---

## 待核实清单(发布前删除本节)

1. **【①动机描述】**「想起来就去刷,要么漏掉,要么被噪音带跑」是我替你编的动机,请换成你的真实感受。
2. **【②「答了 3 个问题」的说法】** 你任务里说的是「approved a plan and answered 3 questions」,但会话记录显示:那 3 个问题弹出后 60 秒超时、无人应答,你是事后用一句话「装上,默认都按你的来(周一 08:30、Simon Willison 仅长文)」整体批准的,同一条消息里附了三条验收标准。正文按记录写成了「超时 + 一句话批准」——如果你记忆里确实逐条答过,改回去。
3. **【③YouTube 404】** 日志确认 dry-run 和 launchd 两次运行该 feed 都是 404(`logs/digest.log` 与 `launchd.err.log`)。注意:当时 AI 的完工汇报说 launchd 那次「YouTube 也成功、零失败」,与日志矛盾,草稿以日志为准。这个 feed 的 channel_id 可能有误,值得顺手修一下。
4. **【标题「半天」】** 会话时间戳显示从你发出 brief(7 月 1 日 19:27 PT)到 launchd 验证完成(约 20:00 PT)只有 **33 分钟左右**,含全部调研。「半天」不算吹牛但偏保守——如果你把之前构思需求的时间也算上,按体感定;也可以直接用「33 分钟」这个更狠的真实数字(但要确认你没有更早的相关会话)。
5. **【「加起来不超过十分钟」】** 你实际投入的人工时间是我估的,请核对。
6. **【费用】**「走订阅额度、没花一分 API 钱」——机器上确实无 API key、`claude -p` 走订阅登录,属实;但「一分没花」的表述由你确认口径。
