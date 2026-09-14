Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "python ""%USERPROFILE%\AppData\Local\hermes\scripts\openviking_service.py"" stop", 0, False
