---
name: shared-agent-memory
description: 读写双 Agent (Hermes & ZCode) 共享的跨端长期记忆库——单一物理真源，变动自动提交推送至 GitHub main 分支
---

# 双 Agent 共享记忆库 (shared-agent-memory)

共享记忆库**只有一份**（2026-09-05 单一真源架构，取代旧双分支镜像模型）：物理位于 ZCode 记忆目录，本 Agent 的 `memories/topics` 是指向它的 NTFS 目录联接（junction）——**读写 topics 即读写共享库本体**，切换 Agent 零拷贝零拉取。

## 位置与结构

- **共享库物理真源**：`%USERPROFILE%\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`
- **远程仓库**：`https://github.com/3304711297/shared-agent-memory.git`，**共享内容在 `main` 分支（默认分支）**
- **本 Agent 视角（等价路径）**：`%LOCALAPPDATA%\hermes\memories\topics\` = 上述真源的 junction
  - 共享库索引：`topics\MEMORY.md`
  - 单条专题记忆：`topics\<name>.md`（YAML frontmatter + 正文）
- **分支归属**：`main`=双端共享 | `zcode`=ZCode 专属 | `hermes`=Hermes 专属（home 白名单备份，已排除 topics）
- **Hermes 专属记忆（不放共享库）**：`memories\USER.md`（用户画像常驻）、根 `memories\MEMORY.md`（系统与环境常驻索引）→ 随 hermes 分支备份

## 何时读取

用户提到「之前 / 上次 / 记得吗 / 我们之前决定」等回溯性内容，或任务涉及用户环境、历史决策、进行中项目时：
1. 优先阅读常驻 `USER.md` 与根 `MEMORY.md`；
2. 按需检索 `topics/`（即共享库）下对应专题文档，索引见 `topics\MEMORY.md`。

## 何时写入与自动备份

用户说出值得跨会话保留的事实（偏好、纠正、环境约束、项目进展、拍板决定）时：

1. **跨 Agent 事实** → 在 `topics/` 新建/更新专题 `.md`，并同步更新 `topics/MEMORY.md` 索引；frontmatter 格式：

```markdown
---
name: <短横线小写英文标识>
description: <一句话摘要>
metadata:
  type: user | feedback | project | reference
---

<事实正文；type 为 feedback 或 project 时，正文后跟 **Why:** 和 **How to apply:** 两行>
```

2. **Hermes 专属事实**（仅本 Agent 运行时需要）→ 更新 `memories/USER.md` 或根 `memories/MEMORY.md`。
3. **【入库前脱敏门禁铁律】**：由于 shared-agent-memory 属于公开仓库（Public Repo），任何 Agent 在写入或更新任何记忆正文前，**必须执行前置脱敏**：
   - **严禁硬编码开发机用户名与机器物理路径**：任何涉及用户主目录、应用数据目录的路径，必须强制转换为标准环境变量（如 `%USERPROFILE%`、`%LOCALAPPDATA%` 或 `$HOME`），严禁出现真实个人机器名或用户名（如 `VOS-User`）；
   - **严禁泄漏任何真实密钥与凭据**：包含 Token、API Key、Bearer 授权头、Password、Cookie 等一律脱敏为 `<REDACTED_*>` 或占位符；
   - **客观技术知识规范**：通用系统知识保留标准规范写法，个人专属目录与工作区全部变量化泛化。
4. **【铁律】修改或新增记忆后，当轮结束前自动静默推送**（无需等待用户提醒；直连失败回退 `-c http.proxy=http://127.0.0.1:3067`）：
   - 共享内容（topics/ 即共享库，git 仓库在真源目录）：
   ```bash
   git -C "%USERPROFILE%/.zcode/cli/memories" add -A && git -C "%USERPROFILE%/.zcode/cli/memories" commit -m "memory: <简述>" && git -C "%USERPROFILE%/.zcode/cli/memories" push origin main
   ```
   - Hermes 专属内容（自家 home 仓库）：
   ```bash
   git -C "%LOCALAPPDATA%/hermes" add -A && git -C "%LOCALAPPDATA%/hermes" commit -m "docs(memory): <简述>" && git -C "%LOCALAPPDATA%/hermes" push origin hermes
   ```

**注意**：`memories/topics` 已在 home 仓库 .gitignore 中排除，严禁再往 hermes 分支提交共享 topics 镜像；旧镜像历史存档于 hermes 分支 `957241a`。

## 智能语义检索与层级加载层 (OpenViking)

为了避免全局 Grep 造成的长文本 Token 暴击与关键词错失，架构挂载了 OpenViking 作为**二级派生检索索引**（Git `main` 仍为唯一物理真源）：

- **服务拓扑**：
  - **OpenViking 核心服务**：`http://127.0.0.1:1933`（独立虚拟环境 `%USERPROFILE%\.openviking\venv`，无黑框后台运行）
  - **本地向量 Embedding**：`http://127.0.0.1:18082/v1`（llama-server 纯本地驱动 `D:\HermesModels\bge-m3-Q8_0.gguf`，CUDA RTX 4070 硬件加速，1024 维）
  - **提炼模型 (VLM)**：`http://127.0.0.1:18080/v1`（gemini-3.8-flash，用于秒级提炼 L0 摘要与 L1 大纲）
  - **共享记忆挂载点**：`viking://resources/shared-memory/`（客观知识库命名空间，严格与 Agent/User 私有偏好隔离）
- **双驱动自动同步**：
  1. **即时驱动（Git Hook）**：在 `%USERPROFILE%\.zcode\cli\memories\.git\hooks\post-commit` 与 `post-merge` 挂接 `sync_shared_memory_openviking.py`，ZCode 或本地有 commit 产生时秒级增量触发 OpenViking 重新扫描；
  2. **兜底探活**：`sync_shared_memory_openviking.py` 记录 `last_synced_commit.txt`，对比 Git HEAD SHA 自动防漂移。
- **Hermes 召回约束（防 Prompt 污染与注意力稀释）**：
  - `OPENVIKING_RECALL_LIMIT=3`
  - `OPENVIKING_RECALL_SCORE_THRESHOLD=0.35`
  - `OPENVIKING_RECALL_PREFER_ABSTRACT=true`（优先拉取 L0 一句话摘要，按需用 `viking_read` 钻取 L2 全文）
  - `OPENVIKING_RECALL_RESOURCES=true`
  - **Serverless 懒加载与按需唤醒**：网关 `openviking_lazy_gateway.py` 监听 1933 端口，提问时秒级按需唤醒 18082 与 1934，**连续 2 分钟无请求自动休眠释放 800MB 显存**；依用户偏好已移除开机自启，由桌面快捷方式或运维脚本按需启停。
- **后台服务守护与运维**：
  - 查看状态：`python %LOCALAPPDATA%/hermes/scripts/openviking_service.py status`
  - 启停服务：`python %LOCALAPPDATA%/hermes/scripts/openviking_service.py [start|stop|restart]`

## 多步复杂工程与任务看板（Todo-First 规范）

当针对共享库、配置迁移、依赖升级或多仓工程开展 **3 步及以上的任务** 时：
1. **严禁仅在主聊天文本框手打纯文本 Markdown 列表**（`- [ ] 步骤一`）；
2. **必须显式调用 Hermes 原生 `todo_list` 工具**初始化任务看板（`tasks: [{id, content, status}]`）；
3. 每完成一个原子步骤，必须实时调用 `todo_list` 将对应步骤推进为 `completed` 并激活下一步为 `in_progress`，使阶段进度在桌面端原生控件中实时可视化。

