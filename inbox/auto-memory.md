# Auto Memory Inbox

> Memory Commit Protocol 的兜底文件。当 Claude 在对话里听到 Javen 讲"X 现在变成 Y"但**不确定写哪个 vault 文件**时，append 到这里。下次 ingest / session 处理后迁移到正式位置，处理完后从本文件删除。

> 详细规则见 `MyBrain/CLAUDE.md` 的"持久记忆协议（Memory Commit Protocol）"小节。

---

## 待处理事实

（Claude append 在这里，格式见下方示例）

---

## 示例格式

```markdown
## 2026-05-08 14:00
Javen 说："QGOV 也关窗口了"
建议落点：MyBrain/career/applications.md 第 12 行（QGOV 那条），状态从 ⏳ 待 submit → ⛔ 窗口关闭未投
```

---

## 处理日志

- (空)
