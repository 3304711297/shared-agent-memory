---
name: user-windows-environment
description: User environment is Windows-based with adobe-for-creativity plugin
  installed but MCP authentication issues
metadata:
  node_type: memory
  type: project
  originSessionId: sess_96e5646b-aeb8-4de6-abe9-e69399637402
---

## Environment Details
- Platform: Windows (Git Bash shell)
- ZCode CLI path: `C:\Users\VOS-User\.zcode\cli\`
- Memory path: `C:\Users\VOS-User\.zcode\cli\memories\projects\default-135ef1b9f66d8a7e\memory\`
- Working directory: `D:\ai coding\.zcode\workspace\default`
- Not a git repository

## 浏览器
- 用户浏览器是 **Edge Dev**：`C:\Program Files (x86)\Microsoft\Edge Dev\Application\msedge.exe`（注册表 App Paths 里唯一注册的浏览器；2026-08-22 用户确认"这是我的浏览器"）
- **未安装 Google Chrome**：chrome-devtools MCP 默认找 stable 版 chrome.exe 找不到、启动即报错——需要浏览器自动化时须改用 Edge Dev（或给 MCP 显式配 executablePath）
- ChatGPT 对话链接（chatgpt.com/c/<uuid>）是登录私有的，WebFetch 未登录抓取只会得到登录墙；要读用户的 ChatGPT 对话需借助其登录态的 Edge Dev（如 CDP 调试端口），或让用户在 ChatGPT 里生成 /share/ 公开分享链接后抓取

## PowerShell / Shell 环境
- 2026-08-21 起双版本并存：系统内置 Windows PowerShell 5.1（`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`）+ PowerShell 7.6.5（winget 用户级安装，`pwsh` 经 WindowsApps 别名调用；pwsh -File 需绝对路径）。最新稳定版即 7.6.5（GitHub Releases 核实）。**用户偏好：日常默认用 pwsh 7，仅在验证 5.1 兼容性时才切 `powershell`**
- 验证 tweak 脚本两个运行时都要覆盖：用户入口历史上是 5.1（CI 的 pwsh 覆盖不到 5.1 特有行为），现 CI test 已拆 pester(pwsh) + smoke-windows-powershell(5.1) 双任务
- 无 BOM 的 UTF-8 .ps1 在 PS 5.1 下中文乱码并可能破坏语法；含中文的新建脚本必须补 UTF-8 BOM（pwsh 7 默认按 UTF-8 读，无此问题）；PS 5.1 与 7.x 中 `0xFFFFFFFF` 字面量均为 Int32 的 -1，DWORD 上限比较须用 `[uint32]::MaxValue`；**中文弯引号 `“ ”` 被 PowerShell 当作字符串定界符**——双引号字符串里写 `“x”` 会提前终止字符串（表达式模式下直接解析报错，参数模式下静默拆成多参数），ps1 字符串一律用「」或 [] 代替弯引号。已用同一带 BOM 文件在 pwsh 7.6.5 与 5.1 下对照解析实测：两者报错完全一致，该规则跨版本通用
- ZCode Bash 工具即 Git Bash：每次调用独立进程，环境变量不跨调用保留，cwd 每次执行后重置回默认目录（每条命令需自带 cd）；内联 `powershell -Command "…$var…"` 的 `$` 会被 bash 展开，复杂 PS 逻辑应写成临时 .ps1 文件执行（临时脚本须 ASCII 或带 BOM，且失败分支不要无条件 rm）
- GitHub Actions 工作流坑（2026-08-21 实测）：`run: |` 块标量里的多行字符串（如 gh release --notes 的说明文本）续行**必须保持缩进**——顶格续行会终止块标量，其余文本被解析为新 YAML 键，工作流文件直接无效（运行 0 秒失败，仅提示 "workflow file issue" 不给具体行号）；本地可先用 `python -c "import yaml; yaml.safe_load(...)"` 预检；多行内容推荐用 `printf '...\n\n...'` 构造到变量再引用，缩进归 YAML、内容归变量

## Installed Plugins
- adobe-for-creativity v2.0.0 (MCP server not loading due to 403 authentication error)

## Current Issues
- Adobe for creativity MCP server shows "未加载" (not loaded), 0 tools
- Error: "Version negotiation failed: the server denied access (HTTP 403)"
- Plugin installed at: `C:\Users\VOS-User\.zcode\cli\plugins\cache\claude-plugins-official\adobe-for-creativity\2.0.0\`
- Windows PowerShell 当前装有 Pester 6.1.0（CurrentUser 作用域，与 tweak CI 钉的版本一致），2026-08-21 实测本地 `Invoke-Pester` 跑通全部 14 个用例；PSScriptAnalyzer 1.25.0 同日装好（CurrentUser，与 CI 一致）
- 本地工具链（2026-09-05 更新）：gh 2.100.0（MSI 机器级，2026-09-05 由 2.98.0 升级，Authenticode 验签后静默装，keyring 认证无缝保留）；lychee 0.24.2 在 `%LOCALAPPDATA%\Programs\lychee`（已追加用户 PATH，旧终端需重开生效）；PowerShell 7.6.5。Git 装在自定义路径 `D:\Git`——**不要用 winget 升级 Git.Git**（可能改写安装路径）。gh/git/powershell/lychee 已纳入能力看门（[[capability-upstream-watch]]）。
- Git 安全升级方法：注册表 `HKLM:\SOFTWARE\GitForWindows` 的 InstallPath=D:\Git（机器级安装，升级需 UAC）；从 git-for-windows/git GitHub Releases 下载官方安装器，静默参数 `/VERYSILENT /NORESTART /SUPPRESSMSGBOXES /DIR=D:\Git` 显式锁路径；须用"延迟 90 秒的提权脚本"执行——ZCode 每次 Bash 调用会临时占用 D:\Git 的 bash.exe/msys 文件锁，调用之间才释放
- 2026-08-21 Git 已成功升级 2.54.0 → 2.55.0.windows.5：安装器 exit=0，`git --version` 确认新版本，`where git` 仍指向 D:\Git，注册表 InstallPath 未变；临时文件已清理
- winget 的 CDN 源在本机经常连不上（WinHttp 12029），GitHub 直连稳定：装不到的东西优先从 GitHub Releases 直接下载（gh 可自举下载新版 MSI 后 msiexec 提权装）
- 网络代理（2026-08-21 确认）：本机经本地代理上网，`http_proxy`/`https_proxy`/`all_proxy`/`ZCODE_HTTP_PROXY` 均为 `http://127.0.0.1:3067`。curl 自动遵循这些变量、可正常访问 raw.githubusercontent.com；**Node 内置 fetch(undici) 不读代理环境变量，会直连失败**——Node 脚本访问外网应先直连再回退 curl 子进程（或用 undici ProxyAgent）
- 代理节点会临时故障（2026-08-23 实例：gh 调 GitHub API 出现 TLS 握手超时，数分钟前同代理还是通的）——遇 gh/API 突发超时先重试，仍失败可提示用户换节点（用户自行更换后即恢复）；**确认是代理问题前别急着改命令**
- 文件摆放偏好（2026-08-23 明确）：**不喜欢把自装内容放 C 盘**——浏览器扩展等自装文件统一放 D 盘（如 `D:\extensions\`）；涉及安装/落盘位置的操作默认优先考虑 D 盘
- GitHub 账号：gh CLI 已登录 `3304711297`（昵称"智商已更新"），建仓/推 API 均可用

## 模型网关与 Antigravity 桥接（2026-09-04 架构迭代）
- **网关核心**：已彻底退役旧版 ZCode-Antigravity 派生分支，全面升级至官方 **EasyCLIProxyAPI**（核心版本 `v7.2.151`，2026-09-05 手动升级并冒烟验证，commit 5208aec7；安装于 `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64`，cpa-core 内不留旧版本备份，回退=从 GitHub Releases 重装）。
- **运行方式**：本地模型网关监听 `http://127.0.0.1:18080`，官方核心内嵌正版 OAuth 凭据，直接原生支持 `gemini-3.8-flash`（及 `-high` 思维链）、`gemini-3.7-flash`、`gemini-3.6-flash`、`gemini-3.1-pro-low`、`gemini-3.1-flash-image`（生图）、`gemini-web-search` 等全系模型。
- **协议双通**：
  - Hermes Agent 走 OpenAI 兼容协议（`http://127.0.0.1:18080/v1/chat/completions`，提供商 `cpa-gui`）；
  - ZCode 走 Anthropic Messages 协议（`http://127.0.0.1:18080/v1/messages`，提供商 `cpa-gui`，主力模型 `gemini-3.8-flash`）。
- **ZCode 客户端路径规范化**：因 EasyCLIProxyAPI 控制台硬编码探查系统盘规范路径，已在系统建立 NTFS 目录联接（Junction）：
  - `%LOCALAPPDATA%\Programs\ZCode` -> `D:\zcode`
  - `%ProgramFiles%\ZCode` -> `D:\zcode`
  使控制台无需将软件重装至 C 盘即可原生识别客户端版本与一键启动。
- **Google 配额监控微服务 (`Hermes_Quota_Service`)**：
  - 监听 `http://127.0.0.1:18088/quota`，内存缓存 30s，支持 `?force=1` 穿透直连 Google 官方 Antigravity 专有端点（`daily-cloudcode-pa.googleapis.com`）；
  - 注册为 Windows 计划任务 `Hermes_Quota_Service`，开机通过 `pythonw.exe` 静默无窗口后台常驻；
  - 配套 Hermes 桌面端 `token-stats` 毛玻璃 Popover 状态栏微件。
- **三层假故障网络辨析法则**：
  - `TLS timeout` / 握手超时 -> Karing 节点掉线或网络中断；
  - `invalid_grant` -> Google 授权会话失效或 IP 剧烈飘移，需用 EasyCLIProxyAPI 重新登录；
  - `User location is not supported` -> 节点出口地区未获 Google AI 授权（如香港地区节点）；
  - **铁律**：遇到上述三种报错先查代理节点与出口地区，严禁轻率修改本地网关代码。

## 浏览器与扩展环境清单（D 盘摆放规范）
- **日常浏览器**：Microsoft Edge Dev，用户配置目录位于 `%LOCALAPPDATA%\Microsoft\Edge Dev\User Data`。
- **扩展与脚本数据保护**：Hermes 的 `config.yaml` 必须设置 `browser.use_real_profile: false`，彻底隔离日常 Edge 用户目录，防止自动化 Chromium 实例退出时写回空注册表导致扩展清空。
- **核心扩展清单与物理路径**：
  - **应用商店版扩展**（数据位于 `Local Extension Settings`，重装同 ID 即可自动接回数据）：
    - 脚本猫 (ScriptCat)：`liilgpjgabokdklappibcjfablkpcekh`（全部油猴脚本安然无恙）
    - 简约翻译 (KISS Translator)：`jemckldkclkinpjighnoilpbldbdmmlh`
    - 小电视空降助手 (SponsorBlock)：`khkeolgobhdoloioehjgfpobjnmagfha`
    - BewlyCat (B站美化)：`naephbpbijnomloddmldmgmfcjhikbac`
  - **本地解压版扩展**（依规范统一存放于 `D:\extensions\`，在 `edge://extensions` 开发者模式加载）：
    - 青柠起始页：`D:\extensions\LimeStartPage\src`
    - 小黑盒扩展 (better-XiaoHeiHe)：`D:\extensions\better-XiaoHeiHe-main`
    - BewlyBewly / 辅助扩展：`D:\extensions\extension`

## ZCode 全局 Skills 与记忆备份
- **用户核心全局 Skills**（位于 `C:\Users\VOS-User\.zcode\skills\`；2026-09-05 起另有 87 个 Hermes hub skills 迁入，详见 [[hermes-to-zcode-capability-sync]]）：
  1. `gemini-image-gen`：请求本地 `http://127.0.0.1:18080/v1/chat/completions` 调用 `gemini-3.1-flash-image` 生图并保存至 `generated_images/`
  2. `frontend-design`：现代高审美 UI 设计规范（Tailwind / 现代排版）
  3. `readme-master`：专业开源级 README.md 深度扫描与生成规范
  4. `smart-web-crawler`：带代理支持的轻量网页提取与 Markdown 转换（`crawl.py`）
  5. `chinese-copywriting`：中文技术排版规范与中英混排空格自动化（`pangu_format.py`）
  6. `semantic-release-pro`：语义化 Commit、SemVer 计算与 Changelog 生成规范
- **ZCode 记忆持久化云端备份**：私有仓库 `https://github.com/3304711297/shared-agent-memory`（Private，2026-09-05 三分支架构：共享内容推 `main`，`zcode`/`hermes` 分支各放 Agent 专属），本地 `~/.zcode/cli/memories/` 检出 main，已建立"记忆变动自动静默备份"铁律机制（详见 [[multi-branch-memory-backup]]）。

## WorkBuddy 模型桥接
- **WorkBuddy 客户端**：安装在 `D:\workbuddy\WorkBuddy.exe`，CLI 脚本在 `D:\workbuddy\resources\app.asar.unpacked\cli\bin\codebuddy`。
- **workbuddy_to_api 桥接服务**：部署在 `D:\ai coding\workbuddy_to_api`，本地监听 `http://127.0.0.1:3000`（OpenAI: `/v1`，Anthropic: `/`，API Key: `local`），支持 49 个模型（默认 `auto`）。

**Related:** [[adobe-mcp-authentication]] [[cross-repo-coverage-audit]] [[auto-backup-memories-to-github]] [[workbuddy-to-api-setup]]

**2026-09-01 更新**：本地代理 3067 端口出现"监听但转发被重置"状态（curl --proxy 返回 000/Connection reset），同时直连 github.com 反而 200——代理可能切了 TUN/系统模式。git push 时先试直连（`git push`），直连失败再回退 `git -c http.proxy=...`，两种都要备着。
**2026-09-02 更新**：接入 ZCode-Antigravity 本地桥（18080 端口），配置 gemini-3.1-flash-image 生图 Skill 及 5 个高质量日常开发 Skill（前端/README/爬虫/文案/发布）；全开源项目 README 现代化重构完成。
