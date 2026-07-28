# 研究闭合谓词矩阵

- 状态：`RC-01–RC-08/RC-11–RC-17/RC-19–RC-24 CARRY-FORWARD-CANDIDATE-PASS / RC-09/RC-10/RC-18 C7-IMPLEMENTATION-FALSIFIED-C8-REMEDIATION-PENDING / RC-25 PENDING-C8-DOMAIN-GATE-CODE-INTERFACE-REVIEW / RC-26 PENDING-MANIFEST-BOUND-INDEPENDENT-REVIEW`
- 评估对象：当前 C8 successor 总体设计研究候选是否满足 `RESEARCH_PROTOCOL.md` 的闭合条件，并闭合 C7 Shadow 实现已暴露的领域语义缺口
- 当前权威状态：`BLOCKED`；本矩阵是 lead 的候选判定，不能自行签发 `CONDITIONALLY_READY`

## 证据身份

| Evidence ID | 路径 | SHA-256 | 权限 |
|---|---|---|---|
| `E-PROTOCOL` | `RESEARCH_PROTOCOL.md` | `0a1d620ba4d768d2ff0b62263d75207e5eaca79d169b0e060664920361eb265b` | 当前闭合协议候选 |
| `E-INTERVIEW` | `01-黄仁勋访谈核查.md` | `8fca0d1a8720f62389b3f6e99a1995d71a81ebdffa538f213e5409c1d35bbea7` | 访谈种子核查；非理论地基 |
| `E-CLAIMS` | `02-主张与证据地图.md` | `205dbdb6bbcbb6cb87bbae5a5a2e487402bcbe56e33e6d8cbcb760eda5d4152f` | 当前 Claim/RQ/DD 候选 |
| `E-DESIGN` | `03-机会到交易系统-总体设计.md` | `3fadeeafb0b32d59cb5f82604d208d779bfb368c8bf3a93ae8b5cecae857994a` | 当前总体设计候选 |
| `E-LOG` | `04-来源与检索日志.md` | `03c6c85462e9a174583aa90fd3e6f09247f9a4219b528f1428418d32bf2fc00a` | 当前来源宇宙、检索与缺口记录 |
| `E-SSP` | `SEARCH_SATURATION_PROTOCOL.md` | `911b6353b23f180a400865a810b3d45cbfa0ea2598e1127f1e548195ef0c30c1` | frozen SSP-1.0 |
| `E-RUN2-FINAL` | `ssp-run2/FINAL_RUN_STATUS.md` | `5b27030ff9c13a6196ffb81a0e828de3e69ac0ee176651d3fa35fab088e1a6c3` | attempt 2 lead exact final-status object |
| `E-CROSSWALK-HUMAN` | `RUN2_CLAIM_EVIDENCE_CROSSWALK.md` | `8c71e9b5e5b5069259e820db8e1eae490aa21822094ef2e519d815c209ba8a0a` | `23` 条当前 direct bridge 与语义降级记录 |
| `E-CROSSWALK-JSONL` | `RUN2_CLAIM_EVIDENCE_CROSSWALK.jsonl` | `b31b67b255a6f2b797e261199c5ff8196001963e21011b07396e837ab8b0273b` | 全部 final CE-IN 的 canonical exhaustive ledger |
| `E-CROSSWALK-VERIFIER` | `verify_run2_crosswalk.py` | `1c1dafd1f7abfa9ae1ab6c918ccf1b7089c68d9c755c53663fe5a9d823a43ae0` | sealed reconstruction 与冻结 semantic rejection sets |
| `E-CROSSWALK-TEST` | `test_run2_crosswalk.py` | `0b58f975d46d9a17f91881f4362623fdc36716031c603f935a5abfd82e50c99d` | exhaustive、语义拒绝与相邻窄桥回归 |
| `E-RUN2-ACCEPT` | `ssp-run2/FINAL_RUN_STATUS_INDEPENDENT_ACCEPTANCE.json` | `7f473fdf93a3bb70ecb463fb3f48e124ba1d4267de48f3051a5c41950d64155c` | attempt 2 exact final-status independent ACCEPT；只限 SSP 状态 |
| `E-RUN2-ACCEPT-VERIFIER` | `verify_run2_acceptance.py` | `fa40601090c9c454fbdb62b33a62e965f072deda8be330d3387fa0736ad7d6be` | exact path/hash/count、边界与 authority verifier |
| `E-RUN2-ACCEPT-TEST` | `test_run2_acceptance.py` | `1e41bf34e3c51294e27bb9109ed1c6ac5994cfc643becdbf643a01325d8a177d` | receipt/artifact/count/scope/authority 负向回归 |
| `E-ENVELOPE` | `READ_ONLY_SHADOW_ACTION_ENVELOPE.md` | `e74d5fbb0f85655c753e712c5becb2f0990b71db88c7df873fae869503207c99` | 条件式只读实现范围；当前不生效 |
| `E-C6-SANDBOX` | `C6_SANDBOX_PROBE_REPORT.md` | `cd2af770db6881ef48df71e7acb978976309ace97711b18be0c662e35875b42d` | 历史反例、iteration B host-required evidence 与 nonclaims；只作为 C8 的上游 transport/sandbox 输入 |
| `E-C7-SHADOW-FAILURE` | `C7_SHADOW_FAILURE_RECORD.md` | `PENDING-RECOMPUTE-AFTER-C8-BYTES-STABILIZE` | C7 exact Shadow `FAIL / NO-GO` 与 successor 修复边界 |
| `E-C8-DOMAIN-GATE-REVIEW` | `C8_DOMAIN_GATE_REVIEW_REPORT.md` | `PENDING-EXACT-CODE-AND-INTERFACE-REVIEW` | C8 下游 exact-byte 领域 Gate 审查；当前不是 PASS 证据 |
| `E-CAPABILITY-POLICY` | `SHADOW_CAPABILITY_POLICY.json` | `8ca4d90c958ea04adf14d003226a620a4000ad805e439823b5c5cc34a7e7ebb9` | fixed declarative IR/capability/resource policy |
| `E-SHADOW-RUNNER` | `run_shadow_acceptance.py` | `ba5bb3aeb55b14eaa8135c8367ed16295d0782a4f7813b337397998117edbc97` | opened-unlinked interpreter、runtime TCB 与 host Gate |
| `E-SHADOW-TEST` | `test_shadow_acceptance.py` | `a870a2262633b19d40bd892a00c72240d8e8f4c65be436f32573cc8378176eec` | capability/resource/host-required 对抗回归 |
| `E-LEGACY-QUARANTINE` | `../../EXTERNAL_LEGACY_QUARANTINE.md` | `c7689fffcc6feceafe489d5b13f47d4b0b943dedb45a6bce1657bc7582a2ecd3` | 外部可变旧根隔离边界 |
| `E-LEGACY-STATUS` | `../../LEGACY_STATUS.md` | `a760ab781ebcebe3ec09cb154198e1658f69d6ef1c1d7593537921581e45d602` | 旧 runtime/Pilot 权限状态 |
| `E-LEGACY-AUDIT` | `../../LEGACY_CODE_GAP_AUDIT.md` | `4dedeaef09f5e9e735d43020c8d5e46c7fca8b8c6b4c271fef70761fab122e9f` | 旧实现差距与禁止复用边界 |
| `E-REVIEW-HISTORY` | `FINAL_REVIEW_HISTORY.md` | `d66ba239a0123dfd343b84ec95c4585dc42963ebd8256ad8c14a00baf876b6e0` | C1–C6 拒绝、两轮 semantic remediation 与 attempt 2 acceptance |
| `E-CANDIDATE-VERIFIER` | `verify_candidate_manifest.py` | `88c16f8860811215fa4845bdd03c4f15ef4f5fcd2e8cdb85238cd4a77ee3bc69` | closed inventory、exact status/scope 与 Run2 aggregate check |
| `E-POST-VERIFIER` | `verify_post_closure_manifest.py` | `823acd5aba8ac2949312c663acd25bd4c3de203a7c18604d9da066df2f2d45b3` | fixed-policy pre-read limits、snapshot recheck 与 exact shadow receipt bindings |
| `E-PHASE-TEST` | `test_phase_manifests.py` | `13b5f5da3998f72740a752b2bbabdc7621dacc8437f5ca632467cf8443dd3ff8` | producer→consumer、exact candidate status/scope、零漂移、resource 与 phase-boundary 回归 |
| `E-MANIFEST-BUILDER` | `build_candidate_manifest.py` | `41e2c4f2f00ebee53e999eb976b5f596bdf1fcac7567ffe84a6f26901404a0fb` | C7 显式闭集 manifest builder；不自动吸收未知文件 |
| `E-FREEZE-BUILDER` | `build_freeze_report.py` | `7c797767a867e066a62428dcf2c059f14dc4e97c3276dee364669eef5e25b779` | 与 aggregate Gate 共用 exact key set 的外部 freeze-report producer |

任一上列文件的字节变化都会使对应行回到 `STALE`，直到重新计算 hash 并重新审查。当前表中从 C7 复制而来的 exact hashes 只是待重算的历史基线，不得被 C8 freeze 使用；所有当前文件必须在字节稳定后统一重算。`E-RUN2-ACCEPT` 的 reviewer 未撰写或修改 attempt 2，但审过 earlier rejected bytes，所以独立于 authorship/remediation、不是 blind；canonical receipt 是 lead 对本地审查声明的机械物化，不是 reviewer 数字签名或 trusted timestamp。该 receipt 只绑定未变化的 Run2 package，不批准 C8。C8 最终 reviewer 必须检查全部原件、C7 Shadow 拒绝证据、C8 Gate/interface remediation、attempt 1/2 与权限 nonclaims，不能把验证器通过当作独立性证明。

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
| `RC-09` | 双通道有隔离、sealed outputs、污染与新 epoch | `C7-IMPLEMENTATION-FALSIFIED / C8-REMEDIATION-PENDING` | `E-DESIGN,E-ENVELOPE,E-C7-SHADOW-FAILURE,E-C8-DOMAIN-GATE-REVIEW` | C7 反例证明 transport/hash 闭合不等于 lane 语义隔离；C8 须以反例测试和独立代码审查恢复候选判定 |
| `RC-10` | SamplingPlan、acquisition lineage、负样本和 discovery/confirmatory 分离 | `C7-IMPLEMENTATION-FALSIFIED / C8-REMEDIATION-PENDING` | `E-DESIGN,E-ENVELOPE,E-C7-SHADOW-FAILURE,E-C8-DOMAIN-GATE-REVIEW` | C7 接受了未冻结 sampling 的自述；C8 须机械绑定顺序/父 hash 并保留“尚无真实采样框”的 unknown |
| `RC-11` | 生命周期与 blocker 正交，交易/义务逐实体建模 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 没有真实多客户/订单时间序列 |
| `RC-12` | BuyerValue、渠道、采购与价值捕获独立记录/Gate | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 具体买家、渠道、采购和竞争未知 |
| `RC-13` | Seller identity/trust 与 exact-offer delivery feasibility | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 没有任何 exact offer 或现实 seller context |
| `RC-14` | Customer value realization 与付款/留存/收入分离 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 客户结果指标和成熟窗须逐项目冻结 |
| `RC-15` | ActionEnvelope、资源原子性、部分执行与授权 exact binding | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-ENVELOPE` | shadow MVP 不实现现实 Grant/token/executor |
| `RC-16` | 人工监督 readiness、容量、独立性与对照评测 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-CLAIMS,E-DESIGN` | 本系统监督效果和审查容量未实测 |
| `RC-17` | qualification、独立签发、Grant 链与 GovernanceRootPolicy | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 首版 shadow 不签发现实自治权限 |
| `RC-18` | Rights BOM、right-to-sell、assurance closure 与失效传播 | `C7-IMPLEMENTATION-FALSIFIED / C8-REMEDIATION-PENDING` | `E-DESIGN,E-ENVELOPE,E-LEGACY-AUDIT,E-C7-SHADOW-FAILURE,E-C8-DOMAIN-GATE-REVIEW` | C7 可接受 denied/account/external-retrieval 自述；C8 首版只能机械拒绝结构不合格记录，具体资产、平台与司法辖区权利仍未知 |
| `RC-19` | 经济单位、价格瀑布、现金/义务/已赚收入与 sustainable income | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN,E-CLAIMS` | 没有真实价格、成本、合同或现金流 |
| `RC-20` | ExperimentFamily、完整候选宇宙、累计预算与 kill/re-entry | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 组合上限和统计方法须由未来项目冻结 |
| `RC-21` | DecisionExposure 与无识别不发布因果规则 | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 尚无随机或可信准实验 |
| `RC-22` | Outcome maturity、右删失、OwnerObjective 与 income sufficiency | `LEAD-CANDIDATE-PASS-AS-DESIGN` | `E-DESIGN` | 用户收入目标、风险窗与现实 cohort 未冻结 |
| `RC-23` | 残余未知与变化监控明确 | `LEAD-CANDIDATE-PASS` | `E-CLAIMS,E-DESIGN,E-LOG` | 未知只能由 shadow 或经授权现实证据消除 |
| `RC-24` | 冻结两轮逐结果筛选，无 NEW-CRITICAL/UNRESOLVED，完成 joint 与最终状态共同同意 | `INDEPENDENT-EXACT-PASS` | `E-SSP,E-RUN2-FINAL,E-CROSSWALK-JSONL,E-CROSSWALK-VERIFIER,E-CROSSWALK-TEST,E-RUN2-ACCEPT,E-RUN2-ACCEPT-VERIFIER,E-RUN2-ACCEPT-TEST` | attempt 2 exact ACCEPT 只证明协议内类别代码本未扩展；不证明来源正确、研究穷尽、商机或总体 C7 |
| `RC-25` | immutable candidate 与 governance/shadow 后闭合工件的 inventory/失效边界无自引用 | `PENDING-C8-DOMAIN-GATE-CODE-INTERFACE-REVIEW` | `E-ENVELOPE,E-C6-SANDBOX,E-C7-SHADOW-FAILURE,E-CAPABILITY-POLICY,E-SHADOW-RUNNER,E-SHADOW-TEST,E-C8-DOMAIN-GATE-REVIEW,E-LEGACY-QUARANTINE,E-REVIEW-HISTORY,E-CANDIDATE-VERIFIER,E-POST-VERIFIER,E-PHASE-TEST,E-MANIFEST-BUILDER,E-FREEZE-BUILDER` | C6/C7 transport sandbox 局部 PASS 已被 C7 领域语义实现失败限定；C8 必须完成 exact bytes、反例测试和无 Critical/Major 的独立代码/接口复审。same-UID/admin、完整 dylib/host TCB、Darwin RSS hard limit、post-sandbox FD enumeration 与检测型 ceiling 仍为 nonclaims |
| `RC-26` | 最终独立复核绑定完整 manifest 与每个 SHA，无承重缺口 | `PENDING` | 所需证据为 C8 exact `FINAL_CANDIDATE_MANIFEST.json`、builder-produced external freeze report 与 candidate-bound independent review receipt | 必须由未撰写 C8 的 independent reviewer 检查全部原件；只有外部 receipt 明确 PASS 且无 Critical/Major 后才可能进入 governance，当前权威状态保持 `BLOCKED` |

## 当前结论与停止规则

Lead 已登记 C6 declarative iteration A 的承重拒绝项和 iteration B 的 transport/sandbox 局部 PASS；C6 exact candidate/freeze 因 Run2 semantic Major 被完整终审拒绝，attempt 1 又被两份逐条审查拒绝，attempt 2 才由两名只读 reviewer 对相同 exact bytes 接受。C7 canonical manifest、freeze、RC-26 与限定 governance 随后通过，但 C7 Shadow 的 exact 实现审查以领域语义 overaccept 拒绝，因而不能将 C6/C7 代码接口 PASS 迁移给 C8。只有 C8 领域 Gate 独立复审、canonical manifest、builder-produced freeze report 与 RC-26 全量独立 PASS 才能改变总体 `BLOCKED`；任何局部 PASS 均不得迁移为总体终审。

后续顺序固定为：

1. 用显式闭集 builder 生成不自包含的 canonical `FINAL_CANDIDATE_MANIFEST.json`；
2. 运行 crosswalk、Run2 acceptance、phase-boundary 全部验证与测试，并用 `build_freeze_report.py` 在 candidate/post-closure roots 外生成 exact-schema freeze report；
3. 由未撰写 C8 的 independent reviewer 绑定 manifest exact hash、freeze report、全部文件、依赖、C7 失败修复语义、权限边界和 residual unknown，给出 PASS/FAIL；
4. 只有无 unresolved critical/major 的 PASS 后，才能在预声明 governance sibling root 写入 freeze report、review receipt 与外部 `RESEARCH_CLOSURE_DECISION`，再由 governance manifest 和 aggregate Gate 闭合；
5. 只有 aggregate Gate 通过，才可创建另一个 sibling root，开始 `external_action_authority=false` 的本地、合成 fixture、零外部副作用 shadow MVP。

任一 candidate 字节变化都会使 manifest、RC-26、后续 receipt、decision 和 downstream roots 失效；governance 变化使 shadow root 失效；shadow 变化只使相应 implementation/Eval 失效。

即使 RC-26 未来通过，也不能声称存在具体商机、需求已验证、价格可接受、能够交付、可以盈利、可以完全自治或获得任何现实商业动作权限。
