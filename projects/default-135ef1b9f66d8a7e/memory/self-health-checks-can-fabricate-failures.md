---
name: self-health-checks-can-fabricate-failures
description: 自己的排查/验证动作会制造假失败与假产物——变异测试用 copy2 回滚留旧 mtime 骗过 make、误跑裸 build 覆盖正确产物、裸 python 命中错解释器；下结论前先排除自身污染
metadata:
  node_type: memory
  type: feedback
---

2026-09-16，workbuddy2api 收尾时连续收到三条「失败」回执，排查后**没有一条是代码问题**，全部是我的操作手法造成的：

1. **`cargo test` 报 44 passed / 2 failed**（看起来像真回归）。根因：做变异验证时用 `shutil.copy2` 把源码回滚，而 `copy2` **保留原 mtime** → 构建工具认为「产物比源码新、无需重编」→ 实际跑的是**变异版二进制**。`touch` 源码强制重编后立即 46 passed。判据：先查工作树是否与 HEAD 一致（`git status` / `git diff` 全空）+ 搜索变异标记是否残留，脚本里回滚一律用**会更新 mtime 的写法**（`shutil.copyfile` / 写完 `os.utime`），或干脆 `git checkout`。
2. **误跑裸 `cargo build --release` 覆盖了正确产物**。隔离目录里已有一个 `cargo tauri build` 产出的合格 exe，我为排查上一条顺手跑了一次裸 build，把它替换成了**无内嵌前端的半成品**（尺寸差约 68KB、内嵌资源名命中 0 次）。若当时按原计划把文件交付出去，装上的就是空壳。判据：产物**不能只看构建日志说成功**（裸 build 同样打印 `Built application at:` 且退出码 0），必须直查二进制里的标记物（内嵌资源的哈希文件名命中数）。
3. **`python -m pytest` 报 `No module named pytest`**。根因：裸 `python` 解析到的是 Agent 自身运行时，不是项目 venv。机器上三个 Python 里只有前两个装了依赖。判据：跑项目测试一律用项目 venv 的**显式路径**。

**Why:** 宿主 Agent 在排查时同时扮演「改动者」与「验证者」两个角色，自身的中间动作会改变被测对象的状态（mtime、产物文件、PATH 解析），产生看似客观、实则自指的失败信号。若把这类信号当外部事实，会朝错误方向排查甚至做出错误的回滚/重构。

**How to apply:** 遇到「与预期矛盾的失败」时，先把**自身污染**纳入假设：① 检查工作树是否与目标 commit 一致（`git status`/`git diff` 全空是最强证据）；② 检查是否有自己留下的中间产物/备份/变异残留（含被 `.gitignore` 遮住、`git status` 看不见的文件——用 `os.walk` 直接扫）；③ 检查命令解析到的是不是你期望的解释器/工具链；④ 产物类结论必须**直查产物本身**，不信构建日志与退出码。另外：**改动者不应兼任最终验证者**——至少换一种独立手段复核（本例改用「读构建产物内的实际声明」而非「读源码」）。相关：[[audit-count-is-not-impact-scope]]、[[test-assert-invariant-not-literal]]。
