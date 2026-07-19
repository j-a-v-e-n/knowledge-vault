**这是什么**：纲领 §5.3 的 Pi 执行基座 staging 卡在一个待定事实上：用 pi 跑 Claude 到底还吃不吃你的订阅额度。4 月 4 日 Anthropic 封了第三方 harness（改从预付 "extra usage" 池按 token 扣真钱），但 6 月 15 日官方又暂停了相关变更（原文 "third-party app usage **still** draw from your subscription's usage limits"）——两个一手源今天互相矛盾（全部出处见 repo `ledger/research/2026-07-19-pi-substrate/REPORT.md`）。一次 live probe 能**零花费**定案，但要一次 OAuth 授权 = 动你的凭证（冻结内核 c），所以停在这张卡等你点头。
**需要你做什么**：在下面 decision 行回一个词（探 / 不弄）。回「探」后唯一要你手的一步：在 box 终端跑一次 `pi` 的 /login 选 Claude 账号（约 1 分钟，机器会把逐步命令写进本卡回执）。
**不办会怎样**：不回则 §5.3/§5.4 悬置在「墙状态未知」，机器不装不试、不花一分钱；其余工作照常。

# Pi 基座：批一次免费探测（定案计费墙在不在）

decision: <填 探 / 不弄>

## 回「探」后机器做什么（两种结局都不花钱）

1. `npm install -g --ignore-scripts @earendil-works/pi-coding-agent`（免费，MIT）。
2. 你 /login 后，机器发**一条最小请求**：
   - **400 报错**（"Third-party apps now draw from your extra usage…"，实证 issue #3372 的确定性行为）= 墙在、零扣费 → 机器回来出一张有据的「花钱试点还是正式改道」卡（成本按 R9 calls.jsonl 真遥测推算，不再拍区间）。
   - **正常回答且计入订阅** = 墙不在 → 试点属于自由区预授权，机器直接继续 staging（srt 沙箱整进程包裹、permgate/memguard/wallclock 全套，订阅内零边际成本），做完给报告。

## 为什么是这张卡而不是直接让你二选一

上一版卡把「墙在」当既定事实让你在花钱/改道里选；独立评审当天重查抓出 6-15 官方暂停声明与之冲突（政策 5-6 月已翻转两次）。先探再选——不拿没定案的事实请你拍板。

> 备注（不需要你）：pi 07-17 刚合入 llama.cpp router，本地模型可零费用先验证基座替换机制本身；box 硬件承载力机器自行实测，属自由区。
