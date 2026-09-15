---
name: repo-health-audit
description: "体检多仓/全项目健康时必用。只读审计+并行子代理+独立复核。"
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, health-check, git, repos, security-scan, subagents]
    category: software-development
    related_skills: [dispatching-parallel-agents, verification-before-completion]
---

# Repo Health Audit

对一个目录下的**多个** git 仓库做全面体检。核心不是跑命令，而是**子代理自述必须独立复核**——误报率实测很高。

## 流程

1. **主会话做全局扫描**（不要外包）：逐仓 `git status/branch/log`、`git fetch` + ahead/behind、`gh run list`/`gh pr list`/`gh issue list`、Dependabot/secret-scanning 状态、许可证、仓库体积。这一步给出骨架，成本低。
2. **子代理并行做逐仓深挖**（一仓一代理，写聚焦任务书）。每个任务书必须含：只读约束 + 起止 `git status --porcelain` 留底要求 + 明确要求区分【已验证】/【未验证】+ 要求证据里带确切命令与退出码。
3. **主会话独立复核所有高危指控**（见下节）。
4. 汇总成表 + 按严重度排序的遗留项清单。

## 子代理自述必须独立复核

审计类子代理的"高危发现"实测三类误报，**采信前必须自己跑一遍**：

| 误报类型 | 表现 | 复核方法 |
|---|---|---|
| **正则过匹配** | 报"密钥明文入库"，实为文档占位符或随机子串 | 取子代理给的确切 文件:行 定位，打印**掩码后**上下文；看字符长度与上下文语义 |
| **密文/编码内子串** | base64/密文块里的随机片段被当成 token | 看命中是否落在超长（≥200 字符）无分隔串内；统计命中值的长度分布 |
| **模式定义误判** | 把检测器自身的正则定义、测试夹具、或匿名响应头当成真泄漏 | 看该行的完整语义（是 `re.compile(...)` 还是真赋值） |

**报告"无泄漏"时同样要复核**：只报"扫描通过"而不出示命中值特征的结论不可信。

## 输出纪律

- **只报掩码**：`[md5=xxxxxxxx len=N]` 或 `<REDACTED>`。绝不打印完整密钥——包括在你自己的推理与报告里。
- **区分已验证/未验证**：子代理受阻项（API 限流、无浏览器会话、需写权限）如实标注，不要因为"大概没问题"就省略。
- 用 `curl` 免认证读 raw 端点可实测"公开分支是否真的公开"——比 `gh api` 的 visibility 字段更硬。
- 子代理可能**漏报**：正则会漏
  - 子代理的定位往往比主会话的第一版正则更准（它可能看过具体文件）。它报某文件含 token 而你的全库正则没命中时，**先用它的确切路径定向复核**，不要直接判它误报。

## 私有仓库的特殊性

私有仓**不是**免检区：归档型私有仓（会话转录、本地备份）最容易含真实密钥与机器路径，且一旦误设为 public 就是完整泄露。检查项：机器用户名/原始 profile 路径、API key、OAuth token、cookie、内网 IP、主机名。

## 常见坑

- `gh api .../dependabot/alerts` 需要 `admin:repo_hook` scope，普通 `repo` scope 不够——报错时换 `gh api graphql` 查仓库级 `hasVulnerabilityAlertsEnabled` + 已知告警数。
- `gh run list` 偶发 `EOF`（代理/限流抖动）：重试 3 次并 sleep，或改用 `gh api` 具体端点。
- 子代理报"无 CI"时，用 `gh api repos/OWNER/REPO/actions/workflows` 复核——本地没配 ≠ 远端没有。
- "CI 绿灯"只对该 revision 成立：比对 `gh run list --json headSha` 与本地 HEAD，确认是这个提交在跑。
- **"文档承诺 vs 实现"是最隐蔽的一类缺陷**：扫描时把每仓的 docstring/README 声明与代码实际行为对照（例：docstring 称"去 FTS 快照"但实现只有 `VACUUM INTO`）。这类不一致不会让任何 CI 变红。
