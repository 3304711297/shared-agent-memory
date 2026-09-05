@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo   shared-agent-memory 共享记忆库一键备份 (main)
echo ==============================================
git status --short
echo.
git add .
git commit -m "memory: 自动备份最新共享记忆 (%date% %time%)"
git push origin main
echo.
echo [OK] 共享库已推送到 main 分支（ZCode 专属内容请走 zcode 分支，Hermes 专属走 hermes 分支）
pause
