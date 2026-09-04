Hermes 默认主力模型为 gemini-3.8-flash，底层通过 EasyCLIProxyAPI（官方核心 v7.2.149，位于 D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64，本地网关 18080，Hermes 提供商标识为 cpa-gui）原生桥接 Antigravity；ZCode-Antigravity 桥已彻底退役。图片解析辅助模型为 auxiliary.vision=cpa-gui+gemini-3.8-flash。
§
WorkBuddy 经本地 codebuddy2openai 反代（已迁移至桌面 C:\Users\VOS-User\Desktop\codebuddy2openai，fork=3304711297/codebuddy2openai，Release 桌面快捷方式 CodeBuddy2OpenAI.lnk）暴露 OpenAI 兼容端点 http://127.0.0.1:8787/v1。Tauri v2 客户端已对标 EasyCLIProxyAPI 重构闭环：支持全量 28 官方模型矩阵、纯净倍率（去除 credits）、自定义上下文上限、思考强度调节/关闭、多账号切换管理、内嵌积分看板与实时 Debug 日志（UTF-8 容错、无黑框后台静默）；右键托盘对标 GUI.for.Cores 风格（内核状态/启停/重启/退出并双向事件广播）；Hermes/ZCode 配置一键写入（兼容驼峰与下划线）。旧批处理与 vbs 已删。venv=C:\Users\VOS-User\.workbuddy\binaries\python\envs\default。
§
Windows 运行与工具环境：本地网络代理为 127.0.0.1:3067；GitHub CLI 账号为 3304711297；日常浏览器接管使用 Edge Dev + chrome-devtools MCP。
§
本地 4 大插件（context7, desktop-commander, serena, superpowers）包含 Windows 适配与静默参数定制，由 GitHub Actions upstream-watch 定时巡检，更新时严格保护配置文件，严禁全量覆盖。
§
ScriptCat 全脚本静默失效（Edge Dev 154）已修复闭环：根因=chrome.scripting 动态注册的 scriptcat-scripting 广播者丢失（getRegisteredContentScripts=[]），SW 早退守卫（REGISTER_DONE+scriptcat-inject 存在→return）永不补注册，握手断致全部脚本失效（弹窗仍显示 1/1）。修复=SW 内 registerContentScripts 补注册（persistAcrossSessions:true），重启 Edge 复核注册幸存、GitHub/HF/OpenRouter 汉化实测生效。复发时用 hermes/scripts/cdp_live.py（check-register/fix-register；Edge 154 HTTP 发现端点 404 须直连 WS+suppress_origin，SW 30s 休眠需开 options 页唤醒）。已向上游提 issue：scriptscat/scriptcat#1724（早退守卫不校验 scripting 侧 + Edge 154 isolated world chrome.extension=undefined 隐患）。