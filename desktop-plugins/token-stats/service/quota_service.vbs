Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c ""%USERPROFILE%\AppData\Local\hermes\desktop-plugins\token-stats\service\quota_service.cmd""", 0, False
Set WshShell = Nothing
