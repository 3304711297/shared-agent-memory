# ChatGPT Browser Collaboration SOP (基于 BrowserSkill)

本规范定义了 Hermes Agent 如何通过 `browser-skill` (`bsk`) 接管用户已登录的 Edge 浏览器，与 ChatGPT 对话页面进行跨 Agent 协同开发、相互代码审查与对拍的完整标准化工作流。

---

## 适用场景
- 用户在 Edge 浏览器中已有打开的 ChatGPT 会话（含登录态与历史上下文）；
- 需要让外部模型（如 ChatGPT）作为 Reviewer 对当前仓库的改动进行独立对抗式审查；
- 需要在网页输入框中交互提交 diff / CI 证据，读取其复核结论，并二次对拍直到闭环。

---

## 核心执行协议 (SOP)

### 1. 守护进程与会话启动
Windows MSYS/Git-Bash 环境下执行 `bsk` 必须携带 `env BSK_AUTO_START=0`，避免无头自动拉起冲突：

```bash
# 启动会话并获取 session_id
env BSK_AUTO_START=0 bsk session start --json
```

若返回 `session_id: "xxxx"`，后续所有操作均携带 `--session xxxx`。

### 2. 页面导航与定位
如果用户提供了指定 ChatGPT 对话 URL：
```bash
env BSK_AUTO_START=0 bsk navigate "<chatgpt_url>" --session <id>
env BSK_AUTO_START=0 bsk observe --session <id>
```
若打开后处于新会话主页，可在 `observe` 输出的侧边栏历史列表中定位对应会话标题的 ref（如 `@e18 link "xxx"`）并通过 `bsk click @e18 --session <id>` 切换进入。

### 3. 输入报告与提交对拍
1. **定位输入框**：
   在 `observe` 树中寻找目标输入框，形如 `@eXX textbox "与 ChatGPT 聊天"` 或 placeholder 为 `有问题，随便问`。
2. **填充高密度审查提要**：
   ```bash
   env BSK_AUTO_START=0 bsk fill @eXX --value "..." --session <id>
   ```
   **报告内容标准结构**：
   - 提交 SHA 与简短 message；
   - 针对上一轮问题的具体修复落点（代码文件、函数、机制变化）；
   - 契约测试与回归单测（测试名、测试覆盖场景）；
   - 本地全量测试与远端 GitHub Actions CI 真实 Run 结果。
3. **回车提交**：
   ```bash
   env BSK_AUTO_START=0 bsk press Enter --ref @eXX --session <id>
   ```

### 4. 轮询等待与结果回读（强制使用紧凑读页）
- **禁止裸跑 `bsk observe`**：ChatGPT 对话页面包含庞大的历史侧边栏、工具条与深层无障碍树，单次 `bsk observe` 文本量高达 100K~150K 字符，多次轮询会瞬间打爆上下文并触发会话强制压缩（Compaction）。
- **必须使用 `bsk-compact-page-read` (jev)**：
  调用 `bsk-compact-page-read/scripts/table.py` 或提取最新回复正文，以 0.14x~0.3x 的紧凑体积获取页面状态与目标控件，保护会话上下文：
  ```bash
  python "%LOCALAPPDATA%/hermes/skills/web/bsk-compact-page-read/scripts/table.py" --session <id>
  ```
- **轮询判定完成**：输入框状态恢复为 enabled/empty，页面不再出现“停止回答”；
- **回读正文**：仅在判定 ChatGPT 生成结束后，通过紧凑提取或 targeted evaluation / 局部文本读取获取审查复核结论。

### 5. 对抗式双向复核（禁止盲从）
1. **真实性检验**：对 ChatGPT 提出的每一条缺陷指控，Hermes 必须在本地代码树与测试中独立求证，区分真正漏洞与虚假误报；
2. **TDD 闭环**：对确认成立的问题，遵循 `先写失败单测 → 实施最小改动 → 验证全绿 → 提交推送 → 盯 CI 到全绿`；
3. **闭环对拍**：重新组织新提交证据再次输入 ChatGPT，直到对方明确判定 `PASS / CLOSED`。

### 6. 会话与浏览器生命周期
- **尊重用户前台体验**：严禁关闭用户正在使用的 Edge 浏览器；
- **会话释放**：根据用户偏好决定是否保持 session，若用户未要求保持，在全部轮次结束后调用：
  ```bash
  env BSK_AUTO_START=0 bsk session stop <id>
  ```
  释放连接句柄，被借用标签页仍完好保留在用户浏览器中。
