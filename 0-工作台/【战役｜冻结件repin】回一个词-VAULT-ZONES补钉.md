**需要你做什么**：回一个词——`decision: repin`（认可补钉）或 `decision: 否`（我回滚 R16-R20 对该文件的全部改动）。

# VAULT-ZONES.md 冻结件 sha 补钉（一句话卡）

**这是什么**：`doctrine/check.py` 抓到 `campaign/VAULT-ZONES.md`（D-050 file-pin）的 sha 与台账钉的不一致。查透后是**两个 clone 并行演化的时序错位，不是篡改**：07-19 凌晨 02:30 台账会话在 Mac 侧按当时看到的 07-12 R5 版钉了 sha；同一天本 box 战役 R16→R20 四轮陆续给该文件追加了写监狱/exfil 收敛/预筛读面的补焊记录与诚实边界更新。

**为什么可以放心 repin（证据，可核；含如实瑕疵）**：
- **机器真相源没动**：D-050 写明机器单一真相源 = `campaign/vault_zones.json`，它的 sha 与 pin **完全一致**（分区枚举、默认拒绝一字未变）。漂的只是人读证据文件 `VAULT-ZONES.md`。
- **无一扩权**：diff（e5dca11→现工作树）实质全为 §3 新增焊点（bubblewrap 写监狱、gh token 罩死、host-side git、预筛五件）+ §5 诚实边界更新。D-050 逐字核心（私人区永不写、默认拒绝、扩写权=治理边界）**原文未动**（独立评审用 substring 核过）。
- **如实瑕疵（独立评审 R23 抓出、已修）**：R16 改动曾**误删 §4「未来路径迁移的 lockstep 协议」标题**，正文裸挂 §3 尾部、§2 留悬空引用——R23 已恢复标题并把 §5 条目排回 ④⑤⑥⑦ 序（条目编号未变，历史引用不断）。你 repin 的是修复后的版本。
- **各轮评审终态（逐轮如实，不笼统）**：R16 两评审 FAIL→修→**PASS**（aa023af/819d8ba 附言可查）；R17 **independent PASS**（2021ab4）；R18 两评审 **FAIL→findings 修完，未送第三轮复核**（战役日志 R18 自记，如实）；R20 **double PASS**（6c95144）。
- 出处 commit：969930d / aa023af（R16）、2021ab4（R17）、273ea58（R18）、6c95144（R20）+ R23 本轮修复 commit。

**不办会怎样**：`doctrine/check.py` 会一直报这一个 FAIL（其余 0 FAIL；另有 3 个 WARN 是 Mac 侧路径的 soft-pin 在 box 上缺失，跨机已知、与此无关）；不影响战役运行，但"冻结件校验"这盏灯常亮着就没人再信它（狼来了效应）。你回 `repin` 后机器跑 `doctrine/check.py --repin D-050` 并留档；回 `否` 则回滚文档改动（代码焊点不动，只撤文档记录——不推荐，等于让文档假装焊点不存在）。

decision: <填 repin / 否>

[[战役日志]] · 办完 → 拖进 done/
