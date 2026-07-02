---
title: 知识编辑 meta-rules
type: concept
tags: [工程方法, 知识管理, vault 维护, meta-rule]
created: 2026-05-16
updated: 2026-05-16
confidence: high
priority: active
---

# 知识编辑 meta-rules

> 处理 vault 内容（写新页、合并、拆分、改、归档）时的**通用决策原则**。每条都附 trigger condition + 反 pattern。新原则 append（不删旧的）。

跟 [[AI 团队设计原则]] 互补：那篇讲怎么设计 agent，本篇讲 Claude（agent 自己）怎么编辑 vault 不犯低级错。

---

## ① 合并要谨慎 — 避免信息错误 + 丢失信息

**Source**：Javen 2026-05-16 主对话指令

**何时触发**：考虑把 N 个 page / cluster / 文档 / 子任务**合并成一个**时。

**核心原则**：合并的诱惑是"省事"，代价是：

1. **abstraction level 混淆**：原本 micro 和 macro 各自清晰，合并后读者跳来跳去
2. **信息浅化**：怕篇幅过长，每部分都被压缩，关键 evidence 被砍
3. **cross-link 路径丢失**：原本能各自精准 link 到 vault 不同位置，合并后只能 link 到一个 hub
4. **debate / contradiction 被消解**：来源 A 说 X 与来源 B 说非 X，合并时容易"和稀泥"成"两者都对"

**决策 checklist**（决定合并前问自己）：

```
□ 1. 两份内容真的是同一 abstraction level 吗？（micro vs macro 一律分开）
□ 2. 合并后总长度是否会 > 3000 字？是 → 拆开
□ 3. 各自能 cross-link 到 vault 不同 hub 吗？是 → 拆开
□ 4. 有 debate / contradiction 吗？有 → 拆开（debate 页独立）
□ 5. 合并的真实理由是"省 token / 省力气"吗？是 → 拆开
□ 6. 合并能让信息密度提高吗？只有"是"才合并
```

任何一条 ✗ → 默认**拆开**。

**反 pattern**：

- ❌ "这两个内容看起来相关就放一起" → 相关 ≠ 同 abstraction level
- ❌ "合并是因为篇幅都不长" → 篇幅短的应该独立成短文档，不强凑
- ❌ "合并是因为读者一次看完更方便" → vault 是网状，不是线性阅读，读者按 wikilink 跳

**Pro pattern**：

- ✅ 各自独立成 doc + 互相 cross-link
- ✅ 如果真的同议题，分 "Part 1 / Part 2" 系列但保持独立 file
- ✅ 用 hub 页（type: overview）做导航，不是 hub 页本身吞所有内容

**实例（2026-05-16 触发）**：
Cluster 3（Agent 内部架构）+ Cluster 4（Multi-agent 协同）—— 表面相关（都是 agent 主题），但 abstraction level 不同（micro vs macro）。第一直觉合并省事；按本原则拆开为两份独立 wiki 文档，各自 cross-link 到 vault 不同位置（cluster 4 → [[AI 团队设计原则]]；cluster 3 → `.claude/skills/` + MCP + daemon context 管理）。结果信息密度更高 + 丢失风险更小。

---

## ② [将来其他 meta-rule append 在这下面]

新增格式：

```markdown
## ② [一句话原则名]

**Source**：Javen YYYY-MM-DD 主对话

**何时触发**：[场景]
**核心原则**：[逻辑]
**决策 checklist**：[问自己的 N 个问题]
**反 pattern**：[不要做什么]
**Pro pattern**：[要做什么]
**实例**：[触发 incident]
```

---

## 🔗 关联

- [[AI 团队设计原则]] — Agent 系统设计原则（micro+macro level）
- [[automation/docs/lessons.md]] — debug 卡死 / 工程层面教训
- `MyBrain/CLAUDE.md` "持久记忆协议" — 触发条件清单含元规则提取

## 📎 来源

- 2026-05-16 Javen "合并要谨慎，避免信息错误加丢失信息"（cluster 3+4 合并决策时）
- 2026-05-16 Javen "我们平时对话里包含的一些比较底层的思考是否会自动跟新到系统里"（推动元规则系统化的 trigger）
