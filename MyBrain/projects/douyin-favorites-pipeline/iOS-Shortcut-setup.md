# iOS 快捷指令配置 — 极简版（3 个动作，5 分钟）

> 在中文系统里 **iOS Shortcuts = 快捷指令**。下面 action 名字按中文系统来；如果你 iPhone 是英文系统，括号里给了英文对照。
>
> 你只需要把抖音分享出来的**整段文本**写到 iCloud Drive 的一个文件夹。Mac 端已经会从任意文本里 regex 提 URL，**不需要你在 iOS 端做任何提取/解析**。

---

## 配置前确认

- ✅ iPhone 已升级到 iOS 16+
- ✅ iCloud Drive 已开（设置 → [你的名字] → iCloud → iCloud Drive）

DouyinInbox 文件夹我会在 Mac 端 setup.sh 里建，几秒后 iCloud 同步到你 iPhone。

---

## 配置（3 个动作）

### Step 1：新建快捷指令

1. iPhone 打开 **快捷指令**（Shortcuts）app → 右上角 **+** 新建
2. 顶部点名字 → 改成 **抖音收藏存档**
3. 顶部右上 **ⓘ 信息按钮**（i）→ 滑开 **用于"共享表单"**（Use with Share Sheet）
4. **共享表单类型**（Share Sheet Types）只勾 **文本**（Text）

### Step 2：添加 3 个动作

#### 动作 1 · 接收输入
- 搜索栏输 "**接收**"（Receive）→ 选 **「接收来自'共享表单'的输入」**（Receive Input from Share Sheet）
- 输入类型（Input Type）：**文本**（Text）

#### 动作 2 · 格式化日期
- 搜 "**格式化**"（Format）→ 选 **「格式化日期」**（Format Date）
- **日期**（Date）：**当前日期**（Current Date）
- **格式**（Format）：**自定**（Custom）
- **格式字符串**（Format String）：`yyyy-MM-dd_HHmmss`

#### 动作 3 · 存储文件
- 搜 "**存储**"（Save）→ 选 **「存储文件」**（Save File）
- **文件**（File）：拖入变量 **「快捷指令」输入**（Shortcut Input）
- **服务**（Service）：**iCloud Drive**
- **文件名**（File Name）：拖入变量 **已格式化的日期**（Formatted Date）+ 手动输入 `.txt`
- **目标路径**（Destination Path）：`/DouyinInbox/`
- ❌ 关闭 **询问存储位置**（Ask Where to Save）
- ❌ 关闭 **覆盖原文件**（Overwrite If File Exists）

### Step 3：完成

右上角 **完成**（Done）。

---

## 测试

1. 打开抖音 app → 任意视频 → 右下角 **↗ 分享**
2. 滑找 **抖音收藏存档**（找不到点"更多"启用它）
3. 点 → 应该秒回（无任何弹窗）
4. iPhone 打开 **Files** app → iCloud Drive → DouyinInbox → 应该看到一个 `.txt`
5. Mac 端几秒后自动处理，vault `MyBrain/raw/douyin-favorites/` 出 .md

如果想看 Mac 端在做啥，跑：

```bash
tail -f "$HOME/Library/Mobile Documents/com~apple~CloudDocs/DouyinInbox/logs/monitor.log"
```

---

## Phase 1 存量批量分享

setup 完成后，把现有抖音收藏夹几十条手动分享一遍：

1. 抖音 app → 我 → 收藏 / 喜欢
2. 一个个点开 → ↗ 分享 → 抖音收藏存档
3. ~5 秒/条 × 几十条 ≈ 5 分钟

之后看到喜欢视频直接点分享（取代点❤️收藏），pipeline 永久跑。

---

## 故障排查

| 现象 | 修复 |
|---|---|
| 分享菜单看不到 Shortcut | Shortcut 信息页 Share Sheet 没开；或 iPhone 重启 |
| Save File 报错 "找不到文件夹" | DouyinInbox 还没同步到 iPhone（等 30s 或重启 Files app） |
| Mac 端没拉到 | iCloud 同步慢，等 1-2 min；不行 `launchctl list \| grep douyin` 看 daemon |

---

## 备份方案（万一 Shortcut 真有问题）

完全 fallback：手动操作

1. 抖音 app → 分享 → **拷贝链接**
2. iPhone Files → iCloud Drive → DouyinInbox
3. 长按空白 → 新建文件 → `.txt` → 粘贴链接

效果一样。pipeline 同样能拉到。
