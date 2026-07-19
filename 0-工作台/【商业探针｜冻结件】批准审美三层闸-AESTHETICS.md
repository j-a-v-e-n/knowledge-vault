**这是什么**：Gen-2 审美闸（doctrine D4）的尺子文件 `innovation/commercial/AESTHETICS.md` 要冻结生效——尺子属冻结内核 (a)，只能你批。闸代码已建好、正在 report-only 收证据，批了即硬闸。
**需要你做什么**：在下面 decision: 行回一个词（冻结 / edit: 怎么改 / 缓）。
**不办会怎样**：闸停留在"只记录不否决"——页面质量证据照收，但坏页面不会被机器拦下。战役其余工作不受影响（纲领 §4：内核排队，战役不停）。

# 冻结提案 — 审美三层闸 AESTHETICS.md

decision: 冻结

## 你在批什么（一句话一层）

- **Tier-0 选源即闸**：视觉一律从精选源起步（shadcn/ui + shadcnblocks/Tremor 结构，land-book/godly 参照），禁训练记忆品味。
- **Tier-1 机械底线**：Lighthouse accessibility ≥ 0.95、best-practices ≥ 0.95，不达标 deploy 不 accepted（代码判，不判"美"）。
- **Tier-2 相对裁决**：vision-LLM 只做 pairwise、不打绝对分（arXiv 2510.08783：MLLM 与人类偏好部分维度背离、不能替代人评）；**绝对审美判断永远是你的**，你的 pairwise 选择进口味台账。

## 已有的真证据（尺子 DRAFT 期收的）

spendbook 页面按 Tier-0 重建（2026-07-12，替换 Arial 线框）：Lighthouse **a11y 1.0 / best-practices 1.0 / perf 0.95**；新旧截图对比在 `innovation/commercial/runs/2026-07-12/gen2-evidence/`（old-page-desktop.png vs live-page-desktop.png）。顺手修掉线上真 bug：旧页按钮价格重复渲染（"Pre-order — $19 — $19.00"）。

## 附带说明（不需要你批，已按纲领自由区执行）

页面模板 gen2 化（构建物，非尺子）已上线；引文防编造代码闸（页面引文必须逐字链回 CK1 验过的 dossier）已焊进 deploy，fail-closed。criteria.md/checks.py 一字未动。

相关：[[战役纲领]] · innovation/DOCTRINE.md（D4 原文）· 知识库/inbox/二代改造方案.md §4d（三层结构调研出处）

办完 → 拖进 done/
