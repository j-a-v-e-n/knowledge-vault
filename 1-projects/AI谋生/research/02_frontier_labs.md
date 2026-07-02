---
title: "Frontier AI Labs 招聘趋势 2025-2026 — A2 Research Output"
research_date: 2026-05-12
agent: A2 (frontier_labs)
agent_type: researcher (Haiku)
tool_uses: 16 (8 WebFetch + 8 WebSearch)
duration_ms: 84178
confidence_overall: high (FDE/MTS data) + medium (strategic inferences)
---

# Frontier AI Labs 招聘趋势 2025-2026 — Capability Audit

> 调研对象: Anthropic / OpenAI / Google DeepMind / xAI / Meta AI / Mistral / Cohere
> 调研方法: WebFetch 官网 careers 页 (大多 CMS 拦截) → WebSearch 深度报告 (Epoch AI 2026 分析、a16z FDE piece) → 精准锁定 3 个新 role 定义 + 2 个薪资数据源 + 1 个战略分析

## Executive Summary

**Frontier labs 2025-2026 招聘 3 个核心 shift**:
1. **Forward Deployed Engineer (FDE) 爆发** — 从虚无到显学 (2024 新概念). OpenAI 目标 50 人 by 2025. 信号: "模型商品化 → 部署稀缺"
2. **Member of Technical Staff (MTS) title 替代 SWE** — 反映研究院文化, xAI/Anthropic/OpenAI 都在用
3. **2025 重点从纯研究分裂为 "部署 + 硬件" 双轨** — Sales/GTM 角色翻番 (Anthropic +14pp / OpenAI +10pp)

## 1. Forward Deployed Engineer (FDE) — Services-Led Growth 护城河

**关键 finding** (confidence: HIGH — 直接 JD + a16z 分析)

- Anthropic & OpenAI 都在 2024 建立 / 扩张 FDE 团队
- **OpenAI 目标 by 2025: ~50 FDE**
- **JD 重点**: 3+ yr customer-facing technical work, advanced prompt engineering, agent development, production LLM experience
- **薪资**:
  - Anthropic: **$280k–$320k base**
  - OpenAI mid-senior: **$350k–$550k base**

**为什么 frontier labs 都做这个**:
> "Enterprises buying AI are like your grandma getting an iPhone: they need you to set it up." — [a16z services-led growth piece](https://a16z.com/services-led-growth/)

**A16z 论点**: foundation model 本身商品化, **moat 在 deployment + customer integration**. FDE 是 services-led growth 的具体载体。

## 2. Member of Technical Staff (MTS) ≠ Software Engineer

**关键 finding** (confidence: HIGH — 直接薪资 + 公司 careers page)

- MTS title 起源 Bell Labs, 强调 **versatility + cutting-edge problem-solving**, 而非 SWE 的 rigid hierarchy
- Frontier labs (OpenAI, Anthropic) 采用 MTS 信号: **research-engineering blend**, soft skills 也算
- 薪资: **OpenAI MTS $189k–$307k base**
- 含义: research lab 招的不是纯 researcher 也不是纯 engineer, 而是混合体, 能 papers + ship code + 跟 customer 聊

**Source**: [OreateAI on MTS at OpenAI](https://www.oreateai.com/blog/inside-openais-technical-ranks-the-member-of-technical-staff-role-and-its-compensation/cda3df497aa40791f4aa9d25de0d5240)

## 3. 2023→2025 招聘 shift: Research → Deployment + Hardware

**关键 finding** (confidence: HIGH — Epoch AI March 2026 分析)

| Year | 主要 hire focus | Evidence |
|---|---|---|
| **2023** | 纯 research (paper publication) | Anthropic / OpenAI 早期 hire 以 research scientist 为主 |
| **2024** | Large-scale training infra | Distributed training engineer, GPU systems |
| **2025** | **Commercial deployment + 硬件 specialization** | FDE surge + OpenAI 建 consumer device (15 roles, camera/silicon) + DeepMind XR/robotics (9 roles) |

**Sales/GTM growth**:
- Anthropic: 17% → **31%** of open roles (+14pp)
- OpenAI: 18% → **28%** of open roles (+10pp)

**Source**: [Epoch AI 2026 — What Frontier AI Job Postings Reveal](https://epoch.ai/gradient-updates/ai-lab-job-postings)

## 4. Data Strategy Divergence

**关键 finding** (confidence: MEDIUM — inferred from job board public visibility)

- **xAI**: 公开招 27 human data labeling roles
- **Anthropic & DeepMind**: 几乎不公开 advertise labeling roles

**两种推论**:
- (a) xAI 真的在 build in-house labeling culture, 别家用外包 (Scale AI / Surge AI 等)
- (b) 只是招聘 visibility 策略差异 — Anthropic / DeepMind 也大量招但用 contractor / internal rotation

**Source**: Epoch AI March 2026

## 5. Scarce Capabilities Matrix

按 frontier labs hiring intensity 排序 (confidence: MEDIUM — 从 job volume + qualitative cues 推断)

| Rank | Scarce capability | Why scarce | Frontier-lab evidence |
|---|---|---|---|
| **1** | **Forward deployment + customer integration** | "Model 商品化 → 部署 = moat" | Anthropic / OpenAI FDE 全 +50 人扩张 |
| **2** | **Custom silicon / on-device ML** | Compute 效率 + 硬件协同 = frontier moat | OpenAI 21 roles consumer device; DeepMind XR focus |
| **3** | **Evaluation + benchmarking infrastructure** | Eval = arms race; without it new SOTA 无法 verify | OpenAI "Research Engineer, Frontier Evals" 显性招; xAI 大规模 data ops |
| **4** | **Safety + alignment engineering** | RLHF / red-team / mech interp 都是稀缺技能 | Anthropic 招但 opacity 高 (likely 内部 rotation + 保密 JD); DeepMind "Responsibility" roles 涌现 |
| **5** | **Product-adjacent research (MTS proliferation)** | Research labs 也需要 communication + customer empathy | MTS title 普及, 区别 pure researcher / pure engineer |

## 6. Key Verbatim Quotes (for citation)

> "Enterprises buying AI are like your grandma getting an iPhone: they need you to set it up." — a16z

> "OpenAI established its own FDE team at the start of 2024 and plans to expand it to roughly 50 engineers by 2025." — Hashnode 2026 Guide

> "Anthropic's go-to-market positions grew from 17% to 31% of open roles, while OpenAI's increased from 18% to 28%." — Epoch AI March 2026

> "Member of Technical Staff... reflects the culture of innovation and problem-solving rather than strict engineering role definitions" — OreateAI

> "xAI uniquely advertises 27 human data labeling roles publicly, contrasting with competitors' less visible approaches." — Epoch AI

## ⚠️ 矛盾与不确定

- **xAI transparency paradox**: 公开 27 labeling 是真规模差异还是招聘 visibility 策略? (confidence: low)
- **Safety hiring opacity**: Anthropic / OpenAI safety 角色在公开 job board 可能严重 underrepresented; 真实规模未必能 verify (confidence: low)
- **MTS salary range**: $189k–$307k 是 OpenAI 公开 band; 实际 MTS 拿到的可能高于 band (RSU + signing bonus 不在 base 里)

## 📎 Sources

1. [Hashnode — Complete 2026 Guide to the Forward Deployed Engineer](https://hashnode.com/blog/a-complete-2026-guide-to-the-forward-deployed-engineer)
2. [eWeek — Why AI Companies Want Forward Deployed Engineers (Anthropic, OpenAI, Cohere)](https://www.eweek.com/news/openai-anthropic-cohere-ai-hiring/)
3. [OreateAI — OpenAI Member of Technical Staff Role and Compensation](https://www.oreateai.com/blog/inside-openais-technical-ranks-the-member-of-technical-staff-role-and-its-compensation/cda3df497aa40791f4aa9d25de0d5240)
4. [Epoch AI — What Frontier AI Job Postings Reveal (March 2026)](https://epoch.ai/gradient-updates/ai-lab-job-postings)
5. [a16z — Trading Margin for Moat: Forward Deployed Engineer](https://a16z.com/services-led-growth/)
