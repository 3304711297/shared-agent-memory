---
name: bsk-compact-page-read-and-jev-followup
description: 把 jev 的 snapshot.js 元素表嫁接到 bsk 流程（新技能 bsk-compact-page-read）实测与体积数据；顺带更正 edge-dev-cdp-scraping 状态记录
metadata:
  type: project
---

# bsk 紧凑读页技能落地 + jev 后续（2026-09-18）

## 一、做了什么

把 `browser-use/jev-ultrafast` 的 `snapshot.js`（编号元素表机制）嫁接到 bsk 工作流，落地为新技能 **`bsk-compact-page-read`**（`skills/web/`，自研无上游）。

技能内容：`scripts/snapshot.js`（vendored，上游 commit 452c1ad）+ `scripts/selectors.js`（自研桥接）+ `scripts/table.py`（执行器，内置 `read_page()`/`render()` 可 import）。

## 二、实测体积（同为「喂给模型的文本」，字符数）

| 页面 | bsk observe | jev 紧凑表 | 比值 | observe 控件 | jev 元素 |
|---|---|---|---|---|---|
| GitHub 仓库首页 | 34,142 | 4,903 | **0.14x** | 127 | 79 |
| GitHub issues 列表 | 11,676 | 4,078 | **0.35x** | 80 | 66 |
| B站视频页（中文） | 8,391 | 1,650 | **0.20x** | 114 | 25 |

**规律**：页面「文本量 / 控件量」比值越高，省得越多；控件密集的表单页收益最小（那时两者体积接近，但 jev 表额外给出「每个元素支持哪些操作」）。

## 三、关键实现与踩坑（已写入技能正文）

1. **桥接靠 CSS selector，不是 ref。** jev 编号指向 `window.__jevFast.nodes` 的真实 DOM 节点；`bsk click` 接受 `@eN` **或 CSS selector**（`--selector`）→ 用 `selectors.js` 生成 selector 打通。
2. **selector 生成必须校验「身份」而非「唯一」** —— 这是本次最重要的坑：初版只断言 `querySelectorAll(sel).length === 1`，GitHub 页上 **25/81 指向了错误的元素**（结构路径唯一但命中兄弟节点）。修正为 `hits[0] === node` 后 81/81 全对。**属静默失败：点击会「成功」，但点在别的元素上。**
3. **`bsk evaluate` 传长 JS 必须走 argv 列表，不能走 shell。** git-bash 下 `"$(cat file.js)"` 会把含 `"` `\` 的 JS 改写，报 `SyntaxError: Invalid or unexpected token`；Python `subprocess.run([...])` 完全安全。
4. **不要用临时属性打标记做映射** —— 初版给节点加 `data-jev-probe` 再让 bsk 按属性点击，能 work 但污染页面 DOM；selector 方案无副作用。
5. **CJK 页面按字符计量**，`wc -c` 会按 3 字节/字虚高体积。
6. `bsk evaluate` **没有** `--expr-file` 参数，长脚本只能作位置参数传。
7. `snapshot.js` 幂等可反复注入（节点缓存在 `window.__jevFast`，导航重置）；`omitted_actions` 上限 250 个候选。

## 四、技能分工定位

- **执行 / 登录态 / 标签页借用 / 人工协助** → 仍走 `browser-skill`（bsk）；本技能只替换「读页面」这一步。
- **CDP 直连（绕过 bsk）** → `edge-dev-cdp-scraping`。
- **别用在本技能的场景**：shadow DOM / iframe / canvas / 虚拟列表为主战场的页面 —— 那正是 `snapshot.js` 的盲区，改回 `bsk observe`。

## 五、顺带更正的一条台账错误

`capability-inventory.json` 的 `notWatched` 里原记「edge-dev-cdp-scraping 已于 2026-09-17 彻底废弃淘汰并物理删除」——**与事实不符**：该技能文件始终在 `skills/web/` 下、被 git 跟踪，09-12 之后无删除提交（属决定与执行脱节）。且其核心前提「Edge Dev 默认 Profile 无法开启 9222 CDP 端口」已被 09-18 实测推翻。已在清单中更正为「实际仍存在且在用」，并注明最终去留待用户决定。

## 六、jev 决策模型（① 方案）的结论：不值得做

用户问「接文本模型岂不是固定模型端点，对频繁换模型的人不可用」——方向正确：

- **决策那一半**（`model.py:119`）**硬编码** `https://api.typesafe.ai/v1/systemone`，只有 `TYPESAFE_MODEL`（模型名）可换；换端点必须改代码。TypeSafe 为单一厂商，无第二来源可路由。
- **写字那一半**（`model.py:164`）由 `TEXT_MODEL_BASE_URL` / `TEXT_MODEL` 驱动，可指向本机 8787；但硬要求端点支持 `response_format: json_object` 且只返回 `{"text": "..."}`。
- 该架构是「一个专用决策模型 + 一个文本补丁」的 demo，**不为多端点路由设计**。接 8787 只省 1.6% 的成本，破不了 TypeSafe 的 waitlist 门槛（98.4% 在决策侧）。
- 若要完全绕开 TypeSafe 得自写 shim 让通用 LLM 假装决策模型（照抄概率分布 JSON），但会慢一个数量级且准确率下降，等于抹掉该项目的核心卖点 —— **用户已选做 ②（紧凑读页）而非 ①**。

**Why:** 用户选做「把 jev 的编号元素表思路嫁接到现有 bsk 流程」，本次完成实装与实测；同时发现并更正了一处台账与事实不符的记录，两者都需跨会话留存。

**How to apply:** 需要读页面且 `bsk observe` 输出过长时，直接用 `bsk-compact-page-read` 技能（`python table.py --session <id> --selectors`）。若日后讨论接 jev 决策模型，先看本文第六节的结论再决定是否值得。
