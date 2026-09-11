---
name: workbuddy2api-hot-reload-and-rebrand-cleanup
description: workbuddy2api 调度策略改运行时热读（免重启）与改名遗留全面清理的交付记录（2026-09-11）
metadata:
  node_type: memory
  type: project
---

# workbuddy2api：调度热读 + 改名收尾（2026-09-11）

承接 `workbuddy2api-rebrand-and-dual-source.md`（品牌重构与双源拉取）。本文记录后续两个交付。

## 1. 多账号调度策略改为运行时热读（免重启）

**问题**：`rotate_mode` / `rotate_count` 原先经 CLI 启动参数传给内核，`argparse` 只在启动时解析一次 —— 用户在 GUI 切换策略后必须重启内核才生效。

**实现**（commit `92c3540`）：
- `converter.py` 新增 `load_app_settings()`：热读桌面端 `settings.json`，按 **mtime+size 签名缓存**（文件未变不重复读盘，变小开销可忽略）。
- `_get_rotator()` 改为每次请求现读：**优先级 settings.json > CLI 参数/环境变量**（后者降级为「settings.json 不可读时」的兜底默认值）。
- `proxy.rs` 从「仅非 off 时透传」改为**始终透传**参数（兜底用途）。
- `/api/rate_limit` 的 `rotation` 新增 `config_source` 字段：`hot`=已热加载 / `default`=回退兜底 —— 可观测运行态真源。
- 前端 `accounts.js` 保存提示由「需重启服务生效」改为「即时生效」，并回显内核运行态确认。
- 健壮性：非法 `rotate_mode` 归一为 `off`；`rotate_count` 规整为 ≥1；`settings.json` 缺失/损坏时优雅降级并沿用上次配置。

**验证**（用户重建后实测）：`rotation: { mode: failover, config_source: "hot", accounts_count: 2 }` —— 证明运行中的内核确实热读，而非走启动参数。

**通用经验**：桌面端 GUI 配置要「改完即生效」的字段，都应走「内核按 mtime 签名热读配置文件」模式（`model_settings.json` 已是此模式，本次把调度策略对齐）；CLI 参数保留为兜底而非唯一真源。

## 2. 项目改名 codebuddy2openai → workbuddy2api 的遗留清理（commit `db88e36`）

用户点名 three 项（plugin / 托盘显示 / 前端代码）+ 自查补充，逐项落地：

| 位置 | 处理 |
|---|---|
| 托盘 tooltip | 「CodeBuddy2OpenAI 桌面控制台」→「WorkBuddy2API 桌面控制台」 |
| 前端品牌区 | 侧栏 title「CodeBuddy / to OpenAI」→「WorkBuddy2API / OpenAI / Anthropic」 |
| HTTP User-Agent | `codebuddy2openai/2.0` → `workbuddy2api/2.0`（converter.py + auth.rs×2 + billing.rs） |
| 日志器名 | `codebuddy2openai.token_refresher` → `workbuddy2api.token_refresher` |
| 模块注释/头注 | proxy.rs / lib.rs 路径注释、main.js、style.css、agents.rs |
| 文档配置 | FRONTEND-SPEC.md、THIRD_PARTY_NOTICES.md、requirements.txt、package-lock.json、codex 示例 toml |

**环境变量兼容层（防升级后行为静默变化）**：
- Python `_env_compat(suffix)`：`WORKBUDDY2API_<X>` 优先 → `CODEBUDDY2OPENAI_<X>` 兜底。覆盖 13 项（KEY / LOG_LEVEL / LOG / LOG_PAYLOADS / USAGE_LOG / SCAN_ALL_USERS / REPAIR_STREAM_TOOLS / ROTATE_MODE / ROTATE_COUNT / MAX_CONCURRENCY / MIN_INTERVAL_MS / REFRESH_INTERVAL / REFRESH_THRESHOLD）。
- Rust `shared::env_compat(suffix)`：`WORKBUDDY2API_<X>` 优先 → `C2O_<X>` 兜底（PYTHON / CONVERTER）。
- 测试：新增 `tests/test_env_compat.py`（6 例，含「源码中不得再有裸读旧变量」的防回归扫描）。

**有意保留（非遗留）**：旧数据目录 `%LOCALAPPDATA%\codebuddy2openai` 与旧主题 key `codebuddy2openai.theme` 的回退读取（用户迁移期平滑）；上游署名 `HanHan666666/codebuddy2openai`（MIT 许可义务）。

**顺带修复**：目录改名导致工作区 `.venv` 的 uv trampoline 全部失效（`pytest.exe` 等报 `failed to canonicalize script path`）—— 用 `uv venv --allow-existing .venv` + `uv pip install --reinstall <pkgs>` 重建脚本层修复（python 本体不受影响）。

## 3. 交付状态

- 仓库 HEAD `9730200`（最后一条为 AGENTS.md 基线数字修正：pytest 205 / npm 32 / cargo 24），CI 全绿。
- 测试基线：Pytest **205** / Node **32** / Cargo **24** / Vite build / `cargo check` 全通过。
- 已由用户重新构建并验证：exe 内嵌新前端资源 hash 命中，`config_source: "hot"` 确认热读生效。

**Why:** 调度策略此前必须重启内核才生效，是用户实际痛点；改名后遗留散落 6 个技术层（前端/托盘/UA/日志器/文档/环境变量），只改仓库名与包名会留下静默行为差异。
**How to apply:** 该仓库改动前读 `AGENTS.md`（含 AppConfig 整对象覆盖写盘两条铁律、思考档位矩阵约束、风控 11128 机制）；配置类改动优先走「热读 + mtime 签名缓存」而非「重启生效」；改名/迁移类任务务必同步排查环境变量与数据目录的兼容回退，并保留上游署名。
