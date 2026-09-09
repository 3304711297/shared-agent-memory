# 会话收尾双推送铁律

**Why:** 2026-09-09 遗漏案例——一次会话收尾时只推了记忆库（shared-agent-memory main + hermes 分支），忘记归档会话转录到 hermes-sessions。流程与脚本都完备（`upload_session.py` 自带「先推远端、校验 HEAD==origin/main、通过才删本地」安全闸），纯粹是执行遗漏，把「推记忆库」误当成收尾全部。

**How to apply:** 用户说「删除/结束会话」或任务全绿收尾时，**两件事都要做，缺一不可**：

1. **会话转录归档**（私有库，含未脱敏真实路径）
   ```bash
   cd "$HOME/GitRepos/hermes-sessions"   # 或实际克隆位置
   python tools/upload_session.py --latest            # 仅归档
   ```
   **⚠️ 铁律（2026-09-09 两次事故定案）：严禁 `--delete`，会话由用户自行删除。**
   Agent 跑 `--delete` 删掉活跃会话的 state.db 行 → 桌面端写入失败 →
   "session storage could not be written" 回合中止 + 历史丢失（需从归档回灌）。
   脚本已加 30 分钟活跃保护，但 Agent 侧根本不该带 `--delete`。
   误删后的修复工具：`tools/restore_session.py`（整会话回灌）、
   `tools/merge_session_back.py`（并回已重建会话）。
   校验远端落盘：`git rev-parse HEAD` 必须等于 `git ls-remote origin main`。

2. **记忆库推送**（公开库，写入前必须脱敏）
   - 共享内容 → `git -C "$HOME/.zcode/cli/memories" push origin main`
   - Hermes 专属 → `git -C "$LOCALAPPDATA/hermes" push origin hermes`

最后再确认一次「记忆库 push 成功 ≠ 会话已归档」——两者是不同仓库、不同内容、不同隐私级别。顺序建议先归档会话（含完整上下文），再推记忆库。

## 【2026-09-09 二次纠偏】归档必须放最后一步，且必须复读校验

**问题**：把归档放进「三步收尾闭环」的第 3 步，导致归档之后产生的收尾对话（约 12 条）全部漏传，用户需二次提醒才补上。实测：归档后 `--check` 立即报「新增 2 条未归档」——**只要会话还在继续，归档永远追不上**。

**新铁律**：
1. **归档是收尾的最后一个动作**，放在所有回复、推送、CI 确认**之后**；
2. 归档后**必须复读一次** `python tools/upload_session.py --latest --check`，确认返回「已归档且最新」；若报有未归档，立即补传再复读，直到 0 增量；
3. 告知用户「可以删会话了」这句话本身会产生新消息，**必须在复读确认之后**再说，说完若产生了新对话需再补传一次。

**脚本增强（2026-09-09 已实装）**：`upload_session.py` 新增
- `--check`：只检查不上传，返回码 0=已最新 / 2=有待归档；
- **增量检测**：从 `manifest.jsonl` 读上次归档条数，与本地实际条数比对，打印 `[delta] ⚠️ 上次归档(HH:MM)后新增 N 条消息 (X → Y)，本次为补传`；
- 幂等可重复执行，重复归档同会话只是追加 manifest 记录与覆盖产物，不会损坏数据。

**口径注意**：`sessions.message_count` 与 `messages` 表实际行数**不一致**（实测 386 vs 765），脚本取的是 `messages` 表实际行数，以此为准。
