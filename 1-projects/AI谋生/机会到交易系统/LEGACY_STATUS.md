# 旧原型状态

状态：`HISTORICAL / LEGACY_UNQUALIFIED / GLOBALLY_QUARANTINED`

适用范围：本项目旧 `schema/workspace 0.1` 的代码、工作区、记录、状态推导、permission 映射、CLI、测试和 Pilot 工件。

## 当前有效结论

旧 runtime 已被整体 tombstone，而不是继续局部加固。所有保留的公开运行入口在读取或写入任何调用者文件之前，统一抛出固定错误：

`LEGACY_SCHEMA_WORKSPACE_0_1_QUARANTINED: legacy schema/workspace 0.1 is globally tombstoned and has no current authority`

该边界是无条件的：

- 不由工作区内 marker 实现；
- 不由 Pilot 的停止 screening 实现；
- 不因新的 `pass` screening、复制目录、修改路径或删除 marker 而改变；
- 不因旧记录通过结构检查而生成商业状态、权限或工件；
- 不提供从旧对象升级成当前权威对象的自动迁移路径。

CLI 的所有旧子命令均以非零状态和相同原因退出。旧 `validate` 不再输出无范围的合格声明。旧 Python API 也执行相同拒绝，并且拒绝发生在输入检查和文件系统操作之前。

## Pilot 工件撤销

餐馆网页修复样本不是活动 Pilot。原来位于活跃 `workspace/harnesses/` 下的四个文件和活跃 preview 路径下的两张旧截图已经移入 `pilot/restaurant-web-repair/quarantine/original/`；原 RUN_LOG 的精确字节也保存在该目录。每个原路径、新路径和 SHA-256 均由 [`REVOCATION_MANIFEST.json`](./pilot/restaurant-web-repair/quarantine/REVOCATION_MANIFEST.json) 绑定，并统一标记：

- `authority_status = REVOKED_LEGACY_ARTIFACT`
- `authoritative_for = []`

活跃 RUN_LOG 路径只保留撤销通知，不再陈述旧验证结果、商业阶段、permission 或现行任务工件。

## 不授权事项

本次变更没有创建 successor runtime，也没有授权外联、展示、发布、报价、签约、收付款、部署或恢复旧 Pilot。旧材料只能作为历史反例和测试 fixture；未来系统若获授权，仍须以独立身份、独立语义和新鲜验收证据建立。
