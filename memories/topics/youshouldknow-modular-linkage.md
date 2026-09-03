---
name: youshouldknow-modular-linkage
description: youshouldknow 知识库与 tweak 模块化结构联动的行号迁移
metadata:
  node_type: memory
  type: project
  originSessionId: sess_9523491b-83bd-433d-81a2-4d5fdb39af2b
---

历史上已将 40 处显式 `tweakbyjie.ps1:行号` 引用批量改为 `Modules/函数名` 定位，涉及项目导航下 5 篇文档，并在页首加入模块化同步提示；例如 `tweakbyjie.ps1:796` → `Modules/Menu.ps1（Part 1）+ Modules/Common.ps1/Set-RegDword`。但 2026-08-25 复审发现 `tweakbyjie全量执行参考.md` 与 `tweakbyjie-optimization-mapping.md` 仍残留大量模块化前的裸 `:NNN` 行号快照（如 `:62`、`:94-119`、`:813` 等），与“当前应使用 Modules/文件/函数名”的说明不一致；现有 Coverage 脚本只检查 `tweakbyjie.ps1:数字`，不会捕获裸行号。因此不能再记为“剩余真实行号引用为 0”，后续应清理或明确隔离这些历史快照，并同步修正映射页措辞。另有多个页首模块摘要未列出当前 Registry/Nvme/Virtualization/Defender/Mpo/Service/Power/Bcd 等模块。

**Why:** 行号随源码变化会漂移，模块化后旧行号全部失效，需改为稳定定位以维持知识层与执行层联动。
**How to apply:** 后续更新 youshouldknow 映射时使用 `Modules/函数名` 而非行号；新增映射前先查 Modules/ 清单并同步提示块。

[[desktop-projects-tweak-youshouldknow]] [[tweak-modularization-plan]] [[youshouldknow-doc-details]]
