# 下一会话交接：9router 深度评估（✅ 已完成归档 - 2026-09-19）

> **状态**：本评估任务已于 2026-09-19 会话全面完成裁决，结论为 **9router 不采用**。完整裁决报告与实测依据见同目录下的 `rtk-and-9router-evaluation.md`。本交接文件保留作为上下文归档历史。

把下面这段**整段复制**，作为新会话的第一条消息发出即可。

---

## 📋 可直接套用的话

```
请评估 decolua/9router（https://github.com/decolua/9router）是否适合我。

【上一会话已完成的部分 —— 直接读，不要重做】
专题记忆卡：shared-agent-memory 的
  projects/default-135ef1b9f66d8a7e/memory/rtk-and-9router-evaluation.md
（该文件已含 rtk 的完整实测结论、9router 的源码级勘查结果与本机实测口径）

已查明的事实：
- 9router = JS/Next.js 本地 LLM 网关（:20128），29255 stars / MIT / 2144 open issues
- 与本机 EasyCLIProxyAPI(18080) + WorkBuddy2API(8787) 生态位重合
- 三个 token saver 的真实成分：
  · RTK Token Saver = rtk 过滤器的 JS 移植，跑在请求层（不是调 rtk 二进制）
  · Headroom Token Saver = 外部 Python 包 headroom-ai（9router 只做进程管理），
    默认端口 8787 与本机 WorkBuddy2API 撞车
  · Caveman / Ponytail = 提示词注入，不是压缩
- 本机实测天花板：成熟请求 tool_result 占中位 47.1% / P90 90.7%，
  其中 79.1% 落在 headroom 的 filter 族内（terminal 38.6% + read_file 27.2% +
  search_files 7.2% + patch 6.2%）；无 filter 覆盖 20.9%

【本次要裁决的 5 个问题】
1. 是否用 9router 替换现有双反代（18080 + 8787）？
2. 能否只摘取 RTK Token Saver 这个纯 JS 模块，不换整个网关？
3. 是否单独用 headroom-ai（不经 9router）？它是独立 Python 包 + CLI，
   可直接 headroom proxy --port <非8787> 对任意上游生效
4. 端口冲突怎么解（headroom 默认 8787 vs WorkBuddy2API）
5. 与已实施的 tool_output.max_bytes: 8000（命令/输出层，省 36.6% terminal 输出）
   是否重叠、能否叠加

【要求】
- 按 rtk 同样口径：先量化收益，再验实现（读源码 / 本地起实例抓包），最后才谈替换
- 不要重做已完成的事实核查；如需复核请以专门记忆卡为准
- 涉及改本机配置的，先列候选 + 官方默认 + 代价，等我拍板
```

---

## 🔧 交接时的环境前提（给自己看，不必复制给新会话）

| 项 | 状态 |
|---|---|
| `tool_output.max_bytes: 8000` | 已写入 config.yaml，**需重启桌面端才生效**（进程缓存），已登记 config-guard |
| PR #106399 守望 | 已由 GitHub Actions `pr-merge-watch.yml` 接管（与模型路由解耦），合并时自动开 issue |
| 死掉的 cron job | 已删除（`7284af...` 与探针 job；cron 通知链依赖模型路由，切模型即失效） |
| git 全局代理 | 已设 URL-scoped 键，新仓库自动继承；已登记 config-guard ④ 段 |
| 本会话归档 | 已归档，会话仍在增长 → 收尾时需补传 |
| 9router 相关端口 | 20128（9router 自身）/ 8787（headroom 默认，**与 WorkBuddy2API 冲突**）|

## 关键判据速查

- **rtk 不装**的核心理由：实测只能接管 terminal 的 10.3% = 全部工具输出的 3.1%；
  且 78% 的 terminal 调用是复合命令（rtk 明确跳过）。真正省下 36.6% 的是
  `tool_output.max_bytes`（命令/输出层），已实施。
- **9router 值得评估**的理由：它作用在**请求层**，天花板是 tool_result 占比
  （中位 47.1%），比 rtk 命令层高一个数量级——但要扣掉 filter 覆盖不足的 20.9%。
- **风险点**：2144 open issues；Next.js 全家桶（比本机现有双反代重）；headroom 端口撞车。
