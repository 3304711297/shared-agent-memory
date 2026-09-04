Hermes 默认主力模型为 gemini-3.8-flash，底层通过 EasyCLIProxyAPI（官方核心 v7.2.149，位于 D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64，本地网关 18080）原生桥接 Antigravity；ZCode-Antigravity 桥已彻底退役。图片解析辅助模型为 auxiliary.vision=custom:local+gemini-3.7-flash。
§
WorkBuddy/CodeBuddy 通过本地 codebuddy2openai 桥接为 OpenAI 兼容端点（http://127.0.0.1:8787/v1），已配置模型别名 workbuddy / workbuddy-glm / workbuddy-kimi / workbuddy-deepseek / workbuddy-hy4。
§
Windows 运行与工具环境：本地网络代理为 127.0.0.1:3067；GitHub CLI 账号为 3304711297；日常浏览器接管使用 Edge Dev + chrome-devtools MCP。
§
本地 4 大插件（context7, desktop-commander, serena, superpowers）包含 Windows 适配与静默参数定制，由 GitHub Actions upstream-watch 定时巡检，更新时严格保护配置文件，严禁全量覆盖。