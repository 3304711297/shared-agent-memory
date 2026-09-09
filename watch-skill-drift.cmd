@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo ==============================================
echo   技能漂移检查（已装技能 vs 上游同名技能）
echo   语义：只回答「我装的技能是否落后于上游」
echo   新技能发现请查 skill-plugin-resources.md 索引库
echo ==============================================
echo.
for /f "delims=" %%i in ('gh auth token 2^>nul') do set GH_TOKEN=%%i
python scripts\check_skill_drift.py
echo.
echo ==============================================
echo 说明：
echo   - 「需人工评估」= 上游有实质改动，考虑是否跟进
echo   - 「本地增强」= 本地定制（如中文强触发词），禁止被上游覆盖
echo   - 「上游无同名」= 自研技能或上游已下架
echo ==============================================
echo.
pause
