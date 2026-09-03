---
name: evidence-before-absence-claims
description: 用户质疑"是否改了我电脑的系统状态"时，必须用历史/日志证据回答，绝不能凭"我没执行写入命令的意图"下绝对结论
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_a25e7fbc-5adf-42ba-939a-836b65214cf3
---

2026-08-27 用户问"你是不是改了我本机的 BCD"。我当时先答"没有证据表明我改过"，被追问后才发现：①本会话曾在开发机上运行 tweak 的 Pester 测试和点源加载脚本，虽有 mock 防护但属于需要交代的事实；②用户自己的 PowerShell 历史里有 `bcdedit /set hypervisorlaunchtype off`、`/set vsmlaunchtype off` 等写入命令——真正的修改来源基本确定是用户手跑或更早工具，但这只能靠查证得出，不能开局就断言。

**Why:** 对系统状态的否定性结论（"X 没发生过"）比肯定性结论更容易出错；凭意图代替证据会被后续事实打脸，损害信任。
**How to apply:** 涉及"是否改过系统/文件"类质疑时：第一步只做只读取证（bcdedit/enum、注册表读取、备份 JSON 时间戳、PSReadLine 历史 `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`——注意 Documents 下旧路径不存在）；第二步如实区分"我执行过的写操作清单"与"无法归因的状态差异"；第三步才给结论。若此前说过绝对化表述，主动收回。相关项目背景见 [[project-security-audit-2026-08-25]]。
