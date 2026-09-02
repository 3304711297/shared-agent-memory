---
name: user-pref-chinese-commits
description: 用户要求 Git 提交信息尽量使用中文
metadata:
  node_type: memory
  type: feedback
  originSessionId: sess_510f94fa-355d-4031-bc67-00621ccf8b1c
---

用户在提交时明确要求“注意提交名尽量为中文”。已按中文提交信息执行多次：如“修复：补齐 NVMe 原生驱动缺失的检测函数并添加工程化配置”、“文档：新增 MkDocs 站点化配置与文档质量检查”等。

**Why:** 用户偏好中文提交信息，便于阅读与管理。
**How to apply:** 后续所有 git commit message 默认使用中文，格式如“修复：xxx”“完善：xxx”“文档：xxx”。

[[desktop-projects-tweak-youshouldknow]]
