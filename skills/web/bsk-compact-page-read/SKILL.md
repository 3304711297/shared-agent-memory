---
name: bsk-compact-page-read
description: "observe 输出太长时必用。jev 元素表紧凑读页。"
---

# bsk 紧凑读页：jev 编号元素表

把页面压成「编号控件表 + 可见文本」，代替或先用它筛查 `bsk observe` 的长文本树。
实测体积 **0.14x–0.35x**（三个真实页面，同为喂给模型的文本）。

触发场景：`bsk observe` 输出很长（大列表/后台页）、token 吃紧、需要「这个元素支持哪些操作」的结构化信息、需要一次拿全控件做规划。

**别用在**：shadow DOM / iframe / canvas / 虚拟列表是主战场的页面 —— 那正是 `snapshot.js` 的盲区，改回 `bsk observe`。

## 用法

```bash
cd <skill_dir>/scripts

# 表 + CSS selector（selector 可直接喂 `bsk click --selector`）
python table.py --session <id> --selectors

# 最小体积（不要 selector / 不要正文）
python table.py --session <id> --no-text

# 机器可读
python table.py --session <id> --json --selectors
```

`table.py` 内置 `read_page()` / `render()`，可被别的脚本 import 复用。

## 实测数据（2026-09-18，Windows + Edge Dev 155）

| 页面 | bsk observe | jev 紧凑表 | 比值 | observe 控件 | jev 元素 |
|---|---|---|---|---|---|
| GitHub 仓库首页 | 34,142 | 4,903 | **0.14x** | 127 | 79 |
| GitHub issues 列表 | 11,676 | 4,078 | **0.35x** | 80 | 66 |
| B站视频页（中文） | 8,391 | 1,650 | **0.20x** | 114 | 25 |

规律：**页面「文本量 / 控件量」比值越高，省得越多**。纯文本长文章收益最大，控件密集的表单页收益最小（那时两者体积接近，但 jev 表仍多给你「每个元素支持什么操作」）。

## 关键实现细节（踩坑记录）

1. **编号 → bsk 执行的桥接是 CSS selector，不是 ref。** jev 的编号指向 `window.__jevFast.nodes` 里的真实 DOM 节点；`bsk click` 接受 `@eN` ref **或 CSS selector**（`--selector`）。用 `selectors.js` 生成 selector 即可打通。
2. **selector 生成必须校验「身份」，不能只查「唯一」。** 初版只断言 `querySelectorAll(sel).length === 1`，在 GitHub 页上 **25/81 指向了错误的元素**（结构路径唯一但命中了兄弟节点）。修正：`hits[0] === node` 才算通过。修正后 81/81 全对。**这是静默失败——点击会「成功」，但点在别的元素上。**
3. **`bsk evaluate` 传长 JS 用 argv 列表，不要走 shell。** 在 git-bash 里用 `"$(cat file.js)"` 传含 `"` `\` 的 JS 会被改写，报 `SyntaxError: Invalid or unexpected token`。Python 里用 `subprocess.run([...])` 传参则完全安全。
4. **`snapshot.js` 是幂等的、可反复注入。** 它把节点缓存在 `window.__jevFast`（WeakMap+Map）；重复注入只刷新，不重复建表。导航会重置缓存。
5. **不要用临时属性打标记做映射。** 初版给节点加 `data-jev-probe` 再让 bsk 按属性点击 —— 能 work 但污染了页面 DOM，且要额外清理。selector 方案是无副作用的。
6. **CJK 页面按字符计量，不要按字节。** `wc -c` 会把中文算成 3 字节，导致体积对比虚高。
7. **`bsk evaluate` 没有 `--expr-file` 参数**，长脚本只能作位置参数传（配合 argv 列表）。

## 与其他技能的分工

- **执行/登录态/标签页借用/人工协助** → 仍走 `browser-skill`（bsk），本技能只替换「读页面」这一步。
- **CDP 直连抓取（登录墙、绕过 bsk）** → `edge-dev-cdp-scraping`。
- **`snapshot.js` 上游**：`browser-use/jev-ultrafast`（MIT）。`scripts/snapshot.js` 是 vendored 副本（commit 452c1ad），上游改动时同步。
