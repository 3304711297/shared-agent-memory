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

## 二、四大工作模式与适用场景

| 模式名称 | 页面入口指示 | 核心用途与工作特性 |
| :--- | :--- | :--- |
| **Direct Mode** | Combobox 选 `Direct` + 点击模型选择器 | **日常代码审查与迭代对拍首选**。定向绑定特定前沿模型（如 `claude-sonnet-4-6`），进行深度连续对话。 |
| **Side by Side** | Combobox 选 `Side by Side` + 选 Model 1 & 2 | **高难度架构与关键重构审查**。同时指定两款顶尖模型（如 Claude Sonnet 4.6 vs GPT-5.2 High），一键获得双重视角审查报告。 |
| **Agent Mode** | Combobox 选 `Agent Mode` | **复杂工程与仓库级自主任务**。支持挂载 GitHub 仓库与指定分支，进行上下文长工程分析。 |
| **Battle Mode** | Combobox 选 `Battle` | **匿名竞技场盲测**。由平台随机分派两个匿名模型回答，投票后揭晓真实身份。 |

---

## 三、核心执行协议 (SOP)

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

## 四、安全与数据脱敏铁律

**由于 Arena AI 明确声明对话数据可能被脱敏后公开用于学术研究数据集（"Your prompts may be shared publicly to support AI research"）**：
1. **严禁包含任何敏感凭据**：严禁发送真实 Token、API Key、Bearer 授权头、Password、Cookie、内部私网 IP 或项目专有凭据；
2. **机器路径一律泛化**：涉及个人目录、应用路径必须统一替换为标准环境变量（`%USERPROFILE%`、`%LOCALAPPDATA%`、$HOME）；
3. **代码 Diff 精简脱敏**：仅发送核心逻辑函数、架构状态机与测试断言，过滤敏感资产、业务专有数据与账号标识。

---

## 五、浏览器与会话生命周期

- **严禁误杀浏览器进程**：严禁调用 `taskkill` 或直接关闭用户的 Edge 浏览器主进程；
- **会话句柄主动释放**：任务对拍完成后，调用：
  ```bash
  env BSK_AUTO_START=0 bsk session stop <id>
  ```
  释放 CDP 调试连接句柄，标签页保持在用户浏览器中，便于用户随时切回查阅。
