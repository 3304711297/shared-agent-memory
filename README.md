# shared-agent-memory 记忆真源 🧠

Hermes Agent 的跨会话长期记忆真源与运维工具链。**记忆只有一份**：物理存放在本仓库 `projects/<project-id>/memory/`（`main` 分支检出），Hermes 通过 NTFS 目录联接直读，读写零同步成本。

> 🌐 **公开仓库**。2026-09-05 由私有转公开，转公开前已全分支扫描并脱敏本机网关密钥。仓库内置卫生门禁：CI 每次 push 都扫描本机用户名硬编码路径与凭据泄露。
>
> 📜 **沿革**：本库最初由 Hermes 与 ZCode 双 Agent 共用（记忆目录曾位于 `%USERPROFILE%\.zcode\cli\memories`）。ZCode 已于 2026-09-09 退役，本库自此成为 **Hermes 单一真源**，`zcode` 分支仅作历史归档保留。

---

## 🌿 分支模型

| 分支 | 内容 |
|------|------|
| `main`（默认） | **记忆真源（唯一）**：`projects/<project-id>/memory/*.md` 专题记忆 + `MEMORY.md` 索引 |
| `hermes` | 仅 Hermes 专属：home 白名单备份（`SOUL.md`、原生 `USER.md` / `MEMORY.md`、技能与插件配置）；**不含共享 topics** |
| `zcode` | 历史归档（ZCode 已退役，不再写入） |

**Hermes 如何读共享库**：`%LOCALAPPDATA%\hermes\memories\topics` 是一个 NTFS junction，指向本仓库检出目录下的 `projects/<project-id>/memory`；Hermes 原生记忆系统透明读写同一份文件，不存在「两边各存一份」的问题。

**归属判断**：Hermes 通用记忆（跨任务、跨会话复用）→ `main`；仅 Hermes 本机专属（配置白名单备份）→ `hermes` 分支。谁改动谁在当轮结束前推送，无需他人提醒。

---

## 🗂 项目布局

```text
shared-agent-memory/
├── projects/                      # 记忆库正文（main 分支中的真源）
│   ├── default-*/memory/          # 主记忆库：专题记忆卡片 + MEMORY.md 索引
│   └── <project-id>/memory/       # 按项目分区的专属记忆
├── scripts/
│   ├── check_hygiene.py           # 卫生扫描：本机用户名路径 / GitHub 与 AWS 凭据 / 私钥块
│   ├── check_capability_upstream.py  # 能力组件看门（本地解析 + 远程上游比对）
│   └── check_skill_drift.py       # 技能漂移检查：已装技能 vs 上游同名技能
├── capability-inventory.json      # 能力清单：已装技能 / 插件及其来源与版本
├── skills-provenance.json         # 技能来源台账：安装渠道与准入记录
├── watch-capability.cmd           # 本地跑能力看门（--full 强制全量上游比对）
├── watch-skill-drift.cmd          # 本地跑技能漂移检查
├── backup-memories.cmd            # 一键备份提交推送
└── .github/workflows/             # CI：卫生门禁 + 能力清单校验 + 远程上游每日看门
```

> 记忆的物理位置即本仓库 `projects/` 目录。若本地检出中出现仓库根的 `topics/` 目录，那是早期布局的本地残留（已被 `.gitignore` 排除、不参与跟踪），记忆真源始终是 `projects/<project-id>/memory/`。

---

## 🔄 更换电脑 / 重装系统恢复指南

```powershell
# 1. 安装 Git 并完成 GitHub 登录（gh auth login）
# 2. 克隆记忆库到任意位置（示例路径，实际可自定义）：
git clone -b main https://github.com/3304711297/shared-agent-memory.git "$HOME/GitRepos/shared-agent-memory"

# 3. 重建 Hermes 侧 junction，把 <MEMORY_DIR> 替换为上一步克隆目录下的
#    projects/<project-id>/memory（主记忆库为 default-* 项目）：
cmd /c mklink /J "%LOCALAPPDATA%\hermes\memories\topics" "<MEMORY_DIR>"
```

恢复后重启 Hermes 即自动读取全部记忆。

---

## 🛡️ 卫生门禁与看门体系

- **卫生门禁**（CI 每次 push / PR 到 `main` 时运行）：扫描全部跟踪文件，命中本机用户名硬编码路径、GitHub / AWS 凭据或私钥块即失败退出。写入本库前请自行跑一遍：
  ```bash
  python scripts/check_hygiene.py
  ```
- **能力看门**：`capability-inventory.json` 与 `skills-provenance.json` 记录已装的技能 / 插件及来源；远程上游由 CI 每日定时比对并托管到 Issue，本地也可手动巡检：
  ```bash
  watch-capability.cmd          # 本地检查（默认只查本地专属组件）
  watch-capability.cmd --full   # 强制跑全量上游比对
  ```
- **技能漂移检查**：只回答「已安装的技能是否落后于上游同名技能」，不构成自动更新依据：
  ```bash
  watch-skill-drift.cmd
  ```
- **脱敏纪律**：本库为公开仓库，写入前必须泛化机器用户名与本机物理路径（用 `%USERPROFILE%` / `%LOCALAPPDATA%` / `$HOME`），凭据与密钥一律不得入库。

---

## ⚡ 日常备份

记忆变动后（任一 Agent 均可执行）：

```bash
cd "<克隆目录>"
git add -A && git commit -m "memory: <简述>" && git push origin main
```

或直接运行本目录的 `backup-memories.cmd`。Hermes 专属变动则在其 home 仓库推 `hermes` 分支。
