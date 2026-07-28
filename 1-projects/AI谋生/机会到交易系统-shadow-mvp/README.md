# 机会到交易系统：声明式 Shadow MVP 候选

这个 root 只是本地、合成输入、无外部副作用的实现候选。它用冻结候选中的 closed JSON IR 解释器，把“第一性原理 lane”、“现实观察 lane”、需求假设、竞争解释和未执行实验草案封装成可复算记录。

首份 fixture 模拟显性抱怨，第二份 fixture 模拟用户提到的“未主动要求网站的小餐馆”潜在需求场景。它们都是人工构造的反例/契约测试，没有检查任何真实企业，不是市场样本，也不是需求、客户、价格或收入证据。

程序能做的事是：从预先打开、核验并 unlink 的只读 descriptor 消费 canonical JSON；在 runner-owned 临时 CAS 中做 content-addressed round trip；生成绑定输入哈希的规范化输出；运行当前主机的 fail-closed sandbox probes。

程序不能做的事是：上网、抓取、登录、读取项目外文件、触达任何人、部署、报价、签约、收付款、生成 production Harness 或授予任何现实行动权限。

本 root 的 manifest 首次通过 aggregate Gate 时，状态也只能是 `PRESENT_SNAPSHOT_OBSERVED_UNREVIEWED`。只有另一位独立 reviewer 对 exact shadow manifest、policy、runner、snapshot ledger、SBOM、能力/运行报告和输出做绑定审查，再由 caller 提供 exact receipt hash，才能得到限定的 local declarative candidate acceptance。
