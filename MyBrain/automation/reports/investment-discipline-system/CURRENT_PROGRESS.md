# 投研纪律系统｜当前 Graph

> 这是给 Javen 查看进度的只读窗口。它不决定路线，也不构成验收；权威路线仍由冻结的 Mission Graph 和 Product Capability Graph 控制。

## 现在在哪

```mermaid
flowchart TB
    G["✅ Graph 回溯方向<br/>已冻结并通过 fresh review"] --> R1["✖ Paper Gate R1<br/>冻结前失败 · 原样保留"]
    R1 --> R2["✖ Paper Gate R2<br/>无界数值环境依赖 · 已保留"]
    R2 --> R3(["▶ Paper Gate R3<br/>当前唯一 successor"])
    R3 --> D(["▶ 当前动作<br/>有界 fixed-point units"])
    D --> T["○ 边界 + 跨环境攻击验证"]
    T --> P["○ 冻结前独立复审"]
    P --> F["○ 冻结 bounded candidate"]
    F --> V["○ Fresh 独立审查"]
    V --> L["○ Ledger 节点开放"]

    G -. "已否决的旁路" .-> X["✖ Ledger 候选<br/>均未获接受 · 返回 Paper Gate"]

    classDef done fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef current fill:#fff3bf,stroke:#e67700,stroke-width:3px;
    classDef failed fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class G done;
    class R3,D current;
    class R1,R2,X failed;
    class T,P,F,V,L pending;
```

一句话：项目没有停；Graph 仍把工作锁在 **Paper Gate**。R2 的两路独立冻结前审查都复现了同一权威输入会随 Python 进程设置产生不同终态，因此 R2 已作为失败快照保留。当前已换控制层到 R3：先把输入规范化为有界 fixed-point units，再进入 canonical approval、整数 reducer 和 SQLite INTEGER 重放；尚未冻结，也没有开放 Ledger。

## 项目目标与产品主路径

```mermaid
flowchart TB
    M["项目目标<br/>个人 · 本地优先 · 只做纸面投资<br/>AI 辅助 · Javen 最终决定"] --> PG(["▶ 纸面风险闸门<br/>当前唯一节点"])

    PG --> L["事务化账本与复盘<br/>等待 Paper Gate"]
    PG --> H["AI 证据 + 人类决定<br/>等待 Paper Gate"]
    B["诚实历史检验<br/>待完成"] --> W["本地工作台<br/>待开放"]
    D["公开数据证据<br/>待完成"] --> W
    L --> W
    H --> W
    L --> R["可验证恢复<br/>待完成"]
    W --> R
    W --> G["真实纸面 Dogfood<br/>待完成"]
    R --> G
    G --> X["个人 Paper MVP<br/>发布候选"]

    classDef current fill:#fff3bf,stroke:#e67700,stroke-width:3px;
    classDef boundary fill:#e7f5ff,stroke:#1971c2,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class PG current;
    class M,X boundary;
    class L,H,B,D,W,R,G pending;
```

## 当前状态

- 更新时间：`2026-07-30T04:11:54-0700`
- 执行状态：`RUNNING`
- Graph 当前节点：`CAP-PAPER-GATE-INTEGRITY`
- 当前实现：`Paper Gate R3 bounded fixed-point successor`
- 已保留失败快照：`1afc87d2df802efd1563ce9c43c1b0cb7efcf7c4`
- R2 失败收据：`/private/tmp/PAPER_GATE_R2_1AFC87D.prefreeze-failure.json`
- 当前根因：允许无界 Decimal 进入权威状态机，会让进程级整数转换限制改变 canonical 结果、durable terminal 和重放能力。
- 当前动作：在任何 canonical expansion 或大整数构造前，把 price、quantity、money、fee、ratio 映射到项目既有 quantum 的有界 units；之后只允许受检整数运算与 SQLite INTEGER 存储。
- 当前候选：`尚无可冻结候选`
- Ledger：`未开放`
- 用户参与：`当前不需要`

## 权威来源

- 全项目路线：`governance/PROJECT_MISSION_GRAPH_V2.json`
- 产品能力依赖：`governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
- 当前节点边界：`governance/PAPER_GATE_STATE_MACHINE_BOUNDARY_V1.json`
- 当前冻结 Graph 基线：`23ffe3dc67d17fde1e42fc53ac845945849f4dd2`

本页只在阶段切换、候选冻结、fresh review 完成、真实阻塞或项目完成时更新；普通测试与局部思考不写入。
