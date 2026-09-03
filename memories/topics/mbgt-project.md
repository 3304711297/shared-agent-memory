---
name: mbgt-project
description: 新项目 make-bilibili-great-together（桌面）：接手 SukkaW MBGT-EB，双形态
  userscript+MV3，主兼容 BewlyCat
metadata:
  node_type: memory
  type: project
  originSessionId: sess_5aaf10dd-f320-4323-9c4e-f0fba4ee03cf
---

用户 2026-08-30 启动新项目 `make-bilibili-great-together`，位于 `C:\Users\VOS-User\Desktop\make-bilibili-great-together`（仅本地仓库，尚未推 GitHub）。

关键拍板（spec 在 `docs/superpowers/specs/2026-08-30-make-bilibili-great-together-design.md`）：
- 接手 SukkaW/Make-Bilibili-Great-Than-Ever-Before（MIT，新仓库移植其架构，非 fork）
- 双形态：Monorepo 三包共享 core，userscript（ScriptCat）+ MV3 扩展（DNR + options 复用面板）
- 主兼容 BewlyCat、次兼容 AveMujica；模块带 compat 元数据，DOM 特征探测自动禁用重复模块
- 点睛功能三个：CDN 智能选优（range 探测/2s 超时/5min 缓存）、拦截统计看板（30s 节流落盘）、设置+共存面板（Preact）
- 发版沿用 tag-only + 自动 notes 纪律；协议 MIT 保留 SukkaW 署名
- 冲突表 optimize-story 两项待真机实测定稿

状态：Plan 1+2 已合并 main 并推送（CI 绿），真机冒烟已完成（2026-09-01，Edge Dev+ScriptCat1.4+BewlyCat1.6.9 实测）：安装/更新链路✓、15 模块即时+延迟装配✓、defuse-spyware（Sentry mock 0.0.1145141919810/sendBeacon 恒真）✓、disable-av1（isTypeSupported false）✓、共存探测 settle 后 6 冲突模块 auto-disabled✓、视频页 #bewly 宿主存在✓（确认项①解除）。冒烟发现并修复 2 项（0dd7c84/580e3b1）：#bewly-bottom-comment-style 非 AveMujica 独有（BewlyCat1.6.9 也瞬时注入）已移除该标记→AveMujica 走 generic 保守并集；generic 归因标签改为 'generic'。已知遗留：首页 BewlyCat 标记瞬态致常落 generic（合并 Plan 4 面板前找稳定标记）；abort 路径下 B 站自带 bound setRequestHeader 抛 InvalidStateError 噪音（可改 abort 时仍 super.open+noop send，Plan 3 处理）；iframe 实例无扩展时 10s 后冲突模块全启用（预期）。用户浏览器操作链路：CDP 连接要点掉'是否允许远程调试'弹窗（computer-use 元素点击）；ScriptCat 安装页 a11y 可点「更新」；CDP list_pages 不显示 chrome-extension:// 页；extension:// 新开页 ERR_ABORTED；github push 直连偶发 reset 需 -c http.proxy。**Plan 3（MV3 扩展）代码全部完成，CI 绿（2026-09-01，sess_5aaf10dd）**：SDD 6 任务（T1 core 加固 55 测/T2 家族快照入 core 62 测/T3 storage 桥 MAIN↔ISOLATED 66 测/T4 扩展包+browser??chrome 双解析/T5 CI+README，最终修复波次 9d73a2f 8/8 重审通过，core vitest 67/67、三包 tsc 零错误）。manifest 含 minimum_chrome_version 111、DNR 拦 data.bilibili.com/cm.bilibili.com。Ruling（影响 Plan 4）：treeshake 把 avemujica 开关编译消除→面板不得做运行时开关，需接线层传参。**卡点=Task 6 真机冒烟**：edge://extensions 加载解压缩扩展自动化失败（「无法加载扩展」横幅+文件夹对话框 computer-use type 报内部错误），manifest 已验证合法 → 大概率选错目录；**正确目录=`packages\extension\dist` 本身**（manifest.json 等 6 文件在其根下，勿选 packages\extension）。用户主动提出代劳手动加载，成功与否以其回报为准。冒烟 6 项：注入/DNR 拦截/与 BewlyCat 1.7.8 共存/compat status；**先禁用 userscript 版防双装**；BewlyCat 1.7.8 缺 #bewly-bottom-comment-style id，1.6.9 时误判修复需复验首页标记行为。冒烟通过后收尾并启动 Plan 4。相关 [[superpowers-usage]] [[edge-dev-cdp-mcp-setup]] [[user-windows-environment]]
