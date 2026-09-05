# shared-agent-memory 双 Agent 共享记忆库 🧠

Hermes Agent 与 ZCode 共用的跨端长期记忆库。**共享内容只有一份**：物理存放在 ZCode 记忆目录（本仓库 `main` 分支检出），Hermes 通过 NTFS 目录联接直读，切换 Agent 零同步成本。

> 🌐 公开仓库（2026-09-05 由私有转公开；转公开前已全分支扫描并脱敏本机网关密钥）。分支架构 2026-09-05 重构，取代旧的「zcode/hermes 双分支互为镜像」模型。

---

## 🌿 三分支模型

| 分支 | 内容 | 物理位置 |
|------|------|----------|
| `main`（默认） | **双端共享记忆库**（唯一真源）：`projects/default-*/memory/*.md` 专题记忆 + `MEMORY.md` 索引 | `C:\Users\VOS-User\.zcode\cli\memories\` |
| `zcode` | 仅 ZCode 专属、不与 Hermes 共享的内容（占位，暂空） | 按需检出 |
| `hermes` | 仅 Hermes 专属：home 白名单备份（SOUL.md、原生 USER.md/MEMORY.md、技能/插件配置）；**不含共享 topics** | `%LOCALAPPDATA%\hermes\` |

**Hermes 如何读共享库**：`%LOCALAPPDATA%\hermes\memories\topics` 是指向本仓库记忆目录的 NTFS junction，hermes 原生记忆系统透明读写同一份文件。

**归属判断**：两端都该知道的 → main；仅 ZCode 用 → zcode；仅 Hermes 用 → hermes。谁改动谁在当轮结束前推送，无需提醒。

---

## 🔄 更换电脑 / 重装系统恢复指南

```powershell
# 1. 安装 Git 并完成 GitHub 登录（gh auth login）
# 2. 克隆共享记忆库到 ZCode 记忆目录（检出 main）：
git clone -b main https://github.com/3304711297/shared-agent-memory.git "$HOME\.zcode\cli\memories"
# 3. 重建 Hermes 侧 junction（hermes home 就位后执行）：
cmd /c mklink /J "%LOCALAPPDATA%\hermes\memories\topics" "C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory"
```

恢复后重启 ZCode / Hermes 即自动读取全部记忆。

---

## ⚡ 日常备份

共享库变动（任一 Agent）：

```bash
git -C "C:/Users/VOS-User/.zcode/cli/memories" add -A && git -C "C:/Users/VOS-User/.zcode/cli/memories" commit -m "memory: <简述>" && git -C "C:/Users/VOS-User/.zcode/cli/memories" push origin main
```

或直接运行本目录的 `backup-memories.cmd`。Hermes 专属变动则在其 home 仓库推 `hermes` 分支。
