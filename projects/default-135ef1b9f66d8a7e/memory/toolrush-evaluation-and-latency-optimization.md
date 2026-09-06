---
name: toolrush-evaluation-and-latency-optimization
description: OnlyTerp/toolrush (ToolRush v2) 针对 Hermes 本地工具调用延迟的深度技术评估、加速机制剖析与暂不安装观望决策
metadata:
  type: project
---

# OnlyTerp/toolrush 深度技术评估与观望决策（2026-09-06）

## 一、 项目背景与核心定位
- **仓库地址**：`https://github.com/OnlyTerp/toolrush`（作者 OnlyTerp / terpbot，v2.0 架构）
- **核心定位**：解决高速模型（如 Gemini Flash / GLM Flash）在 Hermes Agent 下面临的“工具调用税”（tool-call tax）。
- **痛点分析**：当模型生成速率（TPS）极高时，系统总延迟瓶颈常常转向 Hermes 本地执行层的调度开销（重复 spawn 进程、Git-Bash 包装层多次重定向、序列化 RPC 往返）。

## 二、 ToolRush v2 四大加速机制与实测指标
1. **原生安全文件读取 (`read_file`)**：
   - 耗时：255.23 ms → 4.44 ms（**57.5x 提速**）。
   - 原理：绕过多重 shell 管道包装，复用上游带边界保护与权限审查的原生 Windows 读取器。
2. **温启动持久化 Shell (`terminal`)**：
   - 耗时：285 ms → 12.1 ms（**23.6x 提速**）。
   - 原理：持久化单个 Bash 会话，流式管道传输，执行完成前原子提交环境快照，支持进程树快速取消。
3. **原生 ripgrep 直连传输 (`search_files`)**：
   - 耗时：183–455 ms → 27–97 ms（**4.7~6.8x 提速**）。
   - 原理：直接调用原生 `rg.exe` argv 传输，修复 JSON 尾部乱码及换行边界，保留标准 `.gitignore` 规则。
4. **批量并行只读 RPC (`parallel`)**：
   - 耗时：108 ms → 53 ms（**2.1x 提速**）。
   - 原理：在 `execute_code` 中注入 `from hermes_tools import parallel`，单次 RPC 支持 1~16 个只读操作在最多 4 个 worker 间并发执行。
5. **跨版本防护 (Update Survival)**：
   - 基于 AST 检查在内存中动态修补约 25 个函数；当检测到上游 Hermes 源码变更破坏 AST 时，执行 Fail-Closed 熔断并回退至官方原生逻辑。

## 三、 用户环境适配性与决策权衡
1. **契合点**：
   - 用户主力模型为 `gemini-3.8-flash`，模型端 TPS 极高；
   - 用户使用 Windows 11 环境，进程冷启动（spawn）开销本身就显著高于 POSIX；
   - 用户在代码工程与重构任务中重度推崇并发和自动化脚本扫描。
2. **核心顾虑与暂不安装原因**：
   - **高侵入性 Monkey-Patch**：运行时动态替换 Hermes 内部 25 个核心调度与执行函数。本地已有 context7、desktop-commander、serena、superpowers 以及自研 `token-stats` 插件，在复杂的 Windows PTY/编码边界下极易产生不可预期的相互干扰；
   - **真实体感瓶颈差异**：优化仅针对 Local Tool I/O（节约数十至数百毫秒），但真实端到端耗时大头仍在于模型首字生成（TTFT）、网络 RTT 以及 Exa 联网检索；
   - **单人实验性维护**：目前生态较新（55 Stars），未合并至 Hermes 官方主干，上游频繁发版容易陷入频繁降级或维护成本。
3. **最终决策**：
   - **暂不安装到主环境**，保持基线纯净稳定；
   - 留存为底层加速技术方案储备，待未来处理大规模本地静态代码分析或超高频本地 CLI 调度瓶颈时再按需开启。

**Why:** 用户评估了该底层优化项目的收益与潜在系统稳定性风险，决定暂不引入侵入性补丁，但需在记忆库完整留档以备后续参考。
**How to apply:** 后续若遇到 Hermes 本地工具执行耗时显著阻碍任务、或用户再次提起 ToolRush 时，调阅本文档的技术指标与接入风险，在不破坏现有插件和网关稳定性的前提下审慎决策。
