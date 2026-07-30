# 投研纪律系统｜当前 Graph

> 这是给 Javen 查看进度的只读窗口。它不决定路线，也不构成验收；权威路线仍由冻结的 Mission Graph 和 Product Capability Graph 控制。

## 现在在哪

```mermaid
flowchart TB
    G["✅ Graph 回溯方向<br/>已冻结并通过 fresh review"] --> R1["✖ Paper Gate R1<br/>冻结前失败 · 原样保留"]
    R1 --> R2["✖ Paper Gate R2<br/>无界数值环境依赖 · 已保留"]
    R2 --> R3["✖ Paper Gate R3<br/>重复同根故障 · 已保留"]
    R3 --> D["✅ Fresh 方向审查<br/>选择统一数值权威控制层"]
    D --> Q(["▶ Graph 方向绑定 R4<br/>当前动作 · 消费两个 trigger"])
    Q --> S["○ 唯一 closed-domain successor<br/>仅在绑定通过后"]
    Q -. "若绑定不能保持现有 Graph 权威" .-> H["○ 保持 stalled<br/>Ledger 继续锁定"]
    S --> P["○ Mutable prefreeze<br/>攻击 + 独立复审必须 PASS"]
    P --> F["○ 冻结 exact candidate"]
    F --> V["○ Fresh 独立审查"]
    V --> L["○ Ledger 节点才可能开放"]

    G -. "已否决的旁路" .-> X["✖ Ledger 候选<br/>均未获接受 · 返回 Paper Gate"]

    classDef done fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef current fill:#fff3bf,stroke:#e67700,stroke-width:3px;
    classDef failed fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class G done;
    class D done;
    class Q current;
    class R1,R2,R3,X failed;
    class S,H,P,F,V,L pending;
```

一句话：项目没有停；Graph 仍把工作锁在 **Paper Gate**。Fresh 方向审查已选择“所有权威数值先进入一个闭合、环境无关的表示域”。当前先让 Product Graph 正确绑定并消费这次同根失败与新控制层两个 trigger；绑定通过前不写新的 prototype，Ledger 没有开放。

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

- 更新时间：`2026-07-30T05:10:14-0700`
- 执行状态：`RUNNING_ROUTE_CONTROL_BINDING`
- Graph 当前节点：`CAP-PAPER-GATE-INTEGRITY`
- 当前实现：`没有可接受的 mutable candidate；R3 已冻结为失败证据`
- R1 失败快照：`294e92b2d53c024dd99d1f787dd6e82f0926081d`
- R2 失败快照：`1afc87d2df802efd1563ce9c43c1b0cb7efcf7c4`
- R3 失败快照：`b2745910770c016327f73e749771e63626983d58`
- R3 失败收据：`/private/tmp/PAPER_GATE_R3_B274591.prefreeze-failure.json`
- 当前根因：并非某一个 Decimal 字段，而是没有在 canonical event、reducer 和 replay 之前，把所有权威数值原语收敛到同一个封闭、有界、环境无关的表示域。
- 方向结论：`一个覆盖所有权威 numeric primitive 的 closed canonical scalar/value domain；不是 R3 字段补丁`
- 当前动作：建立窄范围 R4 route-control candidate，让现有 Graph 校验分别消费 `same_acceptance_obligation_fails_after_a_claimed_root_fix` 与 `new_abstraction_or_protocol_layer_is_proposed`；node、work、obligation、objective 与风险规则均不改变。
- 当前候选：`尚无可冻结候选`
- Ledger：`未开放`
- 用户参与：`当前不需要`

## 权威来源

- 全项目路线：`governance/PROJECT_MISSION_GRAPH_V2.json`
- 产品能力依赖：`governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
- 当前节点边界：`governance/PAPER_GATE_STATE_MACHINE_BOUNDARY_V1.json`
- 当前冻结 Graph 基线：`23ffe3dc67d17fde1e42fc53ac845945849f4dd2`

本页只在阶段切换、候选冻结、fresh review 完成、真实阻塞或项目完成时更新；普通测试与局部思考不写入。
