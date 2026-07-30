# 投研纪律系统｜当前 Graph

> 这是给 Javen 查看进度的只读窗口。它不决定路线，也不构成验收；权威路线仍由冻结的 Mission Graph 和 Product Capability Graph 控制。

## 现在在哪

```mermaid
flowchart TB
    G["✅ Graph 基线<br/>冻结 + fresh review"] --> D["✅ 方向结论<br/>一个闭合数值权威域"]
    D --> R["✅ 路线控制 R4D<br/>610328c 已接受"]
    R --> S(["▶ Paper Gate 产品实现<br/>14-path bounded slice"])
    S --> P["○ Mutable prefreeze<br/>攻击验证"]
    P --> K["○ 冻结产品 exact candidate"]
    K --> W["○ Fresh 独立审查"]
    W --> A["○ Paper Gate 验收"]
    A --> L["🔒 Ledger<br/>当前未开放"]

    D -. "失败历史保留" .-> F["✖ R1 / R2 / R3 / R4 / R4B / R4C"]
    S -. "若再现同根失败" .-> H["■ 停止并 backtrack<br/>不做 R5"]

    classDef done fill:#d3f9d8,stroke:#2b8a3e,stroke-width:2px;
    classDef current fill:#fff3bf,stroke:#e67700,stroke-width:3px;
    classDef failed fill:#ffe3e3,stroke:#c92a2a,stroke-width:2px;
    classDef pending fill:#f1f3f5,stroke:#868e96;
    class G,D,R done;
    class S current;
    class F,H,L failed;
    class P,K,W,A pending;
```

一句话：项目没有停。路线控制 `610328c` 已通过 fresh frozen review；当前只实现一个闭合数值域的 Paper Gate 产品切片。Ledger 仍锁定。

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

- 更新时间：`2026-07-30T07:21:48-0700`
- 执行状态：`RUNNING_CLOSED_NUMERIC_DOMAIN_PRODUCT_R4`
- Graph 当前节点：`CAP-PAPER-GATE-INTEGRITY`
- 当前工作项：`WORK-PAPER-GATE-SINGLE-STATE-MACHINE-R1`
- 当前义务：`OBL-PAPER-UNIQUE-COMMIT-SINK`
- 当前实现：`唯一 closed-domain Paper Gate successor；mutable worktree，尚未验收`
- R1 失败快照：`294e92b2d53c024dd99d1f787dd6e82f0926081d`
- R2 失败快照：`1afc87d2df802efd1563ce9c43c1b0cb7efcf7c4`
- R3 失败快照：`b2745910770c016327f73e749771e63626983d58`
- R3 失败收据：`/private/tmp/PAPER_GATE_R3_B274591.prefreeze-failure.json`
- R4 路线绑定失败快照：`ab021e94d94357e9a82255dbf62f3f53c60d50c0`
- R4 路线绑定失败收据：`/private/tmp/PAPER_GATE_DIRECTION_R4_AB021E9.prefreeze-failure.json`
- R4B 路线绑定失败快照：`c1a19d2f33b3a2c40b2938b5c381b10f2cd1803c`
- R4B 路线绑定失败收据：`/private/tmp/PAPER_GATE_DIRECTION_R4B_C1A19D2.prefreeze-failure.json`
- R4C 路线绑定失败快照：`40c88981942bea40502010521623d8d9fef61e58`
- R4C frozen-review 失败收据：`/private/tmp/PAPER_GATE_DIRECTION_R4C_40C8898.frozen-review-failure.json`
- 当前根因：并非某一个 Decimal 字段，而是没有在 canonical event、reducer 和 replay 之前，把所有权威数值原语收敛到同一个封闭、有界、环境无关的表示域。
- 方向结论：`一个覆盖所有权威 numeric primitive 的 closed canonical scalar/value domain；不是 R3 字段补丁`
- 已接受的路线控制：`610328ce328834bd43c60e1cc0fa2aaa7d5866c7`
- Route-control fresh review 收据：`/private/tmp/PAPER_GATE_DIRECTION_R4D_610328C.fresh-review-pass.json`
- 当前动作：在 Graph 允许的既有产品写集内，把所有权威数值在 identity、event、reducer、SQLite 和 replay 之前收敛到同一个 signed-64 fixed-point / integer domain；完成后先做 mutable prefreeze，再冻结 exact product candidate，并由 fresh reviewer 只检查冻结对象。
- 当前产品写集：`14 paths`（既有 inventory；不新增 Graph、governance、authority kernel 或 parallel numeric protocol）
- 当前产品候选：`尚未冻结`
- Ledger：`未开放`
- 用户参与：`当前不需要`

## 权威来源

- 全项目路线：`governance/PROJECT_MISSION_GRAPH_V2.json`
- 产品能力依赖：`governance/PRODUCT_CAPABILITY_GRAPH_V1.json`
- 当前节点边界：`governance/PAPER_GATE_STATE_MACHINE_BOUNDARY_V1.json`
- 当前冻结 Graph 基线：`23ffe3dc67d17fde1e42fc53ac845945849f4dd2`

本页只在阶段切换、候选冻结、fresh review 完成、真实阻塞或项目完成时更新；普通测试与局部思考不写入。
