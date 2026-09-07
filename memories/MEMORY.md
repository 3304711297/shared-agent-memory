Hermes 主力模型 gemini-3.8-flash，经 EasyCLIProxyAPI（网关 18080，provider=cpa-gui）桥接 Antigravity（双账号平级优先级 10 轮询+会话粘性 1h 保缓存）；auxiliary.* 辅助模型严格默认 auto 自动跟随主模型（严禁擅自改动）。
§
WorkBuddy=本地 codebuddy2openai 反代 http://127.0.0.1:8787/v1（Tauri v2 客户端：多账号/积分看板/托盘/Hermes 一键写入）；venv=C:\Users\VOS-User\.workbuddy\binaries\python\envs\default；运维细节检索 OpenViking。
§
Windows 运行环境：本地代理 Karing 混合口 127.0.0.1:3067；NO_PROXY=127.0.0.1,localhost,::1,copilot.tencent.com,.tencent.com,pypi.org,files.pythonhosted.org（github.com 有意不加：常态被墙，加了会在可直连时强制绕代理反失败；不挂节点 git push 用 env -u 清代理变量）；PyPI 下载 CDN=files.pythonhosted.org（.org，非 .com）；GitHub CLI 账号 3304711297；浏览器接管 Edge Dev + chrome-devtools MCP；superpowers 插件有 Windows 定制。
§
子代理路由：delegate_task 默认继承聊天模型；未告知=同聊天模型；严禁固定 delegation.provider/model（已撤回）；单任务定制走 kanban per-task override；改 config.yaml 用 python yaml。
§
Hermes 检索与抽取=Exa 独享（EXA_API_KEY 在 .env，web/search/extract backend 全=exa）；EasyCLIProxyAPI(18080) 的 gemini-web-search 仅是别名无实时搜索，不可作搜索源。
§
本机硬件：RTX 4070 Laptop (8GB)+24GB 内存；C 盘紧张，模型/运行时 NTFS Junction 至 D 盘（models→D:\HermesModels，runtimes→D:\HermesRuntimes）；OpenViking venv=.openviking\venv 按需自启、2 分钟闲置休眠；MCP 终态：Hermes 端仅 chrome-devtools（--autoConnect 纯连接防清扩展）与 deepwiki，lazy+60s 回收；agent_guard 治理 MCP 孤儿进程并联动停 OpenViking 释放显存。
§
记忆架构（09-07 拍板）：memory.provider=openviking 仅为叠加检索层，内置 MEMORY.md/USER.md（3000/2000 字符限额，随系统提示词全量注入）仍并行存在；低频细节用 viking_remember 存 OpenViking 检索召回，内置只留高频必带事实，双库 99% 顶格时优先做减法不是调限额。
§
配置改动流程：先列候选+官方默认+代价清单，等用户拍板再动手，严禁擅自改。
§
Git push 卡住排查：github.com 直连被墙需走 Karing；ALL_PROXY=127.0.0.1:3067 仅在 Karing 已开出站节点时才监听（Karing 进程自身另监听 127.0.0.1:1666），3067 未监听即无路由，先确认节点开启再 push。
§
用户工作方式：外部AI交叉审查产出任务书并严格分级（P0/P1/P2），限定修改范围严禁顺手重构；执行Local-First铁律（本地先跑完整CI等价验证链与Release构建，本地全绿推后严禁在主会话卡等CI拖慢节奏，直接继续后续会话）；补回归测试闭环。