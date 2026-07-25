## Review result: Ordinary baseline vs evidence-governed RS-01

### Reviewed

- [R7 preregistration](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:1>)
- [Ordinary baseline](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:1>)
- [RS-01 governed report](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:1>)
- RS-01 SHA-256 已核对，与提供值 `3754a1115bb60b341ae9cc1ac6295f89b4d73a4c0de81dd9c0c29274472f2672` 一致。

## 总体 verdict

**有条件采用治理核心，但不能据此声称治理方法已被同题对照证明优于普通搜索。**

RS-01 在证据可追踪性、去重、反证、条件边界、可复演记录和决策 delta 上明显强于 baseline；baseline 则明显更轻、更直接，并提供了 RS-01 没覆盖的软件交付实践。

决定性限制是：两份报告回答的不是同一个问题。当前比较只能证明“治理报告产生了更丰富的审计痕迹”，不能证明它发现了更多正确事实、产生了更优决定，或值得其额外成本。

### 🔴 Critical

1. **未满足预注册的 same-task comparison。**

   Baseline 的任务是“用 AI 可靠完成长期复杂软件项目”，见 [baseline L1–23](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:1>)；RS-01 的预注册问题是如何让 AI 项目研究达到可核对的领域充分性，见 [prereg L12–17](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:12>)。

   这违反“对一个固定 AI 项目方法问题分别运行”两种方法的要求，[prereg L137–150](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:137>)。RS-01 自己也承认同任务比较尚未执行，[RS-01 L268](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:268>)。

   **影响：**不能把输出差异因果归因于“普通方法 vs 治理方法”。

2. **RS-01 尚未达到其预注册 claim-closure 标准。**

   预注册要求每个决定性 claim 包含 `impact`、`evidence_cluster_ids`、`reviewer_or_deterministic_check` 等字段，[prereg L106–123](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:106>)。RS-01 的 HC-A–HC-I 表缺少逐 claim impact、cluster ID 和 reviewer/check 字段，[RS-01 L184–196](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:184>)；且作者明确承认尚无非作者复核，[L264–265](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:264>)。

   好的一面是报告没有伪造通过，而是正确标为 `bounded_incomplete`。

## 八维比较

| 维度 | Ordinary baseline | RS-01 | 独立判断 |
|---|---|---|---|
| 来源集合完整性 | 只列 Anthropic、OpenAI、DORA，未给查询、排除项或覆盖标准，[L3–7](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:3>) | 列出 exact query/time、O/R/U 类别以及逐结果纳排，[L3–20](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:3>)；但未完成最终跨类别 stability probe，[L258–267](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:258>) | **RS-01 的覆盖可见性更强，但没有证明领域完整。** |
| 上游簇去重 | 没有 cluster 或独立性记录 | 明确把同论文的 VOR、镜像、索引归为同一 cluster 并排除重复，例如 [L100–114](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:100>) | **RS-01 明显胜出。**但 superseded preprint 和同线程 comment 使用不同 cluster ID，[L112](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:112>)、[L182](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:182>)，分类仍有不一致；因均已排除，暂未造成重复支持。 |
| 反证覆盖 | 有环境差异和多年可靠性未知等反面边界，[L42–45](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:42>)，但没有专门反证查询 | 有明确 Q-F，并系统呈现停止方法冲突、领域差异和正反用户经验，[L116–138](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:116>)、[L215–225](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:215>) | **RS-01 胜出于主题反证。**但缺少针对“完整治理流程是否成本过高、轻量流程何时已经足够”的系统反证，因此不能支持成本效益结论。 |
| Claim entailment | Findings 只标来源名称，短引文不能覆盖全部综合建议，[L9–40](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:9>) | 给出范围、状态、限制和 decision effect，[L184–196](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:184>) | **RS-01 结构更强，但未通过。**作者自审、缺字段、缺源内容哈希，且部分 claim 依赖搜索摘要。 |
| 不确定性与条件边界 | 能区分环境差异以及数月案例不能证明多年可靠性，[L42–45](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:42>) | 明确区分 `entailed`、`inference`、`not_entailed`、固定语料与开放 web，并拒绝宣称 domain complete，[L188–196](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:188>)、[L233–254](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:233>) | **RS-01 明显胜出。**这是其最可信的增量之一。 |
| 可复现性 | 只有来源链接，没有查询、时间、版本、完整筛选轨迹 | 保存 query、UTC、URL、类别、cluster、纳排理由和部分 revision 状态 | **RS-01 明显改善，但仍非完整复现。**缺搜索 channel/返回边界、来源快照和哈希；可变论坛内容无法按报告重建，[L264–270](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:264>)。 |
| 决定/架构 delta 清晰度 | 给出实用循环和下一步，但没有相对冻结基线的明确变化，[L23](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:23>)、[L47–49](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:47>) | 明确分为保留、新增、加强、限定和措辞变化，[L227–254](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:227>) | **RS-01 在清晰度上胜出。**但这些 delta 多为设计推论，尚未由同任务实验验证。 |
| 时间和维护负担 | 产物短、维护对象少，但没有记录实际耗时 | 需要逐结果 ledger、cluster、claim review、source hash、stability probe 和非作者 reviewer；报告还要求续轮，[L256–273](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:256>) | **Baseline 在低负担上占优。**两边都没有完整耗时或长期维护记录，无法计算治理收益是否值得成本。 |

## 两份输出共同支持的 claims

- **生成者不应是唯一验收者。**Baseline 明确要求另一轮 AI/代理或人实际验收，[L17](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:17>)；RS-01 要求非构造 reviewer 检查查询、纳排和 entailment，[L250](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:250>)。

- **完成不能由模型自我宣告，必须落到可观察条件。**Baseline 要求可部署、可观察、可回归，[L11–23](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:11>)；RS-01 将 closure 拆成多个 receipt 字段，[L241–248](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:241>)。

- **状态和证据需要移出聊天上下文。**Baseline 主张版本化项目状态，[L15](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:15>)；RS-01 保存查询、筛选和 claim receipts。

- **不能把有限观察外推为长期或领域完整性。**Baseline 拒绝用数月案例证明多年可靠性；RS-01 拒绝把开放 web 搜索写成总体 recall 或 domain complete。

## 各自独有的有效价值

### Baseline 独有

- 纵向功能切分。
- 跨会话状态恢复。
- 测试、日志、指标与调用链成为 AI 可读反馈。
- CI、lint 和结构测试约束架构。
- 面向软件交付的可执行工作循环。

这些内容与 RS-01 的研究治理互补；RS-01 不能替代它们。

### RS-01 独有

- 区分报告完整、领域完整和 bounded decision sufficiency。
- 区分 `finite_frozen_corpus` 与 `open_dynamic_web`。
- upstream cluster 去重及逐结果排除理由。
- explicit counterevidence。
- sentinel retrieval 与 novelty probe。
- 将单一 closure 拆成可复演性、覆盖、残余风险、独立复核和决策充分性。
- 限制匿名 practitioner 证据只能生成 failure probe，不能证明机制或发生率。
- 在门槛未满足时明确输出 `bounded_incomplete`。

其中前几项是有用治理设计；sentinel/novelty、强制复核等仍是待验证的项目设计推论。

### 🟡 Major findings

1. **Baseline 的“可直接采用”措辞过强。**  
   [L23](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/ORDINARY_BASELINE_RAW_AGENT_REPORT.md:23>) 综合出完整循环，但没有逐项 entailment、项目试验或成本证据。它可作为合理候选流程，不能由该报告证明为直接适用。

2. **RS-01 的 HC-G entailment 置信度超过现有 artifact。**  
   [L194](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:194>) 使用搜索返回摘要和受阻全文支撑具体结果，却标为 `entailed_for_studied datasets`。报告自己承认全文受阻且没有内容哈希。应在独立取证前降级为“search-snippet-supported/unverified”。

3. **HC-D 把事实与设计推论合并为一个 `entailed` claim。**  
   “已知材料可检测浅查询”和“只命中已知材料可能是过拟合”是不同命题，[L191](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:191>) 只给一个精确来源位置，却把整个复合命题标成 `entailed`。

4. **“record every result”无法从报告独立核验。**  
   预注册要求逐结果记录 channel、时间、locator、revision 等，[prereg L80–104](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/research/RESEARCH_REFRESH_PREREGISTRATION_R7_2026-07-25.json:80>)。RS-01 没有搜索 channel、结果排名、分页/截断边界或搜索页 receipt，因此无法证明清单确实包含全部返回结果。

5. **“没有证据支持降低门槛”不等于现有全部门槛已获验证。**  
   [RS-01 L231](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:231>) 可以支撑保守地暂时保留门槛，但不能证明这些门槛的组合成本有效。

6. **成本维度缺乏证据。**  
   Query timestamps 只记录检索时点，不覆盖筛选、核验、写作、独立 review 或长期维护。当前无法判断治理收益是否大于成本。

### 🟢 Minor

- RS-01 末尾披露了 memory dependencies，[L275–283](</Users/javencao/Library/CloudStorage/GoogleDrive-jacao@ucsd.edu/My Drive/知识库/MyBrain/projects/investment-discipline-system/audits/research_r7/RS-01_RAW_AGENT_REPORT.md:275>)，但对应内容未冻结在报告中。它们没有被列为 claim 证据，因此不是当前事实错误，但会降低完整复演性。
- Entailment 状态使用多个自定义值；因最终状态是 `bounded_incomplete`，没有造成错误关闭，但不利于自动化 gate 判断。

### ✅ 检查通过

- RS-01 没有把搜索数量冒充领域完整性。
- 同一上游的大部分镜像和索引没有被重复计为独立支持。
- 报告主动呈现支持与反证，没有隐藏冲突。
- 医疗、法律和软件工程方法向 AI 项目迁移时，多数位置明确标为 inference。
- 匿名用户经验没有被用于推导准确率或普遍发生率。
- RS-01 正确拒绝关闭本轮，并明确保留 `bounded_incomplete`。
- Baseline 也明确披露环境差异与长期可靠性未知，没有宣称多年有效。
- 在指定文件范围内，没有发现可确证的事实捏造；由于未读取外部来源，无法确认其外部事实全部正确。

## Adoption decision

**建议：将 evidence-governed 方法作为“高影响研究与架构决定”的实验性审计门槛，采用其最小核心；不要把完整 R7 流程宣布为已验证的默认方法。**

适合现在采用的核心是：

- 预先冻结问题和边界；
- exact query/result receipt；
- upstream-cluster 去重；
- 明确反证搜索；
- 原子 claim、限制和 decision effect；
- 不满足门槛时使用 `bounded_incomplete`。

目前不支持的更强结论是：

- 治理方法比普通搜索找到更多正确信息；
- 完整流程的收益高于维护成本；
- sentinel/novelty、独立复核和全部 receipts 应用于每个低影响研究任务；
- RS-01 已达到 closure。

要把“条件采用”升级为“项目默认方法”，仍需用完全相同的问题重跑两种流程，并同时记录事实质量、决策变化和实际维护负担。
