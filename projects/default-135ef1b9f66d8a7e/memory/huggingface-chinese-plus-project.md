---
name: huggingface-chinese-plus-project
description: 桌面 huggingface-chinese 油猴脚本项目；GitHub 仓库
  3304711297/huggingface-chinese-plus；引擎原创 + izhadu 词库 GPL-3.0 自动同步
metadata:
  node_type: memory
  type: project
  originSessionId: sess_19bf06e3-9812-4e80-89fc-84a6aa45b9e5
---

桌面 `C:\Users\VOS-User\Desktop\huggingface-chinese\` 是 Hugging Face 中文化油猴脚本项目（2026-08-29 创建），发布仓库 **3304711297/huggingface-chinese-plus**（gh 账号 3304711297），初始提交 `faf7249`，产物 `huggingface-chinese-plus.user.js` v1.0.1。

- **许可证路线（用户未及时拍板、按推荐执行）**：词库采用 izhadu/GreasyFork 的 HuggingFace-Chinese/dict.json（GPL-3.0，1836 静态词条 + 131 正则），本项目整体 GPL-3.0；引擎**原创**（借鉴 izhadu 与 1cyberlangke1/huggingface-zh 的思路，未复制代码），与 [[openrouter-chinese-plus-project]] 的 cny-price 同样的"只借思路"纪律
- 结构：`i18n-core.mjs`（纯函数翻译核心，build 内联去 export，与单测同源）+ `engine.js`（TreeWalker + MutationObserver + requestIdleCallback 空闲批处理，代码块/编辑器/.markdown-body 安全区豁免）+ `sources/hf-dict.json`（vendored 快照）→ `build.mjs` 组装单文件；版本 `<ourBase>.<buildNumber>`（当前 1.2.x；ourBase=功能/引擎修复人工递增，buildNumber=词库自动同步，语义已写进 README）
- **@match 决策（外部 AI 建议后拍板）**：huggingface.co + *.huggingface.co + hf-mirror.com；**有意不匹配 hf.space**——那是用户自建 Gradio/Streamlit 应用界面，翻译会污染应用本身，README 已写明理由
- **同步容灾**：check-upstream 按**候选源整组**尝试（candidateSources 纯函数）：主仓库 raw → jsDelivr CDN（`cdn` 模板字段，~24h 缓存只作容灾）→ mirrors 仓库 raw；同 source 全部文件必须来自同一候选源，任一文件失败整组作废换下源（杜绝多文件"半 raw 半 CDN"混合快照，外部 AI 提醒后已落地）。真机实测兜底生效过一次（raw TLS 失败自动切 jsDelivr）
- 上游同步与 openrouter 项目同构：`upstream.config.json` 指 izhadu/GreasyFork main 的 `HuggingFace-Chinese/dict.json`，check-upstream.mjs SHA-256 比对，cron 每 6h，退出码 0/10/20 语义一致；state 初始 buildNumber=1
- 关键工程细节：`.gitattributes` 强制 `* text=auto eol=lf`（词库哈希字节级比对不能被 CRLF 破坏）；本地跑 check-upstream 必须带 `https_proxy=http://127.0.0.1:3067` 否则 DNS 解析失败（退出码仍是 0，但会把 state 写成 unavailable，需要手动恢复）
- 验证状态（2026-08-29）：本地 build + node --check + 26 项单测全绿；CI 与 upstream-sync（手动触发）均 success 且无空提交 churn；raw 安装链接已验证 200；**真机冒烟通过**（Edge CDP 隔离上下文注入产物实测 huggingface.co：初始翻译/placeholder/正则时间/模型卡与代码块安全区豁免/软导航增量翻译全过，无报错）。发现 HF 部分链接点击是整页刷新非 SvelteKit 软导航，临时注入脚本会随刷新消失属预期，ScriptCat 正式注入不受影响
- **补充词库机制**：`sources/hf-supplement.json` 收录真机漏翻词条（Apps/Dismiss/标题整串/正则"及其他 N 家"等），build.mjs 合并时键覆盖上游、正则追加，与上游快照分离不会被同步冲掉；只收实测漏翻词勿堆词。OUR_BASE 现为 1.1（v1.1.1，`cab3949`）
- 排查技巧：主 profile 里用户还装了 KISS-Translator（会翻译同一页面，无法从译文归因）；验证本脚本行为要用 CDP isolatedContext 开干净页 + evaluate_script 主世界注入产物，console 应出现 `[HF中文] vX 已加载` 日志
- 参考仓库对照结论：cyberlangke1 版（MIT）词库内嵌单文件、2026-07 后停更；izhadu 版（GPL-3.0）引擎+远程词库分离、2026-08 仍活跃——词库选了 izhadu

**Why:** 新项目与 openrouter-chinese-plus 同族，后续维护（上游失效换 fork、ourBase 递增、真机反馈修复）需沿用同一套契约。
**How to apply:** 改动后跑 `node build.mjs && node --check huggingface-chinese-plus.user.js && node --test tests/i18n-core.test.mjs tests/check-upstream.test.mjs`；交付物考虑 ScriptCat 兼容（本产物零 GM_ 依赖菜单项，均带 typeof 守卫）。

**Related:** [[openrouter-chinese-plus-project]] [[user-windows-environment]]
