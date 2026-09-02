---
name: steamdb-chinese-plus-project
description: 桌面 steamdb-chinese 油猴脚本项目；GitHub 仓库
  3304711297/steamdb-chinese-plus；接续停更的 GreasyFork SteamDB_CN(437076)，词库
  Chr233/GM_Scripts AGPL-3.0 自动同步
metadata:
  node_type: memory
  type: project
  originSessionId: sess_19bf06e3-9812-4e80-89fc-84a6aa45b9e5
---

桌面 `C:\Users\VOS-User\Desktop\steamdb-chinese\` 是 SteamDB 中文化油猴脚本项目（2026-08-30 创建），发布仓库 **3304711297/steamdb-chinese-plus**（gh 账号 3304711297），初始提交 `3381af3`，产物 `steamdb-chinese-plus.user.js` v1.0.1（1423 词条）。用户此前用的 GreasyFork 脚本 437076 SteamDB_CN（作者 Chr_）已停更，本项目接续。

- **上游真相（踩坑）**：词库真实仓库是 **Chr233/GM_Scripts**（分支 master，路径 SteamDB/SteamDB_CN.json）——`Chr_/GM_Scripts` 是 404；`raw.chrxw.com/GM_Scripts/...` 是作者自有 CDN（与 GitHub 逐字节一致）；词库版本号在 `DOC["更新时间"]` 字段。上游许可证 AGPL-3.0，本项目整体跟随
- 词库结构（与 HF 项目不同）：`DOC/STATIC/INPUT/LABEL/DYNAMIC`，STATIC 与 DYNAMIC 是 **CSS 选择器作用域词典**（选择器→词典），选择器精确匹配本身就是安全机制，引擎无需 unsafe 区；上游引擎只加载时翻译一次，我们补了 MutationObserver + requestIdleCallback 动态翻译并实装了上游标注"暂未实装"的 DYNAMIC 段
- 引擎与 i18n-core 同 HF 项目模式（[[huggingface-chinese-plus-project]]）；补充词库 `sources/steamdb-supplement.json`（允许空，build 容忍）；check-upstream 的 `cdn` 配置支持**字符串或数组**（jsDelivr + raw.chrxw.com 两个兜底）
- 验证状态（2026-08-30）：22 项单测全绿、CI 绿、upstream-sync 手动触发绿且无 churn、raw 链接 200；**真机冒烟通过**（steamdb.info 隔离上下文注入裁剪词库：导航/placeholder/aria-label/h1/表头翻译 + MutationObserver 探针 2 秒内翻译"附加信息"）。注意 steamdb.info 页面 CSP 拦外部 fetch，CDP 注入需分两步（先 evaluate 设 window 变量装词库、再注入引擎）
- **覆盖率实测（2026-08-30，v1.1.1）**：隔离上下文爬 8 个页面提取约 2500 条未命中文本，人工甄别补 136 词条 + **新增 REGEX 正则规则段**（分页/计数动态文案，引擎与 i18n-core 同步支持 compileRules/lookupRegex，补词库 REGEX 段格式 `[pattern, replacement]` 必须锚定 ^$）；有意不翻：游戏名/价格/专有名词（tech 页）/被链接拆碎的句子片段。报告存 `docs/coverage-2026-08-30.md`。已知缺口：标签词不全（400+ 只覆盖高频）、跨节点句、/badges//calculator//packages/ 与登录后页面未爬。26 项单测全绿、CI 绿、raw=1.1.1
- **引擎坑**：translateElementTexts 只翻直接文本子节点，嵌套文本依赖上游选择器覆盖路径（如 `tr>th span`）——选择器有遗漏时在 supplement 加选择器而非改引擎
- **评审修复（2026-08-30，v1.2.1，OUR_BASE 1.2）**：① build.mjs supplementHasEntries 补上 REGEX 段（REGEX-only 补充词库不再被误判为空，有回归测试）；② MutationObserver 增加 `attributes:true + attributeFilter:['placeholder','aria-label']`，属性变更走单元素轻量直译（中文回写无字母必然空跑，无死循环），真机验证动态 setAttribute 500ms 内自动翻译。27 项单测全绿、CI 绿、raw=1.2.1。注意：git push 遇 Connection reset 时用 `git -c http.proxy=http://127.0.0.1:3067 push` 显式走代理
- **第二轮覆盖实测（2026-08-30，v1.2.2，buildNumber 手动 1→2）**：爬搜索/资产库/历史/SUB/捆绑包/徽章/计算器/404（匿名）+ 登录态 Your Games/Your Wishlist/设置页（用户已登录标签页，未开新窗）；+108 静态 +12 正则（徽章年度活动名按年份正则批量、时长倒计时、设置页绑定/会话/审计日志整块），词条累计 1667。**教训**：SteamDB 登录与 Steam 商店登录独立（OpenID）；steamdb.info 无 /wishlist/ 路径，个人页在 /sales/?displayOnly=OwnedGames|Wishlist 和 /user/；CF Turnstile 在 CDP 主档案会卡"验证成功等待响应"循环，需桌面控制真点一次复选框才过
- **第三轮补爬（2026-08-30，v1.2.3）**：应用户要求补爬榜单页——路径勘误：榜单真实路径在 **/stats/** 下（globaltopsellers/mostfollowed/dailyactiveusers/gameratings/releases），/charts/globaltopsellers/ 等是 404；仅 +3 个榜单页 h1（"Top Currently Global Selling Steam Games" 等），其余内容此前轮次已覆盖；/user/ 深区块（Games by time played 等）属于计算器个人报告页非 /user/。**第三轮增量极低 = 全站主路径已扫完，转入日常"输出未命中词"反馈模式**，不再主动爬页
- **CPU 风暴事故（2026-08-30，v1.3.3，OUR_BASE 1.3）**：用户 ScriptCat 安装后 SteamDB 整页卡死、CPU 吃满、迟迟不汉化。**根因**：document-start 注入 + 站点水合渲染产生大量脱离文档的临时文本节点，旧引擎 `pendingRoots.push(parentElement || document.body)` 对每个孤立节点退化为全页×58 选择器扫描 → 数百次全页扫描吃满主线程。**CDP 注入测试没暴露**（注入时页面已渲染完）——userscript 引擎必须在 document-start 时序下测加载期。修复三处：孤立文本节点忽略（插入时经 childList 进来）、WeakMap 自写回写守卫（文本+属性，防自反馈与多翻译扩展互触）、队列去重+超 300 根合并为单根全页扫+单轮预算。**教训入档：AI 助手另一会话（ZCode 窗口）在跑"HuggingFace 汉化脚本"评审，用户会把两边结论互相转述**
- **性能回归测试（2026-08-30，v1.4.3，OUR_BASE 1.4）**：外部 AI 评审指出事故防护零自动化覆盖 → 新增 `tests/engine-dom.test.mjs`（node:vm + 伪 DOM 垫片直接跑 engine.js，6 项断言：孤立节点忽略/文本自写零重扫/他改仍重查/属性自写守卫/洪水 400 节点扫描上界≤10/全翻对）。**咬合力已验证**：旧引擎 4/6 变红。**测试反哺修出两处真缺陷**：①lastAttrWrite 每元素单槽位，同元素写两个属性互相覆盖致守卫失配 → 元素→属性名→值 三级 Map；②洪水合并出全页根后细粒度根仍漏进队列逐根扫 → pushRoot 遇 body 在队直接跳过。CI 单测命令已含 engine-dom，33 项全绿。**教训：与 git worktree 对照跑测试时，`git show HEAD~1:file > file` 会覆盖未提交修改，checkout 恢复的是 HEAD 不是刚才的编辑——先提交再对照**
- **性能事故闭环（2026-08-30）**：用户真机确认 v1.4.3 卡顿消失、汉化秒出——CPU 风暴事故彻底关闭，项目进入长期维护阶段。维护模式：漏翻词靠用户"输出未命中词"攒词条进 supplement（纯词条 → 手动 bump buildNumber 末段）；引擎/功能改动 → OUR_BASE 前两段递增；改 engine.js 必跑 engine-dom 回归测试
- **待办**：无急项

**Why:** 与 openrouter/huggingface 两个 plus 项目同族第三项目，维护契约一致。
**How to apply:** 改动后跑 `node build.mjs && node --check steamdb-chinese-plus.user.js && node --test tests/i18n-core.test.mjs tests/check-upstream.test.mjs`；本地跑 check-upstream 需带 `https_proxy=http://127.0.0.1:3067`。

**Related:** [[huggingface-chinese-plus-project]] [[openrouter-chinese-plus-project]] [[user-windows-environment]]
