---
name: openviking-project-onboarding-workflow
description: 新项目接入 OpenViking 知识库的标准流程与 Git Hook 自动化增量同步规范
metadata:
  type: feedback
---

# 新项目接入 OpenViking 知识库规范 (SOP)

为保证本地知识库的高质量与高效维护，凡有新项目（代码库、文档站或知识仓库）接入 OpenViking 时，统一按照本标准化流程执行。

## 四步标准流程

1. **精确目录与独立命名空间隔离（严禁整父目录挂载）**：
   - 严禁将包含多个项目或杂乱文件的父目录（如整个 `GitRepos`）直接丢入 OpenViking；
   - 必须针对具体项目核心源码或文档目录（如 `D:/.../<project>/docs` 或特定源码树）进行精确挂载；
   - 明确指定独立、纯净的命名空间：`--to viking://resources/<project>`；
   - 目的：彻底阻断 `.git/`、`node_modules/`、`target/`、`dist/` 等构建缓存与垃圾噪音污染向量空间。

2. **Git Hook 驱动自动增量同步（改动提交即同步）**：
   - 编写对应的轻量同步脚本 `%LOCALAPPDATA%/hermes/scripts/sync_<project>_openviking.py`（比对当前 commit SHA，若有变动则后台异步触发 `ov add-resource`）；
   - 在该项目仓库的 `.git/hooks/` 部署 `post-commit` 与 `post-merge` 钩子并赋予执行权限；
   - 效果：用户或 Agent 编写改动并执行 `git commit` 或 `git pull` 后，Git 瞬间在后台发送增量同步信号，无需手动上传，平时零后台轮询空转。

3. **检索探活实测（严禁盲目声称完成）**：
   - 挂载并触发同步后，必须实际调用 `viking_search` 并指定 `scope="viking://resources/<project>/"` 检索 1~2 个领域关键词，实证确认能够毫秒级召回 L0/L1 摘要与原文。

4. **灾备闭环（写后必推）**：
   - 挂载与变更后，同轮必须执行即时灾备：
     ```bash
     cd "D:/openviking-backup" && MSYS_NO_PATHCONV=1 cmd /c "sync.cmd"
     ```
   - 确保私有灾备仓与本地数据保持完全一致。

**Why:** 父目录一把梭会引入海量构建产物并烧干模型配额；而 Git Hook 触发比后台定时轮询更节能、比手动重新上传更可靠，能在零心智负担下实现“改动即生效”。

**How to apply:** 凡接到“把某项目接入 OpenViking”或创建新知识库任务时，严格按此四步闭环推进，完成后向用户汇报挂载路径、钩子状态与实测证据。
