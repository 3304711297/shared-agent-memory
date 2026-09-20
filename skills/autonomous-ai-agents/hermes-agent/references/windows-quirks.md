# Windows-Specific Quirks

Hermes runs natively on Windows (PowerShell, cmd, Windows Terminal, git-bash
mintty, VS Code integrated terminal). Most of it just works, but a handful
of differences between Win32 and POSIX have bitten us — document new ones
here as you hit them so the next person (or the next session) doesn't
rediscover them from scratch.

### Input / Keybindings

**Alt+Enter doesn't insert a newline** — Windows Terminal (and mintty) grab it
for fullscreen before prompt_toolkit sees it. Use **Ctrl+Enter** instead (the
CLI binds it to newline on Windows; raw Ctrl+J does the same, harmlessly).
To inspect how your terminal reports a keystroke, run
`python scripts/keystroke_diagnostic.py` from the repo root.

### Config / Files

**HTTP 400 "No models provided" on first run** — `config.yaml` was saved with
a UTF-8 BOM (Notepad does this). Re-save as UTF-8 without BOM;
`hermes config edit` writes correctly.

### `execute_code` / Sandbox

**WinError 10106** from the sandbox child process — it can't create an
`AF_INET` socket. Root cause is usually Hermes's env scrubber dropping
`SYSTEMROOT`/`WINDIR`/`COMSPEC` (Python's `socket` needs `SYSTEMROOT` to find
`mswsock.dll`), not a broken Winsock LSP. The `_WINDOWS_ESSENTIAL_ENV_VARS`
allowlist in `tools/code_execution_env.py` covers it; if you still hit it,
echo `os.environ` inside an `execute_code` block to confirm `SYSTEMROOT` is set.

### Testing on Windows

`scripts/run_tests.sh` is POSIX-only (expects `.venv/bin/activate`); the
Hermes-installed `venv/Scripts/` has no pip/pytest (stripped for size).
Install pytest into a system Python and run directly (the repo no longer
uses pytest-xdist; the canonical runner does per-file subprocess isolation,
which the POSIX-only wrapper handles):

```bash
"/c/Program Files/Python311/python" -m pip install --user pytest pyyaml
export PYTHONPATH="$(pwd)"
"/c/Program Files/Python311/python" -m pytest tests/foo/test_bar.py -v --tb=short
```

(POSIX-only tests need skip guards — see the cross-platform guard list in
`references/contributor-guide.md`.)

### Path / Filesystem

**Line endings.** Git may warn `LF will be replaced by CRLF`. Cosmetic — the
repo's `.gitattributes` normalizes. Don't let editors auto-convert committed
POSIX-newline files to CRLF.

**Forward slashes work almost everywhere.** `C:/Users/...` is accepted by
every Hermes tool and most Windows APIs. Prefer forward slashes in code
and logs — avoids shell-escaping backslashes in bash.

### Shell selection on Windows

**The terminal backend is hardwired to bash** — `_find_bash()` in
`tools/environments/local.py` only probes bash candidates
(`HERMES_GIT_BASH_PATH` → bundled portable Git → Git for Windows → PATH);
there is no PowerShell branch, and config.yaml's `terminal` section has no
shell key (verified against v0.21.2).

**PowerShell scenarios** (registry, services, event logs, admin cmdlets):
call `pwsh -NoProfile` (or `powershell` for 5.1-only modules) explicitly
from bash. `-NoProfile` skips the user profile — deterministic, faster,
clean output. For CJK output, prefix
`[Console]::OutputEncoding=[Text.Encoding]::UTF8` or text piped back to
bash arrives as GBK mojibake (inherited console codepage); verified on
pwsh 7.6.6 and Windows PowerShell 5.1.

**Native Windows CLIs from git-bash: use SINGLE-slash flags** (2026-09-18
verified on `tasklist`). MSYS path conversion is disabled in this
environment, so a flag like `/FI` is NOT rewritten and must be passed as
`/FI "IMAGENAME eq x.exe"`; the classic MSYS workaround `//FI` is what
actually breaks — Windows tools parse `//FO` / `//FI` as an *invalid*
`/` option ("无效参数/选项 - '//FO'"), while `tasklist /FO CSV /FI "..."`
runs clean. Don't blind-copy `//`-style flags from MSYS-era notes; test the
single-slash form first. When output only needs filtering, let bash do it
(`tasklist | grep -i foo`) and skip Windows flag syntax entirely.

### Spawning a detached child that the USER can watch

When your app hands off work to a long-running script (installer, updater,
build) and the user is supposed to see progress, the spawn call is the whole
game. Measured on this host (2026-09-20, four variants, PowerShell + pwsh,
both via physical paths and Store aliases):

| Creation flags | Script runs | Console window user can see |
|---|---|---|
| `DETACHED_PROCESS` (0x8) | ❌ not a single line | 0 |
| `CREATE_NO_WINDOW` (0x08000000) | ✅ | **0** — runs fine, user sees nothing |
| `CREATE_NEW_CONSOLE` (0x10) | ✅ | 1 |
| `cmd /d /s /c start "" /min <pwsh> -File ...` | ✅ | **1, minimized** |

`DETACHED_PROCESS` kills console-subsystem programs before they run any
script (the classic "update flashed and vanished, no log, no state file"
bug). `CREATE_NO_WINDOW` is the trap that follows: the script now works, so
it looks solved — but the user has no feedback surface at all.

The fix is Hermes's own: `wrapHandoffForDetachedConsole()` in
`apps/desktop/electron/updater-process.ts` (≈L149-158) returns
`{command:'cmd.exe', args:['/d','/s','/c','start','','/min', command, ...args]}`.
Its comment: "`start` allocates the child its own (minimized) console and
fully detaches it from cmd.exe, which exits immediately." From Rust:
`Command::new("cmd.exe")` with those args and **no `creation_flags`** —
setting any hides the console again.

**Allocating the console is only half the fix.** If the script's log
function writes only to a file (`Write-Host` count = 0), that minimized
window stays blank and the user still sees no progress. Hermes's
`Write-HandoffLog` also calls `Write-Host $line`. When a user reports "I
can't see the progress", count `Write-Host` occurrences first — don't
tunnel on spawn flags alone.

**How to verify window visibility** (a child process cannot observe its own
console windows): from the parent, enumerate with `EnumWindows` +
`GetClassNameW == "ConsoleWindowClass"` and diff the PID set before/after
spawning. `GetWindowLongW(hwnd, GWL_STYLE) & 0x20000000` = `WS_MINIMIZE`
confirms it really is minimized. ⚠️ One sample right after spawn can read 0
because the window is not up yet — sample at least twice (~2s apart) before
concluding anything.

**Paths with spaces must be exercised explicitly.** The quoting chain
(Rust arg → `cmd /s` → `start` → child) has historical bugs at spaces, and
the usual `pwsh` locations do NOT contain spaces (WindowsApps alias), so a
plain test proves nothing. Build a spaced path with
`mklink /J "<dir with space>" "<real dir>"` and assert the script received
its arguments untruncated (this repo lives at `D:\ai coding\...`, so it is a
real exposure, not a hypothetical).

