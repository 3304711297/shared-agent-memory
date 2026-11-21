---
name: youshouldknow-bilibili-watch-ci
description: youshouldknow 的 B 站看门翻页缺陷与 link-check 抖动处置口径
metadata:
  type: project
---

# youshouldknow：B 站看门与 link-check 运维要点

仓库 `D:/ai coding/GitRepos/youshouldknow` ↔ `3304711297/youshouldknow`（MkDocs Material，main 直推，**无分支保护**）。改动前先读 `tools/README.md` 与 `.github/workflows/docs.yml`。

## B 站看门 `tools/watch_bilibili.py`

- 两种模式：`seasons`（合集，按 `season_ids`）与 `uploads`（搜索接口，仅能取到最近约 38 条，历史需 `baseline_bvids` 兜底）。
- **合集归档接口 `seasons_archives_list` 按「加入合集顺序」升序返回，最新视频在最后一页**，必须按 `page.total` 翻页。曾固定 `page_num=1&page_size=30`：合集涨到 42 条后，S3EP01–S3EP10 + S4EP01/S4EP02 共 12 条**静默漏报数周**，每轮打印 `Newly tracked videos: 0` 并 exit 0。
- 修复口径：翻页 + BVID 去重 + 翻页上限内未取全即 `RuntimeError`（宁可变红，不可静默截断）。
- 已跟踪集合 = `docs/` 中出现的 BVID ∪ 配置 `baseline_bvids` ∪ **所有 issue（open+closed）正文中的 BVID**。因此「补历史漏报而只开一张单」可直接生效：把全部 BV 号写进一张汇总 issue 即可（2026-11-21 用 issue #77 一次性补 12 条）。
- `space/wbi/arc/search`（wbi 签名）对 CI/本机仍返回 412，属风控硬墙，不要指望它；`search` 接口才是可用路径。
- 单测在 `tools/test_watch_bilibili.py`，CI 的 `front-matter-check` job 会跑 `python -m unittest discover tools`。

## link-check（lychee）

- 第三方站点 403/429/超时会让 link-check 变红并**连带跳过 deploy**（站点不更新）。合并 dependabot PR 前先确认失败项是否全是外部站点——与依赖升级无关时不要误判为 PR 问题。
- 处置顺序：① 单站点降并发 `[hosts."<domain>"] concurrency=1 / request_interval` → ② 仍持续失败才加入 `exclude` 并在 `tools/lychee-excluded-domains.md` 台账建档（含人工复核责任）。
- **不要用全局浏览器 UA 绕 WAF**：2026-11-21 实测会把 `space.bilibili.com`（412）、`resetera.com`（403）、`gitlab.gnome.org`（406）一起送进失败列表，净亏，已回退。
- 台账已有「本地误报」判据：同一 revision 下 CI 与本地 lychee 的 Total/Unique/Excluded 一致而 Errors 不同 → 属出口差异，别动配置；两边都报同样错误才建档排除。
- 排除行两种写法在 CI 上都生效（单反斜杠与双反斜杠都被接受），沿用文件既有风格即可；`tomllib` 是本地校验 TOML 可解析的最快手段。
