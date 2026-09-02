---
name: youshouldknow-doc-details
description: youshouldknow 薄页重定向、分类索引补齐、主文加厚与显式导航
metadata:
  node_type: memory
  type: project
  originSessionId: sess_9523491b-83bd-433d-81a2-4d5fdb39af2b
---

youshouldknow 已完成 MkDocs 站点化、薄页重定向与内容加厚三阶段：初期新增 mkdocs.yml（material 主题，中文搜索 lang:zh，11 条 redirects 将 5 行薄页指向主文）、requirements-docs.txt、.github/workflows/docs.yml（复制根目录与 13 个中文分类到 docs/ 再 mkdocs build --strict，lychee 死链检查）、.gitignore/.gitattributes，在 项目导航/tweakbyjie关联说明.md 等 5 篇文档中将 40 处 tweakbyjie.ps1:行号批量改为 Modules/函数名并增加模块化提示。

2026-08-20 内容完善批次：补齐 7 个缺失分类 README（系统知识/显卡优化/网络通信/验机相关/笔电相关/内存超频/软件技巧，提交 065f191，13 分类均有落地页）、加厚 4 篇核心薄页——网络通信/Windows网络栈优化原则.md 31→84行、内存与存储/Windows内存管理与性能.md 16→58行、存储与NVMe原理.md 41→60行、项目导航/游戏性能验证流程.md 24→56行（提交 87853ad）。工程收尾：mkdocs.yml 新增显式 nav（13 分类按教学顺序，历史兼容收纳为折叠组）、docs.yml 改为 pip install -r requirements-docs.txt、.gitignore 补 docs/（提交 647d055），本地 mkdocs build --strict 通过。

2026-08-20 用户确认可以发布，新增 gh-pages 自动部署（提交 dd0b8b4）：.github/workflows/docs.yml 新增 deploy 任务（if: push && refs/heads/main，需 build 成功，contents: write，mkdocs gh-deploy --force），push 到 main 时自动发布到 https://3304711297.github.io/youshouldknow/。后续提交 `442bcda` 修正 Coverage manifest 的源仓库路径字段与指向 tweak 的失效 OPTIMIZATION-DETAILS 链接；该提交 docs CI success。gh-pages 站点仍可访问。

tweak 文档同步：docs/POWER-PLAN-SOURCE.md 新增 ultimate-performance.pow 可追溯性（kirby、16384 bytes、SHA256 2EADB1A9A297C985A79100B1F1DBE994A2639D53C2D6A701CA019E5012868C7B / SHA1 59015BD7662A085F0401531F768D3150838CA5AE、校验与 powercfg 复现），README.md 与 docs/reference/OPTIMIZATION-DETAILS.md 同步，修正行号漂移为函数定位，docs/design/CODE-REFACTOR-STATUS.md / MODULE-ROADMAP.md / DEVELOPMENT-NOTES.md 标记第一阶段完成。

**Why:** 薄页与导航空洞影响站点可用性；主文过薄导致关键主题不可读；显式 nav 才能使 navigation.tabs/sections 生效并可校验；自动部署使主分支更新即发布。
**How to apply:** 新增分类需同步创建 README.md 并在 mkdocs.yml nav 注册；加厚主文保持“定位/机制/验证/恢复/边界”结构；2026-08-21 起内容位于 docs/ 标准布局（prepare-docs 复制步骤已废除），本地直接 mkdocs build/serve；requirements-docs.txt 已锁定精确版本（mkdocs 1.6.1 / material 9.7.7 / redirects 1.2.3 / rev-date 1.5.4），navigation.footer/tracking 已开启；发布流程在 docs.yml deploy 任务中维护，pull_request 不触发部署。

## 事实核查全覆盖（2026-08-21）

全部内容页均具备「事实核查记录」小节（两批完成：第一批 6 篇联动文档 `7f7fcd8`，第二批 18 篇 `20886f0`/`e633ce7`/`d623736`/`35e71cf`），按证据等级标注 ✅ 属实 / ❌ 勘误 / ⚠️ 社区源待复核。docs/README「如何新增内容」已写入硬性要求：新文章必附事实核查记录，涉及 tweakbyjie 的声明须对照当前源码核对。核验结论：仅 4 处轻微勘误（模块清单、Part 1 归属、`:813` 行号残留、快照字段说明），其余声明与源码/官方文档一致；审核模式一文经 Microsoft Learn 在线核验。

## 部署门禁与链接检查（2026-08-21 收紧）

docs.yml 的 deploy 原先只 `needs: build`，link-check 失败仅自己变红、部署照常进行；已改为 `needs: [build, link-check]`（`4436a5e`）。收紧后首次运行即拦截 `iknow.lenovo.com.cn` 超时误报（20s×3 次全超时、Errors 0），按既有反爬排除模式加入 lychee.toml exclude（`12fffb0`）。lychee.toml 现行策略：`accept = 200..299/403/429`（反爬墙视为可达）、`timeout=20`、`max_retries=2`、整域 exclude 仅用于连接层直接失败的站点。

## 文档元数据机制（2026-08-24/25）

已落地提交 `5ae61ef`：新增 `tools/check_front_matter.py` 与 10 个单元测试，定义可渐进迁移的四字段 schema（`status`、`risk`、`applies_to`、`verified_on`）；新增 `overrides/main.html` 和 `docs/stylesheets/extra.css`，由 MkDocs Material 在页面顶部显示元数据卡；`mkdocs.yml` 启用 `meta`、主题覆盖和额外 CSS，`requirements-docs.txt` 锁定 `PyYAML==6.0.2`，docs CI 新增 `front-matter-check` 且 deploy needs 包含该门禁。首批仅 5 篇低风险文章加元数据，旧文章继续允许缺失。后续维护时不要把 `verified_on` 当 Git 最后修改日期，也不要根据关键词自动填写风险/稳定性。

本轮 DLSS/DDR5 内容提交 `9da3e7d` 已推送：DLSS 帧生成专题加入刷新率—多帧生成倍率经验矩阵；DLSS 模型专题加入 DLSSTweaks 部署、Ultra Performance 比例、HUD 验证与回滚边界；DDR5 速查加入 AMD OC 公式与 6200C26 示例。所有截图内容均按“用户/社区经验或示例”标注，不当作官方保证或通用推荐。

联动文档校准（2026-08-25，ysk `fd74044`/`8bc7ae2`）：电源计划指南菜单 `6→7` 修正并把"完全可逆"改为"可恢复活动电源计划快照"；映射页 10 处 `Modules/Menu.ps1`（Part N）改为实际业务模块（Registry/Bcd/Service/Power/Mpo），CPU/GPU/MEMORY 行裸 `:NNN` 旧行号清理，核验基线登记 tweak commit；CPU/GPU/启动配置三篇专题与关联说明的模块定位同步修正（关联说明模块计数改为 16 个点源文件）。注意映射/参考文档不能出现占位模块路径，否则 tweak 的 Coverage 审计会报"源码文件不存在"。

继续遵循：`mkdocs build --strict` 不是完整正文链接检查；本地相对链接结构此前通过，但 lychee 外链可能因 WAF/连接中断失败，不能把 403/连接失败直接等同 404。

[[desktop-projects-tweak-youshouldknow]] [[tweak-modularization-plan]] [[youshouldknow-modular-linkage]] [[pow-file-traceability]]
