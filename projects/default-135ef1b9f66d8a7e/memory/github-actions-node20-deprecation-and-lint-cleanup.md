# GitHub Actions Node20 弃用警告治理与 eslint 注解清零（2026-09-08）

跨 9 个仓库治理 CI 注解的实战记录：GitHub Actions 的 Node.js 20 弃用警告、以及 eslint
`@typescript-eslint/no-explicit-any` 警告清零的完整方法。适用于维护多个 GitHub 仓库、
需要消除 CI 注解噪声的场景。

## 一、Node.js 20 弃用警告

### 现象

```
Node.js 20 is deprecated. The following actions target Node.js 20 but are being forced to run on Node.js 24
```

出现在 Annotations 区（warning 级，不阻断 CI），常挂在某个具体 job 名下（如 `hygiene`）。

### 根因

**与 workflow 里的 `node-version` 无关**。是 action 自身的 `action.yml` 声明了
`runs.using: node20`，GitHub 强制在 node24 上运行才弹注解。`composite` 类型的 action
没有 node 运行时，**永不产生此警告**（如 `lycheeverse/lychee-action`、`dtolnay/rust-toolchain`）。

### 诊断三步法（SHA 钉版场景）

```bash
# 1. pinned SHA → tag（annotated tag 要取 ^{} 剥离后的那行）
git ls-remote --tags https://github.com/<owner>/<action> | grep <sha-prefix>

# 2. 查该 tag 的运行时
gh api repos/<owner>/<action>/contents/action.yml?ref=<tag> --jq '.content' | base64 -d | grep using:

# 3. 对比 latest 确认升级目标
gh api repos/<owner>/<action>/releases/latest --jq '.tag_name'
```

### 已验证的升级映射（2026-09）

| action | 旧（node20） | 新（node24） | SHA |
|---|---|---|---|
| `softprops/action-gh-release` | v2.0.8 | v3.0.3 | `efb35369e0ad2afab669f228072c1b0d510eae64` |
| `pnpm/action-setup` | v4.0.0 | v6.1.0 | `ea17c68df8912ef543352723c149a84f56e3d413` |
| `actions/checkout` | v4.2.2 | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-python` | v5.4.0 | v7.0.0 | `5fda3b95a4ea91299a34e894583c3862153e4b97` |

配套注意：
- `pnpm/action-setup` v6 的 packageManager 自动探测契约不变（无需加 `version` 入参）
- `actions/setup-python` v7 移除了 `pip-install` 输入
- `actions/checkout` v7 会阻断 `pull_request_target` / `workflow_run` 中的 fork checkout（v4 无此限制，属破坏性变更）

## 二、关键陷阱：绿灯 ≠ 无注解

**成功（conclusion: success）的 run 仍可携带 warning 注解**。验证消除必须查 check-runs
的 `output.annotations_url`，不能只看 conclusion：

```bash
SHA=$(git rev-parse HEAD)
gh api "repos/<owner>/<repo>/commits/$SHA/check-runs" --jq '.check_runs[].output.annotations_url' \
  | while read url; do gh api "$url" --jq '.[] | "\(.annotation_level) | \(.message)"'; done | sort | uniq -c
```

另一陷阱：**GitHub 注解显示有上限（约 10 条）**。UI 上看到「1 warning」不代表只有 1 条，
本地实测可能是 60 条。清零目标要以本地 lint 全量输出为准。

## 三、eslint `@typescript-eslint/no-explicit-any` 清零套路

按文件集拆分为互不重叠的分区，可并行处理。按出现频率，这些改法覆盖率最高：

1. **hook/mock stub** → 用被测模块的真实接口类型，取 `Partial<接口>` + 调用处 `as 接口`。
   例：`Partial<MakeBilibiliGreatTogetherHook>` 代替 `as any`。
2. **logger 测试桩** → 用 `MinimalConsole` / `Logger` 真实类型补全成员（常缺 `group*` 三个方法）。
3. **store mock 覆写** → `(store as { get: KVStore['get'] }).get = async <T,>(k: string) => ...`，
   比 `as any` 保留类型且无需双重断言。
4. **全局对象注入** → `Object.assign(globalThis, {...})` 代替一串 `(globalThis as any).x = ...`。
5. **真未知类型** → `unknown` + 使用处收窄，而非 `any`。

**严禁**用新增 `eslint-disable` 的方式清零——那只是压制，不是修复。

## 四、类型声明不完整导致的存量告警：改声明而非加断言

判断标准：**报错在调用方，但根因在 `.d.ts` 声明缺能力**。此时在调用处加断言会掩盖真相。

实例（userscript 包 2 条告警）：
- `GM_xmlhttpRequest(...): unknown` → 调用 `handle.abort()` 报 TS18046。
  正确修法：返回类型补成 `{ abort(): void }`，而非 `as { abort(): void }`。
- `registerMenuCommand` 返回 `string | number`，但 `unregisterMenuCommand(id: string)` 只收 string
  （声明自相矛盾）→ 逼出 `prev as number`。正确修法：参数改 `string | number` 与注册侧对齐。

判别时注意区分**存量 vs 本次引入**：用 `git stash` 跑一次基线 build 对比告警清单，
不要把既有问题算到自己头上，也不要漏报。

## 五、协作教训：子代理卡住要果断收回

glm 系模型在「寻找最真实类型」这类开放探索上容易陷入长调研（实测单任务 60+ 分钟未收敛）。
应对：
- 任务书里直接给出**统一套路**（如「mock 一律 `as unknown as 预期类型`，不必找最真实类型」），
  并明确「禁止探索无关细节」；
- 已派发后卡住：先 `steer` 下达收敛指令；仍不动就 `stop` 由主会话接手——
  这类逐行替换工作主会话做往往更快；
- 分区任务要确保**文件集互不重叠**，避免竞态写入；回收后核验 `git status` 确认无残留写入。

## 六、验证清单（宣称清零前）

- [ ] `pnpm -r lint` 全包 0 warning（不只 CI 显示的那几条）
- [ ] 各包 `tsc --noEmit` 干净
- [ ] 全量测试通过（测试文件改类型后必跑）
- [ ] build 产物 + CI 里的产物断言全通过
- [ ] 推送后查 check-runs `annotations_url` 确认**零注解**
- [ ] 确认未误触发发版流程（版本号驱动的 release workflow 应走 skip 路径）
