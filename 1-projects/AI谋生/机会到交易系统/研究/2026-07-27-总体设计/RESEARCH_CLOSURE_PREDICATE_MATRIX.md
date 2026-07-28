# 研究闭合谓词矩阵

- 状态：`RC-01–RC-24 CANDIDATE-PASS / RC-25 PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- 评估对象：当前总体设计研究候选是否满足 `RESEARCH_PROTOCOL.md` 的闭合条件
- 当前权威状态：`BLOCKED`；本矩阵不能自行签发 `CONDITIONALLY_READY`

## 证据身份

| Evidence ID | 路径 | SHA-256 | 权限 |
|---|---|---|---|
| `E-PROTOCOL` | `RESEARCH_PROTOCOL.md` | `fbe404b3d826185236690e900b1ae5076aa19b0880162ca6b80dbbf22fdbefde` | 当前闭合协议候选 |
| `E-INTERVIEW` | `01-黄仁勋访谈核查.md` | `8fca0d1a8720f62389b3f6e99a1995d71a81ebdffa538f213e5409c1d35bbea7` | 访谈种子核查；非理论地基 |
| `E-CLAIMS` | `02-主张与证据地图.md` | `be80b2d24c6820ff29de405a49c08b7cf3809a20a34876b76dd4e859ee526711` | 当前 Claim/RQ/DD 候选 |
| `E-DESIGN` | `03-机会到交易系统-总体设计.md` | `b7604f9032081ccf1624021743654628534835b5fb40fa82785427911c61d55f` | 当前总体设计候选 |
| `E-LOG` | `04-来源与检索日志.md` | `cc08035586b5bf4e66a25c68ab8be9463eec02f38a02d3cc8c0841f5a983bfa0` | 当前来源与检索边界 |
| `E-ARCH-HIST` | `ARCHITECTURE_CHALLENGE_REVIEW.md` | `2900f4608de977e10479ffc5f4ec88d4c11199b6f803eb86d02bcf8f373bb0dc` | 历史 exact-candidate 架构挑战；不替代当前 final review |
| `E-CROSSWALK` | `RUN2_CLAIM_EVIDENCE_CROSSWALK.md` | `2970ee80172c4ef734223d026535e7c8d4cfdc06bb3d19b35caf3464f00232bc` | Run2 CE → Claim/RQ/DD/unknown bridge |
| `E-RUN2` | `ssp-run2/FINAL_RUN_STATUS.md` | `d6f6446a2ab71a478f7eb1cabad836fffc1a817198ad1d738569c5a323dcd84b` | `SATURATED-WITHIN-PROTOCOL`，仅限类别代码本 |
| `E-ENVELOPE` | `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` | `144ab65ca437f55c99f45cf1535dc8931a67f6adedbcfd7dd85843eef19e61a3` | 条件式只读实现范围 |
| `E-LEGACY-STATUS` | `../../LEGACY_STATUS.md` | `a8c89ea188d0acfc032935aa85a9fabaf22ff2ea796848c5ac7b03bb6302dbb4` | 旧 runtime/Pilot 权限隔离 |
| `E-LEGACY-AUDIT` | `../../LEGACY_CODE_GAP_AUDIT.md` | `f285baae9f2544ffa759ef1a1e7709b7c77086d5281df3afb8a02e2891cc5198` | 旧实现差距与 shadow 迁移边界 |

任一上列文件的字节变化都会使对应行回到 `STALE`，直到重新计算 hash 并重新审查。`E-ARCH-HIST` 明确绑定的是更新前候选，只能证明当时的反证修订轨迹；当前候选必须由 RC-25 的 successor review 全量复核。

## 谓词判定

| ID | 冻结闭合谓词 | 候选判定 | Evidence path/hash | Reviewer / 检查 | 残余限制 |
|---|---|---|---|---|---|
| `RC-01` | 每个 RQ 有主来源与 scope | `CANDIDATE-PASS` | `E-CLAIMS,E-LOG` | lead 映射；待 RC-25 独立复核 | 来源覆盖不等于具体市场外部效度 |
| `RC-02` | 核心主张同时有支持与反证/边界 | `CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK` | lead + Run2 joint | 单条 CE-IN 仍受方法、样本与版本限制 |
| `RC-03` | 搜索与来源日志可复查 | `CANDIDATE-PASS` | `E-LOG,E-RUN2` | Run2 lead/independent 机械审查 | 早期检索仍不可复现，只能作历史索引 |
| `RC-04` | Claim-evidence 映射无循环引用 | `CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK` | typed relation 与 CE-OUT 规则；待 RC-25 图审 | 未来新增 Claim 必须重新查闭包 |
| `RC-05` | 每个 RQ 有 Claim→Evidence→Scope→Counterevidence→DD→Unknown | `CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK` | RQ coverage matrix | 真实交易 unknown 被保留而不是填造 |
| `RC-06` | 当前能力与未来设想分开 | `CANDIDATE-PASS` | `E-CLAIMS,E-DESIGN` | current evidence / hypotheses / target state 分型 | 模型、工具和价格会漂移，需未来重新评测 |
| `RC-07` | 竞争架构使用同一评测维度，未测值标 unknown | `CANDIDATE-PASS-AS-SPECIFICATION` | `E-DESIGN` | architecture comparison + eval spec | 任何架构的成功、成本和延迟尚未在本项目实测 |
| `RC-08` | 外部动作权限与最小人工节点明确 | `CANDIDATE-PASS` | `E-DESIGN,E-ENVELOPE` | ActionEnvelope / forbidden capability 审查 | 首版根本不装载外部动作能力 |
| `RC-09` | 双通道有隔离、sealed outputs、污染与新 epoch | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | AR-01/AR-14 历史挑战；RC-25 successor | 实现是否真正隔离必须由 shadow tests 证明 |
| `RC-10` | SamplingPlan、Acquisition lineage、负样本和 discovery/confirmatory 分离 | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | AR-01 与 DD-21 | 尚无第一批真实观察的采样框 |
| `RC-11` | 生命周期与 blocker 正交，交易/义务逐实体建模 | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 状态、记录、转换契约 | 没有真实多客户/订单时间序列 |
| `RC-12` | BuyerValue、渠道、采购与价值捕获独立记录/Gate | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | DD-16/DD-19 + mapping | 具体买家、渠道、采购和竞争未知 |
| `RC-13` | Seller identity/trust 与 exact-offer delivery feasibility | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | AR-03/AR-06/AR-10 | 没有任何 exact offer 或现实 seller context |
| `RC-14` | Customer value realization 与付款/留存/收入分离 | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | AR-02 + DD-22 | 客户结果指标和成熟窗须逐项目冻结 |
| `RC-15` | ActionEnvelope、资源原子性、部分执行与授权 exact binding | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | AR-15 + zero-side-effect envelope | shadow MVP 不实现现实 Grant/token/executor |
| `RC-16` | 人工监督 readiness、容量、独立性与对照评测 | `CANDIDATE-PASS-AS-DESIGN` | `E-CLAIMS,E-DESIGN` | S1 provisional disposition + H-OVERSIGHT-01 | 本系统监督效果和审查容量未实测 |
| `RC-17` | qualification、独立签发、Grant 链与 GovernanceRootPolicy | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | DD-20 + record/gate semantics | 首版 shadow 不签发现实自治权限 |
| `RC-18` | Rights BOM、right-to-sell、assurance closure 与失效传播 | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE,E-LEGACY-AUDIT` | rights/assurance/legacy review | 具体资产和司法辖区权利仍未知 |
| `RC-19` | 经济单位、价格瀑布、现金/义务/已赚收入与 sustainable income | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-CLAIMS` | DD-17/DD-18 + economic records | 没有真实价格、成本、合同或现金流 |
| `RC-20` | ExperimentFamily、完整候选宇宙、累计预算与 kill/re-entry | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | AR-04/AR-08 + DD-24/DD-28 | 组合上限和统计方法须由未来项目冻结 |
| `RC-21` | DecisionExposure 与无识别不发布因果规则 | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | AR-05/AR-11 + DD-25 | 还没有随机或可信准实验 |
| `RC-22` | Outcome maturity、右删失、OwnerObjective 与 income sufficiency | `CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | AR-07/AR-09/AR-12 | 用户收入目标、风险窗与现实 cohort 未冻结 |
| `RC-23` | 残余未知与变化监控明确 | `CANDIDATE-PASS` | `E-CLAIMS,E-DESIGN,E-LOG` | non-claims / unknown sections | 未知只能由 shadow/经授权现实证据消除 |
| `RC-24` | 冻结两轮逐结果筛选，无 NEW-CRITICAL/UNRESOLVED，完成 joint | `PASS` | `E-RUN2,E-CROSSWALK` | S1 joint + S2 exact-hash independent ACCEPT | 只证明协议内类别代码本未扩展 |
| `RC-25` | 最终独立复核绑定完整 manifest 与每个 SHA，无承重缺口 | `PENDING` | 待生成 `FINAL_CANDIDATE_MANIFEST.json` 及外部 receipt | 必须由未撰写当前候选的 independent reviewer 完成 | 在 PASS 前总体权威状态保持 `BLOCKED` |

## 候选结论与停止规则

本矩阵当前没有发现 RC-01—RC-24 的未处理承重设计缺口，但其中多项只是“设计语义完整”，不是现实效果通过。RC-25 是有意保留的外部 Gate，不能由本文作者、旧 architecture review 或 Run2 类别饱和替代。

后续顺序固定为：

1. 冻结包含本矩阵、所有 active closure evidence、旧无效运行排除项和 legacy 隔离项的 canonical manifest；
2. 机械验证每个 path/hash/dependency；
3. independent reviewer 对 manifest exact hash、全部文件和 residual unknown 给出 PASS/FAIL；
4. 只有 PASS 后，外部 `RESEARCH_CLOSURE_DECISION` 才可把精确候选在 `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` 范围内条件式放行；
5. manifest、receipt、closure decision 或其依赖任一变化，状态自动回到 `BLOCKED`。

即使 RC-25 通过，也不能声称存在具体商机、需求已验证、价格可接受、能够交付、可以盈利、可以完全自治或获得任何外部商业动作权限。
