@echo off
rem Hermes Google Quota Monitor Background Daemon
cd /d "C:\Users\<username>\AppData\Local\hermes\desktop-plugins\token-stats"
"C:\Users\<username>\.openviking\venv\Scripts\pythonw.exe" fetch_quota.py --serve
exit /b 0
