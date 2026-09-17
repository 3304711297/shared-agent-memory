---
name: shared-agent-memory
description: "管理记忆库/存记忆时必用。shared-agent-memory真源读写与自动推送。Manage the Hermes shared memory store and auto-push changes."
---

# Hermes 共享记忆库 (shared-agent-memory)

共享记忆库**只有一份**（2026-09-05 单一真源架构）：物理真源位于 `D:/ai coding/GitRepos/shared-agent-memory`（2026-09-09 起，取代旧 .zcode 内路径），本 Agent 的 `memories/topics` 是指向它的 NTFS 目录联接（junction）——**读写 topics 即读写共享库本体**，零拷贝零拉取。ZCode 客户端已于 2026-09-09 拆除，本库现为 Hermes 单 Agent 所有；历史跨端内容保留作归档。

## 位置与结构

- **共享库物理真源**：`D:/ai coding/GitRepos/shared-agent-memory/`（git 仓库根）
- **远程仓库**：`https://github.com/3304711297/shared-agent-memory.git`，**共享内容在 `main` 分支（默认分支）**
- **本 Agent 视角（等价路径）**：`%LOCALAPPDATA%\hermes\memories\topics\` = 上述真源 `projects\default-135ef1b9f66d8a7e\memory\` 的 junction
  - 共享库索引：`topics\MEMORY.md`
  - 单条专题记忆：`topics\<name>.md`（YAML frontmatter + 正文）
- **⚠️ 仓库内 `topics/` 目录是遗留副本陷阱（2026-09-09 实证）**：共享库仓库根下的 `topics/` 已被 .gitignore（`/topics`）且内容陈旧，与真源内容不一致——它不再是任何 junction。**读写必须走 git 跟踪的 `projects/default-135ef1b9f66d8a7e/memory/` 路径**；误写仓库内 topics/ 的改动永远不会进 git。判别方法：对两路径同名文件 `git hash-object` 比对，或看 `.gitignore` 是否含 `/topics`。2026-09-13 已 `git clean -fdX topics/` 清空 80 个幽灵文件（仅保留被跟踪的 `skill-slimming-astrastandards.md`），并立本地警示牌 `topics/__DO_NOT_WRITE_HERE__.md`（ignored，不进仓，仅防 filesystem 浏览误入）。健康状态=该目录仅 1 被跟踪文件 + 1 警示牌；若看到几十个 md，说明又有写入误入陷阱，按上法清理。
- **分支归属**：`main`=记忆真源 | `hermes`=Hermes home 专属备份 | `zcode`=ZCode 会话归档（在姊妹私有仓 shared-agent-sessions，只读历史）

**⚠️ hermes 分支有两个独立克隆（2026-09-15 实证）**：`%LOCALAPPDATA%\hermes`（Hermes 运行 home，日常备份提交源）与 `D:/ai coding/GitRepos/shared-agent-memory`（物理真源，常驻 main）。两者都 fetch/push 同一 origin/hermes。**严禁在 D 盘克隆里 `git checkout hermes`**——真源目录的 `projects/` 会被换成 hermes 分支版本，且 `memories/topics` junction 指向的 `projects/default-.../memory/` 会随之消失（因为该路径被 .gitignore 排除、hermes 上无此目录），共享库当场「断链」。需要改 hermes 分支时用 `git worktree add <临时目录> hermes`，改完 `git worktree remove`。

**推送代理回退（2026-09-15 实证）**：本机对 github.com 直连会 `Recv failure: Connection was reset`，`env -u ALL_PROXY -u HTTP_PROXY -u HTTPS_PROXY git ls-remote/push` 同样失败；必须显式走本地代理 `git -c http.proxy=http://127.0.0.1:3067 push origin <branch>`。`gh` CLI 走 keyring 不受影响（`gh run list/view` 可查 CI 结果）。
- **Hermes 专属记忆（不放共享库）**：`memories\USER.md`（用户画像常驻）、根 `memories\MEMORY.md`（系统与环境常驻索引）→ 随 hermes 分支备份

## 何时读取

用户提到「之前 / 上次 / 记得吗 / 我们之前决定」等回溯性内容，或任务涉及用户环境、历史决策、进行中项目时：
1. 优先阅读常驻 `USER.md` 与根 `MEMORY.md`；
2. 按需检索 `topics/`（即共享库）下对应专题文档，索引见 `topics\MEMORY.md`。

## 何时写入与自动备份

用户说出值得跨会话保留的事实（偏好、纠正、环境约束、项目进展、拍板决定）时：

1. **跨会话事实** → 在 `topics/` 新建/更新专题 `.md`，并同步更新 `topics/MEMORY.md` 索引；frontmatter 格式：

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
   - **严禁硬编码开发机用户名与机器物理路径**：任何涉及用户主目录、应用数据目录的路径，必须强制转换为标准环境变量（如 `%USERPROFILE%`、`%LOCALAPPDATA%` 或 `$HOME`），严禁出现真实个人机器名或用户名（含示例、注释与配置文件）；
   - **【路径替换手法，2026-09-15 实证】**：
     - `.cmd`/`.vbs`：直接用 `%USERPROFILE%\...` 原生写法即可。已实测 `WshShell.Run` 会展开 `%VAR%`（无论命令串外层是否走 `cmd /c`，嵌套引号 `"""%USERPROFILE%\x.exe"" ""y.py"" --flag"` 也能正确展开且参数不漏）；
     - `.py`：**按文件既有惯例二选一**——`Path.home() / "AppData/Local/hermes/..."`（Path 对象，最简）或 `os.path.expandvars(r"%USERPROFILE%\...")`（保留原字符串形态）。注意 `Path.home()` 返回 `C:\Users\<当前用户>`，与原字面量逐字节等价；
     - **改完必须逐条验证运行期取值**：用 `importlib` 动态加载改后的 .py，断言常量解析出的绝对路径与原字面量相同（本次 17 个常量全 PASS），不要只靠肉眼 diff；
     - 脚本若**只**因新增 `os` 用法而需要 import，要顺手补 `import os`（注意该分支文本文件是 **CRLF**，替换串里 `\n` 要写成 `\r\n`）。
   - **通用检测正则不要含真实用户名**：门禁脚本应匹配 `[A-Za-z]:[\\/]{1,2}Users[\\/]{1,2}(名字)` 的**通用**形态（大小写不敏感，防小写盘符绕过），而不是硬编码具体用户名——否则检测器自身在公开仓里就是一处泄露（`main` 分支现状即如此）。文档占位符（`<user>`/`name`）要走白名单，否则误伤正常技能文档；检测器自身文件要自我排除，否则携带检测正则自判失败。
   - **【脱敏不消除历史】**：`git grep` 只看 tip，历史中的旧值仍在。评估残留要遍历 `git rev-list --objects <ref>` 的全部 blob（不只 commit）；本次 hermes 分支历史残留 174 个 blob / 48 条路径，而 tip 已 0 残留——公开仓的历史同样可读，彻底消除需 `filter-repo` + force push（会重写他人克隆，需用户明确授权）。
   - **严禁泄漏任何真实密钥与凭据**：包含 Token、API Key、Bearer 授权头、Password、Cookie 等一律脱敏为 `<REDACTED_*>` 或占位符；
   - **客观技术知识规范**：通用系统知识保留标准规范写法，个人专属目录与工作区全部变量化泛化。
4. **【铁律】修改或新增记忆后，当轮结束前自动静默推送**（无需等待用户提醒；直连失败回退 `-c http.proxy=http://127.0.0.1:3067`）：
   - 共享内容（topics/ 即共享库，git 仓库在真源目录）：
   ```bash
   git -C "D:/ai coding/GitRepos/shared-agent-memory" add -A && git -C "D:/ai coding/GitRepos/shared-agent-memory" commit -m "memory: <简述>" && git -C "D:/ai coding/GitRepos/shared-agent-memory" -c http.proxy=http://127.0.0.1:3067 push origin main
   ```
   - Hermes 专属内容（自家 home 仓库）：
   ```bash
   git -C "%LOCALAPPDATA%/hermes" add -A && git -C "%LOCALAPPDATA%/hermes" commit -m "docs(memory): <简述>" && git -C "%LOCALAPPDATA%/hermes" -c http.proxy=http://127.0.0.1:3067 push origin hermes
   ```
   - **【公开仓 hygiene 门禁】**：`hermes` 与 `main` 分支各自带 `.github/workflows/ci.yml`，推送即触发 `python scripts/check_hygiene.py`（exit 1 = 违规阻断）。它扫**所有被跟踪文件**的密钥与通用机器路径（`<盘符>:/\Users\<名字>`），文档占位符与检测器自身已白名单。提交前可本地先跑一次同名脚本（两分支各有一份，接口/返回码一致）避免推上去才红。
   - **【推送后自检】**：`gh run list --repo 3304711297/shared-agent-memory --limit 5` 确认 CI 绿灯；`git ls-remote origin <branch>` 确认远端 hash 已变。

5. **【铁律】OpenViking 写后即时灾备**——本轮只要调用过任何 OpenViking 写入（`viking_remember`、`viking_add_resource`、记忆/资源挂载等），**无论当前任务主题是否与备份相关**，都必须在本轮结束前静默执行：
   ```bash
   cmd /c "D:\\openviking-backup\\sync.cmd"
   ```
   - 调用方式注意：git-bash 下用 `cd "D:/openviking-backup" && MSYS_NO_PATHCONV=1 cmd /c "sync.cmd"`；直接 `cmd //c` 会落进交互式提示符不执行。
   - 脚本把 `~/.openviking/data/viking/default/{user,resources}` robocopy 镜像到 `D:\openviking-backup\repo` 再推送私有仓 `3304711297/openviking-backup`；无变更秒退，幂等可重复调用。
   - **大删守卫（2026-09-11 加固）**：源文件数 < 备份文件数的 70%（且备份 ≥100 文件）时中止并返回 exit 2，备份保持不动，中止记录写入 `D:\openviking-backup\abort.log`。确认是真实删减而非源数据丢失后，才用 `OV_BACKUP_FORCE=1` 覆盖重跑。
   - 与每日计划任务 `OpenVikingDailyBackup`（09:30）互补：即时同步压缩暴露窗口，计划任务兜底 AI 无感知的异步写入。失败不重试不阻塞。

**规则放置原则（2026-09-11 教训）**：跨会话必须自动执行的约束，**不能只放在语义召回层**（OpenViking 资源 / 共享库文档）——它们仅在话题命中时才进入上下文。凡属「无条件触发」的规则（如写后同步），必须同时写入：(a) 内置 `MEMORY.md`（每轮注入，永远可见）；(b) 对应技能正文（任务命中时加载）。本次就是因规则只存在于召回层，导致修插件 bug 时执行了 `viking_remember` 却整轮无人提醒同步，直到用户手动贴出仓库 URL 才补跑。

## 先检索再造轮子（Lookup-Before-Build，2026-09-13 用户拍板）

**铁律：在自行实现任何解析、签名、抓取、协议适配或样板代码之前，必须先检索是否已有成熟方案；严禁把「手搓」当作默认动作。**

触发场景（任一命中即适用）：

- 要写签名/验签、加密、编码、正则解析之类「看起来有标准答案」的算法；
- 要适配第三方平台的私有接口、私有协议、反爬逻辑；
- 要写数据格式转换、导入导出、迁移脚本；
- 即将写出超过约 50 行「与业务逻辑无关的胶水代码」；
- 遇到陌生的报错码 / 风控码 / 限流码，准备靠调参数试出来时。

必查的三个来源（按优先级）：

1. **本机已装技能池**（Skill-First Rule 的延伸）——先 `skills_list` / `skill_view`，别重复造已封装的轮子；
2. **官方文档与官方 API 文档**（`web_search` / `web_extract`）——确认字段语义、限额、已废弃接口；
3. **成熟开源实现的源码**（GitHub 仓库源码，不只是 README）——看社区是如何绕过同一个坑的，往往能直接得到正确参数组合或结论。

**反面案例（2026-09-13，B 站看门接入）**：为绕过 `-352 风控校验失败`，连续试了伪造 buvid3、`finger/spi` 换取真实 buvid、多组请求头组合、动态接口——都是在「手搓猜参数」。一次检索后立刻拿到决定性证据：官方库文档明写「可使用代理，绕过 b 站风控策略」、RSSHub 同路由源码要 `getCookie()` + wbi 校验串且标注反爬严格——**结论是该风控解不掉，只能换出口 IP 或换接口**。即「不必手搓」不是省事，而是避免朝错误方向白烧一轮。

**反例判据（出现任一即停下来检索）**：同一问题已换过 3 组参数仍失败；正在根据「社区传闻」而非文档调参；准备写超过 50 行与业务无关的胶水；解释不清某个字段/错误码的官方语义。

**Why**：手搓的成本不是行数，而是**方向成本**——在错误假设上迭代会消耗大量轮次且结论不可信；成熟方案已经过社区大规模验证，还能顺带得到边界条件与已知缺陷。

**How to apply**：动手前先花一次 `web_search`（或读官方文档/参考实现源码）；若检索确有结果，优先复用其思路与参数，只写业务差异部分；若检索无结果，**写明「已检索 X/Y/Z 未找到现成方案」再手搓**，让「为什么自研」有据可查。

**注意**：`memories/topics` 已在 home 仓库 .gitignore 中排除，严禁再往 hermes 分支提交共享 topics 镜像；旧镜像历史存档于 hermes 分支 `957241a`。

## 智能语义检索与层级加载层 (OpenViking)

为了避免全局 Grep 造成的长文本 Token 暴击与关键词错失，架构挂载了 OpenViking 作为**二级派生检索索引**（Git `main` 仍为唯一物理真源）：

- **服务拓扑**：
  - **OpenViking 核心服务**：`http://127.0.0.1:1933`（独立虚拟环境 `%USERPROFILE%\.openviking\venv`，无黑框后台运行）
  - **本地向量 Embedding**：`http://127.0.0.1:18082/v1`（llama-server 纯本地驱动 `D:\HermesModels\bge-m3-Q8_0.gguf`，CUDA RTX 4070 硬件加速，1024 维）
  - **提炼模型 (VLM)**：`http://127.0.0.1:18080/v1`（gemini-3.8-flash，用于秒级提炼 L0 摘要与 L1 大纲）
  - **共享记忆挂载点**：`viking://resources/shared-memory/`（客观知识库命名空间，严格与 Agent/User 私有偏好隔离）
- **双驱动自动同步**：
  1. **Git Hook 即时驱动**：真源仓库 `D:/ai coding/GitRepos/shared-agent-memory/.git/hooks/post-commit` 与 `post-merge` 挂接 `sync_shared_memory_openviking.py`，本地 commit 产生时秒级增量触发 OpenViking 重新扫描；
     - **2026-09-09 修复记录**：仓库迁移到 D 盘时 hooks 目录被重置，双钩子丢失导致 OpenViking 同步静默滞后（事发时 last_synced_commit 落后 5 笔提交）。已重建两钩子（bash 后台触发，已 chmod +x）。若发现同步滞后，手动补跑：`python %LOCALAPPDATA%/hermes/scripts/sync_shared_memory_openviking.py`，滞后判据：`%USERPROFILE%/.openviking/last_synced_commit.txt` 中的 SHA ≠ 真源仓库 HEAD；
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

## 本库清单与脚本的结构陷阱（改 `capability-inventory.json` 前必读）

- **`components` 是 JSON 数组，不是以 id 为键的对象**。取某组件必须过滤，不能下标：
  ```python
  comp = next(c for c in data["components"] if c["id"] == "ponytail-skills")
  ```
  写成 `data["components"]["ponytail-skills"]` 会抛 `TypeError: list indices must be integers or slices, not str`。同理 `skills-provenance.json` 的 `sources` 是数组、每项内嵌 `skills` 数组——**本库所有清单顶层都是列表**，先看类型再索引。
- 改完必须跑三项本地门禁再推 main：`python scripts/check_hygiene.py`（机器路径/密钥）、`python scripts/check_capability_upstream.py --lint`（清单结构）、`python scripts/check_capability_upstream.py --local-only`（本地源比对）。三者全绿才推。
- **【假绿铁律】门禁只扫 `git ls-files` 的已跟踪文件**——`git add` 之前跑，新增文件全部不参与扫描，本地绿灯但 CI 必红（2026-09-15 实测踩坑：新纳入 22 个技能文件，本地报 0 违规，CI 报 2 处密钥占位符）。**顺序必须是：`git add -A` → 跑门禁 → 绿了才 commit**。若要预览、还不想入暂存区，用 `git ls-files --cached --others --exclude-standard` 自建文件列表。
- **【同源铁律】`scripts/check_hygiene.py` 与 `tests/test_check_hygiene.py` 在四个位置各有副本，必须逐字节相同**：共享库 main 分支 + hermes 分支 + hermes home 仓 hermes 分支（工作区文件亦为同源）；改动任一份后**立即 cp 覆盖其余并比对 sha256**，不要各自维护。2026-09-15 实证：两份曾分叉到「路径正则量词 `+`/`*` 不同、占位符白名单 15 vs 26 项」，直接后果是**同一份内容在一个仓扫描通过、在另一个仓 CI 变红**，且 `*` 版会把裸 `C:/Users/`（不含用户名、无泄漏）匹配成空捕获而误报。回归测试已接入两边 CI（`python tests/test_check_hygiene.py`）。改检测器时的判据：改完先跑回归测试（50 用例，覆盖真实违规拦截 + 全部白名单项放行 + 白名单快照），变异验证法——故意反转量词/禁用判定/砍白名单项，测试必须报警，否则说明测试有覆盖漏洞。
- **`read_file` 在 `execute_code` 内核里读同一文件有去重守卫**：第 2 次返回 `{status:"unchanged", dedup:true}`（**无 `content` 键**），第 3 次返回 `{error:"BLOCKED…"}`。批量脚本里读本库 JSON 时直接用 `json.load(open(...))` 或 `if "content" in r` 先判形状，不要硬取 `r["content"]`。

## Hermes home 仓库 `.gitignore` 的锚定坑（2026-09-15 实测修复）

本 home 仓库（hermes 分支）的 `.gitignore` 采用「默认忽略全部 `*` + 白名单 `!skills/**`」结构，**白名单之外的无锚定目录规则会连嵌套同名目录一起排除**：

- 实例：第 44 行原为 `hermes-agent/`（本意只排除根目录 3.7G 源码目录），但因无前导斜杠，`skills/autonomous-ai-agents/hermes-agent/` 这个**官方技能**被一并忽略，从未进过 hermes 分支备份。已改为 `/hermes-agent/`（只匹配仓库根）。
- **判据与自检**：新增或修改忽略规则后，用 `git check-ignore -v <path>` 验证目标路径的匹配来源；对 `skills/ plugins/ desktop-plugins/` 三个白名单区跑 `git status --short --ignored skills/ | grep '^!!'`，凡是技能/插件目录出现在 `!!` 列表里就是误伤（`.usage.json.lock`、`__pycache__/` 之类的运行时残留属预期）。
- **通用规则**：本仓库里任何要排除「根目录下的某目录」的规则，一律加前导 `/`；无锚定的写法只适用于运行时产物名（`*.log`、`__pycache__/`）。

## 记忆真源唯一（单点存储铁律，2026-09-15 清理落地）

**记忆只存一处：共享库 `main` 分支的 `projects/<project>/memory/`**（即 `memories/topics` junction 的指向）。任何第二份存档都是分叉隐患，一经发现即清除。

- **实例（已清理）**：hermes home 仓曾跟踪 `projects/default-…/memory/hermes-agent-install.md`——zcode 时代遗留的**独立副本**（真实文件，非 junction），内容停滞在共享库 main 的 `fd540fc`（2026-09-04），比现值少 21 行。两处存档各自演化，正是分叉的温床。处置：`git rm --cached` 脱离跟踪 + 删磁盘副本 + `.gitignore` 加 `/projects/` 防复发。
- **清理前的三项核验（缺一不可，避免误删真源）**：① 副本内容是否为共享库版本的严格子集（比对两侧行集，确认独有 0 行）；② 全仓是否有引用指向该副本路径（`grep` 搜 `LOCALAPPDATA.*projects/` 与 `hermes.*projects/`，本次 0 处——相关脚本引用的是 D 盘真源）；③ 留一份可回滚备份再删。
- **判别某路径是否为「第二份存档」**：`os.path.realpath()` 看是否指向 D 盘真源——是则为 junction（无副本，安全），否则是独立文件（副本，需核验后清理）。
- **自检命令**：hermes home 仓跑 `git ls-files projects/` 应恒为空；跑 `git status --short --ignored skills/ plugins/` 确认无技能/插件目录被误伤。

## 本地看门比对是选测，不是全测（实跑优先，勿臆断）

跑 `check_capability_upstream.py --local-only` **不能**当作「全清单零待跟进」的通用证据：该模式只跑 `local-merged-marketplace` / `local-config-guard` 两类本地源（本机 40 个组件里仅 2 个），其余 38 项输出「⏭️ 本地模式跳过」。真正的判据是**先看云端看门上一次运行报告里的「待跟进组件数」**，再决定要不要本地重跑。

- **正确取证顺序**：① `gh run list --workflow capability-upstream-watch.yml` 取最近成功的 run → 读其结论；② 只余本地专属项时才跑 `--local-only`；③ 外部源项若确需本地复核，用 `GH_TOKEN=$(gh auth token) python scripts/check_capability_upstream.py`（**必须带 GH_TOKEN**，否则 GitHub API 无鉴权、脚本因 `failed_queries >= 3` 直接以 exit 1 中止并不写报告）。
- **告警阈值与噪声的换算**：`hermes-skills-hub` 的判定是 `behind = total > rec_total`（严格大于）。回写当前快照后，把**当次真实值**写进 `version`/`totalSkills`，不要沿用旧值——写成大于上游的值，等价于给未来所有低于它的数当噪声滤掉；写成小于上游的值，会在下次运行立刻再亮 🔴。
- **报出「某分类计数」前先复算自查**：聚合源（skills-hub）单看分类计数不可靠——按 `bySource` 逐项相加后必须等于 `totalSkills`、并且 `localSkills + externalSkills == totalSkills`；三项对不上说明拿到的是缓存/非权威分片，此时不要下结论（本次实测 ClawHub 78,478 与总差 2,277，用样本序号无法对上）。

## `capability-inventory.json` 回写实操（收口看门 Issue 的标准动作）

1. **文件是混合行尾**：既有 CRLF 行也有 LF 行（本文件有一行是 LF、其余 CRLF）。做文本替换时**逐段以各自实际字节为模板**（用 `open(path,'rb')` + `count(check)==1` 断言命中唯一），不要假定全文件统一行尾，更不要用文本模式整体重写（会把 40 个组件全部 reflow 成同一行尾）。
2. **`note` 字段承载「为何这样回写」**：把取证与判据写进被改条目的 `note`（如「上游峰值 X 后回落、连采 N 次稳定于 Y、判定为源波动而非新版」），下次被问到时有据可查。
3. **公开仓禁写账号标识**：回写 note 常牵涉 `gh auth status` 之类的取证，产出里要写「凭据与 token scopes 不变」，**不要**写用户名/账号 ID——`check_hygiene.py` 拦不住它，但公开仓铁律拦得住。

## 改大 JSON 清单前先做「往返一致性」预检（2026-09-16 踩坑）

`capability-inventory.json` / `skills-provenance.json` 这类 40KB 级清单，**不要手拼 JSON 字符串做插入**——转义引号极易写坏文件（本次写出 `Invalid control character at line 686`，整个清单报废，只能 `git checkout --` 恢复重做）。正确顺序：

1. **先量行尾**：`txt.count("\r\n")` vs `txt.count("\n")` —— 逐字节确认是「全 CRLF」「全 LF」还是**混合**（混合则禁止整体重写，只能逐段字节替换）。
2. **做往返预检**：`json.dumps(json.loads(txt), ensure_ascii=False, indent=2)` 归一化行尾后**逐字节比对原文**。相等才可整体重写（本次清单相等 → 安全；provenance 差一个末尾换行 → 按原样补/去）。
3. **整体重写**：`json.dump` + `newline=""` 写回，行尾用归一化后的形态。
4. **写后立刻 `json.load` 回读断言**字段值与组件数，别信写入成功。

— 另：若某个 `note` / `meta` 字段里要写引号，用中文引号或改写措辞，不要靠 `\"` 嵌套；中文的 `“”` 不需要转义。

## 看门范围口径：只收「与本地实装有关」的组件（2026-09-16 拍板）

判断某组件该不该进看门，问一句就够：**它落后了我会不会真的去动本地？**

- 两类不进：① `github-commits-path` 纯台账型（2026-09-09 后永不计入 outdated，每日只打印上游 HEAD/基线，零可执行价值）；② 市场/索引计数型（本地实装 0 项，只会因源侧波动刷计数噪声）。
- 三类必进：已装 CLI / 插件 / MCP（`gh-release`/`pypi`/`npm`/`gh-repo`，落后就要升级）、已装技能套件（`gh-release`）、本地配置守卫（`local-config-guard`）。
- **两个易错点**：① 同一种 check 类型可能两类都在用——本次误判 `github-commits-path` 整体退役，实际还有 19 个 workbuddy 借鉴雷达在用；**下结论前先跑一遍类型计数**（`Counter(c["checks"][0]["type"] for c in components)`）。② 退役**只改清单、不改代码**——三种市场 check 类型与 `github-commits-path` 分支保留在 `check_capability_upstream.py`，未来重启只需补清单条目。
- **借鉴雷达与纯台账区分（2026-09-17 修复落地）**：`github-commits-path` 严格细分为两类：纯技能库路径（`is_radar=False`，保持 09-09 规则不计 outdated 避免噪声）；而**借鉴雷达**（`is_radar=True`，含 `radar: true`、display 含「借鉴雷达」、或 id 为 `wb2api-upstream-*` / `c2api-upstream-*`）上游产生新 commit 时必须判定 `behind=True`、计入 `outdated` 触发 Issue 告警，并输出 compare 对比链接供评估摘樱桃（Cherry-pick）。评估落地或无需采纳后，更新清单中的 sha 基线推 main 即可自动收口 Issue。
- **退看门 ≠ 失去保护**：已装技能的落后判定由 `check_skill_drift.py` 独立完成（脚本自带 `CATEGORY_TO_SOURCE` 映射，**不读清单、不读 provenance**），清单里删掉技能库条目不会削弱任何保护；要确认某技能还受保护，只需看它所属 category 是否在 `CATEGORY_TO_SOURCE` 里。
- **落盘三件套**（缺一即半成品）：清单 `notWatched` 写退役判据 + `meta` 记口径 + `skills-provenance.json` 的 `watchStatus`/`checkType` 改指新保护来源；再同步 README、`MEMORY.md` 索引行、运维与治理两篇专题（索引库那条要说清「为什么它仍是发现入口」）。

## `%TEMP%` 临时克隆的清理规范（2026-09-15 实操沉淀）

排查问题时在 `%TEMP%` 下留的仓库克隆会长期堆积（本次清出 11 个/179MB）。清理按四步走，**不得直接 `rm -rf`**：

1. **枚举 + 判据**：`os.path.isdir(<dir>/.git)` 筛出克隆（非 git 目录的普通临时文件不属此列）。
2. **查未推送提交（最关键）**：`git log --oneline --branches --not --remotes` —— 非空即含本地独有工作，**先抢救再谈删除**。本次 11 个全部为 0，才继续。
3. **查脏改动性质**：`git status --porcelain` 后区分——`D`（文件被删，检出后未还原，取消即恢复）与 `??`（生成残渣）通常无害；`M`（内容修改）需逐条与真源比对，确认是「真源的旧版本」而非「未提交的新内容」（比对法：真源工作区/HEAD vs 副本，看副本独有行是旧措辞/旧结构还是新信息）。
4. **留存 → 删除**：把脏改动导成补丁（`git diff` + `git diff --cached` 合并），连同 `manifest.json`（记录各副本 remote/HEAD/日期）存到 `%TEMP%\_temp_repos_patches_<日期>\`，然后才删。

- **进程占用预检**：删除前用 `wmic process get processid,commandline` 搜目录名，确认无进程引用（尤其名字与在跑服务相关的副本，如 `easycliproxyapi`）。
- **本次结果**：11 个副本（含 agent 自身于 09-06 留的 `sam_view`、09-05 的 `easycliproxyapi`）全部无未推送提交；3 个有脏改动的已存补丁；释放 179MB。

