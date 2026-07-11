**这是什么**：商业探针发布渠道的一次性开通——Reddit 自动发帖凭据 + X 付费渠道拍板。
**需要你做什么**：① 建 Reddit script app 并填 `~/ai-architect/innovation/commercial/state/publish-creds.toml`（约10分钟）；② 拍板 X 按次计费（$0.20/帖）用不用。
**不办会怎样**：凭据不配，每次探针文案都退化成手贴模式（不挡探针，但每次都要你动手）。办完 → 把这张卡拖进 done/（无 watcher，每日自动归档）。

# 商业发布通道设置（v1.1 审批制自动发布已上线）

审批制发布已装好：下次探针上线时，行动卡变成**审批请求**（带各渠道最终文案），你在
《【商业探针｜发布审批】回一个词-*》里回一个词（发 / edit: 怎么改 / 跳过），机器 30 分钟内动作。
**没配好凭据前一切照常**——文案退化为手贴模式，不会卡住任何探针。

## 要你做的（约 10 分钟，Reddit 自动发布的前提）

1. 打开 https://www.reddit.com/prefs/apps → create app → 类型选 **script**，
   redirect uri 随便填 http://localhost:8080。
2. 把 client_id（app 名字下面那串）、client_secret、你的 Reddit 用户名和密码填进
   `~/ai-architect/innovation/commercial/state/publish-creds.toml`（模板已生成，
   该文件被 gitignore，永不入库）。
3. 注意（查证过，三方来源）：2025 底起新 OAuth app 可能要走 Reddit 的审批工单
   （form 在 support 页）；如果 app 建好但 API 401，就是卡在这一步。

## 要你拍板的（花钱）

- **X**：2026-02 起新开发者只有按次计费（带链接的帖子 **$0.20/条**，需开发者账号+预充值）。
  探针一周最多 1-2 条，月成本 <$1，但花钱=你拍板。要开就回一句，我来接（transport 槽位已留）；
  不开则 X 文案永远手贴。
- **Blog**：你还没有 blog；有了以后同样接进来全自动。

## 已自动的（不用你动）

Reddit（凭据填好后）：官方 API、你的账号、单帖、目标 sub 的规则 JSON 每次发布前抓取冻结留证；
triage 阶段已新增 K5——提案的每个社区必须引用其自我推广规则原文并论证合规，否则该渠道被砍。
HN 按你的规格保持手动（无官方写 API），文案在卡里直接复制。
