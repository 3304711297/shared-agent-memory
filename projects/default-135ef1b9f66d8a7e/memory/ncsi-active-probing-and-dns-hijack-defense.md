---
name: ncsi-active-probing-and-dns-hijack-defense
description: 2026-07-21 中国移动 DNS 劫持复盘与 Windows NCSI 主动探测防御体系（机制武器化、EnableActiveProbing、DoH/TUN 治本方案及 tweak/ysk 双仓协同）
metadata:
  type: reference
---

# 2026-07-21 运营商 DNS 劫持与 Windows NCSI 机制防御

## 一、 事件经过与攻击机制复盘

- **时间与范围**：2026 年 7 月 21 日，中国移动西南节点网络用户发生大面积异常。
- **用户表象**：设备开机或联网瞬间，系统自动调起默认浏览器并全屏跳转至非法赌博/博彩网站。用户多误判为电脑中毒或遭遇流氓驱动。
- **底层攻击机理**：
  1. **NCSI 主动探测逻辑**：Windows 网络位置感知服务（`NlaSvc`）内置网络连接状态指示器（NCSI）。网卡联网后自动向 Local DNS 解析 `www.msftconnecttest.com` 并请求 `connecttest.txt` 探针（期望 `200 OK` 且内容为 `Microsoft Connect Test`）。
  2. **Captive Portal 武器化利用**：黑客攻击移动递归 Local DNS 实施投毒，将探测域名解析至受控 IP 并返回 HTTP 302/307 重定向。Windows 判定网络处于机场/酒店等**公共 Wi-Fi 强制门户认证（Captive Portal）**环境，由系统底层机制**自动唤起默认浏览器打开该重定向地址**，造成大面积流氓弹窗。

## 二、 三层防御体系架构

1. **第一层：系统级触发阻断（治标 · 阻断弹窗）**
   - 注册表路径：`HKLM\SYSTEM\CurrentControlSet\Services\NlaSvc\Parameters\Internet`
   - 目标键值：`EnableActiveProbing = 0` (REG_DWORD)
   - 作用：彻底停用 Windows 主动网络探针，彻底切断系统自动弹窗触发链。
   - 副作用与权衡：连接需 Web 认证的公共热点时无法自动弹出认证页（需手动在浏览器输入任意 IP 如 `1.1.1.1` 触发）；任务栏网络图标极罕见情况下可能短暂显示地球标/感叹号，但不影响实际联网。
2. **第二层：网络层换源（局部缓解）**
   - 路由器/网卡手动指定公共受信 DNS（114.114.114.114、223.5.5.5 等）。
   - 局限性：无法抵御运营商骨干层的 **UDP 53 旁路镜像劫持或透明代理**。
3. **第三层：传输加密与虚拟化分流（治本 · 消除温床）**
   - 启用 **DoH / DoT 加密 DNS**，或通过代理客户端（如 Karing / sing-box）配置 **TUN 模式 Fake-IP 虚拟化分流**。
   - 本地协议栈不发出任何明文 UDP 53 数据包，彻底抹除运营商劫持与本地投毒的生存空间。

## 三、 工程落地与双仓闭环（2026-09-07）

- **`youshouldknow` 知识库**：
  - 更新 `docs/网络通信/Windows网络栈优化原则.md`，新增第九节「运营商 DNS 劫持与 Windows NCSI 探测机制防御」；
  - 阐明 NCSI 探针与 Captive Portal 机制武器化机理，给出三层防御指南；
  - 本地 `--strict` 校验通过，提交 `aab8708` 并推送至 `main`。
- **`tweakbyjie` 调优脚本**：
  - 在 `Modules/Registry.ps1`（Part 1 子项 2 系统行为优化）中收录 `EnableActiveProbing=0` 及对应后验断言；
  - 在 `Modules/Backup.Registry.ps1` 快照清单中登记该键，保证「4. 按备份恢复」可无损还原系统默认值；
  - 更新 `tools/knowledge.lock.json` 指向 ysk 最新 SHA；
  - 124 项 Pester 单元测试与 48 项 Cross-Repo Coverage 审计 100% 全绿，提交 `fa35557` 并推送至 `main`。

相关记忆：[[desktop-projects-tweak-youshouldknow]] [[cross-repo-coverage-audit]] [[user-windows-environment]]
