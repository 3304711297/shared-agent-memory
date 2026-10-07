Set objArgs = WScript.Arguments
If objArgs.Count > 0 Then
    rawUrl = objArgs(0)
    Set objShell = CreateObject("WScript.Shell")
    psScript = objShell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\hermes\scripts\invoker\screenbox_invoker.ps1"
    cmd = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File """ & psScript & """ """ & rawUrl & """"
    objShell.Run cmd, 0, False
End If
