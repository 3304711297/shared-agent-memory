"""token-stats — Google/Antigravity 配额监控后端插件。

后端 API 随 Hermes 桌面端后端进程自动挂载（dashboard api 机制），
桌面应用启动即服务在，退出即停 —— 无需计划任务或独立守护进程。
同时注册 /quota 交互式会话斜杠命令。
"""

from __future__ import annotations


def _get_api():
    try:
        from .dashboard import plugin_api
        return plugin_api
    except ImportError:
        import sys
        from pathlib import Path
        p = Path(__file__).resolve().parent / "dashboard"
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
        import plugin_api
        return plugin_api


def _handle_slash(raw_args: str) -> str:
    api = _get_api()
    force = "refresh" in raw_args.lower()
    data = api.fetch_google_quota(force=force)
    return api.format_quota_markdown(data)


def register(ctx) -> None:
    """Register slash command /quota inside CLI and chat sessions."""
    try:
        ctx.register_command(
            "quota",
            handler=_handle_slash,
            description="查看当前模型配额状态与本地网关详情（支持 /quota 或 /quota refresh）",
        )
    except Exception:
        pass
