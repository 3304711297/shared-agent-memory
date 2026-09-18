---
name: jev-ultrafast-local-integration
description: browser-use/jev-ultrafast 本地接入评估：零改动跑通 Edge Dev 链路、接入要点与坑、未验证项
metadata:
  type: project
---

# jev-ultrafast 本地接入评估（2026-09-18）

## 一、项目定位
- **仓库**：`https://github.com/browser-use/jev-ultrafast`（MIT，browser-use 团队，2026-09-16 发布，2 提交、约 1,681 行 Python）
- **本质**：极简浏览器 Agent 骨架，不做视觉、不做自由生成——用 TypeSafe 的 **Jev 决策模型**（System One，只返回 typed 概率决策、不产文本，$0.042/MTok 输入、输出免费、70–500ms/次）从**封闭操作集**中选操作 + 选元素编号。
- **操作集**：`CLICK / TYPE_TEXT / SELECT / SCROLL_UP / SCROLL_DOWN / WAIT / DONE / BLOCKED`。仅 `TYPE_TEXT` 时才把手写文本的活交给第二把小 LLM（OpenAI 兼容端点）。
- **决策机制**：每轮把页面可见控件拍成编号元素表；**一次网络往返**同时问「操作是什么」+「各操作的目标是哪个元素」（TypeSafe speculative fan-out），只用与选中操作匹配的那个 target 头。模型输出**永不变成 selector/坐标/shell/可执行 JS**，执行前重新校验页面新鲜度与点击遮挡。
- **官方成绩**：Google Flights 苏黎世→伦敦 7.073s、约 $0.0039/次；三组对照中位：时间 9.450→7.092s（-25%）、浏览器协议调用 1092→101（-90.8%）。
- **第三方补充观察**：砍 90.8% 调用只换来 25% 时间，因 ~43% 是模型决策延迟、~26% 是页面加载（Amdahl 天花板）；成本 98.4% 在 Jev（每轮重发完整元素表，平均 5,327 输入 token × 17 次），小 LLM 仅 1.6%。另一家 rtrvr.ai 独立实测：加 Jev 快 31–43% 但贵 38–51%。

## 二、本机接入结论：**可行，且零代码改动**
本地克隆 `D:\ai coding\jev-ultrafast`；评估报告见该目录 `INTEGRATION-NOTES.md`。

| 项目 | 结果 |
|---|---|
| 依赖 | `uv sync` → 23 包，Python 3.12.14，browser-harness 0.1.13 |
| 单测 | `uv run pytest` → **31 passed**（离线，无付费调用） |
| 静态 | `ruff check .` 干净；`node --check` 通过 |
| 真实浏览器守卫 | `scripts/check_guards.py` → **21/21 PASS**，跑在本机正在运行的 Edge Dev 上 |
| 元素表产出 | 自建探针页 → 6 元素 + 3 个 target 头（TYPE_TEXT/CLICK/SELECT）全部正确 |
| 零配置发现 | 不设任何环境变量，harness 自动从 `DevToolsActivePort` 找到 9222 并连上 |
| 用户侧影响 | 执行期新建 1 个后台标签页、结束自动关闭；既有标签前后一致，扩展数 13→13 |

## 三、接入要点（三条硬结论）

1. **不要设 `BU_CDP_WS` / `BU_CDP_URL`**。代码分支：设了走 `CDPClient`（`open_timeout=10` 硬死线，网络抖动即 `handshake failed`）；不设走 `_PatientCDPClient`（`open_timeout=None` 无限等）+ 自动发现 + `/json/version` 404→ws 路径回退。实测：设了连续失败两次，不设连续成功三次。
2. **`http://127.0.0.1:9222/json/version` 返回 404 属正常**（Chromium 147+ 对默认 profile 关闭 HTTP 发现），**不能据此判定端口不通**；正确姿势是用 `DevToolsActivePort` 的第二行 ws 路径，或裸 `ws://127.0.0.1:9222/devtools/browser`。
3. **代理变量不阻挡** daemon→`127.0.0.1:9222` 的 ws 连接（带 `HTTP_PROXY`/`ALL_PROXY`=3067 原样跑通）；代理只影响 `curl`/`urllib` 的 `/json/*` HTTP 请求（受 `no_proxy` 控制）。

## 四、登录态与边界
- 它在**同一个 profile**（本机 Edge Dev 默认 profile）里用 `Target.createTarget` 新建后台标签页执行 → **天然共享 cookies/登录态**（此项为代码推导 + 同 profile 事实，**尚未在登录墙站点实跑**）。
- 每次连接会临时多出一个标签页（`setFocusEmulationEnabled` 让后台标签页保持渲染），结束 `Target.closeTarget` 关闭。
- README 自述 MVP 边界：不支持 shadow DOM、iframe、canvas、上传、弹窗新标签、嵌套滚动、任意键盘控件；DOM reader 不覆盖完整 accessible-name 规范。

## 五、未验证项 / 阻塞
- **模型决策循环本身（`choose()` / `field_text()`）未跑过**，需两个 key：
  - `TYPESAFE_API_KEY` —— TypeSafe 早期访问 waitlist（`console.typesafe.ai`）
  - `TEXT_MODEL_API_KEY` —— 任意 OpenAI 兼容端点（仓库默认 DeepSeek）
  - 注：`model.py` **硬编码** `https://api.typesafe.ai/v1/systemone`，Vercel AI Gateway 的 key 不能直接替换（需自建 shim）。
- 官方 Flights / Wikipedia 演示未复现（付费调用）。

## 六、① 方案（接文本模型到本机 8787）的最终结论：**不值得做**

用户问「接文本模型岂不是固定模型端点，对频繁换模型的人不可用」——方向正确：

- **决策那一半**（`model.py:119`）**硬编码** `https://api.typesafe.ai/v1/systemone`，只有 `TYPESAFE_MODEL`（模型名）可换；换端点必须改代码。TypeSafe 为单一厂商，无第二来源可路由。
- **写字那一半**（`model.py:164`）由 `TEXT_MODEL_BASE_URL` / `TEXT_MODEL` 驱动，可指向本机 8787；但硬要求端点支持 `response_format: json_object` 且只返回 `{"text": "..."}`。
- 该架构是「一个专用决策模型 + 一个文本补丁」的 demo，**不为多端点路由设计**。接 8787 只省 1.6% 的成本，破不了 TypeSafe 的 waitlist 门槛（98.4% 在决策侧）。
- 完全绕开 TypeSafe 需自写 shim 让通用 LLM 假装决策模型，会慢一个数量级且准确率下降，等于抹掉核心卖点 —— **用户已选择做 ② 而非 ①**。

## 七、可复用点
- 「编号元素表 + 一次决策」思路已落地为独立技能 **`bsk-compact-page-read`**（详见 [[bsk-compact-page-read-and-jev-followup]]）。
- `scripts/check_guards.py` 可作浏览器自动化的回归闸门（无模型调用、纯本地）。

## 八、顺带修正的旧结论
本机 `edge-dev-cdp-scraping` 技能原先记载「Edge Dev 默认 profile 的 CDP 端口起不来（已试四种方案全失败）」——**本次复查推翻**：`127.0.0.1:9222` 正常 LISTENING，ws 直连实测通过（`Edg/155`）。根因是 `Local State` 里 `devtools.remote_debugging.user-enabled = true`——在 `edge://inspect` 勾选过一次后，重开浏览器就会监听。
该技能已按 09-17 的废弃决定**实际删除**（此前执行遗漏），两块独有知识已迁移：X/Twitter 抓取通道表 → `browser-skill`；Edge 扩展被物理删除的高危坑 → 本已在 `cross-agent-collaboration/references/browser-boundary.md`。

**Why:** 用户要求评估 jev-ultrafast 接入本地浏览器链路的可行性；实测证明可行且零改动，同时推翻本机一项过时的环境结论，两者都需跨会话留存以免重复排查。

**How to apply:** 后续若要实跑该 Agent，按「不设 BU_CDP_WS + 两个 key（文本模型可指向 8787）」直接 `uv run --env-file .env python examples/run.py`；需要复用登录态时它天然共享 Edge Dev profile，但须先确认能接受临时多一个后台标签页。若再讨论接 jev 决策模型，先看本文第六节结论。查 Edge Dev 默认 profile CDP 时不要再沿用「端口起不来」的旧结论。
