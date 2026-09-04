@echo off
rem Hermes Google Quota Monitor Background Daemon
cd /d "C:\Users\VOS-User\AppData\Local\hermes\desktop-plugins\token-stats"
"C:\Users\VOS-User\AppData\Local\hermes\hermes-agent\venv\Scripts\pythonw.exe" fetch_quota.py --serve
exit /b 0
