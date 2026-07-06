> 归宿：发布后 → 本文件移回 1-projects/digest搭建记/（或直接删，原稿留档在那）

# 我让 AI 用 33 分钟给我搭了个私人情报员

## 为什么想要这个东西

起点不是"信息刷不过来"，而是我对 AI 的一个观察：**AI 的能力很强，缺的是主动性**。人会主动给自己找方向、给事情赋予价值；AI 不会，它在等指令。

但我不认同"AI 没有创造力"这个流行说法。把"创新"拆开看，绝大多数创新根本不是无中生有，而是**组合**：把已知的东西跨领域搭在一起。我见过一个团队在大模型上的突破，拆开看就是把另一个领域的现成概念搬过来用，效果非常好——两样东西都是已知的，新的只是这个搭配本身。而组合式创新，恰恰是 AI 的天然强项：人一辈子只能专精一两个领域，读一篇论文要一个小时；AI 几分钟就能横扫多个领域的前沿，总结得还比人清楚。零件库的广度和装配的速度都碾压人类——它缺的只是"往哪个方向组合"的输入。

所以这个工具的真实用途，是**给 AI 喂方向**：把这个领域里我最认的几个人——他们的判断往往就代表着领域未来的走向——变成一份每周自动生成的输入。周报名义上是给我看的，但给我看只是锦上添花；我真正想要的闭环在 AI 那头：让它拿这些前沿信号当灵感源，去主动组合出新的点子。这是第一根管子。

## 活是怎么分的

我自己真正动手的时间，前后加起来大概半小时：和 AI 把需求聊清楚、发出一份 brief（原文见文末）、看完它的方案回一句「装上，默认都按你的来」、外加提了三条验收标准。从发出 brief 到定时任务在真实环境验证通过，时间戳相隔 **33 分钟**——其余时间都是 AI 在跑，我该干嘛干嘛。

它先开了三个并行调研 agent，外加一个专门唱反调的红队，把 15 个以上的开源 RSS 摘要项目筛了一遍，结论是：没有现成项目能同时满足「固定源、7 天窗口、中文摘要、输出单个本地 Markdown、不装服务器不开 Docker」。最接近的一个本身就是段两百行的小脚本，还把 LLM 环节留白了。于是自建：239 行 Python（用 uv 内联声明依赖，连 venv 都不用建）+ 73 行配置 + 39 行 launchd plist，加上 README 总共 406 行，一次 commit。每个 RSS 地址都被真实抓取验证过——它顺手发现 Karpathy 的博客只封 curl 的 User-Agent、Eugene Yan 的 `/rss.xml` 是 404 得用 `/rss/`。

## 出岔子的地方，以及怎么被抓住的

三件事，都挺真实：

**一、批准环节超时了。** AI 出完计划弹了三个问题等我确认（是否批准、周报几点生成、Simon Willison 的 feed 用高信噪比档还是全量档），我人不在，60 秒后超时。它按推荐默认先跑了一次 dry-run，我回来时一份从真实内容生成的周报已经躺在那了，看完一句话补了批准。

**二、launchd 是个著名的坑，这次是被验收逼出来的确定性。** launchd 的运行环境几乎没有 PATH，也不一定继承你终端里的登录态——而我的 claude CLI 是订阅 OAuth 登录，这台机器上没有任何 API key，摘要那步在 launchd 下能不能跑通，不试没人敢打包票。所以我的验收标准里专门写了一条：必须用 `launchctl kickstart` 从 launchd 环境真实触发一次完整运行，不许拿手动跑脚本充数；跑不通就如实报告。结果因为计划阶段就预判了这个坑——PATH 和绝对路径直接写死进 plist——第一次触发就通了。但「通了」是验证出来的，不是假设出来的，这两者的区别就是我提验收标准的全部意义。

**三、Karpathy 的 YouTube feed 两次抓取都是 404。** 脚本设计成单个源失败不中断整体运行，失败清单直接打印在周报底部，所以这个 404 明晃晃躺在第一期周报里等我处理，而不是静默烂掉。

## 每周一早上我收到什么

launchd 每周一 08:30 触发：抓 13 个 feed（7 个人 + 两家实验室新闻 + smol.ai 的 AI News 日报），把近 7 天的新内容喂给 `claude -p` 生成中文摘要，按人分节、每条带原文链接、没动静的人明确标「本周无更新」，最后写进 Obsidian vault 的 inbox。第一期：34 条新内容，一份 17KB 的 Markdown，摘要生成花了两分多钟，走订阅额度，没花一分 API 钱。

**已知盲区（没绕、没 hack）：** 所有人的 X/Twitter 都不覆盖——X 没有免费 API，而 Karpathy 和 Pieter Levels 的主要输出恰恰在 X 上，这是最大的洞，README 里白纸黑字写着。两家的 API changelog 也没官方 RSS（第三方做的 RSS 要 $50/年，没买）。Anthropic News 用的是志愿者维护的非官方镜像，断更了周报底部会显示出来。

## 给想抄作业的人

我发给 AI 的 brief 原文（英文，照贴）：

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

回头看，这份 brief 里最值钱的是三处：**约束里写了「不许 hack、盲区写进 README」**，所以 AI 老老实实告诉我 X 覆盖不了，而不是拿个半残方案糊弄；**要求先调研复用、别上来就写码**，所以那 406 行代码是筛完一圈开源项目后的结论，不是默认选项；**「完成」被定义成可验证的证据**（dry-run 出真实内容 + launchctl 可查），后来我又加码到「必须从 launchd 环境真实触发」。宏观决策我做，微观执行全交出去——这个分工能成立，前提是验收标准足够硬。

## 第一周

第一份周报出现在 inbox 里的那个早上，我的真实感受是：成了，但没多兴奋。因为我要的闭环不在我这头——我读周报只是顺带，什么时候这些前沿信号真的激发出 AI 自己组合出来的点子，那个闭环才算合上。这是我公开记录这条路的第一周，工具才跑了一期，下一步是把这根管子接进我另一套自动化系统里。能不能成，过几个周一再说。
