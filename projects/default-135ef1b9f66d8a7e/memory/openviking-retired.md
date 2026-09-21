---
name: openviking-retired
description: OpenViking 本地向量记忆库的退役记录与架构回归决策
metadata:
  type: project
---

# OpenViking 退役记录（2026-09-21 用户拍板）

本地曾运行 OpenViking（volcengine/OpenViking）作为 Hermes 的二级语义检索记忆层。**2026-09-21 用户拍板彻底退役并物理卸载。**

## 退役理由

1. **显存冲突（决定性因素）**：本地向量 Embedding 服务（llama-server 跑 Octen-Embedding-0.6B）常驻占用 **6.57GB 显存**。主机为 RTX 4070 Laptop **8GB**，剩余不到 1.6GB，导致 ComfyUI 生图与本地大模型都无法施展。
2. **双记忆库维护成本**：内置 `MEMORY.md`/`USER.md` + OpenViking 两套存储需要双向同步、灾备、索引维护，心智负担与流程成本过高。
3. **检索收益可替代**：长篇工程笔记用 ripgrep（`search_files`）按关键字精确检索已足够，且零 GPU、零常驻进程、无需向量模型。

## 已执行的移除动作

| 项目 | 处置 |
|---|---|
| OpenViking 虚拟环境 `%USERPROFILE%/.openviking/` | 物理删除（含 venv、data、ov.conf） |
| 向量模型 `D:\HermesModels\Octen-Embedding-0.6B-Q8_0.gguf` | 物理删除（释放 0.60GB） |
| 灾备仓 `D:\openviking-backup` + 私有仓 3304711297/openviking-backup | 目录物理删除（远端私有仓保留作历史归档） |
| Windows 计划任务 `OpenVikingDailyBackup` | Unregister |
| Git hooks（shared-agent-memory / youshouldknow 的 post-commit、post-merge） | 删除 |
| 守护脚本 lazy_gateway / openviking_service / sync_shared_memory_openviking / sync_ysk_openviking / ov_shim 系列 / backup_sync.cmd / start|stop_openviking.vbs | 删除 |
| Hermes `config.yaml` 的 `memory.provider: openviking` 与 `memory.openviking` 段 | `hermes config unset` 移除 |
| token-stats 插件的 OVLM 联动（后端 375 行 + 前端 OvlmCard 卡片 + `/ovlm` 路由） | 删除 |
| `agent_guard.py` / `cleanup_agent_orphans.py` 的 OpenViking 停机逻辑及对 OV venv pythonw 的依赖 | 拆除，改指向 Hermes venv |

## 迁移回共享库的知识

退役前盘点了 OpenViking 抽取的 851 个记忆文件（128 实体 / 634 事件 / 89 偏好），将共享库缺失的独有事实融回真源：
- `mediatek-mt7922-bluetooth-service-disabled.md`（主机自换 MT7922 网卡 + 联发科蓝牙服务 MTKBTSVC 禁用实证）

其余内容为共享库已有卡片的重述或已被覆盖的过期条目，不重复收录。

## 现行架构（单一真源）

- **高频必带事实** → 内置 `memories/MEMORY.md` / `memories/USER.md`（每轮全量注入）
- **低频长文** → Git 共享库 `shared-agent-memory`（`memories/topics` junction），`search_files` 精确检索
- 无第三处存储、无常驻向量服务、无 GPU 占用

## 回退路径

需要时可从 PyPI 重装：`uv venv` 或 `python -m venv` + `pip install openviking`；向量模型可从 ModelScope/HF 重新拉取 Octen-Embedding-0.6B。但需重新评估 8GB 显存的冲突问题——若要重启，建议将 Embedding 改到 CPU 运行。

**Why:** 8GB 笔记本显存是稀缺资源，任何常驻 GPU 服务都会挤占本地生图与大模型的能力上限；而记忆检索的工程价值可用零成本的 ripgrep 达成。

**How to apply:** 未来若再遇到「为某个辅助能力常驻一个占用数 GB 显存的服务」的提案，先按本案例的判据权衡（显存机会成本 > 该能力的边际收益）。
