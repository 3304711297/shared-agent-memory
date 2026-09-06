Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe"" ""C:\Users\VOS-User\AppData\Local\hermes\scripts\cleanup_agent_orphans.py"" --force", 0, False
