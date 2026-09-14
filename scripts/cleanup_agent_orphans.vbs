Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """%USERPROFILE%\.openviking\venv\Scripts\pythonw.exe"" ""%USERPROFILE%\AppData\Local\hermes\scripts\cleanup_agent_orphans.py"" --force", 0, False
