---
name: rest-graphql-debug
description: "调接口报错时必用。REST/GraphQL状态码认证与复现。Debug REST/GraphQL APIs: status codes, auth, schemas, repro."
version: 1.3.0
author: eren-karakus0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [api, rest, graphql, http, debugging, testing, curl, integration]
    category: software-development
    related_skills: [systematic-debugging, test-driven-development]
---

# API Testing & Debugging — Router

Drive REST/GraphQL diagnosis via `terminal` (curl) / `execute_code` (requests) / `web_extract` (vendor docs).
**Isolate the layer, then fix** — 按链路顺序走，不跳步。

## Routing table

| Need | Read |
|---|---|
| 5 分钟 quickstart（curl / GraphQL / requests） | `references/quickstart.md` |
| 分层排查 1→6（连通/超时/TLS/认证/格式/语义） | `references/layered-flow.md` |
| HTTP 状态码 playbook（401/403/404/409/422/429/5xx） | `references/status-playbook.md` |
| 分页/幂等/契约校验/correlation-id | `references/contracts-correlation.md` |
| 回归测试模板 + Token/日志安全 | `references/regression-security.md` |
| Hermes 工具模式 + 输出格式 | `references/tool-patterns-output.md` |

## Always-on rules

1. 先复现（curl/requests 最小复现），再定位层级，最后才修。
2. 200 OK 也验 body 语义；5xx 先怀疑服务端再查自身。
3. Token/密钥只进环境变量；日志只记脱敏后摘要。
