"""config-guard dashboard plugin — 本地配置守卫 API, mounted at /api/plugins/config-guard/.

Serve the gateway:startup hook's check result (last-result.json) to the
desktop statusbar chip. Zero network, zero subprocess — plain file read of
~/.hermes/hooks/config-guard/last-result.json, written by the
gateway:startup hook after every gateway boot (incl. desktop updates).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

RESULT_FILE = Path(
    os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
) / "hooks" / "config-guard" / "last-result.json"


def _hermes_home() -> Path:
    home = os.environ.get("HERMES_HOME")
    return Path(home) if home else Path.home() / ".hermes"


@router.get("/result")
async def get_result():
    """Return the latest guard result written by the gateway:startup hook."""
    path = _hermes_home() / "hooks" / "config-guard" / "last-result.json"
    if not path.exists():
        return JSONResponse({"exists": False, "ok": None, "problems": [], "detail": [
            "- ⏳ 尚无检查结果：hook 会在网关启动（含更新后重启）时自动写入。"
        ]})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["exists"] = True
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse({"exists": False, "ok": None, "error": f"{type(e).__name__}: {e}",
                             "problems": [], "detail": [f"- ⚠️ 结果文件损坏：{e}"]})
