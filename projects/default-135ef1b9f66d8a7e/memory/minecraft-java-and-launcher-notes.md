---
name: minecraft-java-and-launcher-notes
description: MC 版本↔Java 对应、各启动器 Java 识别差异、CurseForge 整合包 downloadUrl 为 null 的坑与跨启动器搬运法
metadata:
  type: reference
---

# Minecraft Java 与启动器要点（2026-11 实证）

## 一、MC 版本 ↔ 最低 Java

| MC 版本 | 最低 Java |
|---|---|
| 1.12 – 1.16.5 | 8 |
| 1.17 – 1.17.1 | 16 |
| 1.18 – 1.20.4 | 17 |
| 1.20.5 – 1.21.11 | 21 |
| 26.1 起（2026-03-24 起正式改版本号方案） | 25 |

26.1 是第一个**不混淆**的版本，模组生态随之重构（Fabric Loader 0.19、NeoForge `26.1.x` beta），1.21.11 及以前的模组需重新编译。

## 二、启动器识别 Java 的方式不同（踩坑高频点）

| 启动器 | 读取来源 | 版本号容忍度 |
|---|---|---|
| **PCL CE** | PE 资源 `FileVersionInfo.FileVersion`，再 `Version.Parse` | 只接受 **2–4 段**；5 段直接抛 `ArgumentException` |
| **HMCL** | 执行 JVM 读 `java.version` 属性 | 只取主版本号 |
| **Axolotl** | 优先读 JDK 目录 `release` 文件的 `JAVA_VERSION`，失败才跑 JVM 读 `java.version`；`extract_java_version()` 用 `split('.').next()` | 只取主版本号，段数无关 |

**Azul Zulu 的陷阱**：Zulu 文件名 `zulu21.54.109-ca-jdk21.0.13.0.3-win_x64` 里，`21.54.109` 是 Azul bundle 版本（3 段），`21.0.13.0.3` 才是它承载的 JDK 版本。这一轮 OpenJDK 21 PSU 的完整版本串本身就是 5 段（Oracle Release Notes 原文 `21.0.13.0.3+1`），Zulu 如实写进 PE 资源，于是 PCL 解析必崩。同期 Temurin `21.0.13` 的 FileVersion 是 4 段 `21.0.13.0`，不受影响。

**PCL 侧状态（2026-11-10）**：`PeHeaderParser` 已改为 `FileVersion.Split('.').Take(4)`（PR #3796），`DialogService` 的 `UiDispatcher.Invoke` 改为 `Post`（PR #3788），两处已进 dev；**正式版 v2.15.1 尚未包含**（release 停在 2026-10-20）。

**规避手段**：Zulu 之类 5 段 JDK 放到**盘根之下、名字不含关键词的一层**（如 `D:\Tools\JAVA`），PCL 的 `DefaultPathsScanner` 只把「盘根目录下名字含 java/jdk/jre/azul/zulu/oracle/open/temurin 等关键词的文件夹」纳入搜索根，扫不到就不会触发放置即死锁。

## 三、CurseForge 整合包：`downloadUrl` 为 null 会被 PCL 整包丢弃

- CurseForge 对**未开启第三方分发**的文件返回 `downloadUrl: null`，但 CDN 路径仍可取到。
- **PCL CE**：`CompFile.Available => !string.IsNullOrEmpty(FileName) && DownloadUrls.Count != 0`，没有兜底 → `_BuildCurseForgeDownloadFiles` 里逐条 `continue`，最终 0 个文件，却仍提示「启动成功」（游戏变成纯加载器）。实证：All the Mods 11 0.14.0-beta 的 305 个模组全部被跳过，`下载模组` 加载器 0 ms 结束。**上游 issue #3449，2026-11 仍未修**。
- **HMCL 有兜底**（`CurseForgeRemoteAddonRepository.downloadUrl()`）：`downloadUrl == null` 时拼 `https://edge.forgecdn.net/files/{id/1000}/{id%1000}/{fileName}`，所以同一整合包 5.8 分钟装出 298 个 jar / 812 MB。
- **跨启动器搬运法**：先用 HMCL 装同一整合包，再把 `mods/*.jar` 整个复制到 PCL 实例的 `mods/`。前提是两边加载器参数一致（比对实例 json 的 `mainClass` / fancymodloader / accesstransformers / `javaVersion`），一致则 PCL 可直接启动，无需重下。

## 四、本机现状（2026-11）

- JDK：Eclipse Temurin 8 / 16 / 17 / 21 / 25，位于 `D:\JAVA\temurin-*`，全部 4 段 FileVersion，PCL 可识别。
- ATM11（MC 26.1.2 + NeoForge 26.1.2.126）：298 个 mod 由 HMCL 下载后复制进 PCL 实例。
