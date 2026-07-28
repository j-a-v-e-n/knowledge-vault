# 研究闭合谓词矩阵

- 状态：`RC-01–RC-23 LEAD-CANDIDATE-PASS / RC-24 INDEPENDENT-EXACT-PASS / RC-25 C4-FAIL-REMEDIATED-PENDING-C5-EXACT-REVIEW / RC-26 PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- 评估对象：当前 C5 总体设计研究候选是否满足 `RESEARCH_PROTOCOL.md` 的闭合条件
- 当前权威状态：`BLOCKED`；本矩阵是 lead 的候选判定，不能自行签发 `CONDITIONALLY_READY`

## 证据身份

| Evidence ID | 路径 | SHA-256 | 权限 |
|---|---|---|---|
| `E-PROTOCOL` | `RESEARCH_PROTOCOL.md` | `b2660101e82f0d606f45578d909734f4d6e56cc3734dd8d985a57da2cd65cadd` | 当前闭合协议候选 |
| `E-INTERVIEW` | `01-黄仁勋访谈核查.md` | `8fca0d1a8720f62389b3f6e99a1995d71a81ebdffa538f213e5409c1d35bbea7` | 访谈种子核查；非理论地基 |
| `E-CLAIMS` | `02-主张与证据地图.md` | `2c11e00e61611a8d0b463cf9b73ca665388fb9cc8f2b29d7d1202e757c2aba4d` | 当前 Claim/RQ/DD 候选 |
| `E-DESIGN` | `03-机会到交易系统-总体设计.md` | `44ca184a62fb2bf04210e290e2cadcc635b95b30a6d21ff9523081c50ade932d` | 当前总体设计候选 |
| `E-LOG` | `04-来源与检索日志.md` | `a6b6da35b7769739057db4730ccdec312d525a8d0a82aa81bf9ef59bee010d91` | 当前来源宇宙、检索与缺口记录 |
| `E-SSP` | `SEARCH_SATURATION_PROTOCOL.md` | `911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1` | frozen SSP-1.0 |
| `E-RUN2-FINAL` | `ssp-run2/FINAL_RUN_STATUS.md` | `35ffc2e34ca69a491cc5cabe25dc55b7fbf58edde67539fe1257ab23d736d30f` | lead exact final-status object |
| `E-CROSSWALK-HUMAN` | `RUN2_CLAIM_EVIDENCE_CROSSWALK.md` | `c035a55ff1ae5572f81c36a4a1e2b5d349439d4e560837a90e6a17c7a61cee6e` | 当前直接使用的 CE→Claim/RQ/DD bridge |
| `E-CROSSWALK-JSONL` | `RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl` | `1e055c08a8aaf18173a8eaab670747879abb57e8cc96dcf69edc56518342f23b` | 全部最终 CE-IN 的 canonical exhaustive ledger |
| `E-CROSSWALK-VERIFIER` | `verify_run2_crosswalk.py` | `2094a655b174c7cd1793790b22fb0024d5b84479ce49e42a38d60b2327bb3655` | 从 sealed inputs 复算 exhaustive ledger |
| `E-CROSSWALK-TEST` | `test_run2_crosswalk.py` | `1fdfa58d6ec3382b7d86e512f5a0001a5d5d38893f667f2d51295d59b35c8e12` | crosswalk 正向/负向回归 |
| `E-RUN2-ACCEPT` | `ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json` | `be30f6967b5872749403eef2af2c1e0cc25f99828c7ceb01aa0b744692b8a788` | exact final-status independent ACCEPT；只限 SSP 状态 |
| `E-RUN2-ACCEPT-VERIFIER` | `verify_run2_acceptance.py` | `4132c72773c2fd4506f92030e2471692fb57d543d1180ebc9e42957fc21e4ed7` | exact path/hash、边界与 authority verifier |
| `E-RUN2-ACCEPT-TEST` | `test_run2_acceptance.py` | `7668842912daf97ce65629220de5aab8224fed5c22ecb98262ce74fca898d1e4` | receipt/artifact/scope/authority 负向回归 |
| `E-ENVELOPE` | `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` | `c5e0e8d37a7801cc719a90db688f5bb8846b2780105719341ed1048fb90b250c` | 条件式只读实现范围；当前不生效 |
| `E-LEGACY-QUARANTINE` | `../../EXTERNAL_LEGACY_QUARANTINE.md` | `c7689fffcc6feceafe489d5b13f47d4b0b943dedb45a6bce1657bc7582a2ecd3` | 外部可变旧根隔离边界 |
| `E-LEGACY-STATUS` | `../../LEGACY_STATUS.md` | `332798fd0c6fb7c55d4a7e4f518dce03ca7f78c8a4f06bd8689fb13712710328` | 旧 runtime/Pilot 权限状态 |
| `E-LEGACY-AUDIT` | `../../LEGACY_CODE_GAP_AUDIT.md` | `4dedeaef09f5e9e735d43020c8d5e46c7fca8b8c6b4c271fef70761fab122e9f` | 旧实现差距与禁止复用边界 |
| `E-REVIEW-HISTORY` | `FINAL_REVIEW_HISTORY.md` | `a321ceefd591977dbe6848679cecf84c54043c4a442b67a2be48716cd4845d96` | C1–C4 拒绝、Run2 acceptance 与 C5 根因修复 |
| `E-CANDIDATE-VERIFIER` | `verify_candidate_manifest.py` | `a2d4e3b3b97a4dec14dc8c4488346f5694bb07c5be6101513d0474cbc579b2e4` | closed candidate inventory、phase 与 Run2 receipt aggregate check |
| `E-POST-VERIFIER` | `verify_post_closure_manifest.py` | `6264ab27053f9f176681fb5a46256448e5841d9ca745fa61f077f01693f53a81` | sibling governance/shadow 完整 inventory verifier；receipt 必须显式 deny external authority |
| `E-PHASE-TEST` | `test_phase_manifests.py` | `83c012b50a4a76f97415bf34e7b04a3e0b9a204d446c44153fd8f888a508210b` | producer→consumer、candidate/governance/shadow phase-boundary 回归 |
| `E-MANIFEST-BUILDER` | `build_candidate_manifest.py` | `ae71ec97683c6cb6e0431b163d9d3bfbffe4a652736db94341c1a28ced3005c9` | 显式闭集 manifest builder；不自动吸收未知文件 |
| `E-FREEZE-BUILDER` | `build_freeze_report.py` | `e84d1a3cf93386eda7bbbc514dd5234af861ae8e619425f50c6c149e3ebfc4f1` | 与 aggregate Gate 共用 exact key set 的外部 freeze-report producer |

任一上列文件的字节变化都会使对应行回到 `STALE`，直到重新计算 hash 并重新审查。`E-RUN2-ACCEPT` 的 reviewer 未撰写或修改 C4/Run2 remediation，但曾审查 C3 并报告相同缺口，所以独立于 authorship、不是 blind；该 receipt 只绑定未变化的 Run2 package，不批准 C5。C5 最终 reviewer 必须检查原件和 C4 interface remediation，不能把验证器通过当作独立性证明。

## 谓词判定

| ID | 冻结闭合谓词 | 当前判定 | Evidence | 检查与残余限制 |
|---|---|---|---|---|
| `RC-01` | 每个 RQ 有主来源与 scope | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-LOG` | 映射可查；来源覆盖不等于具体市场外部效度，待 RC-26 独立复核 |
| `RC-02` | 核心主张同时有支持与反证/边界 | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK-HUMAN,E-CROSSWALK-JSONL` | exhaustive ledger 防止只展示有利 CE-IN；证据强度与 scope 仍逐来源受限 |
| `RC-03` | 搜索与来源日志可复查 | `LEAD-CANDIDATE-PASS` | `E-LOG,E-SSP,E-RUN2-FINAL,E-RUN2-ACCEPT` | Run2 可复查；早期检索仍只作历史索引 |
| `RC-04` | Claim-evidence 映射无循环引用 | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK-HUMAN,E-CROSSWALK-JSONL,E-CROSSWALK-VERIFIER` | unused CE 不能自晋级；未来新增 Claim 必须重新查图闭包 |
| `RC-05` | 每个 RQ 有 Claim→Evidence→Scope→Counterevidence→DD→Unknown | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-CROSSWALK-HUMAN,E-CROSSWALK-JSONL` | 真实交易 unknown 被保留，不被搜索结果填造 |
| `RC-06` | 当前能力与未来设想分开 | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-DESIGN` | 模型、工具和价格会漂移，必须按模块重新评测 |
| `RC-07` | 竞争架构同口径评测，未测值标 unknown | `LEAD-CANDIDATE-PASS-AS-SPECIFICATION` | `E-DESIGN` | 没有架构在本项目上的真实成功率、成本或延迟数据 |
| `RC-08` | 外部动作权限与最小人工节点明确 | `LEAD-CANDIDATE-PASS` | `E-DESIGN,E-ENVELOPE` | 首版 Envelope 不装载外部动作能力，当前 Envelope 尚未生效 |
| `RC-09` | 双通道有隔离、sealed outputs、污染与新 epoch | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | 实现隔离仍须 shadow tests 证明 |
| `RC-10` | SamplingPlan、acquisition lineage、负样本和 discovery/confirmatory 分离 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | 尚无第一批真实观察的采样框 |
| `RC-11` | 生命周期与 blocker 正交，交易/义务逐实体建模 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 没有真实多客户/订单时间序列 |
| `RC-12` | BuyerValue、渠道、采购与价值捕获独立记录/Gate | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 具体买家、渠道、采购和竞争未知 |
| `RC-13` | Seller identity/trust 与 exact-offer delivery feasibility | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 没有任何 exact offer 或现实 seller context |
| `RC-14` | Customer value realization 与付款/留存/收入分离 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 客户结果指标和成熟窗须逐项目冻结 |
| `RC-15` | ActionEnvelope、资源原子性、部分执行与授权 exact binding | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | shadow MVP 不实现现实 Grant/token/executor |
| `RC-16` | 人工监督 readiness、容量、独立性与对照评测 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-CLAIMS,E-DESIGN` | 本系统监督效果和审查容量未实测 |
| `RC-17` | qualification、独立签发、Grant 链与 GovernanceRootPolicy | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 首版 shadow 不签发现实自治权限 |
| `RC-18` | Rights BOM、right-to-sell、assurance closure 与失效传播 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE,E-LEGACY-AUDIT` | 具体资产、平台与司法辖区权利未知 |
| `RC-19` | 经济单位、价格瀑布、现金/义务/已赚收入与 sustainable income | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-CLAIMS` | 没有真实价格、成本、合同或现金流 |
| `RC-20` | ExperimentFamily、完整候选宇宙、累计预算与 kill/re-entry | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 组合上限和统计方法须由未来项目冻结 |
| `RC-21` | DecisionExposure 与无识别不发布因果规则 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 尚无随机或可信准实验 |
| `RC-22` | Outcome maturity、右删失、OwnerObjective 与 income sufficiency | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 用户收入目标、风险窗与现实 cohort 未冻结 |
| `RC-23` | 残余未知与变化监控明确 | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-DESIGN,E-LOG` | 未知只能由 shadow 或经授权现实证据消除 |
| `RC-24` | 冻结两轮逐结果筛选，无 NEW-CRITICAL/UNRESOLVED，完成 joint 与最终状态共同同意 | `INDEPENDENT-EXACT-PASS` | `E-SSP,E-RUN2-FINAL,E-CROSSWALK-JSONL,E-CROSSWALK-VERIFIER,E-CROSSWALK-TEST,E-RUN2-ACCEPT,E-RUN2-ACCEPT-VERIFIER,E-RUN2-ACCEPT-TEST` | exact reviewer ACCEPT 只证明协议内类别代码本未扩展；不证明来源正确、研究穷尽、商机或总体 C5 |
| `RC-25` | immutable candidate 与 governance/shadow 后闭合工件的 inventory/失效边界无自引用 | `C4-FAIL-REMEDIATED / C5-EXACT-REVIEW-PENDING` | `E-ENVELOPE,E-LEGACY-QUARANTINE,E-REVIEW-HISTORY,E-CANDIDATE-VERIFIER,E-POST-VERIFIER,E-PHASE-TEST,E-MANIFEST-BUILDER,E-FREEZE-BUILDER` | C4 的 report schema/path 与 receipt authority 两项 Major 已进入同一 producer/consumer contract 和重算 hash 链后的 fail-closed tests；仍须由 C5 exact freeze 与 RC-26 独立挑战确认 |
| `RC-26` | 最终独立复核绑定完整 manifest 与每个 SHA，无承重缺口 | `PENDING` | 待生成 C5 `FINAL_CANDIDATE_MANIFEST.json`、builder-produced external freeze report 与 exact review receipt | 必须由未撰写 C5 的 independent reviewer 检查全部原件；在 PASS 与 governance closure 前权威状态保持 `BLOCKED` |

## 当前结论与停止规则

Lead 在 C5 当前字节中没有登记到仍未处理的承重设计缺口；这只是待挑战的候选判断，不是研究闭合结论。C4 全量审查确认 RC-01–RC-24 的限定语义，但因两个 governance interface Major 拒绝 RC-25/RC-26。C5 已把 exact freeze-report producer、consumer schema、review receipt 权限否定和相邻阶段重算测试统一起来；在新的 canonical JSON、builder-produced freeze report 与 RC-26 PASS 之前仍不能称“设计已通过”。

后续顺序固定为：

1. 用显式闭集 builder 生成不自包含的 canonical `FINAL_CANDIDATE_MANIFEST.json`；
2. 运行 crosswalk、Run2 acceptance、phase-boundary 全部验证与测试，并用 `build_freeze_report.py` 在 candidate/post-closure roots 外生成 exact-schema freeze report；
3. 由未撰写 C5 的 independent reviewer 绑定 manifest exact hash、freeze report、全部文件、依赖、语义、权限边界和 residual unknown，给出 PASS/FAIL；
4. 只有无 unresolved critical/major 的 PASS 后，才能在预声明 governance sibling root 写入 freeze report、review receipt 与外部 `RESEARCH_CLOSURE_DECISION`，再由 governance manifest 和 aggregate Gate 闭合；
5. 只有 aggregate Gate 通过，才可创建另一个 sibling root，开始 `external_action_authority=false` 的本地、合成 fixture、零外部副作用 shadow MVP。

任一 candidate 字节变化都会使 manifest、RC-26、后续 receipt、decision 和 downstream roots 失效；governance 变化使 shadow root 失效；shadow 变化只使相应 implementation/Eval 失效。

即使 RC-26 未来通过，也不能声称存在具体商机、需求已验证、价格可接受、能够交付、可以盈利、可以完全自治或获得任何现实商业动作权限。
