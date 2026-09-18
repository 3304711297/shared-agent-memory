"""Hermes pre_tool_call 命令改写插件模板（零依赖，fail-open）。

用途：在工具执行【前】改写 terminal 命令，从源头减少超长输出。
注意：Hermes 无法改写工具输出，只能改写命令——见 SKILL.md 的「Hermes 没有任何钩子能改写工具输出」。

安装（三步，缺一不可）：
  1. 放插件目录：$HERMES_HOME/plugins/cmd-rewrite/__init__.py
     （本机 $HERMES_HOME=%LOCALAPPDATA%\\hermes；不要用 ~/.hermes，那只是残留壳）
  2. 写同目录 plugin.yaml：
         name: cmd-rewrite
         version: "0.1.0"
         hooks:
           - pre_tool_call
  3. 启用：hermes plugins enable cmd-rewrite
     （非 bundled 插件会被问是否授予 allow_tool_override —— 本插件【不需要】该特权，选 No。
       它只改 args，不替换内置工具。）

验证纪律：装完必须实测一条命令，确认工具回显的命令真的变了。"插件已加载"不等于生效。
"""

import logging
import re
import shutil
import subprocess

logger = logging.getLogger(__name__)

# ── 改写规则表 ────────────────────────────────────────────────────────────────
# 每条: (编译好的正则, 替换模板)。只处理能被单条命令安全替换的情形。
_RULES: list[tuple[re.Pattern, str]] = [
    # CI 轮询：gh run watch 会每 3-10 秒刷全屏，实测单条可达 33.5K 字符。
    # 替换为一次问询，只出终态 JSON。
    (
        re.compile(
            r"^gh\s+run\s+watch\s+(?P<id>[0-9]+)\s+"
            r"(?:-R|--repo)\s+(?P<repo>[\w.\-]+/[\w.\-]+)\s*$"
        ),
        "gh run view {id} -R {repo} --json status,conclusion,jobs "
        "--jq '{{status,conclusion,jobs:[.jobs[]|{{name,conclusion}}]}}'",
    ),
]

# 复合命令 / heredoc / 重定向一律不碰 —— 与 rtk 的保守策略一致（改写会改变语义）。
_UNSAFE = re.compile(r"(\||&&|\|\||;|>|<|\$\(|`|\n)")


def register(ctx):
    """注册钩子；任何失败都静默放行（fail-open）。"""
    try:
        ctx.register_hook("pre_tool_call", _pre_tool_call)
    except Exception:
        logger.warning("cmd-rewrite: hook registration failed", exc_info=True)


def _pre_tool_call(tool_name=None, args=None, **_kwargs):
    """只处理 terminal 的 str 型 command；返回官方 modify 指令，否则 None 放行。"""
    try:
        if tool_name != "terminal" or not isinstance(args, dict):
            return None
        command = args.get("command")
        if not isinstance(command, str) or not command.strip():
            return None
        stripped = command.strip()
        if _UNSAFE.search(stripped):
            return None

        for pattern, template in _RULES:
            m = pattern.match(stripped)
            if not m:
                continue
            new_command = template.format(**m.groupdict())
            if new_command == stripped:
                return None
            logger.info("cmd-rewrite: %s -> %s", stripped, new_command)
            # 返回值式改写：官方路径，不依赖 dict 别名语义。
            return {"action": "modify", "args": {"command": new_command}}
    except Exception:
        logger.warning("cmd-rewrite: rewrite failed, passing through", exc_info=True)
    return None


# ── 可选：把 rtk 当后端（有则用，无则跳过） ─────────────────────────────────────
# 若本机装了 rtk，可改用它的注入规则库，避免自己维护规则表：
#
def _rtk_rewrite(command: str) -> str | None:
    if not shutil.which("rtk"):
        return None
    try:
        r = subprocess.run(
            ["rtk", "rewrite", command],
            shell=False, capture_output=True, text=True, timeout=2,
        )
    except Exception:
        return None
    # 0/3 = 有改写；1/2 = 正常跳过
    if r.returncode in (0, 3):
        out = r.stdout.strip()
        return out or None
    return None
