Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Users\<username>\.openviking\venv\Scripts\pythonw.exe"" ""C:\Users\<username>\AppData\Local\hermes\scripts\cleanup_agent_orphans.py"" --force", 0, False
