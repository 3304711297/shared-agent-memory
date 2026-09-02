---
name: five-repo-task-book-v42
description: 五仓库优化任务书 v4.2（15 条冻结）已全部完成并推送，五仓 CI 全绿；含关键 commit、验收结论与后续可选事项
metadata:
  node_type: memory
  type: project
  originSessionId: sess_880325d2-450b-472c-9549-b16679f0626a
---

五仓库任务书 v4.2 全部 15 条 **已完成并推送，五仓 CI 全绿**（2026-09-01 收尾）。

关键 commit：
- steamdb `acd58c3`(P0-1/P0-2)、`5166237`(**词库死词条清理 orc 同口径**,1670→1640 词条,72,598→67,455B,v1.4.4,语义等价门禁 PASS)
- HF：`229f94d`（P0-1/3/4/5：开发者模式+regex-rules.test.mjs 基线哈希 7de29059…+OUR_BASE 1.3→v1.3.1）、`b6729ec`（P1-12 三页截图+P0-4 镜像站导出验证 domain=hf-mirror.com 实测通过）
- orc：`b3186b1`(P0-1)、`aa0bff2`(P1-6 瘦身 294,950→289,620B v1.3.2)、`8adc06e`(P1-8/9)、`cdab536`(P1-7 E2E，**CI e2e 任务真跑通过**，artifact e2e-screenshots 已产出)
- tweak：`c17ceaf`(P1-10/11)、`a97224a`(P2-14 README)、`ac25c73`+`556d5e5`(lock 两轮提升：0f00fc0 与 160e06a)、`a1ec89d`(BOM 修复)、**`e5b0b6a`+tag `v0.2.21` 已发版**(ZIP 版本注入 0.2.21 实测验证；Release notes 现为 GitHub 自动生成——审计定稿行为，用户确认保留)
- ysk：`0f00fc0`(P2-13/14/15)、`160e06a`(矩阵页菜单 0 边界说明)，Pages 均已部署并线上实测

人工验收：P0-1 脚本猫更新检测 **已通过**（用户截图：HF 1.2.1→1.3.1、orc 1.2.2→1.3.2 被脚本猫检测到；steamdb 未出现在列表属正确——本轮只改文档/测试未递增版本）。

**v0.2.21 已发版（2026-09-01，用户问"怎么弄"后我直接执行）**：流程=改 `$script:TweakVersion` '0.2.20'→'0.2.21'（commit `e5b0b6a`）→ `git tag v0.2.21` → `git push origin main v0.2.21` 一起推 → CI 五任务（lint/test/smoke-5.1/coverage-audit/release）全绿自动发版。已实测验证：Release 附件 ZIP(75,639B)+SHA256SUMS，下载解包确认包内版本注入 0.2.21，SHA256=cb310f3c…。注意：**Release notes 现为 GitHub 自动生成**（dependabot PR 列表+compare），这是 2026-08-25 审计"自动 notes+CHANGELOG 已删"的设计决定，与 v0.2.20 的用户手写格式不同；已向用户说明可改回模板（待其拍板）。**发版三步**：源码常量=本次 tag 版本 → tag 打在含最新 ci.yml 的提交 → main+tag 一起推。

**终态与待用户拍板事项**（任务书范围内无未完成）：①五仓终查全部 0 0 clean（唯一例外：orc 有一个本轮之前就存在的未跟踪 `.github/dependabot.yml`，非我创建、未提交，待用户定夺提交/删除）；②ScriptCat 里 HF/orc 两个待更新脚本带「轻微改动」标签——点更新会覆盖用户本地修改，已提醒先备份；③P1-6 280KB 为未达标目标值（282.8KiB 停手，剩余词条均无法证明为死代码）；④待办池：steamdb 词库按 orc 同口径清理、矩阵页边角说明、orc dependabot.yml 处置。

**Why:** 任务书冻结不扩范围；后续改动需遵守本批建立的契约（详见 How to apply）。
**How to apply:** 契约与踩坑：①新建 .ps1 必须 UTF-8 **带 BOM**（5.1 smoke 会按 ANSI 读，无 BOM 中文乱码解析失败——本次唯一 CI 失败即此因，a1ec89d 修复）；②mkdocs 1.6 的 on_page_markdown 收到的 markdown 已剥离 front matter，读 page.meta；Material tags 渲染=material/tags 插件+context['tags']（条目 {"name":...}）；③tweak 发版已是 tag-only，main 推送不烧版本号；lock 提锁顺序=先推 ysk→部署→提锁→审计→推 tweak；④orc 词库死词条判据与"语义等价校验门禁"可复用，上游同步会整文件覆盖快照（README 已注明）；⑤orc E2E 用 GM_* 垫片（故意缺 GM_xmlhttpRequest 验证汇率容错）；HF 截图脚本用 Playwright+msedge-dev+显式 proxy 3067。原待办池两条已于同日完成（steamdb 清理 5166237、矩阵页菜单 0 说明 160e06a+lock 556d5e5），待办池现为空。

[[steamdb-chinese-plus-project]] [[huggingface-chinese-plus-project]] [[openrouter-chinese-plus-project]] [[desktop-projects-tweak-youshouldknow]] [[user-windows-environment]]
