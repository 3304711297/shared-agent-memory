# Arena AI (arena.ai) Browser Collaboration SOP (基于 BrowserSkill)

本规范定义了 Hermes Agent 如何通过 `browser-skill` (`bsk`) 接管用户已登录的 Edge 浏览器，与 **Arena AI (`https://arena.ai/`，原 LMSYS Chatbot Arena)** 页面进行跨 Agent 协同开发、单模型/双模型代码审查与对拍的完整标准化工作流。

---

## 一、定位与模式唯一铁律

- **平台唯一允许模式：Agent Mode（云端 Agent 副产线）**
  - **铁律（用户拍板 2026-09-22）**：**禁止使用 Arena 的其他任何模式（严禁 Direct Mode、Side by Side、Battle Mode）**！**只能使用 Agent Mode**。
  - **为什么禁用 Direct / 对话模式**：Arena 的 Direct/Side by Side 只是普通网页聊天，缺乏本地/联网上下文；而主流旗舰模型（如 Claude Sonnet 系列）在 Claude AI 官方平台不仅是同款，还能联网、深度挂载项目文件与具备完整工作流。若只需单模型对话或审查，应直接走 Claude AI 或本地子代理。
  - **Agent Mode 的核心独占价值**：原生支持 `Agent Mode`，可挂载 GitHub 仓库在非主分支独立探路与打样开发。具备完整 Workspace 沙箱、文件树与终端预览，自主通读全仓开发新功能原型与重型探路。
- **审查与对话协同分流**：
  - 代码复核/方案审查/长文档：路由至 **Claude AI (`https://claude.ai/`)** 或本地子代理；
  - 云端独立副产线/全仓沙箱开发：路由至 **Arena AI (`https://arena.ai/`) 的 Agent Mode**。

---

## 二、模式铁律与 Agent Mode 规范

### 1. 模式门禁（Mode Gatekeeper）

| 模式名称 | 状态 | 准入判定 |
| :--- | :---: | :--- |
| **Agent Mode** |  **唯一合法模式** | **必须使用**。Combobox 选 `Agent Mode`，挂载目标仓库/隔离分支，在独立沙箱与终端中自主运行。 |
| **Direct Mode** | ❌ **严格禁止** | **禁止使用**。普通单模型对话严禁使用 Arena，同款模型直接在 Claude AI 中使用。 |
| **Side by Side** | ❌ **严格禁止** | **禁止使用**。多模型盲测或并排对比不得在 Arena 中执行。 |
| **Battle Mode** | ❌ **严格禁止** | **禁止使用**。匿名竞技场抽卡不可控，禁止使用。 |

### 5. 本地子代理 + Arena 云端多产线并发编排（Fork-First 扩展）
遵循 **Fork-First 强约束门禁**：当遇到多模块并行任务、批量重构或大跨度技术探索时，主控 Hermes 不仅向本地分派 3~6 个 `delegate_task` 并行子代理（负责本地编译、单测、语法校验、多仓排查），**同时将独立的云端探索/重型模块生成分派给 Arena Agent Mode（挂载隔离分支自主开发）**。
- **发送即走，异步接力（2026-09-22 拍板）**：Arena Agent Mode 启动与云端环境初始化较慢（拉代码、装依赖、运行沙箱需要数分钟）。主控向其发送完任务并确认已处于运行态后，**严禁原地阻塞等待**！必须立即切回本地推进核心逻辑，并切至 **ChatGPT** 或 **Claude** 继续推进审查与对拍；
- **平台选择路由**：用户当前指令中指定了哪个就用哪个（提到 ChatGPT 用 ChatGPT，提到 Claude 用 Claude）；
- **三平台免费额度耗尽熔断（2026-09-22 拍板）**：Arena、ChatGPT、Claude 均有免费层额度限制。一旦检测到额度耗尽（报错、无法联网/分析文件、降级），立即无缝切至另一平台继续推进。
- **并行拓扑**：`[本地开发 / Subagent 并发]` 与 `[云端 Arena Agent / 外部 Reviewer 并发]` 同步推进；
- **效率倍增**：主会话免于单线程等待，多方产物就地聚合集成，最大化发挥全网算力吞吐。

---

## 三、模型选型策略与受限白名单

### 1. Text 与 Code 类别模型铁律限制（用户拍板受限名单）
在代码审查、架构方案对拍、Diff 审计与代码生成的 **Text 和 Code 类别**中，Hermes **严格受限且仅允许使用以下三款顶阶模型**（官方直选精确 ID 已核实验证）：
- 🟣 **`claude-sonnet-5-high`**（Anthropic 旗舰，代码审美、生命周期契约与协议规范审查最深）
- 🔴 **`grok-4.6-high`**（xAI 旗舰，长上下文逻辑推演与深度推理）
- 🟡 **`gemini-3.8-flash-high`**（Google 旗舰，1M 超大上下文窗口，响应极速且兼备极高代码分）

> **对拍组合规范 (Side by Side)**：必须从上述三款受限白名单中两两配对（例如 `claude-sonnet-5-high` + `grok-4.6-high`，或 `claude-sonnet-5-high` + `gemini-3.8-flash-high`），严禁超出白名单范围引入未经核准的其他模型。

### 2. 其他类别模型选型（基于 Arena Leaderboard 检索定案）
在非纯文本/代码的专项任务中，经 2026-09-18 实时检索榜单前列与开放直选池，确定以下首选模型：
- 🖼️ **Vision（视觉多模态 / UI 截图分析）**：
  - 首选：**`gemini-3.8-flash-high`**（原生全模态、1M 上下文）与 **`claude-sonnet-5-high`**。
- 📄 **Document（超长文档 / 论文 / 规范合规审计）**：
  - 首选：**`gemini-3.8-flash-high`**（1M 窗口极致长文本）与 **`gpt-5.5-high`**（Document 榜单商用前列）。
- 🔍 **Search（联网事实检索与外部证据 Grounding）**：
  - 首选：**`gemini-3.1-pro-grounding`**（原生 Google Search 检索增强探针）与 **`gpt-5.5-search`**。
- 🎨 **Image（文生图与图像编辑 Text-to-Image / Image Edit）**：
  - 首选：**`gpt-image-2.5-sunburst`**（榜单第 1 名，Elo 1520）与 **`grok-imagine-image-2.0`**。
- 🎬 **Video（文生视频与图生视频 Text/Image-to-Video）**：
  - 首选：**`gemini-omni-1.1-flash`**（榜单第 1 名，Elo 1515）与 **`wan3.0`**（Elo 1494）。

### 3. 榜首未发布模型（Battle 独占机制说明）
- **现象说明**：Arena 排行榜（Leaderboard）榜首常年位居未公开的超新代模型（如 `Claude Fable 5.1 (Max)`、`GPT 6 Astra (Max)`、`Claude Opus 5`、`GPT 5.6 Sol`、`Kimi K3`）；
- **机制真相**：这些属于实验室匿名盲测模型，**平台未开放直选入口**（直选池中不存在），仅在 `Battle Mode` 随机分配；
- **决策建议**：工程审查严禁依赖 Battle 盲抽（因为可能抽中 8B 小模型导致审查质量崩溃）；通过上述受限白名单即可确保 100% 确定性的顶尖输出。

### 4. 模型失效/下架自适应重选机制 (Dynamic Fallback SOP)
若上述受限白名单模型（`claude-sonnet-5-high`、`grok-4.6-high`、`gemini-3.8-flash-high`）后续因平台维护、限流、下架或命名变更而不可用时，Hermes 严禁盲目臆测或降级为弱模型，**必须执行以下自动化动态选型 SOP**：
1. **重新巡检 Leaderboard**：调用 `bsk` 自动导航至 `https://arena.ai/leaderboard/text` 与 `/code/webdev`；
2. **抓取最新前列梯队**：提取当前排行榜 Top 15 中排位最高、评测分最高的候选模型；
3. **开放直选池交叉对拍**：在 `Direct` 模式搜索浮层中输入候选名称，筛选出**当前实际开放直选、且排位最高**的替代模型（优先锁定 Anthropic / OpenAI / Google / 开源旗舰的 High / Max 级别）；
4. **即时向用户报备与规约沉淀**：明确告知用户「原某模型暂不可选，已自动通过排行榜重筛并切换为当前最高分的 XX 模型」，并将最新选型同步沉淀至本规范与共享记忆库（shared-agent-memory）。

### 5. 同厂牌高版本前瞻跃升机制 (Version-Forwarding Rule)
在 Arena AI 调度选型前，必须秉持**「动态看榜、向上跃升」**原则，严禁刻舟求剑停留在旧版本：
- **前置巡检**：配置模型前核查排行榜或直选池中是否存在当前白名单厂商的**同产品线更高版本（同系列最新代际）**：
  - **Anthropic Sonnet 系列**：若出现高于 `claude-sonnet-5-high` 的开放直选版本（如 `claude-sonnet-5.5`、`claude-sonnet-6`），**必须自动向上升级选用最新版本**；
  - **xAI Grok 系列**：若出现高于 `grok-4.6-high` 的开放直选版本（如 `grok-4.7`、`grok-5-high`），**必须自动向上升级选用最新版本**；
  - **Google Gemini 系列**：若出现高于 `gemini-3.8-flash-high` 的开放直选版本（如 `gemini-3.9-flash`、`gemini-4-flash`），**必须自动向上升级选用最新版本**。
- **跃升处理**：自动采用更高版本后，在会话中主动提示「已检测到厂商发布同产品线更高版本并自动升级」，并在同轮就地更新本白名单基线版本与共享记忆库基线。

---

## 四、核心执行协议 (SOP)

### 1. 守护进程与会话启动
MSYS/Git-Bash 环境下执行 `bsk` 必须携带 `env BSK_AUTO_START=0`：

- **守护进程启动避坑（2026-09-19 实测）**：若 `bsk status` 提示 daemon 未启动，Windows 下直接前台执行 `bsk daemon start` 会因管道未脱钩导致挂起 180s 直至超时（exit 124）。必须通过 `cmd /c start /b bsk daemon start` 或后台任务拉起。

```bash
# 启动会话并获取 session_id
env BSK_AUTO_START=0 bsk session start --json
```

若返回 `session_id: "<id>"`，后续所有操作均携带 `--session <id>`。

### 2. 页面导航与会话定位
- **新建或直达 Arena 会话**：
  ```bash
  env BSK_AUTO_START=0 bsk navigate "https://arena.ai/" --session <id>
  env BSK_AUTO_START=0 bsk observe --session <id>
  ```
- **接续已有历史会话**：若需要继续特定主题对话，可在侧边栏（`Today` / `Previous 7 days`）中查找对应的标题 ref（形如 `@e7 link "..."`），或直接导航至会话永久链接 `https://arena.ai/c/<uuid>`。

### 3. 模式与目标仓库精准配置（强制 Agent Mode）
1. **切换模式为 Agent Mode（铁律：严禁切至 Direct / Side by Side）**：
   在 `observe` 树中寻找模式下拉框（形如 `@e14 combobox "... [has-submenu]"`），点击后在弹出的选项列表中**必须且只能**点击 `Agent Mode`（形如 `@eXX button "Agent Mode"`）。
   - **拦截规则**：若误点或当前处于 `Direct` 或其他模式，必须立即切回 `Agent Mode`；
2. **挂载 GitHub 仓库与隔离分支**：
   - 在 Agent Mode 界面中输入/选择目标 GitHub 仓库与非主干开发分支（或独立探路工作区）；
   - 确认工作区沙箱与终端就绪。
3. **选择 Agent Mode 底座模型**：
   - 在支持的模型列表中选择受限白名单顶阶模型（首选 `claude-sonnet-5-high` 或同系列最新版本）。

### 4. 输入提要与提交对拍
1. **定位输入框**：
   在 `observe` 树中寻找 `textarea`，对应 `@eXX textbox "Ask anything…"` 或多轮中的 `placeholder="Ask followup…"`.
2. **填充高密度审查提要**：
   ```bash
   env BSK_AUTO_START=0 bsk fill @eXX --value "..." --session <id>
   ```
   **审查提要标准结构**：
   - 提交 SHA、变更文件列表与核心机制摘要；
   - 针对上一轮问题的具体修复落点与代码 diff；
   - 单元测试与契约回归覆盖场景；
   - 本地全量测试与远端 GitHub Actions CI 真实 Run 证据。
3. **回车提交**：
   ```bash
   env BSK_AUTO_START=0 bsk press Enter --ref @eXX --session <id>
   ```

### 5. 轮询等待与结果回读（单次 sleep 60s 节律铁律，2026-09-22 拍板）
- **Arena Agent Mode 进展缓慢与长程周期特征**：云端 Agent 模式在容器沙箱中执行文件分析、环境探测、执行 bash、跑测试套件与长推理，单次运行通常持续数分钟至十几分钟。**严禁使用 10s / 15s / 20s 等超短延时频繁轮询打断**（极度消耗 turn 且会导致大量冗余截断输出）；
- **标准轮询等待周期：每次固定等待 1 分钟（`sleep 60`）**：
  ```bash
  sleep 60 && env BSK_AUTO_START=0 bsk evaluate --session <id> "(() => ({ isGenerating: !!document.querySelector('[data-testid=\"stop-button\"], button[aria-label*=\"停止\"], button[aria-label*=\"Stop\"]') }))()"
  ```
- **末期孤立等待异步转场与先做要事铁律（2026-09-22 拍板）**：在整个研发闭环已在本地全绿、CI 已过、且 ChatGPT 审查等前置环节均已闭环，**全局只剩等待 Arena 这件事尚未结束的情况下**，主会话**绝对禁止原地干等或急催它完成**。此时应**将轮询等待窗口进一步拉长（如 sleep 2~3 分钟或放后台非阻塞守护）**，前台立即利用这段空隙去完成更高价值的收尾要事——包括：系统性提炼沉淀本轮避坑经验、改写与充实对应 Skill 规范、整理领域 ADR 与架构说明、梳理测试用例台账等，彻底杜绝主会话算力空转。
- **左侧会话历史列表追踪机制**：若会话页面发生重载或切回，**必须直接在左侧会话历史列表（Sidebar 的 `Today` / 历史会话项）中点击对应卡片切入**，严禁新建空会话或覆盖历史上下文；
- **会话完整性与进程守护铁律**：严禁在 Arena Agent 仍在运行（`isGenerating: true`）或未读完全部产出时擅自关闭 Arena 标签页，必须耐心等完进程并回读完整输出。
- **判定完成标准**：页面停止按钮消失（`isGenerating: false`），输入框恢复可用，工作区出现 `Create PR` / `Diff` 或最终总结文本。

### 6. 特别注意：评测分支处理（跳过机制）
在 Arena AI 中进行多轮对话时，由于其研究评估机制，系统偶发会在第 2 轮或后续轮次生成 A/B 两个候选回复，并提示：
`Which response do you prefer? Please choose the response you would like to continue with.`
- **处理方式**：页面底部会提供 `@eXX button "跳过"`（或 Skip），Agent 调用 `bsk click @eXX --session <id>` 即可无缝跳过偏好评分，直接保留模型完整输出并让对话上下文正常延续。

---

## 五、安全与数据脱敏铁律

**由于 Arena AI 明确声明对话数据可能被脱敏后公开用于学术研究数据集（"Your prompts may be shared publicly to support AI research"）**：
1. **严禁包含任何敏感凭据**：严禁发送真实 Token、API Key、Bearer 授权头、Password、Cookie、内部私网 IP 或项目专有凭据；
2. **机器路径一律泛化**：涉及个人目录、应用路径必须统一替换为标准环境变量（`%USERPROFILE%`、`%LOCALAPPDATA%`、$HOME）；
3. **代码 Diff 精简脱敏**：仅发送核心逻辑函数、架构状态机与测试断言，过滤敏感资产、业务专有数据与账号标识。

---

## 六、浏览器与会话生命周期铁律

### 1. 任务执行期标签页与会话常驻复用（Persistent Session & Tab Invariant）
- **严禁单步频繁关闭/释放**：在多轮迭代、多批次任务或持续推进的整个开发会话周期内，**必须保持 `bsk` 会话与已打开的 Arena AI 标签页常驻开启并持续复用**，严禁每完成单步对话或单次操作就调用 `session stop` 或关闭标签页；
- **常驻复用核心收益**：
  - 维持浏览器 CDP 连接与内存会话句柄，省去重复执行 `session start` 握手握流的额外开销；
  - 避免大型 SPA 页面反复重载与路由等待，保留页面完整 DOM 树、滚动位置与即时输入焦点；
  - 保持 Arena 多轮对话历史与 Workspace 状态完全连续。
- **全局终态收口才释放**：**只有在整个复合任务彻底交付验收完毕、确认用户已无任何后续需要调用浏览器的任务时**，才在最后统一调用：
  ```bash
  env BSK_AUTO_START=0 bsk session stop <id>
  ```
  释放 CDP 调试连接句柄；标签页依然完好保留在用户 Edge 浏览器中，便于用户随时切回查阅。

### 2. 浏览器主进程保护
- **绝对严禁误杀浏览器进程**：严禁调用 `taskkill`、`Stop-Process -Force` 或直接终止用户的 Edge 浏览器主进程，尊重并保护用户的全局桌面资产。
