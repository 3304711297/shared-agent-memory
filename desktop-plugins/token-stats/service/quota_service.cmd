@echo off
rem Hermes Google Quota Monitor Background Daemon
cd /d "%USERPROFILE%\AppData\Local\hermes\desktop-plugins\token-stats"
"%LOCALAPPDATA%\hermes\tools\guard-venv\Scripts\pythonw.exe" fetch_quota.py --serve
exit /b 0
