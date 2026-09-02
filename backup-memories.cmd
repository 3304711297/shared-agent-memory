@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo       ZCode 记忆库一键同步与备份
echo ==============================================
git status --short
echo.
git add .
git commit -m "backup: 自动备份最新记忆 (%date% %time%)"
git push origin main
echo.
echo [OK] 备份完成！
pause
