---
name: browser-bookmarks
description: Use when searching user browser bookmarks or saved tools.
---

# 本地浏览器书签极速索引与检索系统 (browser-bookmarks)

用户将个人 Edge Dev 浏览器的 9,000+ 常用书签作为核心个人资源库，涵盖 AI、系统优化、编程开发、设计素材、音视频、实用工具等 12 大领域。

## 检索工作流

当用户询问「我之前存过的某个网站/工具」、「我的书签里有没有...」、「帮我找找我收藏的...」，或者在任务中需要调取相关垂直领域的优质站点时：

### 1. 实时精准/关键词检索（首选，耗时 < 20ms）
直接使用本地检索脚本查询实时书签（永远 100% 实时同步最新收藏）：

```bash
# 关键词检索（支持在标题、URL、所属文件夹中匹配）
python C:/Users/VOS-User/AppData/Local/hermes/scripts/search_bookmarks.py "<关键词>" -n 20

# 按文件夹过滤搜索
python C:/Users/VOS-User/AppData/Local/hermes/scripts/search_bookmarks.py "<关键词>" -f "AI" -n 10

# 查看主要分类文件夹分布
python C:/Users/VOS-User/AppData/Local/hermes/scripts/search_bookmarks.py --folders
```

### 2. 意图/自然语言语义检索 (OpenViking)
当用户表述较为宽泛或使用概念性描述（如「帮我找找我存过的免版权图标站或耳机校准工具」）时，使用 OpenViking 进行语义召回：

```python
# 语义搜索浏览器书签资源库
viking_search(query="免版权图标或UI设计素材", scope="viking://resources/browser-bookmarks/", limit=5)
```

## 隐私与安全规范
1. 原始书签包含用户全量本地浏览习惯，绝对保存在本地机器上（`%LOCALAPPDATA%\Microsoft\Edge Dev\User Data\Default\Bookmarks`）；
2. 严禁将含有敏感个人凭据或私有路径的原始书签全量提交至公开 GitHub 仓库。
