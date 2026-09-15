---
name: upstream-snapshot-drift-detection
description: "快照被人工改动后要显式可检测时必用。双哈希字段分离漂移与更新检测。"
---

# 上游快照漂移显式可检测

## 何时用

仓库 `sources/`(或同类 `vendor/`)是上游文件的 vendored 快照,但被**人工裁剪/改写**过。
若 state 里的哈希字段仍记着上游原文,则:

- state 不再描述被跟踪的文件(溯源记录失真)
- 漂移对同步机制**永久隐形**,任何 CI 都不报
- 上游下次真更新时整文件覆盖,**静默回填**被删内容,清理成果无声丢失

## 核心做法:双哈希字段语义分离

**不要**去改 state 里既有的 `hashes` 字段。它的语义是"上次拉取的上游内容哈希",用于更新检测;
改动它会让真实的更新检测失效。改成新增一个独立字段:

| 字段 | 语义 | 用途 | 谁写 |
|---|---|---|---|
| `hashes` | 上次拉取的上游内容哈希 | 更新检测(拉取内容 vs 此值) | 仅同步流程写 |
| `snapshotHashes` | 当前**本地**快照文件哈希 | 漂移检测(本地文件 vs 此值) | 同步时随 `hashes` 同写;人工裁剪后手工重录 |

两个字段**严格分离、互不读取**。校验函数只读 `snapshotHashes`,绝不碰 `hashes`。

## 校验放在拉取之前

```js
// main() 顶部,网络请求之前
const drift = verifySnapshotHashes(state);
if (!drift.ok) throw new SnapshotDriftError(drift.reason, drift.mismatches);
```

**顺序是关键**:若放在拉取之后,下游"检测到更新"分支会先用上游原文整文件覆盖快照,
人工改动当场被冲掉——校验形同虚设。必须**先拦下,再决定是否拉取**。

## 退出码:新增专用码,不挤既有语义

既有 `0=无事 / 10=已更新 / 20=仓库自身异常` 时,漂移给**新码 30**,而不是塞进 20:

- **语义不同**:20 是"从 git 恢复 state";30 是"先判断改动是否有意,再决定重录还是恢复"。
- **既有语义零改动**:`0/10/20` 的含义与所有既有分支完全不变。
- **workflow 守卫天然覆盖**:`if [ "$code" != "0" ] && [ "$code" != "10" ]` 已自动把 30 判为失败变红,
  无需改判定逻辑,只需更新注释。**先读 workflow 的退出码守卫再选码**,能省掉一次改动。

## 错误分类:用独立标记而非复用

```js
class SnapshotDriftError extends Error {
    constructor(message, mismatches) {
        super(message);
        this.name = 'SnapshotDriftError';
        this.drift = true;          // 专用标记,不与 unexpected 混用
        this.mismatches = mismatches;
    }
}
```

分派时 `e.drift` 判在 `e.unexpected` **之前**(若两者可能同时为真,先判更专用的)。

## 校验函数必须可注入依赖(否则测不了)

```js
function verifySnapshotHashes(state, conf = config, readUtf8 = (p) => readFileSync(join(projectRoot, p), 'utf8')) {
```

文件读取器与配置都可注入,测试才能用假文件系统覆盖"漂移/缺失/未记录"而不真实改仓库文件。
默认参数保持生产行为不变。

## 返回结构:区分三类不符

| kind | 含义 |
|---|---|
| `drift` | 有记录但实际值不同 |
| `unrecorded` | state 无该文件记录(含字段缺失/非法),文件存在 |
| `unreadable` | 文件缺失/不可读 |

**顺序陷阱**:先判断文件可读性再比对记录值。若先查记录,文件缺失会被误报成 `drift` 而非 `unreadable`。
`snapshotHashes` 字段整体缺失/为 `null`/字符串/数组时必须报 `unrecorded`——**删字段不能成为绕过校验的后门**。

## 同步分支要同步重录

上游更新覆写快照时,本地内容 === 上游内容,两个字段写同一个 `hashes` 对象:

```js
hashes,
snapshotHashes: hashes,
```

漏掉这步,更新完立刻自检就会报漂移,workflow 每 6 小时红一次。

## 测试要点(node:test)

必测:**漂移检出 / 无漂移不误报** / 缺字段不可绕过 / 文件缺失 / 文档化真实事故形态的用例。

必加一条**真实仓库态断言**(测试直接读真 `state` 与真配置文件,断言 `ok === true`):
它同时守护"重录后的值确实等于实际文件"和"将来谁改坏快照立刻红"。

**红绿双向验证**(证明测试真在测这件事,而非恒真):

```bash
# 篡改实现让校验恒返回 ok,新用例必须失败
sed -i 's/if (mismatches.length === 0) return { ok: true };/return { ok: true };/' scripts/check-upstream.mjs
node --test tests/*.test.mjs   # 期待:部分 fail
# 恢复后再跑,必须全绿
```

## 重录哈希必须用机器算

```bash
node -e "const c=require('fs'),h=require('crypto');for(const p of ['sources/a.js'])console.log(p,h.createHash('sha256').update(c.readFileSync(p)).digest('hex'))"
```

**不要手写哈希**。且注意:哈希必须对**工作区字节**算,不能对 `git show` 输出算——
`.gitattributes` 的 eol 规则可能让两者不一致。验证可移植性:在全新 `git clone` 里再算一次,
哈希相同才说明记下的值不是本机特有。

## 验证清单

- [ ] 正常态退出码与改动前**完全一致**(通常 0),且 state 无 churn(git status 干净)
- [ ] 篡改 1 字节 → 新退出码 + 报出"记录值 ≠ 实际值",随后 `git checkout --` 恢复
- [ ] **篡改内容在带漂移运行时未被覆盖**(存前后哈希对比)——这条才是本次修复的真实价值
- [ ] 构建产物 sha256 与仓库内被跟踪产物一致
- [ ] 全量测试通过
- [ ] `git ls-remote origin main` 与本地 `HEAD` 一致,并读回 remote raw 文件确认字段已落地
