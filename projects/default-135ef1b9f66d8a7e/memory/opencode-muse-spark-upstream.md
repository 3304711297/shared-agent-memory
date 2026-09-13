---
name: opencode-muse-spark-upstream
description: opencode-free 下 Muse Spark 上游档位钳制与区域不可用实录
metadata:
  type: reference
---

模型 `muse-spark-1.3-contributor-free` / provider `opencode-free`（`https://opencode.ai/zen/v1`，Responses API）：本地 `agent.reasoning_effort=ultra` 经 `META_AI_EFFORTS=(minimal, low, medium, high, xhigh)` 钳制后 wire 实发 `reasoning.effort=xhigh`；`summary` 在 `agent/transports/codex.py` 写死 `auto`（三档 auto / concise / detailed，只管摘要形态不管思考量）。上游 `/v1/models` 对该模型仅回 id / object / created / owned_by，无 context / thinking 参数；参数真源看 models.dev：context 1048576、output 约 943718~1048576、reasoning=true、tool_call=true。

2026-09-13 实测上游回 `403 RegionError: This model is not available in your country`，此前同链路多次 `APIConnectionError` 重试。排查入口：`%LOCALAPPDATA%/hermes/sessions/request_dump_*.json` 看 response_status / body，`logs/errors.log` 看重试链。

Why: 免费模型 403 先查区域限制而非档位；档位值只看 request_dump 实发，不看本地配置名。
How to apply: 免费档故障先读 dump 的回包体，再动档位；换链路优先于调档。
