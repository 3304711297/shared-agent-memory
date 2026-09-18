# rtk-ai/rtk 与 decolua/9router 评估（2026-09-18）

**Why:** 用户 @url 引入这两个仓库问「适合我吗」。结论是 **rtk 不装**，理由建立在自机实测数据上而非项目宣称。这条结论无其他持久落点（skill 里只记了平台机制），故单列。

## rtk-ai/rtk —— 不装

**实测数据（自机 84 会话 / 4299 条唯一工具结果 / 7.96M 字符工具输出）：**

| 口径 | 数值 |
|---|---|
| terminal 占全部工具输出 | 40.3%（3.21M 字符） |
| **rtk 能接管的**（严格按文档化子命令） | **132 条 / 0.33M 字符 = terminal 的 10.3%** |
| 按 rtk 宣称节省折算 | ≈24.6 万字符 = **全部工具输出的 3.1%** |

**不可接管的构成**：`gh run watch`（128K，rtk 无此子命令）、78% 的 terminal 调用是复合命令（`&&`/`|`/`;`/重定向，rtk 明确跳过）、`git diff` 单条 52K、占 12.6% 体积的 python 小脚本输出 41K（rtk 对 python 无 filter）。

**三条反对理由**：
1. **杠杆量级不对**：`background_review` 一项曾占 cache_read 的 37.5%（剔除后每调用均值 -22.8%），`proactive_prune` 至今为 0 —— 3% 的 rtk 相比之下不值一提。
2. **注入点错位**：rtk 改命令、省输出字节；而自机工具结果实测平均重发 3.75 次才是计费口径，它省的 3% 在重发里仍只是 3%。
3. **工作流已天然规避**：本机规则用 `read_file`/`search_files`，terminal 只跑构建/git/进程 —— 而 rtk 的核心卖点正是 `cat`/`grep`/`ls`/`find`（本机各 1-15 次）。rtk 自己也承认 Claude 内置 Read/Grep/Glob 绕过 hook。

**唯一值得回看的场景**：CI 轮询（`gh run watch` 是最大单类输出）—— 但改用命令级改写更精准，见下。

## 真正有效的替代（已实施）

**`tool_output.max_bytes: 8000`**（原默认 50000，本机已配并登记 `capability-inventory.json`）：

| max_bytes | 省掉 | 占 terminal |
|---|---|---|
| 50000（原） | 5.9 万字符 | 1.9% |
| **8000** | **117.6 万字符** | **36.6%** |

无损：溢出部分 tee 到 `%LOCALAPPDATA%/hermes/cache/terminal-output/*.log`，路径随结果返回。**改后需重启桌面端**（该值按进程缓存）。

**命令级改写**：`gh run watch <id> -R <repo>` → `gh run view <id> -R <repo> --json status,conclusion,jobs --jq '{status,conclusion,jobs:[.jobs[]|{name,conclusion}]}'`（33.5K → 几十字符）。模板见 hermes-agent skill 的 `templates/pre_tool_call_rewrite_plugin.py`。

## decolua/9router —— 已做源码级勘查（结论待裁决）

**仓库事实（2026-09-18 实测）**：29255 stars / 5400 forks / 2144 open issues / MIT / 当天仍在推送（`pushed_at=2026-09-18T11:32`）。

**定位**：JS/Next.js 本地 LLM 网关（`localhost:20128`），把各 CLI 工具统一指向它，做格式翻译 + 三级 fallback + 配额追踪 + 多账号轮询。**与本机 EasyCLIProxyAPI(18080) + WorkBuddy2API(8787) 生态位重合**。

### 三个 token saver 的真实成分（读源码得出，非 README 宣称）

| 宣称 | 实际实现 | 关键事实 |
|---|---|---|
| **RTK Token Saver**（默认开） | **JS 移植版 rtk 过滤器**，跑在**请求层** | 不是调 rtk 二进制，是把 rtk 的 filter 逻辑用 JS 重写。peek `tool_result` 前 1KB 自动选 filter：`git-diff`/`git-status`/`grep`/`find`/`ls`/`tree`/`dedup-log`/`smart-truncate`/`read-numbered`/`search-list`。失败即静默保留原文（fail-open） |
| **Headroom Token Saver**（可选） | **外部 Python 包** `headroom-ai`（`chopratejas/headroom`），9router 只是个进程管理器（`src/lib/headroom/process.js` 负责 spawn/pid/log） | ⚠️ **默认端口 8787 —— 与本机 WorkBuddy2API 正面撞车**。v0.37.0、Apache-2.0、Beta；依赖重（litellm + tiktoken + ast-grep-cli + opentelemetry）。可注入 `HEADROOM_URL` 改地址 |
| **Caveman Mode / Ponytail** | **提示词注入**，不是压缩 | Caveman 注入穴居人语提示（省输出 token）；**Ponytail 就是你已在用的那个 skill** |

### 本机实测：这块蛋糕有多大

| 口径 | 数值 |
|---|---|
| 成熟请求里 `tool_result` 占比 | **中位 47.1% / 均值 40.3% / P90 90.7% / 峰值 93.7%**（n=67，≥20K 字符的请求） |
| headroom 过滤器可覆盖的工具族 | **79.1%**（terminal 38.6% + read_file 27.2% + search_files 7.2% + patch 6.2%） |
| 无对应 filter 的 | 20.9%（execute_code 8.9%、skill_view 3.3%、web_* 等） |

⇒ **请求层压缩的天花板是 `tool_result` 那 47%**，而其中约 79% 落在 headroom 的 filter 族内。这比 rtk 命令层的 3.1% 高一个数量级。

### 待裁决的问题（下一会话）

1. **是否替换现有双反代**？本机已有 EasyCLIProxyAPI(18080) + WorkBuddy2API(8787) 承担同一职责，9router 是"更重的同件事"（Next.js 全家桶 + 2144 open issues）。
2. **能否只摘取 token saver 部分**而不换整个网关？RTK Token Saver 是纯 JS 模块，理论上可独立复用。
3. **headroom 是否值得单独用**（不经 9router）？它是独立 Python 包 + CLI，可直接 `headroom proxy --port <非8787>`，对任意上游生效。
4. **端口冲突**：若启用 headroom，必须改端口或改 WorkBuddy2API。
5. 与已实施的 `tool_output.max_bytes: 8000`（命令/输出层，省 36.6% terminal）是否重叠、可否叠加。

**建议评估方式**：按 rtk 同样口径——先量化收益（已有上表），再验实现（读源码/本地起实例抓包），最后才谈替换。


## 上游关联

PR **NousResearch/hermes-agent#106399**（`tool_output.tool_overrides`，per-tool spillover 阈值）已提交实证 review 并挂 CI issue 守望（`pr-merge-watch.yml`）。合并后可为单工具配更低 spillover 阈值 —— 与 `max_bytes` 是不同层（spillover 落盘 vs 输出截断），二者互补。
