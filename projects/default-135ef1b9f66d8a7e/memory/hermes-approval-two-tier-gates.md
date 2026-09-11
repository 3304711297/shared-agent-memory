---
name: hermes-approval-two-tier-gates
description: Hermes 审批弹窗分两层——approvals.mode 管危险命令，security.protected_instruction_files 管指令文件写入，后者 even under --yolo 绕不过；本机已关闭后者（2026-09-11 用户拍板）
metadata:
  node_type: memory
  type: feedback
---

# Hermes 审批弹窗的两层门禁（务必分清）

用户抱怨「每次都要手动允许，不然卡住进度」时，先辨清是**哪一层**在拦——两层独立、开关不同、绕不过的程度也不同。

## 门禁一：`approvals.mode`（危险 shell 命令）

- 管什么：被判为破坏性的 shell 命令（`rm -rf`、`git reset --hard` 等）。
- 三档：`smart`（默认，辅助 LLM 评估风险）/ `manual`（总是问）/ `off`（等同 `--yolo`，直接放行）。
- 绕过方式：`--yolo`、`HERMES_YOLO_MODE=1`、或 `hermes config set approvals.mode off`。
- 本机现状：`off`。

## 门禁二：`security.protected_instruction_files`（指令文件写入）★ 常见误判点

- 管什么：往**指令文件**写入 —— `AGENTS.md` / `CLAUDE.md` / `SOUL.md` / `.cursorrules`（basename 匹配、**任意目录**、大小写不敏感），外加项目级 `<repo>/.hermes/config.yaml`（仅限直接父目录为 `.hermes`）。
- **关键：这一层独立于 `approvals.mode`，源码注释明写 "Writes ALWAYS require human approval — even under --yolo"，且 fail-closed**（无人类通道时拒绝，不静默放行）。所以把 `approvals.mode` 设成 `off` 后弹窗照旧 —— 这正是用户此前踩的坑。
- 覆盖的工具有两个向量：`write_file` / `patch`（写入守卫 `tools/file_tools_write_guards.py`）。UI 呈现为工具行下方的内联审批条（「运行 Ctrl⏎ / 拒绝 Esc / 命令 ^」），不是模态弹窗。
- 审批语义：**单次操作审批，无「本会话放行」也无「始终允许」**（approval payload 带 `pattern_key: protected_instruction_file`，刻意不走可持久化的 `_run_approval_gate`）。
- 开关：
  ```bash
  hermes config set security.protected_instruction_files false   # 关闭（本机已执行）
  hermes config set security.protected_instruction_extra_patterns '["*.mdc", "*.instructions.md"]'  # 反向：追加受保护 glob
  ```
- 生效：`load_config()` 按**文件签名（mtime+size）缓存**，改完即热生效，**无需重启**。
- 匹配实现细节：同时比对规范化路径与 realpath（防符号链接绕过），`~/.hermes` 自身被显式排除（它有独立守卫）。

## 本机决定（2026-09-11，用户拍板）

用户选择**全局关闭**门禁二，理由是频繁手点审批拖慢进度：

```bash
hermes config set security.protected_instruction_files false
# ✓ Set security.protected_instruction_files = False
```

- 已实测验证：往 `AGENTS.md` 写入不再弹窗、直接落盘（测试文件已清理）。
- **副作用（需知悉）**：任何 agent（含被提示注入后的）可在无确认的情况下改写本项目及任意目录的 `AGENTS.md` 等指令文件——即「agent 改自己行为准则」的最后一道闸被移除。用户明确接受此风险。
- 恢复命令：`hermes config set security.protected_instruction_files true`。
- 注意：该开关同时覆盖项目级 `<repo>/.hermes/config.yaml` 的写保护。

**Why:** 两层门禁的开关分离，且第二层刻意不可绕过（连 yolo 都不行）——不知道这点就会反复出现"我明明关了审批怎么还弹"的误判，浪费排障时间。
**How to apply:** 用户吐槽审批弹窗时，先看弹窗内容：是 shell 命令 → 查 `approvals.mode`；是 `<write to AGENTS.md>` 这类 → 查 `security.protected_instruction_files`。改动前告诉用户第二层的安全含义（保护 agent 自身行为准则），并按本机惯例列候选+代价等其拍板。用 `hermes config set` 改，绝不手编 config.yaml。
