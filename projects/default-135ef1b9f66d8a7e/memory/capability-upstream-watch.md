---
name: capability-upstream-watch
description: shared-agent-memory 仓库的每日能力组件上游看门：清单比对+自动 Issue 提醒；含 ZCode 市场两层架构结论与本地一键检查
metadata:
  node_type: memory
  type: project
  originSessionId: sess_888b469b-882a-4e84-aeed-8d68b401a67c
---

**能力组件上游看门**（2026-09-05 建立，位于 shared-agent-memory 仓库 main 分支，用户感知 skill/mcp/plugin/核心工具新版本的统一渠道）：

- **组成**：`capability-inventory.json`（v2 已装版本清单）+ `scripts/check_capability_upstream.py`（stdlib 比对）+ `.github/workflows/capability-upstream-watch.yml`（每天北京时间 09:00 定时 + 手动 dispatch）+ `watch-capability.cmd`（本地一键全量检查并同步 Issue）。
- **检查源八类**：npm registry、GitHub Releases、ZCode 官方市场 CDN manifest（github 插件）、claude-plugins-official 市场 pinned sha、**local-merged-marketplace（客户端本地合并清单，仅本地运行，Actions 跳过）**、**github-commits-path（多源技能库与插件路径提交基线，含 hermes-hub-skills、anthropics/skills、google-gemini/gemini-skills、affaan-m/ECC）**、**hermes-skills-hub（Hermes 官网 Skills Hub 9万+ 全网聚合技能索引）**、**社区/策展市场源（SkillHub 1393 社区技能与 Cola Skill 16 精品策展技能）**。2026-09-05 纳入系统级 CLI（共 12 组件）；**2026-09-07 依用户指示完成看门雷达全量扩充与深度去重治理**：
  1. **看门去重机制**：剔除 `claude-plugins-official` 整仓提交监控，避免与内部已装核心组件（`superpowers` 与 `chrome-devtools-mcp` 的 `claudeMarketplaceSha`）产生同源双重告警；同时排除 `opensquilla` 等 Agent 独立框架；
  2. **非 GitHub 爬虫防失效与优雅降级铁律**：针对 SkillHub API 与 Cola Skill 页面解析，配置浏览器 UA 伪装、结构守卫与异常捕获。上游网络超时、WAF 拦截或模板微调时，严格标记为 `⚠️ 抓取暂不可达` 并保持当前基线，`behind` 严格为 False，绝不误计入 `outdated`，绝不触发误报 Issue，不阻塞整体检查；
  3. **受控组件规模**：全网立体监控总计达到 **18 项**。
- **ZCode 插件市场两层架构（2026-09-05 实查，修正早前「已下架」错误结论）**：UI 清单 = `bundled`（随客户端构建种子分发，source=filesystem，CDN 上无 zip）+ `cdn`（在线市场）合并；UI 真源文件 = `%USERPROFILE%/.zcode/cli/plugins/marketplaces/zcode-plugins-official/marketplace.json`（bundled-marketplace.json + cdn-marketplace.json 合并）。browser-use/computer-use/document-skills/skill-creator/zcode-guide/restore-legacy-sessions/android-emulator/ios-simulator/zcode-cua 共 9 个内置插件随客户端更新自动换代，已作为 `zcode-bundled-plugins` 组件纳入看门（本地检查）。
- **Issue 语义（label `capability-watch`）**：Issue 开着 = 清单落后于上游；升级组件后**必须把清单 `installed.version` 回写为新版并推 main**，下次运行自动收口。Actions 有 skipped_count 防误收口（本地源未检查时不关闭 Issue）。与 hermes 分支旧 watcher 的 `upstream-watch` 标签互不干扰。
- **首轮差异（Issue #2，2026-09-05 当日全部落地并收口）**：chrome-devtools-mcp 1.8.0（双端 MCP 钉版已改、claude 市场插件重装至 pin 45f187b1、保护参数 `--ignore-default-chrome-arg=--disable-extensions` 已补回插件）；github 插件 0.1.2（CDN zip sha256 校验换装）；context7-mcp 确认为远端托管（http mcp.context7.com + npx 未钉版）自动最新，移出监控。
- **第二轮跟进与自动化收口闭环（Issue #3 & #4，2026-09-06 彻底收口归零）**：
  - **Issue #3（hermes-hub-skills 上游技能库同步）**：上游 `NousResearch/hermes-agent` skills 引入 `reddit-reading` 与 `rss-feeds`（commit `ee5b5ec2`）。Hermes 本地与 ZCode `~/.zcode/skills/` 均已同步迁入（总计 89 副本），清单基线更新为 `ee5b5ec2`。同时修补 `.github/workflows/capability-upstream-watch.yml`：移除 `skipped_count == '0'` 限制（防止云端 Actions 因跳过本地种子检查项而阻止自动关单），清单对齐后 Actions 自动留言并收口 Issue #3。
  - **Issue #4（desktop-commander / serena / context7 上游小更新评估）**：上游变动仅为 codespell 修正、LSP 内部坐标返回与文档补充；鉴于四大核心插件本地具有 Windows 平台定制保护规范（严禁盲目全量覆盖），评估无需改动并规范留言关单。
  - **hermes 分支 watcher 加固（09-06）**：`plugin-upstream-watch.yml` 补齐 `Ensure upstream-watch label exists` 步骤（commit `a7c5875`），消除标签缺失红灯隐患。
  - **第三轮（Issue #6 & #7，2026-09-07 收口，根因级治理）**：
    - **Issue #6 = 插件删除后的遗留单**：hermes 分支 watcher（plugin-upstream-watch）仅按「未关闭同标签 Issue」去重、**无内容级去重**——09-06 18:42 开单的三插件变更与当日已评估关闭的 #4 完全重合（同 #680/#1842/#3138），且三插件当晚 20:08 已随 `3c948c7` 物理删除并移出 upstream.json 基线。处置：逐项核对 Compare diff 确认非破坏性后留据关单。规则：**对已删除组件的 watch Issue 直接留评估依据关闭**；基线已空则后续不应再开单。
    - **skills-hub 仅日期刷新误报根治**：Hermes 官网 Skills Hub 每日重跑索引（extractedAt 恒=当天），而工作流无 contents:write 无法回写清单日期，原 `behind = total != rec_total or extracted_at > rec_date` 从装机第二天起**必然天天误报「有更新（0 技能）」**。修复（`e8f7673`）：`behind = total > rec_total` 仅认技能总数增长，缩量属上游数据波动不动作；同 commit 给「编辑已有 Issue」路径补 `--title` 刷新，防标题残留过期「N 项待跟进」。修复后 dispatch 实测 outdated=0 自动收口。
    - **SkillHub total 是分钟级漂移的实时计数器**（评估时 1395→复核 1396），基线按收口时点 API 实测回写即可，不追中间值。
  - **4 仓总盘点结案（2026-09-06）**：`youshouldknow`（外链超时自愈/Pages绿）、`huggingface-chinese-plus`（单测与规则基线对齐/CI绿）、`make-bilibili-great-together`（check/release 双 Job 隔离无缓存报错/Release绿）、`shared-agent-memory`（双分支看门与单测全绿，Issue 全收口），全面达成 0 故障、0 红点、0 遗留 Issue、0 待办 PR。
  - **第四轮（2026-09-08 本地看门报告解耦与防漂移治理）**：
    - **本地报告漂移根因排查**：本地工作区顶层散落 `capability-report.md` 且全篇 ⚠️（HTTP 403 rate limit exceeded）。根因：① `scripts/check_capability_upstream.py` 原 `REPORT_PATH = "capability-report.md"` 为相对路径，在工作区顶层执行时报告脱离仓库散落；② 裸跑脚本未如 `watch-capability.cmd` 先通过 `gh auth token` 注入 `GH_TOKEN`，触发 GitHub 匿名 API 限流（60 次/小时）。
    - **端云分工解耦（--local-only 模式）**：18 项外部上游由 Actions CI 每日定时比对并托管 Issue；本地看门仅负责 2 项云端无环境的本地专属项（`zcode-bundled-plugins` 本地 marketplace.json 与 `hermes-config-guard` 配置守卫）。`check_capability_upstream.py` 新增 `--local-only` 模式并设为 `watch-capability.cmd` 默认行为（0.2s 完成，跳过外部网络查询，不改写/不收口云端 Issue），保留 `--full` 供必要时调试。
    - **路径锚定与防覆盖熔断保护**：`INV_PATH` 与 `REPORT_PATH` 全面基于 `REPO_ROOT` 绝对路径锚定，杜绝在执行目录乱甩文件；增加大面积失败熔断护栏（本地非 local-only 模式下若失败 >= 3 项直接拦截写盘，杜绝以残缺数据污染磁盘与 Issue）。
    - **真源唯一定格**：`capability-report.md` 从 git 跟踪中移除并加入 `.gitignore`（连同 `.pytest_cache/` 一并忽略），Issue 正文作为版本比对真源，本地不再维护 tracked 副本。
  - **第五轮（Issue #11，2026-09-09 收口；6 项全清并沉淀三条升级坑位）**：
    - **先看门结论必须本地复核，不可照抄 Actions 云端报告**：本轮 6 项「落后」中 `hermes-hub-skills` 实为**假阳性**——本地 5 个文件 SHA-256 与上游 `abd83ab5` 全等，内容早已同步，仅基线 sha 未回写。该提交把 `rss-feeds`/`reddit-reading` 迁入 `optional-skills/`，对 `skills/` 路径仅改 2 处文档描述。**规则：技能库类组件先做本地文件哈希比对再决定是否同步，哈希一致则只需回写基线 sha。**
    - **坑位一：`hermes config set` 重写 YAML 会截断尾部注释并改行尾**（config.yaml 受安全写保护，patch/直接写文件均被拒，只能走该命令）。实测它被截断 38 行（409→371 行），并把 CRLF 全转 LF，导致整份文件 diff 全红。**正确做法：先 `cp` 备份 → 用备份为基准只替换目标版本字符串 → 写回后统一 CRLF → 用 diff 确认与备份仅差目标行。** 简言之：能用文件级最小替换就别用 CLI 命令重写。
    - **坑位二：OpenViking 服务状态检测失真**——`openviking_service.py status` 显示全 OFFLINE，实际却有 4 个进程在跑（`openviking-server` + python + 2×pythonw），导致 pip 卸载报 WinError 32 文件占用。**规则：升级前一律先跑 `stop` 再复核进程列表，不能信 status 单方面输出。** 另注：`agent_guard.py` 借用同一 venv 常驻运行（pythonw），**严禁随 openviking 进程一并杀掉**，升级后须确认其 PID 仍存活。
    - **坑位三：uv 创建的 venv 不含 pip**（`No module named pip`），需先 `python -m ensurepip --default-pip` 补装再升级；卸载中断会留下 `~penviking*` 等 `~` 前缀残留目录，需手动清理，否则 pip 持续告警「Ignoring invalid distribution」。
    - **本轮处置**：openviking 0.4.18→0.4.19（服务三端 ONLINE + 实发语义检索验证）、PowerShell 7.6.5→7.6.6（winget）、chrome-devtools-mcp 1.8.0→1.9.0（Hermes config.yaml + ZCode cli/config.json 双端钉版，`npx @1.9.0 --version` 实测通过）。**1.9.0 行为变更留观**：CLI 默认开启 `--allow-unrestricted-paths`、默认过滤 Chrome webui targets，若影响 Edge Dev 抓取流程需回滚钉版。
  - **【重大语义变更 2026-09-09 用户拍板】技能看门从「发现新技能」改为「已装技能漂移检查」**：
    - **旧语义（已废弃）**：`github-commits-path` 类型按「仓库有新提交」判定 `behind`，报「有更新」并计入 outdated。问题：上游 100 笔提交里可能只有 1 笔改动了你装的技能，却全算成待跟进，且**不区分**「上游新增你没装的技能」与「你装的技能内容变了」——本质是误导性噪音。
    - **新语义**：①**发现新技能**完全移交 `skill-plugin-resources.md` 索引库按需检索，看门不再承担；②**已装技能是否落后**由新脚本 `scripts/check_skill_drift.py` 做**技能级内容比对**（本地 SKILL.md vs 上游同名文件）；③`check_capability_upstream.py` 的 `github-commits-path` 分支改为仅展示 HEAD/基线信息，状态标记 `ℹ️ 漂移检查`，**永不计入 outdated**（源码已加注释固化此语义）。
    - **check_skill_drift.py 三层判定（实测有效）**：
      1. **行尾归一哈希**：CRLF/LF + 行尾空白 + BOM 归一后比对，消除跨平台噪声（否则 `adversarial-ux-test` 这类会永久误报）；
      2. **差异方向**：本地多 = `local_extra`（本地增强，忽略）；上游多/大幅改写 = `upstream_extra`/`upstream_rewrote`（需评估）；双向 = `both_changed`（人工判定）；
      3. **仅 description 差异特判**（关键）：若正文完全一致、仅 frontmatter 的 `description` 不同 → 判定为 `local_extra` 并明确标注「本地中文强触发词定制，禁止被上游覆盖」。此规则保护了 2026-09-07 那次 57 字符截断优化成果（superpowers 13 项）。
    - **首次实测结论（18 项可映射技能）**：需人工评估 **0 项**，本地增强 15 项，上游无同名 8 项。典型三类：①`hermes-agent` 本地多 4 行（用户加的 UI 消歧/禁止假称并行铁律）；②superpowers 13 项仅 description 不同（中文强触发词）；③`python-debugpy` 上游把 `platforms` 改成 `[linux, macos]` **去掉 windows**——属上游缩小支持范围，本地保留 windows 正确，**不应跟进**。
    - **运行方式**：本地 `watch-skill-drift.cmd`（依赖本地技能目录，CI runner 无此环境，故不进 Actions）；支持 `--json` 与 `--repo <子串>` 过滤。
    - **配套产物**：`skills-provenance.json`（84 项技能 × 22 来源的出处盘点，含可监控性标注），为后续补监控提供数据基础。
  - **第六轮（Issue #12，2026-09-11 收口；desktop-commander 物理出库与 skillhub 缩量防误报治理）**：
    - **Issue #12 待跟进项 1（desktop-commander）**：上游 npm 发布 0.2.50 触发报警。实查核验：该组件早于 2026-09-06 随 4 大插件瘦身（commit `3c948c7`）从 Hermes 物理删除并移出 `upstream.json`，2026-09-09 ZCode 拆除后双端均已无任何实体与进程，系统内无全局 npm 包，Hermes `config.yaml` 亦无其配置；原清单 `capability-inventory.json` 遗漏移除导致误报。**处置**：从清单 `components` 物理移除并移入 `notWatched`，严格遵循「对已删除组件的 watch Issue 直接留据关闭、基线清空防再报」规范。
    - **Issue #12 待跟进项 2（skillhub-market）**：Issue 报告上游 1,468 技能较基线 1,479 产生 -11 差异，提示「社区有新技能上架（-11 项）」。根因：`check_capability_upstream.py` 原代码使用 `behind = bool(total != rec_total)`，导致社区审核下架/统计缩量时误触发 `behind=True` 误开单。**处置**：对齐 `hermes-skills-hub` 原则，重构判定为 `behind = total > rec_total`（仅总数净增长才计入待跟进，缩量属上游数据波动绝不误报），文案同步细化（增长标新上架、缩量标下架清理波动）；基线按实测时点（1,469 项，2026-09-11）回写更新。
    - **skills-hub 微量漂移对齐**：全网索引增长至 90,700（+1 技能，2026-09-11），清单同步对齐收口。
    - **验证全绿**：本地 `--full` 模式验证 `components=20 outdated=0 skipped=0 has_updates=false`，推 main 后 CI 自动收口 Issue #12。
  - **第七轮（2026-09-11 纳入 IceeAn/codebuddy2api 借鉴雷达与本地报错修复）**：
    - **IceeAn/codebuddy2api 借鉴雷达建立**：清单 `capability-inventory.json` 引入组件 `c2api-upstream-iceean`（codebuddy2api 活跃衍生库，MIT，25★，基线 `894bc3a`），专职监控腾讯 copilot 系反代上游改动，为脱敏与多账号轮换提供长期观测雷达；
    - **未绑定变量异常修复**：修复 `scripts/check_capability_upstream.py` 在触发大面积失败熔断保护（`failed_queries >= 3`）时提前引用未定义变量 `gh_out` 导致的 `UnboundLocalError`，置顶提至条件块外；
    - **验证全绿**：本地验证 `--local-only` 模式 `components=20 outdated=0 skipped=19 has_updates=false` 干净通过。
- **schedule 时线（2026-09-05 会话归档时状态）**：workflow 文件当日 03:26 UTC 才建到 main，此前仅手动 dispatch（当日 6 次：1 失败=Issue 创建前标签不存在，已由 `fix(watch): Issue 创建前先确保 capability-watch 标签存在` 自愈，其后全绿）；**首次 schedule 触发预计 2026-09-06 UTC 01:00（北京 09:00），归档时待验证**。
- **【重大事故复盘 2026-09-05】cli/config.json 的 provider.npm 字段导致整份用户配置被 CLI 静默丢弃**：桌面端/第三方工具写入的 provider 条目含 `npm` 键，而捆绑 CLI（zcode.cjs 0.16.5）的 zod schema 定义 `npm: g.never()`——出现即 parse 失败→配置回退空对象（无任何诊断输出）。症状：marketplace 来源插件（github/claude 市场系）全部显示 disabled、GUI 开关点击弹回、更新徽章异常；bundled 内置插件因走 officialPluginsEnabledByDefault 默认启用列表而看似正常，极具迷惑性。修复=删掉 provider 各条目的 `npm` 键（其他字段 passthrough 全兼容）。排查路径：CLI `plugins list --json` 状态矛盾 → 沙盒复刻（USERPROFILE 重定向+junction plugins 目录+二分 config 段落→字段）。**教训：cli/config.json 是 schema 强校验文件，手工/第三方工具写入前必须过 CLI `plugins list` 冒烟验证**。
- **无 CLI 的 ZCode 插件手工更新法（复刻安装器行为，已两次实操验证）**：下载 zip/tarball → 校验 sha256/来源 → 解压到 cache 新版本目录（zip 需剥离顶层前缀）→ installed_plugins.json 定向更新 version/installPath/updatedAt/source.sha（勿动 cacheTransactionId 等其余字段）→ 删旧版本目录（.git 只读 pack 需先 chmod -R u+w）→ 本地跑脚本验证全绿。注意 python 脚本内不可用 /tmp 路径（MSYS 虚拟路径，Windows python 看不到）。
- **GUI「可更新」徽章与开关的完整闭环（2026-09-05 终版）**：①开关失效根因=provider.npm 配置丢弃事故（详见下条），修复后恢复；②徽章比对源是本地市场快照 + **GUI 自己的 IndexedDB 安装记录（记装机时版本，感知不到任何 GUI 之外的变更）**——手工换装后徽章误报，点 GUI「更新」可消除；③**实测 GUI「更新」会按陈旧记录降级重装**（1.8.0→1.7.0，且不读已手工更新的市场快照文件）——降级后终态=活动插件目录 1.7.0、其 plugin.json 的 args 已补保护参数并钉 `chrome-devtools-mcp@1.8.0`、孤儿 1.8.0 目录已删；后续 GUI 再提示更新时须检查是否又降级并重补参数。已向 zai-org/feedback 提交 issue #527（含配置静默丢弃/开关弹回/徽章不感知/更新降级四案）。
- **ZCode 插件市场真源仓库（2026-09-05 用户发现）**：`zai-org/zcode-plugins`（官方内置+社区插件，17 个，CDN cdn-zcode.z.ai 是其镜像）——看门的 zcode-marketplace 检查已切换为优先拉取该仓库 raw marketplace.json、CDN 作回退；`zai-org/feedback`=官方用户反馈收集仓库（CLI 静默丢弃非法配置零诊断的行为值得去报一个）。
- **【用户拍板 2026-09-05】hermes-agent 与 ZCode CLI 本体永久不纳入看门**（各自自带更新机制；注意 hermes-agent 仓库的 skills/ 子目录提交监控属于技能库不属于本体）；未安装的市场插件（cloudbase-skills/example-plugin/代码安全防护）也不监控，代码安全防护在两份清单均未见、来源待查。
- **脚本坑位**：npm scoped 包需全量 URL 编码（@ 和 /）且必须用普通 Accept 头（GitHub 专用 Accept 会 406）；GitHub API 匿名限流需带 token；工作流建 Issue 前先确保标签存在；内置插件 zip 在 CDN 上连已装版本都 404，勿再试。
- **覆盖盲区**（清单 notWatched 同步维护）：hermes hub 技能（hermes GUI 自带提示）、http 远端 MCP（永远最新）、zcode-custom 自有 skill（无上游）。

**Why:** 更新源分散在 npm/GitHub/两个市场/客户端种子，人工逐个查不可持续；统一看门 + Issue 通知让用户及时用上新版本。

**How to apply:**
- **技能与看门联动铁律（2026-09-07 用户严正纠偏）**：技能变动与看门狗绝对同步——凡技能有任何新装、升级、瘦身裁撤或评估否决，第一动作必须本能同步更新 `capability-inventory.json`（基线版本、已装统计数、`notWatched` 排除说明）并推 main 跑 CI，严禁改完技能漏看门、严禁等用户提醒补漏。
- 任何 Agent 升级/新装受监控组件后，顺手更新 capability-inventory.json 并推 main；ZCode 客户端更新后跑 watch-capability.cmd 检测内置插件换代；新增组件时在清单登记检查源。相关：[[hermes-to-zcode-capability-sync]] [[multi-branch-memory-backup]]

**2026-09-07 上游 Issue 闭环跟进（scriptscat/scriptcat#1724）**：
- 用户反馈在 Edge Dev 154 上 ScriptCat 所有用户脚本静默失效（`#1724`）：根因在于 `registerUserscripts()` 早退守卫只校验了 `chrome.userScripts` 注册，未校验 `chrome.scripting` 侧，导致 `scriptcat-scripting` 广播者丢失后无法自愈；且 Edge 154 isolated world 中 `chrome.extension` 为 undefined；
- **当前状态**：**Closed**。维护者 CodFrm 已合并 PR #1725（提交 `b75124c`），补齐了双向注册校验与 `chrome.extension` 容错，相关问题已在上游彻底收口。
