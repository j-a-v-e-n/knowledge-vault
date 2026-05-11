# Auto Memory Inbox

> Memory Commit Protocol 的兜底文件。当 Claude 在对话里听到 Javen 讲"X 现在变成 Y"但**不确定写哪个 vault 文件**时，append 到这里。下次 ingest / session 处理后迁移到正式位置，处理完后从本文件删除。

> 详细规则见 `MyBrain/CLAUDE.md` 的"持久记忆协议（Memory Commit Protocol）"小节。

---

## 待处理事实

（Claude append 在这里，格式见下方示例）

## 2026-05-11

Javen paste 一段「macOS 中文语音输入 + 不用 Claude voice mode」的操作指南（看起来是教别人/给自己的双设备指南，"电脑同理"暗示前面还有手机端版本）。完整内容：

> 电脑同理——用系统自带的语音输入，不要用 Claude 的 voice mode。
>
> macOS
>
> - 系统设置 → 键盘 → 听写（Dictation） → 打开
> - 语言那一栏 → 加上"普通话 - 中国大陆"（或台湾/香港）。第一次会下载语言包，等几分钟
> - 快捷键设成你顺手的，默认是按两下 fn 键
> - 把 Claude 网页或桌面 app 的输入框点亮，按快捷键，开始说中文，再按一次结束，文字就进去了

**建议落点**（待 Javen 确认）：
- 如果是给自己长期 workflow tip → `MyBrain/wiki/工程方法/超级个体_工具与杠杆.md` 新增"中文语音输入"小节
- 如果是给别人写的指南（朋友 / 家人 / 同学）→ 建新 wiki 页 `wiki/工程方法/中文语音输入跨设备指南.md`（带手机端 + macOS 双 section）
- 如果只是 paste 错窗口 / 临时 dump → 不动，等 ingest 时归档或 delete

**隐含偏好**："不要用 Claude 的 voice mode" 可能是 Javen 自己的工具偏好——但 prompt 不清晰，没自动写到 CLAUDE.md。

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
