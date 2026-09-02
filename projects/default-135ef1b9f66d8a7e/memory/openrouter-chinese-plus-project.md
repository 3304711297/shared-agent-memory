---
name: openrouter-chinese-plus-project
description: 桌面 openrouter-chinese 三合一油猴脚本项目；GitHub 仓库
  3304711297/openrouter-chinese-plus；含上游词库自动同步机制；用户脚本管理器是 ScriptCat
metadata:
  node_type: memory
  type: project
  originSessionId: sess_619b1ebc-599b-48a5-ac7f-6eb15deb6d77
---

桌面 `C:\Users\VOS-User\Desktop\openrouter-chinese\` 是三源合并的油猴脚本项目（2026-08-21 创建），发布目标为 GitHub 仓库 **3304711297/openrouter-chinese-plus**（gh CLI 登录账号 `3304711297`，昵称"智商已更新"）。

- 组装：`node build.mjs` 把 `sources/datou-locals.js` + `sources/datou-main.user.js` + `cny-price.module.js` 拼成单文件产物 `openrouter-chinese-plus.user.js`（构建生成勿手改）
- 取舍：datou1996 引擎+词库整体采用（MIT）；LynnGuo666 人民币价格功能仅借鉴思路、代码全部重写（其 PolyForm Noncommercial 禁止商用，不能复制）；isdoge 未并入（覆盖子集且停更）
- **上游自动同步机制**（2026-08-21 搭好并本地验证）：`upstream.config.json`（repo + mirrors 镜像回退列表）→ `scripts/check-upstream.mjs`（SHA-256 比对快照；有更新覆盖 sources/ 并 buildNumber+1；退出码 10=有变更、0=无变更或上游不可用）→ `upstream.state.json`（哈希、词库版本、buildNumber）→ `.github/workflows/upstream-sync.yml`（每 6 小时 cron + workflow_dispatch，有变更才重新构建并以中文 commit 推送）
- **上游消失兜底**：sources/ 是完整 vendored 快照，上游删除/断网时工作流保持绿色、构建发布不受影响，只是不再跟进新词库；archived 仓库的 raw 文件仍可拉取；上游真死了把 fork 加进 config 的 mirrors 即可，无需改代码
- **版本规则**：`<ourBase>.<buildNumber>`（如 1.0.2）；ourBase 是 build.mjs 常量、功能性改动时手动递增，buildNumber 随上游实际更新自动 +1，保证脚本管理器能识别自动更新
- **远程安装**：@downloadURL/@updateURL 指向 `raw.githubusercontent.com/3304711297/openrouter-chinese-plus/main/openrouter-chinese-plus.user.js`
- 用户的脚本管理器是 ScriptCat（脚本猫），不是 Tampermonkey
- 进度（2026-08-21）：**已全部完成**——仓库已推送，workflow 手动触发验证绿色（CI 直连正常），远程产物 raw 链接可拉取（@version 1.0.2，词库 v1.5.22）
- **churn 修复已端到端验证**（ed28c35）：原实现每次运行都因 `checkedAt` 时间戳变化落盘状态文件，导致每 6h cron 产生空提交；修复为仅词库哈希/版本/buildNumber 实质变化才写 `upstream.state.json`。修复后手动触发 workflow（run 32475063430）成功且远端无新提交，确认生效
- **教训**：check-upstream 的 curl 回退必须带 `-f`——不带时 HTTP 404 页面 body 会被当正常内容写入快照（模拟上游消失时抓出，属数据毁坏级 bug）；Node fetch 不走系统代理（本机 `127.0.0.1:3067`），本地跑需依赖 curl 回退
- OpenRouter DOM 特性：React 把价格拆成 [$]["0.044"]["/M tokens"] 多个文本节点，且事后四舍五入修正价格数字，价格类脚本两种情况都要处理

- **外部 AI 四点工程复审（2026-08-21，用户批准后已全部修复并推送，三仓库 CI 绿）**：① tweakbyjie Coverage 审计漏检——已修，见 [[cross-repo-coverage-audit]]；② 缺功能测试——已修：cny-price.module.js 可测性改造（IIFE 安全传参、document 存在性守卫、Node 下 module.exports 导出纯函数与 state），tests/cny-price.test.cjs 25 项单测（node:test 零依赖，删 require 缓存隔离，stub GM_*/window/Node），新增 push/PR 触发的 ci.yml（build + node --check + 单测 + `git diff --exit-code` 产物漂移守卫）；③ workflow 忽略退出码导致 unavailable 状态触发无意义重建——已修（`977c75c`）：重建仅由 exitcode==10 驱动，git diff 只决定是否提交，状态记录提交用独立信息；④ ourBase 双源——已修（`4dcfc3b`）：state.json/loadState 的 ourBase 已删，build.mjs OUR_BASE 常量唯一权威。相关提交 a9e5678（测试+CI）、811654d（注释补充）。**教训**：本机裸 `node --test`（自动发现模式）会挂死，必须显式给文件路径 `node --test tests/cny-price.test.cjs`（CI 同）；isMarked 无兄弟节点时短路返回 null 而非 false，测试断言需用真值判断。

- **SPA 生命周期修复（2026-08-21 第二轮审计，`25f1f2c`，OUR_BASE 1.0→1.1）**：① 参考价标记由裸文本节点改为带 `data-openrouter-cny` 属性的 span（isMarked/去重/刷新同步改为元素+属性判定）；② rescanAll 在 `/chat`、`/fusion` 等禁用页主动 removeAllMarks——此前 SPA 从 /models 切到 /chat 只停止扫描，旧标记残留到手动刷新；③ removeAllMarks 只删本模块属性节点，不再按"长得像 ≈¥数字"全页匹配（消除误删页面原生同形文本）；④ 周期定时器句柄存 `state.rescanInterval`。测试 25→30：新增最小伪 DOM 生命周期套件（路由清理/切回恢复/精确移除/价格刷新/跳过容器）。**伪 DOM 教训**：必须实现真实 DOM 属性名（漏掉 `parentNode` 别名时模块静默 TypeError 被 try/catch 吞掉）；伪 document 的 readyState 设 `'loading'` 让自动启动挂起在永不触发的 DOMContentLoaded 上，避免真实 setInterval 挂死测试进程；本机裸 `node --test` 自动发现模式会挂死，须显式文件路径。

**Why:** 上游是个人项目随时可能停更，vendored 快照 + 镜像配置让本项目生命周期与上游解耦。
**How to apply:** 改动此项目时先跑 `node scripts/check-upstream.mjs && node build.mjs && node --check openrouter-chinese-plus.user.js`；涉及交付物默认考虑 ScriptCat 兼容性。

**Related:** [[user-windows-environment]] [[openrouter-chinese-scripts-comparison]]
