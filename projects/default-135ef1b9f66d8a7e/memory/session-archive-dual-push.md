# 会话收尾双推送铁律

**Why:** 2026-09-09 遗漏案例——一次会话收尾时只推了记忆库（shared-agent-memory main + hermes 分支），忘记归档会话转录到 hermes-sessions。流程与脚本都完备（`upload_session.py` 自带「先推远端、校验 HEAD==origin/main、通过才删本地」安全闸），纯粹是执行遗漏，把「推记忆库」误当成收尾全部。

**How to apply:** 用户说「删除/结束会话」或任务全绿收尾时，**两件事都要做，缺一不可**：

1. **会话转录归档**（私有库，含未脱敏真实路径）
   ```bash
   cd "$HOME/GitRepos/hermes-sessions"   # 或实际克隆位置
   python tools/upload_session.py --latest            # 仅归档
   python tools/upload_session.py --latest --delete   # 归档并清本地
   ```
   校验远端落盘：`git rev-parse HEAD` 必须等于 `git ls-remote origin main`。

2. **记忆库推送**（公开库，写入前必须脱敏）
   - 共享内容 → `git -C "$HOME/.zcode/cli/memories" push origin main`
   - Hermes 专属 → `git -C "$LOCALAPPDATA/hermes" push origin hermes`

最后再确认一次「记忆库 push 成功 ≠ 会话已归档」——两者是不同仓库、不同内容、不同隐私级别。顺序建议先归档会话（含完整上下文），再推记忆库。
