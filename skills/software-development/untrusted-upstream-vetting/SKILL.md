---
name: untrusted-upstream-vetting
description: "怀疑上游是投放物/发布物对不上源码时必用。只读核验仓库与二进制。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [supply-chain, malware-triage, pe-analysis, release-audit, upstream]
    category: software-development
    related_skills: [repo-health-audit, github]
---

# 上游投放物核验（Untrusted Upstream Vetting）

**目标：在采纳或运行一个陌生仓库之前，用只读手段判断「它是不是它自称的东西」。默认假设不是，证据够硬才反转。**

## When to Use

- 准备把一个陌生 GitHub 仓库纳入上游清单、采纳其调优项或装它的 release 时；
- README 描述与仓库内容/发布物对不上（声称 Rust 却是 Node 壳、声称可构建却无 app crate）；
- star 增长异常、单作者、release 说明是模板话术，需要判定是否投放物；
- 用户贴来一个「一键优化/修复」工具问「这是什么项目」时。

## 0. 只读铁律

- **绝不执行样本**，只解析字节；下载后先记 `sha256`，分析完立刻删除（含解包目录）。
- API 一律走 `gh api`：未鉴权 `curl api.github.com` 很快 429；本机 `raw.githubusercontent.com` 与 release 直链常被拦（`http 000`），但 `gh api … -H "Accept: application/vnd.github.raw"` 与 `gh release download` 可用。

## 1. 仓库能不能产出发布物（最快的一票否决）

```bash
gh api "repos/<owner>/<repo>/git/trees/main?recursive=1" --jq '[.tree[]|{t:.type,s:.size,p:.path}]'
```

判据：

- 声称 Rust/Tauri → 必须有 `src-tauri/`（或应用 crate）+ `tauri.conf.json` + `main.rs`。只有 `crates/<lib>` 的 workspace + 3~4 KB `Cargo.lock` = **只有库、没有应用**，README 的 `cargo tauri build` 必然跑不通。
- 声称 Electron → 看 `package.json` 的 electron 依赖与 `main` 字段；声称 Python → 看 `requirements`/`*.spec`。
- 发布物体积与所述运行时对账：Tauri 5~15 MB，Electron/PyInstaller/node-pkg 80~150 MB。差一个量级就是矛盾。

## 2. 前端是不是演示稿

```bash
gh api "repos/<o>/<r>/contents/app/ui/app.js" -H "Accept: application/vnd.github.raw" \
  | grep -cE 'invoke\(|__TAURI__|fetch\(|ipc'
```

- 0 命中，且存在 `sleep(`/`setTimeout` 把固定数值播成动画（如「118 → 231 FPS」）→ 这是给截图/GIF 用的 mock，后端根本不存在。

## 3. 时间线是否伪造

- 仓库 `created_at` 早于 → 对比最早 commit 的 author date：**commit 早于仓库创建 = 回填历史**。
- 首个 release 距仓库创建只有几分钟，却带着 4 个月的 CHANGELOG = 成套模板。
- 数日 300 star + 0 issue + 单作者只作弱信号，不能单独定罪。

## 4. 二进制身份（不运行）

```python
import struct
b = open(p, 'rb').read()
e = struct.unpack_from('<I', b, 0x3c)[0]
print(hex(struct.unpack_from('<H', b, e + 4)[0]))          # 0x8664 = x64
magic = struct.unpack_from('<H', b, e + 24)[0]
dd = e + 24 + (112 if magic == 0x20b else 96)
print('authenticode', struct.unpack_from('<II', b, dd + 32)[1])   # 0 = 无签名
```

- **版本资源的 `OriginalFilename` 才是真身份**（utf-16 搜 `OriginalFilename`）：`node.exe` / `python3xx.dll` / `gup.exe` 会直接暴露壳的类型。
- 打包器指纹：`pkg`（`package.json` 的 `"pkg": {"targets": ["node22-win-x64"]}` + 尾部 VFS JSON）、Electron（`node_modules`/`V8`/`asar`）、PyInstaller（`_MEIPASS`）、Tauri（`WebView2Loader`）。
- 提取 `pkg` VFS：尾部找 `{"C:\\snapshot` 后逐字符配平取 JSON；`{"0":[off,len]}` 是文件偏移/长度，`"1"` 为明文，`"0"`/`"2"` 带自定义压缩头；随即能列出全部内部文件（随机命名的 `*.bin` 分块 = 待重组载荷）。
- 全文搜产品名/游戏名：**0 命中**说明要么载荷被加密，要么这根本不是那个程序。

## 5. 发布资产一致性

- tag 与文件名版本号不一致、release note 是「Bug fixes and stability improvements」模板、同一 tag 换壳重传，都是矛盾。
- **改名复用合法签名二进制**是最硬的信号：解包后 `Main.exe` 的版本资源写着 `WinGup for Notepad++`，目录里还躺着 `gup.xml` + `libcurl.dll` → 拿官方签名更新器当下载器，绕过名称检测。

## 判定与落地

- 任一硬矛盾（构建不出发布物 / 二进制非所述语言 / 载荷不可读 / 签名二进制被改名）→ 结论「不可审计，禁止下载运行」，不留「也许没问题」的余地。
- 落地三件套（以 tweakbyjie 为例）：`tools/upstream-sources.json` 的 `blocked`（repo + reason + evidence）+ `check-upstream.py` 巡检跳过 + README「已拉黑来源」表；推 main 后验 CI 绿。
- 已核验案例：`Badgenyamultiplexer/pc-game-fps-doctor`（2026-11-08，详见 tweakbyjie README 黑名单表）。

## Pitfalls（常见陷阱）

- 未鉴权 `curl api.github.com` 很快 429；keyring 模式下 `gh auth token` 拿不到可用 token（返回 13 字符），别拿它拼 curl。
- `git/trees?recursive=1` 会返回陈旧快照（实测少 29 个条目，把有 `src` 的仓库看成空壳）：与 `contents/` 根目录对账后再下结论。
- `terminal` 会话的 cwd 是活的，删掉自己 `cd` 进去的 scratch 目录会让后续命令全部 `cd: No such file`——改用 `workdir=`。
- 压缩/加密载荷在没有对应解压器时不要硬猜算法；把「结构特征（分块大小、随机命名、头魔数）」记进证据即可下结论。
