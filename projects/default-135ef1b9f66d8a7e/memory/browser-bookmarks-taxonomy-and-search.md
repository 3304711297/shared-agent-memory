---
name: browser-bookmarks-taxonomy-and-search
description: 用户 Edge Dev 浏览器 9000+ 书签分类地图、本地极速检索工具与 OpenViking 语义知识库集成规范
metadata:
  type: project
---

# 用户浏览器书签分类地图与智能检索体系 (2026-09-07)

## 一、架构设计与安全边界

用户日常深度使用的 Edge Dev 浏览器积累了 **9,064 个精选书签**（602 个分类文件夹，原始文件约 7.3 MB）。为了让双端 Agent（Hermes & ZCode）深度理解用户的资源沉淀与工具偏好，同时杜绝公网泄露风险，确立「三位一体」集成架构：

1. **隐私与安全铁律**：`shared-agent-memory` 为公开 GitHub 仓库，严禁将包含个人私密参数、内部直链的 7.3MB 原始 JSON 直接推送到公网；
2. **本地实时极速检索（首选）**：通过专用工具直接直读本地真实书签文件，零同步开销，耗时 < 20ms，100% 实时同步用户最新收藏；
3. **本地 OpenViking 语义知识库**：清洗脱敏后挂载至本地私有向量库（`viking://resources/browser-bookmarks/`），支持自然语言意图级召回；
4. **记忆库沉淀分类地图**：共享记忆库仅收录脱敏的顶层领域结构，指导 Agent 在面对特定任务时主动调取书签资源。

---

## 二、书签 12 大垂直领域分类地图

| 分类标识 | 领域分类 | 书签数量 | 核心收录内容概括 |
| :--- | :--- | :---: | :--- |
| **01** | **AI 与大模型智能体** | 36 项 | SkillHub、Cola Skill、Hermes Hub、ECC、Gemini/Claude 官方生态、Prompt 调优 |
| **02** | **系统优化与电脑硬件** | 348 项 | Windows 优化/激活/AuditMode、UEFI/BIOS 改写、驱动便携版、显卡/CPU 天梯榜、超频社区 |
| **03** | **编程开发与脚本插件** | 324 项 | GitHub 开源项目、GreasyFork 脚本、代码调试工具、UA 查询、Figma 插件开发 |
| **04** | **设计素材与视觉建模** | 1,421 项 | C4Dzone 模型、Highend3D、免版权图库、UI/Icon 素材、字体排印、着色器 |
| **05** | **网络通信与代理工具** | 827 项 | Telegram 频道/Bot、Karing/TUN 网络栈、VPN/代理协议、网络延迟与 QoS 策略 |
| **06** | **游戏平台与游戏资源** | 267 项 | Steam 数据库/饰品溯源、我的世界模组/联机、泰拉瑞亚、Switch 模拟器、游戏硬件基准 |
| **07** | **音乐与音频素材** | 435 项 | KVR Audio 插件、Musopen 免版权音乐、音效库、广播电台、耳机曲线校准 |
| **08** | **影视动漫与流媒体** | 800 项 | 动漫追番、影视在线、B站扩展（BewlyCat/ACG助手）、影视解析与字幕工具 |
| **09** | **阅读学习与电子书籍** | 1,730 项 | 外刊杂志下载、电子书库、编程开发教程、IT 认证、历史地图与百科知识 |
| **10** | **魔方教程与测速** | 48 项 | CubeSkills、CFOP 还原公式、魔方计时与算法库 |
| **11** | **实用在线工具与导航** | 1,656 项 | 格式转换、网盘与文件传输、磁力/BT 聚合、站长工具、专业万能导航 |
| **12** | **综合资源与实用收藏** | 1,110 项 | 菜谱、生活常备、实用资讯与日常高频站点 |

*(注：成人与个人私密文件夹已在导出与索引阶段彻底物理排除)*

---

## 三、双端 Agent 检索调用规程

已为 Hermes 与 ZCode 建立统一的技能 `browser-bookmarks`：

### 1. 关键词与目录精确检索（首选，秒级执行）
```bash
# 模糊匹配标题、URL 或目录路径
python C:/Users/VOS-User/AppData/Local/hermes/scripts/search_bookmarks.py "<检索词>" -n 20

# 限定在特定分类目录搜索
python C:/Users/VOS-User/AppData/Local/hermes/scripts/search_bookmarks.py "<检索词>" -f "AI" -n 10
```

### 2. 自然语言概念检索（OpenViking 意图召回）
面对模糊或泛化需求时，调用 OpenViking：
```python
viking_search(query="免版权音频或耳机校准", scope="viking://resources/browser-bookmarks/", limit=5)
```

**Why:** 建立安全、实时且具备语义理解的个人资源检索体系，大幅提升 Agent 对用户个性化工具链的认知深度。
**How to apply:** 只要涉及推荐工具、寻找特定网站、回溯历史收藏时，优先检索本地书签库，避免盲目推荐外部未知站点。
