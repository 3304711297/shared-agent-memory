@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ==============================================
echo   能力组件看门：本地全量检查（远端 + 内置插件）
echo ==============================================
for /f "delims=" %%i in ('gh auth token 2^>nul') do set GH_TOKEN=%%i
python scripts\check_capability_upstream.py > "%TEMP%\capwatch-out.txt" 2>&1
type "%TEMP%\capwatch-out.txt" | findstr /C:"has_updates=true" >nul
if !errorlevel!==0 (
    set N=
    for /f "delims=" %%n in ('gh issue list --state open --label capability-watch --json number --jq ".[0].number" 2^>nul') do set N=%%n
    if defined N (
        echo 更新已存在 Issue !N!，刷新正文...
        gh issue edit !N! --body-file capability-report.md
    ) else (
        echo 创建新 Issue...
        gh issue create --title "🔔 [Capability Watch] 本地能力组件有上游更新" --body-file capability-report.md --label capability-watch
    )
    echo [OK] 存在待跟进项，详见 GitHub Issue。
) else (
    set N=
    for /f "delims=" %%n in ('gh issue list --state open --label capability-watch --json number --jq ".[0].number" 2^>nul') do set N=%%n
    if defined N gh issue close !N! --comment "✅ 清单已与上游一致，自动收口。"
    echo [OK] 无待跟进项。
)
echo.
pause
