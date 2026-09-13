---
name: publish-site
description: "发布站点时必用。GitHub/Cloudflare/Netlify多托管版本化部署。Versioned site deploys to GitHub/Cloudflare/Netlify Pages."
version: 1.1.0
author: Hermes Agent (Nous Research)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [publish, deploy, hosting, github-pages, cloudflare-pages, netlify, static-site, versioning, rollback, web-development]
    category: web-development
---

# Publish Site — Router

版本化站点发布：本地构建预览 → 版本号 → 按 provider 阶梯部署 → 回滚预案。

## Routing table

| Need | Read |
|---|---|
| 完整五步 procedure（build/version/deploy/rollback/secrets） | `references/procedure.md` |
| 坑 + 验证 | `references/pitfalls-verify.md` |

## Always-on rules

1. 无例外先本地 `build + preview` 通过，再部署。
2. 每次部署前先打版本（no exceptions），保留一键回滚命令。
