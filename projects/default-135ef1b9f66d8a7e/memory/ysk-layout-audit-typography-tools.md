---
name: ysk-layout-audit-typography-tools
description: youshouldknow 站点排版治理：元数据单一渲染入口、渲染级布局审计工具链、中文排版修正的安全边界
metadata:
  node_type: memory
  type: project
---

# ysk 排版治理与审计工具链（2026-09-11）

ysk 全站排版体检与修复落地，提交 `f7b5d08`（主题重构）+ `e27de1c`（排版规范+工具链），CI 四项全绿，gh-pages 部署已确认指向 `e27de1c`。

## 一、顶部元数据三重冗余（核心问题）

同一批 Front Matter 字段被**三个渲染路径**重复消费，文章标题前堆叠 2~4 份近似信息：

1. `overrides/main.html` 的 `.doc-meta` 卡片（读 status/risk/applies_to/verified_on）
2. `hooks/badges.py` 的 `on_page_markdown` 注入 abstract admonition（读 applies_to/risk/tweak_module）
3. `hooks/badges.py` 的 `on_page_context` 注入 `context['tags']` → Material `partials/tags.html` 渲染成标签条

实测：15 页三重、113 页双重，顶部堆叠最高 517px、中位 330px。

**修复**：收敛为模板层唯一渲染入口。`badges.py` 只把规范化数据写入 `context['meta_card']`（含覆盖矩阵相对链接），`main.html` 渲染成单条紧凑横条，缺失字段自动省略。修复后中位 55px、最高 143px，H1 前块数统一为 1。

**约定**：新增元数据字段必须同时改 `badges.py` 与 `main.html` 两处，**不得另起渲染路径**。已写入 `docs/README.md` 元数据规范章节。

## 二、布局问题（CSS 层）

- 表格长参数串（`useplatformclock/useplatformtick/…`）撑破内容区：桌面唯一一处 931px > 736px 的横向滚动已消除。
- `overflow-wrap: anywhere` 是刻意选择——会计入 min-content，使不可断长串可折行。同时作用于表格 th/td 与正文 p/li/blockquote/admonition。
- 移动端 390px：表格需横向滚动从 70 处降至 58 处（余下为 Material 设计内行为）；长串溢出 7 处归零；H1-H8 硬缺陷三档视口全部为 0。

## 三、内容修复（两个真 bug）

- **围栏嵌套吞正文**：`EasyCLIProxyAPI本地网关架构与多智能体客户端适配.md` 用 3 反引号开 `markdown` 块内含 ` ```bash `，内层闭合符提前终止外层，导致「Parameters / When Executing」等正文被吞进代码块。改用 4 反引号外层围栏。
- **Steam 标题层级**：`Steam设置优化指南.md` 的「四/五/六」用与文章标题同级的 h1，全文 21 处层级修正（h1→h2、h2→h3、h3→h4）。

## 四、工具链（`tools/`，默认 dry-run，非 CI 门禁）

| 脚本 | 用途 |
| --- | --- |
| `audit_typography.py` | 6 类排版规则源码级审计（T1 盘古之白 / T2 半角标点 / T3 标题层级 / T4 围栏语言 / T5 连续空行 / T8 多余空格） |
| `audit_layout.py` | CDP 渲染级布局审计，任意视口；H1-H10 规则 |
| `fix_pangu.py` | 盘古之白批量修正，保护 URL/路径/版本号/单位 |
| `fix_fence_lang.py` | 围栏语言补全（状态栈处理嵌套） |

## 五、三条踩坑教训（务必记住）

1. **剥离 markdown 语法时用哨兵字符占位，不能用空格**。早期审计器报 1681 处"缺空格"，90% 是 `**粗体**` 标记噪声；报 758 处"多余空格"全是行内代码剥离后留下的伪空格。**报告数字前必须抽样人工核对**——本轮的 1681→175→0 和 758→0 都是这个迭代过程。
2. **围栏必须用 `(字符, 长度)` 状态栈解析**。`遇 ``` 就切换` 的朴素写法会被嵌套围栏骗到；审计器本身也踩过这个坑（把 4 反引号内的 ` ```bash ` 误报为缺语言的独立围栏）。
3. **盘古之白修正器要保护链接的 URL 段但修正锚文本**。`[电脑BIOS选项全科普EP09/…](url)` 这类系列命名在锚文本里，是可见正文，需要修正且要全组一致；只有 `](url)` 部分保持不动。

## 六、技能侧修正

`chinese-copywriting` 技能的 `pangu_format.py` 原本有**危险缺陷**：全局正则不做围栏保护，会把代码里的 `C:/Users/name` 加空格、把围栏语言 ```python 改成 ```Python 破坏语法高亮。已重写为 `split_fences()` 分段处理（front matter + 代码围栏原样保留），并把 `fix_casing` 默认关闭。该项目因此改用自研的 `fix_pangu.py` 而非技能脚本。

## 七、契约影响判断

**tweakbyjie 的 `knowledge.lock.json` 无需提升**。2026-09-05 策略调整后（见 tweakbyjie `tools/Coverage-Audit-README.md`）：日常 push/PR 审计直连 `youshouldknow/main` 不校验 lock；lock 校验仅在 **tag 发版**时执行。lock 当前为 `8d0f172`，落后于本次 `e27de1c` 不影响 CI。

[[desktop-projects-tweak-youshouldknow]] [[youshouldknow-doc-details]] [[youshouldknow-repo]]
