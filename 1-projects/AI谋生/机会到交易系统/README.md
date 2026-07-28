# 机会到交易系统：旧原型存档

> 状态：`HISTORICAL / LEGACY_UNQUALIFIED / GLOBALLY_QUARANTINED`

本目录中的 `schema/workspace 0.1` 是研究闭合前形成的旧原型，不是当前系统、实现起点或可运行 Pilot。它不能证明需求、买方、价格、交付可行性、交易、权限或研究闭合。

## 已执行的权限边界

- 旧 CLI 的 `init`、`add`、`validate`、`status` 和 `make-harness` 全部稳定失败关闭；
- 旧 Python API 不读取调用者提供的文件或记录，也不创建、修改任何工作区；
- 旧记录不能再产生结构合格声明、商业状态、外部权限或任务工件；
- 隔离是代码级全局 tombstone，不依赖目录位置、可删除 marker 或 screening，因此复制工作区、换路径或加入 `pass` 记录都不能解除；
- 本目录没有创建 successor runtime。

固定拒绝原因为：

`LEGACY_SCHEMA_WORKSPACE_0_1_QUARANTINED: legacy schema/workspace 0.1 is globally tombstoned and has no current authority`

## 保留材料的用途

- [`LEGACY_STATUS.md`](./LEGACY_STATUS.md)：权威的旧原型隔离状态；
- [`LEGACY_CODE_GAP_AUDIT.md`](./LEGACY_CODE_GAP_AUDIT.md)：为何选择整体撤销而不是继续增量修补；
- [`研究/2026-07-27-总体设计/`](./研究/2026-07-27-总体设计/)：研究候选和闭合材料，其存在本身不授权实现；
- [`pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json`](./pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json)：旧 Pilot 工件的逐文件撤销与原始字节哈希绑定。

目录内其余设计、状态、记录、预览和测试材料都只能作为历史证据或对抗 fixture 阅读。任何未来实现都必须另行获得明确授权，并使用与旧 `0.1` 语义隔离的新身份和验收证据。
