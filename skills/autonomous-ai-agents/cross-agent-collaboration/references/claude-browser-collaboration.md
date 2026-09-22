# Claude Browser Collaboration SOP (基于 BrowserSkill)

本规范定义了 Hermes Agent 如何通过 `browser-skill` (`bsk`) 接管用户已登录的 Edge 浏览器，与 **Claude AI (`https://claude.ai/`)** 对话页面进行跨 Agent 协同开发、架构代码审查、以及基于云端沙箱打样 Patch 的标准化工作流。

---

## 一、定位与三足鼎立协同拓扑

在跨 Agent 协同矩阵中，**Arena AI**、**ChatGPT** 与 **Claude AI** 形成能力互补的三足鼎立格局：

| 平台 | 访问端点 | 定位角色 | 核心优势与适用场景 |
| :--- | :--- | :---: | :--- |
| **Arena AI** | `https://arena.ai/` | **云端独立副产线（Producer）** | 仅允许使用 **Agent Mode** 挂载仓库分支独立探路与打样开发；严禁 Direct / 对话模式。 |
| **ChatGPT** | `https://chatgpt.com/` | **备选主力（Reviewer）** | 显式开启深度推理「思考」模式，擅长对抗式漏洞挖掘、测试覆盖缺口核查，以严格判定 `CLOSED` 作为收口依据。 |
| **Claude AI** | `https://claude.ai/` | **架构复核与沙箱打样（Reviewer / Producer）** | 审美与架构拆分最深、契约规范最严；**网页端原生支持云端沙箱打样与 Patch 交付，为免费（Free）账户提供零 API 成本的云端开发能力**。 |

---

## 二、实战经验与合规安全门禁（2026-09-19 真实闭环提炼）

### 1. 免费账户（Free Tier）零成本沙箱闭环
- **权限边界事实**：桌面端 `Claude Code` CLI 强制要求 Pro / Max / Team / Enterprise 套餐或 Console API 商业额度，免费 Claude.ai 账户无法直连 CLI。
- **免付费沙箱协同工作流**：
  1. Claude.ai 具备网页端沙箱环境（具备读取公开仓库、克隆、建分支、修改代码、运行单测能力）；
  2. Hermes 向 Claude 发起重构/修复/单测补齐诉求；
  3. Claude 在云端沙箱中完成代码改动并生成 `git patch` 文本或压缩包；
  4. Hermes 本地借由 `git apply` / `git am` 无缝合流入本地工作树，执行全量编译与测试回归，实现零 API 成本的跨端生产协同。

### 2. 核心红线：严禁提交反风控与指纹绕行任务（合规门禁）
- **现象事实**：Claude 具备极高的模型安全对齐度与服务协议合规警觉性。一旦在提要中涉及「伪造 UA」、「借用官方 SDK 注入设备 Token 绕过上游风控」、「改写 CLI 身份指纹绕过拦截」、「多账号自动轮换削峰」等对抗逻辑，Claude 会**直接触发合规拒绝并给出风险警告（\"绕风控和指纹伪装那部分，我不会帮着加强\"）**。
- **提要准入白名单（向 Claude 提要必须严格限定在此范围）**：
  - ✅ **协议层兼容性与状态机**：OpenAI Chat、Anthropic Messages、OpenAI Responses 等标准协议转换、SSE 状态机流式处理、tool_calls 分片重组。
  - ✅ **工程架构重构**：目录规范化拆分（前后端分离、kernel/server 解耦）、模块职责单一化。
  - ✅ **安全防御加固**：Host 头校验、CORS 策略收紧、DNS Rebinding 防护、本地凭据加密（系统钥匙串替代明文 JSON）。
  - ✅ **测试覆盖度**：边界测试、契约单测、变异验证覆盖。
  - ✅ **文档与合规声明**：第三方开源协议签署（THIRD_PARTY_NOTICES）、API 文档反引号排版规范。

---

## 三、四大核心协同模式

| 模式 | 协作角色 | 输入内容 | 输出目标 | 适用场景 |
| :--- | :---: | :--- | :--- | :--- |
| **架构与代码审查 (Reviewer)** | Reviewer | 提交 SHA、变更文件、精简 diff、本地测试证据 | 模块职责评估、协议边缘缺陷、安全隐患分析 | 重点功能提交后的第三方架构级复核。 |
| **沙箱打样与 Patch (Producer)** | Producer | 公开仓库链接、目标分支、待修复目标规范 | 标准 `diff` / `git patch` 代码块 | 模块重构、补全单测、编写标准适配层。 |
| **深度推演 (Extended Thinking)** | Reviewer | 复杂状态机时序图、死锁或并发竞争场景描述 | 时序证明、边界状态分析 | 棘手并发 bug、流式解析截断排查。 |
| **文档与协议审查 (Auditor)** | Auditor | README、OpenAPI Schema、接口速查表 | 渲染修复建议、字段歧义排查 | 发版前文档合规与说明核验。 |

---

## 四、核心执行协议 (SOP)

### 1. 守护进程与会话启动
MSYS/Git-Bash 环境下执行 `bsk` 必须携带 `env BSK_AUTO_START=0`，避免无头自动拉起冲突：

- **守护进程启动避坑（2026-09-19 实测）**：若 `bsk status --json` 提示 daemon 未运行，在 Windows 下直接在 Hermes 前台执行 `bsk daemon start` 会因进程管道持有未脱钩，导致前台等待 180 秒直至打满超时被杀（**exit 124**，白等 3 分钟）。**必须使用后台命令启动**：
  ```bash
  # 方式一：Hermes 原生后台启动（推荐）
  terminal(command="bsk daemon start", background=True)
  # 方式二：Windows 命令提示符后台脱钩
  cmd /c start /b bsk daemon start
  ```
- **启动会话**：
```bash
# 启动会话并获取 session_id
env BSK_AUTO_START=0 bsk session start --json
```

记录返回的 `session_id: "<id>"`，后续所有操作均携带 `--session <id>`。

### 2. 页面导航与标签页复用
- **接续已有 Claude 会话（推荐）**：
  若用户提供了特定的 Claude 对话 URL（形如 `https://claude.ai/chat/<uuid>`），或者用户 Edge 中已有该标签页：
  ```bash
  # 查找用户标签页
  env BSK_AUTO_START=0 bsk tab list --scope user --session <id>
  # 借用已有标签页
  env BSK_AUTO_START=0 bsk tab borrow <tab_id> --session <id>
  ```
- **新建或直达对话**：
  ```bash
  env BSK_AUTO_START=0 bsk navigate "https://claude.ai/chat/<uuid>" --session <id>
  ```

### 3. 输入报告与提交协同
1. **定位输入框**：
   在页面中定位主输入框，通常为 `textbox "Write your prompt to Claude"` 或 `#prompt-textarea`。
2. **填充高密度提要**：
   ```bash
   env BSK_AUTO_START=0 bsk fill @eXX --value "..." --session <id>
   ```
   **审查提要标准结构**：
   - 本地 Git 提交 SHA 与变更文件清单；
   - 核心改动动机（协议适配、架构重构、安全加固）；
   - 待复核的代码 diff 或模块设计草案；
   - 本地单测通过情况与 CI 运行证据。
3. **回车提交**：
   ```bash
   env BSK_AUTO_START=0 bsk press Enter --ref @eXX --session <id>
   ```

### 4. 轮询等待与紧凑读页（防 Token 暴击）
- **禁止全量裸跑 `bsk observe`**：Claude 页面包含复杂的项目侧栏、历史会话树与无障碍节点，全量 observe 会产生数万字符的长文本树。
- **必须使用紧凑读页或针对性读取**：
  调用 `bsk-compact-page-read` 脚本：
  ```bash
  python "%LOCALAPPDATA%/hermes/skills/web/bsk-compact-page-read/scripts/table.py" --session <id>
  ```
- **判定生成结束**：
  - 页面出现 `Stop response` 按钮（或正处于思考流输出）时表示正在生成；
  - 当输入框状态恢复为 enabled/empty，且 `Stop response` 按钮消失时，判定生成完毕。
- **正文内容回读**：
  通过 `bsk evaluate` 提取最新一次 Claude 回复内容（例如提取 `.prose` 或正文区域文本），避免引入无关的 DOM 噪声。

### 5. 沙箱 Patch 落地闭环（Producer 模式特有）
当 Claude 在云端沙箱打样并给出 patch 后：
1. **提取 Patch**：通过 `bsk evaluate` 提取代码块中的 unified diff 内容；
2. **本地落盘**：将 diff 写入临时补丁文件 `%LOCALAPPDATA%/Temp/claude_sandbox.patch`；
3. **测试应用**：
   ```bash
   git apply --check "%LOCALAPPDATA%/Temp/claude_sandbox.patch"
   ```
4. **落地并回归**：
   ```bash
   git apply "%LOCALAPPDATA%/Temp/claude_sandbox.patch"
   ```
   执行全量本地测试、类型检查与代码风格校验，确认无破损后再行提交。

---

## 五、安全与脱敏铁律

1. **绝对脱敏**：严禁向 Claude 发送真实 Token、OAuth Refresh Token、API 密钥、Cookies 或未公开的内部服务器 IP；
2. **机器路径变量化**：本地路径一律泛化为 `%USERPROFILE%`、`%LOCALAPPDATA%` 或 `$HOME`；
3. **前台资产保护**：严禁杀死用户 Edge 浏览器主进程；协同工作完成后，务必调用 `bsk tab return <tab_id> --session <id>` 归还借用的标签页，并用 `bsk session stop <id>` 释放会话。
