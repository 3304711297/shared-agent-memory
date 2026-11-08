---
name: hermes-terminal-shell-powershell-status
description: Hermes 终端无法锁定 PowerShell（terminal.shell 未实现）的能力现状、上游 PR/Issue 状态与本机推进记录
metadata:
  type: project
---

# Hermes 终端 shell：PowerShell 锁定能力现状（2026-11-08 核验）

## 结论

**当前无法把 terminal 的默认执行 shell 锁成 PowerShell** —— Windows 上仍是 bash（git-bash / MSYS）硬编码，且上游主干同样如此，升级 Hermes 解决不了。

## 取证（本机 + 上游主干双重核验）

- 本机 `v0.23.0+677.ga08f241`（upstream `a08f2418`，2026-11-07）：`hermes config get terminal` 无 `shell` 键；`hermes config get terminal.shell` 返回 `Config key not set`。
- `tools/environments/local.py::_find_bash()` → `pm/shell.py::bash()`：只解析 bash 候选（staged bundle → PATH → windows_bash_candidates → POSIX fallback），**无配置项、无环境变量覆盖**。
- terminal 工具 schema 仅 `command / background / timeout / pty`，没有 shell 或方言参数。
- 上游 `main`（`21ae0e1238`，2026-11-08 拉取）同样缺失；`git grep terminal.shell` 在 `website/docs/` 零命中。本机落后 main 555 个 commit，但拉满也无此功能。

## 上游推进状态

| 条目 | 状态 | 要点 |
|---|---|---|
| PR #85027 | OPEN（2026-08-13 开，最后一次提交 2026-09-01） | 新增 `terminal.shell: bash \| pwsh`，仅 Windows 本地后端**前台同步**执行；`background` / `pty` fail closed，PowerShell 函数/别名/模块/runspace 不持久，只保 cwd + 环境变量 |
| Issue #36929 | OPEN | 「Windows 支持 PowerShell 作为终端 shell」的原始需求单 |
| Issue #149731 | OPEN（2026-11-05 开） | 提议 `terminal.backend: pwsh`（跨平台，目标 pwsh 7+ 而非 Windows PowerShell 5.1） |

## 为何不能本地打补丁

- PR base `18a76be1`（2026-09-01）已落后 main **37,031 个 commit**，其绿灯 CI 也是 2026-09-01 跑的。
- 实测 `git apply --check --3way`：`tools/environments/local.py`、`tools/terminal_tool.py`、`tools/approval.py`、`agent/prompt_builder.py` 与相关测试文件全部冲突，属需人工判断的 rebase 而非机械重放。
- `hermes update` 会覆盖任何本地改动，每次升级都要重打，维护成本远高于收益。

## 本机已做的上游推进（2026-11-08）

- **PR #85027 评论**：https://github.com/NousResearch/hermes-agent/pull/85027#issuecomment-6717680242
  量化 `_WINDOWS_BASH_SHELL_HINT` 成本（1361 字符 / 约 340 tokens × 每个 Windows 会话常驻）；指出真正的阻塞是分支陈旧而非无人需要；给出实测冲突清单；向维护者提两个范围问题（前台先行 vs 等 background/PTY 一起；`terminal.shell` vs `terminal.backend` 哪个是方向）。
- **Issue #149731 评论**：https://github.com/NousResearch/hermes-agent/issues/149731#issuecomment-6717680850
  先提提案排序风险（两个提案抢同一议程、必须先明确架构目标与第一增量），再补 5 条该 issue 未覆盖的硬需求：background/PTY 必须可用、状态持久化契约要写清、approval 必须 PowerShell 感知否则会 fail open（`Remove-Item -Recurse -Force`、`Stop-Process -Force`、`ri`/`del`/`rm` 别名、`-Fo` 缩写）、强制 UTF-8 否则非英文 locale 下 CJK 输出与路径乱码、跨平台范围与「对象 vs 字节流」对结果截断的影响。
- **未结承诺**：两处留言都承诺「rebase 后可在一台 Windows 11 + pwsh 7.6.9 环境跑 `windows_only` 测试并验证前台/后台/PTY 路径」。若 PR 出现 rebase 或维护者回应，需跟进履诺。

## 现阶段的可用折中

bash 继续作传输层，Windows 原生语义显式写成 `pwsh -NoProfile -Command '...'`；代价是该子进程**不继承**跨调用持久化的 cwd 与环境变量（每次都是新进程）。

**Why:** 用户明确认为 git-bash 难用、希望锁定 PowerShell；误答「可以，去 config set」会直接报错，误答「打补丁就行」会引入每次升级都腐坏的本地分叉，两者都在浪费用户时间。

**How to apply:** 被问到 Hermes 终端 shell 可配置性时，先给「未实现 + 上游 PR 未合并 + 升级无效」三段式结论和取证，再给显式 `pwsh` 折中写法；不要指导 `hermes config set terminal.shell`，不要本地 backport；PR rebase 后按承诺去测试。
