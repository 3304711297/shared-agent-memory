---
name: agentic-video-distill-cpa-route
description: 视频分析在 video_analyze 失败时的 cpa 端点工具集路线（本地反代 Gemini 带工具自主取证）
metadata:
  type: reference
---

# agentic-video-distill 的 cpa 端点工具集路线（2026-09-16 落地）

## 背景：为什么需要这条路

分析一段屏录时，`video_analyze` 报「当前模型不支持视频输入，视频内容已被过滤」。**这不是工具坏了**：
`video_analyze` 把视频交给**主聊天模型链路**，而图片走的 `vision_analyze` 走 `auxiliary.vision`（provider=auto）。
所以「图片能看」不代表「视频能看」——两者是不同路由，不要据此误判。

## 三条路线与失效模式

| 优先级 | 路线 | 状态 |
|---|---|---|
| ① | `video_analyze` | 主模型不支持视频输入时不可用 |
| ② | **cpa 端点工具集路线**（首选 fallback） | 实测可用 |
| ③ | Google 官方直连（`distill.py`） | 已知多坑，可靠性低 |

**官方直连的坑（实测）**：
- 中文文件名必失败——multipart 头按 ascii 编码，报 `'ascii' codec can't encode characters in position 0-3`；
- 脚本内置候选模型名（`gemini-3.8/3.7/3.6-flash`）可能与 Key 上实际可用的 ID 全部失配（需现查 `client.models.list()`）；
- `gemini-3.1-pro-preview` 可能上传成功但返回空串；
- 经本地代理访问 `generativelanguage.googleapis.com` 间歇性 `SSL: UNEXPECTED_EOF_WHILE_READING`。

**低分辨率画面最大的风险是幻觉，不是看不清**：`gemini-3-flash-preview` 分析一段 1318x120 的界面横条时，
凭空编出 `GPT-4o` / `o1-preview` / `Llama 3.1 405B` / `0 / 2000` 等画面中**根本不存在**的 UI 元素——
它用常见 AI 聊天界面的先验把空白填满了。

## cpa 路线怎么跑

```bash
python "<SKILL_DIR>/scripts/agentic-video-cpa.py" "<视频路径>" -o "<输出.md>"
```

让本地反代端点（默认 `http://127.0.0.1:18080/v1`）的 `gemini-3.8-flash-high` **带工具集自主分析**：
模型自己决定抽哪一帧、放大哪块区域、要不要听音轨。该端点实测同时具备**视频输入**与**工具调用**两项能力。

## 三条设计要点（改脚本时勿删）

1. **收敛纪律必须有**：不设预算上限时，模型会无限次重复放大同一区域——实测 14 轮不收敛、上下文滚到 63 万 token 仍未给结论。
   解法三件套：`TOOL_BUDGET`（默认 8）+ 只回带最近 3 组工具结果 + 强制每轮写「已确认」笔记。第 5 轮左右即收口。
2. **防幻觉锚点必须写进 SYSTEM**：显式禁止用常见软件界面的先验去补全画面，并要求「小于 14px 的文字先放大再读」。
3. **交叉验证不可省**：即使模型声称「已放大核对」，低分辨率下不同轮次仍可能给出互相矛盾的具体读数。
   交付前用 `vision_analyze` 对**原始帧的裁剪区域**独立复核关键结论。

**Why**：手搓 ffmpeg 抽帧 + 拼图看似直接，但横条类录屏（高 120px）抽帧后文字只剩十几像素，
视觉模型两次读数会互相打脸，既烧轮次又得不出可信结论。把「看什么」的决定权交给带工具的模型，才是这类任务的正确解法。

**How to apply**：先试 `video_analyze`；报「视频内容已被过滤」或 401 时，直接走 cpa 路线，
不要退回手搓抽帧；交付关键读数前用原始帧裁剪做独立复核。
