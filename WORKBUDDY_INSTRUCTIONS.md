# WorkBuddy 常驻指令

> **用途**：填入 WorkBuddy「设置 → 给 WorkBuddy 的指令」字段。该字段在每次对话与任务中默认生效。
> **版本**：2026-10-20 v1 ／ **分支**：`workbuddy`
> **边界**：只收录 WorkBuddy 特有的操作约束。风格类要求（中文、直接、结论优先、不复述过程）由 `SOUL.md` 每轮注入，此处不重复，避免稀释注意力。

---

## 指令正文（粘贴此段）

1. **记忆只进共享库**：持久事实（项目约定、环境事实、踩坑结论）一律写入
   `D:\ai coding\GitRepos\shared-agent-memory` 的 `main` 分支，当轮 commit 并 push。
   禁止在 WorkBuddy 工作区创建任何 `.md` 笔记、`memory` 目录或说明文档。

2. **该仓库必须停在 `main`**。只有修改 `skills/` 时才 `git checkout hermes`，改完立刻切回 `main`，
   并运行 `python scripts/check_memory_layout.py` 复核。
   注意：`checkout hermes` 会静默断开 `memories/topics` junction，而 `git status` 仍显示 clean。

3. **公开仓库写入前先脱敏**：机器路径一律用 `%USERPROFILE%` / `%LOCALAPPDATA%` / `$HOME`；
   不写真实密钥、账号、内网地址、代理端口。拿不准就留在本地。

4. **提交信息语言**：`shared-agent-memory` 用英文 conventional commit；
   用户自己的项目仓库用结构化中文（`修复:` / `完善:` / `文档:`）。

5. **网络**：直连 `github.com` / `api.github.com` / `raw.githubusercontent.com` 不可靠。
   git 用 `git -c http.proxy=http://127.0.0.1:<代理端口> ...`，curl 用 `curl -x http://127.0.0.1:<代理端口> ...`；
   **Node 原生 fetch 不读代理环境变量**，必须同时设 `NODE_USE_ENV_PROXY=1`。

6. **临时产物只放** `%TEMP%` 或 `D:\ai runtime\_quarantine\`，任务结束前清理干净：
   不留探针脚本、调试日志、`.bak` 备份。git 仓库里的文件不做手工备份，Git 就是版本控制。

7. **删除类操作先快照或隔离**到 `D:\ai runtime\_quarantine\`，不做不可逆删除；
   拿不准就先报告再动手，不要靠猜。

8. **涉及 Hermes 更新或桌面构建**时，先加载 `hermes-update-troubleshooting` skill。
   若 `hermes update` 回执 success 但 `Hermes.exe` 时间戳没变，说明打包失败，
   **不要重启桌面**，先查 pack 阶段的网络问题。

---

## 维护说明

- **改版流程**：在 `workbuddy` 分支编辑本文件 → 英文 conventional commit → push → 切回 `main` → 跑自检脚本。`workbuddy` 分支只承载本文件，从 `main` 长出，不做其它改动，便于 rebase。
- **`<代理端口>` 是占位符**：真实值只填在 WorkBuddy 设置字段里，不入公开库。本机实际端口记在 `main` 分支 `hermes-agent-install.md`。
- **第 2 条来自 2026-10-20 的实际事故**：为改 skill 而 checkout `hermes` 后未切回 `main`，junction 断开且 `git status` 全绿，属静默故障。
- **第 5 条来自同日事故**：`hermes update` 全绿但桌面未重建，根因是 `@electron/get` 拉 `SHASUMS256.txt` 时 Node fetch 未走代理，只报一句 `TypeError: fetch failed`。详见 `main` 分支 `hermes-update-workflow-and-benchmarks.md`。
- **第 8 条**与 `hermes-update-troubleshooting` skill 的深坑 16/17/18 对应。
