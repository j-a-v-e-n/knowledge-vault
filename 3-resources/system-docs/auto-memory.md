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

## 2026-05-15 (UPDATED retrospective — important)

⚠️ **Plan vs 实际提交 SoP 不一致**：

- Javen 5/14 23:59 之前**已提交** BS/MS application（5/15 主对话发现：Form 显示 "You've already responded"）
- **5/14 实际提交版 SoP = `sop-bsms-final.md`**（不是 v6 — 5/16 Form receipt verified）
  - Specialization: **Intelligent Systems, Robotics & Control (Impacted)** (不是 v6 的 Machine Learning & Data Science)
  - Faculty mentioned: **Prof. Nikolay Atanasov** (v6 frontmatter 说 no faculty — 但实际提交版 final.md 有 Atanasov)
  - Entry Quarter selected: **Fall 2027**
  - PID: A17806950
  - GPA: 3.609 cumulative / 3.377 major (cumulative ≥ 3.4 → no LOR needed; major 3.377 < 3.4 但 OR 条件满足)
  - Senior Year Course Plan: Fall 2026 (ECE 107/153/176/COGS) + Winter 2027 (ECE 190/AHI/MATH 180A/ECE 188) + Spring 2027 (MATH 180B/ECE 191/ECE 199)
- **Course plan 跟新 plan 冲突 — surface to Javen**: 5/16 5/16 报告 surface Spring 2027 还有 3 门课 vs Winter 2027 毕业不一致，admissions 可能 push back
- **5/14 提交版 SoP timeline = "June 2027 BS / Fall 2027 MS"**（基于 final.md 内容）
- **Javen 5/15 真实 plan = "Winter 2027 BS / Spring 2027 MS"**（提前一学期）
- **不一致，Google Form 已锁不可改**

**5/15 session 误改 vault（已 revert）**：
- 误以为 SoP 还能改，把 v6 timeline 从 June/Fall 改成 Winter/Spring
- ✅ 已 revert v6 paragraph 6 + checklist 回到 "June 2027 / Fall 2027" reflect 实际提交版本

**task-board 仍有不一致**（待 Javen 决定 follow-up 后再 align）：
- task-027 目标/关键信息/子任务 B3 仍写 "Spring 2027 MS"
- task-009 背景毕业时间也写 "Winter 2027"

**Javen 5/15 选 A** — 想 Spring 2027 开始 MS。

**FAQ 政策已 verified（5/15 WebFetch）**：UCSD ECE BSMS FAQ 明文允许 entry quarter 改动:
> "If I can complete my undergraduate program earlier than I expected, ... can I change my M.S. program starting quarter? Yes, we understand that plans may change. Please notify us as soon as possible. You will need to email us at least one quarter before your undergraduate program completion quarter."
> (source: https://www.ece.ucsd.edu/graduate/bsms-frequently-asked-questions-page)

**行动**: Email `ecebsmsadmissions@ucsd.edu` 改 entry quarter Fall 2027 → Spring 2027
- Email draft 已写到 `MyBrain/career/email-drafts/2026-05-15_bsms-entry-quarter-update.md`
- 政策 deadline: 至少 Fall 2026 quarter 之前（>4 个月窗口，时间充裕）
- FAQ 推荐 timing: "as soon as possible" → 现在发

**等 Javen 发送 + admissions 回复后**:
- 落盘 admissions confirm 邮件
- task-board.md task-027/009 可正式 align "Spring 2027 entry"
- 此时 vault 跟 ground truth 完全一致

**老 sop-bsms-v2.md 也被改过**（5/14-5/15 session 误改 timeline 成 Winter/Spring）——v2 是 backup 未提交不影响 application，但 vault 一致性建议也 revert。

**lesson 触发**: 5/15 session 没先 verify "SoP 是否已提交" 就改 vault → ground truth 跟 vault 短暂不一致。新规则：**操作任何"已提交/已 finalized 文件"前必须先 verify 是否 immutable**——记入 `MyBrain/automation/docs/lessons.md`。

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
