@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ==============================================
echo   能力组件看门：本地专属检查（内置插件 + 配置守卫）
echo   提示：18 项远程上游由 CI 每日定时比对并托管 Issue
echo   若需强制本地跑全量上游比对，请运行: watch-capability.cmd --full
echo ==============================================
set MODE=--local-only
if "%1"=="--full" set MODE=

if "%MODE%"=="" (
    for /f "delims=" %%i in ('gh auth token 2^>nul') do set GH_TOKEN=%%i
    python scripts\check_capability_upstream.py > "%TEMP%\capwatch-out.txt" 2>&1
    type "%TEMP%\capwatch-out.txt"
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
) else (
    python scripts\check_capability_upstream.py --local-only
    echo.
    echo [OK] 本地专属检查完成（本地模式不改写云端 Issue，保持与 CI 对齐）。
)
echo.
pause
