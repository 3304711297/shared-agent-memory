Hermes 默认主力模型为 gemini-3.8-flash，底层通过 EasyCLIProxyAPI（官方核心 v7.2.149，位于 D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64，本地网关 18080，Hermes 提供商标识为 cpa-gui）原生桥接 Antigravity；ZCode-Antigravity 桥已彻底退役。图片解析辅助模型为 auxiliary.vision=cpa-gui+gemini-3.8-flash。
§
WorkBuddy/CodeBuddy 通过本地 codebuddy2openai 桥接为 OpenAI 兼容端点（http://127.0.0.1:8787/v1），已配置模型别名 workbuddy / workbuddy-glm / workbuddy-kimi / workbuddy-deepseek / workbuddy-hy4。
§
Windows 运行与工具环境：本地网络代理为 127.0.0.1:3067；GitHub CLI 账号为 3304711297；日常浏览器接管使用 Edge Dev + chrome-devtools MCP。
§
本地 4 大插件（context7, desktop-commander, serena, superpowers）包含 Windows 适配与静默参数定制，由 GitHub Actions upstream-watch 定时巡检，更新时严格保护配置文件，严禁全量覆盖。
§
ScriptCat 全脚本静默失效（Edge Dev 154）已于 2026-09-04 修复并双端验证：根因=chrome.scripting 动态注册的 scriptcat-scripting 广播者丢失（getRegisteredContentScripts=[]），而 SW 的 registerUserscripts() 早退守卫（REGISTER_DONE+scriptcat-inject 存在→return）永不补注册，握手不广播致全部脚本失效（弹窗静态匹配仍显示 1/1）。修复=SW 内 registerContentScripts 补注册（persistAcrossSessions:true）。重启 Edge 后复核：注册幸存，GitHub/HP/OpenRouter 汉化全部实测生效（GitHub 标题「我的仓库」、HF「模型」）。复发时用 hermes/scripts/cdp_live.py（check-register/fix-register，Edge 154 HTTP 发现端点 404 须直连 WS+suppress_origin，SW 30s 休眠需开 options 页唤醒）。已知 Edge 154 isolated world 中 chrome.extension=undefined（上游 scripting.js 隐患，建议反馈 scriptscat/scriptcat）。