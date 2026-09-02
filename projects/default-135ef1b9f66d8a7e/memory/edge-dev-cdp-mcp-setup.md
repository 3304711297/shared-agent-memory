---
name: edge-dev-cdp-mcp-setup
description: 「AI 接管真实 Edge Dev」最终可用方案（edge://inspect 开关 + 授权弹窗 + autoConnect）、商店装扩展流程与历史教训（勿用路径技巧）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_7baee9ca-827c-4e0e-a934-428b42e9eb6a
---

2026-08-22 深夜最终调通「AI 接管用户真实 Edge Dev（v153）」的**官方方案**，ZCode MCP 已实测连通：

- **Edge 侧**：`edge://inspect → Remote debugging → 允许对此浏览器实例进行远程调试` 勾选一次即**持久化**（Local State 的 `remote_debugging` 键，重启浏览器保留）。Edge 正常启动（无任何参数）后自动在 9222 监听并写 `DevToolsActivePort` 文件。
- **授权弹窗是第二道门**：外部应用连接时 Edge 弹「是否允许远程调试？」，用户点「允许」后握手完成；短时间内的新连接免弹窗，但 Edge 重启后会再弹。**MCP 工具调用 30 秒超时多半是弹窗在等用户点「允许」，点完重试即可。**
- **端点特性**：HTTP 发现接口（/json/*）全部空 404，**只支持直连 WebSocket**（从 DevToolsActivePort 文件读端口+路径）。所以 `--browserUrl` 模式不可用，必须用 `--autoConnect`（它读文件直连 WS）。
- **ZCode 配置**：`~/.zcode/cli/config.json` → `mcp.servers["chrome-devtools"]` = `npx -y chrome-devtools-mcp@1.7.0 --autoConnect --user-data-dir=C:\Users\VOS-User\AppData\Local\Microsoft\Edge Dev\User Data`。
- **使用节奏**：Edge 照常任务栏启动（快捷方式无任何参数）；Edge 没开时 MCP 报 ECONNREFUSED 属正常，开 Edge 即可。
- **商店装扩展流程（实测可用）**：AI 用 CDP 打开 `https://microsoftedge.microsoft.com/addons/detail/<id>` 点「获取」；随后的安装确认小窗是浏览器原生 UI，**CDP 够不着，必须用户手点「添加扩展」**；**一次只装一个**——两个并发会报「将项目添加到 Microsoft Edge 时出现问题」，需刷新页面重试。

**扩展恢复终态（2026-08-23 早）**：用户只用 **ScriptCat（脚本猫）**，明确说之前没装过 Tampermonkey（勿装；`Sync Extension Settings` 里仍有 gmgoa 残留，同步日后可能自动装回，装回则用户手动移除）。已装回：脚本猫 liilgpjgabokdklappibcjfablkpcekh ✓（脚本数据完好）、简约翻译/KISS Translator jemckldkclkinpjighnoilpbldbdmmlh ✓、小电视空降助手/BilibiliSponsorBlock khkeolgobhdoloioehjgfpobjnmagfha ——**两个商店都装不上，改用 GitHub 解压版**。同步自动装回的：hkglf=Edge Flash Player（禁用属正常）、ghbmn=Google Docs Offline（预装）、cgjgj=Unminification、jmjfl=relevant text changes、kfbdp=DevTools Enhancements（后三个是 Edge 内部组件，曾报「无法加载扩展」，重启后自愈，勿从商店装）。

**空降助手安装失败结论（重要）**：Edge 商店与 Chrome 商店都报 `'Default locale is defined but default data couldn't be loaded'`/「包无效」；删 Sync/Local 残留、清缓存（`edge://settings/clearBrowserData` 只勾「缓存的图像和文件」，**必须取消 Cookie/历史**——Cookie 涉及 94 个站点登录态）均无效；GitHub 官方包 v0.13.0 验证完好（default_locale zh_CN、messages.json 有效 JSON、无 BOM）→ **判定这台机器 Edge 的商店 CRX 下载管线损坏（两个商店都坏），与网络代理无关**（GitHub 2.7MB zip 经代理 curl 下载完好）。**最终方案**：`https://github.com/hanydd/BilibiliSponsorBlock/releases/download/0.13.0/EdgeExtension.zip`（资产名是 EdgeExtension.zip，不是 ChromiumExtension.zip）→ 解压到 `C:\Users\VOS-User\Documents\EdgeExtensions\BilibiliSponsorBlock\src` → edge://extensions 开发人员模式「加载解压缩的扩展」（原生文件夹选择器只能用户手选）。代价：**无自动更新**，更新=重新下载覆盖。

**解压版加载也踩坑（2026-08-23，已解决 ✅）**：用户真实手势在 Chrome 商店点「获取」仍报「包无效：Default locale is defined but default data couldn't be loaded」（排除了手势因素）；随后解压版本地加载报**反向错误**「已使用本地化，但未在清单中指定 default_locale」——而 manifest 实际完全合法（顶层第 5 行 `"default_locale": "zh_CN"`，Node 解析通过）。根因（**对照实验证实**）：**Edge Dev 153 对下划线写法 `zh_CN` 的 default_locale 校验有 bug**——本机装成功的脚本猫/简约翻译/Flash 组件 default_locale 全是 `"en"`（都同样带 zh_CN 语言文件夹、中文界面正常），唯一用 `"zh_CN"` 当默认值的空降助手三条安装路全被拦。补丁：manifest 改 `"default_locale": "en"` 后用户重选 src 文件夹，**加载成功、已启用、SW 正常运行**（unpacked ID lnilohdmklhmicfgacedifldeheaenmb）。浏览器语言 zh-CN 仍优先取 zh_CN 翻译，功能不变。扩展恢复至此全部完成。

**已向官方/开发者双渠道反馈（2026-08-23 完成）**：① MicrosoftEdge/EdgeIssues 仓库 404 不存在；MicrosoftEdge 组织无通用浏览器 bug 仓库（DevTools/WebView2Feedback 等都太窄）；官方渠道=**浏览器内反馈 Alt+Shift+I**（已用 CDP press_key 代按弹出），用户已提交（确认页 `explore.microsoft.com/.../edge/feedback?channel=dev&cs=2270062458`，无独立反馈 ID 回报）。② 已在扩展仓库提 issue：**https://github.com/hanydd/BilibiliSponsorBlock/issues/316**（gh 创建，含对照实验、复现步骤、default_locale=en 临时方案）。后续若 Edge 修复或开发者改 en 默认值，可把本地解压版换回商店版。

**第二次官方反馈（2026-08-23 上午，青柠确认后，全部完成 ✅）**：① 用户已通过 Alt+Shift+I 提交**双扩展版报告**（khkeo + pcpnig，含 CRX 直链解包验证 zh_CN 的证据、对照实验，确认页 `explore.microsoft.com/zh-cn/edge/feedback?channel=dev&cs=2270062458`）。② **B 站私信已发送**给青柠作者「是毛布斯呀」(space.bilibili.com/14193369)：用户扫码登录其 B 站账号（19201640751），CDP 填好 389 字精简报告（现象/根因/对照/临时方案/已报微软），用户过目后点发送；**B 站限制对方未回复前只能发一条**，勿再发。注意：**Alt+Shift+I 经 CDP press_key 不一定弹出**（可能被原生弹窗抢焦点），失败就请用户手动按。青柠**无官方 GitHub 仓库**（搜到的都是第三方），开发者只能微博/B 站联系。至此反馈渠道闭环：**微软官方 ×2 + GitHub issue #316 + B 站私信**。青柠起始页已确认装上（Secure Preferences 10:19 注册）。

**浏览器操作补充经验**：① Chrome 商店「获取」需真实用户手势，CDP 程序化点击会报 `is not a valid extension ID`；② CDP `new_page` 打开 edge:// 页面会静默失败，须先建普通页再 `navigate_page` 过去（清缓存后首跳常超时 10s 但实际已加载，重试 snapshot 即可）；③ `edge://inspect` 顶部「Microsoft Edge 正由自动测试软件控制」横幅=远程调试开启的正常提示，**勿点「在设置中关闭」**（会断开 AI 接管）；其 Pages/Extensions 页签只是 DevTools 目标查看器，与装扩展无关。

**历史教训（勿重蹈）**：① `--remote-debugging-port` 对默认用户数据目录无效，显式传同一路径、注册表 RemoteDebuggingAllowed 策略、junction 改路径均无效或危险——junction 曾触发 Edge Profile 完整性保护，**把用户全部扩展注销清空**。② PowerShell `Start-Process -ArgumentList` 数组含空格元素必须内嵌引号，否则被拆参。

**青柠起始页补装与根因再确认（2026-08-23 上午）**：用户指出扩展未装齐并再次强调 **Tampermonkey 完全不需要、勿装**。审计发现漏了**青柠起始页 / Lime Start Page（pcpnigdkpcgemocnjhebmajldpjlbeom，新标签页起始页，即 limestart.cn）**——首次盘点用了 `ls | head -8` 截断，字母序在 khkeo 之后的扩展（含它和当时在运行的脚本猫）被漏数；教训：**盘点扩展目录必须完整 ls，勿截断**。其商店安装同样报错，用 CRX 直链下载验证 manifest 也是 `"default_locale": "zh_CN"`——第二个 zh_CN 受害者，同时**推翻此前「本机 CRX 下载管线损坏」的猜测**（直链 26.6MB 下载完好）。已按同方补装：解压到 `C:\Users\VOS-User\Documents\EdgeExtensions\LimeStartPage\src`（**商店 CRX 解压后须删 `_metadata` 目录**再加载）、default_locale 改 en、用户手选文件夹加载（截至记录时待用户确认结果）。起始页个人配置靠 limestart.cn 账号云同步恢复。**CRX 直链（可绕商店 UI 下载检查）**：`https://edge.microsoft.com/extensionwebstorebase/v1/crx?response=redirect&prod=chromiumcrx&prodchannel=Stable&x=id%3D<扩展ID>%26installsource%3Dondemand%26uc`。

**用户最终决策（2026-08-23）**：拒绝换 Thorium、也拒绝「MCP 自管专用 Profile」模式——**目标就是接管原封不动的日常 Edge**，接受每个浏览器新会话点一次「允许」的代价。Thorium 调研结论（备查）：gz83/thorium（Alex313031/thorium 的维护者 fork）M151=Chromium 151 稳定基座、无自动更新、无 CDP 魔改；**逐次连接授权弹窗是 Chromium 144+ 上游行为**（chrome-devtools-mcp issue #825/#1794 请求「记住授权」未实现），换任何 Chromium 系浏览器都躲不掉；零弹窗唯一路径是 MCP 自管启动模式（--executablePath + 专用持久 Profile）。另实测：远程调试授权有时跨天/跨多次连接仍有效（某日上午首次连接未弹窗），持久性强于最初预期。

**最终落定（2026-08-23，全部完成 ✅）**：① 解压版扩展统一迁至 **`D:\extensions\`**（用户明确不喜欢放 C 盘）：`BilibiliSponsorBlock\src`、`LimeStartPage\src`、`better-XiaoHeiHe-main`（=小黑盒扩展 better-XiaoHeiHe，用户原装的就是它的解压版，此前漏数因 head 截断+无数据痕迹；已顺手升级到最新 v1.2）。C 盘旧 `Documents\EdgeExtensions\` 已删。② 三个 manifest 均已：default_locale 改 `en`、**写入随机生成的 `key` 字段固定 ID**（以后移动文件夹 ID 不变、数据不丢；生成脚本已存 D:/extensions/tools/pin_keys.mjs：RSA SPKI base64 → manifest.key）；小黑盒还补建了 `_locales/en/messages.json`（复制 zh_CN 的，否则改 en 后报「未指定 default_locale」）。③ 用户自行完成三次「加载解压缩的扩展」，全部启用。④ 小黑盒官方 issue 已提：**https://github.com/k1m0206/better-XiaoHeiHe/issues/13**。⑤ 注意：空降助手/青柠因换路径+新 key 获得了**新 ID**，旧 Local Extension Settings 数据未跟随（损失极小：空降助手的跳片段偏好、青柠靠账号云同步）。

**BewlyCat 补装（2026-08-23，最后一个补齐 ✅）**：用户再指出缺一个——**BewlyCat**（B站主页美化、BewlyBewly 系，ID gefpmpkmhbkckhdbajnblcpjnlfegoke）：它是**本地解压加载**的，无 Extensions 目录痕迹，只在 Local Extension Settings 有数据（B站 accessToken/mid + 视频观看记录，8/16 还活跃）；源文件夹 **D:\extensions\BewlyCat-chrome-extension** 仍在且 manifest 自带 key（故 ID 稳定），重新加载后登录态/历史数据原地恢复 ✓。jdiccldimpdaibmpdkjnbmckianbfold=**Microsoft Voices**（Edge 内置朗读组件，预装勿动）。另：空降助手条目上的「错误」按钮=B站页面上的内容脚本运行时报错（与 BewlyCat 同时改 B 站页面所致的老毛病，可无视）。

相关：[[user-windows-environment]] [[openrouter-chinese-plus-project]]

**知识库成文（2026-08-23）**：应要求把「AI 接管 Edge」方法论整理进 youshouldknow——新建 **AI工具 分类（第 14 个分类）**，文章 `docs/AI工具/Edge浏览器CDP远程调试与AI接管指南.md`，提交 `67f7e2d` 已推送（mkdocs --strict 本地验证通过；mkdocs.yml nav、根 README 分类数、AI工具/README 均同步更新）。后续同类内容（MCP、AI 工具链）归入该分类。

相关：[[user-windows-environment]] [[openrouter-chinese-plus-project]] [[youshouldknow-doc-details]]


2026-09-01 更新：BewlyCat 已从 D:\extensions\BewlyCat-chrome-extension（1.6.9 本地解压版）更换为 1.7.8 Edge 商店版。1.6.9 实测会瞬时注入 #bewly-bottom-comment-style（与 AveMujica 共享 id），1.7.8 无此 id——mbgt 项目的 avemujica 标记停用裁定基于 1.6.9，对新版无影响。

**加载解压缩扩展的自动化教训（2026-09-01，mbgt Plan3 冒烟）**：computer-use 驱动 edge://extensions「加载解压缩的扩展」的原生文件夹选择框失败——`type` 报内部错误 `Cannot read properties of undefined (reading 'timeoutMs')`，坐标点击频报 "frame is stale"，且页面出现「无法加载扩展」横幅（很可能选错目录：应选**含 manifest.json 的子目录本身**，如 `packages\extension\dist`，勿选其父目录）。可行节奏：按钮用 AXPress 元素点击（element target，勿用坐标）；文件夹手选这类原生 UI **直接请用户代劳**——用户明确表示愿意手动完成并回报结果（截图自动化读取太慢），这是顺畅路径，勿硬磕自动化。
