---
name: bilibili-great-together-project
description: make-bilibili-great-together：B 站双形态（userscript+MV3 扩展）monorepo 接手
  SukkaW 脚本；Plan 1-5 + P2 收尾 + Issue#1 真机实测全部完成，v0.3.0 已发版，
  main@6ecf235；当前序列=②全自动发版设计已呈现待批准 → ③待办池 → ④发 0.3.1（全自动首跑验证）
metadata:
  node_type: memory
  type: project
  originSessionId: sess_5aaf10dd-f320-4323-9c4e-f0fba4ee03cf
---

2026-08-30 用户提出：做一个脚本或扩展**接手** https://github.com/SukkaW/Make-Bilibili-Great-Than-Ever-Before（最终发布到 GitHub），主兼容 BewlyCat、次兼容 BewlyBewly! AveMujica，融合三者优点（"画龙点睛"）。经 superpowers:brainstorming 流程（architectural 路径）逐项拍板：

- **形态**：Userscript + MV3 扩展双形态（用户自选，未采纳纯脚本推荐项）
- **功能范围**：核心继承 + 共存感知（继承 SukkaW 全部 15 模块并持续维护；检测到 BewlyCat/AveMujica 时自动关闭重复模块；不做深度融合 UI——用户明确否掉吸收扩展 UI 类功能）
- **代码基座**：新仓库、移植 SukkaW 架构（MIT 保留版权+致谢），不 fork 不重写，保留 cherry-pick 上游更新的能力
- **点睛功能**（三选三全要）：①CDN 智能选优（SukkaW 现在是 pickOne 随机镜像，改为延迟探测+失败换源）②拦截统计看板（展示被拦的跟踪/上报/PCDN/P2P 数）③设置+共存面板（页面内设置面板，扩展侧复用为 options 页，展示检测到哪个扩展、哪些模块被自动禁用）
- **技术方案**：A 单核双产物 pnpm monorepo——packages/core（引擎+模块+features+platform 存储适配接口）、packages/userscript（rollup 单文件 .user.js）、packages/extension（MV3：MAIN world document_start 注入同一份 core + declarativeNetRequest 静态规则挡 data/cm.bilibili.com 上报 + options 页）
- **共存感知设计**：模块带 compat 元数据（conflicts: [{extension, feature}]），MutationObserver 探测扩展注入的 DOM 特征，命中即自动禁用并在看板标注原因；用户可在面板强制开启（手动覆盖优先）；两扩展同装时以 BewlyCat 冲突表为准
- **仓库名（已拍板）**：`make-bilibili-great-together`（2026-08-30 用户从三候选中选定）

设计分节确认进度（2026-08-30）：
- 第 1 节（架构+仓库结构）、第 2 节（模块系统+共存感知）：用户确认"没问题"
- 第 3-5 节已呈现，要点：**CDN 选优**=range 段探测候选镜像（2s 超时、失败淘汰、延迟排序、结果缓存 5min、全败回退 SukkaW 随机策略；名单不含 SSL 有问题的 14b 镜像；脚本侧 GM_xmlhttpRequest+新增 @connect 绕 CORS，扩展侧 host_permissions）；**拦截统计**=按模块归因计数、内存累积 30s 节流落盘、右下角可收起角标默认关；**设置+共存面板**=Preact（约 4KB gzip）、含强制开启覆盖/导入导出 JSON/扩展侧复用为 options 页；存储统一 `mbgt:` 前缀+版本迁移；面板/统计崩溃不影响核心拦截（独立入口降级）；测试 Vitest（伪 XHR/fetch 环境测 hook 引擎、伪造特征 DOM 测 compat）；发版沿用用户纪律 tag-only+自动 notes+jsDelivr /gh 通道；扩展不打商店走 Releases zip；MIT 保留 SukkaW 版权头+致谢三上游
- **待办**：等用户确认第 3-5 节 → 写设计文档到 docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md → writing-plans

相关调研见 [[bilibili-enhancement-tools]]（三工具对比、重叠四块、脚本独有功能清单）。

## 2026-09-01 执行状态（Plan 3 完成）

仓库 `C:\Users\VOS-User\Desktop\make-bilibili-great-together`（GitHub 3304711297/...，main）。

- **Plan 1+2 userscript、Plan 3 MV3 扩展均已完成**；SDD 账本重建于 `.superpowers/sdd/2026-09-01-plan3-extension/progress.md`（原 ledger 文件丢失，gitignored）
- 扩展 id `naephbpbijnomloddmldmgmfcjhikbac`（unpacked，dist=`packages/extension/dist`），Edge Dev 154 + BewlyCat 1.7.8 真机冒烟 6 项全过：注入✓ DNR 拦 data/cm✓ pending-family→generic 结算✓ compat status 落盘✓ 桥接端到端✓ userscript 停用✓
- **冒烟抓到核心缺陷并修复 `af32a15`（CI 绿）**：defuse-storage mock `length` 自引用炸栈（单全局域 bare localStorage=mock 自身），视频页 force-enable-4k onVideo 钩子触发后整个 dispatch 循环死掉；修复=length 读闭包原引用 + scheduler dispatchOne 单模块 try/catch 隔离。**铁律：钩子内读被 mock 的全局必须走闭包捕获的原引用**
- Plan 4 ruling：treeshake 消除 avemujica 运行时开关→面板不得做运行时开关，接线层传参；deferred 模块依赖 onSettle 注册；BewlyCat 特征标记只在视频页出现（首页结算走 generic 保守并集，Plan 4 可做延迟命中）
- push 需 `git -c http.proxy=http://127.0.0.1:3067 push`

## 2026-09-01 执行状态（Plan 4 进行中，SDD subagent-driven）

计划：`docs/superpowers/plans/2026-09-01-plan4-golden-trio.md`（12 任务，已入仓库）；账本：`.superpowers/sdd/2026-09-01-plan4-golden-trio/progress.md`；工作分支 **plan4-golden-trio**（BASE af32a15，已推 origin）。

- **T1-T11 全部完成并通过任务级审查**（每任务一个 implementer 子代理 + 独立 task reviewer，fix round 0 全程零返工）：
  - T1 737fe9d 存储语义统一（mbgt:override:* 三值 on/off/force-on + KVStore.getAll + 旧键 mbgt:enabled:* 迁移）
  - T2 88facc4 统计注册表（flushedBaseline 推进移到 set 成功后——brief 逐字代码被其自测证伪，裁定以"写盘失败不丢增量"为准）
  - T3 571710b 五模块埋点（beacon/spyware-fetch/spyware-xhr/storage-defused/p2p-replaced/rtc-mocked/av1-blocked）
  - T4 560638c background DNR 统计（onRuleMatchedDebug，unpacked 专属）+ manifest 扩容（bilivideo host_permissions/declarativeNetRequestFeedback/service_worker）
  - T5 01603fd CDN 探测状态机 + cdnUtil hooksRef 懒挂接线
  - T6 8aa2075 三端探测通道（GM_xmlhttpRequest / 桥接 isolated 裸 fetch）+ readSettingsWithBudget 预算回退；修复 T1 的 unknown-action 误删键缺陷
  - T7 cbc5e0e 统计角标；T8 680f652 面板模型（两处 brief 缺陷裁定修正：enabled=引擎注册语义、DNR rule-id 归并单一 'dnr' kind）
  - T9 3253844 Preact 面板（h() 调用树无 JSX）+ version.ts 单源 + userscript 浮层收口（.user.js gzip +11.3KB）
  - T10 eded695 options 页完整面板（直连 storage.local，即时模块 locked）；T11 e1e4893 版本 0.2.0 三处 + README 三段 + 分支推送
- **子代理模式经验（Plan 4 验证有效）**：brief 常有"参考实现过不了自带测试"的笔误级缺陷（T2/T8 两例同型），reviewer 用 brief 自带测试期望值裁定必要适配；preact 进 core 依赖、extension 也需 devDep（pnpm 隔离下 tsc 看不到 core 依赖类型）
- **冒烟状态（T12 进行中）**：产物断言已本地复核（.user.js @version 0.2.0、zip 含 background.js、options.js 含面板）；用户当前状态=userscript 启用+扩展禁用；**等用户把 ScriptCat 里的脚本更新为 dist 新版后开始 userscript 冒烟，再切扩展冒烟（developerPrivate 启用/重载全自动），结束时恢复用户原状态**
- 发版流程：冒烟→最终全分支审查→合并 main→tag v0.2.0（tag-only 纪律，tag 前需用户确认）
- 已知取舍（面板/README 已写明）：扩展即时模块锁定不可关（document-start 语义）；cdn:probe=false 扩展形态下页首跳探测仍可能发生；DNR 计数依赖 unpacked；面板数据为打开时快照

## 2026-09-01 Plan 4 收尾完成（main @ b2f180e，v0.2.0 已发版 ✓）

- T12 冒烟 12 项全过 + 最终全分支审查 ✅ 可合并 + 修波次 b47a960（迁移移出 document-start 关键路径：同步先行段=守卫+菜单+createCore+probe，异步段=迁移+deferred+UI）；合并 main 47a98b1，CI 绿
- **冒烟抓到 3 轮缺陷全修复并真机复验**：① correspond iframe 覆盖 compat 状态（top-frame.ts 顶层守卫，非顶层仅核心派发）② DNR 键名（Edge 154 实测 rule={ruleId, rulesetId} 与 Chrome 文档 ruleIds 不符，四级回退，真机键变 "1"；诊断探针 b7e0429→已移除 56a715f）③ 同步先行段重构
- deferred minors 18 项终审全 OK-TO-SHIP；1 项 parked：badge/面板合计口径差（角标无 DNR 合并、flush 后重叠计数）——Plan 5 议题
- 复验期间实证：userscript 在场时 DNR 事件为 0（defuse-spyware 先拦）=二选一铁律的运行时证据；example.org 页可发 bilibili 请求触发纯 DNR 事件（用户脚本不在场的隔离通道）
- 浏览器操作经验：developerPrivate 无 setEnabled（用 chrome.management.setEnabled，edge://extensions 页上下文可用）；扩展重载后旧页 content script 上下文失效（桥接 ok:false），须刷新页面再读；扩展重载后同 tab 未重注入，须 navigate/reload 才带新脚本
- 用户状态已还原：userscript 启用（最终构建 0.2.0）+ 扩展禁用；**v0.2.0 已发版 ✓**（Release 资产 .user.js + extension.zip + 自动 notes，jsDelivr /gh 通道可用）；SDD 工作区已删、工作分支已删（本地+远端）
- 发版教训（记入后续仓库惯例）：tag-only 发版前必须确认 release.yml 已在 tag 所指提交（Actions 用 tag 提交的 workflow 定义）——mbgt 仓库首版曾因此 tag 推了却无触发，重指 b2f180e 解决

## 2026-09-01 Plan 5 启动（brainstorming 中，设计草案已呈现待确认）

用户选了 Plan 5（三点：CDN 选优精确化、统计口径统一、面板实时刷新）。按 architectural 路径，三个 AskUserQuestion 已答定：
- CDN 精确化=四项全要：A 首载不漏（cdnUtil 记 pendingProbe + hooksRef.current.cdnUtil 回填后 replayPendingProbe 补探）；B 缓存过期+30s 主动重探（定时器单飞，fake timers 测）；C selectMirrorUrl 改基于候选副本换宿主（天然 https，不再从 incoming 复制）；D 单候选已会探测，仅补面板文案
- 统计口径=归零语义（flushStats 成功后 session[k] -= delta[k] 保留间隙新增，删 flushedBaseline；T7-minor-2 根治）；附带增补待用户点头：badge mount 时读 DNR 键入基线使两处合计一致（终审 Minor-1）
- 面板实时刷新=打开期轮询（PanelApp 每 2s loadPanelData + useEffect cleanup；badge 保持事件实时 + 30s 低频重读基线含 DNR）
- 版本 0.3.0（tag v0.3.0 走既有 release.yml，发版前确认）；预估 4 任务 SDD（T1 registry 归零+badge DNR 基线 / T2 pendingProbe+selectMirrorUrl / T3 主动重探 / T4 轮询+版本+README）

## 2026-09-01 Plan 5 逐节确认通过 + spec 已落盘（main @ 84938ab）

用户逐节确认（§1-§4 全 ✅）并给出三条**冻结实现约束**（已逐字并入 spec §0，实现与测试必须钉死）：
1. pendingProbe 只保留最新一次未探测输入（覆盖语义不累积队列）；replayPendingProbe 幂等——回放即清空，重复调用不得重复探测
2. flushStats 单飞——并发/重叠 flush 不得对同一 delta 重复扣除（实现保证或既有实现+测试钉死）
3. badge 与 panel 同合计口径；DNR 基线实时性=**30s 周期同步（最终一致）**，不承诺任何时刻严格一致（表述已按用户修正：勿写"严格一致"）

用户附加的实现级约束（写进对应任务）：
- badge 30s 重读基线必须叠加当前会话未归档增量（`最新持久基线 + 当前会话增量`），不得纯持久值覆盖（否则吃掉实时计数）
- 面板 2s 轮询单飞/链式（上一轮完成后再安排下一轮），防慢读乱序旧数据覆盖新数据；关闭后 cleanup 零开销必须测试钉死
- flush 归零语义数字样例：flush 开始 session=10、落盘 delta=10、落盘期间新增+3 → 成功后 session=3，下轮只落盘 3；失败不扣、增量保留重试（沿 Plan 4 T2 裁定）
- T1 测试断言集：落盘成功归零/期间新增保留/重复 flush 不重复扣/flush 单飞；T2：pending 回放+幂等+只处理最新+http/https 输出恒 https；T3：到期重探/新探测重置旧 timer/timer 不叠加/cleanup 后不重探；T4：2s 刷新/关闭停止/读失败保留旧数据/不乱序覆盖/badge 重读不吃 session
- §4 裁定：0.3.0 minor bump 成立；4 任务划分不再拆第五项；测试塞进既有测试文件不新增任务
- D 项（单候选探测）确认无代码——现状触发条件已是 mirror_urls.size>0，仅补面板文案

spec：`docs/superpowers/specs/2026-09-01-plan5-polish-design.md` 已提交推送（84938ab，自查零占位符）；badge mount 读 DNR 基线增补用户已点头。
下一步：用户过目 spec → writing-plans 写实施计划 → SDD 执行（同 Plan 4 模式）→ v0.3.0 tag（tag 必须指向已含 release.yml 的提交）。

## 2026-09-01 Plan 5 SDD 完成（main @ bced2b1 合并 CI 绿，待冒烟+tag v0.3.0）

计划 `docs/superpowers/plans/2026-09-01-plan5-polish.md`（已推 0ac9e8b）；账本 `.superpowers/sdd/2026-09-01-plan5-polish/progress.md`；分支 plan5-polish（BASE 0ac9e8b，已推 origin）。

- **T1-T4 全过审**（fix round 仅 T4 一轮）：
  - T1 79ec6f6 归零口径：flushStats 单飞（flushing+try/finally）+ delta 快照在 get 后 set 前、成功后 `session[k]-=delta[k]`（间隙新增保留/失败不扣/无增量不写空 payload）+ readBadgeBaseline（stats+DNR 归并 'dnr' 单键）/foldDnrCounts；brief 新用例#1 的 set mock 每次+3 与末断言 undefined 自相矛盾——裁定实现者改为仅首次 set +3（断言逐字保留）
  - T2 a8a51f7 pendingProbe 覆盖式单槽+replay 先清后探幂等+hooksRef.current.cdnUtil 回填（spread 保留 probe）+ extension main-entry 回填改 spread+replay 调用；selectMirrorUrl 改候选副本构造（scheme 恒 https）
  - T3 aaca40d 主动重探：REPROBE_DELAY_MS=30_000、TTL+30s 单飞 timer（新成功取消重排/fallback 不安排/回调验 cache 过期+lastInput）、destroy；ensureProbe 提为 hoisted 函数（对象字面量内 timer 回调 ReferenceError——必要适配）；lastInput 在 guards 前记录
  - T4 d4f8204+fix a0eea8c 面板 2s 链式轮询（cancelled+clearTimeout 双守卫）+ badge 30s 重读（readBadgeBaseline，不覆盖实时增量）+ D 文案 + 0.3.0 三处 + README 三段
- **brief 缺陷两例同型**：T2 的 http 测试因单候选直返短路先绿（实现者增补单 item 双候选 RED 测试证真）；T4 卸载零调用断言空洞（函数引用比较恒真）——fix 改数值快照（RED 自证 30 vs 12）
- **最终全分支审查 ✅ 可合并**（gates 实跑 core 115/userscript 3/三包 tsc/双构建全绿）；4 条 Minor 均为冻结#3 最终一致口径内设计固有：badge flush 后 30s 自愈前短暂低估、面板纯持久与 badge 持久+session 瞬时差 ≤30s、轮询与手动操作交错 ≤2s 自愈、destroy-in-flight 空转自清
- 合并 main bced2b1，CI 绿（run 33525353555）
- **待办**：用户把 ScriptCat 脚本更新为 0.3.0 构建（packages/userscript/dist/make-bilibili-great-together.user.js）并启用（扩展保持禁用）→ controller 冒烟 4 项（首页面板自动刷新/视频页探测日志与重探/badge 与面板同口径/扩展侧 developerPrivate 重载验首载补探+DNR 键名）→ 用户确认 → tag v0.3.0 @ a0eea8c 之后提交（已含 release.yml ✓）→ 删 SDD 工作区
## 2026-09-01 Plan 5 冒烟+发版完成 ✓（v0.3.0 已发布，main@bced2b1）

- **真机冒烟 4/4**：①面板轮询链路（拦截→registry→30s flush 归零口径→面板 2s 轮询拾取，81→83→84 实测；注意面板读落盘值，会话计数需过 flush 窗口，首验数字不动是设计使然）②主动重探真机证据=面板状态单候选 268ms→双候选 153/162ms（TTL+30s timer 用最新 lastInput）③扩展首载不漏：performance 时基法（loadEpoch=Date.now()-performance.now()）实测 probe 加载后 1223ms 启动/1301ms 完成——时基法排除了跨工具调用的时序歧义，此法可复用 ④DNR 键名沿用 v0.2.0 复验（ruleId→"1"）
- v0.3.0 tag @ bced2b1（含 release.yml ✓）→ Release workflow run 33527914511 ✅ → 资产 .user.js+extension.zip+自动 notes，jsDelivr 可用
- 用户日常：userscript 0.3.0 启用 / 扩展禁用；SDD 工作区保留（git-ignored）
- Plan 5 无遗留待办；下轮可议：badge 瞬时低估自愈加速、AveMujica 实测定稿 optimize-story 冲突表（spec §3.3 provisional）、上游 SukkaW 更新 cherry-pick

## 2026-09-02 用户拍板：三项后续方向暂缓（记录备查，勿主动开工）

1. badge 瞬时低估的自愈加速（目前 30s 重读兜底——冻结#3 最终一致口径内）
2. AveMujica 真机实测，把 optimize-story 的 provisional 冲突表定稿（spec §3.3 provisional 项）
3. 上游 SukkaW/Make-Bilibili-Great-Than-Ever-Before 有更新时 cherry-pick 同步

用户想先解决"release 慢"的体感问题（tag-only + 确认环节的手工感）。

### 2026-09-02 release 慢讨论（未拍板，等用户决定）

- 事实澄清：发版本身已 Actions 自动化——release.yml tag 触发，v0.3.0 Release workflow 仅 37s；慢的体感来自 tag 之前的手工链路（三处版本号同步/构建+冒烟/等 controller tag push/确认环节，以及 v0.2.0 tag 指错提交返工）
- 已向用户提出方案：**版本号驱动全自动发版**——CI 检测 main 上 version.ts 版本号变化且与最新 tag 不一致时自动打 tag + 走 release.yml；以后发版只需"改版本号+push"一次提交
- 设计边界提示：版本号改了但测试未过时怎么办——建议 tag 前置 CI 门禁
- **等用户决定是否做**；做了则按 brainstorming→writing-plans→SDD 流程走

## 2026-09-02 四项收尾全部完成 ✓（v0.3.1 已全自动发版，main@0505345）

1. **Issue #1 真机实测**（6ecf235）：optimize-story 两项冲突确认为真实冲突（详见下节），去 provisional，Issue 已关闭
2. **版本号驱动全自动发版**（ebfe07c）：`.github/workflows/version-release.yml`——push main 检测 version.ts 版本号 vs tag 不一致 → 全量门禁（lint+test+build）→ 三处一致性断言（version.ts=meta.json=manifest.json=产物 @version）→ softprops 自动建 tag+发 Release。**关键坑：GITHUB_TOKEN push tag 不会触发链式 workflow（防递归），故 workflow 自包含不依赖 release.yml**；release.yml 保留服务手工 tag。幂等闸：tag 已存在直接跳过。发版语义已拍板：**改版本号+push 即发版，无人工确认**
3. **AbortController 穿透**（0ce96e5，backlog#1）：ProbeFetch 加可选第三参 AbortSignal；destroy abort 在途请求，适配层收到 abort 以 {ok:false} 结算不 reject；destroyed 闸门保留兜底
4. **userscript 覆盖评估**（fd042ef，backlog#2）：三领域逻辑均在 core 已测；入口层补测 getModuleEnabledSync 三值语义+createGMKVStore（5 项）
5. **T7 双形态提示**（3a56188，backlog#3）：main-entry 最前置置 `__mbgt_extension_active__`；userscript hasExtensionMarker 检测后仅 warn，不自动停用
6. **v0.3.1 全自动发版首跑成功**（0505345 → Version Release 49s 全绿，Release 资产 .user.js+extension.zip，tag v0.3.1 本地远端一致）

backlog.md 已清零（#4 两条顺手优化评估后关闭：debug 为 noop 无输出、落盘 payload 可忽略）。

## 2026-09-02 续：backlog 清零 + README 安装链修复 + 0.3.1 真机冒烟 ✓（远端 999ef1c）

- **README 存量 bug 修复**（999ef1c）：安装段的 jsDelivr /gh 链接 404（dist 不入库，.gitignore 含 dist/+*.user.js）→ 改为 Releases 直链 `releases/download/v<版本>/...user.js`（已验证 200）
- **0.3.1 真机冒烟 4/4**：①ScriptCat 已更到 0.3.1（面板页脚 `MBGT v0.3.1` 实测）②即时模块全数派发 ③compat 结算正常（双扩展在场 generic 并集停 6 模块，日志已是「动态页改造（真机已确认，Issue #1）」新标注）④零 mbgt 错误；扩展禁用时无 T7 警告=单形态零干扰语义正确
- **ScriptCat 自动化更新打法**（CDP 导航缺用户手势拦截不了下载流）：起本地 http.server 供 .user.js（text）→ CDP new_page 触发 ScriptCat 拦截 → 安装页是 edge-extension:// 页 CDP 不可见（MCP 未开 --categoryExtensions）→ 走 computer-use a11y 读到「更新」按钮 AXPress 即可；更新成功后安装页自动关成 about:blank
- 临时标签页已全部清理，浏览器还原（扩展+智谱清言两页）；四扩展开关原状未动
- 下轮两项可选议题已于同日用户拍板「都启动」并完成：
  1. **badge 基线自愈加速**（a768857）：registry onFlush 落盘成功事件 + badge 订阅立即重读基线；低估窗口实测钉死（flush 后新拦截 105→112）；30s timer 保留兜底 DNR 跨上下文（冻结#3 口径不变）
  2. **上游同步机制**（b90d0b2）：`.github/workflows/upstream-watch.yml` 每日 02:00 UTC 检测 SukkaW master HEAD，前进即关旧开新 upstream-sync Issue（状态存 Issue 正文「记录 SHA：」行，标签自建，同 SHA 幂等空转）。基线 Issue #2 已建（记录 19ac3ae）；**实测确认上游自 2026-08-26 后无新提交、移植基线（08-30）已含全部最新修复**。教训：workflow 里 heredoc 结束符必须顶格（YAML block scalar 内不可用），多行内容用 echo 组写临时文件
- 运维经验：workflow 触发用显示名 `gh workflow run "Upstream Watch"`（文件名不带 yml 不行）

## 2026-09-02 Issue #1 真机实测完成 ✓（main@6ecf235，CI 绿，Issue 已关闭）

- **结论：optimize-story 两项冲突均为真实冲突**，provisional 已移除。BewlyCat 1.7.8 与 AveMujica 1.8.32 都在动态页（t.bilibili.com）给 `<html>` 加 `momentsPage bewly-design remove-top-bar ...` 类并隐藏原生组件；AveMujica 代码有 t.bilibili.com//opus 专属 momentsPage 分支
- 运行时路径：动态页上 specific 标记（watch-later 等）不出现 → pending-family 超时 → **generic 保守并集**，两扩展单独在场均实测 `[optimize-story] auto-disabled: generic`，行为正确
- 用户环境补充：AveMujica 1.8.32 已装（GitHub 解压版 D:\extensions\extension，非商店不走同步）；测试后四开关已还原（脚本猫/BewlyCat/AveMujica ON，mbgt 扩展 OFF）
- 修订：CONFLICT_TABLE 与 optimize-story.ts conflicts 标注改「真机已确认，Issue #1」，README/测试名同步；实测技巧：developerPrivate.getExtensionsInfo({includeDisabled:true}) 在 edge://extensions 页可直接读四开关状态

## 2026-09-02 P2 修复与收尾任务书 8/8 完成 ✓（main@1de6589，CI 绿）

按冻结任务书 v1.0 执行（不得扩范围），三个 commit 推送 CI 绿（run 33577835030）：

- **T1+T2 红→绿**：probe.ts `destroyed` 闸门（声明+ensureProbe/runProbe/destroy 恰 4 处；runProbe 闸门在 `probing=false` 之后、cache 写入之前）；两条 race 回归测试（在途 destroy 不落盘不重探不复活 / destroy 后 ensureProbe 拒绝复活）未修复前跑红留证（本地 `D:\ai coding\.zcode\workspace\default\p2-t2-red-evidence.txt`），修复后 120/120 绿
- **T3**：destroy 语义裁定落 plan5 设计文档 §7 + probe.ts 顶部注释——getBestHost 维持旧 cache、不引入 AbortController（fetchLike 自定义签名穿透需改两侧适配层）
- **T4**：optimize-story 两项 provisional 挂汇总 Issue [#1](https://github.com/3304711297/make-bilibili-great-together/issues/1)（checklist+验证步骤），README 冲突行已回填链接
- **T5**：根目录原无 LICENSE → 已按 SukkaW 上游（gh api 实取，MIT © 2024 Sukka）补全 + 尾部归属「基于 SukkaW 原项目修改，© 原作者 / 修改部分 © 3304711297」
- **T6**：Topics 6 个已生效（bilibili/userscript/mv3/anti-tracking/tampermonkey/chrome-extension）
- **T7 跳过归 T8**：extension 侧确认无任何 `window.__mbgt*` 全局标记 → 按任务书分支裁定不改 extension，下一轮单独立项
- **T8**：`docs/backlog.md` 待办池（AbortController 穿透 / userscript 纯函数覆盖评估 / T7 标记注入 / runProbe 闸门 debug 日志与 status 落盘截断两个顺手优化）
- push 仍需 `git -c http.proxy=http://127.0.0.1:3067 push`；gh api 查上游 LICENSE 时匿名 API 被限流，用已认证 gh api 解决

## 2026-09-02 用户拍板顺序执行四项：①Issue#1实测✅ → ②全自动发版（进行中）→ ③待办池 → ④发0.3.1

四项按序逐一执行；④发 0.3.1 定位为**全自动发版 workflow 的首次真机验证**（顺序闭环）。

### ② 版本号驱动全自动发版（bounded 路径，设计已呈现、等用户批准后实施）

三项裁定（AskUserQuestion 全按推荐项拍板）：
1. **tag 前置全量门禁**：发版 workflow 内重跑 lint+test+build，全绿才 tag
2. **自动一致性校验**：tag 前断言三处一致（version.ts = manifest.json = 构建产物 @version）
3. **push 即发版**：「改版本号 + push 到 main」= 发版指令，无人工确认环节（误发可删 tag+Release 补救）

已呈现的设计（待批准）：新增 `.github/workflows/version-release.yml`（**release.yml 一字不动**，继续做 tag 消费者），push main 触发六步：checkout(fetch-depth:0) → 从 version.ts 提取 MBGT_VERSION → 幂等闸（tag v$VER 已存在即跳过，无版本变化空转零副作用）→ 全量门禁 → 三处一致性断言 → 打 lightweight tag v$VER @ HEAD（HEAD 必含 release.yml，规避 v0.2.0 指错提交坑）push 触发 release.yml；加 concurrency 防双 tag；README 发版章节同步改「改版本号+push 即发版」。验证方式=本地模拟逻辑，真跑落在 ④。

现状要点：release.yml tag 触发（softprops 自动 notes + .user.js/extension.zip 资产）；ci.yml=lint+test+build on push main；版本单源 packages/core/src/version.ts MBGT_VERSION（另 manifest.json + 构建注入 @version）。

### ③ 待办池（docs/backlog.md，处理顺序在 ② 之后）

AbortController 穿透 fetchLike / userscript 纯函数覆盖评估（拦截点/CDN 选优/归零口径）/ T7 双形态提示（extension 标记注入+userscript 检测）/ runProbe 闸门 debug 日志、status 落盘截断。

## 2026-09-02 用户反馈「设置不同步」修复 ✓（v0.3.2 已发版+真机运行确认）

- **根因**：两层 UI 语义脱节——面板显示生效状态（compat 自动停用），ScriptCat 菜单只显示用户 override（off/非 off），结算后不刷新 → 菜单全 ☑ 而面板自动停用
- **修复**（e3c3807，0.3.2）：module-menu.ts 重写——moduleMenuLabel/nextMenuOverride 纯函数（9 测试红→绿，21/21）；compat 结算后 updateModuleMenuStates 重注册 deferred 菜单（GM.unregisterMenuCommand 已在 grants）；标签 ⛔=自动停用·点击强制开启、☑（强制开启·点击恢复自动）、☐/☑；点击语义与面板提示对齐
- **全自动发版第三跑**：push→47s→v0.3.2 Release（工作流已完全稳定）
- ScriptCat 已更 0.3.2（同 localhost 流程），用户开着的 B 站首页重载后 `MBGT v0.3.2` 面板实锤 + auto-disabled 6 条同帧出现（重注册路径必然执行）；**菜单 ⛔ 视觉确认留给用户**（工具栏 flyout 自动化点不开：AXPress 与 event 点击均无效/帧失效）
- **环境观察（未动，需用户知悉）**：BewlyBewly! AveMujica 现为关闭态且扩展卡片带「错误」按钮（我 Issue#1 实测还原时是启用；用户自己关的或 Edge 因错自动停用，待用户查看）；mbgt 扩展仍 0.3.0 禁用（扩展侧本地 dist 未更新，菜单修复仅 userscript 相关）

## 2026-09-02 用户日常形态切换：扩展形态为主（记忆更新，旧「userscript 启用/扩展禁用」作废）

- **用户新日常**：仅 BewlyCat + mbgt 扩展（0.3.2）启用，脚本猫/userscript 及其他扩展全禁——纯扩展形态使用
- 已做：extension dist 本地重建 0.3.2（dist 不入库，bump 后必须本地 `pnpm --filter @mbgt/extension build` 再 developerPrivate.reload）→ 重载 → B 站页验证：6 即时模块派发/compat 停 6 模块/无 T7 警告（单形态语义正确）/options 面板完整（v0.3.2、拦截统计 3324、CDN 探测 77ms 最优 mirror08h）
- **「错误」按钮澄清**：扩展卡片「错误」=logger.warn 的两条 `No unsafeWindow.__playinfo__`（非视频页预期路径，WARN 也被 Edge 记入错误数），非故障；排除法：developerPrivate.getExtensionInfo 的 runtimeErrors 看 severity
- 灰色扩展=整体禁用（Edge 站点权限弹窗中禁用扩展灰字点不开），options 需先启用扩展
- AveMujica 保持关闭态（用户自主），compat 现走 BewlyCat 单扩展场景

## 2026-09-02 扩展工具栏入口修复 ✓（v0.3.3，main@6320cfa）

- **用户追问「还是灰的/从哪打开设置」根因**：manifest 从未声明 `action`——无 action 的扩展在 Edge 站点权限弹窗显示灰字、无工具栏图标可点，options 只能走 edge://extensions 详细信息页
- **修复**：manifest 加 `action:{default_title}`（无 popup）+ background-entry `action.onClicked → runtime.openOptionsPage`；v0.3.3 三处 bump 全自动发版（45s）+ 本地 dist 重建 + developerPrivate.reload（0.3.3 ENABLED，后台 SW 正常）
- 教训：本地 dist 重建必须发生在版本 bump **之后**（此前一次顺序反了导致用户看到 0.3.1/0.3.2 旧产物）
- 用户验证项：点工具栏「扩展」拼图 → mbgt 图标 → 点击即开设置面板；建议「固定到工具栏」

## 2026-09-02 面板自动停用说明补全 ✓（v0.3.4，main@456ef0c，用户新常态已确认）

- 用户拍板常态=**仅 BewlyCat + mbgt 扩展（其余全禁）**；建议落地：面板自动停用条目由「自动停用：generic / 功能名」扩为完整说明——`describeAutoDisable` 纯函数（panel/model.ts，4 测试红→绿，全量 144/144）：generic=「识别到 BewlyCat/Ave Mujica 家族共存（探测窗口内无法细分具体是谁），按保守并集停用」、specific=识别到具体扩展；统一附「强制开启可能与对方界面冲突，不建议开启」
- options 页真机确认 0.3.4 新文案生效（扩展重载后 showOptions 重开）
- 面板「灰的没法改」澄清过：9 即时模块锁定=Plan 4 拍板的 document-start 平台约束（MV3 无法同步读设置），README 已载；6 deferred 可勾选=force-on

## 2026-09-02 前端 UI 现代化重构与接口收口 ✓（main@3e4e7cd，CI 绿）

- **UI 重构落地**：毛玻璃设计系统（CSS Tokens）、深浅自适应主题、iOS/Fluent 风格 Switch 滑动开关、2×2 拦截指标卡片、CDN 延迟微光标签、三 Tab 分页导航（模块/监控/备份），独立 options 页（居中卡片 680px）与浮层（380px 抽屉）布局解耦。
- **两项遗留闭环**：
  1. **`noReload` 接口与注释闭环**：`PanelApp` 增加 `noReload?: boolean` prop，options 页传入 `noReload: true` 自动隐藏页内刷新按钮，注释更新对齐。
  2. **面板轮询节流**：在 2s 轮询循环中加入 `if (!document.hidden)` 守卫，页面切入后台或隐藏时自动暂停轮询读盘，节约 CPU。
  - 轮询边界已知微特性：document.hidden 时维持 2s setTimeout 心跳，仅短路跳过 loadPanelData 存储读盘，前台切回即刻恢复；设计上保持极简，不额外挂载 visibilitychange 监听，符合轻量低侵入原则。
## 2026-09-02 待办池全面清理与指纹分层落地 + Edge Dev 真机实测闭环 ✓（main@d97e852，CI 绿）

- **代码架构清理与指纹严格三层分层（f496f15 & d97e852）**：
  1. `activeFeatures` 数据通路彻底清除：从 `ProbeResult` 接口和 `snapshot.ts` 中移除死数据通路与冗余扫描函数，消除“采集但未消费”的代码异味；
  2. 指纹库重构为严格三层分层并消除冗余分支（d97e852）：
     - **层级 1（独占专属特征）**：`BEWLYCAT_EXCLUSIVE_MARKERS`（`logo-cat`、`keleus/BewlyCat`、`keleus`） vs `AVEMUJICA_EXCLUSIVE_MARKERS`（`bewly-ave-mujica`、`VentusUta` 等）；
     - **层级 2（版本号主支启发式）**：`1.8.x` → `avemujica`，`1.7.x` / `1.6.x` → `bewlycat`（注：此为启发式，长期若上游大版本变更需依赖独占指纹）；
     - **层级 3（家族挂载点待定）**：已通过前置 `#bewly[data-version]` 确认宿主在场，未命中层级 1/2 时直接返回 `pending-family`，消除了恒真冗余查询。
  3. 单测全绿通过（122 core + 21 userscript 测试全绿），扩展 dist 生产产物重新构建完毕。
- **Edge Dev 浏览器真机实测验收（Live Verification via CDP）**：
  - 成功接管真实 Edge Dev 浏览器，在真实 Bilibili 首页（`https://www.bilibili.com/`）捕获控制台日志验证：
    - `[BewlyCat][首页加载] 插件开始加载`（BewlyCat 1.7.8 正常激活）；
    - 5 项重叠模块精准触发自动避让：
      - `[mbgt] [no-ad] auto-disabled: bewlycat (blockAds / 首页重构) detected`
      - `[mbgt] [optimize-homepage] auto-disabled: bewlycat (首页重构) detected`
      - `[mbgt] [optimize-story] auto-disabled: bewlycat (动态页改造（真机已确认，Issue #1）) detected`
      - `[mbgt] [player-video-fit] auto-disabled: bewlycat (bewlyWidescreen / 播放器样式) detected`
      - `[mbgt] [remove-useless-url-params] auto-disabled: bewlycat (cleanUrlArgument) detected`
    - `[mbgt] [use-system-fonts] "any" https://www.bilibili.com/` 正常运行；
    - 所有 9 个实时拦截防护模块（防跟踪、反 PCDN、防 WebRTC 泄露、存储防御等）全部正常注入生效。

## 2026-09-03 上游同步看门处置与自动执行拍板

- **Issue #8（上游 SukkaW 提交 19ac3ae 评估）**：逐条比对确认移植基线已完整包含全部 7 个提交涉及的功能改动与重构，无须 cherry-pick，已在 Issue 留言说明并正式关闭。
- **用户拍板铁律（自动执行）**：后续对于上游同步看门（`upstream-watch`）及常规评估类 GitHub Issue，完成比对评估并确认无须改动（或已完成必要移植/测试）后，**直接自动在 GitHub 上留言并关闭 Issue，无需每次额外询问确认**。
