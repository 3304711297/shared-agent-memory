# Arena AI (arena.ai) Browser Collaboration SOP (基于 BrowserSkill)

本规范定义了 Hermes Agent 如何通过 `browser-skill` (`bsk`) 接管用户已登录的 Edge 浏览器，与 **Arena AI (`https://arena.ai/`，原 LMSYS Chatbot Arena)** 页面进行跨 Agent 协同开发、单模型/双模型代码审查与对拍的完整标准化工作流。

---

## 一、定位与优先级决策

- **首选协同平台 (Primary)**：**Arena AI (`https://arena.ai/`)**
  - **核心优势**：完全免费开放业界顶级前沿大模型全家桶（Anthropic Claude Sonnet 4.6 / Claude Sonnet 5 High、OpenAI GPT-5.2 High / o3、Google Gemini 3.8 Flash High、DeepSeek V4.1 Max、xAI Grok 4.6、Qwen 3.7 Max 等）；
  - **多维对拍能力**：原生支持 `Direct Mode`（单模型精准对话）与 `Side by Side`（双模型并行对拍），单轮提问即可同时获取两家顶尖实验室视角的对抗式审查意见，无需消耗任何个人 API 配额。
- **备选协同平台 (Fallback / Secondary)**：**ChatGPT (`https://chatgpt.com/`)**
  - 保留作为特定历史会话复用或 Arena 遇临时网络波动时的兜底审计通道。

---

## 二、四大工作模式与职责角色分工

在跨 Agent 协作中，必须严格区分 **Reviewer（审查者）** 与 **Producer（生产者）** 角色：

| 模式名称 | 页面入口指示 | 协作角色 | 核心用途与工作特性 |
| :--- | :--- | :---: | :--- |
| **Side by Side** | Combobox 选 `Side by Side` + 选 Model 1 & 2 | **Reviewer (审查)** | **日常代码审查与方案对拍第一主力（绝对保底高阶）**。单轮同时获取两家顶尖模型独立出具的审查报告。推荐锁定 `claude-sonnet-5-high` + `gpt-5.5-instant`。 |
| **Direct Mode** | Combobox 选 `Direct` + 选目标模型 | **Reviewer (审查)** | **特定问题多轮深度追问**。定向绑定特定模型（首选 `claude-sonnet-5-high`），进行连续上下文推演。 |
| **Agent Mode** | Combobox 选 `Agent Mode` + 挂载 GitHub 仓库 | **Producer (生产)** | **全工程自主代码生成与新模块开发**。支持挂载 GitHub 仓库分支，具备完整 Workspace 沙箱、文件树与终端预览，适合让外部 Agent 独立探路开发新功能原型。 |
| **Battle Mode** | Combobox 选 `Battle` | **探索性抽卡** | **匿名竞技场盲测**。后台全池随机分配两款模型（有机会撞上未公开发布的超新代模型如 Fable 5.1 / GPT 6 Astra / Opus 5，但下限可能抽到 7B/8B 小模型，无保底且缺乏审查连续性）。 |

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
4. **即时向用户报备与规约沉淀**：明确告知用户「原某模型暂不可选，已自动通过排行榜重筛并切换为当前最高分的 XX 模型」，并将最新选型同步沉淀至本规范与 OpenViking 知识库。

---

## 四、核心执行协议 (SOP)

### 1. 守护进程与会话启动
MSYS/Git-Bash 环境下执行 `bsk` 必须携带 `env BSK_AUTO_START=0`：

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

### 3. 模式与模型精准配置
1. **切换模式**：
   在 `observe` 树中寻找模式下拉框（形如 `@e14 combobox "... [has-submenu]"`），点击后在弹出的选项列表中点击对应模式（如 `@e27 button "Direct Chat with 1 model at a time"` 或 `@e25 button "Side by Side Compare 2 models of your choice"`）。
2. **选择目标模型 (Direct / Side by Side)**：
   - 点击当前模型胶囊按钮（形如 `@e15 button "Max [has-submenu]"`）；
   - 在弹出的搜索浮层中，通过搜索输入框过滤或直接在列表中点击目标模型按钮（例如优先选 `claude-sonnet-4-6`、`gpt-5.2-high`、`deepseek-v4.1-flash-max` 等）；
   - Side by Side 模式下依次配置 Model 1 与 Model 2。

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

### 5. 轮询等待与结果回读
- 模型生成中页面会出现 `Stop generation` 按钮（或 `Generating...` 状态）；
- 采用递进等待轮询：
  ```bash
  sleep 15 && env BSK_AUTO_START=0 bsk observe --session <id>
  ```
- **判定完成标准**：输入框恢复为 enabled/empty，页面不再出现 `Stop generation`。

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

## 六、浏览器与会话生命周期

- **严禁误杀浏览器进程**：严禁调用 `taskkill` 或直接关闭用户的 Edge 浏览器主进程；
- **会话句柄主动释放**：任务对拍完成后，调用：
  ```bash
  env BSK_AUTO_START=0 bsk session stop <id>
  ```
  释放 CDP 调试连接句柄，标签页保持在用户浏览器中，便于用户随时切回查阅。
