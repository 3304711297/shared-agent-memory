---
name: mediatek-mt7922-bluetooth-service-disabled
description: 主机自换 MediaTek MT7922 网卡与联发科蓝牙服务 MTKBTSVC 禁用实证
metadata:
  type: feedback
---

# 主机 MediaTek MT7922 网卡与蓝牙服务禁用说明

记录机械革命极光 X 主机自换无线网卡后的驱动与蓝牙服务配置事实。

## 事实与配置

1. **硬件更换**：主机已自换 **MediaTek MT7922 Wi-Fi 6E 与蓝牙适配器**。
2. **联发科蓝牙服务 (MTKBTSVC)**：
   - 对应路径：`C:\Windows\System32\mtkbtsvc.exe`；
   - 对应系统服务名：`MTKBTSVC`（MediaTek Bluetooth Service Application）；
   - **作用与缺陷**：该服务对日常蓝牙连接（无线键鼠如 MCHOSE G9 PRO、蓝牙耳机等）无实际用处（Windows 自带的 `bthserv` 原生蓝牙栈完全接管且正常工作），且联发科配套服务旧版存在严重的句柄泄漏卡顿 Bug。
3. **状态与建议**：
   - 本机实测已将 `MTKBTSVC` 设为 **Disabled（已禁用/未运行）**；
   - 系统所有日常蓝牙设备连接与休眠唤醒均完全正常；
   - 保持禁用即可，切勿再次开启。

**Why:** 联发科官方配套服务存在句柄泄漏隐患且对日常连接冗余，Windows 原生蓝牙服务已足够稳定。

**How to apply:** 遇到系统蓝牙服务巡检或启动项优化时，确认 `MTKBTSVC` 保持 Disabled，不要将其恢复自启。
