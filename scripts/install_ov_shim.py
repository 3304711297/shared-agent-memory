#!/usr/bin/env python3
"""Install the openviking-server PATH shim: user PATH reorder + .bat writer."""
import ctypes
import os
import winreg

SHIM_DIR = r"C:\Users\VOS-User\.openviking\shim-bin"
PYW = r"C:\Users\VOS-User\.openviking\venv\Scripts\pythonw.exe"
OV_SHIM_PY = r"C:\Users\VOS-User\AppData\Local\hermes\scripts\ov_shim_server.py"


def main() -> None:
    os.makedirs(SHIM_DIR, exist_ok=True)

    bat_lines = [
        "@echo off",
        f'start "" /B "{PYW}" "{OV_SHIM_PY}" %*',
        "exit /b 0",
    ]
    bat_path = os.path.join(SHIM_DIR, "openviking-server.bat")
    with open(bat_path, "w", encoding="ascii") as f:
        f.write("\r\n".join(bat_lines))
    print("shim bat written:", os.path.exists(bat_path))

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ) as k:
        current, reg_type = winreg.QueryValueEx(k, "Path")

    parts = [p for p in current.split(";") if p and p.lower() != SHIM_DIR.lower()]
    new_path = SHIM_DIR + ";" + ";".join(parts)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "Path", 0, reg_type, new_path)

    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    res = ctypes.c_long()
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(res)
    )
    print("PATH head:", new_path[:140])


if __name__ == "__main__":
    main()
