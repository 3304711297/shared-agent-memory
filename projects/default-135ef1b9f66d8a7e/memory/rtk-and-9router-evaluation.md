# rtk-ai/rtk 与 decolua/9router 评估（2026-09-18）

**Why:** 用户 @url 引入这两个仓库问「适合我吗」。结论是 **rtk 不装、9router 不用**，理由建立在自机实测数据、代码实现排查与缓存架构验证上。这条结论无其他持久落点（skill 里只记了平台机制），故单列。

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

## decolua/9router —— 裁决：不采用（0 收益，高维护负债，强退行风险）

**仓库事实（2026-09-18 实测）**：29255 stars / 5400 forks / 2144 open issues / MIT。

**定位**：JS/Next.js 本地 LLM 网关（`localhost:20128`），把各 CLI 工具统一指向它，做格式翻译 + 三级 fallback + 配额追踪 + 多账号轮询。**与本机 EasyCLIProxyAPI(18080) + WorkBuddy2API(8787) 生态位重合**。

### 三个 token saver 的真实成分（读源码得出，非 README 宣称）

| 宣称 | 实际实现 | 关键事实 |
|---|---|---|
| **RTK Token Saver**（默认开） | **JS 移植版 rtk 过滤器**，跑在**请求层** | 不是调 rtk 二进制，是把 rtk 的 filter 逻辑用 JS 重写（`open-sse/rtk/`）。peek `tool_result` 前 1KB 自动选 filter。针对传统终端纯文本，无法妥善处理 Hermes 的原生结构化 JSON 与带行号格式。失败即静默保留原文（fail-open） |
| **Headroom Token Saver**（可选） | **外部 Python 包** `headroom-ai`（`chopratejas/headroom`），9router 只是个进程管理器 | ⚠️ **默认端口 8787 —— 与本机 WorkBuddy2API 正面撞车**。依赖重（litellm + tiktoken + ast-grep-cli + opentelemetry）。默认 `--mode cache` 仅压单轮 Delta；若压历史（`--mode token`）会击穿上游 Prefix Cache；CCR 假工具篡改上下文 |
| **Caveman Mode / Ponytail** | **提示词注入**，不是压缩 | Caveman 注入穴居人语提示（省输出 token）；**Ponytail 就是本机已有的 skill** |

### 本机实测天花板与 5 个核心问题裁决（2026-09-19 最终拍板）

| 口径 | 数值 |
|---|---|
| 成熟请求里 `tool_result` 占比 | **中位 47.1% / 均值 40.3% / P90 90.7% / 峰值 93.7%**（n=67，≥20K 字符的请求） |
| headroom 过滤器可覆盖的工具族 | **79.1%**（terminal 38.6% + read_file 27.2% + search_files 7.2% + patch 6.2%） |
| 无对应 filter 的 | 20.9%（execute_code 8.9%、skill_view 3.3%、web_* 等） |

1. **不替换现有双反代（18080 + 8787）**：
   - `EasyCLIProxyAPI (18080)`：极轻 Go 原生反代，专精 Antigravity (Gemini 主力)，带零配额感知、两账号轮询与 1h sticky 会话绑定。
   - `WorkBuddy2API (8787)`：自研维护的 Tauri v2 桌面客户端，承载账号池配额、积分、调度策略热读 `settings.json` 与双向协议桥接。9router 根本无法承载这套业务控制台。
   - 9router 是常驻 200~500MB+ 内存的 Next.js 全家桶，2144 open issues，引入只会增加巨量维护负债与退行风险。
2. **不剥离复用 RTK 纯 JS 模块**：
   - 自机遵守 Skill-First / Tool efficiency，终端绝不用 `cat/grep/find/ls`，全走原生 `read_file`、`search_files`、`patch`。
   - RTK 对 JSON 结构和带行号文本几乎无法识别（fail-open，压缩率 <2%）；若被 `smart-truncate` 误伤折叠行号，将直接导致 `patch` 锚定失败。
3. **不单独接入 headroom-ai**：
   - 击穿缓存：主力模型 Gemini 3.8 Flash（Antigravity）依赖前缀缓存降本增效，历史消息压缩导致 Prefix Cache 命中率归零，成本反增；
   - 假工具污染：Headroom 的 CCR 依赖注入 `headroom_retrieve` 假工具，破坏 Agent 原生工具流与代码还原。
4. **端口冲突处理策略**：
   - 若未来任何临时实验测试，坚持「第三方外来工具避让」，使用 `--port 8788`，严禁改动已绑定的 WorkBuddy2API (8787)。
5. **与 `tool_output.max_bytes: 8000` 关系**：
   - `max_bytes: 8000` 已经在管道源头直接截断 36.6% 超大终端输出（自动落盘保真），留给后置压缩的边际收益微弱；截断后的内容更易导致请求层压缩器语法解析失败而 fail-open，两者无叠加必要。

### 扩展裁决：反代 ZCode 的生态位澄清

- **本质差异**：9router 是「聚合路由网关」（不产出 Token，自带无效/有毒压缩）；而反代 ZCode（`TriDefender/zcode-api` / SOP）是「临时上游 Token 供给源」（智谱官方活动真实放水，如周末 3 亿 GLM-5.3-Flash）。
- **质量对比**：ZCode 走官方高速通道，直连低延迟，GLM-5.3 代码质量高；纯透传 `/v1/chat/completions` 不篡改系统 Prompt 和工具调用，体验远优于 9router 的公共免费池。
- **定位原则**：ZCode 反代维持既定 SOP（战备型活动羊毛：平时不折腾、不上常驻；活动开领时起在 `:8080`，活动结束即停），与日常主力双反代各司其职，坚决不引入 9router。


## 上游关联

PR **NousResearch/hermes-agent#106399**（`tool_output.tool_overrides`，per-tool spillover 阈值）已提交实证 review 并挂 CI issue 守望（`pr-merge-watch.yml`）。合并后可为单工具配更低 spillover 阈值 —— 与 `max_bytes` 是不同层（spillover 落盘 vs 输出截断），二者互补。
